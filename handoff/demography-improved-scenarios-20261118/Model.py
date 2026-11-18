#!/usr/bin/env python3
"""DRAFT / NON-CANONICAL. IPSS-anchored population ledger + fixed TX macro channels.
Standard library. Run: python3 Model.py Inputs.json --outdir replay
"""
import argparse,base64,copy,csv,hashlib,json,math,types,zlib
from pathlib import Path

def close(a,b):return math.isclose(a,b,abs_tol=1e-6,rel_tol=1e-10)
def writecsv(path,rows):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
  for r in rows:w.writerow({k:format(v,'.11g') if isinstance(v,float) else v for k,v in r.items()})
def demography(cfg,spec):
 ref=cfg['population_reference'];a=cfg['common_assumptions'];obs=cfg['official_initial_2025_oct'];r25=ref['2025']
 anchored=spec.get('anchor','OBS2025')!='IPSS'
 dp=obs['population']-r25['population'] if anchored else 0.
 df=obs['foreign']-r25['foreign'] if anchored else 0.
 ages=[obs[k]-r25[k] if anchored else 0. for k in ['under15','working_age','elderly']]
 rows=[];cum=0.;previous_increment=a['band_reference_stock_increment']
 for y in range(2026,2056):
  r=ref[str(y)];rp=ref[str(y-1)]
  baseflow=163791. if y<=2040 else 163791.*r['population']/ref['2040']['population']
  # This residual includes foreign natural change,nationality and date/rounding effects.
  # It is not an observed nationality or Japanese migration estimate.
  fres=r['foreign']-rp['foreign']-baseflow
  mode=spec['mode'];flow=0.;residual=0.
  if y>2026:
   residual=fres
   if mode=='IPSS':flow=baseflow
   elif mode=='LATEST':flow=a['latest_foreign_net_flow']
   else:flow=a['common_foreign_net_flow']
   if spec['policy']=='F' and y>=a['F_start']:
    if mode.startswith('STOCK'):flow=int(mode[5:])*1000-fres
    elif mode=='NET400':flow=400000.
    elif mode=='BAND':
     J=r['japanese']+dp-df;target=spec.get('band_target',a['band_target'])
     target_stock=target/(1-target)*J
     desired=a['band_speed']*(target_stock-rows[-1]['foreign'])
     inc=(1-a['band_flow_smoothing'])*previous_increment+a['band_flow_smoothing']*desired
     flow=inc-fres;previous_increment=inc
   cum+=flow-baseflow
  P=r['population']+dp+cum;F=r['foreign']+df+cum;J=P-F
  # Preserve exact total and native/foreign split; age allocation of deviations is conditional.
  foreign_working=r['working_age']-r['japanese_working_age'];share=foreign_working/r['foreign']
  foreign_elder=r['elderly']-r['japanese_elderly'];eshare=foreign_elder/r['foreign']
  share25=(r25['working_age']-r25['japanese_working_age'])/r25['foreign']
  eshare25=(r25['elderly']-r25['japanese_elderly'])/r25['foreign']
  jw=r['japanese_working_age']+(ages[1]-df*share25 if anchored else 0.)
  je=r['japanese_elderly']+(ages[2]-df*eshare25 if anchored else 0.)
  wa=jw+F*share;elderly=je+F*eshare;child=P-wa-elderly
  employed_foreign=F*spec.get('employment',a['foreign_employment_per_resident'])
  employed_domestic=jw*a['employment_working_age']+je*a['employment_elderly']
  weighted=employed_domestic+employed_foreign*spec.get('productivity',a['foreign_value_added_trn_per_worker_2026'])/a['domestic_value_added_reference_trn']
  rows.append(dict(year=y,population=P,foreign=F,japanese=J,under15=child,working_age=wa,elderly=elderly,foreign_net_migration=flow,ipss_net_migration_reference=baseflow,foreign_nonmigration_reference_residual=residual,births_calendar=r['births_calendar'],deaths_calendar=r['deaths_calendar'],foreign_employed_conditional=employed_foreign,domestic_employed_conditional=employed_domestic,effective_productive_workers=weighted,ipss_population=r['population'],initial_population_offset=dp,migration_cumulative_difference=cum,foreign_births=None,foreign_deaths=None,nationality_net_transfer=None,japanese_net_migration=None))
  t=rows[-1];assert close(P,J+F) and close(P,child+wa+elderly) and P>F>0 and min(child,wa,elderly,jw,je)>0
  if len(rows)>1:
   prev=rows[-2];t['population_reference_bridge']=P-prev['population']-(r['births_calendar']-r['deaths_calendar'])-flow
   assert close(F-prev['foreign'],flow+residual)
  else:t['population_reference_bridge']=None
 return rows

