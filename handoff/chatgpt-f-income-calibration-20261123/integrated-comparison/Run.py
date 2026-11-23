"""Join income incidence sensitivities to fixed macro and financial diagnostics."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HANDOFF = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0,str(HANDOFF/"chatgpt-f-distribution-fiscal-integration-20261123/stage1-distribution"))
from Common import Checks, csv_rows, render

PRIOR = HANDOFF/"chatgpt-f-middle-income-financing-20261123"
CASES = ("FIXED_F","PRIOR_GROSS","OBSERVED_SHARE","OBSERVED_SHARE_BURDEN","OBSERVED_THRESHOLD")
BASE = ("real_gdp_trn","nominal_gdp_trn","population","tax_diagnostic_trn","SQ_real_GDP","N3_real_GDP",
        "covered_PB_trn","covered_gross_issue_trn","covered_debt_close_trn","covered_unassigned_cash_trn")
INCOME = ("cash_median_nominal_yen","cash_median_real_2026_yen","synthetic_gini_before","synthetic_gini_cash")
FUNDING = ("covered_PB_trn","covered_gross_issue_trn","covered_debt_close_trn","covered_unassigned_cash_trn")
EXTRA = ("synthetic_gini_resources","post_median_cell","post_median_rank","income_tax_receipt_trn",
         "resident_tax_receipt_trn","pension_receipt_trn","A_yen_trn","B_used_yen_trn","C_cash_yen_trn",
         "A_exit_households","B_exit_households","C_exit_households","A_withdrawal_trn","C_withdrawal_trn")


def unique(rows,check):
    indexed={(r["year"],r["case"]):r for r in rows}
    check("unique_keys",len(indexed),len(rows))
    return indexed


def combine(income, check):
    previous = unique(csv_rows((PRIOR/"integrated/Annual.csv").read_bytes()),check)
    funding = unique(csv_rows((PRIOR/"financing-sensitivity/Annual.csv").read_bytes()),check)
    paths = unique(income,check)
    check("complete_income_panel",set(paths),{(str(y),c) for y in range(2026,2056) for c in CASES})
    rows = []
    differences = []
    for y in range(2026,2056):
        year = str(y)
        fixed=previous[year,"FIXED_F"]
        old=previous[year,"VAT_WAGE_ALLOCATION"]
        for key in FUNDING:
            check("read_only_finance_reference",float(fixed[key]),float(funding[year,"FIXED_F"][key]))
        for key in INCOME:
            check("fixed_income",float(paths[year,"FIXED_F"][key]),float(fixed[key]))
            check("prior_income",float(paths[year,"PRIOR_GROSS"][key]),float(old[key]))
        for case in CASES:
            r=paths[year,case]
            rows.append(dict(year=year,case=case,**{k:fixed[k] for k in BASE},
                             **{k:r[k] for k in (*INCOME,*EXTRA)},national_income_and_wage_medians="N/A",
                             national_gini="N/A",national_PB_and_debt_sustainability="N/A"))
            value=float(r["cash_median_real_2026_yen"])
            gini=float(r["synthetic_gini_cash"])
            differences.append(dict(year=year,case=case,
                                    real_median_delta_vs_fixed_yen=value-float(fixed["cash_median_real_2026_yen"]),
                                    real_median_delta_vs_prior_yen=value-float(old["cash_median_real_2026_yen"]),
                                    gini_delta_vs_fixed=gini-float(fixed["synthetic_gini_cash"]),
                                    gini_delta_vs_prior=gini-float(old["synthetic_gini_cash"]),
                                    GDP_effect="N/A_NO_MACRO_FEEDBACK"))
    return render(rows),render(differences)


if __name__=="__main__":
    income,output=map(Path,sys.argv[1:])
    check=Checks()
    for name,data in zip(("Annual.csv","Comparison.csv"),combine(csv_rows(income.read_bytes()),check),strict=True):
        (output/name).write_bytes(data)
    check.save(output)
