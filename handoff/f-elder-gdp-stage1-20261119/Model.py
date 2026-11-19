#!/usr/bin/env python3
"""DRAFT/NON-CANONICAL. python3 Model.py Inputs.json --outdir replay
Standard library; fixed dependencies embedded; no edits to original models.
"""
import argparse,base64,builtins,copy,csv,hashlib,json,math,zlib
from pathlib import Path

def close(a,b):return math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10)
def dump(p,rows):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows({k:format(v,'.12g') if isinstance(v,float) else v for k,v in r.items()} for r in rows)
def dependency(c):
 src=zlib.decompress(base64.b64decode(c['previous_model_zlib_base64']));assert hashlib.sha256(src).hexdigest()==c['previous_model_sha']
 ns={'__name__':'previous_labor_functions'};exec(compile(src,'previous_labor.py','exec'),ns)
 dep=ns['dependency'](c['previous_inputs']);captured={}
 def cap(src,filename,mode):captured['source']=src;return builtins.compile(src,filename,mode)
 dep['compile']=cap;dep['tx_engine'](c['previous_inputs']['base'],True);source=captured['source']
 def sub(a,b):
  nonlocal source
  assert source.count(a)==1,a[:100];source=source.replace(a,b)
 sub('\n    for y in range(2026,2056):','\n    labor_anchor=labor;nonlabor_factor=1.;coreY_anchor=coreY\n    for y in range(2026,2056):')
 sub("            extra_workers=value(p['elderly_additional_workers'])*phase(y,2028) if enabled and not halt else 0.","            extra_workers=c['_elder'][i]['effective_extra'] if enabled and not halt else 0.")
 sub("            coreY*=1+growth;coreN*=1+growth+inflation;coreD=coreN/coreY", "            if spec['_link']=='LEVEL':\n                nonlabor_factor*=1+p['base_growth']-risk\n                next_coreY=coreY_anchor*nonlabor_factor*(labor/labor_anchor)**p['labor_response']\n                growth=next_coreY/coreY-1;coreY=next_coreY\n            else:coreY*=1+growth\n            coreN*=1+growth+inflation;coreD=coreN/coreY")
 sub("        elderly_subsidy=None if p['elderly_additional_workers'] is None or p['elderly_subsidy_per_worker_man'] is None else p['elderly_additional_workers']*phase(y,2028)*p['elderly_subsidy_per_worker_man']/1e8 if i else 0.","        ei=1. if spec['_elder']=='LEGACY' else coreD/(600/580)\n        elderly_subsidy=c['_elder'][i]['subsidy_base_trn']*ei")
 sub("        pension=None if p['elderly_additional_workers'] is None or p['pension_relief_per_worker_man'] is None else p['elderly_additional_workers']*phase(y,2028)*p['pension_relief_per_worker_man']/1e8 if i else 0.","        pension=c['_elder'][i]['pension_support_base_trn']*ei")
 sub("        admin_firm=value(admin_saving)+value(elderly_subsidy)","        admin_firm=value(admin_saving)+value(elderly_subsidy)-c['_elder'][i]['employer_contribution_base_trn']*ei")
 sub("        cash=f['household']-reclassified+ss['household']+med['household']+value(pension)","        cash=f['household']-reclassified+ss['household']+med['household']+value(pension)-c['_elder'][i]['employee_contribution_base_trn']*ei")
 ns2={'__name__':'elder_patched_TX'};exec(compile(source,'elder_patched_TX.py','exec'),ns2);return ns,dep,ns2

def native_counts(c,y):
 prev=c['previous_inputs'];b=prev['base'];ref=b['population_reference'][str(y)];r25=b['population_reference']['2025'];obs=b['official_initial_2025_oct'];df=obs['foreign']-r25['foreign'];dp=obs['population']-r25['population']
 wa=ref['japanese_working_age']+obs['working_age']-r25['working_age']-df*(r25['working_age']-r25['japanese_working_age'])/r25['foreign']
 el=ref['japanese_elderly']+obs['elderly']-r25['elderly']-df*(r25['elderly']-r25['japanese_elderly'])/r25['foreign']
 return ref['japanese']+dp-df,wa,el

