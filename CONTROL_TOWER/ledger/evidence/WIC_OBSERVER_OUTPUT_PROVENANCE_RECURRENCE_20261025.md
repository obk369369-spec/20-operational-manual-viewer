# WIC observer-output failure recurrence — 2026-10-25
Status: OPEN / FAIL_CLOSED / NO_PASS. This is an incident evidence record, NOT a runtime repair or completed E2E.

## Grounded incidents from user-visible conversation
1. Assistant claimed 65-row WIC workbook was a useful comparison despite partial 59/65 Korean translations and 0 verified complete records.
2. Assistant compared a non-executed external product against its own incomplete workbook; no actual A/B parity.
3. Assistant treated its own previously produced pasted output as a user-authored golden reference. User explicitly corrected this provenance error.
4. Assistant sent non-canonical / insufficiently verified workbook and shifted review burden to the observer.
5. User's manually prepared and actually uploaded historical Excel has not been recovered or bound to a verified golden fixture.
6. User explicitly requests consolidation with remaining ~45% Work budget, without repeated manual intervention.

## Merge into existing common ROOT (not six isolated fixes)
Root fingerprint: USER_VISIBLE_OUTPUT_AUTONOMOUS_RECOVERY_AND_RECORD_IDENTITY + EVIDENCE_PROVENANCE_FALSE_PASS_GATE.
Existing canonical: handoff/WIC_NEXT_CHAT_HANDOFF_2026-10-11.md sections 3-8. Prior TOOL013 handoff: CONTROL_TOWER/ledger/evidence/WIC_TOOL013_NEXT_WORK_HANDOFF_20261008.json.
Do not overwrite old PASS or claim those artifacts are tested.

## Required enforcement changes (unimplemented here)
- Provenance: immutable input artifact ID/hash + human-authored vs model-generated label; model-generated output CANNOT be golden truth.
- Output schema: exact 18 official columns, order, formats, business mapping, plus independent validation of downloaded workbook.
- Translation: full-title coverage, no partial topic paraphrase counted as completed translation; unknown title -> HOLD.
- Taxonomy: official hierarchy / approved mapping only, no guessed 2nd/3rd category; quarantine unresolved records.
- External A/B: same source and same independent golden file; no comparison PASS when external A not executed.
- Observer gate: assistant independently inspects and reopens artifact, outputs machine-checkable per-record diffs and metrics, never asks user to enumerate errors.
- Recurrence gate: fail if assistant-created sample is mislabeled as original, if partial translation counted as complete, or if text-only claims are called execution proof.
- Zero rework: reuse existing approved evidence and unchanged PASS; target only affected ROOT, no 3200-wide rescan, no rebuild, no 773-row manual repair.

## Required test/evidence
Real manually prepared historical WIC upload XLSX -> read-only golden provenance -> identical inputs for A and B -> exact 18-column final XLSX -> reopen -> compare every record and field (translation, 1/2/3 categories, pages, dates, overview, TOC, price, identifiers), identity counts, negative and false-PASS tests, quarantine and recovery -> independent audit evidence -> remote read-back. If source inaccessible, set BLOCKED_GOLDEN_SOURCE, not PASS.

## Current execution state
Incident identified, consolidated and committed only. NO code/runtime patch, NO actual E2E, NO valid external A product, NO golden-file match, NO validated final upload. Work budget percent is user-reported, not tool-verified. User is observer only.

