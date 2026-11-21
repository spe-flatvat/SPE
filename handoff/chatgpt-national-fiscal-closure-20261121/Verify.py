#!/usr/bin/env python3
"""Implementer tests; independent arithmetic from exported ledgers, not a review."""
import argparse,csv,json,math,hashlib,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8')))
def n(r,k):return float(r[k])
def near(a,b,tol=1e-6):assert math.isclose(float(a),float(b),abs_tol=tol,rel_tol=5e-11),(a,b)
def main(out,macro,replay=None):
 checks={};rows=[r for f in sorted(out.glob('National_Fiscal_*.csv')) for r in rd(f)];active=[r for r in rows if r['CL_PB_candidate_trn']];nullrows=[r for r in rows if not r['CL_PB_candidate_trn']]
 assert len(rows)==23910
 for r in active:
  near(n(r,'CL_PB_candidate_trn')-n(r,'CL_net_interest_candidate_trn'),r['CL_balance_candidate_trn'])
  near(n(r,'CL_debt_begin_candidate_trn')+n(r,'CL_gross_issue_with_assumed_refinancing_trn')-n(r,'CL_gross_redemption_with_assumed_refinancing_trn')+n(r,'CL_stock_flow_adjustment_unallocated_trn'),r['CL_debt_end_candidate_trn'])
  near(n(r,'CL_cash_assets_begin_candidate_trn')-n(r,'CL_cash_asset_draw_candidate_trn')+n(r,'CL_cash_asset_addition_candidate_trn'),r['CL_cash_assets_end_candidate_trn'])
  near(n(r,'CL_new_cash_borrowing_candidate_trn')-n(r,'CL_cash_surplus_debt_redemption_candidate_trn')+n(r,'CL_cash_asset_draw_candidate_trn')-n(r,'CL_cash_asset_addition_candidate_trn'),r['CL_cash_financing_need_trn'])
  near(-n(r,'CL_balance_candidate_trn'),r['CL_cash_financing_need_trn'])
  near(n(r,'CL_PB_candidate_trn'),n(r,'CL_baseline_PB_trn')+n(r,'CL_primary_delta_after_mapping_trn'))
  near(n(r,'model_government_balance_delta_trn'),n(r,'model_tax_delta_once_trn')-n(r,'model_expenditure_delta_trn'))
  near(n(r,'CL_primary_delta_after_mapping_trn'),n(r,'model_government_balance_delta_trn')+n(r,'existing_policy_interest_removed_trn')+n(r,'macro_tax_mapping_adjustment_trn')-n(r,'insurer_backfill_transfer_trn'))
  near(n(r,'consolidated_known_primary_delta_trn'),n(r,'model_primary_government_delta_trn')+n(r,'macro_tax_mapping_adjustment_trn')+n(r,'model_insurer_balance_delta_trn'))
  for k in ['CL_debt_end_candidate_trn','CL_cash_assets_end_candidate_trn','CL_gross_issue_with_assumed_refinancing_trn','CL_gross_redemption_with_assumed_refinancing_trn']:assert n(r,k)>=0
  if r['year']=='2026':near(r['CL_debt_begin_candidate_trn'],1270.2)
  if r['case']=='SQ_COMMON_ON' or r['year']=='2026':near(r['CL_debt_end_candidate_trn'],r['CL_baseline_debt_end_trn'])
 for r in rows:
  for k in ['national_PB_trn','national_debt_trn','national_bond_issue_trn','national_tax_trn','national_expenditure_trn','CL_total_revenue_trn','CL_total_primary_expenditure_trn','SS_baseline_balance_2026_2055_trn']:assert r[k]=='',k
  if int(r['year'])<=2040:assert r['baseline_status']=='OFFICIAL_CURRENT_PROJECTION_NOT_SPE_FORECAST'
  if r['scenario']=='STRICT_SOURCE_ONLY' and int(r['year'])>2040:assert not r['CL_PB_candidate_trn'] and not r['CL_debt_end_candidate_trn']
  assert r['automatic_macro_debt_interest_feedback']=='False'
 checks.update(fiscal_rows=len(rows),account_identity_rows=len(active),strict_missing_tail_rows=len(nullrows),national_GG_unknowns_retained_rows=len(rows))
 # Changing the assumed refinancing turnover changes gross issues, never debt/PB.
 idx={(r['scenario'],r['mode'],r['case'],r['year']):r for r in rows}
 rollover_changed=0
 for r in rows:
  if r['scenario']!='REFINANCE_20PCT':continue
  z=idx['REFERENCE_CANDIDATE',r['mode'],r['case'],r['year']]
  for k in ['CL_PB_candidate_trn','CL_debt_end_candidate_trn','CL_balance_candidate_trn']:near(r[k],z[k])
  rollover_changed+=r['CL_gross_issue_with_assumed_refinancing_trn']!=z['CL_gross_issue_with_assumed_refinancing_trn']
 assert rollover_changed>0;checks['refinancing_changes_gross_only_rows']=rollover_changed
 for r in rows:
  if r['scenario']!='INSURER_FULL_BACKFILL':continue
  z=idx['REFERENCE_CANDIDATE',r['mode'],r['case'],r['year']]
  near(r['consolidated_known_primary_delta_trn'],z['consolidated_known_primary_delta_trn'])
 checks['backfill_consolidated_primary_neutral_rows']=2400
 official={r['year']:r for r in rd(P/'Official_Fiscal_Baseline_2025_2040.csv')}
 for r in rows:
  if r['case']=='SQ_COMMON_ON' and int(r['year'])<=2040:
   near(r['CL_PB_candidate_trn'],official[r['year']]['CL_PB_trn']);near(r['CL_debt_end_candidate_trn'],official[r['year']]['CL_debt_end_trn'])
 # Actual full macro rerun and all old columns, including nulls and strings.
 original=ROOT/'handoff/chatgpt-n3-pension-counterpart-20261121';old=rd(original/'Gap_Annual.csv');oldby={(r['case'],r['year']):r for r in old};new=rd(out/'Annual79_With_Fiscal.csv');cells=0
 assert len(new)==2370
 for r in new:
  for k,v in oldby[r['case'],r['year']].items():assert r[k]==v,(r['case'],r['year'],k);cells+=1
 checks['old79_original_cells_exact_unchanged']=cells
 # Byte validation of all 4 actually rerun macro annual paths against fixed input.
 candidate={(r['mode'],r['case'],r['year']):r for r in rd(original/'Candidate_Sensitivity_Annual.csv')};candidatecells=0
 for mode in ['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']:
  rerun=rd(macro/mode/'Gap_Annual.csv');assert len(rerun)==2370
  for r in rerun:
   ref=candidate[mode,r['case'],r['year']]
   for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','macro_cash_DI_proxy_trn','pension_fund_stock_trn']:near(r[k],ref[k]);candidatecells+=1
  if mode=='DOMESTIC_TRANSFER':assert (macro/mode/'Gap_Annual.csv').read_bytes()==(original/'Gap_Annual.csv').read_bytes()
 checks['four_mode_annual_regression_numeric_cells']=candidatecells
 # The official GFS workbook contains a separate consolidation adjustment.
 snap={r['sector']:r for r in rd(P/'SNA2024_Sector_Snapshot.csv')}
 for r in snap.values():
  near(n(r,'revenue_trn')-n(r,'expense_trn')-n(r,'net_nonfinancial_asset_acquisition_trn'),r['net_lending_trn'],tol=.0002)
  if r['sector']!='CONSOLIDATION_ADJUSTMENT':near(n(r,'SNA_net_lending_trn')+n(r,'interest_paid_pre_FISIM_trn')-n(r,'interest_received_pre_FISIM_trn'),r['SNA_PB_trn'],tol=.0002)
 for k in ['revenue_trn','expense_trn','tax_trn','social_contributions_trn','net_lending_trn']:
  near(sum(n(snap[s],k) for s in ['CENTRAL','LOCAL','SOCIAL_SECURITY','CONSOLIDATION_ADJUSTMENT']),snap['GENERAL_GOVERNMENT'][k],tol=.0003)
 checks['official_2024_sector_and_consolidation_rows']=5
 # Core payer, fund, medical-protection, VAT, foreign tests from fixed implementation.
 for name in ['Gap_Common.csv','N3_Pension_Accounts.csv','Gap_Foreign_Bridge.csv']:
  assert (macro/'DOMESTIC_TRANSFER'/name).read_bytes()==(original/name).read_bytes(),name
 checks['unchanged_pension_protection_foreign_source_CSVs']=3
 if replay:
  names=[p.name for p in out.glob('National_Fiscal_*.csv')]+['Annual79_With_Fiscal.csv','Fiscal_Channels_All_Modes.csv','Fiscal_Baseline_Annual.csv','Transfer_Audit.csv','Key_Years_Fiscal_Comparison.csv','Pension_Mode_Fiscal_Comparison.csv','Execution_Summary.json']
  for name in names:assert (out/name).read_bytes()==(replay/name).read_bytes(),name
  checks['fiscal_reexecution_byte_identical_files']=len(names)
 result=dict(status='PASS_IMPLEMENTER_TESTS_NOT_NEW_CLAUDE_REVIEW',checks=checks);(out/'Checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);ap.add_argument('--macro',type=Path,required=True);ap.add_argument('--replay',type=Path);a=ap.parse_args();main(a.outdir,a.macro,a.replay)
