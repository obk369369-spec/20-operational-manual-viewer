# TOOL042 — 440 Guide Assets Canonical Registry

STATUS: PARTIAL_CANONICALIZED
DATE: 2026-10-06
OWNER: WIC / TOOL042
CANONICAL_REPO: obk369369-spec/20-operational-manual-viewer

## Purpose
This is the single canonical entry point for the 440 customer-guide source assets. Every chat/workflow MUST read this registry first. Do not ask the observer to re-upload source files merely because work moved to another chat.

## Inventory contract
TOTAL_EXPECTED=440
MARKET_REPORTS=363
ENGINEERING_BOOKS_2026=27
ENGINEERING_BOOKS_2025=50

## Source packages

| Package | Class | Count | SHA-256 | Canonical manifest/evidence | Binary canonical status |
|---|---|---:|---|---|---|
| Activated Carbon Fiber Market Size, Scope, Forecast Report 2026 to 2035 -월드산업정보센터.zip | MARKET_REPORTS | 363 | 1816f35f3330c11d3a998e8e57da537a0fdba76d08d3a4c9b920578dc6c30007 | TOOL042/evidence/WIC_MARKET_REPORT_ZIP_MANIFEST_20261006.csv | HOLD_BINARY_NOT_IN_CANONICAL_REPO |
| Electric Drive System Design for Electric Vehicles-월드산업정보센터.zip | ENGINEERING_BOOKS_2026_A | 18 | 34c7750fb382ecfbb2c99b5bb9114c782f95c7cc1b1cf804d42210279786feef | TOOL042/evidence/WIC_ENGINEERING_BOOKS_2026_ZIP_MANIFEST_20261006.csv | HOLD_BINARY_NOT_IN_CANONICAL_REPO |
| Protection of Electrical Power Transmission Systems -월드산업정보센터.zip | ENGINEERING_BOOKS_2026_B | 9 | NOT_YET_CANONICAL_HASHED | manifest/evidence missing from canonical repo | HOLD_CANONICALIZATION_REQUIRED |
| 2D Materials Fundamentals, Fabrication, and Applications -월드산업정보센터.zip | ENGINEERING_BOOKS_2025 | 50 | NOT_YET_CANONICAL_HASHED | manifest/evidence missing from canonical repo | HOLD_CANONICALIZATION_REQUIRED |

COUNT_CHECK: 363+18+9+50=440

## Mandatory cross-chat rule
1. This registry is the first lookup for TOOL042 guide matching.
2. Existing manifests/index/evidence are reused; no full re-upload request to the observer.
3. A chat split MUST NOT create a private copy, new inventory ID, or separate source-of-truth.
4. CUSTOMER_ID / TASK_ID / GUIDE_ASSET_ID / SOURCE_ID must point back to this canonical registry/evidence.
5. If an original binary is required and the canonical binary is unavailable, status is HOLD_CANONICAL_BINARY_MISSING. Never silently ask the observer to re-upload as the normal workflow and never claim PASS.
6. Once a binary-safe canonical store is available, store the original package once, record immutable location + SHA-256 here, and all chats reuse it.
7. Manifest presence is NOT equivalent to binary preservation.

## Current truth
- 440-count inventory identity is established from four source packages.
- 363-package manifest exists in GitHub and was ZIP-tested PASS when ingested.
- 18-package 2026 engineering-book manifest exists in GitHub and was ZIP-tested PASS when ingested.
- 9-package 2026 engineering-book source and 50-package 2025 engineering-book source are known, but their canonical manifest/hash evidence is not currently present in the repo.
- The first two existing manifests explicitly state that source binaries were retained in conversation upload, so binary centralization is NOT complete.
- Therefore GLOBAL_BINARY_CANONICALIZATION=HOLD. Do not report all 440 original binaries as GitHub-preserved until actual binary read-back evidence exists.

## Acceptance gate
GLOBAL_BINARY_CANONICALIZATION may become PASS only when all four source packages have:
- immutable canonical location
- SHA-256
- entry count
- archive integrity result
- manifest/index
- read-back evidence
and a new chat can resolve the source without observer re-upload.
