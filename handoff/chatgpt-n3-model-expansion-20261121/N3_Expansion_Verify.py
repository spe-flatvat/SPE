#!/usr/bin/env python3
"""Changed-component tests plus old14-case regression; no repeat independent review."""
import argparse,csv,json,math,sys,subprocess,tempfile,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
from N3_Components import eligible_firm,relief,foreign_screen,institutions
P=Path(__file__).resolve().parent
read=lambda p:list(csv.DictReader(Path(p).open()))
def near(a,b):assert math.isclose(float(a),float(b),abs_tol=2e-7,rel_tol=2e-9),(a,b)
def run(source,engine,replay):
 cfg=json.loads((P/'N3_Expansion_Inputs.json').read_text());A=read(P/'N3_Expansion_Annual.csv');C=read(P/'N3_Expansion_Common.csv');by={(r['case'],int(r['year'])):r for r in A};tests={};old=Path(source)/'handoff/claude-n3-model-draft-20261121';cells=0
 assert len(A)==(14+len(cfg['cases']))*30 and len({r['case'] for r in A})==14+len(cfg['cases'])
 for suffix,new in [('Annual','N3_Expansion_Annual.csv'),('Common','N3_Expansion_Common.csv'),('vs_SQ_Common_On','N3_Expansion_Comparison.csv')]:
  original=read(old/('SPE_N3_Medical_'+suffix+'_DRAFT_20261121.csv'));fresh={(r['case'],r['year']):r for r in read(P/new)}
  for r in original:
   n=fresh[r['case'],r['year']]
   for k,v in r.items():
    if v=='':continue # Formerly missing proxy columns are filled separately.
    try:float(v)
    except ValueError:assert v==n[k],(suffix,k,v,n[k])
    else:near(v,n[k]);cells+=1
 tests['old14_case_numeric_regression_cells']=cells
 fixed=read(Path(engine)/'handoff/f-common-endoflife-finalization-20261121/SQ_Common_Annual.csv');rf={(r['case'],int(r['year'])):r for r in fixed}
 for y in range(2026,2056):
  for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn']:
   near(by['SQ_COMMON_ON',y][k],rf['SQ_COMMON_ON',y][k])
 tests['fixed_SQ_ON_regression_cells']=180
 for r in C:
  assert float(r['resource_units_used'])<=float(r['transition_capacity'])+1e-6
  near(float(r['chosen_transitions'])+float(r['universal_palliative_served'])-float(r['overlap_patients']),r['unique_patients_served'])
  for k in ['registration_changes_benefits','registration_changes_copay','registration_changes_palliative_priority','unknown_wish_assumed_refusal','treatment_automatically_stopped','active_life_termination']:near(r[k],0)
 tests['common_protection_capacity_rows']=len(C)
 for r in A:
  near(float(r['patient_payment_delta_trn'])+float(r['public_clinical_payment_delta_trn'])+float(r['insurer_clinical_payment_delta_trn']),r['clinical_cost_delta_trn'])
  near(float(r['medical_only_household_cash_delta_trn'])+float(r['policy_household_cash_delta_trn']),r['household_cash_delta_trn'])
  near(float(r['medical_only_government_cost_delta_trn'])+float(r['policy_government_cost_delta_trn']),r['government_cost_delta_trn'])
  near(float(r['medical_financing_direct_tax_trn'])+float(r['policy_tax_delta_trn']),r['engine_direct_tax_delta_trn'])
  near(float(r['policy_government_cost_delta_trn'])-float(r['policy_insurer_cash_delta_trn'])-float(r['policy_tax_delta_trn']),r['policy_budget_unclosed_trn'])
  for k in ['national_PB_trn','national_debt_trn','national_bond_issue_trn','inheritance40_tax_trn']:assert r[k]==''
 tests['claim_and_separate_medical_policy_accounts']=len(A)
 # Independent cap crossing checks for the two genuinely distinct interpolations.
 def current(age,g):return .2 if age=='PRESCHOOL' else (.2 if age=='AGE70_74' else .1) if age in ['AGE70_74','AGE75PLUS'] and g in ['TAXFREE','GENERAL'] else .3
 def claim(age,g,bill,months,coins):
  elder=age in ['AGE70_74','AGE75PLUS']
  if g=='TAXFREE':cap=25700 if elder else 36900;multi=24600;annual=290000
  elif g=='GENERAL':cap=61500;multi=34500;annual=410000
  elif g=='MIDDLE':cap=85800+max(0,bill-286000)*.01;multi=44400;annual=530000
  else:cap=179100+max(0,bill-597000)*.01;multi=93000;annual=1110000
  return min(min(months,3)*min(coins*bill,cap)+max(months-3,0)*min(coins*bill,multi),annual)
 audit=read(P/'N3_Claim_Candidate_Audit.csv')
 for r in audit:
  age=r['age'];g=r['income'];bill=float(r['bill_yen']);months=int(r['months']);ph=float(r['phase']);base=current(age,g)
  expected=claim(age,g,bill,months,base+(.5-base)*ph) if r['mode']=='RATE' else (1-ph)*claim(age,g,bill,months,base)+ph*claim(age,g,bill,months,.5)
  near(expected,r['actual_paid_yen'])
 assert any(abs(float(by['MED_RATE_INTERPOLATION',y]['patient_payment_delta_trn'])-float(by['N3_MED_50_CAP_SAME',y]['patient_payment_delta_trn']))>1e-6 for y in range(2033,2038))
 near(by['MED_RATE_INTERPOLATION',2055]['patient_payment_delta_trn'],by['N3_MED_50_CAP_SAME',2055]['patient_payment_delta_trn'])
 tests['new_interpolation_independent_claim_boundaries']=len(audit)
 firm=read(P/'N3_Corporate_Accounts.csv')
 for r in firm:
  den=float(r['profit_base_trn']) if r['investment_denominator']=='PROFIT' else float(r['revenue_base_trn']);qualified=float(r['payout_ratio'])>=.60 and float(r['investment_base_trn'])/den>=.20
  assert (r['AND_qualified']=='True')==qualified
  saving=-float(r['corporate_tax_delta_trn']);near(saving,float(r['investment_delta_trn'])+float(r['dividend_delta_trn'])+float(r['retained_delta_trn']))
  near(float(r['dividend_delta_trn'])*.2,r['financial_tax_on_dividend_delta_trn'])
 for p,i,expected in [(.60,.20,True),(.59,.30,False),(.70,.19,False),(.59,.19,False)]:assert eligible_firm(p,i,1,10,'PROFIT')==expected
 assert eligible_firm(.7,1,1,10,'OPEN') is None
 tests['corporate_AND_allocation_rows']=len(firm)
 pension=read(P/'N3_Pension_Accounts.csv');previous={}
 for r in pension:
  cid=r['case'];begin=float(r['fund_begin_trn']);end=float(r['fund_end_trn']);near(begin,previous.get(cid,0));previous[cid]=end
  near(end,begin+float(r['fund_contribution_trn'])+float(r['fund_return_trn'])-float(r['fund_payout_trn']))
  near(r['public_cash_cost_delta_trn'],float(r['public_benefit_delta_trn'])+float(r['diverted_existing_contribution_trn']))
  near(float(r['government_cash_cost_delta_trn'])-float(r['public_insurer_cash_delta_trn']),r['public_cash_cost_delta_trn'])
  if int(r['year'])<int(r['protected_cohort_start']):near(r['delayed_recipients_candidate'],0)
 assert float(by['PENSION75_RETURN4',2055]['pension_fund_stock_trn'])>float(by['PENSION75_RETURN0',2055]['pension_fund_stock_trn'])
 tests['pension_stockflow_and_rights_rows']=len(pension)
 hh=read(P/'N3_Income_Distribution.csv')
 for r in hh:
  spec=next((z for z in cfg['cases'] if z['id']==r['case']),{});active=max(0,min(1,(int(r['year'])-spec.get('household_start',2033)+1)/spec.get('household_ramp',6)))
  flatcase=bool(spec.get('flat_hh'))
  if flatcase:
   expected=(float(r['labour_business_30_gross_base_trn'])*.30+float(r['financial20_gross_base_trn'])*.20-float(r['baseline_allocated_national_tax_trn']))*active
   near(expected,r['flat_tax_delta_trn'])
  else:near(r['flat_tax_delta_trn'],0)
  near(float(r['new_cash_DI_proxy_yen'])-float(r['baseline_DI_proxy_yen'])+float(r['service_expense_avoidance_yen']),float(r['cash_delta_trn'])*1e12/float(r['households']))
  if float(r['income_yen'])>5000000:near(r['premium_saved_trn'],0);near(r['in_kind_trn'],0)
  near(float(r['premium_saved_trn'])+.7*float(r['in_kind_trn'])-float(r['flat_tax_delta_trn'])-float(r['EITC_removal_trn']),r['cash_delta_trn'])
 for inc in [1999999,2000000,4999999,5000000,5000001]:assert 0<=relief(inc,5000000,.35)<=.35
 assert relief(5000001,5000000,.35)==0 and relief(5000000,5000000,.35)==0
 tests['household_threshold_cash_rows']=len(hh)
 assert float(by['FLAT_RELIEF_PHASE1_2030',2030]['policy_tax_delta_trn'])>0
 near(by['FLAT_RELIEF_PHASE1_2030',2029]['policy_tax_delta_trn'],0)
 tests['phase1_household_timing_candidates']=True
 for y in range(2026,2056):
  near(by['PUBLIC_REGULARIZE100K',y]['public_added_jobs'],0)
 assert float(by['PUBLIC_ADD100K',2055]['public_added_jobs'])>0
 tests['employment_regularize_vs_new_jobs']=True
 assert foreign_screen(10000,None,None,.8,[.25]*4)['accepted'] is None
 assert foreign_screen(10000,.04,'EXTERNAL',.8,[.25]*4)['accepted']==8000
 assert foreign_screen(10000,.06,'EXTERNAL',.8,[.25]*4)['accepted']==0
 assert institutions(10,[dict(id='X',density=1,productivity=1,cost=1)],invoice_hours=2,hour_cost=3000)['invoice_saving_yen']==6000
 assert institutions(15,[],growth=-1,threshold=0)['freeze'] is True
 for blocks in [9,16]:
  try:institutions(blocks,[])
  except AssertionError:pass
  else:raise AssertionError('invalid block count accepted')
 structures=read(P/'N3_Structural_Interfaces.csv')
 for r in structures:assert r['foreign_macro_connected']=='False' and 10<=int(r['coop_blocks'])<=15
 kpi=[r for r in structures if r['case']=='VAT_KPI_CANDIDATE'];frozen=False
 for r in kpi:
  if r['kpi_freeze_candidate']=='True':frozen=True
  if frozen:assert r['kpi_freeze_candidate']=='True'
 tests['institution_and_foreign_interfaces']=dict(executed_annual_rows=len(structures),foreign_population='OPEN_not_converted_from_GDP_ratio',KPI_freeze_latched=frozen)
 Q=read(P/'N3_VAT_Regular_Quantity.csv')
 assert any(r['case']=='VAT_ELASTIC_025' and float(r['quantity'])<.999 for r in Q)
 for r in Q:
  # General transaction identity for regular output VAT at actual quantity.
  base=float(r['base']);q=float(r['quantity']);oldVAT=float(r['old_VAT']);near(float(r['VAT'])-oldVAT,float(r['rate_effect'])+float(r['pass_quantity_residual']))
  assert .7-1e-9<=q<=1.3+1e-9
 assert float(by['VAT_ELASTIC_075',2055]['modeled_VAT_trn'])<float(by['N3_VAT_PATH_ONLY',2055]['modeled_VAT_trn'])
 tests['VAT_quantity_response_rows']=len(Q)
 engine_accounts=read(P/'N3_Engine_Accounts.csv')
 for r in engine_accounts:
  z=by[r['case'],int(r['year'])]
  near(float(r['tax_macro_trn'])+float(z['VAT_delta_vs_fixed_reference_trn'])+float(z['engine_direct_tax_delta_trn']),z['tax_diagnostic_trn'])
 tests['VAT_and_policy_tax_once_only_rows']=len(engine_accounts)
 # Re-run generated outputs once; previous independent medical/VAT audit reused.
 deterministic=[]
 if replay:
  with tempfile.TemporaryDirectory(prefix='spe-n3-expanded-replay-') as td:
   cmd=[sys.executable,str(P/'N3_Expansion_Model.py'),str(P/'N3_Expansion_Inputs.json'),'--engine',str(engine),'--source',str(source),'--outdir',td];subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
   for f in sorted(Path(td).iterdir()):
    b=f.read_bytes();assert b==(P/f.name).read_bytes(),f.name;deterministic.append(dict(file=f.name,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
 for tree in [source,engine]:assert subprocess.check_output(['git','-C',str(tree),'status','--porcelain'],text=True)==''
 result=dict(status='PASS_CHANGED_COMPONENTS',checks=tests,deterministic_replay=deterministic,old_independent_PASS_reused=True,formal_acceptance=False,limitations=['hypothetical tax category/profit bases','household vs individual income unit candidate','foreign macro not connected','national budget open','health QOL unconnected','VAT quantity affects receipts;separate household volume-to-GDP channel absent'])
 (P/'N3_Expansion_Checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--engine',required=True);p.add_argument('--replay',action='store_true');a=p.parse_args();run(Path(a.source),Path(a.engine),a.replay)
