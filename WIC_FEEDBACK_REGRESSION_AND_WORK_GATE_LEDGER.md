# WIC FEEDBACK → REGRESSION / CHAT → WORK GATE LEDGER

상태: ACTIVE / NON-NORMATIVE EVIDENCE LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
영구 파이프라인: `HISTORY_EVIDENCE -> CLASSIFY -> RULE/EXPECTED_OUTPUT -> FIXTURE/ERROR_HASH -> ACTUAL_PATCH -> VERIFY -> READ_BACK -> REUSE -> RESTART_POINT`

## Work gate
G1 Chat/Files, G2 GitHub, G3 일반 runtime 중 하나라도 가능하면 `WORK_DEFER_DENIED`. G1~G3 모두 불가 + 구체적 Work-only blocker + exact handoff package가 있을 때만 `WORK_ELIGIBLE`. 과거규칙 재독해/파일검색/터미널 가능 테스트를 Work로 보내면 `CREDIT_WASTE_FAIL`.

## P1 customer DB / send-order
- last_processed_evidence: 이메일수집 V5/V4/본표·스팸회피 공통 규칙 + 2026-08-10 사용자 CORRECTION.
- implementation: `customer_pipeline/customer_db_state_machine.py`, commit `61052ebbd9e5bf1c8c12bab40e7f0c481cd84430`.
- verification: `PASS: 9 deterministic P1 fixtures`.
- still HOLD: 실제 회사 customer DB artifact/runner 연결, 제목·첫 문장 3종 분산 formatter 연결.
- next_unprocessed_evidence: 실제 회사 customer DB/runner 또는 send-ready formatter가 식별될 때만 재개; 동일 문서 재독해 금지.
- Work gate: `WORK_DEFER_DENIED`.

## P2 TOOL007 고객 컨택 판단
- implementation: `customer_pipeline/tool7_contact_judgment.py`, commit `84497e2c6e4e6778f8482bdbeec84ce45ee37346`.
- verification: `PASS: 8 deterministic P2 fixtures`.
- still HOLD: 실제 오늘 고객 레코드와의 end-to-end 판단/전화문구 출력.
- Work gate: `WORK_DEFER_DENIED`.

## P1 -> P2 deterministic handoff
- implementation: `customer_pipeline/p1_to_p2_handoff.py`, commit `1adbcfef1d2b0ad54f87157b9fb8b96b01cabaf2`.
- verification: `PASS: 6 deterministic P1->P2 handoff fixtures`.
- still HOLD: 실제 회사 customer DB 입력.
- Work gate: `WORK_DEFER_DENIED`.

## P3 TOOL001 — processed evidence through 2026-08-10 15:49 KST
### synthetic quarantine
- historical evidence: `안내서_전체_연결버전.html` mapper candidate vs v14 synthetic report generation.
- regression asset: `customer_pipeline/tool1_synthetic_data_guard.py`, commit `456fbf27d41a2ba109de9536c8cfe91101522406`.
- error_hash: `TOOL001_SYNTHETIC_REPORT_DATA`, `TOOL001_REAL_REPORT_FIELDS_MISSING`.
- verification: `PASS: 4 deterministic Tool1 quarantine fixtures`.

### historical stable-layout contract
- processed Library evidence: `1번 고객 자동화 안내서 12.doc`, `1번 고객 자동화 안내서 16.doc` and duplicate historical chain only as corroboration.
- recovered contract: stable/right guide baseline minimum modification only; left 9 fields; one Generate button; right slot ids; `THREE_AREA_VALUE_GAP`.
- regression asset: `customer_pipeline/tool1_historical_contract.py`, commit `c797c5dd1e52610b7c61ab59845544be476e4023`.
- verification: `PASS: 8 deterministic Tool1 historical-contract fixtures`.

### newly processed verified-data + feedback-loop evidence — 15:49 KST
- new Library evidence: `1번 고객 자동화 안내서 8.doc` and `1번 고객 자동화 안내서 23.txt`.
- classification: `CONSTRAINT + NEW_FIXTURE`, absorbed target `TOOL001`; fixed P0-P5 priority unchanged.
- recovered rules:
  1. customer input may come from uploaded DB, prior verified customer table, or explicit tool options, but guide output may use only verified report data.
  2. report title/link/publisher/date/pages/list price/supply price/TOC must be explicit and verified before production guide PASS; unavailable values remain HOLD, never fabricated.
  3. public source path preferred; login/captcha/private-only data remains HOLD.
  4. right-side stable guide structure is not rebuilt for this data-quality patch.
  5. user correction from a guide area becomes one structured feedback event; it must identify guide/report/area/observed/corrected values and route as `CORRECTION` to TOOL001 rather than merge whole chat context.
