"""One actual canonical registration record through the existing transport."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import global_pipeline as pipeline
data = json.loads(Path(__file__).with_name('tool012_connection_actual_input.json').read_text(encoding='utf-8'))
def forbidden(*args, **kwargs):
    raise AssertionError('Completed TOOL012 must not invoke downstream work')
pipeline.command = forbidden
pipeline.load_master_context = forbidden
event = {'event_kind':'CANONICAL_CONNECTION_CHECK','source_chat':'TOOL012',
         'source_ref':'CENTRAL#CI-TOOL012-NOT-ACTIVE','feedback':'Reuse actual verified TOOL012 completion without redeveloping or retesting'}
result = pipeline.execute_actual_transport(event, data, Path.cwd())
assert result['status'] == 'SKIP_REUSE', result
assert result['evidence']['run_id'] == '33310342582'
assert result['evidence']['commit'] == '11bac27ed8a7f594c6e965d5c534c0c6e422b987'
assert result['execution_allowed'] is False
print(json.dumps({'actual_record_count':1,'result':result,'existing_tool_tests':0,'subprocess_or_mutation_calls':0}))
