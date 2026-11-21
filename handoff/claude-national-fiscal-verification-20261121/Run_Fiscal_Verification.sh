#!/bin/bash
# Execution wrapper (log source). Macro inputs = Claude's own 4-mode re-run of the pension-corrected model (pr/, from the previous task).
W=/home/claude/v1121;T=$W/comb3/handoff/chatgpt-national-fiscal-closure-20261121
echo "== START $(date -u +%FT%TZ)"
echo "== [1] integrity: Manifest (48 files), Receipts (4 xlsx), Runtime_Pins (67)"
python3 -I - <<PY
import json,hashlib,pathlib,subprocess
T=pathlib.Path("$T");R=T.parents[1]
m=json.loads((T/'Manifest.json').read_text());bad=0
for x in m['files']:
    b=(T/x['path'].split('/')[-1]).read_bytes()
    if len(b)!=x['size'] or hashlib.sha256(b).hexdigest()!=x['sha256']:bad+=1
print('manifest files',len(m['files']),'mismatch',bad)
pins=json.loads((T/'Runtime_Pins.json').read_text());ok=miss=bad=0;S=pathlib.Path("$W/stage2")
for q in pins:
    p=R/q['path']
    if p.exists():b=p.read_bytes()
    elif 'claude-n3-pension-counterpart-verification' in q['path']:b=(S/q['path'].split('/')[-1]).read_bytes()
    else:
        try:b=subprocess.run(['git','-C',"$W/r",'show',q['commit']+':'+q['path']],capture_output=True,check=True).stdout
        except Exception:miss+=1;print('not retrievable',q['path']);continue
    if len(b)==q['size'] and hashlib.sha256(b).hexdigest()==q['sha256']:ok+=1
    else:bad+=1;print('PIN MISMATCH',q['path'])
print('pins',len(pins),'verified',ok,'not retrievable',miss,'mismatch',bad)
PY
echo "== [2] National_Fiscal.py x2 on Claude macro outputs"
rm -rf $W/nf1 $W/nf2 $W/nf3
python3 -B $T/National_Fiscal.py --macro $W/pr --outdir $W/nf1; python3 -B $T/National_Fiscal.py --macro $W/pr --outdir $W/nf2
echo "== [3] Build_Comparison.py"; cp -r $W/nf1 $W/nf3; python3 -B $T/Build_Comparison.py --outdir $W/nf3 --macro $W/pr
echo "== [4] byte comparison vs Work (20 CSV + 1 JSON)"
python3 -I - <<PY
import pathlib,hashlib,csv
T=pathlib.Path("$T");a=pathlib.Path("$W/nf3");b=pathlib.Path("$W/nf2");rows=[]
for f in sorted(a.iterdir()):
    x=f.read_bytes();t=(T/f.name).read_bytes()
    rows.append(dict(file=f.name,rerun_size=len(x),target_size=len(t),rerun_sha256=hashlib.sha256(x).hexdigest(),target_sha256=hashlib.sha256(t).hexdigest(),byte_identical=x==t,second_run_identical=(b/f.name).read_bytes()==x if (b/f.name).exists() else None))
with open("$W/nv/Fiscal_Byte_Comparison.csv",'w',newline='') as o:
    w=csv.DictWriter(o,list(rows[0].keys()),lineterminator='\n');w.writeheader();w.writerows(rows)
print('files',len(rows),'identical',sum(r['byte_identical'] for r in rows),'second-run identical',sum(1 for r in rows if r['second_run_identical']))
PY
echo "== [5] independent recompute"
python3 -I $W/out/Independent_Fiscal_Check.py $T $W/pr $W/comb3 $W/nf3 $W/nv | grep -E '"total"|"pass_"|"fail"|FAIL|recomputed|Break'
echo "== END $(date -u +%FT%TZ)"
