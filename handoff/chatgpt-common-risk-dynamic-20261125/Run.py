"""Run the fixed-worktree C/D experiment twice and verify individual outputs."""
import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from Runtime import D0, DRAFT, DRAFT_PIN, H, MATCH, run_common, run_f, run_n3

PIN = "6ffd83bb2ce4944ea59690b63e93aca1f6826c40"
PRE = "adb373d87c5beb68b35f84be9e504c84d67014e0"
REC = "ff2e8c3d78d1c64c1d79f8d39dee3a9de786a6d8"
PRICE = "2d8cb85878c931d9d127755af6d2eb336c04c04d"
LATEST = "3d3507e2df9218a6bbda587e9b8b0c0d423ae2ac"
FIX = "7dd893eeed781af2bb323c424b456fdd907a667f"
COMMON = "8a8edb403b960cceb535f9b70461646e9374c229"
CLAUDE = "da79ab621de27a1a2df8dd3edf050e4f02fac63a"
KEYS = (2026,2030,2035,2043,2045,2055)
YEARS = range(2026,2056)
EVENTS = ("conflict","earthquake","disaster","climate")
NA = "N/A"


def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n")


def dump(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, keys, lineterminator="\n", restval=NA)
        writer.writeheader()
        writer.writerows(rows)


def run(root, out, work):
    out.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    checks = Counter()
    deps = {}

    def check(name, condition):
        if not condition:
            raise ValueError(f"{name} after {checks[name]} successful checks")
        checks[name] += 1

    def close(name, x, y):
        check(name, math.isclose(x,y,rel_tol=2e-11,abs_tol=3e-7))

    def git(*args):
        return subprocess.check_output(["git","-C",str(root),*args])

    def raw(ref,path):
        b = git("show",f"{ref}:{path}")
        deps[ref+":"+path] = dict(commit=ref,path=path,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
        return b

    def js(ref,path):
        return json.loads(raw(ref,path))

    def read(ref,path):
        return list(csv.DictReader(io.StringIO(raw(ref,path).decode())))

    # Existing adapters open source files by relative path. Require exact
    # tracked checkout contents and record the fixed tree identity.
    check("fixed_checkout", git("rev-parse","HEAD").decode().strip()==PIN)
    check("immutable_checkout", not git("diff","--name-only","HEAD"))
    price_dir = H+"common-price-nominal-real-20261125/"
    recovery_dir = H+"risk-specific-recovery-20261124/"
    latest_dir = H+"f-latest-integration-20261125/"
    common_dir = H+"f-sq-n3-common-indicators-20261123/"
    price = {(int(r["year"]),r["scenario"],r["mode"]):r for r in read(PRICE,price_dir+"Annual.csv")}
    recovery = {(int(r["year"]),r["scenario"],r["mode"]):r for r in read(REC,recovery_dir+"Annual.csv")}
    events = read(PRE,H+"common-macro-gdp-attribution-20261124/Event_Schedule.csv")
    fixed_f = {(int(r["year"]),r["series"]):r for r in read(LATEST,latest_dir+"Annual.csv")}
    fixed_n3 = {r["year"]:r for r in js(FIX,MATCH+"N3/N3_Actual_Annual.json")}
    fixed_f_runtime = js(FIX,MATCH+"F/F_Actual_Annual.json")
    fixed_f_trace = js(FIX,MATCH+"F/F_Runtime_Trace.json")["years"]
    fixed_sq_trace = js(FIX,MATCH+"BASE_REPLAY/Common_Trace_BASE_REPLAY.json")["years"]
    fixed_n3_midpoints = js(FIX,MATCH+"N3/N3_Runtime_Midpoints.json")
    fixed_common = {(int(r["year"]),r["indicator"]):r for r in read(COMMON,common_dir+"Annual_Comparison.csv")}
    fixed_closure = {r["year"]:r for r in js(FIX,MATCH+"N3/N3_Actual_Fiscal.json")}
    common_deps = js(COMMON,common_dir+"Dependencies.json")
    for item in common_deps.values():
        b = raw(item["commit"],item["path"])
        check("common_source_identity",(len(b),hashlib.sha256(b).hexdigest())==(item["bytes"],item["sha256"]))
    for ref, directory in ((REC,recovery_dir),(PRICE,price_dir),(LATEST,latest_dir)):
        receipt = js(ref,directory+"Custody.json")
        for item in receipt["files"]:
            path = item["path"]
            if ref+":"+path in deps or path.endswith(("Run.py","Report.md","Dependencies.json","Inclusion.csv",
                                                     "Unconnected.csv","Funding_Residual.csv")):
                b = raw(ref,path)
                check("prior_receipt_identity",(len(b),hashlib.sha256(b).hexdigest())==(item["bytes"],item["sha256"]))
    for path in ("policies/FreedomPolicies.md","policies/FreedomPolicies_Annex.md","policies/StatusQuo.md",
                 "policies/New3linesPolicies.md","specifications/SimulationSpecification_v6.md",
                 H+"common-risk-dynamic-request-20261125/SPE_Work_Common_Risk_Dynamic_Integration_Request_20261125.md"):
        raw(PIN,path)
    raw(CLAUDE,"handoff/claude-f-sq-n3-common-indicators-verification-20261123/Validation.json")
    draft = work/"draft"/DRAFT
    draft.parent.mkdir(parents=True)
    draft.write_bytes(raw(DRAFT_PIN,DRAFT))

    annual, bridges, fiscals, incidence, event_rows = [],[],[],[],[]
    by_key = {}
    price_sequence = [D0]
    for y in list(YEARS)[1:]:
        price_sequence.append(price_sequence[-1]*(1.07 if y==2027 else 1.02))
    event_list = [(int(r["year"]),event,float(r[event])) for r in events
                  for event in EVENTS if float(r[event])]
    check("initial_oil_off", all(r["oil_applied"]=="False" for r in events))
    check("common_event_calendar", event_list==sorted(
        [(2027,"conflict",.05),(2031,"earthquake",.03)]+
        [(y,"disaster",.01) for y in range(2029,2056,3)]+
        [(y,"climate",.005) for y in range(2028,2056,2)], key=lambda t:t[0]))
    for i,y in enumerate(YEARS):
        for case in ("F","SQ","N3"):
            old = price[y,case,"A"]
            for metric,field in (("real_gdp","real_gdp_trn"),("nominal_gdp","nominal_gdp_trn")):
                close("fixed_A_identity",float(old[field]),float(fixed_common[y,metric][case]))
            annual.append(dict(year=y,case=case,condition="A",origin="REUSED",
                               real_gdp_trn=float(old["real_gdp_trn"]),nominal_gdp_trn=float(old["nominal_gdp_trn"]),
                               population=float(old["population"]),real_pc_yen=float(old["real_per_capita_yen"]),
                               nominal_pc_yen=float(old["nominal_per_capita_yen"]),
                               deflator_index=float(old["deflator_2026_100"])))
    for mode, prev_mode, duration_short in (("C","P3",1),("D","P4",2)):
        factors = []
        for i,y in enumerate(YEARS):
            pieces = []
            for start,event,loss in event_list:
                if start>y:
                    continue
                duration = 5 if event in ("conflict","earthquake") else duration_short
                left = loss*max(0.,1-(y-start)/duration)
                check("recovery_bounds", 0<=left<=loss and (start!=y or left==loss) and
                      (y-start<duration or left==0))
                pieces.append(1-left)
                event_rows.append(dict(condition=mode,year=y,event=event,start=start,duration=duration,
                                       onset_loss=loss,remaining=left,individual_factor=1-left))
            factors.append(math.prod(pieces))
            close("fixed_recovery_factors", factors[-1],float(recovery[y,"SQ",mode]["risk_multiplier"]))
            close("fixed_P2_price",price_sequence[i],float(price[y,"SQ",prev_mode]["price_coefficient"]))

        # Child runs isolate legacy module globals, traces and adapters.
        job = work/mode
        job.mkdir()
        configuration = job/"Inputs.json"
        save(configuration, dict(factors=factors,prices=price_sequence))
        for worker in ("f","f_sensitivity","common_n3"):
            subprocess.run([sys.executable,str(Path(__file__).resolve()),"--worker",worker,
                            "--root",str(root),"--outdir",str(job),"--input",str(configuration),
                            "--draft",str(work/"draft")], check=True)
        f, ft, fh = json.loads((job/"f.json").read_bytes())
        fs, fst, fsh = json.loads((job/"f_sensitivity.json").read_bytes())
        sq, native_n3, n3, nf, nm, nc, internal_checks = json.loads((job/"common_n3.json").read_bytes())
        checks["N3_runtime_native_dynamic_checks"] += internal_checks
        p = ft["parameters"]
        prev_prices = {}
        live_additive_index = {}
        for i,y in enumerate(YEARS):
            for case in ("F","SQ","N3","F_HH"):
                is_f = case in ("F","F_HH")
                sensitivity = case=="F_HH"
                underlying = "F" if is_f else case
                old = price[y,underlying,prev_mode]
                rec = recovery[y,underlying,mode]
                t = (fst if sensitivity else ft)["years"][i] if is_f else sq[i]
                m = (fs if sensitivity else f)[i] if is_f else t["macro_row"]
                hh = (fsh if sensitivity else fh)[str(y)] if is_f else {}
                if case=="N3":
                    v,b,k = n3[i],nf[i],nm[i]
                    old_t = fixed_n3_midpoints[i]
                    C_state, I_state = k["C"], k["I"]+k["privI"]+k["pubI"]
                    previous_I = old_t["I"]+old_t["privI"]+old_t["pubI"]
                    old_tax = fixed_n3[y]["total_tax_diagnostic_proxy_trn"]
                    real,nom,des,cap,unmet = (v[col] for col in ("real_GDP_trn","nominal_GDP_trn",
                                      "desired_real_GDP_trn","supply_ceiling_real_trn","unmet_demand_real_trn"))
                    tax = v["total_tax_diagnostic_proxy_trn"]
                    income,cons,supply = (v[col] for col in ("household_resource_DI_proxy_trn",
                                                           "consumption_real_trn","supply_real_trn"))
                    wage = 400*(t["coreD"]/D0)*(.99 if y in (2027,2028) else 1.)*(
                            1+p["wage_gap_elasticity"]*(real-t["coreY"])/t["coreY"])
                    pen, relief, inkind = v["pension_contribution_trn"],v["existing_premium_relief_trn"],v["existing_in_kind_trn"]
                    pop = t["demography"]["population"]
                    close("N3_G_off",v["government_purchase_nominal_trn"],0.)
                    close("N3_I_off",v["public_investment_nominal_trn"],0.)
                    close("N3_rollover_retained",b["rollover_share"],fixed_closure[y]["rollover_share"])
                    close("N3_shared_core",native_n3[i]["coreY"],t["coreY"])
                    fiscals.append(dict(year=y,case=case,condition=mode,scope="CONDITIONAL_CENTRAL_LOCAL",
                                       CL_PB_trn=b["PB_trn"],CL_debt_trn=b["debt_end_trn"],
                                       CL_interest_trn=b["interest_trn"],CL_borrowing_candidate_trn=b["new_cash_borrowing_trn"],
                                       CL_cash_assets_trn=b["assets_end_trn"],
                                       CL_cash_redemption_trn=b["cash_debt_redemption_trn"],
                                       CL_assumed_gross_redemption_trn=b["assumed_gross_redemption_trn"],
                                       CL_rollover_share=b["rollover_share"],separate_central_local_closure=NA,
                                       CL_PB_delta_vs_A_trn=b["PB_trn"]-fixed_n3[y]["CL_PB_candidate_trn"],
                                       CL_debt_delta_vs_A_trn=b["debt_end_trn"]-fixed_n3[y]["CL_debt_candidate_trn"],
                                       insurer_policy_partial_trn=b["insurer_balance_delta_trn"],
                                       N3_medical_unassigned_trn=nc[i]["medical_unassigned_trn"],
                                       SFA_fixed_unallocated_trn=b["SFA_trn"],national_PB=NA))
                else:
                    real,nom,des,cap,unmet = (t[col] for col in ("Y","N","desired","capacity","unmet"))
                    supply,wage = t["supply"],t["nominalwage_proxy"]
                    old_t = fixed_f_trace[i] if is_f else fixed_sq_trace[i]
                    C_state, I_state, previous_I = t["C"],t["I"],old_t["I"]
                    old_tax = fixed_f_runtime[i]["tax_diagnostic_trn"] if is_f else old_t["tax"]+old_t["direct"]
                    if is_f:
                        tax = m["tax_diagnostic_trn"]
                        income,cons,pop = (m[col] for col in ("macro_cash_DI_proxy_trn","household_consumption_real_proxy_trn","population"))
                        pen = m["modeled_net_contribution_delta_trn"]+hh.get("pension_delta",0.)
                        relief = m["A_relief_trn"]+hh.get("A_delta",0.)
                        inkind = m["B_used_trn"]+hh.get("B_delta",0.)
                        eg = m["education_unassigned_cash_finance_trn"]
                        mg = m["medical_unassigned_after_sources_trn"]
                        base_g = m["government_unassigned_funding_trn"]
                        base_i = m["insurer_unassigned_funding_trn"]
                        debt = m["bond_end_trn"]+m["medical_policy_debt_stock_trn"]
                        gov,ins = hh.get("government_gap_delta",0.),hh.get("insurer_gap_delta",0.)
                        fiscals.append(dict(year=y,case=case,condition=mode,scope="F_IDENTIFIED_PARTIAL",
                                            F_education_gap_trn=eg,F_medical_gap_trn=mg,
                                            F_ABC_government_signed_gap_trn=base_g+gov,
                                            F_ABC_insurer_signed_gap_trn=base_i+ins,
                                            F_education_medical_debt_trn=debt,
                                            F_partial_government_balance_before_sensitivity_settlement_trn=
                                            m["government_partial_balance_proxy_trn"],
                                            national_PB=NA))
                        close("education_debt_stock",m["bond_end_trn"],m["bond_begin_trn"]+
                              m["bond_issue_trn"]-m["bond_redemption_trn"])
                        for field in ("transfer_residual_trn","independent_claim_residual_trn","independent_financing_residual_trn"):
                            close("F_medical_closure",m[field],0.)
                        if i:
                            old_annual = (fs if sensitivity else f)[i-1]
                            close("F_education_debt_carry",m["bond_begin_trn"],old_annual["bond_end_trn"])
                            old_trace = (fst if sensitivity else ft)["years"][i-1]
                            close("F_consumption_state_carry",t["C"],(1-p["lambda_C"])*old_trace["C"]+p["lambda_C"]*t["Ctarget"])
                        if sensitivity:
                            incidence.append(dict(year=y,condition=mode,**hh,
                                                  median_real_2026_yen=hh["median_nominal_yen"]/(t["coreD"]/D0)))
                    else:
                        tax=t["tax"]+t["direct"]
                        income,cons,pop = (m[col] for col in (
                            "household_disposable_nominal_trn","household_consumption_real_proxy_trn","population_persons"))
                        pen=relief=inkind=NA
                        fiscals.append(dict(year=y,case=case,condition=mode,scope="SQ_FISCAL_CLOSURE_NA",
                                            SQ_tax_proxy_trn=tax, national_PB=NA))

                d=t["coreD"]
                close("live_P2",d,price_sequence[i])
                close("one_real_risk_application",t["coreY"],580*1.01**i*factors[i]*
                      (t["labor"]/t["labor_anchor"])**p["labor_response"])
                close("core_nominal_identity",t["coreN"],t["coreY"]*d)
                close("supply_cap",real,min(des,cap))
                close("unmet_demand",unmet,max(0.,des-real))
                pressure=p["price_pressure_coefficient"]*unmet/t["coreY"]
                close("nominal_identity",nom,real*d*(1+pressure))
                if i==0:
                    close("initial_real",real,580.)
                    close("initial_nominal",nom,600.)
                else:
                    previous = by_key[y-1,case,mode]
                    close("previous_core_growth",t["growth"],t["coreY"]/previous["core_real_gdp_trn"]-1)
                oldY,oldN = float(old["real_gdp_trn"]),float(old["nominal_gdp_trn"])
                start_d,start_c,start_core = [float(rec[col]) for col in ("desired","capacity","core")]
                close("fixed_diagnostic_real",min(start_d,start_c),oldY)
                a = min(start_d+t["coreY"]-start_core,start_c)
                h = min(des,start_c)
                price_effect = real*(d*(1+pressure)-oldN/oldY)
                real_effect = (real-oldY)*oldN/oldY
                close("real_bridge_closure",real-oldY,(a-oldY)+(h-a)+(real-h))
                close("nominal_bridge_closure",nom-oldN,price_effect+real_effect)
                old_latest = fixed_f[y,"F3"] if sensitivity and mode=="C" else None
                c_delta, i_delta = C_state-old_t["C"], I_state-previous_I
                supply_delta = p["capacity_absorption"]*(supply-old_t["supply"])
                other = des-start_d-(t["coreY"]-start_core)-c_delta-i_delta-supply_delta
                close("desired_component_closure", des-start_d,
                      (t["coreY"]-start_core)+c_delta+i_delta+supply_delta+other)
                bridges.append(dict(year=y,condition=mode,case=case,prior_fixed_real=oldY,
                                    prior_fixed_nominal=oldN,delta_real=real-oldY,core_demand_first=a-oldY,
                                    other_demand_next=h-a,capacity_last=real-h,
                                    delta_desired=des-start_d,delta_capacity=cap-start_c,
                                    delta_nominal=nom-oldN,volume_at_fixed_price=real_effect,
                                    price_and_interaction_last=price_effect,
                                    demand_C_state_delta=c_delta,demand_I_state_delta=i_delta,
                                    demand_supply_absorption_delta=supply_delta,
                                    other_desired_terms_residual=other,
                                    tax_diagnostic_delta_vs_A=tax-old_tax,
                                    real_delta_vs_previous_F3=(real-float(old_latest["real_gdp_trn"]) if old_latest else NA),
                                    nominal_delta_vs_previous_F3=(nom-float(old_latest["nominal_gdp_trn"]) if old_latest else NA)))
                if i:
                    live_additive_index[case] *= 1+(0.07 if y==2027 else .02)/(1+t["growth"])
                else:
                    live_additive_index[case]=100.
                implicit = 100*nom/real/D0
                row = dict(year=y,case=case,condition=mode,origin="NON_ADOPTED_DYNAMIC",
                           real_gdp_trn=real,nominal_gdp_trn=nom,population=pop,
                           effective_labor=t["labor"],real_pc_yen=real*1e12/pop,nominal_pc_yen=nom*1e12/pop,
                           core_real_gdp_trn=t["coreY"],core_nominal_gdp_trn=t["coreN"],risk_factor=factors[i],
                           input_inflation_pct=7. if y==2027 else 2.,price_coefficient=d,pressure=pressure,
                           deflator_index=implicit,deflator_growth_pct=100*(implicit/prev_prices[case]-1) if i else NA,
                           same_core_additive_price_index_diagnostic=live_additive_index[case],
                           nominal_wage_proxy_man=wage,household_nominal_income_resource_proxy_trn=income,
                           household_consumption_proxy_real_trn=cons,capacity_real_trn=cap,
                           supply_real_trn=supply,desired_real_trn=des,unmet_real_trn=unmet,tax_diagnostic_trn=tax,
                           contribution_proxy_trn=pen,A_relief_or_N3_premium_relief_trn=relief,B_or_N3_in_kind_trn=inkind,
                           F_C_paid_trn=m["C_cash_trn"]+hh.get("C_delta",0.) if is_f else NA,
                           F_VAT_price_basket_nominal_trn=m["VAT_price_effect_trn"] if is_f else NA,
                           F_education_net_spend_trn=m["net_additional_education_spend_trn"] if is_f else NA,
                           F_medical_clinical_cost_delta_trn=m["clinical_cost_delta_trn"] if is_f else NA,
                           F_synthetic_median_real_2026_yen=hh["median_nominal_yen"]/(d/D0) if is_f else NA,
                           F_HH_import_proxy_delta_trn=(1-p["domestic_share"])*hh["demand_delta"] if sensitivity else NA)
                prev_prices[case]=implicit
                by_key[y,case,mode]=row
                annual.append(row)

    summary, gaps = [], []
    for mode in ("C","D"):
        for case in ("F","SQ","N3","F_HH"):
            complete = [by_key[y,case,mode] for y in YEARS]
            base_case="F" if case=="F_HH" else case
            real=[r["real_gdp_trn"] for r in complete]
            summary.append(dict(condition=mode,case=case,real_2055=real[-1],
                                first_return_580=next((r["year"] for r in complete[1:] if r["real_gdp_trn"]>=580),NA),
                                sustained_return_580=next((r["year"] for j,r in enumerate(complete[1:],1)
                                                           if min(real[j:])>=580),NA),
                                cumulative_real_trn_years=sum(real),
                                cumulative_delta_vs_A=sum(real)-sum(float(price[y,base_case,"A"]["real_gdp_trn"]) for y in YEARS),
                                cumulative_delta_vs_fixed_diagnostic=sum(real)-sum(
                                    float(price[y,base_case,"P3" if mode=="C" else "P4"]["real_gdp_trn"]) for y in YEARS)))
            for row in complete:
                year=row["year"]
                sq=by_key[year,"SQ",mode]
                n3=by_key[year,"N3",mode]
                gaps.append(dict(year=year,condition=mode,case=case,
                                 real_minus_SQ=row["real_gdp_trn"]-sq["real_gdp_trn"],
                                 nominal_minus_SQ=row["nominal_gdp_trn"]-sq["nominal_gdp_trn"],
                                 real_minus_N3=row["real_gdp_trn"]-n3["real_gdp_trn"],
                                 nominal_minus_N3=row["nominal_gdp_trn"]-n3["nominal_gdp_trn"]))
    check("coverage",len(annual)==330 and len(bridges)==240 and len(incidence)==60 and len(by_key)==240)
    for name,rows in (("Annual.csv",annual),("Key_Years.csv",[x for x in annual if x["year"] in KEYS]),
                      ("Dynamic_Bridge.csv",bridges),("Fiscal_Residual.csv",fiscals),
                      ("F_Household_Sensitivity.csv",incidence),("Recovery_Events.csv",event_rows),
                      ("Summary.csv",summary),("Policy_Gaps.csv",gaps)):
        dump(out/name,rows)
    save(out/"Dependencies.json",dict(fixed_runtime_commit=PIN,fixed_tree=git("rev-parse","HEAD^{tree}").decode().strip(),
                                      inputs=list(deps.values())))
    save(out/"Validation.json",dict(status="PASS",new_checks=sum(checks.values()),groups=dict(sorted(checks.items())),
                                     new_main_rows=180,new_household_sensitivity_rows=60,fixed_A_rows=90))


def worker(args):
    source = json.loads(args.input.read_bytes())
    f,d = source["factors"],source["prices"]
    if args.worker in ("f","f_sensitivity"):
        data=run_f(args.root,args.outdir/args.worker,f,d,args.worker=="f_sensitivity")
    else:
        capture,sq,native=run_common(args.root,args.outdir/"capture",args.draft,f,d)
        sq_rows=[r for r in capture["records"] if r["case"]==sq]
        native_rows=[r for r in capture["records"] if r["case"]==native]
        data=(sq_rows,native_rows,*run_n3(args.root,args.outdir/"n3",capture,sq,native,d))
    save(args.outdir/(args.worker+".json"),data)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--outdir",type=Path,required=True)
    parser.add_argument("--worker")
    parser.add_argument("--input",type=Path)
    parser.add_argument("--draft",type=Path)
    args=parser.parse_args()
    args.root=args.root.resolve()
    if args.worker:
        worker(args)
    else:
        with tempfile.TemporaryDirectory() as folder:
            work=Path(folder)
            run(args.root,args.outdir,work/"first")
            other=work/"outputs"
            run(args.root,other,work/"second")
            files=sorted(p.name for p in other.iterdir())
            for name in files:
                assert (other/name).read_bytes()==(args.outdir/name).read_bytes(),name
        validation=args.outdir/"Validation.json"
        record=json.loads(validation.read_bytes())
        record["independent_process_output_byte_matches"]=files
        save(validation,record)
