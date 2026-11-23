"""Replay household incidence from pinned inputs. Run.py RUNTIME REPLAY OUTPUT."""
import importlib.util
import sys
import zlib
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "chatgpt-f-income-calibration-20261123/implementation"
spec = importlib.util.spec_from_file_location("calibration", SOURCE / "Run.py")
calibration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calibration)
prior = calibration.prior
CASES = (*calibration.CASES, "INTEGRATED", "INTEGRATED_GROSS")
FIELDS = ("A_yen", "B_used_yen", "C_cash_yen")
TRN = 1e12


def unpack(value):
    import hashlib
    data = zlib.decompress(base64.b64decode(value["zlib_base64"]))
    assert (len(data), hashlib.sha256(data).hexdigest()) == (value["size"], value["sha256"])
    code = {"__name__": "fixed_embedded"}
    exec(compile(data, "fixed_embedded.py", "exec"), code)
    return code


def total(rows, key):
    return sum(row["households"] * row[key] for row in rows)


def distribute_c(budget, rows):
    weight = total([r for r in rows if r["C_eligible"]], "consumption_yen")
    payments = [budget * TRN * r["consumption_yen"] / weight if weight and r["C_eligible"] else 0.
                for r in rows]
    return payments, 0. if weight else budget


def write(out, name, rows):
    out.mkdir(parents=True, exist_ok=True)
    (out / name).write_bytes(prior.render(rows))


