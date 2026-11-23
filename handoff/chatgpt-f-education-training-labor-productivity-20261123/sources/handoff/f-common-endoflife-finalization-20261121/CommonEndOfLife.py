#!/usr/bin/env python3
"""Set-independent supported-choice resource model. No treatment-stop instructions.
Inputs are disjoint clinical-demand episodes, explicit preferences, capacity and
caller-provided financing weights. No age/disability/income value weights or death
count-based savings. Outputs are scenario accounting, not clinical recommendations.
"""
import math
def close(a,b):assert math.isclose(a,b,abs_tol=1e-8,rel_tol=1e-10),(a,b)
def phase(y,p):return max(0.,min(1.,(y-p['start_year']+1)/p['ramp_years']))
def allocate(amount,weights):
 assert all(v>=0 for v in weights.values());close(sum(weights.values()),1.)
 return {k:amount*v for k,v in weights.items()}
def calculate(year,demand,parameters,financing):
 p=parameters
 delay=p.get('timeline_delay',0);enabled=p['enabled']
 ramp=lambda start,n:max(0.,min(1.,(year-start-delay+1)/n)) if enabled else 0.
 prep=ramp(2027,4);implementation=ramp(2032,4)
 ph=implementation
 supply=ramp(2027,14)*p.get('supply_capacity_factor',1.)
 registry_phase=ramp(2031,10)

 for k in ['adoption_target','confirmed_share','support_completion','clinical_appropriateness','explicit_preference_share']:assert 0<=p[k]<=1,k
 idx=demand['price_index'];scale=demand['population_scale'];adopt=registry_phase*p['adoption_target']*(1-p.get('withdrawn_share',0.))
 prev=max(0.,min(1.,(year-2031-delay)/10))*p['adoption_target'] if enabled else 0.
 # Each episode belongs to one clinical stratum. Death counts are deliberately
 # not accepted by this interface and cannot trigger an automatic cost saving.
 episodes=demand.get('age_demand_episodes',sum(x['episodes_reference']*scale for x in demand['clinical_strata']))
 recorded=episodes*adopt
 referenced=recorded*p.get('reference_target',.85)*ramp(2031,10)
 confirmed=referenced*p['confirmed_share']*p.get('latest_wish_confirmation',.95)
 proxy_rate=p.get('proxy_designation_target',.5)*ramp(2031,10)
 proxy_designated=episodes*proxy_rate
 solo=episodes*p.get('single_share',.3)
 public_proxy=solo*p.get('public_proxy_coverage',.6)*ramp(2031,10)
 fallback=episodes*(1-adopt)*(1-proxy_rate)*p.get('multidisciplinary_coverage',.7)*ramp(2031,10)

 supported=confirmed*p['support_completion']
 willing=supported*p['explicit_preference_share']*p['clinical_appropriateness']
 capacity=p['transition_capacity']*supply*scale*demand.get('capacity_multiplier',1.)
 # Universal cohort includes all willing patients; remaining demand is disjoint.
 universal_need=episodes*p.get('universal_need_share',.7) if enabled and p.get('universal_palliative',False) else 0.
 transition_need=willing*implementation
 universal_target=max(universal_need*implementation,transition_need) if universal_need else 0.
 mode=p.get('capacity_allocation','OVERLAP_EQUAL_ACCESS')
 if universal_target:
  # Same service probability for registered and unregistered patients.
  intensity=1. if mode=='OVERLAP_EQUAL_ACCESS' else p.get('transition_resource_units',2.)
  assert intensity>=1
  # Alternative: transition requires additional staff time. Reserving identical
  # universal access first avoids registration-based palliative priority.
  universal_served=min(universal_target,capacity/(1+(intensity-1)*transition_need/universal_target))
  chosen=transition_need*universal_served/universal_target
  used=universal_served+(intensity-1)*chosen
 else:
  chosen=min(transition_need,capacity);universal_served=0.;used=chosen
 overlap=chosen if universal_target else 0.
 unique=chosen+universal_served-overlap
 assert used<=capacity+1e-7 and overlap<=universal_served+1e-7
 shares=p['destination_shares'];close(sum(shares.values()),1.)
 baseline_unit=sum(p['baseline_setting_shares'][k]*p['baseline_cost_yen'][k] for k in p['baseline_setting_shares'])
 destination_unit=sum(shares[k]*p['destination_cost_yen'][k] for k in shares)
 care_delta=chosen*(destination_unit-baseline_unit)*idx/1e12
 pall=chosen*p['palliative_additional_yen']*idx/1e12
 registry=(demand['registry_population']*max(0.,adopt-prev)*p['initial_record_cost_yen']+demand['registry_population']*adopt*p['record_maintenance_yen'])*idx/1e12
 support=supported*p['decision_support_yen']*idx/1e12
 infrastructure=p['annual_infrastructure_trn']*supply*idx
 proxy_cost=(public_proxy*p.get('public_proxy_unit_yen',20000)+fallback*p.get('team_unit_yen',10000))*idx/1e12
 subsidy=public_proxy*p.get('low_income_share',.3)*p.get('proxy_subsidy_yen',10000)*idx/1e12
 infrastructure+=proxy_cost+subsidy

 program=registry+support+infrastructure
 clinical=care_delta+pall
 pay=allocate(clinical,financing)
 if demand.get('payer_calculator'):
  pay=demand['payer_calculator'](chosen,p,baseline_unit,destination_unit,idx)
 # Expanded palliative access is available independently of registration.
 universal_need=episodes*p.get('universal_need_share',.7) if enabled and p.get('universal_palliative',False) else 0.
 # universal_served and overlap were allocated jointly above
 universal_cost=universal_served*p.get('universal_palliative_unit_yen',100000)*idx/1e12
 universal_pay=allocate(universal_cost,financing)
 if demand.get('payer_calculator') and universal_served:
  universal_pay=demand['payer_calculator'](universal_served,p,0.,p.get('universal_palliative_unit_yen',100000),idx,universal=True,transitioned=overlap)
 clinical+=universal_cost
 pay={k:pay[k]+universal_pay[k] for k in pay}

 home=chosen*shares['HOME'];family_hours=home*p['extra_home_care_hours']
 # Non-insured cash and unpaid time are separated from insured treatment.
 setting=p['destination_shares'];base=p['baseline_setting_shares']
 noninsured=p.get('noninsured_yen',{'HOSPITAL':200000,'HOME':250000,'FACILITY':400000})
 ltc=p.get('ltc_copay_yen',{'HOSPITAL':10000,'HOME':80000,'FACILITY':100000})
 nonmedical=chosen*sum((setting[k]-base[k])*noninsured[k] for k in setting)*idx/1e12
 longcare=chosen*sum((setting[k]-base[k])*ltc[k] for k in setting)*idx/1e12
 hours=family_hours*p.get('family_hours_multiplier',1.)
 opportunity=hours*p.get('hour_value_yen',2000)*idx/1e12
 employment_loss=opportunity*p.get('income_loss_share',.4)
 proxy_household=(public_proxy*p.get('proxy_household_fee_yen',10000)*idx/1e12-subsidy)
 guarantee=public_proxy*p.get('guarantee_avoided_yen',30000)*idx/1e12
 extra_cash=nonmedical+longcare+proxy_household-guarantee+employment_loss
 cashburden=pay['HOUSEHOLD']+extra_cash
 financing_gap=max(0.,cashburden)
 row=dict(year=year,capacity_allocation=mode,allocation_status='UNCALIBRATED_OWNER_UNDECIDED',overlap_patients=overlap,unique_patients_served=unique,service_events=chosen+universal_served,resource_units_used=used,transition_need=transition_need,transition_unmet=max(0.,transition_need-chosen),universal_access_probability=universal_served/universal_target if universal_target else 0.,universal_palliative_need=universal_need,universal_palliative_served=universal_served,universal_palliative_unmet=max(0.,universal_need-universal_served),universal_palliative_cost_trn=universal_cost,universal_palliative_patient_trn=universal_pay['HOUSEHOLD'],universal_palliative_public_trn=universal_pay['GOVERNMENT'],universal_palliative_insurer_trn=universal_pay['INSURER'],preparation_phase=prep,law_passed=int(enabled and year>=2030+delay),implementation_phase=implementation,national_operation=int(enabled and year>=2035+delay),supply_phase=supply,
  registered_persons=demand['registry_population']*adopt,annual_new_registration_net=demand['registry_population']*max(0.,adopt-prev),record_confirmations=demand['registry_population']*adopt,record_changes=demand['registry_population']*adopt*p.get('annual_change_rate',.02),record_revocations=demand['registry_population']*adopt*p.get('annual_revocation_rate',.01),electronic_record_share=p.get('electronic_share',.8),paper_record_share=1-p.get('electronic_share',.8),procedural_legal_immunity_available=int(enabled and year>=2032+delay),
  reference_rate=p.get('reference_target',.85)*ramp(2031,10),referenced_episodes=referenced,latest_wish_confirmation_rate=p.get('latest_wish_confirmation',.95),proxy_designation_rate=proxy_rate,proxy_designated_episodes=proxy_designated,public_proxy_supported_episodes=public_proxy,multidisciplinary_fallback_episodes=fallback,
  palliative_doctor_cost_positions=capacity*p.get('doctor_hours_per_episode',8)/1600,palliative_nurse_cost_positions=capacity*p.get('nurse_hours_per_episode',40)/1600,home_24h_team_equivalents=capacity*setting['HOME']/p.get('episodes_per_24h_team',100),training_places=capacity*p.get('training_places_per_capacity',.02),
  noninsured_household_delta_trn=nonmedical,ltc_copay_delta_trn=longcare,proxy_household_net_delta_trn=proxy_household,guarantee_cost_avoided_trn=guarantee,family_care_hours=hours,family_opportunity_cost_trn=opportunity,family_income_loss_trn=employment_loss,extra_household_cash_burden_trn=extra_cash,household_direct_cash_burden_delta_trn=cashburden,household_total_economic_burden_delta_trn=pay['HOUSEHOLD']+nonmedical+longcare+proxy_household-guarantee+opportunity,savings_drawdown_delta_trn=cashburden*(1-p.get('borrowing_share',.2)),borrowing_need_delta_trn=cashburden*p.get('borrowing_share',.2),public_proxy_program_trn=proxy_cost,proxy_subsidy_trn=subsidy,
  registration_changes_benefits=0,registration_changes_copay=0,registration_changes_palliative_priority=0,registration_voluntary=1,revocation_allowed=1,latest_wish_priority=1,active_life_termination=0,
clinical_demand_episodes=episodes,record_adoption=adopt,recorded_episodes=recorded,confirmed_wishes_episodes=confirmed,supported_decision_episodes=supported,explicit_supported_appropriate_requests=willing,transition_capacity=capacity,chosen_transitions=chosen,capacity_unmet=max(0.,willing-chosen),no_record_episodes=episodes-recorded,
  home_transitions=home,facility_transitions=chosen*shares['FACILITY'],hospital_palliative_transitions=chosen*shares['HOSPITAL'],baseline_cost_per_episode_yen=baseline_unit*idx,destination_cost_per_episode_yen=destination_unit*idx,
  care_path_cost_delta_trn=care_delta,palliative_additional_cost_trn=pall,clinical_cost_delta_trn=clinical,patient_financing_mode='CALLER_CLAIM_RULES' if demand.get('payer_calculator') else 'LEGACY_AVERAGE_SHARE',registry_cost_trn=registry,decision_support_cost_trn=support,infrastructure_cost_trn=infrastructure,common_program_cost_trn=program,total_resource_cost_delta_trn=clinical+program,
  patient_payment_delta_trn=pay['HOUSEHOLD'],public_clinical_payment_delta_trn=pay['GOVERNMENT'],insurer_clinical_payment_delta_trn=pay['INSURER'],preference_concordant_supported_choices=chosen,additional_unpaid_home_care_hours=family_hours,
  wish_concordance_rate=chosen/episodes if episodes else 0.,confirmed_request_fulfillment_rate=chosen/willing if willing else None,
  actual_QOL_gain=None,QALY_gain=None,deaths_averted=None,treatment_automatically_stopped=0,unknown_wish_assumed_refusal=0)
 close(sum(pay.values()),clinical)
 assert chosen<=supported+1e-7 and chosen<=capacity+1e-7
 if p['confirmed_share']==0 or p['explicit_preference_share']==0:close(chosen,0.)
 return row
