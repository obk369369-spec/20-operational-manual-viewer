# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 17:17 KST
상태: ACTIVE / STRUCTURE_FIRST / TOOL006_TARGET_E2E_PASS / TOOL013_APPLY_PENDING_TEST / DISPATCHER_IMPLEMENTED / OVERALL_HOLD
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 최우선 1순위
- 2026-08-13 Work 사용 전후 최우선은 개별 도구가 아니라 **WIC 전체 자동 통합 기반 구조의 실제 완성 + E2E 검증**이다.
- 단순 파일/스크립트/commit 존재는 구조 PASS가 아니다.
- 실제 새 피드백 1건이 `자동 분류 → 충돌/중복 → canonical GitHub write/read-back → 대상 적용 → 실제 테스트/증거 → restart/rollback` 전체를 통과해야 구조 PASS다.
- 구조 PASS 후 우선순위는 **이메일 수집 → 7번 고객 컨택 판단 → 1번 중간/최종 안내서 → 37 메타데이터 → 13 엑셀 자동 업로드 → 6번 목차 정리 → 2번 입찰 → 28~31 → 나머지 등록 도구/주요 업무창**이다.

## 이번 실행에서 실제 개선한 부분
### 1. 최신 restart point 기준으로만 재개
- `WIC_OBSERVER_STATUS.md`와 `WIC_EXECUTION_STATE.json`을 먼저 read-back했다.
- 이미 PASS된 ingest / registry routing / conflict-dedup / canonical writer / canonical GitHub transport / TOOL006 target E2E는 반복하지 않았다.
- 시작점은 `MULTI_TARGET_AND_ROLLBACK = HOLD`였다.

### 2. 두 번째 실제 repository target TOOL013 apply/read-back
- 대상 저장소: `obk369369-spec/13-excel-upload`.
- 기존 `WIC_RULE_SOURCE.md`가 중앙 `WIC_GLOBAL_OPERATING_RULES.md` 단일원본을 가리키는 것을 read-back했다.
- 이번 피드백은 기능변경이 아니라 global priority/work-gate 변경이므로 `index.html` 기능을 억지 수정하지 않았다.
- `WIC_TARGET_APPLY_STATE.json`을 생성해 canonical revision `fa09bcdec96669d97ef3a18f` 소비 상태를 실제 영속화했다.
- feedback_id: `f2aeb4e8f5fac3c9618f`.
- target apply commit: `8f2f1f3e57c9cbba7fd5a0621ba3419d63feee0b`.
- read-back blob: `eeaa796667dd2c78bb2913f5cbf01bf6d11f8052`.
- 현재 커넥터에서 push-triggered workflow run/result가 아직 확인되지 않아 **TOOL013 TEST PASS는 HOLD**다.

### 3. 범용 target/lane adapter registry 실제 추가
- 새 파일: `feedback_pipeline/target_adapter_registry.json`.
- 실제 확인된 repository target만 등록:
  - TOOL006 → `obk369369-spec/06-toc-check`
  - TOOL013 → `obk369369-spec/13-excel-upload`
- repository가 없는 lane은 별도 adapter로 정의:
  - EMAIL_DB
  - TOOL037
  - WORK_GATE
- TOOL001 / TOOL002 / TOOL007은 저장소를 추측하지 않고 unresolved/fail-closed로 유지.
- commit: `d2053d31878cfa7aa950743a1ee460e6bbcfb28f`.

### 4. 범용 deterministic dispatcher 실제 구현
- 새 파일: `feedback_pipeline/target_dispatcher.py`.
- 기능:
  - manifest + verified adapter registry를 읽어 target별 실행계획 생성
  - repository target / non-repository lane 분리
  - `SKIP_UNCHANGED` 지원
  - 검증되지 않은 target은 `HOLD_NO_VERIFIED_ADAPTER`로 fail-closed
  - 중복 target/누락 revision/잘못된 action 검증
- commit: `706695f3d6cce83bc526e9f514554b55d3a1a12c`.
- `.github/workflows/cross-chat-feedback-audit.yml`에 dispatcher fixture 실행을 연결했다.
- workflow wiring commit: `0edee4ba5c92953fe1735efb587c3ae8407e2e97`.
- 실제 workflow run/result가 확인되기 전 **dispatcher CI PASS 주장 금지**.

