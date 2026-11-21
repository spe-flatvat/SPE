#!/bin/bash
# Execution wrapper used for the Claude independent verification (log source). Paths are arguments-free: edit WORK below.
set -u
W=/home/claude/v1121
P=$W/comb/handoff/chatgpt-n3-gap-closure-20261121
echo "== START $(date -u +%FT%TZ)"
echo "== python $(python3 --version 2>&1)"
echo "== [1] fixed-input integrity: Manifest.json (38 files) + Dependency_Pins.json (9 pins) vs actual bytes"
python3 -I - <<PY
import json,hashlib,pathlib
P=pathlib.Path("$P");R=P.parents[1]
m=json.loads((P/'Manifest.json').read_text());bad=0
for x in m['files']:
    b=(R/x['path']).read_bytes()
    if len(b)!=x['size'] or hashlib.sha256(b).hexdigest()!=x['sha256']:bad+=1;print('MISMATCH',x['path'])
print('manifest files',len(m['files']),'mismatch',bad)
bad=0;pins=json.loads((P/'Dependency_Pins.json').read_text())
for q in pins:
    b=(R/q['path']).read_bytes()
    if len(b)!=q['size'] or hashlib.sha256(b).hexdigest()!=q['sha256']:bad+=1;print('PIN MISMATCH',q['path'])
print('pins',len(pins),'mismatch',bad)
PY
echo "== [2] re-run Gap_Model.py (79 cases) into fresh outdir"
( cd $W/comb && time python3 -B $P/Gap_Model.py $P/Gap_Inputs.json --engine . --source . --outdir $W/replay2 ) 2>&1 | tail -6
echo "== [3] Build_Results.py"
python3 -B $P/Build_Results.py --outdir $W/replay2
echo "== [4] Work Verify.py (reference only, not counted as independent)"
python3 -B $P/Verify.py --outdir $W/replay2 2>&1 | tail -18
echo "== [5] Claude independent recompute (own code)"
python3 -I $W/out/SPE_N3_Gap_Independent_Recalc_DRAFT_20261121.py $P $W/replay2 $W/comb $W/run2 2>&1 | tail -45
echo "== [6] byte comparison replay2 vs fixed target outputs"
python3 -I - <<PY
import hashlib,pathlib,csv
P=pathlib.Path("$P");R=pathlib.Path("$W/replay2");rows=[]
for f in sorted(R.iterdir()):
    t=P/f.name
    a=f.read_bytes();b=t.read_bytes() if t.exists() else None
    rows.append(dict(file=f.name,replay_size=len(a),target_size=None if b is None else len(b),replay_sha256=hashlib.sha256(a).hexdigest(),target_sha256=None if b is None else hashlib.sha256(b).hexdigest(),byte_identical=b is not None and a==b))
    print(('SAME ' if rows[-1]['byte_identical'] else 'DIFF ')+f.name)
with open("$W/run2/SPE_N3_Gap_Byte_Comparison_DRAFT_20261121.csv",'w',newline='') as o:
    w=csv.DictWriter(o,list(rows[0].keys()),lineterminator='\n');w.writeheader();w.writerows(rows)
print('files',len(rows),'identical',sum(r['byte_identical'] for r in rows))
PY
echo "== [7] second pass: independent recompute against Work's own delivered outputs (not the replay)"
mkdir -p $W/run3 && python3 -I $W/out/SPE_N3_Gap_Independent_Recalc_DRAFT_20261121.py $P $P $W/comb $W/run3 2>&1 | grep -E '"total"|"pass_"|"fail"|FAIL' | head
cmp $W/run2/SPE_N3_Gap_Independent_Numeric_Comparison_DRAFT_20261121.csv $W/run3/SPE_N3_Gap_Independent_Numeric_Comparison_DRAFT_20261121.csv && echo "replay-based and delivered-output-based comparison CSV identical"
echo "== END $(date -u +%FT%TZ)"
