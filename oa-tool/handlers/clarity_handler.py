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

    def execute_step(self, step: int, messages: list[dict]) -> str:
        dispatch = {
            1: self._step1_identify_deficiency,
            2: self._step2_analyze_claims_and_spec,
            3: self._step3_response_strategy,
            4: self._step4_write_comment,
        }
        fn = dispatch.get(step)
        if fn is None:
            raise ValueError(f"ClarityHandler에 존재하지 않는 단계: {step}")
        return fn(messages)

    # ------------------------------------------------------------------
    # Step 1 — 불비 유형 파악
    # ------------------------------------------------------------------

    def _step1_identify_deficiency(self, messages: list[dict]) -> str:
        if not messages:
            claims_en = self._get_claims_en()
            oa_raw = self._get_oa_raw()
            spec = self._get_spec()
            claims_str = ", ".join(str(c) for c in self.rejection.claims)

            prompt = f"""[Step 1: 기재불비 유형 파악]

아래는 의견제출통지서 원문, 영문 청구항, 명세서 원문입니다.

== 거절 대상 청구항 ==
{claims_str}항

== 의견제출통지서 원문 ==
{oa_raw}

== 영문 청구항 ==
{claims_en}

== 명세서 원문 ==
{spec}

이 단계에서는 기재불비 유형 파악과 심사관 지적 내용 특정만 수행하라. 타당성 분석 및 전략은 수행하지 않는다.

위 자료를 바탕으로 다음을 수행하라:

1. 심사관이 지적한 각 기재불비에 대해 기재불비의 유형을 아래 중 하나로 분류하라.
   - 청구항 불명확 (특허법 제42조 4항 2호): 용어가 모호하거나 보호범위가 불명확
   - 발명의 설명 미뒷받침 (특허법 제42조 4항 1호): 명세서에 청구항 근거 없음
   - 실시가능 요건 미충족 (특허법 제42조 3항): 통상의 기술자가 실시 불가
   - 청구항 기재요건 위배 (제42조 제8항): 한국법상 청구항 기재요건에 부합하지 않음

2. 심사관이 지적한 기재불비의 내용을 명확히 파악하여 특정하라.
   - OA 파싱 결과 "거절이유 목록"에 복수의 기재불비 항목들이 있는 경우, 현재 분석중인 항목에 해당되는 기재불비 지적사항들만 서술하라
   - 심사관이 지적한 기재불비 사항이 무엇인지 핵심만 명확히 서술하라
   - 문제가 된 용어 및/또는 구성을 명확히 서술하라
   - 심사관의 논거를 요약하여 명확히 서술하라

출력 형식: 마크다운, 한국어 (청구항 인용 부분은 영문 원문 그대로)
"""
            messages.append({"role": "user", "content": prompt})

        system = self.llm.load_prompt("clarity")
        return self.llm.chat_messages(messages, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 2 — 심사관 지적의 타당성 분석
    # ------------------------------------------------------------------

    def _step2_analyze_claims_and_spec(self, messages: list[dict]) -> str:
        if not messages:
            step1_path = (
                self.cases_root / self.case_id
                / f"rejection_{self.rejection.id}"
                / "step_1_result.md"
            )
            step1_result = step1_path.read_text(encoding="utf-8") if step1_path.exists() else ""
            claims_en = self._get_claims_en()
            spec = self._get_spec()
            claims_str = ", ".join(str(c) for c in self.rejection.claims)

            prompt = f"""[Step 2: 심사관 지적 타당성]

== 분석 대상 청구항 ==
{claims_str}항

== Step 1 결과 (불비 유형 파악) ==
{step1_result}

== 영문 청구항 ==
{claims_en}

== 명세서 원문 ==
{spec}

이 단계에서는 심사관 지적의 타당성 분석만 수행하라. 전략 제안, 보정안, 의견서 초안은 작성하지 않는다.
분석은 위 "분석 대상 청구항"({claims_str}항)에 한정하라.

위 자료를 바탕으로 다음을 수행하라:

1. 심사관의 지적이 타당한지 여부를 평가하라.
   - 심사관이 지적한 거절이유 각각에 대해 심사관의 지적이 타당한지 여부를 검토하라.
   - 기재불비의 유형을 고려하여 분석하라.
   - 심사관의 지적이 타당한지 여부 및 그 근거를 핵심만 명확하게 서술하라.
   - 필요한 경우에 한하여 명세서에 개시된 내용들을 참조하여 분석 및 서술하라.

2. 이 단계에서는 영문 코멘트 작성을 위한 전략은 수립하지 않는다.

3. 각 논거는 향후 의견서에 바로 활용할 수 있을 정도로 명확하게 작성하라.

출력 형식: 마크다운, 번호별 섹션
"""
            messages.append({"role": "user", "content": prompt})

        system = self.llm.load_prompt("clarity")
        return self.llm.chat_messages(messages, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 3 — 전략 선택
    # ------------------------------------------------------------------

    def _step3_response_strategy(self, messages: list[dict]) -> str:
        if not messages:
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

            prompt = f"""[Step 3: 전략 선택]

== Step 1 결과 (불비 유형 파악) ==
{step1_result}

== Step 2 결과 (심사관 지적 타당성) ==
{step2_result}

== 거절 대상 청구항 ==
{claims_str}항 / 거절 유형: {self.rejection.subtype}

이 단계에서는 대응 전략 선택만 수행하라. 영문 코멘트 초안은 작성하지 않는다.
전략 검토는 위 "거절 대상 청구항"({claims_str}항)에 한정하라.

위 분석을 바탕으로 두 가지 대응 전략을 평가하고, 고려할만한 전략들만을 선택적으로 제안하고, 권고안을 제시하라.

A) 의견서 전략 (Written Opinion)
   - 기재불비가 지적된 부분의 기재가 명확함을 설명하는 논거를 구성하라.
   - 필요한 경우, Step 2에서 도출된 논거를 활용하여 의견서 핵심 주장을 구성하라.
   - 필요한 경우, 명세서의 근거 부분 및 단락 번호를 인용하라.
   - 필요한 경우, 심사관 논거의 약점을 고려하라.
   - 통상의 기술자의 관점에서 근거를 구성하라.

B) 보정 + 의견서 병행 전략
   - 청구항을 어떻게 보정할지 구체적으로 제안하라.
   - 예) "제1 측위 기준값" → "RSSI, RTT, AoA의 가중 평균으로 산출되는 제1 측위 기준값"
   - 보정 예시 문구(한국어 + 영문)를 함께 제시하라.
   - B)의 보정안을 기준으로 기재가 명확함을 설명하는 논거를 구성하라.
   - 필요한 경우, 명세서의 근거 부분 및 단락 번호를 인용하라.
   - 통상의 기술자의 관점에서 근거를 구성하라.

[권고안]
   - 위 전략 중 가장 권고하는 방향과 그 이유를 명확히 제시하라.
   - 의견서만으로 극복 가능한지, 보정이 불가피한지 평가하라.

[피드백 처리 규칙]
변리사가 피드백으로 특정 전략을 선택하거나 수정 지시를 입력하면:
- 선택된 전략만을 기준으로 응답하라. 이전 분석에서 다른 전략을 권고했거나 원래 프롬프트에 다른 전략이 기술되어 있더라도, 변리사의 선택이 절대적으로 우선한다.
- 선택되지 않은 전략은 언급하거나 재분석하지 마라.
- 보정안 제안 요청이 포함된 경우, 요청된 청구항에 대한 구체적인 보정안을 제시하라.

출력 형식: 마크다운, A/B 섹션 + 권고안
"""
            messages.append({"role": "user", "content": prompt})

        system = self.llm.load_prompt("clarity")
        return self.llm.chat_messages(messages, system_prompt=system)

    # ------------------------------------------------------------------
    # Step 4 — 영문 코멘트 작성
    # ------------------------------------------------------------------

    def _step4_write_comment(self, messages: list[dict]) -> str:
        if not messages:
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
- Step 1~3에서 분석한 기재불비 사항에 한정하여 작성한다. OA 원문에 다른 청구항이나 다른 기재불비 지적이 있더라도, Step 1~3에서 분석하지 않은 내용은 포함하지 않는다.
- 샘플 포맷을 최우선으로 따른다. 샘플과 동등한 길이로 작성한다.
- 불필요한 설명, 반복, 법조문 인용을 최소화한다.
- 명세서 인용 시 단락 번호([XXXX])를 명시하고 핵심 문장만 발췌한다.
- 전문 용어는 claims_en의 표현을 그대로 사용한다.
- 언어: 전체 영어. 한국어 사용 금지.
"""
            messages.append({"role": "user", "content": prompt})

        system = self.llm.load_prompt("clarity")
        return self.llm.chat_messages(messages, system_prompt=system)

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
            if self.rejection.raw_text:
                self._oa_raw = self.rejection.raw_text
            else:
                self._oa_raw = (
                    self.read_case_file("oa.pdf")
                    or self.read_case_file("oa_mock.txt")
                )
        return self._oa_raw
