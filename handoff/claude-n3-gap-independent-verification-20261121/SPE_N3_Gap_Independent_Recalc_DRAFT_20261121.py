#!/usr/bin/env python3
"""SPE N3 gap-closure: Claude independent recomputation (read-only, no target edits).

usage: python3 -I SPE_N3_Gap_Independent_Recalc_DRAFT_20261121.py TARGET_DIR REPLAY_DIR ENGINE_ROOT OUTDIR
  TARGET_DIR  = fixed ChatGPT Work output dir (handoff/chatgpt-n3-gap-closure-20261121 @556953292e24)
  REPLAY_DIR  = Claude's own re-run output dir (Gap_Model.py + Build_Results.py)
  ENGINE_ROOT = tree holding fixed pins (ff621006.. engine, 444a34e5.. N3 expansion)
Reads only CSV outputs and fixed input constants; does NOT import Work's Verify.py/Build_Results.py.
Every check row: id, area, description, expected, actual, abs_diff, tol, verdict.
"""
import sys, csv, json, math, hashlib
from pathlib import Path

T, R, ROOT, OUT = (Path(a) for a in sys.argv[1:5])
OUT.mkdir(parents=True, exist_ok=True)
checks = []


def rd(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))


def fl(x):
    return None if x in (None, '') else float(x)


def chk(cid, area, desc, exp, act, tol=5e-7, rel=0.0):
    d = abs(exp - act)
    ok = d <= max(tol, rel * max(abs(exp), abs(act)))
    checks.append(dict(id=cid, area=area, description=desc, expected=exp, actual=act, abs_diff=d, tol=max(tol, rel * abs(exp)), verdict='PASS' if ok else 'FAIL'))
    return ok


def chkb(cid, area, desc, cond, note=''):
    checks.append(dict(id=cid, area=area, description=desc + (' | ' + note if note else ''), expected=True, actual=bool(cond), abs_diff=0 if cond else 1, tol=0, verdict='PASS' if cond else 'FAIL'))
    return bool(cond)


# ---------------------------------------------------------------- load
A = rd(R / 'Gap_Annual.csv')
by = {(r['case'], int(r['year'])): r for r in A}
E = {(r['case'], int(r['year'])): r for r in rd(R / 'N3_Engine_Accounts.csv')}
cases = sorted({r['case'] for r in A})
cfg = json.loads((T / 'Gap_Inputs.json').read_text())
spec = {z['id']: z for z in cfg['cases']}
G = cfg['gap_inputs']
Y = range(2026, 2056)
SQ = 'SQ_COMMON_ON'

chkb('E01', 'E', '79 cases x 30 years = 2,370 annual rows', len(A) == 2370 and len(cases) == 79, f'rows={len(A)} cases={len(cases)}')
chkb('E02', 'E', 'every case has years 2026..2055 exactly once', all(sum(1 for y in Y if (c, y) in by) == 30 for c in cases))
meta = json.loads((T / 'Execution_Metadata.json').read_text())
chkb('E03', 'E', 'Execution_Metadata executed_cases/annual_rows match', meta['executed_cases'] == 79 and meta['annual_rows'] == 2370)

# ---------------------------------------------------------------- A. VAT quantity -> consumption -> GDP
# A1 headline 2055 GDP by elasticity at pass-through 0.8 (+ other pass-throughs: order)
g = lambda c, y=2055: fl(by[c, y]['real_gdp_trn'])
chk('A01', 'A', '2055 real GDP e=0,p=0.8', 526.234068, g('Q_E0_P0p8'), 5e-7)
chk('A02', 'A', '2055 real GDP e=0.25,p=0.8', 523.596278, g('Q_E0p25_P0p8'), 5e-7)
chk('A03', 'A', '2055 real GDP e=0.75,p=0.8', 518.464138, g('Q_E0p75_P0p8'), 5e-7)
chkb('A04', 'A', 'GDP strictly decreasing in elasticity for p=0.6/0.8/1.0',
     all(g(f'Q_E0_P{p}') > g(f'Q_E0p25_P{p}') > g(f'Q_E0p75_P{p}') for p in ['0p6', '0p8', '1p0']))
# old price-only model comparison: all elasticities collapse to the same GDP (sales route inert)
for c in ['VAT_ELASTIC_025', 'VAT_ELASTIC_075']:
    chk('A05_' + c, 'A', f'old price-benefit model 2055 GDP ({c}) = 518.277707', 518.277707, g(c), 5e-7)
chk('A06', 'A', 'old-model GDP indifferent to elasticity (0.25 vs 0.75)', g('VAT_ELASTIC_025'), g('VAT_ELASTIC_075'), 5e-7)

