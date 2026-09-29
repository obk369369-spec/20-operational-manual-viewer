import tempfile
from pathlib import Path

from wic_non_tool_common_closeout import build, run

queue = {"demands": [
    {"demand_id": "done", "root_id": "COMMON-DONE", "target_tool": "CENTRAL",
     "residual_classification": "COMPLETE", "status": "PASS",
     "result_return": {"tool016_ack": "RECEIVED", "run_id": "1"}},
    {"demand_id": "retry", "root_id": "COMMON-RETRY", "target_tool": "TOOL044",
     "residual_classification": "UNFINISHED", "status": "READY_AUTO_REQUEUED",
     "atomic_capabilities": ["CAP"]},
    {"demand_id": "tool", "root_id": "TOOL013-X", "target_tool": "TOOL013",
     "residual_classification": "UNFINISHED"},
    {"demand_id": "legacy-central-tool", "root_id": "T42-LEGACY", "target_tool": "CENTRAL",
     "residual_classification": "UNFINISHED"},
]}
observer = {
    "GLOBAL_REQUIREMENT_RECONCILIATION_PROVEN": True,
    "STATUS_CLASSIFICATION_PROVEN": True,
    "DURABLE_OBSERVER_REPORT_WRITTEN": True,
    "NEXT_WORK_AUTO_SELECTED_AND_HANDED_OFF": True,
    "ALL_ACTIONABLE_UNFINISHED_AUTO_REQUEUED_WITHOUT_OBSERVER_INPUT": True,
    "TOOL016_RESULT_ACK_RECEIVED": 1,
    "REMOTE_GITHUB_READBACK_PASS": True,
    "observer_reinstruction_required": 0,
}
visible = {"CIRCULATION": {"dedup_gate": "PASS"}, "USER_MANUAL_RELAY_REQUIRED": 0}
gates = {"events": [{"event": "STALE_RECLAIM"}]}
ledger, packet = build(queue, observer, visible, gates, "2026-09-29T00:00:00+00:00")
assert len(ledger["requirements"]) == 9
assert ledger["not_worked_count"] == 0
assert ledger["cr_status"] == {f"CR-{n}": "COMPLETE" for n in range(1, 6)}
assert ledger["observer_reinstruction_required"] == 0 and ledger["manual_relay_count"] == 0
assert "COMMON-RETRY" in ledger["auto_requeued_roots"]
assert packet["next_root"] == "COMMON-RETRY"
assert all(row["requirement_id"] != "tool" for row in ledger["requirements"])
with tempfile.TemporaryDirectory() as raw:
    report_path = Path(raw)/"report.json"
    result = run(queue, observer, visible, gates, Path(raw)/"ledger.json", Path(raw)/"packet.json", report_path)
    assert result["counts"]["COMPLETE"] == 6
    report = __import__("json").loads(report_path.read_text())
    assert report["fixed_block_gate"] == "PASS" and report["missing_report_fields"] == []
    hold_ids = {row["requirement_id"] for row in report["PLATFORM_HOLD"]}
    assert hold_ids == {"PLATFORM-TOOL044-CHAT-REPORT-DELIVERY", "TOOL043-HOLD-REEVALUATE"}
print("WIC_NON_TOOL_COMMON_CLOSEOUT: PASS (12/12)")
