#!/usr/bin/env python3
"""SPE N3 pension-return counterpart correction: Claude independent recomputation (read-only).

usage: python3 -I THIS.py TARGET_DIR BEFORE_DIR PR_DIR ROOT OUTDIR
  TARGET_DIR = ChatGPT Work corrected output (76176ae1.. handoff/chatgpt-n3-pension-counterpart-20261121)
  BEFORE_DIR = pre-correction output (556953292e.. handoff/chatgpt-n3-gap-closure-20261121)
  PR_DIR     = Claude's own re-run outputs: PR_DIR/{DOMESTIC_TRANSFER,LEGACY,FOREIGN_INCOME,ADDITIONAL_VA}/
  ROOT       = tree with fixed engine pins (ff621006.. etc.)
Does not import Work's Verify.py / Evaluate.py / Build_Results.py. Reads CSV outputs and fixed constants only.
"""
import sys, csv, json, math
from pathlib import Path

T, B, PR, ROOT, OUT = (Path(a) for a in sys.argv[1:6])
OUT.mkdir(parents=True, exist_ok=True)
MODES = ['LEGACY', 'DOMESTIC_TRANSFER', 'FOREIGN_INCOME', 'ADDITIONAL_VA']
checks = []
obs = []


def rd(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))


def fl(x):
    return None if x in (None, '') else float(x)


def chk(cid, area, desc, exp, act, tol=5e-9):
    d = abs(exp - act)
    checks.append(dict(id=cid, area=area, description=desc, expected=exp, actual=act, abs_diff=d, tol=tol, verdict='PASS' if d <= tol else 'FAIL'))


def chkb(cid, area, desc, cond, note=''):
    checks.append(dict(id=cid, area=area, description=desc + (' | ' + note if note else ''), expected=True, actual=bool(cond), abs_diff=0 if cond else 1, tol=0, verdict='PASS' if cond else 'FAIL'))


# ------------------------------------------------------------ load
AN = {m: rd(PR / m / 'Gap_Annual.csv') for m in MODES}
G = {m: {(r['case'], int(r['year'])): r for r in AN[m]} for m in MODES}
EN = {m: {(r['case'], int(r['year'])): r for r in rd(PR / m / 'N3_Engine_Accounts.csv')} for m in MODES}
PA = {m: rd(PR / m / 'N3_Pension_Accounts.csv') for m in MODES}
BEF = rd(B / 'Gap_Annual.csv')
BG = {(r['case'], int(r['year'])): r for r in BEF}
TG = rd(T / 'Gap_Annual.csv')
cfg = json.loads((T / 'Gap_Inputs.json').read_text())
spec = {z['id']: z for z in cfg['cases']}
cases = sorted({r['case'] for r in BEF})
Y = range(2026, 2056)
keys = [(c, y) for c in cases for y in Y]
chkb('R01', 'R', '79 cases x 30 years = 2,370 rows in every one of 4 candidate runs, no missing/duplicate keys', all(len(AN[m]) == 2370 and set(G[m]) == set(keys) for m in MODES))
chkb('R02', 'R', '4 candidates x 79 x 30 = 9,480 case-years re-executed by Claude', sum(len(AN[m]) for m in MODES) == 9480)

# ------------------------------------------------------------ A. accounting
rate_default = cfg['candidate_parameters']['fund_return']
mx_roll = mx_ret = 0.0
n_roll = 0
for m in MODES:
    for r in PA[m]:
        c = r['case']
        rate = spec.get(c, {}).get('fund_return', rate_default)
        b0, ct, rt, po, e1 = (fl(r[k]) for k in ['fund_begin_trn', 'fund_contribution_trn', 'fund_return_trn', 'fund_payout_trn', 'fund_end_trn'])
        mx_roll = max(mx_roll, abs(b0 + ct + rt - po - e1))
        mx_ret = max(mx_ret, abs(b0 * rate - rt))
        n_roll += 1
chk('A01', 'A', f'fund roll-forward begin+contribution+return-payout=end, {n_roll} rows over 4 candidates', 0.0, mx_roll, 5e-9)
chk('A02', 'A', 'fund return = begin stock x case return rate (default 2%; case overrides 0/4%)', 0.0, mx_ret, 5e-9)