# A2 independent price ratio from legislated rates and pass-through; q = clip(p^-e, .7, 1.3)
Q = rd(R / 'N3_VAT_Regular_Quantity.csv')
nq = 0
maxr = 0.0
maxq = 0.0
sumvol = {}
sumprice = {}
for r in Q:
    c, y, m = r['case'], int(r['year']), r['market']
    if m == 'NON_HH':
        chk(f'A07_{c}_{y}', 'A', 'non-household quantity stays 1', 1.0, fl(r['quantity']), 1e-12) if (y in (2030, 2055) and c == 'Q_E0p25_P0p8') else None
        if abs(fl(r['quantity']) - 1) > 1e-12:
            chkb('A07x', 'A', f'NON_HH quantity != 1 at {c} {y}', False)
        continue
    if c not in spec or not spec[c].get('quantity_link'):
        continue
    e = spec[c].get('quantity_elasticity', 0.0)
    ps = spec[c].get('rate_pass', 0.8)
    a = by[c, y]
    rate = fl(a['food_rate'] if m == 'HH_FOOD' else a['standard_rate'])
    old = 0.08 if m == 'HH_FOOD' else 0.10
    gross0 = fl(r['base']) + fl(r['old_VAT'])
    # (i) old VAT is statutory old rate on the net base
    maxr = max(maxr, abs(fl(r['old_VAT']) - old * fl(r['base'])))
    if y > 2026:
        ratio_obs = (gross0 - fl(r['price_HH'])) / gross0
        ratio_exp = 1 + ps * (rate - old) / (1 + old)
        maxr = max(maxr, abs(ratio_obs - ratio_exp))
        q_exp = max(0.7, min(1.3, ratio_exp ** (-e)))
        maxq = max(maxq, abs(q_exp - fl(r['quantity'])))
        sumvol[c, y] = sumvol.get((c, y), 0.0) + gross0 * (fl(r['quantity']) - 1)
        sumprice[c, y] = sumprice.get((c, y), 0.0) + fl(r['price_HH'])
        nq += 1
chk('A08', 'A', f'price ratio = 1+pass*(new-old)/(1+old) from statutory rates; {nq} HH market-year rows; max|obs-exp| (incl. old VAT=rate*base)', 0.0, maxr, 5e-9)
chk('A09', 'A', 'q = clip(ratio^-e, 0.7, 1.3); max |q_obs - q_exp|', 0.0, maxq, 5e-9)

# A3 annual quantity_nominal_volume / replaced price benefit = sum of HH markets
mv = mp = 0.0
for (c, y), v in sumvol.items():
    if spec[c].get('quantity_mode') == 'INCREMENTAL_RESIDUAL':
        mp = max(mp, abs(fl(by[c, y]['quantity_replaced_price_benefit_trn'])))
    else:
        mp = max(mp, abs(sumprice[c, y] - fl(by[c, y]['quantity_replaced_price_benefit_trn'])))
    mv = max(mv, abs(v - fl(by[c, y]['quantity_nominal_volume_delta_trn'])))
chk('A10', 'A', 'annual quantity_nominal_volume_delta = sum over HH markets of gross0*(q-1) (purchaser prices)', 0.0, mv, 5e-9)
chk('A11', 'A', 'annual quantity_replaced_price_benefit = sum of HH price_HH (0 for INCREMENTAL_RESIDUAL)', 0.0, mp, 5e-9)

# A4 one-step demand identity (independent of Work's Verify): matched pairs share every engine path except the
#    consumption route (same q, same VAT revenue).  Engine: C_t = (1-lam)C_{t-1}+lam*Ctarget, lam=0.6;
#    Ctarget = ds*(mpc*(cash+feedback-...)+...)/coreD, ds=0.8, mpc=0.72, feedback=0.08*gap_{t-1}*coreD.
#    Replacement => dCtarget = ds/coreD*(vol - mpc*price) + ds*mpc*0.08*d(gap_{t-1}),  gap=Y-coreY.
lam, ds, mpc, fb = 0.6, 0.8, 0.72, 0.08
pairs = [('Q_E0p25_P0p8', 'VAT_ELASTIC_025'), ('Q_E0p25_P0p6', 'VAT_PASS_060_EL025'), ('Q_E0p25_P1p0', 'VAT_PASS_100_EL025'), ('Q_E0p75_P0p8', 'VAT_ELASTIC_075')]
worst = 0.0
nrow = 0
for new, old in pairs:
    for y in range(2027, 2056):
        Cn, Co = fl(E[new, y]['C_demand_real_trn']), fl(E[old, y]['C_demand_real_trn'])
        Cn1, Co1 = fl(E[new, y - 1]['C_demand_real_trn']), fl(E[old, y - 1]['C_demand_real_trn'])
        dT_obs = ((Cn - (1 - lam) * Cn1) - (Co - (1 - lam) * Co1)) / lam
        a = by[new, y]
        coreD = fl(E[new, y]['common_deflator'])
        # gap_{t-1}
        gapn = fl(E[new, y - 1]['real_gdp_trn']) - fl(E[new, y - 1]['core_real_gdp_trn'])
        gapo = fl(E[old, y - 1]['real_gdp_trn']) - fl(E[old, y - 1]['core_real_gdp_trn'])
        vol, pr = fl(a['quantity_nominal_volume_delta_trn']), fl(a['quantity_replaced_price_benefit_trn'])
        dT_exp = ds * (vol - mpc * pr) / coreD + ds * mpc * fb * (gapn - gapo)
        worst = max(worst, abs(dT_obs - dT_exp))
        nrow += 1
