import importlib.util,types,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
GAP='handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def build(root,out,definition,fixed_wages):
 G=module('tax_path_gap_runtime',root/GAP/'Attribution_Runtime.py');r,s=G.build(root,out,definition)
 raw=r.resolved_component
 a="   dt=(target30+target20-oldtax*(labourshare+finshare))*hhph if s.get('flat_hh') else 0.\n   hh_tax+=nh*(target30-oldtax*labourshare)*hhph/1e12 if s.get('flat_hh') else 0\n   financial_tax+=nh*(target20-oldtax*finshare)*hhph/1e12 if s.get('flat_hh') else 0"
 b="""   den=labourshare+finshare if s.get('prior_allocation_full',False) else 1.
   old_l=oldtax*labourshare/den;old_f=oldtax*finshare/den
   delta_l=(target30-old_l)*hhph if s.get('flat_hh') and not s.get('mute_labor_wedge') else 0.
   delta_f=(target20-old_f)*hhph if s.get('flat_hh') and not s.get('mute_financial_wedge') else 0.
   dt=delta_l+delta_f
   hh_tax+=nh*delta_l/1e12;financial_tax+=nh*delta_f/1e12"""
 assert raw.count(a)==1;raw=raw.replace(a,b)
 raw=raw.replace('baseline_allocated_national_tax_trn=nh*oldtax*(labourshare+finshare)/1e12',
  "baseline_allocated_national_tax_trn=nh*(old_l+old_f)/1e12,prior_labor_trn=nh*old_l/1e12,prior_financial_trn=nh*old_f/1e12,observed_all_national_tax_trn=nh*oldtax/1e12,local_tax_reference_trn=nh*local/1e12,labor_share=labourshare,financial_share=finshare,phase=hhph,target_labor_trn=nh*target30/1e12,target_financial_trn=nh*target20/1e12,labor_wedge_trn=nh*delta_l/1e12,financial_wedge_trn=nh*delta_f/1e12,baseline_premium_yen=premium")
 ns=dict(r.cm.old.ns);exec(compile(raw,'isolated_household_tax.py','exec'),ns);r.cm.old.Base.step=ns['Components'].step;r.tax_source=raw
 original=r.component
 def component(self):
  co,md=original();step=co.step
  def fixed_pension_step(y,md,prior):
   old=co.cfg['annual_worker_wage_yen'];actual=prior[-1]['nominal_wage_proxy_man']/co.cfg['sq_wage_nominal_man'][y-2027] if prior else 1.
   # Hold the same realized pension contribution/fund path during tax tests.
   co.cfg['annual_worker_wage_yen']=old*fixed_wages[y]/actual
   try:return step(y,md,prior)
   finally:co.cfg['annual_worker_wage_yen']=old
  co.step=fixed_pension_step;return co,md
 r.component=types.MethodType(component,r)
 return r,s
