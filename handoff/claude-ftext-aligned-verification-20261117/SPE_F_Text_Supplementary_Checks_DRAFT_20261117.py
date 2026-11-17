# Supplementary checks for the F-text verification. Usage: python3 -I analysis_text.py <Inputs JSON> <new CSV>
import sys,runpy,io,contextlib,json,copy,csv,os
here=os.path.dirname(os.path.abspath(__file__)); j,cv=sys.argv[1],sys.argv[2]
OLDJ=sys.argv[3] if len(sys.argv)>3 else None   # optional: DM04_DM05 Inputs JSON (30b926dd)
OLDC=sys.argv[4] if len(sys.argv)>4 else None   # optional: DM04_DM05 Annual_Comparison CSV (30b926dd)
sys.argv=['x',j,cv]
buf=io.StringIO()
with contextlib.redirect_stdout(buf): G=runpy.run_path(os.path.join(here,'SPE_F_Text_Independent_Recalc_DRAFT_20261117.py'))
run=G['run']; cfg=G['cfg']; D=G['D']; A=G['A']
print(buf.getvalue().strip())
cs={s['id']:s for s in cfg['cases']}
def sp(**ov): 
    s=copy.deepcopy(cs['TEXT_KNOWN_PARTIAL']); s['overrides'].update(ov); return s
# 1 baseline (no-policy) path of the new model: GDP with all policy channels off ~ TEXT_KNOWN_PARTIAL minus known flows. Use omit all channels and no migration.
allomit=['food','social','firm','medical','hubs','triggers','extra']
def y55(s): o=run(s); return o[2055]['real_gdp_trn'],o[2055]['expenditure_diagnostic_trn'],o[2055]['tax_diagnostic_trn'],o[2055]['population_persons']
print('TEXT_KNOWN_PARTIAL 2055 gdp/E/Tdiag/pop',y55(cs['TEXT_KNOWN_PARTIAL']))
s=copy.deepcopy(cs['TEXT_KNOWN_PARTIAL']); s['omit']=allomit; print('  all channels omitted',y55(s))
print('  migration 0',y55(sp(migration_annual=0.)))
print('  elasticity 1.0',y55(sp(elasticity=1.0)))
# 2 expenditure baseline: new constant 2.5% vs old table (old CORE_NO_POLICY expenditure from stored reference)
for y in (2030,2035,2045,2055):
    o=run(cs['TEXT_KNOWN_PARTIAL'])[y]['expenditure_diagnostic_trn']; oc=float(D[('OLD_CORE_NO_POLICY',y)]['expenditure_diagnostic_trn'])
    print('E',y,'new',round(o,3),'oldCORE',round(oc,3),'108*1.025^i',round(108*1.025**(y-2026),3))
# 3 migration vs 3-5% population-share goal (Annex5): implied foreign stock share
for nm in ('TEXT_KNOWN_PARTIAL','ILLUSTRATIVE_ALL','NO_LABOR_MIGRATION_PACKAGE'):
    p=copy.deepcopy(cfg['parameters']); p.update(cs[nm].get('overrides',{}))
    o=run(cs[nm]); cum=0
    mig=[o[y]['net_migration_conditional_persons'] for y in range(2026,2056)]
    f0=p['foreign_stock_2026'] if p['foreign_stock_2026'] is not None else 0
    stock=f0+sum(mig); print(nm,'cum net migrants 2030-55',round(sum(mig)),'stock(if initial',f0,')',round(stock),'share of 2055 pop',round(stock/o[2055]['population_persons'],3))
# 4 hard-coded coefficients not in parameters
import re
# 5 DM-04 / DM-05 identities in new paths
mx=0
for nm in ('ILLUSTRATIVE_ALL','ILLUSTRATIVE_PREMIUM','ILLUSTRATIVE_PUBLIC','ILLUSTRATIVE_INTERNAL'):
    for y in range(2026,2056):
        r=D[(nm,y)]; g=lambda k:float(r[k] or 0)
        mx=max(mx,abs(g('medical_output_vat')-g('medical_patient_vat')-g('medical_initial_premium')-g('medical_extra_premium')-g('medical_public_vat')-g('medical_internal')-g('medical_unallocated')))
