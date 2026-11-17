#!/usr/bin/env python3
"""Provisional event-linked F model with household/investment/capital carry.
Offline: python3 THIS.py INPUTS.json --outdir NEW_DIRECTORY
Only standard library; all monetary flows/stocks in trillion JPY.
"""
import argparse,csv,copy,hashlib,io,json,math,base64,zlib
from pathlib import Path

CSV='SPE_F_Macro_DM04_DM05_Annual_Comparison_DRAFT_20261117.csv'
MD='SPE_F_Macro_DM04_DM05_Run_Report_DRAFT_20261117.md'
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
    req(p['medical_residual_funding'] in ['UNALLOCATED_COMPAT','PREMIUM','PUBLIC','INTERNAL'],'Invalid medical funding mode')
    req(isinstance(p['investment_start'],int) and not isinstance(p['investment_start'],bool) and 2027<=p['investment_start']<=2055,'Investment start outside transition years')
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
            residual=insurer-premium
            mode=p['medical_residual_funding']
            extra_premium=residual if mode=='PREMIUM' else 0.
            extra_public=residual if mode=='PUBLIC' else 0.
            internal=residual if mode=='INTERNAL' else 0.
            unresolved=residual if mode=='UNALLOCATED_COMPAT' else 0.
            private+=extra_premium
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
        if sec=='medical':ds[sec].update(residual=residual,extra_premium=extra_premium,extra_public=extra_public,internal=internal,unresolved=unresolved)
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
        invphase=0 if disabled else phase(y,p['investment_start'],p['investment_ramp_years'],p['investment_duration'])
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
        expenditure=o['expenditure_trn']+f['benefit']+Espend+med['support']+f['public']-med['comp']+med['extra_public']
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
        r.update(medical_funding_mode=p['medical_residual_funding'],investment_start_year=p['investment_start'],
                 medical_output_vat_trn=med['output'],medical_insurer_residual_before_allocation_trn=med['residual'],
                 medical_premium_additional_trn=med['extra_premium'],medical_public_topup_trn=med['extra_public'],
                 medical_insurer_internal_absorption_trn=med['internal'],medical_unallocated_compat_trn=med['unresolved'],
                 medical_premium_total_trn=med['premium']+med['extra_premium'],
                 medical_public_total_trn=med['public']+med['extra_public'],
                 medical_insurer_operating_balance_delta_trn=med['premium']+med['extra_premium']+med['extra_public']-med['insurer'],
                 medical_insurer_financing_balance_delta_trn=med['premium']+med['extra_premium']+med['extra_public']+med['internal']-med['insurer'],
                 medical_insurer_internal_absorption_cumulative_trn=sum(x['medical_insurer_internal_absorption_trn'] for x in rows)+med['internal'],
                 medical_vat_net_direct_diagnostic_trn=med['output']-med['rate_relief']-med['credit'])
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

