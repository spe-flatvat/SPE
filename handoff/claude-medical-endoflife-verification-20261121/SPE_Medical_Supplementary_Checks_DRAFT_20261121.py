#!/usr/bin/env python3
# Claude supplementary checks for the medical / end-of-life module (Commit d2578751...). Read-only on the repository tree;
# counterfactual engine runs write only to a temp directory.  Usage: python3 -I <this> <repo_root_dir_at_d257875>
import sys, os, csv, json, math, re, tempfile, importlib.util, io, contextlib, copy
R = sys.argv[1]; D = os.path.join(R, 'handoff/f-medical-common-20261121')
sys.path.insert(0, D)
IN = json.load(open(os.path.join(D, 'Inputs.json')))
def rd(f): return list(csv.DictReader(open(os.path.join(D, f))))
A = {(r['case'], int(r['year'])): r for r in rd('Annual.csv')}; REP = open(os.path.join(D, 'Report.md'), encoding='utf-8').read()
EDU = {int(r['year']): r for r in csv.DictReader(open(os.path.join(R, 'handoff/f-education-20261121/Annual.csv'))) if r['case'] == 'COMBINED'}
g = lambda c, y=2055, k='real_gdp_trn': float(A[(c, y)][k])
# ---- 1  Report.md tables vs CSV
chk = miss = 0
for line in REP.splitlines():
    m = re.match(r'\|([A-Z_]+)\|(\d+\.\d+)\|(-?\d+\.\d+)\|(-?\d+\.\d+)\|(\d+\.\d+)\|(-?\d+\.\d+)\|$', line)
    if m and (m.group(1), 2055) in A:
        c = m.group(1); a = A[(c, 2055)]
        exp = [g(c), g(c) - float(EDU[2055]['real_gdp_trn']), g(c) - g('OLD_MEDICAL_REMOVED'), float(a['macro_cash_DI_proxy_trn']), float(a['consolidated_partial_balance_proxy_trn'])]
        got = [float(x) for x in m.groups()[1:]]
        chk += 1
        if any(abs(e - o) > 6e-7 for e, o in zip(exp, got)): miss += 1; print('  TABLE MISMATCH', c, exp, got)
print('1 Report GDP table rows checked', chk, 'mismatch', miss)
ce = {(r['case'], int(r['year'])): r for r in rd('Common_EndOfLife.csv')}
for c in ('COMMON_F_HOUSEHOLD_STRESS',):
    pass
st = [(y, float(ce[('COMMON_ONLY', y)]['household_direct_cash_burden_delta_trn']), float(ce[('COMMON_F_HOUSEHOLD_STRESS', y)]['household_direct_cash_burden_delta_trn']), float(ce[('COMMON_F_HOUSEHOLD_STRESS', y)]['household_total_economic_burden_delta_trn'])) for y in (2035, 2040, 2055)]
print('  stress table (CSV, COMMON_F_HOUSEHOLD_STRESS: shares COMMON_F full-F case, so common-only stress is recomputed in recalc script)', [(y, round(a, 6), round(b, 6), round(c2, 6)) for y, a, b, c2 in st])
# ---- 2  timeline and protection by behaviour (COMMON_ONLY rows)
print('2 timeline COMMON_ONLY (year: law, impl_phase, national_op, registry adoption, chosen transitions, immunity flag)')
for y in (2026, 2027, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2040, 2045, 2055):
    r = ce[('COMMON_ONLY', y)]; print('  ', y, r['law_passed'], r['implementation_phase'][:5], r['national_operation'], r['record_adoption'][:6], '%.0f' % float(r['chosen_transitions']), r['procedural_legal_immunity_available'])
