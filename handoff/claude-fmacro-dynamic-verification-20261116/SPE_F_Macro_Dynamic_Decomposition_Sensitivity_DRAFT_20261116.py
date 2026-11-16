# usage: python3 -I THIS.py INPUTS.json COMPARISON.csv   (the independent recompute script must sit in the same directory)
import sys,copy,json,os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'SPE_F_Macro_Dynamic_Independent_Recalc_DRAFT_20261116.py')).read())
# 1. legacy -> core sequential removal (own macro replica with per-add-on scales)
def legacy_macro(sc,se,si):
    i=c['initial_state_2025_end']; R,N,Pp,Dd,B=[i[k] for k in ['real_gdp','nominal_gdp','population','deaths','births']]
    for t in range(2027,2056):
        net=0 if t<2030 else 400000*min((t-2030+1)/5,1)
        D2=Dd*c['death_rate_coefficient']['value']; B2=B*c['birth_decline_coefficient']['value']*(1+c['phi']['value']*wg(t))
        P2=Pp+B2-D2+net; lab=P2/Pp-1+pw(c['aging_drag_pp']['table'],t)/100
        rg=.01+sc*pw(c['policy_effects_pct']['consumption_stimulus'],t)/100+si*pw(c['policy_effects_pct']['investment_promotion'],t)/100+se*pw(c['policy_effects_pct']['education'],t)/100-risk(t)+(1-c['alpha']['value'])*lab
        R*=1+rg; Pp,Dd,B=P2,D2,B2
    return R
full=legacy_macro(1,1,1); print('legacy F 2055 real GDP',round(full,3))
orders={'消費→投資→教育':[(0,1,1),(0,1,0),(0,0,0)],'教育→投資→消費':[(1,0,1),(1,0,0),(0,0,0)],'投資→教育→消費':[(1,1,0),(1,0,0),(0,0,0)]}
# fix scale tuple order: (consumption, education, investment)
seqs={'消費→教育→投資':[(0,1,1),(0,0,1),(0,0,0)],'投資→教育→消費':[(1,1,0),(1,0,0),(0,0,0)],'教育→投資→消費':[(1,0,1),(1,0,0),(0,0,0)]}
names={'消費→教育→投資':['消費刺激','教育','投資促進'],'投資→教育→消費':['投資促進','教育','消費刺激'],'教育→投資→消費':['教育','投資促進','消費刺激']}
for k,v in seqs.items():
    prev=full; line=[]
    for (a,b,cc),nm in zip(v,names[k]):
        cur=legacy_macro(a,b,cc); line.append(f'{nm} {cur-prev:+.1f}'); prev=cur
    print(k,' | '.join(line),'| core',round(prev,3))
core2055=CORE[2055]['R']; base=paths['DYNAMIC_BASE'][2055]['Y']
print('\nCORE 2055',round(core2055,3),'DYNAMIC_BASE',round(base,3),'policy part',round(base-core2055,3))
# 2. dynamic: one-at-a-time removals (own implementation)
def y55(over=None,spec=None,field='Y'):
    o=run(spec or {},overrides=over)[2055]; return o[field]
def rep(label,over=None,spec=None):
    o=run(spec or {},overrides=over)[2055]; print(f'{label:46s} Y {o["Y"]:8.3f} (vs CORE {o["Y"]-core2055:+7.3f})  gap {o["gap"]:7.2f}  K {o["K"]:6.2f}  Td {o["Td"]:7.2f}')
print('\n-- one-at-a-time removals, 2055 --')
rep('DYNAMIC_BASE')
rep('一般減税なし(taxable share=0)',{'taxable_final_consumption_share':0.})
rep('投資促進フローなし',{'investment_promotion_flow_share':0.})
rep('教育フローなし',{'education_flow_share':0.})
rep('給付なし',{'benefit_trn':0.})
rep('所得フィードバックなし',{'income_feedback':0.})
rep('供給誘発吸収なし',{'capacity_absorption':0.})
rep('資本繰越なし(carry off)',{'carry_enabled':False,'income_feedback':0.})
rep('投資+教育+一般減税すべてなし',{'investment_promotion_flow_share':0.,'education_flow_share':0.,'taxable_final_consumption_share':0.})
print('\n-- structural sensitivity (not fitted), 2055 --')
for lab,ov in [('投資フロー×2(.008)',{'investment_promotion_flow_share':.008}),('投資フロー×5(.02)',{'investment_promotion_flow_share':.02}),('投資フロー×10(.04)',{'investment_promotion_flow_share':.04}),
               ('教育フロー×5(.015)',{'education_flow_share':.015}),('教育フロー×10(.03)',{'education_flow_share':.03}),
               ('資本収率×2(.2)',{'capital_output_yield':.2}),('教育収率×2(.12)',{'education_yield':.12}),('吸収率1.0',{'capacity_absorption':1.0}),
               ('投資×10+収率×2+吸収1.0',{'investment_promotion_flow_share':.04,'capital_output_yield':.2,'capacity_absorption':1.0}),
               ('投資×10+教育×10+収率×2+吸収1.0',{'investment_promotion_flow_share':.04,'education_flow_share':.03,'capital_output_yield':.2,'education_yield':.12,'capacity_absorption':1.0}),
               ('一般減税ベース×0.5(.25→.25 share)',{'taxable_final_consumption_share':.25}),('一般減税ベース×2',{'taxable_final_consumption_share':1.0}),
               ('所得FB .08→.3',{'income_feedback':.3}),('MPC各×? 消費調整.6→.3',{'consumption_adjustment':.3})]:
    rep(lab,ov)
