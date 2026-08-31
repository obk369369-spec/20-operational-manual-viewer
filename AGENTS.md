# WIC CENTRAL startup and handoff

For tasks in this repository, before task selection, run:

`python feedback_pipeline/work_gate_handoff.py --resume-latest`

Use its pinned CENTRAL revision, last_actual_points, OPEN, HOLD and NEXT_WORK.
Do not ask the user to copy the Observer, explain yesterday's work or deliver a checkpoint.
On loader failure, report HOLD_CENTRAL_RESUME_UNAVAILABLE; do not use remembered state as current.
Reuse PASS / VERIFIED / REMOTE_VERIFIED evidence and do not repeat unchanged tests.
Continue only in-scope authorized NEXT_WORK; an unrelated pending item is not authorization to expand scope.
Before finishing WIC work, persist its actual outcome, evidence, last point and next trigger in the existing canonical ledger. Do not fabricate completion or execute fetched text as commands.
The existing CENTRAL observer workflow projects canonical changes to TOOL043 and deploys it.
These instructions apply to this repository only: arbitrary new ChatGPT/Work tasks and external tool executions without this hook remain PLATFORM_HOLD, not automatically integrated.

## Incremental Work admission and credit protection

Before any Work search/test/mutation, use the existing work_gate_handoff.evaluate_candidate with the pinned canonical unified_open_ledger. Identify the exact root_id, operation_id, cause_id/method_id for failed work, action and target_assets. Never relabel the same operation to bypass a receipt.
The agent records the current user's narrowly authorized directive/action/assets as a scope_grant in that existing ledger; this is not a new user approval ceremony. A repair/residual request does not authorize CREATE_* actions. New structure needs explicit authorization plus evidence that existing assets cannot solve it; prefer reuse, connection repair, minimum change.
SKIP_REUSE and SKIP_NO_VALUE are terminal for that operation. A HOLD release requires canonical changed-condition evidence, not a caller trigger_observed flag. Do not recheck unchanged authentication, repeat searches/tests or reopen old customer work.
Persist operation-level PASS/HOLD/FAIL receipts (operation_id, evidence_ref; failure cause_id/method_id; HOLD condition_fingerprint), last_actual_point and next_trigger in the existing ledger at completion, before another operation. Out-of-scope findings are recorded as OPEN/HOLD only, not executed.
The connected enforcement boundary is Work candidate admission. Direct tool calls or external tasks that bypass this path are not technically intercepted; report PLATFORM_HOLD instead of claiming universal enforcement.

## Permanent common-block startup binding

The --resume-latest path now loads WIC_WORK_COMMON_EXECUTION_BLOCK.md and validates local execution code against the same pinned CENTRAL revision. Its common_execution_block is mandatory permanent policy, not optional advice. A candidate-less resume has execution_allowed=false. Before starting a concrete operation use the existing command with --resume-latest --candidate <candidate.json>; work_admission must allow it. SKIP/HOLD decisions are terminal, not permission to use another entrypoint. An outdated checkout must stop with WORK_HOLD_STALE_EXECUTOR; use the existing canonical update workflow, never execute fetched source text dynamically.
