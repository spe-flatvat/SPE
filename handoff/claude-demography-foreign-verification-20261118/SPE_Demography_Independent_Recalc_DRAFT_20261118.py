# Independent verification of handoff/demography-foreign-research-20261118 (commit 154a61c2) by Claude. Read-only.
# Rebuilds the 96 sensitivity paths with an independently written engine (SPE_F_TX_Independent_Recalc_DRAFT_20261118.py, the TX engine
# re-implemented by Claude); the ChatGPT model/Analyze.py are NOT imported. Also checks statistics identities and the GDP-5% / 400k readings.
# Usage: python3 -I this.py <TX Inputs.json> <TX Annual.csv> <Sensitivity_Annual.csv> <Sensitivity_Summary.csv> <Stock400_Ledger.csv> <Official_Statistics.csv> <Research_and_Owner_Decisions.md>
import sys, os, csv, json, copy, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
TXI, TXA, SANN, SSUM, SLED, STAT, MD = sys.argv[1:8]
sys.argv = [sys.argv[0], TXI, TXA]
import SPE_F_TX_Independent_Recalc_DRAFT_20261118 as E
def sec(t): print('\n== ' + t)
stats = list(csv.DictReader(open(STAT, encoding='utf-8')))
def stat(m, y, scope=None):
    for r in stats:
        if r['measure'] == m and r['year'] == str(y) and (scope is None or r['scope'] == scope) and r['value'] != '': return float(r['value'])
    raise KeyError((m, y))

# ---------------------------------------------------------------- A. rebuild 96 cases
start = stat('foreign_resident_stock', 2025); latest = stat('foreign_resident_stock', 2026)
recent = sum(stat('foreign_net_migration', y) for y in (2023, 2024, 2025)) / 3; last = stat('foreign_net_migration', 2025)
def mk(name, stock, flow, slack, pol, cap=True, mode='UNALLOCATED_COMPAT', fs=2030, ret=1., part=.8):
    return dict(id=name, profile='TEXT_ASSUMPTIONS', policy=pol, supply_cap=cap, medical_mode=mode, policy_override=dict(slack=slack, foreign_labor_participation=part),
                migration_override=dict(foreign_initial_stock=stock, common_annual_net_flow=flow, flow_start=fs, foreign_stock_net_retention=ret, enforcement_mode='NONE_REFERENCE'),
                _meta=dict(initial_stock=stock, common_flow=flow, slack=slack, policy=pol, cap=int(cap), medical_mode=mode, flow_start=fs, retention=ret, participation=part))
cases = []
for sn, st in [('LEGACY', 2000000), ('END25', start), ('JUN26', latest)]:
    for fn, fl in [('AVG23_25', recent), ('LAST25', last), ('LEGACY357', 357000), ('NET400', 400000)]:
        for sl in (.02, .05, .10):
            for pol in ('SQ', 'F'): cases.append(mk('%s_%s_S%02d_%s' % (sn, fn, round(sl * 100), pol), st, fl, sl, pol))
for sn, st in [('LEGACY', 2000000), ('END25', start)]:
    for pol in ('SQ', 'F'): cases.append(mk('ANNUAL400_2027_%s_%s' % (sn, pol), st, 400000, .02, pol, fs=2027))
for tag, ret, part in [('RET98', .98, .8), ('LAB60', 1., .6), ('LAB70', 1., .7)]:
    for pol in ('SQ', 'F'): cases.append(mk('%s_%s' % (tag, pol), start, last, .02, pol, ret=ret, part=part))
for mode in ('PREMIUM', 'PUBLIC', 'INTERNAL'):
    for sl in (.02, .05, .10): cases.append(mk('MED_%s_S%02d' % (mode, round(sl * 100)), start, last, sl, 'F', mode=mode))
    cases.append(mk('MED_%s_UNCAPPED' % mode, start, last, .02, 'F', cap=False, mode=mode))
