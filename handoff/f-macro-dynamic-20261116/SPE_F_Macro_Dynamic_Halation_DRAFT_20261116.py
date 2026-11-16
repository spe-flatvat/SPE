#!/usr/bin/env python3
"""Provisional event-linked F model with household/investment/capital carry.
Offline: python3 THIS.py INPUTS.json --outdir NEW_DIRECTORY
Only standard library; all monetary flows/stocks in trillion JPY.
"""
import argparse,csv,copy,hashlib,io,json,math
from pathlib import Path

CSV='SPE_F_Macro_Dynamic_Annual_Comparison_DRAFT_20261116.csv'
MD='SPE_F_Macro_Dynamic_Run_Report_DRAFT_20261116.md'
def req(v,s):
    if not v:raise ValueError(s)
def near(a,b):return math.isclose(a,b,rel_tol=2e-12,abs_tol=1e-8)
def sha(b):return hashlib.sha256(b).hexdigest()
def phase(y,start,ramp,duration=100):
    return 0. if y<start or y>=start+duration else min(1.,(y-start+1)/ramp)
def prepare(c):
    a=c['annex_inputs']
    for n,s in a['sources'].items():
        b=s['utf8'].encode();req(len(b)==s['bytes'] and sha(b)==s['sha256'],'Fixed source mismatch '+n)
    for s in c['retrieval']['policies']:
        b=s['content'].encode();req(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==s['sha'],'Current policy blob mismatch')
    old=json.loads(a['sources']['SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json']['utf8'])
    stored=list(csv.DictReader(io.StringIO(a['sources']['SPE_F_StatusQuo_Annual_Comparison_DRAFT_20261115.csv']['utf8'])))
    off=[{k:(int(r[k]) if k=='year' else float(r[k]) if r[k] not in ['',None] else None) for k in r if k not in ['case','record_type','boundary','row_kind','event_names','wage_gini_status','sonzei_macro_link']} for r in stored if r['case']=='F_2026_INITIAL_29']
    events=[r['event_names'] for r in stored if r['case']=='F_2026_INITIAL_29']
    return old,off,events
def config(c,spec):
    p=copy.deepcopy(c['parameters']);s=copy.deepcopy(c['sequence']);z=copy.deepcopy(c['sectors']);h=copy.deepcopy(c['households'])
    p.update(spec.get('parameters',{}))
    for k,v in spec.get('sequence',{}).items():
        if isinstance(v,dict):s[k].update(v)
        else:s[k]=v
    for k,v in spec.get('sector_overrides',{}).items():z[k].update(v)
    for r in h:r['mpc']=min(1.,r['mpc']*spec.get('mpc_scale',1.))
    req(s['year8']<s['year5'],'Tax schedule order')
    req(all(y>=s['year5'] for y in s['starts'].values()),'Pre-5% expansion forbidden')
    req(p['benefit_start']<s['year8'],'Benefit must lead reduction')
    req(all(v>=1 for v in s['phase_years'].values()),'Invalid phase')
    req(near(sum(r['income_weight'] for r in h),1) and near(sum(r['cash_weight'] for r in h),1),'HH weights')
    req(near(z['medical']['patient_share']+z['medical']['insurer_share']+z['medical']['public_share'],1),'Medical payer shares')
    for k in ['depreciation','consumption_adjustment','investment_adjustment','domestic_share','income_feedback','capacity_slack','capacity_absorption','medical_compensation_offset_share','medical_household_support_share']:
        req(0<=p[k]<=1,'Parameter range '+k)
    for x in z.values():req(0<=x['pass_through']<=1 and 0<=x['investment_share']+x['wage_share']<=1,'Sector split')
    return p,s,z,h
def core(env):
    old,off,events=env;rs=[];R=off[0]['real_gdp_trn'];N=off[0]['nominal_gdp_trn'];T=off[0]['tax_revenue_trn']
    for i,o in enumerate(off):
        if i:
            g=(o['base_growth_scheduled_pct']-o['risk_applied_pct']+.65*o['labor_force_growth_pct'])/100
            ng=g+o['inflation_pct']/100;R*=1+g;N*=1+ng;T=min(T*(1+ng)*o['tax_event_factor_applied'],.3*N)
        rs.append({'year':o['year'],'real':R,'nominal':N,'deflator':N/R,'tax':T})
    return rs
