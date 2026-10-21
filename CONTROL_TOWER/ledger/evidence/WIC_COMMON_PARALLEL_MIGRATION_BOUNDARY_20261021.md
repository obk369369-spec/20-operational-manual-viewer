# WIC common parallel migration boundary — 2026-10-21

## Source and scope

- Existing isolated branch: `wic16-two-lane-integration-20261021`; baseline `97ca32067d258f7630073ec5841b9336c0530b1c`.
- Reuse existing RULES and COMPONENTS official intake lanes, shared Gate, Queue, Workers, provenance receipts and the GitHub Actions runner; **this document creates no new lane, queue, worker or execution authority**.
- Inputs: `feedback_pipeline/VERIFIED_COMPONENT_REGISTRY.json` (8 verified-reusable components), `feedback_pipeline/wic_target_registry.json` (17 registered targets), `CONTROL_TOWER/ledger/WIC_MASTER_INCOMPLETE_LEDGER_20261004.json` (11 historic incomplete roots), existing commit and workflow evidence. The October 4 incomplete ledger is a historical checkpoint, **not a fresh total**.
- Retain existing PASS_LOCK, 6 Job Packs and all prior evidence. No 3,200-case re-scan, no repeat component tests, no chat-history crawl.

## Actually proven, not inferred

- Commit `6608bcce`: existing 8 COMPONENTS selections preserve source commit/hash/evidence and target re-test requirement in claim receipts; this is **not actual external execution**.
- Commit `97ca32067d258f7630073ec5841b9336c0530b1c`; GitHub Actions run `39565172563`: isolated, pinned `doit 0.37.0` wheel ran two independent **synthetic** tasks `TOOL016` and `TOOL044`. Both wrote expected isolated marker files and passed the runner check. This proves one reusable DAG engine can run two jobs in the nonproduction runner, **not concurrent overlap measurements, business E2E or platform-wide migration**.
- External finished products for TOOL013 (pre-investigated Akeneo Supplier Data Manager, WeTransform AI Data Onboarding, LCM TradeIntel, WISEPIM; alternates Claro, SKU Launch, openProd.io + Pimcore) remain **CANDIDATE** until authentic product access and WIC source -> product run -> native output -> comparison -> evidence are obtained. Do **not** conflate TOOL013's existing source tool or existing verified UI modules with importing these external finished products.
- Observed real migrated business jobs: **0**. Observed actual external product E2E PASS: **0**. Operating authorization stays blocked.

## One shared execution route, existing two input lanes

`existing RULES + existing COMPONENTS -> existing central admission Gate -> existing Queue/Worker/runner -> actual product or pinned component -> existing output validator -> existing Evidence -> independent PASS/FAIL/HOLD`.

No route consolidation may bypass fail-closed STOP/admission. Shared socket proof is reusable; each tool's authentic output and functional PASS is independently required. A new product merely named in a registry or a claimed job is not imported/executed.

## Maximum-common parallel work bundles (classification, NOT completion)

| Bundle | Existing roots and components | Parallelization rule | Current evidence/status |
| --- | --- | --- | --- |
| A — canonical evidence, status, observer | `CR-LEDGER-QUEUE-RECONCILIATION`, `CR-CONTROL-TOWER-STATE-INTEGRITY`, `CR-TOOL044-AUTONOMOUS-CIRCULATION-RESIDUAL` | Reuse one canonical root/ID, validator, evidence ledger; reconcile before observer/return | Historical open; no new E2E PASS |
| B — manifested business source intake | `CR-ACCESSIBLE-BUSINESS-ASSET-CANONICALIZATION`, `CR-TOOL001-006-SOURCE-RECOVERY`, `CR-WIC-SCOPED-RECOVERY-0702`; reusable provenance gate | Bounded source manifests, source hash and immutable raw input; parallel independently available source scopes | Non-GitHub USB/PC assets inaccessible from runner absent authorized mount; HOLD per source |
| C — external finished products and product sockets | TOOL013's recorded external CANDIDATES; other one-year-delayed tools' **already recorded** product candidates; existing `DOIT_0_37_0_LOCAL_DAG_EXECUTION_ENGINE`, `WIC_EXTERNAL_COMPONENT_RECEIPT_ASSEMBLY_LAYER` | Share connector/admission/output-evidence contracts across distinct products. Parallelize only independent accessible product accounts and authentic fixtures | Pinned DAG synthetic nonproduction execution PASS; actual external finished-product E2E not run |
| D — existing registered component target work | All 8 VERIFIED_REUSABLE components; existing 6 Job Packs; registered tool targets | Reuse per-source pin; parallel separate approved targets, no re-test of pre-existing PASS | 1 pinned DAG engine executed synthetic 2-task workflow; other 7 and 6 Job Packs not run in this scope |
| E — third-party permissions/runtime | `CR-INDEPENDENT-24H-EXTERNAL-RUNTIME`, `CR-FLOWWINK-SUPABASE-E2E`, `CR-T41-T42-CUSTOMER-NATIVE-E2E` | Isolate external authentication/dependency holds; do not stall A–D | HOLD: account/backend/customer data authorization |
| F — platform restricted/final | `CR-CHAT-SOURCE-NATIVE-INTERCEPTOR`, `PAPERCLIP-FINAL-SLOT` | Preserve platform HOLD; Paperclip waits its already defined final slot | PLATFORM_HOLD / DEFERRED |

All ROOTS here are *already indexed* in the existing ledger. This mapping is not a new claim that all WIC work is inventoried. Keep later Queue/Backlog/Incomplete updates as incremental inputs, grouped by the same reusable boundary. No blanket permission to run real customer tasks.

## Per-product/per-job independent 12-point preflight

For each existing candidate: exact native product and target; prior authentic requirements; existing source original; actual input; expected native output; golden normal result; execution receipt path; PASS test; FAIL/HOLD condition; budget/time cap; next pre-ranked candidate. Evidence plan and actual permissions must exist **before** nonproduction launch. No re-search of prior candidate list. Unknown credentials, incompatible business input, unavailable native capability or subscription constraints must remain HOLD, not simulated success.

## Resource and failure boundaries

- Existing pinned component and verified PASS: SKIP-REUSE / DO_NOT_TOUCH.
- No repeated setup/test loop. One candidate targets <=10–15% of available credit, about 20% maximum; stop on hard mismatch and move to previously ranked fallback.
- Real product evidence must be independently attributable to that product and input, including output artifacts and differential checks.
- `main`, production, STOP and `START_BLOCKED=TRUE` unchanged; real customer output remains forbidden unless separately authorized.
- Complete only after verifiable changes and remote read-back; no success statement from this mapping alone.

## Result of this incremental evidence step

This file freezes **shared grouping and migration boundaries** to prevent repeated Work test design and product research; it is not an import, runtime launch, or product proof. Product imports and the rest of the backlog are **NOT DONE**. Future implementation can claim completion only with per-tool business result receipts and shared-route evidence.
