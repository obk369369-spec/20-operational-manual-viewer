# Kestra Render Free runtime incident — 2026-11-05

## Observed via Render connector
- Service `srv-dbm0obp42hec73a57d3g`, plan `free`, memory limit `512Mi`, autoDeploy `no`.
- Deploy `dep-dbm2frlbedkc73b1d600` marked `live`, but that is deployment success only.
- Render events include multiple `server_failed` entries with `reason.oomKilled.memoryLimit = 512Mi`, e.g. 2026-11-05 07:05:07, 07:08:16, 07:12:48, 07:16:39, 07:26:10 and 07:29:55 UTC.
- Logs show Kestra 2.0.9 startup, JVM max memory ~247MB, and additional plugin installations.
- Existing username/password environment variable names alone do not prove HTTP authentication enforcement.
- No durable database or successful business-flow run/restart/readback evidence.

## Status
- Image build/deployment: PASS.
- Runtime stability: FAIL (repeated out-of-memory kills).
- Security: NOT VERIFIED.
- Permanent storage and 24/7 operation: NOT AVAILABLE on current Render Free setup.
- Business integration: NOT EXECUTED.

## Required next action
- Do not publish customer data or connect production business flows to this runtime.
- Preserve existing service and repo; avoid repeated blind redeploys.
- Resume operational integration only on a host with sufficient memory, authentication, and durable storage, then run real flow and persistence readback tests.
- Oracle signup incident `261031-000191` stays HOLD pending support; no payment retries.
