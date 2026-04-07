"""
main.py — OASIS 전체 흐름 오케스트레이션

실행:
  python main.py                        # 대화형 사건번호 입력
  python main.py KR-2024-12345          # 사건번호 직접 지정
  python main.py KR-2024-12345 --report # 분석 건너뛰고 리포트만 생성

흐름:
  사건번호 입력
    → OA 파싱 (거절이유 추출 + 유형 분류)
    → 세션 로드 or 신규 생성
    → 거절이유 목록 출력 + 사용자 확인
    → 거절이유별 Handler 자동 선택 후 순차 처리
    → 모든 거절이유 완료 → 영문 코멘트 .docx 생성
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# 경로 설정 — 스크립트 위치를 기준으로 고정
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).parent
_CASES_ROOT = _ROOT / "cases"
_SAMPLES_ROOT = _ROOT / "samples"


# ---------------------------------------------------------------------------
# 핸들러 팩토리
# ---------------------------------------------------------------------------

def _make_handler(rejection, session, llm_client, cases_root):
    """거절이유 유형에 따라 적절한 Handler를 생성한다."""
    from handlers.prior_art_handler import PriorArtHandler
    from handlers.clarity_handler import ClarityHandler
    from handlers.unity_handler import UnityHandler
    from handlers.default_handler import DefaultHandler

    dispatch = {
        "prior_art": PriorArtHandler,
        "clarity":   ClarityHandler,
        "unity":     UnityHandler,
        "other":     DefaultHandler,
    }
    cls = dispatch.get(rejection.type, DefaultHandler)
    return cls(
        case_id=session.case_id,
        rejection=rejection,
        session=session,
        llm_client=llm_client,
        cases_root=cases_root,
    )


# ---------------------------------------------------------------------------
# 거절이유 목록 출력
# ---------------------------------------------------------------------------

def _print_rejection_list(session) -> None:
    from session import STATUS_CONCLUDED
    print("\n" + "=" * 70)
    print("  거절이유 목록")
    print("=" * 70)
    for r in sorted(session.rejections, key=lambda x: x.id):
        status_mark = "[완료]" if r.status == STATUS_CONCLUDED else "[미완료]"
        claims_str = ", ".join(str(c) for c in r.claims) if r.claims else "-"
        citations_str = " / " + ", ".join(r.citations) if r.citations else ""
        unity_flag = ""
        if r.type == "unity":
            unity_flag = " (인용발명 있음)" if r.has_citations else " (인용발명 없음)"
        print(
            f"  {status_mark} #{r.id} {r.subtype}{unity_flag}"
            f" — 청구항 {claims_str}{citations_str}"
        )
    print("=" * 70)


# ---------------------------------------------------------------------------
# 사용자 입력 헬퍼
# ---------------------------------------------------------------------------

def _prompt(message: str) -> str:
    try:
        return input(message).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n종료합니다.")
        sys.exit(0)


def _confirm_rejection_list(session) -> bool:
    """거절이유 목록을 보여주고 계속할지 확인한다."""
    _print_rejection_list(session)
    while True:
        answer = _prompt(
            "\n위 거절이유 목록으로 분석을 시작합니다.\n"
            "계속하려면 'Y', 종료하려면 'N': "
        )
        if answer.lower() in ("y", "예", "yes", "승인"):
            return True
        if answer.lower() in ("n", "아니", "no", "종료"):
            return False


# ---------------------------------------------------------------------------
# 메인 처리 루프
# ---------------------------------------------------------------------------

def run_analysis(case_id: str, cases_root: Path, samples_root: Path) -> None:
    """
    거절이유 분석 전체 흐름을 실행한다.
    """
    from handlers.base_handler import ExitRequested, ReviewRequested
    from llm_client import LLMClient
    from oa_parser import parse_oa, print_rejection_summary
    from session import (
        get_or_create_session, save_session,
        STATUS_CONCLUDED, STATUS_IN_PROGRESS,
    )

    case_dir = cases_root / case_id

    # ------------------------------------------------------------------
    # 1. OA 파싱
    # ------------------------------------------------------------------
    print(f"\n[OASIS] 사건번호: {case_id}")
    print("  OA 파일 파싱 중...")
    try:
        rejections = parse_oa(case_dir)
    except FileNotFoundError as e:
        print(f"\n[오류] {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n[오류] {e}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. 세션 로드 or 신규 생성
    # ------------------------------------------------------------------
    session, is_resumed = get_or_create_session(case_id, rejections, cases_root)

    if is_resumed:
        pending = session.pending_rejections()
        concluded_count = sum(
            1 for r in session.rejections if r.status == STATUS_CONCLUDED
        )
        print(f"  기존 세션 복원 — 완료: {concluded_count}건, 미완료: {len(pending)}건")
    else:
        print(f"  새 세션 시작 — 거절이유 {len(rejections)}건")

    # ------------------------------------------------------------------
    # 3. 거절이유 목록 확인
    # ------------------------------------------------------------------
    if not _confirm_rejection_list(session):
        print("  분석을 종료합니다.")
        return

    # ------------------------------------------------------------------
    # 4. LLM 클라이언트 초기화
    # ------------------------------------------------------------------
    print("\n  LLM 클라이언트 초기화 중...")
    try:
        llm = LLMClient()
        print(f"  LLM: {llm}")
    except (ImportError, EnvironmentError) as e:
        print(f"\n[오류] LLM 초기화 실패: {e}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 5. 거절이유 순차 처리
    # ------------------------------------------------------------------
    _process_rejections(session, llm, cases_root)

    # ------------------------------------------------------------------
    # 6. 리포트 생성
    # ------------------------------------------------------------------
    if session.is_all_concluded():
        _generate_report(case_id, session, llm, cases_root, samples_root)
    else:
        pending = session.pending_rejections()
        print(f"\n미완료 거절이유 {len(pending)}건이 남아 있어 리포트를 생성하지 않습니다.")
        print("  나중에 재실행하면 중단된 지점부터 재개됩니다.")


def _process_rejections(session, llm, cases_root: Path) -> None:
    """
    미완료 거절이유를 순차적으로 처리한다.
    ExitRequested / ReviewRequested 예외를 처리한다.
    """
    from handlers.base_handler import ExitRequested, ReviewRequested
    from session import save_session

    while True:
        pending = session.pending_rejections()
        if not pending:
            break

        rejection = pending[0]
        handler = _make_handler(rejection, session, llm, cases_root)

        try:
            handler.handle()

        except ExitRequested:
            save_session(session, cases_root)
            print("\n[저장 완료] 세션을 저장하고 종료합니다.")
            print(f"  재개하려면: python main.py {session.case_id}")
            sys.exit(0)

        except ReviewRequested as e:
            _handle_review_request(e.rejection_id, session, cases_root)
            # 재검토 요청 후 루프 계속

        except KeyboardInterrupt:
            save_session(session, cases_root)
            print("\n\n[중단] 세션을 저장했습니다. 나중에 재개할 수 있습니다.")
            sys.exit(0)


def _handle_review_request(rejection_id: int, session, cases_root: Path) -> None:
    """'재검토 N' 명령 처리 — 해당 거절이유를 in_progress로 되돌린다."""
    from session import save_session

    ok = session.reopen_rejection(rejection_id)
    if ok:
        save_session(session, cases_root)
        print(f"\n  거절이유 #{rejection_id}를 재검토 상태로 변경했습니다.")
    else:
        print(f"\n  [경고] 거절이유 #{rejection_id}를 찾을 수 없습니다.")


# ---------------------------------------------------------------------------
# 리포트 생성
# ---------------------------------------------------------------------------

def _generate_report(
    case_id: str, session, llm, cases_root: Path, samples_root: Path
) -> None:
    from report_generator import ReportGenerator

    print("\n" + "=" * 70)
    print("  모든 거절이유 처리 완료 — 영문 코멘트 생성")
    print("=" * 70)

    try:
        generator = ReportGenerator(
            case_id=case_id,
            session=session,
            llm_client=llm,
            cases_root=cases_root,
            samples_root=samples_root,
        )
        output_path = generator.generate()
        print(f"\n[완료] 영문 코멘트가 생성되었습니다:")
        print(f"  {output_path}")
    except Exception as e:
        print(f"\n[오류] 리포트 생성 실패: {e}")
        raise


# ---------------------------------------------------------------------------
# 리포트만 재생성
# ---------------------------------------------------------------------------

def run_report_only(case_id: str, cases_root: Path, samples_root: Path) -> None:
    """
    분석을 건너뛰고 기존 세션의 결과로 리포트만 생성한다.
    """
    from llm_client import LLMClient
    from session import load_session

    print(f"\n[OASIS] 리포트 재생성 — 사건번호: {case_id}")

    try:
        session = load_session(case_id, cases_root)
    except FileNotFoundError:
        print(f"[오류] 세션 파일이 없습니다. 먼저 분석을 실행하세요.")
        sys.exit(1)

    try:
        llm = LLMClient()
    except (ImportError, EnvironmentError) as e:
        print(f"[오류] LLM 초기화 실패: {e}")
        sys.exit(1)

    _generate_report(case_id, session, llm, cases_root, samples_root)


# ---------------------------------------------------------------------------
# 사건번호 입력
# ---------------------------------------------------------------------------

def _get_case_id(args) -> str:
    """CLI 인수 또는 대화형 입력으로 사건번호를 받는다."""
    if args.case_id:
        return args.case_id.strip()

    print("\n" + "=" * 70)
    print("  OASIS — 특허 의견제출통지서 대응 자동화 시스템")
    print("=" * 70)
    while True:
        case_id = _prompt("\n사건번호를 입력하세요 (예: KR-2024-12345): ")
        if case_id:
            return case_id
        print("  사건번호를 입력해 주세요.")


# ---------------------------------------------------------------------------
# 진입점
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="OASIS — 특허 의견제출통지서 대응 자동화",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "사용 예:\n"
            "  python main.py                        # 대화형 실행\n"
            "  python main.py KR-2024-12345          # 사건번호 직접 지정\n"
            "  python main.py KR-2024-12345 --report # 리포트만 재생성\n"
        ),
    )
    parser.add_argument(
        "case_id",
        nargs="?",
        default=None,
        help="사건번호 (생략 시 대화형 입력)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="기존 세션 결과로 리포트만 재생성",
    )
    parser.add_argument(
        "--cases-root",
        default=str(_CASES_ROOT),
        help=f"cases 디렉토리 경로 (기본: {_CASES_ROOT})",
    )
    parser.add_argument(
        "--samples-root",
        default=str(_SAMPLES_ROOT),
        help=f"samples 디렉토리 경로 (기본: {_SAMPLES_ROOT})",
    )

    args = parser.parse_args()
    cases_root = Path(args.cases_root)
    samples_root = Path(args.samples_root)
    case_id = _get_case_id(args)

    if args.report:
        run_report_only(case_id, cases_root, samples_root)
    else:
        run_analysis(case_id, cases_root, samples_root)


if __name__ == "__main__":
    main()
