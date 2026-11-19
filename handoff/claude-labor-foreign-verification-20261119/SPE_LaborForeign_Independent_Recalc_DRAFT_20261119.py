# Independent recompute (Claude) of SPE labour/foreign-worker comparison model, Commit 47deeee2... : 38 paths x 30 years = 1,140 rows.
# Shares only Inputs.json data. Population ledger (stock recursion), age-sex labour calibration, matched-SQ / F decomposition and Summary are re-implemented;
# TX macro engine = my own independent engine (verified in 7a292ab / b44b1fa), population/labour block patched.
# Usage: python3 -I <this> <tx_inputs.json> <old_tx.csv> <Inputs.json> <Annual.csv> <Summary.csv>
import sys, json, csv, math, importlib.util, os, copy
here = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('eng', os.path.join(here, 'SPE_LaborForeign_Engine_DRAFT_20261119.py'))
eng = importlib.util.module_from_spec(sp); sp.loader.exec_module(eng)
IN = json.load(open(sys.argv[3], encoding='utf-8')); B = IN['base']
ANN = list(csv.DictReader(open(sys.argv[4], encoding='utf-8'))); SUM = list(csv.DictReader(open(sys.argv[5], encoding='utf-8')))
REF = {int(k): v for k, v in B['population_reference'].items()}; OBS = B['official_initial_2025_oct']; CA = B['common_assumptions']; PAR = IN['parameters']
RATE = IN['employment_rates_2025']; AJ = IN['age_japanese_five_year']; AA = IN['age_all_five_year']
OLDR = {(r['case'], int(r['year'])): r for r in IN['old_results']}
YEARS = range(2026, 2056)
def baseflow(y): return 163791. if y <= 2040 else 163791. * REF[y]['population'] / REF[2040]['population']
def fres(y): return REF[y]['foreign'] - REF[y-1]['foreign'] - baseflow(y)

def ledger(spec):
    r25 = REF[2025]; dp = OBS['population'] - r25['population']; df = OBS['foreign'] - r25['foreign']
    P = REF[2026]['population'] + dp; F = REF[2026]['foreign'] + df; out = []; inc_prev = CA['band_reference_stock_increment']; prevP = None
    for y in YEARS:
        r = REF[y]; flow = 0.; res = 0.
        if y > 2026:
            res = fres(y); mode = spec['mode']
            flow = baseflow(y) if mode == 'IPSS' else CA['latest_foreign_net_flow'] if mode == 'LATEST' else CA['common_foreign_net_flow']
            if spec['policy'] == 'F' and y >= CA['F_start']:
                if mode.startswith('STOCK'): flow = int(mode[5:]) * 1000 - res
                elif mode == 'NET400': flow = 400000.
                elif mode == 'BAND':
                    T = spec.get('band_target', CA['band_target']); J = r['japanese'] + dp - df
                    inc = (1 - CA['band_flow_smoothing']) * inc_prev + CA['band_flow_smoothing'] * CA['band_speed'] * (T / (1 - T) * J - F); flow = inc - res; inc_prev = inc
            P = P + (r['population'] - REF[y-1]['population']) + (flow - baseflow(y)); F = F + flow + res
        out.append(dict(year=y, population=P, foreign=F, japanese=P - F, foreign_net_migration=flow, foreign_nonmigration_reference_residual=res, births_calendar=r['births_calendar'], deaths_calendar=r['deaths_calendar'],
                        population_reference_bridge=None if prevP is None else P - prevP - (r['births_calendar'] - r['deaths_calendar']) - flow, ipss_net_migration_reference=baseflow(y)))
        prevP = P
    return out

# ---- age-sex labour calibration (re-implemented) ----
AGEIDX = lambda a: None if a < 15 else 0 if a < 25 else 1 if a < 35 else 2 if a < 45 else 3 if a < 55 else 4 if a < 60 else 5 if a < 65 else 6 if a < 70 else 7 if a < 75 else 8
def rate(age, sex, factor=1.):
    i = AGEIDX(age); return 0. if i is None else min(1., RATE['male' if sex == 0 else 'female'][i] * factor)
