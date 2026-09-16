"""Work execution enforcer: preserve the verified legacy audit and add mandatory automatic waste-plan admission."""
from __future__ import annotations
from work_execution_enforcer_legacy import *
from work_execution_enforcer_legacy import preflight_attempt as _legacy_preflight, main as _legacy_main, self_test as _legacy_self_test
from work_credit_waste_start_gate import enforce_start

def preflight_attempt(candidate: dict, ledger: dict) -> dict:
    waste = enforce_start(candidate)
    if not waste.get("allowed"):
        return {**waste, "execution_allowed": False, "missing_handoff": []}
    result = _legacy_preflight(candidate, ledger)
    if result.get("execution_allowed"):
        result = {**result, "waste_manual_sha256": waste["sha256"], "waste_instruction_scan": "PASS"}
    return result

def self_test() -> None:
    _legacy_self_test()
    blocked = preflight_attempt(
        {"instruction": "각 파일마다 하나씩 수정하고 commit push cloud run read-back을 반복한다"},
        {"entries": []},
    )
    assert blocked["decision"] == "STOP_WASTE_PLAN" and not blocked["execution_allowed"]
    clean = preflight_attempt(
        {"execution_goal": "전체 오류를 먼저 수집하고 원인별로 통합 수정 후 묶음 테스트"},
        {"entries": []},
    )
    assert clean["decision"] == "WORK_HOLD_SCOPE"
    print("PASS: legacy execution audit preserved + automatic waste gate enforced before scope")

def main() -> None:
    import sys
    if "--self-test" in sys.argv:
        self_test(); return
    _legacy_main()

if __name__ == "__main__":
    main()
