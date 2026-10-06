"""Execute the preserved real WIC customer record through the existing 41→7→42 path."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from cross_tool_customer_flow import run_actual_flow

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TOOL_BASE = ROOT.parent
INPUT = HERE / "fixtures" / "cross_tool_actual_kimtaeho_20260907.json"
OUTPUT = HERE / "evidence" / "WIC_FINAL_ACTUAL_CUSTOMER_OUTPUT_20261006.json"
EVIDENCE = HERE / "evidence" / "WIC_FINAL_ACTUAL_CUSTOMER_E2E_20261006.json"
OBSERVER = ROOT / "public" / "wic_observer_state.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def jsha(value: object) -> str:
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())


def main() -> None:
    actual = json.loads(INPUT.read_text(encoding="utf-8"))
    positive = run_actual_flow(actual, TOOL_BASE / "41-wic-email-collection-master", TOOL_BASE / "repo42")
    assert positive["status"] == "CROSS_TOOL_INTEGRATION_PASS"

    bad = json.loads(json.dumps(actual, ensure_ascii=False))
    bad["history"]["contact_history_verified"] = False
    negative = run_actual_flow(bad, TOOL_BASE / "41-wic-email-collection-master", TOOL_BASE / "repo42")
    assert negative["status"] == "HOLD" and negative["first_blocker"] == "TOOL007_HANDOFF_REJECTED"

    failure = run_actual_flow(actual, TOOL_BASE / "41-wic-email-collection-master", TOOL_BASE / "__missing_tool42_runtime__")
    assert failure["status"] == "FAIL" and failure["first_blocker"] == "TOOL042_RUNTIME_ERROR"
    recovery = run_actual_flow(actual, TOOL_BASE / "41-wic-email-collection-master", TOOL_BASE / "repo42")
    assert jsha(recovery) == jsha(positive)

    business_output = {
        "schema": "wic.actual.customer.output.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_sha256": sha(INPUT.read_bytes()),
        "result_sha256": jsha(positive),
        "workflow_status": positive["status"],
        "external_customer_action": "PENDING_EXTERNAL",
        "external_send_executed": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(business_output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert json.loads(OUTPUT.read_text(encoding="utf-8")) == business_output

    observer = json.loads(OBSERVER.read_text(encoding="utf-8-sig"))
    observer["final_actual_wic_e2e"] = {
        "status": "PASS_INTERNAL_PENDING_EXTERNAL",
        "evidence": "customer_pipeline/evidence/WIC_FINAL_ACTUAL_CUSTOMER_E2E_20261006.json",
        "business_output": "customer_pipeline/evidence/WIC_FINAL_ACTUAL_CUSTOMER_OUTPUT_20261006.json",
        "external_customer_action": "PENDING_EXTERNAL",
    }
    OBSERVER.write_text(json.dumps(observer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    surfaced = json.loads(OBSERVER.read_text(encoding="utf-8"))["final_actual_wic_e2e"]["status"] == "PASS_INTERNAL_PENDING_EXTERNAL"
    assert surfaced

    evidence = {
        "schema": "wic.final_actual_customer_e2e.v2",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": "WIC-FINAL-ACTUAL-20261006",
        "input": {"path": str(INPUT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(INPUT.read_bytes()), "class": "PRESERVED_ACTUAL_WIC_CUSTOMER_RECORD"},
        "path": ["TOOL041", "TOOL007", "TOOL042"],
        "positive": {"status": "PASS", "result_sha256": jsha(positive)},
        "negative": {"status": "PASS", "blocked_as": negative["first_blocker"]},
        "failure": {"status": "PASS", "blocked_as": failure["first_blocker"]},
        "retry_recovery_rollback": {"status": "PASS", "deterministic": True, "result_sha256": jsha(recovery)},
        "business_output": {"status": "PASS", "path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(OUTPUT.read_bytes())},
        "observer_surface": {"status": "PASS", "path": str(OBSERVER.relative_to(ROOT)).replace("\\", "/")},
        "pending_external": ["CUSTOMER_RESPONSE", "ORDER", "PAYMENT", "REVENUE", "ACTUAL_24H_ELAPSED"],
        "overall": "PASS_INTERNAL_PENDING_EXTERNAL",
    }
    EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert json.loads(EVIDENCE.read_text(encoding="utf-8")) == evidence
    print(json.dumps({"status": evidence["overall"], "output": str(OUTPUT), "evidence": str(EVIDENCE), "observer": "PASS"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
