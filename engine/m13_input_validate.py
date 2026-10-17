import math

REQUIRED_PARAMS = {
    "risk_shock",
    "aging_drag",
    "tax_elasticity",
    "expenditure_growth",
}


def validate_scenario(data):
    if not isinstance(data, dict):
        raise ValueError("Scenario must be an object")

    if set(data) != {"profile", "annual_inputs"}:
        raise ValueError("Invalid scenario fields")

    profile = data["profile"]
    if not isinstance(profile, str) or not profile.strip():
        raise ValueError("Invalid profile")

    annual = data["annual_inputs"]
    if not isinstance(annual, dict) or not annual:
        raise ValueError("Invalid annual_inputs")

    years = []

    for year, params in annual.items():
        if not isinstance(year, str):
            raise ValueError("Invalid year key")

        if (
            len(year) != 4
            or not year.isascii()
            or not year.isdecimal()
        ):
            raise ValueError(f"Invalid year: {year}")

        years.append(int(year))

        if not isinstance(params, dict):
            raise ValueError(f"Invalid parameters: {year}")

        if set(params) != REQUIRED_PARAMS:
            raise ValueError(f"Invalid parameter keys: {year}")

        for key, value in params.items():
            if type(value) not in (int, float):
                raise ValueError(f"Non-numeric: {year}/{key}")

            if not math.isfinite(value):
                raise ValueError(f"Non-finite: {year}/{key}")

    for year, params in annual.items():
        if params["expenditure_growth"] < -1:
            raise ValueError(
                f"Invalid expenditure growth: {year}"
            )

    years.sort()

    if years != list(range(2027, years[-1] + 1)):
        raise ValueError("Invalid year sequence")

    return annual
