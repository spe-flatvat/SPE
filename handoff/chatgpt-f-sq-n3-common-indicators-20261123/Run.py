"""Rebuild the annual comparison from immutable Git execution originals."""
import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

YEARS = range(2026, 2056)
KEY_YEARS = (2026, 2035, 2045, 2055)
CASES = ("F", "SQ", "N3")
PAIRS = (("F", "SQ"), ("F", "N3"), ("N3", "SQ"))
VARIANT = "CURRENT_REFERENCE_UNCHANGED_COMMON_ON"
MATCHED = "7dd893eeed781af2bb323c424b456fdd907a667f"
SQ_PIN = "149bbf03675884cb8f3fcea96689ebc9e975fac7"
N3_PIN = "93b8393350eb73dd5ebd803b1ace429aaf4dfe1b"
F_PIN = "89e5ee2eead0f1b846d33ed0c315168fc461ceb9"
F_NATIVE = "6a9ccc854f7088339d58c9490174cc1463d2a203"
PREFIX = "handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123/"
SQ_DIR = "handoff/chatgpt-statusquo-common-macro-limited-diagnostic-20261123/"
N3_DIR = "handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/"
F_DIR = "handoff/chatgpt-f-middle-class-integrated-20261123/stage4-integrated/"
CONDITIONAL = "CONDITIONAL"
COMPARABLE = "COMPARABLE"

METRICS = {
    "real_gdp": (CONDITIONAL, "trillion JPY", "2026 model prices", "Final model real GDP"),
    "nominal_gdp": (CONDITIONAL, "trillion JPY", "current model prices", "Final model nominal GDP"),
    "implicit_gdp_deflator": (CONDITIONAL, "index", "2026=100", "100*(nominal GDP/real GDP)/(600/580)"),
    "population": (CONDITIONAL, "persons", "N/A", "Model total resident population"),
    "effective_labor": (CONDITIONAL, "model worker equivalents", "N/A", "Effective labor input to the model"),
    "real_gdp_growth": (CONDITIONAL, "percent", "2026 model prices", "100*(real GDP / prior-year real GDP - 1)"),
    "real_gdp_per_capita": (CONDITIONAL, "JPY/person", "2026 model prices", "Real GDP * 1e12 / model population"),
    "nominal_gdp_per_capita": (CONDITIONAL, "JPY/person", "current model prices", "Nominal GDP * 1e12 / model population"),
    "input_inflation": (COMPARABLE, "percent", "N/A", "Common runtime inflation input * 100"),
    "applied_real_risk": (COMPARABLE, "percent", "N/A", "Applied common real shock rate * 100"),
}
BLOCKED = {
    "employment_headcount": ("NOT COMPARABLE", "3;4", "F employment proxy and effective labor differ. N3 common core retains SQ labor, including no independent matched headcount series for all policy channels."),
    "national_tax": ("NOT COMPARABLE", "2;3;4", "SQ diagnostic, F partial tax bridge and N3 scoped tax bases. A calibrated government-wide tax base and common coverage are needed."),
    "national_wages_income": ("NOT COMPARABLE", "2;3;4", "F wage transmission, SQ modeled wage proxy and N3 gross tax base use different populations and concepts."),
    "national_household_cash": ("NOT COMPARABLE", "2;4", "F macro cash DI and N3 resource DI differ, with in-kind services outside comparable cash. F household cells are synthetic."),
    "household_purchasing_power": ("N/A", "1;2;4", "F fixed basket and synthetic groups are available. A shared household basket, cash DI and price transmission are needed for all three."),
    "national_gini": ("N/A", "1;3;4", "F synthetic equivalized Gini and N3 KPI or diagnostic tax cells do not supply three matched national distributions."),
    "national_government_balance_pb": ("NOT COMPARABLE", "2;3;4", "F partial public accounts and N3 conditional central/local closure have different consolidation coverage. SQ matched closure is not a national fiscal observation."),
    "national_bond_issue_interest_debt": ("N/A", "2;3;4;5", "F program subledgers and N3 scenario closure cannot supply common national issuance, interest and debt. Funding choices remain open."),
    "policy_fiscal_cost": ("NOT COMPARABLE", "2;3;4;5", "Program-specific payer and transfer boundaries differ. Common classifications and unresolved financing are needed."),
    "investment": ("NOT COMPARABLE", "2;3", "F policy investment state excludes the comparable replacement-investment flow present in SQ/N3."),
    "household_consumption": ("NOT COMPARABLE", "2;3;4", "SQ and F computed household consumption proxies and N3 realized model consumption have distinct policy mappings and in-kind boundaries."),
    "fund_stock": ("NOT COMPARABLE", "2;3", "F insurance relief funding and N3 pension fund have distinct stock boundaries."),
}

