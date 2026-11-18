# Expands tx_inputs.json and old_tx.csv from the model's Inputs.json without changing any value.
# Usage: python3 -I <this> <Inputs.json> <outdir>
import sys, json, zlib, base64, os
c = json.load(open(sys.argv[1], encoding='utf-8')); o = sys.argv[2]; os.makedirs(o, exist_ok=True)
json.dump(c['tx_inputs'], open(os.path.join(o, 'tx_inputs.json'), 'w', encoding='utf-8'), ensure_ascii=False)
open(os.path.join(o, 'old_tx.csv'), 'w', encoding='utf-8').write(zlib.decompress(base64.b64decode(c['old_tx_csv_zlib_base64'])).decode())
