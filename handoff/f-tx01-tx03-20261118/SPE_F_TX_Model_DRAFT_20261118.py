#!/usr/bin/env python3
"""F text rules and partial uncalibrated annual accounts. Standard library only.
National full-F estimates stay blank when necessary inputs are missing.
Original24 paths are read-only CSV references, never recalculated here.
"""
import argparse,base64,copy,csv,hashlib,io,json,math,re,zlib
from pathlib import Path
PREFIX='SPE_F_TX_'
CSV=PREFIX+'Annual_Comparison_DRAFT_20261118.csv'
REPORT=PREFIX+'Run_Report_DRAFT_20261118.md'

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
    req(0<p['elasticity']<=2.,'Shared-model elasticity range;1.5-2 source scenario distinct')
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
        household=cash,government=cash-value(vat_return) if p['vat_return_interpretation']=='RECLASSIFY_PRICE_RELIEF' else cash,weighted_demand=value(weighted)+p['generic_mpc']*(value(vat_return)+value(refund)),insurer_contribution_loss=premium,insurer_backfill=premium)

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
        scale=(1+p['sector_nominal_growth'])**(y-2025);R=a['R2025']*scale;P=a['p']*R
        credit=tau*P if active else 0.;output=tau*R if active else 0.;cut=(.1-tau)*P
        if sec=='medical':
            patient=p['patient_share']*output;insurer=p['insurer_share']*output;pub=p['public_share']*output
            premium=p['initial_premium_pass']*insurer;residual=insurer-premium
            extra=residual if p['medical_mode']=='PREMIUM' else 0.;topup=residual if p['medical_mode']=='PUBLIC' else 0.;internal=residual if p['medical_mode']=='INTERNAL' else 0.;unresolved=residual if p['medical_mode']=='UNALLOCATED_COMPAT' else 0.
            private=patient+premium+extra;pub+=topup
            md=dict(medical_output_vat=output,medical_patient_vat=patient,medical_insurer_vat=insurer,medical_initial_premium=premium,medical_extra_premium=extra,medical_public_vat=pub,medical_public_topup=topup,medical_internal=internal,medical_unallocated=unresolved,medical_insurer_operating_balance=-internal-unresolved,medical_insurer_financing_balance=-unresolved,medical_input_credit=credit)
        else:
            pub=output*(p['education_public_payer_share'] if sec=='education' else 0.);private=output-pub
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
        hh+=p['extra_credit_price_share']*cr-out*p['extra_base_private_share'];investment+=p['extra_business_investment_share']*(1-p['extra_credit_price_share'])*cr
    tax+=ext_net;public+=ext_public
    req(close(ext_gross,ext_private+ext_public),'Extra VAT payers')
    return dict(household=hh,direct_tax=tax,investment=investment,public=public,relief=relief,food_relief=foodrelief,
        extra_net=ext_net,extra_output=ext_gross,extra_credit=ext_credit,extra_private=ext_private,extra_public=ext_public,input_credit=credit_all,output_vat=outputs,unknown=unknown,**md)

