"""M6 provisional two-year state transition test.

Tests continuity, not forecast validity.
Parameters are provisional, not canonical.
"""

from math import isclose

from prototype import (
    SimulationState,
    transition_year,
    transition_year_demographics,
)


def advance(previous, *, risk_shock, aging_drag, tax_elasticity, expenditure_growth):
    """Return a fully carried-forward SimulationState."""

    demographics = transition_year_demographics(
        previous_state=previous,
        death_rate_coefficient=1.015,
        birth_decline_coefficient=0.975,
        phi=0.15,
        real_wage_growth_rate=0.0,
        net_migration=0.0,
    )

    population_growth = (
        demographics.population / previous.population - 1
    )

    result = transition_year(
        previous_state=previous,
        death_rate_coefficient=1.015,
        birth_decline_coefficient=0.975,
        phi=0.15,
        real_wage_growth_rate=0.0,
        net_migration=0.0,
        total_population_growth_rate=population_growth,
        aging_drag=aging_drag,
        base_growth_rate=0.01,
        consumption_stimulus_effect=0.0,
        investment_promotion_effect=0.0,
        education_effect=0.0,
        risk_shock=risk_shock,
        alpha=0.35,
        base_inflation_rate=0.02,
        risk_event_inflation_impact=0.0,
        consumption_tax_transitional_factor=0.0,
        tax_elasticity=tax_elasticity,
    )

    assert isclose(
        result.demographic_state.population,
        demographics.population,
    )

    real_gdp = previous.real_gdp * (
        1 + result.real_gdp_growth_rate
    )
    nominal_gdp = previous.nominal_gdp * (
        1 + result.nominal_gdp_growth_rate
    )

    revenue = min(
        result.tax_revenue_before_cap,
        nominal_gdp * 0.30,
    )
    expenditure = previous.expenditure * (1 + expenditure_growth)

    return SimulationState(
        year=previous.year + 1,
        real_gdp=real_gdp,
        nominal_gdp=nominal_gdp,
        tax_revenue=revenue,
        expenditure=expenditure,
        population=result.demographic_state.population,
        deaths=result.demographic_state.deaths,
        births=result.demographic_state.births,
    )


state_2026 = SimulationState(
    year=2026,
    real_gdp=580.0,
    nominal_gdp=600.0,
    tax_revenue=80.0,
    expenditure=108.0,
    population=121_500_000,
    deaths=1_590_000,
    births=640_000,
)

import json
from pathlib import Path

import sys

default_path = Path(__file__).resolve().parent.parent / "scenarios/m8_baseline.json"
scenario_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path
scenario = json.loads(scenario_path.read_text())
annual_inputs = {
    int(year): params
    for year, params in scenario["annual_inputs"].items()
}


from math import isfinite

required = {
    "risk_shock", "aging_drag",
    "tax_elasticity", "expenditure_growth",
}
assert annual_inputs, "No annual inputs"

years = sorted(annual_inputs)
assert years == list(range(2027, years[-1] + 1)), "Non-contiguous years"

for year, params in annual_inputs.items():
    assert set(params) == required, f"Invalid keys in {year}"
    assert all(
        type(value) in (int, float) and isfinite(value)
        for value in params.values()
    ), f"Invalid values in {year}"

states = {2026: state_2026}
for year, inputs in sorted(annual_inputs.items()):
    assert year == max(states) + 1
    states[year] = advance(states[year - 1], **inputs)

state_2027 = states[2027]
state_2028 = states[2028]

assert state_2027.year == 2027
assert state_2028.year == 2028
assert isclose(state_2027.population, 120_510_150)
assert isclose(state_2027.real_gdp, 551.8436, abs_tol=0.0001)
assert isclose(state_2027.nominal_gdp, 582.8727, abs_tol=0.0001)
assert isclose(state_2027.tax_revenue, 76.5745, abs_tol=0.0001)
assert isclose(state_2027.expenditure, 110.7, abs_tol=0.0001)

import json
from dataclasses import asdict

output = {
    "schema_version": "m10.1",
    "scenario": scenario_path.name,
    "profile": scenario["profile"],
    "years": {
        str(year): {
            **asdict(state),
            "bonds": max(
                state.expenditure - state.tax_revenue, 0
            ),
        }
        for year, state in sorted(states.items())
    },
}

print(json.dumps(output, indent=2, allow_nan=False))
