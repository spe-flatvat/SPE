#!/usr/bin/env python3
"""SQ fiscal baseline. Python 3.10+, Git, and the pinned upstream SPE objects."""
import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
import sys
import tempfile
from xml.etree import ElementTree
from zipfile import ZipFile
from collections import Counter
from pathlib import Path

from Runtime import (Entry, EXTERNAL, SECTORS, account, annual_stocks, build_ledger,
                     consolidate, interest_on_opening, stock_flow)

H = "handoff/chatgpt-"
REQUEST = "25af48f0c697d06bf5243e497b3a44d2b69d6a08"
DYNAMIC = "586cceb2a86c66265237a3616b92dc78f506c786"
BASE = "7dd893eeed781af2bb323c424b456fdd907a667f"
STATS = "747273674daed0d648c58aa8fdc07ebe203e6046"
DYN_DIR = H + "common-risk-dynamic-20261125/"
BASE_DIR = H + "sq-baseline-contract-three-scenario-recalculation-20261123/"
STAT_DIR = H + "national-fiscal-closure-20261121/"
YEARS = range(2026, 2056)
KEY = {2026, 2030, 2035, 2043, 2045, 2055}
SCOPES = (*SECTORS, "GENERAL_GOVERNMENT", "CENTRAL_LOCAL")
MED = ("baseline_medical_bill_trn", "baseline_patient_model_trn",
       "baseline_insurance_and_public_model_trn", "clinical_cost_delta_trn",
       "government_cost_delta_trn", "insurer_balance_delta_trn",
       "medical_unassigned_direct_cash_requirement_trn", "medical_unassigned_after_sources_trn",
       "government_insurer_transfer_delta_trn", "medical_policy_interest_trn")


def number(value):
    return None if value in ("", "N/A", None) else float(value)


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def dump(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n", restval="N/A")
        writer.writeheader()
        writer.writerows({k: "N/A" if v is None else v for k, v in row.items()} for row in rows)


def fingerprint(data):
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


class Sources:
    def __init__(self, root):
        self.root = root
        self.dependencies = {}
        self.checks = Counter()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args])

    def require(self, label, condition):
        if not condition:
            raise ValueError(f"{label} failed after {self.checks[label]} matching checks")
        self.checks[label] += 1

    def near(self, label, value, expected):
        self.require(label, math.isclose(value, expected, abs_tol=3e-7, rel_tol=2e-11))

    def raw(self, ref, path):
        data = self.git("show", f"{ref}:{path}")
        self.dependencies[ref, path] = dict(commit=ref, path=path, **fingerprint(data))
        return data

    def js(self, ref, path):
        return json.loads(self.raw(ref, path))

    def csv(self, ref, path):
        return list(csv.DictReader(io.StringIO(self.raw(ref, path).decode("utf-8-sig"))))


def capture_medical(src, macro, out, draft_override):
    runtime_path = src.root / DYN_DIR / "Runtime.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("fixed_dynamic_runtime", runtime_path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    draft_root = out / "draft"
    draft = draft_root / engine.DRAFT
    draft.parent.mkdir(parents=True)
    if draft_override is None:
        data = src.raw(engine.DRAFT_PIN, engine.DRAFT)
    else:
        data = draft_override.read_bytes()
        src.dependencies[engine.DRAFT_PIN, engine.DRAFT] = dict(
            commit=engine.DRAFT_PIN, path=engine.DRAFT, **fingerprint(data))
    expected = next(r for r in src.js(DYNAMIC, DYN_DIR + "Dependencies.json")["inputs"]
                    if r["commit"] == engine.DRAFT_PIN and r["path"] == engine.DRAFT)
    src.require("medical_draft_fixed_bytes",
                fingerprint(data) == dict(bytes=expected["bytes"], sha256=expected["sha256"]))
    draft.write_bytes(data)
    params = [macro[c, y] for c in "CD" for y in YEARS]
    result = {}
    for mode in "ACD":
        rows = [r for r in params if r["condition"] == mode]
        job = out / mode
        job.mkdir()
        save(job / "inputs.json", dict(mode=mode, draft=str(draft_root),
                                       factors=[float(r["risk_factor"]) for r in rows],
                                       prices=[float(r["price_coefficient"]) for r in rows]))
        subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--root", str(src.root),
                        "--outdir", str(job), "--medical-worker"], check=True)
        for r in json.loads((job / "sq.json").read_bytes()):
            y = r["year"]
            fixed = macro[mode, y]
            src.near("medical_capture_real", r["Y"], float(fixed["real_gdp_trn"]))
            src.near("medical_capture_nominal", r["N"], float(fixed["nominal_gdp_trn"]))
            src.near("medical_capture_population", r["demography"]["population"], float(fixed["population"]))
            src.near("medical_capture_internal_transfer", r["medical"]["internal_transfer_consolidated_delta_trn"], 0)
            result[mode, y] = r
    return result



