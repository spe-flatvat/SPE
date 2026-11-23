"""Fixed-basket VAT equivalent and in-kind value in separate columns."""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("income", ROOT / "stage2-income-incidence/Run.py")
income = importlib.util.module_from_spec(spec)
spec.loader.exec_module(income)
benefits = income.benefits


def calculate(data, out):
    check = income.prior.Checks()
    annual, distribution = [], []
    for year,case,rows,scale,macro in data:
        check("VAT_household_price_allocation",
              benefits.total(rows,"VAT_price_effect_yen")/1e12, macro["VAT_price_effect_trn"])
        check("VAT_flow_excludes_wage", macro["VAT_price_effect_trn"],
              macro["household_direct_price_benefit_trn"] if year>2026 else 0.)
        for r in rows:
            check("cash_in_kind_separation", r["resources"]-r["cash"],r["B_used_yen"])
            check("B_no_added_utilization", 0 <= r["B_used_yen"] <= r["B_face_yen"],True)
        _,median = income.prior.median(rows,"cash")
        annual.append(dict(year=year,case=case,cash_median_cell=median["id"],
                           cash_real_2026_yen_at_cell=median["cash"]/scale,
                           B_value_real_2026_yen_at_cell=median["B_used_yen"]/scale,
                           resources_real_2026_yen_at_cell=median["resources"]/scale,
                           VAT_price_real_2026_yen_at_cell=median["VAT_price_effect_yen"]/scale,
                           cash_plus_VAT_fixed_basket_real_2026_yen_at_cell=
                               (median["cash"]+median["VAT_price_effect_yen"])/scale,
                           VAT_price_trn=macro["VAT_price_effect_trn"],
                           VAT_minus_current_SQ_price_trn=macro["price_F_minus_current_SQ_trn"],
                           B_used_trn=benefits.total(rows,"B_used_yen")/1e12,
                           B_fixed_use_service_cost_trn=sum(r["B_service_cost_yen"]*r["households"]
                               for r in rows if r["B_used_yen"])/1e12,
                           B_fixed_use_admin_trn=sum(r["B_admin_yen"]*r["households"]
                               for r in rows if r["B_used_yen"])/1e12,
                           synthetic_resources_gini=income.prior.gini(rows,"resources")))
        for name,subset in income.groups(rows):
            weight = sum(r["households"] for r in subset)
            cash,b,vat = (benefits.total(subset,k)/weight/scale for k in ("cash","B_used_yen","VAT_price_effect_yen"))
            res = benefits.total(subset,"resources")/weight/scale
            check("group_in_kind_bridge",res,cash+b)
            distribution.append(dict(year=year,case=case,group=name,households=weight,
                                     cash_real_2026_yen=cash,B_value_real_2026_yen=b,resources_real_2026_yen=res,
                                     VAT_price_real_2026_yen=vat,cash_plus_VAT_fixed_basket_real_2026_yen=cash+vat))
    benefits.write(out,"Annual.csv",annual)
    benefits.write(out,"Groups.csv",distribution)
    check.save(out)


if __name__ == "__main__":
    runtime,replay,out = map(Path,sys.argv[1:])
    calculate(benefits.calculate(runtime,replay,out.parent/"stage1-benefits-burdens"),out)
