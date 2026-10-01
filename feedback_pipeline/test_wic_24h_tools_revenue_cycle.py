import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
state = json.loads((root / "public/revenue-lab/state.json").read_text(encoding="utf-8"))
assert state["tool_inventory_count"] > 0
assert len(state["cycle_stages"]) == 12
assert {row["id"] for row in state["cycle_stages"]} == set("ABCDEFGHIJKL")
assert state["selected_pilot"] == "MANAGED_UPTIME_STATUS"
assert state["platform_discovery"]["candidates_found"] > 0
assert state["platform_discovery"]["pages_read"] > 0
assert state["revenue_stages"]["external_revenue_evidence"] == "PASS"
assert state["revenue_stages"]["actual_function"] == "PASS"
for key in ("customer_response", "lead", "order", "payment", "revenue"):
    assert state["revenue_stages"][key] == "WAITING"
assert state["financial_action_performed"] is False
assert state["observer_manual_action_required"] == 0
print("PASS: WIC 24h tools and revenue cycle, visible pilot, and honest revenue stages")
