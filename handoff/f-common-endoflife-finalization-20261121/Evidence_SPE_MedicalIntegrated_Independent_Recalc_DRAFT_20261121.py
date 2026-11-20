#!/usr/bin/env python3
# Claude independent recalculation of the corrected medical / common end-of-life module inside the F integrated run
# (Commit 6986bb7d...; handoff/f-medical-corrected-integrated-20261121).  Shares only data with the original:
# Inputs.json, per-case population trajectory (Labor.csv), per-case age populations (Demography_Demand.csv, used as data after
# closure checks) and the price index from f-integrated Annual.csv.  Formulas were rewritten from the code semantics.
# Usage: python3 -I <this> <repo_root_at_6986bb7>
import sys, os, csv, json, math
R = sys.argv[1]; D = os.path.join(R, 'handoff/f-medical-corrected-integrated-20261121')
IN = json.load(open(os.path.join(D, 'Inputs.json')))
def rd(n, d=D): return list(csv.DictReader(open(os.path.join(d, n))))
INTEG = sorted([r for r in rd('Annual.csv', os.path.join(R, 'handoff/f-integrated-20261121')) if r['case'] == 'FULL_ADDITIONAL'], key=lambda r: int(r['year']))
DEF = [float(r['common_deflator']) for r in INTEG]
LAB = {(r['case'], int(r['year'])): r for r in rd('Labor.csv')}
DEM = {}
for r in rd('Demography_Demand.csv'): DEM.setdefault((r['case'], int(r['year'])), {})[r['age']] = r
clamp = lambda x, lo, hi: max(lo, min(hi, x))
AGES = ['U15', 'A15_64', '65_69', '70_74', '75plus']
DP = IN['demand_parameters']; OBS = IN['observations']; CP0 = IN['common_parameters']; FIN0 = IN['common_financing']
# ---- statutory-style patient payment (same rules as the earlier verified version of the module)
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
    return min(sum(min(bill * co, cap if i < 3 else multi) for i in range(months)), ann)
def aclaim(y, *a, **k):
    rg = [('PRE2026AUG', 7 / 12), ('POST2026AUG', 5 / 12)] if y == 2026 else [('POST2026AUG', 7 / 12), ('POST2027AUG', 5 / 12)] if y == 2027 else [('POST2027AUG', 1.)]
    return sum(w * claim(*a, r, **k) for r, w in rg)
# ---- age demand (nationality split and episodes), compared with Demography_Demand.csv
def age_demand(case, y):
    t = LAB[(case, y)]; b = LAB[(case, 2026)]; pop = {k: float(DEM[(case, y)][k]['population']) for k in AGES}; base = {k: float(DEM[(case, 2026)][k]['population']) for k in AGES}
    q = IN['population_reference'][str(y)]
    assert abs(sum(pop.values()) - float(t['population'])) < 1e-3 and abs(sum(pop[k] for k in ('65_69', '70_74', '75plus')) - float(t['elderly'])) < 1e-3
    raw = {'U15': q['japanese_under15'], 'A15_64': q['japanese_working_age']}
    for k in ('65_69', '70_74', '75plus'): raw[k] = q['japanese_elderly'] * pop[k] / float(t['elderly'])
    f = float(t['japanese']) / sum(raw.values()); jap = {k: v * f for k, v in raw.items()}
    rates = DP['episode_rates']; norm = DP['episodes_2026_anchor'] / sum(base[k] * rates[k] for k in AGES)
    ep = {k: pop[k] * rates[k] * norm for k in AGES}
    return pop, base, jap, ep, rates, norm
def cage(a, share): return {'PRESCHOOL': a['U15'] * share, 'AGE6_69': a['U15'] * (1 - share) + a['A15_64'] + a['65_69'], 'AGE70_74': a['70_74'], 'AGE75PLUS': a['75plus']}
def costs(pop, base, mode, tpop, tbase):
    sh = DP['under15_preschool_share']; bp, ap = cage(base, sh), cage(pop, sh)
    return {k: v * (ap[k] / bp[k] if mode == 'AGE' else tpop / tbase) for k, v in DP['cost_weights_2024'].items()}
