"""Dedicated TOOL041/042 execution entry. Exactly one response, after final gate.

stdin: {tool, customer_id, task, mode}. No caller review/verified/context fields.
Modes: history_question; sales_material remains HOLD until canonical materials
are connected. No HTTP server, browser integration or general-chat interception.
"""
from __future__ import annotations
import base64
import csv
import importlib.util
import io
import json
import os
import sys
from pathlib import Path
import customer_release_gate as gate
from customer_model_adapter import ResponsesModel

TOOL42 = 'obk369369-spec/07-wic-setting-tool-v1'


class Hold(Exception):
    pass


def configuration():
    missing = []
    for name in ('OPENAI_API_KEY', 'WIC_MODEL', 'WIC_TOOL041_ROOT'):
        if not os.environ.get(name):
            missing.append(name)
    if not (os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')):
        missing.append('GITHUB_CONTENTS_READ_WRITE_AUTH')
    return missing


class Runtime:
    def __init__(self):
        root = Path(os.environ['WIC_TOOL041_ROOT']).resolve()
        spec = importlib.util.spec_from_file_location('_wic41_mvp', root / 'src/customer_work_start.py')
        sys.path.insert(0, str(root / 'src'))
        self.native = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.native)
        self.root = root
        self.model = ResponsesModel()
        self.locations = {}

    def load(self):
        # Reuse canonical reader. Never execute fetched code or read old fixtures.
        context = self.native.load_canonical()
        self.locations = dict(self.native.SOURCES)
        rev = self.native.api(TOOL42 + '/git/ref/heads/main')['object']['sha']
        context['revisions'][TOOL42] = rev
        additions = {'tool42_master': 'docs/UNIFIED_CUSTOMER_GUIDANCE_RULES.md',
                     'tool42_checkpoint': 'docs/CHAT_42_CUSTOMER_GUIDANCE_WORK_PROGRESS.md'}
        for key, path in additions.items():
            blob = self.native.api(TOOL42 + '/contents/' + path + '?ref=' + rev)
            context[key] = base64.b64decode(blob['content']).decode('utf-8-sig')
            context['source_sha256'][key] = gate.digest(context[key])
            self.locations[key] = (TOOL42, path)
        # Verify the locally reused generator/guard is the same pinned native code.
        repo = self.native.TOOL
        for path in ('src/customer_work_start.py', 'src/customer_integrity.py'):
            blob = self.native.api(repo + '/contents/' + path + '?ref=' + context['revisions'][repo])
            remote = base64.b64decode(blob['content']).decode('utf-8-sig')
            if (self.root / path).read_text(encoding='utf-8-sig') != remote:
                raise Hold('NATIVE_CODE_REVISION_MISMATCH')
        return context

    def customer(self, request, context):
        rows = list(csv.DictReader(io.StringIO(context['customers'])))
        matches = [row for row in rows if row.get('고유번호') == request['customer_id']]
        if len(matches) != 1:
            raise Hold('CUSTOMER_EVIDENCE_REQUIRED')
        row = matches[0]
        if not row.get('접촉이력') or not row.get('공식출처'):
            raise Hold('CUSTOMER_HISTORY_EVIDENCE_REQUIRED')
        candidate = {key: row.get(key, '') for key in
                     ('고유번호', '기관', '부서', '직책', '이메일', '전화번호', '관심분야', '후속조치', '검증상태')}
        candidate.update({'성명': row.get('이름', ''), '담당업무_연구분야': row.get('담당업무', ''),
                          '접촉이력_고객반응': row['접촉이력'] + '\n' + row.get('고객반응', ''),
                          '출처': row['공식출처']})
        checked = self.native._guard_against_current_master(candidate, rows)
        if checked['status'] != 'PASS_CURRENT_MASTER_MATCH_ONLY':
            raise Hold(checked['reason'])
        # Reuse existing integrity generation, still private until final review.
        generated = self.native._merge_customer_rows(checked['rows'])
        if any(str(item.get('검증상태', '')).startswith('HOLD') for item in generated):
            raise Hold('CUSTOMER_INTEGRITY_HOLD')
        return row, generated

    def unchanged(self, context):
        # Final freshness is an incremental source check, not a customer audit.
        for key, (repo, path) in self.locations.items():
            if key == 'central_checkpoint':
                continue  # Observer timestamps are not customer rules/evidence.
            blob = self.native.api(repo + '/contents/' + path + '?ref=main')
            current = base64.b64decode(blob['content']).decode('utf-8-sig')
            if gate.digest(current) != context['source_sha256'][key]:
                return False
        return True

    def persist(self, receipt):
        return gate.save_central(receipt)


def validate_review(result, packet):
    if not isinstance(result, dict) or set(result) != {'checks'}:
        raise Hold('INVALID_SEMANTIC_RESPONSE')
    checks = result['checks']
    if not isinstance(checks, dict) or set(checks) != set(gate.CATEGORIES):
        raise Hold('INCOMPLETE_EIGHT_CATEGORY_REVIEW')
    allowed_refs = set(packet['rules']) | {'customer'}
    for value in checks.values():
        if (not isinstance(value, dict) or set(value) != {'verdict', 'reason', 'evidence_refs'}
                or value['verdict'] not in ('PASS', 'FAIL', 'HOLD')
                or not isinstance(value['reason'], str) or not value['reason'].strip()
                or not isinstance(value['evidence_refs'], list) or not value['evidence_refs']
                or any(not isinstance(ref, str) or ref not in allowed_refs for ref in value['evidence_refs'])):
            raise Hold('UNBOUND_SEMANTIC_RESPONSE')
    return {key: value['verdict'] for key, value in checks.items()}


