#!/usr/bin/env python3
"""Offline provisional annual sonzei→macro bridge; no writes to existing SPE assets.
Run: python3 THIS.py INPUTS.json --outdir NEW_DIRECTORY
Standard library only. Annual money is trillion JPY unless explicitly specified.
"""
import argparse, copy, csv, hashlib, io, json, math, sys, types
from pathlib import Path

DATE='20261116'
CSV='SPE_F_Sonzei_Macro_ON_OFF_Annual_Comparison_DRAFT_'+DATE+'.csv'
REPORT='SPE_F_Sonzei_Macro_Connection_Run_Report_DRAFT_'+DATE+'.md'
def sha(b): return hashlib.sha256(b).hexdigest()
def module(name,text):
    m=types.ModuleType(name);sys.modules[name]=m
    exec(compile(text,'<pinned '+name+'>','exec'),m.__dict__);return m
def near(a,b): return math.isclose(a,b,rel_tol=2e-12,abs_tol=1e-8)
def require(ok,msg):
    if not ok: raise ValueError(msg)
def csv_bytes(rows):
    s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue().encode()
def prepare(cfg):
    for name,s in cfg['sources'].items():
        b=s['utf8'].encode();require(len(b)==s['bytes'] and sha(b)==s['sha256'],'Fixed source mismatch: '+name)
    for s in list(cfg['guidance_sources'].values())+[cfg['claude_verification_source']]:
        b=s['utf8'].encode();require(len(b)==s['bytes'] and sha(b)==s['sha256'],'Provenance source mismatch')
    src=cfg['sources']; oldcfg=json.loads(src['SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json']['utf8'])
    adapter=module('bridge_fixed_adapter',src['SPE_StatusQuo_Provisional_Model_DRAFT_20261115.py']['utf8'])
    son=module('bridge_fixed_v02',src['SPE_F_Sonzei_V02_Fixed_DRAFT_20261115.py']['utf8'])
    bundle=oldcfg['sq_bundle'];engine=module('bridge_engine',bundle['sources']['prototype.py']['utf8'])
    wage=module('bridge_wage',bundle['sources']['m14_wage_anchor.py']['utf8'])
    stored=list(csv.DictReader(io.StringIO(src['SPE_F_StatusQuo_Annual_Comparison_DRAFT_20261115.csv']['utf8'])))
    return oldcfg,adapter,son,engine,wage,stored

def adjusted_path(oldcfg,adapter,son,engine,wage,co):
    # Exact existing simulator, with only C/I annual add-ons scaled by explicit replacement share.
    c=copy.deepcopy(oldcfg)
    for key in ['consumption_stimulus','investment_promotion']:
        for r in c['sq_bundle']['f_config']['policy_effects_pct'][key]:r['value']*=1-co['legacy_CI_replacement_fraction']
    # simulate only needs the legacy diagnostic index for columns; do not rerun 1980 baseline tests.
    idx={}
    for guarded in [False,True]:
        for p,b in son.national_profiles(oldcfg,guarded):
            for y in range(2026,2056):idx[(p['id'],y)]=son.diagnose(oldcfg['policy'],p,b,y)
    return adapter.simulate(c,'F_2026_INITIAL_29',engine,wage,idx)

def sector_channels(oldcfg,son,y,co):
    details=[]
    for p,b in son.national_profiles(oldcfg,False):
        pol=copy.deepcopy(oldcfg['policy'])
        if p['sector']=='rental': pol['kappa']=co['rental_credit_fraction']
        d=son.diagnose(pol,p,b,y)
        # Do not silently replace unknown national compensation or housing rules.
        # Retain existing compensation unchanged; only explicit delta=0 enters bridge.
        required=['R','L_SQ','L_F','L_reduction','L_reduction_rate_part','L_reduction_credit_part',
                  'future_output_VAT_consumer_cost','future_output_VAT_public_cost','delta_tax_attribution_total']
        require(all(d[k] is not None for k in required),'Missing sector bridge input')
        x={k:d[k]/1e12 for k in required}
        require(co['historical_compensation_increment_assumption_trn']==0,'Nonzero compensation requires financing scope; unsupported')
        x['historical_compensation_change']=co['historical_compensation_increment_assumption_trn']
        x['sector']=p['sector'];x['started']=d['started_F']
        x['price_income_relief_trn']=co['household_pass_through']*x['L_reduction']
        x['business_retained_relief_trn']=(1-co['household_pass_through'])*x['L_reduction']
        x['household_net_cash_trn']=x['price_income_relief_trn']-x['future_output_VAT_consumer_cost']
        x['consumption_demand_trn']=co['mpc']*x['household_net_cash_trn']
        x['investment_demand_trn']=co['investment_share_of_retained']*x['business_retained_relief_trn']
        x['sector_net_consumer_wedge_pct']=(x['future_output_VAT_consumer_cost']-x['price_income_relief_trn'])/x['R']*100
        details.append(x)
    return details

