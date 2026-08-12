# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 16:26 KST
상태: ACTIVE / STRUCTURE_FIRST / CANONICAL_TRANSPORT_PASS / TOOL006_TARGET_E2E_PASS / OVERALL_HOLD
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 최우선 1순위
- 2026-08-13 Work 사용 전후 최우선은 개별 도구가 아니라 **WIC 전체 자동 통합 기반 구조의 실제 완성 + E2E 검증**이다.
- 단순 파일/스크립트/commit 존재는 구조 PASS가 아니다.
- 실제 새 피드백 1건이 `자동 분류 → 충돌/중복 → canonical GitHub write/read-back → 대상 적용 → 실제 테스트/증거 → restart/rollback` 전체를 통과해야 구조 PASS다.
- 구조 PASS 후 우선순위는 **이메일 수집 → 7번 고객 컨택 판단 → 1번 중간/최종 안내서 → 37 메타데이터 → 13 엑셀 자동 업로드 → 6번 목차 정리 → 2번 입찰 → 28~31 → 나머지 등록 도구/주요 업무창**이다.

## 이번 실행에서 실제 개선한 부분
### 1. 최신 restart point를 먼저 읽고 완료 작업 반복 금지 준수
- `WIC_OBSERVER_STATUS.md`와 `WIC_EXECUTION_STATE.json`을 먼저 read-back했다.
- observer가 더 최신이었고 중앙 실행상태는 `CANONICAL_WRITE`에 머물러 있어 stale 상태임을 확인했다.
- 이미 PASS된 ingest / registry-source routing / conflict-dedup / canonical writer / canonical GitHub transport는 재개발하지 않았다.
- 실제 시작점은 최신 observer의 `TARGET_REVISION_READ_APPLY = HOLD`였다.

### 2. 첫 실제 cross-repository target apply 수행 — TOOL006
- 대상 저장소: `obk369369-spec/06-toc-check`
- 기존 `WIC_RULE_SOURCE.md`가 중앙 단일원본을 가리키는 것을 read-back했다.
- 현재 피드백은 `PRIORITY_CHANGE`이므로 TOOL006 기능코드를 억지로 수정하지 않고, 중앙 규칙 복제 없이 해당 canonical revision을 실제 소비했다는 target state만 영속화했다.
- 새 상태파일: `WIC_TARGET_APPLY_STATE.json`
- canonical revision: `fa09bcdec96669d97ef3a18f`
- feedback_id: `f2aeb4e8f5fac3c9618f`
- target apply commit: `3961fd8c59b8dc08100204d4437e217460f292b2`
- 최초 read-back blob: `cb508b04baf13bbdc3ae5c0ae0614a99ea591a0f`
- 로컬 규칙 복제본은 생성하지 않았다.

### 3. TOOL006 실제 target test 성공
- target apply push로 기존 실제 검증 workflow가 자동 실행됐다.
- workflow: `GitHub platform evidence (not independent)`
- run: `31573547418`
- validation job: `94040506272`
- 결과: `completed / success`
- 실제 성공 단계: checkout → Node setup → real source static validation → artifact preserve → internal gate.
- Pages deployment job `94040536319`: success.
- permanent GitHub evidence archive job `94040536379`: success.
- target state에 이 실행증거를 기록한 commit: `d3d49c57b4415dcd93377f517fb111c44f9f4526`.
- 이는 **GitHub 내부 실행증거**이며 제3자 독립검증으로 표시하지 않는다.

### 4. 중앙 manifest / revision cache에 TOOL006 결과 환류
- `feedback_pipeline/target_apply_manifest.json`에서 TOOL006을 `APPLIED_TEST_PASS_INTERNAL_GITHUB`로 갱신했다.
- manifest commit: `0fc35179862e071805c6452df0105f4febb215e0`.
- `feedback_pipeline/state.json`의 `target_revision_cache.TOOL006`에 canonical revision, target commit/read-back, workflow run/job 결과를 영속화했다.
- central state commit: `631039fd52c3f37c6ec9a7d4662351f0622a474d`.
- checkpoint는 `TEST_EVIDENCE`까지 전진했지만 다른 routed target/lane과 rollback 증거가 남아 status는 HOLD를 유지했다.