## 2026-10-25 additional recurrence: rule retrieval and output-calculation contract
User reports TOOL013 cannot retrieve and apply the latest accumulated rules; produces outputs so far from expected that an observer cannot identify a small bounded diff. This is not an isolated mistranslation; it is a common root of RULE_SOURCE_RESOLUTION -> VERSION_PRECEDENCE -> FIELD_TRANSFORMATION -> INDEPENDENT_EXPECTED_ACTUAL_VALIDATION -> FAIL_CLOSED_OUTPUT.
No user re-explanation of historical rules, translation choices, or row-by-row correction is permitted.
The required acceptance gate is NOT an arbitrary promise of at most one error. Instead independently verify every field against approved user-authored golden workbook and machine-readable approved rules; zero silent differences; unresolved fields quarantined with machine-generated cause and source citation.
For each rule, record source path, version/priority, hash, affected output fields, fixture ID, expected value, actual value, mismatch root, corrective action and test result. A model-produced workbook cannot be a golden fixture. If rule conflicts exist, use established canonical priority; otherwise BLOCK_RULE_CONFLICT, not arbitrary selection.
For Korean title translation, preserve full original meaning, parenthetical segments, regions, forecast periods and qualifiers; compare with approved translations, reject truncation/topic-only translation and report precise diff automatically.
Repair the shared rule resolver and output gate before any TOOL013-specific per-cell patch. Batch related open roots; reuse existing evidence and PASS, targeted RED->GREEN->regression->actual E2E->download/reopen->GitHub remote read-back. Never claim runtime fixed solely from this ledger update.

## 2026-10-25 15:10 Work execution evidence: blocked self-repair
User-provided Work report: CENTRAL RESUME_LOADED; HEAD f88a382bab25acf78a302988173c97f08309f686; runtime_progress_gate.py missing TOOL013 rule source mapping; Registry checkpoint 820ea587... vs TOOL013 remote HEAD 9212abf64...; stale MASTER/RULE_SOURCE hash; user-authored golden Excel bytes unavailable. Gate SKIP_NO_VALUE due to unregistered change condition for WIC-PARALLEL-RESIDUAL-20260903. Code modifications 0; actual processing 0; validation of broken connections only; GitHub write 0; no manual user checks.
Treat as evidence reported by Work, not independently reproduced runtime test.
Consolidated ROOT: COMMON_RULE_PROVENANCE_AND_SELF_REPAIR_GATE_DEADLOCK. It includes false-PASS prevention and missing legitimate recovery authorization: detect -> fingerprint -> existing change-condition evidence verification -> register justified change-condition via authorized mechanism -> rerun scoped gate -> fix shared resolver -> self-test and self-repair -> XLSX reopen -> observer-only report. No bypass of gate; if authorized registration impossible, preserve explicit BLOCKED_AUTHORIZATION with exact missing proof. Golden unavailable is separate BLOCKED_GOLDEN_SOURCE, but MUST NOT prevent independently testable resolver/validator and negative fixtures from being repaired when gate permits. Never claim actual XLSX E2E without original.
Required evidence must include actual generated workbook plus independent machine-readable diff, failure trace, before/after tests, version hashes, and remote read-back. 'Self-learning' means versioned, approved correction rules and regression fixtures, NOT unreviewed model weight updates or self-modifying guesses.
User observer; no request to manually enumerate translation mistakes or re-teach rules. No user-side Excel review. Existing approved golden/source discovery must be bounded to known paths; avoid broad scans.

## 2026-10-25 scoped runtime repair result
- Admission: ATTEMPT_ALLOWED after canonical trigger_release/scope_grant registration; no STOP/PASS_LOCK bypass.
- Rule retrieval: TOOL013 now resolves pinned remote MASTER and WIC_RULE_SOURCE at 9212abf64f67e56d934c84efb0b91a97253a7203 through existing registry receipts.
- Provenance gate: model-generated or unbound golden evidence blocks with TOOL013_HUMAN_GOLDEN_PROVENANCE_UNVERIFIED; HUMAN_USER provenance with matching immutable source reference passes the bounded gate fixture.
- Completion gate: TOOL013 requires exact_18_columns, full_title_translation, approved_taxonomy, price_and_date, original_preserved, no_missing_duplicate_mixed_rows, and download_reopened from the independent validator.
- Tests: py_compile PASS; tests/test_permanent_reentry_gate.py PASS; work_execution_enforcer.py --self-test PASS; TOOL013 manifest missing=[] and both remote rule identities present.
- Remote code commits: d7dd2bb5545dfe3b7e8ea5ef97abd49d25e51e21, 4e3b90ce34a13da953207e588d4c76d3c4e73e33, 8dcd8a5aa458703db8766350b00ce24cf760b7bb, e3efa220ebff88709c03db81c5f0f36c4b473a05; remote blob read-back matched each uploaded blob.
- Status: COMMON RESOLVER/PROVENANCE/OUTPUT GATE REPAIR PASS. Actual workbook E2E remains BLOCKED_GOLDEN_SOURCE because no accessible user-authored golden workbook bytes exist; no synthetic workbook promoted to PASS.

