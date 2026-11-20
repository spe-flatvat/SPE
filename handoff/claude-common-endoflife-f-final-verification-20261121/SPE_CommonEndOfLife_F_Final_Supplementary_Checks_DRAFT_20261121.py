#!/usr/bin/env python3
# Claude supplementary checks on ff6210061615105de9a0d64767c256796be80ed2 (handoff/f-common-endoflife-finalization-20261121).
# Read-only. Reads CSVs of the fixed folder and of the previous fixed folder (6986bb7); imports the common module only for edge-case calls.
# Usage: python3 <this> <repo_root_with_ff621006_tree> <repo_root_with_6986bb7_tree>
import sys, os, csv, json, math, copy, collections
R, R0 = sys.argv[1], sys.argv[2]
D = os.path.join(R, 'handoff/f-common-endoflife-finalization-20261121'); D0 = os.path.join(R0, 'handoff/f-medical-corrected-integrated-20261121')
sys.path.insert(0, D)
from CommonEndOfLife import calculate            # import of the module under test (edge-case calls)
import CommonInterface
rd = lambda n, d=D: list(csv.DictReader(open(os.path.join(d, n))))
IN = json.load(open(os.path.join(D, 'Inputs.json')))
A = {(r['case'], int(r['year'])): r for r in rd('Annual.csv')}
CE = {(r['case'], int(r['year'])): r for r in rd('Common_EndOfLife.csv')}
CE0 = {(r['case'], int(r['year'])): r for r in rd('Common_EndOfLife.csv', D0)}
A0 = {(r['case'], int(r['year'])): r for r in rd('Annual.csv', D0)}
MA = {(r['case'], int(r['year'])): r for r in rd('Medical_Accounts.csv')}
f = lambda r, k: float(r[k]); Y = range(2026, 2056)
cases = sorted({c for c, _ in CE}); allcases = sorted({c for c, _ in A})
print('B0 counts: Annual rows', len(A), 'cases', len(allcases), '| Common_EndOfLife rows', len(CE), 'cases', len(cases), '| fixed refs', [c for c in allcases if c not in cases])
# ---------------- B: supply / patient-set invariants
tol = 1e-6; viol = collections.Counter(); worst = 0.
for (c, y), r in CE.items():
    cap, used, ch, ov, sv, un, tn, ev = f(r, 'transition_capacity'), f(r, 'resource_units_used'), f(r, 'chosen_transitions'), f(r, 'overlap_patients'), f(r, 'universal_palliative_served'), f(r, 'unique_patients_served'), f(r, 'transition_need'), f(r, 'service_events')
    if used > cap + tol: viol['used>capacity'] += 1
    if ch > ov + tol and sv > 0: viol['chosen>overlap'] += 1
    if ov > sv + tol: viol['overlap>served'] += 1
    if abs(un - (ch + sv - ov)) > tol: viol['unique identity'] += 1
    if abs(ev - (ch + sv)) > tol: viol['service_events identity'] += 1
    if ch > tn + tol: viol['chosen>need'] += 1
    mode = r['capacity_allocation']
    if sv > 0:
        ap = f(r, 'universal_access_probability')
        if tn > 0 and abs(ch / tn - ap) > 1e-9: viol['transition access prob != universal access prob'] += 1
        if mode == 'OVERLAP_EQUAL_ACCESS' and abs(used - sv) > tol: viol['OVERLAP used != served'] += 1
        if mode == 'EXTRA_TRANSITION_RESOURCE' and abs(used - (sv + ch)) > tol: viol['EXTRA used != served+chosen (units=2)'] += 1
    worst = max(worst, used / cap if cap else 0)
