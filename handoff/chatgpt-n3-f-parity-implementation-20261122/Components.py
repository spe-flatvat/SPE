"""Explicit N3 candidate annual bases and institutional triggers on pinned ledgers."""
import importlib.util,copy,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
f=ROOT/'handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Components.py'
sp=importlib.util.spec_from_file_location('pinned_n3_gap_components',f);old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
phase=old.phase;quantity_channels=old.quantity_channels
class Components(old.Components):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.dynamic_rows=[];self.events=[];self.funding_rows=[];self.firm_cash=0.;self.firm_I=0.;self.gini_relief=False
 def step(self,y,md,prior):
  spec=md.s;active='parity' in spec or spec['id'].startswith('PARITY_');dynamic=spec.get('dynamic_bases',False);i=y-2026
  wage=output=1.
  if dynamic and prior:
   r=prior[-1];j=i-1
   wage=r['nominal_wage_proxy_man']/self.cfg['sq_wage_nominal_man'][j]
   output=r['nominal_gdp_trn']/self.cfg['core_nominal'][j]
   assert wage>0 and output>0
  before=self.cfg;cfg=copy.deepcopy(before)
  if dynamic:
   cfg['income_scale']=before.get('income_scale',1.04)*wage
   cfg['core_nominal'][i]*=output
   cfg['annual_worker_wage_yen']=before.get('annual_worker_wage_yen',4000000)*wage
  if y<spec.get('corporate_investment_start',2026):cfg['corporate_investment_response']=0.
  observed=(spec.get('gini_observations') or {}).get(str(y-1))
  gini_trigger=active and y==2035 and observed is not None and observed>spec.get('gini_reference',.38)
  # Duration and magnitude absent from policy: only explicit candidate duration.
  self.gini_relief=gini_trigger if y==2035 else self.gini_relief and y<=spec.get('gini_relief_end_candidate',2035)
  if self.gini_relief and spec.get('gini_relief_increment_candidate') is not None:
   cfg['relief_maximum']=min(1.,cfg.get('relief_maximum',.35)+spec['gini_relief_increment_candidate'])
  self.cfg=cfg
  try:r=super().step(y,md,prior)
  finally:self.cfg=before
  if active:
   r['n3_effective_labor_delta']=r['public_added_jobs']*spec.get('labor_effectiveness',.8)
   # Policy's 2035 evaluation uses lagged income, not GDP growth or future GDP.
   income_growth=None
   if len(prior)>=2:
    a,b=prior[-2:];ka=a.get('parity_real_cash_income_per_person');kb=b.get('parity_real_cash_income_per_person')
    if ka is not None and kb is not None and ka>0:income_growth=100*(kb/ka-1)
   if spec.get('kpi_signal')=='LAGGED_REAL_CASH_INCOME_GROWTH':
    # Base method's GDP-based candidate can never leak into this new switch.
    prior_frozen=self.events[-1]['vat_frozen'] if self.events else False
    evaluate=y==spec.get('kpi_evaluation_year',2035) if spec.get('kpi_once',True) else y>=2035
    trigger=evaluate and spec.get('kpi',False) and income_growth is not None and income_growth<spec['kpi_growth_threshold_pct']
    self.frozen=prior_frozen or trigger
    self.structures[-1].update(kpi_previous_growth_pct=None,kpi_income_growth_pct=income_growth,kpi_signal='LAGGED_REAL_CASH_INCOME_PER_PERSON',kpi_freeze_candidate=self.frozen if spec.get('kpi') else None)
   lastreturn=self.pension[-1]['fund_return_trn'] if spec.get('pension75') else None
   insurance_signal=bool(active and y==2035 and spec.get('insurance_return_floor_candidate') is not None and spec.get('fund_return',cfg.get('fund_return',.02))<spec['insurance_return_floor_candidate'])
   self.events.append(dict(year=y,previous_income_growth_pct=income_growth,evaluation_year=2035,vat_frozen=self.frozen if spec.get('kpi') else False,gini_lagged_observation=observed,gini_relief_trigger=gini_trigger,gini_relief_active_candidate=self.gini_relief,insurance_underperformance_signal=insurance_signal,insurance_competition_effect='STRUCTURE_ONLY_NO_PRODUCTIVITY_COEFFICIENT',fund_return_trn=lastreturn,policy_selection='CANDIDATE_NOT_ADOPTED'))
  self.dynamic_rows.append(dict(year=y,enabled=dynamic,lag_year=y-1 if prior else None,wage_base_factor=wage,corporate_profit_base_factor=output,household_income_scale=cfg.get('income_scale',1.04),pension_contribution_wage_yen=cfg.get('annual_worker_wage_yen',4000000),new_household_income_added_trn=0.,new_corporate_profit_added_trn=0.,method='REPLACE_COMPONENT_BASES_WITH_LAGGED_ACTUAL_NOT_ADD_PRIOR_GDP'))
  if active:
   d=md.deflators[i];pars=self.cfg['macro_parameters'];lam=spec.get('macro_overrides',{}).get('lambda_I',pars['lambda_I'])
   initial=self.firm_cash;priorI=self.firm_I;target=r['policy_investment_delta_trn']
   if i:self.firm_I=(1-lam)*priorI+lam*target/d
   saving=-r['corporate_tax_delta_trn'];dividend=r['dividend_delta_trn'];actual=self.firm_I*d
   self.firm_cash+=saving-dividend-actual
   self.funding_rows.append(dict(year=y,source_tax_saving_trn=saving,dividend_paid_trn=dividend,target_investment_nominal_trn=target,realized_investment_real_trn=self.firm_I,realized_investment_nominal_trn=actual,cash_begin_trn=initial,cash_end_trn=self.firm_cash,cash_change_trn=self.firm_cash-initial,external_funding_need_partial_trn=max(0.,-self.firm_cash),residual_trn=self.firm_cash-initial-saving+dividend+actual,source='EXISTING_CORPORATE_TAX_SAVING_ONLY_NO_SECOND_INVESTMENT'))
  return r
