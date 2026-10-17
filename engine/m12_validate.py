import json
from pathlib import Path

REGISTRY = Path("scenarios/m11_registry.json")

def validate_registry(data):
    if not isinstance(data, dict):
        raise ValueError("Registry must be an object")

    required = (
        "schema_version", "profile",
        "baseline", "scenarios"
    )
    for key in required:
        if key not in data:
            raise ValueError(f"Missing field: {key}")

    if data["schema_version"] != "m11.1":
        raise ValueError("Unsupported schema version")

    if not isinstance(data["profile"], str):
        raise ValueError("Invalid profile")

    scenarios = data["scenarios"]
    if not isinstance(scenarios, dict):
        raise ValueError("Scenarios must be an object")

    if len(scenarios) < 2:
        raise ValueError("At least two scenarios required")

    if data["baseline"] not in scenarios:
        raise ValueError("Baseline not registered")

    if not data["profile"].strip():
        raise ValueError("Empty profile")

    if not isinstance(data["baseline"], str):
        raise ValueError("Invalid baseline")

    if not data["baseline"].strip():
        raise ValueError("Empty baseline")

    seen = set()
    for name, path in scenarios.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Invalid scenario ID")
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Invalid scenario path")

        target = Path(path).resolve()
        if not target.is_file():
            raise ValueError(f"Missing scenario: {name}")
        if target in seen:
            raise ValueError(f"Duplicate scenario path: {name}")
        seen.add(target)

    return scenarios

if __name__ == "__main__":
    data = json.loads(REGISTRY.read_text())
    scenarios = validate_registry(data)

    print("=== M12 REGISTRY VALIDATION ===")
    print("Registered scenarios:", len(scenarios))
    print("Baseline:", data["baseline"])
    print("M12 REGISTRY STRUCTURE: PASS")

def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_registry_strict(path):
    with Path(path).open(encoding="utf-8") as f:
        data = json.load(
            f,
            object_pairs_hook=reject_duplicate_keys
        )
    validate_registry(data)
    return data


def validate_result(data):
    import math

    if not isinstance(data, dict):
        raise ValueError("Result must be an object")

    if data.get("schema_version") != "m10.1":
        raise ValueError("Unsupported result schema")

    years = data.get("years")
    if not isinstance(years, dict) or not years:
        raise ValueError("Invalid years")

    required = {
        "year", "real_gdp", "nominal_gdp",
        "tax_revenue", "expenditure", "population",
        "deaths", "births", "bonds"
    }

    for year, state in years.items():
        if not isinstance(year, str) or (
            len(year) != 4 or not year.isascii()
            or not year.isdecimal()
        ):
            raise ValueError(f"Invalid year key: {year}")

        if not isinstance(state, dict):
            raise ValueError(f"Invalid state: {year}")

        if set(state) != required:
            raise ValueError(f"Invalid indicators: {year}")

        if type(state["year"]) is not int:
            raise ValueError(f"Invalid year value: {year}")

        if state["year"] != int(year):
            raise ValueError(f"Year mismatch: {year}")

        for key in required - {"year"}:
            value = state[key]
            if type(value) not in (int, float):
                raise ValueError(f"Non-numeric: {year}/{key}")
            if not math.isfinite(value):
                raise ValueError(f"Non-finite: {year}/{key}")

    ordered = sorted(int(y) for y in years)
    expected = list(range(ordered[0], ordered[-1] + 1))
    if ordered != expected:
        raise ValueError("Non-contiguous years")

    nonnegative = (
        "real_gdp", "nominal_gdp", "tax_revenue",
        "expenditure", "population", "deaths",
        "births", "bonds"
    )

    for year, state in years.items():
        for key in nonnegative:
            if state[key] < 0:
                raise ValueError(f"Negative value: {year}/{key}")

        expected_bonds = max(
            state["expenditure"] - state["tax_revenue"],
            0.0
        )
        if not math.isclose(
            state["bonds"], expected_bonds,
            rel_tol=1e-10, abs_tol=1e-9
        ):
            raise ValueError(f"Bond mismatch: {year}")

    return years