def elder_ledger(c,s,prev):
 cfg=c['parameters'];out=[];last_extra=0.
 for y in range(2026,2056):
  raw=prev['age_rates'](c['previous_inputs'],y);J,wa,elder=native_counts(c,y);den=sum(sum(v) for a,v in raw.items() if int(a)>=65)
  pools=[]
  for age,v in raw.items():
   age=int(age)
   if age<65:continue
   for sex in [0,1]:
    pop=v[sex]/den*elder;r=prev['employment_rate'](c['previous_inputs'],age,sex)
    pools.append(dict(age=age,sex=sex,population=pop,rate=r,pool=pop*(1-r)))
  SQelder=sum(z['population']*z['rate'] for z in pools);phase=0. if y<cfg['start_year'] else min(1.,(y-cfg['start_year']+1)/cfg['ramp_years']);mode=s['elder'];added=eff=covered=po_count=ps_count=overlap=0.;male=female=0.;rates=[]
  if s['policy']=='F' and mode!='NONE' and phase:
   if mode=='LEGACY':
    added=200000.*phase;eff=added
    for z in pools:
     e=added*z['pool']/sum(x['pool'] for x in pools)
     covered+=e if z['age']<70 else 0.;male+=e if z['sex']==0 else 0.;female+=e if z['sex']==1 else 0.;rates.append(z['rate']+e/z['population'])
   else:
    cover,comp=(.25,.4) if mode=='LOW' else (.75,.8) if mode=='HIGH' else (cfg['coverage'],cfg['compliance'])
    for z in pools:
     grp='65_69' if z['age']<70 else '70_74' if z['age']<75 else '75plus'
     po=cover*comp*cfg['conversion_by_age'][grp]*phase
     ps=cover*cfg['subsidy_hiring_response']*cfg['subsidy_per_extra_job_yen']/cfg['extra_worker_annual_wage_yen']*phase
     if s.get('channel')=='OBLIGATION_ONLY':ps=0.
     if s.get('channel')=='SUBSIDY_ONLY':po=0.
     prob=1-(1-po)*(1-ps);e=z['pool']*prob;assert 0<=prob<=1
     po_count+=z['pool']*po;ps_count+=z['pool']*ps;overlap+=z['pool']*po*ps
     added+=e;covered+=e if z['age']<70 else 0.;male+=e if z['sex']==0 else 0.;female+=e if z['sex']==1 else 0.;rates.append(z['rate']+(1-z['rate'])*prob)
    eff=added*s.get('weight',cfg['extra_job_effective_labor_weight'])
  assert close(added,male+female) and added<=sum(z['pool'] for z in pools)+1e-7
  if mode!='LEGACY':assert close(added,po_count+ps_count-overlap)
  if not rates:rates=[z['rate'] for z in pools]
  age_output={}
  for group,lo,hi in [('65_69',65,69),('70_74',70,74),('75plus',75,110)]:
   for sex,label in [(0,'male'),(1,'female')]:
    cells=[(j,z) for j,z in enumerate(pools) if lo<=z['age']<=hi and z['sex']==sex];pop=sum(z['population'] for _,z in cells);baseE=sum(z['population']*z['rate'] for _,z in cells);newE=sum(z['population']*rates[j] for j,z in cells)
    age_output.update({group+'_'+label+'_population':pop,group+'_'+label+'_SQ_rate':baseE/pop,group+'_'+label+'_F_rate':newE/pop,group+'_'+label+'_extra_jobs':newE-baseE})
  hires=max(added-last_extra*(1-cfg['job_turnover_rate']),0.) if mode!='LEGACY' else added
  subsidy=hires*cfg['subsidy_per_extra_job_yen']/1e12
  support=added*cfg['pension_support_per_extra_job_yen']/1e12
  contributions=0. if mode=='LEGACY' else covered*cfg['pension_coverage_fraction_65_69']*cfg['extra_worker_annual_wage_yen']*cfg['pension_contribution_rate']/1e12
  out.append(dict(year=y,SQ_elder_employed=SQelder,SQ_elder_population=elder,F_extra_jobs=added,F_extra_male=male,F_extra_female=female,F_elder_employed=SQelder+added,F_elder_employment_rate=(SQelder+added)/elder,effective_extra=eff,obligation_jobs=po_count,subsidy_response_jobs=ps_count,overlap_jobs=overlap,hire_flow=hires,subsidy_base_trn=subsidy,pension_support_base_trn=support,employee_contribution_base_trn=contributions*(1-cfg['employer_share']),employer_contribution_base_trn=contributions*cfg['employer_share'],insurer_receipt_base_trn=contributions,pension_future_entitlement=None,pension_withholding=None,pension_full_balance=None,max_age_sex_rate=max(rates),**age_output))
  last_extra=added
 return out

