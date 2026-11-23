"""SPE F/SQ/N3 common indicators - Claude independent recalculation (DRAFT, read-only).

Usage:
  python3 -I SPE_Common_Indicators_Independent_Recalc_DRAFT_20261123.py BARE_GIT_DIR RERUN_DIR OUTDIR [MUTATION_DIR]

BARE_GIT_DIR : git dir already holding the fixed commits (fetched by SHA).
RERUN_DIR    : output dir of Work's Run.py executed by the verifier (auxiliary reproducibility only).
OUTDIR       : where this script writes its CSV/JSON.

Independence: does NOT import or call Work's Run.py. Inputs are read from the immutable
dependency objects (git show <commit>:<path>); the SQ/F/N3 common core, event calendar, price index,
Y/N identities and every derived indicator are re-derived here from the parameters, population and
labour series. Work's Validation.json / Custody.json are not used as evidence.
"""
import csv, hashlib, io, json, math, os, re, subprocess, sys
from collections import Counter

BARE, RERUN, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MUT = sys.argv[4] if len(sys.argv) > 4 else None   # optional: detection-power test only (overrides delivered files)
FINAL = "8a8edb403b960cceb535f9b70461646e9374c229"
PAYLOAD = "7c9d33205297365e5c6536a84e302eff1d26a3fc"
D = "handoff/chatgpt-f-sq-n3-common-indicators-20261123/"
YEARS = list(range(2026, 2056))
os.makedirs(OUT, exist_ok=True)

def show(c, p):
    if MUT and c == "8a8edb403b960cceb535f9b70461646e9374c229" and os.path.exists(os.path.join(MUT, os.path.basename(p))):
        return open(os.path.join(MUT, os.path.basename(p)), "rb").read()
    return subprocess.check_output(["git", "-C", BARE, "show", f"{c}:{p}"])
def tree(c, d):
    return subprocess.check_output(["git", "-C", BARE, "ls-tree", "-r", "--name-only", c, d]).decode().split()
def blob(c, p):
    return subprocess.check_output(["git", "-C", BARE, "rev-parse", f"{c}:{p}"]).decode().strip()
def sha(b):
    return hashlib.sha256(b).hexdigest()
def csvrows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))

LOG = []   # (group, id, expected, actual, abs_diff, ok)
counts = Counter(); fails = Counter()
def rec(group, ident, exp, act, ok, diff=""):
    LOG.append((group, ident, exp, act, diff, ok)); counts[group] += 1
    if not ok: fails[group] += 1
def eq(group, ident, a, b):
    rec(group, ident, a, b, a == b)
def near(group, ident, exp, act, atol=1e-9, rtol=1e-11):
    d = abs(float(exp) - float(act))
    rec(group, ident, exp, act, d <= atol + rtol * abs(float(exp)), d)
def flag(group, ident, cond, note=""):
    rec(group, ident, note, "", bool(cond))

# ---------------------------------------------------------------- A. custody
files_final = tree(FINAL, D); files_pay = tree(PAYLOAD, D)
eq("A_custody", "dir_files_final", 13, len(files_final))
eq("A_custody", "dir_files_payload", 12, len(files_pay))
eq("A_custody", "final_minus_payload", [D + "Custody.json"], sorted(set(files_final) - set(files_pay)))
for p in files_pay:
    eq("A_custody", "payload_eq_final_blob:" + p.split("/")[-1], blob(PAYLOAD, p), blob(FINAL, p))
man = json.loads(show(FINAL, D + "Manifest.json"))
eq("A_custody", "manifest_count", 11, len(man["files"]))
for f in man["files"]:
    raw = show(FINAL, f["path"])
    eq("A_custody", "manifest_size:" + f["path"].split("/")[-1], f["bytes"], len(raw))
    eq("A_custody", "manifest_sha:" + f["path"].split("/")[-1], f["sha256"], sha(raw))
cus = json.loads(show(FINAL, D + "Custody.json"))
eq("A_custody", "custody_payload_commit", PAYLOAD, cus["payload_commit"])
for f in cus["files"]:
    raw = show(FINAL, f["path"])
    eq("A_custody", "custody_size:" + f["path"].split("/")[-1], f["bytes"], len(raw))
    eq("A_custody", "custody_sha:" + f["path"].split("/")[-1], f["sha256"], sha(raw))
dep = json.loads(show(FINAL, D + "Dependencies.json"))
eq("A_custody", "dependency_count", 17, len(dep))
for k, f in dep.items():
    raw = show(f["commit"], f["path"])
    eq("A_custody", f"dep_size:{k}", f["bytes"], len(raw))
    eq("A_custody", f"dep_sha:{k}", f["sha256"], sha(raw))
# Auxiliary rerun (Work Run.py executed by verifier): byte identity with delivered files
for fn in sorted(os.listdir(RERUN)):
    eq("A_rerun_aux", "rerun_bytes:" + fn, sha(show(FINAL, D + fn)), sha(open(os.path.join(RERUN, fn), "rb").read()))