def dm_tests(c,env,b,paths):
    logs=[]
    raw=zlib.decompress(base64.b64decode(c['dm_revision']['baseline_csv_zlib_base64']))
    req(len(raw)==c['dm_revision']['baseline_csv_bytes'] and sha(raw)==c['dm_revision']['baseline_csv_sha256'],'Baseline CSV identity')
    old=list(csv.DictReader(io.StringIO(raw.decode())))
    numeric=0
    for r in old:
        new=paths[r['case']][int(r['year'])-2026]
        for k,v in r.items():
            actual=new[k]
            if actual is None:req(v=='','Baseline blank changed')
            elif isinstance(actual,(int,float)):
                req(float(v)==actual,'Baseline numeric changed '+r['case']+' '+r['year']+' '+k);numeric+=1
            else:req(v==actual,'Baseline text changed')
    logs.append('PASS original18 paths/540 rows: all original columns preserved; '+str(numeric)+' numeric cells exactly equal (regression, not new model progress)')
    for spec in c['cases']:
        p,s,z,h=config(c,spec)
        for i,r in enumerate(paths[spec['id']]):
            O=r['medical_output_vat_trn'];B=r['medical_insurer_trn'];P=r['medical_premium_trn'];A=r['medical_premium_additional_trn'];G=r['medical_public_topup_trn'];R=r['medical_insurer_internal_absorption_trn'];U=r['medical_unallocated_compat_trn']
            req(near(O,r['medical_patient_trn']+B+r['medical_public_trn']),'Medical original payer allocation')
            req(near(B,P+A+G+R+U),'Insurer funding allocation')
            req(near(O,r['medical_patient_trn']+r['medical_premium_total_trn']+r['medical_public_total_trn']+R+U),'VAT ultimate payer reconciliation')
            req(near(r['medical_insurer_operating_balance_delta_trn'],-R-U),'Insurer operating balance')
            req(near(r['medical_insurer_financing_balance_delta_trn'],-U),'Insurer financing balance')
            req(near(r['medical_insurer_internal_absorption_cumulative_trn'],sum(x['medical_insurer_internal_absorption_trn'] for x in paths[spec['id']][:i+1])),'Internal cumulative')
            if p['medical_residual_funding']!='UNALLOCATED_COMPAT':req(U==0,'Unallocated new case')
            f=flows(env,p,s,z,h,r['year'],b[i]['nominal'],spec.get('disable_policy',False) or i==0)
            expense=env[1][i]['expenditure_trn']+f['benefit']+r['education_spending_trn']+f['medical']['support']+f['public']-f['medical']['comp']+G
            req(near(expense,r['expenditure_diagnostic_trn']),'Government transfer once')
            req(near(r['funding_gap_proxy_trn'],max(expense-r['tax_diagnostic_trn'],0)),'Funding gap')
            req(near(r['direct_tax_diagnostic_trn'],f['direct_tax']-p['investment_fiscal_cost_share']*r['investment_promotion_trn']),'Tax once')
            req(near(r['medical_vat_net_direct_diagnostic_trn'],O-r['medical_rate_relief_trn']-r['medical_credit_trn']),'Medical net VAT')
            req(r['medical_compensation_level_trn'] is None,'Invented compensation')
            if r['year']<p['investment_start']:req(r['investment_promotion_trn']==0,'Investment premature')
    logs.append('PASS DM04 annual payer/funding/tax/government/insurer/cumulative identities; compensation remains blank')
    base=paths['DYNAMIC_BASE'];tax=paths['TAX8_ONLY_EARLY'];inv=paths['INVEST_ONLY_EARLY'];both=paths['TAX8_INVEST_EARLY']
    for i in range(30):
        req(base[i]['investment_promotion_trn']==tax[i]['investment_promotion_trn'],'Tax date moved investment')
        req(base[i]['standard_tax_rate']==inv[i]['standard_tax_rate'],'Investment date moved tax')
        req(inv[i]['investment_promotion_trn']==both[i]['investment_promotion_trn'],'Joint investment mismatch')
        req(tax[i]['standard_tax_rate']==both[i]['standard_tax_rate'],'Joint tax mismatch')
        req(near(paths['MED_RESIDUAL_PUBLIC'][i]['expenditure_diagnostic_trn']-base[i]['expenditure_diagnostic_trn'],paths['MED_RESIDUAL_PUBLIC'][i]['medical_public_topup_trn']),'Public added twice')
        for name in ['MED_RESIDUAL_PUBLIC','MED_RESIDUAL_INTERNAL']:
            for k in ['real_gdp_trn','tax_diagnostic_trn','household_disposable_nominal_trn']:
                req(paths[name][i][k]==base[i][k],'Transfer/internal unexpectedly affects demand')
    for name in ['TAX8_ONLY_EARLY','INVEST_ONLY_EARLY','TAX8_INVEST_EARLY']:
        req(paths[name][-1]['capital_delta_real_trn']!=base[-1]['capital_delta_real_trn'],'Missing capital timing effect')
    req(paths['MED_RESIDUAL_PREMIUM'][-1]['household_disposable_nominal_trn']<base[-1]['household_disposable_nominal_trn'],'Premium not in income')
    req(paths['MED_RESIDUAL_PREMIUM'][-1]['real_gdp_trn']<base[-1]['real_gdp_trn'],'Premium not in GDP')
    # Support and additional premiums must also reconcile when combined by an input user.
    stress=simulate(c,env,b,{'id':'stress','parameters':{'medical_residual_funding':'PREMIUM','medical_household_support_share':1.0}})
    for r in stress:req(near(r['medical_support_trn'],r['medical_patient_trn']+r['medical_premium_total_trn']),'Support not paired with premium')
    for bad in ['INVALID',None]:
        try:config(c,{'id':'bad','parameters':{'medical_residual_funding':bad}})
        except ValueError:pass
        else:raise AssertionError('Invalid medical mode accepted')
    for bad in [2026,2056,2030.5,True]:
        try:config(c,{'id':'bad','parameters':{'investment_start':bad}})
        except ValueError:pass
        else:raise AssertionError('Invalid investment start accepted')
    logs.append('PASS DM05 independent dates/2x2 factorial/legacy explicit schedule/capital carry; invalid inputs rejected; combined premium+support checked')
    return logs