print('\n-- funding gap path (DYNAMIC_BASE / CORE / legacy) --')
for t in (2030,2035,2045,2055):
    print(t,'dyn gap',round(paths['DYNAMIC_BASE'][t]['gap'],1),'core gap',round(max(CORE[t]['E']-CORE[t]['T'],0),1),'legacy gap',D[('LEGACY_OFF',t)]['funding_gap_proxy_trn'][:6],'exp',round(paths['DYNAMIC_BASE'][t]['E'],1),'taxdiag',round(paths['DYNAMIC_BASE'][t]['Td'],1))
print('\n-- medical 2055 (DYNAMIC_BASE) --')
m=paths['DYNAMIC_BASE'][2055]['med']; vat=m['vat']; print({k:round(v,4) for k,v in m.items()})
print('vat',round(vat,4),'patient+premium+public',round(m['pat']+m['prem']+m['pub'],4),'unaccounted insurer share',round(vat-(m['pat']+m['prem']+m['pub']),4),'= insurer*(1-pt)',round(m['ins']-m['prem'],4))
print('implied P_medical',round(m['cr']/.05,3),'R',round(vat/.05,3))
# 3. timing cases
print('\n-- timing 2055 (Y) --',{k:round(paths[k][2055]['Y'],3) for k in ['DYNAMIC_BASE','SIMULTANEOUS','DELAYED','EARLY_5PCT','LATE_5PCT','NO_CARRY','CAPACITY_TIGHT']})
# 4. structural identities
for t in (2035,2055):
    o=paths['DYNAMIC_BASE'][t]; print(t,'C',round(o['C'],3),'I',round(o['I'],3),'edu',round(o['edu'],3),'ind',round(o['ind'],3),'sum',round(o['C']+o['I']+o['edu']+o['ind'],3))

# 5. employment / wage index proxies (independent recompute of the two proxy columns)
def pop_path():
    i=c['initial_state_2025_end']; P,Dd,B=i['population'],i['deaths'],i['births']; out={2026:P}
    for t in range(2027,2056):
        net=0 if t<2030 else 400000*min((t-2030+1)/5,1)
        D2=Dd*c['death_rate_coefficient']['value']; B2=B*c['birth_decline_coefficient']['value']*(1+c['phi']['value']*wg(t)); P=P+B2-D2+net; Dd,B=D2,B2; out[t]=P
    return out
pp=pop_path()
def wage(t):
    ys=sorted(an)
    for s,e in zip(ys,ys[1:]):
        if s<=t<=e: return an[s]*(an[e]/an[s])**((t-s)/(e-s))
w0=wage(2026); m=0
for cid in ['DYNAMIC_BASE','CAPACITY_TIGHT','CORE_NO_POLICY']:
    for t in range(2026,2056):
        r=D[(cid,t)]; g=paths[cid][t]['dcore']; R=CORE[t]['R']
        emp=100*pp[t]/pp[2026]*(1+cfg['parameters']['employment_elasticity']*g/R); wi=100*wage(t)/w0*(1+cfg['parameters']['wage_elasticity']*g/R)
        m=max(m,abs(emp-float(r['employment_index_proxy']))/emp,abs(wi-float(r['wage_index_proxy']))/wi)
print('\nemployment/wage index proxy max rel diff',m)
b=paths['DYNAMIC_BASE'][2055]; print('2055 dyn tax_diag/N %.2f%%  exp/N %.2f%%'%(b['Td']/b['N']*100,b['E']/b['N']*100))