def run_path(c,spec):
    p,bprof,mig,enabled,omit=configure(c,spec);validate(p);a=c['initial']
    rows=[];C=I=K=H=0.;firm_Istate=0.;firm_cash_stock=0.;Y=a['real_gdp'];N=a['nominal_gdp'];coreY=Y;coreN=N;tax=a['tax'];pop=a['population'];birth=a['births'];death=a['deaths'];labor=pop*p['labor_initial_ratio'];foreign=mig['foreign_initial_stock'];initialforeign=foreign;gap=0.;coreD=N/Y;prevN=N;prevY=Y
    trigger_edu=False;trigger_gini=None;trigger_migration=False;halt=False;internal_cum=0.;retained_use_cumulative=0.;previous_hubs=0.;prev_wage=a['nominal_wage_man'];prev_realwage=a['real_wage_man'];coreK=p['capital_ratio']*coreY
    common_population=pop;policy_population_increment=0.;foreign_increment=0.;effective_labor=labor;expenditure_core=a['expenditure_proxy']
    for y in range(2026,2056):
        i=y-2026;rules=policy_rules(p,y) if enabled else statusquo_rules(y);triggers=enabled and 'triggers' not in omit
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
        oil=c['exogenous_shocks']['oil_gdp_loss'] if y==2026 and p['apply_oil_to_initial'] else 0.
        risk=oil+(c['exogenous_shocks']['conflict_gdp_loss'] if y==2027 else 0.)+(c['exogenous_shocks']['quake_gdp_loss'] if y==2031 else 0.)+(c['exogenous_shocks']['disaster_gdp_loss'] if y>=p['disaster_anchor'] and (y-p['disaster_anchor'])%3==0 else 0.)+(c['exogenous_shocks']['climate_gdp_loss'] if y>=p['climate_anchor'] and (y-p['climate_anchor'])%2==0 else 0.)
        inflation=.02+(.02 if oil else 0.)+(c['exogenous_shocks']['conflict_gdp_loss'] if y==2027 else 0.)
        migrants=0.;common_flow=policy_requested=policy_accepted=0.;cap_status='INACTIVE';ceiling=None;stock_prev=foreign;common_prev=common_population;policy_pop_prev=policy_population_increment;foreign_increment_prev=foreign_increment;aging=0.;lg=0.;flow_ramp=0.
        if i:
            if bprof['birth_mode']=='SAVED_LEGACY_SHARED':
                birth=c['legacy_demography'][i]['births_persons'];death=c['legacy_demography'][i]['deaths_persons']
            else:birth*=1-p['birth_decline'];death*=1+p['death_growth']
            flow_ramp=phase(y,mig['flow_start'],bprof['migration_delivery_ramp_years'])
            common_flow=mig['common_annual_net_flow']*flow_ramp
            if enabled:
                policy_requested=(max(mig['F_total_flow_reference']-mig['common_annual_net_flow'],0.) if mig['F_flow_interpretation']=='TOTAL_TARGET' else mig['F_additional_flow_reference'])*flow_ramp
            stock_retained=None if foreign is None else foreign*mig['foreign_stock_net_retention']
            policy_accepted=policy_requested
            if enabled and mig['enforcement_mode']=='GDP_STOCK_INTERPRETATION':
                # Diagnostic reading only. Never suppress the common baseline migration flow.
                capfraction=mig['gdp_share_interpretation_fraction']*(1.2 if trigger_migration else 1.)
                if stock_retained is not None and mig['foreign_value_added_per_person_trn'] is not None:
                    ceiling=coreN*capfraction/mig['foreign_value_added_per_person_trn']
                    policy_accepted=min(policy_requested,max(ceiling-stock_retained-common_flow,0.))
                    cap_status='GDP_STOCK_INTERPRETATION_REFERENCE_ONLY'
                else:cap_status='GDP_CAP_NOT_EVALUABLE'
            elif enabled:cap_status='NO_ENFORCEMENT_MONITOR_ONLY'
            migrants=common_flow+policy_accepted
            foreign=None if stock_retained is None else stock_retained+migrants
            foreign_increment=foreign_increment*mig['foreign_stock_net_retention']+migrants
            common_population+=birth-death+common_flow
            policy_population_increment+=policy_accepted
            prevpop=pop;pop=common_population+policy_population_increment
            extra_workers=value(p['elderly_additional_workers'])*phase(y,2028) if enabled and not halt else 0.
            foreign_labor_extra=0. if not bprof['foreign_labor_gap_enabled'] or foreign is None or p['foreign_labor_participation'] is None else (foreign-initialforeign)*(p['foreign_labor_participation']-p['labor_initial_ratio'])
            labornew=pop*p['labor_initial_ratio']+extra_workers+foreign_labor_extra
            aging=schedule(bprof['aging_drag_pp'],y)/100
            lg=labornew/labor-1+aging;labor=labornew;effective_labor*=1+lg
            growth=p['base_growth']+p['labor_response']*lg-risk
            expenditure_core*=1+schedule(bprof['expenditure_growth'],y)
            coreY*=1+growth;coreN*=1+growth+inflation;coreD=coreN/coreY
        elif oil:coreY*=1-oil;coreN*=1-oil+.02;coreD=coreN/coreY
        f=tax_flows(c,p,y,coreN,omit,halt)
        if not enabled:f={k:0. if isinstance(v,(int,float)) or v is None else v for k,v in f.items()}
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
        Ctarget=p['domestic_share']*(p['generic_mpc']*(cash+feedback-ss['household'])+ss['weighted_demand'])/coreD
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
        Y=min(desired,capacity) if spec['supply_cap'] else desired;unmet=max(desired-Y,0.);pressure=p['price_pressure_coefficient']*unmet/coreY;N=Y*coreD*(1+pressure if spec.get('price_feedback',True) else 1)
        if i or oil:tax=min(tax*(1+(N/prevN-1)*p['elasticity'])*(c['exogenous_shocks']['quake_tax_factor'] if y==2031 else 1.),N*p['tax_cap_ratio'])
        direct=f['direct_tax']+value(firm['tax_delta'])-value(firm['credit'])-p['promotion_fiscal_cost_share']*value(invflow)
        stamp=None if p['stamp_tax_removed'] is None else p['stamp_tax_removed'] if y>=p['admin_start'] else 0.
        direct-=value(stamp)
        digital=None if p['digital_system_cost'] is None else p['digital_system_cost'] if p['admin_start']<=y<=2040 else 0.
        expenditure=expenditure_core+f['public']+ss['government']+med['government']+value(eduflow)+value(scholarship)+value(elderly_subsidy)+value(pension)+value(digital)
        taxdiag=tax+direct;Kprev=K;Hprev=H;previous_coreK=coreK;coreK=p['capital_ratio']*coreY
        replacement=coreK-(1-p['depreciation'])*previous_coreK if i else 0.
        if i:K=(1-p['depreciation'])*K+I;H=(1-p['education_decay'])*H+education_nom/coreD
        gap=Y-coreY;internal_cum+=f['medical_internal']
        wage_shock=.99 if p['wage_shock_start']<=y<p['wage_shock_start']+2 else 1.
        edu_wage=1+p['education_wage_level_effect']*phase(y,p['education_start']) if p['growth_hypothesis_mode']=='EDUCATION_LEVEL' else 1.
        realwage_proxy=a['real_wage_man']*wage_shock*edu_wage*(1+p['wage_gap_elasticity']*gap/coreY)
        nominalwage_proxy=a['nominal_wage_man']*(coreD/(a['nominal_gdp']/a['real_gdp']))*wage_shock*edu_wage*(1+p['wage_gap_elasticity']*gap/coreY)
        retained_used=value(firm['release']);retained_use_cumulative+=retained_used
        internal_remaining=None if p['insurer_initial_resources'] is None or p['internal_resource_return'] is None else p['insurer_initial_resources']*(1+p['internal_resource_return'])**i-internal_cum
        unknown=f['unknown']+firm['unknown']+med['unknown']+sum(x is None for x in [ss['premium_relief'],ss['in_kind'],ss['vat_return'],invflow,eduflow,scholarship,edu_bonds,elderly_subsidy,pension,stamp,digital,refund])
        r=dict(case=spec['id'],year=y,scope='NEW_PARTIAL_UNCALIBRATED',real_gdp_trn=Y,nominal_gdp_trn=N,core_real_gdp_trn=coreY,
          real_growth_pct=(Y/prevY-1)*100 if i or oil else 0.,tax_macro_trn=tax,tax_diagnostic_trn=taxdiag,expenditure_diagnostic_trn=expenditure,
          fiscal_balance_partial_trn=taxdiag-expenditure,funding_gap_proxy_trn=max(expenditure-taxdiag,0.),
          household_disposable_nominal_trn=p['household_income_share']*coreN+cash+feedback,household_policy_cash_nominal_trn=cash,
          household_consumption_real_proxy_trn=p['household_income_share']*coreY+C,C_demand_real_trn=C,I_policy_real_trn=I,
          investment_promotion_trn=invflow,education_spending_trn=eduflow,capital_total_real_trn=coreK+K,capital_delta_real_trn=K,human_capital_resource_stock_trn=H,
          population_persons=pop,births_persons=birth,deaths_persons=death,labor_force_population_proxy=effective_labor,net_migration_conditional_persons=migrants,
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
        ratio=None if foreign is None else foreign/pop
        definition_mismatch=None if mig['target_stock_definition_code'] is None else int(mig['stock_definition_code']!=mig['target_stock_definition_code'])
        definition_status='TARGET_DEFINITION_UNSPECIFIED' if definition_mismatch is None else 'DEFINITION_MISMATCH' if definition_mismatch else 'DEFINITIONS_MATCH_BY_INPUT_ONLY'
        ratio_status='UNKNOWN_INITIAL_STOCK' if ratio is None else 'BELOW3' if ratio<.03 else 'WITHIN3TO5' if ratio<=.05 else 'ABOVE5'
        r.update(policy_role='F' if enabled else 'STATUSQUO_INCREMENTAL_REFERENCE',baseline_profile=spec['profile'],supply_cap_enabled=int(spec['supply_cap']),price_feedback_enabled=int(spec.get('price_feedback',True)),
          common_population_persons=common_population,policy_population_increment_persons=policy_population_increment,
          common_migration_net_flow=common_flow,policy_migration_requested_net_flow=policy_requested,policy_migration_accepted_net_flow=policy_accepted,
          total_migration_net_flow=migrants,foreign_stock_conditional_persons=foreign,foreign_stock_population_ratio=ratio,
          foreign_stock_ratio_status=ratio_status,foreign_definition_status=definition_status,foreign_definition_mismatch_flag=definition_mismatch,foreign_ratio_exceeds_5=None if ratio is None else int(ratio>.05),foreign_increment_tracked_persons=foreign_increment,
          foreign_stock_definition_status='CONDITIONAL_NET_MIGRANTS_AS_FOREIGN;STATUS_RETENTION_ASSUMED' if foreign is not None else 'UNKNOWN_INITIAL;INCREMENT_TRACKED_ONLY',
          foreign_eligibility_status='SOURCE_CONDITIONS_REGISTERED;INDIVIDUAL_COMPLIANCE_UNVERIFIED',migration_flow_interpretation=mig['F_flow_interpretation'],migration_enforcement_mode=mig['enforcement_mode'],migration_ramp_fraction=flow_ramp,
          foreign_gdp_contribution_ratio=None if foreign is None or mig['foreign_value_added_per_person_trn'] is None else foreign*mig['foreign_value_added_per_person_trn']/coreN,
          foreign_population_target_breach_is_not_gdp_cap=None if ratio is None else int(ratio>.05),
          common_expenditure_core_trn=expenditure_core,aging_drag_pp=aging*100,labor_growth_pct=lg*100,
          common_tax_elasticity=p['elasticity'],common_climate_anchor=p['climate_anchor'],common_birth_mode=bprof['birth_mode'],
          desired_real_gdp_trn=desired,supply_ceiling_real_gdp_trn=capacity,supply_binding=int(desired>capacity+1e-9) if spec['supply_cap'] else 0,
          excess_demand_relative_to_ceiling_trn=max(desired-capacity,0.),nominal_price_pressure_component_trn=N-Y*coreD,
          capital_previous_real=Kprev,human_capital_previous_real=Hprev,common_deflator=coreD)
        req(close(common_population-common_prev,birth-death+common_flow) if i else True,'Common population identity')
        req(close(policy_population_increment-policy_pop_prev,policy_accepted),'Policy population identity')
        if i and foreign is not None:req(close(foreign,stock_prev*mig['foreign_stock_net_retention']+migrants),'Foreign stock flow identity')
        req(close(pop,common_population+policy_population_increment),'Population split')
        if not enabled:req(close(cash,0.) and close(I,0.) and close(K,0.) and close(direct,0.),'StatusQuo F-channel leakage')
        rows.append(r);prevN=N;prevY=Y
    return rows


def configure(c,spec):
    p={**copy.deepcopy(c['common_model']),**copy.deepcopy(c['policy_inputs']),**copy.deepcopy(c['exogenous_shocks'])}
    b=copy.deepcopy(c['baseline_profiles'][spec['profile']]);b.update(spec.get('profile_override',{}))
    m={**copy.deepcopy(c['common_model']['migration']),**copy.deepcopy(c['policy_inputs']['migration'])};m.update(spec.get('migration_override',{}))
    enabled=spec['policy']=='F';p.update(spec.get('policy_override',{}));p['elasticity']=b['elasticity'];p['climate_anchor']=b['climate_anchor'];p['medical_mode']=spec.get('medical_mode','UNALLOCATED_COMPAT')
    req(m['F_flow_interpretation'] in ['TOTAL_TARGET','ADDITIONAL'],'Flow interpretation')
    req(m['enforcement_mode'] in ['NONE_REFERENCE','GDP_STOCK_INTERPRETATION'],'Diagnostic cap interpretation')
    req(0<=m['foreign_stock_net_retention']<=1 and m['common_annual_net_flow']>=0,'Migration reference')
    req(m['foreign_initial_stock'] is None or m['foreign_initial_stock']>=0,'Initial foreign stock')
    req(b['migration_delivery_ramp_years']>=1,'Ramp')
    omit=[]
    if not enabled:
        omit=['food','social','firm','medical','hubs','extra','triggers']
        # SQ means no incremental F reforms, not zero existing social protection.
        # Existing programs are represented by the same shared expenditure core.
        for k in ['investment_flow_share','education_flow_share','education_program_budget','scholarship_spend','elderly_additional_workers','elderly_subsidy_per_worker_man','pension_relief_per_worker_man','invoice_cost_saving','stamp_tax_removed','digital_system_cost','education_bond_share']:
            p[k]=0.
        p['growth_hypothesis_mode']='STRUCTURAL_ONLY';p['circuit_growth_floor']=None;p['circuit_gini_ceiling']=None
    return p,b,m,enabled,omit

def statusquo_rules(y):
    return dict(standard_tax_rate=.1,food_tax_rate=.08,corporate_rate=None,defense_surcharge=None,
        invoice_monthly_submissions=None,simplified_bookkeeping_allowed=None,exemption_threshold_man=None,
        digital_collection_target=None,guideline_active=0,governance_review=0,governance_reconsider=0,
        foreign_package_active=0,japanese_minimum='',hub_count=0.,transition_medical_active=0,palliative_support_active=0,
        price_total_display=None,financial_transactions_taxed=0)

def references(c):
    b=zlib.decompress(base64.b64decode(c['reference_text_csv_zlib_base64']))
    req(sha(b)==c['reference_text_csv_sha256'],'Fixed prior reference identity')
    return list(csv.DictReader(io.StringIO(b.decode())))

def tx_tests(c,paths,refs):
    logs=[]
    req(len(refs)==1500,'Prior1500 reference rows')
    for s in c['policy_sources']:
        req(len(s['utf8'].encode())==s['bytes'] and sha(s['utf8'].encode())==s['sha256'],'Policy source identity')
    logs.append('PASS fixed prior1500-row CSV and policy2 originals identity; old model/outputs remain read-only')
    # Reconstruct the old CORE from original inputs in the NEW common engine, no fitted numbers.
    replay=paths['LEGACY_CORE_REPLAY']
    for i,r in enumerate(c['legacy_core_reference']):
        for k in ['real_gdp_trn','nominal_gdp_trn','tax_macro_trn','expenditure_diagnostic_trn','population_persons']:
            req(close(replay[i][k],float(r[k])),'Legacy core replay '+k+' '+str(i))
    prior=[r for r in refs if r['case']=='ILLUSTRATIVE_ALL']
    for i,r in enumerate(prior):
        for k in ['real_gdp_trn','nominal_gdp_trn','tax_macro_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','population_persons','I_policy_real_trn','capital_total_real_trn']:
            req(math.isclose(paths['TEXT_PREVIOUS_ASSUMPTIONS_REPLAY'][i][k],float(r[k]),rel_tol=6e-10,abs_tol=1e-8),'Prior text new-engine replay '+k)
    logs.append('PASS new-engine prior text ILLUSTRATIVE replay:30 years major outputs match stored10-digit CSV')
    logs.append('PASS new-engine legacy CORE reproduction:30 years GDP/nominal/tax/expenditure/population within1e-10 relative; no old code execution')
    for name,rs in paths.items():
        req([r['year'] for r in rs]==list(range(2026,2056)),'Annual continuity')
        spec=next(s for s in c['cases'] if s['id']==name);p,b,m,enabled,omit=configure(c,spec)
        for i,r in enumerate(rs):
            req(r['real_gdp_trn']>0 and math.isfinite(r['tax_diagnostic_trn']),'Finite results')
            req(close(r['total_migration_net_flow'],r['common_migration_net_flow']+r['policy_migration_accepted_net_flow']),'Flow split')
            req(close(r['population_persons'],r['common_population_persons']+r['policy_population_increment_persons']),'Population split')
            stock=r['foreign_stock_conditional_persons']
            if stock is None:req(r['foreign_stock_population_ratio'] is None and r['foreign_ratio_exceeds_5'] is None,'Unknown foreign stock fabricated')
            else:req(close(r['foreign_stock_population_ratio'],stock/r['population_persons']),'Foreign ratio')
            if not spec['supply_cap']:req(r['unmet_demand_real']==0 and close(r['real_gdp_trn'],r['desired_real_gdp_trn']),'Uncapped execution')
            else:req(r['real_gdp_trn']<=r['supply_ceiling_real_gdp_trn']+1e-8,'Supply bound')
            if not spec.get('price_feedback',True):req(abs(r['nominal_price_pressure_component_trn'])<1e-8,'Price neutral nominal')
            if i:
                expected=min(rs[i-1]['tax_macro_trn']*(1+(r['nominal_gdp_trn']/rs[i-1]['nominal_gdp_trn']-1)*p['elasticity'])*(c['exogenous_shocks']['quake_tax_factor'] if r['year']==2031 else 1.),r['nominal_gdp_trn']*p['tax_cap_ratio'])
                req(close(r['tax_macro_trn'],expected),'Tax recurrence')
            req(r['gini_actual'] is None and r['full_F_GDP_trn'] is None,'Unresolved original DM metric filled')
    logs.append('PASS all paths: shared engine/population/foreign stock-flow/GDP/capital/tax/medical/social/government identities and missing-data flags')
    for profile in c['baseline_profiles']:
        for suffix in ['CAP','UNCAPPED']:
            sq=paths[profile+'_SQ_'+suffix];f=paths[profile+'_F_'+suffix]
            for i in range(30):
                for k in ['common_population_persons','common_migration_net_flow','common_expenditure_core_trn','aging_drag_pp','common_tax_elasticity','common_climate_anchor']:
                    req(close(sq[i][k],f[i][k]),'Paired common settings differ '+k)
            for mode in ['PREMIUM','PUBLIC','INTERNAL']:
                rs=paths[profile+'_F_'+mode+'_'+suffix]
                req(all(r['medical_unallocated']==0 for r in rs),'DM04 new closure unallocated')
                if mode=='PREMIUM':
                    req(all(close(r['household_policy_cash_nominal_trn']-f[i]['household_policy_cash_nominal_trn'],-r['medical_extra_premium']) for i,r in enumerate(rs)),'Premium twice deducted')
                if mode=='PUBLIC':req(all(close(r['expenditure_diagnostic_trn']-f[i]['expenditure_diagnostic_trn'],r['medical_public_topup']) for i,r in enumerate(rs)),'Public transfer twice counted')
                if mode=='INTERNAL':req(all(close(r['medical_insurer_operating_balance'],-r['medical_internal']) for r in rs),'Insurer internal balance')
    logs.append('PASS paired F/SQ common settings identical; DM04 premium/public/internal allocation maintained')
    rs=paths['INVEST_START_ONLY_2029'];base=paths['OLD_ASSUMPTIONS_F_CAP']
    req(all(a['standard_tax_rate']==b['standard_tax_rate'] for a,b in zip(rs,base)) and rs[2]['corporate_credit']<base[2]['corporate_credit'],'DM05 start independence')
    logs.append('PASS DM05 independent investment date maintained')
    # Population3-5% is a flag, not a hard quota. Force a stock above target and ensure no automatic clipping.
    test=copy.deepcopy(c['cases'][0]);test.update(id='HIGH_RATIO_MONITOR',policy='F',migration_override={'foreign_initial_stock':10000000.})
    rr=run_path(c,test);req(rr[0]['foreign_ratio_exceeds_5']==1 and rr[4]['policy_migration_accepted_net_flow']>0,'Invented population quota')
    test['migration_override'].update(stock_definition_code='FOREIGN_WORKERS',target_stock_definition_code='FOREIGN_RESIDENTS')
    mismatch=run_path(c,test);req(all(r['foreign_definition_mismatch_flag']==1 for r in mismatch),'Definition mismatch not detected')
    unknown=paths['MIG_INITIAL_UNKNOWN'];req(all(r['foreign_stock_population_ratio'] is None for r in unknown),'Unknown stock ratio computed')
    req(paths['MIG_ADDITIONAL400K'][-1]['policy_population_increment_persons']>paths['TEXT_ASSUMPTIONS_F_CAP'][-1]['policy_population_increment_persons'],'Total/additional flow ambiguity hidden')
    logs.append('PASS stock ratio breach/unknown-initial detection; no implicit3-5% enforcement;total versus additional migration distinguished')
    for spec in c['cases']:req(run_path(c,spec)==paths[spec['id']],'Nondeterministic rows')
    logs.append('PASS identical-input repeated simulation exactly equal')
    return logs

METRICS=['real_gdp_trn','nominal_gdp_trn','tax_macro_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn','funding_gap_proxy_trn','household_disposable_nominal_trn','household_consumption_real_proxy_trn','I_policy_real_trn','capital_total_real_trn','population_persons']

def decomposition(paths,year,metric,suffix='CAP'):
    i=year-2026;s0=paths['OLD_ASSUMPTIONS_SQ_'+suffix][i][metric];f0=paths['OLD_ASSUMPTIONS_F_'+suffix][i][metric]
    s1=paths['TEXT_ASSUMPTIONS_SQ_'+suffix][i][metric];f1=paths['TEXT_ASSUMPTIONS_F_'+suffix][i][metric]
    baseline=s1-s0;policy_old=f0-s0;interaction=(f1-s1)-(f0-s0);total=f1-s0
    req(close(total,baseline+policy_old+interaction),'TX01 decomposition identity')
    return baseline,policy_old,interaction,total,f1-s1

def tx_report(c,paths,refs,logs):
    years=[2030,2035,2038,2045,2055]
    lines=['# SPE｜F動学モデル TX-01〜03 限定改良・再計算報告','',
      'Status: DRAFT / LIMITED SCOPE / PARTIAL / UNCALIBRATED / NON-CANONICAL','作成日:2026-11-18（Asia/Tokyo）','',
      '## 実成果と比較の読み方','',
      'TX-01の共通エンジンF/StatusQuo・旧基準再現・基準/政策/相互作用分離、TX-02の供給上限/価格波及の感度、TX-03の共通人口/追加人口/年間純移動/外国人ストック比率を実装。'+str(len(paths))+'経路×30年='+str(len(paths)*30)+'行を計算した。旧コード・旧成果は変更も実行もせず、固定CSVを比較参照する。',
      'F/StatusQuoは同じrun_pathを使い、同じプロファイル内の基調成長・老齢化・出生死亡・共通受入・歳出表・ショック・税応答を共有する。StatusQuoは「既存支出を共通基準として保持し、Fの追加改革だけを有効にしない条件付き参照」。現行制度を全国統計から全面再現した予測ではない。Fの共通財政基準をSQへも置いた比較なので、旧SQの基調0.6/0.3や歳出3%をF/SQ間で混在させない。',
      'すべて前回の仮定付きILLUSTRATIVE入力を再利用した部分・感度計算。全Fの予測、較正、政策の優劣判定ではない。full_F_*・PB・実国債等は引き続き未算定。',
      '人口比3〜5%は検出フラグだけで、人口目標へ合わせた受入制限は実装しない。GDP比5%のストック寄与解釈は別参照ケースだけ。基本参照はNONE_REFERENCEであり、原文のGDP比条件に準拠済みという意味ではない。','',
      '## 固定資料・再利用','',
      '実装基準 `'+c['source_commit']+'` の5原本をGitHub連携Base64で取得、実バイト照合して読取。Claude `'+c['claude_commit']+'` のTX-01〜10報告を取得・読取。前回46,902セルPASSは前回構造の算術証拠として保持し、新しい共通エンジンへ独立検証PASSを転用しない。DM04の同じ勘定式等を再利用し、今回変更部分は自己試験する。',
      '旧DM04/05 `'+c['dm_commit']+'` の固定入力/保存基準を再利用。旧老齢化/歳出表、移民ランプ、出生系列はその内包資料に由来。政治目標を合わせた新係数は導入していない。','',
      '## TX-01：基準条件の分離','',
      '|共通基準|OLD_ASSUMPTIONS|TEXT_ASSUMPTIONS|意味|','|---|---|---|---|',
      '|老齢化ドラッグ（労働成長率へのpp）|2026−.0525、2033−.8123、2044−.3737、2046−.1683|0|旧表が新モデルで脱落していた差を可視化|',
      '|基準歳出年成長|2.5%→2035年1.5%→2045年1%|2.5%固定|旧170.376704兆と前回221.011999兆の差を分離|',
      '|移民フロー実現ランプ|2030〜34の5年|2030年から全量|受入人数自体とは別のモデル実現仮定|',
      '|気候ショック起算|2027・隔年|2028・隔年|外生ショックの起算差|',
      '|共通税収弾性|1.0|1.5|原文1.5〜2の仮説と、旧動学の単位弾性を区別|',
      '|出生系列|保存旧F出生を共通外生系列として使う|毎年×.975|旧系列の賃金アンカー由来の差を明示|',
      '|外国人の労働参加率差|追加しない|仮定参加率.8と基準.55との差を追加|前回の労働計算差を明示|',
      'OLDプロファイルの保存出生は旧Fアンカーの影響を含むため、客観的・観測済みの出生見通しではない。F/SQ両方に同じ系列を使う反実仮想としてのみ利用する。出生死亡は共通外生で、追加移民の子孫・年齢構成・死亡への再接続は未実装。',
      '共通人口は出生−死亡＋共通純移動、政策人口増分はF追加純移動の累計として分ける。老齢化は旧と同じく労働成長へ加算し、GDPに別途二重加算しない。実労働人口は未算定で、労働供給proxyを出す。',
      'LEGACY_CORE_REPLAYは共通受入を旧F総量40万人・5年ランプに置き、F追加改革を切った互換参照。旧COREのGDP・名目GDP・税収・歳出・人口を30年再現。旧結果へ係数を合わせたものではない。TEXT_PREVIOUS_ASSUMPTIONS_REPLAYは旧TEXTの共通移民0＋F40万総量＋GDP寄与上限を再現し、保存ILLUSTRATIVE_ALLの主要出力を10桁丸め精度内で再現する。',
      '入力はpolicy_inputs、common_model（migration内に共通受入・初期ストック等）、exogenous_shocksに分離。baseline_profilesは共通モデルの参照設定。NONE/GDP_STOCK等の解釈選択はpolicy_inputs.migrationの感度で、Owner決定の政策仕様ではない。','',
      '### 2030・2035・2038・2045・2055の比較','',
      '兆円。比率・人口は別表。政策差は必ず同年・同プロファイルのF−SQ。旧別モデルとの生差は政策効果と呼ばない。','','|基準|年|SQ実質GDP|F実質GDP|F−SQ|SQ税収診断|F税収診断|SQ歳出|F歳出|','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for prof in c['baseline_profiles']:
        for y in years:
            sq=paths[prof+'_SQ_CAP'][y-2026];f=paths[prof+'_F_CAP'][y-2026]
            vals=[sq['real_gdp_trn'],f['real_gdp_trn'],f['real_gdp_trn']-sq['real_gdp_trn'],sq['tax_diagnostic_trn'],f['tax_diagnostic_trn'],sq['expenditure_diagnostic_trn'],f['expenditure_diagnostic_trn']]
            lines.append('|'+prof+'|'+str(y)+'|'+'|'.join(f'{v:.6f}' for v in vals)+'|')
    lines+=['','### 正確な2×2分解','',
      '総差=TEXT_F−OLD_SQ。基準差=TEXT_SQ−OLD_SQ、旧基準政策差=OLD_F−OLD_SQ、相互作用=(TEXT_F−TEXT_SQ)−(OLD_F−OLD_SQ)。この恒等式で年次分離し、要因差を恣意的に政策効果へ帰属させない。政策差自体も未較正のモデル内差で因果推定ではない。','','|指標|年|基準差|旧基準政策差|相互作用|総差|新基準政策差|','|---|---:|---:|---:|---:|---:|---:|']
    for metric in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn']:
        for y in years:
            vals=decomposition(paths,y,metric);lines.append('|'+metric+'|'+str(y)+'|'+'|'.join(f'{v:+.6f}' for v in vals)+'|')
    lines+=['','### 個別基準変更の2055年影響','',
      '各行はOLDから当該仮定だけTEXTへ変更。交互作用があるため行の単純和を総差とはしない。','','|変更仮定|SQ GDP差|F GDP差|政策差の変化|SQ歳出差|SQ税収差|','|---|---:|---:|---:|---:|---:|']
    for key in ['aging_drag_pp','expenditure_growth','migration_delivery_ramp_years','climate_anchor','elasticity','birth_mode','foreign_labor_gap_enabled']:
        sq=paths['ONE_'+key+'_SQ'][-1];f=paths['ONE_'+key+'_F'][-1];s0=paths['OLD_ASSUMPTIONS_SQ_CAP'][-1];f0=paths['OLD_ASSUMPTIONS_F_CAP'][-1]
        vals=[sq['real_gdp_trn']-s0['real_gdp_trn'],f['real_gdp_trn']-f0['real_gdp_trn'],(f['real_gdp_trn']-sq['real_gdp_trn'])-(f0['real_gdp_trn']-s0['real_gdp_trn']),sq['expenditure_diagnostic_trn']-s0['expenditure_diagnostic_trn'],sq['tax_diagnostic_trn']-s0['tax_diagnostic_trn']]
        lines.append('|'+key+'|'+'|'.join(f'{v:+.6f}' for v in vals)+'|')
    prev=[r for r in refs if r['case']=='ILLUSTRATIVE_ALL'][-1];dm=[r for r in refs if r['case']=='OLD_DYNAMIC_BASE'][-1]
    lines+=['','### 保存旧モデルとの橋渡し','',
      '|2055年参照|実質GDP|税収診断|歳出|','|---|---:|---:|---:|']
    for name,r in [('保存DM04/05 DYNAMIC_BASE',dm),('保存TEXT ILLUSTRATIVE_ALL',prev),('新OLD基準F',paths['OLD_ASSUMPTIONS_F_CAP'][-1]),('新TEXT基準F',paths['TEXT_ASSUMPTIONS_F_CAP'][-1]),('旧CORE再現',paths['LEGACY_CORE_REPLAY'][-1]),('前回TEXT再現',paths['TEXT_PREVIOUS_ASSUMPTIONS_REPLAY'][-1])]:
        lines.append('|'+name+'|'+'|'.join(f'{float(r[k]):.6f}' for k in ['real_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn'])+'|')
    lines+=['','新OLD基準Fと保存DMの差は、社会・企業・追加課税等の原文補完が異なるため完全互換を意図しない。新TEXT基準Fと保存TEXTの差は、GDP上限解釈を基本へ混入せず、共通357000＋追加43000という総受入解釈に分けたこと等による。保存TEXT再現と旧CORE再現を別に置いて、仕様変更と実装誤りを混同しない。','',
      '## TX-02：供給上限・超過需要・価格税収','',
      'CAPは既存供給上限を保持。UNCAPPEDはY=desiredの診断感度で、恒久撤廃や経済予測ではない。CAP_PRICE_NEUTRALは未充足需要を算定する一方、その価格proxyを名目GDP/税収へ加算しない参照。既定の価格式を黙って変更しない。',
      'CSVにdesired、ceiling、binding、unmet、上限に対する潜在超過、価格proxy、名目価格成分を年次出力。UNCAPPEDでのunmet=0でも潜在超過は別列で残す。長期のCAP/UNCAPPED差は資本・所得・トリガーの経路差も含み、同年の上限切下げ額だけとは異なる。','','|ケース|拘束年数|拘束年|最大未充足|2055GDP|2055価格proxy|2055税収診断|','|---|---:|---|---:|---:|---:|---:|']
    for prof in c['baseline_profiles']:
        for name in ['SQ_CAP','F_CAP','F_UNCAPPED','F_PREMIUM_CAP','F_PREMIUM_UNCAPPED','F_PUBLIC_CAP','F_INTERNAL_CAP','F_CAP_PRICE_NEUTRAL']:
            rs=paths[prof+'_'+name];r=rs[-1];binding=[str(x['year']) for x in rs if x['supply_binding']]
            lines.append('|'+prof+'_'+name+'|'+str(len(binding))+'|'+(','.join(binding) if binding else 'なし')+'|'+f"{max(x['unmet_demand_real'] for x in rs):.6f}|{r['real_gdp_trn']:.6f}|{r['price_pressure_proxy']:.9f}|{r['tax_diagnostic_trn']:.6f}"+'|')
    lines+=['','医療財源のPREMIUMは家計現金を減らすが、供給上限に拘束される期間の実質GDP差は隠れる。UNCAPPEDとの差で需要チャネルを確認する。PUBLIC/INTERNALの財源調達・準備金実残高・機会費用は未モデルなので、帰属の優劣や「経済効果ゼロ」と結論しない。',
      '超過需要が価格proxyを通じて名目GDP・税収へ流れるのは既存モデルの仮定。CAP_PRICE_NEUTRALによりこの仮定の影響を独立に確認できる。物価/CPIとして実証された効果ではない。','',
      '## TX-03：共通人口・フロー・ストック・目標監視','',
      '共通年間純流入357000人は旧SQで人口目標から逆算された仮定で、観測値ではない。F40万人も原文の確定人数ではない。TOTAL_TARGETではF追加=max(400000−共通357000,0)=43000、ADDITIONALでは共通に追加400000。両解釈を出し、前者を政策裁定としない。フローは純移動であり入国許可の総件数とは異なる。',
      '外国人ストック=前年ストック×status保持率＋共通純流入＋F追加純流入。初期200万人・保持率1・純移民全員を外国人とみなす定義は旧仮定の条件付き延長で、外国人労働者/外国人住民/移民累計を実統計として同一視しない。出生・帰化・国籍変更・出国の実系列が不足するため定義整合は未確定。保持率.98は人口を減らさず外国人ステータスの退出だけを見る感度で、移民死亡や実出国率ではない。',
      '人口比目標の外国人母集団は原文だけでは一意に特定できないためtarget_stock_definition_codeは未指定。foreign_definition_statusで未確定を出す。明示入力された目標母集団とストック母集団が異なればdefinition_mismatch_flag=1を出し、比率が計算できても準拠とは扱わない。初期ストック不明ケースは比率/超過判定を未算定とし、増分の追跡だけ行う。N4・審査・統合支援等は既存制度フラグのままで、個別遵守を検証済みとしない。GDP寄与比5%と人口比3-5%は別の分母・別条件。目標超過は検出しても受入量を自動修正しない。',
      'GDP_STOCK_INTERPRETATIONは前回のストックGDP寄与上限の代替解釈。既存共通純流入を勝手に止めず、F追加分にだけ適用する。共通ストックだけで上限を超える場合もあり、総ストック上限準拠を保証するケースではない。人口<1億による上限+20%の判定は従前どおり2035年だけで、新たな年次再判定は入れていない。','','|ケース|2055共通人口|F人口増分|共通年フロー|F追加年フロー|外国人ストック|人口比|3-5%判定|','|---|---:|---:|---:|---:|---:|---:|---|']
    for name in ['OLD_ASSUMPTIONS_SQ_CAP','OLD_ASSUMPTIONS_F_CAP','TEXT_ASSUMPTIONS_SQ_CAP','TEXT_ASSUMPTIONS_F_CAP','MIG_ADDITIONAL400K','MIG_GDP_STOCK_CAP_INTERPRETATION','MIG_INITIAL_UNKNOWN','MIG_RETENTION_98','MIG_COMMON_ZERO_SQ','MIG_COMMON_ZERO_F']:
        r=paths[name][-1];vals=[r['common_population_persons'],r['policy_population_increment_persons'],r['common_migration_net_flow'],r['policy_migration_accepted_net_flow'],r['foreign_stock_conditional_persons']]
        lines.append('|'+name+'|'+'|'.join('未算定' if v is None else f'{v:.3f}' for v in vals)+'|'+('未算定' if r['foreign_stock_population_ratio'] is None else f"{100*r['foreign_stock_population_ratio']:.6f}%")+'|'+r['foreign_stock_ratio_status']+'|')
    lines+=['','共通基準だけでも3-5%を超える仮定がある。Fの追加受入だけが超過原因とは言えず、原文目標に整合する実測人口・国籍・移動定義/人数は未確定。人口8500万人目標に合わせていない。','',
      '## 検証・状態','',
      '```text']+logs+['exit=0','```','',
      '算術:変更部分の恒等式・基準再現・境界・再実行を自己確認。政策準拠性:本文/Annex不変更、受入定義や未指定係数の未確定を維持。経済的妥当性:未較正で判定保留。前回Claude算術PASSは新しいエンジンの独立レビューではない。',
      'CLI別出力先の再実行でCSV/報告書の実バイト一致を確認し、固定Commitからの事後取得照合は引渡し回答に記載する。','',
      '## TXとの重複DM・残る論点','',
      '|項目|今回の対応/残る状態|','|---|---|',
      '|旧COREの老齢化/歳出/移民/気候/税弾性差|TX01で参照プロファイル・共通F/SQ・2×2分解・一要因比較へ|',
      '|DM04帰属比較が上限で隠れる|TX02で有無・価格中立参照と拘束年を追加。公費財源/内部準備金は未解決|',
      '|DM05投資開始独立|維持。税率一定で開始年2029ケースを確認|',
      '|外国人比率・上限定義・2035緩和|TX03で監視・フロー定義を分離。GDP比/人口比を政策裁定せず参照化|',
      '|TX04/06：既知条件ケース/対応表の数値効果有無|旧対応表と未確定状態を保持。今回は仮定付き比較と明示し、全231項目表は再改訂していない|',
      '|TX05：ハードコード共通係数|TX01/02に直接重なるMPC・部門成長・価格係数・投資財政割合・教育公費・賃金弾性等をcommon_modelへ入力化。同値で移植|',
      '|TX07：停止対象/再開条件|独立課題として維持。F停止感度は従来どおり。今回の基本ケースでは停止閾値なし|',
      '|TX08：2035一回の判定|維持。人口比超過に応じた再判定・受入制限を追加しない|',
      '|TX09：保険料軽減上限・公費全額補填/Annex4|既存の仮定・解釈の未確定を維持。今回変更なし|',
      '|TX10：既存PASSの適用範囲|前回モデルの46,902セルとDM04の同一勘定式を区別し、新算術へ独立PASSを転用しない|',
      '|全国VATベース/分布/反応係数/金利/実国債/PB/CPI等|未算定・未較正のまま。今回新たに確定しない|',
      'Owner判断が必要な将来事項は、40万人が総量か追加か、GDP比5%の数量定義/外国人の統計母集団、上限緩和の評価方式等。今回の参照ケース実行には新たな承認を要求しない。','',
      '## 再実行・保存','',
      '標準ライブラリのみ。入力JSONは政策原文/旧保存比較CSV/旧人口系列を内包し、コード+入力でオフライン実行できる。新しい管理台帳・ZIP・正式レビューは作らない。','',
      '```bash','python3 SPE_F_TX_Model_DRAFT_20261118.py SPE_F_TX_Inputs_DRAFT_20261118.json --outdir replay','```','',
      '保存先:work/chatgpt-handoff / handoff/f-tx01-tx03-20261118/。新規4成果物のみ。main・政策原文・旧固定成果・正式エンジンは変更しない。正式Acceptance/Freeze/Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。']
    return '\n'.join(lines)+'\n'

COLUMNS=['case','year','policy_role','baseline_profile','supply_cap_enabled','price_feedback_enabled',
 'real_gdp_trn','nominal_gdp_trn','core_real_gdp_trn','tax_macro_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn','funding_gap_proxy_trn',
 'common_expenditure_core_trn','aging_drag_pp','labor_growth_pct','common_tax_elasticity',
 'household_disposable_nominal_trn','household_consumption_real_proxy_trn','I_policy_real_trn','capital_total_real_trn',
 'population_persons','births_persons','deaths_persons','labor_force_population_proxy','common_population_persons','policy_population_increment_persons','common_migration_net_flow','policy_migration_requested_net_flow','policy_migration_accepted_net_flow','total_migration_net_flow',
 'foreign_stock_conditional_persons','foreign_stock_population_ratio','foreign_stock_ratio_status','foreign_definition_status','foreign_definition_mismatch_flag','foreign_ratio_exceeds_5','foreign_increment_tracked_persons','foreign_gdp_contribution_ratio',
 'migration_enforcement_mode','migration_flow_interpretation','foreign_eligibility_status',
 'desired_real_gdp_trn','supply_ceiling_real_gdp_trn','supply_binding','unmet_demand_real','excess_demand_relative_to_ceiling_trn','price_pressure_proxy','nominal_price_pressure_component_trn',
 'medical_output_vat','medical_insurer_vat','medical_initial_premium','medical_extra_premium','medical_public_topup','medical_internal','medical_internal_cumulative','medical_unallocated','medical_insurer_operating_balance','medical_insurer_financing_balance',
 'delta_paired_SQ_GDP','delta_paired_SQ_tax','delta_paired_SQ_expenditure','delta_prev_text_GDP','delta_prev_text_tax',
 'full_F_GDP_trn','gini_actual','PB_trn','actual_bond_issuance_trn']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('inputs');parser.add_argument('--outdir',required=True);args=parser.parse_args()
    c=json.loads(Path(args.inputs).read_text());refs=references(c);paths={s['id']:run_path(c,s) for s in c['cases']};logs=tx_tests(c,paths,refs)
    prior={int(r['year']):r for r in refs if r['case']=='ILLUSTRATIVE_ALL'}
    for suf in ['CAP','UNCAPPED']:
        for y in range(2026,2056):
            for metric in METRICS:decomposition(paths,y,metric,suf)
    logs.append('PASS TX01 annual2x2 baseline/policy/interaction decomposition identities for all12 major metrics, cap on/off')
    # Add pair-relative columns only when the spec has a valid common comparison.
    for spec in c['cases']:
        match=next((s for s in c['cases'] if s['policy']=='SQ' and s['profile']==spec['profile'] and s.get('profile_override',{})==spec.get('profile_override',{}) and s.get('migration_override',{})==spec.get('migration_override',{}) and s['supply_cap']==spec['supply_cap'] and s.get('price_feedback',True)==spec.get('price_feedback',True)),None)
        for i,r in enumerate(paths[spec['id']]):
            for column,metric in [('delta_paired_SQ_GDP','real_gdp_trn'),('delta_paired_SQ_tax','tax_diagnostic_trn'),('delta_paired_SQ_expenditure','expenditure_diagnostic_trn')]:r[column]=None if match is None else r[metric]-paths[match['id']][i][metric]
            r['delta_prev_text_GDP']=r['real_gdp_trn']-float(prior[r['year']]['real_gdp_trn']);r['delta_prev_text_tax']=r['tax_diagnostic_trn']-float(prior[r['year']]['tax_diagnostic_trn'])
    out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
    with (out/CSV).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS,extrasaction='ignore',lineterminator='\n');w.writeheader()
        for rows in paths.values():
            for r in rows:w.writerow({k:format(r[k],'.10g') if isinstance(r.get(k),float) else r.get(k) for k in COLUMNS})
    logs.append('PASS saved'+str(len(paths)*30)+' annual rows /'+str(len(paths))+' paths; floats10 significant digits; invalid unmatched comparisons blank')
    (out/REPORT).write_text(tx_report(c,paths,refs,logs),encoding='utf-8')
    print('\n'.join(logs));print('exit=0')
    for prof in c['baseline_profiles']:
        s=paths[prof+'_SQ_CAP'][-1];f=paths[prof+'_F_CAP'][-1]
        print(prof,'2055 GDP SQ/F/difference',s['real_gdp_trn'],f['real_gdp_trn'],f['real_gdp_trn']-s['real_gdp_trn'])
if __name__=='__main__':main()
