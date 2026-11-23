#!/usr/bin/env python3
# Independent recalculation of the SQ / F / N3 three-scenario package (fixed commit e981c924).
# Own formulas; does NOT import the Work scripts. Reads the delivered packet, the fixed repo checkout (for earlier fixed outputs),
# and my own re-run output directory (for reproducibility cross-checks).
# Usage: python3 -I <this> TARGET_DIR RERUN_DIR ROOT OUTDIR
import sys, os, json, csv, math, hashlib, subprocess
T, RR, ROOT, OUT = [os.path.abspath(a) for a in sys.argv[1:5]]; os.makedirs(OUT, exist_ok=True)
PIN = '9448e5921dba0fc0ff4e294e52b6b1f3ba862330'
J = lambda *p: json.load(open(os.path.join(*p)))
def R(*p): return list(csv.DictReader(open(os.path.join(*p))))
class Acc:
    def __init__(s): s.rows = {}; s.order = []
    def add(s, cid, desc, resid=0.0, ok=True, note='', tol=None):
        r = s.rows.setdefault(cid, dict(id=cid, desc=desc, items=0, failures=0, max_abs_residual=0.0, note='', first_failure=''))
        if cid not in s.order: s.order.append(cid)
        r['items'] += 1
        bad = (not ok) or (resid is None) or (isinstance(resid, float) and (math.isnan(resid) or (tol is not None and abs(resid) > tol)))
        if resid is not None and isinstance(resid, (int, float)) and not math.isnan(resid): r['max_abs_residual'] = max(r['max_abs_residual'], abs(resid))
        if bad:
            r['failures'] += 1
            if not r['first_failure']: r['first_failure'] = '%s resid=%r' % (note, resid)
        elif note and not r['note']: r['note'] = note
    def num(s, cid, desc, a, b, tol=1e-9, rel=1e-11, note=''):
        d = abs(a - b); s.add(cid, desc, d, ok=d <= tol + rel * max(abs(a), abs(b)), note=note, tol=None)
A = Acc()
Y = list(range(2026, 2056))
# ------------------------------------------------------------------ load
sqt = J(T, 'BASE_REPLAY/Common_Trace_BASE_REPLAY.json'); P = sqt['parameters']; Q = sqt['years']
ft = J(T, 'F/F_Runtime_Trace.json'); FY = ft['years']; FP = ft['parameters']
fa = J(T, 'F/F_Actual_Annual.json'); fo = J(T, 'F_OLD/F_Actual_Annual.json')
fref = J(T, 'F/F_Medical_Reference_Inputs.json'); foref = J(T, 'F_OLD/F_Medical_Reference_Inputs.json')
n3 = J(T, 'N3/N3_Actual_Annual.json'); n3c = J(T, 'N3/N3_Common_Input_Contract.json'); n3sq = J(T, 'N3/N3_SQ_Denominator_States.json')
ann = R(T, 'SPE_Three_Scenario_Annual_Comparison_2026_2055.csv'); key = R(T, 'SPE_Three_Scenario_Key_Years_And_Gaps.csv'); att = R(T, 'SPE_Three_Scenario_Change_Attribution.csv')
sqcsv = R(T, 'SQ_Baseline_2026_2055.csv'); trc = R(T, 'SQ_Price_Event_Parameter_Trace.csv'); chg = R(T, 'SQ_Change_Candidates_And_Impact.csv'); comp = R(T, 'F_N3_SQ_Common_Condition_Compatibility.csv')
defs = J(T, 'SPE_Three_Scenario_Case_Definitions.json')
by = lambda c: {int(x['year']): x for x in ann if x['case'] == c}
S, Fc, N = by('SQ'), by('F'), by('N3')
# ------------------------------------------------------------------ A: custody of source receipts against the fixed Git objects (own computation)
def gshow(path, commit=PIN):
    return subprocess.check_output(['git', '-C', ROOT, 'show', commit + ':' + path])
rec = J(T, 'Fixed_Source_Receipts.json')
for x in rec['files']:
    try:
        b = gshow(x['path']); A.add('A01', 'Fixed_Source_Receipts: size and SHA-256 equal the actual bytes of fixed commit 9448e592', 0.0, ok=(len(b) == x['size'] and hashlib.sha256(b).hexdigest() == x['sha256']), note=x['path'])
    except Exception as e: A.add('A01', 'receipt source retrievable', None, ok=False, note=x['path'] + str(e)[:60])
for x in J(T, 'Fixed_Original_Policy_Receipts.json'):
    b = gshow(x['path'], x['commit']); sv = open(os.path.join(T, x['saved']), 'rb').read()
    A.add('A02', 'Fixed_Originals saved copy = fixed-commit bytes = receipt (size and SHA-256)', 0.0, ok=(b == sv and len(b) == x['size'] and hashlib.sha256(b).hexdigest() == x['sha256']), note=x['path'])
