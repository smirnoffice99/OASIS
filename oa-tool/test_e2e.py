"""
test_e2e.py — KR-TEST-001 end-to-end 테스트

전체 흐름 검증:
  OA 파싱 → 세션 생성 → 거절이유 #1(prior_art, 5단계)
           → 거절이유 #2(clarity, 3단계)
           → 거절이유 #3(unity with_citations, 3단계)
           → 리포트 생성 → final_comment.docx 저장

LLM 호출과 사용자 입력(input)은 모두 mock 처리한다.
"""

from __future__ import annotations

import json
import shutil
import sys
import types
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# 경로 설정
# ---------------------------------------------------------------------------

TOOL_DIR = Path(__file__).parent
sys.path.insert(0, str(TOOL_DIR))

REAL_CASES = TOOL_DIR / "cases"
MOCK_CASE_ID = "KR-TEST-001"

# ---------------------------------------------------------------------------
# 외부 의존성 mock (yaml, anthropic)
# ---------------------------------------------------------------------------

yaml_mock = types.ModuleType("yaml")
yaml_mock.safe_load = lambda f: {
    "provider": "claude",
    "model": "claude-sonnet-4-6",
    "api_key_env": "ANTHROPIC_API_KEY",
    "max_tokens": 4096,
}
sys.modules["yaml"] = yaml_mock

anthropic_mock = types.ModuleType("anthropic")
anthropic_mock.Anthropic = MagicMock()
sys.modules["anthropic"] = anthropic_mock

# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

PASS_COUNT = 0
FAIL_COUNT = 0


def check(condition: bool, label: str) -> None:
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {label}")
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {label}")


def _mock_llm_response(step_label: str) -> str:
    """단계별 mock LLM 응답을 반환한다."""
    return f"## {step_label}\n\nMock analysis result for E2E test.\n"


def _make_llm_mock() -> MagicMock:
    """LLMClient mock — chat()은 단계 레이블을 포함한 텍스트를 반환한다."""
    llm = MagicMock()
    call_count = [0]

    def side_effect(user_message, system_prompt="", temperature=0.3):
        call_count[0] += 1
        return f"## Mock Step Result #{call_count[0]}\n\nMock LLM response for E2E test.\n"

    llm.chat.side_effect = side_effect
    llm.load_prompt.return_value = "mock system prompt"
    return llm


# ---------------------------------------------------------------------------
# 세션 초기화 헬퍼
# ---------------------------------------------------------------------------

def _reset_session(cases_root: Path) -> None:
    """테스트 전 세션 파일을 초기화한다."""
    session_path = cases_root / MOCK_CASE_ID / "session.json"
    if session_path.exists():
        session_path.unlink()
    # rejection_N 디렉토리도 정리
    for d in (cases_root / MOCK_CASE_ID).glob("rejection_*"):
        if d.is_dir():
            shutil.rmtree(d)
    # final_comment 정리
    for f in (cases_root / MOCK_CASE_ID).glob("final_comment.*"):
        f.unlink()


# ---------------------------------------------------------------------------
# 테스트 1: OA 파싱 + 세션 생성
# ---------------------------------------------------------------------------

def test_parse_and_session_create(cases_root: Path) -> None:
    print("\n[Test 1] OA 파싱 + 세션 생성")

    from oa_parser import parse_oa
    from session import create_session, load_session, STATUS_PENDING

    case_dir = cases_root / MOCK_CASE_ID
    rejections = parse_oa(case_dir)

    check(len(rejections) == 3, f"거절이유 3건 파싱 (실제: {len(rejections)})")
    check(rejections[0].type == "prior_art", "#1 prior_art")
    check(rejections[1].type == "clarity", "#2 clarity")
    check(rejections[2].type == "unity", "#3 unity")
    check(rejections[2].has_citations is True, "#3 has_citations=True")

    session = create_session(MOCK_CASE_ID, rejections, cases_root)
    check(session.case_id == MOCK_CASE_ID, "case_id 일치")
    check(len(session.rejections) == 3, "세션에 3건 등록")
    check(all(r.status == STATUS_PENDING for r in session.rejections), "전체 pending")

    # 세션 파일 저장 확인
    session_path = cases_root / MOCK_CASE_ID / "session.json"
    check(session_path.exists(), "session.json 생성 확인")

    # 복원 확인
    restored = load_session(MOCK_CASE_ID, cases_root)
    check(restored.case_id == MOCK_CASE_ID, "세션 복원 case_id 일치")
    check(len(restored.rejections) == 3, "세션 복원 거절이유 3건")


# ---------------------------------------------------------------------------
# 테스트 2: PriorArtHandler 전체 흐름 (5단계)
# ---------------------------------------------------------------------------

