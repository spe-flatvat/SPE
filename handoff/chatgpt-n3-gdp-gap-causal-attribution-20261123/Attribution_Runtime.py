"""Read-only source instrumentation and isolated existing-block counterfactuals."""
import importlib.util,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PREV='handoff/chatgpt-n3-assumptions-specification-calibration-separation-20261123'
SIM='handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123/Resolved_Separation_Runtime.py.txt'
SFA='handoff/chatgpt-n3-sfa-cash-reconciliation-20261122/N3_SFA_Reproduce.py'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def build(root,out,definition):
 prior=module('fixed_assumption_runtime',root/PREV/'Sensitivity_Runtime.py')
 r,s=prior.build(root,out,definition);r.par.update(definition.get('macro_override',{}))
 m=module('gap_sfa_runtime',root/SFA);ns=dict(m.T.previous.__dict__)
 source=(root/SIM).read_text()
 a="penrow=co.pension[-1];self.ck(pre+'pension_stock'"
 b="penrow=co.pension[-1] if co.pension else dict(fund_end_trn=0.,fund_begin_trn=0.,fund_return_trn=0.,fund_contribution_trn=0.,fund_payout_trn=0.);self.ck(pre+'pension_stock'"
 assert source.count(a)==1;source=source.replace(a,b)
 # A fixed-base structure diagnostic must be checked against factor1, while
 # ordinary dynamic cases retain the original lagged-wage ratio invariant.
 a="if y>2026 else 1.))"
 b="if y>2026 and co.dynamic_rows[-1]['enabled'] else 1.))"
 assert source.count(a)==1;source=source.replace(a,b)
 assert source.count('  annual.append(row)')==1
 source=source.replace('  annual.append(row)','  annual.append(row)\n  self.capture(s,y,t,w,co,md,prior,locals())')
 exec(compile(source,'instrumented_attribution_runtime','exec'),ns);r.simulate=types.MethodType(ns['simulate'],r)
 r.resolved_runtime=source;r.targets=[];r.midpoints=[];r.filtered={};r.baseline_cells=[]
 def capture(self,s,y,t,w,co,md,prior,v):
  p=co.rows[-1];d=v['d'];par=self.par;mpc=par['generic_mpc'];dom=par['domestic_share'];lc=self.local_connection[-1]
  pre=s['case']+str(y)+':active_switch:'
  if md.s.get('flat_hh') is False:self.ck(pre+'HHtax_off',abs(p['labour_business_flat30_tax_delta_trn'])+abs(p['household_financial20_tax_delta_trn']))
  if md.s.get('pension75') is False:self.ck(pre+'pension_off',abs(p['pension_benefit_delta_trn'])+abs(p['pension_fund_contribution_trn'])+abs(p['pension_fund_stock_trn'])+abs(p['pension_return_trn']))
  if md.s.get('corporate') is False:self.ck(pre+'corporate_off',abs(p['corporate_tax_delta_trn'])+abs(p['dividend_delta_trn'])+abs(p['policy_investment_delta_trn'])+abs(v['privI']))
  if md.s.get('estate_reported') is False:self.ck(pre+'estate_off',w['wealth_tax_delta_trn'])
  if md.s.get('relief') is False:self.ck(pre+'relief_inkind_off',abs(p['premium_relief_trn'])+abs(p['in_kind_trn']))
  if md.s.get('employment') is False:self.ck(pre+'employment_off',p['public_payroll_delta_trn'])
  if definition.get('macro_override',{}).get('income_feedback')==0.:self.ck(pre+'income_feedback_off',v['feedback'])
  if md.s.get('dynamic_bases') is False:self.ck(pre+'fixed_bases',abs(co.dynamic_rows[-1]['wage_base_factor']-1)+abs(co.dynamic_rows[-1]['corporate_profit_base_factor']-1))
  if s['firm_rate']==0.:self.ck(pre+'residual_investment_off',v['privI'])
  reserve=co.semi_rows[-1]['household_extra_premium_trn'] if co.semi_rows else 0.
  cashparts=dict(labor_tax=-p['labour_business_flat30_tax_delta_trn'],financial_tax=-p['household_financial20_tax_delta_trn'],
   estate_tax=-w['wealth_tax_delta_trn'],corporate_dividend=.8*p['dividend_delta_trn'],premium_relief=p['premium_relief_trn'],
   in_kind_expense_substitution=.7*p['in_kind_trn'],public_payroll=p['public_payroll_delta_trn'],pension_benefit=p['pension_benefit_delta_trn'],
   fund_payout=p['pension_fund_payout_trn'],fund_domestic_return_debit=-p['pension_domestic_income_debit_trn'],semi_med_reserve=-reserve,
   EITC_removal=-p['EITC_removal_trn'],medical_household=w['medical_only_household_cash_delta_trn'],
   VAT_household=t['vat']['household']+lc['VAT_HH_cash_change_trn'])
  cashparts['other_cash_unidentified']=v['cash']-sum(cashparts.values())
  self.ck(s['case']+str(y)+':cash_sources_sum',v['cash']-sum(cashparts.values()))
  targets={k:dom*mpc*value/d for k,value in cashparts.items()}
  targets['estate_tax']+=dom*(mpc-w['estate_mpc_candidate'])*w['wealth_tax_delta_trn']/d
  targets.update(income_feedback=dom*mpc*v['feedback']/d,
    quantity_volume=dom*w['quantity_nominal_volume_delta_trn']/d,
    quantity_price_replacement=-dom*mpc*w['quantity_replaced_price_benefit_trn']/d,
    legacy_social=-dom*mpc*t['social']['household']/d+dom*t['social']['weighted_demand']/d,
    legacy_pension=dom*(t['pension_ledger']['consumption_impulse_trn']-mpc*t['pension_ledger']['household_cash_delta_trn'])/d)
  self.ck(s['case']+str(y)+':Ctarget_sources',v['Ctarget']-sum(targets.values()))
  for key,target in targets.items():
   state=self.filtered.get(key,0.)
   if y>2026:state=(1-par['lambda_C'])*state+par['lambda_C']*target
   self.filtered[key]=state
   self.targets.append(dict(case=s['case'],year=y,channel=key,cash_source_nominal_trn=cashparts.get(key,'not_cash_or_combined_adjustment'),
    consumption_target_real_trn=target,filtered_C_state_real_trn=state,accounting_interpretation='REALIZED_TRAJECTORY_ARITHMETIC_NOT_INDEPENDENT_CAUSAL_CONTRIBUTION'))
  self.ck(s['case']+str(y)+':C_filtered_sources',v['C']-sum(self.filtered.values()))
  self.midpoints.append(dict(case=s['case'],year=y,**{k:v[k] for k in ['Ctarget','C','I','K','privI','privK','pubI','pubK','cash','feedback','policyshift','cashshift','govshift','insshift','investshift','primarychange','supply','capacity','basewant','saving','dividend','origI','flow','available','firmcash','interest','pb','assets','debt']},
    **{'policy_'+k:p[k] for k in ['labour_business_flat30_tax_delta_trn','household_financial20_tax_delta_trn','corporate_tax_delta_trn','wealth_tax_delta_trn','public_payroll_delta_trn','premium_relief_trn','in_kind_trn','pension_benefit_delta_trn','pension_fund_payout_trn','pension_return_trn']},
    VAT_HH_nominal=t['vat']['household']+lc['VAT_HH_cash_change_trn'],medical_HH_nominal=w['medical_only_household_cash_delta_trn'],
    quantity_nominal=w['quantity_nominal_volume_delta_trn'],quantity_price_replaced_nominal=w['quantity_replaced_price_benefit_trn'],
    service_nominal=w['service_production_nominal_delta_trn'],other_cash_unidentified=cashparts['other_cash_unidentified'],
    lagged_wage_factor=co.dynamic_rows[-1]['wage_base_factor'],lagged_profit_factor=co.dynamic_rows[-1]['corporate_profit_base_factor'],
    medical_health_labor_proxy=(self.current_medical or {}).get('health_effective_labor_added'),medical_health_labor_new_core_connection=False,
    extra_G_nominal=v['g'],extra_public_I_nominal=v['z']['pipay'],public_added_jobs=p['public_added_jobs'],
    phase_household=max(0.,min(1.,(y-2030+1)/3)),nominal_deflator=d))
  if s['case']=='BASE_REPLAY':
   for x in co.households:
    if x['year']==y:self.baseline_cells.append(dict(x))
 r.capture=types.MethodType(capture,r)
 return r,s
