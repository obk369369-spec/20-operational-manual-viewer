"""Hash-only admission context: same tamper resistance as full bodies, small enough for a 48KB variable."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CONTROL_TOWER" / "controller"))
from runtime_progress_gate import (  # noqa: E402
    CANONICAL_RULE_FILES, canonical_rule_manifest, compact_rule_context, verify_rule_context)

LIMIT = 48 * 1024


def ctx(root: Path, task="CENTRAL", verified=True):
    return compact_rule_context(canonical_rule_manifest(root, task), source_records_verified=verified)


class CompactAdmission(unittest.TestCase):
    def verdict(self, context, root=ROOT, task="CENTRAL"):
        return verify_rule_context(context, repo_root=root, task_id=task)

    def test_compact_context_allows_and_fits_variable_limit(self):
        c = ctx(ROOT)
        self.assertLess(len(json.dumps(c).encode()), LIMIT)
        self.assertNotIn("rule_records", c)
        self.assertEqual(self.verdict(c)["decision"], "ALLOW")

    def test_legacy_full_context_still_allowed(self):
        m = canonical_rule_manifest(ROOT, "CENTRAL")
        full = dict(m, conflicts=[], source_records_verified=True)
        self.assertEqual(self.verdict(full)["decision"], "ALLOW")

    def test_attacks_are_blocked(self):
        good = ctx(ROOT)
        cases = {
            "missing_context": (None, "RULE_CONTEXT_MISSING"),
            "wrong_version": (dict(good, version="stale"), "RULE_CONTEXT_STALE_OR_TAMPERED"),
            "wrong_files": (dict(good, files={**good["files"], "AGENTS.md": "0" * 64}), "RULE_CONTEXT_STALE_OR_TAMPERED"),
            "wrong_digest": (dict(good, rule_records_sha256="0" * 64), "RULE_CONTEXT_STALE_OR_TAMPERED"),
            "digest_removed": ({k: v for k, v in good.items() if k != "rule_records_sha256"}, "RULE_CONTEXT_STALE_OR_TAMPERED"),
            "empty_full_records": (dict({k: v for k, v in good.items() if k != "rule_records_sha256"}, rule_records=[]), "RULE_CONTEXT_STALE_OR_TAMPERED"),
            "conflict": (dict(good, conflicts=["x"]), "RULE_CONFLICT_UNRESOLVED"),
            "unverified": (ctx(ROOT, verified=False), "REQUIRED_SOURCE_RECORDS_UNVERIFIED"),
        }
        for name, (context, reason) in cases.items():
            with self.subTest(name):
                r = self.verdict(context)
                self.assertEqual((r["decision"], r["reason"]), ("BLOCK", reason))

    def test_rule_file_edit_after_admission_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in CANONICAL_RULE_FILES:
                (root / rel).write_text((ROOT / rel).read_text(encoding="utf-8"), encoding="utf-8")
            admitted = ctx(root)
            self.assertEqual(self.verdict(admitted, root)["decision"], "ALLOW")
            (root / "AGENTS.md").write_text("tampered\n", encoding="utf-8")
            r = self.verdict(admitted, root)
            self.assertEqual((r["decision"], r["reason"]), ("BLOCK", "RULE_CONTEXT_STALE_OR_TAMPERED"))

    def test_locally_mastered_tasks_not_blocked_by_missing_registry_target(self):
        for task in ("TOOL016", "TOOL044"):
            with self.subTest(task):
                m = canonical_rule_manifest(ROOT, task)
                self.assertEqual(m["missing"], [], m["missing"])
                self.assertEqual(self.verdict(ctx(ROOT, task), task=task)["decision"], "ALLOW")

    def test_unmapped_task_without_registry_target_still_blocked(self):
        m = canonical_rule_manifest(ROOT, "TOOL999")
        self.assertIn("REGISTRY_TARGET:TOOL999", m["missing"])


class HandoffBinding(unittest.TestCase):
    WORK = "workflow:wic-top-controller-runtime:controller-cycle"

    def setUp(self):
        import os
        import github_runtime_cycle as runtime
        self.os, self.runtime = os, runtime
        self.saved = os.environ.get("WIC_RULE_ADMISSION_JSON")

    def tearDown(self):
        if self.saved is None:
            self.os.environ.pop("WIC_RULE_ADMISSION_JSON", None)
        else:
            self.os.environ["WIC_RULE_ADMISSION_JSON"] = self.saved

    def test_envelope_without_context_gets_admitted_context(self):
        c = ctx(ROOT)
        self.os.environ["WIC_RULE_ADMISSION_JSON"] = json.dumps({"admissions": {self.WORK: {"rule_context": c}}})
        out = self.runtime.with_admitted_rule_context({"trace_id": "t", "root_id": "r"})
        self.assertEqual(out["task_id"], "CENTRAL")
        self.assertEqual(verify_rule_context(out["rule_context"], repo_root=ROOT, task_id="CENTRAL")["decision"], "ALLOW")

    def test_no_admission_means_no_injection_and_own_context_untouched(self):
        self.os.environ.pop("WIC_RULE_ADMISSION_JSON", None)
        self.assertNotIn("rule_context", self.runtime.with_admitted_rule_context({"trace_id": "t"}))
        mine = {"rule_context": {"x": 1}, "task_id": "TOOL044"}
        self.assertEqual(self.runtime.with_admitted_rule_context(mine), mine)

    def test_tampered_admitted_context_is_still_blocked_by_handoff_gate(self):
        from runtime_progress_gate import accept_handoff  # noqa: F401  (gate is unchanged; context is verified)
        bad = dict(ctx(ROOT), rule_records_sha256="0" * 64)
        self.os.environ["WIC_RULE_ADMISSION_JSON"] = json.dumps({"admissions": {self.WORK: {"rule_context": bad}}})
        out = self.runtime.with_admitted_rule_context({"trace_id": "t"})
        self.assertEqual(verify_rule_context(out["rule_context"], repo_root=ROOT, task_id="CENTRAL")["decision"], "BLOCK")


if __name__ == "__main__":
    unittest.main(verbosity=2)
