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

# 2차 과거 대화 피드백 누락분 회수 — 2026-09-07

정본 evidence: `feedback_pipeline/evidence/tool006_001_009_013_prior_feedback_recovery_20260907.json`. 1차 ROOT와 기존 runtime/deploy gate는 재작성하지 않았다.

## TOOL006

- 과거 사용자지적: 번호·계층·줄바꿈·들여쓰기, 괄호 설명문/별표 각주 혼입, List of Tables/Figures 오분류, Depth 2/3/4, HOLD 남발, UI 기능누락, 개발본과 실사용본 차이, 같은 오류 재발.
- 과거 assistant 자가점검: `파일/화면/단일 테스트 PASS`를 출고기준으로 사용했고 실제 운영파일 재시험·원문↔출력·영향회귀가 강제되지 않았다고 보고.
- 당시 개선안: HARD RELEASE GATE, 발행사/목차형태 식별, Depth/번호/누락/가짜생성/HOLD 검사, 단일 엔진, UI 회귀, 실제 사용 E2E, 오류 fixture 자동축적.
- `ALREADY_APPLIED`: T6-RC-01~04 actual chronic fixtures 및 단일 엔진. 이번 focused 실행에서 functional 9/9, smoke 4/4 PASS.
- `MISSING_FROM_TOOL016`: 위 구체적 실패목록과 release-layer 제안이 기존 4개 occurrence만으로 축약돼 있었다. 회수 완료.
- ROOT: `T6-RC-RELEASE-WITHOUT-ACTUAL-IMPACT-E2E`; 책임층은 TOOL006 parser/tree/depth/output release + deployed-copy gate. 기존층으로 차단 가능하며 신규층 불필요.
- `NORMAL_HOLD`: 발행사 실제 raw→expected golden pair. 기존 actual screenshot/MarketsandMarkets 및 chronic fixture PASS를 모든 발행사 의미정답 PASS로 확대하지 않는다.

## TOOL001

- 과거 사용자지적: 고객 안내서 글씨 크기/형식 불균일, TOC 불안정, 출력 지연.
- 과거 assistant 자가점검/층제안: TOOL001은 최종 안내서 조립·글씨·형식만 소유하고 TOC/고객판단/과거고객/데이터는 TOOL006/007·042/041/013의 VERIFIED 출력만 재사용해야 한다. 접근 차단 발행사는 우회하지 않고 HOLD.
- `ALREADY_APPLIED`: runtime verified-data fail-closed, USB shell quarantine, 소유권 분리. 브라우저 CI fixture 5건은 실제 보고서 5건으로 승격하지 않는다.
- `COLLECTED_NOT_APPLIED`: 실제 검증 보고서 5건으로 고객입력→최종안내서→재개봉 E2E.
- `MISSING_FROM_TOOL016`: 글씨/TOC/속도 실사용 피드백과 최종조립 책임경계. 본 절에서 회수 완료.
- ROOT: `T1-RC-ACTUAL-REPORT-EVIDENCE-GATE`; 책임층은 TOOL001 verified report acquisition + final assembly/output release.
- `NORMAL_HOLD`: 실제 verified report payload count 0, trigger `FIVE_ACTUAL_VERIFIED_REPORT_PAYLOADS_AVAILABLE`. 이는 실제 입력 부족을 정확히 차단한 정상 HOLD다.

### 2026-09-07 실제 보고서 자동확보 증분

