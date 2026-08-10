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

## P3 TOOL001 — processed evidence through 2026-08-10 15:10 KST
### synthetic quarantine
- historical evidence: `안내서_전체_연결버전.html` mapper candidate vs v14 synthetic report generation.
- regression asset: `customer_pipeline/tool1_synthetic_data_guard.py`, commit `456fbf27d41a2ba109de9536c8cfe91101522406`.
- error_hash: `TOOL001_SYNTHETIC_REPORT_DATA`, `TOOL001_REAL_REPORT_FIELDS_MISSING`.
- verification: `PASS: 4 deterministic Tool1 quarantine fixtures`.

### newly recovered historical contract — 15:10 recovery
- new Library evidence processed: `1번 고객 자동화 안내서 12.doc`, `1번 고객 자동화 안내서 16.doc` and duplicate historical chain only as corroboration.
- recovered user-approved contract:
  - stable/right guide baseline must not be rebuilt; minimum modification only.
  - left side fixed to 9 fields: English title, Korean title, publisher, publication date, pages, list price, supply price, report link, TOC.
  - one Generate button only.
  - right-side slot contract includes `TITLE.EN`, `META.PUBLISHER`, `META.DATE`, `META.PAGES`, `META.PRICE`, `LINK.TEXT`, `TOC.TEXT`.
  - diagnostics history establishes `THREE_AREA_VALUE_GAP` when middle/right values diverge and mutation target can identify disappearance point (historically guideDate/guideLink issues).
- regression asset created: `customer_pipeline/tool1_historical_contract.py`.
- commit: `c797c5dd1e52610b7c61ab59845544be476e4023`.
- GitHub read-back blob: `0a745bcd3d757962b47b1ce31b0f0c2141392d8f`.
- error_hash assets: `TOOL001_LEFT_9_FIELDS_ONE_BUTTON_CONTRACT`, `TOOL001_RIGHT_SLOT_MAPPING_MISMATCH`, `TOOL001_STABLE_BASELINE_SCOPE_VIOLATION`, `THREE_AREA_VALUE_GAP`.
- ordinary Python runtime verification: `PASS: 8 deterministic Tool1 historical-contract fixtures`.
- benefit: prior user corrections are now executable regression contracts instead of prose-only history; new shell/rebuild drift can be blocked before production PASS.
- downside/risk: this contract does not itself render the HTML or prove a real customer/report guide E2E.
- rollback: remove only this regression asset if a later user-approved stable baseline proves a conflicting contract; never relax the baseline based on synthetic/demo output.
- Tool1 production status: HOLD — real verified report payload -> stable mapper -> actual guide output -> expected comparison still required.
- next_unprocessed_evidence: real customer + real tradable report approved fixture; then DOM/slot output comparison. Do not reread the processed 12/16 chain unless a conflicting baseline is found.
- Work gate: G1=YES/G2=YES/G3=YES -> `WORK_DEFER_DENIED`.

## TOOL006
- known: MarketsandMarkets upper-level/indent/merged-split/numeric-only/List-of-*/TOC2/revalidation 문제. P3/P4 실고객 안내서가 요구할 때 golden fixture 우선 회수.

## TOOL013 / TOOL037 NUMBER LOCK
- 13번 = Excel automatic upload only.
- 37번 = metadata production/integrated verification only.
- 결합 금지.

## Cross-chat feedback ingestion — implemented 2026-08-10 15:37 KST
### User requirement absorbed
- 모든 관련 대화창의 WIC 피드백을 사용자가 다시 전달하지 않게 한다.
- 접근 가능한 prior-interaction/personal-context에서 새 피드백을 회수하고 중앙 마스터/관련 도구/GitHub로 흡수한다.
- 대화창 전체를 서로 합치지 않고 `feedback event`만 중앙으로 승격한다.

### Actual implementation
- deterministic processor: `feedback_pipeline/cross_chat_feedback_ingest.py`
  - commit: `4d917ae0765612273416b536115e13b46078b97f`
  - functions: classification / tool routing / semantic dedupe id / PII redaction / central-master candidate / regression-fixture candidate / Work gate.
- persistent cursor/dedupe state: `feedback_pipeline/state.json`
  - commit: `8acc109f2cd53562517e1acfa686db3b9b79e663`
  - seeds the 2026-08-07 cross-chat auto-collection instruction and the 2026-08-10 explicit implementation instruction as processed constraints.
- CI audit: `.github/workflows/cross-chat-feedback-audit.yml`
  - commit: `0dfc46375b5999189766d5c7a7e52eb2364de63d`
  - verifies deterministic fixtures, state schema, duplicate IDs, and PII persistence ban on relevant pushes/PRs.
- runtime collector: active scheduled task `WIC 대화창 피드백 수집`, hourly at `:20` KST.
  - source method: accessible prior-interaction/personal-context retrieval; no Chat UI scraping claim.
  - delta only: load state cursor -> recover new WIC feedback -> normalize/dedupe -> master/fixture/implementation routing -> GitHub read-back -> advance state.
  - no-new-feedback behavior: `SKIP — no new cross-chat feedback`, no fake activity commit.

### Safety / direction control
- ordinary CORRECTION/CONSTRAINT/NEW_FIXTURE is absorbed into the existing target and resumes the saved priority; it does not merge whole chat contexts or redirect the program.
- only explicit `PRIORITY_CHANGE` may reorder the fixed office-customer priority stack.
- raw customer PII/private contract text/confidential transaction content is not persisted in the central feedback log; only sanitized rule-level excerpts, hashes, references, and state.
- central normative updates target only `WIC_GLOBAL_OPERATING_RULES.md`; this ledger remains non-normative.

### Work/credit gate
- collection, history retrieval, classification, rule merge, fixture creation, GitHub patching, and ordinary-runtime deterministic tests are `WORK_DEFER_DENIED` whenever Chat/Files/GitHub/runtime can perform them.
- historical re-analysis or terminal-suitable work sent to Work is `CREDIT_WASTE_FAIL`.
- Work receives only exact Work-only blockers with source files + known-good baseline + failing fixture + expected output + error signature + PASS criteria + attempted Chat/runtime work + no-reanalysis scope.

### Verification state
- GitHub storage/read-back: PASS for processor/state/workflow creation commits listed above.
- deterministic processor functional verification: pending CI/ordinary runtime evidence after workflow run; code presence alone is not functional PASS.
- cross-chat collector end-to-end proof requires at least one NEW feedback item from another conversation to be retrieved, deduped, and persisted without manual forwarding. Until that external event occurs, runtime E2E = HOLD, implementation = ACTIVE.
- user forwarding requirement: removed from operating path; user remains observer-only.

## exact restart point
1. Cross-chat collector: next hourly `:20` run must search only after `feedback_pipeline/state.json:last_context_cursor`; if a new feedback item exists, persist one end-to-end proof and advance cursor.
2. P3: real customer + real tradable report가 포함된 과거 사용자 승인 fixture를 신규 evidence로 회수.
3. stable mapper의 실제 DOM/slot id를 그 payload와 비교하여 synthetic 0건 조건으로 guide fixture 생성.
4. actual input -> rendered output -> expected comparison 전 Tool1 생산 PASS 금지.
5. P4 TOC가 필요한 실보고서가 식별되면 해당 publisher golden fixture 적용 후 P3 복귀.

## 사용자 역할
관찰자. 과거 오류 재설명, 동일 파일 재전송, 반복 테스트, PASS/FAIL 판정, 규칙 정리, Work 이관 판단, 대화창 피드백 수동 전달을 요구하지 않는다.
