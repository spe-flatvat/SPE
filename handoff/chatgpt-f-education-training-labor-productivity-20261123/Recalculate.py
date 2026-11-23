"""Pinned full-engine education factorial experiment. Python standard library only.
All outputs are conditional model diagnostics, DRAFT / NON-CANONICAL.
"""
import csv, hashlib, itertools, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
CASES=['BASE_SQ_UNCHANGED','PREVIOUS_FINE_AGE_HOURS','ANNUAL_ALIGNED_FULL_RATES','OCTOBER_NEAR_FULL_RATES','ANNUAL_FINE_WEEK_HOURS','ANNUAL_MONTH_HOURS_PROFILE']
def js(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def main(root,out):
 out.mkdir(parents=True,exist_ok=True);checks=[];annual=[];bridge=[];decomp=[];warnings=[]
 def ck(name,a,b,tol=1e-7):
  err=abs(a-b);ok=math.isfinite(err) and err<=tol+abs(b)*1e-10
  checks.append(dict(check=name,error=err,tolerance=tol,passed=ok));assert ok,(name,a,b)
 receipts=[]
 for e in js(HERE/'Source_Manifest.json'):
  b=(root/e['path']).read_bytes();sha=hashlib.sha256(b).hexdigest()
  ck('source_size:'+e['path'],len(b),e['size'],0);ck('source_sha256:'+e['path'],int(sha!=e['sha256']),0,0)
  receipts.append(dict(**e,retrieval='connected GitHub pinned file/blob',own_byte_verification='MATCH'))
 save(out/'Source_Receipts.json',receipts)
 ec=js(root/'handoff/f-education-20261121/Inputs.json')['defaults']
 references={(r['labor_case'],int(r['year'])):r for r in csv.DictReader((root/'handoff/chatgpt-n3-aligned-labor-baseline-20261123/SQ_F_N3_Aligned_Labor_Annual_2026_2055.csv').open())}
 metrics=['real_gdp_trn','nominal_gdp_trn','labor_force_population_proxy','productivity_gain','nominal_wage_proxy_man','real_wage_proxy_man','tax_diagnostic_trn','government_partial_balance_proxy_trn','consolidated_partial_balance_proxy_trn','net_additional_education_spend_trn','training_credit_trn','bond_end_trn']
 selected=metrics+['real_growth_pct','population','common_deflator','core_real_gdp_trn','capital_total_real_trn','household_disposable_nominal_trn','education_service_trn','education_facility_trn','scholarship_grant_trn','additional_training_trn','training_hours','training_time_worker_equivalent','study_time_worker_equivalent','skill_stock_worker_equivalents','education_effective_labor_added','wage_gain','bond_issue_trn','bond_redemption_trn','bond_interest_trn','education_total_cost_trn','education_unassigned_cash_finance_trn','firm_training_cash_delta_trn']
 with tempfile.TemporaryDirectory() as td:
  for case in CASES:
   results={};old=list(csv.DictReader((root/'handoff/chatgpt-f-policy-cohort-fte-20261123'/case/'Annual_Comparison_2026_2055.csv').open()));fixedtrace=js(root/'handoff/chatgpt-f-policy-cohort-fte-20261123'/case/'F_Runtime_Trace.json')['years'];ci=js(root/'handoff/chatgpt-f-policy-cohort-fte-20261123'/case/'Connection_Inputs.json')
   for mask in [7,0,1,2,4,3,5,6]:
    work=Path(td)/f'{case}_{mask}';subprocess.run([sys.executable,str(HERE/'Worker.py'),str(root),str(work),case,str(mask)],check=True,stdout=subprocess.DEVNULL)
    rows=js(work/'F_Actual_Annual.json');trace=js(work/'F_Runtime_Trace.json');led=js(work/'Policy_Base_Ledgers.json');results[mask]=rows
    ck(f'{case}:{mask}:length',len(rows),30,0)
    stocks={k:0. for k in 'EST'};schedule={k:{} for k in 'EST'};prev=0.
    for i,(r,t) in enumerate(zip(rows,trace['years'])):
     y=r['year'];tag=f'{case}:{mask}:{y}:';rr=references[case,y]
     ck(tag+'year',y,2026+i,0)
     denominator=t['trajectory_effective_L']+led['elder'][i]['effective_extra']
     for k,field,lag in [('E','school_skill_units_scheduled',ec['school_lag']),('S','scholarship_skill_units_scheduled',ec['study_years']),('T','training_skill_units_scheduled',ec['training_lag'])]:
      stocks[k]=stocks[k]*(1-ec['skill_decay'])+schedule[k].get(y,0.)
      schedule[k][y+lag]=schedule[k].get(y+lag,0.)+r[field]
     ck(tag+'skill_stock_recurrence',r['skill_stock_worker_equivalents'],sum(stocks.values()))
     ck(tag+'training_units',r['training_time_worker_equivalent'],r['training_hours']/ec['annual_work_hours'])
     ck(tag+'productivity_cap',r['productivity_gain'],min(ec['productivity_cap'],sum(stocks.values())/max(1.,denominator)))
     gain=denominator*r['productivity_gain'];loss=r['training_time_worker_equivalent']+r['study_time_worker_equivalent']
     ck(tag+'education_labor_bridge',r['education_effective_labor_added'],gain-loss)
     if i:ck(tag+'single_labor_connection',t['labor'],t['trajectory_effective_L']+t['elder_effective_added']+t['health_effective_added']+r['education_effective_labor_added']+ci['common_offset'][i]+ci['elder_delta'][i],1e-5)
     ck(tag+'GDP_demand_capacity',r['real_gdp_trn'],t['desired']-t['unmet'])
     ck(tag+'no_legacy_education_stock',t['education_nom'],0.)
     ck(tag+'no_legacy_level_effect',t['education_level']+t['finite'],0.)
     ck(tag+'bond_stock',r['bond_end_trn'],r['bond_begin_trn']+r['bond_issue_trn']-r['bond_redemption_trn'])
     ck(tag+'credit_split',r['training_credit_trn'],r['credit_on_existing_trn']+r['credit_on_added_trn'])
     ck(tag+'grant_disjoint_uses',r['scholarship_grant_trn'],r['scholarship_HH_consumption_trn']+r['scholarship_saving_trn']+r['scholarship_loan_displacement_trn'])
     ck(tag+'gross_spend',r['gross_education_spend_trn'],r['education_facility_trn']+r['education_service_trn']+r['scholarship_grant_trn'])
     ck(tag+'net_spend',r['net_additional_education_spend_trn'],r['gross_education_spend_trn']-r['reallocated_education_budget_trn'])
     ck(tag+'warning_only_no_expansion',r['education_multiplier']+r['training_multiplier'],2.)
     for k in ['risk','inflation','trajectory_effective_L','elder_effective_added']:
      ck(tag+'preserved_'+k,t[k],fixedtrace[i][k])
     if y<2028:ck(tag+'no_early_education',gain+loss+r['gross_education_spend_trn']+r['training_credit_trn'],0.)
     if mask==7:
      for k,field in [('real_gdp_trn','new_F_real_GDP_trn'),('nominal_gdp_trn','new_nominal_gdp_trn'),('tax_diagnostic_trn','new_tax_diagnostic_trn'),('real_wage_proxy_man','new_real_wage_proxy_man'),('consolidated_partial_balance_proxy_trn','new_consolidated_partial_balance_proxy_trn')]:ck(tag+'fixed_F_replay_'+k,r[k],float(old[i][field]),1e-6)
     if y==2026:
      ck(tag+'anchor_real',r['real_gdp_trn'],580.);ck(tag+'anchor_nominal',r['nominal_gdp_trn'],600.)
     b=dict(labor_case=case,mask=mask,E=bool(mask&1),S=bool(mask&2),T=bool(mask&4),year=y,**{k:r[k] for k in selected},SQ_real_GDP_trn=float(rr['SQ_real_GDP_trn']),N3_real_GDP_trn=float(rr['N3_real_GDP_trn']),old_F_real_GDP_trn=float(old[i]['new_F_real_GDP_trn']),F_minus_SQ_trn=r['real_gdp_trn']-float(rr['SQ_real_GDP_trn']),F_minus_N3_trn=r['real_gdp_trn']-float(rr['N3_real_GDP_trn']),delta_vs_old_F_trn=r['real_gdp_trn']-float(old[i]['new_F_real_GDP_trn']),actual_FTE=None,additional_employed_persons_from_education=None,national_PB_trn=None,total_national_bond_issue_trn=None)
     annual.append(b)
     bridge.append(dict(labor_case=case,mask=mask,year=y,education_worker_denominator=denominator,school_skill_stock=stocks['E'],scholarship_skill_stock=stocks['S'],training_skill_stock=stocks['T'],skill_stock=sum(stocks.values()),gross_productive_worker_equivalent=gain,training_hours=r['training_hours'],training_loss_worker_equivalent=r['training_time_worker_equivalent'],study_loss_worker_equivalent=r['study_time_worker_equivalent'],net_education_worker_equivalent=gain-loss,engine_labor=t['labor'],core_GDP_trn=t['coreY'],education_service_direct_real_trn=r['education_service_domestic_nominal_trn']/t['coreD'],education_facility_nominal_trn=r['education_facility_domestic_nominal_trn'],GDP_trn=t['Y'],unmet_demand_trn=t['unmet'],legacy_education_flow=t['education_nom'],legacy_level_effect=t['education_level'],actual_FTE=None))
    shutil.rmtree(work)
   # Exact factorial/Shapley decomposition including all nonlinear feedback.
   for i in range(30):
    y=2026+i
    for metric in metrics:
     v={m:results[m][i][metric] for m in range(8)};total=v[7]-v[0];phi={}
     for bit,k in [(1,'E'),(2,'S'),(4,'T')]:
      phi[k]=sum(math.factorial(m.bit_count())*math.factorial(2-m.bit_count())/6*(v[m|bit]-v[m]) for m in range(8) if not m&bit)
     ck(f'{case}:{y}:Shapley:{metric}',sum(phi.values()),total)
     mob={}
     for m in [1,2,4,3,5,6,7]:mob[m]=sum((-1)**(m.bit_count()-s.bit_count())*v[s] for s in range(8) if s&m==s)
     ck(f'{case}:{y}:factorial:{metric}',sum(mob.values()),total)
     decomp.append(dict(labor_case=case,year=y,metric=metric,all_off=v[0],all_on=v[7],total_education_effect=total,shapley_E=phi['E'],shapley_S=phi['S'],shapley_T=phi['T'],E_alone=mob[1],S_alone=mob[2],T_alone=mob[4],ES_interaction=mob[3],ET_interaction=mob[5],ST_interaction=mob[6],EST_interaction=mob[7],E_marginal_off=v[7]-v[6],S_marginal_off=v[7]-v[5],T_marginal_off=v[7]-v[3]))
   on=results[7];i=2035-2026
   for label,g in [('2035_YOY',on[i]['real_gdp_trn']/on[i-1]['real_gdp_trn']-1),('2034_YOY_preceding_available',on[i-1]['real_gdp_trn']/on[i-2]['real_gdp_trn']-1),('2026_2035_CAGR',(on[i]['real_gdp_trn']/on[0]['real_gdp_trn'])**(1/i)-1)]:
    warnings.append(dict(labor_case=case,evaluation_year=2035,growth_definition=label,growth=g,threshold=.012,reference_warning=g<.012,automatic_expansion=False,policy_formula_not_confirmed=True))
   print(json.dumps(dict(case=case,paths=8,years=240,real2055=on[-1]['real_gdp_trn'],education_GDP2055=on[-1]['real_gdp_trn']-results[0][-1]['real_gdp_trn'])),flush=True)
 dump(out/'Annual_Comparison_2026_2055.csv',annual);dump(out/'Education_Bridge_2026_2055.csv',bridge);dump(out/'Contribution_And_Interactions.csv',decomp);dump(out/'2035_Reference_Warnings.csv',warnings)
 dump(out/'Key_Years.csv',[r for r in annual if r['year'] in [2026,2030,2035,2040,2045,2050,2055]])
 dump(out/'Validation_Checks.csv',checks);save(out/'Validation.json',dict(new_checks=len(checks),failed=sum(not r['passed'] for r in checks),executed_paths=48,executed_years=1440,fixed_F_replays=6,SQ_N3='fixed comparison reused; not rerun',RP023_M1925='HOLD',RP024='PENDING',formal_acceptance=False))
if __name__=='__main__':main(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE/'sources',Path(sys.argv[2]).resolve() if len(sys.argv)>2 else HERE)
