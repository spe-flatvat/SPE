"""Illustrative age/income/claim accounting, not a full statutory claims engine."""
import math
from CommonEndOfLife import calculate,close
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
  self.c=c;self.s={**c['defaults'],**s};self.deflators=deflators;self.population=population;self.rows=[];self.groups=[];self.common=[];self.previous_hubs=0.
 def step(self,y):
  c=self.c;s=self.s;i=y-2026;idx=self.deflators[i]/self.deflators[0];scale=self.population[i]/self.population[0];ph=ramp(y,s)
  total=c['observations']['medical_total_2024_trn']*idx*scale
  aw=c['age_cost_weights'];gross=oop0=oop1=0.;unmet=0.;staticshift=0.
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
  demand=dict(price_index=idx,population_scale=scale,registry_population=c['registry_population_reference']*scale,clinical_strata=c['clinical_strata'])
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
  ancillary_receipts=common['extra_household_cash_burden_trn']+common['proxy_subsidy_trn']
  transfers=hh+provider_receipts+common_supplier-govcost+insbalance+ancillary_receipts
  close(transfers,0.)
  service=clinical+(prevention+operation+transition+pallsupport+common_supplier)
  capex=equipment+hubcapital
  healthy=s['health_worker_equivalent']*maturity
  harmed=unmet*s['harm_worker_equivalent_per_trn']
  row=dict(year=y,phase=ph,baseline_medical_bill_trn=total,baseline_patient_model_trn=oop0,baseline_insurance_and_public_model_trn=total-oop0,baseline_patient_observed_2024_trn=c['observations']['patient_financing_2024_trn'],baseline_patient_calibration_residual_trn=oop0-c['observations']['patient_financing_2024_trn']*idx*scale,reform_medical_bill_before_common_trn=gross,patient_static_transfer_trn=staticshift,demand_volume_cost_delta_trn=volume_delta,necessary_care_foregone_cost_proxy_trn=unmet,prevention_detection_cost_trn=discovery,prevention_lagged_saving_trn=saving,prevention_clinical_delta_trn=preventclinical,
   clinical_cost_delta_trn=clinical,patient_payment_delta_trn=patient,public_clinical_payment_delta_trn=public,insurer_clinical_payment_delta_trn=insurer,premium_payment_delta_trn=premium,government_insurer_transfer_delta_trn=backfill,government_transfer_cost_delta_trn=backfill,insurer_transfer_receipt_delta_trn=backfill,internal_transfer_consolidated_delta_trn=0.,household_cash_delta_trn=hh,ancillary_and_income_counterpart_trn=ancillary_receipts,government_cost_delta_trn=govcost,insurer_balance_delta_trn=insbalance,partial_public_direct_balance_delta_trn=-govcost+insbalance,provider_payment_receipts_delta_trn=provider_receipts,common_supplier_receipts_trn=common_supplier,transfer_residual_trn=transfers,
   preventive_award_trn=award,prevention_program_cost_trn=prevention,equipment_cost_trn=equipment,hub_count=hubs,new_hubs=newhubs,hub_capital_cost_trn=hubcapital,hub_operation_cost_trn=operation,hub_staff_cost_included_trn=operation*s['hub_staff_share'],transition_support_trn=transition,palliative_provider_support_trn=pallsupport,provider_grants_total_trn=grants,
   service_production_nominal_delta_trn=service*s['domestic_service_share'],investment_nominal_delta_trn=capex*s['domestic_capital_share'],health_effective_labor_added=healthy-harmed,health_effective_gain=healthy,necessary_care_labor_loss=harmed,health_lag_years=s['health_lag'],provider_operating_resource_delta_proxy_trn=clinical*.85+prevention+operation+transition+pallsupport,provider_net_cash_after_capex_proxy_trn=provider_receipts-(clinical*.85+prevention+operation+transition+pallsupport)-capex,provider_cost_ratio_assumption=.85,hub_staff_positions_cost_proxy=operation*s['hub_staff_share']*TRN/(8000000*idx),medical_unassigned_direct_cash_requirement_trn=govcost-insbalance,provider_profit_delta_trn=None,actual_QOL_gain=None,healthy_life_years_gain=None,national_debt_trn=None,national_PB_trn=None,VAT_medical_benefit_readded_trn=0.,VAT_earmarked_new_public_revenue_trn=0.,cap_interpretation=s['cap_mode'],uniform_thirty=int(s['uniform_thirty']),age_demand_forecast='FIXED_2024_COST_SHARES_POPULATION_SCALE')
  self.rows.append(row);return row
