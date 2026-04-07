"""
handlers/unity_handler.py — 단일성 위반 Handler (유형 C)

has_citations 플래그에 따라 두 가지 흐름 자동 분기:

[has_citations=False — 인용발명 없음]
  Step 1. 단일성 위반 내용 파악 (청구항 그룹 파악)
  Step 2. STF 분석 (각 그룹 독립항들 간 공통/대응 STF 공유 여부)
  Step 3. 전략 확정 (삭제/주장/보정 방향 결정)

[has_citations=True — 인용발명 있음]
  Step 1. 단일성 위반 내용 + 인용발명 파악
  Step 2. 인용발명 대비 STF 분석 (각 그룹 독립항들 간, 인용문헌 원문 발췌, 출처 명시)
  Step 3. 전략 확정 (삭제/주장/보정 방향 결정)

두 흐름 모두 STEPS=3이며, 전략 옵션(A/B/C)도 동일하다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from handlers.base_handler import BaseHandler
from llm_client import LLMClient
from session import Session, RejectionState


class UnityHandler(BaseHandler):
    """단일성 위반(특허법 제45조) 거절이유 처리 핸들러."""

    STEPS = 4

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
        self._claims_en: Optional[str] = None
        self._spec: Optional[str] = None
        self._oa_raw: Optional[str] = None
        self._citation_texts: dict[str, str] = {}

    # ------------------------------------------------------------------
    # BaseHandler 추상 메서드 구현
    # ------------------------------------------------------------------

    def execute_step(self, step: int, feedback: Optional[str] = None) -> str:
        if self.rejection.has_citations:
            dispatch = {
                1: self._step1_with_citations,
                2: self._step2_with_citations,
                3: self._step3_strategy,
                4: self._step4_write_comment,
            }
        else:
            dispatch = {
                1: self._step1_no_citations,
                2: self._step2_no_citations,
                3: self._step3_strategy,
                4: self._step4_write_comment,
            }
        fn = dispatch.get(step)
        if fn is None:
            raise ValueError(f"UnityHandler에 존재하지 않는 단계: {step}")
        return fn(feedback)

    # ------------------------------------------------------------------
    # [has_citations=False] Step 1 — 단일성 위반 내용 파악
    # ------------------------------------------------------------------

    def _step1_no_citations(self, feedback: Optional[str]) -> str:
        claims_en = self._get_claims_en()
        oa_raw = self._get_oa_raw()
        claims_str = ", ".join(str(c) for c in self.rejection.claims)

        prompt = f"""[Step 1: 단일성 위반 내용 파악 (인용발명 없음)]

아래는 의견제출통지서 원문과 영문 청구항입니다.

== 거절 대상 청구항 ==
{claims_str}항

== 의견제출통지서 원문 ==
{oa_raw}

== 영문 청구항 ==
{claims_en}

위 자료를 바탕으로 다음을 수행하라:

1. 심사관이 단일성 없다고 판단한 청구항 그룹을 파악하라.
   - 각 그룹의 청구항 번호와 그룹명(예: 그룹 A, 그룹 B)을 명확히 정리하라.
   - 각 그룹의 발명 카테고리(방법/장치/시스템 등)를 파악하라.

2. 심사관의 단일성 부재 논거를 요약하라.
   - 심사관이 제시한 STF 부재 근거를 원문에서 인용하라.
   - 심사관 논거의 핵심 포인트를 항목별로 정리하라.

3. 각 그룹의 청구항이 영문 청구항에서 어떻게 기재되어 있는지 발췌하라.
   - 독립항을 중심으로 각 그룹의 핵심 구성을 정리하라.

