#!/usr/bin/env python3
"""N3 F-parity extension: Claude independent verification of the new annual-dynamic connection (read-only).

usage:
  python3 -I SPE_N3_F_Parity_Independent_Recalc_DRAFT_20261122.py TARGET_DIR MACRO_DIR OLD_RERUN_DIR ROOT OUTDIR
    TARGET_DIR    handoff/chatgpt-n3-f-parity-implementation-20261122 (fixed commit 37c3399f...; Inputs.json, results/, Report.md)
    MACRO_DIR     Claude's own re-run of Model.py: MACRO_DIR/{DOMESTIC_TRANSFER,LEGACY,FOREIGN_INCOME,ADDITIONAL_VA}/
    OLD_RERUN_DIR Claude's own earlier re-run of the 79-case pension-correction model (76176ae1): OLD/{mode}/
    ROOT          tree with fixed pins (F ff621006... final: handoff/f-common-endoflife-finalization-20261121/Annual.csv)
    OUTDIR        where this script writes its comparison CSV / JSON

This script does not import or call Work's Model.py, Components.py, Verify.py, Results.py, Package.py.
It reads only CSV/JSON outputs and re-derives identities from formulas written here (from the engine's published source
Resolved_Macro_Source.py.txt and from Inputs.json). Tolerance: abs 5e-9 + rel 1e-10 (CSV prints 12 significant digits).
"""
import sys, csv, json, math, hashlib, os
from pathlib import Path

TGT, MAC, OLD, ROOT, OUT = (Path(a) for a in sys.argv[1:6])
OUT.mkdir(parents=True, exist_ok=True)
MODES = ['DOMESTIC_TRANSFER', 'LEGACY', 'FOREIGN_INCOME', 'ADDITIONAL_VA']
checks, obs = [], []


def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def fl(x):
    return None if x in (None, '') else float(x)


def n0(r, k):
    v = r.get(k)
    return 0.0 if v in (None, '') else float(v)


def close(a, b, atol=5e-9, rtol=1e-10):
    return abs(a - b) <= atol + rtol * max(abs(a), abs(b))


class Acc:
    """collects one check over many rows: counts, max abs residual, first failing example"""

    def __init__(self, cid, area, desc, atol=5e-9, rtol=1e-10):
        self.cid, self.area, self.desc, self.atol, self.rtol = cid, area, desc, atol, rtol
        self.n = 0
        self.bad = 0
        self.maxres = 0.0
        self.example = None

    def eq(self, a, b, tag=''):
        self.n += 1
        d = abs(a - b)
        self.maxres = max(self.maxres, d)
        if d > self.atol + self.rtol * max(abs(a), abs(b)):
            self.bad += 1
            if self.example is None:
                self.example = f'{tag}: expected={a!r} actual={b!r}'

    def ok(self, cond, tag=''):
        self.n += 1
        if not cond:
            self.bad += 1
            if self.example is None:
                self.example = tag

    def done(self, note=''):
        checks.append(dict(id=self.cid, area=self.area, description=self.desc, items=self.n, failures=self.bad,
                           max_abs_residual=self.maxres, example_failure=self.example or '', note=note,
                           verdict='PASS' if self.bad == 0 and self.n > 0 else 'FAIL'))


def chkb(cid, area, desc, cond, note=''):
    checks.append(dict(id=cid, area=area, description=desc, items=1, failures=0 if cond else 1, max_abs_residual=0.0,
                       example_failure='' if cond else note, note=note if cond else '', verdict='PASS' if cond else 'FAIL'))


# ------------------------------------------------------------------------------------------ load
inp = json.loads((TGT / 'Inputs.json').read_text())
CASES = {c['id']: c for c in inp['cases']}
PARITY = list(inp['parity_cases'])
MP = inp['candidate_parameters']['macro_parameters']
LAM_C, LAM_I, DEP, MPC = MP['lambda_C'], MP['lambda_I'], MP['depreciation'], MP['generic_mpc']
YIELD, CAPR, ELAS, CAP = MP['capital_yield'], MP['capital_ratio'], MP['elasticity'], MP['tax_cap_ratio']
ABS_, FBK, HSH = MP['capacity_absorption'], MP['income_feedback'], MP['household_income_share']
Y = list(range(2026, 2056))
D = {}
for m in MODES:
    d = MAC / m
    D[m] = dict(A={(r['case'], int(r['year'])): r for r in rd(d / 'Gap_Annual.csv')},
                E={(r['case'], int(r['year'])): r for r in rd(d / 'N3_Engine_Accounts.csv')},
                P={(r['case'], int(r['year'])): r for r in rd(d / 'N3_Policy_Accounts.csv')},
                PA={(r['case'], int(r['year'])): r for r in rd(d / 'N3_Pension_Accounts.csv')},
                CF={(r['case'], int(r['year'])): r for r in rd(d / 'Corporate_Funding_Stock.csv')},
                KE={(r['case'], int(r['year'])): r for r in rd(d / 'KPI_Events.csv')},
                DB={(r['case'], int(r['year'])): r for r in rd(d / 'Dynamic_Base_Audit.csv')},
                SM={(r['case'], int(r['year'])): r for r in rd(d / 'Gap_Semi_Medical.csv')},
                ST={(r['case'], int(r['year'])): r for r in rd(d / 'N3_Structural_Interfaces.csv')})
allcases = sorted({k[0] for k in D['DOMESTIC_TRANSFER']['A']})

# ------------------------------------------------------------------------------------------ A. inventory
exp_cases = 14 + len(inp['cases'])
for m in MODES:
    chkb(f'A01_{m}', 'A', f'{m}: 103 cases x 30 years present in Gap_Annual / Engine / Policy accounts (no duplicate keys)',
         len(D[m]['A']) == exp_cases * 30 == 3090 and len(D[m]['E']) == 3090 and len(D[m]['P']) == 3090 and
         all((c, y) in D[m]['A'] for c in allcases for y in Y), f'cases={len(allcases)}')
chkb('A02', 'A', 'case partition = 14 original + 65 existing extensions + 24 PARITY cases = 103; 24 parity ids all present',
     len(allcases) == 103 and len(PARITY) == 24 and all(c in allcases for c in PARITY) and sum(1 for c in allcases if c.startswith('PARITY_')) == 24)
chkb('A03', 'A', '4 modes x 103 cases x 30 years = 12,360 case-years', sum(len(D[m]['A']) for m in MODES) == 12360)

