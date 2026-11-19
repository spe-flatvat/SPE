# Supplementary checks (Claude) for the labour / foreign-worker comparison model, Commit 47deeee2...
# Usage: python3 -I <this> <tx_inputs.json> <old_tx.csv> <Inputs.json> <Annual.csv> <Summary.csv> <Report.md> <prior_Annual_d27b659f.csv>
import sys, json, csv, importlib.util, io, contextlib, itertools, os, collections, math
A_ = sys.argv[1:]; here = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('rc', os.path.join(here, 'SPE_LaborForeign_Independent_Recalc_DRAFT_20261119.py')); rc = importlib.util.module_from_spec(sp)
sv = sys.argv; sys.argv = ['x'] + A_[:5]
with contextlib.redirect_stdout(io.StringIO()): sp.loader.exec_module(rc)
sys.argv = sv; eng = rc.eng; IN = rc.IN; YEARS = rc.YEARS
REPORT = open(A_[5], encoding='utf-8').read()
PRIOR = {(r['case'], int(r['year'])): r for r in csv.DictReader(open(A_[6], encoding='utf-8'))}
ANN = {(r['case'], int(r['year'])): r for r in rc.ANN}; SUMM = {r['case']: r for r in rc.SUM}
CASES = {s['id']: s for s in IN['cases']}
def pr(*a): print(*a)
R = {}; D = {}
for s in IN['cases']:
    r, d, q = rc.case(s); R[s['id']] = r; D[s['id']] = d
g = lambda c, y=2055, k='real_gdp_trn': R[c][y][k]

# A1 vs_previous columns vs exact prior (d27b659f) Annual
bad = 0; mx = 0.
for s in IN['cases']:
    oc = ('SQ_LATEST' if s['mode'] == 'LATEST' else 'SQ_IPSS' if s['mode'] == 'IPSS' else 'SQ_COMMON') if s['policy'] == 'SQ' else ('F_COMMON_LATEST' if s['mode'] == 'LATEST' else 'F_IPSS' if s['mode'] == 'IPSS' else 'F_' + s['mode'] if s['mode'].startswith('STOCK') else 'F_BAND' + str(int(s.get('band_target', .04) * 100)) if s['mode'] == 'BAND' else 'F_SAME_FLOW')
    for y in YEARS:
        o = PRIOR[(oc, y)]; c = ANN[(s['id'], y)]
        for k, v in (('delta_GDP_vs_previous', R[s['id']][y]['real_gdp_trn'] - float(o['real_gdp_trn'])), ('delta_population_vs_previous', D[s['id']][y - 2026]['population'] - float(o['population'])), ('delta_tax_vs_previous', R[s['id']][y]['tax_diagnostic_trn'] - float(o['tax_diagnostic_trn']))):
            e = abs(v - float(c[k])); tol = 0.01 if 'population' in k else 1e-6; mx = max(mx, e / tol); bad += e > tol   # embedded/CSV values carry 10-11 significant digits (1e8-scale populations resolve to ~0.003 persons)
pr('A1 vs_previous columns vs exact prior d27b659f Annual (tolerance: 1e-6兆円 / 0.01人 for 10-11 digit storage): mismatches', bad, 'max |diff|/tol %.2f' % mx)
# A2 OLD stage reproduces the prior model
dd = max(abs(g(a, y) - float(PRIOR[(b, y)]['real_gdp_trn'])) for a, b in (('OLD_SQ', 'SQ_COMMON'), ('OLD_F', 'F_SAME_FLOW'), ('OLD_F400', 'F_STOCK400')) for y in YEARS)
pr('A2 OLD stage vs prior model real GDP, max abs diff (兆円): %.2e' % dd)
# A3 Report.md lines
f = lambda x, n=3: f'{x:,.{n}f}'; miss = []; chk = 0
def need(l):
    global chk; chk += 1
    if l not in REPORT: miss.append(l)
