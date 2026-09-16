# WIC WORK 크레딧 낭비 방지 강제 매뉴얼

상태: ACTIVE / REQUIRED
기준 실패사례: 2026-09-16 Work 실행에서 큰 작업을 한 번에 압축한다는 목적과 달리, 사소한 조회·수정·GitHub 왕복·검증이 반복되어 사용량 대비 신규 완료량이 낮았던 사건.

## 0. 가장 중요한 뜻

`한번에 묶는다`는 말은 사소한 명령 20개를 모아 한꺼번에 실행한다는 뜻이 아니다.

먼저 사소하고 불필요한 작업 자체를 삭제한다. 그 뒤 실제 결과를 바꾸는 큰 작업만 최대한 많이 묶어 한 번에 처리한다.

정상 형태:
`불필요 작업 삭제 → 실제 미완료만 선별 → 같은 원인/파일/도구/시험/배포끼리 큰 묶음 → 대량 수정 → 대량 로컬시험 → 실패 모음 → 대량 재수정/재시험 → 최소 GitHub 반영 → 필요한 cloud 검증 → 마지막 증거 확인`

## 1. 지시문 자체 사전검사 — 실행 전에 강제

Chat/assistant가 만든 Work 지시문을 그대로 신뢰하지 않는다. 실행 전에 먼저 `WASTE_INSTRUCTION_SCAN`을 수행한다.

다음 중 하나라도 있으면 그 소모성 명령은 실행하지 않는다.
- 같은 목적의 조회를 여러 번 시킴
- ROOT/오류/파일 하나마다 별도 조회·수정·test·commit·push·cloud run·read-back을 시킴
- 이미 PASS/VERIFIED/REMOTE_VERIFIED/DEPLOYED_PASS인 것을 다시 확인시킴
- 조건이 변하지 않은 HOLD를 다시 조사시킴
- 결과를 바꾸지 않는 status/log/checkpoint/fetch/diff/count 조회를 반복시킴
- 중간보고 뒤 다시 판단하고 다시 실행하도록 작은 단계들을 늘어놓음
- 동일 실패 명령을 원인 변화 없이 재시도시킴
- 이미 목적 상태가 달성됐는데 `직전 거부 명령 다시 요청` 같은 문장 때문에 완료 명령을 재실행시킴
- 단순 정리/분류/요약을 비싼 Work 실행으로 넘김
- 실제 변경 가능성이 없는 항목을 실행 queue에 넣음

처리:
1. 불필요한 소모 명령은 삭제한다.
2. 필요한 실제 작업은 더 큰 BATCH로 재압축한다.
3. 재압축 뒤에도 같은 소모 구조가 남으면 `STOP_WASTE_PLAN`으로 실제 실행을 시작하지 않는다.
4. STOP은 사용자에게 사소한 명령을 하나씩 승인시키기 위한 것이 아니다. 낭비 계획을 막기 위한 것이다.

## 2. 절대 금지 목록

### A. 조회/조사 낭비
- 이미 확인한 PASS를 또 확인 금지.
- 같은 GitHub run/status/checkpoint/ledger/manifest를 변화 없이 반복 조회 금지.
- 같은 로그를 다른 명령으로 다시 읽어 같은 결론을 확인 금지.
- 파일 존재 확인 뒤 내용 확인 뒤 hash 확인 뒤 remote 확인을 의미 없이 각각 독립 왕복으로 만들지 않는다.
- 전체 repo/전체 USB/전체 기록을 현재 작업과 무관하게 전수검색 금지.
- 이미 canonical evidence가 충분한 항목에 추가 증거를 장식처럼 붙이기 위한 조사 금지.
- 외부 계정/기기/고객/자료가 없어서 풀 수 없는 HOLD 반복 탐색 금지.
- 검색 결과가 없고 조건도 안 바뀌었는데 검색어만 조금 바꿔 반복 금지.
- SKIP_REUSE 판정을 받은 항목을 새 세션이라는 이유로 재검사 금지.

