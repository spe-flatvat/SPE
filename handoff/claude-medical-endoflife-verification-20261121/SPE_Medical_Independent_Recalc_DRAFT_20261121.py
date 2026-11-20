#!/usr/bin/env python3
# Claude independent recalculation of the medical / end-of-life modules (Commit d2578751...).
# Shares only data with the original (Inputs.json, price index and population from f-integrated Annual.csv);
# the formulas below were written from the code and Reproduce.md semantics in a different structure.
# Usage: python3 -I <this> <repo_root_dir_at_d257875>
import sys, csv, json, math, os
R = sys.argv[1]; D = os.path.join(R, 'handoff/f-medical-common-20261121')
IN = json.load(open(os.path.join(D, 'Inputs.json')))
INT = [r for r in csv.DictReader(open(os.path.join(R, 'handoff/f-integrated-20261121/Annual.csv'))) if r['case'] == 'FULL_ADDITIONAL']
DEF = [float(r['common_deflator']) for r in sorted(INT, key=lambda r: int(r['year']))]
POP = [float(r['population']) for r in sorted(INT, key=lambda r: int(r['year']))]
clamp = lambda x, lo, hi: max(lo, min(hi, x))
def rd(f): return list(csv.DictReader(open(os.path.join(D, f))))
def cases():
    out = {}
    for c in IN['cases']:
        s = dict(IN['defaults']); s.update(c); out[c['id']] = s
    return out
# ---------------- common end-of-life ----------------
def common(y, idx, scale, p, fin):
    en = p['enabled']; dl = p.get('timeline_delay', 0)
    rp = lambda st, n: clamp((y - st - dl + 1) / n, 0, 1) if en else 0.
    impl = rp(2032, 4); sup = rp(2027, 14) * p.get('supply_capacity_factor', 1.); regph = rp(2031, 10)
    adopt = regph * p['adoption_target']
    prev = clamp((y - 2031 - dl) / 10, 0, 1) * p['adoption_target'] if en else 0.
    ep = sum(x['episodes_reference'] for x in IN['clinical_strata']) * scale
    rec = ep * adopt; ref = rec * p.get('reference_target', .85) * regph
    conf = ref * p['confirmed_share'] * p.get('latest_wish_confirmation', .95)
    prox = p.get('proxy_designation_target', .5) * regph
    pub = ep * p.get('single_share', .3) * p.get('public_proxy_coverage', .6) * regph
    fb = ep * (1 - adopt) * (1 - prox) * p.get('multidisciplinary_coverage', .7) * regph
    sp = conf * p['support_completion']; will = sp * p['explicit_preference_share'] * p['clinical_appropriateness']
    cap = p['transition_capacity'] * sup * scale; ch = min(will * impl, cap)
    dsh = p['destination_shares']; bsh = p['baseline_setting_shares']
    bu = sum(bsh[k] * p['baseline_cost_yen'][k] for k in bsh); du = sum(dsh[k] * p['destination_cost_yen'][k] for k in dsh)
    care = ch * (du - bu) * idx / 1e12; pall = ch * p['palliative_additional_yen'] * idx / 1e12
    regpop = IN['registry_population_reference'] * scale
    registry = (regpop * max(0, adopt - prev) * p['initial_record_cost_yen'] + regpop * adopt * p['record_maintenance_yen']) * idx / 1e12
    dsup = sp * p['decision_support_yen'] * idx / 1e12
    infra = p['annual_infrastructure_trn'] * sup * idx
    proxy_cost = (pub * p.get('public_proxy_unit_yen', 20000) + fb * p.get('team_unit_yen', 10000)) * idx / 1e12
    subsidy = pub * p.get('low_income_share', .3) * p.get('proxy_subsidy_yen', 10000) * idx / 1e12
    infra += proxy_cost + subsidy
    clin = care + pall; prog = registry + dsup + infra
    pay = {k: clin * v for k, v in fin.items()}
    home = ch * dsh['HOME']; fh = home * p['extra_home_care_hours']
    ni = p.get('noninsured_yen', {'HOSPITAL': 200000, 'HOME': 250000, 'FACILITY': 400000}); lt = p.get('ltc_copay_yen', {'HOSPITAL': 10000, 'HOME': 80000, 'FACILITY': 100000})
    nonmed = ch * sum((dsh[k] - bsh[k]) * ni[k] for k in dsh) * idx / 1e12
    ltc = ch * sum((dsh[k] - bsh[k]) * lt[k] for k in dsh) * idx / 1e12
    hours = fh * p.get('family_hours_multiplier', 1.)
    opp = hours * p.get('hour_value_yen', 2000) * idx / 1e12; loss = opp * p.get('income_loss_share', .4)
    proxy_hh = pub * p.get('proxy_household_fee_yen', 10000) * idx / 1e12 - subsidy
    guar = pub * p.get('guarantee_avoided_yen', 30000) * idx / 1e12
    extra = nonmed + ltc + proxy_hh - guar + loss; cash = pay['HOUSEHOLD'] + extra
    return dict(registered_persons=regpop * adopt, clinical_demand_episodes=ep, chosen_transitions=ch, transition_capacity=cap, confirmed_wishes_episodes=conf, supported_decision_episodes=sp,
                explicit_supported_appropriate_requests=will, care_path_cost_delta_trn=care, palliative_additional_cost_trn=pall, clinical_cost_delta_trn=clin, registry_cost_trn=registry,
                decision_support_cost_trn=dsup, infrastructure_cost_trn=infra, common_program_cost_trn=prog, total_resource_cost_delta_trn=clin + prog,
                patient_payment_delta_trn=pay['HOUSEHOLD'], public_clinical_payment_delta_trn=pay['GOVERNMENT'], insurer_clinical_payment_delta_trn=pay['INSURER'],
                noninsured_household_delta_trn=nonmed, ltc_copay_delta_trn=ltc, proxy_household_net_delta_trn=proxy_hh, guarantee_cost_avoided_trn=guar, family_care_hours=hours,
                family_opportunity_cost_trn=opp, family_income_loss_trn=loss, extra_household_cash_burden_trn=extra, household_direct_cash_burden_delta_trn=cash,
                household_total_economic_burden_delta_trn=pay['HOUSEHOLD'] + nonmed + ltc + proxy_hh - guar + opp, savings_drawdown_delta_trn=cash * (1 - p.get('borrowing_share', .2)),
                borrowing_need_delta_trn=cash * p.get('borrowing_share', .2), public_proxy_program_trn=proxy_cost, proxy_subsidy_trn=subsidy,
                home_transitions=home, additional_unpaid_home_care_hours=fh, capacity_unmet=max(0, will - ch))
