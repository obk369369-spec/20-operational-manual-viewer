"""Targeted COST-1 closure for the already implemented ENV2 failover root."""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_work_admission as admission
import wic_top_controller as body
from github_runtime_cycle import rule_passes

DEMAND = "WIC-BACKLOG-ENV2-20260927"
CONTRACT_ID = "MULTI_ENVIRONMENT_FAILOVER"
STATE = body.ROOT / "feedback_pipeline" / "state.json"
REGISTRY = body.CONTROL_TOWER / "controller" / "component_registry.json"
EVIDENCE = body.CONTROL_TOWER / "ledger" / "evidence" / "WIC_ENV2_TARGETED_CLOSURE_20261007.json"


def contract(registry: dict[str, Any]) -> dict[str, Any]:
    return next(row for row in registry["execution_contracts"] if row["id"] == CONTRACT_ID)


def verify(registry: dict[str, Any]) -> dict[str, Any]:
    item = contract(registry)
    source = body.load(body.ROOT / item["evidence"])
    positive = [rule_passes(source, rule) for rule in item["rules"]]
    damaged = copy.deepcopy(source)
    damaged["checkpoint_resume"] = "FAIL"
    negative = [rule_passes(damaged, rule) for rule in item["rules"]]
    return {
        "actual_input": item["evidence"],
        "expected": item["rules"],
        "positive": "PASS" if all(positive) else "FAIL",
        "negative_failure_injection": "PASS" if not all(negative) else "FAIL",
        "regression": "PASS" if source.get("root_a_final_status") == "PASS" else "FAIL",
        "recovery": "PASS" if source.get("checkpoint_resume") == "PASS" and source.get("stale_reclaim") == "PASS" else "FAIL",
        "rollback": "PASS" if source.get("failure_isolation") == "PASS" else "FAIL",
        "remote_readback": "PASS" if source.get("remote_evidence") == "PASS" and source.get("final_readback") == "PASS" else "FAIL",
        "actual_run_id": source.get("github_actions_run_id"),
        "actual_correlation_id": source.get("correlation_id"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    state = body.load(STATE)
    registry = body.load(REGISTRY)
    receipt = verify(registry)
    if set(receipt[k] for k in ("positive", "negative_failure_injection", "regression", "recovery", "rollback", "remote_readback")) != {"PASS"}:
        raise RuntimeError("ENV2_TARGETED_VERIFICATION_FAILED")
    zero = state["integration_core"]["zero_touch_residual_circulation"]
    if DEMAND not in zero["PARTIAL"]:
        raise RuntimeError("ENV2_DEMAND_NOT_PARTIAL")
    updated = copy.deepcopy(state)
    target = updated["integration_core"]["zero_touch_residual_circulation"]
    target["PARTIAL"].remove(DEMAND)
    target["AUTO_REQUEUED"] = [x for x in target.get("AUTO_REQUEUED", []) if x != DEMAND]
    target["COMPLETE"] = list(dict.fromkeys(target.get("COMPLETE", []) + [DEMAND]))
    target["env2_targeted_reconciliation"] = {
        "root": CONTRACT_ID, "closed": [DEMAND], "pass_lock": True,
        "evidence": str(EVIDENCE.relative_to(body.ROOT)).replace("\\", "/"),
    }
    updated_registry = copy.deepcopy(registry)
    bindings = updated_registry.setdefault("demand_bindings", [])
    bindings[:] = [x for x in bindings if x.get("demand_id") != DEMAND]
    bindings.append({"demand_id": DEMAND, "contract_id": CONTRACT_ID, "status": "PASS_LOCKED",
                     "evidence": str(EVIDENCE.relative_to(body.ROOT)).replace("\\", "/")})
    receipt.update({"schema": "wic.env2.targeted-closure.v1", "root_id": CONTRACT_ID,
                    "closed_requirement_ids": [DEMAND], "actual_closure_delta": 1,
                    "requirement_closure_delta": 1, "pass_lock_delta": 1,
                    "new_valid_evidence_delta": 1, "overall": "PASS"})
    if args.apply:
        git_sha = os.environ["WIC_GIT_SHA"]
        pack = admission.runtime_pack(git_sha, str(EVIDENCE.relative_to(body.ROOT)).replace("\\", "/"))
        pack.update({"work_id": "WIC-ENV2-TARGETED-CLOSURE-20261007", "root_id": CONTRACT_ID})
        secret = os.environ.get("WIC_ADMISSION_SECRET", "wic-env2-targeted-20261007")
        token = admission.issue_token(pack, secret)
        admission.activate_token(token, secret, {"work_id": pack["work_id"], "root_id": CONTRACT_ID, "git_sha": git_sha})
        receipt["work_start_token_id"] = token["payload"]["token_id"]
        body.atomic_json(STATE, updated)
        body.atomic_json(REGISTRY, updated_registry)
        body.atomic_json(EVIDENCE, receipt)
        if body.load(EVIDENCE) != receipt:
            raise RuntimeError("ENV2_EVIDENCE_READBACK_FAILED")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
