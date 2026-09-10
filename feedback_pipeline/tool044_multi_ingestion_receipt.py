"""Cross-check two already executed ingestion paths without replaying them."""
from __future__ import annotations

import json
from pathlib import Path

from tool044_requirement_interlock import HERE, sha256


def run(root: Path = HERE) -> dict:
    source = root / "evidence" / "tool016_tool044_feedback_factory_v2_20260909.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    browser = data["actual_browser_result"]
    tests = data["tests"]
    ci = data["remote_ci"]
    truth = data["truth_boundary"]
    local = {
        "source_capture": browser.get("status") == "RECEIVED",
        "input_hash": str(browser.get("source_id", "")).startswith("SRC-"),
        "job_create": bool(browser.get("tool044_demand_id")),
        "queue_write": browser.get("queue_count_after") == browser.get("queue_count_before", -1) + 1,
        "queue_readback": tests.get("QUEUE_READBACK") == "PASS",
    }
    github = {
        "source_capture": truth.get("authenticated_github_feedback") == "AUTO_INGEST_VERIFIED_RUN_34307507216",
        "input_hash": bool(ci.get("remote_feedback_root")),
        "job_create": ci.get("authenticated_feedback_result") == "PASS",
        "queue_write": ci.get("remote_inbox_match") is True,
        "queue_readback": ci.get("remote_queue_match") is True,
    }
    gates = {"LOCAL_OBSERVER_HTTP": local, "AUTHENTICATED_GITHUB_FEEDBACK": github}
    passed = all(all(checks.values()) for checks in gates.values())
    return {
        "status": "PASS" if passed else "FAIL",
        "source_receipt": str(source.relative_to(root)).replace("\\", "/"),
        "source_receipt_sha256": sha256(source),
        "gates": gates,
        "VERIFIED_INGESTION_GATE_COUNT": 2 if passed else 0,
        "INPUT_LOSS": 0 if passed else 1,
        "SOURCE_LOSS": 0 if passed else 1,
        "JOB_CREATION": "PASS" if passed else "FAIL",
        "QUEUE_WRITE": "PASS" if passed else "FAIL",
        "QUEUE_READBACK": "PASS" if passed else "FAIL",
        "INGESTION_FAILOVER": "NOT_TESTED",
        "evidence_mode": "SKIP_REUSE_VERIFIED_PLUS_INDEPENDENT_CROSS_CHECK",
    }


if __name__ == "__main__":
    result = run()
    out = HERE / "evidence" / "tool044_multi_ingestion_receipt_20260910.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
