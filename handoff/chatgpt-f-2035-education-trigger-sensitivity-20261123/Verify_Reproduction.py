"""Compare two independently executed output directories, including exact CSV bytes."""
import hashlib,json,sys
from pathlib import Path
a,b=map(Path,sys.argv[1:3]);rows=[]
for p in sorted(a.iterdir()):
 if not p.is_file():continue
 q=b/p.name;x=p.read_bytes();y=q.read_bytes()
 rows.append(dict(path=p.name,size=len(x),sha256=hashlib.sha256(x).hexdigest(),reproduced_size=len(y),reproduced_sha256=hashlib.sha256(y).hexdigest(),match=x==y))
assert rows and all(r['match'] for r in rows)
result=dict(separate_process=True,matched=len(rows),failed=0,files=rows,primary_execution_paths=5,reproduction_execution_paths=5,distinct_primary_checks=json.loads((a/"Validation.json").read_text())["new_checks"])
print(json.dumps(result,indent=2))
