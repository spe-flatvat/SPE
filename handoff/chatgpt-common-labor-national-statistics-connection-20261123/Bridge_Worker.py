"""Invoke immutable prior adapters; only this case's in-memory labor connection changes."""
import argparse,importlib.util,json,sys,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
D='handoff/chatgpt-common-macro-demography-labor-productivity-diagnostic-20261123'
T='handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--inputs',type=Path,required=True);a=p.parse_args();root=a.root.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 opened=set()
 def audit(event,args):
  if event=='open' and isinstance(args[0],str):
   p=Path(args[0]).resolve()
   if p.is_relative_to(root) and p.is_file() and 'chatgpt-common-labor-national-statistics-connection-20261123' not in str(p):opened.add(str(p.relative_to(root)))
 sys.addaudithook(audit)
 if a.case=='N3_BASE_UNCHANGED':
  m=module('fixed_three_scenario',root/T/'Three_Scenario_Worker.py');m.n3(root,out)
 elif a.case.startswith('F_'):
  d=json.loads(a.inputs.read_text());definition=d['F_offsets'][a.case];inp=out/'Case_Connection.json';inp.write_text(json.dumps(dict(common_L_offset=definition))+'\n')
  m=module('fixed_prior_diagnostic',root/D/'Diagnostic_Worker.py')
  original_read=Path.read_text
  def read_with_trace(path,*args,**kw):
   text=original_read(path,*args,**kw)
   if path==root/T/'Three_Scenario_Worker.py':
    old="tr.append(dict(year=y,**{k:v.get(k) for k in keys}))"
    new="tr.append(dict(year=y,**{k:v.get(k) for k in keys},trajectory_effective_L=v['c']['_trajectory'][y-2026]['effective_productive_workers'],education_effective_added=v['z']['education_effective_labor_added'],health_effective_added=v['w']['health_effective_labor_added'],elder_effective_added=v.get('extra_workers',0.) if y>2026 else 0.))"
    assert text.count(old)==1;text=text.replace(old,new)
    (out/'Resolved_F_Labor_Trace_Adapter_Source.py.txt').write_text(text)
   return text
  Path.read_text=read_with_trace
  try:m.main(root,out,'F_BASE' if a.case=='F_BASE_UNCHANGED' else 'F_COMMON_L_FIXED',inp)
  finally:Path.read_text=original_read
 else:
  d=json.loads(a.inputs.read_text());inp=out/'Case_Connection.json';sourcecase='BASE_SQ_REPLAY' if a.case=='BASE_SQ_UNCHANGED' else a.case
  inp.write_text(json.dumps(dict(labor={sourcecase:d['cases'][a.case]['engine_L']},common_L_offset=[0.]*30))+'\n')
  m=module('fixed_prior_diagnostic',root/D/'Diagnostic_Worker.py');m.main(root,out,sourcecase,inp)

 receipts=[]
 for path in sorted(opened):
  b=(root/path).read_bytes();receipts.append(dict(path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
 (out/'Bridge_Runtime_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