# ---- common end of life with the caller-provided payer rules
def common(y, idx, scale, p, fin, episodes, ep_age, payer):
    en = p['enabled']; dl = p.get('timeline_delay', 0)
    rp = lambda st, n: clamp((y - st - dl + 1) / n, 0, 1) if en else 0.
    impl = rp(2032, 4); sup = rp(2027, 14) * p.get('supply_capacity_factor', 1.); regph = rp(2031, 10)
    adopt = regph * p['adoption_target'] * (1 - p.get('withdrawn_share', 0.))
    prev = clamp((y - 2031 - dl) / 10, 0, 1) * p['adoption_target'] if en else 0.
    regpop = IN['registry_population_reference'] * scale
    rec = episodes * adopt; ref = rec * p.get('reference_target', .85) * regph
    conf = ref * p['confirmed_share'] * p.get('latest_wish_confirmation', .95); prox = p.get('proxy_designation_target', .5) * regph
    pub = episodes * p.get('single_share', .3) * p.get('public_proxy_coverage', .6) * regph
    fb = episodes * (1 - adopt) * (1 - prox) * p.get('multidisciplinary_coverage', .7) * regph
    sp = conf * p['support_completion']; will = sp * p['explicit_preference_share'] * p['clinical_appropriateness']
    cap = p['transition_capacity'] * sup * scale; ch = min(will * impl, cap)
    dsh = p['destination_shares']; bsh = p['baseline_setting_shares']
    bu = sum(bsh[k] * p['baseline_cost_yen'][k] for k in bsh); du = sum(dsh[k] * p['destination_cost_yen'][k] for k in dsh)
    care = ch * (du - bu) * idx / 1e12; pall = ch * p['palliative_additional_yen'] * idx / 1e12
    registry = (regpop * max(0, adopt - prev) * p['initial_record_cost_yen'] + regpop * adopt * p['record_maintenance_yen']) * idx / 1e12
    dsup = sp * p['decision_support_yen'] * idx / 1e12
    proxy_cost = (pub * p.get('public_proxy_unit_yen', 20000) + fb * p.get('team_unit_yen', 10000)) * idx / 1e12
    subsidy = pub * p.get('low_income_share', .3) * p.get('proxy_subsidy_yen', 10000) * idx / 1e12
    infra = p['annual_infrastructure_trn'] * sup * idx + proxy_cost + subsidy; prog = registry + dsup + infra
    clin = care + pall
    pay = payer(ch, p, bu, du, idx, False, 0.) if payer else {k: clin * v for k, v in fin.items()}
    un_need = episodes * p.get('universal_need_share', .7) if en and p.get('universal_palliative', False) else 0.
    un_served = min(un_need, cap) * impl; un_cost = un_served * p.get('universal_palliative_unit_yen', 100000) * idx / 1e12
    un_pay = {k: un_cost * v for k, v in fin.items()}
    if payer and un_served: un_pay = payer(un_served, p, 0., p.get('universal_palliative_unit_yen', 100000), idx, True, ch)
    clin += un_cost; pay = {k: pay[k] + un_pay[k] for k in pay}
    home = ch * dsh['HOME']; fh = home * p['extra_home_care_hours']
    ni = p.get('noninsured_yen', {'HOSPITAL': 200000, 'HOME': 250000, 'FACILITY': 400000}); lt = p.get('ltc_copay_yen', {'HOSPITAL': 10000, 'HOME': 80000, 'FACILITY': 100000})
    nonmed = ch * sum((dsh[k] - bsh[k]) * ni[k] for k in dsh) * idx / 1e12; ltc = ch * sum((dsh[k] - bsh[k]) * lt[k] for k in dsh) * idx / 1e12
    hours = fh * p.get('family_hours_multiplier', 1.); opp = hours * p.get('hour_value_yen', 2000) * idx / 1e12; loss = opp * p.get('income_loss_share', .4)
    proxy_hh = pub * p.get('proxy_household_fee_yen', 10000) * idx / 1e12 - subsidy; guar = pub * p.get('guarantee_avoided_yen', 30000) * idx / 1e12
    extra = nonmed + ltc + proxy_hh - guar + loss; cash = pay['HOUSEHOLD'] + extra
    return dict(clinical_demand_episodes=episodes, chosen_transitions=ch, transition_capacity=cap, confirmed_wishes_episodes=conf, supported_decision_episodes=sp, explicit_supported_appropriate_requests=will,
                universal_palliative_need=un_need, universal_palliative_served=un_served, universal_palliative_cost_trn=un_cost, universal_palliative_patient_trn=un_pay['HOUSEHOLD'],
                universal_palliative_public_trn=un_pay['GOVERNMENT'], universal_palliative_insurer_trn=un_pay['INSURER'], care_path_cost_delta_trn=care, palliative_additional_cost_trn=pall,
                clinical_cost_delta_trn=clin, registry_cost_trn=registry, decision_support_cost_trn=dsup, infrastructure_cost_trn=infra, common_program_cost_trn=prog, total_resource_cost_delta_trn=clin + prog,
                patient_payment_delta_trn=pay['HOUSEHOLD'], public_clinical_payment_delta_trn=pay['GOVERNMENT'], insurer_clinical_payment_delta_trn=pay['INSURER'], noninsured_household_delta_trn=nonmed,
                ltc_copay_delta_trn=ltc, proxy_household_net_delta_trn=proxy_hh, guarantee_cost_avoided_trn=guar, family_care_hours=hours, family_opportunity_cost_trn=opp, family_income_loss_trn=loss,
                extra_household_cash_burden_trn=extra, household_direct_cash_burden_delta_trn=cash, household_total_economic_burden_delta_trn=pay['HOUSEHOLD'] + nonmed + ltc + proxy_hh - guar + opp,
                savings_drawdown_delta_trn=cash * (1 - p.get('borrowing_share', .2)), borrowing_need_delta_trn=cash * p.get('borrowing_share', .2), public_proxy_program_trn=proxy_cost, proxy_subsidy_trn=subsidy,
                registered_persons=regpop * adopt, home_transitions=home, additional_unpaid_home_care_hours=fh, capacity_unmet=max(0, will - ch)), (pay,)
