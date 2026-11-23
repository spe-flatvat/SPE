"""In-memory adapters only; fixed source and parameters remain unchanged."""
import argparse,copy,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
D='handoff/chatgpt-statusquo-common-macro-limited-diagnostic-20261123'
T='handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123'
def main(root,out,case,inputs):
 out.mkdir(parents=True,exist_ok=True);opened=set()
 def audit(event,args):
  if event=='open' and isinstance(args[0],str):
   p=Path(args[0]).resolve()
   if p.is_relative_to(root) and p.is_file() and not p.is_relative_to(out) and 'chatgpt-common-macro-demography-labor-productivity-diagnostic-20261123' not in str(p):opened.add(str(p.relative_to(root)))
 sys.addaudithook(audit)
 data=json.loads(inputs.read_text())
 if case.startswith('F_'):
  src=(root/T/'Three_Scenario_Worker.py').read_text().split("if __name__=='__main__':")[0]
  ns={'__name__':'private_F_worker'};exec(compile(src,'private_F_worker','exec'),ns)
  orig=ns['mod']
  def mod(n,p):
   m=orig(n,p)
   if n=='isolated_F_model':
    text=p.read_text();old=" exec(compile(source,'medical_education_integrated.py','exec'),ns);return ns"
    change="labornew=t['effective_productive_workers']+extra_workers"
    new="labornew=t['effective_productive_workers']+extra_workers+_common_offset[i]"
    assert text.count(old)==1
    if case=='F_COMMON_L_FIXED':
     text=text.replace(old," source=source.replace("+repr(change)+","+repr(new)+")\n"+old)
    exec(compile(text,str(p),'exec'),m.__dict__);m.__dict__['_common_offset']=data['common_L_offset']
    # _common_offset must reach the final compiled run_path globals.
    oldpatch=m.patch
    def patch(*a,**kw):
     z=oldpatch(*a,**kw);z['run_path'].__globals__['_common_offset']=data['common_L_offset'];return z
    m.patch=patch
   return m
  ns['mod']=mod;ns['f'](root,out,True)
 else:
  src=(root/D/'SQ_Common_Runtime.py').read_text()
  needle='   else:a=b=None'
  new="""   elif mode!='BASE_SQ_REPLAY':
    a="labornew=t['effective_productive_workers']+extra_workers"
    b="labornew="+repr(_labor_values)+"[i]"
    if mode=='A_FIXED':
     a='nonlabor_factor*=1+p[\'base_growth\']-risk'
     b='nonlabor_factor=1. # Diagnostic removes real base growth and event accumulation only'
   else:a=b=None"""
  # repr quoted expression avoids string-literal escaping ambiguity.
  new=new.replace("a='nonlabor_factor*=1+p['base_growth']-risk'",'a="nonlabor_factor*=1+p[\'base_growth\']-risk"')
  assert src.count(needle)==1;src=src.replace(needle,new)
  needle="row={k:v.get(k) for k in keys};row.update"
  src=src.replace(needle,"row={k:v.get(k) for k in keys};row.update(demography=copy.deepcopy(v['t']),macro_row=copy.deepcopy(r));row.update")
  ns={'__name__':'isolated_diagnostic','_labor_values':data['labor'][case]};exec(compile(src,'private_SQ_worker','exec'),ns)
  ns['execute'](root,out,case)
 rs=[]
 for p in sorted(opened):
  b=(root/p).read_bytes();rs.append(dict(path=p,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
 (out/'Runtime_Source_Receipts.json').write_text(json.dumps(rs,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--inputs',type=Path,required=True);a=p.parse_args();main(a.root.resolve(),a.out.resolve(),a.case,a.inputs.resolve())
