"""Execute F off/on with a pure observer; reuse fixed non-adopted diagnoses."""
import copy,csv,hashlib,json,math,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from Review_Indicators import observe,population_band,below_population_threshold
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
P=ROOT/'handoff/chatgpt-f-foreign-workforce-policy-alignment-20261123'
FTE=ROOT/'handoff/chatgpt-f-policy-cohort-fte-20261123'
CASES=['BASE_SQ_UNCHANGED','PREVIOUS_FINE_AGE_HOURS','ANNUAL_ALIGNED_FULL_RATES','OCTOBER_NEAR_FULL_RATES','ANNUAL_FINE_WEEK_HOURS','ANNUAL_MONTH_HOURS_PROFILE']
def js(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def read(p):return list(csv.DictReader(p.open()))
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(out):
 out.mkdir(parents=True,exist_ok=True);checks=[];receipts=[];bytechecks=[]
 def ck(n,a,b=0,tol=0):
  err=abs(a-b);passed=math.isfinite(err) and err<=tol;checks.append(dict(check=n,error=err,tolerance=tol,passed=passed));assert passed,(n,a,b)
 for e in js(HERE/'Fixed_Source_Expected.json'):
  b=(ROOT/e['path']).read_bytes();sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
  ck('source_size:'+e['path'],len(b),e['size']);ck('source_blob:'+e['path'],int(sha!=e['git_blob_sha1']))
  receipts.append(dict(**e,sha256=hashlib.sha256(b).hexdigest(),own_bytes='MATCH'))
 save(out/'Fixed_Source_Receipts.json',receipts)
 # Boundary/sequence tests exercise real observer functions, not macro outputs.
 for r,want in [(.029999,'BELOW_3'),(.03,'WITHIN_3_TO_5'),(.05,'WITHIN_3_TO_5'),(.050001,'ABOVE_5')]:ck('band_boundary:'+str(r),int(population_band(r)!=want))
 for pop,want in [(99999999,True),(100000000,False),(100000001,False)]:ck('100m_boundary:'+str(pop),int(below_population_threshold(pop)),int(want))
 state={};synthetic=[]
 for i,(ratio,pop) in enumerate([(.051,1e8),(.052,99999999),(.04,1e8),(.029,99999999),(.03,1e8)]):
  r=observe(2026+i,ratio*pop,pop,ratio*pop,0,1,1,0,600,1,1,1,state);synthetic.append(r)
 for i,want in enumerate([1,2,0,1,0]):ck('outside_streak:'+str(i),synthetic[i]['consecutive_outside_years'],want)
 for i,r in enumerate(synthetic):
  ck('synthetic_no_admission:'+str(i),r['actual_admission_adjustment']);ck('synthetic_no_multiplier:'+str(i),r['actual_relaxation_multiplier'],1);ck('synthetic_no_fiscal:'+str(i),r['actual_fiscal_savings_trn'])
  ck('GDP_formal_NA:'+str(i),int(r['gdp_formal_review_flag'] is not None))
 ck('relaxation_candidate20',synthetic[1]['relaxation_candidate_pct'],20)
 save(out/'Boundary_Test_Examples.json',synthetic)
 # Only a read-only observer is added around the immutable prior adapter.
 source=(P/'F_Alignment_Adapter.py').read_text();old='def f(root,out,offset,elder_delta,foreign_source):';assert source.count(old)==1
 source=source.replace(old,old.replace('foreign_source):','foreign_source,observer=None):'))
 needle=' assert len(rows)==len(tr)==30';assert source.count(needle)==1
 source=source.replace(needle," if observer is not None:\n  for i,r in enumerate(rows):observer(copy.deepcopy(dict(row=r,trace=tr[i],foreign=b['foreign'][i])))\n"+needle)
 ns={'__name__':'read_only_observer_adapter'};exec(compile(source,'read_only_observer_adapter.py','exec'),ns)
 prior=read(P/'Annual_Comparison_All.csv');fixed={(r['common_case'],int(r['year'])):r for r in prior if r['branch']=='F_RETAINED'}
 cfg=js(ROOT/'handoff/f-vat-core-20261120/Inputs.json')['household_inputs']['pension_inputs']['foreign_inputs']['reference']
 alerts=[];comparison=[];summary=[];logs=[]
 metrics=['real_gdp_trn','nominal_gdp_trn','population','labor_force_population_proxy','tax_diagnostic_trn','government_partial_balance_proxy_trn','consolidated_partial_balance_proxy_trn','nominal_wage_proxy_man','real_wage_proxy_man','household_disposable_nominal_trn','capital_total_real_trn']
 with tempfile.TemporaryDirectory(prefix='spe_review_triggers_') as td:
  for case in CASES:
   conn=js(FTE/case/'Connection_Inputs.json');pt=js(FTE/case/'F_Runtime_Trace.json')['years'];states={};seen=[]
   def observer(snap):
    r=snap['row'];f=snap['foreign'];i=r['year']-2026;ref=pt[max(0,i-1)]
    a=observe(r['year'],f['foreign_resident_stock'],f['population'],f['foreign_resident_stock']-f['resident_stock_delta'],f['resident_stock_delta'],f['foreign_effective_labor'],f['foreign_jobs'],f['government_program_base_trn']+f['employer_program_base_trn'],ref['N'],ref['coreD']/(600/580),cfg['VA_yen'],cfg['labor_cost_yen'],states)
    seen.append(dict(common_case=case,**a))
   paths={}
   for mode in ['BEFORE','AFTER']:
    work=Path(td)/(case+'_'+mode);work.mkdir();ns['f'](ROOT,work,conn['common_offset'],conn['elder_delta'],None,observer if mode=='AFTER' else None);paths[mode]=work
   before=js(paths['BEFORE']/'F_Actual_Annual.json');after=js(paths['AFTER']/'F_Actual_Annual.json');trace=js(paths['AFTER']/'F_Runtime_Trace.json')['years']
   for f in sorted(paths['BEFORE'].iterdir()):
    b=f.read_bytes();a=(paths['AFTER']/f.name).read_bytes();ck('whole_output_bytes:'+case+f.name,int(a!=b))
    bytechecks.append(dict(common_case=case,file=f.name,size=len(b),sha256_before=hashlib.sha256(b).hexdigest(),sha256_after=hashlib.sha256(a).hexdigest(),passed=a==b))
   ck('annual_observations:'+case,len(seen),30);annual=[]
   for i,(b,a,t,alert) in enumerate(zip(before,after,trace,seen)):
    y=2026+i;tag=case+str(y);ref=fixed[case,y]
    for k in metrics:ck('no_intervention:'+tag+k,a[k],b[k])
    for k,pk in [('real_gdp_trn','real_GDP_trn'),('nominal_gdp_trn','nominal_GDP_trn'),('population','total_population'),('labor_force_population_proxy','engine_labor'),('tax_diagnostic_trn','tax_diagnostic_trn'),('government_partial_balance_proxy_trn','government_partial_balance_proxy_trn'),('consolidated_partial_balance_proxy_trn','consolidated_partial_balance_proxy_trn')]:ck('prior_replay:'+tag+k,a[k],float(ref[pk]),1e-6)
    ck('stock_decomposition:'+tag,alert['foreign_resident_numerator'],alert['foreign_reference_stock']+alert['foreign_F_policy_stock_delta'],1e-6)
    ck('ratio_decomposition:'+tag,alert['population_ratio'],alert['reference_stock_contribution_ratio']+alert['F_policy_stock_contribution_ratio'],1e-12)
    ck('no_adjustment:'+tag,alert['actual_admission_adjustment']);ck('no_multiplier:'+tag,alert['actual_relaxation_multiplier'],1);ck('GDP_undefined:'+tag,int(alert['gdp_formal_review_flag'] is not None))
    ck('risk_fixed:'+tag,t['risk'],pt[i]['risk']);ck('inflation_fixed:'+tag,t['inflation'],pt[i]['inflation'])
    if i==0:ck('real_anchor:'+case,a['real_gdp_trn'],580);ck('nominal_anchor:'+case,a['nominal_gdp_trn'],600)
    z=dict(common_case=case,year=y,SQ_real_GDP_trn=float(ref['SQ_real_GDP_trn']),N3_real_GDP_trn=float(ref['N3_real_GDP_trn']),F_minus_SQ_trn=a['real_gdp_trn']-float(ref['SQ_real_GDP_trn']),F_minus_N3_trn=a['real_gdp_trn']-float(ref['N3_real_GDP_trn']),foreign_population=alert['foreign_resident_numerator'],foreign_reference_stock=alert['foreign_reference_stock'],foreign_F_policy_stock_delta=alert['foreign_F_policy_stock_delta'],foreign_actual_FTE=None,elder_conditional_FTE_2080=float(ref['elder_conditional_FTE_2080']))
    for k in metrics:z['before_'+k]=b[k];z['after_'+k]=a[k];z['delta_'+k]=a[k]-b[k]
    annual.append(z)
   dump(out/(case+'_Annual_Indicators.csv'),seen);dump(out/(case+'_Annual_Comparison.csv'),annual);alerts+=seen;comparison+=annual
   for name,pred in [('population_outside',lambda r:r['population_review_flag']),('population_above5',lambda r:r['population_band']=='ABOVE_5'),('population_below3',lambda r:r['population_band']=='BELOW_3'),('below100m',lambda r:r['below100_review_flag']),('post2030_review',lambda r:r['post2030_review_candidate']),('proxy_VA_reference_only',lambda r:r['proxy_VA_above5_reference_only']),('proxy_labor_reference_only',lambda r:r['proxy_labor_above5_reference_only']),('proxy_program_reference_only',lambda r:r['proxy_program_above5_reference_only'])]:
    active=[r for r in seen if pred(r)];summary.append(dict(common_case=case,indicator=name,first_year=active[0]['year'] if active else None,total_active_years=len(active),active_2055=bool(pred(seen[-1])),automatic_policy_effect=False,formal_GDP_status='N/A'))
   logs.append(dict(common_case=case,before_rows=30,after_rows=30,observer_rows=30,max_macro_difference=max(abs(r['delta_real_gdp_trn']) for r in annual)));print(json.dumps(logs[-1]),flush=True)
 # Non-adopted restriction diagnostics are preserved fixed results, not rerun.
 diag=[]
 for r in prior:
  if r['branch']=='F_RETAINED':continue
  rr=fixed[r['common_case'],int(r['year'])];diag.append(dict(branch=r['branch'],common_case=r['common_case'],year=int(r['year']),status='FIXED_NON_ADOPTED_RESTRICTION; NOT_WARNING_BASE',source_commit='a7902595d96cfbebd7207a0a64cf5c2a991d1fc5',diagnostic_real_GDP_trn=float(r['real_GDP_trn']),warning_F_real_GDP_trn=float(rr['real_GDP_trn']),diagnostic_minus_warning_F_trn=float(r['real_GDP_trn'])-float(rr['real_GDP_trn']),diagnostic_foreign_population=float(r['foreign_resident_stock']),diagnostic_foreign_population_ratio=float(r['foreign_population_ratio']),warning_foreign_population_ratio=float(rr['foreign_population_ratio']),cap_active=r['cap_active']))
 dump(out/'Annual_Indicators_All.csv',alerts);dump(out/'F_SQ_N3_Annual_Comparison.csv',comparison);dump(out/'Fixed_Nonadopted_Restriction_Comparison.csv',diag)
 dump(out/'First_Warning_And_Duration.csv',summary);dump(out/'Key_Years_Indicators.csv',[r for r in alerts if r['year'] in [2026,2030,2035,2040,2045,2050,2055]]);dump(out/'Key_Years_Comparison.csv',[r for r in comparison if r['year'] in [2026,2030,2035,2040,2045,2050,2055]])
 dump(out/'Before_After_Full_Byte_Identity.csv',bytechecks);dump(out/'Validation_Checks.csv',checks);save(out/'Execution_Log.json',logs)
 save(out/'Validation.json',dict(status='PASS',new_checks=len(checks),failed=0,executed_paths=12,executed_annual_rows=360,indicator_rows=180,fixed_diagnostic_rows=len(diag),full_before_after_output_byte_matches=len(bytechecks),GDP_formal_warning='N/A',automatic_admission_change=False,formal_policy_text_modified=False,RP023_M1925='HOLD',RP024='PENDING'))
if __name__=='__main__':run(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE)
