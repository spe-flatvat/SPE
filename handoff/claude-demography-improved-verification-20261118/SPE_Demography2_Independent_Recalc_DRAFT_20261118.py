# Independent recompute (Claude) of SPE improved demography model (Commit d27b659f...) : 46 paths x 30 years = 1,380 rows.
# Shares ONLY the Inputs.json data with the model; population ledger, band rule, labour connection and summary are re-implemented.
# TX macro engine = my own earlier independent engine (verified vs the fixed TX model at 5d0c91d8), patched in its population/labour block.
# Usage: python3 -I <this> <tx_inputs.json> <old_tx.csv> <Inputs.json> <Annual.csv> <Summary.csv>
import sys, json, csv, math, importlib.util, os, copy
here = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('eng', os.path.join(here, 'SPE_Demography2_Engine_DRAFT_20261118.py'))
eng = importlib.util.module_from_spec(sp); sp.loader.exec_module(eng)
IN = json.load(open(sys.argv[3], encoding='utf-8'))
ANN = list(csv.DictReader(open(sys.argv[4], encoding='utf-8'))); SUM = list(csv.DictReader(open(sys.argv[5], encoding='utf-8')))
REF = {int(k): v for k, v in IN['population_reference'].items()}; OBS = IN['official_initial_2025_oct']; CA = IN['common_assumptions']
OLD = {}
for r in csv.DictReader(open(sys.argv[2], encoding='utf-8')):
    if r['case'] in ('TEXT_ASSUMPTIONS_F_CAP', 'TEXT_ASSUMPTIONS_SQ_CAP'): OLD[(r['case'].split('_')[2], int(r['year']))] = r
YEARS = range(2026, 2056)

def baseflow(y): return 163791. if y <= 2040 else 163791. * REF[y]['population'] / REF[2040]['population']
def fres(y): return REF[y]['foreign'] - REF[y-1]['foreign'] - baseflow(y)

def ledger(spec):
    """Stock recursion (not the cumulative-difference formula used by the model)."""
    anch = spec.get('anchor', 'OBS2025') != 'IPSS'; r25 = REF[2025]
    dp = OBS['population'] - r25['population'] if anch else 0.; df = OBS['foreign'] - r25['foreign'] if anch else 0.
    da = [(OBS[k] - r25[k]) if anch else 0. for k in ('under15', 'working_age', 'elderly')]
    sh25w = (r25['working_age'] - r25['japanese_working_age']) / r25['foreign']; sh25e = (r25['elderly'] - r25['japanese_elderly']) / r25['foreign']
    P = REF[2026]['population'] + dp; F = REF[2026]['foreign'] + df
    out = []; inc_prev = CA['band_reference_stock_increment']; prevP = prevF = None
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
                    want = CA['band_speed'] * (T / (1 - T) * J - F)       # F is the previous-year stock here
                    inc = (1 - CA['band_flow_smoothing']) * inc_prev + CA['band_flow_smoothing'] * want
                    flow = inc - res; inc_prev = inc
            P = P + (r['population'] - REF[y-1]['population']) + (flow - baseflow(y)); F = F + flow + res
        J = P - F
        sw = (r['working_age'] - r['japanese_working_age']) / r['foreign']; se = (r['elderly'] - r['japanese_elderly']) / r['foreign']
        jw = r['japanese_working_age'] + (da[1] - df * sh25w if anch else 0.); je = r['japanese_elderly'] + (da[2] - df * sh25e if anch else 0.)
        wa = jw + F * sw; el = je + F * se
        ef = F * spec.get('employment', CA['foreign_employment_per_resident'])
        ed = jw * CA['employment_working_age'] + je * CA['employment_elderly']
        eff = ed + ef * spec.get('productivity', CA['foreign_value_added_trn_per_worker_2026']) / CA['domestic_value_added_reference_trn']
        row = dict(year=y, population=P, foreign=F, japanese=J, under15=P - wa - el, working_age=wa, elderly=el, foreign_net_migration=flow, ipss_net_migration_reference=baseflow(y),
                   foreign_nonmigration_reference_residual=res, births_calendar=r['births_calendar'], deaths_calendar=r['deaths_calendar'], foreign_employed_conditional=ef,
                   domestic_employed_conditional=ed, effective_productive_workers=eff, ipss_population=r['population'], initial_population_offset=dp,
                   migration_cumulative_difference=P - r['population'] - dp,
                   population_reference_bridge=None if prevP is None else P - prevP - (r['births_calendar'] - r['deaths_calendar']) - flow)
        prevP = P; out.append(row)
    return out

