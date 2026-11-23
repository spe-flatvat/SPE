"""Execute only SQ_COMMON_ON using immutable common/N3 adapter dependencies.
A private Macro_Adapter wrapper applies at most one diagnostic source change.
"""
import argparse,copy,importlib.util,json,os,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
N3='handoff/chatgpt-n3-f-parity-implementation-20261122'
DRAFT_COMMIT='3c77eafc2073fdaba4c129164817d2f57c9421b9'
DRAFT_PATH='handoff/claude-n3-model-draft-20261121/SPE_N3_Medical_On_CommonSQ_Draft_DRAFT_20261121.py'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def execute(root,out,mode):
 out.mkdir(parents=True,exist_ok=True);os.environ['SPE_PENSION_MODE']='DOMESTIC_TRANSFER'
 sys.path.insert(0,str(root/N3));adapter=module('Macro_Adapter',root/N3/'Macro_Adapter.py');sys.modules['Macro_Adapter']=adapter
 patch=adapter.patch;resolved=[]
 def isolated(source,s):
  source=patch(source,s)
  if s['id']=='SQ_COMMON_ON':
   if mode=='MULTIPLICATIVE_NOMINAL':
    a='coreN*=1+growth+inflation;coreD=coreN/coreY';b='coreN*=(1+growth)*(1+inflation);coreD=coreN/coreY'
   elif mode=='INITIAL_OIL_EXISTING_FLAG':
    a='p,bprof,mig,enabled,omit=configure(c,spec);';b=a+"p['apply_oil_to_initial']=True;"
   elif mode=='NO_PRICE_PRESSURE':
    a='p,bprof,mig,enabled,omit=configure(c,spec);';b=a+"spec['price_feedback']=False;"
   else:a=b=None
   if a is not None:assert source.count(a)==1;source=source.replace(a,b)
   resolved.append(source)
  return source
 adapter.patch=isolated;records=[];seen=set();parameters={};baseline_profile={}
 def local(frame,event,arg):
  if event=='line':
   v=frame.f_locals;r=v.get('r');y=v.get('y')
   if isinstance(r,dict) and r.get('year')==y and y not in seen and 'parity_supply_real_trn' in r:
    seen.add(y);parameters.update(copy.deepcopy(v['p']));baseline_profile.update(copy.deepcopy(v['bprof']))
    keys=['coreY','coreN','coreD','Y','N','labor','labor_anchor','nonlabor_factor','coreY_anchor','growth','risk','inflation','lg','C','I','K','Kprev','H','Hprev','supply','desired','capacity','unmet','pressure','tax','direct','cash','feedback','replacement','education_nom','education_level','finite','prevY','prevN','enabled']
    row={k:v.get(k) for k in keys};row.update(year=y,link=v['spec'].get('_link'),price_feedback=v['spec'].get('price_feedback',True),
     population=v['t']['population'],working_age_population=v['t']['working_age'],foreign_population=v['t']['foreign'],
     birth_count=v['t']['births_calendar'],death_count=v['t']['deaths_calendar'],net_migration=v['t']['foreign_net_migration'],
     service_nominal=v['w']['service_production_nominal_delta_trn'],medical_HH_nominal=v['w']['household_cash_delta_trn'],
     medical_input_deflator=v['_medical'].deflators[y-2026] if '_medical' in v else frame.f_globals['_medical'].deflators[y-2026],
     energy_logistics_metadata_pct=r.get('energy_logistics_shock_pct'),household_consumption_real_proxy=r.get('household_consumption_real_proxy_trn'),
     total_capital_real_proxy=r.get('capital_total_real_trn'),expenditure_core_nominal_proxy=r.get('common_expenditure_core_trn'))
    records.append(row)
  return local
 def trace(frame,event,arg):
  if event=='call' and frame.f_code.co_name=='run_path' and frame.f_code.co_filename=='n3_medical_on_SQ_adapter.py':return local
 with tempfile.TemporaryDirectory(prefix='sq-limited-') as tmp:
  tmp=Path(tmp);script=tmp/DRAFT_PATH;script.parent.mkdir(parents=True)
  script.write_bytes(subprocess.check_output(['git','show',DRAFT_COMMIT+':'+DRAFT_PATH],cwd=root))
  cfg=json.loads((root/N3/'Inputs.json').read_text());cfg['execution_case_filter']=['SQ_COMMON_ON'];inp=tmp/'Inputs.json';inp.write_text(json.dumps(cfg))
  model=module('sq_private_execution',root/N3/'Model.py');old=sys.gettrace();sys.settrace(trace)
  try:model.run(inp,root,tmp,tmp/'runtime')
  finally:sys.settrace(old)
 assert len(records)==30 and len(resolved)==1,(len(records),len(resolved))
 (out/('Common_Trace_'+mode+'.json')).write_text(json.dumps(dict(mode=mode,parameters=parameters,baseline_profile=baseline_profile,years=records),indent=2)+'\n')
 (out/('Resolved_Common_Runtime_'+mode+'.py.txt')).write_text(resolved[0])
 print(json.dumps(dict(mode=mode,rows=30,real2055=records[-1]['Y'],nominal2055=records[-1]['N'])))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);p.add_argument('--mode',required=True);a=p.parse_args();execute(a.root.resolve(),a.outdir.resolve(),a.mode)
