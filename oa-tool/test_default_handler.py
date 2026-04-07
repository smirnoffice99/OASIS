"""
default_handler.py 단위 테스트 (LLM 미호출 — mock 사용)
"""

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, call

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

from handlers.default_handler import DefaultHandler
from session import RejectionState, Session, STATUS_PENDING

CASES_ROOT = Path(__file__).parent / "cases"
CASE_ID = "KR-TEST-001"


def make_handler() -> DefaultHandler:
    rejection = RejectionState(
        id=99,
        type="other",
        subtype="기타 거절이유",
        claims=[1, 2],
        citations=[],
        has_citations=False,
        status=STATUS_PENDING,
        current_step=0,
    )
    session = Session(case_id=CASE_ID, rejections=[rejection])
    llm = MagicMock()
    llm.chat.return_value = (
        "## 거절이유 요약\n테스트 거절이유입니다.\n\n"
        "## 제안 분석 단계\n1. 거절이유 법적 근거 분석\n2. 청구항 영향 범위 분석\n"
    )
    llm.load_prompt.return_value = "system prompt"
    return DefaultHandler(
        case_id=CASE_ID,
        rejection=rejection,
        session=session,
        llm_client=llm,
        cases_root=CASES_ROOT,
    )


def cleanup_plan(handler: DefaultHandler):
    """테스트 후 생성된 plan 파일을 정리한다."""
    plan_path = handler._plan_path()
    if plan_path.exists():
        plan_path.unlink()


# ------------------------------------------------------------------

def test_parse_plan_steps():
    """_parse_plan_steps가 번호 목록을 올바르게 파싱하는지 확인."""
    text = (
        "## 제안 분석 단계\n"
        "1. 법적 근거 분석\n"
        "2. 청구항 검토\n"
        "3. 대응 전략 제안 및 확정\n"  # 이 줄은 제외되어야 함
    )
    steps = DefaultHandler._parse_plan_steps(text)
    assert steps == ["법적 근거 분석", "청구항 검토"], f"파싱 결과: {steps}"
    print(f"PASS: _parse_plan_steps - '대응 전략' 제외, {len(steps)}단계 파싱")


def test_parse_plan_steps_empty():
    """단계 목록이 없는 경우 빈 리스트를 반환하는지 확인."""
    steps = DefaultHandler._parse_plan_steps("분석 내용만 있고 번호 목록 없음")
    assert steps == []
    print("PASS: _parse_plan_steps - 빈 텍스트 -> []")


def test_save_and_load_plan():
    """계획 저장 후 복원이 정상 동작하는지 확인."""
    handler = make_handler()
    plan = ["법적 근거 분석", "청구항 영향 분석"]
    handler._save_plan(plan)
    loaded = handler._load_plan()
    assert loaded == plan, f"복원된 계획: {loaded}"
    cleanup_plan(handler)
    print("PASS: 계획 저장/복원 정상")


def test_load_plan_missing():
    """계획 파일이 없을 때 빈 리스트를 반환하는지 확인."""
    handler = make_handler()
    cleanup_plan(handler)  # 혹시 남아있는 파일 제거
    loaded = handler._load_plan()
    assert loaded == []
    print("PASS: 계획 파일 없음 → []")


def test_steps_dynamic():
    """STEPS가 계획 단계 수 + 1(전략)로 설정되는지 확인."""
    handler = make_handler()
    handler._plan = ["단계A", "단계B", "단계C"]
    handler.STEPS = len(handler._plan) + 1
    assert handler.STEPS == 4
    print("PASS: STEPS = 계획 단계(3) + 전략(1) = 4")


def test_execute_step_analysis():
    """분석 단계(execute_step)가 LLM을 호출하는지 확인."""
    handler = make_handler()
    handler._plan = ["법적 근거 분석", "청구항 검토"]
    handler.STEPS = len(handler._plan) + 1

    captured = []
    handler.llm.chat.side_effect = lambda p, **kw: captured.append(p) or "## Mock"

    result = handler.execute_step(1)
    assert isinstance(result, str)
    assert any("법적 근거 분석" in p for p in captured), "Step 제목이 프롬프트에 없음"
    print(f"PASS: execute_step(1) 분석 단계 실행 ({len(result)} chars)")


def test_execute_step_strategy():
    """전략 단계(마지막 step)가 전략 프롬프트를 사용하는지 확인."""
    handler = make_handler()
    handler._plan = ["법적 근거 분석"]
    handler.STEPS = 2  # 분석 1 + 전략 1

    captured = []
    handler.llm.chat.side_effect = lambda p, **kw: captured.append(p) or "## Mock"

    result = handler.execute_step(2)  # 전략 단계
    assert any("대응 전략" in p for p in captured), "전략 단계 프롬프트에 '대응 전략' 없음"
    print(f"PASS: execute_step(2) 전략 단계 실행 ({len(result)} chars)")


def test_execute_step_invalid():
    """계획 범위를 벗어난 단계에서 ValueError 발생 확인."""
    handler = make_handler()
    handler._plan = ["단계A"]
    handler.STEPS = 2
    try:
        handler.execute_step(99)
        print("FAIL: should raise ValueError")
    except ValueError:
        print("PASS: ValueError raised for step 99")


def test_feedback_included():
    """피드백이 프롬프트에 포함되는지 확인."""
    handler = make_handler()
    handler._plan = ["법적 근거 분석"]
    handler.STEPS = 2
    captured = []
    handler.llm.chat.side_effect = lambda p, **kw: captured.append(p) or "## Mock"
    handler.execute_step(1, feedback="더 구체적으로 분석해 주세요")
    assert any("더 구체적으로 분석" in p for p in captured)
    print("PASS: 피드백이 프롬프트에 포함됨")


def test_collect_prior_results_empty():
    """첫 번째 단계에서는 이전 결과가 없어야 함."""
    handler = make_handler()
    handler._plan = ["단계A", "단계B"]
    result = handler._collect_prior_results(1)  # step 1 이전 = 없음
    assert result == ""
    print("PASS: Step 1 이전 결과 없음 확인")


if __name__ == "__main__":
    print("=" * 55)
    print("default_handler 단위 테스트")
    print("=" * 55)
    test_parse_plan_steps()
    test_parse_plan_steps_empty()
    test_save_and_load_plan()
    test_load_plan_missing()
    test_steps_dynamic()
    test_execute_step_analysis()
    test_execute_step_strategy()
    test_execute_step_invalid()
    test_feedback_included()
    test_collect_prior_results_empty()
    print("=" * 55)
    print("모든 테스트 통과")
