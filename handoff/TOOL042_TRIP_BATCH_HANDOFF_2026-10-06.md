# TOOL042 출장 배치 / 다음 대화창 인계 — 2026-10-06

상태: ACTIVE HANDOFF
기준 계약: /CUSTOMER_GUIDE_OUTPUT_LOCK.md 최신 원격본
목적: 사장님 출장 대상 기관의 현재 조직도 + 고객 매일장부/거래이력 + 시장보고서/공학도서 자산을 한 번에 대조하여 고객별 실제 제시자료를 만들고, 고객/자료/인쇄 중복을 제거한다.

## A. 이번 작업
1. 출장 대상 기관의 최신 조직도를 기준으로 관련 고객 전수 목록을 만든다.
2. 기존 CUSTOMER_ID와 대조한다. 같은 고객이 다른 작업건에 있어도 새 ID를 만들지 않고 기존 ledger에 TASK_ID만 추가한다.
3. 고객 매일장부, 메일, 문의, 견적, 구매, 회신, 과거 발송 정확 타이틀을 대조한다.
4. 현재 업무와 실제 거래행동을 근거로 시장보고서 / 공학도서 / 혼합 / HOLD를 판정한다.
5. 사용자가 제공하는 시장보고서 ZIP, 2025 공학도서 ZIP, 2026 공학도서 ZIP을 먼저 사용한다.
6. 각 ZIP은 수신 즉시 open -> entry count -> manifest -> hash/index -> CUSTOMER_ID mapping을 검사하고 manifest/index를 지속 저장한다.
7. 내부 자산에서 적합자료가 부족할 때만 외부 신규자료를 조사한다. 시장보고서는 원발행사 동일 상세페이지의 제목/발행사/페이지/정가/발행일/URL/실제 TOC/보고서정보를 검증한다.
8. 공학도서는 공학도서 GOLDEN FORMAT과 최신 2025~2026 우선 규칙을 적용한다.

## B. 출력은 2층으로 분리
### 1층 — 사장님 출장용 기관별 압축표
CUSTOMER_ID | 고객 | 현재부서·직급 | 거래/관심 핵심근거 | 자료유형 | 실제 추천 타이틀 1~N | GUIDE_ASSET_ID | PRINT_ASSET_ID | 상태
기관별로 한 화면에서 훑을 수 있게 만들고, 긴 안내서 본문을 표 안에 넣지 않는다.

### 2층 — 사용자가 Word 수동안내서에 바로 붙이는 복붙 블록
사용자가 샘플 승인 후 RENDER_SCHEMA_VERSION을 고정한다. 승인된 모양과 다른 출력은 금지한다.
시장보고서 기본 순서:
정확한 영문 전체 제목
빈 줄
전체 한글 제목
빈 줄
◇ 발행사: [발행사] ( [Pages] Pages ) ◇ 정가: $[가격]
◇ 발행일: [YYYY년 MM월 DD일/확인범위] -PDF- ◆ 공급가격:        원
공식 상세 URL
목차:
공식 TOC 시작부터 공개 마지막 항목까지 번호/문구/순서/계층 그대로
보고서 정보:
동일 공식 상세페이지의 실제 원문만 한국어 번역
공급가격은 사용자 값이 없으면 공란.

공학도서는 CUSTOMER_GUIDE_OUTPUT_LOCK의 공학도서 GOLDEN FORMAT을 사용하고 시장보고서의 -PDF-/발행일 형식을 임의 혼합하지 않는다.

## C. TOC 절대 규칙
- Report Scope/탭/메뉴를 TOC로 오인 금지.
- 채택 SOURCE_ID 하나의 실제 공식 TOC만 사용.
- 다른 사이트에서 목차 보충/짜깁기 금지.
- 시작부터 공개 마지막 항목까지 전수 회수.
- 원문의 번호/문구/순서/계층 보존.
- 번호는 자동목록이 아니라 복사 가능한 평문 문자열.
- 하위단계는 들여쓰기.
- 임의 depth 제한, 요약, 중간절단, '[계속]' placeholder 금지.
- TOC END를 확인하지 못하면 완성본 출력 금지.

## D. 출력 책임 / fail-closed
사용자에게 보여주기 전에 내부 생성본 -> 승인 Golden Sample 비교 -> 사실값 검증 -> TOC 종단검사 -> 고객 중복/자료 중복 -> 렌더 비교를 모두 통과해야 한다.
한 항목이라도 FAIL이면 내부에서 수정/대체/재검증하고, 해결 못한 부분만 HOLD로 보고한다.
사용자가 최종본에서 같은 형식오류를 발견하면 사용자 검수 문제가 아니라 OUTPUT_GATE_FAILURE다. PASS 취소 -> failure evidence -> regression sample -> 동일 원인 의존 출력 전수점검 -> 수정 -> 재검증한다.

