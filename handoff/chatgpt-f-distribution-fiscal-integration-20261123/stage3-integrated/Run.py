"""Join verified distribution and program financing to fresh F model runs."""
import importlib.util
import sys
from pathlib import Path
sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
distribution = here.parent/"stage1-distribution"
fiscal = here.parent/"stage2-fiscal"
sys.path.insert(0,str(distribution))
from Common import Checks, csv_rows, fixed_f, read_verified, render
from Replay import load

def module(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def calculate(run, fixed, sources, check):
    dist = module("distribution",distribution/"Run.py")
    fin = module("fiscal",fiscal/"Run.py")
    subsidiary_check = Checks()
    d = dist.calculate(run,fixed,subsidiary_check)[0]
    f = fin.calculate(run,fixed,subsidiary_check)[0]
    check("stage1_fixed_annual_bytes",d,sources["stage1-distribution/Annual.csv"])
    check("stage2_fixed_annual_bytes",f,sources["stage2-fiscal/Annual.csv"])
    annual, differences, goals = [], [], []
    base_fields = ("real_gdp_trn","nominal_gdp_trn","tax_diagnostic_trn","I_policy_real_trn",
                   "capital_total_real_trn","consolidated_partial_balance_proxy_trn")
    for year,r,distribution_row,fiscal_row in zip(range(2026,2056),
           load(run/"F_Actual_Annual.json"),csv_rows(d),csv_rows(f),strict=True):
        check("integrated_annual_keys",(r["year"],int(distribution_row["year"]),int(fiscal_row["year"])),
              (year,year,year))
        for key in base_fields:
            check("fixed_F",r[key],float(fixed[year][key]))
        check("fiscal_reconciliation",float(fiscal_row["fixed_macro_tax_diagnostic_trn"]),r["tax_diagnostic_trn"])
        check("fiscal_reconciliation",float(fiscal_row["fixed_consolidated_partial_balance_trn"]),
              r["consolidated_partial_balance_proxy_trn"])
        check("distribution_reconciliation",float(distribution_row["synthetic_gini_cash"]),
              r["synthetic_equivalized_gini_after"])
        check("distribution_reconciliation",float(distribution_row["real_wage_proxy_man"]),r["real_wage_proxy_man"])
        check("no_new_trigger",(r["gini_external_2035"],r["gini_triggered"],r["fund_income_trn"],r["triggered"]),
              (None,0,0.,0))
        state = {k:r[k] for k in base_fields}
        state.update(population=r["population"], real_growth_pct=r["real_growth_pct"],
                     macro_cash_DI_proxy_trn=r["macro_cash_DI_proxy_trn"],
                     household_disposable_nominal_trn=r["household_disposable_nominal_trn"],
                     A_relief_trn=r["A_relief_trn"], B_used_trn=r["B_used_trn"], C_cash_trn=r["C_cash_trn"])
        controls = {k:float(fixed[year][k]) for k in ("SQ_real_GDP","N3_real_GDP")}
        annual.append(dict(year=year, **state, **controls,
                           **{k:v for k,v in distribution_row.items() if k!="year"},
                           **{k:v for k,v in fiscal_row.items() if k!="year"},
                           diagnostic_tax_to_nominal_gdp=r["tax_diagnostic_trn"]/r["nominal_gdp_trn"],
                           education_trigger_adopted=r["triggered"], vat_fund_income_trn=r["fund_income_trn"]))
        differences.append(dict(year=year, **{k+"_vs_fixed_F":r[k]-float(fixed[year][k]) for k in base_fields},
                                real_GDP_vs_fixed_SQ=r["real_gdp_trn"]-controls["SQ_real_GDP"],
                                real_GDP_vs_fixed_N3=r["real_gdp_trn"]-controls["N3_real_GDP"],
                                synthetic_gini_delta_vs_same_cells_before=float(distribution_row["synthetic_gini_cash"])-
                                    float(distribution_row["synthetic_gini_before"]),
                                education_medical_PB_vs_fixed_F="N/A_scope_not_previously_reported"))
        if year in (2035,2055):
            goals.append(dict(year=year, population_model=r["population"],
                              population_goal_85m_model_test=("PASS_MODEL" if r["population"]>=85e6 else "FAIL_MODEL")
                                  if year==2055 else "N/A_target_year_2055",
                              population_below_100m_2035=int(r["population"]<100e6) if year==2035 else "N/A",
                              national_gini_target="INDETERMINATE", national_tax_to_GDP_target="INDETERMINATE",
                              national_fiscal_sustainability="INDETERMINATE",
                              fiscal_scope="EDUCATION_AND_MEDICAL_INCREMENTAL_ONLY",
                              observed_gini_trigger_input="N/A"))
    return tuple(map(render,(annual,differences,goals)))

if __name__=="__main__":
    run,replay,reference,output=map(Path,sys.argv[1:])
    deps=load(here/"Dependencies.json")
    fixed=fixed_f(reference,next(d for d in deps if d["local"]=="retrieved/Legacy_Annual.csv"))
    sources={}
    for d in deps:
        if d["local"].startswith(("stage1-distribution/","stage2-fiscal/")):
            sources[d["local"]]=read_verified(here.parent/d["local"],d)
    check=Checks()
    for name in ("F_Actual_Annual.json","Household_Cells.json"):
        check("independent_runtime_bytes",(run/name).read_bytes(),(replay/name).read_bytes())
    a,b=calculate(run,fixed,sources,check),calculate(replay,fixed,sources,check)
    for name,left,right in zip(("Annual.csv","Comparison.csv","Targets.csv"),a,b,strict=True):
        check("independent_CSV_bytes",left,right)
        (output/name).write_bytes(left)
    check.save(output)