for pth in ('policies/StatusQuo.md', 'policies/FreedomPolicies.md', 'policies/FreedomPolicies_Annex.md', 'policies/New3linesPolicies.md'):
    A.add('A03', 'policy originals in the output commit tree are byte-identical to those at the input commit', 0.0, ok=open(os.path.join(ROOT, pth), 'rb').read() == gshow(pth), note=pth)
# my own re-run vs delivered (reproducibility)
nrep = 0
for r, _, fs in os.walk(RR):
    for f in fs:
        p = os.path.relpath(os.path.join(r, f), RR); q = os.path.join(T, p)
        if os.path.exists(q):
            nrep += 1; A.add('A04', 'my re-run output is byte-identical to the delivered file', 0.0, ok=open(q, 'rb').read() == open(os.path.join(r, f), 'rb').read(), note=p)
A.add('A05', 'number of re-run files compared (expected 57)', 0.0, ok=(nrep == 57), note=str(nrep))
# ------------------------------------------------------------------ B: SQ core from my own formulas
risk_loss = dict(oil=P['oil_gdp_loss'], conflict=P['conflict_gdp_loss'], quake=P['quake_gdp_loss'], disaster=P['disaster_gdp_loss'], climate=P['climate_gdp_loss'])
def calendar(y):
    ev = dict(oil=0., conflict=risk_loss['conflict'] if y == 2027 else 0., quake=risk_loss['quake'] if y == 2031 else 0.,
              disaster=risk_loss['disaster'] if (y >= P['disaster_anchor'] and (y - P['disaster_anchor']) % 3 == 0) else 0.,
              climate=risk_loss['climate'] if (y >= P['climate_anchor'] and (y - P['climate_anchor']) % 2 == 0) else 0.)
    return ev
A.add('B00', 'initial-year oil shock is not applied (apply_oil_to_initial False) and the 2026 row is the initial state with no transition', 0.0, ok=(P['apply_oil_to_initial'] is False and Q[0]['year'] == 2026 and len(Q) == 30))
def core_series(labor, infl, risk):
    nl = 1.; yc = [580.]; nc = [600.]
    for i in range(1, 30):
        nl *= 1 + P['base_growth'] - risk[i]
        yc.append(580. * nl * (labor[i] / labor[0]) ** P['labor_response'])
        nc.append(nc[-1] * (yc[-1] / yc[-2] + infl[i]))
    return yc, nc
sq_risk = [sum(calendar(y).values()) for y in Y]
sq_infl = [0.] + [P['base_inflation'] + (P['conflict_inflation_extra'] if y == 2027 else 0.) for y in Y[1:]]
sq_lab = [q['labor'] for q in Q]
myY, myN = core_series(sq_lab, sq_infl, sq_risk)
for i, y in enumerate(Y):
    q = Q[i]
    A.num('B01', 'SQ applied risk (own event calendar from fixed parameters) = trace risk, each event applied once', sum(calendar(y).values()), q['risk'] if i else 0.)
    A.num('B02', 'SQ real core output coreY = 580 * nonlabor factor * (L/L2026)^0.65', myY[i], q['coreY'])
    A.num('B03', 'SQ core nominal recursion coreN_t = coreN_(t-1)*(1+g_t+pi_t)', myN[i], q['coreN'])
    A.num('B04', 'SQ implementation index d = coreN/coreY', myN[i] / myY[i], q['coreD'])
    A.num('B05', 'SQ final nominal N = Y*d*(1+pressure), pressure = 0.5*unmet/coreY', q['Y'] * q['coreD'] * (1 + P['price_pressure_coefficient'] * q['unmet'] / q['coreY']), q['N'])
    A.num('B06', 'SQ Y = desired - unmet (capacity rule)', q['desired'] - q['unmet'], q['Y'])
    A.add('B07', 'SQ price pressure is 0 in every year (no binding capacity)', q['pressure'], ok=(q['pressure'] == 0 and q['unmet'] == 0), tol=0)
    A.num('B08', 'SQ trace input inflation pi = base 2% (+ conflict 5% in 2027)', sq_infl[i], q['inflation'] if i else 0.)
    if i:
        g = myY[i] / myY[i - 1] - 1
        A.num('B09', 'implicit deflator growth = pi/(1+g) under the additive nominal rule', myN[i] / myY[i] / (myN[i - 1] / myY[i - 1]) - 1, sq_infl[i] / (1 + g))
    c = S[y]
    A.num('B10', 'delivered SQ CSV real GDP = trace Y', float(c['real_GDP_trn']), q['Y']); A.num('B11', 'delivered SQ CSV nominal GDP = trace N', float(c['nominal_GDP_trn']), q['N'])
    A.num('B12', 'delivered implementation_price_index = d, implicit deflator = N/Y, normalized by 600/580', float(c['implementation_price_index']) + float(c['implicit_deflator']) + float(c['implicit_deflator_normalized']), q['coreD'] + q['N'] / q['Y'] + q['N'] / q['Y'] / (600 / 580))
    A.num('B13', 'delivered SQ population and effective labor = trace', float(c['population']) + float(c['effective_labor_proxy']), q['population'] + q['labor'])