def coefficients(cfg,overrides):
    c=dict(cfg['coefficients']);c.update(overrides)
    require(all(isinstance(v,(int,float)) and math.isfinite(v) for v in c.values()),'Nonfinite coefficient')
    for k in ['household_pass_through','mpc','investment_share_of_retained','domestic_demand_share',
              'legacy_CI_replacement_fraction','tax_elasticity_replacement_fraction','direct_sector_fiscal_coverage','rental_credit_fraction']:
        require(0<=c[k]<=1,'Coefficient out of range: '+k)
    require(c['demand_multiplier']>=0 and c['tax_elasticity_without_sonzei']>=0,'Negative coefficient')
    return c

def calculate(cfg,env,co,case):
    oldcfg,adapter,son,engine,wage,stored=env
    off=[r for r in stored if r['case']=='F_2026_INITIAL_29']
    adj=adjusted_path(oldcfg,adapter,son,engine,wage,co)
    rows=[];prev_nom=None;prev_real=None;ta=None;tb=None;tc=None
    for i,(o,a) in enumerate(zip(off,adj)):
        y=int(o['year']);apply=i>0;d=sector_channels(oldcfg,son,y,co)
        sums={k:sum(x[k] for x in d) for k in d[0] if isinstance(d[0][k],(int,float)) and k not in ['started','sector_net_consumer_wedge_pct']}
        # A flow in nominal yen is converted to real OUTPUT LEVEL via the same-year adjusted-path deflator.
        # Not a cumulative annual growth boost: each year's demand level replaces the preceding demand level.
        raw=(sums['consumption_demand_trn']+sums['investment_demand_trn'])*co['domestic_demand_share']*co['demand_multiplier']
        deflator=a['nominal_gdp_trn']/a['real_gdp_trn']
        demand_real=raw/deflator if apply else 0.0
        real=a['real_gdp_trn']+demand_real;nom=a['nominal_gdp_trn']+(raw if apply else 0.0)
        require(real>0 and nom>0,'Nonpositive GDP in bridge')
        oldel=float(o['tax_elasticity_scheduled'])
        el=oldel-co['tax_elasticity_replacement_fraction']*(oldel-co['tax_elasticity_without_sonzei'])
        if not apply:
            ta=tb=tc=float(o['tax_revenue_trn']);ng=rg=None
        else:
            ng=nom/prev_nom-1;rg=real/prev_real-1
            adjng=a['nominal_growth_pct']/100;event=float(o['tax_event_factor_applied'])
            # Separate recurrence ledgers so the direct annual VAT flow is NEVER compounded or passed through elasticity.
            ta=min(ta*(1+adjng*oldel)*event,a['nominal_gdp_trn']*.30)
            tb=min(tb*(1+adjng*el)*event,a['nominal_gdp_trn']*.30)
            tc=min(tc*(1+ng*el)*event,nom*.30)
        direct=co['direct_sector_fiscal_coverage']*co['tax_elasticity_replacement_fraction']*sums['delta_tax_attribution_total'] if apply else 0.0
        public=co['direct_sector_fiscal_coverage']*co['tax_elasticity_replacement_fraction']*sums['future_output_VAT_public_cost'] if apply else 0.0
        # Direct series is a sector-attribution PROXY, not a complete national/central treasury estimate.
        taxproxy=tc+direct;exproxy=a['expenditure_trn']+public
        r={'record_type':'PATH','case':case,'year':y,'scope':'NATIONAL_PLACEHOLDERS_PROVISIONAL_NOT_OBSERVED',
           'boundary':'2026_INITIAL_29_TRANSITIONS','row_kind':'INITIAL_STATE' if not apply else 'TRANSITION',
           'real_gdp_trn':real,'nominal_gdp_trn':nom,'real_growth_pct':None if rg is None else rg*100,
           'nominal_growth_pct':None if ng is None else ng*100,'tax_revenue_macro_trn':tc,
           'tax_revenue_plus_sector_attribution_proxy_trn':taxproxy,'expenditure_baseline_trn':a['expenditure_trn'],
           'expenditure_plus_output_VAT_public_proxy_trn':exproxy,
           'funding_gap_macro_proxy_trn':max(a['expenditure_trn']-tc,0),
           'funding_gap_with_sector_proxy_trn':max(exproxy-taxproxy,0),
           'annual_balance_with_sector_proxy_trn':taxproxy-exproxy,
           'population_persons':a['population_persons'],'births_persons':a['births_persons'],'deaths_persons':a['deaths_persons'],
           'actual_bond_issuance_trn':None,'primary_balance_trn':None,'CPI_pct':None,
           'risk_applied_pct':a['risk_applied_pct'],'event_names':a['event_names'],'events_applied':int(apply),
           'replacement_fraction_CI':co['legacy_CI_replacement_fraction'],'effective_tax_elasticity':el,
           'tax_elasticity_replacement_fraction':co['tax_elasticity_replacement_fraction'],
           'rental_credit_fraction_assumption':co['rental_credit_fraction'],
           'nominal_demand_level_trn':raw if apply else 0.0,'real_demand_level_trn':demand_real,'deflator_adjusted_path':deflator,
           'legacy_CI_GDP_adjustment_trn':a['real_gdp_trn']-float(o['real_gdp_trn']),
           'legacy_CI_tax_adjustment_trn':ta-float(o['tax_revenue_trn']),
           'elasticity_tax_adjustment_trn':tb-ta,'GDP_channel_tax_delta_trn':tc-tb,
           'direct_sector_VAT_attribution_applied_trn':direct,'output_VAT_public_cost_applied_trn':public,
           'net_direct_sector_fiscal_applied_trn':direct-public,
           'diagnostic_L_SQ_trn':sums['L_SQ'],'diagnostic_L_F_trn':sums['L_F'],
           'diagnostic_loss_reduction_trn':sums['L_reduction'],'diagnostic_rate_relief_trn':sums['L_reduction_rate_part'],
           'diagnostic_credit_relief_trn':sums['L_reduction_credit_part'],
           'price_income_relief_trn':sums['price_income_relief_trn'],
           'business_retained_relief_trn':sums['business_retained_relief_trn'],
           'household_net_cash_trn':sums['household_net_cash_trn'],
           'consumption_demand_trn':sums['consumption_demand_trn'],'investment_demand_trn':sums['investment_demand_trn'],
           'diagnostic_direct_sector_VAT_trn':sums['delta_tax_attribution_total'],
           'diagnostic_output_VAT_public_trn':sums['future_output_VAT_public_cost'],
           'compensation_change_assumed_trn':sums['historical_compensation_change'],
           'historical_compensation_level_trn':None,
           'diagnostic_applied_to_macro':int(apply),'wage_anchor_feedback':'UNCHANGED_EXTERNAL_WAGE_AFFECTS_BIRTHS;NO_NEW_MACRO_FEEDBACK'}
        for x in d:
            for k in ['L_reduction','price_income_relief_trn','household_net_cash_trn','consumption_demand_trn','investment_demand_trn',
                      'future_output_VAT_consumer_cost','future_output_VAT_public_cost','delta_tax_attribution_total','sector_net_consumer_wedge_pct']:
                r[x['sector']+'_'+(k if k.endswith(('_trn','_pct')) else k+'_trn')]=x[k]
        prev_nom,prev_real=nom,real;rows.append(r)
    return rows

