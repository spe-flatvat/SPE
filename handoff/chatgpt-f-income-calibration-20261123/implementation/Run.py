"""Apply observed employee-income shares and conditional marginal burdens."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HANDOFF = HERE.parents[1]
PRIOR = HANDOFF/"chatgpt-f-middle-income-financing-20261123/middle-income"
EVIDENCE = HERE.parent/"calibration-evidence"
sys.dont_write_bytecode = True
sys.path.insert(0, str(EVIDENCE))
from Run import load_shares

spec = importlib.util.spec_from_file_location("prior_wage", PRIOR/"Run.py")
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)

CASES = ("FIXED_F", "PRIOR_GROSS", "OBSERVED_SHARE", "OBSERVED_SHARE_BURDEN", "OBSERVED_THRESHOLD")
BENEFITS = {"A": "A_yen", "B": "B_used_yen", "C": "C_cash_yen"}


def results(run, check):
    shares = load_shares(EVIDENCE/"Wage_Shares.csv")
    settings = prior.load(EVIDENCE/"Inputs.json")
    rates = settings["burden_sensitivity"]
    thresholds = settings["nominal_household_thresholds"]
    cells = prior.load(run/"Household_Cells.json")
    previous = {(int(r["year"]),r["case"]):r for r in prior.csv_rows((PRIOR/"Annual.csv").read_bytes())}
    annual, distribution = [], []
    for year, macro in zip(range(2026,2056), prior.load(run/"F_Actual_Annual.json"), strict=True):
        check("year_and_trigger",(macro["year"],macro["gini_external_2035"],macro["gini_triggered"]),(year,None,0))
        grid = cells[str(year)]
        pool = macro["household_wage_allocation_trn"] if year>2026 else 0.
        scale = macro["common_deflator"]/(600/580)
        before_group = {(r["reference_income_group"],r["profile"]) for r in grid}
        fixed = None
        observed_wages = None
        for case in CASES:
            wage_bases = {}
            for r in grid:
                gross = r["gross_income_yen"]
                basis = gross if r["profile"] in prior.EMPLOYEE else 0.
                if case.startswith("OBSERVED") and r["profile"] == "EMP_CHILD":
                    share = next(s for limit,s in shares if gross/r["idx"] <= limit)
                    basis *= share
                    check("observed_wage_component_bounded", 0 < basis < gross, True)
                wage_bases[r["id"]] = basis
            denominator = sum(wage_bases[r["id"]]*r["households"] for r in grid)
            rows = []
            for r in grid:
                wage = pool*1e12*wage_bases[r["id"]]/denominator if case!="FIXED_F" else 0.
                pension = national = local = 0.
                if case=="OBSERVED_SHARE_BURDEN":
                    pension = wage*rates["employee_pension_rate_continuous"]
                    taxable = (wage-pension)*rates["illustrative_taxable_share_of_wage_after_pension"]
                    national = taxable*rates["illustrative_national_income_tax_rate"]
                    local = taxable*rates["illustrative_resident_tax_rate"]
                net = wage-pension-national-local
                adjusted = dict(r, wage=wage, pension=pension, income_tax=national, resident_tax=local, net=net,
                                pre=r["baseline_DI_yen"]+net, cash=r["cash_DI_after_yen"]+net,
                                resources=r["resources_after_yen"]+net)
                for key, boundary in thresholds.items():
                    was = r["gross_income_yen"] <= boundary
                    now = r["gross_income_yen"]+wage <= boundary
                    adjusted.update({key+"_eligible": int(now), key+"_exit":int(was and not now),
                                     key+"_enter":int(now and not was),
                                     key+"_paid":int(r[BENEFITS[key]]>0),
                                     key+"_exit_paid":int(was and not now and r[BENEFITS[key]]>0)})
                losses = {key: r[field] if case=="OBSERVED_THRESHOLD" and adjusted[key+"_exit"] else 0.
                          for key,field in BENEFITS.items()}
                adjusted.update({BENEFITS[key]:r[BENEFITS[key]]-loss for key,loss in losses.items()})
                adjusted.update({key+"_withdrawal":loss for key,loss in losses.items()})
                adjusted["cash"] -= losses["A"]+losses["C"]
                adjusted["resources"] -= sum(losses.values())
                for key,field in BENEFITS.items():
                    adjusted[key+"_paid"] = int(adjusted[field]>0)
                check("cash_benefit_bridge", adjusted["cash"]-adjusted["pre"]+losses["A"]+losses["C"],
                      r["cash_DI_after_yen"]-r["baseline_DI_yen"])
                check("in_kind_bridge", adjusted["resources"]-adjusted["cash"],adjusted["B_used_yen"])
                rows.append(adjusted)
            if case=="OBSERVED_SHARE":
                observed_wages = [r["wage"] for r in rows]
            if case=="OBSERVED_SHARE_BURDEN":
                check("burden_only_toggle",[r["wage"] for r in rows],observed_wages)

            def total(key, source=rows):
                return sum(r[key]*r["households"] for r in source)

            def trn(key):
                return total(key)/1e12

            allocated = trn("wage")
            check("wage_pool_conserved",allocated,0. if case=="FIXED_F" else pool)
            check("household_receipt_balance",trn("net")+trn("pension")+trn("income_tax")+trn("resident_tax"),allocated)
            for label, datum in (("A","A_relief_trn"),("B","B_used_trn"),("C","C_cash_trn")):
                check("program_balance",trn(BENEFITS[label])+trn(label+"_withdrawal"),macro[datum])
            check("cash_incidence_balance",trn("net")-trn("A_withdrawal")-trn("C_withdrawal"),
                  sum((r["cash"]-r["cash_DI_after_yen"])*r["households"] for r in rows)/1e12)
            _, pre = prior.median(rows,"pre")
            rank, post = prior.median(rows,"cash")
            metrics = dict(baseline_cash_median_nominal_yen=pre["pre"],cash_median_nominal_yen=post["cash"],
                           baseline_cash_median_real_2026_yen=pre["pre"]/scale,cash_median_real_2026_yen=post["cash"]/scale,
                           synthetic_gini_before=prior.gini(rows,"pre"),synthetic_gini_cash=prior.gini(rows,"cash"),
                           synthetic_gini_resources=prior.gini(rows,"resources"),
                           post_median_cell=post["id"],post_median_rank=rank)
            if case in ("FIXED_F","PRIOR_GROSS"):
                old = previous[year,"FIXED_F" if case=="FIXED_F" else "VAT_WAGE_ALLOCATION"]
                for key,value in metrics.items():
                    check("prior_reproduction",value,type(value)(old[key]))
            if case=="FIXED_F":
                fixed = metrics
            for label in thresholds:
                check("eligibility_bridge",total(label+"_eligible"),
                      sum(r["households"] for r in grid if r["gross_income_yen"]<=thresholds[label])
                      +total(label+"_enter")-total(label+"_exit"))
            annual.append(dict(year=year,case=case,**metrics,
                               delta_real_median_yen=metrics["cash_median_real_2026_yen"]-fixed["cash_median_real_2026_yen"],
                               delta_cash_gini=metrics["synthetic_gini_cash"]-fixed["synthetic_gini_cash"],
                               median_gross_yen=post["gross_income_yen"]+post["wage"],
                               median_wage_yen=post["wage"],median_income_tax_delta_yen=post["income_tax"],
                               median_resident_tax_delta_yen=post["resident_tax"],median_pension_delta_yen=post["pension"],
                               **{f"median_{k}":post[k] for k in (*BENEFITS.values(),*(x+"_eligible" for x in thresholds))},
                               pooled_wage_trn=pool,allocated_wage_trn=allocated,household_net_wage_gain_trn=trn("net"),
                               income_tax_receipt_trn=trn("income_tax"),resident_tax_receipt_trn=trn("resident_tax"),
                               pension_receipt_trn=trn("pension"),
                               **{k+"_households":total(k) for label in thresholds
                                  for k in (label+"_eligible",label+"_enter",label+"_exit",label+"_paid",label+"_exit_paid")},
                               **{k+"_trn":trn(k) for k in (*BENEFITS.values(),*(x+"_withdrawal" for x in thresholds))}))
            group_total = 0.
            for group,profile in sorted(before_group):
                members = [r for r in rows if (r["reference_income_group"],r["profile"])==(group,profile)]
                weight = sum(r["households"] for r in members)
                group_wage = total("wage",members)
                group_total += group_wage
                distribution.append(dict(year=year,case=case,group=group,profile=profile,
                                         employed_proxy=int(profile in prior.EMPLOYEE),
                                         child=members[0]["child"],households=round(weight,3),
                                         gross_wage_delta_per_hh=round(group_wage/weight,3),
                                         **{key+"_per_hh":round(total(key,members)/weight,3)
                                            for key in ("income_tax","resident_tax","pension","cash",*BENEFITS.values())},
                                         net_real_delta_per_hh=round(sum((r["cash"]-r["cash_DI_after_yen"])*r["households"] for r in members)/weight/scale,3),
                                         **{key+"_share":round(total(key,members)/weight,6) for label in thresholds
                                            for key in (label+"_eligible",label+"_paid")}))
            check("income_profile_pool_reconciliation",group_total/1e12,allocated)
    return prior.render(annual),prior.render(distribution)


if __name__=="__main__":
    run,output=map(Path,sys.argv[1:])
    check=prior.Checks()
    annual, distribution = results(run,check)
    (output/"Annual.csv").write_bytes(annual)
    for case in CASES:
        selected = [r for r in prior.csv_rows(distribution) if r["case"]==case]
        (output/f"Distribution_{case}.csv").write_bytes(prior.render(selected))
    check.save(output)