def S(c, k): return float(SUMM[c][k])
for pol in ('SQ', 'F'):
    o, n = 'OLD_' + pol, 'DOM_' + pol; need('|' + pol + '|' + '|'.join([f(S(o, 'real_gdp_trn')), f(S(n, 'real_gdp_trn')), f(S(n, 'real_gdp_trn') - S(o, 'real_gdp_trn')), f(S(o, 'domestic_employed') / 1e4), f(S(n, 'domestic_employed') / 1e4)]) + '|')
for n in ['POLICY_HIST_SQ', 'POLICY_HIST_F', 'POLICY_LATEST_SQ', 'POLICY_LATEST_F', 'POLICY_IPSS_SQ', 'POLICY_IPSS_F', 'F_STOCK300', 'F_STOCK350', 'F_STOCK400', 'F_BAND3', 'F_BAND4', 'F_BAND5']:
    l = rc.ledger(CASES[n]); lab, _ = rc.labour(CASES[n], l); last = lab[-1]
    sqr, _, _ = rc.case({**CASES[n], 'id': 'm', 'policy': 'SQ', 'mode': rc.sqmode(CASES[n])}); dlt = g(n) - sqr[2055]['real_gdp_trn'] if CASES[n]['policy'] == 'F' else 0.
    need('|' + n + '|' + '|'.join([f(last['population'] / 1e4), f(last['foreign'] / 1e4), f(last['population_ratio'] * 100) + '%', f(last['domestic_employed'] / 1e4), f(last['foreign_employed'] / 1e4), f(g(n)), f(g(n, 2055, 'tax_diagnostic_trn')), f(dlt)]) + '|')
for st in ('OLD', 'DOM', 'FOREIGN', 'VA'): need('|' + st + '|' + f(g(st + '_SQ')) + '|' + f(g(st + '_F')) + '|')
for y in (2030, 2035, 2038, 2045, 2055): need('|' + str(y) + '|' + '|'.join(f(g(n, y)) for n in ['POLICY_HIST_SQ', 'POLICY_HIST_F', 'F_STOCK400', 'F_BAND4']) + '|')
pr('A3 Report.md lines checked', chk, 'not found', len(miss)); [pr('  MISSING', m[:120]) for m in miss[:5]]

# B  labour: why domestic employment rises while GDP falls (DOM vs OLD)
def L(c, y): return D[c][y - 2026]['effective_productive_workers']
for pol in ('SQ',):
    o, n = 'OLD_' + pol, 'DOM_' + pol
    pr('B effective workers 2026/2055 (万人): OLD %.1f/%.1f (ratio %.4f) | DOM %.1f/%.1f (ratio %.4f)' % (L(o, 2026) / 1e4, L(o, 2055) / 1e4, L(o, 2055) / L(o, 2026), L(n, 2026) / 1e4, L(n, 2055) / 1e4, L(n, 2055) / L(n, 2026)))
    pr('B domestic employed 2026/2055 (万人): OLD %.1f/%.1f | DOM %.1f/%.1f ; GDP 2055 OLD %.3f DOM %.3f (diff %.3f)' % (D[o][0]['domestic_employed'] / 1e4, D[o][-1]['domestic_employed'] / 1e4, D[n][0]['domestic_employed'] / 1e4, D[n][-1]['domestic_employed'] / 1e4, g(o), g(n), g(n) - g(o)))
    pr('B GDP per effective worker 2026: OLD %.3f万円 DOM %.3f万円 (initial real GDP 580兆 fixed)' % (580e12 / L(o, 2026) / 1e4, 580e12 / L(n, 2026) / 1e4))
# counterfactual: DOM-stage labour path but re-based so the 2026 level equals OLD
import copy
def run_traj(s, labour_scale):
    d, q = rc.labour(s, rc.ledger(s)); cs = {**s, 'policy': 'SQ', 'mode': rc.sqmode(s)}; c, _ = rc.labour(cs, rc.ledger(cs))
    for t in d + c: t['effective_productive_workers'] *= labour_scale
    return rc.macro(s, d, c)
