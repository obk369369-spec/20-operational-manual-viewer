from wic_automatic_handoff import build

queue={"demands":[
 {"demand_id":"new","root_id":"R1","status":"OPEN","atomic_capabilities":["CAP"]},
 {"demand_id":"old","root_id":"R2","status":"OPEN","atomic_capabilities":["BIG","TWO"]},
 {"demand_id":"dup","root_id":"R1","status":"OPEN","atomic_capabilities":["CAP"]},
 {"demand_id":"same-root","root_id":"R2","status":"OPEN","atomic_capabilities":["OTHER"]},
 {"demand_id":"done","root_id":"R3","status":"PASS"},
 {"demand_id":"hold","root_id":"R4","status":"WAITING_24H"},
 {"demand_id":"TOOL043-X","root_id":"R5","status":"OPEN"},
]}
pool={"components":[{"status":"VERIFIED_REUSABLE","atomic_capabilities":["CAP"]}]}
gates={"jobs":{"j":{"JOB_ID":"j","STATUS":"PASS","RESULT":{"status":"PASS"},"OWNER":"GITHUB_ACTIONS:1:GATE_01"}}}
r=build(queue,pool,gates,"2026-09-30T00:00:00+00:00")
assert [x["demand_id"] for x in r["easy_queue"]]==["new"]
assert {x["demand_id"] for x in r["work_batch"]}=={"old","same-root"}
assert r["duplicates_removed"]==["dup"]
assert {x["demand_id"] for x in r["holds"]}=={"hold","TOOL043-X"}
assert r["next_easy_root"]=="R1" and r["observer_reinstruction_required"]==0
assert r["work_batch_full_threshold"]>=10 and not r["work_batch_full"]
assert r["anomalies"]=={"duplicate_demands":["dup"],"stalled_claims":[],"missing_results":[]}
# Negative gate: a PASS job without a result must never disappear from the audit.
bad=build({"demands":[]},pool,{"jobs":{"bad":{"JOB_ID":"bad","STATUS":"PASS"}}})
assert bad["anomalies"]["missing_results"]==["bad"]
print("WIC_AUTOMATIC_HANDOFF: PASS (10/10)")
