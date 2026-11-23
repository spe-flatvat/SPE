"""Reconcile the fixed education and medical incremental funding subaccounts."""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sibling = Path(__file__).resolve().parents[1]/"stage1-distribution"
sys.path.insert(0,str(sibling))
from Common import Checks, fixed_f, render
from Replay import load

def calculate(run, fixed, check):
    annual, differences = [], []
    edu_open = med_open = asset_open = 0.
    for year, r in zip(range(2026,2056),load(run/"F_Actual_Annual.json"),strict=True):
        check("year",r["year"],year)
        for key in ("real_gdp_trn","tax_diagnostic_trn","consolidated_partial_balance_proxy_trn"):
            check("fixed_F",r[key],float(fixed[year][key]))
        edu_gross, edu_redemption, edu_close, edu_interest = (
            r[k] for k in ("bond_issue_trn","bond_redemption_trn","bond_end_trn","bond_interest_trn"))
        med_gross, med_redemption, med_close, med_interest = (
            r[k] for k in ("medical_policy_debt_issue_trn","medical_policy_debt_redemption_trn",
                           "medical_policy_debt_stock_trn","medical_policy_interest_trn"))
        asset_add = r["medical_policy_asset_addition_trn"]
        education_credit = r["training_credit_trn"]
        med_tax, med_premium = r["medical_financing_tax_trn"],r["medical_financing_premium_trn"]
        # Net medical clinical transfers before incremental financing, distinct
        # from gross provider spending and from national insurer expenditure.
        med_cost = r["medical_unassigned_direct_cash_requirement_trn"]-r["medical_other_spending_crowded_trn"]
        income = med_tax+med_premium-education_credit
        expenditure = r["net_additional_education_spend_trn"]+med_cost
        pb = income-expenditure
        interest = edu_interest+med_interest
        deficit = interest-pb
        redemption = edu_redemption+med_redemption
        gross = edu_gross+med_gross
        net = gross-redemption
        cash_need = deficit+redemption+asset_add
        unassigned = cash_need-gross
        check("education_open",r["bond_begin_trn"],edu_open)
        check("education_debt",edu_close,edu_open+edu_gross-edu_redemption)
        check("medical_debt",med_close,med_open+med_gross-med_redemption)
        check("medical_assets",r["medical_policy_financial_asset_stock_trn"],asset_open+asset_add)
        check("gross_and_net_issuance",edu_close+med_close,edu_open+med_open+net)
        check("medical_financing_sources",med_gross-med_redemption-asset_add,
              r["medical_policy_net_financial_source_trn"])
        check("education_primary_cost",r["education_primary_cost_trn"],
              r["net_additional_education_spend_trn"]+education_credit)
        check("program_funding_gap",unassigned,
              r["education_unassigned_cash_finance_trn"]+r["medical_unassigned_after_sources_trn"])
        check("program_consolidated_balance",pb-interest,
              -r["education_total_cost_trn"]+r["partial_public_direct_balance_delta_trn"])
        check("fixed_tax_VAT_bridge",r["tax_diagnostic_trn"],
              r["modeled_VAT_trn"]+r["tax_residual_after_VAT_trn"])
        check("fixed_government_insurer_consolidation",r["consolidated_partial_balance_proxy_trn"],
              r["government_partial_balance_proxy_trn"]+r["insurer_known_change_and_program_balance_trn"])
        check("fixed_internal_transfer_elimination",r["internal_transfer_consolidated_trn"],0.)
        check("no_new_VAT_fund",r["fund_income_trn"],0.)
        annual.append(dict(year=year, covered_primary_revenue_net_trn=income,
                           covered_primary_expenditure_net_trn=expenditure, covered_PB_trn=pb,
                           medical_tax_trn=med_tax, medical_premium_trn=med_premium,
                           education_tax_expenditure_trn=education_credit, education_interest_trn=edu_interest,
                           medical_interest_trn=med_interest, covered_interest_trn=interest,
                           covered_post_interest_deficit_trn=deficit, covered_cash_need_including_redemptions_assets_trn=cash_need,
                           education_issue_trn=edu_gross, medical_issue_trn=med_gross,
                           covered_gross_issue_trn=gross, covered_net_issue_trn=net,
                           covered_redemption_trn=redemption, covered_debt_open_trn=edu_open+med_open,
                           covered_debt_close_trn=edu_close+med_close,
                           covered_medical_asset_add_trn=asset_add,
                           covered_medical_asset_close_trn=r["medical_policy_financial_asset_stock_trn"],
                           covered_unassigned_cash_trn=unassigned,
                           fixed_macro_tax_diagnostic_trn=r["tax_diagnostic_trn"],
                           fixed_covered_VAT_trn=r["modeled_VAT_trn"],
                           fixed_consolidated_partial_balance_trn=r["consolidated_partial_balance_proxy_trn"],
                           national_general_government_PB="N/A", national_bond_issue="N/A", national_debt="N/A",
                           national_refinancing_issue="N/A", national_funding_rate="N/A",
                           policy_rate_pct=0.75 if year==2026 else "N/A"))
        differences.append(dict(year=year, tax_change_vs_fixed_F_trn=r["tax_diagnostic_trn"]-float(fixed[year]["tax_diagnostic_trn"]),
                                balance_change_vs_fixed_F_trn=r["consolidated_partial_balance_proxy_trn"]-
                                float(fixed[year]["consolidated_partial_balance_proxy_trn"]),
                                program_gross_issue_minus_existing_education_trn=med_gross,
                                program_net_issue_minus_existing_education_trn=med_gross-med_redemption,
                                program_debt_close_minus_existing_education_trn=med_close,
                                program_cash_gap_minus_existing_education_trn=r["medical_unassigned_after_sources_trn"]))
        edu_open,med_open,asset_open=edu_close,med_close,r["medical_policy_financial_asset_stock_trn"]
    return render(annual),render(differences)

if __name__=="__main__":
    run,replay,reference,output=map(Path,sys.argv[1:])
    deps=load(Path(__file__).with_name("Dependencies.json"))
    fixed=fixed_f(reference,next(d for d in deps if d["local"]=="retrieved/Legacy_Annual.csv"))
    check=Checks()
    filename="F_Actual_Annual.json"
    check("independent_replay_input",(run/filename).read_bytes(),(replay/filename).read_bytes())
    a,b=calculate(run,fixed,check),calculate(replay,fixed,check)
    for name,left,right in zip(("Annual.csv","Comparison.csv"),a,b,strict=True):
        check("independent_CSV_bytes",left,right)
        (output/name).write_bytes(left)
    check.save(output)
