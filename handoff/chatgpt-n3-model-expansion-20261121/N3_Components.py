"""N3 candidate policy components; all unspecified amounts remain scenario inputs.
Flows are changes to fixed SQ, in trillion yen/year. No national budget closure.
"""
import math

def phase(y,start=2033,ramp=6):return max(0.,min(1.,(y-start+1)/ramp))
def eligible_firm(payout,investment,profit,revenue,denominator):
 den=profit if denominator=='PROFIT' else revenue if denominator=='REVENUE' else None
 return None if den is None or den<=0 else payout>=.60 and investment/den>=.20

def relief(income,threshold,maximum):
 return max(0.,min(maximum,maximum*(threshold-income)/(threshold-2000000))) if income<=threshold else 0.

def institutions(blocks,regions,invoice_hours=None,hour_cost=None,growth=None,threshold=None):
 assert 10<=blocks<=15
 ranked=sorted(regions,key=lambda x:x['density']*x['productivity']/max(x['cost'],1),reverse=True)
 return dict(coop_blocks=blocks,priority=[r['id'] for r in ranked],invoice_saving_yen=None if invoice_hours is None or hour_cost is None else invoice_hours*hour_cost,freeze=None if growth is None or threshold is None else growth<threshold)

def foreign_screen(request,ratio,ratio_definition,qualification,region_weights):
 assert request>=0 and 0<=qualification<=1 and abs(sum(region_weights)-1)<1e-9 and all(0<=w<=1 for w in region_weights)
 if ratio is None or ratio_definition is None:return dict(status='OPEN_GDP_RATIO_DEFINITION',qualified_candidate=request*qualification,accepted=None)
 return dict(status='EXTERNAL_RATIO_SCENARIO_ONLY',qualified_candidate=request*qualification,accepted=request*qualification if 0<=ratio<=.05 else 0)

