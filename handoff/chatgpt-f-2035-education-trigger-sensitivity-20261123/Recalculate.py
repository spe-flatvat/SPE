"""Limited non-adopted F trigger sensitivity. Stdlib; pinned sources only."""
import csv,hashlib,json,math,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
CASE='ANNUAL_FINE_WEEK_HOURS'
def js(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def main(root,out):
 out.mkdir(parents=True,exist_ok=True);checks=[]
 def ck(n,a,b,tol=1e-7):
  error=abs(a-b);ok=math.isfinite(error) and error<=tol+abs(b)*1e-10
  checks.append(dict(check=n,error=error,tolerance=tol,passed=ok));assert ok,(n,a,b)
 receipts=[]
 for e in js(HERE/'Source_Manifest.json'):
  b=(root/e['path']).read_bytes();h=hashlib.sha256(b).hexdigest()
  ck('source_size:'+e['path'],len(b),e['size'],0);ck('source_hash:'+e['path'],int(h!=e['sha256']),0,0)
  receipts.append(dict(**e,own_byte_verification='MATCH',reuse='Prior fixed-commit custody PASS reused; bytes checked on this execution'))
 save(out/'Source_Receipts.json',receipts)
 old={int(r['year']):r for r in csv.DictReader((root/'Prior_Annual.csv').open()) if r['labor_case']==CASE and r['mask']=='7'}
 prior_trace=js(root/'handoff/chatgpt-f-policy-cohort-fte-20261123'/CASE/'F_Runtime_Trace.json')['years']
 ref={int(r['year']):r for r in csv.DictReader((root/'handoff/chatgpt-n3-aligned-labor-baseline-20261123/SQ_F_N3_Aligned_Labor_Annual_2026_2055.csv').open()) if r['labor_case']==CASE}
 ci=js(root/'handoff/chatgpt-f-policy-cohort-fte-20261123'/CASE/'Connection_Inputs.json')
 params=js(root/'handoff/f-education-20261121/Inputs.json')['defaults']
 metrics=['real_gdp_trn','nominal_gdp_trn','core_real_gdp_trn','labor_force_population_proxy','population','productivity_gain','skill_stock_worker_equivalents','education_effective_labor_added','training_hours','training_time_worker_equivalent','study_time_worker_equivalent','nominal_wage_proxy_man','real_wage_proxy_man','household_disposable_nominal_trn','tax_diagnostic_trn','government_partial_balance_proxy_trn','consolidated_partial_balance_proxy_trn','education_facility_trn','education_service_trn','scholarship_grant_trn','net_additional_education_spend_trn','additional_training_trn','training_credit_trn','credit_on_existing_trn','credit_on_added_trn','bond_issue_trn','bond_redemption_trn','bond_interest_trn','bond_end_trn','education_total_cost_trn','education_unassigned_cash_finance_trn','firm_training_cash_delta_trn','facility_stock_real_proxy_trn','real_growth_pct']
 allrows=[];comparison=[];trace_rows=[];paths={};traces={};scenarios=[]
 with tempfile.TemporaryDirectory() as td:
  def run(s):
   folder=Path(td)/s['id'];cfg=Path(td)/(s['id']+'.json');save(cfg,s)
   subprocess.run([sys.executable,str(HERE/'Worker.py'),str(root),str(folder),str(cfg)],check=True,stdout=subprocess.DEVNULL)
   return js(folder/'F_Actual_Annual.json'),js(folder/'F_Runtime_Trace.json'),js(folder/'Policy_Base_Ledgers.json')
  base_s=dict(id='BASE_OFF',multiplier=1.,threshold=.012,baseline_growth=None,fired=False,evaluation_year=2035,effective_year=2036)
  base,bt,ledger=run(base_s);paths['BASE_OFF']=base;traces['BASE_OFF']=bt;scenarios.append(base_s)
  for r in base:
   for k in metrics:
    if k not in old[r['year']]:continue
    ck('fixed_F:'+str(r['year'])+':'+k,r[k],float(old[r['year']][k]),1e-6)
  g=base[9]['real_gdp_trn']/base[8]['real_gdp_trn']-1
  decision=dict(reference='intervention-free BASE_OFF',evaluation_year=2035,comparison_year=2034,formula='real_GDP_2035 / real_GDP_2034 - 1',baseline_growth=g,threshold=.012,strict_less_than=True,fired=g<.012,effective_year=2036,continuation='EVERY_YEAR_2036_2055',scholarship='UNCHANGED',policy_adopted=False)
  save(out/'Trigger_Decision.json',decision)
  ck('decision:observed_2035_growth',g,base[9]['real_growth_pct']/100)
  ck('decision:strict_threshold_equality',int(g<g),0,0)
  ck('decision:strict_threshold_below',int((.012-1e-12)<.012),1,0)
  ck('decision:strict_threshold_at',int(.012<.012),0,0)
  ck('decision:strict_threshold_above',int((.012+1e-12)<.012),0,0)
  # Main requested branch first; two nearby scales and an actual non-fire run.
  for name,mult,threshold in [('EXPAND_1P2',1.2,.012),('EXPAND_1P1',1.1,.012),('EXPAND_1P3',1.3,.012),('NO_FIRE_EQUAL_THRESHOLD',1.2,g)]:
   s=dict(id=name,multiplier=mult,threshold=threshold,baseline_growth=g,fired=g<threshold,evaluation_year=2035,effective_year=2036)
   rows,tr,unused=run(s);paths[name]=rows;traces[name]=tr;scenarios.append(s)
  for s in scenarios:
   name=s['id'];rows=paths[name];tr=traces[name];ck(name+':30_years',len(rows),30,0)
   stocks={k:0. for k in 'EST'};due={k:{} for k in 'EST'}
   for i,(r,t,b) in enumerate(zip(rows,tr['years'],base)):
    y=2026+i;tag=name+':'+str(y)+':';factor=s['multiplier'] if s['fired'] and y>=2036 else 1.
    ck(tag+'year',r['year'],y,0)
    ck(tag+'E_parameter',r['applied_E_multiplier'],factor)
    ck(tag+'T_parameter',r['training_credit_parameter'],params['credit_rate']*factor)
    ck(tag+'scholarship_parameter',r['applied_S_multiplier'],1.)
    ck(tag+'E_facility_scale',r['education_facility_trn'],b['education_facility_trn']*factor)
    ck(tag+'E_service_scale',r['education_service_trn'],b['education_service_trn']*factor)
    ck(tag+'S_grants_unchanged',r['scholarship_grant_trn'],b['scholarship_grant_trn'])
    ck(tag+'S_study_unchanged',r['study_time_worker_equivalent'],b['study_time_worker_equivalent'])
    ck(tag+'T_effective_rate',r['effective_training_credit_rate'],b['effective_training_credit_rate']*factor)
    for k,field,lag in [('E','school_skill_units_scheduled',8),('S','scholarship_skill_units_scheduled',4),('T','training_skill_units_scheduled',1)]:
     stocks[k]=stocks[k]*(1-params['skill_decay'])+due[k].get(y,0.)
     due[k][y+lag]=due[k].get(y+lag,0.)+r[field]
     ck(tag+k+'_lag',r[{'E':'school_lag','S':'scholarship_lag','T':'training_lag'}[k]],lag,0)
    denominator=t['trajectory_effective_L']+ledger['elder'][i]['effective_extra']
    ck(tag+'skill_recurrence',r['skill_stock_worker_equivalents'],sum(stocks.values()))
    ck(tag+'training_time',r['training_time_worker_equivalent'],r['training_hours']/params['annual_work_hours'])
    ck(tag+'productivity',r['productivity_gain'],min(params['productivity_cap'],sum(stocks.values())/denominator))
    ck(tag+'education_labor',r['education_effective_labor_added'],denominator*r['productivity_gain']-r['training_time_worker_equivalent']-r['study_time_worker_equivalent'])
    if i:ck(tag+'labor_once',t['labor'],t['trajectory_effective_L']+t['education_effective_added']+t['health_effective_added']+t['elder_effective_added']+ci['common_offset'][i]+ci['elder_delta'][i],1e-5)
    ck(tag+'GDP_identity',r['real_gdp_trn'],t['desired']-t['unmet'])
    ck(tag+'legacy_education_removed',abs(t['education_nom'])+abs(t['education_level'])+abs(t['finite']),0.)
    ck(tag+'training_credit_split',r['training_credit_trn'],r['credit_on_existing_trn']+r['credit_on_added_trn'])
    ck(tag+'firm_cash',r['firm_training_cash_delta_trn'],r['training_credit_trn']-r['additional_training_trn'])
    ck(tag+'grant_uses',r['scholarship_grant_trn'],r['scholarship_HH_consumption_trn']+r['scholarship_saving_trn']+r['scholarship_loan_displacement_trn'])
    ck(tag+'education_gross',r['gross_education_spend_trn'],r['education_facility_trn']+r['education_service_trn']+r['scholarship_grant_trn'])
    ck(tag+'education_net',r['net_additional_education_spend_trn'],r['gross_education_spend_trn']-r['reallocated_education_budget_trn'])
    ck(tag+'bond_stock',r['bond_end_trn'],r['bond_begin_trn']+r['bond_issue_trn']-r['bond_redemption_trn'])
    ck(tag+'education_cost',r['education_total_cost_trn'],r['net_additional_education_spend_trn']+r['training_credit_trn']+r['bond_interest_trn'])
    ck(tag+'financing',r['education_unassigned_cash_finance_trn'],r['education_total_cost_trn']+r['bond_redemption_trn']-r['bond_issue_trn'])
    ck(tag+'fixed_population',r['population'],b['population'])
    for k in ['risk','inflation','trajectory_effective_L','health_effective_added','elder_effective_added']:
     ck(tag+'fixed_'+k,t[k],bt['years'][i][k])
    if y<=2035 or not s['fired']:
     for k,v in r.items():
      if isinstance(v,(int,float)) and not isinstance(v,bool) and k in b and not k.startswith(('diagnostic_','baseline_trigger_')):
       ck(tag+'pre_intervention_or_no_fire:'+k,v,b[k])
    if y==2026:
     ck(tag+'real_anchor',r['real_gdp_trn'],580.);ck(tag+'nominal_anchor',r['nominal_gdp_trn'],600.)
    # The fixed queue ensures no added skill from E until 2044, T until 2037.
    if y<2037:ck(tag+'no_early_T_or_E_stock',r['skill_stock_worker_equivalents'],b['skill_stock_worker_equivalents'])
    data=dict(scenario=name,year=y,**{k:r[k] for k in metrics},E_multiplier=factor,training_credit_parameter=r['training_credit_parameter'],S_multiplier=1.,trigger_active=bool(s['fired'] and y>=2036),SQ_real_GDP_trn=float(ref[y]['SQ_real_GDP_trn']),N3_real_GDP_trn=float(ref[y]['N3_real_GDP_trn']),actual_FTE=None,actual_national_PB_trn=None,total_national_bond_issue_trn=None,policy_adopted=False)
    allrows.append(data)
    comparison.append(dict(scenario=name,year=y,**{key:val for k in metrics for key,val in [('baseline_'+k,b[k]),('sensitivity_'+k,r[k]),('delta_'+k,r[k]-b[k])]}))
    trace_rows.append(dict(scenario=name,year=y,school_skill_stock=stocks['E'],scholarship_skill_stock=stocks['S'],training_skill_stock=stocks['T'],denominator=denominator,education_labor=r['education_effective_labor_added'],labor=t['labor'],coreY=t['coreY'],coreD=t['coreD'],desired=t['desired'],capacity=t['capacity'],unmet=t['unmet'],risk=t['risk'],inflation=t['inflation'],education_service_direct_real_trn=r['education_service_domestic_nominal_trn']/t['coreD'],education_facility_domestic_nominal_trn=r['education_facility_domestic_nominal_trn'],legacy_education_nom=t['education_nom']))
   print(json.dumps(dict(scenario=name,real2055=rows[-1]['real_gdp_trn'],delta2055=rows[-1]['real_gdp_trn']-base[-1]['real_gdp_trn'])),flush=True)
 # Additional queue boundary checks use the independently rebuilt stocks.
 for name in paths:
  series={int(r['year']):r for r in trace_rows if r['scenario']==name};bs={int(r['year']):r for r in trace_rows if r['scenario']=='BASE_OFF'}
  for y in range(2026,2056):
   for k,last in [('school_skill_stock',2043),('training_skill_stock',2036),('scholarship_skill_stock',2055)]:
    if y<=last:ck(name+':queue_boundary:'+str(y)+':'+k,series[y][k],bs[y][k])
 dump(out/'Annual_2026_2055.csv',allrows);dump(out/'Annual_Difference_vs_Base.csv',comparison);dump(out/'Education_Runtime_Bridge.csv',trace_rows)
 dump(out/'Key_Years.csv',[r for r in comparison if r['year'] in [2026,2035,2036,2040,2045,2050,2055]])
 save(out/'Scenario_Inputs.json',scenarios);dump(out/'Validation_Checks.csv',checks)
 save(out/'Validation.json',dict(new_checks=len(checks),failed=sum(not r['passed'] for r in checks),executed_paths=len(paths),executed_year_rows=30*len(paths),source_files=len(receipts),SQ_N3='fixed references reused; not recalculated',policy_adopted=False,RP023_M1925='HOLD',RP024='PENDING'))
if __name__=='__main__':main(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE/'sources',Path(sys.argv[2]).resolve() if len(sys.argv)>2 else HERE)
