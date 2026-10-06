# WIC TOOL042 NEXT CHAT HANDOFF — 2026-10-06

STATUS: ACTIVE HANDOFF / DO NOT RESTART / DO NOT ASK USER TO REPEAT PRIOR RULES

## Immediate purpose
Prepare the president's institution-visit package in batch. Reconcile current organization-chart people with WIC customer ledger/history, decide market-report vs engineering-book vs mixed, match actual guides/books, prevent customer/task/document/print duplicates, and produce compact institution tables plus copy-paste-ready guide blocks only after validation.

## Canonical contract
Before any TOOL042 output, fetch and enforce CUSTOMER_GUIDE_OUTPUT_LOCK.md, especially section 22 (2026-10-06 single output contract). Do not rely on remembered chat prose as the enforcement source.

## User will provide
1. customer daily ledger / transaction-history file if not already resolvable from Library;
2. overseas market-report archive (re-uploaded/new archive);
3. 2025 engineering-book archive;
4. 2026 engineering-book archive;
5. target institution list / organization charts if not already present.
Customer-per-folder ZIP is accepted and preferred when it already contains guides shown to each customer. Preferred folder name: CUSTOMER_ID_기관_이름.

## First ingestion gate for every ZIP
Do once: resolve source -> open archive -> count entries -> persist manifest -> hash/index -> map customer IDs/assets -> read-back evidence. If failure, classify corruption vs encryption/unsupported archive vs retrieval/materialization vs runtime/container vs parser/index. Never merely say cannot open. Preserve registered source. Do not ask re-upload again if current uploaded bytes are accessible.

## Customer identity and dedup
Global dedup key is CUSTOMER_ID (existing CAR-xxx where available). Same CUSTOMER_ID across trip list/42/other task is one customer with multiple TASK_IDs. Do not merge ambiguous same-name people automatically.
Maintain customer ledger: CUSTOMER_ID, institution, person, current dept/title/work evidence, inquiry/quote/purchase/reply history, exact previously-sent titles, task IDs, material type, selected titles, GUIDE_ASSET_ID, PRINT_ASSET_ID, status, evidence.

## Document/printing dedup
Guide master is deduped by GUIDE_ASSET_ID. If the same guide suits several customers, store/print one master guide and reference it from multiple customer rows. PRINT_ASSET_ID is the physical print key. Do not print the same guide once per customer. Only customer-specific cover/note creates a separate customer-specific print asset.

## Institution output — compact, no long vertical repetition
One table per institution:
CUSTOMER_ID | customer | current dept/title | strongest transaction/interest evidence | type(MARKET/BOOK/MIXED/HOLD) | selected exact titles | GUIDE_ASSET_ID | PRINT_ASSET_ID | status.
Then a short unique-print manifest: PRINT_ASSET_ID | exact title | customers who should be shown it | copies. Detailed guide content is not repeated under every customer.

## Selection chain
current org chart -> customer ledger/history -> actual inbound inquiry/purchase/reply stronger than outbound-only mail -> exact prior sent/purchased title exclusion -> existing market-guide archive exhaustive lookup -> 2025/2026 engineering-book archive lookup -> only missing count external official-source research -> validation -> output.
Do not use irrelevant padding. Do not externally research before existing-guide corpus gate passes.

## Market guide copy-paste schema
Exact official English title

Full Korean translation

◇ 발행사: [publisher]        ( [verified pages] Pages )        ◇ 정가: $[verified price]
◇ 발행일: [verified publication date]        -PDF-        ◆ 공급가격:          원

[canonical original-publisher detail URL]

목차:
[actual official TOC from SAME SOURCE_ID, start through last publicly available item; preserve numbering/order/text/hierarchy; plain-text numbers; indentation by depth; no arbitrary depth cap; no summary; no truncation; no reseller splice]

보고서 정보:
[Korean translation of actual descriptive source text only; no model-added prose]

