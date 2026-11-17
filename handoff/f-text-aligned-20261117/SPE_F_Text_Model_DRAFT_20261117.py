#!/usr/bin/env python3
"""F text rules and partial uncalibrated annual accounts. Standard library only.
National full-F estimates stay blank when necessary inputs are missing.
Original24 paths are read-only CSV references, never recalculated here.
"""
import argparse,base64,copy,csv,hashlib,io,json,math,re,zlib
from pathlib import Path
PREFIX='SPE_F_Text_'
CSV=PREFIX+'Annual_Comparison_DRAFT_20261117.csv'
REPORT=PREFIX+'Run_Report_DRAFT_20261117.md'
MAP=PREFIX+'Policy_Map_DRAFT_20261117.md'
def req(x,msg):
    if not x:raise ValueError(msg)
def close(a,b):return math.isclose(a,b,abs_tol=1e-8,rel_tol=1e-10)
def sha(b):return hashlib.sha256(b).hexdigest()
def value(x):return 0. if x is None else x  # partial subtotal only; full totals remain None

def phase(y,start,ramp=3):return 0. if y<start else min(1.,(y-start+1)/ramp)
def schedule(d,y,default=0.):
    keys=sorted(int(k) for k in (d or {}) if int(k)<=y)
    return d[str(keys[-1])] if keys else default

def policy_rules(p,y):
    """Institutional conditions; no rule forces GDP/population/Gini targets."""
    tau=.1 if y<p['year8'] else .08 if y<p['year5'] else .05
    food=.08 if y<p['food_zero_start'] else 0. if y<p['food_eight_start'] else .08 if y<p['year5'] else .05
    return dict(standard_tax_rate=tau,food_tax_rate=food,
        corporate_rate=.23 if y>=p['corp_start'] else None,
        defense_surcharge=schedule(p['defense_surcharge_schedule'],y) if p['defense_surcharge_schedule'] is not None else None,
        invoice_monthly_submissions=12 if y>=p['admin_start'] else None,
        simplified_bookkeeping_allowed=int(p['admin_start']<=y<=2040),
        exemption_threshold_man=240 if y>=p['admin_start'] else None,
        digital_collection_target=int(y>=2040),guideline_active=int(y>=2028),
        governance_review=int(y==2030),governance_reconsider=int(y==2033),
        foreign_package_active=int(y>=2030),japanese_minimum='N4' if y>=2030 else '',
        hub_count=p['hub_target']*min(1.,max(0.,(y-2027)/8)),
        transition_medical_active=int(2028<=y<=2030),
        palliative_support_active=int(p['palliative_start']<=y<p['palliative_start']+5),
        price_total_display=int(y>=p['base_start']),financial_transactions_taxed=0)

def disclosure(p,y):
    if y<2028:return None
    ratio=p['payout_ratio']
    if ratio is None:return None
    return int(ratio>.4) if p['payout_interpretation']=='BODY_OVER40_DISCLOSURE' else int(ratio<.4)

def validate(p):
    req(p['year8']<p['year5'],'Rate order')
    req(p['food_zero_start']<p['food_eight_start']<p['year5'],'Food rate order')
    req(2027<=p['investment_start']<=2055,'Investment start')
    req(p['medical_mode'] in ['UNALLOCATED_COMPAT','PREMIUM','PUBLIC','INTERNAL'],'Medical mode')
    req(800<=p['hub_target']<=1200,'Hub target source range')
    req(.30<=p['insurance_reduction']<=.40,'Source insurance reduction range')
    req(.05<=p['gini_relief_increment']<=.10,'Gini relief source range')
    req(1.5<=p['elasticity']<=2.,'Source elasticity range')
    req(close(p['patient_share']+p['insurer_share']+p['public_share'],1),'Medical allocation')
    for a in ['preventive_award','equipment_award']:
        lim=.04 if a=='preventive_award' else .025
        req(p[a] is None or 0<=p[a]<=lim,'Medical incentive cap')
    req(p['gini_increment_mode'] in ['PERCENTAGE_POINTS','RELATIVE'],'Gini interpretation')
    if p['cohorts']:
        for r in p['cohorts']:req(r['persons']>=0 and r['income_man']>=0 and 0<=r['mpc']<=1,'Cohort input')
    for k in p['extra_bases']:
        b=p['extra_bases'][k];q=p['extra_input_ratios'][k]
        req(b is None or b>=0,'Negative base');req(q is None or 0<=q<=1,'Input ratio')
    # No invented benefit-before-tax or5%-before-base constraint.

def social(p,y,relief,gini_increment,refund,disabled):
    """Eligibility by income<=500/300; govt backfills contribution loss once."""
    if disabled:return {'premium_relief':0.,'in_kind':0.,'vat_return':0.,'refund':0.,'household':0.,'government':0.,'insurer_contribution_loss':0.,'insurer_backfill':0.,'weighted_demand':0.}
    weighted=None
    if y<p['insurance_start']:premium=kind=0.;weighted=0.
    elif p['cohorts'] is None:premium=kind=None
    else:
        rate=p['insurance_reduction']+gini_increment if p['gini_increment_mode']=='PERCENTAGE_POINTS' else p['insurance_reduction']*(1+gini_increment)
        premium=sum(r['income_man']*r['persons']*r['contribution_rate']*min(rate,1.)/1e8 for r in p['cohorts'] if r['income_man']<=500)
        weighted=sum(r['income_man']*r['persons']*r['contribution_rate']*min(rate,1.)*r['mpc']/1e8 for r in p['cohorts'] if r['income_man']<=500)
        eligible=sum(r['persons'] for r in p['cohorts'] if r['income_man']<=300)
        kind=None if p['in_kind_per_eligible_man'] is None else eligible*p['in_kind_per_eligible_man']/1e8
    vat_return=None if p['vat_relief_social_return_fraction'] is None else relief*p['vat_relief_social_return_fraction']
    # This is explicitly ADDITIONAL_BUDGET_TRANSFER sensitivity, not reusing price relief as revenue.
    if weighted is not None and p['cohorts'] is not None and p['in_kind_per_eligible_man'] is not None:
        weighted+=sum(r['persons']*p['in_kind_per_eligible_man']*r['mpc']/1e8 for r in p['cohorts'] if r['income_man']<=300) if y>=p['insurance_start'] else 0.
    cash=value(premium)+value(kind)+value(vat_return)+value(refund)
    return dict(premium_relief=premium,in_kind=kind,vat_return=vat_return,refund=refund,
        household=cash,government=cash-value(vat_return) if p['vat_return_interpretation']=='RECLASSIFY_PRICE_RELIEF' else cash,weighted_demand=value(weighted)+.72*(value(vat_return)+value(refund)),insurer_contribution_loss=premium,insurer_backfill=premium)

