"""Actual canonical input + malformed-proof negative cases; no TOOL013 rerun."""
import copy
import json
import sys
from pathlib import Path
import night_observer as observer

root = observer.ROOT
read = lambda p: json.loads((root / p).read_text(encoding='utf-8'))
args = [read('feedback_pipeline/work16_root_ledger.json'),
        read('feedback_pipeline/evidence/work16_root_report.json'),
        read('feedback_pipeline/unified_open_ledger.json'),
        read('feedback_pipeline/evidence/work_execution_audit_20260827.json'),
        read('feedback_pipeline/incomplete_register.json'), read('tool043/night_queue.json')]
pilot = 'TOOL044-READY-COMPONENT-PILOT'
expected = {r['root_id'] for r in args[2]['entries'] if r['root_id'] != pilot}
before = observer.current_work(*args)
assert before['conservation_pass'], before['errors']
assert {r['root_id'] for r in before['remaining']} == expected
proof = next(r['completion_evidence'] for r in args[2]['entries'] if r['root_id'] == pilot)
invalid = [True, 'PASS', {'commit': 'invalid'}, dict(proof, path='../fake.json'), dict(proof, remote_blob_sha=''), dict(proof, repository='')]
for bad in invalid:
    altered = copy.deepcopy(args)
    next(r for r in altered[2]['entries'] if r['root_id'] == pilot)['completion_evidence'] = bad
    result = observer.current_work(*altered)
    assert not result['conservation_pass']
    assert pilot in {r['root_id'] for r in result['remaining']}
    assert 'INVALID_COMPLETION_PROOF:' + pilot in result['errors']
observer.self_test()
status, queue = observer.build()
assert status['observer_health'] == 'OK'
assert {r['root_id'] for r in status['current_work']['remaining']} == expected
report = {'status': 'PASS', 'entry': str(Path(observer.__file__).resolve()),
          'input': 'Actual canonical ledger/previous night queue',
          'expected_remaining': sorted(expected), 'actual_remaining': sorted(r['root_id'] for r in before['remaining']),
          'invalid_proof_cases_blocked': len(invalid), 'valid_pilot_preserved': True,
          'regression': 'observer conservation/self-test', 'TOOL013_tests_repeated': 0}
if len(sys.argv) == 2:
    Path(sys.argv[1]).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
