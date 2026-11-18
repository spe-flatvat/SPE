# Supplementary checks for the F TX-01..03 model verification (Claude, read-only). Uses the independent engine in the sibling file.
# Usage: python3 -I SPE_F_TX_Supplementary_Checks_DRAFT_20261118.py <Inputs.json> <Annual_Comparison.csv> <prior Text CSV db52249f> <DM CSV 30b926dd> <Run_Report.md>
import sys, os, csv, json, itertools, copy, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import SPE_F_TX_Independent_Recalc_DRAFT_20261118 as E
cfg = E.cfg; D = E.D
ALL = {s['id']: E.run(s) for s in cfg['cases']}
SPEC = {s['id']: s for s in cfg['cases']}
prior = {int(r['year']): r for r in csv.DictReader(open(sys.argv[3], encoding='utf-8')) if r['case'] == 'ILLUSTRATIVE_ALL'}
dm = {}
for r in csv.DictReader(open(sys.argv[4], encoding='utf-8')): dm.setdefault(r['case'], {})[int(r['year'])] = r
report = open(sys.argv[5], encoding='utf-8').read()
g = lambda c, y, k: ALL[c][y][k]
def sec(t): print('\n== ' + t)

sec('A. Legacy replays against stored fixed outputs (independent engine)')
for name, ref, cols in [('LEGACY_CORE_REPLAY', dm['CORE_NO_POLICY'], ['real_gdp_trn', 'nominal_gdp_trn', 'tax_macro_trn', 'expenditure_diagnostic_trn', 'population_persons']),
                        ('TEXT_PREVIOUS_ASSUMPTIONS_REPLAY', prior, ['real_gdp_trn', 'nominal_gdp_trn', 'tax_macro_trn', 'tax_diagnostic_trn', 'expenditure_diagnostic_trn', 'population_persons', 'I_policy_real_trn', 'capital_total_real_trn'])]:
    mx = 0.
    for y in range(2026, 2056):
        for k in cols:
            a = g(name, y, k); b = float(ref[y][k]); mx = max(mx, abs(a - b) / max(1., abs(b)))
    print(name, 'cols', len(cols), 'max rel diff vs stored', '%.3e' % mx)
emb = cfg['legacy_core_reference']
print('embedded legacy_core_reference == stored 30b926dd CORE_NO_POLICY rows (all shared columns):',
      all(str(emb[i][k]) == dm['CORE_NO_POLICY'][2026 + i][k] for i in range(30) for k in emb[i] if k in dm['CORE_NO_POLICY'][2026 + i]))

sec('B. TX-01 2x2 identity from CSV values (independent, all 12 metrics, both cap states)')
M = ['real_gdp_trn', 'nominal_gdp_trn', 'tax_macro_trn', 'tax_diagnostic_trn', 'expenditure_diagnostic_trn', 'fiscal_balance_partial_trn', 'funding_gap_proxy_trn', 'household_disposable_nominal_trn', 'household_consumption_real_proxy_trn', 'I_policy_real_trn', 'capital_total_real_trn', 'population_persons']
worst = 0.; n = 0
for suf in ['CAP', 'UNCAPPED']:
    for y in range(2026, 2056):
        for k in M:
            s0 = float(D[('OLD_ASSUMPTIONS_SQ_' + suf, y)][k]); f0 = float(D[('OLD_ASSUMPTIONS_F_' + suf, y)][k]); s1 = float(D[('TEXT_ASSUMPTIONS_SQ_' + suf, y)][k]); f1 = float(D[('TEXT_ASSUMPTIONS_F_' + suf, y)][k])
            tot = f1 - s0; parts = (s1 - s0) + (f0 - s0) + ((f1 - s1) - (f0 - s0)); worst = max(worst, abs(tot - parts)); n += 1
print('cells', n, 'max |total - (baseline+policy_old+interaction)|', '%.2e' % worst)

