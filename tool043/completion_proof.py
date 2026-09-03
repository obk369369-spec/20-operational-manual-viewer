"""WIC adapter for the unmodified, pinned fastjsonschema wheel.

Schema validation proves evidence shape, not the underlying business result.
"""
import hashlib
import sys
from pathlib import Path

WHEEL_NAME = 'fastjsonschema-2.21.2-py3-none-any.whl'
WHEEL_SHA = '1c797122d0a86c5cace2e54bf4e819c36223b552017172f32c5c024a6b77e463'
wheel = Path(__file__).parent / 'vendor' / WHEEL_NAME
if hashlib.sha256(wheel.read_bytes()).hexdigest() != WHEEL_SHA:
    raise RuntimeError('BLOCKED_COMPONENT_INTEGRITY')
sys.path.insert(0, str(wheel))
import fastjsonschema

SCHEMA = {
    'type': 'object',
    'required': ['repository', 'commit', 'path', 'remote_blob_sha', 'scope'],
    'properties': {
        'repository': {'type': 'string', 'pattern': r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$'},
        'commit': {'type': 'string', 'pattern': r'^[0-9a-f]{40}$'},
        'remote_blob_sha': {'type': 'string', 'pattern': r'^[0-9a-f]{40}$'},
        'path': {'type': 'string', 'minLength': 1, 'pattern': r'^(?!/)(?!.*\.\.)[^\\]+$'},
        'scope': {'type': 'string', 'minLength': 1},
    },
}
validate = fastjsonschema.compile(SCHEMA, use_default=False)

def valid_proof(proof):
    try:
        validate(proof)
        return True
    except fastjsonschema.JsonSchemaException:
        return False
