import json
import subprocess
import sys

RUNNER = "engine/m10_results.py"
SCENARIOS = {
    "baseline": "scenarios/m8_baseline.json",
    "test": "scenarios/m8_test.json",
}

def run(path):
    raw = subprocess.check_output(
        [sys.executable, RUNNER, path],
        text=True
    )
    data = json.loads(raw)
    assert data["schema_version"] == "m10.1"
    return data["years"]

results = {
    name: run(path)
    for name, path in SCENARIOS.items()
}

baseline = results["baseline"]
test = results["test"]

assert baseline.keys() == test.keys()

print("=== M10 STRUCTURED COMPARISON ===")

for year in sorted(baseline):
    assert baseline[year].keys() == test[year].keys()
    print(f"\nYear: {year}")

    for key in baseline[year]:
        if key == "year":
            continue
        delta = test[year][key] - baseline[year][key]
        print(f"  {key:<16} {delta:+.10f}")

print("\nM10 STRUCTURED COMPARISON: PASS")

# M10 full-precision regression checks
assert sorted(baseline) == [
    "2026", "2027", "2028", "2029"
]

for year in sorted(baseline):
    a = baseline[year]
    b = test[year]

    for key in a:
        delta = b[key] - a[key]

        if year != "2029":
            assert abs(delta) < 1e-10, (year, key)

        elif key in ("expenditure", "bonds"):
            assert abs(delta + 1.7020125) < 1e-9, (
                year, key, delta
            )

        else:
            assert abs(delta) < 1e-10, (year, key)

assert abs(
    test["2029"]["expenditure"]
    - baseline["2029"]["expenditure"]
    - (
        test["2029"]["bonds"]
        - baseline["2029"]["bonds"]
    )
) < 1e-10

print("M10 FULL PRECISION REGRESSION: PASS")
