"""In-memory adapters for the fixed F and N3/SQ runtimes."""
import builtins
import json
import math
import sys
from pathlib import Path

H = "handoff/chatgpt-"
MATCH = H + "sq-baseline-contract-three-scenario-recalculation-20261123/"
PARITY = H + "n3-f-parity-implementation-20261122/"
BURDEN = H + "n3-policy-burden-diagnosis-20261122/"
GAP = H + "n3-gdp-gap-causal-attribution-20261123/"
DRAFT_PIN = "3c77eafc2073fdaba4c129164817d2f57c9421b9"
DRAFT = "handoff/claude-n3-model-draft-20261121/SPE_N3_Medical_On_CommonSQ_Draft_DRAFT_20261121.py"
D0 = 600/580


def replace(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"Expected exactly one anchor: {old}")
    return source.replace(old, new)


def adapt(source, factors, prices):
    """Keep the common labour response. Replace the nonlabour and price laws."""
    source = replace(source, "nonlabor_factor*=1+p['base_growth']-risk",
                     f"nonlabor_factor=(1+p['base_growth'])**i*{tuple(factors)!r}[i]")
    source = replace(source, "coreN*=1+growth+inflation;coreD=coreN/coreY",
                     f"coreD={tuple(prices)!r}[i];coreN=coreY*coreD")
    return source


def load(path):
    return json.loads(path.read_bytes())


def run_f(root, out, factors, prices, sensitivity=False):
    import importlib.util

    worker_path = root/MATCH/"Three_Scenario_Worker.py"
    spec = importlib.util.spec_from_file_location("fixed_f_worker", worker_path)
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    original_mod = worker.mod
    incidence = {}

    def mod(name, path):
        model = original_mod(name, path)
        if name != "isolated_F_model":
            return model
        original_load = model.load
        original_patch = model.patch
        original_medical = model.Medical

        def medical(c, s, d, pop):
            return original_medical(c, s, prices, pop)

        def load_model(c):
            result = original_load(c)
            edu, vat = result[1], result[4]
            original_education = edu.Education
            edu.Education = lambda cfg, s, d: original_education(cfg, s, prices)
            original_dependencies = vat.load_dependencies

            def dependencies(*args):
                value = original_dependencies(*args)
                accounts = value[1]["annual_accounts"]

                def capture(c, s, base, i, f, p, pm, state, disabled):
                    adjusted = dict(base)
                    adjusted["macro"] = list(base["macro"])
                    adjusted["macro"][i] = dict(base["macro"][i], common_deflator=prices[i])
                    ledger, rows = accounts(c, s, adjusted, i, f, p, pm, state, disabled)
                    y = 2026+i
                    if not sensitivity:
                        ordered = sorted((r["cash_DI_after_yen"], r["households"]) for r in rows)
                        half = sum(w for _, w in ordered)/2
                        running = 0.
                        for cash, weight in ordered:
                            running += weight
                            if running >= half:
                                incidence[y] = {"median_nominal_yen":cash}
                                break
                    if sensitivity:
                        incidence[y] = reallocate(rows, ledger, s, c, y, f, p, pm, state, disabled, shares, burden, household_module)
                    return ledger, rows

                value[1]["annual_accounts"] = capture
                return value

            vat.load_dependencies = dependencies
            return result

        def patch(engine, policy, med, s):
            def compile_dynamic(source, filename, mode):
                if filename == "medical_education_integrated.py":
                    source = adapt(source, factors, prices)
                    if sensitivity:
                        source = replace(source, "        Ctarget=", """        _bridge=_incidence[y]
        ss['weighted_demand']+=_bridge['demand_delta']
        ss['household']+=_bridge['cash_delta']
        cash+=_bridge['cash_delta']
        Ctarget=""")
                        source = replace(source, "        taxdiag=tax+direct;",
                                         "        direct+=_bridge['national_tax_delta']+_bridge['local_tax_delta']\n        taxdiag=tax+direct;")
                return builtins.compile(source, filename, mode)

            model.compile = compile_dynamic
            if sensitivity:
                engine["run_path"].__globals__["_incidence"] = incidence
            return original_patch(engine, policy, med, s)

        model.Medical = medical
        model.load = load_model
        model.patch = patch
        return model

    # The worker uses its trace for fiscal and macro rows. Add two wage columns
    # through its existing capture, keeping its output names and call sequence.
    source = worker_path.read_text()
    source = replace(source, "'finite','tax','direct']", "'finite','tax','direct','nominalwage_proxy','realwage_proxy','Ctarget','Kprev','nonlabor_factor','labor_anchor','coreY_anchor','lg']")
    exec(compile(source, str(worker_path), "exec"), worker.__dict__)
    worker.mod = mod
    if sensitivity:
        directory = root/(H+"f-income-calibration-20261123/calibration-evidence")
        config = load(directory/"Inputs.json")
        burden = config["burden_sensitivity"]
        integration = directory/"Run.py"
        cal = original_mod("f_calibration_for_dynamic", integration)
        shares = cal.load_shares(directory/"Wage_Shares.csv")
        household_module = original_mod("fixed_household_rules", root/"handoff/f-household-social-20261120/Model.py")
    out.mkdir(parents=True, exist_ok=True)
    worker.f(root, out, True)
    return load(out/"F_Actual_Annual.json"), load(out/"F_Runtime_Trace.json"), incidence


