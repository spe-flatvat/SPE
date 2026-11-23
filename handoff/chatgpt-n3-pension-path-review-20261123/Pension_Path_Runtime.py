import importlib.util,types,os,copy
from pathlib import Path
GAP='handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def build(root,out,d,fixed_wages):
 G=module('pension_path_gap_runtime',root/GAP/'Attribution_Runtime.py');r,s=G.build(root,out,d)
 # Keep the household labor/financial tax block's actual base and prior tax
 # at the pinned trajectory. Other HH incomes/premiums and pension wages remain endogenous.
 raw=r.resolved_component
 a="oldtax=h['stats']['income_tax_mean_paid_yen'][q]*h['stats']['income_tax_paid_per2000'][q]/2000*idx"
 b=a+"*ext.get('tax_base_wage_ratio',1.)"
 assert raw.count(a)==1;raw=raw.replace(a,b)
 a='target30=income*labourshare*.30;target20=income*finshare*.20'
 b="target30=income*labourshare*.30*ext.get('tax_base_wage_ratio',1.);target20=income*finshare*.20*ext.get('tax_base_wage_ratio',1.)"
 assert raw.count(a)==1;raw=raw.replace(a,b)
 raw=raw.replace('labour_business_30_gross_base_trn=nh*income*labourshare/1e12','labour_business_30_gross_base_trn=nh*income*labourshare/1e12*ext.get(\'tax_base_wage_ratio\',1.)').replace('financial20_gross_base_trn=nh*income*finshare/1e12','financial20_gross_base_trn=nh*income*finshare/1e12*ext.get(\'tax_base_wage_ratio\',1.)')
 if d.get('cohort_mode')=='WORKING_AGE_ONLY':
  a='[(32,.65),(52,.25),(67,.08),(72,.02)]';b='[(32,.65/.9),(52,.25/.9)]'
  assert raw.count(a)==1;raw=raw.replace(a,b)
 ns=dict(r.cm.old.ns);exec(compile(raw,'isolated_pension_path_component','exec'),ns);r.cm.old.Base.step=ns['Components'].step;r.pension_source=raw
 r.cohort_trace=[];r.return_trace=[]
 original=r.component
 def component(self):
  co,md=original();step=co.step
  def pension_step(y,md,prior):
   old=co.cfg.get('tax_base_wage_ratio');actual=prior[-1]['nominal_wage_proxy_man']/co.cfg['sq_wage_nominal_man'][y-2027] if prior else 1.
   co.cfg['tax_base_wage_ratio']=fixed_wages[y]/actual
   before={(z['entry_year'],z['age']):z['assets'] for z in co.cohorts}
   try:p=step(y,md,prior)
   finally:
    if old is None:co.cfg.pop('tax_base_wage_ratio',None)
    else:co.cfg['tax_base_wage_ratio']=old
   pen=co.pension[-1];gain=pen['fund_return_trn'];grant=0.
   if d.get('return_source')=='GOVERNMENT_TRANSFER':
    grant=gain;p['policy_government_cost_delta_trn']+=grant
    p['policy_partial_public_balance_trn']=p['policy_tax_delta_trn']-p['policy_government_cost_delta_trn']+p['policy_insurer_cash_delta_trn'];p['policy_budget_unclosed_trn']=-p['policy_partial_public_balance_trn']
    # This is explicitly a funded transfer guarantee, not investment return.
    pen['government_fund_credit_transfer_trn']=grant;pen['return_source_residual_OPEN_trn']=0.
   mode=d.get('return_source','DOMESTIC_HH');hh=gain if mode=='DOMESTIC_HH' else 0.;foreign=gain if mode=='EXTERNAL_ISSUER' else 0.;unallocated=gain-hh-foreign-grant
   self.return_trace.append(dict(case=d['case'],year=y,legacy_booked_fund_return_trn=gain,effective_investment_return_trn=0. if grant else gain,
    domestic_HH_property_income_debit_trn=hh,external_issuer_payment_trn=foreign,government_fund_transfer_trn=grant,
    source_unallocated_trn=unallocated,source_identification='CONDITIONAL_NOT_EMPIRICALLY_IDENTIFIED' if mode!='UNALLOCATED' else 'NOT_IDENTIFIED_NEGATIVE_CONTROL',
    real_world_portfolio_or_ownership_known=False,new_GDP_from_return_trn=0.))
   for z in co.cohorts:
    k=z['entry_year'],z['age'];begin=before.get(k,0.);ret=begin*co.cfg['fund_return'];entry=z['assets'] if k not in before else 0.;paid=begin+ret+entry-z['assets']
    self.cohort_trace.append(dict(case=d['case'],year=y,entry_year=k[0],entry_age=k[1],age=k[1]+y-k[0],assets_begin_trn=begin,
      contribution_trn=entry,booked_return_trn=ret,payout_trn=paid,assets_end_trn=z['assets'],cohort_mode=d.get('cohort_mode','LEGACY_PROXY_32_52_67_72')))
   return p
  co.step=pension_step;return co,md
 r.component=types.MethodType(component,r)
 source=d.get('return_source','DOMESTIC_HH');os.environ['SPE_PENSION_MODE']='DOMESTIC_TRANSFER' if source=='DOMESTIC_HH' else 'FOREIGN_INCOME' if source=='EXTERNAL_ISSUER' else 'LEGACY'
 return r,s
