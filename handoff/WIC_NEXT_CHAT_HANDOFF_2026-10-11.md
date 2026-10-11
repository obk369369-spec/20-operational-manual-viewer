# WIC NEXT CHAT HANDOFF — 2026-10-11

## 0. Purpose
This is the canonical handoff from the current ChatGPT conversation to the next conversation.
Do not ask the user to reconstruct prior instructions. Read this handoff, the referenced checkpoints/evidence, and continue from the exact next root.

USER = OBSERVER.
USER_MANUAL_REPETITION = 0.
Do not make the user manually test, repair Excel rows, search files, or re-provide known material.

## 1. Canonical repository / preserved state
Repository: obk369369-spec/20-operational-manual-viewer

Prior preservation checkpoint:
WIC-CP-20261010-18PCT-FINAL-PRESERVATION-HANDOFF

Prior preservation commit:
f0d5533bf72b0fa491bf28107cece7ef0e17556a

Global row-isolation/autorecovery rule:
CONTROL_TOWER/ledger/evidence/WIC_GLOBAL_ROW_ISOLATION_AUTORECOVERY_RULE_20261010.md

Prior global rule commit:
a15fe2c24529e4b2a12013012013e77ee74127d9

Preserved Tool013 versions:
- PREVIOUS VERIFIED/PRESERVED:
  CONTROL_TOWER/work/tool013_user_output_closure/13번_V2_최종운영판.before.html
  blob a787c475313efd709c67a65a04c5b4383ba0ba12
- CURRENT ISOLATED/UNVERIFIED:
  CONTROL_TOWER/work/tool013_user_output_closure/13번_V2_최종운영판.html
  blob e6253eda95e6676540138c88afcfbeae22dcc89a

Do not overwrite or delete the preserved before version.

## 2. Common platform already closed — do not rerun
Common governance/root was already PASS_LOCKED.
Known prior runtime: 37769002540.
Do not restart/rebuild/retest unrelated closed common roots.

Locked roots:
1. WIC_GLOBAL_UNCONNECTED_EVIDENCE_OUTPUT_CLOSURE
2. WIC_GLOBAL_USER_INTENT_RULE_OUTPUT_ENFORCEMENT
3. WIC_ZERO_USER_REPETITION_AUTONOMOUS_OPERATION_CLOSURE

Root A automatic factory/failover was already actual-PASS.
Known runs:
- forced failover supervisor 38043275030
- replacement 38043286944
- central return success
24h natural-time validation remains:
PENDING_NATURAL_TIME_DO_NOT_RESTART

## 3. Frozen anti-waste rules
Never rerun:
- 3200 baseline
- D110415
- F100k
- USB262
- D2
- C one-shot
- 2,105,850 enumeration
- broad storage/history scans

No C/D/F drive broad search.
No USB broad search.
No version hunting.
No blanket retest.
Reuse valid PASS evidence.
Only changed root + impacted paths may be tested.

## 4. Tool013 history and why prior PASS was invalidated
Tool013 is ASSEMBLY_ONLY. Do not redevelop it from scratch.

Known prior actual input binding:
C:/Users/obk36/Downloads/TOOL013_실제입력양식_원본.xls
SHA B31A4F...

Known older candidate:
I:/GPT 도구 작업/13번 엑셀 업로드 도구/13번_V2_최종운영판.html
older SHA 62CE7A...

Prior checkpoint:
WIC-CP-20261008-TOOL013-NEXT-WORK-HANDOFF-READY

Prior final directive:
handoff/WIC_FINAL_WORK_EXECUTION_DIRECTIVE_2026-10-10.md
commit 2f78e399...

Tool013 was later internally reported PASS, but actual user-visible output contradicted that PASS.
Therefore actual user-visible output outranks internal PASS labels.

