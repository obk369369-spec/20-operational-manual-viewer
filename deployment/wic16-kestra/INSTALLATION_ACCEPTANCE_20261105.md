# Kestra installation acceptance — 2026-11-05

## Verified: installed (PASS)
- Official Kestra Docker image via `deployment/wic16-kestra/Dockerfile`.
- Render service: `srv-dbm0obp42hec73a57d3g`, branch `wic16-kestra-render-isolated-install-20261105`.
- Deployment: `dep-dbm2frlbedkc73b1d600` reported `live`, finished 2026-11-05 06:55:56 UTC.
- Runtime logs: Kestra 2.0.9 started; HTTP service detected on port 8080.
- Existing Render and GitHub assets preserved.

## Not verified (NOT PASS)
- HTTP authentication enforcement: username/password environment variables saved, but no confirmed unauthorized HTTP 401/login challenge; migration log reported no existing basic-auth setting (not a conclusive auth test).
- Durable storage and successful readback after restart.
- 24-hour availability (Render Free spins down).
- Successful real business flow / Excel integration.

## Decision
- Installation evidence accepted; do not reinstall Kestra.
- Render Free is an isolated test runtime, not approved for customer data or 24/7 production.
- Next: verify authentication, then perform a harmless end-to-end test flow with existing GitHub/Render assets; preserve results separately from production qualification.
- Oracle incident 261031-000191 remains on HOLD; no re-registration or payment.