def reallocate(rows, ledger, settings, cfg, year, vat, parameters, pm, state,
               disabled, wage_shares, burden, household):
    """Apply the existing incidence sensitivity to regenerated synthetic cells."""
    grid = [dict(r) for r in rows]
    basis = []
    pool = vat["household"] - ledger["VAT_price_effect_trn"] if year > 2026 else 0.
    active = 0. if disabled else household.phase(year, settings)
    stats = cfg["stats"]
    for r in grid:
        gross = r["gross_income_yen"]
        wage_basis = gross if r["profile"] in ("EMP_SINGLE","EMP_CHILD") else 0.
        if r["profile"] == "EMP_CHILD":
            wage_basis *= next(share for limit, share in wage_shares if gross/r["idx"] <= limit)
        basis.append(wage_basis)
    denom = sum(r["households"]*b for r,b in zip(grid,basis,strict=True))
    for r,b in zip(grid,basis,strict=True):
        r["wage"] = pool*1e12*b/denom if denom else 0.
        r["adjusted"] = r["gross_income_yen"]+r["wage"]
    cweight = sum(r["households"]*r["consumption_yen"] for r in grid if r["adjusted"] <= 5e6)
    sums = dict((k,0.) for k in ("wage","A_delta","B_delta","B_cost_delta","B_admin_delta","C_delta",
                                  "cash_delta","national_tax_delta","local_tax_delta","pension_delta",
                                  "private_consumption_delta","service_delta","demand_delta"))
    values = []
    equiv = []
    fixed_cash = []
    for r in grid:
        wage = r["wage"]
        pension = wage*burden["employee_pension_rate_continuous"]
        taxable = (wage-pension)*burden["illustrative_taxable_share_of_wage_after_pension"]
        nt = taxable*burden["illustrative_national_income_tax_rate"]
        lt = taxable*burden["illustrative_resident_tax_rate"]
        gross = r["adjusted"]
        a = r["premium_target_yen"]*household.reduction(gross, ledger["maximum_relief_rate"], settings, 1.)*active
        c = ledger["C_cash_trn"]*1e12*r["consumption_yen"]/cweight if cweight and gross<=5e6 else 0.
        b_lost = gross>3e6
        b = 0. if b_lost else r["B_used_yen"]
        qi, coverage = r["quintile"],r["coverage"]
        taxbase = state["taxbase"].get((year,qi,r["idx"]))
        if taxbase is None:
            taxbase = household.equivalent_taxable(stats["income_tax_mean_paid_yen"][qi]*r["idx"], year, pm)
        a_tax = coverage*(pm["income_tax"](taxbase+a/coverage,year)-pm["income_tax"](taxbase,year))*stats["income_tax_paid_per2000"][qi]/2000 if coverage else 0.
        a_local = a*.1*stats["local_tax_paid_per2000"][qi]/2000
        da,db,dc = a-r["A_yen"],b-r["B_used_yen"],c-r["C_cash_yen"]
        dt,dl = nt+a_tax-r["tax_increase_yen"],lt+a_local-r["local_tax_increase_yen"]
        cash_delta = da+dc-dt-dl-pension
        private = (r["mpc"]*(cash_delta+wage) - parameters["generic_mpc"]*wage
                   +(1-r["mpc"])*r["B_substitute_yen"]*b_lost)
        changes = (wage,da,db,db*settings["B_cost_factor"],-r["B_admin_yen"]*b_lost,dc,
                   cash_delta,dt,dl,pension,private,db,private+db)
        for key,value in zip(sums,changes,strict=True):
            sums[key]+=value*r["households"]/1e12
        cash = r["cash_DI_after_yen"]+cash_delta+wage
        values.append((cash,r["households"],qi,r["VAT_price_effect_yen"],b))
        fixed_cash.append((r["cash_DI_after_yen"],r["households"],qi,r["VAT_price_effect_yen"],r["B_used_yen"]))
        equiv.append((max(0.,cash)/r["size"]**.5,r["households"]*r["size"]))
        assert c>=0 and (not a or gross<5e6) and (not b or gross<=3e6)
    assert math.isclose(sums["wage"],pool,abs_tol=1e-8)
    assert math.isclose(sums["C_delta"],0. if cweight else -ledger["C_cash_trn"],abs_tol=1e-8)
    assert math.isclose(sums["cash_delta"],sums["A_delta"]+sums["C_delta"]-sums["national_tax_delta"]-
                        sums["local_tax_delta"]-sums["pension_delta"],abs_tol=1e-8)
    assert math.isclose(sums["demand_delta"],sums["private_consumption_delta"]+sums["service_delta"],abs_tol=1e-8)
    # Existing statutory thresholds are compared in nominal yen, and resource
    # indices remain separate from the GDP deflator used for macro demand.
    def median(data):
        total = sum(r[1] for r in data)
        running = 0.
        for cash, weight, *_ in sorted(data):
            running+=weight
            if running>=total*.5:
                return cash
        raise ValueError("empty household grid")

    def average(data, qi, column):
        selected = [r for r in data if r[2]==qi]
        return sum(r[column]*r[1] for r in selected)/sum(r[1] for r in selected)

    population = sum(w for _,w in equiv)
    cumulative = numerator = 0.
    for value,weight in sorted(equiv):
        numerator+=value*weight*(2*cumulative+weight-population)
        cumulative+=weight
    sums["synthetic_cash_gini"]=numerator/(population*sum(v*w for v,w in equiv))
    sums["median_nominal_yen"]=median(values)
    sums["median_without_sensitivity_nominal_yen"]=median(fixed_cash)
    for qi in (1,2,3):
        for column,name in ((0,"cash"),(3,"VAT"),(4,"B")):
            sums[f"Q{qi+1}_{name}_nominal_yen"]=average(values,qi,column)
    sums["saving_delta"]=sums["cash_delta"]-sums["private_consumption_delta"]
    sums["government_gap_delta"]=(sums["A_delta"]+sums["C_delta"]+
                                  sums["B_cost_delta"]*settings["B_government_share"]+sums["B_admin_delta"]-
                                  sums["national_tax_delta"]-sums["local_tax_delta"])
    sums["insurer_gap_delta"]=sums["B_cost_delta"]*(1-settings["B_government_share"])-sums["pension_delta"]
    return sums


