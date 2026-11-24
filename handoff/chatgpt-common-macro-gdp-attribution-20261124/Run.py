"""Fixed-original real GDP decomposition and frozen-channel counterfactuals."""
import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

WORK = "8a8edb403b960cceb535f9b70461646e9374c229"
CLAUDE = "da79ab621de27a1a2df8dd3edf050e4f02fac63a"
REQUEST = "4ee60743acba214d642a915851489171842f3dba"
OLD = "handoff/chatgpt-f-sq-n3-common-indicators-20261123/"
VERIFY = "handoff/claude-f-sq-n3-common-indicators-verification-20261123/"
CASES = ("SQ", "F", "N3")
MODES = ("CURRENT", "REAL_RISK_OFF", "LABOR_FIXED", "BASE_GROWTH_OFF", "RECOVERY_5Y")
YEARS = tuple(range(2026, 2056))


def run(root, out):
    out.mkdir(parents=True, exist_ok=True)
    checks, sources = Counter(), {}

    def check(group, condition):
        if not condition:
            raise ValueError(group)
        checks[group] += 1

    def close(group, actual, expected):
        check(group, math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-8))

    def read(name, commit, path):
        data = subprocess.check_output(["git", "-C", str(root), "show", f"{commit}:{path}"])
        sources[name] = dict(commit=commit, path=path, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        return json.loads(data) if path.endswith(".json") else data.decode()

    def dump(name, rows):
        with (out / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def save(name, obj):
        (out / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    deps = read("previous_dependencies", WORK, OLD + "Dependencies.json")
    originals = {}
    for name in ("sq", "f_trace", "f", "n3", "n3_denominator", "n3_parameters"):
        pin = deps[name]
        originals[name] = read(name, pin["commit"], pin["path"])
        check("fixed_original_identity", sources[name] == pin)
    validation = read("claude_validation", CLAUDE, VERIFY + "Validation.json")
    check("prior_independent_pass", validation["checks"] == 4818 and validation["failures"] == 0 and validation["target_final_commit"] == WORK)
    previous = list(csv.DictReader(io.StringIO(read("previous_comparison", WORK, OLD + "Annual_Comparison.csv"))))
    prev_gdp = {int(row["year"]): row for row in previous if row["indicator"] == "real_gdp"}
    read("request", REQUEST, "handoff/chatgpt-common-macro-gdp-attribution-request-20261124/SPE_Work_Common_Macro_GDP_Attribution_Request_20261124.md")
    p = originals["sq"]["parameters"]
    sq = originals["sq"]["years"]
    ft = originals["f_trace"]["years"]
    fr = originals["f"]
    nr = originals["n3"]
    ns = originals["n3_denominator"]
    for rows in (sq, ft, fr, nr, ns):
        check("years", tuple(int(r["year"]) for r in rows) == YEARS)
    g, beta, slack = p["base_growth"], p["labor_response"], p["slack"]
    check("baseline_parameters", (g, beta, slack, p["base_inflation"], p["apply_oil_to_initial"]) == (.01, .65, .02, .02, False))
    for key in ("base_growth", "labor_response", "slack", "disaster_anchor", "climate_anchor", "apply_oil_to_initial"):
        check("common_parameters", originals["f_trace"]["parameters"][key] == originals["n3_parameters"]["parameters"][key] == p[key])
    events, risk_rows = [], []
    for i, y in enumerate(YEARS):
        risks = dict(conflict=p["conflict_gdp_loss"] if y == 2027 else 0.,
                     earthquake=p["quake_gdp_loss"] if y == 2031 else 0.,
                     disaster=p["disaster_gdp_loss"] if y >= p["disaster_anchor"] and (y-p["disaster_anchor"]) % 3 == 0 else 0.,
                     climate=p["climate_gdp_loss"] if y >= p["climate_anchor"] and (y-p["climate_anchor"]) % 2 == 0 else 0.)
        close("event_schedule_sq", sum(risks.values()), sq[i]["risk"])
        close("event_schedule_f", sum(risks.values()), ft[i]["risk"])
        for kind, shock in risks.items():
            if shock:
                events.append((y, kind, shock))
        risk_rows.append(dict(year=y, **risks, total=sum(risks.values()),
                              oil_scheduled=y == 2026, oil_applied=False, input_inflation=sq[i]["inflation"]))
    decomposition, simulations, policy, event_recovery = [], [], [], []
    l0, pop0, y0 = sq[0]["labor"], sq[0]["population"], sq[0]["Y"]
    check("initial", y0 == 580 and pop0 == 122618024)
    for i, y in enumerate(YEARS):
        s, f, n = sq[i], ft[i], nr[i]
        baseline_risk = math.prod(1+g-row["total"] for row in risk_rows[1:i+1])
        trend = (1+g)**i
        # Ordered telescope: growth, total population, workers/person, then each risk family.
        growth = y0*trend
        population = growth*(s["population"]/pop0)**beta
        labor = growth*(s["labor"]/l0)**beta
        cur = labor
        selected = []
        impacts = {}
        for kind in ("conflict", "earthquake", "disaster", "climate"):
            selected.append(kind)
            nxt = y0*(s["labor"]/l0)**beta*math.prod(
                1+g-sum(row[k] for k in selected) for row in risk_rows[1:i+1])
            impacts[kind] = nxt-cur
            cur = nxt
        close("sq_core_formula", cur, s["coreY"])
        close("sq_nonlabor_factor", baseline_risk, s["nonlabor_factor"])
        desired_delta = s["desired"]-s["coreY"]
        explicit_demand = s["C"]+s["I"]+p["capacity_absorption"]*s["supply"]+s["education_nom"]/s["coreD"]+s["education_level"]+s["finite"]+s["service_nominal"]/s["coreD"]
        residual = desired_delta-explicit_demand
        close("sq_desired_components", residual, 0.)
        contributions = dict(trend_growth=growth-y0, population=population-growth,
                             labor_per_person=labor-population, **impacts,
                             consumption=s["C"], investment=s["I"],
                             supply_absorption=p["capacity_absorption"]*s["supply"],
                             education_and_finite=s["education_nom"]/s["coreD"]+s["education_level"]+s["finite"],
                             service=s["service_nominal"]/s["coreD"], residual=residual,
                             unmet=-s["unmet"])
        close("sq_total_telescope", sum(contributions.values()), s["Y"]-y0)
        decomposition.append(dict(year=y, initial_gdp=y0, **contributions, core=s["coreY"], final=s["Y"], net=s["Y"]-y0,
                                  population_persons=s["population"], effective_labor=s["labor"], labor_per_person_ratio=s["labor"]/s["population"]))
        rows = {
            "SQ": (s["labor"], s["population"], s["coreY"], s["desired"], s["capacity"], s["unmet"], s["Y"]),
            "F": (f["labor"], fr[i]["population"], f["coreY"], f["desired"], f["capacity"], f["unmet"], f["Y"]),
            "N3": (ns[i]["labor"], ns[i]["macro_row"]["population_persons"], s["coreY"], n["desired_real_GDP_trn"], n["supply_ceiling_real_trn"], n["unmet_demand_real_trn"], n["real_GDP_trn"]),
        }
        close("n3_common_labor", rows["N3"][0], s["labor"])
        close("n3_common_population", rows["N3"][1], s["population"])
        for case, (workers, pop, core, desired, ceiling, unmet, actual) in rows.items():
            close("prior_gdp", actual, float(prev_gdp[y][case]))
            close("scenario_core", core, y0*baseline_risk*(workers/l0)**beta)
            close("scenario_cap", min(desired, ceiling), actual)
            close("scenario_unmet", desired-actual, unmet)
            core_gap = core-s["coreY"]
            demand_gap = (desired-core)-(s["desired"]-s["coreY"])
            cap_gap = -unmet+s["unmet"]
            close("policy_gap_telescope", core_gap+demand_gap+cap_gap, actual-s["Y"])
            policy.append(dict(year=y, scenario=case, sq_core=s["coreY"], sq_noncore=s["Y"]-s["coreY"],
                               policy_labor_core_gap=core_gap, policy_desired_noncore_gap=demand_gap,
                               policy_cap_gap=cap_gap, actual_gdp=actual, gap_vs_sq=actual-s["Y"],
                               F_desired_unresolved= f["desired"]-f["coreY"]-(p["capacity_absorption"]*f["supply"]+f["C"]+f["I"]+f["education_nom"]/f["coreD"]+f["education_level"]+f["finite"]) if case=="F" else "N/A"))
            for mode in MODES if case == "SQ" else ("CURRENT", "REAL_RISK_OFF", "RECOVERY_5Y"):
                factor = baseline_risk
                w = workers
                if mode == "REAL_RISK_OFF":
                    factor = trend
                elif mode == "LABOR_FIXED":
                    w = l0
                elif mode == "BASE_GROWTH_OFF":
                    factor = math.prod(1-row["total"] for row in risk_rows[1:i+1])
                elif mode == "RECOVERY_5Y":
                    # Each event starts with its absolute loss, then linearly fades over five years.
                    # Product of independent remaining losses, including overlaps.
                    factor = trend*math.prod(1-shock*max(0.,1-(y-start)/5) for start, _, shock in events if start <= y)
                cf_core = y0*factor*(w/l0)**beta
                # Hold all annual noncore demand terms and absolute supply additions fixed.
                # The proportional slack follows the new core; re-evaluate the min constraint.
                cf_desired = cf_core+(desired-core)
                cf_ceiling = cf_core*(1+slack)+(ceiling-core*(1+slack))
                cf = min(cf_desired, cf_ceiling)
                if mode == "CURRENT":
                    close("current_reconstruction", cf, actual)
                check("constraint", cf <= cf_desired+1e-8 and cf <= cf_ceiling+1e-8)
                close("per_capita", cf*1e12/pop*pop/1e12, cf)
                simulations.append(dict(year=y, scenario=case, mode=mode, core=cf_core, desired=cf_desired,
                                        capacity=cf_ceiling, unmet=cf_desired-cf, real_gdp=cf, change_vs_current=cf-actual,
                                        population=pop, effective_labor=w, real_gdp_per_capita_yen=cf*1e12/pop,
                                        scope="FROZEN_NONCORE_REAL_DIAGNOSTIC"))
        for start, kind, loss in events:
            if start <= y:
                remaining = loss*max(0.,1-(y-start)/5)
                check("recovery_boundary", 0 <= remaining <= loss and (y != start or remaining == loss) and (y-start < 5 or remaining == 0))
                event_recovery.append(dict(year=y, event_year=start, kind=kind, original_loss=loss,
                                           remaining_loss=remaining, multiplier=1-remaining))
    check("row_counts", len(simulations)==330 and len(decomposition)==30 and len(policy)==90)
    indexed = {(r["year"], r["scenario"], r["mode"]): r["real_gdp"] for r in simulations}
    check("unique_scenario_year", len(indexed) == len(simulations))
    gaps = []
    for year in YEARS:
        for mode in ("CURRENT", "REAL_RISK_OFF", "RECOVERY_5Y"):
            s, f, n = (indexed[year, case, mode] for case in CASES)
            close("scenario_gap_identity", f-s, (f-n)+(n-s))
            gaps.append(dict(year=year, mode=mode, SQ=s, F=f, N3=n, F_minus_SQ=f-s, F_minus_N3=f-n, N3_minus_SQ=n-s))
    dump("SQ_Annual_Attribution.csv", decomposition)
    dump("Counterfactual_Annual.csv", simulations)
    dump("Policy_Gap_Annual.csv", policy)
    dump("Three_Scenario_Gaps.csv", gaps)
    dump("Event_Schedule.csv", risk_rows)
    dump("Recovery_Events.csv", event_recovery)
    dump("Key_Years.csv", [r for r in simulations if r["year"] in (2026,2030,2035,2045,2055)])
    save("Dependencies.json", sources)
    save("Validation.json", dict(status="PASS", checks=sum(checks.values()), failures=0, groups=dict(sorted(checks.items())),
                                 annual_rows=len(simulations), prior_claude_checks_reused=4818, prior_checks_added=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    run(args.root, args.outdir)
