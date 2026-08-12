# WIC OBSERVER STATUS

최종 갱신: 2026-08-13 07:29 KST
상태: ACTIVE / STRUCTURE_PASS / POST_STRUCTURE_PRIORITY
운영 규칙: `WIC_GLOBAL_OPERATING_RULES.md`
라우팅: `WIC_CHAT_ROUTING_REGISTRY.md`
실행상태: `WIC_EXECUTION_STATE.json`

## WIC 전체 자동 통합 기반 구조 — PASS
- 실제 사용자 피드백 `f2aeb4e8f5fac3c9618f`가 자동 분류(`PRIORITY_CHANGE`) → 충돌검사 → 4계층 라우팅 → canonical write → hash read-back까지 실제 처리됐다.
- `feedback_pipeline/state.json`의 `structure_pass=true`와 검증 run `31642596092` / job `94268523138`은 그대로 유효하다.
- 구조 PASS 재검증은 반복하지 않는다.

## 완료 작업 — 반복 금지
- integration core 구현/재구축/재요약.
- feedback ingest/normalize/route/conflict-dedup/canonical write/read-back.
- TOOL006/013 canonical apply/read-back/internal test evidence.
- TOOL001/002 verified repository + canonical apply/read-back.
- EMAIL_DB/TOOL007/TOOL037/WORK_GATE central lane ACK.
- revision-aware SKIP_UNCHANGED.
- controlled rollback/restart checkpoint 및 actual cross-target automatic restart E2E.
- TOOL001 parse repair와 syntax zero-error gate.
- TOOL002 actual bid business E2E.
- TOOL007 중앙 purpose-matching adapter GitHub 실행.
- 구조 PASS 재검증 run `31642596092`.
- P1 customer DB deterministic fixtures 및 P1→P2 deterministic handoff fixtures.

## 이번 실행 실제 확인/개선
- 최신 restart point를 먼저 읽고 구조 PASS 및 기존 HOLD 항목은 반복하지 않았다.
- TOOL013 실제 저장소 `obk369369-spec/13-excel-upload`의 본체 `index.html` blob `1277d2460f7790db40321248078522c19b62cbf1`과 기존 workflow를 다시 확인했다.
- 기존 `.github/workflows/external-evidence.yml`은 `validate-static-tool.mjs` 기반 정적/내부 validation 및 Pages 배포만 수행하며, 실제 업무 Excel 파일을 주입해 변환 결과를 비교하는 browser/business E2E 단계는 없다.
- File Library에서 실제 업무 메타데이터 자산과 규칙관리 자산은 확인했다. 특히 `37번_메타데이터_통합규칙관리.xlsx`에는 LP Information 1,148행, Market Monitor Global 2,582행, MarketsandMarkets 헤더행 2 등 실제 발행사별 구조 정보가 존재하고, `해외시장보고서_28개발행사_메타데이터_샘플검증_규칙잠금_V2.xlsx`에는 실제 원본 파일명/컬럼매핑이 존재한다.
- 그러나 현재 GitHub connector/runtime에서는 File Library의 실제 `.xlsx` 바이너리를 `13-excel-upload` 브라우저 실행에 직접 주입할 수 있는 file mount/connector 경로가 없고, 기존 GitHub workflow에도 실제 Excel fixture가 없다. 따라서 synthetic/static 파일을 새로 만들어 PASS로 위장하지 않고 TOOL013 BUSINESS E2E를 HOLD로 확정했다.
- 지시대로 TOOL013에서 막힌 뒤 즉시 TOOL006으로 이동했다. 실제 저장소 `obk369369-spec/06-toc-check`에서 본체 `index.html` blob `6d3fef9325e75b188b84d9c1a4888fce5ba112c9`, 기존 `tests/marketsandmarkets_historical_fixtures.json`, `external-evidence.yml` 존재를 확인했다. 현재 테스트 자산은 historical fixture 중심이므로 actual business TOC input E2E인지 추가 판정이 필요하다.