sec('C. TX-01 profile coverage and exact factorial (2^7) decomposition, 2055, CAP')
OLD = cfg['baseline_profiles']['OLD_ASSUMPTIONS']; TXT = cfg['baseline_profiles']['TEXT_ASSUMPTIONS']
keys = sorted(k for k in OLD if OLD[k] != TXT[k]); print('profile keys differing OLD vs TEXT:', keys, '| keys in profile:', sorted(OLD))
def run_prof(sub, pol):
    ov = {k: TXT[k] for k in sub}
    s = dict(id='X', profile='OLD_ASSUMPTIONS', profile_override=ov, policy=pol, supply_cap=True)
    return E.run(s)[2055]
cache = {}
def val(sub, pol, metric):
    key = (frozenset(sub), pol)
    if key not in cache: cache[key] = run_prof(sub, pol)
    return cache[key][metric]
full = run_prof(keys, 'F'); print('OLD with all 7 overrides == TEXT profile (F, 2055 GDP):', abs(full['real_gdp_trn'] - g('TEXT_ASSUMPTIONS_F_CAP', 2055, 'real_gdp_trn')) < 1e-9, '| SQ:', abs(run_prof(keys, 'SQ')['real_gdp_trn'] - g('TEXT_ASSUMPTIONS_SQ_CAP', 2055, 'real_gdp_trn')) < 1e-9)
from math import factorial
def shapley(fn):
    nF = len(keys); res = {}
    for k in keys:
        others = [x for x in keys if x != k]; tot = 0.
        for r in range(len(others) + 1):
            for S in itertools.combinations(others, r):
                w = factorial(r) * factorial(nF - r - 1) / factorial(nF)
                tot += w * (fn(set(S) | {k}) - fn(set(S)))
        res[k] = tot
    return res
for metric in ['real_gdp_trn', 'tax_diagnostic_trn', 'expenditure_diagnostic_trn']:
    sq = shapley(lambda S: val(S, 'SQ', metric)); pol = shapley(lambda S: val(S, 'F', metric) - val(S, 'SQ', metric))
    print(metric, '2055 Shapley baseline effect on SQ level (sum %.3f) / on F-SQ gap (sum %.3f)' % (sum(sq.values()), sum(pol.values())))
    for k in keys: print('   %-32s SQ %+9.3f | F-SQ %+8.3f' % (k, sq[k], pol[k]))
print('check: OLD F-SQ gap 2055 + sum of Shapley gap effects = TEXT F-SQ gap ->',
      round(val(set(), 'F', 'real_gdp_trn') - val(set(), 'SQ', 'real_gdp_trn') + sum(shapley(lambda S: val(S, 'F', 'real_gdp_trn') - val(S, 'SQ', 'real_gdp_trn')).values()), 6), 'vs', round(g('TEXT_ASSUMPTIONS_F_CAP', 2055, 'real_gdp_trn') - g('TEXT_ASSUMPTIONS_SQ_CAP', 2055, 'real_gdp_trn'), 6))
a = {k: val({k}, 'SQ', 'real_gdp_trn') - val(set(), 'SQ', 'real_gdp_trn') for k in keys}
print('sum of one-at-a-time SQ GDP effects %.3f vs exact total baseline effect %.3f (non-additive residual %.3f)' % (sum(a.values()), val(set(keys), 'SQ', 'real_gdp_trn') - val(set(), 'SQ', 'real_gdp_trn'), val(set(keys), 'SQ', 'real_gdp_trn') - val(set(), 'SQ', 'real_gdp_trn') - sum(a.values())))

sec('D. Is F-SQ GDP gap a labour-supply effect (core GDP) or a demand/policy effect?')
for pr in ['OLD_ASSUMPTIONS', 'TEXT_ASSUMPTIONS']:
    for y in [2035, 2045, 2055]:
        f = ALL[pr + '_F_CAP'][y]; s = ALL[pr + '_SQ_CAP'][y]
        print(pr, y, 'F-SQ real GDP %.3f = core(labour) %.3f + gap-part %.3f' % (f['real_gdp_trn'] - s['real_gdp_trn'], f['core_real_gdp_trn'] - s['core_real_gdp_trn'], (f['real_gdp_trn'] - f['core_real_gdp_trn']) - (s['real_gdp_trn'] - s['core_real_gdp_trn'])))

