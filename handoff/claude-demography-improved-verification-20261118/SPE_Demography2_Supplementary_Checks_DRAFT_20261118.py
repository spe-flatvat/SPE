# Supplementary checks (Claude) for the improved demography model, Commit d27b659f...
# Usage: python3 -I <this> <tx_inputs.json> <old_tx.csv> <Inputs.json> <Annual.csv> <Summary.csv> <orig_TX_engine.py> <Report.md>
import sys, json, csv, importlib.util, collections, io, contextlib, copy, math
A_ = sys.argv[1:]
def load(name, path, argv):
    sv = sys.argv; sys.argv = argv; sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    with contextlib.redirect_stdout(io.StringIO()): sp.loader.exec_module(m)
    sys.argv = sv; return m
import os; here = os.path.dirname(os.path.abspath(__file__))
rc = load('rc', os.path.join(here, 'SPE_Demography2_Independent_Recalc_DRAFT_20261118.py'), ['x'] + A_[:5])
old = load('oldeng', A_[5], [A_[5], A_[0], A_[1]])
REPORT = open(A_[6], encoding='utf-8').read()
rows = rc.rows; by = collections.defaultdict(dict)
for r in rows: by[r['case']][r['year']] = r
ANN = {(r['case'], int(r['year'])): r for r in csv.DictReader(open(A_[3], encoding='utf-8'))}
CA = rc.CA; IN = rc.IN
def pr(*a): print(*a)

# A1 vs_old columns from exact old engine
oldp = {pol: old.run(dict(id='OLD_' + pol, policy=pol, profile='TEXT_ASSUMPTIONS', supply_cap=True)) for pol in ('SQ', 'F')}
bad = 0; mx = 0.
for r in rows:
    c = ANN[(r['case'], r['year'])]; o = oldp[c['policy']][r['year']]
    for k, v in (('delta_GDP_vs_old', r['real_gdp_trn'] - o['real_gdp_trn']), ('delta_population_vs_old', r['population'] - o['population_persons']), ('delta_tax_vs_old', r['tax_diagnostic_trn'] - o['tax_diagnostic_trn'])):
        e = abs(v - float(c[k])) / max(1., abs(v)); mx = max(mx, e); bad += e > 1e-9
SUMM = {r['case']: r for r in csv.DictReader(open(A_[4], encoding='utf-8'))}; sbad = 0
for cid, r in SUMM.items():
    v = by[cid][2055]['real_gdp_trn'] - oldp[next(x for x in IN['cases'] if x['id'] == cid)['policy']][2055]['real_gdp_trn']
    sbad += abs(v - float(r['delta_GDP_vs_old'])) / max(1., abs(v)) > 1e-9
pr('A1 Summary.csv delta_GDP_vs_old (46 cells) vs exact old engine: mismatches', sbad)
pr('A1 vs_old columns vs exact old engine: mismatches', bad, 'max_rel_err %.2e' % mx)

# A2 Report.md numbers vs my independent rows (formatted as the report formats them)
def f(x, n=3): return f'{x:,.{n}f}'
miss = []; chk = 0
def need(line):
    global chk; chk += 1
    if line not in REPORT: miss.append(line)
def first(case, fn): return next((y for y in range(2026, 2056) if fn(by[case][y])), None)
for n in ['SQ_COMMON', 'F_SAME_FLOW', 'F_STOCK300', 'F_STOCK350', 'F_STOCK400', 'F_NET400', 'F_BAND3', 'F_BAND4', 'F_BAND5', 'SQ_LATEST', 'SQ_IPSS', 'IPSS_EXACT_SQ']:
    l = by[n][2055]; y5 = first(n, lambda x: x['population_ratio'] > .05)
    need('|' + n + '|' + '|'.join([f(l['population'] / 1e4), f(l['foreign'] / 1e4), f(l['population_ratio'] * 100) + '%', f(l['foreign_employed_conditional'] / 1e4), f(l['real_gdp_trn']), f(l['tax_diagnostic_trn']), str(y5 or '2055までなし')]) + '|')
