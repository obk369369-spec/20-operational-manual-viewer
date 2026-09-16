# WIC 각 대화창 최근 오류·피드백 자동수집 → TOOL016 → TOOL044 준비

상태: PREPARED / WORK_IMPLEMENTATION_REQUIRED
작성일: 2026-09-16

## 목적
사용자가 각 대화창을 돌아다니며 오류·피드백을 복사하거나 TOOL044에 직접 전달하지 않는다.

최종 경로:
`각 WIC 대화창/접근 가능한 대화기록 → 수집 → 정규화/중복제거 → TOOL016 ROOT/atomic demand → TOOL044 대상 선별 → TOOL044_REQUEST_INBOX/atomic demand queue → TOOL044 기존 원칙대로 처리`

## A. 채팅창 경로 — 즉시 적용 규칙

채팅창에서 사용자가 WIC 작업을 계속하는 동안 다음을 강제한다.

1. 현재 대화에서 새 오류지적, 개선요구, 운영규칙, HOLD/FAIL, 중요한 의사결정, 실제 작업결과가 발생하면 `FEEDBACK_EVENT` 후보로 취급한다.
2. 같은 원인/같은 요구의 반복은 occurrence로 합치고 새 ROOT를 남발하지 않는다.
3. 이미 PASS/VERIFIED인 동일 요구는 SKIP_REUSE한다.
4. 변화 없는 외부 HOLD는 재작업하지 않는다.
5. TOOL044로 직접 모든 항목을 보내지 않는다. TOOL016에서 ROOT/atomic demand로 정리한 뒤 `외부 완성부품을 무수정 장착하여 해결 가능한 요구`만 TOOL044 대상으로 한다.
6. 사용자가 다른 대화창의 내용을 수동 복사하도록 요구하지 않는다.
7. 현재 채팅 런타임에서 다른 ChatGPT 대화창 전체를 직접 열람할 수 없는 경우 이를 PASS로 위장하지 않는다. 해당 접근 경계는 `CHAT_HISTORY_ACCESS_BOUNDARY`로 기록한다.

### FEEDBACK_EVENT 최소 스키마
- source_chat_or_tool
- observed_at
- event_type: ERROR | FEEDBACK | RULE | HOLD | FAIL | DECISION | RESULT
- raw_summary
- root_cause_or_demand
- occurrence_key
- evidence_ref
- current_status
- tool044_candidate: true|false|unknown

## B. Work 구현 경로 — 다음 실제 미완료

Work는 `지난번 어디까지 했지?`를 재탐색하지 않는다. 기존 SAFE_CHECKPOINT / last_actual_point / next_start / next_trigger를 먼저 회수하고 이미 완료된 16→44 경로는 SKIP_REUSE한다.

현재 실제 미완료 ROOT:
`TOOL016-RETROSPECTIVE-WIC-ERROR-SWEEP-20260908-HISTORICAL_FEEDBACK_INGEST`

기존 증거상 `HISTORICAL_FEEDBACK_INGEST = MISSING_CAPABILITY`이며 TOOL044 완성부품 검색은 `NO_READY_ATOMIC_COMPONENT`였다. 따라서 TOOL044 내부에서 커스텀 개발하지 않는다.

### Work가 구현해야 할 것
1. 저장소/플랫폼에서 합법적으로 접근 가능한 대화기록 입력원을 한 번에 식별한다.
2. 입력원이 있으면 전체 범위를 먼저 수집하고 mutation 전에 오류/피드백 후보를 전부 집계한다.
3. 전 대화/전 파일을 교차하여 같은 ROOT/원인/요구로 dedup/group한다.
4. TOOL016이 소비 가능한 단일 canonical ingest 형식으로 변환한다.
5. 기존 TOOL016→TOOL044 인계기를 재사용한다. 새 병렬 인계 시스템을 만들지 않는다.
6. batch fixture로 여러 대화, 중복 오류, 반복 피드백, PASS 재등장, HOLD 재등장을 한꺼번에 시험한다.
7. 실패를 먼저 전부 모은 후 한 번의 repair batch로 고친다.
8. 최소 Git/GitHub 왕복으로 반영하고 마지막에 E2E read-back 한다.
9. 실제 ChatGPT 전체 대화기록 접근 API/입력원이 제공되지 않으면 그 부분만 `PLATFORM_ACCESS_HOLD`로 남기고, 나머지 ingest/parser/dedup/TOOL016→TOOL044 연결은 fixture/실제 접근가능 입력으로 검증한다.

## Work 낭비 방지 — 강제
- ONE_FILE_ONE_OPERATION = FORBIDDEN
- ONE_ERROR_ONE_OPERATION = FORBIDDEN
- COLLECT_ALL_ERRORS_BEFORE_MUTATION = REQUIRED
- CROSS_FILE_BATCH_REPAIR = REQUIRED
- BATCH_TEST_AFTER_BATCH_MUTATION = REQUIRED
- FAILURES_COLLECT_FIRST_THEN_BATCH_REPAIR = REQUIRED
- NO_FILE_BY_FILE_EXECUTION = REQUIRED
- 완료된 commit/push/cloud/read-back 재실행 금지
- PASS 재확인 금지
- 변화 없는 HOLD 재시도 금지
- 조사만 하는 Work 금지

## 완료 판정
다음이 모두 증거로 확인될 때만 `E2E_PASS`:
1. 실제 접근 가능한 복수 대화기록 입력
2. 최근 오류/피드백 추출
3. ROOT/occurrence dedup
4. TOOL016 canonical ingest
5. TOOL044 대상 자동 선별
6. TOOL044 inbox/atomic queue receipt
7. 중복 재실행 시 idempotent
8. remote read-back

ChatGPT 플랫폼이 전체 대화창 자동열람 통로를 제공하지 않는 경우 전체 시스템 상태는 `PARTIAL_PASS_PLATFORM_ACCESS_HOLD`; 해당 통로가 확보된 뒤 같은 E2E 시험을 실제 전체 대화 범위로 다시 통과해야 최종 PASS한다.