sec('E. TX-02 supply ceiling / price channel')
for pr in ['OLD_ASSUMPTIONS', 'TEXT_ASSUMPTIONS']:
    sqc = ALL[pr + '_SQ_CAP']; sqn = ALL[pr + '_SQ_UNCAPPED']; sqp = ALL[pr + '_SQ_CAP_PRICE_NEUTRAL']
    print(pr, 'SQ cap/uncapped/price-neutral identical in all columns:', all(sqc[y][k] == sqn[y][k] == sqp[y][k] for y in sqc for k in ['real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn']), '| SQ binding years:', sum(sqc[y]['supply_binding'] for y in sqc))
    base = ALL[pr + '_F_CAP']; unc = ALL[pr + '_F_UNCAPPED']; neu = ALL[pr + '_F_CAP_PRICE_NEUTRAL']
    bind = [y for y in base if base[y]['supply_binding']]
    print('  F_CAP binding years %d (%d-%d), max unmet %.3f in %d; first-year unmet %.3f' % (len(bind), bind[0], bind[-1], max(base[y]['unmet_demand_real'] for y in base), max(base, key=lambda y: base[y]['unmet_demand_real']), base[bind[0]]['unmet_demand_real']))
    print('  F_UNCAPPED excess_vs_ceiling max %.3f; GDP 2055 CAP %.3f UNCAPPED %.3f diff %+.3f (%.2f%%)' % (max(unc[y]['excess_demand_relative_to_ceiling_trn'] for y in unc), base[2055]['real_gdp_trn'], unc[2055]['real_gdp_trn'], unc[2055]['real_gdp_trn'] - base[2055]['real_gdp_trn'], 100 * (unc[2055]['real_gdp_trn'] / base[2055]['real_gdp_trn'] - 1)))
    print('  price channel: tax_diag 2055 CAP %.4f PRICE_NEUTRAL %.4f diff %+.4f ; nominal GDP diff %+.4f ; max cumulative-year tax diff %.4f' % (base[2055]['tax_diagnostic_trn'], neu[2055]['tax_diagnostic_trn'], base[2055]['tax_diagnostic_trn'] - neu[2055]['tax_diagnostic_trn'], base[2055]['nominal_gdp_trn'] - neu[2055]['nominal_gdp_trn'], max(base[y]['tax_diagnostic_trn'] - neu[y]['tax_diagnostic_trn'] for y in base)))
    print('  real GDP identical CAP vs PRICE_NEUTRAL in every year:', all(abs(base[y]['real_gdp_trn'] - neu[y]['real_gdp_trn']) < 1e-12 for y in base))
    # DM-04 channel
    print('  DM-04 2055 real GDP diff vs UNALLOCATED:  CAP: PREMIUM %+.6f PUBLIC %+.6f INTERNAL %+.6f | UNCAPPED: PREMIUM %+.6f PUBLIC %+.6f INTERNAL %+.6f' % tuple(
        [g(pr + '_F_%s_CAP' % m, 2055, 'real_gdp_trn') - base[2055]['real_gdp_trn'] for m in ['PREMIUM', 'PUBLIC', 'INTERNAL']] + [g(pr + '_F_%s_UNCAPPED' % m, 2055, 'real_gdp_trn') - unc[2055]['real_gdp_trn'] for m in ['PREMIUM', 'PUBLIC', 'INTERNAL']]))
    print('  DM-04 under CAP: PREMIUM tax_diag 2055 diff %+.5f, nominal diff %+.5f (real GDP unchanged but price channel moves nominal/tax)' % (g(pr + '_F_PREMIUM_CAP', 2055, 'tax_diagnostic_trn') - base[2055]['tax_diagnostic_trn'], g(pr + '_F_PREMIUM_CAP', 2055, 'nominal_gdp_trn') - base[2055]['nominal_gdp_trn']))
    pm = ALL[pr + '_F_PREMIUM_UNCAPPED']; mx = max(range(2028, 2056), key=lambda y: abs(pm[y]['real_gdp_trn'] - unc[y]['real_gdp_trn']))
    print('  PREMIUM vs UNALLOCATED UNCAPPED: largest annual GDP diff %+.4f in %d; cumulative-2055 %+.4f' % (pm[mx]['real_gdp_trn'] - unc[mx]['real_gdp_trn'], mx, pm[2055]['real_gdp_trn'] - unc[2055]['real_gdp_trn']))
    for m in ['PUBLIC', 'INTERNAL']:
        c = ALL[pr + '_F_%s_UNCAPPED' % m]
        print('  %s vs UNALLOCATED UNCAPPED real GDP identical all years: %s | expenditure diff 2055 %+.4f | fiscal_balance diff 2055 %+.4f' % (m, all(abs(c[y]['real_gdp_trn'] - unc[y]['real_gdp_trn']) < 1e-12 for y in c), c[2055]['expenditure_diagnostic_trn'] - unc[2055]['expenditure_diagnostic_trn'], c[2055]['fiscal_balance_partial_trn'] - unc[2055]['fiscal_balance_partial_trn']))

