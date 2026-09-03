"""TOOL044 bounded acquisition of the first verified external component.

Fetch exact upstream bytes, never patch them. Cached verified downloads are reused.
Acquisition is NOT business/deployment PASS; those require the target's real tests.
"""
import argparse
import base64
import hashlib
import io
import json
import tarfile
import subprocess
import shutil
import sys
import zipfile
import os
from pathlib import Path
from urllib.request import urlopen

COMPONENT = 'idb-keyval@6.2.2'
URL = 'https://registry.npmjs.org/idb-keyval/-/idb-keyval-6.2.2.tgz'
INTEGRITY = 'yjD9nARJ/jb1g+CvD0tlhUHOrJ9Sy0P8T9MF3YaLlHnSRpwPfpTX0XIvpmw3gAJUmEu3FiICLBDPXVwyEvrleg=='
SCRIPT_SHA256 = 'f5985c43b11e4f99700e0c97a0d44ac129821f227f17c60afd7de8d421db5a58'
MEMBERS = ('package/dist/umd.js', 'package/LICENCE', 'package/package.json')

PRODUCTION_ROOT = 'TOOL044-PRODUCTION-TOOL043-PROOF-CONTRACT'
WHEEL = 'fastjsonschema-2.21.2-py3-none-any.whl'
WHEEL_SHA = '1c797122d0a86c5cace2e54bf4e819c36223b552017172f32c5c024a6b77e463'

def run_command(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, text=True, encoding='utf-8', errors='replace',
                            capture_output=True, timeout=180, env={**os.environ, 'PYTHONUTF8':'1', 'PYTHONDONTWRITEBYTECODE':'1'})
    if result.returncode:
        raise RuntimeError('COMMAND_BLOCKED: ' + str(argv[:3]) + '\n' + result.stderr[-2000:] + result.stdout[-2000:])
    return result.stdout.strip()

def proof_candidate():
    return dict(root_id=PRODUCTION_ROOT, operation_id='production-proof-contract-deploy',
        directive_ref='USER_TOOL044_PRODUCTION_FINISH', action='REPAIR_AND_DEPLOY',
        target_assets=['TOOL044','TOOL043','VERIFIED_COMPONENT_REGISTRY'],
        gates=dict(chat_files=False,github=False,ordinary_runtime=False),
        blocker='Acquisition-only runtime lacks tested target integration and deployment',
        restart_point='Existing TOOL044 acquire / TOOL043 current_work',
        target_repository='obk369369-spec/20-operational-manual-viewer',
        execution_goal='Deployed TOOL043 structured completion evidence validation',
        success_evidence='Actual canonical input comparison, malformed-proof negatives, deployed-copy test',
        rollback_point='7a8f293759cbbd86c3f5a4ecdf845dd4714f97c6')

def ready_proof_component(workspace):
    """One pinned free/local candidate; no package setup script or dependency execution."""
    cache = workspace / '.tool044_cache'
    cache.mkdir(exist_ok=True)
    wheel = cache / WHEEL
    if not wheel.exists():
        meta = json.loads(urlopen('https://pypi.org/pypi/fastjsonschema/2.21.2/json', timeout=30).read())
        candidate = next(r for r in meta['urls'] if r['filename'] == WHEEL)
        if candidate['digests']['sha256'] != WHEEL_SHA or candidate.get('yanked'):
            raise ValueError('NO_READY_COMPONENT: package identity')
        if not candidate['url'].startswith('https://files.pythonhosted.org/'):
            raise ValueError('NO_READY_COMPONENT: origin')
        data = urlopen(candidate['url'], timeout=30).read()
        if hashlib.sha256(data).hexdigest() != WHEEL_SHA:
            raise ValueError('NO_READY_COMPONENT: hash')
        wheel.write_bytes(data)
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != WHEEL_SHA:
        raise ValueError('BLOCKED_CACHED_COMPONENT')
    with zipfile.ZipFile(wheel) as package:
        license_name = next(n for n in package.namelist() if n.endswith('LICENSE'))
        license_bytes = package.read(license_name)
        if b'Redistribution and use in source and binary forms' not in license_bytes:
            raise ValueError('COPYRIGHT_HOLD')
    # Compile only a trusted local schema, never a remotely supplied schema/code.
    sys.path.insert(0, str(wheel))
    import fastjsonschema
    check = fastjsonschema.compile({'type':'object','required':['commit'],
        'properties':{'commit':{'type':'string','pattern':'^[0-9a-f]{40}$'}}}, use_default=False)
    check({'commit':'d20561e38831333043678f9c8ffa72b825f5bb84'})
    for bad in (True, 'PASS', {}, {'commit':'not-a-sha'}):
        try:
            check(bad)
        except fastjsonschema.JsonSchemaException:
            continue
        raise ValueError('NO_READY_COMPONENT: invalid evidence accepted')
    return wheel, license_bytes

