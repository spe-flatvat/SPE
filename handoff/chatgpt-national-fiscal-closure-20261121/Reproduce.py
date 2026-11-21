#!/usr/bin/env python3
"""Re-run pinned 4x79 macro paths, then new fiscal equations twice. Stdlib + git.
Official extracted inputs are retained; openpyxl is only needed to re-extract XLSX.
"""
import argparse,tempfile,subprocess,sys,os,json,hashlib,concurrent.futures
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def run(out):
 out=out.resolve();out.mkdir(parents=True,exist_ok=True)
 # Receipt checks do not rely on prior AI verification claims.
 for pin in json.loads((P/'Runtime_Pins.json').read_text()):
  b=subprocess.check_output(['git','show',pin['commit']+':'+pin['path']],cwd=ROOT)
  assert hashlib.sha256(b).hexdigest()==pin['sha256'] and len(b)==pin['size'],pin['path']
 with tempfile.TemporaryDirectory(prefix='spe_national_fiscal_') as temp:
  t=Path(temp);engine=t/'engine';source=t/'draft';macro=t/'macro'
  for dest,c in [(engine,'76176ae118ee073677e990c0d8c4cfa498e3563d'),(source,'3c77eafc2073fdaba4c129164817d2f57c9421b9')]:
   if subprocess.run(['git','cat-file','-e',c],cwd=ROOT,capture_output=True).returncode:subprocess.run(['git','fetch','origin',c],cwd=ROOT,check=True)
   subprocess.run(['git','worktree','add','--detach',str(dest),c],cwd=ROOT,check=True)
  try:
   p=engine/'handoff/chatgpt-n3-pension-counterpart-20261121'
   def one(mode):
    dest=macro/mode;dest.mkdir(parents=True,exist_ok=True)
    with (out/(mode+'_Macro_Execution.log')).open('w') as f:
     subprocess.run([sys.executable,str(p/'Gap_Model.py'),str(p/'Gap_Inputs.json'),'--engine',str(engine),'--source',str(source),'--outdir',str(dest)],env={**os.environ,'SPE_PENSION_MODE':mode},stdout=f,stderr=subprocess.STDOUT,check=True)
     subprocess.run([sys.executable,str(p/'Build_Results.py'),'--outdir',str(dest)],stdout=f,stderr=subprocess.STDOUT,check=True)
   with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(one,['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']))
   # New fiscal code resolves fixed F paths in this checkout, protected by pins.
   subprocess.run([sys.executable,str(P/'National_Fiscal.py'),'--macro',str(macro),'--outdir',str(out)],check=True)
   subprocess.run([sys.executable,str(P/'National_Fiscal.py'),'--macro',str(macro),'--outdir',str(t/'replay')],check=True)
   subprocess.run([sys.executable,str(P/'Verify.py'),'--outdir',str(out),'--macro',str(macro),'--replay',str(t/'replay')],check=True)
   subprocess.run([sys.executable,str(P/'Build_Comparison.py'),'--outdir',str(out),'--macro',str(macro)],check=True)
  finally:
   for dest in [engine,source]:subprocess.run(['git','worktree','remove',str(dest)],cwd=ROOT,check=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);run(ap.parse_args().outdir)