def tx_engine(cfg,improved):
 source=zlib.decompress(base64.b64decode(cfg['tx_source_zlib_base64'])).decode()
 assert hashlib.sha256(source.encode()).hexdigest()==cfg['tx_source_sha256']
 if improved:
  def sub(old,new):
   nonlocal source
   assert source.count(old)==1,old[:100];source=source.replace(old,new)
  sub('    common_population=pop;policy_population_increment=0.;foreign_increment=0.;effective_labor=labor;expenditure_core=a[\'expenditure_proxy\']',"    common_population=pop;policy_population_increment=0.;foreign_increment=0.;labor=c['_trajectory'][0]['effective_productive_workers'];effective_labor=labor;expenditure_core=a['expenditure_proxy']")
  start=source.index('        if i:\n            if bprof[\'birth_mode\']')
  end=source.index('        f=tax_flows',start)
  source=source[:start]+'''        t=c['_trajectory'][i];sq=c['_common_trajectory'][i]
        if i:
            birth=t['births_calendar'];death=t['deaths_calendar']
            common_flow=sq['foreign_net_migration'];migrants=t['foreign_net_migration']
            policy_requested=policy_accepted=migrants-common_flow
            foreign=t['foreign'];foreign_increment=foreign-initialforeign
            common_population=sq['population'];policy_population_increment=t['population']-sq['population']
            prevpop=pop;pop=t['population'];flow_ramp=1.;cap_status='NO_GDP_OR_POPULATION_ENFORCEMENT'
            extra_workers=value(p['elderly_additional_workers'])*phase(y,2028) if enabled and not halt else 0.
            labornew=t['effective_productive_workers']+extra_workers
            if spec.get('gdp_labor_mode')=='LEGACY_POP':labornew=pop*p['labor_initial_ratio']+(foreign-initialforeign)*(p['foreign_labor_participation']-p['labor_initial_ratio'])+extra_workers
            lg=labornew/labor-1;labor=labornew;effective_labor=labornew
            growth=p['base_growth']+p['labor_response']*lg-risk
            expenditure_core*=1+schedule(bprof['expenditure_growth'],y)
            coreY*=1+growth;coreN*=1+growth+inflation;coreD=coreN/coreY
        elif oil:coreY*=1-oil;coreN*=1-oil+.02;coreD=coreN/coreY
''' +source[end:]
  sub("close(common_population-common_prev,birth-death+common_flow)","close(common_population-common_prev,birth-death+common_flow+sq['population_reference_bridge'])")
  sub("close(foreign,stock_prev*mig['foreign_stock_net_retention']+migrants)","close(foreign,stock_prev+migrants+t['foreign_nonmigration_reference_residual'])")
  # Comparison control must start with its own legacy initial effective-labor value.
  source=source.replace("labor=c['_trajectory'][0]['effective_productive_workers'];effective_labor=labor", "labor=(pop*p['labor_initial_ratio'] if spec.get('gdp_labor_mode')=='LEGACY_POP' else c['_trajectory'][0]['effective_productive_workers']);effective_labor=labor")
 ns={'__name__':'fixed_tx_functions'};exec(compile(source,'embedded_TX_dependency.py','exec'),ns);return ns

