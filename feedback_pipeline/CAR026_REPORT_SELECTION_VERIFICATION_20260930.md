# CAR-026 REPORT SELECTION VERIFICATION RECEIPT — 2026-09-30

Status: FAIL-CLOSED / 3-OF-3 PASS NOT YET ACHIEVED
Customer: CAR-026 장명진 / 한국섬유개발연구원 / 신사업기획팀
Research axis: 금속사 기반 무납 방사선 차폐 섬유 → 전도성 원사·직물 → 스마트/e-textile·센서
Customer master status: PARTIAL_VERIFIED / UNSENT

## Canonical publisher gate
Source: CUSTOMER_PUBLISHER_MASTER.md
Blob SHA read-back: 993de1a93ad34d2e640e0335eb0edc0f3ff547e0
Rule: only the 78 listed publishers may PASS. QY Research excluded for this customer per TOOL042 customer rule.

## Rejected prior output
- PW Consulting / pmarketresearch: NOT IN WIC PUBLISHER MASTER -> REJECT
- Maximize Market Research: NOT IN WIC PUBLISHER MASTER -> REJECT

## Current official-source verification
1. Coherent Market Insights — GLOBAL E-TEXTILES MARKET SIZE AND SHARE ANALYSIS - GROWTH TRENDS AND FORECASTS (2026-2033)
   - WIC publisher master: PASS
   - title starts Global: PASS
   - 2026 publication: PASS (02 Apr 2026)
   - official detail page: PASS
   - official full TOC publicly verified: FAIL (page exposes segmentation/scope but not complete actual TOC)
   - result: TOC_SOURCE_NOT_VERIFIED / REJECT

2. Data Bridge Market Research — Global Conductive Textile Materials Market Size, Share, and Trends Analysis Report – Industry Overview and Forecast to 2033
   - WIC publisher master: PASS
   - title starts Global: PASS
   - 2026 update: PASS (28 Jul 2026)
   - official detail page: PASS
   - official full TOC publicly verified: FAIL (Request for TOC)
   - result: TOC_SOURCE_NOT_VERIFIED / REJECT

3. Data Bridge Market Research — Global Conductive Textiles Market Size, Share, and Trends Analysis Report – Industry Overview and Forecast to 2032
   - WIC publisher master: PASS
   - title starts Global: PASS
   - 2026 update: PASS (12 May 2026)
   - official detail page: PASS
   - official full TOC publicly verified: FAIL (Request for TOC)
   - result: TOC_SOURCE_NOT_VERIFIED / REJECT

4. MarketsandMarkets — Smart Textiles Market ... - Global Forecast to 2030
   - WIC publisher master: PASS
   - title starts Global: FAIL
   - publication: 2025
   - result: TITLE_GATE_FAIL / REJECT

5. Verified Market Research — Conductive Textiles Market By ...
   - WIC publisher master: PASS
   - official full TOC: PASS
   - title starts Global: FAIL
   - result: TITLE_GATE_FAIL / REJECT

## Runtime gate receipt
LATEST_MASTER_REVISION_USED: PASS (CUSTOMER_PUBLISHER_MASTER.md blob 993de1a93ad34d2e640e0335eb0edc0f3ff547e0)
VALIDATOR_EXECUTED: PASS
SOURCE_GATE: EXECUTED
TITLE_GATE: EXECUTED
YEAR_GATE: EXECUTED
CUSTOMER_RESEARCH_AXIS_GATE: EXECUTED
TOC_GATE: EXECUTED
COMPLETE_SET_GATE: FAIL (0/3 fully compliant)
FINAL_OUTPUT_PASS: FAIL

No candidate may be presented to the customer as PASS until three reports satisfy every mandatory gate.