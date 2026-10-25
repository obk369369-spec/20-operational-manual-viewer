import unittest

from universal_enforcement import enforce_record_isolation, stable_record_id


class RecordIsolationTest(unittest.TestCase):
    def test_positive_and_quarantine_continue(self):
        records = [
            {"origin_file": "a.doc", "origin_row": 1, "value": "ok"},
            {"origin_file": "b.doc", "origin_row": 1, "value": "bad"},
        ]
        result = enforce_record_isolation(records, lambda row: row["value"] == "ok")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["final_usable_count"], 1)
        self.assertEqual(result["quarantined_count"], 1)

    def test_deterministic_repair_and_revalidation(self):
        records = [{"origin_file": "a.doc", "origin_row": 1, "value": "fix"}]
        result = enforce_record_isolation(
            records,
            lambda row: row["value"] == "ok",
            lambda row: {**row, "value": "ok"},
            allowed_repair_fields={"value"},
        )
        self.assertEqual(result["auto_repaired_count"], 1)
        self.assertEqual(result["status"], "PASS")

    def test_duplicate_identity_blocks_output(self):
        record = {"origin_file": "a.doc", "origin_row": 1, "value": "ok"}
        result = enforce_record_isolation([record, dict(record)], lambda row: True)
        self.assertEqual(result["status"], "HOLD_IDENTITY_INTEGRITY")
        self.assertEqual(result["output_records"], [])

    def test_repair_cannot_change_identity_or_protected_field(self):
        record = {"origin_file": "a.doc", "origin_row": 1, "value": "bad", "customer": "A"}
        result = enforce_record_isolation(
            [record], lambda row: row["value"] == "ok",
            lambda row: {**row, "value": "ok", "customer": "B"},
            allowed_repair_fields={"value"},
        )
        self.assertEqual(result["status"], "HOLD_IDENTITY_INTEGRITY")

    def test_stable_id_is_path_separator_independent(self):
        left = stable_record_id({"origin_file": "folder\\a.doc", "origin_row": 2})
        right = stable_record_id({"origin_file": "folder/a.doc", "origin_row": 2})
        self.assertEqual(left, right)

    def test_repair_is_attempted_exactly_once_then_quarantined(self):
        attempts = []
        record = {"origin_file": "a.doc", "origin_row": 1, "value": "bad"}

        def repair(row):
            attempts.append(row["value"])
            return row

        result = enforce_record_isolation(
            [record], lambda row: {"valid": row["value"] == "ok", "field": "value"},
            repair, allowed_repair_fields={"value"},
        )
        self.assertEqual(attempts, ["bad"])
        self.assertEqual(result["quarantined_count"], 1)
        self.assertEqual(result["record_evidence"][0]["repair_attempts"], 1)
        self.assertEqual(result["record_evidence"][0]["reason"], "UNRESOLVED_AFTER_REPAIR")

    def test_repair_identity_removal_is_fail_closed_not_exception(self):
        record = {"origin_file": "a.doc", "origin_row": 1, "value": "bad"}
        result = enforce_record_isolation(
            [record], lambda row: False,
            lambda row: {"value": "ok"}, allowed_repair_fields={"value"},
        )
        self.assertEqual(result["status"], "HOLD_IDENTITY_INTEGRITY")
        self.assertEqual(result["integrity_failures"][0]["repair_attempts"], 1)

    def test_callback_errors_are_quarantined_and_other_records_continue(self):
        records = [
            {"origin_file": "a.doc", "origin_row": 1, "value": "explode"},
            {"origin_file": "b.doc", "origin_row": 1, "value": "ok"},
        ]

        def validate(row):
            if row["value"] == "explode":
                raise RuntimeError("adapter unavailable")
            return True

        result = enforce_record_isolation(records, validate)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["final_usable_count"], 1)
        self.assertEqual(result["quarantined_count"], 1)
        self.assertEqual(result["record_evidence"][0]["reason"], "VALIDATOR_ERROR")


if __name__ == "__main__":
    unittest.main()

