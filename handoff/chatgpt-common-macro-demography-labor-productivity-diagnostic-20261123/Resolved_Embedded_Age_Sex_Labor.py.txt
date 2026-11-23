#!/usr/bin/env python3
"""DRAFT/NON-CANONICAL. Calibrated age-sex employment; separate cost and VA.
python3 Model.py Inputs.json --outdir replay (standard library only)
"""
import argparse,base64,copy,csv,hashlib,json,math,zlib
from pathlib import Path

def close(a,b):return math.isclose(a,b,abs_tol=1e-6,rel_tol=1e-10)
def csvout(path,rows):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows({k:format(v,'.11g') if isinstance(v,float) else v for k,v in r.items()} for r in rows)
def dependency(c):
 src=zlib.decompress(base64.b64decode(c['prior_model_zlib_base64']));assert hashlib.sha256(src).hexdigest()==c['prior_model_sha']
 ns={'__name__':'fixed_demography_dependency'};exec(compile(src,'fixed_demography.py','exec'),ns);return ns

def age_rates(c,y,foreign=False):
 lo=(y//5)*5;hi=min(lo+5,2055);f=(y-lo)/5 if hi>lo else 0.
 def profiles(key):
  d=c[key];return {age:[(1-f)*d[str(lo)][age][sex]+f*d[str(hi)][age][sex] for sex in [0,1]] for age in d[str(lo)]}
 jp=profiles('age_japanese_five_year');tot=profiles('age_all_five_year')
 return {age:[tot[age][sex]-jp[age][sex] for sex in [0,1]] for age in jp} if foreign else jp

def employment_rate(c,age,sex,factor=1.):
 if age<15:return 0.
 ix=0 if age<25 else 1 if age<35 else 2 if age<45 else 3 if age<55 else 4 if age<60 else 5 if age<65 else 6 if age<70 else 7 if age<75 else 8
 return min(1.,c['employment_rates_2025']['male' if sex==0 else 'female'][ix]*factor)

def labor_trajectory(c,s,dep):
 b=copy.deepcopy(c['base']);stage=s.get('stage','VA');d=dep['demography'](b,s)
 q=8000000. if stage in ['OLD','DOM','FOREIGN'] else s.get('productivity_yen',c['parameters']['foreign_VA_per_employed_2026_yen'])
 dq=9000000. if stage in ['OLD','DOM','FOREIGN'] else c['parameters']['domestic_VA_reference_2026_yen']
 for t in d:
  y=t['year'];pr=b['population_reference'][str(y)];r25=b['population_reference']['2025'];obs=b['official_initial_2025_oct']
  df=obs['foreign']-r25['foreign'];waoff=obs['working_age']-r25['working_age']-df*(r25['working_age']-r25['japanese_working_age'])/r25['foreign'];eoff=obs['elderly']-r25['elderly']-df*(r25['elderly']-r25['japanese_elderly'])/r25['foreign']
  jpwa=pr['japanese_working_age']+waoff;jpel=pr['japanese_elderly']+eoff
  targets=[t['japanese']-jpwa-jpel,jpwa,jpel]
  raw=age_rates(c,y);group=lambda age:0 if age<15 else 1 if age<65 else 2
  denomin=[sum(v[sex] for a,v in raw.items() for sex in [0,1] if group(int(a))==g) for g in [0,1,2]]
  em=[0.,0.]
  for age,v in raw.items():
   g=group(int(age))
   for sex in [0,1]:em[sex]+=v[sex]/denomin[g]*targets[g]*employment_rate(c,int(age),sex)
  rawf=age_rates(c,y,True);den=sum(sum(v) for v in rawf.values());ef=[0.,0.];factor=s.get('employment_factor',c['parameters']['foreign_employment_factor'])
  for age,v in rawf.items():
   assert min(v)>=0
   for sex in [0,1]:ef[sex]+=v[sex]/den*t['foreign']*employment_rate(c,int(age),sex,factor)
  if stage!='OLD':t['domestic_employed_conditional']=sum(em)
  if stage not in ['OLD','DOM']:t['foreign_employed_conditional']=sum(ef)
  t['domestic_employed_male_calibrated']=em[0];t['domestic_employed_female_calibrated']=em[1]
  t['foreign_employed_male_age_reference']=ef[0];t['foreign_employed_female_age_reference']=ef[1]
  t['effective_productive_workers']=t['domestic_employed_conditional']+t['foreign_employed_conditional']*q/dq
  assert 0<=t['domestic_employed_conditional']<=t['japanese'] and 0<=t['foreign_employed_conditional']<=t['foreign']
 return d,q

def calculate(c,s,dep,engine):
 d,q=labor_trajectory(c,s,dep);commonmode=s['mode'] if s['mode'] in ['LATEST','IPSS'] else 'COMMON'
 cs={**s,'policy':'SQ','mode':commonmode};common,_=labor_trajectory(c,cs,dep)
 b=copy.deepcopy(c['base']);tx=b['tx_inputs'];tx['_trajectory']=d;tx['_common_trajectory']=common;tx['initial'].update(population=d[0]['population'],births=d[0]['births_calendar'],deaths=d[0]['deaths_calendar']);tx['common_model']['slack']=s.get('slack',.02)
 spec=dict(id=s['id'],policy=s['policy'],profile='TEXT_ASSUMPTIONS',supply_cap=True,medical_mode=s.get('medical_mode','UNALLOCATED_COMPAT'),migration_override=dict(foreign_initial_stock=d[0]['foreign'],enforcement_mode='NONE_REFERENCE'))
 return engine['run_path'](tx,spec),d,q

def run(inp,out):
 raw=Path(inp).read_bytes();c=json.loads(raw);dep=dependency(c);engine=dep['tx_engine'](c['base'],True);paths={};trajectories={};annual=[];summ=[]
 for s in c['cases']:
  r,d,q=calculate(c,s,dep,engine);paths[s['id']]=r;trajectories[s['id']]=d
  sqspec={**s,'id':'matchedSQ','policy':'SQ','mode':s['mode'] if s['mode'] in ['LATEST','IPSS'] else 'COMMON'}
  sq,sd,_=calculate(c,sqspec,dep,engine);fref,_,_=calculate(c,{**sqspec,'id':'matchedF','policy':'F'},dep,engine)
  rows=[];source2035=False
  for i,(x,t) in enumerate(zip(r,d)):
   y=t['year'];cost=s.get('cost_yen',c['parameters']['cost_per_foreign_employed_2026_yen']);D=x['common_deflator']/(600/580);F=t['foreign'];E=t['foreign_employed_conditional'];pop=t['population'];active=s['policy']=='F' and y>=2030
   # Source places evaluation in2035. An annual reference is output separately; neither changes unquantified cap.
   if y==2035:source2035=active and pop<1e8
   oldcase=('SQ_LATEST' if s['mode']=='LATEST' else 'SQ_IPSS' if s['mode']=='IPSS' else 'SQ_COMMON') if s['policy']=='SQ' else ('F_COMMON_LATEST' if s['mode']=='LATEST' else 'F_IPSS' if s['mode']=='IPSS' else 'F_'+s['mode'] if s['mode'].startswith('STOCK') else 'F_BAND'+str(int(s.get('band_target',.04)*100)) if s['mode']=='BAND' else 'F_SAME_FLOW')
   old=next(z for z in c['old_results'] if z['case']==oldcase and int(z['year'])==y)
   nr=dict(case=s['id'],year=y,policy=s['policy'],quantity_condition=s['mode'],stage=s.get('stage','VA'),population=pop,japanese=t['japanese'],foreign=F,population_ratio=F/pop,foreign_stock_net_increase=0. if i==0 else F-d[i-1]['foreign'],foreign_net_migration=t['foreign_net_migration'],foreign_reference_residual=t['foreign_nonmigration_reference_residual'],population_reference_bridge=t['population_reference_bridge'],domestic_employed=t['domestic_employed_conditional'],foreign_employed=E,domestic_employed_male=None if s.get('stage')=='OLD' else t['domestic_employed_male_calibrated'],domestic_employed_female=None if s.get('stage')=='OLD' else t['domestic_employed_female_calibrated'],foreign_employed_male=None if s.get('stage') in ['OLD','DOM'] else t['foreign_employed_male_age_reference'],foreign_employed_female=None if s.get('stage') in ['OLD','DOM'] else t['foreign_employed_female_age_reference'],foreign_employment_fraction=E/F,effective_workers=t['effective_productive_workers'],foreign_cost_per_worker_2026_yen=cost,foreign_VA_per_worker_2026_yen=q,foreign_cost_nominal_trn=E*cost/1e12*D,foreign_VA_attribution_nominal_trn=E*q/1e12*D,foreign_cost_real_2026_trn=E*cost/1e12,foreign_VA_real_2026_trn=E*q/1e12,foreign_cost_GDP_ratio=E*cost/1e12*D/x['nominal_gdp_trn'],foreign_VA_GDP_ratio=E*q/1e12*D/x['nominal_gdp_trn'],pop_reach3=int(F/pop>=.03),pop_reach5=int(F/pop>=.05),pop_exceed5=int(F/pop>.05),cost_exceed5=int(E*cost/1e12*D/x['nominal_gdp_trn']>.05),VA_exceed5=int(E*q/1e12*D/x['nominal_gdp_trn']>.05),F_package_active=int(active),F_N4_required=int(active),F_screening_health_conduct_flag=int(active),F_integration_dispersion_flag=int(active),SQ_ikusei_in_force=int(y>=2027),SQ_SSW1_stock_ceiling_reference=805700 if y<=2028 else None,SQ_ikusei_stock_ceiling_reference=426200 if 2027<=y<=2028 else None,official_total_net_migration_forecast=None,F_N4_quantity_effect_identified=None,F_GDP5_auto_stop=0,F_population5_auto_stop=0,F_source2035_relaxation_trigger=int(source2035),F_source2035_cap_multiplier=1.2 if source2035 else 1.,F_annual_population_relaxation_monitor=int(active and pop<1e8),F_annual_reference_cap_multiplier=1.2 if active and pop<1e8 else 1.,F_base_admission_cap=None,F_effective_admission_cap=None,identified_foreign_policy_GDP_effect=None)
   for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn','funding_gap_proxy_trn','nominal_wage_proxy_man','real_wage_proxy_man','household_disposable_nominal_trn','household_consumption_real_proxy_trn','I_policy_real_trn','capital_total_real_trn','supply_binding','unmet_demand_real','medical_insurer_vat','medical_extra_premium','medical_public_topup','medical_internal','medical_unallocated']:nr[k]=x[k]
   nr.update(delta_GDP_vs_matched_SQ=x['real_gdp_trn']-sq[i]['real_gdp_trn'],delta_population_vs_matched_SQ=pop-sd[i]['population'],delta_foreign_employed_vs_SQ=E-sd[i]['foreign_employed_conditional'],F_other_channels_GDP=fref[i]['real_gdp_trn']-sq[i]['real_gdp_trn'],F_quantity_condition_GDP=x['real_gdp_trn']-fref[i]['real_gdp_trn'] if s['policy']=='F' else 0.,delta_GDP_vs_previous=x['real_gdp_trn']-float(old['real_gdp_trn']),previous_comparison_case=oldcase,delta_population_vs_previous=pop-float(old['population']),delta_tax_vs_previous=x['tax_diagnostic_trn']-float(old['tax_diagnostic_trn']))
   if s['policy']=='F':assert close(nr['delta_GDP_vs_matched_SQ'],nr['F_other_channels_GDP']+nr['F_quantity_condition_GDP'])
   if s.get('stage')=='OLD':
    assert math.isclose(x['real_gdp_trn'],float(old['real_gdp_trn']),rel_tol=5e-11,abs_tol=1e-7)
   if i:
    assert close(pop-d[i-1]['population'],t['births_calendar']-t['deaths_calendar']+t['foreign_net_migration']+t['population_reference_bridge'])
    assert close(F-d[i-1]['foreign'],t['foreign_net_migration']+t['foreign_nonmigration_reference_residual'])
   assert close(nr['foreign_cost_nominal_trn']/nr['foreign_VA_attribution_nominal_trn'],cost/q)
   rows.append(nr)
  annual+=rows;last=rows[-1];u={k:last[k] for k in ['case','quantity_condition','stage','population','japanese','foreign','population_ratio','domestic_employed','foreign_employed','foreign_cost_nominal_trn','foreign_VA_attribution_nominal_trn','foreign_cost_GDP_ratio','foreign_VA_GDP_ratio','real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','delta_GDP_vs_matched_SQ','F_other_channels_GDP','F_quantity_condition_GDP','delta_GDP_vs_previous']}
  for key,threshold in [('population_ratio',.03),('population_ratio5',.05),('foreign_cost_GDP_ratio',.05),('foreign_VA_GDP_ratio',.05)]:
   k='population_ratio' if key=='population_ratio5' else key
   u[key+'_reach']=next((z['year'] for z in rows if z[k]>=threshold),None);u[key+'_exceed']=next((z['year'] for z in rows if z[k]>threshold),None)
  u['binding_years']=sum(z['supply_binding'] for z in rows);u['first_F_annual_relaxation_monitor']=next((z['year'] for z in rows if z['F_annual_population_relaxation_monitor']),None);summ.append(u)
  if s.get('stage')!='OLD':
   assert all(close(z['domestic_employed'],z['domestic_employed_male']+z['domestic_employed_female']) for z in rows)
  if s.get('stage') not in ['OLD','DOM']:
   assert all(close(z['foreign_employed'],z['foreign_employed_male']+z['foreign_employed_female']) for z in rows)
 # Meaningful falsification:changing cost cannot change GDP;cost is notVA nor a macroaddend.
 for s in c['cases']:
  if s['id'].startswith('COST'):
   assert all(close(x['real_gdp_trn'],y['real_gdp_trn']) for x,y in zip(paths[s['id']],paths['F_STOCK400']))
 for pol in ['SQ','F']:
  assert all(close(x['population'],y['population']) for x,y in zip(trajectories['POLICY_HIST_'+pol],trajectories['VA_'+pol]))
 z1,_,_=calculate(c,dict(id='zeroVA1',policy='F',mode='COMMON',productivity_yen=0.),dep,engine);z2,_,_=calculate(c,dict(id='zeroVA2',policy='F',mode='STOCK400',productivity_yen=0.),dep,engine)
 assert all(close(a['real_gdp_trn'],b['real_gdp_trn']) for a,b in zip(z1,z2))
 out=Path(out);out.mkdir(parents=True,exist_ok=True);csvout(out/'Annual.csv',annual);csvout(out/'Summary.csv',summ)
 (out/'Report.md').write_text(report(c,annual,summ),encoding='utf-8');assert Path(inp).read_bytes()==raw
 print(json.dumps(dict(cases=len(paths),annual_rows=len(annual),old_selected_regression='90GDP cells PASS',stock_flow='PASS',employment_bounds='PASS',cost_GDP_falsification='PASS',input_unchanged=True)))

def report(c,annual,summary):
 S={r['case']:r for r in summary};f=lambda x,n=3:'未算定' if x is None else f'{x:,.{n}f}'
 def at(name,y):return next(r for r in annual if r['case']==name and r['year']==y)
 L=['# SPE 労働供給・外国人材経済寄与 F／StatusQuo比較','',
 '2026-11-19 / DRAFT / NON-CANONICAL。政策確定・標準係数の正式採用ではない。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。','',
 '## 今回の改善と読み方','',
 '国内就業者を2025年の年齢・男女別就業率へ較正し、社人研の日本人5歳階級・男女人口へ接続した。外国人は全住民×0.7から年齢・男女構成を明示した条件付き就業率へ分離した。800万円を人件費仮定へ移し、付加価値は別の全国SNA参照係数と感度値で計算する。人口比3〜5%、人件費比5%、付加価値比5%は再評価表示のみで自動停止しない。','',
 '政府制度を確認したが、政府が2055年までの全資格の国際純移動を公表した事実は確認できない。したがって「政府制度条件＋実績平均外挿」「政府制度条件＋最新実績外挿」「政府制度条件＋社人研参照」の3つのSQを並列に計算した。Fも同じ数量条件で制度条件を付す3経路を保持し、N4等から根拠なく人数を削減しない。数量感度（30／35／40万人・比率3／4／5%）は政策によって実現すると推定したものではない。POLICY_HISTを便宜上表の共通比較条件とするが、政府の確定将来経路や唯一の代表Fを意味しない。','',
 '## 国内労働供給の較正','',
 '総務省労働力調査2025年平均表Ⅰ-4の就業率を使用。男女別の15〜24、25〜34、35〜44、45〜54、55〜59、60〜64、65〜69、70〜74、75歳以上の9区分。15歳未満は0。例えば65歳以上の集計就業率は26.0%で旧20%より高いが、65〜69歳54.5%、70〜74歳36.2%、75歳以上12.6%と差がある。将来の高齢者内構成の変化もGDPへ効くため、単に.2を.26へ変える処理ではない。','',
 '社人研1-9A(J)の2025・2030〜2055年の日本人男女5歳人口を線形補間。5歳区分に該当する10歳就業率を割り当て、2025実績差を反映した既存人口勘定の日本人15〜64歳・65歳以上人数へ区分内比例再調整する。外国人の細分構成は同一社人研総人口表1-9aと日本人表の差から得る。出生死亡・国籍異動の未分離残差は前版を維持し、新しい死亡・帰化を捏造しない。','',
 '較正した率は全国・全住民の就業率で、日本人だけの率や外国人だけの率を直接推定したものではない。男女年齢の構成較正は実施したが、国籍別率は未取得。将来率固定は外挿仮定で、就業率の政府目標へ強制的に合わせない。外国人に適用する全国率への倍率0.85／1／1.15は条件付き感度であり、N4不合格率や政策効果ではない。1を超える就業確率は1へ抑える。全住民割合から年齢別就業率へ変えたことで、加齢による就業者割合の変化を明示できる。','',
 '|2055年・同じ純移動条件|旧年齢簡略式GDP兆円|国内のみ較正GDP兆円|変化兆円|旧国内就業万人|較正国内就業万人|','|---|---:|---:|---:|---:|---:|']
 for pol in ['SQ','F']:
  o=S['OLD_'+pol];n=S['DOM_'+pol];L.append('|'+pol+'|'+'|'.join([f(o['real_gdp_trn']),f(n['real_gdp_trn']),f(n['real_gdp_trn']-o['real_gdp_trn']),f(o['domestic_employed']/1e4),f(n['domestic_employed']/1e4)])+'|')
 o=S['OLD_F400'];n=S['DOM_F400'];L.append('|F・年40万純増|'+ '|'.join([f(o['real_gdp_trn']),f(n['real_gdp_trn']),f(n['real_gdp_trn']-o['real_gdp_trn']),f(o['domestic_employed']/1e4),f(n['domestic_employed']/1e4)])+'|')
 L+=['','上表は国内就業式だけを変えた逐次対照。外国人就業と付加価値係数は旧値のままなので、国内較正の影響を他の変更から分離している。初期GDPは既存設計値580兆・600兆へ固定し、就業人数の水準にGDPを数値合わせしていない。','',
 '2025年の社人研総人口に今回の全国男女年齢別率を適用した就業者は68,031,652.825人。実績68,280,000人との差−248,347人（約−0.36%）は、人口基準・10月人口と年平均の差を含む。強制的に一致させる水準補正は行っていない。2026年の国内＋外国人条件付き就業者は旧65,839,300人に対し改良67,965,671人となる。', '',
 '## 人件費・付加価値・追加GDP','',
 '推計人件費=外国人就業者×800万円（2026年価格相当）×共通デフレーター変化。800万円はOwnerの比較仮定で、実測平均賃金ではない。推計付加価値は別係数915.400381万円を参照し、600／1,200万円も計算。参照値は2024暦年SNA名目GDP634.226兆円／同SNA就業者6,928.4万人から導出した全国平均であり、外国人固有の実証係数ではない。2024年価格の数値をモデル2026年初期価格へ据え置く係数1という暫定仮定で、観測された価格変換ではない（国籍別係数・価格変換は未較正）。給与は人件費全体と異なり、人件費は付加価値と異なる。外国人雇用実態調査の月額292.4千円等を800万円や付加価値に置換していない。','',
 '付加価値係数は既存マクロの実効労働の相対重みとして一回だけ使用。人件費・診断付加価値総額はGDPへ加算しない。人件費400／600／800／1,000万円の違いでGDPが変わらないことを反証確認した。これは人件費の経済影響がゼロという実証結果ではなく、賃金コスト→雇用・企業需要の追加反応式を今回は持たないためである。総付加価値寄与は既存GDP内の条件付き按分で、F−SQの追加GDPはマクロ経路差として別に計算する。','',
 '|経路2055年|外国人就業万人|人件費総額兆円|VA診断按分兆円|人件費／GDP|VA／GDP|人件費5%超年|VA5%超年|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for name in ['POLICY_HIST_SQ','POLICY_HIST_F','F_STOCK400','F_BAND4','COST4_F','COST6_F','COST10_F']:
  r=S[name];L.append('|'+name+'|'+'|'.join([f(r['foreign_employed']/1e4),f(r['foreign_cost_nominal_trn']),f(r['foreign_VA_attribution_nominal_trn']),f(r['foreign_cost_GDP_ratio']*100)+'%',f(r['foreign_VA_GDP_ratio']*100)+'%',str(r['foreign_cost_GDP_ratio_exceed'] or 'なし'),str(r['foreign_VA_GDP_ratio_exceed'] or 'なし')])+'|')
 L+=['','5%の正式指標は未確定。人口比の3%到達・5%到達・5%超過、人件費比・VA比の到達と超過は別々にSummaryへ保存し、初年既に該当する場合2026とする。原文Annexの「GDP比5%以内上限」と今回Ownerの「再評価基準・自動停止なし」は異なる。政策原文は変更せず、Policy_Comparison.mdと入力へこの運用差を記録する。','',
 '## F／StatusQuoの制度と数量経路','',
 '制度比較の詳細はPolicy_Comparison.md。特定技能1号の通常のN4相当等、育成就労の就労前A1相当試験又は講習・3年間でA2相当、特定技能2号の一部分野N3、技人国の2026年4月以降の対象申請・対人言語業務でのB2相当資料提出を区別した。「政府は日本語不要、FだけN4」という扱いは誤り。家族・永住者等へF要件を一律適用するかも原文だけでは決まらない。','',
 '政府の2028年度末枠は特定技能1号805,700人、育成就労426,200人の分野別ストック上限の総計。現在の在留者を含み、全外国人の年間純増・年間新規入国ではない。資格変更と技能実習からの移行、分野別不足数がないため、今回の全外国人人口モデルで枠消化率を推計・強制執行することは未実装。両枠と施行日は出力し、数量外挿が制度適合することを証明したと扱わない。2029年度以降の枠を政府確定値として外挿していない。','',
 'Fの2030年N4・選別・即戦力・支援・分散は年次制度フラグとして反映し、人数への因果効果は空欄。人口1億未満で上限+20%は、原文2035年中間評価での発動判定と、毎年判定した場合の参考表示を分ける。元の受入上限の単位・数量が未確定なので上限そのものは空欄、実際の純移動へ1.2を掛けない。上限緩和は実受入人数の20%増を意味しない。','',
 '|経路2055年|人口万人|外国人万人|人口比|国内就業万人|外国人就業万人|実質GDP兆円|税収診断兆円|F−対応SQ兆円|','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for name in ['POLICY_HIST_SQ','POLICY_HIST_F','POLICY_LATEST_SQ','POLICY_LATEST_F','POLICY_IPSS_SQ','POLICY_IPSS_F','F_STOCK300','F_STOCK350','F_STOCK400','F_BAND3','F_BAND4','F_BAND5']:
  r=S[name];L.append('|'+name+'|'+'|'.join([f(r['population']/1e4),f(r['foreign']/1e4),f(r['population_ratio']*100)+'%',f(r['domestic_employed']/1e4),f(r['foreign_employed']/1e4),f(r['real_gdp_trn']),f(r['tax_diagnostic_trn']),f(r['delta_GDP_vs_matched_SQ'])])+'|')
 L+=['','FがSQより数量上抑制的になる条件は、Fの国際純移動が対応SQより小さい条件を置いた場合である。今回の比率参照ではそうなるが、これはN4条件から推定した抑制効果ではない。育成就労の入職前A1／講習からFのN4必須へ上がると候補供給が制約される可能性はある一方、支援・定着・即戦力優先・上限緩和の効果や既存N4/N3適格者の構成は不明。Fが必ず抑制的とは結論しない。同量FとSQのGDP差は他のF税制・教育・投資等を含み、外国人政策の識別効果ではない。','',
 '## 変更別の順次分解・旧結果比較','',
 '|変更段階・2055年|SQ GDP兆円|F同量 GDP兆円|SQ前段階差|F前段階差|','|---|---:|---:|---:|---:|']
 prev=None
 for stage in ['OLD','DOM','FOREIGN','VA']:
  q=S[stage+'_SQ'];r=S[stage+'_F'];L.append('|'+stage+'|'+f(q['real_gdp_trn'])+'|'+f(r['real_gdp_trn'])+'|'+('—' if prev is None else f(q['real_gdp_trn']-prev[0]))+'|'+('—' if prev is None else f(r['real_gdp_trn']-prev[1]))+'|');prev=[q['real_gdp_trn'],r['real_gdp_trn']]
 L+=['','OLDは前版再現、DOMは国内年齢男女率のみ、FOREIGNは外国人年齢就業方式も変更、VAは付加価値係数と国内基準重みをSNA参照へ変更。800万円の人件費化は意味の修正であり、人件費パラメータ自体によるGDP差は0。分解は順序依存・相互作用を含み、因果推定ではない。SQの数量経路再構成はHIST／LATEST／IPSS間の差、Fの数量条件変更は同一SQに対する経路差として示す。政府枠やN4が生む総数量差は未識別なので政策効果として埋めない。','',
 '|主要年|SQ実質GDP兆円|F同量GDP兆円|F40万GDP兆円|F比率4%GDP兆円|','|---|---:|---:|---:|---:|']
 for y in [2030,2035,2038,2045,2055]:L.append('|'+str(y)+'|'+'|'.join(f(at(n,y)['real_gdp_trn']) for n in ['POLICY_HIST_SQ','POLICY_HIST_F','F_STOCK400','F_BAND4'])+'|')
 L+=['','## 検証・残る不確実性','',
 f"{len(summary)}経路×30年={len(annual)}行を生成。旧版の選択3経路・90GDPセル一致は互換フックの確認であり、既存46経路の独立検算をやり直していない。人口ストック・フロー、就業人数の人口内上限・男女合計、VA係数ゼロ時の移民数量差GDP消失、人件費とVAの単位、GDP差分解、元TX内GDP・税収・資本・医療勘定を検査。人件費のみ変更した経路のGDP不変を確認した。再実行したAnnual.csv・Summary.csv・Report.mdの実バイト一致を確認した。",'',
 'Claude固定Commit b44b1facfd9940e12b2c55619b97f2f94328ad86の旧版46経路・数値不一致0は旧条件でのみ再利用。本版への独立検証PASSではない。政策原文を固定Commitから直接取得し、内容を比較した。新規正式レビューは追加していない。','',
 '主要な未確定点は、国籍別の年齢男女就業率、将来就業率・労働時間、資格構成・移行と分野別枠の消化、N4・支援の人数・定着効果、外国人固有の生産性、追加移民の出生死亡帰化コーホート、将来の政府枠。既存の係数未校正・部分財政勘定・賃金proxy・PB／国債発行／CPI未算定の制約を維持する。今回の較正は就業率と全国VA参照を改善したが、GDPの経済的妥当性を確定しない。','',
 '```bash','python3 Model.py Inputs.json --outdir replay','```','',
 '標準ライブラリのみ、ネット接続不要。入力には固定前版コード・TX関数・人口表・就業率・細分人口・旧結果を埋め込む。政策原文、main、既存固定原本は変更しない。']
 return '\n'.join(L)+'\n'

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('--outdir',required=True);a=p.parse_args();run(a.inputs,a.outdir)
