"""Explicit candidate bridges. No new policy values are adopted by this module."""
import sys,json,math,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
# Load pinned component definitions with only source-allocation parametrisation.
source=(ROOT/'handoff/chatgpt-n3-model-expansion-20261121/N3_Components.py').read_text()
source=source.replace('labourshare=.95*(1-elder)+.20*elder;finshare=.05*(1-elder)+.10*elder',"shares=s.get('income_source_shares',[.95,.05,.20,.10]);labourshare=shares[0]*(1-elder)+shares[2]*elder;finshare=shares[1]*(1-elder)+shares[3]*elder")
assert hashlib.sha256((ROOT/'handoff/chatgpt-n3-model-expansion-20261121/N3_Components.py').read_bytes()).hexdigest()=='3da949845436180fb2038e109afe9d01c66c5c9ca064dad548326777ea4a9519'
ns={};exec(compile(source,'pinned_N3_components_parametrised.py','exec'),ns)
Base=ns['Components'];phase=ns['phase']
GAP=json.loads((Path(__file__).parent/'Gap_Inputs.json').read_text())['gap_inputs']

class Components(Base):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.extra_foreign=0.;self.foreign_rows=[];self.gap_rows=[];self.semi_rows=[];self.semi_asset=0.
 def step(self,y,md,prior):
  s=md.s;i=y-2026;idx=md.deflators[i]/md.deflators[0]
  shares=s.get('income_source_shares',[.95,.05,.20,.10]);assert len(shares)==4 and all(0<=v<=1 for v in shares) and shares[0]+shares[1]<=1 and shares[2]+shares[3]<=1
  r=super().step(y,md,prior);ph=phase(y,s.get('household_start',2033),s.get('household_ramp',6))
  estate_base=estate_old=estate_target=estate_delta=0.
  if s.get('estate_reported'):
   estate_base=GAP['estate_reported_2024_base_trn']*idx;estate_old=GAP['estate_reported_2024_tax_trn']*idx;estate_target=.4*estate_base;estate_delta=(estate_target-estate_old)*ph
   r['policy_tax_delta_trn']+=estate_delta;r['policy_household_cash_delta_trn']-=estate_delta
  gift_delta=0.
  if s.get('gift_reported'):
   assert not s.get('estate_reported'),'No additive overlapping estate/gift bases'
   gift_delta=(GAP['gift_reported_2024_base_trn']*.4-GAP['gift_reported_2024_tax_trn'])*idx*ph
   r['policy_tax_delta_trn']+=gift_delta;r['policy_household_cash_delta_trn']-=gift_delta
  r.update(wealth_tax_delta_trn=estate_delta+gift_delta,estate_reported_base_trn=estate_base if s.get('estate_reported') else None,estate_reported_old_tax_trn=estate_old if s.get('estate_reported') else None,estate40_reported_target_trn=estate_target if s.get('estate_reported') else None,estate_tax_delta_trn=estate_delta,estate_mpc_candidate=s.get('estate_mpc',.1),gift_tax_delta_trn=gift_delta if s.get('gift_reported') else None,EITC_baseline_trn=None)
  # Explicit pilot in addition to SQ, with two dimensional definitions of a GDP cap.
  # Baseline foreign stock is charged to the cap first; never cut shared inflow.
  begin=self.extra_foreign;retained=begin*GAP['foreign_stock_retention'];accepted=0.;metric0=metric1=cap=None;N=self.cfg['core_nominal'][i]
  definition=s.get('foreign_definition');t=md.trajectory[i];baseforeign=t['foreign']
  if s.get('foreign_pilot') and y>=GAP['foreign_start']:
   # denominator is fixed SQ nominal GDP, not this pilot's resulting GDP (no look-ahead).
   cap=N*s.get('foreign_cap_ratio',.05)
   per=(GAP['foreign_wage_yen']*idx if definition=='WAGE_BILL' else GAP['foreign_productivity_real_yen']*md.deflators[i])
   metric0=baseforeign*GAP['foreign_employment_share']*per/1e12
   room=max(0.,(cap-metric0)*1e12/per-retained)
   accepted=min(GAP['foreign_pilot_request_per_year']*GAP['foreign_N4_share'],room)
   metric1=metric0+(retained+accepted)*per/1e12
  elif not s.get('foreign_pilot'):retained=0.
  self.extra_foreign=retained+accepted
  va=self.extra_foreign*GAP['foreign_productivity_real_yen']*md.deflators[i]/1e12
  # GDP enters as explicit labour-service VA in the existing solved engine. Do
  # not also add migrant wages as new HH cash: the engine income-feedback route
  # already receives the GDP change. Demographic bridge is separate, not a full
  # age-specific forecast; additional medical/social costs remain unallocated.
  r['policy_service_VA_delta_trn']+=va
  r.update(foreign_extra_employed=self.extra_foreign,foreign_extra_population_bridge=self.extra_foreign,foreign_service_VA_nominal_trn=va,foreign_effective_labor_bridge=self.extra_foreign*.8,foreign_cost_unallocated_trn=None if s.get('foreign_pilot') else 0.)
  if s.get('foreign_pilot'):
   self.foreign_rows.append(dict(year=y,definition=definition,cap_ratio=s['foreign_cap_ratio'],SQ_foreign_stock=baseforeign,extra_begin=begin,extra_retained=retained,extra_admitted_N4=accepted,extra_end=self.extra_foreign,extra_exits=begin-retained,SQ_metric_trn=metric0,cap_trn=cap,total_metric_trn=metric1,baseline_over_cap=metric0 is not None and metric0>cap,added_VA_nominal_trn=va,population_bridge=t['population']+self.extra_foreign,effective_labor_bridge=self.extra_foreign*.8,common_SQ_inflow_changed=False,regions_equal_quarters=accepted/4,costs_status='OPEN_MEDICAL_SOCIAL_HOUSING_FAMILY',mode='CANDIDATE_SERVICE_VA_AND_POPULATION_BRIDGE_NOT_FULL_DEMOGRAPHY'))
  # Re-route an explicitly selected share of existing modeled insurer claims
  # and matching existing risk premium. Matched flows cancel; no public saving
  # is fabricated. Only candidate extra reserve premium changes household cash.
  if s.get('semi_med_share'):
   w=md.rows[-1];share=s['semi_med_share']*phase(y)
   claims=share*max(0.,w['baseline_insurance_and_public_model_trn']*(1-md.s['clinical_public_fraction'])+w['insurer_clinical_payment_delta_trn'])
   begin_asset=self.semi_asset;gain=begin_asset*s.get('semi_med_return',0.)
   reserve=claims*s.get('semi_med_reserve_rate',0.)
   self.semi_asset+=gain+reserve
   r['policy_household_cash_delta_trn']-=reserve
   self.semi_rows.append(dict(year=y,share=share,old_insurer_premium_redirected_trn=claims,old_insurer_claims_redirected_trn=claims,fund_risk_premium_trn=claims,fund_reserve_premium_trn=reserve,fund_total_premium_trn=claims+reserve,fund_claim_payment_trn=claims,fund_begin_trn=begin_asset,fund_return_trn=gain,financial_sector_return_counterpart_trn=-gain,fund_end_trn=self.semi_asset,household_extra_premium_trn=reserve,old_public_system_net_delta_trn=0.,new_public_saving_trn=0.,status='CANDIDATE_EXISTING_CLAIM_RECLASSIFICATION_PLUS_OPTIONAL_HH_RESERVE;NO_EFFICIENCY_ASSUMED'))
  r.update(semi_med_fund_asset_trn=self.semi_asset)
  r['policy_partial_public_balance_trn']=r['policy_tax_delta_trn']-r['policy_government_cost_delta_trn']+r['policy_insurer_cash_delta_trn'];r['policy_budget_unclosed_trn']=-r['policy_partial_public_balance_trn']
  self.gap_rows.append(dict(year=y,estate_base_trn=estate_base,estate_old_trn=estate_old,estate_target_trn=estate_target,estate_delta_trn=estate_delta,estate_mpc=s.get('estate_mpc',.1),gift_delta_trn=gift_delta if s.get('gift_reported') else None,EITC_delta_trn=None,income_source_shares=';'.join(map(str,shares))))
  return r

def quantity_channels(spec,y,audit,vc):
 """Replace regular taxable HH price-based C target with specified gross volume.
 No medical/exempt or revenue-equivalent non-HH base enters this real basket.
 Tax is already in the VAT engine: no extra tax revenue or lost-sales wage shock.
 """
 rs=[audit.get((spec['id'],y,k)) for k in [0,1]]
 volume=price=0.
 if spec.get('quantity_link') and y>2026:
  assert all(rs),(spec['id'],y,'actual yearly VAT account unavailable')
  for r in rs:
   volume+=(r['base']+r['old_VAT'])*(r['quantity']-1);price+=r['price_HH']
  if spec.get('quantity_mode')=='INCREMENTAL_RESIDUAL':price=0.
 return dict(quantity_nominal_volume_delta_trn=volume,quantity_replaced_price_benefit_trn=price,quantity_channel_mode=spec.get('quantity_mode','REPLACE_REGULAR_HH_PRICE') if spec.get('quantity_link') else 'LEGACY_UNCHANGED',quantity_sales_income_feedback='EXISTING_GDP_FEEDBACK_ONCE',medical_quantity_VAT_status='OPEN_EXEMPT_INPUT_CREDIT_BOUNDARY')
