"""Independent read-back of already verified component/warehouse evidence."""
from __future__ import annotations
import json
from pathlib import Path
from tool044_requirement_interlock import HERE, sha256

def read(name): return json.loads((HERE / name).read_text(encoding="utf-8"))

def run():
    ready=read("evidence/tool044_stage3_ready_component_validation_20260909.json")
    growth=read("evidence/tool044_component_growth_20260909.json")
    reuse=read("evidence/tool044_grown_component_reuse_20260909.json")
    speed=read("evidence/tool044_warehouse_speed_20260909.json")
    registry=read("VERIFIED_COMPONENT_REGISTRY.json")
    pool=read("evidence/tool044_verified_composition_pool.json")
    atomic={x.get("component_id") for x in registry.get("components",[])+registry.get("verified_atomic_component_pool",[])
            if x.get("status")=="VERIFIED_REUSABLE"}
    compositions=[x for x in pool.get("compositions",[]) if "VERIFIED" in str(x.get("status",""))]
    t2_checks={
        "parents_receipt_actual": all(x.get("receipt_actual")=="MATCH" for x in ready["parents"]),
        "parents_sandbox": all(x.get("sandbox")=="PASS" for x in ready["parents"]),
        "normal_failure_regression": all(ready["composition"].get(k)=="PASS" for k in
              ("normal_fixture","failure_fixture","parent_function_regression","composition_regression")),
        "no_ready_is_demand_only": ready["gate_correction"].get("factory_hold") is False,
        "invalid_not_promoted": all(x.get("status")=="VERIFIED_REUSABLE" for x in
              registry.get("verified_atomic_component_pool",[])),
    }
    t3_checks={
        "atomic_12": len(atomic)==12, "composition_3": len(compositions)==3,
        "recursive_growth": growth.get("result")=="COMPONENT_GROWTH_PASS",
        "largest_reuse": reuse.get("result") in {"PASS","GROWN_COMPONENT_REUSE_PASS"},
        "effect": speed.get("result")=="PASS" and speed["reuse"]["reuse_hit_rate"]>0
                  and speed["speed"]["throughput_improvement_percent"]>0,
        "production_unchanged": growth.get("production_changed") is False and speed.get("production_changed") is False,
    }
    result={"status":"PASS" if all(t2_checks.values()) and all(t3_checks.values()) else "FAIL",
            "T2_COMPONENT_INTEGRITY":{"status":"PASS" if all(t2_checks.values()) else "FAIL","checks":t2_checks},
            "T3_LARGE_WAREHOUSE":{"status":"PASS" if all(t3_checks.values()) else "FAIL","checks":t3_checks},
            "source_receipts": {p:sha256(HERE/p) for p in (
                "evidence/tool044_stage3_ready_component_validation_20260909.json",
                "evidence/tool044_component_growth_20260909.json",
                "evidence/tool044_grown_component_reuse_20260909.json",
                "evidence/tool044_warehouse_speed_20260909.json",
                "VERIFIED_COMPONENT_REGISTRY.json","evidence/tool044_verified_composition_pool.json")}}
    out=HERE/"evidence"/"tool044_existing_stage_readback_20260909.json"
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    result=run(); print(json.dumps(result,ensure_ascii=False)); raise SystemExit(0 if result["status"]=="PASS" else 1)
