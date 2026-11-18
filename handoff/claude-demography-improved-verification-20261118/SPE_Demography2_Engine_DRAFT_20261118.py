# Independent recompute of SPE_F_TX_Model_DRAFT_20261118 (47 paths x 30 years = 1,410 rows) by Claude.
# Re-implemented from the policy text and from reading the account structure; the model file is NOT imported or executed here.
# Only the INPUT json (parameters/cases) is shared with the model, so this checks the arithmetic of the engine, not the input values.
# Usage: python3 -I SPE_F_TX_Independent_Recalc_DRAFT_20261118.py <Inputs.json> <Annual_Comparison.csv> [<prior Text CSV db52249f> <DM CSV 30b926dd>]
import json, csv, sys, copy, math
cfg = json.load(open(sys.argv[1], encoding='utf-8'))
R = list(csv.DictReader(open(sys.argv[2], encoding='utf-8')))
D = {(r['case'], int(r['year'])): r for r in R}
A = cfg['initial']; SEC = cfg['sector_inputs']
z = lambda x: 0. if x is None else x

def ramp(y, s, n=3): return 0. if y < s else min(1., (y - s + 1) / n)
def sched(d, y):
    ks = sorted(int(k) for k in (d or {}) if int(k) <= y)
    return d[str(ks[-1])] if ks else 0.

def params(spec):
    p = {}
    for k in ('common_model', 'policy_inputs', 'exogenous_shocks'): p.update(copy.deepcopy(cfg[k]))
    prof = copy.deepcopy(cfg['baseline_profiles'][spec['profile']]); prof.update(spec.get('profile_override', {}))
    m = copy.deepcopy(cfg['common_model']['migration']); m.update(copy.deepcopy(cfg['policy_inputs']['migration'])); m.update(spec.get('migration_override', {}))
    F = spec['policy'] == 'F'
    p.update(spec.get('policy_override', {}))
    p['elasticity'] = prof['elasticity']; p['climate_anchor'] = prof['climate_anchor']; p['medical_mode'] = spec.get('medical_mode', 'UNALLOCATED_COMPAT')
    omit = []
    if not F:
        omit = ['food', 'social', 'firm', 'medical', 'hubs', 'extra', 'triggers']
        for k in ['investment_flow_share', 'education_flow_share', 'education_program_budget', 'scholarship_spend', 'elderly_additional_workers', 'elderly_subsidy_per_worker_man', 'pension_relief_per_worker_man', 'invoice_cost_saving', 'stamp_tax_removed', 'digital_system_cost', 'education_bond_share']: p[k] = 0.
        p['growth_hypothesis_mode'] = 'STRUCTURAL_ONLY'; p['circuit_growth_floor'] = None; p['circuit_gini_ceiling'] = None
    return p, prof, m, F, omit

def rates(p, y):
    tau = .10 if y < p['year8'] else .08 if y < p['year5'] else .05
    if y < p['food_zero_start']: food = .08
    elif y < p['food_eight_start']: food = 0.
    elif y < p['year5']: food = .08
    else: food = .05
    return tau, food

def hubcount(p, y): return p['hub_target'] * min(1., max(0., (y - 2027) / 8))

