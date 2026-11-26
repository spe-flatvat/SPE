"""Reproduce the non-adopted SQ fiscal projections from locked upstream objects."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

PIN = "4a1990681b13c3806bec713f3ac0c269f5dc9565"
PREV = "a6387536959966f1e5a027286065fcb9355439e5"
DYN = "586cceb2a86c66265237a3616b92dc78f506c786"
STATS = "747273674daed0d648c58aa8fdc07ebe203e6046"
DEM = "9dcf953e949593e773bab906eb72577f0efec73e"
BASE = "7dd893eeed781af2bb323c424b456fdd907a667f"
H = "handoff/chatgpt-"
P = H + "sq-common-fiscal-20261126/"
S = H + "national-fiscal-closure-20261121/"
KEY = (2026, 2030, 2035, 2040, 2043, 2045, 2055)
YEARS = range(2026, 2056)
MODES = ("A", "C", "D")
SCOPES = ("CENTRAL", "LOCAL", "SOCIAL_SECURITY", "GENERAL_GOVERNMENT")
FLOW = dict(revenue=8, tax=9, income=11, corporate=12, vat=23, social=44,
            premium=45, transfer_in=61, interest_in=66, expense=85, payroll=86,
            supplies=93, depreciation=94, interest_out=95, transfer_out=114,
            benefits=117, ss_cash=119, ss_kind=120, net_capital=146,
            net_fixed_capital=147, balance=160)
FIN = dict(asset_transactions=8, liability_transactions=19, securities_transactions=22,
           loan_transactions=23, financial_balance=30, asset_revaluation=33,
           liability_revaluation=44, asset_volume_changes=58, liability_volume_changes=69,
           assets=83, liabilities=94, securities=97, loans=98)
TAX_KEYS = ("income_tax", "corporate_tax", "consumption_tax", "other_tax")
RECEIPTS = (*TAX_KEYS, "social_contributions", "other_revenue")
EXPENSES = ("cash_benefits", "medical", "education", "other_consumption",
            "capital_formation", "other_primary_expense")
DATA = dict(fy25_nominal=1.042, fy25_real=1.008, fy25_domestic_price=1.026,
            fy26_price_assumption=1.02, ilo24_pension=57.8528, ilo24_medical=44.8055,
            budget26_pension=63.7, budget26_medical=44.6, budget26_care=14.3,
            budget26_welfare=35.8, ilo24_premiums_rounded=83.0, budget26_premiums=84.5)
VARIANTS = ("CENTRAL_ESTIMATE", "TAX_ELASTIC_1P5", "BENEFITS_WAGE_INDEX",
            "RATE_FY2023", "FUNDING_NO_NEW_CREDIT")


class Inputs:
    def __init__(self, root):
        self.root = root
        self.receipts = {}
        self.counts = Counter()

    def verify(self, label, result):
        if not result:
            raise ValueError(label)
        self.counts[label] += 1

    def near(self, label, x, y, tol=1e-8):
        self.verify(label, abs(x-y) <= tol)

    def raw(self, commit, path):
        key = (commit, path)
        data = subprocess.check_output(["git", "-C", str(self.root), "show", commit+":"+path])
        self.receipts[key] = dict(commit=commit, path=path, bytes=len(data),
                                  sha256=hashlib.sha256(data).hexdigest())
        return data

    def csv(self, commit, path):
        return list(csv.DictReader(io.StringIO(self.raw(commit, path).decode("utf-8-sig"))))


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", encoding="utf-8", newline="") as file:
        w = csv.DictWriter(file, keys, lineterminator="\n", restval="N/A")
        w.writeheader()
        w.writerows({k: "N/A" if v is None else round(v, 9) if isinstance(v, float) else v
                     for k, v in row.items()} for row in rows)


def write_json(path, document):
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def read_gfs(inputs):
    path = S + "SNA2024_GFS.xlsx"
    workbook = load_workbook(io.BytesIO(inputs.raw(STATS, path)), data_only=True, read_only=True)
    results = defaultdict(dict)
    bridge = []
    for sheet, fields in zip(workbook, (FLOW, FIN)):
        matrix = list(sheet.values)
        for year in (2022, 2023, 2024):
            for i, scope in enumerate((*SCOPES[:3], "CONSOLIDATION", SCOPES[3])):
                column = 146 + 5*(year-2023) + i
                for term, row in fields.items():
                    raw = matrix[row-1][column]
                    inputs.verify("numeric_GFS_input", isinstance(raw, (float, int)))
                    value = raw/1000
                    results[year, scope][term] = value
                    bridge.append(dict(source="CAO_SNA_GFS", year=year, scope=scope, variable=term,
                                       cell=get_column_letter(column+1)+str(row), table=sheet.title,
                                       raw=raw, unit="billion_yen", amount_trn=value,
                                       conversion="raw / 1000", path=path))
    workbook.close()
    return results, bridge


def read_macros(inputs):
    diagnostics = {(r["condition"], int(r["year"])): r for r in inputs.csv(PREV, P+"Diagnostics.csv")}
    dynamic = {(r["condition"], int(r["year"])): r for r in inputs.csv(
        DYN, H+"common-risk-dynamic-20261125/Annual.csv") if r["case"] == "SQ"}
    a = {int(r["year"]): r for r in inputs.csv(
        BASE, H+"sq-baseline-contract-three-scenario-recalculation-20261123/SQ_Baseline_2026_2055.csv")}
    age = defaultdict(lambda: defaultdict(float))
    for r in inputs.csv(DEM, H+"common-macro-demography-labor-productivity-diagnostic-20261123/"
                        "SQ_Age_Sex_Employment_Cells_2026_2055.csv"):
        y, lower, persons = int(r["year"]), int(r["age_lower"]), float(r["persons"])
        age[y]["population"] += persons
        for group, ok in (("65", lower>=65), ("75", lower>=75), ("child", lower<20)):
            if ok:
                age[y][group] += persons
    output = {}
    for mode,y in diagnostics:
        d, dyn = diagnostics[mode,y], dynamic[mode,y]
        for col in ("nominal_gdp", "real_gdp", "population"):
            key = col if col=="population" else col+"_trn"
            inputs.near("fixed_macro_unchanged", float(d[col]), float(dyn[key]))
        n, real, pop, deflator, labor = (float(d[k]) for k in
            ("nominal_gdp", "real_gdp", "population", "model_deflator", "model_labor"))
        inputs.near("fixed_age_cells_cover_used_population", age[y]["population"], pop, .01)
        consumption = float(a[y]["consumption_real_proxy_trn"] if mode=="A"
                            else dyn["household_consumption_proxy_real_trn"]) * deflator/100
        wages = n/labor
        household_resource = float(a[y]["household_resource_proxy_trn"] if mode=="A"
                                   else dyn["household_nominal_income_resource_proxy_trn"])
        z = dict(n=n, real=real, population=pop, prices=deflator/100, labor=labor,
                 consumption=consumption, wage=wages, household_resource=household_resource, medical=float(d["baseline_insurance_and_public_model_trn"]),
                 medical_unallocated=float(d["medical_unassigned_direct_cash_requirement_trn"]),
                 **{"age"+g: pop*age[y][g]/age[y]["population"] for g in ("65","75","child")})
        output[mode,y] = z
    return output, diagnostics


def benchmark(gfs, public):
    p = DATA
    growth26 = float(public[2026]["official_nominal_GDP_trn"])/float(public[2025]["official_nominal_GDP_trn"])
    prices = p["fy25_domestic_price"]*p["fy26_price_assumption"]
    income = p["fy25_real"]*prices
    nominal = p["fy25_nominal"]*growth26
    initial, bridge = {}, []
    for s in SCOPES[:3]:
        r = gfs[2024,s]
        pension, kind = (p["ilo24_pension"], r["ss_kind"]) if s=="SOCIAL_SECURITY" else (0,0)
        medical = kind*p["budget26_medical"]/(p["budget26_medical"]+p["budget26_welfare"])
        care = kind*p["budget26_care"]/(p["budget26_medical"]+p["budget26_welfare"])
        component = dict(income_tax=(r["income"],income), corporate_tax=(r["corporate"],nominal),
                         consumption_tax=(r["vat"],prices), other_tax=(r["tax"]-r["income"]-r["corporate"]-r["vat"],prices),
                         social_contributions=(r["social"],p["budget26_premiums"]/p["ilo24_premiums_rounded"]),
                         other_revenue=(r["revenue"]-r["tax"]-r["social"]-r["interest_in"]-r["transfer_in"],prices),
                         pension=(pension,p["budget26_pension"]/p["ilo24_pension"]),
                         medical=(medical,p["budget26_medical"]/p["ilo24_medical"]),
                         care=(care,prices), other_benefits=(r["benefits"]-pension-medical-care,prices),
                         payroll=(r["payroll"],income), supplies=(r["supplies"],prices),
                         depreciation=(r["depreciation"],prices), net_fixed_capital=(r["net_fixed_capital"],prices),
                         other_nonfinancial=(r["net_capital"]-r["net_fixed_capital"],prices),
                         other_expense=(r["expense"]-r["benefits"]-r["payroll"]-r["supplies"]-r["depreciation"]
                                        -r["interest_out"]-r["transfer_out"],prices),
                         transfer_in=(r["transfer_in"],prices), transfer_out=(r["transfer_out"],prices),
                         exposure_debt=(r["securities"]+r["loans"],1), exposure_assets=(r["assets"],1))
        initial[s] = {k: a*b for k,(a,b) in component.items()}
        bridge.extend(dict(scope=s, variable=k, source_year=2024, model_year=2026, base=a,
                           factor=b, initial_trn=a*b, state="EXPOSURE_REFERENCE" if k.startswith("exposure")
                           else "NON_ADOPTED_FY26_BRIDGE") for k,(a,b) in component.items())
    return initial, bridge


def rates(gfs, s, source_year):
    r, opening = gfs[source_year,s], gfs[source_year-1,s]
    return r["interest_out"]/(opening["securities"]+opening["loans"]), r["interest_in"]/opening["assets"]


def components(a, idx, variation):
    elasticity = 1.5 if variation=="TAX_ELASTIC_1P5" else 1.0
    benefits = idx["wage"] if variation=="BENEFITS_WAGE_INDEX" else idx["prices"]
    return dict(income_tax=a["income_tax"]*idx["household_resource"]**elasticity,
                corporate_tax=a["corporate_tax"]*idx["n"]**elasticity,
                consumption_tax=a["consumption_tax"]*idx["consumption"]**elasticity,
                other_tax=a["other_tax"]*idx["prices"], social_contributions=a["social_contributions"]*idx["wage_bill"],
                other_revenue=a["other_revenue"]*idx["prices"]*idx["population"],
                pension=a["pension"]*idx["age65"]*benefits,
                medical=a["medical"]*idx["medical"]*(benefits/idx["prices"]),
                care=a["care"]*idx["age75"]*benefits,
                other_benefits=a["other_benefits"]*idx["population"]*benefits,
                payroll=a["payroll"]*idx["wage"]*idx["population"],
                supplies=a["supplies"]*idx["prices"]*idx["population"],
                depreciation=a["depreciation"]*idx["prices"],
                net_fixed_capital=a["net_fixed_capital"]*idx["prices"],
                other_nonfinancial=a["other_nonfinancial"]*idx["prices"],
                other_expense=a["other_expense"]*idx["prices"]*idx["population"],
                transfer_in=a["transfer_in"]*idx["prices"],
                transfer_out=a["transfer_out"]*idx["prices"])


def book(rt, values, sector, y):
    gross_capital = values["depreciation"] + values["net_fixed_capital"]
    assembled = {k: values[k] for k in RECEIPTS}
    assembled.update(cash_benefits=values["pension"]+values["other_benefits"],
                     medical=values["medical"], other_consumption=values["payroll"]+values["supplies"],
                     capital_formation=gross_capital,
                     other_primary_expense=values["other_expense"]+values["care"])
    # Negative net other nonfinancial acquisition is booked in its own signed bridge.
    assembled["other_primary_expense"] += max(values["other_nonfinancial"],0)
    assembled["other_revenue"] += max(-values["other_nonfinancial"],0)
    entries = rt.build_ledger(rt.Entry(k,y,sector,k,rt.EXTERNAL,
                                      "in" if k in RECEIPTS else "out", v,
                                      "SNA_GFS_SQ_projection", k, "non_adopted")
                              for k,v in assembled.items())
    completeness = {(k, "in") for k in (*RECEIPTS, "transfer")} | {
        (k, "out") for k in (*EXPENSES, "transfer")}
    # Education is embedded in payroll and supplies. Zero here is a ledger
    # partition, while the education breakout in the output is explicitly N/A.
    row, audit = rt.account(entries, y, (sector,), completeness)
    return row["primary_revenue"], row["primary_expense"], gross_capital, audit


def run(root, out):
    src = Inputs(root)
    prior_receipt = json.loads(src.raw(PREV, P+"Custody.json"))
    for item in prior_receipt["files"]:
        src.raw(PREV,item["path"])
        r = src.receipts[PREV,item["path"]]
        src.verify("prior_payload_bytes", (r["bytes"],r["sha256"])==(item["bytes"],item["sha256"]))
    for p in ("policies/StatusQuo.md", "specifications/SimulationSpecification_v6_Annex.md"):
        src.raw(PIN,p)
    spec = importlib.util.spec_from_file_location("sq_prior_fiscal_runtime",root/P/"Runtime.py")
    rt = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = rt
    src.verify("runtime_checkout_matches_pin", (root/P/"Runtime.py").read_bytes()==src.raw(PREV,P+"Runtime.py"))
    spec.loader.exec_module(rt)
    gfs, bridge = read_gfs(src)
    macro, diag = read_macros(src)
    old = {(r["condition"],int(r["year"]),r["scope"]):r for r in src.csv(PREV,P+"Annual.csv")}
    public = {int(r["year"]):r for r in src.csv(STATS,S+"Official_Fiscal_Baseline_2025_2040.csv")}
    mof = src.csv(STATS,S+"MOF_Anchor_References.csv")
    new_cap = float(next(r["value_trn"] for r in mof if r["metric"]=="new_bonds"))
    rollover_plan = float(next(r["value_trn"] for r in mof if r["metric"]=="refunding_bonds"))
    initial, initial_rows = benchmark(gfs,public)
    src.verify("case_year_scope_coverage",len(macro)==90 and len(old)==450)
    hist = gfs[2024,SCOPES[3]]
    src.near("historical_revenue",hist["revenue"],235.7316)
    src.near("historical_expenditure",hist["expense"]+hist["net_capital"],244.6436)
    src.near("historical_PB",hist["balance"]+hist["interest_out"]-hist["interest_in"],-8.1922)
    for s in (*SCOPES,"CONSOLIDATION"):
        r,p = gfs[2024,s],gfs[2023,s]
        for k in ("asset","liability"):
            stock = "assets" if k=="asset" else "liabilities"
            src.near("historical_stock_flow",p[stock]+r[k+"_transactions"]+
                     r[k+"_revaluation"]+r[k+"_volume_changes"],r[stock],.00031)
    annual,sensitivity,consolidations,stock_rows,residual=[],[],[],[],[]
    internal = gfs[2024,"CONSOLIDATION"]
    debt_elimination = -internal["securities"]-internal["loans"]
    asset_elimination = -internal["assets"]
    for s in SCOPES[:3]:
        borrow, yield_ = rates(gfs,s,2024)
        for k,value in (("effective_interest_rate",borrow),("effective_asset_yield",yield_)):
            initial_rows.append(dict(scope=s,variable=k,source_year=2024,model_year=2026,
                                     base=value,factor=1,initial_trn=None,initial_rate=value,state="NON_ADOPTED"))
    for name,x in (("internal_debt_elimination",debt_elimination),("internal_asset_elimination",asset_elimination)):
        initial_rows.append(dict(scope=SCOPES[3],variable=name,source_year=2024,model_year=2026,
                                 base=x,factor=1,initial_trn=x,state="EXPOSURE_REFERENCE"))
    for variant in VARIANTS:
        for mode in MODES:
            debt = {s:initial[s]["exposure_debt"] for s in SCOPES[:3]}
            assets = {s:initial[s]["exposure_assets"] for s in SCOPES[:3]}
            rate_year=2023 if variant=="RATE_FY2023" else 2024
            base_rates={s:rates(gfs,s,rate_year) for s in SCOPES[:3]}
            effective=dict((s,v[0]) for s,v in base_rates.items())
            repricing_share=rollover_plan/initial["CENTRAL"]["exposure_debt"]
            src.verify("bounded_refunding_rate_weight",0<repricing_share<1)
            for y in YEARS:
                m = macro[mode,y]
                if y>2026:
                    inflation=macro[mode,y-1]["prices"]/macro[mode,max(2026,y-2)]["prices"]-1 if y>2027 else .02
                    new_coupon=max(0,base_rates["CENTRAL"][0]+inflation-.02)
                    effective["CENTRAL"]=(1-repricing_share)*effective["CENTRAL"]+repricing_share*new_coupon
                anchor=macro[mode,2026]
                idx={k:m[k]/anchor[k] for k in m if k!="medical_unallocated"}
                idx["wage_bill"]=idx["prices"]*idx["labor"]
                if y==2026:
                    src.verify("fixed_initial_macro", (m["real"],m["n"],m["population"])==(580,600,122618024))
                units={s:components(initial[s],idx,variant) for s in SCOPES[:3]}
                transfer_paid=sum(v["transfer_out"] for v in units.values())
                transfer_received_raw=sum(v["transfer_in"] for v in units.values())
                # Aggregate-only alignment of GFS margins. Adjust published rounding;
                # no bilateral transfer is created.
                src.near("transfer_rounding_bound",transfer_paid,transfer_received_raw,.00031*idx["prices"])
                for v in units.values():
                    v["transfer_in"] *= transfer_paid/transfer_received_raw
                rows={}
                for s,v in units.items():
                    income,expense,gross_cap,audit=book(rt,v,s,y)
                    src.verify("exclusive_external_entry_booking",not audit)
                    income+=v["transfer_in"]
                    expense+=v["transfer_out"]
                    pb=income-expense
                    rate,yield_=effective[s],base_rates[s][1]
                    ip,ir=rt.interest_on_opening(initial[s]["exposure_debt"],rate,initial[s]["exposure_assets"],yield_)
                    balance=pb-ip+ir
                    cip,cir=rt.interest_on_opening(debt[s],rate,assets[s],yield_)
                    cbal=pb-cip+cir
                    need=max(0,-cbal)
                    cap=new_cap if s=="CENTRAL" and variant!="FUNDING_NO_NEW_CREDIT" else 0
                    issued=min(cap,need)
                    # Refunding exposure only for central. Both legs match and
                    # are excluded from new net borrowing and PB.
                    rolls=min(debt[s],rollover_plan*debt[s]/initial[s]["exposure_debt"]) if s=="CENTRAL" else None
                    old_debt,old_assets=debt[s],assets[s]
                    stocks=rt.annual_stocks(old_debt,issued,0,0,old_assets,0,0,0)
                    debt[s],assets[s]=stocks["debt_end"],stocks["assets_end"]
                    src.near("conditional_debt_recurrence",debt[s],old_debt+issued)
                    src.near("conditional_assets_recurrence",assets[s],old_assets)
                    src.verify("conditional_unfunded_bounds",0<=issued<=cap and issued<=need)
                    if rolls is not None:
                        src.near("conditional_refunding_neutrality",old_debt+(issued+rolls)-rolls,debt[s])
                    rows[s]=dict(**v, primary_revenue=income, primary_expenditure=expense, pb=pb,
                                 interest_paid=ip,interest_received=ir,net_interest=ip-ir,
                                 revenue=income+ir,expenditure=expense+ip,balance=balance,
                                 accrual_financing_need=max(0,-balance), gross_fixed_capital=gross_cap,
                                 opening_exposure_debt=initial[s]["exposure_debt"],opening_exposure_assets=initial[s]["exposure_assets"],
                                 borrowing_rate=rate,asset_yield=yield_, conditional_opening_debt=old_debt,
                                 conditional_opening_assets=old_assets,conditional_interest_paid=cip,conditional_interest_received=cir,
                                 conditional_net_interest=cip-cir,conditional_balance=cbal,conditional_accrual_need=need,
                                 conditional_net_issuance=issued,conditional_new_issuance_cap=cap,
                                 conditional_uncovered_accrual_need=need-issued,conditional_refunding=rolls,
                                 conditional_gross_issue=None if rolls is None else issued+rolls,
                                 conditional_gross_redemption=rolls,conditional_debt=debt[s],
                                 conditional_assets=assets[s],conditional_net_debt=stocks["net_debt"])
                gg = {}
                for k in rows["CENTRAL"]:
                    vals = [rows[s][k] for s in SCOPES[:3]]
                    gg[k] = sum(vals) if all(v is not None for v in vals) else None
                for col in ("primary_revenue","primary_expenditure","revenue","expenditure"):
                    gg[col]-=transfer_paid
                gg.update(revenue_before_unknown_internal_interest_elimination=gg["revenue"],
                          expenditure_before_unknown_internal_interest_elimination=gg["expenditure"],
                          transfer_in=0,transfer_out=0,interest_paid=None,interest_received=None,
                          revenue=None,expenditure=None,conditional_interest_paid=None,
                          conditional_interest_received=None,borrowing_rate=None,asset_yield=None,
                          opening_exposure_debt=gg["opening_exposure_debt"]-debt_elimination,
                          opening_exposure_assets=gg["opening_exposure_assets"]-asset_elimination,
                          conditional_debt=gg["conditional_debt"]-debt_elimination,
                          conditional_opening_debt=gg["conditional_opening_debt"]-debt_elimination,
                          conditional_assets=gg["conditional_assets"]-asset_elimination,
                          conditional_opening_assets=gg["conditional_opening_assets"]-asset_elimination)
                gg["conditional_net_debt"]=gg["conditional_debt"]-gg["conditional_assets"]
                gg["accrual_financing_need"]=max(0,-gg["balance"])
                gg["conditional_accrual_need"]=max(0,-gg["conditional_balance"])
                gg["conditional_uncovered_accrual_need"]=sum(rows[s]["conditional_uncovered_accrual_need"] for s in SCOPES[:3])
                rows[SCOPES[3]]=gg
                if variant=="CENTRAL_ESTIMATE":
                    consolidations.append(dict(condition=mode,year=y,transfers_eliminated=transfer_paid,
                                                raw_margin_difference=transfer_paid-transfer_received_raw,
                                                matching="GFS_AGGREGATE_ONLY",bilateral_matrix=None,
                                                internal_interest=None, conditional_internal_debt=debt_elimination,
                                                conditional_internal_assets=asset_elimination))
                for s,r in rows.items():
                    src.near("primary_balance_identity",r["primary_revenue"]-r["primary_expenditure"],r["pb"])
                    src.near("net_interest_balance_identity",r["pb"]-r["net_interest"],r["balance"])
                    src.near("conditional_consolidated_stock_carry_step",r["conditional_opening_debt"]+
                             r["conditional_net_issuance"],r["conditional_debt"])
                    prior=old[mode,y,s]
                    pub=old[mode,y,"CENTRAL_LOCAL"]
                    obs=r if variant=="CENTRAL_ESTIMATE" else {k:r[k] for k in
                         ("pb","balance","net_interest","pension","medical","care","conditional_debt",
                          "conditional_net_issuance","conditional_uncovered_accrual_need")}
                    item=dict(condition=mode,year=y,scope=s,variant=variant,nominal_gdp=m["n"],**obs)
                    if variant=="CENTRAL_ESTIMATE":
                        row=item
                        row.update(model_status="NON_ADOPTED",sq_original_tax_proxy=float(diag[mode,y]["sq_tax_proxy"]),
                                   caofin_prior_pb=prior["reference_pb"],caofin_prior_balance=prior["reference_balance"],
                                   prior_CL_PB_50=pub["CL_tax_sensitivity_PB_0p5"],
                                   prior_CL_PB_100=pub["CL_tax_sensitivity_PB_1p0"],
                                   cash_financing_need=None,actual_debt=None,actual_assets=None,actual_issuance=None,
                                   education=None,conditional_asset_acquisition=0,conditional_asset_disposal=0,
                                   conditional_debt_sfa=0,conditional_asset_sfa=0,
                                   gross_revenue_known=r["revenue"] is not None,
                                   funding_status="SEPARATE_CONDITIONAL_ACCRUAL_ONLY")
                        for f in ("revenue","expenditure","primary_revenue","primary_expenditure","pb","balance",
                                  "net_interest","conditional_debt","conditional_assets","conditional_net_debt",
                                  "accrual_financing_need","conditional_uncovered_accrual_need"):
                            row[f+"_pct_gdp"]=None if r[f] is None else 100*r[f]/m["n"]
                        for field in ("pb","balance"):
                            v=row["caofin_prior_"+field]
                            row[field+"_minus_CAO_reference"]=None if v=="N/A" else r[field]-float(v)
                        annual.append(row)
                        stock_rows.append({k:v for k,v in row.items() if k in
                                           ("condition","year","scope","actual_debt","actual_assets","actual_issuance")
                                           or "conditional_" in k})
                        residual.append(dict(condition=mode,year=y,scope=s,projected_accrual_need=row["accrual_financing_need"],
                                             uncovered_conditional_accrual_need=r["conditional_uncovered_accrual_need"],
                                             actual_cash_need=None,medical_payer_gap_outside_ledger=m["medical_unallocated"]
                                             if s==SCOPES[3] else None,
                                             limits="NO_CASH_BRIDGE_NO_BILATERAL_FINANCIAL_MATRIX"))
                    else:
                        sensitivity.append(item)
    base={(r["condition"],r["year"],r["scope"]):r for r in annual}
    for row in (*annual,*sensitivity):
        anchor=base["A",row["year"],row["scope"]]
        control=base[row["condition"],row["year"],row["scope"]]
        for field in ("pb","balance","net_interest","conditional_debt"):
            if row["variant"]=="CENTRAL_ESTIMATE":
                row[field+"_delta_vs_A"]=row[field]-anchor[field]
            else:
                row[field+"_delta_vs_central_estimate"]=row[field]-control[field]
    for mode in MODES:
        for s in SCOPES:
            for y in range(2027,2056):
                a,b=base[mode,y-1,s],base[mode,y,s]
                src.near("conditional_year_to_year_debt",a["conditional_debt"],b["conditional_opening_debt"])
                src.near("conditional_year_to_year_assets",a["conditional_assets"],b["conditional_opening_assets"])
            src.verify("same_rules_cross_2040_2041",base[mode,2041,s]["pb"]!=base[mode,2040,s]["pb"])
    src.verify("output_coverage",len(annual)==360 and len(sensitivity)==1440)
    for y in range(2026,2041):
        r=public[y]
        opening=float(public[y-1]["CL_debt_end_trn"])
        closing=float(r["CL_debt_end_trn"])
        bal=float(r["CL_balance_trn"])
        indiv_open=sum(float(public[y-1][s+"_debt_end_trn"]) for s in ("central","local"))
        indiv_close=sum(float(r[s+"_debt_end_trn"]) for s in ("central","local"))
        indiv_bal=sum(float(r[s+"_balance_trn"]) for s in ("central","local"))
        stock_rows.append(dict(condition="CAO_REFERENCE",year=y,scope="CENTRAL_LOCAL",
                               difference_vs_sum_sector_residual=(closing-opening+bal)-(indiv_close-indiv_open+indiv_bal),
                               reference_opening=opening,reference_closing=closing,reference_balance=bal,
                               reference_unexplained_stock_flow=closing-opening+bal,
                               explained_identical_boundary_component=None,
                               reference_nominal_gdp=float(r["official_nominal_GDP_trn"])))
    stock_rows.extend(dict(condition="GFS_OBSERVED",year=2024,scope=s,**{
        k:gfs[2024,s][k] for k in FIN}) for s in (*SCOPES,"CONSOLIDATION"))
    sources = json.loads(src.raw(STATS,S+"Statistical_Source_Receipts.json"))
    gfs_receipt = next(x for x in sources if x["file"]=="SNA2024_GFS.xlsx")
    src.verify("GFS_original_byte_check", gfs_receipt["sha256"]==src.receipts[STATS,S+"SNA2024_GFS.xlsx"]["sha256"]
               and gfs_receipt["size"]==src.receipts[STATS,S+"SNA2024_GFS.xlsx"]["bytes"])
    for r in bridge:
        r.update(url=gfs_receipt["url"], source_sha256=gfs_receipt["sha256"],
                 publication="SNA FY2024 flow 2025-12-23")
    bridge.extend(dict(source="CAO_PROJECTIONS",year=y,scope="CENTRAL_LOCAL",variable="SPE_N_MINUS_CAO_FY_N",
                       raw=public[y]["official_nominal_GDP_trn"],unit="trillion_yen",
                       amount_trn=macro[c,y]["n"]-float(public[y]["official_nominal_GDP_trn"]),
                       condition=c,conversion="SPE fixed N minus CAO FY reference; no forced calibration")
                  for c in MODES for y in range(2026,2041))
    input_groups = (
        (("fy25_nominal","fy25_real","fy25_domestic_price"),2025,"2026-05-19","2026年1–3月期GDP 1次速報 概要第5節",
         "https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/2026/qe261/pdf/gaiyou2611.pdf","FY_ACTUAL_PRELIMINARY"),
        (("ilo24_pension","ilo24_medical"),2024,"2026-07-29","ILO 社会保障給付費 部門別",
         "https://www.ipss.go.jp/ss-cost/j/fsss-R06/R06-houdou.pdf","ILO_HISTORICAL"),
        (("budget26_pension","budget26_medical","budget26_care","budget26_welfare","budget26_premiums",
          "ilo24_premiums_rounded"),2026,"2026-10","III-18 社会保障 p.31",
         "https://www.mof.go.jp/policy/budget/fiscal_condition/related_data/202610_03.pdf","BUDGET_COMPOSITION"),
        (("fy26_price_assumption",),2026,"N/A","SPE P2通常年を初期橋渡し用に転用",
         "https://github.com/spe-flatvat/SPE/commit/"+DYN,"MODEL_ASSUMPTION"),
    )
    for names, year, publication, table, url, state in input_groups:
        for term in names:
            bridge.append(dict(source=state,year=2024 if term.startswith("ilo24") else year,
                               publication=publication,table=table,url=url,variable=term,raw=DATA[term],
                               unit="multiplier" if term.startswith("fy") else "trillion_yen",
                               conversion="used as ratio or constrained composition in Initial_Conditions"))
    for entry in mof:
        bridge.append(dict(source="MOF_CENTRAL_BOUNDARY_REFERENCE",year=2026,scope=entry["scope"],
                           variable=entry["metric"],raw=entry["value_trn"],unit="trillion_yen",
                           url=entry["source_url"],publication=entry["vintage"],
                           conversion="central new borrowing/refunding diagnostic only" if entry["metric"] in
                           ("new_bonds","refunding_bonds") else "reference only; boundary not interchangeable"))
    original = [dict(condition=c,year=y,origin="FIXED_PRIOR_SQ_MODEL",
                     tax_proxy=float(diag[c,y]["sq_tax_proxy"]),tax_proxy_pct_gdp=float(diag[c,y]["sq_tax_pct_GDP"]),
                     national_tax=None, national_pb=None, medical_model_unallocated=macro[c,y]["medical_unallocated"],
                     prior_CL_PB_50=old[c,y,"CENTRAL_LOCAL"]["CL_tax_sensitivity_PB_0p5"],
                     prior_CL_PB_100=old[c,y,"CENTRAL_LOCAL"]["CL_tax_sensitivity_PB_1p0"])
                for c in MODES for y in YEARS]
    for name, rows in dict(Annual=annual,Original_Reference=original,Key_Years=[r for r in annual if r["year"] in KEY],Initial_Conditions=initial_rows,
                           Source_Bridge=bridge,Consolidation=consolidations,Stock_Flow_Bridge=stock_rows,
                           Fiscal_Residual=residual,Sensitivity=sensitivity).items():
        write_csv(out/(name+".csv"),rows)
    write_json(out/"Dependencies.json",dict(inputs=list(src.receipts.values()),external_parameter_values=DATA,
                                            fiscal_macro_feedback=False))
    write_json(out/"Validation.json",dict(status="PASS_DEFINED_CHANNELS",checks=dict(sorted(src.counts.items())),
                                          total=sum(src.counts.values()),primary_case_years=90,scope_rows=360,
                                          sensitivity_case_years=360,fixed_macro_case_years=90,
                                          not_validated=["actual funding","forward bilateral interest and holdings",
                                                         "cash conversion","full general government closure"]))


if __name__=="__main__":
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root",required=True,type=Path)
    cli.add_argument("--outdir",required=True,type=Path)
    args=cli.parse_args()
    args.outdir.mkdir(parents=True,exist_ok=True)
    run(args.root.resolve(),args.outdir.resolve())
