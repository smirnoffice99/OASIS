"""
handlers/prior_art_handler.py — 선행기술 위반 Handler (유형 A)

분석 흐름:
  Step 1. 본원발명 분석 (청구항 구성요소 + 기술적 의미)
  Step 2. 인용발명 분석 (D1, D2 … 각각 원문 발췌 + 출처 명시)
  Step 3. 차이점 분석 및 진보성 논거 도출 (항상 진보성 기준)
  Step 4. 대응 전략 제안 및 확정

핵심 규칙:
  - 신규성/진보성 구분 없이 Step 4는 항상 진보성 기준으로 분석
  - 인용문헌이 복수일 때 결합 동기(teaching, suggestion, motivation) 부재 여부 검토
  - 인용문헌 발췌 시 출처(컬럼/단락/페이지) 반드시 명시
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from handlers.base_handler import BaseHandler

# 특허번호 인식 패턴 (US출원/등록, JP, KR, WO, EP)
_PATENT_NUM_RE = re.compile(
    r'\b(?:'
    r'US\s*\d{4}/\d{6,7}'           # US 출원: US2020/0008185
    r'|US\s*[\d,]{6,11}\s*[A-Z]\d?' # US 등록: US9,876,543B2
    r'|JP\s*\d{4}[-–]\d{5,7}'       # JP: JP2019-123456
    r'|KR\s*10[-–]\d{4}[-–]\d{7}'   # KR: KR10-2019-0012345
    r'|WO\s*\d{4}/\d{5,6}'          # WO: WO2019/123456
    r'|EP\s*[\d\s]{6,12}[A-Z]\d?'   # EP: EP3456789A1
    r')',
    re.IGNORECASE,
)
from llm_client import LLMClient
from session import Session, RejectionState


class PriorArtHandler(BaseHandler):
    """선행기술 위반(신규성+진보성 통합) 거절이유 처리 핸들러."""

    STEPS = 6

    # ------------------------------------------------------------------
    # 초기화
    # ------------------------------------------------------------------

    def __init__(
        self,
        case_id: str,
        rejection: RejectionState,
        session: Session,
        llm_client: LLMClient,
        cases_root: Path,
    ):
        super().__init__(case_id, rejection, session, llm_client, cases_root)
        # 파일 내용을 캐시하여 반복 I/O 방지
        self._claims_en: Optional[str] = None
        self._spec: Optional[str] = None
        self._oa_raw: Optional[str] = None
        self._citation_texts: dict[str, str] = {}

    # ------------------------------------------------------------------
    # BaseHandler 추상 메서드 구현
    # ------------------------------------------------------------------

    def execute_step(self, step: int, feedback: Optional[str] = None) -> str:
        """
        step 번호에 따라 LLM 분석을 수행하고 결과 텍스트를 반환한다.

        Args:
            step:     1~5
            feedback: 사용자 피드백 (None이면 최초 생성)
        """
        dispatch = {
            1: self._step1_claimed_invention,
            2: self._step2_cited_references,
            3: self._step3_differences_and_inventive_step,
            4: self._step4_response_strategy,
            5: self._step5_confirm_claims,
            6: self._step6_write_comment,
        }
        fn = dispatch.get(step)
        if fn is None:
            raise ValueError(f"PriorArtHandler에 존재하지 않는 단계: {step}")
        return fn(feedback)

    # ------------------------------------------------------------------
    # Step 1 — 본원발명 분석
    # ------------------------------------------------------------------

    def _step1_claimed_invention(self, feedback: Optional[str]) -> str:
        claims_en = self._get_claims_en()
        spec = self._get_spec()
        claims_str = ", ".join(str(c) for c in self.rejection.claims)

        prompt = f"""[Step 1: 본원발명 분석]

아래는 본원 영문 청구항 전문과 명세서 내용입니다.

== 거절 대상 청구항 번호 ==
{claims_str}

== 영문 청구항 (claims_en) ==
{claims_en}

