#!/usr/bin/env python3
"""Isolated provisional F / StatusQuo annual comparison. No formal engine writes.
python3 THIS.py INPUTS.json --outdir OUTPUT_DIR
Requires the companion V02 Python file; otherwise standard library only.
"""
import argparse,csv,copy,hashlib,importlib.util,io,json,math,platform,sys,types
from pathlib import Path


def sha(b):return hashlib.sha256(b).hexdigest()
def load_module(name,code):
    m=types.ModuleType(name);sys.modules[name]=m
    exec(compile(code,'<fixed '+name+'>','exec'),m.__dict__)
    return m
def pw(table,t):return [r['value'] for r in table if r['from']<=t][-1]
def close(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-7)
def strict_sum(vals):return None if any(x is None for x in vals) else sum(vals)


def sources_and_v02(cfg,root):
    bundle=cfg['sq_bundle'];sources=bundle['sources']
    for n,r in sources.items():
        if 'utf8' in r:
            b=r['utf8'].encode();assert len(b)==r['bytes'] and sha(b)==r['sha256'],n
    original=sources['sonzei_original.py']['utf8']
    a="None if credit_f is None else (1-policy['theta'])*credit_f"
    b="None if credit_f is None or credit_sq is None else (1-policy['theta'])*(credit_f-credit_sq)"
    fixed=(root/bundle['artifacts']['v02']).read_text()
    assert original.count(a)==1 and fixed==original.replace(a,b),'V02 must be exactly one expression replacement'
    old=load_module('sq_sonzei_old',original);new=load_module('sq_sonzei_v02',fixed)
    oracle,candidates=old.originals(cfg)
    old_rows=old.all_rows(cfg,candidates);new_rows=new.all_rows(cfg,candidates)
    # Reconstruct the exact original annual CSV without storing a second original.
    def as_csv(rows):
        f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);return f.getvalue().encode()
    old_bytes=as_csv(old_rows);new_bytes=as_csv(new_rows)
    assert sha(old_bytes)==sources['sonzei_original.csv']['sha256']
    assert old_bytes==new_bytes,'Current 1980-row baseline changed'
    p=copy.deepcopy(cfg['policy']);p['current_exempt_activity_input_credit']=.25
    profile,base=new.national_profiles(cfg,False)[0]
    after=new.diagnose(p,profile,base,2040);before=old.diagnose(p,profile,base,2040)
    expect=(1-p['theta'])*(after['input_credit_F']-after['input_credit_SQ'])
    assert close(after['business_retained_credit_only'],expect)
    assert before['business_retained_credit_only']>after['business_retained_credit_only']
    for k in after:
        if k!='business_retained_credit_only':assert after[k]==before[k],k
    log=[f'PASS V02 only one expression differs; current 1980-row CSV byte identical SHA256={sha(new_bytes)}',
         f'PASS credit_SQ>0 test: old={before["business_retained_credit_only"]:.6f} JPY, new={expect:.6f} JPY; all other fields unchanged',
         'PASS V02 missing credit remains unknown; loss/tax/public/GDP definitions unchanged']
    m=new.diagnose(cfg['policy'],dict(profile,credit_category='mixed_unknown'),base,2040)
    assert m['business_retained_credit_only'] is None
    return new_rows,log