r0 = run_traj(CASES['DOM_SQ'], 1.0); r1 = run_traj(CASES['DOM_SQ'], 1.07)
pr('B scaling effective workers by a constant (all years) changes 2055 GDP by %.2e (GDP depends on labour growth, not level)' % (r1[2055]['real_gdp_trn'] - r0[2055]['real_gdp_trn']))
# decomposition: domestic employment path change vs initial-level re-anchoring
r = lambda x: x
# B2 older vs newer: domestic employment growth 2026->2055
for c in ('OLD_SQ', 'DOM_SQ', 'POLICY_HIST_SQ', 'POLICY_HIST_F'):
    d = D[c]; pr('B2', c, 'domestic employed 2026 %.1f -> 2055 %.1f (%.1f%%); foreign employed %.1f -> %.1f; effective workers %.1f -> %.1f (%.2f%%); GDP %.2f -> %.2f' % (d[0]['domestic_employed'] / 1e4, d[-1]['domestic_employed'] / 1e4, (d[-1]['domestic_employed'] / d[0]['domestic_employed'] - 1) * 100, d[0]['foreign_employed'] / 1e4, d[-1]['foreign_employed'] / 1e4, d[0]['effective_productive_workers'] / 1e4, d[-1]['effective_productive_workers'] / 1e4, (d[-1]['effective_productive_workers'] / d[0]['effective_productive_workers'] - 1) * 100, g(c, 2026), g(c)))
# elderly (65+) employment in the calibration
def e65(s, y):
    r25 = rc.REF[2025]; df = rc.OBS['foreign'] - r25['foreign']; led = rc.ledger(s); t = led[y - 2026]; jp = rc.interp(rc.AJ, y); tot = rc.interp(rc.AA, y)
    return sum(v[sx] * rc.rate(a, sx) for a, v in jp.items() if a >= 65 for sx in (0, 1)) / 1e4, sum(v[sx] for a, v in jp.items() if a >= 65 for sx in (0, 1)) / 1e4
for y in (2026, 2040, 2055):
    a, b = e65(CASES['POLICY_HIST_SQ'], y); pr('B3 Japanese 65+ (unscaled interpolation) population %.0f万, employed %.0f万 (%.1f%%), year %d' % (b, a, a / b * 100, y))

# C  F elderly employment promotion (item 1)
ew = IN['base']['tx_inputs']['policy_inputs']['elderly_additional_workers']; sub = IN['base']['tx_inputs']['policy_inputs']['elderly_subsidy_per_worker_man']; pen = IN['base']['tx_inputs']['policy_inputs']['pension_relief_per_worker_man']
pr('C elderly module inputs (inherited TX policy_inputs): additional workers %.0f, subsidy %.1f万円/人, pension relief %.1f万円/人 (F text gives no number)' % (ew, sub, pen))
def macroF(s, omit_off=(), override=None, supply_cap=True, sq_name=None):
    d, q = rc.labour(s, rc.ledger(s)); cs = {**s, 'policy': 'SQ', 'mode': rc.sqmode(s)}; c, _ = rc.labour(cs, rc.ledger(cs))
    eng.cfg['common_model']['slack'] = s.get('slack', .02)
    spec = dict(id=s['id'], policy=s['policy'], profile='TEXT_ASSUMPTIONS', supply_cap=supply_cap, medical_mode=s.get('medical_mode', 'UNALLOCATED_COMPAT'), migration_override=dict(foreign_initial_stock=d[0]['foreign'], enforcement_mode='NONE_REFERENCE'), traj=d, sq_traj=c, policy_override=override or {})
    p, prof, m, F, omit = eng.params(spec); omit = list(omit) + list(omit_off)
    return eng.run(spec, prepared=(p, prof, m, F, omit))
H = CASES['POLICY_HIST_F']; HS = CASES['POLICY_HIST_SQ']
full = macroF(H); pr('C sanity: independent F rerun GDP2055 %.6f vs recompute %.6f' % (full[2055]['real_gdp_trn'], g('POLICY_HIST_F')))
for n in (0., ew, 2 * ew, 5 * ew):
    r = macroF(H, override={'elderly_additional_workers': n}); pr('C elderly workers=%.0f: GDP2055 %.3f (vs F as built %+.3f), expenditure2055 %.3f, funding gap2055 %.3f' % (n, r[2055]['real_gdp_trn'], r[2055]['real_gdp_trn'] - full[2055]['real_gdp_trn'], r[2055]['expenditure_diagnostic_trn'], r[2055]['funding_gap_proxy_trn']))
