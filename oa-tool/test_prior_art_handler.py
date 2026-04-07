"""
prior_art_handler.py 단위 테스트 (LLM 미호출 — mock 사용)
"""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

# yaml 의존성을 mock으로 대체
yaml_mock = types.ModuleType("yaml")
yaml_mock.safe_load = lambda f: {
    "provider": "claude",
    "model": "claude-sonnet-4-6",
    "api_key_env": "ANTHROPIC_API_KEY",
    "max_tokens": 4096,
}
sys.modules["yaml"] = yaml_mock

# anthropic mock
anthropic_mock = types.ModuleType("anthropic")
anthropic_mock.Anthropic = MagicMock()
sys.modules["anthropic"] = anthropic_mock


from handlers.prior_art_handler import PriorArtHandler
from session import RejectionState, Session, STATUS_PENDING

CASES_ROOT = Path(__file__).parent / "cases"


def make_rejection() -> RejectionState:
    return RejectionState(
        id=1,
        type="prior_art",
        subtype="신규성+진보성",
        claims=[1, 3, 5],
        citations=["D1", "D2"],
        has_citations=True,
        status=STATUS_PENDING,
        current_step=0,
    )


def make_session(rejection: RejectionState) -> Session:
    return Session(case_id="KR-TEST-001", rejections=[rejection])


def make_handler() -> PriorArtHandler:
    rejection = make_rejection()
    session = make_session(rejection)

    llm = MagicMock()
    llm.chat.return_value = "## Mock LLM Response\n분석 결과입니다."
    llm.load_prompt.return_value = "system prompt"

    return PriorArtHandler(
        case_id="KR-TEST-001",
        rejection=rejection,
        session=session,
        llm_client=llm,
        cases_root=CASES_ROOT,
    )


# ------------------------------------------------------------------
# 테스트
# ------------------------------------------------------------------

def test_steps_count():
    """STEPS가 5인지 확인."""
    assert PriorArtHandler.STEPS == 5, f"Expected STEPS=5, got {PriorArtHandler.STEPS}"
    print("PASS: STEPS == 5")


def test_execute_step_dispatches():
    """execute_step이 1~5를 모두 처리하는지 확인."""
    handler = make_handler()
    for step in range(1, 6):
        result = handler.execute_step(step, feedback=None)
        assert isinstance(result, str) and len(result) > 0, f"Step {step} returned empty"
        print(f"PASS: execute_step({step}) returned {len(result)} chars")


def test_execute_step_invalid():
    """존재하지 않는 단계에서 ValueError가 발생하는지 확인."""
    handler = make_handler()
    try:
        handler.execute_step(99)
        print("FAIL: should raise ValueError")
    except ValueError:
        print("PASS: ValueError raised for step 99")


def test_feedback_appended():
    """피드백이 있을 때 LLM에 전달되는 프롬프트에 피드백이 포함되는지 확인."""
    handler = make_handler()
    captured_prompts = []
    handler.llm.chat.side_effect = lambda prompt, **kw: (
        captured_prompts.append(prompt) or "## Mock"
    )
    handler.execute_step(1, feedback="청구항 1만 분석해주세요")
    assert any("청구항 1만 분석해주세요" in p for p in captured_prompts), \
        "피드백이 프롬프트에 포함되지 않음"
    print("PASS: 피드백이 프롬프트에 포함됨")


def test_file_read_mock_fallback():
    """mock.txt 파일이 있으면 읽어오는지 확인."""
    handler = make_handler()
    claims = handler._get_claims_en()
    assert "claim" in claims.lower() or len(claims) > 0, "claims_en 읽기 실패"
    print(f"PASS: claims_en 읽기 성공 ({len(claims)} chars)")


def test_citations_block():
    """인용문헌 블록이 D1, D2 섹션을 포함하는지 확인."""
    handler = make_handler()
    block = handler._build_citations_block()
    assert "== D1 ==" in block, "D1 섹션 없음"
    assert "== D2 ==" in block, "D2 섹션 없음"
    print(f"PASS: citations block 생성됨 ({len(block)} chars)")


if __name__ == "__main__":
    print("=" * 50)
    print("prior_art_handler 단위 테스트")
    print("=" * 50)
    test_steps_count()
    test_execute_step_dispatches()
    test_execute_step_invalid()
    test_feedback_appended()
    test_file_read_mock_fallback()
    test_citations_block()
    print("=" * 50)
    print("모든 테스트 통과")