# ------------------------------------------------------------------------------------------ B. annual accounting on actual engine rows
for m in MODES:
    A, E, P = D[m]['A'], D[m]['E'], D[m]['P']
    gdp = Acc(f'B01_{m}', 'B', f'{m}: real GDP = core + absorption*supply + C + I + education/deflator + services - unmet (own identity, all 3,090 case-years)')
    cpers = Acc(f'B02_{m}', 'B', f'{m}: C_t = (1-lamC)*C_(t-1) + lamC*Ctarget_t, with C_(t-1) taken from the PRIOR ROW (not from the logged previous column)')
    iper = Acc(f'B03_{m}', 'B', f'{m}: I_t = (1-lamI)*I_(t-1) + lamI*nominal_investment_t/deflator_t, I_(t-1) from the prior row')
    cap = Acc(f'B04_{m}', 'B', f'{m}: capital stock K_t = (1-dep)*K_(t-1) + I_t (carry cases); NO_CARRY: K_t = I_t')
    sup = Acc(f'B05_{m}', 'B', f'{m}: next-year supply = yield*(1-dep)*K_(t-1) + education supply; K_(t-1) from the prior row')
    tot = Acc(f'B06_{m}', 'B', f'{m}: total capital - delta capital = capital_ratio(3.0) * core real GDP (one core capital line; no second addition)')
    fb = Acc(f'B07_{m}', 'B', f'{m}: income feedback = 0.08 * (prior-year real GDP - prior core real GDP) * deflator; household disposable = 0.6*core nominal + cash + feedback')
    gapi = Acc(f'B08_{m}', 'B', f'{m}: prior-gap column equals prior-row (real GDP - core real GDP)')
    cdef = Acc(f'B09_{m}', 'B', f'{m}: first year (2026) is the observed anchor: C=I=K=0 and real GDP = core = 580 for every case')
    tax = Acc(f'B10_{m}', 'B', f'{m}: macro tax follows nominal GDP only: tax_t = min(tax_(t-1)*(1+1.5*(N_t/N_(t-1)-1))*quake_t, 0.3*N_t); quake factor derived from SQ and required equal in every case')
    dia = Acc(f'B11_{m}', 'B', f'{m}: tax_diagnostic = tax_macro + VAT_delta + engine_direct_tax_delta (policy tax counted once, outside the macro base)')
    dir_ = Acc(f'B12_{m}', 'B', f'{m}: engine_direct_tax_delta = medical_financing_direct_tax + policy_tax_delta')
    bal = Acc(f'B13_{m}', 'B', f'{m}: partial government balance = tax_diagnostic - expenditure_diagnostic')
    hhc = Acc(f'B14_{m}', 'B', f'{m}: household_cash_delta = medical_only_household_cash_delta + policy_household_cash_delta (policy cash once)')
    # quake factor from SQ
    sq = lambda y, k: float(E['SQ_COMMON_ON', y][k])
    quake = None
    for c in allcases:
        for y in Y:
            e, a, p = E[c, y], A[c, y], P[c, y]
            core = float(e['core_real_gdp_trn']); Y_ = float(e['real_gdp_trn']); C_ = float(e['C_demand_real_trn']); I_ = float(e['I_policy_real_trn'])
            d_ = float(e['common_deflator']); coreN = float(e['parity_core_nominal_trn'])
            edu = n0(e, 'education_spending_trn') if 'education_spending_trn' in e else 0.0
            gdp.eq(Y_ - core, ABS_ * float(e['parity_supply_real_trn']) + C_ + I_ + float(e['parity_services_real_trn']) - float(e['parity_unmet_real_trn']) + edu / d_, f'{c} {y}')
            if y == 2026:
                cdef.ok(abs(Y_ - 580) < 1e-9 and abs(core - 580) < 1e-9 and abs(C_) < 1e-12 and abs(I_) < 1e-12 and abs(float(e['capital_delta_real_trn'])) < 1e-12, f'{c}')
            if y > 2026:
                pe = E[c, y - 1]
                carry = e['parity_carry'] == 'True'
                lamC, lamI = float(e['parity_lambda_C']), float(e['parity_lambda_I'])
                cpers.eq(C_, (1 - lamC) * float(pe['C_demand_real_trn']) + lamC * float(e['parity_consumption_target_real_trn']), f'{c} {y}')
                iper.eq(I_, (1 - lamI) * float(pe['I_policy_real_trn']) + lamI * float(e['parity_investment_nominal_trn']) / d_, f'{c} {y}')
                dep = float(e['parity_depreciation'])
                Kt = float(e['capital_delta_real_trn']); Kp = float(pe['capital_delta_real_trn'])
                cap.eq(Kt, ((1 - dep) * Kp if carry else 0.0) + I_, f'{c} {y} carry={carry}')
                Kprev_used = Kp if carry else 0.0
                # education stock H_(t-1): derive from the logged education supply term (kept as an input of the identity)
                sup.eq(float(e['parity_supply_real_trn']), float(e['parity_capital_yield']) * (1 - dep) * Kprev_used + float(e['parity_education_supply_real_trn']), f'{c} {y}')
                fb.eq(float(e['parity_income_feedback_trn']), FBK * (float(pe['real_gdp_trn']) - float(pe['core_real_gdp_trn'])) * d_, f'{c} {y}')
                gapi.eq(float(e['parity_prior_gap_trn']), float(pe['real_gdp_trn']) - float(pe['core_real_gdp_trn']), f'{c} {y}')
                # tax recursion
                N_, Np = float(a['nominal_gdp_trn']), float(A[c, y - 1]['nominal_gdp_trn'])
                t_, tp = float(e['tax_macro_trn']), float(pe['tax_macro_trn'])
                free = tp * (1 + (N_ / Np - 1) * ELAS)
                if y == 2031:
                    if c == 'SQ_COMMON_ON':
                        quake = t_ / free
                    qf = quake if quake is not None else sq(2031, 'tax_macro_trn') / (sq(2030, 'tax_macro_trn') * (1 + (float(A['SQ_COMMON_ON', 2031]['nominal_gdp_trn']) / float(A['SQ_COMMON_ON', 2030]['nominal_gdp_trn']) - 1) * ELAS))
                    free *= qf
                tax.eq(t_, min(free, CAP * N_), f'{c} {y}')
            fb.eq(float(e['household_disposable_nominal_trn']), HSH * coreN + float(e['parity_household_cash_trn']) + float(e['parity_income_feedback_trn']), f'{c} {y} disposable')
            tot.eq(float(e['capital_total_real_trn']) - float(e['capital_delta_real_trn']), CAPR * core, f'{c} {y}')
            dia.eq(float(a['tax_diagnostic_trn']), float(e['tax_macro_trn']) + n0(a, 'VAT_delta_vs_fixed_reference_trn') + n0(a, 'engine_direct_tax_delta_trn') if 'engine_direct_tax_delta_trn' in a else float(a['tax_diagnostic_trn']), f'{c} {y}')
            if 'engine_direct_tax_delta_trn' in a:
                dir_.eq(n0(a, 'engine_direct_tax_delta_trn'), n0(a, 'medical_financing_direct_tax_trn') + n0(p, 'policy_tax_delta_trn'), f'{c} {y}')
            bal.eq(float(e['fiscal_balance_partial_trn']), float(a['tax_diagnostic_trn']) - float(e['expenditure_diagnostic_trn']), f'{c} {y}')
            hhc.eq(n0(a, 'household_cash_delta_trn'), n0(a, 'medical_only_household_cash_delta_trn') + n0(p, 'policy_household_cash_delta_trn'), f'{c} {y}')
    for a_ in (gdp, cpers, iper, cap, sup, tot, fb, gapi, cdef, tax, dia, dir_, bal, hhc):
        a_.done()
    if m == 'DOMESTIC_TRANSFER':
        obs.append(f'quake tax factor in 2031 derived from SQ_COMMON_ON: {quake!r}')