== 명세서 (spec) ==
{spec}

위 자료를 바탕으로 다음을 수행하라:

1. 거절 대상 청구항({claims_str}항) 중 독립항(independent claim)을 식별하라.
   - 다른 청구항을 인용하지 않는 청구항이 독립항이다.
   - 거절 대상({claims_str}항)에 포함되지 않은 독립항은 식별하지 말고 이후 분석에서도 언급하지 마라.

2. 서로 유사한 구성을 갖는 독립항들은 하나의 그룹에 속한다.
   - 카테고리(방법항/장치항/시스템항 등)만 상이하고 실질적 구성이 동일하거나 실질적으로 동일한 독립항들은
     동일 그룹의 독립항들로 취급한다.
     예) "A를 수행하는 방법" 청구항과 "A를 수행하도록 구성된 장치" 청구항이 동일 그룹.
   - 하나의 그룹에서는 최초에 나오는 하나의 독립항만을 대표 독립항으로 식별하라.
   - 그룹 구분 및 각 그룹의 대표 독립항을 명시하라. 같은 그룹 내 나머지 독립항은 "(카테고리만 상이)"로 표시하라.

3. 식별된 대표 독립항들을 중심으로 본원발명에 대한 요약을 제공하라.
   - 각 대표 독립항이 어떤 발명을 청구하는지, 핵심 기술적 특징을 중심으로 설명하라.

4. 종속항은 별도 분석하지 않는다.
   (변리사가 종속항 분석을 요청하는 경우에만 추가 수행)

