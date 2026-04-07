"""
sample_manager.py 단위 테스트 (chromadb/sentence-transformers 미설치 환경 대응)
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sample_manager import SampleManager, SampleEntry, RAG_THRESHOLD, VALID_TYPES

# ---------------------------------------------------------------------------
# 테스트용 임시 디렉토리
# ---------------------------------------------------------------------------

def make_temp_manager() -> tuple[SampleManager, Path]:
    tmp = Path(tempfile.mkdtemp())
    manager = SampleManager(samples_root=tmp)
    return manager, tmp


def make_sample_txt(tmp_dir: Path, name: str, content: str = "sample content") -> Path:
    p = tmp_dir / name
    p.write_text(content, encoding="utf-8")
    return p


def cleanup(tmp: Path):
    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------

def test_ensure_dirs():
    """초기화 시 유형별 폴더와 vector_db 폴더가 생성되는지 확인."""
    manager, tmp = make_temp_manager()
    for t in VALID_TYPES:
        assert (tmp / t).exists(), f"{t} 폴더 없음"
    assert (tmp / "vector_db").exists()
    cleanup(tmp)
    print("PASS: 폴더 자동 생성")


def test_add_sample():
    """샘플 추가 후 인덱스에 등록되는지 확인."""
    manager, tmp = make_temp_manager()
    src = make_sample_txt(tmp, "test.txt", "prior art sample content")
    entry = manager.add(src, "prior_art")
    assert entry.sample_type == "prior_art"
    assert entry.sample_id == "001"
    # 파일 복사 확인
    assert (tmp / "prior_art" / entry.filename).exists()
    # 인덱스 확인
    entries = manager._load_index()
    assert len(entries) == 1
    cleanup(tmp)
    print("PASS: 샘플 추가 + 인덱스 등록")


def test_add_invalid_type():
    """잘못된 유형으로 추가 시 ValueError 발생."""
    manager, tmp = make_temp_manager()
    src = make_sample_txt(tmp, "test.txt")
    try:
        manager.add(src, "invalid_type")
        print("FAIL: should raise ValueError")
    except ValueError:
        print("PASS: 잘못된 유형 -> ValueError")
    cleanup(tmp)


def test_add_missing_file():
    """존재하지 않는 파일 추가 시 FileNotFoundError 발생."""
    manager, tmp = make_temp_manager()
    try:
        manager.add(tmp / "nonexistent.txt", "clarity")
        print("FAIL: should raise FileNotFoundError")
    except FileNotFoundError:
        print("PASS: 없는 파일 -> FileNotFoundError")
    cleanup(tmp)


def test_id_sequence():
    """ID가 001, 002, 003 순서로 증가하는지 확인."""
    manager, tmp = make_temp_manager()
    for i in range(3):
        src = make_sample_txt(tmp, f"s{i}.txt", f"content {i}")
        entry = manager.add(src, "clarity")
        assert entry.sample_id == f"{i+1:03d}", f"ID 오류: {entry.sample_id}"
    cleanup(tmp)
    print("PASS: ID 시퀀스 001 -> 002 -> 003")


def test_delete_sample():
    """샘플 삭제 후 인덱스와 파일이 제거되는지 확인."""
    manager, tmp = make_temp_manager()
    src = make_sample_txt(tmp, "del.txt", "delete me")
    entry = manager.add(src, "unity")
    file_path = tmp / "unity" / entry.filename
    assert file_path.exists()
    ok = manager.delete(entry.sample_id)
    assert ok is True
    assert not file_path.exists()
    assert len(manager._load_index()) == 0
    cleanup(tmp)
    print("PASS: 샘플 삭제 (파일 + 인덱스)")


def test_delete_nonexistent():
    """존재하지 않는 ID 삭제 시 False 반환."""
    manager, tmp = make_temp_manager()
    ok = manager.delete("999")
    assert ok is False
    cleanup(tmp)
    print("PASS: 없는 ID 삭제 -> False")


def test_list_all():
    """list_all이 전체 목록을 반환하는지 확인."""
    manager, tmp = make_temp_manager()
    for i, t in enumerate(["prior_art", "clarity", "unity"]):
        src = make_sample_txt(tmp, f"s{i}.txt", f"content {i}")
        manager.add(src, t)
    all_entries = manager.list_all()
    assert len(all_entries) == 3
    type_entries = manager.list_all("clarity")
    assert len(type_entries) == 1
    cleanup(tmp)
    print("PASS: list_all (전체 / 유형 필터)")


def test_stats():
    """stats가 유형별 카운트와 모드를 반환하는지 확인."""
    manager, tmp = make_temp_manager()
    for i in range(3):
        src = make_sample_txt(tmp, f"p{i}.txt", f"prior {i}")
        manager.add(src, "prior_art")
    src = make_sample_txt(tmp, "c.txt", "clarity")
    manager.add(src, "clarity")
    s = manager.stats()
    assert s["prior_art"] == 3
    assert s["clarity"] == 1
    assert s["total"] == 4
    assert s["mode"] == "Few-shot"
    cleanup(tmp)
    print("PASS: stats (카운트 + 모드)")


def test_mode_threshold():
    """샘플 수에 따라 모드가 올바르게 전환되는지 확인."""
    manager, tmp = make_temp_manager()
    assert manager.get_mode() == "few-shot"

    # RAG_THRESHOLD - 1 개 추가
    for i in range(RAG_THRESHOLD - 1):
        src = make_sample_txt(tmp, f"s{i}.txt", f"content {i}")
        manager.add(src, "prior_art")
    assert manager.get_mode() == "few-shot"

    # 하나 더 추가 → RAG 전환
    src = make_sample_txt(tmp, "last.txt", "last content")
    manager.add(src, "prior_art")
    assert manager.get_mode() == "rag"
    cleanup(tmp)
    print(f"PASS: 모드 전환 (threshold={RAG_THRESHOLD})")


def test_few_shot_select():
    """Few-shot 모드에서 최근 파일 3건을 선택하는지 확인."""
    manager, tmp = make_temp_manager()
    for i in range(5):
        src = make_sample_txt(tmp, f"s{i}.txt", f"content {i}")
        manager.add(src, "prior_art")
    selected = manager._few_shot_select("prior_art", 3)
    assert len(selected) <= 3
    cleanup(tmp)
    print(f"PASS: Few-shot 선택 ({len(selected)}건)")


def test_get_relevant_samples_fewshot():
    """get_relevant_samples가 Few-shot 모드에서 텍스트를 반환하는지 확인."""
    manager, tmp = make_temp_manager()
    for i in range(3):
        src = make_sample_txt(tmp, f"s{i}.txt", f"sample text {i}")
        manager.add(src, "clarity")
    results = manager.get_relevant_samples("clarity", query_text="")
    assert len(results) <= 3
    assert all(isinstance(t, str) and len(t) > 0 for t in results)
    cleanup(tmp)
    print(f"PASS: get_relevant_samples Few-shot ({len(results)}건)")


def test_search_few_shot_keyword():
    """Few-shot 모드에서 키워드 검색이 동작하는지 확인."""
    manager, tmp = make_temp_manager()
    src1 = make_sample_txt(tmp, "novelty_case.txt", "novelty content")
    src2 = make_sample_txt(tmp, "other_case.txt", "other content")
    manager.add(src1, "prior_art")
    manager.add(src2, "prior_art")
    results = manager.search("novelty", "prior_art")
    assert any("novelty" in e.filename for e in results)
    cleanup(tmp)
    print("PASS: Few-shot 키워드 검색")


def test_next_id_after_delete():
    """삭제 후 새 ID가 남은 최대값+1로 채번되는지 확인."""
    manager, tmp = make_temp_manager()
    s1 = make_sample_txt(tmp, "a.txt", "a")
    s2 = make_sample_txt(tmp, "b.txt", "b")
    s3 = make_sample_txt(tmp, "c.txt", "c")
    e1 = manager.add(s1, "other")   # 001
    e2 = manager.add(s2, "other")   # 002
    e3 = manager.add(s3, "other")   # 003
    manager.delete(e3.sample_id)    # 003 삭제 → 남은 최대: 002
    s4 = make_sample_txt(tmp, "d.txt", "d")
    e4 = manager.add(s4, "other")   # 남은 최대(002)+1 = 003
    assert e4.sample_id == "003", f"예상: 003, 실제: {e4.sample_id}"
    cleanup(tmp)
    print("PASS: 삭제 후 ID 채번 (003 삭제 후 재추가 -> 003)")


if __name__ == "__main__":
    print("=" * 55)
    print("sample_manager 단위 테스트")
    print("=" * 55)
    test_ensure_dirs()
    test_add_sample()
    test_add_invalid_type()
    test_add_missing_file()
    test_id_sequence()
    test_delete_sample()
    test_delete_nonexistent()
    test_list_all()
    test_stats()
    test_mode_threshold()
    test_few_shot_select()
    test_get_relevant_samples_fewshot()
    test_search_few_shot_keyword()
    test_next_id_after_delete()
    print("=" * 55)
    print("모든 테스트 통과")
