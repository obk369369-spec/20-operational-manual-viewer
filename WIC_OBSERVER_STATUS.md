# WIC OBSERVER STATUS

최종 갱신: 2026-08-13 12:24 KST
상태: ACTIVE / CORE_STRUCTURE_PASS / LATEST_FEEDBACK_TARGET_TEST_HOLD / PRE_WORK_GATE_VERIFIED
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## WIC 전체 자동 통합 기반 구조
- 기존 reusable integration core 자체의 PASS 증거는 유지한다: run `31642596092` / job `94268523138`.
- 구조 재구축·repository inventory·기존 PASS 재검증은 반복 금지다.
- 단, 새 feedback이 들어오면 그 feedback cycle은 canonical→target apply→target test까지 별도로 완료되어야 한다.

## 이번 실행 실제 새 변화
- 상태파일 갱신 이후 중앙 저장소에 새 사용자 규칙 commit `71dc67e867ebe3652db3bc50dbd2d3628ada4cc8` 및 `177a3159816e090e2a3d94ef7a927e32c05ae455`가 들어온 것을 change detection으로 확인했다.
- 내용: 보고서 정보는 실제 텍스트만 번역하고 이미지/그래프 해석 금지, 원문 위치 직접 대응, 고객용 TOC는 상위+하위까지만 표시하고 하하위 제외, 하위 한 단계 들여쓰기, 보고서 타이틀은 글로벌 범위만 허용하고 단일 지역 타이틀 제외.
- 기존 `feedback_pipeline/state.json`은 이 새 규칙을 아직 processed feedback으로 기록하지 않아 자동흡수 drift가 실제 발견됐다.
- 이 drift를 Work로 넘기지 않고 Chat+GitHub에서 기존 `pending_event.json → wic-feedback-event.yml → apply_feedback_event.py` 경로로 실제 재주입했다.
- ingest commit: `241414938359d79c089c2f0d086a868b3a6cfb10`.
- WIC feedback event actual run `31663661298`는 `completed/success`.
- canonical apply commit: `9f318a884f7def4d43870d89d762499ad7c5b623`.
- 새 feedback id: `b6acdbfd3bc4d0de1b66`; canonical revision: `11f7a751685aeaaf10cab428`.
- `feedback_pipeline/state.json` read-back에서 cursor가 `2026-08-13T12:08:38+09:00`로 전진했고 processed_feedback_ids에 새 feedback id가 추가된 것을 확인했다.
- target manifest read-back 결과 영향 대상은 `TOOL001`, `TOOL006` 두 개이며 둘 다 `APPLY_CHANGED_SCOPE / HOLD_TARGET_APPLY`로 정확히 분류됐다.

## 대상 도구 적용 진행
- TOOL006 `WIC_TARGET_APPLY_STATE.json`을 새 canonical revision으로 갱신: commit `aa22334b89334d44946161074732322e1708234e`.
- TOOL006 GitHub internal validation run `31663710333`이 생성됐으며 현재 GitHub 실행 대기/진행 상태이므로 PASS로 올리지 않는다.
- TOOL001 `WIC_TARGET_APPLY_STATE.json`을 새 canonical revision으로 갱신: commit `df270fff93627deaca19a72452a8b229be5d8ddf`.
- TOOL001 Pages run `31663715593`이 생성됐지만 Pages 배포만으로 기능적 BUSINESS E2E를 증명하지 않으므로 PASS 증거로 사용하지 않는다.

## 현재 실제 PASS
- reusable automatic integration core: `PASS_INTERNAL_GITHUB_E2E`.
- latest feedback EVENT→NORMALIZE→ROUTE→CONFLICT/DEDUP→CANONICAL_WRITE→READ_BACK: PASS.
- Work credit gate + exact handoff generator: `PASS_INTERNAL_GITHUB_RUN`.
- resumable Work exit checkpoint contract/template: `PASS_INTERNAL_GITHUB_RUN`.
- TOOL002 actual bid business E2E: PASS.
- 기존 cross-target rollback/read-back/restart E2E: PASS.

## 현재 HOLD
- latest feedback `b6acdbfd3bc4d0de1b66`: `TARGET_REVISION_READ_APPLY / TEST_EVIDENCE` 미완료.
- TOOL001: revision ACK는 반영했으나 새 규칙(글로벌 타이틀 필터, TOC 2단계, text-only report info)이 실제 브라우저 동작에서 적용되는지 E2E 필요. 기존 Work 후보와 동일하게 browser business E2E가 필요하다.
- TOOL006: revision ACK 반영 후 internal validation run 완료/결과 확인 필요. 또한 실제 original→user-approved-final golden pair가 없으므로 BUSINESS E2E는 기존 HOLD 유지.
- TOOL013: actual `.xlsx` binary injection business E2E는 기존 `WORK_ELIGIBLE` 유지.
- EMAIL_COLLECTION / TOOL007 BUSINESS / TOOL037 / TOOL006 BUSINESS: 공식 input/runner/golden evidence가 생길 때까지 Work credit 사용 금지.
- 제3자 독립검증: actual external run/result 없음.

## 최신 restart point
1. `31663710333` TOOL006 internal validation 결과를 확인한다. success면 revision ACK/test evidence를 기록하고, 실패면 원인·개선방법·restart point를 HOLD로 남긴다.
2. TOOL001은 Pages 성공 여부와 별개로 기능 BUSINESS E2E가 아직 필요하므로 Work 진입 시 첫 실행을 `TOOL001 browser business E2E`로 유지한다. 이번 새 feedback의 글로벌 타이틀 필터·TOC 2단계·text-only source 규칙을 반드시 검증 항목에 추가한다.
3. TOOL001 완료 또는 명확 HOLD 후 `TOOL013 actual .xlsx injection business E2E`를 실행한다.
4. Work 종료 전 artifact `9166037482`의 `WORK_EXIT_RESUMABLE` checkpoint 필드에 실제 evidence/rollback/exact_next_step을 채워 read-back한다.
5. 완료된 구조·inventory·TOOL002·기존 rollback E2E는 반복하지 않는다.

## Work 크레딧 사용 게이트
- rule reread/re-summary/repository re-search에는 사용 금지.
- Chat/GitHub에서 가능한 target ACK/read-back/internal validation은 Work 전에 끝낸다.
- 실제 browser/file injection처럼 현재 연결에서 막히는 E2E에만 Work를 사용한다.
- 기존 handoff 기준 증거: run `31660617974` / job `94324484253` / artifact `9166037482`.

## 독립검증 구분
- GitHub actual commit/run/read-back 증거는 내부 플랫폼 검증이다.
- 제3자 외부 run/result가 없으므로 독립검증 PASS로 표시하지 않는다.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
