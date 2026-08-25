# WIC FEEDBACK → REGRESSION / CHAT → WORK GATE LEDGER

상태: ACTIVE / NON-NORMATIVE EVIDENCE LEDGER
규범 원본: `WIC_GLOBAL_OPERATING_RULES.md`
영구 파이프라인: `HISTORY_EVIDENCE -> CLASSIFY -> RULE/EXPECTED_OUTPUT -> FIXTURE/ERROR_HASH -> ACTUAL_PATCH -> VERIFY -> READ_BACK -> REUSE -> RESTART_POINT`

## SAFE CHECKPOINT — Work 16 / 2026-08-24
- start_remote_read_back: `8928ee37994e4d4271183b84f863ecd5707efaa9`; `87bdd2f` 이전과 이후 이미 반영된 원격 작업은 SKIP-REUSE.
- common_feedback_gate: commit `6c35774b672a64fd638168f39ee0ad8e273cd7a9`; 미등록 route를 CENTRAL-only PASS에서 분리하고 `REPOSITORY_CREATE_HOLD`로 격리. 등록 TOOL006 + 미등록 route 대표 fixture PASS. push 및 원격 SHA/blob read-back PASS.
- TOOL041: remote `21acd06`; 기존 267명 데이터는 저장소 자체 판정 `HOLD_REVALIDATION_REQUIRED`. 전수 재검증·ACTIVE 승격 없음.
- TOOL042: remote `3b5a7ea52865cd409b02fe793f17984773ecb1d9`; 기존 김명곤 actual/expected gate `PASS`, errors 0, holds 0. TOOL007 판단 fixture 8개 PASS. SKIP-REUSE.
- TOOL006: branch `agent/tool006-active-baseline`, commit `578c0bdea402081e1f7893ed376c1a387a7ded96`; smoke runtime 경로 수정, smoke 4/4 및 functional E2E 5/5 PASS, push 및 원격 SHA/blob read-back PASS. main merge와 실제 발행사 golden pair는 기존 HOLD 유지.
- TOOL013: 이번 묶음 미시작. 기존 중앙 target apply 증거만 SKIP-REUSE하며 다수 Excel 실제 연속처리는 미검증 HOLD.
- repository_create: 임의 저장소 생성 없음. 소유 업무군·기존 저장소·생성 권한/경로가 확인되지 않은 신규 route만 `REPOSITORY_CREATE_HOLD`; 기존 등록 route는 계속 실행.
- changed_files: `feedback_pipeline/cross_chat_feedback_ingest.py`, `feedback_pipeline/target_dispatcher.py`, TOOL006 `tests/tool006_smoke.ps1`, 이 ledger.
- unrelated_changes: 0; 운영 저장소 작업트리 clean.
- known_error_groups_remaining: 3 (`TOOL041_REVALIDATION`, `TOOL006_GOLDEN_AND_MAIN_MERGE`, `TOOL013_MULTI_EXCEL_UNVERIFIED`). 이번에 실행한 대표 fixture의 재현 오류는 0.
- NEXT_START: TOOL013 실제 저장소 최신 checkpoint/read-back 확인 후 다수 Excel 연속처리·중단/재개 대표 fixture 1개만 검증. TOOL041은 고객별 원문 근거가 확보된 증분 범위가 아니면 전수작업을 시작하지 않는다.

