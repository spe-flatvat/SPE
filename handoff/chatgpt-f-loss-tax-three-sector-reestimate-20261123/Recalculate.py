"""Reproduce the non-adopted VAT satellite with Python 3."""
import csv
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from Prior_VAT_Model import rates, ramp, sector_account

ROOT = Path(__file__).resolve().parent
I = json.loads((ROOT / 'Diagnostic_Inputs.json').read_text())
NAMES = ('medical', 'education', 'residential_rent')


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def run(destination):
    destination.mkdir(parents=True, exist_ok=True)
    comparison, accounts, historical = [], [], []
    checks = 0

    def check(condition):
        nonlocal checks
        if not condition:
            raise AssertionError(f'check {checks + 1}')
        checks += 1

    with (ROOT / 'Fixed_F_BASE_OFF_Excerpt.csv').open(encoding='utf-8') as stream:
        fixed = {int(r['year']): r for r in csv.DictReader(stream) if r['scenario'] == 'BASE_OFF'}
    check(list(fixed) == list(range(2026, 2056)))
    check(float(fixed[2026]['real_gdp_trn']) == 580)
    check(float(fixed[2026]['nominal_gdp_trn']) == 600)
    check(float(fixed[2026]['SQ_real_GDP_trn']) == float(fixed[2026]['N3_real_GDP_trn']) == 580)
    check(all(r['trigger_active'] == 'False' for r in fixed.values()))

    growth = 1 + I['reference']['sector_growth']
    burden = sum(n * b for _, n, b, a in I['medical']) / 1e9
    compensation = sum(n * a for _, n, b, a in I['medical']) / 1e9
    medical_input_2025 = 2 * burden * growth / .10
    private_rent = sum(n * 1000 * rent * 12 for n, rent in I['rents']) / 1e12
    old_2025 = [s['R2025'] * s['formerly_exempt_share'] * s['input_ratio'] * .10 for s in I['sectors']]
    check(math.isclose(sum(old_2025), 1.24))
    check(math.isclose(sum(pair[0] for pair in I['annex']), 1.7))
    check(math.isclose(sum(pair[1] for pair in I['annex']), 2.55))
    for name, count, b, a in I['medical']:
        historical.append(dict(scope=name, year=2024, burden_5pp_trn=count*b/1e9,
                               compensation_5pp_trn=count*a/1e9, conditional_10pct_equivalent_trn=2*count*b/1e9))
    historical.append(dict(scope='three_facility_types', year=2024, burden_5pp_trn=burden,
                           compensation_5pp_trn=compensation, conditional_10pct_equivalent_trn=2*burden))
    for year, f in fixed.items():
        real, sq, n3 = (float(f[k]) for k in ('real_gdp_trn', 'SQ_real_GDP_trn', 'N3_real_GDP_trn'))
        comparison.append(dict(year=year, fixed_F_real_GDP_trn=real, fixed_F_nominal_GDP_trn=f['nominal_gdp_trn'],
                               fixed_SQ_real_GDP_trn=sq, fixed_N3_real_GDP_trn=n3,
                               fixed_F_minus_SQ_trn=real-sq, fixed_F_minus_N3_trn=real-n3,
                               fixed_F_tax_diagnostic_trn=f['tax_diagnostic_trn'],
                               fixed_F_partial_balance_trn=f['consolidated_partial_balance_proxy_trn'],
                               diagnostic_delta_GDP='N/A', diagnostic_delta_investment='N/A',
                               diagnostic_delta_total_tax='N/A', diagnostic_delta_partial_balance='N/A'))
        for case, start, rate5, length in [('VAT_DEFAULTS', 2035, 2035, 3),
                                          ('ANNEX_FINISH_2038', 2036, 2038, 3)]:
            scenario = dict(I['defaults'], base_start=start, year5=rate5, base_ramp=length)
            std = rates(year, scenario)[0]
            fraction = ramp(year, start, length)
            check(0 <= fraction <= 1)
            check(std == (.10 if year < 2030 else .08 if year < rate5 else .05))
            for sector, old_input in zip(I['sectors'], old_2025):
                name = sector['id']
                old = sector_account(I, scenario, sector, year, std)
                check(math.isclose(old['SQ_unrecoverable_trn'], old_input * growth**(year-2025)))
                check(math.isclose(old['coverage'], fraction))
                check(math.isclose(old['actual_transfer_residual_trn'], 0, abs_tol=1e-10))
                med = name == 'medical'
                new = {}
                if med:
                    taxable_base = sector['R2025'] * sector['formerly_exempt_share']
                    new = sector_account(I, scenario, dict(sector, input_ratio=medical_input_2025/taxable_base), year, std)
                    check(math.isclose(new['SQ_unrecoverable_trn'], 2 * burden * growth**(year-2024)))
                    check(math.isclose(new['new_input_credit_trn'],
                                       new['SQ_unrecoverable_trn'] * std/.10 * fraction))
                    check(math.isclose(new['actual_transfer_residual_trn'], 0, abs_tol=1e-10))
                    check(math.isclose(new['F_unrecoverable_fixed_volume_trn'] + new['new_input_credit_trn'],
                                       new['F_input_VAT_trn']))
                    check(all(new[k] >= 0 for k in ('new_input_credit_trn', 'F_unrecoverable_fixed_volume_trn',
                                                    'output_VAT_fixed_volume_trn')))
                # Separate partial coverage envelopes from medical's replacement run.
                cap = {'education': I['edu_capital_oku']/10000*.10,
                       'residential_rent': I['repair_oku']/10000*.10}.get(name)
                na = 'N/A'
                accounts.append(dict(
                    scenario=case, year=year, sector=name, standard_rate=std, coverage=fraction,
                    old_SQ_unrecoverable_trn=old['SQ_unrecoverable_trn'], old_new_credit_trn=old['new_input_credit_trn'],
                    old_output_VAT_trn=old['output_VAT_fixed_volume_trn'],
                    old_chain_VAT_delta_trn=old['chain_VAT_delta_trn'],
                    old_HH_price_benefit_trn=old['household_price_benefit_trn'],
                    old_provider_benefit_trn=old['provider_operating_benefit_fixed_volume_trn'],
                    partial_replacement_SQ_unrecoverable_trn=new.get('SQ_unrecoverable_trn', na),
                    partial_replacement_remaining_unrecoverable_trn=new.get('F_unrecoverable_fixed_volume_trn', na),
                    partial_replacement_new_credit_trn=new.get('new_input_credit_trn', na),
                    partial_replacement_rate_only_relief_trn=new.get('rate_only_input_relief_trn', na),
                    partial_replacement_output_VAT_trn=new.get('output_VAT_fixed_volume_trn', na),
                    partial_replacement_chain_VAT_delta_trn=new.get('chain_VAT_delta_trn', na),
                    partial_replacement_chain_VAT_change_in_F_level_trn=new['modeled_chain_VAT_trn']-old['modeled_chain_VAT_trn'] if med else na,
                    partial_replacement_difference_in_F_minus_own_SQ_trn=new['chain_VAT_delta_trn']-old['chain_VAT_delta_trn'] if med else na,
                    partial_replacement_national_share_delta_vs_own_SQ_trn=new['chain_VAT_delta_trn']*I['reference']['national_share'] if med else na,
                    partial_replacement_investment_allocation_candidate_trn=new.get('induced_investment_trn', na),
                    partial_replacement_wage_allocation_candidate_trn=new.get('wages_trn', na),
                    partial_replacement_HH_price_benefit_trn=new.get('household_price_benefit_trn', na),
                    partial_replacement_provider_benefit_trn=new.get('provider_operating_benefit_fixed_volume_trn', na),
                    partial_replacement_insurer_price_benefit_trn=new.get('insurer_price_benefit_trn', na),
                    partial_replacement_public_buyer_price_benefit_trn=new.get('government_purchase_benefit_trn', na),
                    partial_spend_VAT_ceiling_current_trn=na if cap is None else cap*growth**(year-2024),
                    partial_new_credit_ceiling_trn=na if cap is None else cap*growth**(year-2024)*std/.10*fraction,
                    private_rent_full_pass_output_only_trn=private_rent*growth**(year-2023)*std*fraction
                    if name == 'residential_rent' else na))
    check(len(accounts) == 180)
    check((len({(r['scenario'],r['year'],r['sector']) for r in accounts})) == len(accounts))
    for row in accounts:
        if row['year'] < (2035 if row['scenario'] == 'VAT_DEFAULTS' else 2036):
            check(row['coverage'] == 0 and row['old_new_credit_trn'] == 0 and row['old_output_VAT_trn'] == 0)
    for case, final in [('VAT_DEFAULTS', 2037), ('ANNEX_FINISH_2038', 2038)]:
        check(all(r['coverage'] == 1 for r in accounts if r['scenario']==case and r['year']==final))
    write_csv(destination / 'Medical_Historical_2024.csv', historical)
    write_csv(destination / 'Annual_VAT_Diagnostic_2026_2055.csv', accounts)
    write_csv(destination / 'Annual_F_SQ_N3_Comparison.csv', comparison)
    (destination / 'Validation.json').write_text(json.dumps(dict(new_checks=checks, failures=0, annual_sector_rows=len(accounts),
                                                                  comparison_rows=len(comparison)), indent=2)+'\n')


if __name__ == '__main__':
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
