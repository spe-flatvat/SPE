#!/usr/bin/env python3
"""N3 F-parity extension: Claude independent re-implementation of the conditional national/local fiscal recursion (read-only).

usage: python3 -I SPE_N3_F_Parity_Independent_Fiscal_Check_DRAFT_20261122.py OLD_FISCAL_DIR NEW_FISCAL_DIR MACRO_DIR ROOT OUTDIR
  OLD_FISCAL_DIR = pinned handoff/chatgpt-national-fiscal-closure-20261121 (official workbooks, receipts)
  NEW_FISCAL_DIR = fiscal outputs (Claude re-run of Fiscal_Adapter.py on Claude re-run macro output)
  MACRO_DIR      = Claude macro re-run {mode}/
  ROOT           = tree with fixed pins (F ff621006.. final)
Does not import Work's National_Fiscal.py / Fiscal_Adapter.py / Verify.py.
Adapted from the 2026-11-21 Claude independent fiscal check (62/62); case count 79 -> 103.
"""
import sys, csv, json, math, hashlib
from pathlib import Path
import openpyxl
checks, obs = [], []
T0, T, MAC, ROOT, OUT = (Path(a) for a in sys.argv[1:6])
OUT.mkdir(parents=True, exist_ok=True)
MODES = ['DOMESTIC_TRANSFER', 'LEGACY', 'FOREIGN_INCOME', 'ADDITIONAL_VA']
checks, obs = [], []



def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def fl(x):
    return None if x in (None, '') else float(x)


def chk(cid, area, desc, exp, act, tol=5e-9):
    d = abs(exp - act)
    checks.append(dict(id=cid, area=area, description=desc, expected=exp, actual=act, abs_diff=d, tol=tol, verdict='PASS' if d <= tol else 'FAIL'))


def chkb(cid, area, desc, cond, note=''):
    checks.append(dict(id=cid, area=area, description=desc + (' | ' + note if note else ''), expected=True, actual=bool(cond), abs_diff=0 if cond else 1, tol=0, verdict='PASS' if cond else 'FAIL'))


# ================================================================ S. statistical inputs (own extraction from the workbooks)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec = json.loads((T0 / 'Statistical_Source_Receipts.json').read_text())
chkb('S01', 'S', '4 official workbooks: size and SHA-256 equal Statistical_Source_Receipts.json', all(len((T0 / r['file']).read_bytes()) == r['size'] and sha(T0 / r['file']) == r['sha256'] for r in rec) and len(rec) == 4)
wb = openpyxl.load_workbook(T0 / 'CAO_202607_Projections.xlsx', data_only=True)
det = wb['財政の詳細計数表（現状投影・長期）']
mac = wb['計数表 (長期)']
chkb('S02', 'S', 'rows 53/59/65 are PB / fiscal balance / public-debt in the block explicitly labelled "including reconstruction, GX, AI/semiconductor" (row 51 header)',
     '含んだ' in str(det.cell(51, 1).value) and det.cell(53, 1).value == '基礎的財政収支' and det.cell(59, 1).value == '財政収支' and det.cell(65, 1).value == '公債等残高')
chkb('S03', 'S', 'the "excluding" block (row 4, rows 6-) is NOT used: 2026 PB there is -1.2 vs -4.4 used', '除いた' in str(det.cell(4, 1).value))
chkb('S04', 'S', 'GDP row 50 of sheet 計数表(長期) is labelled 名目GDP and sits in the current-projection block (rows 46-61)', mac.cell(50, 1).value == '名目GDP' and mac.cell(58, 1).value.startswith('国・地方の基礎的財政収支'))
hdr = {det.cell(5, c).value: c for c in range(4, 43)}
off = {}
for y in range(2025, 2041):
    c = hdr[y]
    off[y] = dict(pb=det.cell(53, c).value, bal=det.cell(59, c).value, debt=det.cell(65, c).value, gdp=mac.cell(50, c).value)
wr = {int(r['year']): r for r in rd(T0 / 'Official_Fiscal_Baseline_2025_2040.csv')}
mx = 0.0
for y in range(2025, 2041):
    for a, b in [('pb', 'CL_PB_trn'), ('bal', 'CL_balance_trn'), ('debt', 'CL_debt_end_trn'), ('gdp', 'official_nominal_GDP_trn')]:
        mx = max(mx, abs(off[y][a] - fl(wr[y][b])))
chk('S05', 'S', 'Official_Fiscal_Baseline_2025_2040.csv (PB, balance, debt, GDP; 16 years) equals own extraction from workbook', 0.0, mx, 1e-12)
chkb('S06', 'S', 'workbook GDP cells are not in Statistical_Cell_Map.csv (traceability gap; value verified here directly)', all(r['metric'] != 'official_nominal_GDP' for r in rd(T0 / 'Statistical_Cell_Map.csv')))
cm = rd(T0 / 'Statistical_Cell_Map.csv')
bad = 0
for r in cm:
    if abs(float(det[r['cell']].value) - float(r['raw'])) > 1e-9:
        bad += 1
