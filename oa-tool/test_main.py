"""
main.py 통합 흐름 테스트 (LLM + 사용자 입력 mock)
"""

import sys
import types
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))

# yaml mock
yaml_mock = types.ModuleType("yaml")
yaml_mock.safe_load = lambda f: {
    "provider": "claude", "model": "claude-sonnet-4-6",
    "api_key_env": "ANTHROPIC_API_KEY", "max_tokens": 4096,
}
sys.modules["yaml"] = yaml_mock

# anthropic mock
anthropic_mock = types.ModuleType("anthropic")
anthropic_mock.Anthropic = MagicMock()
sys.modules["anthropic"] = anthropic_mock

from main import _make_handler, _handle_review_request, _print_rejection_list
from session import RejectionState, Session, STATUS_PENDING, STATUS_CONCLUDED


CASES_ROOT = Path(__file__).parent / "cases"


def make_rejection(rid, rtype, subtype, claims, citations=None, status=STATUS_PENDING):
    return RejectionState(
        id=rid, type=rtype, subtype=subtype,
        claims=claims, citations=citations or [],
        has_citations=bool(citations),
        status=status, current_step=0,
    )


def make_session(rejections):
    return Session(case_id="KR-TEST-001", rejections=rejections)


# ------------------------------------------------------------------

def test_make_handler_prior_art():
    from handlers.prior_art_handler import PriorArtHandler
    r = make_rejection(1, "prior_art", "신규성+진보성", [1, 3, 5], ["D1"])
    session = make_session([r])
    llm = MagicMock()
    h = _make_handler(r, session, llm, CASES_ROOT)
    assert isinstance(h, PriorArtHandler)
    print("PASS: prior_art -> PriorArtHandler")


def test_make_handler_clarity():
    from handlers.clarity_handler import ClarityHandler
    r = make_rejection(2, "clarity", "기재불비", [7])
    session = make_session([r])
    llm = MagicMock()
    h = _make_handler(r, session, llm, CASES_ROOT)
    assert isinstance(h, ClarityHandler)
    print("PASS: clarity -> ClarityHandler")


def test_make_handler_unity():
    from handlers.unity_handler import UnityHandler
    r = make_rejection(3, "unity", "단일성 위반", list(range(1, 9)), ["D1"])
    session = make_session([r])
    llm = MagicMock()
    h = _make_handler(r, session, llm, CASES_ROOT)
    assert isinstance(h, UnityHandler)
    print("PASS: unity -> UnityHandler")


def test_make_handler_other():
    from handlers.default_handler import DefaultHandler
    r = make_rejection(4, "other", "기타", [1])
    session = make_session([r])
    llm = MagicMock()
    h = _make_handler(r, session, llm, CASES_ROOT)
    assert isinstance(h, DefaultHandler)
    print("PASS: other -> DefaultHandler")


def test_make_handler_unknown_falls_back_to_default():
    from handlers.default_handler import DefaultHandler
    r = make_rejection(5, "unknown_type", "미분류", [1])
    session = make_session([r])
    llm = MagicMock()
    h = _make_handler(r, session, llm, CASES_ROOT)
    assert isinstance(h, DefaultHandler)
    print("PASS: 미분류 타입 -> DefaultHandler 폴백")


def test_print_rejection_list(capsys=None):
    """_print_rejection_list가 오류 없이 출력되는지 확인."""
    rejections = [
        make_rejection(1, "prior_art", "신규성+진보성", [1, 3, 5], ["D1", "D2"]),
        make_rejection(2, "clarity", "기재불비", [7], status=STATUS_CONCLUDED),
        make_rejection(3, "unity", "단일성 위반", list(range(1, 9)), ["D1"]),
    ]
    session = make_session(rejections)
    _print_rejection_list(session)  # 예외 없이 출력되면 통과
    print("PASS: _print_rejection_list 출력 정상")


def test_handle_review_request_valid():
    """유효한 거절이유 ID에 대해 reopen이 정상 동작하는지 확인."""
    r = make_rejection(1, "prior_art", "신규성+진보성", [1], status=STATUS_CONCLUDED)
    session = make_session([r])
    from session import STATUS_IN_PROGRESS
    _handle_review_request(1, session, CASES_ROOT)
    assert session.get_rejection(1).status == STATUS_IN_PROGRESS
    print("PASS: 재검토 요청 -> in_progress 전환")


def test_handle_review_request_invalid():
    """존재하지 않는 ID 재검토 요청 시 경고만 출력하고 오류 없음."""
    r = make_rejection(1, "prior_art", "신규성+진보성", [1])
    session = make_session([r])
    _handle_review_request(99, session, CASES_ROOT)  # 오류 없이 통과
    print("PASS: 없는 ID 재검토 -> 경고만 출력")


def test_pending_rejections_skips_concluded():
    """concluded 거절이유가 pending_rejections에서 제외되는지 확인."""
    r1 = make_rejection(1, "prior_art", "신규성+진보성", [1], status=STATUS_CONCLUDED)
    r2 = make_rejection(2, "clarity", "기재불비", [7])
    session = make_session([r1, r2])
    pending = session.pending_rejections()
    assert len(pending) == 1
    assert pending[0].id == 2
    print("PASS: concluded 거절이유 pending에서 제외")


def test_is_all_concluded():
    """모든 거절이유가 concluded일 때 is_all_concluded()가 True를 반환하는지 확인."""
    r1 = make_rejection(1, "prior_art", "신규성+진보성", [1], status=STATUS_CONCLUDED)
    r2 = make_rejection(2, "clarity", "기재불비", [7], status=STATUS_CONCLUDED)
    session = make_session([r1, r2])
    assert session.is_all_concluded() is True
    print("PASS: is_all_concluded() - 전부 완료")


def test_exit_requested_saves_session():
    """ExitRequested 발생 시 세션이 저장되고 SystemExit이 발생하는지 확인."""
    from handlers.base_handler import ExitRequested
    from main import _process_rejections

    r = make_rejection(1, "prior_art", "신규성+진보성", [1, 3, 5], ["D1"])
    session = make_session([r])
    llm = MagicMock()

    with patch("session.save_session") as mock_save, \
         patch("main._make_handler") as mock_make:
        mock_handler = MagicMock()
        mock_handler.handle.side_effect = ExitRequested()
        mock_make.return_value = mock_handler

        try:
            _process_rejections(session, llm, CASES_ROOT)
            print("FAIL: should raise SystemExit")
        except SystemExit as e:
            assert e.code == 0, f"예상 exit code 0, 실제: {e.code}"
            mock_save.assert_called()
            print("PASS: ExitRequested -> 세션 저장 후 SystemExit(0)")


def test_help_output():
    """--help 출력에 주요 인수가 포함되는지 확인."""
    import subprocess, os
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(Path(__file__).parent),
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert "--report" in result.stdout, f"--report 없음: {result.stdout[:200]}"
    assert "case_id" in result.stdout
    print("PASS: --help 출력 확인")


if __name__ == "__main__":
    print("=" * 55)
    print("main.py 통합 흐름 테스트")
    print("=" * 55)
    test_make_handler_prior_art()
    test_make_handler_clarity()
    test_make_handler_unity()
    test_make_handler_other()
    test_make_handler_unknown_falls_back_to_default()
    test_print_rejection_list()
    test_handle_review_request_valid()
    test_handle_review_request_invalid()
    test_pending_rejections_skips_concluded()
    test_is_all_concluded()
    test_exit_requested_saves_session()
    test_help_output()
    print("=" * 55)
    print("모든 테스트 통과")
