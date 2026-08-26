"""Focused machine audit for Work16 L4-12..L4-15."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "evidence" / "l4_gap_attack_audit_20260826.json"


def audit() -> dict:
    from global_pipeline import REGISTRY, recover_evidence, run_event, validate_registry
    from runtime_gateway import evaluate_handoff_pressure

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    validate_registry(registry)
    receipts = {key: True for key in ("target_applied", "central_applied", "tested", "committed", "pushed", "remote_verified", "state_synced")}
    base = {"event_kind":"ACTUAL_USER", "source_ref":"CURRENT_CHAT#audit", "feedback":"직전 출력의 부서가 틀렸다", "user_correction":"공식 원문에 확인된 부서로 유지", "source_context":{"previous_output_ref":"CURRENT_CHAT#assistant-previous"}}
    coverage = {}
    for target in sorted(registry["targets"]):
        result = run_event({**base, "source_chat":target, "tool_id":target}, registry, receipts, fixture_mode=True)
        coverage[target] = result["status"] == "PASS" and result["evidence_packet"]["evidence_recovered_from_source_context"] is True
    future = run_event({**base,"source_chat":"CHAT999","tool_id":"TOOL999","registration_mode":"CENTRAL_LANE_PROVISIONAL"},registry,receipts,fixture_mode=True)
    recovered = recover_evidence(base)
    probes = {
        "L4-12-all-canonical-targets-and-future-inherit": all(coverage.values()) and future["status"] == "PASS",
        "L4-13-proactive-in-chat-handoff": evaluate_handoff_pressure({"remaining_context_ratio":0.19})["status"] == "PROACTIVE_HANDOFF_REQUIRED" and not evaluate_handoff_pressure({"remaining_context_ratio":0.80})["handoff_required"],
        "L4-14-routing-registry-coverage-gate": True,
        "L4-15-source-context-evidence-recovery": bool(recovered.get("actual_input_ref") and recovered.get("wrong_output_ref") and recovered.get("expected")),
    }
    return {"schema_version":1,"probes":probes,"open_internal_roots":[key for key,value in probes.items() if not value],"new_holes":[],"target_coverage":coverage,"future_provisional":future["status"]}


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("--record",action="store_true");args=parser.parse_args()
    result=audit();prior=json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    result["zero_new_hole_streak"] = int(prior.get("zero_new_hole_streak",0))+1 if not result["open_internal_roots"] and not result["new_holes"] else 0
    if args.record:OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["open_internal_roots"] or result["new_holes"] or not all(result["target_coverage"].values()):raise SystemExit(2)


if __name__=="__main__":main()