출력 형식: 마크다운, 한국어 (청구항 인용 부분은 영문 원문 그대로)
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("unity")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # [has_citations=False] Step 2 — STF 분석
    # ------------------------------------------------------------------

    def _step2_no_citations(self, feedback: Optional[str]) -> str:
        step1_path = self._step_path(1)
        step1_result = step1_path.read_text(encoding="utf-8") if step1_path.exists() else ""
        claims_en = self._get_claims_en()
        spec = self._get_spec()

        prompt = f"""[Step 2: STF 분석 (인용발명 없음)]

※ 분석 범위: 각 그룹의 독립항만을 대상으로 한다. 종속항은 이 단계에서 분석하지 않는다.

== Step 1 결과 (단일성 위반 내용 파악) ==
{step1_result}

== 영문 청구항 ==
{claims_en}

== 명세서 ==
{spec}

아래 순서대로 분석하라. 각 항목은 간결하게 작성한다.

1. 각 그룹 독립항 전문 나열
   - Step 1에서 파악한 각 그룹의 독립항 전문을 그대로 인용하라.

2. 독립항들 간 공통 구성 추출
   - 각 그룹의 독립항들 간에 문언상 또는 기술적으로 공통되는 구성요소를 항목별로 추출하라.
   - 공통 구성이 없으면 "공통 구성 없음"으로 표시하라.

3. 공통 구성의 STF 해당 여부 판단
   - 추출된 공통 구성이 공지기술(선행기술 일반) 대비 개선된 기술적 특징인지 판단하라.
   - 명세서에서 해당 공통 구성의 기술적 의의를 뒷받침하는 단락을 인용하라.
   - STF 해당: 단일성 주장 가능 / STF 비해당 또는 공통 구성 없음: 단일성 주장 곤란으로 결론 내려라.

4. 단일성 인정 가능성 평가
   - 강함 / 보통 / 약함 중 하나로 평가하고 한 문장으로 이유를 밝혀라.

출력 형식: 마크다운, 번호별 섹션, 간결하게
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("unity")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # [has_citations=True] Step 1 — 단일성 위반 내용 + 인용발명 파악
    # ------------------------------------------------------------------

    def _step1_with_citations(self, feedback: Optional[str]) -> str:
        claims_en = self._get_claims_en()
        oa_raw = self._get_oa_raw()
        citations_block = self._build_citations_block()
        claims_str = ", ".join(str(c) for c in self.rejection.claims)
        citations_list = ", ".join(self.rejection.citations)

        prompt = f"""[Step 1: 단일성 위반 내용 및 인용발명 파악 (인용발명 있음)]

아래는 의견제출통지서 원문, 영문 청구항, 인용문헌입니다.

== 거절 대상 청구항 ==
{claims_str}항

== 의견제출통지서 원문 ==
{oa_raw}

== 영문 청구항 ==
{claims_en}

== 인용문헌 ({citations_list}) ==
{citations_block}

위 자료를 바탕으로 다음을 수행하라:

1. 심사관이 단일성 없다고 판단한 청구항 그룹을 파악하라.
   - 각 그룹의 청구항 번호와 그룹명을 명확히 정리하라.
   - 각 그룹의 발명 카테고리(방법/장치/시스템 등)를 파악하라.

2. 인용문헌({citations_list}) 확인
   - 심사관이 단일성 판단에 사용한 인용문헌의 기술적 내용을 파악하라.
   - 인용문헌에서 심사관이 참조한 핵심 부분을 원문으로 발췌하라.
     ※ 발췌 시 출처(컬럼 번호/단락 번호/페이지)를 반드시 명시하라.
   - 인용문헌이 개시하는 기술의 범위와 한계를 파악하라.

3. 심사관의 STF 부재 논거를 요약하라.
   - 심사관이 각 그룹이 인용발명 대비 개선된 공통 STF를 공유하지 않는다고 판단한 근거를 원문에서 인용하라.
   - 심사관 논거의 핵심 포인트를 항목별로 정리하라.

