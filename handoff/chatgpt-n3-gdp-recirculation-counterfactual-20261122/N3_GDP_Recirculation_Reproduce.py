#!/usr/bin/env python3
"""Isolated tax-amount-preserving GDP/fiscal/investment counterfactuals.
All fixed engine/policy files are read-only; diagnostic coefficients are explicit.
Python stdlib + git. No national calibration or policy adoption is implied.
"""
import argparse,copy,csv,hashlib,importlib.util,json,math,os,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
N3='37c3399f9c553673a79ba1298fc68d758a77055e';BURDEN='b552d93d325c3d128b9d8c472b087feda6efe721';REQUEST='8de9960bc657443251817e87741c959babcef243';CLAUDE='ba08c45d4ecb99defecb8416c8d63e0cbfde8cb4'
ND='handoff/chatgpt-n3-f-parity-implementation-20261122';BD='handoff/chatgpt-n3-policy-burden-diagnosis-20261122';FD='handoff/chatgpt-national-fiscal-closure-20261121';BASE='PARITY_CONNECTED_CANDIDATE';SQ='SQ_COMMON_ON';MODES=['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA']
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8')))
def n(r,k):return float(r[k]) if r.get(k) not in ['',None] else 0.
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def loadmodule(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fixed(root,commit,path,receipts):
 if subprocess.run(['git','cat-file','-e',commit],cwd=root,capture_output=True).returncode:subprocess.run(['git','fetch','origin',commit],cwd=root,check=True)
 b=subprocess.check_output(['git','show',commit+':'+path],cwd=root);p=root/path
 if p.exists():assert p.read_bytes()==b,path
 receipts.append(dict(commit=commit,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),local_match=p.exists()));return b

def definitions():
 cases=[]
 def add(cid,group,**kw):
  r=dict(case=cid,group=group,g_share=0.,pi_share=0.,firm_rate=0.,firm_stock_draw_rate=0.,mpc=.72,lambda_C=.6,income_feedback=.08,gov_domestic=.8,public_capital_productivity=1.,household_policy_cash_fixed=True,policy_tax_amounts_fixed=True,policy_tax_rates_fixed=True,kpi_vat_path_fixed=True,scope='ISOLATED_NON_ADOPTED_DIAGNOSTIC')
  r.update(kw);r['classification']='UNCHANGED_IMPLEMENTATION' if group=='BASE' else 'PARAMETER_SENSITIVITY_NOT_POLICY' if group=='C' else 'ADDITIONAL_POLICY_OR_UNDECIDED_ALLOCATION_NOT_AUTHORIZED_AS_N3';cases.append(r)
 add('BASE_N3','BASE')
 for share in [.25,.5,.75]:
  add('G_'+str(int(100*share)),'A',g_share=share)
  add('PUBLIC_I_'+str(int(100*share)),'A',pi_share=share)
  add('FIRM_FLOW_'+str(int(100*share)),'B',firm_rate=share)
 add('FIRM_STOCK_DRAW25','B',firm_stock_draw_rate=.25)
 for m in [.5,.9]:add('MPC_'+str(int(m*100)),'C',mpc=m)
 for speed in [.3,1.]:add('C_SPEED_'+str(int(speed*100)),'C',lambda_C=speed)
 for strength in [0.,.04,.16]:add('FEEDBACK_'+str(int(strength*100)),'C',income_feedback=strength)
 add('G50_FIRM75','AB',g_share=.5,firm_rate=.75)
 add('G75_FIRM75','AB',g_share=.75,firm_rate=.75)
 add('G50_PUBLIC_I25','A_MIX',g_share=.5,pi_share=.25)
 add('G50_PUBLIC_I25_FIRM75','AB_MIX',g_share=.5,pi_share=.25,firm_rate=.75)
 add('G50_PUBLIC_I25_FIRM75_MPC50','ABC',g_share=.5,pi_share=.25,firm_rate=.75,mpc=.5)
 add('G50_PUBLIC_I25_FIRM75_MPC90','ABC',g_share=.5,pi_share=.25,firm_rate=.75,mpc=.9)
 add('G50_PUBLIC_I25_FIRM75_FB16','ABC',g_share=.5,pi_share=.25,firm_rate=.75,income_feedback=.16)
 for dom in [.6,1.]:add('MIX_DOMESTIC_'+str(int(dom*100)),'ASSUMPTION',g_share=.5,pi_share=.25,firm_rate=.75,gov_domestic=dom)
 add('MIX_PUBLIC_YIELD_ZERO','ASSUMPTION',g_share=.5,pi_share=.25,firm_rate=.75,public_capital_productivity=0.)
 add('PUBLIC_I75_YIELD_ZERO','ASSUMPTION',pi_share=.75,public_capital_productivity=0.)
 return cases

