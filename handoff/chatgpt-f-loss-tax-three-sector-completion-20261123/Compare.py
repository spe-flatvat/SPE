"""Read the independent native runs and validate their annual bridges."""
import csv
import json
import math
import sys
from pathlib import Path

runtime, runs, out = map(Path, sys.argv[1:])
cases = ('BASE', 'MEDICAL', 'MEDICAL_REBASE', 'MEDICAL_2038')
metrics = '''real_gdp_trn nominal_gdp_trn modeled_VAT_trn VAT_national_reference_trn tax_diagnostic_trn
C_cash_trn C_reference_trn household_disposable_nominal_trn household_direct_price_benefit_trn
business_total_fixed_volume_benefit_trn government_purchase_benefit_trn insurer_VAT_balance_delta_trn
VAT_induced_investment_trn I_policy_real_trn government_partial_balance_proxy_trn
insurer_known_change_and_program_balance_trn consolidated_partial_balance_proxy_trn'''.split()
sector_fields = '''SQ_unrecoverable_trn F_input_VAT_trn F_unrecoverable_fixed_volume_trn new_input_credit_trn
rate_only_input_relief_trn output_VAT_fixed_volume_trn modeled_chain_VAT_trn chain_VAT_delta_trn
household_price_benefit_trn government_purchase_benefit_trn insurer_price_benefit_trn
business_buyer_benefit_trn provider_operating_benefit_fixed_volume_trn induced_investment_trn
medical_reimbursement_rebase_trn'''.split()
with (runtime / 'Fixed_F_BASE_OFF_Excerpt.csv').open() as stream:
    fixed = {int(r['year']): r for r in csv.DictReader(stream)}
annual, sectors, differences = [], [], []
checks = 0


def read(case, file):
    return json.loads((runs / case / (file + '.json')).read_text())


def check(a, b, key):
    global checks
    assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-7), (key, a, b)
    checks += 1


def dump(name, rows):
    with (out / name).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, rows[0].keys(), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


baseline = read('BASE', 'F_Actual_Annual')
base_sectors = {(r['year'], r['sector']): r for r in read('BASE', 'Sector')}
for case in cases:
    path = read(case, 'F_Actual_Annual')
    trace = read(case, 'F_Runtime_Trace')['years']
    start, flat = (2036, 2038) if case == 'MEDICAL_2038' else (2035, 2035)
    check(len(path), 30, case)
    check(path[0]['real_gdp_trn'], 580, case)
    check(path[0]['nominal_gdp_trn'], 600, case)
    for year, r, b, t in zip(range(2026, 2056), path, baseline, trace, strict=True):
        check(r['year'], year, case)
        ref = fixed[year]
        check(r['standard_rate'], .10 if year < 2030 else .08 if year < flat else .05, (case,year,'rate'))
        for key in metrics:
            if case == 'BASE' and key in ref:
                check(r[key], float(ref[key]), (year,key))
            if year < 2035:
                check(r[key], b[key], (case,year,key))
        check(r['population'], b['population'], case)
        check(r['education_effective_labor_added'], b['education_effective_labor_added'], case)
        check(r['land_principal_GDP_addition_trn'], 0, case)
        check(r['real_gdp_trn'], t['desired'] - t['unmet'], case)
        check(r['government_partial_balance_proxy_trn'] + r['insurer_known_change_and_program_balance_trn'],
              r['consolidated_partial_balance_proxy_trn'], case)
        annual.append(dict(case=case, year=year, **{k:r[k] for k in metrics},
                           fixed_SQ_real_GDP_trn=ref['SQ_real_GDP_trn'], fixed_N3_real_GDP_trn=ref['N3_real_GDP_trn'],
                           actual_general_government_PB='N/A'))
        differences.append(dict(case=case, year=year, **{k:r[k]-b[k] for k in metrics},
                                F_minus_fixed_SQ_real_GDP_trn=r['real_gdp_trn']-float(ref['SQ_real_GDP_trn']),
                                F_minus_fixed_N3_real_GDP_trn=r['real_gdp_trn']-float(ref['N3_real_GDP_trn'])))
    seen = set()
    for s in read(case, 'Sector'):
        year, name = s['year'], s['sector']
        if name not in ('medical', 'education', 'residential_rent'):
            continue
        key = year, name
        assert key not in seen
        seen.add(key)
        check(s['coverage'], max(0, min(1, (year-start+1)/3)), (case,key,'coverage'))
        check(s['F_unrecoverable_fixed_volume_trn'] + s['new_input_credit_trn'], s['F_input_VAT_trn'], (case,key))
        check(s['modeled_chain_VAT_trn'], s['seller_remittance_trn'] + s['upstream_VAT_trn'] - s['buyer_credit_trn'], (case,key))
        check(s['actual_transfer_residual_trn'], 0, (case,key))
        fixed_benefits = sum(s[k] for k in ('household_price_benefit_trn', 'government_purchase_benefit_trn',
                            'insurer_price_benefit_trn', 'business_buyer_benefit_trn',
                            'provider_operating_benefit_fixed_volume_trn', 'fixed_volume_government_delta_trn'))
        check(fixed_benefits, 0, (case,key))
        if case != 'MEDICAL_REBASE' or name != 'medical' or year < start:
            check(s['medical_reimbursement_rebase_trn'], 0, (case,key))
        else:
            assert 0 <= s['medical_reimbursement_rebase_trn'] <= s['new_input_credit_trn'] + 1e-10
            checks += 1
        if name != 'medical' and case != 'MEDICAL_2038':
            for field in sector_fields:
                check(s[field], base_sectors[key][field], (case,key,field))
        sectors.append(dict(case=case, year=year, sector=name, coverage=s['coverage'],
                            **{k:s[k] for k in sector_fields}))
    check(len(seen), 90, case)
out.mkdir(parents=True, exist_ok=True)
dump('Integrated_Annual.csv', annual)
dump('Integrated_Difference_vs_F.csv', differences)
dump('Sector_Annual.csv', sectors)
(out / 'Validation.json').write_text(json.dumps(dict(new_checks=checks, failed=0, integrated_rows=len(annual),
                                                   sector_rows=len(sectors)), indent=2)+'\n')
