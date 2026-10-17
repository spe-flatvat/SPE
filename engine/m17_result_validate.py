"""Validation for the provisional m17.1 Gini-output schema."""

from math import isfinite

from m12_validate import validate_result


def validate_m17_result(data):
    if not isinstance(data, dict):
        raise ValueError("Result must be an object")

    if data.get("schema_version") != "m17.1":
        raise ValueError("Unsupported result schema")

    years = data.get("years")
    if not isinstance(years, dict) or not years:
        raise ValueError("Invalid years")

    wage_presence = set()
    base_years = {}

    for year, state in years.items():
        if not isinstance(state, dict):
            raise ValueError(f"Invalid state: {year}")

        if "gini_coefficient" not in state:
            raise ValueError(f"Missing Gini coefficient: {year}")

        gini = state["gini_coefficient"]

        if type(gini) not in (int, float):
            raise ValueError(f"Non-numeric Gini coefficient: {year}")

        if not isfinite(gini) or not 0 <= gini <= 1:
            raise ValueError(f"Invalid Gini coefficient: {year}")

        has_wage = "real_median_wage" in state
        wage_presence.add(has_wage)

        if has_wage:
            wage = state["real_median_wage"]

            if type(wage) not in (int, float):
                raise ValueError(f"Non-numeric wage: {year}")

            if not isfinite(wage) or wage <= 0:
                raise ValueError(f"Invalid wage: {year}")

        base_years[year] = {
            key: value
            for key, value in state.items()
            if key not in {
                "gini_coefficient",
                "real_median_wage",
            }
        }

    if len(wage_presence) != 1:
        raise ValueError("Inconsistent wage field presence")

    base_result = {
        **data,
        "schema_version": "m10.1",
        "years": base_years,
    }

    validate_result(base_result)

    return years