def test_prior_art_handler_full_flow(cases_root: Path) -> None:
    print("\n[Test 2] PriorArtHandler 전체 흐름 (5단계, 승인 mock)")

    from session import load_session, STATUS_CONCLUDED
    from handlers.prior_art_handler import PriorArtHandler

    session = load_session(MOCK_CASE_ID, cases_root)
    rejection = session.get_rejection(1)
    llm = _make_llm_mock()

    handler = PriorArtHandler(
        case_id=MOCK_CASE_ID,
        rejection=rejection,
        session=session,
        llm_client=llm,
        cases_root=cases_root,
    )

    # 5번 승인 입력 시뮬레이션 (각 step + 마지막 전략 확정)
    user_inputs = ["Y"] * 5

    with patch("builtins.input", side_effect=user_inputs):
        handler.handle()

    check(llm.chat.call_count >= 5, f"LLM 5회 이상 호출 (실제: {llm.chat.call_count})")
    check(rejection.status == STATUS_CONCLUDED, "#1 거절이유 concluded")

    # 파일 저장 확인
    rej_dir = cases_root / MOCK_CASE_ID / "rejection_1"
    for step in range(1, 6):
        path = rej_dir / f"step_{step}_result.md"
        check(path.exists(), f"step_{step}_result.md 생성")

    check((rej_dir / "conclusion.md").exists(), "conclusion.md 생성")
    check((rej_dir / "dialogue.json").exists(), "dialogue.json 생성")


# ---------------------------------------------------------------------------
# 테스트 3: ClarityHandler 전체 흐름 (3단계)
# ---------------------------------------------------------------------------

def test_clarity_handler_full_flow(cases_root: Path) -> None:
    print("\n[Test 3] ClarityHandler 전체 흐름 (3단계, 승인 mock)")

    from session import load_session, STATUS_CONCLUDED
    from handlers.clarity_handler import ClarityHandler

    session = load_session(MOCK_CASE_ID, cases_root)
    rejection = session.get_rejection(2)
    llm = _make_llm_mock()

    handler = ClarityHandler(
        case_id=MOCK_CASE_ID,
        rejection=rejection,
        session=session,
        llm_client=llm,
        cases_root=cases_root,
    )

    user_inputs = ["Y"] * 3

    with patch("builtins.input", side_effect=user_inputs):
        handler.handle()

    check(llm.chat.call_count >= 3, f"LLM 3회 이상 호출 (실제: {llm.chat.call_count})")
    check(rejection.status == STATUS_CONCLUDED, "#2 거절이유 concluded")

    rej_dir = cases_root / MOCK_CASE_ID / "rejection_2"
    for step in range(1, 4):
        path = rej_dir / f"step_{step}_result.md"
        check(path.exists(), f"step_{step}_result.md 생성")

    check((rej_dir / "conclusion.md").exists(), "conclusion.md 생성")


# ---------------------------------------------------------------------------
# 테스트 4: UnityHandler 전체 흐름 (3단계, has_citations=True)
# ---------------------------------------------------------------------------

def test_unity_handler_full_flow(cases_root: Path) -> None:
    print("\n[Test 4] UnityHandler 전체 흐름 (3단계, has_citations=True, 승인 mock)")

    from session import load_session, STATUS_CONCLUDED
    from handlers.unity_handler import UnityHandler

    session = load_session(MOCK_CASE_ID, cases_root)
    rejection = session.get_rejection(3)
    llm = _make_llm_mock()

    check(rejection.has_citations is True, "has_citations=True 확인")

    handler = UnityHandler(
        case_id=MOCK_CASE_ID,
        rejection=rejection,
        session=session,
        llm_client=llm,
        cases_root=cases_root,
    )

    user_inputs = ["Y"] * 3

    with patch("builtins.input", side_effect=user_inputs):
        handler.handle()

    check(llm.chat.call_count >= 3, f"LLM 3회 이상 호출 (실제: {llm.chat.call_count})")
    check(rejection.status == STATUS_CONCLUDED, "#3 거절이유 concluded")

    rej_dir = cases_root / MOCK_CASE_ID / "rejection_3"
    for step in range(1, 4):
        path = rej_dir / f"step_{step}_result.md"
        check(path.exists(), f"step_{step}_result.md 생성")

    check((rej_dir / "conclusion.md").exists(), "conclusion.md 생성")


# ---------------------------------------------------------------------------
# 테스트 5: 세션 전체 concluded 확인
# ---------------------------------------------------------------------------

def test_all_concluded(cases_root: Path) -> None:
    print("\n[Test 5] 세션 전체 concluded 상태 확인")

    from session import load_session, STATUS_CONCLUDED, OVERALL_COMPLETED

    session = load_session(MOCK_CASE_ID, cases_root)
    check(session.is_all_concluded(), "모든 거절이유 concluded")
    for r in session.rejections:
        check(r.status == STATUS_CONCLUDED, f"#{r.id} status=concluded")


# ---------------------------------------------------------------------------
# 테스트 6: 리포트 생성
# ---------------------------------------------------------------------------

