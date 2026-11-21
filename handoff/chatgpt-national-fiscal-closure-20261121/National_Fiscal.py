#!/usr/bin/env python3
"""Cash financing satellite to fixed SPE macro paths, with open stock-flow residuals.
No financing feedback, automatic acceptance, or changes to source macro equations.
"""
import csv,json,argparse,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
MODES=['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']
def rd(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def read_fiscal(folder):
 return [r for f in sorted(folder.glob('National_Fiscal_*.csv')) for r in rd(f)]
def n(r,k,default=None):
 v=r.get(k);return default if v in ['',None] else float(v)
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows({k:format(v,'.14g') if isinstance(v,float) else v for k,v in r.items()} for r in rows)
def baseline(s,official):
 out={};prev=official[2025]['CL_debt_end_trn']
 for y in range(2026,2056):
  if y<=2040:
   b=dict(official[y]);b['baseline_status']='OFFICIAL_CURRENT_PROJECTION_NOT_SPE_FORECAST'
   b['stock_flow_adjustment_unallocated_trn']=b['CL_debt_end_trn']-prev+b['CL_balance_trn'];b['official_debt_end_trn']=b['CL_debt_end_trn']
  elif s['tail']=='NULL_AFTER_2040':
   out[y]=None;continue
  else:
   b=dict(official[2040]);b['year']=y;b['baseline_status']='UNADOPTED_NOMINAL_FLOW_HOLD2040_NO_SFA_ASSUMPTION'
   b['CL_debt_end_trn']=prev-b['CL_balance_trn'];b['stock_flow_adjustment_unallocated_trn']=0.;b['official_debt_end_trn']=None
   for k in ['official_nominal_GDP_trn','central_debt_end_trn','local_debt_end_trn']:b[k]=None
  b['CL_debt_begin_trn']=prev;b['CL_net_interest_trn']=b['CL_PB_trn']-b['CL_balance_trn'];out[y]=b;prev=b['CL_debt_end_trn']
 return out

def finance(begin,assets,pb,interest,sfa,refinance_share):
 balance=pb-interest;need=-balance;draw=min(assets,max(need,0.));new=max(need-draw,0.);surplus=max(-need,0.)
 post_adjustment=begin+sfa;assert post_adjustment>=-1e-7
 repay=min(max(0.,post_adjustment),surplus);save=surplus-repay
 # A declared illustrative refinancing schedule, not observed gross bond issues.
 rollover=min(begin*refinance_share,max(0.,begin-repay))
 end=begin+new-repay+sfa;endassets=assets-draw+save
 return dict(CL_PB_candidate_trn=pb,CL_net_interest_candidate_trn=interest,CL_balance_candidate_trn=balance,CL_cash_financing_need_trn=need,
  CL_debt_begin_candidate_trn=begin,CL_debt_end_candidate_trn=max(0.,end),CL_cash_assets_begin_candidate_trn=assets,CL_cash_assets_end_candidate_trn=endassets,
  CL_new_cash_borrowing_candidate_trn=new,CL_cash_surplus_debt_redemption_candidate_trn=repay,CL_cash_asset_draw_candidate_trn=draw,CL_cash_asset_addition_candidate_trn=save,
  CL_scheduled_refinancing_assumption_trn=rollover,CL_gross_issue_with_assumed_refinancing_trn=new+rollover,CL_gross_redemption_with_assumed_refinancing_trn=repay+rollover,
  CL_stock_flow_adjustment_unallocated_trn=sfa,CL_actual_gross_bond_issue_trn=None,CL_actual_bond_redemption_trn=None)

def main(macro,out,config=None):
 out.mkdir(parents=True,exist_ok=True);cfg=json.loads((config or P/'Fiscal_Inputs.json').read_text())
 official={int(r['year']):{k:float(v) if k.endswith('_trn') and v else v for k,v in r.items()} for r in rd(P/'Official_Fiscal_Baseline_2025_2040.csv')}
 annual={mode:rd(macro/mode/'Gap_Annual.csv') for mode in MODES};engine={mode:{(r['case'],r['year']):r for r in rd(macro/mode/'N3_Engine_Accounts.csv')} for mode in MODES}
 for mode in MODES:assert len(annual[mode])==2370
 F=rd(ROOT/'handoff/f-common-endoflife-finalization-20261121/Annual.csv');F={r['year']:r for r in F if r['case']=='LATEST_F'}
 FF={r['year']:r for r in rd(ROOT/'handoff/f-common-endoflife-finalization-20261121/Fiscal.csv') if r['case']=='LATEST_F'}
 baseA={r['year']:r for r in annual['DOMESTIC_TRANSFER'] if r['case']=='SQ_COMMON_ON'};baseE={r['year']:r for r in engine['DOMESTIC_TRANSFER'].values() if r['case']=='SQ_COMMON_ON'}
 transfers=[];allrows=[];channelrows=[];baserows=[]
 # Shared arithmetic for F fixed and each recalculated N3 path.
 def channels(r,e,mode):
  y=r['year'];sq=baseA[y];se=baseE[y];isf=r['case']=='F_FIXED_REFERENCE'
  g0=n(se,'fiscal_balance_partial_trn');i0=n(sq,'consolidated_partial_balance_proxy_trn')-g0
  gov=n(FF[y],'government_partial_balance_proxy_trn') if isf else n(e,'fiscal_balance_partial_trn')
  ins=n(FF[y],'insurer_known_change_and_program_balance_trn') if isf else n(r,'consolidated_partial_balance_proxy_trn')-gov
  expense=n(FF[y],'government_expenditure_after_pension_reclassification_trn') if isf else n(e,'expenditure_diagnostic_trn')
  macro_tax=n(FF[y],'tax_macro_feedback_proxy_trn') if isf else n(e,'tax_macro_trn')
  oldinterest=n(r,'medical_policy_interest_trn',0.)+n(r,'bond_interest_trn',0.)-n(sq,'medical_policy_interest_trn',0.)
  taxdelta=n(r,'tax_diagnostic_trn')-n(sq,'tax_diagnostic_trn');exdelta=expense-n(se,'expenditure_diagnostic_trn')
  assert math.isclose(gov-g0,taxdelta-exdelta,abs_tol=5e-7,rel_tol=3e-9)
  return dict(case=r['case'],year=y,mode=mode,model_government_balance_delta_trn=gov-g0,model_insurer_balance_delta_trn=ins-i0,
   model_tax_delta_once_trn=taxdelta,model_macro_tax_feedback_delta_trn=macro_tax-n(se,'tax_macro_trn'),model_expenditure_delta_trn=exdelta,
   existing_policy_interest_removed_trn=oldinterest,model_primary_government_delta_trn=gov-g0+oldinterest,
   modeled_VAT_delta_diagnostic_only_trn=n(r,'modeled_VAT_trn')-n(sq,'modeled_VAT_trn'),policy_direct_tax_delta_diagnostic_only_trn=n(r,'policy_tax_delta_trn'),
   real_gdp_trn=n(r,'real_gdp_trn'),nominal_gdp_trn=n(r,'nominal_gdp_trn'),macro_cash_DI_definition_matched_proxy_trn=n(r,'macro_cash_DI_proxy_trn')-(0. if isf else n(r,'household_direct_price_benefit_trn')),
   household_consumption_nominal_proxy_trn=n(r,'household_consumption_nominal_proxy_trn'),model_tax_diagnostic_proxy_trn=n(r,'tax_diagnostic_trn'),
   pension_fund_stock_trn=n(r,'pension_fund_stock_trn'),pension_benefit_delta_trn=n(r,'pension_benefit_delta_trn',n(r,'pension_reform_payment_delta_trn')),
   clinical_cost_delta_trn=n(r,'clinical_cost_delta_trn'),government_insurer_internal_transfer_diagnostic_trn=n(r,'government_insurer_transfer_delta_trn',0.),
   fund_status='UNADOPTED_MODELED_PENSION_NOT_GOVERNMENT_DEBT_NETTING')
 # F has a fixed source separate from the 79 N3 IDs.
 frows=[dict(r,case='F_FIXED_REFERENCE') for r in F.values()]
 for mode in MODES:
  source_rows=annual[mode]+(frows if mode=='DOMESTIC_TRANSFER' else [])
  grouped={}
  for r in source_rows:
   e=engine[mode].get((r['case'],r['year']),{})
   ch=channels(r,e,mode);channelrows.append(ch);grouped.setdefault(r['case'],[]).append(ch)
  scenarios=cfg['scenarios'] if mode=='DOMESTIC_TRANSFER' else cfg['scenarios'][:1]
  for s in scenarios:
   bas=baseline(s,official)
   if mode=='DOMESTIC_TRANSFER':
    for y,b in bas.items():
     if b:baserows.append(dict(scenario=s['id'],**b))
   for cid,items in grouped.items():
    debt=official[2025]['CL_debt_end_trn'];assets=0.
    for ch in sorted(items,key=lambda z:int(z['year'])):
     y=int(ch['year']);b=bas[y];ins=ch['model_insurer_balance_delta_trn'];backfill=-s['insurer_deficit_backfill']*min(ins,0.)
     adjustment=(s['macro_tax_feedback_scale']-1)*ch['model_macro_tax_feedback_delta_trn']
     primary=ch['model_primary_government_delta_trn']+adjustment-backfill
     z=dict(scenario=s['id'],mode=mode,case=cid,year=y,status='PARTIAL_CLOSURE_CENTRAL_LOCAL_CANDIDATE_NOT_GENERAL_GOVERNMENT',macro_source='FIXED_F_NOT_REEXECUTED' if cid=='F_FIXED_REFERENCE' else 'REEXECUTED_PINNED_79_CASE_MACRO',time_basis=cfg['time_bridge'],
      incremental_interest_rate_candidate=s['incremental_interest_rate'],insurer_deficit_backfill_fraction_candidate=s['insurer_deficit_backfill'],macro_tax_feedback_scale_candidate=s['macro_tax_feedback_scale'],refinancing_share_assumption=s['refinance_share'],
      **{k:v for k,v in ch.items() if k not in ['case','year','mode']},CL_primary_delta_after_mapping_trn=primary,insurer_backfill_transfer_trn=backfill,insurer_balance_delta_after_backfill_trn=ins+backfill,
      consolidated_known_primary_delta_trn=primary+ins+backfill,macro_tax_mapping_adjustment_trn=adjustment,
      national_PB_trn=None,national_debt_trn=None,national_bond_issue_trn=None,national_tax_trn=None,national_social_contributions_trn=None,
      national_expenditure_trn=None,CL_total_revenue_trn=None,CL_total_primary_expenditure_trn=None,central_policy_allocation_trn=None,local_policy_allocation_trn=None,SS_baseline_balance_2026_2055_trn=None,
      unallocated_foreign_social_cost_trn=None,automatic_macro_debt_interest_feedback=False)
     if b:
      # Proportionate baseline interest retires with baseline debt; new excess
      # debt and explicitly accumulated cash assets use the candidate rate.
      baseinterest=b['CL_net_interest_trn'];basedebt=b['CL_debt_begin_trn']
      debtinterest=baseinterest*min(1.,debt/basedebt)+s['incremental_interest_rate']*max(0.,debt-basedebt)
      interest_delta=debtinterest-baseinterest-s['incremental_interest_rate']*assets
      pb=b['CL_PB_trn']+primary;interest=b['CL_net_interest_trn']+interest_delta
      z.update(baseline_status=b['baseline_status'],CL_baseline_PB_trn=b['CL_PB_trn'],CL_baseline_balance_trn=b['CL_balance_trn'],CL_baseline_debt_begin_trn=b['CL_debt_begin_trn'],CL_baseline_debt_end_trn=b['CL_debt_end_trn'],CL_official_debt_end_trn=b['official_debt_end_trn'],official_nominal_GDP_trn=b['official_nominal_GDP_trn'],CL_incremental_net_interest_trn=interest_delta,
       **finance(debt,assets,pb,interest,b['stock_flow_adjustment_unallocated_trn'],s['refinance_share']))
      debt=z['CL_debt_end_candidate_trn'];assets=z['CL_cash_assets_end_candidate_trn']
      z['CL_debt_to_SPE_nominal_GDP_candidate_pct']=100*debt/ch['nominal_gdp_trn'];z['CL_debt_minus_baseline_trn']=debt-b['CL_debt_end_trn']
     else:z.update(baseline_status='MISSING_OFFICIAL_AFTER2040_STRICT_NULL',CL_PB_candidate_trn=None,CL_debt_end_candidate_trn=None,CL_gross_issue_with_assumed_refinancing_trn=None)
     allrows.append(z)
     if mode=='DOMESTIC_TRANSFER' and s['id']=='REFERENCE_CANDIDATE':transfers.append(dict(case=cid,year=y,government_payment_trn=backfill,insurer_receipt_trn=backfill,internal_transfer_consolidated_trn=0,insurer_before_trn=ins,insurer_after_trn=ins+backfill,pension_contributions_not_second_HH_charge=True,medical_pension_tax_VAT_already_in_model_delta=True))
 dump(out/'Fiscal_Channels_All_Modes.csv',channelrows);
 for sc in cfg['scenarios']:
  for mode in MODES:
   selected=[r for r in allrows if r['scenario']==sc['id'] and r['mode']==mode]
   if not selected:continue
   name='National_Fiscal_Annual.csv' if sc['id']=='REFERENCE_CANDIDATE' and mode=='DOMESTIC_TRANSFER' else 'National_Fiscal_Mode_'+mode+'.csv' if sc['id']=='REFERENCE_CANDIDATE' else 'National_Fiscal_Scenario_'+sc['id']+'.csv'
   dump(out/name,selected)
 dump(out/'Fiscal_Baseline_Annual.csv',baserows);dump(out/'Transfer_Audit.csv',transfers)
 domestic={(r['case'],str(r['year'])):r for r in allrows if r['scenario']=='REFERENCE_CANDIDATE' and r['mode']=='DOMESTIC_TRANSFER' and r['case']!='F_FIXED_REFERENCE'}
 extended=[]
 for r in annual['DOMESTIC_TRANSFER']:
  z=domestic[r['case'],r['year']];extended.append(dict(r,**{'fiscal_'+k:v for k,v in z.items() if k not in ['case','year','mode']}))
 dump(out/'Annual79_With_Fiscal.csv',extended)
 # Every existing macro column is retained verbatim as strings; only new columns added.
 dump(out/'Key_Years_Fiscal_Comparison.csv',[r for r in allrows if r['mode']=='DOMESTIC_TRANSFER' and r['case'] in ['SQ_COMMON_ON','F_FIXED_REFERENCE','N3_CONNECTED_COMPONENTS_A','CONNECTED_Q','CONNECTED_Q_ESTATE'] and r['year'] in [2026,2035,2045,2055]])
 # Main mode-by-mode results include all original 79 IDs, not just selected packages.
 dump(out/'Pension_Mode_Fiscal_Comparison.csv',[r for r in allrows if r['scenario']=='REFERENCE_CANDIDATE' and r['year'] in [2026,2035,2045,2055]])
 (out/'Execution_Summary.json').write_text(json.dumps(dict(status='EXECUTED_PARTIAL_CLOSURE',macro_cases_per_mode=79,macro_modes=4,macro_case_years=9480,national_fiscal_rows=len(allrows),basic_annual_rows=len(extended),f_reexecuted=False,macro_financing_feedback=False,full_GG_closed=False,years=[2026,2055]),indent=2)+'\n')
 print(json.dumps(dict(fiscal_rows=len(allrows),annual79_rows=len(extended),source_channel_rows=len(channelrows))))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--macro',type=Path,required=True);ap.add_argument('--outdir',type=Path,required=True);a=ap.parse_args();main(a.macro,a.outdir)