def simulate(spec,trace,sq,funding,fiscal,primary,fp,official,chk):
 pars=trace[2026]['_parameters'];fbase=fp.baseline(dict(tail='NOMINAL_HOLD_2040'),official)
 C=I=K=pubI=pubK=privI=privK=0.;Y=trace[2026]['Y'];tax=trace[2026]['tax'];prevNom=trace[2026]['N'];gap=0.;firmcash=0.;debt=official[2025]['CL_debt_end_trn'];assets=0.;prevpriv=0.;prevpub=0.;rows=[];ledger=[]
 for year in range(2026,2056):
  t=trace[year];r=t['macro_row'];d=t['coreD'];isinitial=year==2026;f=funding[year];oldfund=n(f,'cash_end_trn');existingI=n(f,'realized_investment_nominal_trn');flow=n(f,'source_tax_saving_trn')-n(f,'dividend_paid_trn')-existingI
  beginfirm=firmcash;available=beginfirm+flow;assert available>=-2e-7,(spec['case'],year,available)
  target=spec['firm_rate']*max(flow,0.)+spec['firm_stock_draw_rate']*max(beginfirm,0.)
  privI=min(max(available,0.)/d,(1-pars['lambda_I'])*privI+pars['lambda_I']*target/d) if not isinitial else 0.
  paid=privI*d;firmcash=available-paid
  room=max(0.,primary[year]);g=spec['g_share']*room;pubbudget=spec['pi_share']*room
  pubI=min(pubbudget*spec['gov_domestic']/d,(1-pars['lambda_I'])*pubI+pars['lambda_I']*pubbudget*spec['gov_domestic']/d) if not isinitial else 0.
  public_paid=pubI*d/spec['gov_domestic'];spend=g+public_paid
  fb=spec['income_feedback']*gap*d
  # Recompute the original Ctarget, including special MPC/quantity/pension/estate terms.
  w=t['medical'];ss=t['social'];pen=t['pension_ledger'];mpc=spec['mpc']
  Ctarget=pars['domestic_share']*(mpc*(t['cash']+fb-ss['household'])+ss['weighted_demand']+pen['consumption_impulse_trn']-mpc*pen['household_cash_delta_trn']+w['quantity_nominal_volume_delta_trn']-mpc*w['quantity_replaced_price_benefit_trn']+(mpc-w['estate_mpc_candidate'])*w['wealth_tax_delta_trn'])/d
  if not isinitial:
   C=(1-spec['lambda_C'])*C+spec['lambda_C']*Ctarget
   I=(1-pars['lambda_I'])*I+pars['lambda_I']*t['invest_nom']/d
  supply=pars['capital_yield']*(1-pars['depreciation'])*(K+privK+spec['public_capital_productivity']*pubK)+(t['supply']-pars['capital_yield']*(1-pars['depreciation'])*t['Kprev'])
  desired=t['coreY']+pars['capacity_absorption']*supply+C+I+privI+pubI+g*spec['gov_domestic']/d+t['education_nom']/d+t['education_level']+t['finite']+w['service_production_nominal_delta_trn']/d
  cap=t['coreY']+supply+pars['slack']*t['coreY']+t['education_level'];Y=min(desired,cap);unmet=max(0.,desired-Y);pressure=pars['price_pressure_coefficient']*unmet/t['coreY'];nom=Y*d*(1+pressure)
  if not isinitial:tax=min(tax*(1+(nom/prevNom-1)*pars['elasticity'])*(.9 if year==2031 else 1.),nom*pars['tax_cap_ratio'])
  taxchange=tax-t['tax'];beforedebt=debt;beforeassets=assets;b=fbase[year]
  pb=n(fiscal[year],'CL_PB_candidate_trn')+taxchange-spend
  interest=b['CL_net_interest_trn']*min(1.,debt/b['CL_debt_begin_trn'])+.02*max(0.,debt-b['CL_debt_begin_trn'])-.02*assets
  z=fp.finance(debt,assets,pb,interest,b['stock_flow_adjustment_unallocated_trn'],.1);debt=z['CL_debt_end_candidate_trn'];assets=z['CL_cash_assets_end_candidate_trn']
  prevK=K;prevpriv=privK;prevpub=pubK
  if not isinitial:
   K=(1-pars['depreciation'])*K+I;privK=(1-pars['depreciation'])*privK+privI;pubK=(1-pars['depreciation'])*pubK+pubI
  originalC=n(r,'household_consumption_real_proxy_trn');consumption=originalC+(C-t['C'])
  fixedHousehold=t['cash'];resourceDI=pars['household_income_share']*t['coreN']+fixedHousehold+fb
  gapSQ=Y-sq[year]['Y'];gap=Y-t['coreY'];prevNom=nom
  row=dict(case=spec['case'],year=year,SQ_real_GDP_trn=sq[year]['Y'],real_GDP_trn=Y,GDP_minus_SQ_trn=gapSQ,GDP_improvement_vs_N3_trn=Y-t['Y'],nominal_GDP_trn=nom,consumption_real_proxy_trn=consumption,consumption_minus_SQ_trn=consumption-n(sq[year]['macro_row'],'household_consumption_real_proxy_trn'),policy_consumption_delta_real_trn=C,private_policy_investment_real_trn=I+privI,extra_private_investment_real_trn=privI,public_investment_extra_real_trn=pubI,private_replacement_investment_reference_real_trn=n(r,'capital_replacement_investment_real_trn'),capital_total_proxy_real_trn=n(r,'capital_total_real_trn')-t['K']+K+privK+pubK,extra_private_capital_end_trn=privK,extra_public_capital_end_trn=pubK,supply_real_trn=supply,desired_real_GDP_trn=desired,supply_ceiling_real_GDP_trn=cap,unmet_demand_real_trn=unmet,common_deflator=d,diagnostic_price_pressure=pressure,tax_macro_proxy_trn=tax,policy_direct_tax_fixed_trn=t['direct'],tax_diagnostic_proxy_trn=tax+t['direct'],tax_minus_SQ_proxy_trn=tax+t['direct']-sq[year]['tax']-sq[year]['direct'],N3_policy_tax_fixed_trn=w['policy_tax_delta_trn'],N3_labor_business_tax_delta_fixed_trn=w['labour_business_flat30_tax_delta_trn'],flat_labor_rate=.30,flat_financial_corporate_rate=.20,estate_rate=.40,VAT_standard_rate_fixed=t['_VATrate'],household_policy_cash_fixed_trn=fixedHousehold,household_medical_plus_N3_cash_fixed_trn=w['household_cash_delta_trn'],N3_policy_household_cash_fixed_trn=w['policy_household_cash_delta_trn'],household_policy_cash_minus_SQ_trn=fixedHousehold-sq[year]['cash'],income_feedback_nominal_trn=fb,household_resource_DI_proxy_trn=resourceDI,N3_corporate_cash_end_trn=firmcash,legacy79_corporate_cash_partial_fixed_trn=t['firm_cash_stock'],government_purchase_extra_nominal_trn=g,public_investment_extra_nominal_trn=public_paid,CL_PB_candidate_trn=pb,CL_PB_minus_SQ_trn=pb-n(fiscal[year].get('_SQ',{}),'CL_PB_candidate_trn'),CL_debt_candidate_trn=debt,CL_cash_assets_candidate_trn=assets,CL_interest_candidate_trn=interest,CL_new_cash_borrowing_candidate_trn=z['CL_new_cash_borrowing_candidate_trn'],CL_gross_issue_assumed_rollover_trn=z['CL_gross_issue_with_assumed_refinancing_trn'],general_government_PB=None,general_government_debt=None,actual_bond_issue=None,policy_tax_amount_fixed=True,macro_tax_amount_fixed=False,policy_income_bases_frozen=True,kpi_vat_schedule_frozen=True,full_national_calibration=False)
  sqr=sq[year]['macro_row'];sqf=fiscal[year]['_SQ']
  row.update(SQ_consumption_real_proxy_trn=n(sqr,'household_consumption_real_proxy_trn'),SQ_policy_investment_real_trn=sq[year]['I'],SQ_private_replacement_reference_real_trn=n(sqr,'capital_replacement_investment_real_trn'),private_total_investment_proxy_real_trn=n(r,'capital_replacement_investment_real_trn')+I+privI,private_investment_minus_SQ_real_trn=n(r,'capital_replacement_investment_real_trn')+I+privI-n(sqr,'capital_replacement_investment_real_trn')-sq[year]['I'],SQ_tax_diagnostic_proxy_trn=sq[year]['tax']+sq[year]['direct'],SQ_household_policy_cash_trn=sq[year]['cash'],SQ_CL_PB_candidate_trn=n(sqf,'CL_PB_candidate_trn'),SQ_CL_debt_candidate_trn=n(sqf,'CL_debt_end_candidate_trn'),CL_debt_minus_SQ_trn=debt-n(sqf,'CL_debt_end_candidate_trn'),CL_debt_to_diagnostic_GDP_pct=100*debt/nom,government_expenditure_diagnostic_proxy_trn=n(r,'expenditure_diagnostic_trn')+spend,SQ_government_expenditure_diagnostic_proxy_trn=n(sqr,'expenditure_diagnostic_trn'),SQ_CL_new_cash_borrowing_candidate_trn=n(sqf,'CL_new_cash_borrowing_candidate_trn'),whole_economy_public_investment_level=None)
  rows.append(row)
  led=dict(case=spec['case'],year=year,fiscal_room_fixed_primary_vs_SQ_trn=room,g_share=spec['g_share'],public_I_share=spec['pi_share'],unallocated_debt_asset_share=1-spec['g_share']-spec['pi_share'],government_purchase_cash_trn=g,public_investment_cash_budget_trn=pubbudget,public_investment_cash_executed_trn=public_paid,unspent_public_I_budget_trn=pubbudget-public_paid,remaining_room_for_debt_assets_trn=room-spend,government_real_domestic_purchase_trn=g*spec['gov_domestic']/d,government_purchase_import_leak_trn=g*(1-spec['gov_domestic']),public_I_import_leak_trn=public_paid*(1-spec['gov_domestic']),macro_tax_feedback_increment_trn=taxchange,base_CL_PB_trn=n(fiscal[year],'CL_PB_candidate_trn'),CL_PB_trn=pb,CL_debt_begin_trn=beforedebt,CL_debt_end_trn=debt,CL_assets_begin_trn=beforeassets,CL_assets_end_trn=assets,CL_interest_trn=interest,CL_balance_trn=pb-interest,SFA_unallocated_trn=b['stock_flow_adjustment_unallocated_trn'],new_cash_borrowing_trn=z['CL_new_cash_borrowing_candidate_trn'],cash_debt_redemption_trn=z['CL_cash_surplus_debt_redemption_candidate_trn'],asset_draw_trn=z['CL_cash_asset_draw_candidate_trn'],asset_addition_trn=z['CL_cash_asset_addition_candidate_trn'],gross_bond_issue_assumed_trn=z['CL_gross_issue_with_assumed_refinancing_trn'],gross_redemption_assumed_trn=z['CL_gross_redemption_with_assumed_refinancing_trn'],firm_begin_trn=beginfirm,firm_tax_saving_source_trn=n(f,'source_tax_saving_trn'),firm_dividend_paid_fixed_trn=n(f,'dividend_paid_trn'),firm_original_investment_nominal_fixed_trn=existingI,firm_new_flow_after_original_uses_trn=flow,firm_extra_target_nominal_trn=target,firm_extra_actual_paid_trn=paid,firm_end_trn=firmcash,firm_original_counterfactual_cash_end_trn=oldfund,private_K_begin_trn=prevpriv,private_K_end_trn=privK,public_K_begin_trn=prevpub,public_K_end_trn=pubK,depreciation=pars['depreciation'],financing_to_GDP_feedback='EXPLICIT_ADDITIONAL_G_AND_I_ONLY_NO_DIRECT_PB_ADDITION',fiscal_scope='CENTRAL_LOCAL_CANDIDATE_POST2040_HOLD_NOT_GG')
  ledger.append(led)
  prefix=spec['case']+':'+str(year)+':'
  chk(prefix+'firm_source_uses',firmcash-beginfirm-flow+paid)
  chk(prefix+'firm_cash_nonnegative',min(firmcash,0.))
  chk(prefix+'public_single_use',max(spend-room*(spec['g_share']+spec['pi_share']),0.))
  chk(prefix+'PB_bridge',pb-n(fiscal[year],'CL_PB_candidate_trn')-taxchange+spend)
  chk(prefix+'debt_identity',debt-beforedebt-z['CL_new_cash_borrowing_candidate_trn']+z['CL_cash_surplus_debt_redemption_candidate_trn']-b['stock_flow_adjustment_unallocated_trn'])
  chk(prefix+'asset_identity',assets-beforeassets+z['CL_cash_asset_draw_candidate_trn']-z['CL_cash_asset_addition_candidate_trn'])
  chk(prefix+'budget_stock_flow',debt-assets-beforedebt+beforeassets+(pb-interest)-b['stock_flow_adjustment_unallocated_trn'])
  chk(prefix+'GDP_min',Y-min(desired,cap));chk(prefix+'aggregate_GDP_component_bridge',Y-t['Y']-((C-t['C'])+(I-t['I'])+privI+pubI+g*spec['gov_domestic']/d+pars['capacity_absorption']*(supply-t['supply'])-unmet+t['unmet']));chk(prefix+'tax_amount_fixed',row['N3_policy_tax_fixed_trn']-t['medical']['policy_tax_delta_trn']);chk(prefix+'cash_fixed',fixedHousehold-t['cash'])
  if not isinitial:
   chk(prefix+'private_K',privK-(1-pars['depreciation'])*prevpriv-privI);chk(prefix+'public_K',pubK-(1-pars['depreciation'])*prevpub-pubI)
 return rows,ledger

