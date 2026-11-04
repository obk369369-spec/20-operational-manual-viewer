"""Regression test for the WIC16 engine/final status proof contract.

Run: python -m unittest discover -s CONTROL_TOWER/controller/tests -p 'test_runtime_status_contract.py'
Does not start the controller, write runtime files, or require GitHub credentials.
"""
import ast
import pathlib
import unittest

CONTROLLER = pathlib.Path(__file__).resolve().parents[1] / "wic_top_controller.py"


def load_isolated_writer():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    fn = next(node for node in tree.body
              if isinstance(node, ast.FunctionDef) and node.name == "write_tool_state")
    namespace = {
        "Any": object,
        "ROOT": pathlib.Path("/tmp/wic16"),
        "STATE": pathlib.Path("/tmp/wic16/state.json"),
        "EVIDENCE": pathlib.Path("/tmp/wic16/evidence.json"),
        "TOOL_STATE": pathlib.Path("/tmp/wic16/tool_state.json"),
        "now": lambda: "2026-11-04T00:00:00Z",
        "atomic_json": lambda path, payload: namespace.setdefault("captured", payload),
    }
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(CONTROLLER), "exec"), namespace)
    return namespace


class RuntimeStatusContract(unittest.TestCase):
    def setUp(self):
        self.ns = load_isolated_writer()
        self.state = {
            "requirements": [],
            "source_matrix_sha256": "isolated-test",
            "independent_runtime": "NOT_PROVEN",
            "actual_24h_elapsed_validation": "HOLD",
        }

    def check(self, overall, runtime, elapsed, engine, final):
        self.state.update(independent_runtime=runtime,
                          actual_24h_elapsed_validation=elapsed)
        self.ns.pop("captured", None)
        self.ns["write_tool_state"](self.state, overall)
        output = self.ns["captured"]
        self.assertEqual((output["ENGINE_STATUS"], output["FINAL_STATUS"]),
                         (engine, final))

    def test_missing_proof_holds(self):
        self.check("PASS", "NOT_PROVEN", "HOLD", "HOLD", "HOLD")

    def test_local_proof_runs(self):
        self.check("PASS", "PROVEN", "PASS", "RUNNING", "PASS")

    def test_existing_github_actions_proof_runs(self):
        self.check("PASS", "GITHUB_ACTIONS_SCHEDULED_PASS", "PASS", "RUNNING", "PASS")

    def test_github_actions_without_24h_holds(self):
        self.check("PASS", "GITHUB_ACTIONS_SCHEDULED_PASS", "PENDING_NATURAL_TIME", "HOLD", "HOLD")

    def test_failure_never_runs(self):
        self.check("FAIL", "GITHUB_ACTIONS_SCHEDULED_PASS", "PASS", "HOLD", "FAIL")


if __name__ == "__main__":
    unittest.main()
