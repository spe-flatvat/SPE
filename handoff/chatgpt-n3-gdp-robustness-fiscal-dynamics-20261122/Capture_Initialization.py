#!/usr/bin/env python3
"""Extract only initialization required by unmodified native Components.step.
Run in a fresh Python process. Original dependency checks remain in effect.
"""
from pathlib import Path
import argparse,copy,json
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--workdir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=a.root.resolve()
f=root/'handoff/chatgpt-n3-policy-burden-diagnosis-20261122/N3_Policy_Burden_Diagnosis_Reproduce.py'
s=f.read_text().replace("records=[];seen=set();params={}","records=[];seen=set();params={};component_inputs={}")
s=s.replace("seen.add((cid,y));params[cid]=copy.deepcopy(v['p'])", "seen.add((cid,y));params[cid]=copy.deepcopy(v['p'])\n    if cid not in component_inputs:component_inputs[cid]=copy.deepcopy(dict(config=md.components.cfg,household=md.components.hh,pension=md.components.pen,s=md.s,deflators=md.deflators,trajectory=md.trajectory,elder=md.elder))")
s=s.replace("data=dict(parameters=params,records=records)","data=dict(parameters=params,records=records,component_inputs=component_inputs)")
ns={'__file__':str(f),'__name__':'capture_initialization'};exec(compile(s,str(f),'exec'),ns);ns['SELECT']=['SQ_COMMON_ON','PARITY_CONNECTED_CANDIDATE'];a.workdir.mkdir(parents=True,exist_ok=True)
d=ns['capture'](root,a.workdir.resolve(),a.source.resolve())['component_inputs']['PARITY_CONNECTED_CANDIDATE']
d['elder']=[{k:v for k,v in r.items() if k in ['65_69_male_population','65_69_female_population','70_74_male_population','70_74_female_population']} for r in d['elder']]
d['household']={k:d['household'][k] for k in ['stats','income_cells']};d['pension']={'public':{'strata':d['pension']['public']['strata']}}
a.output.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('INITIALIZATION_EXTRACTED',a.output.stat().st_size)