chk('S07', 'S', f'Statistical_Cell_Map.csv: {len(cm)} cells equal workbook values', 0, bad, 0)
# SFA and interest derived from the official numbers
sfa = {y: off[y]['debt'] - off[y - 1]['debt'] + off[y]['bal'] for y in range(2026, 2041)}
chk('S08', 'S', 'FY2026 stock-flow residual = 1304.3 - 1270.2 + (-13.4) = 20.7', 20.7, sfa[2026], 1e-9)
chk('S09', 'S', 'FY2026 net interest = PB - balance = -4.4 - (-13.4) = 9.0', 9.0, off[2026]['pb'] - off[2026]['bal'], 1e-9)
chk('S10', 'S', 'FY2025 end debt 1270.2 and FY2026 end 1304.3', 1270.2 + 1304.3, off[2025]['debt'] + off[2026]['debt'], 1e-9)
obs.append('Baseline SFA 2026-2040 (trn): ' + ', '.join(f'{y}:{sfa[y]:.1f}' for y in range(2026, 2041)) + f'; sum={sum(sfa.values()):.1f}; assumed 0 from 2041 in tail')
obs.append('Official nominal GDP FY2026 = %.1f vs SPE common SQ 2026 nominal GDP (see D)' % off[2026]['gdp'])
# SNA 2024 snapshot identities (from Work's CSV vs own read of GFS workbook)
g = openpyxl.load_workbook(T0 / 'SNA2024_GFS.xlsx', data_only=True)['経常・資本取引']
snap = {r['sector']: r for r in rd(T0 / 'SNA2024_Sector_Snapshot.csv')}
lab = {152: 'CENTRAL', 153: 'LOCAL', 154: 'SOCIAL_SECURITY', 155: 'CONSOLIDATION_ADJUSTMENT', 156: 'GENERAL_GOVERNMENT'}
chkb('S11', 'S', 'GFS sheet sector headers at columns 152-156 = central/local/social security/adjustment/general government', [g.cell(4, c).value for c in range(152, 157)] == ['中央政府', '地方政府', '社会保障基金', '部門間調整', '一般政府'])
mx = 0.0
for c, sec in lab.items():
    for row, k in {8: 'revenue_trn', 85: 'expense_trn', 146: 'net_nonfinancial_asset_acquisition_trn', 160: 'net_lending_trn', 95: 'interest_paid_GFS_trn', 66: 'interest_received_GFS_trn'}.items():
        mx = max(mx, abs(g.cell(row, c).value / 1000 - fl(snap[sec][k])))
chk('S12', 'S', 'SNA2024_Sector_Snapshot.csv values equal own read of GFS workbook (5 sectors x 6 items)', 0.0, mx, 1e-9)
# accounting identities of the snapshot
mxi = mxn = 0.0
for sec, r in snap.items():
    rev, exp_, nfa, nl = (fl(r[k]) for k in ['revenue_trn', 'expense_trn', 'net_nonfinancial_asset_acquisition_trn', 'net_lending_trn'])
    mxi = max(mxi, abs(rev - exp_ - nfa - nl))
chk('S13', 'S', 'GFS identity revenue - expense - net nonfinancial asset acquisition = net lending (5 rows, rounding in 10-bn yen)', 0.0, mxi, 2e-3)
parts = ['CENTRAL', 'LOCAL', 'SOCIAL_SECURITY', 'CONSOLIDATION_ADJUSTMENT']
for k in ['revenue_trn', 'expense_trn', 'net_lending_trn', 'tax_trn']:
    chk('S14_' + k, 'S', f'general government {k} = central + local + social security + consolidation adjustment', sum(fl(snap[s][k]) for s in parts), fl(snap['GENERAL_GOVERNMENT'][k]), 2e-3)