- 기존 완료 경로를 반복 검색하지 않고 TOOL001 canonical/실사용 참조, CENTRAL evidence, provenance가 확인된 `repo42/fixtures`와 TOOL013 실제입력 evidence만 scoped 검사했다.
- 실제 고객 fixture에서 서로 다른 발행사 실제 보고서 기록 3건(BCC Research, Technavio, Stratistics MRC)을 회수해 `evidence/tool001_actual_report_input_registry_20260907.json`에 영속화했다.
- 세 기록 모두 제목·발행사·발행일·페이지·원문 URL·전체 TOC·보고서 정보 provenance가 있으나, TOOL001 필수 계약의 공급가격(Technavio는 정가도 포함)이 독립 검증되지 않아 각각 HOLD다. 없는 값을 생성하지 않았다.
- `ACTUAL_VERIFIED_REPORTS = 0/5`, `RECOVERED_ACTUAL_REPORT_RECORDS = 3/5`; REPORT-4/5는 미회수다.
- 반복 HOLD ROOT는 `T1-RC-ACTUAL-INPUT-DISCOVERY-PERSISTENCE-GAP`이다. 세부 원인은 (1) 실제 업무 입력 자동발견층이 canonical runtime에 연결되지 않음, (2) provenance 실제입력 registry가 없었음, (3) 실물은 존재하지만 필수 상업필드가 완전하지 않아 runtime의 5건 gate를 통과할 수 없음이다.
- 기존 `T1-RC-ACTUAL-REPORT-EVIDENCE-GATE`의 recurrence로 병합한다. 새 공통층은 만들지 않는다. 이번 registry로 동일 세 위치/세 보고서를 다음 Work에서 다시 찾는 것을 금지한다.

## TOOL009

- 과거 대상 대화창에서 사용자의 원인보고 요청에 답한 assistant 피드백: `NOT_FOUND_IN_PRIOR_FEEDBACK`.
- canonical evidence에서 확인된 실제 상태만 기록: repository `obk369369-spec/09-contents-making-tool`; production `index.html`이 빈 storage/parsing failure 때 `createInitialSampleData()` 및 sample-1/2/3 fallback을 사용한다.
- ROOT: `T9-RC-SYNTHETIC-FALLBACK-AS-PRODUCTION`; 책임층은 TOOL009 canonical/runtime start + actual-input fail-closed gate.
- `COLLECTED_NOT_APPLIED`: synthetic fallback 제거와 actual-input HOLD 전환. 그러나 actual-use canonical entrypoint와 안전한 부분수정 경로가 확정되지 않아 코드 수정하지 않았다.
- `NORMAL_HOLD`: `HOLD_CANONICAL_NOT_RESOLVED`; `실제 오류 상태`: `FAIL_SYNTHETIC_FALLBACK_PRESENT_PATCH_BLOCKED`. 잘못된 정본을 추측해 수정하지 않는다.

## TOOL013

- 과거 사용자지적: 실제 배포본 114개 입력이 `행 0 / 발행사 UNKNOWN / 순차 배치 114개 읽기 시작`에서 멈춤.
- 과거 assistant 자가점검: 파일선택 이후 자동감지→매핑→미리보기까지 연결되지 않았고, Work가 실제 배포본 E2E 없이 완료 처리한 shell completion이라고 보고.
- 당시 개선안: 실제 최종 배포본에서 동일 입력 E2E, row 0/UNKNOWN/중간정지/미리보기 없음 즉시 BLOCK, 동일 입력 재시험, 실패 시 DIFF rework 출력.
- `ALREADY_APPLIED`: 동일 실제 114개→823행, MarketsandMarkets, 114 PASS/0 HOLD, output reopen; 원본/preview/download 1:1; 실제 `.xls`/`.xlsx`→BIFF8 `.xls` 배포본 재시험 PASS.
- `MISSING_FROM_TOOL016`: 이 actual recurrence와 `파일 생성 ≠ 실제 업무 PASS / 개발본 PASS ≠ deployed-copy PASS` 원인서술. 본 절에서 회수 완료.
- ROOT: `T13-RC-LARGE-BATCH-MAIN-THREAD-STALL` + `RC-DEPLOYED-COPY-NOT-ACTUAL-E2E`; 기존 batch/release/deployed-copy gate로 `VERIFIED_CLOSED / SKIP_REUSE`.

## 1차+2차 공통 ROOT

| 공통 ROOT | 확인 TOOL 수 | 책임 기존층 | 판정 |
|---|---:|---|---|
| `규칙 존재 ≠ runtime 강제` | 7 | 각 TOOL start/preload/release | 기존층 보강 가능; 신규층 불필요 |
| `TEST PASS ≠ 실제 업무 PASS` | 6 | actual-input E2E + output release | 기존 공통 TEST/DEPLOY gate 적용 |
| `canonical/test본 ≠ 실제 사용본` | 5 | canonical receipt + deployed-copy test | 기존 receipt/deploy gate 적용 |
| `source/provenance 부족` | 7 | evidence/provenance + fail-closed HOLD | 기존층 적용; 외부 증거는 정상 HOLD |
| `partial test ≠ full impact regression` | 5 | change-only impact regression | 기존층 적용 |

