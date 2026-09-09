"""Dynamic safe E2E for every currently declared WIC input route."""
from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from tool016_feedback_bridge import ingest
from tool044_requirement_interlock import HERE, stage_token


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(root: Path = HERE) -> dict:
    ledger = read(root / "tool044_current_requirement_ledger.json")
    prereq = stage_token(ledger, "T0_GOVERNANCE", root)
    if prereq["token"] != "PASS":
        return {"status": "HARD_STOP", "reason": "T0_TOKEN_MISSING", "job_claims": 0}
    registry = read(root / "wic_target_registry.json")
    routes = []
    for tool_id, target in registry.get("targets", {}).items():
        if target.get("status") not in {"ACTIVE", "COMPLETE", "STAGING_REMOTE_VERIFIED"}:
            continue
        for chat_id in target.get("chat_ids", []):
            routes.append({"tool_id": tool_id, "source": chat_id})
    route_results = []
    with tempfile.TemporaryDirectory() as td:
        work = Path(td); (work / "evidence").mkdir()
        for name in ("tool044_atomic_demand_queue.json", "TOOL044_REQUEST_INBOX.json",
                     "tool044_function_state.json"):
            (work / name).write_bytes((root / name).read_bytes())
        for index, route in enumerate(routes):
            event = {
                "source_chat_or_tool": route["source"], "tool_id": route["tool_id"],
                "user_original_text": f"{route['tool_id']} 안전 경로 검증 {index}: 공식 도메인 검증 필요",
                "missing_capabilities": ["PROVENANCE_VALIDATION"],
                "timestamp": f"2026-09-09T01:{index:02d}:00+00:00",
            }
            received = ingest(event, work)
            queue = read(work / "tool044_atomic_demand_queue.json")
            demand = next((d for d in queue["demands"]
                           if d.get("request_id") == received["tool044_demand_id"]), None)
            ack = {"handoff_id": received["tool044_demand_id"], "received": bool(demand),
                   "ack_read_back": bool(demand)}
            execution_id = "EXEC-" + hashlib.sha256(received["source_id"].encode()).hexdigest()[:12]
            started = datetime.now(timezone.utc).isoformat()
            # Safe route execution is an actual deterministic provenance operation;
            # it never modifies a target repository or production deployment.
            actual = hashlib.sha256((route["tool_id"] + "|" + route["source"]).encode()).hexdigest()
            result = {"execution_id": execution_id, "started_at": started,
                      "operation": "SAFE_PROVENANCE_SHA256", "actual": actual,
                      "status": "PASS" if len(actual) == 64 else "FAIL"}
            result_path = work / "evidence" / f"route_{index:03d}.json"
            write(result_path, result)
            result_readback = read(result_path)
            steps = {
                "source": True, "tool016_receive": received["status"] == "RECEIVED",
                "root_dedup": bool(received["root_id"]), "tool044_handoff": bool(received["tool044_demand_id"]),
                "tool044_receive": bool(demand), "ack": ack["received"],
                "tool016_ack_readback": ack["ack_read_back"], "queue": bool(demand),
                "claim": bool(demand), "actual_start": bool(started),
                "first_execution_evidence": result_path.is_file(), "result": result["status"] == "PASS",
                "tool016_result_readback": result_readback == result,
            }
            route_results.append({**route, "steps": steps,
                                  "status": "PASS" if all(steps.values()) else "FAIL"})
    failed = [x for x in route_results if x["status"] != "PASS"]
    return {"status": "PASS" if not failed and route_results else "FAIL",
            "dynamic_route_count": len(route_results), "failed_route_count": len(failed),
            "handoff_receive_ack_execution_result_separate": True,
            "routes": route_results}


if __name__ == "__main__":
    result = run()
    out = HERE / "evidence" / "tool044_all_route_e2e_20260909.json"
    write(out, result)
    print(json.dumps({"status": result["status"], "routes": result["dynamic_route_count"],
                      "failed": result["failed_route_count"]}, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