출력 형식: 마크다운, 한국어
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("prior_art")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 2 — 인용발명 분석
    # ------------------------------------------------------------------

    def _step2_cited_references(self, feedback: Optional[str]) -> str:
        step1_result = self._load_step_result(1)
        claims_en = self._get_claims_en()
        citations_block = self._build_citations_block()
        citations_list = ", ".join(self.rejection.citations)
        examiner_opinion = self._get_oa_raw()

        # 인용발명 검사: 불일치 및 내용 미추출(이미지 PDF 등)
        mismatches: dict[str, tuple[set[str], set[str]]] = {}
        unreadable: list[str] = []
        for cit_id in self.rejection.citations:
            pdf_text = self._get_citation_text(cit_id)
            if pdf_text and not pdf_text.strip():
                # 파일은 열렸으나 텍스트 추출 실패 (이미지 기반 PDF 등)
                unreadable.append(cit_id)
            else:
                result = self._check_citation_mismatch(cit_id)
                if result:
                    mismatches[cit_id] = result

        # 경고 블록 구성
        mismatch_block = ""
        warning_parts = []

        if unreadable:
            unreadable_list = ", ".join(unreadable)
            if feedback:
                warning_parts.append(
                    f"⚠️ [텍스트 추출 불가 — 사용자 요청에 따라 분석 진행]\n"
                    f"- {unreadable_list}: 이미지 기반 PDF로 텍스트를 읽을 수 없습니다.\n"
                    f"사용자가 분석을 요청하였으므로, 심사관 거절이유 원문과 청구항만을 근거로 "
                    f"추론하여 분석하라. 각 해당 섹션 첫 줄에 "
                    f"\"⚠️ 파일 내용을 읽을 수 없어 심사관 지적 및 청구항 기반으로 추론하였습니다.\" 를 표시하라."
                )
            else:
                warning_parts.append(
                    f"⚠️ [인용발명 파일 읽기 실패 — 분석 불가]\n"
                    f"- {unreadable_list}: 이미지 기반 PDF이거나 텍스트 추출에 실패하여 실제 내용을 확인할 수 없습니다.\n"
                    f"해당 인용발명 섹션에 아래 메시지를 출력하고 분석은 수행하지 마라:\n"
                    f"\"⚠️ {unreadable_list} 파일의 텍스트를 읽을 수 없습니다. "
                    f"파일이 이미지 기반 PDF인지 확인하고, 텍스트 PDF로 교체해 주세요.\""
                )

        if mismatches:
            lines = []
            for cit_id, (oa_nums, pdf_nums) in mismatches.items():
                lines.append(
                    f"- {cit_id}: OA 기재 문헌({', '.join(sorted(oa_nums))})과 "
                    f"첨부 파일({', '.join(sorted(pdf_nums))})이 상이함"
                )
            mismatch_summary = "\n".join(lines)

            if feedback:
                warning_parts.append(
                    f"⚠️ [인용발명 불일치 확인됨 — 사용자 요청에 따라 분석 진행]\n"
                    f"{mismatch_summary}\n"
                    f"불일치에도 불구하고 사용자가 분석을 요청하였으므로, 첨부된 파일 내용을 기준으로 분석하라.\n"
                    f"각 불일치 인용발명 섹션 첫 줄에 "
                    f"\"⚠️ 첨부 파일이 OA 기재 문헌과 상이할 수 있습니다.\" 한 줄만 표시하고 분석을 계속하라."
                )
            else:
                first_key = list(mismatches.keys())[0]
                warning_parts.append(
                    f"⚠️ [인용발명 불일치 경고 — 분석 전 확인 필요]\n"
                    f"{mismatch_summary}\n"
                    f"불일치가 감지된 인용발명에 대해서는:\n"
                    f"1. 해당 섹션 상단에 불일치를 명확히 보고하라:\n"
                    f"   \"⚠️ 첨부된 {first_key}({{첨부 파일 번호}})은 OA에 기재된 {{OA 기재 번호}}와 상이합니다. 파일을 확인해 주세요.\"\n"
                    f"2. 해당 인용발명의 분석은 수행하지 말고, 변리사에게 올바른 파일로 교체할 것을 안내하라.\n"
                    f"3. 불일치가 없는 인용발명은 아래 지시에 따라 정상 분석하라."
                )

        if warning_parts:
            mismatch_block = "\n\n" + "\n\n".join(warning_parts) + "\n"

        prompt = f"""[Step 2: 인용발명 분석]

== Step 1 결과 (본원발명 분석 — 대표 독립항 목록 포함) ==
{step1_result}

== 영문 청구항 (claims_en) ==
{claims_en}

== 심사관 거절이유 원문 ==
{examiner_opinion}

== 인용문헌 ({citations_list}) ==
{citations_block}
{mismatch_block}
위 자료를 바탕으로 각 인용문헌({citations_list})에 대해 다음을 수행하라:

1. Step 1에서 식별한 대표 독립항(들)에 대응되는 부분을 중심으로 심사관의 지적을 고려하여 해당 인용문헌 발명의 내용을 요약하라.

2. 인용문헌의 특정 부분을 서술할 때에는 출처(컬럼 번호/단락 번호/페이지)를 명시하라.
   예) "Column 3, Lines 15-40: ..."
       "단락 [0045]: ..."

출력 형식: 마크다운, 인용문헌별 섹션으로 구분
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("prior_art")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 3 — 심사관 지적 타당성 분석
    # ------------------------------------------------------------------

    def _step3_differences_and_inventive_step(self, feedback: Optional[str]) -> str:
        step1_result = self._load_step_result(1)
        step2_result = self._load_step_result(2)
        claims_en = self._get_claims_en()
        spec = self._get_spec()
        examiner_opinion = self._get_oa_raw()
        citations_block = self._build_citations_block()
        citations_list = ", ".join(self.rejection.citations)
        multi_citation = len(self.rejection.citations) > 1

        combination_note = ""
        if multi_citation:
            combination_note = f"\n- 필요시: {citations_list}를 결합하려는 동기(TSM: Teaching, Suggestion, Motivation)가 인용문헌에 명시적으로 존재하는지 여부도 고려하라."

        prompt = f"""[Step 3: 심사관 지적 타당성 분석]

중요: 한국 특허법상 신규성 없는 발명에는 항상 진보성도 없다는 거절이 병행되므로,
신규성/진보성 구분 없이 진보성 기준으로 분석하라.