print('B1 invariants over', len(CE), 'case-years: violations', dict(viol) or 'none', '| max used/capacity %.6f' % worst)
mm = collections.Counter(r['capacity_allocation'] for r in CE.values()); print('B2 allocation modes (rows):', dict(mm))
binding = sum(1 for (c, y), r in CE.items() if f(r, 'universal_palliative_unmet') > 1 and f(r, 'implementation_phase') >= 1 and f(r, 'resource_units_used') >= .9999 * f(r, 'transition_capacity'))
print('B3 fully-implemented case-years where capacity binds:', binding, 'of', sum(1 for r in CE.values() if f(r, 'implementation_phase') >= 1))
for y in (2035, 2040, 2055):
    n, o = CE[('LATEST_F', y)], CE0[('LATEST_F', y)]
    print('B4 LATEST_F %d new chosen %.0f served %.0f cap %.0f overlap %.0f unique %.0f used %.0f access %.4f | old chosen %.0f served %.0f cap %.0f (old chosen+served %.0f)' % (y, f(n, 'chosen_transitions'), f(n, 'universal_palliative_served'), f(n, 'transition_capacity'), f(n, 'overlap_patients'), f(n, 'unique_patients_served'), f(n, 'resource_units_used'), f(n, 'universal_access_probability'), f(o, 'chosen_transitions'), f(o, 'universal_palliative_served'), f(o, 'transition_capacity'), f(o, 'chosen_transitions') + f(o, 'universal_palliative_served')))
# unmet reporting before implementation
r26 = CE[('LATEST_F', 2026)]; r31 = CE[('LATEST_F', 2031)]
print('B5 unmet reported before implementation: 2026 need %.0f served %.0f unmet %.0f (impl phase %.2f) ; 2031 unmet %.0f' % (f(r26, 'universal_palliative_need'), f(r26, 'universal_palliative_served'), f(r26, 'universal_palliative_unmet'), f(r26, 'implementation_phase'), f(r31, 'universal_palliative_unmet')))
bad = [(c, y) for (c, y), r in CE.items() if f(r, 'capacity_unmet') > f(r, 'transition_unmet') + 1 and c == 'LATEST_F']
print('B6 capacity_unmet (uses willing, not phase-scaled need) exceeds transition_unmet in LATEST_F years:', len(bad), 'e.g.', bad[:1], '; 2035 capacity_unmet %.0f vs transition_unmet %.0f' % (f(CE[('LATEST_F', 2035)], 'capacity_unmet'), f(CE[('LATEST_F', 2035)], 'transition_unmet')))
# ---------------- B edge cases through the module under test, compared with an independent closed form
base_p = {**IN['common_parameters'], 'enabled': True, 'universal_palliative': True, 'palliative_additional_yen': 0.}
fin = dict(HOUSEHOLD=.1, GOVERNMENT=.45, INSURER=.45)
def call(year=2040, ep=450000., over=None, scale=1., capm=1., **kw):
    p = {**base_p, **(over or {})}
    d = dict(price_index=1., population_scale=scale, registry_population=IN['registry_population_reference'], age_demand_episodes=ep, capacity_multiplier=capm, clinical_strata=IN['clinical_strata'])
    return calculate(year, d, p, fin)
def closed(r, p, ep, scale=1., year=2040, capm=1.):
    en = p['enabled']; dl = p.get('timeline_delay', 0); ramp = lambda s, n: max(0, min(1, (year - s - dl + 1) / n)) if en else 0.
    impl = ramp(2032, 4); sup = ramp(2027, 14) * p.get('supply_capacity_factor', 1.); cap = p['transition_capacity'] * sup * scale * capm
    tn = f(r, 'transition_need'); un = ep * p.get('universal_need_share', .7) if en and p.get('universal_palliative') else 0.; tgt = max(un * impl, tn) if un else 0
    k = 1. if p.get('capacity_allocation', 'OVERLAP_EQUAL_ACCESS') == 'OVERLAP_EQUAL_ACCESS' else p.get('transition_resource_units', 2.)
    if not tgt: return min(tn, cap), 0.
    a = min(1., cap / (tgt + (k - 1) * tn)) if tgt + (k - 1) * tn else 0.
    return a * tn, a * tgt
