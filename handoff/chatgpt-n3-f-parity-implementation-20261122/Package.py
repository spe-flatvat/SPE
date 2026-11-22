#!/usr/bin/env python3
"""Select individual reproducible annual originals; no archives or compressed files."""
import argparse,csv,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent
MODES=['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rows,keys=None):
 p.parent.mkdir(parents=True,exist_ok=True)
 if keys is None:keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows({k:r.get(k) for k in keys} for r in rows)
def run(source,out):
 out.mkdir(parents=True,exist_ok=True);parity=set(json.loads((P/'Inputs.json').read_text())['parity_cases'])
 metrics=['real_gdp_trn','nominal_gdp_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','tax_diagnostic_trn','macro_cash_DI_proxy_trn','household_direct_price_benefit_trn','household_cash_delta_trn','policy_household_cash_delta_trn','policy_tax_delta_trn','policy_government_cost_delta_trn','policy_insurer_cash_delta_trn','consolidated_partial_balance_proxy_trn','patient_payment_delta_trn','government_cost_delta_trn','insurer_balance_delta_trn','medical_financing_direct_tax_trn','engine_direct_tax_delta_trn','modeled_VAT_trn','VAT_delta_vs_fixed_reference_trn','pension_fund_stock_trn','pension_fund_contribution_trn','pension_fund_payout_trn','pension_return_trn','pension_domestic_income_debit_trn','pension_external_primary_income_trn','pension_additional_VA_nominal_trn','semi_med_fund_asset_trn','foreign_extra_employed','population','public_added_jobs','public_payroll_delta_trn','national_PB_trn','national_debt_trn','national_bond_issue_trn']
 engine=['core_real_gdp_trn','common_deflator','capital_delta_real_trn','capital_previous_real','capital_replacement_investment_real_trn','parity_supply_real_trn','parity_investment_nominal_trn','parity_consumption_target_real_trn','parity_C_previous_real_trn','parity_I_previous_real_trn','parity_depreciation','parity_lambda_C','parity_lambda_I','parity_generic_mpc','parity_capital_yield','parity_capacity_absorption','parity_unmet_real_trn','parity_services_real_trn','parity_nominal_wage_man','parity_core_nominal_trn','parity_carry','C_demand_real_trn','household_consumption_real_proxy_trn','labor_force_population_proxy','tax_macro_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn']
 counts={}
 for mode in MODES:
  d=source/'macro'/mode
  rows=rd(source/('Annual_'+mode+'.csv'));keys=['case','year','mode']+metrics+['macro_'+k for k in engine];dump(out/('Annual_'+mode+'.csv'),rows,keys);counts[mode]=len(rows)
  for name in ['N3_Policy_Accounts.csv','N3_Pension_Accounts.csv','N3_Corporate_Accounts.csv','Gap_Semi_Medical.csv','Dynamic_Base_Audit.csv','Corporate_Funding_Stock.csv','KPI_Events.csv']:
   rs=[r for r in rd(d/name) if r['case'] in parity];dump(out/(mode+'_'+name),rs)
 # Key-year comparison includes full SQ/F deltas, all annual differences in compact form.
 comparisons=rd(source/'SQ_F_N3_Comparison.csv');keys=['mode','case','year','real_gdp_minus_initial580','F_status','N3_policy_status']
 for k in ['real_gdp_trn','nominal_gdp_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','labor_force_population_proxy','tax_diagnostic_trn','macro_cash_DI_proxy_trn']:
  keys += [k,k+'_minus_SQ',k+'_minus_F_FIXED']
 dump(out/'SQ_F_N3_Annual_Comparison.csv',comparisons,keys);dump(out/'Key_Years.csv',[r for r in comparisons if int(r['year']) in [2026,2035,2045,2055]])
 # Individual macro effect rows for parity cases, all 30 years and four ownership candidates.
 dump(out/'Sensitivity.csv',[r for r in rd(source/'Sensitivity.csv') if r['metric'] in ['real_gdp_trn','capital_total_real_trn','tax_diagnostic_trn','macro_cash_DI_proxy_trn','I_policy_real_trn']])
 fiscal=[]
 for f in sorted((source/'fiscal').glob('National_Fiscal_*.csv')):fiscal+=rd(f)
 keys=['mode','scenario','case','year','status','baseline_status','real_gdp_trn','nominal_gdp_trn','CL_PB_candidate_trn','CL_balance_candidate_trn','CL_net_interest_candidate_trn','CL_debt_begin_candidate_trn','CL_debt_end_candidate_trn','CL_cash_assets_end_candidate_trn','CL_new_cash_borrowing_candidate_trn','CL_cash_surplus_debt_redemption_candidate_trn','CL_stock_flow_adjustment_unallocated_trn','insurer_backfill_transfer_trn','insurer_balance_delta_after_backfill_trn','national_PB_trn','national_debt_trn','national_bond_issue_trn','CL_actual_gross_bond_issue_trn','CL_actual_bond_redemption_trn','automatic_macro_debt_interest_feedback']
 dump(out/'Conditional_National_Local_Fiscal.csv',fiscal,keys)
 for name in ['Policy_Implementation_Map.csv','Old79_Changed_Cells.csv','Execution_Metadata.json','Verification.json','Verification.log']:
  shutil.copy(source/name,out/name)
 for name in ['Fiscal_Inputs.json','Official_Fiscal_Baseline_2025_2040.csv']:
  shutil.copy(P.parents[1]/'handoff/chatgpt-national-fiscal-closure-20261121'/name,out/name)
 for mode in MODES:
  for suffix in ['_Execution.log','_Corrected_Execution.log']:
   if (source/(mode+suffix)).exists():shutil.copy(source/(mode+suffix),out/(mode+suffix))
 (out/'Result_Selection.json').write_text(json.dumps(dict(annual_rows_by_mode=counts,full_runtime_outputs='Regenerated by Reproduce.py --outdir; all four annual originals retain macro/sector channels needed for comparison. Detailed new policy/fund/firm/KPI accounts included. Old79 detailed accounts reused by fixed-source reference.',archives=False),indent=2)+'\n')
 print('PACKAGED',sum(counts.values()),'annual rows',len(fiscal),'fiscal rows')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.source,a.outdir)
