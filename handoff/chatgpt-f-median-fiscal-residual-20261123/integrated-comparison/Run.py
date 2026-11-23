"""Join fixed F macro diagnostics with the verified median and financing attribution."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parents[1] / "chatgpt-f-distribution-fiscal-integration-20261123"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PREVIOUS / "stage1-distribution"))
from Common import Checks, csv_rows, fixed_f, render
from Replay import load

MACRO = ("real_gdp_trn", "nominal_gdp_trn", "population", "tax_diagnostic_trn",
         "consolidated_partial_balance_proxy_trn")

LIMITS = ("national_gini", "national_income_median", "national_nominal_wage_median",
          "national_real_wage_median", "national_general_government_PB", "national_bond_issue",
          "national_debt", "national_refinancing_issue", "national_funding_rate")


def calculate(run, fixed, attribution, finance, check):
    baseline = csv_rows((PREVIOUS / "stage3-integrated/Annual.csv").read_bytes())
    annual = []
    for year, old, r, a, b in zip(range(2026,2056), baseline, load(run/"F_Actual_Annual.json"),
                                  attribution, finance, strict=True):
        check("year_join", (int(old["year"]), r["year"], int(a["year"]), int(b["year"])), (year,)*4)
        differences = {}
        for key in MACRO:
            difference = float(r[key])-float(old[key])
            check("fixed_stage3_macro", difference, 0.)
            differences[key+"_vs_stage3"] = difference
        for key in ("real_gdp_trn", "nominal_gdp_trn", "tax_diagnostic_trn",
                    "consolidated_partial_balance_proxy_trn"):
            check("fixed_F", r[key], float(fixed[year][key]))
        for key in ("SQ_real_GDP", "N3_real_GDP"):
            check("fixed_reference_only", float(old[key]), float(fixed[year][key]))
        for key in LIMITS:
            check("national_NA", old[key], "N/A")
        check("gates", (r["gini_external_2035"], r["gini_triggered"], r["triggered"], r["fund_income_trn"]),
              (None, 0, 0, 0.))
        additions = {}
        for source in (a, b):
            for key, value in source.items():
                if key == "year":
                    continue
                if key in old:
                    difference = float(value)-float(old[key])
                    check("fixed_stage3_overlap", difference, 0.)
                    differences[key+"_vs_stage3"] = difference
                else:
                    additions[key] = value
        check("median_closed", float(a["closure_residual_yen"]), 0.)
        check("fiscal_closed", float(b["closure_residual_trn"]), 0.)
        annual.append(dict(old, **additions, **differences))
    return render(annual)


if __name__ == "__main__":
    run, reference, a_csv, b_csv, output = map(Path, sys.argv[1:])
    deps = load(PREVIOUS / "stage3-integrated/Dependencies.json")
    fixed = fixed_f(reference, next(d for d in deps if d["local"] == "retrieved/Legacy_Annual.csv"))
    checks = Checks()
    annual = calculate(run, fixed, csv_rows(a_csv.read_bytes()), csv_rows(b_csv.read_bytes()), checks)
    (output/"Annual.csv").write_bytes(annual)
    checks.save(output)