sec('F. TX-03 flow / stock / ratio: closed-form checks and breach years')
def closed(c):
    sp = SPEC[c]; p, prof, m, F, om = E.params(sp); rp = prof['migration_delivery_ramp_years']
    rs = [E.ramp(y, m['flow_start'], rp) for y in range(2027, 2056)]
    cf = sum(m['common_annual_net_flow'] * x for x in rs)
    add = (max(m['F_total_flow_reference'] - m['common_annual_net_flow'], 0.) if m['F_flow_interpretation'] == 'TOTAL_TARGET' else m['F_additional_flow_reference']) * sum(rs) if F and m['enforcement_mode'] == 'NONE_REFERENCE' else None
    return cf, add, m
for c in ['OLD_ASSUMPTIONS_SQ_CAP', 'OLD_ASSUMPTIONS_F_CAP', 'TEXT_ASSUMPTIONS_SQ_CAP', 'TEXT_ASSUMPTIONS_F_CAP', 'MIG_ADDITIONAL400K', 'MIG_COMMON_ZERO_SQ', 'MIG_COMMON_ZERO_F', 'MIG_RETENTION_98']:
    cf, add, m = closed(c); r = ALL[c][2055]
    exp_stock = None if (add is None or m['foreign_stock_net_retention'] != 1.0) else m['foreign_initial_stock'] + cf + add
    print('%-26s common cum %.0f (model common-pop minus births-deaths ok) | F add closed %s vs model %.0f | stock closed %s vs model %.0f' % (c, cf, None if add is None else '%.0f' % add, r['policy_population_increment_persons'], None if exp_stock is None else '%.0f' % exp_stock, r['foreign_stock_conditional_persons']))
print('\nfirst year ratio > 3% / > 5% (population ratio of conditional foreign stock), ratio in 2026 and 2030, and GDP-contribution ratio (stock*8e-6/coreN) 2055:')
for c in ['OLD_ASSUMPTIONS_SQ_CAP', 'OLD_ASSUMPTIONS_F_CAP', 'TEXT_ASSUMPTIONS_SQ_CAP', 'TEXT_ASSUMPTIONS_F_CAP', 'MIG_ADDITIONAL400K', 'MIG_GDP_STOCK_CAP_INTERPRETATION', 'MIG_RETENTION_98', 'MIG_COMMON_ZERO_SQ', 'MIG_COMMON_ZERO_F']:
    rs = ALL[c]; y3 = next((y for y in rs if rs[y]['foreign_stock_population_ratio'] is not None and rs[y]['foreign_stock_population_ratio'] > .03), None); y5 = next((y for y in rs if rs[y]['foreign_stock_population_ratio'] is not None and rs[y]['foreign_stock_population_ratio'] > .05), None)
    print('  %-34s >3%%: %s  >5%%: %s  ratio2026 %.2f%% 2030 %.2f%% 2055 %.2f%% | GDP-share 2055 %.2f%% (2035 %.2f%%) | trigger_migration(2035)=%d' % (c, y3, y5, 100 * rs[2026]['foreign_stock_population_ratio'], 100 * rs[2030]['foreign_stock_population_ratio'], 100 * rs[2055]['foreign_stock_population_ratio'], 100 * rs[2055]['foreign_gdp_contribution_ratio'], 100 * rs[2035]['foreign_gdp_contribution_ratio'], rs[2055]['_tg_mig']))
