#!/usr/bin/env python3
"""Run from an ordinary git clone of spe-flatvat/SPE; stdlib + git, no ZIP.
python handoff/chatgpt-n3-gap-closure-20261121/Reproduce.py --outdir /tmp/n3-gap
Only reads tracked originals. Writes output and a detached source worktree in tmp.
"""
import argparse,subprocess,tempfile,sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def main(out):
 with tempfile.TemporaryDirectory(prefix='spe_n3_source_') as tmp:
  source=Path(tmp)/'source';commit='3c77eafc2073fdaba4c129164817d2f57c9421b9'
  if subprocess.run(['git','cat-file','-e',commit],cwd=ROOT,capture_output=True).returncode:
   subprocess.run(['git','fetch','origin',commit],cwd=ROOT,check=True)
  subprocess.run(['git','worktree','add','--detach',str(source),commit],cwd=ROOT,check=True)
  try:
   subprocess.run([sys.executable,str(P/'Gap_Model.py'),str(P/'Gap_Inputs.json'),'--engine',str(ROOT),'--source',str(source),'--outdir',str(out)],cwd=ROOT,check=True)
   subprocess.run([sys.executable,str(P/'Build_Results.py'),'--outdir',str(out)],cwd=ROOT,check=True)
   subprocess.run([sys.executable,str(P/'Verify.py'),'--outdir',str(out)],cwd=ROOT,check=True)
  finally:subprocess.run(['git','worktree','remove',str(source)],cwd=ROOT,check=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);main(ap.parse_args().outdir.resolve())
