# WIC OBSERVER STATUS

최종 갱신: 2026-08-12 23:27 KST
상태: ACTIVE / STRUCTURE_FIRST / OVERALL_HOLD
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## 현재 최우선 1순위
- 2026-08-13 Work의 최우선은 개별 도구가 아니라 WIC 전체 자동 통합 기반 구조 자체의 실제 완성 + E2E 검증이다.
- 구조 PASS 후 순서는 이메일 수집 → 7번 → 1번 → 37 → 13번 → 6번 → 2번 → 28~31 → 나머지 등록 도구/주요 업무창이다.
- 실제 실행증거 없는 항목은 PASS로 표시하지 않는다.

## 이번 실행 실제 개선
- 최신 중앙 상태와 restart point를 먼저 읽고 완료 작업은 반복하지 않았다.
- TOOL001 기존 `tool1-verified-data-regression.yml`은 production-data guard만 실행하며 실제 고객 입력→화면 생성 업무 E2E가 아님을 read-back으로 확인했다.
- TOOL001에 실제 Chromium 브라우저로 고객 입력(`반도체 세정`) → 생성 버튼 → 후보 5개 → 가운데 상세 → 오른쪽 안내서 전파를 검사하는 `.github/workflows/tool1-business-browser-e2e.yml`을 추가했다. 최초 commit `ed312b6aac120dc62fae44d79b7fb9c34c661859`.
- 최초 actual run `31606579319`, job `94146945489`의 harness module-resolution 오류를 분리 진단하고 TOOL001 본체는 건드리지 않은 채 harness만 commit `f487b6052d3dd09913ce9379c0cc8841ba2077f2`로 수정했다.
- 수정 후 actual browser run `31606697361`, job `94147360821`은 Chromium 설치/로컬 페이지 실행/실제 고객 입력/생성 클릭/결과 캡처까지 실행 완료했고 evidence artifact `9145425244`를 실제 생성했다.
- actual 결과: 가운데/오른쪽 안내서에는 `Semiconductor Cleaning...`, `MarketsandMarkets`, `2026년 1월`, `180`, 가격, 링크, 목차가 실제 전파됐으나 후보 카드 count는 `0`이어서 expected 5를 통과하지 못했다.
- 같은 실제 브라우저 실행에서 `SyntaxError: Invalid regular expression: missing /`, `missing ) after argument list`, `Invalid or unexpected token`, `Unexpected token ')'` 등 page JavaScript SyntaxError 6건이 수집됐다. 따라서 Pages build success와 별개로 TOOL001 현재 브라우저 실행 본체는 PASS가 아니다.

## 현재 실제 PASS
- 실제 새 피드백 ingest/normalize/route.
- conflict/dedup.
- canonical GitHub write/read-back.
- TOOL006 repository apply/read-back/test/evidence.
- TOOL013 repository apply/read-back/test/evidence.
- TOOL001/002 verified repository 확인 및 canonical revision apply/read-back.
- EMAIL_DB/TOOL037/WORK_GATE lane ACK actual workflow evidence.
- TOOL001/002/006/013 revision-aware SKIP_UNCHANGED actual workflow evidence.
- controlled rollback/restart checkpoint fixture actual workflow evidence.
- integration-core evidence artifact actual 생성.
- TOOL002 canonical apply commit에 대한 archived static STRUCTURE_PASS evidence read-back.
- TOOL001 canonical apply commit의 GitHub Pages build/deployment success 및 public built 상태 확인.
- TOOL002 public GitHub Pages built 상태 및 canonical apply commit의 external-evidence workflow success 확인.