def production(workspace, operating_root, prepare_only=False):
    """Execute the admitted existing TOOL043 adapter; unknown targets never run commands."""
    from work_gate_handoff import load_latest_resume
    resume = load_latest_resume(proof_candidate())
    if not resume['execution_allowed']:
        return {'status':resume['work_admission']['decision'], 'new_target_executed':False}
    workspace = workspace.resolve()
    operating_root = operating_root.resolve()
    if operating_root != Path('I:/GPT 도구 작업').resolve():
        raise ValueError('BLOCKED_OPERATING_ROOT')
    evidence = workspace / 'feedback_pipeline/evidence/tool044_production_run.json'
    if evidence.exists():
        prior = json.loads(evidence.read_text(encoding='utf-8'))
        if prior.get('status') == 'DEPLOYED_PASS':
            return {'status':'SKIP_REUSE','evidence':str(evidence)}
        raise ValueError('STOP_CARD: prior attempt requires cause review, no automatic retry')
    record = {'status':'IN_PROGRESS','root_id':PRODUCTION_ROOT,'stages':[], 'user_action_queue':[]}
    def stage(name, **facts):
        record['stages'].append({'stage':name, **facts})
        evidence.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    try:
        wheel, license_bytes = ready_proof_component(workspace)
        stage('READY_COMPONENT', candidate_count=1, search_stopped=True, sha256=WHEEL_SHA,
              expected='valid SHA accepted, four malformed inputs rejected', actual='MATCH')
        vendor = workspace / 'tool043/vendor'
        vendor.mkdir(exist_ok=True)
        shutil.copyfile(wheel, vendor / WHEEL)
        (vendor / 'LICENSE.fastjsonschema.txt').write_bytes(license_bytes)
        stage('UNMODIFIED_COMPONENT_INSTALLED')
        report = workspace / 'feedback_pipeline/evidence/tool043_proof_e2e.json'
        out = run_command([sys.executable,'-X','utf8','tool043/test_completion_proof.py',str(report)],workspace)
        result = json.loads(report.read_text(encoding='utf-8'))
        if result['status'] != 'PASS' or result['expected_remaining'] != result['actual_remaining']:
            raise ValueError('DEPLOY_BLOCKED_EXPECTED_ACTUAL')
        stage('TARGET_ACTUAL_INPUT_AND_REGRESSION_PASS', report=str(report.relative_to(workspace)))
        if prepare_only:
            record['status']='TESTED_NOT_PUBLISHED'
            evidence.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
            return record
        release_files = ['tool043/night_observer.py','tool043/completion_proof.py','tool043/test_completion_proof.py',
            'tool043/vendor/'+WHEEL,'tool043/vendor/LICENSE.fastjsonschema.txt',
            'feedback_pipeline/tool044_acquire.py','feedback_pipeline/TOOL044_MASTER.md',
            'feedback_pipeline/tool044_start.cmd','feedback_pipeline/evidence/tool043_proof_e2e.json', '.gitattributes']
        git = ['git','-c','safe.directory='+workspace.as_posix(),'-c','maintenance.auto=false']
        staged=run_command(git+['diff','--cached','--name-only'],workspace).splitlines()
        if set(staged)-set(release_files):
            raise ValueError('BLOCKED_UNRELATED_STAGED_FILES')
        run_command(git+['add','--']+release_files,workspace)
        run_command(git+['commit','-m','Deploy TOOL044 production adapter and TOOL043 verified proof component'],workspace)
        sha=run_command(git+['rev-parse','HEAD'],workspace)
        run_command(git+['push','origin','HEAD:main'],workspace)
        for name in release_files:
            remote=json.loads(run_command(['gh','api',f'repos/obk369369-spec/20-operational-manual-viewer/contents/{name}?ref={sha}'],workspace))
            if base64.b64decode(remote['content']) != (workspace/name).read_bytes():
                raise ValueError('REMOTE_BYTE_MISMATCH:'+name)
        stage('GITHUB_PUSH_READBACK_PASS', commit=sha)
        deploy43=operating_root/'43번 모바일 관찰판'
        deploy44=operating_root/'44번 완성부품 가져오기'
        # Explicit files only. Preserve all unrelated assets; no directory mirroring/deletion.
        inputs=['feedback_pipeline/work16_root_ledger.json','feedback_pipeline/evidence/work16_root_report.json',
            'feedback_pipeline/unified_open_ledger.json','feedback_pipeline/incomplete_register.json',
            'feedback_pipeline/approval_queue.json','feedback_pipeline/evidence/work_execution_audit_20260827.json']
        files43=[n for n in release_files if n.startswith('tool043/')]+inputs+[
            'tool043/index.html','tool043/status.json','tool043/night_queue.json','tool043/manifest.webmanifest','tool043/icon.svg']
        for folder,names in ((deploy43,files43),(deploy44,['feedback_pipeline/tool044_acquire.py',
                'feedback_pipeline/TOOL044_MASTER.md','feedback_pipeline/tool044_start.cmd',
                'feedback_pipeline/work_gate_handoff.py','feedback_pipeline/work_execution_enforcer.py',
                'feedback_pipeline/evidence_classification_gate.py'])):
            for name in names:
                dest=folder/name;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(workspace/name,dest)
                if dest.read_bytes() != (workspace/name).read_bytes():
                    raise ValueError('DEPLOY_BYTE_MISMATCH:'+name)
        stage('LOCAL_DEPLOYED', tool043=str(deploy43/'tool043/index.html'),
              tool044=str(deploy44/'feedback_pipeline/tool044_start.cmd'))
        deployed_report=workspace/'feedback_pipeline/evidence/tool043_proof_deployed.json'
        run_command([sys.executable,'-X','utf8',str(deploy44/'feedback_pipeline/tool044_acquire.py'),
            '--deployment-check',str(evidence)],deploy44)
        deployed_report = deploy44 / 'tool043_proof_deployed.json'
        stage('DEPLOYED_COPY_TEST_PASS', report=str(deployed_report))
        record['status']='DEPLOYED_PASS'
        record['safe_checkpoint']=sha
        evidence.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
        shutil.copyfile(deployed_report, workspace/'feedback_pipeline/evidence/tool043_proof_deployed.json')
        persisted=['feedback_pipeline/evidence/tool044_production_run.json','feedback_pipeline/evidence/tool043_proof_deployed.json']
        run_command(git+['add','--']+persisted,workspace)
        run_command(git+['commit','-m','Record actual deployed TOOL044 to TOOL043 production run'],workspace)
        evidence_sha=run_command(git+['rev-parse','HEAD'],workspace)
        run_command(git+['push','origin','HEAD:main'],workspace)
        for name in persisted:
            remote=json.loads(run_command(['gh','api',f'repos/obk369369-spec/20-operational-manual-viewer/contents/{name}?ref={evidence_sha}'],workspace))
            if base64.b64decode(remote['content']).decode('utf-8').replace('\r\n','\n') != (workspace/name).read_text(encoding='utf-8'):
                raise ValueError('EVIDENCE_READBACK_MISMATCH')
        registry_path=workspace/'feedback_pipeline/VERIFIED_COMPONENT_REGISTRY.json'
        registry=json.loads(registry_path.read_text(encoding='utf-8'))
        component={'component_id':'FASTJSONSCHEMA_2_21_2_TOOL043_PROOF','status':'VERIFIED_REUSABLE',
            'source_tool':'TOOL044','applied_tool':'TOOL043','license':'BSD-3-Clause',
            'source_file':'tool043/vendor/'+WHEEL,'source_sha256':WHEEL_SHA,'external_modified':False,
            'source_commit':sha,'evidence_commit':evidence_sha,'input_contract':'Structured completion proof',
            'output_contract':'Invalid proof retained as unresolved; valid canonical closure preserved',
            'test_evidence':persisted,'reuse_requires_target_retest':True}
        registry['components']=[r for r in registry['components'] if r.get('component_id')!=component['component_id']]+[component]
        registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        run_command(git+['add','--','feedback_pipeline/VERIFIED_COMPONENT_REGISTRY.json'],workspace)
        run_command(git+['commit','-m','Register deployed verified TOOL043 proof component'],workspace)
        run_command(git+['push','origin','HEAD:main'],workspace)
        record['evidence_commit']=evidence_sha
        return record
    except Exception as exc:
        record['status']='BLOCKED'
        record['error']=str(exc)
        record['next_start']='Review failed stage; preserve verified source/deployed assets; no same-method automatic retry'
        evidence.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
        raise

