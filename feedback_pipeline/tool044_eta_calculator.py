#!/usr/bin/env python3
"""Evidence-derived TOOL044 ETA calculator. Does not alter circulation state."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

QUEUE = Path(__file__).with_name("tool044_atomic_demand_queue.json")
PRIORITY = ["TOOL042", "TOOL041", "TOOL007", "TOOL013", "TOOL002"]
DONE = {"PASS", "VERIFIED_PASS", "SATISFIED_BY_COMMON_COMPONENT", "COMPLETE"}

def parse_time(v):
    if not v: return None
    try: return datetime.fromisoformat(v.replace("Z","+00:00"))
    except ValueError: return None

def tool_of(d):
    for r in d.get("source_records", []):
        t=r.get("TOOL_ID")
        if t: return t
    return d.get("tool") or d.get("target_tool")

def completed(d):
    return d.get("status") in DONE or d.get("residual_classification")=="COMPLETE" or d.get("result_return",{}).get("status")=="PASS"

def duration_hours(d):
    start=parse_time(d.get("claim",{}).get("claimed_at"))
    end=parse_time(d.get("completed_at") or d.get("satisfied_at") or d.get("result_return",{}).get("returned_at"))
    if start and end and end >= start:
        return (end-start).total_seconds()/3600
    return None

def calculate(data):
    rows=[]
    demands=data.get("demands",[])
    for rank,tool in enumerate(PRIORITY,1):
        ds=[d for d in demands if tool_of(d)==tool]
        total=len(ds); done=sum(completed(d) for d in ds); remaining=total-done
        samples=[duration_hours(d) for d in ds if completed(d)]
        samples=[x for x in samples if x is not None and x>0]
        throughput=(len(samples)/sum(samples)) if samples and sum(samples)>0 else None
        eta_hours=(remaining/throughput) if throughput else None
        if remaining==0 and total>0:
            status="ETA_COMPLETE"; eta_hours=0.0
        elif total==0:
            status="ETA_PENDING_NO_CONFIRMED_WORKLOAD"
        elif throughput is None:
            status="ETA_PENDING_INSUFFICIENT_EXECUTION_SAMPLE"
        else:
            status="ETA_CALCULATED"
        rows.append({"priority":rank,"tool":tool,"completed_atomic":done,"total_atomic":total,
                     "remaining_atomic":remaining,"throughput_atomic_per_hour":throughput,
                     "eta_active_hours":eta_hours,"status":status})
    return {"generated_at":datetime.now(timezone.utc).isoformat(),"priority_order":PRIORITY,"tools":rows}

if __name__=="__main__":
    print(json.dumps(calculate(json.loads(QUEUE.read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))
