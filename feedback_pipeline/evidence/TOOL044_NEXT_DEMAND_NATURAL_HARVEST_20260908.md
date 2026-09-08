# TOOL044 next-demand natural harvest

- Natural scheduled run: `2026-09-08 09:33:01 KST`; cycle `20260908T003302Z`.
- Trigger: `SCHEDULED`; `work_triggered=false`; `user_triggered=false`.
- Demand: `T42-TOC-STRUCTURE-EXTRACTION`.
- Candidate: `mistune 3.3.4`; official source `https://pypi.org/pypi/mistune/3.3.4/json`.
- License: `BSD-3-Clause`.
- Dependency receipt: `typing-extensions; python_version < 3.11`; not active in the Python 3.11 runtime used for verification.
- Artifact: `mistune-3.3.4-py3-none-any.whl`.
- Official SHA-256: `ee015381e955e370962968befe1d729ab60fafb6a715ac6751763fbce38c8d4a`.
- Actual SHA-256: `ee015381e955e370962968befe1d729ab60fafb6a715ac6751763fbce38c8d4a`; `MATCH`.
- Sandbox normal: Markdown headings `1`, `1.1`, `1.1.1`, `1.1.1.1` produced AST levels `1,2,3,4`.
- Sandbox malformed/no-heading: no heading tokens produced.
- Expected versus actual: `MATCH`; sandbox `PASS`.
- New component: `MISTUNE_3_3_4_TOC_STRUCTURE_EXTRACTION = VERIFIED_REUSABLE`.
- html2text composition: `NOT_TESTED`; no actual TOOL042 HTML-to-TOC failure fixture was available, so no composition was invented.
- Paid API/SaaS calls: 0; production mutations: 0.