print('trigger_migration fired (pop<1e8 in 2035) in any of 47 paths:', [c for c in ALL if ALL[c][2035]['_tg_mig']])
print('min population 2034 across paths: %.0f ; max: %.0f' % (min(ALL[c][2034]['population_persons'] for c in ALL), max(ALL[c][2034]['population_persons'] for c in ALL)))
m0 = ALL['MIG_GDP_STOCK_CAP_INTERPRETATION']
print('GDP_STOCK interpretation: F accepted flow by year (nonzero):', {y: round(m0[y]['policy_migration_accepted_net_flow']) for y in m0 if m0[y]['policy_migration_requested_net_flow'] > 0 and y < 2040}, '| ceiling persons 2031/2035/2055: %.0f / %.0f / %.0f' % (m0[2031]['_ceil'], m0[2035]['_ceil'], m0[2055]['_ceil']))
print('  cap binds on F additions from year', next(y for y in m0 if m0[y]['policy_migration_accepted_net_flow'] < m0[y]['policy_migration_requested_net_flow'] - 1e-9), '; GDP-share of stock vs 5% in same case 2031..2035:', [round(100 * m0[y]['foreign_gdp_contribution_ratio'], 2) for y in range(2031, 2036)])
r = ALL['MIG_RETENTION_98']
print('RETENTION_98: foreign labour term sign 2027-2029 (stock - initial):', [round(r[y]['foreign_stock_conditional_persons'] - 2000000.) for y in (2027, 2028, 2029)], '-> labour growth pct', [round(r[y]['labor_growth_pct'], 4) for y in (2027, 2028, 2029)], 'vs retention=1 TEXT_F', [round(ALL['TEXT_ASSUMPTIONS_F_CAP'][y]['labor_growth_pct'], 4) for y in (2027, 2028, 2029)])
print('F-additional share of 2055 stock excess: TEXT_F stock %.0f of which F additional %.0f (%.1f%%)' % (ALL['TEXT_ASSUMPTIONS_F_CAP'][2055]['foreign_stock_conditional_persons'], ALL['TEXT_ASSUMPTIONS_F_CAP'][2055]['policy_population_increment_persons'], 100 * ALL['TEXT_ASSUMPTIONS_F_CAP'][2055]['policy_population_increment_persons'] / ALL['TEXT_ASSUMPTIONS_F_CAP'][2055]['foreign_stock_conditional_persons']))

sec('G. Regression / side effects: DM-04 payer identities and DM-05 start-year independence')
bad = 0
for c in ALL:
    for y in ALL[c]:
        r = ALL[c][y]
        if abs(r['medical_insurer_vat'] - r['medical_initial_premium'] - r['medical_extra_premium'] - r['medical_public_topup'] - r['medical_internal'] - r['medical_unallocated']) > 1e-9: bad += 1
print('insurer funding identity violations over', len(ALL) * 30, 'rows:', bad)
# DM-05: year8-only / investment-only / both, using the independent engine, F policy with a non-null investment_flow_share to also exercise the promotion-flow channel
def mk(ov, share=None):
    o = dict(ov)
    if share is not None: o['investment_flow_share'] = share
    return dict(id='T', profile='OLD_ASSUMPTIONS', policy='F', supply_cap=True, policy_override=o)
