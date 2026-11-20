#!/usr/bin/env python3
"""Independent numerical/accounting checks and byte-identical CSV replay."""
import csv, hashlib, importlib.util, json, math, subprocess, sys, tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pension',P/'Model.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def near(a,b,abs_tol=1e-7):assert math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=abs_tol),(a,b)
def read(name):return list(csv.DictReader((P/name).open()))
checks=[]
# Hand-computed statutory examples: no adjustment, half excess, full suspension.
near(m.suspension(400000,150000,650000),0);near(m.suspension(550000,150000,650000),25000);near(m.suspension(1000000,150000,650000),150000)
near(m.income_tax(7000000,2026),974000*1.021);near(m.income_tax(0,2055),0)
near(m.pension_taxable(3500000),2350000)
near(m.remuneration_ceiling(2027),660000)
checks.append('Hand-calculated statutory examples and nonrefundable income tax')
annual=read('Annual.csv');paths={}
for r in annual:paths.setdefault(r['case'],[]).append(r)
assert len(paths)==30 and len(annual)==900
for name,rows in paths.items():
 assert [int(r['year']) for r in rows]==list(range(2026,2056))
 for r in rows:
  z=paths[r['backdrop']+'_ZERO'][int(r['year'])-2026]
  for k in ['population','foreign_jobs','foreign_resident_stock','foreign_effective_labor','legacy_elder_extra_jobs']:near(r[k],z[k])
  near(float(r['SQ_modeled_suspension_trn'])-float(r['F_modeled_suspension_trn']),float(r['direct_pension_relief_trn'])+float(r['behavior_pension_change_trn']))
  near(r['public_benefit_delta_trn'],float(r['direct_pension_relief_trn'])+float(r['behavior_pension_change_trn'])-float(r['legacy_overlap_removed_trn']))
  near(r['public_premium_delta_trn'],float(r['employee_premium_delta_trn'])+float(r['employer_premium_delta_trn']))
  near(r['extra_private_contribution_trn'],float(r['asset_transfer_trn'])+float(r['new_saving_from_contribution_trn']))
  for pol in ['SQ','F']:
   near(r[pol+'_balance_trn'],sum(float(r[pol+'_'+k+'_trn'])*sign for k,sign in [('previous',1),('return',1),('contribution',1),('payout',-1)]))
  assert r['national_pension_total_trn']==r['full_public_pension_balance_trn']==r['general_budget_transfer_delta_trn']==''
checks.append('All annual stock-flow, benefit, payer and unchanged foreign/population identities')
for r in read('Public_Strata.csv'):
 if r['age_group']!='65_69':near(r['premium_delta_trn'],0)
checks.append('No pension contribution assigned to workers aged70+')
for r in paths['MEDIUM_ALL_TRANSFER']:near(r['private_balance_minus_displaced_assets_trn'],0,abs_tol=1e-6)
for r in paths['MEDIUM_NO_PRIVATE_RESPONSE']:near(r['extra_private_balance_trn'],0)
for r in paths['MEDIUM_NO_BEHAVIOR']:near(r['additional_effective_labor'],0)
assert float(paths['MEDIUM_NEGATIVE_BEHAVIOR'][-1]['additional_jobs'])<0
assert float(paths['MEDIUM_TIGHTEN'][-1]['public_benefit_delta_trn'])<0
checks.append('Pure transfer cannot create net financial assets; no uptake/no labor/downside controls')
for row in read('Interactions.csv'):
 for key in ['real_gdp_trn','nominal_gdp_trn','elder_employed','labor_force_population_proxy','household_disposable_nominal_trn','household_consumption_nominal_proxy_trn','tax_diagnostic_trn','extended_expenditure_partial_trn','extended_fiscal_balance_partial_trn','public_benefit_delta_trn','public_premium_delta_trn','extra_private_balance_trn']:
  near(row[key+'_combined'],sum(float(row[key+'_'+s]) for s in ['public','private','interaction']))
checks.append('Independent factorial decomposition')
outputs=['Annual.csv','Comparison.csv','Summary.csv','Interactions.csv','Public_Strata.csv','Private_Distribution.csv','StatusQuo.csv','Validation.json']
with tempfile.TemporaryDirectory() as tmp:
 subprocess.run([sys.executable,str(P/'Model.py'),str(P/'Inputs.json'),'--outdir',tmp],check=True,capture_output=True)
 for name in outputs:assert (P/name).read_bytes()==(Path(tmp)/name).read_bytes(),name
checks.append('Fresh complete replay: all8 numerical outputs byte-identical')
for line in (P/'SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
checks.append('Local delivery SHA-256 manifest')
print(json.dumps(dict(status='PASS',checks=checks,case_count=len(paths),annual_rows=len(annual)),ensure_ascii=False,indent=2))
