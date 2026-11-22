#!/bin/bash
# Claude re-execution + independent verification of the N3 F-parity extension (read-only on the target).
# Layout (all fixed Commits fetched with git archive into W):
#   W/comb4  = F ff621006 final + N3 pins (as used for the 2026-11-21 checks) + fiscal-closure 74727367 + TARGET dir (37c3399f)
#   W/tgt    = TARGET commit 37c3399f9c553673a79ba1298fc68d758a77055e archive (handoff/chatgpt-n3-f-parity-implementation-20261122)
#   W/old79  = Claude's own earlier re-run of the 79-case pension-correction model (76176ae1), {mode}/
W=${W:-/home/claude/v1122}; R=$W/comb4; P=$R/handoff/chatgpt-n3-f-parity-implementation-20261122; T=$W/tgt/handoff/chatgpt-n3-f-parity-implementation-20261122
OLD79=${OLD79:-/home/claude/v1121/pr}; RR=${RR:-$W/rr2}; OUT=${OUT:-$W/out_final}
mkdir -p $RR/macro $OUT
echo "== START $(date -u +%FT%TZ) python=$(python3 --version 2>&1)"
echo "== 0. target Manifest.json: size / SHA-256 / git blob SHA-1 of every listed original vs the actual bytes of the fixed Commit"
python3 -I - <<PY
import json,hashlib,os,csv
T="$W/tgt/";d='handoff/chatgpt-n3-f-parity-implementation-20261122'
m=json.load(open(T+d+'/Manifest.json'));rows=[];listed=set()
for x in m['files']:
    p=T+x['path'];b=open(p,'rb').read() if os.path.exists(p) else None;listed.add(x['path'])
    h=hashlib.sha256(b).hexdigest() if b is not None else None;bl=hashlib.sha1(b'blob %d\0'%len(b)+b).hexdigest() if b is not None else None
    rows.append(dict(path=x['path'],manifest_size=x['size'],actual_size=None if b is None else len(b),actual_sha256=h,manifest_sha256_match=x['sha256']==h,blob_sha1_match=x['git_blob_sha']==bl,size_match=b is not None and x['size']==len(b)))
extra=[]
for r,_,fs in os.walk(T+d):
    for f in fs:
        q=os.path.relpath(os.path.join(r,f),T)
        if q not in listed:extra.append(q)
with open("$OUT/N3_F_Parity_Target_Manifest_Byte_Check_DRAFT_20261122.csv",'w',newline='') as o:
    w=csv.DictWriter(o,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print('manifest files',len(rows),'sha ok',sum(r['manifest_sha256_match'] for r in rows),'blob ok',sum(r['blob_sha1_match'] for r in rows),'size ok',sum(r['size_match'] for r in rows),'files in directory not in Manifest',extra,'listed total bytes',sum(r['manifest_size'] for r in rows))
PY
echo "== 1. Model.py re-execution (4 attribution modes x 103 cases x 30 years)"
run(){ M=$1; mkdir -p $RR/macro/$M; ( cd $R && SPE_PENSION_MODE=$M python3 -B $P/Model.py $P/Inputs.json --engine . --source . --outdir $RR/macro/$M ) > $RR/${M}_Execution.log 2>&1; echo "   $M rc=$? $(date -u +%FT%TZ)"; }
run DOMESTIC_TRANSFER & run LEGACY & wait
run FOREIGN_INCOME & run ADDITIONAL_VA & wait
echo "== 2. Fiscal_Adapter.py / Results.py / Package.py (re-run for byte comparison only)"
( cd $P && python3 -B Fiscal_Adapter.py --macro $RR/macro --outdir $RR/fiscal && python3 -B Results.py --outdir $RR && cp $T/results/Verification.json $T/results/Verification.log $RR/ && python3 -B Package.py --source $RR --outdir $RR/results ) 2>&1 | tail -n 4
echo "== 3. byte comparison of re-run packaged results vs delivered results/"
python3 -I - <<PY
import hashlib,csv,os
T="$T/results/";R="$RR/results/";rows=[]
for f in sorted(os.listdir(T)):
    ba=open(R+f,'rb').read() if os.path.exists(R+f) else None;bb=open(T+f,'rb').read()
    trivial = f in ('Verification.json','Verification.log')   # copied from the target before packaging: not an independent comparison
    rows.append(dict(file=f,rerun_size=None if ba is None else len(ba),target_size=len(bb),rerun_sha256=None if ba is None else hashlib.sha256(ba).hexdigest(),target_sha256=hashlib.sha256(bb).hexdigest(),byte_identical=ba==bb,comparison_kind='COPIED_FROM_TARGET_NOT_INDEPENDENT' if trivial else ('LOG_OR_ENV_FILE' if f.endswith('.log') or f=='Execution_Metadata.json' else 'DATA_FILE')))
with open("$OUT/N3_F_Parity_Results_Byte_Comparison_DRAFT_20261122.csv",'w',newline='') as o:
    w=csv.DictWriter(o,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
d=[r for r in rows if r['comparison_kind']=='DATA_FILE']
print('delivered files',len(rows),'data files',len(d),'data files byte-identical',sum(r['byte_identical'] for r in d))
for r in rows:
    if not r['byte_identical']:print('  differs:',r['file'],r['comparison_kind'],r['rerun_size'],r['target_size'])
PY
echo "== 4. independent macro verification (own code; no import of Work code)"
python3 -I $W/out/SPE_N3_F_Parity_Independent_Recalc_DRAFT_20261122.py $T $RR/macro $OLD79 $R $OUT
echo "== 5. independent fiscal recomputation (own code)"
python3 -I $W/out/SPE_N3_F_Parity_Independent_Fiscal_Check_DRAFT_20261122.py $R/handoff/chatgpt-national-fiscal-closure-20261121 $RR/fiscal $RR/macro $R $OUT
echo "== END $(date -u +%FT%TZ)"
