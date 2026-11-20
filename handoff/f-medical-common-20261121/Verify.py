#!/usr/bin/env python3
"""Checks new medical bridges plus deterministic replay of generated outputs."""
import argparse,csv,hashlib,json,math,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
def rows(f):return list(csv.DictReader((P/f).open()))
def close(a,b):assert math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-8),(a,b)
def run(replay):
 checks={}
 sys.path.insert(0,str(P))
 from CommonEndOfLife import calculate
 c=json.loads((P/'Inputs.json').read_text())
 d=dict(price_index=1.,population_scale=1.,registry_population=c['registry_population_reference'],clinical_strata=c['clinical_strata'])
 base=c['common_parameters']
 for y in range(2026,2056):
  r=calculate(y,d,base,c['common_financing'])
  assert r['law_passed']==int(y>=2030)
  assert r['national_operation']==int(y>=2035)
  if y<2032:close(r['chosen_transitions'],0.)
  if y==2035:
   close(r['implementation_phase'],1.);assert 0<r['record_adoption']<1
  for k in ['registration_changes_benefits','registration_changes_copay','registration_changes_palliative_priority','active_life_termination']:close(r[k],0.)
  close(r['household_direct_cash_burden_delta_trn'],float(r['patient_payment_delta_trn'])+r['extra_household_cash_burden_trn'])
  close(r['savings_drawdown_delta_trn']+r['borrowing_need_delta_trn'],r['household_direct_cash_burden_delta_trn'])
 # Independent proxy and registration controls; capacity does not depend on either.
 a=calculate(2040,d,{**base,'adoption_target':0},c['common_financing']);b=calculate(2040,d,{**base,'proxy_designation_target':0},c['common_financing'])
 assert a['proxy_designated_episodes']>0 and b['recorded_episodes']>0
 close(a['transition_capacity'],b['transition_capacity'])
 checks['timeline_protection_household_years']=30
 rs=rows('Annual.csv');by={(r['case'],int(r['year'])):r for r in rs}
 for r in rows('Medical_Accounts.csv'):
  close(r['clinical_cost_delta_trn'],sum(float(r[k]) for k in ['patient_payment_delta_trn','public_clinical_payment_delta_trn','insurer_clinical_payment_delta_trn']))
  close(r['transfer_residual_trn'],0.);close(r['government_transfer_cost_delta_trn'],r['insurer_transfer_receipt_delta_trn']);close(r['internal_transfer_consolidated_delta_trn'],0.)
  close(r['hub_staff_cost_included_trn'],float(r['hub_operation_cost_trn'])*.7)
 checks['new_clinical_and_transfer_rows']=len(rows('Medical_Accounts.csv'))
 for y in range(2026,2056):
  for case in ['LATEST_EDUCATION_FIXED','ADDITIONAL_ZERO']:
   if case=='ADDITIONAL_ZERO':
    for k in ['real_gdp_trn','nominal_gdp_trn','macro_cash_DI_proxy_trn','consolidated_partial_balance_proxy_trn']:close(by[case,y][k],by['LATEST_EDUCATION_FIXED',y][k])
  for case in ['OLD_MEDICAL_REMOVED','COMMON_ONLY','COPAY_ONLY','PROVIDER_ONLY','COMMON_F_MEDIUM']:
   r=by[case,y]
   for k in ['old_medical_government_trn','old_medical_insurer_trn','old_medical_hub_capital_trn']:close(r[k],0.)
   close(float(r['government_partial_balance_proxy_trn'])+float(r['insurer_known_change_and_program_balance_trn']),r['consolidated_partial_balance_proxy_trn'])
  a=by['COMMON_F_MEDIUM',y];b=by['BACKFILL_TEST',y]
  close(a['consolidated_partial_balance_proxy_trn'],b['consolidated_partial_balance_proxy_trn']);close(a['real_gdp_trn'],b['real_gdp_trn'])
  for case in ['COMMON_ONLY','COMMON_F_MEDIUM','ANNEX_THIRTY','C_FUNDED']:
   rr=next(r for r in rows('Common_EndOfLife.csv') if r['case']==case and int(r['year'])==y)
   ref=next(r for r in rows('Common_EndOfLife.csv') if r['case']=='COMMON_ONLY' and int(r['year'])==y)
   for k in ['chosen_transitions','total_resource_cost_delta_trn']:close(rr[k],ref[k])
  close(by['C_DIRECT',y]['C_cash_trn'],by['C_FUNDED',y]['C_cash_trn'])
 checks['backfill_cancellation_years']=30;checks['old_medical_zero_year_cases']=150
 for r in rows('VAT_No_DoubleCount.csv'):
  close(r['medical_credit_readded_trn'],0.)
  close(r['new_input_credit_trn'],sum(float(r[k]) for k in ['newly_recovered_to_price_trn','newly_recovered_to_wages_trn','newly_recovered_to_investment_trn','newly_recovered_to_profit_other_trn']))
 checks['VAT_medical_rows']=len(rows('VAT_No_DoubleCount.csv'))
 # Debt schedule / lagged skills remain the existing education calculation; no
 # medical capital is incorrectly added to the education bond stock.
 for r in rows('Education_Preserved.csv'):
  close(r['bond_end_trn'],float(r['bond_begin_trn'])+float(r['bond_issue_trn'])-float(r['bond_redemption_trn']))
 checks['education_bond_identity_rows']=len(rows('Education_Preserved.csv'))
 replayfiles=[]
 if replay:
  with tempfile.TemporaryDirectory(prefix='spe-medical-replay-') as td:
   subprocess.run([sys.executable,str(P/'Model.py'),str(P/'Inputs.json'),'--outdir',td],check=True,stdout=subprocess.DEVNULL)
   for f in sorted(Path(td).iterdir()):
    expected=(P/f.name).read_bytes();actual=f.read_bytes();assert expected==actual,f.name
    replayfiles.append(dict(file=f.name,size=len(actual),sha256=hashlib.sha256(actual).hexdigest()))
 out=dict(status='PASS_LOCAL',checks=checks,replay_outputs=replayfiles,note='No clinical causal validation, national fiscal closure, formal acceptance or canonicalization implied.')
 (P/'Verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--replay',action='store_true');a=ap.parse_args();run(a.replay)
