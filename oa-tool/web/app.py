"""
web/app.py — OASIS 웹 애플리케이션 (FastAPI)

실행:
  cd oa-tool
  uvicorn web.app:app --reload --port 8000

브라우저: http://localhost:8000
"""

from __future__ import annotations

import json
import queue as stdlib_queue
import sys
import threading
from pathlib import Path
from typing import Optional

# .env 파일의 환경변수를 자동으로 로드 (파일이 없어도 오류 없이 무시)
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# oa-tool 모듈 경로를 sys.path에 추가
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from oa_parser import parse_oa
from session import (
    get_or_create_session,
    load_session,
    save_session,
    session_exists,
    save_step_result,
    save_conclusion,
    append_dialogue,
    STATUS_CONCLUDED,
    STATUS_IN_PROGRESS,
    STATUS_PENDING,
)
from llm_client import LLMClient


# ---------------------------------------------------------------------------
# 경로 설정
# ---------------------------------------------------------------------------

CASES_ROOT = _ROOT / "cases"
SAMPLES_ROOT = _ROOT / "samples"
STATIC_DIR = Path(__file__).parent / "static"

# ---------------------------------------------------------------------------
# FastAPI 앱 초기화
# ---------------------------------------------------------------------------

app = FastAPI(title="OASIS", description="특허 의견제출통지서 대응 자동화")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ---------------------------------------------------------------------------
# LLM 클라이언트 (지연 초기화)
# ---------------------------------------------------------------------------

_llm: Optional[LLMClient] = None
_llm_lock = threading.Lock()


def get_llm() -> LLMClient:
    global _llm
    with _llm_lock:
        if _llm is None:
            _llm = LLMClient()
    return _llm


# ---------------------------------------------------------------------------
# 핸들러 팩토리 (main.py와 동일한 로직)
# ---------------------------------------------------------------------------

def _make_handler(rejection, session, llm, cases_root):
    from handlers.prior_art_handler import PriorArtHandler
    from handlers.clarity_handler import ClarityHandler
    from handlers.unity_handler import UnityHandler
    from handlers.default_handler import DefaultHandler

    dispatch = {
        "prior_art": PriorArtHandler,
        "clarity": ClarityHandler,
        "unity": UnityHandler,
        "other": DefaultHandler,
    }
    cls = dispatch.get(rejection.type, DefaultHandler)
    return cls(
        case_id=session.case_id,
        rejection=rejection,
        session=session,
        llm_client=llm,
        cases_root=cases_root,
    )


# ---------------------------------------------------------------------------
# Pydantic 요청 모델
# ---------------------------------------------------------------------------

class ExecuteRequest(BaseModel):
    step: Optional[int] = None
    feedback: Optional[str] = None


class ApproveRequest(BaseModel):
    last_result: str = ""


class FeedbackRequest(BaseModel):
    text: str


# ---------------------------------------------------------------------------
# 라우트: 루트 → index.html
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))


# ---------------------------------------------------------------------------
# 라우트: 사건 목록
# ---------------------------------------------------------------------------

@app.get("/api/cases")
async def list_cases():
    """cases/ 폴더 아래 사건번호 목록을 반환한다."""
    if not CASES_ROOT.exists():
        return {"cases": []}
    cases = []
    for d in sorted(CASES_ROOT.iterdir()):
        if d.is_dir():
            has_session = (d / "session.json").exists()
            has_oa = (d / "oa.pdf").exists() or (d / "oa_mock.txt").exists()
            cases.append({
                "case_id": d.name,
                "has_session": has_session,
                "has_oa": has_oa,
            })
    return {"cases": cases}


# ---------------------------------------------------------------------------
# 라우트: 파일 업로드
# ---------------------------------------------------------------------------

