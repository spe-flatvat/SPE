# Supplementary checks for DM-04/DM-05 verification (read-only). Usage: python3 -I analysis_dm.py <new Inputs JSON> <new CSV> <old(783b3de0) CSV>
import sys,runpy,csv,copy,json
g=None
sys.argv=[sys.argv[0]]+sys.argv[1:3]+sys.argv[3:]
newj,newc,oldc=sys.argv[1],sys.argv[2],sys.argv[3]
sys.argv=['recalc',newj,newc]
import io,contextlib
buf=io.StringIO()
with contextlib.redirect_stdout(buf): G=runpy.run_path(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'SPE_F_Macro_DM04_DM05_Independent_Recalc_DRAFT_20261117.py'))
run=G['run'];cfg=G['cfg'];D=G['D']
# 1) old 18 paths preserved (all original columns, text exact)
old=list(csv.DictReader(open(oldc,encoding='utf-8')));new={(r['case'],r['year']):r for r in csv.DictReader(open(newc,encoding='utf-8'))}
bad=0;cells=0;cols=list(old[0].keys())
for r in old:
    n=new[(r['case'],r['year'])]
    for k in cols:
        cells+=1
        if r[k]!=n[k]: bad+=1
print('old cases',len({r['case'] for r in old}),'rows',len(old),'cols',len(cols),'cells',cells,'text-exact mismatches',bad)
print('new total rows',len(new),'cases',len({k[0] for k in new}))
# 2) factorial additivity in GDP, capital, tax; and under CAPACITY_TIGHT
def spec(i,**kw):
    s={'id':i};s.update(kw);return s
def fact(extra_params,tag):
    P=lambda **q:{'parameters':{**extra_params,**q}}
    b=run(spec('b',**P()))
    a=run(spec('a',sequence={'year8':2029},**P()))
    v=run(spec('v',**P(investment_start=2029)))
    w=run(spec('w',sequence={'year8':2029},**P(investment_start=2029)))
    mx={}
    for key in ['Y','K','T','Td','gap','un']:
        mx[key]=max(abs(w[t][key]-a[t][key]-v[t][key]+b[t][key]) for t in range(2026,2056))
    print(tag,'max |interaction| by var:',{k:f'{x:.3e}' for k,x in mx.items()})
fact({}, 'DEFAULT')
fact({'capacity_slack':0.0},'CAPACITY_TIGHT')
fact({'capacity_slack':0.0,'capacity_absorption':1.0,'capital_output_yield':0.15},'TIGHT+HIGH_YIELD')
# 3) investment_start effect isolation: promotion flow identical when only year8 moves; sector-investment still moves
b=run(spec('b'));a=run(spec('a',sequence={'year8':2029}));v=run(spec('v',parameters={'investment_start':2029}))
print('promotion flow max diff (tax8-only vs base):',max(abs(a[t]['Ipro']-b[t]['Ipro']) for t in range(2026,2056)))
print('tax path (rate) invest-only vs base: hh cash max diff:',max(abs(v[t]['hh']-b[t]['hh']) for t in range(2026,2056)))
print('sector-cash investment state diff 2030 (tax8-only):',a[2030]['I']-b[2030]['I'],' promo flow',a[2030]['Ipro']-b[2030]['Ipro'])
# 4) PREMIUM analytic check 2055: dGDP vs extra premium
p=run(spec('p',parameters={'medical_residual_funding':'PREMIUM'}));u=run(spec('u'))
for t in (2038,2045,2055):
    dh=p[t]['hh']-u[t]['hh'];x=p[t]['med']['xprem']
    print(t,'dHHcash',round(dh,6),'-xprem',round(-x,6),'dY',round(p[t]['Y']-u[t]['Y'],6),'dC',round(p[t]['C']-u[t]['C'],6),'dI',round(p[t]['I']-u[t]['I'],6),'dTax',round(p[t]['T']-u[t]['T'],6))
# with support share 1 (premium must be offset in cash)
ps=run(spec('ps',parameters={'medical_residual_funding':'PREMIUM','medical_household_support_share':1.0}));us=run(spec('us',parameters={'medical_household_support_share':1.0}))
print('PREMIUM+support=1 2055 dHHcash',ps[2055]['hh']-us[2055]['hh'],'(expected ~0 since support offsets)')
# 5) cumulative unfunded 2038-2055 and PUBLIC expenditure add
r=run(spec('r',parameters={'medical_residual_funding':'INTERNAL'}))
print('cum internal 2055',sum(r[t]['med']['xint'] for t in range(2026,2056)))
# 6) investment_start range & legacy compat
for yr in (2027,2035,2055):
    o=run(spec('o',parameters={'investment_start':yr}))
    print('inv start',yr,'first flow year',min(t for t in range(2026,2056) if o[t]['Ipro']>0) if any(o[t]['Ipro']>0 for t in range(2026,2056)) else None,'2055 Y',round(o[2055]['Y'],6))
# 7) year8 moved alone, previously dragged investment: new vs implied legacy
for y8 in (2029,2033):
    n_=run(spec('n',sequence={'year8':y8}));l_=run(spec('l',sequence={'year8':y8},parameters={'investment_start':y8}))
    print('year8',y8,'2055 Y alone',round(n_[2055]['Y'],6),'with linked inv',round(l_[2055]['Y'],6),'diff',round(l_[2055]['Y']-n_[2055]['Y'],6))
# 8) ordering: investment start before benefit/8% start allowed?
bs=cfg['parameters']['benefit_start'];print('benefit_start',bs,'year8',cfg['sequence']['year8'],'year5',cfg['sequence']['year5'])