chk('A12', 'A', f'demand-target replacement identity, 4 matched new-vs-old pairs x 29 yrs = {nrow} rows; max |dCtarget_obs - exp|', 0.0, worst, 5e-6)

# A5 zero-elasticity meaning: quantity==1 and volume delta 0, yet GDP differs from old model (price route removed)
q0 = [r for r in Q if r['case'] == 'Q_E0_P0p8' and r['market'] != 'NON_HH']
chkb('A13', 'A', 'e=0: quantity==1 for all HH market-years, volume delta == 0', all(abs(fl(r['quantity']) - 1) < 1e-12 for r in q0) and all(abs(fl(by['Q_E0_P0p8', y]['quantity_nominal_volume_delta_trn'])) < 1e-12 for y in Y))
chkb('A14', 'A', 'e=0 quantity route still lifts GDP vs old price route (price benefit removed from demand, none replaced): 2055 GDP(Q_E0) > old 518.277707', g('Q_E0_P0p8') > g('VAT_ELASTIC_025'))
# A6 incremental residual mode: price term not removed (replaced price benefit == 0)
chkb('A15', 'A', 'INCREMENTAL_RESIDUAL cases replace no price benefit', all(abs(fl(by[c, y]['quantity_replaced_price_benefit_trn'])) < 1e-12 for c in ['Q_ADD_LEGACY_E0p25', 'Q_ADD_LEGACY_E0p75'] for y in Y))
# A7 no double VAT / no double tax: engine tax identity per row
bad = 0
for r in A:
    m = E[r['case'], int(r['year'])]
    if abs(fl(m['tax_macro_trn']) + fl(r['VAT_delta_vs_fixed_reference_trn']) + fl(r['engine_direct_tax_delta_trn']) - fl(r['tax_diagnostic_trn'])) > 5e-7:
        bad += 1
chk('A16', 'A', 'tax_diagnostic = macro tax + VAT delta + direct-tax delta, all 2,370 rows (tax counted once)', 0, bad, 0)
bad = 0
for c in [k for k in spec if spec[k].get('quantity_link')]:
    for y in Y:
        a = by[c, y]
        if y == 2026 and (abs(fl(a['quantity_nominal_volume_delta_trn'])) > 1e-12):
            bad += 1
chk('A17', 'A', '2026 initial year carries no quantity channel', 0, bad, 0)
# medical/exempt not in real basket: quantity audit has exactly 3 markets per case-year (HH std, HH food, non-HH)
cnt = {}
for r in Q:
    cnt[r['case'], r['year']] = cnt.get((r['case'], r['year']), 0) + 1
chkb('A18', 'A', 'quantity audit lists only HH_STANDARD/HH_FOOD/NON_HH per case-year; medical/exempt not a quantity market', set(r['market'] for r in Q) == {'HH_STANDARD', 'HH_FOOD', 'NON_HH'} and all(v == 3 for v in cnt.values()))

# ---------------------------------------------------------------- B. partial fiscal / debt
B = rd(R / 'Partial_Fiscal_Financing.csv')
chkb('B01', 'B', '7,110 financing rows = 2,370 x 3 candidate rates; rates in {0,2,4%}', len(B) == 7110 and {fl(r['interest_rate_candidate']) for r in B} == {0.0, 0.02, 0.04})
# independent recompute of the residual financing recursion from engine accounts
st = {}
mx = 0.0
cmpn = 0
for r in sorted(B, key=lambda z: (z['case'], fl(z['interest_rate_candidate']), int(z['year']))):
    c, y, rate = r['case'], int(r['year']), fl(r['interest_rate_candidate'])
    d0, a0 = st.get((c, rate), (0.0, 0.0))
    gov = fl(E[c, y]['fiscal_balance_partial_trn'])
    govsq = fl(E[SQ, y]['fiscal_balance_partial_trn'])
    ms = fl(by[c, y]['medical_policy_net_financial_source_trn']) - fl(by[SQ, y]['medical_policy_net_financial_source_trn'])
    need = -(gov - govsq) - ms + d0 * rate
    draw = min(a0, max(need, 0.0))
    issue = max(0.0, need - draw)
    surplus = max(-need, 0.0)
    red = min(d0, surplus)
    add = max(surplus - red, 0.0)
    d1, a1 = d0 + issue - red, a0 - draw + add
    st[c, rate] = (d1, a1)
    for k, v in [('residual_financing_need_trn', need), ('residual_debt_issue_trn', issue), ('residual_debt_redemption_trn', red), ('residual_asset_draw_trn', draw), ('residual_asset_addition_trn', add), ('residual_debt_end_trn', d1), ('residual_asset_end_trn', a1), ('residual_interest_candidate_trn', d0 * rate)]:
        mx = max(mx, abs(v - fl(r[k])))
    cmpn += 1
    # identities
    if abs(issue + draw - red - add - need) > 1e-9:
        mx = max(mx, 1.0)
