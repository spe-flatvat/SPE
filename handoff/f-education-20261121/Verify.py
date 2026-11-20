#!/usr/bin/env python3
"""Focused tests of education cohorts, transfers, debt and causal timing."""
import csv,hashlib,importlib.util,json,math,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
def eq(a,b):assert math.isclose(a,b,abs_tol=2e-7,rel_tol=3e-10),(a,b)
def read(n):return list(csv.DictReader((P/n).open()))
def n(r,k):return float(r[k])
c=json.loads((P/'Inputs.json').read_text());s=c['defaults'];a={(r['case'],int(r['year'])):r for r in read('Annual.csv')};e=read('Education.csv');checks=[]
for r in e:
 eq(n(r,'gross_education_spend_trn'),sum(n(r,k) for k in ['education_service_trn','education_facility_trn','scholarship_grant_trn']))
 eq(n(r,'net_additional_education_spend_trn'),n(r,'gross_education_spend_trn')-n(r,'reallocated_education_budget_trn'))
 eq(n(r,'bond_end_trn'),n(r,'bond_begin_trn')+n(r,'bond_issue_trn')-n(r,'bond_redemption_trn'))
 eq(n(r,'scholarship_grant_trn'),sum(n(r,k) for k in ['scholarship_HH_consumption_trn','scholarship_saving_trn','scholarship_loan_displacement_trn']))
 eq(n(r,'scholarship_HH_consumption_trn')+n(r,'scholarship_cash_saving_plus_debt_reduction_trn'),n(r,'scholarship_grant_trn'))
 eq(n(r,'training_credit_trn'),n(r,'credit_on_existing_trn')+n(r,'credit_on_added_trn'))
 eq(n(r,'additional_training_trn'),n(r,'eligible_existing_training_trn')*next((q.get('training_price_response',s['training_price_response']) for q in c['cases'] if q['id']==r['case']),s['training_price_response'])*n(r,'effective_training_credit_rate')/(1-n(r,'effective_training_credit_rate')))
 eq(n(r,'firm_training_cash_delta_trn'),n(r,'training_credit_trn')-n(r,'additional_training_trn'))
 eq(n(r,'education_total_cost_trn'),n(r,'net_additional_education_spend_trn')+n(r,'training_credit_trn')+n(r,'bond_interest_trn'))
 for k in ['full_national_bond_issue_trn','national_PB_trn','actual_enrolment_rate','actual_completion_rate']:assert r[k]==''
