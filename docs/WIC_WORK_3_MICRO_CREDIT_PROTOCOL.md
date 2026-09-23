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


## Final Work operating lock — 2026-09-23

This section supersedes narrower round-planning guidance when preparing the final remaining WIC Work.

### Credit and MICRO ceiling

- FINAL_WORK_CREDIT_HARD_CAP = 20_PERCENT
- CREDIT_RESERVE_FOR_UNEXPECTED_VARIABLES = 80_PERCENT
- MINIMIZE_MICRO_COUNT = REQUIRED
- If the remaining safe work can be completed in 1 MICRO, finish it in 1 MICRO.
- Use 2 MICRO only when separation is actually safer or cheaper.
- MAX_MICRO = 3 remains a hard ceiling.
- Do not spend up to the cap merely because the cap exists.

### Maximum batch repair rule

- Collect remaining errors/work before repair whenever practical.
- Group common errors by common ROOT cause.
- Repair each common ROOT as one batch rather than occurrence-by-occurrence.
- Reuse one validation to prove multiple related fixes whenever the evidence is valid for all of them.
- Maximize consolidation only when it reduces real time, credit, approvals, duplicate reads, setup, Actions, or validation.
- Do not consolidate when doing so increases retry risk, blast radius, approvals, Actions, or credit consumption.

### Non-repeat locks

- PASS_REVALIDATION = FORBIDDEN
- SAME_OR_NEAR_DUPLICATE_QUERY_REPEAT = FORBIDDEN
- UNNECESSARY_ACTIONS_REPEAT = FORBIDDEN
- UNCHANGED_HOLD_RETRY = FORBIDDEN
- RETRY_BLOCKED_WITHOUT_NEW_EVIDENCE = FORBIDDEN
- RUN_B_POLLING_WITHOUT_NEW_EVIDENCE = FORBIDDEN
- ONE_ERROR_ONE_REPAIR = FORBIDDEN
- ONE_ROOT_ONE_PUSH = FORBIDDEN
- ONE_ROOT_ONE_ACTIONS_RUN = FORBIDDEN

### Final remaining-work scope

The final Work scope is not limited to TOOL044 runtime completion. It must account for the remaining WIC system as a whole, while reusing already verified evidence and excluding unchanged RETRY_BLOCKED work.

The scope includes, where still incomplete:
1. observer manual-work removal;
2. automatic collection of errors and feedback across WIC chats/tools;
3. reuse and application of the existing TOOL045 171,910 occurrences / 315 ROOT candidates / 12 ROOT families without re-extraction;
4. application of TOOL046/047 repeated-error and repair instructions;
5. incorporation of actual customer-guide/mail errors and feedback;
6. common-ROOT batch repair;
7. preservation of actual work information from ingress through tracking;
8. automatic HOLD/FAIL return to TOOL016 central;
9. durable state and resume after interruption;
10. duplicate-work prevention / atomic claim;
11. state recovery across runtimes/work sessions where supported;
12. TOOL016↔TOOL044 automatic routing and result return;
13. automatic routing among other WIC tools where evidence/contracts exist;
14. automatic next-work selection;
15. isolation of blocked work so it does not stop independent work;
16. TOOL001 remaining real-use customer-guide automation;
17. TOOL006 remaining TOC/summary work;
18. TOOL007 customer-contact judgment automation;
19. TOOL013 metadata/Excel upload automation;
20. TOOL014 website work that remains actually incomplete;
21. TOOL041→TOOL007→TOOL042 customer-work chain;
22. TOOL042 real guide quality and repeated-output-error removal;
23. TOOL043 actual external release evidence;
24. TOOL044 ready-component import, validation, regression, deployment;
25. reuse of TOOL045 results as improvement input;
26. TOOL048 error/component database accumulation and reuse;
27. remaining HOLD/FAIL/OPEN or undeployed work in other known WIC tools, including previously referenced TOOL009/010/012/018/027/028/029/034/035/039 when still applicable;
28. automatic validation of existing tools;
29. deployment of validated tools to real use locations where a safe contract exists;
30. automatic judgment of whether a new tool is actually needed;
31. external ready-component-first policy;
32. quarantine/HOLD of failed or unsuitable components;
33. automatic selection of revenue-relevant work where a verified business contract exists;
34. customer-work automatic cycle where the required real contracts exist;
35. enforcement of user fixed rules before work and before output;
36. prevention of repeated Work/credit waste;
37. enforcement of the minimum-MICRO / maximum-3-MICRO rule;
38. free external execution;
39. free multi-runtime/failover execution;
40. continuous multi-work processing;
41. safe batch processing without omission/duplication;
42. runtime-failure recovery and handoff;
43. post-deployment revalidation only for newly changed/deployed scope;
44. full WIC E2E cycle;
45. 24-hour unattended operation evidence;
46. persistent final evidence/receipts rather than label-only completion;
47. final omission audit for remaining HOLD/FAIL/OPEN/undeployed/manual-observer work.