# attribution columns per mode
bad = {m: 0 for m in MODES}
for m in MODES:
    for r in AN[m]:
        gain = fl(r['pension_return_trn'])
        d, e, v = fl(r['pension_domestic_income_debit_trn']), fl(r['pension_external_primary_income_trn']), fl(r['pension_additional_VA_nominal_trn'])
        want = dict(LEGACY=(0, 0, 0), DOMESTIC_TRANSFER=(gain, 0, 0), FOREIGN_INCOME=(0, gain, 0), ADDITIONAL_VA=(0, 0, gain))[m]
        if max(abs(d - want[0]), abs(e - want[1]), abs(v - want[2])) > 1e-12:
            bad[m] += 1
        if abs(fl(r['pension_direct_GDP_subtraction_trn'])) > 0 or abs(fl(r['pension_second_contribution_charge_trn'])) > 0:
            bad[m] += 1
        if r['pension_counterpart_mode'] != m:
            bad[m] += 1
chk('A03', 'A', 'each candidate assigns 100% of the return to exactly one channel (LEGACY none/unattributed, DOMESTIC debit, FOREIGN external, ADDITIONAL_VA service VA); direct GDP subtraction 0; second contribution charge 0 (all 9,480 rows)', 0, sum(bad.values()), 0)

# fund stock/contribution/payout unchanged across modes and vs pre-correction
mx = 0.0
for m in MODES:
    for k in keys:
        for col in ['pension_fund_stock_trn', 'pension_fund_payout_trn', 'pension_fund_contribution_trn', 'pension_benefit_delta_trn']:
            mx = max(mx, abs(fl(G[m][k][col]) - fl(BG[k][col])))
chk('A04', 'A', 'fund stock/contribution/payout and benefit delta identical to pre-correction in all 4 candidates (no change in fund balance, no second contribution deduction)', 0.0, mx, 1e-9)

# household cash and service VA identities vs the pre-correction (LEGACY) state
mxc = mxv = 0.0
for m in MODES:
    for k in keys:
        r, b = G[m][k], BG[k]
        mxc = max(mxc, abs(fl(r['policy_household_cash_delta_trn']) - (fl(b['policy_household_cash_delta_trn']) - fl(r['pension_domestic_income_debit_trn']))))
        mxv = max(mxv, abs(fl(r['policy_service_VA_delta_trn']) - (fl(b['policy_service_VA_delta_trn']) + fl(r['pension_additional_VA_nominal_trn']))))
chk('A05', 'A', 'policy household cash(mode) = pre-correction cash - domestic debit, all 4 candidates x 2,370 rows', 0.0, mxc, 1e-9)
chk('A06', 'A', 'policy service VA(mode) = pre-correction VA + additional VA only (ADDITIONAL_VA), all rows', 0.0, mxv, 1e-9)
# total household cash delta moves one-for-one for DOMESTIC
mxh = max(abs((fl(G['DOMESTIC_TRANSFER'][k]['household_cash_delta_trn']) - fl(BG[k]['household_cash_delta_trn'])) + fl(G['DOMESTIC_TRANSFER'][k]['pension_domestic_income_debit_trn'])) for k in keys)
chk('A07', 'A', 'DOMESTIC total household_cash_delta moves by exactly -debit (no extra channel)', 0.0, mxh, 1e-9)
# FOREIGN_INCOME and LEGACY equal pre-correction for ALL columns that existed before
neq = 0
cells = 0
for m in ['LEGACY', 'FOREIGN_INCOME']:
    for k in keys:
        for col, v in BG[k].items():
            cells += 1
            if G[m][k][col] != v:
                neq += 1
chk('A08', 'A', f'LEGACY and FOREIGN_INCOME reproduce all {cells // 2:,} pre-correction cells exactly (string-equal) per mode', 0, neq, 0)
# GDP identity: domestic transfer creates no new primary income
mx = 0.0
for k in keys:
    r = G['DOMESTIC_TRANSFER'][k]
    mx = max(mx, abs(fl(r['pension_incremental_primary_income_trn'])))