for y in (2030, 2035, 2038, 2045, 2055):
    s, ff, b = by['SQ_COMMON'][y], by['F_STOCK400'][y], by['F_BAND4'][y]
    need('|' + str(y) + '|' + f(s['population'] / 1e4) + '／' + f(ff['population'] / 1e4) + '|' + f(s['population_ratio'] * 100) + '／' + f(ff['population_ratio'] * 100) + '%|' + f(s['real_gdp_trn']) + '／' + f(ff['real_gdp_trn']) + '|' + f(s['tax_diagnostic_trn']) + '／' + f(ff['tax_diagnostic_trn']) + '|' + f(b['population_ratio'] * 100) + '%|')
for n in ['SQ_COMMON', 'F_SAME_FLOW', 'F_STOCK400', 'F_BAND4']:
    l = by[n][2055]; need('|' + n + '|' + f(l['delta_population_vs_old'] / 1e4) + '|' + f(l['delta_GDP_vs_old']) + '|' + f(l['delta_tax_vs_old']) + '|')
for n in ['SQ_COMMON', 'F_STOCK300', 'F_STOCK400', 'F_BAND4']:
    l = by[n][2055]; need('|' + n + '|' + f((l['population'] - l['ipss_population']) / 1e4) + '|' + f(l['initial_population_offset'] / 1e4) + '|' + f(l['migration_cumulative_difference'] / 1e4) + '|')
for n in ['F_STOCK300', 'F_STOCK350', 'F_STOCK400', 'F_BAND4']:
    l = by[n][2055]; need('|' + n + '|' + '|'.join(f(l[k]) for k in ['delta_GDP_vs_matched_SQ', 'F_nonmigration_GDP', 'F_migration_GDP']) + '|')
for n in ['SQ_COMMON', 'F_STOCK400', 'F_BAND4']:
    a = first(n, lambda x: x['legacy_resident_gdp5_reference'] > .05); b = first(n, lambda x: x['worker_va_gdp_ratio'] > .05)
    need('|' + n + '|' + str(a or 'なし') + '|' + str(b or 'なし') + '|')
for e in (.6, .7, .8):
    for q in (6, 8, 10, 12):
        n = 'F_STOCK400' if e == .7 and q == 8 else f'ECON_E{int(e*100)}_Q{q}_F400'; l = by[n][2055]
        need('|' + f(e, 1) + '|' + str(q * 100) + '|' + f(l['real_gdp_trn']) + '|' + f(l['delta_GDP_vs_matched_SQ']) + '|' + str(first(n, lambda x: x['worker_va_gdp_ratio'] > .05) or 'なし') + '|')
for n in ['F_STOCK400', 'SLACK5_F400', 'SLACK10_F400', 'DM04_PREMIUM', 'DM04_PUBLIC', 'DM04_INTERNAL']:
    need('|' + n + '|' + str(sum(by[n][y]['supply_binding'] for y in range(2026, 2056))) + '|' + f(by[n][2055]['real_gdp_trn']) + '|')
need('人口比4%参照の期間最大比率は' + f(max(by['F_BAND4'][y]['population_ratio'] for y in range(2026, 2056)) * 100) + '%、最小の年間国際純移動は' + f(min(by['F_BAND4'][y]['foreign_net_migration'] for y in range(2027, 2056)), 0) + '人')
need('ANCHOR_ONLY_SQは' + f(by['ANCHOR_ONLY_SQ'][2055]['real_gdp_trn']) + '兆円')
need('変更すると' + f(by['SQ_COMMON'][2055]['real_gdp_trn'] - by['ANCHOR_ONLY_SQ'][2055]['real_gdp_trn']) + '兆円変化する')
pr('A2 Report.md lines checked', chk, 'not found', len(miss)); [pr('  MISSING', m) for m in miss[:6]]

# A3 identities
mxid = 0.
for c, d in by.items():
    for y, r in d.items():
        mxid = max(mxid, abs(r['population'] - r['foreign'] - r['japanese']), abs(r['population'] - r['under15'] - r['working_age'] - r['elderly']))
