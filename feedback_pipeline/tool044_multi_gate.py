"""Durable GitHub matrix gate for verified TOOL044 components.

The coordinator serializes planning, persists claims before execution, assigns
each job to one of 15 isolated lanes, and merges result artifacts afterwards.
External-provider adapters remain fail-closed until their credentials exist.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tool044_safe_integration import READY_COMPONENT_FIELDS

HERE = Path(__file__).resolve().parent
POOL = HERE / "evidence" / "tool044_verified_external_component_pool.json"
STATE = HERE / "evidence" / "tool044_multi_gate_state.json"
CENTRAL = HERE / "state.json"
QUEUE = HERE / "tool044_atomic_demand_queue.json"
MAX_GATES = 15
TERMINAL = {"PASS", "FAIL", "HOLD", "BLOCKED", "RETURNED"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def stamp(value: datetime) -> str:
    return value.isoformat()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".next")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)


def load(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def validate_component(component: dict) -> list[str]:
    return [field for field in READY_COMPONENT_FIELDS if not component.get(field)]


def expand_command(command: list[str], sandbox: Path) -> list[str]:
    values = {"python": sys.executable, "repo": str(HERE.parent), "sandbox": str(sandbox)}
    expanded = []
    for part in command:
        value = str(part)
        for key, replacement in values.items():
            value = value.replace("{" + key + "}", replacement)
        expanded.append(value)
    return expanded


def _components(pool: dict) -> list[dict]:
    return pool.get("components", []) + pool.get("verified_atomic_component_pool", [])


def build_plan(pool: dict, state: dict, run_id: str, now: datetime,
               queue: dict | None = None) -> tuple[dict, list[dict]]:
    jobs = state.setdefault("jobs", {})
    events = state.setdefault("events", [])
    for job in jobs.values():
        expiry = job.get("LEASE_EXPIRY")
        if job.get("STATUS") in {"CLAIMED", "RUNNING", "VALIDATING"} and expiry:
            if datetime.fromisoformat(expiry) <= now:
                job.update(STATUS="READY", OWNER=None, CLAIM_TIME=None, LEASE_EXPIRY=None)
                events.append({"event": "STALE_RECLAIM", "job_id": job["JOB_ID"], "at": stamp(now)})

    for component in _components(pool):
        component_id = component.get("component_id")
        if component.get("status") not in {"READY", "READY_FOR_INTEGRATION"} or not component_id:
            continue
        missing = validate_component(component)
        job_id = f"COMPONENT::{component_id}"
        if missing:
            jobs.setdefault(job_id, {
                "JOB_ID": job_id, "ROOT_ID": component.get("target_root"),
                "TARGET_TOOL": component.get("target_tool"), "COMPONENT_ID": component_id,
                "OWNER": None, "CLAIM_TIME": None, "LEASE_EXPIRY": None,
                "CHECKPOINT": "RECEIVED", "STATUS": "HOLD", "RETRY_COUNT": 0,
                "RESULT": {"reason": "COMPONENT_CONTRACT_INCOMPLETE", "missing": missing},
            })
            continue
        jobs.setdefault(job_id, {
            "JOB_ID": job_id, "ROOT_ID": component["target_root"],
            "TARGET_TOOL": component["target_tool"], "COMPONENT_ID": component_id,
            "OWNER": None, "CLAIM_TIME": None, "LEASE_EXPIRY": None,
            "CHECKPOINT": "RECEIVED", "STATUS": "READY", "RETRY_COUNT": 0,
            "RESULT": None, "COMPONENT": component,
        })

    # A component becomes reusable only after the prior isolated lane returned PASS.
    for job in jobs.values():
        if (job.get("JOB_ID", "").startswith("COMPONENT::") and
                job.get("STATUS") == "PASS" and job.get("RESULT", {}).get("status") == "PASS"):
            component_id = job.get("COMPONENT_ID")
            for component in _components(pool):
                if component.get("component_id") == component_id:
                    component["status"] = "VERIFIED_REUSABLE"
                    component["multi_gate_evidence"] = {
                        "job_id": job["JOB_ID"], "owner": job.get("OWNER"),
                        "checkpoint": job.get("CHECKPOINT"), "result": job.get("RESULT"),
                    }

    # Feed real unfinished atomic demands into the same verified-component lanes.
    capability_map = {
        capability: component
        for component in _components(pool) if component.get("status") == "VERIFIED_REUSABLE"
        for capability in component.get("atomic_capabilities", [])
    }
    for demand in (queue or {}).get("demands", []):
        if demand.get("status") in {"PASS", "COMPLETED", "SATISFIED_BY_COMMON_COMPONENT"}:
            continue
        capabilities = demand.get("atomic_capabilities", [])
        if len(capabilities) != 1 or capabilities[0] not in capability_map:
            continue
        component = capability_map[capabilities[0]]
        component_id = component["component_id"]
        demand_id = demand.get("demand_id")
        job_id = f"DEMAND::{demand_id}::{component_id}"
        jobs.setdefault(job_id, {
            "JOB_ID": job_id, "DEMAND_ID": demand_id, "ROOT_ID": demand.get("root_id") or demand_id,
            "TARGET_TOOL": demand.get("target_tool") or "CENTRAL", "COMPONENT_ID": component_id,
            "OWNER": None, "CLAIM_TIME": None, "LEASE_EXPIRY": None,
            "CHECKPOINT": "COMMON_COMPONENT_MATCHED", "STATUS": "READY", "RETRY_COUNT": 0,
            "RESULT": None, "COMPONENT": component,
        })

    ready = sorted((job for job in jobs.values() if job.get("STATUS") == "READY"),
                   key=lambda row: row["JOB_ID"])[:MAX_GATES]
    matrix = []
    for index, job in enumerate(ready, 1):
        gate_id = f"GATE_{index:02d}"
        owner = f"GITHUB_ACTIONS:{run_id}:{gate_id}"
        job.update(OWNER=owner, CLAIM_TIME=stamp(now),
                   LEASE_EXPIRY=stamp(now + timedelta(minutes=30)),
                   CHECKPOINT="CLAIM_DURABLE", STATUS="CLAIMED")
        matrix.append({"gate_id": gate_id, "job_id": job["JOB_ID"], "owner": owner})
    state.update(schema_version=1, updated_at=stamp(now), capacity=MAX_GATES,
                 active_claims=len(matrix), provider="GITHUB_ACTIONS")
    return state, matrix


def plan(pool_path: Path, state_path: Path, run_id: str, queue_path: Path = QUEUE) -> list[dict]:
    pool = load(pool_path, {"components": []})
    state, matrix = build_plan(pool, load(state_path, {"jobs": {}, "events": []}),
                               run_id, utcnow(), load(queue_path, {"demands": []}))
    atomic_json(pool_path, pool)
    atomic_json(state_path, state)
    return matrix


def run_lane(state_path: Path, job_id: str, owner: str, result_path: Path) -> dict:
    state = load(state_path, {"jobs": {}})
    job = state.get("jobs", {}).get(job_id)
    if not job or job.get("STATUS") != "CLAIMED" or job.get("OWNER") != owner:
        result = {"job_id": job_id, "status": "BLOCKED", "reason": "CLAIM_MISMATCH"}
        atomic_json(result_path, result)
        return result
    component = job["COMPONENT"]
    install = component.get("install_method")
    validator = component.get("validator")
    rollback = component.get("rollback_method")
    if not all(isinstance(command, list) and command for command in (install, validator, rollback)):
        result = {"job_id": job_id, "owner": owner, "status": "HOLD",
                  "reason": "EXECUTABLE_COMMAND_CONTRACT_REQUIRED"}
        atomic_json(result_path, result)
        return result
    with tempfile.TemporaryDirectory(prefix="wic-component-") as raw:
        sandbox = Path(raw)
        site = sandbox / "site"
        env = {**os.environ, "WIC_COMPONENT_SANDBOX": raw,
               "PYTHONPATH": str(site) + os.pathsep + os.environ.get("PYTHONPATH", "")}
        progress = {"job_id": job_id, "owner": owner, "status": "RUNNING",
                    "checkpoint": "FETCH_COMPLETE", "heartbeat": stamp(utcnow())}
        atomic_json(result_path, progress)
        installed = subprocess.run(expand_command(install, sandbox), cwd=raw, env=env,
                                   capture_output=True, text=True, timeout=600)
        validated = None
        if installed.returncode == 0:
            progress.update(checkpoint="INSTALL_COMPLETE", heartbeat=stamp(utcnow()))
            atomic_json(result_path, progress)
            validated = subprocess.run(expand_command(validator, sandbox), cwd=raw, env=env,
                                       capture_output=True, text=True, timeout=600)
        passed = installed.returncode == 0 and validated is not None and validated.returncode == 0
        rolled_back = None
        if not passed:
            rolled_back = subprocess.run(expand_command(rollback, sandbox), cwd=raw, env=env,
                                         capture_output=True, text=True, timeout=600)
        result = {
            "job_id": job_id, "owner": owner, "component_id": job["COMPONENT_ID"],
            "root_id": job["ROOT_ID"], "target_tool": job["TARGET_TOOL"],
            "status": "PASS" if passed else "FAIL",
            "checkpoint": "REGRESSION_COMPLETE" if passed else "ROLLBACK_COMPLETE",
            "install_returncode": installed.returncode,
            "validator_returncode": validated.returncode if validated else None,
            "rollback_returncode": rolled_back.returncode if rolled_back else None,
            "rollback_pass": rolled_back is None or rolled_back.returncode == 0,
            "heartbeat": stamp(utcnow()),
            "production_mutation": 0,
        }
    atomic_json(result_path, result)
    return result


def aggregate(state_path: Path, central_path: Path, result_paths: list[Path],
              queue_path: Path = QUEUE) -> dict:
    state = load(state_path, {"jobs": {}, "events": []})
    returned = 0
    for path in result_paths:
        result = load(path, {})
        job = state.get("jobs", {}).get(result.get("job_id"))
        if not job or result.get("owner") != job.get("OWNER"):
            continue
        job.update(STATUS=result["status"], CHECKPOINT=result.get("checkpoint", "RETURNED"),
                   RESULT=result, LEASE_EXPIRY=None)
        returned += 1
    state.update(updated_at=stamp(utcnow()), active_claims=0, results_returned=returned)
    atomic_json(state_path, state)
    queue = load(queue_path, {"demands": []})
    returned_demand_ids = {
        row.get("DEMAND_ID") for row in state.get("jobs", {}).values()
        if row.get("DEMAND_ID") and row.get("STATUS") == "PASS"
    }
    for demand in queue.get("demands", []):
        if demand.get("demand_id") in returned_demand_ids:
            demand.update(status="SATISFIED_BY_COMMON_COMPONENT",
                          satisfied_at=state["updated_at"],
                          satisfied_component=next(
                              row["COMPONENT_ID"] for row in state["jobs"].values()
                              if row.get("DEMAND_ID") == demand.get("demand_id")))
    atomic_json(queue_path, queue)
    central = load(central_path, {})
    core = central.setdefault("integration_core", {})
    core["tool044_multi_gate"] = {
        "updated_at": state["updated_at"], "capacity": MAX_GATES,
        "results_returned": returned,
        "jobs": {key: {field: row.get(field) for field in (
            "ROOT_ID", "TARGET_TOOL", "COMPONENT_ID", "STATUS", "CHECKPOINT", "RESULT")}
                 for key, row in state.get("jobs", {}).items()},
    }
    counts = {}
    for row in state.get("jobs", {}).values():
        counts[row.get("STATUS", "UNKNOWN")] = counts.get(row.get("STATUS", "UNKNOWN"), 0) + 1
    total_demands = len(queue.get("demands", []))
    remaining = sum(d.get("status") not in {"PASS", "COMPLETED", "SATISFIED_BY_COMMON_COMPONENT"}
                    for d in queue.get("demands", []))
    core["tool044_external_progress"] = {
        "TOTAL_DEMAND": total_demands, "READY": counts.get("READY", 0),
        "CLAIMED": counts.get("CLAIMED", 0), "RUNNING": counts.get("RUNNING", 0),
        "COMPONENT_FOUND": sum(bool(row.get("COMPONENT_ID")) for row in state.get("jobs", {}).values()),
        "VALIDATING": counts.get("VALIDATING", 0), "PASS": counts.get("PASS", 0),
        "FAIL": counts.get("FAIL", 0), "HOLD": counts.get("HOLD", 0),
        "RETURNED": returned, "REMAINING": remaining,
        "LAST_HEARTBEAT": state["updated_at"], "CURRENT_RUNNER": "GITHUB_ACTIONS",
        "CURRENT_COMPONENT": None, "RECENT_EVENT": "RESULTS_RETURNED_TO_TOOL016",
        "USER_MANUAL_RELAY_REQUIRED": 0,
    }
    atomic_json(central_path, central)
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--pool", type=Path, default=POOL); p.add_argument("--state", type=Path, default=STATE)
    p.add_argument("--queue", type=Path, default=QUEUE)
    p.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", "LOCAL")); p.add_argument("--github-output")
    r = sub.add_parser("run-lane")
    r.add_argument("--state", type=Path, default=STATE); r.add_argument("--job-id", required=True)
    r.add_argument("--owner", required=True); r.add_argument("--result", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--state", type=Path, default=STATE); a.add_argument("--central", type=Path, default=CENTRAL)
    a.add_argument("--queue", type=Path, default=QUEUE)
    a.add_argument("results", nargs="*", type=Path)
    args = parser.parse_args()
    if args.command == "plan":
        matrix = plan(args.pool, args.state, args.run_id, args.queue)
        payload = json.dumps({"include": matrix or [{"gate_id": "GATE_01", "job_id": "NOOP", "owner": "NOOP"}]})
        if args.github_output:
            with Path(args.github_output).open("a", encoding="utf-8") as handle:
                handle.write(f"matrix={payload}\nhas_jobs={'true' if matrix else 'false'}\n")
        print(payload)
    elif args.command == "run-lane":
        print(json.dumps(run_lane(args.state, args.job_id, args.owner, args.result)))
    else:
        print(json.dumps(aggregate(args.state, args.central, args.results, args.queue)))


if __name__ == "__main__":
    main()