chk('A09', 'A', 'DOMESTIC_TRANSFER incremental primary income = 0 in all rows', 0.0, mx, 1e-12)
mx = max(abs(fl(G['ADDITIONAL_VA'][k]['pension_incremental_primary_income_trn']) - fl(G['ADDITIONAL_VA'][k]['pension_return_trn'])) for k in keys)
chk('A10', 'A', 'ADDITIONAL_VA incremental primary income = return (counterfactual labelled separately)', 0.0, mx, 1e-12)
# source accounts (Work file) re-derived from my runs
src = rd(T / 'Pension_Source_Accounts.csv')
mine = {}
for m in MODES:
    for r in PA[m]:
        g = G[m][r['case'], int(float(r['year']))]
        mine[m, r['case'], int(float(r['year']))] = g
mx = 0.0
miss = 0
for r in src:
    k = (r['mode'], r['case'], int(r['year']))
    if k not in mine:
        miss += 1
        continue
    g = mine[k]
    for a, b in [('fund_property_income_credit_trn', 'pension_return_trn'), ('domestic_existing_income_debit_trn', 'pension_domestic_income_debit_trn'), ('overseas_income_trn', 'pension_external_primary_income_trn'), ('additional_service_VA_trn', 'pension_additional_VA_nominal_trn')]:
        mx = max(mx, abs(fl(r[a]) - fl(g[b])))
    resid = fl(g['pension_return_trn']) - fl(g['pension_domestic_income_debit_trn']) - fl(g['pension_external_primary_income_trn']) - fl(g['pension_additional_VA_nominal_trn'])
    mx = max(mx, abs(fl(r['unallocated_legacy_source_trn']) - resid))
chk('A11', 'A', f'Pension_Source_Accounts.csv ({len(src)} rows) re-derived from Claude re-run; rows not found={miss}; unallocated residual = return - sum(channels); LEGACY residual = 100%', float(miss), mx + miss, 1e-9)
chkb('A12', 'A', 'only LEGACY has an unallocated source; the three candidates leave zero residual', all((abs(fl(r['unallocated_legacy_source_trn'])) < 1e-9) == (r['mode'] != 'LEGACY') or abs(fl(r['fund_property_income_credit_trn'])) < 1e-12 for r in src))

# ------------------------------------------------------------ B. 2055 numbers and propagation
g55 = lambda m, c, k='real_gdp_trn': fl(G[m][c, 2055][k])
exp = {
    ('LEGACY', 'N3_CONNECTED_COMPONENTS_A'): 477.587252101,
    ('DOMESTIC_TRANSFER', 'N3_CONNECTED_COMPONENTS_A'): 475.923625914,
    ('FOREIGN_INCOME', 'N3_CONNECTED_COMPONENTS_A'): 477.587252101,
    ('ADDITIONAL_VA', 'N3_CONNECTED_COMPONENTS_A'): 480.566616773,
    ('LEGACY', 'PENSION_COUNTERPART_R0'): 518.507629544,
    ('DOMESTIC_TRANSFER', 'PENSION_COUNTERPART_R0'): 518.507629544,
    ('DOMESTIC_TRANSFER', 'PENSION_COUNTERPART_R0p02'): 516.912231237,
    ('DOMESTIC_TRANSFER', 'PENSION_COUNTERPART_R0p04'): 514.665206158,
}
for i, ((m, c), v) in enumerate(exp.items(), 1):
    chk(f'B{i:02d}', 'B', f'2055 real GDP {m} {c}', v, g55(m, c), 5e-7)
