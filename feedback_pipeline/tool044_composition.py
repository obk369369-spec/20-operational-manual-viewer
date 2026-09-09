"""Bounded verified-component composition tests; never mutates production tools."""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
import tempfile
import time
from pathlib import Path

from wic_asset_provenance import classify


def lookup_verified_composition(pool_path: Path, demand: dict) -> dict:
    """Return an exact verified composition without rebuilding or external lookup."""
    started = time.perf_counter()
    required = set(demand.get("atomic_capabilities", []))
    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    matches = []
    for composition in pool.get("compositions", []):
        if composition.get("status") != "VERIFIED_COMPOSITION" or not composition.get("ready_for_integration"):
            continue
        provided = set(composition.get("atomic_capabilities", []))
        if provided == required:
            matches.append(composition)
    selected = matches[0] if len(matches) == 1 else None
    return {
        "demand_id": demand.get("demand_id"),
        "required_capabilities": sorted(required),
        "result": "VERIFIED_COMPOSITION_DIRECT_REUSE" if selected else "NO_EXACT_VERIFIED_COMPOSITION",
        "selected_composition": selected.get("composition_id") if selected else None,
        "warehouse_hits": 1 if selected else 0,
        "parent_component_searches": 0,
        "external_queries": 0,
        "compositions_created": 0,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
    }


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
        "atomic_capabilities": ["URL_VALIDATION", "PROVENANCE_VALIDATION"],
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
        "atomic_capabilities": ["WEBPAGE_TEXT_EXTRACTION", "TOC_STRUCTURE_EXTRACTION"],
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


def test_provenance_html_toc_growth(html2text_wheel: Path, mistune_wheel: Path,
                                    normal_fixture: Path, heading_failure_fixture: Path) -> dict:
    """Grow verified HTML->TOC with the verified manifested provenance gate."""
    with tempfile.TemporaryDirectory() as directory:
        sandbox = Path(directory)
        artifact = sandbox / "publisher-detail.html"
        artifact.write_text(
            json.loads(normal_fixture.read_text(encoding="utf-8"))["html"], encoding="utf-8"
        )
        evidence = sandbox / "publisher-detail-evidence.json"
        evidence.write_text("{}", encoding="utf-8")
        actual_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
        manifest = {
            "asset_id": "TOOL042_OFFICIAL_DETAIL_HTML",
            "path": str(artifact),
            "role": "official detail page HTML",
            "declared_state": "VERIFIED",
            "provenance": "bounded TOOL042 official detail-page fixture",
            "version": "fixture-v1",
            "expected_sha256": actual_hash,
            "evidence_path": str(evidence),
            "evidence_status": "DEPLOYED_PASS",
            "actual_execution": "PASS",
            "expected_actual": "MATCH",
            "promotion_routes": ["READY_FOR_INTEGRATION"],
        }
        provenance_normal = classify(manifest)
        provenance_failure = classify({**manifest, "expected_sha256": "0" * 64})
        ab = test_html_toc_composition(
            html2text_wheel, mistune_wheel, normal_fixture, heading_failure_fixture
        )
        provenance_parent_regression = (
            provenance_normal["status"] == "VERIFIED"
            and provenance_failure["promotion_allowed"] is False
        )
        ab_parent_regression = ab["status"] == "VERIFIED_COMPOSITION" and all(ab["tests"].values())
        normal_match = provenance_normal["status"] == "VERIFIED" and ab["expected_actual"] == "MATCH"
        failure_blocked = (
            provenance_failure["promotion_allowed"] is False
            and provenance_failure["status"] != "VERIFIED"
        )
        abc_regression = normal_match and failure_blocked and provenance_parent_regression and ab_parent_regression

    tests = {
        "functional": normal_match,
        "expected_actual": normal_match,
        "normal_fixture": normal_match,
        "failure_fixture": failure_blocked,
        "ab_parent_regression": ab_parent_regression,
        "c_parent_regression": provenance_parent_regression,
        "abc_regression": abc_regression,
    }
    passed = all(tests.values())
    return {
        "composition_id": "PROVENANCE_THEN_HTML2TEXT_THEN_MISTUNE_TOC_V1",
        "parents": ["HTML2TEXT_THEN_MISTUNE_TOC_V1", "WIC_MANIFESTED_ASSET_PROVENANCE_GATE"],
        "atomic_components": [
            "HTML2TEXT_2025_4_15_WEBPAGE_TEXT_EXTRACTION",
            "MISTUNE_3_3_4_TOC_STRUCTURE_EXTRACTION",
            "WIC_MANIFESTED_ASSET_PROVENANCE_GATE",
        ],
        "atomic_capabilities": [
            "PROVENANCE_VALIDATION", "WEBPAGE_TEXT_EXTRACTION", "TOC_STRUCTURE_EXTRACTION"
        ],
        "root": "T42-VERIFIED-DETAIL-PAGE-TO-TOC",
        "applicable_tools": ["TOOL042"],
        "input_contract": "Manifested HTML artifact with verified hash and explicit heading elements",
        "output_contract": "Ordered TOC headings only after provenance verification passes",
        "normal_fixture": str(normal_fixture.as_posix()),
        "failure_fixture": "same HTML artifact with mismatched manifested SHA-256",
        "expected": {"provenance": "VERIFIED", "html_toc": "MATCH"},
        "actual": {"provenance": provenance_normal["status"], "html_toc": ab["expected_actual"]},
        "lineage": {
            "ab": "HTML2TEXT_THEN_MISTUNE_TOC_V1",
            "c": "WIC_MANIFESTED_ASSET_PROVENANCE_GATE",
            "ab_status": ab["status"],
            "c_status": provenance_normal["status"],
        },
        "tests": tests,
        "expected_actual": "MATCH" if normal_match else "MISMATCH",
        "regression": "PASS" if abc_regression else "FAIL",
        "ready_for_integration": passed,
        "status": "VERIFIED_COMPOSITION" if passed else "COMPOSITION_FAILED",
    }
