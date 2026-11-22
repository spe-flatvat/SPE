#!/usr/bin/env python3
import argparse,copy,csv,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
PIN='f62f00a08e9db2ad05b472034c963de1a4f346c4'
PREV='handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123'
HERE='handoff/chatgpt-n3-native-policy-completion-20261123'
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(root,out):
 out.mkdir(parents=True,exist_ok=True);F=mod('supported_functions',root/HERE/'Native_Supported_Functions.py')
 S=mod('completion_previous',root/PREV/'N3_Native_Diagnostic_Reproduce.py');m=mod('completion_sfa',root/S.SFA/'N3_SFA_Reproduce.py')
 authority=json.loads((root/S.AUTH/'Conditional_Finite_Authority_Inputs.json').read_text());caps={int(y):v for y,v in authority['annual_caps'].items()}
 source=(root/PREV/'Resolved_Separation_Runtime.py.txt').read_text();ns=dict(m.T.previous.__dict__);exec(compile(source,'fixed_separation_runtime','exec'),ns)
 class Runner(m.Runner):
  simulate=ns['simulate']
  def authority_cap(self,s,y,k):return 0. if s['GI_mode']=='OFF' else caps[y][k]
  def cash_budget(self,s,y,pb,interest,sfa,assets):
   base=super().cash_budget(s,y,pb,interest,sfa,assets)
   if s['GI_mode']=='OFF':return 0.
   extra=authority['conditional_expenditure_authority_2030_trn'] if y==2030 else 0.
   return min(base+extra,max(0.,pb-interest-self.cash_part(s,y,sfa)+caps[y]['borrowing']))
  def component(self):
   co,md=super().component();runner=self;step=co.step
   def connected(y,md,prior):
    initial=co.cfg.get('public_job_target',100000)
    if getattr(runner,'conditional_timing',False):
     old=max(0.,min(1.,(y-2030+1)/6));new=max(0.,min(1.,(y-md.s['household_start']+1)/md.s['household_ramp']))
     co.cfg['public_job_target']=initial*new/old if old else initial
    try:r=step(y,md,prior)
    finally:co.cfg['public_job_target']=initial
    event=co.events[-1] if co.events else {};pen=co.pension[-1]
    rule=F.kpi_review(y,income_growth=event.get('previous_income_growth_pct'),income_target=None,
      gini=None,gini_reference=None,fund_return=co.cfg.get('fund_return'),return_floor=None)
    runner.functions.append(dict(case=runner.active_case,year=y,phase=F.phase(y),**rule,
      income_growth_proxy_pct=event.get('previous_income_growth_pct'),income_target_pct='unknown',gini='unknown',
      EITC_baseline_trn='unknown',EITC_removal_measured=False,net_new_public_jobs=r['public_added_jobs'],
      original_employment_phase1_complete=y>=2032,legacy_employment_ramp_complete=y>=2035,
      employment_timing_status='CONDITIONAL_EXISTING_HOUSEHOLD_RAMP' if getattr(runner,'conditional_timing',False) else 'LEGACY_RAMP_CROSSES_PHASE1',
      invoice_status=F.invoice_transition(None,None)['status'],coop_partition_status=F.coop_partition(None,None,None)['status'],
      foreign_eligibility=F.foreign_eligibility(None,None,None,None)['eligible'],new_G_trn=0.,new_public_I_trn=0.,
      optimization_saving_trn='unknown'))
    runner.pensions.append(dict(case=runner.active_case,**pen))
    runner.policy.append(dict(case=runner.active_case,**r))
    runner.ck(str(y)+':fund_carry',pen['fund_end_trn']-pen['fund_begin_trn']-pen['fund_return_trn']-pen['fund_contribution_trn']+pen['fund_payout_trn'])
    return r
   co.step=connected;return co,md
 r=Runner(root,out);r.functions=[];r.pensions=[];r.policy=[]
 old=rd(root/PREV/'N3_Native_vs_Diagnostic_Annual_Comparison_2026_2055.csv');native={int(x['year']):x for x in old if x['case']=='N3_NATIVE_EXISTING'}
 delivered=[x for x in old if x['case'] in ['N3_NATIVE_EXISTING','N3_PLUS_GI_DIAGNOSTIC','SQ_REFERENCE']];led=[];bridges=[];cases=[]
 for cid,conditional,gi in [('N3_NATIVE_COMPLETED_SUPPORTED',False,False),('N3_NATIVE_CONDITIONAL_OPTION',True,False)]:
  r.active_case=cid;r.conditional_timing=conditional
  s=m.spec(cid,cash_partition='SECTOR',q_central=0.,q_local=0.,GI_mode='OFF');s.update(conditional_employment_household_ramp=conditional)
  a,l,b=r.simulate(s);cases.append(s);led+=l;bridges+=b
  for x,lx in zip(a,l):
   y=x['year'];x.update(result_origin='NEW_ANNUAL_EXECUTION',fixed_source_commit=PIN,
    additional_G_nominal_trn=x['government_purchase_nominal_trn'],additional_public_I_nominal_trn=x['public_investment_nominal_trn'],
    actual_usable_cash_trn='unknown',total_government_final_consumption_nominal_trn='unknown',total_public_GFCF_nominal_trn='unknown',
    actual_bond_issuance_trn='unknown',cash_assets_begin_trn=lx['assets_begin_trn'],cash_assets_end_trn=lx['assets_end_trn'],
    cash_new_borrowing_candidate_trn=lx['new_cash_borrowing_trn'],SFA_total_residual_trn=lx['SFA_trn'],
    cash_redemption_candidate_trn=lx['cash_debt_redemption_trn'],new_payroll_added_to_G_trn=0.,new_in_kind_added_to_G_trn=0.,
    intergovernment_transfer_trn=0.,conditional_only=conditional)
   r.ck(cid+str(y)+':GI_off',x['government_purchase_nominal_trn']+x['public_investment_nominal_trn'])
   if not conditional:
    for k in ['real_GDP_trn','nominal_GDP_trn','total_tax_diagnostic_proxy_trn','household_resource_DI_proxy_trn','private_investment_real_trn','CL_PB_candidate_trn','CL_debt_candidate_trn','CL_assets_candidate_trn','existing_public_payroll_delta_trn','existing_in_kind_trn']:
     r.ck('supported_preserves_fixed:'+str(y)+k,x[k]-float(native[y][k]),3e-6)
  delivered+=a
 # Functional tests: missing inputs must never silently become a no-trigger.
 checks=[('KPI_missing',F.kpi_review(2035)['freeze_required'] is None),('KPI_miss',F.kpi_review(2035,-1,0)['freeze_required'] is True),
 ('KPI_equal',F.kpi_review(2035,0,0)['freeze_required'] is False),('KPI_other_year',F.kpi_review(2034,-1,0)['freeze_required'] is None),
 ('gini_missing_size',not F.kpi_review(2035,gini=.4,gini_reference=.38)['relief_executable']),
 ('gini_ready',F.kpi_review(2035,gini=.4,gini_reference=.38,relief_increment=.01,relief_end=2036)['relief_executable']),
 ('invoice_keep',F.invoice_transition(True,True)['valid']),('invoice_violation',not F.invoice_transition(True,False)['valid']),
 ('coop_missing',F.coop_partition(12,None,None)['valid'] is None),
 ('coop_partition',F.coop_partition(10,list(range(10)),{i:i for i in range(10)})['valid']),
 ('coop_range',not F.coop_partition(9,list(range(9)),{i:i for i in range(9)})['valid']),
 ('foreign_unknown',F.foreign_eligibility(4,True,None,None)['eligible'] is None),
 ('foreign_N5',F.foreign_eligibility(5,True,None,None)['eligible'] is False),
 ('foreign_boundary',F.foreign_eligibility(4,True,.05,'TEST_ONLY')['eligible'] is True)]
 regions=r.ci['config']['regions'];front=F.smart_frontiers(regions)
 checks.append(('smart_partial_order',{x['region']:x['dominance_tier'] for x in front}==dict(A=1,B=1,C=2)))
 for name,ok in checks:r.ck('function:'+name,0. if ok else 1.)
 for key,value in [('existing_public_payroll_delta_trn',.018672318768),('existing_in_kind_trn',.275091249212),('existing_policy_government_cost_delta_trn',.293763567980)]:
  r.ck('2030_no_double_count:'+key,float(next(x for x in delivered if x['case']=='N3_NATIVE_COMPLETED_SUPPORTED' and x['year']==2030)[key])-value,1e-10)
 dump(out/'Function_Test_Results.csv',[dict(test=n,passed=bool(ok),input_class='SYNTHETIC_TEST_ONLY_NOT_ANNUAL_POLICY_INPUT') for n,ok in checks])
 dump(out/'Smart_Compact_Partial_Order.csv',[dict(**x,input_class='LEGACY_SYNTHETIC_REGIONS_NOT_REAL_CITY_ALLOCATION') for x in front])
 dump(out/'N3_Native_Completion_Annual_Comparison_2026_2055.csv',delivered)
 dump(out/'N3_Annual_Executable_Functions.csv',r.functions);dump(out/'N3_Pension_Annual_Accounts.csv',r.pensions);dump(out/'N3_Policy_Annual_Accounts.csv',r.policy)
 dump(out/'N3_Completion_Fiscal_Cash_Debt_Ledger.csv',led);dump(out/'N3_Completion_Tax_And_Medical_Connections.csv',r.connections);dump(out/'N3_Completion_Tax_Bridge.csv',bridges)
 diffs=[];summary=[]
 metrics=['real_GDP_trn','nominal_GDP_trn','total_tax_diagnostic_proxy_trn','household_resource_DI_proxy_trn','consumption_real_trn','private_investment_real_trn','CL_PB_candidate_trn','CL_interest_candidate_trn','CL_debt_candidate_trn','CL_assets_candidate_trn']
 for cid in dict.fromkeys(x['case'] for x in delivered):
  a=[x for x in delivered if x['case']==cid];below=sum(float(x['GDP_minus_SQ_trn']) < -1e-7 for x in a)
  for x in a:
   for k in metrics:
    try:delta=float(x[k])-float(native[int(x['year'])][k])
    except (ValueError,TypeError,KeyError):delta='unknown'
    diffs.append(dict(case=cid,year=x['year'],metric=k,delta_vs_native=delta))
  for year in [2030,2035,2039,2055]:
   x=next(x for x in a if int(x['year'])==year)
   summary.append(dict(case=cid,year=year,SQ_below_years=below,**{k:x.get(k,'unknown') for k in metrics},GDP_minus_SQ_trn=x['GDP_minus_SQ_trn'],GDP_delta_vs_native_trn=float(x['real_GDP_trn'])-float(native[year]['real_GDP_trn']),G=x['government_purchase_nominal_trn'],I=x['public_investment_nominal_trn']))
 dump(out/'N3_Native_Completion_Case_Summary.csv',summary);dump(out/'N3_Completion_Numeric_Differences.csv',diffs)
 coverage=[];functions=[]
 additions={
 'A_VAT_SWITCH':('KPI_RULE_EXECUTABLE_MISSING_TARGET','2035 income comparison preserves unknown; threshold supplied only in tests','income definition/target/window; no supported VAT freeze execution'),
 'KPI_REVIEW':('KPI_RULE_EXECUTABLE_MISSING_INPUTS','gini/insurance tri-state triggers and relief readiness gate','gini observations/reference; relief size/duration; insurance floor/response'),
 'A_INVOICE':('NONMONETARY_CONSTRAINT_EXECUTABLE','reject simplification losing small-business relief; missing reform stays unknown','simplified regime, administrative baseline/cost'),
 'B_COOP':('PARTITION_VALIDATOR_EXECUTABLE','check 10-15 blocks, complete unique coverage and no unassigned members','real membership/geography/legal entities, contribution/benefit and efficiency amounts'),
 'D_SMART':('PARTIAL_ORDER_EXECUTABLE','density/productivity dominance tiers; incomparable regions left unordered','real city/asset data, scalar priority rule, project amounts/funding'),
 'C_FOREIGN':('ELIGIBILITY_VALIDATOR_UNRESOLVED_GDP_DEFINITION','N4 AND regional placement AND externally defined GDP cap; unknown propagation','GDP ratio definition and actual individual/region data; no admission/population change'),
 'C_EMPLOYMENT':('PARTIAL_TIMING_CONDITIONAL_ONLY','annual phase conflict exposed; separate execution uses existing household ramp for same regularization target','new posts, employer/budget; exact employment annual allocation unadopted'),
 'S_PHASE1':('PARTIAL_TIMING_CONDITIONAL_ONLY','annual text phase and employment ramp mismatch; separate timing option','exact timing for each policy and corporate tax transition'),
 'S_PHASE2':('PARTIAL_WITH_ANNUAL_ACCOUNTS','text phase attached to annual policy/pension/medical ledgers','institutional transition, cohorts/costs'),
 'S_PHASE3':('NOT_QUANTIFIED_WITH_CONTINUING_ACCOUNTS','post2039 phase state and continuing pension/medical accounts','unique optimization effect and sovereign burden reduction not quantified'),
 'B_PENSION':('PARTIAL_WITH_ANNUAL_ACCOUNTS','fund/public/HH counterpart ledger exported each year with fund carry check','complete cohorts, social-fund consolidation; prior 50/50 candidate not original'),
 'B_MEDICAL':('PARTIAL_WITH_ANNUAL_ACCOUNTS','medical payer and unassigned financing annual connection exported','national financing and clinical response'),
 'B_RELIEF':('PARTIAL_WITH_ANNUAL_ACCOUNTS','existing premium relief and insurer counterpart exported without second HH credit','statutory relief curve and backfill allocation'),
 }
 for x in rd(root/PREV/'N3_Native_Policy_Implementation_Coverage.csv'):
  pid=x['policy_id'];after,behavior,missing=additions.get(pid,(x['native_coverage_status'],'ALREADY_MODELED; existing effect retained',x['original_difference_or_unimplemented']))
  row=dict(policy_id=pid,before_status=x['native_coverage_status'],after_status=after,new_executable_behavior=behavior,
   evidence=f"{PIN}:{x['original_path']} section {x['original_section']}; "+x['implementation_reference']+'; Native_Supported_Functions.py; N3_Native_Completion_Reproduce.py',
   still_missing=missing,conditional_only=pid in ['C_EMPLOYMENT','S_PHASE1'],full_implementation=False)
  coverage.append(row);functions.append(dict(**row,monetary_effect_new='CONDITIONAL_TIMING_ONLY' if row['conditional_only'] else 'NONE_SUPPORTED',
   residual_class='MISSING_DATA; NOT_QUANTIFIABLE_FROM_TEXT' if pid not in ['A_VAT','B_EITC'] else 'ALREADY_MODELED' if pid=='A_VAT' else 'MISSING_DATA'))
 assert len(coverage)==22
 dump(out/'N3_22_Policy_Coverage_Before_After.csv',coverage);dump(out/'N3_Implemented_Functions_And_Residual_Unknowns.csv',functions)
 contract=dict(source_commit=PIN,request_commit='5391530800600594658c740ec2d577b82f76770f',cases=cases,
  supported='nonmonetary rule execution and annual accounting connections; no new monetary calibration',
  conditional='employment REGULARIZE existing target/wages retained; use existing household_start2030/ramp3 instead of legacy2030/ramp6; no net new jobs; unadopted annual allocation',
  KPI_income_target=None,KPI_gini_reference=None,KPI_gini_observations=None,additional_GI_supported=False,
  inherited_private_reinvestment75='UNADOPTED_PREEXISTING_BEHAVIORAL_ASSUMPTION_RETAINED_FOR_COMPARABILITY_NOT_TEXT_VALUE',
  formal_policy_adopted=False,full_native_implementation=False,common_engine_changed=False)
 (out/'Completion_Inputs_And_Case_Definitions.json').write_text(json.dumps(contract,indent=2)+'\n')
 receipts=[]
 # Verify every pre-existing tracked file, including all transitive runtime inputs,
 # against fixed source. No claim based on another AI's report.
 paths=subprocess.check_output(['git','ls-tree','-rz','--name-only',PIN],cwd=root,text=True).strip('\0').split('\0')
 for path in paths:
  b=subprocess.check_output(['git','show',PIN+':'+path],cwd=root)
  local=(root/path).read_bytes();assert b==local,path
  receipts.append(dict(commit=PIN,path=path,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),retrieval='git clone origin; git show fixed commit',match=True))
 request_path='handoff/chatgpt-n3-native-policy-completion-request-20261123/SPE_Work_N3_Native_Policy_Implementation_Completion_Request_20261123.md'
 request_commit='5391530800600594658c740ec2d577b82f76770f'
 b=subprocess.check_output(['git','show',request_commit+':'+request_path],cwd=root);assert (root/request_path).read_bytes()==b
 receipts.append(dict(commit=request_commit,path=request_path,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),retrieval='git show fixed request commit; connector content read',match=True))
 (out/'Input_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 v=dict(status='PASS_LIMITED_IMPLEMENTATION_AND_ANNUAL_EXECUTION' if not r.checks else 'FAIL',checks=r.counter,failed=len(r.checks),failures=r.checks,
  annual_executed_paths=2,annual_executed_rows=60,reused_comparison_paths=3,reused_comparison_rows=90,delivered_annual_rows=len(delivered),prior_PASS_reused=5990,
  original_items=22,full_native_implementation=False,new_supported_monetary_effect=False,conditional_timing_effect_separate=True,
  unchanged_fixed_source_files=len(receipts),source_policy_or_common_engine_modified=False,real_world_fiscal_closure=False)
 (out/'Verification.json').write_text(json.dumps(v,indent=2)+'\n')
 lines=['# N3原文22項目・既存実装補完結果','DRAFT / NON-CANONICAL / ISOLATED EXECUTION / 2026-11-23',
 '原文根拠あり経路と条件付き雇用移行枝を各30年実行。既存N3・SQ・追加G/I診断90年次を固定再利用した。全22項目の完全実装は未達。今回の根拠あり補完は非金銭ルールと年次勘定接続であり、根拠不足の予算・係数を追加していない。',
 '新たに実行できること：2035年の所得・ジニ・保険運用判定をunknownを保ったまま評価、補完率と期間のない軽減措置の実行抑止、共済10〜15ブロックの外部区割り検証、N4・地域配置・GDP上限の三条件検証、インボイス簡素化時の小規模事業者軽減維持検証、人口密度・生産性による優越関係（同順位ではなく比較不能を保持）の計算。いずれも実制度導入完了ではない。',
 '既存都市順位はdensity×productivity/costという仮定。原文は重み・費用除算を確定していないので、既存順位を上書きせず、追加機能は二指標で両方優れる場合だけ優先する部分順序。既存仮想A/B/CではAとBが比較不能、Cが次段。都市別公共投資を創作していない。',
 '税制：30/20/40%、法人20/16%条件、控除処理、相続と贈与の非重複を保持。法人税が2033年から移行する旧候補と原文フェーズ1開始の不整合は未解決。正確な法人移行年・配分が原文にないため変更なし。企業残余75%再投資は引き続き原文由来でない既存仮定。',
 '年金・医療・保険：基金期首/収益/拠出/払出/期末、家計/政府/保険者の既存対応と医療未配賦財源を年次ファイルへ接続。既存50/50負担等は未採用仮定であり原文の国地方負担割合ではない。緩和ケアは共通SQにもある既存効果を保持。追加の削減額や普及費はunknown。EITC比較基準・全国較正も未解決。',
 '2035年：所得成長proxyは既存計算から取得できるが、原文の所得定義・目標・期間は未定。gini実観測・補完率・期間も不足。既存0%閾値や0.38参照を正式値へ昇格しない。KPIルールの発動/非発動は合成試験で確認したが、VAT凍結・追加減免のマクロ作動は根拠あり経路では実行していない。',
 '雇用：既存100000人・給与300/400万円・2030開始6年ランプは既存仮定であり、純増は0。条件付き枝だけ、既存家計移行2030開始3年ランプを正規化へ適用する未採用配分を実行。原文期間への適合例であり原文が確定した年間配分ではない。給与差額は家計・政府双方へ既存処理で一度だけ接続し、新規Gへ加算しない。',
 '## 結果（GDP差：実質兆円）','|経路|年|GDP−SQ|GDP−旧N3|SQ割れ年数|','|---|---:|---:|---:|---:|']
 for z in summary:lines.append(f"|{z['case']}|{z['year']}|{float(z['GDP_minus_SQ_trn']):.9f}|{z['GDP_delta_vs_native_trn']:.9f}|{z['SQ_below_years']}|")
 lines+=['根拠あり経路のGDP・税収・家計・投資・PB・債務・現金差は検証許容内でゼロ。新しい金銭効果が得られたとは評価しない。数値差のある雇用移行は条件付き枝のみ。追加G/Iは旧固定結果の比較専用で今回の施策財源や効果へ流用なし。',
 '2030年既存給与差額0.018672318768兆円、現物0.275091249212兆円、政府費用0.293763567980兆円を含む既存経路を再現。これらを追加Gへ二重計上していない。現金恒等式、債務ストック、基金、税合計等は継承ランタイムで実行検証。政府間移転の新規追加は0、既存統合境界の全面閉合は未確認。名目/実質単位は列名を継承。SQ財政欠落はunknown。',
 f"検証：新規実行チェック{v['checks']}件、失敗{v['failed']}。前回5990件は再利用し再監査PASSとは記さない。合成機能試験は実政策入力ではない。固定原本{len(receipts)}ファイルを自身の実バイトで照合。",
 '再現：`python3 '+HERE+'/N3_Native_Completion_Reproduce.py --root . --outdir /tmp/n3-completion-replay`。Git履歴を持つcheckoutが必要。全原本照合・限定再実行を含む。',
 '未完了：全国税源/控除/地方税、法人移行時期、EITC基準、GDP5%定義、KPI目標と観測、年金全コホート、全国医療財源、雇用純増と予算、インボイス具体制度、実在共済区割り・効率化、実都市投資、2039以降最適化効果。全22項目数値実装・実制度導入・全国財政閉合は未達。',
 '本文・税率・控除・共通エンジンと既存原本を変更せず新規ディレクトリのみ。正式採用、暫定改訂N3、PR/merge、Acceptance、DecisionLog、Freeze、Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。']
 (out/'SPE_N3_Native_Policy_Implementation_Completion_Report_DRAFT_20261123.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
 print(json.dumps(v));assert not r.checks,r.checks[:5]
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.outdir.resolve())
