import json
import tempfile
from pathlib import Path

from tool016_visible_handoff import run


def write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


with tempfile.TemporaryDirectory() as raw:
    root = Path(raw)
    queue = root / "queue.json"
    pool = root / "pool.json"
    gates = root / "gates.json"
    central = root / "state.json"
    visible = root / "visible.json"
    observer = root / "observer.json"
    checkpoint = root / "checkpoint.json"
    write(queue, {"demands": [
        {"demand_id": "done", "status": "PASS", "result_return": {"tool016_ack": "RECEIVED"}},
        {"demand_id": "retry", "status": "RETURNED_FAIL", "atomic_capabilities": ["CAP"],
         "result_return": {"tool016_ack": "RECEIVED"}},
        {"demand_id": "missing", "status": "OPEN", "atomic_capabilities": ["NO_COMPONENT"]},
        {"demand_id": "platform", "status": "HOLD_EXTERNAL_AUTH"},
        {"demand_id": "time", "status": "WAITING_24H_NATURAL_RUN"},
    ]})
    write(pool, {"components": [{"status": "VERIFIED_REUSABLE", "atomic_capabilities": ["CAP"]}]})
    write(gates, {"jobs": {}, "capacity": 30})
    write(central, {})
    first = run(queue, pool, gates, central, visible, observer, checkpoint)
    report = json.loads(observer.read_text(encoding="utf-8"))
    updated = json.loads(queue.read_text(encoding="utf-8"))
    assert report["COMPLETE"] == ["done"]
    assert report["PARTIAL"] == ["retry"]
    assert report["UNFINISHED"] == ["missing"]
    assert report["PLATFORM_HOLD"] == ["platform"]
    assert report["LONG_TERM_HOLD"] == ["time"]
    assert report["AUTO_REQUEUED"] == ["retry"] and report["NEXT_WORK"] == "retry"
    retry = next(row for row in updated["demands"] if row["demand_id"] == "retry")
    assert retry["status"] == "READY_AUTO_REQUEUED" and retry["requeue_generation"] == 1
    run(queue, pool, gates, central, visible, observer, checkpoint)
    retry2 = next(row for row in json.loads(queue.read_text())["demands"] if row["demand_id"] == "retry")
    assert retry2["requeue_generation"] == 1
    assert first["USER_MANUAL_RELAY_REQUIRED"] == 0
    assert json.loads(checkpoint.read_text())["observer_reinstruction_required"] == 0
    print("ZERO_TOUCH_RESIDUAL_CIRCULATION: PASS (12/12)")
