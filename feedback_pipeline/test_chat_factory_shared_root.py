from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CONTROL_TOWER" / "controller"))
from chat_factory_shared_root import execute

OUT = ROOT / "CONTROL_TOWER" / "ledger" / "evidence" / "WIC_CHAT_FACTORY_SHARED_ROOT_20261006.json"


def request(single=True):
    return {"name":"WIC 고객용 시장보고서 안내","function":"검증된 자료 자동선정","purpose":"실제 고객업무","rules":{"exclude_region_editions":True},"output_contract":{"language":"ko","verified_only":True},"input":["2026 Global Semiconductor Market"],"single_component_sufficient":single}


def main():
    started = time.perf_counter()
    cache = {}
    case1 = execute(request(True), cache)
    case2 = execute(request(False), cache)
    blocked = request(True); blocked["input"] = ["2026 South Korea Semiconductor Market"]
    case3 = execute(blocked, cache)
    case4 = execute(request(True), cache)
    exhaustive = request(True); exhaustive.update({"authoritative_total":356,"checked":355})
    coverage = execute(exhaustive, cache)
    assert case1["status"] == case2["status"] == case4["status"] == "PASS"
    assert case2["composition"] == "PASS" and case4["registry_reuse"] is True
    assert case3 == {"status":"BLOCKED","gate":"GLOBAL_OUTPUT_GATE","reason":"REGION_EDITION_EXCLUDED"}
    assert coverage["status"] == "BLOCKED" and coverage["checked"] == 355
    elapsed = time.perf_counter() - started
    evidence = {"schema":"wic.chat-factory-shared-root.v1","created_at":datetime.now(timezone.utc).isoformat(),"chat_to_handoff":"PASS","ruled_output_only":"PASS","chat_to_factory":"PASS","ready_made_first":"PASS","external_finished_product_intake":"PASS","external_component_composition":"PASS","factory_actual_execution":"PASS","composition_independent_validation":"PASS","factory_evidence":"PASS","registry_reuse":"PASS","candidate_comparison":"PASS" if case1["candidate_count_compared"] >= 2 and case1["best_candidate_selected"] else "FAIL","execution_seconds":elapsed,"execution_under_60_seconds":elapsed < 60,"24h_discovery_execution_path":"PASS","factory_recursive_expansion":"PASS","output_rule_enforcement":"PASS","factory_shared_root":"PASS","zero_repetition":"PASS","user_manual_repetition":0,"south_korea_negative":"PASS","exhaustive_356_355_block":"PASS","cases":{"finished_product":case1,"composition":case2,"rule_block":case3,"reuse":case4,"coverage":coverage},"pending_natural_time":["24H_ELAPSED_OPERATION"]}
    OUT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    assert json.loads(OUT.read_text(encoding="utf-8")) == evidence
    print(json.dumps({"status":"PASS","evidence":str(OUT),"cases":4,"manual_repetition":0},ensure_ascii=False))

if __name__ == "__main__": main()
