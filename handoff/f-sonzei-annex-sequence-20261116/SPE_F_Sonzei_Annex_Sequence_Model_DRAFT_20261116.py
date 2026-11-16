#!/usr/bin/env python3
"""Offline Annex-sequenced F bridge; provisional, no existing SPE asset is edited.
python3 THIS.py INPUTS.json --outdir NEW_DIRECTORY
Only Python standard library. Annual monetary columns are trillion JPY.
"""
import argparse,copy,csv,hashlib,io,json,math,types,sys
from pathlib import Path

OUTCSV='SPE_F_Sonzei_Annex_Annual_Comparison_DRAFT_20261116.csv'
OUTMD='SPE_F_Sonzei_Annex_Run_Report_DRAFT_20261116.md'
def check(ok,msg):
    if not ok:raise ValueError(msg)
def close(a,b):return math.isclose(a,b,rel_tol=2e-12,abs_tol=1e-8)
def digest(b):return hashlib.sha256(b).hexdigest()
def prepare(c):
    for n,s in c['sources'].items():
        b=s['utf8'].encode();check(len(b)==s['bytes'] and digest(b)==s['sha256'],'Source mismatch '+n)
    source=c['sources']
    old=json.loads(source['SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json']['utf8'])
    raw=list(csv.DictReader(io.StringIO(source['SPE_F_StatusQuo_Annual_Comparison_DRAFT_20261115.csv']['utf8'])))
    off=[]
    for r in raw:
        if r['case']!='F_2026_INITIAL_29':continue
        x={k:float(r[k]) for k in ['real_gdp_trn','nominal_gdp_trn','tax_revenue_trn','expenditure_trn','population_persons','births_persons','deaths_persons']}
        for k in ['real_growth_pct','nominal_growth_pct','inflation_pct','base_growth_scheduled_pct','consumption_effect_scheduled_pp','investment_effect_scheduled_pp','education_effect_scheduled_pp','labor_force_growth_pct','risk_applied_pct','tax_elasticity_scheduled','tax_event_factor_applied']:
            x[k]=None if r[k]=='' else float(r[k])
        x['year']=int(r['year']);x['event_names']=r['event_names'];off.append(x)
    m=types.ModuleType('pinned_v02_sequence');sys.modules[m.__name__]=m
    exec(compile(source['SPE_F_Sonzei_V02_Fixed_DRAFT_20261115.py']['utf8'],'<fixed V02>','exec'),m.__dict__)
    # Original national placeholder paths are reused. No 91-row partial-case aggregation.
    return old,off,m
def settings(cfg,spec):
    s=copy.deepcopy(cfg['schedule']);c=dict(cfg['coefficients'])
    for k,v in spec.get('schedule',{}).items():
        if isinstance(v,dict):s[k].update(v)
        else:s[k]=v
    c.update(spec.get('coefficients',{}))
    check(2026<=s['year8']<s['year5']<=2055,'Require year8 < year5 in horizon')
    check(s['benefit_start']<s['year8'] and s['benefit_end']>=s['benefit_start'],'Benefit must lead tax reduction')
    for z in ['medical','education','rental']:
        check(s['sector_starts'][z]>=s['year5'],'Base expansion before 5%: '+z)
        check(isinstance(s['phase_years'][z],int) and s['phase_years'][z]>=1,'Invalid phase')
    for k in ['household_pass_through','mpc','investment_share','domestic_share','legacy_CI_overlap','elasticity_overlap','benefit_already_in_legacy_share','direct_fiscal_inclusion','rental_credit_fraction']:
        check(math.isfinite(c[k]) and 0<=c[k]<=1,'Invalid fraction '+k)
    check(c['multiplier']>=0 and c['elasticity_anchor']>=0 and s['benefit_trn']>=0,'Negative assumption')
    return s,c
