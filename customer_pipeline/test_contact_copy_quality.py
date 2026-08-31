"""Changed-scope historical replay + negative gates. Does not send messages."""
import json
import subprocess
import sys
from pathlib import Path
from tool7_contact_judgment import prepare_contact_copy, validate_contact_copy

HERE = Path(__file__).parent
data = json.loads((HERE / 'contact_copy_actual_cases.json').read_text(encoding='utf-8'))
base = dict(current_employment_verified=True, company_direction_verified=True, phone_allowed=True)
results = []
for case in data['cases']:
    out = prepare_contact_copy(base, case['context'])
    assert out['status'] == 'DRAFT_VALIDATED', (case['id'], out)
    assert out['turns'][-1] == case['expected_question']
    assert out['recommendation_allowed'] is False
    assert out['next_action'] == 'WAIT_FOR_CUSTOMER_REPLY'
    cli=json.loads(subprocess.check_output([sys.executable,str(HERE/'tool7_contact_judgment.py'),'--copy-stdin'],input=json.dumps({'customer':base,'context':case['context']}).encode()))
    assert cli==out
    if case['context'].get('landline_unavailable'):
        assert out['phone_message'] == '' and out['channel'] == 'EMAIL'
    # Both native adapters must consume the same actual evidence with identical copy.
    if len(sys.argv) > 1:
        js = "const m=require(process.argv[1]);const p=JSON.parse(process.argv[2]);console.log(JSON.stringify(m.prepareContactCopy({current_affiliation_verified:true,contact_history_verified:true},p)))"
        raw = subprocess.check_output(['node', '-e', js, str(Path(sys.argv[1]).resolve()), json.dumps(case['context'])])
        target = json.loads(raw)
        assert target['turns'] == out['turns'] and target['status'] == out['status']
        jscli=json.loads(subprocess.check_output(['node',str(Path(sys.argv[1]).resolve())],input=json.dumps({'state':{'current_affiliation_verified':True,'contact_history_verified':True},'context':case['context']}).encode()))
        assert jscli==target
    results.append({'id':case['id'], 'input_evidence':case['source_ref'], 'output':out})

ctx=data['cases'][0]['context']
assert prepare_contact_copy(base,{**ctx,'evidence_verified':False})['status']=='HOLD'
assert prepare_contact_copy(base,{**ctx,'source_ref':''})['status']=='HOLD'
assert prepare_contact_copy({**base,'explicit_stop_or_rejection':True},ctx)['status']=='FAIL'
for text in ['정기적으로 보내드리겠습니다.','휴대전화 번호를 알려주세요.','현재 관심 분야에 맞춥니다.','연구하고 계시더라고요.','소자공정·고신뢰성·실증 기반구축 자료입니다.','무엇인가요? 언제인가요?']:
    assert validate_contact_copy({'turns':[text],'history_kind':'one_way'}), text
assert validate_contact_copy({'turns':['문의하신 자료입니다.'],'history_kind':'one_way'})
for code,expected in [('STOP','DO_NOT_CONTACT'),('OTHER','WAIT_FOR_CUSTOMER_SCOPE'),('LATER','WAIT_FOR_REQUESTED_FOLLOWUP'),('SCOPE','WAIT_FOR_SCOPE_CONFIRMATION')]:
    out=prepare_contact_copy(base,ctx,{'code':code,'source_ref':'negative-test-reply','verified':True,'plain_scope':'수술로봇'})
    assert out['next_action']==expected and not out['recommendation_allowed']
assert prepare_contact_copy(base,ctx,{'code':'SCOPE','plain_scope':'unknown'})['status']=='HOLD'
confirmed=prepare_contact_copy(base,ctx,{'code':'CONFIRMED','plain_scope':'수술로봇','source_ref':'test-confirmed','verified':True})
assert confirmed['recommendation_allowed'] is True
assert confirmed['send_allowed'] is False
invalid=prepare_contact_copy(base,ctx,{'code':'CONFIRMED','plain_scope':'고신뢰성','source_ref':'test-confirmed','verified':True})
assert invalid['status']=='HOLD' and invalid['recommendation_allowed'] is False and invalid['email_body']==''
summary={'historical_cases':3,'native_adapter_parity':len(sys.argv)>1,'actual_cli_runs':6 if len(sys.argv)>1 else 3,'negative_gates':'PASS','results':results}
if '--save' in sys.argv:
    (HERE/'contact_copy_validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True))