def execute(request, runtime):
    stages = []
    rewrite_count = 0
    last_digest = None
    verdicts = {key: 'NOT_EXECUTED' for key in gate.CATEGORIES}
    persist_attempted = False
    saved = None
    try:
        if (not isinstance(request, dict) or set(request) - {'tool', 'customer_id', 'task', 'mode'}
                or request.get('tool') not in ('TOOL041', 'TOOL042')
                or not isinstance(request.get('customer_id'), str) or not request['customer_id'].strip()
                or not isinstance(request.get('task'), str) or not request['task'].strip()
                or len(request['task']) > 4000):
            raise Hold('INVALID_CUSTOMER_REQUEST')
        context = runtime.load()
        stages.append('CENTRAL_LATEST_LOADED')
        preflight = gate.evaluate({'context': context})
        if preflight['reason'] != 'SEMANTIC_REVIEW_RUNTIME_NOT_CONNECTED':
            raise Hold(preflight['reason'])
        customer, rows = runtime.customer(request, context)
        stages.append('CUSTOMER_HISTORY_FEEDBACK_APPLIED')
        if request.get('mode') != 'history_question':
            raise Hold('ACTUAL_MATERIALS_EVIDENCE_REQUIRED')
        rules = {key: context[key] for key in ('central_master', 'copy_rules', 'feedback', 'master',
                                               'checkpoint', 'tool42_master', 'tool42_checkpoint')}
        packet = {'rules': rules, 'customer': customer, 'request': request,
                  'tool041_result': rows, 'source_sha256': context['source_sha256']}
        body, generation_id = runtime.model.generate(packet)
        stages.append('GENERATED_PRIVATE')
        for attempt in range(2):
            if not isinstance(body, str) or not body.strip() or len(body) > 20000:
                raise Hold('INVALID_PRIVATE_DRAFT')
            draft = {'body': body, 'rows': rows if request['tool'] == 'TOOL041' else []}
            last_digest = gate.digest({'draft': draft, 'context': gate.digest(packet)})
            review, review_id = runtime.model.review(packet, json.dumps(draft, ensure_ascii=False))
            if not isinstance(review_id, str) or not review_id:
                raise Hold('REVIEW_RESPONSE_ID_REQUIRED')
            verdicts = validate_review(review, packet)
            stages.append('SEMANTIC_REVIEW_' + str(attempt + 1))
            # Reuse existing explicit-FAIL filter; its historical rewrite hash
            # is diagnostic only, never used as this MVP's semantic rewrite.
            legacy = gate.evaluate({'context': context, 'draft': draft})
            if legacy['reason'] != 'SEMANTIC_REVIEW_RUNTIME_NOT_CONNECTED':
                raise Hold(legacy['reason'])
            rejected = legacy.get('rejected_case_ids', [])
            if not rejected and all(value == 'PASS' for value in verdicts.values()):
                if not runtime.unchanged(context):
                    raise Hold('CANONICAL_CHANGED_DURING_WORK')
                receipt = {'status': 'PASS', 'reason': 'DEDICATED_MVP_SEMANTIC_PASS',
                           'draft_sha256': last_digest, 'rewrite_count': rewrite_count,
                           'semantic_checks': verdicts, 'rejected_case_ids': []}
                persist_attempted = True
                saved = runtime.persist(receipt)
                if saved.get('status') not in ('PASS', 'SKIP_REUSE'):
                    raise Hold('NATIVE_CENTRAL_SAVE_REQUIRED')
                stages.extend(['CENTRAL_SAVED', 'PASS_OUTPUT'])
                return {**receipt, 'output_allowed': True, 'body': body,
                        'rows': draft['rows'], 'stages': stages, 'native_central_save': saved,
                        'generation_response_id': generation_id, 'review_response_id': review_id,
                        'send_allowed': False}
            if attempt == 1:
                raise Hold('SEMANTIC_REVIEW_FAILED_AFTER_ONE_REWRITE')
            body, generation_id = runtime.model.generate(packet, previous=body,
                                                         review={'semantic': review, 'rejected_case_ids': rejected})
            rewrite_count = 1
            stages.append('REWRITTEN_PRIVATE_ONCE')
    except Exception as exc:
        reason = str(exc) if isinstance(exc, Hold) else 'EXECUTION_OR_MODEL_UNAVAILABLE'
        result = gate.blocked(reason, stages=stages, rewrite_count=rewrite_count,
                              draft_sha256=last_digest, semantic_checks=verdicts)
        if persist_attempted:
            result['native_central_save'] = saved or {'status': 'HOLD', 'reason': 'NATIVE_CENTRAL_SAVE_UNAVAILABLE'}
        else:
            try:
                result['native_central_save'] = runtime.persist(result)
            except Exception:
                result['native_central_save'] = {'status': 'HOLD', 'reason': 'NATIVE_CENTRAL_SAVE_UNAVAILABLE'}
        return result


def main():
    missing = configuration()
    if missing:
        result = gate.blocked('AUTH_OR_RUNTIME_CONFIGURATION_REQUIRED', missing=missing)
    else:
        try:
            raw = sys.stdin.read(16385)
            if len(raw) > 16384:
                raise ValueError('REQUEST_TOO_LARGE')
            result = execute(json.loads(raw), Runtime())
        except Exception:
            result = gate.blocked('REQUEST_OR_NATIVE_RUNTIME_UNAVAILABLE')
    # The only production stdout write. No draft streaming, preview or temp file.
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get('output_allowed') is True else 2


if __name__ == '__main__':
    raise SystemExit(main())
