#!/usr/bin/env python3
"""Narrow medical replacement in the pinned education/integration GDP engine."""
import argparse,copy,csv,hashlib,importlib.util,json,math,sys
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from FMedical import Medical
from CommonEndOfLife import calculate,close
def read(p):return list(csv.DictReader(p.open()))
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader()
  for r in rows:w.writerow({k:format(v,'.12g') if isinstance(v,float) else v for k,v in r.items()})
def load(c):
 root=P.parents[1]
 for x in c['runtime_dependencies']:
  b=(root/x['path']).read_bytes();assert len(b)==x['size'] and hashlib.sha256(b).hexdigest()==x['sha256'],x['path']
 file=root/'handoff/f-education-20261121/Model.py';spec=importlib.util.spec_from_file_location('fixed_education',file);edu=importlib.util.module_from_spec(spec)
 source=file.read_text();needle="exec(compile(source,'education_integrated_macro.py','exec'),ns);return ns";assert source.count(needle)==1
 source=source.replace(needle,"exec(compile(source,'education_integrated_macro.py','exec'),ns);ns['_medical_source']=source;return ns")
 exec(compile(source,str(file),'exec'),edu.__dict__)
 ec=json.loads((file.parent/'Inputs.json').read_text());_,integ,v,vc=edu.load(ec)
 return root,edu,ec,integ,v,vc
def patch(engine,pol,med,s):
 if pol!='F' or s['keep_legacy']:return engine
 source=engine['_medical_source'];ns=dict(engine['run_path'].__globals__);ns['_medical']=med
 def sub(a,b):
  nonlocal source
  assert source.count(a)==1,a;source=source.replace(a,b)
 # Remove the complete old clinical/hub accounting before adding new flows.
 sub("med=medical_reform(p,y,'medical' in omit or halt or not i,'hubs' in omit,previous_hubs)","med=medical_reform(p,y,True,True,previous_hubs)")
 sub("t['effective_productive_workers']+=z['education_effective_labor_added']", "t['effective_productive_workers']+=z['education_effective_labor_added']\n        w=_medical.step(y)\n        t['effective_productive_workers']+=w['health_effective_labor_added']")
 sub("+z['education_facility_domestic_nominal_trn']", "+z['education_facility_domestic_nominal_trn']+w['investment_nominal_delta_trn']")
 sub("cash+=z['scholarship_grant_trn']", "cash+=z['scholarship_grant_trn']+w['household_cash_delta_trn']")
 sub("desired=coreY+p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+z['education_service_domestic_nominal_trn']/coreD", "desired=coreY+p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+(z['education_service_domestic_nominal_trn']+w['service_production_nominal_delta_trn'])/coreD")
 sub("p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+z['education_service_domestic_nominal_trn']/coreD-unmet)","p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+(z['education_service_domestic_nominal_trn']+w['service_production_nominal_delta_trn'])/coreD-unmet)")
 sub("expenditure+=z['net_additional_education_spend_trn']+z['bond_interest_trn']", "expenditure+=z['net_additional_education_spend_trn']+z['bond_interest_trn']+w['government_cost_delta_trn']")
 sub("        direct-=z['training_credit_trn'];", "        direct+=w['medical_financing_direct_tax_trn'];direct-=z['training_credit_trn'];")
 sub("firm=firm_policy(p,y,coreN,a['nominal_gdp'],omit,halt or not i)", "firm=firm_policy(p,y,coreN,a['nominal_gdp'],omit,halt or not i or _medical.s.get('omit_firm',False))")
 if s.get('omit_investment'):sub("invflow=None if p['investment_flow_share'] is None else p['investment_flow_share']*coreN*phase(y,p['investment_start']) if i and not halt else 0.", "invflow=0.")
 exec(compile(source,'medical_education_integrated.py','exec'),ns);return ns

def vat_hook(v,md,s):
 saved=v.sector_account
 def account(c,vs,a,y,std):
  before=saved(c,vs,a,y,std)
  if a['id']!='medical' or not s['vat_response'] or not md.rows or y!=md.rows[-1]['year'] or y==2026:return before
  amount=md.rows[-1]['medical_VAT_scope_flow_delta_trn']
  base=before['market_turnover_reference_trn'];factor=max(.05,1+amount/max(base,1e-9))
  after=saved(c,vs,{**a,'R2025':a['R2025']*factor},y,std)
  after.update(medical_flow_volume_factor=factor,medical_nominal_flow_delta_trn=amount,old_medical_turnover_trn=base,medical_chain_VAT_response_trn=after['modeled_chain_VAT_trn']-before['modeled_chain_VAT_trn'])
  return after
 v.sector_account=account
 return saved