def sq_mode(s): return 'LATEST' if s['mode'] == 'LATEST' else 'IPSS' if s['mode'] == 'IPSS' else 'COMMON'
def macro(s, traj, sqtraj):
    eng.cfg['common_model']['slack'] = s.get('slack', CA['slack'])
    spec = dict(id=s['id'], policy=s['policy'], profile='TEXT_ASSUMPTIONS', supply_cap=True, medical_mode=s.get('medical_mode', 'UNALLOCATED_COMPAT'),
                gdp_labor_mode=s.get('gdp_labor_mode', 'WEIGHTED_EMPLOYMENT'), migration_override=dict(foreign_initial_stock=traj[0]['foreign'], enforcement_mode='NONE_REFERENCE'), traj=traj, sq_traj=sqtraj)
    return eng.run(spec)

def case(s):
    d = ledger(s); cs = {**s, 'policy': 'SQ', 'mode': sq_mode(s)}; c = ledger(cs)
    return macro(s, d, c), d
res = {}; rows = []
for s in IN['cases']:
    r, d = case(s); res[s['id']] = (r, d)
for s in IN['cases']:
    r, d = res[s['id']]
    sqs = {**s, 'id': 'pairedSQ', 'policy': 'SQ', 'mode': sq_mode(s)}; sr, sd = case(sqs); fs_, _ = case({**sqs, 'id': 'pairedF', 'policy': 'F'})
    q = s.get('productivity', CA['foreign_value_added_trn_per_worker_2026']); d0 = IN['tx_inputs']['initial']['nominal_gdp'] / IN['tx_inputs']['initial']['real_gdp']
    for i, y in enumerate(YEARS):
        m = r[y]; dd = d[i]; o = OLD[(s['policy'], y)]; nomq = q * (m['common_deflator'] / d0)
        row = dict(case=s['id'], **dd)
        for k in ('real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn', 'expenditure_diagnostic_trn', 'funding_gap_proxy_trn', 'household_disposable_nominal_trn', 'household_consumption_real_proxy_trn', 'I_policy_real_trn', 'capital_total_real_trn', 'unmet_demand_real', 'price_pressure_proxy', 'supply_binding', 'medical_insurer_vat', 'medical_extra_premium', 'medical_public_topup', 'medical_internal', 'medical_unallocated'): row[k] = m[k]
        row['population_ratio'] = dd['foreign'] / dd['population']
        row['legacy_resident_gdp5_reference'] = dd['foreign'] * 8e-6 / (m['core_real_gdp_trn'] * m['common_deflator'])
        row['worker_va_attribution_nominal'] = dd['foreign_employed_conditional'] * nomq; row['worker_va_gdp_ratio'] = row['worker_va_attribution_nominal'] / m['nominal_gdp_trn']
        row['initial_foreign_va_included_not_added'] = d[0]['foreign_employed_conditional'] * q
        row['delta_employment_vs_SQ'] = dd['foreign_employed_conditional'] - sd[i]['foreign_employed_conditional']; row['delta_va_attribution_vs_SQ'] = row['delta_employment_vs_SQ'] * nomq
        row['delta_GDP_vs_old'] = m['real_gdp_trn'] - float(o['real_gdp_trn']); row['delta_population_vs_old'] = dd['population'] - float(o['population_persons']); row['delta_tax_vs_old'] = m['tax_diagnostic_trn'] - float(o['tax_diagnostic_trn'])
        row['delta_GDP_vs_matched_SQ'] = m['real_gdp_trn'] - sr[y]['real_gdp_trn']; row['F_nonmigration_GDP'] = fs_[y]['real_gdp_trn'] - sr[y]['real_gdp_trn']
        row['F_migration_GDP'] = m['real_gdp_trn'] - fs_[y]['real_gdp_trn'] if s['policy'] == 'F' else 0.
        rows.append(row)