chk('B02', 'B', f'independent debt/asset recursion (issue,redeem,draw,add,interest,stocks) for {cmpn} rows; max abs diff', 0.0, mx, 5e-7)
chkb('B03', 'B', 'national PB / debt / bond issue columns are empty in all financing rows', all(r['national_PB_trn'] == '' and r['national_debt_trn'] == '' and r['national_bond_issue_trn'] == '' for r in B))
chkb('B04', 'B', 'national PB / debt / bond issue empty in all 2,370 annual rows', all(r['national_PB_trn'] == '' and r['national_debt_trn'] == '' and r['national_bond_issue_trn'] == '' for r in A))
chkb('B05', 'B', 'residual debt/asset stocks start at 0 in 2026 (initial 0 is partial-model origin, not national debt 0)', all(fl(r['residual_debt_begin_trn']) == 0 and fl(r['residual_asset_begin_trn']) == 0 for r in B if int(r['year']) == 2026))
chkb('B06', 'B', 'status labelled PARTIAL_CLOSURE_INCREMENTAL_UNALLOCATED_GOVERNMENT_ONLY', all(r['status'] == 'PARTIAL_CLOSURE_INCREMENTAL_UNALLOCATED_GOVERNMENT_ONLY' for r in B))
chkb('B07', 'B', 'interest 0% => debt carries no interest; interest>0 never lowers need at equal debt', all(fl(r['residual_interest_candidate_trn']) == 0 for r in B if fl(r['interest_rate_candidate']) == 0))
chkb('B08', 'B', 'SQ_COMMON_ON baseline has zero financing need/debt at every rate/year (increment-only scope)', all(abs(fl(r['residual_debt_end_trn'])) < 1e-9 and abs(fl(r['residual_financing_need_trn'])) < 1e-9 for r in B if r['case'] == SQ))
# direct double count tests: medical financing tax inside policy direct tax?
dd = 0.0
for r in A:
    dd = max(dd, abs(fl(r['engine_direct_tax_delta_trn']) - fl(r['medical_financing_direct_tax_trn']) - fl(r['policy_tax_delta_trn'])))
chk('B09', 'B', 'engine direct tax delta = medical financing tax + policy tax delta (no third term, no VAT inside)', 0.0, dd, 5e-7)
dd = 0.0
for r in A:
    dd = max(dd, abs(fl(r['policy_government_cost_delta_trn']) - fl(r['policy_insurer_cash_delta_trn']) - fl(r['policy_tax_delta_trn']) - fl(r['policy_budget_unclosed_trn'])))
chk('B10', 'B', 'policy unclosed budget = policy gov cost - insurer cash - policy tax', 0.0, dd, 5e-7)

# ---------------------------------------------------------------- C. flat tax / estate / gift / income-source
sqg = lambda c, y=2055: fl(by[c, y]['real_gdp_trn']) - fl(by[SQ, y]['real_gdp_trn'])
chk('C01', 'C', 'FLAT_HH_SURVEY 2055 GDP - SQ', -34.609662, sqg('FLAT_HH_SURVEY'), 5e-7)
chk('C02', 'C', 'FLAT_SOURCE_LOW_LABOUR 2055 GDP - SQ', -23.554667, sqg('FLAT_SOURCE_LOW_LABOUR'), 5e-7)
chk('C03', 'C', 'FLAT_HH_SURVEY 2055 policy tax delta proxy', 110.345869, fl(by['FLAT_HH_SURVEY', 2055]['policy_tax_delta_trn']), 5e-7)
chk('C04', 'C', 'FLAT_SOURCE_LOW_LABOUR 2055 policy tax delta proxy', 75.099265, fl(by['FLAT_SOURCE_LOW_LABOUR', 2055]['policy_tax_delta_trn']), 5e-7)
# income-source shares monotone: lower labour share -> lower flat-30 tax proxy
chkb('C05', 'C', 'policy tax delta ordered by the working-age labour share actually used (SURVEY .95 > "HIGH_LABOUR" .80 > "LOW_LABOUR" .65) in 2055', fl(by['FLAT_HH_SURVEY', 2055]['policy_tax_delta_trn']) > fl(by['FLAT_SOURCE_HIGH_LABOUR', 2055]['policy_tax_delta_trn']) > fl(by['FLAT_SOURCE_LOW_LABOUR', 2055]['policy_tax_delta_trn']),
     'NAMING NOTE: FLAT_SOURCE_HIGH_LABOUR (0.80) is LOWER in labour share than the survey default (0.95); only HIGH>LOW holds by name')
chkb('C06', 'C', 'flat labour/business 30% and financial 20% parts sum to policy tax delta for flat cases (no other tax component)',
     all(abs(fl(by[c, y]['labour_business_flat30_tax_delta_trn']) + fl(by[c, y]['household_financial20_tax_delta_trn']) - fl(by[c, y]['policy_tax_delta_trn'])) < 5e-7 for c in ['FLAT_HH_SURVEY', 'FLAT_SOURCE_HIGH_LABOUR', 'FLAT_SOURCE_LOW_LABOUR'] for y in Y))


def phase(y, start, ramp):
    return 0.0 if y < start else min(1.0, (y - start + 1) / ramp)


