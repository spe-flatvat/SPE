"""Run common ON/OFF through the existing SQ engine without F policy activation."""
import json,copy
from pathlib import Path
from Model import load,dump,read
from FMedical import Medical
P=Path(__file__).resolve().parent

def run():
 c=json.loads((P/'Inputs.json').read_text());root,edu,ec,integ,v,vc=load(c)
 fixed=[r for r in read(P.parent/'f-education-20261121/Annual.csv') if r['case']=='SQ_FIXED']
 defs=[float(r['common_deflator']) for r in fixed];pops=[float(r['population']) for r in fixed]
 annual=[];accounts=[];commons=[]
 for enabled in [False,True]:
  s={**c['defaults'],'id':'SQ_COMMON_ON' if enabled else 'SQ_COMMON_OFF_REPLAY','common':enabled,'copay':False,'provider':False}
  md=Medical(c,s,defs,pops);original_base=integ.make_base
  def base(*a,**kw):
   r=original_base(*a,**kw);md.trajectory=r[3]['d'];md.elder=r[3]['elder'];return r
  integ.make_base=base
  def hook(engine,pol):
   assert pol=='SQ'
   source=engine['_integration_source'];ns=dict(engine['run_path'].__globals__);ns['_medical']=md
   def sub(a,b):
    nonlocal source
    assert source.count(a)==1,a
    source=source.replace(a,b)
   sub("t=c['_trajectory'][i];sq=c['_common_trajectory'][i]", "t=c['_trajectory'][i];sq=c['_common_trajectory'][i]\n        w=_medical.step(y)")
   sub("invest_nom=value(invflow)+value(firm['investment'])+f['investment']+value(med['hubs'])", "invest_nom=value(invflow)+value(firm['investment'])+f['investment']+value(med['hubs'])+w['investment_nominal_delta_trn']")
   sub("cash+=_pension[i]['household_cash_delta_trn']", "cash+=_pension[i]['household_cash_delta_trn']+w['household_cash_delta_trn']")
   sub("desired=coreY+p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite", "desired=coreY+p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+w['service_production_nominal_delta_trn']/coreD")
   # Diagnostic GDP identity repeats the production equation.
   source=source.replace("p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite-unmet)","p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+w['service_production_nominal_delta_trn']/coreD-unmet)")
   sub("taxdiag=tax+direct;", "direct+=w['medical_financing_direct_tax_trn'];expenditure+=w['government_cost_delta_trn']\n        taxdiag=tax+direct;")
   sub("if not enabled:req(close(cash,f['household']) and close(direct,f['direct_tax']) and close(invest_nom,f['investment']) and close(education_nom,0.),'StatusQuo VAT-only changes; no other F channels')", "if not enabled:req(close(cash,f['household']+w['household_cash_delta_trn']) and close(direct,f['direct_tax']+w['medical_financing_direct_tax_trn']) and close(invest_nom,f['investment']+w['investment_nominal_delta_trn']) and close(education_nom,0.),'SQ only VAT reference and explicit common policy flows')")
   exec(compile(source,'common_SQ_adapter.py','exec'),ns);return ns
  integ._education_hook=hook
  try: rows,inc,sec,b,raw,cc=integ.execute(v,vc,dict(id=s['id'],policy='SQ',E=False,F=False,PEN=False,VAT=False,A=False,B=False,C=False))
  finally:integ.make_base=original_base
  for r,w,co in zip(rows,md.rows,md.common):
   annual.append(dict(**r,common_policy=enabled,comparison_scope='PAIRED_SQ_COMMON_ON_OFF_EXISTING_ENGINE',**{k:val for k,val in w.items() if k not in r}))
   accounts.append(dict(case=s['id'],**w));commons.append(dict(case=s['id'],**co))
 dump(P/'SQ_Common_Annual.csv',annual);dump(P/'SQ_Common_Accounts.csv',accounts);dump(P/'SQ_Common_Patients.csv',commons)
 by={(r['case'],r['year']):r for r in annual};comparison=[]
 for y in range(2026,2056):
  on=by['SQ_COMMON_ON',y];off=by['SQ_COMMON_OFF_REPLAY',y]
  for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn']:
   comparison.append(dict(year=y,metric=k,common_on=on[k],common_off=off[k],common_effect=on[k]-off[k],original_SQ_fixed=float(fixed[y-2026][k]),off_vs_fixed=off[k]-float(fixed[y-2026][k]),status='PARTIAL_MACRO_CONNECTION_VAT_VOLUME_HEALTH_QOL_UNCONNECTED'))
 dump(P/'SQ_Common_Comparison.csv',comparison)
if __name__=='__main__':run()