print('paths', len(res), 'rows', len(rows))
# ---- A: Annual.csv cell-by-cell
A = {(r['case'], int(r['year'])): r for r in ANN}; assert len(A) == len(ANN) == len(rows)
def cmp(a, b, tol=1e-9): return a == b or abs(a - b) <= tol * max(1., abs(a), abs(b))
VSOLD = ('delta_GDP_vs_old', 'delta_population_vs_old', 'delta_tax_vs_old'); skipped = 0
n = bad = 0; mx = 0.; blanks = 0; badl = []
for r in rows:
    c = A[(r['case'], r['year'])]
    for k, v in r.items():
        if k in ('case', 'year'): continue
        if k in VSOLD: skipped += 1; continue   # old-model deltas: the embedded old CSV has only 10 significant digits; re-derived from the exact old engine in the supplementary script (A1)
        cv = c[k]
        if v is None:
            blanks += 1
            if cv != '': bad += 1; badl.append((r['case'], r['year'], k, v, cv))
            continue
        x = float(cv); n += 1; e = abs(v - x) / max(1., abs(v)); mx = max(mx, e)
        if not cmp(v, x): bad += 1; badl.append((r['case'], r['year'], k, v, cv))
print('A numeric cells', n, '(vs_old cells deferred to supplementary A1:', skipped, ')', 'blank-compared', blanks, 'mismatch', bad, 'max_rel_err %.3e' % mx, badl[:5])
# model-only columns that I do not rebuild
extra = [k for k in ANN[0] if k not in rows[0]]; print('csv columns not independently rebuilt:', extra)
# ---- B: Summary.csv
Sm = {r['case']: r for r in SUM}; sb = 0; sc = 0
for r in IN['cases']:
    s = r; rr = [x for x in rows if x['case'] == s['id']]; last = rr[-1]; u = {}
    def first(f): return next((x['year'] for x in rr if f(x)), None)
    for k, key in (('population_ratio', 'population_ratio'), ('population_ratio5', 'population_ratio'), ('worker_va_gdp_ratio', 'worker_va_gdp_ratio'), ('legacy_resident_gdp5_reference', 'legacy_resident_gdp5_reference')):
        t = .03 if k == 'population_ratio' else .05
        u[k + '_reach'] = first(lambda x: x[key] >= t); u[k + '_exceed'] = first(lambda x: x[key] > t)
    u['binding_years'] = sum(x['supply_binding'] for x in rr); u['max_ratio'] = max(x['population_ratio'] for x in rr); u['min_net_migration'] = min(x['foreign_net_migration'] for x in rr[1:])
    for k in ('population', 'foreign', 'population_ratio', 'foreign_employed_conditional', 'real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn', 'delta_GDP_vs_old', 'delta_GDP_vs_matched_SQ', 'F_nonmigration_GDP', 'F_migration_GDP', 'employment_fraction', 'value_added_per_worker_2026_yen'):
        if k in last: u[k] = last[k]
    u['employment_fraction'] = s.get('employment', CA['foreign_employment_per_resident']); u['value_added_per_worker_2026_yen'] = s.get('productivity', CA['foreign_value_added_trn_per_worker_2026']) * 1e12
    c = Sm[s['id']]
    for k, v in u.items():
        if k == 'delta_GDP_vs_old': continue
        sc += 1; cv = c[k]
        ok = (cv == '') if v is None else (cv != '' and cmp(v, float(cv)))
        if not ok: sb += 1; print('SUMMARY MISMATCH', s['id'], k, v, cv)
print('B summary cells', sc, 'mismatch', sb)