print('DM-04 final-payer identity max resid (CSV, 10sig):',mx)
b=run(cs['ILLUSTRATIVE_ALL']); pu=run(cs['ILLUSTRATIVE_PUBLIC']); pr=run(cs['ILLUSTRATIVE_PREMIUM']); it=run(cs['ILLUSTRATIVE_INTERNAL'])
for y in (2038,2045,2055):
    print(y,'dGDP prem/pub/int',round(pr[y]['real_gdp_trn']-b[y]['real_gdp_trn'],6),round(pu[y]['real_gdp_trn']-b[y]['real_gdp_trn'],6),round(it[y]['real_gdp_trn']-b[y]['real_gdp_trn'],6),
          '| dExp pub',round(pu[y]['expenditure_diagnostic_trn']-b[y]['expenditure_diagnostic_trn'],6),'| dTax prem',round(pr[y]['tax_diagnostic_trn']-b[y]['tax_diagnostic_trn'],6),'| supply ceiling binding? unmet',round(b[y]['unmet_demand_real'],6))
# unmet demand across all cases
print('max unmet demand across cases/years',max(float(r['unmet_demand_real']) for r in D.values() if r['unmet_demand_real'] not in ('',None) and not r['case'].startswith('OLD_')))
# 6 DM-05 independence: INVEST_START_ONLY_2029 vs ILLUSTRATIVE_ALL (investment_start 2028)
i29=run(cs['INVEST_START_ONLY_2029']); 
print('INVEST_START_ONLY_2029 vs ALL: rate path identical',all(D[('INVEST_START_ONLY_2029',y)]['standard_tax_rate']==D[('ILLUSTRATIVE_ALL',y)]['standard_tax_rate'] for y in range(2026,2056)),'credit 2028',i29[2028]['corporate_credit'],b[2028]['corporate_credit'],'GDP 2055 diff',round(i29[2055]['real_gdp_trn']-b[2055]['real_gdp_trn'],6))
# 7 tax elasticity: tax/GDP and 30% cap
print('tax_macro/N 2055 ALL',round(b[2055]['tax_macro_trn']/b[2055]['nominal_gdp_trn'],4),'TEXT',round(run(cs['TEXT_KNOWN_PARTIAL'])[2055]['tax_macro_trn']/run(cs['TEXT_KNOWN_PARTIAL'])[2055]['nominal_gdp_trn'],4))
# 8 threshold/branch checks on inputs
p=cfg['parameters']
print('500/300 inclusive & 240 inclusive handled in model: tested via direct calls below')
tf=G['social']; pp=copy.deepcopy(p); pp['cohorts']=[dict(income_man=v,persons=1.,contribution_rate=.15,mpc=.8) for v in (300.,300.01,500.,500.01)]; pp['in_kind_per_eligible_man']=1.
r=tf(pp,2030,0.,0.,0.,False); print('premium',r['prem'],'expected',(300+300.01+500)*.15*.35/1e8,'kind',r['kind'])
# 9 circuit-breaker: elderly subsidy not halted while workers halted
ci=run(cs['CIRCUIT_ILLUSTRATION']); hl=[y for y in range(2026,2056) if ci[y]['circuit_halted']]
print('CIRCUIT halted years',hl[:3],'..',hl[-1:] ,'count',len(hl))
# 10 supply-ceiling regime: years with unmet demand >0, per case
import collections
cnt=collections.OrderedDict()
for s in cfg['cases']:
    o=run(s); cnt[s['id']]=sum(1 for y in range(2026,2056) if o[y]['unmet_demand_real']>1e-12)
print('years with unmet demand>0 (of 30):',dict(cnt))
# PREMIUM vs ALL GDP effect if the ceiling does not bind (slack=1.0)
def withslack(nm,sl):
    s=copy.deepcopy(cs[nm]); s['overrides']['slack']=sl; return run(s)
