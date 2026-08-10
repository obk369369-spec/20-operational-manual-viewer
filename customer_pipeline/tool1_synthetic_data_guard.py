"""Tool1 regression guard for historically observed fabricated report generation.
This is a quarantine test, not a replacement UI implementation.
"""

FORBIDDEN_SIGNATURES = (
    "Market Report ${year}",
    "Industry Outlook ${year}",
    "Global ${kw} Supply Chain Report",
    "Competitive Landscape Report ${year}",
    "Technology and Application Report ${year}",
    "String(160 + i*20)",
    "${320 + i*10}만원",
    "https://www.worldic.co.kr",
)

REQUIRED_REAL_FIELDS = (
    "title",
    "publisher",
    "publication_date",
    "pages",
    "list_price",
    "supply_price",
    "report_link",
    "toc",
)


def quarantine_scan(source_text):
    hits = [sig for sig in FORBIDDEN_SIGNATURES if sig in source_text]
    return {
        "state": "FAIL" if hits else "PASS",
        "error_hash": "TOOL001_SYNTHETIC_REPORT_DATA" if hits else None,
        "hits": hits,
    }


def validate_real_report_payload(payload):
    missing = [k for k in REQUIRED_REAL_FIELDS if payload.get(k) in (None, "")]
    if missing:
        return {"state": "HOLD", "error_hash": "TOOL001_REAL_REPORT_FIELDS_MISSING", "missing": missing}
    return {"state": "PASS", "missing": []}


def run_fixtures():
    historical_v14_fragment = """
    {title:`${kw} Market Report ${year}`, link:'https://www.worldic.co.kr'}
    page: String(160 + i*20), price: `${320 + i*10}만원`
    """
    r = quarantine_scan(historical_v14_fragment)
    assert r["state"] == "FAIL"
    assert r["error_hash"] == "TOOL001_SYNTHETIC_REPORT_DATA"
    assert "https://www.worldic.co.kr" in r["hits"]

    mapper_fragment = "titleEnInput publisherInput dateInput pageInput priceInput supplyInput linkInput tocInput"
    assert quarantine_scan(mapper_fragment)["state"] == "PASS"

    real = {
        "title": "Verified Report Title",
        "publisher": "Verified Publisher",
        "publication_date": "2026-07",
        "pages": "250",
        "list_price": "$4,500",
        "supply_price": "verified",
        "report_link": "https://publisher.example/report/123",
        "toc": "1. Executive Summary",
    }
    assert validate_real_report_payload(real)["state"] == "PASS"
    bad = dict(real); bad["report_link"] = ""
    x = validate_real_report_payload(bad)
    assert x["state"] == "HOLD"
    assert "report_link" in x["missing"]

    return "PASS: 4 deterministic Tool1 quarantine fixtures"


if __name__ == "__main__":
    print(run_fixtures())
