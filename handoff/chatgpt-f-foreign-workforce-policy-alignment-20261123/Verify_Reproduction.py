"""Separate-process regeneration and exact byte comparison."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='spe_foreign_reproduction_') as td:
 out=Path(td);subprocess.run([sys.executable,str(P/'Recalculate.py'),str(out)],check=True)
 rows=[]
 for f in sorted(out.rglob('*')):
  if f.is_file():
   b=f.read_bytes();a=(P/f.relative_to(out)).read_bytes();rows.append(dict(path=str(f.relative_to(out)),size=len(b),sha256=hashlib.sha256(b).hexdigest(),passed=a==b))
 result=dict(status='PASS' if all(r['passed'] for r in rows) else 'FAIL',new_byte_comparisons=len(rows),failed=sum(not r['passed'] for r in rows),files=rows)
 (P/'Reproduction_Verification.json').write_text(json.dumps(result,indent=2)+'\n');assert result['status']=='PASS'
 print(json.dumps({k:v for k,v in result.items() if k!='files'}))