# ---------------------------------------------------------------- inputs
def dj(name):
    f = dep[name]; return json.loads(show(f["commit"], f["path"]))
def dc(name):
    f = dep[name]; return csvrows(show(f["commit"], f["path"]))
sq_doc = dj("sq"); SQP = sq_doc["parameters"]
sq = {r["year"]: r for r in sq_doc["years"]}
f_doc = dj("f_trace"); ft = {r["year"]: r for r in f_doc["years"]}
fa = {r["year"]: r for r in dj("f")}
fo = {r["year"]: r for r in dj("f_before_reconnection")}
na = {r["year"]: r for r in dj("n3")}
nd = {r["year"]: r for r in dj("n3_denominator")}
n3p = dj("n3_parameters")["parameters"]
sqprior = {r["year"]: r for r in dj("sq_prior")["years"]}
nprior = {int(r["year"]): r for r in dc("n3_prior")}
fnat = {int(r["year"]): r for r in dc("f_fixed_native") if r["case"] == "LATEST_F"}
fh = dc("f_household")
prior_cmp = dc("prior_comparison")
for t in (sq, ft, fa, fo, na, nd):
    eq("B_inputs", "years_complete", YEARS, sorted(t))

# ---------------------------------------------------------------- B. parameters & event calendar (own derivation)
P = SQP
eq("B_params", "base_growth", 0.01, P["base_growth"])
eq("B_params", "base_inflation", 0.02, P["base_inflation"])
eq("B_params", "labor_response", 0.65, P["labor_response"])
eq("B_params", "slack", 0.02, P["slack"])
eq("B_params", "price_pressure_coefficient", 0.5, P["price_pressure_coefficient"])
eq("B_params", "apply_oil_to_initial", False, P["apply_oil_to_initial"])
for k in ("base_inflation", "oil_inflation_extra", "conflict_inflation_extra", "apply_oil_to_initial", "disaster_anchor",
          "climate_anchor", "base_growth", "labor_response", "oil_gdp_loss", "conflict_gdp_loss", "quake_gdp_loss",
          "disaster_gdp_loss", "climate_gdp_loss", "slack", "price_pressure_coefficient"):
    eq("B_params", "F_param_eq_SQ:" + k, P[k], f_doc["parameters"][k])
    eq("B_params", "N3_param_eq_SQ:" + k, P[k], n3p[k])

def risk_of(y):
    if y == 2026: return 0.0   # oil scheduled but not applied to the initial state; no 2026 transition
    r = 0.0
    if y == 2027: r += P["conflict_gdp_loss"]
    if y == 2031: r += P["quake_gdp_loss"]
    if y >= P["disaster_anchor"] and (y - P["disaster_anchor"]) % 3 == 0: r += P["disaster_gdp_loss"]
    if y >= P["climate_anchor"] and (y - P["climate_anchor"]) % 2 == 0: r += P["climate_gdp_loss"]
    return r
def infl_of(y):
    return P["base_inflation"] + (P["conflict_inflation_extra"] if y == 2027 else 0.0)

RISK = {y: risk_of(y) for y in YEARS}; INFL = {y: infl_of(y) for y in YEARS}
for y in YEARS:
    near("B_events", f"SQ_risk:{y}", RISK[y], sq[y]["risk"], 1e-15, 0)
    near("B_events", f"F_risk:{y}", RISK[y], ft[y]["risk"], 1e-15, 0)
    near("B_events", f"N3_risk_via_denominator_SQ:{y}", RISK[y], sq[y]["risk"], 1e-15, 0)
    near("B_events", f"SQ_inflation:{y}", INFL[y], sq[y]["inflation"], 1e-15, 0)
    near("B_events", f"F_inflation:{y}", INFL[y], ft[y]["inflation"], 1e-15, 0)

def core(labor, y0=580.0, n0=600.0):
    nl = 1.0; yc = {2026: y0}; nc = {2026: n0}
    for y in YEARS[1:]:
        nl *= 1 + P["base_growth"] - RISK[y]
        yc[y] = y0 * nl * (labor[y] / labor[2026]) ** P["labor_response"]
        g = yc[y] / yc[y - 1] - 1 if y - 1 in yc else None
        nc[y] = nc[y - 1] * (1 + g + INFL[y])
    return yc, nc

def check_branch(tag, rows, labor, pop, unmet_fn, desired_fn, cap_fn, Yfinal, Nfinal, ceiling_label):
    yc, nc = core(labor)
    out = {}
    for y in YEARS:
        r = rows[y]
        near("C_core_" + tag, f"coreY:{y}", yc[y], r["coreY"])
        near("C_core_" + tag, f"coreN:{y}", nc[y], r["coreN"])
        d = nc[y] / yc[y]
        near("C_core_" + tag, f"coreD:{y}", d, r["coreD"])
        des, cap = desired_fn(y), cap_fn(y)
        Y = min(des, cap); unmet = max(des - cap, 0.0)
        pressure = P["price_pressure_coefficient"] * unmet / yc[y]
        N = Y * d * (1 + pressure)
        near("C_YN_" + tag, f"Y=min(desired,{ceiling_label}):{y}", Y, Yfinal(y))
        near("C_YN_" + tag, f"N=Y*coreD*(1+pressure):{y}", N, Nfinal(y))
        out[y] = (Y, N, d, pressure)
    return yc, nc, out

