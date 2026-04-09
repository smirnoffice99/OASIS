"""
oa_parser.py — 의견제출통지서 파서

역할:
  1. oa.pdf (또는 oa_mock.txt) 에서 거절이유 목록을 추출
  2. 각 거절이유를 4가지 유형으로 분류
       prior_art  : 신규성(제29조1항) + 진보성(제29조2항) 통합
       clarity    : 기재불비(제42조)
       unity      : 단일성(제45조)
       other      : 기타
  3. 단일성의 경우 인용문헌 포함 여부를 has_citations 플래그로 기록
  4. 파싱 결과를 RejectionInfo 리스트로 반환
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# 데이터 모델
# ---------------------------------------------------------------------------

@dataclass
class RejectionInfo:
    """거절이유 하나를 나타내는 데이터 클래스."""

    id: int                          # 거절이유 번호 (1-based)
    type: str                        # prior_art / clarity / unity / other
    subtype: str                     # 실제 거절 유형 표시용 (예: "신규성+진보성")
    claims: List[int]                # 대상 청구항 번호 목록 ([-1] = 전항)
    citations: List[str]             # 인용문헌 ID 목록 (예: ["D1", "D2"])
    has_citations: bool              # 단일성 위반 시 인용발명 포함 여부
    raw_text: str                    # 해당 거절이유 원문
    examiner_opinion: str = ""       # 심사관 의견 부분만 추출

    def display_label(self) -> str:
        """터미널 출력용 한 줄 레이블."""
        citations_str = (
            " / " + ", ".join(self.citations) if self.citations else ""
        )
        if self.claims == [-1]:
            claims_str = "전항"
        else:
            claims_str = ", ".join(str(c) for c in self.claims)
        unity_flag = (
            " (인용발명 있음)" if self.type == "unity" and self.has_citations
            else " (인용발명 없음)" if self.type == "unity"
            else ""
        )
        return (
            f"#{self.id} {self.subtype}{unity_flag}"
            f" — 청구항 {claims_str}{citations_str}"
        )


# ---------------------------------------------------------------------------
# 분류 규칙 (법조항 우선, 키워드 폴백)
# ---------------------------------------------------------------------------

_PRIOR_ART_PATTERNS = [
    r"제\s*29조\s*제?\s*[12]항",
    r"신규성",
    r"진보성",
    r"선행\s*기술",
    r"인용\s*발명",
]

_CLARITY_PATTERNS = [
    r"제\s*42조",
    r"기재\s*불비",
    r"명확\s*하지\s*않",
    r"불명확",
    r"미뒷받침",
    r"뒷받침.*없",
    r"실시\s*가능",
    r"기재\s*요건",
]

_UNITY_PATTERNS = [
    r"제\s*45조",
    r"단일성",
    r"단일\s*성",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text) for p in patterns)


def _classify(block_text: str) -> tuple[str, str]:
    """
    거절이유 블록 텍스트를 분석하여 (type, subtype) 을 반환한다.
    법조항 번호 우선 → 키워드 폴백 순서로 판단한다.
    """
    # 1순위: 법조항 번호 기반 (가장 신뢰도 높음)
    if re.search(r"제\s*45조", block_text):
        return "unity", "단일성 위반"

    if re.search(r"제\s*29조", block_text):
        has_novelty = bool(re.search(r"신규성|제\s*29조\s*제?\s*1항", block_text))
        has_inv_step = bool(re.search(r"진보성|제\s*29조\s*제?\s*2항", block_text))
        if has_novelty and has_inv_step:
            return "prior_art", "신규성+진보성"
        if has_novelty:
            return "prior_art", "신규성"
        if has_inv_step:
            return "prior_art", "진보성"
        return "prior_art", "선행기술 위반"

    if re.search(r"제\s*42조", block_text):
        return "clarity", "기재불비"

    # 2순위: 키워드 기반 폴백
    has_novelty = bool(re.search(r"신규성", block_text))
    has_inv_step = bool(re.search(r"진보성", block_text))

    if has_novelty and has_inv_step:
        return "prior_art", "신규성+진보성"
    if has_novelty:
        return "prior_art", "신규성"
    if has_inv_step:
        return "prior_art", "진보성"

    if _matches_any(block_text, _UNITY_PATTERNS):
        return "unity", "단일성 위반"

    if _matches_any(block_text, _CLARITY_PATTERNS):
        return "clarity", "기재불비"

    return "other", "기타 거절이유"


# ---------------------------------------------------------------------------
# 청구항 번호 추출
# ---------------------------------------------------------------------------

def _extract_claims(text: str) -> List[int]:
    """
    텍스트에서 청구항 번호를 추출한다.

    처리 형식:
      - "청구항 전항" / "전 청구항" → [-1] (전항 표시)
      - "청구항 제1항 내지 제20항, 제31항 내지 제52항" (제N항 형식, 다중 범위)
      - "청구항 제58항, 제67항" (제N항 개별 열거)
      - "청구항 1~5", "청구항 1 내지 5" (숫자만, 구형 호환)

    PDF 추출 보정:
      - _normalize_pdf_text()가 한글 간 공백을 제거하여 "청구항제1항" 형태가 되므로
        "청구항" 뒤의 공백을 선택적(\s*)으로 처리한다.
      - PDF 테이블에서 숫자가 "5 2" 처럼 분리될 수 있어 인접 숫자 간 공백을 먼저 제거한다.
    """
    # PDF 테이블 추출 시 숫자 사이에 삽입된 공백 제거 ("5 2" → "52")
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    # 한 번으로 충분하지 않을 수 있으므로 재적용 ("1 2 3" → "123")
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)

    claims: set[int] = set()

    # 전항 체크
    if re.search(r"청구항\s*전\s*항|전\s*청구항", text):
        return [-1]

    # ── 제N항 형식 (현행 한국 특허청 표기) ──────────────────────────────
    # "청구항" 뒤에 오는 "제N항 [내지 제M항] [, 제K항 ...]" 덩어리를 통째로 캡처
    # \s* 사용: 정규화로 "청구항제1항"처럼 공백이 제거된 경우도 처리
    claim_section_re = re.compile(
        r"청구항\s*"
        r"((?:제\s*\d+\s*항\s*(?:내지\s*제\s*\d+\s*항)?\s*(?:[,、및]\s*)?)+)"
    )
    for m in claim_section_re.finditer(text):
        chunk = m.group(1)
        # 범위 처리: "제N항 내지 제M항"
        for rm in re.finditer(r"제\s*(\d+)\s*항\s*내지\s*제\s*(\d+)\s*항", chunk):
            n1, n2 = int(rm.group(1)), int(rm.group(2))
            if n1 < n2 and (n2 - n1) < 500:
                claims.update(range(n1, n2 + 1))
        # 개별 항: "제N항"
        for im in re.finditer(r"제\s*(\d+)\s*항", chunk):
            claims.add(int(im.group(1)))

    # ── 구형 형식 (하위 호환) ────────────────────────────────────────────
    # "청구항 1~5" 또는 "청구항 1 내지 5"
    for m in re.finditer(r"청구항\s*(\d+)\s*(?:~|내지|–|-)\s*(\d+)", text):
        start, end = int(m.group(1)), int(m.group(2))
        if start < end and (end - start) < 500:
            claims.update(range(start, end + 1))

    # "청구항 1, 3, 5항" (숫자만 열거)
    for m in re.finditer(r"청구항\s*([\d,\s]+)항?", text):
        raw = m.group(1)
        # 숫자가 너무 많으면 청구항 번호가 아닐 가능성이 높으므로 제한
        nums = re.findall(r"\d+", raw)
        if len(nums) <= 20:
            for num_str in nums:
                n = int(num_str)
                if 1 <= n <= 999:
                    claims.add(n)

    return sorted(claims)


# ---------------------------------------------------------------------------
# 인용문헌 추출
# ---------------------------------------------------------------------------

def _extract_citations(text: str) -> List[str]:
    """
    텍스트에서 인용문헌 ID를 추출한다.
    - "D1", "D2" 형식 (내부 표기)
    - "인용발명 1", "인용발명 2" 형식 → D1, D2 로 변환
    """
    seen: set[str] = set()
    result: List[str] = []

    def _add(key: str) -> None:
        if key not in seen:
            seen.add(key)
            result.append(key)

    # "D1", "D2" 스타일
    for m in re.finditer(r"\bD(\d+)\b", text):
        _add(f"D{m.group(1)}")

    # "인용발명 1", "인용발명 2" 스타일 → D1, D2
    for m in re.finditer(r"인용\s*발명\s*(\d+)", text):
        _add(f"D{m.group(1)}")

    # "인용문헌 1", "인용문헌 2" 스타일 → D1, D2
    for m in re.finditer(r"인용\s*문헌\s*(\d+)", text):
        _add(f"D{m.group(1)}")

    return result


# ---------------------------------------------------------------------------
# 심사관 의견 추출
# ---------------------------------------------------------------------------

def _extract_examiner_opinion(block_text: str) -> str:
    """
    블록 텍스트에서 '[심사관 의견]' 섹션 이후의 내용을 추출한다.
    """
    m = re.search(r"\[심사관\s*의견\](.*)", block_text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


# ---------------------------------------------------------------------------
# 텍스트 읽기 (PDF 우선, 없으면 mock .txt)
# ---------------------------------------------------------------------------

def _ocr_page(page, llm_client) -> str:
    """이미지 기반 PDF 페이지를 LLM Vision으로 텍스트를 추출한다."""
    if llm_client is None:
        return ""
    try:
        pixmap = page.get_pixmap(dpi=300)
        return llm_client.ocr_image(pixmap.tobytes("png"))
    except Exception as e:
        print(f"[경고] LLM OCR 실패: {e}")
        return ""


def _normalize_pdf_text(text: str) -> str:
    """
    PDF 추출 시 한글 음절 사이에 삽입되는 공백을 제거한다.
    예) "구 체 적 인 거 절 이 유" → "구체적인거절이유"
    """
    pattern = re.compile(r'(?<=[\uAC00-\uD7A3]) (?=[\uAC00-\uD7A3])')
    prev = None
    while prev != text:
        prev = text
        text = pattern.sub('', text)
    return text


def _read_oa_text(case_dir: Path, llm_client=None) -> str:
    """
    case_dir에서 OA 텍스트를 읽어 반환한다.
    우선순위: oa.pdf → oa_mock.txt

    Args:
        llm_client: 이미지 기반 PDF 페이지 OCR에 사용할 LLMClient (없으면 OCR 건너뜀)
    """
    pdf_path = case_dir / "oa.pdf"
    if pdf_path.exists():
        try:
            import fitz  # type: ignore  # pymupdf
            doc = fitz.open(str(pdf_path))
            pages = []
            ocr_applied = False
            for page in doc:
                # "text" 모드: 레이아웃 보존, 줄바꿈 유지
                text = page.get_text("text")
                if text.strip():
                    pages.append(text)
                else:
                    pages.append(_ocr_page(page, llm_client))
                    ocr_applied = True
            doc.close()
            if ocr_applied:
                print("[정보] 이미지 기반 PDF에 LLM OCR을 적용했습니다: oa.pdf")
            text = _normalize_pdf_text("\n".join(pages))
            if text.strip():
                return text
            print("[경고] PDF에서 텍스트를 추출하지 못했습니다 (이미지 기반 PDF이며 LLM OCR도 실패).")
        except ImportError:
            print("[경고] pymupdf(fitz) 미설치 — oa_mock.txt로 대체합니다.")
        except Exception as e:
            print(f"[경고] PDF 읽기 실패: {e} — oa_mock.txt로 대체합니다.")

    mock_path = case_dir / "oa_mock.txt"
    if mock_path.exists():
        return mock_path.read_text(encoding="utf-8")

    raise FileNotFoundError(
        f"{case_dir} 에서 oa.pdf 또는 oa_mock.txt 를 찾을 수 없습니다."
    )


# ---------------------------------------------------------------------------
# 심사결과 요약표 파싱 (청구항 목록 신뢰도 높음)
# ---------------------------------------------------------------------------

def _parse_summary_table(oa_text: str) -> dict[int, List[int]]:
    """
    [심사결과] 섹션의 요약표에서 거절이유별 청구항 목록을 추출한다.

    PDF 추출 시 표의 각 셀이 별도 줄로 분리되는 형식을 처리한다.
    예)
      1
      청구항 전항
      특허법 제45조 ...
      2
      청구항 제1항 내지 제20항, 제31항 내지
      제52항
      특허법 제29조제2항
      ...

    반환: {거절이유번호: 청구항목록}
    """
    result: dict[int, List[int]] = {}

    # [심사결과] ~ [구체적인 거절이유] 사이 섹션 추출
    section_match = re.search(
        r"\[심사\s*결과\](.*?)\[구체적인\s*거절이유\]",
        oa_text,
        re.DOTALL,
    )
    if not section_match:
        return result

    lines = [line.strip() for line in section_match.group(1).split("\n")]

    i = 0
    while i < len(lines):
        line = lines[i]

        # 거절이유 순번: 1~20 사이의 단독 숫자
        if re.match(r"^\d{1,2}$", line) and 1 <= int(line) <= 20:
            num = int(line)
            claim_parts: list[str] = []
            j = i + 1

            while j < len(lines):
                nxt = lines[j]
                if not nxt:
                    j += 1
                    continue
                # 다음 순번 또는 법조항 → 중단
                if re.match(r"^\d{1,2}$", nxt) and 1 <= int(nxt) <= 20:
                    break
                if nxt.startswith("특허법"):
                    break
                # 헤더 행 건너뜀
                if re.match(r"^(순번|거절이유|관련\s*법|□)", nxt):
                    j += 1
                    continue
                claim_parts.append(nxt)
                j += 1

            if claim_parts:
                combined = " ".join(claim_parts)
                if "청구항" in combined:
                    result[num] = _extract_claims(combined)

        i += 1

    return result


# ---------------------------------------------------------------------------
# 거절이유 블록 분할
# ---------------------------------------------------------------------------

# 폴백용: "거절이유 N" 패턴
_REJECTION_SPLIT_RE = re.compile(
    r"거절\s*이유\s*(\d+)",
    re.IGNORECASE,
)

# "[구체적인 거절이유]" 섹션 내 번호 단락 패턴
# 예) "1. 이 출원은 ...", "2. 이 출원의 ..."
_NUMBERED_PARA_RE = re.compile(
    r"^\s*(\d+)\.\s+이\s*출원",
    re.MULTILINE,
)


def _split_rejection_blocks(oa_text: str) -> list[tuple[int, str]]:
    """
    OA 전문을 거절이유별 블록으로 분할한다.

    전략 1 (우선): [구체적인 거절이유] 섹션을 찾아 번호 단락("N. 이 출원은/의...")으로 분할
    전략 2 (폴백): "거절이유 N" 패턴으로 분할

    반환값: [(거절이유번호, 블록텍스트), ...]
    """
    # ── 전략 1: [구체적인 거절이유] 섹션 + 번호 단락 ────────────────────
    detail_match = re.search(
        r"\[구체적인\s*거절이유\](.*?)(?=\[첨\s*부\]|\Z)",
        oa_text,
        re.DOTALL,
    )
    if detail_match:
        detail = detail_match.group(1)
        positions = [
            (int(m.group(1)), m.start())
            for m in _NUMBERED_PARA_RE.finditer(detail)
        ]
        if positions:
            blocks: list[tuple[int, str]] = []
            for i, (num, start) in enumerate(positions):
                end = positions[i + 1][1] if i + 1 < len(positions) else len(detail)
                blocks.append((num, detail[start:end]))
            return blocks
        # 번호 단락 없음 — 구 형식 OA: 섹션 전체를 거절이유 1번으로 처리
        if detail.strip():
            return [(1, detail)]

    # ── 전략 2: 폴백 — "거절이유 N" 패턴 ───────────────────────────────
    positions2 = [
        (int(m.group(1)), m.start())
        for m in _REJECTION_SPLIT_RE.finditer(oa_text)
    ]
    if not positions2:
        return []

    blocks2: list[tuple[int, str]] = []
    for i, (num, start) in enumerate(positions2):
        end = positions2[i + 1][1] if i + 1 < len(positions2) else len(oa_text)
        blocks2.append((num, oa_text[start:end]))
    return blocks2


# ---------------------------------------------------------------------------
# 공개 함수
# ---------------------------------------------------------------------------

def parse_oa(case_dir: str | Path, llm_client=None) -> List[RejectionInfo]:
    """
    OA 파일을 파싱하여 RejectionInfo 리스트를 반환한다.

    Args:
        case_dir:   cases/{사건번호}/ 디렉토리 경로
        llm_client: 이미지 기반 PDF OCR에 사용할 LLMClient (없으면 OCR 건너뜀)

    Returns:
        List[RejectionInfo]  거절이유 목록 (id 순 정렬)

    Raises:
        FileNotFoundError: OA 파일이 없는 경우
    """
    case_dir = Path(case_dir)
    oa_text = _read_oa_text(case_dir, llm_client)
    blocks = _split_rejection_blocks(oa_text)

    if not blocks:
        # 전체 텍스트를 디버그 파일로 저장
        debug_path = case_dir / "oa_debug.txt"
        try:
            debug_path.write_text(oa_text, encoding="utf-8")
        except Exception:
            pass
        preview = oa_text[:500].replace("\n", " ") if oa_text else "(빈 텍스트)"
        raise ValueError(
            "OA 텍스트에서 거절이유를 찾을 수 없습니다. "
            "문서 형식을 확인해주세요.\n"
            f"전체 추출 텍스트가 {debug_path} 에 저장되었습니다.\n"
            f"[추출된 텍스트 앞부분]: {preview}"
        )

    # 요약표에서 청구항 목록 선추출 (상세 블록보다 신뢰도 높음)
    summary_claims = _parse_summary_table(oa_text)

    rejections: List[RejectionInfo] = []

    for num, block in blocks:
        rtype, subtype = _classify(block)
        # 요약표 청구항 우선, 없으면 블록에서 추출
        claims = summary_claims.get(num) or _extract_claims(block)
        citations = _extract_citations(block)
        examiner_opinion = _extract_examiner_opinion(block)

        # 단일성의 경우 인용문헌 포함 여부 판단
        has_citations = bool(citations) if rtype == "unity" else False

        rejections.append(
            RejectionInfo(
                id=num,
                type=rtype,
                subtype=subtype,
                claims=claims,
                citations=citations,
                has_citations=has_citations,
                raw_text=block.strip(),
                examiner_opinion=examiner_opinion,
            )
        )

    return sorted(rejections, key=lambda r: r.id)


def print_rejection_summary(rejections: List[RejectionInfo]) -> None:
    """거절이유 목록을 터미널에 출력한다."""
    print("\n" + "=" * 60)
    print("  거절이유 목록")
    print("=" * 60)
    for r in rejections:
        print(f"  {r.display_label()}")
    print("=" * 60 + "\n")
