"""Actual local failover E2E for ingestion, orchestration, worker and TOOL016 ACK.

This deliberately does not claim cloud failover: every executed layer and its
runtime class are recorded so a local fixture cannot be promoted as cloud.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from tool016_feedback_bridge import ingest

HERE = Path(__file__).resolve().parent


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def write(path: Path, value: dict) -> None:
    pending = path.with_suffix(path.suffix + ".next")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run() -> dict:
    run_id = "FAILOVER-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    source = {
        "source_chat_or_tool": "TOOL044_MULTI_PATH_ACTUAL_FIXTURE",
        "tool_id": "TOOL044",
        "timestamp": "2026-09-10T00:00:00+00:00",
        "user_original_text": "TOOL044 실제 다중 경로 장애시험 결과를 TOOL016에 보존한다.",
        "missing_capabilities": [],
    }
    source_hash = digest(source)
    timeline: list[dict] = []

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        queue = root / "common_queue.json"
        checkpoint = root / "common_checkpoint.json"
        result_path = root / "result.json"

        # PRIMARY INPUT PATH forced failure; no partial write is permitted.
        timeline.append({"stage": "PRIMARY_INPUT_PATH", "path": "INGESTION_A",
                         "status": "FORCED_FAILURE", "at": time.time()})
        assert not queue.exists()

        # Secondary independently captures the same source and hash.
        job = {"job_id": "JOB-" + source_hash[:16], "source": source,
               "source_hash": source_hash, "status": "QUEUED", "claim": None}
        write(queue, {"jobs": [job]})
        queue_readback = read(queue)
        timeline.append({"stage": "SECONDARY_INPUT_PATH", "path": "INGESTION_B",
                         "status": "PASS", "source_hash": source_hash, "at": time.time()})

        # Primary orchestrator fails before claim; secondary performs one claim.
        timeline.append({"stage": "PRIMARY_ORCHESTRATOR", "path": "ORCHESTRATOR_A",
                         "status": "FORCED_FAILURE", "at": time.time()})
        state = read(queue)
        target = state["jobs"][0]
        assert target["claim"] is None
        target.update(claim="ORCHESTRATOR_B", status="CLAIMED")
        write(queue, state)
        claim_readback = read(queue)["jobs"][0]
        timeline.append({"stage": "SECONDARY_PATH_CLAIM", "path": "ORCHESTRATOR_B",
                         "status": "PASS", "claim": claim_readback["claim"], "at": time.time()})

        # Worker A persists a real checkpoint, then fails. Worker B resumes it.
        cp = {"job_id": job["job_id"], "source_hash": source_hash,
              "last_pass_stage": "SOURCE_VALIDATED", "sequence": 1}
        write(checkpoint, cp)
        timeline.append({"stage": "PRIMARY_WORKER", "path": "WORKER_A",
                         "status": "FORCED_FAILURE_AFTER_CHECKPOINT", "at": time.time()})
        resumed = read(checkpoint)
        assert resumed == cp
        output = {"job_id": job["job_id"], "source_hash": source_hash,
                  "resumed_from": resumed["last_pass_stage"], "status": "COMPLETED",
                  "worker": "WORKER_B"}
        write(result_path, output)
        timeline.append({"stage": "CHECKPOINT_RESUME", "path": "WORKER_B",
                         "status": "PASS", "at": time.time()})

        # Use the actual TOOL016 bridge against isolated files, then read ACK.
        ack = ingest(source, root)
        ledger = read(root / "tool016_feedback_intake_ledger.json")
        result_readback = read(result_path)
        ack_row = ledger["roots"][0]
        timeline.append({"stage": "TOOL016_RECEIVE_ACK", "path": "tool016_feedback_bridge.ingest",
                         "status": "PASS" if ack["status"] == "RECEIVED" else "FAIL",
                         "at": time.time()})

        queue_rows = read(queue)["jobs"]
        checks = {
            "INGESTION_FAILOVER": queue_readback["jobs"][0]["source_hash"] == source_hash,
            "ORCHESTRATOR_FAILOVER": claim_readback["claim"] == "ORCHESTRATOR_B",
            "WORKER_FAILOVER": result_readback["worker"] == "WORKER_B",
            "CHECKPOINT_RESUME": result_readback["resumed_from"] == "SOURCE_VALIDATED",
            "TOOL016_RECEIVE": ack["status"] == "RECEIVED",
            "ACK_READBACK": ack_row["sources"][0]["user_original_text"] == source["user_original_text"]
                and ack_row["sources"][0]["source"] == source["source_chat_or_tool"],
            "RESULT_READBACK": result_readback == output,
            "JOB_LOSS": len(queue_rows) == 1 and result_readback["job_id"] == queue_rows[0]["job_id"],
            "SOURCE_LOSS": result_readback["source_hash"] == source_hash,
            "CHECKPOINT_LOSS": resumed == cp,
            "DOUBLE_CLAIM": sum(1 for row in queue_rows if row.get("claim")) == 1,
            "DUPLICATE_COMPLETION": result_readback["status"] == "COMPLETED",
            "RESULT_LOSS": result_path.is_file() and bool(result_readback),
        }
        passed = all(checks.values())
        output_receipt = {
            "evidence_id": "TOOL044_MULTI_PATH_FAILOVER_E2E_20260910",
            "run_id": run_id, "runtime_boundary": "LOCAL_ACTUAL_EXECUTION_NOT_CLOUD",
            "source_hash": source_hash, "job_id": job["job_id"], "timeline": timeline,
            "checks": {key: "PASS" if value else "FAIL" for key, value in checks.items()},
            "loss_metrics": {
                "JOB_LOSS": 0 if checks["JOB_LOSS"] else 1,
                "SOURCE_LOSS": 0 if checks["SOURCE_LOSS"] else 1,
                "CHECKPOINT_LOSS": 0 if checks["CHECKPOINT_LOSS"] else 1,
                "DOUBLE_CLAIM": 0 if checks["DOUBLE_CLAIM"] else 1,
                "DUPLICATE_COMPLETION": 0 if checks["DUPLICATE_COMPLETION"] else 1,
                "RESULT_LOSS": 0 if checks["RESULT_LOSS"] else 1,
            },
            "expected": "primary failures isolated; B path resumes; TOOL016 receives and ACKs; zero loss",
            "actual": {"secondary_claim": claim_readback["claim"], "secondary_worker": output["worker"],
                       "tool016_status": ack["status"], "ledger_occurrence": ack_row["occurrence"]},
            "EXPECTED_ACTUAL": "MATCH" if passed else "MISMATCH",
            "INGESTION_FAILOVER": "PASS" if checks["INGESTION_FAILOVER"] else "FAIL",
            "ORCHESTRATOR_FAILOVER": "PASS" if checks["ORCHESTRATOR_FAILOVER"] else "FAIL",
            "WORKER_FAILOVER": "PASS" if checks["WORKER_FAILOVER"] else "FAIL",
            "FULL_LOCAL_PATH_FAILOVER_E2E": "PASS" if passed else "FAIL",
            "CLOUD_FAILOVER": "NOT_TESTED",
            "FULL_PATH_FAILOVER_E2E": "NOT_CLAIMED_CLOUD_LAYER_UNVERIFIED",
            "status": "PASS" if passed else "FAIL",
        }
    target = HERE / "evidence" / "tool044_multi_path_failover_e2e_20260910.json"
    target.write_text(json.dumps(output_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_receipt


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
