"""Bounded verified-component composition tests; never mutates production tools."""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
import tempfile
from pathlib import Path

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


def test_html_toc_composition(html2text_wheel: Path, mistune_wheel: Path,
                              normal_fixture: Path, failure_fixture: Path) -> dict:
    """Verify HTML extraction followed by explicit Markdown heading extraction."""
    normal_data = json.loads(normal_fixture.read_text(encoding="utf-8"))
    failure_data = json.loads(failure_fixture.read_text(encoding="utf-8"))
    sys.path[:0] = [str(html2text_wheel), str(mistune_wheel)]
    try:
        html2text = importlib.import_module("html2text")
        mistune = importlib.import_module("mistune")
        parser = mistune.create_markdown(renderer="ast")

        markdown = html2text.html2text(normal_data["html"])
        tokens = parser(markdown)
        actual = [
            {"level": token.get("attrs", {}).get("level"), "text": token.get("children", [{}])[0].get("raw", "")}
            for token in tokens if token.get("type") == "heading"
        ]
        failure_markdown = html2text.html2text(failure_data["html"])
        failure_headings = [token for token in parser(failure_markdown) if token.get("type") == "heading"]

        html_parent_regression = all(value in markdown for value in normal_data["expected_text"])
        mistune_parent_regression = [item["level"] for item in actual] == normal_data["expected_levels"]
        normal_match = actual == normal_data["expected_headings"]
        failure_blocked = failure_headings == []
        composition_regression = normal_match and failure_blocked
    finally:
        for name in ("html2text", "mistune"):
            sys.modules.pop(name, None)
        for value in (str(html2text_wheel), str(mistune_wheel)):
            if value in sys.path:
                sys.path.remove(value)

    tests = {
        "functional": normal_match,
        "expected_actual": normal_match,
        "normal_fixture": normal_match,
        "failure_fixture": failure_blocked,
        "html2text_parent_regression": html_parent_regression,
        "mistune_parent_regression": mistune_parent_regression,
        "composition_regression": composition_regression,
    }
    passed = all(tests.values())
    return {
        "composition_id": "HTML2TEXT_THEN_MISTUNE_TOC_V1",
        "components": [
            "HTML2TEXT_2025_4_15_WEBPAGE_TEXT_EXTRACTION",
            "MISTUNE_3_3_4_TOC_STRUCTURE_EXTRACTION",
        ],
        "root": "T42-WEBPAGE-TO-TOC-STRUCTURE",
        "applicable_tools": ["TOOL042"],
        "input_contract": "HTML document with explicit heading elements",
        "output_contract": "Ordered heading text and source heading levels; no inferred headings",
        "normal_fixture": str(normal_fixture.as_posix()),
        "failure_fixture": str(failure_fixture.as_posix()),
        "normal_fixture_sha256": hashlib.sha256(normal_fixture.read_bytes()).hexdigest(),
        "failure_fixture_sha256": hashlib.sha256(failure_fixture.read_bytes()).hexdigest(),
        "expected": normal_data["expected_headings"],
        "actual": actual,
        "tests": tests,
        "expected_actual": "MATCH" if normal_match else "MISMATCH",
        "regression": "PASS" if composition_regression else "FAIL",
        "known_limitations": [
            "Only explicit HTML heading elements are preserved",
            "Does not infer numbering or publisher-specific hierarchy from plain text",
        ],
        "ready_for_integration": passed,
        "status": "VERIFIED_COMPOSITION" if passed else "COMPOSITION_FAILED",
    }