pr('A3 pop = JP + foreign = age sum, max abs dev (persons): %.2e' % mxid)
jd = max(abs(by[c][y]['japanese'] - by['SQ_COMMON'][y]['japanese']) for c in by if by[c] and c not in ('IPSS_EXACT_SQ',) and IN['cases'] and 1 for y in range(2026, 2056) if next(s for s in IN['cases'] if s['id'] == c).get('anchor', 'OBS2025') == 'OBS2025')
pr('A3 Japanese population identical across every anchored path (max dev, persons): %.2e' % jd)
ex = by['IPSS_EXACT_SQ']; me = max(max(abs(ex[y]['population'] - rc.REF[y]['population']), abs(ex[y]['foreign'] - rc.REF[y]['foreign']), abs(ex[y]['japanese'] - rc.REF[y]['japanese'])) for y in range(2026, 2056))
pr('A3 IPSS_EXACT_SQ vs IPSS table max dev (persons): %.2e' % me)
# cumulative-formula equivalence (model) vs stock-recursion (mine): P-ipss-dp == sum(flow-base)
mx2 = 0.
for c, d in by.items():
    cum = 0.
    for y in range(2027, 2056): cum += d[y]['foreign_net_migration'] - d[y]['ipss_net_migration_reference']; mx2 = max(mx2, abs(d[y]['migration_cumulative_difference'] - cum))
pr('A3 cumulative-difference identity, max dev: %.2e' % mx2)

# B net migration reflection / double count in ledger
sq = by['SQ_COMMON']; f4 = by['F_STOCK400']
pr('B F400-SQ population diff 2055', round(f4[2055]['population'] - sq[2055]['population']), 'sum of flow diffs', round(sum(f4[y]['foreign_net_migration'] - sq[y]['foreign_net_migration'] for y in range(2030, 2056))), '; foreign diff', round(f4[2055]['foreign'] - sq[2055]['foreign']))
pr('B residual R_F (persons/yr) 2027,2035,2040,2045,2055:', [round(sq[y]['foreign_nonmigration_reference_residual']) for y in (2027, 2035, 2040, 2045, 2055)], 'sum 2027-55', round(sum(sq[y]['foreign_nonmigration_reference_residual'] for y in range(2027, 2056))))
pr('B bridge term IPSS_EXACT (persons) 2027,2035,2041,2045,2055:', [round(ex[y]['population_reference_bridge']) for y in (2027, 2035, 2041, 2045, 2055)])
pr('B foreign share 2055 SQ_IPSS (anchored) vs IPSS table:', round(by['SQ_IPSS'][2055]['foreign']), rc.REF[2055]['foreign'], 'diff', round(by['SQ_IPSS'][2055]['foreign'] - rc.REF[2055]['foreign']), '= initial foreign offset', round(OBS_df := (rc.OBS['foreign'] - rc.REF[2025]['foreign'])))
pr('B 2026 start: pop %.0f foreign %.0f JP %.0f; vs 2026-10 estimate 122,690,000 -> %.0f' % (sq[2026]['population'], sq[2026]['foreign'], sq[2026]['japanese'], sq[2026]['population'] - 122690000))

# C ratio targets: constant flow scan (ledger only, 2027 start), zero inflow, compare band rule
def ratio_path(flow, pol='SQ', mode='COMMON'):
    old_f = CA['common_foreign_net_flow']; CA['common_foreign_net_flow'] = flow
    try: L = rc.ledger(dict(policy=pol, mode=mode))
    finally: CA['common_foreign_net_flow'] = old_f
    return [r['foreign'] / r['population'] for r in L]
z = ratio_path(0.); pr('C zero inflow from 2027: ratio 2026 %.3f%%, max %.3f%% (year %d), 2055 %.3f%%' % (z[0] * 100, max(z) * 100, 2026 + z.index(max(z)), z[-1] * 100))
def solve(fn, target):
    lo, hi = -2e5, 8e5
    for _ in range(80):
        mid = (lo + hi) / 2
        if fn(mid) > target: hi = mid
        else: lo = mid
    return lo
for T in (.03, .04, .05):
    a = solve(lambda x: ratio_path(x)[-1], T); b = solve(lambda x: max(ratio_path(x)), T)
    pr('C constant annual net flow from 2027: 2055 ratio = %d%% needs %.0f/yr ; max-over-years <= %d%% needs %.0f/yr' % (T * 100, a, T * 100, b))