def rate(y,s):return .10 if y<s['year8'] else .08 if y<s['year5'] else .05
def phase(y,s,z):return max(0.,min(1.,(y-s['sector_starts'][z]+1)/s['phase_years'][z]))
def channels(old,son,y,s,c):
    # Reuse fixed V02 diagnosis at the requested rate, then phase output VAT and credit
    # together. A zero phase leaves current exemption intact, not just a nominal start flag.
    tau=rate(y,s);policy=copy.deepcopy(old['policy'])
    policy['tax_F_points']={'2026':tau,'2055':tau};theta=c['household_pass_through']
    d={};details=[]
    for p,b in son.national_profiles(old,False):
        pol=copy.deepcopy(policy);z=p['sector'];pol['start_years'][z]=s['sector_starts'][z]
        # Counterfactual endpoint only: not a legal finding on residential buildings.
        pol['kappa']=c['rental_credit_fraction'] if z=='rental' else 1.
        x=son.diagnose(pol,p,b,y);q=phase(y,s,z)
        check(all(x[k] is not None for k in ['R','P_net','input_VAT_SQ','input_VAT_F','input_credit_F']),'Unknown sector input')
        R=x['R']/1e12;P=x['P_net']/1e12
        # SQ credit remains the pinned 0; reject future nonzero assumptions until separated.
        check(old['policy']['current_exempt_activity_input_credit']==0,'Nonzero SQ credit requires explicit phase contract')
        rr=(x['input_VAT_SQ']-x['input_VAT_F'])/1e12
        cc=q*x['input_credit_F']/1e12
        out=q*tau*R;public=old['policy']['phi'][z]*out
        private=out-public
        x={'sector':z,'phase':q,'rate':tau,'R':R,
           'rate_relief_trn':rr,'credit_relief_trn':cc,
           'price_income_rate_trn':theta*rr,'price_income_credit_trn':theta*cc,
           'business_rate_trn':(1-theta)*rr,'business_credit_trn':(1-theta)*cc,
           'rate_C_trn':c['mpc']*theta*rr,'rate_I_trn':c['investment_share']*(1-theta)*rr,
           'credit_C_trn':c['mpc']*theta*cc,'credit_I_trn':c['investment_share']*(1-theta)*cc,
           'private_VAT_C_trn':-c['mpc']*private,
           'output_VAT_trn':out,'private_VAT_trn':private,'public_VAT_trn':public,
           'rate_tax_trn':-rr,'base_tax_trn':out-cc}
        details.append(x)
    for k in ['rate_relief_trn','credit_relief_trn','price_income_rate_trn','price_income_credit_trn','business_rate_trn','business_credit_trn','rate_C_trn','rate_I_trn','credit_C_trn','credit_I_trn','private_VAT_C_trn','output_VAT_trn','private_VAT_trn','public_VAT_trn','rate_tax_trn','base_tax_trn']:
        d[k]=sum(x[k] for x in details)
    Ps={z:old['prototype_config']['sectors'][z]['R_2025']['value']*old['prototype_config']['sectors'][z]['p_ratio']['value'] for z in ['medical','education','rental']}
    # Weights derive from fixed P, not facility counts. Zero assumed rental credit
    # gives no sonzei-replacement weight even when output VAT has started.
    d['active_weight']=sum(Ps[z]*phase(y,s,z)*(c['rental_credit_fraction'] if z=='rental' else 1.) for z in Ps)/sum(Ps.values())
    d['benefit_trn']=s['benefit_trn'] if s['benefit_start']<=y<=s['benefit_end'] else 0.
    d['benefit_C_trn']=c['mpc']*d['benefit_trn']
    d['benefit_residual_C_trn']=d['benefit_C_trn']*(1-c['benefit_already_in_legacy_share'])
    return d