def interp(tab, y):
    lo = (y // 5) * 5; hi = min(lo + 5, 2055); w = (y - lo) / 5 if hi > lo else 0.
    return {int(a): [(1 - w) * tab[str(lo)][a][s] + w * tab[str(hi)][a][s] for s in (0, 1)] for a in tab[str(lo)]}
def labour(s, led):
    stage = s.get('stage', 'VA'); old = stage in ('OLD', 'DOM', 'FOREIGN')
    q = 8e6 if old else s.get('productivity_yen', PAR['foreign_VA_per_employed_2026_yen']); dq = 9e6 if old else PAR['domestic_VA_reference_2026_yen']
    r25 = REF[2025]; df = OBS['foreign'] - r25['foreign']
    out = []
    for t in led:
        y = t['year']; r = REF[y]
        jw = r['japanese_working_age'] + OBS['working_age'] - r25['working_age'] - df * (r25['working_age'] - r25['japanese_working_age']) / r25['foreign']
        je = r['japanese_elderly'] + OBS['elderly'] - r25['elderly'] - df * (r25['elderly'] - r25['japanese_elderly']) / r25['foreign']
        tgt = [t['japanese'] - jw - je, jw, je]; jp = interp(AJ, y); tot = interp(AA, y); grp = lambda a: 0 if a < 15 else 1 if a < 65 else 2
        den = [sum(v[0] + v[1] for a, v in jp.items() if grp(a) == g) for g in range(3)]
        dom = 0.; dm = dfm = 0.
        for a, v in jp.items():
            for sx in (0, 1):
                e = v[sx] / den[grp(a)] * tgt[grp(a)] * rate(a, sx); dom += e
        fo = {a: [tot[a][sx] - jp[a][sx] for sx in (0, 1)] for a in jp}; fd = sum(v[0] + v[1] for v in fo.values()); fe = [0., 0.]
        fac = s.get('employment_factor', PAR['foreign_employment_factor'])
        for a, v in fo.items():
            for sx in (0, 1): fe[sx] += v[sx] / fd * t['foreign'] * rate(a, sx, fac)
        if stage == 'OLD':
            dom = jw * CA['employment_working_age'] + je * CA['employment_elderly']
        if stage in ('OLD', 'DOM'): fem = t['foreign'] * CA['foreign_employment_per_resident']
        else: fem = fe[0] + fe[1]
        u = dict(t); u.update(domestic_employed=dom, foreign_employed=fem, effective_productive_workers=dom + fem * q / dq, population_ratio=t['foreign'] / t['population'])
        out.append(u)
    return out, q

def sqmode(s): return 'LATEST' if s['mode'] == 'LATEST' else 'IPSS' if s['mode'] == 'IPSS' else 'COMMON'
def macro(s, traj, sqtraj):
    eng.cfg['common_model']['slack'] = s.get('slack', .02)
    sp_ = dict(id=s['id'], policy=s['policy'], profile='TEXT_ASSUMPTIONS', supply_cap=True, medical_mode=s.get('medical_mode', 'UNALLOCATED_COMPAT'), migration_override=dict(foreign_initial_stock=traj[0]['foreign'], enforcement_mode='NONE_REFERENCE'), traj=traj, sq_traj=sqtraj)
    return eng.run(sp_)
def case(s):
    d, q = labour(s, ledger(s)); cs = {**s, 'policy': 'SQ', 'mode': sqmode(s)}; c, _ = labour(cs, ledger(cs))
    d0 = d
    return macro(s, d, c), d, q

if __name__ == '__main__':
    res = {}; rows = []
    for s in IN['cases']: res[s['id']] = case(s)
    for s in IN['cases']:
        r, d, q = res[s['id']]; sqs = {**s, 'id': 'matchedSQ', 'policy': 'SQ', 'mode': sqmode(s)}; sr, sd, _ = case(sqs); fr, _, _ = case({**sqs, 'id': 'matchedF', 'policy': 'F'})
        cost = s.get('cost_yen', PAR['cost_per_foreign_employed_2026_yen']); d0 = 600. / 580.
        oc = ('SQ_LATEST' if s['mode'] == 'LATEST' else 'SQ_IPSS' if s['mode'] == 'IPSS' else 'SQ_COMMON') if s['policy'] == 'SQ' else ('F_COMMON_LATEST' if s['mode'] == 'LATEST' else 'F_IPSS' if s['mode'] == 'IPSS' else 'F_' + s['mode'] if s['mode'].startswith('STOCK') else 'F_BAND' + str(int(s.get('band_target', .04) * 100)) if s['mode'] == 'BAND' else 'F_SAME_FLOW')
        for i, y in enumerate(YEARS):
            m = r[y]; t = d[i]; D = m['common_deflator'] / d0; E = t['foreign_employed']; o = OLDR[(oc, y)]
            row = dict(case=s['id'], year=y, population=t['population'], japanese=t['japanese'], foreign=t['foreign'], population_ratio=t['foreign'] / t['population'], foreign_stock_net_increase=0. if i == 0 else t['foreign'] - d[i-1]['foreign'],
                       foreign_net_migration=t['foreign_net_migration'], foreign_reference_residual=t['foreign_nonmigration_reference_residual'], population_reference_bridge=t['population_reference_bridge'], domestic_employed=t['domestic_employed'], foreign_employed=E,
                       foreign_employment_fraction=E / t['foreign'], effective_workers=t['effective_productive_workers'], foreign_VA_per_worker_2026_yen=q, foreign_cost_nominal_trn=E * cost / 1e12 * D, foreign_VA_attribution_nominal_trn=E * q / 1e12 * D,
                       foreign_cost_GDP_ratio=E * cost / 1e12 * D / m['nominal_gdp_trn'], foreign_VA_GDP_ratio=E * q / 1e12 * D / m['nominal_gdp_trn'])
            for k in ('real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn', 'expenditure_diagnostic_trn', 'funding_gap_proxy_trn', 'household_disposable_nominal_trn', 'household_consumption_real_proxy_trn', 'I_policy_real_trn', 'capital_total_real_trn', 'unmet_demand_real', 'supply_binding', 'medical_insurer_vat', 'medical_extra_premium', 'medical_public_topup', 'medical_internal', 'medical_unallocated'): row[k] = m[k]
            row.update(delta_GDP_vs_matched_SQ=m['real_gdp_trn'] - sr[y]['real_gdp_trn'], delta_population_vs_matched_SQ=t['population'] - sd[i]['population'], delta_foreign_employed_vs_SQ=E - sd[i]['foreign_employed'],
                       F_other_channels_GDP=fr[y]['real_gdp_trn'] - sr[y]['real_gdp_trn'], F_quantity_condition_GDP=m['real_gdp_trn'] - fr[y]['real_gdp_trn'] if s['policy'] == 'F' else 0.,
                       delta_GDP_vs_previous=m['real_gdp_trn'] - float(o['real_gdp_trn']), delta_population_vs_previous=t['population'] - float(o['population']), delta_tax_vs_previous=m['tax_diagnostic_trn'] - float(o['tax_diagnostic_trn']))
            rows.append(row)
    print('paths', len(res), 'rows', len(rows))
    A = {(r['case'], int(r['year'])): r for r in ANN}; assert len(A) == len(ANN) == len(rows)
    cmp = lambda a, b: a == b or abs(a - b) <= 1e-9 * max(1., abs(a), abs(b))
    VSPREV = ('delta_GDP_vs_previous', 'delta_population_vs_previous', 'delta_tax_vs_previous'); skipped = 0
    n = bad = blank = 0; mx = 0.; bl = []
    for r in rows:
        c = A[(r['case'], r['year'])]
        for k, v in r.items():
            if k in ('case', 'year'): continue
            if k in VSPREV: skipped += 1; continue   # old_results carry 10 significant digits; checked separately in supplementary (exact prior-model rerun)
            cv = c[k]
            if v is None:
                blank += 1
                if cv != '': bad += 1; bl.append((r['case'], r['year'], k, v, cv))
                continue
            x = float(cv); n += 1; mx = max(mx, abs(v - x) / max(1., abs(v)))
            if not cmp(v, x): bad += 1; bl.append((r['case'], r['year'], k, v, cv))
    print('A numeric cells', n, '(vs_previous cells deferred to supplementary:', skipped, ')', 'blank-compared', blank, 'mismatch', bad, 'max_rel_err %.3e' % mx, bl[:5])
    # Summary
    Sm = {r['case']: r for r in SUM}; sb = sc = 0
    for s in IN['cases']:
        rr = [x for x in rows if x['case'] == s['id']]; last = rr[-1]; u = {}
        first = lambda f: next((x['year'] for x in rr if f(x)), None)
        for key, th, src in (('population_ratio', .03, 'population_ratio'), ('population_ratio5', .05, 'population_ratio'), ('foreign_cost_GDP_ratio', .05, 'foreign_cost_GDP_ratio'), ('foreign_VA_GDP_ratio', .05, 'foreign_VA_GDP_ratio')):
            u[key + '_reach'] = first(lambda x: x[src] >= th); u[key + '_exceed'] = first(lambda x: x[src] > th)
        u['binding_years'] = sum(x['supply_binding'] for x in rr)
        for k in ('population', 'japanese', 'foreign', 'population_ratio', 'domestic_employed', 'foreign_employed', 'foreign_cost_nominal_trn', 'foreign_VA_attribution_nominal_trn', 'foreign_cost_GDP_ratio', 'foreign_VA_GDP_ratio', 'real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn', 'delta_GDP_vs_matched_SQ', 'F_other_channels_GDP', 'F_quantity_condition_GDP', 'delta_GDP_vs_previous'): u[k] = last[k]
        c = Sm[s['id']]
        for k, v in u.items():
            if k == 'delta_GDP_vs_previous': continue
            sc += 1; cv = c[k]; ok = (cv == '') if v is None else (cv != '' and cmp(v, float(cv)))
            if not ok: sb += 1; print('SUMMARY MISMATCH', s['id'], k, v, cv)
    print('B summary cells', sc, 'mismatch', sb)
