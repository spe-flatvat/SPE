#!/usr/bin/env python3
"""Replace fiscal satellite macro inputs only; retain all prior fiscal assumptions."""
import argparse,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def run(macro,out):
 old=ROOT/'handoff/chatgpt-national-fiscal-closure-20261121/National_Fiscal.py';s=old.read_text()
 needle='for mode in MODES:assert len(annual[mode])==2370';assert s.count(needle)==1
 s=s.replace(needle,"for mode in MODES:assert len(annual[mode])==30*(14+len(json.loads((PARITY/'Inputs.json').read_text())['cases']))")
 s=s.replace("'REEXECUTED_PINNED_79_CASE_MACRO'","'N3_PARITY_ANNUAL_BASE_ADAPTER_CANDIDATES'")
 ns={'__file__':str(old),'__name__':'pinned_national_fiscal_parity','PARITY':P};exec(compile(s,str(old),'exec'),ns);ns['main'](macro,out)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--macro',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.macro,a.outdir)