# ---------------- SQ
for y in YEARS:
    near("C_inputs_SQ", f"SQ_pop_eq_N3denom_pop:{y}", sq[y]["population"], nd[y]["macro_row"]["population_persons"], 1e-6, 0)
    near("C_inputs_SQ", f"SQ_labor_eq_N3denom_labor:{y}", sq[y]["labor"], nd[y]["labor"], 1e-6, 0)
    near("C_inputs_SQ", f"SQ_vs_prior_SQ_trace_Y:{y}", sq[y]["Y"], sqprior[y]["Y"], 1e-12, 0)
    near("C_inputs_SQ", f"SQ_vs_prior_SQ_trace_N:{y}", sq[y]["N"], sqprior[y]["N"], 1e-12, 0)
SQlabor = {y: sq[y]["labor"] for y in YEARS}
def sq_desired(y):
    r = sq[y]; d = r["coreD"]
    return (r["coreY"] + P["capacity_absorption"] * r["supply"] + r["C"] + r["I"]
            + r["education_nom"] / d + r["education_level"] + r["finite"] + r["service_nominal"] / d)
def sq_cap(y):
    r = sq[y]; return r["coreY"] * (1 + P["slack"]) + r["supply"]
for y in YEARS:
    near("C_YN_SQ", f"desired_decomposition:{y}", sq_desired(y), sq[y]["desired"], 1e-9, 0)
    near("C_YN_SQ", f"capacity=coreY*(1+slack)+supply:{y}", sq_cap(y), sq[y]["capacity"], 1e-9, 0)
SQyc, SQnc, SQo = check_branch("SQ", sq, SQlabor, None, None, lambda y: sq[y]["desired"], lambda y: sq[y]["capacity"],
                               lambda y: sq[y]["Y"], lambda y: sq[y]["N"], "capacity")
# ---------------- F
Flabor = {y: ft[y]["labor"] for y in YEARS}
for y in YEARS:
    near("C_inputs_F", f"F_trace_labor_eq_annual_labor_proxy:{y}", ft[y]["labor"], fa[y]["labor_force_population_proxy"], 1e-6, 0)
    near("C_inputs_F", f"F_trace_Y_eq_annual:{y}", ft[y]["Y"], fa[y]["real_gdp_trn"], 1e-12, 0)
    near("C_inputs_F", f"F_trace_N_eq_annual:{y}", ft[y]["N"], fa[y]["nominal_gdp_trn"], 1e-12, 0)
    near("C_YN_F", f"capacity=coreY*(1+slack)+supply:{y}", ft[y]["coreY"] * (1 + P["slack"]) + ft[y]["supply"], ft[y]["capacity"], 1e-9, 0)
    des = (ft[y]["coreY"] + P["capacity_absorption"] * ft[y]["supply"] + ft[y]["C"] + ft[y]["I"]
           + ft[y]["education_nom"] / ft[y]["coreD"] + ft[y]["education_level"] + ft[y]["finite"])
    # F desired also carries a domestic education-service term and services (not exposed in the trace years);
    # report residual instead of asserting equality
    LOG.append(("C_YN_F", f"desired_residual_info:{y}", "", "", des - ft[y]["desired"], True))
Fyc, Fnc, Fo = check_branch("F", ft, Flabor, None, None, lambda y: ft[y]["desired"], lambda y: ft[y]["capacity"],
                            lambda y: fa[y]["real_gdp_trn"], lambda y: fa[y]["nominal_gdp_trn"], "capacity")
# ---------------- N3 (core = SQ core via common labour; own demand-side result)
for y in YEARS:
    near("C_inputs_N3", f"N3_GDP_prior_decomposition_real:{y}", na[y]["real_GDP_trn"], nprior[y]["N3_real_GDP_trn"], 2e-8, 2e-12)
    near("C_inputs_N3", f"N3_GDP_prior_decomposition_nominal:{y}", na[y]["nominal_GDP_trn"], nprior[y]["N3_nominal_GDP_trn"], 2e-8, 2e-12)
    eq("C_inputs_N3", f"N3_gov_purchase_and_public_inv_zero:{y}", (0, 0), (na[y]["government_purchase_nominal_trn"], na[y]["public_investment_nominal_trn"]))
    near("C_YN_N3", f"ceiling=coreY*(1+slack)+supply_real:{y}", SQyc[y] * (1 + P["slack"]) + na[y]["supply_real_trn"], na[y]["supply_ceiling_real_trn"], 1e-8, 0)
