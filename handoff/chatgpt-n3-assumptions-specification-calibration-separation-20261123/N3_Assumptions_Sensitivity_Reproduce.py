#!/usr/bin/env python3
"""Execute one-factor unadopted N3 sensitivities, preserve fixed SQ and tax rates."""
import argparse,csv,hashlib,importlib.util,json,os,subprocess,sys,types
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
PIN='e8bea03671225189c6af5ccc7a4ec5cbb27817f0';REQ='89371098c127e5ff7b44e10fa4d891bec73b2ebe'
PREV='handoff/chatgpt-n3-native-policy-completion-20261123'
SEP='handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123'
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
METRICS=['real_GDP_trn','nominal_GDP_trn','GDP_minus_SQ_trn','total_tax_diagnostic_proxy_trn','household_resource_DI_proxy_trn','household_policy_cash_nominal_trn','consumption_real_trn','private_investment_real_trn','extra_private_investment_real_trn','CL_PB_candidate_trn','CL_interest_candidate_trn','CL_debt_candidate_trn','CL_assets_candidate_trn','CL_new_borrowing_trn','CL_gross_issue_assumed_trn','N3_firm_cash_trn','pension_fund_end_trn','pension_contribution_trn','pension_benefit_delta_trn','existing_public_payroll_delta_trn','existing_in_kind_trn','existing_premium_relief_trn']
def run(root,out):
 out.mkdir(parents=True,exist_ok=True);R=module('isolated_runtime',HERE/'Sensitivity_Runtime.py');V=module('inventory',HERE/'Assumptions_Inventory.py')
 inp=json.loads((HERE/'Sensitivity_Inputs.json').read_text());prior=rd(root/PREV/'N3_Native_Completion_Annual_Comparison_2026_2055.csv')
 fixed={int(x['year']):x for x in prior if x['case']=='N3_NATIVE_COMPLETED_SUPPORTED'};conditional={int(x['year']):x for x in prior if x['case']=='N3_NATIVE_CONDITIONAL_OPTION'}
 raw=[];ledger=[];policy=[];pensions=[];medical=[];case_defs=[];contracts=[];traces=[];counter=0;failures=[];baseline=None;receipts=[];paths=set()
 for definition in inp['cases']:
  cid=definition['case'];r,s=R.build(root,out,definition);a,l,b=r.simulate(s)
  rck=r.ck
  hh={y:[x for x in r.live_component.households if x['year']==y] for y in range(2026,2056)}
  for i,(x,lx,p,pen,med) in enumerate(zip(a,l,r.live_component.rows,r.live_component.pension,r.medical_accounts)):
   y=x['year'];pre=cid+str(y);h=hh[y];cfg=r.live_component.cfg;ps=cfg.get('pension_public_share',.5)
   rck(pre+':GI_OFF',x['government_purchase_nominal_trn']+x['public_investment_nominal_trn'])
   rck(pre+':no_net_new_jobs',p['public_added_jobs'])
   # Reconstruct policy household/government/insurer sources independently
   # from emitted cell and fund records, not merely the aggregate's own residual.
   rck(pre+':in_kind_cells',p['in_kind_trn']-sum(z['in_kind_trn'] for z in h))
   rck(pre+':premium_cells',p['premium_relief_trn']-sum(z['premium_saved_trn'] for z in h))
   rck(pre+':policy_G_cost_once',p['policy_government_cost_delta_trn']-(p['in_kind_trn']-p['EITC_removal_trn']+ps*pen['public_cash_cost_delta_trn']+p['public_payroll_delta_trn']))
   rck(pre+':insurer_counterpart',p['policy_insurer_cash_delta_trn']+p['premium_relief_trn']+(1-ps)*pen['public_cash_cost_delta_trn'])
   reserve=r.live_component.semi_rows[i]['household_extra_premium_trn'] if r.live_component.semi_rows else 0.
   cash=sum(z['cash_delta_trn'] for z in h)+.8*p['dividend_delta_trn']+pen['household_pension_cash_delta_trn']-pen['domestic_property_income_debit_trn']+p['public_payroll_delta_trn']-p['wealth_tax_delta_trn']-reserve
   rck(pre+':HH_sources_once',p['policy_household_cash_delta_trn']-cash)
   rck(pre+':fund_stock',pen['fund_end_trn']-pen['fund_begin_trn']-pen['fund_return_trn']-pen['fund_contribution_trn']+pen['fund_payout_trn'])
   rck(pre+':domestic_fund_return',pen['fund_return_trn']-pen['domestic_property_income_debit_trn'])
   rck(pre+':public_insurer_partition',pen['government_cash_cost_delta_trn']-pen['public_insurer_cash_delta_trn']-pen['public_cash_cost_delta_trn'])
   rck(pre+':fund_no_second_contribution',pen['second_contribution_charge_trn'])
   rck(pre+':rates_unchanged',abs(x['policy_labor_rate']-.3)+abs(x['policy_financial_rate']-.2)+abs(x['policy_estate_rate']-.4)+abs(x['VAT_standard_rate']-float(fixed[y]['VAT_standard_rate'])))
   rck(pre+':cash_identity_independent',lx['PB_trn']-lx['interest_trn']-lx['SFA_cash_need_trn']+lx['new_cash_borrowing_trn']-lx['cash_debt_redemption_trn']-lx['assets_end_trn']+lx['assets_begin_trn'])
   rck(pre+':fund_return_formula',pen['fund_return_trn']-pen['fund_begin_trn']*cfg['fund_return'])
   if cid=='BASE_REPLAY':
    for k in METRICS:rck('fixed_replay:'+str(y)+k,x[k]-float(fixed[y][k]),3e-6)
   if cid=='EMP_RAMP3':
    for k in ['real_GDP_trn','CL_PB_candidate_trn','CL_debt_candidate_trn','existing_public_payroll_delta_trn']:rck('prior_conditional_ramp3:'+str(y)+k,x[k]-float(conditional[y][k]),3e-6)
   if cid in ['GI_INACTIVE_CONTROL','ROLLOVER020']:
    for k in METRICS:
     if k=='CL_gross_issue_assumed_trn' and cid=='ROLLOVER020':continue
     rck('expected_neutral:'+pre+k,x[k]-baseline[i][k],3e-6)
   x.update(case=cid,source_status='MECHANICAL_SENSITIVITY_UNADOPTED',population_persons=r.base[y]['demography']['population'],
    common_deflator=r.base[y]['coreD'],core_real_GDP_trn=r.base[y]['coreY'],additional_G_trn=0.,additional_public_I_trn=0.,
    actual_usable_cash_trn='unknown',GG_PB='unknown',GG_debt='unknown',actual_bond_issue='unknown',
    VAT_base_dynamics_actual='LAGGED_NOMINAL_GDP',medical_base_dynamics_actual='LAGGED_PRICE_FACTOR')
   policy.append(dict(case=cid,**p));pensions.append(dict(case=cid,**pen,effective_return_counterparty='DOMESTIC_HH_PROPERTY_INCOME_TRANSFER'));medical.append(med)
   traces.append(dict(case=cid,year=y,firm_rate_actual=s['firm_rate'],job_target_actual=cfg['public_job_target'],
    wage_gap_reference_yen=cfg['public_new_wage_yen']-cfg['public_old_wage_yen'],employment_ramp_actual=cfg.get('employment_ramp',6),
    in_kind_reference_yen=cfg['in_kind_yen'],in_kind_HH_substitution_actual=cfg.get('in_kind_substitution',.7),in_kind_service_complement=1-cfg.get('in_kind_substitution',.7),
    pension_government_share_actual=ps,pension_insurer_share_actual=1-ps,pension_return_actual=cfg['fund_return'],
    medical_clinical_public_share_actual=r.native_medical.s['clinical_public_fraction'],medical_clinical_insurer_share_actual=1-r.native_medical.s['clinical_public_fraction'],
    backfill_enabled=s['backfill'],GI_mode=s['GI_mode'],actual_G=x['government_purchase_nominal_trn'],actual_public_I=x['public_investment_nominal_trn'],
    common_population_persons=x['population_persons'],core_real_GDP_trn=x['core_real_GDP_trn'],kpi_enabled_in_component=r.live_md.s['kpi'],
    macro_parameters_sha256=hashlib.sha256(json.dumps(r.par,sort_keys=True).encode()).hexdigest()))
  if cid=='BASE_REPLAY':
   baseline=copy_rows=[dict(z) for z in a]
   params,coverage,priorities=V.inventories(root,r,s,rd(root/PREV/'N3_22_Policy_Coverage_Before_After.csv'))
   (out/'Resolved_Isolated_Component_Source.py.txt').write_text(r.resolved_component)
  if cid=='ROLLOVER020':
   rck('rollover_changes_gross_issue',0. if max(abs(x['CL_gross_issue_assumed_trn']-baseline[i]['CL_gross_issue_assumed_trn']) for i,x in enumerate(a))>1e-6 else 1.)
  counter+=r.counter;failures+=r.checks;raw+=a;ledger+=l
  contracts.append(dict(case=cid,runtime=s,component_config_scalars={k:v for k,v in r.live_component.cfg.items() if isinstance(v,(int,float,str)) or v is None},
   component_spec=r.live_md.s,medical_spec=r.native_medical.s,original_common_macro_parameters_sha256=hashlib.sha256(json.dumps(r.par,sort_keys=True).encode()).hexdigest()))
  case_defs.append(dict(case=cid,group=definition['group'],change=definition['change'],config=json.dumps(definition.get('config',{}),sort_keys=True),runtime=json.dumps(definition.get('runtime',{}),sort_keys=True),medical_spec=json.dumps(definition.get('medical_spec',{}),sort_keys=True),adoption_status='MECHANICAL_TEST_UNADOPTED',GI_mode='OFF',original_rates_unchanged=True))
  # Trace the actual module graph; reused predecessor receipt covers its original
  # acquisition. Recheck current runtime/input bytes only, not every project file.
  seen=set()
  def walk(obj,depth=0):
   if id(obj) in seen or depth>5:return
   seen.add(id(obj));p=getattr(obj,'__file__',None)
   if p:
    try:paths.add(str(Path(p).resolve().relative_to(root)))
    except ValueError:pass
   if isinstance(obj,types.ModuleType):
    for v in vars(obj).values():
     if isinstance(v,types.ModuleType) and getattr(v,'__file__',None) and str(root) in str(v.__file__):walk(v,depth+1)
  for obj in [r.cm,r.fp,r.old,r.FM,r.V]:walk(obj)
  print(json.dumps(dict(case=cid,checks=r.counter,failed=len(r.checks),GDPgap2030=a[4]['GDP_minus_SQ_trn'],GDPgap2055=a[-1]['GDP_minus_SQ_trn'])))
 # Common external paths and comparison coefficients are identical by year.
 baseline_trace={x['year']:x for x in traces if x['case']=='BASE_REPLAY'}
 for t in traces:
  for k in ['common_population_persons','core_real_GDP_trn','macro_parameters_sha256']:
   counter+=1
   if t[k]!=baseline_trace[t['year']][k]:failures.append(dict(check='shared_exogenous:'+t['case']+str(t['year'])+k))
 # Standard comparison output includes fixed reused reference branches without
 # running prior GI diagnostics or relabelling them as native policy.
 results=[];summaries=[];effects=[];bi={x['year']:x for x in baseline}
 for x in raw:
  y=x['year'];z=dict(case=x['case'],year=y,source_status=x['source_status'])
  for k in METRICS:z[k]=x[k];z['delta_vs_base_'+k]=x[k]-bi[y][k]
  for k in ['population_persons','common_deflator','core_real_GDP_trn','additional_G_trn','additional_public_I_trn','actual_usable_cash_trn','GG_PB','GG_debt','actual_bond_issue']:z[k]=x[k]
  results.append(z)
 for cid in [z['case'] for z in inp['cases']]:
  a=[x for x in raw if x['case']==cid];below=sum(x['GDP_minus_SQ_trn']<-1e-7 for x in a)
  for year in [2030,2035,2039,2055]:
   x=next(x for x in a if x['year']==year);summaries.append(dict(case=cid,year=year,SQ_below_years=below,**{k:x[k] for k in METRICS},**{'delta_vs_base_'+k:x[k]-bi[year][k] for k in METRICS}))
  group=next(d['group'] for d in inp['cases'] if d['case']==cid)
  effects.append(dict(case=cid,group=group,SQ_below_years=below,
   maximum_abs_GDP_difference_trn=max(abs(x['real_GDP_trn']-bi[x['year']]['real_GDP_trn']) for x in a),
   maximum_abs_debt_difference_trn=max(abs(x['CL_debt_candidate_trn']-bi[x['year']]['CL_debt_candidate_trn']) for x in a),
   maximum_abs_cash_difference_trn=max(abs(x['CL_assets_candidate_trn']-bi[x['year']]['CL_assets_candidate_trn']) for x in a),
   maximum_abs_gross_issue_difference_trn=max(abs(x['CL_gross_issue_assumed_trn']-bi[x['year']]['CL_gross_issue_assumed_trn']) for x in a),
   maximum_abs_PB_difference_trn=max(abs(x['CL_PB_candidate_trn']-bi[x['year']]['CL_PB_candidate_trn']) for x in a),
   GDP_difference2030_trn=a[4]['real_GDP_trn']-bi[2030]['real_GDP_trn'],GDP_difference2055_trn=a[-1]['real_GDP_trn']-bi[2055]['real_GDP_trn'],
   cash_difference2055_trn=a[-1]['CL_assets_candidate_trn']-bi[2055]['CL_assets_candidate_trn'],debt_difference2055_trn=a[-1]['CL_debt_candidate_trn']-bi[2055]['CL_debt_candidate_trn'],
   effect_class='INACTIVE_GI_BUNDLE' if cid=='GI_INACTIVE_CONTROL' else 'GROSS_FLOW_ONLY_NET_NEUTRAL' if cid=='ROLLOVER020' else 'BASELINE_REPRODUCTION' if cid=='BASE_REPLAY' else 'ACTIVE_MECHANICAL_ASSUMPTION_SENSITIVITY',
   calibration_or_policy_gap_resolved=False))
 for e in effects:
  if e['effect_class']=='ACTIVE_MECHANICAL_ASSUMPTION_SENSITIVITY' and e['maximum_abs_GDP_difference_trn']<1e-9:
   e['effect_class']='ACTIVE_FISCAL_ONLY_NO_GDP_FEEDBACK_IN_GI_OFF_MODEL' if max(e['maximum_abs_PB_difference_trn'],e['maximum_abs_cash_difference_trn'],e['maximum_abs_debt_difference_trn'])>1e-9 else 'ACTIVE_ACCOUNT_RECLASSIFICATION_OR_CANCELLATION'
 groups={}
 for e in effects:groups[e['group']]=max(groups.get(e['group'],0.),e['maximum_abs_GDP_difference_trn'])
 policy_groups={'A_CORPORATE':['FIRM'],'C_EMPLOYMENT':['JOBS','WAGE_GAP','EMP_RAMP'],'S_PHASE1':['EMP_RAMP'],'B_IN_KIND':['INKIND_AMOUNT','INKIND_SUBSTITUTION'],'B_RELIEF':['RELIEF','INSURER_BACKFILL'],'B_MEDICAL':['MEDICAL_PAYER','INSURER_BACKFILL'],'B_PENSION':['PENSION_PAYER','PENSION_RETURN','INSURER_BACKFILL']}
 for z in priorities:
  gs=policy_groups.get(z['policy_id'],[]);z.update(tested_sensitivity_groups=';'.join(gs),maximum_abs_GDP_difference_tested_trn=max([groups[g] for g in gs] or [0.]),
   maximum_abs_cash_difference_tested_trn=max([e['maximum_abs_cash_difference_trn'] for e in effects if e['group'] in gs] or [0.]),
   maximum_abs_PB_difference_tested_trn=max([e['maximum_abs_PB_difference_trn'] for e in effects if e['group'] in gs] or [0.]),
   untested_not_zero_effect=not bool(gs),execution_priority='P1' if z['existing_data_code_can_advance'] else 'P2_DATA_OR_SPEC_REQUIRED',
   concrete_existing_data_action=('expose firm funding and macro investment diagnostics separately; do not equate20% eligibility with75% response' if z['policy_id']=='A_CORPORATE' else
   'parameterize wage/start/ramp as independent optional diagnostics; preserve REGULARIZE and identify ADD_JOBS scope before any labor claim' if z['policy_id'] in ['C_EMPLOYMENT','S_PHASE1'] else
   'map government/insurer premium and fund accounts with explicit sector boundary and unassigned residual' if z['policy_id'] in ['B_MEDICAL','B_PENSION','B_RELIEF'] else
   'make substitution and service complement explicit in optional runtime and keep final-purchaser/SNA G status unknown' if z['policy_id']=='B_IN_KIND' else z['next_executable_improvement']))
 # Priority order never treats untested policy channels as low estimated effect.
 priorities.sort(key=lambda z:(z['execution_priority'],-max(z['maximum_abs_GDP_difference_tested_trn'],z['maximum_abs_PB_difference_tested_trn']),z['policy_id']))
 for i,z in enumerate(priorities,1):z['execution_order']=i
 write(out/'Resolved_Case_Contracts.json',contracts)
 dump(out/'N3_Sensitivity_Case_Definitions.csv',case_defs);dump(out/'N3_Sensitivity_Annual_Comparison_2026_2055.csv',results)
 dump(out/'N3_Sensitivity_Case_Summary.csv',summaries);dump(out/'N3_Sensitivity_Impact_Ranking.csv',sorted(effects,key=lambda z:-z['maximum_abs_GDP_difference_trn']))
 dump(out/'N3_Active_Parameter_Provenance_And_Usage.csv',params);dump(out/'N3_22_Policy_Assumptions_And_Gaps.csv',coverage);dump(out/'N3_Gap_Resolution_And_Execution_Priority.csv',priorities)
 dump(out/'N3_Actual_Runtime_Input_Trace.csv',traces);dump(out/'N3_Sensitivity_Fiscal_Cash_Debt_Ledger.csv',ledger)
 dump(out/'N3_Sensitivity_Policy_Accounts.csv',policy);dump(out/'N3_Sensitivity_Pension_Accounts.csv',pensions);dump(out/'N3_Sensitivity_Medical_Accounts.csv',medical)
 reused=[x for x in prior if x['case'] in ['N3_NATIVE_COMPLETED_SUPPORTED','N3_NATIVE_CONDITIONAL_OPTION','N3_PLUS_GI_DIAGNOSTIC','SQ_REFERENCE']]
 dump(out/'Reused_Fixed_Annual_References.csv',reused)
 # Verify the fixed predecessor originals and actual runtime inputs; retain
 # predecessor receipt as evidence of older complete acquisition, no re-audit claim.
 paths.update(str(p.relative_to(root)) for p in (root/PREV).iterdir() if p.is_file())
 paths.update([V.CI,V.MI,V.BASE,V.GAP,V.PAR,V.ROB,V.TR,V.SF,V.SIM,
  'policies/New3linesPolicies.md','handoff/chatgpt-n3-policy-burden-diagnosis-20261122/N3_Unchanged_Execution_Trace.json',
  'handoff/chatgpt-n3-policy-burden-diagnosis-20261122/N3_Conditional_Fiscal_Primary_Bridge.csv',
  'handoff/chatgpt-n3-f-parity-implementation-20261122/results/DOMESTIC_TRANSFER_Corporate_Funding_Stock.csv',
  'handoff/chatgpt-n3-f-parity-implementation-20261122/results/Conditional_National_Local_Fiscal.csv',
  'handoff/chatgpt-national-fiscal-closure-20261121/Official_Fiscal_Baseline_2025_2040.csv',
  'handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Inputs.json','handoff/f-vat-core-20261120/Inputs.json',
  'handoff/chatgpt-n3-gdp-recirculation-counterfactual-20261122/N3_GDP_Recirculation_Annual_Comparison_2026_2055.csv'])
 paths={p for p in paths if not p.endswith('.pyc')}
 for path in sorted(paths):
  b=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);assert b==(root/path).read_bytes(),path
  receipts.append(dict(commit=PIN,path=path,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True,retrieval='git fetch fixed commit / git show'))
 request='handoff/chatgpt-n3-assumptions-specification-calibration-separation-request-20261123/SPE_Work_N3_Assumptions_Specification_Calibration_Separation_Request_20261123.md'
 b=subprocess.check_output(['git','show',REQ+':'+request],cwd=root);assert b==(root/request).read_bytes()
 receipts.append(dict(commit=REQ,path=request,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True,retrieval='connected GitHub fetch_file; local git fetch/show fixed request'))
 write(out/'Input_Source_Receipts.json',receipts)
 # No tracked source modifications are allowed in this worktree.
 assert not subprocess.check_output(['git','diff','--name-only',REQ],cwd=root,text=True).strip()
 assert len(coverage)==22 and len(raw)==len(inp['cases'])*30
 verification=dict(status='PASS_ISOLATED_MECHANICAL_SENSITIVITIES' if not failures else 'FAIL',executed_cases=len(inp['cases']),sensitivity_cases=len(inp['cases'])-1,
  executed_annual_rows=len(raw),checks=counter,failed=len(failures),failures=failures,reused_prior_checks=[1754,5990],reused_fixed_reference_rows=len(reused),
  parameter_inventory_rows=len(params),policy_coverage_rows=len(coverage),source_files_rechecked=len(receipts),
  policy_text_tax_rates_deductions_or_common_engine_modified=False,additional_GI_in_sensitivity=False,policy_adopted=False,national_calibration_completed=False,
  note='individual scenario sensitivities, no probability weights or confidence intervals; negatives controls not independent policy effects')
 write(out/'Verification.json',verification)
 report(out,verification,effects,summaries,priorities,params)
 print(json.dumps(verification));assert not failures,failures[:8]