edge = [('baseline', {}, {}), ('capacity 0', dict(capm=0.), {}), ('capacity tiny', dict(capm=1e-6), {}), ('demand 0', dict(ep=0.), {}), ('adoption 0', {}, dict(adoption_target=0.)), ('adoption 1', {}, dict(adoption_target=1.)),
        ('withdrawn all', {}, dict(withdrawn_share=1.)), ('unknown/no explicit preference', {}, dict(explicit_preference_share=0.)), ('confirmed 0', {}, dict(confirmed_share=0.)),
        ('extreme: all want, tiny universal need', {}, dict(adoption_target=1., confirmed_share=1., support_completion=1., explicit_preference_share=1., clinical_appropriateness=1., universal_need_share=.01)),
        ('EXTRA units 2', {}, dict(capacity_allocation='EXTRA_TRANSITION_RESOURCE', transition_resource_units=2.)), ('EXTRA units 5', {}, dict(capacity_allocation='EXTRA_TRANSITION_RESOURCE', transition_resource_units=5.)),
        ('universal off', {}, dict(universal_palliative=False)), ('supply short .15', {}, dict(supply_capacity_factor=.15)), ('disabled', {}, dict(enabled=False)), ('delay 3', {}, dict(timeline_delay=3))]
ok = 0
for name, kw, over in edge:
    for y in (2031, 2032, 2035, 2040, 2055):
        r = call(year=y, over=over, **kw); p = {**base_p, **over}
        ch_i, sv_i = closed(r, p, kw.get('ep', 450000.), 1., y, kw.get('capm', 1.))
        assert math.isclose(f(r, 'chosen_transitions'), ch_i, rel_tol=1e-9, abs_tol=1e-6) and math.isclose(f(r, 'universal_palliative_served'), sv_i, rel_tol=1e-9, abs_tol=1e-6), (name, y)
        assert f(r, 'resource_units_used') <= f(r, 'transition_capacity') + 1e-6 and f(r, 'overlap_patients') <= f(r, 'universal_palliative_served') + 1e-6
        assert r['unknown_wish_assumed_refusal'] == 0 and r['treatment_automatically_stopped'] == 0 and r['active_life_termination'] == 0 and r['registration_changes_palliative_priority'] == 0
        if over.get('explicit_preference_share') == 0. or over.get('confirmed_share') == 0. or over.get('adoption_target') == 0. or over.get('withdrawn_share') == 1.: assert f(r, 'chosen_transitions') == 0.
        ok += 1
print('B7 edge-case calls matching independent closed form and protection flags:', ok, '(%d scenarios x 5 years)' % len(edge))
r = call(year=2040, over=dict(adoption_target=1., confirmed_share=1., support_completion=1., explicit_preference_share=1., clinical_appropriateness=1., universal_need_share=.01))
print('B8 extreme registration: transition_need %.0f universal_need %.0f served %.0f chosen %.0f access %.3f overlap<=served %s' % (f(r, 'transition_need'), f(r, 'universal_palliative_need'), f(r, 'universal_palliative_served'), f(r, 'chosen_transitions'), f(r, 'universal_access_probability'), f(r, 'overlap_patients') <= f(r, 'universal_palliative_served') + 1e-6))
# registration changes affect unregistered access only through the shared target (externality), not through priority
lo = call(2040, over=dict(adoption_target=.1)); hi = call(2040, over=dict(adoption_target=.9))
print('B9 access probability low registration %.4f vs high registration %.4f (equal while target = universal need)' % (f(lo, 'universal_access_probability'), f(hi, 'universal_access_probability')))
# ---------------- C: set independence
src = ''.join(open(os.path.join(D, n)).read() for n in ('CommonEndOfLife.py', 'CommonInterface.py'))
imports = [l.strip() for l in src.splitlines() if l.strip().startswith(('import ', 'from '))]
print('C1 imports in CommonEndOfLife.py + CommonInterface.py:', imports)
print('C2 mentions of F/N3/set names in the two files:', [w for w in ('FMedical', 'N3', 'caller', 'policy_set', 'set_id') if w in src])
ST = rd('Set_Interface_Tests.csv'); by = collections.defaultdict(list)
for r in ST: by[int(r['year'])].append(r)
diffcols = collections.Counter()
for y, rs in by.items():
    for k in rs[0]:
        if k in ('caller', 'test_only'): continue
        if len({r[k] for r in rs}) > 1: diffcols[k] += 1
