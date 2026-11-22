"""Asserted final-source adapters. Shared SQ and risk parameters are untouched."""
from pathlib import Path
P=Path(__file__).resolve().parent
AUDIT_KEYS=['capital_previous_real','capital_replacement_investment_real_trn','capital_total_real_trn','I_policy_real_trn']
def patch(source,s):
 def sub(a,b):
  nonlocal source
  assert source.count(a)==1,a
  source=source.replace(a,b)
 # Emit same runtime source for inspection before any annual execution.
 if s['id']=='PARITY_CONNECTED_CANDIDATE':(P/'Resolved_Macro_Source.py.txt').write_text(source)
 active=s['id'].startswith('PARITY_')
 if active:
  sub("p,bprof,mig,enabled,omit=configure(c,spec);", "p,bprof,mig,enabled,omit=configure(c,spec);p.update(_parity_spec.get('macro_overrides',{}));")
  # Own-case-only carry ablation; no change to shared SQ inputs/risks.
  sub("        supply=p['capital_yield']", "        if not _parity_spec.get('macro_carry',True):K=0.\n        supply=p['capital_yield']")
 sub('        Ctarget=', '        parity_Cprev=C;parity_Iprev=I;parity_prior_gap=gap\n        Ctarget=')
 sub('        rows.append(r);prevN=N;prevY=Y', '''        r.update(capital_replacement_investment_real_trn=replacement,parity_supply_real_trn=supply,parity_investment_nominal_trn=invest_nom,parity_consumption_target_real_trn=Ctarget,parity_prior_gap_trn=parity_prior_gap,parity_C_previous_real_trn=parity_Cprev,parity_I_previous_real_trn=parity_Iprev,parity_depreciation=p['depreciation'],parity_lambda_C=p['lambda_C'],parity_lambda_I=p['lambda_I'],parity_generic_mpc=p['generic_mpc'],parity_domestic_share=p['domestic_share'],parity_capital_yield=p['capital_yield'],parity_education_supply_real_trn=p['education_yield']*(1-p['education_decay'])*Hprev,parity_capacity_absorption=p['capacity_absorption'],parity_unmet_real_trn=unmet,parity_services_real_trn=w['service_production_nominal_delta_trn']/coreD,parity_nominal_wage_man=nominalwage_proxy,parity_core_nominal_trn=coreN,parity_household_cash_trn=cash,parity_income_feedback_trn=feedback,parity_carry=_parity_spec.get('macro_carry',True),parity_real_cash_income_per_person=(r['household_disposable_nominal_trn']-f['household'])/coreD/pop)
        rows.append(r);prevN=N;prevY=Y''')
 return source
