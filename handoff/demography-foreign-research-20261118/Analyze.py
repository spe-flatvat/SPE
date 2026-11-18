#!/usr/bin/env python3
"""Read-only TX analysis. Standard library; no standard inputs/code overwritten.
python3 Analyze.py --model ../f-tx01-tx03-20261118/SPE_F_TX_Model_DRAFT_20261118.py --inputs ../f-tx01-tx03-20261118/SPE_F_TX_Inputs_DRAFT_20261118.json --outdir replay
"""
import argparse,copy,csv,hashlib,importlib.util,json,math
from pathlib import Path
MODEL_SHA='c6dee8d7059f7b95726b9b35b105a936025baf7b02a9e50607d5d2cc48155a28'
INPUT_SHA='d35501a0ac9beba3bf40e941fe691d31078371a1ce4964f390403d66e86b8aa5'
BASE=Path(__file__).resolve().parent
METRICS=['population_persons','births_persons','deaths_persons','labor_force_population_proxy','foreign_stock_conditional_persons','foreign_stock_population_ratio','foreign_gdp_contribution_ratio','common_migration_net_flow','policy_migration_accepted_net_flow','total_migration_net_flow','real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','household_disposable_nominal_trn','household_consumption_real_proxy_trn','I_policy_real_trn','capital_total_real_trn','supply_binding','unmet_demand_real','price_pressure_proxy','medical_insurer_vat','medical_extra_premium','medical_public_topup','medical_internal','medical_unallocated']
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,rows):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows({k:(format(v,'.10g') if isinstance(v,float) else v) for k,v in r.items()} for r in rows)
def run(model,inputs,out):
 assert digest(model)==MODEL_SHA and digest(inputs)==INPUT_SHA,'Fixed source byte mismatch'
 sp=importlib.util.spec_from_file_location('tx_fixed',model);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 c=json.loads(Path(inputs).read_text()); allrows=[];paths={};metadata={}
 stats=list(csv.DictReader((BASE/'Official_Statistics.csv').open()))
 def stat(measure,year,scope=None):return float(next(r['value'] for r in stats if r['measure']==measure and r['year']==str(year) and (scope is None or r['scope']==scope)))
 latest=stat('foreign_resident_stock',2026);start=stat('foreign_resident_stock',2025);recent=sum(stat('foreign_net_migration',y) for y in [2023,2024,2025])/3;last=stat('foreign_net_migration',2025)
 def calc(name,stock,flow,slack,policy,cap=True,mode='UNALLOCATED_COMPAT',flowstart=2030,retention=1.,participation=.8):
  cc=copy.deepcopy(c);cc['common_model']['slack']=slack;cc['common_model']['foreign_labor_participation']=participation
  spec=dict(id=name,profile='TEXT_ASSUMPTIONS',policy=policy,supply_cap=cap,medical_mode=mode,migration_override=dict(foreign_initial_stock=stock,common_annual_net_flow=flow,flow_start=flowstart,foreign_stock_net_retention=retention,enforcement_mode='NONE_REFERENCE'))
  rs=m.run_path(cc,spec);paths[name]=rs;metadata[name]=dict(initial_stock=stock,common_flow=flow,slack=slack,policy=policy,cap=int(cap),medical_mode=mode,flow_start=flowstart,retention=retention,participation=participation)
  for r in rs:
   allrows.append(dict(case=name,year=r['year'],**metadata[name],**{k:r[k] for k in METRICS}))
  for a,b in zip(rs,rs[1:]):assert math.isclose(b['foreign_stock_conditional_persons'],a['foreign_stock_conditional_persons']*retention+b['total_migration_net_flow'],abs_tol=1e-6)
  return rs
 #72 matched paths:3 stocks x4 flows x3 slack x2 policy. Keep timing2030 unchanged.
 for sn,stock in [('LEGACY',2000000),('END25',start),('JUN26',latest)]:
  for fn,flow in [('AVG23_25',recent),('LAST25',last),('LEGACY357',357000),('NET400',400000)]:
   for slack in [.02,.05,.10]:
    for pol in ['SQ','F']:calc(f'{sn}_{fn}_S{int(slack*100):02}_{pol}',stock,flow,slack,pol)
 #Explicit common400k from2027, not model's2030 start; no automatic acceptance controller.
 for stockname,stock in [('LEGACY',2000000),('END25',start)]:
  for pol in ['SQ','F']:calc(f'ANNUAL400_2027_{stockname}_{pol}',stock,400000,.02,pol,flowstart=2027)
 #Diagnostic retention/participation paired references: do not assert these are estimated.
 for tag,ret,part in [('RET98',.98,.8),('LAB60',1.,.6),('LAB70',1.,.7)]:
  for pol in ['SQ','F']:calc(f'{tag}_{pol}',start,last,.02,pol,retention=ret,participation=part)
 #DM04 supply masking check, three financer cases x3slacks +uncapped; baseline grid provides UNALLOCATED andSQ.
 for mode in ['PREMIUM','PUBLIC','INTERNAL']:
  for slack in [.02,.05,.10]:calc(f'MED_{mode}_S{int(slack*100):02}',start,last,slack,'F',mode=mode)
  calc(f'MED_{mode}_UNCAPPED',start,last,.02,'F',cap=False,mode=mode)
 for pol in ['SQ','F']:calc(f'UNCAPPED_{pol}',start,last,.02,pol,cap=False)
 #Light regression against existing published selected rows, no full legacy recomputation.
 old=list(csv.DictReader(Path(inputs).with_name('SPE_F_TX_Annual_Comparison_DRAFT_20261118.csv').open())) if Path(inputs).with_name('SPE_F_TX_Annual_Comparison_DRAFT_20261118.csv').exists() else []
 regression=0
 for pol in ['SQ','F']:
  for r in paths[f'LEGACY_LEGACY357_S02_{pol}']:
   ref=next((x for x in old if x['case']==f'TEXT_ASSUMPTIONS_{pol}_CAP' and int(x['year'])==r['year']),None)
   if ref:
    for k in ['real_gdp_trn','nominal_gdp_trn','population_persons','foreign_stock_conditional_persons']:
     assert math.isclose(r[k],float(ref[k]),abs_tol=1e-8,rel_tol=5e-10),(pol,r['year'],k,r[k],ref[k]);regression+=1
 #Thresholds: both inclusive reaching and strict exceeding;2026 means already at initial boundary, earlier year not known.
 summaries=[]
 for name,rs in paths.items():
  end=rs[-1];s=dict(case=name,**metadata[name])
  for label,key,t in [('pop3','foreign_stock_population_ratio',.03),('pop5','foreign_stock_population_ratio',.05),('gdp5_reference','foreign_gdp_contribution_ratio',.05)]:
   for op in ['reach','exceed']:s[label+'_'+op]=next((r['year'] for r in rs if r[key]>=t if op=='reach'),None) if op=='reach' else next((r['year'] for r in rs if r[key]>t),None)
  for k in METRICS:s['end2055_'+k]=end[k]
  s['binding_years']=sum(r['supply_binding'] for r in rs);s['max_unmet_demand']=max(r['unmet_demand_real'] for r in rs)
  summaries.append(s)
 #Closed stock ledger:400k annual STOCK increase2027 onward;population denominator uses same model natural change.
 #Separate from engine;no GDP response is calculated for this ledger.
 ledger=[]
 for stockname,stock in [('LEGACY',2000000),('END25',start),('JUN26',latest)]:
  rs=paths['ANNUAL400_2027_END25_SQ']
  for r in rs:
   S=stock+400000*(r['year']-2026)
   ledger.append(dict(case='STOCK400_'+stockname,year=r['year'],foreign_stock=S,population_denominator=r['population_persons'],population_ratio=S/r['population_persons'],definition='ANALYSIS_ONLY_FIXED_STOCK_INCREMENT;NO_GDP_EFFECT_ESTIMATE'))
 out.mkdir(parents=True,exist_ok=True);dump(out/'Sensitivity_Annual.csv',allrows);dump(out/'Sensitivity_Summary.csv',summaries);dump(out/'Stock400_Ledger.csv',ledger)
 assert digest(model)==MODEL_SHA and digest(inputs)==INPUT_SHA
 checks=dict(paths=len(paths),annual_rows=len(allrows),stock_ledger_rows=len(ledger),regression_cells=regression,model_hash_unchanged=True,input_hash_unchanged=True,flow_average=recent,stock2025=start,stock2026=latest)
 print(json.dumps(checks,ensure_ascii=False));return checks
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--inputs',required=True);p.add_argument('--outdir',required=True);a=p.parse_args();run(a.model,a.inputs,Path(a.outdir))