### B. 수정 낭비
- 오류 하나 발견 즉시 수정→배포 왕복 금지.
- 같은 ROOT/cause의 occurrence를 각각 따로 고치기 금지.
- 같은 파일을 작은 변경마다 여러 번 열고 저장하고 commit하기 금지.
- timestamp/줄바꿈/정렬/자동생성 noise를 기능 수정으로 취급 금지.
- 이미 검증된 부품을 다시 만들거나 비슷한 부품을 중복 개발 금지.
- TOOL044에서 READY_COMPONENT가 없는데 새 부품 개발 금지.
- 실제 결과와 관계없는 리팩터링/정리/이름변경을 긴급 Work에 끼워 넣기 금지.

### C. 테스트 낭비
- 사소한 수정 하나마다 전체 테스트 금지.
- 같은 binary/hash/commit을 같은 조건에서 반복 시험 금지.
- PASS한 테스트를 `혹시 모르니` 재실행 금지.
- 서로 독립적인 변경을 직렬로 하나씩 테스트하지 말고 가능한 범위에서 batch test.
- 테스트 실패 시 같은 명령 즉시 반복 금지. 실패 원인을 먼저 모은다.
- ZERO SCAN을 전체 작업 처음부터 재시험하는 절차로 사용 금지. ZERO SCAN은 누락 탐지이며 누락/변경분만 재실행한다.

### D. Git/GitHub 낭비
- `1 ROOT = 1 commit` 금지.
- `1 ROOT = 1 push` 금지.
- `1 ROOT = 1 cloud run` 금지.
- `1 ROOT = 1 remote read-back` 금지.
- 작은 수정마다 fetch/status/diff/add/commit/push 반복 금지.
- 같은 결과를 보기 위한 API 조회와 git fetch를 둘 다 수행 금지.
- 이미 push 성공 증거가 있는데 다시 push 금지.
- 이미 cloud SUCCESS가 있는데 같은 commit의 cloud run 재실행 금지.
- 이미 remote read-back PASS가 있는데 같은 commit 재-fetch 금지.
- main이 자동 writer 때문에 움직일 때 매번 뒤쫓아 rebase/fetch 반복 금지. 가능한 한 하나의 동기화 창과 큰 batch를 사용한다.
- 거부된 명령을 재요청하기 전에 목표 상태가 이미 달성됐는지 확인한다. 달성됐으면 `SKIP_ALREADY_ACHIEVED`.

### E. Work 흐름 낭비
- 논리적 회차를 실제 사용자/Work 왕복 회차로 만들기 금지.
- `1회차 완료 → 보고 → 계속 → 2회차` 금지.
- 중간보고를 만들기 위해 실행을 멈추기 금지.
- 작은 오류 하나 때문에 독립 작업 전체를 멈추기 금지. 치명적 공유 blocker가 아니면 failure bucket에 모으고 독립 lane 계속.
- 반대로 실제 의존성이 있는 작업을 억지 병렬화해 충돌/재작업 만들기 금지.
- 실행 도중 발견한 비핵심 새 아이디어 때문에 현재 작업을 버리고 scope 확대 금지.
- 이미 끝난 단계로 되돌아가 처음부터 재시작 금지.
- 컨텍스트 압축 뒤 기존 checkpoint를 무시하고 재조사 금지.
- Work에서 장시간 `무엇을 할지`만 연구하고 실제 mutation을 늦추기 금지.

### F. HOLD/SKIP/외부조건 낭비
- 외부 증거가 없는 HOLD를 내부 계산으로 PASS 만들려는 시도 금지.
- 실제 고객 evidence가 없는데 고객 E2E를 가짜 fixture로 완료 주장 금지.
- 실제 device가 없는데 device evidence를 반복 시도 금지.
- 실제 cloud provider가 하나뿐인데 multi-cloud failover를 반복 실행해 PASS 주장 금지.
- 번역 runtime/license/category contract 등 필수조건 부재가 확인되면 조건 변화 전 반복 금지.
- HOLD가 하나 있다고 독립적으로 가능한 다른 큰 작업까지 멈추기 금지.

