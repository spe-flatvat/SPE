"""Export annual attribution and validate fixed comparisons and independent replay."""
import csv
import hashlib
import io
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

prior, runs, replay, output = map(Path, sys.argv[1:])
cases = json.loads(Path(__file__).with_name("Inputs.json").read_text())["cases"]
years = list(range(2026, 2056))
fixed_metrics = {
    "real_gdp_trn": "real_gdp_trn",
    "nominal_gdp_trn": "nominal_gdp_trn",
    "I_policy_real_trn": "I_policy_real_trn",
    "capital_total_real_trn": "capital_total_real_trn",
    "corporate_tax_delta_trn": "corporate_tax_delta",
    "corporate_credit_trn": "corporate_credit",
    "tax_macro_feedback_proxy_trn": None,
    "tax_diagnostic_trn": "tax_diagnostic_trn",
    "consolidated_partial_balance_proxy_trn": "consolidated_partial_balance_proxy_trn",
}
checks = defaultdict(int)

def check(group, actual, expected=True):
    equal = (math.isclose(actual, expected, abs_tol=1e-8, rel_tol=1e-11)
             if isinstance(actual, float) and isinstance(expected, (int, float))
             else actual == expected)
    assert equal, (group, actual, expected)
    checks[group] += 1

def read(name):
    with (prior / name).open(newline="") as stream:
        return list(csv.DictReader(stream))

