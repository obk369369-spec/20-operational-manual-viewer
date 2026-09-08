from tool044_safe_integration import gate, run_fixture


def test_gate_is_fail_closed():
    allowed, missing = gate({"source_receipt": True})
    assert not allowed
    assert "artifact_match" in missing


def test_fixture_deploy_and_rollback():
    result = run_fixture()
    assert result["expected_actual"] == "MATCH"
    assert result["safe_fixture_deploy_gate"] == "VERIFIED"
    assert result["safe_fixture_auto_rollback"] == "VERIFIED"
    assert result["arbitrary_wic_tool_auto_deploy"] == "NOT_IMPLEMENTED"
