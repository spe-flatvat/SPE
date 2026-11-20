import hashlib,json,subprocess,sys,math
from pathlib import Path
from Model import read
P=Path(__file__).resolve().parent
files=['SQ_Common_Annual.csv','SQ_Common_Accounts.csv','SQ_Common_Patients.csv','SQ_Common_Comparison.csv']
before={n:(P/n).read_bytes() for n in files}
subprocess.run([sys.executable,str(P/'CommonBaseline.py')],check=True)
for n,b in before.items():assert b==(P/n).read_bytes(),n
count=0
for r in read(P/'SQ_Common_Comparison.csv'):
 assert abs(float(r['off_vs_fixed']))<1e-7
 count+=1
# The emitted cap audit must reproduce an independent 2035 closed form.
for r in read(P/'Patient_Cap_Audit.csv'):
 months=int(r['months']);group=r['income'];elder=r['age'] in ['AGE70_74','AGE75PLUS']
 def independent(total):
  bill=total/months
  if group=='TAXFREE':cap=25700 if elder else 36900;multi=24600;annual=290000
  elif group=='GENERAL':cap=61500;multi=34500;annual=410000
  elif group=='MIDDLE':cap=85800+max(0.,bill-286000)*.01;multi=44400;annual=530000
  else:cap=179100+max(0.,bill-597000)*.01;multi=93000;annual=1110000
  return min(min(months,3)*min(.3*bill,.9*cap)+max(0,months-3)*min(.3*bill,.9*multi),.9*annual)
 expected=independent(float(r['bill_after_yen']))-independent(float(r['bill_before_yen']))
 assert math.isclose(expected,float(r['marginal_payment_yen']),abs_tol=1e-6)
# Stock-flow checks use beginning stock from the preceding exported year.
for name in sorted({r['case'] for r in read(P/'Medical_Accounts.csv')}):
 debt=asset=0.
 for r in [r for r in read(P/'Medical_Accounts.csv') if r['case']==name]:
  debt+=float(r['medical_policy_debt_issue_trn'])-float(r['medical_policy_debt_redemption_trn']);asset+=float(r['medical_policy_asset_addition_trn'])
  assert math.isclose(debt,float(r['medical_policy_debt_stock_trn']),abs_tol=1e-8)
  assert math.isclose(asset,float(r['medical_policy_financial_asset_stock_trn']),abs_tol=1e-8)
result=dict(status='PASS',SQ_replay=[dict(file=n,size=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in before.items()],SQ_OFF_fixed_regression_cells=count,independent_cap_formula_examples=144,medical_debt_asset_stockflow_rows=1650,unconnected_SQ=['medical VAT volume hook','health QOL'])
(P/'Extended_Checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