# ---------------- F medical ----------------
def claim(age, grp, prof, regime, uniform=False, capm=1.):
    eld = age in ('AGE70_74', 'AGE75PLUS'); bill = prof['bill_yen']; months = prof['months']; old = regime == 'PRE2026AUG'
    co = .2 if age == 'PRESCHOOL' else .3
    if eld: co = (.2 if age == 'AGE70_74' else .1) if grp in ('TAXFREE', 'GENERAL') else .3
    if uniform: co = .3
    inf = math.inf
    if grp == 'TAXFREE': cap = (24600 if old else 25700) if eld else (35400 if old else 36900); multi = 24600; ann = inf if old else 290000
    elif grp == 'GENERAL': cap = 57600 if old else 61500; multi = 34500 if regime == 'POST2027AUG' else 44400; ann = inf if old else 410000
    elif grp == 'MIDDLE': cap = (80100 + max(0, bill - 267000) * .01) if old else (85800 + max(0, bill - 286000) * .01); multi = 44400; ann = inf if old else 530000
    else: cap = (167400 + max(0, bill - 558000) * .01) if old else (179100 + max(0, bill - 597000) * .01); multi = 93000; ann = inf if old else 1110000
    cap *= capm; multi *= capm; ann *= capm
    tot = 0.
    for i in range(months): tot += min(bill * co, cap if i < 3 else multi)
    return min(tot, ann)
def annual_claim(y, *a, **k):
    rg = [('PRE2026AUG', 7 / 12), ('POST2026AUG', 5 / 12)] if y == 2026 else [('POST2026AUG', 7 / 12), ('POST2027AUG', 5 / 12)] if y == 2027 else [('POST2027AUG', 1.)]
    return sum(w * claim(*a, r, **k) for r, w in rg)