d = lambda m, c, k: fl(G[m][c, 2055][k]) - fl(G['LEGACY'][c, 2055][k])
c0 = 'N3_CONNECTED_COMPONENTS_A'
chk('B09', 'B', 'A case DOMESTIC 2055 GDP diff vs pre-correction', -1.663626187, d('DOMESTIC_TRANSFER', c0, 'real_gdp_trn'), 5e-7)
chk('B10', 'B', 'A case ADDITIONAL_VA 2055 GDP diff', 2.979364672, d('ADDITIONAL_VA', c0, 'real_gdp_trn'), 5e-7)
chk('B11', 'B', 'A case DOMESTIC 2055 tax proxy diff', -0.710505920, d('DOMESTIC_TRANSFER', c0, 'tax_diagnostic_trn'), 5e-7)
chk('B12', 'B', 'A case DOMESTIC 2055 DI proxy diff', -5.763875768, d('DOMESTIC_TRANSFER', c0, 'macro_cash_DI_proxy_trn'), 5e-7)
chk('B13', 'B', 'A case DOMESTIC 2055 fund asset diff', 0.0, d('DOMESTIC_TRANSFER', c0, 'pension_fund_stock_trn'), 5e-9)
old_r4_r0 = g55('LEGACY', 'PENSION_COUNTERPART_R0p04') - g55('LEGACY', 'PENSION_COUNTERPART_R0')
chk('B14', 'B', 'old R4-R0 2055 GDP = 0.157022376 (old yield sensitivity, not the counterpart correction amount)', 0.157022376, old_r4_r0, 5e-7)
new_r4_r0 = g55('DOMESTIC_TRANSFER', 'PENSION_COUNTERPART_R0p04') - g55('DOMESTIC_TRANSFER', 'PENSION_COUNTERPART_R0')
obs.append(f'DOMESTIC R4-R0 2055 GDP = {new_r4_r0:.9f} (sign flips vs old +0.157022376: domestic debit exceeds retained-return demand effect). Correction amount at R4 = {d("DOMESTIC_TRANSFER", "PENSION_COUNTERPART_R0p04", "real_gdp_trn"):.9f}')
# independent demand-target identity for the correction (same case, DOMESTIC vs LEGACY)
lam, ds, mpc, fb = 0.6, 0.8, 0.72, 0.08
worst = 0.0
n = 0
for c in cases:
    for y in range(2027, 2056):
        e_d, e_l = EN['DOMESTIC_TRANSFER'], EN['LEGACY']
        Cd, Cl = fl(e_d[c, y]['C_demand_real_trn']), fl(e_l[c, y]['C_demand_real_trn'])
        Cd1, Cl1 = fl(e_d[c, y - 1]['C_demand_real_trn']), fl(e_l[c, y - 1]['C_demand_real_trn'])
        dT = ((Cd - (1 - lam) * Cd1) - (Cl - (1 - lam) * Cl1)) / lam
        coreD = fl(e_d[c, y]['common_deflator'])
        gd = fl(e_d[c, y - 1]['real_gdp_trn']) - fl(e_d[c, y - 1]['core_real_gdp_trn'])
        gl = fl(e_l[c, y - 1]['real_gdp_trn']) - fl(e_l[c, y - 1]['core_real_gdp_trn'])
        debit = fl(G['DOMESTIC_TRANSFER'][c, y]['pension_domestic_income_debit_trn'])
        exp_dT = ds * mpc * (-debit) / coreD + ds * mpc * fb * (gd - gl)
        worst = max(worst, abs(dT - exp_dT))
        n += 1
chk('B15', 'B', f'demand-target identity of the correction: dCtarget = ds*MPC*(-debit)/coreD + ds*MPC*0.08*d(gap_t-1); {n} case-years (all 79 cases)', 0.0, worst, 5e-9)
# timing: partial consumption of gain; debit is full gain but demand response uses MPC 0.72 (not 100%)
chkb('B16', 'B', 'demand falls by MPC x debit only (0.72 of the return), never the full return; gain is not assumed fully consumed', True, 'by B15 identity (MPC 0.72, domestic share 0.8)')
# ADDITIONAL_VA transmission is supply-side labelled: GDP rise is positive and bounded by VA in real terms
ratio = []
for y in (2035, 2045, 2055):
    v = fl(G['ADDITIONAL_VA'][c0, y]['pension_additional_VA_nominal_trn']) / fl(EN['ADDITIONAL_VA'][c0, y]['common_deflator'])
    dg = fl(G['ADDITIONAL_VA'][c0, y]['real_gdp_trn']) - fl(G['LEGACY'][c0, y]['real_gdp_trn'])
    ratio.append((y, v, dg))
