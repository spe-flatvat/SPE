#!/usr/bin/env python3
"""Reproduce N3 4 ownership candidates; stdlib + git; no edits outside --outdir."""
import argparse,subprocess,concurrent.futures,sys,os,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
MODES=['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']
def run(out,source=None):
 out=out.resolve();out.mkdir(parents=True,exist_ok=True)
 if source is None:
  source=out/'fixed-draft-source';commit='3c77eafc2073fdaba4c129164817d2f57c9421b9'
  if not source.exists():
   if subprocess.run(['git','cat-file','-e',commit],cwd=ROOT,capture_output=True).returncode:subprocess.run(['git','fetch','origin',commit],cwd=ROOT,check=True)
   subprocess.run(['git','worktree','add','--detach',str(source),commit],cwd=ROOT,check=True)
 def one(mode):
  dest=out/'macro'/mode;dest.mkdir(parents=True,exist_ok=True)
  with (out/(mode+'_Execution.log')).open('w') as log:
   subprocess.run([sys.executable,str(P/'Model.py'),str(P/'Inputs.json'),'--engine',str(ROOT),'--source',str(source.resolve()),'--outdir',str(dest)],env={**os.environ,'SPE_PENSION_MODE':mode},stdout=log,stderr=subprocess.STDOUT,check=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(one,MODES))
 subprocess.run([sys.executable,str(P/'Fiscal_Adapter.py'),'--macro',str(out/'macro'),'--outdir',str(out/'fiscal')],check=True)
 subprocess.run([sys.executable,str(P/'Results.py'),'--outdir',str(out)],check=True)
 subprocess.run([sys.executable,str(P/'Verify.py'),'--outdir',str(out)],check=True)
 subprocess.run([sys.executable,str(P/'Package.py'),'--source',str(out),'--outdir',str(out/'results')],check=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--outdir',type=Path,required=True);p.add_argument('--source',type=Path);a=p.parse_args();run(a.outdir,a.source)
