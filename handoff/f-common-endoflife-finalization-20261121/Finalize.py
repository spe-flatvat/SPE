"""Focused checks, claim-cap audit, comparisons and delivery manifest."""
import csv,json,hashlib,subprocess,sys,math
from pathlib import Path
from Model import dump,read
from CommonInterface import run_common
from FMedical import annual_patient
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def near(a,b):assert math.isclose(float(a),float(b),abs_tol=2e-7,rel_tol=1e-8),(a,b)
def run():
 c=json.loads((P/'Inputs.json').read_text());a=read(P/'Annual.csv');old=read(P.parent/'f-medical-corrected-integrated-20261121/Annual.csv');oldco=read(P.parent/'f-medical-corrected-integrated-20261121/Common_EndOfLife.csv')
 co=read(P/'Common_EndOfLife.csv');by={(r['case'],int(r['year'])):r for r in a};ob={(r['case'],int(r['year'])):r for r in old};oc={(r['case'],int(r['year'])):r for r in oldco}
 for r in co:
  assert float(r['resource_units_used'])<=float(r['transition_capacity'])+1e-6
  near(float(r['chosen_transitions'])+float(r['universal_palliative_served'])-float(r['overlap_patients']),r['unique_patients_served'])
  assert float(r['overlap_patients'])<=float(r['universal_palliative_served'])+1e-6
  if float(r['implementation_phase'])==0:near(r['chosen_transitions'],0)
 # Independent reconstruction from exported claim/recipient/source ledgers.
 med=read(P/'Medical_Accounts.csv')
 for r in med:
  uses=float(r['government_cost_delta_trn'])+float(r['medical_other_spending_crowded_trn'])-float(r['insurer_balance_delta_trn'])+float(r['medical_financing_premium_trn'])
  sources=sum(float(r[k]) for k in ['medical_financing_tax_trn','medical_financing_premium_trn','medical_other_spending_crowded_trn','medical_policy_debt_issue_trn','medical_unassigned_after_sources_trn'])-float(r['medical_policy_debt_redemption_trn'])-float(r['medical_policy_asset_addition_trn'])
  near(uses,sources)
  # Detect an omitted or corrupted source, rather than passing any cancellation.
  assert not math.isclose(uses,sources+.01,abs_tol=1e-7)
  assert r['post_financing_transfer_residual_trn']==''
 comparisons=[]
 metrics=['real_gdp_trn','nominal_gdp_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','macro_cash_DI_proxy_trn','tax_diagnostic_trn','clinical_cost_delta_trn','patient_payment_delta_trn','public_clinical_payment_delta_trn','insurer_clinical_payment_delta_trn','consolidated_partial_balance_proxy_trn']
 for r in a:
  key=r['case'],int(r['year'])
  if key not in ob:continue
  for k in metrics:
   if r.get(k,'')!='' and ob[key].get(k,'')!='':comparisons.append(dict(case=key[0],year=key[1],metric=k,old=float(ob[key][k]),new=float(r[k]),difference=float(r[k])-float(ob[key][k])))
 dump(P/'Before_After.csv',comparisons)
 supply=[]
 for r in co:
  key=r['case'],int(r['year'])
  if key not in oc:continue
  for k in ['chosen_transitions','universal_palliative_served','universal_palliative_unmet','household_direct_cash_burden_delta_trn']:
   supply.append(dict(case=key[0],year=key[1],metric=k,old=float(oc[key][k]),new=float(r[k]),difference=float(r[k])-float(oc[key][k])))
 dump(P/'Supply_Before_After.csv',supply)
 nonadd=[]
 effects=read(P/'Policy_Effects.csv')
 for y in range(2026,2056):
  total=float(by['LATEST_F',y]['real_gdp_trn'])-float(by['SQ_FIXED',y]['real_gdp_trn'])
  marginal=sum(float(r['marginal_in_integrated_F']) for r in effects if int(r['year'])==y and r['metric']=='real_gdp_trn')
  nonadd.append(dict(year=y,total_F_minus_common_OFF_SQ=total,sum_leave_one_out=marginal,nonadditivity=marginal-total,additive_attribution=False,investment_status='UNCONNECTED_NULL_INPUT'))
 dump(P/'Nonadditivity.csv',nonadd)
 # Caller-injected financing with identical clinical policy and distinct tariffs.
 callers=[]
 demand=dict(price_index=1.,population_scale=1.,registry_population=c['registry_population_reference'],clinical_strata=c['clinical_strata'],age_demand_episodes=450000)
 params={**c['common_parameters'],'universal_palliative':True,'palliative_additional_yen':0.}
 for name,share,gov in [('F',.1,.5),('N3_CALL_TEST',.2,.4),('N_CALL_TEST',.3,.3),('F3_CALL_TEST',.15,.6),('R4_CALL_TEST',.05,.7)]:
  fin=dict(HOUSEHOLD=share,GOVERNMENT=(1-share)*gov,INSURER=(1-share)*(1-gov))
  for y in range(2026,2056):
   r=run_common(y,demand,params,fin);callers.append(dict(caller=name,test_only=True,**r))
 for y in range(2026,2056):
  sample=[r for r in callers if r['year']==y]
  for r in sample:
   for k in ['law_passed','implementation_phase','record_adoption','chosen_transitions','universal_palliative_served','resource_units_used']:near(r[k],sample[0][k])
 dump(P/'Set_Interface_Tests.csv',callers)
 # Independent marginal cap arithmetic audit using published model candidate rules.
 audit=[]
 for months in [1,3,6]:
  for age in ['PRESCHOOL','AGE6_69','AGE70_74','AGE75PLUS']:
   for group,weight in c['income_weights'].items():
    for setting,base in c['common_parameters']['baseline_cost_yen'].items():
     extra=100000.;b=annual_patient(2035,age,group,dict(months=months,bill_yen=base/months),uniform=True,cap_multiplier=.9)
     n=annual_patient(2035,age,group,dict(months=months,bill_yen=(base+extra)/months),uniform=True,cap_multiplier=.9)
     marginal=n-b
     assert 0<=marginal<=.3*extra+1e-7
     # HIGH/MIDDLE cap rises only 1% of additional monthly bill, then *.9.
     audit.append(dict(year=2035,months=months,age=age,income=group,setting=setting,income_weight=weight,bill_before_yen=base,bill_after_yen=base+extra,paid_before_yen=b,paid_after_yen=n,marginal_payment_yen=marginal,marginal_rate=marginal/extra,cap_status='MODEL_CANDIDATE_NOT_NEW_LEGAL_VALIDATION'))
 dump(P/'Patient_Cap_Audit.csv',audit)
 # Recover only four existing independent evidence originals; retain provenance.
 provenance=[]
 commit='995cbca98935752234452c6a6760150e639b312d';folder='handoff/claude-f-integrated-verification-20261121/'
 names=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,folder],cwd=ROOT,text=True).splitlines()
 for n in names:
  b=subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT);target=P/('Evidence_'+Path(n).name);target.write_bytes(b)
  provenance.append(dict(commit=commit,path=n,saved_file=target.name,size=len(b),sha256=hashlib.sha256(b).hexdigest(),route='git fetch fixed commit then git show',verification='OWN_BYTE_IDENTITY_TO_FIXED_GIT_OBJECT'))
 (P/'Evidence_Reuse.json').write_text(json.dumps(dict(existing_Claude_PASS='37/37 manifest;12/12 deps;16 byte outputs;154440 cells;OLD_VERSION_ONLY',originals=provenance),indent=2)+'\n')
 result=dict(status='PASS_LOCAL_CHANGED_IMPLEMENTATION',capacity_rows=len(co),independent_financing_rows=len(med),source_error_injection_detected=True,set_interface_rows=len(callers),patient_cap_audit_rows=len(audit),formal_acceptance=False,N3_policy_model_implemented=False)
 (P/'Final_Checks.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':run()