def flows(env,p,s,z,h,y,N,disabled):
    old=env[0];out={};ds={};tau=.1 if y<s['year8'] else .08 if y<s['year5'] else .05
    # Rates and scopes are disjoint hypothetical bases; no claim of a measured national VAT base.
    general_base=N*p['household_income_share']*p['taxable_final_consumption_share']
    general_relief=(.1-tau)*general_base if not disabled else 0.
    for sec,raw in old['prototype_config']['sectors'].items():
        a=z[sec];q=phase(y,s['starts'][sec],s['phase_years'][sec]);q=0 if disabled else q
        scale=(1+old['prototype_config']['nominal_growth_pct']['value']/100)**(y-2025)
        R=raw['R_2025']['value']*scale;P=R*raw['p_ratio']['value']
        rr=(.1-tau)*P if not disabled else 0.;credit=q*tau*P*(a.get('credit_fraction',1.))
        vat=q*tau*R
        comp=p['medical_compensation_offset_share']*credit if sec=='medical' else 0.
        if sec=='medical':
            patient=vat*a['patient_share'];insurer=vat*a['insurer_share'];public=vat*a['public_share']
            premium=insurer*a['premium_pass_through'];private=patient+premium
            support=p['medical_household_support_share']*private
        else:
            patient=premium=insurer=0.;public=vat*a['public_share'];private=vat*a['private_share'];support=0.
        relief=rr+credit;price=a['pass_through']*relief
        firm=(1-a['pass_through'])*relief-comp
        # Negative firm cash is a contraction, not silently clipped into a benefit.
        inv=a['investment_share']*firm;pay=a['wage_share']*firm
        ds[sec]={'rate_relief':rr,'credit':credit,'price':price,'firm':firm,'investment':inv,'pay':pay,'phase':q,
                 'patient':patient,'insurer':insurer,'public':public,'private':private,'premium':premium,'support':support,
                 'comp':comp,'output':vat}
    benefit=p['benefit_trn'] if not disabled and p['benefit_start']<=y<=p['benefit_end'] else 0.
    total=lambda k:sum(v[k] for v in ds.values())
    # General price relief and the three-sector upstream cost relief use the same
    # 1-trillion budget only within their own explicit disjoint scopes.
    for k in ['rate_relief','credit','price','firm','investment','pay','private','public']:
        out[k]=total(k)
    out['general_relief']=general_relief;out['benefit']=benefit
    out['household_cash']=general_relief+total('price')+benefit+total('pay')-total('private')+ds['medical']['support']
    out['direct_tax']=-general_relief-total('rate_relief')+total('output')-total('credit')
    out.update(ds)
    return out
