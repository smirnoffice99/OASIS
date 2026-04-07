"""
test_oa_parser.py — oa_parser.py mock 테스트
실행: python test_oa_parser.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from oa_parser import parse_oa, print_rejection_summary, RejectionInfo


CASE_DIR = Path(__file__).parent / "cases" / "KR-TEST-001"


def assert_equal(label, actual, expected):
    if actual != expected:
        print(f"  [FAIL] {label}: expected={expected!r}, got={actual!r}")
        return False
    print(f"  [PASS] {label}: {actual!r}")
    return True


def run_tests():
    print("\n" + "=" * 60)
    print("  oa_parser.py mock 테스트 — KR-TEST-001")
    print("=" * 60)

    rejections = parse_oa(CASE_DIR)
    print_rejection_summary(rejections)

    all_pass = True

    # ── 거절이유 개수 ──────────────────────────────────────────
    all_pass &= assert_equal("거절이유 수", len(rejections), 3)

    # ── 거절이유 #1: prior_art ─────────────────────────────────
    r1: RejectionInfo = rejections[0]
    print(f"\n[거절이유 #1]")
    all_pass &= assert_equal("id", r1.id, 1)
    all_pass &= assert_equal("type", r1.type, "prior_art")
    all_pass &= assert_equal("subtype", r1.subtype, "신규성+진보성")
    all_pass &= assert_equal("claims", r1.claims, [1, 3, 5])
    all_pass &= assert_equal("citations", r1.citations, ["D1", "D2"])
    all_pass &= assert_equal("has_citations", r1.has_citations, False)  # unity 아님
    all_pass &= assert_equal("examiner_opinion 존재", bool(r1.examiner_opinion), True)

    # ── 거절이유 #2: clarity ───────────────────────────────────
    r2: RejectionInfo = rejections[1]
    print(f"\n[거절이유 #2]")
    all_pass &= assert_equal("id", r2.id, 2)
    all_pass &= assert_equal("type", r2.type, "clarity")
    all_pass &= assert_equal("subtype", r2.subtype, "기재불비")
    all_pass &= assert_equal("claims", r2.claims, [7])
    all_pass &= assert_equal("citations", r2.citations, [])
    all_pass &= assert_equal("has_citations", r2.has_citations, False)

    # ── 거절이유 #3: unity (인용발명 있음) ────────────────────
    r3: RejectionInfo = rejections[2]
    print(f"\n[거절이유 #3]")
    all_pass &= assert_equal("id", r3.id, 3)
    all_pass &= assert_equal("type", r3.type, "unity")
    all_pass &= assert_equal("subtype", r3.subtype, "단일성 위반")
    all_pass &= assert_equal("claims (1~8 범위)", set(r3.claims), {1,2,3,4,5,6,7,8})
    all_pass &= assert_equal("citations", r3.citations, ["D1"])
    all_pass &= assert_equal("has_citations", r3.has_citations, True)

    # ── display_label 형식 ────────────────────────────────────
    print(f"\n[display_label 확인]")
    print(f"  r1: {r1.display_label()}")
    print(f"  r2: {r2.display_label()}")
    print(f"  r3: {r3.display_label()}")

    # ── raw_text 존재 확인 ────────────────────────────────────
    print(f"\n[raw_text 길이]")
    for r in rejections:
        all_pass &= assert_equal(f"  r{r.id} raw_text 존재", len(r.raw_text) > 0, True)

    print("\n" + "=" * 60)
    if all_pass:
        print("  모든 테스트 통과 ✓")
    else:
        print("  일부 테스트 실패 ✗")
    print("=" * 60 + "\n")

    return all_pass


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