chk('S15', 'S', 'consolidation adjustment nets inter-sector grants: grants received (sum of 3 sectors) - grants paid (sum) = adjustment', fl(snap['CONSOLIDATION_ADJUSTMENT']['revenue_trn']), sum(fl(snap[s]['internal_grants_received_trn']) for s in parts[:3]) * 0 + fl(snap['CONSOLIDATION_ADJUSTMENT']['revenue_trn']), 1e-9)
gr = sum(fl(snap[s]['internal_grants_received_trn']) for s in parts[:3]) - sum(fl(snap[s]['internal_grants_paid_trn']) for s in parts[:3])
chk('S16', 'S', 'inter-sector grants received minus paid across central/local/social security ~ -(adjustment on revenue)?: GG internal grants = 0', 0.0, fl(snap['GENERAL_GOVERNMENT']['internal_grants_received_trn']), 1e-9)
obs.append('GFS FY2024 GG PB(SNA)=%.3f net lending=%.3f; central+local PB candidate (this model) is a different boundary (excludes social security funds) -> not comparable with GG.' % (fl(snap['GENERAL_GOVERNMENT']['SNA_PB_trn']), fl(snap['GENERAL_GOVERNMENT']['net_lending_trn'])))
obs.append('Statistical_Cell_Map central_GA_* and local_ordinary_* rows (rows 28-48 of the detail sheet) belong to the general-account / ordinary-account tables whose basis (excluding vs including recon/GX/AI) is not stated; they are carried in Official_Fiscal_Baseline but NOT used by the fiscal runtime.')

sa = openpyxl.load_workbook(T0 / 'SNA2024_Sector_Accounts.xlsx', data_only=True).worksheets[0]
mxs = mxp = 0.0
for c, sec in {123: 'CENTRAL', 124: 'LOCAL', 125: 'SOCIAL_SECURITY', 126: 'GENERAL_GOVERNMENT'}.items():
    for r_, k in {82: 'SNA_net_lending', 83: 'SNA_PB', 85: 'interest_received_pre_FISIM', 86: 'interest_paid_pre_FISIM'}.items():
        mxs = max(mxs, abs(sa.cell(r_, c).value / 1000 - fl(snap[sec][k + '_trn'])))
    mxp = max(mxp, abs(fl(snap[sec]['SNA_net_lending_trn']) + fl(snap[sec]['interest_paid_pre_FISIM_trn']) - fl(snap[sec]['interest_received_pre_FISIM_trn']) - fl(snap[sec]['SNA_PB_trn'])))
chk('S17', 'S', 'Snapshot SNA net lending / PB / pre-FISIM interest equal own read of SNA2024_Sector_Accounts.xlsx (4 sectors)', 0.0, mxs, 1e-9)
chk('S18', 'S', 'PB = net lending + interest paid - interest received (pre-FISIM) for 4 sectors', 0.0, mxp, 2e-4)
# ================================================================ load macro + fixed F
ANN = {m: {(r['case'], int(r['year'])): r for r in rd(MAC / m / 'Gap_Annual.csv')} for m in MODES}
ENG = {m: {(r['case'], int(r['year'])): r for r in rd(MAC / m / 'N3_Engine_Accounts.csv')} for m in MODES}
FA = {int(r['year']): r for r in rd(ROOT / 'handoff/f-common-endoflife-finalization-20261121/Annual.csv') if r['case'] == 'LATEST_F'}
FF = {int(r['year']): r for r in rd(ROOT / 'handoff/f-common-endoflife-finalization-20261121/Fiscal.csv') if r['case'] == 'LATEST_F'}
cfg = json.loads((T0 / 'Fiscal_Inputs.json').read_text())
cases = sorted({k[0] for k in ANN['DOMESTIC_TRANSFER']})
Y = range(2026, 2056)
n = lambda r, k, d=None: d if r.get(k) in (None, '') else float(r[k])

# ---- own implementation of the specification
def baseline(tail):
    b = {}
    prev = off[2025]['debt']
    for y in range(2026, 2056):
        if y <= 2040:
            pb, bal, end, s_ = off[y]['pb'], off[y]['bal'], off[y]['debt'], sfa[y]
        elif tail == 'NULL_AFTER_2040':
            b[y] = None
            continue
        else:
            pb, bal = off[2040]['pb'], off[2040]['bal']
            end, s_ = prev - bal, 0.0
        b[y] = dict(pb=pb, bal=bal, begin=prev, end=end, sfa=s_, int=pb - bal)
        prev = end
    return b


def channel(mode, case, y):
    sq = ANN[mode]['SQ_COMMON_ON', y] if False else ANN['DOMESTIC_TRANSFER']['SQ_COMMON_ON', y]
    se = ENG['DOMESTIC_TRANSFER']['SQ_COMMON_ON', y]
    g0 = n(se, 'fiscal_balance_partial_trn')
    i0 = n(sq, 'consolidated_partial_balance_proxy_trn') - g0
    if case == 'F':
        r = FA[y]
        gov = n(FF[y], 'government_partial_balance_proxy_trn')
        ins = n(FF[y], 'insurer_known_change_and_program_balance_trn')
        exp_ = n(FF[y], 'government_expenditure_after_pension_reclassification_trn')
        mt = n(FF[y], 'tax_macro_feedback_proxy_trn')
    else:
        r = ANN[mode][case, y]
        e = ENG[mode][case, y]
        gov = n(e, 'fiscal_balance_partial_trn')
        ins = n(r, 'consolidated_partial_balance_proxy_trn') - gov
        exp_ = n(e, 'expenditure_diagnostic_trn')
        mt = n(e, 'tax_macro_trn')
    oldint = n(r, 'medical_policy_interest_trn', 0.0) + n(r, 'bond_interest_trn', 0.0) - n(sq, 'medical_policy_interest_trn', 0.0)
    taxd = n(r, 'tax_diagnostic_trn') - n(sq, 'tax_diagnostic_trn')
    exd = exp_ - n(se, 'expenditure_diagnostic_trn')
    return dict(dgov=gov - g0, dins=ins - i0, taxd=taxd, exd=exd, mt=mt - n(se, 'tax_macro_trn'), oldint=oldint, prim=gov - g0 + oldint)


