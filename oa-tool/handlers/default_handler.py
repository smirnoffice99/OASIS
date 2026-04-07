"""
handlers/default_handler.py — 기타 거절이유 Handler (유형 D)

유형 A/B/C에 해당하지 않는 모든 거절이유를 처리한다.

흐름:
  [계획 단계] 거절이유 내용을 보여주고 변리사와 분석 방향 협의
              → LLM이 분석 계획(단계 목록) 초안 제시
              → 변리사 확인/수정 → 계획 확정
  [실행 단계] 확정된 계획에 따라 단계별 분석 실행
              → 각 단계마다 변리사 승인 후 진행
  [전략 단계] 최종 대응 전략 제안 및 확정

특징:
  - STEPS가 고정되지 않음 — 변리사와 협의로 결정
  - handle()을 오버라이드하여 계획 → 실행 흐름 구현
  - 분석 계획은 cases/{case_id}/rejection_{n}/analysis_plan.json에 저장
  - 재개 시 저장된 계획을 복원하여 중단 지점부터 재개
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from handlers.base_handler import BaseHandler, ExitRequested, ReviewRequested
from llm_client import LLMClient
from session import (
    Session,
    RejectionState,
    STATUS_CONCLUDED,
    save_session,
    save_step_result,
    save_conclusion,
    append_dialogue,
)

_PLAN_FILE = "analysis_plan.json"


class DefaultHandler(BaseHandler):
    """기타 거절이유 처리 핸들러 — 변리사 협의 기반 가변 단계."""

    # STEPS는 계획 수립 후 동적으로 설정됨 (기본값 0)
    STEPS: int = 0

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
        self._plan: list[str] = []  # 확정된 분석 단계 목록 (단계 제목 문자열)

    # ------------------------------------------------------------------
    # handle() 오버라이드 — 계획 → 실행 흐름
    # ------------------------------------------------------------------

    def handle(self) -> None:
        """
        기타 거절이유 전체 처리 흐름.

        1. concluded 상태이면 즉시 반환
        2. 기존 계획 파일이 있으면 복원, 없으면 계획 수립
        3. 확정된 계획에 따라 단계별 분석 실행
        4. 전략 단계 실행 후 concluded 처리
        """
        if self.rejection.status == STATUS_CONCLUDED:
            self._print(f"거절이유 #{self.rejection.id}는 이미 완료되었습니다. 건너뜁니다.")
            return

        self.session.start_rejection(self.rejection.id)
        save_session(self.session, self.cases_root)

        self._print_separator()
        self._print(
            f"[거절이유 #{self.rejection.id}] {self._rejection_label()} 처리 시작"
        )

        # 계획 복원 또는 신규 수립
        self._plan = self._load_plan()
        if not self._plan:
            self._plan = self._conduct_planning()
            self._save_plan(self._plan)

        # STEPS를 계획 단계 수 + 전략 단계(1) + 코멘트 단계(1)로 설정
        self.STEPS = len(self._plan) + 2

        self._print(
            f"\n분석 계획: {len(self._plan)}개 분석 단계 + 전략 단계 + 코멘트 단계 = 총 {self.STEPS}단계"
        )

        # 분석 단계 실행 (1 ~ len(plan))
        start_step = max(self.rejection.current_step, 1)
        for step in range(start_step, self.STEPS + 1):
            self._run_step_loop(step)

        # concluded 처리
        self.session.conclude_rejection(self.rejection.id)
        save_session(self.session, self.cases_root)
        self._print(f"\n거절이유 #{self.rejection.id} 처리 완료.")

    # ------------------------------------------------------------------
    # execute_step 구현 — 계획 기반 분배
    # ------------------------------------------------------------------

    def execute_step(self, step: int, feedback: Optional[str] = None) -> str:
        """
        step이 분석 단계(1 ~ len(plan))이면 해당 분석 실행,
        마지막 단계(len(plan)+1)이면 최종 전략 단계 실행.
        """
        if not self._plan:
            self._plan = self._load_plan()

        analysis_step_count = len(self._plan)
        strategy_step = analysis_step_count + 1
        comment_step = analysis_step_count + 2

        if step <= analysis_step_count:
            step_title = self._plan[step - 1]
            return self._execute_analysis_step(step, step_title, feedback)
        elif step == strategy_step:
            return self._execute_strategy_step(feedback)
        elif step == comment_step:
            return self._execute_comment_step(feedback)
        else:
            raise ValueError(
                f"DefaultHandler: 존재하지 않는 단계 {step} "
                f"(계획 단계 수: {analysis_step_count})"
            )

    # ------------------------------------------------------------------
    # 계획 수립 단계
    # ------------------------------------------------------------------

    def _conduct_planning(self) -> list[str]:
        """
        거절이유 내용을 보여주고 변리사와 분석 계획을 협의한다.
        확정된 분석 단계 목록을 반환한다.
        """
        oa_raw = self._get_oa_raw()
        claims_en = self._get_claims_en()

        # 1. 거절이유 내용 출력
        self._print_separator(minor=True)
        self._print("  [기타 거절이유] 거절 내용 및 LLM 분석 계획 초안을 확인합니다.")

        # 2. LLM이 분석 계획 초안 생성
        plan_prompt = f"""아래는 특허청 의견제출통지서의 거절이유 원문과 청구항입니다.

