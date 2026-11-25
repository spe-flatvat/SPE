"""Reprice fixed SPE real paths. All GDP amounts are in trillion yen."""
import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

REQUEST = "01fd26973ff41797d424b51ec9894e279316d1b5"
COMMON = "8a8edb403b960cceb535f9b70461646e9374c229"
ATTRIBUTION = "adb373d87c5beb68b35f84be9e504c84d67014e0"
RECOVERY = "ff2e8c3d78d1c64c1d79f8d39dee3a9de786a6d8"
HOUSEHOLD = "89e5ee2eead0f1b846d33ed0c315168fc461ceb9"
CLAUDE = "da79ab621de27a1a2df8dd3edf050e4f02fac63a"
PREFIX = "handoff/chatgpt-"
YEARS = range(2026, 2056)
KEY_YEARS = (2026, 2030, 2035, 2045, 2055)
CASES = ("F", "SQ", "N3")
MODES = ("A", "P1", "P2", "P3", "P4")
D0 = 600 / 580


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(root, out):
    out.mkdir(parents=True, exist_ok=True)
    deps, checks = {}, Counter()

    def check(name, condition):
        if not condition:
            raise ValueError(f"{name} failed after {checks[name]} successful checks")
        checks[name] += 1

    def close(name, actual, expected):
        check(name, math.isclose(actual, expected, abs_tol=2e-8, rel_tol=1e-11))

    def raw(commit, path):
        data = subprocess.check_output(["git", "-C", str(root), "show", f"{commit}:{path}"])
        deps[path] = dict(commit=commit, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        return data

    def rows(commit, path):
        return list(csv.DictReader(io.StringIO(raw(commit, path).decode())))

    def dump(name, data):
        with (out / name).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, list(data[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(data)

    current_dir = PREFIX + "f-sq-n3-common-indicators-20261123/"
    prior_dir = PREFIX + "common-macro-gdp-attribution-20261124/"
    recovery_dir = PREFIX + "risk-specific-recovery-20261124/"
    household_dir = PREFIX + "f-middle-class-integrated-20261123/"
    claude_dir = "handoff/claude-f-sq-n3-common-indicators-verification-20261123/"
    for file in ("Run.py", "Report.md"):
        raw(COMMON, current_dir + file)
    upstream = json.loads(raw(COMMON, current_dir + "Dependencies.json"))
    for source in upstream.values():
        raw(source["commit"], source["path"])
        receipt = deps[source["path"]]
        check("common_pinned_inputs", (receipt["sha256"], receipt["bytes"]) ==
              (source["sha256"], source["bytes"]))

    def original(name):
        return json.loads(raw(upstream[name]["commit"], upstream[name]["path"]))

    sq = original("sq")
    sq_trace = sq["years"]
    f_input = original("f_trace")
    f_trace = f_input["years"]
    f_params = f_input["parameters"]
    params = sq["parameters"]
    comparison_path = upstream["prior_comparison"]
    current = {(int(r["year"]), r["case"]): r for r in
               rows(comparison_path["commit"], comparison_path["path"])}
    schedule = {int(r["year"]): r for r in rows(ATTRIBUTION, prior_dir + "Event_Schedule.csv")}
    recovery = {(int(r["year"]), r["scenario"], r["mode"]): r for r in
                rows(RECOVERY, recovery_dir + "Annual.csv")}
    common = {(int(r["year"]), r["indicator"]): r for r in
              rows(COMMON, current_dir + "Annual_Comparison.csv")}
    groups = {(int(r["year"]), r["case"], r["group"]): r for r in
              rows(HOUSEHOLD, household_dir + "stage3-purchasing-power/Groups.csv")}
    household = {(int(r["year"]), r["case"]): r for r in
                 rows(HOUSEHOLD, household_dir + "stage3-purchasing-power/Annual.csv")}
    ledger = {(int(r["year"]), r["case"]): r for r in
              rows(HOUSEHOLD, household_dir + "stage4-integrated/Comparison.csv")}
    for file in ("Run.py", "Report.md"):
        for commit, directory in ((RECOVERY, recovery_dir), (ATTRIBUTION, prior_dir),
                                  (HOUSEHOLD, household_dir + "stage4-integrated/")):
            raw(commit, directory + file)
    for commit, directory in ((COMMON, current_dir), (ATTRIBUTION, prior_dir),
                              (RECOVERY, recovery_dir), (HOUSEHOLD, household_dir + "stage4-integrated/"),
                              (CLAUDE, claude_dir)):
        raw(commit, directory + "Validation.json")
        receipt_name = "Custody_Verification.json" if commit == CLAUDE else "Custody.json"
        custody = json.loads(raw(commit, directory + receipt_name))
        for item in custody.get("files", []):
            path = item["path"]
            if path in deps:
                entry = deps[path]
                check("prior_receipt_comparison", (entry["bytes"], entry["sha256"]) ==
                      (item.get("bytes", item.get("size")), item["sha256"]))
    source_paths = (
        "policies/FreedomPolicies.md", "policies/FreedomPolicies_Annex.md",
        "policies/StatusQuo.md", "policies/New3linesPolicies.md",
        "specifications/SimulationSpecification_v6.md",
        "specifications/SimulationSpecification_v6_Annex.md",
        "engine/prototype.py", "engine/m8_scenario_runner.py",
        "handoff/f-tx01-tx03-20261118/SPE_F_TX_Model_DRAFT_20261118.py",
        "handoff/f-household-social-20261120/Model.py",
        "handoff/f-vat-core-20261120/Model.py",
        PREFIX + "statusquo-common-macro-limited-diagnostic-20261123/SQ_Common_Runtime.py",
        household_dir + "stage3-purchasing-power/Run.py",
        PREFIX + "common-price-nominal-real-request-20261125/"
        "SPE_Work_Common_Price_Nominal_Real_Connection_Request_20261125.md",
    )
    for path in source_paths:
        raw(REQUEST, path)
    check("coverage", len(current) == 90 and len(recovery) == 360 and list(schedule) == list(YEARS))
    check("fixed_settings", params["base_inflation"] == .02 and not params["apply_oil_to_initial"]
          and params["climate_anchor"] == 2028)

    annual, attribution, household_rows = [], [], []
    previous = {}
    base = params["base_inflation"]
    coefficient = params["price_pressure_coefficient"]
    base_path = event_path = no_real_risk_rule = sq_rule = f_rule = D0

    for i, y in enumerate(YEARS):
        s, f = sq_trace[i], f_trace[i]
        event = schedule[y]
        check("trace_year_and_oil", s["year"] == f["year"] == y and event["oil_applied"] == "False")
        check("climate_calendar", float(event["climate"]) ==
              (params["climate_gdp_loss"] if y >= 2028 and y % 2 == 0 else 0))
        extra = params["conflict_inflation_extra"] if y == 2027 else 0.
        inflation = base + extra
        for rate in (s["inflation"], f["inflation"], float(event["input_inflation"])):
            close("event_inflation", rate, inflation)
        close("growth_risk_schedule", s["risk"], float(event["total"]))
        if i:
            base_path *= 1 + base
            event_path *= 1 + inflation
            no_real_risk_rule *= 1 + inflation / (1 + s["growth"] + s["risk"])
            sq_rule *= 1 + inflation / (1 + s["growth"])
            f_rule *= 1 + inflation / (1 + f["growth"])
            for trace, prior, rule in ((s, sq_trace[i-1], sq_rule),
                                       (f, f_trace[i-1], f_rule)):
                close("real_core_recurrence", trace["coreY"], prior["coreY"] * (1 + trace["growth"]))
                close("nominal_core_recurrence", trace["coreN"],
                      prior["coreN"] * (1 + trace["growth"] + inflation))
                close("core_price_recurrence", rule, trace["coreD"])
        close("base_compounding", base_path, D0 * 1.02**i)
        close("event_level_persistence", event_path / base_path, 1.07 / 1.02 if i else 1.)

        for case in CASES:
            ref = current[y, case]
            real, nominal, pop, d, p = (float(ref[key]) for key in
                                       ("real_GDP_trn", "nominal_GDP_trn", "population",
                                        "implementation_price_index", "price_pressure"))
            for metric, value in (("real_gdp", real), ("nominal_gdp", nominal),
                                  ("implicit_gdp_deflator", 100 * nominal / real / D0)):
                close("fixed_common_indicator", value, float(common[y, metric][case]))
            rule = f_rule if case == "F" else sq_rule
            baseline = recovery[y, case, "A"]
            close("baseline_real", real, float(baseline["real_gdp"]))
            close("baseline_population", pop, float(baseline["population"]))
            close("baseline_core", float(baseline["core"]), (f if case == "F" else s)["coreY"])
            close("baseline_pressure_reconstruction", p,
                  coefficient * float(baseline["unmet"]) / float(recovery[y, "SQ" if case == "N3" else case, "A"]["core"]))
            close("baseline_price", d, rule)
            close("baseline_nominal", nominal, real * d * (1 + p))
            components = {
                "anchor": D0 - 1,
                "trend": base_path - D0,
                "event_price": event_path - base_path,
                "additive_rule_excluding_real_risk": no_real_risk_rule - event_path,
                "additive_rule_real_risk_interaction": sq_rule - no_real_risk_rule,
                "policy_labor_indirect": rule - sq_rule,
                "policy_direct_price_applied": 0.,
                "supply_pressure": d * p,
            }
            residual = nominal / real - 1 - sum(components.values())
            close("decomposition_closure", residual, 0.)
            attribution.append(dict(year=y, scenario=case, **{k + "_trn": v * real for k, v in components.items()},
                                    **{k + "_index_points": 100*v / D0 for k, v in components.items() if k != "anchor"},
                                    residual_trn=residual * real, nominal_minus_real_trn=nominal-real,
                                    gap_vs_2pct_deflator_points=100*(nominal/real-base_path)/D0,
                                    direct_policy_price_causal_estimate="N/A"))

            for mode in MODES:
                state = {"P3": "C", "P4": "D"}.get(mode, "A")
                actual = recovery[y, case, state]
                volume = float(actual["real_gdp"])
                pressure = p
                if state != "A":
                    unmet = max(0., float(actual["desired"]) - volume)
                    close("recovery_unmet", unmet, float(actual["unmet"]))
                    core = float(recovery[y, "SQ" if case == "N3" else case, state]["core"])
                    pressure = coefficient * unmet / core
                if mode == "P1":
                    price, pressure = base_path, 0.
                else:
                    price = d if mode == "A" else event_path
                value = nominal if mode == "A" else volume * price * (1 + pressure)
                index = 100 * (value / volume) / D0
                old = previous.get((case, mode))
                if not i:
                    check("initial_anchor", (volume, value, index) == (580., 600., 100.))
                previous[case, mode] = index
                close("annual_identity", value, volume * price * (1 + pressure))
                close("annual_deflator_identity", value, volume * D0 * index / 100)
                real_pc, nominal_pc = volume * 1e12 / pop, value * 1e12 / pop
                close("real_per_capita", real_pc * pop / 1e12, volume)
                close("nominal_per_capita", nominal_pc * pop / 1e12, value)
                annual.append(dict(year=y, scenario=case, mode=mode,
                                   origin="REUSED" if mode == "A" else "NON_ADOPTED_DIAGNOSTIC",
                                   real_gdp_trn=volume, nominal_gdp_trn=value,
                                   price_coefficient=price, pressure_fraction=pressure,
                                   pressure_nominal_trn=volume * price * pressure,
                                   deflator_2026_100=index,
                                   annual_deflator_growth_pct="N/A" if old is None else 100*(index/old-1),
                                   fixed_source_input_inflation_pct=100*inflation,
                                   applied_event_inflation_pp=100*extra if mode != "P1" else 0.,
                                   population=pop, real_per_capita_yen=real_pc, nominal_per_capita_yen=nominal_pc,
                                   nominal_minus_real_trn=value-volume,
                                   nominal_using_current_price_and_recomputed_pressure_trn=
                                   volume*d*(1+pressure) if state != "A" else "N/A",
                                   nominal_using_current_effective_price_trn=volume*d*(1+p) if state != "A" else "N/A"))

    for (y, case), entry in household.items():
        if case not in ("FIXED_F", "INTEGRATED"):
            continue
        record = dict(entry)
        check("household_year", y in YEARS)
        close("B_excluded_from_cash", float(entry["resources_real_2026_yen_at_cell"]),
              float(entry["cash_real_2026_yen_at_cell"]) + float(entry["B_value_real_2026_yen_at_cell"]))
        close("basket_excluded_from_cash", float(entry["cash_plus_VAT_fixed_basket_real_2026_yen_at_cell"]),
              float(entry["cash_real_2026_yen_at_cell"]) + float(entry["VAT_price_real_2026_yen_at_cell"]))
        for group in ("Q2", "Q3", "Q4"):
            for key in ("cash_real_2026_yen", "B_value_real_2026_yen", "VAT_price_real_2026_yen",
                        "cash_plus_VAT_fixed_basket_real_2026_yen"):
                value = ledger[y, case][group + "_" + key]
                close("household_stage3_stage4", float(value), float(groups[y, case, group][key]))
                record[group + "_" + key] = value
            close("same_basket_across_integrated_cases",
                  float(record[group + "_VAT_price_real_2026_yen"]),
                  float(ledger[y, "FIXED_F"][group + "_VAT_price_real_2026_yen"]))
        record.update(standard_VAT_pct=10 if y < f_params["year8"] else 8 if y < f_params["year5"] else 5,
                      food_VAT_pct=8 if y < f_params["food_zero_start"] else
                      0 if y < f_params["food_eight_start"] else 8 if y < f_params["year5"] else 5,
                      national_CPI="N/A", direct_VAT_GDP_price_input="NOT_WIRED",
                      direct_B_GDP_price_input="NOT_WIRED")
        household_rows.append(record)
    check("household_coverage", len(household_rows) == 60)

    indexed = {(r["year"], r["scenario"], r["mode"]): r for r in annual}
    check("output_coverage", len(indexed) == len(annual) == 450 and len(attribution) == 90)
    gaps = []
    for y in YEARS:
        for mode in MODES:
            for metric in ("real_gdp_trn", "nominal_gdp_trn", "deflator_2026_100",
                           "real_per_capita_yen", "nominal_per_capita_yen"):
                f, s, n = (indexed[y, case, mode][metric] for case in CASES)
                close("policy_gap_closure", f-s, (f-n)+(n-s))
                gaps.append(dict(year=y, mode=mode, metric=metric, F_minus_SQ=f-s,
                                 N3_minus_SQ=n-s, F_minus_N3=f-n))
    dump("Annual.csv", annual)
    dump("Key_Years.csv", [r for r in annual if r["year"] in KEY_YEARS])
    dump("Price_Contribution.csv", attribution)
    dump("Policy_Gaps.csv", gaps)
    dump("F_Household_Price.csv", household_rows)
    save(out / "Dependencies.json", deps)
    save(out / "Validation.json", dict(status="PASS", new_checks=sum(checks.values()),
                                       groups=dict(sorted(checks.items())), reused_rows=90,
                                       new_rows=360, prior_PASS_count_included=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    run(args.root.resolve(), args.outdir)
    with tempfile.TemporaryDirectory() as directory:
        second = Path(directory)
        run(args.root.resolve(), second)
        files = sorted(p.name for p in second.iterdir())
        for name in files:
            if (second / name).read_bytes() != (args.outdir / name).read_bytes():
                raise ValueError(f"Non-reproducible output: {name}")
    validation = args.outdir / "Validation.json"
    data = json.loads(validation.read_text())
    data["rerun_byte_identical"] = files
    save(validation, data)
