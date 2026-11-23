"""Rebuild native SQ/N3 ledgers before existing dynamic N3 execution; no source writes."""
import argparse,copy,csv,hashlib,importlib.util,json,os,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
P='handoff/chatgpt-labor-timing-older-workers-annual-hours-20261123'
BD='handoff/chatgpt-n3-policy-burden-diagnosis-20261122'
ND='handoff/chatgpt-n3-f-parity-implementation-20261122'
ROB='handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122'
TRANS='handoff/chatgpt-n3-transition-financing-full-dynamics-20261122'
FD='handoff/chatgpt-national-fiscal-closure-20261121'
BASE='PARITY_CONNECTED_CANDIDATE';SQ='SQ_COMMON_ON'
def js(p):return json.loads(p.read_text())
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def capture(root,out,draft,labor,refs=None,only_sq=False):
 out.mkdir(parents=True,exist_ok=True)
 adapter=mod('Macro_Adapter',root/ND/'Macro_Adapter.py');sys.modules['Macro_Adapter']=adapter;patch=adapter.patch;resolved={}
 def aligned(source,s):
  source=patch(source,s)
  if labor is not None:
   old="labornew=t['effective_productive_workers']+extra_workers";assert source.count(old)==1
   source=source.replace(old,'labornew='+repr(labor)+'[i]')
  resolved[s['id']]=source
  return source
 adapter.patch=aligned
 f=root/BD/'N3_Policy_Burden_Diagnosis_Reproduce.py';src=f.read_text()
 src=src.replace('records=[];seen=set();params={}','records=[];seen=set();params={};component_inputs={};medical_inputs={}')
 a="seen.add((cid,y));params[cid]=copy.deepcopy(v['p'])"
 b=a+"\n    if cid not in component_inputs:\n     component_inputs[cid]=copy.deepcopy(dict(config=md.components.cfg,household=md.components.hh,pension=md.components.pen,s=md.s,deflators=md.deflators,trajectory=md.trajectory,elder=md.elder))\n     medical_inputs[cid]=copy.deepcopy(dict(c=md.c,s=md.s,deflators=md.deflators,population=md.population,trajectory=md.trajectory,elder=md.elder))"
 assert src.count(a)==1;src=src.replace(a,b).replace('data=dict(parameters=params,records=records)','data=dict(parameters=params,records=records,component_inputs=component_inputs,medical_inputs=medical_inputs)')
 ns={'__file__':str(f),'__name__':'aligned_capture'};exec(compile(src,str(f),'exec'),ns);ns['SELECT']=[SQ] if only_sq else [SQ,BASE]
 original=Path.read_text
 def read(p,*a,**kw):
  text=original(p,*a,**kw)
  if refs and p==root/'handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Model.py':
   old="original_medical=FM.Medical;original_claim=";assert text.count(old)==1
   text=text.replace(old,'core='+repr(refs['core_nominal'])+'\n '+old)
   old="active.clear();ex=extensions.get(s['id'],{});";assert text.count(old)==1
   text=text.replace(old,'defs='+repr(refs['deflators'])+';pops='+repr(refs['population'])+';'+old)
  return text
 Path.read_text=read
 try:d=ns['capture'](root,out,draft)
 finally:Path.read_text=original
 for k,v in resolved.items():(out/('Resolved_'+k+'.py.txt')).write_text(v)
 return d

