# WIC 각 대화창 최근 오류·피드백 자동수집 → TOOL016 → TOOL044 준비

상태: PREPARED / MERGE_INTO_NEXT_COMPRESSED_WORK_BATCH
작성일: 2026-09-16

## 목적
사용자가 각 대화창을 돌아다니며 오류·피드백을 복사하거나 TOOL044에 직접 전달하지 않는다.

최종 경로:
`각 WIC 대화창/접근 가능한 대화기록 → 수집 → 정규화/중복제거 → TOOL016 ROOT/atomic demand → TOOL044 대상 선별 → TOOL044_REQUEST_INBOX/atomic demand queue → TOOL044 기존 원칙대로 처리`

## A. 채팅창 경로 — 즉시 적용 규칙
현재 대화에서 새 오류지적, 개선요구, 운영규칙, HOLD/FAIL, 중요한 의사결정, 실제 작업결과가 발생하면 FEEDBACK_EVENT 후보로 취급한다. 같은 원인/요구의 반복은 occurrence로 합치고 새 ROOT를 남발하지 않는다. 이미 PASS/VERIFIED인 동일 요구는 SKIP_REUSE하고 변화 없는 외부 HOLD는 재작업하지 않는다. TOOL016에서 ROOT/atomic demand로 정리한 뒤 외부 완성부품을 무수정 장착하여 해결 가능한 요구만 TOOL044 대상으로 한다. 사용자가 다른 대화창 내용을 수동 복사하도록 요구하지 않는다. 현재 런타임에서 다른 ChatGPT 대화창 전체를 직접 열람할 수 없는 경우 CHAT_HISTORY_ACCESS_BOUNDARY로 기록하고 PASS로 위장하지 않는다.

FEEDBACK_EVENT 최소 스키마: source_chat_or_tool, observed_at, event_type, raw_summary, root_cause_or_demand, occurrence_key, evidence_ref, current_status, tool044_candidate.

## B. Work 처리 방식 — 독립 작업 금지

이 항목만 따로 Work를 열거나, 이것만 붙잡고 별도 조사/구현/검증하는 것을 금지한다.

`HISTORICAL_FEEDBACK_INGEST`는 **다음 WIC 전체 압축 Work batch의 한 하위 ROOT**로만 포함한다. 다른 실제 미완료 ROOT들과 함께 전체 범위를 먼저 모은 뒤, 중복/PASS/변화 없는 HOLD를 제거하고 공통 원인·공통 파일·공통 시험·공통 배포 단위로 교차파일 대량 처리한다.

Work는 `지난번 어디까지 했지?`를 재탐색하지 않는다. 기존 SAFE_CHECKPOINT / last_actual_point / next_start / next_trigger를 회수하고 이미 완료된 16→44 경로는 SKIP_REUSE한다.

현재 포함할 미완료 ROOT:
`TOOL016-RETROSPECTIVE-WIC-ERROR-SWEEP-20260908-HISTORICAL_FEEDBACK_INGEST`

기존 증거상 HISTORICAL_FEEDBACK_INGEST=MISSING_CAPABILITY이고 TOOL044 검색은 NO_READY_ATOMIC_COMPONENT였다. TOOL044 내부 커스텀 개발은 금지한다.

### 전체 압축 batch 안에서 이 ROOT가 할 일
1. 다른 미완료 ROOT들과 함께 접근 가능한 입력원/오류 범위를 한 번에 수집한다.
2. mutation 전에 전체 오류·피드백 후보를 집계한다.
3. 전 대화/전 파일 교차 ROOT dedup/group한다.
4. TOOL016 canonical ingest로 변환한다.
5. 기존 TOOL016→TOOL044 인계기를 재사용한다.
6. 여러 대화/중복 오류/반복 피드백/PASS 재등장/HOLD 재등장을 다른 batch 시험들과 함께 시험한다.
7. 이 ROOT의 실패도 다른 실패들과 먼저 모은 후 repair batch에 합쳐 고친다.
8. 이 ROOT 때문에 별도 commit/push/cloud/read-back을 만들지 않는다. 전체 batch의 Git/GitHub/cloud/read-back에 합친다.
9. 플랫폼 전체 대화기록 입력원이 없으면 PLATFORM_ACCESS_HOLD만 남기고 그 HOLD 때문에 전체 Work를 붙잡지 않는다. 접근 가능한 범위의 parser/dedup/TOOL016→TOOL044 검증을 끝내고 다른 ROOT로 계속 진행한다.

## Work 낭비 방지 — 강제
- STANDALONE_WORK_FOR_THIS_ROOT = FORBIDDEN
- BLOCK_OTHER_WORK_FOR_THIS_ROOT = FORBIDDEN
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

## 이 ROOT의 완료 판정
실제 접근 가능한 복수 대화기록 입력 → 최근 오류/피드백 추출 → ROOT/occurrence dedup → TOOL016 canonical ingest → TOOL044 대상 자동선별 → TOOL044 receipt → idempotent → 전체 batch final remote read-back까지 확인되면 해당 범위 PASS.

ChatGPT 플랫폼 전체 대화창 자동열람 통로가 없으면 해당 항목만 PARTIAL_PASS_PLATFORM_ACCESS_HOLD로 남긴다. **이 HOLD는 다른 WIC 실제 작업의 진행을 막는 critical blocker로 취급하지 않는다.**
