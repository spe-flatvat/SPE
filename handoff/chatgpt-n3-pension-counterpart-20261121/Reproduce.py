#!/usr/bin/env python3
"""Python stdlib + git. Writes only requested output and temporary worktrees."""
import argparse,subprocess,tempfile,sys,os,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def run(out):
 out=out.resolve();out.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='spe_pension_') as tmp:
  tmp=Path(tmp);source=tmp/'source';commit='3c77eafc2073fdaba4c129164817d2f57c9421b9'
  if subprocess.run(['git','cat-file','-e',commit],cwd=ROOT,capture_output=True).returncode:subprocess.run(['git','fetch','origin',commit],cwd=ROOT,check=True)
  subprocess.run(['git','worktree','add','--detach',str(source),commit],cwd=ROOT,check=True)
  try:
   def one(mode,dest,log):
    dest.mkdir(parents=True,exist_ok=True)
    with log.open('w') as f:
     subprocess.run([sys.executable,str(P/'Gap_Model.py'),str(P/'Gap_Inputs.json'),'--engine',str(ROOT),'--source',str(source),'--outdir',str(dest)],env={**os.environ,'SPE_PENSION_MODE':mode},stdout=f,stderr=subprocess.STDOUT,check=True)
     subprocess.run([sys.executable,str(P/'Build_Results.py'),'--outdir',str(dest)],stdout=f,stderr=subprocess.STDOUT,check=True)
   one('DOMESTIC_TRANSFER',out,out/'Execution.log')
   for mode in ['LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']:one(mode,tmp/mode,out/(mode+'_Execution.log'))
   one('DOMESTIC_TRANSFER',tmp/'replay',out/'Replay.log')
   subprocess.run([sys.executable,str(P/'Verify.py'),'--outdir',str(out),'--replay',str(tmp/'replay')],check=True)
   subprocess.run([sys.executable,str(P/'Evaluate.py'),'--outdir',str(out),'--sens',str(tmp),'--replay',str(tmp/'replay')],check=True)
  finally:subprocess.run(['git','worktree','remove',str(source)],cwd=ROOT,check=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);run(ap.parse_args().outdir)
