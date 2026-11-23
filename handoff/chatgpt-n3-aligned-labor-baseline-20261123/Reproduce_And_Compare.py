"""Six native baseline rebuilds, independent output replay, source-byte and state checks."""
import argparse,concurrent.futures,csv,hashlib,json,math,pathlib,shutil,subprocess,sys,tempfile
from Rebuild_N3_Worker import P,BD,ND,ROB,TRANS,BASE,SQ,js,save
CASES=['BASE_SQ_UNCHANGED','PREVIOUS_FINE_AGE_HOURS','ANNUAL_ALIGNED_FULL_RATES','OCTOBER_NEAR_FULL_RATES','ANNUAL_FINE_WEEK_HOURS','ANNUAL_MONTH_HOURS_PROFILE']
ALLSQ=CASES+['ANNUAL_SAME_SURVEY_UNDER65','OLDER_FINE_RATES_ONLY','UNIFORM_LEVEL_CONTROL']
SOURCE='21de7c095b500575934f7c098d5bc6f183cc6710';REQUEST='99a984a0d2e3fec3fc9e9a249afa2e9dc13bed96'
def sha(b):return hashlib.sha256(b).hexdigest()
def csvout(path,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def run(root,out,replay):
 out.mkdir(parents=True,exist_ok=True)
 worker=pathlib.Path(__file__).resolve().parent/'Rebuild_N3_Worker.py'
 for c in CASES:
  if not (out/c/'N3_Annual.json').exists():subprocess.run([sys.executable,str(worker),'--root',str(root),'--out',str(out/c),'--case',c],check=True)
 checks=[]
 def ck(name,a,b=0.,tol=1e-6):
  error=abs(a-b);ok=math.isfinite(error) and error<=tol;checks.append(dict(check=name,error=error,tolerance=tol,passed=ok));assert ok,(name,a,b)
 def same(name,a,b):ck(name,0 if a==b else 1,0,0)
 # Own receipt, not predecessor's declared result.
 source=[]
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only',SOURCE,'--',P],cwd=root,text=True).splitlines()
 for path in paths:
  raw=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=root);b=(root/path).read_bytes();same('prior_bytes:'+path,raw,b);source.append(dict(path=path,commit=SOURCE,size=len(b),sha256=sha(b)))
 same('prior_file_count',len(paths),169)
 for name,expected in [('Manifest.json','d6bb00f37f70531e2590a04d491b74dfbbf2d1f27cbd40f420d9665204679ac2'),('SPE_Labor_Timing_65Plus_Annual_Hours_Connection_Report_DRAFT_20261123.md','f0792c6e23919b8f156dc579ff1cccb8c8e76389d8075aecf3613799ab509a05')]:same('known_sha:'+name,sha((root/P/name).read_bytes()),expected)
 save(out/'Prior_Originals_Receipt.json',dict(commit=SOURCE,files=source,bytes=sum(x['size'] for x in source)))
 sourceidx={}
 for c in CASES:
  for row in js(out/c/'Runtime_Source_Receipts.json'):sourceidx[row['path']]=row
 for path,row in sourceidx.items():
  b=subprocess.check_output(['git','show',REQUEST+':'+path],cwd=root);same('runtime_pinned:'+path,sha(b),row['sha256']);same('runtime_size:'+path,len(b),row['size'])
 save(out/'Fixed_Runtime_Source_Identity.json',dict(commit=REQUEST,files=list(sourceidx.values())))
 if replay:
  with tempfile.TemporaryDirectory(prefix='n3-aligned-replay-') as tmp:
   tmp=pathlib.Path(tmp)
   def one(c):
    z=subprocess.run([sys.executable,str(worker),'--root',str(root),'--out',str(tmp/c),'--case',c],capture_output=True,text=True);assert z.returncode==0,(c,z.stderr)
    return c
   with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:list(e.map(one,CASES))
   reproduced=[]
   for c in CASES:
    for f in sorted((out/c).glob('*.json')):
     if f.name=='Runtime_Source_Receipts.json':continue
     b=f.read_bytes();other=(tmp/c/f.name).read_bytes();same('reproduced:'+c+'/'+f.name,b,other);reproduced.append(dict(path=c+'/'+f.name,size=len(b),sha256=sha(b),match=True))
   save(out/'Reproduction_Verification.json',dict(status='PASS',method='fresh processes; native SQ/N3 rebuild plus dynamic 30-year execution',cases=6,files=reproduced,mismatches=0))
 prior=js(root/P/'Fixed_Aligned_Case_Inputs.json');baseline_n3=js(root/P/'N3_BASE_UNCHANGED/N3_Actual_Annual.json');base_spec=js(out/CASES[0]/'Runtime_Specification.json');references=[];annual=[];new_runtime=0;gdp_native_rounding={}
 for c in ALLSQ:
  sq=js(root/P/c/('Common_Trace_'+('BASE_SQ_REPLAY' if c==CASES[0] else c)+'.json'))['years'];f=js(root/P/('F_BASE_UNCHANGED' if c==CASES[0] else 'F_'+c)/'F_Actual_Annual.json') if c in CASES else None
  if c in CASES:
   p=out/c;n3=js(p/'N3_Annual.json');refs=js(p/'N3_References_Used.json');native=js(p/'Native_Base_Trace.json');idx={(t['case'],t['year']):t for t in native['records']};ci=js(p/'Component_Initialization.json');mi=js(p/'Medical_Initialization.json');spec=js(p/'Runtime_Specification.json');rv=js(p/'N3_Runtime_Validation.json');dyn=js(p/'N3_Dynamic_Base_Factors.json');fin=js(p/'N3_Fiscal.json');new_runtime+=rv['checks'];same(c+':native_no_failures',rv['failures'],[]);same(c+':switches',spec,base_spec);same(c+':N3_30years',len(n3),30)
   oldci=js(root/ROB/'Component_Initialization.json');oldmi=js(root/TRANS/'Medical_Initialization.json');oldnative=js(root/BD/'N3_Unchanged_Execution_Trace.json');oldidx={(x['case'],x['year']):x for x in oldnative['records']}
   same(c+':medical_population',mi['population'],oldmi['population']);same(c+':policy_spec',ci['s'],oldci['s']);same(c+':params',native['parameters'][BASE],oldnative['parameters'][BASE]);gdp_native_rounding[c]=max(abs(idx[SQ,y]['Y']-sq[y-2026]['Y']) for y in range(2026,2056))
   for i,row in enumerate(n3):
    y=2026+i;t=idx[BASE,y];q=idx[SQ,y];ref=refs[i];expect=prior['cases'][c]['engine_L'][i]
    for label,value in [('base_labor',t['labor']),('sq_labor',q['labor']),('saved_base_labor',ref['base_labor']),('saved_sq_labor',ref['sq_labor'])]:ck(c+':'+str(y)+':'+label,value,expect,1e-5)
    same(c+':'+str(y)+':base_reference_hash',ref['base_sha256'],sha(json.dumps(t,sort_keys=True).encode()));same(c+':'+str(y)+':sq_reference_hash',ref['sq_sha256'],sha(json.dumps(q,sort_keys=True).encode()))
    for k in ['coreY','coreN','coreD']:
     ck(c+':'+str(y)+':common_'+k,t[k],q[k]);ck(c+':'+str(y)+':prior_'+k,q[k],sq[i][k])
    ck(c+':'+str(y)+':preserved_SQ',q['Y'],sq[i]['Y']);ck(c+':'+str(y)+':wage_reference',ref['sq_wage_reference'],q['nominalwage_proxy'],0)
    oq=oldidx[SQ,y]
    # Ratios preserve published predecessor precision for unchanged initializations.
    ck(c+':'+str(y)+':medical_init',mi['deflators'][i],oldmi['deflators'][i]*q['coreD']/oq['coreD'],1e-10)
    ck(c+':'+str(y)+':component_medical_same',ci['deflators'][i],mi['deflators'][i],1e-10)
    ck(c+':'+str(y)+':core_nominal_ref',ref['core_nominal_reference'],oldci['config']['core_nominal'][i]*q['coreN']/oq['coreN'],1e-9)
    ck(c+':'+str(y)+':GI_OFF',abs(row['government_purchase_nominal_trn'])+abs(row['public_investment_nominal_trn']))
    ck(c+':'+str(y)+':SQ_denominator',row['SQ_real_GDP_trn'],q['Y'],0);ck(c+':'+str(y)+':gap',row['GDP_minus_SQ_trn'],row['real_GDP_trn']-q['Y'])
    ck(c+':'+str(y)+':tax_lag_factor',row['lagged_wage_base_factor'],dyn[i]['wage_base_factor'])
    if i==0:
     for k,v in [('coreY',580),('coreN',600)]:ck(c+':initial_'+k,t[k],v)
     ck(c+':initial_L',t['labor'],prior['cases'][c]['engine_L'][0],1e-5)
    if c==CASES[0]:
     for k in ['real_GDP_trn','nominal_GDP_trn','total_tax_diagnostic_proxy_trn','CL_PB_candidate_trn','CL_debt_candidate_trn','pension_fund_end_trn']:ck('baseline_replay:'+str(y)+k,row[k],baseline_n3[i][k])
   for old,new,dep in [('Runner.base','Native_Base_Trace.json','native N3 full policy/medical/tax states'),('Runner.sq','Native_Base_Trace.json','native SQ complete denominator states'),('Component_Initialization','Component_Initialization.json','SQ wage, common core nominal, medical deflator, demographics'),('Medical_Initialization','Medical_Initialization.json','same condition medical deflators/population'),('Runner.fiscal/sf','Fiscal_Rebuilt_References.json','national fiscal mapping from new native annual accounts'),('Runner.primary','Primary_Rebuilt_References.json','native tax less expenditure plus removed medical interest'),('Runner.funding','native/runtime/Corporate_Funding_Stock.csv','new native firm source-use ledger')]:references.append(dict(case=c,old_reference=old,rebuilt_file=c+'/'+new,dependency=dep,status='REGENERATED_AND_EXECUTED',verification='source identity, year references, arithmetic, fresh replay'))
  for i,q in enumerate(sq):
   y=q['year'];r=dict(labor_case=c,year=y,SQ_real_GDP_trn=q['Y'],SQ_nominal_GDP_trn=q['N'],SQ_macro_tax_proxy_trn=q['tax'],SQ_direct_tax_proxy_trn=q['direct'],F_real_GDP_trn=f[i]['real_gdp_trn'] if f else None,F_nominal_GDP_trn=f[i]['nominal_gdp_trn'] if f else None,F_tax_diagnostic_proxy_trn=f[i]['tax_diagnostic_trn'] if f else None,F_government_partial_balance_proxy_trn=f[i]['government_partial_balance_proxy_trn'] if f else None,F_insurer_known_balance_proxy_trn=f[i]['insurer_known_change_and_program_balance_trn'] if f else None,F_minus_SQ_trn=f[i]['real_gdp_trn']-q['Y'] if f else None,SQ_source_commit=SOURCE,F_source_commit=SOURCE if f else None,N3_status='EXECUTED' if c in CASES else 'N/A_OUTSIDE_SIX_REQUESTED_PRIORITY_CONDITIONS',general_government_PB=None,general_government_debt=None,actual_gross_bond_issue=None)
   if c in CASES:
    n=n3[i];r.update(N3_real_GDP_trn=n['real_GDP_trn'],N3_nominal_GDP_trn=n['nominal_GDP_trn'],N3_minus_SQ_trn=n['real_GDP_trn']-q['Y'],N3_native_SQ_denominator_trn=n['SQ_real_GDP_trn'],N3_native_minus_preserved_SQ_rounding_trn=n['SQ_real_GDP_trn']-q['Y'],N3_change_vs_current_trn=n['real_GDP_trn']-baseline_n3[i]['real_GDP_trn'],N3_macro_tax_proxy_trn=n['macro_tax_proxy_trn'],N3_total_tax_diagnostic_proxy_trn=n['total_tax_diagnostic_proxy_trn'],N3_CL_PB_candidate_trn=n['CL_PB_candidate_trn'],N3_CL_debt_candidate_trn=n['CL_debt_candidate_trn'],N3_CL_assets_candidate_trn=n['CL_assets_candidate_trn'],N3_pension_fund_trn=n['pension_fund_end_trn'],N3_pension_contribution_trn=n['pension_contribution_trn'],N3_medical_price_factor=js(out/c/'N3_Connection_Trace.json')[i]['medical_price_factor'],N3_additional_G_nominal_trn=n['government_purchase_nominal_trn'],N3_additional_I_nominal_trn=n['public_investment_nominal_trn'])
   annual.append(r)
 ck('current2055',js(out/CASES[0]/'N3_Annual.json')[-1]['real_GDP_trn'],483.991492,5e-7)
 csvout(out/'N3_Baseline_Reference_And_Rebuild_Map.csv',references);csvout(out/'SQ_F_N3_Aligned_Labor_Annual_2026_2055.csv',annual);csvout(out/'SQ_F_N3_Aligned_Labor_Key_Years.csv',[r for r in annual if r['year'] in [2026,2030,2035,2039,2055]]);csvout(out/'Validation_Checks.csv',checks)
 save(out/'N3_Changed_Baseline_Validation.json',dict(status='PASS',new_reference_and_reproduction_checks=len(checks),new_native_runtime_checks=new_runtime,new_total_checks=len(checks)+new_runtime,failed=0,N3_conditions=6,N3_annual_rows=180,N3_changed_conditions=5,annual_comparison_rows=len(annual),prior_execution_only=dict(SQ_paths=9,F_paths=6,N3_paths=1,annual_rows=480,checks=5265,N3_checks=748,Claude_checks=2845),same_runtime_current_reexecuted=True,previous_checks_added_to_new_count=False,native_SQ_vs_preserved_SQ_max_absolute_GDP_rounding_trn=gdp_native_rounding,rounding_tolerance_trn=1e-6,policy_switches_unchanged=True,additional_GI='OFF',formal_acceptance=False,RP023_M1925='HOLD',RP024='PENDING'))
 # Remove reproducible staging copies; retain native annual accounts and resolved runtime source.
 for c in CASES:
  p=out/c
  for name in ['bootstrap','draft-source','fiscal-input','fiscal']:shutil.rmtree(p/name,ignore_errors=True)
  for f in (p/'native').iterdir():
   if f.is_file() and f.name not in ['Resolved_SQ_COMMON_ON.py.txt','Resolved_PARITY_CONNECTED_CANDIDATE.py.txt']:f.unlink()
  for f in (p/'native/runtime').iterdir():
   if f.name not in ['Gap_Annual.csv','N3_Engine_Accounts.csv','Corporate_Funding_Stock.csv']:f.unlink()
 print(json.dumps(dict(status='PASS',new_checks=len(checks)+new_runtime,reference_checks=len(checks),runtime_checks=new_runtime,annual_rows=len(annual),results2055=[r for r in annual if r['year']==2055 and r['labor_case'] in CASES]),ensure_ascii=False),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--replay',action='store_true');a=p.parse_args();run(a.root.resolve(),a.out.resolve(),a.replay)