== Step 1 결과 (본원발명 분석 — 대표 독립항 목록 포함) ==
{step1_result}

== Step 2 결과 (인용발명 분석) ==
{step2_result}

== 영문 청구항 (claims_en) ==
{claims_en}

== 명세서 (spec) ==
{spec}

== 심사관 거절이유 원문 ==
{examiner_opinion}

== 인용문헌 ({citations_list}) ==
{citations_block}

위 자료를 바탕으로 다음을 수행하라:

Step 1에서 식별한 대표 독립항(들) 각각에 대해, 심사관의 신규성/진보성 관련 지적이 타당한지 여부만을 검토하라.

- 종속항에 대한 심사관의 신규성/진보성 지적 타당성은 사용자가 별도로 요청할 경우에만 검토하라.
- 이 단계에서는 영문 코멘트 작성을 위한 전략은 수립하지 않는다.

필요한 경우 아래 관점들을 고려하라:
- 기능적/효과적 차이점
- 예측하지 못한 현저한 효과(Unexpected Remarkable Effect)
- 심사관 논거의 약점 (논리적 비약, 과도한 일반화, 사후적 고찰(hindsight) 등){combination_note}

각 논거는 향후 의견서에 바로 활용할 수 있을 정도로 구체적으로 작성하라.

출력 형식: 마크다운, 대표 독립항별 섹션으로 구분
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("prior_art")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 4 — 전략 선택
    # ------------------------------------------------------------------

    def _step4_response_strategy(self, feedback: Optional[str]) -> str:
        step3_path = (
            self.cases_root / self.case_id
            / f"rejection_{self.rejection.id}"
            / "step_3_result.md"
        )
        step3_result = step3_path.read_text(encoding="utf-8") if step3_path.exists() else ""
        claims_str = ", ".join(str(c) for c in self.rejection.claims)

        prompt = f"""[Step 4: 전략 선택]

== Step 3 결과 (차이점 분석 및 진보성 논거) ==
{step3_result}

== 거절 대상 청구항 ==
{claims_str}항 / 거절 유형: {self.rejection.subtype}

위 분석을 바탕으로 세 가지 전략 중에서 고려할만한 전략들만을 선택적으로 제안하고, 권고안을 제시하라.

A) 보정 전략 (Amendment)
   - 어떤 구성요소를 어떻게 한정하여 차이점을 청구항에 명확히 반영할지 제안
   - 청구항 보정 시 권리범위 축소 리스크 평가
   - 보정 후 기대 효과

B) 의견서 전략 (Written Opinion)
   - Step 3에서 도출된 논거를 활용한 의견서 핵심 주장 구성
   - 신규성 주장 논거 (해당 시)
   - 진보성 주장 논거 (구조적 차이, 현저한 효과, 결합 동기 부재 등)
   - 심사관 논거 약점에 대한 반박 포인트

C) 보정 + 의견서 병행 전략
   - 위 A, B를 결합한 최적 시나리오
   - 보정과 의견서의 역할 분담

[권고안]
   - 세 전략 중 가장 권고하는 방향과 그 이유를 명확히 제시하라.
   - 리스크와 기대 성공 가능성을 함께 평가하라.

이 내용은 변리사가 검토하고 최종 확정한다.
사용자 피드백이 있으면 그에 맞게 전략을 조정하라.

출력 형식: 마크다운, A/B/C 섹션 + 권고안
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 전략을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("prior_art")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 5 — 대표청구항(독립항) 확정
    # ------------------------------------------------------------------

    def _step5_confirm_claims(self, feedback: Optional[str]) -> str:
        step1_result = self._load_step_result(1)
        step4_result = self._load_step_result(4)
        claims_en = self._get_claims_en()

        prompt = f"""[Step 5: 대표청구항(독립항) 확정]

아래 자료를 바탕으로 OA 대응에 사용할 최종 대표 청구항(Representative Claim)을 제안하라.

