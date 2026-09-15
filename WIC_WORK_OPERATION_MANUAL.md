# WIC Work 운영 매뉴얼

## 1. 최상위 원칙

`CHAT = CONTROL / DECISION`

`WORK = PHYSICAL EXECUTION / MEASUREMENT`

`OVERLAP = 0`

채팅과 Work가 같은 일을 두 번 하지 않는다. 채팅에서 판단할 수 있는 일은 Work에 넘기지 않는다. Work는 채팅에서 이미 확정한 실행명세를 물리적으로 실행하고 실제 결과를 측정하는 역할만 한다.

사용자는 작업자가 아니라 Observer다. 사용자에게 조사, 명령 실행, 테스트, 상태 전달, 반복 handoff, Work 크레딧 감시를 맡기지 않는다.

## 2. NORMAL_MODE — 채팅 전용 업무

다음은 반드시 채팅에서 끝낸다. Work에서 다시 수행하지 않는다.

- 과거 기록·현재 상태·직접 증거 확인
- 문제/HOLD/PARTIAL/FAIL/stale-state 판정
- 중복·이미 해결·기존 PASS 제거
- 원인 분석
- 해결방법 결정
- 외부 완성부품 검색·비교·선정
- 기존 검증부품 재사용 판단
- 언어·runtime·환경·의존성 호환성 판단
- 정확한 수정 파일과 수정 위치 확정
- 입력/출력 계약 확정
- 실제 테스트 입력 확보
- EXPECTED 결과 확정
- 회귀시험 범위와 PASS/HOLD 조건 확정
- 실행 순서 확정
- Work 실패 결과의 원인 분석 및 다음 수정안 결정
- 최종 Work 실행명세 작성

### Work 진입 7-GATE

다음 7개가 모두 확정되기 전에는 Work를 실행하지 않는다.

1. 무엇을 고칠지 확정
2. 정확한 파일 확정
3. 정확한 수정 위치 확정
4. 사용할 해결책/부품 확정
5. 언어·runtime·환경 호환성 확정
6. 실제 테스트 입력 확보
7. EXPECTED 결과 확정

하나라도 없으면 Work 금지. 채팅에서 해결하거나 HOLD한다.

## 3. NORMAL_MODE — Work 전용 업무

Work는 판단하지 않는다. 아래의 물리 작업만 수행한다.

- 지정 파일의 지정 변경
- 지정 프로그램/명령의 실제 실행
- 지정 테스트의 실제 실행
- ACTUAL 결과 수집
- 채팅이 고정한 EXPECTED와 ACTUAL의 기계적 비교
- 실제 배포
- 배포된 위치 smoke test
- commit
- push
- remote read-back
- SAFE_CHECKPOINT 저장 및 read-back

Work가 수행한 검증은 새로운 해결책을 판단하기 위한 조사가 아니라, 채팅에서 정한 EXPECTED가 실제로 나왔는지를 측정하는 검증이다.

## 4. Work에서 절대 하지 않는 일

- 원인 재조사
- 해결방법 재판단
- 후보 탐색·비교
- 외부 검색
- 새 부품 검색
- 환경·호환성 재판단
- 수정 위치 탐색
- 테스트 설계
- EXPECTED 변경
- 범위 확대
- 기존 PASS 전체 재시험
- 이미 검증된 자산의 불필요한 재검증
- 실패 후 임의 수정
- 실패 후 새로운 해결책 탐색
- 사용자에게 테스트·명령 실행·상태 전달 요청
- 사용자의 반복 승인 요구

기존 검증 결과는 `SKIP_REUSE_VERIFIED`한다.

## 5. 실패 처리 — 채팅과 Work 완전 분리

Work에서 EXPECTED와 ACTUAL이 다르면 Work는 원인을 조사하지 않는다.

`EXPECTED 불일치 → ACTUAL/실패 위치/증거 저장 → HOLD → SAFE_CHECKPOINT → STOP`