def main():
    cases = {}
    for c in IN['cases']: s = dict(IN['defaults']); s.update(c); cases[c['id']] = s
    MA = {(r['case'], int(r['year'])): r for r in rd('Medical_Accounts.csv')}; CE = {(r['case'], int(r['year'])): r for r in rd('Common_EndOfLife.csv')}; DD = DEM
    n = bad = 0; mx = 0.; badl = []
    def cmp(src, row, tag):
        nonlocal n, bad, mx
        for k, v in src.items():
            o = row.get(k)
            if o in (None, ''): continue
            o = float(o); e = abs(v - o) / max(1., abs(o)) if abs(o) > 1e-3 else abs(v - o); n += 1; mx = max(mx, e)
            if e > 1e-8: bad += 1; badl.append((tag, k, v, o))
    for cid, s in cases.items():
        if s.get('keep_legacy'): continue
        debt = 0.; asset = 0.; prevhubs = 0.
        for y in range(2026, 2056):
            i = y - 2026; idx = DEF[i] / DEF[0]; scale = float(LAB[(cid, y)]['population']) / float(LAB[(cid, 2026)]['population']); ph = clamp((y - s['start_year'] + 1) / s['ramp_years'], 0, 1)
            pop, base, jap, ep, rates, norm = age_demand(cid, y)
            tot_ep = sum(ep.values()) if s['demand_mode'] == 'AGE' else DP['episodes_2026_anchor'] * float(LAB[(cid, y)]['population']) / float(LAB[(cid, 2026)]['population'])
            if s['demand_mode'] != 'AGE': ep = {k: v / sum(ep.values()) * tot_ep for k, v in ep.items()}
            # demography rows
            for k in AGES:
                row = DEM[(cid, y)][k]; cmp(dict(japanese=jap[k], foreign=pop[k] - jap[k], terminal_episode_rate_candidate=rates[k] * norm, terminal_episodes=ep[k]), row, (cid, y, k))
            aw = costs(pop, base, s['demand_mode'], float(LAB[(cid, y)]['population']), float(LAB[(cid, 2026)]['population']))
            ratio = sum(aw.values()) / sum(IN['age_cost_weights'].values()); total = OBS['medical_total_2024_trn'] * idx * ratio
            gross = o0 = o1 = unmet = static = 0.; wsum = sum(aw.values()); refc = sum(p['probability'] * p['bill_yen'] * p['months'] for p in IN['claim_profiles'])
            for age, w in aw.items():
                for grp, iw in IN['income_weights'].items():
                    persons = total * w / wsum * iw * 1e12 / (refc * idx)
                    for pr in IN['claim_profiles']:
                        p = dict(pr, bill_yen=pr['bill_yen'] * idx); nn = persons * p['probability']; bb = nn * p['bill_yen'] * p['months'] / 1e12
                        a = nn * aclaim(y, age, grp, p) / 1e12
                        mult = 1. + (-1 if s['cap_mode'] == 'PATIENT_CAP_DOWN' else 1) * s['cap_change'] * ph if s['copay'] else 1.
                        b0 = nn * aclaim(y, age, grp, p, uniform=s['copay'] and s['uniform_thirty'], capm=mult) / 1e12; b = a + (b0 - a) * ph
                        q = clamp((max(b, 1e-12) / max(a, 1e-12)) ** (-s['demand_elasticity']), .7, 1.2) if s['copay'] else 1.
                        gross += bb * q; o0 += a; o1 += b * q; static += b - a; unmet += max(0, bb - bb * q) * s['necessary_care_share']
            vol = gross - total; oopd = o1 - o0
            if abs(vol) < 1e-10: vol = 0.
            if abs(oopd) < 1e-10: oopd = 0.
            ben = vol - oopd
            pp = ph * s['provider_capacity'] if s['provider'] else 0.
            mat = clamp((y - s['start_year'] - s['health_lag'] + 1) / s['ramp_years'], 0, 1) if s['provider'] else 0.
            disc = s['prevention_discovery_trn'] * pp * idx; sav = s['prevention_saving_trn'] * mat * idx; pc = disc - sav
            pf = o0 / max(total, 1e-9); xp = pc * pf; xb = pc - xp
            cp = dict(CP0); cp.update(s['common_overrides']); cp['enabled'] = s['common']
            if s['universal_palliative']: cp.update(universal_palliative=True, palliative_additional_yen=0.)
            payer = None
            if s['payer_mode'] == 'CLAIMS':
                def payer(chosen, p, baseline, destination, price, universal=False, transitioned=0., _s=s, _y=y, _ph=ph, _ep=ep, _tot=tot_ep):
                    def oop(age, grp, cost):
                        prof = dict(months=_s['episode_months'], bill_yen=cost * price / _s['episode_months']); a0 = aclaim(_y, age, grp, prof)
                        if not _s['copay']: return a0
                        m = 1. + (-1 if _s['cap_mode'] == 'PATIENT_CAP_DOWN' else 1) * _s['cap_change'] * _ph
                        return a0 + (aclaim(_y, age, grp, prof, uniform=_s['uniform_thirty'], capm=m) - a0) * _ph
                    amap = {'U15': 'PRESCHOOL', 'A15_64': 'AGE6_69', '65_69': 'AGE6_69', '70_74': 'AGE70_74', '75plus': 'AGE75PLUS'}
                    pat = gr = 0.
                    for ag, cnt in _ep.items():
                        for grp, wt in IN['income_weights'].items():
                            if universal:
                                ngross = destination; old = 0.; tshare = min(1., transitioned / max(chosen, 1e-9))
                                bm = sum(p['baseline_setting_shares'][k] * (oop(amap[ag], grp, p['baseline_cost_yen'][k] + destination) - oop(amap[ag], grp, p['baseline_cost_yen'][k])) for k in p['baseline_setting_shares'])
                                dm = sum(p['destination_shares'][k] * (oop(amap[ag], grp, p['destination_cost_yen'][k] + destination) - oop(amap[ag], grp, p['destination_cost_yen'][k])) for k in p['destination_shares'])
                                new = (1 - tshare) * bm + tshare * dm; bgross = 0.
                            else:
                                bgross = sum(p['baseline_setting_shares'][k] * p['baseline_cost_yen'][k] for k in p['baseline_setting_shares'])
                                ngross = sum(p['destination_shares'][k] * (p['destination_cost_yen'][k] + p['palliative_additional_yen']) for k in p['destination_shares'])
                                old = sum(p['baseline_setting_shares'][k] * oop(amap[ag], grp, p['baseline_cost_yen'][k]) for k in p['baseline_setting_shares'])
                                new = sum(p['destination_shares'][k] * oop(amap[ag], grp, p['destination_cost_yen'][k] + p['palliative_additional_yen']) for k in p['destination_shares'])
                            wgt = cnt / _tot * wt; pat += chosen * wgt * (new - old) / 1e12; gr += chosen * wgt * (ngross - bgross) * price / 1e12
                    benefit = gr - pat
                    return dict(HOUSEHOLD=pat, GOVERNMENT=benefit * _s['clinical_public_fraction'], INSURER=benefit * (1 - _s['clinical_public_fraction']))
            cm, _ = common(y, idx, scale, cp, FIN0, tot_ep, ep, payer)
            cmp(cm, CE[(cid, y)], (cid, y, 'common'))
            clin = vol + pc + cm['clinical_cost_delta_trn']; pat = oopd + xp + cm['patient_payment_delta_trn']
            pub = (ben + xb) * s['clinical_public_fraction'] + cm['public_clinical_payment_delta_trn']; ins = (ben + xb) * (1 - s['clinical_public_fraction']) + cm['insurer_clinical_payment_delta_trn']
            prem = ins * s['premium_pass']; bf = ins * s['government_insurer_backfill_share']
            award = (s['eligible_preventive_fee_trn'] * s['preventive_award'] + s['eligible_equipment_fee_trn'] * s['equipment_award']) * pp * idx
            prv = s['preventive_spend_trn'] * pp * idx; eq = s['equipment_spend_trn'] * pp * idx
            hubs = s['hub_target'] * ph if s['provider'] else 0.; new = max(0, hubs - prevhubs); prevhubs = hubs
            hcap = new * s['hub_capital_yen'] * idx / 1e12; hop = hubs * s['hub_operation_yen'] * idx / 1e12
            tr = s['transition_support_trn'] * idx if s['provider'] and 2028 <= y <= 2030 else 0.; ps = s['palliative_provider_support_trn'] * idx if s['provider'] and 2028 <= y < 2033 else 0.
            grants = award + prv + eq + hcap + hop + tr + ps; prog = cm['common_program_cost_trn']
            gov = pub + grants + prog + bf; insb = -ins + prem + bf; hh = -pat - prem - cm['extra_household_cash_burden_trn']
            supsrc = prog - cm['proxy_subsidy_trn']; service = clin + (prv + hop + tr + ps + supsrc); capex = eq + hcap
            healthy = s['health_worker_equivalent'] * mat; harmed = unmet * s['harm_worker_equivalent_per_trn']
            # financing and value-added connection
            mix = s['finance_mix']; interest = debt * s['medical_debt_rate']; need = gov - insb + interest; ff = s['finance_fraction']
            tax = need * ff * mix['TAX']; fprem = need * ff * mix['PREMIUM']; crowd = need * ff * mix['OTHER_SPENDING']; dflow = need * ff * mix['DEBT']
            issue = max(0., dflow); redeem = min(debt, max(0., -dflow)); addasset = max(0., -dflow - redeem); debt += issue - redeem; asset += addasset
            dom = 1 - s['medical_import_share']; va = (1 - s['medical_intermediate_share']) * s['medical_VA_scale']; rep = 1 - s['medical_displacement_share']
            newsvc = service * dom * va * rep - crowd * s['other_spending_VA_ratio']
            inv = capex * dom * s['capital_VA_ratio'] * s['medical_VA_scale'] * rep
            if s['legacy_GDP']: newsvc = service * s['domestic_service_share']; inv = capex * s['domestic_capital_share']
            m = dict(baseline_medical_bill_trn=total, baseline_patient_model_trn=o0, reform_medical_bill_before_common_trn=gross, patient_static_transfer_trn=static, demand_volume_cost_delta_trn=vol, necessary_care_foregone_cost_proxy_trn=unmet,
                     prevention_clinical_delta_trn=pc, clinical_cost_delta_trn=clin, patient_payment_delta_trn=pat, public_clinical_payment_delta_trn=pub, insurer_clinical_payment_delta_trn=ins, premium_payment_delta_trn=prem,
                     household_cash_delta_trn=hh - tax - fprem, government_cost_delta_trn=gov + interest - crowd, insurer_balance_delta_trn=insb + fprem, provider_grants_total_trn=grants, hub_count=hubs, hub_capital_cost_trn=hcap,
                     service_production_nominal_delta_trn=newsvc, investment_nominal_delta_trn=inv, health_effective_labor_added=healthy - harmed, health_effective_gain=healthy, necessary_care_labor_loss=harmed,
                     gross_medical_service_delta_trn=service, medical_financing_need_before_sources_trn=need, medical_financing_tax_trn=tax, medical_financing_premium_trn=fprem, medical_other_spending_crowded_trn=crowd,
                     medical_policy_debt_issue_trn=issue, medical_policy_debt_stock_trn=debt, medical_policy_debt_redemption_trn=redeem, medical_policy_asset_addition_trn=addasset, medical_policy_financial_asset_stock_trn=asset,
                     medical_policy_interest_trn=interest, medical_unassigned_after_sources_trn=need * (1 - ff), medical_VAT_scope_flow_delta_trn=clin + prv + hop + ps,
                     partial_public_direct_balance_delta_trn=-(gov + interest - crowd) + insb + fprem + tax, medical_unassigned_direct_cash_requirement_trn=gov - insb)
            cmp(m, MA[(cid, y)], (cid, y, 'medical'))
    print('A corrected medical+common+demand recompute: cells', n, 'mismatch', bad, 'max err (rel for |x|>1e-3 else abs) %.3e' % mx, badl[:3])
main()
