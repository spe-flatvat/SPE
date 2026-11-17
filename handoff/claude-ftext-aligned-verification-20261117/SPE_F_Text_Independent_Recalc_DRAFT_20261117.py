# Independent recompute of SPE_F_Text_Model_DRAFT_20261117 (26 new paths x 30 years) by Claude.
# Rewritten from the policy text (thresholds/dates) and a reading of the model's account structure; NOT importing the model.
# Usage: python3 -I indep_text.py <F_Text Inputs JSON> <F_Text Annual_Comparison CSV>
import json,csv,sys,copy
cfg=json.load(open(sys.argv[1],encoding='utf-8')); R=list(csv.DictReader(open(sys.argv[2],encoding='utf-8')))
D={(r['case'],int(r['year'])):r for r in R}
A=cfg['initial']; SEC=cfg['sector_inputs']
z=lambda x:0. if x is None else x
def ramp(y,s,n=3): return 0. if y<s else min(1.,(y-s+1)/n)
def sched(d,y):
    ks=sorted(int(k) for k in (d or {}) if int(k)<=y); return d[str(ks[-1])] if ks else 0.
def rates(p,y):
    tau=.10 if y<p['year8'] else .08 if y<p['year5'] else .05
    if y<p['food_zero_start']: food=.08
    elif y<p['food_eight_start']: food=0.
    elif y<p['year5']: food=.08
    else: food=.05
    return tau,food
def tax_flows(p,y,N,omit,halt):
    tau,food=rates(p,y); gen=N*p['household_income_share']*p['taxable_share']
    fb=None if p['food_share_of_tax_base'] is None else gen*p['food_share_of_tax_base']
    rr=(.1-tau)*(gen-z(fb)); fr=0. if 'food' in omit else (None if fb is None else (.08-food)*fb)
    relief=rr+z(fr); hh=relief; tax=-relief; inv=0.; pub=0.; cr_all=0.; outv=0.; unk=int(fr is None); m={}
    for s,a in SEC.items():
        st=p.get('sector_starts',{}).get(s,p['base_start']); act=(y>=st) and not halt
        Rv=a['R2025']*1.015**(y-2025); P=a['p']*Rv
        cred=tau*P if act else 0.; out=tau*Rv if act else 0.; cut=(.1-tau)*P
        if s=='medical':
            pat=p['patient_share']*out; ins=p['insurer_share']*out; pb=p['public_share']*out
            prem=p['initial_premium_pass']*ins; res=ins-prem; md=p['medical_mode']
            xp=res if md=='PREMIUM' else 0.; xt=res if md=='PUBLIC' else 0.; xi=res if md=='INTERNAL' else 0.; xu=res if md=='UNALLOCATED_COMPAT' else 0.
            priv=pat+prem+xp; pb+=xt
            m=dict(out=out,pat=pat,ins=ins,prem=prem,xp=xp,pubm=pb,xt=xt,xi=xi,xu=xu,cred=cred)
        else:
            pb=out*(.2 if s=='education' else 0.); priv=out-pb
        biz=(1-a['price'])*(cut+cred)
        hh+=a['price']*(cut+cred)+a['wage']*biz-priv; inv+=a['invest']*biz; pub+=pb
        tax+=out-cred-cut; cr_all+=cred; outv+=out
    en=0.
    for s,B in p['extra_bases'].items():
        if 'extra' in omit or halt or y<p.get('extra_base_start',p['base_start']): continue
        q=p['extra_input_ratios'][s]
        if any(v is None for v in [B,q,p['extra_base_private_share'],p['extra_base_public_share']]): unk+=1; continue
        base=B*N/A['nominal_gdp']; out=tau*base; cr=tau*base*q
        en+=out-cr; hh+=.3*cr-out*p['extra_base_private_share']; inv+=.2*.7*cr; pub+=out*p['extra_base_public_share']
    tax+=en
    return dict(hh=hh,tax=tax,inv=inv,pub=pub,relief=relief,en=en,unk=unk,**m)