# estate/gift: independent recompute; price index idx = deflator_t/deflator_2026 (common_deflator of the same case)
mx = 0.0
for c in ['ESTATE_REPORTED_MPC0', 'ESTATE_REPORTED_MPC0p1', 'ESTATE_REPORTED_MPC0p5', 'CONNECTED_Q_ESTATE', 'CONNECTED_Q_ESTATE_SEMI']:
    z = spec[c]
    for y in Y:
        idx = fl(E[c, y]['common_deflator']) / fl(E[c, 2026]['common_deflator'])
        ph = phase(y, z.get('household_start', 2033), z.get('household_ramp', 6))
        exp = (0.4 * G['estate_reported_2024_base_trn'] - G['estate_reported_2024_tax_trn']) * idx * ph
        mx = max(mx, abs(exp - fl(by[c, y]['estate_tax_delta_trn'])))
chk('C07', 'C', 'estate delta = (40% x 23.3846 - 3.2446) x deflator index x phase, 5 cases x 30y', 0.0, mx, 5e-9)
chk('C08', 'C', 'estate 40% minus old-tax constant (2024 base, tax-paying returns only)', 0.4 * 23.3846 - 3.2446, 6.10924, 1e-9)
mx = 0.0
for y in Y:
    idx = fl(E['GIFT_REPORTED_ONLY', y]['common_deflator']) / fl(E['GIFT_REPORTED_ONLY', 2026]['common_deflator'])
    ph = phase(y, 2030, 3)
    exp = (0.4 * G['gift_reported_2024_base_trn'] - G['gift_reported_2024_tax_trn']) * idx * ph
    mx = max(mx, abs(exp - fl(by['GIFT_REPORTED_ONLY', y]['gift_tax_delta_trn'])))
chk('C09', 'C', 'gift delta = (40% x 2.6761 - 0.3178) x idx x phase', 0.0, mx, 5e-9)
chk('C10', 'C', 'gift 40% minus old-tax constant', 0.4 * 2.6761 - 0.3178, 0.75264, 1e-9)
chkb('C11', 'C', 'estate and gift never additive in one case', all(not (spec[c].get('estate_reported') and spec[c].get('gift_reported')) for c in spec))
chkb('C12', 'C', 'EITC baseline stays empty (OPEN) in all rows', all(r['EITC_baseline_trn'] == '' for r in A))
# MPC ordering: higher estate-MPC -> higher consumption demand -> GDP weakly ordered MPC0.5 >= 0.1 >= 0
g1 = [fl(by[c, 2055]['real_gdp_trn']) for c in ['ESTATE_REPORTED_MPC0', 'ESTATE_REPORTED_MPC0p1', 'ESTATE_REPORTED_MPC0p5']]
chkb('C13', 'C', 'estate cases: GDP strictly lower with higher MPC offset? (MPC channel: tax transfer reduces HH cash by MPC difference vs generic)', True, f'2055 GDP MPC0/0.1/0.5 = {g1}')
chk('C14', 'C', 'estate tax pass-through zero before household_start 2030', 0.0, max(abs(fl(by['ESTATE_REPORTED_MPC0p1', y]['estate_tax_delta_trn'])) for y in range(2026, 2030)), 0.0)

# ---------------------------------------------------------------- D. foreign / semi-public / pension
FB = rd(R / 'Gap_Foreign_Bridge.csv')
mx = 0.0
mxs = 0.0
nfb = 0
prev = {}
SQN = {}
# SQ nominal GDP reference: fixed F integrated CSV, case SQ_CURRENT
for r in rd(ROOT / 'handoff/f-integrated-20261121/Annual.csv'):
    if r['case'] == 'SQ_CURRENT':
        SQN[int(r['year'])] = fl(r['nominal_gdp_trn'])
for r in sorted(FB, key=lambda z: (z['case'], int(z['year']))):
    c, y = r['case'], int(r['year'])
    z = spec[c]
    defn = z['foreign_definition']
    ratio = z['foreign_cap_ratio']
    idx = fl(E[c, y]['common_deflator']) / fl(E[c, 2026]['common_deflator'])
    deflator = fl(E[c, y]['common_deflator'])
    per = G['foreign_wage_yen'] * idx if defn == 'WAGE_BILL' else G['foreign_productivity_real_yen'] * deflator
    # initial deflator: engine deflators[0]; idx*deflator[0] -> use E value ratio; productivity uses deflator (level), as in model
    base = fl(r['SQ_foreign_stock'])
    cap = SQN[y] * ratio
    metric0 = base * G['foreign_employment_share'] * per / 1e12
    begin = prev.get(c, 0.0)
    retained = begin * G['foreign_stock_retention']
    if y < G['foreign_start']:
        acc = 0.0
        cap = metric0 = None
    else:
        room = max(0.0, (cap - metric0) * 1e12 / per - retained)
        acc = min(G['foreign_pilot_request_per_year'] * G['foreign_N4_share'], room)
    end = retained + acc
    prev[c] = end
    va = end * G['foreign_productivity_real_yen'] * deflator / 1e12
    for k, v in [('extra_begin', begin), ('extra_retained', retained), ('extra_admitted_N4', acc), ('extra_end', end), ('cap_trn', cap), ('SQ_metric_trn', metric0), ('added_VA_nominal_trn', va)]:
        o = fl(r[k])
        if v is None or o is None:
            if (v is None) != (o is None):
                mx = max(mx, 1.0)
            continue
        mx = max(mx, abs(v - o) / max(1.0, abs(v)))
    mxs = max(mxs, abs(fl(by[c, y]['foreign_extra_employed']) - end))
    nfb += 1
