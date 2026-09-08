"""Persistent TOOL016 function-state to TOOL044 factory handoff."""
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

def read(path, fallback):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else fallback

def save(path, value):
    pending = path.with_suffix(path.suffix + ".next")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)

def intake():
    source = read(HERE / "tool044_function_state.json", {})
    path = HERE / "tool044_factory_runtime.json"
    state = read(path, {"schema_version": 1, "jobs": {}, "last_failure": None})
    for demand in source.get("tool044_external_demand_candidates", []):
        identifier = "ZWF-" + hashlib.sha256(demand["demand_id"].encode()).hexdigest()[:16]
        old = state["jobs"].get(identifier, {})
        if old.get("status") == "COMPLETED": continue
        state["jobs"][identifier] = {"job_id": identifier, "source": "TOOL016_FUNCTION_STATE",
            "demand_id": demand["demand_id"], "missing_capabilities": demand["missing_capabilities"],
            "priority": demand["search_priority"], "status": old.get("status", "QUEUED"),
            "attempts": old.get("attempts", 0)}
    state.update(current_stage="INTAKE", queue_length=sum(x["status"] != "COMPLETED" for x in state["jobs"].values()),
                 updated_at=datetime.now(timezone.utc).isoformat())
    save(path, state); return state

def finalize():
    path = HERE / "tool044_factory_runtime.json"
    state = read(path, {"schema_version": 1, "jobs": {}, "last_failure": None})
    cycle = read(HERE / "evidence" / "tool044_atomic_watch_state.json", {})
    results = {x.get("demand_id"): x for x in cycle.get("results", [])}; now = datetime.now(timezone.utc).isoformat()
    mapping = {"READY_ATOMIC_COMPONENT_FOUND":"COMPLETED", "DUPLICATE_SEARCH_BLOCKED":"BACKOFF",
               "PARTIAL_ATOMIC_COMPONENT_SET":"WAITING_COMPONENT", "NO_READY_ATOMIC_COMPONENT":"WAITING_COMPONENT"}
    for job in state["jobs"].values():
        result = results.get(job["demand_id"])
        if not result: continue
        job.update(attempts=job["attempts"] + 1, last_result=result.get("result"), updated_at=now)
        job["status"] = mapping.get(result.get("result"), "FAILED")
        if job["status"] == "FAILED": state["last_failure"] = {"job_id":job["job_id"], "at":now}
    complete = sum(x["status"] == "COMPLETED" for x in state["jobs"].values())
    waiting = sum(x["status"] != "COMPLETED" for x in state["jobs"].values())
    state.update(current_stage="CHECKPOINT", queue_length=waiting, completed_jobs=complete, active_workers=0,
                 last_success=now if complete else state.get("last_success"), last_heartbeat=now,
                 checkpoint=cycle.get("cycle_id"), updated_at=now)
    save(path, state); return state

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("mode",choices=("intake","finalize")); a=p.parse_args()
    print(json.dumps(intake() if a.mode=="intake" else finalize(), ensure_ascii=False))