## SAFE CHECKPOINT — Work 16 continuation / 2026-08-24
- start_checkpoint: `aef1ae46201a01b94291ddd6de250416f7c4f2aa`; 이전 PASS 전부 SKIP-REUSE.
- TOOL013: 기존 `obk369369-spec/13-excel-upload` 재사용. commit `e3b695b8acd9f3d1de327cf285db80ed5cbfc185`; 실제 CSV 2개 순차입력 → 누적 2행 미리보기 → 동일행 중복차단 → 페이지 재시작 체크포인트 복원 E2E PASS. push 및 원격 SHA/4개 blob read-back PASS.
- TOOL006: PR #6을 기존 검증 결과와 새 smoke/E2E 결과로 ready 전환 후 일반 merge. 원격 main merge commit `4af3d0722c369f4e09fffdb43346bb8810b866c8`; 검증 branch `578c0bdea402081e1f7893ed376c1a387a7ded96`가 merge parent이고 smoke blob 일치. 실제 발행사 golden pair 부재는 별도 HOLD 유지.
- TOOL041: remote `21acd06`; 고객별 원문 동일인 교차검증 자산이 저장소에 없어 기존 267명 `HOLD_REVALIDATION_REQUIRED` 유지. ACTIVE 승격·전수 재검증 없음.
- changed_files: TOOL013 `index.html`, `scripts/tool13_batch_state.js`, `tests/tool13_batch_resume.test.js`, `tests/tool13_multi_file_e2e.js`, 이 ledger. TOOL006는 검증 완료 PR의 main merge만 수행.
- unrelated_changes: 0; 관련 저장소 작업트리 clean.
- known_error_groups_remaining: 2 (`TOOL041_SOURCE_CROSSCHECK_UNAVAILABLE`, `TOOL006_REAL_PUBLISHER_GOLDEN_PAIR_UNAVAILABLE`). TOOL013 이번 대표 묶음 재현 오류 0.
- NEXT_START: TOOL013 고정 오류목록의 다음 공통 원인 묶음(상태/패킷/재검증 불일치)을 대표 fixture로 처리. TOOL041 원문 근거 또는 TOOL006 실제 original→user-approved final pair가 새로 확인될 때만 해당 HOLD 재개.

## LOCAL LEDGER ACCUMULATION — TOOL013 fixed-error closeout / 2026-08-24
- central_push_policy_at_capture: `HOLD_REMOTE_CONTINUOUS_UPDATE`; 당시 중앙 push 재시도 없이 `work/work16-tool13-checkpoint`에 누적 보존.
- SAFE_CHECKPOINT_SHA: `1d51ba4816cdda704ce9580309b670d075762d17`.
- actual_scope: 고정 오류 `03,08,09,10,11,14,15,17,23,24`의 실행 증거 연결, 함수 오류 영향범위 기록, 화면 packet과 저장 JSON 일치, 오류목록/재검증 전후 상태, 장문 개요·목차 XLSX read-back, 실제 XLSX 2개 연속처리·중복차단·재시작 복원.
- verification: TOOL013 전체 5개 대표 fixture PASS; 실제 `.xlsx` 연속 입력 포함; browser page error `0`; runtime fixed-error FAIL card `0`; `git diff --check` PASS.
- remote_read_back: 원격 `main` SHA 일치. 변경 4파일 blob 일치: `index.html=c2b43a6925315cc1befb02315e55560b16c872f2`, `tool13_download_consistency_e2e.js=76fdc6ed13a798d125c5187a8a399ead7a08da75`, `tool13_multi_file_e2e.js=9a9ff96056760a8b66a4f92c7373306e547c9f05`, `tool13_rollback_history_e2e.js=a53beb9e56f369f91b4bb1bcee8808d0e058cf8c`.
- TOOL013 known-error representative gate: `PASS`; verified fixed IDs `01~32`, 알려진 오류 잔여수 `0` (대표 fixture 기준).
- SKIP_REUSE: TOOL013 `e3b695b`, `2b21e6a`, `9fd3a83`, `ffa61ad`, `444ec41`, `e3a5996`, `1d51ba4` 이전 묶음 전체.
- NEXT_START: 신규 실제 오류가 없으면 TOOL013 재작업 금지. 41번은 신규 HOLD 근거 없으면 재검증 금지, TOOL006 golden pair는 실제 자료 없으면 HOLD 유지. 다음 실행 가능한 미완료 업무만 시작.
- reconciled_on_2026_08_25: 원격 main `7aff149340bf1bb45b7f96cb552063534e15b72f` 안전 병합·push·read-back으로 `HOLD_REMOTE_CONTINUOUS_UPDATE` 해소; 원본 local branch `60641f8a139ef90cc76531a7d17eec5c98e77ab2` 보존.

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
