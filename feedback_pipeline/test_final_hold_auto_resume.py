from pathlib import Path
from final_hold_auto_resume import TRIGGERS, evaluate


def test_holds_without_real_evidence(tmp_path: Path):
    actual = evaluate({"status": "WAITING"}, {})
    assert actual["external_root_status"] == "HOLD"
    assert actual["elapsed_time_status"] == "WAITING"
    assert actual["automatic_resume_queue"] == []


def test_only_real_files_and_real_24h_pass_enqueue(tmp_path: Path):
    evidence = tmp_path / "evidence.json"; evidence.write_text("{}", encoding="utf-8")
    env = {next(iter(TRIGGERS.values())): str(evidence)}
    actual = evaluate({"status": "PASS"}, env)
    assert actual["external_root_status"] == "READY_PARTIAL"
    assert actual["elapsed_time_status"] == "PASS"
    assert len(actual["automatic_resume_queue"]) == 2
    repeated = evaluate({"status": "PASS"}, env)
    assert repeated["automatic_resume_queue"] == actual["automatic_resume_queue"]
    assert len(repeated["automatic_resume_queue"]) == len(set(repeated["automatic_resume_queue"]))
    assert actual["fake_pass_forbidden"] is True
