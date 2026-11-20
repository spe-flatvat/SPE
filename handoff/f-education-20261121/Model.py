#!/usr/bin/env python3
"""SPE education replacement: cohorts, incremental fiscal flows and pinned GDP engine.
DRAFT / NON-CANONICAL. All behaviour and policy amounts are scenario candidates.
"""
import argparse,copy,csv,hashlib,importlib.util,json,math
from pathlib import Path
P=Path(__file__).resolve().parent
TRN=1e12
def eq(a,b):assert math.isclose(a,b,abs_tol=1e-7,rel_tol=2e-10),(a,b)
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader()
  for r in rows:w.writerow({k:format(v,'.12g') if isinstance(v,float) else v for k,v in r.items()})
def read(p):return list(csv.DictReader(p.open()))
def ramp(y,start,n):return max(0.,min(1.,(y-start+1)/n))
class Education:
 def __init__(self,c,s,deflators):
  self.c=c;self.s={**c['defaults'],**s};self.deflators=deflators
  self.rows=[];self.groups=[];self.scholars=[];self.skills={};self.skill_stock=0.;self.school_stock=0.;self.bonds=[];self.bond_stock=0.;self.borrowing_avoided=0.;self.trigger=False;self.judged_growth=None;self.completions={}
 def step(self,y,previous,workers):
  c=self.c;s=self.s;i=y-2026;idx=self.deflators[i]/self.deflators[0]
  ph=ramp(y,s['start_year'],s['ramp_years']);realized_completions=self.completions.pop(y,0.)
  observed=previous[-1]['real_growth_pct']/100 if previous else None
  if y==s['trigger_evaluation_year']:
   test=observed if s['trigger_mode']!='EXTERNAL' else s['external_growth']
   self.judged_growth=test
   self.trigger=s['trigger_mode']=='FORCED' or (s['trigger_mode'] in ['AUTO','EXTERNAL'] and test is not None and test<.012)
  on=self.trigger and y>=s['trigger_start_year']
  em=s['education_expansion'] if on else 1.;tm=s['training_expansion'] if on else 1.
  self.skill_stock*=1-s['skill_decay'];matured=self.skills.pop(y,0.);self.skill_stock+=matured
  facility=(s['annual_envelope_trn']*s['facility_share']*ph*idx*em if s['E'] else 0.)*s['supply_capacity']
  service=(s['annual_envelope_trn']*s['service_share']*ph*idx*em if s['E'] else 0.)*s['supply_capacity']
  # New grants are allocated within the scholarship envelope, not added twice.
  scholarship_cap=s['annual_envelope_trn']*s['scholarship_share']*ph*idx*em if s['S'] else 0.
  unit=s['grant_unit_yen']*idx
  top_count=min(c['observations']['grant_recipients_2025']*s['incumbent_topup_share'],scholarship_cap*TRN*s['topup_budget_share']/(s['topup_yen']*idx)) if scholarship_cap else 0.
  top=top_count*s['topup_yen']*idx/TRN
  continuing=[]
  for co in self.scholars:
   age=y-co['start']
   if 0<age<s['study_years']:
    co['current']*=1-s['annual_dropout'];continuing.append(co)
  continuing_count=sum(co['current'] for co in continuing)
  continuing_cost=continuing_count*unit/TRN
  assert continuing_cost<=scholarship_cap-top+1e-7
  slots=max(0.,scholarship_cap-top-continuing_cost)*TRN/unit
  new_count=min(slots,s['new_eligible_pool']*ph)
  if new_count:
   self.scholars.append(dict(start=y,current=new_count,new_enrolment=new_count*s['new_enrolment_share']))
  new_cost=new_count*unit/TRN;grant=top+continuing_cost+new_cost
  current_new_enrol=sum(co['new_enrolment']*(1-s['annual_dropout'])**(y-co['start']) for co in self.scholars if y-co['start']<s['study_years'])
  additional_completion=(new_count*s['new_enrolment_share']*s['completion_rate']+new_count*(1-s['new_enrolment_share'])*s['completion_uplift'])
  due=y+s['study_years'];self.completions[due]=self.completions.get(due,0.)+additional_completion
  skill_s=additional_completion*s['graduate_skill_gain']
  self.skills[due]=self.skills.get(due,0.)+skill_s
  school_service_net=service*(1-s['reallocation_share'])
  school_participant_years=school_service_net*TRN/(s['school_service_unit_yen']*idx)
  school_graduates=school_participant_years/s['study_years']*s['completion_rate']
  skill_e=school_graduates*s['school_skill_gain']
  self.skills[y+s['school_lag']]=self.skills.get(y+s['school_lag'],0.)+skill_e
  # OFF-JT expense per worker is conditional on spending firms; covered workers
  # are a scenario population, never a national extrapolation of the survey.
  baseline_training=s['covered_workers']*c['observations']['OFFJT_yen_per_worker_2024']*idx/TRN
  rate=min(.8,s['credit_rate']*tm)*ph if s['T'] else 0.
  eligible_existing=baseline_training*s['training_eligibility']
  effective_credit_rate=rate*s['tax_capacity']*(1-s['existing_support_overlap'])
  added_training=eligible_existing*s['training_price_response']*effective_credit_rate/max(.01,1-effective_credit_rate)
  credit_existing=eligible_existing*rate*s['tax_capacity']*(1-s['existing_support_overlap'])
  credit_added=added_training*rate*s['tax_capacity']*(1-s['existing_support_overlap'])
  credit=credit_existing+credit_added
  episodes=added_training*TRN/(s['training_unit_yen']*idx)
  training_hours=episodes*s['training_hours']
  skill_t=episodes*s['training_completion']*s['training_skill_gain']
  self.skills[y+s['training_lag']]=self.skills.get(y+s['training_lag'],0.)+skill_t
  # No additional headcount: skill gains attach to the existing future workforce.
  # Incremental study and training time have separate current opportunity costs.
  lost_training=training_hours/s['annual_work_hours']
  lost_study=current_new_enrol*s['student_employment_weight']
  productivity=min(s['productivity_cap'],self.skill_stock/max(1.,workers))
  effective_added=workers*productivity-lost_training-lost_study
  assert workers+effective_added>0
  # Scholarship use: displaced borrowing, additional tuition/consumption and
  # retained resources are disjoint uses of the same incremental cash transfer.
  tuition_new=min(grant*s['new_tuition_share'],current_new_enrol*s['education_cost_yen']*idx/TRN)
  loan=min(grant*s['loan_displacement_share'],max(0.,grant-tuition_new))
  residual=grant-tuition_new-loan
  life_consumption=residual*s['grant_mpc'];saving=residual-life_consumption
  consumed=tuition_new+life_consumption
  eq(grant,loan+consumed+saving);self.borrowing_avoided+=loan
  gross_spend=facility+service+grant
  reallocated=(facility+service)*s['reallocation_share']
  net_spend=gross_spend-reallocated
  issue=net_spend*s['bond_share'];begin=self.bond_stock
  redemption=sum(co['issue']/s['amortization_years'] for co in self.bonds if s['grace_years']<=y-co['year']<s['grace_years']+s['amortization_years'])
  interest=begin*s['bond_rate']+issue*s['bond_rate']*.5
  self.bonds.append(dict(year=y,issue=issue));self.bond_stock=begin+issue-redemption
  eq(self.bond_stock,begin+issue-redemption)
  self.school_stock=(1-s['facility_depreciation'])*self.school_stock+facility*(1-s['reallocation_share'])/self.deflators[i]
  row=dict(year=y,phase=ph,trigger_mode=s['trigger_mode'],trigger_source_growth=observed if s['trigger_mode']!='EXTERNAL' else s['external_growth'],trigger_threshold=.012,trigger_evaluation_year=s['trigger_evaluation_year'],trigger_assessed_growth=self.judged_growth,triggered=int(on),education_multiplier=em,training_multiplier=tm,
   education_service_trn=service,education_facility_trn=facility,scholarship_cap_trn=scholarship_cap,scholarship_grant_trn=grant,scholarship_unspent_trn=scholarship_cap-grant,incumbent_topup_recipients=top_count,incumbent_topup_trn=top,new_awards=new_count,continuing_awards=continuing_count,additional_grant_recipients=new_count+continuing_count,annual_grant_unit_yen=unit,additional_enrolments=new_count*s['new_enrolment_share'],additional_students_stock=current_new_enrol,scheduled_additional_completions=additional_completion,completion_effect_year=due,realized_additional_completions=realized_completions,labor_market_skill_start_year=due,
   school_participant_years=school_participant_years,teacher_positions_cost_proxy=service*TRN*.7/(8000000*idx),school_graduate_equivalents=school_graduates,baseline_training_reference_trn=baseline_training,eligible_existing_training_trn=eligible_existing,additional_training_trn=added_training,credit_on_existing_trn=credit_existing,credit_on_added_trn=credit_added,training_credit_trn=credit,effective_training_credit_rate=effective_credit_rate,training_episodes=episodes,training_unique_persons=None,training_hours=training_hours,training_time_worker_equivalent=lost_training,study_time_worker_equivalent=lost_study,
   school_skill_units_scheduled=skill_e,scholarship_skill_units_scheduled=skill_s,training_skill_units_scheduled=skill_t,matured_skill_worker_equivalents=matured,skill_stock_worker_equivalents=self.skill_stock,productivity_gain=productivity,wage_gain=productivity*s['wage_pass'],education_effective_labor_added=effective_added,school_lag=s['school_lag'],scholarship_lag=s['study_years'],training_lag=s['training_lag'],
   education_expense_new_consumption_trn=tuition_new,living_consumption_trn=life_consumption,scholarship_HH_consumption_trn=consumed,scholarship_saving_trn=saving,scholarship_cash_saving_plus_debt_reduction_trn=saving+loan,scholarship_loan_displacement_trn=loan,cumulative_borrowing_avoided_trn=self.borrowing_avoided,tuition_and_living_own_resources_relief_trn=residual,
   gross_education_spend_trn=gross_spend,reallocated_education_budget_trn=reallocated,net_additional_education_spend_trn=net_spend,education_facility_domestic_nominal_trn=facility*(1-s['reallocation_share'])*s['domestic_share'],education_service_domestic_nominal_trn=school_service_net*s['domestic_share'],facility_stock_real_proxy_trn=self.school_stock,
   bond_begin_trn=begin,bond_issue_trn=issue,bond_redemption_trn=redemption,bond_end_trn=self.bond_stock,bond_interest_trn=interest,education_primary_cost_trn=net_spend+credit,education_total_cost_trn=net_spend+credit+interest,education_unassigned_cash_finance_trn=net_spend+credit+interest+redemption-issue,firm_training_cash_delta_trn=credit-added_training,
   covered_student_cost_reference_trn=(top_count+new_count+continuing_count)*c['observations']['student_cost_2024_yen']*idx/TRN,tuition_only_cost_trn=None,full_national_bond_issue_trn=None,national_PB_trn=None,actual_enrolment_rate=None,actual_completion_rate=None,actual_HH_student_loan_balance_trn=None)
  self.rows.append(row)
  for group,weight in s['income_group_weights'].items():
   self.groups.append(dict(year=y,income_group=group,synthetic_allocation_weight=weight,target_new_eligible_pool=s['new_eligible_pool']*weight,new_awards=new_count*weight,continuing_awards=continuing_count*weight,grant_trn=grant*weight,additional_enrolments=new_count*s['new_enrolment_share']*weight,scheduled_additional_completions=additional_completion*weight,HH_consumption_trn=consumed*weight,saving_trn=saving*weight,loan_displacement_trn=loan*weight,observed_income_distribution=False))
  return row