@app.post("/api/cases/{case_id}/upload")
async def upload_files(
    case_id: str,
    oa: Optional[UploadFile] = File(None),
    spec: Optional[UploadFile] = File(None),
    claims_en: Optional[UploadFile] = File(None),
):
    """OA, 명세서, 영문청구항 파일을 업로드한다."""
    case_dir = CASES_ROOT / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for upload, name in [(oa, "oa.pdf"), (spec, "spec.pdf"), (claims_en, "claims_en.docx")]:
        if upload and upload.filename:
            dest = case_dir / name
            content = await upload.read()
            dest.write_bytes(content)
            saved.append(name)

    return {"saved": saved, "case_dir": str(case_dir)}


@app.post("/api/cases/{case_id}/upload-citation")
async def upload_citation(
    case_id: str,
    citation_id: str = Form(...),
    file: UploadFile = File(...),
):
    """인용문헌 파일을 업로드한다."""
    citations_dir = CASES_ROOT / case_id / "citations"
    citations_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename).suffix or ".pdf"
    dest = citations_dir / f"{citation_id}{suffix}"
    content = await file.read()
    dest.write_bytes(content)

    return {"saved": dest.name}


# ---------------------------------------------------------------------------
# 라우트: OA 파싱 + 세션 생성/로드
# ---------------------------------------------------------------------------

@app.post("/api/cases/{case_id}/parse")
async def parse_case(case_id: str):
    """OA를 파싱하고 세션을 생성(또는 기존 세션을 로드)한다."""
    case_dir = CASES_ROOT / case_id
    if not case_dir.exists():
        raise HTTPException(404, f"사건 디렉토리가 없습니다: {case_id}")

    try:
        rejections = parse_oa(case_dir)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))

    session, is_resumed = get_or_create_session(case_id, rejections, CASES_ROOT)
    return {
        "session": session.to_dict(),
        "is_resumed": is_resumed,
        "rejection_count": len(rejections),
    }


# ---------------------------------------------------------------------------
# 라우트: 세션 상태 조회
# ---------------------------------------------------------------------------

@app.get("/api/cases/{case_id}/status")
async def get_status(case_id: str):
    """현재 세션 상태를 반환한다."""
    if not session_exists(case_id, CASES_ROOT):
        raise HTTPException(404, "세션이 없습니다. 먼저 파싱을 실행하세요.")

    session = load_session(case_id, CASES_ROOT)

    # 각 거절이유의 저장된 step 결과 파일 목록도 포함
    rejection_files = {}
    for r in session.rejections:
        rej_dir = CASES_ROOT / case_id / f"rejection_{r.id}"
        if rej_dir.exists():
            files = sorted(f.name for f in rej_dir.glob("step_*_result.md"))
            conclusion = (rej_dir / "conclusion.md").exists()
            rejection_files[r.id] = {"step_files": files, "has_conclusion": conclusion}

    return {"session": session.to_dict(), "rejection_files": rejection_files}


# ---------------------------------------------------------------------------
# 라우트: step 결과 파일 읽기
# ---------------------------------------------------------------------------

@app.get("/api/cases/{case_id}/rejections/{rid}/steps/{step}")
async def get_step_result(case_id: str, rid: int, step: int):
    """저장된 step 결과 파일을 반환한다."""
    path = CASES_ROOT / case_id / f"rejection_{rid}" / f"step_{step}_result.md"
    if not path.exists():
        raise HTTPException(404, "결과 파일이 없습니다.")
    return {"content": path.read_text(encoding="utf-8")}


@app.get("/api/cases/{case_id}/rejections/{rid}/conclusion")
async def get_conclusion(case_id: str, rid: int):
    """저장된 conclusion 파일을 반환한다."""
    path = CASES_ROOT / case_id / f"rejection_{rid}" / "conclusion.md"
    if not path.exists():
        raise HTTPException(404, "결론 파일이 없습니다.")
    return {"content": path.read_text(encoding="utf-8")}


# ---------------------------------------------------------------------------
# 라우트: step 실행 (SSE 스트리밍)
# ---------------------------------------------------------------------------

