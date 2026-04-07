# Claude Code 시작 프롬프트 — 특허 의견제출통지서 대응 자동화 툴 (최종)

다음 사양으로 특허 의견제출통지서(OA) 대응 자동화 툴을 Python으로 구현해줘.

---

## 1. 프로젝트 개요

한국 특허청 의견제출통지서 PDF를 입력받아, 거절이유별로 변리사와 상호작용하면서
대응 전략을 수립하고, 최종적으로 해외 고객에게 송부할 영문 코멘트 .docx를 생성하는 툴.

핵심 특징:
- 거절이유 유형별로 완전히 다른 분석 흐름 적용
- 각 단계마다 변리사가 검토·승인해야 다음 단계 진행 (Human-in-the-Loop)
- 과거 코멘트 샘플을 학습하여 사무소 고유의 스타일로 영문 코멘트 작성
- LLM API는 교체 가능한 구조로 설계

---

## 2. 입력 파일 구조

cases/{사건번호}/
├── oa.pdf                  ← 의견제출통지서 (필수)
├── spec.pdf                ← 본원 명세서 (필수)
├── claims_en.docx          ← 본원 영문 청구항 (필수)
└── citations/
    ├── D1.pdf
    ├── D2.pdf
    └── ...                 ← 인용문헌 (해당하는 경우)

- 각 분석 단계에서 관련 파일을 직접 읽어 근거를 찾아라.
- 인용문헌 분석 시 반드시 출처(컬럼/단락/페이지)를 명시해라.
- 영문 코멘트 작성 시 claims_en.docx의 청구항 용어를 그대로 사용해라.

---

## 3. 거절이유 유형 분류

거절이유는 아래 4가지 유형으로 분류하고, 유형별로 전혀 다른 Handler를 적용해라.

  유형 A: 선행기술 위반  ← 신규성(제29조 1항) + 진보성(제29조 2항) 통합 처리
  유형 B: 기재불비       ← 특허법 제42조
  유형 C: 단일성 위반    ← 특허법 제45조 (인용발명 있는 경우 포함)
  유형 D: 기타           ← 위 유형에 해당하지 않는 모든 거절이유

신규성 또는 진보성으로 거절한 경우 모두 "유형 A"로 분류하고 동일한 Handler로
처리한다. 분석 결과 출력 시에는 실제 거절 유형(신규성/진보성)을 명시해라.

단일성 위반(유형 C)의 경우, OA 파싱 시 인용문헌 포함 여부를 확인하여
session.json에 has_citations 플래그로 기록하고 분석 흐름을 자동 분기해라.

---

## 4. 거절이유 유형별 분석 로직

### 유형 A: 선행기술 위반 (신규성 + 진보성 통합)

[중요 전제]
한국 특허법상 신규성이 없는 발명에는 항상 진보성도 없다는 거절이유가 함께 제시된다.
따라서 Step 4의 차이점 분석은 신규성/진보성 구분 없이 항상 진보성 기준으로 처리한다.
분석 결과 출력 및 영문 코멘트에는 실제 거절 유형(신규성+진보성)을 병기한다.

Step 1. 본원발명 분석
        - 대상 청구항의 구성요소를 항목별로 정리
        - 각 구성요소의 기술적 의미와 효과 설명
        → 사용자 확인

Step 2. 인용발명 분석
        - 인용문헌(D1, D2 등) 각각에 대해:
          · 관련 구성요소 원문 발췌 (출처: 컬럼/단락/페이지 반드시 명시)
          · 해당 구성요소의 기술적 의미 설명
        → 사용자 확인

Step 3. 구성요소 대비표 작성
        - 본원발명 구성요소 vs 인용발명 대응 구성요소 1:1 대응표
        - 인용문헌이 복수인 경우 (D1+D2 등) 각 열로 구분
        → 사용자 확인

Step 4. 차이점 분석 및 진보성 논거 도출
        (신규성/진보성 구분 없이 항상 아래 기준으로 처리)
        - 구조적 차이점 특정
        - 기능적/효과적 차이점 특정
        - 인용문헌이 복수인 경우: D1+D2 결합의 동기 부재 여부 검토
        - 예측하지 못한 현저한 효과 여부 검토
        - 심사관의 논거 약점 파악
        → 사용자 확인

