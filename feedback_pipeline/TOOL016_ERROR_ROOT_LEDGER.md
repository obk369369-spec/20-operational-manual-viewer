# TOOL016 ERROR ROOT LEDGER

Scope: evidence-backed TOOL041 / TOOL007 / TOOL042 errors only. Counts are confirmed occurrences in the cited fixtures/evidence, not estimates.

| ROOT | TOOL | Discovery | Confirmed occurrences | Symptom | Root cause | Responsible existing layer | Why it missed | Scope | Status / evidence |
|---|---|---:|---:|---|---|---|---|---|---|
| `T41-RC-DATA-INTEGRITY` | 041 | USER | 3 | duplicate rows, phone conflict overwrite, locked ID replacement | identity/field merge did not fail closed | TOOL041 `customer_integrity` | legacy merge lacked field conflict/identity lock | TOOL-specific | VERIFIED_CLOSED; `tests/fixtures/t41_actual_pairs.json`, `t41_t42_actual_fixes_20260825.json` |
| `T41-RC-CURRENT-MASTER-LINKAGE` | 041 | WORK | 2 | current customer fields missing; current identity not unique | actual row cannot be uniquely joined to current canonical master | TOOL041 current-master guard | source customer evidence incomplete | TOOL-specific | HOLD_EXTERNAL; `TOOL041_042_AUTOMATION_20260831.json` |
| `T7-T42-RC-CONTACT-COPY-QUALITY` | 007,042 | USER | 3 | purpose/marketing exposure, generic follow-up, long administrative opener | copy generation did not consistently reuse actual response/history constraints | existing copy validator/release gate | fixed structural checks cannot prove all semantic naturalness | Shared 007/042 | PARTIAL_VERIFIED/HOLD_SEMANTIC; `contact_copy_actual_cases.json`, `TOOL041_042_RELEASE_GATE_20260831.json` |
| `T42-RC-CUSTOMER-BRANCH` | 042 | USER | 2 | uniform branch; proceeds with unverified history | customer/history/recommendation branch contract incomplete | TOOL042 `branchCustomer` | legacy path did not require the verified state bundle | TOOL-specific | VERIFIED_CLOSED; `customer_branch_actual_kmg.json`, `t41_t42_actual_fixes_20260825.json` |
| `T41-T7-T42-RC-FACT-BOUNDARY` | 041,007,042 | USER+WORK | 4 | company direction treated as personal interest; outbound send treated as customer action; downstream output from incomplete upstream | verification contract did not require contact-history evidence at the 041→007 boundary | existing `p1_to_p2_handoff`, TOOL007 judgment, TOOL042 branch gate | TOOL042 checked history but the earlier TOOL007 boundary did not | Shared all three | FIXED_THIS_WORK; actual cross-tool fixture plus negative history fixture |
| `T42-RC-SEMANTIC-EXECUTOR` | 042 | WORK | 1 | eight semantic checks remain `HOLD_NOT_EXECUTED` | authenticated semantic runtime absent | existing release gate | required execution environment/evidence unavailable | TOOL-specific | HOLD_EXTERNAL; `TOOL041_042_SEMANTIC_EXECUTOR_HOLD_20260831.json` |

## Recurrence/dedup

- `T41-RC-DATA-INTEGRITY`: 3 confirmed manifestations, one ROOT.
- `T7-T42-RC-CONTACT-COPY-QUALITY`: 3 confirmed user-corrected manifestations, one shared ROOT.
- `T41-T7-T42-RC-FACT-BOUNDARY`: 4 confirmed manifestations grouped by the same evidence-boundary failure; no new layer created.
- Closed ROOTs remain `SKIP_REUSE` unless their directly affected contract changes.

## This Work

- Existing layer strengthened: `contact_history_verified` is now mandatory in `p1_to_p2_handoff` and TOOL007 `judge_contact`.
- TOOL042 already had `contact_history_verified` fail-closed handling, so it was not modified.
- No TOOL044 component and no new common execution layer were required.