for pol in ('SQ', 'F'): cases.append(mk('UNCAPPED_' + pol, start, last, .02, pol, cap=False))
ALL = {c['id']: E.run(c) for c in cases}
sec('A1. case set and annual rows vs Sensitivity_Annual.csv')
rows = list(csv.DictReader(open(SANN, encoding='utf-8'))); names = {r['case'] for r in rows}
print('independent cases', len(cases), '| csv cases', len(names), '| csv rows', len(rows), '| name sets equal', names == {c['id'] for c in cases})
NUM = ['population_persons', 'births_persons', 'deaths_persons', 'labor_force_population_proxy', 'foreign_stock_conditional_persons', 'foreign_stock_population_ratio', 'foreign_gdp_contribution_ratio', 'common_migration_net_flow', 'policy_migration_accepted_net_flow', 'total_migration_net_flow', 'real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn', 'expenditure_diagnostic_trn', 'household_disposable_nominal_trn', 'household_consumption_real_proxy_trn', 'I_policy_real_trn', 'capital_total_real_trn', 'supply_binding', 'unmet_demand_real', 'price_pressure_proxy', 'medical_insurer_vat', 'medical_extra_premium', 'medical_public_topup', 'medical_internal', 'medical_unallocated']
spec = {c['id']: c for c in cases}; n = 0; mx = 0.; bad = []
for r in rows:
    c = spec[r['case']]; o = ALL[r['case']][int(r['year'])]
    for k, v in c['_meta'].items():
        a = float(r[k]) if k not in ('policy', 'medical_mode') else r[k]
        if (a != v) if isinstance(a, str) else abs(a - v) > 1e-6 * max(1, abs(v)): bad.append((r['case'], 'meta', k, a, v))
    for k in NUM:
        v = o[k]; cc = r[k]
        if v is None or cc == '':
            if not (v is None and cc == ''): bad.append((r['case'], r['year'], k, v, cc))
            continue
        a = float(cc); d = abs(a - v) / max(1., abs(v)); mx = max(mx, d); n += 1
        if d > 1e-9: bad.append((r['case'], r['year'], k, v, a))
print('numeric cells compared', n, 'max rel diff %.3e' % mx, 'mismatches', len(bad), bad[:6])

sec('A2. thresholds (reach = >=, exceed = >) and 2055 end values vs Sensitivity_Summary.csv')
summ = {r['case']: r for r in csv.DictReader(open(SSUM, encoding='utf-8'))}
def yr(rs, key, t, op):
    for y in sorted(rs):
        v = rs[y][key]
        if v is not None and (v >= t if op == 'reach' else v > t): return str(y)
    return ''
bad = []; n = 0
for cid, rs in ALL.items():
    s = summ[cid]
    for label, key, t in [('pop3', 'foreign_stock_population_ratio', .03), ('pop5', 'foreign_stock_population_ratio', .05), ('gdp5_reference', 'foreign_gdp_contribution_ratio', .05)]:
        for op in ('reach', 'exceed'):
            n += 1
            if yr(rs, key, t, op) != s[label + '_' + op]: bad.append((cid, label, op, yr(rs, key, t, op), s[label + '_' + op]))
    for k in NUM:
        v = rs[2055][k]; c = s['end2055_' + k]; n += 1
        if v is None or c == '':
            if not (v is None and c == ''): bad.append((cid, k, v, c))
        elif abs(float(c) - v) / max(1., abs(v)) > 1e-9: bad.append((cid, k, v, c))
    n += 2
    if sum(rs[y]['supply_binding'] for y in rs) != int(s['binding_years']): bad.append((cid, 'binding'))
    if abs(max(rs[y]['unmet_demand_real'] for y in rs) - float(s['max_unmet_demand'])) > 1e-8: bad.append((cid, 'unmet'))
print('summary cells compared', n, 'mismatches', len(bad), bad[:6])

