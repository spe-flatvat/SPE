# Independent recompute of the Annex-sequence bridge. Reuses only the SHA-pinned V02 sector diagnostic (previously verified)
# for sector inputs R, P_net, input_VAT_SQ/F, input_credit_F. Macro, phases, gates, demand, tax ledgers, proxies, differences rewritten here.
import json,csv,math,sys,types,copy
cfg=json.load(open(sys.argv[1],encoding='utf-8')); rows=list(csv.DictReader(open(sys.argv[2],encoding='utf-8')))
I={(r['record_type'],r['case'],int(r['year'])):r for r in rows}
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
def macro(rho):   # rho(t): fraction of C/I add-ons removed in year t
    i=c['initial_state_2025_end']; R,N,T,E,P,D,B=[i[k] for k in ['real_gdp','nominal_gdp','tax_revenue','expenditure','population','deaths','births']]
    out={2026:dict(R=R,N=N,T=T,E=E,ng=None,lam=None,ev=None)}
    for t in range(2027,2056):
        net=0 if t<2030 else 400000*min((t-2030+1)/5,1)
        D2=D*c['death_rate_coefficient']['value']; B2=B*c['birth_decline_coefficient']['value']*(1+c['phi']['value']*wg(t))
        P2=P+B2-D2+net; lab=P2/P-1+pw(c['aging_drag_pp']['table'],t)/100
        k=1-rho(t)
        rg=.01+k*pw(c['policy_effects_pct']['consumption_stimulus'],t)/100+k*pw(c['policy_effects_pct']['investment_promotion'],t)/100+pw(c['policy_effects_pct']['education'],t)/100-risk(t)+(1-c['alpha']['value'])*lab
        ng=rg+.02+c['inflation_extra_pp']['by_year'].get(str(t),0)/100
        lam=pw(c['tax_elasticity']['table'],t); ev=c['tax_factor_by_year'].get(str(t),1.0)
        N2=N*(1+ng); R*=1+rg; N=N2
        E*=1+pw(c['expenditure_growth_pct']['table'],t)/100; P,D,B=P2,D2,B2
        out[t]=dict(R=R,N=N,E=E,ng=ng,lam=lam,ev=ev)
    return out
off=macro(lambda t:0)
mx=0;n=0
def chk(a,b,tag):
    global mx,n
    a=float(a); b=float(b); d=abs(a-b)/max(1,abs(b)); mx=max(mx,d); n+=1
    assert d<1e-9,(tag,a,b)
# baseline OFF replica vs stored OFF row (and 2026 tax)
T0=old['sq_bundle']['f_config']['initial_state_2025_end']['tax_revenue']
tx=T0
for t in range(2026,2056):
    if t>2026: tx=min(tx*(1+off[t]['ng']*off[t]['lam'])*off[t]['ev'],off[t]['N']*.3)
    r=I[('PATH','OFF_F',t)]; chk(off[t]['R'],r['real_gdp_trn'],('offR',t)); chk(off[t]['N'],r['nominal_gdp_trn'],('offN',t)); chk(tx,r['tax_revenue_macro_trn'],('offT',t))
# sector inputs
Pbase={z:old['prototype_config']['sectors'][z]['R_2025']['value']*old['prototype_config']['sectors'][z]['p_ratio']['value'] for z in ['medical','education','rental']}
prof=son.national_profiles(old,False)
def sec(t,tau,starts,kap_rent):
    res={}
    for p,b in prof:
        z=p['sector']; pol=copy.deepcopy(old['policy']); pol['tax_F_points']={'2026':tau,'2055':tau}; pol['start_years'][z]=starts[z]; pol['kappa']=kap_rent if z=='rental' else 1.
        x=son.diagnose(pol,p,b,t); res[z]=x
    return res