def main(root,out,case):
 out.mkdir(parents=True,exist_ok=True);opened=set()
 def audit(event,args):
  if event=='open' and isinstance(args[0],str):
   p=Path(args[0]).resolve()
   if p.is_relative_to(root) and p.is_file() and not p.is_relative_to(Path(__file__).parent):opened.add(str(p.relative_to(root)))
 sys.addaudithook(audit)
 oldtrace=js(root/BD/'N3_Unchanged_Execution_Trace.json');oldSQ=[x for x in oldtrace['records'] if x['case']==SQ]
 labor=None if case=='BASE_SQ_UNCHANGED' else js(root/P/'Fixed_Aligned_Case_Inputs.json')['cases'][case]['engine_L']
 draft=out/'draft-source';path='handoff/claude-n3-model-draft-20261121/SPE_N3_Medical_On_CommonSQ_Draft_DRAFT_20261121.py';f=draft/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(subprocess.check_output(['git','show','3c77eafc2073fdaba4c129164817d2f57c9421b9:'+path],cwd=root))
 # Bootstrap common core price/nominal series. These core states precede medical feedback.
 if labor is not None:
  bootstrap=capture(root,out/'bootstrap',draft,labor,only_sq=True);sq=bootstrap['records'];ciold=js(root/ROB/'Component_Initialization.json');miold=js(root/TRANS/'Medical_Initialization.json')
  refs=dict(core_nominal=[ciold['config']['core_nominal'][i]*t['coreN']/oldSQ[i]['coreN'] for i,t in enumerate(sq)],deflators=[miold['deflators'][i]*t['coreD']/oldSQ[i]['coreD'] for i,t in enumerate(sq)],population=miold['population'])
 else:refs=None
 # Discard bootstrap module mutations before the final native execution.
 for name,m in list(sys.modules.items()):
  file=getattr(m,'__file__',None)
  if file and Path(file).resolve().is_relative_to(root/'handoff') and Path(file).resolve()!=Path(__file__).resolve():sys.modules.pop(name,None)
 data=capture(root,out/'native',draft,labor,refs);ci=data.pop('component_inputs')[BASE];mi=data.pop('medical_inputs')[BASE]
 ci['elder']=[{k:v for k,v in r.items() if k in ['65_69_male_population','65_69_female_population','70_74_male_population','70_74_female_population']} for r in ci['elder']];ci['household']={k:ci['household'][k] for k in ['stats','income_cells']};ci['pension']={'public':{'strata':ci['pension']['public']['strata']}}
 save(out/'Component_Initialization.json',ci);save(out/'Medical_Initialization.json',mi);save(out/'Native_Base_Trace.json',data)
 # Execute unchanged fiscal mapping on the newly generated two-case ledgers.
 nf=root/FD/'National_Fiscal.py';src=nf.read_text().replace("MODES=['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']","MODES=['DOMESTIC_TRANSFER']").replace('for mode in MODES:assert len(annual[mode])==2370','for mode in MODES:assert len(annual[mode])==60').replace("frows=[dict(r,case='F_FIXED_REFERENCE') for r in F.values()]","frows=[]")
 ns={'__file__':str(nf),'__name__':'aligned_fiscal'};exec(compile(src,str(nf),'exec'),ns)
 macro=out/'fiscal-input';(macro/'DOMESTIC_TRANSFER').mkdir(parents=True,exist_ok=True)
 for name in ['Gap_Annual.csv','N3_Engine_Accounts.csv']:(macro/'DOMESTIC_TRANSFER'/name).write_bytes((out/'native/runtime'/name).read_bytes())
 ns['main'](macro,out/'fiscal')
 fiscal=ns['read_fiscal'](out/'fiscal'); fiscal=[r for r in fiscal if r['scenario']=='REFERENCE_CANDIDATE'];assert len(fiscal)==60
 primary=[];idx={(x['case'],x['year']):x for x in data['records']}
 for y in range(2026,2056):
  t=idx[BASE,y];q=idx[SQ,y];value=t['macro_row']['tax_diagnostic_trn']-q['macro_row']['tax_diagnostic_trn']-t['macro_row']['expenditure_diagnostic_trn']+q['macro_row']['expenditure_diagnostic_trn']+t['medical'].get('medical_policy_interest_trn',0.)-q['medical'].get('medical_policy_interest_trn',0.)
  primary.append(dict(year=y,policy_primary_delta_trn=value))
 replacements={root/BD/'N3_Unchanged_Execution_Trace.json':data,root/ROB/'Component_Initialization.json':ci,root/TRANS/'Medical_Initialization.json':mi}
 # Runner constructors read these fixed cache names; redirect all dependent caches together.
 oldread=Path.read_text
 def redirect(p,*args,**kw):
  if p in replacements:return json.dumps(replacements[p])
  return oldread(p,*args,**kw)
 Path.read_text=redirect
 try:
  R=mod('aligned_attribution',root/'handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/Attribution_Runtime.py');runner,s=R.build(root,out,dict(case='BASE_REPLAY'))
 finally:Path.read_text=oldread
 runner.fiscal={int(r['year']):r for r in fiscal if r['case']==BASE};runner.sf={int(r['year']):r for r in fiscal if r['case']==SQ};runner.primary={r['year']:r['policy_primary_delta_trn'] for r in primary}
 runner.funding={int(r['year']):r for r in ns['rd'](out/'native/runtime/Corporate_Funding_Stock.csv') if r['case']==BASE}
 save(out/'Runtime_Specification.json',s);save(out/'Fiscal_Rebuilt_References.json',fiscal);save(out/'Primary_Rebuilt_References.json',primary)
 annual,ledger,bridge=runner.simulate(s)
 save(out/'N3_Annual.json',annual);save(out/'N3_Fiscal.json',ledger);save(out/'N3_Tax_Bridge.json',bridge);save(out/'N3_Midpoints.json',runner.midpoints);save(out/'N3_Clinical_Accounts.json',runner.medical_accounts);save(out/'N3_Connection_Trace.json',runner.local_connection)
 save(out/'N3_Dynamic_Base_Factors.json',runner.live_component.dynamic_rows);save(out/'N3_Pension_Accounts.json',runner.live_component.pension);save(out/'N3_Policy_Accounts.json',runner.live_component.rows)
 save(out/'N3_Runtime_Validation.json',dict(checks=runner.counter,failures=runner.checks))
 (out/'Resolved_N3_Runtime.py.txt').write_text(runner.resolved_runtime)
 # Emit the precise references used per year, allowing independent consistency checks.
 refs_used=[]
 for y in range(2026,2056):
  refs_used.append(dict(year=y,case=case,base_sha256=hashlib.sha256(json.dumps(runner.base[y],sort_keys=True).encode()).hexdigest(),sq_sha256=hashlib.sha256(json.dumps(runner.sq[y],sort_keys=True).encode()).hexdigest(),base_labor=runner.base[y]['labor'],sq_labor=runner.sq[y]['labor'],base_coreY=runner.base[y]['coreY'],sq_coreY=runner.sq[y]['coreY'],base_coreN=runner.base[y]['coreN'],sq_coreN=runner.sq[y]['coreN'],base_coreD=runner.base[y]['coreD'],sq_coreD=runner.sq[y]['coreD'],medical_deflator=runner.medical_input['deflators'][y-2026],component_deflator=runner.ci['deflators'][y-2026],sq_wage_reference=runner.ci['config']['sq_wage_nominal_man'][y-2026],core_nominal_reference=runner.ci['config']['core_nominal'][y-2026]))
 save(out/'N3_References_Used.json',refs_used)
 receipts=[]
 for path in sorted(opened):
  b=(root/path).read_bytes();receipts.append(dict(path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
 save(out/'Runtime_Source_Receipts.json',receipts)
 print(json.dumps(dict(case=case,real2055=annual[-1]['real_GDP_trn'],checks=runner.counter,failures=runner.checks)),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();main(a.root.resolve(),a.out.resolve(),a.case)
