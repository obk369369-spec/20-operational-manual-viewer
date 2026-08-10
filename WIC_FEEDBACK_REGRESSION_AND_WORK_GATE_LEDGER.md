# WIC FEEDBACK → REGRESSION / CHAT → WORK GATE LEDGER

상태: ACTIVE / NON-NORMATIVE EVIDENCE LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
목적: 과거 대화·파일·사용자 피드백을 실제 도구의 입력·기대출력·회귀테스트로 변환하고, Chat/일반 실행으로 처리 가능한 일을 Work에 넘겨 시간·크레딧을 낭비하지 않도록 실행 증거를 누적한다.

## 영구 파이프라인
`HISTORY_EVIDENCE -> CLASSIFY -> RULE/EXPECTED_OUTPUT -> FIXTURE/ERROR_HASH -> ACTUAL_PATCH -> VERIFY -> READ_BACK -> REUSE -> RESTART_POINT`

## Work gate
G1 Chat/Files, G2 GitHub, G3 일반 runtime 중 하나라도 가능하면 `WORK_DEFER_DENIED`. G1~G3 모두 불가 + 구체적 Work-only blocker + exact handoff package가 있을 때만 `WORK_ELIGIBLE`. 과거규칙 재독해/파일검색/터미널 가능 테스트를 Work로 보내면 `CREDIT_WASTE_FAIL`.

## 처리 장부
### P1 customer DB
- last_processed_evidence: 이메일수집 V5/V4 규칙 + P1 schema/state-machine 구현.
- implementation: `customer_pipeline/customer_db_state_machine.py`.
- verification: GitHub 저장/read-back PASS; runtime fixture 실행 HOLD.
- next_unprocessed_evidence: 실제 회사 customer DB artifact 또는 runner/CI hook이 새로 식별될 때만 재개. 같은 target 검색 반복 금지.
- Work gate: `WORK_DEFER_DENIED`.

### P2 TOOL007 고객 컨택 판단 — 2026-08-10 13:50 KST
- source_file_or_chat:
  - `7번 고객 컨택 판단 도구 5 (새 대화창에서 이어서 진행).txt`
  - `7번 고객 컨택 판단.doc`
  - `7번 고객 컨택 판단 도구 7.txt`
- newly_processed_rules:
  1. 고객 상태 판별 -> 접촉 가능 여부 -> 채널 선택 -> 멘트 생성. 멘트는 마지막.
  2. 현재 재직과 고객 회사의 실제 최신 방향 확인 전 추천자료/멘트 생성 금지.
  3. 일방 발송 메일은 고객 니즈로 과대해석 금지.
  4. CC 이력은 직접 문의/구매처럼 표현 금지.
  5. 오래된 장부 메모는 최초 연락 이유로 사용 금지; 현재 회사/부서 최신 방향 뒤의 보조 맥락으로만 사용.
  6. 연구기관/기업은 자료 추천을 전화보다 먼저 할 수 있음.
  7. 추천자료는 제목/발행사/발행일/링크/유료 여부/거래가능 여부를 검증.
- regression_fixture: `customer_pipeline/tool7_contact_judgment.py::run_fixtures()` 8개.
- error_signatures:
  - `COMPANY_DIRECTION_MISSING`
  - `CURRENT_EMPLOYMENT_UNVERIFIED`
  - `MOVED_OR_LEFT_HOLD`
  - `CONTACT_STOP`
  - `ONE_WAY_NOTICE_NOT_CUSTOMER_NEED`
  - `CC_HISTORY_NOT_DIRECT_INQUIRY`
  - `FREE_REPORT_EXCLUDED`
  - `NON_TRADABLE_PUBLISHER`
- implementation_target: `customer_pipeline/tool7_contact_judgment.py`.
- actual_patch: commit `84497e2c6e4e6778f8482bdbeec84ce45ee37346`.
- verification_method: GitHub exact file read-back 완료; 일반 runtime fixture 실행은 다음 재시작점.
- verification_result: CODE STORED/READ-BACK PASS; FUNCTIONAL PASS HOLD.
- reusable_scope: P1 세 고객군이 P2로 넘어올 때 공통 접촉허용 gate로 재사용 가능. Tool1/Tool6의 비즈니스 규칙으로 무분별 복제 금지.
- last_processed_evidence: 위 3개 Tool7 계열에서 이번에 추출한 상태/접촉허용/이력사용/자료우선 규칙.
- next_unprocessed_evidence: 실제 고객별 성공/실패 사례에서 expected-output fixture 추가; 특히 고객 유형별 채널/분기와 추천자료 `핵심/확장/안전` 역할 검증.
- Work gate:
  - G1 Chat/Files = YES
  - G2 GitHub = YES
  - G3 일반 runtime = YES 가능
  - 판정 = `WORK_DEFER_DENIED`
  - credit_waste_risk = HIGH if deferred now.

## TOOL001
- known: `안내서_전체_연결버전.html` layout/input mapper 후보; v14/RUN은 historical evidence. synthetic title/page/price/link 생성은 `TOOL001_SYNTHETIC_REPORT_DATA`; shell-only PASS는 `TOOL001_SHELL_PASS_WITHOUT_REAL_OUTPUT`.
- next: P2 runtime/handoff 후 실제 공개 보고서 input -> 실제 guide output -> expected 비교 fixture.

## TOOL006
- known: MarketsandMarkets upper-level/indent/merged-split/numeric-only/List-of-*/TOC2/revalidation 문제. 원본->사용자 승인 최종본 golden fixture 회수 필요.
- next: P3/P4 고객 guide가 요구할 때 우선 회수, 이후 batch regression.

## TOOL013
- 37번과 분리. known regression `Publishing Date serial 46145`; Chat/GitHub/runtime 우선. Work defer 금지 상태.

## TOOL037
- 13번과 분리. 한글 상품명/영문명, ISBN/CODE, 행 무결성, 발행사별 구조 fixture화 대상.

## 사용자 역할
관찰자. 과거 오류 재설명, 동일 파일 재전송, 반복 테스트, PASS/FAIL 판정, 규칙 정리, Work 이관 판단을 요구하지 않는다.