def driver(c,a,case,t,wage):
    isf=case.startswith('F_');low=case=='SQ_POLICY9_LOW_29';high=case=='SQ_POLICY9_HIGH_29'
    risks=[r for r in c['risk_shock_pct']['rules'] if (r['type']=='once' and t==r['year']) or (r['type']=='every' and t>=r['start'] and (t-r['start'])%r['step']==0)]
    risk=sum(r['pct'] for r in risks)/100
    tag=[]
    if t==2026:tag.append('OIL_2026')
    if t==2027:tag.append('TAIWAN_2027')
    if t==2031:tag.append('NANKAI_2031')
    if t>=2029 and (t-2029)%3==0:tag.append('DISASTER_3Y')
    if t>=2027 and (t-2027)%2==0:tag.append('CLIMATE_2Y')
    grow=.01 if isf or low or high else (.01 if t<=2034 else .006 if t<=2044 else .003)
    invest=pw(c['policy_effects_pct']['investment_promotion'],t)/100 if isf else .003 if low else .005 if high else 0.0
    migration=c['migration']['steady_per_year'] if isf else 400000 if case=='SQ_V5_MIGRATION400_29' else a['sq_migration_steady']
    ramp=c['migration'];net=0 if t<ramp['ramp_start'] else migration*min((t-ramp['ramp_start']+1)/ramp['ramp_years'],1)
    elasticity=pw(c['tax_elasticity']['table'],t) if isf else 1.5 if low else 2.0 if high else .85 if t<=2034 else .75
    return {'death_rate_coefficient':c['death_rate_coefficient']['value'],'birth_decline_coefficient':c['birth_decline_coefficient']['value'],'phi':c['phi']['value'],
       'real_wage_growth_rate':0 if t==2026 else wage.wage_growth_rate(wage.anchors,t), 'net_migration':net,
       'aging_drag':pw(c['aging_drag_pp']['table'],t)/100,'base_growth_rate':grow,
       'consumption_stimulus_effect':pw(c['policy_effects_pct']['consumption_stimulus'],t)/100 if isf else 0.0,
       'investment_promotion_effect':invest,'education_effect':pw(c['policy_effects_pct']['education'],t)/100 if isf else 0.0,
       'risk_shock':risk,'alpha':c['alpha']['value'],'base_inflation_rate':c['base_inflation_rate_pct']['value']/100,
       'risk_event_inflation_impact':c['inflation_extra_pp']['by_year'].get(str(t),0)/100,'consumption_tax_transitional_factor':0.0,
       'tax_elasticity':elasticity,'expenditure_growth':pw(c['expenditure_growth_pct']['table'],t)/100 if isf else .03,
       'tax_event_factor':c['tax_factor_by_year'].get(str(t),1.0),'tax_cap_ratio':c['tax_cap_ratio_of_nominal_gdp']['value'],'event_names':';'.join(tag)}


