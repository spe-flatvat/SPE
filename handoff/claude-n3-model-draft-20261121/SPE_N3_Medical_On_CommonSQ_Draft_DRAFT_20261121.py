#!/usr/bin/env python3
"""N3 medical-reform draft on the fixed common StatusQuo engine (DRAFT / NON-CANONICAL).

What this is: the N3 policy text's medical-burden rules (staged coinsurance up to 50%,
tighter high-cost-care caps) injected into the *existing* F/common engine chain
(fixed Commit ff621006...) through the same `Medical` interface that CommonBaseline.py
uses for the StatusQuo path. The common end-of-life module is called unchanged
(set-independent); N3 supplies only its own claim rule.
Also (EXPERIMENTAL, UNVERIFIED beyond the engine's own identities): the N3 consumption-tax
path (10% -> reduced rate abolished 2030 -> 12/15/18/20%) is fed into the engine's existing
VAT price-pass-through channel by replacing the StatusQuo rate function; a "freeze at 2035"
variant is included. No N3-specific growth shock, 3-band flat tax, pension (75), EITC abolition,
public-sector regularization, corporate incentive or co-op blocks are modeled here.
All N3 numeric inputs below are UNCALIBRATED candidates, not adopted policy values.

usage: python3 THIS.py <tree_root_of_ff621006> <outdir>
(reads the fixed tree; writes ONLY to <outdir>; never writes into the tree)
"""
import sys,json,math,csv
from pathlib import Path
sys.dont_write_bytecode=True
tree=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
F=tree/'handoff/f-common-endoflife-finalization-20261121'
sys.path.insert(0,str(F))
import Model as M          # fixed: load(), read(), dump()
import FMedical as FM      # fixed: Medical, patient_claim

c=json.loads((F/'Inputs.json').read_text())
root,edu,ec,integ,v,vc=M.load(c)
fixed=[r for r in M.read(F.parent/'f-education-20261121/Annual.csv') if r['case']=='SQ_FIXED']
defs=[float(r['common_deflator']) for r in fixed];pops=[float(r['population']) for r in fixed]

# ---- N3 claim rule (candidate inputs; see N3_Inputs JSON) -------------------------
N3={'coinsurance':0.5,'scope':'ALL_AGES'}   # scope: ALL_AGES | ONLY_CURRENT_30 (原文は年齢範囲を規定せず)
_orig_claim=FM.patient_claim
def n3_claim(age,group,profile,regime,uniform=False,cap_multiplier=1.):
    """Same statutory structure as F's illustrative claim engine; only the coinsurance
    rate of the 'uniform' reform branch differs (N3 candidate: all ages at N3['coinsurance'])."""
    if not uniform:return _orig_claim(age,group,profile,regime,False,cap_multiplier)
    # re-implement uniform branch with N3 rate (copy of F structure, coins replaced)
    elderly=age in ['AGE70_74','AGE75PLUS'];bill=profile['bill_yen'];months=profile['months'];coins=N3['coinsurance']
    if N3['scope']=='ONLY_CURRENT_30':
        # raise only the groups whose current statutory rate is 30%; keep the 10/20% tiers
        cur=.2 if age=='PRESCHOOL' else ((.2 if age=='AGE70_74' else .1) if (elderly and group in ['TAXFREE','GENERAL']) else .3)
        coins=coins if abs(cur-.3)<1e-12 else cur
    old=regime=='PRE2026AUG'
    if group=='TAXFREE':cap=(24600 if old else 25700) if elderly else (35400 if old else 36900);multi=24600;annual=math.inf if old else 290000
    elif group=='GENERAL':cap=57600 if old else 61500;multi=34500 if regime=='POST2027AUG' else 44400;annual=math.inf if old else 410000
    elif group=='MIDDLE':cap=(80100+max(0.,bill-267000)*.01) if old else (85800+max(0.,bill-286000)*.01);multi=44400;annual=math.inf if old else 530000
    else:cap=(167400+max(0.,bill-558000)*.01) if old else (179100+max(0.,bill-597000)*.01);multi=93000;annual=math.inf if old else 1110000
    cap*=cap_multiplier;multi*=cap_multiplier;annual*=cap_multiplier
    paid=sum(min(bill*coins,cap if i<3 else multi) for i in range(months))
    return min(paid,annual)

# --- self-test: with coinsurance 0.3 / ALL_AGES the N3 branch must equal F's uniform-30 branch exactly
def selftest():
    N3.update(coinsurance=.3,scope='ALL_AGES');n=0;mx=0.
    for age in ['PRESCHOOL','AGE6_69','AGE70_74','AGE75PLUS']:
        for g in c['income_weights']:
            for pr in c['claim_profiles']:
                for rg in ['PRE2026AUG','POST2026AUG','POST2027AUG']:
                    for cm in (1.,.9,1.1):
                        a=_orig_claim(age,g,dict(pr),rg,True,cm);b=n3_claim(age,g,dict(pr),rg,True,cm);mx=max(mx,abs(a-b));n+=1
                        assert n3_claim(age,g,dict(pr),rg,False,cm)==_orig_claim(age,g,dict(pr),rg,False,cm)
    return dict(tests=n,max_abs_diff_yen=mx)