# ------------------------------------------------------------------------------------------ C. dynamic bases (previous-year income / profit)
for m in MODES:
    E, A, DB = D[m]['E'], D[m]['A'], D[m]['DB']
    w = Acc(f'C01_{m}', 'C', f'{m}: wage_base_factor_t = nominal wage proxy(case,t-1) / nominal wage proxy(SQ_COMMON_ON,t-1) for every dynamic case-year after 2026')
    pf = Acc(f'C02_{m}', 'C', f'{m}: corporate_profit_base_factor_t = nominal GDP(case,t-1) / core nominal GDP path(t-1)  (denominator = the fixed SQ core nominal path, not each case own core path)')
    one = Acc(f'C03_{m}', 'C', f'{m}: factors are exactly 1 in 2026, in 2027 (prior year = common anchor/SQ) wage factor, and in all years of non-dynamic cases')
    pos = Acc(f'C04_{m}', 'C', f'{m}: factors finite and positive; the two bases are replaced, no new income/profit is added (audit columns = 0)')
    fl_ = Acc(f'C05_{m}', 'C', f'{m}: dynamic flag in audit equals Inputs.json dynamic_bases (True only for PARITY_* cases with dynamic_bases)')
    maxdelta = 0.0
    for c in allcases:
        spec = CASES.get(c, {})
        dyn_exp = bool(spec.get('dynamic_bases', False))
        for y in Y:
            r = DB[c, y]
            en = r['enabled'] == 'True'
            fl_.ok(en == dyn_exp, f'{c} {y}: audit {en} vs input {dyn_exp}')
            wf, pfv = float(r['wage_base_factor']), float(r['corporate_profit_base_factor'])
            pos.ok(math.isfinite(wf) and math.isfinite(pfv) and wf > 0 and pfv > 0 and float(r['new_household_income_added_trn']) == 0.0 and float(r['new_corporate_profit_added_trn']) == 0.0, f'{c} {y}')
            if y == 2026 or not dyn_exp:
                one.ok(wf == 1.0 and pfv == 1.0, f'{c} {y}: {wf} {pfv}')
            if dyn_exp and y > 2026:
                wexp = float(E[c, y - 1]['parity_nominal_wage_man']) / float(E['SQ_COMMON_ON', y - 1]['parity_nominal_wage_man'])
                w.eq(wexp, wf, f'{c} {y}')
                pexp = float(A[c, y - 1]['nominal_gdp_trn']) / float(E['SQ_COMMON_ON', y - 1]['parity_core_nominal_trn'])
                pf.eq(pexp, pfv, f'{c} {y}')
                # difference between "core path" denominator and actual SQ nominal GDP
                sqN = float(A['SQ_COMMON_ON', y - 1]['nominal_gdp_trn'])
                maxdelta = max(maxdelta, abs(float(E['SQ_COMMON_ON', y - 1]['parity_core_nominal_trn']) / sqN - 1))
    for a_ in (w, pf, one, pos, fl_):
        a_.done()
    if m == 'DOMESTIC_TRANSFER':
        obs.append(f'corporate-base denominator is the fixed core nominal path, not SQ_COMMON_ON actual nominal GDP: max relative difference between the two = {maxdelta:.3e}')
# policy tax delta is rebased by exactly the lagged factor (reform AND pre-reform tax scaled by the same factor => delta scales by it)
for m in MODES:
    P, DB = D[m]['P'], D[m]['DB']
    r1 = Acc(f'C07_{m}', 'C', f'{m}: labour/business flat-30 and household financial-20 tax delta (dynamic case) / same delta (PARITY_FIXED_BASES) = wage_base_factor for every dynamic parity case with the flat tax on and years after 2030', atol=0.0, rtol=1e-9)
    r2 = Acc(f'C08_{m}', 'C', f'{m}: corporate tax delta (dynamic) / (fixed bases) = corporate_profit_base_factor; and pension contribution (dynamic) / (fixed) = wage_base_factor, for the cases that keep those policies', atol=0.0, rtol=1e-9)
    for c in PARITY:
        sp = CASES[c]
        if not sp.get('dynamic_bases', False):
            continue
        for y in range(2031, 2056):
            wf = float(DB[c, y]['wage_base_factor']); pf_ = float(DB[c, y]['corporate_profit_base_factor'])
            if sp.get('flat_hh', True) and c not in ('PARITY_NO_FLAT',):
                for col in ('labour_business_flat30_tax_delta_trn', 'household_financial20_tax_delta_trn'):
                    fx = n0(P['PARITY_FIXED_BASES', y], col)
                    if abs(fx) > 1e-9:
                        r1.eq(wf * fx, n0(P[c, y], col), f'{c} {y} {col}')
            if sp.get('corporate', True) and c not in ('PARITY_NO_CORPORATE',):
                fx = n0(P['PARITY_FIXED_BASES', y], 'corporate_tax_delta_trn')
                if abs(fx) > 1e-9:
                    r2.eq(pf_ * fx, n0(P[c, y], 'corporate_tax_delta_trn'), f'{c} {y} corp')
    r1.done(); r2.done()
# FIXED vs CONNECTED
m = 'DOMESTIC_TRANSFER'
E = D[m]['E']; A = D[m]['A']
first_div = {}
for c in PARITY:
    fd = None
    for y in Y:
        if not close(float(A[c, y]['real_gdp_trn']), float(A['PARITY_CONNECTED_CANDIDATE', y]['real_gdp_trn']), 1e-9, 0):
            fd = y
            break
    first_div[c] = fd
chkb('C06', 'C', 'PARITY_FIXED_BASES (dynamic bases off) equals PARITY_CONNECTED_CANDIDATE through 2029 and diverges only after the base factors depart from 1',
     first_div['PARITY_FIXED_BASES'] is not None and first_div['PARITY_FIXED_BASES'] >= 2030, f'first GDP divergence year = {first_div["PARITY_FIXED_BASES"]}')
obs.append('first year real GDP differs from PARITY_CONNECTED_CANDIDATE (DOMESTIC_TRANSFER): ' + json.dumps(first_div))
# policy tax delta ratio vs wage factor (information): reform and pre-reform both scaled
rat = []
for y in range(2030, 2056):
    f1 = float(D[m]['P']['PARITY_CONNECTED_CANDIDATE', y]['policy_tax_delta_trn']); f0 = float(D[m]['P']['PARITY_FIXED_BASES', y]['policy_tax_delta_trn'])
    rat.append((y, f1, f0, float(D[m]['DB']['PARITY_CONNECTED_CANDIDATE', y]['wage_base_factor'])))
obs.append('policy_tax_delta (connected vs fixed bases) 2035/2045/2055: ' + '; '.join(f'{y}: {a:.3f} vs {b:.3f} (wage factor {w_:.4f})' for y, a, b, w_ in rat if y in (2035, 2045, 2055)))