수치는 이번 1·2차 장부에서 실제로 같은 증상이 확인된 TOOL을 중복 없이 센 값이다. 유사 문구만으로 recurrence를 늘리지 않았다.

## 2차 결론

- 새 공통층 필요성: `필요 없음`.
- `NEW_LAYER_CANDIDATE`: 0. 기존 start/evidence/release/receipt/deployed-copy 층으로 책임 매핑 가능하다.
- TOOL core 수정: 0. TOOL001/009는 실제 입력·정본 조건이 없어 사전 HOLD, TOOL006/013은 이미 실제 회귀가 닫혀 재수정 금지.
- TOOL044 사용: 0.
- 다음 trigger: TOOL006 publisher golden pair, TOOL001 five verified reports, TOOL009 canonical actual-use entrypoint + safe patch path. TOOL013은 새로운 상충 실사용 증거 없으면 SKIP_REUSE.

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

---

# 3차 과거 대화 피드백 누락분 회수 — 2026-09-07

정본 evidence: `feedback_pipeline/evidence/tool014_012_002_prior_feedback_recovery_20260907.json`. 필수 대상 TOOL014·012 이후에는 전체 TOOL을 조사하지 않고, registry가 ACTIVE이며 최신 운영 대화와 실제 오류증거가 함께 확인된 TOOL002만 선정했다.

## TOOL014

- 사용자 발견: 시간이 지나도 잔여량이 같고 실제 조립 산출물이 없는데 작업·테스트가 계속된다고 반복 보고했다.
- assistant 자가발견: 실제 상태는 설계/HTML 뼈대뿐이며 `test.worldic.co.kr` 배포와 브라우저 실행·검증을 하지 않았고, 과거 `30% 남음/테스트 진행 중` 주장은 부정확했다고 정정했다.
- 당시 개선안: 실행 가능한 staging 산출물 → 브라우저 검증 → 배포/read-back 뒤에만 완료.
- TOOL016 대조: 구체 대화 occurrence는 `MISSING_FROM_TOOL016`이었으나 ROOT는 기존 `TEST PASS ≠ 실제 업무 PASS`, `정본·테스트본 ≠ 실사용본`과 동일하다.
- 현재: `ALREADY_APPLIED / STAGING_REMOTE_VERIFIED`; runtime `ae41bc0...`, evidence checkpoint `7dee81e...`, Pages run `33310481614`. 실제 live 홈페이지 적용은 `NORMAL_HOLD / LIVE_HOMEPAGE_APPLY_REQUIRES_EXPLICIT_AUTHORIZATION`이며 억지 PASS하지 않는다.

## TOOL012

- 사용자 발견: 서브웹사이트 창에 20개 도구 범위를 섞음, 수개월 규모를 분 단위로 축소, 사용자를 반복 안내·검수 작업자로 만듦, 껍데기 진행을 실제 개발처럼 보고.
- assistant 자가발견: 설계/1차 시안 외 실제 코드·배포·DB/API·메일/PDF·결제 연결은 실행되지 않았고, 종전 버튼 구현/테스트/오류 0 주장은 파일·로그 증거가 없다고 정정했다.
- 당시 개선안: 현실 작업계획, 실제 산출물 기반 진행, 외부 실행층 HOLD 분리, 실제 화면/기능/오류 검증.
- TOOL016 대조: 구체 occurrence는 `MISSING_FROM_TOOL016`; ROOT는 기존 `규칙 존재 ≠ runtime 강제`, `TEST PASS ≠ 실제 업무 PASS`와 동일하다.
- 현재: `VERIFIED_CLOSED / COMPLETE / REMOTE_VERIFIED / SKIP_REUSE`; runtime `aa9cc2e...`, checkpoint `11bac27e...`, Pages run `33310342582`. 과거 오류 기록은 보존하되 재수정하지 않는다.

## 기타 현재 운영 TOOL — TOOL002

