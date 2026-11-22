#!/usr/bin/env python3
"""Isolated N3 continuation: stock-flow cash closure and native policy-base feedback.
All coefficients below are diagnostic scenarios, not adopted policy or calibration.
Stdlib only. Run from any fixed checkout containing the pinned predecessor.
"""
import argparse,copy,csv,hashlib,importlib.util,json,math,os,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent; ROOT=P.parents[1]
OLD='handoff/chatgpt-n3-gdp-recirculation-counterfactual-20261122'; ND='handoff/chatgpt-n3-f-parity-implementation-20261122'; FD='handoff/chatgpt-national-fiscal-closure-20261121'; BD='handoff/chatgpt-n3-policy-burden-diagnosis-20261122'
PIN='293039bf1875d1910073e1b8c14543c57d76c173';REQUEST='9155b22d4ba4aef6cdf91b8ff3d0f521e7080f72';BASE='PARITY_CONNECTED_CANDIDATE';SQ='SQ_COMMON_ON'
def rd(p):return list(csv.DictReader(p.open()))
def n(r,k):return float(r.get(k) or 0.)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def spec(cid,**kw):
 d=dict(case=cid,g_share=.5,pi_share=.25,firm_rate=.75,domestic=.8,yield_public=.1,lag=1,cap_scale=1.,dynamic=False,room_mode='FIXED_PRIMARY',tail='HOLD',rate=.02,interest_mode='LEGACY_EXCESS_ONLY',rollover=.1,sfa_tail='ZERO',backfill=False,ss_growth=0.,ss_start=2041,kpi='FIXED',extra_service_cost=0.)
 d.update(kw);return d