A.num('B14', '2026 initial row: real 580, nominal 600, implementation index 600/580', S[2026]['real_GDP_trn'] and float(S[2026]['real_GDP_trn']) + float(S[2026]['nominal_GDP_trn']), 1180.)
A.add('B15', '29 transitions: 2027..2055 each with growth defined, 2026 growth 0', 0.0, ok=(float(S[2026]['real_growth_pct']) == 0 and all(float(S[y]['real_growth_pct']) != 0 for y in Y[1:])))
for y in Y[1:]:
    A.num('B16', 'delivered real_growth_pct = (Y_t/Y_(t-1)-1)*100', float(S[y]['real_growth_pct']), (float(S[y]['real_GDP_trn']) / float(S[y - 1]['real_GDP_trn']) - 1) * 100, tol=1e-9)
for i, y in enumerate(Y):
    q = Q[i]; A.num('B22', 'SQ GDP decomposition: desired = coreY + 0.5*supply + C + I + education/d + education level + finite + services/d', q['coreY'] + 0.5 * q['supply'] + q['C'] + q['I'] + q['education_nom'] / q['coreD'] + q['education_level'] + q['finite'] + q['service_nominal'] / q['coreD'], q['desired'])
# nonlabor factor 2055 and cumulative one-time application, scheduled vs applied columns
for x in trc:
    y = int(x['year']); ev = json.loads(x['scheduled_events']); mine = calendar(y); mine['oil'] = risk_loss['oil'] if y == 2026 else 0.
    A.add('B17', 'scheduled_events column = my calendar (oil scheduled 2026 only)', 0.0, ok=all(abs(ev[k] - mine[k]) < 1e-15 for k in mine), note=str(y))
    A.num('B18', 'applied_risk column = sum of non-oil events', float(x['applied_risk']), sum(v for k, v in mine.items() if k != 'oil'))
    A.add('B19', 'oil: scheduled in 2026 but never applied; initial_transition flag False only in 2026', 0.0, ok=((x['oil_applied'] == 'False') and (x['oil_scheduled'] == 'True') == (y == 2026) and (x['initial_transition'] == 'False') == (y == 2026)))
    A.add('B20', 'recovery rule is UNKNOWN_NOT_ADDED and the loss state is permanent (flag)', 0.0, ok=(x['recovery_rule'] == 'UNKNOWN_NOT_ADDED' and x['permanent_state'] == 'True'))
cum_nl = 1.
for y in Y[1:]: cum_nl *= 1 + P['base_growth'] - sum(calendar(y).values())
A.add('B21', 'permanent loss: with no recovery term the cumulative nonlabor factor ends at (my product)', 0.0, ok=True, note='nonlabor factor 2055 = %.6f (events: 2027 conflict, 2031 quake, disaster 2029.. every 3y, climate 2028.. every 2y)' % cum_nl)
# ------------------------------------------------------------------ C: price-key variants (own recompute of nominal path)
for mode in ('KEYS_DEFAULT', 'KEY_BASE_NONDEFAULT', 'KEY_CONFLICT_NONDEFAULT', 'LEGACY_BASE_NONDEFAULT', 'LEGACY_CONFLICT_NONDEFAULT'):
    v = J(T, mode, 'Common_Trace_%s.json' % mode)['years']
    base = .03 if mode == 'KEY_BASE_NONDEFAULT' else P['base_inflation']
    conf = .01 if mode == 'KEY_CONFLICT_NONDEFAULT' else P['conflict_inflation_extra']
    if mode.startswith('LEGACY'): base = P['base_inflation']; conf = P['conflict_gdp_loss']      # legacy wiring ignores the keys
    infl = [0.] + [base + (conf if y == 2027 else 0.) for y in Y[1:]]
    # variant nominal core with the SAME real core (real core independent of price keys)
    nc = [600.]
    for i in range(1, 30): nc.append(nc[-1] * (myY[i] / myY[i - 1] + infl[i]))
    for i, y in enumerate(Y):
        A.num('C01:' + mode, 'variant nominal core from my formula with the expected input inflation = trace coreN', nc[i], v[i]['coreN'])
        A.num('C02:' + mode, 'variant real core and applied risk are identical to the reference (price keys independent of real loss)', v[i]['coreY'] - Q[i]['coreY'] + v[i]['risk'] - Q[i]['risk'], 0.0)
        A.num('C03:' + mode, 'variant N = Y*d (no price pressure)', v[i]['Y'] * v[i]['coreD'] * (1 + 0.5 * v[i]['unmet'] / v[i]['coreY']), v[i]['N'])
    dY = v[-1]['Y'] - Q[-1]['Y']; dN = v[-1]['N'] - Q[-1]['N']
    A.add('C04:' + mode, 'recorded 2055 differences vs reference (real, nominal)', 0.0, note='real %+.9f nominal %+.9f' % (dY, dN))
    r = [x for x in chg if x['case'] == mode and x['year'] == '2055'][0]
    A.num('C05:' + mode, 'delivered change-candidate CSV 2055 real/nominal difference = my difference', float(r['real_GDP_minus_reference']) + float(r['nominal_GDP_minus_reference']), dY + dN)
    if mode in ('KEYS_DEFAULT', 'LEGACY_BASE_NONDEFAULT', 'LEGACY_CONFLICT_NONDEFAULT'):
        A.add('C06:' + mode, 'default / legacy wiring leaves all 30-year states unchanged', max(abs(v[i]['Y'] - Q[i]['Y']) + abs(v[i]['N'] - Q[i]['N']) for i in range(30)), tol=1e-12)