def simulate(cfg,case,engine,wage_module,sonzei):
    b=cfg['sq_bundle'];c=b['f_config'];a=b['assumptions'];isf=case.startswith('F_')
    anchors={int(y):float(v) for y,v in (c['wage_anchor_man_yen']['anchors'] if isf else a['wage_anchors_sq_man_yen']).items()}
    w=types.SimpleNamespace(anchors=anchors,wage_growth_rate=wage_module.wage_growth_rate)
    legacy=case.endswith('30');initial=c['initial_state_2025_end']
    st=engine.SimulationState(year=2025 if legacy else 2026,**{k:v for k,v in initial.items() if k!='tag'})
    rows=[]
    def record(t,kind,p,result=None,prev=None):
        applied=kind=='TRANSITION';popg=None if prev is None else st.population/prev.population-1
        gini_end=.348 if isf else .415
        diag=[sonzei[('CLAUDE_BASELINE_'+s,t)] for s in ['medical','education','rental']]
        guarded=[sonzei[('NATIONAL_GUARDED_'+s,t)] for s in ['medical','education','rental']]
        return {'record_type':'PATH','case':case,'year':t,'boundary':'30_TRANSITIONS_LEGACY' if legacy else '2026_INITIAL_29_TRANSITIONS',
          'row_kind':kind,'real_gdp_trn':st.real_gdp,'nominal_gdp_trn':st.nominal_gdp,'tax_revenue_trn':st.tax_revenue,'expenditure_trn':st.expenditure,
          'funding_gap_proxy_trn':max(st.expenditure-st.tax_revenue,0),'population_persons':st.population,'births_persons':st.births,'deaths_persons':st.deaths,
          'net_migration_applied_persons':p['net_migration'] if applied else 0,'net_migration_scheduled_persons':p['net_migration'],
          'population_growth_pct':None if popg is None else popg*100,'labor_force_growth_pct':None if result is None else result.labor_force_growth_rate*100,'labor_force_population_persons':None,
          'real_growth_pct':None if result is None else result.real_gdp_growth_rate*100,'nominal_growth_pct':None if result is None else result.nominal_gdp_growth_rate*100,'inflation_pct':None if result is None else result.inflation_rate*100,
          'base_growth_scheduled_pct':p['base_growth_rate']*100,'consumption_effect_scheduled_pp':p['consumption_stimulus_effect']*100,'investment_effect_scheduled_pp':p['investment_promotion_effect']*100,'education_effect_scheduled_pp':p['education_effect']*100,
          'aging_drag_scheduled_pp':p['aging_drag']*100,'risk_scheduled_pct':p['risk_shock']*100,'risk_applied_pct':p['risk_shock']*100 if applied else 0,
          'event_names':p['event_names'],'events_applied':int(applied),'inflation_risk_applied_pp':p['risk_event_inflation_impact']*100 if applied else 0,'tax_event_factor_applied':p['tax_event_factor'] if applied else 1,
          'tax_elasticity_scheduled':p['tax_elasticity'],'expenditure_growth_scheduled_pct':p['expenditure_growth']*100,'tax_to_nominal_gdp_pct':st.tax_revenue/st.nominal_gdp*100,
          'real_wage_anchor_man_yen':wage_module.interpolate_wage(anchors,t),'gini_anchor':.380+(gini_end-.380)*(t-2026)/29,
          'wage_gini_status':'EXOGENOUS_ANCHORS_NOT_ENDOGENOUS_RESULTS','actual_bond_issuance_trn':None,'primary_balance_trn':None,'initial_bond_reference_trn':28 if t==2026 and not legacy else None,
          'sonzei_L_SQ_reference_trn':sum(r['L_SQ'] for r in diag)/1e12,
          'sonzei_L_F_legacy_reference_trn':sum(r['L_F'] for r in diag)/1e12 if isf else None,
          'sonzei_L_F_guarded_reference_trn':None if not isf or any(r['L_F'] is None for r in guarded) else sum(r['L_F'] for r in guarded)/1e12,
          'sonzei_macro_link':'FIXED_SECTOR_ASSUMPTIONS_NOT_LINKED_TO_THIS_MACRO_PATH','sonzei_GDP_addition_trn':0.0,'sonzei_tax_addition_trn':0.0}
    if not legacy:
        rows.append(record(2026,'INITIAL_STATE',driver(c,a,case,2026,w)))
    for t in range(2026 if legacy else 2027,2056):
        p=driver(c,a,case,t,w);prev=st
        ds=engine.transition_year_demographics(previous_state=prev,**{k:p[k] for k in ['death_rate_coefficient','birth_decline_coefficient','phi','real_wage_growth_rate','net_migration']})
        kwargs={k:v for k,v in p.items() if k not in ['expenditure_growth','tax_event_factor','tax_cap_ratio','event_names']}
        kwargs['total_population_growth_rate']=ds.population/prev.population-1
        result=engine.transition_year(prev,**kwargs)
        nom=prev.nominal_gdp*(1+result.nominal_gdp_growth_rate)
        st=engine.SimulationState(year=t,real_gdp=prev.real_gdp*(1+result.real_gdp_growth_rate),nominal_gdp=nom,tax_revenue=min(result.tax_revenue_before_cap*p['tax_event_factor'],nom*p['tax_cap_ratio']),expenditure=prev.expenditure*(1+p['expenditure_growth']),population=ds.population,births=ds.births,deaths=ds.deaths)
        assert close(st.population,prev.population+st.births-st.deaths+p['net_migration'])
        rows.append(record(t,'TRANSITION',p,result,prev))
    return rows