User-visible failures observed:
- 773 rows were blocked.
- category display corruption previously included codes/numeric-like values and non-official display values.
- Excel serial dates leaked previously.
- visible field/wiring problems existed.
- later correction workbook improved category/date display but required the user to manually correct hundreds of rows.
- correction workbook columns included 오류_원본행, 오류_필드, 오류_실제값, 오류_기대값, 오류_이유.
- many errors were 2차카테고리, 한글명, or both.
- the user was forced to discover/test the failure after a PASS claim.

Current truthful affected status:
TOOL013 USER_USABLE_FINAL = HOLD
AUTONOMOUS_RECOVERY = HOLD
RECORD_IDENTITY_INTEGRITY = UNVERIFIED
USER_MANUAL_REPETITION = FAIL

Negative Golden classes:
- USER_FORCED_MANUAL_VALIDATION
- BLOCK_WITHOUT_AUTONOMOUS_RECOVERY
- RECORD_IDENTITY_INTEGRITY_UNPROVEN
- PASS_CONTRADICTED_BY_ACTUAL_USER_OUTPUT
- CATEGORY_CODE_AS_DISPLAY_VALUE
- EXCEL_DATE_SERIAL_LEAKAGE
- WRONG_COLUMN_MAPPING
- BLANK_REQUIRED_OUTPUT
- CROSS_ROW_FIELD_MIXING
- DUPLICATE_RECORD
- MISSING_RECORD
- IDENTITY_SWAP
- OUTPUT_NOT_REOPENED

## 5. Maximum-common rule established from Tool013 failure
For separable-record workflows:

ERROR FOUND != WHOLE JOB STOP.

Required generic behavior:
problem record
-> detect
-> classify
-> deterministic auto-repair using existing approved components
-> automatic revalidation
-> if repaired, join usable output
-> if not safely resolvable, quarantine only that record
-> continue all unaffected safe records.

Example:
1000 input
= 980 normal + 15 auto-repaired + 5 unresolved
=> 995 usable output + 5 quarantined.

The user must NOT manually repair hundreds of Excel cells.
Correction/quarantine workbook is audit evidence, not a mass manual work assignment.

Exception:
If record identity/lineage is corrupted or cross-row contamination makes safe output untrustworthy, block the affected unsafe final output.

## 6. Record identity invariant
Every record must preserve:
origin_file + origin_row + stable_record_id

through:
INPUT
-> MERGE
-> TRANSLATION
-> CATEGORY
-> DATE
-> FIELD MAPPING
-> VALIDATION
-> AUTO-REPAIR
-> QUARANTINE
-> FINAL OUTPUT.

Order may change; identity may not.

Required proof:
MISSING_RECORD_COUNT = 0
DUPLICATE_RECORD_COUNT = 0
IDENTITY_SWAP_COUNT = 0
CROSS_ROW_MIX_COUNT = 0

Required count invariant:
INPUT_RECORD_COUNT =
FINAL_USABLE_COUNT + QUARANTINED_COUNT + explicitly documented non-business rows.

## 7. Meaning of “common mechanism”
In user-facing explanations, avoid vague jargon.
“Common mechanism” means:
one reusable shared error-handling function/path used by multiple WIC tools:
detect error -> auto-fix -> recheck -> quarantine only unresolved rows -> continue safe rows -> verify row identity.
Do not build the same repair logic separately inside every tool.

## 8. Current first Work / NEXT_ROOT
Exact NEXT_ROOT:
USER_VISIBLE_OUTPUT_AUTONOMOUS_RECOVERY_AND_RECORD_IDENTITY

The first Work must combine:
- ZERO-RECURRENCE / FAIL-CLOSED top-level gate
- USER_VISIBLE_OUTPUT_AUTONOMOUS_RECOVERY
- ROW ISOLATION
- RECORD IDENTITY INTEGRITY

The 42/16 ZERO-RECURRENCE directive is the top-level control layer.
The current Tool013/root work is the execution target underneath it.
They are not two independent jobs.

