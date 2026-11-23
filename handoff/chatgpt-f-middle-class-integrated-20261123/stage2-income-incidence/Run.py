"""Compare annual cash incidence using fixed reference-income groups."""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("benefits", ROOT / "stage1-benefits-burdens/Run.py")
benefits = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benefits)
prior = benefits.prior


def groups(rows):
    yield "ALL", rows
    for q in range(5):
        yield f"Q{q+1}", [r for r in rows if r["quintile"] == q]
    for p in sorted({r["profile"] for r in rows}):
        yield p, [r for r in rows if r["profile"] == p]
    for q in range(1,4):
        for p in sorted({r["profile"] for r in rows}):
            yield f"Q{q+1}_{p}", [r for r in rows if r["quintile"] == q and r["profile"] == p]


def equal_profile(rows):
    nodes = {}
    for r in rows:
        nodes.setdefault(r["id"].split("_",1)[0], []).append(r)
    return [dict(r, households=sum(z["households"] for z in node)/len(node))
            for node in nodes.values() for r in node]


def calculate(data, out):
    check = prior.Checks()
    annual, distribution = [], []
    for year, case, rows, scale, macro in data:
        variants = [("FIXED",rows)]
        if case in ("FIXED_F","INTEGRATED","INTEGRATED_GROSS"):
            variants.append(("EQUAL_PROFILE_RETABULATION",equal_profile(rows)))
        for weights, tab in variants:
            check("household_count", sum(r["households"] for r in tab), sum(r["households"] for r in rows))
            rank, med = prior.median(tab,"cash")
            gini = prior.gini(tab,"cash")
            check("gini_range", 0 <= gini <= 1, True)
            annual.append(dict(year=year,case=case,weights=weights,cash_median_nominal_yen=med["cash"],
                               cash_median_real_2026_yen=med["cash"]/scale,median_cell=med["id"],median_rank=rank,
                               median_A_yen=med["A_yen"],median_C_yen=med["C_cash_yen"],
                               median_income_tax=med["income_tax"]+med["A_income_tax"],
                               median_resident_tax=med["resident_tax"]+med["A_resident_tax"],
                               median_pension=med["pension"],synthetic_cash_gini=gini))
            group_count = 0.
            for name, subset in groups(tab):
                weight = sum(r["households"] for r in subset)
                check("positive_group_weight", weight > 0, True)
                if name in ("Q1","Q2","Q3","Q4","Q5"):
                    group_count += weight
                distribution.append(dict(year=year,case=case,weights=weights,group=name,households=weight,
                                         cash_real_2026_yen=benefits.total(subset,"cash")/weight/scale,
                                         delta_cash_real_2026_yen=benefits.total(subset,"delta_cash")/weight/scale,
                                         **{k:benefits.total(subset,k)/weight for k in (
                                            "wage","pension","income_tax","resident_tax","A_income_tax","A_resident_tax",
                                            "premium_paid","A_yen","C_cash_yen","net_benefit","cash")}))
            check("quintile_partition", group_count, sum(r["households"] for r in tab))
    benefits.write(out,"Annual.csv",annual)
    benefits.write(out,"Groups.csv",distribution)
    check.save(out)


if __name__ == "__main__":
    runtime,replay,out = map(Path,sys.argv[1:])
    calculate(benefits.calculate(runtime,replay,out.parent/"stage1-benefits-burdens"),out)