for share in [None, 0.01]:
    print('investment_flow_share =', share)
    base = E.run(mk({}, share)); y8 = E.run(mk({'year8': 2031, 'year5': 2036, 'food_eight_start': 2031}, share)); inv = E.run(mk({'investment_start': 2030}, share))
    both = E.run(mk({'year8': 2031, 'year5': 2036, 'food_eight_start': 2031, 'investment_start': 2030}, share))
    f = lambda rs, k, y: 0. if rs[y][k] is None else rs[y][k]
    print('   I_policy_real 2029/2031/2035: base %s | tax-start only %s | invest-start only %s | both %s' % tuple([[round(f(rs, 'I_policy_real_trn', y), 5) for y in (2029, 2031, 2035)] for rs in (base, y8, inv, both)]))
    print('   corporate credit proxy via firm_credit not exported; GDP 2035: base %.4f tax-start-only %.4f invest-only %.4f both %.4f' % (base[2035]['real_gdp_trn'], y8[2035]['real_gdp_trn'], inv[2035]['real_gdp_trn'], both[2035]['real_gdp_trn']))
print('model default investment_start=%s, year8=%s, investment_flow_share=%s, education_flow_share=%s' % (cfg['policy_inputs']['investment_start'], cfg['policy_inputs']['year8'], cfg['policy_inputs']['investment_flow_share'], cfg['policy_inputs']['education_flow_share']))
a = ALL['INVEST_START_ONLY_2029']; b = ALL['OLD_ASSUMPTIONS_F_CAP']
print('INVEST_START_ONLY_2029 vs base: rates identical:', all(a[y]['real_gdp_trn'] is not None for y in a), '| I_policy 2028/2029/2030 base %s vs 2029-start %s' % ([round(b[y]['I_policy_real_trn'], 6) for y in (2028, 2029, 2030)], [round(a[y]['I_policy_real_trn'], 6) for y in (2028, 2029, 2030)]))

sec('H. Report tables regenerated independently and found verbatim in the markdown report')
miss = 0; chk = 0
for pr in ['OLD_ASSUMPTIONS', 'TEXT_ASSUMPTIONS']:
    for y in [2030, 2035, 2038, 2045, 2055]:
        s = ALL[pr + '_SQ_CAP'][y]; f = ALL[pr + '_F_CAP'][y]
        vals = [s['real_gdp_trn'], f['real_gdp_trn'], f['real_gdp_trn'] - s['real_gdp_trn'], s['tax_diagnostic_trn'], f['tax_diagnostic_trn'], s['expenditure_diagnostic_trn'], f['expenditure_diagnostic_trn']]
        line = '|' + pr + '|' + str(y) + '|' + '|'.join('%.6f' % v for v in vals) + '|'; chk += 1
        if line not in report: miss += 1; print('MISSING', line)
for metric in ['real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn', 'expenditure_diagnostic_trn', 'fiscal_balance_partial_trn']:
    for y in [2030, 2035, 2038, 2045, 2055]:
        S = lambda c: ALL[c][y][metric]
        s0 = S('OLD_ASSUMPTIONS_SQ_CAP'); f0 = S('OLD_ASSUMPTIONS_F_CAP'); s1 = S('TEXT_ASSUMPTIONS_SQ_CAP'); f1 = S('TEXT_ASSUMPTIONS_F_CAP')
        vals = [s1 - s0, f0 - s0, (f1 - s1) - (f0 - s0), f1 - s0, f1 - s1]
        line = '|' + metric + '|' + str(y) + '|' + '|'.join('%+.6f' % v for v in vals) + '|'; chk += 1
        if line not in report: miss += 1; print('MISSING', line)