def calculate(c,s,prev,dep,engine):
 pc=c['previous_inputs'];d,_=prev['labor_trajectory'](pc,dict(id=s['id'],policy=s['policy'],mode='COMMON'),dep)
 common,_=prev['labor_trajectory'](pc,dict(id='SQ',policy='SQ',mode='COMMON'),dep);ed=elder_ledger(c,s,prev)
 unit=s.get('labor_unit_scale',1.)
 for t in d:t['effective_productive_workers']*=unit
 for t in common:t['effective_productive_workers']*=unit
 for t in ed:t['effective_extra']*=unit
 tx=copy.deepcopy(pc['base']['tx_inputs']);tx['_trajectory']=d;tx['_common_trajectory']=common;tx['_elder']=ed
 tx['initial'].update(population=d[0]['population'],births=d[0]['births_calendar'],deaths=d[0]['deaths_calendar']);tx['common_model']['slack']=s.get('slack',.02)
 # Remove the inherited fixed-worker and fixed-finance mechanisms before replacing them.
 tx['policy_inputs']['elderly_additional_workers']=0.
 spec=dict(id=s['id'],policy=s['policy'],profile='TEXT_ASSUMPTIONS',supply_cap=s.get('cap',True),_link=s['link'],_elder=s['elder'],migration_override=dict(foreign_initial_stock=d[0]['foreign'],enforcement_mode='NONE_REFERENCE'))
 r=engine['run_path'](tx,spec);return r,d,ed

