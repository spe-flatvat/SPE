#!/usr/bin/env python3
# Claude integrity check of ff6210061615105de9a0d64767c256796be80ed2 (handoff/f-common-endoflife-finalization-20261121).
# Usage: python3 -I <this> <tree_root_of_fixed_commit> <replay_tree_root> <Delivery_Verification.json fetched from fixed record commit>
import sys, os, json, hashlib
R, RP, DVP = sys.argv[1:4]; F = 'handoff/f-common-endoflife-finalization-20261121'; sha = lambda b: hashlib.sha256(b).hexdigest()
M = json.load(open(os.path.join(R, F, 'Manifest.json')))
ok = sum(1 for x in M['files'] if (lambda b: len(b) == x['size'] and sha(b) == x['sha256'])(open(os.path.join(R, F, x['file']), 'rb').read()))
print('I1 Manifest entries %d, size+SHA-256 match %d (Manifest excludes Manifest.json and Delivery_Verification.json)' % (len(M['files']), ok))
dep = json.load(open(os.path.join(R, F, 'Inputs.json')))['runtime_dependencies']
okd = sum(1 for x in dep if (lambda b: len(b) == x['size'] and sha(b) == x['sha256'])(open(os.path.join(R, x['path']), 'rb').read()))
print('I2 runtime_dependencies %d, size+SHA-256 match %d' % (len(dep), okd))
files = sorted(f for f in os.listdir(os.path.join(R, F)) if os.path.isfile(os.path.join(R, F, f)))
print('I3 files physically in the fixed folder: %d (= %d Manifest entries + Manifest.json)' % (len(files), len(M['files'])))
same = [f for f in files if open(os.path.join(R, F, f), 'rb').read() == open(os.path.join(RP, F, f), 'rb').read()]
print('I4 replay (Model, CommonBaseline, Finalize, Verify --replay, ExtendedVerify, ReportResults) byte-identical files: %d of %d ; differing: %s' % (len(same), len(files), sorted(set(files) - set(same)) or 'none'))
dv = json.load(open(DVP)); d = {x['file']: x for x in dv['files']}
act = {f: open(os.path.join(R, F, f), 'rb').read() for f in files}
okv = sum(1 for f, b in act.items() if f in d and d[f]['size'] == len(b) and d[f]['sha256'] == sha(b))
print('I5 Delivery_Verification.json (record commit 6a9ccc85...): status %s, artifact_commit %s, entries %d, all MATCH %s, entries agreeing with my own bytes %d of %d' % (dv['status'], dv['artifact_commit'][:8], len(dv['files']), {x['result'] for x in dv['files']} == {'MATCH'}, okv, len(files)))
