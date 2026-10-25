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