def run(inp,out):
 b=Path(inp).read_bytes();c=json.loads(b);prev,dep,engine=dependency(c);paths={};ds={};es={};annual=[];summary=[]
 for s in c['cases']:
  r,d,e=calculate(c,s,prev,dep,engine);paths[s['id']]=r;ds[s['id']]=d;es[s['id']]=e
 for s in c['cases']:
  r=paths[s['id']];d=ds[s['id']];e=es[s['id']];g=s['link'];sq=paths['A10_SQ' if g=='LEVEL' else 'A00_SQ'];no,_,_=calculate(c,{**s,'id':'matched_no_elder','policy':'F','elder':'NONE'},prev,dep,engine);rows=[]
  for i,(x,t,z) in enumerate(zip(r,d,e)):
   y=x['year'];ei=1. if s['elder']=='LEGACY' else x['common_deflator']/(600/580);legacy='POLICY_HIST_'+s['policy'];old=next(q for q in c['previous_reference'] if q['case']==legacy and int(q['year'])==y)
   L=t['effective_productive_workers']+z['effective_extra'];E=t['domestic_employed_conditional']+z['F_extra_jobs']+t['foreign_employed_conditional'];L0=d[0]['effective_productive_workers']
   row=dict(case=s['id'],year=y,policy=s['policy'],GDP_link=g,elder_condition=s['elder'],population=t['population'],foreign=t['foreign'],foreign_net_flow=t['foreign_net_migration'],foreign_employed=t['foreign_employed_conditional'],domestic_employed_baseline=t['domestic_employed_conditional'],domestic_employed=t['domestic_employed_conditional']+z['F_extra_jobs'],total_employed=E,effective_labor=L,effective_labor_anchor=L0,real_GDP_anchor=580.,nominal_GDP_anchor=600.,anchor_real_GDP_per_effective_worker_yen=580e12/L0,anchor_nominal_GDP_per_total_employed_yen=600e12/(d[0]['domestic_employed_conditional']+d[0]['foreign_employed_conditional']),labor_elasticity=.65,core_real_per_effective_worker_yen=x['core_real_gdp_trn']*1e12/L,total_real_GDP_per_employed_yen=x['real_gdp_trn']*1e12/E,extra_wages_diagnostic_nominal_trn=z['F_extra_jobs']*c['parameters']['extra_worker_annual_wage_yen']/1e12*ei,**{k:v for k,v in z.items() if k!='year'})
   for k in ['real_gdp_trn','nominal_gdp_trn','core_real_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn','funding_gap_proxy_trn','household_disposable_nominal_trn','I_policy_real_trn','capital_total_real_trn','nominal_wage_proxy_man','real_wage_proxy_man','unmet_demand_real','supply_binding']:row[k]=x[k]
   row.update(subsidy_nominal_trn=z['subsidy_base_trn']*ei,pension_support_nominal_trn=z['pension_support_base_trn']*ei,employee_contribution_nominal_trn=z['employee_contribution_base_trn']*ei,employer_contribution_nominal_trn=z['employer_contribution_base_trn']*ei,insurer_receipt_nominal_trn=z['insurer_receipt_base_trn']*ei,pension_related_known_subtotal_trn=(z['insurer_receipt_base_trn']-z['pension_support_base_trn'])*ei,delta_GDP_vs_previous=x['real_gdp_trn']-float(old['real_gdp_trn']),delta_GDP_vs_SQ=x['real_gdp_trn']-sq[i]['real_gdp_trn'],elder_GDP_vs_zero=x['real_gdp_trn']-no[i]['real_gdp_trn'] if s['policy']=='F' else 0.,elder_core_GDP_vs_zero=x['core_real_gdp_trn']-no[i]['core_real_gdp_trn'] if s['policy']=='F' else 0.)
   assert close(x['labor_force_population_proxy'],L)
   if z['F_extra_jobs']>0:assert x['core_real_gdp_trn']>=no[i]['core_real_gdp_trn']-1e-8
   assert not x['circuit_halted'],'Circuit requires employment ledger synchronisation'
   assert close(row['employee_contribution_nominal_trn']+row['employer_contribution_nominal_trn'],row['insurer_receipt_nominal_trn'])
   if s['id'] in ['A00_SQ','A00_F']:
    for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn']:assert math.isclose(x[k],float(old[k]),rel_tol=5e-11,abs_tol=1e-7)
   assert close(row['domestic_employed']-row['domestic_employed_baseline'],row['F_extra_jobs']) and row['max_age_sex_rate']<=1
   if s['policy']=='SQ':assert close(z['F_extra_jobs'],0.) and close(z['subsidy_base_trn'],0.)
   rows.append(row)
  annual+=rows;u={k:rows[-1][k] for k in ['case','GDP_link','elder_condition','domestic_employed','SQ_elder_employed','F_elder_employed','F_extra_jobs','F_extra_male','F_extra_female','effective_extra','hire_flow','effective_labor','core_real_per_effective_worker_yen','real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','subsidy_nominal_trn','pension_support_nominal_trn','insurer_receipt_nominal_trn','pension_related_known_subtotal_trn','delta_GDP_vs_previous','delta_GDP_vs_SQ','elder_GDP_vs_zero','elder_core_GDP_vs_zero']}
  u['binding_years']=sum(v['supply_binding'] for v in rows);u['cum_subsidy_nominal_trn']=sum(v['subsidy_nominal_trn'] for v in rows);summary.append(u)
 # Difference-in-differences separates effect of replacing elder scheme under old/new GDP links.
 inter=[]
 for i in range(30):
  get=lambda name,k:paths[name][i][k]
  a=get('A00_F','real_gdp_trn');g=get('A10_F','real_gdp_trn');e=get('A01_F','real_gdp_trn');both=get('A11_F','real_gdp_trn')
  inter.append(dict(year=2026+i,old_F=a,GDP_link_only=g-a,elder_replacement_only=e-a,combined=both-a,interaction=both-g-e+a,obligation_subsidy_GDP_interaction=get('A11_F','real_gdp_trn')-get('OBLIGATION_ONLY_F','real_gdp_trn')-get('SUBSIDY_ONLY_F','real_gdp_trn')+get('NONE_LEVEL_F','real_gdp_trn')))
  d00=a-get('A00_SQ','real_gdp_trn');d10=g-get('A10_SQ','real_gdp_trn');d01=e-get('A01_SQ','real_gdp_trn');d11=both-get('A11_SQ','real_gdp_trn')
  inter[-1].update(old_F_minus_SQ=d00,new_F_minus_SQ=d11,policy_GDP_link_only=d10-d00,policy_elder_replacement_only=d01-d00,policy_combined=d11-d00,policy_interaction=d11-d10-d01+d00)
  assert close(inter[-1]['combined'],inter[-1]['GDP_link_only']+inter[-1]['elder_replacement_only']+inter[-1]['interaction'])
 # A permanent common unit rescaling must leave GDP unchanged under fixedGDP anchoring.
 test={**next(s for s in c['cases'] if s['id']=='A11_F'),'labor_unit_scale':1.07}
 scaled,_,_=calculate(c,test,prev,dep,engine)
 assert all(close(x['real_gdp_trn'],y['real_gdp_trn']) for x,y in zip(scaled,paths['A11_F']))
 pprev=c['previous_inputs'];sd,_=prev['labor_trajectory'](pprev,dict(id='x',policy='SQ',mode='COMMON'),dep)
 assert all(close(x['foreign'],ds['A00_SQ'][i]['foreign']) for i,x in enumerate(sd))
 out=Path(out);out.mkdir(parents=True,exist_ok=True);dump(out/'Annual.csv',annual);dump(out/'Comparison.csv',summary);dump(out/'Interactions.csv',inter)
 (out/'Report.md').write_text(report(c,annual,summary,inter),encoding='utf-8');assert b==Path(inp).read_bytes()
 print(json.dumps(dict(cases=len(paths),annual_rows=len(annual),previous_reference_cells=180,population_and_foreign_inputs_unchanged=True,employment_and_finance_identities='PASS',factorial_decomposition='PASS')))

