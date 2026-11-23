"""Verify the fixed reference, threshold eligibility, accounts, and replay."""
import csv
import hashlib
import io
import json
import math
import sys
from collections import Counter
from pathlib import Path

fixed_file, runs, replay, output = map(Path, sys.argv[1:])
here = Path(__file__).parent
settings = json.loads((here/"Inputs.json").read_text())
fixed_data = fixed_file.read_bytes()
dependency = next(row for row in json.loads((here/"Dependencies.json").read_text())
                  if row["path"].endswith("/Legacy_Annual.csv"))
assert (len(fixed_data), hashlib.sha256(fixed_data).hexdigest()) == (dependency["size"], dependency["sha256"])
fixed = {int(row["year"]): row for row in csv.DictReader(io.StringIO(fixed_data.decode()))
         if row["case"] == "LEGACY_F"}
metrics = """
real_gdp_trn nominal_gdp_trn macro_cash_DI_proxy_trn household_disposable_nominal_trn
real_wage_proxy_man nominal_wage_proxy_man tax_diagnostic_trn tax_macro_feedback_proxy_trn
modeled_VAT_trn government_expenditure_after_pension_reclassification_trn
A_relief_trn B_used_trn C_cash_trn fund_income_trn fund_relief_trn I_policy_real_trn
capital_total_real_trn corporate_cash_flow_proxy_trn consolidated_partial_balance_proxy_trn population
""".split()
fixed_keys = """
real_gdp_trn nominal_gdp_trn tax_diagnostic_trn
tax_macro_feedback_proxy_trn I_policy_real_trn capital_total_real_trn corporate_cash_flow_proxy_trn
consolidated_partial_balance_proxy_trn corporate_tax_delta_trn corporate_credit_trn
""".split()
checks = Counter(fixed_reference_bytes=1)

def check(group, actual, expected):
    same = (math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-9)
            if isinstance(actual, float) and isinstance(expected, (float, int)) else actual == expected)
    assert same, (group, actual, expected)
    checks[group] += 1

def read(folder, case, filename):
    return (folder/case/filename).read_bytes()

def render(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=rows[0], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()

bands = settings["illustrative_residual_bands"]
cutoff = settings["new_threshold_sales_man"]
check("threshold_boundary", [b["sales_man"] for b in bands if b["sales_man"] > cutoff], [241, 500])
check("threshold_boundary", [b["sales_man"] for b in bands if b["sales_man"] <= cutoff], [239, 240])
cohort_base = sum(b["net_tax_inclusive_base_2026_trn"] for b in bands if b["sales_man"] > cutoff)

def calculate(folder):
    annual, differences = [], []
    paths = {case: json.loads(read(folder, case, "F_Actual_Annual.json")) for case in settings["cases"]}
    traces = {case: json.loads(read(folder, case, "F_Runtime_Trace.json")) for case in settings["cases"]}
    for case, rows in paths.items():
        previous_capital = 0.
        trace = traces[case]
        for year, row, off, t in zip(range(2026, 2056), rows, paths["OFF"], trace["years"], strict=True):
            check("continuity", row["year"], year)
            check("continuity", t["year"], year)
            active = case != "OFF" and year >= trace["parameters"]["admin_start"]
            check("activation", row["threshold_active"], int(active))
            check("activation", row["threshold_man"], cutoff if active else None)
            rate = row["standard_rate"]
            check("rate", row["threshold_rate"], rate)
            base = cohort_base * t["coreN"]/settings["reference_nominal_gdp_trn"] if active and case == "ON_SENSITIVITY" else 0.
            vat = base*rate/(1+rate)
            for key, value in (("threshold_residual_base_trn", base), ("threshold_incremental_vat_trn", vat),
                               ("threshold_seller_cash_trn", -vat),
                               ("threshold_investment_target_trn", -vat*trace["parameters"]["firm_investment_response"])):
                check("threshold_ledger", row[key], value)
            for key in ("modeled_VAT_trn", "VAT_delta_vs_fixed_reference_trn", "VAT_F_minus_current_SQ_trn"):
                check("VAT_once", row[key]-off[key], vat)
            check("VAT_once", row["modeled_VAT_trn"], row["VAT_national_reference_trn"]+row["VAT_local_reference_trn"])
            check("VAT_once", row["tax_residual_after_VAT_trn"], row["tax_diagnostic_trn"]-row["modeled_VAT_trn"])
            check("VAT_once", row["tax_diagnostic_trn"]-off["tax_diagnostic_trn"]
                  -row["tax_macro_feedback_proxy_trn"]+off["tax_macro_feedback_proxy_trn"], vat)
            check("seller_incidence_once", row["corporate_cash_flow_proxy_trn"]-off["corporate_cash_flow_proxy_trn"], -vat)
            check("partial_fiscal_bridge", row["consolidated_partial_balance_proxy_trn"]-off["consolidated_partial_balance_proxy_trn"],
                  row["tax_diagnostic_trn"]-off["tax_diagnostic_trn"])
            check("capital_identity", row["capital_delta_real_trn"],
                  (1-trace["parameters"]["depreciation"])*previous_capital+row["I_policy_real_trn"])
            previous_capital = row["capital_delta_real_trn"]
            for key in ("A_relief_trn", "B_used_trn", "C_cash_trn", "fund_income_trn", "fund_relief_trn", "population",
                        "government_expenditure_after_pension_reclassification_trn", "gini_triggered"):
                check("no_new_transfer_or_trigger", row[key], off[key])
            if case == "OFF":
                for key in fixed_keys:
                    check("fixed_F", row[key], float(fixed[year][key]))
            if case == "ON_ZERO" or not active:
                for key in metrics:
                    check("zero_effect", row[key], off[key])
            state = {key: row[key] for key in metrics}
            threshold = {key: value for key, value in row.items() if key.startswith("threshold_")}
            controls = {key: fixed[year][key] for key in ("SQ_real_GDP", "N3_real_GDP")}
            annual.append(dict(case=case, year=year, **state, **threshold, **controls,
                               actual_income_median="N/A", full_national_PB="N/A",
                               actual_threshold_firms="N/A"))
            differences.append(dict(case=case, year=year,
                                    **{key+"_vs_F": value-off[key] for key, value in state.items()},
                                    real_GDP_vs_fixed_SQ=state["real_gdp_trn"]-float(controls["SQ_real_GDP"]),
                                    real_GDP_vs_fixed_N3=state["real_gdp_trn"]-float(controls["N3_real_GDP"])))
    return render(annual), render(differences)

first, second = calculate(runs), calculate(replay)
for case in settings["cases"]:
    for name in ("F_Actual_Annual.json", "F_Runtime_Trace.json"):
        check("independent_runtime_replay", read(runs, case, name), read(replay, case, name))
for name, a, b in zip(("Annual.csv", "Comparison.csv"), first, second, strict=True):
    check("independent_csv_replay", a, b)
    (output/name).write_bytes(a)
(output/"Validation.json").write_text(json.dumps(dict(
    checks=sum(checks.values()), failures=0, groups=checks, cases=3, annual_rows=90,
    csv_sha256=[hashlib.sha256(data).hexdigest() for data in first]), indent=2)+"\n")