def simulate(env,s,c):
    old,off,_=env;f=old['sq_bundle']['f_config'];prevR=off[0]['real_gdp_trn'];prevN=off[0]['nominal_gdp_trn']
    taxCI=taxE=off[0]['tax_revenue_trn'];parts={}
    # Target demand channels are LEVELs; separate GDP contributions, not recurring growth shocks.
    for y in range(2026,2056):
        o=off[y-2026];
        d=channels(old,env[2],y,s,c)
        rho=c['legacy_CI_overlap']*d['active_weight'];erho=c['elasticity_overlap']*d['active_weight']
        lam=o['tax_elasticity_scheduled'];eff=lam-erho*(lam-c['elasticity_anchor'])
        R,N=prevR,prevN
        if y>2026:
            g=(o['base_growth_scheduled_pct']+(1-rho)*o['consumption_effect_scheduled_pp']+(1-rho)*o['investment_effect_scheduled_pp']+o['education_effect_scheduled_pp']-o['risk_applied_pct']+.65*o['labor_force_growth_pct'])/100
            R=prevR*(1+g);N=prevN*(1+g+o['inflation_pct']/100)
            ng=N/prevN-1
            taxCI=min(taxCI*(1+ng*lam)*o['tax_event_factor_applied'],N*.30)
            taxE=min(taxE*(1+ng*eff)*o['tax_event_factor_applied'],N*.30)
        parts[y]={'adjusted_real':R,'adjusted_nominal':N,'tax_CI':taxCI,'tax_E':taxE,'rho':rho,'erho':erho,'eff':eff,'d':d}
        prevR,prevN=R,N
    newtax=off[0]['tax_revenue_trn'];lastN=off[0]['nominal_gdp_trn'];rs=[]
    for y in range(2026,2056):
        o=off[y-2026];x=parts[y];d=x['d'];apply=y>2026
        factor=c['domestic_share']*c['multiplier']
        # 1 trillion cash × no model-dependent empirical multiplier assumption.
        ns={'benefit':factor*d['benefit_residual_C_trn'],'rate':factor*(d['rate_C_trn']+d['rate_I_trn']),
            'credit':factor*(d['credit_C_trn']+d['credit_I_trn']),'burden':factor*d['private_VAT_C_trn']}
        for k in ns:
            if not apply:ns[k]=0.
        D=x['adjusted_nominal']/x['adjusted_real'];re={k:v/D for k,v in ns.items()}
        real=x['adjusted_real']+sum(re.values());nom=x['adjusted_nominal']+sum(ns.values())
        if apply:newtax=min(newtax*(1+(nom/lastN-1)*x['eff'])*o['tax_event_factor_applied'],nom*.30)
        # Not a consolidated national revenue claim. Base no direct inclusion because
        # the old F elasticity's direct reform component is unidentified.
        dt=c['direct_fiscal_inclusion']*(d['rate_tax_trn']+d['base_tax_trn']) if apply else 0.
        pc=c['direct_fiscal_inclusion']*d['public_VAT_trn'] if apply else 0.
        # Full grants are explicit budget expenditure even if demand is already embedded.
        # Incremental fiscal treatment is a separately disclosed provisional assumption.
        bene=d['benefit_trn'] if apply else 0.
        tp=newtax+dt;ep=o['expenditure_trn']+pc+bene
        r={'case':None,'record_type':'PATH','year':y,'boundary':'2026_INITIAL_29','scope':'THREE_SECTOR_NATIONAL_PLACEHOLDERS',
           'real_gdp_trn':real,'nominal_gdp_trn':nom,'tax_revenue_macro_trn':newtax,
           'tax_plus_diagnostic_trn':tp,'expenditure_plus_diagnostic_trn':ep,'funding_gap_proxy_trn':max(ep-tp,0),
           'real_gdp_delta_trn':real-o['real_gdp_trn'],'tax_macro_delta_trn':newtax-o['tax_revenue_trn'],
           'GDP_CI_adjustment_trn':x['adjusted_real']-o['real_gdp_trn'],
           'GDP_benefit_trn':re['benefit'],'GDP_rate_partial_trn':re['rate'],'GDP_credit_trn':re['credit'],'GDP_private_burden_trn':re['burden'],
           'tax_CI_adjustment_trn':x['tax_CI']-o['tax_revenue_trn'],
           'tax_elasticity_adjustment_trn':x['tax_E']-x['tax_CI'],'tax_GDP_channel_trn':newtax-x['tax_E'],
           'direct_tax_applied_trn':dt,'direct_public_applied_trn':pc,
           'standard_tax_rate':rate(y,s),'food_transitional_tax_rate':None,
           'CI_fraction_applied':x['rho'],'elasticity_fraction_applied':x['erho'],
           'effective_tax_elasticity':x['eff'],
           'population_persons':o['population_persons'],'births_persons':o['births_persons'],'deaths_persons':o['deaths_persons'],
           'event_names':o['event_names'],'risk_applied_pct':o['risk_applied_pct'],
           'actual_bond_issuance_trn':None,'debt_stock_trn':None,'PB_trn':None,'CPI_pct':None,
           'general_tax_beyond_three_sectors_trn':None,
           'price_income_relief_trn':d['price_income_rate_trn']+d['price_income_credit_trn'],
           'business_relief_trn':d['business_rate_trn']+d['business_credit_trn'],
           'household_net_cash_trn':d['price_income_rate_trn']+d['price_income_credit_trn']-d['private_VAT_trn'],
           'consumer_burden_trn':d['private_VAT_trn'],'retained_relief_trn':d['business_rate_trn']+d['business_credit_trn'],
           'consumption_total_trn':d['rate_C_trn']+d['credit_C_trn']+d['private_VAT_C_trn'],
           'investment_total_trn':d['rate_I_trn']+d['credit_I_trn']}
        for k in ['rate_relief_trn','credit_relief_trn','benefit_trn','benefit_C_trn','benefit_residual_C_trn','output_VAT_trn','private_VAT_trn','public_VAT_trn','rate_tax_trn','base_tax_trn']:
            r[k]=d[k]
        # Event markers include every overlapping policy, not just the first one.
        events=[]
        if y==s['benefit_start']:events.append('BENEFIT_START')
        if y==s['benefit_end']+1:events.append('BENEFIT_END')
        if y==s['year8']:events.append('STANDARD_8')
        if y==s['year5']:events.append('STANDARD_5')
        for z in ['medical','education','rental']:
            if y==s['sector_starts'][z]:events.append('BASE_START_'+z)
            r[z+'_phase']=phase(y,s,z)
        r['policy_events']=';'.join(events)
        lastN=nom;rs.append(r)
    return rs

