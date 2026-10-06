#!/usr/bin/env python3
"""Build the final WIC evidence pack from already-produced canonical evidence.

This is a closeout-only component.  It never runs the platform, mutates the
queue, or manufactures PASS values.  Missing or inconsistent proof is kept
fail-closed in ``closure_status``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "CONTROL_TOWER" / "ledger" / "evidence" / "WIC_PLATFORM_FINAL_EVIDENCE_PACK.json"

CANONICAL_INPUTS = {
    "final_actual_wic_e2e": ROOT / "customer_pipeline" / "evidence" / "WIC_FINAL_PLATFORM_LANE_A_20261006.json",
    "observer_actual_public_e2e": ROOT / "CONTROL_TOWER" / "ledger" / "evidence" / "WIC_FINAL_VALIDATION_OBSERVER_CLOSURE_20261006.json",
    "off_device_runtime_continuity": ROOT / "CONTROL_TOWER" / "ledger" / "evidence" / "WIC_OFF_DEVICE_RUNTIME_CONTINUITY.json",
    "runtime_controller_state": ROOT / "CONTROL_TOWER" / "controller" / "runtime" / "controller_state.json",
    "runtime_requirement_queue": ROOT / "CONTROL_TOWER" / "controller" / "runtime" / "requirement_queue.json",
    "public_observer_state": ROOT / "public" / "wic_observer_state.json",
    "handoff_gate": ROOT / "feedback_pipeline" / "evidence" / "wic_automatic_handoff_state.json",
    "incremental_files": ROOT / "CONTROL_TOWER" / "ledger" / "evidence" / "WIC_INCREMENTAL_FILE_DISCOVERY.json",
}


def load_json(path: Path) -> tuple[Any | None, dict[str, Any]]:
    receipt: dict[str, Any] = {"path": path.relative_to(ROOT).as_posix(), "exists": path.is_file()}
    if not receipt["exists"]:
        receipt.update({"readback": "MISSING", "sha256": None})
        return None, receipt
    raw = path.read_bytes()
    receipt["sha256"] = hashlib.sha256(raw).hexdigest()
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        receipt.update({"readback": "INVALID_JSON", "error": str(exc)})
        return None, receipt
    receipt["readback"] = "PASS"
    return value, receipt


def find_value(value: Any, keys: set[str]) -> Any | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in keys:
                return item
        for item in value.values():
            found = find_value(item, keys)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_value(item, keys)
            if found is not None:
                return found
    return None


def is_pass(value: Any) -> bool:
    if isinstance(value, dict):
        value = value.get("status") or value.get("overall") or value.get("result")
    return value is True or (isinstance(value, str) and value.upper() in {"PASS", "COMPLETE", "CLOSED", "SUCCESS", "PASS_INTERNAL_PENDING_EXTERNAL"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--commit", default=os.getenv("GITHUB_SHA"))
    parser.add_argument("--remote-run-id", default=os.getenv("GITHUB_RUN_ID"))
    parser.add_argument("--remote-readback", choices=("PASS", "FAIL", "PENDING"), default="PENDING")
    args = parser.parse_args()

    evidence: dict[str, Any] = {}
    receipts: dict[str, Any] = {}
    for name, path in CANONICAL_INPUTS.items():
        evidence[name], receipts[name] = load_json(path)

    final_e2e = evidence["final_actual_wic_e2e"]
    observer = evidence["observer_actual_public_e2e"]
    runtime = evidence["runtime_controller_state"]
    public_state = evidence["public_observer_state"]

    gates = {
        "actual_wic_e2e": is_pass(find_value(final_e2e, {"status", "result", "overall", "overall_status", "overall_result", "pass"})),
        "actual_business_output": bool(find_value(final_e2e, {"actual_output", "business_output", "output_file", "output_path", "artifact"})),
        "observer_user_surface": is_pass(find_value(observer, {"status", "result", "overall_status", "overall_result", "pass"})),
        "failure_recovery": is_pass(find_value(final_e2e, {"failure_recovery", "recovery_result", "recovery_status", "retry_recovery_rollback"})),
        "runtime_state_readback": receipts["runtime_controller_state"]["readback"] == "PASS",
        "observer_state_readback": receipts["public_observer_state"]["readback"] == "PASS",
        "remote_canonical_readback": args.remote_readback == "PASS" and bool(args.commit) and bool(args.remote_run_id),
    }

    runtime_id = (runtime or {}).get("github_runtime", {}).get("run_id")
    observer_runtime_id = (public_state or {}).get("current", {}).get("run_id")
    state_consistency = bool(runtime_id and observer_runtime_id and str(runtime_id) == str(observer_runtime_id))
    gates["runtime_evidence_observer_consistency"] = state_consistency

    pending_external = []
    for source in (runtime, evidence["runtime_requirement_queue"], public_state):
        found = find_value(source, {"pending_external", "long_term_hold", "external_blocked", "market_validation_pending"})
        if found:
            pending_external.append(found)

    closure_pass = all(gates.values())
    pack = {
        "schema": "wic.platform-final-evidence-pack.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "FINAL_CLOSURE_FAIL_CLOSED",
        "closed_reuse_only": ["INCREMENTAL_FILES", "HANDOFF_GATE"],
        "final_platform_run_id": find_value(final_e2e, {"run_id", "execution_id", "final_platform_run_id"}),
        "actual_wic_input": find_value(final_e2e, {"actual_input", "input_file", "input_path", "source_file"}),
        "actual_wic_business_output": find_value(final_e2e, {"actual_output", "business_output", "output_file", "output_path", "artifact"}),
        "gates": gates,
        "canonical_receipts": receipts,
        "remote": {
            "commit": args.commit,
            "runtime_run_id": args.remote_run_id,
            "canonical_readback": args.remote_readback,
        },
        "pending_external": pending_external,
        "closure_status": "PASS" if closure_pass else "HOLD",
        "WIC_PLATFORM_OPERATIONAL_VERIFIED": "PASS" if closure_pass else "HOLD",
        "missing_or_failed_gates": [name for name, passed in gates.items() if not passed],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reread = json.loads(args.output.read_text(encoding="utf-8"))
    if reread != pack:
        raise SystemExit("FINAL_EVIDENCE_PACK_READBACK_MISMATCH")
    print(json.dumps({
        "output": str(args.output),
        "closure_status": pack["closure_status"],
        "missing_or_failed_gates": pack["missing_or_failed_gates"],
        "readback": "PASS",
    }, ensure_ascii=False))
    return 0 if closure_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
