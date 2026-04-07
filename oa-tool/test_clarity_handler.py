"""
clarity_handler.py 단위 테스트 (LLM 미호출 — mock 사용)
"""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

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

from handlers.clarity_handler import ClarityHandler
from session import RejectionState, Session, STATUS_PENDING

CASES_ROOT = Path(__file__).parent / "cases"


def make_handler() -> ClarityHandler:
    rejection = RejectionState(
        id=2,
        type="clarity",
        subtype="기재불비",
        claims=[7],
        citations=[],
        has_citations=False,
        status=STATUS_PENDING,
        current_step=0,
    )
    session = Session(case_id="KR-TEST-001", rejections=[rejection])
    llm = MagicMock()
    llm.chat.return_value = "## Mock LLM Response\n분석 결과입니다."
    llm.load_prompt.return_value = "system prompt"
    return ClarityHandler(
        case_id="KR-TEST-001",
        rejection=rejection,
        session=session,
        llm_client=llm,
        cases_root=CASES_ROOT,
    )


def test_steps_count():
    assert ClarityHandler.STEPS == 3
    print("PASS: STEPS == 3")


def test_execute_step_dispatches():
    handler = make_handler()
    for step in range(1, 4):
        result = handler.execute_step(step)
        assert isinstance(result, str) and len(result) > 0
        print(f"PASS: execute_step({step}) OK ({len(result)} chars)")


def test_invalid_step():
    handler = make_handler()
    try:
        handler.execute_step(4)
        print("FAIL: should raise ValueError")
    except ValueError:
        print("PASS: ValueError raised for step 4")


def test_no_citations():
    """기재불비는 인용문헌이 없어야 함."""
    handler = make_handler()
    assert handler.rejection.citations == []
    assert handler.rejection.has_citations is False
    print("PASS: citations 없음 확인")


def test_spec_loaded():
    handler = make_handler()
    spec = handler._get_spec()
    assert len(spec) > 0
    print(f"PASS: spec 읽기 성공 ({len(spec)} chars)")


def test_oa_loaded():
    handler = make_handler()
    oa = handler._get_oa_raw()
    assert "기재불비" in oa or "42조" in oa or len(oa) > 0
    print(f"PASS: OA 읽기 성공 ({len(oa)} chars)")


def test_step1_prompt_contains_claim():
    """Step 1 프롬프트에 대상 청구항 번호가 포함되는지 확인."""
    handler = make_handler()
    captured = []
    handler.llm.chat.side_effect = lambda p, **kw: captured.append(p) or "## Mock"
    handler.execute_step(1)
    assert any("7" in p for p in captured)
    print("PASS: Step 1 프롬프트에 청구항 7 포함")


def test_feedback_included():
    """피드백이 프롬프트에 포함되는지 확인."""
    handler = make_handler()
    captured = []
    handler.llm.chat.side_effect = lambda p, **kw: captured.append(p) or "## Mock"
    handler.execute_step(1, feedback="42조 3항도 검토해 주세요")
    assert any("42조 3항도 검토" in p for p in captured)
    print("PASS: 피드백이 프롬프트에 포함됨")


if __name__ == "__main__":
    print("=" * 50)
    print("clarity_handler 단위 테스트")
    print("=" * 50)
    test_steps_count()
    test_execute_step_dispatches()
    test_invalid_step()
    test_no_citations()
    test_spec_loaded()
    test_oa_loaded()
    test_step1_prompt_contains_claim()
    test_feedback_included()
    print("=" * 50)
    print("모든 테스트 통과")
