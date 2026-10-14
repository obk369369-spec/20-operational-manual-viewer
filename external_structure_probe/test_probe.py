import json
import os
import unittest
from pathlib import Path

from external_structure_probe.probe import transform


ROOT = Path(__file__).resolve().parent


class ProbeContractTest(unittest.TestCase):
    def test_golden_contract(self):
        actual = transform(json.loads((ROOT / "golden_input.json").read_text(encoding="utf-8")))
        expected = json.loads((ROOT / "golden_output.json").read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)
        self.assertEqual([r["id"] for r in actual["records"]], ["A-001", "A-002"])


if __name__ == "__main__":
    unittest.main()
