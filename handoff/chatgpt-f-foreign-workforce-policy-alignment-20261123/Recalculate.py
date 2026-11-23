"""Run inherited FTE F and non-adopted foreign-policy interpretations."""
import csv,hashlib,json,math,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
import F_Alignment_Adapter as A
from Build_Foreign_Source import BRANCHES,build,trigger,admission_cap
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'handoff/chatgpt-f-policy-cohort-fte-20261123'
CASES=['BASE_SQ_UNCHANGED','PREVIOUS_FINE_AGE_HOURS','ANNUAL_ALIGNED_FULL_RATES','OCTOBER_NEAR_FULL_RATES','ANNUAL_FINE_WEEK_HOURS','ANNUAL_MONTH_HOURS_PROFILE']
FOCUS='ANNUAL_FINE_WEEK_HOURS'
def js(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def read(p):return list(csv.DictReader(p.open()))
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def run(out):
 out.mkdir(parents=True,exist_ok=True);checks=[];sources=[]
 def ck(n,a,b=0,tol=1e-6):
  error=abs(a-b);ok=math.isfinite(error) and error<=tol+1e-11*abs(b)
  checks.append(dict(check=n,error=error,passed=ok));assert ok,(n,a,b)
 for e in js(HERE/'Fixed_Source_Expected.json'):
  b=(ROOT/e['path']).read_bytes();sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
  ck('source_size:'+e['path'],len(b),e['size'],0);ck('source_blob:'+e['path'],int(sha!=e['git_blob_sha1']),0,0)
  sources.append(dict(**e,sha256=hashlib.sha256(b).hexdigest(),own_bytes='MATCH'))
 save(out/'Fixed_Source_Receipts.json',sources);save(out/'Branch_Definitions.json',BRANCHES)
 old={(r['case'],int(r['year'])):r for r in read(PRIOR/'Annual_Comparison_All_Cases.csv')}
 refs={(r['labor_case'],int(r['year'])):r for r in read(ROOT/'handoff/chatgpt-n3-aligned-labor-baseline-20261123/SQ_F_N3_Aligned_Labor_Annual_2026_2055.csv')}
 allrows=[];execution=[];traces=[];ledgers=[];retained={}
 routes=[('F_RETAINED',c) for c in CASES]+[(b,FOCUS) for b in BRANCHES if b!='F_RETAINED']
 # Source trigger boundary tests, without treating synthetic populations as observations.
 for timing in ['SOURCE_2035','ANNUAL_LAG']:
  for year in [2029,2030,2035,2036]:
   for pop in [99999999.,100000000.,100000001.]:
    want=year>=2030 and pop<1e8 and (timing=='ANNUAL_LAG' or year==2035)
    ck('trigger_boundary:'+timing+str(year)+str(pop),int(trigger(year,pop,False,timing)),int(want),0)
 ck('latch2035',int(trigger(2036,110e6,True,'SOURCE_2035')),1,0)
 ck('annual_reversibility',int(trigger(2036,110e6,True,'ANNUAL_LAG')),0,0)
 # Cap helper clipping and linear-budget invariants, including exhausted stock.
 for mode in ['GDP_VA','GDP_LABOR','GDP_PROGRAM','POP_CEILING']:
  x=admission_cap(mode,1000,10,.5,10000,10000,.5,1000,.03,1000,1,100,30)
  ck('exhausted_cap:'+mode,x,0)
 for factor in [1.,1.2]:
  cap=admission_cap('GDP_PROGRAM',10000*factor,1,.5,10,0,0,1,.05,100,1,100,30)
  ck('program_budget_units:'+str(factor),100+10*30+cap*(100+30),10000*factor)
 with tempfile.TemporaryDirectory(prefix='spe_foreign_run_') as tmp:
  for index,(branch,case) in enumerate(routes):
   conn=js(PRIOR/case/'Connection_Inputs.json');priortrace=js(PRIOR/case/'F_Runtime_Trace.json')['years']
   nominal=[r['N'] for r in priortrace];deflator=[r['coreD']/(600/580) for r in priortrace]
   source=build(branch,nominal,deflator);work=Path(tmp)/(branch+'__'+case);work.mkdir()
   A.f(ROOT,work,conn['common_offset'],conn['elder_delta'],source)
   rows=js(work/'F_Actual_Annual.json');trace=js(work/'F_Runtime_Trace.json')['years'];b=js(work/'Policy_Base_Ledgers.json')
   key=branch+'__'+case;target=out/key;target.mkdir(exist_ok=True)
   save(target/'Connection_Inputs.json',dict(branch=branch,common_case=case,**conn,diagnostic_fixed_F_nominal=nominal if source else None,diagnostic_fixed_F_deflator=deflator if source else None,non_adopted=True))
   if case==FOCUS and source:(target/'Resolved_Foreign_Overlay.py.txt').write_text(source)
   annual=[]
   for i,(r,t,f) in enumerate(zip(rows,trace,b['foreign'])):
    y=2026+i;tag=key+str(y);base=old[case,y];rr=refs[case,y]
    ck(tag+':GDP',t['Y'],t['desired']-t['unmet'])
    ck(tag+':single_labor',t['labor'],t['trajectory_effective_L']+t['education_effective_added']+t['health_effective_added']+t['elder_effective_added']+conn['common_offset'][i]+(conn['elder_delta'][i] if i else 0),tol=1e-5)
    ck(tag+':population',f['population'],f['japanese']+f['foreign_resident_stock'],tol=1e-5)
    ck(tag+':macro_population',r['population'],f['population'],tol=1e-5)
    ck(tag+':flows',f['foreign_net_migration'],f['all_new_admissions']-f['all_returns'])
    ck(tag+':admission_rejections',f['all_new_admissions'],f['baseline_new_admissions']-sum(f[k] for k in ['n4_rejected','screening_rejected','scope_rejected','transition_rejected','cap_rejected']))
    ck(tag+':cohort_difference',f['resident_stock_delta'],f['target_stock']-f['target_zero_stock'])
    ck(tag+':jobs',f['foreign_jobs'],f['policy_only_foreign_jobs']+(f['foreign_resident_stock']-f['resident_stock_delta'])*f['foreign_base_employment_rate'])
    ck(tag+':ratio',f['population_ratio'],f['foreign_resident_stock']/f['population'])
    ck(tag+':elder_headcount_preserved',b['elder'][i]['F_extra_jobs'],float(base['elder_headcount']))
    ck(tag+':bounds',int(0<=f['foreign_jobs']<=f['foreign_resident_stock'] and f['cap_rejected']>=-1e-6),1,0)
    for k in ['risk','inflation']:ck(tag+':fixed_'+k,t[k],priortrace[i][k])
    if i:
     prev=b['foreign'][i-1]
     ck(tag+':stock_flow',f['foreign_resident_stock']-prev['foreign_resident_stock'],f['foreign_net_migration']+f['foreign_reference_residual'],tol=1e-5)
    if y<2030:
     ck(tag+':no_early_policy_delta',f['resident_stock_delta'],0)
     ck(tag+':no_early_cap',f['cap_rejected'],0)
     ck(tag+':before2030_GDP',r['real_gdp_trn'],float(base['new_F_real_GDP_trn']))
    if i==0:ck(tag+':real_anchor',r['real_gdp_trn'],580);ck(tag+':nominal_anchor',r['nominal_gdp_trn'],600)
    if branch=='F_RETAINED':
     ck(tag+':replayGDP',r['real_gdp_trn'],float(base['new_F_real_GDP_trn']))
     ck(tag+':replayN',r['nominal_gdp_trn'],float(base['new_nominal_gdp_trn']))
     ck(tag+':replayL',t['labor'],float(base['new_engine_L']),tol=1e-5)
    cap=f['conditional_target_admission_cap']
    if cap is not None:ck(tag+':admission_ceiling',int(f['target_new_admissions']<=cap+1e-6),1,0)
    mode=BRANCHES[branch]['mode'];num=den=ratio=None;residual=None
    if source:
     den=f['diagnostic_GDP_denominator_trn'];D=f['diagnostic_deflator'];den_yen=den*1e12
     numerator=(f['foreign_effective_labor']*9154003.810403556*D if mode=='GDP_VA' else f['foreign_jobs']*8000000*D if mode=='GDP_LABOR' else (f['government_program_base_trn']+f['employer_program_base_trn'])*D*1e12 if mode=='GDP_PROGRAM' else None)
     num=numerator/1e12 if numerator is not None else None;ratio=numerator/den_yen if numerator is not None else None
     residual=max(0.,ratio-.05*f['cap_relaxation_multiplier']) if ratio is not None else max(0.,f['population_ratio']-f['diagnostic_population_ceiling'])
     ck(tag+':fixed_lag_denominator',den,nominal[max(0,i-1)])
    row=dict(branch=branch,common_case=case,year=y,policy_interpretation='RETAINED_UNRESOLVED' if branch=='F_RETAINED' else 'DIAGNOSTIC_NOT_ADOPTED',foreign_reference_stock=f['foreign_resident_stock']-f['resident_stock_delta'],foreign_policy_stock_delta=f['resident_stock_delta'],foreign_resident_stock=f['foreign_resident_stock'],total_population=f['population'],foreign_population_ratio=f['population_ratio'],target_stock=f['target_stock'],counterfactual_target_stock=f['target_zero_stock'],gross_inflow=f['all_new_admissions'],gross_outflow=f['all_returns'],net_migration=f['foreign_net_migration'],baseline_gross_inflow=f['baseline_new_admissions'],foreign_nonmigration_reference_residual=f['foreign_reference_residual'],requested_target_inflow=f['requested_target_admissions'],accepted_target_inflow=f['target_new_admissions'],cap_rejected=f['cap_rejected'],admission_cap=cap,cap_active=f['cap_rejected']>1e-6,relaxation_multiplier=f['cap_relaxation_multiplier'],relaxation_active=bool(f['F_source2035_relaxation']),foreign_jobs=f['foreign_jobs'],policy_additional_foreign_jobs=f['policy_only_foreign_jobs'],foreign_effective_labor_inherited=f['foreign_effective_labor'],foreign_hours_weight=f['target_hours_weight'],foreign_actual_hours=None,foreign_actual_FTE=None,elder_conditional_FTE_2080=float(base['elder_conditional_FTE_2080']),engine_labor=t['labor'],common_offset_once=conn['common_offset'][i],elder_delta_once=conn['elder_delta'][i],real_GDP_trn=r['real_gdp_trn'],nominal_GDP_trn=r['nominal_gdp_trn'],delta_vs_prior_F_trn=r['real_gdp_trn']-float(base['new_F_real_GDP_trn']),SQ_real_GDP_trn=float(rr['SQ_real_GDP_trn']),N3_real_GDP_trn=float(rr['N3_real_GDP_trn']),F_minus_SQ_trn=r['real_gdp_trn']-float(rr['SQ_real_GDP_trn']),F_minus_N3_trn=r['real_gdp_trn']-float(rr['N3_real_GDP_trn']),diagnostic_numerator_trn=num,diagnostic_fixed_lag_denominator_trn=den,diagnostic_ratio=ratio,unresolved_ceiling_excess=residual,general_government_PB=None,general_government_debt=None,foreign_FTE_reason='No nationality-specific measured time; inherited effective labor is not measured FTE')
    for k in ['tax_diagnostic_trn','government_partial_balance_proxy_trn','consolidated_partial_balance_proxy_trn','nominal_wage_proxy_man','real_wage_proxy_man','household_disposable_nominal_trn','capital_total_real_trn']:row[k]=r.get(k)
    for k in ['tax_diagnostic_trn','government_partial_balance_proxy_trn','consolidated_partial_balance_proxy_trn','nominal_wage_proxy_man','real_wage_proxy_man']:
     previous=base.get('new_'+k);row['delta_vs_prior_F_'+k]=r[k]-float(previous) if previous not in [None,''] and isinstance(r.get(k),(int,float)) else None
    annual.append(row);traces.append(dict(branch=branch,common_case=case,**t));ledgers.append(dict(branch=branch,common_case=case,**f))
   dump(target/'Annual_2026_2055.csv',annual);allrows+=annual
   execution.append(dict(branch=branch,common_case=case,rows=30,first_cap_year=next((r['year'] for r in annual if r['cap_active']),None),first_relaxation_year=next((r['year'] for r in annual if r['relaxation_active']),None)))
   print(json.dumps(execution[-1]),flush=True)
 # Explicitly check no cap/trigger is silently adopted into retained candidate.
 for r in allrows:
  if r['branch']=='F_RETAINED':ck('retained_no_GDP_cap:'+r['common_case']+str(r['year']),int(r['admission_cap'] is not None),0,0)
 dump(out/'Annual_Comparison_All.csv',allrows);dump(out/'Key_Years.csv',[r for r in allrows if r['year'] in [2026,2030,2035,2040,2045,2050,2055]])
 dump(out/'F_Runtime_Trace.csv',traces);dump(out/'Foreign_Stock_Flow_Accounts.csv',ledgers);dump(out/'Validation_Checks.csv',checks)
 save(out/'Execution_Log.json',execution);save(out/'Validation.json',dict(status='PASS',new_checks=len(checks),failed=0,paths=len(routes),annual_rows=len(allrows),retained_common_cases=6,diagnostic_common_case=FOCUS,diagnostic_paths=6,formal_F_definition_adopted=False,RP023_M1925='HOLD',RP024='PENDING'))
if __name__=='__main__':run(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE)