### G. 승인/복구 낭비
- 사용자가 같은 범위의 사소한 터미널 명령을 계속 승인하게 만들기 금지.
- 명령 거부 후 무조건 동일 명령 재요청 금지.
- `다시 요청`이라는 사용자 문장을 문자 그대로 따라 이미 완료된 결과까지 재실행 금지.
- restore/reset/rebase 같은 복구 명령은 실제 필요한 변경을 잃지 않는지 먼저 최소 diff 분류 후 사용.
- 복구 후 전체 테스트 처음부터 재실행 금지. 영향받은 묶음만 시험.
- Work 중단 후 새 Work에서 모든 상태를 다시 찾기 금지. SAFE_CHECKPOINT 재사용.

### H. 보고/문맥 낭비
- Work 중간마다 긴 자연어 보고 생성 금지.
- 같은 상태를 표/문장/JSON으로 중복 보고 금지.
- 거대한 지시문으로 같은 규칙을 여러 표현으로 반복 금지.
- 실행에 필요 없는 역사 설명을 Work prompt에 넣기 금지.
- 로그 전문을 읽고 다시 요약하고 다시 분류하는 다단계 금지. 필요한 증거만 추출.
- 사용자에게 이미 시스템이 가진 경로/ID/checkpoint를 다시 묻기 금지.

## 3. 숨은 낭비 패턴 검사

아래도 명시적 반복이 아니어도 낭비로 판정한다.
- 명령 이름은 다르지만 같은 사실을 확인하는 경우
- 파일은 다르지만 같은 ROOT를 각각 처리하는 경우
- 도구는 다르지만 동일 shared component 수정으로 함께 해결되는 경우
- test 이름은 다르지만 같은 behavior를 중복 증명하는 경우
- 여러 workflow가 같은 commit을 중복 검증하는 경우
- 성공 증거가 있는데 형식만 다른 영수증을 만들려고 재실행하는 경우
- `꼼꼼함`을 반복 확인으로 해석하는 경우
- `전수조사`를 관련 없는 범위 확장으로 해석하는 경우
- `계속`을 이미 완료된 단계 반복으로 해석하는 경우
- `재개`를 처음부터 다시 시작으로 해석하는 경우
- `검증`을 같은 결과를 여러 방식으로 확인하는 것으로 해석하는 경우
- `병렬`을 무조건 모든 작업 동시 실행으로 해석하는 경우
- `압축`을 사소한 명령을 단순히 한 command에 이어붙이는 것으로 해석하는 경우

## 4. 정상 BATCH 규칙

실제 실행 전에 항목을 다음 네 종류로만 나눈다.
- `DELETE_WASTE`: 결과에 필요 없는 일. 실행하지 않음.
- `SKIP_REUSE`: 기존 증거 재사용. 실행하지 않음.
- `HOLD_EXTERNAL`: 조건 변화 전 실행하지 않음.
- `ACTUAL_WORK`: 실제 결과를 바꿀 작업. 이것만 Work 실행 대상으로 사용.

ACTUAL_WORK는 다시 ROOT/cause/shared file/shared component/shared test/shared deploy 기준으로 최대한 합친다.

사소한 명령 수를 줄이는 것이 목표가 아니라 `실제 완료량 / 비싼 왕복`을 최대화한다.

## 5. 왕복 예산 — 기본 강제값

정상 batch 하나의 기본 원격 왕복 예산:
- 초기 필요한 remote snapshot: 최대 1회
- batch push: 원칙 1회
- 호환되는 cloud 검증: workflow group당 원칙 1회
- 최종 remote read-back: 원칙 1회

예외는 실제 batch 실패가 있을 때만 허용한다. 그 경우에도 실패 하나마다 즉시 왕복하지 않고 실패들을 먼저 모아 한 번의 repair batch로 만든다.

`ONE_ROOT_ONE_PUSH = FORBIDDEN`
`ONE_ROOT_ONE_CLOUD_RUN = FORBIDDEN`
`ONE_ROOT_ONE_READBACK = FORBIDDEN`
`REPEAT_PASS_CHECK = FORBIDDEN`
`UNCHANGED_HOLD_RETRY = FORBIDDEN`
`DENIED_COMMAND_BLIND_RETRY = FORBIDDEN`

## 6. 크레딧 이상소모 STOP 게이트

크레딧 절약 자체보다 많은 실제 작업 완료가 우선이다. 그러나 완료량 없이 크레딧만 줄어드는 것은 즉시 차단한다.