def load(c):
 root=P.parents[1]
 for x in c['runtime_dependencies']:
  b=(root/x['path']).read_bytes();assert len(b)==x['size'] and hashlib.sha256(b).hexdigest()==x['sha256'],x['path']
 src=(root/c['integration_model']).read_text();spec=importlib.util.spec_from_file_location('fixed_integration',root/c['integration_model']);integ=importlib.util.module_from_spec(spec)
 needle="exec(compile(text,'integrated_macro.py','exec'),ns);engine=ns";assert src.count(needle)==1
 src=src.replace(needle,needle+";ns['_education_final_source']=text")
 needle="  r=original(cfg,engine,d,sq,elder,pol,case,end_year);raw.extend(r);return r";assert src.count(needle)==1
 src=src.replace(needle,"  engine=_education_hook(engine,pol)\n"+needle)
 exec(compile(src,'immutable_integration_with_education_hook.py','exec'),integ.__dict__)
 ic=json.loads((root/c['integration_inputs']).read_text());_,v,vc=integ.load(ic)
 return root,integ,v,vc
def patched_engine(engine,policy,edu,mode):
 if policy!='F' or mode=='LEGACY':return engine
 if mode=='LEGACY_LEVEL':
  source=engine['_education_final_source'];ns=dict(engine['run_path'].__globals__)
  needle="p,bprof,mig,enabled,omit=configure(c,spec);validate(p);a=c['initial']";assert source.count(needle)==1
  source=source.replace(needle,"p,bprof,mig,enabled,omit=configure(c,spec);p=copy.deepcopy(p);p['growth_hypothesis_mode']='EDUCATION_LEVEL';validate(p);a=c['initial']")
  exec(compile(source,'legacy_level_hypothesis.py','exec'),ns);return ns
 source=engine['_education_final_source'];ns=dict(engine['run_path'].__globals__);ns['_edu']=edu
 def sub(a,b):
  nonlocal source
  assert source.count(a)==1,a;source=source.replace(a,b)
 # Remove all identified overlapping legacy education/training-human channels.
 sub("p,bprof,mig,enabled,omit=configure(c,spec);validate(p);a=c['initial']", "p,bprof,mig,enabled,omit=configure(c,spec);p=copy.deepcopy(p);p.update(education_program_budget=0.,education_flow_share=0.,scholarship_spend=0.,training_credit_rate=0.,growth_hypothesis_mode='STRUCTURAL_ONLY');p['governance_allocation']['human']=0.;validate(p);a=c['initial']")
 sub("t=c['_trajectory'][i];sq=c['_common_trajectory'][i]", "t=copy.copy(c['_trajectory'][i]);sq=c['_common_trajectory'][i]\n        z=_edu.step(y,rows,t['effective_productive_workers']+c['_elder'][i]['effective_extra'])\n        t['effective_productive_workers']+=z['education_effective_labor_added']")
 sub("invest_nom=value(invflow)+value(firm['investment'])+f['investment']+value(med['hubs'])", "invest_nom=value(invflow)+value(firm['investment'])+f['investment']+value(med['hubs'])+z['education_facility_domestic_nominal_trn']")
 sub("firm_sources=value(firm['credit'])-value(firm['tax_delta'])+value(firm['release'])+admin_firm+f.get('_firm_cash',0.)", "firm_sources=value(firm['credit'])-value(firm['tax_delta'])+value(firm['release'])+admin_firm+f.get('_firm_cash',0.)+z['firm_training_cash_delta_trn']")
 sub("        cash-=_foreign_ledger[i]['employee_pension_nominal_trn']", "        cash-=_foreign_ledger[i]['employee_pension_nominal_trn']\n        cash+=z['scholarship_grant_trn']")
 needle="-p['generic_mpc']*_pension[i]['household_cash_delta_trn'])/coreD"
 sub(needle,"-p['generic_mpc']*_pension[i]['household_cash_delta_trn']+z['scholarship_HH_consumption_trn']-p['generic_mpc']*z['scholarship_grant_trn'])/coreD")
 sub("desired=coreY+p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite", "desired=coreY+p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+z['education_service_domestic_nominal_trn']/coreD")
 sub("p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite-unmet)", "p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+z['education_service_domestic_nominal_trn']/coreD-unmet)")
 sub("        taxdiag=tax+direct;", "        direct-=z['training_credit_trn'];expenditure+=z['net_additional_education_spend_trn']+z['bond_interest_trn']\n        taxdiag=tax+direct;")
 sub("realwage_proxy=a['real_wage_man']*wage_shock*edu_wage*", "realwage_proxy=a['real_wage_man']*wage_shock*edu_wage*(1+z['wage_gain'])*")
 sub("nominalwage_proxy=a['nominal_wage_man']*(coreD/(a['nominal_gdp']/a['real_gdp']))*wage_shock*edu_wage*", "nominalwage_proxy=a['nominal_wage_man']*(coreD/(a['nominal_gdp']/a['real_gdp']))*wage_shock*edu_wage*(1+z['wage_gain'])*")
 exec(compile(source,'education_integrated_macro.py','exec'),ns);return ns
