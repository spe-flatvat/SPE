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

    state_2027 = transition_year_demographics(
        previous_state=state_2026,
        death_rate_coefficient=1.0,
        birth_decline_coefficient=1.0,
        phi=0.15,
        real_wage_growth_rate=0.0,
        net_migration=0.0,
    )

    print(f"State 2026: {state_2026}")
    print(f"State 2027: {state_2027}")
