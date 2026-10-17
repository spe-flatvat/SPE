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

annual_inputs = {
    2027: {"aging_drag": -0.005, "tax_elasticity": 1.5, "expenditure_growth": 0.025, "risk_shock": 0.05},
    2028: {"aging_drag": -0.005, "tax_elasticity": 1.5, "expenditure_growth": 0.025, "risk_shock": 0.00},
    2029: {"aging_drag": -0.005, "tax_elasticity": 1.5, "expenditure_growth": 0.025, "risk_shock": 0.00},
}

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

print("=== SPE M7 ANNUAL INPUT RUNNER ===")
print("Profile: provisional, not canonical")

for state in states.values():
    bonds = max(state.expenditure - state.tax_revenue, 0.0)

    print(
        f"{state.year} | "
        f"Population: {state.population:,.0f} | "
        f"Real GDP: {state.real_gdp:.4f} | "
        f"Nominal GDP: {state.nominal_gdp:.4f} | "
        f"Revenue: {state.tax_revenue:.4f} | "
        f"Expenditure: {state.expenditure:.4f} | "
        f"Bonds: {bonds:.4f}"
    )

assert state_2028.population < state_2027.population
assert state_2028.expenditure > state_2027.expenditure
assert state_2028.tax_revenue != state_2027.tax_revenue

assert state_2028.year == 2028
assert states[2029].year == 2029
assert len(states) == 4
print("M7 ANNUAL INPUT RUNNER: PASS")