FM.patient_claim=n3_claim
ST=selftest();assert ST['max_abs_diff_yen']==0.
(out/'N3_Selftest.json').write_text(json.dumps(ST)+'\n')

def n3_vat(y,freeze=False):
    """Candidate reading of the N3 text: standard 10% until 2031; reduced (food) rate abolished from 2030;
    12% 2032, 15% 2034, 18% 2038, 20% 2040. freeze=True holds the 2035 level (15%) afterwards
    (the 2035 automatic-freeze trigger has no numeric condition in the text; here it is a switch)."""
    yy=min(y,2035) if freeze and y>=2035 else y
    std=.1 if yy<2032 else .12 if yy<2034 else .15 if yy<2038 else .18 if yy<2040 else .2
    food=.08 if y<2030 else std
    return std,food
_orig_sq_rates=v.sq_rates
CASES=[ # id, common, copay(N3 rule on), rate, cap_change, cap_mode, start, ramp, scope
 ('SQ_COMMON_OFF',False,False,.3,.0,'PATIENT_CAP_DOWN',2033,6,'ALL_AGES',None),
 ('SQ_COMMON_ON',True,False,.3,.0,'PATIENT_CAP_DOWN',2033,6,'ALL_AGES',None),
 ('N3_MED_50_CAP_SAME',True,True,.5,.0,'PATIENT_CAP_DOWN',2033,6,'ALL_AGES',None),        # reference candidate
 ('N3_MED_50_CAP_UP10',True,True,.5,.1,'PATIENT_CAP_UP',2033,6,'ALL_AGES',None),          # reading A: benefit tightened (patient caps +10%)
 ('N3_MED_50_CAP_DOWN10',True,True,.5,.1,'PATIENT_CAP_DOWN',2033,6,'ALL_AGES',None),      # reading B: cap amount itself reduced (-10%)
 ('N3_MED_50_COMMON_OFF',False,True,.5,.0,'PATIENT_CAP_DOWN',2033,6,'ALL_AGES',None),
 ('N3_MED_40_CAP_SAME',True,True,.4,.0,'PATIENT_CAP_DOWN',2033,6,'ALL_AGES',None),
 ('N3_MED_50_ONLY_CURRENT_30',True,True,.5,.0,'PATIENT_CAP_DOWN',2033,6,'ONLY_CURRENT_30',None),
 ('N3_MED_50_START2030',True,True,.5,.0,'PATIENT_CAP_DOWN',2030,6,'ALL_AGES',None),
 ('N3_MED_50_FAST3Y',True,True,.5,.0,'PATIENT_CAP_DOWN',2033,3,'ALL_AGES',None),
 ('F_RULE_ON_SQ_30_CAP_DOWN10',True,True,.3,.1,'PATIENT_CAP_DOWN',2028,8,'ALL_AGES',None), # F's own medical rule on SQ: comparison control
 ('N3_VAT_PATH_ONLY',True,False,.3,.0,'PATIENT_CAP_DOWN',2033,6,'ALL_AGES','PATH'),            # EXPERIMENTAL VAT connection
 ('N3_VAT_FREEZE2035_ONLY',True,False,.3,.0,'PATIENT_CAP_DOWN',2033,6,'ALL_AGES','FREEZE2035'),
 ('N3_VAT_PATH_PLUS_MED_50',True,True,.5,.0,'PATIENT_CAP_DOWN',2033,6,'ALL_AGES','PATH'),
]
KEYS=['standard_rate','food_rate','modeled_VAT_trn','VAT_delta_vs_fixed_reference_trn','household_direct_price_benefit_trn','real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','consolidated_partial_balance_proxy_trn','macro_cash_DI_proxy_trn']
MK=['baseline_medical_bill_trn','baseline_patient_model_trn','reform_medical_bill_before_common_trn','patient_static_transfer_trn','demand_volume_cost_delta_trn','necessary_care_foregone_cost_proxy_trn','clinical_cost_delta_trn','patient_payment_delta_trn','public_clinical_payment_delta_trn','insurer_clinical_payment_delta_trn','household_cash_delta_trn','government_cost_delta_trn','insurer_balance_delta_trn','medical_financing_tax_trn','medical_financing_premium_trn','medical_other_spending_crowded_trn','medical_policy_debt_issue_trn','health_effective_labor_added','medical_unassigned_direct_cash_requirement_trn','financing_account_status']
CK=['clinical_demand_episodes','transition_need','chosen_transitions','transition_unmet','transition_capacity','universal_palliative_need','universal_palliative_served','universal_palliative_unmet','universal_access_probability','resource_units_used','patient_payment_delta_trn','household_direct_cash_burden_delta_trn','total_resource_cost_delta_trn','registration_changes_benefits','registration_changes_copay','registration_changes_palliative_priority','treatment_automatically_stopped','unknown_wish_assumed_refusal','active_life_termination']