def firm_policy(p,y,N,initialN,omit,halt):
    if 'firm' in omit or halt:return dict(tax_delta=0.,credit=0.,investment=0.,release=0.,human=0.,unknown=0)
    scale=N/initialN;taxdelta=None;credit=None;inv=None;release=None;human=0.;unknown=0
    if y<p['corp_start']:taxdelta=credit=inv=0.
    else:
        if p['corp_profit_base'] is not None and p['corp_reference_rate'] is not None and p['defense_surcharge_schedule'] is not None:
            taxdelta=p['corp_profit_base']*scale*(.23*(1+schedule(p['defense_surcharge_schedule'],y))-p['corp_reference_rate'])
        if y<p['investment_start']:credit=0.
        elif p['tax_incentive_eligible'] is True and all(p[k] is not None for k in ['hyper_eligible_investment','hyper_extra_deduction','training_eligible_spend','training_credit_rate']):
            # Credit is applied to eligible incremental investment base, not depreciated stock again.
            credit=scale*(.23*p['hyper_eligible_investment']*p['hyper_extra_deduction']+p['training_eligible_spend']*p['training_credit_rate'])
        if p['firm_investment_response'] is not None and taxdelta is not None and credit is not None:inv=p['firm_investment_response']*(credit-taxdelta)
    if p['governance_compliance'] is True and y>=2028 and p['governance_release_fraction'] is not None and p['governance_eligible_retained'] is not None:
        release=p['governance_eligible_retained']*p['governance_release_fraction']*phase(y,2028)
        human=release*p['governance_allocation']['human']
        if inv is not None:inv+=release*(p['governance_allocation']['equipment']+p['governance_allocation']['research'])
    for x in [taxdelta,credit,inv,release]:unknown+=int(x is None)
    return dict(tax_delta=taxdelta,credit=credit,investment=inv,release=release,human=human,unknown=unknown)

def medical_reform(p,y,disabled,hub_disabled,previous_hubs):
    if disabled or y<p['medical_start']:return dict(patient_shift=0.,high_cost_relief=0.,awards=0.,saving=0.,palliative=0.,transition=0.,hubs=0.,government=0.,household=0.,insurer_payer_balance=0.,provider_receipt=0.,unknown=0)
    shift=0. if not p['annex4_patient_thirty'] else None if p['medical_total_bill_base'] is None or p['current_patient_share'] is None else p['medical_total_bill_base']*(.3-p['current_patient_share'])
    high=None if p['high_cost_eligible_amount'] is None or p['high_cost_relief_fraction'] is None else p['high_cost_eligible_amount']*p['high_cost_relief_fraction']
    award=None if any(p[k] is None for k in ['preventive_eligible_fee','preventive_award','equipment_eligible_fee','equipment_award']) else p['preventive_eligible_fee']*p['preventive_award']+p['equipment_eligible_fee']*p['equipment_award']
    saving=p['palliative_saving_base'];palliative=p['palliative_subsidy'] if p['palliative_start']<=y<p['palliative_start']+5 else 0.
    transition=p['transition_fee_support'] if 2028<=y<=2030 else 0.
    count=p['hub_target']*min(1.,max(0.,(y-2027)/8))
    hubs=0. if hub_disabled else None if p['hub_unit_cost'] is None else (count-previous_hubs)*p['hub_unit_cost']
    payer_delta=-value(shift)+value(high)+value(award)-value(saving)
    frac=p['medical_public_payer_fraction']
    govt=payer_delta*(frac if frac is not None else 0.)+value(palliative)+value(transition)+value(hubs)
    insurer_payer=None if frac is None else -payer_delta*(1-frac)
    return dict(patient_shift=shift,high_cost_relief=high,awards=award,saving=saving,palliative=palliative,transition=transition,hubs=hubs,government=govt,household=-value(shift)+value(high),insurer_payer_balance=insurer_payer,provider_receipt=value(award)-value(saving)+value(palliative)+value(transition),unknown=int(frac is None)+sum(x is None for x in [shift,high,award,saving,palliative,transition,hubs]))

def tax_flows(c,p,y,N,omit,halt):
    rules=policy_rules(p,y);tau=rules['standard_tax_rate'];general=N*p['household_income_share']*p['taxable_share']
    foodbase=None if p['food_share_of_tax_base'] is None else general*p['food_share_of_tax_base']
    # Generic base historically at10%; food base historically8%; disjoint final uses.
    rate_relief=(.1-tau)*(general-value(foodbase))
    foodrelief=0. if 'food' in omit else None if foodbase is None else (.08-rules['food_tax_rate'])*foodbase
    relief=rate_relief+value(foodrelief);hh=relief;tax=-relief;investment=pay=public=0.;credit_all=0.;outputs=0.;unknown=int(foodrelief is None);md={}
    for sec,a in c['sector_inputs'].items():
        start=p.get('sector_starts',{}).get(sec,p['base_start']);active=y>=start and not halt
        scale=1.015**(y-2025);R=a['R2025']*scale;P=a['p']*R
        credit=tau*P if active else 0.;output=tau*R if active else 0.;cut=(.1-tau)*P
        if sec=='medical':
            patient=p['patient_share']*output;insurer=p['insurer_share']*output;pub=p['public_share']*output
            premium=p['initial_premium_pass']*insurer;residual=insurer-premium
            extra=residual if p['medical_mode']=='PREMIUM' else 0.;topup=residual if p['medical_mode']=='PUBLIC' else 0.;internal=residual if p['medical_mode']=='INTERNAL' else 0.;unresolved=residual if p['medical_mode']=='UNALLOCATED_COMPAT' else 0.
            private=patient+premium+extra;pub+=topup
            md=dict(medical_output_vat=output,medical_patient_vat=patient,medical_insurer_vat=insurer,medical_initial_premium=premium,medical_extra_premium=extra,medical_public_vat=pub,medical_public_topup=topup,medical_internal=internal,medical_unallocated=unresolved,medical_insurer_operating_balance=-internal-unresolved,medical_insurer_financing_balance=-unresolved,medical_input_credit=credit)
        else:
            pub=output*(.2 if sec=='education' else 0.);private=output-pub
        business=(1-a['price'])*(cut+credit)
        hh+=a['price']*(cut+credit)+a['wage']*business-private
        investment+=a['invest']*business;pay+=a['wage']*business;public+=pub
        tax+=output-credit-cut;credit_all+=credit;outputs+=output
    ext_net=0.;ext_gross=0.;ext_credit=0.;ext_private=0.;ext_public=0.
    for sec,B in p['extra_bases'].items():
        if 'extra' in omit or halt or y<p.get('extra_base_start',p['base_start']):continue
        q=p['extra_input_ratios'][sec]
        if any(v is None for v in [B,q,p['extra_base_private_share'],p['extra_base_public_share']]):unknown+=1;continue
        req(close(p['extra_base_private_share']+p['extra_base_public_share'],1),'Extra base payer shares')
        base=B*N/c['initial']['nominal_gdp'];out=tau*base;cr=tau*base*q
        ext_gross+=out;ext_credit+=cr;ext_net+=out-cr;ext_private+=out*p['extra_base_private_share'];ext_public+=out*p['extra_base_public_share']
        hh+=.3*cr-out*p['extra_base_private_share'];investment+=.2*.7*cr
    tax+=ext_net;public+=ext_public
    req(close(ext_gross,ext_private+ext_public),'Extra VAT payers')
    return dict(household=hh,direct_tax=tax,investment=investment,public=public,relief=relief,food_relief=foodrelief,
        extra_net=ext_net,extra_output=ext_gross,extra_credit=ext_credit,extra_private=ext_private,extra_public=ext_public,input_credit=credit_all,output_vat=outputs,unknown=unknown,**md)