Step 5. 대응 전략 제안 및 확정
        A) 보정 (청구항 한정으로 차이점 부각)
        B) 의견서 (선행기술과의 차이점 및 진보성 주장)
        C) 보정 + 의견서 병행
        → 사용자 선택 후 상호작용하며 결론 확정


### 유형 B: 기재불비 (특허법 제42조)

※ 인용발명 없음 — 구성요소 대비 및 차이점 분석 불필요

Step 1. 불비 유형 파악
        - 청구항 불명확 (용어 모호, 범위 불명확)
        - 발명의 설명 미뒷받침 (명세서에 근거 없음)
        - 실시가능 요건 미충족
        → 사용자 확인

Step 2. 해당 청구항 + 명세서 대응 부분 분석
        - 심사관이 지적한 부분과 명세서 원문 대조
        - 명세서에 뒷받침 근거가 있는지 확인
        → 사용자 확인

Step 3. 대응 전략 제안 및 확정
        A) 청구항 보정으로 명확화
        B) 의견서로 용어 해석 제시
        C) 명세서 보정 (실시예 추가 등)
        D) 보정 + 의견서 병행
        → 사용자 선택 후 상호작용하며 결론 확정


### 유형 C: 단일성 위반 (특허법 제45조)

[중요 전제]
한국 특허법상 복수의 발명들 간에 인용발명에 비해 개선된 공통 또는 대응되는
기술적 특징(STF)이 없으면 단일성이 없는 것으로 본다.
따라서 단일성 위반 거절에도 인용발명이 제시되는 경우가 있다.
OA 파싱 시 인용문헌 포함 여부를 자동 확인하고,
has_citations 플래그에 따라 아래 두 가지 흐름 중 하나를 자동 선택해라.

[인용발명이 없는 경우 — has_citations: false]

Step 1. 단일성 위반 내용 파악
        - 심사관이 단일성 없다고 판단한 청구항 그룹 파악
        → 사용자 확인

Step 2. STF 분석
        - 각 청구항 그룹 간 공통/대응 특별한 기술적 특징(STF) 공유 여부 검토
        - 심사관 논리의 타당성 검토
        → 사용자 확인

Step 3. 대응 전략 제안 및 확정
        A) 의견서로 단일성 주장 (STF 공유 근거 제시)
        B) 청구항 삭제/보정으로 단일성 확보
        C) 분할출원 검토
        → 사용자 선택 후 상호작용하며 결론 확정

[인용발명이 있는 경우 — has_citations: true]

Step 1. 단일성 위반 내용 및 인용발명 파악
        - 심사관이 단일성 없다고 판단한 청구항 그룹 파악
        - 인용문헌(D1 등) 확인 및 심사관의 STF 부재 논거 파악
        → 사용자 확인

Step 2. 인용발명 대비 STF 분석
        - 인용문헌 관련 구성요소 원문 발췌 (출처: 컬럼/단락/페이지 명시)
        - 각 청구항 그룹이 인용발명에 비해 개선된 공통/대응 STF를
          공유하는지 여부 분석
        - 심사관 논리의 타당성 검토
        → 사용자 확인

Step 3. 대응 전략 제안 및 확정
        A) 의견서로 단일성 주장
           (각 그룹이 인용발명 대비 개선된 공통 STF를 공유한다는 근거 제시)
        B) 청구항 삭제/보정으로 단일성 확보
        C) 분할출원 검토
        → 사용자 선택 후 상호작용하며 결론 확정


### 유형 D: 기타 거절이유

- 유형명과 심사관 지적 내용을 먼저 사용자에게 보여주고
- 어떤 분석이 필요한지 사용자와 협의한 후 진행해라.

---

## 5. 각 Step의 사용자 상호작용 규칙

[핵심 원칙]
- 사용자가 명시적으로 승인("Y" 또는 "승인")해야만 다음 Step으로 진행
- 사용자가 수정을 요청하면 해당 내용을 반영하여 현재 Step 재생성 후 재확인
- 마지막 Step(전략)에서는 결론이 명확히 확정될 때까지 대화를 계속
- 각 Step의 분석 결과는 파일로 저장한 뒤 터미널에 출력

