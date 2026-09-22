from dataclasses import dataclass


@dataclass
class SimulationState:
    """Carried-forward simulation state defined by SPE v6."""

    year: int
    real_gdp: float
    nominal_gdp: float
    tax_revenue: float
    expenditure: float
    population: float
    deaths: float
    births: float

@dataclass
class TransitionResult:
    """Annual results computable from the current SPE v6 baseline."""

    demographic_state: SimulationState
    labor_force_growth_rate: float
    real_gdp_growth_rate: float
    inflation_rate: float
    nominal_gdp_growth_rate: float
    tax_revenue_before_cap: float

def transition_deaths(
    previous_deaths: float,
    death_rate_coefficient: float,
) -> float:
    """Apply the SPE v6 Death Count Transition."""
    return previous_deaths * death_rate_coefficient

def transition_births(
    previous_births: float,
    birth_decline_coefficient: float,
    phi: float,
    real_wage_growth_rate: float,
) -> float:
    """Apply the SPE v6 Birth Count Transition."""
    return (
        previous_births
        * birth_decline_coefficient
        * (1 + phi * real_wage_growth_rate)
    )

def transition_population(
    previous_population: float,
    births: float,
    deaths: float,
    net_migration: float,
) -> float:
    """Apply the SPE v6 Population Transition."""
    return previous_population + (births - deaths) + net_migration

def calculate_labor_force_growth_rate(
    total_population_growth_rate: float,
    aging_drag: float,
) -> float:
    """Apply the SPE v6 Labor Force Growth Rate composition rule."""
    return total_population_growth_rate + aging_drag

def calculate_real_gdp_growth_rate(
    base_growth_rate: float,
    consumption_stimulus_effect: float,
    investment_promotion_effect: float,
    education_effect: float,
    risk_shock: float,
    alpha: float,
    labor_force_growth_rate: float,
) -> float:
    """Apply the SPE v6 F-Scenario Real GDP Growth Rate composition rule."""
    return (
        base_growth_rate
        + consumption_stimulus_effect
        + investment_promotion_effect
        + education_effect
        - risk_shock
        + (1 - alpha) * labor_force_growth_rate
    )

def calculate_inflation_rate(
    base_inflation_rate: float,
    risk_event_inflation_impact: float,
    consumption_tax_transitional_factor: float,
) -> float:
    """Apply the SPE v6 Inflation Rate composition rule."""
    return (
        base_inflation_rate
        + risk_event_inflation_impact
        + consumption_tax_transitional_factor
    )

def calculate_nominal_gdp_growth_rate(
    real_gdp_growth_rate: float,
    inflation_rate: float,
) -> float:
    """Apply the SPE v6 Nominal GDP Growth Rate composition rule."""
    return real_gdp_growth_rate + inflation_rate

def calculate_tax_revenue_before_cap(
    previous_tax_revenue: float,
    nominal_gdp_growth_rate: float,
    tax_elasticity: float,
) -> float:
    """Apply the SPE v6 Tax Revenue Transition before the unresolved cap."""
    return previous_tax_revenue * (
        1 + nominal_gdp_growth_rate * tax_elasticity
    )

def transition_year_demographics(
    previous_state: SimulationState,
    death_rate_coefficient: float,
    birth_decline_coefficient: float,
    phi: float,
    real_wage_growth_rate: float,
    net_migration: float,
) -> SimulationState:
    """Advance one year using the implemented demographic transitions only."""

    deaths = transition_deaths(
        previous_deaths=previous_state.deaths,
        death_rate_coefficient=death_rate_coefficient,
    )

    births = transition_births(
        previous_births=previous_state.births,
        birth_decline_coefficient=birth_decline_coefficient,
        phi=phi,
        real_wage_growth_rate=real_wage_growth_rate,
    )

    population = transition_population(
        previous_population=previous_state.population,
        births=births,
        deaths=deaths,
        net_migration=net_migration,
    )

    return SimulationState(
        year=previous_state.year + 1,
        real_gdp=previous_state.real_gdp,
        nominal_gdp=previous_state.nominal_gdp,
        tax_revenue=previous_state.tax_revenue,
        expenditure=previous_state.expenditure,
        population=population,
        deaths=deaths,
        births=births,
    )

