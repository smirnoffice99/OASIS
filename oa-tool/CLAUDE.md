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
