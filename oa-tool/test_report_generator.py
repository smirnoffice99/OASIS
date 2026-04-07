"""
report_generator.py 단위 테스트 (LLM + docx 미설치 환경 대응)
"""

import json
import shutil
import sys
import tempfile
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

from report_generator import ReportGenerator, _format_claims, _rejection_title
from session import Session, RejectionState, STATUS_CONCLUDED

CASES_ROOT = Path(__file__).parent / "cases"
CASE_ID = "KR-TEST-001"


def make_concluded_rejection(rid: int, rtype: str, subtype: str, claims: list, citations: list = None) -> RejectionState:
    return RejectionState(
        id=rid, type=rtype, subtype=subtype,
        claims=claims, citations=citations or [],
        has_citations=bool(citations),
        status=STATUS_CONCLUDED, current_step=99,
    )


def make_generator(rejections: list[RejectionState]) -> ReportGenerator:
    session = Session(case_id=CASE_ID, rejections=rejections)
    llm = MagicMock()
    llm.chat.return_value = "This is a mock English response for the section."
    llm.load_prompt.return_value = "system prompt"
    gen = ReportGenerator(
        case_id=CASE_ID,
        session=session,
        llm_client=llm,
        cases_root=CASES_ROOT,
    )
    return gen


# ------------------------------------------------------------------

def test_format_claims():
    assert _format_claims([1]) == "Claim 1"
    assert _format_claims([1, 3, 5]) == "Claims 1, 3, 5"
    assert _format_claims([]) == "Claims (unspecified)"
    print("PASS: _format_claims")


def test_rejection_title_prior_art():
    r = make_concluded_rejection(1, "prior_art", "신규성+진보성", [1, 3, 5], ["D1", "D2"])
    title = _rejection_title(r)
    assert "Lack of Novelty" in title
    assert "Claims 1, 3, 5" in title
    assert "D1" in title
    print(f"PASS: _rejection_title prior_art -> '{title}'")


def test_rejection_title_clarity():
    r = make_concluded_rejection(2, "clarity", "기재불비", [7])
    title = _rejection_title(r)
    assert "Lack of Clarity" in title
    assert "Claim 7" in title
    print(f"PASS: _rejection_title clarity -> '{title}'")


def test_rejection_title_unity():
    r = make_concluded_rejection(3, "unity", "단일성 위반", list(range(1, 9)), ["D1"])
    title = _rejection_title(r)
    assert "Unity" in title
    print(f"PASS: _rejection_title unity -> '{title}'")


def test_load_analysis_data_with_mock_files():
    """cases/KR-TEST-001/rejection_1/ 에 파일이 있으면 로드되는지 확인."""
    r = make_concluded_rejection(1, "prior_art", "신규성+진보성", [1, 3, 5], ["D1", "D2"])
    gen = make_generator([r])

    # 임시 step 파일 생성
    rejection_dir = CASES_ROOT / CASE_ID / "rejection_1"
    rejection_dir.mkdir(parents=True, exist_ok=True)
    test_file = rejection_dir / "step_1_result.md"
    test_file.write_text("## Step 1 분석 결과\n본원 청구항 분석 내용", encoding="utf-8")

    data = gen._load_analysis_data(r)
    assert "step_1" in data
    assert "본원 청구항" in data["step_1"]
    assert "all_steps" in data

    # 정리
    test_file.unlink()
    print("PASS: _load_analysis_data - step 파일 로드")


def test_load_analysis_data_empty():
    """분석 파일이 없어도 빈 dict 반환 (오류 없음)."""
    r = make_concluded_rejection(99, "other", "기타", [1])
    gen = make_generator([r])
    data = gen._load_analysis_data(r)
    assert "all_steps" in data
    assert data["all_steps"] == ""
    print("PASS: _load_analysis_data - 파일 없을 때 빈 dict")


def test_get_claims_en():
    """claims_en_mock.txt를 읽어오는지 확인."""
    r = make_concluded_rejection(1, "prior_art", "신규성+진보성", [1])
    gen = make_generator([r])
    claims = gen._get_claims_en()
    assert len(claims) > 0
    assert "claim" in claims.lower()
    print(f"PASS: _get_claims_en ({len(claims)} chars)")


