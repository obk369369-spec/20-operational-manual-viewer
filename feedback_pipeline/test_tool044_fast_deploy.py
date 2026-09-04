from __future__ import annotations

import argparse
import json
from pathlib import Path

from tool044_fast_deploy import FAST_DEPLOY_STAGES, plan


def main():
    p = argparse.ArgumentParser(); p.add_argument("--evidence", type=Path); a = p.parse_args()
    case1 = plan({"target_tool":"TOOL044","precheck":"SKIP_REUSE",
                  "local_result":"SKIP_REUSE","execution_mode":"LOCAL"})
    assert case1["status"] == "SKIP_REUSE" and case1["user_approval_count"] == 0

    case2 = plan({"target_tool":"TOOL001","precheck":"NO",
                  "local_result":"HOLD_EXTERNAL","execution_mode":"LOCAL"})
    assert case2["status"] == "HOLD_EXTERNAL" and case2["user_approval_count"] == 0

    ready = {"target_tool":"TOOL099","precheck":"YES","local_result":"LOCAL_READY",
             "execution_mode":"LOCAL","reuse_component":"VERIFIED_X",
             "work_handoff_required":"NO"}
    case3 = plan(ready)
    assert case3["status"] == "FAST_DEPLOY_READY" and case3["fast_deploy_stages"] == FAST_DEPLOY_STAGES
    assert case3["user_approval_count"] == 0

    required = [{"name":"network_push_and_deploy","platform_required":True},
                {"name":"remote_readback","platform_required":True}]
    case4 = plan(ready, required)
    assert case4["user_approval_count"] == 1 and len(case4["user_action_queue"]["actions"]) == 2

    mixed = required + [{"name":"unnecessary_confirmation","platform_required":False}]
    case5 = plan(ready, mixed)
    assert case5["user_approval_count"] == 1 and case5["avoidable_approval_count"] == 0
    assert case5["blocked_avoidable_action_count"] == 1
    # Avoidable actions are measured but never placed in the platform queue.
    assert len(case5["user_action_queue"]["actions"]) == 2

    work = plan({"target_tool":"TOOL099","precheck":"YES","local_result":"STOPPED_FOR_WORK_DECISION",
                 "execution_mode":"WORK_REQUIRED","work_handoff_required":"YES"})
    assert work["status"] == "WORK_DECISION_REQUIRED" and not work["fast_deploy_stages"]
    internal = plan({"target_tool":"TOOL099","precheck":"YES","local_result":"LOCAL_READY",
                     "execution_mode":"LOCAL","work_handoff_required":"NO","internal_wic_rule":True})
    assert internal["resolution_type"] == "C_INTERNAL_WIC_RULE" and not internal["fast_deploy_stages"]
    assert plan(ready) == plan(ready)
    result = {"CASE-1":case1,"CASE-2":case2,"CASE-3":case3,"CASE-4":case4,
              "CASE-5":case5,"boundary_work":work,"boundary_internal":internal,
              "expected_actual":"PASS","regression":"LOCAL_FIRST_UNCHANGED",
              "idempotency":"PASS"}
    if a.evidence:
        a.evidence.parent.mkdir(parents=True, exist_ok=True)
        a.evidence.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__": main()