N3 = {}
for y in YEARS:
    des, ceil = na[y]["desired_real_GDP_trn"], na[y]["supply_ceiling_real_trn"]
    Y = min(des, ceil); unmet = max(des - ceil, 0.0)
    near("C_YN_N3", f"unmet=max(desired-ceiling,0):{y}", unmet, na[y]["unmet_demand_real_trn"], 1e-8, 0)
    near("C_YN_N3", f"Y=min(desired,ceiling):{y}", Y, na[y]["real_GDP_trn"], 1e-8, 1e-12)
    d = SQnc[y] / SQyc[y]
    pr = P["price_pressure_coefficient"] * unmet / SQyc[y]
    N = Y * d * (1 + pr)
    near("C_YN_N3", f"N=Y*coreD_SQ*(1+pressure):{y}", N, na[y]["nominal_GDP_trn"], 1e-8, 1e-12)
    N3[y] = (na[y]["real_GDP_trn"], na[y]["nominal_GDP_trn"])
# ---- shared labour/population facts
for y in YEARS:
    near("D_conditions", f"N3_labor_eq_SQ_labor_zero_gap:{y}", 0.0, nd[y]["labor"] - sq[y]["labor"], 1e-9, 0)
    near("D_conditions", f"N3_pop_eq_SQ_pop_zero_gap:{y}", 0.0, nd[y]["macro_row"]["population_persons"] - sq[y]["population"], 1e-6, 0)
eq("D_conditions", "init_real_nominal_pop_F_SQ_N3",
   [(580.0, 600.0, 122618024)] * 3,
   [(fa[2026]["real_gdp_trn"], fa[2026]["nominal_gdp_trn"], round(fa[2026]["population"])),
    (sq[2026]["Y"], sq[2026]["N"], round(sq[2026]["population"])),
    (na[2026]["real_GDP_trn"], na[2026]["nominal_GDP_trn"], round(nd[2026]["macro_row"]["population_persons"]))])
eq("D_conditions", "oil_not_applied_initial", False, f_doc["parameters"]["apply_oil_to_initial"])
eq("D_conditions", "SQ_2026_no_growth_transition", None, sq[2026]["growth"])
flag("D_conditions", "F_labor_differs_from_SQ_labor_policy_channel", any(abs(Flabor[y] - SQlabor[y]) > 1 for y in YEARS))
flag("D_conditions", "F_population_differs_from_SQ_population", any(abs(fa[y]["population"] - sq[y]["population"]) > 1 for y in YEARS))
FPOP = {y: fa[y]["population"] for y in YEARS}; SQPOP = {y: sq[y]["population"] for y in YEARS}
N3POP = {y: nd[y]["macro_row"]["population_persons"] for y in YEARS}

# ---------------------------------------------------------------- E. derived indicators (own definitions)
BASE_D = 600.0 / 580.0
own = {}   # (case, year) -> dict of 10 indicators
vals = {"F": {}, "SQ": {}, "N3": {}}
for y in YEARS:
    vals["F"][y] = (Fo[y][0], Fo[y][1], FPOP[y], Flabor[y])
    vals["SQ"][y] = (SQo[y][0], SQo[y][1], SQPOP[y], SQlabor[y])
    vals["N3"][y] = (N3[y][0], N3[y][1], N3POP[y], nd[y]["labor"])
infl_in = {"F": {y: ft[y]["inflation"] for y in YEARS}, "SQ": {y: sq[y]["inflation"] for y in YEARS}, "N3": {y: sq[y]["inflation"] for y in YEARS}}
risk_in = {"F": {y: ft[y]["risk"] for y in YEARS}, "SQ": {y: sq[y]["risk"] for y in YEARS}, "N3": {y: sq[y]["risk"] for y in YEARS}}
for c in vals:
    for y in YEARS:
        R, N, pop, lab = vals[c][y]
        g = 100 * (R / vals[c][y - 1][0] - 1) if y > 2026 else None
        own[(c, y)] = {"real_gdp": R, "nominal_gdp": N, "implicit_gdp_deflator": 100 * (N / R) / BASE_D, "population": pop,
                       "effective_labor": lab, "real_gdp_growth": g, "real_gdp_per_capita": R * 1e12 / pop,
                       "nominal_gdp_per_capita": N * 1e12 / pop, "input_inflation": 100 * infl_in[c][y], "applied_real_risk": 100 * risk_in[c][y]}
INDS = ["real_gdp", "nominal_gdp", "implicit_gdp_deflator", "population", "effective_labor", "real_gdp_growth",
        "real_gdp_per_capita", "nominal_gdp_per_capita", "input_inflation", "applied_real_risk"]