for key in ['aging_drag_pp', 'expenditure_growth', 'migration_delivery_ramp_years', 'climate_anchor', 'elasticity', 'birth_mode', 'foreign_labor_gap_enabled']:
    sq = ALL['ONE_%s_SQ' % key][2055]; f = ALL['ONE_%s_F' % key][2055]; s0 = ALL['OLD_ASSUMPTIONS_SQ_CAP'][2055]; f0 = ALL['OLD_ASSUMPTIONS_F_CAP'][2055]
    vals = [sq['real_gdp_trn'] - s0['real_gdp_trn'], f['real_gdp_trn'] - f0['real_gdp_trn'], (f['real_gdp_trn'] - sq['real_gdp_trn']) - (f0['real_gdp_trn'] - s0['real_gdp_trn']), sq['expenditure_diagnostic_trn'] - s0['expenditure_diagnostic_trn'], sq['tax_diagnostic_trn'] - s0['tax_diagnostic_trn']]
    line = '|' + key + '|' + '|'.join('%+.6f' % v for v in vals) + '|'; chk += 1
    if line not in report: miss += 1; print('MISSING', line)
for pr in ['OLD_ASSUMPTIONS', 'TEXT_ASSUMPTIONS']:
    for nm in ['SQ_CAP', 'F_CAP', 'F_UNCAPPED', 'F_PREMIUM_CAP', 'F_PREMIUM_UNCAPPED', 'F_PUBLIC_CAP', 'F_INTERNAL_CAP', 'F_CAP_PRICE_NEUTRAL']:
        rs = ALL[pr + '_' + nm]; b = [str(y) for y in rs if rs[y]['supply_binding']]
        line = '|' + pr + '_' + nm + '|' + str(len(b)) + '|' + (','.join(b) if b else 'なし') + '|' + '%.6f|%.6f|%.9f|%.6f' % (max(rs[y]['unmet_demand_real'] for y in rs), rs[2055]['real_gdp_trn'], rs[2055]['price_pressure_proxy'], rs[2055]['tax_diagnostic_trn']) + '|'; chk += 1
        if line not in report: miss += 1; print('MISSING', line)
for nm in ['OLD_ASSUMPTIONS_SQ_CAP', 'OLD_ASSUMPTIONS_F_CAP', 'TEXT_ASSUMPTIONS_SQ_CAP', 'TEXT_ASSUMPTIONS_F_CAP', 'MIG_ADDITIONAL400K', 'MIG_GDP_STOCK_CAP_INTERPRETATION', 'MIG_INITIAL_UNKNOWN', 'MIG_RETENTION_98', 'MIG_COMMON_ZERO_SQ', 'MIG_COMMON_ZERO_F']:
    r = ALL[nm][2055]; vals = [r['common_population_persons'], r['policy_population_increment_persons'], r['common_migration_net_flow'], r['policy_migration_accepted_net_flow'], r['foreign_stock_conditional_persons']]
    line = '|' + nm + '|' + '|'.join('未算定' if v is None else '%.3f' % v for v in vals) + '|' + ('未算定' if r['foreign_stock_population_ratio'] is None else '%.6f%%' % (100 * r['foreign_stock_population_ratio'])) + '|' + r['foreign_stock_ratio_status'] + '|'; chk += 1
    if line not in report: miss += 1; print('MISSING', line)
print('report table lines regenerated:', chk, 'missing from report:', miss)

sec('I. Regression: all 26 prior (db52249f) F-text paths replayed on the independent TX-structure engine')
# argv[6] = prior Text inputs json (db52249f). Prior parameters win over the new common inputs; prior overrides applied last.
pc = json.load(open(sys.argv[6], encoding='utf-8'))
prior_rows = {}
for r in csv.DictReader(open(sys.argv[3], encoding='utf-8')): prior_rows.setdefault(r['case'], {})[int(r['year'])] = r
import copy as _c
def prior_prepared(sp):
    p = {}
    for k in ('common_model', 'policy_inputs', 'exogenous_shocks'): p.update(_c.deepcopy(cfg[k]))
    p.update(_c.deepcopy(pc['parameters'])); p.update(_c.deepcopy(sp['overrides']))
    prof = _c.deepcopy(cfg['baseline_profiles']['TEXT_ASSUMPTIONS']); prof['migration_delivery_ramp_years'] = 1
    prof['elasticity'] = p['elasticity']
    p['climate_anchor'] = prof['climate_anchor']
    m = _c.deepcopy(cfg['common_model']['migration']); m.update(_c.deepcopy(cfg['policy_inputs']['migration']))
    m.update(common_annual_net_flow=0., enforcement_mode='GDP_STOCK_INTERPRETATION', F_flow_interpretation='TOTAL_TARGET',
             F_total_flow_reference=p.get('migration_annual', 400000.), foreign_initial_stock=p.get('foreign_stock_2026', 2000000.))
    p['migration'] = m
    return p, prof, m, True, list(sp.get('omit', []))