class Components:
 def __init__(self,config,household,pension):
  self.cfg=config;self.hh=household;self.pen=pension;self.cohorts=[];self.pension=[];self.households=[];self.firms=[];self.rows=[];self.structures=[];self.frozen=False
 def step(self,y,md,macro_prior):
  s=md.s;i=y-2026;ext=self.cfg;idx=md.deflators[i]/md.deflators[0];t=md.trajectory[i];pop=t['population'];ph=phase(y)
  cash=tax=gov=ins=service=invest=jobs=dividend=retained=0.;hh_tax=financial_tax=corp_tax=inheritance=None;reduction=in_kind=eitc=0.
  hh_tax=financial_tax=corp_tax=0.
  hhph=phase(y,s.get("household_start",2033),s.get("household_ramp",6))
  # Source distribution: existing 2025 survey/2024 incomes. Category allocation
  # below is explicitly synthetic; no national microdata cross-section is claimed.
  h=self.hh;count=pop/h['stats']['mean_household_size'];uplift=ext.get('income_scale',1.04)
  for n,x in enumerate(h['income_cells']):
   income=x['income_yen']*idx*uplift;nh=count*x['share'];q=x['quintile'];cov=(h['stats']['paid_per_2000'][q]-h['stats']['amount_unknown_per_2000'][q])/2000
   premium=h['stats']['observed_premium_total_yen'][q]*cov*idx*uplift
   elder=x['elder_share'];labourshare=.95*(1-elder)+.20*elder;finshare=.05*(1-elder)+.10*elder
   # Pension income treatment and local-tax redesign remain OPEN, not taxed at30.
   oldtax=h['stats']['income_tax_mean_paid_yen'][q]*h['stats']['income_tax_paid_per2000'][q]/2000*idx
   target30=income*labourshare*.30;target20=income*finshare*.20
   local=h['stats']['local_tax_mean_paid_yen'][q]*h['stats']['local_tax_paid_per2000'][q]/2000*idx
   baseline_DI=income-oldtax-local-premium
   dt=(target30+target20-oldtax*(labourshare+finshare))*hhph if s.get('flat_hh') else 0.
   hh_tax+=nh*(target30-oldtax*labourshare)*hhph/1e12 if s.get('flat_hh') else 0
   financial_tax+=nh*(target20-oldtax*finshare)*hhph/1e12 if s.get('flat_hh') else 0
   rr=relief(income,5000000,ext.get('relief_maximum',.35))*hhph if s.get('relief') else 0
   saved=nh*premium*rr/1e12;benefit=nh*ext.get('in_kind_yen',30000)*idx*hhph/1e12 if s.get('relief') and income<=5000000 else 0
   oldeitc=ext.get('eitc_per_household_yen');lost=0 if oldeitc is None else nh*oldeitc*idx*hhph/1e12 if s.get('relief') and income<=5000000 else 0
   reduction+=saved;in_kind+=benefit;eitc+=lost
   cash+=-nh*dt/1e12+saved+.7*benefit-lost
   if s.get('flat_hh') or s.get('relief'):
    self.households.append(dict(year=y,cell=n,income_yen=income,households=nh,baseline_DI_proxy_yen=baseline_DI,new_cash_DI_proxy_yen=baseline_DI-dt+premium*rr-(lost*1e12/nh if nh else 0),service_expense_avoidance_yen=.7*benefit*1e12/nh if nh else 0,DI_scope='ISOLATED_TAX_RELIEF_NOT_ALL_N3_CHANNELS',eligible_5m=income<=5000000,labour_business_30_gross_base_trn=nh*income*labourshare/1e12,financial20_gross_base_trn=nh*income*finshare/1e12,baseline_allocated_national_tax_trn=nh*oldtax*(labourshare+finshare)/1e12,flat_tax_delta_trn=nh*dt/1e12,relief_rate=rr,premium_saved_trn=saved,in_kind_trn=benefit,EITC_removal_trn=lost,cash_delta_trn=-nh*dt/1e12+saved+.7*benefit-lost,source_class='SURVEY_WEIGHTED_SYNTHETIC_CATEGORY_ALLOCATION'))
  tax+=hh_tax+financial_tax
  gov+=in_kind-eitc;ins-=reduction
  service+=in_kind*.3*ext.get('service_VA_ratio',.216)
  # Firm profit base is a separate explicit hypothetical GDP share, not an
  # observed national corporation-tax base. Corporate/finance tax are disjoint.
  if s.get('corporate'):
   # Fixed SQ reference nominal path; no endogenous-profit calibration is claimed.
   N=ext['core_nominal'][i];profitbase=N*ext.get('profit_GDP_share',.10);margin=ext.get('profit_margin',.10)
   for n,f in enumerate(ext['firm_cells']):
    profit=profitbase*f['weight'];revenue=profit/margin;investment=profit*f['investment_profit_ratio'];qualified=eligible_firm(f['payout'],investment,profit,revenue,s.get('investment_denominator','PROFIT'))
    target=.16 if qualified and s.get('corporate_incentive') else .20
    # statutory targets apply as written; phase and baseline30 are candidates.
    base_rate=ext.get('corporate_baseline_rate',.30);delta=profit*(target-base_rate)*ph;saving=-delta
    addedI=saving*ext.get('corporate_investment_response',.3);addedD=saving*ext.get('dividend_response',.4);kept=saving-addedI-addedD
    assert abs(saving-addedI-addedD-kept)<1e-8
    corp_tax+=delta;invest+=addedI;dividend+=addedD;retained+=kept;cash+=addedD*.8;tax+=addedD*.2
    self.firms.append(dict(year=y,cell=n,profit_base_trn=profit,revenue_base_trn=revenue,payout_ratio=f['payout'],investment_base_trn=investment,investment_denominator=s.get('investment_denominator','PROFIT'),AND_qualified=qualified,effective_rate_candidate=base_rate+ph*(target-base_rate),corporate_tax_delta_trn=delta,investment_delta_trn=addedI,dividend_delta_trn=addedD,financial_tax_on_dividend_delta_trn=addedD*.20,retained_delta_trn=kept,status='HYPOTHETICAL_PROFIT_BASE_NOT_NATIONAL_TAX_FORECAST'))
   tax+=corp_tax
  # Estate base is absent. Supplying a basis explicitly enables a hypothetical
  # transaction ledger; default remains null, not invented nationwide receipts.
  estate=ext.get('inheritance_base_trn');inheritance=None if estate is None else estate*.4*ph
  if s.get('flat_hh') and inheritance is not None:tax+=inheritance;cash-=inheritance
  pension_delta=contrib=fundpay=returns=fund_begin=fund_end=public_pension_cost=0.
  if s.get('pension75'):
   fund_begin=sum(z['assets'] for z in self.cohorts);rate=ext.get('fund_return',.02)
   for z in self.cohorts:
    gain=z['assets']*rate;z['assets']+=gain;returns+=gain
    if z['age']+y-z['entry_year']>=75:
     payout=min(z['assets'],z['assets']/max(1,ext.get('payout_years',20)-(y-z['entry_year']-(75-z['age']))));z['assets']-=payout;fundpay+=payout
   eligible_year=s.get('protected_from_year',2033)
   delayed=0.
   for group,offset,age in [('65_69',0,67),('70_74',5,72)]:
    # Uniform within5-year age bins; only cohorts reaching65 after eligibility
    # year are delayed. Pre-existing recipients remain protected.
    popage=sum(md.elder[i][group+'_'+sex+'_population'] for sex in ['male','female']);fraction=min(1,max(0,(y-eligible_year+1-offset)/5))
    delayed+=popage*fraction*ext.get('pension_coverage',.85)
   unit=sum(z['weight']*z['pension_month'] for z in self.pen['public']['strata'])*12*idx
   pension_delta=-delayed*unit*ph/1e12
   # Re-route an explicit fraction of an existing proxy contribution base, with
   # no second household deduction. Public system loses the same contributions.
   wagebase=t['working_age']*ext.get('working_employment_share',.70)*ext.get('annual_worker_wage_yen',4000000)*idx/1e12
   contrib=wagebase*ext.get('pension_contribution_rate',.183)*ext.get('fund_diversion_share',.25)*ph
   # Worker age cohorts are candidates; old-age saving matures at75.
   for age,weight in [(32,.65),(52,.25),(67,.08),(72,.02)]:self.cohorts.append(dict(entry_year=y,age=age,assets=contrib*weight))
   fund_end=sum(z['assets'] for z in self.cohorts)
   assert math.isclose(fund_end,fund_begin+returns+contrib-fundpay,abs_tol=1e-8)
   public_pension_cost=pension_delta+contrib
   gov+=public_pension_cost*.5;ins-=public_pension_cost*.5;cash+=pension_delta+fundpay
   self.pension.append(dict(year=y,protected_cohort_start=eligible_year,delayed_recipients_candidate=delayed*ph,public_benefit_delta_trn=pension_delta,diverted_existing_contribution_trn=contrib,public_cash_cost_delta_trn=public_pension_cost,fund_begin_trn=fund_begin,fund_contribution_trn=contrib,fund_return_trn=returns,fund_payout_trn=fundpay,fund_end_trn=fund_end,household_pension_cash_delta_trn=pension_delta+fundpay,government_cash_cost_delta_trn=public_pension_cost*.5,public_insurer_cash_delta_trn=-public_pension_cost*.5,return_counterparty='EXTERNAL_FINANCIAL_INCOME_OPEN',status='PARTIAL_COHORT_CANDIDATE_NO_EXISTING_RIGHTS_REVOKED'))
  # Payroll regularization, or a separate candidate of net-new jobs. Both are
  # budgeted. Existing workers are not counted as additional employment.
  payroll=0.
  if s.get('employment'):
   n=ext.get('public_job_target',100000)*phase(y,2030,6)*pop/md.trajectory[0]['population']
   if s.get('employment_mode','REGULARIZE')=='ADD_JOBS':
    jobs=min(n,t['working_age']*(1-ext.get('working_employment_share',.70)));payroll=jobs*ext.get('public_new_wage_yen',4000000)*idx/1e12
   else:payroll=n*(ext.get('public_new_wage_yen',4000000)-ext.get('public_old_wage_yen',3000000))*idx/1e12
   cash+=payroll;gov+=payroll
  previous_growth=None if not macro_prior else macro_prior[-1].get('real_growth_pct')
  inst=institutions(ext.get('coop_blocks',12),ext['regions'],growth=previous_growth,threshold=s.get('kpi_growth_threshold_pct'))
  if s.get('kpi') and y>=2035:self.frozen=self.frozen or bool(inst['freeze'])
  fs=foreign_screen(ext.get('foreign_requested',10000),s.get('foreign_ratio_value'),s.get('foreign_ratio_definition'),ext.get('N4_qualified_share',.8),ext['regional_weights'])
  # Ambiguous ratio definition prevents macro admission. Interface evaluates
  # explicit external-ratio examples, without turning5% GDP into a headcount.
  self.structures.append(dict(year=y,coop_blocks=inst['coop_blocks'],smart_priority=';'.join(inst['priority']),invoice_cost_saving_yen=inst['invoice_saving_yen'],kpi_external_candidate_threshold=s.get('kpi_growth_threshold_pct'),kpi_previous_growth_pct=previous_growth,kpi_freeze_candidate=self.frozen if s.get('kpi') else None,foreign_ratio_definition=s.get('foreign_ratio_definition'),foreign_ratio_value=s.get('foreign_ratio_value'),foreign_qualified_candidate=fs['qualified_candidate'],foreign_accepted_conditional=fs['accepted'],foreign_macro_connected=False,foreign_status=fs['status']))
  row=dict(year=y,policy_household_cash_delta_trn=cash,policy_tax_delta_trn=tax,policy_government_cost_delta_trn=gov,policy_insurer_cash_delta_trn=ins,policy_service_VA_delta_trn=service,policy_investment_delta_trn=invest,n3_effective_labor_delta=jobs*.8,public_added_jobs=jobs,public_payroll_delta_trn=payroll,labour_business_flat30_tax_delta_trn=hh_tax,household_financial20_tax_delta_trn=financial_tax,corporate_tax_delta_trn=corp_tax,inheritance40_tax_trn=inheritance,inheritance_status='OPEN_BASELINE_AND_TAXBASE' if estate is None else 'HYPOTHETICAL_GROSS_NOT_REVENUE_DELTA',dividend_delta_trn=dividend,retained_delta_trn=retained,premium_relief_trn=reduction,in_kind_trn=in_kind,EITC_removal_trn=eitc,EITC_status='OPEN_BASELINE' if ext.get('eitc_per_household_yen') is None else 'HYPOTHETICAL_BASELINE',pension_benefit_delta_trn=pension_delta,pension_fund_contribution_trn=contrib,pension_fund_payout_trn=fundpay,pension_fund_stock_trn=fund_end,policy_partial_public_balance_trn=tax-gov+ins,policy_budget_unclosed_trn=gov-ins-tax,national_PB_trn=None,national_debt_trn=None,national_bond_issue_trn=None,policy_financing_status='OPEN_NATIONAL_CLOSURE')
  self.rows.append(row);return row