sec('A3. Stock400 ledger: S(y)=S(2026)+400000*(y-2026); denominator = SQ population with 400k net migration from 2027')
led = list(csv.DictReader(open(SLED, encoding='utf-8'))); bad = []; first5 = {}
sq = ALL['ANNUAL400_2027_END25_SQ']
for r in led:
    nm = r['case'].split('_')[1]; st = {'LEGACY': 2000000, 'END25': start, 'JUN26': latest}[nm]; y = int(r['year']); S = st + 400000 * (y - 2026)
    if abs(float(r['foreign_stock']) - S) > 1e-6 or abs(float(r['population_denominator']) - sq[y]['population_persons']) > 1e-9 * sq[y]['population_persons'] or abs(float(r['population_ratio']) - S / sq[y]['population_persons']) > 1e-9: bad.append((r['case'], y))  # CSV keeps 10 significant digits
    if S / sq[y]['population_persons'] > .05 and nm not in first5: first5[nm] = y
print('ledger rows', len(led), 'mismatches', len(bad), '| first year >5%:', first5, '| 2055 END25 stock %.0f ratio %.3f%%' % (start + 400000 * 29, 100 * (start + 400000 * 29) / sq[2055]['population_persons']))
print('independent engine ANNUAL400_2027_END25_SQ stock = ledger stock for all years:', all(abs(sq[y]['foreign_stock_conditional_persons'] - (start + 400000 * (y - 2026))) < 1e-6 for y in sq))
print('population denominator independent of initial foreign stock (END25 vs LEGACY SQ):', all(abs(ALL['ANNUAL400_2027_END25_SQ'][y]['population_persons'] - ALL['ANNUAL400_2027_LEGACY_SQ'][y]['population_persons']) < 1e-6 for y in sq))

# ---------------------------------------------------------------- B. statistics
sec('B1. Official_Statistics.csv internal identities (2020-2025)')
bad = []
for y in range(2020, 2026):
    tot = stat('population_total', y, 'usual_residents_all'); jp = stat('population_japanese', y); fo = stat('population_foreign', y)
    if abs(tot - jp - fo) > 0: bad.append(('total=jp+foreign', y, tot - jp - fo))
    nm = stat('foreign_net_migration', y); nat = stat('foreign_natural_change', y); nc = stat('foreign_net_nationality_change', y)
    if abs(stat('foreign_births', y) - stat('foreign_deaths', y) - nat) > 0: bad.append(('foreign natural', y))
    if y > 2020:
        d = stat('population_foreign', y) - stat('population_foreign', y - 1)
        if abs(d - (nm + nat + nc)) > 0: bad.append(('foreign stock accounting (pop-estimate basis)', y, d, nm + nat + nc, d - (nm + nat + nc)))
    u15 = None
    try: u15 = stat('under15', y); w = stat('age15_64', y); o65 = stat('age65plus', y)
    except KeyError: pass
    if u15 is not None and abs(u15 + w + o65 - tot) > 2000: bad.append(('age sum', y, u15 + w + o65 - tot))
print('violations', bad)
print('2025: net migration + natural + nationality =', 327557 + 13835 - 8218, '(report: 333,174 = population_foreign 2025 - 2024:', stat('population_foreign', 2025) - stat('population_foreign', 2024), ')')
print('resident-stock yoy: 2025 %.0f (report 356,418), 2026H1 %.0f (report 155,631); workers yoy 2025 %.0f (report 268,450)' % (stat('foreign_resident_stock', 2025) - stat('foreign_resident_stock', 2024), stat('foreign_resident_stock', 2026) - stat('foreign_resident_stock', 2025), stat('foreign_workers_notified', 2025) - stat('foreign_workers_notified', 2024)))
print('avg 2023-25 net migration %.3f ; 2025 vs 357000: %+.0f ; avg vs 357000: %+.3f' % (recent, 357000 - last, 357000 - recent))
print('net migration needed for stock +400,000 using 2025 residual (natural+nationality=%+d): %d' % (13835 - 8218, 400000 - (13835 - 8218)))
sec('B2. table in Research_and_Owner_Decisions.md section A vs CSV')
md = open(MD, encoding='utf-8').read(); bad = []; seen = 0
for line in md.splitlines():
    m = re.match(r'\|(20\d\d)\|([\d,]+)\|([\d,]+)\|([\d,]+)\|([\d,]+)\|(-?[\d,]+)\|([\d,]+)／([\d,]+)\|', line)
    if not m: continue
    y = int(m.group(1)); v = [int(x.replace(',', '')) for x in m.groups()[1:]]; seen += 1
    ref = [stat('population_total', y, 'usual_residents_all'), stat('population_foreign', y), stat('foreign_resident_stock', y), stat('foreign_workers_notified', y), stat('foreign_net_migration', y)]
    for a, b in zip(v[:5], ref):
        if a != int(b): bad.append((y, a, b))
