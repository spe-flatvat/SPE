#!/usr/bin/env python3
"""Implementation checks on actual annual output; not independent review."""
import argparse,csv,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
MODES=['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']
def rd(p):return list(csv.DictReader(p.open()))
def n(r,k):
 v=r.get(k);return None if v in [None,''] else float(v)
def near(a,b):return math.isclose(a,b,abs_tol=2e-7,rel_tol=3e-10)
def run(out):
 counts={};fail=[];samples=[]
 def req(ok,name,detail=''):
  counts[name]=counts.get(name,0)+1
  if not ok:fail.append(dict(check=name,detail=str(detail)))
 expected=14+len(json.loads((P/'Inputs.json').read_text())['cases'])
 for mode in MODES:
  d=out/'macro'/mode;rs=rd(d/'Gap_Annual.csv');es=rd(d/'N3_Engine_Accounts.csv');eidx={(r['case'],r['year']):r for r in es};idx={(r['case'],r['year']):r for r in rs}
  req(len(rs)==expected*30 and len(eidx)==expected*30,'annual_count',mode)
  for a in rs:
   e=eidx[a['case'],a['year']];y=int(a['year']);tag=(mode,a['case'],y);delta=n(e,'capital_delta_real_trn');I=n(e,'I_policy_real_trn');prev=n(e,'capital_previous_real');dep=n(e,'parity_depreciation')
   req(near(n(e,'real_gdp_trn')-n(e,'core_real_gdp_trn'),n(e,'parity_capacity_absorption')*n(e,'parity_supply_real_trn')+n(e,'C_demand_real_trn')+I+n(e,'parity_services_real_trn')-n(e,'parity_unmet_real_trn')),'GDP_decomposition',tag)
   if y>2026:
    req(near(delta,(1-dep)*prev+I),'incremental_capital_identity',tag)
    req(near(n(e,'C_demand_real_trn'),(1-n(e,'parity_lambda_C'))*n(e,'parity_C_previous_real_trn')+n(e,'parity_lambda_C')*n(e,'parity_consumption_target_real_trn')),'C_persistence_identity',tag)
    req(near(I,(1-n(e,'parity_lambda_I'))*n(e,'parity_I_previous_real_trn')+n(e,'parity_lambda_I')*n(e,'parity_investment_nominal_trn')/n(e,'common_deflator')),'I_persistence_identity',tag)
    req(near(n(e,'parity_supply_real_trn'),n(e,'parity_capital_yield')*(1-dep)*prev+n(e,'parity_education_supply_real_trn')),'lagged_supply_identity',tag)
    if e['parity_carry']=='True':
     ep=eidx[a['case'],str(y-1)]
     req(near(prev,n(ep,'capital_delta_real_trn')),'prior_capital_carried',tag)
     req(near(n(e,'capital_total_real_trn')-(1-dep)*n(ep,'capital_total_real_trn'),n(e,'capital_replacement_investment_real_trn')+I),'total_capital_identity',tag)
   req(near(n(a,'tax_diagnostic_trn'),n(e,'tax_macro_trn')+n(a,'VAT_delta_vs_fixed_reference_trn')+n(a,'engine_direct_tax_delta_trn')),'tax_VAT_direct_once',tag)
   req(near(n(e,'fiscal_balance_partial_trn'),n(e,'tax_diagnostic_trn')-n(e,'expenditure_diagnostic_trn')),'government_balance_identity',tag)
   req(near(n(a,'engine_direct_tax_delta_trn'),n(a,'medical_financing_direct_tax_trn')+n(a,'policy_tax_delta_trn')),'policy_direct_once',tag)
   req(near(n(a,'household_cash_delta_trn'),n(a,'medical_only_household_cash_delta_trn')+n(a,'policy_household_cash_delta_trn')),'household_cash_once',tag)
   req(near(n(a,'pension_second_contribution_charge_trn'),0.) and near(n(a,'pension_direct_GDP_subtraction_trn'),0.),'pension_no_second_premium_or_direct_GDP_debit',tag)
   req(a.get('national_PB_trn','')=='' and a.get('national_debt_trn','')=='' and a.get('national_bond_issue_trn','')=='','national_values_remain_null',tag)
  for r in rd(d/'N3_Pension_Accounts.csv'):
   req(near(n(r,'fund_end_trn'),n(r,'fund_begin_trn')+n(r,'fund_contribution_trn')+n(r,'fund_return_trn')-n(r,'fund_payout_trn')),'pension_stock_flow',(mode,r['case'],r['year']))
  for r in rd(d/'Corporate_Funding_Stock.csv'):
   req(near(n(r,'cash_end_trn')-n(r,'cash_begin_trn'),n(r,'source_tax_saving_trn')-n(r,'dividend_paid_trn')-n(r,'realized_investment_nominal_trn')),'corporate_funding_stock',(mode,r['case'],r['year']))
  for r in rd(d/'Gap_Semi_Medical.csv'):
   req(near(n(r,'old_public_system_net_delta_trn'),0.) and near(n(r,'new_public_saving_trn'),0.),'semi_medical_internal_transfer_neutral',(mode,r['case'],r['year']))
   req(near(n(r,'fund_end_trn'),n(r,'fund_begin_trn')+n(r,'fund_return_trn')+n(r,'fund_reserve_premium_trn')),'semi_medical_reserve_stock',(mode,r['case'],r['year']))
  for r in rd(d/'Dynamic_Base_Audit.csv'):
   req(n(r,'new_household_income_added_trn')==0. and n(r,'new_corporate_profit_added_trn')==0.,'replace_base_no_duplicate_income',(mode,r['case'],r['year']))
   if r['enabled']=='True':
    y=int(r['year'])
    if y>2026:
     prev=eidx[r['case'],str(y-1)];sq=eidx['SQ_COMMON_ON',str(y-1)]
     req(near(n(r,'wage_base_factor'),n(prev,'parity_nominal_wage_man')/n(sq,'parity_nominal_wage_man')),'dynamic_base_lagged_wage',(mode,r['case'],y))
  events={(r['case'],r['year']):r for r in rd(d/'KPI_Events.csv')}
  for cid in ['PARITY_CONNECTED_CANDIDATE','PARITY_KPI_HIGH_THRESHOLD']:
   incomes=[]
   for yr in ['2033','2034']:
    er=eidx[cid,yr];ar=idx[cid,yr]
    vat_household=n(er,'parity_household_cash_trn')-n(ar,'household_cash_delta_trn')
    incomes.append((n(er,'household_disposable_nominal_trn')-vat_household)/n(er,'common_deflator')/n(ar,'population'))
   req(near(n(events[cid,'2035'],'previous_income_growth_pct'),100*(incomes[1]/incomes[0]-1)),'KPI_uses_actual_lagged_income_without_future_data',(mode,cid))
  req(events['PARITY_GINI_SIGNAL','2035']['gini_relief_trigger']=='True' and events['PARITY_GINI_SIGNAL','2036']['gini_relief_active_candidate']=='False','external_Gini_candidate_duration',mode)
  req(events['PARITY_INSURANCE_STRESS','2035']['insurance_underperformance_signal']=='True','insurance_signal_without_invented_productivity',mode)
  req(events['PARITY_KPI_HIGH_THRESHOLD','2035']['vat_frozen']=='True' and n(idx['PARITY_KPI_HIGH_THRESHOLD','2040'],'standard_rate')==.15,'income_KPI_positive_trigger_freezes_VAT',mode)
  req(events['PARITY_KPI_LOW_THRESHOLD','2035']['vat_frozen']=='False','income_KPI_no_false_trigger',mode)
  for r in events.values():
   if r['case'] in ['PARITY_CONNECTED_CANDIDATE','PARITY_KPI_LOW_THRESHOLD'] and int(r['year'])<2035:req(r['vat_frozen']=='False','KPI_no_early_freeze',(mode,r['case'],r['year']))
  # Sensitivity responses must affect actual 2055 states, not just labels.
  base=idx['PARITY_CONNECTED_CANDIDATE','2055'];be=eidx['PARITY_CONNECTED_CANDIDATE','2055']
  for name,metric in [('MPC_LOW','real_gdp_trn'),('MPC_HIGH','real_gdp_trn'),('DEPRECIATION_LOW','capital_total_real_trn'),('DEPRECIATION_HIGH','capital_total_real_trn'),('INVESTMENT_START2038','capital_total_real_trn'),('INVESTMENT_RESPONSE0','capital_total_real_trn'),('INVESTMENT_RESPONSE60','capital_total_real_trn'),('LABOR_ADD100K','real_gdp_trn'),('NO_CARRY','real_gdp_trn'),('FIXED_BASES','real_gdp_trn')]:
   r=idx['PARITY_'+name,'2055'];delta=n(r,metric)-n(base,metric);req(abs(delta)>1e-7,'actual_sensitivity_'+name,mode);samples.append(dict(mode=mode,case='PARITY_'+name,metric=metric,year=2055,delta=delta))
  req(n(eidx['PARITY_LABOR_ADD100K','2055'],'labor_force_population_proxy')>n(eidx['PARITY_LABOR_ZERO','2055'],'labor_force_population_proxy'),'new_jobs_labor_not_regularization',mode)
  req(all(n(idx['SQ_COMMON_ON',str(y)],'real_gdp_trn')==float(next(r for r in rd(ROOT/'handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Annual.csv') if r['case']=='SQ_COMMON_ON' and r['year']==str(y))['real_gdp_trn']) for y in range(2026,2056)),'shared_SQ_unchanged',mode)
 meta=json.loads((out/'Execution_Metadata.json').read_text());req(meta['legacy79_changed_cells']==0,'old79_no_unintended_changes',meta['legacy79_changed_cells'])
 for f in (out/'fiscal').glob('National_Fiscal_*.csv'):
  for r in rd(f):
   if n(r,'CL_PB_candidate_trn') is not None:
    req(near(n(r,'CL_balance_candidate_trn'),n(r,'CL_PB_candidate_trn')-n(r,'CL_net_interest_candidate_trn')),'fiscal_PB_interest_balance',(f.name,r['case'],r['year']))
    req(near(n(r,'CL_debt_end_candidate_trn'),n(r,'CL_debt_begin_candidate_trn')+n(r,'CL_new_cash_borrowing_candidate_trn')-n(r,'CL_cash_surplus_debt_redemption_candidate_trn')+n(r,'CL_stock_flow_adjustment_unallocated_trn')),'fiscal_debt_identity',(f.name,r['case'],r['year']))
   req(r['national_PB_trn']=='' and r['national_debt_trn']=='' and r['national_bond_issue_trn']=='','fiscal_general_government_null',(f.name,r['case'],r['year']))
 for r in rd(out/'fiscal/Transfer_Audit.csv'):
  req(near(n(r,'government_payment_trn'),n(r,'insurer_receipt_trn')) and near(n(r,'internal_transfer_consolidated_trn'),0.),'government_insurer_internal_transfer_neutral',(r['case'],r['year']))
 result=dict(status='PASS_IMPLEMENTER_CHECKS' if not fail else 'FAIL',independent_verification=False,checks=sum(counts.values()),checks_by_family=counts,failed=len(fail),failures=fail[:100],sensitivity_examples=samples)
 (out/'Verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['checks'],'failures',len(fail));assert not fail,fail[:3]
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--outdir',type=Path,required=True);run(p.parse_args().outdir)
