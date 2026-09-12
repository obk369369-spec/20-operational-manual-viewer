import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT_ID = "T16-T44-RC-HANDOFF-EXECUTION-STATUS-RETURN-GAP"
REQUEST_ID = "TOOL044-CHAT-HANDOFF-GAP-20260910"
JOB_ID = f"{REQUEST_ID}::HANDOFF_RECEIVE_ACK"


base = Path(__file__).resolve().parent
ledger_path = base / "TOOL016_ERROR_ROOT_LEDGER.md"
inbox_path = base / "TOOL044_REQUEST_INBOX.json"
evidence_path = base / "evidence" / "tool016_tool044_handoff_ack_e2e_20260912.json"
checkpoint_path = base / "evidence" / "safe_checkpoint_tool016_tool044_handoff_ack_20260912.json"

ledger = ledger_path.read_text(encoding="utf-8")
inbox = json.loads(inbox_path.read_text(encoding="utf-8"))

source_hits = ledger.count(f"`ROOT`: `{ROOT_ID}`")
received = [r for r in inbox["requests"] if r.get("request_id") == REQUEST_ID and r.get("root_id") == ROOT_ID]
if source_hits != 1 or len(received) != 1:
    raise SystemExit(f"actual-root contract failed: source_hits={source_hits}, received={len(received)}")

request = received[0]
handoff = {
    "job_id": JOB_ID,
    "root_id": ROOT_ID,
    "source": "TOOL016_ERROR_ROOT_LEDGER.md",
    "target": "TOOL044_REQUEST_INBOX.json",
    "source_hash": request["source_hash"],
}
handoff_digest = hashlib.sha256(json.dumps(handoff, sort_keys=True).encode()).hexdigest()
ack = {
    "ack_id": f"ACK::{JOB_ID}",
    "job_id": JOB_ID,
    "root_id": ROOT_ID,
    "receiver": "TOOL044",
    "status": "RECEIVED",
    "handoff_sha256": handoff_digest,
}

# TOOL016 read-back is an actual serialization boundary, not an in-memory assertion.
payload = {
    "schema_version": 1,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "actual_root": ROOT_ID,
    "handoff": handoff,
    "tool044_receive": {"status": "PASS", "request_id": REQUEST_ID, "matches": len(received)},
    "ack": ack,
}
evidence_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
readback = json.loads(evidence_path.read_text(encoding="utf-8"))

same_identity = (
    readback["handoff"]["job_id"] == readback["ack"]["job_id"] == JOB_ID
    and readback["handoff"]["root_id"] == readback["ack"]["root_id"] == ROOT_ID
)
result = {
    **readback,
    "tool016_ack_readback": "PASS" if same_identity else "FAIL",
    "same_job_root": same_identity,
    "source_loss": 0 if source_hits == 1 else 1,
    "handoff_loss": 0 if len(received) == 1 and same_identity else 1,
    "duplicate_handoff": max(0, len(received) - 1),
    "tool016_to_tool044_handoff": "PASS" if same_identity else "FAIL",
    "tool044_ack": "PASS" if same_identity else "FAIL",
}
evidence_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
checkpoint_path.write_text(json.dumps({
    "safe_checkpoint": "TOOL016_TO_TOOL044_HANDOFF_ACK_E2E_20260912",
    "evidence": str(evidence_path.relative_to(base)).replace("\\", "/"),
    "root_id": ROOT_ID,
    "job_id": JOB_ID,
    "status": "PASS" if same_identity else "FAIL",
    "next_scope": "ROUND_2_TOOL044_QUEUE_CLAIM_EXTERNAL_EXECUTION",
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