mx = max(abs(J(T, 'KEY_BASE_NONDEFAULT/Common_Trace_KEY_BASE_NONDEFAULT.json')['years'][i]['Y'] - Q[i]['Y']) for i in range(30))
A.add('C07', 'non-default price keys: realised real GDP is NOT exactly unchanged (only core/risk are); max abs real GDP change over 30 years', 0.0, note='KEY_BASE max |dY| = %.3e trn (tiny demand-side coupling through the price level)' % mx)
# ------------------------------------------------------------------ D: F
shared = [k for k in P if k in FP]; diffk = [k for k in shared if P[k] != FP[k]]
A.add('D01', 'F runtime parameters: keys that differ from the SQ common parameters', 0.0, note='%d shared keys, differing: %s' % (len(shared), ','.join(diffk) or 'none'))
for k in ('base_inflation', 'oil_inflation_extra', 'conflict_inflation_extra', 'apply_oil_to_initial', 'disaster_anchor', 'climate_anchor', 'base_growth', 'labor_response', 'oil_gdp_loss', 'conflict_gdp_loss', 'quake_gdp_loss', 'disaster_gdp_loss', 'climate_gdp_loss'):
    A.add('D02', 'F and SQ share the macro event/price/growth parameters exactly', 0.0, ok=(P[k] == FP[k]), note=k)
fl = [x['labor'] for x in FY]; fr = sq_risk; fi = sq_infl
fY, fN = core_series(fl, fi, fr)
for i, y in enumerate(Y):
    t = FY[i]
    A.num('D03', 'F applied risk = SQ calendar (same event once)', t['risk'], sq_risk[i] if i else 0.)
    A.num('D04', 'F input inflation = SQ input inflation', t['inflation'], sq_infl[i] if i else 0. if i == 0 else sq_infl[i]) if i else None
    A.num('D05', 'F real core from the same formula with F policy-endogenous labor', fY[i], t['coreY'])
    A.num('D06', 'F core nominal recursion', fN[i], t['coreN']); A.num('D07', 'F d = coreN/coreY', fN[i] / fY[i], t['coreD'])
    A.num('D08', 'F final nominal N = Y*d*(1+0.5*unmet/coreY)', t['Y'] * t['coreD'] * (1 + 0.5 * t['unmet'] / t['coreY']), t['N'])
    A.num('D09', 'F capacity rule Y = desired - unmet; capacity = 1.02*coreY + supply + education level', t['desired'] - t['unmet'], t['Y'])
    A.num('D09b', 'F GDP decomposition: desired = coreY + 0.5*supply + C + I + education/d + level + finite + services/d + domestic education service/d (F-specific term)', t['coreY'] + 0.5 * t['supply'] + t['C'] + t['I'] + t['education_nom'] / t['coreD'] + t['education_level'] + t['finite'] + fa[i]['service_production_nominal_delta_trn'] / t['coreD'] + fa[i]['education_service_domestic_nominal_trn'] / t['coreD'], t['desired'], tol=1e-9)
    A.num('D10', 'F capacity components', 1.02 * t['coreY'] + t['supply'] + t['education_level'], t['capacity'])
    a = fa[i]; c = Fc[y]
    A.num('D11', 'F_Actual_Annual real/nominal = runtime trace Y/N = delivered CSV', a['real_gdp_trn'] + a['nominal_gdp_trn'] - t['Y'] - t['N'] + float(c['real_GDP_trn']) - t['Y'] + float(c['nominal_GDP_trn']) - t['N'], 0.0)
    A.num('D12', 'F CSV population = F_Actual population; F labor proxy = trace labor', float(c['population']) - a['population'] + float(c['effective_labor_proxy']) - t['labor'], 0.0)
    if i:
        A.num('D13', 'F policy capital state recursion K_t = (1-0.05)*K_(t-1) + I_t (runtime trace)', t['K'], 0.95 * FY[i - 1]['K'] + t['I'])
    A.num('D13b', 'F delivered total real capital = 3.0*coreY + K policy state; I_policy column = trace I', a['capital_total_real_trn'] - 3.0 * t['coreY'] - t['K'] + a['I_policy_real_trn'] - t['I'], 0.0)
    A.num('D14', 'F-SQ real GDP difference column = F - SQ', float(c['GDP_minus_SQ_trn']), a['real_gdp_trn'] - Q[i]['Y'])