print('C3 Set_Interface_Tests: %d rows, %d callers; columns that vary across callers:' % (len(ST), len({r['caller'] for r in ST})), sorted(diffcols))
payer_cols = {k for k in diffcols if any(w in k for w in ('patient', 'public', 'insurer', 'household', 'cash', 'drawdown', 'borrowing', 'burden'))}
print('C4 non-payer columns that vary across callers (should be none):', sorted(set(diffcols) - payer_cols))
# different payer calculators and demand scales, same policy: eligibility/supply must not change
def payer_a(chosen, p, b, d, price, universal=False, transitioned=0.): return dict(HOUSEHOLD=chosen * 1e-7, GOVERNMENT=chosen * 2e-7, INSURER=chosen * 3e-7) if False else None
outs = []
for share in (0., .3, 1.):
    for ep in (450000.,):
        fin2 = dict(HOUSEHOLD=share, GOVERNMENT=(1 - share) / 2, INSURER=(1 - share) / 2)
        d = dict(price_index=1., population_scale=1., registry_population=IN['registry_population_reference'], age_demand_episodes=ep, clinical_strata=IN['clinical_strata'])
        outs.append(CommonInterface.run_common(2040, d, base_p, fin2))
inv = [k for k in ('chosen_transitions', 'universal_palliative_served', 'overlap_patients', 'resource_units_used', 'law_passed', 'implementation_phase', 'explicit_supported_appropriate_requests') if len({o[k] for o in outs}) > 1]
print('C5 financing share 0/.3/1 -> supply/eligibility columns that changed:', inv or 'none', '| patient payment varies:', [round(o['patient_payment_delta_trn'], 5) for o in outs])
# ---------------- D: F annual recalculation / comparability
dg = [(y, f(A[('LATEST_F', y)], 'real_gdp_trn') - f(A0[('LATEST_F', y)], 'real_gdp_trn')) for y in Y]
print('D1 LATEST_F real GDP new-old: 2035 %.6f 2040 %.6f 2055 %.6f ; max |diff| %.6f (%d), sign changes %d' % (dg[9][1], dg[14][1], dg[29][1], max(abs(v) for _, v in dg), max(dg, key=lambda t: abs(t[1]))[0], sum(1 for i in range(1, 30) if dg[i][1] * dg[i - 1][1] < 0)))
print('D2 LATEST_F 2055 real GDP new %.9f old %.9f' % (f(A[('LATEST_F', 2055)], 'real_gdp_trn'), f(A0[('LATEST_F', 2055)], 'real_gdp_trn')))
reg = 0; regmax = 0.
for c in A0:
    if c[0] in ('LATEST_F',) or c not in A: continue
for c in ('NO_VAT', 'NO_EDUCATION', 'MEDICAL_OFF', 'F_ONLY_NO_COPAY'):
    m = max(abs(f(A[(c, y)], 'real_gdp_trn') - f(A0[(c, y)], 'real_gdp_trn')) for y in Y); regmax = max(regmax, m)