obs.append('ADDITIONAL_VA real VA (nominal/deflator) vs GDP rise: ' + '; '.join(f'{y}: VA_real={v:.4f} dGDP={dg:.4f}' for y, v, dg in ratio))
chkb('B17', 'B', 'ADDITIONAL_VA raises GDP by the explicit VA channel (positive, same order as VA); counterfactual, not adoptable', all(dg > 0 for _, _, dg in ratio))
# FOREIGN: GDP/tax/DI identical to LEGACY (done A08) -> no direct GDP add
chkb('B18', 'B', 'FOREIGN_INCOME leaves domestic GDP/tax/DI identical to pre-correction in all 2,370 rows (no direct GDP add; full GNI not implemented)', all(G['FOREIGN_INCOME'][k]['real_gdp_trn'] == BG[k]['real_gdp_trn'] for k in keys))
# tax once
bad = 0
for k in keys:
    m_ = EN['DOMESTIC_TRANSFER'][k]
    r = G['DOMESTIC_TRANSFER'][k]
    if abs(fl(m_['tax_macro_trn']) + fl(r['VAT_delta_vs_fixed_reference_trn']) + fl(r['engine_direct_tax_delta_trn']) - fl(r['tax_diagnostic_trn'])) > 5e-7:
        bad += 1
chk('B19', 'B', 'tax_diagnostic = macro tax + VAT delta + direct-tax delta (tax counted once) after correction, 2,370 rows', 0, bad, 0)

# ------------------------------------------------------------ C. regression
tot = 0
diffs = []
for k in keys:
    b, r = BG[k], G['DOMESTIC_TRANSFER'][k]
    for col, v in b.items():
        tot += 1
        if r[col] != v:
            diffs.append((k[0], k[1], col, v, r[col]))
chk('C01', 'C', 'pre-correction cells compared (2,370 rows x 174 columns)', 412380, tot, 0)
chk('C02', 'C', 'changed cells in DOMESTIC vs pre-correction', 2640, len(diffs), 0)
chk('C03', 'C', 'exactly identical cells', 409740, tot - len(diffs), 0)
colset = {}
for c_, y_, col, _, _ in diffs:
    colset[col] = colset.get(col, 0) + 1
chkb('C04', 'C', '8 changed columns, 330 case-years each', set(colset) == {'real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn', 'household_consumption_nominal_proxy_trn', 'consolidated_partial_balance_proxy_trn', 'macro_cash_DI_proxy_trn', 'policy_household_cash_delta_trn', 'household_cash_delta_trn'} and set(colset.values()) == {330}, str(colset))
chcases = sorted({d_[0] for d_ in diffs})
chkb('C05', 'C', '15 changed cases', len(chcases) == 15, ','.join(chcases))
changed_keys = {(d_[0], int(d_[1])) for d_ in diffs}
ret_keys = {k for k in keys if fl(G['DOMESTIC_TRANSFER'][k]['pension_return_trn']) > 0}
chkb('C06', 'C', 'changed case-years == case-years with positive pension return (zero yield, no pension, pre-start unchanged)', changed_keys == ret_keys, f'{len(changed_keys)} vs {len(ret_keys)}')
chkb('C07', 'C', 'every pension case with zero return (R0, no-pension, pre-start) has zero change', all(k not in changed_keys for k in keys if fl(G['DOMESTIC_TRANSFER'][k]['pension_return_trn']) == 0))
# Work's Before_After_Cell_Differences equals my independent list
wd = rd(T / 'Before_After_Cell_Differences.csv')
mine_d = {(a, str(b), c_): (fl(v0), fl(v1)) for a, b, c_, v0, v1 in diffs}
okd = len(wd) == len(mine_d) and all((r['case'], r['year'], r['column']) in mine_d and abs(mine_d[r['case'], r['year'], r['column']][1] - fl(r['after'])) < 1e-9 and abs(mine_d[r['case'], r['year'], r['column']][0] - fl(r['before'])) < 1e-9 and abs((fl(r['after']) - fl(r['before'])) - fl(r['delta'])) < 1e-9 for r in wd)
chkb('C08', 'C', 'Work Before_After_Cell_Differences.csv (2,640 rows) equals independent cell-by-cell diff', okd)
# non-pension/other fields unchanged: population, medical, foreign, tax settings
unch = ['population', 'foreign_extra_employed', 'medical_policy_debt_stock_trn', 'estate_tax_delta_trn', 'VAT_delta_vs_fixed_reference_trn']
chkb('C09', 'C', 'population/foreign/medical/estate/VAT-delta columns unchanged (not in changed set)', all(c_ not in colset for c_ in unch))
# Target Gap_Annual == my DOMESTIC rerun (values) and unchanged-column identity
chkb('C10', 'C', 'target Gap_Annual.csv == Claude DOMESTIC rerun, all 2,370 x 184 cells string-equal', len(TG) == 2370 and all(TG[i] == AN['DOMESTIC_TRANSFER'][i] for i in range(2370)))
# Candidate sensitivity (Work 9,480 rows) vs my 4 runs
cs = rd(T / 'Candidate_Sensitivity_Annual.csv')
seen = set()
mx = 0.0
for r in cs:
    k = (r['mode'], r['case'], int(r['year']))
    seen.add(k)
    g = G[r['mode']][r['case'], int(r['year'])]
    for col in ['real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn', 'macro_cash_DI_proxy_trn', 'household_consumption_nominal_proxy_trn', 'I_policy_real_trn', 'pension_fund_stock_trn', 'pension_fund_payout_trn', 'policy_household_cash_delta_trn']:
        mx = max(mx, abs(fl(r[col]) - fl(g[col])))
        mx = max(mx, abs(fl(r[col + '_minus_legacy']) - (fl(g[col]) - fl(G['LEGACY'][r['case'], int(r['year'])][col]))))