def run(inp,out):
 c=json.loads(Path(inp).read_text());root,integ,v,vc=load(c);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 fixed=read(root/'handoff/f-integrated-20261121/Annual.csv');refs={(r['case'],int(r['year'])):r for r in fixed};sq={int(r['year']):r for r in fixed if r['case']=='SQ_CURRENT'}
 paths={};education=[];groups=[];fiscal=[];regression=0
 for sp in c['cases']:
  s={**c['defaults'],**sp};deflators=[float(refs['FULL_ADDITIONAL',y]['common_deflator']) for y in range(2026,2056)]
  edu=Education(c,s,deflators);integ._education_hook=lambda engine,pol:patched_engine(engine,pol,edu,s['legacy_mode'])
  vs=dict(id=s['id'],C=s['C'],C_mode=s['C_mode'])
  r,inc,sectors,b,raw,cc=integ.execute(v,vc,vs)
  if s['legacy_mode']=='LEGACY':
   for row in r:
    prior=refs['FULL_ADDITIONAL' if s['C'] else 'FULL_DIRECT',row['year']]
    for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','fiscal_balance_partial_trn','C_cash_trn','total_unassigned_funding_trn','labor_force_population_proxy','household_disposable_nominal_trn']:
     eq(row[k],float(prior[k]));regression+=1
  for i,(row,m) in enumerate(zip(r,raw)):
   fi=integ.fiscal(row,m,b,i,cc);z=edu.rows[i] if edu.rows else {}
   row.update(fi);row.update(z);row['case']=s['id'];row['legacy_education_mode']=s['legacy_mode'];row['C_interpretation']=s['C_mode'] if s['C'] else 'DIRECT_PRICE_ONLY';row['background']='FIXED_ELDER_W50_FOREIGN_MEDIUM_PENSION_MEDIUM'
   row.update(core_real_gdp_trn=m['core_real_gdp_trn'],tax_macro_trn=m['tax_macro_trn'],policy_cash_trn=m['household_policy_cash_nominal_trn'],capital_delta_real_trn=m['capital_delta_real_trn'],capital_previous_real_trn=m['capital_previous_real'],nominal_wage_proxy_man=m['nominal_wage_proxy_man'],real_wage_proxy_man=m['real_wage_proxy_man'],real_growth_pct=m['real_growth_pct'],legacy_education_budget_trn=m['education_spending_trn'],legacy_scholarship_trn=m['scholarship_spend'],legacy_education_H_stock_trn=m['human_capital_resource_stock_trn'],old_education_level_GDP_trn=m['education_level_effect'],old_wage_level_reference=.002,old_GDP_level_reference=.003,
    macro_cash_DI_proxy_trn=row['household_disposable_nominal_trn']-row['household_direct_price_benefit_trn'],headcount_education_addition=0.,education_wage_bill_actual_trn=None,national_cash_DI_actual_trn=None)
   row['employed_headcount_preserved_proxy']=b['d'][i]['domestic_employed_conditional']+b['foreign'][i]['foreign_jobs']+b['elder'][i]['F_extra_jobs']+b['pension'][i]['additional_jobs']
   row['wage_bill_proxy_trn']=row['employed_headcount_preserved_proxy']*row['nominal_wage_proxy_man']*10000/TRN
   row['F_minus_SQ_real_GDP_trn']=row['real_gdp_trn']-float(sq[row['year']]['real_gdp_trn'])
   row['GDP_minus_fixed_integration_trn']=row['real_gdp_trn']-float(refs['FULL_ADDITIONAL',row['year']]['real_gdp_trn'])
   if z:
    education.append(dict(case=s['id'],**z));fiscal.append(dict(case=s['id'],year=row['year'],**{k:row[k] for k in ['net_additional_education_spend_trn','scholarship_grant_trn','training_credit_trn','bond_issue_trn','bond_redemption_trn','bond_end_trn','bond_interest_trn','education_primary_cost_trn','education_total_cost_trn','education_unassigned_cash_finance_trn','government_partial_balance_proxy_trn','insurer_known_change_and_program_balance_trn','consolidated_partial_balance_proxy_trn','total_unassigned_funding_trn','tax_macro_trn','tax_diagnostic_trn']}))
  groups += [dict(case=s['id'],**g) for g in edu.groups];paths[s['id']]=r
 # SQ is a fixed paired reference, not a re-estimated national education budget.
 sqrows=[dict(r,case='SQ_FIXED',year=int(r['year'])) for r in fixed if r['case']=='SQ_CURRENT'];paths['SQ_FIXED']=sqrows
 comparison=[]
 for name,rows in paths.items():
  if name=='SQ_FIXED':continue
  for i,r in enumerate(rows):
   off=paths['REPLACED_ZERO'][i];old=paths['LEGACY'][i]
   rr=dict(case=name,year=r['year'],legacy_mode=r['legacy_education_mode'],C_interpretation=r['C_interpretation'])
   for k in ['real_gdp_trn','nominal_gdp_trn','macro_cash_DI_proxy_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','labor_force_population_proxy','nominal_wage_proxy_man','tax_diagnostic_trn','consolidated_partial_balance_proxy_trn']:
    rr[k]=r[k];rr[k+'_minus_replaced_zero']=r[k]-off[k];rr[k+'_minus_legacy']=r[k]-old[k]
   rr['F_minus_SQ_real_GDP_trn']=r['F_minus_SQ_real_GDP_trn'];comparison.append(rr)
 interactions=[]
 for i,y in enumerate(range(2026,2056)):
  z=paths['REPLACED_ZERO'][i];full=paths['COMBINED'][i]
  for k in ['real_gdp_trn','consolidated_partial_balance_proxy_trn','macro_cash_DI_proxy_trn','labor_force_population_proxy']:
   singles=[paths[n][i][k]-z[k] for n in ['EDUCATION_ONLY','SCHOLARSHIP_ONLY','TRAINING_ONLY']]
   combined=full[k]-z[k]
   interactions.append(dict(year=y,metric=k,education_only=singles[0],scholarship_only=singles[1],training_only=singles[2],sum_of_single_effects=sum(singles),combined_effect=combined,interaction=combined-sum(singles)))
 # Fiscal feedback is measured against the same replacement background, not
 # called a measured national education tax multiplier.
 for r in fiscal:
  i=r['year']-2026;off=paths['REPLACED_ZERO'][i]
  r['macro_tax_feedback_vs_zero_trn']=r['tax_macro_trn']-off['tax_macro_trn'];r['partial_public_balance_vs_zero_trn']=r['consolidated_partial_balance_proxy_trn']-off['consolidated_partial_balance_proxy_trn'];r['tax_feedback_gross_proxy_vs_zero_trn']=r['tax_diagnostic_trn']-off['tax_diagnostic_trn']+r['training_credit_trn'];r['other_policy_and_tax_interaction_residual_trn']=r['partial_public_balance_vs_zero_trn']-r['macro_tax_feedback_vs_zero_trn']+r['education_total_cost_trn'];r['nationwide_PB_trn']=None;r['nationwide_debt_trn']=None
 allrows=[r for rs in paths.values() for r in rs]
 dump(out/'Annual.csv',allrows);dump(out/'Education.csv',education);dump(out/'Scholarship_Groups.csv',groups);dump(out/'Fiscal_Bonds.csv',fiscal);dump(out/'Comparison.csv',comparison);dump(out/'Interactions.csv',interactions);dump(out/'Summary.csv',[r for r in comparison if r['year'] in [2026,2030,2035,2045,2055]])
 dump(out/'Education_Investment.csv',[{k:r[k] for k in ['case','year','phase','education_service_trn','education_facility_trn','school_participant_years','teacher_positions_cost_proxy','reallocated_education_budget_trn','education_facility_domestic_nominal_trn','education_service_domestic_nominal_trn','facility_stock_real_proxy_trn','school_lag']} for r in education])
 dump(out/'Scholarship.csv',[{k:r[k] for k in ['case','year','scholarship_cap_trn','scholarship_grant_trn','scholarship_unspent_trn','incumbent_topup_recipients','incumbent_topup_trn','new_awards','continuing_awards','additional_grant_recipients','annual_grant_unit_yen','additional_enrolments','additional_students_stock','scheduled_additional_completions','realized_additional_completions','completion_effect_year','labor_market_skill_start_year','covered_student_cost_reference_trn','tuition_only_cost_trn','education_expense_new_consumption_trn','living_consumption_trn','scholarship_saving_trn','scholarship_cash_saving_plus_debt_reduction_trn','scholarship_loan_displacement_trn','cumulative_borrowing_avoided_trn']} for r in education])
 dump(out/'Corporate_Training.csv',[{k:r[k] for k in ['case','year','baseline_training_reference_trn','eligible_existing_training_trn','additional_training_trn','credit_on_existing_trn','credit_on_added_trn','training_credit_trn','firm_training_cash_delta_trn','training_episodes','training_unique_persons','training_hours','training_time_worker_equivalent','training_skill_units_scheduled','training_lag']} for r in education])
 dump(out/'Human_Capital.csv',[{k:r.get(k) for k in ['case','year','legacy_education_mode','skill_stock_worker_equivalents','matured_skill_worker_equivalents','school_skill_units_scheduled','scholarship_skill_units_scheduled','training_skill_units_scheduled','productivity_gain','wage_gain','education_effective_labor_added','labor_force_population_proxy','employed_headcount_preserved_proxy','nominal_wage_proxy_man','real_wage_proxy_man','wage_bill_proxy_trn','real_gdp_trn','nominal_gdp_trn','legacy_education_H_stock_trn','old_education_level_GDP_trn']} for rows in paths.values() for r in rows if r['case']!='SQ_FIXED'])
 (out/'Validation.json').write_text(json.dumps(dict(status='PASS_LOCAL',cases=len(paths),annual_rows=len(allrows),fixed_integration_regression_cells=regression,checks=['pinned bytes','legacy exact path','grant uses sum','bond stock flow','no graduate headcount addition','new skills scheduled with separate lags','old education removed on replacement','same inherited GDP identities'],limitations='All behavioural returns and policy amounts are explicit uncalibrated candidates; national budget and PB remain unavailable.'),indent=2)+'\n')
 print(json.dumps(dict(cases=len(paths),rows=len(allrows),regression=regression)))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('inputs');ap.add_argument('--outdir',required=True);a=ap.parse_args();run(a.inputs,a.outdir)