def calculate(runtime, replay, out):
    check = prior.Checks()
    vat = prior.load(runtime / "handoff/f-vat-core-20261120/Inputs.json")
    household = vat["household_inputs"]
    settings = household["defaults"]
    stats = household["stats"]
    embedded = unpack(vat["household_model"])
    pension_model = unpack(household["pension_model"])
    income_tax = pension_model["income_tax"]
    config = prior.load(calibration.EVIDENCE / "Inputs.json")
    thresholds = config["nominal_household_thresholds"]
    rates = config["burden_sensitivity"]
    shares = calibration.load_shares(calibration.EVIDENCE / "Wage_Shares.csv")
    baseline, _ = calibration.results(replay, prior.Checks())
    assert baseline == (SOURCE / "Annual.csv").read_bytes()
    check("prior_150_rows_byte_match", True, True)
    previous = {(int(r["year"]), r["case"]): r for r in prior.csv_rows(baseline)}
    grid = prior.load(replay / "Household_Cells.json")
    ledger, cells, all_rows = [], [], []
    check("C_no_eligible_capacity", distribute_c(1., [dict(C_eligible=False)]), ([0.], 1.))
    for gross, expected in ((1999999, .35), (2000000, .35), (3500000, .175),
                            (5000000, 0.), (5000001, 0.)):
        check("A_exact_boundary", embedded["reduction"](gross, .35, settings, 1.), expected)
    for year, macro in zip(range(2026, 2056), prior.load(replay / "F_Actual_Annual.json"), strict=True):
        original = grid[str(year)]
        scale = macro["common_deflator"] / (600 / 580)
        budget = macro["C_cash_trn"]
        active = embedded["phase"](year, settings)
        pool = macro["household_wage_allocation_trn"] if year > 2026 else 0.
        check("year", macro["year"], year)
        for field in ("C_earmarked_funding_trn", "fund_relief_trn", "fund_income_trn"):
            check("fixed_funding_partition", macro[field], 0.)
        check("fixed_f_budget", budget, macro["C_requested_trn"])
        check("fixed_contribution_backfill", macro["government_backfill_trn"], macro["A_relief_trn"])
        equivalent = {
            q: embedded["equivalent_taxable"](stats["income_tax_mean_paid_yen"][q] * original[0]["idx"], year, pension_model)
            for q in range(5)
        }

        def relief(r, gross):
            return r["premium_target_yen"] * embedded["reduction"](
                gross, macro["maximum_relief_rate"], settings, 1.) * active

        def released_tax(r, a):
            q = r["quintile"]
            base = equivalent[q]
            coverage = r["coverage"]
            released = (income_tax(base + a / coverage, year) - income_tax(base, year)) if coverage else 0.
            return (coverage * released * stats["income_tax_paid_per2000"][q] / 2000,
                    a * .1 * stats["local_tax_paid_per2000"][q] / 2000)

        for r in original:
            check("original_A_taper", relief(r, r["gross_income_yen"]), r["A_yen"])
            check("original_deduction_tax", released_tax(r, r["A_yen"])[0], r["tax_increase_yen"])
            check("original_deduction_local", released_tax(r, r["A_yen"])[1], r["local_tax_increase_yen"])
            check("original_B_utilization", r["B_used_yen"], r["B_face_yen"] * settings["B_utilization"]
                  * settings["B_supply_capacity"] * (1 - settings["B_existing_overlap"]))
        eligible = sum(r["households"] * r["consumption_yen"] for r in original
                       if r["gross_income_yen"] <= thresholds["C"])
        for r in original:
            target = budget * TRN * r["consumption_yen"] / eligible if r["gross_income_yen"] <= thresholds["C"] else 0.
            check("original_C_consumption_weights", target, r["C_cash_yen"])

        for case in CASES:
            combined = case.startswith("INTEGRATED")
            burden = combined or case == "OBSERVED_SHARE_BURDEN"
            observed = case.startswith("OBSERVED") or case == "INTEGRATED"
            bases = []
            for r in original:
                gross = r["gross_income_yen"]
                basis = gross if r["profile"] in prior.EMPLOYEE else 0.
                if observed and r["profile"] == "EMP_CHILD":
                    basis *= next(share for limit, share in shares if gross / r["idx"] <= limit)
                bases.append(basis)
            denom = sum(r["households"] * basis for r, basis in zip(original, bases))
            rows = []
            for r, basis in zip(original, bases):
                wage = pool * TRN * basis / denom if case != "FIXED_F" else 0.
                gross = r["gross_income_yen"] + wage
                rows.append(dict(r, wage=wage, adjusted_gross=gross,
                                 **{f"{k}_eligible": int(gross <= t) for k, t in thresholds.items()},
                                 **{f"{k}_exit": int(r["gross_income_yen"] <= t < gross) for k, t in thresholds.items()},
                                 **{f"{k}_enter": int(gross <= t < r["gross_income_yen"]) for k, t in thresholds.items()}))
            eligible_rows = [r for r in rows if r["C_eligible"]]
            payments, unpaid = distribute_c(budget, rows)
            for r, payment in zip(rows, payments):
                orig_a, orig_b, orig_c = (r[f] for f in FIELDS)
                pension = r["wage"] * rates["employee_pension_rate_continuous"] if burden else 0.
                taxable = (r["wage"] - pension) * rates["illustrative_taxable_share_of_wage_after_pension"]
                national = taxable * rates["illustrative_national_income_tax_rate"] if burden else 0.
                local = taxable * rates["illustrative_resident_tax_rate"] if burden else 0.
                a, b, c = orig_a, orig_b, orig_c
                a_tax, a_local = r["tax_increase_yen"], r["local_tax_increase_yen"]
                if combined:
                    a = relief(r, r["adjusted_gross"])
                    b = orig_b * r["B_eligible"]
                    c = payment
                    a_tax, a_local = released_tax(r, a)
                elif case == "OBSERVED_THRESHOLD":
                    a, b, c = (value * (1 - r[f"{key}_exit"]) for key, value in zip(thresholds, (a, b, c)))
                net = r["wage"] - pension - national - local
                cash = (r["cash_DI_after_yen"] + net + (a - orig_a) + (c - orig_c)
                        - (a_tax - r["tax_increase_yen"]) - (a_local - r["local_tax_increase_yen"]))
                if combined:
                    check("cash_identity", cash, r["baseline_DI_yen"] + net + a + c - a_tax - a_local)
                    check("A_cap_and_threshold", 0 <= a <= r["premium_target_yen"] * macro["maximum_relief_rate"]
                          and (not a or r["A_eligible"]), True)
                    check("C_and_B_bounds", c >= 0 and (not c or r["C_eligible"]) and
                          (not b or r["B_eligible"]), True)
                    check("cell_premium_balance", r["premium_before_yen"] + pension >= a, True)
                r.update(A_yen=a, B_used_yen=b, C_cash_yen=c, cash=cash, resources=cash+b,
                         net=net, pension=pension, income_tax=national, resident_tax=local,
                         A_income_tax=a_tax, A_resident_tax=a_local, orig_A=orig_a, orig_C=orig_c,
                         net_benefit=a + c - a_tax - a_local - national - local - pension,
                         delta_cash=cash-r["cash_DI_after_yen"], premium_paid=r["premium_before_yen"]+pension-a)
            if combined:
                trn = lambda key: total(rows, key) / TRN
                paid = trn("C_cash_yen")
                check("C_budget_closed", paid+unpaid, budget)
                check("wage_pool_closed", trn("wage"), pool)
                check("marginal_payees_closed", trn("net")+trn("pension")+trn("income_tax")+trn("resident_tax"), pool)
                check("premium_payee_closed", trn("premium_paid")+trn("A_yen")-trn("pension"), macro["premium_before_trn"])
                retained = sum(r["orig_C"] * r["households"] for r in eligible_rows) / TRN
                check("C_reallocation_closed", paid-retained, budget-retained-unpaid)
                for label, threshold in thresholds.items():
                    before = sum(r["households"] for r in original if r["gross_income_yen"] <= threshold)
                    check("threshold_entry_exit", total(rows, label+"_eligible"),
                          before + total(rows, label+"_enter") - total(rows, label+"_exit"))
                ledger.append(dict(year=year,case=case,C_budget_trn=budget,C_paid_trn=paid,C_unallocated_trn=unpaid,
                                   C_retained_before_redistribution_trn=retained,C_redistributed_trn=paid-retained,
                                   C_VAT_earmark_trn=0.,fund_draw_trn=0.,A_fixed_trn=macro["A_relief_trn"],
                                   A_recalculated_trn=trn("A_yen"),A_government_backfill_trn=trn("A_yen"),
                                   A_insurer_loss_trn=trn("A_yen"),A_reserve_trn=0.,
                                   insurer_employee_premiums_trn=trn("premium_paid"),
                                   **{k+"_trn":trn(k) for k in ("wage","net","pension","income_tax","resident_tax",
                                                               "A_income_tax","A_resident_tax")},
                                   **{f"{label}_{event}_households":total(rows,f"{label}_{event}")
                                      for label in thresholds for event in ("eligible","enter","exit")}))
                if case == "INTEGRATED":
                    fields = ("profile","quintile","households","gross_income_yen","adjusted_gross","orig_A","A_yen",
                              "orig_C","C_cash_yen","A_income_tax","A_resident_tax","wage","pension","income_tax","resident_tax",
                              "premium_paid","cash","B_used_yen","A_exit","B_exit","C_exit")
                    cells.extend(dict(year=year,cell=r["id"],**{k:r[k] for k in fields}) for r in rows)
            else:
                old = previous[year,case]
                rank, median = prior.median(rows,"cash")
                check("prior_case_median", median["cash"], float(old["cash_median_nominal_yen"]))
                check("prior_case_rank", (median["id"],rank), (old["post_median_cell"],int(old["post_median_rank"])))
                check("prior_case_gini", prior.gini(rows,"cash"), float(old["synthetic_gini_cash"]))
            all_rows.append((year,case,rows,scale,macro))
    write(out,"Annual.csv",ledger)
    write(out,"Cells.csv",cells)
    check.save(out)
    return all_rows


if __name__ == "__main__":
    calculate(*map(Path, sys.argv[1:]))