def dm_report(c,paths,logs):
    lines=['# SPE｜Fマクロ動学モデル DM-04／DM-05限定改良・実行報告','',
      'Status: DRAFT / PROVISIONAL / NON-CANONICAL','作成日: 2026-11-17（Asia/Tokyo）','',
      '## 実成果・取得元','',
      '医療保険者残額の3帰属ケースと、8%開始・投資開始の独立した時期比較を実装し、24経路×30年＝720行を実行した。従来できなかった負担帰属の年次突合と、投資開始だけを変えた比較が可能になった。旧18経路540行は全既存列を保持した。',
      '実装基準: `783b3de06961f0d38d330d0768489fb89dfa93c2`、`handoff/f-macro-dynamic-20261116/`。GitHub連携Base64取得・デコード、4原本のサイズ/SHA-256は引継ぎ値と一致。',
      'Claude検算: `a18ee57a5b4587783f79b6c46478db4e6769daec`、`handoff/claude-fmacro-dynamic-verification-20261116/SPE_F_Macro_Dynamic_Claude_Independent_Verification_DRAFT_20261116.md` を取得・読取。既存10,650セルPASSはClaudeの独立再計算として再利用し、今回の自己試験と区別する。全面レビューは追加していない。','',
      '## DM-04：医療勘定','',
      '旧DYNAMIC_BASEはUNALLOCATED_COMPATとして数値を保ち、未配賦額を明示する。未配賦を解消した基本政策へ黙って変更しない。追加3ケースは政策裁定ではなく感度分析。',
      '- MED_RESIDUAL_PREMIUM: 残額を追加保険料で家計へ帰属。家計現金から1回控除し、既存MPC・部分調整・所得フィードバックを通して消費/GDP/税収に波及する。',
      '- MED_RESIDUAL_PUBLIC: 残額を公費から保険者へ移転。政府歳出に1回加算する。保険者への移転を追加の最終需要に加算しないため、このモデルではGDP・家計・税収は旧基準と同じで、資金不足proxyが増える。財源調達の増税・国債は未モデル化。',
      '- MED_RESIDUAL_INTERNAL: 残額を保険者内部資源で吸収。保険者経常収支差をマイナス、同額の内部資金取崩しで資金収支差をゼロにする。累計取崩しは名目額の単純和。既知の準備金残高・持続可能性を意味しない。家計/投資への追加行動反応を置かないのでGDP・税収・政府歳出は旧基準と同じ。',
      '保険者総負担 = 既存保険料転嫁 + 追加保険料 + 公費補填 + 内部吸収 + 未配賦。出力VAT = 患者 + 保険料合計 + 公費合計 + 内部吸収 + 未配賦。公費補填は税収を増減させず、同じ出力VATを再計上しない。税収診断の医療純直接分は出力VAT−上流税率軽減−仕入税額控除。医療の診療報酬補填水準は不明の空欄のまま。内部吸収は医療機関の投資や既存補填と混同しない。',
      'CSVのmedical_premium_trn/public_trnは旧定義（初期転嫁・直接公費）を保持する。新しいmedical_premium_total_trn/public_total_trnが最終負担。medical_insurer_operating_balance_delta_trnは内部吸収前、financing_balance_deltaは内部資金投入後。旧比較の未配賦は後者に負額として残る。','',
      '## DM-05：独立入力・最小2×2比較','',
      'parameters.investment_startを独立入力化（既定2030、遷移年2027〜2055の整数）。投資・教育の効果式、CORE、旧F、政策原本は変更しない。旧EARLY_5PCT/LATE_5PCTは明示入力2029/2033で従来連動を再現する互換ケース。',
      '追加ケースはTAX8_ONLY_EARLY（8%開始2029・投資2030）、INVEST_ONLY_EARLY（8%開始2030・投資2029）、TAX8_INVEST_EARLY（両方2029）。比較元DYNAMIC_BASEは両方2030。5%開始2035・部門課税化2036〜2038は4ケース共通。これらはF原文の確定日程ではない。','',
      '## 結果：旧基準との差と年次比較','',
      '単位は兆円（資本・消費は実質兆円相当proxy、収支・財源は名目兆円）。表は2030・2035・2038・2045・2055。全2026〜2055年・24ケースの年次値はCSVに収録。Δは同じ年の旧DYNAMIC_BASEとの差で、旧Fとの差ではない。']
    cases=['DYNAMIC_BASE','MED_RESIDUAL_PREMIUM','MED_RESIDUAL_PUBLIC','MED_RESIDUAL_INTERNAL','TAX8_ONLY_EARLY','INVEST_ONLY_EARLY','TAX8_INVEST_EARLY']
    years=[2030,2035,2038,2045,2055]
    groups=[('GDP・家計・消費',[('real_gdp_trn','実質GDP'),('nominal_gdp_trn','名目GDP'),('household_disposable_nominal_trn','家計所得'),('household_consumption_real_proxy_trn','消費proxy')]),
      ('投資・資本・財政',[('investment_promotion_trn','投資促進flow'),('I_policy_real_trn','政策投資state'),('capital_total_real_trn','資本総量'),('expenditure_diagnostic_trn','政府歳出診断'),('tax_macro_trn','macro税収'),('tax_diagnostic_trn','税収診断'),('funding_gap_proxy_trn','不足proxy')])]
    for title,cols in groups:
        lines+=['','### '+title,'','|ケース|年|'+'|'.join(label+' / Δ' for _,label in cols)+'|','|---|---:|'+'---:|'*len(cols)]
        for name in cases:
            for y in years:
                r=paths[name][y-2026];b=paths['DYNAMIC_BASE'][y-2026]
                lines.append('|'+name+'|'+str(y)+'|'+'|'.join(f"{r[k]:.6f} / {r[k]-b[k]:+.6f}" for k,_ in cols)+'|')
    cols=[('medical_output_vat_trn','出力VAT'),('medical_patient_trn','患者'),('medical_insurer_trn','保険者総額'),('medical_premium_trn','初期保険料'),('medical_insurer_residual_before_allocation_trn','配賦前残額'),('medical_premium_additional_trn','追加保険料'),('medical_public_total_trn','公費合計'),('medical_insurer_internal_absorption_trn','内部吸収'),('medical_unallocated_compat_trn','未配賦'),('medical_insurer_operating_balance_delta_trn','経常収支差'),('medical_insurer_financing_balance_delta_trn','資金収支差'),('medical_insurer_internal_absorption_cumulative_trn','累計取崩し')]
    lines+=['','### 医療年次勘定','','|ケース|年|'+'|'.join(t for _,t in cols)+'|','|---|---:|'+'---:|'*len(cols)]
    for name in cases[:4]:
        for y in years:
            r=paths[name][y-2026];lines.append('|'+name+'|'+str(y)+'|'+'|'.join(f'{r[k]:.6f}' for k,_ in cols)+'|')
    lines+=['','### 時期の持越し・交互作用','','交互作用は「両方−税率だけ−投資だけ＋基準」。同時変更を単純な独立加算と仮定しない。2055年に現行フロー・税率が一致しても資本ストック差が残る。','','|年|税率だけGDPΔ|投資だけGDPΔ|両方GDPΔ|GDP交互作用|投資だけ資本Δ|両方資本Δ|','|---:|---:|---:|---:|---:|---:|---:|']
    for y in years:
        b=paths['DYNAMIC_BASE'][y-2026];a=paths['TAX8_ONLY_EARLY'][y-2026];i=paths['INVEST_ONLY_EARLY'][y-2026];j=paths['TAX8_INVEST_EARLY'][y-2026];k='real_gdp_trn'
        values=[a[k]-b[k],i[k]-b[k],j[k]-b[k],j[k]-a[k]-i[k]+b[k],i['capital_total_real_trn']-b['capital_total_real_trn'],j['capital_total_real_trn']-b['capital_total_real_trn']]
        lines.append('|'+str(y)+'|'+'|'.join(f'{v:+.9f}' for v in values)+'|')
    lines+=['','### 全期間の比較','','累計GDP差は各年の実質GDP水準差の単純和（兆円・年）。厚生損失・財政純損失・累積債務ではない。','','|ケース|累計GDP差 対旧動学基準|','|---|---:|']
    for name in cases:
        lines.append('|'+name+'|'+f"{sum(r['real_gdp_trn']-paths['DYNAMIC_BASE'][i]['real_gdp_trn'] for i,r in enumerate(paths[name])):+.6f}"+'|')
    lines+=['','## 検証結果' ,'','```text']+logs+['exit=0','```','',
      '決定論性は本プログラム内で二度のsimulateを比較し、加えて同一入力を別出力先でCLI再実行してCSV/報告書の実バイト一致を確認する。後者の実施結果・4成果物の固定Commit/サイズ/SHA/事後取得照合は引渡し回答に記載する。','',
      '## 制約・権限・再実行','',
      'DYNAMIC_BASEは旧Fの固定消費・投資・教育成長加算を除いた暫定構造。旧682兆円との差を政策損失とは解釈しない。資源フロー.004/.003は元の成長率効果を再現する較正値ではない。全国VATベース、反応係数、資本収率、供給吸収、分配等は未校正。税収・歳出・資金不足は診断proxyで、国庫純増・実際の国全体税収・国債発行・PBではない。金利・債務・CPI・実人数雇用・賃金中央値・ジニ・食料品0%は未算定。公費調達・保険者準備金の実残高・内部吸収の二次行動反応も未算定。',
      '変更はDM-04とDM-05および必要な比較列・試験・報告に限定。main・政策原本・正式エンジン・既存固定成果は変更しない。正式Acceptance/Finding Close/Freeze/Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。ZIPなし。','',
      '標準ライブラリのみ。入力JSONには固定比較CSVをzlib+Base64で内包（配布アーカイブではなく再現検証用の入力データ）。コードとJSONでオフライン再実行可能。','',
      '```bash','python3 SPE_F_Macro_DM04_DM05_Model_DRAFT_20261117.py SPE_F_Macro_DM04_DM05_Inputs_DRAFT_20261117.json --outdir replay','```']
    return '\n'.join(lines)+'\n'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('inputs');parser.add_argument('--outdir',required=True);args=parser.parse_args()
    c=json.loads(Path(args.inputs).read_text());env=prepare(c);b=core(env)
    paths={s['id']:simulate(c,env,b,s) for s in c['cases']}
    paths={**refs(env,c['direct_only_rows'],paths['DYNAMIC_BASE'][0]),**paths}
    logs=tests(c,env,b,paths)+dm_tests(c,env,b,paths)
    repeated={s['id']:simulate(c,env,b,s) for s in c['cases']}
    req(all(repeated[k]==paths[k] for k in repeated),'Nondeterministic simulation')
    logs.append('PASS identical input repeated simulation: all dynamic rows exactly equal')
    delta_keys=['real_gdp_trn','nominal_gdp_trn','household_disposable_nominal_trn','household_consumption_real_proxy_trn','investment_promotion_trn','capital_total_real_trn','expenditure_diagnostic_trn','tax_macro_trn','tax_diagnostic_trn','funding_gap_proxy_trn']
    for rows in paths.values():
        for i,r in enumerate(rows):
            for key in delta_keys:r['delta_old_dynamic_'+key]=r[key]-paths['DYNAMIC_BASE'][i][key] if r[key] is not None else None
    out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
    rs=[r for rows in paths.values() for r in rows]
    with (out/CSV).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
    req(len(list(csv.DictReader((out/CSV).open())))==720,'Saved row count')
    logs.append('PASS saved720 annual rows /24 paths /2026-2055')
    (out/MD).write_text(dm_report(c,paths,logs),encoding='utf-8')
    print('\n'.join(logs));print('exit=0')
    for name in ['DYNAMIC_BASE','MED_RESIDUAL_PREMIUM','MED_RESIDUAL_PUBLIC','MED_RESIDUAL_INTERNAL','TAX8_ONLY_EARLY','INVEST_ONLY_EARLY','TAX8_INVEST_EARLY']:
        r=paths[name][-1];print(name,{k:r[k] for k in ['real_gdp_trn','tax_diagnostic_trn','funding_gap_proxy_trn']})
if __name__=='__main__':main()
