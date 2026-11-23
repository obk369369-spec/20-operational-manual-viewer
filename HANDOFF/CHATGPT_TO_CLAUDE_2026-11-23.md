# TOOL002 nationwide procurement coverage — research and implementation handoff (2026-11-23)

## Status
RESEARCH_PARTIAL / IMPLEMENTATION_NOT_STARTED / NO_LIVE_E2E_PASS. This is a task handoff, not a duplicate operating-rule master. Follow WIC_GLOBAL_OPERATING_RULES.md and the TOOL002 canonical repository. No credentials or customer private data.

## User objective
Do not limit discovery by institution or procurement website. Cover all South Korean research institutes and other public buyers whenever WIC could legitimately bid for market intelligence reports, overseas technical publications, databases, electronic resources, books, subscriptions, research data or legally eligible related services. Institution inclusion is broad; bidding eligibility is strictly notice-specific. User should be an observer, not a repetitive form-filler.

## Public source evidence (2026-11-23 research)
- KRICT proprietary small-quotation portal: https://www.krict.re.kr/bidbuy/bid/pblanc/list — user-provided tender 20261119-024, Helium Market Size & Share Analysis (2026–2031), PDF, base 6,555,000 KRW incl VAT, deadline 2026-11-25 10:00 KST; original notice/attachments must govern.
- G2B public tender R26BK01834463: Korea Customs Service, overseas customs authority database purchase, deadline 2026-11-24 10:00 per https://bid24.kr/b/R26BK01834463 ; qualification and status HOLD pending original.
- G2B R26BK01820724: Korea Customs Service, international raw-material market-information database purchase, deadline 2026-11-23 10:00 per https://bid24.kr/b/R26BK01820724 ; already deadline, not an active opportunity.
- G2B R26BK01811494: SEMAS, overseas online platform trend-analysis service, deadline 2026-11-20 per https://nara.salusai.kr/notice/740673 ; services may require actual research delivery and credentials, not automatically eligible.
- Multi-source index lists G2B, D2B, KEPCO SRM, LH, S2B, KR, K-water, KOGAS, KORAIL, KEC, KHNP: https://g2b.dima.tools/search . Aggregators are discovery aids, never official authority.
- KRICT G2B example listing https://narais.com/agency/7ZWc6rWt7ZmU7ZWZ7Jew6rWs7JuQ ; not all equipment/service tenders are WIC-fit.

## Tender families to discover and classify
A. Single overseas market/industry/technology research report, PDF/book/CD.
B. Annual/multi-year market intelligence database subscriptions and renewals.
C. Online research platform/site license and institutional access.
D. E-book, specialist books, overseas publications, journals, serials and bundled research collections.
E. Standards, patents, statistics, commodity prices, customs/trade data and commercial data licensing when WIC has legitimate resale/distribution rights.
F. Customized research, literature review, market study, technology trend research and translation ONLY if WIC can deliver the required service and meet credentials; otherwise MANUAL_REQUIRED/EXCLUDE.
G. Framework/unit-price contracts, multiple-item lots, small quotation, single-source negotiation, general/restricted competition, price-only, threshold/eligibility examination, proposal/negotiated, two-stage/technical-price, rebid, canceled/amended.
H. Requests for quotation/market research/pre-announcements that are leads, not yet live bid invitations.

## Source coverage design
- G2B official API/current portal, including research institutions, national labs, government, public enterprises, local government, universities, university-industry foundations, libraries and public-funded bodies.
- Institution-operated procurement portals and their RFQ/quotation pages (KRICT is a concrete example); include KISTI current procurement route.
- Other independent procurement networks as relevant: D2B, KEPCO SRM, LH, S2B, K-water, KOGAS, KORAIL, KR, KEC, KHNP and new sites discovered by institution registry. Verify each official source and availability; no claim of universal coverage without source-by-source proof.
- Discover institutions continuously from verified government/public institution registries and official tender issuer names; don't hardcode an exclusive institution whitelist.
- Aggregators are secondary leads only; always follow official notice and attachments.

## Required pipeline
DISCOVER -> SOURCE_LINK -> ORIGINAL_NOTICE_AND_ATTACHMENTS -> AMENDMENT_CHAIN -> DEDUPE -> WIC_RELEVANCE -> LEGAL_ELIGIBILITY -> SUPPLY_RIGHTS/FEASIBILITY -> PRICING_METHOD -> COST_SEPARATION -> DOCUMENT_MATRIX -> DEADLINE_ALERT -> USER_APPROVAL -> OFFICIAL_FINAL_SUBMIT -> RECEIPT -> AWARD/RESULT -> CONTRACT/DELIVERY/INSPECTION/PAYMENT -> EVIDENCE.

Every record stores source, issuer, bid ID, amendment version, item(s), due date, route, status, procurement method, qualification, document list, publisher/license constraints, and immutable raw evidence. Unknowns stay HOLD, never inferred.

## Document burden automation verification
For each document requirement, label: AUTO_RETRIEVE (public source), AUTO_DRAFT (from verified business data), AUTO_VALIDATE (expiry/format/required fields), USER_AUTH_REQUIRED (official portal login, certificate issuance), LEGAL_ATTESTATION_REQUIRED (conflict-of-interest etc), or MANUAL_REQUIRED. Automate safe repeatable checks, PDFs, source highlighting, file naming, reuse of current non-sensitive templates, mismatch detection and deadline warnings. Do not auto-answer legal declarations, bypass authentication, issue sensitive certificates without authorization, or perform irreversible submission. Store confidential docs only in approved secure storage, not GitHub.

## Development / audit instructions
Claude Code: compare latest local/unpushed branches with existing TOOL002 PASS_LOCKED core and preserve proven modules. Google AI: independent gap analysis and audit; ChatGPT: public source research, original-vs-output comparison and factual HOLD list. Reuse official G2B API/MCP and tested open components first, no duplicate engine. Add site-specific adapters, not a universal bidding formula. Test real samples per source and each tender family, include cancellation, amendments, late notices, restricted eligibility, VAT, multiple lots, and expired certificates. PASS requires actual inputs, output, expected=actual, regression and evidence; no blanket claim of 'all sites/all bids' until coverage matrix proves it.

## Urgent split
KRICT tender 20261119-024 deadline 2026-11-25 10:00 KST. Prepare official submission separately and in parallel. No bid has been submitted by this handoff. User controls bid amount, legal attestation, authentication and final submission.

## Next outputs
1. Coverage matrix by source and institution with verified working adapters.
2. Actual currently open WIC-relevant notices, source URL, exact deadline and eligibility HOLD/PASS/FAIL; no invented coverage counts.
3. Per-notice document automation matrix and manual burden estimate based on measured steps, not guessed savings.
4. Claude change diff vs existing TOOL002, tests and evidence links, Google AI audit.