def validate_package(raw):
    if base64.b64encode(hashlib.sha512(raw).digest()).decode() != INTEGRITY:
        raise ValueError('BLOCKED_PACKAGE_INTEGRITY')
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        payload = {name: archive.extractfile(name).read() for name in MEMBERS}
    if hashlib.sha256(payload[MEMBERS[0]]).hexdigest() != SCRIPT_SHA256:
        raise ValueError('BLOCKED_EXTERNAL_MODIFICATION')
    meta = json.loads(payload[MEMBERS[2]])
    if meta['version'] != '6.2.2' or meta['license'] != 'Apache-2.0' or meta.get('dependencies'):
        raise ValueError('BLOCKED_COMPONENT_CONTRACT')
    return payload

def acquire(destination):
    destination.mkdir(parents=True, exist_ok=True)
    package = destination / 'idb-keyval-6.2.2.tgz'
    reused = package.exists()
    raw = package.read_bytes() if reused else urlopen(URL, timeout=30).read()
    payload = validate_package(raw)
    if not reused:
        package.write_bytes(raw)
    for name, content in payload.items():
        output = destination / name
        if output.exists():
            if output.read_bytes() != content:
                raise ValueError('BLOCKED_EXISTING_ASSET_MISMATCH: ' + str(output))
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
    return {'component': COMPONENT, 'status': 'VERIFIED_DOWNLOAD_REUSED' if reused else 'DOWNLOAD_VERIFIED',
            'network_requests': 0 if reused else 1, 'external_modified': False,
            'business_pass': False, 'next': 'Target EXPECTED/ACTUAL, regression, remote and deployed-copy tests required'}