@app.post("/api/cases/{case_id}/rejections/{rid}/execute")
async def execute_step(case_id: str, rid: int, body: ExecuteRequest):
    """
    지정한 거절이유의 현재 step을 실행하고 LLM 결과를 SSE로 스트리밍한다.
    body.feedback이 있으면 피드백을 반영하여 재생성한다.
    """
    if not session_exists(case_id, CASES_ROOT):
        raise HTTPException(404, "세션이 없습니다.")

    session = load_session(case_id, CASES_ROOT)
    rejection = session.get_rejection(rid)

    if rejection is None:
        raise HTTPException(404, f"거절이유 #{rid}를 찾을 수 없습니다.")

    # 실행할 step 결정
    step = body.step if body.step is not None else max(rejection.current_step, 1)
    feedback = body.feedback or None

    # 이전 단계가 승인되지 않은 경우 실행 불가 (순차 실행 강제)
    allowed_step = max(rejection.current_step, 1)
    if step > allowed_step:
        raise HTTPException(
            400,
            f"Step {step}은(는) 실행할 수 없습니다. "
            f"Step {allowed_step}을(를) 먼저 승인하세요."
        )

    # 세션 상태 업데이트
    if rejection.status == STATUS_PENDING:
        session.start_rejection(rid)
        save_session(session, CASES_ROOT)

    llm = get_llm()

    # ------------------------------------------------------------------
    # 스트리밍 인터셉터 설정
    # LLM chat() 호출을 가로채서 청크를 큐에 넣는다
    # ------------------------------------------------------------------
    chunk_queue: stdlib_queue.Queue = stdlib_queue.Queue()
    result_holder: list[str] = []
    error_holder: list[str] = []
    original_chat = llm.chat

    def streaming_chat(user_message: str, system_prompt: str = "", temperature: float = 0.3) -> str:
        accumulated = ""
        try:
            for chunk in llm.chat_stream(user_message, system_prompt, temperature):
                chunk_queue.put(("chunk", chunk))
                accumulated += chunk
        except Exception as exc:
            chunk_queue.put(("error", str(exc)))
            raise
        return accumulated

    def run_step():
        llm.chat = streaming_chat
        try:
            handler = _make_handler(rejection, session, llm, CASES_ROOT)
            result = handler.execute_step(step, feedback)

            # 결과 파일 저장
            save_step_result(case_id, rid, step, result, CASES_ROOT)
            append_dialogue(case_id, rid, "assistant", result, CASES_ROOT)
            result_holder.append(result)
        except Exception as exc:
            import traceback
            error_holder.append(traceback.format_exc())
            chunk_queue.put(("error", str(exc)))
        finally:
            llm.chat = original_chat
            chunk_queue.put(("done", None))

    thread = threading.Thread(target=run_step, daemon=True)
    thread.start()

    async def generate():
        import asyncio
        deadline = 300  # 최대 대기 시간(초)
        elapsed = 0.0
        interval = 0.05  # polling 간격(초)

        while elapsed < deadline:
            try:
                event_type, data = chunk_queue.get_nowait()
            except stdlib_queue.Empty:
                await asyncio.sleep(interval)
                elapsed += interval
                continue

            if event_type == "chunk":
                yield f"data: {json.dumps({'type': 'chunk', 'text': data})}\n\n"
            elif event_type == "error":
                yield f"data: {json.dumps({'type': 'error', 'message': data})}\n\n"
                break
            elif event_type == "done":
                result = result_holder[0] if result_holder else ""
                tmp_handler = _make_handler(rejection, session, llm, CASES_ROOT)
                total_steps = tmp_handler.STEPS
                yield f"data: {json.dumps({'type': 'done', 'result': result, 'step': step, 'total_steps': total_steps})}\n\n"
                break
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': '응답 시간 초과 (300초)'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# 라우트: step 승인
# ---------------------------------------------------------------------------

