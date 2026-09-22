# WIC Work 3-MICRO Credit-Efficient Protocol

## Purpose

Use ChatGPT Work with the smallest practical bounded batch while WIC is being completed, especially TOOL044-centered multi/batch cycles and free unattended external execution.

## Fixed operating rule

- One Work request: maximum 3 MICRO tasks.
- Stop automatically after MICRO 3. Never begin MICRO 4.
- Each MICRO has one narrow purpose.
- Reuse already verified evidence and paths.
- Do not revalidate PASS items unless a new change directly affects them.
- Do not retry unchanged HOLD items.
- On STRUCTURAL_HOLD, isolate it and move to the next independent blocker unless that HOLD is the direct current target.
- Avoid broad repository rediscovery.
- Avoid repeated GitHub Actions runs.
- Avoid large E2E tests until the final verification stage.
- Use synthetic/isolated data for validation; do not mutate production customer/business state.
- After a failed validation, record the first disconnect only. Do not immediately perform multiple repairs/retries in the same batch unless explicitly scoped.
- User receives/pastes only the final result of the 3-MICRO bundle; no intermediate manual relay is required.

## MICRO consolidation rule

- MAX_MICRO = 3 remains a hard ceiling.
- Within that ceiling, combine work only when the combined work reuses the same evidence, repository reads, execution, or validation and therefore reduces total time, credit usage, approval prompts, or duplicate setup.
- Prefer one MICRO that batches closely related reads/checks over multiple MICRO tasks that repeat the same context or evidence.
- Do not combine work merely to reduce the visible number of rounds.
- If consolidation would materially increase execution scope, retries, approval count, failure blast radius, or credit use, keep the work separated using the existing bounded method.
- PASS evidence must be reused rather than re-created as part of a consolidated task.
- The decision rule is: **consolidate only when it is actually cheaper/safer; otherwise preserve the current split workflow.**

## Observer-mode approval rule

The user is an observer. The preferred flow is:

**one instruction → wait → one final result**

- APPROVAL_BUTTON_BUDGET = 0 by default.
- If the platform requires approval for an essential action, combine related actions as much as possible and target one approval.
- Do not ask approval command-by-command.
- Batch read-only GitHub metadata, run, job, log, artifact, commit, and blob reads whenever practical.
- If one read-only query is incomplete, do not immediately create another approval prompt for a near-duplicate query. Re-plan remaining reads as one batch.
- If approval prompts begin repeating for the same purpose, stop subdividing. Either use one consolidated essential approval or end with HOLD.
- Write/execute approval may remain when genuinely required, but the change scope must be bounded before asking.
- Do not force zero approvals when that would create an artificial HOLD. The priority is zero approvals when possible; otherwise the smallest consolidated approval count.
- Same/near-identical read-only approval retries are forbidden unless the previous request actually failed for a new technical reason.

## Error and batch handling

- Collect and classify before repair.
- Do not repair one error at a time.
- Group occurrences with the same underlying cause into one ROOT/BATCH.
- A Work request may still contain at most 3 MICRO tasks; ROOT/BATCH handling happens inside that bounded request.
- Within each MICRO, combine closely related lookup, validation, and read-back work where practical.
- Do not turn every file, error occurrence, log lookup, or read-back into a separate MICRO.

## Credit policy

The 3-MICRO limit is the current preferred balance between very small one-step requests and large Work requests.

It is not a guarantee of zero credit usage. Credit consumption can vary by search scope, tool calls, execution time, repository operations, Actions runs, and retries.

Observed operating principle:
- Too-small requests create repeated setup/context/relay overhead.
- 3-MICRO bundles can combine closely related checks efficiently while keeping scope bounded.
- Larger bundles can increase search, execution, retry, and validation work and therefore may consume more credit.
- Do not enlarge a bundle merely to reduce the number of turns.
- Approval/read-back fragmentation is also treated as avoidable overhead.

## Progress counting

Remaining Work-round estimates are not fixed commitments. The number can decrease when:
- one MICRO satisfies multiple prerequisites safely;
- an existing verified component already satisfies the next requirement;
- a PASS removes the need for a planned follow-up;
- multiple dependent checks can be proven by one bounded execution.

The number can increase only when a real new disconnect is found. Do not invent extra rounds for already verified paths.

