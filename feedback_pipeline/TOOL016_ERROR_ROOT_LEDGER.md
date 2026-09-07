# TOOL016 ERROR ROOT LEDGER — 16번 중앙 오류·원인 수집장부

상태: ACTIVE / INCREMENTAL
기준일: 2026-09-07
목적: WIC 각 TOOL/대화창에서 반복된 오류와 도구가 스스로 발견한 오류를 16번이 중앙 수집하고, 원인(ROOT)별로 묶어 기존 층을 먼저 보강한다. 새 층은 기존 층으로 막을 수 없는 공통오류에 한해서만 검토한다.

## 강제 운영순서
`각 TOOL 오류수집 → 사용자발견/자가발견 구분 → ROOT 원인 → 재발 여부 → 어느 기존 층이 잡았어야 했는지 → 기존 층 최소보강 → 실제 과거 실패사례 재시험 → 효과 확인 → 다음 묶음`

- 한꺼번에 전체 WIC를 수정하지 않는다.
- 각 묶음에서 실제 개선효과를 확인한 뒤 다음 묶음으로 간다.
- 44번은 첫 수단이 아니다. `16번 원인분석 → 기존 층 보강 → 필요한 기능이 없을 때 TOOL044` 순서다.
- 기존 PASS/VERIFIED/DEPLOYED_PASS는 직접 영향이 없으면 SKIP_REUSE한다.
- 오류수집 자체와 코드/층 수정은 분리한다. 원인증거 없이 공통층을 임의 변경하지 않는다.

## 단계별 순서
### 1차
TOOL041 → TOOL007 → TOOL042

### 2차
TOOL006 → TOOL001 → TOOL009 → TOOL013

### 3차
TOOL014 → TOOL012 → 기타 현재 운영 TOOL

### 4차
나머지 WIC 대화창/도구

### 5차
여러 TOOL에서 반복된 ROOT만 공통층 보강 또는, 기존 층으로 차단 불가가 실제 증명된 경우에만 신규층 검토

---

# 1차 수집 — TOOL041 / TOOL007 / TOOL042

## TOOL041 — 고객정보 수집·검증

### 사용자/실사용에서 반복 확인된 오류 후보
1. 현재 재직·부서·직급·담당업무 근거가 약한데 다음 단계로 넘길 위험.
2. 회사 전체 사업방향과 고객 개인의 실제 현재 관심분야가 섞일 위험.
3. 과거 정보와 현재 정보가 섞여 옛 직책/업무를 현재 사실처럼 사용할 위험.

### 도구/Work 자체점검에서 확인된 오류·방어 필요
1. VERIFIED되지 않은 고객정보를 downstream으로 넘기면 안 됨.
2. 실제 고객 현재 관심근거가 없으면 임의로 채우지 말고 HOLD해야 함.

### ROOT 후보
- ROOT-CUST-01: `발견된 정보`와 `현재 사실로 검증된 정보`의 경계 부족.
- ROOT-CUST-02: `회사/부서 방향`과 `개인 현재 관심`의 경계 부족.
- ROOT-CUST-03: `과거 사실`과 `현재 사실`의 시간축 경계 부족.

### 잡았어야 할 기존 층
- provenance/currentness verification
- upstream VERIFIED output gate
- current-state evidence gate

### 현재 상태
COLLECTED_INITIAL / ROOT_NEEDS_EVIDENCE_EXPANSION

---

## TOOL007 — 고객 컨택 판단

### 사용자/실사용에서 반복 확인된 오류 후보
1. 회사/부서 방향을 고객 개인 관심으로 확대해석할 위험.
2. WIC가 일방적으로 보낸 메일을 고객의 관심/요구로 오인할 위험.
3. 문의·답장·견적·구매·전화·소개와 단순 outbound 발송이 섞일 위험.
4. 고객 현재 근거보다 자료추천/컨택 판단이 먼저 나갈 위험.

### 도구/Work 자체점검에서 확인된 오류·방어 필요
1. `MATERIAL_FIRST`는 고객 요구가 있다는 뜻이 아님.
2. TOOL041 VERIFIED 고객정보가 없으면 확정 판단하면 안 됨.
3. 단순 발송 이력을 고객행동으로 사용하면 안 됨.

