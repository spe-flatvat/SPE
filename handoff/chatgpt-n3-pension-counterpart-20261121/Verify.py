#!/usr/bin/env python3
"""Numerical regression and independent account identities; implementer checks."""
import csv,json,math,hashlib,argparse
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def read(p):return list(csv.DictReader(p.open()))
def n(r,k):return float(r[k])
def near(a,b):assert math.isclose(float(a),float(b),abs_tol=5e-7,rel_tol=3e-9),(a,b)
def run(out,replay=None):
 A=read(out/'Gap_Annual.csv');by={(r['case'],r['year']):r for r in A};E={(r['case'],r['year']):r for r in read(out/'N3_Engine_Accounts.csv')};tests={};cfg=json.loads((P/'Gap_Inputs.json').read_text());assert len(A)==(14+len(cfg['cases']))*30
 old=read(ROOT/'handoff/chatgpt-n3-model-expansion-20261121/N3_Expansion_Annual.csv');cells=0
 for r in old:
  fresh=by[r['case'],r['year']]
  if fresh['pension_return_trn'] != '0':continue
  for k,v in r.items():
   if v=='':continue
   try:float(v)
   except ValueError:assert v==fresh[k],(r['case'],k,v,fresh[k])
   else:near(v,fresh[k]);cells+=1
 tests['old46_zero_return_annual_numeric_cells']=cells
 # Extra regression of old common and component ledgers, including 29-cell HH.
 ledgers=0
 for file in ['N3_Policy_Accounts.csv','N3_Pension_Accounts.csv','N3_Income_Distribution.csv','N3_Corporate_Accounts.csv','N3_Structural_Interfaces.csv','N3_VAT_Regular_Quantity.csv']:
  o=read(ROOT/'handoff/chatgpt-n3-model-expansion-20261121'/file);new=read(out/file)
  names={r['case'] for r in old};nr=[r for r in new if r['case'] in names]
  assert len(o)==len(nr),(file,len(o),len(nr))
  for a,b in zip(o,nr):
   if by[b['case'],b['year']]['pension_return_trn'] != '0':continue
   for k,v in a.items():
    if v=='':continue
    try:float(v)
    except ValueError:assert v==b[k],(file,k,v,b[k])
    else:near(v,b[k]);ledgers+=1
 tests['old46_zero_return_component_numeric_cells']=ledgers
 for r in A:
  m=E[r['case'],r['year']]
  near(n(m,'tax_macro_trn')+n(r,'VAT_delta_vs_fixed_reference_trn')+n(r,'engine_direct_tax_delta_trn'),r['tax_diagnostic_trn'])
  near(n(m,'tax_diagnostic_trn')-n(m,'expenditure_diagnostic_trn'),m['fiscal_balance_partial_trn'])
  near(n(r,'patient_payment_delta_trn')+n(r,'public_clinical_payment_delta_trn')+n(r,'insurer_clinical_payment_delta_trn'),r['clinical_cost_delta_trn'])
  near(n(r,'policy_government_cost_delta_trn')-n(r,'policy_insurer_cash_delta_trn')-n(r,'policy_tax_delta_trn'),r['policy_budget_unclosed_trn'])
  for k in ['national_PB_trn','national_debt_trn','national_bond_issue_trn','EITC_baseline_trn']:assert r[k]==''
  for k in ['real_gdp_trn','nominal_gdp_trn','capital_total_real_trn','household_consumption_nominal_proxy_trn','population','pension_fund_stock_trn']:assert n(r,k)>=0 and math.isfinite(n(r,k))
 tests['tax_once_payer_identity_open_national_nonnegative_rows']=len(A)
 for r in read(out/'Gap_Common.csv'):
  for k in ['registration_changes_benefits','registration_changes_copay','registration_changes_palliative_priority','unknown_wish_assumed_refusal','treatment_automatically_stopped','active_life_termination']:near(r[k],0)
  assert n(r,'resource_units_used')<=n(r,'transition_capacity')+1e-6
 tests['common_wish_and_capacity_rows']=len(A)
 qrows=read(out/'VAT_Price_Quantity_Income.csv')
 for r in qrows:
  if r['market']=='NON_HH':near(r['quantity'],1);assert r['quantity_change_purchaser_constant_price_trn']=='';continue
  near(n(r,'HH_nominal_spend_trn')-n(r,'seller_net_sales_trn'),r['VAT'])
  near((n(r,'base')+n(r,'old_VAT'))*(n(r,'quantity')-1),r['quantity_change_purchaser_constant_price_trn'])
  cid=r['case'];spec=next((s for s in cfg['cases'] if s['id']==cid),{});elastic=spec.get('quantity_elasticity',0)
  near(max(.7,min(1.3,n(r,'price_ratio')**(-elastic))),r['quantity'])
 tests['VAT_quantity_sales_tax_identities']=len(qrows)
 # Within same pass-through, elasticity must move GDP after tax increase.
 for rate in ['0p6','0p8','1p0']:
  vals=[n(by[c,'2055'],'real_gdp_trn') for c in ['Q_E0_P'+rate,'Q_E0p25_P'+rate,'Q_E0p75_P'+rate]]
  assert vals[0]>vals[1]>vals[2],vals
 for r in A:
  if not r['case'].startswith('Q_E'):continue
  z=[x for x in qrows if x['case']==r['case'] and x['year']==r['year'] and x['market']!='NON_HH']
  near(sum(n(x,'quantity_change_purchaser_constant_price_trn') for x in z),r['quantity_nominal_volume_delta_trn'])
  near(sum(n(x,'price_HH') for x in z),r['quantity_replaced_price_benefit_trn'])
 tests['elasticity_GDP_monotonic_same_price_pass']=3
 for r in read(out/'Partial_Fiscal_Financing.csv'):
  near(n(r,'residual_debt_begin_trn')+n(r,'residual_debt_issue_trn')-n(r,'residual_debt_redemption_trn'),r['residual_debt_end_trn'])
  near(n(r,'residual_asset_begin_trn')-n(r,'residual_asset_draw_trn')+n(r,'residual_asset_addition_trn'),r['residual_asset_end_trn'])
  near(n(r,'residual_debt_issue_trn')+n(r,'residual_asset_draw_trn')-n(r,'residual_debt_redemption_trn')-n(r,'residual_asset_addition_trn'),r['residual_financing_need_trn'])
  near(n(r,'residual_debt_begin_trn')*n(r,'interest_rate_candidate'),r['residual_interest_candidate_trn'])
 tests['partial_financing_stock_flow_rows']=len(read(out/'Partial_Fiscal_Financing.csv'))
 for r in read(out/'Pension_Counterpart.csv'):
  near(n(r,'fund_begin_trn')+n(r,'fund_contribution_trn')+n(r,'fund_return_trn')-n(r,'fund_payout_trn'),r['fund_end_trn'])
  near(n(r,'fund_return_trn')+n(r,'financial_sector_return_counterpart_trn'),0)
  near(n(r,'diverted_existing_contribution_trn'),r['public_contribution_loss_trn']);near(r['HH_fund_contribution_second_deduction_trn'],0)
 tests['pension_stock_flow_counterparty_rows']=len(read(out/'Pension_Counterpart.csv'))
 for r in read(out/'Gap_Semi_Medical.csv'):
  near(r['old_insurer_premium_redirected_trn'],r['old_insurer_claims_redirected_trn']);near(r['old_public_system_net_delta_trn'],0)
  near(n(r,'fund_begin_trn')+n(r,'fund_total_premium_trn')+n(r,'fund_return_trn')-n(r,'fund_claim_payment_trn'),r['fund_end_trn'])
  near(n(r,'fund_return_trn')+n(r,'financial_sector_return_counterpart_trn'),0)
 for y in map(str,range(2026,2056)):
  for cid in ['SEMI_MED_TRANSFER_0p25','SEMI_MED_TRANSFER_0p5']:
   near(by[cid,y]['real_gdp_trn'],by['MED_RATE_INTERPOLATION',y]['real_gdp_trn'])
 tests['semi_medical_no_fabricated_saving_rows']=len(read(out/'Gap_Semi_Medical.csv'))
 for r in read(out/'Gap_Foreign_Bridge.csv'):
  near(n(r,'extra_retained')+n(r,'extra_admitted_N4'),r['extra_end']);near(n(r,'extra_begin')-n(r,'extra_exits'),r['extra_retained'])
  assert n(r,'extra_admitted_N4')<=8000 and r['common_SQ_inflow_changed']=='False'
  if r['baseline_over_cap']=='True':near(r['extra_admitted_N4'],0)
  elif r['cap_trn'] and n(r,'total_metric_trn')>n(r,'cap_trn')+1e-7:near(r['extra_admitted_N4'],0) # do not expel retained workers or cut SQ inflow
 tests['foreign_N4_cap_SQ_nonduplication_rows']=len(read(out/'Gap_Foreign_Bridge.csv'))
 for r in read(out/'Gap_Additional_Accounts.csv'):
  near((.4*n(r,'estate_base_trn')-n(r,'estate_old_trn'))*max(0,min(1,(int(r['year'])-2030+1)/3)),r['estate_delta_trn']) if r['case'].startswith('ESTATE_REPORTED') else None
 tests['estate_reported_only_tax_delta']=90
 for y in range(2026,2056):
  r=by['GIFT_REPORTED_ONLY',str(y)];m=E[r['case'],r['year']]
  near(r['gift_tax_delta_trn'],(.4*2.6761-.3178)*(n(m,'common_deflator')/(600/580))*max(0,min(1,(y-2030+1)/3)))
 tests['gift_standalone_no_estate_overlap']=30
 if replay:
  names={p.name for p in (ROOT/'handoff/chatgpt-n3-gap-closure-20261121').glob('*.csv')} | {'N3_Selftest.json'}
  files=[p for p in out.iterdir() if p.name in names]
  for p in files:assert p.read_bytes()==(replay/p.name).read_bytes(),p.name
  tests['reexecuted_byte_identical_files']=len(files)
 result=dict(status='PASS_IMPLEMENTER_TESTS_NOT_INDEPENDENT_REVIEW',cases=len(A)//30,annual_rows=len(A),new_cases=len(cfg['gap_case_ids']),tests=tests)
 (out/'Checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,default=P);ap.add_argument('--replay',type=Path);a=ap.parse_args();run(a.outdir,a.replay)