def main(inp,out):
 raw=Path(inp).read_bytes();cfg=json.loads(raw);engine=tx_engine(cfg,True);oldengine=tx_engine(cfg,False);paths={};demopaths={};allrows=[];summ=[]
 a=cfg['common_assumptions'];specs=cfg['cases']
 # Build reference SQ for each economic condition,not a shared mismatched counterfactual.
 def calculate(s):
  d=demography(cfg,s);cs={**s,'policy':'SQ','mode':('LATEST' if s['mode']=='LATEST' else 'IPSS' if s['mode']=='IPSS' else 'COMMON')};common=demography(cfg,cs)
  c=copy.deepcopy(cfg['tx_inputs']);c['_trajectory']=d;c['_common_trajectory']=common;c['initial']['population']=d[0]['population'];c['initial']['births']=d[0]['births_calendar'];c['initial']['deaths']=d[0]['deaths_calendar'];c['common_model']['slack']=s.get('slack',a['slack'])
  spec=dict(id=s['id'],policy=s['policy'],profile='TEXT_ASSUMPTIONS',supply_cap=True,medical_mode=s.get('medical_mode','UNALLOCATED_COMPAT'),gdp_labor_mode=s.get('gdp_labor_mode','WEIGHTED_EMPLOYMENT'),migration_override=dict(foreign_initial_stock=d[0]['foreign'],enforcement_mode='NONE_REFERENCE'))
  return engine['run_path'](c,spec),d
 for s in specs:
  r,d=calculate(s);paths[s['id']]=r;demopaths[s['id']]=d
 for d in demopaths['IPSS_EXACT_SQ']:
  ref=cfg['population_reference'][str(d['year'])]
  assert all(close(d[k],ref[k]) for k in ['population','foreign','japanese'])
 for s in specs:
  assert close(paths[s['id']][0]['real_gdp_trn'],cfg['tx_inputs']['initial']['real_gdp'])
  assert close(paths[s['id']][0]['nominal_gdp_trn'],cfg['tx_inputs']['initial']['nominal_gdp'])
 # Old paths only evaluate current fixed TX F/SQ; compare with embedded previously published rows.
 old={}
 for pol in ['SQ','F']:
  old[pol]=oldengine['run_path'](cfg['tx_inputs'],dict(id='OLD_'+pol,policy=pol,profile='TEXT_ASSUMPTIONS',supply_cap=True))
 regress=0
 refrows=list(csv.DictReader(__import__('io').StringIO(zlib.decompress(base64.b64decode(cfg['old_tx_csv_zlib_base64'])).decode())))
 for pol,rr in old.items():
  for r in rr:
   q=next(x for x in refrows if x['case']==f'TEXT_ASSUMPTIONS_{pol}_CAP' and int(x['year'])==r['year'])
   for k in ['real_gdp_trn','nominal_gdp_trn','population_persons','tax_diagnostic_trn']:
    assert math.isclose(r[k],float(q[k]),rel_tol=5e-10,abs_tol=1e-8);regress+=1
 # Conditional VA attribution only; it is never added to GDP a second time.
 for s in specs:
  rs=paths[s['id']];ds=demopaths[s['id']]
  # matched SQ and same-flow F remove all immigration changes for policy decomposition.
  sqs={**s,'id':'pairedSQ','policy':'SQ','mode':'LATEST' if s['mode']=='LATEST' else 'IPSS' if s['mode']=='IPSS' else 'COMMON'}
  sq,sd=calculate(sqs);fs,_=calculate({**sqs,'id':'pairedF','policy':'F'})
  for i,(r,d) in enumerate(zip(rs,ds)):
   y=r['year'];o=old[s['policy']][i];q= s.get('productivity',a['foreign_value_added_trn_per_worker_2026']);nomq=q*(r['common_deflator']/(cfg['tx_inputs']['initial']['nominal_gdp']/cfg['tx_inputs']['initial']['real_gdp']))
   nr=dict(case=s['id'],policy=s['policy'],migration_mode=s['mode'],anchor=s.get('anchor','OBS2025'),employment_fraction=s.get('employment',a['foreign_employment_per_resident']),value_added_per_worker_2026_yen=q*1e12,slack=s.get('slack',a['slack']),**d)
   for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','funding_gap_proxy_trn','household_disposable_nominal_trn','household_consumption_real_proxy_trn','I_policy_real_trn','capital_total_real_trn','unmet_demand_real','price_pressure_proxy','supply_binding','medical_insurer_vat','medical_extra_premium','medical_public_topup','medical_internal','medical_unallocated'] :nr[k]=r[k]
   nr.update(population_ratio=d['foreign']/d['population'],legacy_resident_gdp5_reference=d['foreign']*.000008/(r['core_real_gdp_trn']*r['common_deflator']),worker_va_attribution_nominal=d['foreign_employed_conditional']*nomq,worker_va_gdp_ratio=d['foreign_employed_conditional']*nomq/r['nominal_gdp_trn'],initial_foreign_va_included_not_added=ds[0]['foreign_employed_conditional']*q,delta_employment_vs_SQ=d['foreign_employed_conditional']-sd[i]['foreign_employed_conditional'],delta_va_attribution_vs_SQ=(d['foreign_employed_conditional']-sd[i]['foreign_employed_conditional'])*nomq,delta_GDP_vs_old=r['real_gdp_trn']-o['real_gdp_trn'],delta_population_vs_old=d['population']-o['population_persons'],delta_tax_vs_old=r['tax_diagnostic_trn']-o['tax_diagnostic_trn'],delta_GDP_vs_matched_SQ=r['real_gdp_trn']-sq[i]['real_gdp_trn'],F_nonmigration_GDP=fs[i]['real_gdp_trn']-sq[i]['real_gdp_trn'],F_migration_GDP=r['real_gdp_trn']-fs[i]['real_gdp_trn'] if s['policy']=='F' else 0.)
   if s['policy']=='F':assert close(nr['delta_GDP_vs_matched_SQ'],nr['F_nonmigration_GDP']+nr['F_migration_GDP'])
   allrows.append(nr)
  last=allrows[-1];u={k:last[k] for k in ['case','migration_mode','employment_fraction','value_added_per_worker_2026_yen','population','foreign','population_ratio','foreign_employed_conditional','real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','delta_GDP_vs_old','delta_GDP_vs_matched_SQ','F_nonmigration_GDP','F_migration_GDP']}
  rr=allrows[-30:]
  for k,t in [('population_ratio',.03),('population_ratio5',.05),('worker_va_gdp_ratio',.05),('legacy_resident_gdp5_reference',.05)]:
   key='population_ratio' if k=='population_ratio5' else k
   for op in ['reach','exceed']:u[k+'_'+op]=next((x['year'] for x in rr if x[key]>=t if op=='reach'),None) if op=='reach' else next((x['year'] for x in rr if x[key]>t),None)
  u['binding_years']=sum(x['supply_binding'] for x in rr);u['max_ratio']=max(x['population_ratio'] for x in rr);u['min_net_migration']=min(x['foreign_net_migration'] for x in rr[1:]);summ.append(u)
 out=Path(out);out.mkdir(parents=True,exist_ok=True);writecsv(out/'Annual.csv',allrows);writecsv(out/'Summary.csv',summ)
 assert Path(inp).read_bytes()==raw
 checks=dict(status='DRAFT_NON_CANONICAL',paths=len(paths),rows=len(allrows),old_regression_cells=regress,ledger_and_macro_identities='PASS',input_unchanged=True)
 (out/'Report.md').write_text(report(cfg,allrows,summ,checks),encoding='utf-8');print(json.dumps(checks))

