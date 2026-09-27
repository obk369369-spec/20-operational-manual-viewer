"""Automatically detect final external triggers without converting absence into PASS."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

TRIGGERS = {
    "LIBRARY_SOURCE_BYTES": "WIC_LIBRARY_MOUNT_EVIDENCE_PATH",
    "VERIFIED_REPORT_PAYLOADS": "WIC_VERIFIED_REPORT_EVIDENCE_PATH",
    "INDEPENDENT_VERIFIER": "WIC_EXTERNAL_VERIFIER_EVIDENCE_PATH",
    "CONTROL_TOWER_RUNTIME": "WIC_CONTROL_TOWER_EVIDENCE_PATH",
    "INDEPENDENT_ENV2": "WIC_ENV2_EVIDENCE_PATH",
}


def evaluate(unattended_verdict: dict, environ: dict | None = None) -> dict:
    env = environ if environ is not None else os.environ
    children = {}
    for target, variable in TRIGGERS.items():
        raw = env.get(variable, "")
        ready = bool(raw and Path(raw).is_file() and Path(raw).stat().st_size > 0)
        children[target] = {"status": "READY" if ready else "HOLD", "trigger": variable,
                            "evidence": raw if ready else None}
    external_ready = [target for target, row in children.items() if row["status"] == "READY"]
    elapsed_ready = unattended_verdict.get("status") == "PASS"
    queue = external_ready + (["ACTUAL_24H_SCHEDULE_CONTINUITY"] if elapsed_ready else [])
    return {
        "schema_version": 1, "updated_at": datetime.now(timezone.utc).isoformat(),
        "external_root_status": "PASS" if len(external_ready) == len(TRIGGERS) else
                                ("READY_PARTIAL" if external_ready else "HOLD"),
        "elapsed_time_status": "PASS" if elapsed_ready else "WAITING",
        "children": children, "automatic_resume_queue": queue,
        "automatic_resume_required": bool(queue), "user_manual_relay_required": False,
        "fake_pass_forbidden": True,
    }


def persist(path: Path, unattended_verdict: dict, environ: dict | None = None) -> dict:
    result = evaluate(unattended_verdict, environ)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
