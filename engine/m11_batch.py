import json
from pathlib import Path

REGISTRY = Path("scenarios/m11_registry.json")

with REGISTRY.open(encoding="utf-8") as f:
    registry = json.load(f)

assert registry["schema_version"] == "m11.1"

scenarios = registry["scenarios"]
baseline = registry["baseline"]

assert isinstance(scenarios, dict)
assert len(scenarios) >= 2
assert baseline in scenarios

for name, path in scenarios.items():
    assert isinstance(name, str) and name
    assert isinstance(path, str) and path
    assert Path(path).is_file(), (name, path)

print("=== M11 SCENARIO REGISTRY ===")
print("Profile:", registry["profile"])
print("Baseline:", baseline)

for name, path in scenarios.items():
    print(f"{name}: {path}")

print("M11 REGISTRY VALIDATION: PASS")

import subprocess
import sys

RUNNER = "engine/m10_results.py"
results = {}

for name, path in scenarios.items():
    raw = subprocess.check_output(
        [sys.executable, RUNNER, path],
        text=True
    )
    data = json.loads(raw)

    assert data["schema_version"] == "m10.1"
    assert isinstance(data["years"], dict)
    assert data["years"], name

    results[name] = data["years"]
    print(f"Executed: {name} ({len(data['years'])} years)")

assert results.keys() == scenarios.keys()

print("M11 BATCH EXECUTION: PASS")

reference = results[baseline]

print("\n=== M11 BATCH COMPARISON ===")

for name, years in results.items():
    if name == baseline:
        continue

    assert years.keys() == reference.keys(), name
    print(f"\nScenario: {name} vs {baseline}")

    for year in sorted(reference):
        a = reference[year]
        b = years[year]
        assert a.keys() == b.keys(), (name, year)

        print(f"Year: {year}")
        for key in a:
            if key == "year":
                continue
            delta = b[key] - a[key]
            print(f"  {key:<16} {delta:+.10f}")

print("\nM11 BATCH COMPARISON: PASS")

# M11 regression checks
assert len(results) >= 3
assert results.keys() == scenarios.keys()
assert results["test"] == results["test_copy"]

a = results["baseline"]
b = results["test"]

assert sorted(a) == ["2026", "2027", "2028", "2029"]

for year in sorted(a):
    assert a[year].keys() == b[year].keys()

    for key in a[year]:
        delta = b[year][key] - a[year][key]

        expected = (
            -1.7020125
            if year == "2029"
            and key in ("expenditure", "bonds")
            else 0.0
        )
        assert abs(delta - expected) < 1e-9, (
            year, key, delta
        )

print("M11 BATCH REGRESSION: PASS")