# C2 band rule: equilibrium/stability and flows
pr('C2 band rule (speed .2, smoothing .5): matrix [[.9,.5],[-.1,.5]] det=%.2f trace=%.2f |eig|=%.3f' % (.9 * .5 + .5 * .1, 1.4, math.sqrt(.5)))
for n in ('F_BAND3', 'F_BAND4', 'F_BAND5'):
    d = by[n]; neg = [y for y in range(2027, 2056) if d[y]['foreign_net_migration'] < 0]
    pr('C2', n, 'neg-flow years', len(neg), 'first', neg[0] if neg else None, 'min', round(min(d[y]['foreign_net_migration'] for y in range(2027, 2056))), 'cum 2030-55 flow', round(sum(d[y]['foreign_net_migration'] for y in range(2030, 2056))), 'max ratio %.3f%%' % (max(d[y]['population_ratio'] for y in d) * 100), 'ratio2055 %.3f%%' % (d[2055]['population_ratio'] * 100))
pr('C2 SQ_COMMON cum 2030-55 flow', round(sum(sq[y]['foreign_net_migration'] for y in range(2030, 2056))))

# D labour connection / contribution
tx = rc.eng.cfg; ew = tx['policy_inputs']['elderly_additional_workers']; pr('D elderly_additional_workers (F, from 2030 full):', ew, ' TEXT aging_drag:', tx['baseline_profiles']['TEXT_ASSUMPTIONS']['aging_drag_pp'], 'labor_response', tx['common_model']['labor_response'])
def Lw(n, y): return by[n][y]['effective_productive_workers'] + (ew if by[n][y]['policy'] == 'F' else 0.) if 'policy' in by[n][y] else None
def pol(n): return next(s for s in IN['cases'] if s['id'] == n)['policy']
def Leff(n, y): return by[n][y]['effective_productive_workers'] + (ew * rc.eng.ramp(y, 2028) if pol(n) == 'F' else 0.)
for a, b in (('F_STOCK400', 'F_SAME_FLOW'), ('F_STOCK300', 'F_SAME_FLOW'), ('F_BAND4', 'F_SAME_FLOW'), ('SQ_COMMON', 'SQ_IPSS')):
    y = 2055; dY = by[a][y]['real_gdp_trn'] - by[b][y]['real_gdp_trn']; dL = Leff(a, y) - Leff(b, y); dFo = by[a][y]['foreign'] - by[b][y]['foreign']; dEm = by[a][y]['foreign_employed_conditional'] - by[b][y]['foreign_employed_conditional']
    el = (dY / by[b][y]['real_gdp_trn']) / (dL / Leff(b, y)); impl = dY * 1e12 / dEm if dEm else float('nan'); dN = by[a][y]['nominal_gdp_trn'] - by[b][y]['nominal_gdp_trn']; dAtt = (by[a][y]['foreign_employed_conditional'] - by[b][y]['foreign_employed_conditional']) * 8e-6 * (by[a][y]['nominal_gdp_trn'] and (rc.eng.cfg and 1))
    pr('D %s - %s (2055): dGDP %.3f兆, dForeignRes %.0f万, dForeignWorkers %.0f万, dEffLabour %.1f万, GDP-elasticity-to-labour %.3f, implied real GDP per extra foreign worker %.0f万円, dNominalGDP %.3f兆' % (a, b, dY, dFo / 1e4, dEm / 1e4, dL / 1e4, el, impl / 1e4, dN))
# product-only identification
for a, b in (('ECON_E60_Q8_F400', 'ECON_E80_Q6_F400'), ('ECON_E60_Q8_SQ', 'ECON_E80_Q6_SQ')):
    dm = max(abs(by[a][y]['real_gdp_trn'] - by[b][y]['real_gdp_trn']) for y in range(2026, 2056)); dt = max(abs(by[a][y]['tax_diagnostic_trn'] - by[b][y]['tax_diagnostic_trn']) for y in range(2026, 2056))
    pr('D employment x coefficient collinearity:', a, 'vs', b, 'max |dGDP| %.2e max |dTax| %.2e (employment .6x800 == .8x600)' % (dm, dt))
# productivity-zero test: does foreign stock add anything outside the weighted labour channel?
def run_case(s, pol_override=None):
    ss = {**s}; d = rc.ledger(ss); c = rc.ledger({**ss, 'policy': 'SQ', 'mode': rc.sq_mode(ss)}); 
    if pol_override: ss['policy'] = pol_override
    return rc.macro(ss, d, c), d
