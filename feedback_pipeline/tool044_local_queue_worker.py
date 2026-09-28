"""Execute LOCAL_REQUIRED jobs only through the shared fail-closed contract."""
import json
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
QUEUE=HERE/"tool044_local_required_queue.json"
from wic_common_execution import ClaimStore, execute_registered

def save(value):
    pending=QUEUE.with_suffix(".json.next")
    pending.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    pending.replace(QUEUE)

def run():
    state=json.loads(QUEUE.read_text(encoding="utf-8")); now=datetime.now(timezone.utc).isoformat()
    store=ClaimStore(HERE/"evidence"/"shared_claim_store")
    for job in state.get("jobs",{}).values():
        if job.get("status")=="COMPLETED": continue
        if job.get("execution_class")!="LOCAL_REQUIRED":
            job.update(status="REJECTED",reason="NOT_LOCAL_REQUIRED"); continue
        result=execute_registered(job, HERE.parent, store, "OFFICE_LOCAL_TOOL044")
        if result.get("final_state")=="PASS":
            job.update(status="COMPLETED",worker="OFFICE_LOCAL_TOOL044",completed_at=now,
                       execution_result=result,cloud_executed=False)
        else:
            job.update(status=result.get("final_state","HOLD"),reason=result.get("reason"),
                       execution_result=result,cloud_executed=False)
    state.update(updated_at=now,queue_length=sum(j.get("status")!="COMPLETED" for j in state.get("jobs",{}).values()))
    save(state); return state

if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False))