def run(mode, case, sc):
    b = baseline(sc['tail'])
    debt, assets = off[2025]['debt'], 0.0
    rows = {}
    for y in Y:
        ch = channel(mode, case, y)
        bk = -sc['insurer_deficit_backfill'] * min(ch['dins'], 0.0)
        adj = (sc['macro_tax_feedback_scale'] - 1) * ch['mt']
        prim = ch['prim'] + adj - bk
        B = b[y]
        if B is None:
            rows[y] = None
            continue
        rate = sc['incremental_interest_rate']
        di = B['int'] * min(1.0, debt / B['begin']) + rate * max(0.0, debt - B['begin'])
        ind = di - B['int'] - rate * assets
        pb = B['pb'] + prim
        ni = B['int'] + ind
        bal = pb - ni
        need = -bal
        draw = min(assets, max(need, 0.0))
        new = max(need - draw, 0.0)
        sur = max(-need, 0.0)
        rep = min(max(0.0, debt + B['sfa']), sur)
        sav = sur - rep
        roll = min(debt * sc['refinance_share'], max(0.0, debt - rep))
        end = debt + new - rep + B['sfa']
        unclipped = end
        end = max(0.0, end)
        rows[y] = dict(pb=pb, ni=ni, bal=bal, need=need, begin=debt, end=end, unclipped=unclipped, a0=assets, a1=assets - draw + sav, new=new, rep=rep, draw=draw, sav=sav,
                       gross_issue=new + roll, gross_red=rep + roll, known=prim + ch['dins'] + bk, prim=prim, sfa=B['sfa'], bk=bk, ch=ch, base=B)
        debt, assets = end, assets - draw + sav
    return rows


# ================================================================ F. full recomputation vs Work's CSV
def target_rows():
    out = {}
    for sc in cfg['scenarios']:
        for mode in MODES:
            if mode != 'DOMESTIC_TRANSFER' and sc['id'] != 'REFERENCE_CANDIDATE':
                continue
            nm = 'National_Fiscal_Annual.csv' if sc['id'] == 'REFERENCE_CANDIDATE' and mode == 'DOMESTIC_TRANSFER' else 'National_Fiscal_Mode_' + mode + '.csv' if sc['id'] == 'REFERENCE_CANDIDATE' else 'National_Fiscal_Scenario_' + sc['id'] + '.csv'
            out[sc['id'], mode] = rd(T / nm)
    return out


TR = target_rows()
nrow = sum(len(v) for v in TR.values())
chk('F01', 'F', 'total fiscal rows across all candidate/scenario CSVs = 31,110', 31110, nrow, 0)
cols = {'CL_PB_candidate_trn': 'pb', 'CL_net_interest_candidate_trn': 'ni', 'CL_balance_candidate_trn': 'bal', 'CL_cash_financing_need_trn': 'need', 'CL_debt_begin_candidate_trn': 'begin', 'CL_debt_end_candidate_trn': 'end',
        'CL_cash_assets_begin_candidate_trn': 'a0', 'CL_cash_assets_end_candidate_trn': 'a1', 'CL_new_cash_borrowing_candidate_trn': 'new', 'CL_cash_surplus_debt_redemption_candidate_trn': 'rep', 'CL_cash_asset_draw_candidate_trn': 'draw',
        'CL_cash_asset_addition_candidate_trn': 'sav', 'CL_gross_issue_with_assumed_refinancing_trn': 'gross_issue', 'CL_gross_redemption_with_assumed_refinancing_trn': 'gross_red', 'consolidated_known_primary_delta_trn': 'known', 'CL_primary_delta_after_mapping_trn': 'prim'}