@app.post("/api/cases/{case_id}/rejections/{rid}/approve")
async def approve_step(case_id: str, rid: int, body: ApproveRequest):
    """현재 step을 승인하고 다음 단계로 진행하거나 거절이유를 완료한다."""
    session = load_session(case_id, CASES_ROOT)
    rejection = session.get_rejection(rid)

    if rejection is None:
        raise HTTPException(404, f"거절이유 #{rid}를 찾을 수 없습니다.")

    step = rejection.current_step
    llm = get_llm()
    handler = _make_handler(rejection, session, llm, CASES_ROOT)
    total_steps = handler.STEPS
    is_last = step == total_steps

    append_dialogue(case_id, rid, "user", "승인", CASES_ROOT)

    if is_last:
        # 마지막 단계 — 결론 저장 + 거절이유 완료
        if body.last_result:
            save_conclusion(case_id, rid, body.last_result, CASES_ROOT)
        session.conclude_rejection(rid)
    else:
        session.advance_step(rid, step + 1)

    save_session(session, CASES_ROOT)
    return {"session": session.to_dict(), "concluded": is_last}


# ---------------------------------------------------------------------------
# 라우트: step 건너뛰기
# ---------------------------------------------------------------------------

@app.post("/api/cases/{case_id}/rejections/{rid}/skip")
async def skip_step(case_id: str, rid: int):
    """현재 step을 건너뛰고 다음 단계로 진행한다."""
    session = load_session(case_id, CASES_ROOT)
    rejection = session.get_rejection(rid)

    if rejection is None:
        raise HTTPException(404, f"거절이유 #{rid}를 찾을 수 없습니다.")

    step = rejection.current_step
    llm = get_llm()
    handler = _make_handler(rejection, session, llm, CASES_ROOT)
    total_steps = handler.STEPS
    is_last = step == total_steps

    # 건너뜀 표시 저장
    save_step_result(case_id, rid, step, "(건너뜀)", CASES_ROOT)
    append_dialogue(case_id, rid, "user", "건너뛰기", CASES_ROOT)

    if is_last:
        save_conclusion(case_id, rid, "(건너뜀)", CASES_ROOT)
        session.conclude_rejection(rid)
    else:
        session.advance_step(rid, step + 1)

    save_session(session, CASES_ROOT)
    return {"session": session.to_dict(), "concluded": is_last}


# ---------------------------------------------------------------------------
# 라우트: step 승인 취소
# ---------------------------------------------------------------------------

@app.post("/api/cases/{case_id}/rejections/{rid}/cancel-approval")
async def cancel_approval(case_id: str, rid: int):
    """
    현재 단계의 이전 단계 승인을 취소하고 그 단계로 돌아간다.

    규칙:
      - 첫 번째 단계(Step 1)는 취소 불가.
      - 가장 최근에 승인된 단계만 취소 가능 (역순 순차 취소).
      - 현재 단계의 stale 결과 파일을 삭제한다.
    """
    session = load_session(case_id, CASES_ROOT)
    rejection = session.get_rejection(rid)

    if rejection is None:
        raise HTTPException(404, f"거절이유 #{rid}를 찾을 수 없습니다.")

    current_step = max(rejection.current_step, 1)
    if rejection.status == STATUS_CONCLUDED:
        # concluded인 경우 current_step은 STEPS+1로 간주
        llm = get_llm()
        handler = _make_handler(rejection, session, llm, CASES_ROOT)
        current_step = handler.STEPS + 1

    if current_step <= 1:
        raise HTTPException(400, "첫 번째 단계는 이전 단계 승인을 취소할 수 없습니다.")

    # 현재 단계의 stale 결과 파일 삭제
    stale_path = CASES_ROOT / case_id / f"rejection_{rid}" / f"step_{current_step}_result.md"
    stale_path.unlink(missing_ok=True)

    ok = session.step_back(rid)
    if not ok:
        raise HTTPException(400, "이전 단계 승인을 취소할 수 없습니다.")

    save_session(session, CASES_ROOT)
    return {
        "session": session.to_dict(),
        "current_step": rejection.current_step,
    }


# ---------------------------------------------------------------------------
# 라우트: 거절이유 재검토
# ---------------------------------------------------------------------------

