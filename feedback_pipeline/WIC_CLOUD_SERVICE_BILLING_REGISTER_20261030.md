# WIC cloud service billing / payment-method register

Updated: 2026-10-31. User-reported account screen, not independently audited bank charges.

## Deno Deploy
- Organization: obk369369-spec
- Console: https://console.deno.com/obk369369-spec/~/billing
- Subscription: Free Plan ($0/month), user-confirmed 2026-10-30.
- Payment method: Mastercard **registered** (do not store card digits, expiry, billing address, or email in this repository).
- Billing Details > Edit > Payment Method displayed Update Payment Method; no delete option visible in that screen.
- User wishes to keep free tier and prohibit paid upgrade or metered/credit-based spending without explicit permission.
- Existing deployed apps: 33 shown in dashboard (user report); this does not prove 24/7 persistent VM operation.
- Historical event: on 2025-12-03 Free Plan Memory Time quota alerts 75%, 90%, then exceeded; applications temporarily suspended. Gmail subjects: 'Usage alert for obk369369-spec', 'Usage limit exceeded - obk369369-spec suspended'.
- Why card was originally registered: UNKNOWN. May relate to quota or service setup, but no direct evidence; do not claim certainty.
- No verified card charge or paid subscription as of this entry; this is NOT evidence that past charges never occurred.

## Oracle Cloud Infrastructure
- Official signup: https://signup.oraclecloud.com/
- Account status (2026-10-31): email verification and payment-card verification were performed; temporary SGD 1.38 authorization and reversal reported by user. This is NOT proof of a successfully created account. Account activation email absent, cloud account login unavailable, retry demanded card verification again. Account creation FAILED / Oracle Help ticket OPEN. No VM deployed.
- Intended tier: Free Tier / Always Free only. Do not upgrade to Pay As You Go or select paid resources.
- Signup may request a card for verification; no card number, expiry, CVC, personal address, or credentials should ever be stored in GitHub.
- Server provisioned: NO confirmed VM ID or running remote workload.
- Oracle Help official signup-issue ticket: 261031-000191, submitted 2026-10-31; support explicitly asks to wait for email and avoid duplicate tickets or contacting other teams. Next review: 2026-11-02; no promised response deadline. Do not repeat card verification, upgrade, or open duplicate tickets without new evidence.
- Do not store cardholder name, full card details, addresses, or support-chat private identifiers beyond ticket number in repository.

## Operating rules
1. Never record card numbers (including last four), card expiry, CVC, billing addresses, passwords, or tokens in this public repository.
2. Maintain statuses separately: card registered, free plan verified, paid plan activated, charge verified, account opened, VM deployed.
3. Any new service/card registration must be recorded here with date, provider, status, and verification source, excluding sensitive details.
4. No paid upgrade, credit-based execution, or automatic spending without explicit user authorization.
5. User should verify real charges through provider invoices and card issuer statements, not infer them from card registration alone.

## WIC16 external runtime and replacement review (2026-10-31)
- Objective: PC-off 24-hour external execution, prioritize ready-made external software, no internal reimplementation, reuse canonical ROOT ledger/queue/gates and prior evidence. A VM alone does NOT implement automatic software discovery, vetting, import, licensing, deployment, or runtime integration.
- Existing GitHub evidence: feedback_pipeline/tool044_multi_gate_adapters.json lists GitHub Actions, CircleCI Cloud and Deno Deploy as ACTUAL_RUN_PASS for scoped jobs; NOT proof of permanent 24-hour Windmill host. Prior 2026-10-12 audit says Deno had build/deploy evidence but no verified independent scheduled watchdog; scheduled GitHub Actions can be delayed or skipped. Keep unresolved ROOTs BLOCKED rather than marking PASS.
- Existing Deno Deploy Free with Mastercard registered and user-reported 33 deployed apps; 2025-12 quota exceeded and apps suspended. NOT a proven unrestricted always-on VM.
- Alternatives to investigate and test (NOT DEPLOYED): Google Cloud e2-micro always-free VM (official free tier, but too small for full Windmill stack: Windmill states 2 vCPU, 4GB RAM, 20GB disk minimum); Cloudflare Workers Cron for scheduled short jobs (NOT general-purpose Docker VM); existing GitHub Actions + CircleCI + Deno as a no-VM distributed execution layer; other 24h VM/container offers require current billing, inactivity, memory, cost, and persistence checks.
- Official references: https://cloud.google.com/products/compute ; https://developers.cloudflare.com/workers/configuration/cron-triggers/ ; https://www.windmill.dev/platform/self-host ; https://www.oracle.com/kr/cloud/free/faq/
- Strict gates: do not activate paid tier, add another card, incur metered fees, claim 24h PASS, install Windmill, or claim external product acquisition without actual run and read-back evidence. User expects root-cause grouped parallel remediation and minimal user intervention.
- Status: GitHub record update is documentation only; no alternative VM, Windmill instance, or automated software importer was deployed by this change.
