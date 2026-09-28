import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from wic_common_execution import ClaimStore, auto_register, execute_registered, integrate_component


def run():
    checks = {}
    with tempfile.TemporaryDirectory(prefix="wic-common-exec-") as raw:
        root = Path(raw)
        (root / "input.txt").write_text("wic", encoding="utf-8")
        queue = {"demands": []}
        contract = {
            "input": "input.txt",
            "output": "output.txt",
            "handler": ["{python}", "-c", "from pathlib import Path; Path(r'{output}').write_text(Path(r'{input}').read_text().upper())"],
            "expected": {"returncode": 0, "output_exists": True},
        }
        demand, created = auto_register(queue, {"demand_id": "REAL-DEMAND-1", "execution_contract": contract})
        _, duplicate_created = auto_register(queue, {"demand_id": "REAL-DEMAND-1", "execution_contract": contract})
        checks["auto_registration"] = created and not duplicate_created and len(queue["demands"]) == 1
        store = ClaimStore(root / "claims")
        first = store.claim("CLAIM-TEST", "A")
        second = store.claim("CLAIM-TEST", "B")
        checks["duplicate_claim_blocked"] = first["status"] == "CLAIMED" and second["status"] == "BLOCKED_CLAIMED"
        try:
            store.heartbeat("CLAIM-TEST", "B", first["fencing_token"])
            checks["fencing"] = False
        except PermissionError:
            checks["fencing"] = True
        store.release_for_resume("CLAIM-TEST", "A", first["fencing_token"], {"stage": "INTERRUPTED"})
        checks["checkpoint"] = any(store.recovery.glob("*.json"))
        resumed = store.claim("CLAIM-TEST", "B")
        checks["resume"] = resumed["status"] == "CLAIMED"
        store.release_for_resume("CLAIM-TEST", "B", resumed["fencing_token"], {"stage": "RESUMED"})
        result = execute_registered(demand, root, store, "RUNNER-A")
        checks["handler_execution"] = result["actual"]["returncode"] == 0
        checks["output_created"] = (root / "output.txt").read_text() == "WIC"
        checks["expected_actual"] = all(result["comparison"].values())
        checks["terminal_state"] = result["final_state"] == "PASS" and store.terminal("REAL-DEMAND-1").exists()
        checks["result_return"] = result["result_return"] == {"status": "PASS", "tool016_ack": "RECEIVED"}
        repeat = execute_registered(demand, root, store, "RUNNER-B")
        checks["completed_reselection_blocked"] = repeat["reason"] == "BLOCKED_COMPLETED"
        bad = {"demand_id": "REAL-DEMAND-FAIL", "execution_contract": {**contract, "handler": ["{python}", "-c", "raise SystemExit(7)"]}}
        failed = execute_registered(bad, root, store, "RUNNER-A")
        checks["failure_not_complete_and_checkpointed"] = (
            failed["final_state"] == "FAIL"
            and not store.terminal("REAL-DEMAND-FAIL").exists()
            and any(store.recovery.glob("*.json"))
        )
        (root / "stable.txt").write_text("OLD", encoding="utf-8")
        stable = integrate_component({"component_id": "STABLE-1", "target": "stable.txt",
            "channel": "STABLE", "execution_contract": {**contract, "output": "stable-output.txt"}},
            root, store, "RUNNER-A")
        checks["stable_deploy_and_readback"] = stable["deployed"] and stable["readback"] and (root / "stable.txt").read_text() == "WIC"
        (root / "stable.txt").write_text("KEEP", encoding="utf-8")
        next_result = integrate_component({"component_id": "NEXT-1", "target": "stable.txt",
            "channel": "NEXT", "execution_contract": {**contract, "output": "next-output.txt"}},
            root, store, "RUNNER-A")
        checks["stable_next_routing"] = next_result["route"] == "NEXT" and not next_result["deployed"] and (root / "stable.txt").read_text() == "KEEP"
        failed_component = integrate_component({"component_id": "ROLLBACK-1", "target": "stable.txt",
            "channel": "STABLE", "execution_contract": {**contract, "output": "bad-output.txt",
            "handler": ["{python}", "-c", "raise SystemExit(9)"]}}, root, store, "RUNNER-A")
        checks["failed_validation_rollback"] = failed_component["rollback"] and not failed_component["deployed"] and (root / "stable.txt").read_text() == "KEEP"
        checks["component_lifecycle_admission"] = stable["registered"] and next_result["registered"] and failed_component["registered"]
    return {"status": "PASS" if all(checks.values()) and len(checks) == 16 else "FAIL",
            "checks": checks, "passed": sum(checks.values()), "total": len(checks)}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