def test_report_generation(cases_root: Path) -> None:
    print("\n[Test 6] 리포트 생성 (final_comment.docx)")

    from session import load_session
    from report_generator import ReportGenerator

    session = load_session(MOCK_CASE_ID, cases_root)
    samples_root = TOOL_DIR / "samples"
    llm = _make_llm_mock()
    # 리포트용 LLM mock: overall strategy도 포함
    llm.chat.side_effect = lambda *a, **kw: (
        "## English Comment Section\n\nMock report content.\n"
    )

    generator = ReportGenerator(
        case_id=MOCK_CASE_ID,
        session=session,
        llm_client=llm,
        cases_root=cases_root,
        samples_root=samples_root,
    )

    output_path = generator.generate()

    # python-docx 미설치 시 .txt 폴백 — 실제 저장 파일을 확인한다.
    actual_path = output_path if output_path.exists() else output_path.with_suffix(".txt")

    check(actual_path.exists(), f"final_comment 파일 생성: {actual_path.name}")
    check(actual_path.suffix in (".docx", ".txt"), "출력 파일 형식 확인 (.docx 또는 .txt 폴백)")
    check(actual_path.stat().st_size > 0, "파일 크기 > 0")


# ---------------------------------------------------------------------------
# 테스트 7: 세션 재개 (concluded 건너뛰기)
# ---------------------------------------------------------------------------

def test_session_resume(cases_root: Path) -> None:
    print("\n[Test 7] 세션 재개 — concluded 거절이유 건너뛰기")

    from session import load_session, get_or_create_session
    from oa_parser import parse_oa

    case_dir = cases_root / MOCK_CASE_ID
    rejections = parse_oa(case_dir)

    # 이미 세션이 있으면 재개
    session, is_resumed = get_or_create_session(MOCK_CASE_ID, rejections, cases_root)
    check(is_resumed is True, "기존 세션 복원 (is_resumed=True)")

    pending = session.pending_rejections()
    check(len(pending) == 0, f"미완료 거절이유 없음 (pending={len(pending)})")
    check(session.is_all_concluded(), "전체 concluded 확인")


# ---------------------------------------------------------------------------
# 테스트 8: 재검토 + 재처리
# ---------------------------------------------------------------------------

def test_reopen_and_reprocess(cases_root: Path) -> None:
    print("\n[Test 8] 재검토(재검토 1) → 재처리 → 재concluded")

    from session import load_session, STATUS_IN_PROGRESS, STATUS_CONCLUDED
    from handlers.prior_art_handler import PriorArtHandler

    session = load_session(MOCK_CASE_ID, cases_root)
    ok = session.reopen_rejection(1)
    check(ok is True, "reopen_rejection(1) 성공")

    from session import save_session
    save_session(session, cases_root)

    rejection = session.get_rejection(1)
    check(rejection.status == STATUS_IN_PROGRESS, "#1 in_progress로 전환")

    llm = _make_llm_mock()
    handler = PriorArtHandler(
        case_id=MOCK_CASE_ID,
        rejection=rejection,
        session=session,
        llm_client=llm,
        cases_root=cases_root,
    )

    user_inputs = ["Y"] * 5

    with patch("builtins.input", side_effect=user_inputs):
        handler.handle()

    check(rejection.status == STATUS_CONCLUDED, "#1 재처리 후 concluded")
    check(llm.chat.call_count >= 5, f"재처리 시 LLM 5회 이상 호출 (실제: {llm.chat.call_count})")


# ---------------------------------------------------------------------------
# 통합 실행
# ---------------------------------------------------------------------------

def run_all() -> None:
    global PASS_COUNT, FAIL_COUNT

    print("=" * 65)
    print("  OASIS end-to-end 테스트 — KR-TEST-001")
    print("=" * 65)

    # 임시 디렉토리를 사용하여 원본 cases/ 보존
    with tempfile.TemporaryDirectory() as tmp:
        tmp_cases = Path(tmp) / "cases"
        # KR-TEST-001 mock 파일 복사 (실제 파일 재사용)
        shutil.copytree(REAL_CASES / MOCK_CASE_ID, tmp_cases / MOCK_CASE_ID)

        # 세션 초기화
        _reset_session(tmp_cases)

        test_parse_and_session_create(tmp_cases)
        test_prior_art_handler_full_flow(tmp_cases)
        test_clarity_handler_full_flow(tmp_cases)
        test_unity_handler_full_flow(tmp_cases)
        test_all_concluded(tmp_cases)
        test_report_generation(tmp_cases)
        test_session_resume(tmp_cases)
        test_reopen_and_reprocess(tmp_cases)

    print()
    print("=" * 65)
    print(f"  결과: PASS {PASS_COUNT} / FAIL {FAIL_COUNT} / 합계 {PASS_COUNT + FAIL_COUNT}")
    print("=" * 65)

    if FAIL_COUNT > 0:
        sys.exit(1)
    else:
        print("  모든 end-to-end 테스트 통과")


if __name__ == "__main__":
    run_all()
