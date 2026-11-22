"""Evidence-led inventory; policy, data, calibration and accounting axes are independent."""
import json
from pathlib import Path
BASE='handoff/chatgpt-n3-model-expansion-20261121/N3_Components.py'
GAP='handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Components.py'
PAR='handoff/chatgpt-n3-f-parity-implementation-20261122/Components.py'
ROB='handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122/N3_GDP_Robustness_Reproduce.py'
TR='handoff/chatgpt-n3-transition-financing-full-dynamics-20261122/N3_Transition_Reproduce.py'
SF='handoff/chatgpt-n3-sfa-cash-reconciliation-20261122/N3_SFA_Reproduce.py'
SIM='handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123/Resolved_Separation_Runtime.py.txt'
MED='handoff/f-common-endoflife-finalization-20261121/FMedical.py'
CI='handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122/Component_Initialization.json'
MI='handoff/chatgpt-n3-transition-financing-full-dynamics-20261122/Medical_Initialization.json'

def ref(root,path,token):
 lines=(root/path).read_text().splitlines();hits=[str(i+1) for i,t in enumerate(lines) if token in t]
 return path+':'+','.join(hits[:8])+' token='+token

def inventories(root,r,s,coverage):
 params=[]
 def add(layer,key,value,pids,unit,years,status,origin,path,token,destination,note='',empirical='NOT_ESTIMATED',calibration='UNCALIBRATED',account='PARTIAL_CONNECTION'):
  if origin=='POLICY_TEXT':empirical='TEXT_VALUE_NO_STATISTICAL_ESTIMATE_REQUIRED';calibration='VALUE_FIXED_BY_TEXT_BASES_STILL_PARTIAL'
  params.append(dict(parameter_id=layer+'.'+key,policy_ids=pids,current_value=json.dumps(value,ensure_ascii=False),unit=unit,use_years=years,
   applicable_branch='N3_NATIVE_COMPLETED_SUPPORTED;all sensitivity branches except explicit override',executable_status=status,
   assumption_origin=origin,adoption_status='TEXT_SPECIFIED_NOT_FORMAL_ADOPTION' if origin=='POLICY_TEXT' else 'NOT_ADOPTED_AS_POLICY',
   empirical_data_status=empirical,calibration_status=calibration,accounting_status=account,
   implementation=ref(root,path,token),input_source=CI if layer in ['config','component_spec'] else MI if layer=='medical_spec' else 'Completion_Inputs_And_Case_Definitions.json / pinned runtime' if layer=='runtime' else path,
   economic_fiscal_outputs=destination,interpretation_and_limit=note,numeric_empirical_provenance='UNKNOWN_PROVENANCE' if origin=='LEGACY_IMPLEMENTATION_ASSUMPTION' else origin))
 cfg=r.ci['config'];cs=r.ci['s'];ms=r.medical_input['s']
 for k,pids,unit,yrs,token,dest,note in [
 ('public_job_target','C_EMPLOYMENT;S_PHASE1','PERSONS_REGULARIZED','2030-2055','public_job_target','payroll;HH cash;G cost;C;GDP;PB;cash;debt','100k target declines with population; not net-new employees'),
 ('public_old_wage_yen','C_EMPLOYMENT','YEN_REFERENCE_PER_WORKER','2030-2055','public_old_wage_yen','payroll gap','3m reference wage; deflator applies'),
 ('public_new_wage_yen','C_EMPLOYMENT','YEN_REFERENCE_PER_WORKER','2030-2055','public_new_wage_yen','payroll gap','4m reference wage; net-new jobs remain0'),
 ('in_kind_yen','B_IN_KIND','YEN_REFERENCE_PER_ELIGIBLE_HH','2030-2055','in_kind_yen','government;HH expense replacement;service VA;GDP','30k per eligible household; distinct from stale par.in_kind_per_eligible_man2'),
 ('relief_maximum','B_RELIEF','FRACTION','2030-2055','relief_maximum','premium collection loss;HH cash;insurer','0.35 maximum; linear taper from2m to5m not statutory curve'),
 ('fund_return','B_PENSION','ANNUAL_FRACTION','2034-2055','fund_return','fund assets/payout;matching HH property-income debit','not sovereign policy interest rate'),
 ('pension_coverage','B_PENSION','FRACTION','2033-2055','pension_coverage','delayed recipients/benefits','85% coverage proxy; uniform5-year bins'),
 ('fund_diversion_share','B_PENSION','FRACTION','2033-2055','fund_diversion_share','reroute existing contribution;public system and fund','no second HH deduction'),
 ('pension_contribution_rate','B_PENSION','FRACTION','2033-2055','pension_contribution_rate','contribution proxy','0.183; exact adopted base not supplied'),
 ('payout_years','B_PENSION','YEARS','2036-2055','payout_years','fund payouts and assets','20-year payout rule is inherited candidate'),
 ('working_employment_share','B_PENSION','FRACTION','2033-2055','working_employment_share','pension contribution wagebase','0.70 proxy'),
 ('annual_worker_wage_yen','B_PENSION','YEN_REFERENCE','2033-2055','annual_worker_wage_yen','wagebase;contributions','4m scaled by actual lagged wage/SQ wage'),
 ('income_scale','A_LABOR_TAX;A_FINANCIAL_TAX;B_RELIEF','MULTIPLIER','2026-2055','income_scale','synthetic taxable bases;relief eligibility','1.04 uplift plus lagged wage replacement; not actual national income forecast'),
 ('profit_GDP_share','A_CORPORATE','FRACTION_NOMINAL_GDP','2033-2055','profit_GDP_share','corporate tax saving;dividend;private I','0.10 hypothetical profit base, not national tax statistic'),
 ('profit_margin','A_CORPORATE','FRACTION','2033-2055','profit_margin','revenue denominator when selected','0.10 revenue inference; PROFIT selected so does not change qualification in baseline'),
 ('corporate_baseline_rate','A_CORPORATE','FRACTION_COUNTERFACTUAL','2033-2055','corporate_baseline_rate','tax delta vs old rate','0.30 counterfactual old rate, not original policy rate'),
 ('corporate_investment_response','A_CORPORATE','FRACTION_TAX_SAVING','2033-2055','corporate_investment_response','first investment target;firm residual source','0.30 original model I response distinct from residual75%'),
 ('dividend_response','A_CORPORATE','FRACTION_TAX_SAVING','2033-2055','dividend_response','HH dividend net financial20 tax;firm residual','0.40 saving response is NOT payout eligibility60%'),
 ('service_VA_ratio','B_IN_KIND','FRACTION','2030-2055','service_VA_ratio','non-substitution in-kind service VA','default0.216; not whole government final consumption'),
 ]:
  add('config',k,cfg.get(k,.216 if k=='service_VA_ratio' else None),pids,unit,yrs,'ACTIVE_CONDITIONAL_FLOW' if k!='profit_margin' else 'ACCOUNT_REVENUE_ONLY_PROFIT_DENOMINATOR_SELECTED','LEGACY_IMPLEMENTATION_ASSUMPTION',BASE,token,dest,note)
 for key,value,pids,unit,yrs,status,path,token,note in [
 ('employment_start',2030,'C_EMPLOYMENT;S_PHASE1','YEAR','2030-2055','ACTIVE',BASE,'phase(y,2030,6)','start2030 not fixed in text'),
 ('employment_ramp',6,'C_EMPLOYMENT;S_PHASE1','YEARS','2030-2035','ACTIVE',BASE,'phase(y,2030,6)','3-year option previously conditional; exact annual schedule unspecified'),
 ('employment_mode','REGULARIZE','C_EMPLOYMENT','ENUM','2030-2055','ACTIVE_DEFAULT',BASE,"employment_mode','REGULARIZE'",'net-new jobs0; payroll changes wages of existing workers'),
 ('in_kind_substitution',.7,'B_IN_KIND','FRACTION','2030-2055','ACTIVE',BASE,'.7*benefit','complement0.3 service allocation; paired not independent'),
 ('in_kind_service_fraction',.3,'B_IN_KIND','FRACTION','2030-2055','ACTIVE_COMPLEMENT',BASE,'in_kind*.3','paired with HH substitution; calibrated demand effects absent'),
 ('pension_public_share',.5,'B_PENSION','FRACTION','2033-2055','ACTIVE',BASE,'public_pension_cost*.5','other0.5 belongs insurer; NOT central/local share'),
 ('investment_denominator','PROFIT','A_CORPORATE','ENUM','2033-2055','ACTIVE_DEFAULT',BASE,"investment_denominator','PROFIT'",'policy does not define denominator of20% criterion'),
 ('income_source_shares',[.95,.05,.20,.10],'A_LABOR_TAX;A_FINANCIAL_TAX','FRACTIONS','2030-2055','ACTIVE_DEFAULT',GAP,'income_source_shares','synthetic nonelder/elder labour/financial shares; pension income/local redesign open'),
 ('corporate_phase_start',2033,'A_CORPORATE;S_PHASE1','YEAR','2033-2055','ACTIVE_DEFAULT',BASE,'ph=phase(y)','phase1 original says tax transition starts2026-2032; legacy corporate defaults phase2'),
 ('corporate_phase_ramp',6,'A_CORPORATE','YEARS','2033-2038','ACTIVE_DEFAULT',BASE,'def phase','not text-fixed corporate transition schedule'),
 ('income_threshold',5000000,'B_RELIEF','YEN_NOMINAL','2030-2055','ACTIVE',BASE,'5000000','text5m; threshold fixed nominal while proxy income inflated'),
 ('pension_age',75,'B_PENSION','AGE_YEARS','2033-2055','ACTIVE',BASE,">=75",'text principle; old recipients protected by candidate cohort rules'),
 ('corporate_AND',[.6,.2,.16,.2],'A_CORPORATE','FRACTIONS','2033-2055','ACTIVE',BASE,'eligible_firm','text60% payout AND20% investment; eligible16% otherwise20%; bases/behavior remain candidates'),
 ('labor_financial_estate_rates',[.3,.2,.4],'A_LABOR_TAX;A_FINANCIAL_TAX;A_ESTATE_GIFT','FRACTIONS','2030-2055','ACTIVE',BASE,'target30','text rates retained; estate report subset and gift mutual exclusion in gap'),
 ('coop_blocks',12,'B_COOP','BLOCK_COUNT','2026-2055','STRUCTURE_ONLY',BASE,'coop_blocks','12 is candidate within10-15 text range; no geography/fiscal saving'),
 ('foreign_requested',10000,'C_FOREIGN','CANDIDATE_PERSONS','2026-2055','SCREEN_ONLY_NO_ADMISSIONS',BASE,'foreign_requested','N4 share0.8 and region quarters do not establish GDP5% definition'),
 ('eitc_per_household_yen',None,'B_EITC','YEN','2030-2055','UNKNOWN_BASELINE_MODELED_REMOVAL0',BASE,'eitc_per_household_yen','None is unknown, not demonstrated no entitlement/saving'),
 ('inheritance_base_trn',None,'A_ESTATE_GIFT','TRILLION_YEN_NOMINAL','2026-2055','INACTIVE_ALTERNATIVE_BASE',BASE,'inheritance_base_trn','estate_reported alternative is active; gift branch not added'),
 ('kpi_growth_threshold_pct',0.,'A_VAT_SWITCH;KPI_REVIEW','PERCENT','2035','DISABLED_FIXED_KPI_BRANCH',PAR,'kpi_growth_threshold_pct','0% candidate exists but original target undefined; must not treat as adopted'),
 ('gini_observation',None,'KPI_REVIEW','GINI','2034_FOR2035','MISSING_IN_ACTIVE_COMPONENT_SPEC',PAR,'gini_observations','par.gini_observations2035=0.38 is stale other-layer input, not component lag2034 observation')]:
  origin='POLICY_TEXT' if key in ['income_threshold','pension_age','corporate_AND','labor_financial_estate_rates'] else 'MISSING_INPUT' if value is None else 'LEGACY_IMPLEMENTATION_ASSUMPTION'
  add('literal_or_default',key,value,pids,unit,yrs,status,origin,path,token,'policy accounts;GDP;tax;finance where active',note)
 for key in ['firm_rate','g_share','pi_share','domestic','yield_public','lag','rate','rollover','sfa_tail','ss_growth','ss_start','kpi','cash_basis','backfill','cash_partition','q','q_central','q_local','interest_mode','tail','GI_mode','cap_scale','use_assets','extra_service_cost']:
  status='ACTIVE';note='';path=SIM;token=key;unit='FRACTION';yrs='2026-2055'
  if key in ['g_share','pi_share','domestic','yield_public','lag']:status='ECONOMICALLY_INACTIVE_GI_OFF';note='may be evaluated or echoed in metadata/requested budgets; actual G/I/capital0';unit='YEARS' if key=='lag' else unit
  if key=='firm_rate':note='0.75 applied to positive firm residual flow subject to funds and smoothing; active without public G/I'
  if key=='rate':path=ROB;note='legacy interest on debt excess and negative asset interest; not central-bank policy rate'
  if key=='rollover':path='handoff/chatgpt-national-fiscal-closure-20261121/National_Fiscal.py';note='gross issuance/refinancing changes; net stock neutral'
  if key=='sfa_tail':path=ROB;yrs='2041-2055';unit='ENUM';note='ZERO is assumed future residual, not measured no cash need'
  if key=='ss_growth':path=ROB;yrs='2041-2055';note='0 disables extra central GA social security growth stress; not no population ageing'
  if key=='ss_start':path=ROB;yrs='2041-2055';unit='YEAR';status='DISABLED_SS_GROWTH0'
  if key=='kpi':status='ACTIVE_DISABLE_SWITCH';note='FIXED suppresses automatic VAT/gini candidate; original KPI specification missing';unit='ENUM'
  if key=='cash_basis':path=TR;status='LEGACY_LABEL_OVERRIDE_IN_EFFECT';unit='ENUM';note='actual SFA/cash uses cash_part and cash_budget override; original cash_basis rule not used'
  if key=='backfill':status='DISABLED_FALSE';note='False leaves insurer deficits outside sovereign PB backfill; not national insurance closure'
  if key in ['cash_partition','q','q_central','q_local']:path=SF;note='SECTOR selects q_c/q_l before2041; allq0 assumption treats residual as remaining adjustment; q is not identified cash ratio';unit='ENUM' if key=='cash_partition' else 'FRACTION'
  if key=='q':status='ONLY_POST2040_WHEN_SECTOR;ZERO_SFA_TAIL_MAKES_INACTIVE'
  if key=='interest_mode':path=ROB;unit='ENUM';note='LEGACY_EXCESS_ONLY carries fixed official net interest scaled by debt plus rate excess/asset terms'
  if key=='tail':path=ROB;unit='ENUM';yrs='2041-2055';note='HOLD freezes2040 nominal baseline flows; not official2055 forecast'
  if key=='GI_mode':unit='ENUM';status='ACTIVE_OFF_GUARD';path='handoff/chatgpt-n3-native-policy-completion-20261123/N3_Native_Completion_Reproduce.py';note='authority_cap and cash_budget return0'
  if key=='extra_service_cost':path=ROB;status='NOT_CONSUMED_BY_SELECTED_RUNTIME';note='stored in spec but no read in selected simulate/overrides'
  if key=='use_assets':status='DISABLED_FOR_ADDITIONAL_GI';path=SF;note='does not disable ordinary cash balance financing in National_Fiscal.finance'
  add('runtime',key,s[key],'A_CORPORATE' if key=='firm_rate' else 'ALL_NATIVE_COMPARISON_FINANCE',unit,yrs,status,'COMPARISON_DIAGNOSTIC_ASSUMPTION',path,token,'firm I or PB/interest/cash/debt/gross issuance;GI only when enabled',note)
 for key in ['clinical_public_fraction','premium_pass','government_insurer_backfill_share','finance_fraction','finance_mix','medical_debt_rate','demand_elasticity','medical_import_share','medical_intermediate_share','medical_VA_scale','medical_displacement_share','start_year','ramp_years']:
  add('medical_spec',key,ms[key],'B_MEDICAL;B_EOL;S_PHASE2','YEAR' if key=='start_year' else 'YEARS' if key=='ramp_years' else 'FRACTION_OR_MIX','2033-2055 except common care',
   'ACTIVE' if key!='government_insurer_backfill_share' else 'DISABLED_ZERO_SHARE','LEGACY_IMPLEMENTATION_ASSUMPTION',MED,key,
   'patient/public/insurer;premium;medical financing;C;tax;service;GDP;PB',
   'clinical public/insurer allocation is not original patient coinsurance50% and not central/local split; semi-med counterpart synced in sensitivity' if key=='clinical_public_fraction' else 'clinical/finance parameter; no full national calibration')
 for key in ['generic_mpc','domestic_share','lambda_C','lambda_I','income_feedback','depreciation','capital_yield','elasticity','tax_cap_ratio','household_income_share','wage_gap_elasticity']:
  add('macro_active',key,r.par[key],'ALL_NATIVE_DYNAMIC_CHANNELS','FRACTION_OR_COEFFICIENT','2026-2055','ACTIVE','COMPARISON_DIAGNOSTIC_ASSUMPTION',SIM,key,'C;I;K;GDP;income;tax',
   'domestic_share here affects HH demand and is separate from inactive runtime.domestic for extraGI' if key=='domestic_share' else 'fixed comparison coefficient; not empirically estimated by this task')
 for key,value,note in [('estate_reported_2024_base_trn',23.3846,'2024 taxable-estate returns only; no all-estate deduction abolition base'),('estate_reported_2024_tax_trn',3.2446,'2024 reported tax; common-deflator projection thereafter'),('gift_reported_2024_base_trn',2.6761,'standalone alternative not added to overlapping estates'),('gift_reported_2024_tax_trn',.3178,'not used in selected estate branch')]:
  add('reported_statistics',key,value,'A_ESTATE_GIFT','TRILLION_YEN_2024_NOMINAL','2030-2055 if selected','ACTIVE_ESTATE_ALTERNATIVE' if key.startswith('estate') else 'INACTIVE_GIFT_ALTERNATIVE','PINNED_REPORTED_STATISTIC',GAP,'estate_reported' if key.startswith('estate') else 'gift_reported','wealth tax;HH cash;C;tax',note,'REPORTED_SUBSET_AVAILABLE','PROJECTION_UNCALIBRATED')
 add('literal_or_default','in_kind_income_cutoff',5000000,'B_IN_KIND','YEN_NOMINAL','2030-2055','ACTIVE','LEGACY_IMPLEMENTATION_ASSUMPTION',BASE,'income<=5000000','eligibility/in-kind/G-cost/service','text5m explicitly specifies premium relief; applying same cutoff to in-kind is inherited model scope, not independently fixed by text')
 for k,value,status,note in [('semi_med_share',cs.get('semi_med_share'), 'MATCHED_FLOW_RECLASSIFICATION','matched redirected premium and claims; no efficiency gain'),('semi_med_reserve_rate',cs.get('semi_med_reserve_rate',0.),'DISABLED_ZERO','reserve premium0 means no additional HH burden or fund accumulation'),('semi_med_return',cs.get('semi_med_return',0.),'ZERO_RATE_ZERO_ASSETS','no independent added GDP')]:
  add('component_spec',k,value,'B_MEDICAL','FRACTION','2033-2055',status,'LEGACY_IMPLEMENTATION_ASSUMPTION',GAP,k,'insurer/fund gross classification',note)
 add('macro_stale_config','invoice_cost_saving',cfg['macro_parameters']['invoice_cost_saving'],'A_INVOICE','TRILLION_YEN','none in selected live component','STALE_CONFIG_NOT_SELECTED','LEGACY_IMPLEMENTATION_ASSUMPTION',PAR,"pars=self.cfg['macro_parameters']",'none in selected invoice rule','0.05 stale nested config is not applied invoice savings; component only reads macro lambda_I here')
 add('macro_fixed_trace','invoice_cost_saving',r.par['invoice_cost_saving'],'A_INVOICE','TRILLION_YEN','fixed reference','FIXED_ZERO_NOT_NEW_MONETARY_IMPLEMENTATION','COMPARISON_DIAGNOSTIC_ASSUMPTION',SIM,'par=self.par','no new live invoice channel','actual fixed execution trace has0.0; do not use stale0.05')
 # Every original item gets independent axes, including legal/authority gap.
 details={
 'A_VAT':('SCHEDULE_FIXED_BASE_SCOPE_OPEN','TRANSACTION_BASE_AND_MEDICAL_SCOPE_PARTIAL','PASS_THROUGH_AND_ELASTICITY_CANDIDATES','VAT_TO_HH_G_INSURER_PARTIAL','fixed schedule; quantity_elasticity0.25 and rate_pass0.8; bases are proxies','national transaction calibration; preserve rates','STATISTICAL_CALIBRATION;CODE_CONNECTION'),
 'A_VAT_SWITCH':('MISSING_INCOME_DEFINITION_TARGET_WINDOW','MISSING_ADOPTED_OBSERVATION_SERIES','NO_TARGET_CALIBRATION','KPI_TO_VAT_MACRO_NOT_CONNECTED_IN_FIXED_BRANCH','disabled candidate0% threshold; proxy income available','do not convert GDP growth or synthetic gini to original KPI','POLICY_CHOICE;CODE_CONNECTION'),
 'A_INVOICE':('MISSING_SIMPLIFIED_REGIME_DETAILS','ADMIN_COST_BASELINE_MISSING','SAVING_UNESTIMATED','NO_MONETARY_FLOW_ASSIGNED','inherited invoiceHours None; active macro invoice saving0, not hypothetical0.05 in stale config','constrain small-business relief; no fabricated savings','POLICY_CHOICE;STATISTICAL_CALIBRATION'),
 'A_LABOR_TAX':('RATE30_FIXED_PENSION_LOCAL_TAX_OPEN','SURVEY_AVAILABLE_INCOME_SOURCE_MICRODATA_MISSING','SYNTHETIC_SOURCE_SHARES_AND_UPLIFT','HH_TAX_GOV_WEDGE_PARTIAL_LOCAL_SCOPE_OPEN','shares.95/.05/.20/.10; income_scale1.04; observed tax weights','reuse survey with separate sources; do not add full gross tax twice','STATISTICAL_CALIBRATION;CODE_CONNECTION;POLICY_CHOICE'),
 'A_FINANCIAL_TAX':('RATE20_FIXED_SOURCE_SCOPE_OPEN','FINANCIAL_INCOME_DISTRIBUTION_MISSING','SYNTHETIC_CATEGORY_ALLOCATION','DIVIDEND_TAX_CONNECTION_PRESENT','synthetic financial shares plus20% incremental corporate dividend tax','align survey and tax income-source definitions','STATISTICAL_CALIBRATION;CODE_CONNECTION'),
 'A_ALLOWANCE':('ABOLITION_FIXED_LEGAL_SCOPE_LOCAL_RULES_OPEN','DEDUCTION_AND_PENSION_BASE_MISSING','GROSS_CATEGORY_PROXY','LOCAL_TAX_LEFT_AS_LEGACY','gross synthetic taxable bases; not full abolition by legal deduction type','separate tax-base construction from behavior','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION'),
 'A_CORPORATE':('60_AND20_16_FIXED_DENOMINATOR_AND_TIMING_OPEN','NATIONAL_PROFIT_PAYOUT_INVESTMENT_JOINT_BASE_MISSING','PROFIT10_MARGIN10_RESPONSE30_DIV40_RESIDUAL75_UNCALIBRATED','FIRM_SOURCES_USES_CONNECTED_NATIONAL_SCOPE_PARTIAL','corporate2033/ramp6 vs phase1; private firm_rate.75 not threshold.20','first trace tax saving/dividend/originalI/residualI and firm balance','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION'),
 'A_ESTATE_GIFT':('RATE40_FIXED_LEGAL_NONOVERLAP_OPEN','2024_TAXABLE_RETURN_SUBSET_AVAILABLE_ALL_ASSETS_MISSING','DEFLATOR_ONLY_AND_ESTATE_MPC0.1','GIFT_ALTERNATIVE_MUTEX_ESTABLISHED_FULL_SCOPE_OPEN','estate23.3846/tax3.2446; gift2.6761/tax.3178 not simultaneously used','map taxable-return scope before extending all deductions','STATISTICAL_CALIBRATION;CODE_CONNECTION;POLICY_CHOICE'),
 'B_PENSION':('AGE75_FIXED_PROTECTED_COHORT_AND_FUND_RULES_OPEN','COARSE_COHORTS_WAGE_CONTRIBUTION_PROXY','RETURN2_COVER85_DIVERT25_PAYOUT20_ASSUMED','FUND_HH_RETURN_CONNECTED_PUBLIC_INSURER50_50_UNADOPTED','0.183 contribution; fund_return2%; domestic HH debit not new GDP','cohort refinement with existing elder data; sovereign/fund classification','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION'),
 'B_MEDICAL':('PATIENT50_FIXED_CAP_AND_INSTITUTION_DETAILS_OPEN','CLAIM_PROFILE_AND_NATIONAL_PAYER_DATA_PARTIAL','DEMAND0.1_PUBLIC0.5_PREMIUM0.5_FINANCE0.5_UNCALIBRATED','UNASSIGNED_FINANCE_AND_NATIONAL_CONSOLIDATION_OPEN','clinical public0.5 is benefit payer split not patient0.5; medical debt not automatically national debt','keep claims/payment identities and explicit unassigned financing','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION;INSTITUTION_AUTHORITY'),
 'B_EOL':('PALLIATIVE_CARD_DIRECTION_FIXED_ROLLOUT_DETAIL_OPEN','COMMON_EOL_INPUTS_AVAILABLE_POLICY_INCREMENT_MISSING','COMMON_PATH_AND_RESPONSE_PROXIES','COMMON_N3_SQ_ONCE_NO_SECOND_SAVING','shared common care effect; no new promotion amount','reuse common supplier/family/insurer ledgers; no N3-only recredit','STATISTICAL_CALIBRATION;CODE_CONNECTION;INSTITUTION_AUTHORITY'),
 'B_COOP':('10_TO15_FIXED_MEMBERSHIP_LEGAL_RULES_OPEN','REAL_BLOCK_MAPPING_AND_MEMBERS_MISSING','EFFICIENCY_UNESTIMATED','LEGAL_ENTITY_SNA_SECTOR_UNASSIGNED','12 synthetic blocks structural only','use partition validator with actual membership when available','POLICY_CHOICE;STATISTICAL_CALIBRATION;INSTITUTION_AUTHORITY'),
 'B_EITC':('ABOLITION_FIXED_COMPARISON_ENTITLEMENT_OPEN','EITC_BASELINE_UNKNOWN','NO_MEASURED_REMOVAL','ZERO_MODELED_IS_NOT_SAVING','eitc_per_household_yen None','identify baseline then compare same entitlement definition','STATISTICAL_CALIBRATION;POLICY_CHOICE'),
 'B_RELIEF':('5M_FIXED_TAPER_MAX_AND_BACKFILL_OPEN','OBSERVED_PREMIUM_SURVEY_PARTIAL','MAX35_TAPER2_TO5M_CANDIDATE','HH_SAVING_INSURER_LOSS_CONNECTED_SOVEREIGN_BACKFILL_FALSE','threshold5m; maximum35%; insurance deficit not fully sovereign fiscal closure','sum insurer components and explicit government backfill sensitivity','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION;INSTITUTION_AUTHORITY'),
 'B_IN_KIND':('BENEFIT_DIRECTION_FIXED_TYPES_ELIGIBILITY_AMOUNT_OPEN','ACTUAL_BENEFIT_UNIT_COST_MISSING','30K_SUBSTITUTION70_SERVICE30_VA.216_ASSUMED','G_COST_ONCE_SNA_G_FINAL_PURCHASER_OPEN','30k per eligibleHH; not full cash benefit, not all added G','distinguish actual service purchases, household replacement, accounting G classification','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION;INSTITUTION_AUTHORITY'),
 'C_EMPLOYMENT':('REGULAR_FRAME_EXPANSION_FIXED_NET_NEW_COUNT_TIMING_OPEN','EMPLOYER_WAGE_HEADCOUNT_DATA_MISSING','100K_WAGES3_4M_RAMP6_ASSUMED','PAYROLL_HH_GOV_ONCE_NET_NEW0','REGULARIZE net0; 2030-2035 vs original phase1 to2032','baseline wages/headcount must precede any ADD_JOBS labor-supply claim','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION;INSTITUTION_AUTHORITY'),
 'C_FOREIGN':('N4_5PCT_DISPERSION_FIXED_GDP_METRIC_OPEN','INDIVIDUAL_QUALIFICATION_REGION_DATA_MISSING','PILOT_PARAMS_INACTIVE_COMMON_POPULATION_FIXED','NO_NEW_ADMISSION_NO_NEW_COST_ACCOUNT','requested10000/qualified80% screen; GDP definition unknown','separate screen from common demographic path; do not map GDP5% to people','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION;INSTITUTION_AUTHORITY'),
 'D_SMART':('DENSITY_PRODUCTIVITY_DIRECTION_FIXED_SCALAR_TRADEOFF_OPEN','REAL_CITY_ASSET_COST_OWNER_MISSING','SYNTHETIC_SCORE_COST_DIVISION_UNADOPTED','NO_PROJECT_PUBLIC_I_OR_FINANCE_ASSIGNED','B/A/C legacy cost ratio; new Pareto partial order A and B incomparable','reuse partial-order function with actual regions; no diagnosticI allocation','POLICY_CHOICE;STATISTICAL_CALIBRATION;INSTITUTION_AUTHORITY'),
 'S_PHASE1':('2026_2032_FIXED_EXACT_POLICY_RAMP_OPEN','IMPLEMENTATION_CAPACITY_AND_COST_MISSING','HH2030_RAMP3_EMP2030_RAMP6_CORP2033_RAMP6','POLICY_SCHEDULE_CROSSCHECK_AVAILABLE','employment3-year separate candidate; corporate starts late','centralize independent schedules without choosing new statutory dates','POLICY_CHOICE;CODE_CONNECTION;INSTITUTION_AUTHORITY'),
 'S_PHASE2':('2033_2038_FIXED_INSTITUTIONAL_DETAIL_OPEN','FULL_COHORT_AND_INSURER_TRANSITION_MISSING','MEDICAL_PENSION_RAMP6_CANDIDATE','LEDGERS_PARTIAL_NOT_INSTITUTIONAL_CLOSURE','pension/medical transition active; public ownership not determined','preserve annual cohort/fund/claims source-use bridge','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION;INSTITUTION_AUTHORITY'),
 'S_PHASE3':('2039_ONWARD_FIXED_OPTIMIZATION_DETAIL_OPEN','ACTUAL_OPERATION_COST_DATA_MISSING','NO_UNIQUE_SAVING_COEFFICIENT','CONTINUING_FUNDS_NOT_PROOF_OF_PUBLIC_BURDEN_ELIMINATION','optimization saving unknown','continue ledgers and quantify only observed/costed changes','POLICY_CHOICE;STATISTICAL_CALIBRATION;INSTITUTION_AUTHORITY'),
 'KPI_REVIEW':('MISSING_GINI_REFERENCE_SUPPLEMENT_SIZE_DURATION_RETURN_FLOOR','GINI_LAG_OBSERVATION_AND_INSURANCE_SERIES_MISSING','NO_ENDOGENOUS_GINI_CALIBRATION','TRISTATE_RULE_ONLY_NO_ADOPTED_MACRO_RESPONSE','FIXED; stale macro gini2035.38 not lag2034 component observation','typed input/lag/year contract and unknown propagation first','POLICY_CHOICE;STATISTICAL_CALIBRATION;CODE_CONNECTION')}
 rows=[];priorities=[]
 for x in coverage:
  pid=x['policy_id'];spec,data,cal,acct,assum,action,route=details[pid]
  evidence=x['evidence']+'; '+ '; '.join(p['implementation'] for p in params if pid in p['policy_ids'].split(';'))
  rows.append(dict(policy_id=pid,original_evidence=x['evidence'],before_status=x['before_status'],after_status=x['after_status'],
   original_fixed_content=next(z['original_summary'] for z in __import__('csv').DictReader((root/'handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123/N3_Native_Policy_Implementation_Coverage.csv').open()) if z['policy_id']==pid),
   actual_assumptions=assum,policy_spec_status=spec,empirical_data_status=data,calibration_status=cal,accounting_status=acct,
   institutional_budget_authority_status='NOT_CONFIRMED_REAL_WORLD_AUTHORITY; original modeling approval is not statutory implementation authority',
   assumption_origin='MIXED_POLICY_TEXT_REPORTED_SUBSET_LEGACY_ASSUMPTIONS; see parameter ledger',adoption_status='NO_NEW_POLICY_ADOPTION; legacy numeric values not Owner-adopted policy',
   executable_status='EXISTING_PARTIAL_MODEL_OR_STRUCTURAL_ONLY; see parameter ledger',evidence=evidence,remaining_action=action))
  priorities.append(dict(policy_id=pid,resolution_routes=route,policy_judgment_required='POLICY_CHOICE' in route,statistics_or_estimation_required='STATISTICAL_CALIBRATION' in route,
   existing_data_code_can_advance='CODE_CONNECTION' in route,institution_budget_authority_required='INSTITUTION_AUTHORITY' in route,
   next_executable_improvement=action,can_fully_resolve_with_existing_code_data=False,
   no_new_owner_decision_requested=True,priority_basis='numeric sensitivity magnitude + original discrepancy + data availability + double-counting risk',
   authority_note='No new implementation authorization or formal adoption inferred'))
 return params,rows,priorities
