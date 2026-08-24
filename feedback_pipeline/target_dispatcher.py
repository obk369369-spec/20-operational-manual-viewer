from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "target_apply_manifest.json"
ADAPTERS = ROOT / "target_adapter_registry.json"
REVISION_CACHE = ROOT / "target_revision_cache.json"

REQUIRED_MUTATION_STAGES = [
    "PRECHECK_USER_DIRECTIVE",
    "VALIDATE",
    "APPLY",
    "TEST",
    "EVIDENCE",
    "ROLLBACK_OR_HOLD",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_common_mutation_contract(adapters: dict) -> None:
    contract = adapters.get("common_mutation_contract", {})
    assert contract.get("contract_id") == "WIC_MATERIAL_MUTATION_V1", "missing common material mutation contract"
    assert contract.get("required_stage_order") == REQUIRED_MUTATION_STAGES, "material mutation stage order drift"
    assert contract.get("fail_closed") is True, "material mutation contract must fail closed"
    assert contract.get("apply_requires_precheck_allow") is True, "APPLY must require PRECHECK_USER_DIRECTIVE ALLOW"
    assert contract.get("deny_decision") == "DENY_HOLD", "unauthorized mutation must DENY_HOLD"
    assert contract.get("deny_observer_report_required") is True, "DENY evidence must reach observer report lane"
    assert contract.get("deny_observer_delivery_target") == "WIC_OBSERVER_STATUS.md", "DENY observer delivery target drift"
    assert contract.get("deny_must_be_blocked_before_mutation") is True, "DENY must occur before material mutation"
    assert contract.get("rollback_or_hold_required_on_post_apply_failure") is True, "post-APPLY failure must rollback or hold"
    assert contract.get("evidence_required_before_pass") is True, "PASS requires evidence"


def build_plan(manifest: dict, adapters: dict, revision_cache: dict) -> dict:
    revision = manifest["canonical_revision"]
    feedback_id = manifest["feedback_id"]
    repository_targets = adapters.get("repository_targets", {})
    lane_targets = adapters.get("lane_targets", {})
    cached_targets = revision_cache.get("targets", {})
    plan = {"canonical_revision": revision, "feedback_id": feedback_id, "actions": [], "holds": []}

    for target, item in manifest.get("targets", {}).items():
        decision = item.get("decision")
        cached = cached_targets.get(target, {})
        if decision == "SKIP_UNCHANGED" or cached.get("applied_revision") == revision:
            plan["actions"].append({
                "target": target,
                "action": "SKIP_UNCHANGED",
                "canonical_revision": revision,
                "reason": "target revision cache already records the same canonical revision",
                "test_status": cached.get("test_status", "UNKNOWN"),
            })
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
                "status": "REPOSITORY_CREATE_HOLD",
                "reason": (
                    "No verified repository/lane adapter is registered. Existing repository ownership "
                    "and repository-create authority/path must be verified before creating anything."
                ),
                "normal_registered_routes_continue": True,
                "repository_create_attempted": False,
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
            assert action.get("canonical_revision")
        else:
            raise AssertionError(f"unknown action: {action['action']}")


def validate_against_inputs(plan: dict, manifest: dict, adapters: dict, revision_cache: dict) -> None:
    revision = manifest["canonical_revision"]
    repository_targets = adapters.get("repository_targets", {})
    lane_targets = adapters.get("lane_targets", {})
    cached_targets = revision_cache.get("targets", {})
    actions = {x["target"]: x for x in plan["actions"]}
    holds = {x["target"]: x for x in plan["holds"]}

    expected_targets = set(manifest.get("targets", {}))
    actual_targets = set(actions) | set(holds)
    assert actual_targets == expected_targets, "dispatch plan target set differs from manifest"

    for target, item in manifest.get("targets", {}).items():
        decision = item.get("decision")
        cached = cached_targets.get(target, {})
        if decision == "SKIP_UNCHANGED" or cached.get("applied_revision") == revision:
            assert actions[target]["action"] == "SKIP_UNCHANGED"
        elif target in repository_targets:
            assert actions[target]["action"] == "REPOSITORY_REVISION_ACK"
        elif target in lane_targets:
            assert actions[target]["action"] == "LANE_ACK"
        else:
            assert holds[target]["status"] == "REPOSITORY_CREATE_HOLD"
            assert holds[target]["normal_registered_routes_continue"] is True
            assert holds[target]["repository_create_attempted"] is False


def main() -> None:
    manifest = load(MANIFEST)
    adapters = load(ADAPTERS)
    revision_cache = load(REVISION_CACHE)
    assert revision_cache["schema_version"] == 1
    validate_common_mutation_contract(adapters)
    plan = build_plan(manifest, adapters, revision_cache)
    validate_plan(plan)
    validate_against_inputs(plan, manifest, adapters, revision_cache)

    # Representative boundary fixture: one registered repository keeps running
    # while one ownerless route is isolated in repository-create HOLD.
    fixture_manifest = {
        "canonical_revision": "fixture-revision",
        "feedback_id": "fixture-feedback",
        "targets": {
            "TOOL006": {"decision": "APPLY_CHANGED_SCOPE"},
            "UNREGISTERED_ROUTE": {"decision": "APPLY_CHANGED_SCOPE"},
        },
    }
    fixture_plan = build_plan(fixture_manifest, adapters, {"targets": {}})
    validate_plan(fixture_plan)
    validate_against_inputs(fixture_plan, fixture_manifest, adapters, {"targets": {}})
    fixture_actions = {item["target"]: item for item in fixture_plan["actions"]}
    fixture_holds = {item["target"]: item for item in fixture_plan["holds"]}
    assert fixture_actions["TOOL006"]["action"] == "REPOSITORY_REVISION_ACK"
    assert fixture_holds["UNREGISTERED_ROUTE"]["status"] == "REPOSITORY_CREATE_HOLD"
    assert fixture_holds["UNREGISTERED_ROUTE"]["normal_registered_routes_continue"] is True

    out = ROOT / "target_dispatch_plan.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: common material mutation contract + dispatch plan match current manifest, adapter registry, and revision cache")


if __name__ == "__main__":
    main()