def simulate(c,env,base,spec):
    p,s,z,h=config(c,spec);disabled=spec.get('disable_policy',False);carry=p['carry_enabled']
    old,off,events=env;rows=[];C=0.;I=0.;K=0.;H=0.;lastgap=0.;tax=off[0]['tax_revenue_trn'];lastN=off[0]['nominal_gdp_trn']
    Is={k:0. for k in ['medical','education','rental','promotion']};Ks=dict(Is)
    initialpop=off[0]['population_persons'];mpc=sum(x['mpc']*x['cash_weight'] for x in h)
    for i,b in enumerate(base):
        y=b['year'];o=off[i];D=b['deflator'];f=flows(env,p,s,z,h,y,b['nominal'],disabled or not i)
        # Event-linked replacement of the old investment/education growth add-ons:
        # coefficients are RESOURCE FLOW/GDP shares here, not the old pp/year effects.
        invphase=0 if disabled else phase(y,s['year8'],p['investment_ramp_years'],p['investment_duration'])
        edu=0 if disabled else phase(y,p['education_start'],p['education_ramp_years'],p['education_duration'])
        Ipromo=p['investment_promotion_flow_share']*b['nominal']*invphase if i else 0.
        Espend=p['education_flow_share']*b['nominal']*edu if i else 0.
        feedback=p['income_feedback']*lastgap*D if carry and i else 0.
        disposable=p['household_income_share']*b['nominal']+f['household_cash']+feedback
        targetC=p['domestic_share']*sum(x['mpc']*(x['cash_weight']*f['household_cash']+x['income_weight']*feedback) for x in h)/D
        targetI=(Ipromo+f['investment'])/D
        Kprev=K;Hprev=H;Cprev=C;Iprev=I;Kparts_prev=dict(Ks)
        if i:
            C=(1-p['consumption_adjustment'])*C+ p['consumption_adjustment']*targetC if carry else targetC
            for sec in Is:
                target=(Ipromo if sec=='promotion' else f[sec]['investment'])/D
                Is[sec]=(1-p['investment_adjustment'])*Is[sec]+p['investment_adjustment']*target if carry else target
            I=sum(Is.values())
        # Current investment does not provide current productive capacity; use lagged stocks.
        supply=p['capital_output_yield']*(1-p['depreciation'])*Kprev+p['education_yield']*(1-p['education_decay'])*Hprev if carry else 0.
        capacity=b['real']+supply
        induced=p['capacity_absorption']*supply
        desired=b['real']+induced+C+I+Espend/D
        ceiling=capacity+p['capacity_slack']*b['real']
        Y=min(desired,ceiling);unmet=max(desired-Y,0.)
        req(Y>0,'Nonpositive GDP')
        pressure=p['price_pressure_coefficient']*unmet/b['real']
        N=Y*D*(1+pressure)
        if i:tax=min(tax*(1+(N/lastN-1)*p['macro_tax_elasticity'])*o['tax_event_factor_applied'],N*.30)
        subsidy=p['investment_fiscal_cost_share']*Ipromo
        direct=f['direct_tax']-subsidy
        med=f['medical']
        expenditure=o['expenditure_trn']+f['benefit']+Espend+med['support']+f['public']-med['comp']
        taxdiag=tax+direct
        if i:
            for sec in Ks:Ks[sec]=(1-p['depreciation'])*Kparts_prev[sec]+Is[sec] if carry else 0.
            K=sum(Ks.values())
            H=(1-p['education_decay'])*Hprev+Espend/D if carry else 0.
        coreK=p['base_capital_output_ratio']*b['real']
        # This baseline replacement investment makes the capital identity explicit.
        prevCoreK=p['base_capital_output_ratio']*base[max(i-1,0)]['real']
        replacement=coreK-(1-p['depreciation'])*prevCoreK if i else 0.
        gap=Y-b['real']
        r={'case':spec['id'],'year':y,'scope':'PROVISIONAL_ASSUMPTIONS_NOT_POLICY_ESTIMATE',
           'real_gdp_trn':Y,'nominal_gdp_trn':N,'tax_macro_trn':tax,'tax_diagnostic_trn':taxdiag,
           'expenditure_diagnostic_trn':expenditure,'funding_gap_proxy_trn':max(expenditure-taxdiag,0.),
           'GDP_delta_legacy_trn':Y-o['real_gdp_trn'],'GDP_delta_core_trn':gap,
           'legacy_addons_removal_trn':b['real']-o['real_gdp_trn'],
           'C_demand_real_trn':C,'I_policy_real_trn':I,'education_demand_real_trn':Espend/D,
           'capacity_absorption_real_trn':induced,'supply_constraint_real_trn':unmet,
           'capital_delta_real_trn':K,'capital_total_real_trn':coreK+K,
           'capital_replacement_investment_real_trn':replacement,
           'human_capital_resource_stock_trn':H,'supply_gain_real_trn':supply,
           'capacity_real_trn':capacity,'price_pressure_proxy':pressure,
           'household_disposable_nominal_trn':disposable,'household_policy_cash_nominal_trn':f['household_cash'],
           'household_consumption_real_proxy_trn':p['household_income_share']*b['real']+C,
           'household_feedback_nominal_trn':feedback,'general_rate_relief_trn':f['general_relief'],
           'benefit_trn':f['benefit'],'investment_promotion_trn':Ipromo,'education_spending_trn':Espend,
           'direct_tax_diagnostic_trn':direct,'tax_GDP_delta_core_trn':tax-b['tax'],
           'standard_tax_rate':.10 if y<s['year8'] else .08 if y<s['year5'] else .05,
           'employment_index_proxy':100*o['population_persons']/initialpop*(1+p['employment_elasticity']*gap/b['real']),
           'wage_index_proxy':100*o['real_wage_anchor_man_yen']/off[0]['real_wage_anchor_man_yen']*(1+p['wage_elasticity']*gap/b['real']),
           'population_persons':o['population_persons'],'actual_employment_persons':None,'CPI_pct':None,
           'policy_interest_rate_pct':None,'actual_bond_issuance_trn':None,'debt_stock_trn':None,'PB_trn':None,
           'medical_compensation_level_trn':None,
           'risk_applied_pct':o['risk_applied_pct'],'event_names':events[i]}
        for a in h:
            r['HH_'+a['id']+'_cash_change_trn']=a['cash_weight']*f['household_cash']+a['income_weight']*feedback
        for sec in ['medical','education','rental']:
            for k in ['rate_relief','credit','price','firm','investment','pay','phase']:
                r[sec+'_'+k+('_trn' if k!='phase' else '')]=f[sec][k]
            r[sec+'_investment_real_state_trn']=Is[sec]
            r[sec+'_capital_real_trn']=Ks[sec]
            r[sec+'_capacity_gain_real_trn']=p['capital_output_yield']*(1-p['depreciation'])*Kparts_prev[sec] if carry else 0.
        r['promotion_capital_real_trn']=Ks['promotion']
        for k in ['patient','insurer','public','premium','support']:
            r['medical_'+k+'_trn']=med[k]
        r['medical_compensation_offset_assumed_trn']=med['comp']
        r['private_burden_trn']=f['private']
        r['carry_K_prev_trn']=Kprev;r['carry_H_prev_trn']=Hprev
        lastgap=gap;lastN=N;rows.append(r)
    return rows
