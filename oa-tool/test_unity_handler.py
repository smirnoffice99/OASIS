"""
unity_handler.py 단위 테스트 (LLM 미호출 — mock 사용)
두 가지 흐름 (has_citations=False / True) 모두 검증
"""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent))

yaml_mock = types.ModuleType("yaml")
yaml_mock.safe_load = lambda f: {
    "provider": "claude", "model": "claude-sonnet-4-6",
    "api_key_env": "ANTHROPIC_API_KEY", "max_tokens": 4096,
}
sys.modules["yaml"] = yaml_mock

anthropic_mock = types.ModuleType("anthropic")
anthropic_mock.Anthropic = MagicMock()
sys.modules["anthropic"] = anthropic_mock

from handlers.unity_handler import UnityHandler
from session import RejectionState, Session, STATUS_PENDING

CASES_ROOT = Path(__file__).parent / "cases"


def make_handler(has_citations: bool) -> UnityHandler:
    rejection = RejectionState(
        id=3,
        type="unity",
        subtype="단일성 위반",
        claims=list(range(1, 9)),
        citations=["D1"] if has_citations else [],
        has_citations=has_citations,
        status=STATUS_PENDING,
        current_step=0,
    )
    session = Session(case_id="KR-TEST-001", rejections=[rejection])
    llm = MagicMock()
    llm.chat.return_value = "## Mock LLM Response\n분석 결과입니다."
    llm.load_prompt.return_value = "system prompt"
    return UnityHandler(
        case_id="KR-TEST-001",
        rejection=rejection,
        session=session,
        llm_client=llm,
        cases_root=CASES_ROOT,
    )


# ------------------------------------------------------------------

def test_steps_count():
    assert UnityHandler.STEPS == 3
    print("PASS: STEPS == 3")


def test_no_citations_all_steps():
    """has_citations=False 흐름: Step 1~3 모두 정상 실행."""
    handler = make_handler(has_citations=False)
    for step in range(1, 4):
        result = handler.execute_step(step)
        assert isinstance(result, str) and len(result) > 0
        print(f"PASS: [no_citations] execute_step({step}) OK ({len(result)} chars)")


def test_with_citations_all_steps():
    """has_citations=True 흐름: Step 1~3 모두 정상 실행."""
    handler = make_handler(has_citations=True)
    for step in range(1, 4):
        result = handler.execute_step(step)
        assert isinstance(result, str) and len(result) > 0
        print(f"PASS: [with_citations] execute_step({step}) OK ({len(result)} chars)")


def test_invalid_step():
    handler = make_handler(has_citations=False)
    try:
        handler.execute_step(4)
        print("FAIL: should raise ValueError")
    except ValueError:
        print("PASS: ValueError raised for step 4")


def test_no_citations_uses_unity_prompt():
    """has_citations=False 시 'unity' 프롬프트 사용."""
    handler = make_handler(has_citations=False)
    handler.execute_step(1)
    handler.llm.load_prompt.assert_called_with("unity")
    print("PASS: has_citations=False → 'unity' 프롬프트 사용")


def test_with_citations_uses_unity_with_citations_prompt():
    """has_citations=True 시 'unity_with_citations' 프롬프트 사용."""
    handler = make_handler(has_citations=True)
    handler.execute_step(1)
    handler.llm.load_prompt.assert_called_with("unity_with_citations")
    print("PASS: has_citations=True → 'unity_with_citations' 프롬프트 사용")


def test_step3_strategy_used_for_both_flows():
    """Step 3은 두 흐름 모두 동일한 _step3_strategy 메서드를 사용."""
    for has_cit in (False, True):
        handler = make_handler(has_citations=has_cit)
        captured = []
        handler.llm.chat.side_effect = lambda p, **kw: captured.append(p) or "## Mock"
        handler.execute_step(3)
        assert any("대응 전략" in p for p in captured), \
            f"has_citations={has_cit}: Step 3 프롬프트에 '대응 전략' 없음"
        print(f"PASS: [has_citations={has_cit}] Step 3 전략 프롬프트 확인")


def test_with_citations_step1_includes_citation_text():
    """has_citations=True Step 1 프롬프트에 D1 내용이 포함되는지 확인."""
    handler = make_handler(has_citations=True)
    captured = []
    handler.llm.chat.side_effect = lambda p, **kw: captured.append(p) or "## Mock"
    handler.execute_step(1)
    assert any("D1" in p for p in captured), "Step 1 프롬프트에 D1 없음"
    print("PASS: [with_citations] Step 1 프롬프트에 D1 포함")


def test_no_citations_step1_no_citation_block():
    """has_citations=False Step 1 프롬프트에 인용문헌 블록이 없어야 함."""
    handler = make_handler(has_citations=False)
    captured = []
    handler.llm.chat.side_effect = lambda p, **kw: captured.append(p) or "## Mock"
    handler.execute_step(1)
    assert not any("== D1 ==" in p for p in captured), \
        "has_citations=False인데 Step 1에 D1 블록이 포함됨"
    print("PASS: [no_citations] Step 1 프롬프트에 D1 블록 없음")


def test_feedback_included():
    handler = make_handler(has_citations=True)
    captured = []
    handler.llm.chat.side_effect = lambda p, **kw: captured.append(p) or "## Mock"
    handler.execute_step(2, feedback="STF를 더 구체적으로 분석해 주세요")
    assert any("STF를 더 구체적으로" in p for p in captured)
    print("PASS: 피드백이 프롬프트에 포함됨")


if __name__ == "__main__":
    print("=" * 55)
    print("unity_handler 단위 테스트")
    print("=" * 55)
    test_steps_count()
    test_no_citations_all_steps()
    test_with_citations_all_steps()
    test_invalid_step()
    test_no_citations_uses_unity_prompt()
    test_with_citations_uses_unity_with_citations_prompt()
    test_step3_strategy_used_for_both_flows()
    test_with_citations_step1_includes_citation_text()
    test_no_citations_step1_no_citation_block()
    test_feedback_included()
    print("=" * 55)
    print("모든 테스트 통과")