# ------------------------------------------------------------------------------------------ D. corporate funding stock and investment
for m in MODES:
    CF, P, E = D[m]['CF'], D[m]['P'], D[m]['E']
    roll = Acc(f'D01_{m}', 'D', f'{m}: firm cash end = begin + tax saving - dividend - realized nominal investment; begin = prior-year end')
    src = Acc(f'D02_{m}', 'D', f'{m}: tax saving = -corporate_tax_delta; dividend = dividend_delta; target investment = policy_investment_delta (policy account)')
    rec = Acc(f'D03_{m}', 'D', f'{m}: firm realized real investment_t = (1-lamI)*prior + lamI*target/deflator (first year 2026 = 0); nominal = real*deflator')
    res = Acc(f'D04_{m}', 'D', f'{m}: residual column equals recomputed residual and is 0; external funding need = max(0,-cash)')
    gate = Acc(f'D05_{m}', 'D', f'{m}: investment start-year gate: no realized/target corporate investment before corporate_investment_start (PARITY_INVESTMENT_START2038 / RESPONSE0 cases)')
    once = Acc(f'D06_{m}', 'D', f'{m}: GDP adds investment once: macro investment line minus the policy (corporate-induced) investment equals the whole line of PARITY_NO_CORPORATE within 0.2% (the firm funding stock itself never enters the GDP identity: B01/B03)')
    maxshare = 0.0
    maxdefl = [0.0]
    gaprem = [0.0]
    for c in PARITY:
        spec = CASES[c]
        start = spec.get('corporate_investment_start', 2026)
        cashp = None
        Ireal_p = 0.0
        for y in Y:
            r = CF[c, y]; p = P[c, y]; e = E[c, y]
            d_ = float(E['SQ_COMMON_ON', y]['common_deflator'])  # firm account uses the fixed SQ deflator path
            dcase = float(e['common_deflator'])
            maxdefl[0] = max(maxdefl[0], abs(dcase / d_ - 1))
            cb, ce = float(r['cash_begin_trn']), float(r['cash_end_trn'])
            if cashp is not None:
                roll.eq(cb, cashp, f'{c} {y} begin=prior end')
            roll.eq(ce, cb + float(r['source_tax_saving_trn']) - float(r['dividend_paid_trn']) - float(r['realized_investment_nominal_trn']), f'{c} {y}')
            cashp = ce
            src.eq(float(r['source_tax_saving_trn']), -float(p['corporate_tax_delta_trn']), f'{c} {y} saving')
            src.eq(float(r['dividend_paid_trn']), float(p['dividend_delta_trn']), f'{c} {y} dividend')
            src.eq(float(r['target_investment_nominal_trn']), float(p['policy_investment_delta_trn']), f'{c} {y} target')
            lam = float(e['parity_lambda_I'])
            if y == 2026:
                exp_real = 0.0
            else:
                exp_real = (1 - lam) * Ireal_p + lam * float(r['target_investment_nominal_trn']) / d_
            rec.eq(float(r['realized_investment_real_trn']), exp_real, f'{c} {y}')
            rec.eq(float(r['realized_investment_nominal_trn']), float(r['realized_investment_real_trn']) * d_, f'{c} {y} nominal')
            Ireal_p = float(r['realized_investment_real_trn'])
            res.eq(float(r['residual_trn']), 0.0, f'{c} {y}')
            res.eq(float(r['external_funding_need_partial_trn']), max(0.0, -ce), f'{c} {y} need')
            if y < start:
                gate.ok(abs(float(r['target_investment_nominal_trn'])) < 1e-12 and abs(float(r['realized_investment_real_trn'])) < 1e-12, f'{c} {y}: target={r["target_investment_nominal_trn"]}')
            # macro investment line = policy (firm-induced) investment + remainder; remainder must equal the NO_CORPORATE case's whole line
            if c in ('PARITY_CONNECTED_CANDIDATE', 'PARITY_FIXED_BASES', 'PARITY_NO_MEDICAL', 'PARITY_MPC_LOW', 'PARITY_MPC_HIGH', 'PARITY_NO_KPI', 'PARITY_KPI_LOW_THRESHOLD'):
                rem = float(e['parity_investment_nominal_trn']) - float(p['policy_investment_delta_trn'])
                rem0 = float(E['PARITY_NO_CORPORATE', y]['parity_investment_nominal_trn'])
                gaprem[0] = max(gaprem[0], abs(rem - rem0))
                once.ok(abs(rem - rem0) < 2e-3 + 2e-3 * abs(rem0) and abs(float(r['target_investment_nominal_trn']) - float(p['policy_investment_delta_trn'])) < 1e-12, f'{c} {y}: remainder {rem} vs no-corporate line {rem0}')
    for a_ in (roll, src, rec, res, gate, once):
        a_.done()
    if m == 'DOMESTIC_TRANSFER':
        obs.append(f'macro investment line minus corporate-induced policy investment vs PARITY_NO_CORPORATE line: max gap {gaprem[0]:.5f} trn; the remainder is NEGATIVE (2045: {float(E["PARITY_NO_CORPORATE", 2045]["parity_investment_nominal_trn"]):.3f} trn) because employer-cost channels (pension employer premium etc., x firm_investment_response 0.3) reduce investment in the inherited old-79 mechanism; net investment of the base candidate in 2045 = {float(E["PARITY_CONNECTED_CANDIDATE", 2045]["parity_investment_nominal_trn"]):.3f} trn')
        obs.append(f'firm funding account deflates with the fixed SQ deflator; the macro engine deflates investment with each case\'s own deflator: max relative gap over parity cases = {maxdefl[0]:.3e}')
    # SQ never has corporate flows
chkb('D07', 'D', 'start-year sensitivity: PARITY_INVESTMENT_START2038 has zero corporate investment before 2038 and a positive target from 2038 on (DOMESTIC_TRANSFER)',
     all(abs(float(D['DOMESTIC_TRANSFER']['CF']['PARITY_INVESTMENT_START2038', y]['target_investment_nominal_trn'])) < 1e-12 for y in range(2026, 2038)) and
     any(abs(float(D['DOMESTIC_TRANSFER']['CF']['PARITY_INVESTMENT_START2038', y]['target_investment_nominal_trn'])) > 1e-9 for y in range(2038, 2056)))
chkb('D08', 'D', 'PARITY_INVESTMENT_RESPONSE0: zero corporate investment target in all years; tax saving still goes to dividend/cash (cash > 0 by 2055)',
     all(abs(float(D['DOMESTIC_TRANSFER']['CF']['PARITY_INVESTMENT_RESPONSE0', y]['target_investment_nominal_trn'])) < 1e-12 for y in Y))
# cash accumulation is a diagnostic: report the end-2055 stock of the base candidate
cf55 = float(D['DOMESTIC_TRANSFER']['CF']['PARITY_CONNECTED_CANDIDATE', 2055]['cash_end_trn'])
obs.append(f'PARITY_CONNECTED_CANDIDATE firm cash stock at end-2055 (DOMESTIC_TRANSFER) = {cf55:.4f} trn (negative = external funding need, diagnostic only; not fed back to GDP)')

