# WIC Work Handoff — Zero-Touch Residual Circulation

ROOT_ID = WIC-COMMON-ZERO-TOUCH-FEEDBACK-CIRCULATION
PRIORITY = CRITICAL
OBSERVER_REINSTRUCTION_REQUIRED = 0
PASS_POLICY = E2E_EVIDENCE_ONLY

## Purpose
Finish the common failure in which the observer still has to ask again whether prior requirements are complete or manually request that unfinished work be reinserted.

## Reuse / do not rebuild
Preserve all evidenced PASS locks, including OUTPUT_GATE_ENFORCEMENT, INSTRUCTION_CONFLICT_DEDUP, TOOL016↔WORK handoff validation, verified multi-gate components, and existing 30-lane GitHub Actions execution capacity. Regression-check only.

## Required implementation
1. At every work closeout, load ALL previously unresolved requirements plus requirements added during the current cycle.
2. Reconcile by evidence and classify every item exactly as COMPLETE / PARTIAL / UNFINISHED / PLATFORM_HOLD / LONG_TERM_HOLD.
3. PASS-lock only items with actual E2E evidence.
4. Automatically requeue every actionable PARTIAL or UNFINISHED item into the next TOOL044 circulation queue. The observer must never need to say "requeue", "check again", or copy the item again.
5. Automatically select and hand off the next executable work after requeue.
6. Produce a durable observer report containing: completed this cycle, partial, unfinished, platform hold, long-term hold, auto-requeued items, and next automatically selected work.
7. Bulk-ingest all accessible feedback/error/improvement directives from TOOL016/TOOL044 durable sources, deduplicate by common cause, and propagate the resulting work to every related accessible tool/program target.
8. Preserve checkpoints across Work/TOOL044 interruption and resume from the last verified point instead of restarting.
9. If GitHub/ordinary runtime can complete an atomic item, use it. If implementation remains impossible there and a complete restart package exists, mark it WORK_ELIGIBLE and hand it to Work. Do not use WORK_REQUIRED_REMAINDER=0 to hide implementation work that is still objectively UNFINISHED.
10. Work completion itself is not global completion. Immediately after Work returns, run the global residual reconciliation again and automatically retain/requeue everything not proven COMPLETE.

## Platform boundary
Native automatic reading/writing of every historical ChatGPT conversation is PLATFORM_HOLD unless an actually supported hook is installed and evidenced. Keep it tracked; do not fake PASS and do not let it block other actionable work.

## Acceptance evidence
PASS requires all of:
- GLOBAL_REQUIREMENT_RECONCILIATION_PROVEN
- STATUS_CLASSIFICATION_PROVEN
- ALL_ACTIONABLE_UNFINISHED_AUTO_REQUEUED_WITHOUT_OBSERVER_INPUT
- NEXT_WORK_AUTO_SELECTED_AND_HANDED_OFF
- TOOL016_RESULT_ACK_RECEIVED
- DURABLE_OBSERVER_REPORT_WRITTEN
- REMOTE_GITHUB_READBACK_PASS
- observer_reinstruction_required = 0

Any cycle that merely reports unfinished work but waits for the observer to request reinsertion is FAIL.

## Required final report
Return evidence under five buckets:
COMPLETE / PARTIAL / UNFINISHED / PLATFORM_HOLD / LONG_TERM_HOLD.
Also return AUTO_REQUEUED and NEXT_WORK.