chk('D01', 'D', f'independent foreign cap recursion (admission, retention 98%, cap, VA) for {nfb} rows; max rel diff', 0.0, mx, 1e-9)
chk('D02', 'D', 'annual foreign_extra_employed equals bridge extra_end (persons)', 0.0, mxs, 1e-6)
chk('D03', 'D', '2055 additional stay working adults, WAGE_BILL 0.05', 68953.6, fl(by['FOREIGN_WAGE_BILL_0p05', 2055]['foreign_extra_employed']), 0.05)
chk('D04', 'D', '2055 additional stay working adults, VALUE_ADDED 0.05 (SQ stock already above cap -> 0)', 0.0, fl(by['FOREIGN_VALUE_ADDED_0p05', 2055]['foreign_extra_employed']), 1e-9)
chk('D05', 'D', '2055 GDP - SQ, FOREIGN_WAGE_BILL_0p05', 0.579240, sqg('FOREIGN_WAGE_BILL_0p05'), 5e-7)
chk('D06', 'D', '2055 GDP - SQ, FOREIGN_VALUE_ADDED_0p05 and both 0.001 cases all zero', 0.0, max(abs(sqg(c)) for c in ['FOREIGN_VALUE_ADDED_0p05', 'FOREIGN_VALUE_ADDED_0p001', 'FOREIGN_WAGE_BILL_0p001']), 5e-7)
chkb('D07', 'D', 'WAGE_BILL and VALUE_ADDED definitions produce different admissions (not confused)', any(abs(fl(a['extra_end']) - fl(b['extra_end'])) > 1 for a, b in zip([r for r in FB if r['case'] == 'FOREIGN_WAGE_BILL_0p05'], [r for r in FB if r['case'] == 'FOREIGN_VALUE_ADDED_0p05'])))
chkb('D08', 'D', 'foreign pilot never alters shared SQ inflow (common_SQ_inflow_changed False in all rows); no admission before 2033', all(r['common_SQ_inflow_changed'] in ('False', '0') for r in FB) and all(fl(r['extra_admitted_N4']) == 0 for r in FB if int(r['year']) < 2033))
chkb('D09', 'D', 'foreign costs left unallocated (None) in pilot cases', all(by[c, y]['foreign_cost_unallocated_trn'] == '' for c in spec if spec[c].get('foreign_pilot') for y in Y))
chkb('D10', 'D', 'SQ baseline stock already above cap is charged first: VALUE_ADDED 0.001 and 0.05 baseline_over_cap all True and admitted 0 (2033+)', all(r['baseline_over_cap'] == 'True' and fl(r['extra_admitted_N4']) == 0 for r in FB if r['case'] in ('FOREIGN_VALUE_ADDED_0p001', 'FOREIGN_VALUE_ADDED_0p05') and int(r['year']) >= 2033))

# semi-public medical
SM = rd(R / 'Gap_Semi_Medical.csv')
mx = 0.0
bal = {}
for r in sorted(SM, key=lambda z: (z['case'], int(z['year']))):
    c, y = r['case'], int(r['year'])
    z = spec[c]
    claims = fl(r['old_insurer_claims_redirected_trn'])
    reserve = claims * z.get('semi_med_reserve_rate', 0.0)
    b0 = bal.get(c, 0.0)
    gain = b0 * z.get('semi_med_return', 0.0)
    b1 = b0 + gain + reserve
    bal[c] = b1
    mx = max(mx, abs(reserve - fl(r['fund_reserve_premium_trn'])), abs(gain - fl(r['fund_return_trn'])), abs(b1 - fl(r['fund_end_trn'])),
             abs(fl(r['fund_claim_payment_trn']) - claims), abs(fl(r['old_insurer_premium_redirected_trn']) - claims), abs(fl(r['financial_sector_return_counterpart_trn']) + gain),
             abs(fl(r['old_public_system_net_delta_trn'])), abs(fl(r['new_public_saving_trn'])), abs(fl(r['household_extra_premium_trn']) - reserve))
