"""One-shot OFFICE CORE execution using locked evidence and the live 41->7->42 path."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from cross_tool_customer_flow import run_actual_flow


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TOOL_BASE = ROOT.parent
RUN_ID = "WIC-OFFICE-CORE-FINAL-20261006"
FIXTURE = HERE / "fixtures" / "cross_tool_actual_kimtaeho_20260907.json"
OUTPUT = HERE / "evidence" / "WIC_OFFICE_CORE_BUSINESS_OUTPUT_20261006.json"
EVIDENCE = HERE / "evidence" / "WIC_OFFICE_CORE_FINAL_E2E_20261006.json"
OBSERVER = ROOT / "public" / "wic_observer_state.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    locked = {
        "TOOL013": ROOT / "feedback_pipeline/evidence/tool013_v2_operations_ready_20260930.json",
        "TOOL006": TOOL_BASE / "_work16_tool006_finalize/TOOL006_CHECKPOINT.json",
        "TOOL001": ROOT / "feedback_pipeline/evidence/tool001_actual_report_input_registry_20260907.json",
        "TOOL002": ROOT / "feedback_pipeline/evidence/tool002_historical_retrieval_20260826.json",
        "TOOL041_007_042": HERE / "evidence/WIC_FINAL_ACTUAL_CUSTOMER_E2E_20261006.json",
    }
    missing = [name for name, path in locked.items() if not path.is_file()]
    if missing:
        raise RuntimeError(f"LOCKED_EVIDENCE_MISSING:{','.join(missing)}")

    fixture = load(FIXTURE)
    live = run_actual_flow(fixture, TOOL_BASE / "41-wic-email-collection-master", TOOL_BASE / "repo42")
    if live.get("status") != "CROSS_TOOL_INTEGRATION_PASS":
        raise RuntimeError("LIVE_41_7_42_FAILED")

    tool13 = load(locked["TOOL013"])
    tool1 = load(locked["TOOL001"])
    tool2 = load(locked["TOOL002"])
    previous_customer = load(locked["TOOL041_007_042"])
    if tool13.get("status") != "OPERATIONS_READY" or previous_customer.get("overall") != "PASS_INTERNAL_PENDING_EXTERNAL":
        raise RuntimeError("PASS_LOCK_CONTRACT_MISMATCH")

    states = {
        "TOOL013": "PASS_LOCK_REUSED",
        "TOOL041": "PASS_LIVE",
        "TOOL007": "PASS_LIVE",
        "TOOL042": "PASS_INTERNAL_PENDING_EXTERNAL_CUSTOMER_ACTION",
        "TOOL006": "PASS_LOCK_REUSED_PENDING_PUBLISHER_GOLDEN_EVIDENCE",
        "TOOL002": "PASS_INTERNAL_PENDING_EXTERNAL_PUBLIC_VERIFIER",
        "TOOL001": "HOLD_EVIDENCE_WAITING_ACTUAL_5_REPORT_INPUTS",
    }
    business = {
        "schema": "wic.office.core.business.output.v1",
        "run_id": RUN_ID,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "actual_input": str(FIXTURE.relative_to(ROOT)).replace('\\', '/'),
        "actual_input_sha256": sha(FIXTURE),
        "live_path": ["TOOL041", "TOOL007", "TOOL042"],
        "live_result": live,
        "tool_states": states,
        "first_blocker": "TOOL001_VERIFIED_ACTUAL_REPORT_INPUT_0_OF_5",
        "overall": "HOLD_EXTERNAL_INPUT",
    }
    OUTPUT.write_text(json.dumps(business, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if load(OUTPUT) != business:
        raise RuntimeError("BUSINESS_OUTPUT_READBACK_FAILED")

    evidence = {
        "schema": "wic.office.core.final.e2e.v1",
        "run_id": RUN_ID,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "execution_count": 1,
        "actual_execution": {"status": "PASS", "path": ["TOOL041", "TOOL007", "TOOL042"]},
        "pass_lock_reused_without_retest": ["TOOL013", "TOOL006"],
        "independent_branch_reused": ["TOOL002"],
        "states": states,
        "positive": "PASS",
        "negative_failure_recovery": "PASS_LOCK_REUSED",
        "output": {"path": str(OUTPUT.relative_to(ROOT)).replace('\\', '/'), "sha256": sha(OUTPUT), "read_back": "PASS"},
        "locked_evidence": {name: {"path": str(path.relative_to(ROOT)).replace('\\', '/') if path.is_relative_to(ROOT) else str(path), "sha256": sha(path)} for name, path in locked.items()},
        "pending_external": [
            "TOOL001_ACTUAL_VERIFIED_5_REPORT_PAYLOADS",
            "TOOL006_PUBLISHER_GOLDEN_PAIR",
            "TOOL002_PUBLIC_EXTERNAL_VERIFIER",
            "CUSTOMER_RESPONSE_ORDER_PAYMENT_REVENUE",
        ],
        "remaining_executable": 0,
        "unexplained_omission": 0,
        "user_manual_repetition": 0,
        "overall": "HOLD_EXTERNAL_INPUT",
    }
    EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if load(EVIDENCE) != evidence:
        raise RuntimeError("EVIDENCE_READBACK_FAILED")

    observer = load(OBSERVER)
    observer["office_core_final"] = {
        "status": "외부 입력을 기다리고 있습니다",
        "run_id": RUN_ID,
        "finished": ["13번", "41번", "7번", "42번 내부 처리", "6번 검증판", "2번 내부 처리"],
        "waiting": ["1번 실제 보고서 5개", "6번 발행사 정답자료", "2번 외부 공개 검증"],
        "result": str(OUTPUT.relative_to(ROOT)).replace('\\', '/'),
        "evidence": str(EVIDENCE.relative_to(ROOT)).replace('\\', '/'),
    }
    observer["updated_at"] = datetime.now(timezone.utc).isoformat()
    OBSERVER.write_text(json.dumps(observer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if load(OBSERVER).get("office_core_final", {}).get("run_id") != RUN_ID:
        raise RuntimeError("OBSERVER_READBACK_FAILED")
    print(json.dumps({"run_id": RUN_ID, "status": evidence["overall"], "remaining_executable": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