print('table rows', seen, 'mismatches', bad)
print('2026 values: Oct provisional %.0f, May final %.0f, foreign(May) %.0f, 2026-06 resident %.0f' % (122690000, 122812000, 3974314, latest))
print('foreign share definitions 2026: pop-estimate 3,974,314/122,812,000 = %.3f%% ; resident 4,281,026/122,812,000 = %.3f%% ; model END25 4,125,395/121.5M = %.3f%% ; model JUN26 = %.3f%%' % (100 * 3974314 / 122812000, 100 * 4281026 / 122812000, 100 * start / 121.5e6, 100 * latest / 121.5e6))

# ---------------------------------------------------------------- C. GDP-5% reference formula
sec('C. GDP-5% reference: stock x 8e-6 trn / core nominal GDP (2026 core nominal = 600 trn)')
va = 8e-6; N0 = E.A['nominal_gdp']
for lab, st in [('LEGACY 2.0M', 2e6), ('END25 resident 4,125,395', start), ('JUN26 resident 4,281,026', latest), ('END25 workers notified 2,571,037', stat('foreign_workers_notified', 2025))]:
    print('  %-34s initial GDP-share %.2f%%' % (lab, 100 * st * va / N0))
print('  implied employed persons behind 8M yen/person: %.1f million ; actual employed 2025 (Labour Force Survey): 68.28 million -> GDP per employed person %.2f M yen' % (N0 / va / 1e6, N0 / 68.28))
w = stat('foreign_workers_notified', 2025); print('  workers / residents (2025) = %.3f ; foreign workers / employed = %.2f%%' % (w / start, 100 * w / 68.28e6))
print('  END25 initial, workers-only (ratio x %.3f): GDP-share %.2f%%' % (w / start, 100 * w / start * start * va / N0))
for cid in ('END25_LAST25_S02_SQ', 'END25_LAST25_S02_F', 'LEGACY_LEGACY357_S02_SQ', 'ANNUAL400_2027_END25_SQ'):
    rs = ALL[cid]; k = w / start
    y5 = next((y for y in rs if rs[y]['foreign_gdp_contribution_ratio'] > .05), None); yw = next((y for y in rs if rs[y]['foreign_gdp_contribution_ratio'] * k > .05), None)
    print('  %-26s first >5%% as defined: %s ; if only workers (x%.3f of stock) counted: %s ; 2055 share as defined %.2f%% / workers-only %.2f%%' % (cid, y5, k, yw, 100 * rs[2055]['foreign_gdp_contribution_ratio'], 100 * k * rs[2055]['foreign_gdp_contribution_ratio']))

