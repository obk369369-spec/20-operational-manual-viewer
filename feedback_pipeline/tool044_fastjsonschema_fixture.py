"""Immutable functional fixture for TOOL044's verified fastjsonschema component."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
wheel = root / "tool043/vendor/fastjsonschema-2.21.2-py3-none-any.whl"
source_hash = hashlib.sha256(wheel.read_bytes()).hexdigest()
sys.path.insert(0, str(wheel))
import fastjsonschema

schema = {
    "type": "object",
    "required": ["repository", "commit", "path", "remote_blob_sha"],
    "properties": {
        "repository": {"type": "string", "minLength": 1},
        "commit": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
        "path": {"type": "string", "pattern": "^(?!.*\\.\\.).+$"},
        "remote_blob_sha": {"type": "string", "pattern": "^[0-9a-f]{40}$"}
    }
}
validate = fastjsonschema.compile(schema, use_default=False)
valid = {
    "repository": "obk369369-spec/20-operational-manual-viewer",
    "commit": "99269456d92972fc49c875ca16c36ab23f3b5ffc",
    "path": "feedback_pipeline/evidence/tool044_production_run.json",
    "remote_blob_sha": "313c7b40df0d1c9ae6e479233e3760f1e1faef46"
}
validate(valid)
invalid = [
    True,
    "PASS",
    {},
    {**valid, "commit": "invalid"},
    {**valid, "path": "../fake.json"},
    {**valid, "remote_blob_sha": ""}
]
blocked = 0
for item in invalid:
    try:
        validate(item)
    except (fastjsonschema.JsonSchemaException, TypeError):
        blocked += 1
if blocked != len(invalid):
    raise SystemExit("INVALID_INPUT_ACCEPTED")
report = {
    "status": "PASS",
    "input": "Immutable fastjsonschema completion-proof contract fixture",
    "valid_proof_accepted": True,
    "invalid_proof_cases_blocked": blocked,
    "source_sha256": source_hash
}
if len(sys.argv) != 2:
    raise SystemExit("RESULT_PATH_REQUIRED")
Path(sys.argv[1]).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
