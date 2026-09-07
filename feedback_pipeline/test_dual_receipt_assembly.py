from __future__ import annotations

import hashlib
from pathlib import Path

from wic_component_receipts import dual_receipt_assembly


ROOT = Path(__file__).resolve().parent
WIC_RUNTIME = ROOT / "tool044_mechanical.py"
ACTUAL_HASH = hashlib.sha256(WIC_RUNTIME.read_bytes()).hexdigest()

EXTERNAL_OK = {
    "component_id": "FASTJSONSCHEMA-2.21.2",
    "status": "COMPONENT_VERIFIED",
    "receipt_comparison": "RECEIPT_MATCH_PASS",
}
WIC_CANONICAL = {
    "component_id": "TOOL044_MECHANICAL",
    "canonical_path": "feedback_pipeline/tool044_mechanical.py",
    "version": "2026-09-07",
    "checkpoint": "bd5af3b55841e84b444082572112b68afd5498ec",
    "sha256": ACTUAL_HASH,
    "evidence": "feedback_pipeline/evidence/tool044_mechanical_deployed.actual.json",
    "verified_status": "DEPLOYED_PASS",
    "entrypoint": "feedback_pipeline/tool044_mechanical.py",
}
WIC_DEPLOYED = {**WIC_CANONICAL, "canonical_path": str(WIC_RUNTIME)}


def main() -> None:
    # 1. Both actual receipts match and the interface works.
    assert dual_receipt_assembly(EXTERNAL_OK, WIC_CANONICAL, WIC_DEPLOYED, lambda: True)["status"] == "ASSEMBLY_VERIFIED"

    # 2. External receipt mismatch blocks before interface execution.
    external_bad = {**EXTERNAL_OK, "receipt_comparison": "RECEIPT_MISMATCH"}
    assert dual_receipt_assembly(external_bad, WIC_CANONICAL, WIC_DEPLOYED, lambda: True)["status"] == "ASSEMBLY_BLOCKED_RECEIPT_MISMATCH"

    # 3. WIC hash/version mismatch blocks assembly.
    deployed_bad = {**WIC_DEPLOYED, "sha256": "0" * 64, "version": "stale"}
    assert dual_receipt_assembly(EXTERNAL_OK, WIC_CANONICAL, deployed_bad, lambda: True)["status"] == "ASSEMBLY_BLOCKED_RECEIPT_MISMATCH"

    # 4. A WIC shell/draft cannot be assembled.
    deployed_shell = {**WIC_DEPLOYED, "verified_status": "DRAFT"}
    assert dual_receipt_assembly(EXTERNAL_OK, WIC_CANONICAL, deployed_shell, lambda: True)["status"] == "SHELL_OR_INVALID"

    # 5. Matching receipts do not override a failed real interface.
    assert dual_receipt_assembly(EXTERNAL_OK, WIC_CANONICAL, WIC_DEPLOYED, lambda: False)["status"] == "ASSEMBLY_BLOCKED_INTERFACE_FAIL"

    # 6. Normal assembly records expected/actual and impacted regression.
    result = dual_receipt_assembly(EXTERNAL_OK, WIC_CANONICAL, WIC_DEPLOYED, lambda: WIC_RUNTIME.is_file())
    assert result["status"] == "ASSEMBLY_VERIFIED"
    assert result["expected_actual"] == "MATCH"
    assert result["impacted_regression"] == "PASS"
    print("6/6 PASS: dual external/WIC receipt assembly gate")


if __name__ == "__main__":
    main()