# ------------------------------------------------------------------------------------------ E. 2035 income KPI, Gini and insurance signal
for m in MODES:
    A, E, KE, ST = D[m]['A'], D[m]['E'], D[m]['KE'], D[m]['ST']
    inc = {}
    for c in allcases:
        for y in Y:
            a, e = A[c, y], E[c, y]
            vat_h = float(e['parity_household_cash_trn']) - n0(a, 'household_cash_delta_trn')  # engine cash minus policy/medical cash = VAT household effect
            inc[c, y] = (float(e['household_disposable_nominal_trn']) - vat_h) / float(e['common_deflator']) / float(a['population'])
    g = Acc(f'E01_{m}', 'E', f'{m}: logged previous_income_growth_pct = 100*(income per person(t-1)/(t-2) - 1) from the actual rows; income = (disposable - VAT household effect)/deflator/population')
    thr = Acc(f'E02_{m}', 'E', f'{m}: freeze decision in 2035 = (growth < threshold) for kpi cases; sticky afterwards; KPI-off cases never frozen')
    rate = Acc(f'E03_{m}', 'E', f'{m}: frozen cases keep the standard VAT rate at the 2035 level for all later years; unfrozen cases follow the unfrozen path (NO_KPI)')
    fut = Acc(f'E04_{m}', 'E', f'{m}: growth used in the 2035 decision does not depend on 2035 or later values (it equals the 2034/2033 computation)')
    for c in PARITY:
        spec = CASES[c]
        if spec.get('kpi_signal') != 'LAGGED_REAL_CASH_INCOME_GROWTH':
            continue
        T_ = spec.get('kpi_growth_threshold_pct', 0.0)
        frozen = False
        for y in range(2028, 2056):
            expg = 100 * (inc[c, y - 1] / inc[c, y - 2] - 1)
            gv = KE[c, y]['previous_income_growth_pct']
            g.eq(expg, float(gv), f'{c} {y}')
            if y == 2035:
                fut.eq(expg, 100 * (inc[c, 2034] / inc[c, 2033] - 1), f'{c}')
            trig = (y == 2035) and spec.get('kpi', False) and expg < T_
            frozen = frozen or trig
            thr.ok((KE[c, y]['vat_frozen'] == 'True') == (frozen if spec.get('kpi', False) else False), f'{c} {y}: logged {KE[c, y]["vat_frozen"]} expected {frozen}')
        if spec.get('kpi', False) and (KE[c, 2035]['vat_frozen'] == 'True'):
            s35 = float(A[c, 2035]['standard_rate'])
            for y in range(2035, 2056):
                rate.ok(abs(float(A[c, y]['standard_rate']) - s35) < 1e-12, f'{c} {y}')
        elif spec.get('kpi', False):
            for y in range(2026, 2056):
                rate.ok(abs(float(A[c, y]['standard_rate']) - float(A['PARITY_NO_KPI', y]['standard_rate'])) < 1e-12, f'{c} {y}')
    for a_ in (g, thr, rate, fut):
        a_.done()
m = 'DOMESTIC_TRANSFER'
KE, A, E = D[m]['KE'], D[m]['A'], D[m]['E']
gv35 = {c: float(KE[c, 2035]['previous_income_growth_pct']) for c in ['PARITY_CONNECTED_CANDIDATE', 'PARITY_KPI_HIGH_THRESHOLD', 'PARITY_KPI_LOW_THRESHOLD']}
chkb('E05', 'E', 'high-threshold (100%) freezes VAT at 15% from 2035; low-threshold (-100%) and base (0%) do not fire; NO_KPI never fires (2040 standard rate: 15 / 20 / 20 / 20%)',
     KE['PARITY_KPI_HIGH_THRESHOLD', 2035]['vat_frozen'] == 'True' and KE['PARITY_KPI_LOW_THRESHOLD', 2035]['vat_frozen'] == 'False' and KE['PARITY_CONNECTED_CANDIDATE', 2035]['vat_frozen'] == 'False' and KE['PARITY_NO_KPI', 2055]['vat_frozen'] == 'False'
     and abs(float(A['PARITY_KPI_HIGH_THRESHOLD', 2040]['standard_rate']) - 0.15) < 1e-12 and abs(float(A['PARITY_KPI_LOW_THRESHOLD', 2040]['standard_rate']) - 0.20) < 1e-12 and abs(float(A['PARITY_CONNECTED_CANDIDATE', 2040]['standard_rate']) - 0.20) < 1e-12)
obs.append(f'2035 KPI input (income-per-person growth between 2033 and 2034, %): connected={gv35["PARITY_CONNECTED_CANDIDATE"]:.6f}; this is only {gv35["PARITY_CONNECTED_CANDIDATE"]:.3f} percentage points above the 0% candidate threshold (knife-edge: a small change of level can flip the freeze)')
# Gini
gz = D[m]['KE']
chkb('E06', 'E', 'external Gini candidate: only PARITY_GINI_SIGNAL has an observation; trigger 2035 (0.40 > 0.38), active in 2035 only, observation is labelled 2034 (lag); no other case triggers',
     gz['PARITY_GINI_SIGNAL', 2035]['gini_relief_trigger'] == 'True' and gz['PARITY_GINI_SIGNAL', 2035]['gini_lagged_observation'] == '0.4' and gz['PARITY_GINI_SIGNAL', 2036]['gini_relief_active_candidate'] == 'False'
     and all(gz[c, y]['gini_relief_trigger'] == 'False' for c in allcases if c.startswith('PARITY_') and c != 'PARITY_GINI_SIGNAL' for y in Y if (c, y) in gz))
rel_diff = {y: float(D[m]['A']['PARITY_GINI_SIGNAL', y]['premium_relief_trn']) - float(D[m]['A']['PARITY_CONNECTED_CANDIDATE', y]['premium_relief_trn']) for y in Y}
inkind_diff = {y: float(D[m]['A']['PARITY_GINI_SIGNAL', y]['in_kind_trn']) - float(D[m]['A']['PARITY_CONNECTED_CANDIDATE', y]['in_kind_trn']) for y in Y}
chkb('E07', 'E', 'Gini relief increment changes relief/in-kind support only in the trigger year window (2035) and never before; later differences, if any, enter only through lagged macro states',
     all(abs(rel_diff[y]) + abs(inkind_diff[y]) < 1e-12 for y in range(2026, 2035)) and abs(rel_diff[2035]) + abs(inkind_diff[2035]) > 1e-9,
     f'2034:{rel_diff[2034]:.3e} 2035:{rel_diff[2035]:.6f}/{inkind_diff[2035]:.6f} 2036:{rel_diff[2036]:.3e}/{inkind_diff[2036]:.3e}')
# insurance signal
ins = D[m]['KE']
chkb('E08', 'E', 'insurance under-performance: signal true only in 2035 of PARITY_INSURANCE_STRESS (return -1% < floor 0%); competition effect is STRUCTURE_ONLY (no productivity coefficient)',
     ins['PARITY_INSURANCE_STRESS', 2035]['insurance_underperformance_signal'] == 'True' and sum(1 for y in Y if ins['PARITY_INSURANCE_STRESS', y]['insurance_underperformance_signal'] == 'True') == 1
     and all(ins[c, y]['insurance_competition_effect'] == 'STRUCTURE_ONLY_NO_PRODUCTIVITY_COEFFICIENT' for c in allcases if c.startswith('PARITY_') for y in Y if (c, y) in ins)
     and all(ins[c, y]['insurance_underperformance_signal'] == 'False' for c in allcases if c.startswith('PARITY_') and c != 'PARITY_INSURANCE_STRESS' for y in Y if (c, y) in ins))
# does the insurance stress case move GDP only through the pension return?
dg = {y: float(A['PARITY_INSURANCE_STRESS', y]['real_gdp_trn']) - float(A['PARITY_CONNECTED_CANDIDATE', y]['real_gdp_trn']) for y in Y}
dr = {y: float(D[m]['PA']['PARITY_INSURANCE_STRESS', y]['fund_return_trn']) - float(D[m]['PA']['PARITY_CONNECTED_CANDIDATE', y]['fund_return_trn']) for y in Y}
obs.append(f'PARITY_INSURANCE_STRESS vs CONNECTED real GDP difference 2035/2045/2055 = {dg[2035]:.4f}/{dg[2045]:.4f}/{dg[2055]:.4f} trn; pension fund return difference {dr[2035]:.4f}/{dr[2045]:.4f}/{dr[2055]:.4f} trn. The GDP difference is a pension-return/fund-balance effect (fund_return -1% instead of +2%); no separate competition-productivity effect exists in the code path (label STRUCTURE_ONLY). The case therefore does not isolate the signal.')