r = macroF(H, override={'elderly_additional_workers': ew, 'elderly_subsidy_per_worker_man': 0., 'pension_relief_per_worker_man': 0.}); pr('C subsidy+pension relief set to 0: expenditure2055 %.4f vs %.4f (diff %.4f兆円/yr), GDP diff %.4f' % (r[2055]['expenditure_diagnostic_trn'], full[2055]['expenditure_diagnostic_trn'], full[2055]['expenditure_diagnostic_trn'] - r[2055]['expenditure_diagnostic_trn'], full[2055]['real_gdp_trn'] - r[2055]['real_gdp_trn']))
pr('C reported domestic_employed F vs SQ 2055 identical:', ANN[('POLICY_HIST_F', 2055)]['domestic_employed'] == ANN[('POLICY_HIST_SQ', 2055)]['domestic_employed'], '| elderly add-on enters effective workers only (%d workers = %.2f%% of domestic employed)' % (ew, ew / D['POLICY_HIST_F'][-1]['domestic_employed'] * 100))
# 65+ employed number and what a rate change would mean
a, b = e65(HS, 2055); pr('C 2055 Japanese 65+ population %.0f万, employed %.0f万; +1pp employment rate of 65+ = %.1f万人 workers' % (b, a, b / 100))

# D  F-SQ decomposition into channels (exact Shapley over 8 channels) for POLICY_HIST_F 2055
CH = collections.OrderedDict([('ELDER', dict(override={'elderly_additional_workers': 0.})), ('EDU', dict(override={'education_program_budget': 0., 'scholarship_spend': 0.})), ('ADMIN', dict(override={'invoice_cost_saving': 0., 'stamp_tax_removed': 0., 'digital_system_cost': 0.})),
                              ('FIRM', dict(omit=['firm'])), ('SOCIAL', dict(omit=['social'])), ('MEDICAL', dict(omit=['medical', 'hubs'])), ('EXTRA', dict(omit=['extra'])), ('TRIG', dict(omit=['triggers'])), ('FOOD', dict(omit=['food']))])
names = list(CH)
def val(on, key='real_gdp_trn', y=2055, s=H, cap=True):
    omit = []; ov = {}
    for n in names:
        if n not in on:
            omit += CH[n].get('omit', []); ov.update(CH[n].get('override', {}))
    return macroF(s, omit, ov, cap)[y][key]
cache = {}
def v(on, key='real_gdp_trn'):
    k = (frozenset(on), key)
    if k not in cache: cache[k] = val(on, key)
    return cache[k]
sq_gdp = g('POLICY_HIST_SQ'); core = v(set()); fullv = v(set(names))
pr('D F-SQ total %.3f = F-core (tax-rate path, sector VAT/credit, no extra channel) %.3f + channels %.3f ; F-all-on check %.3f' % (g('POLICY_HIST_F') - sq_gdp, core - sq_gdp, fullv - core, fullv - sq_gdp))
n = len(names); sh = {c: 0. for c in names}
for c in names:
    others = [x for x in names if x != c]
    for k in range(n):
        for sub_ in itertools.combinations(others, k):
            w = math.factorial(k) * math.factorial(n - k - 1) / math.factorial(n); sh[c] += w * (v(set(sub_) | {c}) - v(set(sub_)))