def baseline(off,template):
    rows=[]
    for o in off:
        r={k:None for k in template};r.update(case='OFF_F',record_type='PATH',year=o['year'],boundary='2026_INITIAL_29',scope='EXISTING_FIXED_F',real_gdp_trn=o['real_gdp_trn'],nominal_gdp_trn=o['nominal_gdp_trn'])
        r['tax_revenue_macro_trn']=r['tax_plus_diagnostic_trn']=o['tax_revenue_trn']
        r['expenditure_plus_diagnostic_trn']=o['expenditure_trn'];r['funding_gap_proxy_trn']=max(o['expenditure_trn']-o['tax_revenue_trn'],0)
        r['real_gdp_delta_trn']=r['tax_macro_delta_trn']=0
        for k in ['population_persons','births_persons','deaths_persons','event_names','risk_applied_pct']:r[k]=o[k]
        rows.append(r)
    return rows

def checks(c,env,paths):
    logs=[]
    def ok(s):logs.append('PASS '+s)
    a=paths['ANNEX_BASE']
    for spec in c['cases']:
        s,co=settings(c,spec);rs=paths[spec['id']]
        check([r['year'] for r in rs]==list(range(2026,2056)),'Year gap')
        for r in rs:
            y=r['year'];check(r['standard_tax_rate'] in [.05,.08,.10],'Wrong tax rate')
            if y<s['year5']:
                check(r['credit_relief_trn']==0 and all(r[z+'_phase']==0 for z in ['medical','education','rental']),'Early credit')
            if y<min(s['sector_starts'].values()):
                check(r['CI_fraction_applied']==r['elasticity_fraction_applied']==0,'Premature replacement')
            check(close(r['real_gdp_delta_trn'],sum(r[k] for k in ['GDP_CI_adjustment_trn','GDP_benefit_trn','GDP_rate_partial_trn','GDP_credit_trn','GDP_private_burden_trn'])),'GDP decomposition')
            check(close(r['tax_macro_delta_trn'],sum(r[k] for k in ['tax_CI_adjustment_trn','tax_elasticity_adjustment_trn','tax_GDP_channel_trn'])),'Tax decomposition')
            check(all(math.isfinite(r[k]) for k in ['real_gdp_trn','nominal_gdp_trn','tax_revenue_macro_trn']),'Nonfinite')
            check(r['tax_revenue_macro_trn']<=r['nominal_gdp_trn']*.30+1e-8,'Tax cap')
    ok('All 16 ON paths continuous; rates 10→8→5; no 7.5%; gates/phase-weighted replacement verified')
    for r,o in zip(paths['OFF_F'],env[1]):
        check(r['real_gdp_trn']==o['real_gdp_trn'] and r['nominal_gdp_trn']==o['nominal_gdp_trn'] and r['tax_revenue_macro_trn']==o['tax_revenue_trn'],'OFF changed')
    for r,o in zip(paths['ZERO_CHANNEL'],paths['OFF_F']):
        check(close(r['real_gdp_trn'],o['real_gdp_trn']) and close(r['tax_revenue_macro_trn'],o['tax_revenue_macro_trn']),'Zero bridge mismatch')
    ok('OFF exact stored match; actual zero-channel calculation matches existing F')
    for r,o in zip(a,env[1]):
        check(r['CI_fraction_applied']==r['elasticity_fraction_applied']==0,'Base overlap must be zero')
        check(r['effective_tax_elasticity']==o['tax_elasticity_scheduled'],'Base elasticity changed')
    ok('ANNEX_BASE keeps old C/I and elasticity; 2035 matches 5%; no unsupported 25% replacement')
    y=2030
    check(paths['TIMING_EARLY'][y-2026]['real_gdp_trn']!=paths['TIMING_LATE'][y-2026]['real_gdp_trn'],'Timing has no effect')
    check(paths['SIMULTANEOUS'][2035-2026]['credit_relief_trn']>a[2035-2026]['credit_relief_trn'],'Timing not wired')
    check(paths['TIMING_EARLY'][y-2026]['tax_revenue_macro_trn']!=paths['TIMING_LATE'][y-2026]['tax_revenue_macro_trn'],'No tax timing effect')
    ok('Changing activation years changes actual GDP and taxes')
    for r,o in zip(paths['OVERLAP_25'],env[1]):
        if r['year']<2036:check(close(r['real_gdp_trn'],a[r['year']-2026]['real_gdp_trn']),'Before-start sensitivity differs')
    ok('CL-06 regression: overlap case equals Annex base before activation')
    for spec in ['NO_BENEFIT','DOUBLE_BENEFIT','BENEFIT_NOT_IN_LEGACY']:
        check(paths[spec][1]['expenditure_plus_diagnostic_trn']!=a[1]['expenditure_plus_diagnostic_trn'] if spec!='BENEFIT_NOT_IN_LEGACY' else paths[spec][1]['real_gdp_trn']!=a[1]['real_gdp_trn'],'Benefit not wired')
    ok('Benefit on/off and sizes affect budgets; legacy-contained vs residual demand are exclusive alternatives')
    bad=copy.deepcopy(c);bad['schedule']['sector_starts']['medical']=2034
    try:settings(bad,{'id':'bad'})
    except ValueError:pass
    else:raise AssertionError('Illegal pre-5 expansion accepted')
    ok('Pre-5% base expansion rejected, not silently moved to another year')
    for rs in paths.values():
        for r in rs:
            check(r['actual_bond_issuance_trn'] is None and r['PB_trn'] is None and r['CPI_pct'] is None,'Unknown filled')
    ok('Unknown debt/PB/CPI remain blank; source-fixed GDP data not treated as policy validity proof')
    return logs

