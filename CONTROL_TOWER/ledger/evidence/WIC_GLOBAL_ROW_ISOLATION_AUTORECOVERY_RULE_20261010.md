# WIC Global Row Isolation / Auto-Recovery Rule
Date: 2026-10-10
Scope: ALL WIC tools, workflows, conversations, customer/report processing paths

## Mandatory global behavior
For every row/record/item processing workflow:
1. Detect a problem at record level.
2. Attempt deterministic automatic correction using already-approved rules/components.
3. Revalidate the corrected record automatically.
4. If correction cannot be proven safe, quarantine ONLY that record.
5. Continue processing all unaffected records.
6. Never require the observer to manually edit hundreds of rows/cells to continue.
7. Never fail or discard the whole file merely because one or more independent records are unresolved.
8. Exception: if record identity/lineage integrity is broken or cross-row contamination is detected, block the affected final output because unrelated data may be corrupted.

## Identity invariant
Every record must retain stable identity across input -> transform -> validation -> recovery -> final output:
origin_file + origin_row + stable_record_id.
Validation must prove no omission, duplicate, identity swap, or cross-row field mixing.

## Output contract
Produce:
- usable output containing all verified normal and safely auto-corrected records;
- quarantine output containing only unresolved records with reason/candidates/source identity;
- machine-readable counts for input, normal, auto-corrected, quarantined, omitted, duplicated, identity failures.
The observer approves exceptional ambiguous decisions only; the observer is not the repair operator.

## Hard Gate
PASS is forbidden when:
- an independent bad record blocks otherwise valid records;
- manual spreadsheet repair is required for deterministic errors;
- final output was not automatically revalidated;
- record identity integrity is unproven;
- actual user-visible output contradicts internal PASS evidence.

## TOOL013 Negative Golden
The observed 773-row correction-file workflow is a failure example: detection/explanation may pass, but forcing the observer to repair the workbook is not autonomous recovery.
This is a common-platform rule; do not solve future occurrences row-by-row or publisher-by-publisher.

## Propagation
This rule is mandatory for all WIC tools and processing conversations going forward. Apply by impact when a tool processes separable records. Do not blanket-retest already PASS_LOCKed unrelated functionality; enforce this gate when affected paths next execute or are changed.
