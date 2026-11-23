"""Compare isolated shapes for wage attribution and education financing."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HANDOFF = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HANDOFF/"chatgpt-f-distribution-fiscal-integration-20261123/stage1-distribution"))
from Common import Checks, csv_rows, render

CASES = {
    "FIXED_F": ("FIXED_F", "FIXED_F"),
    "VAT_WAGE_ALLOCATION": ("VAT_WAGE_ALLOCATION", "FIXED_F"),
    "ISSUE_ALL_EDUCATION": ("FIXED_F", "ISSUE_ALL_EDUCATION"),
    "REFINANCE_EXTERNAL": ("FIXED_F", "REFINANCE_EXTERNAL"),
}
MACRO = ("real_gdp_trn","nominal_gdp_trn","population","tax_diagnostic_trn","SQ_real_GDP","N3_real_GDP")
INCOME = ("cash_median_nominal_yen","cash_median_real_2026_yen","synthetic_gini_before","synthetic_gini_cash")
FISCAL = ("covered_PB_trn","covered_interest_trn","covered_redemption_trn","covered_gross_issue_trn",
          "covered_net_issue_trn","covered_debt_close_trn","covered_unassigned_cash_trn")
OTHER = ("external_unidentified_trn","education_unassigned_trn","medical_unassigned_trn")


def by_key(rows, check):
    indexed = {(r["year"], r["case"]):r for r in rows}
    check("unique_year_case",len(indexed),len(rows))
    return indexed


def calculate(base, incomes, financing, check):
    annual, differences = [], []
    a = by_key(incomes,check)
    b = by_key(financing,check)
    check("income_coverage",len(a),90)
    check("financing_coverage",len(b),90)
    for y,fixed in zip(range(2026,2056),base,strict=True):
        year = str(y)
        check("year_join",year,fixed["year"])
        check("fixed_trigger",fixed["gini_triggered"],"0")
        for key in ("national_gini","national_income_median","national_real_wage_median",
                    "national_general_government_PB","national_bond_issue","national_debt",
                    "national_refinancing_issue","national_funding_rate"):
            check("fixed_NA",fixed[key],"N/A")
        for key in INCOME:
            check("fixed_income",float(a[year,"FIXED_F"][key]),float(fixed[key]))
        for key in FISCAL:
            check("fixed_finance",float(b[year,"FIXED_F"][key]),float(fixed[key]))
        for case,(ac,bc) in CASES.items():
            income = a[year,ac]
            funding = b[year,bc]
            result = {key:income[key] for key in INCOME} | {key:funding[key] for key in (*FISCAL,*OTHER)}
            check("one_branch_only",ac=="FIXED_F" or bc=="FIXED_F",True)
            check("macro_invariance",income["real_GDP_effect"],"N/A_NO_MACRO_FEEDBACK")
            check("medical_separate",funding["medical_unassigned_trn"],b[year,"FIXED_F"]["medical_unassigned_trn"])
            annual.append(dict(year=y,case=case, **{k:fixed[k] for k in MACRO}, **result))
            delta = {k:float(result[k])-float(fixed[k]) for k in (*INCOME,*FISCAL)}
            for k in (FISCAL if ac!="FIXED_F" else INCOME):
                check("other_branch_fixed",delta[k],0.)
            differences.append(dict(year=y,case=case,**{k:round(v,10) for k,v in delta.items()},
                                    fixed_GDP_minus_SQ_trn=float(fixed["real_gdp_trn"])-float(fixed["SQ_real_GDP"]),
                                    fixed_GDP_minus_N3_trn=float(fixed["real_gdp_trn"])-float(fixed["N3_real_GDP"]),
                                    GDP_response="N/A_NO_MACRO_FEEDBACK"))
    return render(annual),render(differences)


if __name__=="__main__":
    income, finance, output = map(Path,sys.argv[1:])
    prior = HANDOFF/"chatgpt-f-median-fiscal-residual-20261123/integrated-comparison/Annual.csv"
    check = Checks()
    result = calculate(*(csv_rows(p.read_bytes()) for p in (prior,income,finance)),check)
    for name,data in zip(("Annual.csv","Comparison.csv"),result,strict=True):
        (output/name).write_bytes(data)
    check.save(output)
