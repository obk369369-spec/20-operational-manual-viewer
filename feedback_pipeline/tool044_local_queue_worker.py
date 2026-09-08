"""Claim TOOL044 LOCAL_REQUIRED jobs without allowing cloud/local duplicate execution."""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
QUEUE=HERE/"tool044_local_required_queue.json"

def save(value):
    pending=QUEUE.with_suffix(".json.next")
    pending.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    pending.replace(QUEUE)

def run():
    state=json.loads(QUEUE.read_text(encoding="utf-8")); now=datetime.now(timezone.utc).isoformat()
    for job in state.get("jobs",{}).values():
        if job.get("status")=="COMPLETED": continue
        if job.get("execution_class")!="LOCAL_REQUIRED":
            job.update(status="REJECTED",reason="NOT_LOCAL_REQUIRED"); continue
        target=HERE.parent/job["payload"]
        if not target.exists():
            job.update(status="FAILED",reason="PAYLOAD_MISSING"); continue
        job.update(status="COMPLETED",worker="OFFICE_LOCAL_TOOL044",completed_at=now,
                   result_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),cloud_executed=False)
    state.update(updated_at=now,queue_length=sum(j.get("status")!="COMPLETED" for j in state.get("jobs",{}).values()))
    save(state); return state

if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False))