def run_common(root, out, draft, factors, prices):
    import importlib.util
    path = root/BURDEN/"N3_Policy_Burden_Diagnosis_Reproduce.py"
    spec = importlib.util.spec_from_file_location("fixed_capture", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SELECT = [module.SQ, module.BASE]
    # The existing capture imports this adapter inside its isolated run_path.
    adapter_path = root/PARITY/"Macro_Adapter.py"
    spec = importlib.util.spec_from_file_location("Macro_Adapter", adapter_path)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    original = adapter.patch
    def patch(source, settings):
        source = adapt(original(source, settings), factors, prices)
        return replace(source, "w=_medical.step(y,rows)", f"_medical.deflators[i]={tuple(prices)!r}[i];w=_medical.step(y,rows)")
    adapter.patch = patch
    sys.modules["Macro_Adapter"] = adapter
    source = path.read_text()
    source = replace(source, "'nominalwage_proxy']",
                     "'nominalwage_proxy','pressure','lg','labor_anchor','coreY_anchor','nonlabor_factor','growth']")
    exec(compile(source,str(path),"exec"), module.__dict__)
    module.SELECT = [module.SQ, module.BASE]
    out.mkdir(parents=True, exist_ok=True)
    try:
        results = module.capture(root,out,draft)
    finally:
        sys.modules.pop("Macro_Adapter",None)
    return results, module.SQ, module.BASE


def run_n3(root, out, capture, sq, baseline, prices):
    import importlib.util
    import types

    spec = importlib.util.spec_from_file_location("fixed_attribution", root/GAP/"Attribution_Runtime.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out.mkdir(parents=True, exist_ok=True)
    runner, settings = module.build(root, out, {"case":"BASE_REPLAY"})
    original_base = runner.base
    original_fiscal_base = runner.fiscal_base
    runner.base = {row["year"]:row for row in capture["records"] if row["case"] == baseline}
    runner.sq = {row["year"]:row for row in capture["records"] if row["case"] == sq}
    runner.medical_input["deflators"] = list(prices)
    runner.ci["deflators"] = list(prices)
    runner.ci["config"]["sq_wage_nominal_man"] = [row["nominalwage_proxy"] for row in runner.sq.values()]

    def fiscal_base(self, s, y):
        pb, sfa, ss, tail, scale = original_fiscal_base(s,y)
        # Fixed official fiscal and SFA boundaries. Map the regenerated national-
        # local model tax change once against the original N3 reference.
        tax_delta = self.base[y]["tax"] - original_base[y]["tax"]
        policy_delta = (self.base[y]["medical"]["policy_tax_delta_trn"] -
                        original_base[y]["medical"]["policy_tax_delta_trn"])
        cost_delta = (self.base[y]["medical"]["government_cost_delta_trn"] -
                      original_base[y]["medical"]["government_cost_delta_trn"])
        return pb+tax_delta+policy_delta-cost_delta, sfa, ss, tail, scale

    runner.fiscal_base = types.MethodType(fiscal_base, runner)
    # The inherited finance routine retains the exact same rollover and zero
    # additional G/I branch. Its output is the existing conditional candidate.
    annual, fiscal, bridge = runner.simulate(settings)
    if runner.checks:
        raise ValueError(runner.checks[:8])
    return annual, fiscal, runner.midpoints, runner.local_connection, runner.counter