def report(c,paths,logs):
    a=paths['ANNEX_BASE'];b=paths['OFF_F']
    years=[2026,2028,2030,2035,2036,2038,2040,2055]
    table=[]
    for y in years:
        r=a[y-2026];o=b[y-2026]
        table.append('|'+str(y)+'|'+'|'.join(f'{v:.6f}' for v in [o['real_gdp_trn'],r['real_gdp_trn'],r['real_gdp_delta_trn'],o['tax_revenue_macro_trn'],r['tax_revenue_macro_trn'],r['tax_macro_delta_trn']])+'|')
    end=[]
    for name,rs in paths.items():
        r=rs[-1]
        end.append('|'+name+'|'+'|'.join(f'{v:.6f}' for v in [r['real_gdp_trn'],r['tax_revenue_macro_trn'],r['funding_gap_proxy_trn']])+'|')
    pre=[]
    for y in [2027,2028,2035,2055]:
        new=a[y-2026]['real_gdp_delta_trn'];old=c['previous_lookup'][str(y)]['real_gdp_trn']-b[y-2026]['real_gdp_trn']
        pre.append('|'+str(y)+'|'+'|'.join(f'{v:.6f}' for v in [old,new,new-old])+'|')
    defs='\n'.join('|'+k+'|'+str(v)+'|'+c['coefficient_basis'][k]+'|' for k,v in c['coefficients'].items())
    inventory='\n'.join('|'+n+'|'+str(s['bytes'])+'|`'+s['sha256']+'`|' for n,s in c['sources'].items())
    return f'''# SPE｜F損税マクロ接続 Annexシーケンス修正

Status: DRAFT / PROVISIONAL / NON-CANONICAL  
作成日: 2026-11-16（Asia/Tokyo）。標準ライブラリのみ、追加依存なし。

## 新しい実成果

標準税率10→8→5、給付先行、部門別開始、段階導入を入力で変え、2026〜2055年を実計算した。OFF＋16 ONケースの510 PATH行と差分480行、計990行を出力。従来の2027年からの一律置換を撤去し、主ケースは置換なし、感度のみ開始済み部門の実際の控除額に対応するP加重・段階導入比で適用した。CL-06の既存7,251セルPASSは旧実装の算術検証として維持し、今回の政策時期適合の証明へ転用しない。

## 原文

指定2政策原本をGitHub連携で直接取得、ブランチをCommit `{c['policy_commit']}`へ固定した。

- `policies/FreedomPolicies.md` §5: 「2035年頃：消費税5%完全フラット化」。本計算は2035を暫定年度化。
- 同§4: 「暫定食料品0% → 8% → 5%全品目フラット化」。これは食料品措置。標準税率10→8→5とは別で、食料品売上・期間が未指定のため**食料品0%措置の効果は未算定**。標準税率へ0%を流用しない。
- Annex §6A: 「消費税5%への減税」を先行、「課税ベース拡大」を後続フェーズへ。本体の税率/ベース設計を変更せず順序を反映。
- Annex §6Gの2038年完了・累積120兆円等は原文の旧試算記載。今回の計算をその値へ強制一致させず、国債/返済を新規算定したとは扱わない。

8%は原文に年指定なし。2030を例示し可変化。給付開始2027・期間2027〜2029・年間1兆円は**新規の暫定入力**。なし/2兆円を比較。社会保険料還元給付の政策方向は原文§4/§6にあるが金額と具体年は確定していない。原文を改訂していない。

比較基準は既存F `c0347270009a375dddf65b2d3e596845fb6b5157`。旧接続は`14e0e15b903d21e792fac1ba330c95d2fe428905`、CL-06追補は`b2d97202bfd89e88dccef7a07f402152fc1ed647`（今回の読取は後者）。初回`487f40d...`の検証結果は追補に記載された既存PASSとして利用する。

|原本|bytes|SHA-256|
|---|---:|---|
{inventory}

## 変更点

基準ANNEX_BASE: 8%2030、5%2035、教育2036・住宅2037・医療2038。1年導入。SIMULTANEOUSは全2035。DELAYEDは各元開始を3年遅らせ教育2039・住宅2040・医療2041（5%は2035で維持）。入力のphase_yearsで3年等のランプへ変更可。phase=0ならoutput VATもcreditも0。部門開始<5%到達はエラーとして拒否。

```text
tax_rate = 10% (year<year8), 8% (year8<=year<year5), 5% (year>=year5)
phase_s = clip((year−start_s+1)/phase_years_s, 0, 1)
rate_relief_s = inputVAT_SQ_s−inputVAT_F_s
credit_relief_s = phase_s×eligible_input_credit_F_s
private_VAT_s = phase_s×tax_rate×R_s×(1−public_share_s)
ΔC_rate = MPC×theta×rate_relief
ΔI_rate = investment_share×(1−theta)×rate_relief
ΔC_credit = MPC×theta×credit_relief
ΔI_credit = investment_share×(1−theta)×credit_relief
ΔC_burden = −MPC×private_VAT
ΔC_benefit_residual = MPC×benefit×(1−benefit_already_in_legacy_share)
active_weight = Σ(P_s×phase_s×credit_fraction_s) / ΣP_s
CI_fraction = specified_CI_overlap×active_weight
elasticity_fraction = specified_elasticity_overlap×active_weight
GDP_ON = GDP_adjusted_CI + domestic_share×multiplier×(ΔC+ΔI)/deflator_adjusted
```

需要は**水準**として各年へ反映、恒久的成長率への累積加算はしない。標準税率変更による3部門の部分効果を分けるが、**一般消費税減税の全国効果は算定していない**。既存入力に全国課税消費ベースがなく、3部門だけで外挿しない。`general_tax_beyond_three_sectors_trn`は空欄。

基準のlegacy_CI_overlap/elasticity_overlapは0。既存F消費・投資・教育のスケジュールと税収弾性を維持するので、それらに既に含まれる将来政策時期を完全に再構成したモデルではない。今回修正したのは**明示的な損税接続経路**。重複不明を解消したとは称さない。感度は25%/50%だが時期ゲート後にのみP加重で置換する。

直接VATはF旧税収弾性との重複範囲が不明なので、基準では`direct_fiscal_inclusion=0`。別表示の診断値を効果ゼロとみなさない。財政感度1は直接部門VATを税収proxy、公費output VATを歳出proxyへ加算する**非連結診断**で国庫純増ではない。

給付は既存F刺激に全額包含と置く基準（share1）では需要を追加せず、なしとありのGDP差は0。予算への包含は未特定なので、今回の給付額は追加支出として計上し、なし/ありで財政差を表示する。この需要/予算の非対称は明示的仮定である。`benefit_already_in_legacy_share=0`では追加需要が出る代替ケース。実測による根拠ではない。

主ケースのその他係数:

|係数|値|根拠|
|---|---:|---|
{defs}

住宅控除0/全額は計算端点で、現行/将来制度の法的適格性を認定しない。部分実測施設と全国仮定を合算しない。価格/所得のcash帰着を計算するがCPIは未算定。既存賃金→出生は固定、ここに新たな波及は入れない。

## 年次結果

単位は兆円。値は表示で丸め、CSV原精度を保持する。

|年|OFF GDP|ANNEX GDP|GDP差|OFF税収|ANNEX税収|税収差|
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

### 2055年感度

|ケース|GDP|税収|資金不足proxy|
|---|---:|---:|---:|
{chr(10).join(end)}

従来値との違い（主ケース。改善は因果的な政策便益を意味しない）:

|年|従来GDP差|新GDP差|変化|
|---|---:|---:|---:|
{chr(10).join(pre)}

## 確認

```text
{chr(10).join(logs)}
exit=0
```

コード/JSONでオフライン再実行可能。実行:

```bash
python3 SPE_F_Sonzei_Annex_Sequence_Model_DRAFT_20261116.py SPE_F_Sonzei_Annex_Sequence_Inputs_DRAFT_20261116.json --outdir replay
```

新規コードの差分検証が対象。旧基準の1980行・240行全検査を工程として追加していない。食料品0%、全国減税税収、国債発行、債務残高、PB、CPI、投資の将来資本効果、所得分布、制度別詳細は未算定。原文が要求する最終的な全F動学モデルの完成とは異なる。

成果4原本は`work/chatgpt-handoff`の`handoff/f-sonzei-annex-sequence-20261116/`に新規保全し、固定Commit・SHA・サイズは回答で報告する。既存原本・政策・main・仕様・DecisionLogは未変更。正式Acceptance・Finding Close・Freeze・Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('--outdir',required=True);a=p.parse_args()
    c=json.loads(Path(a.inputs).read_text());env=prepare(c)
    paths={}
    for spec in c['cases']:
        s,co=settings(c,spec);rs=simulate(env,s,co)
        for r in rs:r['case']=spec['id']
        paths[spec['id']]=rs
    paths={'OFF_F':baseline(env[1],paths['ANNEX_BASE'][0]),**paths}
    logs=checks(c,env,paths)
    rows=[r for rs in paths.values() for r in rs]
    for name in paths:
        if name=='OFF_F':continue
        for r,b in zip(paths[name],paths['OFF_F']):
            q={k:None for k in r};q.update(case=name+'_MINUS_OFF_F',record_type='DIFFERENCE',year=r['year'])
            for k in ['real_gdp_trn','nominal_gdp_trn','tax_revenue_macro_trn','tax_plus_diagnostic_trn','expenditure_plus_diagnostic_trn','funding_gap_proxy_trn']:q[k]=r[k]-b[k]
            rows.append(q)
    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    with (out/OUTCSV).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    saved=list(csv.DictReader((out/OUTCSV).open()))
    check(len(saved)==990,'Row count');check(all(r['PB_trn']==r['CPI_pct']=='' for r in saved),'Saved unknowns')
    logs.append('PASS saved CSV 990 rows; unknown values preserved; differences read back')
    (out/OUTMD).write_text(report(c,paths,logs))
    print('\n'.join(logs));print('exit=0; SHA256='+digest((out/OUTCSV).read_bytes()))
    for name in ['OFF_F','ANNEX_BASE','SIMULTANEOUS','DELAYED','TIMING_EARLY','TIMING_LATE']:
        print(name,{k:paths[name][-1][k] for k in ['real_gdp_trn','tax_revenue_macro_trn','funding_gap_proxy_trn']})
if __name__=='__main__':main()