A.add('D15', 'F policy-endogenous labor/population differ from SQ (as intended): max |labor diff| (persons) and population diff 2055', 0.0, note='labor %.0f; population %.0f' % (max(abs(fl[i] - sq_lab[i]) for i in range(30)), fa[-1]['population'] - Q[-1]['population']))
# medical reference connection
ndef = n3c['medical_input']['deflators']
for i in range(30):
    A.num('D16', 'F aligned medical-reference deflators = N3 medical-initialisation deflators = SQ trace medical_input_deflator (shared SQ reference)', fref['deflators'][i] - ndef[i] + ndef[i] - Q[i]['medical_input_deflator'], 0.0, tol=2e-10)
    A.num('D17', 'F aligned medical-reference population = N3 = SQ population', fref['population'][i] - n3c['medical_input']['population'][i] + fref['population'][i] - Q[i]['population'], 0.0, tol=1e-3)
    A.num('D18', 'F_OLD education deflators = F education deflators (education keeps its own price input)', foref['education_deflators'][i] - fref['education_deflators'][i], 0.0)
A.add('D19', 'F_OLD medical reference is the old F deflator, different from SQ: max |old - SQ| deflator', 0.0, note='%.3e (aligned F: %.1e)' % (max(abs(foref['deflators'][i] - Q[i]['medical_input_deflator']) for i in range(30)), max(abs(fref['deflators'][i] - Q[i]['medical_input_deflator']) for i in range(30))))
oldF = {int(x['year']): x for x in R(ROOT, 'handoff/f-common-endoflife-finalization-20261121/Annual.csv') if x['case'] == 'LATEST_F'}
for i, y in enumerate(Y):
    A.num('D20', 'F_OLD re-execution reproduces the earlier fixed LATEST_F (f-common-endoflife-finalization) real GDP', fo[i]['real_gdp_trn'], float(oldF[y]['real_gdp_trn']), tol=3e-6)
    A.num('D21', 'F reconnection effect column = F(aligned) - F_OLD', float(att[i]['F_shared_medical_reference_reconnection']), fa[i]['real_gdp_trn'] - fo[i]['real_gdp_trn'])
    A.num('D22', 'F policy gap on shared SQ = F(aligned) - SQ(common ON)', float(att[i]['F_policy_gap_on_shared_reference']), fa[i]['real_gdp_trn'] - Q[i]['Y'])
    A.num('D23', 'F_old_own_SQ_FIXED column equals the earlier fixed f-education SQ_FIXED', float(att[i]['F_old_own_SQ_FIXED_denominator']), float([x for x in R(ROOT, 'handoff/f-education-20261121/Annual.csv') if x['case'] == 'SQ_FIXED' and int(x['year']) == y][0]['real_gdp_trn']))
A.add('D24', 'reconnection effect: max |F aligned - F_OLD| and 2055 value (trn)', 0.0, note='max %.3e; 2055 %+.3e' % (max(abs(fa[i]['real_gdp_trn'] - fo[i]['real_gdp_trn']) for i in range(30)), fa[-1]['real_gdp_trn'] - fo[-1]['real_gdp_trn']))
A.add('D25', 'SQ_FIXED(old denominator) vs SQ_COMMON_ON(new denominator) 2055 difference', 0.0, note='%+.6f trn' % (Q[-1]['Y'] - float(att[-1]['F_old_own_SQ_FIXED_denominator'])))
# ------------------------------------------------------------------ E: N3
npar = n3c['parameters']
for k in ('base_inflation', 'oil_inflation_extra', 'conflict_inflation_extra', 'apply_oil_to_initial', 'disaster_anchor', 'climate_anchor', 'base_growth', 'labor_response', 'oil_gdp_loss', 'conflict_gdp_loss', 'quake_gdp_loss', 'disaster_gdp_loss', 'climate_gdp_loss', 'price_pressure_coefficient'):
    A.add('E01', 'N3 and SQ share the macro event/price/growth parameters exactly', 0.0, ok=(P[k] == npar[k]), note=k)