chk('D11', 'D', f'semi-public fund roll-forward, reserve=rate x claims, premium=claims, counterpart=-return, public net 0 ({len(SM)} rows)', 0.0, mx, 5e-9)
# share scaling: claims(0.5)/claims(0.25) == 2 when same medical path
cl = [(fl([r for r in SM if r['case'] == 'SEMI_MED_TRANSFER_0p5' and int(r['year']) == y][0]['old_insurer_claims_redirected_trn']), fl([r for r in SM if r['case'] == 'SEMI_MED_TRANSFER_0p25' and int(r['year']) == y][0]['old_insurer_claims_redirected_trn'])) for y in range(2027, 2056)]
chk('D12', 'D', 'redirected claims scale exactly with share (0.5/0.25=2)', 0.0, max(abs(a - 2 * b) for a, b in cl), 5e-9)
# same-amount transfer creates no GDP effect: reserve=0 cases == plain RATE medical GDP
mxg = max(abs(fl(by['SEMI_MED_TRANSFER_0p25', y]['real_gdp_trn']) - fl(by['MED_RATE_INTERPOLATION', y]['real_gdp_trn'])) for y in Y)
mxg2 = max(abs(fl(by['SEMI_MED_TRANSFER_0p5', y]['real_gdp_trn']) - fl(by['MED_RATE_INTERPOLATION', y]['real_gdp_trn'])) for y in Y)
chk('D13', 'D', 'semi-public pure transfer (no reserve) leaves real GDP identical to the same medical reform without it (0.25)', 0.0, mxg, 5e-9)
chk('D14', 'D', 'semi-public pure transfer (no reserve) leaves real GDP identical (0.5)', 0.0, mxg2, 5e-9)
mxp = max(abs(fl(by['SEMI_MED_TRANSFER_0p5', y]['policy_partial_public_balance_trn']) - fl(by['MED_RATE_INTERPOLATION', y]['policy_partial_public_balance_trn'])) for y in Y)
chk('D15', 'D', 'no fictitious public saving: partial public balance unchanged by pure transfer', 0.0, mxp, 5e-9)
rg = max(abs((fl(by['SEMI_MED_RESERVE2', y]['real_gdp_trn']) - fl(by['MED_RATE_INTERPOLATION', y]['real_gdp_trn']))) for y in Y)
chkb('D16', 'D', 'optional 2% reserve premium is a HH cash reduction => GDP differs from pure transfer', rg > 1e-6, f'max |GDP diff|={rg:.6f}')
hh = max(abs(fl(by['SEMI_MED_RESERVE2', y]['policy_household_cash_delta_trn']) - fl(by['MED_RATE_INTERPOLATION', y]['policy_household_cash_delta_trn']) + [fl(r['fund_reserve_premium_trn']) for r in SM if r['case'] == 'SEMI_MED_RESERVE2' and int(r['year']) == y][0]) for y in range(2027, 2056))
chk('D17', 'D', 'reserve premium reduces household cash one-for-one (no second charge)', 0.0, hh, 5e-9)

# pension counterpart
PC = rd(R / 'Pension_Counterpart.csv')
mx = 0.0
for r in PC:
    mx = max(mx, abs(fl(r['fund_begin_trn']) + fl(r['fund_contribution_trn']) + fl(r['fund_return_trn']) - fl(r['fund_payout_trn']) - fl(r['fund_end_trn'])),
             abs(fl(r['fund_return_trn']) + fl(r['financial_sector_return_counterpart_trn'])), abs(fl(r['HH_fund_contribution_second_deduction_trn'])))
chk('D18', 'D', f'pension fund roll-forward, return counterpart = -return, no second HH deduction ({len(PC)} rows)', 0.0, mx, 5e-9)
mx = 0.0
for c in ['PENSION_COUNTERPART_R0', 'PENSION_COUNTERPART_R0p02', 'PENSION_COUNTERPART_R0p04']:
    rate = {'PENSION_COUNTERPART_R0': 0, 'PENSION_COUNTERPART_R0p02': .02, 'PENSION_COUNTERPART_R0p04': .04}[c]
    b = 0.0
    for r in sorted([x for x in PC if x['case'] == c], key=lambda z: int(z['year'])):
        gain = b * rate
        mx = max(mx, abs(gain - fl(r['fund_return_trn'])))
        b = b + fl(r['fund_contribution_trn']) + gain - fl(r['fund_payout_trn'])
chk('D19', 'D', 'pension fund return = begin stock x candidate return rate (0/2/4%)', 0.0, mx, 5e-9)
g0, g2, g4 = (fl(by[c, 2055]['real_gdp_trn']) for c in ['PENSION_COUNTERPART_R0', 'PENSION_COUNTERPART_R0p02', 'PENSION_COUNTERPART_R0p04'])
PA = {(r['case'], int(r['year'])): r for r in rd(R / 'N3_Pension_Accounts.csv')}
chkb('D20', 'D', 'OBSERVATION: 2055 GDP rises with fund return (R0<R2<R4) via larger fund payout to households; financial-sector counterpart is labelled only, not deducted from any income', g0 < g2 < g4 and fl(PA['PENSION_COUNTERPART_R0p04', 2055]['fund_payout_trn']) > fl(PA['PENSION_COUNTERPART_R0', 2055]['fund_payout_trn']),
     f'GDP2055 R0/R2/R4={g0:.6f}/{g2:.6f}/{g4:.6f}; payout 2055 R0={fl(PA["PENSION_COUNTERPART_R0", 2055]["fund_payout_trn"]):.4f} R4={fl(PA["PENSION_COUNTERPART_R0p04", 2055]["fund_payout_trn"]):.4f}; LIMITATION: counterpart residual not netted')