### 5. 중앙 manifest / revision cache / restart state 환류
- `target_apply_manifest.json`에 TOOL013 apply/read-back을 `APPLIED_PENDING_TEST_EVIDENCE`로 기록.
- EMAIL_DB / TOOL037 / WORK_GATE는 `ADAPTER_DEFINED_PENDING_EXECUTION`.
- TOOL001 / TOOL002 / TOOL007은 `HOLD_NO_VERIFIED_ADAPTER`.
- manifest commit: `9265654aa6d811057f612c11890879aeb57b3b1a`.
- `feedback_pipeline/state.json` target revision cache에 TOOL013 pending evidence를 추가.
- state commit: `291f6e9d2f5168bc4ff97cde7339376c44e517be`.
- `WIC_EXECUTION_STATE.json` restart point도 최신으로 전진.
- execution-state commit: `e94394239f98c641099a1790b961eba336180094`.

## 현재 운영준비도
### 실제 PASS
- 새 피드백 ingest/normalize/route.
- conflict/dedup.
- canonical single-source GitHub write/read-back.
- canonical revision 생성.
- TOOL006 repository target apply/read-back/actual GitHub validation/test/evidence.
- TOOL006 결과 중앙 cache 환류.

### 실제 진행 중
- TOOL013 canonical revision target apply/read-back: 완료.
- TOOL013 actual target workflow test/evidence: 확인 대기/HOLD.
- 범용 dispatcher/adapter code + CI wiring: 구현 완료, actual CI run evidence 확인 전 HOLD.

### 아직 HOLD
1. EMAIL_DB / TOOL037 / WORK_GATE lane adapter actual apply/evidence.
2. TOOL001 / TOOL002 / TOOL007 verified target adapter/repository 확인 및 actual apply/test.
3. `SKIP_UNCHANGED` 다중 target actual evidence.
4. 통제된 실패 target의 rollback hook actual evidence.
5. `last_success_stage`부터 실패→재개 actual evidence.
6. 위 gate 충족 전 전체 구조 PASS 금지.

## blocker
### MULTI_TARGET_TEST_AND_FAILURE_PATH = HOLD
- TOOL013 state write/read-back은 성공했지만 actual push workflow run/result 증거가 아직 없다.
- lane adapter는 정의했지만 실제 실행증거가 없다.
- TOOL001/002/007은 검증된 저장소가 없어 fail-closed 상태다.
- rollback/restart 실패경로를 실제로 실행하지 않았다.

## 개선방법
- TOOL013 commit `8f2f1f3e57c9cbba7fd5a0621ba3419d63feee0b`의 actual GitHub workflow run/result를 먼저 확인하고 중앙 cache에 환류한다.
- EMAIL_DB / TOOL037 / WORK_GATE는 저장소를 새로 만들지 않고 central lane ack/evidence 방식으로 실제 실행한다.
- TOOL001/002/007은 기존 증거에서 실제 target을 확인하기 전 adapter를 만들지 않는다.
- 통제된 실패 fixture 1건으로 rollback + last_success_stage restart를 실제 검증한다.

## 최신 restart point
1. canonical writer / canonical transport / TOOL006 apply / TOOL013 state write / dispatcher 설계는 반복하지 않는다.
2. **TOOL013 actual workflow run/result 확인**부터 시작한다.
3. 성공이면 target state + central manifest/cache에 run/job/result 증거를 환류한다.
4. 다음으로 EMAIL_DB / TOOL037 / WORK_GATE lane adapter를 실제 실행/증거화한다.
5. TOOL001/002/007은 verified target 증거가 있을 때만 연결한다.
6. 이후 controlled failure 1건으로 rollback/restart actual E2E를 검증한다.
7. routed target/lane + failure-path gate 충족 뒤에만 구조 PASS 검토.

## Work 크레딧 사용 게이트
- 기존 규칙 재독해/재요약/저장소 반복검색에는 Work 사용 금지.
- 이미 PASS된 앞단이나 TOOL006 재개발 금지.
- Work는 Chat/GitHub에서 실제로 막히는 cross-target 실행, 실제 E2E, 외부 권한/환경 구간에만 사용.

## 독립검증 상태
- GitHub 내부 Actions/run/read-back: TOOL006에 실제 증거 있음.
- TOOL013: read-back 증거는 있으나 actual workflow result 확인 전 HOLD.
- 제3자 외부검증: **없음 / HOLD**.
- 실제 외부 run/result URL 전 독립검증 PASS 금지.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