annual = csvrows(show(FINAL, D + "Annual_Comparison.csv"))
eq("E_annual", "rows_300", 300, len(annual))
eq("E_annual", "unique_year_indicator", 300, len({(r["year"], r["indicator"]) for r in annual}))
eq("E_annual", "indicator_set", sorted(INDS), sorted({r["indicator"] for r in annual}))
tol = lambda ind: (2e-8, 2e-12) if ind in ("real_gdp", "nominal_gdp", "population", "effective_labor") else (1e-8, 1e-11)
amap = {(int(r["year"]), r["indicator"]): r for r in annual}
for y in YEARS:
    for ind in INDS:
        r = amap[(y, ind)]
        vs = {c: own[(c, y)][ind] for c in ("F", "SQ", "N3")}
        if vs["F"] is None:
            eq("E_annual", f"{ind}:{y}:undefined_is_NA", ("N/A",) * 7, tuple(r[k] for k in ("F", "SQ", "N3", "F_minus_SQ", "F_minus_N3", "N3_minus_SQ")) + ("N/A",))
            eq("E_annual", f"{ind}:{y}:status_NA", "N/A", r["status"])
            continue
        a, b = (2e-8, 2e-12) if ind in ("real_gdp", "nominal_gdp", "population", "effective_labor") else (1e-8, 1e-11)
        for c in ("F", "SQ", "N3"):
            near("E_annual", f"{ind}:{y}:{c}", vs[c], r[c], a, b)
        near("E_annual", f"{ind}:{y}:F-SQ", vs["F"] - vs["SQ"], r["F_minus_SQ"], a, b)
        near("E_annual", f"{ind}:{y}:F-N3", vs["F"] - vs["N3"], r["F_minus_N3"], a, b)
        near("E_annual", f"{ind}:{y}:N3-SQ", vs["N3"] - vs["SQ"], r["N3_minus_SQ"], a, b)
        near("E_telescope", f"{ind}:{y}:F-SQ=(F-N3)+(N3-SQ)", vs["F"] - vs["SQ"], (vs["F"] - vs["N3"]) + (vs["N3"] - vs["SQ"]), 1e-7, 1e-11)
        eq("E_annual", f"{ind}:{y}:status", "COMPARABLE" if ind in ("input_inflation", "applied_real_risk") else "CONDITIONAL", r["status"])
        if ind in ("input_inflation", "applied_real_risk"):
            eq("E_annual", f"{ind}:{y}:comparable_gaps_zero", (0.0, 0.0, 0.0), tuple(float(r[k]) for k in ("F_minus_SQ", "F_minus_N3", "N3_minus_SQ")))
# per-capita restoration and deflator invariance (own)
for c in ("F", "SQ", "N3"):
    for y in YEARS:
        o = own[(c, y)]
        near("E_percap", f"{c}:{y}:real_restore", o["real_gdp"], o["real_gdp_per_capita"] * o["population"] / 1e12, 1e-9, 1e-12)
        near("E_percap", f"{c}:{y}:nominal_restore", o["nominal_gdp"], o["nominal_gdp_per_capita"] * o["population"] / 1e12, 1e-9, 1e-12)
        near("E_percap", f"{c}:{y}:deflator_invariance", o["implicit_gdp_deflator"], 100 * (o["nominal_gdp_per_capita"] / o["real_gdp_per_capita"]) / BASE_D, 1e-9, 1e-12)
        if y > 2026:
            near("E_percap", f"{c}:{y}:growth_chain", o["real_gdp"], 580.0 * math.prod(1 + own[(c, t)]["real_gdp_growth"] / 100 for t in range(2027, y + 1)), 1e-9, 1e-11)

# key years
keyrows = csvrows(show(FINAL, D + "Key_Years.csv"))
eq("E_keyyears", "rows_40", 40, len(keyrows))
eq("E_keyyears", "years", [2026, 2035, 2045, 2055], sorted({int(r["year"]) for r in keyrows}))
for r in keyrows:
    a = amap[(int(r["year"]), r["indicator"])]
    eq("E_keyyears", f"row_eq_annual:{r['year']}:{r['indicator']}", dict(a), dict(r))

# ---------------------------------------------------------------- F. Report.md claims
rep = show(FINAL, D + "Report.md").decode("utf-8")
tbl = {}
for line in rep.splitlines():
    m = re.match(r"\|\s*(2026|2035|2045|2055)\s*\|(.*)\|\s*$", line)
    if m:
        tbl[int(m.group(1))] = [float(x.replace("−", "-").replace("+", "").strip()) for x in m.group(2).split("|")]
eq("F_report", "table_years", [2026, 2035, 2045, 2055], sorted(tbl))
for y, row in tbl.items():
    o = {c: own[(c, y)] for c in ("F", "SQ", "N3")}
    exp = [o["F"]["real_gdp"], o["SQ"]["real_gdp"], o["N3"]["real_gdp"],
           o["F"]["real_gdp"] - o["SQ"]["real_gdp"], o["F"]["real_gdp"] - o["N3"]["real_gdp"], o["N3"]["real_gdp"] - o["SQ"]["real_gdp"],
           o["F"]["real_gdp_per_capita"] / 1e4, o["SQ"]["real_gdp_per_capita"] / 1e4, o["N3"]["real_gdp_per_capita"] / 1e4]
    for i, (e, a) in enumerate(zip(exp, row)):
        dec = 3 if i < 6 else 1
        rec("F_report", f"table:{y}:col{i}", round(e, dec), a, abs(round(e, dec) - a) < 10 ** -dec / 2 + 1e-12, abs(round(e, dec) - a))
