#!/usr/bin/env python3
"""Finite expenditure/borrowing authority constraints; no sector allocations invented.
Borrowing beyond a cap, if needed even at zero added spending, is an UNFUNDED
BASELINE REQUIREMENT in the continuation diagnostic, never authorized issuance.
"""
import argparse,csv,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
PRIOR='handoff/chatgpt-n3-central-local-funding-accounts-20261122'
SFA='handoff/chatgpt-n3-sfa-cash-reconciliation-20261122'
PIN='5c2cdad05119d453e2c0bf002cca4795e5de26b5'
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def module(p):
 sp=importlib.util.spec_from_file_location('pinned_sfa',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def run(root,out):
 out.mkdir(parents=True,exist_ok=True);m=module(root/SFA/'N3_SFA_Reproduce.py');m.install_runtime(out)
 receipts=[]
 for p in sorted((root/PRIOR).iterdir()):
  if not p.is_file():continue
  rel=str(p.relative_to(root));b=subprocess.check_output(['git','show',PIN+':'+rel],cwd=root);assert p.read_bytes()==b
  receipts.append(dict(commit=PIN,path=rel,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 for rel in ['policies/New3linesPolicies.md',SFA+'/N3_SFA_Reproduce.py','handoff/chatgpt-n3-transition-financing-full-dynamics-20261122/N3_Transition_Reproduce.py']:
  b=subprocess.check_output(['git','show',PIN+':'+rel],cwd=root);assert (root/rel).read_bytes()==b;receipts.append(dict(commit=PIN,path=rel,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 (out/'Input_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 old=rd(root/PRIOR/'N3_Central_Local_GDP_Annual_Comparison_2026_2055.csv');reference={int(x['year']):x for x in old if x['case']=='MIN_SQ_BOTH'}
 caps={y:dict(G=float(z['government_purchase_nominal_trn']),I=float(z['public_investment_nominal_trn']),borrowing=max(0.,float(z['CL_new_borrowing_trn']))) for y,z in reference.items()}
 # Epsilon bounds are explicit and finite, not a new economic authorization.
 caps[2030]['borrowing']=11.185303
 budgets=dict(conditional_expenditure_authority_2030_trn=11.184747,annual_caps=caps,source_commit=PIN,source_case='MIN_SQ_BOTH',actual_budget_authorized=False,post2030_deficit_law_extension_assumed=False,scope='CONSOLIDATED_HYPOTHETICAL_FINITE_BUDGETS_NOT_SECTOR_AUTHORITY')
 (out/'Conditional_Finite_Authority_Inputs.json').write_text(json.dumps(budgets,indent=2)+'\n')
 class Runner(m.Runner):
  def authority_cap(self,s,y,k):
   if s.get('verified_only'):return 0.
   if y==2030 and ((k=='G' and s.get('exclude_G2030')) or (k=='I' and s.get('exclude_I2030'))):return 0.
   return caps[y][k]
  def cash_budget(self,s,y,pb,interest,sfa,assets):
   base=super().cash_budget(s,y,pb,interest,sfa,assets)
   if s.get('verified_only'):return 0.
   F=self.cash_part(s,y,sfa);loan=caps[y]['borrowing'];execution=budgets['conditional_expenditure_authority_2030_trn'] if y==2030 else 0.
   return min(base+execution,max(0.,pb-interest-F+loan))
 source=(out/'Resolved_SFA_Simulate.py.txt').read_text()
 oldg="g=s['g_share']*room;pibudget=s['pi_share']*room";assert source.count(oldg)==1
 source=source.replace(oldg,"g=min(s['g_share']*room,self.authority_cap(s,y,'G'));pibudget=s['pi_share']*room")
 marker=";pipay=pi*d/s['domestic'];spend=g+pipay";assert source.count(marker)==1
 source=source.replace(marker,";pi=min(pi,self.authority_cap(s,y,'I')*s['domestic']/d);pipay=pi*d/s['domestic'];spend=g+pipay")
 ns=dict(m.T.previous.__dict__);exec(compile(source,'authority_isolated_runtime.py','exec'),ns);Runner.simulate=ns['simulate'];(out/'Resolved_Authority_Runtime.py.txt').write_text(source)
 r=Runner(root,out);annual=[];ledger=[];summary=[];caprows=[];defs=[]
 for cid,kw in [('VERIFIED_ADDITIONAL_AUTHORITY_ONLY',dict(verified_only=True)),('CONDITIONAL_FINITE_GI_BUDGETS',{}),('CONDITIONAL_NO_G_AUTHORITY_2030',dict(exclude_G2030=True)),('CONDITIONAL_NO_I_AUTHORITY_2030',dict(exclude_I2030=True))]:
  s=m.spec(cid,cash_partition='SECTOR',q_central=0. if kw.get('verified_only') else 1.,q_local=0. if kw.get('verified_only') else 1.,**kw);defs.append(s)
  a,l,b=r.simulate(s);ix={x['year']:x for x in l}
  for x in a:
   y=x['year'];z=ix[y];G=r.authority_cap(s,y,'G');I=r.authority_cap(s,y,'I');B=0. if s.get('verified_only') and y>=2030 else caps[y]['borrowing']
   unsupported=max(0.,z['new_cash_borrowing_trn']-B)
   state='CERTIFIED_INCREMENT_LOWER_NOT_REAL_CASH_FORECAST' if s.get('verified_only') else 'CONDITIONAL_FINITE_BUDGETS_NOT_2030_APPROVAL'
   x.update(authority_classification=state,G_authority_cap_trn=G,I_authority_cap_trn=I,conditional_borrowing_cap_trn=B,unfunded_baseline_cash_requirement_trn=unsupported,actual_2030_sector_funding='unknown',sector_allocation='unknown',post2030_new_deficit_bond_authority='unknown',real_world_feasibility=False)
   caprows.append(dict(case=cid,year=y,G_actual_trn=x['government_purchase_nominal_trn'],G_cap_trn=G,I_actual_trn=x['public_investment_nominal_trn'],I_cap_trn=I,conditional_borrowing_candidate_trn=z['new_cash_borrowing_trn'],borrowing_cap_trn=B,unsupported_baseline_cash_need_trn=unsupported,borrowing_status='UNFUNDED_BASELINE_REQUIREMENT_CONTINUATION_ONLY' if unsupported>1e-6 else 'WITHIN_FINITE_CONDITIONAL_CAP_NOT_CERTIFIED',expenditure_authorized_for_N3=False,central_needed_issue_trn='unknown',local_needed_issue_trn='unknown',central_local_transfer_trn='unknown'))
   r.ck(cid+str(y)+':G_cap',max(0.,x['government_purchase_nominal_trn']-G));r.ck(cid+str(y)+':I_cap',max(0.,x['public_investment_nominal_trn']-I))
   if z['government_spend_trn']>1e-6:r.ck(cid+str(y)+':finite_cash_cap',unsupported,1e-6)
   r.ck(cid+str(y)+':cash_identity',z['PB_trn']-z['interest_trn']-z['SFA_cash_need_trn']+z['new_cash_borrowing_trn']-z['cash_debt_redemption_trn']-z['assets_end_trn']+z['assets_begin_trn'])
   if cid=='CONDITIONAL_FINITE_GI_BUDGETS':
    for k in ['real_GDP_trn','CL_debt_candidate_trn','total_tax_diagnostic_proxy_trn']:r.ck('limited_reference:'+str(y)+k,x[k]-float(reference[y][k]),3e-6)
   if cid=='VERIFIED_ADDITIONAL_AUTHORITY_ONLY':
    oldrow=next(z for z in old if z['case']=='EVIDENCE_CONFIRMED_INCREMENT_LOWER' and int(z['year'])==y)
    r.ck('limited_lower:'+str(y),x['real_GDP_trn']-float(oldrow['real_GDP_trn']),3e-6)
  z=m.T.previous.summary(s,a,l);z.update(gap2030=next(x['GDP_minus_SQ_trn'] for x in a if x['year']==2030),G2030=next(x['government_purchase_nominal_trn'] for x in a if x['year']==2030),I2030=next(x['public_investment_nominal_trn'] for x in a if x['year']==2030),borrow2030=ix[2030]['new_cash_borrowing_trn'],unfunded_baseline_total_trn=sum(x['unfunded_baseline_cash_requirement_trn'] for x in a),real_world_authority_confirmed=False)
  annual+=a;ledger+=l;summary.append(z)
 refs={'EVIDENCE_CONFIRMED_INCREMENT_LOWER','UNCONFIRMED_FLOW_Q0','CONDITIONAL_CENTRAL','CONDITIONAL_LOCAL','CONDITIONAL_BOTH','MIN_SQ_CENTRAL','MIN_SQ_LOCAL','MIN_SQ_BOTH'}
 reused=[{**x,'result_origin':'REUSED_FIXED_RESULT','source_commit':PIN} for x in old if x['case'] in refs]
 dump(out/'N3_Financing_Authority_Annual_Comparison_2026_2055.csv',annual+reused);dump(out/'N3_Authority_Cash_Debt_Ledger_2026_2055.csv',ledger);dump(out/'N3_Annual_Authority_Cap_And_Execution.csv',caprows);dump(out/'N3_Case_Summary.csv',summary);dump(out/'N3_Case_Definitions.csv',defs)
 dump(out/'N3_2030_Authorized_Funding_Capacity_and_Gap.csv',[dict(**{**x,**next(z for z in annual if z['case']==x['case'] and z['year']==2030)},actual_usable_funding_trn='unknown',certified_increment_credit_lower_trn=0.,actual_SFA_cash_need_trn='unknown',actual_central_issue_capacity_trn='unknown',actual_local_issue_capacity_trn='unknown',actual_expenditure_authority_trn='unknown',verified_legal_instrument_exists=True,government_spend_trn=x['G_actual_trn']+x['I_actual_trn']) for x in caprows if x['year']==2030])
 result=dict(status='PASS_LIMITED_ARITHMETIC_AND_CAP_ENFORCEMENT' if not r.checks else 'FAIL',new_cases=4,new_annual_rows=len(annual),reused_cases=8,reused_annual_rows=len(reused),checks=r.counter,failed=len(r.checks),failures=r.checks,prior_checks_reused=[6972,30925],official_budget_cap_2030='unknown',G_and_I_finite_caps_enforced=True,sector_cash_closure=False,real_world_SQ_feasibility=False,policy_adopted=False,common_engine_modified=False)
 (out/'Verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));print(json.dumps(summary));assert not r.checks,r.checks[:4]
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--outdir',type=Path,required=True);z=p.parse_args();run(z.root.resolve(),z.outdir.resolve())