## E. 고객/자료/인쇄 중복
- CUSTOMER_ID = 전역 고객 dedup key. 동일 고객의 다른 작업건은 TASK_ID로 누적.
- GUIDE_ASSET_ID = 안내서 원본 dedup key. 같은 안내서가 여러 고객에게 적합해도 원본 1개.
- PRINT_ASSET_ID = 출장 인쇄 dedup key. 동일 안내서는 원칙적으로 1부만 출력하고 여러 고객 행이 같은 PRINT_ASSET_ID를 참조한다.
- 고객별 개인화 표지/메모가 반드시 다를 때만 CUSTOMER_ID+GUIDE_ASSET_ID 별도 인쇄.
- 이미 발송/구매/견적한 동일 자료 및 단순 업데이트판은 고객별 exclusion set에서 제외.

## F. ZIP 실패 진단
ZIP을 못 열면 '못 연다'로 끝내지 않는다. corruption / encryption·unsupported archive / retrieval-materialization / runtime-container / parser-index를 구분하여 evidence로 남긴다. 원본 등록정보는 유지한다.

## G. 기존 확인된 핵심 오류와 회귀기준
- 규칙을 GitHub에 기록만 하고 출력에서 실행하지 않은 오류가 반복됐다.
- Carbon-Carbon 안내서 소실, 제목 축약, 페이지 임의값, TOC 과도/누락, 다른 사이트 TOC 혼합 등이 실제 실패 사례다.
- 수동 안내서 GOLDEN SAMPLE + SELECTED-SET LOCK을 유지한다.
- 이미 고른 자료의 일부 필드가 미확인이면 자료 자체를 삭제/대체하지 말고 그 필드만 HOLD한다.
- 실제 발송본/사용자 수동본은 해당 유형 회귀검증 정답으로 우선한다.

## H. 플랫폼 상태를 과장하지 말 것
GitHub에 규칙이 존재하는 것과 모든 일반 Chat에서 자동 실행되는 것은 기술적으로 동일하지 않다.
이번에 단순화한 운영원칙은 하나다: TOOL042 고객안내 작업은 /CUSTOMER_GUIDE_OUTPUT_LOCK.md 최신 원격본을 선조회하지 못하면 출력 금지.
플랫폼 전역 자동상속 E2E가 실제 검증되기 전에는 VERIFIED라고 부르지 않는다.

## I. 다른 작업건도 누락 금지
이번 출장건만 단독으로 기억하지 않는다. WIC 상위 작업은 기존 번호체계/체크포인트를 유지한다: 1 안내서, 6 목차, 7 컨택판단, 9/19/24/25 콘텐츠, 12/14/19 SNS, 13 업로드, 21/23 조사, 28 운영센터, 30-2 13번검증, 34 타워, 41 상태, 42 발송/고객안내, 43 소형앱, 44 조달·검증, 45 기록, 46/47 오류·피드백, 48 부품DB.
출장 배치는 TOOL042의 신규 TASK이며 다른 TASK의 완료/HOLD/잔여상태를 덮어쓰지 않는다.

## J. 다음 대화창 시작문
아래 한 문장으로 재개하되, 실제 작업 전에 최신 GitHub 계약/인계본을 read-back한다:
"WIC 계속. 2026-10-06 TOOL042 출장 배치 인계본과 CUSTOMER_GUIDE_OUTPUT_LOCK 최신 원격본을 먼저 read-back하고, 기존 CUSTOMER_ID/TASK ledger와 중복 제거한 뒤 이어가. 이전 설명을 나에게 다시 요구하지 마라. 시장보고서 ZIP과 2025·2026 공학도서 ZIP을 받으면 즉시 manifest/hash/index를 만들고 기관별 고객 전수매칭을 진행한다. 사용자 승인 전에는 최종 배치 출력하지 말고 먼저 소수 고객의 실제 타이틀+완전 TOC 포함 복붙 샘플을 출력게이트 통과 후 보여라."

## K. 다음 입력
사용자가 보내면 되는 핵심 자료:
1. 고객별 폴더 ZIP이 있으면 그대로: 폴더명 권장 CUSTOMER_ID_기관_이름, 내부에는 실제 안내서 원본.
2. 시장보고서 원본 ZIP.
3. 2025 공학도서 ZIP.
4. 2026 공학도서 ZIP.
5. 고객 매일장부/거래기록이 현재 Library/기존 기록에서 회수되지 않을 때만 추가 요청. 먼저 기존 자료를 검색한다.

완료조건: CUSTOMER_TOTAL=CHECKED, SKIPPED=0, 고객별 중복검사 PASS, SOURCE/TOC/메타데이터 PASS, GUIDE_ASSET dedup PASS, PRINT_ASSET dedup PASS, 승인된 RENDER_SCHEMA 회귀검증 PASS.
