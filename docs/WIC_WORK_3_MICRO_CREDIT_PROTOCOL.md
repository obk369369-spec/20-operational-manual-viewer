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

## Credit policy

The 3-MICRO limit is the current preferred balance between very small one-step requests and large Work requests.

It is not a guarantee of zero credit usage. Credit consumption can vary by search scope, tool calls, execution time, repository operations, Actions runs, and retries.

Observed operating principle:
- Too-small requests create repeated setup/context/relay overhead.
- 3-MICRO bundles can combine closely related checks efficiently while keeping scope bounded.
- Larger bundles can increase search, execution, retry, and validation work and therefore may consume more credit.
- Do not enlarge a bundle merely to reduce the number of turns.

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

## Current verified multi-cycle baseline

The following isolated synthetic validations have passed and should not be repeated without a relevant code change:

- MINIMUM_MULTI_CYCLE_PASS
- MIXED_QUEUE_PASS
- MULTI_DEMAND_BATCH_PASS
- MULTI_BATCH_MULTI_CYCLE_PASS
- completed demands are skipped on later cycles
- new demands are processed once
- duplicate return = 0 in the verified isolated paths
- omission = 0 in the verified isolated paths
- production mutation = 0 in the verified isolated paths

Next work should advance toward safe remote deployment and free external unattended execution rather than repeating these local synthetic validations.
