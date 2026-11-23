"""Calculate synthetic distribution metrics without changing the F model."""
import math
import sys
from pathlib import Path
from Common import Checks, fixed_f, render
from Replay import load

def median(values):
    target = sum(w for _, w in values)/2
    cumulative = 0.
    for value, weight in sorted(values):
        cumulative += weight
        if cumulative >= target:
            return value
    raise ValueError("No weighted median")

def gini(values):
    population = sum(w for _, w in values)
    mass = sum(x*w for x, w in values)
    cumulative = 0.
    numerator = 0.
    for x, w in sorted(values):
        numerator += x*w*(2*cumulative+w-population)
        cumulative += w
    return numerator/(population*mass)

def calculate(run, fixed, check):
    annual, comparison, distribution = [], [], []
    cells = load(run/"Household_Cells.json")
    for year, row in zip(range(2026, 2056), load(run/"F_Actual_Annual.json"), strict=True):
        check("year", row["year"], year)
        for key in ("real_gdp_trn", "nominal_gdp_trn", "tax_diagnostic_trn", "capital_total_real_trn"):
            check("fixed_F", row[key], float(fixed[year][key]))
        check("no_gini_trigger", (row["gini_external_2035"], row["gini_triggered"]), (None, 0))
        grid = cells[str(year)]
        weights = {r["id"]: r["households"] for r in grid}
        check("distinct_cells", len(weights), len(grid))
        household_count = sum(weights.values())
        for r in grid:
            check("positive_weights", r["households"] > 0 and r["size"] > 0, True)
            check("baseline_cash", r["baseline_DI_yen"], max(0., r["gross_income_yen"]-r["baseline_tax_yen"]
                                                            -r["baseline_local_tax_yen"]-r["premium_before_yen"]))
            check("cash_policy", r["cash_DI_after_yen"], r["baseline_DI_yen"]+r["A_yen"]+r["fund_yen"]
                  +r["C_cash_yen"]-r["tax_increase_yen"]-r["local_tax_increase_yen"])
            check("premium", r["premium_after_yen"], r["premium_before_yen"]-r["A_yen"]-r["fund_yen"])
            check("in_kind_separate", r["resources_after_yen"], r["cash_DI_after_yen"]+r["B_used_yen"])
        for group in sorted({r["group"] for r in grid}):
            members = [r for r in grid if r["group"] == group]
            population = sum(r["households"] for r in members)
            keys = ("gross_income_yen","baseline_tax_yen","baseline_local_tax_yen",
                    "premium_before_yen","premium_after_yen","A_yen","fund_yen","tax_increase_yen",
                    "local_tax_increase_yen","C_cash_yen","B_used_yen","baseline_DI_yen","cash_DI_after_yen",
                    "resources_after_yen")
            distribution.append(dict(year=year, income_group=group, households=population,
                people_weight=sum(r["households"]*r["size"] for r in members),
                **{k+"_per_HH":sum(r[k]*r["households"] for r in members)/population for k in keys}))
        def total(key):
            return sum(r[key]*r["households"] for r in grid)/1e12
        for key, macro in (("A_yen","A_relief_trn"),("C_cash_yen","C_cash_trn"),
                           ("B_used_yen","B_used_trn"),("cash_DI_delta_yen","cash_DI_delta_trn")):
            check("A_B_C_reconciliation", total(key), row[macro])
        def household_values(key):
            return [(r[key], r["households"]) for r in grid]
        def person_values(key):
            return [(max(0., r[key])/math.sqrt(r["size"]), r["households"]*r["size"]) for r in grid]
        before, after, resources = (gini(person_values(k)) for k in
                                     ("baseline_DI_yen","cash_DI_after_yen","resources_after_yen"))
        for value, key in ((before,"synthetic_equivalized_gini_before"),
                           (after,"synthetic_equivalized_gini_after"),(resources,"synthetic_resources_gini_after")):
            check("gini_range", 0 <= value <= 1, True)
            check("same_distribution_gini", value, row[key])
        medians = {}
        for label,key in (("gross","gross_income_yen"),("baseline_cash","baseline_DI_yen"),
                          ("cash","cash_DI_after_yen"),("resources","resources_after_yen")):
            v = household_values(key)
            med = median(v)
            check("median_lower_weight", sum(w for x,w in v if x<med) <= household_count/2, True)
            check("median_upper_weight", sum(w for x,w in v if x>med) <= household_count/2, True)
            medians[label+"_median_nominal_yen"] = med
            medians[label+"_median_real_2026_yen"] = med / (row["common_deflator"]/(600/580))
        if year==2026:
            check("zero_benefit_gini", after, before)
            check("zero_benefit_median", medians["cash_median_nominal_yen"], medians["baseline_cash_median_nominal_yen"])
        annual.append(dict(year=year, synthetic_households=household_count, synthetic_person_weight=sum(
            r["households"]*r["size"] for r in grid), **medians, synthetic_gini_before=before,
            synthetic_gini_cash=after, synthetic_gini_resources=resources,
            nominal_wage_proxy_man=row["nominal_wage_proxy_man"], real_wage_proxy_man=row["real_wage_proxy_man"],
            national_gini="N/A", national_income_median="N/A", national_nominal_wage_median="N/A",
            national_real_wage_median="N/A", synthetic_wage_median="N/A", gini_triggered=row["gini_triggered"]))
        comparison.append(dict(year=year, synthetic_gini_cash_minus_before=after-before,
                               synthetic_gini_resources_minus_before=resources-before,
                               synthetic_cash_median_nominal_delta_yen=medians["cash_median_nominal_yen"]-
                               medians["baseline_cash_median_nominal_yen"],
                               synthetic_cash_median_real_delta_yen=medians["cash_median_real_2026_yen"]-
                               medians["baseline_cash_median_real_2026_yen"]))
    return tuple(map(render,(annual,comparison,distribution)))

if __name__=="__main__":
    run, replay, reference, output = map(Path,sys.argv[1:])
    deps = load(Path(__file__).with_name("Dependencies.json"))
    fixed = fixed_f(reference, next(d for d in deps if d["local"]=="retrieved/Legacy_Annual.csv"))
    check = Checks()
    for name in ("F_Actual_Annual.json","Household_Cells.json"):
        check("runtime_bytes", (run/name).read_bytes(), (replay/name).read_bytes())
    a,b = calculate(run,fixed,check),calculate(replay,fixed,check)
    for name,left,right in zip(("Annual.csv","Comparison.csv","Distribution.csv"),a,b,strict=True):
        check("CSV_bytes",left,right)
        (output/name).write_bytes(left)
    check.save(output)
