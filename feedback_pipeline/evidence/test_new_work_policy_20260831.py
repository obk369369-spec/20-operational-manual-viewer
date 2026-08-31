"""Three cold-process startup cases, captured GitHub transport, no real work."""
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime

if len(sys.argv) == 4 and sys.argv[1] == '--child':
    snapshot = json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import work_gate_handoff as handoff
    class SnapshotClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.fromisoformat(json.loads(snapshot['files']['tool043/status.json'])['observer_generated_at'])
    handoff.datetime = SnapshotClock
    def transport(request, **kwargs):
        url = request.full_url
        if url.endswith('/git/ref/heads/main'):
            return io.BytesIO(json.dumps({'object':{'sha':snapshot['head']}}).encode())
        prefix = 'https://raw.githubusercontent.com/obk369369-spec/20-operational-manual-viewer/' + snapshot['head'] + '/'
        assert url.startswith(prefix)
        return io.BytesIO(snapshot['files'][url[len(prefix):]].encode())
    handoff.urlopen = transport
    cases = [
        {'root_id':'T41-T42-NATIVE-AUTOMATION','operation_id':'dedicated-mvp-implementation'},
        {'root_id':'T41-T42-NATIVE-AUTOMATION','operation_id':'dedicated-mvp-live-e2e','trigger_observed':True},
        {'root_id':'CI-TOOL012-NOT-ACTIVE','operation_id':'unrequested-mvp','action':'CREATE_MVP','directive_ref':'CURRENT_CHAT#repair','target_assets':['new-mvp']},
    ]
    result = handoff.load_latest_resume(cases[int(sys.argv[3])])
    assert result['common_execution_block']['policy'] == 'PERMANENT_FAIL_CLOSED_V1'
    assert result['execution_allowed'] is False
    print(json.dumps({'decision':result['work_admission']['decision'],'execution_allowed':False,'common_block_loaded':True,'source_revision':result['central_revision']}))
else:
    snapshot = str(Path(sys.argv[1]).resolve())
    results = []
    for index, expected in enumerate(('SKIP_REUSE','SKIP_NO_VALUE','WORK_HOLD_SCOPE')):
        with tempfile.TemporaryDirectory(prefix='wic-cold-work-') as cwd:
            p = subprocess.run([sys.executable,'-I',str(Path(__file__).resolve()),'--child',snapshot,str(index)],cwd=cwd,capture_output=True,text=True,encoding='utf-8')
            assert p.returncode == 0, p.stderr
            result = json.loads(p.stdout)
            assert result['decision'] == expected, result
            results.append(result)
    print(json.dumps({'status':'PASS','cold_processes':3,'cases':results,'downstream_work_executions':0,'transport':'captured GitHub snapshot plus staged code; clock fixed at captured observer timestamp','ui_work_created':False}))