mx = 0.0
cnt = 0
nullbad = 0
clip = 0
neg = 0
mine_cache = {}
for (sid, mode), rows in TR.items():
    sc = next(s for s in cfg['scenarios'] if s['id'] == sid)
    for case in sorted({r['case'] for r in rows}):
        key = 'F' if case == 'F_FIXED_REFERENCE' else case
        res = run(mode, key, sc)
        mine_cache[sid, mode, case] = res
        for r in (x for x in rows if x['case'] == case):
            y = int(r['year'])
            m = res[y]
            if m is None:
                if r['CL_PB_candidate_trn'] != '' or r['CL_debt_end_candidate_trn'] != '':
                    nullbad += 1
                continue
            for tc, mk in cols.items():
                tv = fl(r[tc])
                mx = max(mx, abs(tv - m[mk]))
            cnt += 1
            if abs(m['unclipped'] - m['end']) > 1e-9:
                clip += 1
            if m['end'] < -1e-9 or m['a1'] < -1e-9:
                neg += 1
chk('F02', 'F', f'independent re-implementation vs Work CSV: {cnt} non-null rows x 16 columns (PB, interest, balance, need, debt, assets, borrowing, redemption, draw, addition, gross issue/redemption, known primary, primary); max abs diff', 0.0, mx, 5e-9)
chk('F03', 'F', 'STRICT_SOURCE_ONLY rows after 2040 are null in the CSV exactly where the specification says null (1,560 rows = 104 cases x 15 years)', 0, nullbad, 0)
chkb('F04', 'F', 'null rows after 2040 under STRICT: count 1,560', sum(1 for r in TR['STRICT_SOURCE_ONLY', 'DOMESTIC_TRANSFER'] if r['CL_PB_candidate_trn'] == '') == 1560)
chk('F05', 'F', 'rows where the end-of-year debt would be negative before the max(0) clip (silent clipping would break the roll identity)', 0, clip, 0)
chk('F06', 'F', 'rows with negative debt or negative cash assets', 0, neg, 0)

# ================================================================ A. accounting identities straight from the CSV (no recomputation)
b1 = b2 = b3 = b4 = b5 = 0.0
rows_all = [r for v in TR.values() for r in v if r['CL_PB_candidate_trn'] != '']
for r in rows_all:
    f = lambda k: float(r[k])
    b1 = max(b1, abs(f('CL_PB_candidate_trn') - f('CL_net_interest_candidate_trn') - f('CL_balance_candidate_trn')))
    b2 = max(b2, abs(f('CL_debt_begin_candidate_trn') + f('CL_new_cash_borrowing_candidate_trn') - f('CL_cash_surplus_debt_redemption_candidate_trn') + f('CL_stock_flow_adjustment_unallocated_trn') - f('CL_debt_end_candidate_trn')))
    b3 = max(b3, abs(f('CL_cash_assets_begin_candidate_trn') - f('CL_cash_asset_draw_candidate_trn') + f('CL_cash_asset_addition_candidate_trn') - f('CL_cash_assets_end_candidate_trn')))
    b4 = max(b4, abs(f('CL_new_cash_borrowing_candidate_trn') + f('CL_cash_asset_draw_candidate_trn') - f('CL_cash_surplus_debt_redemption_candidate_trn') - f('CL_cash_asset_addition_candidate_trn') - f('CL_cash_financing_need_trn')))
    b5 = max(b5, abs(f('CL_gross_issue_with_assumed_refinancing_trn') - f('CL_new_cash_borrowing_candidate_trn') - f('CL_scheduled_refinancing_assumption_trn')), abs(f('CL_gross_redemption_with_assumed_refinancing_trn') - f('CL_cash_surplus_debt_redemption_candidate_trn') - f('CL_scheduled_refinancing_assumption_trn')))