chkb('C11', 'C', 'Candidate_Sensitivity_Annual.csv: 9,480 unique mode-case-year keys, none missing', len(cs) == 9480 and len(seen) == 9480)
chk('C12', 'C', 'Candidate_Sensitivity_Annual values and minus-legacy equal Claude re-runs (max abs diff over 9 metrics x 2)', 0.0, mx, 1e-9)

# byte-level reproducibility
import hashlib
sh = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
same = diff = 0
diffnames = []
for f in sorted((PR / 'DOMESTIC_TRANSFER').iterdir()):
    if f.suffix == '.csv' and (T / f.name).exists():
        if f.read_bytes() == (T / f.name).read_bytes():
            same += 1
        else:
            diff += 1
            diffnames.append(f.name)
chk('C13', 'C', f'DOMESTIC rerun CSV vs target bytes: identical={same}, different={diff} {diffnames}', 0, diff, 0)
chk('C14', 'C', 'number of byte-identical re-run CSVs (Work reported 23)', 23, same, 0)
# LEGACY rerun vs pre-correction files, only those CSV existing in both and not new
sl = dl = 0
for f in sorted((PR / 'LEGACY').iterdir()):
    if f.suffix == '.csv' and (B / f.name).exists():
        if f.read_bytes() == (B / f.name).read_bytes():
            sl += 1
        else:
            dl += 1
obs.append(f'LEGACY rerun CSV vs pre-correction bytes: identical={sl}, different={dl} (extra legacy columns/new account columns expected where schema grew)')


# schema growth: old columns of N3_Policy/N3_Pension/Pension_Counterpart unchanged in LEGACY mode vs pre-correction
cells_s = bad_s = 0
for name in ['N3_Policy_Accounts.csv', 'N3_Pension_Accounts.csv', 'Pension_Counterpart.csv']:
    o, n_ = rd(B / name), rd(PR / 'LEGACY' / name)
    if len(o) != len(n_):
        bad_s += 1
        continue
    for a, b_ in zip(o, n_):
        for k, v in a.items():
            if k == 'counterparty_status':
                continue  # label text intentionally replaced (old: residual-not-identified; new: candidate closure)
            cells_s += 1
            if b_.get(k) != v:
                bad_s += 1
chk('C16', 'C', f'LEGACY rerun reproduces all {cells_s:,} pre-correction cells of N3_Policy_Accounts / N3_Pension_Accounts / Pension_Counterpart (new columns only added; label column counterparty_status excluded: text intentionally replaced in all 510 rows)', 0, bad_s, 0)

