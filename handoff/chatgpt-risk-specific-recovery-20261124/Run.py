"""Risk-duration sensitivity using fixed previous real-GDP diagnostic states."""
import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

PIN = "adb373d87c5beb68b35f84be9e504c84d67014e0"
REQUEST = "6ad7922f9b5c7b582044076842a0d28f653f7647"
PRE = "handoff/chatgpt-common-macro-gdp-attribution-20261124/"
YEARS = range(2026, 2056)
CASES = ("F", "SQ", "N3")
MODES = ("A", "B", "C", "D")
KINDS = ("conflict", "earthquake", "disaster", "climate")


def run(root, out):
    out.mkdir(parents=True, exist_ok=True)
    checks, deps = Counter(), {}

    def check(group, ok):
        if not ok:
            raise ValueError(group)
        checks[group] += 1

    def close(group, a, b):
        check(group, math.isclose(a, b, abs_tol=1e-8, rel_tol=1e-11))

    def raw(commit, path):
        data = subprocess.check_output(["git", "-C", str(root), "show", f"{commit}:{path}"])
        deps[path] = dict(commit=commit, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        return data

    def csvread(path):
        return list(csv.DictReader(io.StringIO(raw(PIN, PRE+path).decode())))

    def dump(name, rows):
        with (out/name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)

    def save(name, value):
        (out/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n")

    receipt = json.loads(raw(PIN, PRE+"Custody.json"))
    validation = json.loads(raw(PIN, PRE+"Validation.json"))
    check("prior_pass", receipt["status"]=="CUSTODY PASS" and validation["status"]=="PASS")
    old = csvread("Counterfactual_Annual.csv")
    schedule = csvread("Event_Schedule.csv")
    recovery = csvread("Recovery_Events.csv")
    raw(PIN, PRE+"Run.py")
    prior_deps = json.loads(raw(PIN, PRE+"Dependencies.json"))
    sq_path = prior_deps["sq"]["path"]
    sq_pin = prior_deps["sq"]["commit"]
    p = json.loads(raw(sq_pin, sq_path))["parameters"]
    g, slack = p["base_growth"], p["slack"]
    check("parameters", g==.01 and slack==.02 and not p["apply_oil_to_initial"])
    for f in receipt["files"]:
        if f["path"] in deps:
            check("prior_bytes", deps[f["path"]]["sha256"]==f["sha256"] and deps[f["path"]]["bytes"]==f["bytes"])
    paths = subprocess.check_output(["git","-C",str(root),"ls-tree","-r","--name-only",REQUEST,"policies","specifications"],text=True).splitlines()
    for path in paths:
        raw(REQUEST, path)
    raw(REQUEST,"handoff/chatgpt-risk-specific-recovery-request-20261124/SPE_Work_Risk_Specific_Recovery_Sensitivity_Request_20261124.md")
    check("schedule_years", [int(r["year"]) for r in schedule]==list(YEARS))
    events = [(int(r["year"]),k,float(r[k])) for r in schedule for k in KINDS if float(r[k])]
    check("initial_oil_off", schedule[0]["oil_scheduled"]=="True" and all(r["oil_applied"]=="False" for r in schedule))
    old_rec = {(int(r["year"]),int(r["event_year"]),r["kind"]):float(r["remaining_loss"]) for r in recovery}
    original = {(int(r["year"]),r["scenario"],r["mode"]):r for r in old}
    check("prior_unique", len(original)==len(old))
    duration = {"B":dict.fromkeys(KINDS,5),
                "C":dict(conflict=5,earthquake=5,disaster=1,climate=1),
                "D":dict(conflict=5,earthquake=5,disaster=2,climate=2)}
    annual, event_rows, contributions, gaps = [], [], [], []
    for y in YEARS:
        factors = {}
        for mode, periods in duration.items():
            pieces = []
            for start, kind, loss in events:
                if start>y:
                    continue
                n = periods[kind]
                residual = loss*max(0.,1-(y-start)/n)
                check("recovery_boundary", 0<=residual<=loss and (y!=start or residual==loss) and (y-start<n or residual==0))
                if mode=="B":
                    close("prior_B_event", residual, old_rec[y,start,kind])
                pieces.append(1-residual)
                event_rows.append(dict(year=y,mode=mode,event_year=start,kind=kind,duration=n,loss=loss,remaining=residual,multiplier=1-residual))
            factors[mode] = math.prod(pieces)
        factors["A"] = math.prod((1+g-float(r["total"]))/(1+g) for r in schedule[1:y-2026+1])
        for case in CASES:
            a = original[y,case,"CURRENT"]
            b = original[y,case,"RECOVERY_5Y"]
            no_risk = float(original[y,case,"REAL_RISK_OFF"]["core"])
            current = float(a["real_gdp"])
            base_core = float(a["core"])
            desired_delta = float(a["desired"])-base_core
            capacity_delta = float(a["capacity"])-base_core*(1+slack)
            pop = float(a["population"])

            def calculate(factor):
                core = no_risk*factor
                desired = core+desired_delta
                capacity = core*(1+slack)+capacity_delta
                return core,desired,capacity,min(desired,capacity)

            values = {}
            for mode in MODES:
                core,desired,capacity,gdp = calculate(factors[mode])
                if mode in ("A","B"):
                    prior = a if mode=="A" else b
                    for col,num in (("core",core),("desired",desired),("capacity",capacity),("real_gdp",gdp)):
                        close("prior_AB_reconstruction", num, float(prior[col]))
                    core,desired,capacity,gdp = (float(prior[k]) for k in ("core","desired","capacity","real_gdp"))
                check("capacity", gdp<=capacity+1e-8 and gdp<=desired+1e-8)
                if y==2026:
                    close("initial",gdp,580.)
                pc = gdp*1e12/pop
                close("per_capita",pc*pop/1e12,gdp)
                values[mode]=gdp
                annual.append(dict(year=y,scenario=case,mode=mode,origin="REUSED" if mode in ("A","B") else "NEW",risk_multiplier=factors[mode],core=core,desired=desired,capacity=capacity,unmet=desired-gdp,real_gdp=gdp,population=pop,real_gdp_per_capita_yen=pc,change_vs_A=gdp-current,change_vs_B=gdp-float(b["real_gdp"])))
            for mode in ("C","D"):
                # Sequential B -> shorter disaster -> shorter climate, with interaction assigned to climate.
                hybrid=math.prod(1-loss*max(0.,1-(y-start)/(duration[mode][kind] if kind=="disaster" else 5)) for start,kind,loss in events if start<=y)
                intermediate=calculate(hybrid)[-1]
                d=intermediate-values["B"]
                c=values[mode]-intermediate
                close("risk_contribution",d+c,values[mode]-values["B"])
                contributions.append(dict(year=y,scenario=case,mode=mode,disaster=d,climate=c,total=values[mode]-values["B"],order="disaster_then_climate"))
    idx={(r["year"],r["scenario"],r["mode"]):r for r in annual}
    check("annual_complete",len(idx)==len(annual)==360)
    for y in YEARS:
        for mode in MODES:
            f,s,n=(idx[y,case,mode]["real_gdp"] for case in CASES)
            close("gap",f-s,(f-n)+(n-s))
            gaps.append(dict(year=y,mode=mode,F=f,SQ=s,N3=n,F_minus_SQ=f-s,N3_minus_SQ=n-s,F_minus_N3=f-n))
    summary=[]
    for case in CASES:
        for mode in MODES:
            rows=[idx[y,case,mode] for y in YEARS]
            recovery_year=next((r["year"] for r in rows[1:] if r["real_gdp"]>=580),"N/A")
            sustained=next((r["year"] for i,r in enumerate(rows[1:],1) if all(t["real_gdp"]>=580 for t in rows[i:])),"N/A")
            summary.append(dict(scenario=case,mode=mode,first_recovery_year=recovery_year,sustained_recovery_year=sustained,
                                GDP_2055=rows[-1]["real_gdp"],per_capita_2055=rows[-1]["real_gdp_per_capita_yen"],
                                cumulative_gdp=sum(r["real_gdp"] for r in rows),
                                cumulative_vs_A=sum(r["change_vs_A"] for r in rows),cumulative_vs_B=sum(r["change_vs_B"] for r in rows)))
    dump("Annual.csv",annual)
    dump("Event_Recovery.csv",event_rows)
    dump("Risk_Contribution.csv",contributions)
    dump("Policy_Gaps.csv",gaps)
    dump("Summary.csv",summary)
    dump("Key_Years.csv",[r for r in annual if r["year"] in (2026,2030,2035,2045,2055)])
    save("Dependencies.json",deps)
    save("Validation.json",dict(status="PASS",checks=sum(checks.values()),groups=dict(sorted(checks.items())),failures=0,new_rows=180,reused_rows=180,prior_checks_reused=validation["checks"]))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--outdir",type=Path,required=True)
    args=parser.parse_args()
    run(args.root,args.outdir)
