# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 19:17 KST
상태: ACTIVE / STRUCTURE_FIRST / OVERALL_HOLD
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 최우선 1순위
- 2026-08-13 Work의 최우선은 개별 도구가 아니라 **WIC 전체 자동 통합 기반 구조 자체의 실제 완성 + E2E 검증**이다.
- 구조 PASS 후 순서는 **이메일 수집 → 7번 고객 컨택 판단 → 1번 중간/최종 안내서 → 37 메타데이터 → 13 엑셀 자동 업로드 → 6번 목차 정리 → 2번 입찰 → 28~31 → 나머지 등록 도구/주요 업무창**이다.
- 실제 실행증거 없는 항목은 PASS로 표시하지 않는다.

## 이번 실행 실제 개선
### 1. 완료 작업 반복 금지 준수
- 최신 `WIC_OBSERVER_STATUS.md`와 `WIC_EXECUTION_STATE.json`을 먼저 read-back했다.
- canonical writer, TOOL006/013 E2E, TOOL001/002 apply, dispatcher 기본설계는 다시 만들지 않았다.

### 2. target revision cache 실제 추가
- 새 실행자산: `feedback_pipeline/target_revision_cache.json`.
- TOOL001/002/006/013에 이미 적용된 canonical revision `fa09bcdec96669d97ef3a18f`을 영속화했다.
- commit: `c99eef6861f48e3ff2d438d1c12ce42000d12f8e`.
- 목적: 같은 canonical revision을 다시 처리할 때 repository write를 반복하지 않고 `SKIP_UNCHANGED`로 보내기 위함이다.

### 3. 다중 target `SKIP_UNCHANGED` 실제 코드 연결
- `feedback_pipeline/target_dispatcher.py`가 revision cache를 읽도록 변경했다.
- 동일 revision이면 manifest가 APPLY_CHANGED_SCOPE이어도 repository target을 다시 쓰지 않고 `SKIP_UNCHANGED`로 분기한다.
- TOOL001/002/006/013 네 target을 동시에 검증하도록 assertion을 추가했다.
- commit: `fccceb97c425f2e47607611d45af3ada5c415b74`.
- 단, 최신 GitHub Actions actual run/result가 아직 확인되지 않아 **다중 target SKIP_UNCHANGED 실행 PASS는 아직 HOLD**다.

### 4. rollback/restart 통제 실패 fixture 추가
- 새 실행자산: `feedback_pipeline/restart_rollback_fixture.py`.
- `READ_BACK`까지 성공한 상태에서 `TARGET_REVISION_READ_APPLY` 통제 실패를 발생시키고, 이전 target revision 복구 + `last_success_stage` 다음 단계부터 재개하는지를 검증한다.
- commit: `6b0dbc47d2dab02d693ff75f6296c21fd4b08f94`.
- 내부 fixture일 뿐 실제 cross-target 실패/복구 증거는 아니므로 전체 rollback PASS로 간주하지 않는다.

### 5. 중앙 audit workflow 보강
- `cross-chat-feedback-audit.yml`에 revision-aware dispatcher, rollback/restart fixture, evidence artifact 업로드를 연결했다.
- commit: `feef20eec8b800f5f44231c7721bbf85b69c0f07`.
- 현재 commit combined status에서 Deno deploy success는 확인됐지만 GitHub Actions run/job/artifact ID는 아직 노출되지 않았다.
- 따라서 lane ACK / multi-target SKIP_UNCHANGED / rollback fixture의 **GitHub Actions actual evidence는 HOLD**다.

## 현재 운영준비도
### 실제 PASS
- 실제 새 피드백 ingest/normalize/route.
- conflict/dedup.
- canonical GitHub write/read-back.
- TOOL006 repository target apply/read-back/test/evidence.
- TOOL013 repository target apply/read-back/test/evidence.
- TOOL001 / TOOL002 verified repository 확인 및 canonical revision apply/read-back.

### 구현 완료 / actual run evidence 확인 전 HOLD
- EMAIL_DB / TOOL037 / WORK_GATE lane ACK + artifact workflow.
- TOOL001/002/006/013 revision cache 기반 multi-target `SKIP_UNCHANGED`.
- controlled rollback/restart fixture + artifact workflow.

### 아직 HOLD
1. 최신 audit workflow actual run/job/artifact 증거.
2. TOOL001 / TOOL002 실제 target test/evidence.
3. TOOL007 최신 고객 컨택 판단 목적에 맞는 actual target/adapter.
4. 실제 cross-target controlled failure → rollback → `last_success_stage` restart E2E.
5. 위 gate 전 전체 구조 PASS 금지.

## blocker / 개선방법
- **Audit actual evidence HOLD:** commit은 존재하지만 GitHub Actions run/result ID가 현재 조회 경로에서 아직 확인되지 않는다.
  - 개선: 다음 실행에서 run/job/artifact가 노출되는 즉시 read-back하고 중앙 증거에 반영한다.
- **TOOL001/002 test evidence HOLD:** canonical revision 적용/read-back은 끝났지만 실제 도구 검증 결과가 없다.
  - 개선: 기존 저장소의 실제 검증경로를 재사용해 test evidence를 확보한다.
- **TOOL007 target mismatch HOLD:** 기존 07 저장소는 최신 고객 컨택 판단 목적과 다르다.
  - 개선: 목적 일치 target을 찾기 전 추측 adapter 연결 금지.
- **Rollback actual E2E HOLD:** 현재는 통제 실패 fixture만 존재한다.
  - 개선: 실제 target apply 단계에서 안전한 통제 실패 1건을 만들고 rollback/read-back/restart 증거를 확보한다.

## 최신 restart point
1. canonical writer / TOOL006 / TOOL013 / TOOL001/002 apply / dispatcher 기본설계 / revision cache 구현 반복 금지.
2. audit workflow commit `feef20eec8b800f5f44231c7721bbf85b69c0f07`의 actual run/job/artifact 확인.
3. 성공 시 lane ACK + multi-target SKIP_UNCHANGED + rollback fixture 증거를 중앙 상태에 환류.
4. TOOL001 / TOOL002 actual target test/evidence 확보.
5. TOOL007은 목적 일치 verified target 확인 전 HOLD.
6. 실제 cross-target controlled failure → rollback → restart E2E.
7. 전체 gate 통과 후에만 구조 PASS 검토.

## Work 크레딧 사용 게이트
- 기존 규칙 재독해/재요약/반복검색에 Work 사용 금지.
- 이미 완료된 앞단과 도구 적용을 재개발하지 않는다.
- Chat+GitHub에서 실제로 막히는 cross-target/lane 실행, 권한/환경, actual E2E에만 Work를 사용한다.

## 독립검증 상태
- GitHub 내부 실행/read-back 증거: 일부 있음.
- 제3자 외부검증: **없음 / HOLD**.
- 실제 외부 run/result URL 전 독립검증 PASS 금지.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