pr('D Shapley contribution to 2055 GDP (兆円): ' + ', '.join('%s %+.3f' % (c, sh[c]) for c in names), '| sum %.3f' % sum(sh.values()))
pr('D one-at-a-time from F-core: ' + ', '.join('%s %+.3f' % (c, v({c}) - core) for c in names))
pr('D leave-one-out from full F: ' + ', '.join('%s %+.3f' % (c, fullv - v(set(names) - {c})) for c in names))
inter = {}
for a_, b_ in itertools.combinations(names, 2): inter[(a_, b_)] = v({a_, b_}) - v({a_}) - v({b_}) + core
big = sorted(inter.items(), key=lambda kv: -abs(kv[1]))[:6]
pr('D largest pairwise interactions (from F-core): ' + ', '.join('%s×%s %+.3f' % (a_, b_, x) for (a_, b_), x in big))
pr('D total interaction beyond additive one-at-a-time: %.3f' % ((fullv - core) - sum(v({c}) - core for c in names)))
for key, lab in (('tax_diagnostic_trn', 'tax'), ('expenditure_diagnostic_trn', 'expenditure'), ('funding_gap_proxy_trn', 'funding gap')):
    shk = {c: 0. for c in names}
    for c in names:
        others = [x for x in names if x != c]
        for k in range(n):
            for sub_ in itertools.combinations(others, k):
                w = math.factorial(k) * math.factorial(n - k - 1) / math.factorial(n); shk[c] += w * (v(set(sub_) | {c}, key) - v(set(sub_), key))
    pr('D Shapley %s 2055: ' % lab + ', '.join('%s %+.2f' % (c, shk[c]) for c in names))

# E  supply cap / slack effect on F-SQ
for cap in (True, False):
    f_ = macroF(H, supply_cap=cap); s_ = macroF(HS, supply_cap=cap); pr('E supply_cap=%s: F-SQ 2055 %.3f (F %.3f, SQ %.3f)' % (cap, f_[2055]['real_gdp_trn'] - s_[2055]['real_gdp_trn'], f_[2055]['real_gdp_trn'], s_[2055]['real_gdp_trn']))
pr('E binding years (cap on) POLICY_HIST_F %d, POLICY_HIST_SQ %d, F_STOCK400 %d; unmet demand 2055 F %.2f' % (sum(r['supply_binding'] for r in R['POLICY_HIST_F'].values()), sum(r['supply_binding'] for r in R['POLICY_HIST_SQ'].values()), sum(r['supply_binding'] for r in R['F_STOCK400'].values()), R['POLICY_HIST_F'][2055]['unmet_demand_real']))
for c in ('SLACK5_SQ', 'SLACK5_F'): pr('E', c, 'GDP2055 %.3f' % g(c))
pr('E slack5 F-SQ (STOCK400 vs COMMON mixed pair, for reference) n/a; F_STOCK400 slack2 %.3f vs slack5 %.3f' % (g('F_STOCK400'), g('SLACK5_F')))

# F  foreign-worker assumptions
for a_, b_ in (('F_STOCK400', 'POLICY_HIST_F'), ('F_STOCK300', 'POLICY_HIST_F'), ('POLICY_HIST_SQ', 'POLICY_IPSS_SQ'), ('F_BAND4', 'POLICY_HIST_F')):
    dY = g(a_) - g(b_); dE = D[a_][-1]['foreign_employed'] - D[b_][-1]['foreign_employed']; dN = g(a_, 2055, 'nominal_gdp_trn') - g(b_, 2055, 'nominal_gdp_trn'); dAtt = ANN[(a_, 2055)]['foreign_VA_attribution_nominal_trn']
    att = float(ANN[(a_, 2055)]['foreign_VA_attribution_nominal_trn']) - float(ANN[(b_, 2055)]['foreign_VA_attribution_nominal_trn'])
    pr('F %s - %s 2055: dGDP %.3f兆, dForeignWorkers %.1f万, implied real GDP per extra foreign worker %.0f万円, dNominalGDP %.3f vs diagnostic VA attribution diff %.3f (ratio %.2f)' % (a_, b_, dY, dE / 1e4, dY * 1e12 / dE / 1e4, dN, att, dN / att))
for c in ('POLICY_HIST_F', 'F_STOCK400', 'POLICY_HIST_SQ'):
    d = D[c]; pr('F2', c, 'foreign employment fraction 2026 %.3f 2040 %.3f 2055 %.3f; foreign workers 2026 %.0f万 2055 %.0f万' % (d[0]['foreign_employed'] / d[0]['foreign'], d[14]['foreign_employed'] / d[14]['foreign'], d[-1]['foreign_employed'] / d[-1]['foreign'], d[0]['foreign_employed'] / 1e4, d[-1]['foreign_employed'] / 1e4))
