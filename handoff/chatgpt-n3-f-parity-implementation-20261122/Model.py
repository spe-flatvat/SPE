#!/usr/bin/env python3
"""Extend pinned N3 runtime without changing any source policy or source files."""
import argparse,sys,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(P))
def run(inputs,engine,source,out):
 old=ROOT/'handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Model.py'
 text=old.read_text()
 assert hashlib.sha256(old.read_bytes()).hexdigest()=='9a33fb0946a9fe3087574f5d5cff1bf1e7f7e8b99570173169a31e0ac25b1cef'
 def sub(a,b):
  nonlocal text
  assert text.count(a)==1,a
  text=text.replace(a,b)
 sub('from Gap_Components import Components,phase,quantity_channels','from Components import Components,phase,quantity_channels')
 sub("self.components=Components(ecfg,data,pen);", "self.components=Components(ecfg,data,pen);self.components.cfg['sq_wage_nominal_man']=[r['parity_nominal_wage_man'] for r in engine_audit if r['case']=='SQ_COMMON_ON'];")
 sub("extensions={z['id']:z for z in cfg['cases']};", "cases=[z for z in cases if not cfg.get('execution_case_filter') or z[0] in cfg['execution_case_filter']];extensions={z['id']:z for z in cfg['cases']};")
 # Retain original dependency checks at original __file__, all pinned sources.
 sub("exec(compile(body,'n3_expanded_runtime_adapter.py','exec'),ns)",'''needle="        exec(compile(source,'n3_medical_on_SQ_adapter.py','exec'),ns);return ns"
 assert body.count(needle)==1
 body=body.replace(needle,"        from Macro_Adapter import patch\\n        source=patch(source,_md.s);ns['_parity_spec']=_md.s\\n        exec(compile(source,'n3_medical_on_SQ_adapter.py','exec'),ns);return ns")
 exec(compile(body,'n3_expanded_runtime_adapter.py','exec'),ns)''')
 # Capture all actual annual macro states, not only the old small display set.
 sub("'tax_macro_trn','tax_diagnostic_trn'","'capital_previous_real','capital_replacement_investment_real_trn','capital_total_real_trn','I_policy_real_trn','parity_supply_real_trn','parity_investment_nominal_trn','parity_consumption_target_real_trn','parity_prior_gap_trn','parity_C_previous_real_trn','parity_I_previous_real_trn','parity_depreciation','parity_lambda_C','parity_lambda_I','parity_generic_mpc','parity_domestic_share','parity_capital_yield','parity_education_supply_real_trn','parity_capacity_absorption','parity_unmet_real_trn','parity_services_real_trn','parity_nominal_wage_man','parity_core_nominal_trn','parity_household_cash_trn','parity_income_feedback_trn','parity_carry','tax_macro_trn','tax_diagnostic_trn'")
 # Existing case accounting remains available; new firm stock/event audits are separate.
 sub("# Preserve immutable old outputs",'''M.dump(out/'Dynamic_Base_Audit.csv',[dict(case=md.s['id'],**r) for md in objects for r in md.components.dynamic_rows])
 M.dump(out/'Corporate_Funding_Stock.csv',[dict(case=md.s['id'],**r) for md in objects for r in md.components.funding_rows])
 M.dump(out/'KPI_Events.csv',[dict(case=md.s['id'],**r) for md in objects for r in md.components.events])
 # Preserve immutable old outputs''')
 ns={'__file__':str(old),'__name__':'n3_parity_runtime'}
 exec(compile(text,str(P/'Model.py'), 'exec'),ns)
 ns['run'](inputs,engine,source,out)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('inputs');a.add_argument('--engine',required=True);a.add_argument('--source',required=True);a.add_argument('--outdir',required=True);x=a.parse_args();run(x.inputs,x.engine,x.source,x.outdir)