annual=[];common_rows=[]
for cid,common,copay,rate,capchg,capmode,start,ramp,scope,vat in CASES:
    N3['coinsurance']=rate;N3['scope']=scope
    v.sq_rates=(lambda y,s_:n3_vat(y,False)) if vat=='PATH' else (lambda y,s_:n3_vat(y,True)) if vat=='FREEZE2035' else _orig_sq_rates
    s={**c['defaults'],'id':cid,'common':common,'copay':copay,'provider':False,'uniform_thirty':True,'cap_change':capchg,'cap_mode':capmode,'start_year':start,'ramp_years':ramp}
    md=FM.Medical(c,s,defs,pops);orig=integ.make_base
    def base(*a,_md=md,**kw):
        r=orig(*a,**kw);_md.trajectory=r[3]['d'];_md.elder=r[3]['elder'];return r
    integ.make_base=base
    def hook(engine,pol,_md=md):
        assert pol=='SQ'
        source=engine['_integration_source'];ns=dict(engine['run_path'].__globals__);ns['_medical']=_md
        def sub(a,b):
            nonlocal source
            assert source.count(a)==1,a;source=source.replace(a,b)
        sub("t=c['_trajectory'][i];sq=c['_common_trajectory'][i]","t=c['_trajectory'][i];sq=c['_common_trajectory'][i]\n        w=_medical.step(y)")
        sub("invest_nom=value(invflow)+value(firm['investment'])+f['investment']+value(med['hubs'])","invest_nom=value(invflow)+value(firm['investment'])+f['investment']+value(med['hubs'])+w['investment_nominal_delta_trn']")
        sub("cash+=_pension[i]['household_cash_delta_trn']","cash+=_pension[i]['household_cash_delta_trn']+w['household_cash_delta_trn']")
        sub("desired=coreY+p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite","desired=coreY+p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+w['service_production_nominal_delta_trn']/coreD")
        source=source.replace("p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite-unmet)","p['capacity_absorption']*supply+C+I+education_nom/coreD+education_level+finite+w['service_production_nominal_delta_trn']/coreD-unmet)")
        sub("taxdiag=tax+direct;","direct+=w['medical_financing_direct_tax_trn'];expenditure+=w['government_cost_delta_trn']\n        taxdiag=tax+direct;")
        sub("if not enabled:req(close(cash,f['household']) and close(direct,f['direct_tax']) and close(invest_nom,f['investment']) and close(education_nom,0.),'StatusQuo VAT-only changes; no other F channels')","if not enabled:req(close(cash,f['household']+w['household_cash_delta_trn']) and close(direct,f['direct_tax']+w['medical_financing_direct_tax_trn']) and close(invest_nom,f['investment']+w['investment_nominal_delta_trn']) and close(education_nom,0.),'SQ only VAT reference and explicit common/N3 medical flows')")
        exec(compile(source,'n3_medical_on_SQ_adapter.py','exec'),ns);return ns
    integ._education_hook=hook
    try:rows,inc,sec,b,raw,cc=integ.execute(v,vc,dict(id=cid,policy='SQ',E=False,F=False,PEN=False,VAT=False,A=False,B=False,C=False))
    finally:integ.make_base=orig;v.sq_rates=_orig_sq_rates
    for r,w,co in zip(rows,md.rows,md.common):
        a=dict(case=cid,year=r['year'],coinsurance_candidate=rate if copay else None,cap_mode_candidate=capmode if copay else None,age_scope_candidate=scope if copay else None,vat_path_candidate=vat,cap_change_candidate=capchg if copay else None,start_year=start,ramp_years=ramp,common_policy=common,n3_copay_rule=copay)
        a.update({k:r.get(k) for k in KEYS});a.update({k:w.get(k) for k in MK});annual.append(a)
        common_rows.append(dict(case=cid,year=r['year'],**{k:co.get(k) for k in CK}))
    print('done',cid,flush=True)
M.dump(out/'N3_Medical_Annual.csv',annual);M.dump(out/'N3_Medical_Common.csv',common_rows)
# comparison vs SQ_COMMON_ON (same common module state) for N3 cases
by={(r['case'],r['year']):r for r in annual};cmp=[]
for cid,*_ in CASES:
    for y in range(2026,2056):
        r=by[cid,y];ref=by['SQ_COMMON_ON',y]
        d=dict(case=cid,year=y)
        for k in KEYS+['patient_payment_delta_trn','household_cash_delta_trn','government_cost_delta_trn','necessary_care_foregone_cost_proxy_trn','demand_volume_cost_delta_trn']:
            d[k+'_minus_SQ_COMMON_ON']=(r[k]-ref[k]) if isinstance(r[k],(int,float)) and isinstance(ref[k],(int,float)) else None
        cmp.append(d)
M.dump(out/'N3_Medical_vs_SQ_Common_On.csv',cmp)
print('COMPLETE',len(annual))