def medical_worker(root, out):
    # Capture the same common-medical inputs using the fixed adapters.
    sys.path.insert(0, str(root / DYN_DIR))
    import importlib.util
    runtime_path = root / DYN_DIR / "Runtime.py"
    spec = importlib.util.spec_from_file_location("fixed_dynamic_runtime", runtime_path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    job = json.loads((out / "inputs.json").read_bytes())
    if job["mode"] == "A":
        engine.adapt = lambda source, factors, prices: source
        previous = engine.replace
        engine.replace = lambda source, old, new: (source if old == "w=_medical.step(y,rows)"
                                                   else previous(source, old, new))
    data, sq, _ = engine.run_common(root, out, Path(job["draft"]), job["factors"], job["prices"])
    save(out / "sq.json", [r for r in data["records"] if r["case"] == sq])

def fiscal_reference(rows, src):
    result = {}
    for scope, prefix in [("CENTRAL", "central"), ("LOCAL", "local"), ("CENTRAL_LOCAL", "CL")]:
        opening = float(rows[2025][prefix + "_debt_end_trn"])
        for year in range(2026, 2041):
            row = rows[year]
            pb, balance, closing = (float(row[prefix + "_" + k + "_trn"])
                                    for k in ("PB", "balance", "debt_end"))
            interest = pb - balance
            unexplained = closing - opening + balance
            src.near("official_stock_flow_residual_identity", opening - balance + unexplained, closing)
            result[scope, year] = dict(reference_pb=pb, reference_balance=balance,
                                       reference_net_interest=interest, reference_debt_begin=opening,
                                       reference_debt_end=closing,
                                       reference_implied_stock_balance_residual=unexplained,
                                       reference_deficit=max(0, -balance),
                                       source_nominal_gdp=float(row["official_nominal_GDP_trn"]))
            opening = closing
    return result



def historical_stocks(data):
    """Read numeric cells of the pinned one-sheet SNA supplementary table 3."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(io.BytesIO(data)) as book:
        xml = ElementTree.fromstring(book.read("xl/worksheets/sheet1.xml"))
    values = {cell.attrib["r"]: cell.find("m:v", ns).text
              for cell in xml.findall(".//m:c", ns) if cell.find("m:v", ns) is not None
              and cell.attrib.get("t") not in ("s", "inlineStr")}
    return [
        dict(year=2024, time_basis="CALENDAR_YEAR_END", scope=scope, metric=metric,
             cell=col + str(row), raw_billion_yen=float(values[col + str(row)]),
             amount_trn=float(values[col + str(row)])/1000, status="SNA_HISTORICAL_UNCONSOLIDATED")
        for scope, col in zip((*SECTORS, "GENERAL_GOVERNMENT_UNCONSOLIDATED"), ("DR", "DS", "DT", "DU"))
        for metric, row in (("financial_assets", 14), ("cash_deposits", 16),
                            ("financial_liabilities", 27), ("loans_borrowing", 30))
    ]

def synthetic(src):
    def entry(id, holder, category, party, side, amount, coverage):
        return Entry(id, 2026, holder, category, party, side, amount, "synthetic", coverage)

    central, local, ssf = SECTORS
    tax = entry("tax", central, "income_tax", EXTERNAL, "in", 10, "tax-base")
    entries = [tax]
    for category, amount in (("transfer", 2), ("interest", 0.5), ("internal_stock", 3)):
        entries += [entry(category + "-out", central, category, local, "out", amount, category),
                    entry(category + "-in", local, category, central, "in", amount, category)]
    external, audit = consolidate(build_ledger(entries), 2026)
    src.require("synthetic_consolidation", external == [tax] and
                [r["eliminated"] for r in audit] == [2, 0.5, 3])
    _, incomplete = consolidate(entries[:-1], 2026)
    src.require("synthetic_missing_leg", incomplete[-1]["unmatched"] == 3)
    _, mismatched = consolidate(entries[:-1] + [entry("stock-in", local, "internal_stock",
                                                     central, "in", 2, "internal_stock")], 2026)
    src.require("synthetic_mismatched_legs", mismatched[-1]["status"] == "UNRESOLVED"
                and mismatched[-1]["unmatched"] == 1)
    for duplicate in (tax, entry("alt", central, "other_revenue", EXTERNAL, "in", 10, "tax-base")):
        try:
            build_ledger(entries, [("add", duplicate)])
        except ValueError:
            src.require("synthetic_double_count_rejected", True)
        else:
            raise ValueError("Duplicate coverage accepted")
    for op, amount, expected in (("delta", -3, 7), ("replace", 11, 11), ("replace", None, None)):
        edit = entry("tax", central, "income_tax", EXTERNAL, "in", amount, "tax-base")
        src.require("synthetic_SQ_overlay", build_ledger(entries, [(op, edit)])[0].amount == expected)
    complete = {(kind, side) for kind in ("income_tax", "corporate_tax", "consumption_tax", "other_tax",
                                           "social_contributions", "other_revenue", "cash_benefits",
                                           "medical", "education", "other_consumption", "capital_formation",
                                           "other_primary_expense", "transfer", "interest")
                for side in ("in", "out")}
    rec, _ = account(entries, 2026, SECTORS, complete)
    src.require("synthetic_PB_balance", rec["pb"] == 10 and rec["balance"] == 10)
    rec, _ = account(entries, 2026, SECTORS)
    src.require("synthetic_NA", rec["pb"] is None and rec["funding_shortfall"] is None)
    stocks = annual_stocks(100, 5, 3, 1, 20, 2, 1, -1)
    src.require("synthetic_stock_flow", stocks == dict(debt_end=103, assets_end=20, net_debt=83))
    carried = annual_stocks(stocks["debt_end"], 1, 2, 0, stocks["assets_end"], 0, 1, 0)
    src.require("synthetic_stock_carry", carried == dict(debt_end=102, assets_end=19, net_debt=83))
    src.require("synthetic_missing_SFA", annual_stocks(100, 0, 0, None, 2, 0, 0, 0)["debt_end"] is None)
    src.require("synthetic_opening_interest", interest_on_opening(100, .02, 20, .01) == (2, .2))
    financial = {("issuance", "in"), ("redemption", "out"),
                 ("acquisition", "out"), ("disposal", "in")}
    rec, _ = account(entries, 2026, SECTORS, complete | financial, cash_operating_balance=-5)
    src.require("synthetic_cash_shortfall", rec["cash_balance"] == -5 and rec["funding_shortfall"] == 5)


def run(root, out, work, draft_override):
    src = Sources(root)
    synthetic(src)
    # Runtime opens pinned tracked files, so validate its checkout before executing.
    head = src.git("rev-parse", "HEAD").decode().strip()
    src.require("approved_ancestor", subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", REQUEST, head]).returncode == 0)
    tracked = src.git("diff", "--name-only", REQUEST, "--", ".", ":(exclude)" + H + "sq-common-fiscal-20261126/")
    src.require("fixed_upstream_checkout", not tracked)
    for p in ("policies/StatusQuo.md", "specifications/SimulationSpecification_v6.md",
              "specifications/SimulationSpecification_v6_Annex.md"):
        src.raw(REQUEST, p)
    for p in ("Runtime.py", "Run.py", "Report.md", "Dependencies.json", "Fiscal_Residual.csv",
              "Connection_Status.csv", "Recovery_Events.csv", "Validation.json"):
        src.raw(DYNAMIC, DYN_DIR + p)
    macro = {(r["condition"], int(r["year"])): r
             for r in src.csv(DYNAMIC, DYN_DIR + "Annual.csv") if r["case"] == "SQ"}
    custody = src.js(DYNAMIC, DYN_DIR + "Custody.json")
    for item in custody["files"]:
        identity = src.dependencies.get((DYNAMIC, item["path"]))
        if identity:
            src.require("fixed_dynamic_byte_match",
                        (identity["bytes"], identity["sha256"]) == (item["bytes"], item["sha256"]))
    events = src.csv(DYNAMIC, DYN_DIR + "Recovery_Events.csv")
    starts = {r["event"]: min(int(x["start"]) for x in events if x["event"] == r["event"]) for r in events}
    src.require("fixed_event_boundary", starts == dict(conflict=2027, earthquake=2031, disaster=2029, climate=2028))
    trace = src.js(BASE, BASE_DIR + "BASE_REPLAY/Common_Trace_BASE_REPLAY.json")
    fixed_a = {int(r["year"]): r for r in src.csv(BASE, BASE_DIR + "SQ_Baseline_2026_2055.csv")}
    existing = {int(r["year"]): r for r in src.csv(STATS, STAT_DIR + "Official_Fiscal_Baseline_2025_2040.csv")}
    historical = src.csv(STATS, STAT_DIR + "SNA2024_Sector_Snapshot.csv")
    stocks_2024 = historical_stocks(src.raw(STATS, STAT_DIR + "SNA2024_Sector_Stocks.xlsx"))
    source_reports = src.js(STATS, STAT_DIR + "Statistical_Source_Receipts.json")
    cell_map = src.csv(STATS, STAT_DIR + "Statistical_Cell_Map.csv")
    prior = src.js(STATS, STAT_DIR + "Checks.json")
    for item in source_reports:
        observed = fingerprint(src.raw(STATS, STAT_DIR + item["file"]))
        src.require("official_original_byte_match", observed == dict(bytes=item["size"], sha256=item["sha256"]))
    for commit, directory, name in [
        ("8a8edb403b960cceb535f9b70461646e9374c229", "f-sq-n3-common-indicators-20261123", "Annual_Comparison.csv"),
        ("2d8cb85878c931d9d127755af6d2eb336c04c04d", "common-price-nominal-real-20261125", "Dependencies.json"),
        ("3d3507e2df9218a6bbda587e9b8b0c0d423ae2ac", "f-latest-integration-20261125", "Report.md"),
        ("08d9bddce5bf310e7caf107f70ddf363c341dfa7", "n3-redemption-allocation-20261125", "Report.md"),
        ("f3fc96fce3195a02f4e1f96d94e4574963f6ea57", "n3-central-local-funding-accounts-20261122", "Transfer_Consolidation_Algebra.csv"),
        ("c087a1a5af12b86cdb140d934754d75e5ee9c4ef", "n3-financing-authority-feasibility-20261123", "N3_Central_Local_Financing_Legal_Authority_Map.csv"),
    ]:
        src.raw(commit, H + directory + "/" + name)
    source_ref = fiscal_reference(existing, src)
    medical = capture_medical(src, macro, work, draft_override)
    src.require("coverage", len(macro) == len(medical) == 90)
    annual, consolidated, residual, diagnostics = [], [], [], []
    a_tax, a_med = {}, {}
    for mode in "ACD":
        previous_stocks = {scope: dict(debt_end=None, assets_end=None) for scope in SCOPES}
        last_tax = 80.0
        last_nominal = 600.0
        for year in YEARS:
            r = macro[mode, year]
            m = medical[mode, year]
            nominal, real, pop = (float(r[k]) for k in ("nominal_gdp_trn", "real_gdp_trn", "population"))
            if year == 2026:
                src.require("fixed_initial", (real, nominal, pop) == (580, 600, 122618024))
            else:
                params = trace["parameters"]
                last_tax = min(last_tax * (1 + (nominal / last_nominal - 1) * params["elasticity"])
                               * (params["quake_tax_factor"] if year == 2031 else 1),
                               nominal * params["tax_cap_ratio"])
            src.near("recursive_tax_base", last_tax, m["tax"])
            tax = last_tax + m["direct"]
            src.near("fixed_tax_proxy", tax, float(fixed_a[year]["tax_diagnostic_proxy_trn"])
                     if mode == "A" else float(r["tax_diagnostic_trn"]))
            last_nominal = nominal
            w = m["medical"]
            if mode == "A":
                a_tax[year] = tax
                a_med[year] = w["government_cost_delta_trn"]
            tax_delta = tax - a_tax[year]
            med_delta = w["government_cost_delta_trn"] - a_med[year]
            # No calibrated tax or medical incidence bridge. These remain
            # diagnostics outside the sector ledger, and only tax is stressed.
            diagnostics.append(dict(condition=mode, year=year, sq_macro_tax_proxy=last_tax,
                                    sq_direct_tax_adjustment=m["direct"], sq_tax_proxy=tax,
                                    sq_tax_delta_vs_A=tax_delta, sq_tax_pct_GDP=100*tax/nominal,
                                    modeled_government_medical_delta_vs_A=med_delta,
                                    model_labor=m["labor"], nominal_gdp=nominal,
                                    real_gdp=real, population=pop, model_deflator=r["deflator_index"],
                                    **{k: w[k] for k in MED}))
            for scope in SCOPES:
                members = SECTORS if scope == "GENERAL_GOVERNMENT" else (
                    SECTORS[:2] if scope == "CENTRAL_LOCAL" else (scope,))
                row, audit = account((), year, members)
                src.require("unknown_coverage_propagation",
                            all(row[k] is None for k in ("pb", "balance", "revenue", "expenditure",
                                                        "cash_balance", "funding_shortfall")))
                previous = previous_stocks[scope]
                row.update(annual_stocks(previous["debt_end"], row["issuance"], row["redemption"], None,
                                         previous["assets_end"], row["asset_acquisitions"], row["asset_disposals"], None))
                previous_stocks[scope] = row
                row.update(debt_begin=previous["debt_end"], assets_begin=previous["assets_end"])
                for category in ("income_tax", "corporate_tax", "consumption_tax", "other_tax",
                                 "social_contributions", "other_revenue", "cash_benefits", "medical",
                                 "education", "other_consumption", "capital_formation", "other_primary_expense",
                                 "transfer_received", "transfer_paid"):
                    row[category] = None
                reference = source_ref.get((scope, year), {})
                for field in ("reference_pb", "reference_balance", "reference_net_interest",
                              "reference_debt_begin", "reference_debt_end",
                              "reference_implied_stock_balance_residual", "reference_deficit",
                              "source_nominal_gdp"):
                    row[field] = reference.get(field)
                row.update(rollover=None, debt_sfa=None, asset_sfa=None)
                for label in ("0p5", "1p0"):
                    weight = .5 if label == "0p5" else 1
                    pb = reference["reference_pb"] + tax_delta*weight if reference and scope == "CENTRAL_LOCAL" else None
                    bal = stock_flow(pb, 0, row["reference_net_interest"], 0)
                    row.update({f"CL_tax_sensitivity_PB_{label}": pb,
                                f"CL_tax_sensitivity_balance_{label}": bal,
                                f"CL_tax_sensitivity_deficit_{label}": None if bal is None else max(0, -bal)})
                    if bal is not None:
                        src.near("CL_sensitivity_PB_interest_balance", pb - row["reference_net_interest"], bal)
                for field, val in tuple(row.items()):
                    if field in ("pb", "balance", "revenue", "expenditure", "debt_end", "assets_end",
                                 "net_debt", "interest_paid", "interest_received", "funding_shortfall") or field.startswith(
                                 ("reference_", "CL_tax_sensitivity_")):
                        row[field + "_pct_SPE_GDP"] = None if val is None else 100*val/nominal
                annual.append(dict(condition=mode, year=year, scope=scope, nominal_gdp=nominal,
                                   time_basis="SPE_YEAR; reference=Japan_FY_label", unit="JPY_TRILLION_NOMINAL",
                                   case_status="FIXED_A" if mode == "A" else "P2_NON_ADOPTED", **row))
                residual.append(dict(condition=mode, year=year, scope=scope,
                                     transfer_counterparty_residual=None,
                                     reference_debt_stock_balance_residual=row["reference_implied_stock_balance_residual"],
                                     medical_model_unassigned_pre_sources=w["medical_unassigned_direct_cash_requirement_trn"]
                                     if scope == "GENERAL_GOVERNMENT" else None,
                                     medical_model_allocation="UNASSIGNED_GOVERNMENT_AND_INSURER"
                                     if scope == "GENERAL_GOVERNMENT" else "N/A",
                                     cash_funding_shortfall=None,
                                     cause="MISSING_SAME_BOUNDARY_LEDGER_AND_FINANCING" if reference
                                     else "MISSING_SAME_BOUNDARY_FORWARD_SOURCE"))
                if scope in ("GENERAL_GOVERNMENT", "CENTRAL_LOCAL"):
                    for category in ("transfer", "interest", "internal_stock"):
                        consolidated.append(dict(condition=mode, year=year, scope=scope, category=category,
                                                 matched_elimination=None, unmatched_amount=None,
                                                 status="COUNTERPARTY_MATRIX_NOT_AVAILABLE"))
    historic = {r["sector"]: r for r in historical}
    for r in historical:
        if r["sector"] == "CONSOLIDATION_ADJUSTMENT":
            continue
        val = float(r["revenue_trn"]) - float(r["expenditure_including_net_capital_trn"])
        src.require("SNA_2024_revenue_expenditure_at_source_precision",
                    abs(val - float(r["net_lending_trn"])) <= .00021)
        src.require("SNA_2024_PB_at_source_precision",
                    abs(val + float(r["interest_paid_pre_FISIM_trn"])
                        - float(r["interest_received_pre_FISIM_trn"]) - float(r["SNA_PB_trn"])) <= .00021)
    gg = historic["GENERAL_GOVERNMENT"]
    for field in ("revenue_trn", "expenditure_including_net_capital_trn", "internal_grants_received_trn",
                  "internal_grants_paid_trn", "net_lending_trn"):
        members = (*SECTORS, "CONSOLIDATION_ADJUSTMENT")
        src.require("SNA_2024_published_consolidation_at_source_precision",
                    abs(sum(float(historic[s][field]) for s in members) - float(gg[field])) <= .00031)
    all_rows = {(r["condition"], r["year"], r["scope"]): r for r in annual}
    for r in annual:
        anchor = all_rows["A", r["year"], r["scope"]]
        for k in ("pb", "balance", "debt_end", "assets_end", "funding_shortfall", "CL_tax_sensitivity_PB_1p0",
                  "CL_tax_sensitivity_balance_1p0", "CL_tax_sensitivity_deficit_1p0"):
            r[k + "_delta_vs_A"] = None if r[k] is None or anchor[k] is None else r[k] - anchor[k]
    dump(out / "Annual.csv", annual)
    dump(out / "Diagnostics.csv", diagnostics)
    dump(out / "Key_Years.csv", [r for r in annual if r["year"] in KEY])
    dump(out / "Consolidation.csv", consolidated)
    dump(out / "Fiscal_Residual.csv", residual)
    dump(out / "Historical_SNA_FY2024.csv", historical)
    dump(out / "Historical_SNA_Stocks_2024.csv", stocks_2024)
    for metric in {r["metric"] for r in stocks_2024}:
        rows = [r["amount_trn"] for r in stocks_2024 if r["metric"] == metric]
        src.near("SNA_2024_unconsolidated_stock_sum", sum(rows[:3]), rows[3])
    initial = [
        dict(year=2026, scope="SPE", metric=k, amount=v, source="fixed dynamic Annual.csv", state="FIXED_MODEL")
        for k, v in (("real_GDP_trn", 580), ("nominal_GDP_trn", 600), ("population", 122618024),
                     ("tax_proxy_trn", 80), ("deflator_index", 100), ("effective_labor", medical["A", 2026]["labor"]))
    ]
    initial += [dict(year=2026, scope=s, metric=k, amount=v, source="CAO July 2026 current projection",
                     state="EXTERNAL_REFERENCE_JAPAN_FY") for s in (*SECTORS[:2], "CENTRAL_LOCAL")
                for k, v in source_ref[s, 2026].items()]
    initial += [dict(year=2026, scope=s, metric=k, amount=None, source="same-boundary inputs unavailable",
                     state="N/A") for s in SCOPES for k in ("actual_model_debt_begin", "actual_model_assets_begin",
                                                            "model_borrowing_rate", "model_asset_yield")]
    initial += [
        dict(year=2026, scope="SQ_ORIGINAL", metric="population", amount=121500000,
             source="policies/StatusQuo.md section 6", state="REFERENCE_ONLY_FIXED_MACRO_PRIORITY"),
        dict(year=2026, scope="SQ_ORIGINAL", metric="bond_issuance_trn", amount=28,
             source="policies/StatusQuo.md section 6", state="REFERENCE_ONLY_NO_GROSS_NET_SCOPE"),
        dict(year=2026, scope="SQ_ORIGINAL", metric="policy_rate_pct", amount=.75,
             source="policies/StatusQuo.md section 6", state="REFERENCE_ONLY_NO_STOCK_EFFECTIVE_RATE"),
    ]
    dump(out / "Initial_Conditions.csv", initial)
    refs = {r["file"]: r for r in source_reports}
    publications = {"CAO_202607_Projections.xlsx": "2026-07", "SNA2024_GFS.xlsx": "2025-12-23",
                    "SNA2024_Sector_Accounts.xlsx": "2025-12-23", "SNA2024_Sector_Stocks.xlsx": "2026-01-20"}
    bridge = [{**r, "url": refs[r["file"]]["url"], "publication": publications[r["file"]],
               "source_sha256": refs[r["file"]]["sha256"], "source_bytes": refs[r["file"]]["size"],
               "conversion": "source already trillion JPY" if r["file"].startswith("CAO")
               else "source billion JPY / 1000", "classification": "EXTERNAL_REFERENCE"}
              for r in cell_map]
    stock_ref = refs["SNA2024_Sector_Stocks.xlsx"]
    bridge += [dict(file=stock_ref["file"], sheet="資産・負債残高", cell=r["cell"], metric=r["metric"],
                    year=2024, raw=r["raw_billion_yen"], unit="BILLION_YEN", result=r["amount_trn"],
                    url=stock_ref["url"], publication=publications[stock_ref["file"]],
                    source_sha256=stock_ref["sha256"], source_bytes=stock_ref["size"],
                    conversion="source billion JPY / 1000", classification=r["status"]) for r in stocks_2024]
    bridge += [
        dict(year=y, metric="SPE_N_vs_official_FY_N", raw=existing[y]["official_nominal_GDP_trn"],
             unit="TRILLION_YEN", conversion="SPE_N - CAO_FY_N; no scale adjustment", condition=c,
             result=float(macro[c, y]["nominal_gdp_trn"]) - float(existing[y]["official_nominal_GDP_trn"]))
        for c in "ACD" for y in range(2026, 2041)]
    dump(out / "Source_Bridge.csv", bridge)
    save(out / "Dependencies.json", dict(inputs=list(src.dependencies.values()), official_receipts=source_reports,
                                        prior_checks_referenced=prior["status"], runtime_checkout_boundary=REQUEST))
    src.require("output_counts", len(annual) == 450 and len(consolidated) == 540 and len(residual) == 450)
    save(out / "Validation.json", dict(status="PASS_FOR_PARTIAL_EXECUTION", reused_macro_case_years=90,
                                       new_fiscal_case_years=90, fiscal_scope_rows=450,
                                       total=sum(src.checks.values()), checks=dict(sorted(src.checks.items()))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--draft-file", type=Path, help="Fixed upstream draft bytes when Git object is unavailable")
    parser.add_argument("--medical-worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    args.outdir.mkdir(exist_ok=True, parents=True)
    if args.medical_worker:
        medical_worker(args.root.resolve(), args.outdir)
        sys.exit(0)
    with tempfile.TemporaryDirectory() as folder:
        run(args.root.resolve(), args.outdir, Path(folder), args.draft_file)
