#!/usr/bin/env python3
"""DRAFT/NON-CANONICAL. Standard library; immutable Stage1 embedded in inputs."""
import argparse,base64,copy,csv,hashlib,json,math,zlib
from pathlib import Path

def load(c):
 b=zlib.decompress(base64.b64decode(c['stage1_model_zlib_base64']));assert hashlib.sha256(b).hexdigest()==c['stage1_model_sha']
 ns={'__name__':'stage1_functions'};exec(compile(b,'fixed_stage1.py','exec'),ns);return ns

def run(inp,out):
 original=Path(inp).read_bytes();c=json.loads(original);b=c['stage1_inputs'];old=load(c);prev,dep,engine=old['dependency'](b);annual=[];paths={};ledgers={};trajectories={}
 hist={(r['year'],r['sex'],r['age']):r['rate'] for r in c['employment_history']}
 def rate(y,age,sex,mode):
  r=prev['employment_rate'](b['previous_inputs'],age,sex)
  if age<65 or mode=='FIXED':return r
  group='65_69' if age<70 else '70_74' if age<75 else '75plus';label='male' if sex==0 else 'female';start=2015 if mode=='TREND10_TO2030' else 2019
  slope=(hist[2025,label,group]-hist[start,label,group])/(2025-start)
  # Same observed 2026 anchor. No unobserved employment trend added before 2027.
  return min(1.,max(0.,r+slope*max(0,min(y,c['trend_end'])-2026)))
 def trajectory(s):
  d,_=prev['labor_trajectory'](b['previous_inputs'],dict(id=s['id'],policy=s['policy'],mode='COMMON'),dep)
  for t in d:
   y=t['year'];raw=prev['age_rates'](b['previous_inputs'],y);J,wa,el=old['native_counts'](b,y);den=sum(sum(v) for a,v in raw.items() if int(a)>=65)
   delta=sum(v[sex]/den*el*(rate(y,int(a),sex,s['rates'])-rate(y,int(a),sex,'FIXED')) for a,v in raw.items() if int(a)>=65 for sex in [0,1])
   t['domestic_employed_conditional']+=delta;t['effective_productive_workers']+=delta
  return d
 for s in c['cases']:
  d=trajectory(s);common=trajectory({**s,'policy':'SQ'});ed=[]
  # Stage1 calls rates for all years in one ledger. Bind the year via its age-profile callback.
  current=[2026];view=dict(prev)
  def ages(pc,y):current[0]=y;return prev['age_rates'](pc,y)
  view['age_rates']=ages;view['employment_rate']=lambda pc,a,sex:rate(current[0],a,sex,s['rates'])
  ed=old['elder_ledger'](b,{**s,'weight':s['hours_ratio']*s['productivity_ratio']},view)
  tx=copy.deepcopy(b['previous_inputs']['base']['tx_inputs']);tx['_trajectory']=d;tx['_common_trajectory']=common;tx['_elder']=ed;tx['initial'].update(population=d[0]['population'],births=d[0]['births_calendar'],deaths=d[0]['deaths_calendar']);tx['common_model']['slack']=.02;tx['policy_inputs']['elderly_additional_workers']=0.
  spec=dict(id=s['id'],policy=s['policy'],profile='TEXT_ASSUMPTIONS',supply_cap=True,_link='LEVEL',_elder='MEDIUM',migration_override=dict(foreign_initial_stock=d[0]['foreign'],enforcement_mode='NONE_REFERENCE'))
  rr=engine['run_path'](tx,spec);paths[s['id']]=rr;ledgers[s['id']]=ed;trajectories[s['id']]=d
  for x,t,z in zip(rr,d,ed):
   ei=x['common_deflator']/(600/580);L=t['effective_productive_workers']+z['effective_extra']
   row=dict(case=s['id'],policy=s['policy'],SQ_rate_path=s['rates'],hours_ratio=s['hours_ratio'],hourly_productivity_ratio=s['productivity_ratio'],effective_weight=s['hours_ratio']*s['productivity_ratio'],population=t['population'],foreign=t['foreign'],foreign_employed=t['foreign_employed_conditional'],foreign_net_migration=t['foreign_net_migration'],domestic_employed=t['domestic_employed_conditional']+z['F_extra_jobs'],effective_labor=L,labor_productivity_real_yen=x['real_gdp_trn']*1e12/(t['domestic_employed_conditional']+t['foreign_employed_conditional']+z['F_extra_jobs']),**z)
   for k in ['real_gdp_trn','nominal_gdp_trn','core_real_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn','funding_gap_proxy_trn','household_disposable_nominal_trn','I_policy_real_trn','capital_total_real_trn','supply_binding','unmet_demand_real']:row[k]=x[k]
   for k in ['subsidy','pension_support','employee_contribution','employer_contribution','insurer_receipt']:row[k+'_nominal_trn']=z[k+'_base_trn']*ei
   assert old['close'](z['employee_contribution_base_trn']+z['employer_contribution_base_trn'],z['insurer_receipt_base_trn'])
   assert z['max_age_sex_rate']<=1 and z['F_extra_jobs']>=0 and not x['circuit_halted']
   row['pension_known_subtotal_nominal_trn']=row['insurer_receipt_nominal_trn']-row['pension_support_nominal_trn'];annual.append(row)
 # Matched annual baselines and finite-change attribution.
 lookup={(r['case'],r['year']):r for r in annual};inter=[]
 for row in annual:
  sid=row['case'];y=row['year'];sq=lookup[row['SQ_rate_path']+'_W50_SQ',y] if row['policy']=='F' else row
  row['elder_GDP_vs_zero']=row['real_gdp_trn']-lookup[row['SQ_rate_path']+'_NONE_F',y]['real_gdp_trn'] if row['policy']=='F' else 0.
  base=lookup['FIXED_W50_'+row['policy'],y];row['F_minus_SQ_GDP']=row['real_gdp_trn']-sq['real_gdp_trn'];row['GDP_delta_stage1']=row['real_gdp_trn']-base['real_gdp_trn']
  for s in ['foreign','foreign_employed','foreign_net_migration','population']:assert old['close'](row[s],base[s])
 for y in range(2026,2056):
  for policy in ['SQ','F']:
   get=lambda name:lookup[name+'_'+policy,y]['real_gdp_trn']
   a=get('FIXED_W50');r=get('TREND10_TO2030_W50');h=get('FIXED_H25OF40');both=get('TREND10_TO2030_H25OF40')
   inter.append(dict(year=y,policy=policy,rate_only=r-a,input_only=h-a,combined=both-a,interaction=both-r-h+a))
 # Reuse prior PASS; targeted regression of both Stage1 LEVEL/MEDIUM cases only.
 for policy,case in [('SQ','A11_SQ'),('F','A11_F')]:
  s=next(v for v in b['cases'] if v['id']==case);r,_,_=old['calculate'](b,s,prev,dep,engine)
  for x,z in zip(r,paths['FIXED_W50_'+policy]):
   for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','capital_total_real_trn']:assert old['close'](x[k],z[k]),(policy,k)
 # Equal products of hours and productivity must have identical GDP, but remain distinct inputs.
 for policy in ['SQ','F']:
  for x,z in zip(paths['FIXED_W50_'+policy],paths['FIXED_H25_P80_'+policy]):assert old['close'](x['real_gdp_trn'],z['real_gdp_trn'])
 out=Path(out);out.mkdir(parents=True,exist_ok=True);old['dump'](out/'Annual.csv',annual);old['dump'](out/'Interactions.csv',inter)
 summary=[r for r in annual if r['year'] in [2030,2035,2038,2045,2055]];old['dump'](out/'Comparison.csv',summary)
 old['dump'](out/'Employment_History.csv',c['employment_history'])
 lines=['# F高齢者就業：前提精査・限定再計算','', '2026-11-19 / DRAFT / NON-CANONICAL。RP-023／M19–25 HOLD、RP-024 PENDING維持。','', '## 実装と較正の境界','', '第1弾のLEVEL接続・実効投入0.5を再現する固定基準を維持。2015〜2025年の男女・65〜69／70〜74／75歳以上の観測就業率を入力化した。観測した傾きは較正できたが、将来の傾き継続は感度仮定である。TREND10は2015〜2025、TREND6は2019〜2025の年平均変化を2027〜2030年の4回だけ延長し、その後率を固定。初期GDP580兆円と2026労働アンカーを共通に維持し、2026初期値の変更による相殺を避けた。2026の実績就業率を推定した意味ではない。政府予測・F効果の推定ではない。','', '人口年齢構成は全ケース共通。固定率経路の変化は人口構成、同年固定率との差は階級内率変化、F追加人数はその上の非就業者プールから計算する。SQ率上昇でFの追加対象プールが縮小するため、Fの係数を変えずとも追加人数は減少する。外国人経路・就業率・915.4万円参照係数・その他政策は固定。','', '実効投入を労働時間比×時間当たり生産性比へ分離した。0.25／0.5／1.0の旧感度を維持し、25時間／40時間×1=0.625、同×0.8=0.5を追加。時間比は既存助成制度の短時間20〜30時間帯を参考にした例示であり、追加就業者の測定平均ではない。40時間は法定通常週の参照で、マクロの平均就業時間に一致するとは限らない。既存就業者の時間分布・賃金を追加就業者の限界生産性に転用していない。0.625を採用値とはしない。','', '## 2055年比較','', '|経路|SQ GDP兆円|F GDP兆円|F−SQ|F追加人数|F実効追加|Fの第1弾差|高齢者追加策ゼロ比GDP|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for name in ['FIXED_W50','TREND10_TO2030_W50','TREND6_TO2030_W50','FIXED_W25','FIXED_H25OF40','FIXED_W100','TREND10_TO2030_H25OF40']:
  f=lookup[name+'_F',2055];q=lookup[name+'_SQ',2055];lines.append('|'+name+'|'+'|'.join(f'{v:.6f}' for v in [q['real_gdp_trn'],f['real_gdp_trn'],f['F_minus_SQ_GDP'],f['F_extra_jobs'],f['effective_extra'],f['GDP_delta_stage1'],f['elder_GDP_vs_zero']])+'|')
 lines+=['','## 年次比較・財政・相互作用','', 'Comparison.csvは2030・2035・2038・2045・2055年、Annual.csvは全年。6年齢男女セルの人口・SQ/F率・追加人数、国内頭数・実効投入・生産性・税収・採用補助・本人/事業主保険料・保険者収入・年金支援を収録。Interactions.csvは率のみ、投入のみ、両方、相互作用=両方−率のみ−投入のみ＋基準をSQ/F別に保存する。F−SQは必ず同じSQ率経路との比較であり、基準の変化を政策効果と呼ばない。','', '補助金・賃金200万円・年金支援5万円・加入割合50%・離職補充10%・政策適用率/履行率/反応率は未較正の第1弾値を維持した。支出額は算定可能だが効果の実証推定ではない。実際の既存助成金適用者とF補助の重複受給は個票・制度定義がなく算定不能。今回のF補助は既存支出に加える仮定の増分勘定で、既存助成予算全体を計上していない。置換・死重損失をゼロと確認したものではない。年金既知小計は保険料−支援のみで将来給付・在職停止・全体収支は未算定。','', '## 検証・再実行','', f"{len(c['cases'])}経路×30年={len(annual)}行。第1弾のLEVEL/MEDIUM F/SQのGDP・名目GDP・税収・資本240セルを許容誤差内で再現。人口・外国人経路固定、就業率範囲、保険料本人＋企業＝保険者、回路非停止、時間×生産性の同積同結果を検査。元エンジンのGDP・税収・資本検査も保持。旧Claude算術PASSは旧対象範囲だけ再利用し、今回独立検証PASSとはしない。",'', '```bash','python3 Model.py Inputs.json --outdir replay','```','', '標準ライブラリのみ。Sources.mdは調査原本、その他CSVとReportは再生成される。出力の実バイト再現性は外側の再実行で確認。算術整合・政策忠実性・経済的妥当性は別の評価であり、後二者の未確定事項は残る。','', '## Owner判断と残る不確実性','', '固定率を基本参照として残し、短期トレンドと労働時間条件を併記する。F準義務化の対象年齢・履行・新規採用か継続雇用か・既存助成との併給条件は原文未指定。政策判断で確定する必要がある。追加就業者の時間・生産性、置換率、補助の因果効果は追加実証が必要。観測就業率上昇を既存制度の因果効果と断定しない。GDPを引き上げるための較正はしていない。政策原文・旧成果・mainは変更しない。']
 (out/'Report.md').write_text('\n'.join(lines)+'\n');assert original==Path(inp).read_bytes();print(json.dumps(dict(cases=len(c['cases']),annual_rows=len(annual),stage1_regression_cells=240,checks='PASS')))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('--outdir',required=True);a=p.parse_args();run(a.inputs,a.outdir)