## 2026-10-25 follow-up: verified 3 commits and remaining common breaks
- Verified via GitHub commit fetch: 093dd140 modified CONTROL_TOWER/controller/github_runtime_cycle.py; 76fbb742 modified tests/test_wic16_queue_isolation.py; 500310e6 modified feedback_pipeline/deployment_observer_gate.py.
- Reported by Work, not independently reproduced here: Python compile PASS; 12 queue isolation tests PASS; observer fail-closed self-test PASS; three remote blob read-backs PASS.
- Remaining open: R1/R3 rule body not delivered to transformer; TOOL013 title field direction inconsistent; R4 row quarantine/self-repair not wired; R5 non-Excel independent reopen/receipts missing; R6 remote receipt may be satisfiable from local hash alone.
- Next execution must repair common runtime edges in parallel on isolated files, with genuine remote blob retrieval and independent artifact reopen receipts; no code-only PASS as business/output PASS. Golden user-authored workbook remains BLOCKED_GOLDEN_SOURCE, no synthetic substitute.

## 2026-10-25 scoped follow-through check (assistant direct GitHub read)
- Directly fetched latest CENTRAL `feedback_pipeline/deployment_observer_gate.py` (blob f09478af0732196b237c559f190f91a202bbd7d0) and `CONTROL_TOWER/controller/github_runtime_cycle.py` (blob 6740d4bac3ed19db12bf0a695932659536717045). Both are present; this is source inspection, NOT executable runtime testing.
- Repo-scoped code searches: `rule_source_payload` no results; `remote_blob_receipt` no results; `download_reopened` matched existing pre_work_admission and evidence. Search absence is not proof of absence of equivalent code.
- Next scoped implementation admission: R1/R3 attach actual canonical rule BODY to TOOL013 transformation and resolve `상품명` Korean / `한글명` original English direction; R4 wire existing safe auto-fix/quarantine; R5 add independent format-specific artifact reopen receipt; R6 require fetched remote blob content+identity (not local hash-only). Parallelize independent modules only after gate admission; actual user golden E2E remains HOLD.
- No runtime code changed, no tests run, no final artifact produced in this assistant check. Do not mark these items PASS.