== Step 1 결과 (본원발명 — 독립항 목록 및 구성요소) ==
{step1_result}

== Step 4 결과 (대응 전략) ==
{step4_result}

== 영문 청구항 원문 ==
{claims_en}

수행 내용:
1. Step 4의 권고 전략을 확인하라.
   - 보정 전략(Amendment)이면: 보정된 독립항 전문을 제안한다.
   - 의견서 전략(Written Opinion)이면: 현행 독립항 원문을 그대로 제시한다.
   - 복수의 독립항이 있으면 각각 제시한다.

2. 출력 형식 (아래 형식을 반드시 준수하라):

## 확정 대상 독립항

[독립항 번호 및 영문 전문 — claims_en의 원문 그대로]

## 보정/유지 이유

[Step 4 전략 요약, 2-3문장]

## 변리사 검토 사항

[있으면 기재, 없으면 "(없음)"]

---
사용자가 승인하면 이 청구항이 Step 6 코멘트 작성의 기준이 된다.
사용자가 피드백으로 청구항 원문을 직접 입력하거나 수정 지시를 입력하면 그 내용을 반영하여 재작성하라.
"""
        if feedback:
            prompt += f"\n\n[사용자 확정 내용 또는 수정 지시]\n{feedback}"

        system = self.llm.load_prompt("prior_art")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 6 — 영문 코멘트 작성
    # ------------------------------------------------------------------

    def _step6_write_comment(self, feedback: Optional[str]) -> str:
        step3_result = self._load_step_result(3)
        step4_result = self._load_step_result(4)
        step5_result = self._load_step_result(5)
        oa_raw = self._get_oa_raw()
        claims_en = self._get_claims_en()
        citations_block = self._build_citations_block()
        claims_str = ", ".join(str(c) for c in self.rejection.claims)
        citations_list = ", ".join(self.rejection.citations)
        sample_text = self._get_sample_reference()

        prompt = f"""[Step 6: Write English Comment]

Write an English-only OA response comment strictly following the structure and phrasing of the sample below.

== Cited references ==
{citations_list}

== Examiner's rejection (original) ==
{oa_raw}

== Claims (claims_en) ==
{claims_en}

== Cited reference texts ==
{citations_block}

== Step 3 result (differences & inventive step arguments) ==
{step3_result}

== Step 4 result (selected strategy) ==
{step4_result}

== Step 5 confirmed claim(s) ==
{step5_result}

== [SAMPLE — follow this structure exactly] ==
{sample_text}

---

WRITING RULES — follow strictly:

[LANGUAGE]
- The entire output MUST be in English. No Korean characters whatsoever.
- All element names, feature descriptions, and technical terms must be written in English.
  If a source document contains Korean, translate it into English; never mix Korean and English.
- Use the exact terminology from claims_en verbatim.

[DEPENDENT CLAIMS]
- Do NOT discuss dependent claims individually or at length.
- One closing sentence only: "A similar argument can be made for the other independent claims."

[CITED REFERENCE LIST]
- List each reference as: "D1: [document number / title] ([date])"
- Extract number, publication number, and date from the examiner's rejection text.

[1. Status of counterpart applications]
Output the following block EXACTLY as written below — every sentence, every numbered option (1)~(4), in this exact order.
Do NOT select, omit, reorder, or rephrase any part. Output all of it verbatim.
Only fill in the placeholders [patent number], [D1–Dx], and (date) using information from the examiner's rejection; if unavailable, leave them as-is.

---BEGIN VERBATIM BLOCK---
We reviewed the prosecution of the US, EP, and JP counterpart applications to leverage similar claim amendments and arguments, where possible. A summary thereof is as follows:

We think that the features of the issued claims of counterpart US patent No. [patent number] are distinguishable from those disclosed in [D1–Dx]. Thus, we will provide you with our comments below by making reference to the issued US claims.

(1) Since the same references were cited during the US prosecution, we will provide our comments below by making reference to the US response filed on (date).

