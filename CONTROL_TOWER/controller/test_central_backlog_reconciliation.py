import json
import unittest
from pathlib import Path

from github_runtime_cycle import reconcile_central_backlog


class CentralBacklogReconciliationTest(unittest.TestCase):
    def test_actual_ledger_selects_immediate_without_reopening_closed(self):
        root = Path(__file__).resolve().parents[2]
        ledger = json.loads((root / "feedback_pipeline" / "unified_open_ledger.json").read_text(encoding="utf-8"))
        queue = {"queued_requirement_ids": []}
        result = reconcile_central_backlog(queue, ledger)
        self.assertEqual(result["pass_locked_reopened"], 0)
        self.assertGreaterEqual(result["open_ledger_count"], 1)
        self.assertEqual(result["executable_count"], 1)
        self.assertEqual(result["next_root"], "WIC-0702-SCOPED-RECOVERY")
        self.assertEqual(queue["backlog_root_ids"], ["WIC-0702-SCOPED-RECOVERY"])

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


if __name__ == "__main__":
    unittest.main()