# ---------------------------------------------------------------- D. reproducibility of the stated comparisons
sec('D. Stated comparisons (Research_and_Owner_Decisions.md) re-derived')
g = lambda c, y, k: ALL[c][y][k]
print('initial-stock-only change leaves real GDP unchanged (LEGACY/END25/JUN26 x same flow/slack/policy): ', all(abs(g('%s_%s_S%02d_%s' % (s_, f_, sl, p_), y, 'real_gdp_trn') - g('LEGACY_%s_S%02d_%s' % (f_, sl, p_), y, 'real_gdp_trn')) < 1e-9 for s_ in ('END25', 'JUN26') for f_ in ('AVG23_25', 'LAST25', 'LEGACY357', 'NET400') for sl in (2, 5, 10) for p_ in ('SQ', 'F') for y in range(2026, 2056)))
print('F paths identical across the four common-flow levels (same total 400k): ', all(abs(g('END25_%s_S02_F' % f_, y, 'real_gdp_trn') - g('END25_LAST25_S02_F', y, 'real_gdp_trn')) < 1e-9 and abs(g('END25_%s_S02_F' % f_, y, 'foreign_stock_conditional_persons') - g('END25_LAST25_S02_F', y, 'foreign_stock_conditional_persons')) < 1e-6 for f_ in ('AVG23_25', 'LEGACY357', 'NET400') for y in range(2026, 2056)))
for f_ in ('LEGACY357', 'AVG23_25', 'LAST25', 'NET400'):
    d = g('END25_%s_S02_F' % f_, 2055, 'real_gdp_trn') - g('END25_%s_S02_SQ' % f_, 2055, 'real_gdp_trn'); ex = (400000 - min(400000, {'LEGACY357': 357000, 'AVG23_25': recent, 'LAST25': last, 'NET400': 400000}[f_])) * 26
    print('  F-SQ real GDP 2055, common flow %-9s: %.3f  (F additional persons %.0f)' % (f_, d, ex))
print('  => non-migration F channels (NET400, F additional = 0): %.3f ; migration part at LEGACY357: %.3f per %.3f M extra persons' % (g('END25_NET400_S02_F', 2055, 'real_gdp_trn') - g('END25_NET400_S02_SQ', 2055, 'real_gdp_trn'), (g('END25_LEGACY357_S02_F', 2055, 'real_gdp_trn') - g('END25_LEGACY357_S02_SQ', 2055, 'real_gdp_trn')) - (g('END25_NET400_S02_F', 2055, 'real_gdp_trn') - g('END25_NET400_S02_SQ', 2055, 'real_gdp_trn')), 1.118))
for s in (2, 5, 10): print('  slack %d%%: F binding years %d, F 2055 GDP %.6f tax %.6f' % (s, sum(ALL['END25_LAST25_S%02d_F' % s][y]['supply_binding'] for y in ALL['END25_LAST25_S%02d_F' % s]), g('END25_LAST25_S%02d_F' % s, 2055, 'real_gdp_trn'), g('END25_LAST25_S%02d_F' % s, 2055, 'tax_diagnostic_trn')))
print('  slack5 == slack10 == UNCAPPED_F in every year (real GDP, tax):', all(abs(g('END25_LAST25_S05_F', y, k) - g('UNCAPPED_F', y, k)) < 1e-9 and abs(g('END25_LAST25_S10_F', y, k) - g('UNCAPPED_F', y, k)) < 1e-9 for y in range(2026, 2056) for k in ('real_gdp_trn', 'tax_diagnostic_trn')))
print('  MED_PREMIUM_S05 vs UNALLOCATED(S05) 2055 GDP diff: %+.6f ; PUBLIC/INTERNAL: %+.6f / %+.6f ; at S02 (capped): %+.6f' % (g('MED_PREMIUM_S05', 2055, 'real_gdp_trn') - g('END25_LAST25_S05_F', 2055, 'real_gdp_trn'), g('MED_PUBLIC_S05', 2055, 'real_gdp_trn') - g('END25_LAST25_S05_F', 2055, 'real_gdp_trn'), g('MED_INTERNAL_S05', 2055, 'real_gdp_trn') - g('END25_LAST25_S05_F', 2055, 'real_gdp_trn'), g('MED_PREMIUM_S02', 2055, 'real_gdp_trn') - g('END25_LAST25_S02_F', 2055, 'real_gdp_trn')))
for t in ('RET98', 'LAB60', 'LAB70'):
    print('  %-6s F 2055 GDP %.3f (base %.3f, diff %+.3f) ; SQ %.3f (diff %+.3f) ; F-SQ %.3f ; stock F %.0f ; pop F %.0f' % (t, g(t + '_F', 2055, 'real_gdp_trn'), g('END25_LAST25_S02_F', 2055, 'real_gdp_trn'), g(t + '_F', 2055, 'real_gdp_trn') - g('END25_LAST25_S02_F', 2055, 'real_gdp_trn'), g(t + '_SQ', 2055, 'real_gdp_trn'), g(t + '_SQ', 2055, 'real_gdp_trn') - g('END25_LAST25_S02_SQ', 2055, 'real_gdp_trn'), g(t + '_F', 2055, 'real_gdp_trn') - g(t + '_SQ', 2055, 'real_gdp_trn'), g(t + '_F', 2055, 'foreign_stock_conditional_persons'), g(t + '_F', 2055, 'population_persons')))