CORE=['real_gdp_trn','nominal_gdp_trn','tax_revenue_macro_trn','tax_revenue_plus_sector_attribution_proxy_trn',
      'expenditure_baseline_trn','expenditure_plus_output_VAT_public_proxy_trn','funding_gap_macro_proxy_trn',
      'funding_gap_with_sector_proxy_trn','annual_balance_with_sector_proxy_trn','population_persons','births_persons','deaths_persons']
def baseline_rows(stored,case,template):
    rs=[]
    for s in stored:
        if s['case']!=case:continue
        r={k:None for k in template};r.update(record_type='PATH',case='OFF_F' if case.startswith('F_') else 'REF_STATUSQUO_V5',year=int(s['year']),scope='EXISTING_FIXED_BASELINE',boundary=s['boundary'],row_kind=s['row_kind'],event_names=s['event_names'],events_applied=int(s['events_applied']),risk_applied_pct=float(s['risk_applied_pct']))
        for k in ['real_gdp_trn','nominal_gdp_trn','population_persons','births_persons','deaths_persons']:r[k]=float(s[k])
        for k in ['real_growth_pct','nominal_growth_pct']:r[k]=None if s[k]=='' else float(s[k])
        r['tax_revenue_macro_trn']=r['tax_revenue_plus_sector_attribution_proxy_trn']=float(s['tax_revenue_trn'])
        r['expenditure_baseline_trn']=r['expenditure_plus_output_VAT_public_proxy_trn']=float(s['expenditure_trn'])
        r['funding_gap_macro_proxy_trn']=r['funding_gap_with_sector_proxy_trn']=float(s['funding_gap_proxy_trn'])
        r['annual_balance_with_sector_proxy_trn']=float(s['tax_revenue_trn'])-float(s['expenditure_trn'])
        rs.append(r)
    return rs

