"""Scoped checks using the existing persisted feedback and registry inputs."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from global_pipeline import build_packets, preserve_user_directive, resolve_event
from ingest_actual_feedback_batch import BATCH, REGISTRY, STATE, run
from unauthorized_structure_guard import ChangeProposal, evaluate


class CommonInputBatch(unittest.TestCase):
    def test_original_directive_reaches_tool016_packet(self):
        original = "고객 출력 금지 규칙을 유지하고 코드 수정해. 상세 원문을 보존하라."
        event = preserve_user_directive({"source_chat": "CENTRAL", "source_ref": "CURRENT_CHAT#actual",
                                         "feedback": "축약", "directive_text": original})
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        target, row = resolve_event(registry, event)
        evidence, _ = build_packets(event, target, row)
        self.assertEqual(evidence["actual_user_feedback"], original)
        with self.assertRaises(ValueError):
            preserve_user_directive({"feedback": "축약", "directive_text": " "})

    def test_unrelated_prohibition_and_actual_denial(self):
        instruction = "코드 수정해. 새 대화창 생성하지 마."
        p = ChangeProposal("MODIFY_PROGRAM", "program", instruction, "user:fixture")
        self.assertEqual(evaluate(p, instruction).decision, "ALLOW")
        denied = ChangeProposal("MODIFY_PROGRAM", "program", "코드 수정하지 마.", "user:fixture")
        self.assertEqual(evaluate(denied, denied.directive_text).decision, "DENY_HOLD")

    def test_existing_actual_batch_uses_active_registry_and_resumes(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            shutil.copyfile(STATE, state_path)
            first = run(state_path, BATCH, REGISTRY)
            second = run(state_path, BATCH, REGISTRY)
            self.assertEqual(first["result"], "PASS")
            self.assertEqual(second["inserted"], 0)
            self.assertEqual(sum(second["by_tool"].values()), second["roots"])
            registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
            self.assertEqual(resolve_event(registry, {"source_chat": "TOOL041"})[0], "TOOL041")

    def test_unregistered_target_is_blocked_before_state_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path, batch_path = root / "state.json", root / "batch.json"
            shutil.copyfile(STATE, state_path)
            batch = json.loads(BATCH.read_text(encoding="utf-8"))
            batch["events"][0]["tool"] = "TOOL_NOT_REGISTERED"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            before = state_path.read_bytes()
            with self.assertRaises(ValueError):
                run(state_path, batch_path, REGISTRY)
            self.assertEqual(state_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