class Runner:
 def __init__(self,root,out):
  self.root=root;self.out=out;self.checks=[];self.counter=0
  tr=json.loads((root/BD/'N3_Unchanged_Execution_Trace.json').read_text());self.base={t['year']:t for t in tr['records'] if t['case']==BASE};self.sq={t['year']:t for t in tr['records'] if t['case']==SQ};self.par=tr['parameters'][BASE]
  self.ci=json.loads((P/'Component_Initialization.json').read_text());self.cm=module('native_component',root/ND/'Components.py');self.fp=module('native_finance',root/FD/'National_Fiscal.py');self.old=module('prior_recirculation',root/OLD/'N3_GDP_Recirculation_Reproduce.py')
  self.funding={int(r['year']):r for r in rd(root/ND/'results/DOMESTIC_TRANSFER_Corporate_Funding_Stock.csv') if r['case']==BASE}
  self.official={int(r['year']):{k:float(v) if k.endswith('_trn') and v else v for k,v in r.items()} for r in rd(root/FD/'Official_Fiscal_Baseline_2025_2040.csv')};self.fb=self.fp.baseline({'tail':'NOMINAL_HOLD_2040'},self.official)
  self.primary={int(r['year']):n(r,'policy_primary_delta_trn') for r in rd(root/BD/'N3_Conditional_Fiscal_Primary_Bridge.csv')}
  fr=rd(root/ND/'results/Conditional_National_Local_Fiscal.csv');self.fiscal={int(r['year']):r for r in fr if r['case']==BASE and r['scenario']=='REFERENCE_CANDIDATE' and r['mode']=='DOMESTIC_TRANSFER'};self.sf={int(r['year']):r for r in fr if r['case']==SQ and r['scenario']=='REFERENCE_CANDIDATE' and r['mode']=='DOMESTIC_TRANSFER'}
  self.initdebt=self.official[2025]['CL_debt_end_trn'];self.vatrate={int(z['year']):n(z,'VAT_standard_rate_fixed') for z in rd(root/OLD/'N3_GDP_Recirculation_Annual_Comparison_2026_2055.csv') if z['case']=='BASE_N3'}
 def ck(self,name,error,tol=5e-7):
  self.counter+=1
  if not math.isfinite(error) or abs(error)>tol:self.checks.append(dict(check=name,error=error,tolerance=tol))
 def component(self):
  d=copy.deepcopy(self.ci);return self.cm.Components(d['config'],d['household'],d['pension']),SimpleNamespace(s=d['s'],deflators=d['deflators'],trajectory=d['trajectory'],elder=d['elder'],rows=[])
 def native_replay(self):
  co,md=self.component();prior=[]
  for y,t in self.base.items():
   md.rows.append(copy.deepcopy(t['medical']));p=co.step(y,md,prior)
   for k in ['policy_tax_delta_trn','policy_household_cash_delta_trn','policy_government_cost_delta_trn','policy_insurer_cash_delta_trn','policy_investment_delta_trn','pension_fund_stock_trn','pension_fund_contribution_trn','semi_med_fund_asset_trn']:
    self.ck('native_component_replay:'+str(y)+':'+k,p[k]-t['medical'][k])
   prior.append(copy.deepcopy(t['macro_row']))
 def fiscal_base(self,s,y):
  b=self.fb[y];o=self.official[min(y,2040)];scale=1.
  if y>2040:
   if s['tail']=='SQ_NOMINAL':scale=self.sq[y]['N']/self.sq[2040]['N']
   elif s['tail']=='GROW2':scale=1.02**(y-2040)
  # GA plus local ordinary accounts are an illustrative bridge, NOT SNA totals.
  # Strip central->local grants from expenses and local receipts, not twice.
  anchor=self.official[2040]
  exp_anchor=anchor['central_GA_primary_expenditure_trn']-anchor['central_GA_local_transfer_trn']+anchor['local_ordinary_expenditure_trn']-anchor['local_ordinary_debt_service_trn']
  rev_anchor=anchor['central_GA_nonbond_revenue_trn']+anchor['local_ordinary_nonbond_revenue_trn']-anchor['central_GA_local_transfer_trn']
  pbshift=(rev_anchor-exp_anchor)*(scale-1) if y>2040 else 0.
  ss_extra=o['central_GA_social_security_trn']*((1+s['ss_growth'])**max(0,y-s['ss_start']+1)-1)
  pb=b['CL_PB_trn']+pbshift-ss_extra
  sfa=b['stock_flow_adjustment_unallocated_trn']
  if y>2040 and s['sfa_tail']=='MEAN5':sfa=sum(self.fb[j]['stock_flow_adjustment_unallocated_trn'] for j in range(2036,2041))/5
  elif y>2040 and s['sfa_tail']=='PLUS1GDP':sfa=.01*self.sq[y]['N']
  return pb,sfa,ss_extra,pbshift,scale
 def simulate(self,s,record=True):
  par=self.par;C=I=K=privI=privK=pubI=pubK=0.;firmcash=0.;debt=self.initdebt;assets=0.;tax=self.base[2026]['tax'];prevN=self.base[2026]['N'];gap=0.;prior=[];pubhistory=[];pubflows=[];annual=[];closure=[];bridge=[]
  co,md=self.component()
  if s['kpi']=='FIXED':md.s['kpi']=False # pinned baseline has no freeze; no endogenous switch leaks
  ssqdebt=self.initdebt;ssqassets=0.
  for y in range(2026,2056):
   t=self.base[y];old=t['medical'];w=copy.deepcopy(old);d=t['coreD'];initial=y==2026;native={};policyshift=govshift=insshift=cashshift=investshift=0.
   if s['dynamic']:
    md.rows.append(copy.deepcopy(old));native=co.step(y,md,prior)
    policyshift=native['policy_tax_delta_trn']-old['policy_tax_delta_trn'];govshift=native['policy_government_cost_delta_trn']-old['policy_government_cost_delta_trn'];insshift=native['policy_insurer_cash_delta_trn']-old['policy_insurer_cash_delta_trn'];cashshift=native['policy_household_cash_delta_trn']-old['policy_household_cash_delta_trn'];investshift=native['policy_investment_delta_trn']-old['policy_investment_delta_trn']
    w.update(native);w['household_cash_delta_trn']=old['medical_only_household_cash_delta_trn']+native['policy_household_cash_delta_trn'];w['government_cost_delta_trn']=old['medical_only_government_cost_delta_trn']+native['policy_government_cost_delta_trn'];w['service_production_nominal_delta_trn']=old['service_production_nominal_delta_trn']+native['policy_service_VA_delta_trn']-old['policy_service_VA_delta_trn']
   f=self.funding[y];saving=-w['corporate_tax_delta_trn'];dividend=w['dividend_delta_trn'];origI=co.funding_rows[-1]['realized_investment_nominal_trn'] if s['dynamic'] else n(f,'realized_investment_nominal_trn')
   flow=saving-dividend-origI;firmbegin=firmcash;available=firmcash+flow
   privI=min(max(available,0.)/d,(1-par['lambda_I'])*privI+par['lambda_I']*s['firm_rate']*max(flow,0.)/d) if not initial else 0.;privatepaid=privI*d;firmcash=available-privatepaid
   b=self.fb[y];baselinepb,sfa,ssextra,tailshift,scale=self.fiscal_base(s,y)
   sqpb=baselinepb+n(self.sf[y],'CL_primary_delta_after_mapping_trn')
   sqinterest=self.interest(s,ssqdebt,ssqassets,b);sqz=self.fp.finance(ssqdebt,ssqassets,sqpb,sqinterest,sfa,s['rollover']);ssqdebt=sqz['CL_debt_end_candidate_trn'];ssqassets=sqz['CL_cash_assets_end_candidate_trn']
   inslevel=n(self.fiscal[y],'model_insurer_balance_delta_trn')+insshift;backfill=max(0.,-inslevel) if s['backfill'] else 0.
   primarychange=policyshift-govshift-backfill
   feedback=par['income_feedback']*gap*d
   cash=t['cash']+cashshift;ss=t['social'];pen=t['pension_ledger'];mpc=par['generic_mpc']
   Ctarget=par['domestic_share']*(mpc*(cash+feedback-ss['household'])+ss['weighted_demand']+pen['consumption_impulse_trn']-mpc*pen['household_cash_delta_trn']+w['quantity_nominal_volume_delta_trn']-mpc*w['quantity_replaced_price_benefit_trn']+(mpc-w['estate_mpc_candidate'])*w['wealth_tax_delta_trn'])/d
   if not initial:C=(1-par['lambda_C'])*C+par['lambda_C']*Ctarget;I=(1-par['lambda_I'])*I+par['lambda_I']*(t['invest_nom']+investshift)/d
   mature=pubhistory[-s['lag']]*(1-par['depreciation'])**(s['lag']-1) if len(pubhistory)>=s['lag'] else 0.
   supply=par['capital_yield']*(1-par['depreciation'])*(K+privK)+s['yield_public']*(1-par['depreciation'])*mature+(t['supply']-par['capital_yield']*(1-par['depreciation'])*t['Kprev'])
   capacity=t['coreY']+supply+s['cap_scale']*par['slack']*t['coreY']+t['education_level']
   basewant=t['coreY']+par['capacity_absorption']*supply+C+I+privI+t['education_nom']/d+t['education_level']+t['finite']+w['service_production_nominal_delta_trn']/d
   interest=self.interest(s,debt,assets,b)
   # Within-year fiscal resource constraint solved with bisection; tax map evaluated
   # from previous-year tax and nominal GDP, not repeatedly compounded per iteration.
   def evalroom(room):
    g=s['g_share']*room;pibudget=s['pi_share']*room
    pi=min(pibudget*s['domestic']/d,(1-par['lambda_I'])*pubI+par['lambda_I']*pibudget*s['domestic']/d) if not initial else 0.;pipay=pi*d/s['domestic'];spend=g+pipay
    desired=basewant+pi+g*s['domestic']/d;Y=min(desired,capacity);unmet=max(0.,desired-Y);nom=Y*d*(1+par['price_pressure_coefficient']*unmet/t['coreY'])
    tx=min(tax*(1+(nom/prevN-1)*par['elasticity'])*(.9 if y==2031 else 1.),nom*par['tax_cap_ratio']) if not initial else tax
    pbpre=n(self.fiscal[y],'CL_PB_candidate_trn')+(baselinepb-b['CL_PB_trn'])+primarychange+(tx-t['tax'])
    policyroom=max(0.,self.primary[y]+primarychange+tx-t['tax'])
    budget=max(0.,pbpre-interest-max(0.,sfa))
    return dict(g=g,pi=pi,pipay=pipay,spend=spend,Y=Y,nom=nom,tax=tx,pbpre=pbpre,desired=desired,unmet=unmet,policyroom=policyroom,budget=budget)
   room=max(0.,self.primary[y])
   if s['room_mode']!='FIXED_PRIMARY':
    caproom=max(0.,self.primary[y]+max(primarychange,0.)+1000.)
    def residual(r):
     z=evalroom(r)
     return r-z['policyroom'] if s['room_mode']=='CURRENT_PRIMARY' else max(r-z['policyroom'],z['spend']-z['budget'])
    lo=0.;hi=caproom
    if s['g_share']+s['pi_share']:
     assert residual(lo)<=1e-7 and residual(hi)>=0
     for _ in range(55):
      mid=(lo+hi)/2
      if residual(mid)>0:hi=mid
      else:lo=mid
     room=(lo+hi)/2
    else:room=0.
   z=evalroom(room);g=z['g'];pubI=z['pi'];spend=z['spend'];Y=z['Y'];nom=z['nom'];tax=z['tax'];pb=z['pbpre']-spend
   dbegin=debt;abegin=assets;fin=self.fp.finance(debt,assets,pb,interest,sfa,s['rollover']);debt=fin['CL_debt_end_candidate_trn'];assets=fin['CL_cash_assets_end_candidate_trn']
   pkbegin=privK;pubbegin=pubK;Kbegin=K
   if not initial:K=(1-par['depreciation'])*K+I;privK=(1-par['depreciation'])*privK+privI;pubK=(1-par['depreciation'])*pubK+pubI
   pubhistory.append(pubK);pubflows.append((y,pubI))
   gap=Y-t['coreY'];prevN=nom
   wage0=self.base[2026]['nominalwage_proxy'];shock=.99 if par['wage_shock_start']<=y<par['wage_shock_start']+2 else 1.
   wage=wage0*(d/self.base[2026]['coreD'])*shock*(1+par['wage_gap_elasticity']*gap/t['coreY'])
   resource=par['household_income_share']*t['coreN']+cash+feedback
   r=copy.deepcopy(t['macro_row']);r.update(real_gdp_trn=Y,nominal_gdp_trn=nom,nominal_wage_proxy_man=wage,real_growth_pct=(Y/prior[-1]['real_gdp_trn']-1)*100 if prior else 0.,household_disposable_nominal_trn=resource,parity_real_cash_income_per_person=(resource-t['vat']['household'])/d/t['demography']['population']);prior.append(r)
   row=dict(case=s['case'],year=y,dynamic=s['dynamic'],room_mode=s['room_mode'],domestic=s['domestic'],public_yield=s['yield_public'],public_lag=s['lag'],SQ_real_GDP_trn=self.sq[y]['Y'],real_GDP_trn=Y,GDP_minus_SQ_trn=Y-self.sq[y]['Y'],GDP_change_vs_BASE_N3_trn=Y-t['Y'],nominal_GDP_trn=nom,consumption_real_trn=n(t['macro_row'],'household_consumption_real_proxy_trn')+C-t['C'],SQ_consumption_real_trn=n(self.sq[y]['macro_row'],'household_consumption_real_proxy_trn'),private_investment_real_trn=n(t['macro_row'],'capital_replacement_investment_real_trn')+I+privI,extra_private_investment_real_trn=privI,extra_public_investment_real_trn=pubI,SQ_private_investment_real_trn=n(self.sq[y]['macro_row'],'capital_replacement_investment_real_trn')+self.sq[y]['I'],capital_total_real_proxy_trn=n(t['macro_row'],'capital_total_real_trn')-t['K']+K+privK+pubK,government_purchase_nominal_trn=g,public_investment_nominal_trn=z['pipay'],policy_tax_delta_trn=w['policy_tax_delta_trn'],macro_tax_proxy_trn=tax,total_tax_diagnostic_proxy_trn=tax+t['direct']+policyshift,SQ_tax_diagnostic_proxy_trn=self.sq[y]['tax']+self.sq[y]['direct'],household_policy_cash_nominal_trn=cash,household_resource_DI_proxy_trn=resource,N3_firm_cash_trn=firmcash,pension_fund_end_trn=w['pension_fund_stock_trn'],pension_contribution_trn=w['pension_fund_contribution_trn'],pension_benefit_delta_trn=w['pension_benefit_delta_trn'],CL_PB_candidate_trn=pb,SQ_CL_PB_same_fiscal_scenario_trn=sqpb,CL_debt_candidate_trn=debt,SQ_CL_debt_same_fiscal_scenario_trn=ssqdebt,CL_assets_candidate_trn=assets,CL_interest_candidate_trn=interest,CL_new_borrowing_trn=fin['CL_new_cash_borrowing_candidate_trn'],CL_gross_issue_assumed_trn=fin['CL_gross_issue_with_assumed_refinancing_trn'],supply_real_trn=supply,supply_ceiling_real_trn=capacity,unmet_demand_real_trn=z['unmet'],lagged_wage_base_factor=co.dynamic_rows[-1]['wage_base_factor'] if s['dynamic'] else None,lagged_profit_base_factor=co.dynamic_rows[-1]['corporate_profit_base_factor'] if s['dynamic'] else None,GG_PB=None,GG_debt=None,actual_gross_bond_issue=None,full_calibration=False,VAT_standard_rate=self.vatrate[y],VAT_schedule_fixed=s['kpi']=='FIXED',VAT_base_endogenous=False,medical_base_endogenous=False)
   annual.append(row)
   c=dict(case=s['case'],year=y,baseline_PB_trn=baselinepb,post2040_flow_scale=scale,post2040_PB_shift_trn=tailshift,central_GA_social_security_extra_trn=ssextra,insurer_balance_delta_trn=inslevel,insurer_backfill_trn=backfill,policy_primary_change_trn=primarychange,available_primary_delta_trn=z['policyroom'],fixed_primary_delta_trn=self.primary[y],nominal_allocation_room_trn=room,cash_budget_after_interest_SFA_trn=z['budget'],government_spend_trn=spend,government_import_leak_trn=spend*(1-s['domestic']),public_capital_domestic_formation_trn=pubI*d,primary_balance_before_additional_spend_trn=z['pbpre'],PB_trn=pb,interest_trn=interest,SFA_trn=sfa,debt_begin_trn=dbegin,debt_end_trn=debt,assets_begin_trn=abegin,assets_end_trn=assets,new_cash_borrowing_trn=fin['CL_new_cash_borrowing_candidate_trn'],cash_debt_redemption_trn=fin['CL_cash_surplus_debt_redemption_candidate_trn'],asset_draw_trn=fin['CL_cash_asset_draw_candidate_trn'],asset_addition_trn=fin['CL_cash_asset_addition_candidate_trn'],rollover_share=s['rollover'],assumed_gross_issue_trn=fin['CL_gross_issue_with_assumed_refinancing_trn'],assumed_gross_redemption_trn=fin['CL_gross_redemption_with_assumed_refinancing_trn'],firm_begin_trn=firmbegin,firm_source_tax_saving_trn=saving,firm_dividend_trn=dividend,firm_original_investment_paid_trn=origI,firm_additional_investment_paid_trn=privatepaid,firm_end_trn=firmcash,unallocated_SFA=True,SS_baseline_complete=False,GA_local_to_SNA_reconciliation_complete=False)
   closure.append(c)
   bridge.append(dict(case=s['case'],year=y,dynamic=s['dynamic'],policy_tax_fixed_reference_trn=old['policy_tax_delta_trn'],policy_tax_recomputed_trn=w['policy_tax_delta_trn'],policy_tax_change_trn=policyshift,labor_tax_recomputed_trn=w['labour_business_flat30_tax_delta_trn'],financial_tax_recomputed_trn=w['household_financial20_tax_delta_trn'],corporate_tax_recomputed_trn=w['corporate_tax_delta_trn'],household_cash_fixed_reference_trn=t['cash'],household_cash_recomputed_trn=cash,household_cash_change_trn=cashshift,policy_government_cost_change_trn=govshift,policy_insurer_change_trn=insshift,original_investment_target_change_trn=investshift,pension_fund_fixed_trn=old['pension_fund_stock_trn'],pension_fund_recomputed_trn=w['pension_fund_stock_trn'],pension_contribution_recomputed_trn=w['pension_fund_contribution_trn'],lagged_wage_factor=row['lagged_wage_base_factor'],lagged_profit_factor=row['lagged_profit_base_factor'],labor_rate=.3,financial_rate=.2,estate_rate=.4,corporate_rates='0.20/0.16_qualified',VAT_standard_rate=self.vatrate[y],scope='NATIVE_POLICY_COMPONENT_PARTIAL_DYNAMIC_VAT_MEDICAL_CORE_FROZEN',KPI_frozen=s['kpi']=='FIXED'))
   if record:
    pre=s['case']+':'+str(y)+':'
    self.ck(pre+'firm_funding',firmcash-firmbegin-saving+dividend+origI+privatepaid);self.ck(pre+'firm_nonnegative',min(0.,firmcash));self.ck(pre+'budget_identity',debt-assets-dbegin+abegin+pb-interest-sfa);self.ck(pre+'gross_stock',debt-dbegin-fin['CL_gross_issue_with_assumed_refinancing_trn']+fin['CL_gross_redemption_with_assumed_refinancing_trn']-sfa);self.ck(pre+'PB',pb-z['pbpre']+spend);self.ck(pre+'GDP_cap',Y-min(z['desired'],capacity));self.ck(pre+'tax_sum',w['policy_tax_delta_trn']-w['labour_business_flat30_tax_delta_trn']-w['household_financial20_tax_delta_trn']-w['corporate_tax_delta_trn']-.2*w['dividend_delta_trn']-w['wealth_tax_delta_trn'])
    if not initial:self.ck(pre+'private_K',privK-.95*pkbegin-privI);self.ck(pre+'public_K',pubK-.95*pubbegin-pubI)
    if s['room_mode']=='CASH_NEUTRAL':
     self.ck(pre+'cash_constraint',max(0.,spend-z['budget']),1e-6);self.ck(pre+'allocation_envelope',max(0.,room-z['policyroom']),1e-6)
    independent_public_supply=s['yield_public']*sum(v*(1-par['depreciation'])**(y-j) for j,v in pubflows if j<=y-s['lag'])
    self.ck(pre+'mature_public_supply',s['yield_public']*(1-par['depreciation'])*mature-independent_public_supply)
    if s['dynamic']:
     penrow=co.pension[-1];self.ck(pre+'pension_stock',penrow['fund_end_trn']-penrow['fund_begin_trn']-penrow['fund_return_trn']-penrow['fund_contribution_trn']+penrow['fund_payout_trn']);self.ck(pre+'lag_wage',co.dynamic_rows[-1]['wage_base_factor']-(prior[-2]['nominal_wage_proxy_man']/co.cfg['sq_wage_nominal_man'][y-2027] if y>2026 else 1.))
  return annual,closure,bridge
 def interest(self,s,debt,assets,b):
  if s['interest_mode']=='ALL_STOCK':return s['rate']*(debt-assets)
  return b['CL_net_interest_trn']*min(1.,debt/b['CL_debt_begin_trn'])+s['rate']*max(0.,debt-b['CL_debt_begin_trn'])-s['rate']*assets