def rate(t,s): return .10 if t<s['year8'] else .08 if t<s['year5'] else .05
def phase(t,s,z): return max(0.,min(1.,(t-s['sector_starts'][z]+1)/s['phase_years'][z]))
paths={}
for spec in cfg['cases']:
    s=copy.deepcopy(cfg['schedule']); co=dict(cfg['coefficients'])
    for k,v in spec.get('schedule',{}).items():
        if isinstance(v,dict): s[k].update(v)
        else: s[k]=v
    co.update(spec.get('coefficients',{}))
    # rule checks (independent): gates
    assert s['year8']<s['year5'] and all(s['sector_starts'][z]>=s['year5'] for z in Pbase), spec['id']
    # pass 1: per-year flows & weights
    fl={}
    for t in range(2026,2056):
        tau=rate(t,s); X=sec(t,tau,s['sector_starts'],co['rental_credit_fraction'])
        d=dict(rr=0,cc=0,cvat=0,out=0,pub=0)
        for z,x in X.items():
            q=phase(t,s,z); R=x['R']/1e12; rr=(x['input_VAT_SQ']-x['input_VAT_F'])/1e12; cc=q*x['input_credit_F']/1e12
            out=q*tau*R; pub=old['policy']['phi'][z]*out; priv=out-pub
            th=co['household_pass_through']
            d['rr']+=rr; d['cc']+=cc; d['out']+=out; d['pub']+=pub; d['cvat']+=priv
            d.setdefault('Crate',0); d['Crate']+=co['mpc']*th*rr; d.setdefault('Irate',0); d['Irate']+=co['investment_share']*(1-th)*rr
            d.setdefault('Ccred',0); d['Ccred']+=co['mpc']*th*cc; d.setdefault('Icred',0); d['Icred']+=co['investment_share']*(1-th)*cc
            d.setdefault('Cburd',0); d['Cburd']+=-co['mpc']*priv
            d.setdefault('ratetax',0); d['ratetax']+=-rr; d.setdefault('basetax',0); d['basetax']+=out-cc
            # gate check: nothing before start
            if t<s['sector_starts'][z]: assert q==0 and cc==0 and out==0,(spec['id'],t,z)
            if t<s['year5']: assert cc==0 and out==0
        w=sum(Pbase[z]*phase(t,s,z)*(co['rental_credit_fraction'] if z=='rental' else 1.) for z in Pbase)/sum(Pbase.values())
        d['w']=w; d['ben']=s['benefit_trn'] if s['benefit_start']<=t<=s['benefit_end'] else 0.
        fl[t]=d
    rho=lambda t:co['legacy_CI_overlap']*fl[t]['w']
    adj=macro(rho)
    taxCI=taxE=taxN=T0; lastN=600.0 if False else old['sq_bundle']['f_config']['initial_state_2025_end']['nominal_gdp']
    P={}
    for t in range(2026,2056):
        ap=t>2026; d=fl[t]; lam=off[t]['lam'] if ap else None
        eff=None
        if ap:
            erho=co['elasticity_overlap']*d['w']; eff=lam-erho*(lam-co['elasticity_anchor'])
            taxCI=min(taxCI*(1+adj[t]['ng']*lam)*off[t]['ev'],adj[t]['N']*.3); taxE=min(taxE*(1+adj[t]['ng']*eff)*off[t]['ev'],adj[t]['N']*.3)
        f=co['domestic_share']*co['multiplier']
        ns={'benefit':f*co['mpc']*d['ben']*(1-co['benefit_already_in_legacy_share']),'rate':f*(d['Crate']+d['Irate']),'credit':f*(d['Ccred']+d['Icred']),'burden':f*d['Cburd']}
        if not ap: ns={k:0. for k in ns}
        D=adj[t]['N']/adj[t]['R']; re={k:v/D for k,v in ns.items()}
        real=adj[t]['R']+sum(re.values()); nom=adj[t]['N']+sum(ns.values())
        if ap: taxN=min(taxN*(1+(nom/lastN-1)*eff)*off[t]['ev'],nom*.3)
        else: taxN=T0
        dt=co['direct_fiscal_inclusion']*(d['ratetax']+d['basetax']) if ap else 0.; pc=co['direct_fiscal_inclusion']*d['pub'] if ap else 0.
        bene=d['ben'] if ap else 0.
        tp=taxN+dt; ep=adj[t]['E']+pc+bene
        r=I[('PATH',spec['id'],t)]
        chk(real,r['real_gdp_trn'],(spec['id'],t,'R')); chk(nom,r['nominal_gdp_trn'],(spec['id'],t,'N')); chk(taxN,r['tax_revenue_macro_trn'],(spec['id'],t,'T'))
        chk(tp,r['tax_plus_diagnostic_trn'],(spec['id'],t,'tp')); chk(ep,r['expenditure_plus_diagnostic_trn'],(spec['id'],t,'ep')); chk(max(ep-tp,0),r['funding_gap_proxy_trn'],(spec['id'],t,'gap'))
        chk(real-off[t]['R'],r['real_gdp_delta_trn'],(spec['id'],t,'dR'))
        chk(adj[t]['R']-off[t]['R'],r['GDP_CI_adjustment_trn'],(spec['id'],t,'ciG'))
        for k,kk in [('benefit','GDP_benefit_trn'),('rate','GDP_rate_partial_trn'),('credit','GDP_credit_trn'),('burden','GDP_private_burden_trn')]: chk(re[k],r[kk],(spec['id'],t,kk))
        # tax decomposition
        tOFF=[I[('PATH','OFF_F',t)]][0]['tax_revenue_macro_trn']
        chk(taxN-float(tOFF),r['tax_macro_delta_trn'],(spec['id'],t,'dT'))
        if ap: chk(taxCI-float(tOFF),r['tax_CI_adjustment_trn'],(spec['id'],t,'tCI')); chk(taxE-taxCI,r['tax_elasticity_adjustment_trn'],(spec['id'],t,'tE')); chk(taxN-taxE,r['tax_GDP_channel_trn'],(spec['id'],t,'tG'))
        chk(rate(t,s),r['standard_tax_rate'],(spec['id'],t,'rate'))
        for z in Pbase: chk(phase(t,s,z),r[z+'_phase'],(spec['id'],t,z))
        chk(rho(t),r['CI_fraction_applied'],(spec['id'],t,'rho'))
        # closure
        chk(real-off[t]['R'],(adj[t]['R']-off[t]['R'])+sum(re.values()),(spec['id'],t,'Gclose'))
        lastN=nom; P[t]=(real,taxN,tp,ep)
    paths[spec['id']]=P
    # DIFFERENCE rows
    for t in range(2026,2056):
        d=I[('DIFFERENCE',spec['id']+'_MINUS_OFF_F',t)]; o=I[('PATH','OFF_F',t)]
        chk(d['real_gdp_trn'],P[t][0]-float(o['real_gdp_trn']),(spec['id'],t,'dif')); chk(d['tax_revenue_macro_trn'],P[t][1]-float(o['tax_revenue_macro_trn']),(spec['id'],t,'difT'))