a=withslack('ILLUSTRATIVE_ALL',1.0); b2=withslack('ILLUSTRATIVE_PREMIUM',1.0)
print('slack=1.0: PREMIUM-ALL dGDP 2038/2045/2055',[round(b2[y]['real_gdp_trn']-a[y]['real_gdp_trn'],6) for y in (2038,2045,2055)],'unmet years',sum(1 for y in range(2026,2056) if a[y]['unmet_demand_real']>1e-12))
# 11 circuit: elderly subsidy gating
s=copy.deepcopy(cs['CIRCUIT_ILLUSTRATION']); o1=run(s)
s2=copy.deepcopy(s); s2['overrides']['elderly_subsidy_per_worker_man']=0.; s2['overrides']['pension_relief_per_worker_man']=0.; o2=run(s2)
print('CIRCUIT 2040 halted',o1[2040]['circuit_halted'],'expenditure diff when elderly subsidy+pension set 0:',round(o1[2040]['expenditure_diagnostic_trn']-o2[2040]['expenditure_diagnostic_trn'],6),'(nonzero = paid while halted)')
# 12 old-model anchors for disaster/climate
try:
    assert OLDJ
    old=json.load(open(OLDJ))
    oc=json.loads(old['annex_inputs']['sources']['SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json']['utf8'])['sq_bundle']['f_config']
    print('old risk rules:',oc['risk_shock_pct']['rules']); print('old expenditure growth table:',oc['expenditure_growth_pct']['table'])
except Exception as e: print('old config not read',e)
# 13 stored OLD_ rows vs old DM04/DM05 CSV (30b926dd) on shared columns
oldp=OLDC
if oldp and os.path.exists(oldp):
    OR={(r['case'],r['year']):r for r in csv.DictReader(open(oldp,encoding='utf-8'))}
    shared=[k for k in next(iter(csv.DictReader(open(cv,encoding='utf-8')))) if k in next(iter(OR.values())) and k not in('case','year','scope')]
    mism=0;cells=0
    for (c,y),r in D.items():
        if not c.startswith('OLD_'): continue
        o=OR[(c[4:],str(y))]
        for k in shared:
            cells+=1
            if r[k]!=o[k]: mism+=1
    print('OLD_ rows vs 30b926dd CSV: shared cols',len(shared),'cells',cells,'string mismatches',mism)

# 14 baseline attribution: new CORE vs old (aging-drag table, migration ramp) -- uses old config embedded in the 30b926dd JSON
try:
    tab=oc['aging_drag_pp']['table']
    def pw(t): return [x['value'] for x in tab if x['from']<=t][-1]
    src=open(os.path.join(here,'SPE_F_Text_Independent_Recalc_DRAFT_20261117.py'),encoding='utf-8').read().split("mx=0.; n=0; bad=[]")[0]
    def build(aging,ramp):
        h=src
        if aging: h=h.replace("lg=ln/lab-1; lab=ln","lg=ln/lab-1+PW(y)/100; lab=ln")
        if ramp: h=h.replace("want=p['migration_annual']; cf=","want=p['migration_annual']*min((y-2030+1)/5,1.); cf=")
        sys.argv=['x',j,cv]; g={'PW':pw,'__name__':'m'}; exec(compile(h,'m','exec'),g); return g
    for nm,(ag,rp) in {'as modelled':(0,0),'+old aging drag table':(1,0),'+old 5y migration ramp':(0,1),'+both':(1,1)}.items():
        g=build(ag,rp); o=g['run']({s_['id']:s_ for s_ in g['cfg']['cases']}['TEXT_KNOWN_PARTIAL'])
        print('baseline attribution:',nm,'TEXT_KNOWN_PARTIAL 2055 real GDP',round(o[2055]['real_gdp_trn'],3),'pop(M)',round(o[2055]['population_persons']/1e6,2))
    print('old expenditure growth table vs new constant 2.5%: 2055 expenditure new',round(run(cs['TEXT_KNOWN_PARTIAL'])[2055]['expenditure_diagnostic_trn'],2),'oldCORE',D[('OLD_CORE_NO_POLICY',2055)]['expenditure_diagnostic_trn'][:7])
except Exception as e: print('attribution skipped',e)
# 15 circuit: first halted year, subsidy gating
hy=[y for y in range(2026,2056) if run(cs['CIRCUIT_ILLUSTRATION'])[y]['circuit_halted']]
s2=copy.deepcopy(cs['CIRCUIT_ILLUSTRATION']); s2['overrides']['elderly_subsidy_per_worker_man']=0.; s2['overrides']['pension_relief_per_worker_man']=0.
print('CIRCUIT halted years',hy,'| expenditure paid during halt (subsidy+pension) in',hy[0],':',round(run(cs['CIRCUIT_ILLUSTRATION'])[hy[0]]['expenditure_diagnostic_trn']-run(s2)[hy[0]]['expenditure_diagnostic_trn'],6))