### ROOT 후보
- ROOT-CUST-02: 회사/부서 방향과 개인 현재 관심 혼합.
- ROOT-HISTORY-01: `WIC 행동`과 `고객 행동` 혼합.
- ROOT-EVIDENCE-01: 실제 고객근거보다 판단/출력이 앞서는 문제.

### 잡았어야 할 기존 층
- history classification gate
- customer-action vs outbound separation
- TOOL041→TOOL007 dependency gate
- evidence-before-judgment gate

### 현재 상태
COLLECTED_INITIAL / ROOT_NEEDS_EVIDENCE_EXPANSION

---

## TOOL042 — 고객별 자료추천·안내

### 사용자/실사용에서 반복 확인된 오류 후보
1. 현재 관심분야 근거 없이 추천자료를 만들 위험.
2. 상류정보가 불완전해도 완성된 안내문처럼 출력될 위험.
3. 공식업무/회사방향을 고객의 현재 구매·자료요구로 오인할 위험.

### 도구/Work 자체점검에서 확인된 오류·방어 필요
1. 실제 현재 관심근거가 없으면 `HOLD / VERIFY_CUSTOMER_STATE`가 정상.
2. 불확실한 상태에서 고객 안내문/발송까지 진행하면 안 됨.

### ROOT 후보
- ROOT-EVIDENCE-01: 근거보다 결과물이 먼저 생성되는 문제.
- ROOT-CUST-02: 공식업무/회사방향과 개인 현재 관심 혼합.
- ROOT-UPSTREAM-01: upstream 불확실성이 downstream의 그럴듯한 출력에 가려지는 문제.

### 잡았어야 할 기존 층
- TOOL007→TOOL042 dependency gate
- current-interest evidence gate
- final-output release gate

### 현재 상태
COLLECTED_INITIAL / ROOT_NEEDS_EVIDENCE_EXPANSION

---

# 1차 공통 ROOT — 현재까지 보이는 것
1. `추정`과 `검증된 사실`이 섞임.
2. `과거`와 `현재`가 섞임.
3. `회사/부서 방향`과 `고객 개인 관심`이 섞임.
4. `WIC가 한 행동`과 `고객이 한 행동`이 섞임.
5. 앞 단계가 불확실한데 다음 단계가 결과를 만들어냄.
6. 결과물이 그럴듯하면 내부 근거 부족이 가려짐.

## 1차 개선 판단 규칙
- 위 ROOT가 41/7/42에서 실제로 같은 원인으로 재현되면 공통 기존층 보강 후보.
- 한 TOOL에만 존재하는 오류면 해당 TOOL만 최소 수정.
- 기존 층이 이미 있는데 못 잡았으면 새 층을 만들지 말고 기존 층을 먼저 강화.
- 기존 어느 층으로도 구조적으로 차단 불가능하다는 실제 증거가 있을 때만 신규층 검토.

---

# 다음 수집 예약
## 2차 대상
- TOOL006: 실제 결과/목차 안정성, 겉보기 PASS와 실제 사용 차이, 자체점검 오류 회수
- TOOL001: 실제 보고서 기반 검증 부족, 안내서 실제 산출물 오류/자가점검 회수
- TOOL009: canonical 정본 불명확/연결 문제 및 자체점검 오류 회수
- TOOL013: 변환파일 존재와 실제 필드/숫자/업로드 정상 여부 차이, 자체점검 오류 회수

## 완료판정
각 단계는 `오류 수집 완료`만으로 끝내지 않는다.
`수집 → ROOT 분류 → 기존층/개별층 매핑 → 최소보강 → 실제 과거 실패입력 재시험 → 개선효과 PASS`까지 닫혀야 해당 단계 COMPLETE다.

TOOL016_ERROR_COLLECTION = INCREMENTAL_REQUIRED
USER_FOUND_ERRORS = REQUIRED
SELF_FOUND_ERRORS = REQUIRED
ROOT_CAUSE_GROUPING = REQUIRED
EXISTING_LAYER_FIX_FIRST = REQUIRED
NEW_LAYER_ONLY_IF_EXISTING_LAYER_INSUFFICIENT = TRUE
TOOL044_AFTER_ROOT_ANALYSIS = REQUIRED
PAST_FAILURE_RETEST = REQUIRED
PHASE_EFFECTIVENESS_GATE = REQUIRED

