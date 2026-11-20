"""Illustrative age/income/claim accounting, not a full statutory claims engine."""
import math
from CommonEndOfLife import calculate,close
from Demand import calculate as age_demand
TRN=1e12
def ramp(y,s):return max(0.,min(1.,(y-s['start_year']+1)/s['ramp_years']))
def patient_claim(age,group,profile,regime,uniform=False,cap_multiplier=1.):
 # Representative income bands: GENERAL=180man, MIDDLE=450man,HIGH=850man.
 # No outpatient-only cap, household pooling, special public aid or full income
 # cross-section. Monthly / repeated / annual caps retained for these profiles.
 elderly=age in ['AGE70_74','AGE75PLUS'];bill=profile['bill_yen'];months=profile['months']
 coins=.2 if age=='PRESCHOOL' else .3
 if elderly:
  coins=(.2 if age=='AGE70_74' else .1) if group in ['TAXFREE','GENERAL'] else .3
 if uniform:coins=.3
 old=regime=='PRE2026AUG'
 if group=='TAXFREE':
  cap=(24600 if old else 25700) if elderly else (35400 if old else 36900);multi=24600;annual=math.inf if old else 290000
 elif group=='GENERAL':
  cap=57600 if old else 61500;multi=34500 if regime=='POST2027AUG' else 44400;annual=math.inf if old else 410000
 elif group=='MIDDLE':cap=(80100+max(0.,bill-267000)*.01) if old else (85800+max(0.,bill-286000)*.01);multi=44400;annual=math.inf if old else 530000
 else:cap=(167400+max(0.,bill-558000)*.01) if old else (179100+max(0.,bill-597000)*.01);multi=93000;annual=math.inf if old else 1110000
 cap*=cap_multiplier;multi*=cap_multiplier;annual*=cap_multiplier
 paid=sum(min(bill*coins,cap if i<3 else multi) for i in range(months))
 return min(paid,annual)
def annual_patient(y,age,group,profile,**kw):
 # Calendar-year approximation to the fiscal Aug-Jul cap year. Not a person-level
 # carry-over/eligibility calculator. Statutory nominal caps are NOT price-indexed.
 regimes=[('PRE2026AUG',7/12),('POST2026AUG',5/12)] if y==2026 else [('POST2026AUG',7/12),('POST2027AUG',5/12)] if y==2027 else [('POST2027AUG',1.)]
 return sum(w*patient_claim(age,group,profile,r,**kw) for r,w in regimes)
