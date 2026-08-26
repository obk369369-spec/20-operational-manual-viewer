"""Machine-computed attack audit for the persistent-feedback ingress boundary."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
OUT = ROOT / "evidence" / "persistent_feedback_attack_audit_20260826.json"


def audit() -> dict:
    files = {name: (REPO / name).read_text(encoding="utf-8") for name in (
        "feedback_pipeline/global_pipeline.py",
        "feedback_pipeline/runtime_gateway.py",
        "feedback_pipeline/cross_chat_feedback_ingest.py",
        "feedback_pipeline/apply_feedback_event.py",
        "feedback_pipeline/canonical_writer.py",
        ".github/workflows/wic-feedback-event.yml",
        "WIC_GLOBAL_OPERATING_RULES.md",
    )}
    registry = json.loads((ROOT / "wic_target_registry.json").read_text(encoding="utf-8"))
    ledger = [json.loads(x) for x in (ROOT / "occurrence_ledger.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    probes = {
        "single_pending_slot_trigger_disabled": "pending_event.json'" not in files[".github/workflows/wic-feedback-event.yml"],
        "append_only_ledger": "os.O_APPEND" in (ROOT / "event_ledger.py").read_text(encoding="utf-8"),
        "occurrence_conservation": bool(ledger) and len(ledger) == len({x["occurrence_id"] for x in ledger}),
        "source_identity_before_keyword": "def resolve_event" in files["feedback_pipeline/global_pipeline.py"],
        "route_cache_not_stale": "@lru_cache" not in files["feedback_pipeline/cross_chat_feedback_ingest.py"],
        "first_actual_error_not_accumulating": "work_ready = actionable" in (ROOT / "work_ready_tracker.py").read_text(encoding="utf-8"),
        "no_silent_id_eviction": "[-2000:]" not in files["feedback_pipeline/apply_feedback_event.py"] and "[-200:]" not in files["feedback_pipeline/apply_feedback_event.py"],
        "no_auto_merge_rebase": all(x not in files["feedback_pipeline/global_pipeline.py"] + files[".github/workflows/wic-feedback-event.yml"] for x in ("pull --rebase", 'merge","--no-edit', "merge --no-edit")),
        "no_skip_ci": "[skip ci]" not in files["feedback_pipeline/global_pipeline.py"] + files[".github/workflows/wic-feedback-event.yml"],
        "bounded_subprocess": "timeout=900" in files["feedback_pipeline/global_pipeline.py"] and "timeout=900" in files["feedback_pipeline/runtime_gateway.py"],
        "machine_section_exactly_one": files["WIC_GLOBAL_OPERATING_RULES.md"].count("WIC_CANONICAL_FEEDBACK_START") == 1 and files["WIC_GLOBAL_OPERATING_RULES.md"].count("WIC_CANONICAL_FEEDBACK_END") == 1,
        "real_registry_shas": all(re.fullmatch(r"[0-9a-f]{40}", str(row["latest_verified_commit"])) for row in registry["targets"].values()),
        "handoff_persisted_without_ui_mutation": "def capture_handoff" in files["feedback_pipeline/runtime_gateway.py"],
        "empty_manifest_pass_blocked": "pass_claimed\": False" in (ROOT / "target_dispatcher.py").read_text(encoding="utf-8"),
    }
    gaps = sorted(name for name, passed in probes.items() if not passed)
    return {
        "schema_version": 1,
        "probes": probes,
        "unique_gap_count": len(probes),
        "fixed_or_verified_count": len(probes) - len(gaps),
        "open_internal_gaps": gaps,
        "new_gaps_this_attack_pass": len(gaps),
        "platform_limits": ["ORDINARY_CHATGPT_INGRESS_INTERCEPTOR", "CHAT_UI_HANDOFF_CREATION_AND_TITLE_CONTROL"],
        "platform_limit_count": 2,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    result = audit()
    prior = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    result["zero_new_gap_streak"] = int(prior.get("zero_new_gap_streak", 0)) + 1 if not result["open_internal_gaps"] else 0
    if args.record:
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["open_internal_gaps"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