---

# 1차 과거 대화 피드백 누락분 회수 — 2026-09-07

근거 정본: `customer_pipeline/evidence/tool041_007_042_prior_feedback_recovery_20260907.json`. 대화 제목이 아니라 앱의 실제 thread/turn/message ID로 출처를 고정했다. 당시 assistant가 말하지 않은 내용은 보충하지 않았다.

## TOOL041

### 과거 사용자지적/assistant 원인보고
- `상태복원 실패 → 전체 고객·고유번호 원장 미확정 → 직전 정상 출력형식·분야 흐름 미복원 → 후보선발 규칙 위반 → 검증 없는 PASS성 출력` 연쇄.
- 실제 실패 occurrence: 대학 기본제외 위반, KAIST 4명 편중, 기관/도메인 분산 위반, 전체 번호원장 미대조, 축약 출력, 미확인 후보 PASS 표현, 4명에서 중단.

### 과거 자가점검
- 실제 웹검증 없이 공식 현재정보/URL을 제시할 위험.
- 전체 번호원장 없이 ROB-011 등 다음 번호 계산.
- 직전 정상표와 신규 결과 자동대조 누락.
- HOLD/PASS 경계 약화.
- `MASTER에 규칙 존재`를 `runtime 강제 실행`으로 오인.

### 당시 제안 층
`L0 상태복원 → L1 기준본 역할분리 → L2 규칙충돌 → L3 고유번호 → L4 후보 사전필터 → L5 실제증거 → L6 독립 3중검증 → L7 이어가기 DIFF → L8 출력계약 → L9 배포 전 자가검사 → L10 재발차단 → L11 GitHub/read-back → L12 TOOL016 전달`.

### 현재 대조
- `ALREADY_APPLIED`: identity lock/conflict HOLD actual pairs 3/3; current MASTER의 고유번호·회피·원문완전성·3중검증·출력계약·재발차단 규칙.
- `COLLECTED_NOT_APPLIED`: 위 규칙 전체를 한 canonical runtime entrypoint가 실행 전에 강제하고 실제 웹수집→최종표까지 증명한 E2E. 현재 실제 증거는 merge/integrity 3쌍과 문서규칙이며 전체 실행증거가 아니다.
- `MISSING_FROM_TOOL016`: 위의 상세 연쇄, 7개 실사용 실패, 5개 자가점검, L0~L12 제안이 기존 장부에는 세 개 추상 후보로만 남아 있었다. 본 절에서 회수 완료.
- ROOT: `T41-RC-RUNTIME-RULE-ENFORCEMENT`; 책임층은 TOOL041 start/resume + candidate/output release. 놓친 이유는 master 규칙과 실제 single runtime gate가 동일시됐기 때문.
- 상태: `COLLECTED_NOT_APPLIED / NOT_VERIFIED_RUNTIME`. 외부 HOLD로 위장하지 않는다. 현재 온라인 실제 수집 입력과 canonical 실행 entrypoint가 확정되지 않은 상태에서 가짜 fixture로 PASS하지 않는다.

## TOOL007

### 과거 사용자지적/자가점검 회수
- 동명이인, 최신 재직, 일방발송/고객반응 혼합, 추천 필수값, 거래 발행사/중복, brochure/PDF 링크, 긴 전문 멘트, 실제 연락명분, 최근 연락간격, 답변 유도 질문, artifact provenance, 환경실패/도구실패 혼합, 실행증거 없는 완료.
- 자가점검 핵심은 `규칙을 잘 만듦`과 `실제 작동 실물에 규칙이 연결됨`을 같은 것으로 본 오류.

