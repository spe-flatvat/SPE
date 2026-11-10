"""Local DRAFT adapter: uses unchanged fixed SPE v6 functions; no GitHub writes.
Usage: python3 SPE_F_Provisional_Run_20261110.py ENGINE_DIR INPUT_JSON OUTPUT_DIR
"""
import csv,dataclasses,hashlib,json,math,sys
from pathlib import Path
def main():
 engine,inp,out=map(Path,sys.argv[1:4]);engine=engine.resolve();out.mkdir(exist_ok=True)
 sys.dont_write_bytecode=True;sys.path.insert(0,str(engine))
 from prototype import SimulationState,transition_year,transition_year_demographics
 from m14_wage_anchor import wage_growth_rate,interpolate_wage
 c=json.loads(inp.read_text()); anchors={int(y):float(v) for y,v in c['wage_anchor_man_yen']['anchors'].items()}
 def pw(table,t):
  return [r['value'] for r in table if r['from']<=t][-1]
 def params(t):
  risk=sum(r['pct'] for r in c['risk_shock_pct']['rules'] if (r['type']=='once' and t==r['year']) or (r['type']=='every' and t>=r['start'] and (t-r['start'])%r['step']==0)) /100
  m=c['migration']; migration=0 if t<m['ramp_start'] else m['steady_per_year']*min((t-m['ramp_start']+1)/m['ramp_years'],1)
  d=dict(death_rate_coefficient=c['death_rate_coefficient']['value'],birth_decline_coefficient=c['birth_decline_coefficient']['value'],phi=c['phi']['value'],real_wage_growth_rate=0 if t==2026 else wage_growth_rate(anchors,t),net_migration=migration)
  return {**d,'aging_drag':pw(c['aging_drag_pp']['table'],t)/100,'base_growth_rate':c['base_growth_rate_pct']['value']/100,'consumption_stimulus_effect':pw(c['policy_effects_pct']['consumption_stimulus'],t)/100,'investment_promotion_effect':pw(c['policy_effects_pct']['investment_promotion'],t)/100,'education_effect':pw(c['policy_effects_pct']['education'],t)/100,'risk_shock':risk,'alpha':c['alpha']['value'],'base_inflation_rate':c['base_inflation_rate_pct']['value']/100,'risk_event_inflation_impact':c['inflation_extra_pp']['by_year'].get(str(t),0)/100,'consumption_tax_transitional_factor':0.0,'tax_elasticity':pw(c['tax_elasticity']['table'],t),'expenditure_growth':pw(c['expenditure_growth_pct']['table'],t)/100,'tax_event_factor':c['tax_factor_by_year'].get(str(t),1.0),'tax_cap_ratio':c['tax_cap_ratio_of_nominal_gdp']['value']}
 allparams={t:params(t) for t in range(2026,2056)};rows=[];tests=[]
 for case,first,initial_year in [('F_2026_INITIAL_29',2027,2026),('F_2026_TRANSITION_30',2026,2025)]:
  s0=c['initial_state_2025_end'];st=SimulationState(year=initial_year,**{k:v for k,v in s0.items() if k!='tag'})
  def row(kind,g=None):
   return {'case':case,'row_kind':kind,**dataclasses.asdict(st),'funding_gap_proxy':max(st.expenditure-st.tax_revenue,0),'real_wage_anchor_man_yen':interpolate_wage(anchors,st.year),'tax_to_gdp_pct':st.tax_revenue/st.nominal_gdp*100,'real_growth_pct':'' if g is None else g*100}
  if first==2027:rows.append(row('INITIAL_STATE'))
  for t in range(first,2056):
   p=allparams[t]; prev=st
   d=transition_year_demographics(previous_state=prev,**{k:p[k] for k in ['death_rate_coefficient','birth_decline_coefficient','phi','real_wage_growth_rate','net_migration']})
   args={k:v for k,v in p.items() if k not in ['expenditure_growth','tax_event_factor','tax_cap_ratio']}
   args['total_population_growth_rate']=d.population/prev.population-1
   r=transition_year(prev,**args)
   assert r.demographic_state==d
   nom=prev.nominal_gdp*(1+r.nominal_gdp_growth_rate)
   tax=min(r.tax_revenue_before_cap*p['tax_event_factor'],nom*p['tax_cap_ratio'])
   st=SimulationState(year=t,real_gdp=prev.real_gdp*(1+r.real_gdp_growth_rate),nominal_gdp=nom,tax_revenue=tax,expenditure=prev.expenditure*(1+p['expenditure_growth']),population=d.population,deaths=d.deaths,births=d.births)
   assert all(math.isfinite(v) and v>=0 for v in dataclasses.asdict(st).values())
   assert st.tax_revenue<=st.nominal_gdp*.30+1e-9
   assert abs(st.population-(prev.population+st.births-st.deaths+p['net_migration']))<1e-6
   rows.append(row('ENGINE_TRANSITION',r.real_gdp_growth_rate))
  case_rows=[r for r in rows if r['case']==case]
  assert [r['year'] for r in case_rows]==list(range(2026,2056))
  tests.append({'case':case,'rows':len(case_rows),'transitions':2056-first,'real_gdp_2055':st.real_gdp,'population_2055':st.population,'tax_revenue_2055':st.tax_revenue,'expenditure_2055':st.expenditure,'funding_gap_2055':max(st.expenditure-st.tax_revenue,0),'max_tax_to_gdp_pct':max(r['tax_to_gdp_pct'] for r in case_rows),'cagr_pct':((st.real_gdp/s0['real_gdp'])**(1/(2056-first))-1)*100,'first_zero_gap_year':next((r['year'] for r in case_rows if r['funding_gap_proxy']==0),None)})
 def write(name,rs):
  with (out/name).open('w',newline='',encoding='utf-8') as f:
   w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
 write('SPE_F_Annual_Results_DRAFT_20261110.csv',rows)
 write('SPE_F_Annual_Inputs_Expanded_DRAFT_20261110.csv',[{'year':y,**p} for y,p in allparams.items()])
 summary={'input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),'engine_files':{n:hashlib.sha256((engine/n).read_bytes()).hexdigest() for n in ['prototype.py','m14_wage_anchor.py']},'cases':tests,'numerical_checks':'PASS: finite/nonnegative stocks, population conservation, tax cap, demographic consistency, complete years','python':sys.version}
 (out/'run_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