checks+=['education spending composition, no financing double count','grant cash-consumption-saving-borrowing uses','existing and induced training tax support separated','policy-specific bond stock-flow and interest cost scope','national debt/PB and measured causal rates blank']
for y in range(2026,2056):
 legacy=a['LEGACY',y];zero=a['LEGACY_EXTRA_ZERO',y];new=a['COMBINED',y];off=a['REPLACED_ZERO',y]
 for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','household_disposable_nominal_trn']:eq(n(legacy,k),n(zero,k))
 for name in ['EDUCATION_ONLY','SCHOLARSHIP_ONLY','TRAINING_ONLY','COMBINED','LOW','HIGH','TRIGGER_AUTO']:
  r=a[name,y]
  eq(n(r,'legacy_education_budget_trn')+n(r,'legacy_scholarship_trn')+n(r,'legacy_education_H_stock_trn')+n(r,'old_education_level_GDP_trn'),0.)
  eq(n(r,'employed_headcount_preserved_proxy'),n(off,'employed_headcount_preserved_proxy'))
  assert math.isclose(n(r,'labor_force_population_proxy')-n(off,'labor_force_population_proxy'),n(r,'education_effective_labor_added'),abs_tol=.0002,rel_tol=1e-9)  # 12-significant-digit CSV headcount rounding
  eq(n(r,'consolidated_partial_balance_proxy_trn'),n(r,'government_partial_balance_proxy_trn')+n(r,'insurer_known_change_and_program_balance_trn'))
  if y>2026:eq(n(r,'capital_delta_real_trn'),.95*n(r,'capital_previous_real_trn')+n(r,'I_policy_real_trn'))
 eq(n(new,'real_gdp_trn'),n(a['NO_BOND',y],'real_gdp_trn'))
 eq(n(a['ALL_BORROWING_REPLACEMENT',y],'scholarship_HH_consumption_trn'),0.)
 eq(n(a['ZERO_TRAINING_RESPONSE',y],'training_episodes'),0.)
 eq(n(a['ZERO_CAUSAL_RETURNS',y],'productivity_gain'),0.)
 if y>=2030:assert n(a['ZERO_TRAINING_RESPONSE',y],'credit_on_existing_trn')>0
 if y<2029:eq(n(a['TRAINING_ONLY',y],'matured_skill_worker_equivalents'),0.)
 if y<2032:eq(n(a['SCHOLARSHIP_ONLY',y],'realized_additional_completions'),0.)
 if y<2036:eq(n(a['EDUCATION_ONLY',y],'matured_skill_worker_equivalents'),0.)
 assert n(a['TRIGGER_AT_THRESHOLD',y],'triggered')==0
 if y>=2035:assert n(a['TRIGGER_FORCED',y],'triggered')==1
 if y>=2035:
  r=a['TRIGGER_AUTO',y];g=n(a['TRIGGER_AUTO',2034],'real_growth_pct')/100;eq(n(r,'trigger_assessed_growth'),g);eq(n(r,'triggered'),int(g<.012))
 if y>=2036:
  r=a['TRIGGER_2035_GROWTH_2036',y];g=n(a['TRIGGER_2035_GROWTH_2036',2035],'real_growth_pct')/100;eq(n(r,'trigger_assessed_growth'),g);eq(n(r,'triggered'),int(g<.012))
checks+=['legacy plus additional-zero equality','old budget/scholarship/H-stock removed before replacement','no education job headcount double counting','effective labour plus skills minus time identity','inherited capital identity','bond financing has no direct GDP demand','loan displacement alone has no consumption stimulus','tax subsidy without additional training has no new participants','zero causal return control','separate 1/4/8-year training/scholar/school lags','strict trigger threshold and lagged endogenous assessment']
# Independent small debt example, not just a CSV identity: one 1trn issue in
# 2028, 2% interest, first repayment after five years, twenty equal instalments.
spec=importlib.util.spec_from_file_location('edu',P/'Model.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
t=m.Education(c,{**s,'E':True,'S':False,'T':False,'annual_envelope_trn':1.,'facility_share':0.,'service_share':1.,'supply_capacity':1.,'reallocation_share':0.,'ramp_years':1},[1.]*30)
results=[]
for y in range(2026,2056):
 if y==2029:t.s['annual_envelope_trn']=0.
 results.append(t.step(y,[],1000000.))
by={r['year']:r for r in results};eq(by[2028]['bond_issue_trn'],1.);eq(by[2028]['bond_interest_trn'],.01);eq(by[2029]['bond_interest_trn'],.02);eq(by[2033]['bond_redemption_trn'],.05);eq(by[2033]['bond_end_trn'],.95);eq(by[2052]['bond_end_trn'],0.)
checks+=['hand debt cohort example: issue, half-year interest, grace, 20 repayments']
for r in read('Interactions.csv'):eq(n(r,'combined_effect'),n(r,'sum_of_single_effects')+n(r,'interaction'))
checks+=['single/combined interaction decomposition']
replay=[]
with tempfile.TemporaryDirectory(prefix='spe_education_') as td:
 subprocess.run([sys.executable,str(P/'Model.py'),str(P/'Inputs.json'),'--outdir',td],check=True,stdout=subprocess.DEVNULL)
 for p in sorted(Path(td).iterdir()):
  b=p.read_bytes();assert b==(P/p.name).read_bytes(),p.name
  replay.append(dict(file=p.name,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
checks+=['fresh numerical output byte replay']
print(json.dumps(dict(status='PASS',checks=checks,replayed_outputs=replay),ensure_ascii=False,indent=2))