f = ALL['END25_LAST25_S02_F'][2055]; print('  F 2055 pop %.0f births %.0f deaths %.0f ; IPSS 2055 100,508,000 -> gap %.0f' % (f['population_persons'], f['births_persons'], f['deaths_persons'], 100508000 - f['population_persons']))

# ---------------------------------------------------------------- E. timing: model has zero common inflow 2027-2029
sec('E. Timing sensitivity (not in the ChatGPT set; independent): actual-level common inflow already from 2027 instead of 2030')
for lab, fl, fs_ in [('LAST25 from 2030 (set)', last, 2030), ('LAST25 from 2027', last, 2027), ('LEGACY357 from 2027', 357000, 2027)]:
    for pol in ('SQ', 'F'):
        rs = E.run(mk('x', start, fl, .02, pol, fs=fs_)); y3 = next((y for y in rs if rs[y]['foreign_stock_population_ratio'] > .03), None); y5 = next((y for y in rs if rs[y]['foreign_stock_population_ratio'] > .05), None)
        print('  END25 %-24s %-2s: >3%% %s  >5%% %s  stock2030 %.0f  ratio2030 %.2f%%  ratio2055 %.2f%%' % (lab, pol, y3, y5, rs[2030]['foreign_stock_conditional_persons'], 100 * rs[2030]['foreign_stock_population_ratio'], 100 * rs[2055]['foreign_stock_population_ratio']))

# ---------------------------------------------------------------- F. numbers quoted in the report tables
sec('F. Report tables (Research_and_Owner_Decisions.md) vs independent engine')
fl = lambda s: float(s.replace(',', '').replace('%', ''))
bad = []; n = 0
lines = md.splitlines()
def rows_of(header):
    i = next(k for k, l in enumerate(lines) if l.startswith(header)); out = []
    for l in lines[i + 2:]:
        if not l.startswith('|'): break
        out.append([x.strip() for x in l.strip('|').split('|')])
    return out
for r in rows_of('|ケース|人口（万人）|外国人（万人）'):
    o = ALL[r[0]][2055]; ref = [o['population_persons'] / 1e4, o['foreign_stock_conditional_persons'] / 1e4, 100 * o['foreign_stock_population_ratio'], o['real_gdp_trn'], o['tax_diagnostic_trn']]
    for a, b in zip([fl(x) for x in r[1:6]], ref):
        n += 1
        if abs(a - b) > 0.0006 * max(1, abs(b)) / 1: bad.append((r[0], a, b))
    base = r[0].rsplit('_', 1)[0]; sqid = base + '_SQ'; fid = base + '_F'
    n += 1
    if abs(fl(r[6]) - (ALL[fid][2055]['real_gdp_trn'] - ALL[sqid][2055]['real_gdp_trn'])) > 0.0006: bad.append((r[0], 'F-SQ'))
for r in rows_of('|ケース|人口3%超|人口5%超'):
    rs = ALL[r[0]]
    for lab, key, t, cell in [('p3', 'foreign_stock_population_ratio', .03, r[1]), ('p5', 'foreign_stock_population_ratio', .05, r[2]), ('g5', 'foreign_gdp_contribution_ratio', .05, r[3])]:
        n += 1
        if yr(rs, key, t, 'exceed') != cell: bad.append((r[0], lab, yr(rs, key, t, 'exceed'), cell))
