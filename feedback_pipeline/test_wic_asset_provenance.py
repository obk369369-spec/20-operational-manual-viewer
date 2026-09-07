import hashlib, tempfile
from pathlib import Path
from wic_asset_provenance import classify, inspect

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    artifact = root / "component.bin"
    artifact.write_bytes(b"actual component")
    evidence = root / "evidence.json"
    evidence.write_text("{}")
    good = {"asset_id":"GOOD", "path":str(artifact), "role":"component", "declared_state":"VERIFIED",
            "provenance":"official", "version":"1", "expected_sha256":hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "evidence_path":str(evidence), "evidence_status":"DEPLOYED_PASS", "actual_execution":"PASS",
            "expected_actual":"MATCH", "promotion_routes":["registry"]}
    assert classify(good)["status"] == "VERIFIED"
    assert classify({**good, "expected_sha256":"0"*64})["status"] == "HOLD"
    assert classify({**good, "declared_state":"DRAFT"})["promotion_allowed"] is False
    assert classify({**good, "path":str(root/'missing')})["status"] == "UNKNOWN"
    result = inspect({"assets":[good,{**good,"asset_id":"PARTIAL","declared_state":"PARTIAL"}]})
    assert result["status"] == "PASS" and result["counts"] == {"VERIFIED":1,"PARTIAL":1}
    print("5/5 PASS")