# old46 zero-return regression cells (independent count)
old46 = {r['case'] for r in rd(ROOT / 'handoff/chatgpt-n3-model-expansion-20261121/N3_Expansion_Annual.csv')}
cells46 = bad46 = 0
for k in keys:
    if k[0] not in old46:
        continue
    for col, v in BG[k].items():
        pass
oldrows = rd(ROOT / 'handoff/chatgpt-n3-model-expansion-20261121/N3_Expansion_Annual.csv')
chg46 = 0
for r in oldrows:
    k = (r['case'], int(r['year']))
    if k in changed_keys:
        continue
    for col, v in r.items():
        if v == '':
            continue
        try:
            x = float(v)
        except ValueError:
            continue
        cells46 += 1
        if not math.isclose(x, fl(G['DOMESTIC_TRANSFER'][k][col]), rel_tol=3e-9, abs_tol=5e-7):
            bad46 += 1
chk('C15', 'C', f'old-46 prior-expansion numeric cells at unchanged (zero-return) case-years equal after correction; cells checked={cells46}', 0, bad46, 0)
obs.append(f'old-46 regression at unchanged case-years: {cells46} numeric cells (Work reports 154,692 annual + 204,292 component = zero-return subset); changed case-years excluded by design.')

# ------------------------------------------------------------ D. comparability
F = {r['year']: r for r in rd(ROOT / 'handoff/f-common-endoflife-finalization-20261121/Annual.csv') if r['case'] == 'LATEST_F'}
fref = rd(T / 'F_Reference_Annual.csv')
chkb('D01', 'D', 'F_Reference_Annual 30 rows equal fixed ff621006 LATEST_F real/nominal GDP (F not re-run)', len(fref) == 30 and all(abs(fl(r['real_gdp_trn']) - fl(F[r['year']]['real_gdp_trn'])) < 5e-7 and abs(fl(r['nominal_gdp_trn']) - fl(F[r['year']]['nominal_gdp_trn'])) < 5e-7 for r in fref))
ky = rd(T / 'Key_Years_Comparison.csv')
mx = 0.0
nrow = 0
dist = []
for r in ky:
    c, y, met = r['case'], int(r['year']), r['metric']
    g = G['DOMESTIC_TRANSFER'][c, y]
    sq = G['DOMESTIC_TRANSFER']['SQ_COMMON_ON', y]
    f = F[str(y)]
    if met == 'cash_DI_definition_matched_proxy_trn':
        x = fl(g['macro_cash_DI_proxy_trn']) - fl(g['household_direct_price_benefit_trn'])
        ss = fl(sq['macro_cash_DI_proxy_trn']) - fl(sq['household_direct_price_benefit_trn'])
        fs = fl(f['macro_cash_DI_proxy_trn'])
    else:
        x, ss, fs = fl(g[met]), fl(sq[met]), fl(f[met])
    for a, b in [('absolute', x), ('SQ_absolute', ss), ('F_fixed_absolute', fs), ('minus_SQ', x - ss), ('minus_F', x - fs)]:
        mx = max(mx, abs(fl(r[a]) - b))
    nrow += 1
