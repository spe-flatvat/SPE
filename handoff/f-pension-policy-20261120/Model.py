#!/usr/bin/env python3
"""SPE pension difference model. DRAFT / NON-CANONICAL; Python stdlib only.
python Model.py Inputs.json --outdir replay
National pension totals and causal behavioral coefficients are NOT estimated.
"""
import argparse, base64, builtins, copy, csv, hashlib, json, math, zlib
from pathlib import Path
YEARS = range(2026, 2056)
TRN = 1e12


def close(a, b):
    return math.isclose(a, b, abs_tol=1e-7, rel_tol=1e-10)


def dump(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows({k: format(v, '.12g') if isinstance(v, float) else v for k, v in r.items()} for r in rows)


def unpack(blob):
    b = zlib.decompress(base64.b64decode(blob['zlib_base64']))
    assert len(b) == blob['size'] and hashlib.sha256(b).hexdigest() == blob['sha256']
    return b


def phase(y, s):
    return max(0., min(1., (y - s['start_year'] + 1) / s['ramp_years']))


def suspension(wage_month, pension_month, threshold):
    # Earnings-related pension only, basic pension never enters this calculation.
    return min(pension_month, max(0., (wage_month + pension_month - threshold) / 2.))


def income_tax(taxable, y):
    x = math.floor(max(0., taxable) / 1000.) * 1000.
    bands = [(1950000, .05, 0), (3300000, .10, 97500), (6950000, .20, 427500),
             (9000000, .23, 636000), (18000000, .33, 1536000),
             (40000000, .40, 2796000), (float('inf'), .45, 4796000)]
    r, d = next((r, d) for limit, r, d in bands if x < limit)
    # 2027: reconstruction 1.1% + defence 1%; reconstruction expires after 2047.
    return max(0., x * r - d) * (1.021 if y <= 2047 else 1.01)


def pension_taxable(gross, age=65):
    # Official public-pension miscellaneous income schedule, other income <=10m.
    if age >= 65 and gross <= 3300000:
        return max(0., gross - 1100000)
    if age < 65 and gross <= 1300000:
        return max(0., gross - 600000)
    if gross <= 4100000:
        return max(0., gross * .75 - 275000)
    if gross <= 7700000:
        return gross * .85 - 685000
    if gross <= 10000000:
        return gross * .95 - 1455000
    return gross - 1955000


def annual_threshold(y, index, mode):
    # Calendar-year weighted approximation to Apr annual revisions, not a forecast.
    if y == 2026:
        return (3 * 510000 + 9 * 650000) / 12
    return 650000 * (index if mode == 'WAGE_PROXY' else 1.)


def remuneration_ceiling(y):
    return {2026: 650000, 2027: (8*650000+4*680000)/12,
            2028: (8*680000+4*710000)/12,
            2029: (8*710000+4*750000)/12}.get(y, 750000)


def public_ledger(c, s, elders, baseline):
    rows, strata_rows = [], []
    q = c['public']
    for i, (e, m) in enumerate(zip(elders, baseline)):
        y = 2026 + i
        idx = m['common_deflator'] / (600/580)
        z = phase(y, s) if s['public'] else 0.
        threshold_sq = annual_threshold(y, idx, s['threshold_index'])
        # Candidate fully abolishes only after ramp; interpolate statutory suspension.
        threshold_f = threshold_sq + s['threshold_add_yen'] * idx * z
        def stopped(w, b, candidate):
            if y == 2026:
                return (3*suspension(w,b,510000)+9*suspension(w,b,650000))/12
            base = suspension(w,b,threshold_sq)
            return base*(1-z) if candidate and s['abolish'] else suspension(w,b,threshold_f) if candidate else base
        total = {k:0. for k in ['sq_suspension','f_suspension','modeled_gross','direct_relief','behavior_benefit',
                                'jobs','hours_equivalent','wages','premiums','overlap','legacy_relief','covered_jobs']}
        for age in ['65_69','70_74','75plus']:
            pop = sum(e[age+'_'+sex+'_population'] for sex in ['male','female'])
            base_jobs = sum(e[age+'_'+sex+'_population']*e[age+'_'+sex+'_SQ_rate'] for sex in ['male','female'])
            legacy_jobs = sum(e[age+'_'+sex+'_extra_jobs'] for sex in ['male','female'])
            jobs = base_jobs + legacy_jobs
            pool = max(0., pop - jobs)
            coverage = min(1., q['coverage'][age] * s['coverage_scale'])
            # Existing 50k recipients have 2m annual wages, as fixed in elder stage2.
            legacy_b = sum(t['weight']*t['pension_month'] for t in q['strata'])*idx
            legacy_w = q['legacy_worker_annual_wage_yen']/12*idx
            legacy_gain = max(0., stopped(legacy_w,legacy_b,False)-stopped(legacy_w,legacy_b,True))*12
            # Same-recipient cap; eligibility intersection is assumed, not observed.
            overlap = min(q['legacy_support_yen']*idx,legacy_gain)*legacy_jobs*coverage
            if s['overlap_mode'] == 'REPLACE_ALL':
                overlap = q['legacy_support_yen']*idx*legacy_jobs*z
            total['overlap'] += overlap
            total['legacy_relief'] += legacy_gain*legacy_jobs*coverage
            for t in q['strata']:
                salary,bonus=t['salary_month']*idx,t['annual_bonus']*idx
                def remuneration(factor=1.):
                    # Continuous standard-remuneration approximation; bonus ceiling
                    # applies per payment (1.5m), salary ceiling scheduled by law.
                    return min(salary*factor,remuneration_ceiling(y))+min(bonus*factor,t['bonus_payments']*1500000)/12
                w,b,weight=remuneration(),t['pension_month']*idx,t['weight']
                old_stop,new_stop = stopped(w,b,False),stopped(w,b,True)
                annual_gain = (old_stop-new_stop)*12
                exposure = base_jobs*coverage*weight
                # Bounds operate on remaining pool AFTER existing F elder employment.
                ratio = annual_gain/max(1.,salary*12+bonus)
                prob = max(-1.,min(1.,s['job_response']*ratio))
                added = (pool if prob >= 0 else base_jobs)*coverage*weight*prob
                hours = exposure*max(-.5,min(.5,s['hours_response']*ratio))
                # New workers already received a pension while not working: only new
                # suspension is an incremental benefit expense, never their full pension.
                assert -base_jobs*coverage*weight-1e-6 <= added <= pool*coverage*weight+1e-6
                behavior = -added*new_stop*12
                # Hours change both wages and suspension of incumbent workers.
                hour_rate = hours/exposure if exposure else 0.
                hours_benefit = exposure*(new_stop-stopped(remuneration(1+hour_rate),b,True))*12
                behavior += hours_benefit
                contrib_base = added*w*12
                contrib_base += exposure*(remuneration(1+hour_rate)-w)*12
                premiums = contrib_base*q['contribution_rate'] if age == '65_69' else 0.
                relief = exposure*annual_gain
                total['direct_relief'] += relief
                total['behavior_benefit'] += behavior
                total['sq_suspension'] += exposure*old_stop*12
                total['f_suspension'] += exposure*new_stop*12-behavior
                total['modeled_gross'] += exposure*b*12
                total['jobs'] += added
                total['hours_equivalent'] += hours
                total['wages'] += (added+hours)*(salary*12+bonus)
                total['premiums'] += premiums
                total['covered_jobs'] += added if age=='65_69' else 0.
                strata_rows.append(dict(case=s['id'],year=y,age_group=age,stratum=t['id'],
                    covered_incumbents=exposure,wage_month_yen=w,pension_month_yen=b,
                    SQ_threshold_yen=threshold_sq,F_threshold_yen=None if s['abolish'] and z==1 else threshold_f,
                    SQ_suspension_month_yen=old_stop,F_suspension_month_yen=new_stop,
                    direct_benefit_relief_trn=relief/TRN,additional_jobs=added,
                    hours_equivalent_workers=hours,premium_delta_trn=premiums/TRN))
            # Separate fixed-elder group: no representative high-wage attribution to 2m jobs.
            total['sq_suspension'] += legacy_jobs*coverage*stopped(legacy_w,legacy_b,False)*12
            total['f_suspension'] += legacy_jobs*coverage*stopped(legacy_w,legacy_b,True)*12
            total['direct_relief'] += legacy_gain*legacy_jobs*coverage
            total['modeled_gross'] += legacy_jobs*coverage*legacy_b*12
        benefit = total['direct_relief']+total['behavior_benefit']-total['overlap']
        # Wage effect already passes through core labor income share; do not add twice.
        # Public-pension tax effective rate is sensitivity, not an individual assessment.
        public_tax = benefit*s['public_tax_rate']
        hh = benefit-public_tax-total['premiums']*.5
        rows.append(dict(year=y,public_phase=z,SQ_threshold_month_yen=threshold_sq,
            F_threshold_month_yen=threshold_f,
            SQ_modeled_suspension_trn=total['sq_suspension']/TRN,
            F_modeled_suspension_trn=total['f_suspension']/TRN,
            modeled_full_earnings_pension_trn=total['modeled_gross']/TRN,
            direct_pension_relief_trn=total['direct_relief']/TRN,
            behavior_pension_change_trn=total['behavior_benefit']/TRN,
            legacy_overlap_removed_trn=total['overlap']/TRN,
            public_benefit_delta_trn=benefit/TRN,
            additional_jobs=total['jobs'],hours_equivalent_workers=total['hours_equivalent'],
            additional_effective_labor=(total['jobs']+total['hours_equivalent'])*q['new_worker_effective_weight'],
            public_premium_delta_trn=total['premiums']/TRN,
            employee_premium_delta_trn=total['premiums']*.5/TRN,
            employer_premium_delta_trn=total['premiums']*.5/TRN,
            public_tax_delta_trn=public_tax/TRN,public_household_cash_delta_trn=hh/TRN,
            pension_insurer_cash_delta_trn=(total['premiums']-benefit)/TRN,
            general_budget_transfer_delta_trn=None,
            public_consumption_impulse_trn=hh*s['public_mpc']/TRN,
            extra_gross_wage_diagnostic_trn=total['wages']/TRN,
            new_public_entitlement_future_trn=None,
            national_pension_total_trn=None,national_premium_total_trn=None))
        assert close(total['sq_suspension']-total['f_suspension'],total['direct_relief']+total['behavior_benefit'])
        assert total['sq_suspension']>=-1e-6 and total['f_suspension']>=-1e-6
    return rows,strata_rows


def private_cap(cat, age, y, s, is_f):
    old=cat['old_cap']
    new=max(0.,cat['new_cap']-cat['other_plan_month'])
    # Previous participants not claiming basic pension can use extended age access.
    # Voluntary insured retain fund-shared cap until65; other over60 non-employees
    # represented by new eligible non-insured category with62k, not a universal right.
    if age>=60 and cat['id'] in ['SELF','DEPENDENT']:
        new=62000
    if age>=65:new=62000
    base=(old*11+new)/12 if y==2026 else new
    add=s['private_cap_add_month']*phase(y,s) if is_f and s['private'] else 0.
    return base+add,base,old


def private_ledger(c,s,baseline):
    q=c['private']; cats=q['categories']; total_count=sum(t['count'] for t in cats)
    cohorts=[]
    for cat in cats:
        denom=sum(n for _,n in cat['ages'])
        for age,n in cat['ages']:
            for inc in q['income_strata']:
                count=cat['count']*n/denom*inc['weight']
                assets=q['initial_participant_assets_trn']*TRN*count/total_count
                cohorts.append(dict(cat=cat,inc=inc,age2026=age,count=count,start=2026,SQ=assets,F=assets,transfer=0.))
    rows=[];dist=[]
    for i,m in enumerate(baseline):
        y=2026+i;idx=m['common_deflator']/(600/580)
        if i and s['new_entrants']:
            for cat in cats:
                for inc in q['income_strata']:
                    cohorts.append(dict(cat=cat,inc=inc,age2026=30-i,count=s['new_entrants']*cat['count']/total_count*inc['weight'],start=y,SQ=0.,F=0.,transfer=0.))
        inflation=m['common_deflator']/baseline[i-1]['common_deflator']-1 if i else 0.
        ret=(1+s['real_return'])*(1+inflation)-1
        acc={k:0. for k in ['SQ_contribution','F_contribution','SQ_balance','F_balance','SQ_payout','F_payout',
                              'SQ_income_tax_relief','F_income_tax_relief','SQ_local_tax_relief','F_local_tax_relief',
                              'SQ_payout_tax','F_payout_tax','SQ_return','F_return','SQ_previous','F_previous']}
        groups={v['id']:{k:0. for k in ['count','extra_contribution','income_relief','local_relief','payout_delta','payout_tax_delta']} for v in q['income_strata']}
        transfer_balance=transfer_payout=0.
        for co in cohorts:
            cat,inc=co['cat'],co['inc'];n=co['count'];age=co['age2026']+i
            G=groups[inc['id']];G['count']+=n
            cap,base,old=private_cap(cat,age,y,s,True)
            # Statutory limits held nominal; observed mean wages scale with common price
            # proxy. Cap uptake and affordability are explicit, uncalibrated behavior.
            mean=cat['mean_month']*idx*inc['affordability']
            desired_sq=mean+s['sq_cap_uptake']*max(0.,base-old)
            extra_desired=s['private_response']*max(0.,cap-base)*inc['affordability']
            csq=min(base,desired_sq)*12 if age<s['retire_age'] else 0.
            cf=min(cap,min(base,desired_sq)+extra_desired)*12 if age<s['retire_age'] else 0.
            taxable=inc['taxable_before_private_yen']*idx
            vals={}
            for pol,contrib in [('SQ',csq),('F',cf)]:
                before=co[pol];gain=before*ret
                grown=before+gain
                remaining=max(1,s['payout_years']-(age-s['retire_age']))
                payout=(grown/remaining if age>=s['retire_age'] else 0.)
                if age>=s['retire_age']+s['payout_years']:payout=grown
                co[pol]=grown+contrib*n-payout
                relief=(income_tax(taxable,y)-income_tax(max(0.,taxable-contrib),y))*n
                local=min(taxable,contrib)*.10*n
                # EET annuity proxy: taxable pension marginal income under NTA1600,
                # effective tax parameter then multiplies income delta, not principal.
                gross=payout/n if n else 0.
                base_public=1800000*idx
                payouttax=(pension_taxable(base_public+gross,max(age,65))-pension_taxable(base_public,max(age,65)))*s['payout_tax_rate']*n
                for key,val in [('contribution',contrib*n),('balance',co[pol]),('payout',payout),('income_tax_relief',relief),('local_tax_relief',local),('payout_tax',payouttax),('return',gain),('previous',before)]:acc[pol+'_'+key]+=val
                vals[pol]=(contrib*n,relief,local,payout,payouttax)
            # Track forgone outside assets: transfer principal would also be available
            # at retirement. Same return/withdrawal schedule is a neutral closure.
            transferred=(vals['F'][0]-vals['SQ'][0])*(1-s['new_saving_share'])
            outside=co['transfer']*(1+ret)
            outside_payout=outside/remaining if age>=s['retire_age'] else 0.
            if age>=s['retire_age']+s['payout_years']:outside_payout=outside
            co['transfer']=outside+transferred-outside_payout
            transfer_balance+=co['transfer'];transfer_payout+=outside_payout
            G['extra_contribution']+=vals['F'][0]-vals['SQ'][0]
            G['income_relief']+=vals['F'][1]-vals['SQ'][1]
            G['local_relief']+=vals['F'][2]-vals['SQ'][2]
            G['payout_delta']+=vals['F'][3]-vals['SQ'][3]
            G['payout_tax_delta']+=vals['F'][4]-vals['SQ'][4]
        delta={key:acc['F_'+key]-acc['SQ_'+key] for key in ['contribution','balance','payout','income_tax_relief','local_tax_relief','payout_tax','return']}
        transfer=delta['contribution']*(1-s['new_saving_share']);saving=delta['contribution']-transfer
        relief=delta['income_tax_relief']+delta['local_tax_relief']
        netpayout=delta['payout']-transfer_payout-delta['payout_tax']
        consume=relief*s['private_mpc']-saving+netpayout*s['retiree_mpc']
        # Principal payouts are dissaving, not current disposable income or GDP income.
        hh=relief-delta['payout_tax']
        row=dict(year=y,private_phase=phase(y,s) if s['private'] else 0.,
                 **{k+'_trn':v/TRN for k,v in acc.items()},
                 extra_private_contribution_trn=delta['contribution']/TRN,
                 extra_private_balance_trn=delta['balance']/TRN,
                 extra_private_payout_trn=delta['payout']/TRN,
                 asset_transfer_trn=transfer/TRN,new_saving_from_contribution_trn=saving/TRN,
                 displaced_outside_asset_balance_trn=transfer_balance/TRN,
                 forgone_outside_payout_trn=transfer_payout/TRN,
                 private_balance_minus_displaced_assets_trn=(delta['balance']-transfer_balance)/TRN,
                 private_income_tax_relief_delta_trn=delta['income_tax_relief']/TRN,
                 private_local_tax_relief_delta_trn=delta['local_tax_relief']/TRN,
                 private_payout_tax_delta_trn=delta['payout_tax']/TRN,
                 private_household_cash_delta_trn=hh/TRN,
                 private_consumption_impulse_trn=consume/TRN,
                 private_net_saving_delta_trn=(hh-consume)/TRN,
                 private_asset_direct_GDP_addition_trn=0.,
                 corporate_DC_total_balance_trn=None,death_inheritance_flow_trn=None)
        rows.append(row)
        for inc,g in groups.items():dist.append(dict(case=s['id'],year=y,income_stratum=inc,**{k:val if k=='count' else val/TRN for k,val in g.items()}))
        for pol in ['SQ','F']:
            assert close(acc[pol+'_balance'],acc[pol+'_previous']+acc[pol+'_return']+acc[pol+'_contribution']-acc[pol+'_payout'])
        assert close(delta['contribution'],transfer+saving)
    return rows,dist


def patch_engine(source,ledger):
    ns={'__name__':'pension_macro','_pension':ledger}
    def sub(a,b):
        nonlocal source
        assert source.count(a)==1,a
        source=source.replace(a,b)
    sub("admin_firm=value(admin_saving)+value(elderly_subsidy)-c['_elder'][i]['employer_contribution_base_trn']*ei",
        "admin_firm=value(admin_saving)+value(elderly_subsidy)-c['_elder'][i]['employer_contribution_base_trn']*ei-_pension[i]['employer_premium_delta_trn']")
    sub("        Ctarget=p['domestic_share']*(p['generic_mpc']*(cash+feedback-ss['household'])+ss['weighted_demand'])/coreD",
        "        cash+=_pension[i]['household_cash_delta_trn']\n        Ctarget=p['domestic_share']*(p['generic_mpc']*(cash+feedback-ss['household'])+ss['weighted_demand']+_pension[i]['consumption_impulse_trn']-p['generic_mpc']*_pension[i]['household_cash_delta_trn'])/coreD")
    sub("        taxdiag=tax+direct;", "        direct+=_pension[i]['direct_tax_delta_trn'];expenditure+=_pension[i]['public_benefit_delta_trn']\n        taxdiag=tax+direct;")
    exec(compile(source,'pension_macro.py','exec'),ns)
    return ns


def dependencies(c):
    foreign={'__name__':'fixed_foreign'}
    exec(compile(unpack(c['foreign_model']),'fixed_foreign.py','exec'),foreign)
    old,prev,dem,engine=foreign['dependencies'](c['foreign_inputs'])
    # Independently recapture final engine source from fixed dependency loader.
    code=zlib.decompress(base64.b64decode(c['foreign_inputs']['stage1_model_zlib_base64'])).decode()
    marker="ns2={'__name__':'elder_patched_TX'};"
    assert code.count(marker)==1
    captured={}
    temp={'__name__':'capture_fixed_engine','save_engine':lambda source:captured.update(source=source)}
    exec(compile(code.replace(marker,"save_engine(source);"+marker),'capture.py','exec'),temp)
    temp['dependency'](c['foreign_inputs']['stage1_inputs'])
    assert captured['source'].encode()==unpack(c['engine'])
    return foreign,old,prev,dem,engine


def base_path(c,foreign,old,prev,dem,engine,name):
    spec=next(x for x in c['foreign_inputs']['cases'] if x['id']==name)
    saved=foreign['macro'];cap={}
    def capture(cfg,eng,d,sq,elder,pol,case,end_year=2055):
        result=saved(cfg,eng,d,sq,elder,pol,case,end_year)
        if case==name:cap.update(d=copy.deepcopy(d),sq=copy.deepcopy(sq),elder=copy.deepcopy(elder),macro=result)
        return result
    foreign['macro']=capture
    try:cap['foreign']=foreign['calculate'](c['foreign_inputs'],spec,old,prev,dem,engine)
    finally:foreign['macro']=saved
    assert 'd' in cap
    return cap


def calculate(c,s,base,foreign):
    s={**c['defaults'],**s}
    assert s['ramp_years']>=1 and 0<=s['new_saving_share']<=1 and s['real_return']>-.5
    pub,ps=public_ledger(c,s,base['elder'],base['macro'])
    priv,ds=private_ledger(c,s,base['macro'])
    hooks=[]
    for a,b in zip(pub,priv):
        hooks.append(dict(household_cash_delta_trn=a['public_household_cash_delta_trn']+b['private_household_cash_delta_trn'],
            consumption_impulse_trn=a['public_consumption_impulse_trn']+b['private_consumption_impulse_trn'],
            employer_premium_delta_trn=a['employer_premium_delta_trn'],public_benefit_delta_trn=a['public_benefit_delta_trn'],
            direct_tax_delta_trn=a['public_tax_delta_trn']-b['private_income_tax_relief_delta_trn']-b['private_local_tax_relief_delta_trn']+b['private_payout_tax_delta_trn']))
    d=copy.deepcopy(base['d'])
    for t,a in zip(d,pub):t['effective_productive_workers']+=a['additional_effective_labor']
    engine=patch_engine(unpack(c['engine']).decode(),hooks)
    macro=foreign['macro'](c['foreign_inputs'],engine,d,base['sq'],base['elder'],'F',s['id'])
    rows=[]
    for i,(r,a,b,h,e,f) in enumerate(zip(macro,pub,priv,hooks,base['elder'],base['foreign'])):
        row=dict(case=s['id'],backdrop=s['backdrop'],year=r['year'],policy='F',
                 **{**{k:v for k,v in a.items() if k!='year'},**{k:v for k,v in b.items() if k!='year'},**h})
        for k in ['real_gdp_trn','nominal_gdp_trn','core_real_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn','household_disposable_nominal_trn','household_consumption_real_proxy_trn','C_demand_real_trn','I_policy_real_trn','capital_total_real_trn','labor_force_population_proxy','common_deflator','supply_binding']:
            row[k]=r[k]
        row.update(population=f['population'],foreign_resident_stock=f['foreign_resident_stock'],foreign_jobs=f['foreign_jobs'],foreign_effective_labor=f['foreign_effective_labor'],
            elder_employed=e['SQ_elder_employed']+e['F_extra_jobs']+a['additional_jobs'],
            elder_effective_added=e['effective_extra']+a['additional_effective_labor'],
            legacy_elder_extra_jobs=e['F_extra_jobs'],legacy_pension_support_trn=e['pension_support_base_trn']*base['macro'][i]['common_deflator']/(600/580),
            preserved_foreign_program_cost_trn=f['government_program_nominal_trn'],
            public_premium_receipts_delta_trn=a['public_premium_delta_trn'],
            extended_expenditure_partial_trn=r['expenditure_diagnostic_trn']+f['government_program_nominal_trn'],
            extended_fiscal_balance_partial_trn=r['fiscal_balance_partial_trn']-f['government_program_nominal_trn'],
            known_public_balance_delta_trn=r['fiscal_balance_partial_trn']-base['macro'][i]['fiscal_balance_partial_trn']+a['public_premium_delta_trn'],
            household_consumption_nominal_proxy_trn=r['household_consumption_real_proxy_trn']*r['common_deflator'],
            household_net_saving_change_before_macro_feedback_trn=h['household_cash_delta_trn']-h['consumption_impulse_trn'],
            original_real_gdp_trn=base['macro'][i]['real_gdp_trn'],
            pension_GDP_delta_trn=r['real_gdp_trn']-base['macro'][i]['real_gdp_trn'],
            nominal_GDP_delta_trn=r['nominal_gdp_trn']-base['macro'][i]['nominal_gdp_trn'],
            modeled_pension_payment_trn=a['modeled_full_earnings_pension_trn']-a['F_modeled_suspension_trn'],
            national_total_household_net_saving_trn=None,full_public_pension_balance_trn=None)
        assert close(row['labor_force_population_proxy'],f['total_effective_labor']+a['additional_effective_labor'])
        rows.append(row)
    return rows,ps,ds


def run(inp,out):
    c=json.loads(Path(inp).read_text());out=Path(out);out.mkdir(parents=True,exist_ok=True)
    foreign,old,prev,dem,engine=dependencies(c)
    bases={k:base_path(c,foreign,old,prev,dem,engine,n) for k,n in [('ZERO','HIST_ZERO'),('MEDIUM','HIST_COMBINED_MEDIUM'),('SQ','SQ_HIST')]}
    paths={};ps=[];ds=[]
    for spec in c['cases']:
        rows,p,d=calculate(c,spec,bases[spec['backdrop']],foreign)
        paths[spec['id']]=rows;ps+=p;ds+=d
    regression=0
    previous=c['foreign_reference']
    assert previous is not None,'Missing immutable foreign reference'
    for backdrop,name in [('ZERO','HIST_ZERO'),('MEDIUM','HIST_COMBINED_MEDIUM'),('SQ','SQ_HIST')]:
        prior={int(r['year']):r for r in previous if r['case']==name}
        for i,r in enumerate(bases[backdrop]['foreign']):
            for key in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','population','foreign_jobs','foreign_resident_stock','total_effective_labor']:
                assert close(r[key],float(prior[r['year']][key])),(backdrop,r['year'],key)
                regression+=1
    metrics=['real_gdp_trn','nominal_gdp_trn','elder_employed','labor_force_population_proxy',
             'household_disposable_nominal_trn','household_consumption_nominal_proxy_trn',
             'tax_diagnostic_trn','extended_expenditure_partial_trn','extended_fiscal_balance_partial_trn',
             'public_benefit_delta_trn','public_premium_delta_trn','extra_private_balance_trn']
    interactions=[];comparison=[]
    for backdrop in ['ZERO','MEDIUM']:
        for i,y in enumerate(YEARS):
            z,a,b,ab=[paths[backdrop+'_'+n][i] for n in ['ZERO','PUBLIC','PRIVATE','COMBINED']]
            base=bases[backdrop]['macro'][i]
            for key in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','household_disposable_nominal_trn','household_consumption_real_proxy_trn']:
                assert close(z[key],base[key]),('ZERO regression',backdrop,y,key);regression+=1
            row=dict(backdrop=backdrop,year=y)
            for key in metrics:
                row[key+'_public']=a[key]-z[key];row[key+'_private']=b[key]-z[key]
                row[key+'_combined']=ab[key]-z[key];row[key+'_interaction']=ab[key]-a[key]-b[key]+z[key]
            interactions.append(row)
    annual=[]
    for name,rows in paths.items():
        for i,r in enumerate(rows):
            sq=bases['SQ']['macro'][i];z=paths[r['backdrop']+'_ZERO'][i]
            r['F_minus_SQ_real_GDP_trn']=r['real_gdp_trn']-sq['real_gdp_trn']
            r['F_minus_SQ_nominal_GDP_trn']=r['nominal_gdp_trn']-sq['nominal_gdp_trn']
            r['SQ_real_gdp_trn']=sq['real_gdp_trn'];r['SQ_nominal_gdp_trn']=sq['nominal_gdp_trn']
            r['household_disposable_change_trn']=r['household_disposable_nominal_trn']-z['household_disposable_nominal_trn']
            r['household_consumption_change_trn']=r['household_consumption_nominal_proxy_trn']-z['household_consumption_nominal_proxy_trn']
            for k,v in r.items():
                assert not isinstance(v,float) or math.isfinite(v),(name,r['year'],k)
            if r['year']<min(c['defaults']['start_year'],next(x for x in c['cases'] if x['id']==name).get('start_year',2030)):
                assert close(r['pension_GDP_delta_trn'],0.)
            annual.append(r)
            comparison.append(dict(case=name,year=r['year'],**{k:r[k] for k in ['real_gdp_trn','pension_GDP_delta_trn','F_minus_SQ_real_GDP_trn','additional_jobs','hours_equivalent_workers','additional_effective_labor','public_benefit_delta_trn','employee_premium_delta_trn','employer_premium_delta_trn','extra_private_contribution_trn','extra_private_balance_trn','asset_transfer_trn','new_saving_from_contribution_trn','extra_private_payout_trn','household_disposable_change_trn','household_consumption_change_trn','known_public_balance_delta_trn']}))
    summary=[r for r in comparison if r['year'] in [2026,2030,2035,2045,2055]]
    # Genuine falsification conditions: F cap with no uptake cannot produce extra assets;
    # statutory release with no labor behavior must leave every labor quantity unchanged.
    no=paths['MEDIUM_NO_PRIVATE_RESPONSE'];assert all(close(r['extra_private_contribution_trn'],0.) and close(r['extra_private_balance_trn'],0.) for r in no)
    assert all(close(r['additional_jobs'],0.) and close(r['additional_effective_labor'],0.) for r in paths['MEDIUM_NO_BEHAVIOR'])
    assert all(close(r['new_saving_from_contribution_trn'],0.) for r in paths['MEDIUM_ALL_TRANSFER'])
    assert all(close(r['asset_transfer_trn'],0.) for r in paths['MEDIUM_ALL_NEW_SAVING'])
    validation=dict(status='PASS_LOCAL_MODEL_CHECKS',cases=len(paths),annual_rows=len(annual),years=30,old_and_zero_regression_cells=regression,
        checks=['fixed dependencies bytes','recaptured macro exact match','old foreign results','zero overlay equality','public suspension identity','private cohort stock-flow identity','remaining labor pool bounds','zero behavior','zero uptake','pure asset-transfer control','finite outputs','factorial effects'],
        limitations='No causal effect calibration; national pension and private/DC totals not estimated. Local tests are not delivery or custody.',input_sha256=hashlib.sha256(Path(inp).read_bytes()).hexdigest())
    for name,rows in [('Annual.csv',annual),('Comparison.csv',comparison),('Summary.csv',summary),('Interactions.csv',interactions),('Public_Strata.csv',ps),('Private_Distribution.csv',ds)]:dump(out/name,rows)
    # SQ reform satellite ledger: not added again to macro already containing SQ aggregate flows.
    sqspec={**c['defaults'],'id':'SQ_DIAGNOSTIC','public':False,'private':False}
    sp,_=public_ledger(c,sqspec,bases['SQ']['elder'],bases['SQ']['macro']);sv,_=private_ledger(c,sqspec,bases['SQ']['macro'])
    dump(out/'StatusQuo.csv',[dict(year=2026+i,**{k:v for k,v in p.items() if k!='year'},**{k:v for k,v in q.items() if k!='year'},**{k:bases['SQ']['macro'][i][k] for k in ['real_gdp_trn','nominal_gdp_trn','household_disposable_nominal_trn','household_consumption_real_proxy_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','labor_force_population_proxy']},elder_employed=bases['SQ']['elder'][i]['SQ_elder_employed'],population=bases['SQ']['foreign'][i]['population'],foreign_jobs=bases['SQ']['foreign'][i]['foreign_jobs']) for i,(p,q) in enumerate(zip(sp,sv))])
    (out/'Validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(validation,ensure_ascii=False))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('inputs');ap.add_argument('--outdir',default='replay');a=ap.parse_args();run(a.inputs,a.outdir)