def summary(s,rows,led):
 ix={r['year']:r for r in rows};bad=[r for r in rows if r['GDP_minus_SQ_trn']< -1e-7];worst=min(rows,key=lambda r:r['GDP_minus_SQ_trn']);last=ix[2055]
 return dict(case=s['case'],all_years_SQ=not bad,first_below_year=bad[0]['year'] if bad else None,below_years=len(bad),worst_year=worst['year'],worst_gap_trn=worst['GDP_minus_SQ_trn'],gap2035=ix[2035]['GDP_minus_SQ_trn'],gap2044=ix[2044]['GDP_minus_SQ_trn'],gap2055=last['GDP_minus_SQ_trn'],annual_gap_sum_trn_years=sum(r['GDP_minus_SQ_trn'] for r in rows),PB2055=last['CL_PB_candidate_trn'],debt2055=last['CL_debt_candidate_trn'],debt_GDP2055_pct=100*last['CL_debt_candidate_trn']/last['nominal_GDP_trn'],assets2055=last['CL_assets_candidate_trn'],tax2055=last['total_tax_diagnostic_proxy_trn'],policy_tax2055=last['policy_tax_delta_trn'],fund2055=last['pension_fund_end_trn'],extra_spend_cumulative=sum(r['government_spend_trn'] for r in led),new_borrowing_cumulative=sum(r['new_cash_borrowing_trn'] for r in led),conditional_arithmetic_only=True,robust_policy_success=False)