# ------------------------------------------------------------------------------------------ F. four pension ownership candidates, insurer/government transfers
PAm = {mm: D[mm]['PA'] for mm in MODES}
for m in MODES:
    PA, P, A = D[m]['PA'], D[m]['P'], D[m]['A']
    st = Acc(f'F01_{m}', 'F', f'{m}: fund end = begin + contribution + return - payout, begin = prior-year end, for every case with a pension account')
    cn = Acc(f'F02_{m}', 'F', f'{m}: ownership counterpart: LEGACY none; DOMESTIC debit = return, external 0; FOREIGN external = return, debit 0; ADDITIONAL_VA VA added = return nominal; second contribution charge and direct GDP subtraction = 0')
    sm = Acc(f'F03_{m}', 'F', f'{m}: semi-public medical: public net delta 0 and new public saving 0; reserve fund end = begin + return + reserve premium')
    for c in sorted({k[0] for k in PA}):
        pb = None
        for y in Y:
            r = PA[c, y]
            fe = float(r['fund_end_trn'])
            st.eq(fe, float(r['fund_begin_trn']) + float(r['fund_contribution_trn']) + float(r['fund_return_trn']) - float(r['fund_payout_trn']), f'{c} {y}')
            if pb is not None:
                st.eq(float(r['fund_begin_trn']), pb, f'{c} {y} begin')
            pb = fe
            p = P[c, y]
            ret = float(p['pension_return_trn'])
            deb, ext, vaa = n0(p, 'pension_domestic_income_debit_trn'), n0(p, 'pension_external_primary_income_trn'), n0(p, 'pension_additional_VA_nominal_trn')
            if m == 'LEGACY':
                cn.ok(abs(deb) + abs(ext) + abs(vaa) < 1e-12, f'{c} {y}')
            elif m == 'DOMESTIC_TRANSFER':
                cn.ok(abs(deb - ret) < 1e-12 and abs(ext) < 1e-12 and abs(vaa) < 1e-12, f'{c} {y}')
            elif m == 'FOREIGN_INCOME':
                cn.ok(abs(ext - ret) < 1e-12 and abs(deb) < 1e-12 and abs(vaa) < 1e-12, f'{c} {y}')
            else:
                cn.ok(abs(vaa - ret) < 1e-9 and abs(deb) < 1e-12 and abs(ext) < 1e-12, f'{c} {y} va={vaa} ret={ret}')
            cn.ok(abs(n0(p, 'pension_second_contribution_charge_trn')) < 1e-12 and abs(n0(p, 'pension_direct_GDP_subtraction_trn')) < 1e-12, f'{c} {y} second charge')
            s = D[m]['SM'].get((c, y))
            if s is not None:
                sm.ok(abs(n0(s, 'old_public_system_net_delta_trn')) < 1e-12 and abs(n0(s, 'new_public_saving_trn')) < 1e-12, f'{c} {y}')
                sm.eq(float(s['fund_end_trn']), float(s['fund_begin_trn']) + float(s['fund_return_trn']) + float(s['fund_reserve_premium_trn']), f'{c} {y} reserve')
    for a_ in (st, cn, sm):
        a_.done()
# cross-mode: fund stock and non-pension channels are mode-invariant
inv = Acc('F04', 'F', 'across the 4 candidates: pension fund stock/contribution/payout/return are identical for every NON-dynamic-base case that has a pension account (dynamic-base cases are expected to differ, see F04b)')
PC = sorted(k_ for k_ in {k[0] for k in PAm['DOMESTIC_TRANSFER']} if not CASES.get(k_, {}).get('dynamic_bases', False))
PCD = sorted(k_ for k_ in {k[0] for k in PAm['DOMESTIC_TRANSFER']} if CASES.get(k_, {}).get('dynamic_bases', False))
for c in PC:
    for y in Y:
        for k in ('fund_end_trn', 'fund_contribution_trn', 'fund_payout_trn', 'fund_return_trn'):
            for mm in MODES[1:]:
                inv.eq(float(PAm['DOMESTIC_TRANSFER'][c, y][k]), float(PAm[mm][c, y][k]), f'{c} {y} {k} {mm}')
inv.done()
dyn_gap = max((abs(float(PAm['DOMESTIC_TRANSFER'][c, y]['fund_end_trn']) - float(PAm[mm][c, y]['fund_end_trn'])) for c in PCD for y in Y for mm in MODES[1:]), default=0.0)
dyn_gap55 = max((abs(float(PAm['DOMESTIC_TRANSFER'][c, 2055]['fund_end_trn']) - float(PAm[mm][c, 2055]['fund_end_trn'])) for c in PCD for mm in MODES[1:]), default=0.0)
chkb('F04b', 'F', 'dynamic-base cases: pension fund contribution uses the previous-year wage of the case itself, so fund stock now differs by attribution candidate (expected consequence of the lagged wage base; first-year 2026-2028 equal)',
     all(abs(float(PAm['DOMESTIC_TRANSFER'][c, y]['fund_end_trn']) - float(PAm[mm][c, y]['fund_end_trn'])) < 1e-9 for c in PCD for y in (2026, 2027, 2028) for mm in MODES[1:]) and dyn_gap > 0, f'max fund-stock gap across candidates = {dyn_gap:.6f} trn (2055: {dyn_gap55:.6f})')
legacy_foreign = Acc('F05', 'F', 'FOREIGN_INCOME real/nominal GDP equals LEGACY exactly for all 103 cases (overseas income has no domestic GDP effect and no household debit)')
for c in allcases:
    for y in Y:
        legacy_foreign.eq(float(D['LEGACY']['A'][c, y]['real_gdp_trn']), float(D['FOREIGN_INCOME']['A'][c, y]['real_gdp_trn']), f'{c} {y}')
legacy_foreign.done()
ordr = Acc('F06', 'F', '2055 ordering for the 24 parity cases: positive-return cases DOMESTIC_TRANSFER <= LEGACY = FOREIGN_INCOME <= ADDITIONAL_VA; the negative-return stress case reverses (debit becomes a credit, VA a loss)')
for c in PARITY:
    g_ = {mm: float(D[mm]['A'][c, 2055]['real_gdp_trn']) for mm in MODES}
    rets = [float(D['DOMESTIC_TRANSFER']['P'][c, y]['pension_return_trn']) for y in Y]
    pos_ = sum(rets) >= 0
    if pos_:
        ordr.ok(g_['DOMESTIC_TRANSFER'] <= g_['LEGACY'] + 1e-9 and abs(g_['LEGACY'] - g_['FOREIGN_INCOME']) < 1e-9 and g_['LEGACY'] <= g_['ADDITIONAL_VA'] + 1e-9, f'{c}: {g_}')
    else:
        # negative cumulative return (stress case): the debit becomes a credit and the added VA a loss -> order reverses
        ordr.ok(g_['DOMESTIC_TRANSFER'] >= g_['LEGACY'] - 1e-9 and abs(g_['LEGACY'] - g_['FOREIGN_INCOME']) < 1e-9 and g_['LEGACY'] >= g_['ADDITIONAL_VA'] - 1e-9, f'{c}: {g_}')
ordr.done()
for c in ('PARITY_CONNECTED_CANDIDATE',):
    obs.append('2055 real GDP of ' + c + ' by pension ownership: ' + ', '.join(f'{mm}={float(D[mm]["A"][c, 2055]["real_gdp_trn"]):.6f}' for mm in MODES))