@app.post("/api/cases/{case_id}/rejections/{rid}/reopen")
async def reopen_rejection(case_id: str, rid: int):
    """완료된 거절이유를 재검토 상태로 되돌린다."""
    session = load_session(case_id, CASES_ROOT)
    ok = session.reopen_rejection(rid)
    if not ok:
        raise HTTPException(404, f"거절이유 #{rid}를 찾을 수 없습니다.")
    save_session(session, CASES_ROOT)
    return {"session": session.to_dict()}


# ---------------------------------------------------------------------------
# 공통 헬퍼 — ReportGenerator 스트리밍 실행
# ---------------------------------------------------------------------------

def _run_report_streaming(fn, chunk_queue: stdlib_queue.Queue) -> None:
    """
    ReportGenerator의 generate_draft() 또는 finalize()를 백그라운드 스레드에서 실행하고
    LLM 청크를 chunk_queue에 넣는다.
    fn: callable — 반환값은 str(draft) 또는 Path(finalize)
    """
    pass  # 호출부에서 직접 구성


# ---------------------------------------------------------------------------
# 라우트: 리포트 초안 생성 (SSE 스트리밍)
# ---------------------------------------------------------------------------

class DraftRequest(BaseModel):
    feedback: Optional[str] = None


@app.post("/api/cases/{case_id}/report/draft")
async def generate_report_draft(case_id: str, body: DraftRequest):
    """
    영문 코멘트 초안을 LLM으로 생성하고 SSE로 스트리밍한다.
    body.feedback이 있으면 수정 지침으로 포함한다.
    완료 후 draft_comment.md / draft_data.json 저장.
    """
    session = load_session(case_id, CASES_ROOT)

    if not session.is_all_concluded():
        pending = session.pending_rejections()
        raise HTTPException(
            422,
            f"미완료 거절이유가 {len(pending)}건 있습니다: "
            + ", ".join(f"#{r.id}" for r in pending),
        )

    llm = get_llm()
    chunk_queue: stdlib_queue.Queue = stdlib_queue.Queue()
    result_holder: list[str] = []
    error_holder: list[str] = []
    original_chat = llm.chat

    def streaming_chat(user_message: str, system_prompt: str = "", temperature: float = 0.3) -> str:
        accumulated = ""
        try:
            for chunk in llm.chat_stream(user_message, system_prompt, temperature):
                chunk_queue.put(("chunk", chunk))
                accumulated += chunk
        except Exception as exc:
            chunk_queue.put(("error", str(exc)))
            raise
        return accumulated

    def run_draft():
        llm.chat = streaming_chat
        try:
            from report_generator import ReportGenerator
            generator = ReportGenerator(
                case_id=case_id,
                session=session,
                llm_client=llm,
                cases_root=CASES_ROOT,
                samples_root=SAMPLES_ROOT,
            )
            markdown = generator.generate_draft(feedback=body.feedback or None)
            result_holder.append(markdown)
        except Exception as exc:
            import traceback
            error_holder.append(traceback.format_exc())
            chunk_queue.put(("error", str(exc)))
        finally:
            llm.chat = original_chat
            chunk_queue.put(("done", None))

    thread = threading.Thread(target=run_draft, daemon=True)
    thread.start()

    async def generate():
        import asyncio
        deadline = 600.0
        elapsed = 0.0
        interval = 0.05

        while elapsed < deadline:
            try:
                event_type, data = chunk_queue.get_nowait()
            except stdlib_queue.Empty:
                await asyncio.sleep(interval)
                elapsed += interval
                continue

            if event_type == "chunk":
                yield f"data: {json.dumps({'type': 'chunk', 'text': data})}\n\n"
            elif event_type == "error":
                yield f"data: {json.dumps({'type': 'error', 'message': data})}\n\n"
                break
            elif event_type == "done":
                draft = result_holder[0] if result_holder else ""
                yield f"data: {json.dumps({'type': 'done', 'draft': draft})}\n\n"
                break
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': '응답 시간 초과 (600초)'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# 라우트: 저장된 초안 조회
# ---------------------------------------------------------------------------