def tax_flows(p, y, N, omit, halt):
    tau, food = rates(p, y); gen = N * p['household_income_share'] * p['taxable_share']
    fb = None if p['food_share_of_tax_base'] is None else gen * p['food_share_of_tax_base']
    rr = (.1 - tau) * (gen - z(fb)); fr = 0. if 'food' in omit else (None if fb is None else (.08 - food) * fb)
    relief = rr + z(fr); hh = relief; tax = -relief; inv = 0.; pub = 0.; cr_all = 0.; outv = 0.; unk = int(fr is None); m = {}
    for s, a in SEC.items():
        st = p.get('sector_starts', {}).get(s, p['base_start']); act = (y >= st) and not halt
        Rv = a['R2025'] * (1 + p['sector_nominal_growth']) ** (y - 2025); P = a['p'] * Rv
        cred = tau * P if act else 0.; out = tau * Rv if act else 0.; cut = (.1 - tau) * P
        if s == 'medical':
            pat = p['patient_share'] * out; ins = p['insurer_share'] * out; pb = p['public_share'] * out
            prem = p['initial_premium_pass'] * ins; res = ins - prem; md = p['medical_mode']
            xp = res if md == 'PREMIUM' else 0.; xt = res if md == 'PUBLIC' else 0.; xi = res if md == 'INTERNAL' else 0.; xu = res if md == 'UNALLOCATED_COMPAT' else 0.
            priv = pat + prem + xp; pb += xt
            m = dict(medical_output_vat=out, medical_insurer_vat=ins, medical_initial_premium=prem, medical_extra_premium=xp, medical_public_topup=xt, medical_internal=xi, medical_unallocated=xu, _pat=pat, _pubm=pb)
        else:
            pb = out * (p['education_public_payer_share'] if s == 'education' else 0.); priv = out - pb
        biz = (1 - a['price']) * (cut + cred)
        hh += a['price'] * (cut + cred) + a['wage'] * biz - priv; inv += a['invest'] * biz; pub += pb
        tax += out - cred - cut; cr_all += cred; outv += out
    en = 0.
    for s, B in p['extra_bases'].items():
        if 'extra' in omit or halt or y < p.get('extra_base_start', p['base_start']): continue
        q = p['extra_input_ratios'][s]
        if any(v is None for v in [B, q, p['extra_base_private_share'], p['extra_base_public_share']]): unk += 1; continue
        base = B * N / A['nominal_gdp']; out = tau * base; cr = tau * base * q
        en += out - cr; hh += p['extra_credit_price_share'] * cr - out * p['extra_base_private_share']; inv += p['extra_business_investment_share'] * (1 - p['extra_credit_price_share']) * cr
        pub += out * p['extra_base_public_share']
    tax += en
    return dict(hh=hh, tax=tax, inv=inv, pub=pub, relief=relief, en=en, unk=unk, **m)

def social(p, y, relief, gadd, refund, off):
    if off: return dict(prem=0., kind=0., vr=0., hh=0., gov=0., wd=0.)
    co = p['cohorts']
    if y < p['insurance_start']: prem = kind = 0.; wd = 0.
    elif co is None: prem = kind = None; wd = None
    else:
        rate = p['insurance_reduction'] + gadd if p['gini_increment_mode'] == 'PERCENTAGE_POINTS' else p['insurance_reduction'] * (1 + gadd)
        rate = min(rate, 1.)
        low = [r for r in co if r['income_man'] <= 500]; kin = [r for r in co if r['income_man'] <= 300]
        prem = sum(r['income_man'] * r['persons'] * r['contribution_rate'] * rate / 1e8 for r in low)
        wd = sum(r['income_man'] * r['persons'] * r['contribution_rate'] * rate * r['mpc'] / 1e8 for r in low)
        kind = None if p['in_kind_per_eligible_man'] is None else sum(r['persons'] for r in kin) * p['in_kind_per_eligible_man'] / 1e8
        if p['in_kind_per_eligible_man'] is not None: wd += sum(r['persons'] * p['in_kind_per_eligible_man'] * r['mpc'] / 1e8 for r in kin)
    vr = None if p['vat_relief_social_return_fraction'] is None else relief * p['vat_relief_social_return_fraction']
    cash = z(prem) + z(kind) + z(vr) + z(refund)
    gov = cash - z(vr) if p['vat_return_interpretation'] == 'RECLASSIFY_PRICE_RELIEF' else cash
    return dict(prem=prem, kind=kind, vr=vr, hh=cash, gov=gov, wd=z(wd) + p['generic_mpc'] * (z(vr) + z(refund)))

