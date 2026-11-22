#!/usr/bin/env python3
"""Comparisons and explicit policy mapping from executed paths, no fabricated data."""
import argparse,csv,json,hashlib,platform,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
MODES=['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']
def read(p):return list(csv.DictReader(p.open()))
def num(r,k):
 try:return float(r[k]) if r.get(k) not in ['',None] else None
 except (ValueError,TypeError):return None
def dump(p,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def run(out):
 cfg=json.loads((P/'Inputs.json').read_text());metrics=['real_gdp_trn','nominal_gdp_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','labor_force_population_proxy','tax_diagnostic_trn','macro_cash_DI_proxy_trn','household_cash_delta_trn','consolidated_partial_balance_proxy_trn','pension_fund_stock_trn','semi_med_fund_asset_trn','patient_payment_delta_trn','policy_household_cash_delta_trn','modeled_VAT_trn','population']
 F={r['year']:r for r in read(ROOT/'handoff/f-common-endoflife-finalization-20261121/Annual.csv') if r['case']=='LATEST_F'}
 fixed_old=read(ROOT/'handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Annual.csv');old={(r['case'],r['year']):r for r in fixed_old}
 comparison=[];legacy=[];sens=[];annual=[]
 for mode in MODES:
  d=out/'macro'/mode;rs=read(d/'Gap_Annual.csv');eng={(r['case'],r['year']):r for r in read(d/'N3_Engine_Accounts.csv')};by={(r['case'],r['year']):r for r in rs};sq={r['year']:r for r in rs if r['case']=='SQ_COMMON_ON'}
  for r in rs:
   e=eng[r['case'],r['year']];z=dict(r,mode=mode,scope='CANDIDATE_NOT_ADOPTED',**{'macro_'+k:v for k,v in e.items() if k not in ['case','year']});annual.append(z)
   c=dict(mode=mode,case=r['case'],year=r['year'],F_status='ff621006_FIXED_REFERENCE_NOT_REEXECUTED',N3_policy_status='UNADOPTED_CANDIDATE',real_gdp_minus_initial580=num(r,'real_gdp_trn')-580)
   for k in metrics:
    value=num(r,k);sv=num(sq[r['year']],k);fv=num(F[r['year']],k)
    if k=='labor_force_population_proxy':value=num(e,k);sv=num(eng['SQ_COMMON_ON',r['year']],k)
    if k=='macro_cash_DI_proxy_trn':
     value-=num(r,'household_direct_price_benefit_trn') or 0
     sv-=num(sq[r['year']],'household_direct_price_benefit_trn') or 0
    c[k]=value;c[k+'_minus_SQ']=None if value is None or sv is None else value-sv;c[k+'_minus_F_FIXED']=None if value is None or fv is None else value-fv
   comparison.append(c)
   if mode=='DOMESTIC_TRANSFER' and (r['case'],r['year']) in old:
    prev=old[r['case'],r['year']]
    for k in prev:
     a=num(prev,k);b=num(r,k)
     same=prev[k]==r.get(k) or a is not None and b is not None and abs(a-b)<=max(1e-8,abs(a)*1e-11)
     if not same:legacy.append(dict(case=r['case'],year=r['year'],column=k,old=prev[k],new=r.get(k),classification='UNEXPECTED_OLD_CASE_CHANGE'))
  for name in cfg['parity_cases']:
   for y in range(2026,2056):
    r=by[name,str(y)];base=by['PARITY_CONNECTED_CANDIDATE',str(y)]
    for k in metrics:
     a=num(r,k);b=num(base,k)
     sens.append(dict(mode=mode,case=name,year=y,metric=k,value=a,delta_vs_connected_candidate=None if a is None or b is None else a-b,method='PAIRED_REEXECUTION_NOT_ADDITIVE_ATTRIBUTION'))
 dump(out/'SQ_F_N3_Comparison.csv',comparison);dump(out/'Key_Years.csv',[r for r in comparison if int(r['year']) in [2026,2035,2045,2055]])
 dump(out/'Sensitivity.csv',sens);dump(out/'Old79_Changed_Cells.csv',legacy or [dict(status='NO_OLD79_CHANGE',changed_cells=0)])
 # Fully joined macro diagnostics permit an independent annual identity check.
 for mode in MODES:dump(out/('Annual_'+mode+'.csv'),[r for r in annual if r['mode']==mode])
 policy=[
 ('4A VAT','existing statutory path + price/quantity replacement','VAT rates and household C','EXISTING_CONNECTED','2035 income KPI candidate now connected; threshold unspecified'),
 ('4A income30 finance20','survey weighted synthetic bases','HH cash -> smoothed C -> GDP/income/tax','EXTENDED_LAGGED_BASE_CANDIDATE','lag actual wage adjusts policy base; survey allocation not actual nationwide microdata'),
 ('4A corporate20/16 AND60/20','firm cells eligibility preserved','tax saving -> dividend/I -> K -> next capacity','EXISTING_CARRY_PLUS_NEW_FIRM_STOCK_AND_LAGGED_PROFIT_BASE','profit/revenue denominator alternatives retained; no coefficient targeting'),
 ('4A estate/gift40','reported taxpaying bases only','wealth burden -> candidate MPC -> C','EXISTING_PARTIAL_CONNECTED','full deduction abolition and overlap unestimated'),
 ('4A invoice simplification','existing cost interface','transaction cost','STRUCTURE_ONLY','hours/compliance baseline absent; no fabricated saving'),
 ('4B pension75','protected cohorts + contribution diversion + reserve','fund -> payout -> HH C; four source candidates','EXTENDED_LAGGED_WAGE_CONTRIBUTION_BASE','four ownership modes unadopted; no second premium charge'),
 ('4B medical50/cap','amount and rate interpolation candidates','patient/public/insurer -> HH C/VA/labor','EXISTING_CONNECTED','patient cap down/up interpretation alternatives retained'),
 ('4B common palliative','unchanged fixed common module','clinical resource and cash -> macro','EXISTING_CONNECTED','autonomy and beneficiary protection preserved'),
 ('4B semi medical','claim/premium reclassification + optional reserve','fund stock -> matching payer accounts','EXISTING_PARTIAL_CONNECTED','no assumed efficiency or nonexistent public saving'),
 ('4B EITC/relief/in-kind','income<=5m threshold; relief candidate','HH expense substitution + government/insurer','EXTENDED_INCOME_BASE_AND_EXTERNAL_GINI_TRIGGER','EITC baseline null; increment/duration candidate only'),
 ('4B co-op 10-15 blocks','existing 12-block candidate interface','institutional partition','STRUCTURE_ONLY','regional claims and cost input unavailable'),
 ('4C employment anchor','regularization/additional jobs separate','payroll -> HH/expense; additional effective labor','EXISTING_CONNECTED_PLUS_LABOR_SENSITIVITY','regularization never additional jobs'),
 ('4C foreign5% N4 regional','wagebill/VA cap candidates and retention','additional service VA once; population/labor bridge','EXISTING_PARTIAL_CONNECTED','ratio definition and medical/housing/social/family cost OPEN; no second wage/GDP'),
 ('4D smart shrink','density productivity cost ranking','investment priority interface','STRUCTURE_ONLY','no national investment envelope/return assumption'),
 ('6/7 income KPI','lagged real cash income per capita 2034/2033','2035 evaluation -> sticky VAT freeze','NEW_CONNECTED_CANDIDATE','old GDP signal case retained; no future observation'),
 ('7 Gini KPI','lagged external observation','candidate relief increment in 2035','NEW_CONDITIONAL_EXECUTION','national Gini remains null; no inferred distribution metric'),
 ('7 insurance KPI','explicit candidate return floor','underperformance -> competition signal','STRUCTURE_ONLY_SIGNAL_EXECUTED','no invented competition productivity gain'),
 ('9 simulation conditions','common initial/risk baseline unchanged','shared annual risk/labor engine','REUSED_NOT_POLICY_MECHANISM','no SQ growth diagnosis or common engine redesign')]
 dump(out/'Policy_Implementation_Map.csv',[dict(policy=a,existing=b,connection=c,status=d,boundary=e) for a,b,c,d,e in policy])
 (out/'Execution_Metadata.json').write_text(json.dumps(dict(status='EXECUTED_ANNUAL_CANDIDATES',cases_per_mode=14+len(cfg['cases']),modes=MODES,annual_rows=len(annual),years=[2026,2055],legacy79_changed_cells=len(legacy),python=platform.python_version(),source_fixed_commit='3c77eafc2073fdaba4c129164817d2f57c9421b9',input_engine_commit='92b72ed0a4ea743aca477d7f6d0006e733c9969c',F_fixed_commit='ff6210061615105de9a0d64767c256796be80ed2',F_reexecuted=False,independent_verification=False),indent=2)+'\n')
 print('RESULTS',len(annual),'old79 changes',len(legacy))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--outdir',type=Path,required=True);run(p.parse_args().outdir)
