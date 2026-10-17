"""Validation for the provisional m16.1 wage-output schema."""

from math import isfinite

from m12_validate import validate_result


def validate_m16_result(data):
    if not isinstance(data, dict):
        raise ValueError("Result must be an object")

    if data.get("schema_version") != "m16.1":
        raise ValueError("Unsupported result schema")

    years = data.get("years")
    if not isinstance(years, dict) or not years:
        raise ValueError("Invalid years")

    base_years = {}

    for year, state in years.items():
        if not isinstance(state, dict):
            raise ValueError(f"Invalid state: {year}")

        if "real_median_wage" not in state:
            raise ValueError(f"Missing wage: {year}")

        wage = state["real_median_wage"]

        if type(wage) not in (int, float):
            raise ValueError(f"Non-numeric wage: {year}")

        if not isfinite(wage) or wage <= 0:
            raise ValueError(f"Invalid wage: {year}")

        base_years[year] = {
            key: value
            for key, value in state.items()
            if key != "real_median_wage"
        }

    base_result = {
        **data,
        "schema_version": "m10.1",
        "years": base_years,
    }

    validate_result(base_result)

    return years