### Current newly verified/fixed fact

- FIRST_INFORMATION_LOSS_POINT was identified at the candidate creation path:
  apply_feedback_event.py → work_ready_tracker.py / assess_work_ready().
- Existing source information was not fully preserved in the work candidate.
- Work reported a local fix preserving the then-existing input information and work ID through candidate creation → tracker storage.
- Reported local changed files:
  - feedback_pipeline/apply_feedback_event.py
  - feedback_pipeline/work_ready_tracker.py
- Reported change size: +18 / -5.
- No commit was made in that Work round.
- Existing uncommitted feedback_pipeline/tool044_atomic_watch_v2.py changes must also be preserved.
- Actions = 0 and approval buttons = 0 for that round.

### Current RETRY_BLOCKED fact

- ACTUAL_EXECUTION_TARGET_NOT_PRESENT_AT_SOURCE = RETRY_BLOCKED
- The original candidate input does not currently contain a verified per-job execution handler, arguments, and success criteria.
- Do not retry this problem with reworded prompts.
- Reopen only when new evidence identifies a real job ↔ existing handler contract.
- If such evidence appears naturally during other final work, it may be integrated then.

### Final completion rule

The target is to complete and verify as much of the entire remaining WIC scope as safely possible within the 20% hard cap, using the fewest MICRO tasks and the largest genuinely credit-saving batches.

No item may be marked PASS merely to fit the credit target. Evidence that inherently requires elapsed real time, including a true 24-hour unattended observation, must remain evidence-waiting until the elapsed-time condition is actually satisfied. The system should automate collection of that evidence so the observer does not manually monitor it.


## MICRO-1 enforcement update — 2026-09-23

- CURRENT_5H_REMAINING_BASELINE = 89_PERCENT
- FINAL_REMAINING_FLOOR = 80_PERCENT
- REMAINING_SPEND_BUDGET = ABOUT_9_PERCENTAGE_POINTS
- DEFAULT_MICRO = 1
- MICRO_2_AND_3 = EXCEPTION_ONLY
- Repository/document lookup, evidence reading, error collection, classification, repair, deployment, and validation must not be split into separate MICRO tasks merely because they are different phases.
- Before repair, collect as many remaining actionable errors as practical and group common causes into shared ROOT batches.
- MICRO 2 may begin only when MICRO 1 cannot safely include the work for a concrete technical reason and splitting is expected to reduce total credit/risk. The reason must be recorded as WHY_MICRO_1_CANNOT_SAFELY_INCLUDE_THIS.
- The same requirement applies before MICRO 3.
- A different task type, file, tool number, or validation phase is not by itself a valid reason to create another MICRO.
- Reuse local commit 93761db1b and its verified changes; do not re-create or revalidate them unless a later change directly affects them.
- Preserve all prior anti-waste locks: PASS revalidation forbidden, duplicate queries forbidden, unnecessary Actions forbidden, unchanged HOLD/RETRY_BLOCKED retry forbidden.
- Current priority is to use the remaining budget for actionable bulk repair + deployment + integrated validation, not preparation or repeated status discovery.
