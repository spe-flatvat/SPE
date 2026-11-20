#!/usr/bin/env python3
"""Accounting, policy boundary and replay checks, independent of model assertions."""
import base64,csv,hashlib,importlib.util,io,json,math,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('household',P/'Model.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def read(n):return list(csv.DictReader((P/n).open()))
def near(a,b,tol=2e-7):assert math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=tol),(a,b)
c=json.loads((P/'Inputs.json').read_text());s=c['defaults']
near(m.reduction(1000000,.35,s,1),.35);near(m.reduction(3500000,.35,s,1),.175);near(m.reduction(5000000,.35,s,1),0);near(m.reduction(5000001,.35,s,1),0)
assert m.close(sum(x['share'] for x in c['income_cells']),1.)
for qi in range(5):near(sum(x['share'] for x in c['income_cells'] if x['quintile']==qi),.2)
sources=json.loads((P/'Source_Integrity.json').read_text())
for src in sources['public_sources']:
 if 'original_bytes_base64' in src:
  raw=base64.b64decode(src['original_bytes_base64']);assert len(raw)==src['size'] and hashlib.sha256(raw).hexdigest()==src['sha256']
  if src['id']=='t153':
   rr=list(csv.reader(io.StringIO(raw.decode('cp932'))));v=next(r for r in rr if r and r[0].replace(' ','').replace('　','')=='社会保険料')
   assert [float(x)*10000 for x in v[-5:]]==c['stats']['observed_premium_total_yen']
paths={}
for r in read('Annual.csv'):paths.setdefault(r['case'],[]).append(r)
assert len(paths)==53
for n,rs in paths.items():
 assert [int(r['year']) for r in rs]==list(range(2026,2056))
 for i,r in enumerate(rs):
  original=paths[r['background']+'_OLD'][i]
  for k in ['population','foreign_jobs','elder_employed','labor_force_population_proxy']:near(r[k],original[k])
  near(r['government_balance_direct_trn'],float(r['tax_increase_trn'])-float(r['government_program_spending_trn']))
  near(float(r['government_balance_direct_trn'])+float(r['insurer_balance_direct_trn']),r['consolidated_balance_direct_trn'])
  near(r['premium_before_trn'],float(r['premium_after_trn'])+float(r['A_relief_trn'])+float(r['fund_relief_trn']))
  near(r['cash_DI_delta_trn'],float(r['HH_consumption_direct_delta_trn'])+float(r['HH_saving_direct_delta_trn']))
  near(r['B_face_trn'],sum(float(r[k]) for k in ['B_existing_overlap_removed_trn','B_nonclaimed_trn','B_supply_shortfall_trn','B_used_trn']))
  near(r['B_used_trn'],float(r['B_substitute_trn'])+float(r['B_new_service_trn']))
  if n.endswith('M2'):near(r['cash_DI_delta_trn'],0)
  if r['mode']!='LEGACY':near(r['consolidated_public_balance_vs_OFF_trn'],float(r['fiscal_balance_partial_trn'])-float(paths[r['background']+'_M0'][i]['fiscal_balance_partial_trn'])+float(r['insurer_balance_direct_trn']))
  assert r['national_gini']==''
income_sums={}
for r in read('Household_Income.csv'):
 v=income_sums.setdefault((r['case'],int(r['year'])),[0.,0.,0.])
 for j,k in enumerate(['cash_DI_delta_per_HH_yen','B_used_per_HH_yen','HH_consumption_delta_per_HH_yen']):v[j]+=float(r[k])*float(r['households'])/1e12
 near(r['cash_DI_delta_per_HH_yen'],float(r['A_per_HH_yen'])+float(r['fund_per_HH_yen'])+float(r['C_cash_per_HH_yen'])-float(r['tax_increase_per_HH_yen'])-float(r['local_tax_increase_per_HH_yen']),tol=.001)
 near(r['cash_DI_delta_per_HH_yen'],float(r['HH_consumption_delta_per_HH_yen'])+float(r['HH_saving_delta_per_HH_yen']),tol=.001)
 near(r['expanded_resources_delta_per_HH_yen'],float(r['cash_DI_delta_per_HH_yen'])+float(r['B_used_per_HH_yen']),tol=.001)
 near(r['living_burden_reduction_per_HH_yen'],float(r['cash_DI_delta_per_HH_yen'])+float(r['B_substitute_per_HH_yen']),tol=.001)
for (name,year),sums in income_sums.items():
 r=paths[name][year-2026]
 for k,v in zip(['cash_DI_delta_trn','B_used_trn','HH_consumption_direct_delta_trn'],sums):near(r[k],v)
for r in read('Triggers.csv'):
 if r['case'] in ['MM_FUND_ON','MM_BOTH_TRIGGERS','MM_FUND_AND_C_POOL'] and int(r['year'])>=2035:near(r['fund_income_trn'],float(r['VAT_lag_excess_reference_trn'])*.5)
 if r['case']=='MM_GINI_PP5' and int(r['year'])>=2035:near(r['maximum_relief_rate'],.4)
 if r['case']=='MM_GINI_REL5' and int(r['year'])>=2035:near(r['maximum_relief_rate'],.3675)
 if r['case']=='MM_GINI_AT_THRESHOLD':assert r['gini_triggered']=='0'
 if r['case']=='MM_FUND_AND_C_POOL':assert float(r['C_earmarked_funding_trn'])<=float(r['C_remaining_pool_trn'])+1e-8
for a,b in zip(paths['MM_M7'],paths['MM_BACKFILL_80']):
 near(a['consolidated_balance_direct_trn'],b['consolidated_balance_direct_trn']);near(a['cash_DI_delta_trn'],b['cash_DI_delta_trn'])
for a,b in zip(paths['MM_C_RECLASSIFY'],paths['MM_M3']):near(a['real_gdp_trn'],b['real_gdp_trn'])
for r in read('Interactions.csv'):
 for k in ['real_gdp_trn','nominal_gdp_trn','cash_DI_delta_trn','HH_consumption_direct_delta_trn','HH_saving_direct_delta_trn','B_used_trn','government_program_spending_trn','consolidated_balance_direct_trn','tax_diagnostic_trn','extended_government_balance_trn']:
  near(r[k+'_combined'],sum(float(r[k+'_'+a]) for a in ['A','B','C','AB_interaction','AC_interaction','BC_interaction','ABC_interaction']))
outputs=['Annual.csv','Household_Income.csv','Household_Detail.csv','Fiscal_Insurer.csv','Comparison.csv','Interactions.csv','Summary.csv','StatusQuo.csv','Triggers.csv','Validation.json']
with tempfile.TemporaryDirectory() as tmp:
 subprocess.run([sys.executable,str(P/'Model.py'),str(P/'Inputs.json'),'--outdir',tmp],check=True,capture_output=True)
 for n in outputs:assert (P/n).read_bytes()==(Path(tmp)/n).read_bytes(),n
for line in (P/'SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
print(json.dumps(dict(status='PASS',cases=len(paths),annual_rows=1590,byte_identical_replay_outputs=len(outputs),checks=['Nonuniform rate and threshold hand calculations','All government/insurer and household identities','No cash disposable increase from B alone','Household resource measures avoid double counting B','Fund50% and lag; PP vs relative; strict Gini threshold','Public backfill cannot change consolidated balance','Price reclassification cannot create extra cash/GDP','Full8-cell factorial decomposition','Unchanged labor/population and immutable dependencies','Byte-identical complete replay and SHA manifest']),ensure_ascii=False,indent=2))
