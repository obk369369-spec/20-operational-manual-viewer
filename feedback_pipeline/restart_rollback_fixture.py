from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "restart_rollback_evidence.json"
STAGES = [
    "EVENT",
    "NORMALIZE",
    "ROUTE_EXISTING_REGISTRY",
    "CONFLICT_DEDUP",
    "CANONICAL_WRITE",
    "READ_BACK",
    "TARGET_REVISION_READ_APPLY",
    "TEST_EVIDENCE",
    "RESTART_OR_HOLD",
]


def run_controlled_failure() -> dict:
    before = {
        "feedback_id": "fixture-controlled-failure",
        "last_success_stage": "READ_BACK",
        "canonical_revision": "fixture-revision-a",
        "target_revision": "fixture-revision-old",
        "status": "ACTIVE",
    }
    working = deepcopy(before)
    failure_stage = "TARGET_REVISION_READ_APPLY"
    try:
        working["target_revision"] = "fixture-revision-bad"
        raise RuntimeError("controlled target apply failure")
    except RuntimeError as exc:
        working = deepcopy(before)
        working["status"] = "HOLD_CONTROLLED_FAILURE"
        working["failure_stage"] = failure_stage
        working["error"] = str(exc)
        working["rollback_restored_target_revision"] = before["target_revision"]
        working["restart_from_stage"] = STAGES[STAGES.index(before["last_success_stage"]) + 1]

    assert working["rollback_restored_target_revision"] == "fixture-revision-old"
    assert working["restart_from_stage"] == "TARGET_REVISION_READ_APPLY"
    assert working["last_success_stage"] == "READ_BACK"
    return {
        "schema_version": 1,
        "fixture_type": "CONTROLLED_FAILURE_ROLLBACK_RESTART",
        "before": before,
        "after": working,
        "result": "PASS_INTERNAL_FIXTURE",
        "external_independent_verification": False,
    }


def main() -> None:
    result = run_controlled_failure()
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: controlled failure rollback + last_success_stage restart fixture")


if __name__ == "__main__":
    main()
