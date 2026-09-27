# WIC FINAL BULK WORK HANDOFF — 2026-09-27

Status: CHAT_COMPRESSION_COMPLETE / WORK_EXECUTION_PACKET
Goal: stable production tools usable immediately, while later generalized capabilities are developed and verified in separate versions.

## 0. Absolute rules
- Observer is not tester, formatter, relay, duplicate cleaner, or approval operator.
- Collect actionable errors first, deduplicate, group by ROOT cause, then repair each ROOT once in the largest safe batch.
- Never repair one occurrence/file at a time when the same ROOT can be fixed once.
- Reuse existing PASS. No unchanged PASS reruns.
- Default 1 MICRO, maximum 3. No MICRO 4.
- No fake PASS: actual execution + target deployment + deployed-copy verification + persistent evidence/read-back are required.
- Stable production must never be overwritten by unfinished next-version work.

## 1. Version split for every WIC tool
### PRODUCTION-STABLE
Functions already promised for current completion and actually verified.
Freeze scope, give an unmistakable STABLE file/folder name, deploy to actual-use folder, run final smoke/reopen/read-back, and make usable immediately.

### NEXT-DEVELOPMENT
New/generalized capabilities beyond the current stable contract.
Use a separate version/folder/branch/artifact. Never destabilize STABLE. Promote only after its own actual E2E + deployed-copy PASS.

## 2. TOOL006
### STABLE
Reuse 9/9 functional/chronic fixtures + 4/4 smoke.
Use supplied deduplicated manual-guide corpus and actual EML TOCs to close current promised publisher/layout coverage.
Verify depth selection, hierarchy/indent, parenthetical noise, asterisk footnotes, List of Tables/Figures/appendix noise, copy-enabled output and zero deeper-depth leakage.
Deploy frozen verified copy to real-use TOOL006 folder and verify deployed copy.

### NEXT
1. Unknown/unseen publisher TOC layout generalization using holdout fixtures.
2. URL mode: URL -> acquire page -> isolate TOC -> normalize -> depth render -> copyable output.
3. Login/JS/anti-bot/ambiguous page fails closed; never invent TOC.
Endpoint: observer pastes TOC or URL and waits.

## 3. TOOL013
### STABLE
Reuse 114-file/823-row PASS, XLS/XLSX conversion, cache/resume, regime display and deployed evidence.
Close only previously promised current-version gaps provable from existing rules/sources.
Deploy frozen stable real-use copy and verify reopen/read-back.

### NEXT
Incoming publisher spreadsheet -> detect workbook/schema/publisher -> preserve English title -> publisher-specific Korean title -> canonical 18 secondary-category mapping -> required-field/duplicate validation -> tracking + upload outputs -> reopen/readback.
Unknown publisher/schema -> bounded inference/quarantine; never silent guessing.
Automatic title translation and canonical secondary-category matching remain required until runtime PASS.
Endpoint: observer drops spreadsheet, waits for two validated outputs, and only performs business upload.

## 4. TOOL001 / 041 / 007 / 042 / 048
Use supplied 2026 actual EML archive, recovered chat records and unique guide templates.
Blanket source-acquisition HOLDs are stale; exhaust supplied corpus first.
- TOOL001: recover >=5 provenance-backed actual report payloads and run actual report -> final guide E2E. Intentional blank supply price = NOT_ERROR.
- TOOL041 -> TOOL007 -> TOOL042: cross-link named real customer history, verified current facts, actual sent output and branch result. Batch multiple real cases; no customer hardcoding.
- TOOL048: filter guide/customer mails from mixed mailbox, cross-link to 42/chat evidence, deduplicate repeated errors, ROOT-group and validate pre-send gates.
- HTML/DOC historical templates are evidence/reference, not automatically production truth.
- Deploy stable current versions separately from new automation/generalization.

## 5. TOOL044 / TOOL016 expanded circulation
Do not rebuild verified component pipeline, trust chain, watchdog, hourly report or minimum failover PASS.
Use actual remaining work to prove:
TOOL016 demand -> ROOT batch -> TOOL044 verified-component-first reuse/acquisition -> free runtime -> checkpoint/heartbeat -> failure isolation/failover -> bounded target adapter -> regression -> correct STABLE/NEXT deployment -> deployed-copy readback -> result return -> observer projection.
Primary expansion targets: TOOL006 + TOOL013 + one batched customer-chain validation.

## 6. Infrastructure still requiring actual proof
- multi-demand continuous processing without omission/duplication;
- cross-cycle state preservation and completed-demand reselection prevention;
- heterogeneous multi-tool expanded E2E;
- free external runtime while local PC/screen is off;
- logged-off worker only PASS if actually solved;
- true 24-hour unattended operation requires elapsed 24h evidence;
- arbitrary future-tool Git push/deploy/rollback is not currently proven;
- ordinary ChatGPT all-message native interception remains platform-limited unless supported capability appears;
- generalized continuous external discovery for unknown future capabilities is not global PASS until actual proof.

## 7. Source corpus now available
- canonical manual-guide superset: 2020-공학도서-양서 archive.
- smaller 지난 안내서 모음 is exact-content subset; do not process separately.
- guide template archive contains unique DOC/HTML templates; preserve only unique payloads.
- 2026 sent-mail archive contains 1,226 EML, with hundreds of guide/material candidates; it is mixed mail and must be classified, not assumed customer-only.
- cross-link mail subject/customer/date/report/TOC against 41/7/42/48 chat history.

## 8. Error collection before repair
Build one current ledger from:
1. current GitHub OPEN/HOLD/FAIL/RETRY_BLOCKED;
2. supplied actual guide/mail corpus;
3. recovered chat feedback;
4. deployed-copy/current runtime evidence.
For every item record:
ROOT_ID / affected tools / actual occurrence count / current implementation / existing PASS to reuse / missing contract / repair batch / validation / deployment target.
Then deduplicate superseded/stale HOLDs.
Only after collection is complete start repair.

## 9. Bulk repair order
ROOT-A: production-stable release blockers across current tools.
ROOT-B: TOOL006 current-layout correctness and stable deployment.
ROOT-C: TOOL013 current promised gaps and stable deployment.
ROOT-D: customer chain + TOOL001/048 actual-output defects.
ROOT-E: generalized NEXT TOOL006/013 automation.
ROOT-F: TOOL044/016 expanded multi-tool circulation.
ROOT-G: unattended/failover/24h infrastructure evidence.
Independent ROOTs may execute in parallel; dependent ROOTs wait on their real prerequisite, not user confirmation.

## 10. Completion report
Return one final matrix:
TOOL / VERSION / ROOT / BEFORE / FIX / ACTUAL TEST / DEPLOYED PATH / READBACK / STATUS.
Statuses only: ACTUAL_PASS / IN_PROGRESS / HOLD / FAIL / PLATFORM_LIMIT / TRUE_EXTERNAL_INPUT_REQUIRED / SKIP_REUSE.
List any remaining item only with its exact blocker and the next automatic trigger.
No user manual testing unless TRUE_EXTERNAL_INPUT_REQUIRED.

## 11. Final observer criterion
A tool is operationally complete only when the observer's remaining action is the natural business action:
- TOOL006: paste TOC/URL and receive verified output.
- TOOL013: provide received spreadsheet and receive validated upload/tracking files.
- customer tools: choose/receive a real customer case and receive validated guidance/action output.
- common infrastructure: observer reads status/results; no relay or repeated approvals.
Any repeated formatting, duplicate cleanup, source re-upload, cross-chat copying, manual regression checking, or publisher-specific re-teaching remains an automation defect.