cols = ['real_gdp_trn', 'nominal_gdp_trn', 'tax_macro_trn', 'tax_diagnostic_trn', 'expenditure_diagnostic_trn', 'population_persons', 'I_policy_real_trn', 'capital_total_real_trn', 'fiscal_balance_partial_trn', 'household_disposable_nominal_trn', 'unmet_demand_real']
worst = {}; fails = []
for sp in pc['cases']:
    try:
        out = E.run(dict(id=sp['id'], profile='TEXT_ASSUMPTIONS', policy='F', supply_cap=True), prior_prepared(sp))
    except Exception as ex:
        fails.append((sp['id'], 'EXC ' + repr(ex)[:80])); continue
    mx = 0.
    for y in range(2026, 2056):
        for k in cols:
            if k not in prior_rows[sp['id']][y]: continue
            c = prior_rows[sp['id']][y][k]
            if c == '' or out[y][k] is None: continue
            b = float(c); mx = max(mx, abs(out[y][k] - b) / max(1., abs(b)))
    worst[sp['id']] = mx
    if mx > 1e-8: fails.append((sp['id'], mx))
print('prior paths replayed: %d ; paths with max rel diff <= 1e-8: %d ; max over all: %.3e' % (len(worst), sum(v <= 1e-8 for v in worst.values()), max(worst.values())))
print('not reproduced / error:', fails)

sec('J. Sensitivity (not calibration): initial foreign stock 2.0M (model) vs 4,281,026 (MOJ/ISA resident foreigners, end of June 2026, public release 2026-10-16)')
for ini in (2000000., 4281026.):
    for c in ('TEXT_ASSUMPTIONS_SQ_CAP', 'TEXT_ASSUMPTIONS_F_CAP', 'MIG_COMMON_ZERO_SQ'):
        s = dict(SPEC[c]); mo = dict(s.get('migration_override', {})); mo['foreign_initial_stock'] = ini; s['migration_override'] = mo
        o = E.run(s)
        y3 = next((y for y in o if o[y]['foreign_stock_population_ratio'] > .03), None); y5 = next((y for y in o if o[y]['foreign_stock_population_ratio'] > .05), None)
        print('initial stock %.0f | %-26s ratio2026 %.2f%% first>3%%: %s first>5%%: %s ratio2055 %.2f%% GDP-share 2035 %.2f%% 2055 %.2f%%' % (ini, c, 100 * o[2026]['foreign_stock_population_ratio'], y3, y5, 100 * o[2055]['foreign_stock_population_ratio'], 100 * o[2035]['foreign_gdp_contribution_ratio'], 100 * o[2055]['foreign_gdp_contribution_ratio']))

sec('K. Ceiling vs price channel on 2055 tax_diagnostic (F): real-ceiling effect = NEUTRAL - UNCAPPED ; price effect = CAP - NEUTRAL')
for pr in ('OLD_ASSUMPTIONS', 'TEXT_ASSUMPTIONS'):
    c_ = g(pr + '_F_CAP', 2055, 'tax_diagnostic_trn'); u_ = g(pr + '_F_UNCAPPED', 2055, 'tax_diagnostic_trn'); n_ = g(pr + '_F_CAP_PRICE_NEUTRAL', 2055, 'tax_diagnostic_trn')
    print(pr, 'ceiling-real %+.4f ; price %+.4f ; net CAP-UNCAPPED %+.4f' % (n_ - u_, c_ - n_, c_ - u_))