def medical(s, y, state):
    T = 1e12; i = y - 2026; idx = DEF[i] / DEF[0]; scale = POP[i] / POP[0]
    ph = clamp((y - s['start_year'] + 1) / s['ramp_years'], 0, 1)
    total = IN['observations']['medical_total_2024_trn'] * idx * scale
    aw = IN['age_cost_weights']; wsum = sum(aw.values())
    refc = sum(p['probability'] * p['bill_yen'] * p['months'] for p in IN['claim_profiles'])
    gross = o0 = o1 = unmet = 0.
    for age, w in aw.items():
        for grp, iw in IN['income_weights'].items():
            persons = total * w / wsum * iw * T / (refc * idx)
            for pr in IN['claim_profiles']:
                p = dict(pr, bill_yen=pr['bill_yen'] * idx); n = persons * p['probability']; bb = n * p['bill_yen'] * p['months'] / T
                a = n * annual_claim(y, age, grp, p) / T
                mult = 1. + (-1 if s['cap_mode'] == 'PATIENT_CAP_DOWN' else 1) * s['cap_change'] * ph if s['copay'] else 1.
                b0 = n * annual_claim(y, age, grp, p, uniform=s['copay'] and s['uniform_thirty'], capm=mult) / T
                b = a + (b0 - a) * ph
                q = clamp((max(b, 1e-12) / max(a, 1e-12)) ** (-s['demand_elasticity']), .7, 1.2) if s['copay'] else 1.
                bill = bb * q; gross += bill; o0 += a; o1 += b * q; unmet += max(0, bb - bill) * s['necessary_care_share']
    vol = gross - total; oopd = o1 - o0
    if abs(vol) < 1e-10: vol = 0.
    if abs(oopd) < 1e-10: oopd = 0.
    ben = vol - oopd
    pp = ph * s['provider_capacity'] if s['provider'] else 0.
    mat = clamp((y - s['start_year'] - s['health_lag'] + 1) / s['ramp_years'], 0, 1) if s['provider'] else 0.
    disc = s['prevention_discovery_trn'] * pp * idx; sav = s['prevention_saving_trn'] * mat * idx; pc = disc - sav
    pf = o0 / max(total, 1e-9); xp = pc * pf; xb = pc - xp
    cp = dict(IN['common_parameters']); cp.update(s['common_overrides']); cp['enabled'] = s['common']
    cm = common(y, idx, scale, cp, IN['common_financing'])
    clin = vol + pc + cm['clinical_cost_delta_trn']; pat = oopd + xp + cm['patient_payment_delta_trn']
    pub = (ben + xb) * s['clinical_public_fraction'] + cm['public_clinical_payment_delta_trn']
    ins = (ben + xb) * (1 - s['clinical_public_fraction']) + cm['insurer_clinical_payment_delta_trn']
    prem = ins * s['premium_pass']; bf = ins * s['government_insurer_backfill_share']
    award = (s['eligible_preventive_fee_trn'] * s['preventive_award'] + s['eligible_equipment_fee_trn'] * s['equipment_award']) * pp * idx
    prv = s['preventive_spend_trn'] * pp * idx; eq = s['equipment_spend_trn'] * pp * idx
    hubs = s['hub_target'] * ph if s['provider'] else 0.; new = max(0, hubs - state['hubs']); state['hubs'] = hubs
    hcap = new * s['hub_capital_yen'] * idx / T; hop = hubs * s['hub_operation_yen'] * idx / T
    tr = s['transition_support_trn'] * idx if s['provider'] and 2028 <= y <= 2030 else 0.
    ps = s['palliative_provider_support_trn'] * idx if s['provider'] and 2028 <= y < 2033 else 0.
    grants = award + prv + eq + hcap + hop + tr + ps
    gov = pub + grants + cm['common_program_cost_trn'] + bf; insb = -ins + prem + bf
    hh = -pat - prem - cm['extra_household_cash_burden_trn']
    sup = cm['common_program_cost_trn'] - cm['proxy_subsidy_trn']
    service = clin + (prv + hop + tr + ps + sup); capex = eq + hcap
    healthy = s['health_worker_equivalent'] * mat; harmed = unmet * s['harm_worker_equivalent_per_trn']
    return dict(baseline_medical_bill_trn=total, baseline_patient_model_trn=o0, reform_medical_bill_before_common_trn=gross, demand_volume_cost_delta_trn=vol, necessary_care_foregone_cost_proxy_trn=unmet,
                prevention_clinical_delta_trn=pc, clinical_cost_delta_trn=clin, patient_payment_delta_trn=pat, public_clinical_payment_delta_trn=pub, insurer_clinical_payment_delta_trn=ins,
                premium_payment_delta_trn=prem, household_cash_delta_trn=hh, government_cost_delta_trn=gov, insurer_balance_delta_trn=insb, provider_grants_total_trn=grants,
                service_production_nominal_delta_trn=service * s['domestic_service_share'], investment_nominal_delta_trn=capex * s['domestic_capital_share'], health_effective_labor_added=healthy - harmed,
                hub_count=hubs, hub_capital_cost_trn=hcap, hub_operation_cost_trn=hop, medical_unassigned_direct_cash_requirement_trn=gov - insb), cm
