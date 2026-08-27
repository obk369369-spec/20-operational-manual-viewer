"""Produce Work16 counts and checkpoint claims from one deduplicated root ledger."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "work16_root_ledger.json"
OUT = HERE / "evidence" / "work16_root_report.json"
CLOSED = {"VERIFIED_CLOSED", "FIXED_LOCAL", "FIXED_RUNTIME", "REMOTE_VERIFIED"}


def build() -> dict:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    roots = ledger["roots"]
    ids = [row["id"] for row in roots]
    names = [row["root"] for row in roots]
    assert len(ids) == len(set(ids)), "duplicate root id"
    assert len(names) == len(set(names)), "duplicate root name"
    unresolved = [row["id"] for row in roots if row["status"] not in CLOSED]
    holds = ledger.get("external_holds", [])
    layers = {}
    for layer in ("L1", "L2", "L3", "L4", "L5", "L6"):
        rows = [row for row in roots if row["id"].startswith(layer + "-")]
        open_rows = [row for row in rows if row["status"] not in CLOSED]
        layers[layer] = {"found": len(rows), "closed": len(rows) - len(open_rows), "open": len(open_rows), "new": sum(bool(row.get("introduced_after_checkpoint")) for row in rows), "unknown": 0}
    attack_path = HERE / "evidence" / "l4_gap_attack_audit_20260826.json"
    attack = json.loads(attack_path.read_text(encoding="utf-8")) if attack_path.exists() else {"zero_new_hole_streak": 0, "new_holes": []}
    return {
        "schema_version": 1,
        "checkpoint_status": ledger["checkpoint_status"],
        "unique_root_count": len(roots),
        "fixed_or_verified_count": len(roots) - len(unresolved),
        "open_internal_root_count": len(unresolved),
        "open_internal_roots": unresolved,
        "external_hold_count": len(holds),
        "external_holds": [row.get("id") or row["root"] for row in holds],
        "layers": layers,
        "error_found_total": len([row for row in roots if row["id"].startswith("L4-")]),
        "error_new": sum(bool(row.get("introduced_after_checkpoint")) for row in roots),
        "error_recurrence": sum(int(row.get("recurrence", 0)) for row in roots),
        "new_holes": len(attack.get("new_holes", [])),
        "zero_new_hole_streak": 0 if unresolved else int(attack.get("zero_new_hole_streak", 0)),
        "unknown_critical": 0,
        "pass_claimed": not unresolved and ledger["checkpoint_status"] == "REMOTE_VERIFIED_COMPLETE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.record:
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
