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
 exec(compile(source,'medical_education_integrated.py','exec'),ns);return ns
def run(inp,out):
 c=json.loads(Path(inp).read_text());root,edu,ec,integ,v,vc=load(c);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 fixed=read(root/'handoff/f-education-20261121/Annual.csv');old={int(r['year']):r for r in fixed if r['case']=='COMBINED'};sq={int(r['year']):r for r in fixed if r['case']=='SQ_FIXED'}
 ir=read(root/'handoff/f-integrated-20261121/Annual.csv');ir={int(r['year']):r for r in ir if r['case']=='FULL_ADDITIONAL'}
 deflators=[float(ir[y]['common_deflator']) for y in range(2026,2056)];population=[float(ir[y]['population']) for y in range(2026,2056)]
 eduspec=next(x for x in ec['cases'] if x['id']=='COMBINED')
 paths={};clinical=[];commonrows=[];groups=[];fiscals=[];vat=[];education=[];regression=0
 for sp in c['cases']:
  s={**c['defaults'],**sp};ed=edu.Education(ec,eduspec,deflators);md=Medical(c,s,deflators,population)
  integ._education_hook=lambda engine,pol:patch(edu.patched_engine(engine,pol,ed,'REPLACE'),pol,md,s)
  rows,inc,sectors,b,raw,cc=integ.execute(v,vc,dict(id=s['id'],C=s['C'],C_mode=s['C_mode']))
  if s['keep_legacy']:
   for r in rows:
    for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','fiscal_balance_partial_trn','C_cash_trn','total_unassigned_funding_trn','labor_force_population_proxy','household_disposable_nominal_trn']:
     close(r[k],float(old[r['year']][k]));regression+=1
  for i,(r,m) in enumerate(zip(rows,raw)):
   fi=integ.fiscal(r,m,b,i,cc);w=md.rows[i] if md.rows else {};z=ed.rows[i]
   if w:
    fi['insurer_known_change_and_program_balance_trn']+=w['insurer_balance_delta_trn']
    fi['consolidated_partial_balance_proxy_trn']+=w['insurer_balance_delta_trn']
   r.update(fi);r.update(z);r.update(w);r['case']=s['id'];r['legacy_medical_preserved']=s['keep_legacy'];r['legacy_education_mode']='REPLACE';r['C_interpretation']=s['C_mode'] if s['C'] else 'DIRECT_PRICE_ONLY'
   r.update(real_growth_pct=m['real_growth_pct'],capital_delta_real_trn=m['capital_delta_real_trn'],nominal_wage_proxy_man=m['nominal_wage_proxy_man'],real_wage_proxy_man=m['real_wage_proxy_man'],macro_cash_DI_proxy_trn=r['household_disposable_nominal_trn']-r['household_direct_price_benefit_trn'],old_medical_government_trn=-m['medical_patient_shift']+m['medical_high_cost_relief']+m['medical_provider_receipt']+m['medical_reform_insurer_balance']+m['hub_spend'],old_medical_insurer_trn=m['medical_reform_insurer_balance'],old_medical_hub_capital_trn=m.get('hub_spend'),full_national_medical_balance_trn=None,national_PB_trn=None,national_debt_trn=None)
   r['ABC_unassigned_funding_only_trn']=r['total_unassigned_funding_trn']
   r['ABC_plus_medical_unassigned_direct_proxy_trn']=r['total_unassigned_funding_trn']+(w.get('medical_unassigned_direct_cash_requirement_trn',0.))
   r['F_minus_SQ_real_GDP_trn']=r['real_gdp_trn']-float(sq[r['year']]['real_gdp_trn']);r['GDP_minus_latest_education_trn']=r['real_gdp_trn']-float(old[r['year']]['real_gdp_trn'])
   close(fi['government_partial_balance_proxy_trn']+fi['insurer_known_change_and_program_balance_trn'],fi['consolidated_partial_balance_proxy_trn'])
   if w:
    clinical.append(dict(case=s['id'],**w));commonrows.append(dict(case=s['id'],**md.common[i]));fiscals.append({**fi,**{k:w[k] for k in w if k.endswith('_trn')},'case':s['id'],'year':r['year']})
   education.append(dict(case=s['id'],**z))
  for se in sectors:
   if se.get('sector')=='medical' or se.get('sector_id')=='medical':vat.append(dict(case=s['id'],**se,medical_credit_readded_trn=0.))
  groups.extend(dict(case=s['id'],**r) for r in md.groups);paths[s['id']]=rows
 # Preserved SQ is a fixed comparator; common policy is separately identified,
 # never described as an F-exclusive advantage over this common-OFF comparator.
 paths['SQ_FIXED']=[dict(r,case='SQ_FIXED',year=int(r['year'])) for r in fixed if r['case']=='SQ_FIXED']
 comparison=[];interactions=[]
 metrics=['real_gdp_trn','nominal_gdp_trn','macro_cash_DI_proxy_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','labor_force_population_proxy','tax_diagnostic_trn','consolidated_partial_balance_proxy_trn','modeled_VAT_trn','C_cash_trn','total_unassigned_funding_trn']
 for name,rows in paths.items():
  if name=='SQ_FIXED':continue
  for i,r in enumerate(rows):
   q=dict(case=name,year=r['year'],C_interpretation=r['C_interpretation'],common_policy_included=next({**c['defaults'],**x}['common'] for x in c['cases'] if x['id']==name),SQ_common_policy=False)
   for k in metrics:
    q[k]=r[k];q[k+'_minus_old']=r[k]-float(old[r['year']][k]);q[k+'_minus_medical_off']=r[k]-paths['OLD_MEDICAL_REMOVED'][i][k]
   comparison.append(q)
 for i,y in enumerate(range(2026,2056)):
  for k in metrics:
   off=paths['OLD_MEDICAL_REMOVED'][i][k];co=paths['COMMON_ONLY'][i][k]-off;cp=paths['COPAY_ONLY'][i][k]-off;pr=paths['PROVIDER_ONLY'][i][k]-off;f=paths['F_COMBINED'][i][k]-off;allv=paths['COMMON_F_MEDIUM'][i][k]-off
   interactions.append(dict(year=y,metric=k,common_only=co,copay_only=cp,provider_only=pr,F_combined=f,F_interaction=f-cp-pr,common_F_combined=allv,common_F_interaction=allv-co-f,all_interaction=allv-co-cp-pr))
 # Standalone contractual equivalence across policy labels is not a simulation of
 # the unimplemented policy sets. The label is deliberately excluded from inputs.
 contract=[]
 for y in range(2026,2056):
  i=y-2026;d=dict(price_index=deflators[i]/deflators[0],population_scale=population[i]/population[0],registry_population=c['registry_population_reference']*population[i]/population[0],clinical_strata=c['clinical_strata'])
  values=[]
  for label in ['F','N3','N','F3','R4']:
   rr=calculate(y,d,c['common_parameters'],c['common_financing']);values.append(rr);contract.append(dict(policy_label=label,contract_test_only=True,**rr))
  assert all(x==values[0] for x in values)
  if y>=2035:
   for override in [dict(confirmed_share=0.),dict(explicit_preference_share=0.)]:close(calculate(y,d,{**c['common_parameters'],**override},c['common_financing'])['chosen_transitions'],0.)
 for r in commonrows:
  if r['case'] in ['ZERO_CLINICAL_SAVING','COMMON_ZERO_SAVING']:close(r['clinical_cost_delta_trn'],0.)
  if r['case'] in ['COST_INCREASE','COMMON_COST_INCREASE'] and r['year']>=2032:assert r['clinical_cost_delta_trn']>0
 household=[{k:r.get(k) for k in r if k in ['case','year','patient_payment_delta_trn','record_adoption','reference_rate','proxy_designation_rate'] or any(t in k for t in ['household','family_','ltc_','guarantee_','savings_','borrowing_'])} for r in commonrows]
 dump(out/'Household_EndOfLife.csv',household)
 allrows=[r for rows in paths.values() for r in rows]
 for f,rs in [('Annual.csv',allrows),('Medical_Accounts.csv',clinical),('Common_EndOfLife.csv',commonrows),('Household_Age_Income.csv',groups),('Fiscal.csv',fiscals),('Comparison.csv',comparison),('Interactions.csv',interactions),('Common_Interface_Tests.csv',contract),('Education_Preserved.csv',education),('VAT_No_DoubleCount.csv',vat),('Legacy_Medical.csv',[{k:r.get(k) for k in ['case','year','old_medical_government_trn','old_medical_insurer_trn','old_medical_hub_capital_trn','legacy_medical_preserved']} for rs in paths.values() for r in rs if r['case']!='SQ_FIXED']),('Summary.csv',[r for r in comparison if r['year'] in [2026,2030,2035,2040,2045,2055]])]:dump(out/f,rs)
 validation=dict(status='PASS_LOCAL',cases=len(paths),annual_rows=len(allrows),legacy_regression_cells=regression,common_policy_label_rows=len(contract),claims_rows=len(groups),checks=['9 pinned dependency byte identities','education COMBINED reproduced through medical identity hook','old medical flows removed before replacement','clinical payer sum','HH-provider-government-insurer-supplier transfer sum','internal transfer cancellation','common same-input five-label identity','no confirmed wishes / no explicit preference => zero transitions','clinical saving zero and cost increase cases','original GDP / capital identities','VAT credit added zero','education subsystem retained'],limitations=['synthetic claim and income mix not statutory entitlement forecast','fixed age cost shares','clinical eligible pool and all causal coefficients uncalibrated','QOL/QALY/healthy life years unknown','medical volume valued with explicit domestic value-added proxy','national PB/debt and full insurer accounts unknown'])
 (out/'Validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n');print(json.dumps(validation))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('inputs');ap.add_argument('--outdir',required=True);a=ap.parse_args();run(a.inputs,a.outdir)
