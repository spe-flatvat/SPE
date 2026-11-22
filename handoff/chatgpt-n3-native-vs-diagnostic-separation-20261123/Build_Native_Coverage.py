#!/usr/bin/env python3
"""Classify the 22 fixed original-policy trace entries by active native scope.
No mechanism missing from the native runtime is filled with a new coefficient.
"""
import argparse,csv,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
PREV=ROOT/'handoff/chatgpt-n3-policy-gi-executor-financing-mapping-20261123'
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(out):
 old=list(csv.DictReader((PREV/'N3_Policy_Implementation_Expenditure_Trace.csv').open()))
 states={
 'A_VAT':('IMPLEMENTED_IN_NATIVE','ACTIVE_FIXED_RATE_PATH','schedule matches fixed path; realized tax/price/quantity partial-proxy bases','VAT_standard_rate; total_tax_diagnostic_proxy_trn','transaction base calibration, medical scope, KPI extension beyond fixed path'),
 'A_VAT_SWITCH':('PARTIAL_OR_PROXY','INACTIVE_FIXED_KPI_BRANCH','income-growth switch exists in component but kpi=FIXED turns it off in current native contract','component event hooks; fixed VAT_standard_rate','actual 2035 trigger observation and automatic adjustment in this selected path'),
 'A_INVOICE':('STRUCTURAL_ONLY','STRUCTURE_NO_MONETARY_EFFECT','invoice cost-saving interface exists without amount','native institutions invoice_cost_saving_yen=unknown','administrative cost baseline, reform execution cost and savings'),
 'A_LABOR_TAX':('PARTIAL_OR_PROXY','ACTIVE','30% tax calculation on synthetic category gross bases; local redesign unresolved','labor_gross_base_trn; policy_tax_delta_trn','national tax base, pension-income/local-tax treatment'),
 'A_FINANCIAL_TAX':('PARTIAL_OR_PROXY','ACTIVE','20% synthetic category allocation not national financial transaction microdata','financial_gross_base_trn; policy_tax_delta_trn','national income-source bases and distribution calibration'),
 'A_ALLOWANCE':('PARTIAL_OR_PROXY','ACTIVE','gross-flat calculation implemented in existing survey categories','policy_tax_delta_trn; household_policy_cash_nominal_trn','full legal deductions and national/local implementation contract'),
 'A_CORPORATE':('PARTIAL_OR_PROXY','ACTIVE','incentive eligibility and original private investment preserved; firm75 additional residual investment shared across native/control','corporate_profit_base_trn; private_investment_real_trn; N3_firm_cash_trn','national corporate bases, denominators, unadopted private75 behavioral assumption'),
 'A_ESTATE_GIFT':('PARTIAL_OR_PROXY','ESTATE_BRANCH_ACTIVE_GIFT_SEPARATE_NOT_ADDED','reported estate base and lagged price interface; overlapping gift alternative not simultaneous','policy_tax_delta_trn; household_policy_cash_nominal_trn','separate asset prices, transactions, distinct gift base and full legal implementation'),
 'B_PENSION':('PARTIAL_OR_PROXY','ACTIVE','75-year cohort delay and fund balances; DOMESTIC_TRANSFER source retained','pension_fund_end_trn; pension_contribution_trn; pension_benefit_delta_trn','complete cohorts, social-fund consolidation, incidence/calibration'),
 'B_MEDICAL':('PARTIAL_OR_PROXY','ACTIVE','existing N3 claims/rate interpolation/caps and insurer HH/G payer loops retained','existing_policy_government_cost_delta_trn plus medical fields in fixed sources','clinical utilization/income response, national payer consolidation and full financing'),
 'B_EOL':('PARTIAL_OR_PROXY','ACTIVE_SHARED_COMMON_COMPONENT','shared end-of-life/palliative branch retained on SQ and N3','medical service and cost fields in fixed native sources','policy-specific additional promotion budget, complete national service calibration'),
 'B_COOP':('STRUCTURAL_ONLY','STRUCTURE_ONLY','12 block candidate within original10-15; no legal entity or efficiency gain inferred','native institutions coop_blocks','membership, legal entity, contribution/benefit/funding split'),
 'B_EITC':('UNRESOLVED','BASELINE_UNKNOWN_ZERO_MODELED_REMOVAL','eitc_per_household_yen=None, no identified loss/saving','fixed EITC_removal_trn=0; EITC_baseline_trn=unknown','baseline entitlement/amount and national consolidation'),
 'B_RELIEF':('PARTIAL_OR_PROXY','ACTIVE','income-linked premium relief already retained and insurer counterpart not discarded','existing_premium_relief_trn; household_policy_cash_nominal_trn','national actual premiums, statutory relief curve and sovereign backfill allocation'),
 'B_IN_KIND':('PARTIAL_OR_PROXY','ACTIVE','existing model amount, government cost, .7 HH expense replacement and partial service VA retained','existing_in_kind_trn; existing_policy_government_cost_delta_trn','benefit types, government final purchaser, SNA mapping and calibrated effect'),
 'C_EMPLOYMENT':('PARTIAL_OR_PROXY','ACTIVE_REGULARIZE_NOT_NEW_HEADCOUNT','100000 target, wages3/4m, start2030/ramp6 are prior assumptions; added_jobs0','existing_public_payroll_delta_trn; existing_public_added_jobs','new posts/headcount, employer shares and authorized budget; do not put diagnosticG here'),
 'C_FOREIGN':('UNRESOLVED','NO_NEW_N3_PILOT_COMMON_POPULATION_RETAINED','original GDP5% definition unresolved; existing structural screen and unchanged common flow retained','population_persons and fixed foreign-screen fields','GDP ratio definition, full N4/regional enforcement, costs/demographic responses'),
 'D_SMART':('STRUCTURAL_ONLY','RANKING_ONLY','synthetic B/A/C density-productivity-cost priority, no public budget','native_smart_priority','individual assets/projects, incremental investment, nonoverlap, executor and finance'),
 'S_PHASE1':('PARTIAL_OR_PROXY','PARTIAL_TIMING_INPUTS','policy2026-2032 interval versus household2030/ramp3 and payroll2030/ramp6 inputs','fixed component initialization','original does not fix exact amounts, start or completion ramp; payroll crosses2032'),
 'S_PHASE2':('PARTIAL_OR_PROXY','PARTIAL_TIMING_AND_COHORTS','2033-2038 medical/pension transition partially represented','native medical/pension fields','institutional transition, cohorts and implementation costs'),
 'S_PHASE3':('NOT_QUANTIFIED','NO_UNIQUE_MONETARY_EFFECT','post2039 institutional aspiration not an extra fiscal saving amount','continued candidate insurance/fund ledger','fully operating institution and public-pressure reduction not separately quantified'),
 'KPI_REVIEW':('PARTIAL_OR_PROXY','HOOKS_EXIST_NOT_ACTIVE_OR_OBSERVATIONS_MISSING','fixed KPI branch, external gini observations absent, competition structural only','component events in fixed original model','endogenous gini, income threshold/duration, actual insurer competition response')}
 outrows=[]
 for x in old:
  state,active,scope,series,missing=states[x['policy_id']]
  outrows.append({**x,'native_coverage_status':state,'selected_native_active_status':active,'existing_numeric_assumptions_and_scope':scope,'native_output_series':series,'original_difference_or_unimplemented':missing,'added_GI_overlap_rule':'retain existing effect once; no automatic subtraction or readdition; smart ranking not diagnostic I amount','new_parameter_filled':False,'full_text_compliance_asserted':False})
 assert len(outrows)==22 and len(set(x['policy_id'] for x in outrows))==22
 dump(out/'N3_Native_Policy_Implementation_Coverage.csv',outrows)
 counts={s:sum(x['native_coverage_status']==s for x in outrows) for s in ['IMPLEMENTED_IN_NATIVE','PARTIAL_OR_PROXY','STRUCTURAL_ONLY','NOT_QUANTIFIED','UNRESOLVED']}
 (out/'Coverage_Verification.json').write_text(json.dumps(dict(rows=22,counts=counts,source_commit='65227a9b86f198df62430f541fbee41e3e788b80',full_policy_implementation=False,diagnostic_GI_reclassified_as_native=False),indent=2)+'\n');print(json.dumps(counts))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--outdir',type=Path,default=P);z=a.parse_args();run(z.outdir)