## 아직 HOLD
1. TOOL001 actual business browser E2E: run `31606697361` / job `94147360821` / artifact `9145425244` = FAIL. 후보 5 expected 대비 실제 0 + page SyntaxError 6건.
2. TOOL001 실제 공개 보고서 데이터의 진위/상세페이지/가격 검증은 별도 HOLD. 현재 E2E 값 생성 성공을 실데이터 PASS로 오인 금지.
3. TOOL002 실제 입찰 target input→run→output→expected 테스트 증거.
4. TOOL001/002 Deno deploy failure는 별도 경로 이슈로 유지하되 GitHub Pages 성공 경로와 분리한다.
5. TOOL007 최신 고객 컨택 판단 목적에 맞는 actual target/adapter.
6. 실제 cross-target controlled failure → repository rollback/read-back → last_success_stage restart E2E.
7. 위 gate 전 전체 구조 PASS 금지.

## blocker / 개선방법
- TOOL001: 실제 browser E2E가 본체 SyntaxError 6건과 candidate list 0을 검출했다. 누적된 중복/충돌 script 중 parse error 발생 script를 좌표화하고, 실제 실행에 필요한 최종 canonical script 경로를 보존하면서 깨진/deprecated script를 제거 또는 격리한 뒤 동일 run을 재실행해야 한다. 가운데/오른쪽 전파가 이미 동작하므로 전체 재작성 금지.
- TOOL001 실데이터: E2E에 표시된 제목/발행일/페이지/가격/검색 URL은 현재 화면 생성값이며 독립적으로 검증된 실제 보고서 데이터가 아니다. verified public detail source를 붙이기 전 데이터 PASS 금지.
- TOOL002: GitHub Pages built와 external-evidence workflow success는 실제 공고 업무 E2E가 아니다. 기존 static evidence를 재사용하고 실제 업무 입력 E2E만 추가한다.
- TOOL007: 기존 저장소 목적 불일치. 목적 일치 target 확인 전 추측 adapter 연결 금지.
- rollback: fixture actual workflow는 PASS했지만 실제 cross-target repository rollback은 미검증. 안전한 테스트 target에서 통제 실패→rollback→read-back→restart 증거 필요.

## 최신 restart point
1. canonical writer / TOOL006 / TOOL013 / TOOL001/002 apply / dispatcher / revision cache / audit workflow 구현 반복 금지.
2. audit run `31587057240`, job `94083205492`, artifact `9137534969` 재검증 반복 금지.
3. TOOL001 Pages 배포, harness 오류, actual browser run `31606697361` 재실행 반복 금지.
4. 다음 TOOL001 작업은 artifact `9145425244`와 browser pageErrors를 기준으로 SyntaxError script 좌표를 좁혀 깨진/deprecated script만 최소 수정/격리 → 같은 actual browser E2E 재실행.
5. TOOL001 전체 재작성 금지. 이미 성공한 middle→right 전파 경로 보존.
6. TOOL001 수정이 즉시 불가능하면 HOLD 원인/좌표를 유지하고 TOOL002 실제 공고 업무 E2E로 즉시 이동.
7. TOOL007은 목적 일치 verified target 확인 전 HOLD.
8. 실제 cross-target controlled failure → repository rollback/read-back → last_success_stage restart E2E.
9. 전체 gate 통과 후에만 구조 PASS 검토.

## Work 크레딧 사용 게이트
- 기존 규칙 재독해·재요약·반복검색에 Work 사용 금지.
- 이미 완료된 앞단과 내부 fixture 재개발 금지.
- Chat+GitHub에서 실제로 막히는 actual 실행/E2E 및 위 SyntaxError 최소수정에만 Work 사용.

## 독립검증 상태
- GitHub 내부 actual run/read-back/artifact 증거: 있음.
- TOOL001 actual browser business E2E: FAIL 증거 있음 — run `31606697361`, job `94147360821`, artifact `9145425244`.
- GitHub Pages 실제 배포 상태: TOOL001 built/success, TOOL002 built.
- Deno actual deploy status: TOOL001 failure / TOOL002 failure (별도 경로).
- 제3자 외부 PASS 증거: 없음 / HOLD.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
