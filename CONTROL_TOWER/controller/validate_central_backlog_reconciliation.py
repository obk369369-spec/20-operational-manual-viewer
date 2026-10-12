from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from github_runtime_cycle import reconcile_central_backlog


def main(output: str) -> int:
    root = Path(__file__).resolve().parents[2]
    ledger_path = root / "feedback_pipeline" / "unified_open_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    queue = {"queued_requirement_ids": []}
    result = reconcile_central_backlog(queue, ledger)
    expected = {
        "open_ledger_count": 6,
        "executable_count": 1,
        "deferred_count": 5,
        "next_root": "WIC-0702-SCOPED-RECOVERY",
        "pass_locked_reopened": 0,
    }
    comparison = {key: result.get(key) == value for key, value in expected.items()}
    evidence = {
        "schema": "wic.central-backlog-reconciliation.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "root_cause": "RUNTIME_NUMERIC_QUEUE_DRAINED_WHILE_CANONICAL_LEDGER_RETAINED_OPEN_ROOTS",
        "actual_input": str(ledger_path.relative_to(root)).replace("\\", "/"),
        "expected": expected,
        "actual": {key: result.get(key) for key in expected},
        "comparison": comparison,
        "selected": result["executable"],
        "deferred": result["deferred"],
        "positive_pass": result["next_root"] == expected["next_root"],
        "negative_pass": result["pass_locked_reopened"] == 0,
        "external_and_time_hold_pass": result["deferred_count"] == 5,
        "queue_writeback": queue,
        "overall": "PASS" if all(comparison.values()) else "FAIL",
    }
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    reread = json.loads(target.read_text(encoding="utf-8"))
    print(json.dumps({"overall": reread["overall"], "actual": reread["actual"],
                      "evidence_readback": reread == evidence}, ensure_ascii=False))
    return 0 if reread == evidence and evidence["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