o55 = {c: own[(c, 2055)] for c in ("F", "SQ", "N3")}
for c, v in zip(("F", "SQ", "N3"), (1045.124, 1023.330, 936.329)):
    rec("F_report", f"nominal2055:{c}", v, round(o55[c]["nominal_gdp"], 3), abs(round(o55[c]["nominal_gdp"], 3) - v) < 5e-4 + 1e-12)
for c, v in zip(("F", "SQ", "N3"), (186.995, 187.011, 187.011)):
    rec("F_report", f"deflator2055:{c}", v, round(o55[c]["implicit_gdp_deflator"], 3), abs(round(o55[c]["implicit_gdp_deflator"], 3) - v) < 5e-4 + 1e-12)
for c, v in zip(("F", "SQ", "N3"), (10445, 10465, 10465)):
    rec("F_report", f"pop2055_10k:{c}", v, round(o55[c]["population"] / 1e4), abs(round(o55[c]["population"] / 1e4) - v) <= 1)
# F reconnection bridge claim and bridge csv
bridge = {int(r["year"]): r for r in csvrows(show(FINAL, D + "F_Native_To_Matched_Bridge.csv"))}
for y in YEARS:
    near("G_bridge", f"real_bridge:{y}", fa[y]["real_gdp_trn"] - fo[y]["real_gdp_trn"], bridge[y]["matched_f_real_gdp_minus_native_trn"], 1e-12, 0)
    near("G_bridge", f"nominal_bridge:{y}", fa[y]["nominal_gdp_trn"] - fo[y]["nominal_gdp_trn"], bridge[y]["matched_f_nominal_gdp_minus_native_trn"], 1e-12, 0)
    near("G_bridge", f"old_F_vs_fixed_LATEST_F_real:{y}", float(fnat[y]["real_gdp_trn"]), fo[y]["real_gdp_trn"], 3e-6, 2e-12)
    near("G_bridge", f"old_F_vs_fixed_LATEST_F_nominal:{y}", float(fnat[y]["nominal_gdp_trn"]), fo[y]["nominal_gdp_trn"], 3e-6, 2e-12)
    near("G_bridge", f"old_F_vs_fixed_LATEST_F_population:{y}", float(fnat[y]["population"]), fo[y]["population"], 1e-3, 0)
rec("G_bridge", "report_bridge_2055_-9.392e-6", -9.392e-6, fa[2055]["real_gdp_trn"] - fo[2055]["real_gdp_trn"],
    abs((fa[2055]["real_gdp_trn"] - fo[2055]["real_gdp_trn"]) - (-9.392e-6)) < 5e-10)
flag("G_bridge", "bridge_max_abs_real_lt_1e-4", max(abs(fa[y]["real_gdp_trn"] - fo[y]["real_gdp_trn"]) for y in YEARS) < 1e-4)
# medical reference identity (re-derived from sources, independent of Work Validation.json)
fin = dj("f_native_input"); fmr = dj("f_medical_reference")
n3med = dj("n3_parameters")["medical_input"]
for key in ("common_parameters", "common_financing", "clinical_strata", "registry_population_reference"):
    eq("G_medref", "F_native_input_eq_N3_medical:" + key, fin[key], n3med["c"][key])
for key in ("deflators", "population"):
    eq("G_medref", "F_medical_reference_eq_N3:" + key, fmr[key], n3med[key])

# ---------------------------------------------------------------- G. F household context (F-only)
hh = csvrows(show(FINAL, D + "F_Household_Context.csv"))
eq("H_household", "rows_60", 60, len(hh))
cols = ("cash_median_real_2026_yen", "cash_median_real_2026_yen_delta_fixed", "synthetic_cash_gini", "synthetic_cash_gini_delta_fixed",
        "Q2_cash_real_2026_yen_delta_fixed", "Q3_cash_real_2026_yen_delta_fixed", "Q4_cash_real_2026_yen_delta_fixed")
for case, status in (("FIXED_F", "F_ONLY_SYNTHETIC_FIXED_REFERENCE"), ("INTEGRATED", "F_ONLY_SYNTHETIC_NOT_ADOPTED")):
    mine = {int(r["year"]): r for r in fh if r["case"] == case}
    out = {int(r["year"]): r for r in hh if r["case"] == case}
    eq("H_household", f"{case}:years", YEARS, sorted(out))
    for y in YEARS:
        eq("H_household", f"{case}:{y}:status", status, out[y]["status"])
        for c in cols:
            near("H_household", f"{case}:{y}:{c}", mine[y][c], out[y][c], 1e-9, 1e-12)
