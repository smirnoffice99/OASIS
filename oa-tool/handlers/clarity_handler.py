"""
handlers/clarity_handler.py — 기재불비 Handler (유형 B)

분석 흐름:
  Step 1. 불비 유형 파악
          - 심사관이 지적한 불비 유형 분류: 청구항 불명확 / 발명의 설명 미뒷받침 / 실시가능 요건
          - 지적 내용과 대상 청구항 파악
  Step 2. 해당 청구항 + 명세서 대응 부분 분석
          - 심사관 지적 부분과 명세서 원문 대조
          - 명세서에 뒷받침 근거 존재 여부 확인 (단락 번호 명시)
  Step 3. 대응 전략 제안 및 확정
          A) 청구항 보정으로 명확화
          B) 의견서로 용어 해석 제시
          C) 명세서 보정 (실시예 추가 등)
          D) 보정 + 의견서 병행

핵심 규칙:
  - 인용발명 없음 — 구성요소 대비 및 차이점 분석 불필요
  - 명세서 내부 분석만 수행
  - 뒷받침 근거 인용 시 단락 번호([XXXX]) 또는 페이지/섹션 명시
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from handlers.base_handler import BaseHandler
from llm_client import LLMClient
from session import Session, RejectionState


class ClarityHandler(BaseHandler):
    """기재불비(특허법 제42조) 거절이유 처리 핸들러."""

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

    # ------------------------------------------------------------------
    # BaseHandler 추상 메서드 구현
    # ------------------------------------------------------------------

    def execute_step(self, step: int, feedback: Optional[str] = None) -> str:
        dispatch = {
            1: self._step1_identify_deficiency,
            2: self._step2_analyze_claims_and_spec,
            3: self._step3_response_strategy,
            4: self._step4_write_comment,
        }
        fn = dispatch.get(step)
        if fn is None:
            raise ValueError(f"ClarityHandler에 존재하지 않는 단계: {step}")
        return fn(feedback)

    # ------------------------------------------------------------------
    # Step 1 — 불비 유형 파악
    # ------------------------------------------------------------------

    def _step1_identify_deficiency(self, feedback: Optional[str]) -> str:
        claims_en = self._get_claims_en()
        oa_raw = self._get_oa_raw()
        claims_str = ", ".join(str(c) for c in self.rejection.claims)

        prompt = f"""[Step 1: 기재불비 유형 파악]

아래는 의견제출통지서 원문과 영문 청구항입니다.

== 거절 대상 청구항 ==
{claims_str}항

== 의견제출통지서 원문 ==
{oa_raw}

== 영문 청구항 ==
{claims_en}

위 자료를 바탕으로 다음을 수행하라:

1. 심사관이 지적한 기재불비의 유형을 아래 중 해당하는 것으로 분류하라.
   - 청구항 불명확 (특허법 제42조 4항 2호): 용어가 모호하거나 보호범위가 불명확
   - 발명의 설명 미뒷받침 (특허법 제42조 4항 1호): 명세서에 청구항 근거 없음
   - 실시가능 요건 미충족 (특허법 제42조 3항): 통상의 기술자가 실시 불가
   - 복수의 유형에 해당하는 경우 모두 나열

2. 심사관이 구체적으로 지적한 내용을 인용하라.
   - 문제가 된 용어 또는 구성을 명확히 특정하라.
   - 심사관의 논거를 요약하라.

3. 대상 청구항({claims_str}항)에서 지적받은 표현을 영문 원문으로 발췌하라.

출력 형식: 마크다운, 한국어 (청구항 인용 부분은 영문 원문 그대로)
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("clarity")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 2 — 청구항 + 명세서 대응 부분 분석
    # ------------------------------------------------------------------

    def _step2_analyze_claims_and_spec(self, feedback: Optional[str]) -> str:
        step1_path = (
            self.cases_root / self.case_id
            / f"rejection_{self.rejection.id}"
            / "step_1_result.md"
        )
        step1_result = step1_path.read_text(encoding="utf-8") if step1_path.exists() else ""
        claims_en = self._get_claims_en()
        spec = self._get_spec()
        claims_str = ", ".join(str(c) for c in self.rejection.claims)

        prompt = f"""[Step 2: 청구항 + 명세서 대응 부분 분석]

== Step 1 결과 (불비 유형 파악) ==
{step1_result}

== 영문 청구항 ==
{claims_en}

== 명세서 원문 ==
{spec}

위 자료를 바탕으로 다음을 수행하라:

1. 심사관이 지적한 문제 부분과 명세서 원문을 대조하라.
   - 지적받은 용어 또는 구성이 명세서의 어느 단락에서 정의 또는 설명되는지 확인하라.
   - 해당 단락의 원문을 발췌하고 단락 번호([XXXX]) 또는 섹션을 명시하라.

2. 명세서에 뒷받침 근거가 충분한지 평가하라.
   - 뒷받침 있음: 어느 단락에서 어떻게 뒷받침되는지 구체적으로 기술
   - 뒷받침 불충분: 어떤 내용이 추가되어야 하는지 제안
   - 뒷받침 없음: 청구항 보정 또는 삭제 필요성 평가

3. 청구항({claims_str}항)의 용어가 명세서 전체에서 일관되게 사용되고 있는지 확인하라.
   - 동일 개념에 복수의 용어가 혼용되는 경우 모두 나열하라.
   - 혼용이 있는 경우 어느 용어가 가장 적합한지 의견을 제시하라.

4. 통상의 기술자 관점에서 해당 청구항을 이해하고 실시할 수 있는지 평가하라.

출력 형식: 마크다운, 번호별 섹션
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("clarity")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 3 — 대응 전략 제안 및 확정
    # ------------------------------------------------------------------

    def _step3_response_strategy(self, feedback: Optional[str]) -> str:
        step1_path = (
            self.cases_root / self.case_id
            / f"rejection_{self.rejection.id}"
            / "step_1_result.md"
        )
        step2_path = (
            self.cases_root / self.case_id
            / f"rejection_{self.rejection.id}"
            / "step_2_result.md"
        )
        step1_result = step1_path.read_text(encoding="utf-8") if step1_path.exists() else ""
        step2_result = step2_path.read_text(encoding="utf-8") if step2_path.exists() else ""
        claims_str = ", ".join(str(c) for c in self.rejection.claims)

        prompt = f"""[Step 3: 기재불비 대응 전략 제안 및 확정]

