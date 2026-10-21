# WIC external workspace cutover acceptance — 2026-10-21

## Non-negotiable outcome
Finish the actual migration within the current Work session; from 2026-10-22 use the external platform's own independently running workspace, with durable evidence. A GitHub commit or a scheduled YAML file alone is NOT cutover.

## Existing immutable boundaries
- Keep `main`, STOP, START_BLOCKED=TRUE, PASS_LOCK, existing evidence, Queue and six Job Packs intact.
- Preserve exactly two official inputs: RULES and COMPONENTS; both feed one shared execution/evidence route.
- Do not rescan the historical ~3,200 items or re-run prior PASS.
- ChatGPT/Codex/Work recurring schedulers are disabled/not allowed as operational owners.
- No unapproved paid hosting, credential creation, customer communication or production mutations.

## Execute in parallel, not serially
A. Reuse existing Render/Kestra/Node-RED/FlowWink infrastructure where authenticated live endpoints exist; verify actual current status rather than old PASS.
B. Obtain and connect external ready-made platforms (Kestra, Windmill, Activepieces, n8n, Temporal, Airflow, Prefect, Dagster) via official packages, plugins or images; only deploy to an accessible free remote host. A candidate URL is not a product installation.
C. Enable native external scheduling and persistent evidence. Existing Kestra flow: `external_workspace/kestra/wic_external_socket_discovery_hourly.yml`. It is STAGED, NOT DEPLOYED.
D. Verify alternate workers and failover with persisted checkpoint and independent validator; do not equate retry settings with observed recovery.
E. Transfer accessible authentic WIC jobs from bundles A–F; compare against expected real output. Block inaccessible sources individually without halting independent lanes.

## Cutover evidence — all required before PASS
1. Actual remote external platform URL, runtime version, deployment/instance ID and timestamp.
2. External-native schedule ID and next execution time; actual triggered execution ID and full logs.
3. Verified persisted discovery output (at least one authentic upstream source), hashes, and independently checked provenance.
4. Two independent authentic WIC jobs (not synthetic markers) with job IDs, input/output hashes and validators.
5. Parallel overlap observed; worker interruption and automatic takeover/restart from persisted checkpoint observed.
6. Proof no ChatGPT/Codex scheduler is required for execution; no unintended costs or unauthorized customer actions.
7. Read-back of central evidence and per-job PASS/FAIL/HOLD; keep production blocked until authorization.

## Current verified boundary
- 8 products inventoried, not installed: `external_workspace/WIC_EXTERNAL_SOCKET_CANDIDATES_20261021.json`.
- Native Kestra hourly schedule YAML committed and remotely read back, but NOT deployed or run.
- Actual external runtime, schedule execution, recovery, and authentic WIC migration evidence: NOT YET PRESENT.
- Do not assert 2026-10-22 readiness without items 1–7. Missing external host endpoint or authenticated deployment access is a genuine blocker, not a reason to loop over research.

## Final report format
Destination | Actual change | External URL/run ID/log/hash | independent read-back | PASS/FAIL/HOLD. Separate staged files from running services and actual business migrations.
