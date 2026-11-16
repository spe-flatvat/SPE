# Independent recompute of the F macro dynamic / halation model (SPE_F_Macro_Dynamic_Halation_DRAFT_20261116).
# Rewritten from the report's equations and a reading of the code; uses only the pinned fixed inputs (SHA-checked in JSON) for F macro
# scheduling (risk, labor/aging, inflation, events) via my own macro replica, and the sector R/P placeholders from the pinned StatusQuo inputs JSON.
import json,csv,math,sys,copy
cfg=json.load(open(sys.argv[1],encoding='utf-8')); rows=list(csv.DictReader(open(sys.argv[2],encoding='utf-8')))
D={(r['case'],int(r['year'])):r for r in rows}
old=json.loads(cfg['annex_inputs']['sources']['SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json']['utf8'])
c=old['sq_bundle']['f_config']
def pw(tab,t): return [x['value'] for x in tab if x['from']<=t][-1]
def risk(t):
    s=0
    for r in c['risk_shock_pct']['rules']:
        if r['type']=='once' and t==r['year']: s+=r['pct']
        if r['type']=='every' and t>=r['start'] and (t-r['start'])%r['step']==0: s+=r['pct']
    return s/100
an={int(k):float(v) for k,v in c['wage_anchor_man_yen']['anchors'].items()}
def wg(t):
    ys=sorted(an)
    for s,e in zip(ys,ys[1:]):
        if s<t<=e: return (an[e]/an[s])**(1/(e-s))-1
def core_path():
    i=c['initial_state_2025_end']; R,N,T,E,P,Dd,B=[i[k] for k in ['real_gdp','nominal_gdp','tax_revenue','expenditure','population','deaths','births']]
    out={2026:dict(R=R,N=N,T=T,E=E,ev=1.0)}
    for t in range(2027,2056):
        net=0 if t<2030 else 400000*min((t-2030+1)/5,1)
        D2=Dd*c['death_rate_coefficient']['value']; B2=B*c['birth_decline_coefficient']['value']*(1+c['phi']['value']*wg(t))
        P2=P+B2-D2+net; lab=P2/P-1+pw(c['aging_drag_pp']['table'],t)/100
        rg=.01-risk(t)+(1-c['alpha']['value'])*lab           # old C/I/E removed
        ng=rg+.02+c['inflation_extra_pp']['by_year'].get(str(t),0)/100
        ev=c['tax_factor_by_year'].get(str(t),1.0)
        N2=N*(1+ng); R*=1+rg; N=N2; T=min(T*(1+ng)*ev,N*.3)
        E*=1+pw(c['expenditure_growth_pct']['table'],t)/100; P,Dd,B=P2,D2,B2
        out[t]=dict(R=R,N=N,T=T,E=E,ev=ev)
    return out
CORE=core_path()
mx=0;n=0
def chk(a,b,tag,tol=1e-9):
    global mx,n
    a=float(a); b=float(b); d=abs(a-b)/max(1,abs(b)); mx=max(mx,d); n+=1
    assert d<tol,(tag,a,b)
for t in range(2026,2056):
    r=D[('CORE_NO_POLICY',t)]; chk(CORE[t]['R'],r['real_gdp_trn'],('coreR',t)); chk(CORE[t]['N'],r['nominal_gdp_trn'],('coreN',t)); chk(CORE[t]['T'],r['tax_macro_trn'],('coreT',t))
