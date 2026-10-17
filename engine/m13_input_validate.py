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

    required_fields = {"profile", "annual_inputs"}
    allowed_fields = required_fields | {"wage_anchors", "gini_anchors"}

    if not required_fields <= set(data):
        raise ValueError("Missing scenario fields")

    if not set(data) <= allowed_fields:
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

    if "wage_anchors" in data:
        from m14_wage_anchor import validate_anchors

        raw = data["wage_anchors"]

        if not isinstance(raw, dict):
            raise ValueError("Invalid wage_anchors")

        anchors = {}

        for year, wage in raw.items():
            if (
                not isinstance(year, str)
                or len(year) != 4
                or not year.isascii()
                or not year.isdecimal()
            ):
                raise ValueError("Invalid wage anchor year")

            anchors[int(year)] = wage

        anchor_years = validate_anchors(anchors)

        if anchor_years[0] != 2026:
            raise ValueError("Wage anchors must start in 2026")

        if anchor_years[-1] != years[-1]:
            raise ValueError("Wage anchors must end at scenario end")

    if "gini_anchors" in data:
        from m17_gini_anchor import validate_gini_anchors

        raw = data["gini_anchors"]

        if not isinstance(raw, dict):
            raise ValueError("Invalid gini_anchors")

        anchors = {}

        for year, gini in raw.items():
            if (
                not isinstance(year, str)
                or len(year) != 4
                or not year.isascii()
                or not year.isdecimal()
            ):
                raise ValueError("Invalid Gini anchor year")

            anchors[int(year)] = gini

        anchor_years = validate_gini_anchors(anchors)

        if anchor_years[0] != 2026:
            raise ValueError("Gini anchors must start in 2026")

        if anchor_years[-1] != years[-1]:
            raise ValueError("Gini anchors must end at scenario end")

    return annual
