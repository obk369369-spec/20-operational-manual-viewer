import json

from tool016_visible_handoff import (build, reconcile_registry_pass_locks,
                                     import_verified_closure_receipts)


def test_visible_handoff_groups_work_and_auto_routes_external():
    queue = {"demands": [
        {"demand_id": "DONE", "status": "SATISFIED_BY_COMMON_COMPONENT"},
        {"demand_id": "OLD-PASS", "status": "PASS_WORK_ROOT_SPECIFIC_RETET_20260925"},
        {"demand_id": "WORK-1", "status": "SUPERSEDED"},
        {"demand_id": "WORK-1", "root_id": "ROOT-A", "target_tool": "TOOL016",
         "status": "OPEN", "atomic_capabilities": ["SCHEMA"]},
        {"demand_id": "WORK-2", "root_id": "ROOT-A", "target_tool": "TOOL044",
         "status": "OPEN", "atomic_capabilities": ["SCHEMA"]},
        {"demand_id": "EXTERNAL", "root_id": "ROOT-B", "status": "OPEN",
         "atomic_capabilities": ["MISSING"]},
    ]}
    pool = {"components": [{"status": "VERIFIED_REUSABLE", "atomic_capabilities": ["SCHEMA"]}]}
    providers = {"target_provider_count": 15, "providers": [
        {"provider_id": "GITHUB", "status": "ACTUAL_RUN_PASS"},
        {"provider_id": "WOODPECKER", "status": "BLOCKED_USER_ACTION"},
    ], "bulk_summary": {"actual_run_pass": 1}}
    result = build(queue, pool, {"capacity": 15, "jobs": {}}, "NOW", providers)
    assert result["UNFINISHED_SCANNED"] == 3
    assert result["ALREADY_PASS_EXCLUDED"] == 3
    assert result["ROOTS_MERGED"] == 1
    assert result["WORK_FIXABLE_ROOTS"] == 1
    assert result["TOOL044_AUTO_HANDED_OFF"] == 1
    assert result["WORK_BATCHES"][0]["demands"] == ["WORK-1", "WORK-2"]
    assert result["USER_MANUAL_RELAY_REQUIRED"] == 0
    assert result["CIRCULATION"]["dedup_gate"] == "PASS"
    assert result["FREE_EXTERNAL_RUNNER_POOL"]["actual_run_pass"] == ["GITHUB"]
    assert result["FREE_EXTERNAL_RUNNER_POOL"]["blocked_user_action"] == ["WOODPECKER"]


def test_registry_pass_lock_requires_explicit_passing_receipt(tmp_path):
    good = tmp_path / "good.json"
    bad = tmp_path / "bad.json"
    good.write_text(json.dumps({"overall": "PASS", "closed_requirement_ids": ["A"]}))
    bad.write_text(json.dumps({"overall": "FAIL", "closed_requirement_ids": ["B"]}))
    queue = {"demands": [
        {"demand_id": "A", "status": "OPEN"},
        {"demand_id": "B", "status": "OPEN"},
        {"demand_id": "C", "status": "OPEN"},
    ]}
    registry = {"demand_bindings": [
        {"demand_id": "A", "status": "PASS_LOCKED", "contract_id": "ROOT",
         "evidence": "good.json"},
        {"demand_id": "B", "status": "PASS_LOCKED", "contract_id": "ROOT",
         "evidence": "bad.json"},
        {"demand_id": "C", "status": "PASS_LOCKED", "contract_id": "ROOT",
         "evidence": "missing.json"},
    ]}
    assert reconcile_registry_pass_locks(queue, registry, tmp_path) == ["A"]
    assert queue["demands"][0]["status"] == "PASS_LOCKED"
    assert queue["demands"][1]["status"] == "OPEN"
    assert queue["demands"][2]["status"] == "OPEN"


def test_verified_closure_receipt_imports_once(tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"overall": "PASS", "root": "COMMON",
                                   "closed": ["A", "B"]}))
    registry = {"demand_bindings": [{"demand_id": "A", "status": "PASS_LOCKED"}]}
    assert import_verified_closure_receipts(registry, tmp_path, ("receipt.json",)) == ["B"]
    assert import_verified_closure_receipts(registry, tmp_path, ("receipt.json",)) == []


def test_internal_common_governance_receipt_imports_pass_lock(tmp_path):
    receipt = tmp_path / "common.json"
    receipt.write_text(json.dumps({
        "overall": "PASS",
        "root": "INTERNAL_COMMON_GOVERNANCE_EXECUTION",
        "closed": ["WIC-BACKLOG-TOOL016-20260927"],
        "closed_requirement_ids": ["WIC-BACKLOG-TOOL016-20260927"],
    }), encoding="utf-8")
    registry = {"demand_bindings": []}
    imported = import_verified_closure_receipts(
        registry, tmp_path, ("common.json",)
    )
    assert imported == ["WIC-BACKLOG-TOOL016-20260927"]
    assert registry["demand_bindings"][0]["status"] == "PASS_LOCKED"


def test_pass_lock_never_reopens_without_legacy_result_ack():
    from tool016_visible_handoff import reconcile_demands
    queue = {"demands": [{"demand_id": "LOCKED", "status": "PASS_LOCKED",
                           "atomic_capabilities": ["CAP"],
                           "pass_lock": {"evidence_readback": "PASS"}}]}
    pool = {"components": [{"status": "VERIFIED_REUSABLE",
                             "atomic_capabilities": ["CAP"]}]}
    updated, report = reconcile_demands(queue, pool, "NOW")
    assert updated["demands"][0]["status"] == "PASS_LOCKED"
    assert report["COMPLETE"] == ["LOCKED"]
    assert report["AUTO_REQUEUED"] == []