[사용자 입력 처리]
- "Y" 또는 "승인"  → 다음 Step 진행
- 텍스트 입력      → 해당 내용을 반영하여 현재 Step 재생성
- "건너뛰기"       → 해당 Step을 빈 상태로 기록하고 다음으로 진행
- "종료"           → 세션 저장 후 프로그램 종료 (나중에 재개 가능)
- "재검토 N"       → 거절이유 N번을 다시 열어 재처리

---

## 6. 전체 처리 흐름

python main.py
    ↓
사건번호 입력 (예: KR-2024-12345)
    ↓
기존 세션 있으면 이어서 재개 / 없으면 새로 시작
    ↓
[OA 파서] oa.pdf에서 거절이유 목록 자동 추출 + 유형 분류
          단일성의 경우 has_citations 플래그 자동 설정
    ↓
거절이유 목록 출력 + 사용자 확인
  예) #1 선행기술 위반 (신규성+진보성) — 청구항 1, 3, 5 / D1, D2
      #2 기재불비                       — 청구항 7
      #3 단일성 위반 (인용발명 있음)    — 청구항 1~5 vs 6~8 / D1
    ↓
거절이유 #1 — 유형 및 has_citations에 따라 Handler 자동 선택 후 순차 처리
    ↓
거절이유 #2, #3 ... 순차 처리
    ↓
모든 거절이유 완료
    ↓
[샘플 매니저] 유형별 유사 샘플 자동 선택
    ↓
[리포트 생성] 영문 코멘트 .docx 생성
    ↓
cases/{사건번호}/final_comment.docx 저장

---

## 7. 영문 코멘트 스타일 학습 기능

### 7-1. 샘플 폴더 구조

samples/
├── prior_art/          ← 선행기술 위반 (신규성+진보성) 샘플
├── clarity/            ← 기재불비 샘플
├── unity/              ← 단일성 샘플 (인용발명 있는 경우 포함)
├── other/              ← 기타 샘플
└── vector_db/          ← chromadb 로컬 저장소

- 샘플은 .docx 또는 .txt 파일로 저장
- 툴 완성 후에도 파일을 추가하면 자동으로 반영
- 샘플 관리 명령어: python sample_manager.py add <파일경로> --type prior_art

### 7-2. 초기 구현: Few-shot 방식 (샘플 20건 미만)

- report_generator.py에서 해당 유형의 samples/ 폴더를 자동으로 읽음
- 샘플이 3건 이상이면 가장 최근 수정된 3건만 프롬프트에 포함
- 프롬프트 구조:

  아래는 우리 사무소의 실제 코멘트 샘플이다.
  이 스타일, 톤, 문장 구조, 용어 선택을 그대로 따라 작성해라.

  --- 샘플 1 ---
  {sample_01 내용}

  --- 샘플 2 ---
  {sample_02 내용}

  이제 아래 사건의 코멘트를 작성해라:
  {현재 사건 분석 결과 종합}

### 7-3. 확장 구현: RAG 방식 (샘플 20건 이상 시 자동 전환)

- chromadb를 사용하여 샘플을 로컬 벡터DB에 저장 (서버 불필요)
- 현재 사건의 거절이유 유형, 기술분야, 인용문헌 수 등을 기준으로
  유사도 높은 샘플 상위 3건을 자동 선택
- 샘플 수가 20건을 넘는 순간 자동으로 RAG 방식으로 전환
- 벡터DB는 samples/vector_db/ 폴더에 로컬 저장

### 7-4. sample_manager.py 기능

python sample_manager.py add <파일> --type <유형>   ← 샘플 추가 + 벡터화
python sample_manager.py list                       ← 전체 샘플 목록 출력
python sample_manager.py delete <샘플ID>            ← 샘플 삭제
python sample_manager.py search <키워드>            ← 유사 샘플 검색
python sample_manager.py stats                      ← 유형별 샘플 현황

---

## 8. API 설계 (교체 가능하게)

- LLM 호출은 반드시 llm_client.py 한 파일에서만 처리
- provider와 model을 config.yaml로 관리
- Claude / OpenAI / Gemini 전환이 코드 수정 없이 가능하도록 추상화
- 기본값: Claude (claude-sonnet-4-6)

