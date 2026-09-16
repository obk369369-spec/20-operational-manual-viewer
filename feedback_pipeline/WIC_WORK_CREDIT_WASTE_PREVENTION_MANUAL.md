# WIC WORK 크레딧 낭비 방지 강제 매뉴얼

상태: ACTIVE / REQUIRED

## 0. 최우선 실행 원칙
`한번에 묶는다`는 사소한 명령을 한 command에 이어붙인다는 뜻이 아니다. **파일별 실행 경로 자체를 만들지 않는다.** Work는 mutation 전에 현재 범위의 모든 파일/ROOT/오류/미완료를 먼저 수집하고, 중복·PASS·변화 없는 HOLD·불필요 작업을 제거한 뒤 실제 변경만 원인/공통부품/공통시험/공통배포 기준의 큰 cross-file batch로 처리한다.

정상 형태:
`전체 범위 1회 확보 → 모든 오류 선수집 → DELETE_WASTE/SKIP_REUSE/HOLD_EXTERNAL 제거 → ACTUAL_WORK 통합 → cross-file 대량 수정 → 대량 로컬시험 → 실패 전체수집 → 대량 재수정/재시험 → 최소 GitHub 반영 → 필요한 cloud 검증 → 최종 read-back → 누락만 ZERO SCAN`

`FILE_BY_FILE_EXECUTION_PATH = DO_NOT_CREATE`
`ONE_FILE_ONE_OPERATION = FORBIDDEN`
`ONE_ERROR_ONE_OPERATION = FORBIDDEN`
`COLLECT_ALL_ERRORS_BEFORE_MUTATION = REQUIRED`
`CROSS_FILE_BATCH_REPAIR = REQUIRED`
`BATCH_TEST_AFTER_BATCH_MUTATION = REQUIRED`
`FAILURES_COLLECT_FIRST_THEN_BATCH_REPAIR = REQUIRED`
`NO_FILE_BY_FILE_EXECUTION = REQUIRED`

파일 A 조회→수정→시험→확인 후 파일 B로 넘어가는 방식은 금지한다. A/B/C를 각각 독립 명령으로 병렬 실행하는 것도 같은 낭비로 본다. 기술적 의존성 때문에 내부 순서가 반드시 필요한 경우만 예외이며, 그 경우에도 사용자/Work 왕복을 파일 단위로 쪼개지 않는다.

## 1. WASTE_INSTRUCTION_SCAN — 실행 전 강제
Chat/assistant가 만든 Work 지시문을 신뢰하지 않는다. Work 진입 프로그램이 현재 매뉴얼을 직접 읽고 지시문의 instruction/prompt/plan/execution_goal/restart_point/steps를 자동 검사한다. 사용자에게 SHA나 `scan_passed` 값을 입력시키지 않는다.

다음 소모 구조는 실행하지 않는다: 같은 목적 반복조회; ROOT/오류/파일 하나마다 별도 조회·수정·test·commit·push·cloud run·read-back; 이미 PASS/VERIFIED/REMOTE_VERIFIED/DEPLOYED_PASS 재확인; 조건 변화 없는 HOLD 재조사; 결과를 바꾸지 않는 status/log/checkpoint/fetch/diff/count 반복; 중간보고 후 재판단하는 작은 회차; 동일 실패/거부 명령의 원인변화 없는 재시도; 완료 상태에서 거부 명령 문구만 보고 재실행; 단순 정리/분류/요약을 Work로 넘김; 실제 변경 가능성 없는 항목 실행.

발견 시 소모 명령을 삭제하고 실제 작업을 큰 batch로 재압축한다. 소모 구조가 남으면 `STOP_WASTE_PLAN`으로 실행 전 차단한다. STOP은 사용자에게 사소한 명령을 승인시키기 위한 것이 아니다.

