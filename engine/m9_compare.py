import re
import subprocess
import sys

RUNNER = "engine/m8_scenario_runner.py"
SCENARIOS = {
    "baseline": "scenarios/m8_baseline.json",
    "test": "scenarios/m8_test.json",
}

def run(path):
    result = subprocess.run(
        [sys.executable, RUNNER, path],
        capture_output=True, text=True, check=True
    )
    rows = {}
    for line in result.stdout.splitlines():
        if not re.match(r"^20\d\d \|", line):
            continue
        parts = line.split(" | ")
        year = int(parts[0])
        rows[year] = {
            item.split(": ")[0]: float(
                item.split(": ")[1].replace(",", "")
            )
            for item in parts[1:]
        }
    return rows

results = {name: run(path) for name, path in SCENARIOS.items()}

assert results["baseline"].keys() == results["test"].keys()
print("M9 SCENARIO LOADING: PASS")
print("Years:", sorted(results["baseline"]))

year = 2029
baseline = results["baseline"][year]
test = results["test"][year]

assert baseline.keys() == test.keys()

print(f"\n=== M9 SCENARIO COMPARISON: {year} ===")
print(f"{'Indicator':<16} {'Baseline':>14} {'Test':>14} {'Delta':>14}")

for indicator in baseline:
    a = baseline[indicator]
    b = test[indicator]
    delta = b - a
    print(f"{indicator:<16} {a:>14.4f} {b:>14.4f} {delta:>+14.4f}")

assert abs((test["Expenditure"] - baseline["Expenditure"]) + 1.7020) < 0.0002
assert abs((test["Bonds"] - baseline["Bonds"]) + 1.7020) < 0.0002
assert test["Real GDP"] == baseline["Real GDP"]
assert test["Revenue"] == baseline["Revenue"]

print("M9 DELTA COMPARISON: PASS")

print("\n=== M9 ANNUAL DELTA TABLE ===")
print(f"{'Year':<6} {'Real GDP':>12} {'Revenue':>12} {'Expenditure':>14} {'Bonds':>12}")

for year in sorted(results["baseline"]):
    a = results["baseline"][year]
    b = results["test"][year]
    assert a.keys() == b.keys()
    print(
        f"{year:<6} "
        f"{b['Real GDP'] - a['Real GDP']:>+12.4f} "
        f"{b['Revenue'] - a['Revenue']:>+12.4f} "
        f"{b['Expenditure'] - a['Expenditure']:>+14.4f} "
        f"{b['Bonds'] - a['Bonds']:>+12.4f}"
    )

print("M9 ANNUAL COMPARISON: PASS")

# M9 regression checks
expected_years = [2026, 2027, 2028, 2029]
assert sorted(results["baseline"]) == expected_years

for year in expected_years:
    a = results["baseline"][year]
    b = results["test"][year]

    assert a.keys() == b.keys()

    for indicator in a:
        delta = b[indicator] - a[indicator]

        if year < 2029:
            assert abs(delta) < 0.0001, (year, indicator)

        elif indicator in ("Expenditure", "Bonds"):
            assert abs(delta + 1.7020) < 0.0002

        else:
            assert abs(delta) < 0.0001, indicator

print("M9 REGRESSION CHECK: PASS")