print('independent Annex recompute: cases',len(cfg['cases']),'cells',n,'max rel diff',mx)
# --- findings support
G=lambda cid,t:paths[cid][t][0]-off[t]['R']
print('\nGDP delta by year (ON-OFF), 兆円')
ids=['ANNEX_BASE','SIMULTANEOUS','DELAYED','TIMING_EARLY','TIMING_LATE','PHASE_3','BENEFIT_NOT_IN_LEGACY','OVERLAP_25']
print('year',*ids)
for t in [2027,2029,2030,2033,2034,2035,2036,2037,2038,2039,2040,2041,2042,2045,2050,2055]:
    print(t,*['%+.3f'%G(i,t) for i in ids])
print('\n2055 GDP level identical across timing cases? ',{i:round(paths[i][2055][0],9) for i in ['ANNEX_BASE','SIMULTANEOUS','DELAYED','TIMING_EARLY','TIMING_LATE','PHASE_3','NO_BENEFIT','DOUBLE_BENEFIT','BENEFIT_NOT_IN_LEGACY']})
print('\ncumulative 2026-2055 GDP diff vs OFF (兆円) and tax(macro) diff:')
for i in ['ANNEX_BASE','SIMULTANEOUS','DELAYED','TIMING_EARLY','TIMING_LATE','PHASE_3','BENEFIT_NOT_IN_LEGACY','OVERLAP_25','OVERLAP_50']:
    cg=sum(G(i,t) for t in range(2026,2056)); ct=sum(paths[i][t][1]-float(I[('PATH','OFF_F',t)]['tax_revenue_macro_trn']) for t in range(2026,2056))
    print('%-24s GDP %+9.3f  tax %+9.3f'%(i,cg,ct))
# structural proof: level-only => 2055 GDP depends only on 2055 flows