== Step 1 결과 (불비 유형 파악) ==
{step1_result}

== Step 2 결과 (청구항·명세서 분석) ==
{step2_result}

== 거절 대상 청구항 ==
{claims_str}항 / 거절 유형: {self.rejection.subtype}

위 분석을 바탕으로 네 가지 대응 전략을 평가하고 권고안을 제시하라.

A) 청구항 보정으로 명확화 (Amendment for Clarity)
   - 어느 용어를 어떻게 보정할지 구체적으로 제안하라.
   - 예) "제1 측위 기준값" → "RSSI, RTT, AoA의 가중 평균으로 산출되는 제1 측위 기준값"
   - 보정 후 청구항 권리범위의 변화(확장/축소)를 평가하라.
   - 보정 예시 문구(한국어 + 영문)를 함께 제시하라.

B) 의견서로 용어 해석 제시 (Written Opinion with Claim Interpretation)
   - 지적받은 용어의 기술적 의미를 명세서 근거와 함께 설명하는 논거를 구성하라.
   - 통상의 기술자가 해당 용어를 이해할 수 있다는 근거를 제시하라.
   - 명세서 근거 단락 번호를 인용하라.

C) 명세서 보정 (Specification Amendment)
   - 미뒷받침 또는 불명확한 부분에 대해 실시예 추가, 용어 정의 삽입 등을 제안하라.
   - 추가할 내용의 초안(한국어)을 제시하라.
   - 해당하는 경우에만 이 옵션을 제안하라.

D) 보정 + 의견서 병행 (Combined Strategy)
   - A 또는 C의 보정과 B의 의견서를 결합한 최적 시나리오를 기술하라.

[권고안]
   - 위 전략 중 가장 권고하는 방향과 그 이유를 명확히 제시하라.
   - 명세서 뒷받침 강도에 따라 의견서만으로 극복 가능한지, 보정이 불가피한지 평가하라.
   - 리스크와 기대 성공 가능성을 함께 평가하라.

출력 형식: 마크다운, A/B/C/D 섹션 + 권고안
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 전략을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("clarity")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 4 — 영문 코멘트 작성
    # ------------------------------------------------------------------

    def _step4_write_comment(self, feedback: Optional[str]) -> str:
        step1_result = self._load_step_result(1)
        step2_result = self._load_step_result(2)
        step3_result = self._load_step_result(3)
        oa_raw = self._get_oa_raw()
        claims_en = self._get_claims_en()
        spec = self._get_spec()
        claims_str = ", ".join(str(c) for c in self.rejection.claims)
        sample_text = self._get_sample_reference()

        prompt = f"""[Step 4: 기재불비 영문 코멘트 작성]

== [최우선 참조] 샘플 코멘트 ==
{sample_text}

위 샘플의 구조, 길이, 문체를 그대로 따라 작성하라.
샘플에 없는 섹션을 추가하거나, 샘플보다 길게 쓰지 마라.

---

== 거절 대상 청구항 ==
{claims_str}항 / {self.rejection.subtype}

== 심사관 거절이유 원문 ==
{oa_raw}

== 영문 청구항 ==
{claims_en}

== 명세서 원문 ==
{spec}

== Step 1 결과 (불비 유형 파악) ==
{step1_result}

== Step 2 결과 (청구항·명세서 분석) ==
{step2_result}

== Step 3 결과 (대응 전략) ==
{step3_result}

---

작성 지침:
- 샘플 포맷을 최우선으로 따른다. 샘플과 동등한 길이로 작성한다.
- 불필요한 설명, 반복, 법조문 인용을 최소화한다.
- 명세서 인용 시 단락 번호([XXXX])를 명시하고 핵심 문장만 발췌한다.
- 전문 용어는 claims_en의 표현을 그대로 사용한다.
- 언어: 전체 영어. 한국어 사용 금지.
"""
        if feedback:
            prompt += f"\n\n[사용자 수정 지시 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("clarity")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # 헬퍼 — step 결과 로드 / 샘플 참조
    # ------------------------------------------------------------------

    def _load_step_result(self, step: int) -> str:
        path = (
            self.cases_root / self.case_id
            / f"rejection_{self.rejection.id}"
            / f"step_{step}_result.md"
        )
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _get_sample_reference(self) -> str:
        """최근 수정 순으로 최대 3개 샘플을 결합하여 반환한다."""
        samples_dir = self.cases_root.parent / "samples" / "clarity"
        if not samples_dir.exists():
            return "(샘플 없음)"

        candidates = sorted(
            [p for p in samples_dir.iterdir() if p.suffix in (".docx", ".txt")],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:3]

        parts = []
        for i, sample_path in enumerate(candidates, 1):
            try:
                if sample_path.suffix == ".docx":
                    text = self._read_docx(sample_path)
                else:
                    text = sample_path.read_text(encoding="utf-8")
                parts.append(f"--- 샘플 {i}: {sample_path.name} ---\n{text}")
            except Exception:
                continue

        return "\n\n".join(parts) if parts else "(샘플 없음)"

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
