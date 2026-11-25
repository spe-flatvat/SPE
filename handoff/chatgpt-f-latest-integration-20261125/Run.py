"""Reproduce the fixed native household grid and connect incremental F flows."""
import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from itertools import accumulate
from pathlib import Path

REQUEST = "248cd3ace9ddcb771e9a766363ad8a2349a48fb9"
MATCH = "7dd893eeed781af2bb323c424b456fdd907a667f"
NATIVE = "6a9ccc854f7088339d58c9490174cc1463d2a203"
COMMON = "8a8edb403b960cceb535f9b70461646e9374c229"
HOUSE = "89e5ee2eead0f1b846d33ed0c315168fc461ceb9"
PRICE = "2d8cb85878c931d9d127755af6d2eb336c04c04d"
REC = "ff2e8c3d78d1c64c1d79f8d39dee3a9de786a6d8"
RES = "5f5443d168c9225b33e7d7c85ae6e7d119054f4a"
CAL = "893a66dd4e10f6dbf7aee183b363e4073ad2e0d0"
FIN = "cb27577f359211310202c0af022a617a0b3f047e"
CLAUDE = "da79ab621de27a1a2df8dd3edf050e4f02fac63a"
H = "handoff/chatgpt-"
D0 = 600 / 580
TRN = 1e12
YEARS = range(2026, 2056)
KEYS = (2026, 2030, 2035, 2043, 2045, 2055)
TERMS = ("A_relief", "C_redistribution", "B_substitution", "B_service", "net_wage_replacement")


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(root, out, work):
    out.mkdir(parents=True, exist_ok=True)
    sources, checks = {}, Counter()

    def check(name, condition):
        if not condition:
            raise ValueError(f"{name} failed after {checks[name]} successful checks")
        checks[name] += 1

    def close(name, a, b, tolerance=2e-8):
        check(name, math.isclose(a, b, abs_tol=tolerance, rel_tol=1e-11))

    def raw(ref, path):
        data = subprocess.check_output(["git", "-C", str(root), "show", f"{ref}:{path}"])
        sources[ref + ":" + path] = dict(commit=ref, path=path, bytes=len(data),
                                         sha256=hashlib.sha256(data).hexdigest())
        return data

    def js(ref, path):
        return json.loads(raw(ref, path))

    def read(ref, path):
        return list(csv.DictReader(io.StringIO(raw(ref, path).decode())))

    def put(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def dump(name, rows):
        with (out / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, rows[0].keys(), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def index(rows, *keys):
        return {tuple(int(r[k]) if k == "year" else r[k] for k in keys):r for r in rows}

    def n(row, key):
        return float(row[key])

    matched_dir = H + "sq-baseline-contract-three-scenario-recalculation-20261123/"
    price_dir = H + "common-price-nominal-real-20261125/"
    rec_dir = H + "risk-specific-recovery-20261124/"
    house_dir = H + "f-middle-class-integrated-20261123/"
    common_dir = H + "f-sq-n3-common-indicators-20261123/"
    prior_dir = H + "f-hyper-depreciation-retained-earnings-20261123/"
    fiscal_dir = H + "f-median-fiscal-residual-20261123/fiscal-residual/"
    trace = js(MATCH, matched_dir + "F/F_Runtime_Trace.json")
    parameters = trace["parameters"]
    matched = index(js(MATCH, matched_dir + "F/F_Actual_Annual.json"), "year")
    unaligned = index(js(MATCH, matched_dir + "F_OLD/F_Actual_Annual.json"), "year")
    prices = index(read(PRICE, price_dir + "Annual.csv"), "year", "scenario", "mode")
    recover = index(read(REC, rec_dir + "Annual.csv"), "year", "scenario", "mode")
    common = index(read(COMMON, common_dir + "Annual_Comparison.csv"), "year", "indicator")
    fixed = index(read(HOUSE, house_dir + "stage4-integrated/Comparison.csv"), "year", "case")
    power = index(read(HOUSE, house_dir + "stage3-purchasing-power/Annual.csv"), "year", "case")
    stage1 = index(read(HOUSE, house_dir + "stage1-benefits-burdens/Annual.csv"), "year", "case")
    fiscal = index(read(RES, fiscal_dir + "Annual.csv"), "year")
    integrated_cells = defaultdict(dict)
    for row in read(HOUSE, house_dir + "stage1-benefits-burdens/Cells.csv"):
        cells = integrated_cells[int(row["year"])]
        check("unique_integrated_cell", row["cell"] not in cells)
        cells[row["cell"]] = row

    fixed_deps = js(HOUSE, house_dir + "stage1-benefits-burdens/Dependencies.json")
    for item in fixed_deps["fixed_dependencies"]:
        data = raw(item["ref"], item["path"])
        check("stage1_dependency_bytes", len(data) == item["size"] and
              hashlib.sha256(data).hexdigest() == item["sha256"])
    for item in js(COMMON, common_dir + "Dependencies.json").values():
        data = raw(item["commit"], item["path"])
        check("common_dependency_bytes", len(data) == item["bytes"] and
              hashlib.sha256(data).hexdigest() == item["sha256"])
    for ref, directory in ((HOUSE, house_dir + "stage4-integrated/"),
                           (PRICE, price_dir), (REC, rec_dir)):
        for item in js(ref, directory + "Custody.json")["files"]:
            key = ref + ":" + item["path"]
            if key in sources:
                entry = sources[key]
                check("prior_receipt_bytes", (entry["bytes"], entry["sha256"]) ==
                      (item.get("bytes", item.get("size")), item["sha256"]))
    for ref, path in (
        (REQUEST, "policies/FreedomPolicies.md"), (REQUEST, "policies/FreedomPolicies_Annex.md"),
        (REQUEST, "specifications/SimulationSpecification_v6.md"), (REQUEST, "engine/m8_scenario_runner.py"),
        (REQUEST, "handoff/f-vat-core-20261120/Model.py"),
        (REQUEST, "handoff/f-household-social-20261120/Model.py"),
        (REQUEST, H + "f-policy-coverage-completion-20261123/Coverage.md"),
        (MATCH, matched_dir + "Three_Scenario_Worker.py"),
        (COMMON, common_dir + "Run.py"), (COMMON, common_dir + "Report.md"),
        (NATIVE, "handoff/f-common-endoflife-finalization-20261121/Inputs.json"),
        (NATIVE, "handoff/f-common-endoflife-finalization-20261121/Validation.json"),
        (CAL, H + "f-income-calibration-20261123/implementation/Report.md"),
        (FIN, H + "f-middle-income-financing-20261123/financing-sensitivity/Report.md"),
        (RES, fiscal_dir + "Report.md"), (PRICE, price_dir + "Report.md"),
        (REC, rec_dir + "Report.md"),
        ("adb373d87c5beb68b35f84be9e504c84d67014e0", H + "common-macro-gdp-attribution-20261124/Report.md"),
        (CLAUDE, "handoff/claude-f-sq-n3-common-indicators-verification-20261123/Validation.json"),
        (REQUEST, H + "f-latest-integration-request-20261125/"
         "SPE_Work_F_Latest_Implementation_Integration_Request_20261125.md"),
    ):
        raw(ref, path)
    for stage in ("stage1-benefits-burdens", "stage2-income-incidence",
                  "stage3-purchasing-power", "stage4-integrated"):
        for filename in ("Run.py", "Validation.json", "Report.md"):
            raw(HOUSE, house_dir + stage + "/" + filename)

    manifest = raw(RES, prior_dir + "Runtime_Sources.json")
    replay_dir = H + "f-distribution-fiscal-integration-20261123/stage1-distribution/"
    for name in ("Replay.py", "Dependencies.json"):
        put(work / name, raw(RES, replay_dir + name))
    put(work / "prior/Runtime_Sources.json", manifest)
    runtime = work / "runtime"
    for item in json.loads(manifest):
        data = raw(item["ref"], item["fixed_path"])
        check("replay_runtime_bytes", len(data) == item["size"] and
              hashlib.sha256(data).hexdigest() == item["sha256"])
        put(runtime / item["path"], data)
    subprocess.run([sys.executable, str(work / "Replay.py"), str(runtime),
                    str(work / "prior"), str(work / "native")], check=True, capture_output=True)
    grid = json.loads((work / "native/Household_Cells.json").read_bytes())
    native = index(json.loads((work / "native/F_Actual_Annual.json").read_bytes()), "year")
    b_settings = json.loads((runtime / "handoff/f-vat-core-20261120/Inputs.json").read_bytes())[
        "household_inputs"]["defaults"]
    native_pinned = index([r for r in read(NATIVE, "handoff/f-common-endoflife-finalization-20261121/Annual.csv")
                           if r["case"] == "LATEST_F"], "year")

    annual, delta_rows, funding = [], [], []
    states = {m: dict.fromkeys(TERMS, 0.) for m in ("F2", "F3")}
    for t, year in zip(trace["years"], YEARS, strict=True):
        check("trace_year", t["year"] == year)
        m, old, p = matched[year,], native[year,], stage1[year, "INTEGRATED"]
        baseline, previous_p3 = (prices[year, "F", mode] for mode in ("A", "P3"))
        baseline_house = fixed[year, "FIXED_F"]
        integrated_house = fixed[year, "INTEGRATED"]
        for col in ("real_gdp_trn", "nominal_gdp_trn", "population", "common_deflator"):
            close("fixed_LATEST_F_to_unaligned", unaligned[year,][col], n(native_pinned[year,], col),
                  .001 if col == "population" else 3e-6)
        for col in ("real_gdp", "nominal_gdp", "population"):
            price_col = col + "_trn" if col != "population" else col
            close("fixed_A_comparators", n(baseline, price_col), n(common[year, col], "F"))
            for case in ("SQ", "N3"):
                close("fixed_A_comparators", n(prices[year, case, "A"], price_col), n(common[year, col], case))
        for col in ("real_gdp_trn", "nominal_gdp_trn", "population"):
            close("matched_fixed_A", m[col], n(baseline, col))
        close("matched_labor", t["labor"], n(common[year, "effective_labor"], "F"))
        close("matched_cash_price_bridge", m["macro_cash_DI_proxy_trn"],
              m["household_disposable_nominal_trn"] - m["household_direct_price_benefit_trn"])
        close("fixed_C_budget", old["C_cash_trn"], n(p, "C_budget_trn"))
        close("unchanged_B_basis", old["B_used_trn"], m["B_used_trn"])
        close("unchanged_A_basis", old["A_relief_trn"], m["A_relief_trn"])
        close("unchanged_A_tax_basis", old["tax_increase_trn"], m["tax_increase_trn"])
        close("no_earmark", sum(abs(m[k]) for k in ("fund_income_trn", "fund_relief_trn", "C_earmarked_funding_trn")), 0.)
        close("native_C_budget_closure", n(p, "C_paid_trn") + n(p, "C_unallocated_trn"), n(p, "C_budget_trn"))
        close("native_wage_pool", n(p, "wage_trn"), old["household_wage_allocation_trn"] if year > 2026 else 0.)
        close("native_backfill", n(p, "A_government_backfill_trn"), n(p, "A_recalculated_trn"))

        # Keep the published sensitivity's cell eligibility and shares. Map its
        # wage and allocated-C fractions onto the already booked common-F pools.
        wc = m["household_wage_allocation_trn"] / n(p, "wage_trn") if n(p, "wage_trn") else 0.
        cc = m["C_cash_trn"] / old["C_cash_trn"] if old["C_cash_trn"] else 0.
        flows = dict.fromkeys(TERMS, 0.)
        totals = defaultdict(float)
        cells = integrated_cells[year]
        check("cell_coverage", set(cells) == {r["id"] for r in grid[str(year)]})
        for o in grid[str(year)]:
            r = cells[o["id"]]
            w = o["households"] / TRN
            mpc = o["mpc"]
            close("fixed_cell_weight", n(r, "households"), o["households"])
            close("fixed_cell_A", n(r, "orig_A"), o["A_yen"])
            close("fixed_cell_C", n(r, "orig_C"), o["C_cash_yen"])
            close("fixed_cell_gross", n(r, "gross_income_yen"), o["gross_income_yen"])
            close("integrated_cell_gross", n(r, "adjusted_gross"), o["gross_income_yen"] + n(r, "wage"))
            a, c, b = (n(r, "A_yen")-o["A_yen"],
                       (n(r, "C_cash_yen")-o["C_cash_yen"])*cc,
                       n(r, "B_used_yen")-o["B_used_yen"])
            at = n(r, "A_income_tax") - o["tax_increase_yen"]
            al = n(r, "A_resident_tax") - o["local_tax_increase_yen"]
            pension, nt, lt, wage = (n(r, name)*wc for name in ("pension", "income_tax", "resident_tax", "wage"))
            lost_b = int(r["B_exit"])
            bs = -o["B_substitute_yen"] * lost_b
            admin = -o["B_admin_yen"] * lost_b
            close("B_fixed_use_eligibility", b, -o["B_used_yen"] * lost_b)
            check("threshold_no_outside_payment", (not n(r, "C_cash_yen") or n(r, "adjusted_gross") <= 5e6)
                  and (not n(r, "A_yen") or n(r, "adjusted_gross") < 5e6)
                  and (not n(r, "B_used_yen") or n(r, "adjusted_gross") <= 3e6))
            source_net = n(r, "wage") - sum(n(r, x) for x in ("pension", "income_tax", "resident_tax"))
            close("native_cell_cash_closure", n(r, "cash")-o["cash_DI_after_yen"],
                  source_net + a + n(r, "C_cash_yen") - o["C_cash_yen"] - at - al, 2e-6)
            net = wage-pension-nt-lt
            flows["A_relief"] += w*mpc*(a-at-al)
            flows["C_redistribution"] += w*mpc*c
            flows["B_substitution"] += w*(mpc-1)*bs
            flows["B_service"] += w*b
            flows["net_wage_replacement"] += w*(mpc*net-parameters["generic_mpc"]*wage)
            for key, value in dict(A=a, C=c, B=b, admin=admin, national=nt+at, local=lt+al,
                                   pension=pension, wage=wage, cash=a+c-at-al-(pension+nt+lt)).items():
                totals[key] += w*value

        for branch, reference in (("FIXED_F", baseline_house), ("INTEGRATED", integrated_house)):
            ordered = sorted((o["cash_DI_after_yen"] if branch == "FIXED_F" else n(cells[o["id"]], "cash"),
                              o["id"], o["households"]) for o in grid[str(year)])
            half = sum(r[2] for r in ordered)/2
            rank, median = next((i, row) for i, (row, cumulative) in enumerate(
                zip(ordered, accumulate(r[2] for r in ordered), strict=True), 1) if cumulative >= half)
            check("synthetic_median_rank", rank == int(reference["median_rank"]) and median[1] == reference["median_cell"])
            close("synthetic_median_price_basis", median[0]/(old["common_deflator"]/D0),
                  n(reference, "cash_median_real_2026_yen"), 2e-6)
        close("mapped_wage_existing_once", totals["wage"],
              m["household_wage_allocation_trn"] if year > 2026 else 0.)
        close("mapped_C_budget_closure", totals["C"] + cc*n(p, "C_unallocated_trn"), 0.)
        close("macro_cash_excludes_rebooked_gross", totals["cash"], totals["A"]+totals["C"]-
              totals["national"]-totals["local"]-totals["pension"])
        bcost = totals["B"] * b_settings["B_cost_factor"]
        gov_delta = (totals["A"]+totals["C"]+bcost*b_settings["B_government_share"]+
                     totals["admin"]-totals["national"]-totals["local"])
        insurer_delta = bcost*(1-b_settings["B_government_share"])-totals["pension"]
        close("funding_consolidation", gov_delta+insurer_delta,
              totals["A"]+totals["C"]+bcost+totals["admin"]-totals["national"]-
              totals["local"]-totals["pension"])
        private_flow = sum(v for label,v in flows.items() if label != "B_service")
        saving = totals["cash"]-private_flow
        close("cash_consumption_saving", totals["cash"], private_flow+saving)

        for mode in ("F0", "F1", "F2", "F3"):
            modified = mode in states
            diagnostic = mode == "F3"
            recovered = recover[year, "F", "C" if diagnostic else "A"]
            price = previous_p3 if diagnostic else baseline
            d = n(price, "price_coefficient")
            desired, capacity, core = (n(recovered, col) for col in ("desired", "capacity", "core"))
            ref_real = n(price, "real_gdp_trn")
            ref_nom = n(price, "nominal_gdp_trn")
            close("reference_supply", min(desired, capacity), ref_real)
            state = states.get(mode, dict.fromkeys(TERMS, 0.))
            domestic = parameters["domestic_share"]
            close("domestic_import_proxy_closure", domestic*sum(flows.values())+
                  (1-domestic)*sum(flows.values()), private_flow+flows["B_service"])
            smoothing = parameters["lambda_C"]
            if modified and year > 2026:
                for term in TERMS:
                    state[term] = (1-smoothing)*state[term]+smoothing*domestic*flows[term]/d
            ordered_real, ordered_nom = ref_real, ref_nom
            for term in TERMS:
                if not modified:
                    continue
                desired += state[term]
                real = min(desired, capacity)
                pressure = parameters["price_pressure_coefficient"]*max(0., desired-real)/core
                nom = real*d*(1+pressure)
                delta_rows.append(dict(year=year, series=mode, term=term,
                                       raw_nominal_demand_delta_trn=flows[term],
                                       smoothed_domestic_real_state_delta_trn=state[term],
                                       real_GDP_delta_trn=real-ordered_real,
                                       nominal_GDP_delta_trn=nom-ordered_nom))
                ordered_real, ordered_nom = real, nom
            real, nominal = ordered_real, ordered_nom
            pressure = parameters["price_pressure_coefficient"]*max(0., desired-real)/core
            check("supply_capacity", real <= capacity and real <= desired)
            close("GDP_price_identity", nominal, real*d*(1+pressure))
            if mode in ("F0", "F1"):
                close("F0_F1_fixed_real", real, m["real_gdp_trn"])
                close("F0_F1_fixed_nominal", nominal, m["nominal_gdp_trn"])
            if year == 2026:
                close("initial_GDP_real", real, 580.)
                close("initial_GDP_nominal", nominal, 600.)
            pop = n(price, "population")
            comparators = {s: prices[year, s, "P3" if diagnostic else "A"] for s in ("SQ", "N3")}
            hh = integrated_house if modified else baseline_house
            hh_power = power[year, "INTEGRATED" if modified else "FIXED_F"]
            record = dict(year=year, series=mode, reference_condition="P3" if diagnostic else "A",
                          real_gdp_trn=real, nominal_gdp_trn=nominal, population=pop,
                          effective_labor_proxy=t["labor"], real_pc_yen=real*TRN/pop,
                          nominal_pc_yen=nominal*TRN/pop, GDP_deflator_2026_100=100*nominal/real/D0,
                          price_pressure_fraction=pressure, delta_real_vs_same_condition_F=real-ref_real,
                          delta_nominal_vs_same_condition_F=nominal-ref_nom,
                          delta_real_vs_F0=real-m["real_gdp_trn"], delta_nominal_vs_F0=nominal-m["nominal_gdp_trn"],
                          prior_recovery_C_real_delta_trn=ref_real-m["real_gdp_trn"] if diagnostic else 0.,
                          prior_recovery_C_nominal_at_A_price_delta_trn=
                          n(price, "nominal_using_current_effective_price_trn")-m["nominal_gdp_trn"] if diagnostic else 0.,
                          prior_P2_price_nominal_delta_trn=
                          ref_nom-n(price, "nominal_using_current_effective_price_trn") if diagnostic else 0.,
                          fixed_common_cash_proxy_trn=m["macro_cash_DI_proxy_trn"],
                          connected_cash_proxy_trn=m["macro_cash_DI_proxy_trn"]+(totals["cash"] if modified else 0.),
                          F1_plus_cash_and_B_resources_proxy_trn="N/A" if mode == "F0" else
                          m["macro_cash_DI_proxy_trn"]+m["B_used_trn"]+
                          (totals["cash"]+totals["B"] if modified else 0.),
                          F1_plus_partial_government_ABC_funding_residual_trn="N/A" if mode == "F0" else
                          m["government_unassigned_funding_trn"]+(gov_delta if modified else 0.),
                          F1_plus_partial_insurer_ABC_funding_residual_trn="N/A" if mode == "F0" else
                          m["insurer_unassigned_funding_trn"]+(insurer_delta if modified else 0.),
                          synthetic_household_reference="NATIVE_STAGE4_FIXED_PRICE",
                          synthetic_median_cash_real_2026_yen=hh["cash_median_real_2026_yen"],
                          synthetic_equiv_cash_gini=hh["synthetic_cash_gini"],
                          fixed_basket_VAT_at_median_real_2026_yen=hh_power["VAT_price_real_2026_yen_at_cell"],
                          B_at_median_real_2026_yen=hh_power["B_value_real_2026_yen_at_cell"],
                          private_consumption_flow_delta_nominal_trn=private_flow if modified else 0.,
                          synthetic_saving_flow_delta_nominal_trn=saving if modified else 0.,
                          B_service_flow_delta_nominal_trn=flows["B_service"] if modified else 0.,
                          import_proxy_delta_nominal_trn=(1-domestic)*sum(flows.values()) if modified else 0.,
                          domestic_demand_delta_real_trn=sum(state.values()),
                          fixed_household_consumption_proxy_real_trn=m["household_consumption_real_proxy_trn"],
                          connected_household_consumption_proxy_same_A_real_trn=
                          "N/A" if diagnostic else m["household_consumption_real_proxy_trn"]+
                          sum(state[k] for k in TERMS if k != "B_service"),
                          macro_receipts_proxy_plus_identified_direct_tax_trn=
                          m["tax_diagnostic_trn"]+(totals["national"]+totals["local"] if modified else 0.),
                          fixed_tax_diagnostic_trn=m["tax_diagnostic_trn"],
                          direct_tax_increment_nominal_trn=totals["national"]+totals["local"] if modified else 0.,
                          employee_pension_increment_nominal_trn=totals["pension"] if modified else 0.,
                          A_relief_nominal_trn=m["A_relief_trn"]+(totals["A"] if modified else 0.),
                          B_used_nominal_trn=m["B_used_trn"]+(totals["B"] if modified else 0.),
                          C_paid_nominal_trn=m["C_cash_trn"]+(totals["C"] if modified else 0.),
                          VAT_model_nominal_trn=m["modeled_VAT_trn"], VAT_price_effect_nominal_trn=m["VAT_price_effect_trn"],
                          education_medical_covered_debt_trn=m["bond_end_trn"]+m["medical_policy_debt_stock_trn"],
                          national_PB="N/A", national_debt="N/A", national_CPI="N/A")
            for group in ("Q2", "Q3", "Q4"):
                for metric in ("cash_real_2026_yen", "cash_plus_VAT_fixed_basket_real_2026_yen",
                               "VAT_price_real_2026_yen", "B_value_real_2026_yen"):
                    record[group+"_"+metric] = hh[group+"_"+metric]
            for scenario, ref in comparators.items():
                for metric in ("real_gdp_trn", "nominal_gdp_trn"):
                    value = n(ref, metric)
                    record[scenario+"_"+metric] = value
                    record["F_minus_"+scenario+"_"+metric] = record[metric]-value
            close("A_to_branch_real_bridge", record["delta_real_vs_F0"],
                  record["prior_recovery_C_real_delta_trn"]+record["delta_real_vs_same_condition_F"])
            close("A_to_branch_nominal_bridge", record["delta_nominal_vs_F0"],
                  record["prior_recovery_C_nominal_at_A_price_delta_trn"]+
                  record["prior_P2_price_nominal_delta_trn"]+record["delta_nominal_vs_same_condition_F"])
            annual.append(record)
        funding.append(dict(year=year, fixed_government_ABC_unassigned_trn=m["government_unassigned_funding_trn"],
                            fixed_insurer_ABC_unassigned_trn=m["insurer_unassigned_funding_trn"],
                            fixed_education_unassigned_trn=m["education_unassigned_cash_finance_trn"],
                            fixed_medical_unassigned_trn=m["medical_unassigned_after_sources_trn"],
                            native_reference_education_medical_unassigned_trn=fiscal[year,]["covered_unassigned_cash_trn"],
                            mapped_national_income_tax_delta_trn=totals["national"],
                            mapped_local_resident_tax_delta_trn=totals["local"],
                            employee_pension_receiver_delta_trn=totals["pension"],
                            A_backfill_internal_delta_trn=totals["A"],
                            B_service_cost_delta_trn=bcost, B_admin_delta_trn=totals["admin"],
                            C_unallocated_budget_trn=cc*n(p, "C_unallocated_trn"),
                            F2_F3_government_ABC_signed_funding_delta_trn=gov_delta,
                            F2_F3_insurer_ABC_signed_funding_delta_trn=insurer_delta,
                            F2_F3_combined_ABC_signed_funding_delta_trn=gov_delta+insurer_delta,
                            F2_F3_government_ABC_signed_unassigned_trn=m["government_unassigned_funding_trn"]+gov_delta,
                            F2_F3_insurer_ABC_signed_unassigned_trn=m["insurer_unassigned_funding_trn"]+insurer_delta,
                            actual_earmark_or_cross_account_transfer="N/A", added_borrowing="N/A"))
    check("complete_years", len(annual)==120 and len(delta_rows)==300 and len(funding)==30)
    for record in annual:
        if record["series"] in states:
            matches = [r for r in delta_rows if (r["year"],r["series"]) == (record["year"],record["series"])]
            for metric in ("real", "nominal"):
                close("sequential_contribution_closure",
                      sum(r[metric+"_GDP_delta_trn"] for r in matches),
                      record["delta_"+metric+"_vs_same_condition_F"])
    close("fixed_2055_median_yen", n(fixed[2055,"FIXED_F"],"cash_median_real_2026_yen"), 4238340, 5.)
    close("integrated_2055_median_yen", n(fixed[2055,"INTEGRATED"],"cash_median_real_2026_yen"), 4249980, 5.)
    dump("Annual.csv", annual)
    dump("Key_Years.csv", [r for r in annual if r["year"] in KEYS])
    dump("Contributions.csv", delta_rows)
    dump("Funding_Residual.csv", funding)
    save(out / "Dependencies.json", list(sources.values()))
    save(out / "Validation.json", dict(status="PASS", new_checks=sum(checks.values()),
                                       groups=dict(sorted(checks.items())), new_rows=90,
                                       reused_F0_rows=30, prior_PASS_count_included=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        run(args.root.resolve(), args.outdir, temporary / "first")
        second = temporary / "second"
        run(args.root.resolve(), second, temporary / "replay")
        files = sorted(x.name for x in second.iterdir())
        for name in files:
            if (second / name).read_bytes() != (args.outdir / name).read_bytes():
                raise ValueError(f"Re-execution differs: {name}")
    validation = args.outdir / "Validation.json"
    data = json.loads(validation.read_bytes())
    data["re_execution_byte_identical"] = files
    save(validation, data)