그 다음 채팅이 ACTUAL 증거를 받아 다음을 수행한다.

`실패 원인 분석 → 해결방법 결정 → 수정 위치 확정 → 새 EXPECTED 확정 → 새 실행명세 작성`

그 후 필요한 경우에만 새 Work 회차에서 물리 실행한다.

즉, 실패 원인 분석과 재수정 판단은 항상 채팅 업무이며 Work 업무가 아니다.

## 6. Work 실행명세 최소 형식

Work에는 이미 결정된 내용만 전달한다.

- REPO / 실제 실행 위치
- FILES
- CHANGE — 정확히 무엇을 어떻게 변경할지
- INPUT
- EXPECTED
- REGRESSION — 유지되어야 할 기존 결과
- 실행 순서
- 금지 범위
- 최종 출력 증거

긴 배경설명, 후보 비교, 원인 추론 과정은 Work에 넣지 않는다.

기본 실행 체인:

`MODIFY → RUN → TEST/REGRESSION → EXPECTED↔ACTUAL → DEPLOY(if required) → COMMIT → PUSH → REMOTE READ-BACK → SAFE_CHECKPOINT → STOP`

EXPECTED 불일치 시:

`ACTUAL EVIDENCE → HOLD → SAFE_CHECKPOINT → STOP`

Work 내부 재판단·재설계·재검색·임의 재수정은 하지 않는다.

## 7. 크레딧 최소화 규칙

- Work는 채팅의 조사 도구가 아니다.
- Work에 후보 선택을 맡기지 않는다.
- 한 번의 Work 회차에는 채팅에서 완성된 독립 실행묶음만 넣는다.
- Work가 읽어야 할 범위를 정확한 파일/입력/명령으로 제한한다.
- 중간 보고를 요구하지 않는다.
- 기존 PASS는 재실행하지 않는다.
- 같은 내용을 채팅과 Work에서 각각 검토하지 않는다.
- 크레딧 사용량을 사용자가 계속 감시할 필요가 없도록 한다.
- 작은 Work 회차를 반복하면 매 회차 저장소 확인, 상태 확인, 실행환경 확인 등 초기 세팅이 반복되어 시간과 크레딧이 낭비될 수 있으므로 피한다.

## 8. NORMAL_COMPRESSED_CONTINUOUS_MODE — 평상시 압축 연속실행

이 모드는 비상모드가 아니다. 초기화 시각이 임박하지 않았지만 남은 시간과 Work 크레딧을 효율적으로 사용해야 할 때 적용하는 NORMAL_MODE의 실행 방식이다.

목적은 `채팅↔Work 왕복 횟수`와 `Work 초기 세팅 반복`을 줄이는 것이다.

원칙:

- 채팅에서 여러 독립 작업의 판단·해결책·7-GATE를 먼저 묶어서 완료한다.
- Work는 완성된 여러 실행묶음을 한 회차에서 연속 처리한다.
- 한 작업이 막혀도 다른 독립 작업의 실행명세가 완성되어 있으면 Work 전체를 끝내지 않는다.
- 막힌 작업은 `ACTUAL 증거 → HOLD 또는 NEEDS_CHAT_DECISION → SKIP`하고 다음 독립 작업으로 진행한다.
- Work는 막힌 작업의 원인을 연구하거나 새 해결책을 만들지 않는다.
- 기존 PASS는 즉시 SKIP한다.
- 가능한 변경은 묶어서 테스트하고 가능하면 ONE COMMIT / ONE PUSH / ONE REMOTE READ-BACK으로 끝낸다.
- 중간 보고와 중간 handoff를 최소화한다.
- 실행 가능한 독립 묶음을 모두 소진한 뒤 한 번만 채팅으로 결과를 반환한다.

압축 실행식:

`CHAT: 여러 작업 일괄 FIND/JUDGE/DESIGN/7-GATE`