for i, y in enumerate(Y):
    s = n3sq[i]; a = n3[i]; c = N[y]; q = Q[i]
    for k in ('coreY', 'coreN', 'coreD', 'Y', 'N', 'labor', 'C', 'I', 'K', 'tax'):
        A.num('E02', 'N3 fixed SQ denominator state = SQ trace (core/Y/N/labor/C/I/K/tax), two separate executions', s[k], q[k], tol=2e-9)
    A.num('E03', 'N3 SQ-denominator coreY from my formula', myY[i], s['coreY']); A.num('E04', 'N3 SQ-denominator coreN from my formula', myN[i], s['coreN'])
    A.num('E05', 'N3 SQ real GDP column = SQ Y', a['SQ_real_GDP_trn'], q['Y'])
    A.num('E06', 'N3 GDP_minus_SQ = N3 - SQ', a['GDP_minus_SQ_trn'], a['real_GDP_trn'] - q['Y'])
    dec = sum(a[k] for k in ('GDP_core_difference_trn', 'GDP_C_difference_trn', 'GDP_I_difference_trn', 'GDP_G_domestic_trn', 'GDP_supply_difference_trn', 'GDP_other_difference_trn', 'GDP_unmet_difference_trn'))
    A.num('E07', 'N3 GDP difference decomposition (core+C+I+G+supply+other+unmet) closes', dec, a['GDP_minus_SQ_trn'], tol=2e-9)
    A.num('E08', 'N3 core difference is exactly 0 (policy does not alter core, population or labor)', a['GDP_core_difference_trn'], 0.0, tol=1e-9)
    A.num('E09', 'N3 final nominal N = Y*d_SQ*(1+0.5*unmet/coreY_SQ)', a['real_GDP_trn'] * q['coreD'] * (1 + 0.5 * a['unmet_demand_real_trn'] / q['coreY']), a['nominal_GDP_trn'])
    A.num('E10', 'N3 government purchase and public investment are zero (G/I OFF)', a['government_purchase_nominal_trn'] + a['public_investment_nominal_trn'], 0.0)
    A.num('E11', 'N3 delivered CSV = N3_Actual_Annual', float(c['real_GDP_trn']) - a['real_GDP_trn'] + float(c['nominal_GDP_trn']) - a['nominal_GDP_trn'], 0.0)
    A.num('E12', 'N3 CSV population/labor equal SQ (policy does not alter them)', float(c['population']) - q['population'] + float(c['effective_labor_proxy']) - q['labor'], 0.0)
ex = [a['extra_private_investment_real_trn'] for a in n3]; ep = [a['extra_public_investment_real_trn'] for a in n3]
A.add('E16', 'N3 line: G purchases and public investment are zero in all years (G/I OFF); tax-delta and pension-contribution blocks are ON (not zero)', 0.0, ok=(max(abs(a['government_purchase_nominal_trn']) + abs(a['public_investment_nominal_trn']) + abs(a['extra_public_investment_real_trn']) for a in n3) == 0 and max(abs(a['policy_tax_delta_trn']) for a in n3) > 1 and max(abs(a['pension_contribution_trn']) for a in n3) > 1))
A.add('E17', 'N3 line: extra PRIVATE investment (existing retained-earnings reinvestment) is nonzero, i.e. "extra G/I OFF" means G and public investment only', 0.0, note='max extra_private_investment_real_trn = %.3f trn/yr; 2055 = %.3f' % (max(ex), ex[-1]))
A.add('E18', 'N3 line: no new employment assumption (existing_public_added_jobs = 0 all years)', 0.0, ok=all(a['existing_public_added_jobs'] == 0 for a in n3))
oldn = {int(x['year']): x for x in R(ROOT, 'handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/N3_GDP_Gap_Counterfactual_Annual_2026_2055.csv') if x['case'] == 'BASE_REPLAY'}
for i, y in enumerate(Y): A.num('E13', 'N3 re-execution reproduces the earlier fixed N3 BASE_REPLAY (gap attribution)', n3[i]['real_GDP_trn'], float(oldn[y]['real_GDP_trn']), tol=3e-6)
oq = J(ROOT, 'handoff/chatgpt-statusquo-common-macro-limited-diagnostic-20261123/Common_Trace_BASE_REPLAY.json')['years']
for i in range(30): A.num('E14', 'SQ re-execution reproduces the earlier fixed SQ diagnostic trace (Y,N,coreN)', Q[i]['Y'] - oq[i]['Y'] + Q[i]['N'] - oq[i]['N'] + Q[i]['coreN'] - oq[i]['coreN'], 0.0, tol=2e-6)
A.add('E15', 'attribution columns SQ_common_macro_change_real / N3_common_macro_change_real are constants 0 in the CSV (asserted, not computed); substantiated by E02/E08/E14', 0.0, ok=all(float(x['SQ_common_macro_change_real']) == 0 and float(x['N3_common_macro_change_real']) == 0 for x in att), note='constant columns')
# ------------------------------------------------------------------ F: compatibility CSV and shared conditions
fin = J(ROOT, 'handoff/f-common-endoflife-finalization-20261121/Inputs.json')
for k in ('common_parameters', 'common_financing', 'clinical_strata', 'registry_population_reference'):
    A.add('F01', 'F common medical definitions = N3 common medical definitions (own comparison of fixed Inputs.json with N3 contract)', 0.0, ok=(fin[k] == n3c['medical_input']['c'][k]), note=k)