def test_generate_section_calls_llm():
    """_generate_section이 LLM을 호출하는지 확인."""
    r = make_concluded_rejection(1, "prior_art", "신규성+진보성", [1, 3, 5], ["D1"])
    gen = make_generator([r])
    section = gen._generate_section(r)
    assert gen.llm.chat.called
    assert "title" in section
    assert "summary" in section
    assert "strategy" in section
    print(f"PASS: _generate_section LLM 호출 확인 ({gen.llm.chat.call_count}회)")


def test_generate_section_prior_art_has_subsections():
    """prior_art 섹션에 analysis_subsections가 생성되는지 확인."""
    r = make_concluded_rejection(1, "prior_art", "신규성+진보성", [1, 3, 5], ["D1", "D2"])
    gen = make_generator([r])
    section = gen._generate_section(r)
    assert section["analysis_subsections"] is not None
    assert "claimed_invention" in section["analysis_subsections"]
    assert "cited_references" in section["analysis_subsections"]
    assert "differences" in section["analysis_subsections"]
    assert section["analysis"] is None
    print("PASS: prior_art 섹션 - analysis_subsections 생성")


def test_generate_section_clarity_no_subsections():
    """clarity 섹션에 analysis_subsections가 없는지 확인."""
    r = make_concluded_rejection(2, "clarity", "기재불비", [7])
    gen = make_generator([r])
    section = gen._generate_section(r)
    assert section["analysis_subsections"] is None
    assert section["analysis"] is not None
    print("PASS: clarity 섹션 - subsections 없음, analysis 있음")


def test_write_txt_fallback():
    """python-docx 없이 .txt 폴백이 정상 작성되는지 확인."""
    r = make_concluded_rejection(1, "prior_art", "신규성+진보성", [1, 3, 5], ["D1"])
    gen = make_generator([r])
    section = {
        "rejection": r,
        "title": "Lack of Novelty and Inventive Step — Claims 1, 3, 5 / D1",
        "summary": "The examiner rejected claims 1, 3, and 5.",
        "analysis": None,
        "analysis_subsections": {
            "claimed_invention": "The claimed invention includes...",
            "cited_references": "D1 discloses...",
            "differences": "The key differences are...",
        },
        "strategy": "We propose to file a written argument.",
    }
    overall = "Overall, we are confident in overcoming the rejections."

    tmp = Path(tempfile.mkdtemp())
    txt_path = tmp / "final_comment.txt"
    gen._write_txt_fallback([section], overall, txt_path)
    assert txt_path.exists()
    content = txt_path.read_text(encoding="utf-8")
    assert "Rejection Ground 1" in content
    assert "Summary of Rejection" in content
    assert "Overall Strategy" in content
    shutil.rmtree(tmp)
    print("PASS: _write_txt_fallback 정상 작성")


def test_no_concluded_raises():
    """concluded 거절이유가 없으면 ValueError 발생."""
    from session import STATUS_PENDING
    r = RejectionState(
        id=1, type="prior_art", subtype="신규성+진보성",
        claims=[1], citations=[], has_citations=False,
        status=STATUS_PENDING, current_step=0,
    )
    gen = make_generator([r])
    try:
        gen.generate()
        print("FAIL: should raise ValueError")
    except ValueError as e:
        print(f"PASS: concluded 없음 -> ValueError")


def test_build_prompt_includes_samples():
    """샘플이 있을 때 프롬프트에 샘플이 포함되는지 확인."""
    r = make_concluded_rejection(1, "clarity", "기재불비", [7])
    gen = make_generator([r])
    prompt = gen._build_prompt(
        task="Write N.1",
        instruction="Be concise.",
        rejection=r,
        data={"all_steps": "분석 내용"},
        samples=["Sample comment 1 text.", "Sample comment 2 text."],
        claims_en="Claim 1: A method...",
    )
    assert "Sample 1" in prompt
    assert "Sample 2" in prompt
    assert "Claim 1" in prompt
    print("PASS: _build_prompt - 샘플 포함 확인")


if __name__ == "__main__":
    print("=" * 55)
    print("report_generator 단위 테스트")
    print("=" * 55)
    test_format_claims()
    test_rejection_title_prior_art()
    test_rejection_title_clarity()
    test_rejection_title_unity()
    test_load_analysis_data_with_mock_files()
    test_load_analysis_data_empty()
    test_get_claims_en()
    test_generate_section_calls_llm()
    test_generate_section_prior_art_has_subsections()
    test_generate_section_clarity_no_subsections()
    test_write_txt_fallback()
    test_no_concluded_raises()
    test_build_prompt_includes_samples()
    print("=" * 55)
    print("모든 테스트 통과")
