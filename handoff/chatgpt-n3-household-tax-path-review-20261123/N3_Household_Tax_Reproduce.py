#!/usr/bin/env python3
import argparse,csv,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
PIN='93b8393350eb73dd5ebd803b1ace429aaf4dfe1b';AUTH='cca5acaf83843827e97c0d26e78480cc84e63668'
GAP='handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123';PREV='handoff/chatgpt-n3-assumptions-specification-calibration-separation-20261123'
MET=['real_GDP_trn','nominal_GDP_trn','GDP_minus_SQ_trn','consumption_real_trn','total_tax_diagnostic_proxy_trn','household_resource_DI_proxy_trn','private_investment_real_trn','CL_PB_candidate_trn','CL_interest_candidate_trn','CL_assets_candidate_trn','CL_debt_candidate_trn']
def rd(p):return list(csv.DictReader(p.open()))
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def dump(p,a):
 keys=list(dict.fromkeys(k for x in a for k in x))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(a)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def run(root,out):
 out.mkdir(parents=True,exist_ok=True);R=load('household_runtime',HERE/'Household_Tax_Runtime.py')
 old=rd(root/GAP/'N3_GDP_Gap_Counterfactual_Annual_2026_2055.csv');base={int(x['year']):x for x in old if x['case']=='BASE_REPLAY'}
 fixed_wages={int(x['year']):float(x['lagged_wage_factor']) for x in rd(root/GAP/'N3_GDP_Gap_All_Case_Intermediate_Accounts.csv') if x['case']=='BASE_REPLAY'}
 pen={int(x['year']):x for x in rd(root/PREV/'N3_Sensitivity_Pension_Accounts.csv') if x['case']=='BASE_REPLAY'}
 ci=json.loads((root/'handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122/Component_Initialization.json').read_text());hh=ci['household'];stat=json.loads((root/'handoff/chatgpt-n3-policy-burden-diagnosis-20261122/Official_Statistics_Limited_Check.json').read_text())
 mean=sum(c['share']*c['income_yen'] for c in hh['income_cells']);ol=sum(c['share']*c['income_yen']*(.95*(1-c['elder_share'])+.2*c['elder_share']) for c in hh['income_cells']);of=sum(c['share']*c['income_yen']*(.05*(1-c['elder_share'])+.1*c['elder_share']) for c in hh['income_cells'])
 observed=stat['sources'][0];ls=mean*(observed['official_labor_income_yen']/observed['official_mean_household_income_yen'])/ol;fs=mean*(observed['official_property_income_yen']/observed['official_mean_household_income_yen'])/of
 shares=[.95*ls,.05*fs,.20*ls,.10*fs];assert shares[0]+shares[1]<=1 and shares[2]+shares[3]<=1
 cases=[dict(case='BASE_REPLAY',kind='PINNED_BASELINE',component_spec={}),dict(case='LABOR_WEDGE_OFF',kind='MECHANICAL_IDENTIFICATION_NOT_POLICY',component_spec={'mute_labor_wedge':True}),
  dict(case='FINANCIAL_WEDGE_OFF',kind='MECHANICAL_IDENTIFICATION_NOT_POLICY',component_spec={'mute_financial_wedge':True}),
  dict(case='PRIOR_FULL_ALLOCATION',kind='MECHANICAL_PRIOR_TAX_ALLOCATION_BOUNDARY_NOT_CALIBRATED',component_spec={'prior_allocation_full':True}),
  dict(case='SURVEY_SOURCE_MOMENTS',kind='EVIDENCE_LINKED_PARTIAL_SOURCE_MOMENT_CANDIDATE_NOT_NATIONAL_TAX_CALIBRATION',component_spec={'income_source_shares':shares}),
  dict(case='SURVEY_SOURCE_AND_PRIOR_FULL',kind='COMBINED_UNADOPTED_DIAGNOSTIC_NOT_INDEPENDENT_EFFECT',component_spec={'income_source_shares':shares,'prior_allocation_full':True})]
 write(out/'Household_Tax_Inputs_And_Cases.json',dict(cases=cases,derived_source_shares=shares,observed_income_year=2024,survey_year=2025,property_income_not_full_financial_tax_base=True,
  pension='EXACT_ANNUAL_FLOW_FIXED_TO_PRIOR_BASELINE_BY_COMPENSATING_PENSION_WAGE_DRIVER_ONLY',tax_rates=[.3,.2],new_deductions=None,SQ='FIXED',GI='OFF',policy_adopted=False))
 annual=[];trace=[];trans=[];cells=[];pensions=[];fisc=[];summ=[];checks=0;fails=[];baseC=None
 for d in cases:
  r,s=R.build(root,out,d,fixed_wages);a,l,b=r.simulate(s)
  by={y:[x for x in r.live_component.households if x['year']==y] for y in range(2026,2056)}
  for x in a:
   y=x['year'];items=by[y];p=pen[y];pp=r.live_component.pension[y-2026]
   for k in ['fund_begin_trn','fund_contribution_trn','fund_return_trn','fund_payout_trn','fund_end_trn','public_benefit_delta_trn','government_cash_cost_delta_trn','public_insurer_cash_delta_trn','household_cash_after_counterpart_trn']:
    r.ck(d['case']+str(y)+':fixed_pension:'+k,pp[k]-float(p[k]),1e-6)
   r.ck(d['case']+str(y)+':HH_count',sum(z['households'] for z in items)-r.sq[y]['demography']['population']/hh['stats']['mean_household_size'],1e-6)
   for source,basekey,oldkey,targetkey,wedgekey,rate,muteflag in [('LABOR_BUSINESS','labour_business_30_gross_base_trn','prior_labor_trn','target_labor_trn','labor_wedge_trn',.3,'mute_labor_wedge'),('FINANCIAL','financial20_gross_base_trn','prior_financial_trn','target_financial_trn','financial_wedge_trn',.2,'mute_financial_wedge')]:
    gross=sum(z[basekey] for z in items);prior=sum(z[oldkey] for z in items);target=sum(z[targetkey] for z in items);wedge=sum(z[wedgekey] for z in items);phase=items[0]['phase']
    r.ck(d['case']+str(y)+source+':rate',target-rate*gross)
    r.ck(d['case']+str(y)+source+':wedge',wedge-(0. if s is None else 0.) if d['component_spec'].get(muteflag) else wedge-(target-prior)*phase)
    trace.append(dict(case=d['case'],year=y,source=source,gross_base_proxy_trn=gross,prior_allocated_tax_trn=prior,target_tax_before_phase_trn=target,phase=phase,incremental_tax_trn=wedge,
     households=sum(z['households'] for z in items),denominator='fixed_population/2.22 weighted_all_households; not taxpayer_count',source_income_year=2024,survey_year=2025,
     income_deduction='new tax is gross proxy with no legal deduction microdata; pension-income treatment/local redesign OPEN; prior tax includes existing deductions implicitly',
     source_path='N3_Components.step -> Gap_Components -> parity dynamic bases -> Household_Tax_Runtime in-memory method',unit='TRILLION_YEN_NOMINAL',provenance='fixed survey cells and tax-payment frequencies; source shares candidate'))
   sum_prior=sum(z['prior_labor_trn']+z['prior_financial_trn'] for z in items);all_prior=sum(z['observed_all_national_tax_trn'] for z in items)
   if d['component_spec'].get('prior_allocation_full'):r.ck(d['case']+str(y)+':full_old_tax_once',sum_prior-all_prior)
   else:r.ck(d['case']+str(y)+':prior_not_overallocated',max(0.,sum_prior-all_prior))
   r.ck(d['case']+str(y)+':income_sources_no_overlap',sum(max(0.,z['labor_share']+z['financial_share']-1) for z in items))
   r.ck(d['case']+str(y)+':tax_cell_sum',sum(z['labor_wedge_trn']+z['financial_wedge_trn']-z['flat_tax_delta_trn'] for z in items))
   r.ck(d['case']+str(y)+':GI_off',x['government_purchase_nominal_trn']+x['public_investment_nominal_trn'])
   if d['case']=='BASE_REPLAY':
    for k in MET:r.ck('baseline'+str(y)+k,x[k]-float(base[y][k]),3e-6)
   x.update(case=d['case'],kind=d['kind'],pension_realized_flows_fixed=True,SQ_unchanged=True,GDP_minus_initial2026_trn=x['real_GDP_trn']-580.,C_state_real_trn=r.midpoints[y-2026]['C'])
   for k in MET:x['delta_vs_base_'+k]=x[k]-float(base[y][k])
   annual.append(x);pensions.append(dict(case=d['case'],**pp))
   for z in items:cells.append(dict(case=d['case'],**z))
  if d['case']=='BASE_REPLAY':(out/'Resolved_Household_Tax_Component.py.txt').write_text(r.tax_source)
  for t in r.targets:
   if t['channel'] in ['labor_tax','financial_tax','income_feedback']:trans.append(t)
  fisc+=l;checks+=r.counter;fails+=r.checks
  below=sum(x['GDP_minus_SQ_trn']<-1e-7 for x in a)
  for y in [2030,2035,2039,2055]:
   x=a[y-2026];summ.append(dict(case=d['case'],kind=d['kind'],year=y,SQ_below_years=below,**{k:x[k] for k in MET},GDP_minus_initial2026_trn=x['real_GDP_trn']-580.,GDP_delta_vs_base=x['real_GDP_trn']-float(base[y]['real_GDP_trn'])))
  print(json.dumps(dict(case=d['case'],rows=30,checks=r.counter,failed=len(r.checks),gap2030=a[4]['GDP_minus_SQ_trn'],gap2055=a[-1]['GDP_minus_SQ_trn'])))
 # Reuse predecessor full-tax OFF and exact fixed SQ without rerunning or applying survey changes to SQ.
 reused=[x for x in old if x['case']=='NO_HH_FLAT_TAX']
 sq=rd(root/'handoff/chatgpt-n3-native-policy-completion-20261123/N3_Native_Completion_Annual_Comparison_2026_2055.csv');reused +=[x for x in sq if x['case']=='SQ_REFERENCE']
 dump(out/'Reused_Fixed_Tax_OFF_And_SQ.csv',reused)
 for x in reused:
  z=dict(x);y=int(x['year']);z.update(kind='REUSED_FIXED_REFERENCE',GDP_minus_initial2026_trn=float(x['real_GDP_trn'])-580.,pension_realized_flows_fixed='original fixed path; not reexecuted',result_origin='REUSED_93b8393350_or_e8bea036')
  for k in MET:
   try:z['delta_vs_base_'+k]=float(x[k])-float(base[y][k])
   except (ValueError,KeyError):z['delta_vs_base_'+k]='unknown'
  annual.append(z)
 gaps=[dict(item='National labor/business tax base',observed='2024 survey operating-income mean4262000 yen/HH; synthetic gross source4596631.29 before uplift',proxy='all-household count/population2.22 and age-source fractions; source moment candidate',unknown='business expenses/taxpayer vs HH/legal tax-base crosswalk; national2026-2055 base',resolution='joint source/taxpayer/deduction microdata, no invented gross base'),
 dict(item='Financial tax base',observed='2024 survey property income160000 yen/HH',proxy='synthetic financial income344290.51 yen/HH',unknown='capital gains/withholding/overlap with corporate dividends; property is not full taxable financial income',resolution='source-moment match is scope-changing diagnostic, not verified financial tax calibration'),
 dict(item='Prior national tax allocation',observed='quintile mean national income tax × paid frequency',proxy='old national tax allocated by total-income source shares',unknown='source-specific prior tax incl pensions; normalized allocation uses full oldtax as boundary only',resolution='obtain source-level prior effective taxes; no source double allocation'),
 dict(item='Deductions and non-taxable incomes',observed='original policy says deductions abolition; pension/local treatment unresolved',proxy='gross proxy×30/20 with old net-of-deduction tax subtraction',unknown='legal deduction types/amounts, pensions/non-taxable/remittance scope',resolution='no new deduction/rate adopted'),
 dict(item='Macro diagnostic tax cap',observed='2024 general-account income tax21.2trn, total75.2trn, different year/scope',proxy='macro tax proxy plus policy wedge; cap applies to macro component only',unknown='full national taxes/reconciliation and possible scope overlap',resolution='do not calibrate future proxy to2024 national receipts by arbitrary multiplier'),
 dict(item='Consumption transmission',observed='no causal response estimate provided',proxy='MPC0.72, domestic0.8, lambdaC0.6, income_feedback0.08',unknown='income-class MPC and response identification',resolution='coefficients fixed; tax-source change not behavioral-parameter calibration'),
 dict(item='Pension and other policy control',observed='fixed baseline pension ledger available',proxy='pension annual wage driver compensated to reproduce exact baseline flows',unknown='empirical pension validity remains separate request',resolution='pension benefits/contributions/returns/payouts/balances fixed; corporate/VAT/medical parameters unchanged, realized endogenous responses can differ')]
 dump(out/'N3_Household_Tax_Calibration_Gaps.csv',gaps);dump(out/'N3_Household_Tax_Base_And_Prior_Tax_Trace.csv',trace);dump(out/'N3_Household_Tax_Cell_Trace.csv',cells);dump(out/'N3_Household_Tax_Consumption_Transmission.csv',trans)
 dump(out/'N3_Household_Tax_Annual_Counterfactual_2026_2055.csv',annual);dump(out/'N3_Household_Tax_Case_Definitions.csv',[dict(case=x['case'],kind=x['kind'],changes=json.dumps(x['component_spec'])) for x in cases]);dump(out/'N3_Household_Tax_Case_Summary.csv',summ)
 dump(out/'Fixed_Pension_Control_Ledger.csv',pensions);dump(out/'N3_Household_Tax_Fiscal_Ledger.csv',fisc)
 paths=[str(p.relative_to(root)) for p in (root/GAP).iterdir() if p.is_file()]+[PREV+'/N3_Sensitivity_Pension_Accounts.csv',PREV+'/Sensitivity_Runtime.py','policies/New3linesPolicies.md','handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122/Component_Initialization.json','handoff/chatgpt-n3-policy-burden-diagnosis-20261122/Official_Statistics_Limited_Check.json']
 rec=[]
 for path in sorted(set(paths)):
  b=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);assert (root/path).read_bytes()==b
  rec.append(dict(commit=PIN,path=path,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 request='handoff/chatgpt-n3-household-tax-path-review-request-20261123/SPE_Work_N3_Household_Tax_Base_Calibration_And_Transmission_Request_20261123.md';b=subprocess.check_output(['git','show',AUTH+':'+request],cwd=root);assert b==(root/request).read_bytes();rec.append(dict(commit=AUTH,path=request,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 write(out/'Input_Source_Receipts.json',rec)
 v=dict(status='PASS_LIMITED_HOUSEHOLD_TAX_REVIEW' if not fails else 'FAIL',executed_paths=6,executed_annual_rows=180,reused_rows=60,delivered_rows=len(annual),checks=checks,failed=len(fails),failures=fails,prior_PASS_reused=[13928,32439],pension_realized_flows_fixed=True,SQ_modified=False,GI=False,tax_rates_or_formal_deductions_changed=False,national_calibration=False,source_files_checked=len(rec))
 write(out/'Verification.json',v)
 lines=['# N3家計課税経路の限定精査','DRAFT / NON-CANONICAL / 2026-11-23',
 '全国課税較正は未達。原文30%/金融20%を変更せず、源泉別税負担を識別し、固定調査の所得種類別構成へ合わせる根拠付き候補と、従前税配賦の機械的境界を区別して実行した。正しい税源補正や税制撤回案を採用した結果ではない。',
 '基準：2030年労働・事業proxy295.817492×30%=88.745248、従前14.770375との差×1/3=24.658291兆円。金融proxy22.156912×20%と従前0.952983との差×1/3=1.159466。2055年追加は労働102.658687、金融4.827151。税源は全世帯の合成所得であって納税者数・給与支払総額・課税所得額の実測ではない。',
 '世帯数=共通人口/平均世帯人員2.22。セル重み、所得2024/調査2025、所得帯中点・年齢源泉比、income_scale1.04、共通物価、内生賃金比を使用。旧税は五分位の支払額×支払頻度で、旧税全額を源泉へ正確に対応付けたものではない。現行はoldtax×労働/金融所得比、全額配賦診断はその比を労働+金融比で正規化するため、未配賦の公的年金等の旧税まで割り当て得る。後者を補正確定値とは扱わない。',
 '所得控除は新たな法定控除表を作らず、既存は新制度の粗所得proxy×原文税率と、既存控除等を含む従前税の差。年金所得・非課税項目・事業費用・地方税改革の厳密な境界は不明。給与/金融の非重複をセルで検証したが、全国課税の網羅性PASSではない。企業改革による追加配当20%課税は別フローで今回OFFにしていない。',
 f"原データの確認：厚労省2026白書PDF p10の2025調査/2024所得は平均575.2万円、稼働426.2万円、財産16.0万円。既存セル平均{mean:.3f}円、労働{ol:.3f}円、金融{of:.3f}円。候補はセル平均を保ったまま調査源泉構成へ合わせ、派生4係数{shares}を使用。財産所得と譲渡益等を含む金融税源は同義ではなく、これだけで全国金融課税較正はできない。",
 '消費は税差額を家計資源から一度控除し、国内比0.8×MPC0.72/デフレーター→Ctarget→平滑化0.6→GDPへ。これら行動係数は変更しない。年金は基準の年次給付/拠出/運用益/払出/基金残高/政府・保険者負担まで固定し、税変更による賃金の影響を年金用ドライバーだけで相殺。その他施策の設定は保持するが内生的な実現値の反応は残す。',
 '|経路|年|GDP−SQ|基準との差|SQ割れ年数|','|---|---:|---:|---:|---:|']
 for z in summ:
  if z['year'] in [2030,2055]:lines.append(f"|{z['case']}|{z['year']}|{z['GDP_minus_SQ_trn']:+.6f}|{z['GDP_delta_vs_base']:+.6f}|{z['SQ_below_years']}|")
 lines += ['前回課税ブロックOFFと固定SQは別ファイル/年次比較へ再利用。前回OFFはその時の内生年金状態を含み、今回の年金実現フロー固定対照とは完全に同じ制御ではないため、厳密な労働/金融相互作用の基準へ転用しない。SQ超えは各年のSQ差で判定し、2055年−580兆円は補助指標。',
 f"新規6経路180年次、既存60年次再利用。チェック{checks}件・失敗{len(fails)}。源泉税額、従前税の非重複配賦、所得源泉上限、世帯集計、GDP算術、年金フロー固定、追加G/I OFFを検証。全国較正や控除別税源の解消は未完了。外部PDFを取得し本文の対象年・母集団を確認したが、将来税源へ任意倍率で合わせていない。",
 '出典：[厚労省白書p10](https://www.mhlw.go.jp/wp/hakusyo/kousei/26-2/dl/01.pdf)、[財務省2024一般会計決算](https://www.mof.go.jp/policy/budget/budger_workflow/account/fy2024/ke0711b.pdf)。2024年一般会計所得税21.2兆円・総税収75.2兆円は、将来の合成課税差額とは年・税源・範囲が異なる。取得原本のSHA/サイズと未解決範囲はPublic_Source_Check.json/Calibration_Gapsに記録。',
 '再現：`python3 handoff/chatgpt-n3-household-tax-path-review-20261123/N3_Household_Tax_Reproduce.py --outdir /tmp/n3-tax-replay`。既存原本・共通エンジン・SQ・税率・控除・年金正式制度は変更なし。正式採用・Acceptance・PR/merge・Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。']
 (out/'SPE_N3_Household_Tax_Path_Review_Report_DRAFT_20261123.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
 print(json.dumps(v));assert not fails,fails[:4]
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.outdir.resolve())