fx = {int(r["year"]): r for r in hh if r["case"] == "FIXED_F"}; it = {int(r["year"]): r for r in hh if r["case"] == "INTEGRATED"}
rec("H_household", "report_FIXED_F_median_2055_423.834万", 423.834, round(float(fx[2055]["cash_median_real_2026_yen"]) / 1e4, 3), abs(round(float(fx[2055]["cash_median_real_2026_yen"]) / 1e4, 3) - 423.834) < 5e-4)
rec("H_household", "report_INTEGRATED_median_2055_424.998万", 424.998, round(float(it[2055]["cash_median_real_2026_yen"]) / 1e4, 3), abs(round(float(it[2055]["cash_median_real_2026_yen"]) / 1e4, 3) - 424.998) < 5e-4)
flag("H_household", "household_not_in_annual_comparison", not any("household" in r["indicator"] or "gini" in r["indicator"] for r in annual))

# ---------------------------------------------------------------- H. comparison contract / N-A boundary
con = csvrows(show(FINAL, D + "Comparison_Contract.csv"))
eq("I_contract", "rows_22", 22, len(con))
st = Counter(r["status"] for r in con)
eq("I_contract", "status_counts", {"CONDITIONAL": 8, "COMPARABLE": 2, "NOT COMPARABLE": 9, "N/A": 3}, dict(st))
eq("I_contract", "annual_indicators_equal_contract_defined",
   sorted(r["indicator"] for r in con if r["status"] in ("CONDITIONAL", "COMPARABLE")), sorted(INDS))
blocked = [r for r in con if r["status"] in ("NOT COMPARABLE", "N/A")]
for r in blocked:
    flag("I_contract", f"blocked_has_cause_code:{r['indicator']}", r["cause_codes"] != "")
    flag("I_contract", f"blocked_not_in_annual:{r['indicator']}", r["indicator"] not in {x["indicator"] for x in annual})
    eq("I_contract", f"blocked_no_numeric_unit_or_years:{r['indicator']}", ("N/A", "N/A", "N/A"), (r["unit"], r["price_basis"], r["available_years"]))
for r in con:
    if r["status"] in ("CONDITIONAL", "COMPARABLE"):
        eq("I_contract", f"defined_no_cause_code:{r['indicator']}", "", r["cause_codes"])
        eq("I_contract", f"defined_years:{r['indicator']}", "2027-2055" if r["indicator"] == "real_gdp_growth" else "2026-2055", r["available_years"])
# Referenced proxy columns exist (so N/A is a definitional boundary, not missing data) and raw proxies are shown to diverge
def col(tbl, key, y): return tbl[y].get(key)
refs = [("national_tax", fa, "tax_diagnostic_trn", sq, None, na, "total_tax_diagnostic_proxy_trn"),
        ("national_household_cash", fa, "macro_cash_DI_proxy_trn", nd, "macro_row.household_disposable_nominal_trn", na, "household_resource_DI_proxy_trn"),
        ("investment", fa, "I_policy_real_trn", nd, "macro_row.capital_replacement_investment_real_trn", na, "private_investment_real_trn"),
        ("household_consumption", fa, "household_consumption_real_proxy_trn", sq, "household_consumption_real_proxy", na, "consumption_real_trn")]
raw_rows = []
for name, ft_, fk, st_, sk, nt_, nk in refs:
    exists_f = fk in ft_[2055]; exists_n = nk in nt_[2055]
    flag("I_boundary", f"{name}:F_column_exists", exists_f); flag("I_boundary", f"{name}:N3_column_exists", exists_n)
    if sk is None:
        sv = st_[2055]["tax"] + st_[2055]["direct"]
    elif "." in sk:
        a, b = sk.split("."); sv = st_[2055][a][b]
    else:
        sv = st_[2055][sk]
    fv, nv = ft_[2055][fk], nt_[2055][nk]
    raw_rows.append((name, fv, sv, nv))
flag("I_boundary", "F_I_policy_excludes_replacement_investment (F value << SQ replacement flow)", abs(raw_rows[2][1]) < 0.2 * abs(raw_rows[2][2]), f"F {raw_rows[2][1]:.4f} vs SQ {raw_rows[2][2]:.4f}")
flag("I_boundary", "N3_has_PB_debt_SQ_closure_not_national", "SQ_CL_PB_same_fiscal_scenario_trn" in na[2055] and "CL_PB_candidate_trn" in na[2055])
flag("I_boundary", "N3_fund_vs_F_fund_boundaries_differ", "pension_fund_end_trn" in na[2055] and "fund_balance_trn" in fa[2055])
with open(os.path.join(OUT, "Raw_Proxy_2055_Not_Comparable_Info.csv"), "w", newline="") as fo_:
    w = csv.writer(fo_); w.writerow(["indicator", "F_proxy_2055", "SQ_proxy_2055", "N3_proxy_2055", "note"])
    for r in raw_rows: w.writerow(list(r) + ["raw model proxies with different definitions; shown only to illustrate the N/A boundary, not a comparison"])

