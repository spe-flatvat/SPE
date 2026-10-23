"""Endpoint metrics derived from validated annual outputs.

M18 scope:
    Calculate endpoint and period metrics without modifying
    simulation states or introducing scenario parameters.

    Results ending before 2055 are provisional evaluations,
    not official 2055 endpoint evaluations.

    No automatic judgment is made for bond divergence,
    because its quantitative threshold is not specified.
"""

from m12_validate import validate_result
from m16_result_validate import validate_m16_result
from m17_result_validate import validate_m17_result


def evaluate_result(data):
    schema = data.get("schema_version") if isinstance(data, dict) else None

    validators = {
        "m10.1": validate_result,
        "m16.1": validate_m16_result,
        "m17.1": validate_m17_result,
    }

    if schema not in validators:
        raise ValueError("Unsupported result schema")

    years = validators[schema](data)
    ordered = sorted(map(int, years))

    start_year = ordered[0]
    end_year = ordered[-1]

    if start_year != 2026:
        raise ValueError(
            "Evaluation must start in 2026"
        )

    if end_year <= start_year:
        raise ValueError("At least two years required")

    first = years[str(start_year)]
    last = years[str(end_year)]

    initial_gdp = first["real_gdp"]

    if initial_gdp <= 0:
        raise ValueError("Initial real GDP must be positive")

    cagr = (
        (last["real_gdp"] / initial_gdp)
        ** (1 / (end_year - start_year))
        - 1
    )

    tax_ratios = []

    for year in ordered:
        state = years[str(year)]
        nominal_gdp = state["nominal_gdp"]

        if nominal_gdp <= 0:
            raise ValueError(
                f"Nominal GDP must be positive: {year}"
            )

        tax_ratios.append(
            state["tax_revenue"] / nominal_gdp
        )

    return {
        "start_year": start_year,
        "end_year": end_year,
        "is_2055_endpoint": end_year == 2055,
        "real_gdp_endpoint": last["real_gdp"],
        "real_gdp_cagr": cagr,
        "real_median_wage_endpoint": last.get(
            "real_median_wage"
        ),
        "gini_coefficient_endpoint": last.get(
            "gini_coefficient"
        ),
        "population_endpoint": last["population"],
        "tax_to_gdp_ratio_max": max(tax_ratios),
        "bond_issuance_endpoint": last["bonds"],
    }