- actual tool-repo regression asset: `obk369369-spec/01-auto-guide-v1/regression/tool1_verified_data_contract.py`.
- commit: `78d92ac9a1aa06639bdce2f278bcbe973ab3f9af`.
- read-back blob: `1243533ab80cfcf3f8b04e9fc20d09a550afe04c`.
- CI workflow added in actual Tool1 repo: `.github/workflows/tool1-verified-data-regression.yml`, commit `5948cc7a6fff016b37bd429f87f85e98ed9119b3`.
- error_hash assets: `TOOL001_REAL_REPORT_VERIFICATION_GATE`, `TOOL001_CUSTOMER_CONTEXT_UNVERIFIED`, `TOOL001_UNKNOWN_FEEDBACK_AREA`, `TOOL001_FEEDBACK_EVENT_INCOMPLETE`.
- ordinary Python runtime verification: `PASS: 12 deterministic Tool1 verified-data/feedback fixtures`.
- external deployment status on workflow commit: existing `deploy/obk369369-spec/01-auto-guide-v1` status = FAILURE; therefore deployment/production E2E remains HOLD and is not confused with regression-storage PASS.
- benefit: exact historical user complaints about wrong title/link and repeated manual correction are now executable production guards in the actual Tool1 repository.
- downside/risk: fixture PASS does not prove DOM rendering or live deployment; the verified sample in fixture is deterministic test data, not a real tradable report/customer.
- rollback: remove/relax only this guard if a later user-approved production contract conflicts; do not restore synthetic generation.
- next_unprocessed_evidence: a real customer + real tradable report approved case, then stable mapper DOM/slot render comparison; do not reread 8/12/16/23 unless conflicting evidence appears.
- Work gate: G1=YES/G2=YES/G3=YES -> `WORK_DEFER_DENIED`.

## TOOL006
- known: MarketsandMarkets upper-level/indent/merged-split/numeric-only/List-of-*/TOC2/revalidation 문제. P3/P4 실고객 안내서가 요구할 때 golden fixture 우선 회수.

## TOOL013 / TOOL037 NUMBER LOCK
- 13번 = Excel automatic upload only.
- 37번 = metadata production/integrated verification only.
- 결합 금지.

## Cross-chat feedback ingestion — implemented 2026-08-10 15:40 KST
- deterministic processor: `feedback_pipeline/cross_chat_feedback_ingest.py`; runtime regression `PASS: 11 deterministic cross-chat feedback fixtures`.
- persistent cursor/dedupe state: `feedback_pipeline/state.json`.
- CI audit: `.github/workflows/cross-chat-feedback-audit.yml`.
- runtime collector: scheduled `WIC 대화창 피드백 수집`, hourly `:20` KST.
- collector was created after the 15:20 slot; at 15:48 KST `last_run_time=null` is not a missed-run failure. First eligible scheduled run is 16:20 KST.
- cross-chat E2E remains HOLD until a NEW feedback item from another conversation is retrieved/deduped/persisted automatically.

## Chat proliferation guard — implemented 2026-08-10 16:11 KST
- user feedback classification: `CONSTRAINT + STRUCTURE_CORRECTION`.
- cause: similar preparation/observer/development chats increase navigation burden and force the user to repeat feedback instead of reducing it.
- routing ledger: `WIC_CHAT_ROUTING_REGISTRY.md`, commit `80ae661bd9ac97ffed875e00945263dd2c672241`.
- default: `NO_NEW_CHAT`.
- allowed logical lanes only: `CONTROL / EMAIL_COLLECTION / TOOL007 / TOOL001 / TOOL006 / CRM_RESPONSE`.
- ambiguous work stays in CONTROL instead of creating another chat role.
- duplicate/similar historical chats are `EVIDENCE_SOURCE_ONLY`, not additional active destinations.
- development/observer/Work-gate/feedback-ingestion reports consolidate to CONTROL only; specialist output stays in its existing specialist lane.
- cross-chat collector and stop-watch automation updated to load this registry and forbid inventing/renaming/proposing extra preparation/observer/development chats.
- user is never asked to choose between similar chats or forward the same feedback.
- benefit: active navigation burden is capped; feedback continues to flow centrally without merging whole chat contexts.
- downside/risk: Chat UI may still contain old similar chats because assistant cannot delete/rename UI conversations; the guard controls routing and future behavior, not the existing sidebar contents.
- rollback: only if the user explicitly requests a new independent chat lane for a genuinely distinct workflow.
- Work gate: G1=YES/G2=YES -> `WORK_DEFER_DENIED`.

## exact restart point
1. P0 live customer blocker가 나타나면 즉시 최우선.
2. P3: real customer + real tradable report가 포함된 과거 사용자 승인 fixture를 신규 evidence로 계속 탐색하되 8/12/16/23 processed chain 재독해 금지.
3. 해당 실제 payload를 `tool1_verified_data_contract.py` gate에 통과시킨 뒤 stable mapper actual DOM/slot과 rendered output을 expected 값에 비교.
4. P4 TOC가 필요한 실보고서가 식별되면 해당 publisher golden fixture 적용 후 P3 복귀.
5. cross-chat collector는 첫 eligible run 이후 last_run/evidence 확인.
6. chat routing은 `NO_NEW_CHAT`; 새 유사창 대신 CONTROL 또는 기존 전문 lane 재사용.

## 사용자 역할
관찰자. 과거 오류 재설명, 동일 파일 재전송, 반복 테스트, PASS/FAIL 판정, 규칙 정리, Work 이관 판단, 대화창 피드백 수동 전달, 비슷한 대화창 선택을 요구하지 않는다.