def run_path(c,spec):
    p=copy.deepcopy(c['parameters']);p.update(spec.get('overrides',{}));validate(p);omit=spec.get('omit',[]);a=c['initial']
    rows=[];C=I=K=H=0.;firm_Istate=0.;firm_cash_stock=0.;Y=a['real_gdp'];N=a['nominal_gdp'];coreY=Y;coreN=N;tax=a['tax'];pop=a['population'];birth=a['births'];death=a['deaths'];labor=pop*p['labor_initial_ratio'];foreign=p['foreign_stock_2026'];initialforeign=foreign;gap=0.;coreD=N/Y;prevN=N;prevY=Y
    trigger_edu=False;trigger_gini=None;trigger_migration=False;halt=False;internal_cum=0.;retained_use_cumulative=0.;previous_hubs=0.;prev_wage=a['nominal_wage_man'];prev_realwage=a['real_wage_man'];coreK=p['capital_ratio']*coreY
    for y in range(2026,2056):
        i=y-2026;rules=policy_rules(p,y);triggers='triggers' not in omit
        if y==2035 and triggers:
            lastgrowth=rows[-1]['real_growth_pct']/100 if rows else 0.
            trigger_edu=lastgrowth<.012  # lagged2034; no future information
            observed=p['gini_observations'].get(str(y));trigger_gini=None if observed is None else observed>.36
            trigger_migration=pop<100000000.
        if y>=p['circuit_evaluation_start'] and i and p['circuit_growth_floor'] is not None:
            halt=rows[-1]['real_growth_pct']/100<p['circuit_growth_floor']
        if y>=p['circuit_evaluation_start'] and p['circuit_gini_ceiling'] is not None:
            observed=p['gini_observations'].get(str(y))
            if observed is not None:halt=halt or observed>p['circuit_gini_ceiling']
        oil=.03 if y==2026 and p['apply_oil_to_initial'] else 0.
        risk=oil+(.05 if y==2027 else 0.)+(.03 if y==2031 else 0.)+(.01 if y>=p['disaster_anchor'] and (y-p['disaster_anchor'])%3==0 else 0.)+(.005 if y>=p['climate_anchor'] and (y-p['climate_anchor'])%2==0 else 0.)
        inflation=.02+(.02 if oil else 0.)+(.05 if y==2027 else 0.)
        migrants=0.;cap_status='INACTIVE';ceiling=None
        if i:
            birth*=.975;death*=1.015
            if y>=2030:
                desired=p['migration_annual'];capfrac=.05*(1.2 if trigger_migration else 1.)
                if foreign is not None and p['foreign_value_added_per_person_trn'] is not None:
                    ceiling=coreN*capfrac/p['foreign_value_added_per_person_trn'];migrants=max(0.,min(desired,ceiling-foreign));foreign+=migrants;cap_status='CONDITIONAL_STOCK_GDP_CONTRIBUTION_CAP'
                else:migrants=desired;cap_status='ILLUSTRATIVE_FLOW_CAP_NOT_EVALUABLE'
            prevpop=pop;pop+=birth-death+migrants
            extra_workers=value(p['elderly_additional_workers'])*phase(y,2028) if not halt else 0.
            foreign_labor_extra=0. if foreign is None or p['foreign_labor_participation'] is None else (foreign-initialforeign)*(p['foreign_labor_participation']-p['labor_initial_ratio'])
            labornew=pop*p['labor_initial_ratio']+extra_workers+foreign_labor_extra
            lg=labornew/labor-1;labor=labornew
            growth=.01+p['labor_response']*lg-risk
            coreY*=1+growth;coreN*=1+growth+inflation;coreD=coreN/coreY
        elif oil:coreY*=1-oil;coreN*=1-oil+.02;coreD=coreN/coreY
        f=tax_flows(c,p,y,coreN,omit,halt)
        if i==0:
            # Initial2026 is an observed-design anchor. No new policy flows at t0.
            f={k:0. if isinstance(v,(int,float)) else v for k,v in f.items()}
        refund=None
        if triggers and i:
            key=str(y-1);actual=(p['vat_observed_revenue'] or {}).get(key);expected=(p['vat_expected_revenue'] or {}).get(key)
            if actual is not None and expected is not None:refund=.5*max(actual-expected,0.)
        giniadd=p['gini_relief_increment'] if trigger_gini else 0.
        ss=social(p,y,f['relief'],giniadd,refund,'social' in omit or halt or not i)
        firm=firm_policy(p,y,coreN,a['nominal_gdp'],omit,halt or not i)
        med=medical_reform(p,y,'medical' in omit or halt or not i,'hubs' in omit,previous_hubs)
        if i:previous_hubs=rules['hub_count']
        edu_multiplier=value(p['education_trigger_multiplier']) if trigger_edu and p['education_trigger_multiplier'] is not None else 1.
        invflow=None if p['investment_flow_share'] is None else p['investment_flow_share']*coreN*phase(y,p['investment_start']) if i and not halt else 0.
        budget=p['education_program_budget']
        edubase=budget if budget is not None else None if p['education_flow_share'] is None else p['education_flow_share']*coreN
        eduflow=None if edubase is None else edubase*phase(y,p['education_start'])*edu_multiplier if i and not halt else 0.
        scholarship=None if p['scholarship_spend'] is None else p['scholarship_spend']*phase(y,p['education_start']) if i and not halt else 0.
        edu_bonds=None if eduflow is None or scholarship is None or p['education_bond_share'] is None else (eduflow+scholarship)*p['education_bond_share']
        # Itemized and generic promotion are kept in separate case families.
        # Existing generic promotion is a separate residual channel; tax/retained funds enter once here.
        invest_nom=value(invflow)+value(firm['investment'])+f['investment']+value(med['hubs'])
        education_nom=value(eduflow)+value(scholarship)+firm['human']
        elderly_subsidy=None if p['elderly_additional_workers'] is None or p['elderly_subsidy_per_worker_man'] is None else p['elderly_additional_workers']*phase(y,2028)*p['elderly_subsidy_per_worker_man']/1e8 if i else 0.
        pension=None if p['elderly_additional_workers'] is None or p['pension_relief_per_worker_man'] is None else p['elderly_additional_workers']*phase(y,2028)*p['pension_relief_per_worker_man']/1e8 if i else 0.
        admin_saving=None if p['invoice_cost_saving'] is None else p['invoice_cost_saving'] if y>=p['admin_start'] and i else 0.
        admin_firm=value(admin_saving)+value(elderly_subsidy)
        firm_response=value(p['firm_investment_response']) if not halt else 0.
        invest_nom+=firm_response*admin_firm
        firm_sources=value(firm['credit'])-value(firm['tax_delta'])+value(firm['release'])+admin_firm
        firm_investment=value(firm['investment'])+firm_response*admin_firm
        firm_uninvested=firm_sources-firm_investment-firm['human']
        req(close(firm_sources,firm_investment+firm['human']+firm_uninvested),'Firm allocation')
        feedback=p['income_feedback']*gap*coreD
        reclassified=value(ss['vat_return']) if p['vat_return_interpretation']=='RECLASSIFY_PRICE_RELIEF' else 0.
        cash=f['household']-reclassified+ss['household']+med['household']+value(pension)
        Ctarget=p['domestic_share']*(.72*(cash+feedback-ss['household'])+ss['weighted_demand'])/coreD
        if i:
            C=(1-p['lambda_C'])*C+p['lambda_C']*Ctarget
            I=(1-p['lambda_I'])*I+p['lambda_I']*invest_nom/coreD
            firm_Istate=(1-p['lambda_I'])*firm_Istate+p['lambda_I']*firm_investment/coreD
            firm_cash_stock+=firm_sources-firm_Istate*coreD-firm['human']
        supply=p['capital_yield']*(1-p['depreciation'])*K+p['education_yield']*(1-p['education_decay'])*H
        if p['growth_hypothesis_mode']=='EDUCATION_LEVEL':education_level=p['education_level_effect']*coreY*phase(y,p['education_start'])
        else:education_level=0.
        finite=0.
        if p['growth_hypothesis_mode']=='FINITE_FLOW_HYPOTHESIS' and p['education_start']<=y<=2035:
            # Bounded level-equivalent demand scenario, never permanent annual compounding.
            finite=coreY*(p['consumption_hypothesis_pp']+p['investment_hypothesis_pp'])*phase(y,p['investment_start'])
        desired=coreY+p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite
        capacity=coreY+supply+p['slack']*coreY+education_level
        Y=min(desired,capacity);unmet=max(desired-Y,0.);pressure=.5*unmet/coreY;N=Y*coreD*(1+pressure)
        if i or oil:tax=min(tax*(1+(N/prevN-1)*p['elasticity'])*(.9 if y==2031 else 1.),N*.3)
        direct=f['direct_tax']+value(firm['tax_delta'])-value(firm['credit'])-.25*value(invflow)
        stamp=None if p['stamp_tax_removed'] is None else p['stamp_tax_removed'] if y>=p['admin_start'] else 0.
        direct-=value(stamp)
        digital=None if p['digital_system_cost'] is None else p['digital_system_cost'] if p['admin_start']<=y<=2040 else 0.
        expenditure=a['expenditure_proxy']*1.025**i+f['public']+ss['government']+med['government']+value(eduflow)+value(scholarship)+value(elderly_subsidy)+value(pension)+value(digital)
        taxdiag=tax+direct;Kprev=K;Hprev=H;previous_coreK=coreK;coreK=p['capital_ratio']*coreY
        replacement=coreK-(1-p['depreciation'])*previous_coreK if i else 0.
        if i:K=(1-p['depreciation'])*K+I;H=(1-p['education_decay'])*H+education_nom/coreD
        gap=Y-coreY;internal_cum+=f['medical_internal']
        wage_shock=.99 if p['wage_shock_start']<=y<p['wage_shock_start']+2 else 1.
        edu_wage=1+p['education_wage_level_effect']*phase(y,p['education_start']) if p['growth_hypothesis_mode']=='EDUCATION_LEVEL' else 1.
        realwage_proxy=a['real_wage_man']*wage_shock*edu_wage*(1+.3*gap/coreY)
        nominalwage_proxy=a['nominal_wage_man']*(coreD/(a['nominal_gdp']/a['real_gdp']))*wage_shock*edu_wage*(1+.3*gap/coreY)
        retained_used=value(firm['release']);retained_use_cumulative+=retained_used
        internal_remaining=None if p['insurer_initial_resources'] is None or p['internal_resource_return'] is None else p['insurer_initial_resources']*(1+p['internal_resource_return'])**i-internal_cum
        unknown=f['unknown']+firm['unknown']+med['unknown']+sum(x is None for x in [ss['premium_relief'],ss['in_kind'],ss['vat_return'],invflow,eduflow,scholarship,edu_bonds,elderly_subsidy,pension,stamp,digital,refund])
        r=dict(case=spec['id'],year=y,scope='NEW_PARTIAL_UNCALIBRATED',real_gdp_trn=Y,nominal_gdp_trn=N,core_real_gdp_trn=coreY,
          real_growth_pct=(Y/prevY-1)*100 if i or oil else 0.,tax_macro_trn=tax,tax_diagnostic_trn=taxdiag,expenditure_diagnostic_trn=expenditure,
          fiscal_balance_partial_trn=taxdiag-expenditure,funding_gap_proxy_trn=max(expenditure-taxdiag,0.),
          household_disposable_nominal_trn=p['household_income_share']*coreN+cash+feedback,household_policy_cash_nominal_trn=cash,
          household_consumption_real_proxy_trn=p['household_income_share']*coreY+C,C_demand_real_trn=C,I_policy_real_trn=I,
          investment_promotion_trn=invflow,education_spending_trn=eduflow,capital_total_real_trn=coreK+K,capital_delta_real_trn=K,human_capital_resource_stock_trn=H,
          population_persons=pop,births_persons=birth,deaths_persons=death,labor_force_population_proxy=labor,net_migration_conditional_persons=migrants,
          nominal_wage_proxy_man=nominalwage_proxy,real_wage_proxy_man=realwage_proxy,
          unmet_demand_real=unmet,price_pressure_proxy=pressure,energy_logistics_shock_pct=15. if y==2026 else 0.,medical_internal_cumulative=internal_cum,insurance_relief_trn=ss['premium_relief'],in_kind_trn=ss['in_kind'],vat_social_return_trn=ss['vat_return'],automatic_refund_trn=refund,
          corporate_realized_investment=firm_Istate,corporate_cash_buffer_partial=firm_cash_stock,corporate_external_funding_need_partial=max(-firm_cash_stock,0.),corporate_cash_change=firm_sources,corporate_cash_uninvested=firm_uninvested,corporate_retained_use_cumulative=retained_use_cumulative,medical_internal_resources_remaining=internal_remaining,corporate_tax_delta=firm['tax_delta'],corporate_credit=firm['credit'],corporate_induced_investment=firm['investment'],retained_used_sensitivity=firm['release'],
          medical_reform_insurer_balance=med['insurer_payer_balance'],medical_provider_receipt=med['provider_receipt'],medical_patient_shift=med['patient_shift'],medical_high_cost_relief=med['high_cost_relief'],medical_incentives=med['awards'],palliative_saving=med['saving'],palliative_subsidy=med['palliative'],hub_spend=med['hubs'],
          extra_base_net_tax=f['extra_net'],education_bond_gross_partial=edu_bonds,scholarship_spend=scholarship,
          trigger_education=int(trigger_edu),trigger_gini=None if trigger_gini is None else int(trigger_gini),trigger_migration=int(trigger_migration),circuit_halted=int(halt),
          unknown_component_count=unknown,foreign_cap_status=cap_status,foreign_stock_conditional=foreign,foreign_cap_persons=ceiling,
          dividend_disclosure_required=disclosure(p,y),gini_actual=None,nominal_wage_median_actual=None,real_wage_median_actual=None,income_median_actual=None,engel_actual=None,
          actual_bond_issuance_trn=None,PB_trn=None,debt_stock_trn=None,policy_interest_rate_pct=a['interest_rate_pct'] if not i else None,CPI_pct=None,full_F_GDP_trn=None,full_F_tax_trn=None,full_F_fiscal_balance_trn=None,
          education_level_effect=education_level,finite_effect_sensitivity=finite,**f,**rules)
        # Internal identities; household/firm/insurer transfers checked apart from national completeness.
        req(close(f['medical_output_vat'],f['medical_patient_vat']+f['medical_initial_premium']+f['medical_extra_premium']+f['medical_public_vat']+f['medical_internal']+f['medical_unallocated']),'Medical final payers')
        req(close(f['medical_insurer_vat'],f['medical_initial_premium']+f['medical_extra_premium']+f['medical_public_topup']+f['medical_internal']+f['medical_unallocated']),'Insurer funding')
        if med['insurer_payer_balance'] is not None:
            req(close(med['household']+med['provider_receipt']+med['insurer_payer_balance']+value(med['hubs']),med['government']),'Medical reform transfer ledger')
        req(close(value(ss['insurer_contribution_loss']),value(ss['insurer_backfill'])),'Social insurer transfer')
        if i:req(close(K,(1-p['depreciation'])*Kprev+I),'Capital identity')
        req(close(Y-coreY,p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite-unmet),'GDP decomposition')
        req(close(taxdiag,tax+direct),'Tax decomposition')
        r['_identity_capital_residual']=K-(1-p['depreciation'])*Kprev-I if i else 0.
        r['_identity_medical_residual']=f['medical_insurer_vat']-f['medical_initial_premium']-f['medical_extra_premium']-f['medical_public_topup']-f['medical_internal']-f['medical_unallocated']
        rows.append(r);prevN=N;prevY=Y
    return rows

