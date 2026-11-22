#!/usr/bin/env python3
"""Policy/executor routing on finite authority runtime; all sector routes are
explicit unadopted options. No payroll, benefits, transfer or capital is added a
second time. Aggregate dynamics are recomputed; sector full balances stay unknown.
"""
import argparse,csv,json,hashlib,subprocess,importlib.util,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
AUTH='handoff/chatgpt-n3-financing-authority-feasibility-20261123';PIN='c087a1a5af12b86cdb140d934754d75e5ee9c4ef'
SFA='handoff/chatgpt-n3-sfa-cash-reconciliation-20261122'
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(root,out):
 out.mkdir(parents=True,exist_ok=True);sp=importlib.util.spec_from_file_location('mapping_fixed_sfa',root/SFA/'N3_SFA_Reproduce.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 receipts=[]
 paths=[str(f.relative_to(root)) for f in sorted((root/AUTH).iterdir()) if f.is_file()]
 paths+=['policies/New3linesPolicies.md','specifications/SimulationSpecification_v6_Annex.md','policies/FreedomPolicies_Annex.md','handoff/chatgpt-n3-model-expansion-20261121/N3_Components.py','handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Components.py','handoff/chatgpt-n3-f-parity-implementation-20261122/Components.py','handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122/Component_Initialization.json']
 for rel in paths:
  b=subprocess.check_output(['git','show',PIN+':'+rel],cwd=root);assert (root/rel).read_bytes()==b
  receipts.append(dict(commit=PIN,path=rel,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 (out/'Input_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 authority=json.loads((root/AUTH/'Conditional_Finite_Authority_Inputs.json').read_text());caps={int(y):z for y,z in authority['annual_caps'].items()}
 routes=[dict(case='NO_UNAPPROVED_ASSIGNMENT',verified_only=True,G_executor='UNASSIGNED',I_executor='UNASSIGNED',transfer='NONE'),dict(case='CONDITIONAL_CENTRAL_EXECUTOR',G_executor='CENTRAL',I_executor='CENTRAL',transfer='NONE'),dict(case='CONDITIONAL_LOCAL_ELIGIBLE_I',exclude_G2030=True,G_executor='CENTRAL',I_executor='LOCAL_ASSET_OWNER',transfer='NONE_LOCAL_RESOURCES_UNVERIFIED'),dict(case='CONDITIONAL_MIXED_WITH_TRANSFERS',G_executor='CENTRAL',I_executor='LOCAL_ASSET_OWNER',transfer='CENTRAL_GRANT_EQUALS_I_UNAPPROVED_FULL_FUNDING')]
 # I-only branch keeps G unexecuted ALL years to isolate local eligible-I route.
 routes[2]['exclude_G_all_years']=True
 inputs=dict(base_authority_inputs=authority,routes=routes,actual_sector_shares='unknown',conditional_routes_are_policy_adoption=False,extra_G_earmarked_to_existing_payroll=False,extra_I_individual_projects='unknown',additional_I_nonoverlap_with_baseline='CONDITIONAL_NOT_VERIFIED',budget_2030='unknown',grant_funding_fraction=1.,grant_fraction_status='ONLY_MIXED_BRANCH_UNAPPROVED_OPTION_NOT_EXISTING_PROGRAM_RATE')
 (out/'Conditional_Executor_Routing_Inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
 class Runner(m.Runner):
  def authority_cap(self,s,y,k):
   if s.get('verified_only'):return 0.
   if k=='G' and s.get('exclude_G_all_years'):return 0.
   return caps[y][k]
  def cash_budget(self,s,y,pb,interest,sfa,assets):
   base=super().cash_budget(s,y,pb,interest,sfa,assets)
   if s.get('verified_only'):return 0.
   execution=authority['conditional_expenditure_authority_2030_trn'] if y==2030 else 0.
   return min(base+execution,max(0.,pb-interest-self.cash_part(s,y,sfa)+caps[y]['borrowing']))
 source=(root/AUTH/'Resolved_Authority_Runtime.py.txt').read_text()
 needle='  annual.append(row)';assert source.count(needle)==1
 source=source.replace(needle,"  row.update(existing_public_payroll_delta_trn=w.get('public_payroll_delta_trn'),existing_public_added_jobs=w.get('public_added_jobs'),existing_in_kind_trn=w.get('in_kind_trn'),existing_premium_relief_trn=w.get('premium_relief_trn'),existing_policy_government_cost_delta_trn=w.get('policy_government_cost_delta_trn'),existing_policy_investment_delta_trn=w.get('policy_investment_delta_trn'),native_smart_priority=';'.join(co.structures[-1]['smart_priority'].split(';')) if co.structures else 'unknown')\n"+needle)
 ns=dict(m.T.previous.__dict__);exec(compile(source,'isolated_mapping_runtime.py','exec'),ns);Runner.simulate=ns['simulate'];(out/'Resolved_Mapping_Runtime.py.txt').write_text(source)
 r=Runner(root,out);annual=[];integrated=[];sectors=[];summ=[];definitions=[];alloc=[]
 prev=rd(root/AUTH/'N3_Financing_Authority_Annual_Comparison_2026_2055.csv');ref={(x['case'],int(x['year'])):x for x in prev}
 native=[]
 for route in routes:
  s=m.spec(route['case'],cash_partition='SECTOR',q_central=0. if route.get('verified_only') else 1.,q_local=0. if route.get('verified_only') else 1.,**{k:v for k,v in route.items() if k!='case'});definitions.append(s)
  a,l,b=r.simulate(s);ix={x['year']:x for x in l}
  for x in a:
   y=x['year'];g=x['government_purchase_nominal_trn'];i=x['public_investment_nominal_trn'];Gcentral=g if route['G_executor']=='CENTRAL' else 0.;Icentral=i if route['I_executor']=='CENTRAL' else 0.;Ilocal=i if route['I_executor']=='LOCAL_ASSET_OWNER' else 0.;T=i if route['transfer']=='CENTRAL_GRANT_EQUALS_I_UNAPPROVED_FULL_FUNDING' else 0.
   unsupported=max(0.,ix[y]['new_cash_borrowing_trn']-caps[y]['borrowing'])
   x.update(conditional_central_G_trn=Gcentral,conditional_central_I_trn=Icentral,conditional_local_G_trn=0.,conditional_local_I_trn=Ilocal,conditional_central_to_local_transfer_trn=T,transfer_added_to_GDP_trn=0.,evidence_assigned_increment_G_trn=0.,evidence_assigned_increment_I_trn=0.,policy_use_unassigned_increment_G_trn=g,policy_use_unassigned_increment_I_trn=i,actual_central_G_trn='unknown',actual_local_G_trn='unknown',actual_central_I_trn='unknown',actual_local_I_trn='unknown',actual_central_debt_trn='unknown',actual_local_debt_trn='unknown',new_payroll_added_to_G_trn=0.,new_in_kind_added_to_G_trn=0.,new_smart_project_cost_added_trn=0.,unfunded_baseline_continuation_trn=unsupported,route_status='NO_CERTIFIED_EXTRA_MONETARY_ASSIGNMENT' if route.get('verified_only') else 'CONDITIONAL_OPTION_NOT_ADOPTED')
   r.ck(route['case']+str(y)+':final_execution_once',Gcentral+Icentral+Ilocal-g-i)
   r.ck(route['case']+str(y)+':transfer_cancel',-T+T)
   r.ck(route['case']+str(y)+':source_use_after_transfer_cancel',Gcentral+Icentral+T+Ilocal-T-g-i)
   r.ck(route['case']+str(y)+':G_cap',max(0.,g-r.authority_cap(s,y,'G')));r.ck(route['case']+str(y)+':I_cap',max(0.,i-r.authority_cap(s,y,'I')))
   if g+i>1e-6:r.ck(route['case']+str(y)+':funding_cap',unsupported,1e-6)
   if route['case'] in ['CONDITIONAL_CENTRAL_EXECUTOR','CONDITIONAL_MIXED_WITH_TRANSFERS','NO_UNAPPROVED_ASSIGNMENT']:
    old='VERIFIED_ADDITIONAL_AUTHORITY_ONLY' if route.get('verified_only') else 'CONDITIONAL_FINITE_GI_BUDGETS'
    for k in ['real_GDP_trn','total_tax_diagnostic_proxy_trn','CL_debt_candidate_trn']:r.ck('limited_reference:'+route['case']+str(y)+k,x[k]-float(ref[old,y][k]),3e-6)
   for sector,gg,ii,outgoing,incoming in [('CENTRAL',Gcentral,Icentral,T,0.),('LOCAL',0.,Ilocal,0.,T)]:
    sectors.append(dict(case=route['case'],year=y,sector=sector,conditional_increment_G_trn=gg,conditional_increment_I_trn=ii,conditional_transfer_out_trn=outgoing,conditional_transfer_in_trn=incoming,conditional_net_policy_cash_use_trn=gg+ii+outgoing-incoming,existing_payroll_sector_trn='unknown',existing_in_kind_sector_trn='unknown',sector_tax_trn='unknown',cash_begin_trn='unknown',cash_end_trn='unknown',interest_trn='unknown',gross_bond_issue_trn='unknown',net_cash_borrowing_trn='unknown',debt_end_trn='unknown',SFA_cash_use_trn='unknown',appropriation_2030='unknown',status='PARTIAL_POLICY_USE_ROUTING_ONLY_NO_CASH_CLOSURE'))
   native.append(dict(case=route['case'],year=y,existing_public_payroll_delta_trn=x['existing_public_payroll_delta_trn'],public_added_jobs=x['existing_public_added_jobs'],employment_mode=r.ci['s'].get('employment_mode','REGULARIZE'),public_job_target_model=r.ci['config']['public_job_target'],regularization_payroll_start=2030,regularization_ramp=6,existing_in_kind_trn=x['existing_in_kind_trn'],existing_premium_relief_trn=x['existing_premium_relief_trn'],existing_policy_government_cost_delta_trn=x['existing_policy_government_cost_delta_trn'],existing_policy_investment_delta_trn=x['existing_policy_investment_delta_trn'],smart_priority=x['native_smart_priority'],smart_priority_region_status='SYNTHETIC_A_B_C_NOT_REAL_LOCAL_GOVERNMENTS',native_compact_infrastructure_budget='not_implemented',original_policy_sector_assignment='unknown',separate_new_payroll_added_trn=0.,separate_new_in_kind_added_trn=0.,status='EXISTING_NATIVE_FLOW_EXTRACTED_NOT_NEW_RESOURCE'))
   if y==2030:
    for typ,amount in [('G',g),('I',i)]:
     base=float(ref['CONDITIONAL_FINITE_GI_BUDGETS',2030]['government_purchase_nominal_trn' if typ=='G' else 'public_investment_nominal_trn'])
     alloc.append(dict(case=route['case'],GI=typ,reference_envelope_trn=base,original_text_monetary_assignment_trn='unknown',evidence_accepted_increment_assignment_credit_trn=0.,reference_unassigned_to_original_policy_and_actual_executor_trn=base,branch_executed_trn=amount,branch_not_executed_vs_reference_trn=base-amount,conditional_central_executor_trn=Gcentral if typ=='G' else Icentral,conditional_local_executor_trn=0. if typ=='G' else Ilocal,actual_central_share='unknown',actual_local_share='unknown',existing_native_payroll_separate_trn=x['existing_public_payroll_delta_trn'] if typ=='G' else 'not_applicable',native_payroll_deducted_from_new_G_trn=0.,classification='CONDITIONAL_OPTION' if not route.get('verified_only') else 'NO_UNAPPROVED_ASSIGNMENT',budget2030='unknown',finance2030='unknown'))
  z=m.T.previous.summary(s,a,l);z.update(gap2030=next(x['GDP_minus_SQ_trn'] for x in a if x['year']==2030),G2030=next(x['government_purchase_nominal_trn'] for x in a if x['year']==2030),I2030=next(x['public_investment_nominal_trn'] for x in a if x['year']==2030),borrow2030=ix[2030]['new_cash_borrowing_trn'],transfer2030=next(x['conditional_central_to_local_transfer_trn'] for x in a if x['year']==2030),unfunded_baseline_total_trn=sum(x['unfunded_baseline_continuation_trn'] for x in a),sector_cash_closed=False,policy_adopted=False);summ.append(z);annual+=a;integrated+=l
 keep={'CONDITIONAL_FINITE_GI_BUDGETS','CONDITIONAL_NO_G_AUTHORITY_2030','CONDITIONAL_NO_I_AUTHORITY_2030'}
 reused=[{**x,'result_origin':'REUSED_PINNED_RESULT','source_commit':PIN} for x in prev if x['case'] in keep]
 dump(out/'N3_Policy_GI_Annual_Comparison_2026_2055.csv',annual+reused);dump(out/'N3_Conditional_Sector_Policy_Use_Ledger_2026_2055.csv',sectors);dump(out/'N3_Integrated_Cash_Debt_Ledger_2026_2055.csv',integrated);dump(out/'N3_Existing_Native_Payroll_Benefits_And_Priority.csv',native);dump(out/'N3_2030_GI_Allocation_And_Unresolved_Shares.csv',alloc);dump(out/'N3_Case_Summary.csv',summ);dump(out/'N3_Case_Definitions.csv',definitions);dump(out/'Detail_2029_2032.csv',[x for x in annual if 2029<=x['year']<=2032])
 v=dict(status='PASS_LIMITED_TRACE_ROUTING_AND_ARITHMETIC' if not r.checks else 'FAIL',new_cases=4,new_annual_rows=len(annual),reused_cases=3,reused_annual_rows=len(reused),checks=r.counter,failed=len(r.checks),failures=r.checks,prior_checks_reused=[3190,6972],extra_payroll_and_benefit_readdition=False,actual_2030_GI_assignment='unknown',confirmed_additional_monetary_assignment_credit_trn=0.,sector_cash_closed=False,real_world_all_years_SQ=False,policy_adopted=False,common_engine_modified=False)
 (out/'Verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v));print(json.dumps(summ));assert not r.checks,r.checks[:6]
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--outdir',type=Path,required=True);z=a.parse_args();run(z.root.resolve(),z.outdir.resolve())