(2) Although some of the references were cited during the US prosecution, since main reference D1 has been newly cited by the Korean examiner, we will provide our comments below based on our own analysis.

(3) Since none of the references were cited during the prosecution of the US, EP, or JP counterpart application, we will provide our comments below based on our own analysis.

(4) Please note that the US response filed on (date) in response to the OA with the same cited references as the subject Korean case was already leveraged on filing a response to the previous OA.
---END VERBATIM BLOCK---

[2. Our suggestion]
Write in the following order:

(1) Examiner's allegations
    "The examiner alleged that claims [X] do not have novelty over [D#]."
    "Furthermore, the examiner alleged that claims [Y] do not have an inventive step over [D#, D#, ...]."
    → If only inventive step is rejected, use a single sentence with "an inventive step."

(2) STRATEGY-DEPENDENT BLOCK — read Step 4 result carefully and choose EXACTLY ONE of the following two options. Do NOT output both.

    ■ IF Step 4 strategy is "Written Opinion" (no amendment, claims maintained as-is):
      Output ONLY this block:
        "However, we disagree with the examiner. Claim [N] is as follows:"
        [Full verbatim text of the Step 5 confirmed claim — no changes]
        "[Pending] claim [N] recites the features of '[key distinguishing feature].'
         We think that [D#] fails to teach or suggest these features of pending claim [N]."

    ■ IF Step 4 strategy is "Amendment" or "Amendment + Written Opinion" (claims are amended):
      Output ONLY this block:
        "In order to overcome this rejection reason, we suggest amending claim [N] as follows:"
        [Full verbatim text of the Step 5 confirmed (amended) claim — no changes]
        "This amendment is supported by paragraphs [xxxx] of the PCT application.
         A similar amendment can be made for the other independent claims.
         For more details, please refer to our Proposed Claims."

(3) Per-reference discussion (one paragraph per reference, independent claims only)
    "[D#] relates to [subject — translate from Korean to English if needed].
     In this regard, [relevant content from D# — quote or translate from original, citing column/paragraph/page].
     However, [reason the inventive feature is absent in D#].
     Thus, [D#] fails to teach or suggest the feature of '[feature from Step 5 claim]'
     as recited in [proposed/pending] claim [N]."

(4) Closing
    "A similar argument can be made for the other independent claims.
     Therefore, if you approve of our suggestion, we will argue these points in an Argument,
     based on amended claims."

Output format: Markdown with ## section headings.
"""
        if feedback:
            prompt += f"\n\n[사용자 수정 지시 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("prior_art")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # 파일 캐시 헬퍼
    # ------------------------------------------------------------------

    def _get_claims_en(self) -> str:
        if self._claims_en is None:
            # .docx 우선, 없으면 mock .txt
            self._claims_en = (
                self.read_case_file("claims_en.docx")
                or self.read_case_file("claims_en_mock.txt")
            )
        return self._claims_en

    def _get_spec(self) -> str:
        if self._spec is None:
            self._spec = (
                self.read_case_file("spec.pdf")
                or self.read_case_file("spec_mock.txt")
            )
        return self._spec

    def _get_oa_raw(self) -> str:
        if self._oa_raw is None:
            self._oa_raw = (
                self.read_case_file("oa.pdf")
                or self.read_case_file("oa_mock.txt")
            )
        return self._oa_raw

    def _get_citation_text(self, citation_id: str) -> str:
        """D1, D2 등 인용문헌 텍스트를 반환한다 (캐시 적용)."""
        if citation_id not in self._citation_texts:
            text = self.read_citation(citation_id)
            if not text:
                self._print(f"  [경고] 인용문헌 {citation_id} 파일을 찾을 수 없습니다.")
            self._citation_texts[citation_id] = text
        return self._citation_texts[citation_id]

    def _load_step_result(self, step: int) -> str:
        """저장된 step_{n}_result.md 파일을 읽어 반환한다."""
        path = (
            self.cases_root / self.case_id
            / f"rejection_{self.rejection.id}"
            / f"step_{step}_result.md"
        )
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _get_sample_reference(self) -> str:
        """
        samples/prior_art/ 폴더의 첫 번째 .docx 또는 .txt 샘플을 읽어
        양식 참고용 텍스트로 반환한다.
        """
        samples_dir = self.cases_root.parent / "samples" / "prior_art"
        if not samples_dir.exists():
            return "(샘플 없음)"

        for suffix in (".docx", ".txt"):
            for sample_path in sorted(samples_dir.glob(f"*{suffix}")):
                try:
                    if suffix == ".docx":
                        return self._read_docx(sample_path)
                    else:
                        return sample_path.read_text(encoding="utf-8")
                except Exception:
                    continue
        return "(샘플 없음)"

    def _extract_patent_numbers(self, text: str) -> set[str]:
        """텍스트에서 특허번호를 추출한다."""
        return {m.group() for m in _PATENT_NUM_RE.finditer(text)}

    def _normalize_patent_num(self, num: str) -> str:
        """비교용 정규화: 공백·쉼표 제거, 대문자화, 끝의 '호'·종류코드(A1/B2 등) 제거."""
        n = re.sub(r'[\s,]', '', num).upper()
        n = re.sub(r'호$', '', n)
        n = re.sub(r'[A-Z]\d?$', '', n)
        return n

    def _get_oa_expected_numbers(self, cit_id: str) -> set[str]:
        """
        OA 텍스트에서 특정 인용문헌(D1, D2 …)과 연관된 특허번호를 추출한다.
        각 D번호·인용발명N 언급 위치 이후 500자 창에서 탐색한다.
        """
        oa_text = self._get_oa_raw()
        num = cit_id[1:]  # "D1" → "1"
        patterns = [
            rf'\bD{num}\b',
            rf'인용\s*발명\s*{num}',
            rf'인용\s*문헌\s*{num}',
        ]
        found: set[str] = set()
        for pat in patterns:
            for m in re.finditer(pat, oa_text):
                window = oa_text[m.start(): m.start() + 500]
                found |= self._extract_patent_numbers(window)
        return found

    def _check_citation_mismatch(
        self, cit_id: str
    ) -> tuple[set[str], set[str]] | None:
        """
        OA 기재 특허번호와 첨부 PDF의 특허번호를 비교한다.
        - 불일치(교집합 없음): (oa_nums, pdf_nums) 반환
        - 일치 또는 판단 불가(번호 미검출): None 반환
        """
        pdf_text = self._get_citation_text(cit_id)
        if not pdf_text:
            return None  # 파일 없음은 별도 경고로 처리

        oa_nums = self._get_oa_expected_numbers(cit_id)
        if not oa_nums:
            return None  # OA에서 번호 미검출 → 판단 보류

        # PDF 앞 3000자(표지·헤더)에서 번호 탐색
        pdf_nums = self._extract_patent_numbers(pdf_text[:3000])
        if not pdf_nums:
            return None  # PDF에서도 번호 미검출 → 판단 보류

        oa_norms = {self._normalize_patent_num(n) for n in oa_nums}
        pdf_norms = {self._normalize_patent_num(n) for n in pdf_nums}

        # 어느 한쪽이 다른 쪽의 부분 문자열이면 일치로 간주
        for a in oa_norms:
            for b in pdf_norms:
                if a in b or b in a:
                    return None  # 일치

        return (oa_nums, pdf_nums)

    def _build_citations_block(self) -> str:
        """
        모든 인용문헌 텍스트를 하나의 블록으로 조합한다.
        예) == D1 ==\n...\n\n== D2 ==\n...
        """
        parts = []
        for cit_id in self.rejection.citations:
            text = self._get_citation_text(cit_id)
            parts.append(f"== {cit_id} ==\n{text}")
        return "\n\n".join(parts) if parts else "(인용문헌 없음)"
