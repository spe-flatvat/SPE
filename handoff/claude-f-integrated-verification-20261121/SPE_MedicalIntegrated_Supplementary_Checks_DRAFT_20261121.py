#!/usr/bin/env python3
# Claude supplementary checks on 6986bb7 F medical-corrected integrated run. Read-only; data from CSV only.
# Usage: python3 -I <this> <repo_root_at_6986bb7>
import sys, os, csv, json, collections
R = sys.argv[1]; D = os.path.join(R, 'handoff/f-medical-corrected-integrated-20261121')
rd = lambda n: list(csv.DictReader(open(os.path.join(D, n))))
A = {(r['case'], int(r['year'])): r for r in rd('Annual.csv')}
CE = {(r['case'], int(r['year'])): r for r in rd('Common_EndOfLife.csv')}
f = lambda c, y, k: float(A[(c, y)][k])
Y = range(2026, 2056)
cases = sorted({c for c, _ in A}); print('cases', len(cases), 'rows', len(A))
# 1 Policy_Effects marginals recomputed from Annual
CH = ['VAT', 'FOREIGN', 'ELDER', 'PENSION', 'HOUSEHOLD_A', 'HOUSEHOLD_B', 'HOUSEHOLD_C', 'EDUCATION', 'INVESTMENT', 'FIRM', 'COMMON', 'F_MEDICAL']
PE = {(r['channel'], r['metric'], int(r['year'])): float(r['marginal_in_integrated_F']) for r in rd('Policy_Effects.csv') if r['metric'] == 'real_gdp_trn'}
bad = max(abs(PE[(c, 'real_gdp_trn', y)] - (f('LATEST_F', y, 'real_gdp_trn') - f('NO_' + c, y, 'real_gdp_trn'))) for c in CH for y in Y if (c, 'real_gdp_trn', y) in PE)
print('1 Policy_Effects GDP marginals vs Annual recompute: max abs diff %.2e' % bad)
# 2 additivity: sum of leave-one-out marginals vs total
for y in (2030, 2040, 2055):
    tot = f('LATEST_F', y, 'real_gdp_trn') - f('SQ_FIXED', y, 'real_gdp_trn'); s = sum(f('LATEST_F', y, 'real_gdp_trn') - f('NO_' + c, y, 'real_gdp_trn') for c in CH)
    print('2 %d total vs SQ %.4f  sum LOO marginals %.4f  non-additive %.4f' % (y, tot, s, s - tot))
# 3 inert channels
cols = [k for k in A[('LATEST_F', 2026)] if k != 'case']
for c in ('INVESTMENT', 'COMMON'):
    d = [k for k in cols if any(A[('LATEST_F', y)][k] != A[('NO_' + c, y)][k] for y in Y)]
    mg = max(abs(f('LATEST_F', y, 'real_gdp_trn') - f('NO_' + c, y, 'real_gdp_trn')) for y in Y)
    print('3 NO_%s: differing columns %d; max |GDP marginal| %.2e' % (c, len(d), mg))
# 4 capacity double use
mx = 0; yrs = []
for y in Y:
    r = CE[('LATEST_F', y)]; ch, un, cap = float(r['chosen_transitions']), float(r['universal_palliative_served']), float(r['transition_capacity'])
    if ch + un > cap * 1.0000001: yrs.append(y); mx = max(mx, (ch + un) / cap if cap else 0)
print('4 capacity double use: years with chosen+universal > capacity: %d (first %s), max ratio %.3f' % (len(yrs), yrs[:1], mx))
for y in (2035, 2045, 2055):
    r = CE[('LATEST_F', y)]; print('   ', y, {k: round(float(r[k])) for k in ('chosen_transitions', 'universal_palliative_served', 'transition_capacity')})
# 5 universal palliative payer: share paid by patient
for y in (2035, 2055):
    r = CE[('LATEST_F', y)]; c = float(r['universal_palliative_cost_trn']); print('5 %d universal cost %.4f patient %.4f (%.1f%%) public %.4f insurer %.4f' % (y, c, float(r['universal_palliative_patient_trn']), 100 * float(r['universal_palliative_patient_trn']) / c, float(r['universal_palliative_public_trn']), float(r['universal_palliative_insurer_trn'])))
# 6 VA x finance grid
print('6 GDP2055 grid (rows VA 0/50/100, cols FIN 0/50/100):')
for va in (0, 50, 100): print('   ', [round(f('VA%d_FIN%d' % (va, fi), 2055, 'real_gdp_trn'), 4) for fi in (0, 50, 100)])
# 7 GDP decomposition vs reference cases
for ref in ('SQ_FIXED', 'OLD_EDUCATION_F', 'OLD_MEDICAL_F', 'MEDICAL_OFF'):
    print('7 LATEST_F - %s GDP: %s' % (ref, {y: round(f('LATEST_F', y, 'real_gdp_trn') - f(ref, y, 'real_gdp_trn'), 4) for y in (2030, 2040, 2055)}))
# 8 medical finance accounting identities (LATEST_F)
mm = 0
for c in cases:
    for y in Y:
        a = A[(c, y)]
        try: need = float(a['medical_financing_need_before_sources_trn']); parts = sum(float(a[k]) for k in ('medical_financing_tax_trn', 'medical_financing_premium_trn', 'medical_other_spending_crowded_trn', 'medical_policy_debt_issue_trn')) - float(a['medical_policy_debt_redemption_trn']) - float(a['medical_policy_asset_addition_trn']) + float(a['medical_unassigned_after_sources_trn'])
        except (KeyError, ValueError): continue
        mm = max(mm, abs(need - parts))
print('8 finance sources identity (need = tax+prem+crowd+debt net+unassigned) max abs %.2e' % mm)
# 9 year jumps in LATEST_F GDP and household cash
jp = sorted(((abs(f('LATEST_F', y, 'real_gdp_trn') - f('LATEST_F', y - 1, 'real_gdp_trn')), y) for y in range(2027, 2056)), reverse=True)[:3]
print('9 largest yoy GDP moves LATEST_F:', [(y, round(v, 3)) for v, y in jp])
# 10 household sensitivity
S = [r for r in rd('Household_Sensitivity.csv') if r['metric'] == 'household_direct_cash_burden_delta_trn']
print('10 household direct cash burden range (兆円/年):', [(r['year'], round(float(r['lower']), 4), r['lower_case'], round(float(r['upper']), 4), r['upper_case'], r['sign_reversal']) for r in S if r['year'] in ('2035', '2040', '2055')])
# 11 post_financing_transfer_residual: tautological (identically zero by construction)
z = max(abs(float(A[(c, y)]['post_financing_transfer_residual_trn'] or 0)) for c in cases for y in Y)
print('11 post_financing_transfer_residual_trn max |value| over all 1650 rows: %.2e (identically 0 = not an independent check)' % z)
# 12 2026->2027 step is a base-year feature shared with SQ
print('12 GDP 2026->2027 step: SQ_FIXED %.1f -> %.1f ; LATEST_F %.1f -> %.1f (same step, not F-induced)' % (f('SQ_FIXED', 2026, 'real_gdp_trn'), f('SQ_FIXED', 2027, 'real_gdp_trn'), f('LATEST_F', 2026, 'real_gdp_trn'), f('LATEST_F', 2027, 'real_gdp_trn')))