Do not execute duplicate E2E/Negative/Recovery/Evidence/read-back just because both directives require them.
One valid evidence result may satisfy both layers.

## 9. ZERO-RECURRENCE / FAIL-CLOSED requirements that must remain
Before substantive work, use a PRE-WORK HARD GATE.
It must establish, with evidence, the ability to identify:
actual input, canonical registry, latest master, current requirements, feedback/failure history, validator, evidence gate, partial-completion gate, queue, failure classification, recovery path, actual E2E, negative test, recovery test, read-back, impact regression, output gate, checkpoint recovery, preservation of existing PASS, and separation of actual output from observer report.

For the current root it must additionally prove capability for:
record identity, row-independent handling, deterministic repair, automatic revalidation, unresolved-row quarantine, continuation of safe rows, actual XLSX reopen, source/final identity comparison, and missing/duplicate/swap/cross-row-mix detection.

If a required Preflight item is NO/UNKNOWN/no evidence:
PRE_WORK_GATE = FAIL.
Do not launch expensive broad work.
Only repair the minimum automatically repairable preflight defect, or report BLOCKED_BY_PREFLIGHT.

Core zero-bypass route:
INPUT -> IDENTITY -> REGISTRY -> LATEST MASTER -> CURRENT REQUIREMENTS -> FEEDBACK/FAILURE HISTORY -> REQUIRED DATA -> EXECUTION -> AUTO-RECOVERY/ROW ISOLATION -> VALIDATOR -> EVIDENCE -> COMPLETION MATH -> REGRESSION -> READ-BACK -> OUTPUT GATE -> FINAL OUTPUT -> OBSERVER REPORT.

Unknown/unverified/no-evidence/not-tested are not PASS.

MASTER_FIXED != RUNTIME_FIXED.
FIXTURE_PASS != ACTUAL_E2E_PASS.
SAVE/COMMIT != READ_BACK_PASS.

Final PASS requires actual Gate + Test + Evidence.

## 10. Tool013 proof requirements
Tool013 is the first proof case for the reusable common behavior, not a one-off patch.

Use known actual MarketsandMarkets Revamped Reports Metadata 17072025 input if it is accessible through known Registry/Evidence/Handoff/current paths.
Do not broad-scan drives to find it.
If inaccessible, record ACTUAL_INPUT=HOLD honestly.

The 773 rows must NOT be manually fixed one-by-one by Work.
Use existing approved:
- translation
- official 18-category logic
- date conversion
- field mapping
- validation
- XLSX generation/download
- existing recovery components
and connect only missing wiring.

Actual proof path:
ACTUAL INPUT
-> UPLOAD
-> PROCESS
-> DETECT
-> AUTO-RECOVER
-> REVALIDATE
-> QUARANTINE ONLY UNRESOLVED
-> CONTINUE SAFE ROWS
-> FINAL XLSX
-> DOWNLOAD
-> REOPEN
-> ACTUAL BUSINESS FIELD VALIDATION
-> RECORD IDENTITY COMPARISON.

Reopen the real XLSX and validate at minimum:
product name, Korean name, category 1/2/3, publication date, and other major business fields.

Do not ask the user to test.

Tool013 HOLD may be released only if evidence proves:
A normal rows continue
B deterministic errors auto-fix
C auto-revalidation
D only unresolved rows quarantined
E no user mass Excel repair
F identity tuple preserved
G missing 0
H duplicate 0
I identity swap 0
J cross-row mix 0
K actual final XLSX reopen PASS
L actual business field comparison PASS
M Evidence PASS
N GitHub remote read-back PASS
O Negative Test PASS
P Recovery Test PASS
Q False-Pass Attack PASS.

## 11. Credit-waste hard gate
Do not repeat the same failing segment indefinitely.
On repeated same-segment failure:
classify/root-fingerprint
-> preserve evidence
-> rollback to last safe verified state if needed
-> checkpoint
-> record exact next resume point
-> stop wasting credits.