## Current final target

A final WIC unattended cycle is not complete until all required conditions are actually verified:

- FREE_EXTERNAL_RUNTIME = REQUIRED
- PHONE_PC_SCREEN_OFF = REQUIRED
- 24H_UNATTENDED_CYCLE = REQUIRED
- PAID_RUNTIME = FORBIDDEN
- multi-demand processing without omission or duplication
- cross-cycle state preservation
- completed-demand reselection prevention
- verified result return
- safe failure/HOLD handling

## Anti-waste rules

- COLLECT_BEFORE_ANY_REPAIR = REQUIRED
- REPAIR_DURING_COLLECTION = FORBIDDEN
- ONE_ERROR_ONE_REPAIR = FORBIDDEN
- ONE_FILE_ONE_REPAIR = FORBIDDEN
- IMMEDIATE_REPAIR_AFTER_DISCOVERY = FORBIDDEN
- IMMEDIATE_REPAIR_AFTER_TEST_FAILURE = FORBIDDEN
- ONE_ROOT_ONE_PUSH = FORBIDDEN
- ONE_ROOT_ONE_CLOUD_RUN = FORBIDDEN
- ONE_ROOT_ONE_READBACK = FORBIDDEN
- PASS_REVALIDATION = FORBIDDEN
- UNCHANGED_HOLD_RETRY = FORBIDDEN
- REPOSITORY_FULL_REDISCOVERY = FORBIDDEN
- STATUS_REDISCOVERY = FORBIDDEN

## Current verified baseline

The following validations are PASS and must not be repeated unless a later change directly affects them:

- MINIMUM_MULTI_CYCLE_PASS
- MIXED_QUEUE_PASS
- MULTI_DEMAND_BATCH_PASS
- MULTI_BATCH_MULTI_CYCLE_PASS
- REMOTE_MULTI_CYCLE_DEPLOY_PASS
- ISOLATED_EXTERNAL_CENTRAL_RETURN_PASS
- FREE_EXTERNAL_SINGLE_RUN_PASS
- completed demands are skipped on later verified cycles
- new demands are processed once in verified isolated paths
- duplicate return = 0 in verified isolated paths
- omission = 0 in verified isolated paths
- production mutation = 0 in verified isolated paths
- GitHub-hosted external execution works without PC or smartphone execution dependency
- isolated input WIC-ISOLATED-35676184779 was processed once and returned once to TOOL016 central ACK
- isolated persistence artifact was saved with production customer/queue/state/checkpoint mutation = 0

Relevant deployed evidence:
- isolated-contract commit: 591b75bf056424e295625c91e14c8e37bf1fd188
- successful isolated run: 35676184779
- RUN A artifact id: 10672364968
- scheduled-restore contract commit reported by Work: 95c3f1ea5339bb73d6bc85e190e9863f1d018529
- central ACK: TOOL016_CENTRAL_RECEIVED

## Current next target

Current target: **SCHEDULED_CROSS_RUN_CONTINUITY**

Current state:
- RUN A isolated artifact exists.
- A scheduled isolated-artifact restore contract was reported written to main at commit 95c3f1ea5339bb73d6bc85e190e9863f1d018529.
- At the last Work check, no scheduled RUN B after that change existed yet.
- Final remote read-back was intentionally not approved to avoid another fragmented approval prompt.
- Therefore continuity PASS is not yet declared.

Next evidence should be consolidated when doing so reduces duplicate work:
- confirm the deployed restore contract;
- find a natural scheduled RUN B after the contract;
- verify prior isolated state restoration;
- completed-demand reprocessing = 0;
- duplicate central return = 0;
- production mutation = 0;
- persistence preserved.

If the same evidence can safely support FREE_MULTI_BATCH_SCHEDULED_CYCLE without extra broad execution, combine that validation in the same max-3-MICRO Work round. Otherwise keep it separate.

Do not redo FREE_EXTERNAL_SINGLE_RUN or earlier synthetic multi-cycle validations.

After scheduled cross-run continuity, advance toward:
1. FREE_MULTI_BATCH_SCHEDULED_CYCLE
2. 24H_UNATTENDED_CYCLE evidence

Do not call the entire WIC business system fully autonomous solely from these runtime proofs; separate structural business-path HOLDs remain until independently resolved.