== 거절이유 원문 ==
{oa_raw}

== 영문 청구항 ==
{claims_en}

이 거절이유는 선행기술 위반(유형 A), 기재불비(유형 B), 단일성 위반(유형 C)에 해당하지 않는 기타 거절이유입니다.

다음을 수행하라:

1. 거절이유의 유형과 심사관이 지적한 핵심 내용을 요약하라.

2. 이 거절이유에 대응하기 위해 필요한 분석 단계를 제안하라.
   - 각 단계를 한 줄로 명확하게 기술하라.
   - 3~5개 단계를 권장하나 거절이유의 복잡도에 따라 조정하라.
   - 마지막 단계는 반드시 "대응 전략 제안 및 확정"으로 할 것
     (이 단계는 시스템이 자동으로 추가하므로 목록에서 제외하라)

출력 형식:
## 거절이유 요약
[요약 내용]

## 제안 분석 단계
1. [단계 제목]
2. [단계 제목]
3. [단계 제목]
(필요 시 추가)
"""
        system = self.llm.load_prompt("default")
        plan_draft = self.llm.chat(plan_prompt, system_prompt=system)
        append_dialogue(
            self.case_id, self.rejection.id, "assistant", plan_draft, self.cases_root
        )

        # 3. 계획 초안 출력
        print("\n" + plan_draft)

        # 4. 변리사와 계획 협의 루프
        while True:
            user_input = self._prompt_user(
                "\n분석 계획을 확인하세요.\n"
                "  - 승인: 'Y' 또는 '승인'\n"
                "  - 수정: 수정 내용 직접 입력\n"
                "  - 종료: '종료'\n"
                "> "
            )

            cmd = self._classify_input(user_input)

            if cmd == "approve":
                append_dialogue(
                    self.case_id, self.rejection.id, "user", user_input, self.cases_root
                )
                # LLM 응답에서 단계 목록 파싱
                steps = self._parse_plan_steps(plan_draft)
                if not steps:
                    self._print("  [경고] 단계 목록 파싱 실패. 기본 2단계로 진행합니다.")
                    steps = ["거절이유 분석", "명세서 및 청구항 검토"]
                self._print(f"\n  확정된 분석 계획: {len(steps)}단계")
                for i, s in enumerate(steps, 1):
                    self._print(f"    Step {i}. {s}")
                return steps

            elif cmd == "exit":
                append_dialogue(
                    self.case_id, self.rejection.id, "user", user_input, self.cases_root
                )
                save_session(self.session, self.cases_root)
                raise ExitRequested()

            elif cmd == "review":
                rid = self._parse_review_id(user_input)
                append_dialogue(
                    self.case_id, self.rejection.id, "user", user_input, self.cases_root
                )
                save_session(self.session, self.cases_root)
                raise ReviewRequested(rid)

            else:
                # 피드백 → 계획 재생성
                append_dialogue(
                    self.case_id, self.rejection.id, "user", user_input, self.cases_root
                )
                self._print("피드백을 반영하여 분석 계획을 재생성합니다...")
                revise_prompt = (
                    f"{plan_prompt}\n\n"
                    f"[변리사 피드백 — 아래 내용을 반영하여 계획을 수정하라]\n{user_input}"
                )
                plan_draft = self.llm.chat(revise_prompt, system_prompt=system)
                append_dialogue(
                    self.case_id, self.rejection.id, "assistant", plan_draft, self.cases_root
                )
                print("\n" + plan_draft)

    # ------------------------------------------------------------------
    # 분석 단계 실행
    # ------------------------------------------------------------------

    def _execute_analysis_step(
        self, step: int, step_title: str, feedback: Optional[str]
    ) -> str:
        """계획의 분석 단계 하나를 실행한다."""
        oa_raw = self._get_oa_raw()
        claims_en = self._get_claims_en()
        spec = self._get_spec()

        # 이전 단계 결과 수집 (컨텍스트용)
        prior_results = self._collect_prior_results(step)

        prompt = f"""[Step {step}: {step_title}]