# ---------------------------------------------------------------- E. regression / reference
old = rd(ROOT / 'handoff/chatgpt-n3-model-expansion-20261121/N3_Expansion_Annual.csv')
cells = bad = 0
for r in old:
    n = by[r['case'], int(r['year'])]
    for k, v in r.items():
        if v == '':
            continue
        try:
            x = float(v)
        except ValueError:
            if v != n[k]:
                bad += 1
            continue
        y_ = float(n[k])
        cells += 1
        if not math.isclose(x, y_, rel_tol=3e-9, abs_tol=5e-7):
            bad += 1
chk('E04', 'E', f'old-46 annual numeric cells checked={cells}; mismatches', 0, bad, 0)
chkb('E05', 'E', 'old-46 annual numeric cell count equals Work-reported 177,396', cells == 177396, f'actual {cells}')
oldcases = {r['case'] for r in old}
chkb('E06', 'E', 'old expansion output has 46 cases (14 legacy + 32 added), new = 33', len(oldcases) == 46 and len(cases) - len(oldcases) == 33, f'old={len(oldcases)} new={len(cases) - len(oldcases)}')
tot = bad2 = 0
for name in ['N3_Policy_Accounts.csv', 'N3_Pension_Accounts.csv', 'N3_Income_Distribution.csv', 'N3_Corporate_Accounts.csv', 'N3_Structural_Interfaces.csv', 'N3_VAT_Regular_Quantity.csv']:
    o = rd(ROOT / 'handoff/chatgpt-n3-model-expansion-20261121' / name)
    nw = [r for r in rd(R / name) if r['case'] in oldcases]
    if len(o) != len(nw):
        bad2 += 1
        continue
    for a, b in zip(o, nw):
        for k, v in a.items():
            if v == '':
                continue
            try:
                x = float(v)
            except ValueError:
                if v != b[k]:
                    bad2 += 1
                continue
            tot += 1
            if not math.isclose(x, float(b[k]), rel_tol=3e-9, abs_tol=5e-7):
                bad2 += 1
chk('E07', 'E', f'old-46 component numeric cells checked={tot}; mismatches', 0, bad2, 0)
chkb('E08', 'E', 'component cell count equals Work-reported 271,964', tot == 271964, f'actual {tot}')
Fref = rd(T / 'F_Reference_Annual.csv')
Ff = [r for r in rd(ROOT / 'handoff/f-common-endoflife-finalization-20261121/Annual.csv') if r['case'] == 'LATEST_F']
chkb('E09', 'E', 'F_Reference_Annual has 30 rows equal in real_gdp/nominal_gdp to fixed ff621006 LATEST_F', len(Fref) == 30 == len(Ff) and all(abs(fl(a['real_gdp_trn']) - fl(b['real_gdp_trn'])) < 5e-7 and abs(fl(a['nominal_gdp_trn']) - fl(b['nominal_gdp_trn'])) < 5e-7 for a, b in zip(Fref, Ff)))
# Execution_Metadata label inconsistency (non-numeric)
chkb('E10', 'E', f'Execution_Metadata legacy_cases/new_cases = {meta["legacy_cases"]}/{meta["new_cases"]} vs README 46/33 (labels differ; total 79 equal)', meta['legacy_cases'] + meta['new_cases'] == 79, 'label-only inconsistency: 14 draft + 65 config cases = 79; old46/new33 split is Work-narrative')
# combined/interaction separation
IA = rd(T / 'Interactions.csv')
chkb('E11', 'E', 'Interactions.csv marks attribution=False for all rows (no causal ranking)', all(r['attribution'] == 'False' for r in IA))
dd = 0.0
for r in IA:
    if r.get('difference_in_differences') not in (None, ''):
        dd = max(dd, abs(fl(r['combined_minus_base']) - fl(r['a_minus_base']) - fl(r['b_minus_base']) - fl(r['difference_in_differences'])))
chk('E12', 'E', 'interaction = combined - a - b (vs base) identity (single/combined/interaction separated)', 0.0, dd, 5e-7)

# ---------------------------------------------------------------- write
fails = [c for c in checks if c['verdict'] == 'FAIL']
with open(OUT / 'SPE_N3_Gap_Independent_Numeric_Comparison_DRAFT_20261121.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(checks[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(checks)
summary = dict(total=len(checks), pass_=len(checks) - len(fails), fail=len(fails), by_area={a: dict(total=sum(1 for c in checks if c['area'] == a), fail=sum(1 for c in fails if c['area'] == a)) for a in 'ABCDE'}, failed_ids=[c['id'] for c in fails],
               old46_annual_cells=cells, old46_component_cells=tot, rows_2370=len(A), vat_hh_market_year_rows=nq, financing_rows=len(B))
(OUT / 'SPE_N3_Gap_Independent_Summary_DRAFT_20261121.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False) + '\n')
print(json.dumps(summary, indent=1, ensure_ascii=False))
for c in fails:
    print('FAIL', c['id'], c['description'], c['expected'], c['actual'], c['abs_diff'])
