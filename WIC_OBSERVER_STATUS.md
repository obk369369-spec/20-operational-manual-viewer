# WIC OBSERVER STATUS

최종 갱신: 2026-08-13 00:24 KST
상태: ACTIVE / STRUCTURE_FIRST / OVERALL_HOLD
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 최우선 1순위
- 개별 도구 개발보다 WIC 전체 자동 통합 기반 구조 자체의 실제 완성 + E2E 검증이 우선이다.
- 구조 PASS 후 순서는 이메일 수집 → 7번 → 1번 → 37 → 13번 → 6번 → 2번 → 28~31 → 나머지 등록 도구/주요 업무창이다.
- 실제 실행증거 없는 항목은 PASS로 표시하지 않는다.

## 완료 작업 — 반복 금지
- 새 피드백 ingest/normalize/route, conflict/dedup, canonical GitHub write/read-back.
- TOOL006/013 canonical revision apply/read-back/test/evidence.
- TOOL001/002 verified repository 확인 및 canonical revision apply/read-back.
- EMAIL_DB/TOOL037/WORK_GATE lane ACK actual workflow evidence.
- TOOL001/002/006/013 revision-aware SKIP_UNCHANGED actual workflow evidence.
- controlled rollback/restart checkpoint fixture actual workflow evidence.
- integration-core evidence artifact actual 생성.
- TOOL001/002 Pages built 경로 확인 및 Deno failure 별도 분리.
- TOOL001 actual browser E2E run `31606697361` / job `94147360821` / artifact `9145425244` 실패 증거 확인.

## 이번 실행 실제 개선
- 최신 `WIC_OBSERVER_STATUS.md`와 restart point를 먼저 읽고 완료 작업은 반복하지 않았다.
- TOOL001 실패 artifact `9145425244`를 실제 다운로드/read-back했다. 결과는 candidateCount=0, executionPass=false, pageErrors=6, middle→right 전파는 성공이었다.
- `index.html`에서 실제 손상 좌표를 좁혔다: 잘린 정규식 2곳 + `pickClickedTarget()` 뒤에 함수 밖으로 튀어나온 중복 코드 조각 1곳.
- TOOL001 저장소에 `.github/workflows/tool1-minimal-syntax-repair.yml`을 commit `8a442b63846d8959ef38478c2b8520f284db6dca`로 추가했다. 전체 재작성 없이 확인된 손상만 패치하고 모든 inline script를 `node --check` 하는 최소 복구 workflow다.
- actual repair workflow run `31612083645`, job `94165673831`이 실행됐다. 확인된 3개 손상 패치는 적용 단계에서 성공했지만 parse gate에서 추가 손상 5개가 검출되어 index commit은 의도대로 차단됐다.
- 추가 실제 parse failure 좌표: script-001 line 334 `chapterNodes` 잘린 regex, script-002 line 15 quote 충돌, script-008 line 86 잘린 문자열, script-010 line 329 잘린 `.join()` 문자열, script-012 line 24 `map[pub]||map.` 손상, script-015 line 63 잘린 배열 문자열. 따라서 현재 TOOL001 본체 수정은 아직 HOLD이며 잘못된 부분을 commit하지 않았다.

## 현재 실제 PASS
- 중앙 integration core의 기존 PASS 항목은 그대로 유지한다.
- 이번 실행에서 새로 PASS로 올린 것은 없음.
- 최소복구 workflow 자체의 '손상 좌표 패치 단계'는 success였지만 전체 parse gate 실패이므로 TOOL001 수정 PASS로 취급하지 않는다.

## 아직 HOLD
1. TOOL001 actual business browser E2E: 기존 run `31606697361` FAIL.
2. TOOL001 최소복구: run `31612083645` / job `94165673831` = FAIL. 추가 5개 parse 손상 때문에 commit 차단.
3. TOOL001 실제 공개 보고서 데이터 진위/상세페이지/가격 검증.
4. TOOL002 실제 입찰 target input→run→output→expected 테스트 증거.
5. TOOL007 최신 고객 컨택 판단 목적에 맞는 actual target/adapter.
6. 실제 cross-target controlled failure → repository rollback/read-back → last_success_stage restart E2E.
7. 제3자 외부검증 actual run/result.
8. 위 gate 전 전체 구조 PASS 금지.

## blocker / 개선방법
- TOOL001: 전체 재작성 금지. run `31612083645` 로그가 준 6개 parse 좌표만 순서대로 복구하고, 모든 inline script `node --check`가 0 error일 때만 index.html commit 허용. 그 commit이 생기면 기존 `tool1-business-browser-e2e.yml`이 자동 실행되므로 동일 actual browser E2E의 candidate 5 + middle/right 전파 + pageErrors 0을 확인한다.
- parse repair가 즉시 끝나지 않으면 TOOL001 HOLD 좌표를 유지하고 TOOL002 실제 공고 E2E로 이동한다.
- TOOL002: Pages/static evidence 재검증 금지. 실제 공고 업무 입력 E2E만 추가한다.
- TOOL007: 목적 일치 verified target 확인 전 추측 adapter 연결 금지.
- rollback: fixture PASS 반복 금지. 실제 repository rollback/read-back/restart만 남음.

## 최신 restart point
1. canonical writer / TOOL006 / TOOL013 / TOOL001/002 apply / dispatcher / revision cache / audit workflow 반복 금지.
2. TOOL001 기존 browser E2E run `31606697361` 재실행 반복 금지.
3. TOOL001 repair run `31612083645` 로그의 parse failure 좌표부터 이어서 최소 수정한다.
4. 모든 inline script `node --check` 0 error → index commit → 자동 browser E2E → artifact read-back 순서.
5. 전체 재작성 금지, 이미 성공한 middle→right 경로 보존.
6. 즉시 복구가 막히면 TOOL002 실제 입찰 E2E로 이동.
7. TOOL007 목적 일치 target → 실제 cross-target rollback/read-back/restart E2E 순서.
8. 전체 gate 통과 후에만 구조 PASS 검토.

## Work 크레딧 사용 게이트
- 기존 규칙 재독해·재요약·반복검색에 사용 금지.
- Chat+GitHub에서 막히는 actual 실행/E2E와 확인된 SyntaxError 최소수정에만 사용.

## 독립검증 상태
- GitHub 내부 actual run/read-back/artifact 증거: 있음.
- TOOL001 browser E2E: FAIL 증거 있음.
- TOOL001 minimal syntax repair: FAIL 증거 있음; commit은 안전하게 차단됨.
- 제3자 외부 PASS 증거: 없음 / HOLD.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