def social(p,y,relief,gadd,refund,off):
    if off: return dict(prem=0.,kind=0.,vr=0.,refund=0.,hh=0.,gov=0.,wd=0.)
    co=p['cohorts']
    if y<p['insurance_start']: prem=kind=0.; wd=0.
    elif co is None: prem=kind=None; wd=None
    else:
        rate=p['insurance_reduction']+gadd if p['gini_increment_mode']=='PERCENTAGE_POINTS' else p['insurance_reduction']*(1+gadd)
        rate=min(rate,1.)
        low=[r for r in co if r['income_man']<=500]; kin=[r for r in co if r['income_man']<=300]
        prem=sum(r['income_man']*r['persons']*r['contribution_rate']*rate/1e8 for r in low)
        wd=sum(r['income_man']*r['persons']*r['contribution_rate']*rate*r['mpc']/1e8 for r in low)
        kind=None if p['in_kind_per_eligible_man'] is None else sum(r['persons'] for r in kin)*p['in_kind_per_eligible_man']/1e8
        if p['in_kind_per_eligible_man'] is not None: wd+=sum(r['persons']*p['in_kind_per_eligible_man']*r['mpc']/1e8 for r in kin)
    vr=None if p['vat_relief_social_return_fraction'] is None else relief*p['vat_relief_social_return_fraction']
    cash=z(prem)+z(kind)+z(vr)+z(refund)
    gov=cash-z(vr) if p['vat_return_interpretation']=='RECLASSIFY_PRICE_RELIEF' else cash
    return dict(prem=prem,kind=kind,vr=vr,refund=refund,hh=cash,gov=gov,wd=z(wd)+.72*(z(vr)+z(refund)))
def firm(p,y,N,off):
    if off: return dict(td=0.,cr=0.,inv=0.,rel=0.,hum=0.,unk=0)
    sc=N/A['nominal_gdp']; td=cr=inv=rel=None; hum=0.
    if y<p['corp_start']: td=cr=inv=0.
    else:
        if None not in (p['corp_profit_base'],p['corp_reference_rate'],p['defense_surcharge_schedule']):
            td=p['corp_profit_base']*sc*(.23*(1+sched(p['defense_surcharge_schedule'],y))-p['corp_reference_rate'])
        if y<p['investment_start']: cr=0.
        elif p['tax_incentive_eligible'] is True and None not in (p['hyper_eligible_investment'],p['hyper_extra_deduction'],p['training_eligible_spend'],p['training_credit_rate']):
            cr=sc*(.23*p['hyper_eligible_investment']*p['hyper_extra_deduction']+p['training_eligible_spend']*p['training_credit_rate'])
        if p['firm_investment_response'] is not None and td is not None and cr is not None: inv=p['firm_investment_response']*(cr-td)
    if p['governance_compliance'] is True and y>=2028 and p['governance_release_fraction'] is not None and p['governance_eligible_retained'] is not None:
        rel=p['governance_eligible_retained']*p['governance_release_fraction']*ramp(y,2028)
        g=p['governance_allocation']; hum=rel*g['human']
        if inv is not None: inv+=rel*(g['equipment']+g['research'])
    return dict(td=td,cr=cr,inv=inv,rel=rel,hum=hum,unk=sum(x is None for x in [td,cr,inv,rel]))
def medical(p,y,off,hub_off,prev):
    if off or y<p['medical_start']: return dict(shift=0.,high=0.,award=0.,sav=0.,pal=0.,tr=0.,hub=0.,gov=0.,hh=0.,ib=0.,prov=0.,unk=0)
    sh=0. if not p['annex4_patient_thirty'] else (None if p['medical_total_bill_base'] is None or p['current_patient_share'] is None else p['medical_total_bill_base']*(.3-p['current_patient_share']))
    hi=None if p['high_cost_eligible_amount'] is None or p['high_cost_relief_fraction'] is None else p['high_cost_eligible_amount']*p['high_cost_relief_fraction']
    aw=None if any(p[k] is None for k in ['preventive_eligible_fee','preventive_award','equipment_eligible_fee','equipment_award']) else p['preventive_eligible_fee']*p['preventive_award']+p['equipment_eligible_fee']*p['equipment_award']
    sav=p['palliative_saving_base']; pal=p['palliative_subsidy'] if p['palliative_start']<=y<p['palliative_start']+5 else 0.
    tr=p['transition_fee_support'] if 2028<=y<=2030 else 0.
    cnt=p['hub_target']*min(1.,max(0.,(y-2027)/8))
    hub=0. if hub_off else (None if p['hub_unit_cost'] is None else (cnt-prev)*p['hub_unit_cost'])
    pd=-z(sh)+z(hi)+z(aw)-z(sav); fr=p['medical_public_payer_fraction']
    gov=pd*(fr if fr is not None else 0.)+z(pal)+z(tr)+z(hub)
    return dict(shift=sh,high=hi,award=aw,sav=sav,pal=pal,tr=tr,hub=hub,gov=gov,hh=-z(sh)+z(hi),ib=None if fr is None else -pd*(1-fr),prov=z(aw)-z(sav)+z(pal)+z(tr),unk=int(fr is None)+sum(x is None for x in [sh,hi,aw,sav,pal,tr,hub]))
