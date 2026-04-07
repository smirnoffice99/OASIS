"""
session.py — 세션 저장 / 복원

역할:
  - cases/{case_id}/session.json 에 진행 상태를 저장하고 복원한다.
  - 프로그램 재실행 시 concluded 거절이유는 건너뛰고,
    in_progress / pending 거절이유부터 재개한다.
  - "재검토 N" 명령으로 concluded 거절이유를 다시 열 수 있다.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from oa_parser import RejectionInfo


# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------

STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_CONCLUDED = "concluded"

OVERALL_PENDING = "pending"
OVERALL_IN_PROGRESS = "in_progress"
OVERALL_COMPLETED = "completed"


# ---------------------------------------------------------------------------
# 데이터 모델
# ---------------------------------------------------------------------------

class RejectionState:
    """세션 내 거절이유 하나의 진행 상태."""

    def __init__(
        self,
        id: int,
        type: str,
        subtype: str,
        claims: List[int],
        citations: List[str],
        has_citations: bool,
        status: str = STATUS_PENDING,
        current_step: int = 0,
    ):
        self.id = id
        self.type = type
        self.subtype = subtype
        self.claims = claims
        self.citations = citations
        self.has_citations = has_citations
        self.status = status
        self.current_step = current_step

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "subtype": self.subtype,
            "claims": self.claims,
            "citations": self.citations,
            "has_citations": self.has_citations,
            "status": self.status,
            "current_step": self.current_step,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RejectionState":
        return cls(
            id=d["id"],
            type=d["type"],
            subtype=d["subtype"],
            claims=d.get("claims", []),
            citations=d.get("citations", []),
            has_citations=d.get("has_citations", False),
            status=d.get("status", STATUS_PENDING),
            current_step=d.get("current_step", 0),
        )

    @classmethod
    def from_rejection_info(cls, info: RejectionInfo) -> "RejectionState":
        return cls(
            id=info.id,
            type=info.type,
            subtype=info.subtype,
            claims=info.claims,
            citations=info.citations,
            has_citations=info.has_citations,
        )


class Session:
    """사건 하나의 전체 세션 상태."""

    def __init__(
        self,
        case_id: str,
        rejections: List[RejectionState],
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        overall_status: str = OVERALL_PENDING,
    ):
        self.case_id = case_id
        self.rejections = rejections
        self.created_at = created_at or _now_iso()
        self.updated_at = updated_at or self.created_at
        self.overall_status = overall_status

    # ------------------------------------------------------------------
    # 직렬화
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "overall_status": self.overall_status,
            "rejections": [r.to_dict() for r in self.rejections],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Session":
        return cls(
            case_id=d["case_id"],
            rejections=[RejectionState.from_dict(r) for r in d.get("rejections", [])],
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
            overall_status=d.get("overall_status", OVERALL_PENDING),
        )

    # ------------------------------------------------------------------
    # 조회
    # ------------------------------------------------------------------

    def get_rejection(self, rejection_id: int) -> Optional[RejectionState]:
        for r in self.rejections:
            if r.id == rejection_id:
                return r
        return None

    def pending_rejections(self) -> List[RejectionState]:
        """처리가 필요한 거절이유 목록 (concluded 제외, id 순 정렬)."""
        return [
            r for r in sorted(self.rejections, key=lambda x: x.id)
            if r.status != STATUS_CONCLUDED
        ]

    def is_all_concluded(self) -> bool:
        return all(r.status == STATUS_CONCLUDED for r in self.rejections)

    # ------------------------------------------------------------------
    # 상태 변경
    # ------------------------------------------------------------------

    def start_rejection(self, rejection_id: int) -> None:
        """거절이유를 in_progress 로 전환하고 세션 상태를 갱신한다."""
        r = self.get_rejection(rejection_id)
        if r:
            r.status = STATUS_IN_PROGRESS
            if r.current_step == 0:
                r.current_step = 1
        self.overall_status = OVERALL_IN_PROGRESS
        self.updated_at = _now_iso()

    def advance_step(self, rejection_id: int, step: int) -> None:
        """거절이유의 현재 단계를 갱신한다."""
        r = self.get_rejection(rejection_id)
        if r:
            r.current_step = step
        self.updated_at = _now_iso()

    def conclude_rejection(self, rejection_id: int) -> None:
        """거절이유를 concluded 로 확정한다."""
        r = self.get_rejection(rejection_id)
        if r:
            r.status = STATUS_CONCLUDED
        if self.is_all_concluded():
            self.overall_status = OVERALL_COMPLETED
        self.updated_at = _now_iso()

    def reopen_rejection(self, rejection_id: int) -> bool:
        """
        "재검토 N" 명령 처리 — concluded 거절이유를 in_progress 로 되돌린다.
        current_step을 1로 초기화하여 첫 단계부터 재처리한다.
        성공 시 True, 해당 id 없으면 False.
        """
        r = self.get_rejection(rejection_id)
        if r is None:
            return False
        r.status = STATUS_IN_PROGRESS
        r.current_step = 1
        self.overall_status = OVERALL_IN_PROGRESS
        self.updated_at = _now_iso()
        return True

    def step_back(self, rejection_id: int) -> bool:
        """
        "승인취소" 명령 처리 — 현재 단계를 한 단계 이전으로 되돌린다.

        current_step이 1 이하이면 (첫 단계) 취소 불가능 → False 반환.
        concluded 상태였다면 in_progress로 되돌린다 (마지막 단계 승인 취소 시).
        성공 시 True, 해당 id 없거나 첫 단계이면 False.
        """
        r = self.get_rejection(rejection_id)
        if r is None:
            return False
        current = max(r.current_step, 1)
        if current <= 1:
            return False
        r.current_step = current - 1
        if r.status == STATUS_CONCLUDED:
            r.status = STATUS_IN_PROGRESS
            self.overall_status = OVERALL_IN_PROGRESS
        self.updated_at = _now_iso()
        return True


# ---------------------------------------------------------------------------
# 파일 I/O
# ---------------------------------------------------------------------------

def _session_path(case_dir: Path) -> Path:
    return case_dir / "session.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def session_exists(case_id: str, cases_root: str | Path = "cases") -> bool:
    case_dir = Path(cases_root) / case_id
    return _session_path(case_dir).exists()


def create_session(
    case_id: str,
    rejections: List[RejectionInfo],
    cases_root: str | Path = "cases",
) -> Session:
    """
    OA 파서 결과로부터 새 세션을 만들고 session.json 에 저장한다.
    기존 rejection_N/ 폴더(이전 실행 결과)가 있으면 삭제하여 오염을 방지한다.

    Args:
        case_id:     사건번호 (예: "KR-2024-12345")
        rejections:  oa_parser.parse_oa() 반환값
        cases_root:  cases/ 루트 경로 (기본값: "cases")

    Returns:
        Session 객체
    """
    case_dir = Path(cases_root) / case_id
    _clear_rejection_dirs(case_dir)

    states = [RejectionState.from_rejection_info(r) for r in rejections]
    session = Session(case_id=case_id, rejections=states)
    save_session(session, cases_root)
    return session


def _clear_rejection_dirs(case_dir: Path) -> None:
    """
    cases/{case_id}/rejection_N/ 폴더를 모두 삭제한다.
    새 세션 시작 시 이전 분석 결과 파일이 남아 오염되는 것을 방지한다.
    """
    import re
    for entry in case_dir.glob("rejection_*/"):
        if entry.is_dir() and re.match(r"rejection_\d+", entry.name):
            shutil.rmtree(entry)


def load_session(
    case_id: str,
    cases_root: str | Path = "cases",
) -> Session:
    """
    session.json 을 읽어 Session 을 복원한다.

    Raises:
        FileNotFoundError: session.json 이 없는 경우
    """
    case_dir = Path(cases_root) / case_id
    path = _session_path(case_dir)
    if not path.exists():
        raise FileNotFoundError(
            f"세션 파일이 없습니다: {path}\n"
            "새 세션을 시작하려면 create_session()을 사용하세요."
        )
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Session.from_dict(data)


def save_session(
    session: Session,
    cases_root: str | Path = "cases",
) -> None:
    """
    Session 을 cases/{case_id}/session.json 에 저장한다.
    디렉토리가 없으면 자동으로 생성한다.
    """
    case_dir = Path(cases_root) / session.case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    path = _session_path(case_dir)
    session.updated_at = _now_iso()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)


def get_or_create_session(
    case_id: str,
    rejections: List[RejectionInfo],
    cases_root: str | Path = "cases",
) -> tuple[Session, bool]:
    """
    기존 세션이 있으면 복원하고, 없으면 새로 생성한다.

    OA 재파싱 결과와 세션의 거절이유 수/ID가 다르면 경고를 출력한다.
    (세션은 유지하되 사용자가 인지할 수 있도록 안내)

    Returns:
        (Session, is_resumed)
        is_resumed=True  → 기존 세션 복원
        is_resumed=False → 새 세션 생성
    """
    if session_exists(case_id, cases_root):
        session = load_session(case_id, cases_root)
        _warn_if_mismatch(session, rejections)
        return session, True
    else:
        session = create_session(case_id, rejections, cases_root)
        return session, False


def _warn_if_mismatch(session: "Session", rejections: List[RejectionInfo]) -> None:
    """
    세션의 거절이유 목록과 OA 재파싱 결과가 다르면 경고를 출력한다.
    거절이유 수 또는 ID 집합이 다를 때 경고한다.
    """
    session_ids = {r.id for r in session.rejections}
    parsed_ids = {r.id for r in rejections}

    if session_ids != parsed_ids or len(session.rejections) != len(rejections):
        print(
            "\n[경고] 저장된 세션과 현재 OA 파싱 결과가 다릅니다.\n"
            f"  세션 거절이유: {sorted(session_ids)}\n"
            f"  OA 파싱 결과: {sorted(parsed_ids)}\n"
            "  세션을 초기화하려면 session.json을 삭제 후 재실행하세요.\n"
            "  현재는 저장된 세션으로 계속 진행합니다."
        )


# ---------------------------------------------------------------------------
# 결과 파일 저장 헬퍼
# ---------------------------------------------------------------------------

def save_step_result(
    case_id: str,
    rejection_id: int,
    step: int,
    content: str,
    cases_root: str | Path = "cases",
) -> Path:
    """
    cases/{case_id}/rejection_{n}/step_{x}_result.md 에 분석 결과를 저장한다.

    Returns:
        저장된 파일의 Path
    """
    rejection_dir = Path(cases_root) / case_id / f"rejection_{rejection_id}"
    rejection_dir.mkdir(parents=True, exist_ok=True)
    path = rejection_dir / f"step_{step}_result.md"
    path.write_text(content, encoding="utf-8")
    return path


def save_conclusion(
    case_id: str,
    rejection_id: int,
    content: str,
    cases_root: str | Path = "cases",
) -> Path:
    """
    cases/{case_id}/rejection_{n}/conclusion.md 에 최종 전략을 저장한다.
    """
    rejection_dir = Path(cases_root) / case_id / f"rejection_{rejection_id}"
    rejection_dir.mkdir(parents=True, exist_ok=True)
    path = rejection_dir / "conclusion.md"
    path.write_text(content, encoding="utf-8")
    return path


def append_dialogue(
    case_id: str,
    rejection_id: int,
    role: str,
    content: str,
    cases_root: str | Path = "cases",
) -> None:
    """
    cases/{case_id}/rejection_{n}/dialogue.json 에 대화 항목을 추가한다.

    Args:
        role:    "assistant" 또는 "user"
        content: 메시지 내용
    """
    rejection_dir = Path(cases_root) / case_id / f"rejection_{rejection_id}"
    rejection_dir.mkdir(parents=True, exist_ok=True)
    path = rejection_dir / "dialogue.json"

    dialogue: list = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            dialogue = json.load(f)

    dialogue.append({
        "timestamp": _now_iso(),
        "role": role,
        "content": content,
    })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(dialogue, f, ensure_ascii=False, indent=2)