def render(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()

published = {(r["case"], int(r["year"])): r for r in read("Integrated_Annual.csv")}
accounts = read("Corporate_Annual.csv")
schedules = defaultdict(float)
for row in read("Vintage_Schedules.csv"):
    schedules[row["case"], row["vintage"]] += float(row["shift"])
for shift in schedules.values():
    check("tax_vintage_lifetime_shift", shift, 0.)
for row in accounts:
    if int(row["year"]) < 2028:
        for key in ("guideline_applies", "disclosure_flag", "guideline_equipment"):
            check("guideline_pre_2028", float(row[key]), 0.)
    if row["case"] in ("GUIDELINE_ONLY", "BOTH_ON"):
        check("guideline_default_zero_behavior", float(row["guideline_equipment"]), 0.)

def load_rows(folder):
    paths = {}
    for name, switches in cases.items():
        annual = json.loads((folder / name / "F_Actual_Annual.json").read_bytes())
        trace = json.loads((folder / name / "F_Runtime_Trace.json").read_bytes())
        p = trace["parameters"]
        rows = {}
        previous_capital = 0.
        for year, row, t in zip(years, annual, trace["years"], strict=True):
            check("annual_continuity", row["year"], year)
            check("annual_continuity", t["year"], year)
            f = t["firm"]
            prior_schedule = [int(y) for y in p["defense_surcharge_schedule"] if int(y) <= year]
            surcharge = p["defense_surcharge_schedule"][str(max(prior_schedule))] if prior_schedule else 0.
            scale = t["coreN"] / 600.
            tax = p["corp_profit_base"] * scale * (.23 * (1 + surcharge) - p["corp_reference_rate"]) if year >= p["corp_start"] else 0.
            credit = (.23 * p["hyper_eligible_investment"] * p["hyper_extra_deduction"] * scale
                      if switches["hyper"] and year >= max(p["corp_start"], p["investment_start"]) else 0.)
            release = (p["governance_eligible_retained"] * p["governance_release_fraction"]
                       * min(1., (year - 2028 + 1) / 3) if switches["release"] and year >= 2028 else 0.)
            allocation = p["governance_allocation"]
            for key, expected in (("tax_delta", tax), ("credit", credit), ("release", release),
                                  ("investment", p["firm_investment_response"] * (credit-tax)
                                   + release * (allocation["equipment"] + allocation["research"]))):
                check("legacy_switch_and_formula", f[key] or 0., expected)
            check("firm_cash_once", t["firm_sources"], credit-tax+release+t["admin_firm"]
                  +t["vat_firm_cash"]+t["education_firm_cash"])
            check("firm_cash_once", t["firm_sources"], t["firm_investment"]+f["human"]+t["firm_uninvested"])
            check("macro_tax_once", row["tax_diagnostic_trn"], t["tax"]+t["direct"])
            check("economic_capital_identity", row["capital_delta_real_trn"],
                  (1-p["depreciation"])*previous_capital+row["I_policy_real_trn"])
            previous_capital = row["capital_delta_real_trn"]
            values = {key: row[key] for key in fixed_metrics}
            values.update(corporate_net_tax_change_trn=tax-credit,
                          corporate_release_trn=release,
                          corporate_induced_investment=f["investment"],
                          corporate_cash_flow_proxy_trn=t["firm_sources"],
                          corporate_cash_stock_proxy_trn=t["corporate_cash_stock"])
            ref = published["LEGACY_F" if name == "LEGACY_F" else "BOTH_OFF", year]
            if name in ("LEGACY_F", "BOTH_OFF"):
                for key, prior_key in fixed_metrics.items():
                    if prior_key:
                        check("fixed_regression", values[key], float(ref[prior_key]))
                check("fixed_regression", f["investment"], float(ref["corporate_induced_investment"]))
            rows[year] = values
        paths[name] = rows
    for year in years:
        baseline = paths["BOTH_OFF"][year]
        for name, series in paths.items():
            row = series[year]
            check("direct_corporate_tax_once",
                  row["tax_diagnostic_trn"]-row["tax_macro_feedback_proxy_trn"]
                  -baseline["tax_diagnostic_trn"]+baseline["tax_macro_feedback_proxy_trn"],
                  row["corporate_net_tax_change_trn"]-baseline["corporate_net_tax_change_trn"])
            if year < 2028:
                check("old_branches_pre_2028", row, baseline)
    return paths

def outputs(paths):
    annual, decomposition = [], []
    for name, path in paths.items():
        for year, row in path.items():
            fixed = published["LEGACY_F", year]
            annual.append(dict(case=name, year=year, **row, SQ_real_GDP=fixed["SQ_real_GDP"],
                               N3_real_GDP=fixed["N3_real_GDP"], actual_cash="N/A", complete_PB="N/A"))
    for year in years:
        off, hyper, release, legacy = (paths[name][year] for name in
                                         ("BOTH_OFF", "OLD_HYPER_ONLY", "OLD_RELEASE_ONLY", "LEGACY_F"))
        for key in off:
            h, r = hyper[key]-off[key], release[key]-off[key]
            total = legacy[key]-off[key]
            interaction = total-h-r
            check("attribution_identity", h+r+interaction, total)
            decomposition.append(dict(year=year, metric=key, legacy_minus_off=total,
                                      hyper_at_off=h, release_at_off=r, interaction=interaction,
                                      hyper_at_release_on=legacy[key]-release[key],
                                      release_at_hyper_on=legacy[key]-hyper[key]))
    return render(annual), render(decomposition)

a = outputs(load_rows(runs))
b = outputs(load_rows(replay))
for initial, repeated in zip(a, b, strict=True):
    check("independent_csv_byte_match", initial, repeated)
for case in cases:
    for name in ("F_Actual_Annual.json", "F_Runtime_Trace.json"):
        check("independent_runtime_byte_match", (runs/case/name).read_bytes(), (replay/case/name).read_bytes())
for name, data in zip(("Legacy_Annual.csv", "Attribution_Annual.csv"), a, strict=True):
    (output/name).write_bytes(data)

comparison = read("Comparison.csv")
check("prior_diagnostic_rows", len(comparison), 270)
check("prior_diagnostic_keys", len({(r["case"], r["year"]) for r in comparison}), 270)
for row in comparison:
    name, year = row["case"], int(row["year"])
    current = published[name, year]
    legacy, off = published["LEGACY_F", year], published["BOTH_OFF", year]
    for key in ("real_gdp_trn", "I_policy_real_trn", "capital_total_real_trn",
                "corporate_tax_delta", "tax_diagnostic_trn", "consolidated_partial_balance_proxy_trn"):
        check("prior_diagnostic_difference", float(row[key+"_vs_legacy"]), float(current[key])-float(legacy[key]))
        check("prior_diagnostic_difference", float(row[key+"_vs_off"]), float(current[key])-float(off[key]))
    for key in ("SQ_real_GDP", "N3_real_GDP"):
        check("fixed_SQ_N3", current[key], legacy[key])
    row.update(real_gdp_trn=current["real_gdp_trn"], SQ_real_GDP=current["SQ_real_GDP"],
               N3_real_GDP=current["N3_real_GDP"])
(output/"Diagnostic_Comparison.csv").write_bytes(render(comparison))
(output/"Validation.json").write_text(json.dumps(dict(
    checks=sum(checks.values()), failures=0, groups=checks, legacy_annual_rows=120,
    reused_diagnostic_rows=270, replay_csv_sha256=[hashlib.sha256(data).hexdigest() for data in a]),
    indent=2)+"\n")