def main():
    cs = cases(); keep = {k for k, v in cs.items() if v.get('keep_legacy')}
    MA = {(r['case'], int(r['year'])): r for r in rd('Medical_Accounts.csv')}; CE = {(r['case'], int(r['year'])): r for r in rd('Common_EndOfLife.csv')}
    n = bad = 0; mx = 0.; badl = []
    for cid, s in cs.items():
        if cid in keep: continue
        st = {'hubs': 0.}
        for y in range(2026, 2056):
            m, c = medical(s, y, st)
            for src, ref in ((m, MA), (c, CE)):
                row = ref[(cid, y)]
                for k, v in src.items():
                    o = row.get(k)
                    if o in (None, ''): continue
                    o = float(o); e = abs(v - o) / max(1., abs(o)) if abs(o) > 1e-3 else abs(v - o); n += 1
                    if e > 1e-8:
                        bad += 1; badl.append((cid, y, k, v, o))
                    mx = max(mx, e)
    print('A medical+common recompute: cells', n, 'mismatch', bad, 'max err (rel for |x|>1e-3 else abs) %.3e' % mx, badl[:3])
    # household table of the Report (COMMON_ONLY)
    ce = {y: CE[('COMMON_ONLY', y)] for y in (2035, 2040, 2055)}
    keys = ['patient_payment_delta_trn', 'noninsured_household_delta_trn', 'ltc_copay_delta_trn', 'proxy_household_net_delta_trn', 'guarantee_cost_avoided_trn', 'family_income_loss_trn', 'household_direct_cash_burden_delta_trn', 'household_total_economic_burden_delta_trn']
    st = {'hubs': 0.}
    print('B COMMON_ONLY household (independent, 兆円 / 億円):')
    for y in (2035, 2040, 2055):
        idx = DEF[y - 2026] / DEF[0]; sc = POP[y - 2026] / POP[0]; p = dict(IN['common_parameters']); p['enabled'] = True
        c = common(y, idx, sc, p, IN['common_financing'])
        print(' ', y, ' '.join('%s=%.6f(%.2f億)' % (k.split('_trn')[0][:22], c[k], c[k] * 1e4) for k in keys))
        o = [float(ce[y][k]) for k in keys]
        assert all(abs(a - b) < 1e-9 for a, b in zip(o, [c[k] for k in keys])), 'report/csv mismatch'
        pay = c['patient_payment_delta_trn']; opp = c['family_opportunity_cost_trn']; loss = c['family_income_loss_trn']
        print('    identities: cash = patient + extra:', abs(c['household_direct_cash_burden_delta_trn'] - pay - c['extra_household_cash_burden_trn']) < 1e-15, '| total - cash = (1-0.4)*opportunity:', abs((c['household_total_economic_burden_delta_trn'] - c['household_direct_cash_burden_delta_trn']) - (opp - loss)) < 1e-15, '(opp-loss = %.6f, 60%% of opportunity)' % (opp - loss))
        print('    cash components: patient %.6f + nonins %.6f + ltc %.6f + proxy %.6f - guarantee %.6f + income loss %.6f = %.6f' % (pay, c['noninsured_household_delta_trn'], c['ltc_copay_delta_trn'], c['proxy_household_net_delta_trn'], c['guarantee_cost_avoided_trn'], loss, c['household_direct_cash_burden_delta_trn']))
    # sensitivity of the 2040 sign of the direct-cash difference
    y = 2040; idx = DEF[y - 2026] / DEF[0]; sc = POP[y - 2026] / POP[0]
    print('C 2040 direct cash difference (億円) under single changes:')
    base = dict(IN['common_parameters']); base['enabled'] = True
    def cash(**ov):
        p = dict(base); p.update(ov); return common(y, idx, sc, p, IN['common_financing'])['household_direct_cash_burden_delta_trn'] * 1e4
    print('   base %.3f | income_loss_share 0 %.3f | 0.6 %.3f | guarantee 0 %.3f | guarantee 60k %.3f | proxy fee 0 %.3f | noninsured home 400k %.3f | hour_value 3000 %.3f | pub proxy coverage 0.3 %.3f' % (
        cash(), cash(income_loss_share=0.), cash(income_loss_share=.6), cash(guarantee_avoided_yen=0), cash(guarantee_avoided_yen=60000), cash(proxy_household_fee_yen=0),
        cash(noninsured_yen={'HOSPITAL': 200000, 'HOME': 400000, 'FACILITY': 400000}), cash(hour_value_yen=3000), cash(public_proxy_coverage=.3)))
main()
