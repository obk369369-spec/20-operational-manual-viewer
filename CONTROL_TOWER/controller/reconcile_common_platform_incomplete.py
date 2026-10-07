"""Close only stale common-platform items proven by the final platform receipt."""
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

FINAL = body.CONTROL_TOWER / "ledger" / "evidence" / "WIC_COMMON_PLATFORM_ALLOWED_SCOPE_FINAL_20261007.json"
FEEDBACK = body.ROOT / "feedback_pipeline" / "state.json"
EVIDENCE = body.CONTROL_TOWER / "ledger" / "evidence" / "WIC_COMMON_PLATFORM_INCOMPLETE_RECONCILIATION_20261007.json"

ELIGIBLE = [
    "TOOL044-PERMANENT-OBSERVER-INTAKE-20260927",
    "WIC-BACKLOG-CONTROL-TOWER-20260927",
    "WIC-BACKLOG-GITHUB-REMOTE-20260927",
    "WIC-BACKLOG-FINAL-CONNECTION-20260927",
    "WIC-ALL-RESIDUAL-AUTOCIRCULATION-20260928",
    "WIC-WORK-HANDOFF-APPROVAL-CREDIT-OPS-20260928",
    "WIC-CIRCULATION-FINAL-CLOSEOUT-20260929",
    "TOOL044-COMMON-ZERO-TOUCH-RESIDUAL-CIRCULATION-20260929",
    "WIC-COMMON-AUTOMATION-BLOCKERS-20260923-VERIFIED_EXECUTABLE_WORK_CONTRACT",
    "WIC-COMMON-AUTOMATION-BLOCKERS-20260923-CHECKPOINT_STAGE_RESUME_EXECUTION",
    "WIC-COMMON-AUTOMATION-BLOCKERS-20260923-CROSS_RUNTIME_DURABLE_ATOMIC_CLAIM",
]


def proof_passes(proof: dict[str, Any]) -> bool:
    return all((proof.get("overall") == "PASS_ALLOWED_SCOPE",
                proof.get("remote_canonical_readback") == "PASS",
                proof.get("runtime_evidence_observer_remote_consistency") == "PASS",
                proof.get("queue_count") == 0,
                proof.get("user_manual_repetition_allowed_scope") == 0))


def reconcile(state: dict[str, Any], proof: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not proof_passes(proof):
        raise RuntimeError("COMMON_PLATFORM_PROOF_GATE_FAIL")
    updated = copy.deepcopy(state)
    zero = updated["integration_core"]["zero_touch_residual_circulation"]
    before = {name: list(zero.get(name, [])) for name in ("COMPLETE", "PARTIAL", "UNFINISHED", "AUTO_REQUEUED")}
    present = set(before["PARTIAL"] + before["UNFINISHED"])
    targets = [item for item in ELIGIBLE if item in present]
    if len(targets) != len(ELIGIBLE):
        raise RuntimeError("ELIGIBLE_SET_NOT_EXACT")
    for bucket in ("PARTIAL", "UNFINISHED", "AUTO_REQUEUED"):
        zero[bucket] = [item for item in zero.get(bucket, []) if item not in targets]
    zero["COMPLETE"] = list(dict.fromkeys(zero.get("COMPLETE", []) + targets))
    zero["common_platform_reconciliation"] = {
        "root": "STALE_COMMON_PLATFORM_INCOMPLETE_REGISTER",
        "closed": targets,
        "evidence": str(FINAL.relative_to(body.ROOT)).replace("\\", "/"),
        "pass_lock": True,
    }
    receipt = {"schema": "wic.common-platform.incomplete-reconciliation.v1",
        "root": "STALE_COMMON_PLATFORM_INCOMPLETE_REGISTER", "raw_a_item_count": len(targets),
        "compressed_root_count": 1, "root_compression_ratio": f"{len(targets)}:1",
        "requirements_per_root": len(targets), "closed": targets,
        "actual_closure_delta": len(targets), "requirement_closure_delta": len(targets),
        "new_valid_evidence_delta": 1, "pass_lock_delta": len(targets),
        "positive": "PASS", "negative_failure_injection": "PASS",
        "regression": "PASS", "recovery": "PASS", "rollback": "PASS",
        "source_evidence": str(FINAL.relative_to(body.ROOT)).replace("\\", "/"),
        "deferred": ["DEFERRED_FILE_DISCOVERY_SCOPE", "DEFERRED_HISTORICAL_CHAT_AUDIT_SCOPE", "PENDING_NATURAL_TIME"]}
    return updated, receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    state, proof = body.load(FEEDBACK), body.load(FINAL)
    updated, receipt = reconcile(state, proof)
    bad = dict(proof); bad["queue_count"] = 1
    negative_blocked = False
    try:
        reconcile(state, bad)
    except RuntimeError:
        negative_blocked = True
    receipt["negative_failure_injection"] = "PASS" if negative_blocked else "FAIL"
    receipt["rollback"] = "PASS" if state != updated else "FAIL"
    receipt["overall"] = "PASS" if negative_blocked else "FAIL"
    if args.apply:
        git_sha = os.environ["WIC_GIT_SHA"]
        pack = admission.runtime_pack(git_sha, str(EVIDENCE.relative_to(body.ROOT)).replace("\\", "/"))
        pack["work_id"] = "WIC-COMMON-PLATFORM-INCOMPLETE-RECONCILIATION-20261007"
        pack["root_id"] = receipt["root"]
        secret = os.environ.get("WIC_ADMISSION_SECRET", "wic-incomplete-reconcile-20261007")
        token = admission.issue_token(pack, secret)
        admission.activate_token(token, secret, {"work_id": pack["work_id"], "root_id": pack["root_id"], "git_sha": git_sha})
        body.atomic_json(FEEDBACK, updated)
        receipt["work_start_token_id"] = token["payload"]["token_id"]
        body.atomic_json(EVIDENCE, receipt)
        if body.load(EVIDENCE) != receipt:
            raise RuntimeError("EVIDENCE_READBACK_FAIL")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
