"""Execute non-adopted N3 redemption allocations on fixed dynamic C/D."""
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

from Allocation import load_module, run as allocate

PIN="1ecb4399ae81bdcddd95f3a4c7f88ec8366fafca"
DYN="586cceb2a86c66265237a3616b92dc78f506c786"
PRE="adb373d87c5beb68b35f84be9e504c84d67014e0"
H="handoff/chatgpt-"
BASE=H+"common-risk-dynamic-20261125/"
AUTH=H+"n3-financing-authority-feasibility-20261123/"
EXEC=H+"n3-policy-gi-executor-financing-mapping-20261123/"
ACCOUNTS=H+"n3-central-local-funding-accounts-20261122/"
NATIVE=H+"n3-native-vs-diagnostic-separation-20261123/"
ASSUME=H+"n3-assumptions-specification-calibration-separation-20261123/"
YEARS=range(2026,2056)
KEYS=(2026,2030,2035,2045,2055)
NA="N/A"


def save(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def dump(path, rows):
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def execute(root,out,work):
    work.mkdir(parents=True)
    out.mkdir(parents=True,exist_ok=True)
    deps, checks = {}, Counter()

    def check(group, ok):
        if not ok:
            raise ValueError(f"{group} failed after {checks[group]} successful checks")
        checks[group]+=1

    def close(group, a, b):
        check(group,math.isclose(a,b,abs_tol=4e-7,rel_tol=2e-11))

    def git(*args):
        return subprocess.check_output(["git","-C",str(root),*args])

    def raw(commit,path):
        data=git("show",f"{commit}:{path}")
        deps[commit+":"+path]=dict(commit=commit,path=path,bytes=len(data),
                                    sha256=hashlib.sha256(data).hexdigest())
        return data

    def read(commit,path):
        return list(csv.DictReader(io.StringIO(raw(commit,path).decode())))

    check("checkout_pin",git("rev-parse","HEAD").decode().strip()==PIN)
    check("tracked_input_unchanged",not git("diff","--name-only","HEAD"))
    for item in json.loads(raw(DYN,BASE+"Custody.json"))["files"]:
        data=raw(DYN,item["path"])
        check("dynamic_source_bytes",(len(data),hashlib.sha256(data).hexdigest())==
              (item["bytes"],item["sha256"]))
    for path in ("policies/New3linesPolicies.md","specifications/SimulationSpecification_v6.md",
                 H+"n3-redemption-allocation-request-20261125/SPE_Work_N3_Redemption_Allocation_Sensitivity_Request_20261125.md",
                 ACCOUNTS+"N3_Central_Local_Official_Account_Map.csv",
                 ACCOUNTS+"N3_Central_Local_Cash_Asset_Inventory.csv",
                 AUTH+"N3_Central_Local_Financing_Legal_Authority_Map.csv",
                 AUTH+"N3_GI_Expenditure_Financing_Eligibility.csv",
                 EXEC+"N3_GI_Executor_Financing_Eligibility_Map.csv",
                 EXEC+"Conditional_Executor_Routing_Inputs.json",
                 NATIVE+"Resolved_Separation_Runtime.py.txt",
                 ASSUME+"Sensitivity_Runtime.py",
                 H+"n3-gdp-gap-causal-attribution-20261123/Attribution_Runtime.py",
                 H+"national-fiscal-closure-20261121/National_Fiscal.py"):
        raw(PIN,path)
    runtime_path=root/BASE/"Runtime.py"
    runtime=load_module("fixed_risk_runtime",runtime_path)
    draft=work/"draft"/runtime.DRAFT
    draft.parent.mkdir(parents=True)
    draft.write_bytes(raw(runtime.DRAFT_PIN,runtime.DRAFT))
    events=read(PRE,H+"common-macro-gdp-attribution-20261124/Event_Schedule.csv")
    event_list=[(int(r["year"]),k,float(r[k])) for r in events
                for k in ("conflict","earthquake","disaster","climate") if float(r[k])]
    fixed={(r["condition"],r["case"],int(r["year"])):r for r in read(DYN,BASE+"Annual.csv")}
    fiscal={(r["condition"],int(r["year"])):r for r in read(DYN,BASE+"Fiscal_Residual.csv") if r["case"]=="N3"}
    prices=[float(fixed["C","N3",y]["price_coefficient"]) for y in YEARS]
    annual, bridge, treasury, summary=[],[],[],[]

    def prepare(mode):
        factors=[math.prod(1-loss*max(0.,1-(y-start)/(5 if k in ("earthquake","conflict") else (1 if mode=="C" else 2)))
                           for start,k,loss in event_list if start<=y) for y in YEARS]
        for j,y in enumerate(YEARS):
            close("frozen_factor",factors[j],float(fixed[mode,"N3",y]["risk_factor"]))
            close("fixed_common_price",prices[j],float(fixed[mode,"N3",y]["price_coefficient"]))
        capture_dir=work/("capture_"+mode)
        capture_dir.mkdir()
        inputs=capture_dir/"Inputs.json"
        save(inputs,dict(factors=factors,prices=prices))
        subprocess.run([sys.executable,"-B",str(root/BASE/"Run.py"),"--worker","common_n3",
                        "--root",str(root),"--outdir",str(capture_dir),"--input",str(inputs),
                        "--draft",str(work/"draft")],check=True)
        sq,n3,*_=json.loads((capture_dir/"common_n3.json").read_bytes())
        return dict(records=sq+n3),sq[0]["case"],n3[0]["case"]

    def case(mode, data, rate, route, authorized=False):
        capture,sq,native=data
        label="AUTHORITY_LOWER_BOUND" if authorized else f"R{int(rate*100):03d}_{route}"
        fixed_fin={y:fiscal[mode,y] for y in YEARS}
        a,f,mid,nc,count,alloc=allocate(root,work/(mode+"_"+label),runtime_path,capture,sq,native,
                                        prices,fixed_fin,rate,route,authorized)
        checks["inherited_dynamic_run_checks"]+=count
        rows=[]
        for i,y in enumerate(YEARS):
            v,b,l=a[i],f[i],alloc[y]
            reference=fixed[mode,"N3",y]
            s=fixed[mode,"SQ",y]
            ff=fixed[mode,"F",y]
            Y,N=v["real_GDP_trn"],v["nominal_GDP_trn"]
            gap=Y-float(s["real_gdp_trn"])
            pop=float(reference["population"])
            d=prices[i]
            base_core=float(reference["core_real_gdp_trn"])
            pressure=.5*v["unmet_demand_real_trn"]/base_core
            if authorized:
                for kind,value in (("real_gdp_trn",Y),("nominal_gdp_trn",N),("tax_diagnostic_trn",v["total_tax_diagnostic_proxy_trn"])):
                    close("authority_matches_fixed",value,float(reference[kind]))
                for kind,value in (("CL_PB_trn",b["PB_trn"]),("CL_debt_trn",b["debt_end_trn"]),
                                    ("CL_interest_trn",b["interest_trn"]),("CL_cash_assets_trn",b["assets_end_trn"])):
                    close("authority_fiscal_matches_fixed",value,float(fixed_fin[y][kind]))
            close("cash_allocation_closure",l["released_hypothetical_cash_trn"],
                  l["spending_G_nominal_trn"]+l["spending_I_nominal_trn"]+l["unallocated_retained_trn"])
            check("live_cut_cap",0.<=l["released_hypothetical_cash_trn"]<=
                  min(l["requested_cut_trn"],l["modeled_slice_trn"])+1e-10)
            check("no_rollover_policy_change",b["rollover_share"]==float(fixed_fin[y]["CL_rollover_share"]))
            close("matched_rollover_both_sides",l["gross_issue_trn"]-b["new_cash_borrowing_trn"],
                  l["gross_redemption_trn"]-l["actual_cash_redemption_trn"])
            close("GDP_cap",Y,min(v["desired_real_GDP_trn"],v["supply_ceiling_real_trn"]))
            close("nominal_identity",N,Y*d*(1+pressure))
            close("tax_not_counted_twice",v["macro_tax_proxy_trn"]-l["no_spend_tax_trn"],
                  l["extra_same_year_tax_vs_no_spend_trn"])
            close("debt_stock",b["debt_end_trn"],b["debt_begin_trn"]+b["new_cash_borrowing_trn"]-
                  l["actual_cash_redemption_trn"]+b["SFA_remaining_adjustment_trn"])
            if i:
                close("carry_debt",b["debt_begin_trn"],f[i-1]["debt_end_trn"])
                close("carry_assets",b["assets_begin_trn"],f[i-1]["assets_end_trn"])
            else:
                close("initial_GDP",Y,580.)
                close("initial_nominal",N,600.)
            scope="EVIDENCE_LOWER_BOUND_ZERO" if authorized else "UNAUTHORIZED_HYPOTHETICAL"
            key=dict(condition=mode,scenario=label,year=y,scope=scope)
            rows.append(dict(**key,requested_cut_share=rate,route=route,
                             real_gdp_trn=Y,nominal_gdp_trn=N,population=pop,real_pc_yen=Y*1e12/pop,
                             nominal_pc_yen=N*1e12/pop,price_coefficient=d,price_pressure=pressure,
                             deflator_index=100*N/Y/runtime.D0,
                             sq_fixed_real_trn=float(s["real_gdp_trn"]),sq_fixed_nominal_trn=float(s["nominal_gdp_trn"]),
                             f_fixed_real_trn=float(ff["real_gdp_trn"]),f_fixed_nominal_trn=float(ff["nominal_gdp_trn"]),
                             real_minus_SQ_trn=gap,real_minus_F_trn=Y-float(ff["real_gdp_trn"]),
                             real_delta_vs_fixed_N3_trn=Y-float(reference["real_gdp_trn"]),
                             tax_diagnostic_trn=v["total_tax_diagnostic_proxy_trn"],
                             tax_change_vs_fixed_N3_trn=v["total_tax_diagnostic_proxy_trn"]-float(reference["tax_diagnostic_trn"]),
                             desired_real_trn=v["desired_real_GDP_trn"],capacity_real_trn=v["supply_ceiling_real_trn"],
                             unmet_real_trn=v["unmet_demand_real_trn"],PB_candidate_trn=b["PB_trn"],
                             interest_candidate_trn=b["interest_trn"],debt_end_candidate_trn=b["debt_end_trn"],
                             debt_nominal_GDP_pct=100*b["debt_end_trn"]/N,
                             cash_assets_candidate_trn=b["assets_end_trn"],SFA_trn=b["SFA_trn"],
                             cash_borrowing_candidate_trn=b["new_cash_borrowing_trn"],
                             G_nominal_trn=l["spending_G_nominal_trn"],I_nominal_trn=l["spending_I_nominal_trn"]))
            bridge.append(dict(**key,**{k:x for k,x in l.items() if k!="year"},
                               G_domestic_real_trn=v["GDP_G_domestic_trn"],I_domestic_real_trn=v["extra_public_investment_real_trn"],
                               G_I_import_proxy_trn=b["government_import_leak_trn"],
                               capital_supply_real_trn=v["supply_real_trn"],
                               approved_central_gi_trn=NA,approved_local_gi_trn=NA))
            treasury.append(dict(**key,PB_candidate_trn=b["PB_trn"],interest_candidate_trn=b["interest_trn"],
                                 debt_begin_trn=b["debt_begin_trn"],debt_end_trn=b["debt_end_trn"],
                                 debt_delta_vs_fixed_trn=b["debt_end_trn"]-float(fixed_fin[y]["CL_debt_trn"]),
                                 interest_delta_vs_fixed_trn=b["interest_trn"]-float(fixed_fin[y]["CL_interest_trn"]),
                                 PB_delta_vs_fixed_trn=b["PB_trn"]-float(fixed_fin[y]["CL_PB_trn"]),
                                 SFA_unallocated_trn=b["SFA_remaining_adjustment_trn"],assets_begin_trn=b["assets_begin_trn"],
                                 assets_end_trn=b["assets_end_trn"],asset_draw_trn=b["asset_draw_trn"],asset_add_trn=b["asset_addition_trn"],
                                 cash_borrowing_candidate_trn=b["new_cash_borrowing_trn"],
                                 requested_cash_not_released_trn=l["requested_unavailable_trn"],
                                 assumed_rollover_trn=l["actual_rollover_trn"],national_PB=NA,national_debt=NA))
        annual.extend(rows)
        rank=[r for r in rows if r["year"]>2026 and r["real_minus_SQ_trn"]>1e-7]
        sustained=next((r["year"] for j,r in enumerate(rows[1:],1)
                        if all(t["real_minus_SQ_trn"]>1e-7 for t in rows[j:])),NA)
        end=rows[-1]
        peak=max(rows[1:],key=lambda r:r["real_minus_SQ_trn"])
        entry=dict(condition=mode,scenario=label,scope=scope,rate=rate,route=route,
                   first_overtake_year=rank[0]["year"] if rank else NA,sustained_overtake_year=sustained,
                   best_gap_year=peak["year"],best_annual_real_gap_trn=peak["real_minus_SQ_trn"],
                   real_2055_trn=end["real_gdp_trn"],nominal_2055_trn=end["nominal_gdp_trn"],
                   real_gap_2055_trn=end["real_minus_SQ_trn"],cumulative_real_gap_trn_years=sum(r["real_minus_SQ_trn"] for r in rows),
                   cumulative_gain_vs_fixed_N3_trn_years=sum(r["real_delta_vs_fixed_N3_trn"] for r in rows),
                   requested_total_trn=sum(l["requested_cut_trn"] for l in alloc.values()),
                   released_total_trn=sum(l["released_hypothetical_cash_trn"] for l in alloc.values()),
                   spent_total_trn=sum(l["spending_G_nominal_trn"]+l["spending_I_nominal_trn"] for l in alloc.values()),
                   retained_total_trn=sum(l["unallocated_retained_trn"] for l in alloc.values()),
                   unavailable_total_trn=sum(l["requested_unavailable_trn"] for l in alloc.values()),
                   peak_debt_trn=max(r["debt_end_candidate_trn"] for r in rows),
                   debt_2055_trn=end["debt_end_candidate_trn"],interest_2055_trn=end["interest_candidate_trn"],
                   PB_2055_trn=end["PB_candidate_trn"])
        summary.append(entry)
        return entry

    c=prepare("C")
    executable=case("C",c,0.,"HOLD",True)
    exploratory=[]
    for rate in (.25,.5,.75,1.):
        for route in ("G","I","MIX"):
            exploratory.append(case("C",c,rate,route))
    case("C",c,.5,"HOLD")
    # Use observed regimes only. Refine any no-overtake/overtake brackets
    # with at most six additional paths, keeping all tested outcomes.
    extra=0
    for route in ("G","I","MIX"):
        route_rows=[dict(rate=0.,first_overtake_year=executable["first_overtake_year"])]
        route_rows.extend(sorted((r for r in exploratory if r["route"]==route),key=lambda r:r["rate"]))
        intervals=[(a,b) for a,b in zip(route_rows,route_rows[1:]) if
                   (a["first_overtake_year"]==NA)!=(b["first_overtake_year"]==NA)]
        for lo,hi in intervals:
            for _ in range(2):
                if extra>=6:
                    break
                mid=round((lo["rate"]+hi["rate"])/2,2)
                if not lo["rate"]<mid<hi["rate"]:
                    break
                result=case("C",c,mid,route)
                exploratory.append(result)
                extra+=1
                if (result["first_overtake_year"]==NA)==(lo["first_overtake_year"]==NA):
                    lo=result
                else:
                    hi=result
    d=prepare("D")
    case("D",d,0.,"HOLD",True)
    best=max(exploratory,key=lambda r:r["real_gap_2055_trn"])
    case("D",d,best["rate"],best["route"])
    crossing=[x for x in exploratory if x["first_overtake_year"]!=NA]
    if crossing:
        nearest=min(crossing,key=lambda x:(x["rate"],-x["best_annual_real_gap_trn"]))
        if nearest["scenario"]!=best["scenario"]:
            case("D",d,nearest["rate"],nearest["route"])
    grouped=Counter((r["condition"],r["scenario"]) for r in annual)
    check("complete_grid_years",len(grouped)==len(summary) and set(grouped.values())=={30})
    for name,rows in (("Annual.csv",annual),("Key_Years.csv",[r for r in annual if r["year"] in KEYS]),
                      ("Scenario_Comparison.csv",summary),("Allocation_Bridge.csv",bridge),("Fiscal_Residual.csv",treasury)):
        dump(out/name,rows)
    save(out/"Dependencies.json",dict(runtime_commit=PIN,tree=git("rev-parse","HEAD^{tree}").decode().strip(),
                                      sources=list(deps.values())))
    save(out/"Validation.json",dict(status="PASS",new_checks=sum(checks.values()),groups=dict(sorted(checks.items())),
                                    new_rows=len(annual)-60,reproduced_evidence_control_rows=60,extra_boundary_branches=extra,
                                    fixed_F_SQ_N3_source_rows_reused=180))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",required=True,type=Path)
    parser.add_argument("--outdir",required=True,type=Path)
    args=parser.parse_args()
    with tempfile.TemporaryDirectory() as folder:
        work=Path(folder)
        execute(args.root.resolve(),args.outdir,work/"first")
        other=work/"outputs"
        execute(args.root.resolve(),other,work/"second")
        matches=sorted(x.name for x in other.iterdir())
        for name in matches:
            if (other/name).read_bytes()!=(args.outdir/name).read_bytes():
                raise ValueError(f"non-reproducible: {name}")
    data=json.loads((args.outdir/"Validation.json").read_bytes())
    data["rerun_byte_identical"]=matches
    save(args.outdir/"Validation.json",data)