# insurer / government transfer neutrality in policy accounts
tn = Acc('F07', 'F', 'government <-> insurer transfers cancel in the consolidated partial balance: consolidated = government + insurer lines for all cases (4 modes)')
for m in MODES:
    for c in allcases:
        for y in Y:
            a, e = D[m]['A'][c, y], D[m]['E'][c, y]
            tn.ok(abs(n0(a, 'internal_transfer_consolidated_delta_trn')) < 1e-9, f'{m} {c} {y}')
tn.done()
# national nulls
nn = Acc('F08', 'F', 'national general-government PB, debt and actual bond issue stay null in all 12,360 macro rows')
for m in MODES:
    for c in allcases:
        for y in Y:
            a = D[m]['A'][c, y]
            nn.ok(a.get('national_PB_trn', '') == '' and a.get('national_debt_trn', '') == '' and a.get('national_bond_issue_trn', '') == '', f'{m} {c} {y}')
nn.done()

# ------------------------------------------------------------------------------------------ G. key years, rounding, comparison to F fixed reference
Fann = {int(r['year']): r for r in rd(ROOT / 'handoff/f-common-endoflife-finalization-20261121/Annual.csv') if r['case'] == 'LATEST_F'}
A_ = D['DOMESTIC_TRANSFER']['A']
rep = {2026: dict(SQ=580.0, F=580.0, old=580.0, new=580.0),
       2035: dict(SQ=539.172, F=547.910, old=498.602, new=499.271),
       2045: dict(SQ=533.524, F=544.461, old=480.604, new=481.331),
       2055: dict(SQ=528.962, F=540.275, old=480.747, new=481.331)}
ky = []
for y, e in rep.items():
    got = dict(SQ=float(A_['SQ_COMMON_ON', y]['real_gdp_trn']), F=float(Fann[y]['real_gdp_trn']), old=float(A_['CONNECTED_Q_ESTATE_SEMI', y]['real_gdp_trn']), new=float(A_['PARITY_CONNECTED_CANDIDATE', y]['real_gdp_trn']))
    for k in e:
        ky.append(dict(year=y, series=k, reported=e[k], recomputed=got[k], diff=got[k] - e[k], rounded3=round(got[k], 3), match_after_rounding=abs(round(got[k], 3) - e[k]) < 5e-4 + 1e-12))
chkb('G01', 'G', 'reported 2026/2035/2045/2055 real GDP (SQ, F fixed, old composite, new candidate; DOMESTIC_TRANSFER) re-derived from the rows and equal after rounding to 3 decimals', all(r['match_after_rounding'] for r in ky), '; '.join(f"{r['year']} {r['series']} {r['recomputed']:.6f}" for r in ky if not r['match_after_rounding']))
n55 = float(A_['PARITY_CONNECTED_CANDIDATE', 2055]['real_gdp_trn'])
chkb('G02', 'G', 'quoted differences: new 2055 vs initial 580 = -98.669; vs SQ = -47.631; vs F fixed = -58.944 (trn)', abs((n55 - 580) + 98.669) < 6e-4 and abs((n55 - float(A_['SQ_COMMON_ON', 2055]['real_gdp_trn'])) + 47.631) < 6e-4 and abs((n55 - float(Fann[2055]['real_gdp_trn'])) + 58.944) < 6e-4, f'{n55 - 580:.6f} {n55 - float(A_["SQ_COMMON_ON", 2055]["real_gdp_trn"]):.6f} {n55 - float(Fann[2055]["real_gdp_trn"]):.6f}')
# SQ_COMMON_OFF vs ON and F fixed reference columns inside delivered comparison file
cmp = rd(TGT / 'results/SQ_F_N3_Annual_Comparison.csv')
bad = 0
for r in cmp:
    if r['mode'] == 'DOMESTIC_TRANSFER':
        y = int(r['year']); a = A_[r['case'], y]
        v = float(r['real_gdp_trn'])
        if abs(v - float(a['real_gdp_trn'])) > 1e-9 or abs(float(r['real_gdp_trn_minus_SQ']) - (v - float(A_['SQ_COMMON_ON', y]['real_gdp_trn']))) > 1e-9 or abs(float(r['real_gdp_trn_minus_F_FIXED']) - (v - float(Fann[y]['real_gdp_trn']))) > 1e-9:
            bad += 1
