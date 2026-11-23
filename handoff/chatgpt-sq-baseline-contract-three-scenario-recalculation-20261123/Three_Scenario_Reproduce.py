"""Pinned three-scenario execution and narrowly scoped input-connection tests.
Stdlib only. Run: python <this-file> --root <fixed-checkout> --outdir <empty-output>
"""
import argparse,csv,hashlib,json,math,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
PIN='9448e5921dba0fc0ff4e294e52b6b1f3ba862330'
PREV='handoff/chatgpt-statusquo-common-macro-limited-diagnostic-20261123'
F='handoff/f-common-endoflife-finalization-20261121'
HERE=Path(__file__).resolve().parent
MODES=['BASE_REPLAY','KEYS_DEFAULT','KEY_BASE_NONDEFAULT','KEY_CONFLICT_NONDEFAULT','LEGACY_BASE_NONDEFAULT','LEGACY_CONFLICT_NONDEFAULT','F_OLD','F','N3']
def js(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def read(p):return list(csv.DictReader(p.open()))
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(root,out):
 out.mkdir(parents=True,exist_ok=True);logs=[]
 for mode in MODES:
  cmd=[sys.executable,str(HERE/'Three_Scenario_Worker.py'),'--root',str(root),'--outdir',str(out/mode),'--case',mode]
  z=subprocess.run(cmd,capture_output=True,text=True);logs.append(dict(case=mode,command=['python3','Three_Scenario_Worker.py','--root','<fixed-checkout>','--outdir','<out>/'+mode,'--case',mode],exit_code=z.returncode,stdout=z.stdout,stderr=z.stderr));save(out/'Execution_Log.json',logs)
  if z.returncode:raise RuntimeError(z.stderr)
  print(mode,z.stdout.strip(),flush=True)
 sq=js(out/'BASE_REPLAY/Common_Trace_BASE_REPLAY.json');q=sq['years'];p=sq['parameters'];f=js(out/'F/F_Actual_Annual.json');fo=js(out/'F_OLD/F_Actual_Annual.json');ft=js(out/'F/F_Runtime_Trace.json');n=js(out/'N3/N3_Actual_Annual.json');nsq=js(out/'N3/N3_SQ_Denominator_States.json');nc=js(out/'N3/N3_Common_Input_Contract.json');fc=js(root/F/'Inputs.json');fmref=js(out/'F/F_Medical_Reference_Inputs.json');ncheck=js(out/'N3/N3_Runtime_Checks.json')
 checks=ncheck['checks'];failures=list(ncheck['failures'])
 def ck(name,error,tol=2e-6):
  nonlocal checks
  checks+=1
  if not isinstance(error,(int,float)) or not math.isfinite(error) or abs(error)>tol:failures.append(dict(check=name,error=error,tolerance=tol))
 oldsq=js(root/PREV/'Common_Trace_BASE_REPLAY.json')['years'];oldf={int(x['year']):x for x in read(root/F/'Annual.csv') if x['case']=='LATEST_F'};oldn={int(x['year']):x for x in read(root/'handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/N3_GDP_Gap_Counterfactual_Annual_2026_2055.csv') if x['case']=='BASE_REPLAY'} if (root/'handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/N3_GDP_Gap_Counterfactual_Annual_2026_2055.csv').exists() else {}
 compat=[]
 for key in ['common_parameters','common_financing','clinical_strata','registry_population_reference']:
  match=fc[key]==nc['medical_input']['c'][key];ck('common_definition:'+key,0 if match else 1);compat.append(dict(condition=key,SQ_F_N3_status='SAME_SHARED_DEFINITION',verified=match,limitation='Uncalibrated common clinical assumptions retained; policy-specific copay and payer rules remain distinct'))
 for key in ['deflators','population']:
  match=fmref[key]==nc['medical_input'][key];ck('common_medical_reference:'+key,0 if match else 1);compat.append(dict(condition='medical_reference_'+key,SQ_F_N3_status='F_RECONNECTED_TO_EXISTING_SQ_N3_REFERENCE',verified=match,limitation='Policy-driven actual trajectory and lagged price feedback remain distinct'))
 for key in ['base_inflation','oil_inflation_extra','conflict_inflation_extra','apply_oil_to_initial','disaster_anchor','climate_anchor','base_growth','labor_response']:
  ck('common_parameter_F:'+key,float(ft['parameters'][key])-float(p[key]));ck('common_parameter_N3:'+key,float(nc['parameters'][key])-float(p[key]))
  compat.append(dict(condition=key,SQ_F_N3_status='SAME_COMMON_INPUT',verified=True,limitation='F policy labor additions may alter realized growth and implicit deflator'))
 trace=[];annual=[];changes=[];attribution=[];case_defs=[]
 for i,y in enumerate(range(2026,2056)):
  s=q[i];t=ft['years'][i];nr=n[i];dr=s['coreD'];sqn=nsq[i]
  for k in ['Y','N','coreY','coreN','coreD','labor','C','I','K','tax']:
   ck('SQ_prior:'+str(y)+k,s[k]-oldsq[i][k]);ck('N3_same_SQ_denominator:'+str(y)+k,s[k]-sqn[k])
  for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn']:
   ck('F_old_replay:'+str(y)+k,fo[i][k]-float(oldf[y][k]),3e-6)
  if oldn:
   for k in ['real_GDP_trn','nominal_GDP_trn','total_tax_diagnostic_proxy_trn']:ck('N3_prior:'+str(y)+k,nr[k]-float(oldn[y][k]),3e-6)
  for k in ['coreY','coreN','coreD','labor']:ck('N3_SQ_core:'+str(y)+k,sqn[k]-s[k])
  ck('F_GDP_capacity_identity:'+str(y),t['Y']-t['desired']+t['unmet'])
  ck('N3_GDP_decomposition:'+str(y),nr['GDP_minus_SQ_trn']-sum(nr[k] for k in ['GDP_core_difference_trn','GDP_C_difference_trn','GDP_I_difference_trn','GDP_G_domestic_trn','GDP_supply_difference_trn','GDP_other_difference_trn','GDP_unmet_difference_trn']))
  ck('N3_GI_off:'+str(y),nr['government_purchase_nominal_trn']+nr['public_investment_nominal_trn'])
  ck('SQ_N_formula:'+str(y),s['N']-s['Y']*dr*(1+s['pressure']))
  ck('F_N_formula:'+str(y),t['N']-t['Y']*t['coreD']*(1+t['pressure']))
  ck('N3_N_formula:'+str(y),nr['nominal_GDP_trn']-nr['real_GDP_trn']*dr*(1+p['price_pressure_coefficient']*nr['unmet_demand_real_trn']/s['coreY']))
  if i:
   prev=q[i-1];ck('SQ_additive_nominal:'+str(y),s['coreN']-prev['coreN']*(1+s['growth']+s['inflation']));ck('SQ_price_rate:'+str(y),dr/prev['coreD']-1-s['inflation']/(1+s['growth']))
  events=dict(oil=p['oil_gdp_loss'] if y==2026 else 0.,conflict=p['conflict_gdp_loss'] if y==2027 else 0.,quake=p['quake_gdp_loss'] if y==2031 else 0.,disaster=p['disaster_gdp_loss'] if y>=p['disaster_anchor'] and (y-p['disaster_anchor'])%3==0 else 0.,climate=p['climate_gdp_loss'] if y>=p['climate_anchor'] and (y-p['climate_anchor'])%2==0 else 0.)
  applied=sum(v for k,v in events.items() if k!='oil');ck('SQ_risk_once:'+str(y),s['risk']-applied);ck('F_same_event:'+str(y),t['risk']-s['risk']);ck('F_same_pi:'+str(y),t['inflation']-s['inflation'])
  trace.append(dict(year=y,base_inflation_input=p['base_inflation'],conflict_price_input=p['conflict_inflation_extra'],conflict_real_loss_input=p['conflict_gdp_loss'],input_inflation=s['inflation'],implicit_core_deflator_growth=None if not i else dr/q[i-1]['coreD']-1,implementation_index=dr,nominal_rule='ADDITIVE_CURRENT_REFERENCE_UNCHANGED',initial_transition=False if not i else True,scheduled_events=json.dumps(events),applied_risk=s['risk'],oil_scheduled=y==2026,oil_applied=False,applied_distinct_events=';'.join(k for k,v in events.items() if v and k!='oil'),permanent_state=True,recovery_rule='UNKNOWN_NOT_ADDED',F_input_inflation=t['inflation'],F_implementation_index=t['coreD'],N3_implementation_index=dr))
  variants=[dict(case='SQ',Y=s['Y'],N=s['N'],d=dr,pop=s['population'],labor=s['labor'],C=s['household_consumption_real_proxy'],I=sqn['macro_row']['capital_replacement_investment_real_trn']+s['I'],K=s['total_capital_real_proxy'],tax=s['tax']+s['direct'],hh=sqn['macro_row']['household_disposable_nominal_trn'],PB=None,debt=None,fund=None,pressure=s['pressure']),dict(case='F',Y=f[i]['real_gdp_trn'],N=f[i]['nominal_gdp_trn'],d=t['coreD'],pop=f[i]['population'],labor=f[i]['labor_force_population_proxy'],C=f[i]['household_consumption_real_proxy_trn'],I=f[i]['I_policy_real_trn'],K=f[i]['capital_total_real_trn'],tax=f[i]['tax_diagnostic_trn'],hh=f[i]['macro_cash_DI_proxy_trn'],PB=None,debt=None,fund=f[i].get('fund_balance_trn'),pressure=t['pressure']),dict(case='N3',Y=nr['real_GDP_trn'],N=nr['nominal_GDP_trn'],d=dr,pop=s['population'],labor=s['labor'],C=nr['consumption_real_trn'],I=nr['private_investment_real_trn'],K=nr['capital_total_real_proxy_trn'],tax=nr['total_tax_diagnostic_proxy_trn'],hh=nr['household_resource_DI_proxy_trn'],PB=nr['CL_PB_candidate_trn'],debt=nr['CL_debt_candidate_trn'],fund=nr['pension_fund_end_trn'],pressure=p['price_pressure_coefficient']*nr['unmet_demand_real_trn']/s['coreY'])]
  for v in variants:
   prev=next((x for x in annual if x['case']==v['case'] and x['year']==y-1),None)
   annual.append(dict(case=v['case'],year=y,SQ_reference='CURRENT_REFERENCE_UNCHANGED_COMMON_ON',real_GDP_trn=v['Y'],nominal_GDP_trn=v['N'],implementation_price_index=v['d'],implicit_deflator=v['N']/v['Y'],implicit_deflator_normalized=(v['N']/v['Y'])/(600/580),real_growth_pct=0. if not prev else (v['Y']/prev['real_GDP_trn']-1)*100,price_pressure=v['pressure'],population=v['pop'],effective_labor_proxy=v['labor'],consumption_real_proxy_trn=v['C'],investment_real_proxy_trn=v['I'],capital_real_proxy_trn=v['K'],tax_diagnostic_proxy_trn=v['tax'],household_resource_proxy_trn=v['hh'],PB_conditional_trn=v['PB'],debt_conditional_trn=v['debt'],fund_stock_scope_specific_trn=v['fund'],GDP_minus_SQ_trn=v['Y']-s['Y'],nominal_GDP_minus_SQ_trn=v['N']-s['N'],GDP_minus_2026_580_trn=v['Y']-580.,cross_scenario_national_fiscal_rank='N/A',investment_comparability='N/A_F_policy_state_vs_SQ_N3_replacement_inclusive',household_comparability='N/A_DI_definitions_differ',fund_comparability='N/A_different_fund_scope',policy_status='EXISTING_IMPLEMENTED_UNCALIBRATED_NOT_ADOPTED_FORECAST'))
   if i==0:ck('initial_Y:'+v['case'],v['Y']-580);ck('initial_N:'+v['case'],v['N']-600)
  attribution.append(dict(year=y,SQ_common_macro_change_real=0.,N3_common_macro_change_real=0.,N3_policy_gap=nr['real_GDP_trn']-s['Y'],F_old_own_SQ_FIXED_denominator=float(next(x for x in read(root/'handoff/f-education-20261121/Annual.csv') if x['case']=='SQ_FIXED' and int(x['year'])==y)['real_gdp_trn']),F_new_shared_SQ=s['Y'],F_shared_medical_reference_reconnection=f[i]['real_gdp_trn']-fo[i]['real_gdp_trn'],F_old_policy_level=fo[i]['real_gdp_trn'],F_new_policy_level=f[i]['real_gdp_trn'],F_policy_gap_on_shared_reference=f[i]['real_gdp_trn']-s['Y'],interpretation='Sequential accounting telescope; not independent causal channel effects'))
 for mode in MODES[:6]:
  rs=js(out/mode/('Common_Trace_'+mode+'.json'))['years']
  for i,r in enumerate(rs):
   for key in ['Y','N','coreY','coreN','coreD','inflation']:
    if mode in ['KEYS_DEFAULT','LEGACY_BASE_NONDEFAULT','LEGACY_CONFLICT_NONDEFAULT']:ck(mode+str(r['year'])+key,r[key]-q[i][key])
   if mode.startswith('KEY_'):
    expect=.03+(.05 if r['year']==2027 else 0.) if mode=='KEY_BASE_NONDEFAULT' else .02+(.01 if r['year']==2027 else 0.)
    ck(mode+str(r['year'])+'price_key_active',r['inflation']-expect);ck(mode+str(r['year'])+'real_risk_independent',r['risk']-q[i]['risk']);ck(mode+str(r['year'])+'real_core_independent',r['coreY']-q[i]['coreY'])
   changes.append(dict(case=mode,year=r['year'],real_GDP_trn=r['Y'],nominal_GDP_trn=r['N'],real_GDP_minus_reference=r['Y']-q[i]['Y'],nominal_GDP_minus_reference=r['N']-q[i]['N'],input_inflation=r['inflation'],risk=r['risk'],status='NOT_ADOPTED_MECHANICAL_INPUT_TEST' if mode not in ['BASE_REPLAY','KEYS_DEFAULT'] else 'REFERENCE_REPLAY' if mode=='BASE_REPLAY' else 'ISOLATED_KEY_CONNECTION_CANDIDATE_DEFAULT_NEUTRAL',price_medical_scope='CACHED_MEDICAL_INPUTS_RETAINED_NO_FULL_PRICE_REINITIALIZATION'))
 keyyears=[]
 for cid in ['SQ','F','N3']:
  rr=[x for x in annual if x['case']==cid];below=sum(x['GDP_minus_SQ_trn']< -1e-7 for x in rr)
  for x in rr:
   if x['year'] in [2026,2030,2035,2039,2055]:keyyears.append(dict(**x,SQ_below_years=below,below_initial_580_years=sum(t['real_GDP_trn']<580-1e-7 for t in rr)))
 # Validate source receipts against actual fixed commit, not a previous AI claim.
 receipts={}
 for mode in MODES:
  for x in js(out/mode/('Source_Receipts_'+mode+'.json')):receipts[x['path']]=x
 for path,x in sorted(receipts.items()):
  raw=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);ck('source_size:'+path,len(raw)-x['size']);ck('source_sha:'+path,0 if hashlib.sha256(raw).hexdigest()==x['sha256'] else 1)
 for path in ['policies/StatusQuo.md','handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/N3_GDP_Gap_Counterfactual_Annual_2026_2055.csv']:
  raw=(root/path).read_bytes();fixedraw=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);ck('additional_source:'+path,0 if raw==fixedraw else 1);receipts[path]=dict(path=path,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
 save(out/'Fixed_Source_Receipts.json',dict(commit=PIN,files=list(receipts.values()),route='runtime read audit; fixed Git object retrieval; actual bytes SHA256'))
 compatibility_extra=[dict(condition='realized_deflator_and_population',SQ_F_N3_status='POLICY_ENDOGENOUS_DIFFERENCES_ALLOWED',verified=True,limitation='Same initial anchors/input inflation/events; F policy labor/foreign/education effects alter actual population and implicit deflator. N3 retains unchanged common labor core.'),dict(condition='common_medical_interface',SQ_F_N3_status='SAME_IMPLEMENTATION_SAME_PARAMETER_BASE',verified=True,limitation='Patient charges follow each existing policy; financing and VAT/health scope gaps not solved.'),dict(condition='GDP_comparison',SQ_F_N3_status='CONDITIONAL_IMPLEMENTED_MODEL_COMPARISON',verified=True,limitation='Not complete original-policy forecast or fully nationally calibrated ranking'),dict(condition='national_fiscal_household_investment_fund',SQ_F_N3_status='N/A_NONMATCHED_ACCOUNTING_SCOPE',verified=True,limitation='Partial proxies and N3 conditional fiscal closure exported; no forced national ranking')]
 dump(out/'F_N3_SQ_Common_Condition_Compatibility.csv',compat+compatibility_extra)
 dump(out/'SPE_Three_Scenario_Annual_Comparison_2026_2055.csv',annual);dump(out/'SPE_Three_Scenario_Key_Years_And_Gaps.csv',keyyears);dump(out/'SPE_Three_Scenario_Change_Attribution.csv',attribution);dump(out/'SQ_Price_Event_Parameter_Trace.csv',trace);dump(out/'SQ_Baseline_2026_2055.csv',[x for x in annual if x['case']=='SQ']);dump(out/'SQ_Change_Candidates_And_Impact.csv',changes)
 prov=read(root/PREV/'SQ_Baseline_Variant_Provenance_And_Comparability.csv');dump(out/'SQ_Common_Macro_Contract_And_Variant_Provenance.csv',prov+[dict(family='CURRENT_COMPARISON',case='SQ_COMPARISON_REFERENCE',commit=PIN,initial_year=2026,transitions=29,price_rule='ADDITIVE_CURRENT_REFERENCE_UNCHANGED',common_policy='ON',recovery='UNKNOWN',canonical=False)])
 for mode in MODES:case_defs.append(dict(case=mode,years=[2026,2055],rows=30,purpose='UNCHANGED_COMMON_REFERENCE' if mode=='BASE_REPLAY' else 'MAIN_F_COMMON_MEDICAL_REFERENCE_ALIGNED' if mode=='F' else 'NATIVE_N3_GI_OFF_UNCHANGED' if mode=='N3' else 'OLD_F_REEXECUTION_CONTROL' if mode=='F_OLD' else 'UNADOPTED_INPUT_CONNECTION_DIAGNOSTIC',mechanical_override={'base_inflation':.03} if 'BASE_NONDEFAULT' in mode else {'conflict_inflation_extra':.01} if 'CONFLICT_NONDEFAULT' in mode else {},originals_changed=False))
 save(out/'SPE_Three_Scenario_Case_Definitions.json',dict(fixed_input_commit=PIN,SQ_COMPARISON_REFERENCE='CURRENT_REFERENCE_UNCHANGED',cases=case_defs,shared_initial_real=580,shared_initial_nominal=600,main_comparison='SQ + aligned existing F + unchanged native existing N3',candidate_in_main=False,extra_GI='OFF',policy_adoption=False,initial_oil=False,nominal_price_rule='CURRENT_ADDITIVE',recovery_added=False))
 save(out/'Verification.json',dict(status='PASS' if not failures else 'FAIL',checks=checks,failed=len(failures),failures=failures,executed_paths=9,executed_annual_rows=270,main_comparison_paths=3,main_annual_rows=90,source_files=len(receipts),previous_PASS_reused=[2199,13928,8058,15590],formal_adoption=False,full_policy_calibration=False,originals_changed=False))
 assert not failures,failures[:4]
 print(json.dumps(dict(status='PASS',checks=checks,rows=270,key2055=[{k:x[k] for k in ['case','real_GDP_trn','nominal_GDP_trn','GDP_minus_SQ_trn']} for x in keyyears if x['year']==2055])),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.outdir.resolve())
