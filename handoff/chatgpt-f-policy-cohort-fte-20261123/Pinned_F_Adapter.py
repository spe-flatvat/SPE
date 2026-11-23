"""Isolated workers. All existing modules/inputs remain byte unchanged."""
import argparse,copy,hashlib,importlib.util,json,os,sys
from pathlib import Path
sys.dont_write_bytecode=True
D='handoff/chatgpt-statusquo-common-macro-limited-diagnostic-20261123'
F='handoff/f-common-endoflife-finalization-20261121'
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sq(root,out,mode):
 # Extend prior asserted adapter in memory; only SQ is selected.
 source=(root/D/'SQ_Common_Runtime.py').read_text()
 a="   else:a=b=None"
 b="""   elif mode in ['KEYS_DEFAULT','KEY_BASE_NONDEFAULT','KEY_CONFLICT_NONDEFAULT','LEGACY_BASE_NONDEFAULT','LEGACY_CONFLICT_NONDEFAULT']:
    if mode.startswith('KEY'):
     old=\"inflation=.02+(.02 if oil else 0.)+(c['exogenous_shocks']['conflict_gdp_loss'] if y==2027 else 0.)\"
     new=\"inflation=p['base_inflation']+(p['oil_inflation_extra'] if oil else 0.)+(p['conflict_inflation_extra'] if y==2027 else 0.)\"
     assert source.count(old)==1;source=source.replace(old,new)
    a='p,bprof,mig,enabled,omit=configure(c,spec);'
    b=a+(\"p['base_inflation']=.03;\" if 'BASE_NONDEFAULT' in mode else \"p['conflict_inflation_extra']=.01;\" if 'CONFLICT_NONDEFAULT' in mode else '')
   else:a=b=None"""
 assert source.count(a)==1;source=source.replace(a,b)
 ns={'__name__':'isolated_sq_worker'};exec(compile(source,'isolated_sq_worker.py','exec'),ns);ns['execute'](root,out,mode)