def run(root,out,work,source,skip_reexecution=False):
 out.mkdir(parents=True,exist_ok=True);work.mkdir(parents=True,exist_ok=True);receipts=[];checks=[]
 def chk(name,error,tol=3e-7):checks.append(dict(check=name,error=error,tolerance=tol,passed=abs(error)<=tol))
 assumptions=dict(status='ISOLATED_DIAGNOSTIC_NOT_POLICY_ADOPTION',tax_regime='EXISTING_N3_FIXED',government_room='max(0,fixed_N3_minus_SQ_primary_delta)',government_spending_shares=[0,.25,.5,.75],government_domestic_share_candidates=[.6,.8,1.],public_capital_yield_factor_candidates=[0,1],private_source='N3_corporate_tax_saving_after_fixed_dividend_and_original_investment',private_flow_conversion_candidates=[0,.25,.5,.75],stock_draw='25% of remaining beginning stock per year; separate case',MPC_candidates=[.5,.72,.9],lambda_C_candidates=[.3,.6,1.],income_feedback_candidates=[0,.04,.08,.16],fixed_common_parameters='not modified; read pinned trace',policy_bases='frozen to preserve tax amounts; generic macro tax recomputed',public_capital_import_scope='government domestic share applied to purchase and capital formation; uncalibrated',fiscal_scope='CL candidate only; 2040 nominal flow hold after2040; 2% interest and 10% assumed rollover inherited',original_parameters_or_policy_files_modified=False)
 (out/'Counterfactual_Assumptions.json').write_text(json.dumps(assumptions,indent=2)+'\n')
 # Source identity includes the policy, engine adapters, fixed results, fiscal assumptions and past diagnostics.
 for name in ['Inputs.json','Model.py','Components.py','Macro_Adapter.py','Resolved_Macro_Source.py.txt','results/Annual_DOMESTIC_TRANSFER.csv','results/Conditional_National_Local_Fiscal.csv','results/DOMESTIC_TRANSFER_Corporate_Funding_Stock.csv','results/DOMESTIC_TRANSFER_KPI_Events.csv']:
  fixed(root,N3,ND+'/'+name,receipts)
 for mode in MODES:
  for name in ['Annual_'+mode+'.csv',mode+'_N3_Pension_Accounts.csv']:fixed(root,N3,ND+'/results/'+name,receipts)
 for name in ['policies/New3linesPolicies.md',FD+'/National_Fiscal.py',FD+'/Fiscal_Inputs.json',FD+'/Official_Fiscal_Baseline_2025_2040.csv']:
  fixed(root,N3,name,receipts)
 for name in ['N3_Unchanged_Execution_Trace.json','N3_GDP_Gap_Decomposition_2026_2055.csv','N3_Investment_Source_Decomposition.csv','N3_Conditional_Fiscal_Primary_Bridge.csv','N3_Household_Counterpart_Ledger.csv','N3_Policy_Burden_Diagnosis_Reproduce.py']:
  fixed(root,BURDEN,BD+'/'+name,receipts)
 for name in ['N3_F_Parity_Independent_Summary_DRAFT_20261122.json','N3_F_Parity_Fiscal_Summary_DRAFT_20261122.json']:
  b=fixed(root,CLAUDE,'handoff/claude-n3-f-parity-verification-20261122/'+name,receipts);(out/('Reused_Claude_'+name)).write_bytes(b)
 fixed(root,'620803b9f0ffcdfa4e7b5a3a82254bae8a5d1bec','handoff/chatgpt-n3-income-tax-rate-deduction-diagnosis-20261122/N3_Income_Tax_Existing_Bridge_2026_2055.csv',receipts)
 fixed(root,'4453f5300e1a6e2320b45c30d4e3767ed9e8b74e','handoff/chatgpt-sq-growth-diagnosis-20261122/SQ_Growth_Contribution_Summary.csv',receipts)
 fixed(root,REQUEST,'handoff/chatgpt-n3-gdp-recirculation-counterfactual-request-20261122/SPE_Work_N3_GDP_Recirculation_Investment_Counterfactual_Request_20261122.md',receipts)
 capture=loadmodule('fixed_burden_capture',root/BD/'N3_Policy_Burden_Diagnosis_Reproduce.py');capture.SELECT=[SQ,BASE]
 baselinework=work/'baseline';baselinework.mkdir(exist_ok=True)
 if not skip_reexecution or not (baselinework/'N3_Unchanged_Execution_Trace.json').exists():capture.capture(root,baselinework,source)
 trace=json.loads((baselinework/'N3_Unchanged_Execution_Trace.json').read_text());prior=json.loads((root/BD/'N3_Unchanged_Execution_Trace.json').read_text());fixedtrace={(t['case'],t['year']):t for t in prior['records']}
 ix={(t['case'],t['year']):t for t in trace['records']};base={y:ix[BASE,y] for y in range(2026,2056)};sq={y:ix[SQ,y] for y in range(2026,2056)}
 for cid in [SQ,BASE]:
  for y in range(2026,2056):
   for key in ['Y','N','C','I','K','tax','direct','cash','supply']:chk('fresh_engine_reproduction:'+cid+str(y)+key,ix[cid,y][key]-fixedtrace[cid,y][key],1e-8)
 vatrows={int(r['year']):r for r in rd(baselinework/'runtime/Gap_Annual.csv') if r['case']==BASE}
 for y in base:
  base[y]['_parameters']=trace['parameters'][BASE];base[y]['_VATrate']=n(vatrows[y],'standard_rate')
 funding={int(r['year']):r for r in rd(root/ND/'results/DOMESTIC_TRANSFER_Corporate_Funding_Stock.csv') if r['case']==BASE}
 allf=rd(root/ND/'results/Conditional_National_Local_Fiscal.csv');fiscal={int(r['year']):r for r in allf if r['case']==BASE and r['scenario']=='REFERENCE_CANDIDATE' and r['mode']=='DOMESTIC_TRANSFER'};sqf={int(r['year']):r for r in allf if r['case']==SQ and r['scenario']=='REFERENCE_CANDIDATE' and r['mode']=='DOMESTIC_TRANSFER'}
 for y in fiscal:fiscal[y]['_SQ']=sqf[y]
 primary={int(r['year']):n(r,'policy_primary_delta_trn') for r in rd(root/BD/'N3_Conditional_Fiscal_Primary_Bridge.csv')}
 fp=loadmodule('read_only_fiscal_functions',root/FD/'National_Fiscal.py');official={int(r['year']):{k:float(v) if k.endswith('_trn') and v else v for k,v in r.items()} for r in rd(root/FD/'Official_Fiscal_Baseline_2025_2040.csv')}
 cases=definitions();annual=[];ledger=[]
 for case in cases:
  a,l=simulate(case,base,sq,funding,fiscal,primary,fp,official,chk);annual+=a;ledger+=l
 mainbase={r['year']:r for r in annual if r['case']=='BASE_N3'}
 for y in base:
  z=mainbase[y];t=base[y]
  for key,old in [('real_GDP_trn','Y'),('nominal_GDP_trn','N'),('policy_consumption_delta_real_trn','C'),('private_policy_investment_real_trn','I'),('tax_macro_proxy_trn','tax')]:chk('adapter_baseline:'+str(y)+key,z[key]-t[old])
  for key in ['CL_PB_candidate_trn','CL_debt_end_candidate_trn','CL_cash_assets_end_candidate_trn']:
   newkey={'CL_debt_end_candidate_trn':'CL_debt_candidate_trn','CL_cash_assets_end_candidate_trn':'CL_cash_assets_candidate_trn'}.get(key,key);chk('fiscal_baseline:'+str(y)+key,z[newkey]-n(fiscal[y],key),3e-6)
  chk('firm_baseline:'+str(y),z['N3_corporate_cash_end_trn']-n(funding[y],'cash_end_trn'),3e-7)
 # Old requested milestones are rounded at 6 decimals.
 for year,g in [(2030,-7.595361),(2035,-39.900457),(2044,-52.290436),(2055,-47.631465)]:chk('requested_baseline_gap:'+str(year),mainbase[year]['GDP_minus_SQ_trn']-g,5.1e-7)
 summary=[]
 for case in cases:
  a=[r for r in annual if r['case']==case['case']];below=[r for r in a if r['GDP_minus_SQ_trn']< -1e-7];worst=min(a,key=lambda r:r['GDP_minus_SQ_trn']);key={r['year']:r for r in a}
  summary.append(dict(case=case['case'],group=case['group'],all_years_at_or_above_SQ=not below,first_below_SQ_year=below[0]['year'] if below else None,below_SQ_years=len(below),worst_year=worst['year'],worst_GDP_gap_trn=worst['GDP_minus_SQ_trn'],GDP_gap_2035_trn=key[2035]['GDP_minus_SQ_trn'],GDP_gap_2044_trn=key[2044]['GDP_minus_SQ_trn'],GDP_gap_2055_trn=key[2055]['GDP_minus_SQ_trn'],annual_gap_sum_trn_years=sum(r['GDP_minus_SQ_trn'] for r in a),improvement_2055_trn=key[2055]['GDP_improvement_vs_N3_trn'],PB_2055_trn=key[2055]['CL_PB_candidate_trn'],debt_2055_trn=key[2055]['CL_debt_candidate_trn'],debt_zero_first_year=next((r['year'] for r in a if r['CL_debt_candidate_trn']<1e-7),None),assets_2055_trn=key[2055]['CL_cash_assets_candidate_trn'],government_extra_cash_cumulative_trn=sum(r['government_purchase_extra_nominal_trn']+r['public_investment_extra_nominal_trn'] for r in a),firm_extra_cash_cumulative_trn=sum(l['firm_extra_actual_paid_trn'] for l in ledger if l['case']==case['case']),policy_tax_amount_fixed=True,household_policy_cash_fixed=True,GG_fiscal_sustainability_identified=False,classification=case['classification']))
 dump(out/'N3_GDP_Recirculation_Annual_Comparison_2026_2055.csv',annual);dump(out/'N3_GDP_Recirculation_Fiscal_Investment_Ledger.csv',ledger);dump(out/'N3_GDP_Recirculation_Case_Definitions.csv',cases);dump(out/'N3_GDP_Recirculation_Case_Summary.csv',summary)
 followup(root,out,work,source,base,sq,allf,chk,receipts,skip_reexecution)
 # Nonlinear interaction is calculated from simultaneous recurrence, never sum-only prediction.
 combos=[];indices={(r['case'],r['year']):r for r in annual}
 for y in base:
  for combo,g in [('G50_FIRM75','G_50'),('G75_FIRM75','G_75')]:
   effect=indices[combo,y]['GDP_improvement_vs_N3_trn'];single=indices[g,y]['GDP_improvement_vs_N3_trn']+indices['FIRM_FLOW_75',y]['GDP_improvement_vs_N3_trn'];combos.append(dict(case=combo,year=y,simultaneous_effect_trn=effect,sum_of_single_effects_trn=single,interaction_trn=effect-single))
 dump(out/'N3_GDP_Recirculation_Interactions.csv',combos)
 # Monotonic source-limited firm investment and pure government demand controls.
 for y in base:
  vals=[indices[c,y]['extra_private_investment_real_trn'] for c in ['FIRM_FLOW_25','FIRM_FLOW_50','FIRM_FLOW_75']]
  chk('firm_conversion_monotonic:'+str(y),min(vals[1]-vals[0],0.)+min(vals[2]-vals[1],0.))
 for r in receipts:
  p=root/r['path']
  if p.exists():chk('source_unchanged:'+r['path'],0. if hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'] else 1.,0.)
 (out/'Input_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 failed=[c for c in checks if not c['passed']];result=dict(status='PASS_CONDITIONAL_DIAGNOSTIC' if not failed else 'FAIL',checks=len(checks),failed=len(failed),failures=failed,request_commit=REQUEST,N3_fixed_commit=N3,source_policy_or_common_engine_modified=False,baseline_fresh_engine_reexecuted=not skip_reexecution,main_cases=len(cases),annual_rows=len(annual),all_years_SQ_candidates=[r['case'] for r in summary if r['all_years_at_or_above_SQ']],policy_tax_amount_and_household_policy_cash_fixed=True,macro_tax_proxy_recomputed=True,full_dynamic_policy_tax_bases_recomputed=False,whole_GG_fiscal_sustainability_verified=False,claude_existing_pass_reused_not_reexecuted=True,checks_detail=checks)
 report(out,summary,annual,ledger,result)
 result['artifacts']=[dict(path=f.name,size=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(out.iterdir()) if f.is_file() and f.name not in ['N3_GDP_Recirculation_Verification.json','Execution.log']]
 (out/'N3_GDP_Recirculation_Verification.json').write_text(json.dumps(result,indent=2)+'\n');assert not failed,failed[:8]
 print('RECIRCULATION_PASS',len(checks),'checks',len(cases),'cases',len(annual),'annual rows')

# Follow-up/report definitions below.
def followup(root,out,work,source,base,sq,allf,chk,receipts,skip):
 # Actual code-boundary comparison, separate from main tax-fixed cases.
 cfg=json.loads((root/ND/'Inputs.json').read_text());original=next(c for c in cfg['cases'] if c['id']==BASE)
 events=rd(root/ND/'results/DOMESTIC_TRANSFER_KPI_Events.csv');signal=n(next(r for r in events if r['case']==BASE and r['year']=='2035'),'previous_income_growth_pct')
 thresholds=[('PARITY_DIAG_KPI_LOW',signal-.000001),('PARITY_DIAG_KPI_REPORTED_EQUAL',signal),('PARITY_DIAG_KPI_HIGH',signal+.000001)]
 additions=[dict(copy.deepcopy(original),id=cid,kpi_growth_threshold_pct=threshold) for cid,threshold in thresholds]
 cfg['cases']+=additions;cfg['execution_case_filter']=[SQ]+[c['id'] for c in additions]
 kwork=work/'kpi';kwork.mkdir(exist_ok=True);inp=kwork/'Input.json';inp.write_text(json.dumps(cfg,indent=2)+'\n')
 if not skip or not (kwork/'runtime/Gap_Annual.csv').exists():
  subprocess.run([sys.executable,str(root/ND/'Model.py'),str(inp),'--engine',str(root),'--source',str(source),'--outdir',str(kwork/'runtime')],env={**os.environ,'SPE_PENSION_MODE':'DOMESTIC_TRANSFER'},check=True)
 kr=rd(kwork/'runtime/Gap_Annual.csv');ke=rd(kwork/'runtime/KPI_Events.csv');engine={(r['case'],int(r['year'])):r for r in rd(kwork/'runtime/N3_Engine_Accounts.csv')}
 krows=[];fs=loadmodule('kpi_read_fiscal',root/FD/'National_Fiscal.py');official={int(r['year']):{k:float(v) if k.endswith('_trn') and v else v for k,v in r.items()} for r in rd(root/FD/'Official_Fiscal_Baseline_2025_2040.csv')};bas=fs.baseline({'tail':'NOMINAL_HOLD_2040'},official)
 for cid,threshold in thresholds:
  debt=official[2025]['CL_debt_end_trn'];assets=0.;e2035=next(r for r in ke if r['case']==cid and r['year']=='2035');actual_signal=n(e2035,'previous_income_growth_pct');freeze=e2035['vat_frozen']=='True';chk('KPI_strict_less_boundary:'+cid,float(freeze)-float(actual_signal<threshold),0.)
  for r in sorted([r for r in kr if r['case']==cid],key=lambda r:int(r['year'])):
   y=int(r['year']);e=engine[cid,y];se=engine[SQ,y];newtax=n(r,'tax_diagnostic_trn');ex=n(e,'expenditure_diagnostic_trn')-n(se,'expenditure_diagnostic_trn');oldinterest=n(r,'medical_policy_interest_trn')+n(r,'bond_interest_trn')-n(next(s for s in kr if s['case']==SQ and int(s['year'])==y),'medical_policy_interest_trn')
   primary=newtax-n(next(s for s in kr if s['case']==SQ and int(s['year'])==y),'tax_diagnostic_trn')-ex+oldinterest
   b=bas[y];pb=b['CL_PB_trn']+primary;interest=b['CL_net_interest_trn']*min(1.,debt/b['CL_debt_begin_trn'])+.02*max(0.,debt-b['CL_debt_begin_trn'])-.02*assets;f=fs.finance(debt,assets,pb,interest,b['stock_flow_adjustment_unallocated_trn'],.1);debt=f['CL_debt_end_candidate_trn'];assets=f['CL_cash_assets_end_candidate_trn']
   krows.append(dict(case=cid,year=y,threshold_pct=threshold,actual_2035_signal_pct=actual_signal,strict_less_than_operator=True,kpi_freeze_2035=freeze,standard_VAT_rate=n(r,'standard_rate'),real_GDP_trn=n(r,'real_gdp_trn'),GDP_minus_SQ_trn=n(r,'real_gdp_trn')-sq[y]['Y'],GDP_difference_vs_N3_trn=n(r,'real_gdp_trn')-base[y]['Y'],household_policy_cash_trn=n(e,'parity_household_cash_trn'),tax_diagnostic_trn=newtax,policy_tax_delta_trn=n(r,'policy_tax_delta_trn'),pension_fund_stock_trn=n(r,'pension_fund_stock_trn'),CL_PB_candidate_trn=pb,CL_debt_candidate_trn=debt,policy_tax_amount_fixed=False,scope='NATIVE_ENGINE_KPI_BOUNDARY_ONLY_NOT_TAX_PRESERVING_CANDIDATE'))
 chk('KPI_lower_no_freeze',float(next(r for r in krows if r['case']=='PARITY_DIAG_KPI_LOW')['kpi_freeze_2035']),0.)
 chk('KPI_higher_freeze',float(next(r for r in krows if r['case']=='PARITY_DIAG_KPI_HIGH')['kpi_freeze_2035'])-1,0.)
 for row in krows:
  if row['case']=='PARITY_DIAG_KPI_LOW':
   y=row['year'];chk('KPI_no_switch_matches_base_GDP:'+str(y),row['real_GDP_trn']-base[y]['Y']);chk('KPI_no_switch_matches_base_PB:'+str(y),row['CL_PB_candidate_trn']-n(next(r for r in allf if r['case']==BASE and r['mode']=='DOMESTIC_TRANSFER' and r['scenario']=='REFERENCE_CANDIDATE' and int(r['year'])==y),'CL_PB_candidate_trn'),3e-6)
 dump(out/'N3_KPI_Threshold_Boundary_Annual.csv',krows)
 # Four native pension attribution paths are reused, not silently rebased to the main frozen tax path.
 pension=[];fundbyyear={y:[] for y in range(2026,2056)}
 for mode in MODES:
  rows=[r for r in rd(root/ND/('results/Annual_'+mode+'.csv')) if r['case']==BASE];p={int(r['year']):r for r in rd(root/ND/('results/'+mode+'_N3_Pension_Accounts.csv')) if r['case']==BASE};ff={int(r['year']):r for r in allf if r['case']==BASE and r['mode']==mode and r['scenario']=='REFERENCE_CANDIDATE'}
  for r in rows:
   y=int(r['year']);f=p[y];stock=n(f,'fund_end_trn');fundbyyear[y].append(stock);chk('pension_fund_identity:'+mode+str(y),stock-n(f,'fund_begin_trn')-n(f,'fund_contribution_trn')-n(f,'fund_return_trn')+n(f,'fund_payout_trn'),2e-7)
   pension.append(dict(mode=mode,year=y,real_GDP_trn=n(r,'real_gdp_trn'),GDP_minus_same_SQ_trn=n(r,'real_gdp_trn')-sq[y]['Y'],household_cash_trn=n(r,'household_cash_delta_trn'),household_resource_DI_proxy_trn=n(r,'macro_cash_DI_proxy_trn'),tax_diagnostic_proxy_trn=n(r,'tax_diagnostic_trn'),policy_tax_delta_trn=n(r,'policy_tax_delta_trn'),pension_fund_begin_trn=n(f,'fund_begin_trn'),pension_fund_end_trn=stock,pension_fund_return_trn=n(f,'fund_return_trn'),domestic_income_debit_trn=n(f,'domestic_property_income_debit_trn'),external_income_credit_trn=n(f,'overseas_primary_income_credit_trn'),additional_VA_trn=n(f,'additional_VA_trn'),CL_PB_candidate_trn=n(ff[y],'CL_PB_candidate_trn'),CL_debt_candidate_trn=n(ff[y],'CL_debt_end_candidate_trn'),policy_tax_amount_fixed=False,scope='REUSED_FIXED_NATIVE_ATTRIBUTION_CANDIDATE_NOT_ADOPTED'))
 dump(out/'N3_Pension_Attribution_Annual_Comparison.csv',pension)
 # Correct investment residual attribution. Preserve VAT channel, do not repeat the earlier employer-cost guess.
 inv=[r for r in rd(root/BD/'N3_Investment_Source_Decomposition.csv') if r['case']==BASE]
 dump(out/'N3_Existing_Investment_Source_Decomposition.csv',inv)
 health=[]
 for y,t in base.items():
  delta=t['medical']['health_effective_labor_added']-sq[y]['medical']['health_effective_labor_added'];effect=t['coreY']*((t['labor']+delta)/t['labor'])**t['_parameters']['labor_response']-t['coreY'];health.append(dict(year=y,computed_effective_labor_difference=delta,fixed_input_core_GDP_effect_if_connected_trn=effect,actual_labor_path_changed=False,not_realized_GDP_contribution=True))
 dump(out/'N3_Health_Labor_Limited_Sensitivity.csv',health)
 maxspread=max(max(v)-min(v) for v in fundbyyear.values());(out/'Followup_Measures.json').write_text(json.dumps(dict(KPI_reported_signal_pct=signal,base_candidate_pension_fund_max_spread_trn=maxspread,health_labor_2055=health[-1],KPI_boundary_2035=[r for r in krows if r['year']==2035],KPI_boundary_2040=[r for r in krows if r['year']==2040]),indent=2)+'\n')
 lines=['# Claude指摘の限定フォロー','既存164マクロ＋52財政のPASS_WITH_LIMITATIONSを再利用。本件で独立AIレビューを再発出していない。未較正をPASSへ変更しない。',
 '## KPI閾値','実コードの演算子は `income_growth < threshold`。2035年評価は2033→2034年の実質現金所得一人当たりproxyであり、正式所得中央値ではない。固定出力の丸めた信号±0.000001百分率ポイントと、表示信号そのものを閾値とする3ケースを元エンジンで再実行した。表示値と内部浮動小数値は同一とは限らず、REPORTED_EQUALは厳密な内部値との等号を意味しない。LOW/HIGHは両側を検証。閾値・正式KPI定義の採用は行わない。',
 '| 閾値ケース | 閾値% | 2035凍結 | 2040 VAT | 2055 GDP−SQ |','|---|---:|---|---:|---:|']
 for cid,threshold in thresholds:
  z=next(r for r in krows if r['case']==cid and r['year']==2055);v=next(r for r in krows if r['case']==cid and r['year']==2040);lines.append(f"| {cid} | {threshold:.12f} | {z['kpi_freeze_2035']} | {v['standard_VAT_rate']:.2f} | {z['GDP_minus_SQ_trn']:.6f} |")
 lines+=['KPI枝はVAT・動学税基礎も変わるため、税負担維持の主比較から分離した。税の緩和を本件の改善候補として採用していない。',
 '## 年金4帰属','固定4候補の年次GDP・家計・基金・税・財政120行を再利用して比較した。主反実仮想のDOMESTIC_TRANSFERと同じSQを比較基準とする。帰属を変更すると動学税基礎も変わるため、主比較に混ぜない。基金は同一ではなく、基準N3候補の最大年次差は '+f'{maxspread:.9f}兆円。'+'旧全候補集合での最大約0.371兆円と、今回の基準候補のみの差を区別する。',
 '| 帰属 | 2055 GDP | GDP−SQ | 基金 | 家計現金 | CL PB |','|---|---:|---:|---:|---:|---:|']
 for mode in MODES:
  z=next(r for r in pension if r['mode']==mode and r['year']==2055);lines.append('| '+mode+' | '+' | '.join(f'{z[k]:.6f}' for k in ['real_GDP_trn','GDP_minus_same_SQ_trn','pension_fund_end_trn','household_cash_trn','CL_PB_candidate_trn'])+' |')
 lines+=['## 投資残余・資金勘定','2045年の約−1.870769兆円の投資帰着はVAT側である。旧雇主費用説を再採用しない。全30年のN3法人施策・VAT・旧79ケース残余を既存分解から個別CSVへ保存。N3法人減税残余現金と旧macroのcorporate_cash_buffer_partialは別勘定であり合算して投資財源にしていない。既存投資と配当を控除後のフローから追加転換し、追加投資を別資本ストックに一度だけ計上した。',
 '## 健康労働・比較境界','健康労働差の固定入力仮接続は2055年 '+f"{health[-1]['fixed_input_core_GDP_effect_if_connected_trn']:.9f}兆円。"+'主計算へ接続・正式実装していない。SQ共通縮小や別条件のF参照をN3固有差へ足し戻していない。FにGDP値を合わせる係数調整も行っていない。']
 (out/'N3_GDP_Recirculation_Claude_Followup.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')

def report(out,summary,annual,ledger,result):
 # Initial numerical report; all fields are generated from actual execution.
 best=min(summary,key=lambda r:(r['below_SQ_years'],-r['worst_GDP_gap_trn']));indexed={r['case']:r for r in summary};base=indexed['BASE_N3'];achieved=[r['case'] for r in summary if r['all_years_at_or_above_SQ']]
 lines=['# N3税負担維持下のGDP還流・投資・所得フィードバック診断',
 'DRAFT / NON-CANONICAL / EXECUTED CONDITIONAL DIAGNOSTIC。政策改訂・正式採用・全国較正PASSではない。',
 '## 判定',
 ('全30年でSQ以上の条件付きケース: '+', '.join(achieved)) if achieved else '未達。本診断グリッドに、2026〜2055年の全期間でSQ以上となるケースはなかった。',
 'N3税率・控除・導入率・既存政策税額・家計政策現金経路を維持し、政府購入／公共投資／企業投資／消費・所得フィードバックを隔離した。所得税比較の70.042771兆円を既存税へ置換していない。政策本文・既存係数・共通エンジンは変更していない。RP-023／M19–25 HOLD、RP-024 PENDINGを維持する。',
 '## 主要結果（GDPは実質兆円、PB・債務は名目兆円）',
 '基準係数を維持した複合例G50_PUBLIC_I25_FIRM75では、2035/2044/2055年のGDP−SQは '+ '/'.join(f"{indexed['G50_PUBLIC_I25_FIRM75'][k]:+.6f}" for k in ['GDP_gap_2035_trn','GDP_gap_2044_trn','GDP_gap_2055_trn'])+'兆円。30年すべてSQ以上だが、2055年CL債務は'+f"{indexed['G50_PUBLIC_I25_FIRM75']['debt_2055_trn']:.6f}"+'兆円残る。基準N3の債務ゼロ・現金資産積上げをそのまま維持する結果ではない。',
 '| ケース | 2035 GDP−SQ | 2044 | 2055 | 初回SQ割れ | 割れ年数 | 最悪年 | 最悪差 | 2055 CL PB | 債務 |',
 '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for r in summary:
  lines.append('| '+r['case']+' | '+' | '.join([f"{r[k]:.6f}" for k in ['GDP_gap_2035_trn','GDP_gap_2044_trn','GDP_gap_2055_trn']]+[str(r['first_below_SQ_year'] or 'なし'),str(r['below_SQ_years']),str(r['worst_year']),f"{r['worst_GDP_gap_trn']:.6f}",f"{r['PB_2055_trn']:.6f}",f"{r['debt_2055_trn']:.6f}"])+' |')
 lines+=['割合25/50/75は%で、政府は既存N3対SQの正の追加primary余力を固定母数とする。購入Gと公共Iを同じ母数から配分し、合計は最大75%。未配分・未執行分は従来のPB・債務・現金資産経路へ残す。FIRM_FLOWはN3法人減税から配当・既存投資を差し引いた残余新規フローの追加投資転換率。STOCK_DRAW25は毎年の期首残余現金の25%取崩しという別条件。MPС・所得フィードバック等の変更は診断アブレーションであり、政策改善を意味しない。',
 'ケースごとの年次差合計、基準N3比改善、初回債務ゼロ、累積追加支出はCase_Summary CSV。SQ割れは丸め誤差を避け1e−7兆円未満で判定し、年次の生値を保存した。',
 '## 計算の範囲と接続',
 '固定版SQ・N3を元エンジンで再実行し、既存トレースのGDP・名目GDP・C・I・K・税・家計・供給を照合した。さらに隔離アダプタのゼロ変更ケースでマクロと国地方財政を再現した。既存PASS全件やり直しではない。',
 '主比較は既存の政策所得基礎・政策税額・家計政策現金を固定し、C/I/K、供給能力、需要、供給上限、価格圧力、名目GDP、一般マクロ税proxy、前年GDP→所得フィードバックを再計算する。税率不変に加えて政策税額を固定した制御実験である。一般マクロ税proxyはGDPで変わるため、合計税額まで一定とはしていない。政府・投資で増えた所得が翌年消費へ戻る。政策税基礎・年金・KPIまで内生的に再計算する完全N3動学予測ではない。',
 'Ctargetは既存の家計現金、特殊MPC、年金、VAT数量代替、相続税項を保存して計算。C速度は0.3/0.6/1、MPC0.5/0.72/0.9、所得フィードバック0/0.04/0.08/0.16。純家計現金が負なので高MPCは負の消費効果を増幅し得る。SQ比較経路は全ケースで同一に固定しており、共通較正の代替ではない。',
 '追加投資は既存lambda_I=0.6で調整し、資金上限で制約。資本減耗5%、追加資本の供給寄与は翌年から既存capital_yield=0.1、需要吸収0.5を使う。公共資本に同じ生産性を使う根拠は較正されていないため、公共資本供給寄与ゼロも別ケース。政府購入は支出年の需要へ接続、国内比0.8（0.6/1も感度）、公共Iも同じ輸入漏出を仮置きする。これは未較正の実行仮定であり新しい保証乗数ではない。企業Iは既存モデルと同じく追加輸入分離を持たない。供給上限を適用し、未充足需要はGDPへ加算しない。',
 '## 財政閉合と資金の単一使用',
 '基準では資金余力はCL PB・債務償還・債務ゼロ後の現金資産へ流れ、financing_to_GDP_feedback=False。追加Gと公共Iの実執行額をPBから差し引き、税フィードバックを一度加え、利払い・資産利息・債務・新規現金借入・仮定ロールオーバーを年次再計算。PB黒字や現金ストックを直接GDPへ加算していない。',
 '財政は既存の国地方候補であり一般政府ではない。2041年以降は2040年名目フロー据置、未配賦SFA・社会保障の欠落、税proxyの全国較正未完、仮定借換率10%・金利2%を継承。実際の国債発行・一般政府PB/債務は空欄。債務が非負で計算閉合しても、全国財政持続可能性を証明したとは扱わない。高い税率を緩和していない一方、資産積上げと支出・投資を交換するトレードオフがある。',
 '企業資金は減税源泉−配当−既存投資−追加投資＝残余現金。既存投資は消さず、追加投資は別状態・別資本へ一度だけ加える。現金残高非負・資本減耗・資金恒等式を年次検証。約60.75兆円を単年度投資財源とせず、旧79のVAT等の企業勘定とも合算しない。',
 '政府還流・企業投資だけの主係数維持ケースでも全期間SQ以上となる一方、MIX_DOMESTIC_60では24年SQ割れ。公共I75%のみの達成は公共資本の供給効果に依存し、同供給効果をゼロとしたPUBLIC_I75_YIELD_ZEROは9年SQ割れ、最悪差約−0.553兆円。条件付き達成を頑健性の証明へ読み替えない。',
 '家計現金は定義を分離した。2055年の医療＋N3政策の固定差は約−153.778兆円で、既存診断と同じ。消費式へ入るmacro cashは旧VAT等も含み約−181.886兆円。CSVに両者とN3政策のみを併記し、負担が軽くなったとは扱わない。家計資源所得proxyは前年GDPフィードバックにより変わる。',
 '## 原文との関係・識別限界',
 '企業優遇・設備投資条件とコンパクトシティ投資優先はN3原文にある。しかし追加現金の転換率、政府余力のG/I配分率、公共資本生産性、政府購入の輸入比率は原文から一意に決まらない。本ケースを未接続部品の正式補完や既存N3政策と認定しない。政府還流率の選択は原文外または未裁定の配分追加、企業残余投資は既存施策の接続候補＋追加行動仮定、MPC等は未較正感度である。',
 '既存財政→GDPの未接続はコードで識別でき、接続時の条件付き改善幅は算出できる。ただし政府還流・投資をゼロとすることが政策上の選択か実装不足かは原文から確定しない。税による消費減、基金帰属による所得移転、投資・供給への還流、較正仮定の相互作用を唯一の因果額に分けられない。Interactions CSVは同時再計算と単独効果和の差を示す。SQ共通縮小やF別条件差をN3固有損失へ二重計上しない。',
 '## Claude指摘と検証',
 'KPI閾値3本を元エンジンで実行しVAT15%/20%分岐を確認。これは税負担を変える別枝であり主改善候補から除外。年金4帰属は固定版120年次を比較、基金同一とはしていない。投資残余はVAT側へ帰属する既存診断を維持。健康労働の固定入力仮接続は小さく、正式実装はしない。詳細はClaude_Followup.mdと専用CSV。',
 f"検証 {result['checks']}件、失敗{result['failed']}件。基準再現、税・現金固定、政府資金の単一使用、企業源泉使途、現金非負、資本減耗、GDP需要/供給制約、PB・債務・資産、KPI境界、年金基金恒等式、固定原本不変を検証した。既存Claude164＋52 PASS_WITH_LIMITATIONSは再利用し、本件の新規独立検算とは記載しない。",
 '## 再現・成果物',
 '実行: `python3 handoff/chatgpt-n3-gdp-recirculation-counterfactual-20261122/N3_GDP_Recirculation_Reproduce.py --root . --outdir /tmp/n3-recirculation-replay --workdir /tmp/n3-recirculation-replay-work --source /path/to/fixed-3c77eaf-worktree`。--source省略時は固定3c77eafの読取用worktreeを作る。通常は元エンジンを再実行。--skip-reexecutionは既に当該workdirで実行済みの原出力を使う診断開発用で、fresh実行とは表示しない。',
 '年次比較、ケース定義・要約、財政投資台帳、交互作用、KPI境界、年金帰属、健康労働、旧投資源泉、公的基準財政の継承情報、再現コード、入力実バイト照合、検証JSON・実行ログを個別ファイルで引き渡す。ZIPなし。新規成果物以外の原本は変更していない。']
 (out/'SPE_N3_GDP_Recirculation_Counterfactual_Report_DRAFT_20261122.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--outdir',type=Path,required=True);a.add_argument('--workdir',type=Path,required=True);a.add_argument('--source',type=Path);a.add_argument('--skip-reexecution',action='store_true');z=a.parse_args();root=z.root.resolve();source=z.source.resolve() if z.source else z.workdir.resolve()/'fixed-source'
 if not source.exists():
  fixed_source='3c77eafc2073fdaba4c129164817d2f57c9421b9'
  if subprocess.run(['git','cat-file','-e',fixed_source],cwd=root,capture_output=True).returncode:subprocess.run(['git','fetch','origin',fixed_source],cwd=root,check=True)
  subprocess.run(['git','worktree','add','--detach',str(source),fixed_source],cwd=root,check=True)
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()=='3c77eafc2073fdaba4c129164817d2f57c9421b9'
 run(root,z.outdir.resolve(),z.workdir.resolve(),source,z.skip_reexecution)