def run(cfg,root):
    b=cfg['sq_bundle'];sources=b['sources'];sonzei_rows,logs=sources_and_v02(cfg,root)
    sonzei={(r['case_id'],r['year']):r for r in sonzei_rows}
    engine=load_module('sq_fixed_engine',sources['prototype.py']['utf8']);wage=load_module('sq_fixed_wage',sources['m14_wage_anchor.py']['utf8'])
    cases=['F_2026_INITIAL_29','SQ_V5_CANDIDATE_29','SQ_POLICY9_LOW_29','SQ_POLICY9_HIGH_29','SQ_V5_MIGRATION400_29','F_2026_TRANSITION_30','SQ_V5_LEGACY30']
    paths={c:simulate(cfg,c,engine,wage,sonzei) for c in cases}
    expected=list(csv.DictReader(io.StringIO(sources['SPE_F_Annual_Results_DRAFT_20261110.csv']['utf8'])))
    index={(r['case'],r['year']):r for r in expected}
    mapping={'real_gdp_trn':'real_gdp','nominal_gdp_trn':'nominal_gdp','tax_revenue_trn':'tax_revenue','expenditure_trn':'expenditure','population_persons':'population','births_persons':'births','deaths_persons':'deaths','funding_gap_proxy_trn':'funding_gap_proxy','real_wage_anchor_man_yen':'real_wage_anchor_man_yen','tax_to_nominal_gdp_pct':'tax_to_gdp_pct'}
    for c in ['F_2026_INITIAL_29','F_2026_TRANSITION_30']:
        for r in paths[c]:
            exp=index[(c,str(r['year']))]
            for k,v in mapping.items():assert close(r[k],float(exp[v])),(c,r['year'],k,r[k],exp[v])
    logs.append('PASS F primary+legacy: 60 rows x 10 stored metrics reproduce fixed 30530ad2 results')
    for c,rows in paths.items():
        assert [r['year'] for r in rows]==list(range(2026,2056))
        assert sum(r['row_kind']=='TRANSITION' for r in rows)==(30 if c.endswith('30') else 29)
        for r in rows:
            for k in ['real_gdp_trn','nominal_gdp_trn','tax_revenue_trn','expenditure_trn','population_persons','births_persons','deaths_persons']:
                assert math.isfinite(r[k]) and r[k]>=0
            assert r['tax_to_nominal_gdp_pct']<=30+1e-9
            assert r['actual_bond_issuance_trn'] is None and r['primary_balance_trn'] is None and r['labor_force_population_persons'] is None
            assert r['sonzei_GDP_addition_trn']==r['sonzei_tax_addition_trn']==0
    logs.append('PASS 7 paths x 30 continuous years; 29/30 transitions; nonnegative finite stocks; tax cap; missing indicators preserved')
    f=paths['F_2026_INITIAL_29'];sq=paths['SQ_V5_CANDIDATE_29']
    for a,r in zip(f,sq):
        for k in ['risk_applied_pct','risk_scheduled_pct','event_names','inflation_risk_applied_pp','tax_event_factor_applied','aging_drag_scheduled_pp','row_kind']:
            assert a[k]==r[k],(a['year'],k)
    assert f[0]['risk_scheduled_pct']==3 and f[0]['risk_applied_pct']==0
    assert sq[1]['risk_applied_pct']==5.5
    assert close(next(r for r in sq if r['year']==2031)['risk_applied_pct'],3.5)
    assert next(r for r in sq if r['year']==2031)['tax_event_factor_applied']==.9
    logs.append('PASS common calendar: 2026 scheduled oil not transitioned in primary; 2027 conflict+climate 5.5%; 2031 quake+climate 3.5% and tax x.90')
    assert next(r for r in sq if r['year']==2035)['base_growth_scheduled_pct']==.6
    assert next(r for r in sq if r['year']==2045)['base_growth_scheduled_pct']==.3
    assert all(r['consumption_effect_scheduled_pp']==0 and r['education_effect_scheduled_pp']==0 and r['investment_effect_scheduled_pp']==0 for r in sq)
    assert sq[-1]['real_wage_anchor_man_yen']==472 and sq[-1]['gini_anchor']==.415
    assert paths['SQ_POLICY9_LOW_29'][-1]['tax_elasticity_scheduled']==1.5
    assert paths['SQ_POLICY9_HIGH_29'][-1]['tax_elasticity_scheduled']==2.0
    logs.append('PASS SQ v5 parameter breaks, wage/Gini anchors; no F-specific add-ons; policy9 endpoints are separate sensitivities')
    assert all(close(r['sonzei_L_SQ_reference_trn'],f[i]['sonzei_L_SQ_reference_trn']) for rows in paths.values() for i,r in enumerate(rows))
    logs.append('PASS fixed L_SQ diagnostic reused unchanged across macro paths; no GDP/tax/debt automatic addition')
    numeric_diff=['real_gdp_trn','nominal_gdp_trn','tax_revenue_trn','expenditure_trn','funding_gap_proxy_trn','population_persons','births_persons','deaths_persons','real_wage_anchor_man_yen','gini_anchor','labor_force_growth_pct','tax_to_nominal_gdp_pct']
    diff=[]
    for a,r in zip(f,sq):
        d={k:None for k in a};d.update({'record_type':'DIFFERENCE','case':'F_MINUS_SQ_V5_29','year':a['year'],'boundary':'MATCHED_2026_INITIAL_29','row_kind':'INITIAL_DIFFERENCE' if a['year']==2026 else 'YEAR_DIFFERENCE','sonzei_macro_link':'NOT_ADDED_TO_MACRO','wage_gini_status':'ANCHOR_DIFFERENCE_NOT_DISTRIBUTION_EFFECT'})
        for k in numeric_diff:d[k]=None if a[k] is None or r[k] is None else a[k]-r[k]
        diff.append(d)
    assert diff[0]['real_gdp_trn']==diff[0]['population_persons']==0
    logs.append('PASS matched F−SQ difference rows share initial GDP/population and year definitions')
    return [r for rows in paths.values() for r in rows]+diff,paths,logs