r0, d0 = run_case(dict(id='Q0F', policy='F', mode='STOCK400', productivity=0.)); r1, d1 = run_case(dict(id='Q0S', policy='F', mode='COMMON', productivity=0.))
pr('D productivity=0: F_STOCK400 vs F_SAME_FLOW real GDP 2055 %.6f vs %.6f (diff %.3e) -> foreign stock has no GDP channel except weighted labour; extra 2.75M residents with q=0' % (r0[2055]['real_gdp_trn'], r1[2055]['real_gdp_trn'], r0[2055]['real_gdp_trn'] - r1[2055]['real_gdp_trn']))
# E: GDP-5% attribution: diagnostic nominal attribution vs actual nominal GDP diff for pure migration path
for a, b in (('F_STOCK400', 'F_SAME_FLOW'), ('F_BAND4', 'F_SAME_FLOW')):
    y = 2055; dAtt = (by[a][y]['worker_va_attribution_nominal'] - by[b][y]['worker_va_attribution_nominal']); dN = by[a][y]['nominal_gdp_trn'] - by[b][y]['nominal_gdp_trn']
    pr('E diagnostic nominal attribution diff %s-%s: %.3f兆 vs actual nominal GDP diff %.3f兆 (ratio %.2f)' % (a, b, dAtt, dN, dN / dAtt))
for n in ('SQ_COMMON', 'F_STOCK400'):
    l = by[n][2055]; pr('E', n, '2055 worker-VA attribution %.2f兆 of nominal GDP %.2f兆 = %.2f%%; legacy resident formula %.2f%%; 2026 start legacy %.2f%% worker %.2f%%' % (l['worker_va_attribution_nominal'], l['nominal_gdp_trn'], l['worker_va_gdp_ratio'] * 100, l['legacy_resident_gdp5_reference'] * 100, by[n][2026]['legacy_resident_gdp5_reference'] * 100, by[n][2026]['worker_va_gdp_ratio'] * 100))

# F: F-SQ decomposition ordering dependence (interaction)
def gdp(s, mig_pol, macro_pol):
    ss = {**s, 'policy': mig_pol}; d = rc.ledger(ss); c = rc.ledger({**ss, 'policy': 'SQ', 'mode': rc.sq_mode(ss)})
    return rc.macro({**ss, 'policy': macro_pol}, d, c)[2055]['real_gdp_trn']
for n, mode in (('F_STOCK400', 'STOCK400'), ('F_STOCK300', 'STOCK300'), ('F_BAND4', 'BAND')):
    base = gdp(dict(id='a', mode='COMMON'), 'SQ', 'SQ'); fcom = gdp(dict(id='a', mode='COMMON'), 'F', 'F'); fmig = gdp(dict(id='a', mode=mode), 'F', 'F'); smig = gdp(dict(id='a', mode=mode), 'F', 'SQ')
    total = fmig - base; nonmig = fcom - base; mig_after = fmig - fcom; mig_alone = smig - base; pol_after_mig = fmig - smig
    pr('F %s total %.3f = [order A: non-migration %.3f + migration|F %.3f] = [order B: migration alone %.3f + policy|migration %.3f] ; interaction %.3f' % (n, total, nonmig, mig_after, mig_alone, pol_after_mig, mig_after - mig_alone))

# G: input-table internal consistency (IPSS tables themselves are NOT re-read from the PDF: not on the session allowlist)
REF = rc.REF; bad = []; mxd = 0.
for y in range(2025, 2056):
    r = REF[y]; fw = r['working_age'] - r['japanese_working_age']; fe = r['elderly'] - r['japanese_elderly']; fc = r['under15'] - r['japanese_under15']
    ds = [abs(r['population'] - r['japanese'] - r['foreign']), abs(r['population'] - r['under15'] - r['working_age'] - r['elderly']), abs(r['japanese'] - r['japanese_under15'] - r['japanese_working_age'] - r['japanese_elderly']), abs(fw + fe + fc - r['foreign'])]
    mxd = max(mxd, *ds)
    if min(fw, fe, fc) < 0: bad.append((y, 'negative foreign age group'))
    if r['foreign'] != r['population'] - r['japanese']: bad.append((y, 'foreign not derived'))