def run(spec):
    p=copy.deepcopy(cfg['parameters']); p.update(spec.get('overrides',{})); omit=spec.get('omit',[])
    out={}; C=I=K=H=0.; fIs=0.; fcs=0.; Y=A['real_gdp']; N=A['nominal_gdp']; cY=Y; cN=N; tax=A['tax']; pop=A['population']; b=A['births']; d=A['deaths']
    lab=pop*p['labor_initial_ratio']; fs=p['foreign_stock_2026']; fs0=fs; gap=0.; cD=N/Y; pN=N; pY=Y
    tg_edu=False; tg_gini=None; tg_mig=False; halt=False; icum=0.; rcum=0.; prevhub=0.; lastg=0.
    for y in range(2026,2056):
        i=y-2026; trg='triggers' not in omit
        if y==2035 and trg:
            tg_edu=lastg<.012; ob=p['gini_observations'].get(str(y)); tg_gini=None if ob is None else ob>.36; tg_mig=pop<1e8
        if y>=p['circuit_evaluation_start'] and i and p['circuit_growth_floor'] is not None: halt=lastg<p['circuit_growth_floor']
        if y>=p['circuit_evaluation_start'] and p['circuit_gini_ceiling'] is not None:
            ob=p['gini_observations'].get(str(y))
            if ob is not None: halt=halt or ob>p['circuit_gini_ceiling']
        oil=.03 if (y==2026 and p['apply_oil_to_initial']) else 0.
        risk=oil+(.05 if y==2027 else 0.)+(.03 if y==2031 else 0.)+(.01 if y>=p['disaster_anchor'] and (y-p['disaster_anchor'])%3==0 else 0.)+(.005 if y>=p['climate_anchor'] and (y-p['climate_anchor'])%2==0 else 0.)
        infl=.02+(.02 if oil else 0.)+(.05 if y==2027 else 0.); mig=0.; ceil=None
        if i:
            b*=.975; d*=1.015
            if y>=2030:
                want=p['migration_annual']; cf=.05*(1.2 if tg_mig else 1.)
                if fs is not None and p['foreign_value_added_per_person_trn'] is not None:
                    ceil=cN*cf/p['foreign_value_added_per_person_trn']; mig=max(0.,min(want,ceil-fs)); fs+=mig
                else: mig=want
            pop+=b-d+mig
            ew=z(p['elderly_additional_workers'])*ramp(y,2028) if not halt else 0.
            fl=0. if fs is None or p['foreign_labor_participation'] is None else (fs-fs0)*(p['foreign_labor_participation']-p['labor_initial_ratio'])
            ln=pop*p['labor_initial_ratio']+ew+fl; lg=ln/lab-1; lab=ln
            g=.01+p['labor_response']*lg-risk; cY*=1+g; cN*=1+g+infl; cD=cN/cY
        elif oil: cY*=1-oil; cN*=1-oil+.02; cD=cN/cY
        f=tax_flows(p,y,cN,omit,halt)
        if i==0: f={k:(0. if isinstance(v,(int,float)) else v) for k,v in f.items()}
        refund=None
        if trg and i:
            k=str(y-1); ac=(p['vat_observed_revenue'] or {}).get(k); ex=(p['vat_expected_revenue'] or {}).get(k)
            if ac is not None and ex is not None: refund=.5*max(ac-ex,0.)
        ga=p['gini_relief_increment'] if tg_gini else 0.
        ss=social(p,y,f['relief'],ga,refund,('social' in omit) or halt or not i)
        fm=firm(p,y,cN,halt or not i)
        if 'firm' in omit or halt: fm=dict(td=0.,cr=0.,inv=0.,rel=0.,hum=0.,unk=0)
        md=medical(p,y,('medical' in omit) or halt or not i,'hubs' in omit,prevhub)
        hubc=p['hub_target']*min(1.,max(0.,(y-2027)/8))
        if i: prevhub=hubc
        em=z(p['education_trigger_multiplier']) if (tg_edu and p['education_trigger_multiplier'] is not None) else 1.
        active=i and not halt
        invf=None if p['investment_flow_share'] is None else (p['investment_flow_share']*cN*ramp(y,p['investment_start']) if active else 0.)
        bud=p['education_program_budget']; eb=bud if bud is not None else (None if p['education_flow_share'] is None else p['education_flow_share']*cN)
        ef=None if eb is None else (eb*ramp(y,p['education_start'])*em if active else 0.)
        sch=None if p['scholarship_spend'] is None else (p['scholarship_spend']*ramp(y,p['education_start']) if active else 0.)
        ebond=None if ef is None or sch is None or p['education_bond_share'] is None else (ef+sch)*p['education_bond_share']
        inv_nom=z(invf)+z(fm['inv'])+f['inv']+z(md['hub']); edu_nom=z(ef)+z(sch)+fm['hum']
        w=p['elderly_additional_workers']
        els=None if w is None or p['elderly_subsidy_per_worker_man'] is None else (w*ramp(y,2028)*p['elderly_subsidy_per_worker_man']/1e8 if i else 0.)
        pen=None if w is None or p['pension_relief_per_worker_man'] is None else (w*ramp(y,2028)*p['pension_relief_per_worker_man']/1e8 if i else 0.)
        adm=None if p['invoice_cost_saving'] is None else (p['invoice_cost_saving'] if (y>=p['admin_start'] and i) else 0.)
        af=z(adm)+z(els); fr_=z(p['firm_investment_response']) if not halt else 0.
        inv_nom+=fr_*af; fsrc=z(fm['cr'])-z(fm['td'])+z(fm['rel'])+af; finv=z(fm['inv'])+fr_*af; funi=fsrc-finv-fm['hum']
        fb=p['income_feedback']*gap*cD; rec=z(ss['vr']) if p['vat_return_interpretation']=='RECLASSIFY_PRICE_RELIEF' else 0.
        cash=f['hh']-rec+ss['hh']+md['hh']+z(pen)
        Ct=p['domestic_share']*(.72*(cash+fb-ss['hh'])+ss['wd'])/cD
        if i:
            C=(1-p['lambda_C'])*C+p['lambda_C']*Ct; I=(1-p['lambda_I'])*I+p['lambda_I']*inv_nom/cD
            fIs=(1-p['lambda_I'])*fIs+p['lambda_I']*finv/cD; fcs+=fsrc-fIs*cD-fm['hum']
        sup=p['capital_yield']*(1-p['depreciation'])*K+p['education_yield']*(1-p['education_decay'])*H
        el=p['education_level_effect']*cY*ramp(y,p['education_start']) if p['growth_hypothesis_mode']=='EDUCATION_LEVEL' else 0.
        fin=0.
        if p['growth_hypothesis_mode']=='FINITE_FLOW_HYPOTHESIS' and p['education_start']<=y<=2035: fin=cY*(p['consumption_hypothesis_pp']+p['investment_hypothesis_pp'])*ramp(y,p['investment_start'])
        des=cY+p['capacity_absorption']*sup+C+I+edu_nom/cD+el+fin; cap=cY+sup+p['slack']*cY+el
        Y=min(des,cap); un=max(des-Y,0.); pr=.5*un/cY; N=Y*cD*(1+pr)
        if i or oil: tax=min(tax*(1+(N/pN-1)*p['elasticity'])*(.9 if y==2031 else 1.),N*.3)
        direct=f['tax']+z(fm['td'])-z(fm['cr'])-.25*z(invf)
        stamp=None if p['stamp_tax_removed'] is None else (p['stamp_tax_removed'] if y>=p['admin_start'] else 0.); direct-=z(stamp)
        dig=None if p['digital_system_cost'] is None else (p['digital_system_cost'] if p['admin_start']<=y<=2040 else 0.)
        exp=A['expenditure_proxy']*1.025**i+f['pub']+ss['gov']+md['gov']+z(ef)+z(sch)+z(els)+z(pen)+z(dig)
        td=tax+direct
        if i: K=(1-p['depreciation'])*K+I; H=(1-p['education_decay'])*H+edu_nom/cD
        gap=Y-cY; icum+=f.get('xi',0.); rcum+=z(fm['rel'])
        out[y]=dict(real_gdp_trn=Y,nominal_gdp_trn=N,real_growth_pct=(Y/pY-1)*100 if (i or oil) else 0.,tax_macro_trn=tax,tax_diagnostic_trn=td,expenditure_diagnostic_trn=exp,
            fiscal_balance_partial_trn=td-exp,funding_gap_proxy_trn=max(exp-td,0.),household_disposable_nominal_trn=p['household_income_share']*cN+cash+fb,household_policy_cash_nominal_trn=cash,
            household_consumption_real_proxy_trn=p['household_income_share']*cY+C,C_demand_real_trn=C,I_policy_real_trn=I,investment_promotion_trn=invf,education_spending_trn=ef,
            capital_total_real_trn=p['capital_ratio']*cY+K,capital_delta_real_trn=K,human_capital_resource_stock_trn=H,population_persons=pop,births_persons=b,deaths_persons=d,labor_force_population_proxy=lab,
            net_migration_conditional_persons=mig,insurance_relief_trn=ss['prem'],in_kind_trn=ss['kind'],vat_social_return_trn=ss['vr'],automatic_refund_trn=refund,corporate_realized_investment=fIs,
            corporate_cash_buffer_partial=fcs,corporate_cash_change=fsrc,corporate_cash_uninvested=funi,corporate_retained_use_cumulative=rcum,corporate_tax_delta=fm['td'],corporate_credit=fm['cr'],
            corporate_induced_investment=fm['inv'],retained_used_sensitivity=fm['rel'],medical_output_vat=f.get('out'),medical_patient_vat=f.get('pat'),medical_insurer_vat=f.get('ins'),medical_initial_premium=f.get('prem'),
            medical_extra_premium=f.get('xp'),medical_public_vat=f.get('pubm'),medical_public_topup=f.get('xt'),medical_internal=f.get('xi'),medical_internal_cumulative=icum,medical_unallocated=f.get('xu'),
            medical_reform_insurer_balance=md['ib'],medical_provider_receipt=md['prov'],medical_patient_shift=md['shift'],medical_high_cost_relief=md['high'],medical_incentives=md['award'],
            palliative_saving=md['sav'],palliative_subsidy=md['pal'],hub_spend=md['hub'],extra_base_net_tax=f['en'],education_bond_gross_partial=ebond,scholarship_spend=sch,
            unmet_demand_real=un,price_pressure_proxy=pr,trigger_education=int(tg_edu),trigger_gini=None if tg_gini is None else int(tg_gini),trigger_migration=int(tg_mig),circuit_halted=int(halt))
        lastg=(Y/pY-1) if (i or oil) else 0.; pY=Y; pN=N
    return out
mx=0.; n=0; bad=[]
for s in cfg['cases']:
    o=run(s)
    for y in range(2026,2056):
        r=D[(s['id'],y)]
        for k,v in o[y].items():
            c=r[k]
            if v is None:
                if c!='': bad.append((s['id'],y,k,v,c))
                continue
            if c=='': bad.append((s['id'],y,k,v,c)); continue
            a=float(c); dd=abs(a-v)/max(1.,abs(v)); mx=max(mx,dd); n+=1
            if dd>2e-8: bad.append((s['id'],y,k,v,a))
print('cases',len(cfg['cases']),'cells compared',n,'max rel diff',mx,'mismatches',len(bad)); print(bad[:10])