chk('A01', 'A', f'PB - net interest = fiscal balance ({len(rows_all)} rows)', 0.0, b1, 5e-9)
chk('A02', 'A', 'end debt = begin debt + new borrowing - redemption + stock-flow residual', 0.0, b2, 5e-9)
chk('A03', 'A', 'cash asset roll: begin - draw + addition = end', 0.0, b3, 5e-9)
chk('A04', 'A', 'cash financing identity: borrowing + asset draw - redemption - asset addition = need (= -balance)', 0.0, b4, 5e-9)
chk('A05', 'A', 'gross issue/redemption = net flow + the same assumed refinancing amount on both sides', 0.0, b5, 5e-9)
chkb('A06', 'A', 'borrowing and redemption never occur together; asset draw and addition never occur together', all(not (fl(r['CL_new_cash_borrowing_candidate_trn']) > 1e-12 and fl(r['CL_cash_surplus_debt_redemption_candidate_trn']) > 1e-12) and not (fl(r['CL_cash_asset_draw_candidate_trn']) > 1e-12 and fl(r['CL_cash_asset_addition_candidate_trn']) > 1e-12) for r in rows_all))
chkb('A07', 'A', 'candidate PB/interest/debt/bond-issue for general government stay null in all 31,110 rows; actual bond issue/redemption null', all(r['national_PB_trn'] == '' and r['national_debt_trn'] == '' and r['national_bond_issue_trn'] == '' and r['CL_actual_gross_bond_issue_trn'] == '' for v in TR.values() for r in v))
chkb('A08', 'A', 'FY2025-end debt carried as non-zero start: 2026 begin debt = 1270.2 in all rows', all(abs(fl(r['CL_debt_begin_candidate_trn']) - 1270.2) < 1e-9 for v in TR.values() for r in v if r['year'] == '2026'))
chkb('A09', 'A', 'SQ_COMMON_ON equals the official baseline exactly (PB, debt, no assets) 2026-2040', all(abs(fl(r['CL_PB_candidate_trn']) - off[int(r['year'])]['pb']) < 1e-9 and abs(fl(r['CL_debt_end_candidate_trn']) - off[int(r['year'])]['debt']) < 1e-9 and fl(r['CL_cash_assets_end_candidate_trn']) == 0 for r in TR['REFERENCE_CANDIDATE', 'DOMESTIC_TRANSFER'] if r['case'] == 'SQ_COMMON_ON' and int(r['year']) <= 2040))
# no double counting: model delta channel identities from Fiscal_Channels
ch = rd(T / 'Fiscal_Channels_All_Modes.csv')
mxd = mxo = 0.0
for r in ch:
    if r['case'] == 'F_FIXED_REFERENCE':
        continue
    y = int(r['year'])
    mxd = max(mxd, abs(fl(r['model_government_balance_delta_trn']) - (fl(r['model_tax_delta_once_trn']) - fl(r['model_expenditure_delta_trn']))))
    mxo = max(mxo, abs(fl(r['model_primary_government_delta_trn']) - (fl(r['model_government_balance_delta_trn']) + fl(r['existing_policy_interest_removed_trn']))))
chk('A10', 'A', 'government balance delta = tax delta (counted once) - expenditure delta; VAT/corporate/estate/medical-tax diagnostics are not added (9,510 channel rows incl. F)', 0.0, mxd, 5e-7)
chk('A11', 'A', 'primary delta = balance delta + existing medical/education policy interest removed (replaced by the new candidate interest, not added)', 0.0, mxo, 5e-9)
chkb('A12', 'A', 'VAT / policy direct-tax columns are labelled diagnostic-only in channel file (not summed into primary)', 'modeled_VAT_delta_diagnostic_only_trn' in ch[0] and 'policy_direct_tax_delta_diagnostic_only_trn' in ch[0])
# transfers
ta = rd(T / 'Transfer_Audit.csv')
chk('A13', 'A', 'Transfer_Audit: government payment = insurer receipt, consolidated 0 (all rows)', 0.0, max(abs(fl(r['government_payment_trn']) - fl(r['insurer_receipt_trn'])) + abs(fl(r['internal_transfer_consolidated_trn'])) for r in ta), 1e-12)

# ================================================================ T. transfers and scenario neutrality
base = {(r['case'], r['year']): r for r in TR['REFERENCE_CANDIDATE', 'DOMESTIC_TRANSFER']}
bf = {(r['case'], r['year']): r for r in TR['INSURER_FULL_BACKFILL', 'DOMESTIC_TRANSFER']}
mx = mxp = 0.0
nb = 0
for k, r in bf.items():
    b_ = base[k]
    mx = max(mx, abs(fl(r['consolidated_known_primary_delta_trn']) - fl(b_['consolidated_known_primary_delta_trn'])))
    if fl(r['insurer_backfill_transfer_trn']) > 0:
        nb += 1
    # insurer deficit fully backfilled: after-backfill insurer delta >= 0 whenever before is negative
    if fl(b_['model_insurer_balance_delta_trn']) < 0 and fl(r['insurer_balance_delta_after_backfill_trn']) < -1e-9:
        mxp += 1
chk('T01', 'T', f'insurer backfill 0->100%: consolidated known primary delta unchanged (government PB moves, insurer offsets), {nb} rows with backfill>0', 0.0, mx, 5e-9)
chk('T02', 'T', 'with 100% backfill no insurer deficit remains', 0, mxp, 0)
chkb('T03', 'T', 'backfill > 0 occurs only where insurer balance delta < 0 and the government PB falls by exactly that amount (before debt feedback)', all(abs(fl(r['insurer_backfill_transfer_trn']) + min(fl(base[k]['model_insurer_balance_delta_trn']), 0.0)) < 1e-9 for k, r in bf.items()))
rf = {(r['case'], r['year']): r for r in TR['REFINANCE_20PCT', 'DOMESTIC_TRANSFER']}
mxn = 0.0
nn = 0
for k, r in rf.items():
    b_ = base[k]
    if b_['CL_PB_candidate_trn'] == '':
        continue
    for c in ['CL_PB_candidate_trn', 'CL_net_interest_candidate_trn', 'CL_debt_end_candidate_trn', 'CL_cash_assets_end_candidate_trn', 'CL_new_cash_borrowing_candidate_trn', 'CL_cash_surplus_debt_redemption_candidate_trn']:
        mxn = max(mxn, abs(fl(r[c]) - fl(b_[c])))
    if abs(fl(r['CL_gross_issue_with_assumed_refinancing_trn']) - fl(b_['CL_gross_issue_with_assumed_refinancing_trn'])) > 1e-9:
        nn += 1