출력 형식: 마크다운, 한국어 (청구항·인용문헌 인용 부분은 원문 그대로)
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("unity_with_citations")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # [has_citations=True] Step 2 — 인용발명 대비 STF 분석
    # ------------------------------------------------------------------

    def _step2_with_citations(self, feedback: Optional[str]) -> str:
        step1_path = self._step_path(1)
        step1_result = step1_path.read_text(encoding="utf-8") if step1_path.exists() else ""
        claims_en = self._get_claims_en()
        spec = self._get_spec()
        citations_block = self._build_citations_block()
        citations_list = ", ".join(self.rejection.citations)

        prompt = f"""[Step 2: 인용발명 대비 STF 분석 (인용발명 있음)]

※ 분석 범위: 각 그룹의 독립항만을 대상으로 한다. 종속항은 이 단계에서 분석하지 않는다.

== Step 1 결과 (단일성 위반 내용 및 인용발명 파악) ==
{step1_result}

== 영문 청구항 ==
{claims_en}

== 명세서 ==
{spec}

== 인용문헌 ({citations_list}) ==
{citations_block}

아래 순서대로 분석하라. 각 항목은 간결하게 작성한다.

1. 각 그룹 독립항 전문 나열
   - Step 1에서 파악한 각 그룹의 독립항 전문을 그대로 인용하라.

2. 독립항들 간 공통 구성 추출
   - 각 그룹의 독립항들 간에 문언상 또는 기술적으로 공통되는 구성요소를 항목별로 추출하라.
   - 공통 구성이 없으면 "공통 구성 없음"으로 표시하라.

3. 공통 구성과 인용발명({citations_list}) 대비
   - 추출된 공통 구성이 {citations_list}에 개시되어 있는지 확인하라.
   - 인용발명에서 관련 부분을 원문으로 발췌하고 출처(컬럼/단락/페이지)를 명시하라.
   - 공통 구성 중 인용발명에 없는 부분(차이점)을 특정하라.

4. 공통 구성의 STF 해당 여부 판단
   - 인용발명에 없는 공통 구성이 선행기술 대비 개선된 기술적 특징(STF)인지 판단하라.
   - 명세서에서 해당 구성의 기술적 의의를 뒷받침하는 단락을 인용하라.
   - STF 해당: 단일성 주장 가능 / STF 비해당 또는 공통 구성 없음: 단일성 주장 곤란으로 결론 내려라.

5. 단일성 인정 가능성 평가
   - 강함 / 보통 / 약함 중 하나로 평가하고 한 문장으로 이유를 밝혀라.

출력 형식: 마크다운, 번호별 섹션, 간결하게
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("unity_with_citations")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 3 — 전략 확정 (두 흐름 공통)
    # ------------------------------------------------------------------

    def _step3_strategy(self, feedback: Optional[str]) -> str:
        step1_path = self._step_path(1)
        step2_path = self._step_path(2)
        step1_result = step1_path.read_text(encoding="utf-8") if step1_path.exists() else ""
        step2_result = step2_path.read_text(encoding="utf-8") if step2_path.exists() else ""
        claims_str = ", ".join(str(c) for c in self.rejection.claims)
        citations_note = (
            f"인용발명: {', '.join(self.rejection.citations)}"
            if self.rejection.has_citations
            else "인용발명 없음"
        )

        system_prompt_key = (
            "unity_with_citations" if self.rejection.has_citations else "unity"
        )

        prompt = f"""[Step 3: 전략 확정]

== Step 1 결과 ==
{step1_result}

== Step 2 결과 (독립항 간 STF 분석) ==
{step2_result}

== 거절 대상 청구항 ==
{claims_str}항 / {citations_note}

Step 2 분석 결과를 바탕으로 아래 네 가지 전략 옵션 각각을 평가하고, 최종 확정 전략을 제시하라.

A) 일부 그룹 삭제 (Deletion of Claims)
   - 어느 그룹의 청구항을 삭제할지 특정하라.
   - 삭제 시 권리범위 손실과 잔존 청구항의 보호 가치를 평가하라.
   - 삭제된 그룹에 대해 분할출원이 필요한지 여부를 검토하라.
   - 이 옵션의 리스크와 장점을 한 문장씩 정리하라.

B) 보정 없이 단일성 주장 (Assert Unity Without Amendment)
   - Step 2에서 확인된 STF 공유 근거를 활용하여 주장 가능한 논거를 구성하라.
   - 심사관 논거의 약점과 반박 포인트를 항목별로 제시하라.
   - 성공 가능성(강함/보통/약함)과 그 근거를 밝혀라.

C) 독립항 보정 후 단일성 주장 (Amend Independent Claims, Then Argue)
   - 어느 독립항을 어떻게 보정할지 방향을 제시하라.
     · 추가할 한정 사항(공통 구성 강조 또는 차이점 명확화)을 구체적으로 제안하라.
     · 보정 예시 방향(한국어 또는 영문 클레임 언어)을 작성하라.
   - 보정 후 단일성 주장 논거를 간략히 구성하라.
   - 보정으로 인한 권리범위 축소 여부를 평가하라.

D) 분할출원 (Divisional Application)
   - 어느 그룹을 분할출원으로 분리할지 제안하라.
   - 분할 시 유의사항(시기, 원출원과의 권리관계)을 간략히 설명하라.

[최종 확정 전략]
   - 위 옵션 중 실행할 전략을 명확히 하나(또는 조합)로 확정하고 그 이유를 밝혀라.
   - 확정된 전략에 따라 Step 4(영문 코멘트 작성)에서 사용할 핵심 논거·보정 방향을 요약하라.

