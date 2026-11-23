"""Attribute program cash requirements and independently reconstruct debt schedules."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parents[1] / "chatgpt-f-distribution-fiscal-integration-20261123"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PREVIOUS / "stage1-distribution"))
from Common import Checks, csv_rows, fixed_f, render
from Replay import load


def settings(runtime, folder, case):
    data = load(runtime / "handoff" / folder / "Inputs.json")
    return {**data["defaults"], **next(r for r in data["cases"] if r["id"] == case)}


def calculate(run, fixed, runtime, check):
    edu = settings(runtime, "f-education-20261121", "COMBINED")
    med = settings(runtime, "f-common-endoflife-finalization-20261121", "LATEST_F")
    prior = csv_rows((PREVIOUS / "stage2-fiscal/Annual.csv").read_bytes())
    cohort_issues = {}
    edu_open = med_open = assets = 0.
    rows = []
    for year, r, old in zip(range(2026,2056), load(run/"F_Actual_Annual.json"), prior, strict=True):
        check("year", (r["year"], int(old["year"])), (year, year))
        for key in ("tax_diagnostic_trn", "consolidated_partial_balance_proxy_trn"):
            check("fixed_F", r[key], float(fixed[year][key]))
        education_spend = r["net_additional_education_spend_trn"]
        credit = r["training_credit_trn"]
        edu_issue = education_spend * edu["bond_share"]
        grace = edu["grace_years"]
        duration = edu["amortization_years"]
        edu_redeem = sum(issue/duration for vintage, issue in cohort_issues.items()
                         if grace <= year-vintage < grace+duration)
        edu_interest = (edu_open+edu_issue/2) * edu["bond_rate"]
        edu_close = edu_open+edu_issue-edu_redeem
        cohort_issues[year] = edu_issue
        edu_gap = education_spend+credit+edu_interest+edu_redeem-edu_issue
        med_direct = r["medical_unassigned_direct_cash_requirement_trn"]
        med_interest = med_open * med["medical_debt_rate"]
        med_need = med_direct+med_interest
        assigned = med_need * med["finance_fraction"]
        mix = med["finance_mix"]
        tax = assigned*mix["TAX"]
        premium = assigned*mix["PREMIUM"]
        crowd = assigned*mix["OTHER_SPENDING"]
        debt_flow = assigned*mix["DEBT"]
        med_issue = max(0., debt_flow)
        med_redeem = min(med_open, max(0., -debt_flow))
        asset_add = max(0., -debt_flow-med_redeem)
        med_close = med_open+med_issue-med_redeem
        med_spend = med_direct-crowd
        med_gap = med_spend-tax-premium+med_interest+med_redeem+asset_add-med_issue
        for key, val in {
            "bond_begin_trn":edu_open, "bond_issue_trn":edu_issue, "bond_redemption_trn":edu_redeem,
            "bond_interest_trn":edu_interest, "bond_end_trn":edu_close,
            "education_unassigned_cash_finance_trn":edu_gap, "medical_finance_fraction":med["finance_fraction"],
            "medical_policy_interest_trn":med_interest, "medical_financing_tax_trn":tax,
            "medical_financing_premium_trn":premium, "medical_other_spending_crowded_trn":crowd,
            "medical_policy_net_financial_source_trn":debt_flow, "medical_policy_debt_issue_trn":med_issue,
            "medical_policy_debt_redemption_trn":med_redeem, "medical_policy_debt_stock_trn":med_close,
            "medical_policy_asset_addition_trn":asset_add, "medical_policy_financial_asset_stock_trn":assets+asset_add,
            "medical_unassigned_after_sources_trn":med_gap,
        }.items():
            check("program_module_bridge", val, r[key])
        check("medical_unassigned_share", med_gap, med_need*(1-med["finance_fraction"]))
        check("no_new_VAT_fund", r["fund_income_trn"], 0.)
        revenue = tax+premium-credit
        spend = education_spend+med_spend
        pb = revenue-spend
        interest = edu_interest+med_interest
        redemption = edu_redeem+med_redeem
        gross = edu_issue+med_issue
        net = gross-redemption
        cash = interest-pb+redemption+asset_add
        gap = cash-gross
        residual = gap-(edu_gap+med_gap)
        check("cash_bridge", residual, 0.)
        check("cash_bridge_net_issuance", gap, interest-pb+asset_add-net)
        check("stock_bridge", edu_close+med_close, edu_open+med_open+net)
        check("existing_consolidated_program_coverage", pb-interest,
              -r["education_total_cost_trn"]+r["partial_public_direct_balance_delta_trn"])
        check("existing_consolidation", r["consolidated_partial_balance_proxy_trn"],
              r["government_partial_balance_proxy_trn"]+r["insurer_known_change_and_program_balance_trn"])
        metrics = dict(covered_primary_revenue_net_trn=revenue, covered_primary_expenditure_net_trn=spend,
                       covered_PB_trn=pb, covered_interest_trn=interest, covered_redemption_trn=redemption,
                       covered_cash_need_including_redemptions_assets_trn=cash, covered_gross_issue_trn=gross,
                       covered_net_issue_trn=net, covered_debt_close_trn=edu_close+med_close,
                       covered_medical_asset_add_trn=asset_add, covered_unassigned_cash_trn=gap)
        for key, val in metrics.items():
            check("fixed_stage2", val, float(old[key]))
        rows.append(dict(year=year, **metrics, education_net_spend_trn=education_spend, education_credit_trn=credit,
                         education_interest_trn=edu_interest, education_redemption_trn=edu_redeem,
                         education_issue_trn=edu_issue, education_debt_open_trn=edu_open,
                         education_debt_close_trn=edu_close, education_unassigned_trn=edu_gap,
                         medical_direct_before_sources_trn=med_direct, medical_tax_trn=tax,
                         medical_premium_trn=premium, medical_spending_offset_trn=crowd, medical_net_spend_trn=med_spend,
                         medical_interest_trn=med_interest, medical_redemption_trn=med_redeem,
                         medical_issue_trn=med_issue, medical_debt_open_trn=med_open,
                         medical_debt_close_trn=med_close, medical_unassigned_trn=med_gap,
                         medical_assets_close_trn=assets+asset_add, closure_residual_trn=residual))
        edu_open, med_open, assets = edu_close, med_close, assets+asset_add
    return render(rows)


if __name__ == "__main__":
    source, reference, runtime, output = map(Path, sys.argv[1:])
    dependencies = load(PREVIOUS / "stage2-fiscal/Dependencies.json")
    fixed = fixed_f(reference, next(d for d in dependencies if d["local"] == "retrieved/Legacy_Annual.csv"))
    check = Checks()
    (output/"Annual.csv").write_bytes(calculate(source, fixed, runtime, check))
    check.save(output)
