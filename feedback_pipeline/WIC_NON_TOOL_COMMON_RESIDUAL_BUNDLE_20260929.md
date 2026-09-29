# WIC non-tool common infrastructure residual bundle — 2026-09-29

Scope: common Work/TOOL016/TOOL044 infrastructure only. Individual tool functional work is excluded.

## Preserve as PASS / do not rebuild
- Proven GitHub-side reconciliation/classification/requeue/next-selection/result-return.
- TOOL016 -> TOOL044 active circulation.
- Proven dedup/checkpoint/lease/result-return and remote read-back evidence.
- Existing evidence-backed PASS roots use SKIP-REUSE unless regression/new requirement exists.

## Residual COMMON_ROOTS to execute
1. HISTORICAL_COMMON_DIRECTIVE_LEDGER
   - Recover and normalize all non-tool common-infrastructure Work directives from the earliest available Work handoff through current time.
   - Include later deltas.
   - Every registered requirement must end in COMPLETE, PARTIAL, UNFINISHED, PLATFORM_HOLD, or LONG_TERM_HOLD.
   - No silent NOT_WORKED.

2. GLOBAL_PIPELINE_COVERAGE
   - One central common pipeline for all registered current WIC work chats and normally registered future WIC work chats.
   - Feedback -> central judgment -> root/dedup -> execution preparation -> Work only when required -> validation -> GitHub -> state sync.
   - No separate manual routing by the observer.
   - If native cross-chat capture is unsupported, isolate only that stage as PLATFORM_HOLD; do not claim global coverage PASS.

3. OBSERVER_ZERO_MANUAL_RELAY
   - Observer must not repeatedly copy chat content, carry instructions to Work, locate repo/master, count roots, check GitHub/read-back, calculate next condition, re-explain same error, requeue unfinished work, or manually monitor watchdog status.
   - Platform-required user confirmation remains PLATFORM_HOLD and must not be represented as automated.

4. EXACT_OBSERVER_REPORT_DELIVERY
   - At each closeout first report COMPLETE/PARTIAL/UNFINISHED/HOLD, emphasizing unfinished actionable items.
   - Required destination: existing conversation named "44번 완성부품 가져오기".
   - A GitHub JSON/report file is durable evidence but is not proof of in-chat delivery.
   - If exact existing-chat autonomous delivery is unsupported, record PLATFORM_HOLD and keep other circulation active.

5. CHAT_IDENTITY_AND_AUTOMATION_SAFETY
   - Track unrequested new chat creation, original-chat rename, reminder/schedule creation, automation/task activation.
   - Separate WIC-controlled execution paths from ChatGPT platform behavior.
   - WIC-controlled paths require explicit user request.
   - Platform-controlled behavior that cannot be changed here remains PLATFORM_HOLD.
   - Do not create real chats/schedules merely for destructive testing; use safe negative/fixture testing where possible.

6. CLOSEOUT_RECONCILE_REQUEUE_LOOP
   - After every Work/circulation closeout, reconcile the entire historical common-infrastructure ledger plus new directives.
   - PASS-lock only E2E-evidenced COMPLETE.
   - First produce observer status report.
   - Automatically requeue all actionable PARTIAL/UNFINISHED items.
   - Compress same causes into COMMON_ROOT.
   - Auto-select next eligible root, recover result, then repeat full reconciliation.
   - No user "continue/check/requeue" instruction required.

7. WORK_HANDOFF_AND_CREDIT_EFFICIENCY
   - Free/existing verified circulation first.
   - Work only for work-required residuals.
   - Batch by COMMON_ROOT.
   - No duplicate/PASS reruns.
   - Resume from checkpoint rather than restart.
   - Track handoff heartbeat loss, missing result return, duplicate handoff, stalls, and unnecessary Work invocation; recirculate actionable failures.
   - Credit telemetry must use actual readable values only; never invent usage.

8. CANONICAL_STATE_AND_WORKSPACE_RECOVERY
   - Restore latest central master/state/root ledger/checkpoint/handoff/NEXT_START/OPEN/HOLD before work.
   - Detect the actual WIC workspace rather than permanently hardcoding one drive letter.
   - Wrong or unavailable workspace must be HOLD, never false PASS.
   - Apply DIFF-only changes where appropriate and verify remote read-back.

9. PLATFORM_LIMIT_ISOLATION
   - Unsupported Work invocation/result retrieval, exact existing-chat posting, native all-chat capture, or required platform confirmation must remain explicit PLATFORM_HOLD.
   - A platform limitation must not stop solvable GitHub/TOOL016/TOOL044 circulation.

## Required closeout
- Produce a deduplicated table of all non-tool common-infrastructure requirements with evidence and status.
- Completed items are PASS-locked and excluded from further work.
- Actionable incomplete items are automatically requeued.
- HOLD items retain exact resume condition.
- observer_reinstruction_required = 0 for all supported stages.
- Never claim 100% completion unless the historical ledger completeness itself is proven and every ledger row has evidence-backed status.
