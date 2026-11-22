#!/usr/bin/env python3
"""Read fixed SPE sources, trace unchanged SQ engine, independently decompose it.
Stdlib + git. Diagnostic counterfactuals never edit model inputs/coefficients.
"""
import argparse,csv,json,math,hashlib,sys,subprocess,importlib.util,inspect,copy
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
N3='37c3399f9c553673a79ba1298fc68d758a77055e';CLAUDE='ba08c45d4ecb99defecb8416c8d63e0cbfde8cb4'
N3DIR='handoff/chatgpt-n3-f-parity-implementation-20261122'
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8')))
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def pin(root,commit,path,receipts):
 if subprocess.run(['git','cat-file','-e',commit],cwd=root,capture_output=True).returncode:subprocess.run(['git','fetch','origin',commit],cwd=root,check=True)
 b=subprocess.check_output(['git','show',commit+':'+path],cwd=root)
 a=(root/path).read_bytes() if (root/path).exists() else None
 if a is not None:assert a==b,(commit,path)
 receipts.append(dict(commit=commit,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),local_matches_fixed_git_object=a==b if a is not None else None))
 return b

def capture(root,out,draft):
 n3=root/N3DIR;cfg=json.loads((n3/'Inputs.json').read_text());original=copy.deepcopy(cfg);cfg['execution_case_filter']=['SQ_COMMON_ON']
 assert {k:v for k,v in cfg.items() if k!='execution_case_filter'}==original
 inp=out/'SQ_Isolated_Execution_Input.json';inp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
 traces=[];seen=set();params={};trajectory={}
 def local(frame,event,arg):
  if event=='line':
   v=frame.f_locals;r=v.get('r');y=v.get('y')
   if isinstance(r,dict) and r.get('year')==y and y not in seen and 'parity_supply_real_trn' in r:
    # r is final only after the diagnostic-only update added by the fixed N3 adapter.
    seen.add(y);params.update(copy.deepcopy(v['p']));trajectory.update(d=copy.deepcopy(v['c']['_trajectory']),sq=copy.deepcopy(v['c']['_common_trajectory']))
    keys=['coreY','coreN','coreD','Y','N','labor','effective_labor','labor_anchor','nonlabor_factor','coreY_anchor','growth','risk','inflation','lg','C','I','K','Kprev','H','Hprev','supply','desired','capacity','unmet','pressure','tax','direct','cash','feedback','replacement','education_nom','education_level','finite','prevY','prevN','enabled']
    traces.append(dict(year=y,**{k:v.get(k) for k in keys},link=v['spec'].get('_link'),macro_row=copy.deepcopy(r),demography=copy.deepcopy(v['t']),common_demography=copy.deepcopy(v['sq']),medical=copy.deepcopy(v['w'])))
  return local
 def trace(frame,event,arg):
  if event=='call' and frame.f_code.co_name=='run_path' and frame.f_code.co_filename=='n3_medical_on_SQ_adapter.py':return local
 spec=importlib.util.spec_from_file_location('fixed_n3_execution',n3/'Model.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 old=sys.gettrace();sys.settrace(trace)
 try:mod.run(inp,root,draft,out/'runtime')
 finally:sys.settrace(old)
 assert len(traces)==30,len(traces)
 (out/'SQ_Unchanged_Engine_Trace.json').write_text(json.dumps(dict(parameters=params,trajectory=trajectory,years=traces),ensure_ascii=False,indent=2)+'\n')
 return dict(parameters=params,trajectory=trajectory,years=traces)

def run(root,out,draft):
 out.mkdir(parents=True,exist_ok=True);receipts=[]
 for path in ['Inputs.json','Model.py','Components.py','Macro_Adapter.py','Resolved_Macro_Source.py.txt','Source_Identity.json','Manifest.json','results/Annual_DOMESTIC_TRANSFER.csv','results/SQ_F_N3_Annual_Comparison.csv','results/Verification.json']:
  pin(root,N3,N3DIR+'/'+path,receipts)
 for path in ['handoff/f-foreign-quantity-20261120/Model.py','handoff/f-common-endoflife-finalization-20261121/Annual.csv','handoff/f-tx01-tx03-20261118/SPE_F_TX_Inputs_DRAFT_20261118.json']:
  pin(root,N3,path,receipts)
 for name in ['N3_F_Parity_Independent_Summary_DRAFT_20261122.json','SPE_N3_F_Parity_Limited_Independent_Verification_Report_DRAFT_20261122.md']:
  b=pin(root,CLAUDE,'handoff/claude-n3-f-parity-verification-20261122/'+name,receipts)
  if name.endswith('json'):(out/'Reused_Claude_Summary.json').write_bytes(b)
 if not draft.exists():
  commit='3c77eafc2073fdaba4c129164817d2f57c9421b9'
  subprocess.run(['git','fetch','origin',commit],cwd=root,check=True)
  subprocess.run(['git','worktree','add','--detach',str(draft),commit],cwd=root,check=True)
 data=capture(root,out,draft)
 (out/'Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 analyze(root,out,data,receipts)

def analyze(root,out,data,receipts):
 p=data['parameters'];rs=data['years'];alpha=p['labor_response'];anchor=rs[0];fixed=rd(root/N3DIR/'results/Annual_DOMESTIC_TRANSFER.csv');sq={int(r['year']):r for r in fixed if r['case']=='SQ_COMMON_ON'}
 annual=[];counter=[];dem=[];comparison=[];errs=[];checks=[]
 def check(name,value,tolerance=2e-8):
  checks.append(dict(check=name,error=value,tolerance=tolerance,pass_=abs(value)<=tolerance))
 def risks(y):return dict(conflict=p['conflict_gdp_loss'] if y==2027 else 0.,quake=p['quake_gdp_loss'] if y==2031 else 0.,disaster=p['disaster_gdp_loss'] if y>=p['disaster_anchor'] and (y-p['disaster_anchor'])%3==0 else 0.,climate=p['climate_gdp_loss'] if y>=p['climate_anchor'] and (y-p['climate_anchor'])%2==0 else 0.)
 factors={k:1. for k in ['ACTUAL','NO_BASE_GROWTH_TERM','NO_REAL_RISK_TERMS','NO_CONFLICT','NO_QUAKE','NO_RECURRING_DISASTER','NO_CLIMATE']};initialL=anchor['labor'];initialP=anchor['demography']['population'];prevC=anchor['coreY'];prevY=anchor['Y'];prevK=anchor['K'];prevN=anchor['N'];prevCoreN=anchor['coreN'];prevTax=anchor['tax'];prevD=anchor['coreD'];prevComponents=None
 cumulative={};maxima={};fref={int(r['year']):r for r in rd(root/'handoff/f-common-endoflife-finalization-20261121/Annual.csv') if r['case']=='LATEST_F'};nref={int(r['year']):r for r in fixed if r['case']=='PARITY_CONNECTED_CANDIDATE'}
 for i,t in enumerate(rs):
  y=t['year'];pop=t['demography']['population'];L=t['labor'];q=(L/rs[i-1]['labor'])**alpha if i else 1.;rr=risks(y) if i else dict.fromkeys(risks(y),0.);r=sum(rr.values());G=1+p['base_growth']-r if i else 1.
  # Separate reconstruction uses only fixed coefficients, labor levels and shock calendar.
  reconCore=prevC*G*q if i else anchor['coreY']
  components=dict(supply_absorption=p['capacity_absorption']*t['supply'],consumption_adjustment=t['C'],policy_investment=t['I'],education_demand=t['education_nom']/t['coreD']+t['education_level']+t['finite'],common_service=t['medical']['service_production_nominal_delta_trn']/t['coreD'],supply_constraint=-t['unmet'])
  reconY=reconCore+sum(components.values());dY=t['Y']-prevY if i else 0.
  row=dict(year=y,real_GDP_trn=t['Y'],fixed_real_GDP_trn=float(sq[y]['real_gdp_trn']),reconstructed_real_GDP_trn=reconY,reconstruction_error_trn=reconY-float(sq[y]['real_gdp_trn']),nominal_GDP_trn=t['N'],common_deflator=t['coreD'],annual_real_growth_pct=100*(t['Y']/prevY-1) if i else 0.,cumulative_real_change_trn=t['Y']-anchor['Y'],index_2026_100=t['Y']/anchor['Y']*100,core_real_GDP_trn=t['coreY'],real_GDP_change_trn=dY,population=pop,domestic_employed=t['demography']['domestic_employed_conditional'],foreign_employed=t['demography']['foreign_employed_conditional'],effective_labor=L,effective_labor_growth_pct=100*(L/rs[i-1]['labor']-1) if i else 0.,base_growth_rate=p['base_growth'],labor_elasticity=alpha,actual_link=t['link'],real_risk_rate=r,nonlabor_factor=t['nonlabor_factor'],labor_level_factor=(L/initialL)**alpha,growth_additive_candidate_NOT_EXECUTED_pct=100*(p['base_growth']+alpha*t['lg']-r) if i else 0.,growth_executed_LEVEL_pct=t['growth']*100 if i else 0.,baseline_capital_real_trn=p['capital_ratio']*t['coreY'],additional_capital_real_trn=t['K'],total_capital_real_trn=p['capital_ratio']*t['coreY']+t['K'],replacement_investment_real_trn=t['replacement'],policy_investment_real_trn=t['I'],supply_gain_real_trn=t['supply'],supply_ceiling_real_trn=t['capacity'],unmet_real_trn=t['unmet'],household_consumption_real_proxy_trn=t['macro_row']['household_consumption_real_proxy_trn'],household_cash_delta_trn=t['cash'],income_feedback_nominal_trn=t['feedback'],macro_tax_trn=t['tax'],direct_tax_trn=t['direct'],tax_diagnostic_trn=t['tax']+t['direct'],observed_TFP=None,observed_total_real_investment=None,identified_causal_immigration_effect=None)
  row['contrib_base_growth_trn']=prevC*p['base_growth'] if i else 0.
  row['contrib_labor_trn']=prevC*(q-1) if i else 0.
  for name,risk in rr.items():row['contrib_'+name+'_trn']=-prevC*risk if i else 0.
  row['contrib_growth_risk_labor_interaction_trn']=prevC*(p['base_growth']-r)*(q-1) if i else 0.
  for name,value in components.items():row['contrib_'+name+'_trn']=value-(prevComponents[name] if prevComponents else value)
  additive=[k for k in row if k.startswith('contrib_')];row['additive_contribution_sum_trn']=sum(row[k] for k in additive);row['decomposition_residual_trn']=dY-row['additive_contribution_sum_trn']
  # Nested population/employment composition decomposition: an alternative to labor, not extra GDP.
  pp=pop/rs[i-1]['demography']['population'] if i else 1.;ss=(L/pop)/(rs[i-1]['labor']/rs[i-1]['demography']['population']) if i else 1.;qp=pp**alpha;qs=ss**alpha
  row['nested_population_labor_trn']=prevC*(qp-1) if i else 0.;row['nested_employment_mix_trn']=prevC*(qs-1) if i else 0.;row['nested_population_mix_interaction_trn']=prevC*(qp-1)*(qs-1) if i else 0.
  check('labor_nested_'+str(y),sum(row[k] for k in ['nested_population_labor_trn','nested_employment_mix_trn','nested_population_mix_interaction_trn'])-row['contrib_labor_trn'])
  if i:
   td=t['demography'];prev=rs[i-1];deltaP=pop-prev['demography']['population'];units=dict(births=td['births_calendar'],deaths=-td['deaths_calendar'],net_migration=td['foreign_net_migration'],population_reference_bridge=td['population_reference_bridge'])
   check('population_account_'+str(y),sum(units.values())-deltaP,2e-7)
   scale=row['nested_population_labor_trn']/deltaP if deltaP else 0.
   for name,units_value in units.items():row['nested_'+name+'_population_contribution_trn']=scale*units_value
   deltaL=L-prev['labor'];deltaDom=td['domestic_employed_conditional']-prev['demography']['domestic_employed_conditional'];deltaForeign=td['foreign_employed_conditional']-prev['demography']['foreign_employed_conditional']
   check('SQ_employment_components_'+str(y),deltaDom+deltaForeign-deltaL,2e-7)
   slope=row['contrib_labor_trn']/deltaL if deltaL else prevC*alpha/L
   row['nested_domestic_employment_trn']=slope*deltaDom;row['nested_foreign_employment_trn']=slope*deltaForeign
   check('capital_stock_identity_'+str(y),t['K']-(1-p['depreciation'])*prevK-t['I'])
   nominal=prevCoreN*(1+t['growth']+t['inflation']);check('core_nominal_formula_'+str(y),nominal-t['coreN'],1e-7)
   check('actual_nominal_formula_'+str(y),t['Y']*t['coreD']*(1+t['pressure'])-t['N'],1e-7)
   tax_before_quake=prevTax*(1+(t['N']/prevN-1)*p['elasticity']);qfactor=p['quake_tax_factor'] if y==2031 else 1.
   tax_after_quake=tax_before_quake*qfactor;tax_recon=min(tax_after_quake,t['N']*p['tax_cap_ratio'])
   row.update(tax_nominal_feedback_trn=tax_before_quake-prevTax,tax_quake_adjustment_trn=tax_after_quake-tax_before_quake,tax_cap_adjustment_trn=tax_recon-tax_after_quake,tax_reconstruction_error_trn=tax_recon-t['tax'])
   check('tax_reconstruction_'+str(y),tax_recon-t['tax'])
  else:
   for name in ['births','deaths','net_migration','population_reference_bridge']:row['nested_'+name+'_population_contribution_trn']=0.
   row.update(nested_domestic_employment_trn=0.,nested_foreign_employment_trn=0.,tax_nominal_feedback_trn=0.,tax_quake_adjustment_trn=0.,tax_cap_adjustment_trn=0.,tax_reconstruction_error_trn=0.)
  for key,value in row.items():
   if key.startswith('contrib_'):cumulative[key]=cumulative.get(key,0.)+value
  check('GDP_reconstructed_'+str(y),reconY-float(sq[y]['real_gdp_trn']))
  check('additive_decomposition_'+str(y),row['decomposition_residual_trn'])
  check('core_reconstructed_'+str(y),reconCore-t['coreY'])
  check('year_on_year_growth_'+str(y),row['annual_real_growth_pct']-t['macro_row']['real_growth_pct'])
  check('GDP_output_proxy_'+str(y),t['Y']-float(sq[y]['real_gdp_trn']))
  check('labor_output_'+str(y),L-float(sq[y]['macro_labor_force_population_proxy']),1e-4)
  check('base_risk_trace_'+str(y),r-t['risk'])
  # Fixed-input analytic ablations. Hold observed labor and demand wedge fixed.
  for name in factors:
   remove={'NO_CONFLICT':'conflict','NO_QUAKE':'quake','NO_RECURRING_DISASTER':'disaster','NO_CLIMATE':'climate'}.get(name)
   riskcf=0. if name=='NO_REAL_RISK_TERMS' else r-(rr.get(remove,0.) if remove else 0.)
   basecf=0. if name=='NO_BASE_GROWTH_TERM' else p['base_growth']
   if i:factors[name]*=1+basecf-riskcf
   cy=anchor['coreY']*factors[name]*(L/initialL)**alpha;cfY=cy+t['Y']-t['coreY']
   counter.append(dict(case=name,year=y,core_GDP_trn=cy,diagnostic_GDP_with_actual_demand_wedge_trn=cfY,difference_from_actual_trn=cfY-t['Y'],method='FIXED_LABOR_AND_ACTUAL_DEMAND_WEDGE_NOT_FULL_MODEL_COUNTERFACTUAL',additive=False,model_coefficients_changed=False))
  for name,lc in [('HOLD_EFFECTIVE_LABOR_2026',initialL),('HOLD_FOREIGN_JOBS_2026',t['demography']['domestic_employed_conditional']+anchor['demography']['foreign_employed_conditional']),('HOLD_DOMESTIC_JOBS_2026',anchor['demography']['domestic_employed_conditional']+t['demography']['foreign_employed_conditional'])]:
   cy=anchor['coreY']*t['nonlabor_factor']*(lc/initialL)**alpha
   counter.append(dict(case=name,year=y,core_GDP_trn=cy,diagnostic_GDP_with_actual_demand_wedge_trn=cy+t['Y']-t['coreY'],difference_from_actual_trn=cy-t['coreY'],method='FIXED_BASE_LABOR_LEVEL_ABLATION_NOT_NO_IMMIGRATION_FORECAST',additive=False,model_coefficients_changed=False))
  dem.append(dict(t['demography']))
  comparison.append(dict(year=y,SQ_real_GDP_trn=t['Y'],F_fixed_real_GDP_trn=float(fref[y]['real_gdp_trn']),N3_candidate_real_GDP_trn=float(nref[y]['real_gdp_trn']),F_minus_SQ_trn=float(fref[y]['real_gdp_trn'])-t['Y'],N3_minus_SQ_trn=float(nref[y]['real_gdp_trn'])-t['Y'],N3_policy_tax_delta_trn=float(nref[y]['policy_tax_delta_trn']),N3_household_cash_delta_trn=float(nref[y]['household_cash_delta_trn']),N3_scope='UNADOPTED_DOMESTIC_TRANSFER_CANDIDATE_NOT_SQ_CAUSE',F_scope='ff621006_FIXED_NOT_REEXECUTED'))
  annual.append(row);prevC=reconCore;prevY=t['Y'];prevK=t['K'];prevN=t['N'];prevCoreN=t['coreN'];prevTax=t['tax'];prevD=t['coreD'];prevComponents=components
 dump(out/'SQ_Annual_Growth_Decomposition_2026_2055.csv',annual);dump(out/'SQ_Fixed_Input_Ablations.csv',counter);dump(out/'SQ_Demography_Labor_Accounting.csv',dem);dump(out/'SQ_F_N3_Diagnostic_Comparison.csv',comparison)
 summary=[]
 for lo,hi in [(2026,2035),(2035,2045),(2045,2055),(2026,2055)]:
  selected=[r for r in annual if lo<r['year']<=hi];start=annual[lo-2026];end=annual[hi-2026]
  z=dict(start_year=lo,end_year=hi,start_real_GDP_trn=start['real_GDP_trn'],end_real_GDP_trn=end['real_GDP_trn'],change_trn=end['real_GDP_trn']-start['real_GDP_trn'],cumulative_change_pct=(end['real_GDP_trn']/start['real_GDP_trn']-1)*100,CAGR_pct=((end['real_GDP_trn']/start['real_GDP_trn'])**(1/(hi-lo))-1)*100,method='ANNUAL_PREVIOUS_CORE_BASE_EXACT_ADDITIVE_SUM_NOT_CAUSAL_SHAPLEY')
  for key in annual[0]:
   if key.startswith('contrib_') or key.startswith('nested_'):z[key]=sum(r.get(key,0.) for r in selected)
  z['contribution_sum_trn']=sum(z[k] for k in z if k.startswith('contrib_'));z['residual_trn']=z['change_trn']-z['contribution_sum_trn'];summary.append(z);check('interval_'+str(lo)+'_'+str(hi),z['residual_trn'])
 dump(out/'SQ_Growth_Contribution_Summary.csv',summary)
 # Independent log-level identity with a different arithmetic order.
 logarithmic=anchor['coreY']*math.exp(sum(math.log(1+p['base_growth']-sum(risks(y).values())) for y in range(2027,2056))+alpha*math.log(rs[-1]['labor']/initialL))
 check('independent_log_level_2055',logarithmic-rs[-1]['coreY'])
 # Validate base growth is present once in the actually executed branch.
 source=(root/N3DIR/'Resolved_Macro_Source.py.txt').read_text();check('single_nonlabor_multiplication',source.count("nonlabor_factor*=1+p['base_growth']-risk")-1,0)
 assert "next_coreY=coreY_anchor*nonlabor_factor*(labor/labor_anchor)**p['labor_response']" in source
 check('SQ_new_policy_tax_zero',max(abs(t['medical']['policy_tax_delta_trn']) for t in rs),0)
 check('SQ_new_policy_cash_zero',max(abs(t['medical']['policy_household_cash_delta_trn']) for t in rs),0)
 check('SQ_supply_not_binding',max(t['unmet'] for t in rs),1e-10)
 # Verify no input/source changes: read back every pinned local object after execution.
 for item in receipts:
  file=root/item['path']
  if file.exists():check('source_unchanged:'+item['path'],0 if hashlib.sha256(file.read_bytes()).hexdigest()==item['sha256'] else 1,0)
 failures=[r for r in checks if not r['pass_']]
 result=dict(status='PASS_NUMERICAL_DIAGNOSIS' if not failures else 'FAIL',independent_model_review=False,checks=len(checks),failed=len(failures),failures=failures,checks_detail=checks,target_commit=N3,request_commit='3f6f3eb47a7b094b3b6a8b4e51554fbb71b0cfc7',Claude_reused_commit=CLAUDE,known_observations_reproduced=True,hypothesis=dict(common_exogenous_positive_growth='SUPPORTED_AS_EXPLICIT_SPECIFICATION',SQ_specific_extra_growth_or_duplicate_base='NOT_SUPPORTED',empirical_adequacy='NOT_IDENTIFIED'),limits=['No nationwide empirical TFP or observed gross investment inferred','Population accounting allocations are algebraic; immigration causal effect not identified','Fixed-input ablations do not rerun endogenous demographics/demand/tax','F fixed not rerun; N3 issues separate; old PASS reused not reissued'])
 (out/'SQ_Growth_Diagnosis_Verification.json').write_text(json.dumps(result,indent=2)+'\n');assert not failures,failures[:4]
 report(root,out,data,annual,summary,counter,result)
 print('DIAGNOSIS_PASS',len(annual),'years',len(checks),'checks')

def report(root,out,data,annual,summary,counter,result):
 p=data['parameters'];start=data['years'][0];end=data['years'][-1];total=summary[-1]
 def fmt(x):return f'{x:+.6f}'
 main=[('基調成長1%',total['contrib_base_growth_trn']),('有効労働',total['contrib_labor_trn']),('2027年紛争',total['contrib_conflict_trn']),('2031年地震',total['contrib_quake_trn']),('3年ごとの災害',total['contrib_disaster_trn']),('隔年気候ショック',total['contrib_climate_trn']),('成長・リスク×労働の交互作用',total['contrib_growth_risk_labor_interaction_trn']),('消費調整',total['contrib_consumption_adjustment_trn']),('共通医療サービスVA',total['contrib_common_service_trn']),('資本供給・追加投資・教育・供給制約の合計',sum(total[k] for k in ['contrib_supply_absorption_trn','contrib_policy_investment_trn','contrib_education_demand_trn','contrib_supply_constraint_trn']))]
 table='|要因|2026→2055寄与（兆円）|\n|---|---:|\n'+''.join(f'|{name}|{fmt(value)}|\n' for name,value in main)+f"|合計|{fmt(total['contribution_sum_trn'])}|\n"
 intervals='|区間|開始GDP|終了GDP|変化（兆円）|年率CAGR|\n|---|---:|---:|---:|---:|\n'+''.join(f"|{r['start_year']}→{r['end_year']}|{r['start_real_GDP_trn']:.6f}|{r['end_real_GDP_trn']:.6f}|{r['change_trn']:+.6f}|{r['CAGR_pct']:+.4f}%|\n" for r in summary)
 cf='|固定入力の診断|2055年GDP換算値|実際との差（兆円）|\n|---|---:|---:|\n'
 labels={'NO_BASE_GROWTH_TERM':'基調成長項を除く','NO_REAL_RISK_TERMS':'実質リスク項を除く','HOLD_EFFECTIVE_LABOR_2026':'有効労働を2026水準に固定','HOLD_FOREIGN_JOBS_2026':'外国人就業を2026水準に固定'}
 for name,label in labels.items():
  r=next(r for r in counter if r['case']==name and r['year']==2055);cf+=f"|{label}|{r['diagnostic_GDP_with_actual_demand_wedge_trn']:.6f}|{r['difference_from_actual_trn']:+.6f}|\n"
 text=f'''# SPE｜SQ成長経路の数値診断

2026-11-22 JST。OWNER-DIRECTED / READ-ONLY DIAGNOSIS / DRAFT / NON-CANONICAL。

## 結論

SQの実質GDPは2026年580.000000兆円から2055年528.962336兆円へ **51.037664兆円（8.7996%）減少**する。主因は、有効労働減少と、回復項を伴わずGDP水準に残る共通リスクショックの反復である。1%基調成長は大きな正寄与だが、これらの減少を補いきれない。通常の追加投資/資本・需要不足・供給上限が主因という説明は、このSQには当てはまらない。

**SQだけに付与された追加成長・1%の二重計上という疑惑は `NOT_SUPPORTED`。** 一方、実証TFPから独立した共通の外生1%による押上げは、仕様として明確に存在する（`SUPPORTED_AS_EXPLICIT_SPECIFICATION`）。この1%やリスク・労働弾性の実証的妥当性/楽観性は本診断では `NOT_IDENTIFIED`。正寄与の存在と不具合を分けて判定した。

## 実際の式と再構成

変更なしのSQ実行の `run_path` をPythonトレースで取得し、毎年の局所変数・実行パラメータ・人口就業軌道を保存した。政策・係数・エンジン原本に変更なし。対象は `SQ_COMMON_ON` だけで、F/N3をSQの代理にしていない。

実行経路は `_link='LEVEL'`、基調成長 `g=0.01`、労働弾性 `a=0.65`。

```text
A_t = A_(t-1) × (1 + g − risk_t), A_2026 = 1
Ycore_t = 580 × A_t × (L_t / L_2026)^0.65
Y_t = Ycore_t + 0.5×supply_t + C_t + I_t
      + education_t + common_service_t − unmet_t
```

2055年は `580 × 1.049593758673 × 0.868911644203 = 528.962458384658` 兆円。共通医療等の需要差は `−0.000122051477` 兆円で、実際の528.962336333181に一致する。初期580は設計アンカーであり、2026年のオイルショックは `apply_oil_to_initial=False` で追加適用されない。F/N3も同じ初期実質GDPであり、SQ限定バフとは確認できない。

ソース中では先に `growth = g + 0.65×労働前年比 − risk` が計算されるが、LEVEL分岐で `growth = next_coreY/coreY − 1` に**置換**される。両方を加算しているわけではない。名目基礎GDPは別途 `coreN_(t-1)×(1+growth+inflation)`、実際の名目GDPは `Y×coreD×(1+pressure)`。前者の前年値へ実際の名目GDPを代入すると、微小な需要差まで混ぜた再構成誤差になるため区別した。

{intervals}

## 加法的な縮小要因

各年の前年基礎GDPを `B`、`q=(L_t/L_(t-1))^0.65` とすると、

```text
ΔYcore = B×g − B×risk + B×(q−1) + B×(g−risk)×(q−1)
```

に厳密に分解できる。これを29遷移で合計し、需要差の前年差を加えた結果が次表。リスクは2027紛争5%、2031地震3%、2029〜2053の3年ごと災害1%（9回）、2028〜2054の隔年気候0.5%（14回）。単なる一時的な成長率の下押しとして翌年元水準へ戻すコードではなく、積で水準損失が残る。

{table}
残差は `{total['residual_trn']:.3e}` 兆円。全期間の災害等合計は−131.856581兆円。2026→2035の減少約40.828兆円が全期間の大部分を占め、紛争・地震と早期反復リスクが効いている。これらはモデル式に基づく会計的寄与であり、現実経済の実証的因果推定ではない。

## 人口・就業・外国人材の内訳

人口は122.618024百万人→104.653182百万人、有効労働は67.965671百万人→54.752750百万人。実行人口は最新固定人口基盤の値で、旧政策§9の121.5百万人を推測代入していない。

労働寄与−75.267623兆円を `L = 人口 × 一人当たり有効就業` としてさらに分解すると、人口要因−55.241079、就業率/年齢等構成−20.100188、両者交互作用＋0.073644兆円。これは主表の労働寄与の**内訳**であり、別途加算しない。就業率と年齢構成それぞれの純粋な効果は未識別で、同じ列にまとめる。

人口恒等式の出生・死亡・純移民・参照接続残差を人口寄与へ比例配分した内訳は、出生＋61.664867、死亡−143.674269、純移民＋26.981982、参照接続−0.213659兆円。これは固定人口軌道に対する数学的配分で、出生政策や移民政策の因果効果ではない。

別の切り方では、日本人側就業65.168696→46.133637百万人、外国人就業2.796974→8.619113百万人。有効労働の変化へ比例配分すると、国内就業−108.280913、外国人就業＋33.013290兆円。SQでも既存の外国人ストック・純流入があるため縮小を緩和している。ただし外国人就業の増加には人口・年齢・就業率仮定も含み、全額を移民政策効果と呼べない。人口内訳とこの就業内訳を重ねて足してはならない。

## 資本・需要・物価・税収

SQの追加政策投資と追加資本は丸め誤差程度（2055年 `I≈−2.12e−17`、`K≈−3.08e−16` 兆円）。基礎資本は `3×Ycore` としてGDPから作られ、1740→1586.887375兆円へ減る。これはGDP縮小の**結果として構成された資本proxy**で、独立に観測した資本不足によるGDP低下の証拠ではない。減耗5%に対して置換投資は `Kcore_t−0.95×Kcore_(t−1)` と逆算される。2055年87.418698兆円を実測投資や政策追加投資と扱わない。

供給上限は `Ycore + supply + 2%×Ycore`、全30年で未充足需要は0。供給制約によるGDP損失は0。消費調整−0.003893兆円と共通医療サービス＋0.003771兆円がほぼ相殺する。消費proxyの大半は `0.6×Ycore + C` というGDP連動成分であり、消費proxyの水準低下を丸ごと独立した需要ショックとして二重に数えない。

実質GDPが減る一方、共通デフレータは1.034483→1.934599（倍率1.870112）、名目GDPは600→1023.329981兆円。税収は名目増加率×弾性1.5で動き、2031年だけ0.9倍、名目GDPの30%上限を持つ。マクロ税proxy80→159.721457兆円の変化は、年次名目feedback＋88.802391、地震税調整−9.080934、上限調整0で再構成できる。直接税差分等を含む診断税proxyは159.759058兆円。税の増加を実質GDPの成長バフと取り違えない。このSQの税・財政から実質GDPへの追加利払/債務feedbackはなく、地震の税収10%減をGDPからもう一度減算しない。

## 固定入力の反実仮想と仮説判定

元の係数は変更せず、診断コード内の数式で対象項を除いた固定入力の計算。人口・労働・実際の需要差は保持し、完全な内生反実仮想ではない。

{cf}

外生1%を除くと2055年換算値は395.412613兆円まで下がる。実際との差133.549723兆円は、主表の年次寄与＋156.303873とは定義が違い、加算しない。リスク項除去・外国人就業固定等も相互作用を持ち、各差を足して合計政策効果にしない。

確認できた原因は、有効労働の減少、恒久的水準効果を残すリスク反復、共通外生1%の正寄与。SQ限定の余分な成長項、外生1%の二重加算、人口と移民就業のGDP再加算は、取得したSQ実行経路では認められない。実証較正を伴わない1%の妥当性、反復災害の長期回復、資本基礎をGDP比から作る設計の適切さは別の未較正論点。今回は修正していない。

## F/N3との切分け

2055年F固定参照540.274554、N3国内移転候補481.330871、SQ528.962336兆円。F−SQは＋11.312218、N3−SQは−47.631465兆円だが、接続範囲・候補入力が異なり政策因果順位ではない。Fは固定参照のまま再実行していない。

N3の2035年政策税差分＋85.784兆円、2055年家計現金−153.778兆円はN3固有の部品勘定。SQでは新規政策税・家計現金差分は全30年0であり、SQ縮小の原因に転用しない。N3では低MPC候補の2055年GDP495.655504、高MPC候補469.410124となる。負の家計現金ショックに高いMPCをかければ需要損失が拡大するため、その逆符号をSQ成長バグの証拠にしない。旧N3由来の負の投資残余（Claude検算で2045年約−1.871兆円）も別論点で、SQ追加投資はほぼ0。N3の水準・負担の妥当性診断は今回行っていない。

## 検証・出典・引渡し

変更なしSQ30年を実行し、既存固定出力と年次水準を照合。年次加法分解・人口/就業恒等式・資本恒等式・名目/税再構成・異なる演算順序の対数水準式・ソース非変更を `{result['checks']}` 件確認し、失敗0。既存SQ出力に対するGDP再構成最大誤差は `{max(abs(r['reconstruction_error_trn']) for r in annual):.3e}` 兆円（CSV丸めを含む）。独立した別AIレビューを追加したものではない。

N3原本 `37c3399f9c553673a79ba1298fc68d758a77055e`、Claude限定独立検算 `ba08c45d4ecb99defecb8416c8d63e0cbfde8cb4` の原本を取得し、旧再現性・旧79回帰PASSを保持した。Claudeの164/164 PASS_WITH_LIMITATIONSを今回の新分解の独立PASSとして流用していない。

主要出典：N3原本の `Resolved_Macro_Source.py.txt` の `run_path`（LEVEL分岐、需要・資本・税）、`f-foreign-quantity-20261120/Model.py:macro`（LEVEL指定）、`SQ_Unchanged_Engine_Trace.json` のparameters/years/demography、固定 `results/Annual_DOMESTIC_TRANSFER.csv` のSQ_COMMON_ON。対応列・式は `SQ_Column_Formula_Map.csv`、参照版と実バイトSHA-256は `Source_Receipts.json`、本成果のサイズ・SHA-256は `SQ_Growth_Diagnosis_Verification.json` に記録。

再現は標準ライブラリ＋git。SPEの固定資料を持つチェックアウトで次を実行する。元エンジンを改変せず、SQだけの実行フィルタを付けて隔離出力へ再計算する。

```bash
python handoff/chatgpt-sq-growth-diagnosis-20261122/SQ_Growth_Diagnosis_Reproduce.py --outdir /workspace/scratch/sq-diagnosis-reproduction
```

書込みは指定新規診断ディレクトリに限定。PR/merge、政策・モデル係数・共通エンジン・既存出力、Acceptance/DecisionLog/Freeze/Canonical、RP-023/M19–25 HOLD、RP-024 PENDINGの変更なし。必要な検討候補は外生1%・反復リスクの回復・基礎資本proxyの意味の較正確認にとどめ、変更実装はしていない。
'''
 (out/'SPE_SQ_Growth_Path_Diagnosis_Report_DRAFT_20261122.md').write_text(text)
 mapping=[
 ('real_GDP_trn','SQ macro_row.real_gdp_trn / fixed real_gdp_trn','Ycore + demand wedge, subject to supply ceiling','TRN_REAL'),
 ('population','trace.demography.population','births-deaths+netmigration+referencebridge recurrence','PERSONS'),
 ('effective_labor','trace.labor / fixed macro_labor_force_population_proxy','SQ domestic_employed + foreign_employed, verified','EFFECTIVE_PERSONS_PROXY'),
 ('core_real_GDP_trn','trace.coreY','580*product(1+g-risk)*(L/L0)^0.65','TRN_REAL'),
 ('nonlabor_factor','trace.nonlabor_factor','product(1+base_growth-risk), once in LEVEL branch','DIMENSIONLESS'),
 ('contrib_*','annual mathematical decomposition','previous_core*g/risk/labor/cross + delta demand wedge','TRN_ADDITIVE'),
 ('nested_*','nested labor/population decomposition','alternatives/internal splits, NOT additional contributions','TRN_NESTED_DO_NOT_DOUBLE_ADD'),
 ('baseline_capital_real_trn','3*trace.coreY','capital is constructed from GDP; not observed input','TRN_REAL_PROXY'),
 ('replacement_investment_real_trn','trace.replacement','coreK_t-0.95*coreK_previous','TRN_IMPUTED_NOT_OBSERVED'),
 ('policy_investment_real_trn','trace.I','0.4*Iprev+0.6*invest_nom/coreD','TRN_REAL_ADDITIONAL'),
 ('supply_gain_real_trn','trace.supply','0.1*0.95*Kprev + education yield term','TRN_REAL_ADDITIONAL'),
 ('household_consumption_real_proxy_trn','macro_row.household_consumption_real_proxy_trn','0.6*Ycore+C','TRN_REAL_PROXY'),
 ('macro_tax_trn','trace.tax','min(prevTax*(1+nominalGrowth*1.5)*quakefactor,0.3*N)','TRN_NOMINAL_PROXY'),
 ('observed_TFP','ABSENT','NOT_IDENTIFIED: base_growth not measured TFP','NULL'),
 ('identified_causal_immigration_effect','ABSENT','NOT_IDENTIFIED: fixed paths/stock algebra only','NULL')]
 dump(out/'SQ_Column_Formula_Map.csv',[dict(column=a,source=b,formula=c,unit_or_status=d) for a,b,c,d in mapping])
 # Verification record excludes itself and mutable execution logs.
 names=['SQ_Growth_Diagnosis_Reproduce.py','SPE_SQ_Growth_Path_Diagnosis_Report_DRAFT_20261122.md','SQ_Annual_Growth_Decomposition_2026_2055.csv','SQ_Growth_Contribution_Summary.csv','SQ_Fixed_Input_Ablations.csv','SQ_Demography_Labor_Accounting.csv','SQ_F_N3_Diagnostic_Comparison.csv','SQ_Column_Formula_Map.csv','SQ_Unchanged_Engine_Trace.json','SQ_Isolated_Execution_Input.json','Reused_Claude_Summary.json','Source_Receipts.json']
 result['artifacts']=[dict(path=name,size=(out/name).stat().st_size,sha256=hashlib.sha256((out/name).read_bytes()).hexdigest()) for name in names if (out/name).exists()]
 (out/'SQ_Growth_Diagnosis_Verification.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--outdir',type=Path,required=True);a.add_argument('--draft',type=Path);z=a.parse_args();run(z.root.resolve(),z.outdir.resolve(),(z.draft or z.outdir/'fixed-draft-source').resolve())
