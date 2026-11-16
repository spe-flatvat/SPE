# Independent recompute of the sonzei->macro bridge. Reuses ONLY the SHA-pinned V02 sector diagnostic (already verified PASS)
# for sector-level L/VAT inputs; the macro simulator and the whole bridge are rewritten here from the formulas.
import json,csv,math,sys,types,copy,hashlib
cfg=json.load(open(sys.argv[1],encoding='utf-8')); rows=list(csv.DictReader(open(sys.argv[2],encoding='utf-8')))
idx={(r['record_type'],r['case'],int(r['year'])):r for r in rows}
S=cfg['sources']; old=json.loads(S['SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json']['utf8'])
son=types.ModuleType('son'); exec(compile(S['SPE_F_Sonzei_V02_Fixed_DRAFT_20261115.py']['utf8'],'son','exec'),son.__dict__)
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
def macro(ci_scale):
    i=c['initial_state_2025_end']; R,N,T,E,P,D,B=[i[k] for k in ['real_gdp','nominal_gdp','tax_revenue','expenditure','population','deaths','births']]
    out={2026:dict(R=R,N=N,T=T,E=E,P=P,ng=None,el=None,ev=None)}
    for t in range(2027,2056):
        net=0 if t<2030 else 400000*min((t-2030+1)/5,1)
        D2=D*c['death_rate_coefficient']['value']; B2=B*c['birth_decline_coefficient']['value']*(1+c['phi']['value']*wg(t))
        P2=P+B2-D2+net; lab=P2/P-1+pw(c['aging_drag_pp']['table'],t)/100
        cons=pw(c['policy_effects_pct']['consumption_stimulus'],t)/100*ci_scale; inv=pw(c['policy_effects_pct']['investment_promotion'],t)/100*ci_scale
        edu=pw(c['policy_effects_pct']['education'],t)/100
        rg=.01+cons+inv+edu-risk(t)+(1-c['alpha']['value'])*lab
        ng=rg+.02+c['inflation_extra_pp']['by_year'].get(str(t),0)/100
        el=pw(c['tax_elasticity']['table'],t); ev=c['tax_factor_by_year'].get(str(t),1.0)
        N2=N*(1+ng); T=min(T*(1+ng*el)*ev,N2*.3); R*=1+rg; N=N2
        E*=1+pw(c['expenditure_growth_pct']['table'],t)/100; P,D,B=P2,D2,B2
        out[t]=dict(R=R,N=N,T=T,E=E,P=P,ng=ng,el=el,ev=ev)
    return out
cases={x['id']:x['overrides'] for x in cfg['cases']}
base_co=cfg['coefficients']
off=macro(1.0)
mx=0;n=0
def chk(a,b,tag):
    global mx,n
    a=float(a); b=float(b); d=abs(a-b)/max(1,abs(b)); mx=max(mx,d); n+=1
    assert d<1e-9,(tag,a,b)
# 1. OFF baseline replica
for t in range(2026,2056):
    r=idx[('PATH','OFF_F',t)]
    chk(off[t]['R'],r['real_gdp_trn'],('off R',t)); chk(off[t]['T'],r['tax_revenue_macro_trn'],('off T',t)); chk(off[t]['E'],r['expenditure_baseline_trn'],('off E',t))
# 2. sector diagnostics (kappa override for rental), trillions
prof=son.national_profiles(old,False)
def sectors(t,co):
    L=dict(red=0,rel=0,cc=0,pub=0,dt=0)
    tot=dict(L_red=0,hh=0,biz=0,cons=0,inv=0,cvat=0,pub=0,dtax=0,Lsq=0,Lf=0,rate=0,cred=0,net=0)
    for p,b in prof:
        pol=copy.deepcopy(old['policy'])
        if p['sector']=='rental': pol['kappa']=co['rental_credit_fraction']
        d=son.diagnose(pol,p,b,t); g=lambda k:d[k]/1e12
        red=g('L_reduction'); assert abs(red-(g('L_SQ')-g('L_F')))<1e-9, 'L_red != L_SQ-L_F'
        assert abs(red-(g('L_reduction_rate_part')+g('L_reduction_credit_part')))<1e-9
        hh=co['household_pass_through']*red; biz=(1-co['household_pass_through'])*red
        net=hh-g('future_output_VAT_consumer_cost')
        tot['L_red']+=red;tot['hh']+=hh;tot['biz']+=biz;tot['net']+=net
        tot['cons']+=co['mpc']*net;tot['inv']+=co['investment_share_of_retained']*biz
        tot['cvat']+=g('future_output_VAT_consumer_cost');tot['pub']+=g('future_output_VAT_public_cost');tot['dtax']+=g('delta_tax_attribution_total')
        tot['Lsq']+=g('L_SQ');tot['Lf']+=g('L_F');tot['rate']+=g('L_reduction_rate_part');tot['cred']+=g('L_reduction_credit_part')
    return tot
