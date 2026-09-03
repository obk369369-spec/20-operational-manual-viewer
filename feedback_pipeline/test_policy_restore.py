"""Narrow common-policy restoration regression, not a remote execution claim."""
import io
import json
import re
import subprocess
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
import work_gate_handoff as gate

ROOT = Path(__file__).resolve().parents[1]
COMMON = 'feedback_pipeline/WIC_WORK_COMMON_EXECUTION_BLOCK.md'
def git_file(rev, path):
    return subprocess.check_output(['git', 'show', f'{rev}:{path}'], cwd=ROOT)

def run():
    old = git_file('0509f464', COMMON).decode('utf-8')
    baseline = git_file('1a79d25d', COMMON).decode('utf-8')
    current = (ROOT / COMMON).read_text(encoding='utf-8')
    for text in (old, baseline):
        for line in text.splitlines():
            if re.match(r'^[A-Z][A-Z0-9_]* = ', line) or line.startswith('## '):
                assert line in current, ('lost policy', line)
    state = json.loads(git_file('1a79d25d', 'tool043/status.json'))
    class Clock(datetime):
        @staticmethod
        def now(tz=None):
            return datetime.fromisoformat(state['observer_generated_at'].replace('Z', '+00:00')) + timedelta(seconds=1)
    def reply(req, timeout=30):
        url = req.full_url
        if '/git/ref/' in url:
            return io.BytesIO(json.dumps({'object': {'sha': '1a79d25d15c97126e152927f9ad9632ef4526ec3'}}).encode())
        path = url.split('/1a79d25d15c97126e152927f9ad9632ef4526ec3/')[1]
        return io.BytesIO(current.encode() if path == COMMON else git_file('1a79d25d', path))
    candidate = json.loads((ROOT / 'feedback_pipeline/evidence/parallel_lane_admission_20260903.json').read_text())
    with patch.object(gate, 'urlopen', reply), patch.object(gate, 'datetime', Clock):
        result = gate.load_latest_resume(candidate)
        assert result['status'] == 'RESUME_LOADED'
        assert result['execution_allowed'] is True, result['work_admission']
        assert gate.load_latest_resume()['execution_allowed'] is False
        current = baseline
        try:
            gate.load_latest_resume(candidate)
            raise AssertionError('Missing policy accepted')
        except ValueError as exc:
            assert str(exc) == 'Permanent common Work policy missing'
    print(json.dumps({'test':'common-policy-restore','expected':'preserve old/new policy, admit valid candidate, reject missing policy and candidate-less execution','actual':'matched','pass':True,'scope':'pinned canonical input replay; live remote resume still required'}))

if __name__ == '__main__':
    run()
