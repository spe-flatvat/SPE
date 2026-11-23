"""Model only the additional education financing vintages and their cash service."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HANDOFF = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HANDOFF/"chatgpt-f-distribution-fiscal-integration-20261123/stage1-distribution"))
from Common import Checks, csv_rows, render
from Replay import load

CASES = ("FIXED_F", "ISSUE_ALL_EDUCATION", "REFINANCE_EXTERNAL")
RATE = .02
GRACE = 5
AMORTIZATION = 20


def calculate(check, fixed):
    outputs = []
    differences = []
    for case in CASES:
        cohorts = []
        opening = 0.
        for year, row in zip(range(2026,2056),fixed,strict=True):
            check("year", int(row["year"]), year)
            r = {k:float(v) for k,v in row.items()}
            pb = r["covered_PB_trn"]
            old_interest = r["covered_interest_trn"]
            old_maturity = r["covered_redemption_trn"]
            old_issue = r["covered_gross_issue_trn"]
            old_close = r["covered_debt_close_trn"]
            assets = r["covered_medical_asset_add_trn"]
            education = r["education_unassigned_trn"]
            medical = r["medical_unassigned_trn"]
            check("fixed_cash", old_interest-pb+old_maturity+assets-old_issue, r["covered_unassigned_cash_trn"])
            check("fixed_split", education+medical, r["covered_unassigned_cash_trn"])
            check("fixed_education_residual",
                  r["education_credit_trn"]+r["education_interest_trn"]+r["education_redemption_trn"],education)
            maturity = sum(issue/AMORTIZATION for vintage,issue in cohorts if GRACE<=year-vintage<GRACE+AMORTIZATION)
            opening_interest = RATE*opening
            # Full issuance covers interest on half of this year's own issue as well.
            if case=="ISSUE_ALL_EDUCATION":
                issue = (education+maturity+opening_interest)/(1-RATE/2)
                external = 0.
            elif case=="REFINANCE_EXTERNAL":
                issue = r["education_redemption_trn"]+maturity
                external = r["education_credit_trn"]+r["education_interest_trn"]+opening_interest+RATE*issue/2
            else:
                issue = external = 0.
            interest = opening_interest+RATE*issue/2
            close = opening+issue-maturity
            cohorts.append((year,issue))
            remaining = sum(amount*(1-min(AMORTIZATION,max(0,year-vintage-GRACE+1))/AMORTIZATION)
                            for vintage,amount in cohorts)
            check("vintage_principal", close, remaining)
            edu_left = education+interest+maturity-issue-external
            check("education_closure", edu_left, education if case=="FIXED_F" else 0.)
            gap = old_interest+interest-pb+old_maturity+maturity+assets-old_issue-issue-external
            check("combined_cash", gap, edu_left+medical)
            check("combined_stock_flow", old_close+close,
                  r["education_debt_open_trn"]+r["medical_debt_open_trn"]+opening
                  +old_issue+issue-old_maturity-maturity)
            check("no_medical_transfer", gap-edu_left, medical)
            outputs.append(dict(year=year,case=case,covered_PB_trn=pb,covered_interest_trn=old_interest+interest,
                                covered_redemption_trn=old_maturity+maturity,covered_assets_trn=assets,
                                covered_gross_issue_trn=old_issue+issue,covered_net_issue_trn=old_issue+issue-old_maturity-maturity,
                                covered_debt_close_trn=old_close+close,covered_unassigned_cash_trn=gap,
                                education_unassigned_trn=edu_left,medical_unassigned_trn=medical,
                                external_unidentified_trn=external,added_issue_trn=issue,added_interest_trn=interest,
                                added_redemption_trn=maturity,added_debt_open_trn=opening,added_debt_close_trn=close))
            differences.append(dict(year=year,case=case,delta_PB_trn=0.,delta_gross_issue_trn=issue,
                                    delta_interest_trn=interest,delta_redemption_trn=maturity,delta_debt_trn=close,
                                    delta_unassigned_trn=gap-r["covered_unassigned_cash_trn"],external_unidentified_trn=external))
            opening = close
    return render(outputs),render(differences)


if __name__=="__main__":
    output = Path(sys.argv[1])
    check = Checks()
    prior = HANDOFF/"chatgpt-f-median-fiscal-residual-20261123/fiscal-residual/Annual.csv"
    integrated = HANDOFF/"chatgpt-f-median-fiscal-residual-20261123/integrated-comparison/Annual.csv"
    fixed = csv_rows(prior.read_bytes())
    for source, benchmark in zip(fixed,csv_rows(integrated.read_bytes()),strict=True):
        check("integrated_year",source["year"],benchmark["year"])
        for key in ("covered_PB_trn","covered_interest_trn","covered_redemption_trn","covered_gross_issue_trn",
                    "covered_net_issue_trn","covered_debt_close_trn","covered_medical_asset_add_trn",
                    "covered_unassigned_cash_trn"):
            check("fixed_reference",float(source[key]),float(benchmark[key]))
    for name,data in zip(("Annual.csv","Comparison.csv"),calculate(check,fixed),strict=True):
        (output/name).write_bytes(data)
    check.save(output)
