from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / 'feedback_pipeline'
HANDOFF = PIPE / 'tool045_tool016_handoff.json'
RECEIPT = PIPE / 'tool016_tool045_receipt.json'
PENDING = PIPE / 'tool016_tool045_root_pending.json'
INBOX = PIPE / 'TOOL044_REQUEST_INBOX.json'
SOURCE_MANIFEST = PIPE / 'tool045_source_manifest.json'
ROOT_REVIEW = PIPE / 'tool016_tool045_root_review.json'

def now():
    return datetime.now(timezone.utc).isoformat()

def stable_id(record):
    raw = json.dumps(record, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:24]

def load_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    if not HANDOFF.exists():
        receipt = {
            'schema_version': 1,
            'source': 'TOOL045',
            'receiver': 'TOOL016',
            'received': False,
            'state': 'WAITING_FOR_TOOL045_HANDOFF',
            'received_at': now(),
            'record_count': 0,
            'eligible_for_tool044_count': 0,
            'tool044_handoff_count': 0,
            'truth_contract': 'RECEIVE_ONLY_UNTIL_ROOT_AND_MISSING_CAPABILITY_ARE_VERIFIED'
        }
        RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(receipt, ensure_ascii=False))
        return

    handoff = load_json(HANDOFF, {})
    records = handoff.get('records', []) or []
    seen = set()
    unique = []
    for r in records:
        oid = r.get('occurrence_id') or stable_id(r)
        if oid in seen:
            continue
        seen.add(oid)
        row = dict(r)
        row['occurrence_id'] = oid
        unique.append(row)

    existing_pending = load_json(PENDING, {'schema_version':1,'records':[]})
    existing_by_id = {r.get('occurrence_id'): r for r in existing_pending.get('records', []) if r.get('occurrence_id')}
    for r in unique:
        existing_by_id[r['occurrence_id']] = {
            **r,
            'tool016_receive_state': 'RECEIVED',
            'root_review_state': 'PENDING_VERIFICATION' if r.get('root') in (None, '', 'ROOT_UNVERIFIED') else 'ROOT_PRESENT_UNVERIFIED',
            'missing_capability_review_state': 'PENDING_VERIFICATION' if r.get('missing_capability') in (None, '', 'MISSING_CAPABILITY_UNVERIFIED') else 'CAPABILITY_PRESENT_UNVERIFIED'
        }
    pending_records = list(existing_by_id.values())
    pinned_manifest = load_json(SOURCE_MANIFEST, {})
    root_review = load_json(ROOT_REVIEW, {})
    pinned_review_available = bool(not pending_records and pinned_manifest and root_review)

    eligible = []
    for r in pending_records:
        status = r.get('status')
        root = r.get('root')
        cap = r.get('missing_capability')
        if status == 'RESOLVED_VERIFIED':
            continue
        if not root or root == 'ROOT_UNVERIFIED':
            continue
        if not cap or cap == 'MISSING_CAPABILITY_UNVERIFIED':
            continue
        if r.get('missing_capability_verified') is not True:
            continue
        eligible.append(r)

    inbox = load_json(INBOX, {'schema_version':1,'purpose':'Persistent TOOL016 intake for TOOL044','requests':[]})
    requests = inbox.setdefault('requests', [])
    existing_req = {q.get('request_id') for q in requests}
    added = 0
    for r in eligible:
        rid = f"TOOL045-{r['occurrence_id']}"
        if rid in existing_req:
            continue
        requests.append({
            'request_id': rid,
            'tool_or_program_name': r.get('tool_id', 'TOOL_UNCERTAIN'),
            'related_tool': 'TOOL016',
            'source_chat_or_tool': r.get('source_chat') or r.get('source_id'),
            'root_id': r.get('root'),
            'original_error_or_feedback': r.get('original_feedback'),
            'occurrence_or_evidence': f"TOOL045 occurrence {r['occurrence_id']}",
            'purpose': 'Resolve verified missing capability derived from TOOL045 historical conversation evidence after TOOL016 ROOT review.',
            'desired_result': 'Verified reusable component or capability path without duplicating an already-verified WIC component.',
            'required_capabilities': [r.get('missing_capability')],
            'current_status': 'MISSING_CAPABILITY',
            'priority': 'HIGH',
            'status': 'OPEN',
            'user_action': 'NONE',
            'created_at': now()
        })
        existing_req.add(rid)
        added += 1

    if not pinned_review_available:
        PENDING.write_text(json.dumps({'schema_version':1,'source':'TOOL045','receiver':'TOOL016','updated_at':now(),'records':pending_records}, ensure_ascii=False, indent=2), encoding='utf-8')
    if added:
        INBOX.write_text(json.dumps(inbox, ensure_ascii=False, indent=2), encoding='utf-8')

    receipt = {
        'schema_version': 1,
        'source': 'TOOL045',
        'receiver': 'TOOL016',
        'received': True,
        'state': ('RECEIVED_ROOT_REVIEW_PENDING' if pending_records else
                  'PINNED_ROOT_REVIEW_REUSED_SOURCE_ASSET_NOT_MOUNTED' if pinned_review_available else
                  'RECEIVED_EMPTY'),
        'received_at': now(),
        'handoff_state_seen': handoff.get('state'),
        'record_count': len(records),
        'deduplicated_record_count': len(unique),
        'pending_root_review_count': len(pending_records),
        'eligible_for_tool044_count': len(eligible),
        'tool044_handoff_count_this_run': added,
        'pinned_source_occurrence_count': pinned_manifest.get('occurrence_count') if pinned_review_available else None,
        'pinned_source_root_candidate_count': pinned_manifest.get('root_candidate_count') if pinned_review_available else None,
        'reviewed_global_root_family_count': root_review.get('duplicate_review', {}).get('global_root_families') if pinned_review_available else None,
        'verified_missing_capability_count': root_review.get('missing_capability_review', {}).get('verified_missing_capabilities') if pinned_review_available else None,
        'source_asset_sha256': pinned_manifest.get('asset_zip_sha256') if pinned_review_available else None,
        'truth_contract': 'TOOL044_ONLY_AFTER_VERIFIED_ROOT_AND_VERIFIED_MISSING_CAPABILITY'
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False))

if __name__ == '__main__':
    main()