config.yaml 예시:
  provider: claude            # claude / openai / gemini
  model: claude-sonnet-4-6
  api_key_env: ANTHROPIC_API_KEY
  max_tokens: 4096

지원 provider별 모델 예시:
  claude  → claude-sonnet-4-6, claude-haiku-4-5
  openai  → gpt-4o, gpt-4o-mini
  gemini  → gemini-2.5-flash, gemini-2.5-pro

- 각 분석 단계 호출 시 관련 문서 전체를 컨텍스트로 전달
- 시스템 프롬프트는 prompts/ 폴더에서 유형별로 관리
- API 키는 환경변수로만 관리 (코드에 직접 입력 금지)

---

## 9. 세션 저장/복원

cases/{사건번호}/
├── session.json
├── rejection_1/
│   ├── step_1_result.md
│   ├── step_2_result.md
│   ├── step_3_result.md
│   ├── step_4_result.md      ← 유형 A만
│   ├── dialogue.json
│   └── conclusion.md
├── rejection_2/
│   └── ...
└── final_comment.docx

session.json 구조:
  {
    "case_id": "KR-2024-12345",
    "created_at": "...",
    "updated_at": "...",
    "rejections": [
      {
        "id": 1,
        "type": "prior_art",        ← prior_art / clarity / unity / other
        "subtype": "신규성+진보성",  ← 실제 거절 유형 표시용
        "claims": [1, 3, 5],
        "citations": ["D1", "D2"],
        "has_citations": true,       ← 단일성의 인용발명 여부 (유형 C에서 사용)
        "status": "concluded",       ← pending / in_progress / concluded
        "current_step": 5
      }
    ],
    "overall_status": "in_progress"
  }

- 프로그램 재실행 시 session.json을 읽어 중단된 지점부터 재개
- concluded 상태의 거절이유는 건너뛰고 미완료 건부터 시작
- "재검토 N" 명령으로 완료된 거절이유를 다시 열 수 있음

---

## 10. 최종 영문 코멘트 (.docx) 형식

- 고객 송부용 톤: formal, concise
- claims_en.docx의 청구항 용어를 그대로 사용
- 거절이유별 섹션으로 구성:

  1. Rejection Ground 1: Lack of Novelty and Inventive Step — Claims 1, 3, 5
     1.1 Summary of Rejection
     1.2 Our Analysis
         1.2.1 Analysis of the Claimed Invention
         1.2.2 Analysis of the Cited References
         1.2.3 Differences from the Cited References
     1.3 Proposed Response Strategy

  2. Rejection Ground 2: Lack of Clarity — Claim 7
     2.1 Summary of Rejection
     2.2 Our Analysis
     2.3 Proposed Response Strategy

  3. Rejection Ground 3: Lack of Unity of Invention — Claims 1-8
     3.1 Summary of Rejection
     3.2 Our Analysis
     3.3 Proposed Response Strategy

  Overall Strategy (전체 대응 방향 요약)

- python-docx 라이브러리로 생성
- samples/에서 학습한 스타일/톤/용어 선택을 반영

---

## 11. 프로젝트 구조

oa-tool/
├── CLAUDE.md
├── config.yaml
├── main.py
├── oa_parser.py                    ← PDF → 거절이유 추출 + 유형/has_citations 분류
├── llm_client.py
├── session.py
├── report_generator.py
├── sample_manager.py
├── handlers/
│   ├── base_handler.py             ← 공통 상호작용 루프
│   ├── prior_art_handler.py        ← 선행기술 위반 (신규성+진보성 통합)
│   ├── clarity_handler.py          ← 기재불비
│   ├── unity_handler.py            ← 단일성 (has_citations 분기 포함)
│   └── default_handler.py          ← 기타
├── prompts/
│   ├── prior_art.txt
│   ├── clarity.txt
│   ├── unity.txt
│   ├── unity_with_citations.txt    ← 인용발명 있는 단일성 전용
│   └── report.txt
├── samples/
│   ├── prior_art/
│   ├── clarity/
│   ├── unity/
│   ├── other/
│   └── vector_db/
└── cases/

---

## 12. 기술 스택

