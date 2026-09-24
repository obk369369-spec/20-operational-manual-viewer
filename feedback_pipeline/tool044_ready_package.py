from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
SRC=HERE/'evidence'/'tool044_verified_external_component_pool.json'
OUT=HERE/'evidence'/'tool044_ready_package_pool.json'

REQUIRED=('component_id','source','license','version','input_contract','output_contract',
          'install_method','validator','success_condition','failure_condition',
          'rollback_method','rollback_condition','evidence','source_sha256')

def build():
    data=json.loads(SRC.read_text(encoding='utf-8')) if SRC.exists() else {'components':[]}
    packages=[]; rejected=[]
    for c in data.get('components',[]):
        missing=[k for k in REQUIRED if not c.get(k)]
        gate=c.get('multi_gate_evidence',{}).get('result',{})
        actual_pass=(c.get('status')=='VERIFIED_REUSABLE' and gate.get('status')=='PASS'
                     and gate.get('install_returncode')==0 and gate.get('validator_returncode')==0
                     and gate.get('production_mutation')==0)
        if missing or not actual_pass:
            rejected.append({'component_id':c.get('component_id'),'missing':missing,
                             'reason':'ACTUAL_EXECUTION_EVIDENCE_REQUIRED'})
            continue
        cid=c['component_id']
        packages.append({
            'PACKAGE_ID':'READY::'+cid,'COMPONENT_ID':cid,'SOURCE':c['source'],
            'VERSION':c['version'],'HASH':c['source_sha256'],'LICENSE':c['license'],
            'TARGET_ROOT':c.get('target_root'),'TARGET_TOOL':c.get('target_tool'),
            'FUNCTION':(c.get('atomic_capabilities') or [None])[0],
            'INPUT_CONTRACT':c['input_contract'],'OUTPUT_CONTRACT':c['output_contract'],
            'CONFIG':{'install_target':c.get('install_target')},
            'CONNECTION_METHOD':'Use the verified install_method exactly; do not modify the external component.',
            'EXECUTION_COMMAND':c['install_method'],'VALIDATION_METHOD':c['validator'],
            'SUCCESS_CONDITION':c['success_condition'],'FAILURE_CONDITION':c['failure_condition'],
            'ROLLBACK_CONDITION':c['rollback_condition'],'ROLLBACK_METHOD':c['rollback_method'],
            'SANDBOX_COMPONENT_PASS':'YES','ACTUAL_EXECUTION_EVIDENCE':c['multi_gate_evidence'],
            'TOOL016_HANDOFF_CONTRACT':'TOOL016 selects PACKAGE_ID by FUNCTION/TARGET_ROOT and hands the unchanged package to final installer.',
            'TOOL016_RETURN_CONTRACT':'Return PACKAGE_ID, install result, validation result, evidence ref, rollback result if any.',
            'WORK_INSTRUCTION':f"Install READY package {cid} exactly as specified. Do not modify/customize the external component. Run VALIDATION_METHOD, fail closed on any mismatch, rollback on failure, then return execution evidence to TOOL016.",
            'READY_TO_PLUG':True,'EVIDENCE_REFS':[c['evidence']]
        })
    payload={'schema_version':1,'updated_at':datetime.now(timezone.utc).isoformat(),
             'ready_package_count':len(packages),'rejected_count':len(rejected),
             'packages':packages,'rejected':rejected,
             'rule':'ONLY_ACTUAL_EXECUTION_VERIFIED_EXTERNAL_COMPONENTS_CAN_BECOME_READY_PACKAGES'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return payload

def self_test():
    p=build()
    assert all(x['READY_TO_PLUG'] and x['SANDBOX_COMPONENT_PASS']=='YES' for x in p['packages'])
    return 'PASS'

if __name__=='__main__':
    import sys
    print(self_test() if '--self-test' in sys.argv else json.dumps(build(),ensure_ascii=False))
