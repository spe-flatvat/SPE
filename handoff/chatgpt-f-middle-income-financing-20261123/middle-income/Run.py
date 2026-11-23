"""Allocate the existing fixed VAT wage pool to synthetic employee households."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HANDOFF = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HANDOFF/"chatgpt-f-distribution-fiscal-integration-20261123/stage1-distribution"))
from Common import Checks, csv_rows, render
from Replay import load

EMPLOYEE = {"EMP_SINGLE", "EMP_CHILD"}
CASES = {"FIXED_F": 0., "ZERO_ON": 0., "VAT_WAGE_ALLOCATION": 1.}
FIELDS = ("A_yen", "fund_yen", "C_cash_yen", "B_used_yen", "premium_after_yen",
          "baseline_tax_yen", "baseline_local_tax_yen", "tax_increase_yen", "local_tax_increase_yen")


def median(grid, key):
    ordered = sorted(grid, key=lambda r: (r[key], r["id"]))
    half = sum(r["households"] for r in ordered)/2
    cumulative = 0.
    for rank, r in enumerate(ordered, 1):
        cumulative += r["households"]
        if cumulative >= half:
            return rank, r


def gini(grid, key):
    values = sorted((max(0., r[key])/r["size"]**.5, r["size"]*r["households"]) for r in grid)
    population = sum(w for _, w in values)
    cumulative = numerator = 0.
    for value, weight in values:
        numerator += value*weight*(2*cumulative+weight-population)
        cumulative += weight
    return numerator/(population*sum(value*weight for value, weight in values))


def calculate(run, check):
    prior = csv_rows((HANDOFF/"chatgpt-f-median-fiscal-residual-20261123/median-attribution/Annual.csv").read_bytes())
    grid_by_year = load(run/"Household_Cells.json")
    annual, groups = [], []
    for year, macro, old in zip(range(2026,2056), load(run/"F_Actual_Annual.json"), prior, strict=True):
        check("year", (macro["year"], int(old["year"])), (year, year))
        check("no_gini_trigger", (macro["gini_triggered"], macro["gini_external_2035"]), (0, None))
        grid = grid_by_year[str(year)]
        scale = macro["common_deflator"]/(600/580)
        wages = macro["household_wage_allocation_trn"] if year > 2026 else 0.
        wage_base = sum(r["gross_income_yen"]*r["households"] for r in grid if r["profile"] in EMPLOYEE)
        check("wage_base_exists", wage_base > 0, True)
        for r in grid:
            check("A_range", r["A_yen"] == 0 or r["gross_income_yen"] <= 5e6, True)
            check("B_range", r["B_used_yen"] == 0 or r["gross_income_yen"] <= 3e6, True)
            check("C_range", r["C_cash_yen"] == 0 or r["gross_income_yen"] <= 5e6, True)
        base_result = None
        for name, share in CASES.items():
            rows = []
            for r in grid:
                inc = wages*1e12*share*r["gross_income_yen"]/wage_base if r["profile"] in EMPLOYEE else 0.
                rows.append(dict(r, wage_yen=inc, pre=r["baseline_DI_yen"]+inc,
                                 post=r["cash_DI_after_yen"]+inc, resources=r["resources_after_yen"]+inc))
            allocated = sum(r["wage_yen"]*r["households"] for r in rows)/1e12
            check("pool_allocation", allocated, wages*share)
            check("macro_pool_conserved", allocated+wages*(1-share), wages)
            for policy, key in (("A_yen","A_relief_trn"), ("C_cash_yen","C_cash_trn"), ("B_used_yen","B_used_trn")):
                check("no_policy_readdition", sum(r[policy]*r["households"] for r in rows)/1e12, macro[key])
            _, pre = median(rows, "pre")
            rank, post = median(rows, "post")
            before_gini, after_gini, resources_gini = (gini(rows,k) for k in ("pre","post","resources"))
            result = dict(baseline_cash_median_nominal_yen=pre["pre"], cash_median_nominal_yen=post["post"],
                          baseline_cash_median_real_2026_yen=pre["pre"]/scale, cash_median_real_2026_yen=post["post"]/scale,
                          synthetic_gini_before=before_gini, synthetic_gini_cash=after_gini,
                          synthetic_gini_resources=resources_gini, post_median_cell=post["id"], post_median_rank=rank)
            if name == "FIXED_F":
                base_result = result
                for key, value in result.items():
                    if key in old:
                        check("prior_median_and_gini", value, float(old[key]) if isinstance(value,float) else old[key])
            if name == "ZERO_ON":
                check("zero_on", result, base_result)
            annual.append(dict(year=year, case=name, **result,
                               median_gross_nominal_yen=post["gross_income_yen"]+post["wage_yen"],
                               median_cell_households=post["households"],
                               median_cell_person_shares="|".join(map(str,post["shares"])),
                               median_cell_fixed_gross_yen=post["gross_income_yen"],
                               median_A_household_threshold=post["gross_income_yen"]<=5e6,
                               median_B_household_threshold=post["gross_income_yen"]<=3e6,
                               median_C_household_threshold=post["gross_income_yen"]<=5e6,
                               median_cell_vat_price_effect_yen=post["VAT_price_effect_yen"],
                               **{f"median_{k}":post[k] for k in FIELDS},
                               wage_pool_trn=wages, assigned_wage_trn=allocated, unassigned_wage_trn=wages*(1-share),
                               public_cost_delta_trn=0, tax_premium_reassessment="N/A_FIXED_LIABILITIES",
                               real_GDP_effect="N/A_NO_MACRO_FEEDBACK",
                               delta_real_median_yen=result["cash_median_real_2026_yen"]-base_result["cash_median_real_2026_yen"],
                               delta_cash_gini=after_gini-base_result["synthetic_gini_cash"]))
            group_sum = 0.
            for group in sorted({r["reference_income_group"] for r in rows}):
                subset = [r for r in rows if r["reference_income_group"]==group]
                weight = sum(r["households"] for r in subset)
                means = {key:sum(r[key]*r["households"] for r in subset)/weight for key in (*FIELDS,"pre","post","wage_yen")}
                group_sum += means["wage_yen"]*weight/1e12
                if name=="VAT_WAGE_ALLOCATION":
                    display = {key:round(value,6) for key,value in means.items()}
                    groups.append(dict(year=year,case=name,reference_income_group=group,households=round(weight,6),
                                       **display, fixed_post_yen=round(means["post"]-means["wage_yen"],6),
                                       post_real_yen=round(means["post"]/scale,6),
                                       wage_delta_real_yen=round(means["wage_yen"]/scale,6)))
            check("group_wage_reconciliation", group_sum, allocated)
    return render(annual), render(groups)


if __name__ == "__main__":
    run, output = map(Path,sys.argv[1:])
    checks = Checks()
    for name, data in zip(("Annual.csv","Comparison.csv"),calculate(run,checks),strict=True):
        (output/name).write_bytes(data)
    checks.save(output)