A.add('F02', 'compatibility CSV rows are all verified=True; clinical/definition rows present', 0.0, ok=all(x['verified'] == 'True' for x in comp), note='%d rows' % len(comp))
shared3 = [k for k in P if k in npar]; d3 = [k for k in shared3 if P[k] != npar[k]]
A.add('F03', 'SQ vs N3 full parameter dictionaries: keys differing', 0.0, note='%d shared keys, differing: %s' % (len(shared3), ','.join(d3) or 'none'))
# ------------------------------------------------------------------ G: delivered comparison CSVs internal consistency, key years, ranks, N/A, case definitions
for c, D in (('F', Fc), ('N3', N)):
    for y in Y:
        x = D[y]
        A.num('G01', 'GDP_minus_SQ and nominal_GDP_minus_SQ columns = difference to SQ rows', float(x['GDP_minus_SQ_trn']) - (float(x['real_GDP_trn']) - float(S[y]['real_GDP_trn'])) + float(x['nominal_GDP_minus_SQ_trn']) - (float(x['nominal_GDP_trn']) - float(S[y]['nominal_GDP_trn'])), 0.0)
        A.num('G02', 'GDP_minus_2026_580 = real - 580', float(x['GDP_minus_2026_580_trn']), float(x['real_GDP_trn']) - 580.)
for c, D in (('SQ', S), ('F', Fc), ('N3', N)):
    for y in Y:
        x = D[y]; A.num('G03', 'implicit deflator = N/Y; normalized = (N/Y)/(600/580)', float(x['implicit_deflator']) - float(x['nominal_GDP_trn']) / float(x['real_GDP_trn']) + float(x['implicit_deflator_normalized']) - float(x['nominal_GDP_trn']) / float(x['real_GDP_trn']) / (600 / 580), 0.0)
        A.add('G04', 'non-comparable columns are N/A and no cross-scenario national fiscal rank', 0.0, ok=(x['cross_scenario_national_fiscal_rank'] == 'N/A' and x['household_comparability'].startswith('N/A') and x['fund_comparability'].startswith('N/A') and x['investment_comparability'].startswith('N/A')))
    A.add('G05', 'PB/debt conditional values are absent for SQ and F (not supplemented)', 0.0, ok=(c == 'N3' or all(D[y]['PB_conditional_trn'] == '' and D[y]['debt_conditional_trn'] == '' for y in Y)))
below = {c: sum(float(D[y]['GDP_minus_SQ_trn']) < -1e-7 for y in Y) for c, D in (('SQ', S), ('F', Fc), ('N3', N))}
below580 = {c: sum(float(D[y]['real_GDP_trn']) < 580 - 1e-7 for y in Y) for c, D in (('SQ', S), ('F', Fc), ('N3', N))}
for x in key:
    c, y = x['case'], int(x['year']); D = {'SQ': S, 'F': Fc, 'N3': N}[c]
    A.num('G06', 'key-year rows equal the annual rows', float(x['real_GDP_trn']) - float(D[y]['real_GDP_trn']) + float(x['nominal_GDP_trn']) - float(D[y]['nominal_GDP_trn']), 0.0)
    A.add('G07', 'SQ-below-years and below-initial-580 years counts = my counts', 0.0, ok=(int(x['SQ_below_years']) == below[c] and int(x['below_initial_580_years']) == below580[c]), note='%s %s' % (c, below[c]))
