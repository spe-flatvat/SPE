#!/usr/bin/env python3
import argparse,csv,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
PIN='93b8393350eb73dd5ebd803b1ace429aaf4dfe1b';AUTH='cca5acaf83843827e97c0d26e78480cc84e63668'
GAP='handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123';PREV='handoff/chatgpt-n3-assumptions-specification-calibration-separation-20261123'
MET=['real_GDP_trn','nominal_GDP_trn','GDP_minus_SQ_trn','consumption_real_trn','household_resource_DI_proxy_trn','total_tax_diagnostic_proxy_trn','CL_PB_candidate_trn','CL_interest_candidate_trn','CL_assets_candidate_trn','CL_debt_candidate_trn','pension_fund_end_trn']
def rd(p):return list(csv.DictReader(p.open()))
def write(p,a):p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n')
def dump(p,a):
 keys=list(dict.fromkeys(k for x in a for k in x))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(a)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def run(root,out):
 out.mkdir(parents=True,exist_ok=True);R=load('pension_runtime',HERE/'Pension_Path_Runtime.py')
 old=rd(root/GAP/'N3_GDP_Gap_Counterfactual_Annual_2026_2055.csv');base={int(x['year']):x for x in old if x['case']=='BASE_REPLAY'}
 fixed={int(x['year']):x for x in rd(root/GAP/'N3_GDP_Gap_All_Case_Intermediate_Accounts.csv') if x['case']=='BASE_REPLAY'};wages={y:float(x['lagged_wage_factor']) for y,x in fixed.items()}
 cases=[dict(case='BASE_REPLAY',kind='FIXED_BASELINE',return_source='DOMESTIC_HH'),
  dict(case='EXTERNAL_ISSUER_RETAINED',kind='CONDITIONAL_SOURCE_DIAGNOSTIC_NOT_ADOPTED',return_source='EXTERNAL_ISSUER'),
  dict(case='GOVERNMENT_FUND_TRANSFER',kind='CONDITIONAL_TRANSFER_GUARANTEE_NOT_INVESTMENT_RETURN_OR_ADOPTED_POLICY',return_source='GOVERNMENT_TRANSFER'),
  dict(case='NO_HH_DEBIT_SOURCE_UNALLOCATED',kind='NEGATIVE_CONTROL_SOURCE_NOT_CLOSED_NOT_CORRECTION',return_source='UNALLOCATED'),
  dict(case='WORKING_AGE_CONTRIBUTORS_ONLY',kind='AGE_BASE_CONSISTENCY_CANDIDATE_NOT_POPULATION_CALIBRATED',return_source='DOMESTIC_HH',cohort_mode='WORKING_AGE_ONLY')]
 write(out/'Pension_Case_Definitions_And_Inputs.json',dict(cases=cases,source_commit=PIN,request_commit=AUTH,GI='OFF',SQ='UNCHANGED',
  household_labor_financial_tax='EXACT_ANNUAL_BASE_AND_PRIOR_TAX_WEDGES_FIXED',household_tax_rates=[.3,.2],return_rate=.02,
  cohort_entry_legacy=[[32,.65],[52,.25],[67,.08],[72,.02]],cohort_entry_candidate=[[32,.65/.9],[52,.25/.9]],fund_payout_years=20,
  public_benefit_coverage=.85,contribution_rate=.183,diversion=.25,worker_share=.70,annual_reference_wage_yen=4000000,public_government_share=.5,
  real_policy_or_correct_return_source_adopted=False))
 raw=[];ledger=[];returns=[];cohorts=[];schedule=[];trans=[];fisc=[];summ=[];checks=0;fails=[];cache={};source_codes={}
 for d in cases:
  r,s=R.build(root,out,d,wages);a,l,b=r.simulate(s)
  source_codes[d['case']]=r.pension_source
  for x,pen,p,src,lx in zip(a,r.live_component.pension,r.live_component.rows,r.return_trace,l):
   y=x['year'];i=y-2026;pre=d['case']+str(y);mid=r.midpoints[i];grant=src['government_fund_transfer_trn'];H=src['domestic_HH_property_income_debit_trn'];X=src['external_issuer_payment_trn'];B=pen['public_benefit_delta_trn'];C=pen['fund_contribution_trn'];F=pen['fund_payout_trn'];RR=pen['fund_return_trn']
   HH=B+F-H;G=-pen['government_cash_cost_delta_trn']-grant;ins=pen['public_insurer_cash_delta_trn'];fund=C+RR-F;ext=-X;unallocated=HH+G+ins+fund+ext
   r.ck(pre+':fund_stock',pen['fund_end_trn']-pen['fund_begin_trn']-C-RR+F)
   r.ck(pre+':effective_return_or_transfer_stock',pen['fund_end_trn']-pen['fund_begin_trn']-C-src['effective_investment_return_trn']-grant+F)
   for key in ['coreY','coreN','coreD']:r.ck(pre+':SQ_common_'+key,r.base[y][key]-r.sq[y][key])
   r.ck(pre+':SQ_population',r.base[y]['demography']['population']-r.sq[y]['demography']['population'])
   r.ck(pre+':sector_transfer_residual',unallocated-src['source_unallocated_trn'])
   if d['return_source']!='UNALLOCATED':r.ck(pre+':identified_diagnostic_transfer_symmetry',unallocated)
   else:r.ck(pre+':negative_control_unallocated_detected',unallocated-RR)
   r.ck(pre+':no_second_contribution_HH_charge',pen['second_contribution_charge_trn'])
   r.ck(pre+':household_pension_flow',pen['household_cash_after_counterpart_trn']-HH)
   r.ck(pre+':policy_government_pension_plus_grant',p['policy_government_cost_delta_trn']-(p['in_kind_trn']-p['EITC_removal_trn']+pen['government_cash_cost_delta_trn']+p['public_payroll_delta_trn']+grant))
   for key,actual in [('policy_labour_business_flat30_tax_delta_trn',p['labour_business_flat30_tax_delta_trn']),('policy_household_financial20_tax_delta_trn',p['household_financial20_tax_delta_trn'])]:r.ck(pre+':fixed_HH_tax:'+key,actual-float(fixed[y][key]),1e-6)
   cc=[z for z in r.cohort_trace if z['year']==y]
   for z in cc:r.ck(pre+':individual_cohort_stock:'+str(z['entry_year'])+str(z['entry_age']),z['assets_end_trn']-z['assets_begin_trn']-z['contribution_trn']-z['booked_return_trn']+z['payout_trn'])
   for ck,pk in [('assets_end_trn','fund_end_trn'),('contribution_trn','fund_contribution_trn'),('booked_return_trn','fund_return_trn'),('payout_trn','fund_payout_trn')]:r.ck(pre+':cohort_aggregate:'+ck,sum(z[ck] for z in cc)-pen[pk])
   if d.get('cohort_mode')=='WORKING_AGE_ONLY':r.ck(pre+':new_contributor_under65',sum(z['contribution_trn'] for z in cc if z['entry_year']==y and z['entry_age']>=65))
   r.ck(pre+':GI_off',x['government_purchase_nominal_trn']+x['public_investment_nominal_trn'])
   if d['case']=='BASE_REPLAY':
    fixed_trans=rd(root/GAP/'N3_GDP_Gap_Transmission_Trace.csv')
    for channel in ['pension_benefit','fund_payout','fund_domestic_return_debit']:
     now=next(t['filtered_C_state_real_trn'] for t in r.targets if t['year']==y and t['channel']==channel)
     prior=float(next(t['filtered_C_state_real_trn'] for t in fixed_trans if int(t['year'])==y and t['channel']==channel))
     r.ck(pre+':baseline_pension_C_source_'+channel,now-prior)
    for k in MET:r.ck(pre+':baseline_'+k,x[k]-float(base[y][k]),3e-6)
   ledger.append(dict(case=d['case'],year=y,fund_begin_trn=pen['fund_begin_trn'],diverted_existing_contribution_trn=C,
    effective_investment_return_trn=src['effective_investment_return_trn'],government_transfer_to_fund_trn=grant,legacy_booked_fund_return_trn=RR,
    fund_payout_trn=F,fund_end_trn=pen['fund_end_trn'],public_benefit_delta_trn=B,HH_pension_cash_delta_trn=HH,
    government_pension_cash_delta_trn=G,public_insurer_cash_delta_trn=ins,fund_asset_change_trn=fund,external_issuer_cash_delta_trn=ext,
    sector_flow_residual_trn=unallocated,unallocated_source_trn=src['source_unallocated_trn'],HH_second_contribution_charge_trn=0.,
    government_aggregate_cash_assets_trn=x['CL_assets_candidate_trn'],government_aggregate_debt_trn=x['CL_debt_candidate_trn'],
    actual_HH_total_cash_stock='unknown',actual_HH_pension_claim_on_fund_stock='unknown',fund_liability_or_owner_equity='unknown',
    real_portfolio_counterparty='unknown',formal_government_funding_authority='unknown',full_national_sector_closure=False))
   phase=max(0.,min(1.,(y-2033+1)/6));idx=r.ci['deflators'][i]/r.ci['deflators'][0];unit=sum(z['weight']*z['pension_month'] for z in r.ci['pension']['public']['strata'])*12*idx
   counts={grp:sum(r.ci['elder'][i][grp+'_'+sex+'_population'] for sex in ['male','female']) for grp in ['65_69','70_74']}
   f65=min(1.,max(0.,(y-2033+1)/5));f70=min(1.,max(0.,(y-2033+1-5)/5));delayed=(counts['65_69']*f65+counts['70_74']*f70)*.85*phase
   r.ck(pre+':cohort_delay_formula',pen['delayed_recipients_candidate']-delayed,1e-6);r.ck(pre+':benefit_formula',B+delayed*unit/1e12)
   schedule.append(dict(case=d['case'],year=y,phase=phase,protected65_entry_year=2033,population65_69=counts['65_69'],population70_74=counts['70_74'],fraction65_69=f65,fraction70_74=f70,
    coverage_proxy=.85,delayed_recipients=delayed,annual_benefit_unit_yen=unit,public_benefit_delta_trn=B,working_age_population=r.ci['trajectory'][i]['working_age'],
    contribution_wage_reference_yen=4000000,actual_lagged_wage_factor=mid['lagged_wage_factor'],contribution_trn=C,payout_trn=F,
    mortality_and_exit_model='NOT_IDENTIFIED_IN_FUND_COHORTS',source='pinned coarse-age elder series and public strata80k/150k/250k monthly with0.4/0.4/0.2 weights'))
   x.update(case=d['case'],kind=d['kind'],HH_labor_financial_tax_actual_wedges_fixed=True,SQ_unchanged=True,GDP_minus_initial2026_trn=x['real_GDP_trn']-580.)
   for k in MET:x['delta_vs_base_'+k]=x[k]-float(base[y][k])
   raw.append(x)
  cache[d['case']]=a;returns+=r.return_trace;cohorts+=r.cohort_trace;fisc+=l;checks+=r.counter;fails+=r.checks
  for z in r.targets:
   if z['channel'] in ['pension_benefit','fund_payout','fund_domestic_return_debit','income_feedback']:trans.append(z)
  below=sum(x['GDP_minus_SQ_trn']<-1e-7 for x in a)
  for y in [2030,2035,2039,2055]:
   x=a[y-2026];summ.append(dict(case=d['case'],kind=d['kind'],year=y,SQ_below_years=below,**{k:x[k] for k in MET},GDP_delta_vs_base=x['real_GDP_trn']-float(base[y]['real_GDP_trn']),GDP_minus_initial2026_trn=x['real_GDP_trn']-580.))
  print(json.dumps(dict(case=d['case'],rows=30,checks=r.counter,failed=len(r.checks),gap2055=a[-1]['GDP_minus_SQ_trn'],fund2055=a[-1]['pension_fund_end_trn'])))
 # Explicit source choice can alter sovereign finance while GDP remains the same
 # with G/I OFF. Lack of a donor is detected, not silently passed as closed.
 for x,z in zip(cache['GOVERNMENT_FUND_TRANSFER'],cache['NO_HH_DEBIT_SOURCE_UNALLOCATED']):
  checks+=1
  if abs(x['real_GDP_trn']-z['real_GDP_trn'])>5e-7:fails.append(dict(check='GOV_transfer_vs_unallocated_GDP_neutral',year=x['year']))
 # Reuse previous return and payer-share tests; they allowed endogenous HH tax
 # bases and therefore are references, not same-control derivatives here.
 prev=rd(root/PREV/'N3_Sensitivity_Annual_Comparison_2026_2055.csv');ids=['PENSION_RETURN001','PENSION_RETURN003','PENSION_PUBLIC025','PENSION_PUBLIC075'];reused=[dict(x,reference_control='OLD_ENDOGENOUS_HH_TAX_BASES_NOT_FROZEN') for x in prev if x['case'] in ids]
 reused +=[dict(x,reference_control='OLD_MATCHED_BLOCK_OFF_WITH_ENDOGENOUS_HH_TAX') for x in old if x['case']=='NO_PENSION_BLOCK']
 dump(out/'Reused_Return_Payer_And_Pension_OFF_References.csv',reused)
 combined=list(raw)
 for x in reused:
  z=dict(x);y=int(z['year']);z.update(kind='REUSED_DIAGNOSTIC_DIFFERENT_HH_TAX_CONTROL',GDP_minus_initial2026_trn=float(z['real_GDP_trn'])-580.)
  combined.append(z)
 dump(out/'N3_Pension_Counterfactual_Annual_2026_2055.csv',combined);dump(out/'N3_Pension_Counterfactual_Case_Summary.csv',summ);dump(out/'N3_Pension_Counterfactual_Cases.csv',[dict(case=d['case'],kind=d['kind'],return_source=d['return_source'],cohort_mode=d.get('cohort_mode','LEGACY'),new_GDP_production_from_return=0.,adopted=False) for d in cases])
 dump(out/'N3_Pension_Cohort_Benefit_Contribution_Trace.csv',schedule);dump(out/'N3_Pension_Individual_Cohort_Assets.csv',cohorts);dump(out/'N3_Pension_Household_Government_Fund_Annual_Ledger.csv',ledger)
 dump(out/'N3_Pension_Investment_Return_Source_And_Transfers.csv',returns);dump(out/'N3_Pension_Consumption_GDP_Transmission.csv',trans);dump(out/'N3_Pension_Fiscal_Cash_Debt_Ledger.csv',fisc)
 for name,cid in [('Resolved_Pension_Base_Component.py.txt','BASE_REPLAY'),('Resolved_Working_Age_Cohort_Component.py.txt','WORKING_AGE_CONTRIBUTORS_ONLY')]: (out/name).write_text(source_codes[cid])
 unknowns=[dict(item=a,evidence=b,still_unknown=c,classification=d,adopted=False) for a,b,c,d in [
 ('75-age and transition','Original75 principle; candidate2033-2038 ramp;65-entry protection2033;5-year age bins','exact statutory cohorts/rights, mortality and migration by cohort','POLICY_SPEC;DATA'),
 ('Benefit units','80k/150k/250k monthly at40/40/20%; CPI proxy','national pension-system strata, survivor/disability/coverage/price-wage indexation','CALIBRATION;POLICY_SPEC'),
 ('Contribution base','working_age15-64 ×employment70% ×wage4m ×18.3% ×diversion25% ×phase','actual insured contributions, older workers and baseline charges','DATA;CALIBRATION'),
 ('Entry cohort inconsistency','10% of contributions sourced from working-age base allocated to entry ages67/72; no extra older contribution base','correct age weights and eligibility; working-age-only renormalization is candidate, not measured','CODE_BASE_CONSISTENCY;CALIBRATION'),
 ('Return source','2% nominal asset return credited; default debits aggregate HH property income','actual portfolio domestic/external mix, payer, retained/distributed return, owner/beneficiary, taxes','ACCOUNTING;DATA'),
 ('Transfer vs return','explicit government credit has matching government cost but is a grant guarantee, not investment income','legal budget authority and funding responsibility','POLICY_SPEC;AUTHORITY'),
 ('Household asset ownership','fund assets tracked; no second HH contribution charge','HH fund claims/fund liabilities, distribution, loss of liquidity vs total wealth','ACCOUNTING;DATA'),
 ('Government/insurer split','50/50 public pension cost; prior25/75% tests reused','correct sovereign vs insurer responsibility, central/local split and full fiscal consolidation','ACCOUNTING;POLICY_SPEC'),
 ('Consumption structure','MPC.72/domestic.8/lambda.6; HH debit reduces C, funded returns are not new GDP','beneficiary-specific propensities and return incidence, calibrated total/GNI effects','STRUCTURE;CALIBRATION')]]
 dump(out/'N3_Pension_Calibration_Unknowns.csv',unknowns)
 rec=[];paths=[str(p.relative_to(root)) for p in (root/GAP).iterdir() if p.is_file()]+[PREV+'/Sensitivity_Runtime.py',PREV+'/N3_Sensitivity_Pension_Accounts.csv',PREV+'/N3_Sensitivity_Annual_Comparison_2026_2055.csv','handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122/Component_Initialization.json','handoff/chatgpt-n3-model-expansion-20261121/N3_Components.py','handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Components.py','policies/New3linesPolicies.md']
 for path in sorted(set(paths)):
  b=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);assert b==(root/path).read_bytes();rec.append(dict(commit=PIN,path=path,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 req='handoff/chatgpt-n3-pension-path-review-request-20261123/SPE_Work_N3_Pension_Household_Fund_Fiscal_Transmission_Request_20261123.md';b=subprocess.check_output(['git','show',AUTH+':'+req],cwd=root);assert b==(root/req).read_bytes();rec.append(dict(commit=AUTH,path=req,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 write(out/'Input_Source_Receipts.json',rec)
 v=dict(status='PASS_LIMITED_PENSION_PATH_DIAGNOSTICS' if not fails else 'FAIL',executed_paths=5,executed_rows=150,reused_rows=len(reused),delivered_rows=len(combined),checks=checks,failed=len(fails),failures=fails,
 prior_PASS_reused=[13928,32439],source_files_checked=len(rec),HH_labor_financial_tax_realized_wedges_fixed=True,SQ_modified=False,GI=False,
 max_negative_control_unallocated_source_trn=max(x['source_unallocated_trn'] for x in returns if x['case']=='NO_HH_DEBIT_SOURCE_UNALLOCATED'),negative_control_source_closure=False,correct_real_world_return_source_identified=False,national_calibration=False,formal_policy_adopted=False)
 write(out/'Verification.json',v);report(out,v,summ,ledger,trans)
 print(json.dumps(v));assert not fails,fails[:5]

def report(out,v,summ,ledger,trans):
 lines=['# N3年金経路の限定精査','DRAFT / NON-CANONICAL / 2026-11-23',
 '年金の勘定と消費伝播を実行で追跡した。75歳移行・年金給付減、基金払出、基金運用益の国内家計振替が現行GDPへ別々に作用する。正しい運用原資・受益者・全国年金構造は特定できず、源泉を変更した結果を修正確定値とはしない。',
 '制度の実装：原文75歳原則に対し、候補2033開始6年移行、2033年以降65歳に達した層を対象に5歳区分で遅延率を計算し、給付対象率85%を掛ける。給付単価は月8/15/25万円を40/40/20%で加重し共通価格でスライド。これら原文非確定値は既存仮定。受給遅延人数×給付単価を家計給付差B<0、政府/保険者の公的費用へ対応させる。',
 '拠出：15-64歳人口×就業70%×年給与400万円×共通物価×遅行賃金×18.3%×25%×移行率を既存公的制度から基金へ振り替える。家計から同額を二度控除しない。基金は期首資産に名目2%を付利、75歳以降の候補20年払出を行い、その後当年拠出を入れる。新規拠出の当年利息は0。死亡・脱退・相続の資産移転は未接続。',
 'コホート不整合候補：拠出基礎は15-64歳だが、基金新規拠出の8%/2%を入年齢67/72歳へ割り当てている。別の高齢就業拠出基礎がないため基礎と年齢配分が不整合。32/52歳の既存65/25%を90%で再正規化する候補を隔離実行したが、正しい全国年齢分布を取得・採用したものではない。単に高齢拠出を禁止する制度提案ではない。',
 '会計：B=公的給付差、C=拠出振替、F=基金払出、R=基金収益。家計差=B+F−国内家計振替H。政府現金差=−0.5(B+C)−政府保証移転、保険者現金差=−0.5(B+C)、基金資産差=C+R−F。外部支払者差=−外部利払。合計残差=R−H−政府移転−外部支払。既存政府50%は国/地方50%ではない。HH現金残高・基金への家計請求権/基金負債は未計上で、基金資産増をそのまま全国純富増や家計損失としない。',
 '国内家計源泉：既存は基金運用益と同額を家計財産所得から控除し基金へ保持。保存的な国内振替として勘定は対応するが、GDPの一定割合から作る家計資源にその所得が元々含まれるか、基金の帰属/受益者・配当/値上がり益/利息の区別は未確認。二重拠出は検出されない一方、既存家計所得との重複控除が現実に正しいかは未識別。利回り上昇で家計Cが下がるのはこの振替・払出ラグ・消費構造による条件付き結果であり、運用益自体が負の生産効果を持つという推計ではない。',
 '比較ケース：外部支払者利息を基金へ保持する枝は外部→基金の原資を別勘定で示し、家計から控除せず、新GDPを加算しない。政府基金移転枝は収益相当を保証移転として政府費用へ計上し、投資収益と区別する。原資未配賦で家計控除だけ外す枝は負の対照で、基金は収益を受け取るが支払者不明のため源泉閉合PASSではない。政府保証も現実の債券ポートフォリオ/予算権限の存在を確認したものではない。',
 '全新規枝で給与/事業・金融の家計課税基礎・従前税・追加税の年次値を基準に固定。年金側賃金・拠出は内生反応を残し、他の税率・設定は変更しない。旧1%/3%利回り・政府25/75%負担・年金OFFは通常の内生家計課税だったため参考として再利用し、今回の課税固定対照との厳密な効果差へ混ぜない。税年金相互作用+0.269451兆円は元の2×2結果のまま、配賦しない。',
 '|経路|年|GDP−SQ|基準N3との差|基金残高|政府現金|SQ割れ年数|','|---|---:|---:|---:|---:|---:|---:|']
 for z in summ:
  if z['year'] in [2030,2055]:lines.append(f"|{z['case']}|{z['year']}|{z['GDP_minus_SQ_trn']:+.6f}|{z['GDP_delta_vs_base']:+.6f}|{z['pension_fund_end_trn']:.6f}|{z['CL_assets_candidate_trn']:.6f}|{z['SQ_below_years']}|")
 lines+=['金額：GDPは実質兆円、基金/財政は名目兆円。2026年実質580兆円との差は補助列。各年SQ超えを目標比較とし、目標合わせの係数変更はしていない。',
 '基準2055年の実現軌道C状態源泉：公的給付−10.174233、基金払出+0.283110、運用益振替−1.551784兆円を再現。これらは同じ軌道内の平滑化後源泉であり、年金OFFの+11.818289兆円と同じ独立寄与ではない。政府基金移転と原資未配賦枝はGDPが同じでもPB/現金/債務が異なる。追加G/I OFFで政府負担からGDPへ自動帰還する経路がないためで、財政負担が0という意味ではない。',
 f"新規5経路150年次、旧{v['reused_rows']}年次再利用。検証{v['checks']}件・失敗{v['failed']}。個別コホート/基金全体残高、家計/政府/保険者/基金/外部のフロー対称性、原資不明枝の残差検出、二重拠出なし、固定家計課税、GDP算術、追加G/I OFFを検証。負の対照は閉合した制度としてPASSさせていない。",
 '未完了：全国受給者/拠出・給付/年齢・死亡/制度別基礎、実ポートフォリオ、運用益課税・帰属、家計請求権と基金負債、国地方/保険者の正式負担・財源・予算権限、所得分配別消費反応。全国較正後GDPと原文の最終効果はunknown。',
 '再現：`python3 handoff/chatgpt-n3-pension-path-review-20261123/N3_Pension_Path_Reproduce.py --outdir /tmp/n3-pension-replay`。旧原本・政策本文・税率・控除・年金正式制度・共通エンジン・SQは変更なし。正式採用・Acceptance・PR/merge・Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。']
 (out/'SPE_N3_Pension_Path_Review_Report_DRAFT_20261123.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.outdir.resolve())