`WORK: A 실행 → B 실행 → 막힌 C는 HOLD/SKIP → D 실행 → 묶음 TEST → ONE COMMIT/PUSH/READ-BACK → CHECKPOINT → RETURN ONCE`

금지:

- 압축을 이유로 Work가 조사·판단·설계 업무를 가져가는 것
- 실패한 항목을 Work 내부에서 임의 수정·재시도하는 것
- 단순히 크레딧을 소비하기 위한 반복 실행

시간이 충분한 평상시에도 실행 대상이 여러 개 준비되어 있으면 소규모 왕복보다 이 모드를 우선한다.

## 9. Observer 보호

목표:

- `USER_MANUAL_HANDOFF = 0`
- `MANUAL_STATE_HANDOFF = 0`
- `REPEAT_INSTRUCTION_REQUIRED = 0`
- `MANUAL_16_TO_44_HANDOFF = 0`

사용자는 Work 운영자·테스터·감시자가 아니다. 불가피한 보안 승인 또는 Work 실행 시작 외의 중간 조작을 요구하지 않는다.

## 10. USB / 로컬 경로

- USB는 USB에만 필요한 실제 artifact가 있다는 증거가 있을 때만 사용한다.
- USB/로컬 자료 자체를 검증하는 회차에서는 필요한 범위에 한해 사용할 수 있다.
- GitHub 정본으로 가능한 작업 때문에 USB 또는 I: 전체 조사를 선행하지 않는다.
- 필요한 경로·권한·입력은 채팅에서 먼저 확정한다.

## 11. NORMAL_MODE 종료 규칙

단일 실행묶음 NORMAL_MODE에서는:

`지정 실행 완료 또는 EXPECTED 불일치 → ACTUAL 결과/증거 출력 → SAFE_CHECKPOINT 저장 → checkpoint read-back → 즉시 자동중단`

NORMAL_COMPRESSED_CONTINUOUS_MODE에서는 한 lane의 EXPECTED 불일치가 다른 독립 lane까지 중단시키지 않는다. 실패 lane의 증거를 보존하고 HOLD/SKIP한 뒤 이미 실행명세가 완성된 다른 lane을 계속한다. 모든 준비된 lane 소진 후 SAFE_CHECKPOINT와 read-back을 수행하고 종료한다.

`MASTER_FIXED != RUNTIME_FIXED`

실제 배포가 필요한 작업은 저장소 수정만으로 완료 처리하지 않는다. 채팅에서 정한 배포·실사용 검증 범위까지 실제 증거가 있어야 한다.

## 12. EMERGENCY_CREDIT_EXPIRY_MODE — NORMAL_MODE와 별도

비상모드는 NORMAL_MODE가 아니다.

- 발동 조건: Work 사용량 초기화·소멸 시각이 임박하고, 잔여량을 이월할 수 없으며, 사용자가 비상모드를 명시적으로 승인한 경우에만 적용한다.
- 비상모드에서는 평상시 소규모 사용 제한을 일시 해제하되 사용자가 지정한 최소 reserve를 보존한다.
- 현재 독립적으로 실행 가능하고 실제 미완료를 닫는 작업만 병렬 처리한다.
- 기존 PASS는 `SKIP_REUSE_VERIFIED`하며 무의미한 반복시험·가짜 작업·사용량 소진 목적 작업은 금지한다.
- reserve 도달 또는 실행 가능한 독립 작업 소진 시 진행 중 원자 작업을 안전하게 닫고 종료한다.
- 비상모드 결과는 잔여작업 원장에 남긴다.
- 비상모드 종료는 WIC 전체 완료를 의미하지 않는다.
- 종료 즉시 NORMAL_MODE로 복귀한다.
- 다음 Work 회차는 반드시 채팅 선행작업 및 7-GATE 원칙을 다시 적용한다.

고정 문구:

`EMERGENCY_MODE 종료는 WIC 전체 완료를 의미하지 않는다. 비상모드 결과를 잔여작업 원장에 남긴 뒤 즉시 NORMAL_MODE로 복귀한다. 다음 Work 회차는 반드시 채팅 선행작업 및 7-GATE 원칙을 다시 적용한다.`

2026-09-14 승인 사례는 당시 비상상황에만 해당하며 NORMAL_MODE의 일반 운영기준으로 사용하지 않는다.

## 13. 2026-09-15 자동 폐루프 실제 검증 상태

### 현재 우선순위

개별 도구 개선보다 연결 인프라를 먼저 완성한다.

`배달원/외부입력 → TOOL016 → TOOL044 → 외부 부품 공급·검증 → 자동 순환 → 결과귀환 → 중앙상태 → 대량확장 → 마지막에 개별 도구 개선`

TOOL006/013/041/042/045 및 1년치 도구 작업은 현재 연결 인프라보다 뒤로 둔다.

### Issue #16 실제 E2E

AUTOMATIC_LOOP 전체 상태는 아직 `HOLD`이지만 앞쪽 폐루프 연결은 실제 PASS했다.

실제 성공 경로:

`Issue #16 → ingress → PRECHECK → material receipt → TARGET_REMOTE_PASS → TOOL044 inbox → atomic demands 3건 → result evidence → TOOL016 central ACK → remote read-back`

확정 상태:

- 배달원: PASS — Issue #16, ingress run `34833105286`
- PRECHECK: PASS
- Material decision: PASS — `NO_TARGET_DIFF_REQUIRED`; required hashes + validator + output gate 확인
- TOOL016: PASS — `TARGET_REMOTE_PASS`
- TOOL044 inbox/atomic routing: PASS — atomic demand 3건 생성
- TOOL044 ACK/결과귀환: PASS
- 중앙상태: PASS — `TOOL044_RESULT_RETURN_ACK`
- 사용자 수동전달: PASS / 0
- 외부공급/실제 component 검증: HOLD — Issue #16 cycle에서는 실행되지 않음
- WORKER_STALE_GAP: HOLD — 5분 cron 설정은 유효하지만 확인 시점 마지막 자연 실행은 `34815474673`
- missing pool persistence 2건: 코드·격리시험 PASS, 자연 scheduler 배포본 실행 증거 대기
- MASS_EXPANSION: HOLD — 선행 외부공급 실제 실행증거 부족

증거:

- E2E run: `34833117038`
- pipeline ID: `f8bc3e81228256cba56e`
- result SHA: `d2285cd4977917f55376c4fcb9798ce5c6041ca689b5433e6566ce65b2951f2b`
- 관련 commits: `86f9a83be`, `20185273a`, workflow-generated `caa475582`, final `f0f9b7381`
- push: PASS
- remote read-back: PASS
- SAFE_CHECKPOINT: `f0f9b7381f739058aed358dba7ae2c4a1cf33de4`

변경 파일:

- `.github/workflows/wic-github-issue-ingress.yml`
- `.github/workflows/wic-feedback-event.yml`
- `feedback_pipeline/tool044_atomic_watch.py`

### Material decision 고정 규칙

material-decision 안전 gate를 삭제하거나 우회하지 않는다. 기존 3값 계약만 사용한다.

- `TARGET_DIFF_APPLIED`
- `CENTRAL_DIFF_APPLIED`
- `NO_TARGET_DIFF_REQUIRED`

Issue #16에서는 기존 승인 지시와 실제 증거를 사용한 `NO_TARGET_DIFF_REQUIRED`가 PASS했다. required asset hashes, validator, output gate 증거가 없으면 PASS하지 않고 HOLD한다.

### 현재 다음 작업 — 44번 뒤 자동공장

이미 PASS한 배달원, PRECHECK, TOOL016→TOOL044, 결과귀환, 중앙 ACK를 다시 만들지 않는다.

현재 남은 핵심은 다음 순서다.

