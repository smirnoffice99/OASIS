"""
handlers/base_handler.py — 공통 상호작용 루프

모든 유형별 Handler가 상속하는 기반 클래스.

책임:
  - 단계별 LLM 호출 → 터미널 출력 → 사용자 입력 처리 루프
  - 결과 파일 저장 (step_N_result.md, dialogue.json, conclusion.md)
  - 특수 명령 처리: Y/승인, 종료, 재검토 N, 승인취소

사용법:
  서브클래스에서 STEPS와 execute_step()을 구현하고,
  handle() 를 호출하면 전체 흐름이 진행된다.
"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from llm_client import LLMClient
from session import (
    Session,
    RejectionState,
    STATUS_IN_PROGRESS,
    STATUS_CONCLUDED,
    save_session,
    save_step_result,
    save_conclusion,
    append_dialogue,
)


# ---------------------------------------------------------------------------
# 특수 명령 상수
# ---------------------------------------------------------------------------

CMD_APPROVE = ("y", "승인")
CMD_EXIT = "종료"
CMD_REVIEW_PREFIX = "재검토"
CMD_CANCEL = "승인취소"


# ---------------------------------------------------------------------------
# 예외 — 종료 신호
# ---------------------------------------------------------------------------

class ExitRequested(Exception):
    """사용자가 '종료' 명령을 입력했을 때 발생하는 신호."""


class ReviewRequested(Exception):
    """사용자가 '재검토 N' 명령을 입력했을 때 발생하는 신호."""

    def __init__(self, rejection_id: int):
        super().__init__(f"재검토 요청: 거절이유 #{rejection_id}")
        self.rejection_id = rejection_id


class StepCancelRequested(Exception):
    """사용자가 '승인취소' 명령을 입력했을 때 발생하는 신호.

    현재 단계에서 이전 단계의 승인을 취소하고 그 단계로 돌아간다.
    """


# ---------------------------------------------------------------------------
# 기반 Handler
# ---------------------------------------------------------------------------

class BaseHandler(ABC):
    """
    모든 유형별 Handler의 공통 기반 클래스.

    서브클래스 구현 요구사항:
      - STEPS: int  — 총 단계 수 (마지막 단계가 전략 확정 단계)
      - execute_step(step, feedback) -> str
            LLM을 호출하여 해당 step의 분석 결과를 반환한다.
            feedback이 None이면 최초 생성, 문자열이면 피드백 반영 재생성.
    """

    STEPS: int = 0  # 서브클래스에서 오버라이드

    def __init__(
        self,
        case_id: str,
        rejection: RejectionState,
        session: Session,
        llm_client: LLMClient,
        cases_root: Path,
    ):
        self.case_id = case_id
        self.rejection = rejection
        self.session = session
        self.llm = llm_client
        self.cases_root = Path(cases_root)
        self.case_dir = self.cases_root / case_id

    # ------------------------------------------------------------------
    # 추상 메서드 — 서브클래스에서 구현
    # ------------------------------------------------------------------

    @abstractmethod
    def execute_step(self, step: int, feedback: Optional[str] = None) -> str:
        """
        step 번호에 해당하는 분석을 수행하고 결과 텍스트를 반환한다.

        Args:
            step:     현재 단계 번호 (1-based)
            feedback: 사용자 피드백 (None이면 최초 생성)

        Returns:
            분석 결과 마크다운 문자열
        """

    # ------------------------------------------------------------------
    # 공개 진입점
    # ------------------------------------------------------------------

    def handle(self) -> None:
        """
        거절이유 하나를 처음부터 끝까지 처리한다.

        - 세션의 current_step에서 재개한다.
        - concluded 상태이면 즉시 반환한다.
        - ExitRequested / ReviewRequested 예외를 상위로 전파한다.
        - '승인취소' 시 StepCancelRequested를 잡아 이전 단계로 돌아간다.
        """
        if self.rejection.status == STATUS_CONCLUDED:
            self._print(f"거절이유 #{self.rejection.id}는 이미 완료되었습니다. 건너뜁니다.")
            return

        # 세션 시작 표시
        self.session.start_rejection(self.rejection.id)
        save_session(self.session, self.cases_root)

        step = max(self.rejection.current_step, 1)
        self._print_separator()
        self._print(
            f"[거절이유 #{self.rejection.id}] {self._rejection_label()} 처리 시작 "
            f"(Step {step} / {self.STEPS})"
        )

        while step <= self.STEPS:
            try:
                self._run_step_loop(step)
                step += 1
            except StepCancelRequested:
                # 이전 단계 승인 취소 — step은 현재 실행 중이던 단계
                # 한 단계 앞으로 돌아간다 (step - 1이 취소 대상)
                cancelled_step = step - 1
                self._delete_step_result(step)   # 현재 단계의 미완성 결과 삭제
                step = cancelled_step
                self._update_session_step(step)
                self._print(
                    f"\n  Step {cancelled_step} 승인이 취소되었습니다. "
                    f"Step {cancelled_step}으로 돌아갑니다."
                )

        # 모든 단계 완료 → concluded
        self.session.conclude_rejection(self.rejection.id)
        save_session(self.session, self.cases_root)
        self._print(f"\n거절이유 #{self.rejection.id} 처리 완료.")

    # ------------------------------------------------------------------
    # 단계별 루프
    # ------------------------------------------------------------------

    def _run_step_loop(self, step: int) -> None:
        """
        단일 step에 대해 [생성 → 출력 → 사용자 입력] 루프를 돈다.
        승인 시 반환, 승인취소 시 StepCancelRequested 발생.
        """
        self._print_separator(minor=True)
        self._print(f"  Step {step} / {self.STEPS} 분석 중...")

        feedback: Optional[str] = None
        is_final_step = (step == self.STEPS)

        while True:
            # LLM 호출
            result = self.execute_step(step, feedback)

            # 파일 저장
            saved_path = save_step_result(
                self.case_id, self.rejection.id, step, result, self.cases_root
            )
            append_dialogue(
                self.case_id, self.rejection.id, "assistant", result, self.cases_root
            )

            # 터미널 출력
            self._print(f"\n--- Step {step} 결과 (저장: {saved_path}) ---")
            print(result)

            # 마지막 단계(전략)는 결론 확정까지 계속
            if is_final_step:
                cancel_hint = "" if step == 1 else "/'승인취소'"
                user_input = self._prompt_user(
                    f"\n[전략 확정] 수정 요청 또는 '승인'/'Y'로 결론 확정"
                    f"{cancel_hint}: "
                )
                cmd = self._classify_input(user_input)

                if cmd == "approve":
                    # 결론 저장
                    save_conclusion(
                        self.case_id, self.rejection.id, result, self.cases_root
                    )
                    append_dialogue(
                        self.case_id, self.rejection.id, "user", user_input, self.cases_root
                    )
                    self._update_session_step(step + 1)
                    return

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

                elif cmd == "cancel":
                    if step == 1:
                        self._print("  첫 번째 단계는 이전 단계 승인 취소가 불가합니다.")
                    else:
                        append_dialogue(
                            self.case_id, self.rejection.id, "user", user_input, self.cases_root
                        )
                        save_session(self.session, self.cases_root)
                        raise StepCancelRequested()

                else:
                    # 피드백 → 재생성
                    feedback = user_input
                    append_dialogue(
                        self.case_id, self.rejection.id, "user", user_input, self.cases_root
                    )
                    self._print("피드백을 반영하여 재생성합니다...")

            else:
                # 중간 단계 — 승인 시 다음 단계
                cancel_hint = "" if step == 1 else "/'승인취소'"
                user_input = self._prompt_user(
                    f"\n승인하려면 'Y' 또는 '승인', 수정 요청은 내용 입력, "
                    f"'종료'/'재검토 N'{cancel_hint}: "
                )
                cmd = self._classify_input(user_input)

                if cmd == "approve":
                    append_dialogue(
                        self.case_id, self.rejection.id, "user", user_input, self.cases_root
                    )
                    self._update_session_step(step + 1)
                    return

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

                elif cmd == "cancel":
                    if step == 1:
                        self._print("  첫 번째 단계는 이전 단계 승인 취소가 불가합니다.")
                    else:
                        append_dialogue(
                            self.case_id, self.rejection.id, "user", user_input, self.cases_root
                        )
                        save_session(self.session, self.cases_root)
                        raise StepCancelRequested()

                else:
                    # 피드백 → 현재 step 재생성
                    feedback = user_input
                    append_dialogue(
                        self.case_id, self.rejection.id, "user", user_input, self.cases_root
                    )
                    self._print("피드백을 반영하여 재생성합니다...")

    # ------------------------------------------------------------------
    # 입력 분류 헬퍼
    # ------------------------------------------------------------------

    def _classify_input(self, text: str) -> str:
        """
        사용자 입력을 명령 코드로 분류한다.

        Returns:
            "approve" | "exit" | "review" | "cancel" | "feedback"
        """
        stripped = text.strip()
        lower = stripped.lower()

        if lower in CMD_APPROVE:
            return "approve"
        if stripped == CMD_EXIT:
            return "exit"
        if stripped.startswith(CMD_REVIEW_PREFIX):
            return "review"
        if stripped == CMD_CANCEL:
            return "cancel"
        return "feedback"

    def _parse_review_id(self, text: str) -> int:
        """
        '재검토 N' 에서 N을 파싱한다.
        숫자가 없으면 ValueError를 발생시킨다.
        """
        parts = text.strip().split()
        if len(parts) >= 2 and parts[1].isdigit():
            return int(parts[1])
        raise ValueError(f"재검토 명령에서 번호를 파싱할 수 없습니다: {text!r}")

    # ------------------------------------------------------------------
    # 세션 갱신 헬퍼
    # ------------------------------------------------------------------

    def _update_session_step(self, step: int) -> None:
        self.session.advance_step(self.rejection.id, step)
        save_session(self.session, self.cases_root)

    def _delete_step_result(self, step: int) -> None:
        """step 결과 파일이 존재하면 삭제한다 (승인취소 시 stale 파일 정리)."""
        path = (
            self.cases_root
            / self.case_id
            / f"rejection_{self.rejection.id}"
            / f"step_{step}_result.md"
        )
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 파일 읽기 헬퍼 — 서브클래스에서 사용
    # ------------------------------------------------------------------

    def read_case_file(self, filename: str) -> str:
        """
        cases/{case_id}/{filename} 을 읽어 텍스트로 반환한다.
        PDF는 PyMuPDF로, docx는 python-docx로 추출한다.
        파일이 없으면 빈 문자열을 반환한다.
        """
        path = self.case_dir / filename
        if not path.exists():
            return ""
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return self._read_pdf(path)
        elif suffix == ".docx":
            return self._read_docx(path)
        else:
            return path.read_text(encoding="utf-8")

    def read_citation(self, citation_name: str) -> str:
        """
        cases/{case_id}/citations/{citation_name} 파일을 읽어 반환한다.
        확장자 없이 이름만 전달하면 .pdf → .txt → _mock.txt 순으로 시도한다.
        """
        citations_dir = self.case_dir / "citations"
        candidates = [
            f"{citation_name}",
            f"{citation_name}.pdf",
            f"{citation_name}.txt",
            f"{citation_name}_mock.txt",
            f"{citation_name}_mock.pdf",
        ]
        for name in candidates:
            path = citations_dir / name
            if path.exists():
                return self.read_case_file(f"citations/{path.name}")
        return ""

    def _read_pdf(self, path: Path) -> str:
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("pymupdf 패키지가 필요합니다: pip install pymupdf")

        # OCR 캐시 파일: {파일명}_ocr.txt (같은 폴더)
        cache_path = path.parent / f"{path.stem}_ocr.txt"
        if cache_path.exists():
            print(f"[정보] OCR 캐시 사용: {cache_path.name}")
            return cache_path.read_text(encoding="utf-8")

        doc = fitz.open(str(path))
        total = len(doc)
        texts = []
        ocr_applied = False
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                texts.append(text)
            else:
                print(f"[OCR] {path.name} 페이지 {i + 1}/{total} 처리 중...", flush=True)
                texts.append(self._ocr_page_with_llm(page, path.name))
                ocr_applied = True
        doc.close()

        result = "\n".join(texts)
        if ocr_applied:
            print(f"[정보] {path.name} OCR 완료. 캐시 저장: {cache_path.name}")
            try:
                cache_path.write_text(result, encoding="utf-8")
            except Exception as e:
                print(f"[경고] OCR 캐시 저장 실패: {e}")

        return result

    def _ocr_page_with_llm(self, page, filename: str = "") -> str:
        """이미지 기반 PDF 페이지를 LLM Vision으로 텍스트 추출한다."""
        try:
            pixmap = page.get_pixmap(dpi=150)
            return self.llm.ocr_image(pixmap.tobytes("png"))
        except Exception as e:
            print(f"[경고] LLM OCR 실패 ({filename}): {e}")
            return ""

    @staticmethod
    def _read_docx(path: Path) -> str:
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx 패키지가 필요합니다: pip install python-docx")
        doc = Document(str(path))
        return "\n".join(para.text for para in doc.paragraphs)

    # ------------------------------------------------------------------
    # 표시 헬퍼
    # ------------------------------------------------------------------

    def _rejection_label(self) -> str:
        type_labels = {
            "prior_art": "선행기술 위반",
            "clarity": "기재불비",
            "unity": "단일성 위반",
            "other": "기타",
        }
        label = type_labels.get(self.rejection.type, self.rejection.type)
        if self.rejection.subtype:
            label = f"{label} ({self.rejection.subtype})"
        return label

    def _print(self, message: str) -> None:
        print(message, flush=True)

    def _print_separator(self, minor: bool = False) -> None:
        if minor:
            print("  " + "-" * 60, flush=True)
        else:
            print("\n" + "=" * 70, flush=True)

    # 세션 내 입력창 높이 상태 (Ctrl+↑/↓ 로 조절, 1~20줄)
    _input_height: int = 3

    def _prompt_user(self, prompt: str) -> str:
        """
        사용자 입력을 받는다.

        prompt_toolkit이 설치되어 있으면 크기 조절 가능한 멀티라인 입력창을 사용한다.
          - Enter        : 제출
          - Alt+Enter    : 줄바꿈 (긴 피드백 작성 시)
          - Ctrl+Shift+↑ : 입력창 1줄 확대 (VSCode 터미널 권장)
          - Ctrl+Shift+↓ : 입력창 1줄 축소 (Ctrl+↑/↓ 도 동작)
        미설치 시 기본 input()으로 폴백한다.
        """
        try:
            return self._prompt_resizable(prompt)
        except ImportError:
            pass
        except KeyboardInterrupt:
            raise
        except Exception:
            pass
        # 폴백
        try:
            return input(prompt).strip()
        except EOFError:
            return CMD_EXIT

    def _prompt_resizable(self, prompt_text: str) -> str:
        """prompt_toolkit 기반 크기 조절 가능 입력창."""
        from prompt_toolkit import Application
        from prompt_toolkit.buffer import Buffer
        from prompt_toolkit.formatted_text import HTML
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.layout import Layout, HSplit, Window
        from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
        from prompt_toolkit.layout.dimension import Dimension as D
        from prompt_toolkit.styles import Style

        buf = Buffer(multiline=True)

        def get_height() -> D:
            # D.exact() 로 내용이 적어도 지정한 높이를 항상 유지
            return D.exact(BaseHandler._input_height)

        def get_toolbar() -> HTML:
            h = BaseHandler._input_height
            return HTML(
                " <b>[Enter]</b>제출  <b>[Alt+Enter]</b>줄바꿈  "
                "<b>[Ctrl+Shift+↑]</b>확대  <b>[Ctrl+Shift+↓]</b>축소  "
                f"<ansiyellow>현재 {h}줄</ansiyellow>"
            )

        layout = Layout(
            HSplit([
                Window(
                    FormattedTextControl(text=prompt_text),
                    dont_extend_height=True,
                    style="class:prompt-label",
                ),
                Window(
                    BufferControl(buffer=buf, focusable=True),
                    height=get_height,
                    wrap_lines=True,
                    style="class:input-field",
                ),
                Window(
                    FormattedTextControl(get_toolbar),
                    height=1,
                    style="class:toolbar",
                ),
            ])
        )

        kb = KeyBindings()

        @kb.add("enter")
        def _submit(event):
            event.app.exit(result=buf.text)

        @kb.add("escape", "enter")  # Alt+Enter
        def _newline(event):
            buf.insert_text("\n")

        @kb.add("c-s-up")   # Ctrl+Shift+↑ (VSCode 터미널에서 가로채지 않음)
        @kb.add("c-up")     # Ctrl+↑ (다른 터미널 폴백)
        def _expand(event):
            BaseHandler._input_height = min(BaseHandler._input_height + 1, 20)

        @kb.add("c-s-down") # Ctrl+Shift+↓
        @kb.add("c-down")   # Ctrl+↓ (다른 터미널 폴백)
        def _shrink(event):
            BaseHandler._input_height = max(BaseHandler._input_height - 1, 1)

        @kb.add("c-d")
        def _ctrl_d(event):
            if not buf.text:
                event.app.exit(result=CMD_EXIT)
            else:
                buf.delete()

        @kb.add("c-c")
        def _ctrl_c(event):
            raise KeyboardInterrupt

        app_kwargs = dict(
            layout=layout,
            key_bindings=kb,
            style=Style.from_dict({
                "prompt-label": "bold",
                "input-field": "",
                "toolbar": "bg:#444444 #ffffff",
            }),
            full_screen=False,
        )

        # Win32Output 실패 시(VSCode 통합 터미널 등 xterm pseudo-tty) Vt100_Output 으로 재시도
        try:
            app = Application(**app_kwargs)
        except Exception:
            import os, sys as _sys
            from prompt_toolkit.output.vt100 import Vt100_Output
            term = os.environ.get("TERM", "xterm-256color")
            # stderr 쪽이 stdout이 파이프로 연결되더라도 터미널에 남아있는 경우가 많음
            out_stream = _sys.stderr if _sys.stderr is not None else _sys.stdout
            app = Application(output=Vt100_Output.from_pty(out_stream, term=term), **app_kwargs)

        result = app.run()
        return (result or "").strip()
