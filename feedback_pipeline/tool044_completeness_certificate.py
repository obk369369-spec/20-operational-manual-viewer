from __future__ import annotations
import json
from tool044_requirement_interlock import HERE,stage_token
from tool044_requirement_ledger import current_ledger

def run():
    ledger=current_ledger(HERE)
    prior=('T0_GOVERNANCE','T1_CROSS_CHAT','T2_COMPONENT_INTEGRITY','T3_LARGE_WAREHOUSE','T4_PARALLEL_FACTORY','T5_AUTO_DEPLOY','T6_OBSERVER','T7_FINAL_RECONCILIATION')
    tokens={s:stage_token(ledger,s,HERE)['token'] for s in prior}
    matched=sum(1 for r in ledger['requirements'] if r.get('status')=='PASS')
    certificate_allowed=all(x=='PASS' for x in tokens.values()) and matched==ledger['current_requirement_total']-1
    return {'status':'TOOL044_COMPLETENESS_CERTIFICATE' if certificate_allowed else 'COMPLETE_FORBIDDEN',
            'current_requirement_total':ledger['current_requirement_total'],
            'matched_before_certificate':matched,'unmatched_before_certificate':ledger['current_requirement_total']-matched,
            'stage_tokens':tokens,'time_dependent_exception':{'24H_ACTIVE_PROVING':'RUNNING'},
            'historical_chat_extraction':'SEPARATE_FUTURE_SCOPE'}
if __name__=='__main__':
    r=run();out=HERE/'evidence'/'tool044_completeness_certificate_20260909.json';out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False));raise SystemExit(0 if r['status']=='TOOL044_COMPLETENESS_CERTIFICATE' else 1)