const = {k: {ce[(c, y)][k] for c in {x[0] for x in ce} for y in range(2026, 2056)} for k in ['registration_changes_benefits', 'registration_changes_copay', 'registration_changes_palliative_priority', 'registration_voluntary', 'revocation_allowed', 'latest_wish_priority', 'active_life_termination', 'treatment_automatically_stopped', 'unknown_wish_assumed_refusal']}
print('  protection flags (all cases x years, distinct values):', {k: sorted(v) for k, v in const.items()})
src = open(os.path.join(D, 'CommonEndOfLife.py'), encoding='utf-8').read()
print('  protection flags are literal constants in the row dict (not computed):', all(re.search(k + r'=[01]\b', src) for k in ['registration_changes_benefits', 'registration_changes_copay', 'registration_changes_palliative_priority', 'registration_voluntary', 'revocation_allowed', 'latest_wish_priority', 'active_life_termination']), '| unknown_wish_assumed_refusal literal 0:', 'unknown_wish_assumed_refusal=0' in src)
import FMedical, CommonEndOfLife
c0 = IN['common_parameters']; d = dict(price_index=1., population_scale=1., registry_population=1e8, clinical_strata=IN['clinical_strata'])
fin = IN['common_financing']; base = CommonEndOfLife.calculate(2040, d, c0, fin)
print('  behavioural: adoption_target 0 / 1 -> chosen', CommonEndOfLife.calculate(2040, d, {**c0, 'adoption_target': 0.}, fin)['chosen_transitions'], CommonEndOfLife.calculate(2040, d, {**c0, 'adoption_target': 1.}, fin)['chosen_transitions'], '(base %.0f); patient payment per clinical euro identical:' % base['chosen_transitions'],
      abs(base['patient_payment_delta_trn'] / base['clinical_cost_delta_trn'] - fin['HOUSEHOLD']) < 1e-12, '| proxy_designation_target 0 leaves chosen:', CommonEndOfLife.calculate(2040, d, {**c0, 'proxy_designation_target': 0.}, fin)['chosen_transitions'] == base['chosen_transitions'])
print('  confirmed_share=0 or explicit_preference_share=0 => chosen:', CommonEndOfLife.calculate(2040, d, {**c0, 'confirmed_share': 0.}, fin)['chosen_transitions'], CommonEndOfLife.calculate(2040, d, {**c0, 'explicit_preference_share': 0.}, fin)['chosen_transitions'])
print('  unknown-wish pathway: no_record_episodes (2040) %.0f, chosen from them: 0 by construction (chosen<=willing<=recorded*...) ; fallback multidisciplinary episodes %.0f are cost-only' % (base['no_record_episodes'], base['multidisciplinary_fallback_episodes']))
print('  set independence: CommonEndOfLife imports only math; F modules import from it:', re.findall(r'^import .*|^from .*', src, re.M), '| FMedical->', re.findall(r'^from CommonEndOfLife.*', open(os.path.join(D, 'FMedical.py'), encoding='utf-8').read(), re.M))
# ---- 3  engine counterfactuals (uses the Work's pinned engine via Model.py; inputs vary only)
spec = importlib.util.spec_from_file_location('wmodel', os.path.join(D, 'Model.py')); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
need = {'OLD_MEDICAL_REMOVED', 'COMMON_ONLY', 'COPAY_ONLY', 'PROVIDER_ONLY', 'F_COMBINED', 'COMMON_F_MEDIUM', 'ZERO_CLINICAL_SAVING', 'COST_INCREASE', 'COMMON_ZERO_SAVING'}
zero_common = {'destination_cost_yen': {'HOME': 1270000, 'FACILITY': 1270000, 'HOSPITAL': 1270000}, 'palliative_additional_yen': 0.0}
extra = [dict(id='FX_P_S0', provider=True, prevention_saving_trn=0.0), dict(id='FX_PC_S0', provider=True, copay=True, prevention_saving_trn=0.0), dict(id='FX_PZC', common=True, provider=True, copay=True, prevention_saving_trn=0.0, common_overrides=zero_common),
         dict(id='FX_PC_ND', provider=True, copay=True, demand_elasticity=0.0, necessary_care_share=0.0), dict(id='FX_C_ONLY_NOHEALTH', copay=True, health_worker_equivalent=0.0, necessary_care_share=0.0)]
def runcases(ablate=()):
    inp = copy.deepcopy(IN); inp['cases'] = [c for c in inp['cases'] if c['id'] in need] + extra
    orig = FMedical.Medical.step
    def step(self, y):
        w = orig(self, y)
        for k in ablate: w[k] = 0.
        return w
    FMedical.Medical.step = step
    try:
        with tempfile.TemporaryDirectory() as td:
            ip = os.path.join(td, 'in.json'); json.dump(inp, open(ip, 'w'))
            with contextlib.redirect_stdout(io.StringIO()): M.run(ip, td)
            return {(r['case'], int(r['year'])): r for r in csv.DictReader(open(os.path.join(td, 'Annual.csv')))}
    finally: FMedical.Medical.step = orig