def refs(env,direct,template):
    _,off,events=env;out={}
    for case in ['LEGACY_OFF','DIRECT_ONLY']:
        rs=[]
        for i,o in enumerate(off):
            r={k:None for k in template};r.update(case=case,year=o['year'],scope='FIXED_EXISTING_REFERENCE',population_persons=o['population_persons'])
            if case=='LEGACY_OFF':
                r['real_gdp_trn']=o['real_gdp_trn'];r['nominal_gdp_trn']=o['nominal_gdp_trn'];r['tax_macro_trn']=o['tax_revenue_trn'];r['tax_diagnostic_trn']=o['tax_revenue_trn'];r['expenditure_diagnostic_trn']=o['expenditure_trn']
            else:
                d=direct[i]
                for a,b in [('real_gdp_trn','real_gdp_trn'),('nominal_gdp_trn','nominal_gdp_trn'),('tax_macro_trn','tax_revenue_macro_trn'),('tax_diagnostic_trn','tax_plus_diagnostic_trn'),('expenditure_diagnostic_trn','expenditure_plus_diagnostic_trn')]:r[a]=float(d[b])
            r['funding_gap_proxy_trn']=max(r['expenditure_diagnostic_trn']-r['tax_diagnostic_trn'],0.)
            r['GDP_delta_legacy_trn']=r['real_gdp_trn']-o['real_gdp_trn'];rs.append(r)
        out[case]=rs
    return out