class Medical:
 def __init__(self,c,s,deflators,population):
  self.c=c;self.s={**c['defaults'],**s};self.deflators=deflators;self.population=population;self.rows=[];self.groups=[];self.common=[];self.previous_hubs=0.;self.trajectory=None;self.elder=None;self.demography=[];self.debt=0.;self.financial_asset=0.;self.vat_records=[]
 def step(self,y):
  c=self.c;s=self.s;i=y-2026;idx=self.deflators[i]/self.deflators[0];scale=self.trajectory[i]['population']/self.trajectory[0]['population'];ph=ramp(y,s)
  total=c['observations']['medical_total_2024_trn']*idx*scale
  episodes,episode_age,aw,dr=age_demand(y,self.trajectory,self.elder,c['population_reference'],c['demand_parameters'],s['demand_mode']);self.demography.extend(dr)
  demand_ratio=sum(aw.values())/sum(c['age_cost_weights'].values())
  total=c['observations']['medical_total_2024_trn']*idx*demand_ratio
  gross=oop0=oop1=0.;unmet=0.;staticshift=0.
  # Fixed age cost shares: no invented demographic age forecast or death link.
  for age,weight in aw.items():
   for group,iw in c['income_weights'].items():
    agebudget=total*weight/sum(aw.values())*iw
    refcost=sum(p['probability']*p['bill_yen']*p['months'] for p in c['claim_profiles'])
    persons=agebudget*TRN/(refcost*idx)
    for profile in c['claim_profiles']:
     p=dict(profile,bill_yen=profile['bill_yen']*idx)
     n=persons*p['probability'];basebill=n*p['bill_yen']*p['months']/TRN
     a=n*annual_patient(y,age,group,p)/TRN
     mult=1.+(-1 if s['cap_mode']=='PATIENT_CAP_DOWN' else 1)*s['cap_change']*ph if s['copay'] else 1.
     b=n*annual_patient(y,age,group,p,uniform=s['copay'] and s['uniform_thirty'],cap_multiplier=mult)/TRN
     b=a+(b-a)*ph
     q=min(1.2,max(.7,(max(b,1e-12)/max(a,1e-12))**(-s['demand_elasticity']))) if s['copay'] else 1.
     bill=basebill*q;op=b*q;gross+=bill;oop0+=a;oop1+=op;staticshift+=b-a
     necessary=max(0.,basebill-bill)*s['necessary_care_share'];unmet+=necessary
     self.groups.append(dict(year=y,age=age,income_group=group,claim_profile=p['id'],synthetic_patient_years=n,baseline_bill_trn=basebill,reform_bill_trn=bill,baseline_patient_trn=a,reform_patient_trn=op,volume_factor=q,necessary_care_foregone_cost_proxy_trn=necessary,observed_joint_distribution=False))
  volume_delta=gross-total;oop_delta=oop1-oop0
  if abs(volume_delta)<1e-10:volume_delta=0.
  if abs(oop_delta)<1e-10:oop_delta=0.
  benefit_delta=volume_delta-oop_delta
  pp=ph*s['provider_capacity'] if s['provider'] else 0.
  maturity=max(0.,min(1.,(y-s['start_year']-s['health_lag']+1)/s['ramp_years'])) if s['provider'] else 0.
  discovery=s['prevention_discovery_trn']*pp*idx;saving=s['prevention_saving_trn']*maturity*idx
  preventclinical=discovery-saving
  # Approximate marginal cost shares; observed financing shares are NOT benefit shares.
  patient_fraction=oop0/max(total,1e-9)
  extra_patient=preventclinical*patient_fraction;extra_benefit=preventclinical-extra_patient
  cp={**c['common_parameters'],**s['common_overrides'],'enabled':s['common']}
  if s['universal_palliative']:cp.update(universal_palliative=True,palliative_additional_yen=0.)
  demand=dict(price_index=idx,population_scale=scale,registry_population=c['registry_population_reference']*scale,clinical_strata=c['clinical_strata'])
  demand['age_demand_episodes']=episodes
  demand['capacity_multiplier']=s['capacity_multiplier']
  if s['payer_mode']=='CLAIMS':
   def payer(chosen,parameters,baseline,destination,price,universal=False,transitioned=0.):
    # Monthly bills derived from each setting's episode cost, not an average
    # financing share. Same current F rules before/after and for unregistered.
    def oop(age,group,cost):
     profile=dict(months=s['episode_months'],bill_yen=cost*price/s['episode_months'])
     aa=annual_patient(y,age,group,profile)
     reform=annual_patient(y,age,group,profile,uniform=s['copay'] and s['uniform_thirty'],cap_multiplier=1.+(-1 if s['cap_mode']=='PATIENT_CAP_DOWN' else 1)*s['cap_change']*ph if s['copay'] else 1.)
     return aa+(reform-aa)*ph if s['copay'] else aa
    age_map={'U15':'PRESCHOOL','A15_64':'AGE6_69','65_69':'AGE6_69','70_74':'AGE70_74','75plus':'AGE75PLUS'}
    patient=0.;gross=0.
    for ag,n in episode_age.items():
     for group,weight in c['income_weights'].items():
      baseline_gross=0. if universal else sum(parameters['baseline_setting_shares'][k]*parameters['baseline_cost_yen'][k] for k in parameters['baseline_setting_shares'])
      if universal:
       newgross=destination;oldpaid=0.
       transitioned_share=min(1.,transitioned/max(chosen,1e-9))
       baseline_marginal=sum(parameters['baseline_setting_shares'][k]*(oop(age_map[ag],group,parameters['baseline_cost_yen'][k]+destination)-oop(age_map[ag],group,parameters['baseline_cost_yen'][k])) for k in parameters['baseline_setting_shares'])
       destination_marginal=sum(parameters['destination_shares'][k]*(oop(age_map[ag],group,parameters['destination_cost_yen'][k]+destination)-oop(age_map[ag],group,parameters['destination_cost_yen'][k])) for k in parameters['destination_shares'])
       newpaid=(1-transitioned_share)*baseline_marginal+transitioned_share*destination_marginal
      else:
       newgross=sum(parameters['destination_shares'][k]*(parameters['destination_cost_yen'][k]+parameters['palliative_additional_yen']) for k in parameters['destination_shares'])
       oldpaid=sum(parameters['baseline_setting_shares'][k]*oop(age_map[ag],group,parameters['baseline_cost_yen'][k]) for k in parameters['baseline_setting_shares'])
       newpaid=sum(parameters['destination_shares'][k]*oop(age_map[ag],group,parameters['destination_cost_yen'][k]+parameters['palliative_additional_yen']) for k in parameters['destination_shares'])
      wgt=n/episodes*weight;patient+=chosen*wgt*(newpaid-oldpaid)/TRN;gross+=chosen*wgt*(newgross-baseline_gross)*price/TRN
    benefit=gross-patient
    return dict(HOUSEHOLD=patient,GOVERNMENT=benefit*s['clinical_public_fraction'],INSURER=benefit*(1-s['clinical_public_fraction']))
   demand['payer_calculator']=payer
  common=calculate(y,demand,cp,c['common_financing']);self.common.append(common)
  clinical=volume_delta+preventclinical+common['clinical_cost_delta_trn']
  patient=oop_delta+extra_patient+common['patient_payment_delta_trn']
  public=(benefit_delta+extra_benefit)*s['clinical_public_fraction']+common['public_clinical_payment_delta_trn']
  insurer=(benefit_delta+extra_benefit)*(1-s['clinical_public_fraction'])+common['insurer_clinical_payment_delta_trn']
  close(clinical,patient+public+insurer)
  premium=insurer*s['premium_pass'];backfill=insurer*s['government_insurer_backfill_share']
  award=(s['eligible_preventive_fee_trn']*s['preventive_award']+s['eligible_equipment_fee_trn']*s['equipment_award'])*pp*idx
  prevention=s['preventive_spend_trn']*pp*idx;equipment=s['equipment_spend_trn']*pp*idx
  hubs=s['hub_target']*ph if s['provider'] else 0.;newhubs=max(0.,hubs-self.previous_hubs);self.previous_hubs=hubs
  hubcapital=newhubs*s['hub_capital_yen']*idx/TRN;operation=hubs*s['hub_operation_yen']*idx/TRN
  transition=s['transition_support_trn']*idx if s['provider'] and 2028<=y<=2030 else 0.
  pallsupport=s['palliative_provider_support_trn']*idx if s['provider'] and 2028<=y<2033 else 0.
  grants=award+prevention+equipment+hubcapital+operation+transition+pallsupport
  commonprogram=common['common_program_cost_trn']
  govcost=public+grants+commonprogram+backfill
  insbalance=-insurer+premium+backfill
  hh=-patient-premium-common['extra_household_cash_burden_trn']
  provider_receipts=clinical+grants
  # Supplier receipts include registry/decision support. Capital and grants are
  # funding transfers here; domestic production is a separate macro connection.
  common_supplier=commonprogram-common['proxy_subsidy_trn']
  setting_receipts=common['noninsured_household_delta_trn']+common['ltc_copay_delta_trn']
  proxy_receipts=common['proxy_household_net_delta_trn']+common['proxy_subsidy_trn']
  guarantee_receipts=-common['guarantee_cost_avoided_trn']
  family_income_counterpart=common['family_income_loss_trn']
  transfers=hh+provider_receipts+common_supplier-govcost+insbalance+setting_receipts+proxy_receipts+guarantee_receipts+family_income_counterpart
  close(transfers,0.)
  service=clinical+(prevention+operation+transition+pallsupport+common_supplier)
  capex=equipment+hubcapital
  healthy=s['health_worker_equivalent']*maturity
  harmed=unmet*s['harm_worker_equivalent_per_trn']
  row=dict(year=y,phase=ph,baseline_medical_bill_trn=total,baseline_patient_model_trn=oop0,baseline_insurance_and_public_model_trn=total-oop0,baseline_patient_observed_2024_trn=c['observations']['patient_financing_2024_trn'],baseline_patient_calibration_residual_trn=oop0-c['observations']['patient_financing_2024_trn']*idx*scale,reform_medical_bill_before_common_trn=gross,patient_static_transfer_trn=staticshift,demand_volume_cost_delta_trn=volume_delta,necessary_care_foregone_cost_proxy_trn=unmet,prevention_detection_cost_trn=discovery,prevention_lagged_saving_trn=saving,prevention_clinical_delta_trn=preventclinical,
   clinical_cost_delta_trn=clinical,patient_payment_delta_trn=patient,public_clinical_payment_delta_trn=public,insurer_clinical_payment_delta_trn=insurer,premium_payment_delta_trn=premium,government_insurer_transfer_delta_trn=backfill,government_transfer_cost_delta_trn=backfill,insurer_transfer_receipt_delta_trn=backfill,internal_transfer_consolidated_delta_trn=0.,household_cash_delta_trn=hh,setting_provider_receipts_trn=setting_receipts,proxy_provider_receipts_trn=proxy_receipts,guarantee_provider_receipts_trn=guarantee_receipts,family_lost_income_counterpart_trn=family_income_counterpart,government_cost_delta_trn=govcost,insurer_balance_delta_trn=insbalance,partial_public_direct_balance_delta_trn=-govcost+insbalance,provider_payment_receipts_delta_trn=provider_receipts,common_supplier_receipts_trn=common_supplier,transfer_residual_trn=transfers,
   preventive_award_trn=award,prevention_program_cost_trn=prevention,equipment_cost_trn=equipment,hub_count=hubs,new_hubs=newhubs,hub_capital_cost_trn=hubcapital,hub_operation_cost_trn=operation,hub_staff_cost_included_trn=operation*s['hub_staff_share'],transition_support_trn=transition,palliative_provider_support_trn=pallsupport,provider_grants_total_trn=grants,
   service_production_nominal_delta_trn=service*s['domestic_service_share'],investment_nominal_delta_trn=capex*s['domestic_capital_share'],health_effective_labor_added=healthy-harmed,health_effective_gain=healthy,necessary_care_labor_loss=harmed,health_lag_years=s['health_lag'],provider_operating_resource_delta_proxy_trn=clinical*.85+prevention+operation+transition+pallsupport,provider_net_cash_after_capex_proxy_trn=provider_receipts-(clinical*.85+prevention+operation+transition+pallsupport)-capex,provider_cost_ratio_assumption=.85,hub_staff_positions_cost_proxy=operation*s['hub_staff_share']*TRN/(8000000*idx),medical_unassigned_direct_cash_requirement_trn=govcost-insbalance,provider_profit_delta_trn=None,actual_QOL_gain=None,healthy_life_years_gain=None,national_debt_trn=None,national_PB_trn=None,VAT_medical_benefit_readded_trn=0.,VAT_earmarked_new_public_revenue_trn=0.,cap_interpretation=s['cap_mode'],uniform_thirty=int(s['uniform_thirty']),age_demand_forecast='FIXED_2024_COST_SHARES_POPULATION_SCALE')
  # Explicit opportunity-cost / value-added scenario, not a sign correction.
  mix=s['finance_mix'];close(sum(mix.values()),1.)
  interest=self.debt*s['medical_debt_rate'];need=govcost-insbalance+interest
  tax=need*s['finance_fraction']*mix['TAX'];finance_premium=need*s['finance_fraction']*mix['PREMIUM'];crowd=need*s['finance_fraction']*mix['OTHER_SPENDING']
  debt_flow=need*s['finance_fraction']*mix['DEBT'];debt_issue=max(0.,debt_flow)
  debt_redemption=min(self.debt,max(0.,-debt_flow));asset_add=max(0.,-debt_flow-debt_redemption)
  self.debt+=debt_issue-debt_redemption;self.financial_asset+=asset_add
  close(tax+finance_premium+crowd+need*s['finance_fraction']*mix['DEBT']+need*(1-s['finance_fraction']),need)
  domestic=(1-s['medical_import_share']);va=(1-s['medical_intermediate_share'])*s['medical_VA_scale'];replacement=(1-s['medical_displacement_share'])
  gross_service=service
  new_service=gross_service*domestic*va*replacement-crowd*s['other_spending_VA_ratio']
  row.update(medical_demand_mode=s['demand_mode'],terminal_episodes=episodes,common_patient_mode=s['payer_mode'],gross_medical_service_delta_trn=gross_service,medical_import_component_trn=gross_service*s['medical_import_share'],medical_domestic_intermediate_component_trn=gross_service*domestic*s['medical_intermediate_share'],medical_VA_scale=s['medical_VA_scale'],medical_displacement_share=s['medical_displacement_share'],medical_finance_fraction=s['finance_fraction'],medical_financing_need_before_sources_trn=need,medical_financing_tax_trn=tax,medical_financing_premium_trn=finance_premium,medical_other_spending_crowded_trn=crowd,medical_policy_debt_issue_trn=debt_issue,medical_policy_debt_stock_trn=self.debt,medical_policy_debt_redemption_trn=debt_redemption,medical_policy_net_financial_source_trn=debt_flow,medical_policy_asset_addition_trn=asset_add,medical_policy_financial_asset_stock_trn=self.financial_asset,medical_policy_interest_trn=interest,medical_unassigned_after_sources_trn=need*(1-s['finance_fraction']),clinical_episode_effective_patient_rate=common['patient_payment_delta_trn']/common['clinical_cost_delta_trn'] if abs(common['clinical_cost_delta_trn'])>1e-10 else None,medical_VAT_scope_flow_delta_trn=clinical+prevention+operation+pallsupport,
   household_cash_delta_trn=hh-tax-finance_premium,government_cost_delta_trn=govcost+interest-crowd,insurer_balance_delta_trn=insbalance+finance_premium,medical_financing_direct_tax_trn=tax,partial_public_direct_balance_delta_trn=-(govcost+interest-crowd)+insbalance+finance_premium+tax,post_financing_transfer_residual_trn=transfers-tax-finance_premium-interest+crowd+tax+finance_premium+interest-crowd,displaced_other_supplier_receipts_trn=-crowd,interest_creditor_receipts_trn=interest,
   service_production_nominal_delta_trn=new_service,investment_nominal_delta_trn=capex*domestic*s['capital_VA_ratio']*s['medical_VA_scale']*replacement,health_effective_labor_added=healthy-harmed)
  if s['legacy_GDP']:row.update(service_production_nominal_delta_trn=gross_service*s['domestic_service_share'],investment_nominal_delta_trn=capex*s['domestic_capital_share'])
  self.rows.append(row);return row
