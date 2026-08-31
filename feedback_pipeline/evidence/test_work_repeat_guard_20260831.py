"""Bounded Work-record replay; no customer/model/CI execution."""
import copy
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from work_gate_handoff import evaluate_candidate
ledger = json.loads((Path(__file__).resolve().parents[1] / 'unified_open_ledger.json').read_text(encoding='utf-8'))
root = 'T41-T42-NATIVE-AUTOMATION'
results = []
def check(name, candidate, expected, state=ledger):
    result = evaluate_candidate(candidate, state)
    assert result['decision'] == expected, (name, result)
    assert result.get('execution_allowed') is False
    results.append({'case': name, 'decision': result['decision'], 'downstream_executions': 0})
check('41/42 completed MVP redevelopment', {'root_id':root,'operation_id':'dedicated-mvp-implementation'}, 'SKIP_REUSE')
check('41/42 completed blocking gate', {'root_id':root,'operation_id':'native-release-blocking-boundary'}, 'SKIP_REUSE')
check('41/42 unchanged auth/customer HOLD', {'root_id':root,'operation_id':'dedicated-mvp-live-e2e','trigger_observed':True}, 'SKIP_NO_VALUE')
check('same TOOL012 CI failure', {'root_id':'CI-TOOL012-NOT-ACTIVE','operation_id':'registry-ci-audit','cause_id':'TOOL012_NOT_ACTIVE','method_id':'UNCHANGED_GLOBAL_CI_AUDIT'}, 'SKIP_NO_VALUE')
check('repair is not new MVP approval', {'root_id':'CI-TOOL012-NOT-ACTIVE','operation_id':'new-mvp','action':'CREATE_MVP','directive_ref':'CURRENT_CHAT#repair','target_assets':['new-mvp']}, 'WORK_HOLD_SCOPE')
check('unrelated root', {'root_id':'UNREQUESTED','operation_id':'expand'}, 'WORK_HOLD_SCOPE')
state = copy.deepcopy(ledger)
state['execution_policy']['scope_grants'] = [{'root_id':'CI-TOOL012-NOT-ACTIVE','directive_ref':'CONTROL_ONLY','actions':['REPAIR'],'assets':['existing.py'],'reusable_assets':['existing.py']}]
candidate = {'root_id':'CI-TOOL012-NOT-ACTIVE','operation_id':'different-repair','action':'REPAIR','directive_ref':'CONTROL_ONLY','target_assets':['existing.py'],'gates':{'chat_files':False,'github':True,'ordinary_runtime':False}}
assert evaluate_candidate(candidate, state)['decision'] == 'WORK_DEFER_DENIED'
results.append({'case':'authorized repair retains cheaper lane gate','decision':'WORK_DEFER_DENIED','downstream_executions':0})
check('asset expansion', dict(candidate,target_assets=['new-db']), 'WORK_HOLD_SCOPE', state)
print(json.dumps({'status':'PASS','cases':results,'actual_customer_runs':0,'old_pass_tests':0},ensure_ascii=False))