def exemption_eligible(annual_sales_man):return annual_sales_man<=240

def annex_debt_split(year,additional_tax,additional_debt):
    """Annex6G conditional split; no invented120trn issuance or94% target."""
    if additional_tax is None or additional_debt is None:return (None,None,None)
    if year<2039:return (0.,0.,additional_debt)
    repay=min(max(additional_tax,0.)*.5,max(additional_debt,0.));rebate=max(additional_tax,0.)*.5
    return repay,rebate,additional_debt-repay

def load_reference(c):
    raw=zlib.decompress(base64.b64decode(c['baseline_csv_zlib_base64']))
    req(sha(raw)==c['baseline_csv_sha256'],'Baseline reference bytes')
    return list(csv.DictReader(io.StringIO(raw.decode())))

def policy_map(c):
    lines=['# SPE｜F本文・Annex 全項目対応表','',
        'Status: DRAFT / PARTIAL IMPLEMENTATION / NON-CANONICAL','',
        '政策読取固定Commit: `'+c['policy_commit']+'`（作業開始時main）。本文とAnnexを別原本で固定。作業ブランチはmainへ同期・変更しない。',
        '旧比較固定Commit: `'+c['baseline_commit']+'`。旧モデルを変更・再計算せず720行の保存CSVを参照。',
        '以下は空行以外の原文全行を網羅した対応表。初期値・評価項目・リスク等の密集行はさらに項目分割。見出し/理念/参考試算も記録し、制度実装済みと混同しない。',
        '「現在区分」は準拠済み/暫定代替/未実装/原文未指定/要解釈。「暫定代替」は条件式や施行フラグが実装済みでも、金額・行動式・解釈が未確定な項目。未実装の定量効果を0と結論しない。',
        '対応する関数名/入力キーを示す。policy_rules=施行/条件、tax_flows=税・負担、social=所得条件、firm_policy=企業、medical_reform=医療、run_path=動学/人口/トリガー。source registryは政策テキスト保持であり数値実装ではない。','']
    for source in c['sources']:
        name=Path(source['path']).name
        lines+=['## '+name,'',f"bytes={source['bytes']} / SHA-256=`{source['sha256']}`",'',
          '|原文章節・行/項|原文項目|種別|改良前区分/実装箇所|現在区分|差異・対応結果|新実装|残る理由|',
          '|---|---|---|---|---|---|---|---|']
        for r in c['policy_items']:
            if r['source']!=name:continue
            cols=[r['section']+' L'+str(r['line'])+'.'+str(r['part']),r['text'],r['type'],r['before']+' / '+r['old_location'],r['status'],r['result'],r['implementation'],r['remaining_reason']]
            lines.append('|'+ '|'.join(x.replace('|','／').replace('\n',' ') for x in cols)+'|')
    lines+=['','## 計算上の未指定入力','',
        '各入力Noneはデータ欠落。TEXT_KNOWN_PARTIALは既知/継承可能な成分の部分計算、ILLUSTRATIVE_ALLは明示した架空条件で式を試す感度である。どちらも全F推計ではない。',
        'food_share/土地等ベース、企業利益/償却率/付加税幅、保険料対象群、給付単価、地域拠点費、緩和ケア節減、人口労働係数、VAT実績予想、停止閾値等は原文に定量値がない。入力JSONのparameter_basis・unresolved参照。']
    return '\n'.join(lines)+'\n'