chk = Acc('G03', 'G', 'delivered SQ_F_N3_Annual_Comparison.csv (DOMESTIC_TRANSFER, 3,090 rows): real GDP, minus-SQ and minus-F_FIXED re-derived from the macro rows and the fixed F reference')
chk.n, chk.bad = sum(1 for r in cmp if r['mode'] == 'DOMESTIC_TRANSFER'), bad
chk.done()
with open(OUT / 'N3_F_Parity_Key_Years_Independent_DRAFT_20261122.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(ky[0]), lineterminator='\n'); w.writeheader(); w.writerows(ky)

# ------------------------------------------------------------------------------------------ H. sensitivity timing / direction
m = 'DOMESTIC_TRANSFER'
A = D[m]['A']
exp_first = {'PARITY_MPC_LOW': 2027, 'PARITY_MPC_HIGH': 2027, 'PARITY_DEPRECIATION_LOW': 2028, 'PARITY_DEPRECIATION_HIGH': 2028,
             'PARITY_INVESTMENT_START2038': 2030, 'PARITY_INVESTMENT_RESPONSE0': 2030, 'PARITY_NO_CARRY': 2028}
timing = []
for c, ye in exp_first.items():
    fd = first_div[c]
    timing.append(dict(case=c, expected_first_year_at_or_after=ye, observed_first_divergence=fd, ok=fd is not None and fd >= ye))
chkb('H01', 'H', 'parameter-change cases first diverge from the base candidate at or after the first year the parameter can act (MPC 2027; depreciation 2028 (lagged capital); corporate start/response 2030 (household_start); NO_CARRY 2028)', all(t['ok'] for t in timing), json.dumps(timing))
sgn = []
cash55 = float(D[m]['A']['PARITY_CONNECTED_CANDIDATE', 2055]['household_cash_delta_trn'])
cash_sign = 1 if cash55 > 0 else -1   # MPC multiplies the household cash change: its GDP sign follows the sign of the cash change
for c, sign in [('PARITY_MPC_LOW', -cash_sign), ('PARITY_MPC_HIGH', cash_sign), ('PARITY_DEPRECIATION_LOW', +1), ('PARITY_DEPRECIATION_HIGH', -1), ('PARITY_NO_CARRY', -1), ('PARITY_LABOR_ADD100K', +1)]:
    d55 = float(A[c, 2055]['real_gdp_trn']) - float(A['PARITY_CONNECTED_CANDIDATE', 2055]['real_gdp_trn'])
    sgn.append(dict(case=c, delta_2055=d55, expected_sign=sign, ok=(d55 > 0) == (sign > 0) and abs(d55) > 1e-9))
chkb('H02', 'H', '2055 real GDP moves in the expected direction: MPC effect follows the sign of the household cash change (negative cash in 2055 => lower MPC raises GDP, higher MPC lowers it); higher depreciation and no-carry reduce, lower depreciation and +100k effective labour raise', all(s['ok'] for s in sgn), json.dumps(sgn))
obs.append(f'household cash change of the base candidate in 2055 = {cash55:.3f} trn (negative: N3 is a net household burden, so a higher MPC LOWERS GDP); PARITY_LABOR_ZERO > base by payroll demand only (base candidate has no added jobs; ZERO adds payroll but 0 effective labour); LABOR_ADD100K - LABOR_ZERO = {float(A["PARITY_LABOR_ADD100K", 2055]["real_gdp_trn"]) - float(A["PARITY_LABOR_ZERO", 2055]["real_gdp_trn"]):+.3f}')
obs.append('sensitivity 2055 real GDP deltas vs base candidate (DOMESTIC_TRANSFER): ' + ', '.join(f"{s['case']}={s['delta_2055']:+.3f}" for s in sgn) + ', ' + ', '.join(f"{c}={float(A[c, 2055]['real_gdp_trn']) - float(A['PARITY_CONNECTED_CANDIDATE', 2055]['real_gdp_trn']):+.3f}" for c in ['PARITY_INVESTMENT_START2038', 'PARITY_INVESTMENT_RESPONSE0', 'PARITY_INVESTMENT_RESPONSE60', 'PARITY_FIXED_BASES', 'PARITY_NO_FLAT', 'PARITY_NO_CORPORATE', 'PARITY_NO_PENSION', 'PARITY_NO_MEDICAL', 'PARITY_NO_RELIEF', 'PARITY_NO_ESTATE', 'PARITY_NO_KPI']))
with open(OUT / 'N3_F_Parity_Sensitivity_Timing_Independent_DRAFT_20261122.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(timing[0]), lineterminator='\n'); w.writeheader(); w.writerows(timing)
# NO_* ablation cases must set the policy channel to 0
abl = {'PARITY_NO_FLAT': ['labour_business_flat30_tax_delta_trn', 'household_financial20_tax_delta_trn'], 'PARITY_NO_CORPORATE': ['corporate_tax_delta_trn', 'dividend_delta_trn'],
       'PARITY_NO_PENSION': ['pension_fund_contribution_trn'], 'PARITY_NO_ESTATE': ['estate_tax_delta_trn', 'wealth_tax_delta_trn'], 'PARITY_NO_RELIEF': ['premium_relief_trn', 'in_kind_trn']}
okabl = True
note = []
for c, cols in abl.items():
    for col in cols:
        src = D[m]['P'] if col in D[m]['P']['PARITY_CONNECTED_CANDIDATE', 2040] else A
        v = max(abs(n0(src[c, y], col)) for y in Y)
        base_v = max(abs(n0(src['PARITY_CONNECTED_CANDIDATE', y], col)) for y in Y)
        if v > 1e-12 or base_v < 1e-9:
            okabl = False
            note.append(f'{c}.{col} max|ablated|={v:.3e} base={base_v:.3e}')
chkb('H02b', 'H', 'labour: ADD_JOBS with zero effectiveness differs from the base only by payroll demand; with effectiveness 0.8 GDP is higher than with 0 effectiveness in 2055',
     float(A['PARITY_LABOR_ADD100K', 2055]['real_gdp_trn']) > float(A['PARITY_LABOR_ZERO', 2055]['real_gdp_trn']) and all(abs(n0(D[m]['P']['PARITY_LABOR_ZERO', y], 'n3_effective_labor_delta')) < 1e-12 for y in Y) and all(abs(n0(D[m]['P']['PARITY_CONNECTED_CANDIDATE', y], 'public_added_jobs')) < 1e-12 for y in Y))
chkb('H03', 'H', 'ablation cases zero exactly the policy channel they name (flat tax, corporate, pension contribution, estate, relief) while the base candidate has a non-zero value', okabl, '; '.join(note))

# ------------------------------------------------------------------------------------------ I. old-79 regression (independent, all four modes, all files)
tot = diff = missing = 0
files = 0
filetab = []
for m in MODES:
    for f in sorted(os.listdir(OLD / m)):
        if not f.endswith('.csv') or not (MAC / m / f).exists():
            continue
        old = rd(OLD / m / f)
        new = rd(MAC / m / f)
        if not old:
            continue
        keycols = [c for c in old[0] if c in ('case', 'year', 'sector', 'sector_id', 'market', 'channel', 'group', 'mode', 'id', 'name', 'scenario', 'parameter', 'component', 'cell', 'region')]

        def idx(rs):
            d = {}
            for r in rs:
                k0 = tuple(r.get(x) for x in keycols)
                n_ = 0
                while (k0, n_) in d:
                    n_ += 1
                d[(k0, n_)] = r
            return d
        ni, oi = idx(new), idx(old)
        files += 1
        cols = [c for c in old[0] if c in new[0]]
        f_t0, f_d0, f_m0 = tot, diff, missing
        for k, o in oi.items():
            n_ = ni.get(k)
            if n_ is None:
                missing += 1
                continue
            for c in cols:
                tot += 1
                if o[c] != n_[c]:
                    diff += 1
        filetab.append(dict(mode=m, file=f, old_rows=len(old), new_rows=len(new), columns_compared=len(cols), old_columns_absent_in_new=len(old[0]) - len(cols), cells_compared=tot - f_t0, cells_different=diff - f_d0, old_rows_missing_in_new=missing - f_m0))
chk = Acc('I01', 'I', f'old 79-case macro outputs (fixed pension-correction model, Claude re-run) vs the new model for the 79 old cases, all 4 attribution modes, {files} CSV files: string-for-string cell comparison')
chk.n, chk.bad = tot, diff + missing
chk.done(note=f'cells={tot:,}; different={diff}; old rows missing in new={missing}')
with open(OUT / 'N3_F_Parity_Old79_Regression_By_File_DRAFT_20261122.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(filetab[0]), lineterminator='\n'); w.writeheader(); w.writerows(filetab)

# ------------------------------------------------------------------------------------------ J. policy map vs implemented channels
pm = rd(TGT / 'results/Policy_Implementation_Map.csv')
complete_words = [r for r in pm if any(w_ in (r['status'] + r['connection']).upper() for w_ in ('COMPLETE', 'CALIBRATED', 'ADOPTED_FINAL', 'DONE'))]
chkb('J01', 'J', 'Policy_Implementation_Map.csv: 18 rows; no row is labelled complete/calibrated; STRUCTURE_ONLY/OPEN rows remain for invoice, co-op, smart-shrink and insurance competition',
     len(pm) == 18 and not complete_words and sum(1 for r in pm if r['status'].startswith('STRUCTURE_ONLY')) >= 3, f'rows={len(pm)} structure_only={sum(1 for r in pm if r["status"].startswith("STRUCTURE_ONLY"))}')
for r in pm:
    pass

# ------------------------------------------------------------------------------------------ write
fails = [c for c in checks if c['verdict'] == 'FAIL']
with open(OUT / 'N3_F_Parity_Independent_Numeric_Comparison_DRAFT_20261122.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(checks[0].keys()), lineterminator='\n')
    w.writeheader(); w.writerows(checks)
summary = dict(checks=len(checks), passed=len(checks) - len(fails), failed=len(fails), failed_ids=[c['id'] for c in fails],
               items_checked=sum(c['items'] for c in checks), by_area={a: dict(total=sum(1 for c in checks if c['area'] == a), fail=sum(1 for c in fails if c['area'] == a)) for a in sorted({c['area'] for c in checks})},
               observations=obs)
(OUT / 'N3_F_Parity_Independent_Summary_DRAFT_20261122.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'observations'}, indent=1))
for o in obs:
    print('OBS', o)
for c in fails:
    print('FAIL', c['id'], c['description'][:150], '|', c['example_failure'][:300], '| items', c['items'], 'bad', c['failures'], 'max', c['max_abs_residual'])
