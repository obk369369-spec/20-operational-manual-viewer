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
    pool.write_text(json.dumps({"components": [component()]}), encoding="utf-8")
    central.write_text(json.dumps({"integration_core": {}}), encoding="utf-8")
    matrix = plan(pool, state, "RUN-1")
    assert len(matrix) == 1
    claimed = json.loads(state.read_text(encoding="utf-8"))["jobs"]["COMPONENT::READY-ONE"]
    assert claimed["STATUS"] == "CLAIMED" and claimed["CHECKPOINT"] == "CLAIM_DURABLE"
    result = tmp_path / "result.json"
    actual = run_lane(state, matrix[0]["job_id"], matrix[0]["owner"], result)
    assert actual["status"] == "PASS" and actual["production_mutation"] == 0
    merged = aggregate(state, central, [result])
    assert merged["jobs"][matrix[0]["job_id"]]["STATUS"] == "PASS"
    returned = json.loads(central.read_text(encoding="utf-8"))["integration_core"]["tool044_multi_gate"]
    assert returned["results_returned"] == 1


def test_incomplete_component_is_held(tmp_path: Path):
    row = component("INCOMPLETE"); del row["rollback_condition"]
    pool = tmp_path / "pool.json"; state = tmp_path / "state.json"
    pool.write_text(json.dumps({"components": [row]}), encoding="utf-8")
    assert plan(pool, state, "RUN-2") == []
    job = json.loads(state.read_text(encoding="utf-8"))["jobs"]["COMPONENT::INCOMPLETE"]
    assert job["STATUS"] == "HOLD" and job["RESULT"]["missing"] == ["rollback_condition"]


def test_failed_validator_runs_rollback(tmp_path: Path):
    row = component("ROLLBACK")
    row["validator"] = [sys.executable, "-c", "raise SystemExit(2)"]
    pool = tmp_path / "pool.json"; state = tmp_path / "state.json"
    pool.write_text(json.dumps({"components": [row]}), encoding="utf-8")
    matrix = plan(pool, state, "RUN-3")
    result = run_lane(state, matrix[0]["job_id"], matrix[0]["owner"], tmp_path / "result.json")
    assert result["status"] == "FAIL"
    assert result["rollback_pass"] is True