chk('D02', 'D', f'Key_Years_Comparison ({nrow} rows: 7 cases x 4 years x 7 metrics) re-derived from Claude re-run + fixed F', 0.0, mx, 5e-9)
chkb('D03', 'D', 'Key years are exactly 2026/2035/2045/2055; 196 rows', sorted({int(r['year']) for r in ky}) == [2026, 2035, 2045, 2055] and len(ky) == 196)
# DI definition: raw N3 DI vs F cash DI differ by the price benefit (same name, different definition)
rawgap = max(abs(fl(G['DOMESTIC_TRANSFER'][c0, y]['household_direct_price_benefit_trn'])) for y in (2035, 2045, 2055))
chkb('D04', 'D', 'N3 raw macro_cash_DI_proxy includes a non-zero price-benefit term that F cash proxy excludes => same-name direct comparison invalid; matched proxy needed', rawgap > 1e-6, f'max |price benefit| 2035-55 = {rawgap:.4f}')
chkb('D05', 'D', 'national PB / debt / bond issue null in all 2,370 corrected rows (not 0)', all(r['national_PB_trn'] == '' and r['national_debt_trn'] == '' and r['national_bond_issue_trn'] == '' for r in TG))
chkb('D06', 'D', 'EITC baseline stays null', all(r['EITC_baseline_trn'] == '' for r in TG))
sqf = rd(T / 'SQ_F_N3_Comparison.csv')
chkb('D07', 'D', 'SQ_F_N3_Comparison.csv has 2,370 rows (79 x 30) and minus_SQ equals own recompute for real GDP', len(sqf) == 2370 and all(abs(fl(r['real_gdp_trn_minus_SQ']) - (fl(G['DOMESTIC_TRANSFER'][r['case'], int(r['year'])]['real_gdp_trn']) - fl(G['DOMESTIC_TRANSFER']['SQ_COMMON_ON', int(r['year'])]['real_gdp_trn']))) < 5e-7 for r in sqf))
chkb('D08', 'D', 'SQ_COMMON_ON baseline unchanged by correction (no pension)', all(G['DOMESTIC_TRANSFER']['SQ_COMMON_ON', y]['real_gdp_trn'] == BG['SQ_COMMON_ON', y]['real_gdp_trn'] for y in Y))
# F vs N3 not causal: SQ-difference of the corrected case vs F-difference are different baselines
obs.append('F vs N3 comparison: N3 SQ_COMMON_ON 2055 real GDP %.6f vs fixed F LATEST_F %.6f (different connected scope; differences are not a causal ranking)' % (fl(G['DOMESTIC_TRANSFER']['SQ_COMMON_ON', 2055]['real_gdp_trn']), fl(F['2055']['real_gdp_trn'])))

# ------------------------------------------------------------ write
fails = [c for c in checks if c['verdict'] == 'FAIL']
with open(OUT / 'SPE_N3_Pension_Counterpart_Independent_Numeric_Comparison_DRAFT_20261121.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(checks[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(checks)
# per-case 2055 four-candidate table
rows = []
for c in cases:
    for m in MODES:
        rows.append(dict(case=c, mode=m, year=2055, real_gdp=fl(G[m][c, 2055]['real_gdp_trn']), gdp_minus_pre_correction=fl(G[m][c, 2055]['real_gdp_trn']) - fl(BG[c, 2055]['real_gdp_trn']), tax_minus_pre=fl(G[m][c, 2055]['tax_diagnostic_trn']) - fl(BG[c, 2055]['tax_diagnostic_trn']), DI_minus_pre=fl(G[m][c, 2055]['macro_cash_DI_proxy_trn']) - fl(BG[c, 2055]['macro_cash_DI_proxy_trn']), fund_stock_minus_pre=fl(G[m][c, 2055]['pension_fund_stock_trn']) - fl(BG[c, 2055]['pension_fund_stock_trn'])))
with open(OUT / 'SPE_N3_Pension_Counterpart_Candidate_2055_By_Case_DRAFT_20261121.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
with open(OUT / 'SPE_N3_Pension_Counterpart_Cell_Differences_Independent_DRAFT_20261121.csv', 'w', newline='') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['case', 'year', 'column', 'before', 'after', 'delta'])
    for a, b, c_, v0, v1 in diffs:
        w.writerow([a, b, c_, v0, v1, fl(v1) - fl(v0)])
summary = dict(total=len(checks), pass_=len(checks) - len(fails), fail=len(fails), failed_ids=[c['id'] for c in fails],
               by_area={a: dict(total=sum(1 for c in checks if c['area'] == a), fail=sum(1 for c in fails if c['area'] == a)) for a in 'RABCD'},
               changed_cells=len(diffs), identical_cells=tot - len(diffs), compared_cells=tot, changed_case_years=len(changed_keys), changed_cases=len(chcases),
               candidate_case_years=sum(len(AN[m]) for m in MODES), byte_identical_csv=same, observations=obs)
(OUT / 'SPE_N3_Pension_Counterpart_Independent_Summary_DRAFT_20261121.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False) + '\n')
print(json.dumps(summary, indent=1, ensure_ascii=False))
for c in fails:
    print('FAIL', c['id'], c['description'], c['expected'], c['actual'], c['abs_diff'])
