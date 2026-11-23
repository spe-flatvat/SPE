"""Replay-based weighted median attribution in 2026 yen."""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parents[1] / "chatgpt-f-distribution-fiscal-integration-20261123" / "stage1-distribution"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PREVIOUS))
from Common import Checks, csv_rows, fixed_f, render
from Replay import load

TERMS = {
    "gross": ("gross_income_yen", 1),
    "baseline_income_tax": ("baseline_tax_yen", -1),
    "baseline_local_tax": ("baseline_local_tax_yen", -1),
    "baseline_premium": ("premium_before_yen", -1),
    "A_relief": ("A_yen", 1),
    "fund": ("fund_yen", 1),
    "C_cash": ("C_cash_yen", 1),
    "incremental_income_tax": ("tax_increase_yen", -1),
    "incremental_local_tax": ("local_tax_increase_yen", -1),
}


def parts(row):
    result = {label: sign * row[key] for label, (key, sign) in TERMS.items()}
    raw = sum(list(result.values())[:4])
    result["cash_floor"] = max(0, -raw)
    return result


def order(grid, key):
    return sorted(grid, key=lambda row: (row[key], row["id"]))


def median(ordered, weights):
    target = sum(weights.values()) / 2
    cumulative = 0
    for row in ordered:
        cumulative += weights[row["id"]]
        if cumulative >= target:
            return row


def gini(grid, key):
    values = sorted((max(0., r[key])/math.sqrt(r["size"]), r["households"]*r["size"]) for r in grid)
    population = sum(w for _, w in values)
    cumulative = numerator = 0.
    for value, weight in values:
        numerator += value * weight * (2*cumulative + weight - population)
        cumulative += weight
    return numerator / (population * sum(value * weight for value, weight in values))