def verify(c,paths,old):
    log=[]
    req(len(old)==720 and len({r['case'] for r in old})==24,'24/720 reference')
    req(len({(r['case'],r['year']) for r in old})==720,'Duplicate reference')
    for src in c['sources']:
        b=src['utf8'].encode();req(len(b)==src['bytes'] and sha(b)==src['sha256'],'Policy source bytes')
        needed={i for i,l in enumerate(src['utf8'].splitlines(),1) if l.strip()}
        mapped={r['line'] for r in c['policy_items'] if r['source']==Path(src['path']).name}
        req(needed==mapped,'Policy line missing from map')
    log.append('PASS source2 byte identities; all nonempty source lines mapped (atomic conditions retained)')
    log.append('REUSE Claude arithmetic22530 cells/account PASS; no policy-fidelity or economic-validity PASS inferred')
    log.append('PASS original24/720 read-only reference identity; old model not executed/modified')
    for case,rs in paths.items():
        req(len(rs)==30 and [r['year'] for r in rs]==list(range(2026,2056)),'Year continuity')
        for r in rs:
            req(math.isfinite(r['real_gdp_trn']) and r['real_gdp_trn']>0,'GDP finite')
            req(close(r['tax_diagnostic_trn']-r['expenditure_diagnostic_trn'],r['fiscal_balance_partial_trn']),'Fiscal partial identity')
            req(r['full_F_GDP_trn'] is None and r['gini_actual'] is None and r['PB_trn'] is None,'Unknown misrepresented')
            req(r['financial_transactions_taxed']==0,'Financial transaction not excluded')
            req(abs(r['_identity_capital_residual'])<1e-8 and abs(r['_identity_medical_residual'])<1e-8,'Flow stock identity')
    log.append('PASS all new paths: years/GDP/tax/capital/medical/SS-insurer/partial fiscal identities; actual unknown metrics blank')
    p=c['parameters'];req(policy_rules(p,2027)['food_tax_rate']==0 and policy_rules(p,2030)['food_tax_rate']==.08 and policy_rules(p,2035)['food_tax_rate']==.05,'Food stages')
    req(exemption_eligible(240) and not exemption_eligible(240.01),'240 exemption boundary')
    test=copy.deepcopy(p);test['cohorts']=[dict(income_man=i,persons=1.,contribution_rate=.15,mpc=.8) for i in [300.,300.01,500.,500.01]];test['in_kind_per_eligible_man']=1.;r=social(test,2030,0.,0.,0.,False)
    req(close(r['premium_relief'],(300+300.01+500)*.15*.35/1e8) and close(r['in_kind'],1/1e8),'Income thresholds')
    req(annex_debt_split(2040,10,3)==(3,5.,0) and annex_debt_split(2040,None,3)==(None,None,None),'Annex debt split')
    # No invented ordering: early expansion before5% is a valid simulation input.
    early=copy.deepcopy(c['cases'][1]);early['overrides']['base_start']=2032
    rs=run_path(c,early);req(rs[2032-2026]['medical_output_vat']>0,'Unrequested pre5% prohibition')
    log.append('PASS tax/food dates,500/300 inclusive income thresholds,240 threshold, incentive caps and Annex debt conditional split; no invented policy ordering')
    req(paths['TEXT_KNOWN_PARTIAL'][2028-2026]['insurance_relief_trn'] is None,'Unknown population distribution treated as zero')
    req(paths['TEXT_KNOWN_PARTIAL'][2035-2026]['trigger_gini'] is None,'Unknown Gini trigger forced')
    req(paths['ILLUSTRATIVE_ALL'][2035-2026]['trigger_gini']==1,'Gini branch')
    req(paths['ILLUSTRATIVE_ALL'][2035-2026]['automatic_refund_trn']==.5,'50% VAT refund')
    # Empty forecasts must not silently use macro-tax as observed VAT.
    req(paths['TEXT_KNOWN_PARTIAL'][2035-2026]['automatic_refund_trn'] is None,'VAT forecast fabricated')
    for r in paths['ILLUSTRATIVE_ALL'][:4]:req(r['foreign_package_active']==0,'Migration before2030')
    req(all(r['net_migration_conditional_persons']==0 for r in paths['ILLUSTRATIVE_ALL'] if r['year']<2030),'Premature migration')
    req(any(r['circuit_halted'] for r in paths['CIRCUIT_ILLUSTRATION']),'Circuit branch')
    req(paths['ANNEX4_MEDICAL_EXTENSION'][2028-2026]['medical_patient_shift']>0 and paths['ILLUSTRATIVE_ALL'][2028-2026]['medical_patient_shift']==0,'Annex4 mixed into body')
    req(all(r['medical_output_vat']==0 for r in paths['ANNEX6_CUT_FIRST_ONLY'] if r['year']<2038),'Annex6 ordering')
    log.append('PASS2035 branches/VAT50%/missing-condition unknown/migration2030/circuit example; Annex4 and Annex6 kept in separate cases')
    inv=paths['INVEST_START_ONLY_2029'];base=paths['ILLUSTRATIVE_ALL']
    req(all(a['standard_tax_rate']==b['standard_tax_rate'] for a,b in zip(inv,base)),'DM05 coupled again')
    req(inv[2]['corporate_credit']<base[2]['corporate_credit'],'DM05 independent start inactive')
    for name in ['ILLUSTRATIVE_PREMIUM','ILLUSTRATIVE_PUBLIC','ILLUSTRATIVE_INTERNAL']:
        req(all(r['medical_unallocated']==0 for r in paths[name]),'DM04 residual missing')
    log.append('PASS DM04 three closures retained; DM05 investment timing independent of tax timing')
    for spec in c['cases']:req(run_path(c,spec)==paths[spec['id']],'Simulation replay not identical')
    log.append('PASS repeated same-input simulation exact equality')
    return log