# ---------------------------------------------------------------- I. deflator vs input inflation, labour facts (informational + checked)
dcagr = {c: (own[(c, 2055)]["implicit_gdp_deflator"] / 100) ** (1 / 29) - 1 for c in ("F", "SQ", "N3")}
meaninfl = sum(INFL[y] for y in YEARS[1:]) / 29
flag("J_deflator", "implicit_deflator_differs_from_input_inflation_SQ", abs(dcagr["SQ"] - meaninfl) > 1e-5, f"deflator CAGR {dcagr['SQ']:.6f} vs mean input {meaninfl:.6f}")
for y in YEARS[1:]:
    g = SQyc[y] / SQyc[y - 1] - 1   # own growth of the real core (not the stored 'growth' column)
    near("J_deflator", f"SQ_deflator_growth=1+pi/(1+g) (additive rule):{y}",
         1 + INFL[y] / (1 + g), own[("SQ", y)]["implicit_gdp_deflator"] / own[("SQ", y - 1)]["implicit_gdp_deflator"], 1e-12, 0)

# ---------------------------------------------------------------- outputs
with open(os.path.join(OUT, "Independent_Numeric_Comparison_DRAFT_20261123.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["group", "check", "expected", "actual", "abs_diff", "ok"]); w.writerows(LOG)
keyout = []
for y in (2026, 2035, 2045, 2055):
    for ind in INDS:
        r = amap[(y, ind)]
        vs = {c: own[(c, y)][ind] for c in ("F", "SQ", "N3")}
        keyout.append([y, ind] + [vs[c] for c in ("F", "SQ", "N3")] + ([vs["F"] - vs["SQ"], vs["F"] - vs["N3"], vs["N3"] - vs["SQ"]] if vs["F"] is not None else ["N/A"] * 3))
with open(os.path.join(OUT, "Independent_Key_Years_DRAFT_20261123.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["year", "indicator", "F", "SQ", "N3", "F_minus_SQ", "F_minus_N3", "N3_minus_SQ"]); w.writerows(keyout)
maxdiff = {}
for g, i, e, a, d, ok in LOG:
    if d != "": maxdiff[g] = max(maxdiff.get(g, 0.0), float(d))
# ---- Source_Identity.json : values MEASURED by this script from git objects (not copied from Work's records)
ident = {"final_commit": FINAL, "payload_commit": PAYLOAD,
         "final_directory": [{"path": p, "bytes": len(show(FINAL, p)), "sha256": sha(show(FINAL, p)), "git_blob": blob(FINAL, p)} for p in files_final],
         "dependencies": {k: {"commit": f["commit"], "path": f["path"], "bytes": len(show(f["commit"], f["path"])),
                              "sha256": sha(show(f["commit"], f["path"])), "git_blob": blob(f["commit"], f["path"])} for k, f in dep.items()},
         "note": "bytes/sha256/git_blob measured from fixed git objects by the verifier; Custody.json receives no credit as evidence"}
json.dump(ident, open(os.path.join(OUT, "Source_Identity_DRAFT_20261123.json"), "w"), indent=1)

n_items = len(LOG)
summary = {"check_groups": len(counts), "checks_counted": sum(counts.values()), "items_logged": n_items, "failures": sum(fails.values()),
           "groups_failed": sorted(fails), "per_group": dict(sorted(counts.items())), "max_abs_diff_per_group": maxdiff,
           "real2055": {c: own[(c, 2055)]["real_gdp"] for c in ("F", "SQ", "N3")},
           "nominal2055": {c: own[(c, 2055)]["nominal_gdp"] for c in ("F", "SQ", "N3")},
           "gap2055": {"F-SQ": o55["F"]["real_gdp"] - o55["SQ"]["real_gdp"], "F-N3": o55["F"]["real_gdp"] - o55["N3"]["real_gdp"], "N3-SQ": o55["N3"]["real_gdp"] - o55["SQ"]["real_gdp"]},
           "deflator_CAGR": dcagr, "mean_input_inflation_2027_2055": meaninfl,
           "years_real_below_580": {c: sum(1 for y in YEARS[1:] if own[(c, y)]["real_gdp"] < 580) for c in ("F", "SQ", "N3")},
           "years_N3_below_SQ": sum(1 for y in YEARS if own[("N3", y)]["real_gdp"] < own[("SQ", y)]["real_gdp"])}
json.dump(summary, open(os.path.join(OUT, "Independent_Summary_DRAFT_20261123.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: summary[k] for k in ("check_groups", "checks_counted", "failures", "groups_failed", "real2055", "gap2055", "years_real_below_580", "years_N3_below_SQ")}, indent=1))
for g, c in sorted(counts.items()):
    print(f"{g:24s} {c:6d} fail={fails.get(g, 0)}")
for g, i, e, a, d, ok in LOG:
    if not ok: print("FAIL", g, i, e, a, d)
sys.exit(1 if fails else 0)