base = runcases()
ok = all(abs(float(base[(c, 2055)]['real_gdp_trn']) - g(c)) < 1e-9 for c in need)
print('3 counterfactual harness reproduces original 2055 GDP for', len(need), 'cases:', ok)
G = lambda r, c: float(r[(c, 2055)]['real_gdp_trn']); off = G(base, 'OLD_MEDICAL_REMOVED')
print('  2055 real GDP minus OFF (兆円):', {c: round(G(base, c) - off, 4) for c in ['COMMON_ONLY', 'COPAY_ONLY', 'PROVIDER_ONLY', 'F_COMBINED', 'FX_P_S0', 'FX_PC_S0', 'ZERO_CLINICAL_SAVING', 'FX_PZC', 'COST_INCREASE', 'COMMON_ZERO_SAVING', 'FX_PC_ND']})
print('  ZERO_CLINICAL_SAVING - F_COMBINED = %.6f' % (G(base, 'ZERO_CLINICAL_SAVING') - G(base, 'F_COMBINED')))
print('  decomposition (sequential, provider on): F_COMBINED -> remove copay (PROVIDER_ONLY) %+.4f -> saving 0 (FX_P_S0) %+.4f -> common zero-cost cfg (ZERO) %+.4f ; total %+.4f' % (G(base, 'PROVIDER_ONLY') - G(base, 'F_COMBINED'), G(base, 'FX_P_S0') - G(base, 'PROVIDER_ONLY'), G(base, 'ZERO_CLINICAL_SAVING') - G(base, 'FX_P_S0'), G(base, 'ZERO_CLINICAL_SAVING') - G(base, 'F_COMBINED')))
print('  other order: F_COMBINED -> saving 0 (FX_PC_S0) %+.4f -> remove copay (FX_P_S0) %+.4f -> common (ZERO) %+.4f' % (G(base, 'FX_PC_S0') - G(base, 'F_COMBINED'), G(base, 'FX_P_S0') - G(base, 'FX_PC_S0'), G(base, 'ZERO_CLINICAL_SAVING') - G(base, 'FX_P_S0')))
chs = ['service_production_nominal_delta_trn', 'investment_nominal_delta_trn', 'health_effective_labor_added', 'household_cash_delta_trn', 'government_cost_delta_trn']
print('  channel ablation: 2055 GDP(F_COMBINED), GDP(ZERO), gap  [channel zeroed in the engine hook]')
for a in [()] + [(k,) for k in chs] + [tuple(chs)]:
    r = runcases(a) if a else base
    print('   ', ','.join(k.split('_')[0] + '_' + k.split('_')[1] for k in a) if a else 'none', '%.4f %.4f gap %.4f' % (G(r, 'F_COMBINED'), G(r, 'ZERO_CLINICAL_SAVING'), G(r, 'ZERO_CLINICAL_SAVING') - G(r, 'F_COMBINED')))
for c in ('PROVIDER_ONLY', 'COPAY_ONLY', 'F_COMBINED', 'ZERO_CLINICAL_SAVING', 'COST_INCREASE'):
    r = A[(c, 2055)]; print('  ', c, 'service_prod %.4f invest %.4f labour %.0f cash %.4f govcost %.4f clinical %.4f' % tuple(float(r[k]) for k in ['service_production_nominal_delta_trn', 'investment_nominal_delta_trn', 'health_effective_labor_added', 'household_cash_delta_trn', 'government_cost_delta_trn', 'clinical_cost_delta_trn']))
print('  marginal GDP per 1兆円 of extra clinical cost, from COST_INCREASE vs ZERO: %.3f' % ((G(base, 'COST_INCREASE') - G(base, 'ZERO_CLINICAL_SAVING')) / (float(A[('COST_INCREASE', 2055)]['clinical_cost_delta_trn']) - float(A[('ZERO_CLINICAL_SAVING', 2055)]['clinical_cost_delta_trn']))))
# ---- 4  transfer-closure test content
ma = rd('Medical_Accounts.csv')
r = next(x for x in ma if x['case'] == 'COMMON_ONLY' and x['year'] == '2040'); f = lambda k: float(r[k])
print('4 closure: ancillary receipts equal extra household cash burden + subsidy by construction ->', abs(f('ancillary_and_income_counterpart_trn') - (float(ce[('COMMON_ONLY', 2040)]['extra_household_cash_burden_trn']) + float(ce[('COMMON_ONLY', 2040)]['proxy_subsidy_trn']))) < 1e-15, '; transfer_residual', r['transfer_residual_trn'])
# ---- 5  extra: share of GDP effect inside the old-vs-new ranges, regression
leg = [r for r in rd('Legacy_Medical.csv') if r['case'] == 'OLD_MEDICAL_REMOVED']; print('5 old medical removed: legacy columns all zero in OLD_MEDICAL_REMOVED:', all(float(r[k]) == 0. for r in leg for k in ['old_medical_government_trn', 'old_medical_insurer_trn', 'old_medical_hub_capital_trn']))
print('  legacy preserved (LATEST_EDUCATION_FIXED) 2055 government legacy medical: %s ; education COMBINED GDP 2055 %s vs LATEST_EDUCATION_FIXED %s' % ([r['old_medical_government_trn'] for r in rd('Legacy_Medical.csv') if r['case'] == 'LATEST_EDUCATION_FIXED' and r['year'] == '2055'], EDU[2055]['real_gdp_trn'], A[('LATEST_EDUCATION_FIXED', 2055)]['real_gdp_trn']))
# ---- 6  education regression (480 cells), old medical removal, VAT file
cols = ['real_gdp_trn', 'nominal_gdp_trn', 'tax_diagnostic_trn', 'fiscal_balance_partial_trn', 'C_cash_trn', 'total_unassigned_funding_trn', 'labor_force_population_proxy', 'household_disposable_nominal_trn']
cells = bad = 0
for c in ('LATEST_EDUCATION_FIXED', 'ADDITIONAL_ZERO'):
    for y in range(2026, 2056):
        for k in cols:
            cells += 1; bad += abs(float(A[(c, y)][k]) - float(EDU[y][k])) > 1e-9 * max(1., abs(float(EDU[y][k])))