CORE_COLUMNS=['case','year','scope','real_gdp_trn','nominal_gdp_trn','real_growth_pct','tax_macro_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn','funding_gap_proxy_trn','household_disposable_nominal_trn','household_policy_cash_nominal_trn','household_consumption_real_proxy_trn','C_demand_real_trn','I_policy_real_trn','investment_promotion_trn','education_spending_trn','capital_total_real_trn','capital_delta_real_trn','human_capital_resource_stock_trn','population_persons','births_persons','deaths_persons','labor_force_population_proxy','net_migration_conditional_persons','nominal_wage_proxy_man','real_wage_proxy_man',
 'insurance_relief_trn','in_kind_trn','vat_social_return_trn','automatic_refund_trn','corporate_realized_investment','corporate_cash_buffer_partial','corporate_external_funding_need_partial','unmet_demand_real','price_pressure_proxy','energy_logistics_shock_pct','corporate_cash_change','corporate_cash_uninvested','corporate_retained_use_cumulative','medical_internal_resources_remaining','corporate_tax_delta','corporate_credit','corporate_induced_investment','retained_used_sensitivity','medical_output_vat','medical_patient_vat','medical_insurer_vat','medical_initial_premium','medical_extra_premium','medical_public_vat','medical_public_topup','medical_internal','medical_internal_cumulative','medical_unallocated','medical_insurer_operating_balance','medical_insurer_financing_balance','medical_input_credit','medical_reform_insurer_balance','medical_provider_receipt','medical_patient_shift','medical_high_cost_relief','medical_incentives','palliative_saving','palliative_subsidy','hub_spend','hub_count','food_relief','extra_base_net_tax','education_bond_gross_partial','scholarship_spend','standard_tax_rate','food_tax_rate','corporate_rate','trigger_education','trigger_gini','trigger_migration','circuit_halted','unknown_component_count','foreign_cap_status','dividend_disclosure_required','gini_actual','nominal_wage_median_actual','real_wage_median_actual','income_median_actual','engel_actual','actual_bond_issuance_trn','PB_trn','debt_stock_trn','policy_interest_rate_pct','CPI_pct','full_F_GDP_trn','full_F_tax_trn','full_F_fiscal_balance_trn',
 'delta_old_dynamic_GDP','delta_old_dynamic_tax','delta_old_dynamic_expenditure','delta_old_dynamic_population']

