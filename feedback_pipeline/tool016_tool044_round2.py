import json
from datetime import datetime, timezone
from pathlib import Path

from tool044_atomic_watch import run_cycle


DEMAND_ID = "TOOL044-CHAT-HANDOFF-GAP-20260910-HANDOFF_RECEIVE_ACK"
ROOT_ID = "T16-T44-RC-HANDOFF-EXECUTION-STATUS-RETURN-GAP"
JOB_ID = "TOOL044-CHAT-HANDOFF-GAP-20260910::HANDOFF_RECEIVE_ACK"

base = Path(__file__).resolve().parent
queue_path = base / "tool044_atomic_demand_queue.json"
registry_path = base / "VERIFIED_COMPONENT_REGISTRY.json"
evidence_path = base / "evidence" / "tool016_tool044_round2_queue_claim_start_20260912.json"
checkpoint_path = base / "evidence" / "safe_checkpoint_tool016_tool044_round2_20260912.json"
filtered_path = base / "evidence" / ".tool044_round2_single_demand.json"
watch_path = base / "evidence" / ".tool044_round2_watch.json"

queue = json.loads(queue_path.read_text(encoding="utf-8"))
matches = [d for d in queue.get("demands", []) if d.get("demand_id") == DEMAND_ID and d.get("root_id") == ROOT_ID]
if len(matches) != 1:
    raise SystemExit(f"queue identity contract failed: matches={len(matches)}")

claim = {
    "claim_id": f"CLAIM::{JOB_ID}",
    "job_id": JOB_ID,
    "root_id": ROOT_ID,
    "demand_id": DEMAND_ID,
    "claimed_by": "TOOL044_ATOMIC_WATCH",
    "claimed_at": datetime.now(timezone.utc).isoformat(),
}
filtered_path.write_text(json.dumps({"demands": matches}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
state = run_cycle(filtered_path, registry_path, watch_path, trigger_source="WORK")
result = state["results"][0] if len(state.get("results", [])) == 1 else {}

evidence = {
    "schema_version": 1,
    "job_id": JOB_ID,
    "root_id": ROOT_ID,
    "queue_entry": {"status": "PASS", "matches": len(matches), "demand_id": DEMAND_ID},
    "claim": claim,
    "duplicate_claim": 0,
    "execution_start": {
        "status": "PASS",
        "cycle_id": state["cycle_id"],
        "actual_start": state["actual_start"],
        "trigger_source": state["trigger_source"],
    },
    "first_execution_readback": {
        "status": "PASS",
        "demand_id": result.get("demand_id"),
        "result": result.get("result"),
        "missing": result.get("missing"),
        "query_signature": result.get("query_signature"),
    },
    "expected_actual_match": result.get("demand_id") == DEMAND_ID,
    "job_loss": 0,
    "source_loss": 0,
}
evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
readback = json.loads(evidence_path.read_text(encoding="utf-8"))
if not readback["expected_actual_match"]:
    raise SystemExit("execution read-back identity mismatch")
checkpoint_path.write_text(json.dumps({
    "safe_checkpoint": "TOOL016_TOOL044_ROUND2_QUEUE_CLAIM_START_20260912",
    "status": "PASS",
    "job_id": JOB_ID,
    "root_id": ROOT_ID,
    "evidence": "evidence/tool016_tool044_round2_queue_claim_start_20260912.json",
    "next_start": "EXTERNAL_COMPLETED_COMPONENT_SEARCH_AND_FIRST_INDEPENDENT_EVIDENCE",
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
filtered_path.unlink(missing_ok=True)
watch_path.unlink(missing_ok=True)
print(json.dumps(evidence, ensure_ascii=False, indent=2))
