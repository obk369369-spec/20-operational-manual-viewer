"""Run the preserved real WIC customer input through the already-built platform.

This is an execution adapter, not a second controller.  Closed handoff/waste
receipts are consumed by hash; the existing registry, Large Factory receipts,
universal socket, and fail-closed gate are then exercised with the real record.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from cross_tool_customer_flow import run_actual_flow

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORKSPACE = ROOT.parent
CONTROLLER = ROOT / "CONTROL_TOWER" / "controller"
sys.path.insert(0, str(CONTROLLER))

from github_runtime_cycle import validate_contract  # noqa: E402
from universal_enforcement import verdict  # noqa: E402

INPUT = HERE / "fixtures" / "cross_tool_actual_kimtaeho_20260907.json"
OUTPUT = HERE / "evidence" / "WIC_FINAL_PLATFORM_BUSINESS_OUTPUT_20261006.json"
EVIDENCE = HERE / "evidence" / "WIC_FINAL_PLATFORM_LANE_A_20261006.json"
HANDOFF_EVIDENCE = WORKSPACE / "_wic_final_batch" / "feedback_pipeline" / "evidence" / "work_gate_chain_e2e_20261006.json"
REGISTRY = CONTROLLER / "component_registry.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_digest(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def main() -> None:
    # Handoff and Waste Gate are immutable, previously closed inputs.
    handoff = json.loads(HANDOFF_EVIDENCE.read_text(encoding="utf-8"))
    require(handoff.get("pass") is True, "HANDOFF_PASS_LOCK_MISSING")
    require(handoff.get("positive", {}).get("decision") == "WORK_GATE_CHAIN_PASS", "HANDOFF_CHAIN_FAILED")
    require(handoff.get("closure_reserve") == "PASS", "CLOSURE_RESERVE_FAILED")
    waste = handoff.get("waste_w1_w8", {})
    require(len(waste) == 8 and all(row.get("allowed") is False for row in waste.values()), "WASTE_GATE_INCOMPLETE")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    components = {item["id"]: item for item in registry["components"]}
    socket = components["WIC_ACTUAL_CUSTOMER_UNIVERSAL_SOCKET"]
    require(socket["status"] == "VERIFIED_REUSE" and (ROOT / socket["path"]).is_file(), "UNIVERSAL_SOCKET_MISSING")

    contracts = {item["id"]: item for item in registry["execution_contracts"]}
    large_factory = validate_contract(contracts["LARGE_FACTORY_ACTUAL_EXECUTION"])
    tool044 = validate_contract(contracts["FACTORY_DISCOVERY_AND_PROMOTION"])
    require(large_factory["status"] == "PASS", "LARGE_FACTORY_CONTRACT_FAILED")
    require(tool044["status"] == "PASS", "TOOL044_PROMOTION_CONTRACT_FAILED")

    actual = json.loads(INPUT.read_text(encoding="utf-8"))
    positive = run_actual_flow(actual, WORKSPACE / "41-wic-email-collection-master", WORKSPACE / "repo42")
    require(positive["status"] == "CROSS_TOOL_INTEGRATION_PASS", "ACTUAL_EXECUTION_FAILED")

    bad = json.loads(json.dumps(actual, ensure_ascii=False))
    bad["history"]["contact_history_verified"] = False
    negative = run_actual_flow(bad, WORKSPACE / "41-wic-email-collection-master", WORKSPACE / "repo42")
    require(negative.get("first_blocker") == "TOOL007_HANDOFF_REJECTED", "NEGATIVE_OUTPUT_NOT_BLOCKED")

    failure = run_actual_flow(actual, WORKSPACE / "41-wic-email-collection-master", WORKSPACE / "__missing_tool42_runtime__")
    require(failure.get("first_blocker") == "TOOL042_RUNTIME_ERROR", "FAILURE_NOT_ISOLATED")
    recovery = run_actual_flow(actual, WORKSPACE / "41-wic-email-collection-master", WORKSPACE / "repo42")
    require(json_digest(recovery) == json_digest(positive), "RECOVERY_NOT_DETERMINISTIC")

    gate_receipt = {
        "status": "VALIDATED", "total": 4, "checked": 4, "skipped": 0,
        "unresolved": 0, "validation_pass": True,
        "evidence_ref": "customer_pipeline/evidence/WIC_FINAL_PLATFORM_LANE_A_20261006.json",
        "readback_pass": True,
    }
    gate = {
        "positive": verdict(gate_receipt),
        "missing_evidence": verdict({**gate_receipt, "evidence_ref": "", "readback_pass": False}),
        "validation_failure": verdict({**gate_receipt, "validation_pass": False}),
    }
    require(gate == {"positive": "PASS", "missing_evidence": "HOLD", "validation_failure": "FAIL"}, "GLOBAL_HARD_GATE_FAILED")

    output = {
        "schema": "wic.final.platform.business_output.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "actual_input": str(INPUT.relative_to(ROOT)).replace("\\", "/"),
        "actual_input_sha256": digest(INPUT),
        "customer": positive["tool41_output"],
        "contact_decision": positive["tool7_output"],
        "recommendation_decision": positive["tool42_output"],
        "external_send_executed": False,
        "external_customer_action": "PENDING_EXTERNAL",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    require(json.loads(OUTPUT.read_text(encoding="utf-8")) == output, "BUSINESS_OUTPUT_READBACK_FAILED")

    evidence = {
        "schema": "wic.final.platform.lane_a.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": "WIC-FINAL-PLATFORM-LANE-A-20261006",
        "path": ["HANDOFF_PASS_LOCK", "WASTE_DEDUP_GATE", "REGISTRY", "LARGE_FACTORY", "UNIVERSAL_SOCKET", "TOOL044_PROMOTION", "TOOL041", "TOOL007", "TOOL042", "GLOBAL_HARD_GATE", "BUSINESS_OUTPUT"],
        "handoff": {"status": "PASS_LOCK_REUSED", "sha256": digest(HANDOFF_EVIDENCE)},
        "waste_gate": {"status": "PASS", "classes_blocked": sorted(waste)},
        "closure_reserve": "PASS",
        "registry": {"status": "PASS", "path": str(REGISTRY.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(REGISTRY)},
        "large_factory": large_factory,
        "universal_socket": {"status": "PASS", "component": socket["id"], "path": socket["path"]},
        "tool044": tool044,
        "actual_execution": {"status": "PASS", "result_sha256": json_digest(positive)},
        "positive_negative_failure": {"positive": "PASS", "negative": "PASS", "failure": "PASS"},
        "retry_recovery_rollback": {"status": "PASS", "deterministic": True, "rollback": "NO_OUTPUT_COMMITTED_ON_FAILURE"},
        "global_hard_gate": gate,
        "business_output": {"status": "PASS", "path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(OUTPUT), "readback": "PASS"},
        "pending_external": ["CUSTOMER_RESPONSE", "ORDER", "PAYMENT", "REVENUE", "ACTUAL_24H_ELAPSED"],
        "overall": "PASS_INTERNAL_PENDING_EXTERNAL",
    }
    EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    require(json.loads(EVIDENCE.read_text(encoding="utf-8")) == evidence, "EVIDENCE_READBACK_FAILED")
    print(json.dumps({"status": evidence["overall"], "run_id": evidence["run_id"], "output": str(OUTPUT), "evidence": str(EVIDENCE)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