def run(inp,out):
 c=json.loads(Path(inp).read_text());root,edu,ec,integ,v,vc=load(c);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 oldfile=root/'handoff/f-medical-common-20261121/Annual.csv';oldall=read(oldfile);old={(r['case'],int(r['year'])):r for r in oldall}
 er=read(root/'handoff/f-education-20261121/Annual.csv');edref={int(r['year']):r for r in er if r['case']=='COMBINED'}
 ir=read(root/'handoff/f-integrated-20261121/Annual.csv');ir={int(r['year']):r for r in ir if r['case']=='FULL_ADDITIONAL'}
 deflators=[float(ir[y]['common_deflator']) for y in range(2026,2056)];population=[float(ir[y]['population']) for y in range(2026,2056)]
 eduspec=next(x for x in ec['cases'] if x['id']=='COMBINED')
 paths={};medical=[];common=[];demography=[];education=[];fiscal=[];vat=[];labor=[];hh=[];claims=[];regression=0
 for index,sp in enumerate(c['cases']):
  s={**c['defaults'],**sp};ed=edu.Education(ec,{**eduspec,'E':s['edu_E'],'S':s['edu_S'],'T':s['edu_T']},deflators);md=Medical(c,s,deflators,population)
  # Capture the actually selected population/elder trajectory for every ablation.
  original_base=integ.make_base
  def base(*args,**kw):
   result=original_base(*args,**kw);md.trajectory=result[3]['d'];md.elder=result[3]['elder'];return result
  integ.make_base=base
  integ._education_hook=lambda engine,pol:patch(edu.patched_engine(engine,pol,ed,'REPLACE'),pol,md,s)
  saved_sector=vat_hook(v,md,s)
  vs={k:s[k] for k in ['id','C','C_mode']}
  vs.update({k:sp[k] for k in ['E','F','PEN','A','B','VAT'] if k in sp})
  try:rows,inc,sectors,b,raw,cc=integ.execute(v,vc,vs)
  finally:integ.make_base=original_base;v.sector_account=saved_sector
  for i,(r,m) in enumerate(zip(rows,raw)):
   w=md.rows[i];co=md.common[i];z=ed.rows[i];fi=integ.fiscal(r,m,b,i,cc)
   fi['insurer_known_change_and_program_balance_trn']+=w['insurer_balance_delta_trn'];fi['consolidated_partial_balance_proxy_trn']+=w['insurer_balance_delta_trn']
   close(fi['government_partial_balance_proxy_trn']+fi['insurer_known_change_and_program_balance_trn'],fi['consolidated_partial_balance_proxy_trn'])
   r.update(fi);r.update(z);r.update(w);r.update(case=s['id'],scope='IMPLEMENTED_F_CHANNELS_PLUS_EXPLICIT_UNCALIBRATED_SENSITIVITIES',medical_demand_mode=s['demand_mode'],medical_payer_mode=s['payer_mode'],universal_palliative=s['universal_palliative'],common_policy=s['common'],F_medical_copay=s['copay'],F_medical_provider=s['provider'])
   r.update(real_growth_pct=m['real_growth_pct'],nominal_wage_proxy_man=m['nominal_wage_proxy_man'],real_wage_proxy_man=m['real_wage_proxy_man'],core_real_gdp_trn=m['core_real_gdp_trn'],capital_delta_real_trn=m['capital_delta_real_trn'],macro_cash_DI_proxy_trn=r['household_disposable_nominal_trn']-r['household_direct_price_benefit_trn'],old_medical_insurer_trn=m['medical_reform_insurer_balance'],old_medical_patient_shift_trn=m['medical_patient_shift'],old_medical_hubs_trn=m['hub_spend'])
   jobs=b['d'][i]['domestic_employed_conditional']+b['foreign'][i]['foreign_jobs']+b['elder'][i]['F_extra_jobs']+b['pension'][i]['additional_jobs']
   r.update(employed_persons_proxy=jobs,gross_wage_bill_proxy_trn=jobs*m['nominal_wage_proxy_man']*10000/1e12,national_PB_trn=None,national_debt_trn=None,national_bond_issue_trn=None,policy_interest_rate=None,income_median=None,gini_actual=None,engel_actual=None,births_policy_connected=None,deaths_policy_connected=None,partial_medical_debt_only_trn=w['medical_policy_debt_stock_trn'])
   for k in ['old_medical_insurer_trn','old_medical_patient_shift_trn','old_medical_hubs_trn']:close(r[k],0.)
   medical.append(dict(case=s['id'],**w));common.append(dict(case=s['id'],**co));education.append(dict(case=s['id'],**z));fiscal.append({**fi,**{k:val for k,val in w.items() if k.endswith('_trn')},'case':s['id'],'year':r['year']})
   labor.append(dict(case=s['id'],year=r['year'],population=r['population'],japanese=b['d'][i]['japanese'],foreign=b['d'][i]['foreign'],under15=b['d'][i]['under15'],working_age=b['d'][i]['working_age'],elderly=b['d'][i]['elderly'],foreign_jobs=b['foreign'][i]['foreign_jobs'],elder_extra_jobs=b['elder'][i]['F_extra_jobs'],pension_extra_jobs=b['pension'][i]['additional_jobs'],employed_persons_proxy=jobs,effective_labor=r['labor_force_population_proxy'],medical_effective_labor=w['health_effective_labor_added'],education_effective_labor=z['education_effective_labor_added'],nominal_wage_proxy_man=m['nominal_wage_proxy_man'],gross_wage_bill_proxy_trn=r['gross_wage_bill_proxy_trn']))
   hh.append(dict(case=s['id'],year=r['year'],unit='trillion_yen_per_year',positive_sign='burden_increase',uncalibrated=True,**{k:co[k] for k in co if any(t in k for t in ['household','family_','ltc_','guarantee_','savings_','borrowing_'])},medical_patient_delta_trn=w['patient_payment_delta_trn'],common_patient_delta_trn=co['patient_payment_delta_trn'],ordinary_medical_premium_delta_trn=w['premium_payment_delta_trn'],financing_tax_trn=w['medical_financing_tax_trn'],financing_premium_trn=w['medical_financing_premium_trn'],total_medical_household_cash_delta_trn=w['household_cash_delta_trn'],macro_cash_DI_proxy_trn=r['macro_cash_DI_proxy_trn'],income_loss_share=s['common_overrides'].get('income_loss_share',.4),guarantee_avoided_yen=s['common_overrides'].get('guarantee_avoided_yen',30000),home_noninsured_yen=s['common_overrides'].get('noninsured_yen',{'HOME':250000})['HOME'],proxy_coverage=s['common_overrides'].get('public_proxy_coverage',.6),family_hours_multiplier=s['common_overrides'].get('family_hours_multiplier',1.)))
  for z in sectors:
   if z['sector']=='medical':vat.append(dict(case=s['id'],**z))
  if s['id'] in ['LATEST_F','MEDICAL_OFF','COMMON_ONLY','F_ONLY','LEGACY_PAYER','CAP_BENEFIT_DOWN']:claims.extend(dict(case=s['id'],**z) for z in md.groups)
  demography.extend(dict(case=s['id'],**z) for z in md.demography);paths[s['id']]=rows
  print(json.dumps(dict(progress=index+1,total=len(c['cases']),case=s['id'])),flush=True)
 # Fixed references are actual bytes already verified by Claude; no redundant
 # reimplementation claim. Only changed-model regressions are executed above.
 for case,source,filtercase in [('SQ_FIXED',er,'SQ_FIXED'),('OLD_EDUCATION_F',er,'COMBINED'),('OLD_MEDICAL_F',oldall,'COMMON_F_MEDIUM')]:
  paths[case]=[{k:(int(val) if k=='year' else val if k=='case' or val=='' else float(val) if isnumber(val) else val) for k,val in r.items()} for r in source if r['case']==filtercase]
  for r in paths[case]:r['case']=case;r['reference_status']='IMMUTABLE_FIXED_REFERENCE'
 metrics=['real_gdp_trn','nominal_gdp_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','labor_force_population_proxy','tax_diagnostic_trn','consolidated_partial_balance_proxy_trn','macro_cash_DI_proxy_trn','modeled_VAT_trn']
 comparison=[];effects=[];interactions=[]
 for name,rows in paths.items():
  for i,r in enumerate(rows):
   q=dict(case=name,year=r['year'],sensitivity_not_forecast=name not in ['SQ_FIXED','OLD_EDUCATION_F','OLD_MEDICAL_F'])
   for k in metrics:
    q[k]=r.get(k)
    for refname in ['SQ_FIXED','OLD_EDUCATION_F','OLD_MEDICAL_F','LATEST_F']:
     other=paths[refname][i].get(k);q[k+'_minus_'+refname]=r.get(k)-other if isinstance(r.get(k),(int,float)) and isinstance(other,(int,float)) else None
   comparison.append(q)
 for channel in ['VAT','FOREIGN','ELDER','PENSION','HOUSEHOLD_A','HOUSEHOLD_B','HOUSEHOLD_C','EDUCATION','INVESTMENT','FIRM','COMMON','F_MEDICAL']:
  for i,y in enumerate(range(2026,2056)):
   for k in metrics:
    effects.append(dict(channel=channel,year=y,metric=k,marginal_in_integrated_F=paths['LATEST_F'][i][k]-paths['NO_'+channel][i][k],method='paired_reexecution_full_minus_off',additive_attribution=False))
 for i,y in enumerate(range(2026,2056)):
  for k in metrics:
   z=paths['MEDICAL_OFF'][i][k];commonv=paths['COMMON_ONLY'][i][k]-z;fv=paths['F_ONLY'][i][k]-z;comb=paths['LATEST_F'][i][k]-z
   interactions.append(dict(year=y,metric=k,common=commonv,F_medical=fv,combined=comb,interaction=comb-commonv-fv))
 # Cross-channel difference-in-differences on the same fully solved engine.
 for name,bothoff,channeloff in [('EDUCATION_MEDICAL','NO_EDUCATION_NO_MEDICAL','NO_EDUCATION'),('VAT_MEDICAL','NO_VAT_NO_MEDICAL','NO_VAT')]:
  for i,y in enumerate(range(2026,2056)):
   for k in metrics:
    interactions.append(dict(test=name,year=y,metric=k,interaction=paths['LATEST_F'][i][k]-paths[channeloff][i][k]-paths['MEDICAL_OFF'][i][k]+paths[bothoff][i][k],method='full_minus_single_offs_plus_both_off'))
 sensitivity=[]
 for y in range(2026,2056):
  sample=[r for r in hh if r['year']==y and (r['case']=='LATEST_F' or r['case'].startswith('HH_'))]
  for metric in ['household_direct_cash_burden_delta_trn','household_total_economic_burden_delta_trn','total_medical_household_cash_delta_trn']:
   lo=min(sample,key=lambda x:x[metric]);hi=max(sample,key=lambda x:x[metric]);sensitivity.append(dict(year=y,metric=metric,unit='trillion_yen_per_year',lower=lo[metric],lower_case=lo['case'],upper=hi[metric],upper_case=hi['case'],sign_reversal=lo[metric]<0<hi[metric],status='UNCALIBRATED_SENSITIVITY_RANGE'))
 allrows=[r for rows in paths.values() for r in rows]
 for name,rs in [('Annual.csv',allrows),('Comparison.csv',comparison),('Summary.csv',[r for r in comparison if r['year'] in [2026,2030,2035,2040,2045,2055]]),('Medical_Accounts.csv',medical),('Common_EndOfLife.csv',common),('Household.csv',hh),('Household_Sensitivity.csv',sensitivity),('Fiscal.csv',fiscal),('Labor.csv',labor),('Education.csv',education),('Demography_Demand.csv',demography),('VAT_Medical.csv',vat),('Claims_Examples.csv',claims),('Policy_Effects.csv',effects),('Interactions.csv',interactions)]:dump(out/name,rs)
 (out/'Validation.json').write_text(json.dumps(dict(status='PASS_LOCAL_EXECUTION',cases=len(paths),executed_cases=len(c['cases']),fixed_references=3,annual_rows=len(allrows),years=[2026,2055],checks=['inherited GDP/capital identities','old clinical flows zero','payer claim sum','explicit counterpart sum','government-insurer sum','fixed dependency byte identity'],scope='Existing implemented F channels and provisional background;not all original policy instruments causally modeled'),indent=2)+'\n')
 print('COMPLETE',len(allrows),flush=True)

def isnumber(x):
 try:float(x);return True
 except (ValueError,TypeError):return False
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('inputs');ap.add_argument('--outdir',required=True);a=ap.parse_args();run(a.inputs,a.outdir)