def calculate(run, fixed, check):
    annual = []
    cells = []
    data = load(run / "Household_Cells.json")
    macro = load(run / "F_Actual_Annual.json")
    baseline = {r["id"]: r for r in data["2026"]}
    baseline_order = order(baseline.values(), "cash_DI_after_yen")
    initial_weights = {i: row["households"] for i, row in baseline.items()}
    original = median(baseline_order, initial_weights)["cash_DI_after_yen"]
    deflator_base = macro[0]["common_deflator"]
    check("2026_deflator", deflator_base, 600/580)
    old = csv_rows((PREVIOUS / "Annual.csv").read_bytes())
    for year, row, prior in zip(range(2026,2056), macro, old, strict=True):
        check("year", (row["year"], int(prior["year"])), (year, year))
        for key in ("real_gdp_trn", "nominal_gdp_trn", "tax_diagnostic_trn"):
            check("fixed_F", row[key], float(fixed[year][key]))
        grid = data[str(year)]
        active = {r["id"]: r for r in grid}
        weights = {i: r["households"] for i, r in active.items()}
        check("same_cell_universe", (len(grid), set(active)), (len(baseline), set(baseline)))
        check("income_band_count", len({i.split("_",1)[0] for i in active}), 29)
        check("household_weight", sum(weights.values()), float(prior["synthetic_households"]))
        check("person_weight", sum(r["households"]*r["size"] for r in grid), float(prior["synthetic_person_weight"]))
        check("national_trigger", (row["gini_external_2035"], row["gini_triggered"]), (None, 0))
        scale = row["common_deflator"] / deflator_base
        pre = order(grid, "baseline_DI_yen")
        post = order(grid, "cash_DI_after_yen")
        before = median(pre, weights)
        after = median(post, weights)
        anchor = median(baseline_order, weights)
        current = active[anchor["id"]]
        before_cash = before["baseline_DI_yen"]
        after_cash = after["cash_DI_after_yen"]
        initial_parts = parts(anchor)
        current_parts = parts(current)
        contribution = {key + "_real_yen": (current_parts[key]-value)/scale for key, value in initial_parts.items()}
        contribution.update(composition_real_yen=(anchor["cash_DI_after_yen"]-original)/scale,
                            reranking_real_yen=(after_cash-current["cash_DI_after_yen"])/scale,
                            deflator_real_yen=original*(1/scale-1))
        residual = after_cash/scale-original-sum(contribution.values())
        check("median_bridge", residual, 0.)
        metrics = dict(baseline_cash_median_nominal_yen=before_cash, cash_median_nominal_yen=after_cash,
                       baseline_cash_median_real_2026_yen=before_cash/scale,
                       cash_median_real_2026_yen=after_cash/scale,
                       synthetic_gini_before=gini(grid, "baseline_DI_yen"),
                       synthetic_gini_cash=gini(grid, "cash_DI_after_yen"),
                       synthetic_gini_resources=gini(grid, "resources_after_yen"))
        for key, value in metrics.items():
            check("fixed_stage1", value, float(prior[key]))
        household_index = current["idx"] / anchor["idx"]
        check("indexed_baseline_cell", current["baseline_DI_yen"],
              anchor["baseline_DI_yen"]*household_index)
        below_improved = sum(r["households"] for r in grid
                             if r["baseline_DI_yen"] < before_cash and r["cash_DI_delta_yen"] > 0)
        all_improved = sum(r["households"] for r in grid if r["cash_DI_delta_yen"] > 0)
        annual.append(dict(year=year, deflator_2026=scale, household_income_index_2026=household_index,
                           improved_below_baseline_median_share=below_improved/sum(weights.values()),
                           improved_all_share=all_improved/sum(weights.values()), **metrics,
                           composition_anchor=anchor["id"], pre_median_cell=before["id"],
                           post_median_cell=after["id"], pre_median_cell_cash_delta_yen=before["cash_DI_delta_yen"],
                           post_median_cell_cash_delta_yen=after["cash_DI_delta_yen"],
                           median_cash_policy_real_yen=(after_cash-before_cash)/scale,
                           **contribution, closure_residual_yen=residual))
        pre_ranks = {r["id"]: n for n, r in enumerate(pre, 1)}
        post_median_rank = next(n for n, r in enumerate(post, 1) if r is after)
        pre_median_rank = pre_ranks[before["id"]]
        pre_cumulative = {}
        total = sum(weights.values())
        cumulative = 0.
        for r in pre:
            cumulative += r["households"]
            pre_cumulative[r["id"]] = cumulative / total
        cumulative = 0.
        for rank, r in enumerate(post, 1):
            i = r["id"]
            values = parts(r)
            check("positive_weight_and_size", r["households"] > 0 and r["size"] > 0, True)
            check("cash_components", sum(values.values()), r["cash_DI_after_yen"])
            check("cash_delta", r["cash_DI_after_yen"]-r["baseline_DI_yen"], r["cash_DI_delta_yen"])
            check("premium_relief_once", r["premium_after_yen"], r["premium_before_yen"]-r["A_yen"]-r["fund_yen"])
            check("in_kind_outside_cash", r["resources_after_yen"], r["cash_DI_after_yen"]+r["B_used_yen"])
            cumulative += r["households"]
            if abs(rank-post_median_rank) > 2 and abs(pre_ranks[i]-pre_median_rank) > 2 and i != anchor["id"]:
                continue
            cells.append(dict(year=year, cell=i, profile=r["profile"], income_group=r["group"], quintile=r["quintile"],
                              size=r["size"], households=r["households"], household_share=r["households"]/total,
                              before_rank=pre_ranks[i], after_rank=rank, before_cumulative_share=pre_cumulative[i],
                              after_cumulative_share=cumulative/total, before_nominal_yen=r["baseline_DI_yen"],
                              after_nominal_yen=r["cash_DI_after_yen"], after_real_yen=r["cash_DI_after_yen"]/scale,
                              in_kind_yen=r["B_used_yen"], **{k+"_nominal_yen": v for k,v in values.items()}))
        for label, key in (("A_yen", "A_relief_trn"), ("C_cash_yen", "C_cash_trn"), ("B_used_yen", "B_used_trn")):
            check("policy_aggregation", sum(r[label]*r["households"] for r in grid)/1e12, row[key])
    return render(annual), render(cells)


if __name__ == "__main__":
    source, reference, output = map(Path, sys.argv[1:])
    dependencies = load(PREVIOUS / "Dependencies.json")
    fixed = fixed_f(reference, next(d for d in dependencies if d["local"] == "retrieved/Legacy_Annual.csv"))
    check = Checks()
    for name, data in zip(("Annual.csv", "Cell_Detail.csv"), calculate(source, fixed, check), strict=True):
        (output / name).write_bytes(data)
    check.save(output)
