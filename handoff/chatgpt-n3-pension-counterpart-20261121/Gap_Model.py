#!/usr/bin/env python3
"""Add candidate N3 components through the existing SQ/common GDP engine.
usage: python N3_Expansion_Model.py INPUTS --engine ROOT --source ROOT --outdir DIR
All changes are runtime adapters; fixed source files remain read-only.
"""
import os,sys,argparse,json,copy,csv,math,hashlib,inspect,contextlib,io
from pathlib import Path
sys.dont_write_bytecode=True
from Gap_Components import Components,phase,quantity_channels

def run(config,engine,source,out):
 cfg=json.loads(Path(config).read_text());
 for pin in json.loads((Path(__file__).parent/'Dependency_Pins.json').read_text()):
  b=(Path(engine)/pin['path']).read_bytes();assert len(b)==pin['size'] and hashlib.sha256(b).hexdigest()==pin['sha256'],pin['path']
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);engine=Path(engine).resolve();source=Path(source).resolve()
 F=engine/'handoff/f-common-endoflife-finalization-20261121';sys.path.insert(0,str(F))
 import Model as M,FMedical as FM
 script=source/'handoff/claude-n3-model-draft-20261121/SPE_N3_Medical_On_CommonSQ_Draft_DRAFT_20261121.py';b=script.read_bytes()
 assert hashlib.sha256(b).hexdigest()==cfg['draft_script_sha256']
 # Load the original definitions and validated baseline interface, keeping its
 # original self-test and14 cases. Execute only in a private namespace.
 text=b.decode();prefix=text[:text.index('annual=[];common_rows=[]')];body=text[text.index('annual=[];common_rows=[]'):]
 original_argv=sys.argv;sys.argv=[str(script),str(engine),str(out)]
 ns={'__name__':'n3_existing_adapter','__file__':str(script)}
 try:exec(compile(prefix,str(script),'exec'),ns)
 finally:sys.argv=original_argv
 c=ns['c'];vc=ns['vc'];v=ns['v'];integ=ns['integ'];legacy=list(ns['CASES']);cases=legacy+[(z['id'],True,z.get('medical',False),z.get('rate',.5),z.get('cap_change',0.),z.get('cap_mode','PATIENT_CAP_DOWN'),z.get('start_year',2033),z.get('ramp_years',6),z.get('scope','ALL_AGES'),z.get('vat')) for z in cfg['cases']]
 extensions={z['id']:z for z in cfg['cases']};active={};objects=[];claim_audit=[];quantity_audit={};sector_audit=[];engine_audit=[]
 current_tax={};regular_original=v.regular_account;tax_original=v.tax_account
 def regular(*args,**kw):
  z=regular_original(*args,**kw)
  if current_tax.get('record'):
   slot=current_tax['slot'];current_tax['slot']+=1;quantity_audit[current_tax['case'],current_tax['year'],slot]=dict(case=current_tax['case'],year=current_tax['year'],market=['HH_STANDARD','HH_FOOD','NON_HH'][slot],**z)
  return z
 def tax_capture(c,s,y,N):
  current_tax.update(record=s.get('policy')=='SQ',case=s.get('id'),year=y,slot=0)
  z=tax_original(c,s,y,N);current_tax['record']=False;return z
 v.regular_account=regular;v.tax_account=tax_capture
 original_execute=integ.execute
 def capture_execute(*args,**kw):
  z=original_execute(*args,**kw);sector_audit.extend(dict(case=args[2]['id'],**r) for r in z[2]);engine_audit.extend(dict(case=args[2]['id'],year=r['year'],**{k:m.get(k) for k in ['tax_macro_trn','tax_diagnostic_trn','fiscal_balance_partial_trn','core_real_gdp_trn','common_deflator','real_gdp_trn','capital_delta_real_trn','real_growth_pct','household_disposable_nominal_trn','effective_labor','C_demand_real_trn','expenditure_diagnostic_trn','household_consumption_real_proxy_trn','labor_force_population_proxy']}) for r,m in zip(z[0],z[4]));return z
 integ.execute=capture_execute
 data=json.loads((engine/'handoff/f-household-social-20261120/Inputs.json').read_text());pen=json.loads((engine/'handoff/f-pension-policy-20261120/Inputs.json').read_text())
 core=[float(r['nominal_gdp_trn']) for r in M.read(engine/'handoff/f-integrated-20261121/Annual.csv') if r['case']=='SQ_CURRENT']
 assert len(core)==30
 original_medical=FM.Medical;original_claim=ns['_orig_claim'];base_n3_claim=ns['n3_claim']
 # Compile a separate rate-interpolation class; the original class is unchanged.
 medsrc=(F/'FMedical.py').read_text().replace('b=a+(b-a)*ph','b=b').replace("return aa+(reform-aa)*ph if s['copay'] else aa","return reform if s['copay'] else aa")
 medns=dict(FM.__dict__);exec(compile(medsrc,'rate_interpolation_candidate.py','exec'),medns);RateMedical=medns['Medical']
 def newclaim(age,group,profile,regime,uniform=False,cap_multiplier=1.):
  if not uniform:return original_claim(age,group,profile,regime,False,cap_multiplier)
  spec=active['spec'];year=active['year'];old=ns['N3'].copy()
  if spec.get('interpolation','AMOUNT')=='RATE':
   cur=.2 if age=='PRESCHOOL' else (.2 if age=='AGE70_74' else .1) if age in ['AGE70_74','AGE75PLUS'] and group in ['TAXFREE','GENERAL'] else .3
   target=old['coinsurance'] if old['scope']!='ONLY_CURRENT_30' or abs(cur-.3)<1e-12 else cur
   ns['N3'].update(coinsurance=cur+phase(year,spec['start_year'],spec['ramp_years'])*(target-cur),scope='ALL_AGES')
  try:return base_n3_claim(age,group,profile,regime,True,cap_multiplier)
  finally:ns['N3'].update(old)
 FM.patient_claim=newclaim;medns['patient_claim']=newclaim
 class ExpandedMedical(original_medical):
  def __init__(self,c,s,defs,pops):
   active.clear();ex=extensions.get(s['id'],{});s={**s,**ex};super().__init__(c,s,defs,pops);ecfg={**cfg['candidate_parameters'],**ex,'core_nominal':core};self.components=Components(ecfg,data,pen);self.mask=[k for k in ['medical','vat','flat_hh','corporate','corporate_incentive','pension75','relief','employment','kpi'] if s.get(k)];self.mask += ['VAT_QUANTITY'] if ex.get('quantity_elasticity',0)>0 else [];self.mask += ['RATE_INTERPOLATION'] if ex.get('interpolation')=='RATE' else [];self.mask += ['MEDICAL_FINANCE_CANDIDATE'] if 'finance_fraction' in ex else [];self.mask += ['STRUCTURE_ONLY_FOREIGN_OPEN'] if s['id'].startswith('FOREIGN_INTERFACE') else [];objects.append(self)
   vc['defaults']['quantity_elasticity']=ex.get('quantity_elasticity',0.);vc['defaults']['rate_pass']=ex.get('rate_pass',.8)
  def quantity_step(self,y):
   z=quantity_channels(self.s,y,quantity_audit,vc);self.rows[-1].update(z);return z
  def step(self,y,prior=None):
   active.update(spec=self.s,year=y)
   if self.s['id'] in ['N3_MED_50_CAP_SAME','MED_RATE_INTERPOLATION'] and 2033<=y<=2038:
    for age in ['PRESCHOOL','AGE6_69','AGE70_74','AGE75PLUS']:
     for group in c['income_weights']:
      for bill in [50000,150000,1200000]:
       for months in [1,3,6]:
        prof=dict(bill_yen=bill,months=months);before=FM.annual_patient(y,age,group,prof);after=FM.annual_patient(y,age,group,prof,uniform=True);ph=phase(y,self.s['start_year'],self.s['ramp_years']);paid=after if self.s.get('interpolation')=='RATE' else before+ph*(after-before)
        claim_audit.append(dict(case=self.s['id'],year=y,age=age,income=group,bill_yen=bill,months=months,mode=self.s.get('interpolation','AMOUNT'),phase=ph,actual_paid_yen=paid))
   # The medical claim and payer closure must use the same candidate mode.
   if self.s.get('interpolation')=='RATE':w=RateMedical.step(self,y)
   else:w=original_medical.step(self,y)
   p=self.components.step(y,self,prior or [])

   # Medical-financing channels retain separate accounts; policy modules have
   # their own unclosed budget, never auto-funded by an invented tax.
   w.update({('medical_only_'+k):w[k] for k in ['household_cash_delta_trn','government_cost_delta_trn','insurer_balance_delta_trn']})
   w.update(p)
   w['household_cash_delta_trn']+=p['policy_household_cash_delta_trn'];w['government_cost_delta_trn']+=p['policy_government_cost_delta_trn'];w['engine_direct_tax_delta_trn']=w['medical_financing_direct_tax_trn']+p['policy_tax_delta_trn'];w['service_production_nominal_delta_trn']+=p['policy_service_VA_delta_trn'];w['investment_nominal_delta_trn']+=p['policy_investment_delta_trn']
   w.update(implementation_mask=';'.join(self.mask) or 'LEGACY_MEDICAL_VAT_ONLY',interpolation_mode=self.s.get('interpolation','AMOUNT'),candidate_only=True)
   active['kpi_freeze']=self.components.structures[-1]['kpi_freeze_candidate'] if self.s.get('kpi') else False
   return w
 FM.Medical=ExpandedMedical
 originalrates=ns['n3_vat']
 def rates(y,freeze=False):return originalrates(y,freeze or bool(active.get('kpi_freeze')))
 ns['n3_vat']=rates;ns['CASES']=cases
 # Attach previous actual macro rows and the explicit new-job labor delta.
 body=body.replace('w=_medical.step(y)','w=_medical.step(y,rows)\\n        t=copy.copy(t);t[\'effective_productive_workers\']+=w[\'n3_effective_labor_delta\']')
 # source literal above must contain escaped newlines, not actual string breaks.
 body=body.replace("a.update({k:r.get(k) for k in KEYS});a.update({k:w.get(k) for k in MK});annual.append(a)","a.update({k:r.get(k) for k in KEYS});a.update(w);a.update(population=r['population'],macro_cash_DI_proxy_trn=r.get('household_disposable_nominal_trn'),consolidated_partial_balance_proxy_trn=r['fiscal_balance_partial_trn']+r.get('insurer_balance_direct_trn',0)+r.get('insurer_VAT_balance_delta_trn',0)+w['medical_only_insurer_balance_delta_trn']+w['policy_insurer_cash_delta_trn']);annual.append(a)")
 body=body.replace("common_rows.append(dict(case=cid,year=r['year'],**{k:co.get(k) for k in CK}))","common_rows.append(dict(case=cid,**co))")
 body=body.replace("w['medical_financing_direct_tax_trn']","w['engine_direct_tax_delta_trn']")
 # Add only a C-target correction. Fixed-price demand is replaced for the
 # regular HH taxable basket, not supplemented. GDP/income/tax feedback solve once.
 body=body.replace("        exec(compile(source,'n3_medical_on_SQ_adapter.py','exec'),ns);return ns", "        sub(\"        Ctarget=\",\"        w.update(_medical.quantity_step(y))\\n        Ctarget=\")\n        sub(\"-p['generic_mpc']*_pension[i]['household_cash_delta_trn'])/coreD\",\"-p['generic_mpc']*_pension[i]['household_cash_delta_trn']+w['quantity_nominal_volume_delta_trn']-p['generic_mpc']*w['quantity_replaced_price_benefit_trn']+(p['generic_mpc']-w['estate_mpc_candidate'])*w['wealth_tax_delta_trn'])/coreD\")\n        exec(compile(source,'n3_medical_on_SQ_adapter.py','exec'),ns);return ns")
 body=body.replace('N3_Medical_Annual.csv','Gap_Annual.csv').replace('N3_Medical_Common.csv','Gap_Common.csv').replace('N3_Medical_vs_SQ_Common_On.csv','Gap_vs_SQ.csv')
 # Include new policy columns in absolute/SQ-difference comparison.
 ns['KEYS']+=['population','policy_tax_delta_trn','policy_household_cash_delta_trn','policy_insurer_cash_delta_trn','policy_budget_unclosed_trn','policy_investment_delta_trn','public_added_jobs','dividend_delta_trn','pension_benefit_delta_trn','premium_relief_trn','in_kind_trn']
 # Baseline r lacks satellite keys; add them after medical row overlay above.
 exec(compile(body,'n3_expanded_runtime_adapter.py','exec'),ns)
 M.dump(out/'N3_Engine_Accounts.csv',engine_audit)
 M.dump(out/'N3_Claim_Candidate_Audit.csv',claim_audit);M.dump(out/'N3_VAT_Regular_Quantity.csv',list(quantity_audit.values()));M.dump(out/'N3_VAT_Sectors.csv',sector_audit)
 for name,rows in [('N3_Policy_Accounts.csv',[dict(case=md.s['id'],**r) for md in objects for r in md.components.rows]),('N3_Pension_Accounts.csv',[dict(case=md.s['id'],**r) for md in objects for r in md.components.pension]),('N3_Income_Distribution.csv',[dict(case=md.s['id'],**r) for md in objects for r in md.components.households]),('N3_Corporate_Accounts.csv',[dict(case=md.s['id'],**r) for md in objects for r in md.components.firms]),('N3_Structural_Interfaces.csv',[dict(case=md.s['id'],**r) for md in objects for r in md.components.structures])]:M.dump(out/name,rows)
 for name,attr in [('Gap_Additional_Accounts.csv','gap_rows'),('Gap_Foreign_Bridge.csv','foreign_rows'),('Gap_Semi_Medical.csv','semi_rows')]:M.dump(out/name,[dict(case=md.s['id'],**r) for md in objects for r in getattr(md.components,attr)])
 # Preserve immutable old outputs by reference; never duplicate8 originals.
 (out/'Execution_Metadata.json').write_text(json.dumps(dict(executed_cases=len(cases),years=[2026,2055],annual_rows=len(cases)*30,legacy_cases=len(legacy),new_cases=len(cfg['cases']),source_script='3c77eafc2073fdaba4c129164817d2f57c9421b9:handoff/claude-n3-model-draft-20261121/'+script.name,engine_commit=cfg['engine_commit'],scope='N3_PARTIAL_CONNECTED_CANDIDATES',not_N3_FULL=True,selected_run=os.environ.get('SPE_PENSION_MODE','DOMESTIC_TRANSFER')+'_CANDIDATE_NOT_ADOPTED',case_partition='14 original draft + 65 configured = 79; previous expansion 46 + gap addition 33 = 79'),indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('--engine',required=True);p.add_argument('--source',required=True);p.add_argument('--outdir',required=True);a=p.parse_args();run(a.inputs,a.engine,a.source,a.outdir)