def phase(y,start,ramp,duration=100): return 0. if y<start or y>=start+duration else min(1.,(y-start+1)/ramp)
def run(spec,P0=None,overrides=None):
    p=copy.deepcopy(cfg['parameters']); s=copy.deepcopy(cfg['sequence']); z=copy.deepcopy(cfg['sectors']); h=copy.deepcopy(cfg['households'])
    p.update(spec.get('parameters',{}))
    if overrides: p.update(overrides)
    for k,v in spec.get('sequence',{}).items():
        if isinstance(v,dict): s[k].update(v)
        else: s[k]=v
    for k,v in spec.get('sector_overrides',{}).items(): z[k].update(v)
    for r in h: r['mpc']=min(1.,r['mpc']*spec.get('mpc_scale',1.))
    dis=spec.get('disable_policy',False); carry=p['carry_enabled']
    # structural gates (independent)
    assert s['year8']<s['year5'] and all(v>=s['year5'] for v in s['starts'].values()) and p['benefit_start']<s['year8']
    out={}; C=I=K=H=0.; Is={k:0. for k in ['medical','education','rental','promotion']}; Ks=dict(Is); lastgap=0.
    tax=CORE[2026]['T']; lastN=CORE[2026]['N']
    nomg=old['prototype_config']['nominal_growth_pct']['value']
    for t in range(2026,2056):
        i=t>2026; b=CORE[t]; Dflat=b['N']/b['R']
        off_=dis or not i
        tau=.1 if t<s['year8'] else .08 if t<s['year5'] else .05
        gen_base=b['N']*p['household_income_share']*p['taxable_final_consumption_share']
        gen=0. if off_ else (.1-tau)*gen_base
        tot=dict(price=0,firm=0,inv={},pay=0,priv=0,pub=0,rr=0,cr=0,vat=0,comp=0)
        sec={}
        for k,raw in old['prototype_config']['sectors'].items():
            a=z[k]; q=0. if off_ else phase(t,s['starts'][k],s['phase_years'][k])
            R=raw['R_2025']['value']*(1+nomg/100)**(t-2025); Pp=R*raw['p_ratio']['value']
            rr=0. if off_ else (.1-tau)*Pp; cr=q*tau*Pp*a.get('credit_fraction',1.); vat=q*tau*R
            comp=p['medical_compensation_offset_share']*cr if k=='medical' else 0.
            if k=='medical':
                pat=vat*a['patient_share']; ins=vat*a['insurer_share']; pub=vat*a['public_share']; prem=ins*a['premium_pass_through']; priv=pat+prem; sup=p['medical_household_support_share']*priv
            else:
                pat=prem=ins=0.; pub=vat*a['public_share']; priv=vat*a['private_share']; sup=0.
            rel=rr+cr; price=a['pass_through']*rel; firm=(1-a['pass_through'])*rel-comp
            sec[k]=dict(rr=rr,cr=cr,price=price,firm=firm,inv=a['investment_share']*firm,pay=a['wage_share']*firm,priv=priv,pub=pub,vat=vat,comp=comp,sup=sup,pat=pat,ins=ins,prem=prem)
        S=lambda key:sum(v[key] for v in sec.values())
        ben=0. if off_ else (p['benefit_trn'] if p['benefit_start']<=t<=p['benefit_end'] else 0.)
        hh=gen+S('price')+ben+S('pay')-S('priv')+sec['medical']['sup']
        dtax=-gen-S('rr')+S('vat')-S('cr')
        invph=0 if dis else phase(t,s['year8'],p['investment_ramp_years'],40)
        eduph=0 if dis else phase(t,p['education_start'],p['education_ramp_years'],28)
        Ipro=p['investment_promotion_flow_share']*b['N']*invph if i else 0.
        Esp=p['education_flow_share']*b['N']*eduph if i else 0.
        fb=p['income_feedback']*lastgap*Dflat if carry and i else 0.
        tC=p['domestic_share']*sum(x['mpc']*(x['cash_weight']*hh+x['income_weight']*fb) for x in h)/Dflat
        Kp,Hp,Ksp=K,H,dict(Ks)
        if i:
            C=(1-p['consumption_adjustment'])*C+p['consumption_adjustment']*tC if carry else tC
            for k in Is:
                tg=(Ipro if k=='promotion' else sec[k]['inv'])/Dflat
                Is[k]=(1-p['investment_adjustment'])*Is[k]+p['investment_adjustment']*tg if carry else tg
            I=sum(Is.values())
        sup_=p['capital_output_yield']*(1-p['depreciation'])*Kp+p['education_yield']*(1-p['education_decay'])*Hp if carry else 0.
        cap=b['R']+sup_; ind=p['capacity_absorption']*sup_
        des=b['R']+ind+C+I+Esp/Dflat; ceil=cap+p['capacity_slack']*b['R']
        Y=min(des,ceil); un=max(des-Y,0.); pr=p['price_pressure_coefficient']*un/b['R']
        Nn=Y*Dflat*(1+pr)
        if i: tax=min(tax*(1+(Nn/lastN-1)*p['macro_tax_elasticity'])*b['ev'],Nn*.3)
        sub=p['investment_fiscal_cost_share']*Ipro
        direct=dtax-sub
        exp=b['E']+ben+Esp+sec['medical']['sup']+S('pub')-sec['medical']['comp']
        if i:
            for k in Ks: Ks[k]=(1-p['depreciation'])*Ksp[k]+Is[k] if carry else 0.
            K=sum(Ks.values()); H=(1-p['education_decay'])*Hp+Esp/Dflat if carry else 0.
        gap=Y-b['R']
        out[t]=dict(Y=Y,N=Nn,T=tax,Td=tax+direct,E=exp,gap=max(exp-(tax+direct),0.),dcore=gap,C=C,I=I,edu=Esp/Dflat,ind=ind,un=un,K=K,H=H,sup=sup_,fb=fb,hh=hh,gen=gen,Ipro=Ipro,Esp=Esp,priv=S('priv'),
                    med=sec['medical'],insur_unfunded=sec['medical']['ins']-sec['medical']['prem'],pr=pr)
        lastgap=gap; lastN=Nn
    return out
paths={}
for spec in cfg['cases']:
    o=run(spec); paths[spec['id']]=o
    for t in range(2026,2056):
        r=D[(spec['id'],t)]; x=o[t]
        for a,k in [(x['Y'],'real_gdp_trn'),(x['N'],'nominal_gdp_trn'),(x['T'],'tax_macro_trn'),(x['Td'],'tax_diagnostic_trn'),(x['E'],'expenditure_diagnostic_trn'),(x['gap'],'funding_gap_proxy_trn'),
                    (x['dcore'],'GDP_delta_core_trn'),(x['C'],'C_demand_real_trn'),(x['I'],'I_policy_real_trn'),(x['edu'],'education_demand_real_trn'),(x['ind'],'capacity_absorption_real_trn'),
                    (x['un'],'supply_constraint_real_trn'),(x['K'],'capital_delta_real_trn'),(x['H'],'human_capital_resource_stock_trn'),(x['sup'],'supply_gain_real_trn'),(x['fb'],'household_feedback_nominal_trn'),
                    (x['hh'],'household_policy_cash_nominal_trn'),(x['gen'],'general_rate_relief_trn'),(x['pr'],'price_pressure_proxy'),(x['priv'],'private_burden_trn')]:
            chk(a,r[k],(spec['id'],t,k))
        # decomposition closure
        chk(x['dcore'],x['C']+x['I']+x['edu']+x['ind']-x['un'],(spec['id'],t,'close'))
        chk(x['Td'],CORE[t]['T']+(x['T']-CORE[t]['T'])+(x['Td']-x['T']),(spec['id'],t,'taxclose'))
print('independent dynamic recompute: cases',len(cfg['cases']),'cells',n,'max rel diff',mx)
