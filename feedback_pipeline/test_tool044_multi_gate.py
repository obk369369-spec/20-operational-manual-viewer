import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from tool044_multi_gate import aggregate, plan, run_lane
from tool044_safe_integration import READY_COMPONENT_FIELDS


def component(component_id="READY-ONE"):
    row = {field: f"verified-{field}" for field in READY_COMPONENT_FIELDS}
    row.update(component_id=component_id, status="READY", target_root="ROOT-1", target_tool="TOOL044",
               install_method=[sys.executable, "-c", "from pathlib import Path; Path('installed').write_text('ok')"],
               validator=[sys.executable, "-c", "from pathlib import Path; assert Path('installed').read_text() == 'ok'"],
               rollback_method=[sys.executable, "-c", "from pathlib import Path; Path('installed').unlink(missing_ok=True)"])
    return row


def test_plan_claim_run_and_central_return(tmp_path: Path):
    pool = tmp_path / "pool.json"; state = tmp_path / "state.json"; central = tmp_path / "central.json"
    queue = tmp_path / "queue.json"
    pool.write_text(json.dumps({"components": [component()]}), encoding="utf-8")
    central.write_text(json.dumps({"integration_core": {}}), encoding="utf-8")
    queue.write_text(json.dumps({"demands": []}), encoding="utf-8")
    matrix = plan(pool, state, "RUN-1", queue)
    assert len(matrix) == 1
    claimed = json.loads(state.read_text(encoding="utf-8"))["jobs"]["COMPONENT::READY-ONE"]
    assert claimed["STATUS"] == "CLAIMED" and claimed["CHECKPOINT"] == "CLAIM_DURABLE"
    result = tmp_path / "result.json"
    actual = run_lane(state, matrix[0]["job_id"], matrix[0]["owner"], result)
    assert actual["status"] == "PASS" and actual["production_mutation"] == 0
    merged = aggregate(state, central, [result], queue)
    assert merged["jobs"][matrix[0]["job_id"]]["STATUS"] == "PASS"
    returned = json.loads(central.read_text(encoding="utf-8"))["integration_core"]["tool044_multi_gate"]
    assert returned["results_returned"] == 1


def test_incomplete_component_is_held(tmp_path: Path):
    row = component("INCOMPLETE"); del row["rollback_condition"]
    pool = tmp_path / "pool.json"; state = tmp_path / "state.json"
    pool.write_text(json.dumps({"components": [row]}), encoding="utf-8")
    queue = tmp_path / "queue.json"; queue.write_text(json.dumps({"demands": []}), encoding="utf-8")
    assert plan(pool, state, "RUN-2", queue) == []
    job = json.loads(state.read_text(encoding="utf-8"))["jobs"]["COMPONENT::INCOMPLETE"]
    assert job["STATUS"] == "HOLD" and job["RESULT"]["missing"] == ["rollback_condition"]


def test_failed_validator_runs_rollback(tmp_path: Path):
    row = component("ROLLBACK")
    row["validator"] = [sys.executable, "-c", "raise SystemExit(2)"]
    pool = tmp_path / "pool.json"; state = tmp_path / "state.json"
    pool.write_text(json.dumps({"components": [row]}), encoding="utf-8")
    queue = tmp_path / "queue.json"; queue.write_text(json.dumps({"demands": []}), encoding="utf-8")
    matrix = plan(pool, state, "RUN-3", queue)
    result = run_lane(state, matrix[0]["job_id"], matrix[0]["owner"], tmp_path / "result.json")
    assert result["status"] == "FAIL"
    assert result["rollback_pass"] is True


def test_verified_component_auto_claims_real_demand(tmp_path: Path):
    row = component("MATCHER")
    row["atomic_capabilities"] = ["INPUT_CONTRACT_VALIDATION"]
    pool = tmp_path / "pool.json"; state = tmp_path / "state.json"
    queue = tmp_path / "queue.json"; central = tmp_path / "central.json"
    pool.write_text(json.dumps({"components": [row]}), encoding="utf-8")
    queue.write_text(json.dumps({"demands": [{"demand_id": "REAL-DEMAND-1", "root_id": "ROOT-1",
                                               "target_tool": "TOOL016", "status": "OPEN",
                                               "atomic_capabilities": ["INPUT_CONTRACT_VALIDATION"]}]}), encoding="utf-8")
    central.write_text(json.dumps({"integration_core": {}}), encoding="utf-8")
    first = plan(pool, state, "RUN-4", queue)
    result = tmp_path / "component.json"
    run_lane(state, first[0]["job_id"], first[0]["owner"], result)
    aggregate(state, central, [result], queue)
    second = plan(pool, state, "RUN-5", queue)
    assert second[0]["job_id"].startswith("DEMAND::REAL-DEMAND-1::MATCHER")
    demand_result = tmp_path / "demand.json"
    run_lane(state, second[0]["job_id"], second[0]["owner"], demand_result)
    aggregate(state, central, [demand_result], queue)
    assert json.loads(queue.read_text(encoding="utf-8"))["demands"][0]["status"] == "SATISFIED_BY_COMMON_COMPONENT"
    progress = json.loads(central.read_text(encoding="utf-8"))["integration_core"]["tool044_external_progress"]
    assert progress["REMAINING"] == 0 and progress["USER_MANUAL_RELAY_REQUIRED"] == 0


def test_verified_component_claims_multiple_independent_demands_in_one_batch(tmp_path: Path):
    row = component("SHARED-MATCHER")
    row.update(status="VERIFIED_REUSABLE", atomic_capabilities=["INPUT_CONTRACT_VALIDATION"])
    pool = tmp_path / "pool.json"; state = tmp_path / "state.json"; queue = tmp_path / "queue.json"
    pool.write_text(json.dumps({"components": [row]}), encoding="utf-8")
    queue.write_text(json.dumps({"demands": [
        {"demand_id": "DEMAND-A", "root_id": "ROOT-A", "status": "OPEN",
         "atomic_capabilities": ["INPUT_CONTRACT_VALIDATION"]},
        {"demand_id": "DEMAND-B", "root_id": "ROOT-B", "status": "OPEN",
         "atomic_capabilities": ["INPUT_CONTRACT_VALIDATION"]},
    ]}), encoding="utf-8")
    matrix = plan(pool, state, "RUN-BATCH", queue)
    assert len(matrix) == 2
    assert {row["job_id"].split("::")[1] for row in matrix} == {"DEMAND-A", "DEMAND-B"}
