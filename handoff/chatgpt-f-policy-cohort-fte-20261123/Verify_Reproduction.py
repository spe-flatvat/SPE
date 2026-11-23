"""Run all 12 paths again and compare every generated deliverable byte."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='spe_f_fte_') as temp:
 out=Path(temp)
 subprocess.run([sys.executable,str(P/'Recalculate.py'),str(out)],check=True)
 rows=[]
 for f in sorted(out.rglob('*')):
  if not f.is_file():continue
  other=P/f.relative_to(out);b=f.read_bytes();a=other.read_bytes()
  rows.append(dict(path=str(f.relative_to(out)),size=len(b),sha256=hashlib.sha256(b).hexdigest(),passed=a==b))
 result=dict(status='PASS' if all(r['passed'] for r in rows) else 'FAIL',new_byte_comparisons=len(rows),failed=sum(not r['passed'] for r in rows),files=rows)
 (P/'Reproduction_Verification.json').write_text(json.dumps(result,indent=2)+'\n')
 assert result['status']=='PASS'
 print(json.dumps({k:v for k,v in result.items() if k!='files'}))