print('D3 other cases max |real GDP new-old| (NO_VAT, NO_EDUCATION, MEDICAL_OFF, F_ONLY_NO_COPAY): %.6f' % regmax)
mo = max(abs(f(A[('MEDICAL_OFF', y)], 'real_gdp_trn') - f(A0[('MEDICAL_OFF', y)], 'real_gdp_trn')) for y in Y); print('D4 MEDICAL_OFF new-old max abs diff %.2e (should be 0: no medical change)' % mo)
SQC = rd('SQ_Common_Comparison.csv'); offfix = max(abs(f(r, 'off_vs_fixed')) for r in SQC); print('D5 SQ common OFF replay vs fixed SQ: max abs diff over 180 cells %.2e' % offfix)
for y in (2035, 2040, 2055):
    print('D6 SQ common effect %d: ' % y, {r['metric']: round(f(r, 'common_effect'), 6) for r in SQC if int(r['year']) == y})
CF = rd('Common_ON_F_SQ_Comparison.csv'); print('D7 F(common ON) - SQ(common ON) 2055:', {r['metric']: round(f(r, 'difference'), 4) for r in CF if int(r['year']) == 2055}); print('   scope note:', CF[0]['scope_difference'][:160])
SQA = {(r['case'], int(r['year'])): r for r in rd('SQ_Common_Annual.csv')}
tot = {y: f(A[('LATEST_F', y)], 'real_gdp_trn') - f(SQA[('SQ_COMMON_OFF_REPLAY', y)], 'real_gdp_trn') for y in Y}
print('D8 LATEST_F minus SQ common-OFF replay 2055: %.6f' % tot[2055])
# Nonadditivity
PE = collections.defaultdict(float)
for r in rd('Policy_Effects.csv'):
    if r['metric'] == 'real_gdp_trn': PE[int(r['year'])] += float(r['marginal_in_integrated_F'])
NA = {int(r['year']): r for r in rd('Nonadditivity.csv')}
mx = max(abs(f(NA[y], 'nonadditivity') - (PE[y] - (f(A[('LATEST_F', y)], 'real_gdp_trn') - f(A[('SQ_FIXED', y)], 'real_gdp_trn')))) for y in Y)
print('D9 Nonadditivity.csv recomputed from Policy_Effects/Annual: max abs diff %.2e ; 2055 nonadditivity %.6f ; additive flag %s' % (mx, f(NA[2055], 'nonadditivity'), NA[2055]['additive_attribution']))
inv = [r for r in rd('Policy_Effects.csv') if r['channel'] == 'INVESTMENT']; print('D10 INVESTMENT rows', len(inv), 'connection_status', {r.get('connection_status') for r in inv})
# ---------------- E: accounting (independent ledger, with error injection)
def ledger(r):
    uses = f(r, 'government_cost_delta_trn') + f(r, 'medical_other_spending_crowded_trn') - f(r, 'insurer_balance_delta_trn') + f(r, 'medical_financing_premium_trn')
    srcs = sum(f(r, k) for k in ('medical_financing_tax_trn', 'medical_financing_premium_trn', 'medical_other_spending_crowded_trn', 'medical_policy_debt_issue_trn', 'medical_unassigned_after_sources_trn')) - f(r, 'medical_policy_debt_redemption_trn') - f(r, 'medical_policy_asset_addition_trn')
    return uses - srcs
mxl = max(abs(ledger(r)) for r in MA.values()); print('E1 financing ledger residual over', len(MA), 'rows: max abs %.2e' % mxl)
# a second, structurally different identity: need = government expenditure - insurer balance + interest, rebuilt from claim-level columns
mxn = 0.; mxc = 0.
for r in MA.values():
    mxc = max(mxc, abs(f(r, 'patient_payment_delta_trn') + f(r, 'public_clinical_payment_delta_trn') + f(r, 'insurer_clinical_payment_delta_trn') - f(r, 'clinical_cost_delta_trn')))
