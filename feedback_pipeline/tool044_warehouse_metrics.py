"""Measure warehouse coverage, reuse, and validated parallel throughput."""
import json, sys, time
from pathlib import Path

from tool044_composition import lookup_verified_composition, test_provenance_html_toc_growth

HERE=Path(__file__).resolve().parent
registry=json.loads((HERE/'VERIFIED_COMPONENT_REGISTRY.json').read_text(encoding='utf-8'))
pool=json.loads((HERE/'evidence/tool044_verified_composition_pool.json').read_text(encoding='utf-8'))
demands=[
 {'demand_id':'URL-PROVENANCE','atomic_capabilities':['URL_VALIDATION','PROVENANCE_VALIDATION']},
 {'demand_id':'HTML-TOC','atomic_capabilities':['WEBPAGE_TEXT_EXTRACTION','TOC_STRUCTURE_EXTRACTION']},
 {'demand_id':'VERIFIED-HTML-TOC','atomic_capabilities':['PROVENANCE_VALIDATION','WEBPAGE_TEXT_EXTRACTION','TOC_STRUCTURE_EXTRACTION']},
 {'demand_id':'NO-READY','atomic_capabilities':['LOCAL_TITLE_TRANSLATION']},
]
lookups=[];start=time.perf_counter()
for d in demands: lookups.append(lookup_verified_composition(HERE/'evidence/tool044_verified_composition_pool.json',d))
lookup_elapsed=time.perf_counter()-start
start=time.perf_counter();test_provenance_html_toc_growth(HERE/'external_candidate_pool/html2text-2025.4.15-py3-none-any.whl',HERE/'external_candidate_pool/mistune-3.3.4-py3-none-any.whl',HERE/'fixtures/tool042_html_toc_normal.json',HERE/'fixtures/tool042_html_toc_failure.json');baseline=time.perf_counter()-start
pv=json.loads((HERE/'evidence/tool044_parallel_verify_deployed_20260909.json').read_text(encoding='utf-8'))
rows=pv['workers'];parallel_wall=(max(r['end_ns'] for r in rows)-min(r['start_ns'] for r in rows))/1e9;serial_sum=sum((r['end_ns']-r['start_ns'])/1e9 for r in rows)
unique={x['component_id']:x for x in registry.get('components',[])+registry.get('verified_atomic_component_pool',[]) if x.get('status')=='VERIFIED_REUSABLE'}
caps=set()
for x in unique.values(): caps.update(x.get('atomic_capabilities') or x.get('capabilities') or [])
hits=sum(x['warehouse_hits'] for x in lookups);total=len(lookups)
out={'warehouse':{'verified_atomic_unique':len(unique),'verified_compositions':len(pool['compositions']),'unique_capabilities':len(caps),'newly_registered_compositions_this_run':2},'reuse':{'total_demands':total,'warehouse_hits':hits,'composition_hits':hits,'external_search_required':total-hits,'reuse_hit_rate':hits/total,'external_search_skipped':hits,'external_search_skip_rate':hits/total,'lookups':lookups},'speed':{'composition_rebuild_seconds':baseline,'warehouse_lookup_seconds':lookup_elapsed,'composition_speed_improvement_percent':(1-lookup_elapsed/baseline)*100 if baseline else 0,'parallel_verify_wall_seconds':parallel_wall,'serial_verify_sum_seconds':serial_sum,'parallel_throughput_jobs_per_second':len(rows)/parallel_wall,'serial_equivalent_jobs_per_second':len(rows)/serial_sum,'throughput_improvement_percent':(serial_sum/parallel_wall-1)*100},'validation_quality_preserved':all(x['result']=='PASS' for x in rows),'result':'PASS'}
print(json.dumps(out,ensure_ascii=False,indent=2))
if len(pool['compositions'])<3 or hits!=3 or lookup_elapsed>=baseline or not out['validation_quality_preserved']: raise SystemExit(2)