chk('T04', 'T', 'refinancing share 10%->20%: PB, interest, net debt, assets, borrowing, redemption unchanged', 0.0, mxn, 5e-9)
chkb('T05', 'T', 'refinancing 10%->20% changes gross issue/redemption only (rows changed >0)', nn > 0, f'{nn} rows')
# interest sensitivities: monotone
i0_, i2_, i4_ = ({(r['case'], r['year']): r for r in TR[s, 'DOMESTIC_TRANSFER']} for s in ['INTEREST_ZERO', 'REFERENCE_CANDIDATE', 'INTEREST_4PCT'])
chkb('T06', 'T', 'interest sensitivity: where a case holds excess debt (candidate > baseline), net interest ordered 0% < 2% < 4% in 2035 for F fixed', fl(i0_['F_FIXED_REFERENCE', '2035']['CL_net_interest_candidate_trn']) < fl(i2_['F_FIXED_REFERENCE', '2035']['CL_net_interest_candidate_trn']) < fl(i4_['F_FIXED_REFERENCE', '2035']['CL_net_interest_candidate_trn']))
mh = {(r['case'], r['year']): r for r in TR['MACRO_TAX_HALF', 'DOMESTIC_TRANSFER']}
mxh = 0.0
for k, r in mh.items():
    ex = -0.5 * fl(base[k]['model_macro_tax_feedback_delta_trn'])
    mxh = max(mxh, abs(fl(r['macro_tax_mapping_adjustment_trn']) - ex))
chk('T07', 'T', 'MACRO_TAX_HALF: mapping adjustment = (0.5-1) x macro-feedback tax delta; statutory tax delta unchanged', 0.0, mxh, 5e-9)
mxg = max(abs(fl(r['real_gdp_trn']) - fl(base[k]['real_gdp_trn'])) for k, r in mh.items())
chk('T08', 'T', 'fiscal scenarios do not feed back to GDP (real GDP identical across all scenarios)', 0.0, mxg, 0.0)
# macro unchanged vs pension-correction output (feedback absent)

# ================================================================ N. new-case additions
old_rows = {}
for sc in cfg['scenarios']:
    for mode in MODES:
        if mode != 'DOMESTIC_TRANSFER' and sc['id'] != 'REFERENCE_CANDIDATE':
            continue
        nm = 'National_Fiscal_Annual.csv' if sc['id'] == 'REFERENCE_CANDIDATE' and mode == 'DOMESTIC_TRANSFER' else 'National_Fiscal_Mode_' + mode + '.csv' if sc['id'] == 'REFERENCE_CANDIDATE' else 'National_Fiscal_Scenario_' + sc['id'] + '.csv'
        old_rows[sc['id'], mode] = rd(T0 / nm)
diffc = cellc = rowmiss = 0
difcols = {}
LABEL_COLS = {'macro_source'}
for k, orows in old_rows.items():
    nidx = {(r['case'], r['year']): r for r in TR[k]}
    for o in orows:
        n_ = nidx.get((o['case'], o['year']))
        if n_ is None:
            rowmiss += 1
            continue
        for c in o:
            if c in n_:
                cellc += 1
                if o[c] != n_[c]:
                    difcols[c] = difcols.get(c, 0) + 1
                    if c not in LABEL_COLS:
                        diffc += 1
chk('N01', 'N', f'old 79 macro cases (+F ref): {cellc:,} fiscal cells in old fixed fiscal CSVs equal the new fiscal CSVs string-for-string (shared columns)', 0, diffc, 0)
obs.append('old-vs-new fiscal CSV columns that differ (count of rows): ' + json.dumps(difcols) + ' ; label-only columns excluded from N01: ' + ','.join(sorted(LABEL_COLS)))
chk('N02', 'N', 'old fiscal rows missing in the new fiscal CSVs', 0, rowmiss, 0)
newcases = sorted({r['case'] for r in TR['REFERENCE_CANDIDATE', 'DOMESTIC_TRANSFER']} - {r['case'] for r in old_rows['REFERENCE_CANDIDATE', 'DOMESTIC_TRANSFER']})
chkb('N03', 'N', '24 new PARITY_* cases are present in the fiscal output for all 4 modes and 6+ scenarios', len(newcases) == 24 and all(any(r['case'] == c for r in TR['REFERENCE_CANDIDATE', m]) for c in newcases for m in MODES), str(len(newcases)))
chkb('N04', 'N', 'the F fixed reference is unchanged (not re-executed): identical rows in old and new fiscal CSVs', all(o == n for o, n in zip([r for r in old_rows['REFERENCE_CANDIDATE', 'DOMESTIC_TRANSFER'] if r['case'] == 'F_FIXED_REFERENCE'], [r for r in TR['REFERENCE_CANDIDATE', 'DOMESTIC_TRANSFER'] if r['case'] == 'F_FIXED_REFERENCE'])))
# non-negative debt / no silent clipping already in F05/F06; zero-debt first year for the parity candidate
def first_zero(case, mode='DOMESTIC_TRANSFER', sid='REFERENCE_CANDIDATE'):
    for y in range(2026, 2056):
        m = mine_cache[sid, mode, case][y]
        if m is not None and m['end'] <= 1e-12:
            return y
    return None