## 2026-10-25 common R1/R3/R4/R5/R6 runtime-edge repair
- Scope/admission: current user directive registered as a narrow reuse-only scope grant; STOP and PASS_LOCK unchanged.
- R1/R3 before: cross-repository rule receipts carried identity/hash only. After: source/path/version/priority/hash/affected_fields/content are mandatory, content digest is verified, records are deterministically ordered and the exact rule bodies are returned in the runtime context. TOOL013 MASTER and WIC_RULE_SOURCE bodies were pinned from revision 9212abf64f67e56d934c84efb0b91a97253a7203.
- R4 before: callback failures could abort unrelated records and repair evidence did not prove one-pass revalidation. After: validate -> one safe repair attempt -> revalidate -> quarantine; validator/repairer errors isolate one record, while identity/protected-field mutation holds the whole affected output.
- R5/R6 before: completion did not require a common independent reopen receipt and remote readback could be represented by local hash equality. After: parser/validator identity, separate reopen execution, format checks, artifact/source hashes, remote commit/blob/retrieval/path/retrieved-hash receipt are mandatory.
- Changed commits: registry 2b873492542b4c921c05959b9557e99b24c12b75; rule runtime d67c679b86c6a0552ce38274cb3dc7c7f51b801d; R4 6a3de84beaad7eca66e8e4c79218abab11d57572 and 44a5c9c0b56c712b07de51226d78a630d1fc3f39; R5/R6 7810dc4d078c30783cb64ffe6450bac66bc2511c and 57006da1c001cb91c50400e882bde86c927cb4a2; rule tests 8e3fcb0df2333c0aa2ef20ab7882424cb3a91b9f.
- Bounded validation: py_compile PASS; permanent reentry/rule negative-positive gate PASS; record isolation 8 tests PASS; common output reopen/remote gate positive PDF and TOOL013 XLSX contract PASS with 6 negative mutations blocked; git diff check PASS.
- Remote readback: all seven changed code/registry/test paths were re-fetched through the GitHub connector and matched expected blob identities/content markers.
- Completion classification: CODE PASS and TEST PASS only. ACTUAL BUSINESS PASS and FINAL OUTPUT PASS remain HOLD_GOLDEN_SOURCE; no model-generated workbook was promoted.
- Remaining exact edge: an approved real transformer/format adapter must consume rule_records and produce an actual artifact plus independent reopen/diff receipt. Golden user-authored workbook bytes remain unavailable.


## 2026-10-25 final handler/output-boundary continuation
- ROOT A: verified rule_context/rule_records are copied from admission into queue.admitted_rule_contexts and passed to requirement/backlog handler contracts. Missing/nonempty rule_records now fails before evidence or handler validation with VERIFIED_RULE_RECORDS_NOT_BOUND_TO_HANDLER.
- ROOT B: the existing common handler execute_registered now sends its actual return code/output existence/content checks through enforce_record_isolation. A failed record is quarantined without rerunning the handler; unrelated jobs continue. No unapproved repair callback was invented.
- ROOT D: terminal PASS requires a 64-hex expected output SHA-256 matching the generated artifact. Missing digest and mismatched digest both fail; matching digest succeeds. The malformed literal line breaks introduced in remote test commit 54d67118 were repaired in 7637d34e1553fc420853d7d5a2e055d706cb7765.
- Changed-boundary evidence: exact remote runner blob 8bef1f7011c89d48b9ac0e8165f9d18a64c860b4 and repaired remote test blob 016ed2a034dbe3727b250b04c0ceef4345268248 executed together: 19/19 PASS. Queue isolation impact suite: 13/13 PASS locally before upload.
- Commits: aa9104d4809d9275b15936cd896dd8870ca3c5b5, 9dd08fb7545cc36a686d20faa69ff1830e3038f7, 999ed61410f03e7504094f0904d0be9e4ed4413b, b3222edfb5ccc80e627c98c3a5053443a82b24ab, 0bc7e754d0d2ce25994e6ad6f71858f85c97913a, 54d671182b67eac0f0e4e15369f056ce033d7821, 7637d34e1553fc420853d7d5a2e055d706cb7765.
- Actual business/output classification: HOLD_ACTUAL_INPUT_UNAVAILABLE_AND_NO_REGISTERED_TRANSFORMER_ADAPTER. The known C: TOOL013 input path is absent and D: is outside the current sandbox; existing generated XLSX is prior output, not new input.
- ROOT C/E exact hold: HOLD_REMOTE_ARTIFACT_NOT_CANONICALIZED. The only current producer creates an untracked temporary isolated-execution.txt and reuses that local ref as remote_readback_ref. It cannot truthfully supply a remote commit/blob/retrieved SHA until an approved producer stores and pushes the actual output and a separate readback retrieves that exact commit/path.
- No actual business PASS, auto-repair PASS, or final-output PASS was promoted from fixtures.
