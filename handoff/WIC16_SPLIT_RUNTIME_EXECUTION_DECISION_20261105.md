# WIC16 split-runtime execution decision — 2026-11-05

## User-approved binding rule
When a single 24-hour host is unavailable, split the platform by function and reuse proven existing external tools. Do not block all work because Kestra/Oracle is unavailable. No new internal scripts, API wiring or duplicate tools; no paid resources or credit-based services.

## Existing assets (confirmed)
- `.github/workflows/wic-top-controller-runtime.yml`: scheduled hourly at minute 17 UTC; existing central controller and durable-state commit steps. Requires `WIC_RULE_ADMISSION_JSON` and checks `WIC_USER_STOP`.
- `.github/workflows/tool044-multi-gate.yml`: scheduled every 5 minutes; existing component claims/parallel lanes, completion gate and persisted state.
- `.github/workflows/wic-24h-tools-revenue-cycle.yml`: daily at 01:23 UTC; existing business tools/revenue cycle and GitHub Pages publishing.
- Kestra isolated Render service `srv-dbm0obp42hec73a57d3g`: installation evidence PASS, operational runtime FAIL due to repeated 512Mi OOM kills. Not a source of durable data.

## Execution ownership
1. Scheduled activation and parallel jobs: reuse existing GitHub Actions workflows on `main` without copying their scripts.
2. Durable checkpoints: existing Git-tracked evidence/state, with conflict checks; no secrets or customer personal data in public repos.
3. Kestra: keep as installed coordinator candidate, no critical workflow depends on its uptime.
4. Excel: must use existing approved external finished product; do not claim GitHub workflow status is proof of actual Excel input-output equivalence.
5. Oracle: support ticket 261031-000191 remains HOLD; not on critical path for independent GitHub jobs.

## Verification gates and known limitations
- Workflow files and schedules VERIFIED present in `main`; **current execution success and schedule enablement NOT VERIFIED**.
- GitHub schedules are not a continuously running server; jobs can be delayed/dropped, and scheduling runs on default branch only.
- Excel end-to-end input/output and persistence NOT VERIFIED; no production customer data authorized.
- Need actual workflow-run/job evidence and Excel golden-sample comparison before PASS; do not equate a GitHub commit with completed business work.
- Keep independent lanes running when one lane is HOLD, subject to user stop and admission gates.
