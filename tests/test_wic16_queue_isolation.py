"""Changed-boundary synthetic tests; no customer input or existing PASS reruns."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CONTROL_TOWER" / "controller"))
import github_runtime_cycle as runtime  # noqa: E402
import pre_work_admission  # noqa: E402
import runtime_progress_gate  # noqa: E402
import wic_top_controller as body  # noqa: E402


class QueueIsolationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "feedback_pipeline" / "evidence").mkdir(parents=True)
        self.root_patch = patch.object(runtime.body, "ROOT", self.root)
        self.rule_patch = patch.object(runtime_progress_gate, "verify_rule_context",
                                       return_value={"decision": "ALLOW", "reason": None})
        self.root_patch.start()
        self.rule_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.addCleanup(self.rule_patch.stop)

    def admission(self, work_id: str, *, stop: bool = False, bad_hash: bool = False) -> dict:
        relative = f"feedback_pipeline/evidence/{work_id.replace(':', '_')}.json"
        target = self.root / relative
        original = self.root / "input.txt"
        original.write_text("synthetic source", encoding="utf-8")
        target.write_text(json.dumps({
            "work_id": work_id, "task_id": "TOOL044",
            "source_records_verified": True, "validation_result": "PASS",
            "validator_id": "synthetic-independent-validator",
            "source_refs": [{"path": "input.txt", "sha256": hashlib.sha256(original.read_bytes()).hexdigest()}],
            "rule_version": "synthetic-current",
            "validation_plan": {"method": "synthetic compare", "expected_result": "match",
                                "evidence_required": "original and receipt"},
        }), encoding="utf-8")
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        return {"work_id": work_id, "task_id": "TOOL044",
                "user_stop": stop, "rule_context": {"task_id": "TOOL044", "version": "synthetic-current"},
                "source_receipt": {"path": relative, "sha256": "stale" if bad_hash else digest}}

    @staticmethod
    def state(*ids: int, locked: tuple[int, ...] = ()) -> dict:
        return {"requirements": [{"id": value, "status": "VERIFIED_CLOSED" if value in locked else "OPEN",
                                  "queue_status": "PASS_LOCKED" if value in locked else "QUEUED",
                                  "retry_count": 0} for value in ids]}

    @staticmethod
    def registry(*ids: int) -> dict:
        return {"execution_contracts": [
            {"id": f"C{value}", "task_id": "TOOL044", "requirement_ids": [value], "proof": "synthetic"}
            for value in ids]}

    def test_three_allowed_one_blocked_and_worker_failure_isolated(self) -> None:
        state = self.state(1, 2, 3, 4)
        queue = {"queued_requirement_ids": [1, 2, 3, 4], "backlog_root_ids": [],
                 "rule_admissions": {f"requirement:{value}": self.admission(f"requirement:{value}")
                                     for value in (1, 2, 3)}}
        receipt = runtime.isolate_denied_queued_work(state, queue, {"entries": []}, self.registry(1, 2, 3, 4))
        self.assertEqual((receipt["decision"], receipt["allowed_count"]), ("PARTIAL", 3))
        self.assertEqual(queue["queued_requirement_ids"], [1, 2, 3])
        self.assertEqual(state["requirements"][3]["queue_status"], "WAITING")
        self.assertEqual(queue["quarantined_requirements"][0]["requirement_id"], 4)

        def worker(contract: dict) -> dict:
            if contract["id"] == "C1":
                return {"status": "HOLD", "reason": "SYNTHETIC_FAILURE", "attempts": 1, "evidence": []}
            return {"status": "PASS", "reason": None, "attempts": 1, "evidence": ["synthetic-result"]}

        with patch.object(runtime, "validate_contract", side_effect=worker) as called:
            processed, held = runtime.route_contracts(state, queue, self.registry(1, 2, 3, 4))
        self.assertEqual({item["requirement_id"] for item in processed}, {2, 3})
        self.assertEqual({item["requirement_id"] for item in held}, {1})
        self.assertEqual(called.call_count, 3)
        self.assertEqual(state["requirements"][3]["queue_status"], "WAITING")

    def test_two_allowed_one_explicit_stop(self) -> None:
        state = self.state(1, 2, 3)
        queue = {"queued_requirement_ids": [1, 2, 3], "backlog_root_ids": [],
                 "rule_admissions": {f"requirement:{value}": self.admission(
                     f"requirement:{value}", stop=value == 3) for value in (1, 2, 3)}}
        receipt = runtime.isolate_denied_queued_work(state, queue, {"entries": []}, self.registry(1, 2, 3))
        self.assertEqual(queue["queued_requirement_ids"], [1, 2])
        self.assertEqual(receipt["receipts"][2]["reason"], "USER_STOP_OR_START_BLOCKED")

    def test_all_blocked_then_checkpoint_does_not_reenter(self) -> None:
        state = self.state(1, 2)
        queue = {"queued_requirement_ids": [1, 2], "backlog_root_ids": [], "rule_admissions": {}}
        receipt = runtime.isolate_denied_queued_work(state, queue, {"entries": []}, self.registry(1, 2))
        self.assertEqual((receipt["decision"], queue["queued_requirement_ids"]), ("BLOCK", []))
        snapshot = body.preserved_queue_runtime_fields(queue)
        self.assertEqual(len(snapshot["quarantined_requirements"]), 2)
        self.assertEqual([row["id"] for row in state["requirements"]
                          if row["queue_status"] == "QUEUED"], [])
        self.assertEqual(runtime.queued_work_admission(
            {"queued_requirement_ids": [], "backlog_root_ids": [], **snapshot},
            self.registry(1, 2))["selected_count"], 0)

    def test_pass_lock_unchanged_and_admission_preserved(self) -> None:
        state = self.state(1, 2, locked=(2,))
        queue = {"queued_requirement_ids": [1, 2], "backlog_root_ids": [],
                 "rule_admissions": {"requirement:1": self.admission("requirement:1")}}
        receipt = runtime.isolate_denied_queued_work(state, queue, {"entries": []}, self.registry(1, 2))
        self.assertEqual(receipt["skipped_pass_locked"], [2])
        self.assertEqual(queue["queued_requirement_ids"], [1])
        self.assertEqual(state["requirements"][1]["queue_status"], "PASS_LOCKED")
        self.assertEqual(body.preserved_queue_runtime_fields(queue)["rule_admissions"], queue["rule_admissions"])

    def test_stale_source_receipt_only_blocks_its_job(self) -> None:
        state = self.state(1, 2)
        queue = {"queued_requirement_ids": [1, 2], "backlog_root_ids": [],
                 "rule_admissions": {"requirement:1": self.admission("requirement:1"),
                                     "requirement:2": self.admission("requirement:2", bad_hash=True)}}
        receipt = runtime.isolate_denied_queued_work(state, queue, {"entries": []}, self.registry(1, 2))
        self.assertEqual(queue["queued_requirement_ids"], [1])
        self.assertEqual(receipt["receipts"][1]["reason"], "SOURCE_VALIDATION_RECEIPT_STALE_OR_TAMPERED")

    def test_backlog_denial_persists_in_ledger(self) -> None:
        ledger = {"entries": [{"root_id": "A", "status": "OPEN", "next_trigger": "IMMEDIATE"},
                              {"root_id": "B", "status": "OPEN", "next_trigger": "IMMEDIATE"}]}
        queue = {"queued_requirement_ids": [], "backlog_root_ids": ["A", "B"],
                 "rule_admissions": {"backlog:A": self.admission("backlog:A")}}
        registry = {"backlog_execution_contracts": [
            {"root_id": root, "task_id": "TOOL044"} for root in ("A", "B")]}
        receipt = runtime.isolate_denied_queued_work({"requirements": []}, queue, ledger, registry)
        self.assertEqual(receipt["decision"], "PARTIAL")
        self.assertEqual(queue["backlog_root_ids"], ["A"])
        self.assertEqual(ledger["entries"][1]["status"], "HOLD_EXECUTION_ADMISSION")
        self.assertEqual(ledger["entries"][1]["next_trigger"], "CURRENT_RULE_OR_SOURCE_ADMISSION_CHANGED")

    def test_backlog_supply_requires_contract_and_source_admission(self) -> None:
        ledger = {"entries": [{"root_id": root, "status": "OPEN", "next_trigger": "IMMEDIATE"}
                              for root in ("A", "B", "C")]}
        queue = {"queued_requirement_ids": [], "backlog_root_ids": [],
                 "rule_admissions": {"backlog:A": self.admission("backlog:A")}}
        registry = {"backlog_execution_contracts": [
            {"root_id": root, "task_id": "TOOL044"} for root in ("A", "C")]}
        supply = runtime.reconcile_central_backlog(queue, ledger, registry)
        self.assertEqual(queue["backlog_root_ids"], ["A"])
        self.assertEqual(supply["executable_count"], 1)
        self.assertEqual({row["root_id"]: row["defer_reason"] for row in supply["deferred"]}, {
            "B": "EXECUTION_CONTRACT_MISSING",
            "C": "WORK_ADMISSION_OR_SOURCE_RECEIPT_MISSING",
        })
        receipt = runtime.isolate_denied_queued_work({"requirements": []}, queue, ledger, registry)
        self.assertEqual((receipt["decision"], receipt["allowed_count"]), ("ALLOW", 1))
        self.assertTrue(all(row["status"] == "OPEN" for row in ledger["entries"]))

    def test_changed_original_blocks_only_affected_job(self) -> None:
        state = self.state(1, 2)
        first = self.admission("requirement:1")
        (self.root / "input.txt").write_text("changed source", encoding="utf-8")
        second = self.admission("requirement:2")
        queue = {"queued_requirement_ids": [1, 2], "backlog_root_ids": [],
                 "rule_admissions": {"requirement:1": first, "requirement:2": second}}
        result = runtime.isolate_denied_queued_work(state, queue, {"entries": []}, self.registry(1, 2))
        self.assertEqual(queue["queued_requirement_ids"], [2])
        self.assertEqual(result["receipts"][0]["reason"], "ORIGINAL_SOURCE_MISSING_OR_CHANGED")

    def test_contract_pass_cannot_close_root_without_actual_result(self) -> None:
        ledger = {"entries": [{"root_id": "A", "status": "OPEN", "next_trigger": "IMMEDIATE"}]}
        queue = {"backlog_root_ids": ["A"], "backlog_quarantine": []}
        registry = {"backlog_execution_contracts": [{"root_id": "A", "task_id": "TOOL044"}]}
        with patch.object(runtime, "validate_contract", return_value={
                "status": "PASS", "evidence": ["synthetic-contract.json"], "readback_pass": True}):
            receipts = runtime.execute_central_backlog(queue, ledger, registry)
        self.assertEqual(receipts[0]["reason"], "ACTUAL_RESULT_AND_INDEPENDENT_COMPLETION_MISSING")
        self.assertEqual(ledger["entries"][0]["status"], "HOLD_EXECUTION_COMPLETION")
        self.assertNotEqual(ledger["entries"][0]["status"], "VERIFIED_CLOSED")
        self.assertEqual(queue["backlog_quarantine"][0]["root_id"], "A")

    def test_authoritative_global_stop_still_blocks(self) -> None:
        with patch.dict(os.environ, {"WIC_USER_STOP": "1"}):
            receipt = pre_work_admission.require_external_admission("synthetic-work", "TOOL044")
        self.assertEqual(receipt["decision"], "BLOCK")
        self.assertEqual(receipt["reason"], "USER_STOP_OR_START_BLOCKED")


if __name__ == "__main__":
    unittest.main()

