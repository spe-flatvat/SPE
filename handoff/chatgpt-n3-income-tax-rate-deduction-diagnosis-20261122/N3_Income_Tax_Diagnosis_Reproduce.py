#!/usr/bin/env python3
"""National income-tax 2x2 diagnostic on fixed SPE exposure; stdlib+git.
Original engine/policies/coefficients untouched. Not a national microsimulation.
"""
import json,csv,math,hashlib,argparse,subprocess,sys,random,re
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(P))
from Tax_Model import RULES,BOUNDARIES,salary_income,basic,spouse,progressive,profile,household,decompose
BURDEN='b552d93d325c3d128b9d8c472b087feda6efe721';BD='handoff/chatgpt-n3-policy-burden-diagnosis-20261122';N3='37c3399f9c553673a79ba1298fc68d758a77055e';ND='handoff/chatgpt-n3-f-parity-implementation-20261122'
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8')))
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def pin(root,commit,path):
 if subprocess.run(['git','cat-file','-e',commit],cwd=root,capture_output=True).returncode:subprocess.run(['git','fetch','origin',commit],cwd=root,check=True)
 b=subprocess.check_output(['git','show',commit+':'+path],cwd=root);a=root/path
 if a.exists():assert b==a.read_bytes(),path
 return dict(commit=commit,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),local_matches_fixed=True if a.exists() else None,route='git show fixedcommit:path')
