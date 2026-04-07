"""
sample_manager.py — 스타일 샘플 관리 + Few-shot / RAG 자동 전환

역할:
  - samples/{type}/ 폴더의 .docx/.txt 파일을 관리한다.
  - 전체 샘플 수 < 20: Few-shot 모드 (최근 수정 3건)
  - 전체 샘플 수 >= 20: RAG 모드 (chromadb 시맨틱 검색 상위 3건) 자동 전환

CLI:
  python sample_manager.py add <파일> --type <유형>   ← 샘플 추가 + 벡터화
  python sample_manager.py list                       ← 전체 목록
  python sample_manager.py delete <id>                ← 샘플 삭제
  python sample_manager.py search <키워드>            ← 유사 샘플 검색
  python sample_manager.py stats                      ← 유형별 현황
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------

VALID_TYPES = ("prior_art", "clarity", "unity", "other")
RAG_THRESHOLD = 20          # 이 수 이상이면 RAG 모드
FEW_SHOT_COUNT = 3          # Few-shot / RAG 모두 상위 N건 반환
INDEX_FILE = "index.json"   # samples/index.json
COLLECTION_NAME = "oa_samples"


# ---------------------------------------------------------------------------
# 샘플 항목 데이터 클래스
# ---------------------------------------------------------------------------

class SampleEntry:
    def __init__(
        self,
        sample_id: str,
        sample_type: str,
        filename: str,
        rel_path: str,
        added_at: str,
    ):
        self.sample_id = sample_id
        self.sample_type = sample_type
        self.filename = filename
        self.rel_path = rel_path          # samples/{type}/{filename}
        self.added_at = added_at

    def to_dict(self) -> dict:
        return {
            "id": self.sample_id,
            "type": self.sample_type,
            "filename": self.filename,
            "path": self.rel_path,
            "added_at": self.added_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SampleEntry":
        return cls(
            sample_id=d["id"],
            sample_type=d["type"],
            filename=d["filename"],
            rel_path=d["path"],
            added_at=d.get("added_at", ""),
        )


# ---------------------------------------------------------------------------
# SampleManager
# ---------------------------------------------------------------------------

class SampleManager:
    """
    샘플 파일 관리 및 Few-shot/RAG 선택 로직.

    Args:
        samples_root: samples/ 디렉토리 경로 (기본: 스크립트 옆 samples/)
    """

    def __init__(self, samples_root: str | Path | None = None):
        if samples_root is None:
            samples_root = Path(__file__).parent / "samples"
        self.root = Path(samples_root)
        self.vector_db_path = self.root / "vector_db"
        self.index_path = self.root / INDEX_FILE
        self._ensure_dirs()

    # ------------------------------------------------------------------
    # 디렉토리 초기화
    # ------------------------------------------------------------------

    def _ensure_dirs(self) -> None:
        for t in VALID_TYPES:
            (self.root / t).mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 인덱스 I/O
    # ------------------------------------------------------------------

    def _load_index(self) -> list[SampleEntry]:
        if not self.index_path.exists():
            return []
        with open(self.index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [SampleEntry.from_dict(d) for d in data]

    def _save_index(self, entries: list[SampleEntry]) -> None:
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in entries], f, ensure_ascii=False, indent=2)

    def _next_id(self, entries: list[SampleEntry]) -> str:
        if not entries:
            return "001"
        max_num = max(int(e.sample_id) for e in entries if e.sample_id.isdigit())
        return f"{max_num + 1:03d}"

    # ------------------------------------------------------------------
    # 샘플 추가
    # ------------------------------------------------------------------

    def add(self, source_path: str | Path, sample_type: str) -> SampleEntry:
        """
        샘플 파일을 samples/{type}/ 에 복사하고 인덱스에 등록한다.
        전체 샘플 수가 RAG_THRESHOLD 이상이면 벡터 DB에도 추가한다.

        Args:
            source_path:  추가할 .docx 또는 .txt 파일 경로
            sample_type:  prior_art / clarity / unity / other

        Returns:
            SampleEntry
        """
        if sample_type not in VALID_TYPES:
            raise ValueError(
                f"유효하지 않은 유형: '{sample_type}'. "
                f"허용값: {', '.join(VALID_TYPES)}"
            )

        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {source}")
        if source.suffix.lower() not in (".docx", ".txt"):
            raise ValueError("지원 형식: .docx, .txt")

        entries = self._load_index()
        new_id = self._next_id(entries)

        # samples/{type}/{id}_{filename} 으로 저장
        dest_name = f"{new_id}_{source.name}"
        dest_path = self.root / sample_type / dest_name
        shutil.copy2(source, dest_path)

        rel_path = f"samples/{sample_type}/{dest_name}"
        entry = SampleEntry(
            sample_id=new_id,
            sample_type=sample_type,
            filename=dest_name,
            rel_path=rel_path,
            added_at=_now_iso(),
        )
        entries.append(entry)
        self._save_index(entries)

        # 전체 샘플 수가 RAG_THRESHOLD 이상이면 벡터 DB에 추가
        if len(entries) >= RAG_THRESHOLD:
            self._upsert_to_vector_db(entry, dest_path)

        return entry

    # ------------------------------------------------------------------
    # 샘플 삭제
    # ------------------------------------------------------------------

    def delete(self, sample_id: str) -> bool:
        """
        ID로 샘플을 삭제한다 (파일 + 인덱스 + 벡터 DB).

        Returns:
            True if deleted, False if not found
        """
        entries = self._load_index()
        target = next((e for e in entries if e.sample_id == sample_id), None)
        if target is None:
            return False

        # 파일 삭제
        file_path = self.root.parent / target.rel_path if not (
            self.root / target.sample_type / target.filename
        ).exists() else self.root / target.sample_type / target.filename

        actual_path = self.root / target.sample_type / target.filename
        if actual_path.exists():
            actual_path.unlink()

        # 인덱스에서 제거
        entries = [e for e in entries if e.sample_id != sample_id]
        self._save_index(entries)

        # 벡터 DB에서 제거 (있으면)
        self._delete_from_vector_db(sample_id)

        return True

    # ------------------------------------------------------------------
    # 목록 조회
    # ------------------------------------------------------------------

    def list_all(self, sample_type: Optional[str] = None) -> list[SampleEntry]:
        """전체 또는 특정 유형의 샘플 목록을 반환한다."""
        entries = self._load_index()
        if sample_type:
            entries = [e for e in entries if e.sample_type == sample_type]
        return sorted(entries, key=lambda e: e.added_at)

    # ------------------------------------------------------------------
    # 통계
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, int]:
        """유형별 샘플 수를 반환한다."""
        entries = self._load_index()
        counts: dict[str, int] = {t: 0 for t in VALID_TYPES}
        for e in entries:
            counts[e.sample_type] = counts.get(e.sample_type, 0) + 1
        counts["total"] = len(entries)
        counts["mode"] = "RAG" if len(entries) >= RAG_THRESHOLD else "Few-shot"
        return counts

    # ------------------------------------------------------------------
    # 유사 샘플 검색 (CLI용)
    # ------------------------------------------------------------------

    def search(self, query: str, sample_type: Optional[str] = None, n: int = 5) -> list[SampleEntry]:
        """
        키워드/의미 기반 유사 샘플을 검색한다.
        RAG 모드: chromadb 시맨틱 검색
        Few-shot 모드: 파일명 기반 키워드 검색
        """
        entries = self._load_index()
        if sample_type:
            entries = [e for e in entries if e.sample_type == sample_type]

        total = len(self._load_index())
        if total >= RAG_THRESHOLD:
            return self._rag_search(query, sample_type, n)
        else:
            # Few-shot 모드: 파일명에 키워드 포함된 항목 반환
            keyword = query.lower()
            matched = [
                e for e in entries
                if keyword in e.filename.lower() or keyword in e.sample_type.lower()
            ]
            return matched[:n] if matched else entries[:n]

    # ------------------------------------------------------------------
    # report_generator.py가 호출하는 핵심 메서드
    # ------------------------------------------------------------------

    def get_relevant_samples(
        self,
        sample_type: str,
        query_text: str = "",
        n: int = FEW_SHOT_COUNT,
    ) -> list[str]:
        """
        유형별로 관련 샘플 내용을 반환한다.
        Few-shot 모드: 가장 최근 수정된 N건
        RAG 모드:     query_text와 의미적으로 유사한 상위 N건

        Returns:
            샘플 텍스트 내용 리스트 (최대 n개)
        """
        all_entries = self._load_index()
        total = len(all_entries)

        if total >= RAG_THRESHOLD and query_text:
            entries = self._rag_search(query_text, sample_type, n)
        else:
            entries = self._few_shot_select(sample_type, n)

        texts = []
        for entry in entries:
            path = self.root / entry.sample_type / entry.filename
            if path.exists():
                texts.append(_read_file_text(path))
        return texts

    def get_mode(self) -> str:
        """현재 모드를 반환한다: 'few-shot' 또는 'rag'"""
        total = len(self._load_index())
        return "rag" if total >= RAG_THRESHOLD else "few-shot"

    # ------------------------------------------------------------------
    # Few-shot 선택 (최근 수정 N건)
    # ------------------------------------------------------------------

    def _few_shot_select(self, sample_type: str, n: int) -> list[SampleEntry]:
        """samples/{type}/ 폴더에서 최근 수정된 N건을 반환한다."""
        type_dir = self.root / sample_type
        files = sorted(
            [f for f in type_dir.iterdir() if f.suffix.lower() in (".docx", ".txt")],
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:n]

        entries = self._load_index()
        result = []
        for f in files:
            entry = next(
                (e for e in entries if e.filename == f.name and e.sample_type == sample_type),
                None,
            )
            if entry:
                result.append(entry)
            else:
                # 인덱스에 없는 파일은 임시 entry 생성
                result.append(SampleEntry(
                    sample_id="?",
                    sample_type=sample_type,
                    filename=f.name,
                    rel_path=f"samples/{sample_type}/{f.name}",
                    added_at="",
                ))
        return result

    # ------------------------------------------------------------------
    # RAG — chromadb 연동
    # ------------------------------------------------------------------

    def _get_chroma_collection(self):
        """chromadb 컬렉션을 반환한다. 미설치 시 ImportError."""
        try:
            import chromadb  # noqa: PLC0415
        except ImportError:
            raise ImportError(
                "chromadb가 설치되지 않았습니다: pip install chromadb"
            )
        client = chromadb.PersistentClient(path=str(self.vector_db_path))
        return client.get_or_create_collection(COLLECTION_NAME)

    def _get_embedding(self, text: str) -> list[float]:
        """sentence-transformers로 텍스트를 벡터화한다."""
        try:
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415
        except ImportError:
            raise ImportError(
                "sentence-transformers가 설치되지 않았습니다: "
                "pip install sentence-transformers"
            )
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        return model.encode(text[:2000]).tolist()  # 긴 텍스트는 앞부분만 사용

    def _upsert_to_vector_db(self, entry: SampleEntry, file_path: Path) -> None:
        """샘플을 chromadb에 추가/갱신한다. 실패해도 경고만 출력한다."""
        try:
            text = _read_file_text(file_path)
            if not text:
                return
            collection = self._get_chroma_collection()
            embedding = self._get_embedding(text)
            collection.upsert(
                ids=[entry.sample_id],
                embeddings=[embedding],
                documents=[text[:2000]],
                metadatas=[{
                    "type": entry.sample_type,
                    "filename": entry.filename,
                    "added_at": entry.added_at,
                }],
            )
        except Exception as e:
            print(f"  [경고] 벡터 DB 추가 실패 ({entry.filename}): {e}", file=sys.stderr)

    def _delete_from_vector_db(self, sample_id: str) -> None:
        """chromadb에서 샘플을 삭제한다. 실패해도 무시한다."""
        try:
            collection = self._get_chroma_collection()
            collection.delete(ids=[sample_id])
        except Exception:
            pass

    def _rag_search(
        self, query: str, sample_type: Optional[str], n: int
    ) -> list[SampleEntry]:
        """chromadb에서 의미적으로 유사한 샘플을 검색한다."""
        try:
            collection = self._get_chroma_collection()
            embedding = self._get_embedding(query)

            where = {"type": sample_type} if sample_type else None
            results = collection.query(
                query_embeddings=[embedding],
                n_results=min(n, collection.count()),
                where=where,
            )
            if not results["ids"] or not results["ids"][0]:
                return self._few_shot_select(sample_type or VALID_TYPES[0], n)

            entries = self._load_index()
            found = []
            for rid in results["ids"][0]:
                entry = next((e for e in entries if e.sample_id == rid), None)
                if entry:
                    found.append(entry)
            return found

        except Exception as e:
            print(f"  [경고] RAG 검색 실패, Few-shot으로 대체: {e}", file=sys.stderr)
            return self._few_shot_select(sample_type or VALID_TYPES[0], n)

    # ------------------------------------------------------------------
    # 전체 재벡터화 (RAG 모드 전환 시 또는 복구용)
    # ------------------------------------------------------------------

    def rebuild_vector_db(self) -> int:
        """
        모든 샘플을 chromadb에 재등록한다.

        Returns:
            등록된 샘플 수
        """
        entries = self._load_index()
        count = 0
        for entry in entries:
            path = self.root / entry.sample_type / entry.filename
            if path.exists():
                self._upsert_to_vector_db(entry, path)
                count += 1
        return count


# ---------------------------------------------------------------------------
# 파일 읽기 헬퍼
# ---------------------------------------------------------------------------

def _read_file_text(path: Path) -> str:
    """
    .docx 또는 .txt 파일의 텍스트를 반환한다.
    """
    suffix = path.suffix.lower()
    if suffix == ".docx":
        try:
            from docx import Document  # noqa: PLC0415
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise ImportError("python-docx가 필요합니다: pip install python-docx")
        except Exception as e:
            return f"[파일 읽기 오류: {e}]"
    elif suffix == ".txt":
        return path.read_text(encoding="utf-8")
    return ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_add(args, manager: SampleManager) -> None:
    entry = manager.add(args.file, args.type)
    total = len(manager._load_index())
    mode = manager.get_mode()
    print(f"샘플 추가 완료: [{entry.sample_id}] {entry.filename} (유형: {entry.sample_type})")
    print(f"전체 샘플 수: {total}건 | 현재 모드: {mode.upper()}")
    if total == RAG_THRESHOLD:
        print(f"※ 샘플 수가 {RAG_THRESHOLD}건에 도달했습니다. RAG 모드로 전환됩니다.")
        print("  전체 샘플을 벡터 DB에 등록합니다...")
        count = manager.rebuild_vector_db()
        print(f"  벡터 DB 등록 완료: {count}건")


def _cmd_list(args, manager: SampleManager) -> None:
    sample_type = getattr(args, "type", None)
    entries = manager.list_all(sample_type)
    if not entries:
        print("등록된 샘플이 없습니다.")
        return

    print(f"\n{'ID':>4}  {'유형':<12}  {'파일명':<40}  {'등록일'}")
    print("-" * 80)
    for e in entries:
        added = e.added_at[:10] if e.added_at else "-"
        print(f"{e.sample_id:>4}  {e.sample_type:<12}  {e.filename:<40}  {added}")
    print(f"\n총 {len(entries)}건")


def _cmd_delete(args, manager: SampleManager) -> None:
    ok = manager.delete(args.id)
    if ok:
        print(f"샘플 [{args.id}] 삭제 완료.")
    else:
        print(f"샘플 [{args.id}]를 찾을 수 없습니다.")


def _cmd_search(args, manager: SampleManager) -> None:
    sample_type = getattr(args, "type", None)
    entries = manager.search(args.keyword, sample_type, n=5)
    if not entries:
        print("검색 결과가 없습니다.")
        return
    mode = manager.get_mode()
    print(f"[{mode.upper()} 검색] '{args.keyword}' 결과 {len(entries)}건:\n")
    for e in entries:
        print(f"  [{e.sample_id}] {e.sample_type:<12}  {e.filename}")


def _cmd_stats(args, manager: SampleManager) -> None:
    s = manager.stats()
    print("\n=== 샘플 현황 ===")
    for t in VALID_TYPES:
        print(f"  {t:<15}: {s.get(t, 0):>3}건")
    print(f"  {'합계':<15}: {s['total']:>3}건")
    print(f"  현재 모드        : {s['mode']}")
    if s["total"] < RAG_THRESHOLD:
        remaining = RAG_THRESHOLD - s["total"]
        print(f"  RAG 전환까지     : {remaining}건 남음")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OASIS 샘플 관리자 — Few-shot/RAG 자동 전환"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="샘플 추가")
    p_add.add_argument("file", help="추가할 .docx 또는 .txt 파일 경로")
    p_add.add_argument(
        "--type", required=True,
        choices=VALID_TYPES,
        help="샘플 유형: prior_art / clarity / unity / other",
    )

    # list
    p_list = sub.add_parser("list", help="샘플 목록")
    p_list.add_argument(
        "--type", choices=VALID_TYPES, default=None, help="유형 필터 (선택)"
    )

    # delete
    p_del = sub.add_parser("delete", help="샘플 삭제")
    p_del.add_argument("id", help="삭제할 샘플 ID")

    # search
    p_search = sub.add_parser("search", help="유사 샘플 검색")
    p_search.add_argument("keyword", help="검색 키워드")
    p_search.add_argument(
        "--type", choices=VALID_TYPES, default=None, help="유형 필터 (선택)"
    )

    # stats
    sub.add_parser("stats", help="유형별 샘플 현황")

    args = parser.parse_args()
    manager = SampleManager()

    commands = {
        "add": _cmd_add,
        "list": _cmd_list,
        "delete": _cmd_delete,
        "search": _cmd_search,
        "stats": _cmd_stats,
    }
    commands[args.command](args, manager)


if __name__ == "__main__":
    main()
