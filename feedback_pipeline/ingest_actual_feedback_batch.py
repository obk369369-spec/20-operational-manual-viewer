from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from work_ready_tracker import assess_work_ready, update_work_ready_state

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state.json"
BATCH = ROOT / "actual_feedback_batch_20260825.json"
REGISTRY = ROOT / "wic_target_registry.json"


def run(state_path: Path = STATE, batch_path: Path = BATCH, registry_path: Path = REGISTRY) -> dict[str, Any]:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    active = {tool for tool, row in registry["targets"].items() if row["status"] == "ACTIVE"}
    integration = dict(state.get("integration_core", {}))
    roots = dict(integration.get("actual_feedback_roots", {}))
    seen = set(integration.get("actual_occurrence_ids", []))
    inserted = 0
    skipped = 0
    for event in batch["events"]:
        assert event["event_kind"] == "ACTUAL_USER"
        if event["tool"] not in active:
            raise ValueError(f"unregistered or inactive WIC target: {event['tool']}")
        occurrence_id = event["occurrence_id"]
        if occurrence_id in seen:
            skipped += 1
            continue
        root_id = event["root_cause_id"]
        previous = dict(roots.get(root_id, {}))
        recur_count = int(previous.get("recur_count", 0)) + 1
        assessment = assess_work_ready(
            root_cause_id=root_id,
            text=event["text"],
            recur_count=recur_count,
            classification="NEW_FIXTURE",
        )
        assessment.update({
            "tool": event["tool"],
            "event_kind": "ACTUAL_USER",
            "latest_occurrence_id": occurrence_id,
            "last_observed_at": event["observed_at"],
            "count_status": event["count_status"],
            "fixture_or_test_counted": False,
        })
        roots[root_id] = assessment
        integration = update_work_ready_state(integration, assessment)
        seen.add(occurrence_id)
        inserted += 1
    integration["actual_feedback_roots"] = roots
    integration["actual_occurrence_ids"] = sorted(seen)
    integration["actual_feedback_summary"] = {
        "root_count": len(roots),
        "by_tool": {
            tool: sum(1 for item in roots.values() if item["tool"] == tool)
            for tool in sorted({item["tool"] for item in roots.values()})
        },
        "fixture_or_test_events_counted": 0,
    }
    state["integration_core"] = integration
    state["last_context_cursor"] = max(event["observed_at"] for event in batch["events"])
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    read_back = json.loads(state_path.read_text(encoding="utf-8"))
    assert read_back["integration_core"]["actual_feedback_summary"]["by_tool"] == integration["actual_feedback_summary"]["by_tool"]
    assert read_back["integration_core"]["actual_feedback_summary"]["fixture_or_test_events_counted"] == 0
    return {"result":"PASS", "inserted":inserted, "skipped":skipped, "roots":len(roots),
            "by_tool": integration["actual_feedback_summary"]["by_tool"]}


def main() -> None:
    print(json.dumps(run(), ensure_ascii=False))


if __name__ == "__main__":
    main()
