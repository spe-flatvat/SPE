"""M5 provisional one-year numerical dry run.

Historical inputs and explicit test assumptions.
Not a canonical Neutral or F scenario.
"""

from math import isclose

from prototype import SimulationState, transition_year
from prototype import transition_year_demographics

# Units: GDP, revenue, expenditure = trillion JPY
# Population, deaths, births = persons
state = SimulationState(
    year=2026,
    real_gdp=580.0,
    nominal_gdp=600.0,
    tax_revenue=80.0,
    expenditure=108.0,  # Inferred: 80 + 28
    population=121_500_000,
    deaths=1_590_000,
    births=640_000,
)

# M5 test assumptions, not canonical parameters
wage_growth = 0.0
aging_drag = -0.005
risk_inflation = 0.0
expenditure_growth = 0.025
tax_elasticity = 1.5

# Resolve population growth before annual transition
demographics = transition_year_demographics(
    previous_state=state,
    death_rate_coefficient=1.015,
    birth_decline_coefficient=0.975,
    phi=0.15,
    real_wage_growth_rate=wage_growth,
    net_migration=0.0,
)

population_growth = (
    demographics.population / state.population - 1
)

result = transition_year(
    previous_state=state,
    death_rate_coefficient=1.015,
    birth_decline_coefficient=0.975,
    phi=0.15,
    real_wage_growth_rate=wage_growth,
    net_migration=0.0,
    total_population_growth_rate=population_growth,
    aging_drag=aging_drag,
    base_growth_rate=0.01,
    consumption_stimulus_effect=0.0,
    investment_promotion_effect=0.0,
    education_effect=0.0,
    risk_shock=0.05,
    alpha=0.35,
    base_inflation_rate=0.02,
    risk_event_inflation_impact=risk_inflation,
    consumption_tax_transitional_factor=0.0,
    tax_elasticity=tax_elasticity,
)

# Provisional GDP level transitions from historical TSUBAME
real_gdp = state.real_gdp * (
    1 + result.real_gdp_growth_rate
)
nominal_gdp = state.nominal_gdp * (
    1 + result.nominal_gdp_growth_rate
)

# Cap application is provisional; this case does not hit cap
tax_ceiling = nominal_gdp * 0.30
revenue = min(result.tax_revenue_before_cap, tax_ceiling)

expenditure = state.expenditure * (
    1 + expenditure_growth
)
bonds = max(expenditure - revenue, 0.0)

# Invariant checks
assert result.demographic_state.year == 2027
assert isclose(
    result.demographic_state.population,
    state.population
    + result.demographic_state.births
    - result.demographic_state.deaths,
)
assert revenue <= tax_ceiling
assert isclose(bonds, max(expenditure - revenue, 0.0))
assert isclose(real_gdp, 551.8436, abs_tol=0.0001)
assert isclose(nominal_gdp, 582.8727, abs_tol=0.0001)

print("=== SPE M5 NUMERIC DRY RUN ===")
print("Profile: provisional, not canonical")
print(f"Year: {result.demographic_state.year}")
print(f"Population: {result.demographic_state.population:,.0f}")
print(f"Real GDP: {real_gdp:.4f} tn JPY")
print(f"Nominal GDP: {nominal_gdp:.4f} tn JPY")
print(f"Tax Revenue: {revenue:.4f} tn JPY")
print(f"Expenditure: {expenditure:.4f} tn JPY")
print(f"Bond Issuance: {bonds:.4f} tn JPY")
print("Invariant checks: PASS")