### 현재 대조
- `ALREADY_APPLIED`: current employment/company direction/contact history fail-closed; one-way send/customer action 분리; 짧은 질문/copy pressure 검사; paid/tradable publisher 및 기본 report fields; provenance/deploy 공통 gate.
- `COLLECTED_NOT_APPLIED`: 최근 연락일 기반 `CADENCE GATE`; product detail HTML과 brochure/PDF를 구분하는 `LINK TYPE GATE`; 실제 사용 HTML과 현재 canonical Python judgment contract의 연결. 실제 source-backed fixture 없이 새 예외를 만들지 않는다.
- `MISSING_FROM_TOOL016`: 당시 17개 gate 목록과 `actual artifact first / ENV vs TOOL / runtime PASS` 구분이 기존 장부의 4개 추상 후보에 없었다. 본 절에서 회수 완료.
- ROOT: `T7-RC-RUNTIME-CONTRACT-GAPS`; 책임층은 TOOL007 recommendation/link/cadence gate와 actual-use entrypoint. TOOL 고유 ROOT이며 공통 신규층 사유가 아니다.
- 1차 `contact_history_verified` 보강은 `SKIP_REUSE`; 동일 실제 positive/negative 연결 회귀 PASS.

## TOOL042

### 과거 사용자지적/자가점검 회수
- 사용자지적: 하위 TOC 들여쓰기 누락, 번호까지 복사되지 않는 TOC.
- 자가점검: master 선조회 HARD GATE 부재, scoped history 회수 불완전, copyable-number 검사 부족, N종 전체 발행사 중복검사 부족, parser/indent renderer 단절, 출력 직전 시각·구조 self-test 부재.
- 당시 제안: `L0 router → L1 master preload → L2 history → L3 current work → L4 candidate → L5 publisher/copyable TOC → L6 N-publisher uniqueness → L7 hierarchy parser → L8 indent renderer → L9 preoutput self-test → L10 evidence PASS`.

### 현재 대조 및 실제 과거 실패형 재시험
- `ALREADY_APPLIED`: `customer_work_start.js` canonical multi-repo preload; output gate의 SHA read-back evidence; `EXACT_FULL`; `TOC_NUMBER_COPYABLE`; `TOC_INDENTATION`; N-report `PUBLISHER_DUPLICATE`; full-body SHA.
- 실제 김명곤 STRICT_FULL_V1 3-report/219 TOC-line output PASS.
- 같은 실제 출력에서 `2.1` 번호만 제거: FAIL `R2_TOC_NUMBER_COPYABLE`.
- 같은 실제 출력에서 `2.1` 들여쓰기만 제거: FAIL `R2_TOC_INDENTATION`.
- internal chain은 customer-name/path/fixture hardcoding 없음과 common runtime/format contract PASS. 단 두 번째 실제 고객 완성 fixture 부재로 `REPRESENTATIVE_1_ONLY_PASS`, `FORMAT_STABILITY=HOLD_REQUIRES_SECOND_ACTUAL_CUSTOMER` 유지.
- `COLLECTED_NOT_APPLIED`: 일반 Chat 전체를 제품 차원에서 강제하는 interceptor, 두 번째 실제 고객 format stability, 인증된 현재 관심/의미 실행.
- `MISSING_FROM_TOOL016`: 위 다섯 named gap과 L0~L10 제안. 본 절에서 회수 완료.
- ROOT: `T42-RC-PRELOAD-OUTPUT-ENFORCEMENT`; 기존 start/output gate에서 닫힘. 외부 현재 관심/두 번째 고객 증거 HOLD는 오류가 아니다.

## 세 TOOL 공통 ROOT 재대조

| ROOT | recurrence | 책임 기존층 | 현재 판정 |
|---|---:|---|---|
| `T41-T7-T42-RC-FACT-BOUNDARY` | 4 | verified upstream handoff + judgment gate | `FIXED_VERIFIED / SKIP_REUSE` |
| `RC-MASTER-RULE-NOT-RUNTIME-ENFORCED` | 3 TOOL | 각 TOOL start/preload/release entrypoint | TOOL042 적용·실패형 재시험 PASS; TOOL041/007 actual-use entrypoint는 `COLLECTED_NOT_APPLIED` |
| `RC-OUTPUT-EXISTS-BUT-NOT-ACTUAL-PASS` | 3 TOOL | actual execution + release/deploy evidence | 공통 gate 존재; TOOL별 실제 증거 범위만 인정 |