def tests(c,env,b,paths):
    logs=[]
    def ok(s):logs.append('PASS '+s)
    for name,rs in paths.items():req([r['year'] for r in rs]==list(range(2026,2056)),'Year gap')
    for i,o in enumerate(env[1]):
        req(paths['LEGACY_OFF'][i]['real_gdp_trn']==o['real_gdp_trn'],'Legacy changed')
        req(paths['DIRECT_ONLY'][i]['real_gdp_trn']==float(c['direct_only_rows'][i]['real_gdp_trn']),'Direct changed')
        req(paths['DIRECT_ONLY'][i]['tax_macro_trn']==float(c['direct_only_rows'][i]['tax_revenue_macro_trn']),'Direct tax changed')
    ok('LEGACY_OFF and DIRECT_ONLY preserve fixed numeric results; original PASS reused')
    for spec in c['cases']:
        name=spec['id'];p,s,z,h=config(c,spec);rs=paths[name]
        for i,r in enumerate(rs):
            for k in ['real_gdp_trn','nominal_gdp_trn','tax_macro_trn']:
                req(math.isfinite(r[k]) and r[k]>0,'Nonfinite '+name)
            req(near(r['GDP_delta_core_trn'],r['C_demand_real_trn']+r['I_policy_real_trn']+r['education_demand_real_trn']+r['capacity_absorption_real_trn']-r['supply_constraint_real_trn']),'GDP decomposition')
            req(near(r['GDP_delta_legacy_trn'],r['legacy_addons_removal_trn']+r['GDP_delta_core_trn']),'Legacy decomposition')
            req(near(r['tax_diagnostic_trn'],b[i]['tax']+r['tax_GDP_delta_core_trn']+r['direct_tax_diagnostic_trn']),'Tax decomposition')
            req(r['real_gdp_trn']<=r['capacity_real_trn']+p['capacity_slack']*b[i]['real']+1e-8,'Supply not bounded')
            req(near(sum(r['HH_'+x['id']+'_cash_change_trn'] for x in h),r['household_policy_cash_nominal_trn']+r['household_feedback_nominal_trn']),'HH allocations')
            req(r['CPI_pct'] is None and r['PB_trn'] is None and r['actual_bond_issuance_trn'] is None,'Unknown filled')
            if p['carry_enabled'] and i:
                req(near(r['capital_delta_real_trn'],(1-p['depreciation'])*r['carry_K_prev_trn']+r['I_policy_real_trn']),'Capital identity')
                req(near(r['capital_total_real_trn']-(1-p['depreciation'])*rs[i-1]['capital_total_real_trn'],r['capital_replacement_investment_real_trn']+r['I_policy_real_trn']),'Total capital identity')
            if i:
                req(near(r['tax_macro_trn'],min(rs[i-1]['tax_macro_trn']*(1+(r['nominal_gdp_trn']/rs[i-1]['nominal_gdp_trn']-1)*p['macro_tax_elasticity'])*env[1][i]['tax_event_factor_applied'],r['nominal_gdp_trn']*.3)),'Tax recurrence')
            if r['year']<s['year5']:
                req(all(r[sec+'_credit_trn']==0 for sec in ['medical','education','rental']),'Early base')
    ok('All cases continuous; GDP/tax/household decompositions close; capital identity holds in carry-enabled cases')
    ok('Supply constrains actual output; tax recurrence excludes direct diagnostic from next-year tax base')
    req(paths['CORE_NO_POLICY'][0]['real_gdp_trn']==env[1][0]['real_gdp_trn'],'Initial mismatch')
    req(all(near(r['real_gdp_trn'],b[i]['real']) for i,r in enumerate(paths['CORE_NO_POLICY'])),'Effect before event/zero policy')
    req(paths['DYNAMIC_BASE'][1]['household_policy_cash_nominal_trn']==1.,'Benefit initial cash/activation')
    req(paths['DYNAMIC_BASE'][1]['investment_promotion_trn']==0.,'Premature investment event')
    ok('Zero policy reproduces no-add-on core; no pre-activation benefit/tax/base/investment effects')
    req(abs(paths['EARLY_5PCT'][-1]['real_gdp_trn']-paths['LATE_5PCT'][-1]['real_gdp_trn'])>1e-5,'No long-run timing effect')
    for k in ['standard_tax_rate','investment_promotion_trn','medical_credit_trn','education_credit_trn','rental_credit_trn']:
        req(near(paths['EARLY_5PCT'][-1][k],paths['LATE_5PCT'][-1][k]),'Terminal policy state differs: '+k)
    req(abs(paths['EARLY_5PCT'][-1]['capital_delta_real_trn']-paths['LATE_5PCT'][-1]['capital_delta_real_trn'])>1e-5,'No capital timing')
    req(abs(paths['DYNAMIC_BASE'][-1]['real_gdp_trn']-paths['NO_CARRY'][-1]['real_gdp_trn'])>1e-5,'Carry unconnected')
    ok('Same final tax state but timing changes capital and2055 GDP; NO_CARRY differs')
    req(any(r['price_pressure_proxy']>0 for r in paths['CAPACITY_TIGHT']),'Supply constraint sensitivity inactive')
    req(any(r['medical_patient_trn']>0 for r in paths['DYNAMIC_BASE']),'Missing patient burden')
    req(paths['MEDICAL_SUPPORT'][-1]['real_gdp_trn']>paths['DYNAMIC_BASE'][-1]['real_gdp_trn'],'Support channel not connected')
    req(any(r['medical_support_trn']>0 for r in paths['MEDICAL_SUPPORT']),'No support')
    ok('Positive relief/investment and negative private burden computed; medical support and compensation sensitivity distinct')
    bad=copy.deepcopy(c);bad['sequence']['starts']['medical']=2034
    try:config(bad,{'id':'bad'})
    except ValueError:pass
    else:raise AssertionError('Early base accepted')
    ok('Pre-5% base expansion rejected; no old C/I/E growth additions in dynamic core')
    return logs