### 5. stale 중앙 restart state 교정
- `WIC_EXECUTION_STATE.json`을 실제 최신 상태로 갱신했다.
- TOOL006 target E2E를 완료 작업 목록에 추가하고 다시 수행하지 않도록 잠갔다.
- execution-state commit: `d1c31ad145348c90703f43fbf2ce88c8b3609899`.

## 현재 운영준비도
### PASS된 부분
- 실제 새 피드백 ingest/normalize/route.
- conflict/dedup 판정.
- canonical single-source GitHub write.
- canonical GitHub read-back.
- canonical revision 생성.
- 실제 cross-repository target 1개(TOOL006)의 revision apply/read-back.
- TOOL006 actual GitHub validation/test/evidence.
- TOOL006 target revision cache 중앙 환류.

### 아직 HOLD인 부분
1. TOOL001 / TOOL002 / TOOL007 / TOOL013 등 나머지 독립 저장소 target의 범용 apply adapter/dispatcher 및 실제 증거.
2. EMAIL_DB / TOOL037 / WORK_GATE처럼 독립 저장소가 아닌 lane의 apply 방식.
3. 변경이 없으면 SKIP하고 변경된 scope만 적용하는 공통 dispatcher의 다중 target 실제 증거.
4. 실패 target에 대한 rollback hook 실제 실행증거.
5. last_success_stage부터 restart되는 실패→재개 실제 증거.
6. 위 조건 충족 전 구조 전체 PASS 금지.

## blocker
### MULTI_TARGET_AND_ROLLBACK = HOLD
- 원인: TOOL006 한 대상의 실제 apply/test는 성공했지만, 하나의 피드백이 route한 나머지 target/lane으로 같은 패턴을 재사용하는 자동 dispatcher와 실패경로 증거가 아직 없다.
- 따라서 첫 cross-repository target E2E는 PASS지만 **WIC 전체 자동 통합 구조 자체는 아직 PASS가 아니다.**

## 개선방법
- TOOL006에서 검증된 `central revision → target state → target actual test → central evidence/cache` 패턴을 범용 dispatcher/adapter contract로 일반화한다.
- 다음 독립 저장소 target은 TOOL013을 우선 사용한다.
- 독립 저장소가 없는 EMAIL_DB / TOOL037 / WORK_GATE는 repository write를 억지로 만들지 않고 lane-specific apply/evidence adapter를 정의한다.
- 같은 canonical revision이면 `SKIP_UNCHANGED`; 바뀐 경우만 impacted scope를 적용한다.
- 통제된 실패 fixture 1건을 만들어 rollback/restart가 실제로 작동하는지 증거를 남긴다.

## 최신 restart point
1. `apply_feedback_event.py`, `canonical_writer.py`, TOOL006 target apply를 다시 만들지 않는다.
2. TOOL006에서 성공한 패턴을 재사용해 **공통 target dispatcher/adapter**를 다음 실행 가능한 범위에서 구현한다.
3. 두 번째 실제 repository target은 TOOL013을 우선한다.
4. TOOL013에서 `canonical revision read → last_applied 비교 → changed-scope apply/ack → actual target test → evidence → central cache`를 실제 실행한다.
5. EMAIL_DB / TOOL037 / WORK_GATE lane adapter를 저장소 생성 없이 정의/실행 가능한 형태로 연결한다.
6. 통제된 실패 1건으로 rollback + last_success_stage restart를 실제 검증한다.
7. routed target/lane과 failure-path gate를 충족한 뒤에만 구조 PASS를 검토한다.

## Work 크레딧 사용 게이트
- 기존 규칙 재독해/재요약/저장소 반복검색에는 사용 금지.
- 이미 PASS된 ingest/registry/conflict/canonical writer/canonical transport/TOOL006 apply 재개발 금지.
- Work는 다중 target cross-repository apply, 실제 target 실행/E2E, 외부 권한/환경 때문에 Chat+GitHub에서 막히는 구간에만 사용한다.

## 독립검증 상태
- GitHub 내부 Actions/run/read-back: 실제 증거 있음.
- 제3자 외부검증: **없음 / HOLD**.
- 실제 외부 run/result URL이 생기기 전 독립검증 PASS 금지.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
