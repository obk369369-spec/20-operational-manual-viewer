from chat_work_coordinator import route

def event(eid, job, status, action, remaining="", capability="", parent=None):
    row={"EVENT_ID":eid,"CHAT_JOB_ID":job,"RELATED_TOOL":"TOOL042","JOB_PURPOSE":"actual flow",
         "RESULT":status,"STATUS":status,"REMAINING_WORK":remaining,"ERROR":"err" if status in {"FAIL","PARTIAL","HOLD","REPEATED_ERROR","ACTUAL_USE_FAILURE"} else "",
         "NEXT_REQUIRED_CAPABILITY":capability,"NEXT_ACTION":action}
    if parent: row["PARENT_CHAT_JOB_ID"]=parent
    return row

events=[
 event("e1","chat-a","PASS","ZERO_WORK_EXECUTION","validate and deploy"),
 event("e2","chat-b","REPEATED_ERROR","TOOL044_DEMAND","repair","OFFICIAL_DOMAIN_VALIDATION"),
 event("e3","component-b","READY_FOR_INTEGRATION","CHAT_RESUME","",parent="chat-b"),
 event("e4","chat-c","HOLD","WORK_APPROVAL_REQUIRED","native chat action"),
]
s=route(events)
assert s["chat_auto_execution"]=="NOT_PROVEN"
assert s["counts"]=={"jobs":4,"zero_work_execution_queue":1,"tool016_error_root_intake":2,
 "tool044_request_demand_queue":1,"chat_resume_queue":1,"work_approval_queue":1}
assert s["work_approval_queue"][0]["APPROVED"] is False
assert route(events,s)["counts"]==s["counts"]
try: route([{"CHAT_JOB_ID":"bad"}])
except ValueError: pass
else: raise AssertionError("missing fields did not fail closed")
print("PASS: zero-work, TOOL016, TOOL044, resume, approval and idempotency routing")