def report(c,annual,comparison,inter):
 S={r['case']:r for r in comparison};f=lambda v,n=3:'未算定' if v is None else f'{v:,.{n}f}'
 def at(n,y):return next(r for r in annual if r['case']==n and r['year']==y)
 L=['# SPE F段階的改善 第1弾：高齢者就業・GDP接続','',
 '2026-11-19 / DRAFT / NON-CANONICAL。政策原文・main・既存固定成果は変更しない。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。正式Acceptance・Freeze・Canonical化は行わない。','',
 '## 今回何が変わったか','',
 '固定20万人を人口の年齢男女別の非就業者プールに対する政策転換率へ置き換え、国内就業者と65歳以上就業率へ明示的に反映した。準義務化の適用範囲・履行率、採用補助の反応を区別し、重なる対象を一回だけ数える。補助金は追加就業ストック全員への毎年給付から、採用・補充フローへの比較仮定へ変更した。保険料・支援支出・将来給付の未算定部分を分離した。GDPは初期アンカーを維持しつつ労働弾性0.65を水準比へ厳密適用する参照方式を実装し、旧方式との2×2比較・相互作用を生成した。','',
 '## 固定参照・原文・既存検算','',
 '基準はCommit `47deeee23621d2b6804351ef9131b6dbde51ffda`の労働・外国人材モデル。Claude検算Commit `cdd6feaccf87eae80436b2cac265a3d0cc243d4f`のレポートをGitHubから取得・読取し、旧38経路の算術一致を旧条件で再利用した。今回の改良版が独立検証PASSという意味ではない。旧版の労働成長率と固定GDPアンカーの説明は算術不具合ではないという既存評価を維持する。','',
 '政策本文・AnnexはGitHubのCommit `5804388482864af08204ba0d0e76a46206dacdbd`から直接取得。本文は「高齢者就業促進（準義務化＋採用企業補助金）」と年金制度改善を記載するが、義務化率・対象年齢の上限・補助金単価・就業増人数・効果係数は明記しない。実施年表は2028〜2032年を含む。比較上の発動は従来と同じ2028開始・2030満額を維持した暫定設定で、原文の確定年次仕様ではない。','',
 '現行政府でも65歳まで雇用確保の義務、70歳まで就業確保の努力義務がある。Fで初めて高齢者就業対策が生まれるとは扱わず、2025実績就業率を用いたSQとの差分である。ただし政府施策の将来普及・率上昇を推定していないため、固定SQ率に対する比較という制約は残る。','',
 '## 就業促進の計算','',
 '基準就業率は前版の2025年・男女9年齢区分。社人研日本人5歳男女人口の補間・既存人口勘定への再集約も維持する。外国人人口・就業経路、915.4万円参照係数・人件費800万円・税率・投資教育式等は固定。今回追加就業の対象は日本人65歳以上の比較とし、外国人高齢者の政策増分は対象外（F原文が国籍限定を定めたという意味ではない）。','',
 '年齢性別セルのSQ率r、人口Pについて、準義務化側p_o=適用範囲×履行率×年齢別就業転換率×ランプ、補助側p_s=適用範囲×補助反応係数×(採用補助金／年間賃金仮定)×ランプ。F率=r+(1−r)×[1−(1−p_o)(1−p_s)]、追加人数=P×(F率−r)。p_o+p_sをそのまま加算せず、重複p_o p_sを控除する。性別は基準率・人口の違いとして反映し、政策効果の男女別実証係数は未取得。','',
 '|感度|適用範囲|履行率|年齢別非就業者転換係数65〜69／70〜74／75+|','|---|---:|---:|---|','|LOW|25%|40%|10%／6%／2%|','|MEDIUM|50%|60%|10%／6%／2%|','|HIGH|75%|80%|10%／6%／2%|','',
 '共通の補助反応係数0.20、採用補助10万円、追加就業者の年間賃金200万円、追加就業者1人の実効投入0.5（基準平均就業者単位）も全て暫定仮定。政策効果の推計・正式採用値ではない。就業人数は頭数、実効投入は平均就業者換算であって、0.5を測定済みFTEとしない。実効投入0.25／1の感度も計算。','',
 '採用人数=max[当年追加就業者−前年追加就業者×(1−離職率10%),0]、補助金=採用人数×10万円。離職率は未較正。追加就業者の実際の職歴・再雇用・給付資格を追うモデルではなく、採用フロー支出の一次近似である。比較用LEGACYは従来どおり20万人×ランプ・毎年10万円・毎年年金支援5万円を再現し、旧値との違いを混同しない。NONEは高齢者追加策ゼロの対照で、既存の高齢者就業ゼロではない。','',
 '## GDP接続とアンカー','',
 '従来式：Y_core,t=Y_core,t−1×[1+g_nonlabor,t+0.65×(L_t/L_t−1−1)]、g_nonlabor=基礎成長1%−既存リスク。基準年580兆円を固定するため、就業者データを増やしても初期の1人当たり生産性が下がり、将来労働比の変化によってGDPが低下することがある。この性質を計算バグとしない。','',
 '改善参照式：Y_core,t=580×Π(1+g_nonlabor,s)×(L_t/L_2026)^0.65。弾性0.65・基礎成長・リスクを維持し、有限の労働水準比を厳密に反映する。労働変化と非労働成長を加算近似する旧式から乗法へ分離した仕様差であり、推定済みの生産関数ではない。既存の資本・教育・消費等の波及式は継続。初期GDPを引き上げる変更ではない。','',
 '両方式とも2026年のGDP580兆／600兆と、同じ基準年就業者・実効投入を使用し、GDP／就業者の労働生産性とGDP／実効投入を別々に出力する。外国人915.4万円は相対重みの参照係数で、基準年全体の生産性や追加高齢者の生産性そのものではない。初期全就業者は約6,796.6万人、名目GDP／頭数は約882.8万円。実効投入の単位変更に対しアンカー分母も変更され、GDPが不変となることを検査した。','',
 'データの水準修正と政策による追加就業は異なる。就業人数のみを一律に増やしてGDP初期値まで自動的に上げると、観測・設計GDPを別の値へ改定することになるため今回は行わない。改良方式でも同じ固定GDPアンカーを用いる点は合理的な部分として維持し、追加就業は2028以降にSQ比のL増として入る。政策追加就業が2026分母に入って相殺される処理はしない。','',
 '## 2×2比較：2055年','',
 '|ケース|GDP接続|高齢者策|SQ実質GDP兆円|F実質GDP兆円|F−SQ兆円|F追加就業人|実効追加人相当|','|---|---|---|---:|---:|---:|---:|---:|']
 for name,sq in [('A00_F','A00_SQ'),('A10_F','A10_SQ'),('A01_F','A01_SQ'),('A11_F','A11_SQ')]:
  r=S[name];q=S[sq];L.append('|'+name+'|'+r['GDP_link']+'|'+r['elder_condition']+'|'+'|'.join([f(q['real_gdp_trn']),f(r['real_gdp_trn']),f(r['delta_GDP_vs_SQ']),f(r['F_extra_jobs'],0),f(r['effective_extra'],0)])+'|')
 L+=['','### 高齢者施策のゼロ追加策対照との差・財政関連（2055年）','','|条件・GDP接続|追加人数|高齢就業者合計万人|GDP寄与兆円|CORE供給側寄与兆円|採用補助兆円|年金支援兆円|保険料収入兆円|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for n in ['A10_F','LOW_LEVEL_F','A11_F','HIGH_LEVEL_F','HOURS25_F','HOURS100_F']:
  r=S[n];L.append('|'+n+'|'+'|'.join([f(r['F_extra_jobs'],0),f(r['F_elder_employed']/1e4),f(r['elder_GDP_vs_zero']),f(r['elder_core_GDP_vs_zero']),f(r['subsidy_nominal_trn'],6),f(r['pension_support_nominal_trn'],6),f(r['insurer_receipt_nominal_trn'],6)])+'|')
 L+=['','追加人数の増加がGDP寄与を必ず比例的に増やすわけではない。実効投入係数、年金拠出による家計・企業資金の移転、補助金フロー、消費投資調整、供給上限が介在する。置換による増減（MEDIUM−旧20万人）と、施策そのものの寄与（MEDIUM−追加策NONE）を区別する。','',
 '### 年次主要点','','|年|SQ高齢就業万人|F追加就業人|F高齢就業万人|F国内就業万人|F実質GDP兆円|F税収診断兆円|','|---|---:|---:|---:|---:|---:|---:|']
 for y in [2030,2035,2038,2045,2055]:
  r=at('A11_F',y);L.append('|'+str(y)+'|'+'|'.join([f(r['SQ_elder_employed']/1e4),f(r['F_extra_jobs'],0),f(r['F_elder_employed']/1e4),f(r['domestic_employed']/1e4),f(r['real_gdp_trn']),f(r['tax_diagnostic_trn'])])+'|')
 L+=['','## 単独・複合・相互作用','',
 '2×2の変更差は旧Fを起点にし、相互作用=両改善−GDP接続のみ−高齢者策のみ＋旧F。F−SQの政策差についても同じ差分を別に計算し、GDP接続による共通基準変化を政策改善と混同しない。Interactions.csvは30年全てを保存。','',
 '|2055年変更差|F水準差兆円|F−SQ差の変化兆円|','|---|---:|---:|']
 r=inter[-1]
 for label,key in [('GDP接続のみ','GDP_link_only'),('高齢者策置換のみ','elder_replacement_only'),('相互作用','interaction'),('両改善合計','combined')]:L.append('|'+label+'|'+f(r[key],6)+'|'+f(r['policy_'+key],6)+'|')
 L+=['','準義務化のみ・補助のみ・両方・高齢者追加策ゼロでもGDP差を分解した。非就業者プールの重なりを明示控除し、その後のマクロ相互作用は別に扱う。2055年の準義務化×補助のGDP相互作用は'+f(r['obligation_subsidy_GDP_interaction'],6)+'兆円。加法的な政策効果の実証値ではない。','',
 '## 補助金・家計・企業・年金勘定','',
 '改良策は旧20万人の供給加算と旧20万人分の支出を先に無効化し、新勘定を一度だけ入れる。採用補助は政府歳出→企業資金、年金支援5万円／追加就業者／年は暫定の政府支出→家計支援として継承。実際の在職老齢年金の支給停止・将来給付増額を推定した金額ではない。','',
 '保険料は追加就業者のうち65〜69歳×加入割合50%×賃金仮定200万円×18.3%。事業主・本人折半を企業資金と家計可処分所得から一回ずつ控除し、合計を保険者収入として表示する。原則70歳以上には新たな厚生年金保険料を賦課しない。標準報酬上限、個別適用・任意加入の例外、本人受給額と給与分布を再現した計算ではない。税収診断に保険料を加算しない。','',
 '年金関連既知小計=保険料収入−年金支援は、政府・保険者を跨ぐ部分勘定の参考であり年金収支全体ではない。在職老齢年金の支給停止・将来の権利増額・年金フル収支・行政執行費は未算定（空欄）。追加賃金総額は診断表示のみとし、GDPにより生じる所得へ二重加算しない。改良策の金額は2026年価格の仮定から共通デフレーターで名目化、LEGACYは従来の固定名目支出をそのまま再現する。','',
 '## 供給制約による減衰','','|ケース|拘束年数|2055GDP兆円|追加策ゼロ比GDP兆円|','|---|---:|---:|---:|']
 for n in ['A11_F','SLACK5_BOTH_F','UNCAPPED_BOTH_F','UNCAPPED_OLD_ELDER_F','UNCAPPED_NONE_F']:
  r=S[n];L.append('|'+n+'|'+str(r['binding_years'])+'|'+f(r['real_gdp_trn'])+'|'+f(r['elder_GDP_vs_zero'])+'|')
 L+=['','上限なしは感度診断であり正式予測ではない。上限ありの追加策効果と、上限なしで同じ追加策ゼロ対照を用いた効果を比較する。各経路の追加策ゼロ対照は、slack・上限有無を同じにして計算した。','',
 '## 出典・再現・検証と残る制約','',
 '- 政策原本：本文[固定版](https://github.com/spe-flatvat/SPE/blob/5804388482864af08204ba0d0e76a46206dacdbd/policies/FreedomPolicies.md)、Annex同Commit。',
 '- 就業率・人口：前版Inputs.jsonの総務省労働力調査2025年表Ⅰ-4、社人研1-9a・1-9A(J)。元のURL・ダウンロードSHAは今回Inputs.jsonのprevious_inputs.sourcesへ保持。',
 '- 政府高齢者制度：[厚労省概要](https://www.mhlw.go.jp/content/11700000/001245647.pdf)、[Q&A](https://www.mhlw.go.jp/content/11700000/001245651.pdf)（2025-03-31改訂、2025-04-01適用）。65歳雇用確保義務と70歳就業確保努力義務を確認。',
 '- 保険料：[日本年金機構](https://www.nenkin.go.jp/service/kounen/hokenryo/hoshu/20150515-01.html)の18.3%・折半、[2026年在職老齢年金改正](https://www.nenkin.go.jp/tokusetsu/zairoukaisei.html)（更新2026-04-01）の65万円基準と70歳以上の扱いを確認。今回その個別給付計算は実装していない。資料取得日2026-11-19、ページ初出日未確認は未確認のまま扱う。','',
 f"{len(comparison)}経路×30年={len(annual)}行。旧A00 F／SQのGDP・名目GDP・税収計180セルは元CSV有効桁の範囲で再現。就業率0〜1・追加人数上限・性別合計、準義務化と補助の重複控除、GDP・税収・資本の元エンジン内検査、保険料の家計＋企業＝保険者、2×2相互作用分解を確認。外国人経路・人口・VA参照係数を固定。実効投入単位を一律1.07倍に変えても改善GDPが不変となる反証試験を実施。再実行によるAnnual・Comparison・Interactions・Reportの実バイト一致を確認した。",'',
 '残る未較正は、F準義務化の法的対象・適用範囲・履行率・就業転換率、補助の雇用反応、離職補充率、追加就業者の賃金・時間・生産性、年金加入割合・給付調整・将来権利・執行費、政府施策の将来普及である。固定SQ就業率は今後の政府対策効果を含む予測ではない。外国人政策数量・人口の自然動態残差・915.4万円の国籍固有妥当性・既存財政部分勘定等の未解決も今回の範囲外として維持する。算術整合と経済的妥当性・政策効果の実証は区別する。','',
 '```bash','python3 Model.py Inputs.json --outdir replay','```','',
 '標準ライブラリのみ・オフライン実行可能。不変の旧モデルを入力へ埋込み、限定的な就業・財政・GDP接続ブロックだけを置換する。埋込元SHA・置換対象の一意性を検査する。新規正式レビュー工程は設けない。']
 return '\n'.join(L)+'\n'

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('--outdir',required=True);a=p.parse_args();run(a.inputs,a.outdir)
