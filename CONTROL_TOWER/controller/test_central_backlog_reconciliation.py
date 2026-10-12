import json
import unittest
from pathlib import Path

from github_runtime_cycle import (execute_central_backlog, reconcile_central_backlog,
                                  route_contracts, validate_contract,
                                  evaluate_runtime_continuity)
from wic_top_controller import preserved_queue_runtime_fields


class CentralBacklogReconciliationTest(unittest.TestCase):
    def test_actual_ledger_preserves_completed_attempt_without_reopening_closed(self):
        root = Path(__file__).resolve().parents[2]
        ledger = json.loads((root / "feedback_pipeline" / "unified_open_ledger.json").read_text(encoding="utf-8"))
        queue = {"queued_requirement_ids": []}
        result = reconcile_central_backlog(queue, ledger)
        self.assertEqual(result["pass_locked_reopened"], 0)
        self.assertGreaterEqual(result["open_ledger_count"], 1)
        self.assertEqual(result["executable_count"], 0)
        self.assertEqual(result["deferred_count"], 6)
        self.assertIsNone(result["next_root"])
        self.assertEqual(queue["backlog_root_ids"], [])
        self.assertEqual(queue["backlog_quarantine"][0]["root_id"], "WIC-0702-SCOPED-RECOVERY")

    def test_external_and_not_ready_are_deferred(self):
        ledger = {"entries": [
            {"root_id": "done", "status": "VERIFIED_CLOSED", "next_trigger": "IMMEDIATE"},
            {"root_id": "now", "status": "OPEN", "next_trigger": "IMMEDIATE"},
            {"root_id": "later", "status": "OPEN", "next_trigger": "FILE_AVAILABLE"},
            {"root_id": "external", "status": "EXTERNAL_BLOCKED", "next_trigger": "AUTH"},
        ]}
        queue = {"queued_requirement_ids": []}
        result = reconcile_central_backlog(queue, ledger)
        self.assertEqual(result["executable_count"], 1)
        self.assertEqual(result["deferred_count"], 2)
        self.assertNotIn("done", queue["backlog_root_ids"])

    def test_missing_primary_recovers_only_from_declared_verified_evidence(self):
        contract = {
            "id": "recovery", "requirement_ids": [1], "proof": "test",
            "evidence": "missing-evidence.json",
            "recovery_evidence": "CONTROL_TOWER/ledger/evidence/WIC_CENTRAL_BACKLOG_RECONCILIATION_20261012.json",
            "rules": [{"path": "overall", "operation": "equals", "expected": "PASS"}],
        }
        receipt = validate_contract(contract)
        self.assertEqual(receipt["status"], "PASS")
        self.assertTrue(receipt["evidence_recovered"])

    def test_unrecoverable_failure_is_quarantined_while_good_contract_continues(self):
        state = {"requirements": [
            {"id": 1, "queue_status": "QUEUED", "retry_count": 1},
            {"id": 2, "queue_status": "QUEUED", "retry_count": 0},
        ]}
        queue = {"queued_requirement_ids": [1, 2]}
        registry = {"execution_contracts": [
            {"id": "bad", "requirement_ids": [1], "proof": "bad", "evidence": "absent.json",
             "rules": [{"path": "overall", "operation": "equals", "expected": "PASS"}]},
            {"id": "good", "requirement_ids": [2], "proof": "good",
             "evidence": "CONTROL_TOWER/ledger/evidence/WIC_CENTRAL_BACKLOG_RECONCILIATION_20261012.json",
             "rules": [{"path": "overall", "operation": "equals", "expected": "PASS"}]},
        ]}
        processed, held = route_contracts(state, queue, registry)
        self.assertEqual([item["requirement_id"] for item in processed], [2])
        self.assertEqual([item["requirement_id"] for item in held], [1])
        self.assertEqual(queue["queued_requirement_ids"], [])
        self.assertEqual(queue["quarantined_requirements"][0]["requirement_id"], 1)

    def test_selected_backlog_is_actually_attempted_then_safely_held(self):
        ledger = {"entries": [{"root_id": "root", "status": "OPEN", "next_trigger": "IMMEDIATE"}]}
        queue = {"queued_requirement_ids": [], "backlog_root_ids": ["root"], "next_backlog_root": "root"}
        receipts = execute_central_backlog(queue, ledger, {"backlog_execution_contracts": []})
        self.assertEqual(receipts[0]["status"], "HOLD")
        self.assertEqual(ledger["entries"][0]["status"], "HOLD_EXECUTION_CONTRACT_OR_ACTUAL_INPUT")
        self.assertEqual(queue["backlog_root_ids"], [])
        second = execute_central_backlog(queue, ledger, {"backlog_execution_contracts": []})
        self.assertEqual(second, [])
        self.assertEqual(len(queue["backlog_quarantine"]), 1)

    def test_restart_preserves_handoff_and_quarantine(self):
        previous = {
            "handoff_inbox": [{"trace_id": "one"}],
            "backlog_quarantine": [{"root_id": "blocked"}],
            "quarantined_requirements": [{"requirement_id": 9}],
        }
        preserved = preserved_queue_runtime_fields(previous)
        self.assertEqual(preserved["handoff_inbox"], previous["handoff_inbox"])
        self.assertEqual(preserved["backlog_quarantine"], previous["backlog_quarantine"])
        self.assertEqual(preserved["quarantined_requirements"], previous["quarantined_requirements"])

    def test_24h_continuity_pass_and_gap_fail_closed(self):
        regular = [
            {"id": index, "created_at": f"2026-10-{10 + index // 24:02d}T{index % 24:02d}:00:00Z",
             "status": "completed", "conclusion": "success"}
            for index in range(49)
        ]
        self.assertEqual(evaluate_runtime_continuity(regular)["status"], "PASS")
        gapped = [regular[0], regular[8], regular[16], regular[24], regular[32], regular[40], regular[48]]
        self.assertEqual(evaluate_runtime_continuity(gapped)["status"], "HOLD_SCHEDULE_GAP")

    def test_24h_failure_requires_later_recovery(self):
        runs = [
            {"id": index, "created_at": f"2026-10-{10 + index // 24:02d}T{index % 24:02d}:00:00Z",
             "status": "completed", "conclusion": "failure" if index == 48 else "success"}
            for index in range(49)
        ]
        self.assertEqual(evaluate_runtime_continuity(runs)["status"], "HOLD_UNRECOVERED_RUNTIME_FAILURE")


if __name__ == "__main__":
    unittest.main()