== 거절이유 원문 ==
{oa_raw}

== 영문 청구항 ==
{claims_en}

== 명세서 ==
{spec}
"""
        if prior_results:
            prompt += f"\n== 이전 단계 분석 결과 ==\n{prior_results}\n"

        prompt += f"""
위 자료를 바탕으로 '{step_title}' 분석을 수행하라.

분석 시 유의사항:
- 심사관의 거절 논거를 정확히 파악하고 약점을 찾아라.
- 명세서와 청구항에서 반박 근거를 찾아라.
- 인용문헌이 있다면 출처(컬럼/단락/페이지)를 명시하라.
- 향후 의견서 작성에 바로 활용할 수 있을 정도로 구체적으로 작성하라.

출력 형식: 마크다운, 한국어 (청구항·인용문헌 인용 부분은 원문 그대로)
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("default")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # 전략 단계 실행
    # ------------------------------------------------------------------

    def _execute_strategy_step(self, feedback: Optional[str]) -> str:
        """최종 대응 전략 단계를 실행한다."""
        all_results = self._collect_prior_results(self.STEPS + 1)  # 전체 결과
        claims_str = ", ".join(str(c) for c in self.rejection.claims)

        prompt = f"""[최종 단계: 대응 전략 제안 및 확정]

== 지금까지 분석 결과 ==
{all_results}

== 거절 대상 청구항 ==
{claims_str}항 / 거절 유형: {self.rejection.subtype}

위 분석을 바탕으로 대응 전략을 제안하고 확정하라.

1. 거절이유 극복 가능성 평가
   - 현재 분석 결과를 바탕으로 거절이유를 극복할 수 있는지 평가하라.
   - 강점과 약점을 명확히 정리하라.

2. 권고 대응 전략
   아래 옵션 중 적합한 것을 선택하고 구체적인 실행 방안을 제시하라:
   A) 의견서 제출 — 심사관 논거 반박 논거 구성
   B) 청구항 보정 — 구체적인 보정 방향 제안
   C) 명세서 보정 — 추가해야 할 내용 제안
   D) 복합 대응 (A+B, A+C, 또는 A+B+C)
   E) 기타 (분할출원, 포기 등 특수 상황)

3. 의견서 핵심 주장 초안
   - 선택한 전략의 핵심 주장을 항목별로 정리하라.
   - 향후 영문 코멘트 작성에 활용할 수 있도록 논거를 구체화하라.

출력 형식: 마크다운, 번호별 섹션
"""
        if feedback:
            prompt += f"\n\n[사용자 피드백 — 아래 전략을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("default")
        return self.llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # 코멘트 단계 실행
    # ------------------------------------------------------------------

    def _execute_comment_step(self, feedback: Optional[str]) -> str:
        """최종 영문 코멘트를 작성한다."""
        all_results = self._collect_prior_results(self.STEPS + 1)
        oa_raw = self._get_oa_raw()
        claims_en = self._get_claims_en()
        claims_str = ", ".join(str(c) for c in self.rejection.claims)
        sample_text = self._get_sample_reference()

        prompt = f"""[코멘트 단계: 영문 코멘트 작성]

아래 자료를 바탕으로 영문 OA 대응 코멘트를 작성하라.
[양식 참고] 샘플이 있으면 그 구조와 문체를 최우선으로 따른다.

== 거절 대상 청구항 ==
{claims_str}항 / 거절 유형: {self.rejection.subtype}

== 심사관 거절이유 원문 ==
{oa_raw}

== 영문 청구항 (claims_en) ==
{claims_en}

== 지금까지 분석 및 전략 결과 ==
{all_results}

== [양식 참고] 샘플 코멘트 ==
{sample_text}

---

작성 규칙:
1. 거절이유의 유형에 맞는 섹션 제목 사용
2. 심사관 지적사항을 명확히 개시한 후 반박 또는 대응 방안 제시
3. 전략 단계에서 확정된 대응 방향을 충실히 반영하라
4. 명세서·청구항 인용 시 단락 번호 또는 출처를 반드시 명시하라
5. 결론 문장으로 마무리하라

언어: 전체 영어. 한국어 일체 사용 금지.
전문 용어: claims_en.docx의 용어를 그대로 사용하라.
출력 형식: 마크다운 (제목은 ## 사용)
"""
        if feedback:
            prompt += f"\n\n[사용자 수정 지시 — 아래 내용을 반영하여 재작성하라]\n{feedback}"

        system = self.llm.load_prompt("default")
        return self.llm.chat(prompt, system_prompt=system)

    def _get_sample_reference(self) -> str:
        samples_dir = self.cases_root.parent / "samples" / "other"
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
    # 계획 파일 저장/복원
    # ------------------------------------------------------------------

    def _plan_path(self) -> Path:
        rejection_dir = (
            self.cases_root / self.case_id / f"rejection_{self.rejection.id}"
        )
        rejection_dir.mkdir(parents=True, exist_ok=True)
        return rejection_dir / _PLAN_FILE

    def _save_plan(self, steps: list[str]) -> None:
        path = self._plan_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"steps": steps}, f, ensure_ascii=False, indent=2)

    def _load_plan(self) -> list[str]:
        path = self._plan_path()
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("steps", [])

    # ------------------------------------------------------------------
    # 계획 텍스트 파싱 헬퍼
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_plan_steps(plan_text: str) -> list[str]:
        """
        LLM이 출력한 계획 텍스트에서 단계 목록을 파싱한다.

        인식하는 형식:
          "1. 단계 제목"
          "2. 단계 제목"
          ...
        """
        import re
        steps = []
        for line in plan_text.splitlines():
            m = re.match(r"^\s*\d+\.\s+(.+)$", line.strip())
            if m:
                title = m.group(1).strip()
                # "대응 전략" 단계는 시스템이 자동 추가하므로 제외
                if "대응 전략" not in title and "전략 제안" not in title:
                    steps.append(title)
        return steps

    # ------------------------------------------------------------------
    # 이전 단계 결과 수집 헬퍼
    # ------------------------------------------------------------------

    def _collect_prior_results(self, up_to_step: int) -> str:
        """step 1 ~ (up_to_step - 1)까지의 저장된 결과를 모두 읽어 반환한다."""
        parts = []
        for s in range(1, up_to_step):
            path = (
                self.cases_root / self.case_id
                / f"rejection_{self.rejection.id}"
                / f"step_{s}_result.md"
            )
            if path.exists():
                content = path.read_text(encoding="utf-8")
                title = self._plan[s - 1] if s - 1 < len(self._plan) else f"Step {s}"
                parts.append(f"### Step {s}: {title}\n{content}")
        return "\n\n".join(parts)

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