A.add('G08', 'key years are exactly 2026, 2030, 2035, 2039, 2055 for 3 cases (15 rows)', 0.0, ok=(sorted((x['case'], int(x['year'])) for x in key) == sorted((c, y) for c in ('SQ', 'F', 'N3') for y in (2026, 2030, 2035, 2039, 2055))))
A.add('G09', 'case definitions: 9 cases, main comparison SQ+F+N3, candidates not in the main line, G/I OFF, no recovery added, initial oil False', 0.0, ok=(len(defs['cases']) == 9 and defs['candidate_in_main'] is False and defs['extra_GI'] == 'OFF' and defs['recovery_added'] is False and defs['initial_oil'] is False and defs['policy_adoption'] is False and defs['shared_initial_real'] == 580 and defs['shared_initial_nominal'] == 600))
# report table values (re-derive from my own annual numbers)
rep = open(os.path.join(T, 'SPE_SQ_Baseline_And_Three_Scenario_Recalculation_Report_DRAFT_20261123.md'), encoding='utf-8').read()
for c, rows in (('SQ', S), ('F', Fc), ('N3', N)):
    line = [l for l in rep.split('\n') if l.startswith('|' + c + '|')][0].strip('|').split('|')
    mine = [rows[y]['real_GDP_trn'] for y in (2030, 2035, 2039, 2055)] + [rows[2055]['nominal_GDP_trn'], rows[2055]['GDP_minus_SQ_trn'], below[c]]
    for a, b in zip(line[1:], mine): A.num('G10', 'report headline table cell = my value from annual rows (6 decimals)', float(a), float(b), tol=6e-7)
# ------------------------------------------------------------------ H: deflator / real-nominal structure statements (observed, not judged)
d26 = float(S[2026]['implicit_deflator']); d55 = float(S[2055]['implicit_deflator']); n = 29
imp_cagr = (d55 / d26) ** (1 / n) - 1; pi_avg = sum(sq_infl[1:]) / n
A.add('H01', 'SQ implicit deflator CAGR 2026-55 vs average input inflation', 0.0, note='implicit %.4f%% vs mean input %.4f%%; nominal CAGR %.4f%%' % (imp_cagr * 100, pi_avg * 100, ((float(S[2055]['nominal_GDP_trn']) / 600) ** (1 / n) - 1) * 100))
for c, D in (('F', Fc), ('N3', N)):
    A.add('H02:' + c, 'implicit deflator 2055 differs from SQ (F: policy-endogenous labor; N3: final price pressure only)', 0.0, note='%s 2055 d=%.6f vs SQ %.6f' % (c, float(D[2055]['implicit_deflator']), d55))
lf = (sq_lab[-1] / sq_lab[0]) ** P['labor_response']
A.add('H03', 'SQ 2055 real core = 580 * nonlabor factor * labor factor (arithmetic split, not a causal diagnosis)', 0.0, note='nonlabor factor %.6f (base growth + permanent event losses), labor factor (L55/L26)^0.65 = %.6f [L55/L26 = %.4f] -> coreY %.3f' % (cum_nl, lf, sq_lab[-1] / sq_lab[0], 580 * cum_nl * lf))
# ------------------------------------------------------------------ write
rows = [A.rows[k] for k in A.order]
for r in rows: r['verdict'] = 'PASS' if r['failures'] == 0 else 'FAIL'
with open(os.path.join(OUT, 'Three_Scenario_Independent_Numeric_Comparison_DRAFT_20261123.csv'), 'w', newline='') as o:
    w = csv.DictWriter(o, ['id', 'desc', 'items', 'failures', 'max_abs_residual', 'verdict', 'note', 'first_failure'], lineterminator='\n'); w.writeheader(); w.writerows(rows)
tot = sum(r['items'] for r in rows); fail = sum(r['failures'] for r in rows)
sumj = dict(check_groups=len(rows), items=tot, failures=fail, groups_failed=[r['id'] for r in rows if r['failures']], below_SQ_years=below, below_initial_580_years=below580,
            real2055=dict(SQ=float(S[2055]['real_GDP_trn']), F=float(Fc[2055]['real_GDP_trn']), N3=float(N[2055]['real_GDP_trn'])), nominal2055=dict(SQ=float(S[2055]['nominal_GDP_trn']), F=float(Fc[2055]['nominal_GDP_trn']), N3=float(N[2055]['nominal_GDP_trn'])))
json.dump(sumj, open(os.path.join(OUT, 'Three_Scenario_Independent_Summary_DRAFT_20261123.json'), 'w'), indent=1)
print(json.dumps(sumj, indent=1))
for r in rows:
    if r['failures']: print('FAIL', r['id'], r['failures'], r['first_failure'][:160])
