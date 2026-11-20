#!/usr/bin/env python3
"""Integration-specific accounting and counterfactual checks, plus fresh replay."""
import csv,hashlib,json,math,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
def rows(n):return list(csv.DictReader((P/n).open()))
def num(r,k):return float(r[k])
def eq(a,b):assert math.isclose(a,b,abs_tol=2e-7,rel_tol=3e-10),(a,b)
a={(r['case'],int(r['year'])):r for r in rows('Annual.csv')}
f=rows('Fiscal.csv');h=rows('Household.csv');income=rows('Income_Groups.csv');checks=[]
for r in f:
 eq(num(r,'government_partial_balance_proxy_trn')+num(r,'insurer_known_change_and_program_balance_trn'),num(r,'consolidated_partial_balance_proxy_trn'))
 eq(num(r,'government_to_insurer_transfer_trn'),num(r,'insurer_transfer_receipt_trn'))
 eq(num(r,'internal_transfer_consolidated_trn'),0.)
 assert all(r[k]=='' for k in ['actual_bonds_trn','PB_trn','national_consolidated_balance_trn','national_SI_receipts_trn','national_pension_total_trn'])
 if r['case']=='SQ_CURRENT':continue
 eq(sum(num(r,k) for k in ['elder_contribution_delta_trn','foreign_contribution_delta_trn','pension_reform_contribution_delta_trn']),num(r,'modeled_gross_contribution_delta_trn'))
 eq(num(r,'legacy_tax_diagnostic_trn'),num(r,'VAT_total_reference_trn')+num(r,'tax_residual_after_VAT_trn'))
checks+=['government/insurer transfer cancellation and subtotal','known SI components once','VAT satellite not added to macro tax a second time','national fiscal totals and bonds/PB blank']
for r in h:
 eq(num(r,'macro_resource_income_proxy_trn')-num(r,'price_benefit_trn'),num(r,'macro_cash_DI_proxy_trn'))
 eq(num(r,'AB_C_cash_delta_trn'),num(r,'AB_C_direct_consumption_delta_trn')+num(r,'AB_C_direct_saving_delta_trn'))
 eq(num(r,'macro_cash_DI_proxy_trn')-num(r,'synthetic_micro_DI_after_trn'),num(r,'macro_minus_micro_cash_proxy_gap_trn'))
 group=[z for z in income if z['case']==r['case'] and z['year']==r['year']]
 eq(sum(num(z,'cash_DI_after_per_HH_yen')*num(z,'households') for z in group)/1e12,num(r,'synthetic_micro_DI_after_trn'))
 assert r['pension_labor_allocation_to_micro_groups_trn']==''
checks+=['cash-price-kind separation','direct household saving identity','weighted income-grid aggregation with explicit unmatched macro gap']
for y in range(2026,2056):
 direct=a['FULL_DIRECT',y];display=a['FULL_RECLASSIFY',y];pool=a['FULL_POOL',y]
 eq(num(direct,'real_gdp_trn'),num(display,'real_gdp_trn'));eq(num(display,'C_cash_trn'),0.)
 eq(num(pool,'C_cash_trn'),num(pool,'C_earmarked_funding_trn'))
 for name in ['FULL_ADDITIONAL','FULL_POOL','FULL_RECLASSIFY','FULL_OLD_C','FULL_LOW','FULL_HIGH']:
  r=a[name,y]
  for k in ['population','foreign_jobs','elder_employed','labor_force_population_proxy']:eq(num(r,k),num(direct,k))
 # Hand accounting test: the newly connected employee cost has a one-half share
 # of the precomputed foreign pension contribution. Employer cash also pays its
 # share and the previously satellite-only employer integration programme cost.
 old=a['REPLAY_DIRECT',y]
 eq(num(direct,'household_policy_cash_nominal_trn')-num(old,'household_policy_cash_nominal_trn'),-.5*num(direct,'foreign_contribution_delta_trn'))
 eq(num(direct,'corporate_cash_change_trn')-num(old,'corporate_cash_change_trn'),-.5*num(direct,'foreign_contribution_delta_trn')-num(direct,'foreign_employer_cost_trn'))
 if y==2026:
  for name in ['FULL_DIRECT','FULL_ADDITIONAL','FULL_LOW','FULL_HIGH','SQ_CURRENT']:eq(num(a[name,y],'real_gdp_trn'),580.)
checks+=['C display-only no new cash/GDP','resource-limited C constraint','unchanged labour and population across C/price sensitivities','foreign employee/employer cash links match existing half-share amounts','2026 common GDP anchor']
for r in rows('Interactions.csv'):eq(num(r,'integrated_effect'),num(r,'sum_of_singles')+num(r,'interaction'))
checks+=['single vs integrated policy effect identity and calculated interactions']
replayed=[]
with tempfile.TemporaryDirectory(prefix='spe_integration_') as td:
 subprocess.run([sys.executable,str(P/'Model.py'),str(P/'Inputs.json'),'--outdir',td],check=True,stdout=subprocess.DEVNULL)
 for p in sorted(Path(td).iterdir()):
  b=p.read_bytes();assert b==(P/p.name).read_bytes(),p.name
  replayed.append(dict(file=p.name,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
checks+=['fresh numerical replay exact-byte match']
print(json.dumps(dict(status='PASS',checks=checks,replayed_outputs=replayed),ensure_ascii=False,indent=2))