def difference(a,b,label):
    out=[]
    for x,y in zip(a,b):
        r={k:None for k in x};r.update(record_type='DIFFERENCE',case=label,year=x['year'],scope='PAIRED_CASE_DIFFERENCE_NOT_ADDITIVE_PATH',boundary=x['boundary'],row_kind='YEAR_DIFFERENCE')
        for k in CORE:r[k]=x[k]-y[k]
        out.append(r)
    return out

def checks(cfg,env,paths,allrows):
    log=[]
    def ok(msg):log.append('PASS '+msg)
    off=paths['OFF_F'];stored=env[-1]
    src=[r for r in stored if r['case']=='F_2026_INITIAL_29']
    for x,s in zip(off,src):
        for k in ['real_gdp_trn','nominal_gdp_trn','population_persons','births_persons','deaths_persons']:require(x[k]==float(s[k]),'OFF changed')
        require(x['tax_revenue_macro_trn']==float(s['tax_revenue_trn']) and x['expenditure_baseline_trn']==float(s['expenditure_trn']),'OFF fiscal changed')
    # A new zero-bridge path uses the actual simulator, not just a copy of stored OFF.
    for a,b in zip(paths['ON_ZERO_CHANNEL_NO_REPLACEMENT'],off):
        for k in CORE:require(near(a[k],b[k]),'Zero bridge mismatch '+k)
    ok('OFF unchanged; actual zero-channel simulator reproduces fixed F in all core fields')
    for case,rs in paths.items():
        require([r['year'] for r in rs]==list(range(2026,2056)),'Year discontinuity')
        for i,r in enumerate(rs):
            require(all(math.isfinite(r[k]) for k in CORE),'Nonfinite core output')
            require(r['actual_bond_issuance_trn'] is None and r['primary_balance_trn'] is None and r['CPI_pct'] is None,'Unknown filled')
            if case.startswith('ON_'):
                require(near(r['tax_revenue_plus_sector_attribution_proxy_trn']-off[i]['tax_revenue_macro_trn'],sum(r[k] for k in ['legacy_CI_tax_adjustment_trn','elasticity_tax_adjustment_trn','GDP_channel_tax_delta_trn','direct_sector_VAT_attribution_applied_trn'])),'Tax decomposition does not close')
                require(near(r['real_gdp_trn']-off[i]['real_gdp_trn'],r['legacy_CI_GDP_adjustment_trn']+r['real_demand_level_trn']),'GDP decomposition')
                require(r['risk_applied_pct']==off[i]['risk_applied_pct'] and r['event_names']==off[i]['event_names'],'Event changed')
                require(r['population_persons']==off[i]['population_persons'],'Unspecified population feedback')
                require(near(r['diagnostic_loss_reduction_trn'],r['diagnostic_rate_relief_trn']+r['diagnostic_credit_relief_trn']),'Relief split')
                require(near(r['price_income_relief_trn']+r['business_retained_relief_trn'],r['diagnostic_loss_reduction_trn']),'Incidence double count')
    ok('All paths 30 continuous years; fixed initial conditions/events/population; missing CPI/bond/PB stay unknown')
    ok('GDP/tax decompositions close; total relief allocated once between households and firms')
    for r in allrows:
        if r['record_type']=='DIFFERENCE':
            left,right=r['case'].split('_MINUS_')
            a=paths[left][r['year']-2026];b=paths[right][r['year']-2026]
            for k in CORE:require(r[k]==a[k]-b[k],'Difference error')
    ok('All ON−OFF and MAIN−StatusQuo differences computed from paired outputs')
    oldcfg,adapter,son,*_=env
    co=coefficients(cfg,{})
    ds=sector_channels(oldcfg,son,2040,co)
    for d in ds:
        p,b=next((p,b) for p,b in son.national_profiles(oldcfg,False) if p['sector']==d['sector'])
        po=copy.deepcopy(oldcfg['policy']);po['kappa']=0 if p['sector']=='rental' else po['kappa']
        x=son.diagnose(po,p,b,2040)
        require(near(d['L_reduction']*1e12,x['L_reduction']),'JPY/trillion conversion')
    ok('JPY→trillion conversion matches original diagnostic; no per-facility or alternate cases summed')
    require(paths['ON_RENTAL_FULL_CREDIT'][14]['diagnostic_loss_reduction_trn']>paths['ON_MAIN'][14]['diagnostic_loss_reduction_trn'],'Housing endpoint not distinct')
    require(paths['ON_HIGH_RESPONSE'][14]['real_demand_level_trn']!=paths['ON_LOW_RESPONSE'][14]['real_demand_level_trn'],'Sensitivity overwritten')
    require(all(r['direct_sector_VAT_attribution_applied_trn']==0 for r in paths['ON_RETAIN_ELASTICITY_NO_DIRECT_VAT']),'Direct VAT double count with retained elasticity')
    ok('Rental and coefficient sensitivities distinct; retaining old elasticity suppresses direct VAT addition')
    # Test level-vs-growth semantics: a constant demand injection produces a constant LEVEL uplift,
    # and the difference of the level contributes to next-year nominal growth (no repeated flow accumulation).
    a=100.;growth=.02;constant=2.;y1=a*(1+growth)+constant;y2=a*(1+growth)**2+constant
    require(near(y2-(a*(1+growth)**2),constant),'Demand flow accumulated')
    require(y2!=y1*(1+growth)+constant,'Annual flow treated as cumulative growth')
    ok('Annual demand enters output LEVEL; not cumulatively re-added as a permanent growth-rate increment')
    # Missing input must raise instead of zero-fill.
    bad=copy.deepcopy(oldcfg);bad['prototype_config']['sectors']['medical']['R_2025']['value']=None
    try:sector_channels(bad,son,2040,co)
    except (TypeError,ValueError):pass
    else:raise AssertionError('Missing sector input silently filled')
    ok('Missing sector input rejected; true zero used only in explicit endpoint assumptions')
    return log

