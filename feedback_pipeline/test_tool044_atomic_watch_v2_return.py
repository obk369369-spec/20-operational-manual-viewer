"""Actual persisted Issue handoff fixture; no external search or base-loop replay."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tool044_atomic_watch_v2 import return_verified_results

HERE = Path(__file__).resolve().parent


class WorkerReturnContract(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name) / "feedback_pipeline"
        root.mkdir()
        for name in ("TOOL044_REQUEST_INBOX.json", "tool044_atomic_demand_queue.json",
                     "VERIFIED_COMPONENT_REGISTRY.json", "state.json"):
            shutil.copyfile(HERE / name, root / name)
        evidence = root / "evidence"
        evidence.mkdir()
        shutil.copyfile(HERE / "evidence" / "tool044_atomic_watch_state.json",
                        evidence / "tool044_atomic_watch_state.json")
        pool = HERE / "evidence" / "tool044_verified_external_component_pool.json"
        if pool.exists():
            shutil.copyfile(pool, evidence / pool.name)
        wheel = HERE / "external_candidate_pool" / "doit-0.37.0-py3-none-any.whl"
        if wheel.exists():
            artifacts = root / "external_candidate_pool"
            artifacts.mkdir()
            shutil.copyfile(wheel, artifacts / wheel.name)
        self.queue = root / "tool044_atomic_demand_queue.json"
        self.registry = root / "VERIFIED_COMPONENT_REGISTRY.json"
        self.state_path = evidence / "tool044_atomic_watch_state.json"
        self.central_path = root / "state.json"
        inbox_path = root / "TOOL044_REQUEST_INBOX.json"
        inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
        queue = json.loads(self.queue.read_text(encoding="utf-8"))
        central = json.loads(self.central_path.read_text(encoding="utf-8"))
        eligible = set(central["integration_core"]["feedback_checkpoints"])
        request = next(r for r in inbox["requests"] if r["request_id"] in eligible and
                       any(d.get("request_id") == r["request_id"] for d in queue["demands"]))
        self.request_id = request["request_id"]
        inbox_path.write_text(json.dumps({"requests": [request]}), encoding="utf-8")
        queue["demands"] = [d for d in queue["demands"] if d.get("request_id") == self.request_id]
        self.queue.write_text(json.dumps(queue), encoding="utf-8")
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        ids = {d["demand_id"] for d in queue["demands"]}
        state["results"] = [r for r in state["results"] if r.get("demand_id") in ids]
        state["cycle_id"] = "RETURN-CONTRACT-ACTUAL-FIXTURE"
        self.state = state
        checkpoint = central["integration_core"]["feedback_checkpoints"][self.request_id]
        for key in ("tool044_natural_worker_return", "tool044_worker_checkpoint", "tool044_worker_return_ack"):
            checkpoint.pop(key, None)
        self.central_path.write_text(json.dumps(central), encoding="utf-8")

    def checkpoint(self):
        return json.loads(self.central_path.read_text(encoding="utf-8"))["integration_core"]["feedback_checkpoints"][self.request_id]

    def test_normal_return_restart_and_no_duplicate(self):
        first = return_verified_results(self.queue, self.registry, self.state_path, self.state)
        self.assertEqual(first, {"acknowledged": 1, "blocked": []})
        receipt = self.checkpoint()["tool044_natural_worker_return"]
        self.assertEqual(receipt["ack"], "TOOL016_CENTRAL_RECEIVED")
        self.assertEqual(len(receipt["source_receipt_sha256"]), 64)
        self.assertEqual(len(receipt["worker_receipt_sha256"]), 64)
        before = self.central_path.read_bytes()
        second = return_verified_results(self.queue, self.registry, self.state_path, self.state)
        self.assertEqual(second, {"acknowledged": 0, "blocked": []})
        self.assertEqual(self.central_path.read_bytes(), before)

    def test_receipt_mismatch_blocks_pass(self):
        bad = copy.deepcopy(self.state)
        bad["results"][0]["result"] = "READY_ATOMIC_COMPONENT_FOUND"
        result = return_verified_results(self.queue, self.registry, self.state_path, bad)
        self.assertEqual(result["acknowledged"], 0)
        self.assertTrue(result["blocked"])
        self.assertNotEqual(self.checkpoint().get("tool044_worker_return_ack"), "PASS")

    def test_component_artifact_mismatch_blocks_pass(self):
        wheel = self.queue.parent / "external_candidate_pool" / "doit-0.37.0-py3-none-any.whl"
        wheel.write_bytes(b"different artifact")
        result = return_verified_results(self.queue, self.registry, self.state_path, self.state)
        self.assertEqual(result["acknowledged"], 0)
        self.assertTrue(result["blocked"])
        self.assertNotEqual(self.checkpoint().get("tool044_worker_return_ack"), "PASS")

    def test_partial_write_failure_restores_exact_checkpoint_then_resume(self):
        before = self.central_path.read_bytes()

        def broken_writer(path, _value):
            path.write_text("broken partial write", encoding="utf-8")
            raise OSError("injected interruption")

        with self.assertRaises(OSError):
            return_verified_results(self.queue, self.registry, self.state_path, self.state, broken_writer)
        self.assertEqual(self.central_path.read_bytes(), before)
        self.assertEqual(return_verified_results(self.queue, self.registry, self.state_path, self.state)["acknowledged"], 1)
        self.assertEqual(self.checkpoint()["tool044_worker_return_ack"], "PASS")


if __name__ == "__main__":
    unittest.main()