for cid,ov in cases.items():
    co=dict(base_co);co.update(ov)
    adj=macro(1-co['legacy_CI_replacement_fraction'])
    ta=tb=tc=80.0; prevN=prevR=None
    for t in range(2026,2056):
        r=idx[('PATH',cid,t)]; ap=t>2026; s=sectors(t,co)
        raw=(s['cons']+s['inv'])*co['domestic_demand_share']*co['demand_multiplier'] if ap else 0.0
        defl=adj[t]['N']/adj[t]['R']; dem=raw/defl if ap else 0.0
        R=adj[t]['R']+dem; N=adj[t]['N']+raw
        elo=off[t]['el']
        if ap:
            el=elo-co['tax_elasticity_replacement_fraction']*(elo-co['tax_elasticity_without_sonzei'])
            ev=off[t]['ev']; ngA=adj[t]['ng']; ng=N/prevN-1
            ta=min(ta*(1+ngA*elo)*ev,adj[t]['N']*.3); tb=min(tb*(1+ngA*el)*ev,adj[t]['N']*.3); tc=min(tc*(1+ng*el)*ev,N*.3)
            cov=co['direct_sector_fiscal_coverage']*co['tax_elasticity_replacement_fraction']
            direct=cov*s['dtax']; pub=cov*s['pub']
        else: el=elo; direct=pub=0.0
        prevN,prevR=N,R
        E=adj[t]['E']
        chk(R,r['real_gdp_trn'],(cid,t,'R')); chk(N,r['nominal_gdp_trn'],(cid,t,'N')); chk(tc,r['tax_revenue_macro_trn'],(cid,t,'T'))
        chk(tc+direct,r['tax_revenue_plus_sector_attribution_proxy_trn'],(cid,t,'Tp')); chk(E+pub,r['expenditure_plus_output_VAT_public_proxy_trn'],(cid,t,'Ep'))
        chk(max(E+pub-tc-direct,0),r['funding_gap_with_sector_proxy_trn'],(cid,t,'gap')); chk(max(E-tc,0),r['funding_gap_macro_proxy_trn'],(cid,t,'gapm'))
        chk(dem,r['real_demand_level_trn'],(cid,t,'dem')); chk(raw,r['nominal_demand_level_trn'],(cid,t,'raw'))
        if ap:
            chk(s['cons'],r['consumption_demand_trn'],(cid,t,'cons')); chk(s['inv'],r['investment_demand_trn'],(cid,t,'inv'))
            chk(s['hh'],r['price_income_relief_trn'],(cid,t,'hh')); chk(s['biz'],r['business_retained_relief_trn'],(cid,t,'biz')); chk(s['net'],r['household_net_cash_trn'],(cid,t,'net'))
            # decomposition columns
            chk(adj[t]['R']-off[t]['R'],r['legacy_CI_GDP_adjustment_trn'],(cid,t,'dGDPci')); chk(ta-off[t]['T'],r['legacy_CI_tax_adjustment_trn'],(cid,t,'dTci'))
            chk(tb-ta,r['elasticity_tax_adjustment_trn'],(cid,t,'dTel')); chk(tc-tb,r['GDP_channel_tax_delta_trn'],(cid,t,'dTgdp'))
        # closure of decomposition vs OFF
        offT=off[t]['T']
        chk((tc+direct)-offT,(ta-offT)+(tb-ta)+(tc-tb)+direct,(cid,t,'Tclose'))
        chk(R-off[t]['R'],(adj[t]['R']-off[t]['R'])+dem,(cid,t,'Gclose'))
    # DIFFERENCE rows
    for t in range(2026,2056):
        d=idx[('DIFFERENCE',cid+'_MINUS_OFF_F',t)]; a=idx[('PATH',cid,t)]; b=idx[('PATH','OFF_F',t)]
        chk(float(d['real_gdp_trn']),float(a['real_gdp_trn'])-float(b['real_gdp_trn']),(cid,t,'diffR'))
        chk(float(d['tax_revenue_macro_trn']),float(a['tax_revenue_macro_trn'])-float(b['tax_revenue_macro_trn']),(cid,t,'diffT'))
print('independent bridge recompute: cases',len(cases),'cells',n,'max rel diff',mx)
# 3. extra: effective numbers for interpretation
m=idx; 
for cid in ['ON_MAIN','ON_ISOLATED_DEMAND_ONLY','ON_NO_CI_REPLACEMENT']:
    r=m[('PATH',cid,2055)]; o=m[('PATH','OFF_F',2055)]
    print(cid,'dGDP',round(float(r['real_gdp_trn'])-float(o['real_gdp_trn']),3),'dTmacro',round(float(r['tax_revenue_macro_trn'])-float(o['tax_revenue_macro_trn']),3),'direct',round(float(r['direct_sector_VAT_attribution_applied_trn'] or 0),3))
# sector-level 2040/2055 signs
for t in (2030,2038,2040,2055):
    s=sectors(t,base_co); print(t,{k:round(v,3) for k,v in s.items()})