## 이번 변경 판정
- 새 공통층: 0.
- TOOL core 수정: 0. 회수 결과 없는 상태에서 새 코드를 상상해 만들지 않았다.
- TOOL016 누락 피드백: 중앙장부와 evidence에 반영.
- 정상 HOLD: TOOL042 `VERIFY_CUSTOMER_STATE`, semantic current-interest evidence, second actual-customer fixture.
- 다음 안전 시작점: 실제 입력/evidence가 들어올 때에만 TOOL041 runtime E2E, TOOL007 cadence/link actual case, TOOL042 second-customer format stability를 각각 DIFF ONLY로 실행한다.

---

# 1차 증거 확정 및 기존층 보강 결과 — 2026-09-07

아래 수치는 추정이 아니라 지정된 fixture/evidence에서 확인된 occurrence만 집계한다.

| ROOT | TOOL | 발견 | 확인 occurrence | 실제 ROOT / 증상 | 기존 책임층과 누락 이유 | 범위 | 판정·증거 |
|---|---|---:|---:|---|---|---|---|
| `T41-RC-DATA-INTEGRITY` | 041 | 사용자 | 3 | identity/field merge가 fail-closed하지 않아 중복·전화충돌·고정 ID 교체 | TOOL041 integrity; 과거 merge에 충돌/ID lock 부족 | 고유 | `VERIFIED_CLOSED`; `t41_actual_pairs.json`, `t41_t42_actual_fixes_20260825.json` |
| `T41-RC-CURRENT-MASTER-LINKAGE` | 041 | 자체 | 2 | 실제 고객을 current master에 유일 연결 불가 | current-master guard; 원천 고객증거 부족 | 고유 | `HOLD_EXTERNAL`; `TOOL041_042_AUTOMATION_20260831.json` |
| `T7-T42-RC-CONTACT-COPY-QUALITY` | 007·042 | 사용자 | 3 | 목적·영업성 노출, 일반화 후속문, 긴 행정 설명 | 기존 copy validator/release gate; 정형 검사만으로 의미 자연스러움 확정 불가 | 공통 | `PARTIAL_VERIFIED/HOLD_SEMANTIC`; `contact_copy_actual_cases.json` |
| `T42-RC-CUSTOMER-BRANCH` | 042 | 사용자 | 2 | 획일 분기 및 미검증 이력으로 진행 | TOOL042 branch gate; 과거 필수 state bundle 누락 | 고유 | `VERIFIED_CLOSED`; `customer_branch_actual_kmg.json` |
| `T41-T7-T42-RC-FACT-BOUNDARY` | 041·007·042 | 사용자+자체 | 4 | 회사방향/개인관심, WIC 발송/고객행동, 불완전 upstream/downstream 출력 혼합 | 041→007 handoff와 TOOL007 judgment가 접촉이력 verified receipt를 요구하지 않았음 | 세 TOOL 공통 | `FIXED_VERIFIED_THIS_WORK`; 동일 actual fixture negative/positive 회귀 |
| `T42-RC-SEMANTIC-EXECUTOR` | 042 | 자체 | 1 | 8개 의미검사가 `HOLD_NOT_EXECUTED` | release gate; 인증된 의미실행환경 부재 | 고유 | `HOLD_EXTERNAL`; `TOOL041_042_SEMANTIC_EXECUTOR_HOLD_20260831.json` |

## 보강 결과

- 새 층 없음. 기존 `p1_to_p2_handoff`에 `contact_history_verified`를 필수 receipt로 추가하고 TOOL007 `judge_contact`도 동일 값이 없으면 `CONTACT_HISTORY_UNVERIFIED`로 차단한다.
- TOOL042는 이미 동일 fail-closed 검사를 수행하므로 수정하지 않았다.
- 과거 실제 김태호/KRICT fixture에서 검증 이력이 있으면 기존 결과를 보존하고, 동일 fixture에서 이력 검증만 제거하면 TOOL007 출력 전에 HOLD된다.
- 증거: `customer_pipeline/evidence/tool041_007_042_root_regression_20260907.json`.