def run_report(c,paths,old,logs):
    oldbase={int(r['year']):r for r in old if r['case']=='DYNAMIC_BASE'}
    lines=['# SPE｜F原文準拠化・年次部分計算 実行報告','',
      'Status: DRAFT / PARTIAL IMPLEMENTATION / UNCALIBRATED / NON-CANONICAL','',
      '## 結果の位置づけ','',
      '原文全行対応・実装可能な制度条件/勘定/動学の補完・2026〜2055計算・旧24経路比較を実行した。ただし全国の課税ベース/所得分布/企業反応/医療財源等がなく、F全体の原文準拠定量モデルの完成には未達。数値は既知・仮定付き成分の部分計算で、全Fの予測・政策因果推定ではない。全F総GDP/税収/財政収支はCSVのfull_F_*で空欄を維持した。',
      '旧24経路720行は保存CSVから読むだけで、旧モデルを再計算・変更しない。新'+str(len(paths))+'経路'+str(len(paths)*30)+'行を年次実行。比較CSVには旧720行の選択列も含める。原本全114列は入力内の固定比較CSVに保存されている。',
      '新たに計算可能: 食品0→8→5の独立税率、所得500/300万円条件付き軽減/現物給付、企業利益/追加償却/訓練控除から投資、土地/他不動産等の追加VAT勘定、医療改革と拠点投資、教育用途別部分発行、出生死亡と2030移民、2035条件判定と50%還元、開示40%の2解釈。制度ルールと金額未確定を分ける。','',
      '## 固定参照と既存PASS','',
      '政策原本2件: mainの作業開始時Commit `'+c['policy_commit']+'`。本文/Annexの実バイトサイズ・SHAは対応表と入力sourcesに記載。作業ブランチへ政策を上書きしない。',
      '旧動学 `'+c['baseline_commit']+'` / `handoff/f-macro-dynamic-dm04-dm05-20261117/`。Claude `'+c['claude_commit']+'` の検算報告を取得・読取。22,530セル算術/勘定PASSを再利用し、政策忠実性・経済妥当性のPASSには転用しない。','',
      '## 解釈を分離した事項','',
      '- 本文2035頃5%完全フラット化に対し、基準側は2035一斉課税化の年次近似。8%や食品0開始年、投資優遇開始2028などは原文未指定の感度入力。5%到達後課税拡大はAnnex6の専用ケースだけ。新コードは先行拡大を禁止しない。',
      '- 本文の40%超開示とAnnexの40%未満理由説明を別関数解釈で出力。配当40%強制や内部留保の自動現金化をしない。',
      '- 一律診療3割は本文基本にないAnnex4の拡張。ANNEX4_MEDICAL_EXTENSIONだけで有効。旧DM04の患者10%は出力VATの帰属で、診療費自己負担率とは別。',
      '- 社会還元給付は原文だけで税率低下メリットの組替か追加給付か一意でない。ADDITIONAL_TRANSFERは減税に加え別予算を要する給付、RECLASSIFY_PRICE_RELIEFは家計の既存メリットの分類替え（政府/保険者を通す実制度効果は未モデル）。追加給付を税収減分から無財源に賄えるとは扱わない。2ケースを分離した。',
      '- 2035トリガーは2034実質成長と評価直前人口で判定し2035計算へ反映するラグ解釈。ジニは入力観測/感度がある場合だけ判定。教育拡大率は未指定。+5-10%はポイント加算/相対増の二解釈。',
      '- VAT超過還元は前年のVAT実績と予想の正差×50%。総税収macroをVATと代用せず、観測欠落なら未算定。',
      '- GDP比5%外国人材上限は外国人ストックのGDP寄与額による上限という感度解釈。既存外国人ストック/一人当たり寄与がなければ上限遵守を確認できない（人口はその条件付き移民フロー経路）。人口比3-5%の目標と別概念。',
      '- 2026初期値と2026油ショック前後は両立条件が曖昧。通常は2026初期値を保持、OIL_INITIAL_ALTのみ同年ショックを追加適用。災害/気候の起算年も仮定で入力化。',
      '- 税弾性1.5-2を原文条件へ戻し感度化。税収/GDP30%は政策目標判定とし、直接税診断まで都合よく切り下げない。',
      '- 消費/投資の年成長仮説を恒久複利加算へ戻さない。資源フロー.004/.003はRESOURCE_FLOW_ONLY_SENSITIVITYだけ（企業項目別チャネルを外して重複を防止）。通常のILLUSTRATIVEは投資促進を新規償却/訓練控除・留保使途から生成し、教育は仮定予算2兆円。どちらも原文に金額がない。EDUCATION_LEVEL_READINGはGDP+.3%/賃金+.2%を水準として独立解釈。FINITE_FLOW_HYPOTHESISは2028-35限定の需要換算感度で、原文の成長率効果を再現したものではない。',
      '- 地域拠点1000（範囲800-1200）・2028-35等は条件付き数量計画。拠点単価/便益/健康寿命の実測がないので完成実績や節減予測ではない。','',
      '## ケース・入力の意味','',
      'TEXT_KNOWN_PARTIALは未指定金額をNoneのまま除外した部分集計（欠落の効果を0と断定しない）。ILLUSTRATIVE_ALLと派生ケースは、入力内に明示した架空の課税ベース・代表群・費用・行動反応を用いる式の動作/感度。全国額の推定ではない。係数を旧682兆/旧460兆/参考1580兆に合わせていない。',
      '供給上限が拘束すると医療帰属を変えても実質GDPは同じになり得る。価格圧力proxyや税収は異なる。これを帰属の経済効果がないという証明にしない。企業列は資金配分目標と実現投資stateを分離し、差額を部分現金バッファに記録する（企業全体の資金繰りではない）。unknown_component_countは列挙した金額欠落の件数で、全未実装論点数ではない。',
      'ILLUSTRATIVEは社会還元の追加予算解釈を含む。NONE基準との比較で政策純効果を語らず、構造差・範囲差・係数差を併記する。DM04のPUBLIC/INTERNALがGDPに同じ影響とは一般化しない（調達財源・実残高・機会費用は不足）。','',
      '|ケース|定義|','|---|---|']
    for spec in c['cases']:
        labels=[]
        if spec.get('omit'):labels+=['除外チャネル='+','.join(spec['omit'])]
        if spec.get('annex6'):labels+=['Annex6代替順序のみ（債務120/113等を再現しない）']
        if spec.get('annex4'):labels+=['Annex4診療3割拡張']
        for k in ['medical_mode','elasticity','growth_hypothesis_mode','payout_interpretation','vat_return_interpretation','investment_start','gini_increment_mode']:
            if k in spec.get('overrides',{}):labels.append(k+'='+str(spec['overrides'][k]))
        lines.append('|'+spec['id']+'|'+('; '.join(labels) or '原文既知条件の部分計算/架空入力の統合感度')+'|')
    years=[2030,2035,2038,2045,2055]
    for title,keys in [('GDP・税・政府', [('real_gdp_trn','実質GDP'),('nominal_gdp_trn','名目GDP'),('tax_diagnostic_trn','税収診断'),('expenditure_diagnostic_trn','歳出診断'),('fiscal_balance_partial_trn','部分財政差額')]),('家計・投資・人口',[('household_disposable_nominal_trn','家計所得'),('household_consumption_real_proxy_trn','消費proxy'),('I_policy_real_trn','政策投資'),('capital_total_real_trn','資本'),('population_persons','人口')])]:
        lines+=['','## '+title,'','兆円（人口は人）。全値は部分・感度。旧/新は計算範囲が異なる。','','|ケース|年|'+'|'.join(label for _,label in keys)+'|','|---|---:|'+'---:|'*len(keys)]
        for name in ['OLD_DYNAMIC_BASE','TEXT_KNOWN_PARTIAL','ILLUSTRATIVE_ALL','ILLUSTRATIVE_PREMIUM','ILLUSTRATIVE_PUBLIC','ILLUSTRATIVE_INTERNAL','ANNEX6_CUT_FIRST_ONLY']:
            for year in years:
                if name=='OLD_DYNAMIC_BASE':r=oldbase[year]
                else:r=paths[name][year-2026]
                vals=[]
                for k,_ in keys:
                    v=r.get(k)
                    if name=='OLD_DYNAMIC_BASE' and k=='fiscal_balance_partial_trn':v=float(r['tax_diagnostic_trn'])-float(r['expenditure_diagnostic_trn'])
                    vals.append('未算定' if v in [None,''] else f'{float(v):.6f}')
                lines.append('|'+name+'|'+str(year)+'|'+'|'.join(vals)+'|')
    lines+=['','## 新実装チャネルの条件付き寄与','',
      '下表はILLUSTRATIVE_ALL−当該チャネル除外ケース。順序依存・相互作用があり合計は総効果にならない。新規施策の実証効果ではない。','','|除外ケース|2030GDP差|2035GDP差|2038GDP差|2045GDP差|2055GDP差|','|---|---:|---:|---:|---:|---:|']
    for name in ['NO_FOOD_CHANNEL','NO_SOCIAL_CHANNEL','NO_FIRM_CHANNEL','NO_MEDICAL_HUB_CHANNEL','NO_TRIGGERS','NO_EXTRA_BASES','NO_LABOR_MIGRATION_PACKAGE']:
        lines.append('|'+name+'|'+'|'.join(f"{paths['ILLUSTRATIVE_ALL'][y-2026]['real_gdp_trn']-paths[name][y-2026]['real_gdp_trn']:+.6f}" for y in years)+'|')
    lines+=['','##2055目標の判定（出力を強制修正しない）'.replace('##2055','## 2055'),'','|ケース|人口8500万以上|ジニ.35以下|税/GDP30%以内（部分診断）|','|---|---|---|---|']
    for name in ['TEXT_KNOWN_PARTIAL','ILLUSTRATIVE_ALL']:
        targets=evaluate_targets(paths[name][-1]);lines.append('|'+name+'|'+str(targets['population_85m'])+'|未算定|'+str(targets['tax_ratio_30pct_partial'])+'|')
    lines+=['','## 検証：構造・算術・忠実性・経済妥当性の区別','','|区分|結果|','|---|---|',
        '|モデル構造|部分計算・勘定/ストック式の実装。DSGE/全Fモデル完成ではない|',
        '|算術|変更部分の条件分岐・恒等式・再実行一致を確認|',
        '|政策忠実性|原文全行対応、本文/Annex対案区別、既知閾値/条件を実装。未指定金額/複数解釈は未解消のため全面PASSとはしない|',
        '|経済的妥当性|未較正・判定保留。GDP/税/財政の絶対水準は政策評価に使用しない|','','```text']+logs+['```','',
        '独立CLI2回によるCSV・対応表・報告書のバイト一致と、保存後固定Commitからの事後取得SHA一致は引渡し回答で報告する。','',
        '## 未達・理由','',
        '|項目|理由区分|対応/限界|','|---|---|---|']
    for u in c['unresolved']:lines.append('|'+u['item']+'|'+u['reason']+'|'+u['action']+'|')
    lines+=['','本来指標未算定: 政策金利（2026初期0.75以降）、実国債発行/総債務/PB、株主配当・内部留保総額・日経平均、実労働者人口/非正規率、全国の名目/実質賃金中央値/所得中央値/ジニ/エンゲル。初期値はinput.initialに保持。雇用/賃金はproxyと名付け、代表群から全国中央値を作らない。出生/死亡/人口も入力仮定付きであり予測ではない。',
        '技術的に計算器を実装できないため停止した項目はない。主な未達理由は原文の条件不足・統計/行動係数不足・政策解釈の未裁定である。未達を管理文書の生成や試験PASSで完了扱いにしない。','',
        '## 再実行・引渡し','',
        '標準ライブラリのみ。新モデルと入力JSONでオフライン実行。入力は政策原文・対応項目・固定比較CSV（内部zlib+Base64）を含む。配布ZIP等は使わない。','',
        '```bash','python3 SPE_F_Text_Model_DRAFT_20261117.py SPE_F_Text_Inputs_DRAFT_20261117.json --outdir replay','```','',
        '新規5原本のみwork/chatgpt-handoffのhandoff/f-text-aligned-20261117/へ格納。main/政策原本/旧固定成果/正式エンジンは変更しない。正式Acceptance/Close/Freeze/Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。']
    return '\n'.join(lines)+'\n'

