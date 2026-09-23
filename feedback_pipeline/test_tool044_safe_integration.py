from tool044_safe_integration import (
    READY_COMPONENT_FIELDS,
    WORK_REENTRY_RECEIPTS,
    component_reentry_gate,
    gate,
    run_fixture,
)


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


def test_component_reentry_gate_requires_complete_contract_and_receipts():
    component = {key: f"verified-{key}" for key in READY_COMPONENT_FIELDS}
    receipts = {key: True for key in WORK_REENTRY_RECEIPTS}
    ready = component_reentry_gate(component, receipts)
    assert ready["status"] == "READY_FOR_WORK_REENTRY"
    assert ready["work_reentry_allowed"] is True

    incomplete = component_reentry_gate(
        {key: value for key, value in component.items() if key != "install_target"},
        {**receipts, "sandbox_component_pass": False},
    )
    assert incomplete["status"] == "HOLD_COMPONENT_CONTRACT_INCOMPLETE"
    assert incomplete["work_reentry_allowed"] is False
    assert incomplete["missing_fields"] == ["install_target"]
    assert incomplete["missing_receipts"] == ["sandbox_component_pass"]