1. `WORKER_STALE_GAP` — 5분 자연 scheduler가 실제 지속 실행되는지 증거 확보
2. missing pool persistence — 후보가 0개여도 아래 2개 상태 파일 생성/유지/read-back 검증
   - `tool044_external_candidate_pool.json`
   - `tool044_verified_external_component_pool.json`
3. Issue #16에서 생성된 atomic demand 3건이 기존 TOOL044 cloud factory에 자연 수신되는지 검증
4. 기존 경로만 사용하여 `atomic queue → dynamic candidate discovery → external candidate → verified asset → verified composition` 실제 실행
5. 외부공급/검증 결과를 기존 result-return 접합으로 `TOOL044 → TOOL016 central return → ACK → central state → remote read-back` 귀환
6. 1~5 실제 지속순환 증거 확보 후에만 `MASS_EXPANSION` 진행

외부공급 lane의 실제 component가 검증되지 않았으면 PASS 금지다.

scheduler가 정상인데 자연 실행이 없고 새로운 원인판단이나 새 구조가 필요하면 Work가 임의 수정하지 않는다. `ACTUAL evidence → NEEDS_CHAT_DECISION/HOLD → 다음 독립 lane`으로 진행한다.

### missing-pool persistence 수정 상태

`feedback_pipeline/tool044_atomic_watch.py`에 후보가 0개여도 external/verified pool 상태를 저장하도록 하는 최소 수정이 검증되었다. 격리시험은 PASS했다. Issue E2E가 만든 원격 커밋과 충돌했을 때 최신 `origin/main` 위로 검증된 단일 수정을 rebase하여 push하는 방식만 허용했다. force push는 사용하지 않는다.

자연 scheduler에서 실제 파일 생성·유지·read-back이 확인되기 전에는 배포상태 전체 PASS로 승격하지 않는다.

### Work의 현재 실행범위

이번 연결 회차에서 Work가 할 수 있는 것은 이미 결정된 물리 실행과 측정뿐이다.

- 원격 main read-back
- 자연 TOOL044 cloud scheduler 실행증거 read-back
- 기존 worker 실행
- 기존 queue/pool/validator 경로의 실제 실행 및 측정
- 결과귀환 read-back
- 이미 검증된 missing-pool 최소 수정의 commit/push/read-back
- 조건 충족 시 기존 자산을 이용한 MASS_EXPANSION 실행

금지:

- 새로운 worker/scheduler/배달원/중앙시스템 설계
- 실패 원인의 Work 내부 연구
- 같은 실패방식 반복
- material-decision 안전 gate 우회
- TOOL006/013/041/042/045 및 1년치 도구 개선로 전환

### 현재 완료 판정 기준

앞쪽 폐루프 PASS만으로 `AUTOMATIC_LOOP=PASS`라고 하지 않는다.

다음이 실제로 모두 이어져야 전체 PASS 후보가 된다.

`실제 입력 → 배달원 → TOOL016 → TOOL044 → 자연 worker → 외부공급 → 실제 component 검증 → 결과귀환 → 중앙 ACK → remote read-back`

사용자 역할은 계속 Observer이며 목표는 `USER_WORK=0`, `USER_MANUAL_RELAY=0`이다.

## 14. 최종 운영식

`CHAT: FIND → JUDGE → DESIGN → FIX SPEC → TEST SPEC → EXPECTED`

`WORK: MODIFY → EXECUTE → MEASURE → RECORD → DEPLOY/PUSH → READ-BACK → CHECKPOINT → STOP`

`NORMAL_COMPRESSED_CONTINUOUS: CHAT에서 여러 실행묶음 완성 → WORK 한 회차에서 연속·압축 실행 → 막힌 lane만 HOLD/SKIP → 마지막에 한 번 반환`

`FAIL: WORK records ACTUAL → CHAT diagnoses and decides → new WORK executes only if required`

**채팅과 Work의 공통 판단업무는 0으로 유지한다.**