def write_csv(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def report(cfg,paths,logs,out):
    b=cfg['sq_bundle'];a=b['assumptions'];s=b['sources'];f=paths['F_2026_INITIAL_29'];sq=paths['SQ_V5_CANDIDATE_29']
    lines=[]
    for y in [2026,2028,2031,2035,2040,2055]:
        for case,rs in [('F主',f),('SQ v5候補',sq)]:
            r=next(r for r in rs if r['year']==y)
            lines.append('|'+str(y)+'|'+case+'|'+'|'.join(f'{r[k]:,.6f}' for k in ['real_gdp_trn','nominal_gdp_trn','tax_revenue_trn','expenditure_trn','funding_gap_proxy_trn'])+'|'+f'{r["population_persons"]/10000:,.4f}'+'|'+f'{r["real_wage_anchor_man_yen"]:.4f}|{r["gini_anchor"]:.6f}|')
    endpoints=[]
    for case,rs in paths.items():
        r=rs[-1];endpoints.append('|'+case+'|'+'|'.join(f'{r[k]:,.6f}' for k in ['real_gdp_trn','tax_revenue_trn','funding_gap_proxy_trn'])+'|'+f'{r["population_persons"]/10000:,.4f}'+'|')
    old=a['v5_old_reference'];r=sq[-1];rl=paths['SQ_V5_LEGACY30'][-1]
    src='\n'.join('|`'+n+'`|`'+v['commit']+'`|'+str(v['bytes'])+'|`'+v['sha256']+'`|' for n,v in s.items())
    v02=(Path(__file__).parent/b['artifacts']['v02']).read_bytes()
    return f'''# SPE｜V-02限定修正・StatusQuo暫定実装 実行報告

Status: DRAFT / PROVISIONAL / NON-CANONICAL  
作成日: 2026-11-15（Asia/Tokyo、依頼日）  
実行: Python {platform.python_version()} / {platform.system()}。標準ライブラリのみ。追加インストールなし。

## 結果

V-02は1式だけを変更し、現行1,980行の全CSV実バイト不変を確認。credit_SQ>0の試験では控除増分を使用し、他の列は不変だった。StatusQuoは2026初期状態から29回遷移する主ケースを実行し、2026〜2055年のF比較CSVを作成した。全国推計の妥当性や正式採用の承認ではない。

成果物は指定4件に、再実行用入力JSON1件を追加した。JSONは固定エンジン2原本、F入力・出力・アダプタ、政策原本/v5、旧損税コード・入力等を内包し、外部取得なしで再実行できる。ZIPは使用しない。

## V-02限定差分

```python
None if credit_f is None or credit_sq is None else (1-policy['theta'])*(credit_f-credit_sq)
```

変更前の控除総額基準から増分へ変更。欠損はNoneのまま。原コードに対してこの1式以外の差分がないことを機械確認した。V-01・V-03〜V-05は変更していない。新コードSHA-256：`{sha(v02)}`。現行credit_SQ=0のため出力CSVは固定原本SHA `e4a0e91e3f24ffec14a831c95b7d44bc116afff7655ff1ba483b9066c2c6ed5a` と一致する。

## 採用設定と優先関係

StatusQuo本文は既存制度の漸進的調整を継続する方針。主ケース `SQ_V5_CANDIDATE_29` はOwnerが候補指定した旧v5 §4-5を、再現可能な**推定パラメータ候補**として採用する。政策原本第9節を誤記・無効と判断したのではない。旧v5の「流用ミス」記載は旧文書の見解であり、本Workが原本第9節を取り消す裁定をしていない。

|項目|主SQ候補|F主・共通条件／差|
|---|---|---|
|実質基調成長|1.0%〜2034、0.6%2035〜44、0.3%2045〜|Fは1%＋既存F効果。SQの基調項が既存制度継続を含む縮約仮定|
|税収弾性|.85〜2034、.75以降|F 1.5→1.7→2.0の既存設定と分離|
|歳出成長|3%全期間|F 2.5→1.5→1.0%の既存設定と分離|
|消費刺激/教育/F追加投資|主SQでは個別上乗せなし|v5主ケース式による。既存制度の経済作用がゼロという意味ではない|
|純移民|2030〜34に35.7万人/年へ線形ランプ|F同じランプで40万人。35.7万人は旧人口目標からの逆算仮定で現行実績ではない。開始・刻みはFとの共通化仮定|
|死亡・出生|1.015、.975、出生賃金弾性φ=.15|v6実装の同じ関数。φは推定|
|賃金アンカー|400→472万円・幾何補間|F 400→860。いずれも外生アンカー。本文/仕様§1の実質初期380とは不一致を保持|
|ジニアンカー|.380→.415・線形補間|F .380→.348をv5から参考補足。既存Fコードの内生計算値ではなく、共通の表示用補間仮定|
|労働項|人口成長＋共通aging drag、資本α=.35|労働力人口の人数は未算出。移民の年齢構成も未実装|
|インフレ/名目GDP|2%＋イベント、名目成長=実質成長＋インフレ|複利の積ではなく既存v6の加算定義を共通使用|
|財政|弾性式・GDP30%cap・2031税収×.9|同じ式。歳出−税収正部は資金不足proxyだけ|

政策原本第9節の基調1%・弾性1.5〜2・投資+.3〜.5ppは、`SQ_POLICY9_LOW_29`（1.5/.3）と`SQ_POLICY9_HIGH_29`（2.0/.5）の**別感度**で計算した。中間値の創作なし。2つの同時端点ケースであり、統計的信頼区間や全条件の上下限ではない。歳出・賃金・移民等は比較のため主SQ候補と共通の仮定を維持し、本文だけから一意に決まるシナリオとは称さない。本文第9節の名目成長3%は基調1%＋インフレ2%の説明として参照し、イベントや人口項を含む実際の年次名目成長を毎年3%に固定してはいない。

さらに `SQ_V5_MIGRATION400_29` は移民定常値だけを40万人にする比較用反実仮想。主StatusQuo政策として採用せず、Fとの差に含まれる移民仮定の影響を分離する。`F_2026_TRANSITION_30` と `SQ_V5_LEGACY30` は境界差だけの参考で、主29回比較と混ぜない。

## 境界・イベント

主比較の2026は保存済み初期状態。両ケースで実質GDP580・名目600・税収80・歳出108兆円、人口121,500,000・死亡1,590,000・出生640,000を共有。2026オイルショックは予定入力に記録するが、**初期状態へ遷移ショックとして適用しない**。2027に繰り越してもいない。これは固定F主ケースの境界との一致を優先したため。

30回遷移参考だけは初期状態を2025末と表示して2026オイルGDP−3%・追加インフレ2ppを適用する。2027は中台5%＋気候.5%=5.5%、2031は南海3%＋気候.5%=3.5%と税収×.90。2029起点3年災害、2027起点隔年気候は重複年に両方加算する。F/SQのイベント暦・インフレ影響・aging dragの一致を全30年確認した。

## 計算式と比較可能範囲

```text
deaths_t = deaths_(t−1)×1.015
births_t = births_(t−1)×.975×(1+.15×wage_growth_t)
population_t = population_(t−1)+births_t−deaths_t+net_migration_t
labor_growth_t = population_growth_t + aging_drag_t
real_growth_t = base + consumption + investment + education − risk + .65×labor_growth_t
inflation_t = .02 + risk_inflation_t
nominal_growth_t = real_growth_t + inflation_t
tax_t = min(tax_(t−1)×(1+nominal_growth_t×elasticity_t)×event_factor_t, nominalGDP_t×.30)
expenditure_t = expenditure_(t−1)×(1+expenditure_growth_t)
funding_gap_proxy_t = max(expenditure_t−tax_t,0)
```

上記は固定v6関数をそのまま読み込み、暫定アダプタで政策別係数・歳出・capを適用。正式エンジンを書き換えていない。Fの60行（主＋参考）の10指標を固定F出力と照合した。

GDP・税収・歳出・人口/出生/死亡・労働成長率は同一定義で比較可能。賃金/ジニは外生アンカーの比較であり、内生的政策帰着ではない。労働力人口人数、実際の国債発行額、PB、所得中央値等は未算出。CSVの実際の国債発行/PB/労働力人口列は空欄とし、資金不足proxyで穴埋めしていない。初期国債28兆円は初期参照値だけで、将来国債系列へ接続しない。

## 主要年結果

GDP・財政は兆円、人口は万人、賃金は万円。丸め表示でありCSVの精度とは分ける。

|年|ケース|実質GDP|名目GDP|税収|歳出|資金不足proxy|人口・万人|賃金アンカー|ジニアンカー|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(lines)}

## 2055年・感度と旧v5参考

|ケース|実質GDP・兆円|税収・兆円|資金不足proxy・兆円|人口・万人|
|---|---:|---:|---:|---:|
{chr(10).join(endpoints)}

旧v5参考はGDP381.4兆円・人口8,298万人・『国債発行』174兆円。今回の主SQはそれぞれGDP差 `{r['real_gdp_trn']-old['real_gdp_2055_trn']:+.6f}`兆円、人口差 `{(r['population_persons']-old['population_2055'])/10000:+.4f}`万人。資金不足proxyと旧ラベル値の数値差は `{r['funding_gap_proxy_trn']-174:+.6f}`兆円だが、実際の国債発行の差とは解釈しない。

境界を30回に戻した参考SQはGDP `{rl['real_gdp_trn']:.6f}`兆円・人口 `{rl['population_persons']/10000:.4f}`万人・proxy `{rl['funding_gap_proxy_trn']:.6f}`兆円。29/30の差はこの参考ケースで分離できる。残る旧v5との差は移民ランプの詳細、賃金補間・年度境界、v6実装への接続等が候補だが、旧試算の実行コード/全入力は今回の指定原本に無く、寄与を一意に分解できない。本文の結果値へ合わせる係数調整はしていない。

## 損税診断との距離

`sonzei_L_SQ_reference_trn` は固定した3部門R/P仮定のL_SQ合計を再利用し、すべてのマクロケースで同じ値を保持する。マクロGDPで売上を自動スケールしない。Fの旧再現L_Fと住宅条件留保後L_Fは別列。留保後は2037年以降の欠損合計を空欄とする。損税削減・税収帰属・公費負担を、マクロGDP・税収・実際の国債へ加算していない。マクロの税収弾性仮定と損税効果を二重計上しない。

## 実行・確認ログ

```bash
python3 {b['artifacts']['model']} {b['artifacts']['inputs']} --outdir replay
# V02だけを旧CLIで試す場合（入力JSONは同じ）:
python3 {b['artifacts']['v02']} {b['artifacts']['inputs']} --outdir v02-replay
```

V02単独CLIは元の出力名を使用するため、必ず独立出力ディレクトリを指定する。GitHub追加原本は今回の5件だけ。

```text
{chr(10).join(logs)}
exit=0
```

CSVは7経路×30年＋F主−SQ主の30差分行、計240行。`record_type=DIFFERENCE` は経路として合算しない。DIFFERENCEの実質GDP等はF−SQ、賃金/ジニ差もアンカー差であり、未知の指標は差分でも空欄。PATHの`*_scheduled`は当年の予定係数で、2026初期行で適用済みとはしない。列名`_trn`は兆円、`_persons`は人、`_pct`/`_pp`は%、ポイント。

保存CSVを再読取し、年次・欠損・単位を確認する。再実行のバイト一致は引渡し回答で報告する。後続Claude検証や比較HTMLは今回実施しない。実装PASSと政策推計妥当性を分離する。

再開時には前回DRAFTを別名退避した。前回コードの2031年リスク検査に浮動小数点の完全一致比較が残っていたため、既存の許容誤差付きclose検査へ変更した。3.5%という予定値・計算式・CSVの数値はこの修正で変えていない。最終実行は上記すべてPASS。これは利用制限そのものの原因を特定したという報告ではない。

## 出典原本・同一性

StatusQuo/v5のOwner指定ブランチ参照は作業開始時HEAD `0986799393e651caa4a106dbbf0a66fe12a3d870` に固定した。GitHubから取得した本文・blob・SHAを記録。旧損税入力・原本と検証は既存保存原本のSHA一致を再利用。JSONは原文を含み、原本を編集していない。

|入力原本|固定Commit|bytes|SHA-256|
|---|---|---:|---|
{src}

GitHub保存対象は `work/chatgpt-handoff` の `handoff/f-statusquo-provisional-20261115/` に指定4件＋入力JSON1件のみ。既存原本・main・正式エンジン・政策本文・旧v5・ビジュアル・DecisionLogは未変更。正式Acceptance、Finding Close、Freeze、Canonical化、新規RP・追加レビューなし。RP-023／M19–25 HOLD、RP-024 PENDING維持。引渡し後停止。
'''


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('inputs',type=Path);ap.add_argument('--outdir',type=Path,default=Path('.'));args=ap.parse_args()
    cfg=json.loads(args.inputs.read_text());rows,paths,logs=run(cfg,Path(__file__).resolve().parent)
    out=args.outdir;out.mkdir(parents=True,exist_ok=True);a=cfg['sq_bundle']['artifacts']
    csvpath=out/a['csv'];write_csv(csvpath,rows)
    reread=list(csv.DictReader(csvpath.open(encoding='utf-8',newline='')));assert len(reread)==240
    assert all(r['actual_bond_issuance_trn']=='' and r['primary_balance_trn']=='' for r in reread)
    logs.append('PASS saved CSV reread: 240 rows; missing bond/PB indicators remain blank')
    (out/a['report']).write_text(report(cfg,paths,logs,out),encoding='utf-8',newline='\n')
    for log in logs:print(log)
    print('rows=240; 7 paths + matched difference; years=2026..2055; exit=0')
    for case,rs in paths.items():
        r=rs[-1];print(case,'GDP2055=',r['real_gdp_trn'],'population=',r['population_persons'],'gap_proxy=',r['funding_gap_proxy_trn'])


if __name__=='__main__':main()
