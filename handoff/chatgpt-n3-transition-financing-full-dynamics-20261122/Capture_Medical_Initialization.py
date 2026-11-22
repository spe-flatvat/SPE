#!/usr/bin/env python3
from pathlib import Path
import argparse,copy,json,subprocess
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--workdir',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=a.root.resolve();a.workdir.mkdir(parents=True,exist_ok=True)
f=root/'handoff/chatgpt-n3-policy-burden-diagnosis-20261122/N3_Policy_Burden_Diagnosis_Reproduce.py';s=f.read_text().replace('records=[];seen=set();params={}','records=[];seen=set();params={};medical_inputs={}')
s=s.replace("seen.add((cid,y));params[cid]=copy.deepcopy(v['p'])", "seen.add((cid,y));params[cid]=copy.deepcopy(v['p'])\n    if cid not in medical_inputs:medical_inputs[cid]=copy.deepcopy(dict(c=md.c,s=md.s,deflators=md.deflators,population=md.population,trajectory=md.trajectory,elder=md.elder))")
s=s.replace('data=dict(parameters=params,records=records)','data=dict(parameters=params,records=records,medical_inputs=medical_inputs)')
ns={'__file__':str(f),'__name__':'medical_initialization_capture'};exec(compile(s,str(f),'exec'),ns);ns['SELECT']=['SQ_COMMON_ON','PARITY_CONNECTED_CANDIDATE']
d=ns['capture'](root,a.workdir.resolve(),a.source.resolve())['medical_inputs']['PARITY_CONNECTED_CANDIDATE'];a.output.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print('MEDICAL_INITIALIZATION_CAPTURED',a.output.stat().st_size)