## 2. 절대 금지
- 오류 하나 발견 즉시 수정→배포 왕복 금지.
- 같은 ROOT/cause occurrence 개별 수정 금지.
- 같은 파일 작은 변경마다 열기/저장/commit 금지.
- 사소한 수정 하나마다 전체 테스트 금지.
- 실패 하나마다 즉시 재시험 금지; 실패들을 먼저 모은다.
- `1 ROOT = 1 commit/push/cloud run/read-back` 금지.
- 작은 수정마다 fetch/status/diff/add/commit/push 반복 금지.
- push 성공, cloud SUCCESS, remote read-back PASS를 같은 commit에서 반복 금지.
- `1회차 완료 → 보고 → 계속 → 2회차` 금지.
- 중간보고 때문에 실행 중단 금지.
- SAFE_CHECKPOINT 무시하고 처음부터 재조사 금지.
- 사용자에게 이미 가진 경로/ID/checkpoint 재질문 금지.
- 사용자가 같은 범위의 사소한 터미널 명령을 계속 승인하게 만들기 금지.
- TOOL044 READY_COMPONENT 부재 시 내부 신규개발 금지.
- 외부 조건 미변경 HOLD 반복 금지.

## 3. 실행 분류
실행 전 전체 항목을 `DELETE_WASTE`, `SKIP_REUSE`, `HOLD_EXTERNAL`, `ACTUAL_WORK` 네 종류로 분류한다. Work에는 ACTUAL_WORK만 넣는다. ACTUAL_WORK는 ROOT/cause/shared file/shared component/shared test/shared deploy 기준으로 최대한 합친다. 목표는 명령 수가 아니라 `실제 완료량 / 비싼 왕복` 최대화다.

## 4. 원격 왕복 예산
정상 batch 기본값: 초기 remote snapshot 최대 1회, batch push 원칙 1회, 호환 cloud 검증 workflow group당 원칙 1회, 최종 remote read-back 원칙 1회. 실제 batch 실패 때만 예외이며 실패들을 먼저 모아 repair batch로 만든다.

`ONE_ROOT_ONE_PUSH = FORBIDDEN`
`ONE_ROOT_ONE_CLOUD_RUN = FORBIDDEN`
`ONE_ROOT_ONE_READBACK = FORBIDDEN`
`REPEAT_PASS_CHECK = FORBIDDEN`
`UNCHANGED_HOLD_RETRY = FORBIDDEN`
`DENIED_COMMAND_BLIND_RETRY = FORBIDDEN`

## 5. STOP 게이트
조회/분류만 계속되고 대량 mutation으로 넘어가지 못하면 `STOP_WASTE_RECONNAISSANCE`. 사용량이 감소하는데 신규 ACTUAL_WORK closure가 거의 없으면 `STOP_LOW_CLOSURE_DENSITY`. 같은 commit/hash/결과에 push/run/read-back을 다시 하려 하면 `STOP_DUPLICATE_REMOTE_ACTION`. STOP 시 SAFE_CHECKPOINT를 보존하고 재개 때 처음부터 시작하지 않는다.

## 6. Chat/Work 책임
Chat은 저수준 파일별 shell 절차를 생성하지 않고 결과·금지조건·성공증거를 전달한다. 이미 완료된 증거는 SKIP_REUSE, 외부조건 미변경은 HOLD_EXTERNAL로 제외한다. Chat 지시문이 이 규칙을 위반해도 Work 시작 게이트가 `WASTE_INSTRUCTION_SCAN`으로 실행 전에 차단한다.

## 7. 완료 기준
최소 중복 증거로 최대 실제 미완료를 닫는다. 최종 ZERO SCAN은 미처리 ACTUAL_WORK, 변경 영향, 새 실패, 새로 풀린 외부 HOLD만 검사한다. 변화 없으면 재실행하지 않는다.

`WASTE_INSTRUCTION_SCAN = REQUIRED`
`DELETE_TRIVIAL_WORK_BEFORE_BATCH = REQUIRED`
`ACTUAL_WORK_ONLY_EXECUTION = REQUIRED`
`BATCH_BY_ROOT_CAUSE_SHARED_ASSET = REQUIRED`
`REMOTE_ROUNDTRIP_MINIMIZATION = REQUIRED`
`PASS_LOCK_UNTIL_IMPACTED = REQUIRED`
`HOLD_LOCK_UNTIL_CONDITION_CHANGED = REQUIRED`
`STOP_DUPLICATE_REMOTE_ACTION = REQUIRED`
`STOP_LOW_CLOSURE_DENSITY = REQUIRED`
