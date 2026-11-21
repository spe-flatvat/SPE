#!/usr/bin/env python3
"""Build comparisons and partial financing bridges from solved paths; no GDP edits."""
import csv,json,math,argparse
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def read(p):return list(csv.DictReader(p.open()))
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def num(r,k):return float(r[k]) if r.get(k) not in [None,''] else None
def main(out):
 A=read(out/'Gap_Annual.csv');E=read(out/'N3_Engine_Accounts.csv');by={(r['case'],r['year']):r for r in A};eng={(r['case'],r['year']):r for r in E};cfg=json.loads((P/'Gap_Inputs.json').read_text());spec={r['id']:r for r in cfg['cases']}
 F={r['year']:r for r in read(ROOT/'handoff/f-common-endoflife-finalization-20261121/Annual.csv') if r['case']=='LATEST_F'}
 metrics=['real_gdp_trn','nominal_gdp_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','tax_diagnostic_trn','modeled_VAT_trn','macro_cash_DI_proxy_trn','population','consolidated_partial_balance_proxy_trn','policy_tax_delta_trn','labour_business_flat30_tax_delta_trn','household_financial20_tax_delta_trn','estate_tax_delta_trn','gift_tax_delta_trn','corporate_tax_delta_trn','pension_benefit_delta_trn','pension_fund_stock_trn','foreign_extra_population_bridge']
 C=[];B=[];V=[];S=[]
 for r in A:
  cid=r['case'];y=r['year'];m=eng[cid,y];sq=by['SQ_COMMON_ON',y];sm=eng['SQ_COMMON_ON',y];q=dict(case=cid,year=y,scope='PARTIAL_CONNECTED_CANDIDATES_NOT_CAUSAL_PACKAGE_RANKING')
  for k in metrics:
   x=num(r,k);q[k]=x
   for name,ref in [('SQ',sq),('F',F[y])]:
    b=num(ref,k);q[k+'_minus_'+name]=None if x is None or b is None else x-b
  q.update(effective_labor_core=num(m,'labor_force_population_proxy'),effective_labor_plus_foreign_bridge=num(m,'labor_force_population_proxy')+num(r,'foreign_effective_labor_bridge'),population_plus_foreign_bridge=num(r,'population')+num(r,'foreign_extra_population_bridge'))
  C.append(q)
  for rate in [0.,.02,.04]:
   # Financing scenario covers ONLY incremental government proxy gap left after
   # the already modeled medical financial source. It is not national debt/PB.
   prev=next((b for b in reversed(B) if b['case']==cid and b['interest_rate_candidate']==rate),None)
   debt=prev['residual_debt_end_trn'] if prev else 0.;assets=prev['residual_asset_end_trn'] if prev else 0.;interest=debt*rate
   gov=num(m,'fiscal_balance_partial_trn');delta=gov-num(sm,'fiscal_balance_partial_trn')
   medsource=num(r,'medical_policy_net_financial_source_trn')-num(sq,'medical_policy_net_financial_source_trn')
   need=-delta-medsource+interest
   draw=min(assets,max(need,0.));issue=max(0.,need-draw);surplus=max(-need,0.);redemption=min(debt,surplus);addition=max(surplus-redemption,0.)
   B.append(dict(case=cid,year=y,status='PARTIAL_CLOSURE_INCREMENTAL_UNALLOCATED_GOVERNMENT_ONLY',interest_rate_candidate=rate,tax_macro_proxy_trn=num(m,'tax_macro_trn'),VAT_policy_delta_proxy_trn=num(r,'VAT_delta_vs_fixed_reference_trn'),policy_direct_tax_delta_trn=num(r,'policy_tax_delta_trn'),medical_financing_tax_trn=num(r,'medical_financing_direct_tax_trn'),tax_diagnostic_proxy_trn=num(m,'tax_diagnostic_trn'),tax_boundary_residual_trn=num(m,'tax_diagnostic_trn')-num(r,'modeled_VAT_trn'),government_expense_proxy_trn=num(m,'expenditure_diagnostic_trn'),government_balance_proxy_trn=gov,government_balance_delta_vs_SQ_trn=delta,government_primary_balance_partial_proxy_trn=gov+num(r,'medical_policy_interest_trn'),insurer_known_medical_delta_trn=num(r,'medical_only_insurer_balance_delta_trn'),insurer_N3_components_delta_trn=num(r,'policy_insurer_cash_delta_trn'),consolidated_partial_balance_proxy_trn=num(r,'consolidated_partial_balance_proxy_trn'),medical_existing_net_financial_source_delta_trn=medsource,residual_debt_begin_trn=debt,residual_asset_begin_trn=assets,residual_interest_candidate_trn=interest,residual_financing_need_trn=need,residual_asset_draw_trn=draw,residual_debt_issue_trn=issue,residual_debt_redemption_trn=redemption,residual_asset_addition_trn=addition,residual_debt_end_trn=debt+issue-redemption,residual_asset_end_trn=assets-draw+addition,medical_debt_stock_partial_trn=num(r,'medical_policy_debt_stock_trn'),medical_asset_stock_partial_trn=num(r,'medical_policy_financial_asset_stock_trn'),pension_fund_assets_trn=num(r,'pension_fund_stock_trn'),semi_med_fund_assets_trn=num(r,'semi_med_fund_asset_trn'),national_PB_trn=None,national_debt_trn=None,national_bond_issue_trn=None,local_central_allocation='OPEN',unallocated_foreign_costs_trn=num(r,'foreign_cost_unallocated_trn')))
  if cid in cfg['gap_case_ids']:
   S.append(dict(case=cid,year=y,quantity_elasticity=spec[cid].get('quantity_elasticity',0),rate_pass=spec[cid].get('rate_pass',.8),source_shares=str(spec[cid].get('income_source_shares','LEGACY')),real_gdp_trn=num(r,'real_gdp_trn'),GDP_minus_SQ=num(r,'real_gdp_trn')-num(sq,'real_gdp_trn'),tax_delta_proxy_trn=num(r,'policy_tax_delta_trn'),estate_delta_trn=num(r,'estate_tax_delta_trn'),quantity_target_delta_nominal_trn=num(r,'quantity_nominal_volume_delta_trn'),replaced_regular_price_benefit_trn=num(r,'quantity_replaced_price_benefit_trn')))
 for r in read(out/'N3_VAT_Regular_Quantity.csv'):
  cid=r['case'];y=r['year'];annual=by[cid,y];b=num(r,'base');ov=num(r,'old_VAT');q=num(r,'quantity');hh=r['market'].startswith('HH_');gross0=b+ov;pricegross=gross0-num(r,'price_HH') if hh else None;rate=num(annual,'food_rate' if r['market']=='HH_FOOD' else 'standard_rate')
  # HH final expenditure = net seller receipts + actual VAT exactly.
  expenditure=pricegross*q if hh else None;seller=expenditure-num(r,'VAT') if hh else None
  V.append(dict(**r,price_ratio=pricegross/gross0 if hh and gross0 else None,quantity_change_producer_constant_price_trn=b*(q-1) if hh else None,quantity_change_purchaser_constant_price_trn=gross0*(q-1) if hh else None,HH_nominal_spend_trn=expenditure,seller_net_sales_trn=seller,seller_net_sales_delta_trn=seller-b if hh else None,annual_macro_consumption_nominal_proxy_trn=annual['household_consumption_nominal_proxy_trn'],annual_GDP_real_trn=annual['real_gdp_trn'],annual_VAT_trn=annual['modeled_VAT_trn'],quantity_link_mode=annual['quantity_channel_mode'],deflator=eng[cid,y]['common_deflator']))
 interactions=[]
 for combined,a,b,base,label in [('CONNECTED_Q_ESTATE','CONNECTED_Q','ESTATE_REPORTED_MPC0p1','SQ_COMMON_ON','Q_PACKAGE_x_ESTATE'),('CONNECTED_Q','CONNECTED_Q_NO_FLAT','FLAT_HH_SURVEY','SQ_COMMON_ON','PACKAGE_x_FLAT_TIMING_DIFF_DIAGNOSTIC'),('CONNECTED_Q_ESTATE_SEMI','CONNECTED_Q_ESTATE','SEMI_MED_TRANSFER_0p5','N3_MED_50_CAP_SAME','SEMI_RECLASSIFICATION_CONTROL')]:
  for year in range(2026,2056):
   y=str(year)
   for k in ['real_gdp_trn','tax_diagnostic_trn','household_consumption_nominal_proxy_trn']:
    z=[num(by[x,y],k) for x in [combined,a,b,base]]
    interactions.append(dict(test=label,year=y,metric=k,combined_case=combined,a_case=a,b_case=b,base_case=base,combined_minus_base=z[0]-z[3],a_minus_base=z[1]-z[3],b_minus_base=z[2]-z[3],difference_in_differences=z[0]-z[1]-z[2]+z[3],attribution=False))
 # Isolated component deletion marginals retain identical timing.
 for alt in ['CONNECTED_Q_NO_FLAT','CONNECTED_Q_NO_PENSION','CONNECTED_Q_LOW_LABOUR']:
  for y in map(str,range(2026,2056)):
   for k in ['real_gdp_trn','tax_diagnostic_trn']:
    interactions.append(dict(test='MATCHED_PACKAGE_CHANGE',year=y,metric=k,combined_case='CONNECTED_Q',a_case=alt,matched_difference=num(by['CONNECTED_Q',y],k)-num(by[alt,y],k),attribution=False))
 dump(out/'F_Reference_Annual.csv',[dict(case='LATEST_F_FIXED_REFERENCE',year=y,reference_commit='ff6210061615105de9a0d64767c256796be80ed2',**{k:r.get(k) for k in metrics}) for y,r in F.items()]);dump(out/'SQ_F_N3_Comparison.csv',C);dump(out/'Partial_Fiscal_Financing.csv',B);dump(out/'VAT_Price_Quantity_Income.csv',V);dump(out/'Sensitivity.csv',S);dump(out/'Interactions.csv',interactions)
 dump(out/'Key_Years.csv',[r for r in C if r['year'] in ['2026','2030','2035','2040','2055']])
 pen=[]
 for r in read(out/'N3_Pension_Accounts.csv'):
  pen.append(dict(**r,financial_sector_return_counterpart_trn=-num(r,'fund_return_trn'),public_contribution_loss_trn=num(r,'diverted_existing_contribution_trn'),HH_fund_contribution_second_deduction_trn=0.,counterparty_status='EXPLICIT_RESIDUAL_FINANCIAL_SECTOR_NOT_IDENTIFIED_AS_TREASURY_OR_DOMESTIC_GDP'))
 dump(out/'Pension_Counterpart.csv',pen)
 print(json.dumps(dict(annual_rows=len(A),cases=len(A)//30,new_cases=len(cfg['gap_case_ids']),comparison_rows=len(C),financing_scenario_rows=len(B))))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,default=P);main(ap.parse_args().outdir)
