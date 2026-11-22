#!/usr/bin/env python3
"""Separate native-existing and finite diagnostic G/I paths.
Shared fiscal stock residual but explicit q cash interpretations; matched 2x2
uses q_c=q_l=1. No unbounded financing, policy adoption or source modification.
"""
import argparse,csv,json,hashlib,subprocess,importlib.util,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
PIN='65227a9b86f198df62430f541fbee41e3e788b80';PREV='handoff/chatgpt-n3-policy-gi-executor-financing-mapping-20261123';AUTH='handoff/chatgpt-n3-financing-authority-feasibility-20261123';SFA='handoff/chatgpt-n3-sfa-cash-reconciliation-20261122'
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(root,out):
 out.mkdir(parents=True,exist_ok=True);sp=importlib.util.spec_from_file_location('separation_sfa',root/SFA/'N3_SFA_Reproduce.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 rec=[]
 paths=[str(p.relative_to(root)) for p in sorted((root/PREV).iterdir()) if p.is_file()]+['policies/New3linesPolicies.md',AUTH+'/Conditional_Finite_Authority_Inputs.json',SFA+'/N3_SFA_Reproduce.py','handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122/Component_Initialization.json','handoff/chatgpt-n3-policy-burden-diagnosis-20261122/N3_Unchanged_Execution_Trace.json']
 for path in paths:
  b=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);assert (root/path).read_bytes()==b;rec.append(dict(commit=PIN,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 (out/'Input_Source_Receipts.json').write_text(json.dumps(rec,indent=2)+'\n')
 authority=json.loads((root/AUTH/'Conditional_Finite_Authority_Inputs.json').read_text());caps={int(y):x for y,x in authority['annual_caps'].items()}
 class Runner(m.Runner):
  def authority_cap(self,s,y,k):return 0. if s['GI_mode']=='OFF' or (s['GI_mode']=='G_ONLY' and k=='I') else caps[y][k]
  def cash_budget(self,s,y,pb,interest,sfa,assets):
   base=super().cash_budget(s,y,pb,interest,sfa,assets)
   if s['GI_mode']=='OFF':return 0.
   if s.get('cash_neutral_only'):return base
   extra=authority['conditional_expenditure_authority_2030_trn'] if y==2030 else 0.
   return min(base+extra,max(0.,pb-interest-self.cash_part(s,y,sfa)+caps[y]['borrowing']))
 source=(root/PREV/'Resolved_Mapping_Runtime.py.txt').read_text();ns=dict(m.T.previous.__dict__);exec(compile(source,'separated_existing_runtime.py','exec'),ns);Runner.simulate=ns['simulate'];(out/'Resolved_Separation_Runtime.py.txt').write_text(source)
 runner=Runner(root,out);old=rd(root/PREV/'N3_Policy_GI_Annual_Comparison_2026_2055.csv');oldix={(x['case'],int(x['year'])):x for x in old}
 definitions=[m.spec('N3_NATIVE_EXISTING',cash_partition='SECTOR',q_central=0.,q_local=0.,GI_mode='OFF'),m.spec('N3_NATIVE_MATCHED_FINANCE',cash_partition='SECTOR',q_central=1.,q_local=1.,GI_mode='OFF'),m.spec('N3_PLUS_GI_DIAGNOSTIC',cash_partition='SECTOR',q_central=1.,q_local=1.,GI_mode='BOTH'),m.spec('N3_PLUS_GI_CASH_NEUTRAL',cash_partition='SECTOR',q_central=1.,q_local=1.,GI_mode='BOTH',cash_neutral_only=True),m.spec('N3_PLUS_G_ONLY_DIAGNOSTIC',cash_partition='SECTOR',q_central=1.,q_local=1.,GI_mode='G_ONLY')]
 raw=[];led=[];cache={};origin={};summaries=[]
 for s in definitions:
  a,l,b=runner.simulate(s);cache[s['case']]=(a,l);raw+=a;led+=l;origin[s['case']]='LIMITED_REPRODUCTION_EXECUTED' if s['case'] in ['N3_NATIVE_EXISTING','N3_PLUS_GI_DIAGNOSTIC'] else 'NEW_MATCHED_CONTROL_EXECUTED'
  prior={'N3_NATIVE_EXISTING':'NO_UNAPPROVED_ASSIGNMENT','N3_PLUS_GI_DIAGNOSTIC':'CONDITIONAL_CENTRAL_EXECUTOR'}.get(s['case'])
  if prior:
   for x in a:
    for k in ['real_GDP_trn','nominal_GDP_trn','total_tax_diagnostic_proxy_trn','CL_PB_candidate_trn','CL_debt_candidate_trn','CL_assets_candidate_trn','existing_public_payroll_delta_trn','existing_in_kind_trn']:runner.ck('limited_replay:'+s['case']+str(x['year'])+k,x[k]-float(oldix[prior,x['year']][k]),3e-6)
  for x,lx in zip(a,l):
   y=x['year'];runner.ck(s['case']+str(y)+':G_cap',max(0.,x['government_purchase_nominal_trn']-runner.authority_cap(s,y,'G')));runner.ck(s['case']+str(y)+':I_cap',max(0.,x['public_investment_nominal_trn']-runner.authority_cap(s,y,'I')))
   if s['GI_mode']=='OFF':runner.ck(s['case']+str(y)+':GI_off',x['government_purchase_nominal_trn']+x['public_investment_nominal_trn'])
   allowed_borrow=max(0.,lx['SFA_cash_need_trn']-lx['primary_balance_before_additional_spend_trn']+lx['interest_trn']) if s.get('cash_neutral_only') else caps[y]['borrowing']
   runner.ck(s['case']+str(y)+':finite_or_baseline_borrow',max(0.,lx['new_cash_borrowing_trn']-allowed_borrow),1e-6)
   runner.ck(s['case']+str(y)+':cash_bridge',lx['PB_trn']-lx['interest_trn']-lx['SFA_cash_need_trn']+lx['new_cash_borrowing_trn']-lx['cash_debt_redemption_trn']-lx['assets_end_trn']+lx['assets_begin_trn'])
 # I-only prior is exactly the ALL-YEARS G-off matched counterpart; do not rerun.
 irows=[{k:v for k,v in x.items()} for x in old if x['case']=='CONDITIONAL_LOCAL_ELIGIBLE_I'];il=[x for x in rd(root/PREV/'N3_Integrated_Cash_Debt_Ledger_2026_2055.csv') if x['case']=='CONDITIONAL_LOCAL_ELIGIBLE_I']
 def numeric(row):
  z={}
  for k,v in row.items():
   if v=='':z[k]=None
   else:
    try:z[k]=float(v)
    except (ValueError,TypeError):z[k]=v
  z['year']=int(z['year']);z['case']='N3_PLUS_I_ONLY_DIAGNOSTIC';return z
 ia=[numeric(x) for x in irows];ills=[numeric(x) for x in il];assert len(ia)==len(ills)==30
 cache['N3_PLUS_I_ONLY_DIAGNOSTIC']=(ia,ills);origin['N3_PLUS_I_ONLY_DIAGNOSTIC']='REUSED_EXACT_ALL_YEAR_I_ONLY_FIXED_RESULT';raw+=ia;led+=ills
 # Check actual external sequences shared across original N3 and SQ before labelling.
 ex=[]
 for y in range(2026,2056):
  n=runner.base[y];q=runner.sq[y]
  for k in ['coreY','coreN','coreD']:runner.ck('shared_core:'+str(y)+k,n[k]-q[k])
  runner.ck('shared_population:'+str(y),n['demography']['population']-q['demography']['population'])
  ex.append(dict(year=y,core_real_GDP_trn=n['coreY'],core_nominal_GDP_trn=n['coreN'],common_deflator=n['coreD'],population_persons=n['demography']['population'],births=n['demography']['births_calendar'],deaths=n['demography']['deaths_calendar'],energy_logistics_shock_pct=n['macro_row']['energy_logistics_shock_pct'],common_climate_anchor=n['macro_row']['common_climate_anchor'],other_shocks='EMBEDDED_UNCHANGED_PINNED_CORE_PATH; no new shock amounts',source_commit=PIN))
  # Exact SFA reclassification with no G/I must not be mistaken for G/I effect.
  n0=cache['N3_NATIVE_EXISTING'][0][y-2026];nm=cache['N3_NATIVE_MATCHED_FINANCE'][0][y-2026]
  for k in ['real_GDP_trn','total_tax_diagnostic_proxy_trn','CL_debt_candidate_trn','CL_assets_candidate_trn']:runner.ck('matched_native_macro:'+str(y)+k,nm[k]-n0[k],3e-6)
 # Standardized delivery; retain raw native/source metrics too.
 delivered=[];units=dict(GDP='TRILLION_YEN_REAL',cash_tax_debt_GI='TRILLION_YEN_NOMINAL',population='PERSONS',rates='AS_IN_FIXED_ENGINE',scope='PARTIAL_PROXY_NOT_OFFICIAL_GENERAL_GOVERNMENT')
 def enrich(x,case,lx=None,sq=False):
  y=x['year'];b=runner.sq[y] if sq else runner.base[y];mr=b['macro_row'];d=ex[y-2026];outrow=dict(x)
  outrow.update(case=case,year=y,fixed_source_commit=PIN,result_origin='REUSED_FIXED_SQ_REFERENCE' if sq else origin[case],population_persons=d['population_persons'],common_deflator=d['common_deflator'],energy_logistics_shock_pct=d['energy_logistics_shock_pct'],common_climate_anchor=d['common_climate_anchor'],total_government_final_consumption_nominal_trn='unknown',total_public_GFCF_nominal_trn='unknown',actual_bond_issuance_trn='unknown',central_debt_trn='unknown',local_debt_trn='unknown',new_payroll_added_to_G_trn=0.,new_in_kind_added_to_G_trn=0.,intergovernment_transfer_trn=0.,actual_2030_funding_authority='unknown')
  if lx:outrow.update(cash_assets_begin_trn=lx['assets_begin_trn'],cash_assets_end_trn=lx['assets_end_trn'],SFA_total_residual_trn=lx['SFA_trn'],SFA_assumed_cash_use_trn=lx['SFA_cash_need_trn'],cash_new_borrowing_candidate_trn=lx['new_cash_borrowing_trn'],cash_redemption_candidate_trn=lx['cash_debt_redemption_trn'],additional_G_nominal_trn=x['government_purchase_nominal_trn'],additional_public_I_nominal_trn=x['public_investment_nominal_trn'],unfinanced_existing_need_trn=max(0.,lx['new_cash_borrowing_trn']-(caps[y]['borrowing'] if case!='N3_PLUS_GI_CASH_NEUTRAL' else max(0.,lx['SFA_cash_need_trn']-lx['primary_balance_before_additional_spend_trn']+lx['interest_trn']))),actual_usable_cash_trn='unknown',SQ_fiscal_attachment_status='NOT_PART_OF_FIXED_MACRO_SQ_REFERENCE')
  return outrow
 for case,(a,l) in cache.items():
  for x,lx in zip(a,l):delivered.append(enrich(x,case,lx))
 sqrows=[]
 for y,b in runner.sq.items():
  mr=b['macro_row'];z=dict(case='SQ_REFERENCE',year=y,real_GDP_trn=b['Y'],nominal_GDP_trn=b['N'],GDP_minus_SQ_trn=0.,SQ_real_GDP_trn=b['Y'],consumption_real_trn=mr['household_consumption_real_proxy_trn'],private_investment_real_trn=mr['capital_replacement_investment_real_trn']+b['I'],household_resource_DI_proxy_trn=mr['household_disposable_nominal_trn'],household_policy_cash_nominal_trn=mr['household_policy_cash_nominal_trn'],total_tax_diagnostic_proxy_trn=b['tax']+b['direct'],macro_tax_proxy_trn=b['tax'],CL_PB_candidate_trn='unknown',CL_interest_candidate_trn='unknown',CL_debt_candidate_trn='unknown',CL_assets_candidate_trn='unknown',cash_new_borrowing_candidate_trn='unknown',cash_assets_begin_trn='unknown',cash_assets_end_trn='unknown',cash_redemption_candidate_trn='unknown',SFA_assumed_cash_use_trn='unknown',additional_G_nominal_trn=0.,additional_public_I_nominal_trn=0.,government_purchase_nominal_trn=0.,public_investment_nominal_trn=0.,existing_public_payroll_delta_trn=0.,existing_in_kind_trn=mr['in_kind_trn'],policy_tax_delta_trn=0.,actual_usable_cash_trn='unknown',SQ_fiscal_attachment_status='FIXED_MACRO_SQ_NO_NATIONAL_FISCAL_CLOSURE_SERIES')
  sqrows.append(enrich(z,'SQ_REFERENCE',sq=True))
 delivered+=sqrows
 # Differences and exact telescope, path-dependent matched factorial terms.
 metrics=['real_GDP_trn','nominal_GDP_trn','total_tax_diagnostic_proxy_trn','CL_PB_candidate_trn','CL_interest_candidate_trn','CL_debt_candidate_trn','CL_assets_candidate_trn','government_purchase_nominal_trn','public_investment_nominal_trn','private_investment_real_trn','household_resource_DI_proxy_trn','consumption_real_trn']
 index={(x['case'],x['year']):x for x in delivered};attribution=[]
 for y in range(2026,2056):
  N=index['N3_NATIVE_EXISTING',y];M=index['N3_NATIVE_MATCHED_FINANCE',y];D=index['N3_PLUS_GI_DIAGNOSTIC',y];C=index['N3_PLUS_GI_CASH_NEUTRAL',y];G=index['N3_PLUS_G_ONLY_DIAGNOSTIC',y];I=index['N3_PLUS_I_ONLY_DIAGNOSTIC',y];Q=index['SQ_REFERENCE',y]
  for k in metrics:
   val=lambda x:x[k] if isinstance(x.get(k),(int,float)) else None
   n,mm,d,c,g,i,q=map(val,[N,M,D,C,G,I,Q]);assert None not in [n,mm,d,c,g,i],(y,k)
   row=dict(year=y,metric=k,unit='REAL_TRILLION_YEN' if k in ['real_GDP_trn','private_investment_real_trn','consumption_real_trn'] else 'NOMINAL_TRILLION_YEN',native_minus_SQ='unknown' if q is None else n-q,diagnostic_minus_SQ='unknown' if q is None else d-q,diagnostic_minus_native=d-n,raw_difference_class='G_I_PLUS_DIFFERENT_CASH_CLASSIFICATION_AND_AUTHORITY',matched_GI_increment=d-mm,native_financing_classification_effect=mm-n,G_only_increment=g-mm,I_only_increment=i-mm,GI_dynamic_interaction=d-g-i+mm,GI_under_cash_neutral_increment=c-mm,finite_financing_authority_increment=d-c,decomposition_status='MATCHED_PATH_DIFFERENCES_NOT_CAUSAL_CALIBRATION',SQ_fiscal_difference_status='unknown' if q is None else 'AVAILABLE_FIXED_SQ_METRIC')
   runner.ck('telescope_match:'+str(y)+k,(d-n)-(d-mm)-(mm-n))
   runner.ck('factorial:'+str(y)+k,(d-mm)-(g-mm)-(i-mm)-(d-g-i+mm))
   runner.ck('funding_split:'+str(y)+k,(d-mm)-(c-mm)-(d-c))
   if q is not None:runner.ck('SQ_telescope:'+str(y)+k,(d-q)-(n-q)-(d-n))
   attribution.append(row)
 # Summaries do not label every native implementation fully compliant.
 for case in [*cache,'SQ_REFERENCE']:
  a=[x for x in delivered if x['case']==case];below=[x for x in a if x['GDP_minus_SQ_trn'] < -1e-7];worst=min(a,key=lambda x:x['GDP_minus_SQ_trn']);z30=next(x for x in a if x['year']==2030);end=a[-1]
  summaries.append(dict(case=case,rows=len(a),result_origin=a[0]['result_origin'],gap2030_trn=z30['GDP_minus_SQ_trn'],gap2055_trn=end['GDP_minus_SQ_trn'],SQ_below_years=len(below),worst_year=worst['year'],worst_gap_trn=worst['GDP_minus_SQ_trn'],cumulative_GDP_gap_trn_years=sum(x['GDP_minus_SQ_trn'] for x in a),G2030_trn=z30['government_purchase_nominal_trn'],I2030_trn=z30['public_investment_nominal_trn'],debt2055_trn=end['CL_debt_candidate_trn'],cash_assets2055_trn=end['CL_assets_candidate_trn'],cash_borrow2030_trn=z30['cash_new_borrowing_candidate_trn'],native_policy_full_implementation=False,real_world_SQ_feasibility=False))
 contract=dict(fixed_source_commit=PIN,period=[2026,2055],SQ='EXACT_FIXED_SQ_COMMON_ON_MACRO_SERIES',native_existing_equivalent='NO_UNAPPROVED_ASSIGNMENT',diagnostic_equivalent='CONDITIONAL_CENTRAL_EXECUTOR',shared_parameters=runner.par,shared_component_spec=runner.ci['s'],shared_finance_specs={k:definitions[0][k] for k in ['tail','interest_mode','rate','rollover','sfa_tail','backfill','ss_growth','kpi','firm_rate','g_share','pi_share','domestic','yield_public']},SFA_cash_mapping_note='native q_c=q_l=0; matched factorial q_c=q_l=1; underlying residual series unchanged',finite_GI_authority_inputs=authority,I_only_reuse=dict(commit=PIN,case='CONDITIONAL_LOCAL_ELIGIBLE_I',exact_all_years_G_off=True),native_private_investment75_note='Shared retained preexisting diagnostic assumption; native-existing is not a fully text-derived implementation',SQ_fiscal_fields='unknown in fixed macro reference; do not synthesize national balances',units=units,formal_policy_adopted=False)
 (out/'Comparison_Contract_And_Inputs.json').write_text(json.dumps(contract,indent=2)+'\n');dump(out/'N3_Native_vs_Diagnostic_Annual_Comparison_2026_2055.csv',delivered);dump(out/'N3_Native_vs_Diagnostic_Case_Summary.csv',summaries);dump(out/'N3_Diagnostic_Increment_And_Funding_Attribution.csv',attribution);dump(out/'N3_Fiscal_Cash_Debt_Ledger_2026_2055.csv',led);dump(out/'Shared_Exogenous_Inputs_2026_2055.csv',ex);dump(out/'Executed_Case_Definitions.csv',definitions);dump(out/'Detail_2029_2032_2055.csv',[x for x in delivered if 2029<=x['year']<=2032 or x['year']==2055])
 result=dict(status='PASS_SEPARATED_COMPARISON_AND_ATTRIBUTION' if not runner.checks else 'FAIL',executed_paths=5,executed_annual_rows=150,new_matched_counterfactual_paths=3,new_matched_annual_rows=90,limited_reproduction_paths=2,limited_reproduction_rows=60,reused_I_only_rows=30,reused_SQ_rows=30,delivered_paths=7,delivered_rows=len(delivered),checks=runner.counter,failed=len(runner.checks),failures=runner.checks,prior_checks_reused=[3580,3190,6972],prior_macro_neutrality_comparisons_reused=120,SQ_definition_changed=False,common_engine_changed=False,policy_adopted=False,full_native_implementation=False,real_world_2030_funding='unknown')
 (out/'Verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));print(json.dumps(summaries));assert not runner.checks,runner.checks[:5]
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--outdir',type=Path,required=True);z=a.parse_args();run(z.root.resolve(),z.outdir.resolve())
