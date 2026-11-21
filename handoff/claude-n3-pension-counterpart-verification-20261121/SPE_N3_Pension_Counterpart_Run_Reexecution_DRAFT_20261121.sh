#!/bin/bash
W=/home/claude/v1121;P=$W/comb2/handoff/chatgpt-n3-pension-counterpart-20261121
echo "== START $(date -u +%FT%TZ)"
for M in DOMESTIC_TRANSFER LEGACY FOREIGN_INCOME ADDITIONAL_VA; do
 mkdir -p $W/pr/$M
 echo "== [$M] Gap_Model.py"; ( cd $W/comb2 && time SPE_PENSION_MODE=$M python3 -B $P/Gap_Model.py $P/Gap_Inputs.json --engine . --source . --outdir $W/pr/$M ) 2>&1 | tail -5
 echo "== [$M] Build_Results.py"; SPE_PENSION_MODE=$M python3 -B $P/Build_Results.py --outdir $W/pr/$M
done
echo "== END $(date -u +%FT%TZ)"