def report(cfg,rows,summary,checks):
 # Defined below; deterministic report, no wall-clock time.
 return render_report(cfg,rows,summary,checks)

def render_report(cfg,rows,summary,checks):
 S={r['case']:r for r in summary}
 def f(x,n=3):return '未算定' if x is None else f'{x:,.{n}f}'
 def at(name,y):return next(x for x in rows if x['case']==name and x['year']==y)
 L=['# SPE 人口動態基盤改善・外国人材シナリオ比較','',
 '2026-11-18 / DRAFT / NON-CANONICAL。政策原文・Annex・main・既存固定成果物は変更しない。標準係数の採用・政策確定・Acceptance・Freezeは行わない。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。','',
 '## 今回新たに計算可能になったこと','',
 '社人研中位の総人口・日本人人口・年齢構成を参照し、常住外国人＝総人口−日本人として共通人口勘定を構成した。2025年10月同日実績に接続した初期条件と、2027年からの実績参照共通純移動を用いる。Fの年間外国人ストック純増30・35・40万人、純移動40万人、人口比3・4・5%を緩やかに目指す比較経路を分けた。就業率と就業者1人当たり付加価値を独立入力にし、既存GDPに含む外国人寄与の参考按分と、F−SQの追加効果を別出力した。','',
 '## 基準人口・定義・勘定','',
 '人口は各年10月1日。社人研2023年出生中位・死亡中位の表1-1、日本人参考表1、表1-5、表4-4を使用する。初期2026年は実測値そのものではなく、2025年10月実績から社人研2025→2026変化を適用した条件付き推計。総人口122,618,024人、外国人4,005,332人、日本人118,612,692人となる。人口推計2026年10月概算122,690,000人との差−71,976人も残る。2025国勢調査基準への改定前であり、最新実績に完全校正したものではない。別途IPSS_EXACT_SQで初期差ゼロの参照も保持する。','',
 '2025年実績と社人研の差は、総人口−42,976人、外国人+464,332人、日本人−507,308人。この3差を2026以降の共通初期差として維持する。人口比の分子分母は人口推計の常住定義で揃え、在留資格保有者（在留外国人）や雇用届出者と読み替えない。2026年6月在留外国人4,281,026人をこの分子へ直接代入していない。','',
 '計算式：P_s(y)=P_IPSS(y)+初期総人口差+Σ(M_s−M_IPSS)、F_s(y)=F_IPSS(y)+初期外国人差+Σ(M_s−M_IPSS)、J_s=P_s−F_s。共通の日本人人口を保ち、FとSQで流入差を総人口へ一回だけ反映する。外国人勘定はΔF=M_s+R_F、R_F=ΔF_IPSS−M_IPSS。R_Fは社人研の自然増・国籍異動・時点／丸めを含む未分離の参照残差であり、帰化件数と偽らない。外国人出生・死亡・国籍異動、日本人純移動の個別値は未算定（CSV空欄）。','',
 '出生死亡の表1-5は暦年、人口は10月。総人口の橋渡し項ΔP−(出生−死亡)−外国人純移動をpopulation_reference_bridgeとして出力し、暦年値を10月間隔の確定事象に偽装しない。橋渡し項には日本人純移動・時点差・千人丸めが含まれ、原因別配分は未取得。個別人口勘定の完全推計は未達だが、残差を消さず総数・日本人・外国人の恒等式を満たす。','',
 '社人研外国人純移動は2040年まで163,791人。2041年以降は本モデルでは163,791×社人研総人口(y)/社人研総人口(2040)という集計近似を使う。社人研本来の年齢性別率固定の完全再現ではない。この近似誤差はR_Fへ残し、IPSS_EXACT_SQの人口・外国人ストック自体は公表表へ厳密に戻る設計とした。今回の移民増減に応じた子孫出生・年齢コーホート・国籍変更の再推計は行っていない。年齢は日本人年齢別参照に2025年初期差を配分し、外国人には各年社人研の外国人年齢構成比を当てる条件付き配分で、独自コーホートモデルではない。','',
 '## シナリオ条件','',
 '|経路|2027〜2029|2030以降|','|---|---|---|',
 '|SQ_COMMON|国際純移動303,315.333人／年|同じ値を継続（2023〜25実績平均、予測ではない）|',
 '|F_SAME_FLOW|SQと同じ|SQと同じ。移民以外のF施策の対照|',
 '|F_STOCK300／350／400|SQと同じ|外国人ストック純増30／35／40万人。M=純増−R_F|',
 '|F_NET400|SQと同じ|国際純移動40万人。ストック増は40万人+R_F|',
 '|F_BAND3／4／5|SQと同じ|人口比3／4／5%へ向け、目標差の20%を年次調整、前年増加量との50%平滑化|',
 '|SQ_LATEST／F_COMMON_LATEST|327,557人（2025実績参照）|同じ値を継続|',
 '|SQ_IPSS／F_IPSS|社人研純移動参照|同じ仮定、人口初期差あり|',
 '|IPSS_EXACT_SQ|社人研純移動・初期差ゼロ|社人研人口表を再現する算術対照|','',
 '人口比参照では目標外国人ストック=T/(1−T)×J_y、希望増加量=.2×(目標−前年外国人)、当年増加量=.5×前年増加量+.5×希望増加量、純移動=増加量−R_F。初年の前年増加量35万人も暫定入力である。閾値で停止するルールやGDP比5%制限を設けず、平滑化の結果として一時超過・負の純移動も許す。負値は純流出という比較仮定であり、強制退去・総入国ゼロを意味しない。基準の3〜5%目安を強制達成させる最適化ではない。これらはOwnerが今回承認した比較用調整で、政策原文の確定仕様ではない。','',
 '## 2055年の比較','',
 '|経路|総人口万人|外国人万人|人口比|条件付き外国人就業万人|実質GDP兆円|税収診断兆円|人口5%超初年|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for n in ['SQ_COMMON','F_SAME_FLOW','F_STOCK300','F_STOCK350','F_STOCK400','F_NET400','F_BAND3','F_BAND4','F_BAND5','SQ_LATEST','SQ_IPSS','IPSS_EXACT_SQ']:
  r=S[n];L.append('|'+n+'|'+'|'.join([f(r['population']/1e4),f(r['foreign']/1e4),f(r['population_ratio']*100)+'%',f(r['foreign_employed_conditional']/1e4),f(r['real_gdp_trn']),f(r['tax_diagnostic_trn']),str(r['population_ratio5_exceed'] or '2055までなし')])+'|')
 L+=['','人口比4%参照の期間最大比率は'+f(S['F_BAND4']['max_ratio']*100)+'%、最小の年間国際純移動は'+f(S['F_BAND4']['min_net_migration'],0)+'人。人口比5%を目標にした平滑経路は最大'+f(S['F_BAND5']['max_ratio']*100)+'%へ一時超過する。いずれも目安への機械的な強制停止ではなく、負の純移動を実現可能・望ましいと政策判断したものでもない。']
 L+=['','### 主要年の年次比較','','|年|SQ／F40万総人口万人|SQ／F40万人口比|SQ／F40万実質GDP兆円|SQ／F40万税収診断兆円|F人口比4%参照の人口比|','|---|---:|---:|---:|---:|---:|']
 for y in [2030,2035,2038,2045,2055]:
  sq=at('SQ_COMMON',y);ff=at('F_STOCK400',y);b=at('F_BAND4',y)
  L.append('|'+str(y)+'|'+f(sq['population']/1e4)+'／'+f(ff['population']/1e4)+'|'+f(sq['population_ratio']*100)+'／'+f(ff['population_ratio']*100)+'%|'+f(sq['real_gdp_trn'])+'／'+f(ff['real_gdp_trn'])+'|'+f(sq['tax_diagnostic_trn'])+'／'+f(ff['tax_diagnostic_trn'])+'|'+f(b['population_ratio']*100)+'%|')
 L+=['','### 旧結果との差・差の分離','','旧参照はTX固定CommitのTEXT_ASSUMPTIONS_F_CAP／SQ_CAP。旧成果物は変更しない。新基盤は初期・出生死亡・移動時期・年齢労働接続が異なり、旧F−新Fを政策損失としない。各年の差はAnnual.csvへ保存。','','|経路|2055人口差万人|2055GDP差兆円|2055税収差兆円|','|---|---:|---:|---:|']
 for n in ['SQ_COMMON','F_SAME_FLOW','F_STOCK400','F_BAND4']:
  r=at(n,2055);L.append('|'+n+'|'+f(r['delta_population_vs_old']/1e4)+'|'+f(r['delta_GDP_vs_old'])+'|'+f(r['delta_tax_vs_old'])+'|')
 L+=['','人口の社人研中位からの差は、初期差と2027以降の累積純移動差へ厳密に分解できる。これは独立した人口予測の精度保証ではない。','','|経路|2055社人研との差万人|初期差万人|純移動累積差万人|','|---|---:|---:|---:|']
 for n in ['SQ_COMMON','F_STOCK300','F_STOCK400','F_BAND4']:
  r=at(n,2055);L.append('|'+n+'|'+f((r['population']-r['ipss_population'])/1e4)+'|'+f(r['initial_population_offset']/1e4)+'|'+f(r['migration_cumulative_difference']/1e4)+'|')
 L+=['','F政策差は同一基準のSQとの比較を用い、F_SAME_FLOW−SQを移民以外、各F−同じ共通流入Fを移民経路差とする。両者の和は全年度で総差へ一致する。人口・労働との相互作用を移民経路差側へ含める逐次分解で、独立な因果効果の推定ではない。','','|経路|2055F−SQ兆円|移民以外兆円|移民経路差・相互作用兆円|','|---|---:|---:|---:|']
 for n in ['F_STOCK300','F_STOCK350','F_STOCK400','F_BAND4']:
  r=S[n];L.append('|'+n+'|'+'|'.join(f(r[k]) for k in ['delta_GDP_vs_matched_SQ','F_nonmigration_GDP','F_migration_GDP'])+'|')
 L+=['','人口更新と労働接続更新の順次分解（SQ、2055年）：新人口を旧人口比例労働式へ入れた対照ANCHOR_ONLY_SQは'+f(S['ANCHOR_ONLY_SQ']['real_gdp_trn'])+'兆円。そこから年齢・就業割合・生産性の接続へ変更すると'+f(S['SQ_COMMON']['real_gdp_trn']-S['ANCHOR_ONLY_SQ']['real_gdp_trn'])+'兆円変化する。これは順序依存の仕様差分であり、人口更新だけの政策効果ではない。','','|経路|旧住民式GDP5%超|条件付き就業者式GDP5%超|','|---|---:|---:|']
 for n in ['SQ_COMMON','F_STOCK400','F_BAND4']:
  r=S[n];L.append('|'+n+'|'+str(r['legacy_resident_gdp5_reference_exceed'] or 'なし')+'|'+str(r['worker_va_gdp_ratio_exceed'] or 'なし')+'|')
 L+=['','## 就業率・800万円・GDP比5%の再評価','',
 '2024暦年の内閣府SNA（2020年基準）の名目GDP634.226兆円／同SNA就業者69,284,000人＝1人約915.4万円。旧基準609兆円や2025年労働力調査就業者68,280,000人と混ぜず、同年同SNA基準で計算した。800万円は全国平均と同じ桁だが外国人特有の実測係数ではなく、この比較だけで妥当と確定できない。産業構成・就業時間・資本装備・技能・自営業等が必要。給与292.4千円×12は雇用報酬の一部で、利益・減耗等を含む付加価値に置換できない。','',
 '今回の条件付き就業者=常住外国人×.6／.7／.8（全住民に対する就業割合で、15歳以上の労働参加率ではない）。初期含め推計であって届出実数ではない。厚労省2,571,037人／在留4,125,395人≒62.3%は対象日付が違う粗比率の参考に留め、.7を標準採用していない。国内就業も日本人15〜64歳×.8＋65歳以上×.2という未較正proxy。就業者を生産性係数で国内基準900万円相当へ換算し、既存TXの労働増減チャネルへ一回だけ接続する。初期GDPは600兆／580兆の既存設計値を維持し、外国人ストック×係数をGDPへ加算しない。600・800・1,000・1,200万円（2026名目価格相当）の感度を比較した。','',
 '付加価値係数は相対生産性としてGDP労働チャネルへ入る。GDPの人口弾性や供給・需要波及は旧TX係数を維持しており、就業者増×係数がそのままGDP純増となるモデルではない。診断用按分額は就業者×係数×共通デフレーター変化、実質係数は固定。これはGDPの外国人付加価値を統計的に分離した推定ではない。Annual.csvのworker_va_attribution_nominalをGDPへ再加算しない。初期寄与included列、SQとの差の診断按分額、実際のモデルGDP差を別々に示した。','',
 '|就業割合|係数万円|2055F40万実質GDP兆円|F−対応SQ兆円|就業者方式5%超初年|','|---|---:|---:|---:|---:|']
 for e in [.6,.7,.8]:
  for q in [6,8,10,12]:
   n='F_STOCK400' if e==.7 and q==8 else f'ECON_E{int(e*100)}_Q{q}_F400';r=S[n]
   L.append('|'+f(e,1)+'|'+str(q*100)+'|'+f(r['real_gdp_trn'])+'|'+f(r['delta_GDP_vs_matched_SQ'])+'|'+str(r['worker_va_gdp_ratio_exceed'] or 'なし')+'|')
 L+=['','GDP比の候補：(1)全住民×800万円／CORE名目GDPは旧参照式、(2)外国人就業者×条件付き付加価値／シナリオ名目GDPは寄与の診断按分、(3)SQに対する追加GDP／SQ名目GDPは反実仮想差で分子の価格整合が別途必要、(4)外国人就業者比率は人数比でGDP比ではない。(2)の総寄与を(3)の追加効果と混同しない。現行(1)(2)は両方を年次出力するが、どちらも5%超過で受入を制限しない。','',
 '## 供給感度と医療機能','',
 '|経路|拘束年数|2055実質GDP兆円|','|---|---:|---:|']
 for n in ['F_STOCK400','SLACK5_F400','SLACK10_F400','DM04_PREMIUM','DM04_PUBLIC','DM04_INTERNAL']:
  r=S[n];L.append('|'+n+'|'+str(r['binding_years'])+'|'+f(r['real_gdp_trn'])+'|')
 L+=['','DM04の保険料追加転嫁・公費補填・内部吸収および未配分互換、DM05の独立投資開始年と税率設定は元TX関数を維持する。医療財源の実額を推計せず、診療報酬補填の不明値を確定値にしない。供給slack2／5／10%も未校正の感度であり、GDP差が上限へ隠れる場合は政策効果ゼロを意味しない。','',
 '## Owner判断と追加実証','',
 '|論点|今回の数値で議論できること|判断／追加根拠|','|---|---|---|',
 '|人口比3〜5%と年30〜40万人|人口基準改善後も、一定のストック純増と比率維持は別経路になる|長期一定純増か人口比目安か、対象と評価時点を判断。人口比参照の速度・平滑化は暫定|',
 '|純増の定義|同じ40万人でもSTOCK400とNET400は異なる|住民純増／対象就業者純増／国際純移動を政策条件として区別|',
 '|就業割合・付加価値|独立感度と同条件SQ比較が可能|年齢資格産業別就業・労働時間・付加価値の実証が必要。.7・800万円は正式採用しない|',
 '|人口基準|初期差と流入累積差を分離|2025国勢調査基準の改定、暦年／10月期間統計、国籍異動・外国人出生死亡の追加取得が必要|',
 '|将来人口応答|公表コーホート推計を参照する共通基盤へ改善|追加移民の出生・死亡・帰化・年齢コーホートを再推計するには詳細率が必要。今回残差を独立推定と扱わない|',
 '|GDP比5%|住民式と就業者式で超過年が異なる|対象と付加価値／追加効果の意味を先に定義。受入制限に使わない|',
 '|治安・摩擦・地域能力|今回の人口比だけでは因果推定できない|地域の支援能力と費用、適正判定、雇用定着等の観測が必要。人数から安全上限を断定しない|','',
 '## 検証と再現','',
 f"{checks['paths']}経路×30年={checks['rows']}行。旧TX参照2経路の240セルは元公表CSV有効桁に応じ一致。全経路で総人口=日本人+外国人、年齢合計、外国人ストック、共通人口・政策差分、GDP・税収・資本・医療勘定、政策差分解の恒等式を実行時に検査。IPSS_EXACT_SQは全30年で社人研総人口・日本人・外国人ストックへ一致。入力は実行前後不変。再実行によるAnnual.csv・Summary.csv・Report.mdの実バイト一致を確認した。",'',
 '既存Claude検算Commit b789f0a4ba040d4cf9ddb707c81456d947527541の96経路・74,880数値セル一致は以前の調査についての証拠として再利用。本改良版の独立検算PASSではない。新規正式レビューは設けない。未較正係数、GDP・税収の部分勘定、実際の財政収支・国債発行・PB・CPI・賃金所得中央値未算定を維持。','',
 '```bash','python3 Model.py Inputs.json --outdir replay','```','',
 '標準ライブラリのみ。Inputs.jsonへ固定TX関数と旧入力・旧比較CSVを圧縮埋込みし、旧モデルへ書き込まずオフライン実行できる。人口フックのみ実行時に置換し、置換対象の一意性と元ソースSHA-256を検証する。人口フックを使わない対照は元関数で照合する。追加のVAT・投資教育効果式・医療の式変更はしていない。出典と取得ファイルSHAはInputs.jsonのsources、Data_Sources.mdを参照。']
 return '\n'.join(L)+'\n'

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('--outdir',required=True);a=p.parse_args();main(a.inputs,a.outdir)