Unverified fields stay blank/HOLD; never invent. Supply price stays blank unless user supplies it.

## Output gate BEFORE user sees a completed guide
Generate internally -> compare field-by-field with Golden Sample -> exact title -> same SOURCE_ID metadata -> publication date -> pages -> price/license -> canonical URL -> actual TOC start/end -> numbering -> indentation -> description translation -> prior-title duplicate -> publisher constraints -> final render/schema diff. Any FAIL blocks display and triggers internal correction/replacement/retest. If unresolved, show HOLD, not a malformed completed guide.

## Responsibility for bad output
If user later catches a format/TOC/factual error, treat it as OUTPUT_GATE_FAILURE, not user QA: revoke PASS, store failure evidence/regression sample, inspect other outputs sharing the cause, fix/revalidate, then reissue. Never claim recurrence prevention without evidence.

## Historical rules that remain mandatory
- Original publisher detail page only for customer-facing market-report source; no reseller as source.
- Exact official full English title; no model abbreviation.
- 2026 first; 2025 only when allowed and justified.
- Trading-publisher pool and exclusions remain active.
- Same customer publisher diversity where applicable.
- Actual TOC required; Scope/segmentation/navigation is not TOC.
- Do not splice metadata/TOC from different sources.
- Past actual EML/inbound/purchase evidence overrides a mistaken UNSENT row.
- Outbound-only mail is not proof of customer interest.
- Existing completed guide first; external new guide only for missing count.
- Selected-set lock: missing field does not delete/replace a locked report.
- No spreadsheet/file creation unless user asks.

## CAR-039 Kim Tae Hee regression facts
KITECH Kim Tae Hee is not UNSENT historically. Actual past evidence includes 2024 nonwoven/e-textile/industrial textile sends, 2024 nanofiber material interaction, and a quoted 2016 inbound email explicitly stating interest in cosmeceuticals and tissue engineering/regenerative medicine. Priority: tissue engineering/regenerative medicine -> biomaterials/medical polymers -> 3D bioprinting; cosmetics secondary. Do not re-send exact prior titles. Final top titles remain HOLD until existing guide archive is actually enumerated/indexed.

## Archive incident already evidenced
Registered Library sources exist for the historical market-guide archives. Previous runtime could materialize raw ZIP but Files text-read returned zero lines and container execution failed. GitHub evidence commits already recorded source recovery/runtime gate. Do not claim 356/356 without a manifest. New re-upload must be tested immediately with archive-open/count/manifest/hash/index.

## GitHub evidence/current update
CUSTOMER_GUIDE_OUTPUT_LOCK.md section 22 added on 2026-10-06.
Commit: bb325c13d13b027ff45bf56623ae83c6b563f0f2.
This update unifies: canonical output contract, pre-display validation, TOC complete gate, CUSTOMER_ID/TASK_ID dedup, GUIDE_ASSET_ID/PRINT_ASSET_ID dedup, institution compact table, ZIP ingestion gate, OUTPUT_GATE_FAILURE responsibility, and batch completion criteria.

## Critical truth about platform enforcement
The old sentence 'GitHub master recorded != automatically executed in every general chat' described a real architectural gap, not an acceptable final design. For TOOL042 now, fail closed locally: no completed customer-guide output unless the latest canonical contract is fetched and applied. The LEVEL-10 target remains global automatic inheritance across all components, but do not claim that platform-wide E2E enforcement is VERIFIED until actual runtime evidence proves it. RULE_WRITTEN != PASS.

## Next-chat start instruction
Do not explain architecture again. Read this handoff + latest CUSTOMER_GUIDE_OUTPUT_LOCK.md; then ingest the user's newly attached market-report / 2025-book / 2026-book archives and ledger, run the archive manifest/index gate, show only a small validated sample if user requested sample approval, lock the approved render schema, then batch the trip institutions. Do not ask user to say continue between customers.
