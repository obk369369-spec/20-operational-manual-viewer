from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "target_apply_manifest.json"
ADAPTERS = ROOT / "target_adapter_registry.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_plan(manifest: dict, adapters: dict) -> dict:
    revision = manifest["canonical_revision"]
    feedback_id = manifest["feedback_id"]
    repository_targets = adapters.get("repository_targets", {})
    lane_targets = adapters.get("lane_targets", {})
    plan = {"canonical_revision": revision, "feedback_id": feedback_id, "actions": [], "holds": []}

    for target, item in manifest.get("targets", {}).items():
        decision = item.get("decision")
        if decision == "SKIP_UNCHANGED":
            plan["actions"].append({"target": target, "action": "SKIP_UNCHANGED"})
            continue
        if target in repository_targets:
            adapter = repository_targets[target]
            plan["actions"].append({
                "target": target,
                "action": "REPOSITORY_REVISION_ACK",
                "repository": adapter["repository"],
                "state_path": adapter["state_path"],
                "mode": adapter["mode"],
                "canonical_revision": revision,
            })
        elif target in lane_targets:
            adapter = lane_targets[target]
            plan["actions"].append({
                "target": target,
                "action": "LANE_ACK",
                "mode": adapter["mode"],
                "evidence": adapter["evidence"],
                "canonical_revision": revision,
            })
        else:
            plan["holds"].append({
                "target": target,
                "status": "HOLD_NO_VERIFIED_ADAPTER",
                "reason": "No verified repository/lane adapter is registered; do not guess a target repository."
            })
    return plan


def validate_plan(plan: dict) -> None:
    targets = [x["target"] for x in plan["actions"]] + [x["target"] for x in plan["holds"]]
    assert len(targets) == len(set(targets)), "duplicate target in dispatch plan"
    assert plan["canonical_revision"], "missing canonical revision"
    assert plan["feedback_id"], "missing feedback id"
    for action in plan["actions"]:
        if action["action"] == "REPOSITORY_REVISION_ACK":
            assert action.get("repository") and action.get("state_path")
        elif action["action"] == "LANE_ACK":
            assert action.get("evidence")
        elif action["action"] == "SKIP_UNCHANGED":
            pass
        else:
            raise AssertionError(f"unknown action: {action['action']}")


def main() -> None:
    manifest = load(MANIFEST)
    adapters = load(ADAPTERS)
    plan = build_plan(manifest, adapters)
    validate_plan(plan)
    out = ROOT / "target_dispatch_plan.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    by_target = {x["target"]: x for x in plan["actions"]}
    assert by_target["TOOL001"]["repository"] == "obk369369-spec/01-auto-guide-v1"
    assert by_target["TOOL002"]["repository"] == "obk369369-spec/02-auto-bid-narajangter-v1"
    assert by_target["TOOL006"]["repository"] == "obk369369-spec/06-toc-check"
    assert by_target["TOOL013"]["repository"] == "obk369369-spec/13-excel-upload"
    assert by_target["EMAIL_DB"]["action"] == "LANE_ACK"
    assert by_target["TOOL037"]["action"] == "LANE_ACK"
    assert by_target["WORK_GATE"]["action"] == "LANE_ACK"
    held = {x["target"] for x in plan["holds"]}
    assert held == {"TOOL007"}
    print("PASS: deterministic target dispatcher plan + verified TOOL001/002 + fail-closed TOOL007")


if __name__ == "__main__":
    main()
