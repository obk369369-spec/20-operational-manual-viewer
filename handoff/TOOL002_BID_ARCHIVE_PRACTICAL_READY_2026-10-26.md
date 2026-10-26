# CENTRAL HANDOFF — TOOL002 Bid Archive / Practical Readiness — 2026-10-26

## User request
Analyze the complete historical bid archive and one-year bid-tool conversation records, prepare the user to enter actual bidding work immediately, create a beginner-ready manual, update all important rules to GitHub, and identify existing external automation tools that are more practical than rebuilding equivalent features in chat/Work.

## Evidence surveyed
### User archive
- 입찰.zip
- 220 actual files / approx. 173.4MB
- KISTI 114
- SME-status 40
- BidQ notice lists 16
- NaraJangter 12
- ETRI 8
- KEPCO procurement 5
- multiple other procurement systems
- historical KISTI winner/upper/lower result folders
- KISTI post-award inspection/payment records
- old participant registration, SME confirmation and institution registration materials
- sensitive credential/tax/certificate originals

### Historical conversation/library
Recovered 2번 입찰 tool records show evolution from:
static/manual calculation
-> browser program
-> classification + calculation + institution accumulation
-> Work/GitHub PASS evidence
-> observer concept

Do not restart from March 2026.

### Existing canonical product evidence
Reuse TOOL002 PASS_LOCKED evidence and current canonical repository.
Do not rebuild or re-run closed large-XLSX proof without new failure/change evidence.

## New canonical docs in TOOL002 repo
- docs/BID_ARCHIVE_AUDIT_20261026.md
- docs/BID_PRACTICAL_MANUAL_20261026.md
- docs/TOOL002_OPERATING_RULES_20261026.md
- docs/EXTERNAL_BID_AUTOMATION_20261026.md

## Critical findings
1. Legacy KISTI ebid material through 2024 is historical, not the current primary route.
2. Historical KISTI winner/upper/lower records remain highly valuable for analysis.
3. KISTI historical 88% examples must NOT become a universal rule.
4. Example B2017-000667-00 proves final threshold can differ from base*88% because final expected price may derive from multiple preliminary prices.
5. User archive contains sensitive credentials/tax/certificate documents; these must never be committed to GitHub.
6. Current practical official monitoring should prioritize G2B/NaraJangter.
7. Mature external services (Info21C/BidQ) already provide generic customized notice alerts, mobile push/Kakao, document/calendar and analysis features.
8. Do not waste Work credits rebuilding generic alert/search functions unless WIC-specific gaps justify it.

## Current practical architecture
G2B / external alert service
-> relevant notice
-> TOOL002 WIC relevance + exact notice extraction
-> publisher/supply-cost branch
-> notice-specific bid calculation
-> document checklist
-> official final submit
-> receipt/opening/result
-> institution/history accumulation

## Small observer
Observer remains NOT EVIDENCE-PASSED.
When implemented, prefer G2B official OpenAPI.
Observer scope only:
- NEW
- CHANGED
- deadline
- WIC relevance first screen
- institution accumulation
- handoff to TOOL002

No final bid submit, no auth bypass, no duplicated calculation core.

## Beginner practical manual rule
Exact current notice/attachments are authoritative.
AUTO / MANUAL_REQUIRED / FINAL-SUBMIT must remain separated.
Final irreversible submit remains user-controlled.

## Restart point
Do not redesign TOOL002.
Do not reprocess historical archive unless a targeted question needs a specific source.
For the next actual KISTI notice:
1. search current official notice
2. save notice+attachments
3. extract eligibility/deadline/submission/numeric rules
4. check publisher supply/cost
5. run TOOL002
6. self-audit
7. official submit
8. preserve receipt
9. record opening/result

## Security
Never place passwords, certificates, certificate request numbers, raw tax/insurance/employment documents, raw account/login data or sensitive identifiers in GitHub.

Status:
ARCHIVE_AUDITED
PRACTICAL_MANUAL_READY
OPERATING_RULES_UPDATED
EXTERNAL_TOOLS_EVALUATED
TOOL002_CORE_PASS_LOCK_REUSED
OBSERVER_NOT_YET_PASS
