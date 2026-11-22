#!/usr/bin/env python3
"""Isolated transition financing and native VAT/medical interface continuation.
No source engine file or policy is changed. Diagnostic allocations are not policy.
"""
import argparse,ast,copy,csv,hashlib,importlib.util,inspect,json,math,os,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PREV='handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122';OLD='handoff/chatgpt-n3-gdp-recirculation-counterfactual-20261122';BD='handoff/chatgpt-n3-policy-burden-diagnosis-20261122';ND='handoff/chatgpt-n3-f-parity-implementation-20261122';REQUEST='bf0f051116f82a91302244d41fbdd3d5a9bfd9bc';PIN='606e2019c00b466b3ccdcc292136c581aef478d3'
def module(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def n(r,k):return float(r.get(k) or 0.)
previous=module('pinned_robustness',ROOT/PREV/'N3_GDP_Robustness_Reproduce.py')
def spec(cid,**kw):
 s=previous.spec(cid,dynamic=True,room_mode='CASH_NEUTRAL');s.update(cash_basis='DEBT_NONINCREASE',vat_dynamic=False,medical_dynamic=False,medical_VAT_scope=False,estate_dynamic=False,vat_anchor='CORE',min_to_SQ=False,bridge_cap=0.,bridge_total_cap=1e6,bridge_start=2030,bridge_end=2032,pre_tax_budget=0.,frontload_start=2029,frontload_end=2029,repay_start=2035,repay_end=2040,spending_delay=0,carry_unspent=False,use_assets=False);s.update(kw);s['classification']='UNADOPTED_DIAGNOSTIC_ALLOCATION_AND_INTERFACE';s['additional_borrow_or_timing_candidate']=bool(s['bridge_cap'] or s['pre_tax_budget'] or s['spending_delay']);return s
class Runner(previous.Runner):
 def __init__(self,root,out):
  super().__init__(root,out);self.extra_ledger=[];self.connections=[];self.native_tests=[];self.medical_input=json.loads((P/'Medical_Initialization.json').read_text());self.V=module('transition_native_VAT',root/'handoff/f-vat-core-20261120/Model.py');self.vc=json.loads((root/'handoff/f-vat-core-20261120/Inputs.json').read_text())
  fmroot=root/'handoff/f-common-endoflife-finalization-20261121';sys.path.insert(0,str(fmroot));self.FM=module('transition_native_medical',fmroot/'FMedical.py')
  # Extract the exact N3 cap/claim function from the pinned original source.
  pin='3c77eafc2073fdaba4c129164817d2f57c9421b9';path='handoff/claude-n3-model-draft-20261121/SPE_N3_Medical_On_CommonSQ_Draft_DRAFT_20261121.py'
  
  if subprocess.run(['git','cat-file','-e',pin],cwd=root,capture_output=True).returncode:subprocess.run(['git','fetch','origin',pin],cwd=root,check=True)
  source=subprocess.check_output(['git','show',pin+':'+path],cwd=root,text=True);tree=ast.parse(source);node=next(z for z in tree.body if isinstance(z,ast.FunctionDef) and z.name=='n3_claim');ns=dict(math=math,_orig_claim=self.FM.patient_claim,N3=dict(coinsurance=.5,scope='ALL_AGES'));exec(compile(ast.Module(body=[node],type_ignores=[]),'pinned_N3_claim.py','exec'),ns);self.claimns=ns;self.n3claim=ns['n3_claim']
  medsrc=(fmroot/'FMedical.py').read_text();assert medsrc.count('b=a+(b-a)*ph')==1;medsrc=medsrc.replace('b=a+(b-a)*ph','b=b').replace("return aa+(reform-aa)*ph if s['copay'] else aa","return reform if s['copay'] else aa");medns=dict(self.FM.__dict__);exec(compile(medsrc,'native_rate_interpolation_medical.py','exec'),medns);self.medns=medns;self.Medical=medns['Medical']
  self.V.sq_rates=lambda y,s:(self.vatrate[y],.08 if y<2030 else self.vatrate[y]);self.vs=dict(id='N3_FIXED_VAT_BRANCH',rate=False,expansion=False,recovery=False,C=False,quantity_elasticity=.25,rate_pass=.8)
  self.regular_original=self.V.regular_account;self.sector_original=self.V.sector_account
 def channel_start(self,s):
  self.current_case=s;self.local_connection=[];self.current_medical=None;self.native_medical=None;self.bridge_used=0.;self.bridge_outstanding=0.;self.backlog=0.;self.extra_map={}
  if s['medical_dynamic'] or s['medical_VAT_scope']:
   d=copy.deepcopy(self.medical_input);self.native_medical=self.Medical(d['c'],d['s'],d['deflators'],d['population']);self.native_medical.trajectory=d['trajectory'];self.native_medical.elder=d['elder']
 def medical_row(self,s,y,prior,old):
  if not self.native_medical:self.current_medical=None;return copy.deepcopy(old)
  md=self.native_medical;i=y-2026
  factor=prior[-1]['nominal_gdp_trn']/prior[-1]['real_gdp_trn']/self.base[y-1]['coreD'] if prior and s['medical_dynamic'] else 1.
  md.deflators[i]=self.medical_input['deflators'][i]*factor
  def claim(age,group,profile,regime,uniform=False,cap_multiplier=1.):
   if not uniform:return self.claimns['_orig_claim'](age,group,profile,regime,False,cap_multiplier)
   cur=.2 if age=='PRESCHOOL' else (.2 if age=='AGE70_74' else .1) if age in ['AGE70_74','AGE75PLUS'] and group in ['TAXFREE','GENERAL'] else .3
   phase=max(0.,min(1.,(y-md.s['start_year']+1)/md.s['ramp_years']));self.claimns['N3']['coinsurance']=cur+phase*(.5-cur)
   return self.n3claim(age,group,profile,regime,True,cap_multiplier)
  self.medns['patient_claim']=claim;w=md.step(y);self.current_medical=w;self.medical_price_factor=factor
  return copy.deepcopy(w)
 def vat(self,y,N,medical=None):
  regular=[]
  def reg(*a,**kw):z=self.regular_original(*a,**kw);regular.append(z);return z
  def sector(c,s,a,year,std):
   b=self.sector_original(c,s,a,year,std)
   if medical is None or a['id']!='medical' or year==2026:return b
   factor=max(.05,1+medical['medical_VAT_scope_flow_delta_trn']/max(b['market_turnover_reference_trn'],1e-9))
   return self.sector_original(c,s,{**a,'R2025':a['R2025']*factor},year,std)
  self.V.regular_account=reg;self.V.sector_account=sector
  try:l,rr=self.V.tax_account(self.vc,self.vs,y,N)
  finally:self.V.regular_account=self.regular_original;self.V.sector_account=self.sector_original
  hh=l['household_direct_price_benefit_trn']+l['household_wage_allocation_trn'];q=sum((z['base']+z['old_VAT'])*(z['quantity']-1) for z in regular[:2]);price=sum(z['price_HH'] for z in regular[:2]);return l,rr,hh,q,price
 def channels(self,s,y,t,w,co,md,prior):
  initial=y==2026;factor=1.;vdt=vh=vg=vi=vis=medtax=medhh=medgov=medins=medinv=estate=0.;quantity=w['quantity_nominal_volume_delta_trn'];price=w['quantity_replaced_price_benefit_trn'];w=copy.deepcopy(w);old=t['medical'];med=self.current_medical
  if med:
   medhh=med['household_cash_delta_trn']-old['medical_only_household_cash_delta_trn'];medgov=med['government_cost_delta_trn']-old['medical_only_government_cost_delta_trn'];medins=med['insurer_balance_delta_trn']-old['medical_only_insurer_balance_delta_trn'];medtax=med['medical_financing_direct_tax_trn']-old['medical_financing_direct_tax_trn']
   medinterest=med['medical_policy_interest_trn']-old['medical_policy_interest_trn']
   medgov-=medinterest # remove native satellite interest before national PB mapping
   medinv=med['investment_nominal_delta_trn']-(old['investment_nominal_delta_trn']-old['policy_investment_delta_trn']);medservice=med['service_production_nominal_delta_trn']-(old['service_production_nominal_delta_trn']-old['policy_service_VA_delta_trn']);w['service_production_nominal_delta_trn']+=medservice
   w.update(medical_only_household_cash_delta_trn=med['household_cash_delta_trn'],medical_only_government_cost_delta_trn=med['government_cost_delta_trn'],medical_only_insurer_balance_delta_trn=med['insurer_balance_delta_trn'])
  if s['vat_dynamic'] and prior:
   denominator=self.base[y-1]['coreN'] if s['vat_anchor']=='CORE' else self.base[y-1]['N'];factor=prior[-1]['nominal_gdp_trn']/denominator
  l=rr=None
  if s['vat_dynamic'] or s['medical_VAT_scope']:
   l,rr,hh,quantity,price=self.vat(y,t['coreN']*factor,med if s['medical_VAT_scope'] else None)
   vdt=l['VAT_delta_vs_fixed_reference_trn']-t['vat']['direct_tax'];vh=hh-t['vat']['household'];vi=l['VAT_induced_investment_trn']-t['vat']['investment'];vg=-l['government_purchase_benefit_trn']-t['vat']['public']
   # Insurer VAT deltas are satellite changes; do not also count them as public cash.
   oldl,_,_,_,_=self.vat(y,t['coreN']);vis=l['insurer_VAT_balance_delta_trn']-oldl['insurer_VAT_balance_delta_trn']
   if initial:vdt=vh=vi=vg=vis=0.;quantity=price=0.
   w.update(quantity_nominal_volume_delta_trn=quantity,quantity_replaced_price_benefit_trn=price)
  efactor=prior[-1]['nominal_gdp_trn']/prior[-1]['real_gdp_trn']/self.base[y-1]['coreD'] if s['estate_dynamic'] and prior else 1.
  if s['estate_dynamic']:
   estate=old['wealth_tax_delta_trn']*(efactor-1);w['wealth_tax_delta_trn']+=estate;w['policy_tax_delta_trn']+=estate;w['policy_household_cash_delta_trn']-=estate;w['household_cash_delta_trn']-=estate
  w['household_cash_delta_trn']+=medhh
  self.local_connection.append(dict(case=s['case'],year=y,VAT_enabled=s['vat_dynamic'],medical_enabled=s['medical_dynamic'],medical_scope_link=s['medical_VAT_scope'],estate_enabled=s['estate_dynamic'],VAT_lagged_output_factor=factor,VAT_regular_taxexclusive_base_trn=l['regular_reference_taxexclusive_base_trn'] if l else None,VAT_modeled_revenue_trn=l['modeled_VAT_trn'] if l else None,VAT_increment_vs_fixed_trn=vdt,VAT_HH_cash_change_trn=vh,VAT_G_cost_change_trn=vg,VAT_I_target_change_trn=vi,VAT_quantity_replacement_trn=quantity,VAT_price_replaced_trn=price,medical_price_factor=getattr(self,'medical_price_factor',1.) if med else 1.,medical_HH_cash_change_trn=medhh,medical_G_cost_change_trn=medgov,medical_insurer_change_trn=medins,medical_tax_change_trn=medtax,medical_investment_change_trn=medinv,medical_unassigned_trn=med['medical_unassigned_after_sources_trn'] if med else old['medical_unassigned_after_sources_trn'],medical_debt_trn=med['medical_policy_debt_stock_trn'] if med else old['medical_policy_debt_stock_trn'],estate_price_factor=efactor,estate_tax_change_trn=estate,legacy_pension_cash_trn=t['pension_ledger']['household_cash_delta_trn'],legacy_pension_status='NATIVE_SQ_PENSION_SATELLITE_DISABLED_ZERO',population_labor_core_deflator='FIXED_COMMON_PATH_NO_NEW_BEHAVIOR',VAT_rates_fixed=True))
  if s['medical_dynamic'] or s['medical_VAT_scope']:
   for key in ['transfer_residual_trn','independent_claim_residual_trn','independent_financing_residual_trn']:
    self.ck(s['case']+str(y)+':native_medical_'+key,med[key],5e-7)
  if l:self.ck(s['case']+str(y)+':VAT_decomposition',l['VAT_delta_vs_fixed_reference_trn']-l['regular_rate_effect_trn']-l['regular_pass_quantity_effect_trn']-l['sector_chain_VAT_effect_trn']-l['invoice_and_reference_bridge_trn'])
  return dict(w=w,direct=vdt+medtax+estate,cash=vh+medhh-estate,government=vg+medgov,insurer=vis+medins,investment=vi+medinv)
 def cash_budget(self,s,y,pb,interest,sfa,assets):
  ordinary=max(0.,pb-interest-(max(0.,sfa) if s['cash_basis']=='DEBT_NONINCREASE' else 0.))
  asset_available=max(0.,assets) if s['use_assets'] else 0.
  repay=min(self.bridge_outstanding,self.bridge_used/max(1,s['repay_end']-s['repay_start']+1)) if s['repay_start']<=y<=s['repay_end'] else 0.
  self.repay_requirement=repay
  allowance=min(s['bridge_cap'],max(0.,s['bridge_total_cap']-self.bridge_used)) if s['bridge_start']<=y<=s['bridge_end'] else 0.
  self.current_allowance=allowance
  return max(0.,ordinary+asset_available-repay)+(0. if s['min_to_SQ'] else allowance)
 def finalize_room(self,s,y,z,room,evalroom,interest,sfa,assets):
  neededspending=None;requiredauthority=None;original=dict(z);originalroom=room;target_GDP=self.sq[y]['Y'];window=s['bridge_start']<=y<=s['bridge_end']
  # Re-ordering and deferral are explicit allocation candidates, not source changes.
  if s['spending_delay'] and y<2030+s['spending_delay']:room=0.;z=evalroom(room)
  if s['min_to_SQ'] and z['Y']<target_GDP-1e-7 and window:
   lo=room;hi=room+max(1000.,self.primary[y]*5)
   # The minimum is conditional on fixed G/I shares and inherited states, not a global optimum.
   for _ in range(60):
    mid=(lo+hi)/2
    if evalroom(mid)['Y']>=target_GDP-1e-8:hi=mid
    else:lo=mid
   neededroom=hi;needed=evalroom(hi);primarylimit=needed['policyroom']
   maxroom=primarylimit
   if s['pre_tax_budget']>0:maxroom+=s['pre_tax_budget']/max(s['g_share']+s['pi_share'],1e-9)
   # For MIN policies, bridge_cap sets extra expenditure authority above the base.
   rawbudget=self.cash_budget({**s,'bridge_cap':0.},y,needed['pbpre'],interest,sfa,assets)
   required=max(0.,needed['spend']-rawbudget);neededspending=needed['spend'];requiredauthority=required
   allowed=min(s['bridge_cap'],max(0.,s['bridge_total_cap']-self.bridge_used))
   if neededroom<=maxroom+1e-7 and required<=allowed+1e-7:room=neededroom;z=needed
   else:
    lo=originalroom;hi=min(neededroom,maxroom)
    for _ in range(55):
     mid=(lo+hi)/2;zz=evalroom(mid);raw=self.cash_budget({**s,'bridge_cap':0.},y,zz['pbpre'],interest,sfa,assets)
     if zz['spend']>raw+allowed:hi=mid
     else:lo=mid
    room=(lo+hi)/2;z=evalroom(room)
  if s['min_to_SQ']:
   raw0=self.cash_budget({**s,'bridge_cap':0.},y,z['pbpre'],interest,sfa,assets);z['budget']=raw0+min(s['bridge_cap'],max(0.,s['bridge_total_cap']-self.bridge_used)) if window else raw0
  if s['pre_tax_budget'] and s['frontload_start']<=y<=s['frontload_end']:
   # Explicit pre-tax public expenditure financed through the same cash satellite.
   lo=0.;hi=max(1.,s['pre_tax_budget']*10)
   for _ in range(55):
    mid=(lo+hi)/2
    if evalroom(mid)['spend']>s['pre_tax_budget']:hi=mid
    else:lo=mid
   room=(lo+hi)/2;z=evalroom(room)
  rawbudget=self.cash_budget({**s,'bridge_cap':0.},y,z['pbpre'],interest,sfa,assets);excess=max(0.,z['spend']-rawbudget);authority=excess if s['min_to_SQ'] or s['pre_tax_budget'] else 0.
  paid=min(self.repay_requirement,max(0.,z['pbpre']-interest-z['spend']))
  self.bridge_used+=authority;self.bridge_outstanding=max(0.,self.bridge_outstanding+authority-paid)
  noSFAcash=max(0.,z['pbpre']-interest);newcash_need=max(0.,z['spend']-(z['pbpre']-interest)-assets)
  self.extra_map[y]=dict(case=s['case'],year=y,cash_basis=s['cash_basis'],binding_reference='PB_INTEREST_AND_POSITIVE_SFA' if s['cash_basis']=='DEBT_NONINCREASE' else 'ACTUAL_CASH_BALANCE_NO_SFA_AS_RESOURCE',ordinary_cash_surplus_before_spending_trn=z['pbpre']-interest,positive_SFA_trn=max(0.,sfa),base_execution_without_bridge_trn=original['spend'],final_execution_trn=z['spend'],additional_expenditure_authority_trn=authority,bridge_authority_cumulative_trn=self.bridge_used,bridge_authority_outstanding_trn=self.bridge_outstanding,scheduled_bridge_repayment_reserved_trn=paid,repayment_requested_trn=self.repay_requirement,unserved_repayment_trn=self.repay_requirement-paid,expenditure_above_cash_rule_trn=excess,actual_new_cash_need_after_assets_trn=newcash_need,allocation_room_trn=room,annual_primary_available_trn=z['policyroom'],G_requested_trn=s['g_share']*z['policyroom'],I_requested_trn=s['pi_share']*z['policyroom'],G_executed_trn=z['g'],I_executed_trn=z['pipay'],I_unexecuted_budget_trn=max(0.,s['pi_share']*z['policyroom']-z['pipay']),earliest_cash_constraint_binding=(z['spend']>=z['budget']-1e-7 and (s['g_share']+s['pi_share'])*z['policyroom']>z['spend']+1e-7),primary_envelope_binding=room>=z['policyroom']-1e-7,GDP_shortfall_before_additional_trn=min(0.,original['Y']-target_GDP),GDP_shortfall_after_trn=min(0.,z['Y']-target_GDP),required_spending_to_SQ_conditional_trn=neededspending,required_additional_authority_unconstrained_trn=requiredauthority,SFA_is_cash_source=False,authority_is_not_necessarily_new_cash_borrowing=True)
  return z,room

def install_runtime(out):
 source=inspect.getsource(previous.Runner.simulate);source='\n'.join(z[1:] for z in source.splitlines())+'\n'
 def sub(old,new):
  nonlocal source
  assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
 sub('co,md=self.component()','co,md=self.component();self.channel_start(s)')
 sub("md.rows.append(copy.deepcopy(old));native=co.step(y,md,prior)","md.rows.append(self.medical_row(s,y,prior,old));native=co.step(y,md,prior)")
 sub("f=self.funding[y];saving=", "channel=self.channels(s,y,t,w,co,md,prior);w=channel['w'];policyshift+=channel['direct'];govshift+=channel['government'];insshift+=channel['insurer'];cashshift+=channel['cash'];investshift+=channel['investment']\n  f=self.funding[y];saving=")
 sub("budget=max(0.,pbpre-interest-max(0.,sfa))", "budget=self.cash_budget(s,y,pbpre,interest,sfa,assets)")
 sub("z=evalroom(room);g=z['g'];", "z=evalroom(room);z,room=self.finalize_room(s,y,z,room,evalroom,interest,sfa,assets);g=z['g'];")
 sub("self.ck(pre+'allocation_envelope',max(0.,room-z['policyroom']),1e-6)","self.ck(pre+'allocation_envelope',max(0.,room-z['policyroom']),1e-6) if not s['pre_tax_budget'] else None")
 # Main tax decomposition includes VAT/medical separately, not in native policy tax.
 sub("policy_tax_change_trn=policyshift","policy_tax_change_trn=w['policy_tax_delta_trn']-old['policy_tax_delta_trn'],all_direct_tax_change_trn=policyshift")
 sub("return annual,closure,bridge", "self.connections.extend(self.local_connection)\n self.extra_ledger.extend(self.extra_map.values())\n return annual,closure,bridge")
 sub('annual.append(row)', '''row.update(GDP_core_difference_trn=t['coreY']-self.sq[y]['coreY'],GDP_C_difference_trn=C-self.sq[y]['C'],GDP_I_difference_trn=I-self.sq[y]['I']+privI+pubI,GDP_G_domestic_trn=g*s['domestic']/d,GDP_supply_difference_trn=par['capacity_absorption']*(supply-self.sq[y]['supply']),GDP_other_difference_trn=t['education_nom']/d-self.sq[y]['education_nom']/self.sq[y]['coreD']+t['education_level']-self.sq[y]['education_level']+t['finite']-self.sq[y]['finite']+w['service_production_nominal_delta_trn']/d-self.sq[y]['medical']['service_production_nominal_delta_trn']/self.sq[y]['coreD'],GDP_unmet_difference_trn=-z['unmet']+self.sq[y]['unmet'],desired_real_GDP_trn=z['desired'],policy_labor_rate=.3,policy_financial_rate=.2,policy_estate_rate=.4,labor_gross_base_trn=sum(x['labour_business_30_gross_base_trn'] for x in co.households if x['year']==y),financial_gross_base_trn=sum(x['financial20_gross_base_trn'] for x in co.households if x['year']==y),corporate_profit_base_trn=sum(x['profit_base_trn'] for x in co.firms if x['year']==y))
  if record:self.ck(s['case']+str(y)+':GDP_component_sum',row['GDP_minus_SQ_trn']-sum(row[k] for k in ['GDP_core_difference_trn','GDP_C_difference_trn','GDP_I_difference_trn','GDP_G_domestic_trn','GDP_supply_difference_trn','GDP_other_difference_trn','GDP_unmet_difference_trn']))
  annual.append(row)''')
 ns=dict(previous.__dict__);exec(compile(source,'isolated_transition_simulate.py','exec'),ns);Runner.simulate=ns['simulate'];(out/'Resolved_Transition_Simulate.py.txt').write_text(source)

def run(root,out,smoke=False):
 out.mkdir(parents=True,exist_ok=True);receipts=[]
 paths=[str(f.relative_to(root)) for f in sorted((root/PREV).iterdir()) if f.is_file()]
 paths += [OLD+'/N3_GDP_Recirculation_Reproduce.py',BD+'/N3_Unchanged_Execution_Trace.json',BD+'/N3_Conditional_Fiscal_Primary_Bridge.csv',ND+'/Components.py',ND+'/Inputs.json',ND+'/results/DOMESTIC_TRANSFER_Corporate_Funding_Stock.csv',ND+'/results/Conditional_National_Local_Fiscal.csv','handoff/f-vat-core-20261120/Model.py','handoff/f-vat-core-20261120/Inputs.json','handoff/f-common-endoflife-finalization-20261121/FMedical.py','handoff/f-common-endoflife-finalization-20261121/CommonInterface.py','handoff/f-common-endoflife-finalization-20261121/CommonEndOfLife.py','handoff/f-common-endoflife-finalization-20261121/Demand.py','handoff/chatgpt-national-fiscal-closure-20261121/National_Fiscal.py','handoff/chatgpt-national-fiscal-closure-20261121/Official_Fiscal_Baseline_2025_2040.csv','policies/New3linesPolicies.md','handoff/chatgpt-n3-transition-financing-full-dynamics-request-20261122/SPE_Work_N3_Transition_Financing_Full_Dynamics_Request_20261122.md']
 for path in paths:
  b=subprocess.check_output(['git','show',REQUEST+':'+path],cwd=root);assert (root/path).read_bytes()==b,path
  receipts.append(dict(commit=REQUEST,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 (out/'Input_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 install_runtime(out);r=Runner(root,out)
 # Native VAT at original input must match the old VAT flow exactly.
 for y,t in r.base.items():
  l,rr,hh,q,price=r.vat(y,t['coreN'])
  for key,error in [('direct',l['VAT_delta_vs_fixed_reference_trn']-t['vat']['direct_tax']),('household',hh-t['vat']['household']),('quantity',q-t['medical']['quantity_nominal_volume_delta_trn']),('price_replacement',price-t['medical']['quantity_replaced_price_benefit_trn'])]:r.ck('native_VAT_replay:'+str(y)+key,error)
  for v in t['pension_ledger'].values():r.ck('native_legacy_pension_disabled_zero:'+str(y),v)
 # Native claims on the unchanged medical price/population path must match.
 r.channel_start(spec('MEDICAL_REPLAY',medical_dynamic=True));prior=[]
 for y,t in r.base.items():
  med=r.medical_row(spec('MEDICAL_REPLAY'),y,prior,t['medical'])
  for key,oldkey in [('household_cash_delta_trn','medical_only_household_cash_delta_trn'),('government_cost_delta_trn','medical_only_government_cost_delta_trn'),('insurer_balance_delta_trn','medical_only_insurer_balance_delta_trn'),('medical_policy_debt_stock_trn','medical_policy_debt_stock_trn')]:r.ck('native_medical_replay:'+str(y)+key,med[key]-t['medical'][oldkey],2e-6)
  prior.append(copy.deepcopy(t['macro_row']))
 ann=[];led=[];bridges=[];summ=[];defs=[];cache={};bound=[]
 def execute(s):
  a,l,b=r.simulate(s);ann.extend(a);led.extend(l);bridges.extend(b);z=previous.summary(s,a,l);z['gap2030']=next(t['GDP_minus_SQ_trn'] for t in a if t['year']==2030);z['first_cash_binding_year']=next((t['year'] for t in r.extra_ledger if t['case']==s['case'] and t['earliest_cash_constraint_binding']),None);z['actual_borrowing_after2029_trn']=sum(t['new_cash_borrowing_trn'] for t in l if t['year']>=2030);z['extra_authority_total_trn']=sum(t['additional_expenditure_authority_trn'] for t in r.extra_ledger if t['case']==s['case']);z['authority_outstanding2055_trn']=next(t['bridge_authority_outstanding_trn'] for t in r.extra_ledger if t['case']==s['case'] and t['year']==2055);summ.append(z);defs.append(s);cache[s['case']]=(a,l,b);return z
 execute(spec('PREV_DYN_BASE',g_share=0.,pi_share=0.,firm_rate=0.))
 execute(spec('PREV_DYN_MIX',room_mode='FIXED_PRIMARY'))
 execute(spec('PREV_DYN_MIX_CASH'))
 stress=dict(tail='SQ_NOMINAL',ss_growth=.03,sfa_tail='PLUS1GDP',backfill=True,interest_mode='ALL_STOCK',rate=.04,rollover=.2)
 execute(spec('PREV_CASH_STRESS',**stress))
 execute(spec('CASH_ONLY',cash_basis='CASH_ONLY'))
 execute(spec('CASH_ONLY_ASSETS',cash_basis='CASH_ONLY',use_assets=True))
 execute(spec('G_FIRST_CASH',g_share=.75,pi_share=0.))
 execute(spec('I_FIRST_CASH',g_share=0.,pi_share=.75))
 execute(spec('DELAY1_CASH',spending_delay=1))
 execute(spec('DELAY2_CASH',spending_delay=2))
 for cap in [0.,1.,5.,10.,20.]:execute(spec('MIN_SQ_AUTH'+str(int(cap)),min_to_SQ=True,bridge_cap=cap,bridge_total_cap=cap))
 execute(spec('CASH_FRONTLOAD5',cash_basis='CASH_ONLY',pre_tax_budget=5.,bridge_cap=5.,bridge_total_cap=5.,bridge_start=2029,bridge_end=2029))
 flags=dict(vat_dynamic=True,medical_dynamic=True,medical_VAT_scope=True,estate_dynamic=True)
 for name,flag in [('VAT',dict(vat_dynamic=True)),('MEDICAL',dict(medical_dynamic=True)),('MEDICAL_SCOPE',dict(medical_VAT_scope=True)),('ESTATE',dict(estate_dynamic=True)),('ALL',flags)]:
  execute(spec(name+'_FIXED_ROOM',room_mode='FIXED_PRIMARY',**flag))
  execute(spec(name+'_CASH_ONLY',cash_basis='CASH_ONLY',**flag))
 execute(spec('ALL_BASE',g_share=0.,pi_share=0.,firm_rate=0.,**flags))
 execute(spec('ALL_DEBT_LIMIT',**flags))
 execute(spec('ALL_MIN_AUTH20',min_to_SQ=True,bridge_cap=20.,bridge_total_cap=20.,**flags))
 execute(spec('ALL_CASH_DOM60',cash_basis='CASH_ONLY',domestic=.6,**flags))
 execute(spec('ALL_CASH_PUBLIC_Y0',cash_basis='CASH_ONLY',yield_public=0.,**flags))
 execute(spec('ALL_CASH_STRESS',cash_basis='CASH_ONLY',**stress,**flags))
 execute(spec('ALL_MIN_CASH_STRESS20',cash_basis='CASH_ONLY',min_to_SQ=True,bridge_cap=20.,bridge_total_cap=20.,**stress,**flags))
 execute(spec('ALL_CASH_FRONTLOAD5',cash_basis='CASH_ONLY',pre_tax_budget=5.,bridge_cap=5.,bridge_total_cap=5.,bridge_start=2029,bridge_end=2029,**flags))
 # Anchored improvement-only VAT base is a separate identification sensitivity.
 execute(spec('ALL_VAT_BASELINE_ANCHOR',cash_basis='CASH_ONLY',vat_anchor='BASELINE_ACTUAL',**flags))
 if smoke:
  (out/'Smoke.json').write_text(json.dumps({'failures':r.checks,'summary':summ},indent=2)+'\n');print(json.dumps({'checks':r.counter,'failures':r.checks,'summary':summ},ensure_ascii=False));return
 # Reuse four earlier cases and compare a limited set of actual values.
 old={(z['case'],int(z['year'])):z for z in rd(root/PREV/'N3_GDP_Robustness_Annual_Comparison_2026_2055.csv')}
 for new,priorcid in [('PREV_DYN_BASE','DYN_BASE'),('PREV_DYN_MIX','DYN_MIX'),('PREV_DYN_MIX_CASH','DYN_MIX_CASH'),('PREV_CASH_STRESS','CASH_COMBINED_STRESS')]:
  for x in cache[new][0]:
   for k in ['real_GDP_trn','consumption_real_trn','policy_tax_delta_trn','CL_PB_candidate_trn','CL_debt_candidate_trn']:r.ck('prior_reproduction:'+new+str(x['year'])+k,x[k]-n(old[priorcid,x['year']],k),3e-6)
 # Cash-only uses no actual extra cash borrowing after the transition starts.
 for x in cache['CASH_ONLY'][1]:
  if x['year']>=2030:r.ck('cash_only_no_new_borrowing:'+str(x['year']),x['new_cash_borrowing_trn'],1e-6)
 # Assets do not create an invisible initial balance.
 for a,b in zip(cache['CASH_ONLY'][0],cache['CASH_ONLY_ASSETS'][0]):r.ck('asset_access_when_none:'+str(a['year']),a['real_GDP_trn']-b['real_GDP_trn'])
 # Bridge principal reserved from spend must really be amortised within cash surplus.
 for e in r.extra_ledger:
  l=next(z for z in led if z['case']==e['case'] and z['year']==e['year']);r.ck('tagged_repayment:'+e['case']+str(e['year']),max(0.,e['scheduled_bridge_repayment_reserved_trn']-l['cash_debt_redemption_trn']),2e-6)
 # Model-local minimum funding authority bracket, with fixed early G/I shares.
 for flagname,fl in [('PARTIAL',{}),('CONNECTED',flags)]:
  lo=0.;hi=20.
  def test(cap):
   s=spec('SEARCH_'+flagname,min_to_SQ=True,bridge_cap=cap,bridge_total_cap=cap,**fl);a,l,b=r.simulate(s,record=False);return all(z['GDP_minus_SQ_trn']>=-1e-7 for z in a),s,a,l
  good,_,_,_=test(hi)
  if good:
   for _ in range(24):
    mid=(lo+hi)/2
    if test(mid)[0]:hi=mid
    else:lo=mid
   for label,v in [('FAIL',lo),('PASS',hi)]:
    s=spec('BOUND_'+flagname+'_'+label,min_to_SQ=True,bridge_cap=v,bridge_total_cap=v,**fl);z=execute(s);bound.append(dict(boundary=flagname,side=label,authority_cap_total_trn=v,width_trn=hi-lo,all_years_SQ=z['all_years_SQ'],below_years=z['below_years'],worst_year=z['worst_year'],worst_gap=z['worst_gap_trn'],debt2055=z['debt2055'],actual_new_borrowing_after2029_trn=z['actual_borrowing_after2029_trn'],authority_used=z['extra_authority_total_trn'],global_intertemporal_minimum=False))
  else:bound.append(dict(boundary=flagname,side='NO_SUCCESS_CAP20',authority_cap_total_trn=20.,global_intertemporal_minimum=False))
 for e in r.extra_ledger:
  if e['case'] not in {d['case'] for d in defs}:continue
  l=next(z for z in led if z['case']==e['case'] and z['year']==e['year'])
  r.ck('final_tagged_repayment:'+e['case']+str(e['year']),max(0.,e['scheduled_bridge_repayment_reserved_trn']-l['cash_debt_redemption_trn']),2e-6)
  if 'BOUND_' in e['case']:r.ck('boundary_finance_identity:'+e['case']+str(e['year']),l['debt_end_trn']-l['assets_end_trn']-l['debt_begin_trn']+l['assets_begin_trn']+l['PB_trn']-l['interest_trn']-l['SFA_trn'])
 # Searching does not constitute an output case; retain only declared delivered cases.
 ids={s['case'] for s in defs};connections=[z for z in r.connections if z['case'] in ids];extra=[z for z in r.extra_ledger if z['case'] in ids]
 ixextra={(z['case'],z['year']):z for z in extra};ixconn={(z['case'],z['year']):z for z in connections};ixann={(z['case'],z['year']):z for z in ann}
 combined=[]
 for z in led:
  a=ixann[z['case'],z['year']];combined.append(dict(**z,**{k:v for k,v in ixextra[z['case'],z['year']].items() if k not in z},GDP_minus_SQ_trn=a['GDP_minus_SQ_trn'],consumption_real_trn=a['consumption_real_trn'],household_policy_cash_trn=a['household_policy_cash_nominal_trn'],policy_tax_trn=a['policy_tax_delta_trn'],macro_tax_trn=a['macro_tax_proxy_trn'],total_tax_trn=a['total_tax_diagnostic_proxy_trn'],private_I_trn=a['private_investment_real_trn'],public_I_trn=a['extra_public_investment_real_trn'],unmet_demand_real_trn=a['unmet_demand_real_trn'],supply_ceiling_trn=a['supply_ceiling_real_trn'],**{k:v for k,v in ixconn[z['case'],z['year']].items() if k not in z and k not in ixextra[z['case'],z['year']]}))
 # Single-channel and simultaneous effects, always from actual annual recurrence.
 deltas=[]
 for name in ['VAT','MEDICAL','MEDICAL_SCOPE','ESTATE','ALL']:
  for basis,ref in [('FIXED_ROOM','PREV_DYN_MIX'),('CASH_ONLY','CASH_ONLY')]:
   cid=name+'_'+basis
   for a,b in zip(cache[cid][0],cache[ref][0]):
    deltas.append(dict(channel=name,basis=basis,case=cid,reference=ref,year=a['year'],GDP_delta_trn=a['real_GDP_trn']-b['real_GDP_trn'],tax_delta_trn=a['total_tax_diagnostic_proxy_trn']-b['total_tax_diagnostic_proxy_trn'],household_cash_delta_trn=a['household_policy_cash_nominal_trn']-b['household_policy_cash_nominal_trn'],PB_delta_trn=a['CL_PB_candidate_trn']-b['CL_PB_candidate_trn'],debt_delta_trn=a['CL_debt_candidate_trn']-b['CL_debt_candidate_trn'],status='EXECUTED_NATIVE_INTERFACE_PARTIAL_DYNAMIC',new_policy_adopted=False))
 for a in ann:
  co=ixconn[a['case'],a['year']];a.update(VAT_standard_rate=r.vatrate[a['year']],VAT_base_proxy=co['VAT_regular_taxexclusive_base_trn'],VAT_increment_vs_fixed_trn=co['VAT_increment_vs_fixed_trn'],estate_tax_increment_vs_fixed_trn=co['estate_tax_change_trn'],medical_tax_increment_vs_fixed_trn=co['medical_tax_change_trn'],full_N3_dynamic=False)
 dump(out/'Cause_2026_2035.csv',[dict(**z,**{k:ixann[z['case'],z['year']][k] for k in ixann[z['case'],z['year']] if k.startswith('GDP_') and k not in z}) for z in combined if z['year']<=2035 and z['case'] in ['PREV_DYN_BASE','PREV_DYN_MIX','PREV_DYN_MIX_CASH','CASH_ONLY','ALL_CASH_ONLY','ALL_DEBT_LIMIT']]);dump(out/'N3_Transition_Financing_Case_Comparison.csv',ann);dump(out/'N3_Transition_Financing_Annual_Ledger_2026_2055.csv',combined);dump(out/'N3_Full_Dynamics_Connection_Deltas.csv',deltas);dump(out/'N3_Transition_Financing_Boundaries.csv',bound);dump(out/'N3_Transition_Case_Summary.csv',summ);dump(out/'N3_Transition_Case_Definitions.csv',defs);dump(out/'N3_Native_Channel_Accounts.csv',connections);dump(out/'N3_Transition_Native_Tax_Household_Bridge.csv',bridges)
 result=dict(status='PASS_LIMITED_CONNECTED_DIAGNOSTIC' if not r.checks else 'FAIL',checks=r.counter,failed=len(r.checks),failures=r.checks,cases=len(defs),annual_rows=len(ann),prior_checks_reused=35281,earlier_checks_reused=12311,prior_full_reaudit=False,native_VAT_price_quantity_revenue_recomputed=True,native_medical_claim_payers_recomputed=True,legacy_pension_inactive_zero_confirmed=True,estate_realized_price_interface=True,full_N3_dynamic=False,general_government_closed=False,source_policy_or_engine_modified=False,policy_adopted=False)
 statusrows=[
 dict(channel='VAT',previous='FIXED_CORE_BASE',current='NATIVE_LAGGED_GDP_BASE_PRICE_QUANTITY_REVENUE',formula='existing tax_account with lag actual nominal GDP/core nominal ratio; replace quantity correction once',unresolved='GDP proxy rather than separately calibrated HH consumption and private investment transaction bases; residual nonHH revenue-equivalent base',policy_adopted=False),
 dict(channel='MEDICAL',previous='FIXED_CLAIM_LEDGER',current='NATIVE_CLAIM_PAYER_LOOP_WITH_LAGGED_REALIZED_PRICE',formula='same N3 rate interpolation and nominal caps; fixed age trajectory; lag N/Y price interface',unresolved='no supported income-to-utilisation function; full clinical and fiscal calibration absent',policy_adopted=False),
 dict(channel='MEDICAL_VAT_SCOPE',previous='NO_CURRENT_NATIVE_SCOPE_UPDATE',current='EXISTING_VAT_HOOK_FORMULA_CONNECTED',formula='existing medical turnover*(1+medical VAT scope nominal flow/old turnover)',unresolved='scope and production VA bridge remain uncalibrated',policy_adopted=False),
 dict(channel='N3_PENSION',previous='NATIVE_DYNAMIC',current='NATIVE_DYNAMIC_PRESERVED',formula='contribution+fund returns-payout; DOMESTIC_TRANSFER retained',unresolved='national pension and social fund complete consolidation absent',policy_adopted=False),
 dict(channel='LEGACY_PENSION_SATELLITE',previous='FIXED_ZERO_ON_SQ_ENGINE',current='30_YEARS_ZERO_CONFIRMED_NO_SECOND_BENEFIT',formula='all five existing old satellite flows zero',unresolved='not a separate missing funded pension path',policy_adopted=False),
 dict(channel='ESTATE',previous='REPORTED_BASE_TIMES_COMMON_PRICE',current='LAGGED_REALIZED_PRICE_INTERFACE',formula='old reported transaction base and 40% wedge scale by prior realised/common price ratio',unresolved='separate asset prices, transaction count, national tax-base calibration absent',policy_adopted=False),
 dict(channel='POPULATION_LABOR_CORE_COMMON_DEFLATOR',previous='FIXED_EXTERNAL_COMMON',current='FIXED_EXTERNAL_COMMON',formula='unchanged source trajectory',unresolved='no supported new response function; full macro dynamics incomplete',policy_adopted=False),
 dict(channel='GENERAL_GOVERNMENT',previous='INCOMPLETE',current='INCOMPLETE_CL_CANDIDATE_ONLY',formula='cash PB, national-local interest, SFA, debt/assets and assumed refinancing',unresolved='social contributions, benefits, internal transfers, SFA attribution and actual maturities absent',policy_adopted=False)]
 dump(out/'Connection_Status.csv',statusrows)
 (out/'N3_Transition_Verification.json').write_text(json.dumps(result,indent=2)+'\n');write_report(out,summ,bound,result)
 print(json.dumps(result));assert not r.checks,r.checks[:8]

def write_report(out,summ,bound,v):
 ix={z['case']:z for z in summ};lines=['# N3移行期の財源制約・未接続動学の限定接続と年次計算','DRAFT / NON-CANONICAL / NO POLICY ADOPTION',
 '## 判定','算術・実装整合：'+('PASS' if not v['failed'] else 'FAIL')+'。税率・控除維持下の全期間SQ以上：条件付きで成立。移行期・完全動学・全国財政を含む頑健性：未成立。一般政府閉合、全国較正、人口労働・コア等の完全動学は未完了。',
 '## 移行期の原因と財源','前回DYN_MIX_CASHのSQ割れは2030年−7.595361兆円と2031年−0.067629兆円。2030年の追加primary余力26.751280兆円、追加支出前PB29.151280、利払い17.100000、正SFA13.900000。PB−利払いの現金黒字12.051280兆円から、正SFAも差し引いたため執行可能額がゼロになった。前回CASH_NEUTRALは現金制約に加え正SFA相当の債務増抑制条件を含んでいた。純粋な現金収支制約と区別が必要であり、前回のラベルだけから借入不可の帰結と一般化できない。',
 'DEBT_NONINCREASEは前回の保守的制約をそのまま比較対照として維持。CASH_ONLYはSFAを現金資源に使わず、PB−利払いの現金黒字を政府支出へ配分する。SFAは従来どおり債務ストックへ別計上。したがってSFAを無視したり税収に加算したケースではなく、償還と支出の選択を明示した候補である。後年資産が実在する場合だけ使用する別ケースも実行し、移行期は初期現金資産ゼロを保持。',
 '政府購入・公共投資の要求と実執行、未執行、企業資金、消費・所得、PB・利払い・SFA・債務・国債発行は年次台帳で結合した。未執行の要求額を将来使える現金とみなさない。供給上限は常に適用。2030年の消費減に対し購入・公共投資がゼロとなることが需要不足を作り、2031年には消費慣性・前年所得と投資資本の不足が残る。',
 '## 主結果（GDP−SQは実質兆円、債務は名目兆円）','| ケース | 2030 | 2035 | 2044 | 2055 | SQ割れ年数 | 最悪年 | 最悪差 | 2055債務 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for cid in ['PREV_DYN_BASE','PREV_DYN_MIX','PREV_DYN_MIX_CASH','PREV_CASH_STRESS','CASH_ONLY','G_FIRST_CASH','I_FIRST_CASH','DELAY1_CASH','MIN_SQ_AUTH10','CASH_FRONTLOAD5','VAT_CASH_ONLY','MEDICAL_CASH_ONLY','MEDICAL_SCOPE_CASH_ONLY','ESTATE_CASH_ONLY','ALL_BASE','ALL_FIXED_ROOM','ALL_DEBT_LIMIT','ALL_CASH_ONLY','ALL_MIN_AUTH20','ALL_CASH_DOM60','ALL_CASH_PUBLIC_Y0','ALL_CASH_STRESS','ALL_MIN_CASH_STRESS20','ALL_CASH_FRONTLOAD5','ALL_VAT_BASELINE_ANCHOR']:
  z=ix[cid];lines.append(f"| {cid} | {z['gap2030']:+.6f} | {z['gap2035']:+.6f} | {z['gap2044']:+.6f} | {z['gap2055']:+.6f} | {z['below_years']} | {z['worst_year']} | {z['worst_gap_trn']:+.6f} | {z['debt2055']:.6f} |")
 lines+=['判定許容はGDP−SQが−1e−7兆円以上。最小値探索では丸め誤差を避け、目標をSQ−1e−8兆円とする。表のゼロ近傍はこの数値許容内であり、経済的な負差を切り捨てたものではない。','## 限定資金調達と最小値の意味','MIN_SQは2030〜2032年に限定し、固定した政府購入50%・公共投資25%・企業投資75%の配分で各年の継承状態からSQへ届く最小執行額を二分探索する。借入・追加支出の容認は未採用候補。DEBT_NONINCREASEからの追加支出権限は償還減少だけで満たせることがあるため、権限額と実際の新規現金借入を区別した。CASH_ONLYを超える支出は実際の財政赤字・現金借入・後年利払いへ同時反映。前倒し投資は2029年に5兆円の支出を別候補として実行し、税収発生前の借入を無償財源としない。',
 '返済用余力を2035〜2040年の政府追加支出から控除する診断ケースでは、実現した現金黒字内でタグ付き返済を追跡し、実際の債務償還との整合を確認。SFA相当の償還抑制解除も実際の新規借入と同じと呼ばない。最小値は所与の配分・国内比率・年次順序・初期状態に条件付けた逐年最小で、全期間を最適化した数学的最小費用ではない。',
 '| 境界 | 成否側 | 総追加支出権限上限 | SQ割れ年数 | 最悪差 | 2030年以降の実際新規借入合計 | 2055債務 |','|---|---|---:|---:|---:|---:|---:|']
 for z in bound:
  if 'below_years' in z:lines.append(f"| {z['boundary']} | {z['side']} | {z['authority_cap_total_trn']:.9f} | {z['below_years']} | {z['worst_gap']:+.9f} | {z['actual_new_borrowing_after2029_trn']:.6f} | {z['debt2055']:.6f} |")
 lines+=['新規現金借入ゼロは2030年以降の追加支出についての結果。全ケースが継承する2026〜2029年の基準借入46.9兆円までゼロにした意味ではない。前倒し5兆円ケースの2029年追加現金借入は同年税フィードバック後約4.181兆円。MINの将来返済枠は追加支出権限に対する債務回復目標で、存在しない独立ローンの法的元本ではない。','## 新規接続と未接続','VATは既存tax_account/regular_account/sector_accountを呼び、標準・食料率と主KPI分岐を固定して価格・数量・税基礎・税収・家計／政府／企業帰着を再計算。主接続では当年固定コア税基礎へ前年の実現名目GDP／前年コア名目GDPを乗じる。これは既存企業利益基礎と同じ前年参照インターフェースをVATへ延長した未較正候補。固定基準N3の実現GDPを分母にする増分アンカーも別実行し、仕様依存を開示。追加支出そのものに別VAT率を掛けた税収を加算していない。改革差額の税を一般マクロ税proxyへ一度だけ接続。VAT価格を含む家計現金に加え、既存の数量代替式を新しい値で置換し、二重に数量効果を加えない。',
 '医療は既存の年齢別需要・N3の負担率補間・法定上限・家計／政府／保険者・既存財源分担を保持した原コードを隔離呼出し。人口・年齢構成は固定共通経路、取引価格は前年実現N/Yを共通価格に対する比率で入れ替える候補。所得別受診弾力性は既存にないため創作しない。医療課税基礎は既存vat_hookと同じ医療名目フロー／既存医療市場基礎の接続式を別チャンネルとして実行。医療未財源分を消さず、保険者補填は既存ストレス別条件を維持。',
 'N3年金拠出・基金・給付・DOMESTIC_TRANSFERは前回のネイティブComponents.stepを継続。旧SQ年金衛星は30年すべてゼロであり、新しいN3給付を重複追加しない。相続は既存報告取引基礎×共通価格という式に前年実現価格比を接続し、税率40%・取引量を固定。相続資産の価格・取引量の独立モデル、所得分布の全国較正は未接続。',
 '人口・労働・コア成長・共通デフレータは外生固定。無根拠な出生・就業・生産性の反応関数は追加しない。実現価格を特定部門の取引基礎へ返す局所インターフェースは、共通経路や他施策を上書きしない。完全N3動学・一般政府連結は未完了。年金・VAT・医療の会計整合PASSを全国較正PASSとしない。',
 '単独接続差分はConnection_Deltas、同時再計算はALL各ケース。単独差分の足し算を複合結果として使用していない。2030〜2035原因表はCause_2026_2035.csv、各年の税基礎・税額・医療未財源・旧年金状態はNative_Channel_Accountsを参照。',
 '医療衛星の利払い差額は国地方PBへ接続する際に除き、国地方側の再計算利払いと重複させない。医療衛星債務は診断内訳であり国地方債務へもう一度足さない。VAT課税ベースは前年GDPproxyによる接続で、家計消費・企業設備投資をそれぞれ独立に観測した全国取引税基礎ではない。価格・数量比は既存の率・転嫁率・弾力性に従い再計算し、倍率を合わせる新弾力性は追加していない。','## 財政限界と引渡し',f"今回{v['cases']}ケース・{v['annual_rows']}年次、検証{v['checks']}件・失敗{v['failed']}件。前回35,281件と先行12,311件のPASSを再利用し、4基準ケースのみ限定再現。借換・2041年以降フロー・SFA・社会保障・全債務金利は既存定義を再利用。一般政府・実際の満期別発行・SFA配賦・全国税基礎較正は未完了。",'実行：`python3 handoff/chatgpt-n3-transition-financing-full-dynamics-20261122/N3_Transition_Reproduce.py --root . --outdir /tmp/n3-transition-replay`。既存エンジンは読取専用、隔離ランタイムへの限定置換箇所はResolved_Transition_Simulate.py.txt。Medical_Initialization.jsonはCapture_Medical_Initialization.pyで固定原エンジンから再抽出可能。','税率・控除・本文・既存エンジン・固定成果物を変更していない。配分変更・前倒し・借入は未採用診断。正式政策採用・暫定改訂版なし。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。']
 (out/'SPE_N3_Transition_Financing_Full_Dynamics_Report_DRAFT_20261122.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--outdir',type=Path,required=True);a.add_argument('--smoke',action='store_true');z=a.parse_args();run(z.root.resolve(),z.outdir.resolve(),z.smoke)