- 선정근거: current registry `ACTIVE`, 실제 최근 운영 대화 존재, 사용자 오류지적과 assistant 자가정정 모두 확인. 다른 운영 TOOL은 이번에 전수 선정하지 않았다.
- 사용자 발견: 최신 전체 기록을 먼저 회수하지 않고 2026-03-16을 최신점처럼 답함; 웹/파일 접근 승인 부담을 관찰자에게 반복 전가.
- assistant 자가발견: 3월 16일 최신점 주장은 오류였고, 8월 functional E2E PASS와 이후 공개수집 확장 HOLD를 분리해야 한다고 정정했다.
- 당시 개선안: 8월 functional E2E는 SKIP_REUSE, 본체/소형 관찰자/CENTRAL 역할 분리, 공개수집과 인증 투찰 범위 분리.
- TOOL016 대조: `MISSING_FROM_TOOL016`; ROOT는 기존 `규칙 존재 ≠ runtime 강제`, `partial test ≠ impact regression`의 하위형이다.
- 현재: 기본 입력→저장→화면표시 functional E2E는 `VERIFIED_CLOSED / SKIP_REUSE`. 공개수집·기관별 수집·인증 제출 확장은 기존 PASS로 확대하지 않는 `NORMAL_HOLD`다.

## 1차+2차+3차 공통 ROOT

| ROOT | 1차 TOOL | 2차 TOOL | 3차 TOOL | 총 영향 TOOL | 책임 기존층 | 현재 차단 가능 여부 |
|---|---|---|---|---:|---|---|
| 규칙 존재 ≠ runtime 강제 | 041·007·042 | 006·001·009·013 | 012·002 | 9 | TOOL start/preload/release | 가능; 실제 entrypoint 연결증거 없는 TOOL만 HOLD |
| TEST PASS ≠ 실제 업무 PASS | 041·007·042 | 006·001·013 | 014·012 | 8 | actual-input E2E + output release | 가능; staging/live 및 fixture/actual 분리 필수 |
| 정본·테스트본 ≠ 실사용본 | 041·007·042 | 006·001·013 | 014 | 6 | canonical receipt + deployed-copy test | 가능; TOOL014 live는 승인 HOLD |
| source/provenance 부족 | 041·007·042 | 006·001·009·013 | 없음 | 7 | provenance/evidence fail-closed | 가능; 정상 외부 HOLD 보존 |
| partial test ≠ impact regression | 041·007·042 | 006·013 | 002 | 6 | change-only impacted regression | 가능; 기본 PASS를 확장범위 PASS로 확대 금지 |

수치는 각 단계 정본 evidence에서 같은 ROOT가 실제 확인된 TOOL의 합집합이다. 3차 occurrence를 과거 수치에 기계적으로 더하지 않았다.

## 3차 효과 및 판정

- 증거가 더 강해진 ROOT: `규칙 존재 ≠ runtime 강제`, `TEST PASS ≠ 실제 업무 PASS`, `정본·테스트본 ≠ 실사용본`, `partial test ≠ impact regression`.
- 기존층 보강 대상으로 거의 확정: start/preload/release에서 실제 entrypoint 증거 강제, actual-input/deployed-copy 구분. 단 이미 공통게이트가 존재하므로 새 층이 아니라 TOOL 적용 시 강제할 항목이다.
- 증거 부족 ROOT: 없음(3차에서 새로운 독립 ROOT를 만들 근거 없음).
- `NEW_LAYER_CANDIDATE = 0`; TOOL core 수정 0, TOOL044 사용 0.
- 기존층이 실제 차단/닫은 사례 3, 불필요한 TOOL 개별수정 회피 3, 거짓 PASS 재분류 2, 정상 HOLD 유지 2, 과거 실패 재시험 0(기능 변경 없음).
- 2차 미완료 보존: TOOL001 3/5 회수·0/5 완전검증, TOOL006 publisher golden pair HOLD, TOOL009 synthetic fallback 오류/canonical 미확정.
- 최종: `PHASE3_FEEDBACK_RECOVERY_COMPLETE_NO_CODE_FIX_JUSTIFIED`.

---

# 4차 잔여 운영 TOOL 피드백 회수 — 2026-09-07

정본 evidence: `feedback_pipeline/evidence/tool043_044_020_027_035_prior_feedback_recovery_20260907.json`.

## 대상 선정

