from tool016_visible_handoff import build


def test_visible_handoff_groups_work_and_auto_routes_external():
    queue = {"demands": [
        {"demand_id": "DONE", "status": "SATISFIED_BY_COMMON_COMPONENT"},
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
    assert result["ALREADY_PASS_EXCLUDED"] == 1
    assert result["ROOTS_MERGED"] == 1
    assert result["WORK_FIXABLE_ROOTS"] == 1
    assert result["TOOL044_AUTO_HANDED_OFF"] == 1
    assert result["WORK_BATCHES"][0]["demands"] == ["WORK-1", "WORK-2"]
    assert result["USER_MANUAL_RELAY_REQUIRED"] == 0
    assert result["FREE_EXTERNAL_RUNNER_POOL"]["actual_run_pass"] == ["GITHUB"]
    assert result["FREE_EXTERNAL_RUNNER_POOL"]["blocked_user_action"] == ["WOODPECKER"]