def report(out,v,effects,summaries,priorities,params):
 lines=['# N3未採用仮定・政策仕様・モデル較正不足の分離と感度実行','DRAFT / NON-CANONICAL / MECHANICAL SENSITIVITY / UNADOPTED / 2026-11-23',
 '## 実行結果と達成範囲',f"基準再現1経路＋未採用感度{v['sensitivity_cases']}経路、計{v['executed_annual_rows']}年次を実行。既存固定比較{v['reused_fixed_reference_rows']}年次を再利用。新規チェック{v['checks']}件、失敗{v['failed']}。22項目は政策仕様・統計・較正・会計・制度権限を独立列で分類し、実パラメータ{v['parameter_inventory_rows']}行をコード位置・有効性・単位・年度・出力へ追跡した。従来1754/5990チェックは再利用であり全件再監査ではない。",
 '今回の改善は、既存コードで定数だった給与移行・現物配分・年金負担を隔離ランタイム内で明示的に変更できるようにし、実際の年次影響と関連部門の対応を計算・比較したこと。仕様不足や較正不足を解決済みとはしていない。',
 '## 主要発見',
 '企業75%：実装は正の当期企業残余フロー（法人税節減−追加配当−既存投資実払）に75%を掛け、平滑化と企業資金残高制約の下で追加民間投資を決定する。内部留保残高全体の75%ではなく、原文の設備投資20%以上という優遇資格判定でもない。追加G/I OFFでも作動。原文60%配当・20%投資AND・16%税率と、仮定の利益GDP比10%、配当応答40%、初期投資応答30%、残余75%を分離した。',
 '雇用：REGULARIZEは既存職員の給与差額を家計と政府へ一度ずつ接続し、純増雇用は0。10万人・給与300/400万円・2030開始6年ランプは原文非確定。3年枝は前回条件付き結果を再現し、9年枝も機械試験。人数と賃金差額は積で作用するため、このモデルでは人数50%変更と給与差額50%変更の効果が対応する。原文の雇用枠拡大を新規雇用数の実装完了と読み替えない。',
 '現物給付：基準は適格家計あたり3万円×物価×移行率、0.7を家計支出代替、残り0.3×VA比0.216をサービスへ。支出代替率を変える際はサービス残分も連動し、独立効果と呼ばない。金額変更は政府費用・家計・サービスへ既存経路で接続する。全額を新規Gへ再加算しない。',
 '保険者・年金：年金公的費用の政府/保険者50/50は国/地方50/50ではない。政府比率25/75%感度は補完比率も動く。医療clinical_public_fraction0.5は保険給付の政府/保険者配分で、原文の患者自己負担50%とは別物。医療負担変更では保険料・財源・準備金分類も連動する。backfill=Falseは負の保険者収支の政府補填を外す比較仮定であり、全国財源閉合の達成ではない。True感度は負の保険者勘定全体を対象とする複合的な帰属試験。',
 '年金運用：利回り2%は基金期首資産へ適用。国内振替枝では同額を家計財産所得から控除し、追加GDPや第二の拠出として加算しない。1/3%感度でも対応を保持。75歳原則は原文だが、既存受給者保護・粗いコホート・拠出代理率・20年払出は較正/仕様不足を残す。',
 '不活性：GI OFFではg_share0.5、pi_share0.25、runtime.domestic0.8、yield_public0.1、lag1は追加G/Iの経済効果を生まない。要求予算やメタデータに値が現れても実執行ではない。macro par.domestic_share0.8は別変数で家計需要へ実際に作動しており、不活性と扱わない。cash_basis=CASH_ONLYは旧ラベルで、現行資金計算はcash_part/現金予算overrideに従う。GI不活性バンドルで主要経済・財政系列ゼロ差を確認。',
 '財政：rate0.02は中央銀行政策金利ではなく、旧公式純利払＋超過債務/現金資産の利息仮定。現金資産から利息を差し引くため後年の純利払が負になる候補もある。rollover0.1は仮定借換総額を動かすが純債務やGDPを動かさない。2041以降のHOLD、SFA ZERO、社会保障追加成長0は外挿仮定であり、現実の将来支出やSFA現金需要が0と判明したものではない。',
 '2035年KPI：FIXEDが既存成長0%候補を無効化。原文の所得定義・目標・窓、ジニ基準/観測/補完率/期間、運用不振基準は未確定。macro par内の2035年0.38を、componentが2035評価で必要とする2034観測と取り違えない。閾値を正式採用せず、今回はKPIマクロ感度を実行していない。',
 '税源・移行：所得/金融は調査重み付き合成源泉配分。相続は2024年課税対象申告23.3846兆円・税3.2446兆円の限定範囲で、全遺産/全控除廃止ではない。贈与2.6761兆円・税0.3178兆円は重複排除した非同時の比較枝。法人税移行は既存2033年開始6年ランプで原文フェーズ1とのずれがあるが、今回新時期を採用しない。',
 'EITC基準、外国人材GDP5%定義、N4/実配置データ、共済実区割り、行政簡素化費用、実都市投資・執行主体・財源、2039以降固有効率化はunknown。合成テスト用入力や既存コード値をOwner正式採用値/実観測へ昇格していない。',
 '## 数値比較',
 '下表は基準N3比。GDPは実質兆円、現金・債務は名目兆円。最大差は2026〜2055の絶対値最大。変動幅は試験設計に依存し、政策の重要度の一般的順位でも信頼区間でもない。',
 '|機械試験|GDP差2030|GDP差2055|最大GDP差|現金差2055|債務差2055|SQ割れ年数|','|---|---:|---:|---:|---:|---:|---:|']
 for e in effects:
  lines.append(f"|{e['case']}|{e['GDP_difference2030_trn']:+.6f}|{e['GDP_difference2055_trn']:+.6f}|{e['maximum_abs_GDP_difference_trn']:.6f}|{e['cash_difference2055_trn']:+.6f}|{e['debt_difference2055_trn']:+.6f}|{e['SQ_below_years']}|")
 lines+=['基準GDP−SQは2030年−7.595361131兆円、2055年−44.970844763兆円、SQ割れ26年。税、家計所得/消費、民間投資、PB、利払、現金、債務、基金と給与・給付の各年差分はAnnual_ComparisonとCase_Summaryに格納。未採用追加G/I診断は旧固定比較専用で、今回実行する全枝の追加G/Iは0。',
 'GDPゼロ差の区別：年金政府/保険者配分、政府補填、利息係数は実際に財政・現金へ作用するが、追加G/I OFFではそれら財政変化からGDPへ戻す経路がない。借換率は総発行だけを変え純ストックは中立。GI配分バンドルは実支出0のため不活性。これらを一律に無影響と評価しない。2055年債務は全枝で0だが途中年の債務差は残るため、最大途中年差もImpact_Rankingに格納。基金利回り上昇でGDPが下がる結果は、国内家計財産所得の振替と期間内払出という既存構造に依存し、一般的な運用収益の効果を推計したものではない。',
 '## 不足の帰属と実行可能な改善',
 '政策判断が必要：所得/ジニ目標・対象/期間、雇用純増枠と時期、給付種類/金額/減免曲線、基金制度・財政責任、外国人GDP5%の定義など。今回は選択をOwnerへ要求しない。原文確定済みの税率・75歳・N4・10〜15ブロックを選び直す課題とは分離する。',
 '統計/推計で進められるもの：企業利益・配当・投資の同一分母データ、雇用主体別人数と賃金、所得源泉・控除データ、医療患者/保険者/政府の請求・負担実績、年齢別年金/拠出、実都市・共済加入者情報。統計があっても反応係数・因果効果は別に推計が必要。今回外部新規収集は行わず固定統計を再利用した。',
 '既存コード/データだけで前進できるもの：独立移行日程の引数化、企業資格判定と残余投資/資金の表示分離、家計代替とサービス補完の契約明示、基金/保険者/政府の部門対応表、KPIの年・遅行・unknown入力契約、原文項目と実出力の自動対応。今回そのうち定数の隔離引数化と関連勘定・実入力トレースを実装した。既存全国データのない費目をコード変更だけで閉合したとはしない。',
 '制度/予算権限：雇用主体・任用・給与予算、保険者の補填責任、共済法人・加入/拠出、都市投資主体・国地方分担等。モデル実行承認と現実の法定実施権限は別。追加の承認ゲートやレビュー工程は作成していない。',
 '優先表は感度の大きさ、原文とのずれ、既存データでの実装可能性、二重計上リスクから並べた。未試験項目の感度は0と評価せずuntestedと明記。採用判断/データ/較正/会計/権限の複数不足を単一ラベルへ押し込まない。',
 '## 検証と再現',
 f"基準・前回3年雇用枝の限定再現、毎年の家計/政府/保険者源泉、給付セル集計、基金収益と国内家計対応、税率・VAT固定経路、現金/債務恒等式、追加G/I OFF、借換中立性を検証。入力原本{v['source_files_rechecked']}件は固定Commitとの実バイトSHA-256/サイズ記録。既存原本・共通エンジン等の変更なし。",
 '`python3 handoff/chatgpt-n3-assumptions-specification-calibration-separation-20261123/N3_Assumptions_Sensitivity_Reproduce.py --root . --outdir /tmp/n3-assumptions-replay`。標準Python/Git履歴で再現。Sensitivity_Inputs.jsonはすべて未採用機械テスト値。',
 '実行結果の限界：全国較正、所得分配/内生ジニ、現実の2030予算・全国保険財源・部門閉合・実発行権限は未完了。個別感度の結果を同時変更効果や確率予測として合算しない。正式政策採用・暫定改訂N3・PR/merge・Acceptance・DecisionLog・Freeze・Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。']
 (out/'SPE_N3_Assumptions_Specification_Calibration_Report_DRAFT_20261123.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.outdir.resolve())