## 현재 실제 PASS
- WIC reusable automatic integration core: `PASS_INTERNAL_GITHUB_E2E`.
- actual feedback canonical processing/read-back: PASS.
- TOOL007 central purpose-matching adapter lane: PASS_INTERNAL_GITHUB_RUN.
- cross-target rollback/read-back/restart: PASS.
- TOOL002 actual bid business E2E: PASS.
- TOOL001 syntax repair gate: PASS.

## 구조 PASS 후 현재 HOLD
1. EMAIL_COLLECTION: 실제 고객 원본은 확인됐지만 GitHub/runtime에서 해당 로컬 DB를 읽는 actual runner/send-ready formatter가 식별되지 않음.
2. TOOL007 BUSINESS E2E: 목적 일치 adapter는 검증됐으나 실제 현재 고객 레코드 기반 업무 E2E 증거 없음.
3. TOOL001 BUSINESS E2E: repaired commit 기준 Chromium 재실행 dispatch 경로가 현재 capability에서 막힘.
4. TOOL037 BUSINESS E2E: 실제 목적 일치 production repository/runner 미식별.
5. TOOL013 BUSINESS E2E: 실제 업무 메타데이터 자산은 File Library에서 확인했지만 현재 runtime이 해당 `.xlsx` 바이너리를 GitHub/browser E2E에 주입할 수 없음. 기존 workflow는 static/internal validation뿐임.
6. TOOL006 BUSINESS E2E: 저장소/fixture/workflow는 확인했으나 historical fixture가 실제 업무 입력을 보존한 것인지, 실제 TOC input→정리→output/read-back 비교를 수행하는지 아직 검증 필요.
7. 제3자 외부검증 actual run/result 없음.

## 개선방법
- TOOL013: 새 synthetic fixture를 만들지 않는다. 실제 발행사 `.xlsx`가 connector file mount 또는 실행환경 파일로 접근 가능해지는 즉시 기존 `index.html`에 주입하고 input row/header → output row/header/content를 비교한다.
- TOOL006: 기존 historical fixture와 workflow를 먼저 읽어 실제 업무 원문 보존 여부 및 input→output 비교 여부를 판정한다. 실제 업무 기반이면 그대로 재사용하고, 단순 fixture이면 HOLD 후 다음 우선순위로 이동한다.
- EMAIL_COLLECTION/TOOL007/TOOL001/TOOL037: blocker 변화 없이는 동일 탐색 반복 금지.

## 최신 restart point
1. 구조 PASS는 재검증하지 않는다.
2. TOOL013 BUSINESS E2E는 `actual Excel binary injection path unavailable`로 HOLD; 동일 File Library 검색을 반복하지 않는다.
3. 다음 실행 항목은 TOOL006 actual business E2E 판정이다.
4. `obk369369-spec/06-toc-check/tests/marketsandmarkets_historical_fixtures.json`과 existing workflow/script가 실제 업무 TOC 입력→정리→출력 expected 비교를 하는지 read-back한다.
5. actual business evidence이면 run/job/artifact까지 확인한다. synthetic/historical-only이면 HOLD + 원인 + 개선방법을 기록하고, TOOL002는 이미 business PASS이므로 반복하지 않고 28~31로 이동한다.

## Work 크레딧 사용 게이트
- 구조는 PASS이므로 구조 재독해·재요약·재검색에 Work 사용 금지.
- 현재 Work 후보는 실제 파일 주입/브라우저 E2E처럼 Chat+GitHub connector로 실행이 막히는 부분만 해당한다.

## 독립검증 상태
- GitHub 내부 actual run/read-back/commit/artifact 증거: 있음.
- WIC 전체 구조: PASS_INTERNAL_GITHUB_E2E.
- 제3자 외부 PASS 증거: 없음 / 독립검증 HOLD.

이 파일은 계속 같은 `WIC_OBSERVER_STATUS.md`를 덮어써서 유지한다.