Each safe minimum unit:
CHANGE -> TEST -> EVIDENCE -> COMMIT -> READ-BACK -> CHECKPOINT.

Existing valid PASS = SKIP-REUSE.
Impact-based validation only.

## 12. What happens AFTER the first Work
Do NOT mix the following second-stage expansion into the first Tool013 proof before the common behavior is proven.

After the first Work result is known, create/run a second integrated directive covering:
- Tool013 EXCLUDED from redevelopment/retest except evidence reuse
- other major WIC tools
- existing actual-input pending 3
- existing external-original pending 1
- all WIC tools/work from approximately the last year as ROOT-CAUSE DISCOVERY SCOPE.

Important:
“last year” does NOT mean execute/retest every tool.
It means include the year’s tools/failures/feedback in the discovery scope so identical/similar failures can be grouped into the maximum common Root Cause.

Second-stage desired method:
last-year tool/failure scope
-> recover known Registry/Evidence/Failure/Feedback
-> group same/similar failures by ROOT_FINGERPRINT
-> identify maximum common roots
-> reuse existing PASS where unaffected
-> validate major tools first as representative actual paths
-> implement/reuse one common solution per common root
-> propagate only to impacted tools
-> impact-based validation
-> handle truly tool-specific residual failures last.

Do NOT:
- fix the same root separately in every tool
- blanket rerun the last year
- rescan all storage
- redevelop already-complete tools.

This is the preferred balance between omission prevention and credit preservation.

## 13. Remaining known work
After current common-engine/Tool013 proof:
- actual-input pending: 3
- external-original pending: 1

Root A 24h:
PENDING_NATURAL_TIME_DO_NOT_RESTART

These remain separate and must not be falsely counted as completed.

## 14. Required final report for current first Work
PRE-WORK: PASS/FAIL
WORK START ALLOWED: YES/NO
COMMON AUTO-RECOVERY: PASS/HOLD/FAIL
ROW ISOLATION: PASS/HOLD/FAIL
RECORD IDENTITY: PASS/HOLD/FAIL
TOOL013 ACTUAL INPUT: name/inaccessible
INPUT RECORDS
NORMAL
AUTO-REPAIRED
QUARANTINED
FINAL USABLE
MISSING
DUPLICATE
IDENTITY SWAP
CROSS-ROW MIX
FINAL XLSX REOPEN: PASS/HOLD/FAIL
USER MANUAL EXCEL CORRECTION: 0/count
TOOL013 USER-USABLE: PASS/HOLD/FAIL
NEGATIVE TEST: PASS/FAIL
RECOVERY TEST: PASS/FAIL
ACTUAL E2E: PASS/FAIL
EVIDENCE-LESS PASS: count
OUTPUT BYPASS: count
CRITICAL UNKNOWN: count
REGRESSION: PASS/FAIL
GLOBAL PROPAGATION: PASS/PARTIAL/HOLD
ACTUAL-INPUT REMAINING: count
EXTERNAL-ORIGINAL REMAINING: count
24H: status
PLATFORM_LIMIT: count
CHECKPOINT: id
GITHUB: commit
REMOTE READ-BACK: PASS/FAIL
NEXT_ROOT: exact root/NONE
FINAL: PASS/HOLD/FAIL/BLOCKED

## 15. Next-chat instruction
The next ChatGPT conversation must:
1. Read this handoff first.
2. Read the referenced latest checkpoint/evidence as needed.
3. Do not ask the user to repeat this conversation.
4. Do not rerun closed common work.
5. Preserve before/current Tool013 separation.
6. Continue from the exact current NEXT_ROOT.
7. First Work = current integrated zero-recurrence + auto-recovery + row-isolation + identity proof.
8. Only after its result, prepare/execute the second-stage integrated directive for other major tools + pending 3+1 + last-year maximum-common-root audit.
9. Treat user-visible actual output as stronger evidence than an internal PASS label.
10. User remains observer only.