print('E2 clinical claims identity (patient+public+insurer = clinical cost) max abs %.2e' % mxc)
inj = 0
for r in list(MA.values()):
    for k in ('medical_financing_tax_trn', 'medical_policy_debt_issue_trn', 'medical_other_spending_crowded_trn'):
        q = dict(r); q[k] = str(float(q[k]) + .01)
        if abs(ledger(q)) > 1e-3: inj += 1
print('E3 error injection of +0.01兆円 into a single source: detected in', inj, 'of', 3 * len(MA), 'trials')
# stock-flow of medical debt and assets
sf = 0.
for c in cases:
    debt = asset = 0.
    for y in Y:
        r = MA[(c, y)]; debt += f(r, 'medical_policy_debt_issue_trn') - f(r, 'medical_policy_debt_redemption_trn'); asset += f(r, 'medical_policy_asset_addition_trn')
        sf = max(sf, abs(debt - f(r, 'medical_policy_debt_stock_trn')), abs(asset - f(r, 'medical_policy_financial_asset_stock_trn')))
print('E4 debt/asset stock-flow max abs %.2e' % sf)
st = collections.Counter(r.get('financing_account_status') for r in MA.values()); print('E5 financing_account_status counts', dict(st), '; post_financing_transfer_residual blank in all rows:', all(r['post_financing_transfer_residual_trn'] == '' for r in MA.values()))
# household sensitivity
HH = collections.defaultdict(list)
for r in rd('Household.csv'):
    if r['case'] == 'LATEST_F' or r['case'].startswith('HH_'): HH[int(r['year'])].append(r)
HS = {(r['year'], r['metric']): r for r in rd('Household_Sensitivity.csv')}; bad = 0
for y in Y:
    for m in ('household_direct_cash_burden_delta_trn', 'household_total_economic_burden_delta_trn', 'total_medical_household_cash_delta_trn'):
        v = [f(r, m) for r in HH[y]]; row = HS[(str(y), m)]
        if abs(min(v) - f(row, 'lower')) > 1e-12 or abs(max(v) - f(row, 'upper')) > 1e-12: bad += 1
print('E6 Household_Sensitivity recomputed min/max: mismatching rows', bad)
for y in Y:
    row = HS[(str(y), 'household_direct_cash_burden_delta_trn')]
    if y in (2030, 2035, 2040, 2045, 2050, 2055): print('E7 direct cash burden range %d: %.1f ~ %+.1f 億円/年 (sign reversal %s)  | total medical household cash (incl. taxes/premiums) %.0f ~ %.0f 億円/年' % (y, 1e4 * f(row, 'lower'), 1e4 * f(row, 'upper'), row['sign_reversal'], 1e4 * f(HS[(str(y), 'total_medical_household_cash_delta_trn')], 'lower'), 1e4 * f(HS[(str(y), 'total_medical_household_cash_delta_trn')], 'upper')))
print('E8 years with sign reversal in direct cash burden (2026-2055):', [y for y in Y if HS[(str(y), 'household_direct_cash_burden_delta_trn')]['sign_reversal'] == 'True'][:3], '...', sum(1 for y in Y if HS[(str(y), 'household_direct_cash_burden_delta_trn')]['sign_reversal'] == 'True'), 'years')
# ---------------- F: patient cap audit recomputed with a separate claim implementation (statutory-style rules, F uniform 30%, caps x0.9)
def claim(age, grp, bill, months, y, capm):
    inf = math.inf; co = .3
    eld = age in ('AGE70_74', 'AGE75PLUS')
    if grp == 'TAXFREE': cap = 25700 if eld else 36900; multi = 24600; ann = 290000
    elif grp == 'GENERAL': cap = 61500; multi = 34500; ann = 410000
    elif grp == 'MIDDLE': cap = 85800 + max(0, bill - 286000) * .01; multi = 44400; ann = 530000
    else: cap = 179100 + max(0, bill - 597000) * .01; multi = 93000; ann = 1110000
    cap *= capm; multi *= capm; ann *= capm
    return min(sum(min(bill * co, cap if i < 3 else multi) for i in range(months)), ann)
