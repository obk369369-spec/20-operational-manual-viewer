# WIC16 Work handoff — install only missing machines (2026-11-05)

## Owner split
- **Work:** Install and test ERPNext, Dify; reuse existing OpenRefine 3.10.0; investigate free persistent external execution host and data storage. Backstage/OpenHands only if proven necessary.
- **This chat / connected apps:** Reuse and integrate existing Kestra, GitHub Actions, Render and Deno Deploy; verify deployment logs and cross-component workflows.
- **User:** Approve login/permissions only if genuinely necessary.

## Existing assets (verified through connected apps)
- Kestra: `srv-dbm0obp42hec73a57d3g`, Render Free Docker, branch `wic16-kestra-render-isolated-install-20261105`, **already installed; do not reinstall**.
- Existing WIC runtime: `srv-dar0nu49v7es7392lim0`, main branch; **preserve**.
- Render Postgres instances: **0** (verified).
- Render Free services sleep on inactivity; **not qualified as guaranteed 24-hour host**.
- Oracle incident `261031-000191`: **HOLD pending support**. Do not retry card verification or create another account.
- Existing GitHub: `obk369369-spec/20-operational-manual-viewer`.

## Execution rules
1. Do not repeat completed product research.
2. Check the existing asset before installing anything. Do not replace or delete originals.
3. Do not create public unauthenticated admin services, expose customer data, or embed passwords in GitHub.
4. Do not enable any paid service, metered API, or paid credits.
5. Only install ERPNext/Dify after free host, durable storage, authentication, and capacity are verified. If blocked, record exact cause, not a fake PASS.
6. Verify real user workflow, restart, persisted readback, and evidence links.
7. Keep Work's installations separate from Kestra/Render configuration controlled by this chat.

## Work execution status
- Work run from this chat: **NOT STARTED** (no Work launch action available here).
- This chat Render/GitHub inspection: **DONE**.
- ERPNext/Dify: **NOT INSTALLED**.
- Free always-on durable host: **NOT SECURED**.