def firm(p, y, N, off):
    if off: return dict(td=0., cr=0., inv=0., rel=0., hum=0., unk=0)
    sc = N / A['nominal_gdp']; td = cr = inv = rel = None; hum = 0.
    if y < p['corp_start']: td = cr = inv = 0.
    else:
        if None not in (p['corp_profit_base'], p['corp_reference_rate'], p['defense_surcharge_schedule']):
            td = p['corp_profit_base'] * sc * (.23 * (1 + sched(p['defense_surcharge_schedule'], y)) - p['corp_reference_rate'])
        if y < p['investment_start']: cr = 0.
        elif p['tax_incentive_eligible'] is True and None not in (p['hyper_eligible_investment'], p['hyper_extra_deduction'], p['training_eligible_spend'], p['training_credit_rate']):
            cr = sc * (.23 * p['hyper_eligible_investment'] * p['hyper_extra_deduction'] + p['training_eligible_spend'] * p['training_credit_rate'])
        if p['firm_investment_response'] is not None and td is not None and cr is not None: inv = p['firm_investment_response'] * (cr - td)
    if p['governance_compliance'] is True and y >= 2028 and p['governance_release_fraction'] is not None and p['governance_eligible_retained'] is not None:
        rel = p['governance_eligible_retained'] * p['governance_release_fraction'] * ramp(y, 2028)
        g = p['governance_allocation']; hum = rel * g['human']
        if inv is not None: inv += rel * (g['equipment'] + g['research'])
    return dict(td=td, cr=cr, inv=inv, rel=rel, hum=hum, unk=sum(x is None for x in [td, cr, inv, rel]))

def medical(p, y, off, hub_off, prev):
    if off or y < p['medical_start']: return dict(hub=0., gov=0., hh=0., ib=0., unk=0, shift=0., high=0., award=0., sav=0., pal=0., tr=0., prov=0.)
    sh = 0. if not p['annex4_patient_thirty'] else (None if p['medical_total_bill_base'] is None or p['current_patient_share'] is None else p['medical_total_bill_base'] * (.3 - p['current_patient_share']))
    hi = None if p['high_cost_eligible_amount'] is None or p['high_cost_relief_fraction'] is None else p['high_cost_eligible_amount'] * p['high_cost_relief_fraction']
    aw = None if any(p[k] is None for k in ['preventive_eligible_fee', 'preventive_award', 'equipment_eligible_fee', 'equipment_award']) else p['preventive_eligible_fee'] * p['preventive_award'] + p['equipment_eligible_fee'] * p['equipment_award']
    sav = p['palliative_saving_base']; pal = p['palliative_subsidy'] if p['palliative_start'] <= y < p['palliative_start'] + 5 else 0.
    tr = p['transition_fee_support'] if 2028 <= y <= 2030 else 0.
    hub = 0. if hub_off else (None if p['hub_unit_cost'] is None else (hubcount(p, y) - prev) * p['hub_unit_cost'])
    pd = -z(sh) + z(hi) + z(aw) - z(sav); fr = p['medical_public_payer_fraction']
    gov = pd * (fr if fr is not None else 0.) + z(pal) + z(tr) + z(hub)
    return dict(hub=hub, gov=gov, hh=-z(sh) + z(hi), ib=None if fr is None else -pd * (1 - fr), unk=int(fr is None), shift=sh, high=hi, award=aw, sav=sav, pal=pal, tr=tr, prov=z(aw) - z(sav) + z(pal) + z(tr))

