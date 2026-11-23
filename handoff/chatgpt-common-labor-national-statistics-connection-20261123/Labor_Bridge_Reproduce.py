"""Stdlib annual bridge. No download during reproduction; use pinned original/statistics inputs.
python Labor_Bridge_Reproduce.py --root <ec98f975 checkout> --inputs <packet>/Statistics_Inputs.json --out <empty output>
"""
import argparse,csv,hashlib,itertools,json,math,platform,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
PIN='ec98f9751cf8fc27a76d001c7e5425f904ece62c'
D='handoff/chatgpt-common-macro-demography-labor-productivity-diagnostic-20261123'
T='handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123'
HERE=Path(__file__).resolve().parent
SQCASES=['BASE_SQ_UNCHANGED','HEADCOUNT_DETAIL_2025','UNIFORM_LEVEL_CONTROL','SNA_HOURS_FIXED_CONTROL','LFS_HOURS_BASE_RATES','LFS_HOURS_DETAIL_RATES']
FCASES=['F_BASE_UNCHANGED','F_HEADCOUNT_DETAIL','F_HOURS_DETAIL']
def js(p):return json.loads(p.read_text())
def read(p):return list(csv.DictReader(p.open()))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(root,inp,out):
 out.mkdir(parents=True,exist_ok=True);s=js(inp);ckrows=[]
 def ck(name,a,b,tol=1e-7):
  error=abs(a-b);ok=math.isfinite(error) and error<=tol+1e-12*abs(b);ckrows.append(dict(check=name,error=error,tolerance=tol,passed=ok));assert ok,(name,a,b,error)
 # Check exact downloaded source envelopes, not another AI's receipt.
 import base64
 source=inp.parent/'Source_Originals'
 official=[]
 for p in sorted(source.glob('*.json')):
  x=js(p);b=base64.b64decode(x['base64']);ck('source_size:'+p.name,len(b),x['size'],0);ck('source_sha:'+p.name,0 if hashlib.sha256(b).hexdigest()==x['sha256'] else 1,0,0);official.append(dict(file=p.name,size=len(b),sha256=x['sha256']))
 ck('source_count',len(official),14,0)
 prior=js(root/D/'BASE_SQ_REPLAY/Common_Trace_BASE_SQ_REPLAY.json')['years'];L0=prior[0]['labor'];cells=read(root/D/'SQ_Age_Sex_Employment_Cells_2026_2055.csv');annuals={y:[] for y in range(2026,2056)}
 rates={(r['sex'],r['age_lower']):r['employment_rate'] for r in s['LFS_age_sex_population_employment']};hours={(r['sex'],r['age_lower']):r['annualized_hours_per_employed_proxy'] for r in s['LFS_age_sex_hours']};h24=s['SNA_history'][-1]['annual_hours_per_job'];q24=s['SNA_history'][-1]['real_GDP_per_hour_yen'];ref=s['FTE_reference_hours'];uniform=s['LFS2025_totals']['employed']/68031652.825
 detail=[]
 for row in cells:
  y=int(row['year']);a=int(row['age_lower']);sex=row['sex'];pop=float(row['persons']);old=float(row['employment_rate']);new=rates[(sex,a)] if 15<=a<65 else old
  Eold=pop*old;Enew=pop*new;h=hours[(sex,min(a,65))] if a>=15 else 0.
  # Under15 E=0 from employment definition, not missing statistical hours imputed to0.
  r=dict(year=y,nationality=row['nationality'],age_lower=a,sex=sex,population=pop,old_employment_rate=old,detail2025_rate=new,rate_source='LFS2025 I-B-1 same-cell employed/population ratio held fixed' if 15<=a<65 else 'existing pinned age-sex employment preserved; no coarsening elderly bins',employed_old=Eold,employed_detail=Enew,hours_per_employed_proxy=h if a>=15 else None,total_hours_oldrate_proxy=Eold*h,total_hours_detail_proxy=Enew*h,hours_source='LFS2025 I-B-9 aggregateweekly/employed*52;65+pooled bysex;foreign uses same conditional rates',hours_foreign_direct_observation=False)
  annuals[y].append(r);detail.append(r)
 dump(out/'SQ_Age_Sex_Employment_Hours_Bridge_Cells.csv',detail)
 case_inputs={k:dict(physical_labor=[],headcount=[],hours=[],scope='DRAFT_CONDITIONAL_NOT_ADOPTED') for k in SQCASES};meta=[]
 for i,y in enumerate(range(2026,2056)):
  rs=annuals[y];E=sum(r['employed_old'] for r in rs);En=sum(r['employed_detail'] for r in rs);H=sum(r['total_hours_oldrate_proxy'] for r in rs);Hn=sum(r['total_hours_detail_proxy'] for r in rs)
  ck('prior_cell_employment:'+str(y),E,prior[i]['labor'],1e-5)
  P=sum(r['population'] for r in rs);ck('cell_population:'+str(y),P,prior[i]['population'],1e-5)
  for cid,physical,head,hh in [('BASE_SQ_UNCHANGED',E,E,None),('HEADCOUNT_DETAIL_2025',En,En,None),('UNIFORM_LEVEL_CONTROL',E*uniform,E*uniform,None),('SNA_HOURS_FIXED_CONTROL',E*h24,E,E*h24),('LFS_HOURS_BASE_RATES',H,E,H),('LFS_HOURS_DETAIL_RATES',Hn,En,Hn)]:
   c=case_inputs[cid];c['physical_labor'].append(physical);c['headcount'].append(head);c['hours'].append(hh)
   meta.append(dict(case=cid,year=y,population=P,population15plus=sum(r['population'] for r in rs if r['age_lower']>=15),labor_force_population=None,employee_headcount=None,headcount=head,observed_annual_total_hours=None,physical_labor=physical,physical_unit='person_hours_per_diagnostic_year' if 'HOURS' in cid else 'persons',total_hours_proxy=hh,FTE_diagnostic=hh/ref if hh is not None else None,official_FTE=None,FTE_reference_hours=ref if hh is not None else None,mean_annual_hours_proxy=hh/head if hh is not None else None,real_VA_constant_SNA2024_perhour_satellite_2020_chain_trn=hh*q24/1e12 if hh is not None else None,VA_added_to_GDP=False,VA_model_price_comparison='N/A_MODEL_REAL_PRICE_BASE_UNSPECIFIED;SATELLITE_ONLY',TFP=None,capital_services=None,hours_source_year=2024 if cid=='SNA_HOURS_FIXED_CONTROL' else 2025 if 'HOURS' in cid else None,future_rate_or_hours_improvement=0.,connection='CONDITIONAL_PROXY' if cid!='BASE_SQ_UNCHANGED' else 'CURRENT_REFERENCE',nationality_specific_hours='NOT_OBSERVED',employment_definition='persons employed not labor force',future_fulltime_hours=None))
 for cid,c in case_inputs.items():
  c['engine_L']=[L0*x/c['physical_labor'][0] for x in c['physical_labor']];c['anchor_conversion']=L0/c['physical_labor'][0];c['uniform_scale']=uniform if cid=='UNIFORM_LEVEL_CONTROL' else None
 inputs=dict(fixed_commit=PIN,statistics_input_sha256=hashlib.sha256(inp.read_bytes()).hexdigest(),cases=case_inputs,initial_real=580,initial_nominal=600,labor_elasticity=.65,A_rule_unchanged=True,additional_productivity_growth=0,F_offsets={})
 for f,cid in [('F_BASE_UNCHANGED','BASE_SQ_UNCHANGED'),('F_HEADCOUNT_DETAIL','HEADCOUNT_DETAIL_2025'),('F_HOURS_DETAIL','LFS_HOURS_DETAIL_RATES')]:inputs['F_offsets'][f]=[case_inputs[cid]['engine_L'][i]-prior[i]['labor'] for i in range(30)]
 save(out/'Fixed_Labor_Bridge_Case_Inputs.json',inputs);logs=[];traces={}
 for cid in SQCASES+FCASES+['N3_BASE_UNCHANGED']:
  cmd=[sys.executable,str(HERE/'Bridge_Worker.py'),'--root',str(root),'--out',str(out/cid),'--case',cid,'--inputs',str(out/'Fixed_Labor_Bridge_Case_Inputs.json')]
  z=subprocess.run(cmd,capture_output=True,text=True);logs.append(dict(case=cid,command='python Bridge_Worker.py --root <fixed-root> --out <out>/'+cid+' --case '+cid+' --inputs <out>/Fixed_Labor_Bridge_Case_Inputs.json',exit_code=z.returncode,stdout=z.stdout,stderr=z.stderr));save(out/'Execution_Log.json',logs)
  if z.returncode:raise RuntimeError(z.stderr)
  print(cid,z.stdout.strip(),flush=True)
  if cid in SQCASES:
   src='BASE_SQ_REPLAY' if cid=='BASE_SQ_UNCHANGED' else cid;traces[cid]=js(out/cid/('Common_Trace_'+src+'.json'))
 base=traces['BASE_SQ_UNCHANGED']['years'];par=traces['BASE_SQ_UNCHANGED']['parameters'];compar=[];bridges=[];keyyears=[];ident=[]
 for cid,data in traces.items():
  rs=data['years'];c=case_inputs[cid]
  for i,r in enumerate(rs):
   y=r['year'];b=base[i];m=next(x for x in meta if x['case']==cid and x['year']==y);phys=c['physical_labor'][i];ratio=phys/c['physical_labor'][0]
   ck('ratio_units:'+cid+str(y),r['labor']/L0,ratio);ck('engine_labor:'+cid+str(y),r['labor'],c['engine_L'][i],1e-5);ck('core_formula:'+cid+str(y),r['coreY'],580*b['nonlabor_factor']*ratio**.65)
   for k in ['population','working_age_population','foreign_population','risk','inflation','nonlabor_factor','medical_input_deflator']:ck('preserved:'+cid+str(y)+k,r[k],b[k])
   ck('initial_real:'+cid,rs[0]['Y'],580);ck('initial_nominal:'+cid,rs[0]['N'],600);ck('alpha:'+cid, data['parameters']['labor_response'],.65);ck('basegrowth:'+cid,data['parameters']['base_growth'],.01)
   ck('demand_identity:'+cid+str(y),r['Y'],r['desired']-r['unmet']);ck('price_identity:'+cid+str(y),r['N'],r['Y']*r['coreD']*(1+r['pressure']))
   if cid in ['BASE_SQ_UNCHANGED','UNIFORM_LEVEL_CONTROL','SNA_HOURS_FIXED_CONTROL']:
    for k in ['Y','N','coreY','coreN','coreD','labor']:ck('neutral_or_replay:'+cid+str(y)+k,r[k],prior[i][k],1e-6)
   if m['total_hours_proxy'] is not None:ck('FTE_units:'+cid+str(y),m['FTE_diagnostic']*ref,m['total_hours_proxy'],1e-4)
   bridges.append(dict(**m,engine_anchor_equivalent_L=r['labor'],L_ratio=ratio,physical_L0=c['physical_labor'][0],anchor_conversion=c['anchor_conversion'],nonlabor_A=r['nonlabor_factor'],core_real_GDP_trn=r['coreY'],final_real_GDP_trn=r['Y'],nominal_GDP_trn=r['N'],GDP_minus_current_SQ_trn=r['Y']-b['Y']))
   rec=dict(case=cid,year=y,headcount=m['headcount'],total_hours_proxy=m['total_hours_proxy'],FTE_diagnostic=m['FTE_diagnostic'],L_ratio=ratio,A=r['nonlabor_factor'],core_GDP_trn=r['coreY'],real_GDP_trn=r['Y'],GDP_minus_current_SQ_trn=r['Y']-b['Y'],initial_physical_labor_change=c['physical_labor'][0]-case_inputs['BASE_SQ_UNCHANGED']['physical_labor'][0] if m['physical_unit']=='persons' else None,initial_GDP_change=rs[0]['Y']-base[0]['Y'],provenance='NOT_ADOPTED; NO_NEW_TFP_OR_CAPITAL_SERIES; A_SAME')
   compar.append(rec)
   if y in [2026,2030,2035,2039,2055]:keyyears.append(rec)
 # Current five-factor decomposition reused unchanged, with its original scope.
 previous_attrib=read(root/D/'SQ_Labor_Decline_Attribution_And_Interactions.csv');dump(out/'Prior_SQ_Attribution_Reused_No_New_Factors.csv',[dict(**r,scope='PRIOR_SQ_ONLY;NOT_ADDED_TO_NEW_HOURS_EFFECTS') for r in previous_attrib])
 # Two-factor rate refinement and time-weight connection form a 2x2 accounting identity.
 for i,b in enumerate(base):
  count=traces['HEADCOUNT_DETAIL_2025']['years'][i];h=traces['LFS_HOURS_BASE_RATES']['years'][i];both=traces['LFS_HOURS_DETAIL_RATES']['years'][i]
  countdelta=count['Y']-b['Y'];hdelta=h['Y']-b['Y'];cross=both['Y']-count['Y']-h['Y']+b['Y']
  ck('bridge_interaction_closure:'+str(b['year']),countdelta+hdelta+cross,both['Y']-b['Y'])
  ident.append(dict(year=b['year'],employment_definition_main_delta_trn=countdelta,time_weight_main_delta_trn=hdelta,interaction_trn=cross,total_delta_trn=both['Y']-b['Y'],rate_then_time_second=both['Y']-count['Y'],time_then_rate_second=both['Y']-h['Y'],scope='2x2 ACCOUNTING NOT CAUSAL; DIFFERENT FROM PRIOR FIVE-FACTOR SHAPLEY'))
 dump(out/'SQ_Labor_Statistics_Annual_Bridge_2026_2055.csv',bridges);dump(out/'SQ_Labor_Bridge_Cases_And_GDP_Comparison.csv',compar);dump(out/'SQ_Labor_Bridge_Key_Years.csv',keyyears);dump(out/'SQ_Labor_Bridge_Interactions.csv',ident)
 # 2025 benchmark gap: identify only algebra supported by matched under65 cells.
 fc=js(root/'handoff/f-foreign-quantity-20261120/Inputs.json')['stage1_inputs']['previous_inputs'];ip=fc['age_all_five_year']['2025'];oldrates=fc['employment_rates_2025']
 def oldrate(a,sex):
  if a<15:return 0.
  ix=0 if a<25 else 1 if a<35 else 2 if a<45 else 3 if a<55 else 4 if a<60 else 5 if a<65 else 6 if a<70 else 7 if a<75 else 8
  return oldrates[sex][ix]
 old_under=old_elder=pop_component=rate_component=actual_under=0.
 for a,v in ip.items():
  for si,sex in enumerate(['male','female']):
   age=int(a);n=v[si];r=oldrate(age,sex)
   if age<15:continue
   if age<65:
    t=next(x for x in s['LFS_age_sex_population_employment'] if x['sex']==sex and x['age_lower']==age);np=t['resident_population'];emp=t['employed'];old_under+=n*r;pop_component+=(np-n)*r;rate_component+=emp-np*r;actual_under+=emp
   else:old_elder+=n*r
 oldtotal=old_under+old_elder;actualelder=next(x['employed'] for x in s['LFS_age_sex_population_employment'] if x['sex']=='both' and x['age_lower']==65);actualtotal=s['LFS2025_totals']['employed'];rounding=actualtotal-actual_under-actualelder
 ck('old2025_benchmark',oldtotal,68031652.825,1e-5);ck('2025_gap_accounting',pop_component+rate_component+actualelder-old_elder+rounding,actualtotal-oldtotal,1e-5)
 gaprows=[dict(component=k,persons=v,interpretation=t) for k,v,t in [('old_model2025',oldtotal,'IPSS2025 raw age-sex population times old rates; not same resident temporal base'),('LFS2025',actualtotal,'annual average persons employed'),('under65_population_basis_difference',pop_component,'different published population bases; timing vs population-estimation causes NOT separately identified'),('under65_rate_group_definition_difference',rate_component,'LFS fine-age E/P vs old pooled rates; not future improvement'),('elder65plus_unseparated',actualelder-old_elder,'older-age population/time/rate difference not individually identified from selected table'),('published_rounding_residual',rounding,'total minus sex/fine-age and elderly published subtotals; retained'),('total_LFS_minus_benchmark',actualtotal-oldtotal,'identity only; no national scale fitted')]]
 dump(out/'LFS_2025_Benchmark_Gap_Decomposition.csv',gaprows)
 # F same common-base connection shift. Retain all existing policy equivalent-labor additions once.
 impacts=[];fbase=js(out/'F_BASE_UNCHANGED/F_Actual_Annual.json');fprior=js(root/T/'F/F_Actual_Annual.json')
 for cid,sqcase in [('F_BASE_UNCHANGED','BASE_SQ_UNCHANGED'),('F_HEADCOUNT_DETAIL','HEADCOUNT_DETAIL_2025'),('F_HOURS_DETAIL','LFS_HOURS_DETAIL_RATES')]:
  fs=js(out/cid/'F_Actual_Annual.json');ft=js(out/cid/'F_Runtime_Trace.json')['years']
  for i,r in enumerate(fs):
   y=r['year'];matched=traces[sqcase]['years'][i];tr=ft[i];q=base[i]
   ck('F_initialY:'+cid,fs[0]['real_gdp_trn'],580);ck('F_initialN:'+cid,fs[0]['nominal_gdp_trn'],600);ck('F_risk:'+cid+str(y),tr['risk'],q['risk']);ck('F_inflation:'+cid+str(y),tr['inflation'],q['inflation'])
   if cid=='F_BASE_UNCHANGED':
    ck('F_baseY:'+str(y),r['real_gdp_trn'],fprior[i]['real_gdp_trn']);ck('F_baseN:'+str(y),r['nominal_gdp_trn'],fprior[i]['nominal_gdp_trn'])
   ck('F_labor_read:'+cid+str(y),r['labor_force_population_proxy'],tr['labor'],1e-5)
   ck('F_final_identity:'+cid+str(y),tr['Y'],tr['desired']-tr['unmet'])
   ck('F_L_single_count:'+cid+str(y),tr['labor'],tr['trajectory_effective_L']+tr['education_effective_added']+tr['health_effective_added']+tr['elder_effective_added']+inputs['F_offsets'][cid][i],1e-5)
   ck('F_education_once:'+cid+str(y),tr['education_effective_added'],r['education_effective_labor_added'],1e-5)
   ck('F_health_once:'+cid+str(y),tr['health_effective_added'],r['health_effective_labor_added'],1e-5)
   impacts.append(dict(case=cid,year=y,real_GDP_trn=r['real_gdp_trn'],matched_SQ_GDP_trn=matched['Y'],GDP_minus_matched_SQ_trn=r['real_gdp_trn']-matched['Y'],GDP_change_from_F_base_trn=r['real_gdp_trn']-fbase[i]['real_gdp_trn'],engine_effective_labor=tr['labor'],common_bridge_offset=inputs['F_offsets'][cid][i],scope='LIVE_COMMON_OFFSET_ONLY;F policy equivalent L remains once; not full age-sex hours rebuild for policy cohorts',read_dependency='fixed Diagnostic_Worker F patch: labornew=t.effective+extra_workers+common_offset',national_FTE=None,overlap='no re-add of SQ elderly baseline, foreign baseline, pension hours, education or health as separate GDP addends',status='ISOLATED_NOT_ADOPTED'))
 # Reexecute native N3 unchanged; neutral units do not require altered cached states.
 nr=js(out/'N3_BASE_UNCHANGED/N3_Actual_Annual.json');np=js(root/T/'N3/N3_Actual_Annual.json');ncheck=js(out/'N3_BASE_UNCHANGED/N3_Runtime_Checks.json');assert not ncheck['failures']
 for i,r in enumerate(nr):
  y=r['year'];ck('N3_replayY:'+str(y),r['real_GDP_trn'],np[i]['real_GDP_trn']);ck('N3_replayN:'+str(y),r['nominal_GDP_trn'],np[i]['nominal_GDP_trn']);ck('N3_GI_off:'+str(y),r['government_purchase_nominal_trn']+r['public_investment_nominal_trn'],0.)
  impacts.append(dict(case='N3_BASE_AND_NEUTRAL_UNIT_MAPPING',year=y,real_GDP_trn=r['real_GDP_trn'],matched_SQ_GDP_trn=base[i]['Y'],GDP_minus_matched_SQ_trn=r['real_GDP_trn']-base[i]['Y'],GDP_change_from_F_base_trn=None,engine_effective_labor=base[i]['labor'],common_bridge_offset=0.,scope='one native N3 live replay; neutral scale/hour ratios exactly unchanged, not a new policy simulation',read_dependency='Runner.base/sq cached traces, medical init, wage/price/tax/fiscal references',overlap='no new N3 employment or labor-GDP addend; government GI remains OFF',status='UNCHANGED_REPLAY_AND_ALGEBRAIC_NEUTRAL_COMPATIBILITY'))
  impacts.append(dict(case='N3_DETAIL_HOURS_PENDING_BASE_REBUILD',year=y,real_GDP_trn=None,matched_SQ_GDP_trn=traces['LFS_HOURS_DETAIL_RATES']['years'][i]['Y'],GDP_minus_matched_SQ_trn=None,GDP_change_from_F_base_trn=None,engine_effective_labor=None,common_bridge_offset=inputs['F_offsets']['F_HOURS_DETAIL'][i],scope='changed age/time bridge requires shared base-state reconstruction; final N3 N/A',read_dependency='Runner.base/sq; medical initialization + original clinical controls; wage/tax lagged bases',overlap='do not add SQ delta to N3 final GDP',status='NOT_EXECUTED_FINAL_N3_NO_VALID_LOCAL_OVERRIDE'))
 dump(out/'F_N3_Labor_Bridge_Impact_And_Compatibility.csv',impacts)
 # Source bytes independently pinned to correct commits.
 sources=[]
 for commit,folder in [('9dcf953e949593e773bab906eb72577f0efec73e',D),('e981c924adbe9c7ca77b96d2dc94e40378186613',T),('3611534d85fb52c976592c96120f7663dbfa63f5','handoff/claude-three-scenario-verification-20261123')]:
  paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--',folder],cwd=root,text=True).splitlines()
  for path in paths:
   z=subprocess.check_output(['git','show',commit+':'+path],cwd=root);local=root/path
   if local.exists():ck('fixed_original:'+path,0 if z==local.read_bytes() else 1,0,0)
   sources.append(dict(commit=commit,path=path,size=len(z),sha256=hashlib.sha256(z).hexdigest(),retrieval='fixed git show;local compared when materialized'))
 seen={}
 for cid in SQCASES+FCASES:
  for p in js(out/cid/'Runtime_Source_Receipts.json'):seen[p['path']]=p
 for cid in SQCASES+FCASES+['N3_BASE_UNCHANGED']:
  for rec in js(out/cid/'Bridge_Runtime_Source_Receipts.json'):seen[rec['path']]=rec
 for path,rec in sorted(seen.items()):
  z=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);ck('runtime_source:'+path,0 if hashlib.sha256(z).hexdigest()==rec['sha256'] and len(z)==rec['size'] else 1,0,0);sources.append(dict(commit=PIN,retrieval='runtime open audit; fixed git bytes verified',**rec))
 save(out/'Fixed_Source_Receipts.json',sources);dump(out/'Verification_Checks.csv',ckrows)
 summary=dict(status='PASS',new_bridge_checks=len(ckrows),new_bridge_failures=0,N3_existing_runtime_checks=ncheck['checks'],N3_existing_runtime_failures=0,checks_total=len(ckrows)+ncheck['checks'],executed_paths=10,SQ_paths=6,F_paths=3,N3_paths=1,annual_rows=300,official_originals=len(official),source_files=len(sources),python=platform.python_version(),statistics_extraction=s['extraction_dependency'],future_TFP_added=False,policy_adoption=False,prior_PASS_reuse='prior3037/Claude2845 applies only unchanged fixed originals; no independent verification of new statistical branches',keyyears=keyyears,benchmark_gap=gaprows,case2055=[r for r in compar if r['year']==2055],F_N3_2055=[r for r in impacts if r['year']==2055],interactions2055=ident[-1],SNA2024=s['SNA_history'][-1],LFS2025=s['LFS2025_totals'],originals_changed=False,RP023_M1925='HOLD',RP024='PENDING')
 save(out/'Verification.json',summary);print(json.dumps(dict(status='PASS',new_checks=len(ckrows),N3_existing_runtime_checks=ncheck['checks'],rows=300,case2055=summary['case2055'])),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.inputs.resolve(),a.out.resolve())
