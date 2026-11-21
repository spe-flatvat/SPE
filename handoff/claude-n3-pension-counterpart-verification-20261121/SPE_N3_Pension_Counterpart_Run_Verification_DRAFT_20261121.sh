#!/bin/bash
# wrapper: independent recompute + byte comparison + log (run after run_pension.sh)
W=/home/claude/v1121;T=$W/comb2/handoff/chatgpt-n3-pension-counterpart-20261121;B=$W/comb/handoff/chatgpt-n3-gap-closure-20261121
echo "== START $(date -u +%FT%TZ)"
echo "== independent recompute"
python3 -I $W/out/SPE_N3_Pension_Counterpart_Independent_Recalc_DRAFT_20261121.py $T $B $W/pr $W/comb2 $W/prv
echo "== byte comparison: DOMESTIC rerun vs target; LEGACY rerun vs pre-correction"
python3 -I - <<PY
import hashlib,pathlib,csv
W=pathlib.Path("$W");rows=[]
for mode,ref in [('DOMESTIC_TRANSFER',pathlib.Path("$T")),('LEGACY',pathlib.Path("$B"))]:
    for f in sorted((W/'pr'/mode).iterdir()):
        t=ref/f.name;a=f.read_bytes();b=t.read_bytes() if t.exists() else None
        rows.append(dict(rerun_mode=mode,reference='target_76176ae1' if mode=='DOMESTIC_TRANSFER' else 'pre_correction_55695329',file=f.name,rerun_size=len(a),reference_size=None if b is None else len(b),rerun_sha256=hashlib.sha256(a).hexdigest(),reference_sha256=None if b is None else hashlib.sha256(b).hexdigest(),byte_identical=b is not None and a==b))
with open(W/'prv'/'SPE_N3_Pension_Counterpart_Byte_Comparison_DRAFT_20261121.csv','w',newline='') as o:
    w=csv.DictWriter(o,list(rows[0].keys()),lineterminator='\n');w.writeheader();w.writerows(rows)
for m in ('DOMESTIC_TRANSFER','LEGACY'):
    r=[x for x in rows if x['rerun_mode']==m];print(m,'files',len(r),'identical',sum(x['byte_identical'] for x in r),'differ:',[x['file'] for x in r if not x['byte_identical']])
PY
echo "== END $(date -u +%FT%TZ)"