@app.get("/api/cases/{case_id}/report/draft")
async def get_report_draft(case_id: str):
    """저장된 draft_comment.md를 반환한다."""
    path = CASES_ROOT / case_id / "draft_comment.md"
    if not path.exists():
        raise HTTPException(404, "초안이 없습니다. 먼저 초안을 작성하세요.")
    return {"draft": path.read_text(encoding="utf-8")}


# ---------------------------------------------------------------------------
# 라우트: 리포트 최종 확정 (draft_data.json → docx)
# ---------------------------------------------------------------------------

@app.post("/api/cases/{case_id}/report/finalize")
async def finalize_report(case_id: str):
    """
    저장된 draft_data.json을 final_comment.docx로 변환한다. LLM 호출 없음.
    """
    session = load_session(case_id, CASES_ROOT)
    llm = get_llm()

    try:
        from report_generator import ReportGenerator
        generator = ReportGenerator(
            case_id=case_id,
            session=session,
            llm_client=llm,
            cases_root=CASES_ROOT,
            samples_root=SAMPLES_ROOT,
        )
        output_path = generator.finalize()
        return {"output": str(output_path), "filename": output_path.name}
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc))
    except Exception as exc:
        import traceback
        raise HTTPException(500, f"최종 확정 실패: {exc}\n{traceback.format_exc()}")


# ---------------------------------------------------------------------------
# 라우트: 리포트 다운로드
# ---------------------------------------------------------------------------

@app.get("/api/cases/{case_id}/download")
async def download_report(case_id: str):
    """생성된 final_comment.docx를 다운로드한다."""
    docx_path = CASES_ROOT / case_id / "final_comment.docx"
    if not docx_path.exists():
        raise HTTPException(404, "리포트 파일이 없습니다. 먼저 리포트를 생성하세요.")
    return FileResponse(
        str(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"final_comment_{case_id}.docx",
    )


# ---------------------------------------------------------------------------
# 라우트: 세션 초기화 (새로 시작)
# ---------------------------------------------------------------------------

@app.delete("/api/cases/{case_id}/session")
async def delete_session(case_id: str):
    """session.json을 삭제하여 세션을 초기화한다."""
    session_path = CASES_ROOT / case_id / "session.json"
    if session_path.exists():
        session_path.unlink()
    return {"message": f"{case_id} 세션이 초기화되었습니다."}


# ---------------------------------------------------------------------------
# 라우트: 사건 파일 목록 조회
# ---------------------------------------------------------------------------

@app.get("/api/cases/{case_id}/files")
async def list_case_files(case_id: str):
    """사건 디렉토리에 업로드된 파일 목록을 반환한다."""
    case_dir = CASES_ROOT / case_id
    if not case_dir.exists():
        return {"files": {}, "citations": []}

    files = {}
    for oa_name in ("oa.pdf", "oa_mock.txt"):
        if (case_dir / oa_name).exists():
            files["oa"] = oa_name
            break
    for spec_name in ("spec.pdf", "spec_mock.txt"):
        if (case_dir / spec_name).exists():
            files["spec"] = spec_name
            break
    for claims_name in ("claims_en.docx", "claims_en_mock.txt"):
        if (case_dir / claims_name).exists():
            files["claims_en"] = claims_name
            break

    citations = []
    citations_dir = case_dir / "citations"
    if citations_dir.exists():
        for f in sorted(citations_dir.iterdir()):
            if f.is_file():
                citations.append({"id": f.stem, "name": f.name})

    return {"files": files, "citations": citations}


# ---------------------------------------------------------------------------
# 라우트: 사건 삭제
# ---------------------------------------------------------------------------

@app.delete("/api/cases/{case_id}")
async def delete_case(case_id: str):
    """사건 디렉토리 전체를 삭제한다."""
    import shutil
    case_dir = CASES_ROOT / case_id
    if not case_dir.exists():
        raise HTTPException(404, f"사건이 없습니다: {case_id}")
    shutil.rmtree(case_dir)
    return {"message": f"{case_id} 삭제됨"}