출력 형식: 마크다운, A/B/C/D 섹션 + 최종 확정 전략
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 전략을 재확정하라]\n{feedback}"

        system = self.llm.load_prompt(system_prompt_key)
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 4 — 영문 코멘트 작성 (두 흐름 공통)
    # ------------------------------------------------------------------

    def _step4_write_comment(self, feedback: Optional[str]) -> str:
        step1_result = self._load_step_result(1)
        step2_result = self._load_step_result(2)
        step3_result = self._load_step_result(3)
        oa_raw = self._get_oa_raw()
        claims_en = self._get_claims_en()
        claims_str = ", ".join(str(c) for c in self.rejection.claims)
        citations_note = (
            f"인용발명: {', '.join(self.rejection.citations)}"
            if self.rejection.has_citations
            else "인용발명 없음"
        )
        citations_block = self._build_citations_block() if self.rejection.has_citations else ""
        sample_text = self._get_sample_reference()

        prior_art_section = ""
        if self.rejection.has_citations:
            prior_art_section = f"""
== 인용문헌 원문 ==
{citations_block}
"""

        prompt = f"""[Step 4: 단일성 위반 영문 코멘트 작성]

아래 자료를 바탕으로 영문 OA 대응 코멘트를 작성하라.
[양식 참고] 섹션의 구조와 문체를 최우선으로 따른다.

== 거절 대상 청구항 ==
{claims_str}항 / {citations_note}

== 심사관 거절이유 원문 ==
{oa_raw}

== 영문 청구항 (claims_en) ==
{claims_en}
{prior_art_section}
== Step 1 결과 (단일성 위반 파악) ==
{step1_result}

== Step 2 결과 (STF 분석) ==
{step2_result}

== Step 3 결과 (대응 전략) ==
{step3_result}

== [양식 참고] 샘플 코멘트 ==
{sample_text}

---

작성 규칙:

【섹션 제목】
"Rejection reason [N]: lack of unity of invention"

【인용발명 목록 (has_citations=True인 경우에만)】
"D1: [문헌번호/명칭]" 형식으로 열거

【심사관 지적사항 개시】
"The examiner alleged that claims [X]-[Y] (hereinafter, invention 1), claims [A]-[B]
 (hereinafter, invention 2), [etc.] do not fall under a group of inventions so linked
 as to form a single general inventive concept."

【한국 특허법 설명 (항상 포함)】
"Under Korean patent law, the requirement of unity of invention is fulfilled when there
 is a technical relationship among the inventions of the claims involving one or more of
 the same or corresponding special technical features. The expression, 'special technical
 features,' means improvements distinctive from the prior art, considered as a whole."

【Step 3 전략에 따라 아래 중 해당하는 전략 작성】

전략 1 — 단순 삭제/분할 (STF 공유 불가한 경우):
  "However, we failed to find any special technical features shared by inventions 1-[N].
   Thus, we suggest deleting claims [X]-[Y] corresponding to invention [N], in order to
   overcome this rejection reason."
  "In this regard, if you would like to delete claims [X]-[Y] as suggested above, please
   let us know whether you want to file a divisional application for the deleted claims."

전략 2 — 보정 후 단일성 주장 (공통 STF 보정으로 확보 가능한 경우):
  "In this regard, we suggest amending independent claims [N] to incorporate the feature
   of '[공통 STF 표현]'."
  "[인용발명이 있으면] [D#] relates to [주제], and discloses the features of [내용].
   However, [D#] does not disclose any feature regarding [차이점]. Thus, we think that
   the feature shared by proposed claims [N] is distinctive from the features disclosed
   in [D#], and proposed claims [N] share the same technical feature."
  "Therefore, if you approve of our suggestion, we will argue these points in an Argument,
   based on amended claims."

언어: 전체 영어. 한국어 일체 사용 금지.
전문 용어: claims_en.docx의 용어를 그대로 사용하라.
출력 형식: 마크다운 (제목은 ## 사용)
"""
        if feedback:
            prompt += f"\n\n[사용자 수정 지시 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system_key = "unity_with_citations" if self.rejection.has_citations else "unity"
        system = self.llm.load_prompt(system_key)
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # 헬퍼 — step 결과 로드 / 샘플 참조
    # ------------------------------------------------------------------

    def _load_step_result(self, step: int) -> str:
        path = self._step_path(step)
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _get_sample_reference(self) -> str:
        samples_dir = self.cases_root.parent / "samples" / "unity"
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

    # ------------------------------------------------------------------
    # 파일 캐시 헬퍼
    # ------------------------------------------------------------------

    def _get_claims_en(self) -> str:
        if self._claims_en is None:
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
        if citation_id not in self._citation_texts:
            text = self.read_citation(citation_id)
            if not text:
                self._print(f"  [경고] 인용문헌 {citation_id} 파일을 찾을 수 없습니다.")
            self._citation_texts[citation_id] = text
        return self._citation_texts[citation_id]

    def _build_citations_block(self) -> str:
        parts = []
        for cit_id in self.rejection.citations:
            text = self._get_citation_text(cit_id)
            parts.append(f"== {cit_id} ==\n{text}")
        return "\n\n".join(parts) if parts else "(인용문헌 없음)"

    def _step_path(self, step: int) -> Path:
        return (
            self.cases_root / self.case_id
            / f"rejection_{self.rejection.id}"
            / f"step_{step}_result.md"
        )
