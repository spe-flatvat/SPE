"""Run the four-stage incidence pipeline and produce fixed-F comparisons."""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("purchasing", ROOT / "stage3-purchasing-power/Run.py")
purchasing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(purchasing)
income = purchasing.income
benefits = income.benefits

STAGES = ("stage1-benefits-burdens","stage2-income-incidence","stage3-purchasing-power","stage4-integrated")


def run(runtime,replay,out):
    folders = [out/s for s in STAGES]
    data = benefits.calculate(runtime,replay,folders[0])
    income.calculate(data,folders[1])
    purchasing.calculate(data,folders[2])
    check = income.prior.Checks()
    read = lambda path: income.prior.csv_rows(path.read_bytes())
    money = {(r["year"],r["case"]):r for r in read(folders[1]/"Annual.csv") if r["weights"]=="FIXED"}
    power = {(r["year"],r["case"],r["group"]):r for r in read(folders[2]/"Groups.csv")}
    policy = {(r["year"],r["case"]):r for r in read(folders[0]/"Annual.csv")}
    distribution = {(r["year"],r["case"],r["group"]):r
                    for r in read(folders[1]/"Groups.csv") if r["weights"]=="FIXED"}
    actual = {(str(year),case): benefits.total(rows,"C_cash_yen")/1e12
              for year,case,rows,_,_ in data}
    comparison = []
    check("full_case_year_count",len(money),30*len(benefits.CASES))
    for (year,case),row in money.items():
        fixed = money[year,"FIXED_F"]
        record = dict(year=year,case=case,median_cell=row["median_cell"],median_rank=row["median_rank"])
        for key in ("cash_median_real_2026_yen","cash_median_nominal_yen","synthetic_cash_gini"):
            val = float(row[key])
            delta = val - float(fixed[key])
            if case=="FIXED_F":
                check("zero_fixed_delta",delta,0.)
            record.update({key:val,key+"_delta_fixed":delta})
        for group in ("Q2","Q3","Q4"):
            for rows,keys in ((power,("cash_real_2026_yen","B_value_real_2026_yen","VAT_price_real_2026_yen",
                                      "cash_plus_VAT_fixed_basket_real_2026_yen")),
                              (distribution,("A_yen","C_cash_yen","income_tax","resident_tax","pension",
                                             "A_income_tax","A_resident_tax","net_benefit"))):
                for key in keys:
                    val = float(rows[year,case,group][key])
                    delta = val-float(rows[year,"FIXED_F",group][key])
                    record.update({group+"_"+key:val,group+"_"+key+"_delta_fixed":delta})
            check("same_basket_price_no_macro_feedback",
                  record[group+"_VAT_price_real_2026_yen_delta_fixed"],0.)
        record["C_unallocated_trn"] = float(policy[year,case]["C_unallocated_trn"]) if (year,case) in policy else (
            actual[year,"FIXED_F"]-actual[year,case])
        comparison.append(record)
    benefits.write(folders[3],"Comparison.csv",comparison)
    check.save(folders[3])


if __name__ == "__main__":
    run(*map(Path,sys.argv[1:]))