pr('G IPSS table internal: max identity deviation %.0f persons (source tables are in 1,000-person units, so up to a few thousand is rounding); structural problems:' % mxd, bad)
o = rc.OBS; ob = abs(o['population'] - o['japanese'] - o['foreign']) + abs(o['population'] - o['under15'] - o['working_age'] - o['elderly'])
pr('G IPSS reference table internal consistency problems:', bad, '| 2025 obs identity dev', ob)
pr('G SNA GDP/employed = %.1f yen (report 約915.4万円)' % (IN['reference_economic_data']['nominal_GDP_trn'] * 1e12 / IN['reference_economic_data']['SNA_employed_persons']), '| MHLW 2,571,037/4,125,395 = %.4f' % (2571037 / 4125395))
dpf = [(y, REF[y]['population'] - REF[y-1]['population']) for y in range(2027, 2056)]
imp = {y: (REF[y]['population'] - REF[y-1]['population']) - (REF[y]['births_calendar'] - REF[y]['deaths_calendar']) for y in range(2027, 2056)}
pr('G implied total net migration from IPSS table (dP-(B-D)), 2027,2035,2040,2041,2045,2050,2055:', [round(imp[y]) for y in (2027, 2035, 2040, 2041, 2045, 2050, 2055)], '| model foreign base flow:', [round(rc.baseflow(y)) for y in (2027, 2040, 2041, 2045, 2050, 2055)])
# G2 sensitivity: replace the post-2040 aggregate approximation by 'implied IPSS total migration - 3,209 Japanese/rounding'
orig = rc.baseflow
alt = lambda y: orig(y) if y <= 2040 else imp[y] - 3209.
def with_base(fn, cases):
    rc.baseflow = fn; out = {}
    try:
        for s in cases:
            r, d = rc.case(s); out[s['id']] = (r[2055]['real_gdp_trn'], d[-1]['population'], d[-1]['foreign'] / d[-1]['population'], r[2055]['tax_diagnostic_trn'])
    finally: rc.baseflow = orig
    return out
cs = [s for s in IN['cases'] if s['id'] in ('SQ_COMMON', 'F_STOCK400', 'F_BAND4', 'F_SAME_FLOW')]
a0 = with_base(orig, cs); a1 = with_base(alt, cs)
for k in a0: pr('G2 post-2040 base-flow sensitivity %s 2055: GDP %.3f -> %.3f, pop %.1f万 -> %.1f万, foreign ratio %.3f%% -> %.3f%%' % (k, a0[k][0], a1[k][0], a0[k][1] / 1e4, a1[k][1] / 1e4, a0[k][2] * 100, a1[k][2] * 100))
pr('G2 cumulative base difference 2041-55 (persons):', round(sum(alt(y) - orig(y) for y in range(2041, 2056))))
# H: first-year dependence: BAND initial increment 350k sensitivity (ledger-only)
for inc0 in (0., 150000., 350000., 500000.):
    CA['band_reference_stock_increment'] = inc0; L = rc.ledger(dict(policy='F', mode='BAND'))
    pr('H band prev-increment %.0f: 2030 flow %.0f, min flow %.0f, max ratio %.3f%%, 2055 ratio %.3f%%' % (inc0, L[4]['foreign_net_migration'], min(r['foreign_net_migration'] for r in L[1:]), max(r['foreign'] / r['population'] for r in L) * 100, L[-1]['foreign'] / L[-1]['population'] * 100))
CA['band_reference_stock_increment'] = 350000.

# A4 label/parameter columns written by the model equal the case definitions
lb = 0
for s in IN['cases']:
    for y in range(2026, 2056):
        c = ANN[(s['id'], y)]
        exp = dict(policy=s['policy'], migration_mode=s['mode'], anchor=s.get('anchor', 'OBS2025'))
        if any(c[k] != v for k, v in exp.items()): lb += 1
        if abs(float(c['employment_fraction']) - s.get('employment', CA['foreign_employment_per_resident'])) > 1e-12 or abs(float(c['value_added_per_worker_2026_yen']) - s.get('productivity', CA['foreign_value_added_trn_per_worker_2026']) * 1e12) > 1e-3 or abs(float(c['slack']) - s.get('slack', CA['slack'])) > 1e-12: lb += 1
pr('A4 case label/parameter columns mismatching case definitions:', lb)
# A5 blank (not-computed) columns really blank
pr('A5 foreign_births/foreign_deaths/nationality_net_transfer/japanese_net_migration non-blank cells:', sum(1 for r in ANN.values() for k in ('foreign_births', 'foreign_deaths', 'nationality_net_transfer', 'japanese_net_migration') if r[k] != ''))
