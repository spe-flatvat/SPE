#!/usr/bin/env python3
"""Exhaustive old/new comparison, source accounts and candidate-only comparisons."""
import csv,json,math,hashlib,argparse,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
from Build_Results import read,dump,num
OLD=ROOT/'handoff/chatgpt-n3-gap-closure-20261121'
METRICS=['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','macro_cash_DI_proxy_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','pension_fund_stock_trn','pension_fund_payout_trn','policy_household_cash_delta_trn']
ALLOWED={'real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','household_consumption_nominal_proxy_trn','consolidated_partial_balance_proxy_trn','macro_cash_DI_proxy_trn','policy_household_cash_delta_trn','household_cash_delta_trn'}
def near(a,b):assert math.isclose(float(a),float(b),abs_tol=5e-7,rel_tol=3e-9),(a,b)
def main(out,sens,replay):
 A=read(out/'Gap_Annual.csv');old=read(OLD/'Gap_Annual.csv');by={(r['case'],r['year']):r for r in A};ob={(r['case'],r['year']):r for r in old};checks={};diff=[];summary={};count=0;changedcases=set()
 assert len(A)==2370 and set(by)==set(ob) and len(by)==2370
 for r in A:
  z=ob[r['case'],r['year']]
  for k,v in z.items():
   count+=1
   if v==r[k]:continue
   assert k in ALLOWED,(r['case'],r['year'],k)
   assert float(r['pension_return_trn'])>0,(r['case'],r['year'],k)
   d=float(r[k])-float(v);diff.append(dict(case=r['case'],year=r['year'],column=k,before=v,after=r[k],delta=d));summary[k]=summary.get(k,0)+1;changedcases.add(r['case'])
  near(float(z['policy_household_cash_delta_trn'])-float(r['pension_domestic_income_debit_trn']),r['policy_household_cash_delta_trn'])
  near(r['pension_return_trn'],r['pension_domestic_income_debit_trn'])
  near(r['pension_direct_GDP_subtraction_trn'],0);near(r['pension_second_contribution_charge_trn'],0)
 checks.update(compared_original_cells=count,changed_cells=len(diff),changed_columns=summary,changed_cases=sorted(changedcases),unrelated_original_cells_exactly_unchanged=count-len(diff))
 dump(out/'Before_After_Cell_Differences.csv',diff)
 dump(out/'Before_After_All79.csv',[dict(case=r['case'],year=r['year'],**{k+'_'+suffix:v for k in METRICS for suffix,v in [('before',num(ob[r['case'],r['year']],k)),('after',num(r,k)),('delta',num(r,k)-num(ob[r['case'],r['year']],k))]}) for r in A])
 modes={'DOMESTIC_TRANSFER':out,**{m:sens/m for m in ['LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']}};srows=[];source=[];legacycount=0
 for mode,folder in modes.items():
  ar=read(folder/'Gap_Annual.csv');assert {(r['case'],r['year']) for r in ar}==set(by)
  for r in ar:
   z=ob[r['case'],r['year']];d=by[r['case'],r['year']]
   if mode=='LEGACY':
    for k,v in z.items():assert r[k]==v,(r['case'],r['year'],k);legacycount+=1
   gain=num(r,'pension_return_trn');debit=num(r,'pension_domestic_income_debit_trn');external=num(r,'pension_external_primary_income_trn');va=num(r,'pension_additional_VA_nominal_trn')
   if mode!='LEGACY':near(gain,debit+external+va)
   # Foreign property income changes national income, not domestic production.
   if mode=='FOREIGN_INCOME':
    for k in z:assert r[k]==z[k],(mode,k)
   for k in ['pension_fund_stock_trn','pension_fund_payout_trn','pension_fund_contribution_trn']:near(r[k],z[k])
   srows.append(dict(mode=mode,case=r['case'],year=r['year'],status='CANDIDATE_OPEN_NOT_ADOPTED',**{k:num(r,k) for k in METRICS},**{k+'_minus_legacy':num(r,k)-num(z,k) for k in METRICS}))
   if gain or num(r,'pension_fund_stock_trn'):
    source.append(dict(mode=mode,case=r['case'],year=r['year'],fund_property_income_credit_trn=gain,domestic_existing_income_debit_trn=debit,overseas_income_trn=external,additional_service_VA_trn=va,unallocated_legacy_source_trn=gain-debit-external-va,new_primary_income_bridge_trn=external+va,complete_GNI_level_trn=None,direct_GDP_subtraction_trn=0,second_contribution_charge_trn=0,incremental_return_tax_trn=0,tax_status='NET_RETURN_OR_UNTAXED_SIMPLIFICATION_TAX_INCIDENCE_OPEN',fund_saving_is_not_real_investment=True))
 checks['legacy_exact_original_cells']=legacycount;checks['candidate_case_years']=len(srows);checks['fund_source_account_rows']=len(source)
 dump(out/'Candidate_Sensitivity_Annual.csv',srows);dump(out/'Pension_Source_Accounts.csv',source)
 files=[f for f in out.iterdir() if f.suffix=='.csv' and (replay/f.name).exists()]
 for f in files:assert f.read_bytes()==(replay/f.name).read_bytes(),f.name
 checks['domestic_deterministic_byte_identical_CSVs']=len(files)
 # Same cells in a complete second run; metadata paths intentionally excluded.
 assert len(files)==23
 # Key comparison: preserve exact definitions; F remains fixed, never re-run.
 F={r['year']:r for r in read(ROOT/'handoff/f-common-endoflife-finalization-20261121/Annual.csv') if r['case']=='LATEST_F'}
 eng={(r['case'],r['year']):r for r in read(out/'N3_Engine_Accounts.csv')}
 table=[]
 for cid in ['SQ_COMMON_ON','N3_CONNECTED_COMPONENTS_A','CONNECTED_Q','CONNECTED_Q_ESTATE','PENSION_COUNTERPART_R0','PENSION_COUNTERPART_R0p02','PENSION_COUNTERPART_R0p04']:
  for y in ['2026','2035','2045','2055']:
   r=by[cid,y];sq=by['SQ_COMMON_ON',y];f=F[y]
   for k in ['real_gdp_trn','nominal_gdp_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','tax_diagnostic_trn','population']:
    x=num(r,k);fs=num(f,k);ss=num(sq,k)
    table.append(dict(case=cid,year=y,metric=k,absolute=x,SQ_absolute=ss,F_fixed_absolute=fs,minus_SQ=x-ss,minus_F=x-fs,comparison='SHARED_ENGINE_CANDIDATE_CONDITIONAL' if k=='population' else 'LIMITED_FIXED_F_DIFFERENT_POLICY_COVERAGE',candidate_only=True))
   # Existing N3 macro_cash_DI label holds resource income incl VAT price effect;
   # subtract that effect to match fixed F cash DI proxy definition explicitly.
   k='cash_DI_definition_matched_proxy_trn';x=num(r,'macro_cash_DI_proxy_trn')-num(r,'household_direct_price_benefit_trn');ss=num(sq,'macro_cash_DI_proxy_trn')-num(sq,'household_direct_price_benefit_trn');fs=num(f,'macro_cash_DI_proxy_trn')
   table.append(dict(case=cid,year=y,metric=k,absolute=x,SQ_absolute=ss,F_fixed_absolute=fs,minus_SQ=x-ss,minus_F=x-fs,comparison='LIMITED_ALGEBRA_MATCHED_PROXY_NOT_NATIONAL_CASH_DI',candidate_only=True))
 dump(out/'Key_Years_Comparison.csv',table)
 checks['status']='PASS_IMPLEMENTER_CHECKS_NOT_INDEPENDENT';(out/'Counterpart_Checks.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);ap.add_argument('--sens',type=Path,required=True);ap.add_argument('--replay',type=Path,required=True);a=ap.parse_args();main(a.outdir,a.sens,a.replay)