def run(spec, prepared=None):
    p, prof, m, F, omit = prepared if prepared else params(spec); sh = cfg['exogenous_shocks']
    T = spec['traj']; S = spec['sq_traj']; legacy = spec.get('gdp_labor_mode') == 'LEGACY_POP'
    out = {}; C = I = K = H = 0.; fIs = 0.; fcs = 0.; Y = A['real_gdp']; N = A['nominal_gdp']; cY = Y; cN = N; tax = A['tax']
    cpop = T[0]['population']; ppop = 0.; pop = cpop; b = T[0]['births_calendar']; d = T[0]['deaths_calendar']
    lab = pop * p['labor_initial_ratio'] if legacy else T[0]['effective_productive_workers']; elab = lab
    fs = T[0]['foreign']; fs0 = fs; finc = 0.; gap = 0.; cD = N / Y; pN = N; pY = Y; ecore = A['expenditure_proxy']
    tg_edu = False; tg_gini = None; tg_mig = False; halt = False; icum = 0.; rcum = 0.; prevhub = 0.; lastg = 0.
    for y in range(2026, 2056):
        i = y - 2026; trg = F and 'triggers' not in omit
        if y == 2035 and trg:
            tg_edu = lastg < .012; ob = p['gini_observations'].get(str(y)); tg_gini = None if ob is None else ob > .36; tg_mig = pop < 1e8
        if y >= p['circuit_evaluation_start'] and i and p['circuit_growth_floor'] is not None: halt = lastg < p['circuit_growth_floor']
        if y >= p['circuit_evaluation_start'] and p['circuit_gini_ceiling'] is not None:
            ob = p['gini_observations'].get(str(y))
            if ob is not None: halt = halt or ob > p['circuit_gini_ceiling']
        oil = sh['oil_gdp_loss'] if (y == 2026 and p['apply_oil_to_initial']) else 0.
        risk = oil + (sh['conflict_gdp_loss'] if y == 2027 else 0.) + (sh['quake_gdp_loss'] if y == 2031 else 0.) + (sh['disaster_gdp_loss'] if y >= p['disaster_anchor'] and (y - p['disaster_anchor']) % 3 == 0 else 0.) + (sh['climate_gdp_loss'] if y >= p['climate_anchor'] and (y - p['climate_anchor']) % 2 == 0 else 0.)
        infl = .02 + (.02 if oil else 0.) + (sh['conflict_gdp_loss'] if y == 2027 else 0.)
        mg = 0.; cflow = preq = pacc = 0.; ceil = None; aging = 0.; lg = 0.; fr_ = 0.
        if i:
            t = T[i]; q = S[i]
            b = t['births_calendar']; d = t['deaths_calendar']
            cflow = q['foreign_net_migration']; mg = t['foreign_net_migration']
            preq = pacc = mg - cflow
            fs = t['foreign']; finc = fs - fs0
            cpop = q['population']; ppop = t['population'] - q['population']; pop = t['population']
            ew = z(p['elderly_additional_workers']) * ramp(y, 2028) if F and not halt else 0.
            if legacy: ln = pop * p['labor_initial_ratio'] + (fs - fs0) * (p['foreign_labor_participation'] - p['labor_initial_ratio']) + ew
            else: ln = t['effective_productive_workers'] + ew
            lg = ln / lab - 1; lab = ln; elab = ln
            g = p['base_growth'] + p['labor_response'] * lg - risk
            ecore *= 1 + sched(prof['expenditure_growth'], y)
            cY *= 1 + g; cN *= 1 + g + infl; cD = cN / cY
        elif oil: cY *= 1 - oil; cN *= 1 - oil + .02; cD = cN / cY
        f = tax_flows(p, y, cN, omit, halt)
        if not F or i == 0: f = {k: (0. if (isinstance(v, (int, float)) or v is None) else v) for k, v in f.items()} if not F else {k: (0. if isinstance(v, (int, float)) else v) for k, v in f.items()}
        refund = None
        if trg and i:
            k = str(y - 1); ac = (p['vat_observed_revenue'] or {}).get(k); ex = (p['vat_expected_revenue'] or {}).get(k)
            if ac is not None and ex is not None: refund = .5 * max(ac - ex, 0.)
        ga = p['gini_relief_increment'] if tg_gini else 0.
        ss = social(p, y, f['relief'], ga, refund, ('social' in omit) or halt or not i)
        fm = firm(p, y, cN, ('firm' in omit) or halt or not i)
        md = medical(p, y, ('medical' in omit) or halt or not i, 'hubs' in omit, prevhub)
        if i: prevhub = hubcount(p, y) if F else 0.
        em = z(p['education_trigger_multiplier']) if (tg_edu and p['education_trigger_multiplier'] is not None) else 1.
        act = i and not halt
        invf = None if p['investment_flow_share'] is None else (p['investment_flow_share'] * cN * ramp(y, p['investment_start']) if act else 0.)
        bud = p['education_program_budget']; eb = bud if bud is not None else (None if p['education_flow_share'] is None else p['education_flow_share'] * cN)
        ef = None if eb is None else (eb * ramp(y, p['education_start']) * em if act else 0.)
        sch = None if p['scholarship_spend'] is None else (p['scholarship_spend'] * ramp(y, p['education_start']) if act else 0.)
        ebond = None if ef is None or sch is None or p['education_bond_share'] is None else (ef + sch) * p['education_bond_share']
        inv_nom = z(invf) + z(fm['inv']) + f['inv'] + z(md['hub']); edu_nom = z(ef) + z(sch) + fm['hum']
        w = p['elderly_additional_workers']
        els = None if w is None or p['elderly_subsidy_per_worker_man'] is None else (w * ramp(y, 2028) * p['elderly_subsidy_per_worker_man'] / 1e8 if i else 0.)
        pen = None if w is None or p['pension_relief_per_worker_man'] is None else (w * ramp(y, 2028) * p['pension_relief_per_worker_man'] / 1e8 if i else 0.)
        adm = None if p['invoice_cost_saving'] is None else (p['invoice_cost_saving'] if (y >= p['admin_start'] and i) else 0.)
        af = z(adm) + z(els); frp = z(p['firm_investment_response']) if not halt else 0.
        inv_nom += frp * af; fsrc = z(fm['cr']) - z(fm['td']) + z(fm['rel']) + af; finv = z(fm['inv']) + frp * af; funi = fsrc - finv - fm['hum']
        fb = p['income_feedback'] * gap * cD; rec = z(ss['vr']) if p['vat_return_interpretation'] == 'RECLASSIFY_PRICE_RELIEF' else 0.
        cash = f['hh'] - rec + ss['hh'] + md['hh'] + z(pen)
        Ct = p['domestic_share'] * (p['generic_mpc'] * (cash + fb - ss['hh']) + ss['wd']) / cD
        if i:
            C = (1 - p['lambda_C']) * C + p['lambda_C'] * Ct; I = (1 - p['lambda_I']) * I + p['lambda_I'] * inv_nom / cD
            fIs = (1 - p['lambda_I']) * fIs + p['lambda_I'] * finv / cD; fcs += fsrc - fIs * cD - fm['hum']
        sup = p['capital_yield'] * (1 - p['depreciation']) * K + p['education_yield'] * (1 - p['education_decay']) * H
        el = p['education_level_effect'] * cY * ramp(y, p['education_start']) if p['growth_hypothesis_mode'] == 'EDUCATION_LEVEL' else 0.
        fin = 0.
        if p['growth_hypothesis_mode'] == 'FINITE_FLOW_HYPOTHESIS' and p['education_start'] <= y <= 2035: fin = cY * (p['consumption_hypothesis_pp'] + p['investment_hypothesis_pp']) * ramp(y, p['investment_start'])
        des = cY + p['capacity_absorption'] * sup + C + I + edu_nom / cD + el + fin; cap = cY + sup + p['slack'] * cY + el
        Y = min(des, cap) if spec['supply_cap'] else des; un = max(des - Y, 0.); pr = p['price_pressure_coefficient'] * un / cY
        N = Y * cD * (1 + pr if spec.get('price_feedback', True) else 1)
        if i or oil: tax = min(tax * (1 + (N / pN - 1) * p['elasticity']) * (sh['quake_tax_factor'] if y == 2031 else 1.), N * p['tax_cap_ratio'])
        direct = f['tax'] + z(fm['td']) - z(fm['cr']) - p['promotion_fiscal_cost_share'] * z(invf)
        stamp = None if p['stamp_tax_removed'] is None else (p['stamp_tax_removed'] if y >= p['admin_start'] else 0.); direct -= z(stamp)
        dig = None if p['digital_system_cost'] is None else (p['digital_system_cost'] if p['admin_start'] <= y <= 2040 else 0.)
        exp = ecore + f['pub'] + ss['gov'] + md['gov'] + z(ef) + z(sch) + z(els) + z(pen) + z(dig)
        td = tax + direct; Kp = K; Hp = H
        if i: K = (1 - p['depreciation']) * K + I; H = (1 - p['education_decay']) * H + edu_nom / cD
        gap = Y - cY; icum += f.get('medical_internal', 0.)
        rcum += z(fm['rel'])
        ratio = None if fs is None else fs / pop
        mism = None if m['target_stock_definition_code'] is None else int(m['stock_definition_code'] != m['target_stock_definition_code'])
        dstat = 'TARGET_DEFINITION_UNSPECIFIED' if mism is None else 'DEFINITION_MISMATCH' if mism else 'DEFINITIONS_MATCH_BY_INPUT_ONLY'
        rstat = 'UNKNOWN_INITIAL_STOCK' if ratio is None else 'BELOW3' if ratio < .03 else 'WITHIN3TO5' if ratio <= .05 else 'ABOVE5'
        MI = f.get('medical_internal', 0.); MU = f.get('medical_unallocated', 0.)
        out[y] = dict(case=spec['id'], year=y, policy_role='F' if F else 'STATUSQUO_INCREMENTAL_REFERENCE', baseline_profile=spec['profile'], supply_cap_enabled=int(spec['supply_cap']), price_feedback_enabled=int(spec.get('price_feedback', True)),
            real_gdp_trn=Y, nominal_gdp_trn=N, common_deflator=cD, core_real_gdp_trn=cY, tax_macro_trn=tax, tax_diagnostic_trn=td, expenditure_diagnostic_trn=exp, fiscal_balance_partial_trn=td - exp, funding_gap_proxy_trn=max(exp - td, 0.),
            common_expenditure_core_trn=ecore, aging_drag_pp=aging * 100, labor_growth_pct=lg * 100, common_tax_elasticity=p['elasticity'],
            household_disposable_nominal_trn=p['household_income_share'] * cN + cash + fb, household_consumption_real_proxy_trn=p['household_income_share'] * cY + C, I_policy_real_trn=I, capital_total_real_trn=p['capital_ratio'] * cY + K,
            population_persons=pop, births_persons=b, deaths_persons=d, labor_force_population_proxy=elab, common_population_persons=cpop, policy_population_increment_persons=ppop,
            common_migration_net_flow=cflow, policy_migration_requested_net_flow=preq, policy_migration_accepted_net_flow=pacc, total_migration_net_flow=mg,
            foreign_stock_conditional_persons=fs, foreign_stock_population_ratio=ratio, foreign_stock_ratio_status=rstat, foreign_definition_status=dstat, foreign_definition_mismatch_flag=mism,
            foreign_ratio_exceeds_5=None if ratio is None else int(ratio > .05), foreign_increment_tracked_persons=finc,
            foreign_gdp_contribution_ratio=None if fs is None or m['foreign_value_added_per_person_trn'] is None else fs * m['foreign_value_added_per_person_trn'] / cN,
            migration_enforcement_mode=m['enforcement_mode'], migration_flow_interpretation=m['F_flow_interpretation'], foreign_eligibility_status='SOURCE_CONDITIONS_REGISTERED;INDIVIDUAL_COMPLIANCE_UNVERIFIED',
            desired_real_gdp_trn=des, supply_ceiling_real_gdp_trn=cap, supply_binding=int(des > cap + 1e-9) if spec['supply_cap'] else 0, unmet_demand_real=un, excess_demand_relative_to_ceiling_trn=max(des - cap, 0.),
            price_pressure_proxy=pr, nominal_price_pressure_component_trn=N - Y * cD,
            medical_output_vat=f.get('medical_output_vat', 0.), medical_insurer_vat=f.get('medical_insurer_vat', 0.), medical_initial_premium=f.get('medical_initial_premium', 0.), medical_extra_premium=f.get('medical_extra_premium', 0.),
            medical_public_topup=f.get('medical_public_topup', 0.), medical_internal=MI, medical_internal_cumulative=icum, medical_unallocated=MU, medical_insurer_operating_balance=-MI - MU, medical_insurer_financing_balance=-MU,
            full_F_GDP_trn=None, gini_actual=None, PB_trn=None, actual_bond_issuance_trn=None, _halt=int(halt), _tg_mig=int(tg_mig), _ceil=ceil)
        lastg = (Y / pY - 1) if (i or oil) else 0.; pY = Y; pN = N
    return out