def run(root,out):
 out.mkdir(parents=True,exist_ok=True);r=Runner(root,out);r.native_replay()
 # The unchanged source inputs and predecessor results are read from pinned git bytes.
 receipts=[]
 for commit,directory in [(PIN,OLD),('37c3399f9c553673a79ba1298fc68d758a77055e',ND)]:
  paths=[str(f.relative_to(root)) for f in (root/directory).iterdir() if f.is_file() and (directory==OLD or f.name in ['Inputs.json','Components.py','Macro_Adapter.py','Model.py'])]
  for path in paths:
   b=subprocess.check_output(['git','show',commit+':'+path],cwd=root);assert (root/path).read_bytes()==b
   receipts.append(dict(commit=commit,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 # A compact input initialization was captured from the unchanged existing engine.
 # It is checked by replay of native Components.step against fixed annual ledgers.
 annual=[];fiscal=[];bridge=[];summ=[];definitions=[];cache={}
 def execute(s):
  a,l,b=r.simulate(s);annual.extend(a);fiscal.extend(l);bridge.extend(b);z=summary(s,a,l);summ.append(z);definitions.append(s);cache[s['case']]=(a,l,b);return z
 for s in [spec('FIX_BASE',g_share=0.,pi_share=0.,firm_rate=0.),spec('FIX_MIX'),spec('FIX_NO_FIRM',firm_rate=0.),spec('FIX_PUBLIC75',g_share=0.,pi_share=.75,firm_rate=0.),spec('FIX_G75_FIRM75',g_share=.75,pi_share=0.),spec('FIX_DOM60',domestic=.6),spec('FIX_PUBLIC75_Y0',g_share=0.,pi_share=.75,firm_rate=0.,yield_public=0.),spec('FIX_MIX_Y0',yield_public=0.),spec('DYN_BASE',g_share=0.,pi_share=0.,firm_rate=0.,dynamic=True),spec('DYN_MIX',dynamic=True),spec('DYN_DOM60',dynamic=True,domestic=.6),spec('DYN_MIX_Y0',dynamic=True,yield_public=0.),spec('DYN_MIX_CURRENT',dynamic=True,room_mode='CURRENT_PRIMARY'),spec('DYN_MIX_CASH',dynamic=True,room_mode='CASH_NEUTRAL'),spec('FIX_MIX_CASH',room_mode='CASH_NEUTRAL')]:execute(s)
 # Targeted tail, social security, SFA, interest and gross refinancing diagnostics.
 variations=[('TAIL_SQ',dict(tail='SQ_NOMINAL')),('TAIL_2',dict(tail='GROW2')),('SS_2',dict(ss_growth=.02)),('SS_3',dict(ss_growth=.03)),('SFA_MEAN5',dict(sfa_tail='MEAN5')),('SFA_1GDP',dict(sfa_tail='PLUS1GDP')),('INS_BACKFILL',dict(backfill=True)),('I_ALL_2',dict(interest_mode='ALL_STOCK',rate=.02)),('I_ALL_4',dict(interest_mode='ALL_STOCK',rate=.04)),('I_EXCESS_4',dict(rate=.04)),('ROLL20',dict(rollover=.2)),('COMBINED_STRESS',dict(tail='SQ_NOMINAL',ss_growth=.03,sfa_tail='PLUS1GDP',backfill=True,interest_mode='ALL_STOCK',rate=.04,rollover=.2))]
 for suffix,kw in variations:
  execute(spec('DYN_'+suffix,dynamic=True,**kw))
  if suffix in ['SS_3','SFA_MEAN5','I_ALL_4','COMBINED_STRESS']:execute(spec('CASH_'+suffix,dynamic=True,room_mode='CASH_NEUTRAL',**kw))
 for lag in [3,5]:execute(spec('DYN_LAG'+str(lag),dynamic=True,lag=lag));execute(spec('FIX_LAG'+str(lag),lag=lag))
 execute(spec('DYN_SLACK_ZERO',dynamic=True,cap_scale=0.));execute(spec('FIX_SLACK_ZERO',cap_scale=0.))
 # Verify exact predecessor reproduction, not rerun all predecessor checks.
 oldrows={(z['case'],int(z['year'])):z for z in rd(root/OLD/'N3_GDP_Recirculation_Annual_Comparison_2026_2055.csv')}
 pairs={'FIX_BASE':'BASE_N3','FIX_MIX':'G50_PUBLIC_I25_FIRM75','FIX_NO_FIRM':'G50_PUBLIC_I25','FIX_PUBLIC75':'PUBLIC_I_75','FIX_G75_FIRM75':'G75_FIRM75','FIX_DOM60':'MIX_DOMESTIC_60','FIX_PUBLIC75_Y0':'PUBLIC_I75_YIELD_ZERO','FIX_MIX_Y0':'MIX_PUBLIC_YIELD_ZERO'}
 for new,old in pairs.items():
  for x in cache[new][0]:
   y=x['year'];o=oldrows[old,y]
   for key in ['real_GDP_trn','policy_tax_delta_trn','CL_PB_candidate_trn','CL_debt_candidate_trn']:
    ok={'policy_tax_delta_trn':'N3_policy_tax_fixed_trn'}.get(key,key);r.ck('predecessor:'+new+str(y)+key,x[key]-n(o,ok),3e-6)
 for x in cache['DYN_BASE'][0]:
  for key in ['real_GDP_trn','policy_tax_delta_trn','pension_fund_end_trn']:
   other=next(z for z in cache['FIX_BASE'][0] if z['year']==x['year']);r.ck('zero_extra_dynamic_replay:'+str(x['year'])+key,x[key]-other[key],3e-6)
 # Refunding/reissuing gross bonds cannot affect net financing or real GDP.
 for a,b in zip(cache['DYN_MIX'][0],cache['DYN_ROLL20'][0]):
  for key in ['real_GDP_trn','CL_debt_candidate_trn','CL_PB_candidate_trn']:r.ck('rollover_neutral:'+str(a['year'])+key,a[key]-b[key])
 bounds=[]
 templates=[('MIX',.5,.25,.75),('MIX_NO_FIRM',.5,.25,0.),('PUBLIC75',0.,.75,0.),('G75_FIRM75',.75,0.,.75)]
 for name,g,pi,firm in templates:
  for cy in ([0.,.05,.1] if pi else [0.]):
   for lag in ([1,3,5] if pi else [1]):
    for dynamic in ([False,True] if name=='MIX' and lag==1 else [False]):
     base=spec('BOUND',g_share=g,pi_share=pi,firm_rate=firm,yield_public=cy,lag=lag,dynamic=dynamic)
     def score(dom):
      sp={**base,'domestic':dom};a,l,b=r.simulate(sp,record=False);return min(x['GDP_minus_SQ_trn'] for x in a),a,l
     lower=.6;upper=1.;sl,al,ll=score(lower);su,au,lu=score(upper)
     samples=[score(.6+.05*j)[0] for j in range(9)]
     r.ck('boundary_sample_monotonic:'+name+str(cy)+str(lag)+str(dynamic),sum(min(0.,b-a) for a,b in zip(samples,samples[1:])),1e-6)
     if su< -1e-7:
      status='NO_SUCCESS_IN_0.6_1.0';threshold=None;low=upper;high=None
     elif sl>= -1e-7:
      status='SUCCESS_ALREADY_AT_0.6';threshold=lower;low=None;high=lower
     else:
      status='BRACKETED';lo=lower;hi=upper
      for _ in range(22):
       mid=(lo+hi)/2;sm,_,_=score(mid)
       if sm>= -1e-7:hi=mid
       else:lo=mid
      low=lo;high=hi;threshold=hi
     cid=f'B_{name}_Y{cy}_L{lag}_D{int(dynamic)}'
     record=dict(boundary=cid,template=name,dynamic=dynamic,public_yield=cy,lag=lag,domain_low=.6,domain_high=1.,status=status,failed_domestic_lower=low,successful_domestic_upper=high,threshold_upper=threshold,bracket_width=(high-low) if high is not None and low is not None else None,tolerance_domestic=.4/2**22,threshold_not_calibration=True)
     for label,dom in [('FAIL',low),('PASS',high)]:
      if dom is None:continue
      sp={**base,'case':cid+'_'+label,'domestic':dom};z=execute(sp)
      for k in ['below_years','worst_year','worst_gap_trn','gap2035','gap2044','gap2055']:record[label+'_'+k]=z[k]
     bounds.append(record)
 # Direct limited grid fixes domestic=0.6/0.8/1 and public yield=0/0.05/0.1.
 for dom in [.6,.8,1.]:
  for cy in [0.,.05,.1]:
   if dom==.8 and cy in [0.,.1]:continue
   execute(spec(f'GRID_D{dom}_Y{cy}',domestic=dom,yield_public=cy))
 # Bracket public yield at domestic 0.8, holding all other assumptions fixed.
 for name,g,pi,firm in templates[:3]:
  sp=spec('YBOUND',g_share=g,pi_share=pi,firm_rate=firm)
  def getyield(v):
   a,l,b=r.simulate({**sp,'yield_public':v},record=False);return min(z['GDP_minus_SQ_trn'] for z in a)
  lo=0.;hi=.1
  if getyield(0.)>=-1e-7:status='SUCCESS_AT_ZERO';hi=0.;lo=None
  elif getyield(.1)<-1e-7:status='NO_SUCCESS_0_0.1';hi=None;lo=.1
  else:
   status='BRACKETED'
   for _ in range(22):
    mid=(lo+hi)/2
    if getyield(mid)>=-1e-7:hi=mid
    else:lo=mid
  bounds.append(dict(boundary='PUBLIC_YIELD_'+name,template=name,dynamic=False,domestic=.8,status=status,failed_public_yield_lower=lo,successful_public_yield_upper=hi,bracket_width=(hi-lo) if hi is not None and lo is not None else None,threshold_not_calibration=True))
 # Verify all roots remain bracketed using stored annual endpoints, incl. worst year.
 for z in bounds:
  if z['status']=='BRACKETED' and 'failed_domestic_lower' in z:
   r.ck('root_fail:'+z['boundary'],max(z['FAIL_worst_gap_trn']+1e-7,0.),1e-10);r.ck('root_pass:'+z['boundary'],min(z['PASS_worst_gap_trn']+1e-7,0.),1e-10)
 dump(out/'N3_GDP_Robustness_Annual_Comparison_2026_2055.csv',annual);dump(out/'N3_GDP_Robustness_Fiscal_Closure.csv',fiscal);dump(out/'N3_GDP_Robustness_Dynamic_Tax_Household_Bridge.csv',bridge);dump(out/'N3_GDP_Robustness_Case_Summary.csv',summ);dump(out/'N3_GDP_Robustness_Case_Definitions.csv',definitions);dump(out/'N3_GDP_Robustness_Boundary_Cases.csv',bounds)
 # Statistical public baseline and boundary reconciliation remain distinct outputs.
 oRows=[]
 for y,b in r.fb.items():
  o=r.official[min(y,2040)];primary=o['central_GA_primary_expenditure_trn']-o['central_GA_local_transfer_trn']+o['local_ordinary_expenditure_trn']-o['local_ordinary_debt_service_trn'];revenue=o['central_GA_nonbond_revenue_trn']+o['local_ordinary_nonbond_revenue_trn']-o['central_GA_local_transfer_trn'];accountPB=revenue-primary
  oRows.append(dict(year=y,official_until2040=y<=2040,SNA_CL_PB_or_2040_hold_trn=b['CL_PB_trn'],GA_local_ordinary_net_revenue_proxy_trn=revenue,GA_local_ordinary_net_primary_expenditure_proxy_trn=primary,GA_local_ordinary_PB_proxy_trn=accountPB,SNA_minus_account_PB_residual_trn=b['CL_PB_trn']-accountPB,central_social_security_budget_trn=o['central_GA_social_security_trn'],central_local_transfer_excluded_both_sides_trn=o['central_GA_local_transfer_trn'],CL_baseline_interest_trn=b['CL_net_interest_trn'],debt_begin_trn=b['CL_debt_begin_trn'],debt_end_trn=b['CL_debt_end_trn'],SFA_unallocated_trn=b['stock_flow_adjustment_unallocated_trn'],SS_fund_baseline_revenue=None,SS_fund_baseline_benefits=None,SS_fund_internal_transfers=None,GG_PB=None,GG_debt=None,actual_bond_issue=None))
 dump(out/'Fiscal_Official_Baseline_Boundary_Map.csv',oRows)
 for path in ['handoff/chatgpt-n3-policy-burden-diagnosis-20261122/N3_Unchanged_Execution_Trace.json', 'handoff/chatgpt-n3-policy-burden-diagnosis-20261122/N3_Conditional_Fiscal_Primary_Bridge.csv', 'handoff/chatgpt-national-fiscal-closure-20261121/National_Fiscal.py', 'handoff/chatgpt-national-fiscal-closure-20261121/Fiscal_Inputs.json', 'handoff/chatgpt-national-fiscal-closure-20261121/Official_Fiscal_Baseline_2025_2040.csv', 'handoff/chatgpt-national-fiscal-closure-20261121/SNA2024_Sector_Snapshot.csv', 'handoff/chatgpt-national-fiscal-closure-20261121/Statistical_Source_Receipts.json', 'handoff/chatgpt-national-fiscal-closure-20261121/Statistical_Cell_Map.csv', 'handoff/chatgpt-n3-f-parity-implementation-20261122/results/DOMESTIC_TRANSFER_Corporate_Funding_Stock.csv', 'handoff/chatgpt-n3-f-parity-implementation-20261122/results/Conditional_National_Local_Fiscal.csv', 'handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-request-20261122/SPE_Work_N3_GDP_Robustness_Fiscal_Dynamics_Request_20261122.md']:
  b=subprocess.check_output(['git','show',REQUEST+':'+path],cwd=root);assert (root/path).read_bytes()==b
  receipts.append(dict(commit=REQUEST,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 (out/'Input_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 result=dict(status='PASS_PARTIAL_DYNAMIC_CONDITIONAL' if not r.checks else 'FAIL',checks=r.counter,failed=len(r.checks),failures=r.checks,case_count=len(summ),annual_rows=len(annual),boundary_records=len(bounds),predecessor_cases=29,predecessor_rows=870,predecessor_checks_reused=12311,predecessor_verification_not_rerun=True,native_component_replay=True,baseline_dynamic_reproduction=True,native_dynamic_tax_wage_corporate_pension=True,VAT_and_medical_bases_frozen=True,full_N3_dynamic_complete=False,general_government_closure_complete=False,robustness='NOT_ESTABLISHED_FAILURE_CASES_EXIST',policy_adopted=False,source_files_modified=False)
 (out/'N3_GDP_Robustness_Verification.json').write_text(json.dumps(result,indent=2)+'\n')
 write_report(out,summ,bounds,result)
 print(json.dumps(result));assert not r.checks,r.checks[:8]

def write_report(out,summ,bounds,v):
 ix={z['case']:z for z in summ}
 lines=['# N3 GDP頑健性・財政閉合・政策税基礎動学接続調査','DRAFT / NON-CANONICAL / ISOLATED DIAGNOSTIC / NOT POLICY ADOPTION',
 '## 判定','①算術・実装整合：'+('PASS' if not v['failed'] else 'FAIL')+'。②条件付き全期間SQ以上：成立するケースあり。③現実的条件・財政・動学・較正を含む頑健性：未成立。国内波及率、財源制約、公共資本生産性による失敗境界があり、一般政府・全国税基礎較正とVAT・医療基礎の完全動学は未完了。',
 '既存29ケース・870年次・12,311検証失敗0を再利用。前回の主要8ケースのみ照合、既存PASS全件の再監査はしていない。今回の改善は、成立境界の数値化、当年財源制約の同時解、既存Components.stepを用いた政策税・家計・企業・年金ループの接続である。',
 '## 主な年次結果（実質GDP差は兆円、PB・債務は名目兆円）',
 '| ケース | 2035差 | 2044差 | 2055差 | SQ割れ年数 | 最悪年 | 最悪差 | 2055 PB | 2055債務 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for cid in ['FIX_BASE','FIX_MIX','FIX_DOM60','FIX_MIX_Y0','FIX_PUBLIC75_Y0','DYN_BASE','DYN_MIX','DYN_DOM60','DYN_MIX_Y0','DYN_MIX_CURRENT','DYN_MIX_CASH','FIX_MIX_CASH','DYN_TAIL_SQ','DYN_SS_3','DYN_SFA_MEAN5','DYN_I_ALL_4','DYN_ROLL20','DYN_COMBINED_STRESS','CASH_COMBINED_STRESS','DYN_LAG5','DYN_SLACK_ZERO']:
  z=ix[cid];lines.append(f"| {cid} | {z['gap2035']:+.6f} | {z['gap2044']:+.6f} | {z['gap2055']:+.6f} | {z['below_years']} | {z['worst_year']} | {z['worst_gap_trn']:+.6f} | {z['PB2055']:.6f} | {z['debt2055']:.6f} |")
 lines+=[f"主複合の政策税基礎を内生化すると、2055年政策税差額は固定時{ix['FIX_MIX']['policy_tax2055']:.6f}→{ix['DYN_MIX']['policy_tax2055']:.6f}兆円、基金残高は{ix['FIX_MIX']['fund2055']:.6f}→{ix['DYN_MIX']['fund2055']:.6f}兆円。全期間SQ以上は維持するが2055年GDP差は{ix['DYN_MIX']['gap2055']-ix['FIX_MIX']['gap2055']:+.6f}兆円縮小した。",'当年の利払い・正SFAまで賄う追加借入なし条件では、固定余力の成功ケースも2030年の還流が制約され全期間条件に失敗する。早期投資を後年に追い付かせても、全期間判定の失敗を取り消さない。固定還流の金利ストレスでGDPが不変なのは財政から実行額へ戻していないためで、財政頑健性の証拠ではない。', '## 国内波及・公共資本の数値境界','政府購入50%、公共投資25%、企業残余フロー75%がMIX。PUBLIC75は公共投資75%のみ、G75_FIRM75は政府購入75%・企業75%。配分の母数は正の追加primary余力。企業75%は法人減税源泉から配当と既存投資の実執行を控除した当年残余フローであり、ストック全額ではない。',
 '| 配分 | 税基礎内生 | 公共資本係数 | 供給ラグ年 | 成立国内比率上端 | 直下失敗値 | 境界幅 |','|---|---|---:|---:|---:|---:|---:|']
 for z in bounds:
  if z.get('lag')==1:
   lines.append('| '+str(z['template'])+' | '+str(z['dynamic'])+' | '+str(z['public_yield'])+' | 1 | '+str(z.get('successful_domestic_upper'))+' | '+str(z.get('failed_domestic_lower'))+' | '+str(z.get('bracket_width'))+' |')
 lines+=['探索域は国内比率0.6〜1.0、公共資本の年次供給係数0〜0.1。係数0.1は年次の実質供給増／残存追加実質資本であり、生産弾力性ではない。国内比率二分探索は22回（幅約9.54e−8）、許容GDP差−1e−7兆円。失敗・成功両端の年次系列もCSVへ保存。SUCCESS_ALREADY_AT_0.6は域内の下限でも成立した意味で、数学的な最小値0.6と断定しない。NO_SUCCESSは探索域内で不成立。公共資本係数の境界も別行で表示。二分探索は単調な診断経路を前提とする局所境界であり全国較正や確率的信頼区間ではない。',
 '公共投資需要は当年支払×国内比率／共通デフレータ。投資調整速度0.6・資金上限制約、資本減耗5%。供給寄与は形成後1/3/5年から。遅延中も減耗した当該過去資本を供給へ用いる（ラグ追加年数分も減耗）。政府購入は当年需要のみ。供給上限は共通余剰能力2%を保持し、ゼロ余剰能力も隔離感度。未充足需要はGDPに足さない。',
 '## 財政閉合・実現可能性','FIXED_PRIMARYは旧母数固定、CURRENT_PRIMARYは当年の政策税・政府支出・一般マクロ税による追加primary余力へ更新。CASH_NEUTRALは配分母数を当年追加primary余力以下とした上で、実執行額を「追加支出前PB−利払い−正のSFA」以下に制約する。購入50%・公共投資25%の配分上限を同一母数で保ち、未執行分は財政へ残す。既存赤字がある場合に既存支出を無断削減せず、追加還流をゼロまで制約する。財源とGDP・マクロ税が同時に決まるので各年55回二分探索、過去税を各試行で重複複利にしない。これは追加還流による新規現金借入を避ける条件で、債務償還ゼロ・赤字一切なしを保証しない。',
 '2041年以降はHOLD（前回の2040年名目据置）に加え、SQ名目GDP比延伸・年2%延伸を実行。国一般会計と地方普通会計の歳入・primary歳出は中央地方移転を両側から除いて統合し、SNA国地方PBとの差額を境界残余として保つ。延伸時はこの会計proxyの歳入・歳出を同じ率で延伸した増分だけをSNA PBへ加える。残余の内訳が未同定のため、これを一般政府へ完全再構成したとは扱わない。',
 '社会保障ストレスは国一般会計社会保障費の2040年額を足場に、2041年以降年2/3%増の「据置超過分のみ」を費用控除。既存基準に社会保障がないとみなして全額再控除しない。年金・医療・介護の国地方・社会保障基金全体の将来推計ではなく、制度間移転・給付内訳は未接続。保険者のモデル上の対SQ赤字差額を全額公費補填する別ケースも実行し、内部移転を資源増と扱わない。',
 'SFAは2026〜2040年の公式債務変動−収支から計算された未配賦残余。2041年以降ゼロ、2036〜2040年平均継続、SQ名目GDPの1%というストレスを比較。平均継続・1%は予測ではない。正SFAを現金財源として使わず、現金制約ケースでは債務非増加余力からも控除する。',
 '金利2%を既存債務超過分だけに掛ける旧式では、債務が公式基準未満の間は2→4%感度が効かない。この限界を明示し、全期首債務・現金資産に2/4%を適用する即時借換ストレスを別実行。現実の満期別利率更新ではない。借換10/20%は仮定総発行・総償還を同額増やすだけでPB・純債務・GDPへ影響しないことを検証。実際の国債総発行は満期別データとの将来接続がなく空欄。',
 '財政資金恒等式は検証済みだが、国地方候補を一般政府や全国財政持続可能性PASSと呼ばない。公的年金基金資産を政府債務から差し引かず、家計・企業の現金も公的還流財源に使わない。',
 '## 政策税・家計・年金の接続範囲','DYNは既存N3 Components.stepをそのまま読込み、前年の改善後名目GDP／共通基準GDPと、前年改善後賃金proxy／SQ賃金proxyを既存の課税・企業利益・年金拠出へ戻した。家計所得・旧税比較基礎を同倍率で再計算し、差額政策税だけを一般マクロ税へ一度加算。配当課税20%、法人税20%／条件適合16%、労働30%、金融20%、相続40%と導入率は変更していない。全国納税者分布は既存の合成分布のまま。',
 '毎年の順序は前年GDP・賃金→既存政策Components（課税・家計・企業・年金・基金）→税負担後現金→消費・既存投資・追加投資→ラグ供給と上限制約→GDP・一般マクロ税→PB・債務→翌年。年金拠出の資金移転を家計へ二重控除せず、基金増減は拠出＋収益−給付で閉じる。年金DOMESTIC_TRANSFER帰属を保持し、4帰属の旧結果は変更・採用しない。',
 '完全動学ではない。VATの価格・数量・税基礎、医療給付基礎、旧年金衛星、人口・労働、既存コア成長・共通デフレータ、相続取引基礎は固定原本経路を継承。KPI/VAT主分岐は既存N3の凍結なしを固定。未裁定KPIを再選択せず、内生KPI別枝は本件では未実行。賃金・企業利益・政策税・家計・年金拠出／基金の部分動学である。',
 '全体の政府購入・公共投資の統計水準は未再構成で、年次CSVの政府購入と公共投資は追加分。民間投資は既存資本置換proxy＋既存政策投資＋追加投資、消費は既存モデルproxy。輸入資本の生産効果は別同定できず、前回同様、政府国内比率を公共資本形成にも適用する。較正上の限界である。','## 公的資料・較正','Public_Sources.mdに取得先と適用限界を記録。内閣府長期推計は名目フロー据置以外の延伸と金利感度の必要性を裏付けるが、異なる基準年・経済シナリオの系列をSPEへ無断置換しない。公共資本の生産弾力性をそのまま年次capital_yieldへ転用しない。国内比率0.6/0.8/1.0は支出構成・輸入誘発表と較正していない感度であり、どれかを統計実測値と称さない。',
 '## 検証・成果物',f"今回のチェック{v['checks']}件、失敗{v['failed']}件。既存政策部品リプレイ、前回8ケース再現、追加ゼロの動学基準再現、税・企業源泉使途・資本・年金基金・PB・債務資産・総発行総償還・財源制約・境界両端を検証。年次差合計、初回SQ割れ、最悪年、全ケース定義はCSV。算術整合と条件付きSQ以上を較正頑健性に読み替えない。",'実行：`python3 handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122/N3_GDP_Robustness_Reproduce.py --root . --outdir /tmp/n3-robust-replay`。Python標準ライブラリとgitを使用。Component_Initialization.jsonは固定エンジンから抽出した必要最小入力であり、抽出再現用Capture_Initialization.pyを同梱。','政策本文・既存エンジン・前回19原本は変更せず、新規指定handoffディレクトリのみに成果物を保存。暫定改訂版N3・正式採用・PR/mergeなし。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。']
 (out/'SPE_N3_GDP_Robustness_Fiscal_Dynamics_Report_DRAFT_20261122.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--outdir',type=Path,required=True);z=a.parse_args();run(z.root.resolve(),z.outdir.resolve())