pr('F3 initial level check: real GDP0 580兆/effective workers0 = %.2f万円; nominal GDP0 600兆/effective workers0 = %.2f万円; VA reference (SNA 2024) = %.2f万円; model nominal GDP0 600兆 vs SNA 2024 nominal %.1f兆' % (580e12 / D['POLICY_HIST_SQ'][0]['effective_productive_workers'] / 1e4, 600e12 / D['POLICY_HIST_SQ'][0]['effective_productive_workers'] / 1e4, rc.PAR['foreign_VA_per_employed_2026_yen'] / 1e4, IN['base']['reference_economic_data']['nominal_GDP_trn']))
pr('F4 VA weight q/dq: stage VA = %.3f ; stage OLD..FOREIGN = %.3f ; VA6 %.3f VA12 %.3f' % (rc.PAR['foreign_VA_per_employed_2026_yen'] / rc.PAR['domestic_VA_reference_2026_yen'], 8 / 9, 6e6 / rc.PAR['domestic_VA_reference_2026_yen'], 12e6 / rc.PAR['domestic_VA_reference_2026_yen']))
for c, b in (('VA6_F', 'F_STOCK400'), ('VA12_F', 'F_STOCK400'), ('VA6_SQ', 'POLICY_HIST_SQ'), ('VA12_SQ', 'POLICY_HIST_SQ'), ('EMP85_F', 'F_STOCK400'), ('EMP114_F', 'F_STOCK400'), ('EMP85_SQ', 'POLICY_HIST_SQ'), ('EMP114_SQ', 'POLICY_HIST_SQ')):
    pr('F5 %s GDP2055 %.3f (reference %s %.3f, diff %+.3f)' % (c, g(c), b, g(b), g(c) - g(b)))
for c in ('POLICY_HIST_F', 'POLICY_LATEST_F', 'POLICY_IPSS_F'):
    sqn = c.replace('_F', '_SQ'); pr('F6 %s-%s 2055: %.3f ; SQ level %.3f' % (c, sqn, g(c) - g(sqn), g(sqn)))
pr('F7 SQ future-inflow paths 2055 ratio/GDP: HIST %.2f%%/%.2f, LATEST %.2f%%/%.2f, IPSS %.2f%%/%.2f ; first year >5%%: ' % tuple(x for c in ('POLICY_HIST_SQ', 'POLICY_LATEST_SQ', 'POLICY_IPSS_SQ') for x in (D[c][-1]['population_ratio'] * 100, g(c))) + ', '.join('%s %s' % (c, next((t['year'] for t in D[c] if t['population_ratio'] > .05), None)) for c in ('POLICY_HIST_SQ', 'POLICY_LATEST_SQ', 'POLICY_IPSS_SQ')))

# G  interaction of the elderly add-on with the migration condition (should be ~additive)
for c in ('POLICY_HIST_F', 'F_STOCK400', 'F_BAND4', 'POLICY_IPSS_F'):
    a_ = macroF(CASES[c])[2055]['real_gdp_trn']; b_ = macroF(CASES[c], override={'elderly_additional_workers': 0.})[2055]['real_gdp_trn']
    pr('G elderly add-on effect under %s: %+.3f兆円 (2055)' % (c, a_ - b_))
# H  ramp: when does the elderly add-on enter, and labour-supply share
pr('H elderly add-on ramp (workers): ' + ', '.join('%d:%.0f' % (y, ew * eng.ramp(y, 2028)) for y in (2027, 2028, 2029, 2030, 2031)))
# I  channel inventory: F text items vs. engine channels with a numerical GDP/tax/expenditure path (labelled in the report)
pr('I foreign-package numerical effect columns in Annual.csv: identified_foreign_policy_GDP_effect non-blank cells =', sum(1 for r in ANN.values() if r['identified_foreign_policy_GDP_effect'] != ''), '; F_effective_admission_cap non-blank =', sum(1 for r in ANN.values() if r['F_effective_admission_cap'] != ''), '; F_N4_quantity_effect_identified non-blank =', sum(1 for r in ANN.values() if r['F_N4_quantity_effect_identified'] != ''))