def evaluate_targets(row):
    # Targets are comparisons, never adjustments to calculated paths.
    return {'population_85m':row['population_persons']>=85000000,
            'gini_035':None if row['gini_actual'] is None else row['gini_actual']<=.35,
            'tax_ratio_30pct_partial':row['tax_diagnostic_trn']<=row['nominal_gdp_trn']*.3}

def main():
    a=argparse.ArgumentParser();a.add_argument('inputs');a.add_argument('--outdir',required=True);args=a.parse_args()
    c=json.loads(Path(args.inputs).read_text());old=load_reference(c)
    paths={spec['id']:run_path(c,spec) for spec in c['cases']};logs=verify(c,paths,old)
    base={int(r['year']):r for r in old if r['case']=='DYNAMIC_BASE'}
    combined=[]
    for r in old:
        rr={k:r.get(k,'') for k in CORE_COLUMNS};rr['case']='OLD_'+r['case'];rr['scope']='FIXED_REFERENCE_SELECTED_COLUMNS'
        rr['fiscal_balance_partial_trn']=float(r['tax_diagnostic_trn'])-float(r['expenditure_diagnostic_trn'])
        combined.append(rr)
    for rows in paths.values():
        for r in rows:
            b=base[r['year']]
            for new,k in [('delta_old_dynamic_GDP','real_gdp_trn'),('delta_old_dynamic_tax','tax_diagnostic_trn'),('delta_old_dynamic_expenditure','expenditure_diagnostic_trn'),('delta_old_dynamic_population','population_persons')]:r[new]=r[k]-float(b[k])
            combined.append(r)
    out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
    # New floats formatted to10 significant digits; original reference strings remain unchanged.
    def cell(v):return format(v,'.10g') if isinstance(v,float) else v
    with (out/CSV).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=CORE_COLUMNS,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows({k:cell(r.get(k)) for k in CORE_COLUMNS} for r in combined)
    logs.append('PASS saved'+str(len(combined))+' rows including720 stored reference rows; new floats10 significant digits')
    (out/MAP).write_text(policy_map(c),encoding='utf-8');(out/REPORT).write_text(run_report(c,paths,old,logs),encoding='utf-8')
    print('\n'.join(logs));print('exit=0')
    for name in ['TEXT_KNOWN_PARTIAL','ILLUSTRATIVE_ALL','ILLUSTRATIVE_PREMIUM','ILLUSTRATIVE_PUBLIC','ILLUSTRATIVE_INTERNAL']:
        print(name,{k:paths[name][-1][k] for k in ['real_gdp_trn','tax_diagnostic_trn','funding_gap_proxy_trn','population_persons','unknown_component_count']})
if __name__=='__main__':main()