def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def write_json(path, document):
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def run(root, out):
    out.mkdir(parents=True, exist_ok=True)
    checks = Counter()
    sources = {}

    def require(group, condition, label):
        if not condition:
            raise ValueError(f"{group}: {label}")
        checks[group] += 1

    def close(group, a, b, label, tol=2e-8):
        require(group, math.isclose(float(a), float(b), rel_tol=2e-12, abs_tol=tol), (label, a, b))

    def source(name, pin, path):
        raw = subprocess.check_output(["git", "-C", str(root), "show", f"{pin}:{path}"])
        sources[name] = {"commit": pin, "path": path, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        decoded = raw.decode("utf-8")
        if path.endswith(".json"):
            return json.loads(decoded)
        if path.endswith(".csv"):
            return list(csv.DictReader(io.StringIO(decoded)))
        return decoded

    def annual(rows, label):
        found = {}
        for row in rows:
            year = int(row["year"])
            require("unique_year", year not in found, (label, year))
            found[year] = row
        require("complete_years", set(found) == set(YEARS), label)
        return found

    sq_raw = source("sq", MATCHED, PREFIX + "BASE_REPLAY/Common_Trace_BASE_REPLAY.json")
    f_raw = source("f_trace", MATCHED, PREFIX + "F/F_Runtime_Trace.json")
    n_parameters = source("n3_parameters", MATCHED, PREFIX + "N3/N3_Common_Input_Contract.json")
    n_denom = annual(source("n3_denominator", MATCHED, PREFIX + "N3/N3_SQ_Denominator_States.json"), "N3 denominator")
    sq = annual(sq_raw["years"], "SQ execution trace")
    f_trace = annual(f_raw["years"], "F execution trace")
    f = annual(source("f", MATCHED, PREFIX + "F/F_Actual_Annual.json"), "F execution annual")
    n = annual(source("n3", MATCHED, PREFIX + "N3/N3_Actual_Annual.json"), "N3 execution annual")
    reference = source("prior_comparison", MATCHED, PREFIX + "SPE_Three_Scenario_Annual_Comparison_2026_2055.csv")
    require("variant", len(reference) == 90 and {r["SQ_reference"] for r in reference} == {VARIANT}, "matched table")
    references = {case: annual([r for r in reference if r["case"] == case], case) for case in CASES}

    sq_prior = annual(source("sq_prior", SQ_PIN, SQ_DIR + "Common_Trace_BASE_REPLAY.json")["years"], "prior SQ")
    source("sq_variants", SQ_PIN, SQ_DIR + "SQ_Baseline_Variant_Provenance_And_Comparability.csv")
    n_prior = annual(source("n3_prior", N3_PIN, N3_DIR + "N3_SQ_Annual_GDP_Gap_Decomposition_2026_2055.csv"), "prior N3")
    old_f = annual(source("f_before_reconnection", MATCHED, PREFIX + "F_OLD/F_Actual_Annual.json"), "F before shared medical reference")
    f_native = annual([r for r in source("f_fixed_native", F_NATIVE, "handoff/f-common-endoflife-finalization-20261121/Annual.csv") if r["case"] == "LATEST_F"], "fixed F LATEST_F")
    f_input = source("f_native_input", F_NATIVE, "handoff/f-common-endoflife-finalization-20261121/Inputs.json")
    f_medical = source("f_medical_reference", MATCHED, PREFIX + "F/F_Medical_Reference_Inputs.json")
    for key in ("common_parameters", "common_financing", "clinical_strata", "registry_population_reference"):
        require("common_medical_contract", f_input[key] == n_parameters["medical_input"]["c"][key], key)
    for key in ("deflators", "population"):
        require("common_medical_reference", f_medical[key] == n_parameters["medical_input"][key], key)

    previous_pass = source("reused_validation", MATCHED, PREFIX + "Verification.json")
    require("reused_pass", previous_pass["status"] == "PASS" and previous_pass["failed"] == 0, "comparison engine")
    mid_validation = source("f_household_validation", F_PIN, F_DIR + "Validation.json")
    require("reused_pass", mid_validation["checks"] == 721 and mid_validation["failures"] == 0, "F household")
    mid = source("f_household", F_PIN, F_DIR + "Comparison.csv")

    for key in ("base_inflation", "oil_inflation_extra", "conflict_inflation_extra",
                "apply_oil_to_initial", "disaster_anchor", "climate_anchor", "base_growth",
                "labor_response", "oil_gdp_loss", "conflict_gdp_loss", "quake_gdp_loss",
                "disaster_gdp_loss", "climate_gdp_loss"):
        for params in (f_raw["parameters"], n_parameters["parameters"]):
            require("shared_input", params[key] == sq_raw["parameters"][key], key)

    annual_rows = []
    previous = {}
    f_bridge = []
    for year in YEARS:
        s, nt, ft, fr, nr = sq[year], n_denom[year], f_trace[year], f[year], n[year]
        for key in ("Y", "N", "coreY", "coreN", "coreD", "labor"):
            close("sq_fixed_trace", s[key], sq_prior[year][key], (year, key))
            close("n3_fixed_denominator", s[key], nt[key], (year, key))
        for key in ("growth", "inflation", "risk", "population"):
            if s[key] is None or sq_prior[year][key] is None:
                require("sq_fixed_initial_boundary", year == 2026 and s[key] is sq_prior[year][key] is None, (year, key))
            else:
                close("sq_fixed_trace", s[key], sq_prior[year][key], (year, key))
        close("n3_denominator_population", s["population"], nt["macro_row"]["population_persons"], year)
        for key in ("risk", "inflation"):
            close("f_shared_event_price", ft[key], s[key], (year, key))

        for key in ("real_gdp_trn", "nominal_gdp_trn", "population", "labor_force_population_proxy"):
            close("f_native_reference", old_f[year][key], f_native[year][key], (year, key), 0.001 if key in ("population", "labor_force_population_proxy") else 3e-6)
        close("f_trace_to_annual", ft["labor"], fr["labor_force_population_proxy"], year)
        for trace_key, annual_key in (("Y", "real_gdp_trn"), ("N", "nominal_gdp_trn")):
            close("f_trace_to_annual", ft[trace_key], fr[annual_key], (year, trace_key))
        f_bridge.append({"year": year,
                         "matched_f_real_gdp_minus_native_trn": fr["real_gdp_trn"] - old_f[year]["real_gdp_trn"],
                         "matched_f_nominal_gdp_minus_native_trn": fr["nominal_gdp_trn"] - old_f[year]["nominal_gdp_trn"]})
        for label, a, b in (
            ("N3 real", nr["real_GDP_trn"], n_prior[year]["N3_real_GDP_trn"]),
            ("N3 nominal", nr["nominal_GDP_trn"], n_prior[year]["N3_nominal_GDP_trn"]),
            ("SQ real", s["Y"], n_prior[year]["SQ_real_GDP_trn"]),
            ("SQ nominal", s["N"], n_prior[year]["SQ_nominal_GDP_trn"]),
            ("N3 gap", nr["real_GDP_trn"] - s["Y"], n_prior[year]["GDP_gap_trn"]),
        ):
            close("prior_n3_sq_gdp", a, b, (year, label))
        require("n3_existing_gi_off", nr["government_purchase_nominal_trn"] == nr["public_investment_nominal_trn"] == 0, year)

        values = {
            "F": (fr["real_gdp_trn"], fr["nominal_gdp_trn"], fr["population"], ft["labor"], ft["coreD"], ft["pressure"]),
            "SQ": (s["Y"], s["N"], s["population"], s["labor"], s["coreD"], s["pressure"]),
            "N3": (nr["real_GDP_trn"], nr["nominal_GDP_trn"], nt["macro_row"]["population_persons"], nt["labor"],
                   s["coreD"], sq_raw["parameters"]["price_pressure_coefficient"] * nr["unmet_demand_real_trn"] / s["coreY"]),
        }
        calculated = {}
        for case, (real, nominal, pop, labor, index, pressure) in values.items():
            marker = (case, year)
            require("positive_finite_inputs", all(math.isfinite(x) and x > 0 for x in (real, nominal, pop, labor, index)), marker)
            if year == 2026:
                require("price_population_base", (real, nominal, pop) == (580, 600, 122618024), marker)
            close("nominal_real_price_formula", nominal, real * index * (1 + pressure), marker)
            known = references[case][year]
            deflator = 100 * (nominal / real) / (600 / 580)
            growth = 100 * (real / previous[case] - 1) if case in previous else None
            for col, val in (("real_GDP_trn", real), ("nominal_GDP_trn", nominal), ("population", pop),
                             ("effective_labor_proxy", labor), ("implicit_deflator_normalized", deflator / 100),
                             ("implementation_price_index", index), ("price_pressure", pressure),
                             ("real_growth_pct", growth if growth is not None else 0),
                             ("GDP_minus_SQ_trn", real - s["Y"]), ("nominal_GDP_minus_SQ_trn", nominal - s["N"])):
                close("fixed_comparison_table", val, known[col], (marker, col))
            previous[case] = real
            real_pc, nominal_pc = real * 1e12 / pop, nominal * 1e12 / pop
            close("per_capita_reaggregation_real", real_pc * pop / 1e12, real, marker)
            close("per_capita_reaggregation_nominal", nominal_pc * pop / 1e12, nominal, marker)
            close("per_capita_deflator_invariance", (nominal_pc / real_pc) / (600 / 580) * 100, deflator, marker)
            calculated[case] = dict(zip(METRICS, (real, nominal, deflator, pop, labor, growth,
                                                 real_pc, nominal_pc, 100 * s["inflation"], 100 * s["risk"]), strict=True))

        for indicator, (status, unit, price, _) in METRICS.items():
            amounts = {case: calculated[case][indicator] for case in CASES}
            defined = amounts["F"] is not None
            gaps = {a + "_minus_" + b: amounts[a] - amounts[b] if defined else "N/A" for a, b in PAIRS}
            if defined:
                close("gap_telescope", gaps["F_minus_SQ"], gaps["F_minus_N3"] + gaps["N3_minus_SQ"], (year, indicator))
                if status == COMPARABLE:
                    require("matched_control_gap_zero", all(gap == 0 for gap in gaps.values()), (year, indicator))
            annual_rows.append({"year": year, "indicator": indicator, "status": status if defined else "N/A",
                                "unit": unit, "price_basis": price, "SQ_variant": VARIANT,
                                **{case: value if defined else "N/A" for case, value in amounts.items()}, **gaps})

    output_f = []
    for case in ("FIXED_F", "INTEGRATED"):
        rows = annual([r for r in mid if r["case"] == case], case)
        for year, row in sorted(rows.items()):
            output_f.append({"year": year, "case": case,
                             "status": "F_ONLY_SYNTHETIC_FIXED_REFERENCE" if case == "FIXED_F" else "F_ONLY_SYNTHETIC_NOT_ADOPTED",
                             **{k: row[k] for k in ("cash_median_real_2026_yen", "cash_median_real_2026_yen_delta_fixed",
                                                    "synthetic_cash_gini", "synthetic_cash_gini_delta_fixed",
                                                    "Q2_cash_real_2026_yen_delta_fixed", "Q3_cash_real_2026_yen_delta_fixed",
                                                    "Q4_cash_real_2026_yen_delta_fixed")}})
    all_keys = {(row["year"], row["indicator"]) for row in annual_rows}
    require("unique_output_and_years", len(all_keys) == len(annual_rows) == len(YEARS) * len(METRICS), "annual comparison")
    runtime_columns = {
        "real_gdp": ("f.real_gdp_trn", "sq.Y", "n3.real_GDP_trn"),
        "nominal_gdp": ("f.nominal_gdp_trn", "sq.N", "n3.nominal_GDP_trn"),
        "population": ("f.population", "sq.population", "n3_denominator.macro_row.population_persons"),
        "effective_labor": ("f_trace.labor", "sq.labor", "n3_denominator.labor"),
        "input_inflation": ("f_trace.inflation", "sq.inflation", "sq.inflation via n3_denominator"),
        "applied_real_risk": ("f_trace.risk", "sq.risk", "sq.risk via n3_denominator"),
    }
    excludes = {
        "employment_headcount": ("f_fixed_native+f", "sq", "n3.existing_public_added_jobs"),
        "national_tax": ("f.tax_diagnostic_trn", "sq.tax+sq.direct", "n3.total_tax_diagnostic_proxy_trn"),
        "national_wages_income": ("f.gross_wage_bill_proxy_trn", "n3_denominator.macro_row.nominal_wage_proxy_man", "n3.labor_gross_base_trn"),
        "national_household_cash": ("f.macro_cash_DI_proxy_trn", "n3_denominator.macro_row.household_disposable_nominal_trn", "n3.household_resource_DI_proxy_trn"),
        "household_purchasing_power": ("f_household", "N/A", "N/A"),
        "national_gini": ("f_household.synthetic_cash_gini", "N/A", "N/A"),
        "national_government_balance_pb": ("f.consolidated_partial_balance_proxy_trn", "n3.SQ_CL_PB_same_fiscal_scenario_trn", "n3.CL_PB_candidate_trn"),
        "national_bond_issue_interest_debt": ("f.bond_issue_trn+f.bond_interest_trn+f.bond_end_trn", "n3.SQ_CL_debt_same_fiscal_scenario_trn", "n3.CL_gross_issue_assumed_trn+n3.CL_interest_candidate_trn+n3.CL_debt_candidate_trn"),
        "policy_fiscal_cost": ("f.education_total_cost_trn+f.medical_unassigned_after_sources_trn", "sq.expenditure_core_nominal_proxy", "n3.existing_policy_government_cost_delta_trn"),
        "investment": ("f.I_policy_real_trn", "n3_denominator.macro_row.capital_replacement_investment_real_trn", "n3.private_investment_real_trn"),
        "household_consumption": ("f.household_consumption_real_proxy_trn", "sq.household_consumption_real_proxy", "n3.consumption_real_trn"),
        "fund_stock": ("f.fund_balance_trn", "N/A", "n3.pension_fund_end_trn"),
    }
    contract = []
    for indicator, (status, unit, price, definition) in METRICS.items():
        refs = runtime_columns.get(indicator, ("derived from F inputs", "derived from SQ inputs", "derived from N3 inputs"))
        scope = "F with existing shared medical reference; current SQ_COMMON_ON; native N3 BASE_REPLAY GI OFF"
        if status == COMPARABLE:
            scope = "Shared model input only; 2026 initialization has no macro transition and the oil event is not applied."
        contract.append({"indicator": indicator, "status": status, "unit": unit, "price_basis": price,
                         "available_years": "2027-2055" if indicator == "real_gdp_growth" else "2026-2055",
                         "definition": definition, **dict(zip(CASES, refs, strict=True)),
                         "cause_codes": "", "coverage_or_limitation": scope})
    for indicator, (status, causes, limitation) in BLOCKED.items():
        contract.append({"indicator": indicator, "status": status, "unit": "N/A", "price_basis": "N/A",
                         "available_years": "N/A", "definition": "No three-case comparison output",
                         **dict(zip(CASES, excludes[indicator], strict=True)),
                         "cause_codes": causes, "coverage_or_limitation": limitation})
    write_csv(out / "Comparison_Contract.csv", contract)
    write_csv(out / "Annual_Comparison.csv", annual_rows)
    write_csv(out / "Key_Years.csv", [row for row in annual_rows if row["year"] in KEY_YEARS])
    write_csv(out / "F_Native_To_Matched_Bridge.csv", f_bridge)
    write_csv(out / "F_Household_Context.csv", output_f)
    write_json(out / "Dependencies.json", sources)
    write_json(out / "Validation.json", {"status": "PASS", "checks": sum(checks.values()), "failed": 0,
                                        "check_groups": dict(sorted(checks.items())), "comparison_rows": len(annual_rows),
                                        "years": len(YEARS), "scenarios": len(CASES),
                                        "reused_model_checks": previous_pass["checks"], "reused_F_household_checks": mid_validation["checks"],
                                        "reused_checks_included_in_new_total": False})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    run(args.root, args.outdir)
