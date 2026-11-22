#!/usr/bin/env python3
"""Isolated evidence-lower-bound and conditional sector cash-use recurrence.
No invented historical funds or sector allocation of N3 taxes/spending.
"""
import argparse,csv,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
PREV='handoff/chatgpt-n3-sfa-cash-reconciliation-20261122'
PIN='ccadca9f5435be5db4cbda1c9f5170c13ee0bf0b'
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def load(root):
 sp=importlib.util.spec_from_file_location('fixed_sfa',root/PREV/'N3_SFA_Reproduce.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def run(root,out):
 out.mkdir(parents=True,exist_ok=True);m=load(root);m.install_runtime(out)
 class Runner(m.Runner):
  def cash_budget(self,s,y,pb,interest,sfa,assets):
   b=super().cash_budget(s,y,pb,interest,sfa,assets)
   # Only additional G/I execution is withheld; existing policy and fiscal base stay.
   if s.get('no_verified_spend'):return 0.
   return b
 r=Runner(root,out);receipts=[]
 for p in sorted((root/PREV).iterdir()):
  if p.is_file():
   rel=str(p.relative_to(root));b=subprocess.check_output(['git','show',PIN+':'+rel],cwd=root);assert p.read_bytes()==b
   receipts.append(dict(commit=PIN,path=rel,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 (out/'Input_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 definitions=[m.spec('EVIDENCE_CONFIRMED_INCREMENT_LOWER',no_verified_spend=True),m.spec('UNCONFIRMED_FLOW_Q0'),m.spec('REPLAY_Q50',.5)]
 for sector,qc,ql in [('CENTRAL',1.,0.),('LOCAL',0.,1.),('BOTH',1.,1.)]:
  for minimum in [False,True]:
   definitions.append(m.spec(('MIN_SQ_' if minimum else 'CONDITIONAL_')+sector,cash_partition='SECTOR',q_central=qc,q_local=ql,min_to_SQ=minimum,bridge_cap=100. if minimum else 0.,bridge_total_cap=100.))
 annual=[];integrated=[];summ=[];funding=[];sectorledger=[];connections=[]
 previous={(z['case'],int(z['year'])):z for z in rd(root/PREV/'N3_SFA_GDP_Annual_Comparison_2026_2055.csv')}
 cache={}
 for s in definitions:
  a,l,b=r.simulate(s);annual+=a;integrated+=l;cache[s['case']]=(a,l)
  extra={x['year']:x for x in r.extra_ledger if x['case']==s['case']}
  z=m.T.previous.summary(s,a,l);z.update(gap2030=next(x['GDP_minus_SQ_trn'] for x in a if x['year']==2030),evidence_status='CONFIRMED_INCREMENT_LOWER_NO_CERTIFIED_ADDITIONAL_EXECUTION' if s.get('no_verified_spend') else 'CONDITIONAL_UNVERIFIED_CASH_CONVERSION_AND_AUTHORITY',real_world_feasibility='UNDETERMINED');summ.append(z)
  for x in a:
   y=x['year']
   for new,old in [('UNCONFIRMED_FLOW_Q0','Q0'),('REPLAY_Q50','Q50')]:
    if s['case']==new:
     for k in ['real_GDP_trn','total_tax_diagnostic_proxy_trn','CL_PB_candidate_trn','CL_debt_candidate_trn']:r.ck('limited_replay:'+new+str(y)+k,x[k]-float(previous[old,y][k]),3e-6)
  l30=next(x for x in l if x['year']==2030);e=extra[2030]
  funding.append(dict(case=s['case'],year=2030,actual_SFA_cash_need_trn='unknown',assumed_SFA_cash_need_trn=l30['SFA_cash_need_trn'],verified_usable_historical_cash_trn='unknown',certified_historical_cash_credit_lower_trn=0.,certified_new_execution_funds_lower_trn=0.,cash_proxy_before_additional_spend_trn=l30['primary_balance_before_additional_spend_trn']-l30['interest_trn'],cash_proxy_conversion_adjustment_trn='unknown',government_execution_trn=l30['government_spend_trn'],conditional_new_cash_borrowing_trn=l30['new_cash_borrowing_trn'],conditional_cash_redemption_trn=l30['cash_debt_redemption_trn'],additional_execution_authority_trn=e['additional_expenditure_authority_trn'],GDP_minus_SQ_trn=z['gap2030'],funding_gap_actual_trn='unknown',central_funding_gap_actual_trn='unknown',local_funding_gap_actual_trn='unknown',authorized_asset_sales_trn='unknown',authorized_new_CL_transfers_trn='unknown',certified_asset_sales_credit_trn=0.,certified_new_CL_transfers_credit_trn=0.,sector_capacity_feasible='unknown'))
  # Genuine partial sector ledger: no pro-rata division of consolidated policy flows.
  for y in range(2026,2056):
   o=r.official.get(y,{});prev=r.official.get(y-1,{})
   for sector,prefix in [('CENTRAL','central'),('LOCAL','local')]:
    d0=prev.get(prefix+'_debt_end_trn','unknown');d1=o.get(prefix+'_debt_end_trn','unknown');bal=o.get(prefix+'_balance_trn','unknown');pb=o.get(prefix+'_PB_trn','unknown')
    residual=r.partition.get(y,{}).get(prefix,'unknown');cashpart='unknown'
    if y<=2040 and s['cash_partition']=='SECTOR':cashpart=s['q_central' if sector=='CENTRAL' else 'q_local']*max(0.,residual)
    elif y<=2040 and s['q']==0:cashpart=0.
    inter=pb-bal if isinstance(pb,(int,float)) and isinstance(bal,(int,float)) else 'unknown'
    row=dict(case=s['case'],year=y,sector=sector,official_debt_begin_trn=d0,official_debt_end_trn=d1,official_balance_trn=bal,official_PB_trn=pb,official_net_interest_trn=inter,official_residual_trn=residual,official_cells_status='OFFICIAL_FORECAST_LIMITED_DEBT_BOUNDARY' if y<=2040 else 'unknown',N3_cash_begin_trn='unknown',N3_cash_end_trn='unknown',N3_primary_cash_flow_trn='unknown',accrual_cash_adjustment_trn='unknown',N3_interest_trn='unknown',identified_SFA_cash_use_trn='unknown',conditional_SFA_cash_use_trn=cashpart,conditional_cash_use_status='MODEL_ASSUMPTION_NOT_IDENTIFIED' if cashpart!='unknown' else 'unknown',financial_asset_acquisition_trn='unknown',financial_asset_sale_trn='unknown',fund_deposit_trn='unknown',fund_withdrawal_trn='unknown',central_local_transfer_net_trn='unknown',N3_gross_issue_trn='unknown',N3_refinancing_trn='unknown',N3_maturity_redemption_trn='unknown',N3_debt_end_trn='unknown',verified_usable_cash_trn='unknown',certified_cash_credit_lower_trn=0.,conditional_upper_available_cash_trn='unknown',cash_identity_status='NOT_TESTABLE_MISSING_SECTOR_FLOWS',debt_identity_status='OFFICIAL_STOCK_BALANCE_RESIDUAL_ONLY' if y<=2040 else 'NOT_TESTABLE',GDP_link='CONSOLIDATED_ONLY_SECTOR_ALLOCATION_UNAVAILABLE')
    sectorledger.append(row)
    if y<=2040:r.ck('official_sector_residual:'+s['case']+str(y)+sector,d1-d0+bal-residual,3e-6)
  connections.extend(x for x in r.connections if x['case']==s['case'])
 # Consolidated amount-preserving identities; partial sector cash identities remain unknown.
 for l in integrated:
  r.ck('integrated_cash:'+l['case']+str(l['year']),l['PB_trn']-l['interest_trn']-l['SFA_cash_need_trn']+l['other_asset_sale_trn']+l['new_cash_borrowing_trn']-l['cash_debt_redemption_trn']-l['assets_end_trn']+l['assets_begin_trn'])
  r.ck('integrated_debt:'+l['case']+str(l['year']),l['debt_end_trn']-l['debt_begin_trn']-l['new_cash_borrowing_trn']+l['cash_debt_redemption_trn']-l['SFA_remaining_adjustment_trn'])
 base=cache['UNCONFIRMED_FLOW_Q0'][1]
 for f in funding:
  l=next(x for x in cache[f['case']][1] if x['year']==2030);ref=next(x for x in base if x['year']==2030)
  f.update(redemption_reduction_vs_conditional_Q0_trn=ref['cash_debt_redemption_trn']-l['cash_debt_redemption_trn'],new_borrowing_increment_vs_conditional_Q0_trn=l['new_cash_borrowing_trn']-ref['new_cash_borrowing_trn'])
  if f['case'].startswith('MIN_SQ_'):
   cid='CONDITIONAL_'+f['case'][7:];ref=next(x for x in cache[cid][1] if x['year']==2030)
   f.update(execution_increment_vs_same_cash_use_trn=l['government_spend_trn']-ref['government_spend_trn'],new_borrowing_increment_vs_same_cash_use_trn=l['new_cash_borrowing_trn']-ref['new_cash_borrowing_trn'],redemption_reduction_vs_same_cash_use_trn=ref['cash_debt_redemption_trn']-l['cash_debt_redemption_trn'])
 refs={'Q0','Q25','Q50','Q100','MIN_SQ_Q25','MIN_SQ_Q50','MIN_SQ_Q100'}
 reused=[{**x,'result_origin':'REUSED_FIXED_CCAd_RESULT_NOT_NEW_EXECUTION','source_commit':PIN} for x in rd(root/PREV/'N3_SFA_GDP_Annual_Comparison_2026_2055.csv') if x['case'] in refs]
 dump(out/'N3_Central_Local_GDP_Annual_Comparison_2026_2055.csv',annual+reused)
 dump(out/'N3_Integrated_Conditional_Cash_Ledger_2026_2055.csv',integrated)
 dump(out/'N3_Central_Local_Source_Use_Ledger_2026_2055.csv',sectorledger)
 dump(out/'N3_2030_Funding_Gap_and_Options.csv',funding)
 dump(out/'N3_Case_Summary.csv',summ);dump(out/'N3_Case_Definitions.csv',definitions);dump(out/'N3_Tax_Income_Native_Connections.csv',connections)
 dump(out/'Detail_2029_2032.csv',[x for x in sectorledger if 2029<=x['year']<=2032])
 v=dict(status='PASS_LIMITED_ARITHMETIC_ONLY' if not r.checks else 'FAIL',new_cases=len(definitions),new_annual_rows=len(annual),reused_cases=7,reused_annual_rows=len(reused),checks=r.counter,failures=r.checks,failed=len(r.checks),prior_PASS_reused=[30925,25478,35281],sector_cash_identity='NOT_TESTABLE_UNKNOWN_INPUTS',sector_official_stock_residual_identity='TESTED_2026_2040',integrated_cash_and_debt_identity='TESTED',actual_2030_usable_cash='unknown',actual_SFA_cash_need='unknown',actual_2030_funding_gap='unknown',real_world_all_years_SQ='NOT_ESTABLISHED',general_government_closed=False,calibration_robustness=False,original_policy_and_engine_modified=False,policy_adopted=False)
 (out/'Verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v));assert not r.checks,r.checks[:5]
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--outdir',type=Path,required=True);z=a.parse_args();run(z.root.resolve(),z.outdir.resolve())