- `TOOL043`: 실제 모바일/Pages/상태 projection 운영과 반복 수정·검증 기록이 존재한다.
- `TOOL044`: 실제 component pilot·production·local-first·thin observer 배포 기록과 사용자 반복 보정 지시가 존재한다.
- `TOOL020`, `TOOL027`, `TOOL035`: registry와 원격 검증 기록은 존재하지만 접근 가능한 대화 index에서 사용자 반복오류→assistant 답변 연결을 확인하지 못했다. 추정하지 않고 `NOT_FOUND_IN_PRIOR_FEEDBACK`으로 보존한다.
- 1~3차 대상, 폐기 legacy, 실험/아이디어/SHELL은 제외했다.

## TOOL043

- 사용자 발견: 최신 CENTRAL이 `OPEN_INTERNAL=0`인데 모바일 projection이 오래된 장부 시각과 `OPEN 1`을 계속 표시했고, 화면 OFF/background 결과는 실제 기기 증거 전에는 완료할 수 없다고 반복 지적했다.
- assistant/실행 자가발견: observer refresh는 실제 업무 A→B→C 실행이 아니며, 초기 연속실행 주장에는 task producer/실제 handler/독립 verifier가 없었다. 또한 local launcher 경로 인수 문제로 `Failed to fetch`가 발생했다.
- 당시 개선: CENTRAL→projection→Pages read-back, actual device evidence, completion-proof fail-closed, 실제 task chain과 observer refresh 분리.
- TOOL016 대조: 구체 occurrence는 `MISSING_FROM_TOOL016`; ROOT는 `규칙 존재 ≠ runtime 강제`, `TEST PASS ≠ 실제 업무 PASS`, `정본·테스트본 ≠ 실사용본`, `partial test ≠ impact regression`의 하위형이다.
- 현재: 모바일/Pages 및 completion-proof 합의 범위는 `VERIFIED_CLOSED / SKIP_REUSE`; 실제 business A→B→C handler가 없는 범위는 `ACTUAL_ERROR_HOLD`이며 observer refresh PASS로 확대하지 않는다.

## TOOL044

- 사용자 발견: 최초 대화 답변은 운영지시를 “메모리에 저장”했다고만 하고 다시 시작 여부를 물어 관찰자 원칙과 중앙 영속화를 충족하지 못했다. 이후에도 MASTER/registry/sandbox만으로 완료하지 말고 실제 대상 장착→배포본 재시험까지 요구했다.
- assistant/실행 자가발견: 최초 답변에는 canonical write/read-back 증거가 없었다. 이후 evidence는 TOOL013 idb-keyval pilot과 TOOL043 completion-proof 생산 적용의 범위를 분리했고, 임의 미래 adapter 자동생성까지 검증한 것은 아니라고 명시했다.
- 당시 개선: verified registry 우선, bounded search, receipt 검증, 실제 대상 무수정 장착, deployed-copy retest, SAFE_CHECKPOINT, 사용자 중간조작 0.
- TOOL016 대조: 구체 occurrence는 `MISSING_FROM_TOOL016`; ROOT는 `규칙 존재 ≠ runtime 강제`, `TEST PASS ≠ 실제 업무 PASS`, `정본·테스트본 ≠ 실사용본`의 하위형이다.
- 현재: TOOL013 pilot, TOOL043 production adapter, mechanical runner, thin observer는 해당 증거 범위만 `DEPLOYED_PASS / SKIP_REUSE`; arbitrary future business adapter는 `COLLECTED_NOT_APPLIED`이며 검증 없이 일반화하지 않는다.

## TOOL020 / TOOL027 / TOOL035

- canonical registry와 verified commit/evidence는 확인했다.
- 접근 가능한 대화 index에서 사용자 반복오류, assistant 자가점검, 당시 층 개선을 연결할 실제 turn을 찾지 못했다: `NOT_FOUND_IN_PRIOR_FEEDBACK`.
- TOOL020 first validation, TOOL027 `NO_DEFERRED_WORK`, TOOL035 verified integration은 `SKIP_REUSE`; 피드백을 상상해 occurrence를 추가하지 않는다.

## 1~4차 공통 ROOT 집계

