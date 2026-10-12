from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from github_runtime_cycle import (execute_central_backlog, reconcile_central_backlog,
                                  route_contracts, validate_contract)


def main(output: str) -> int:
    root = Path(__file__).resolve().parents[2]
    ledger_path = root / "feedback_pipeline" / "unified_open_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    queue = {"queued_requirement_ids": []}
    result = reconcile_central_backlog(queue, ledger)
    expected = {
        "open_ledger_count": 6,
        "executable_count": 1,
        "deferred_count": 5,
        "next_root": "WIC-0702-SCOPED-RECOVERY",
        "pass_locked_reopened": 0,
    }
    comparison = {key: result.get(key) == value for key, value in expected.items()}
    recovery_contract = {
        "id": "RECOVERY", "requirement_ids": [1], "proof": "RECOVERY",
        "evidence": "missing-evidence.json",
        "recovery_evidence": "CONTROL_TOWER/ledger/evidence/WIC_CENTRAL_BACKLOG_RECONCILIATION_20261012.json",
        "rules": [{"path": "overall", "operation": "equals", "expected": "PASS"}],
    }
    recovered = validate_contract(recovery_contract)
    state = {"requirements": [
        {"id": 1, "queue_status": "QUEUED", "retry_count": 1},
        {"id": 2, "queue_status": "QUEUED", "retry_count": 0},
    ]}
    isolation_queue = {"queued_requirement_ids": [1, 2]}
    isolation_registry = {"execution_contracts": [
        {"id": "UNRECOVERABLE", "requirement_ids": [1], "proof": "FAIL",
         "evidence": "unrecoverable-evidence.json",
         "rules": [{"path": "overall", "operation": "equals", "expected": "PASS"}]},
        {"id": "NORMAL", "requirement_ids": [2], "proof": "CONTINUE",
         "evidence": "CONTROL_TOWER/ledger/evidence/WIC_CENTRAL_BACKLOG_RECONCILIATION_20261012.json",
         "rules": [{"path": "overall", "operation": "equals", "expected": "PASS"}]},
    ]}
    processed, held = route_contracts(state, isolation_queue, isolation_registry)
    execution_ledger = deepcopy(ledger)
    execution_queue = {"queued_requirement_ids": [], "backlog_root_ids": [result["next_root"]],
                       "next_backlog_root": result["next_root"]}
    attempted = execute_central_backlog(execution_queue, execution_ledger, {"backlog_execution_contracts": []})
    scenario_results = {
        "normal_evidence_preserved": result["pass_locked_reopened"] == 0,
        "missing_recoverable_auto_recovered": recovered["status"] == "PASS" and recovered["evidence_recovered"],
        "missing_unrecoverable_quarantined": bool(isolation_queue.get("quarantined_requirements")),
        "validation_failure_did_not_block_normal": [item["requirement_id"] for item in processed] == [2],
        "open_ledger_root_execution_attempted": attempted[0]["root_id"] == result["next_root"],
        "repeated_failure_retry_stopped": state["requirements"][0]["queue_status"] == "WAITING",
        "checkpoint_resume_data_written": next(
            item for item in execution_ledger["entries"] if item.get("root_id") == result["next_root"]
        )["status"] == "HOLD_EXECUTION_CONTRACT_OR_ACTUAL_INPUT",
    }
    evidence = {
        "schema": "wic.central-backlog-reconciliation.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "root_cause": "RUNTIME_NUMERIC_QUEUE_DRAINED_WHILE_CANONICAL_LEDGER_RETAINED_OPEN_ROOTS",
        "actual_input": str(ledger_path.relative_to(root)).replace("\\", "/"),
        "expected": expected,
        "actual": {key: result.get(key) for key in expected},
        "comparison": comparison,
        "selected": result["executable"],
        "deferred": result["deferred"],
        "positive_pass": result["next_root"] == expected["next_root"],
        "negative_pass": result["pass_locked_reopened"] == 0,
        "external_and_time_hold_pass": result["deferred_count"] == 5,
        "queue_writeback": queue,
        "scenario_results": scenario_results,
        "recovery_receipt": recovered,
        "isolation": {"processed": processed, "held": held,
                      "quarantine": isolation_queue.get("quarantined_requirements", [])},
        "backlog_execution": attempted,
        "overall": "PASS" if all(comparison.values()) and all(scenario_results.values()) else "FAIL",
    }
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    reread = json.loads(target.read_text(encoding="utf-8"))
    print(json.dumps({"overall": reread["overall"], "actual": reread["actual"],
                      "evidence_readback": reread == evidence}, ensure_ascii=False))
    return 0 if reread == evidence and evidence["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
