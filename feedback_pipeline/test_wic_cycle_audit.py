from wic_cycle_audit import Timeline, atomic_demands, parallel_overlap, reconcile

text = """1. Collect every new error automatically
2. Merge duplicate root causes
3. Requeue every unfinished item
4. Verify remote execution evidence
"""
rows = atomic_demands(text)
assert len(rows) == 4
outcomes = {row["atomic_id"]: {"status": "COMPLETE", "evidence": "run:1"} for row in rows}
assert reconcile(rows, outcomes)["closeout_pass"]
bad = reconcile(rows, {key: value for key, value in outcomes.items() if key != "REQ-003"})
assert not bad["closeout_pass"] and bad["auto_requeue"] == ["REQ-003"]
assert not reconcile(rows, {**outcomes, "REQ-004": {"status": "COMPLETE"}})["closeout_pass"]
parallel = parallel_overlap([
    {"name": "lane-1", "started_at": "2026-09-30T01:00:00Z", "completed_at": "2026-09-30T01:00:10Z"},
    {"name": "lane-2", "started_at": "2026-09-30T01:00:02Z", "completed_at": "2026-09-30T01:00:11Z"},
])
assert parallel["parallel_proven"] and parallel["actual_parallel_count"] == 2
timeline = Timeline(); timeline.mark("collect"); timeline.mark("classify")
assert len(timeline.result()["stages"]) == 2
print("WIC_CYCLE_AUDIT: PASS (8/8)")