| ROOT | 영향 TOOL 수 | 사용자 발견 TOOL | 자가발견 TOOL | 재발 TOOL 수 | 책임 기존층 | 기존층 차단 | 5차 우선순위 |
|---|---:|---:|---:|---:|---|---|---|
| 규칙 존재 ≠ runtime 강제 | 11 | 11 | 10 | 11 | start/preload/runtime release | 가능 | P0 |
| TEST PASS ≠ 실제 업무 PASS | 10 | 10 | 10 | 10 | actual-input E2E/output release | 가능 | P0 |
| 정본·테스트본 ≠ 실사용본 | 8 | 8 | 8 | 8 | canonical/deployed receipt + copy test | 가능 | P0 |
| source/provenance 부족 | 7 | 7 | 7 | 7 | provenance fail-closed | 가능 | P1 |
| partial test ≠ impact regression | 7 | 7 | 7 | 7 | change/impact regression | 가능 | P1 |

집계 단위는 독립 문장 수가 아니라 실제 ROOT가 확인된 TOOL 합집합이다. TOOL020·027·035는 prior feedback 미발견이므로 occurrence에 포함하지 않았다.

## PHASE5_COMMON_LAYER_FIX_QUEUE

| ROOT ID | 영향 TOOL | 과거 실패 fixture | 현재 방어층 실패 이유 | 보강할 기존층 | 수정범위 | 필수 regression | PASS 기준 | 신규층 | TOOL044 |
|---|---|---|---|---|---|---|---|---|---|
| P5-RUNTIME-ENFORCEMENT | 041·007·042·006·001·009·013·012·002·043·044 | stale master, memory-only instruction, observer-refresh-as-work | entrypoint receipt가 문서 규칙과 분리됨 | existing start/preload/release gate | receipt 소비·fail-closed DIFF | 041→007→042, 043 projection, 044 production | 최신 receipt 없는 runtime 차단 | NO | NO |
| P5-ACTUAL-USE-E2E | 041·007·042·006·001·013·014·012·043·044 | fixture/staging/UI PASS 확대 | actual input/device/live scope 구분 누락 | existing actual-input/output release | evidence class·scope enforcement | 각 TOOL 보존 fixture + 실제 입력 있는 범위 | fixture/staging PASS가 real-use로 승격되지 않음 | NO | NO |
| P5-CANONICAL-DEPLOYED-RECEIPT | 041·007·042·006·001·013·014·043 | stale projection, local/GitHub mismatch | deployed-copy receipt 소비 누락 | existing dual receipt/deploy gate | hash/version/read-back DIFF | 043 state projection + representative deployed copy | canonical↔deployed mismatch 차단 | NO | NO |
| P5-PROVENANCE-FAIL-CLOSED | 041·007·042·006·001·009·013 | missing customer/report/publisher source | source class가 downstream보다 늦게 검사됨 | existing provenance/evidence gate | upstream-required marker DIFF | saved actual source fixtures | source 없는 생성/승격 차단, 정상 HOLD 보존 | NO | NO |
| P5-IMPACT-REGRESSION | 041·007·042·006·013·002·043 | row-count/partial/single-scope PASS 확대 | changed/impacted mapping 불완전 | existing impacted-regression gate | impact manifest enforcement | 직접 영향 fixture only | 영향검사 누락 시 release 차단 | NO | NO |

## 4차 효과 및 보존

- 4차 신규 독립 ROOT 0, `NEW_LAYER_CANDIDATE = 0`, TOOL core 수정 0, TOOL044 신규사용 0.
- 기존층으로 차단/범위분리 가능한 5개 ROOT, 5차 기존층 보강 큐 5개, 불필요한 TOOL 개별수정 회피 5, 새 층 생성 회피 5.
- 과거 거짓 PASS 재분류 2: TOOL043 observer refresh를 business chain으로 확대, TOOL044 memory/sandbox/registry를 production 전체로 확대.
- 정상 HOLD 보존: TOOL001 3/5 회수·0/5 검증, TOOL006 publisher golden pair, TOOL009 canonical 미확정, TOOL014 live 승인, TOOL043 실제 handler 부재 범위.
- 코드/gate 변경이 없어 실제 실패 재시험 0. 장부 변경을 TOOL 기능 개선으로 보고하지 않는다.
- 최종: `PHASE4_COMPLETE / PHASE5_READY / NO_CODE_FIX_JUSTIFIED`.