def transition_year(
    previous_state: SimulationState,
    *,
    death_rate_coefficient: float,
    birth_decline_coefficient: float,
    phi: float,
    real_wage_growth_rate: float,
    net_migration: float,
    total_population_growth_rate: float,
    aging_drag: float,
    base_growth_rate: float,
    consumption_stimulus_effect: float,
    investment_promotion_effect: float,
    education_effect: float,
    risk_shock: float,
    alpha: float,
    base_inflation_rate: float,
    risk_event_inflation_impact: float,
    consumption_tax_transitional_factor: float,
    tax_elasticity: float,
) -> TransitionResult:
    """Advance one year through all currently implementable SPE v6 transitions."""

    demographic_state = transition_year_demographics(
        previous_state=previous_state,
        death_rate_coefficient=death_rate_coefficient,
        birth_decline_coefficient=birth_decline_coefficient,
        phi=phi,
        real_wage_growth_rate=real_wage_growth_rate,
        net_migration=net_migration,
    )

    labor_force_growth_rate = calculate_labor_force_growth_rate(
        total_population_growth_rate=total_population_growth_rate,
        aging_drag=aging_drag,
    )

    real_gdp_growth_rate = calculate_real_gdp_growth_rate(
        base_growth_rate=base_growth_rate,
        consumption_stimulus_effect=consumption_stimulus_effect,
        investment_promotion_effect=investment_promotion_effect,
        education_effect=education_effect,
        risk_shock=risk_shock,
        alpha=alpha,
        labor_force_growth_rate=labor_force_growth_rate,
    )

    inflation_rate = calculate_inflation_rate(
        base_inflation_rate=base_inflation_rate,
        risk_event_inflation_impact=risk_event_inflation_impact,
        consumption_tax_transitional_factor=consumption_tax_transitional_factor,
    )

    nominal_gdp_growth_rate = calculate_nominal_gdp_growth_rate(
        real_gdp_growth_rate=real_gdp_growth_rate,
        inflation_rate=inflation_rate,
    )

    tax_revenue_before_cap = calculate_tax_revenue_before_cap(
        previous_tax_revenue=previous_state.tax_revenue,
        nominal_gdp_growth_rate=nominal_gdp_growth_rate,
        tax_elasticity=tax_elasticity,
    )

    return TransitionResult(
        demographic_state=demographic_state,
        labor_force_growth_rate=labor_force_growth_rate,
        real_gdp_growth_rate=real_gdp_growth_rate,
        inflation_rate=inflation_rate,
        nominal_gdp_growth_rate=nominal_gdp_growth_rate,
        tax_revenue_before_cap=tax_revenue_before_cap,
    )

if __name__ == "__main__":
    state_2026 = SimulationState(
        year=2026,
        real_gdp=0.0,
        nominal_gdp=0.0,
        tax_revenue=0.0,
        expenditure=0.0,
        population=0.0,
        deaths=0.0,
        births=0.0,
    )

    result_2027 = transition_year(
        previous_state=state_2026,
        death_rate_coefficient=1.0,
        birth_decline_coefficient=1.0,
        phi=0.15,
        real_wage_growth_rate=0.0,
        net_migration=0.0,
        total_population_growth_rate=0.0,
        aging_drag=0.0,
        base_growth_rate=0.0,
        consumption_stimulus_effect=0.0,
        investment_promotion_effect=0.0,
        education_effect=0.0,
        risk_shock=0.0,
        alpha=0.35,
        base_inflation_rate=0.0,
        risk_event_inflation_impact=0.0,
        consumption_tax_transitional_factor=0.0,
        tax_elasticity=1.5,
    )

    print(f"State 2026: {state_2026}")
    print(f"Transition Result 2027: {result_2027}")
