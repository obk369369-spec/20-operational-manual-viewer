"""Bounded verified-component composition tests; never mutates production tools."""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
import tempfile
from pathlib import Path

try:
    from .wic_asset_provenance import classify
except ImportError:
    from wic_asset_provenance import classify


def _url_valid(wheel: Path, value: str) -> bool:
    sys.path.insert(0, str(wheel))
    try:
        module = importlib.import_module("validators")
        return module.url(value) is True
    finally:
        sys.path.remove(str(wheel))
        sys.modules.pop("validators", None)


def test_url_provenance_composition(wheel: Path, actual_failure_fixture: Path) -> dict:
    expected_hash = hashlib.sha256(wheel.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory() as directory:
        evidence = Path(directory) / "verified.json"
        evidence.write_text("{}", encoding="utf-8")
        base = {
            "asset_id": "URL_ARTIFACT", "path": str(wheel), "role": "official release artifact",
            "declared_state": "VERIFIED", "provenance": "official PyPI release", "version": "0.35.0",
            "expected_sha256": expected_hash, "evidence_path": str(evidence), "evidence_status": "DEPLOYED_PASS",
            "actual_execution": "PASS", "expected_actual": "MATCH", "promotion_routes": ["READY_FOR_INTEGRATION"],
        }
        normal = _url_valid(wheel, "https://files.pythonhosted.org/report.whl") and classify(base)["status"] == "VERIFIED"
        malformed = not _url_valid(wheel, "not a url")
        mismatch = classify({**base, "expected_sha256": "0" * 64})["promotion_allowed"] is False
        actual = json.loads(actual_failure_fixture.read_text(encoding="utf-8"))["candidates"][0]
        past_failure = not _url_valid(wheel, str(actual.get("link", "")))
        regression = _url_valid(wheel, "https://example.com/report") and classify(base)["status"] == "VERIFIED"
    passed = all([normal, malformed, mismatch, past_failure, regression])
    return {
        "composition_id": "VALIDATORS_URL_THEN_WIC_PROVENANCE_V1",
        "components": ["VALIDATORS_0_35_0_URL_VALIDATION", "WIC_MANIFESTED_ASSET_PROVENANCE_GATE"],
        "root": "T42-OFFICIAL-DETAIL-PAGE-PROVENANCE",
        "applicable_tools": ["TOOL042"],
        "input_contract": "URL plus downloaded artifact receipt manifest",
        "output_contract": "READY_FOR_INTEGRATION only when URL syntax and artifact provenance both pass",
        "failure_fixture": "fixtures/tool042_customer_branch_actual_kmg.json",
        "failure_fixture_sha256": hashlib.sha256(actual_failure_fixture.read_bytes()).hexdigest(),
        "normal_fixture": "official wheel receipt",
        "tests": {"normal": normal, "malformed": malformed, "provenance_mismatch": mismatch,
                  "past_actual_failure": past_failure, "regression": regression},
        "expected_actual": "MATCH" if passed else "MISMATCH", "regression": "PASS" if regression else "FAIL",
        "known_limitations": ["Does not establish publisher ownership or page semantics"],
        "ready_for_integration": passed, "status": "VERIFIED_COMPOSITION" if passed else "COMPOSITION_FAILED",
    }

def validate_official_publisher_domain(url: str, official_domains: list[str]) -> dict:
    """Fail-closed official-domain validation against an authoritative caller allowlist."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    allowed = sorted({str(x).lower().strip().rstrip(".") for x in official_domains if str(x).strip()})
    if parsed.scheme not in {"http", "https"} or not host:
        return {"status": "HOLD_INVALID_URL", "host": host, "matched_domain": None}
    matched = next((domain for domain in allowed if host == domain or host.endswith("." + domain)), None)
    return {"status": "VERIFIED_OFFICIAL_DOMAIN" if matched else "HOLD_NOT_OFFICIAL_DOMAIN", "host": host, "matched_domain": matched}

def validate_official_detail_page(url: str, official_domains: list[str], detail_markers: list[str]) -> dict:
    """Require valid URL, an allowlisted official domain, and an explicit detail-page marker."""
    from urllib.parse import parse_qs, urlparse
    domain = validate_official_publisher_domain(url, official_domains)
    if domain["status"] != "VERIFIED_OFFICIAL_DOMAIN":
        return {**domain, "detail_marker": None}
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    markers = [str(item).strip() for item in detail_markers if str(item).strip()]
    matched = next((item for item in markers if item in query or item in parsed.path), None)
    if not matched:
        return {**domain, "status": "HOLD_NOT_DETAIL_PAGE", "detail_marker": None}
    return {**domain, "status": "VERIFIED_OFFICIAL_DETAIL_PAGE", "detail_marker": matched}

def extract_webpage_text_and_toc(html: str) -> dict:
    """Extract readable Markdown and heading structure with the verified wheel pair."""
    import html2text
    import mistune

    markdown = html2text.html2text(str(html))
    ast = mistune.create_markdown(renderer="ast")(markdown)

    def walk(nodes):
        for node in nodes if isinstance(nodes, list) else []:
            if isinstance(node, dict):
                if node.get("type") == "heading":
                    yield node
                yield from walk(node.get("children", []))

    headings = list(walk(ast))
    if not markdown.strip():
        return {"status": "HOLD_EMPTY_TEXT", "text_length": 0, "heading_count": 0}
    if not headings:
        return {"status": "HOLD_NO_TOC_STRUCTURE", "text_length": len(markdown), "heading_count": 0}
    return {"status": "VERIFIED_WEBPAGE_TEXT_AND_TOC", "text_length": len(markdown), "heading_count": len(headings)}