for r in rows_of('|年|F／SQ実質GDP兆円'):
    y = int(r[0]); F_ = ALL['END25_LAST25_S02_F'][y]; S_ = ALL['END25_LAST25_S02_SQ'][y]
    for cell, (a, b) in zip(r[1:4], [('real_gdp_trn',) * 2, ('nominal_gdp_trn',) * 2, ('population_persons',) * 2]):
        x, z_ = [fl(t) for t in cell.split('／')]; scale = 1e4 if a == 'population_persons' else 1
        n += 1
        if abs(x - F_[a] / scale) > 0.0006 * max(1, x) or abs(z_ - S_[b] / scale) > 0.0006 * max(1, z_): bad.append((y, a, cell))
    n += 1
    if abs(fl(r[4]) - 100 * F_['foreign_stock_population_ratio']) > 0.0006: bad.append((y, 'ratio'))
for r in rows_of('|Fケース|拘束年数'):
    rs = ALL[r[0]]; n += 3
    if int(r[1]) != sum(rs[y]['supply_binding'] for y in rs) or abs(fl(r[2]) - max(rs[y]['unmet_demand_real'] for y in rs)) > 1e-5 or abs(fl(r[3]) - rs[2055]['real_gdp_trn']) > 1e-5: bad.append((r[0], 'slack table'))
print('quoted table cells compared', n, 'mismatches', len(bad), bad[:8])

# ---------------------------------------------------------------- G. initial-stock definition sensitivity (population-estimate basis)
sec('G. Initial stock on population-estimate basis (foreign usual residents) vs residence-status basis; common flow LAST25 from 2030 (as in the set)')
for lab, st in [('model 2.0M', 2000000.), ('pop-estimate 2025-10 (3,839,332)', stat('population_foreign', 2025)), ('pop-estimate 2026-05 (3,974,314)', stat('population_foreign', 2026)), ('resident END25 (4,125,395)', start), ('resident JUN26 (4,281,026)', latest)]:
    for pol in ('SQ', 'F'):
        rs = E.run(mk('x', st, last, .02, pol)); y3 = next((y for y in rs if rs[y]['foreign_stock_population_ratio'] > .03), None); y5 = next((y for y in rs if rs[y]['foreign_stock_population_ratio'] > .05), None)
        print('  %-36s %-2s ratio2026 %.2f%% >3%%: %s >5%%: %s ratio2055 %.2f%%' % (lab, pol, 100 * rs[2026]['foreign_stock_population_ratio'], y3, y5, 100 * rs[2055]['foreign_stock_population_ratio']))

# ---------------------------------------------------------------- H. what flow is compatible with 3-5% inside the model's own demography?
sec('H. Zero-inflow and break-even reading (model denominators; initial stock = resident END25)')
rs = E.run(mk('x', start, 0., .02, 'SQ')); y5 = next((y for y in rs if rs[y]['foreign_stock_population_ratio'] > .05), None)
print('  END25, common net flow 0, SQ: ratio 2026 %.2f%% 2035 %.2f%% 2045 %.2f%% 2055 %.2f%% ; first >5%%: %s ; population 2055 %.0f' % (100 * rs[2026]['foreign_stock_population_ratio'], 100 * rs[2035]['foreign_stock_population_ratio'], 100 * rs[2045]['foreign_stock_population_ratio'], 100 * rs[2055]['foreign_stock_population_ratio'], y5, rs[2055]['population_persons']))
def ratio2055(flow_const, st=start):
    r = E.run(mk('x', st, flow_const, .02, 'SQ', fs=2027)); return r[2055]['foreign_stock_population_ratio']
lo, hi = 0., 400000.
for _ in range(60):
    mid = (lo + hi) / 2
    if ratio2055(mid) > .05: hi = mid
    else: lo = mid
print('  constant common net inflow from 2027 that gives exactly 5.00%% in 2055 (END25 start): %.0f per year (negative = net outflow needed: %s)' % (lo, 'yes' if lo < 1 else 'no'))
print('  2055 ratio with 0 inflow from 2027: %.2f%% ; with 100,000/yr: %.2f%% ; with 327,557/yr: %.2f%%' % (100 * ratio2055(0.), 100 * ratio2055(100000.), 100 * ratio2055(last)))
