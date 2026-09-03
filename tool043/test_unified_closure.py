"""Regression for actual TOOL044 closure stranded in the night queue."""
import copy
import json
from pathlib import Path
from unittest.mock import patch
import night_observer as observer

root = observer.ROOT
read = lambda name: json.loads((root / name).read_text(encoding='utf-8'))
args = [read('feedback_pipeline/work16_root_ledger.json'),
        read('feedback_pipeline/evidence/work16_root_report.json'),
        read('feedback_pipeline/unified_open_ledger.json'),
        read('feedback_pipeline/evidence/work_execution_audit_20260827.json'),
        read('feedback_pipeline/incomplete_register.json'),
        read('tool043/night_queue.json')]
pilot = 'TOOL044-READY-COMPONENT-PILOT'
expected = {'T41-T42-NATIVE-AUTOMATION', 'HOLD-T6-PUBLISHER-GOLDEN-PAIR',
            'HOLD-T7-CHATGPT-NATIVE-INTERCEPTOR', 'HOLD-T1-VERIFIED-REPORT-ACQUISITION'}
result = observer.current_work(*args)
assert result['conservation_pass'], result['errors']
assert {r['root_id'] for r in result['remaining']} == expected
assert result['pending_total'] == 0 and result['waiting_total'] == 4
assert any(r['root_id'] == pilot for r in result['recent_completed'])
missing = copy.deepcopy(args)
next(r for r in missing[2]['entries'] if r['root_id'] == pilot).pop('completion_evidence')
blocked = observer.current_work(*missing)
assert 'UNPROVEN_COMPLETION:' + pilot in blocked['errors']
assert pilot in {r['root_id'] for r in blocked['remaining']}
conflict = copy.deepcopy(args)
conflict[0]['roots'].append({'id': pilot, 'status': 'OPEN'})
assert pilot in {r['root_id'] for r in observer.current_work(*conflict)['remaining']}
status, queue = observer.build()
assert status['observer_health'] == 'OK'
assert status['current_work']['conservation_pass']
assert pilot not in {r.get('root_id') for r in queue['items']}
observer.self_test()
print(json.dumps({'status':'PASS', 'input':'current canonical ledgers and stale night queue',
    'expected_remaining':sorted(expected), 'actual_remaining':sorted(r['root_id'] for r in result['remaining']),
    'missing_proof_blocked':True, 'conflicting_open_preserved':True,
    'projection_health':'OK', 'TOOL013_tests_repeated':0}))