def f(root,out,offset,elder_delta):
 sys.path.insert(0,str(root/F));M=mod('isolated_F_model',root/F/'Model.py');c=json.loads((root/F/'Inputs.json').read_text());_,edu,ec,integ,v,vc=M.load(c)
 ir={int(r['year']):r for r in M.read(root/'handoff/f-integrated-20261121/Annual.csv') if r['case']=='FULL_ADDITIONAL'}
 defs=[float(ir[y]['common_deflator']) for y in range(2026,2056)];pop=[float(ir[y]['population']) for y in range(2026,2056)]
 s={**c['defaults'],**next(x for x in c['cases'] if x['id']=='LATEST_F')};es=next(x for x in ec['cases'] if x['id']=='COMBINED');ed=edu.Education(ec,{**es,'E':s['edu_E'],'S':s['edu_S'],'T':s['edu_T']},defs);shared=json.loads((root/'handoff/chatgpt-n3-transition-financing-full-dynamics-20261122/Medical_Initialization.json').read_text())
 # Medical-only references are common SQ; education keeps its existing policy inputs.
 aligned=True;medical_defs=shared['deflators']
 medical_pop=shared['population'] if aligned else pop
 md=M.Medical(c,s,medical_defs,medical_pop)
 original=integ.make_base
 def base(*a,**kw):
  r=original(*a,**kw);save(out/'Policy_Base_Ledgers.json',{k:r[3][k] for k in ['d','sq','elder','foreign','pension']});md.trajectory=r[3]['d'];md.elder=r[3]['elder'];return r
 integ.make_base=base;resolved=[];tr=[];seen=set();par={}
 def injected_compile(source,filename,mode):
  if filename=='medical_education_integrated.py':
   old="labornew=t['effective_productive_workers']+extra_workers"
   assert source.count(old)==1
   source=source.replace(old,old+'+_common_offset[i]+_elder_delta[i]')
   (out/'Resolved_F_Cohort_Runtime.py.txt').write_text(source)
  return compile(source,filename,mode)
 M.compile=injected_compile
 def hook(engine,pol):
  n=M.patch(edu.patched_engine(engine,pol,ed,'REPLACE'),pol,md,s)
  if pol=='F':
   n['run_path'].__globals__.update(_common_offset=offset,_elder_delta=elder_delta)
   resolved.append(n['run_path'].__code__)
  return n
 integ._education_hook=hook
 def local(fr,ev,arg):
  v=fr.f_locals;y=v.get('y');r=v.get('r')
  if ev=='line' and isinstance(r,dict) and r.get('year')==y and y not in seen and '_identity_capital_residual' in r:
   seen.add(y);par.update(copy.deepcopy(v['p']));keys=['coreY','coreN','coreD','Y','N','labor','growth','risk','inflation','C','I','K','supply','desired','capacity','unmet','pressure','education_nom','education_level','finite','tax','direct']
   tr.append(dict(year=y,**{k:v.get(k) for k in keys},trajectory_effective_L=v['c']['_trajectory'][y-2026]['effective_productive_workers'],education_effective_added=v['z']['education_effective_labor_added'],health_effective_added=v['w']['health_effective_labor_added'],elder_effective_added=v.get('extra_workers',0.) if y>2026 else 0.))
  return local
 def trace(fr,ev,arg):
  if ev=='call' and fr.f_code.co_name=='run_path' and fr.f_code.co_filename=='medical_education_integrated.py':return local
 saved=M.vat_hook(v,md,s);sys.settrace(trace)
 try:rows,inc,sectors,b,raw,cc=integ.execute(v,vc,dict(id='LATEST_F',C=s['C'],C_mode=s['C_mode']))
 finally:sys.settrace(None);integ.make_base=original;v.sector_account=saved
 for i,(r,m) in enumerate(zip(rows,raw)):
  w=md.rows[i];r.update(integ.fiscal(r,m,b,i,cc));r.update(ed.rows[i]);r.update(w)
  r.update(nominal_wage_proxy_man=m.get('nominal_wage_proxy_man'),real_wage_proxy_man=m.get('real_wage_proxy_man'),real_growth_pct=m['real_growth_pct'],core_real_gdp_trn=m['core_real_gdp_trn'],capital_delta_real_trn=m['capital_delta_real_trn'],macro_cash_DI_proxy_trn=r['household_disposable_nominal_trn']-r['household_direct_price_benefit_trn'])
 assert len(rows)==len(tr)==30
 save(out/'F_Actual_Annual.json',rows);save(out/'F_Medical_Reference_Inputs.json',dict(deflators=medical_defs,population=medical_pop,education_deflators=defs,aligned=aligned));save(out/'F_Runtime_Trace.json',dict(parameters=par,years=tr));save(out/'F_Common_Clinical_Accounts.json',md.common);save(out/'F_Medical_Accounts.json',md.rows)
 print(json.dumps(dict(case='F_LATEST_IMPLEMENTED',rows=len(rows),real2055=rows[-1]['real_gdp_trn'])),flush=True)
def n3(root,out):
 R=mod('isolated_attribution',root/'handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/Attribution_Runtime.py');r,s=R.build(root,out,dict(case='BASE_REPLAY'));a,l,b=r.simulate(s)
 save(out/'N3_Actual_Annual.json',a);save(out/'N3_Actual_Fiscal.json',l);save(out/'N3_Runtime_Midpoints.json',r.midpoints);save(out/'N3_Runtime_Checks.json',dict(checks=r.counter,failures=r.checks));save(out/'N3_Common_Input_Contract.json',dict(parameters=r.par,medical_input=r.medical_input,component_settings=r.ci['s']))
 # SQ replay is independently executed; these are read-only original denominator states for exact matching.
 save(out/'N3_SQ_Denominator_States.json',list(r.sq.values()))
 print(json.dumps(dict(case='N3_NATIVE_EXISTING',rows=len(a),real2055=a[-1]['real_GDP_trn'],checks=r.counter,failed=len(r.checks))),flush=True)