def run(root,out):
 out.mkdir(parents=True,exist_ok=True);receipts=[]
 for f in ['N3_Annual_Tax_Bridge_2026_2055.csv','N3_Tax_Base_Cell_Reconstruction.csv','N3_Unchanged_Execution_Trace.json','N3_Policy_Burden_Diagnosis_Verification.json','SPE_N3_Policy_Burden_Diagnosis_Report_DRAFT_20261122.md']:
  receipts.append(pin(root,BURDEN,BD+'/'+f))
 for f in ['policies/New3linesPolicies.md',ND+'/Inputs.json',ND+'/Components.py',ND+'/Resolved_Macro_Source.py.txt']:
  receipts.append(pin(root,N3,f))
 receipts.append(pin(root,'ba08c45d4ecb99defecb8416c8d63e0cbfde8cb4','handoff/claude-n3-f-parity-verification-20261122/N3_F_Parity_Independent_Summary_DRAFT_20261122.json'))
 receipts.append(pin(root,'4453f5300e1a6e2320b45c30d4e3767ed9e8b74e','handoff/chatgpt-sq-growth-diagnosis-20261122/SQ_Growth_Contribution_Summary.csv'))
 (out/'Input_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 checks=[]
 def chk(name,error,tol=1e-7):checks.append(dict(check=name,error=error,tolerance=tol,pass_=abs(error)<=tol))
 # Official table/boundary/independent marginal integral checks, not mirror tests.
 for gross,net in [(740999,0),(741000,1000),(1780000,1040000),(2190999,1450999),(2191000,1451000),(2192999,1451000),(2193000,1453000),(2196000,1456000),(2200000,1460000),(2203999,1460000),(2384000,1588800),(3600000,2440000),(6600000,4840000),(8500000,6550000),(10000000,8050000)]:chk('official_salary_table_'+str(gross),salary_income(gross)-net)
 for income,amount in [(4890000,1040000),(4890001,670000),(6550000,670000),(6550001,620000),(23500001,480000),(25000001,0)]:chk('official_basic_boundary_'+str(income),basic(income)-amount)
 chk('official_NTA_7million_example',progressive(7000000)[0]-974000)
 rng=random.Random(20261122)
 for i in range(300):
  value=rng.randrange(0,100000001)//1000*1000;rem=value;prior=0;calc=0.
  for top,rate,unused in RULES['progressive_brackets_yen']:
   piece=rem if top is None else min(rem,top-prior);calc+=max(0,piece)*rate;rem-=max(0,piece)
   if rem<=0:break
   prior=top
  chk('independent_marginal_integral_'+str(i),progressive(value)[0]-calc,1e-6)
 chk('salary_threshold178_noSI',household(1780000,profile('SALARY_SINGLE_SI0'),'A',BOUNDARIES[-1])['total_tax_yen'])
 chk('social_paid_not_abolished',household(5000000,profile('SALARY_SINGLE_SI15'),'D',BOUNDARIES[-1])['social_payment_yen']-750000)
 chk('under16_no_dependent_deduction',household(5000000,profile('SALARY_SPOUSE_CHILD10_SI15'),'A',BOUNDARIES[-1])['dependent_deduction_yen'])
 chk('college_dependent630k',household(5000000,profile('SALARY_SPOUSE_COLLEGE_SI15'),'A',BOUNDARIES[-1])['dependent_deduction_yen']-630000)
 # Representative personal/household computations, no population weights.
 profiles=RULES['profiles_aggregate']+['SALARY_SPOUSE_CHILD10_SI15','SALARY_SPOUSE_CHILD17_SI15','SALARY_SINGLE_CREDIT100K_SI15']
 rep=[];repdecomp=[];incomegrid=[500000,1000000,1780000,2000000,3000000,5000000,8000000,10000000,20000000,50000000,100000000]
 for name in profiles:
  p=profile(name)
  for boundary in BOUNDARIES:
   for income in incomegrid:
    casevals={}
    for case in 'ABCD':
     r=household(income,p,case,boundary,True);casevals[case]=r['total_tax_yen'];a=household(income,p,'A',boundary)
     rep.append(dict(rule_year=2026,profile=name,input_kind='GROSS_SALARY_RECEIPTS' if p['kind']=='SALARY' else 'NET_BUSINESS_PROFIT_AFTER_NECESSARY_EXPENSES_BEFORE_BLUE',input_household_yen=income,boundary=boundary,case=case,**r,tax_change_vs_A_yen=r['total_tax_yen']-a['total_tax_yen'],tax_change_pct=None if a['total_tax_yen']==0 else 100*(r['total_tax_yen']/a['total_tax_yen']-1),effective_change_vs_A_pp=(r['effective_on_gross_pct'] or 0)-(a['effective_on_gross_pct'] or 0),observed_microdata=False,resident_tax_included=False,credit100k_eligibility='HYPOTHETICAL_VALID_INPUT_NOT_HOUSING_ELIGIBILITY_VERIFIED' if p['credit'] else 'NO_APPLICABLE_CREDIT_ASSUMED'))
    dec=decompose(casevals);chk('representative_additive_'+name+boundary+str(income),dec['additive_residual']);chk('representative_symmetric_'+name+boundary+str(income),dec['symmetric_residual']);repdecomp.append(dict(scope='REPRESENTATIVE_NOT_POPULATION',profile=name,boundary=boundary,income_yen=income,**dec))
 dump(out/'N3_Income_Tax_Representative_Households.csv',rep);dump(out/'Representative_2x2_Decomposition.csv',repdecomp)
 # Existing 29 exposure cells: preserve sum of household labor income, vary only explicit conditional profiles.
 old={int(r['year']):r for r in rd(root/BD/'N3_Annual_Tax_Bridge_2026_2055.csv')};cells=rd(root/BD/'N3_Tax_Base_Cell_Reconstruction.csv');byyear={y:[r for r in cells if int(r['year'])==y] for y in range(2026,2056)}
 bridge=[];decs=[];scell=[]
 for name in RULES['profiles_aggregate']:
  p=profile(name)
  for boundary in BOUNDARIES:
   for year in range(2026,2056):
    totals={case:dict(total=0.,ordinary=0.,surtax=0.,income=0.,taxable=0.) for case in 'ABCD'};exposure=0.
    for c in byyear[year]:
     n=float(c['households']);income=float(c['labor_base_trn'])*1e12/n;exposure+=income*n/1e12
     for case in 'ABCD':
      r=household(income,p,case,boundary)
      for key,rkey in [('total','total_tax_yen'),('ordinary','ordinary_tax_yen'),('surtax','surtax_yen'),('income','income_before_personal_deductions_yen'),('taxable','taxable_yen')]:totals[case][key]+=n*r[rkey]/1e12
      if year in [2026,2035,2055] and boundary=='INCLUDING_EARNED_INCOME_DROP_CREDITS':scell.append(dict(year=year,profile=name,case=case,cell=c['cell'],households=n,household_labor_receipts_or_profit_yen=income,tax_trn=n*r['total_tax_yen']/1e12,taxable_trn=n*r['taxable_yen']/1e12,scope='SPE_EXPOSURE_CONDITIONAL_PROFILE_NOT_NATIONAL_ESTIMATE'))
    o=old[year];phase=float(o['phase_flat']);oldbase=float(o['labor_base_trn']);oldbefore=float(o['labor_tax_before_trn']);olddelta=float(o['labor_tax_delta_trn']);chk('same_exposure_'+name+boundary+str(year),exposure-oldbase)
    dd=decompose({k:v['total'] for k,v in totals.items()});do=decompose({k:v['ordinary'] for k,v in totals.items()});chk('aggregate_2x2_'+name+boundary+str(year),dd['additive_residual']);chk('aggregate_symmetric_'+name+boundary+str(year),dd['symmetric_residual'])
    allin=decompose(dict(A=totals['A']['total'],B=totals['B']['ordinary'],C=totals['C']['total'],D=totals['D']['ordinary']));policy_delta=phase*dd['total_D_minus_A'];baseline_gap=phase*(totals['A']['total']-oldbefore);definition_gap=phase*.3*(oldbase-totals['D']['income']);rounding_gap=phase*(.3*totals['D']['income']-totals['D']['ordinary']);surtax_gap=-phase*totals['D']['surtax'];residual=olddelta-policy_delta-baseline_gap-definition_gap-rounding_gap-surtax_gap
    chk('old78_bridge_'+name+boundary+str(year),residual)
    b=dict(year=year,rule_year=2026,law_future_basis='2026_NOMINAL_FREEZE_NOT_ACTUAL_FUTURE_LAW',profile=name,boundary=boundary,exposure_scope='SPE_SYNTHETIC_CONDITIONAL_TOTAL_NOT_NATIONAL_TAX_FORECAST',old_labor_base_trn=oldbase,old_allocated_tax_trn=oldbefore,old_policy_tax_delta_trn=olddelta,phase=phase,new_D_minus_A_policy_trn=policy_delta,A_minus_old_allocated_comparison_trn=baseline_gap,gross_vs_income_definition_trn=definition_gap,taxable_rounding_gap_trn=rounding_gap,supplement_scope_gap_trn=surtax_gap,bridge_residual_trn=residual,household_primary_cash_change_vs_old_trn=olddelta-policy_delta,national_current_tax_total=None,unidentified_joint_distribution=None)
    for case in 'ABCD':
     b[case+'_policy_delta_allin30_vs_A_trn']=phase*((totals[case]['ordinary'] if case in ['B','D'] else totals[case]['total'])-totals['A']['total'])
     b[case+'_tax_ordinary_trn']=totals[case]['ordinary'];b[case+'_supplement_trn']=totals[case]['surtax'];b[case+'_tax_with_supplement_trn']=totals[case]['total'];b[case+'_policy_delta_vs_A_trn']=phase*(totals[case]['total']-totals['A']['total'])
    bridge.append(b)
    if year in [2026,2035,2055]:decs.append(dict(year=year,rule_year=2026,profile=name,boundary=boundary,scope='SPE_CONDITIONAL_EXPOSURE_NOT_NATIONAL_ESTIMATE',**{k+'_trn':v for k,v in dd.items()},**{'ordinary_'+k+'_trn':v for k,v in do.items()},**{'allin30_'+k+'_trn':v for k,v in allin.items()},unidentified_profile_weights=None))
 dump(out/'N3_Income_Tax_2x2_Decomposition.csv',decs);dump(out/'N3_Income_Tax_Existing_Bridge_2026_2055.csv',bridge);dump(out/'Conditional_Cell_Tax_Aggregation.csv',scell)
 macro=macro_bridge(root,out,bridge,checks,chk)
 # Explicit bridge classification: baseline replacement is observable under a profile, its true cause cannot be uniquely allocated.
 mapping=[dict(component='old_delta',status='REPRODUCED',meaning='old0.30*gross minus allocated survey national tax'),dict(component='new_D_minus_A_policy',status='CONDITIONAL_IDENTIFIED',meaning='statutory 2x2 for imposed personal/household profile, common supplement scope'),dict(component='A_minus_old_allocated',status='NOT_IDENTIFIED_CAUSAL_SPLIT',meaning='joint effect of method, deduction data, household-to-individual split, other income, taxpayer coverage; not all calibration error'),dict(component='gross_vs_income_definition',status='CONDITIONAL_IDENTIFIED',meaning='salary/blue income calculation preserved under PERSONAL_ONLY versus old gross taxable basis'),dict(component='supplement_scope',status='IDENTIFIED_SCOPE_DIFFERENCE_UNDECIDED_POLICY',meaning='old N3 30% vs ordinary30% plus current2.1% surcharge; N3 treatment not adopted'),dict(component='taxable_rounding',status='IDENTIFIED',meaning='per-person taxable floor1000 yen vs continuous SPE bases'),dict(component='method/deductions/earner shares/time',status='NOT_IDENTIFIED_SEPARATELY',meaning='no observed joint taxpayer data; no fabricated causal allocation of baseline gap')]
 dump(out/'Bridge_Definition_Classification.csv',mapping)
 for f in receipts:
  file=root/f['path']
  if file.exists():chk('source_unchanged:'+f['path'],0 if hashlib.sha256(file.read_bytes()).hexdigest()==f['sha256'] else 1,0.)
 failed=[c for c in checks if not c['pass_']];result=dict(status='PASS_CONDITIONAL_DIAGNOSTIC' if not failed else 'FAIL',checks=len(checks),failed=len(failed),failures=failed,checks_detail=checks,request_commit='4d2925415082617f86c7050a75ccfadf56cded9d',input_commit=BURDEN,official_rule_date='2026-04-01; annual2026 applied December1',national_calibration_pass=False,independent_AI_review=False,limits=['No observed joint taxpayer distribution','National totals not identified: only SPE exposure conditional scenarios','2026 nominal rules frozen after2026, no forecast of sunset/indexing','Resident tax and other taxes excluded','Supplement applicability to N3 undecided','Macro is fixed-exposure partial C/GDP recurrence, not full N3 reexecution'])
 (out/'N3_Income_Tax_Diagnosis_Verification.json').write_text(json.dumps(result,indent=2)+'\n');assert not failed,failed[:5]
 report(out,bridge,decs,rep,macro,result)
 print('INCOME_TAX_DIAGNOSIS_PASS',len(checks),'checks','representative_rows',len(rep),'annual_bridges',len(bridge))

def macro_bridge(root,out,bridge,checks,chk):
 trace=json.loads((root/BD/'N3_Unchanged_Execution_Trace.json').read_text());p=trace['parameters']['PARITY_CONNECTED_CANDIDATE'];base={t['year']:t for t in trace['records'] if t['case']=='PARITY_CONNECTED_CANDIDATE'}
 outputs=[];keys=list(dict.fromkeys((b['profile'],b['boundary']) for b in bridge));idx={(b['profile'],b['boundary'],b['year']):b for b in bridge}
 for name,boundary in keys:
  for case in 'ABCD':
   for scope in ['COMMON_SUPPLEMENT','N3_30_ALL_IN']:
    dC=dy=0.;tax=base[2026]['tax'];prevNom=base[2026]['N'];forcing=[];coefficient=1-p['lambda_C']+p['lambda_C']*p['domestic_share']*p['generic_mpc']*p['income_feedback']
    for year in range(2026,2056):
     t=base[year];b=idx[name,boundary,year];newtax=b[case+('_policy_delta_vs_A_trn' if scope=='COMMON_SUPPLEMENT' else '_policy_delta_allin30_vs_A_trn')];saved=b['old_policy_tax_delta_trn']-newtax;extra_feedback=p['income_feedback']*dy*t['coreD'];target=p['domestic_share']*p['generic_mpc']*(saved+extra_feedback)/t['coreD']
     if year>2026:dC=(1-p['lambda_C'])*dC+p['lambda_C']*target
     newY=min(t['desired']+dC,t['capacity']);dy=newY-t['Y'];newN=newY*t['coreD'];cash=t['cash']+saved;newFeedback=t['feedback']+extra_feedback
     if year>2026:tax=min(tax*(1+(newN/prevNom-1)*p['elasticity'])*(.9 if year==2031 else 1.),newN*.3)
     direct=t['direct']-saved
     outputs.append(dict(year=year,profile=name,boundary=boundary,case=case,supplement_scope=scope,old_N3_GDP_trn=t['Y'],diagnostic_GDP_trn=newY,GDP_difference_from_old_trn=dy,new_labor_tax_policy_delta_trn=newtax,static_household_cash_difference_trn=saved,extra_income_feedback_nominal_trn=extra_feedback,diagnostic_consumption_difference_real_trn=dC,diagnostic_macro_cash_change_trn=cash,diagnostic_resource_DI_trn=p['household_income_share']*t['coreN']+cash+newFeedback,diagnostic_tax_proxy_trn=tax+direct,diagnostic_unmet_demand_trn=max(0,t['desired']+dC-t['capacity']),method='FROZEN_EXPOSURE_OTHER_CHANNELS_FIXED_C_AND_LAGGED_GDP_FEEDBACK_RECURRENCE',full_N3_model_reexecuted=False,core_labor_investment_pension_wages_KPI_recomputed=False,original_engine_changed=False,government_recycling=False,national_fiscal=None))
     if year>2026:forcing.append(p['lambda_C']*p['domestic_share']*p['generic_mpc']*saved/t['coreD'])
     independent_C=sum(x*coefficient**(len(forcing)-1-j) for j,x in enumerate(forcing))
     if all(r['diagnostic_unmet_demand_trn']==0 for r in outputs[-len(forcing):]) if forcing else True:chk('independent_closed_form_C_'+name+boundary+case+scope+str(year),dC-independent_C,1e-7)
     prevNom=newN
 # Null replacement reproduces existing GDP without a fitted coefficient.
 dC=dy=0.
 for y in range(2026,2056):
  t=base[y];target=p['domestic_share']*p['generic_mpc']*(0+p['income_feedback']*dy*t['coreD'])/t['coreD']
  if y>2026:dC=(1-p['lambda_C'])*dC+p['lambda_C']*target
  dy=min(t['desired']+dC,t['capacity'])-t['Y'];chk('old_tax_nochange_control_'+str(y),dy)
 dump(out/'N3_Income_Tax_Partial_Macro_Sensitivity.csv',outputs);return outputs

def report(out,bridge,decs,rep,macro,result):
 boundary='INCLUDING_EARNED_INCOME_DROP_CREDITS';name='SALARY_SINGLE_SI15'
 chosen=[d for d in decs if d['year']==2035 and d['boundary']==boundary]
 b=next(x for x in bridge if x['profile']==name and x['boundary']==boundary and x['year']==2035)
 d=next(x for x in chosen if x['profile']==name)
 text=['# N3所得税率変更・控除撤廃の負担増加寄与診断',
 'DRAFT / NON-CANONICAL / 診断実行済み。政策採用・全国税収推計の認定ではない。',
 '固定依頼書: `4d2925415082617f86c7050a75ccfadf56cded9d`。既存N3実装・税負担診断・Claude独立検算・SQ診断を再利用した。政策本文、既存係数、共通エンジンは変更していない。RP-023／M19–25 HOLD、RP-024 PENDINGを維持する。',
 '## 結論',
 '2035年の既存差分+78.142892兆円は、給与・事業の合成所得基礎312.484949兆円×30%から、旧所得税15.602593兆円を控除した値である。旧側の約4.99%は法定累進税率から計算した実効税率ではなく、既存調査税額を配賦した合成比較値である。このため+78.143兆円をそのまま「税率変更の寄与」と読むことはできない。',
 '同一のSPE所得29セルへ法定計算を適用し、税率・控除・交互作用を識別した。ただし個人別所得、稼得者数、控除・他所得の結合分布がないため、日本全体での唯一の寄与額は未識別である。以下は全世帯へ各属性を仮置きした条件別の計算であり、平均世帯・中心推計・信頼区間ではない。',
 '## 制度・比較の定義',
 '国税庁の2026年改正資料・税額表を確認。2026年分年税額に適用される12月1日施行ルールを使用する。基礎控除は合計所得489万円以下104万円、給与所得控除の最低額74万円。月次源泉徴収額とは区別する。住民税は含まない。2027年以降は2026年の名目ルールを凍結した診断であり、既知の2028年特例終了・将来の物価連動を反映した制度予測ではない。',
 'A=現行税率＋現行控除、B=30%＋現行控除、C=現行税率＋控除撤廃、D=30%＋控除撤廃。主表では比較範囲をそろえて全ケースへ復興特別所得税相当2.1%を加える（B/Dは実効30.63%）。30%を付加税込みと解する別列・年次波及も保存した。N3の付加税の正式扱いは未裁定。',
 '控除撤廃を①所得控除のみ（給与所得計算・青色申告特別控除を維持）、②給与所得控除・所得金額調整控除・青色申告特別控除も含む、に分け、税額控除維持／廃止を交差させた。事業必要経費はどのケースでも存続。事業入力は必要経費控除後・青色控除前の利益であり、売上ではない。',
 '税率寄与=B−A、控除寄与=C−A、交互作用=D−B−C＋A。順序に依存しない対称寄与は各単独寄与に交互作用の半分を加える。',
 '## 2035年条件別2×2（兆円）',
 '| 全世帯へ仮置きする属性 | A | B | C | D | D−A | 対称税率寄与 | 対称控除寄与 |',
 '|---|---:|---:|---:|---:|---:|---:|---:|']
 for x in chosen:
  vals=[x[k+'_trn'] for k in ['A','B','C','D','total_D_minus_A','symmetric_rate','symmetric_deduction']]
  text.append('| '+x['profile']+' | '+' | '.join(f'{v:.6f}' for v in vals)+' |')
 text+=['給与所得控除等も撤廃・共通付加税の条件。SI15は支払社会保険料を所得の15%と仮置きする感度条件であり、実際の保険料率ではない。保険料の支払い自体は控除廃止後も続く。単独稼得、配偶者無収入＋大学生扶養、夫婦均等稼得で差が生じる。事業は青色65万円適格／なしを分けた。所得税は個人課税のため、世帯所得一定でも稼得者配分を変えるとAが大きく変わる。',
 '単身給与・SI15の単独寄与は、税率{:.6f}、控除{:.6f}、交互作用{:.6f}兆円。合計{:.6f}兆円。交互作用は30%課税により撤廃控除の価値も変化することを表す。'.format(d['rate_B_minus_A_trn'],d['deduction_C_minus_A_trn'],d['interaction_trn'],d['total_D_minus_A_trn']),
 '## 旧+78.143兆円との橋渡し',
 '| 構成（単身給与・SI15、2035） | 兆円 |','|---|---:|']
 for label,key in [('新D−A','new_D_minus_A_policy_trn'),('法定Aと旧配賦税の比較差','A_minus_old_allocated_comparison_trn'),('旧総額基礎とD所得計算の定義差','gross_vs_income_definition_trn'),('個人課税標準丸め差','taxable_rounding_gap_trn'),('旧30%との付加税範囲差','supplement_scope_gap_trn'),('以上の合計＝旧差分','old_policy_tax_delta_trn'),('橋渡し残差','bridge_residual_trn')]:text.append('| '+label+' | '+f'{b[key]:.9f}'+' |')
 text+=['法定Aと旧配賦税の差は、計算法・控除・個人分割・他所得・課税対象者範囲等の結合差である。これをすべて「較正誤り」や「控除の効果」と認定できない。未識別項目は空欄と分類CSVに残した。計算ミスとして断定できる算術不整合は今回の検証範囲で検出しなかった。',
 '## 所得階層・世帯別',
 '代表表は年50万〜1億円の11点、9属性、4撤廃境界、4税制を収録。給与は額面給与、事業は必要経費後利益を分母とし、総所得／課税所得分母の負担率も併記。有限差分限界税率は所得+1万円の差であり、控除段階差による飛びを含む。既存SPE29セルは観測個票ではない。',
 '| 単身給与SI15・年収 | A年税額(円) | B | C | D | D−A(円) | A負担率% | D負担率% |', '|---|---:|---:|---:|---:|---:|---:|---:|']
 for income in [1780000,3000000,5000000,10000000,50000000,100000000]:
  z={r['case']:r for r in rep if r['profile']==name and r['boundary']==boundary and r['input_household_yen']==income}
  text.append('| '+str(income)+' | '+' | '.join(str(int(z[c]['total_tax_yen'])) for c in 'ABCD')+' | '+str(int(z['D']['tax_change_vs_A_yen']))+' | '+f"{z['A']['effective_on_gross_pct']:.3f} | {z['D']['effective_on_gross_pct']:.3f} |")
 text+=['給与所得控除等も撤廃したDでは、低所得者にも給与総額のほぼ30.63%がかかる。高所得帯ではAの累進実効税率がDを超え、D−Aが負になる場合がある。扶養控除・配偶者控除は低中所得帯、給与所得控除は課税所得基礎、青色控除は事業利益の比較に影響する。税額控除の適格性を全国分布で把握できないため、10万円適格入力の代表感度例以外は適用なしとした。住宅ローン控除等の適格性の認定ではない。',
 '## 2026〜2055年と部分的なGDP波及',
 '年次CSVは30年×6属性×4境界=720行。旧税基礎・導入率を固定してA/B/C/Dを再計算。部分マクロCSVはさらに4ケース×付加税2解釈=5760行。税差の置換→家計現金→消費の漸進調整→需要GDP→翌年所得フィードバックを既存係数のまま接続した。投資・労働・賃金・年金・供給能力・他政策は旧経路を固定し、政府還流・財政閉合は追加していない。完全なN3モデルの再実行ではなく、税効果の条件付き部分感度である。',
 '| 年 | 旧労働税差 | 新D−A | 家計現金の旧比改善 | GDP旧比差（共通付加税） | GDP旧比差（30%付加税込み） |', '|---|---:|---:|---:|---:|---:|']
 for year in [2026,2035,2055]:
  z=next(x for x in bridge if x['year']==year and x['profile']==name and x['boundary']==boundary)
  mm={x['supplement_scope']:x for x in macro if x['year']==year and x['profile']==name and x['boundary']==boundary and x['case']=='D'}
  vals=[z['old_policy_tax_delta_trn'],z['new_D_minus_A_policy_trn'],z['household_primary_cash_change_vs_old_trn'],mm['COMMON_SUPPLEMENT']['GDP_difference_from_old_trn'],mm['N3_30_ALL_IN']['GDP_difference_from_old_trn']]
  text.append('| '+str(year)+' | '+' | '.join(f'{v:.6f}' for v in vals)+' |')
 text+=['GDP差は旧N3比でありSQ比ではない。家計現金は名目兆円、GDPは既存基準の実質兆円。単身給与SI15を説明用に表示したもので採用ケースではない。全国個票・全チャネルを欠くため、N3税率の適否や全国GDPの一点予測は結論していない。',
 '## 検証・成果',
 f"実行検証 {result['checks']}件、失敗{result['failed']}件。公的税額例、給与所得表と控除境界、別式による累進税の積分照合、2×2加算・対称寄与、旧差分との橋渡し、消費漸化式の閉形式照合、税差無変更対照、固定原本SHA-256・既存コード不変を検証した。これは独立AIレビューや全国較正PASSではない。",
 '制度確認の取得先・適用時期・省略範囲は `N3_Income_Tax_Official_Source_Register.md`。入力固定Commitと実バイト記録は `Input_Source_Receipts.json`。実行コードは `Tax_Model.py`、`Tax_Rules_2026.json`、`N3_Income_Tax_Diagnosis_Reproduce.py`。主要表は依頼名対応の2×2、代表世帯、既存橋渡しCSV、追加の条件別セル・部分マクロCSV。検証詳細はJSON。',
 '再現: リポジトリルートから `python3 handoff/chatgpt-n3-income-tax-rate-deduction-diagnosis-20261122/N3_Income_Tax_Diagnosis_Reproduce.py --root . --outdir /tmp/n3-tax-reproduction`。Python標準ライブラリとgit、固定入力オブジェクトを利用。実行時の固定原本照合を省略しない。',
 '未解決: 全控除の政策上の範囲、N3付加税、個人別他所得・控除・稼得者の結合分布、既存所得セルと法定所得の対応、将来法改正と名目分布の変化、事業適格性・税額控除、他税目・社会保険、完全動学での投資・労働・財政反応。いずれも正式採用・係数調整は行っていない。']
 (out/'SPE_N3_Income_Tax_Rate_Deduction_Diagnosis_Report_DRAFT_20261122.md').write_text(re.sub(r'(?<=\|)\n\n(?=\|)', '\n', '\n\n'.join(text))+'\n')
 artifacts=[]
 for f in sorted(out.iterdir()):
  if f.is_file() and f.name not in ['N3_Income_Tax_Diagnosis_Verification.json','Execution.log']:
   v=f.read_bytes();artifacts.append(dict(path=f.name,size=len(v),sha256=hashlib.sha256(v).hexdigest()))
 result['artifacts']=artifacts
 (out/'N3_Income_Tax_Diagnosis_Verification.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--outdir',type=Path,required=True);z=a.parse_args();run(z.root.resolve(),z.outdir.resolve())