- Python 3.11+
- anthropic               ← Claude API (기본 LLM)
- openai                  ← OpenAI API (교체 시 사용)
- google-generativeai     ← Gemini API (교체 시 사용)
- pymupdf (fitz)          ← PDF 텍스트 추출
- python-docx             ← .docx 읽기/생성
- pyyaml                  ← config.yaml 파싱
- chromadb                ← 샘플 벡터DB (RAG용)
- sentence-transformers   ← 텍스트 벡터화 (chromadb용)

---

## 13. 구현 순서 및 확인 규칙

아래 순서대로 구현하고,
각 항목 완성 후 반드시 나에게 확인을 받고 다음으로 넘어가라.

1.  프로젝트 구조 생성 + CLAUDE.md + config.yaml
2.  llm_client.py (Claude/OpenAI/Gemini 추상화)
3.  oa_parser.py (거절이유 추출 + 유형 분류 + has_citations 설정) + mock 테스트
4.  session.py (저장/복원)
5.  base_handler.py (공통 상호작용 루프)
6.  prior_art_handler.py (선행기술 위반 — 신규성/진보성 통합, Step 4는 항상 진보성 기준)
7.  clarity_handler.py (기재불비)
8.  unity_handler.py (단일성 — has_citations 분기 포함)
9.  default_handler.py (기타)
10. sample_manager.py (Few-shot → RAG 자동 전환 포함)
11. report_generator.py (샘플 스타일 반영 + .docx 생성)
12. main.py (전체 통합)
13. end-to-end 테스트 (mock 데이터 전체 흐름)

---

## 14. 테스트용 Mock 데이터

실제 PDF가 없으므로, 아래 내용으로 mock 데이터를 만들어 테스트해라.

사건번호: KR-TEST-001

거절이유 #1
- 유형: 선행기술 위반 / subtype: 신규성+진보성
- 대상 청구항: 1, 3, 5항
- 인용문헌: D1 (US10,123,456), D2 (US9,876,543)
- D1 관련 부분: 컬럼 3, 라인 15-40
- D2 관련 부분: 단락 [0045]-[0052]

거절이유 #2
- 유형: 기재불비 (특허법 제42조 4항)
- 대상 청구항: 7항
- 사유: "제1 측위 기준값"의 의미가 불명확

거절이유 #3
- 유형: 단일성 위반 / has_citations: true
- 청구항 그룹 A: 1~5항 (위치측정 방법)
- 청구항 그룹 B: 6~8항 (단말 장치)
- 인용문헌: D1 (US10,123,456)
- 심사관 논거: 그룹 A와 B가 D1에 비해 개선된 공통 STF를 공유하지 않음

mock 파일 생성 위치:
  cases/KR-TEST-001/oa_mock.txt
  cases/KR-TEST-001/spec_mock.txt
  cases/KR-TEST-001/claims_en_mock.txt
  cases/KR-TEST-001/citations/D1_mock.txt
  cases/KR-TEST-001/citations/D2_mock.txt

---

## 15. CLAUDE.md 내용 (프로젝트 Agent 지침)

CLAUDE.md 파일에 아래 내용을 포함해라.

# OA 대응 자동화 툴 — Agent 지침

## 목적
한국 특허청 의견제출통지서 대응 자동화

## 거절이유 유형
- 선행기술 위반 (prior_art): 신규성+진보성 통합. Step 4는 항상 진보성 기준으로 처리
- 기재불비 (clarity): 명세서 내부 분석만, 인용발명 없음
- 단일성 (unity): has_citations 플래그에 따라 흐름 자동 분기
- 기타 (other): 사용자와 협의 후 진행

## 핵심 규칙
- 사용자 승인 없이 절대 다음 단계로 넘어가지 마라
- 인용문헌 분석 시 반드시 출처(컬럼/단락/페이지)를 명시해라
- 영문 코멘트는 claims_en.docx의 용어를 그대로 사용해라
- 모든 분석 결과는 파일로 저장 후 터미널에 출력해라
- API 키는 환경변수로만 관리하고 코드에 직접 입력하지 마라

## 파일 저장 위치
- 분석 결과: cases/{사건번호}/rejection_{n}/
- 최종 출력: cases/{사건번호}/final_comment.docx
- 샘플: samples/{유형}/

## LLM 설정
- config.yaml에서 provider/model 변경 가능
- 기본값: claude / claude-sonnet-4-6