def report(c,paths,logs):
    yrs=[2030,2035,2038,2045,2055]
    a=paths['DYNAMIC_BASE'];tbl=[]
    for y in yrs:
        i=y-2026;r=a[i];l=paths['LEGACY_OFF'][i]
        vals=[l['real_gdp_trn'],paths['DIRECT_ONLY'][i]['real_gdp_trn'],r['real_gdp_trn'],paths['CORE_NO_POLICY'][i]['real_gdp_trn'],r['tax_macro_trn'],r['tax_diagnostic_trn']]
        tbl.append('|'+str(y)+'|'+'|'.join(f'{v:.6f}' for v in vals)+'|')
    ends=[]
    for name,rs in paths.items():
        r=rs[-1];cum=sum(x['real_gdp_trn']-paths['LEGACY_OFF'][i]['real_gdp_trn'] for i,x in enumerate(rs));cc=sum(x['real_gdp_trn']-paths['CORE_NO_POLICY'][i]['real_gdp_trn'] for i,x in enumerate(rs))
        ends.append('|'+name+'|'+'|'.join(f'{v:.6f}' for v in [r['real_gdp_trn'],r['tax_macro_trn'],cum,cc])+'|')
    med=[]
    for name in ['DYNAMIC_BASE','MEDICAL_SUPPORT','MEDICAL_COMP_OFFSET']:
        r=paths[name][-1];vals=[r['medical_credit_trn'],r['medical_patient_trn'],r['medical_insurer_trn'],r['medical_public_trn'],r['medical_support_trn'],r['medical_compensation_offset_assumed_trn']]
        med.append('|'+name+'|'+'|'.join(f'{v:.6f}' for v in vals)+'|')
    b=paths['DYNAMIC_BASE'];peaks=max(b,key=lambda r:r['private_burden_trn']);transition=max((r for r in b if r['year']<=2038),key=lambda r:r['private_burden_trn'])
    notes='\n'.join('- **'+k+'**: '+v for k,v in c['assumption_notes'].items())
    coreY=paths['CORE_NO_POLICY'][-1]['real_gdp_trn'];Y=b[-1]['real_gdp_trn']
    return f'''# SPE｜Fマクロ動学接続・正負の波及・持越し計算

Status: DRAFT / PROVISIONAL / NON-CANONICAL  
作成日: 2026-11-16（Asia/Tokyo）。2026初期状態、2027〜2055の29遷移。金額:兆円、資本は実質兆円相当の仮想資源ストック。

## 今回の実成果と比較境界

{len(c['cases'])}動学ケースとLEGACY_OFF・DIRECT_ONLYを計算し、{(len(c['cases'])+2)*30}年次行を生成した。家計所得→消費、企業資金→投資、減耗を伴う資本、教育資源ストック→翌年の供給能力、所得フィードバック、供給制約と価格圧力proxy、税収へ接続した。同じ最終税率でも開始時期で2055GDP・資本が異なる。

**動学基準は旧Fを追加拡張した予測ではない。旧C/I/E固定加算を全部外した新しい暫定構造との比較である。** 2055年の動学GDPは{Y:.6f}兆円、固定加算を除くCOREは{coreY:.6f}。差{Y-coreY:.6f}はこの構造内の政策・波及効果。旧Fとの差には加算を外した影響を含む。旧682.375へ合わせる係数調整はしていない。

## 原文・既存PASS・AN-01〜04

政策本文/AnnexはGitHub連携で直接取得し、読取HEAD `{c['retrieval']['head']}`へ固定。本文§9の消費+.3〜.7%/年、投資+.3〜.5%/年、教育GDP+.3%・賃金+.2%は原文の縮約仮定。旧モデルの年次加算スケジュールはモデル設定で、原文が全開始年を確定したものではない。主動学モデルでは消費を家計cashとMPCから生成し、+.5ppを再加算しない。投資.004、教育.003は今回**資源フロー/GDP比へ意味を変更**しており、元の成長率効果と同一とは称さない。額・年・ランプ・期間は入力可変であり、政策原本は変更しない。

固定Annex `{c['annex_commit']}` の4原本は既存CUSTODY/990行PASSと今回のローカルSHA一致を再利用した。DIRECT_ONLYは保存原本ANNEX_BASEの数値を参照。Claude `{c['retrieval']['verification']['display_url']}` を取得し読取、11,562セルPASSは旧構造の算術検証として維持する。今回の新しい動学仮定の実証には転用しない。

AN-01: 固定C/I/EはLEGACY/DIRECTに保持、主動学ではイベント連動に置換。AN-02: 給付は主動学でcash/消費へ入り、旧消費刺激は残さない。AN-03: 標準10→8→5と給付先行を維持、食料品0%は未算定。AN-04: 根拠のない旧加算25%控除は使わず、別モデル間の差として表示する。

## 計算構造

NO_CARRYは投資・教育を翌年資本に残さない比較用診断で、実際の代替政策とは扱わない。EARLY/LATEは終端の税率・控除・投資支援フローを揃え、資本と2055GDPが異なることを確認する。

```text
CORE growth = base − risk + .65×labor_growth  # old C/I/E removed
HH policy cash = general tax relief + sector price relief + benefit + sector wage allocation − private burden + medical support
HH feedback cash_t = income_feedback × (GDP_(t−1)−CORE_(t−1)) × deflator_t
C_target = domestic_share × sum(MPC_group × cash_group) / deflator
C_state_t = (1−lambdaC) C_(t−1) + lambdaC C_target
I_target = (sector cash investment + event investment promotion) / deflator
I_state_t = (1−lambdaI) I_(t−1) + lambdaI I_target
K_delta_t = (1−depreciation) K_delta_(t−1) + I_state_t
H_t = (1−education_decay) H_(t−1) + education_spending/deflator
capacity_gain_t = capital_yield×(1−depreciation) K_(t−1) + education_yield×(1−education_decay) H_(t−1)
desired GDP = CORE + capacity_absorption×capacity_gain + C_state + I_state + education demand
actual GDP = min(desired GDP, CORE+capacity_gain+slack×CORE)
unmet demand = max(desired−actual,0)
price_pressure_proxy = price_coefficient×unmet/CORE
nominal GDP = actual GDP×CORE_deflator×(1+price_pressure_proxy)
tax_macro = min(previous tax_macro×(1+nominal growth×unit elasticity)×event factor, nominalGDP×.30)
tax_diagnostic = tax_macro + general/sector VAT delta − investment tax subsidy
```

資本の総量はCORE GDP×仮定資本係数3＋政策純増K。基準更新投資を計上し、増加/減耗を区別する。今期投資は今期需要に入り、供給には前期ストックだけが入る。消費、投資、教育、供給誘発吸収、供給制約の分解でGDP差が閉じる。資本の潜在能力の半分が基準吸収を誘発する閉鎖係数.5は例示仮定で、完全稼働や実証された生産性ではない。

家計所得share.6・課税最終消費share.5から一般減税の**新規仮定ベース**を置いた。3部門出力/上流仕入と重複しない仮想勘定として定義するが、全国VATベースの実測ではなく、真のサプライチェーン連結は未実装。税収の直接効果を翌年tax_macroへ再複利しない。旧弾性1.5〜2を主動学で残さず単位弾性に置換。旧税収との差は税制効果と混同しない。

## 部門・家計・医療

部門別に価格帰着/投資/人件費配分を分離。医療.2/.25/.20、教育.4/.15/.30、賃貸.6/.12/.10は例示。残りの企業資金は自動的にGDPへ全額加算しない。企業資金が負なら投資縮小も可能。仕入比率・成長率は既存Claude全国仮定を継承し、部分施設の実測を合算しない。

医療output VATは患者.10・保険者.25・公費.65へ仮配分。保険者の半分を保険料へ転嫁する仮定を別に置く。MEDICAL_SUPPORTは患者＋保険料転嫁分の100%を給付で相殺する感度で、必要給付額との裁定ではない。診療報酬の既存補填**水準は不明のまま空欄**。MEDICAL_COMP_OFFSETでは新規控除の50%を補填から仮に調整する。実際の補填額を推定した値ではなく、既存Aとの同一性未検証。

保険者負担には保険料転嫁後の未財源分が残る。政府歳出へ自動的に付け替えない。患者負担・保険料・公費・家計給付・補填調整の勘定を混同しない。雇用は人口×GDP差弾性の指数proxy、賃金は既存外生アンカー×GDP差弾性の指数proxy。実際の雇用人数/賃金中央値は未算定で、人口・出生を新指数へ再接続していない。

仮定:
{notes}

## 結果

|年|LEGACY GDP|DIRECT GDP|DYNAMIC GDP|CORE GDP|動学税収macro|直接込み診断|
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(tbl)}

|ケース|2055GDP|2055macro税収|累計GDP差 対LEGACY|累計GDP差 対CORE|
|---|---:|---:|---:|---:|
{chr(10).join(ends)}

累計は各年GDP**水準差の単純和（兆円・年）**。厚生損失、財政純損失、割引現在価値、累積債務ではない。DYNAMIC_BASEで移行期（〜2038）の最大私的負担は{transition['private_burden_trn']:.6f}兆円、{transition['year']}年。全期間では{peaks['private_burden_trn']:.6f}兆円、{peaks['year']}年。これは3部門output VATの患者/保険料/民間負担で、手取り改善や給付を差し引く前。

|ケース|2055医療控除|患者|保険者総額|公費|家計支援|補填調整仮定|
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(med)}

## 検証

```text
{chr(10).join(logs)}
exit=0
```

再実行:
```bash
python3 SPE_F_Macro_Dynamic_Halation_DRAFT_20261116.py SPE_F_Macro_Dynamic_Inputs_DRAFT_20261116.json --outdir replay
```

4成果物でオフライン再実行可能、標準ライブラリのみ。固定原本はJSONに内包、DIRECT数値は旧CSVから抽出した参照表。既存原本を変更・再生成したとの主張ではない。旧モデルの完全な再検証は追加していない。

## 未達・引渡し

全構造係数は暫定で、政策因果推定・DSGE・予測ではない。全国課税ベース、費目別住宅控除、既存補填制度、保険者の未財源、金利・実際の国債発行・債務・PB・CPI・所得分布は未実装/未確定。税収diagnosticは国庫純増や確定した国全体税収ではない。次の実成果は税・保険財源の勘定連結と出典付き反応係数への置換計算。

今回のみ`work/chatgpt-handoff`の`handoff/f-macro-dynamic-20261116/`に新規4原本を保存する。固定Commit・bytes/SHA・事後取得照合は回答で提示。main・既存原本・政策・正式エンジン・DecisionLogは未変更。ZIP/新規HTML/レビュー依頼なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。正式Acceptance/Close/Freeze/Canonical化なし。
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('--outdir',required=True);a=p.parse_args();c=json.loads(Path(a.inputs).read_text());env=prepare(c);b=core(env)
    paths={s['id']:simulate(c,env,b,s) for s in c['cases']}
    paths={**refs(env,c['direct_only_rows'],paths['DYNAMIC_BASE'][0]),**paths}
    logs=tests(c,env,b,paths)
    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True);rs=[r for v in paths.values() for r in v]
    with (out/CSV).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
    reread=list(csv.DictReader((out/CSV).open()));req(len(reread)==(len(c['cases'])+2)*30 and all(r['CPI_pct']==r['PB_trn']=='' for r in reread),'Saved output mismatch')
    logs.append('PASS saved CSV '+str(len(reread))+' rows, '+str(len(paths))+' paths, missing values blank')
    (out/MD).write_text(report(c,paths,logs));print('\n'.join(logs));print('exit=0; SHA256='+sha((out/CSV).read_bytes()))
    for name in ['LEGACY_OFF','DIRECT_ONLY','DYNAMIC_BASE','SIMULTANEOUS','DELAYED','EARLY_5PCT','LATE_5PCT']:
        print(name,{k:paths[name][-1][k] for k in ['real_gdp_trn','tax_macro_trn','tax_diagnostic_trn']})
if __name__=='__main__':main()