AU = rd('Patient_Cap_Audit.csv'); worst = 0.; viol = 0
for r in AU:
    m = int(r['months']); a0 = claim(r['age'], r['income'], f(r, 'bill_before_yen') / m, m, 2035, .9); a1 = claim(r['age'], r['income'], f(r, 'bill_after_yen') / m, m, 2035, .9)
    worst = max(worst, abs(a0 - f(r, 'paid_before_yen')), abs(a1 - f(r, 'paid_after_yen')), abs((a1 - a0) / 100000 - f(r, 'marginal_rate')) * 1e5)
    viol += not (-1e-9 <= f(r, 'marginal_rate') <= .3 + 1e-9)
print('F1 Patient_Cap_Audit: %d rows recomputed with separate claim code: max abs diff (yen) %.4f ; marginal rate outside [0,0.3]: %d ; rate range %.4f..%.4f' % (len(AU), worst, viol, min(f(r, 'marginal_rate') for r in AU), max(f(r, 'marginal_rate') for r in AU)))
u = [f(CE[('LATEST_F', y)], 'universal_palliative_patient_trn') / f(CE[('LATEST_F', y)], 'universal_palliative_cost_trn') for y in (2035, 2040, 2055) if f(CE[('LATEST_F', y)], 'universal_palliative_cost_trn')]
print('F2 universal palliative patient share of its cost (LATEST_F 2035/2040/2055):', [round(100 * v, 2) for v in u], '%')
# ---------------- G: before/after tables rebuilt from the two fixed folders; years where capacity_unmet differs from transition_unmet
bad = 0; n = 0
for r in rd('Before_After.csv'):
    k = (r['case'], int(r['year'])); n += 1
    if abs(f(A0[k], r['metric']) - f(r, 'old')) > 1e-9 or abs(f(A[k], r['metric']) - f(r, 'new')) > 1e-9 or abs(f(r, 'new') - f(r, 'old') - f(r, 'difference')) > 1e-9: bad += 1
print('G1 Before_After.csv rows rebuilt from Annual.csv of both folders: %d rows, mismatches %d' % (n, bad))
bad = 0; n = 0
for r in rd('Supply_Before_After.csv'):
    k = (r['case'], int(r['year'])); n += 1
    if abs(f(CE0[k], r['metric']) - f(r, 'old')) > 1e-9 or abs(f(CE[k], r['metric']) - f(r, 'new')) > 1e-9: bad += 1
print('G2 Supply_Before_After.csv rebuilt from Common_EndOfLife.csv of both folders: %d rows, mismatches %d' % (n, bad))
print('G3 LATEST_F years where capacity_unmet > transition_unmet + 1:', [y for y in Y if f(CE[('LATEST_F', y)], 'capacity_unmet') > f(CE[('LATEST_F', y)], 'transition_unmet') + 1])
tr = [(y, f(CE[('LATEST_F', y)], 'chosen_transitions'), f(CE0[('LATEST_F', y)], 'chosen_transitions')) for y in (2032, 2033, 2034, 2035, 2045, 2055)]
print('G4 LATEST_F chosen transitions new/old:', [(y, round(a), round(b)) for y, a, b in tr])
print('G5 LATEST_F household direct cash burden 2055 new %.5f old %.5f (兆円)' % (f(CE[('LATEST_F', 2055)], 'household_direct_cash_burden_delta_trn'), f(CE0[('LATEST_F', 2055)], 'household_direct_cash_burden_delta_trn')))
sv = [(c, y) for (c, y), r in CE.items() if f(r, 'universal_palliative_served') > f(r, 'universal_palliative_need') + 1e-6]
print('G6 case-years with universal_palliative_served > universal_palliative_need:', len(sv))
print('G7 Household.csv sign convention: positive_sign =', rd('Household.csv')[0]['positive_sign'][:200])