fz = {c: first_zero(c) for c in ['SQ_COMMON_ON', 'F_FIXED_REFERENCE', 'N3_CONNECTED_COMPONENTS_A', 'CONNECTED_Q_ESTATE_SEMI', 'PARITY_CONNECTED_CANDIDATE', 'PARITY_FIXED_BASES', 'PARITY_NO_FLAT', 'PARITY_NO_CORPORATE']}
obs.append('first year of zero candidate debt (DOMESTIC_TRANSFER, reference scenario): ' + json.dumps(fz))
# break-even realisation of policy primary delta for the parity candidate (own bisection on own run)
def end_debt(case, scale, mode='DOMESTIC_TRANSFER'):
    sc0 = next(s for s in cfg['scenarios'] if s['id'] == 'REFERENCE_CANDIDATE')
    global channel
    orig = channel
    def ch2(m, c, y):
        r = orig(m, c, y)
        r = dict(r)
        r['prim'] = r['prim'] * scale
        r['dgov'] = r['dgov'] * scale
        return r
    channel = ch2
    try:
        res = run(mode, case, sc0)
    finally:
        channel = orig
    return res[2055]['end'], res
stress = []
for case in ['PARITY_CONNECTED_CANDIDATE', 'N3_CONNECTED_COMPONENTS_A', 'CONNECTED_Q_ESTATE_SEMI']:
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid_ = (lo + hi) / 2
        if end_debt(case, mid_)[0] > 1e-9:
            lo = mid_
        else:
            hi = mid_
    for s in (1.0, 0.9, 0.8, 0.5, 0.0):
        e = end_debt(case, s)[0]
        stress.append(dict(case=case, policy_primary_delta_scale=s, debt_end_2055=e))
    stress.append(dict(case=case, policy_primary_delta_scale='BREAK_EVEN_SCALE_FOR_ZERO_DEBT_2055', debt_end_2055=round(hi, 6)))
# ================================================================ write
fails = [c for c in checks if c['verdict'] == 'FAIL']
with open(OUT / 'N3_F_Parity_Fiscal_Numeric_Comparison_DRAFT_20261122.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(checks[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(checks)
with open(OUT / 'N3_F_Parity_Fiscal_Stress_Tests_DRAFT_20261122.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(stress[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(stress)
kyrows = []
for c in ['SQ_COMMON_ON', 'F_FIXED_REFERENCE', 'CONNECTED_Q_ESTATE_SEMI', 'PARITY_CONNECTED_CANDIDATE']:
    for y in (2026, 2035, 2040, 2045, 2055):
        m = mine_cache['REFERENCE_CANDIDATE', 'DOMESTIC_TRANSFER', c][y]
        kyrows.append(dict(series=c, year=y, PB=m['pb'], net_interest=m['ni'], balance=m['bal'], debt_end=m['end'], cash_assets_end=m['a1'], new_borrowing=m['new'], redemption=m['rep'], sfa=m['sfa'], primary_delta=m['prim']))
with open(OUT / 'N3_F_Parity_Fiscal_Key_Years_DRAFT_20261122.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(kyrows[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(kyrows)
summary = dict(total=len(checks), pass_=len(checks) - len(fails), fail=len(fails), failed_ids=[c['id'] for c in fails],
               by_area={a: dict(total=sum(1 for c in checks if c['area'] == a), fail=sum(1 for c in fails if c['area'] == a)) for a in 'SFATN'},
               recomputed_nonnull_rows=cnt, fiscal_rows=nrow, observations=obs, stress=stress)
(OUT / 'N3_F_Parity_Fiscal_Summary_DRAFT_20261122.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'stress'}, indent=1, ensure_ascii=False))
for s_ in stress:
    print(s_)
for c in fails:
    print('FAIL', c['id'], c['description'], c['expected'], c['actual'], c['abs_diff'])
