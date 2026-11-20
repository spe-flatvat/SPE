#!/usr/bin/env python3
"""Changed-model checks and deterministic replay; reused Claude evidence is separate."""
import argparse,csv,hashlib,json,math,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
def read(n):return list(csv.DictReader((P/n).open()))
def close(a,b):assert math.isclose(float(a),float(b),rel_tol=2e-9,abs_tol=1e-7),(a,b)
def run(replay):
 from CommonEndOfLife import calculate
 from FMedical import annual_patient
 c=json.loads((P/'Inputs.json').read_text());counts={};tests=[]
 rs=read('Annual.csv');by={(r['case'],int(r['year'])):r for r in rs}
 assert len(rs)==(len(c['cases'])+3)*30
 old= list(csv.DictReader((P.parent/'f-medical-common-20261121/Annual.csv').open()));old={(r['case'],int(r['year'])):r for r in old}
 for y in range(2026,2056):
  for k in ['real_gdp_trn','nominal_gdp_trn','macro_cash_DI_proxy_trn','tax_diagnostic_trn','consolidated_partial_balance_proxy_trn','capital_total_real_trn','labor_force_population_proxy','modeled_VAT_trn']:
   close(by['MEDICAL_OFF',y][k],old['OLD_MEDICAL_REMOVED',y][k])
 counts['unchanged_education_integration_regression_cells']=240
 for r in read('Medical_Accounts.csv'):
  close(r['clinical_cost_delta_trn'],sum(float(r[k]) for k in ['patient_payment_delta_trn','public_clinical_payment_delta_trn','insurer_clinical_payment_delta_trn']))
  other=sum(float(r[k]) for k in ['setting_provider_receipts_trn','proxy_provider_receipts_trn','guarantee_provider_receipts_trn','family_lost_income_counterpart_trn','interest_creditor_receipts_trn','displaced_other_supplier_receipts_trn','medical_financing_direct_tax_trn'])
  close(float(r['household_cash_delta_trn'])+float(r['provider_payment_receipts_delta_trn'])+float(r['common_supplier_receipts_trn'])-float(r['government_cost_delta_trn'])+float(r['insurer_balance_delta_trn'])+other,0.)
  close(r['partial_public_direct_balance_delta_trn'],-float(r['government_cost_delta_trn'])+float(r['insurer_balance_delta_trn'])+float(r['medical_financing_direct_tax_trn']))
 counts['clinical_and_explicit_counterparty_rows']=len(read('Medical_Accounts.csv'))
 for r in read('Fiscal.csv'):close(float(r['government_partial_balance_proxy_trn'])+float(r['insurer_known_change_and_program_balance_trn']),r['consolidated_partial_balance_proxy_trn'])
 for r in read('Education.csv'):close(r['bond_end_trn'],float(r['bond_begin_trn'])+float(r['bond_issue_trn'])-float(r['bond_redemption_trn']))
 for r in read('Household.csv'):
  close(r['household_direct_cash_burden_delta_trn'],float(r['common_patient_delta_trn'])+float(r['extra_household_cash_burden_trn']))
  close(float(r['savings_drawdown_delta_trn'])+float(r['borrowing_need_delta_trn']),r['household_direct_cash_burden_delta_trn'])
 # Behavioral protection tests: varying registrations and withdrawals changes
 # supported choice only; insurance rules and universal palliative supply/cost do not.
 demand=dict(price_index=1.,population_scale=1.,registry_population=c['registry_population_reference'],clinical_strata=c['clinical_strata'],age_demand_episodes=450000)
 params={**c['common_parameters'],'universal_palliative':True,'palliative_additional_yen':0.}
 for y in [2035,2040,2055]:
  results=[]
  for adoption in [0.,.3,.6]:
   for withdrawn in [0.,1.]:
    pp={**params,'adoption_target':adoption,'withdrawn_share':withdrawn}
    r=calculate(y,demand,pp,c['common_financing']);results.append(r)
    for age in ['PRESCHOOL','AGE6_69','AGE70_74','AGE75PLUS']:
     for group in c['income_weights']:
      # Registration is intentionally absent from the callable tariff interface.
      cost=annual_patient(y,age,group,dict(months=3,bill_yen=400000),uniform=True,cap_multiplier=.9)
      tests.append(dict(year=y,registration=adoption,withdrawn=withdrawn,age=age,income_group=group,claim_total_yen=1200000,patient_yen=cost,benefit_yen=1200000-cost,universal_palliative_served=r['universal_palliative_served'],universal_palliative_cost_trn=r['universal_palliative_cost_trn'],supported_choices=r['chosen_transitions']))
    if not adoption or withdrawn:close(r['chosen_transitions'],0.)
  for r in results:
   close(r['universal_palliative_served'],results[0]['universal_palliative_served']);close(r['universal_palliative_cost_trn'],results[0]['universal_palliative_cost_trn'])
  unknown=calculate(y,demand,{**params,'confirmed_share':0.},c['common_financing']);close(unknown['chosen_transitions'],0.);assert unknown['universal_palliative_served']>0
 for y in range(2026,2056):
  r=calculate(y,demand,params,c['common_financing']);assert r['law_passed']==int(y>=2030) and r['national_operation']==int(y>=2035)
  if y<2032:close(r['chosen_transitions'],0.);close(r['universal_palliative_served'],0.)
  if y==2035:assert r['implementation_phase']==1. and r['record_adoption']<1.
 # Different real caller conditions, not a label passed to identical calls.
 callers=[]
 for name,pop,capacity,fin in [('CALLER_A',450000,1.,{'HOUSEHOLD':.1,'GOVERNMENT':.4,'INSURER':.5}),('CALLER_B',600000,.5,{'HOUSEHOLD':.3,'GOVERNMENT':.2,'INSURER':.5})]:
  r=calculate(2040,{**demand,'age_demand_episodes':pop,'capacity_multiplier':capacity},params,fin)
  close(r['clinical_cost_delta_trn'],r['patient_payment_delta_trn']+r['public_clinical_payment_delta_trn']+r['insurer_clinical_payment_delta_trn']);callers.append(dict(caller=name,**r))
 assert callers[0]['clinical_demand_episodes']!=callers[1]['clinical_demand_episodes'] and callers[0]['transition_capacity']!=callers[1]['transition_capacity']
 from Model import dump
 dump(P/'Protection_Tests.csv',tests);dump(P/'Independent_Callers.csv',callers)
 counts['behavioral_protection_claim_rows']=len(tests);counts['nonidentical_common_callers']=len(callers)
 for y in [2035,2040,2055]:
  assert abs(float(by['LATEST_F',y]['terminal_episodes'])-float(by['POP_PROPORTIONAL',y]['terminal_episodes']))>1
 counts['age_vs_total_demand_differences']=3
 # VAT responds to the new medical flow; it is computed in the original tax
 # engine, not added to fiscal revenue a second time.
 vv=[r for r in read('VAT_Medical.csv') if r['case']=='LATEST_F' and int(r['year'])==2055];assert len(vv)==1
 assert abs(float(vv[0]['medical_chain_VAT_response_trn']))>1e-9
 counts['VAT_real_flow_response_nonzero']=True
 for r in rs:
  if r['case'] in ['SQ_FIXED','OLD_EDUCATION_F','OLD_MEDICAL_F']:continue
  for k in ['national_PB_trn','national_debt_trn','national_bond_issue_trn','policy_interest_rate','income_median','gini_actual','engel_actual','births_policy_connected','deaths_policy_connected']:assert r[k]==''
 replayfiles=[]
 if replay:
  with tempfile.TemporaryDirectory(prefix='spe-med-corrected-replay-') as td:
   subprocess.run([sys.executable,str(P/'Model.py'),str(P/'Inputs.json'),'--outdir',td],check=True,stdout=subprocess.DEVNULL)
   for f in sorted(Path(td).iterdir()):
    b=f.read_bytes();assert b==(P/f.name).read_bytes(),f.name
    replayfiles.append(dict(file=f.name,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
 for item in json.loads((P/'Evidence_Reuse.json').read_text())['originals']:
  b=(P/item['saved_file']).read_bytes();assert len(b)==item['size'] and hashlib.sha256(b).hexdigest()==item['sha256']
 result=dict(status='PASS_LOCAL_CHANGED_MODEL',checks=counts,deterministic_replay=replayfiles,reused_Claude_PASS='154440 cells / 16 byte-equal outputs / 37 manifest / 12 dependencies;old-version independent evidence only',limitations='Causal calibration and national budget closure unavailable')
 (P/'Verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--replay',action='store_true');args=ap.parse_args();run(args.replay)
