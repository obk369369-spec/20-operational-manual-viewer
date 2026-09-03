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
from pathlib import Path
from urllib.request import urlopen

COMPONENT = 'idb-keyval@6.2.2'
URL = 'https://registry.npmjs.org/idb-keyval/-/idb-keyval-6.2.2.tgz'
INTEGRITY = 'yjD9nARJ/jb1g+CvD0tlhUHOrJ9Sy0P8T9MF3YaLlHnSRpwPfpTX0XIvpmw3gAJUmEu3FiICLBDPXVwyEvrleg=='
SCRIPT_SHA256 = 'f5985c43b11e4f99700e0c97a0d44ac129821f227f17c60afd7de8d421db5a58'
MEMBERS = ('package/dist/umd.js', 'package/LICENCE', 'package/package.json')

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
    args=parser.parse_args()
    if args.acquire:
        result=acquire(args.acquire)
    elif args.target and args.deployed:
        result=verify_deployment(args.target,args.deployed)
    else:
        parser.error('Use --acquire DIR or --target DIR --deployed DIR')
    print(json.dumps(result,ensure_ascii=False,indent=2))