def report(cfg,paths,logs,rows):
    head='|年|OFF実質GDP|ON実質GDP|ON−OFF|ONマクロ税収|ON税収＋部門proxy|ON歳出＋公費proxy|ON資金不足proxy|\n|---|---:|---:|---:|---:|---:|---:|---:|'
    tbl=[]
    for y in [2026,2028,2031,2035,2040,2055]:
        a=paths['ON_MAIN'][y-2026];b=paths['OFF_F'][y-2026]
        tbl.append('|'+str(y)+'|'+'|'.join(f'{v:.6f}' for v in [b['real_gdp_trn'],a['real_gdp_trn'],a['real_gdp_trn']-b['real_gdp_trn'],a['tax_revenue_macro_trn'],a['tax_revenue_plus_sector_attribution_proxy_trn'],a['expenditure_plus_output_VAT_public_proxy_trn'],a['funding_gap_with_sector_proxy_trn']])+'|')
    endpoints=['|ケース|実質GDP|対OFF差|需要水準効果|既存C/I置換効果|マクロ税収|税収＋部門proxy|資金不足proxy|','|---|---:|---:|---:|---:|---:|---:|---:|']
    for k,rs in paths.items():
        a=rs[-1];off=paths['OFF_F'][-1]
        vals=[a['real_gdp_trn'],a['real_gdp_trn']-off['real_gdp_trn'],a['real_demand_level_trn'],a['legacy_CI_GDP_adjustment_trn'],a['tax_revenue_macro_trn'],a['tax_revenue_plus_sector_attribution_proxy_trn'],a['funding_gap_with_sector_proxy_trn']]
        endpoints.append('|'+k+'|'+'|'.join('未適用' if v is None else f'{v:.6f}' for v in vals)+'|')
    coef='\n'.join('|'+k+'|'+str(v)+'|'+cfg['coefficient_basis'][k]+'|' for k,v in cfg['coefficients'].items())
    src='\n'.join('|'+k+'|'+str(s['bytes'])+'|`'+s['sha256']+'`|' for k,s in cfg['sources'].items())
    sensitivity='\n'.join('- `'+x['id']+'`: '+json.dumps(x['overrides'],ensure_ascii=False) for x in cfg['cases'])
    return f'''# SPE｜F損税マクロ接続・年次計算・ON／OFF比較

Status: DRAFT / PROVISIONAL / NON-CANONICAL  
作成日: 2026-11-16（Asia/Tokyo）  
対象: 2026〜2055年、2026初期状態＋29回遷移。単位: 金額は兆円、人口は人。丸め表示とCSV原精度を区別する。

## 新しくできるようになったこと

3部門の損税率低下・控除差額→価格/所得への帰着→家計需要・企業投資→実質GDP水準→名目GDP・税収弾性計算へ接続し、ON／OFFと感度ケースを実行した。部門の直接VAT帰属・output VAT公費負担を別勘定で追加し、財政関連proxyを計算した。既存OFF再現だけでなく、新たに需要経路と既存外生効果の置換を分解できる。

**主ONは例示的な係数セットであり、最良推定・Ownerが確定した政策係数ではない。** 主ONのGDP差には、損税の新しい需要効果だけでなく、既存Fの消費/投資加算項を25%取り除いた効果が含まれる。税収差には旧弾性を1へ置換する効果を含む。ON−OFFの全差を「損税解消の因果効果」と呼ばない。符号がマイナスでもそのまま掲載する。

## 固定入力と既存PASS

基準5原本はCommit `{cfg['base_commit']}`、`{cfg['base_directory']}`。既存Workの固定Commit再取得・SHA一致とClaude `{cfg['independent_verification_commit']}` の240行・1470セル検証PASSを再利用する（今回の自己実測と混同しない）。今回使用したローカル5原本のサイズ・SHAを照合し、入力JSONへ原文を格納した。OFFは保存済みF主結果を使用し、ゼロ接続ケースは実際の既存シミュレータで再計算して一致を確認した。過去1980行全検査を新規工程として再実施していない。

|原本|bytes|SHA-256|
|---|---:|---|
{src}

Owner方針3文書は`work/chatgpt-handoff`からGitHub連携で取得、読取時HEAD `{cfg['guidance_commit']}`。参照パスは入力JSONの`guidance_paths`。Claude独立検証も指定固定Commitから取得・読取。方針を新規承認ゲートへ変換していない。

## 接続式・二重計上調整

```text
ΔL = (inputVAT_SQ−credit_SQ)−(inputVAT_F−credit_F)
household_relief = θ×ΔL
firm_retained = (1−θ)×ΔL
private_output_VAT = outputVAT_F×(1−public_share)
ΔC = MPC×(household_relief−private_output_VAT)
ΔI = investment_share×firm_retained
nominal_demand_level = multiplier×domestic_share×(ΔC+ΔI)
real_demand_level = nominal_demand_level / adjusted_path_deflator
adjusted_legacy_C = original_C×(1−CI_replacement_fraction)
adjusted_legacy_I = original_I×(1−CI_replacement_fraction)
GDP_ON = GDP_adjusted_legacy + real_demand_level
nominalGDP_ON = nominalGDP_adjusted_legacy + nominal_demand_level
elasticity_ON = original_elasticity−replacement_fraction×(original_elasticity−anchor)
tax_macro_ON_t = min(tax_macro_ON_(t−1)×(1+ON_nominal_growth×elasticity_ON)×event_factor, nominalGDP_ON×.30)
direct_VAT_applied = coverage×elasticity_replacement_fraction×sector_VAT_attribution_delta
public_applied = coverage×elasticity_replacement_fraction×future_output_VAT_public_cost
tax_plus_sector_proxy = tax_macro_ON + direct_VAT_applied
expenditure_plus_public_proxy = original_expenditure + public_applied
funding_gap_proxy = max(expenditure_plus_public_proxy−tax_plus_sector_proxy,0)
```

損税解消額をそのままGDPへ等置していない。価格/所得帰着θ、消費性向、投資配分、国内需要比、乗数を経由する。家計と企業へのΔL配分は合計1であり、同じ控除を両方へ全額配賦しない。消費負担増は負号で残す。残留利益の未投資部分をGDPへ加算しない。投資の将来資本ストック・生産性波及は未実装で、当期需要だけを計上する。

新しい需要は各年のGDP**水準**へ入れる。同一の毎年の損税フローを毎年GDP成長率へ累積加算しない。名目GDPから導く実際の成長率を税収へ渡す。価格・所得経路は消費者の現金購買力/部門売上に対する負担率として出力し、CPIは未算出。既存インフレ/リスクと人口・賃金→出生を保持し、新たな賃金/人口フィードバックを創作しない。

消費/投資の既存加算と重なる割合は未同定のため、主25%、感度0%/100%を計算。教育加算は変更しない（教育部門の損税による投資需要と教育生産性スケジュールは別経路として保持、真の独立性は未実証）。主税収弾性は**単位弾性1**を基準に旧Fの上乗せを置換し、部門VAT帰属を別に計上する。1.5を基準に残す感度は上乗せに未同定の重複が残りうる。旧弾性を維持する感度では直接VAT追加と対応公費追加をともに停止し、二重計上を抑制する。これらは重複の真の大きさを証明する調整ではなく、明示的な暫定置換である。

税収分解は①C/I置換による税収差、②弾性置換による税収差、③新GDP経路による税収差、④部門直接VAT帰属を別列に保持し合計一致を確認した。直接VATは当年フローであり、翌年の弾性計算の元税収に入れず再複利しない。GDP30%capは**マクロ税収勘定のみ**。後段の部門加算proxyに同じcapを再適用して差を隠さない。

## 暫定係数の根拠と感度

政策方向（税率5%への低下・課税ベース拡大）と以下の新規暫定値は別である。公的統計から係数を実証したとは称さず、既存θ以外の需要係数は例示的な予算配分・漏出/乗数仮定。

|係数|主値|根拠・区分|
|---|---:|---|
{coef}

感度ケース（同時に合算しない）:
{sensitivity}

住宅は控除条件・建物/経常費用の構成が未確定。主ケースは混合P全体で控除0、上側端点は全額とする**計算上の仮定**で、現行法/将来制度の控除認定ではない。既存guarded原本の未検証をPASSへ変えていない。部門R/PはClaudeの暫定全国値・年率2%経路を利用し、91行の部分実測ケースを全国合計へ混ぜない。診療報酬の既存補填の水準は未取得のまま、変更なしと置いた差額0のみ使用し、公費shareを発明して補填削減を計上しない。

## 主要年の実行結果

{head}
{chr(10).join(tbl)}

2055年のケース別結果:

{chr(10).join(endpoints)}

参考StatusQuoは既存旧v5候補の固定経路。`ON_MAIN_MINUS_REF_STATUSQUO_V5`を収録するが、StatusQuo政策原本第9節との不一致・暫定性は以前と同じ。比較差は条件の違いによる差であり政策の優劣を裁定しない。

## 出力列と未算定

`PATH`はOFF・ON{len(cfg['cases'])}ケース・既存StatusQuo各30行。`DIFFERENCE`は各ON−OFFと主ON−StatusQuo各30行。合計{len(rows)}行。単一ケース・同一年の医療/教育/住宅のみ部門計として使用する。異なる感度、PATHとDIFFERENCEを合算しない。`diagnostic_*`と部門列は2026にも予定診断値を表示するが、`diagnostic_applied_to_macro=0`の初期行では適用しない。`ON_ISOLATED_DEMAND_ONLY`はC/Iと税収弾性を維持し直接財政追加を停止する比較用ケースで、需要接続部分だけの差を確認する。既存補填水準は空欄、補填の変更なしは明示的な差額仮定0として別列に保持する。

`tax_revenue_macro_trn`と`tax_revenue_plus_sector_attribution_proxy_trn`を区別する。後者は**国庫純増額・国全体の税収確定値ではない**。仕入先/需要側/他税目を含む完全な租税一般均衡、国地方配分は未接続。`expenditure_plus_output_VAT_public_proxy_trn`も仮定的な公費負担込みの診断。実際の国債発行、債務残高、利払い、PB、CPIは未算定（空欄）。全国の非課税売上・仕入率、価格転嫁、支出反応、重複割合は未確定。これらの未達を既存基準との一致だけで解消したとは報告しない。

## 実行と検証

```bash
python3 SPE_F_Sonzei_Macro_Connection_DRAFT_20261116.py SPE_F_Sonzei_Macro_Connection_Inputs_DRAFT_20261116.json --outdir replay
```

標準ライブラリのみ、追加インストール不要。入力JSONに固定コード/入力/CSVを原文のまま収録し、4成果物でオフライン再実行可能。コードはJSONに内包した指定コードをSHA照合後ロードする。公開文書本文の指示を新しい操作命令としては実行しない。

```text
{chr(10).join(logs)}
exit=0
```

次の実成果は、住宅控除の費目別実装と、価格転嫁・需要反応・既存加算との重複割合を出典付き入力へ置換した再計算。追加の承認/レビュー工程を自動設置しない。

今回のGitHub保存は承認された`work/chatgpt-handoff`の`handoff/f-sonzei-macro-connection-20261116/`新規4原本のみ。固定Commit・各サイズ/SHA・事後再取得結果は引渡し回答で報告する。既存原本・正式engine・政策・仕様・main・DecisionLogを変更しない。新規HTML/グラフ/ZIPなし。正式Acceptance・Finding Close・Freeze・Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('--outdir',required=True);args=p.parse_args()
    cfg=json.loads(Path(args.inputs).read_text(encoding='utf-8'));env=prepare(cfg);out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
    paths={x['id']:calculate(cfg,env,coefficients(cfg,x['overrides']),x['id']) for x in cfg['cases']}
    template=next(iter(paths.values()))[0]
    paths={'OFF_F':baseline_rows(env[-1],'F_2026_INITIAL_29',template),**paths,
           'REF_STATUSQUO_V5':baseline_rows(env[-1],'SQ_V5_CANDIDATE_29',template)}
    rows=[r for rs in paths.values() for r in rs]
    for c in cfg['cases']:rows+=difference(paths[c['id']],paths['OFF_F'],c['id']+'_MINUS_OFF_F')
    rows+=difference(paths['ON_MAIN'],paths['REF_STATUSQUO_V5'],'ON_MAIN_MINUS_REF_STATUSQUO_V5')
    logs=checks(cfg,env,paths,rows)
    payload=csv_bytes(rows);(out/CSV).write_bytes(payload)
    reread=list(csv.DictReader(io.StringIO((out/CSV).read_text())))
    require(len(reread)==len(rows) and all(r['actual_bond_issuance_trn']==r['primary_balance_trn']==r['CPI_pct']=='' for r in reread),'Saved CSV missing mismatch')
    logs.append('PASS saved CSV reread; rows='+str(len(rows))+'; unknown fields preserved')
    (out/REPORT).write_text(report(cfg,paths,logs,rows),encoding='utf-8')
    print('\n'.join(logs));print('exit=0; CSV SHA256='+sha(payload))
    for c in ['OFF_F','ON_MAIN','ON_NO_CI_REPLACEMENT','ON_FULL_CI_REPLACEMENT','REF_STATUSQUO_V5']:
        print(c,json.dumps({k:paths[c][-1][k] for k in ['real_gdp_trn','tax_revenue_macro_trn','tax_revenue_plus_sector_attribution_proxy_trn','funding_gap_with_sector_proxy_trn']},ensure_ascii=False))
if __name__=='__main__':main()