def verify_deployment(target, deployed):
    source_report = json.loads((target/'tests/tool13_idb_resume_evidence.json').read_text(encoding='utf-8'))
    report = json.loads((target/'tests/tool13_idb_deployed_evidence.json').read_text(encoding='utf-8'))
    for evidence, entry in ((source_report,target/'index.html'), (report,deployed/'index.html')):
        if evidence['status'] != 'PASS' or Path(evidence['entry']).resolve() != entry.resolve():
            raise ValueError('BLOCKED_TEST_EVIDENCE')
        if not all(evidence.get(key) for key in ('real_source_title_preserved','all_titles_and_descriptions_exact','reset_durable')):
            raise ValueError('BLOCKED_EXPECTED_ACTUAL')
    hashes = {}
    for name in ('index.html','vendor/idb-keyval-6.2.2.js','vendor/LICENSE.idb-keyval.txt'):
        raw=(target/name).read_bytes()
        if raw != (deployed/name).read_bytes():
            raise ValueError('BLOCKED_DEPLOYED_COPY_MISMATCH: '+name)
        hashes[name]=hashlib.sha256(raw).hexdigest()
    if hashes['vendor/idb-keyval-6.2.2.js'] != SCRIPT_SHA256:
        raise ValueError('BLOCKED_EXTERNAL_MODIFICATION')
    return {'component':COMPONENT,'status':'DEPLOYED_EVIDENCE_REUSED','sha256':hashes,'tests_repeated':0}

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--acquire',type=Path)
    parser.add_argument('--target',type=Path)
    parser.add_argument('--deployed',type=Path)
    parser.add_argument('--production', action='store_true')
    parser.add_argument('--workspace', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--operating-root', type=Path, default=Path('I:/GPT 도구 작업'))
    parser.add_argument('--deployment-check', type=Path)
    args=parser.parse_args()
    if args.deployment_check:
        proof=json.loads(args.deployment_check.read_text(encoding='utf-8'))
        required={'READY_COMPONENT','TARGET_ACTUAL_INPUT_AND_REGRESSION_PASS','GITHUB_PUSH_READBACK_PASS','LOCAL_DEPLOYED'}
        if not required.issubset({s['stage'] for s in proof['stages']}):
            raise ValueError('COMPLETE_BLOCKED')
        deployed43 = Path('I:/GPT 도구 작업/43번 모바일 관찰판')
        deployed44 = Path('I:/GPT 도구 작업/44번 완성부품 가져오기')
        report = deployed44/'tool043_proof_deployed.json'
        run_command([sys.executable,'-X','utf8',str(deployed43/'tool043/test_completion_proof.py'),str(report)],deployed43)
        actual=json.loads(report.read_text(encoding='utf-8'))
        if actual['status'] != 'PASS' or actual['expected_remaining'] != actual['actual_remaining']:
            raise ValueError('DEPLOYED_EXPECTED_ACTUAL_FAIL')
        result={'status':'DEPLOYED_EXECUTOR_CHECK_PASS','target_deployed_e2e':actual}
    elif args.production:
        result=production(args.workspace,args.operating_root)
    elif args.acquire:
        result=acquire(args.acquire)
    elif args.target and args.deployed:
        result=verify_deployment(args.target,args.deployed)
    else:
        parser.error('Use --acquire DIR or --target DIR --deployed DIR')
    print(json.dumps(result,ensure_ascii=False,indent=2))