- 실행 초기에 조회/분류만 계속되고 대량 실제 변경으로 넘어가지 못하면 `STOP_WASTE_RECONNAISSANCE`.
- 사용량이 눈에 띄게 감소하는데 새로 닫힌 ACTUAL_WORK가 거의 없으면 `STOP_LOW_CLOSURE_DENSITY`.
- 같은 ROOT/cause 때문에 두 번째 원격 repair 왕복이 필요해지면 즉시 다른 실패까지 모아 재압축한다. 세 번째 동일형 왕복을 자동 진행하지 않는다.
- 이미 완료된 commit/push/cloud run/read-back을 다시 하려는 순간 `STOP_DUPLICATE_REMOTE_ACTION`.
- STOP 발생 시 이미 완료된 결과는 보존하고 SAFE_CHECKPOINT에서 멈춘다. 처음부터 다시 하지 않는다.

## 7. 지시문 생성자(Chat/assistant)의 책임

Work만 감시하는 것으로 끝내지 않는다. Work 지시문을 만드는 Chat/assistant도 아래를 지켜야 한다.
- 사소한 상태확인 명령을 세부 단계로 나열하지 않는다.
- 필요한 결과와 금지조건을 중심으로 쓴다.
- 이미 완료된 증거는 prompt에 `SKIP_REUSE`로 잠근다.
- HOLD는 release condition이 없으면 실행 queue에서 뺀다.
- 동일 목적의 명령을 표현만 바꿔 중복 삽입하지 않는다.
- `꼼꼼히`, `전부`, `끝까지`라는 말 때문에 불필요한 재검증을 추가하지 않는다.
- Work가 알아서 판단할 수 있는 사소한 shell 절차를 길게 강제하지 않는다.
- 실제 결과를 바꾸지 않는 보고용 작업을 실행단계에 넣지 않는다.

Chat이 이를 어겨도 Work의 WASTE_INSTRUCTION_SCAN이 차단해야 한다.

## 8. 2026-09-16 실패 재발 방지 규칙

다음 형태는 명시적으로 재발 금지한다.
`조회 → 수정 → push → run → read-back → 작은 오류 발견 → 즉시 수정 → sync/rebase → push → run → read-back`

대신:
`필요한 최소 초기상태 1회 → 가능한 오류/실제 작업 충분히 수집 → 불필요/SKIP/HOLD 제거 → 큰 repair batch → 대량 local test → 실패 모음/대량 repair → batch push → 필요한 cloud 검증 → final read-back`

이번 실패에서 확인된 핵심:
- 큰 작업을 넣었다고 자동으로 큰 batch가 되는 것이 아니다.
- 사소한 실행단계를 prompt에 넣는 순간 Work가 그것을 실제 할 일로 수행할 수 있다.
- 따라서 사소한 낭비 단계는 `묶는 대상`이 아니라 `삭제 대상`이다.
- Chat의 잘못된 지시도 실행 전에 차단되어야 한다.

## 9. 완료 조건

완료는 `명령을 많이 수행함`이 아니다.
완료는 `실제 미완료 항목을 최대한 많이 닫고, 필요한 증거를 최소 중복으로 확보함`이다.

최종 ZERO SCAN에서는 다음만 본다.
- 빠진 ACTUAL_WORK가 있는가
- 변경 때문에 기존 PASS가 실제 영향받았는가
- 새 실패가 남았는가
- 외부 HOLD의 release condition이 새로 충족됐는가

아니면 재실행하지 않는다.

WASTE_INSTRUCTION_SCAN = REQUIRED
DELETE_TRIVIAL_WORK_BEFORE_BATCH = REQUIRED
ACTUAL_WORK_ONLY_EXECUTION = REQUIRED
BATCH_BY_ROOT_CAUSE_SHARED_ASSET = REQUIRED
REMOTE_ROUNDTRIP_MINIMIZATION = REQUIRED
PASS_LOCK_UNTIL_IMPACTED = REQUIRED
HOLD_LOCK_UNTIL_CONDITION_CHANGED = REQUIRED
STOP_DUPLICATE_REMOTE_ACTION = REQUIRED
STOP_LOW_CLOSURE_DENSITY = REQUIRED
SAFE_CHECKPOINT_ON_WASTE_STOP = REQUIRED