print('6 education COMBINED regression (independent comparison with f-education Annual.csv): cells', cells, 'mismatch', bad)
zero = [c for c in ['OLD_MEDICAL_REMOVED', 'COMMON_ONLY', 'COPAY_ONLY', 'PROVIDER_ONLY', 'COMMON_F_MEDIUM'] for y in range(2026, 2056) if all(float(A[(c, y)][k]) == 0. for k in ['old_medical_government_trn', 'old_medical_insurer_trn', 'old_medical_hub_capital_trn'])]
print('  old medical flows exactly zero in removed-legacy cases (case-years):', len(zero), '/150 ; legacy preserved cases nonzero in:', sum(1 for c in ('LATEST_EDUCATION_FIXED', 'ADDITIONAL_ZERO') for y in range(2026, 2056) if float(A[(c, y)]['old_medical_government_trn']) != 0.))
vat = rd('VAT_No_DoubleCount.csv'); print('  VAT file columns:', [k for k in vat[0] if 'medical' in k or 'credit' in k][:8], 'rows', len(vat))
vk = [k for k in vat[0] if k not in ('case', 'year', 'sector', 'sector_id')]
a = {(r['case'], r['year']): r for r in vat if r.get('sector', r.get('sector_id')) == 'medical'}
d = max(abs(float(a[('F_COMBINED', '2055')][k]) - float(a[('OLD_MEDICAL_REMOVED', '2055')][k])) for k in vk if a[('F_COMBINED', '2055')][k] not in ('', None) and k not in ('case',) and re.match(r'^-?[\d.]+(e-?\d+)?$', a[('F_COMBINED', '2055')][k]) and re.match(r'^-?[\d.]+(e-?\d+)?$', a[('OLD_MEDICAL_REMOVED', '2055')][k]))
print('  medical-sector VAT/credit columns: max |F_COMBINED - OLD_MEDICAL_REMOVED| in 2055 =', d, '(0 means the medical sector VAT lines do not respond to the new medical flows)')
# ---- 7  baseline medical demand path vs population
rows = {int(r['year']): r for r in rd('Medical_Accounts.csv') if r['case'] == 'OLD_MEDICAL_REMOVED'}
ce2 = {int(r['year']): r for r in rd('Common_EndOfLife.csv') if r['case'] == 'COMMON_ONLY'}
print('7 baseline medical bill (nominal 兆円) / clinical episodes: ', ', '.join('%d: %.1f / %.0f' % (y, float(rows[y]['baseline_medical_bill_trn']), float(ce2[y]['clinical_demand_episodes'])) for y in (2026, 2035, 2040, 2055)))
print('  clinical episodes follow total population scale (aging-structure not used): 2055/2026 = %.3f' % (float(ce2[2055]['clinical_demand_episodes']) / float(ce2[2026]['clinical_demand_episodes'])))
cm = [(y, float(ce2[y]['clinical_cost_delta_trn']), float(ce2[y]['common_program_cost_trn']), float(ce2[y]['total_resource_cost_delta_trn'])) for y in (2035, 2040, 2055)]
print('  COMMON_ONLY clinical / program / total resource cost (兆円):', [(y, round(a, 4), round(b, 4), round(c2, 4)) for y, a, b, c2 in cm])
