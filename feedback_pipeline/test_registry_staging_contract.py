"""Regression for actual TOOL014 staging status, without running TOOL014."""
import copy
import json
from pathlib import Path
from global_pipeline import REGISTRY, validate_registry

def run():
    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    original = copy.deepcopy(registry['targets']['TOOL014'])
    assert original['status'] == 'STAGING_REMOTE_VERIFIED'
    assert original['hold_reason'] == 'LIVE_HOMEPAGE_APPLY_REQUIRES_EXPLICIT_AUTHORIZATION'
    validate_registry(registry, target='TOOL014')
    assert registry['targets']['TOOL014'] == original
    tested = ['actual staging accepted unchanged']
    for status, reject in [('ACTIVE',False),('MADE_UP_PASS',True),('COMPLETE',True)]:
        candidate = copy.deepcopy(registry)
        candidate['targets']['TOOL014']['status'] = status
        if status == 'COMPLETE':
            candidate['targets']['TOOL014']['first_validation'] = {}
        try:
            validate_registry(candidate,target='TOOL014')
        except ValueError:
            assert reject, status
        else:
            assert not reject, status
        tested.append(status + (' rejected' if reject else ' accepted'))
    result = {'status':'PASS','input':'actual wic_target_registry TOOL014 entry',
              'expected':'staging accepted unchanged, ACTIVE preserved, unknown and unproved COMPLETE rejected',
              'actual':tested,'tool014_runtime_tested':False}
    print(json.dumps(result))

if __name__ == '__main__': run()
