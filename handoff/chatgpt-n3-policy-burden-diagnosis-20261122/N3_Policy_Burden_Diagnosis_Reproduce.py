#!/usr/bin/env python3
"""Diagnostic-only reconstruction of fixed N3 burdens. Stdlib + git.
No original source, coefficient, policy or saved result is modified.
"""
import argparse,csv,json,hashlib,sys,subprocess,importlib.util,copy,math,os
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
N3='37c3399f9c553673a79ba1298fc68d758a77055e';ND='handoff/chatgpt-n3-f-parity-implementation-20261122'
BASE='PARITY_CONNECTED_CANDIDATE';SQ='SQ_COMMON_ON'
SELECT=[SQ,BASE,'PARITY_NO_CORPORATE','PARITY_NO_FLAT','PARITY_NO_PENSION','PARITY_MPC_LOW','PARITY_MPC_HIGH','PARITY_KPI_HIGH_THRESHOLD']
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8')))
def num(r,k,default=0.):
 v=r.get(k);return default if v in [None,''] else float(v)
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def pin(root,commit,path,receipts):
 if subprocess.run(['git','cat-file','-e',commit],cwd=root,capture_output=True).returncode:subprocess.run(['git','fetch','origin',commit],cwd=root,check=True)
 b=subprocess.check_output(['git','show',commit+':'+path],cwd=root);local=root/path
 if local.exists():assert b==local.read_bytes(),path
 receipts.append(dict(commit=commit,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),local_matches_fixed=local.exists()))
 return b

def capture(root,out,draft):
 cfg=json.loads((root/ND/'Inputs.json').read_text());original=copy.deepcopy(cfg);cfg['execution_case_filter']=SELECT
 assert {k:v for k,v in cfg.items() if k!='execution_case_filter'}==original
 inp=out/'Isolated_Diagnostic_Input.json';inp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
 records=[];seen=set();params={}
 def local(frame,event,arg):
  if event=='line':
   v=frame.f_locals;r=v.get('r');y=v.get('y');md=frame.f_globals.get('_medical');cid=md.s['id'] if md else None
   if isinstance(r,dict) and r.get('year')==y and (cid,y) not in seen and 'parity_supply_real_trn' in r:
    seen.add((cid,y));params[cid]=copy.deepcopy(v['p'])
    keys=['coreY','coreN','coreD','Y','N','labor','C','I','K','Kprev','supply','desired','capacity','unmet','tax','direct','cash','feedback','invest_nom','admin_firm','firm_response','firm_sources','firm_investment','firm_uninvested','firm_Istate','firm_cash_stock','ei','elderly_subsidy','pension','admin_saving','invflow','education_nom','education_level','finite','prevY','prevN','Ctarget','parity_Cprev','parity_Iprev','nominalwage_proxy']
    records.append(dict(case=cid,year=y,**{k:v.get(k) for k in keys},macro_row=copy.deepcopy(r),demography=copy.deepcopy(v['t']),medical=copy.deepcopy(v['w']),firm=copy.deepcopy(v['firm']),vat=copy.deepcopy(v['f']),social=copy.deepcopy(v['ss']),old_medical=copy.deepcopy(v['med']),pension_ledger=copy.deepcopy(frame.f_globals['_pension'][y-2026]),elder_ledger=copy.deepcopy(v['c']['_elder'][y-2026])))
  return local
 def trace(frame,event,arg):
  if event=='call' and frame.f_code.co_name=='run_path' and frame.f_code.co_filename=='n3_medical_on_SQ_adapter.py':return local
 spec=importlib.util.spec_from_file_location('fixed_n3_burden_execution',root/ND/'Model.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 if not draft.exists():
  c='3c77eafc2073fdaba4c129164817d2f57c9421b9';subprocess.run(['git','fetch','origin',c],cwd=root,check=True);subprocess.run(['git','worktree','add','--detach',str(draft),c],cwd=root,check=True)
 oldtrace=sys.gettrace();oldmode=os.environ.get('SPE_PENSION_MODE');os.environ['SPE_PENSION_MODE']='DOMESTIC_TRANSFER';sys.settrace(trace)
 try:m.run(inp,root,draft,out/'runtime')
 finally:
  sys.settrace(oldtrace)
  if oldmode is None:os.environ.pop('SPE_PENSION_MODE',None)
  else:os.environ['SPE_PENSION_MODE']=oldmode
 assert len(records)==30*len(SELECT),len(records)
 data=dict(parameters=params,records=records);(out/'N3_Unchanged_Execution_Trace.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');return data

def run(root,out,draft):
 out.mkdir(parents=True,exist_ok=True);receipts=[]
 for path in ['Inputs.json','Model.py','Components.py','Macro_Adapter.py','Resolved_Macro_Source.py.txt','results/Annual_DOMESTIC_TRANSFER.csv','results/Annual_LEGACY.csv','results/Annual_FOREIGN_INCOME.csv','results/Annual_ADDITIONAL_VA.csv','results/DOMESTIC_TRANSFER_N3_Policy_Accounts.csv','results/DOMESTIC_TRANSFER_N3_Pension_Accounts.csv','results/Conditional_National_Local_Fiscal.csv','results/Verification.json']:
  pin(root,N3,ND+'/'+path,receipts)
 for path in ['policies/New3linesPolicies.md','handoff/chatgpt-n3-model-expansion-20261121/N3_Components.py','handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Components.py','handoff/f-household-social-20261120/Inputs.json','handoff/chatgpt-national-fiscal-closure-20261121/National_Fiscal.py','handoff/f-common-endoflife-finalization-20261121/Model.py','handoff/f-vat-core-20261120/Model.py']:
  pin(root,N3,path,receipts)
 for commit,path,name in [
 ('ba08c45d4ecb99defecb8416c8d63e0cbfde8cb4','handoff/claude-n3-f-parity-verification-20261122/N3_F_Parity_Independent_Summary_DRAFT_20261122.json','Reused_Claude_Macro_Summary.json'),
 ('ba08c45d4ecb99defecb8416c8d63e0cbfde8cb4','handoff/claude-n3-f-parity-verification-20261122/N3_F_Parity_Fiscal_Summary_DRAFT_20261122.json','Reused_Claude_Fiscal_Summary.json'),
 ('004bcb217c81879c2b13e2c11fab85376a1a8893','handoff/claude-n3-f-statusquo-report-20261122/SPE_N3_F_StatusQuo_Comparison_Report_DRAFT_20261122.md',None),
 ('4453f5300e1a6e2320b45c30d4e3767ed9e8b74e','handoff/chatgpt-sq-growth-diagnosis-20261122/SQ_Growth_Contribution_Summary.csv',None)]:
  b=pin(root,commit,path,receipts)
  if name:(out/name).write_bytes(b)
 (out/'Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 data=capture(root,out,draft);analyze(root,out,data,receipts)

def analyze(root,out,data,receipts):
 idx={(r['case'],r['year']):r for r in data['records']};params=data['parameters'];basecfg=json.loads((root/ND/'Inputs.json').read_text());cp=basecfg['candidate_parameters'];hh=json.loads((root/'handoff/f-household-social-20261120/Inputs.json').read_text());h=hh['stats'];n3rows={int(r['year']):r for r in rd(out/'runtime/Gap_Annual.csv') if r['case']==BASE}
 dyn={(r['case'],int(r['year'])):r for r in rd(out/'runtime/Dynamic_Base_Audit.csv')};firms={(r['case'],int(r['year']),int(r['cell'])):r for r in rd(out/'runtime/N3_Corporate_Accounts.csv')};pens={(r['case'],int(r['year'])):r for r in rd(out/'runtime/N3_Pension_Accounts.csv')};semis={(r['case'],int(r['year'])):r for r in rd(out/'runtime/Gap_Semi_Medical.csv')};fixedall=rd(root/ND/'results/Annual_DOMESTIC_TRANSFER.csv');fixed={(r['case'],int(r['year'])):r for r in fixedall}
 checks=[]
 def chk(name,a,b=0.,tol=2e-7):checks.append(dict(check=name,error=a-b,tolerance=tol,pass_=abs(a-b)<=tol))
 def ph(y,start,ramp):return max(0.,min(1.,(y-start+1)/ramp))
 tax=[];cells=[];cashrows=[];taxsens=[];flowrows=[];investment=[];gdp=[];cs={};ist={};ks={};taxprev=None
 def flows(t):
  w=t['medical'];r=t['year'];pen=t['pension_ledger'];el=t['elder_ledger'];md=t['old_medical'];ss=t['social'];f=t['vat'];reserve=num(semis.get((t['case'],r),{}),'household_extra_premium_trn')
  z=dict(flat_labor=-w['labour_business_flat30_tax_delta_trn'],financial20=-w['household_financial20_tax_delta_trn'],estate=-w['wealth_tax_delta_trn'],corporate_dividend_net=.8*w['dividend_delta_trn'],premium_relief=w['premium_relief_trn'],in_kind_substitution=.7*w['in_kind_trn'],public_payroll=w['public_payroll_delta_trn'],pension_benefit=w['pension_benefit_delta_trn'],fund_payout=w['pension_fund_payout_trn'],fund_return_domestic_debit=-w['pension_domestic_income_debit_trn'],semi_med_reserve=-reserve,EITC_removed=-w['EITC_removal_trn'],medical_net=w['medical_only_household_cash_delta_trn'])
  z.update(VAT_price=f.get('_price_effect',0.),VAT_wage=f['household']-f.get('_price_effect',0.),legacy_elder_net=(t['pension'] or 0.)-el['employee_contribution_base_trn']*t['ei'],legacy_pension=pen['household_cash_delta_trn'],legacy_medical=md['household'],legacy_social=ss['household']-ss.get('vat_return',0.) if params[t['case']]['vat_return_interpretation']=='RECLASSIFY_PRICE_RELIEF' else ss['household'])
  return z
 def target_channels(t,z):
  p=params[t['case']];w=t['medical'];D=t['coreD'];m=p['generic_mpc'];d=p['domestic_share'];pen=t['pension_ledger'];ss=t['social'];r={k:d*m*v/D for k,v in z.items()}
  r['legacy_social']-=d*m*ss['household']/D;r['legacy_social_weighted']=d*ss['weighted_demand']/D;r['legacy_pension']-=d*m*pen['household_cash_delta_trn']/D;r['legacy_pension_weighted']=d*pen['consumption_impulse_trn']/D
  r['estate']+=d*(m-w['estate_mpc_candidate'])*w['wealth_tax_delta_trn']/D;r['quantity_volume']=d*w['quantity_nominal_volume_delta_trn']/D;r['quantity_price_replacement']=-d*m*w['quantity_replaced_price_benefit_trn']/D;r['income_feedback']=d*m*t['feedback']/D
  return r
 for year in range(2026,2056):
  t=idx[BASE,year];s=idx[SQ,year];w=t['medical'];p=params[BASE];Dfixed=idx[SQ,year]['coreD'];priceidx=Dfixed/idx[SQ,2026]['coreD'];wage=num(dyn[BASE,year],'wage_base_factor');count=t['demography']['population']/h['mean_household_size'];hhphase=ph(year,2030,3)
  sums={k:0. for k in ['gross_income','labor_base','financial_base','baseline_labor_tax','baseline_financial_tax','target_labor_tax','target_financial_tax','all_baseline_national_tax','local_tax_reference']}
  chk('household_cell_weights_'+str(year),sum(c['share'] for c in hh['income_cells']),1.,1e-12)
  for j,c in enumerate(hh['income_cells']):
   q=c['quintile'];n=count*c['share'];inc=c['income_yen']*priceidx*cp['income_scale']*wage;elder=c['elder_share'];ls=.95*(1-elder)+.20*elder;fs=.05*(1-elder)+.10*elder
   oldtax=h['income_tax_mean_paid_yen'][q]*h['income_tax_paid_per2000'][q]/2000*priceidx*wage;local=h['local_tax_mean_paid_yen'][q]*h['local_tax_paid_per2000'][q]/2000*priceidx*wage
   row=dict(year=year,cell=j,households=n,population=t['demography']['population'],mean_household_size=2.22,income_per_household_nominal_yen=inc,income_weight=c['share'],quintile=q,elder_share=elder,labor_share=ls,financial_share=fs,wage_factor_lagged=wage,common_price_index=priceidx,phase=hhphase,gross_income_trn=n*inc/1e12,labor_base_trn=n*inc*ls/1e12,financial_base_trn=n*inc*fs/1e12,baseline_labor_tax_trn=n*oldtax*ls/1e12,baseline_financial_tax_trn=n*oldtax*fs/1e12,target_labor_tax_trn=n*inc*ls*.30/1e12,target_financial_tax_trn=n*inc*fs*.20/1e12)
   row['labor_delta_trn']=(row['target_labor_tax_trn']-row['baseline_labor_tax_trn'])*hhphase;row['financial_delta_trn']=(row['target_financial_tax_trn']-row['baseline_financial_tax_trn'])*hhphase
   cells.append(row)
   for k in ['gross_income','labor_base','financial_base','baseline_labor_tax','baseline_financial_tax','target_labor_tax','target_financial_tax']:sums[k]+=row[k+'_trn']
   sums['all_baseline_national_tax']+=n*oldtax/1e12;sums['local_tax_reference']+=n*local/1e12
  lab=hhphase*(sums['target_labor_tax']-sums['baseline_labor_tax']);fin=hhphase*(sums['target_financial_tax']-sums['baseline_financial_tax']);chk('labor_tax_recomputed_'+str(year),lab,w['labour_business_flat30_tax_delta_trn']);chk('financial_tax_recomputed_'+str(year),fin,w['household_financial20_tax_delta_trn'])
  corpold=corpnew=profit=0.
  for j in range(len(cp['firm_cells'])):
   f=firms[BASE,year,j];profit+=num(f,'profit_base_trn');corpold+=.3*num(f,'profit_base_trn');corpnew+=num(f,'effective_rate_candidate')*num(f,'profit_base_trn')
  corp=corpnew-corpold;chk('corporate_tax_recomputed_'+str(year),corp,w['corporate_tax_delta_trn']);divtax=.2*w['dividend_delta_trn'];estateold=w['estate_reported_old_tax_trn'];estatetarget=w['estate40_reported_target_trn'];estate=ph(year,2030,3)*(estatetarget-estateold)
  chk('estate_delta_'+str(year),estate,w['wealth_tax_delta_trn']);policy=lab+fin+corp+divtax+estate;chk('policy_tax_sum_'+str(year),policy,w['policy_tax_delta_trn'])
  tx=dict(year=year,population=t['demography']['population'],households_synthetic=count,mean_household_size=2.22,source_income_year=2024,source_survey_year=2025,phase_flat=hhphase,common_price_index=priceidx,lagged_wage_factor=wage,**{k+'_trn':v for k,v in sums.items()},labor_tax_before_trn=sums['baseline_labor_tax'],labor_tax_after_trn=sums['baseline_labor_tax']+lab,labor_tax_delta_trn=lab,financial_tax_before_trn=sums['baseline_financial_tax'],financial_tax_after_trn=sums['baseline_financial_tax']+fin,financial_tax_delta_trn=fin,corporate_profit_candidate_trn=profit,corporate_tax_before_trn=corpold,corporate_tax_after_trn=corpnew,corporate_tax_delta_trn=corp,dividend_financial_tax_delta_trn=divtax,estate_tax_before_trn=estateold,estate_tax_after_trn=estateold+estate,estate_tax_delta_trn=estate,policy_tax_delta_trn=policy,policy_tax_delta_change_from_previous_year_trn=policy-(taxprev if taxprev is not None else policy),VAT_direct_delta_trn=t['vat']['direct_tax'],medical_direct_tax_delta_trn=w['medical_financing_direct_tax_trn'],macro_tax_trn=t['tax'],diagnostic_tax_trn=t['tax']+t['direct'],SQ_diagnostic_tax_trn=s['tax']+s['direct'],diagnostic_tax_minus_SQ_trn=t['tax']+t['direct']-s['tax']-s['direct'],diagnostic_tax_to_nominal_GDP_pct=100*(t['tax']+t['direct'])/t['N'],macro_tax_cap_trn=.3*t['N'],diagnostic_tax_above_macro_cap_trn=max(0.,t['tax']+t['direct']-.3*t['N']))
  tx.update(VAT_before_SQ_trn=num(fixed[SQ,year],'modeled_VAT_trn'),VAT_after_trn=num(fixed[BASE,year],'modeled_VAT_trn'),VAT_change_vs_SQ_trn=num(fixed[BASE,year],'modeled_VAT_trn')-num(fixed[SQ,year],'modeled_VAT_trn'),standard_rate=num(n3rows[year],'standard_rate',None),food_rate=num(n3rows[year],'food_rate',None))
  chk('VAT_policy_macro_once_'+str(year),t['tax']+t['vat']['direct_tax']+w['engine_direct_tax_delta_trn'],t['macro_row']['tax_diagnostic_trn']);tax.append(tx);taxprev=policy
  z=flows(t);zs=flows(s);chk('cash_full_components_'+str(year),sum(z.values()),t['cash']);chk('cash_medical_components_'+str(year),sum(z[k] for k in z if not k.startswith('VAT_') and not k.startswith('legacy_')),w['household_cash_delta_trn'])
  ni=t['macro_row']['household_disposable_nominal_trn']-t['vat'].get('_price_effect',0.);si=s['macro_row']['household_disposable_nominal_trn']-s['vat'].get('_price_effect',0.)
  cr=dict(year=year,**{k+'_trn':v for k,v in z.items()},medical_plus_policy_HH_change_trn=w['household_cash_delta_trn'],full_macro_household_cash_delta_trn=t['cash'],SQ_medical_HH_change_trn=s['medical']['household_cash_delta_trn'],N3_cash_DI_comparable_proxy_trn=ni,SQ_cash_DI_comparable_proxy_trn=si,cash_DI_level_gap_trn=ni-si,core_income_level_gap_trn=p['household_income_share']*(t['coreN']-s['coreN']),macro_cash_change_gap_trn=t['cash']-s['cash'],income_feedback_gap_trn=t['feedback']-s['feedback'],VAT_price_reclassification_gap_trn=-t['vat'].get('_price_effect',0.)+s['vat'].get('_price_effect',0.))
  cr['difference_between_level_gap_and_policy_medical_change_trn']=(ni-si)-w['household_cash_delta_trn'];cr['SQ_medical_offset_trn']=-s['medical']['household_cash_delta_trn'];cr['VAT_wage_gap_trn']=z['VAT_wage']-zs['VAT_wage'];cr['legacy_other_gap_trn']=sum(z[k]-zs.get(k,0.) for k in z if k.startswith('legacy_'))
  chk('DI_level_bridge_'+str(year),cr['core_income_level_gap_trn']+cr['macro_cash_change_gap_trn']+cr['income_feedback_gap_trn']+cr['VAT_price_reclassification_gap_trn'],ni-si);cashrows.append(cr)
  # Explicit counterpart ledger uses the same primitive amounts; not a full national SFC closure.
  counterpart={'flat_labor':('HH','GOVERNMENT'),'financial20':('HH','GOVERNMENT'),'estate':('HH','GOVERNMENT'),'corporate_dividend_net':('CORPORATE','HH+GOVERNMENT_20PCT'),'premium_relief':('INSURER','HH'),'in_kind_substitution':('GOVERNMENT','HH_EXPENSE_SUBSTITUTION_NOT_CASH'),'public_payroll':('GOVERNMENT','HH'),'pension_benefit':('PUBLIC_PENSION','HH'),'fund_payout':('PENSION_FUND','HH'),'fund_return_domestic_debit':('HH_PROPERTY_INCOME','PENSION_FUND'),'semi_med_reserve':('HH','SEMI_MED_FUND'),'medical_net':('HH+PROVIDER+GOV+INSURER','AGGREGATED_PAYER_MODEL'),'VAT_price':('HH','VAT_PRODUCER_GOV'),'VAT_wage':('HH_WAGES','PRODUCER_VAT_INCIDENCE')}
  for k,val in z.items():
   if k in counterpart:flowrows.append(dict(year=year,channel=k,household_effect_nominal_trn=val,from_sector=counterpart[k][0],to_sector=counterpart[k][1],scope='PARTIAL_CHANGE_LEDGER_NOT_FULL_NATIONAL_ACCOUNTS'))
  for basis_scale in [.8,1.,1.2]:taxsens.append(dict(year=year,kind='FIXED_INPUT_TAX_EXPOSURE_SCALE',case=str(basis_scale),labor_financial_tax_delta_trn=(lab+fin)*basis_scale,delta_vs_base_trn=(lab+fin)*(basis_scale-1),GDP_effect_trn=None,not_adopted=True,additive=False,original_model_changed=False))
  for rate in [.25,.30,.35]:
   value=hhphase*(rate*sums['labor_base']-sums['baseline_labor_tax']);taxsens.append(dict(year=year,kind='DIAGNOSTIC_ONLY_LABOR_RATE_NOT_POLICY_CHANGE',case=str(rate),labor_financial_tax_delta_trn=value+fin,delta_vs_base_trn=value-lab,GDP_effect_trn=None,not_adopted=True,additive=False,original_model_changed=False))
  for cid in [SQ,BASE]:
   u=idx[cid,year];q=params[cid];v=flows(u);targets=target_channels(u,v);chk('consumption_target_'+cid+'_'+str(year),sum(targets.values()),u['Ctarget'])
   state=cs.setdefault(cid,{k:0. for k in targets})
   for k in targets:
    if year>2026:state[k]=(1-q['lambda_C'])*state[k]+q['lambda_C']*targets[k]
   chk('consumption_channel_convolution_'+cid+'_'+str(year),sum(state.values()),u['C'])
   # Each investment input is injected once; same smoothing/capital rule as engine.
   f=u['firm'];old=u['old_medical'];el=u['elder_ledger'];pe=u['pension_ledger'];vat=u['vat'];ww=u['medical']
   invflows=dict(N3_corporate=ww['policy_investment_delta_trn'],VAT=vat['investment'],legacy_firm=f['investment'] or 0.,legacy_promotion=u['invflow'] or 0.,legacy_hubs=old['hubs'] or 0.,legacy_admin=u['firm_response']*(u['admin_saving'] or 0.),legacy_elder_subsidy=u['firm_response']*u['elderly_subsidy'],legacy_employer_cost=-u['firm_response']*(el['employer_contribution_base_trn']*u['ei']+pe['employer_premium_delta_trn']))
   chk('investment_sources_'+cid+'_'+str(year),sum(invflows.values()),u['invest_nom']);ii=ist.setdefault(cid,{k:0. for k in invflows});kk=ks.setdefault(cid,{k:0. for k in invflows});supplyparts={}
   for k,value in invflows.items():
    supplyparts[k]=q['capital_yield']*(1-q['depreciation'])*kk[k]
    if year>2026:ii[k]=(1-q['lambda_I'])*ii[k]+q['lambda_I']*value/u['coreD'];kk[k]=(1-q['depreciation'])*kk[k]+ii[k]
   chk('investment_state_'+cid+'_'+str(year),sum(ii.values()),u['I']);chk('capital_state_'+cid+'_'+str(year),sum(kk.values()),u['K']);chk('supply_state_'+cid+'_'+str(year),sum(supplyparts.values()),u['supply'])
   investment.append(dict(case=cid,year=year,**{k+'_nominal_flow_trn':val for k,val in invflows.items()},net_nominal_investment_trn=u['invest_nom'],real_I_trn=u['I'],additional_K_real_trn=u['K'],**{k+'_I_real_trn':val for k,val in ii.items()},**{k+'_supply_real_trn':val for k,val in supplyparts.items()}))
  gi=dict(year=year,N3_real_GDP_trn=t['Y'],SQ_real_GDP_trn=s['Y'],real_GDP_gap_trn=t['Y']-s['Y'],core_gap_trn=t['coreY']-s['coreY'],consumption_gap_trn=t['C']-s['C'],investment_gap_trn=t['I']-s['I'],supply_absorption_gap_trn=p['capacity_absorption']*(t['supply']-s['supply']),service_VA_gap_trn=w['service_production_nominal_delta_trn']/t['coreD']-s['medical']['service_production_nominal_delta_trn']/s['coreD'],unmet_gap_trn=-t['unmet']+s['unmet'],education_gap_trn=t['education_nom']/t['coreD']-s['education_nom']/s['coreD'],method='EXACT_REALIZED_PATH_IDENTITY_WITH_LINEAR_CHANNEL_CONVOLUTIONS_NOT_CAUSAL_ABLATION',common_SQ_shrinkage_readded=False)
  gi.update({k+'_C_gap_trn':cs[BASE][k]-cs[SQ][k] for k in cs[BASE]});gi['sum_GDP_bridge_trn']=sum(gi[k] for k in ['core_gap_trn','consumption_gap_trn','investment_gap_trn','supply_absorption_gap_trn','service_VA_gap_trn','unmet_gap_trn','education_gap_trn']);gi['residual_trn']=gi['real_GDP_gap_trn']-gi['sum_GDP_bridge_trn'];chk('GDP_gap_identity_'+str(year),gi['residual_trn']);gdp.append(gi)
  chk('same_common_labor_'+str(year),t['labor'],s['labor']);chk('same_common_core_'+str(year),t['coreY'],s['coreY']);chk('no_second_pension_charge_'+str(year),w['pension_second_contribution_charge_trn'])
 for r in data['records']:
  chk('fixed_GDP_reexecution_'+r['case']+'_'+str(r['year']),r['Y'],num(fixed[r['case'],r['year']],'real_gdp_trn'))
 dump(out/'N3_Annual_Tax_Bridge_2026_2055.csv',tax);dump(out/'N3_Tax_Base_Cell_Reconstruction.csv',cells);dump(out/'N3_Annual_Tax_Household_Bridge_2026_2055.csv',cashrows);dump(out/'N3_Household_Counterpart_Ledger.csv',flowrows);dump(out/'N3_GDP_Gap_Decomposition_2026_2055.csv',gdp);dump(out/'N3_Investment_Source_Decomposition.csv',investment)
 sensitivity=[]
 for case in basecfg['parity_cases']:
  for y in range(2026,2056):
   r=fixed[case,y];b=fixed[BASE,y]
   for metric in ['real_gdp_trn','macro_cash_DI_proxy_trn','policy_tax_delta_trn','pension_fund_stock_trn','I_policy_real_trn']:
    sensitivity.append(dict(year=y,kind='EXISTING_SINGLE_CASE_REEXECUTED_OR_REUSED',case=case,metric=metric,value=num(r,metric),delta_vs_base_trn=num(r,metric)-num(b,metric),additive=False,source_commit=N3,not_adopted=True))
 sensitivity+=taxsens;dump(out/'N3_Policy_Burden_Sensitivity.csv',sensitivity)
 extra=additional_diagnostics(root,out,data,idx,params,checks,chk,tax,cashrows,gdp)
 for f in receipts:
  file=root/f['path']
  if file.exists():chk('source_unchanged:'+f['path'],0 if hashlib.sha256(file.read_bytes()).hexdigest()==f['sha256'] else 1,0,0)
 fail=[c for c in checks if not c['pass_']];result=dict(status='PASS_DIAGNOSTIC_RECONSTRUCTION' if not fail else 'FAIL',checks=len(checks),failed=len(fail),failures=fail,checks_detail=checks,input_commit=N3,request_commit='83c93be124877bf3cda21ae56dad33e597dcddf5',independent_AI_review=False,scope='Arithmetic reconstruction and classification, not calibration or policy adoption',limits=['Taxpayer microdata missing','Pension return incidence undecided','Survey households and macro household income are nonidentical proxies','No full general-government closure or fiscal-to-GDP feedback','Official statistics check limited to mean and aggregates; no micro calibration'])
 (out/'N3_Policy_Burden_Diagnosis_Verification.json').write_text(json.dumps(result,indent=2)+'\n');assert not fail,fail[:3]
 report(root,out,data,tax,cashrows,gdp,extra,result)
 print('N3_BURDEN_DIAGNOSIS_PASS',len(checks),'checks')

def additional_diagnostics(root,out,data,idx,params,checks,chk,tax,cash,gdp):
 basecfg=json.loads((root/ND/'Inputs.json').read_text());p=params[BASE];reg=rd(out/'runtime/N3_VAT_Regular_Quantity.csv');sector=rd(out/'runtime/N3_VAT_Sectors.csv');vatparts=[]
 for y in range(2026,2056):
  t=idx[BASE,y];parts=[]
  for r in reg:
   if r['case']==BASE and int(r['year'])==y:parts.append((r['market'],num(r,'investment'),num(r,'producer')))
  for r in sector:
   if r['case']==BASE and int(r['year'])==y:parts.append((r['sector'],num(r,'induced_investment_trn'),num(r,'provider_operating_benefit_fixed_volume_trn')))
  for name,I,source in parts:vatparts.append(dict(year=y,source=name,VAT_induced_investment_nominal_trn=I,business_or_producer_resource_delta_trn=source,scope='N3_VAT_INCIDENCE_NOT_EMPLOYER_PREMIUM'))
  chk('VAT_investment_sector_sum_'+str(y),sum(z[1] for z in parts),t['vat']['investment'])
  chk('employer_cost_zero_main_'+str(y),t['admin_firm'],0.)
 dump(out/'N3_VAT_Negative_Investment_Sources.csv',vatparts)
 modes=['DOMESTIC_TRANSFER','LEGACY','FOREIGN_INCOME','ADDITIONAL_VA'];mrows=[];fundspreads=[]
 bymode={mode:{int(r['year']):r for r in rd(root/ND/('results/Annual_'+mode+'.csv')) if r['case']==BASE} for mode in modes}
 for y in range(2026,2056):
  b=bymode['DOMESTIC_TRANSFER'][y];assets=[]
  for mode in modes:
   r=bymode[mode][y];assets.append(num(r,'pension_fund_stock_trn'));mrows.append(dict(mode=mode,year=y,real_GDP_trn=num(r,'real_gdp_trn'),GDP_minus_domestic_trn=num(r,'real_gdp_trn')-num(b,'real_gdp_trn'),fund_asset_trn=num(r,'pension_fund_stock_trn'),asset_minus_domestic_trn=num(r,'pension_fund_stock_trn')-num(b,'pension_fund_stock_trn'),fund_return_trn=num(r,'pension_return_trn'),household_cash_delta_trn=num(r,'household_cash_delta_trn'),domestic_income_debit_trn=num(r,'pension_domestic_income_debit_trn'),external_primary_income_trn=num(r,'pension_external_primary_income_trn'),additional_VA_nominal_trn=num(r,'pension_additional_VA_nominal_trn'),ownership='CANDIDATE_NOT_ADOPTED'))
  fundspreads.append(max(assets)-min(assets))
 dump(out/'N3_Pension_Four_Mode_Bridge.csv',mrows)
 all_modes={mode:{(r['case'],int(r['year'])):r for r in rd(root/ND/('results/Annual_'+mode+'.csv'))} for mode in modes};global_spread=0.;spread_case=None
 for case in basecfg['parity_cases']:
  for y in range(2026,2056):
   vals=[num(all_modes[mode][case,y],'pension_fund_stock_trn') for mode in modes];spread=max(vals)-min(vals)
   if spread>global_spread:global_spread=spread;spread_case=dict(case=case,year=y)

 # Verify external taxpayer source statistics only as supplied; no coefficient substitution.
 hh=json.loads((root/'handoff/f-household-social-20261120/Inputs.json').read_text());mean=sum(c['share']*c['income_yen'] for c in hh['income_cells']);financial=sum(c['share']*c['income_yen']*(.05+.05*c['elder_share']) for c in hh['income_cells']);labor=sum(c['share']*c['income_yen']*(.95-.75*c['elder_share']) for c in hh['income_cells'])
 stat=dict(status='LIMITED_PRIMARY_SOURCE_CHECK_NOT_CALIBRATION',sources=[dict(url='https://www.mhlw.go.jp/wp/hakusyo/kousei/26-2/dl/01.pdf',page=10,table='Income, survey2025/income2024',official_mean_household_income_yen=5752000,official_labor_income_yen=4262000,official_property_income_yen=160000,official_public_pension_income_yen=1116000,match_model_mean_input=hh['stats']['mean_income_yen']==5752000),dict(url='https://www.mof.go.jp/policy/budget/budger_workflow/account/fy2024/ke0711b.pdf',page=0,scope='FY2024 general-account receipts, rounded trillion yen',income_tax_trn=21.2,corporate_tax_trn=17.9,VAT_trn=25.0,total_tax_trn=75.2,scope_not_equal_to_future_synthetic_household_tax=True)],synthetic_cell_mean_income_yen=mean,mean_input_yen=hh['stats']['mean_income_yen'],synthetic_labor_income_yen=labor,synthetic_financial_income_yen=financial,synthetic_financial_share=financial/mean,official_property_share=160000/5752000,comparison_limit='Survey property income excludes some financial-tax bases; midpoint/tail cells and age/source allocation synthetic, not national tax microdata',not_verified=['Official joint taxpayer microdata','Future household size/distribution','Full gross financial capital-gains base','FY2026+ actual income/corporate tax projections'])
 (out/'Official_Statistics_Limited_Check.json').write_text(json.dumps(stat,indent=2)+'\n')
 # KPI band holds the already determined lagged 2034/2033 income, not future output.
 events=rd(out/'runtime/KPI_Events.csv');growth=next(num(r,'previous_income_growth_pct') for r in events if r['case']==BASE and r['year']=='2035');bands=[]
 for threshold in [-.5,0.,.1,.15,.17,.175,.176,.18,.2,.5]:bands.append(dict(evaluation_year=2035,actual_lagged_income_proxy_growth_pct=growth,threshold_candidate_pct=threshold,freeze=growth<threshold,VAT_2040_candidate=.15 if growth<threshold else .20,threshold_adopted=False,method='FIXED_2035_OBSERVATION_THRESHOLD_BAND_NO_NEW_MODEL_RUN',interpretation='FREEZE_AFTER2035_NOT_POLICY_PACE_RELAXATION'))
 dump(out/'N3_KPI_Threshold_Band.csv',bands)
 # Reuse verified fiscal equations and inputs, replace only primary-delta scale in diagnostic arithmetic.
 path=root/'handoff/chatgpt-national-fiscal-closure-20261121/National_Fiscal.py';sp=importlib.util.spec_from_file_location('fixed_nf_diagnostic',path);nf=importlib.util.module_from_spec(sp);sp.loader.exec_module(nf)
 cfg=json.loads((path.parent/'Fiscal_Inputs.json').read_text());scenario=cfg['scenarios'][0];official={int(r['year']):{k:float(v) if k.endswith('_trn') and v else v for k,v in r.items()} for r in rd(path.parent/'Official_Fiscal_Baseline_2025_2040.csv')};bas=nf.baseline(scenario,official)
 fixed={int(r['year']):r for r in rd(root/ND/'results/Conditional_National_Local_Fiscal.csv') if r['case']==BASE and r['mode']=='DOMESTIC_TRANSFER' and r['scenario']=='REFERENCE_CANDIDATE'}
 primary={};fbridge=[]
 for y in range(2026,2056):
  t=idx[BASE,y];s=idx[SQ,y];taxdelta=t['macro_row']['tax_diagnostic_trn']-s['macro_row']['tax_diagnostic_trn'];exdelta=t['macro_row']['expenditure_diagnostic_trn']-s['macro_row']['expenditure_diagnostic_trn'];interest=t['medical'].get('medical_policy_interest_trn',0.)-s['medical'].get('medical_policy_interest_trn',0.);primary[y]=taxdelta-exdelta+interest
  chk('fiscal_primary_from_macro_'+str(y),bas[y]['CL_PB_trn']+primary[y],num(fixed[y],'CL_PB_candidate_trn'),3e-6)
  fbridge.append(dict(year=y,macro_tax_difference_trn=t['tax']-s['tax'],VAT_direct_difference_trn=t['vat']['direct_tax']-s['vat']['direct_tax'],policy_tax_difference_trn=t['medical']['policy_tax_delta_trn'],medical_direct_tax_difference_trn=t['medical']['medical_financing_direct_tax_trn']-s['medical']['medical_financing_direct_tax_trn'],total_tax_difference_trn=taxdelta,expenditure_difference_trn=exdelta,old_interest_removed_trn=interest,policy_primary_delta_trn=primary[y],baseline_CL_PB_trn=bas[y]['CL_PB_trn'],candidate_CL_PB_trn=num(fixed[y],'CL_PB_candidate_trn'),candidate_CL_debt_trn=num(fixed[y],'CL_debt_end_candidate_trn'),general_government_PB=None,general_government_debt=None,actual_bond_issue=None,financing_to_GDP_feedback=False))
  chk('fiscal_tax_channel_once_'+str(y),sum(fbridge[-1][k] for k in ['macro_tax_difference_trn','VAT_direct_difference_trn','policy_tax_difference_trn','medical_direct_tax_difference_trn']),taxdelta)
 def fiscal(scale,collect=False):
  debt=official[2025]['CL_debt_end_trn'];assets=0.;rows=[];zero=None
  for y in range(2026,2056):
   b=bas[y];rate=scenario['incremental_interest_rate'];basedebt=b['CL_debt_begin_trn'];interest=b['CL_net_interest_trn']*min(1.,debt/basedebt)+rate*max(0.,debt-basedebt)-rate*assets;pb=b['CL_PB_trn']+primary[y]*scale
   z=nf.finance(debt,assets,pb,interest,b['stock_flow_adjustment_unallocated_trn'],scenario['refinance_share']);debt=z['CL_debt_end_candidate_trn'];assets=z['CL_cash_assets_end_candidate_trn']
   if zero is None and debt<=1e-8:zero=y
   if scale==1.:
    chk('fiscal_debt_reconstructed_'+str(y),debt,num(fixed[y],'CL_debt_end_candidate_trn'),3e-6)
   if collect:rows.append(dict(scale=scale,year=y,CL_PB_candidate_trn=pb,CL_debt_candidate_trn=debt,CL_cash_assets_candidate_trn=assets,method='DIAGNOSTIC_POLICY_PRIMARY_DELTA_REALIZATION_SCALE',general_government_closed=False,GDP_feedback=False))
  return debt,assets,zero,rows
 fs=[]
 for scale in [0.,.5,.6,.65,.7,.8,1.]:fs+=fiscal(scale,True)[3]
 lo,hi=0.,1.
 for j in range(50):
  mid=(lo+hi)/2
  if fiscal(mid)[0]<=1e-8:hi=mid
  else:lo=mid
 break_even=hi;fs.append(dict(scale=break_even,year=2055,CL_PB_candidate_trn=None,CL_debt_candidate_trn=fiscal(break_even)[0],CL_cash_assets_candidate_trn=fiscal(break_even)[1],method='BREAK_EVEN_PRIMARY_DELTA_SCALE_FOR_ZERO2055_DEBT',general_government_closed=False,GDP_feedback=False))
 dump(out/'N3_Conditional_Fiscal_Primary_Bridge.csv',fbridge);dump(out/'N3_Fiscal_Realization_Sensitivity.csv',fs)
 # Compare calculated but unconnected health labor with the actual trajectory.
 hl=[]
 for y in range(2026,2056):
  t=idx[BASE,y];s=idx[SQ,y];delta=t['medical']['health_effective_labor_added']-s['medical']['health_effective_labor_added'];cf=t['coreY']*((t['labor']+delta)/t['labor'])**p['labor_response']-t['coreY']
  hl.append(dict(year=y,computed_health_effective_labor_difference=delta,actual_effective_labor_difference=t['labor']-s['labor'],fixed_input_core_only_effect_if_connected_trn=cf,classification='IMPLEMENTATION_MISMATCH_COMPUTED_CHANNEL_NOT_CONNECTED',not_actual_GDP_contribution=True))
 dump(out/'N3_Unconnected_Health_Labor_Diagnostic.csv',hl)
 issues=[
 ('TAX_GROSS_BASE','UNCALIBRATED_ASSUMPTION','HIGH','30% of synthetic gross labor/business income vs allocated observed effective old tax ~5%; household/source joint distribution not microdata',tax[9]['labor_tax_delta_trn']),
 ('TAX_POPULATION','UNCALIBRATED_ASSUMPTION','HIGH','population/2.22, 2024 cell distribution, 1.04 initial uplift and common inflation reused through2055',None),
 ('MACRO_TAX_COVERAGE','STRUCTURAL_LIMITATION','HIGH','80trn macro tax proxy plus statutory deltas not a fully calibrated national tax system; 30% cap applies before direct deltas',tax[-1]['diagnostic_tax_above_macro_cap_trn']),
 ('VAT_NEGATIVE_I_EXPLANATION','EXPLANATION_MISMATCH','HIGH','Prior Claude employer-cost explanation not supported in main case: admin/employer=0; VAT regular/sector costs generate remainder',idx[BASE,2045]['vat']['investment']),
 ('HEALTH_LABOR','IMPLEMENTATION_MISMATCH','MEDIUM','Computed health labor is not added in N3 trajectory; F adapter does connect health labor. Diagnose only, do not repair',hl[-1]['fixed_input_core_only_effect_if_connected_trn']),
 ('RETURN_OWNERSHIP','UNDECIDED_POLICY_INTERPRETATION','HIGH','four unadopted source allocations; dynamic wage basis makes assets mode dependent',global_spread),
 ('KPI_THRESHOLD','UNDECIDED_POLICY_INTERPRETATION','HIGH','0% threshold not specified; income proxy not observed median; freeze vs pace-relaxation alternatives',growth),
 ('FINANCIAL_BASE','NOT_IDENTIFIED','HIGH','Synthetic financial-income allocation cannot be treated as actual full financial tax base',None),
 ('FISCAL_RECYCLE','STRUCTURAL_LIMITATION','HIGH','Additional receipts retire conditional debt/save; no automatic household recycling or fiscal-to-GDP loop',None),
 ('HOUSEHOLD_CASH_LABEL','STRUCTURAL_LIMITATION','MEDIUM','HH cash contains 70% in-kind expense substitution, and -153.8 excludes VAT/lagged feedback; DI comparison uses other definition',cash[-1]['difference_between_level_gap_and_policy_medical_change_trn']),
 ('MEDICAL_CAP_TIMING','UNDECIDED_POLICY_INTERPRETATION','MEDIUM','N3 base50 copay/cap-same and protected pension cohorts are candidates, not complete original policy adoption',None),
 ('GDP_ARITHMETIC','ARITHMETIC_CHECK_PASS','INFO','Exact annual tax/cash/C/I/K/GDP identities checked; no arithmetic error found in these tested paths',max(abs(r['residual_trn']) for r in gdp))]
 dump(out/'N3_Diagnostic_Issue_Classification.csv',[dict(id=a,classification=b,priority=c,evidence=d,numerical_value=e) for a,b,c,d,e in issues])
 return dict(fund_asset_max_spread=global_spread,base_fund_asset_max_spread=max(fundspreads),fund_spread_case=spread_case,KPI_growth=growth,fiscal_break_even_scale=break_even,first_zero_debt_year=fiscal(1.)[2],fiscal_2055=fbridge[-1],health_labor=hl[-1],official=stat)

def report(root,out,data,tax,cash,gdp,extra,result):
 a=tax[9];b=tax[-1];h=cash[-1];g=gdp[-1];fx=extra['fiscal_2055'];idx={(r['case'],r['year']):r for r in data['records']}
 def table(rows,head='項目',right='兆円'):
  return f'|{head}|{right}|\n|---|---:|\n'+''.join(f'|{k}|{v:+.6f}|\n' for k,v in rows)
 tx='|政策税の構成|2035年|2055年|\n|---|---:|---:|\n'
 for label,key in [('労働・事業30%差分','labor_tax_delta_trn'),('金融20%差分','financial_tax_delta_trn'),('法人税差分','corporate_tax_delta_trn'),('追加配当20%税','dividend_financial_tax_delta_trn'),('申告相続40%差分','estate_tax_delta_trn'),('合計','policy_tax_delta_trn')]:tx+=f"|{label}|{a[key]:+.6f}|{b[key]:+.6f}|\n"
 hhrows=[('労働・事業税',h['flat_labor_trn']),('金融税',h['financial20_trn']),('相続税',h['estate_trn']),('年金給付減',h['pension_benefit_trn']),('基金運用益の国内家計所得からの振替',h['fund_return_domestic_debit_trn']),('医療の家計純変化',h['medical_net_trn']),('配当手取り',h['corporate_dividend_net_trn']),('基金給付',h['fund_payout_trn']),('保険料減免',h['premium_relief_trn']),('現物給付による支出代替',h['in_kind_substitution_trn']),('公務員給与増',h['public_payroll_trn']),('合計：医療＋政策の家計変化',h['medical_plus_policy_HH_change_trn'])]
 gdptable=table([('共通基礎GDP差',g['core_gap_trn']),('消費差',g['consumption_gap_trn']),('投資差',g['investment_gap_trn']),('蓄積資本からの供給吸収差',g['supply_absorption_gap_trn']),('サービスVA差',g['service_VA_gap_trn']),('供給制約・教育差',g['unmet_gap_trn']+g['education_gap_trn']),('GDP差合計',g['real_GDP_gap_trn'])])
 text=f'''# SPE｜N3固有の税・家計負担・GDP差分 数値診断

2026-11-22 JST。OWNER-DIRECTED / READ-ONLY DIAGNOSIS / DRAFT / NON-CANONICAL。

## 結論

2035年政策税差分＋85.783988兆円の主因は、労働・事業所得のフラット税差分＋78.142892兆円である。合成された税基礎312.484949兆円×30%＝93.745485兆円から、同じ基礎への割当て改革前税15.602593兆円を引いている。人数や円→兆円の単純な桁誤りは、今回の再計算では見つからない。**合成された総所得基礎への30%課税と、約5%に相当する割当て旧税額の差が大きい**。その水準は全国個票データで較正されていない。

2055年の医療＋政策の家計変化−153.777666兆円は、労働・金融・相続税計−118.745773兆円と、年金給付減−33.545952兆円等から発生する。SQ比の比較可能な家計現金proxy水準差−163.412529兆円とは定義が違い、追加の−9.634863兆円はVAT賃金帰着と前年GDPからの所得feedback等で説明できる。

N3−SQの実質GDP差−47.631465兆円は、消費差−48.640386兆円を、投資・資本供給・サービスVAの計＋1.008921兆円が一部相殺している。SQの共通縮小−51.037664兆円はここへ再加算しない。

今回確認した計算経路の恒等式は一致する。一方、**旧検算の投資残余に関する説明の誤り**と、**計算された健康労働損失がN3マクロへ未接続**という実装上の不足を特定した。モデル修正や政策採用は行っていない。

## 取得・再利用と実行範囲

- N3原本：`37c3399f9c553673a79ba1298fc68d758a77055e`。
- Claude独立検算：`ba08c45d4ecb99defecb8416c8d63e0cbfde8cb4`。164マクロ・52財政の既存PASS_WITH_LIMITATIONSを保持し、新分解の較正PASSには読み替えない。
- Claude3者比較：`004bcb217c81879c2b13e2c11fab85376a1a8893`。
- SQ成長診断：`4453f5300e1a6e2320b45c30d4e3767ed9e8b74e`。共通成長・リスク・人口経路を再診断しない。

既存コードを変更せず、SQ・N3国内移転候補・法人なし・フラット税なし・年金なし・MPC0.5/0.9・KPI高閾値の8ケース×30年を隔離再実行した。実行フィルタ以外の入力は原本と同一。最終マクロ式の局所変数、VAT/企業/保険者・年金勘定をトレースし、税・家計・C/I/K・GDP・財政接続を別の診断式で再計算した。Fは固定参照で、再実行していない。

## 税の生成源

{tx}

VATはこの政策税列に含まれず、別の直接税チャネルで一回だけ加算される。年金拠出や給付、医療保険料は政策税へ勝手に加算せず、別の家計/保険者/基金勘定で扱う。

### 人数・基礎・年次連動

世帯数は総人口÷2.22。2035年53.086371百万世帯、2055年47.141073百万世帯。所得階級の29セルを正規化したシェアで配分し、各セルの所得代表値に初期1.04倍、共通物価指数、前年実行賃金/SQ賃金比を掛ける。シェア総和1・世帯数・円→兆円換算を再検査した。セルの本数は `N3_Tax_Base_Cell_Reconstruction.csv` のcell列を参照（所得階級・五分位の境界で同一所得の複数セルがある）。

2035年総所得基礎390.332163兆円、労働・事業基礎312.484949、金融基礎23.405315兆円。2055年は512.003877、409.890654、30.701062兆円。フラット税・減免は2030年開始/3年移行、医療・年金は2033年開始/6年移行という既存候補を用いる。原文の移行期間内の一つの読みであり、正式な開始年として採用していない。各セルの年齢配賦から労働割合を非高齢側95%/高齢側20%、金融割合を5%/10%と仮定する。これらは原文の正式な配賦値ではなく合成仮定。

改革前税は五分位別の所得税支払世帯平均×支払世帯比率を同じ世帯数へ拡大し、労働/金融割合で配賦する。動的ケースでは改革後税だけでなく比較対象の旧税額も同じ前年賃金比で更新される。30%・20%を掛けるのは控除廃止を仮定した**総所得**で、課税所得や手取り所得ではない。改革前の割当て税額は別の調査平均から作られ、実際の個人ごとの税源と控除を再現するモデルではない。

2055年労働税は旧20.466128→新122.967196兆円。2035年以降の大きさは約5%相当の旧税と30%総額課税の差に支配される。`N3_Policy_Burden_Sensitivity.csv` に、改革前後を同じ比率で縮小/拡大する税源曝露0.8/1/1.2、労働税率25/30/35%の固定入力診断を収録。これらは政策提案・採用・既存係数変更ではなく数式上の感度で、GDP効果は未計算・空欄。

法人利益は固定SQ名目GDPの10%という候補基礎に前年GDP比を掛ける。旧率30%、新20%または配当60%以上かつ投資20%以上を満たす企業セル16%。旧30%・利益比・応答率・投資分母は未較正/未裁定であり、現実の法人税全体を再現しない。追加配当には20%金融税を一回課す。相続は申告納税対象の既存基礎23.3846兆円と税3.2446兆円を物価で投影し、40%との差額を計上。全相続財産・全控除廃止の網羅ではなく、贈与税との重複は合算していない。

### 税proxyの整合限界

2055年の診断税N3−SQは＋144.110059兆円。内訳はマクロ税feedback−21.033923、VAT直接差＋57.583201、政策税差＋108.138422、医療直接税差−0.577641兆円。プログラム上はこの4項を一回だけ足しており、VATや政策税の同一金額をさらに追加してはいない。

ただし80兆円アンカーのマクロ税と調査ベースの政策税差をつなぐ部分は、全国の税目・地方税・税源・個票が整合した制度モデルではない。しかも30%GDP上限はマクロ税にだけ適用され、直接差分加算後の2055年診断税はGDP比{b['diagnostic_tax_to_nominal_GDP_pct']:.3f}%、上限相当との差は{b['diagnostic_tax_above_macro_cap_trn']:.3f}兆円になる。これは上限の適用境界に関する構造/仕様問題であり、原文§9の上限を正式採用して修正する権限は今回ない。計算内の一回計上と、全国税源としての経済的整合を混同しない。

## 家計現金−153.778兆円

{table(hhrows)}

基金への既存拠出振替は、家計から二度目の保険料を徴収していない。年金給付減は保護対象外の65〜74歳候補の受給延期、基金給付は75歳以降の資産取崩し。国内運用益5.369144兆円は、家計の既存財産所得を基金へ帰属変更する未採用候補であり、新規GDPから直接引く項ではない。基金の資産286.067113兆円はストックで、当年家計所得へ足していない。

現物給付の70%は現金給付でなく家計支出の代替としてこの列に入っている。そのため「家計現金」は厳密な銀行口座入出金の集計ではなく、支出代替を含むモデルproxy。残り30%のサービス追加分には別のVA率が掛かる。個人/世帯・保険料減免対象・加入制度の完全共同分布、名目500万円閾値の長期的な対象変化も未較正。

### −153.778と−163.413の差

3者比較は `0.6×coreN + macro_cash + feedback − VAT価格便益` という定義をそろえた家計proxy。医療＋政策変化の列にはVATの価格/賃金帰着と前年GDPからの所得feedbackを含めていない。

差−9.634863兆円は、VAT賃金帰着のSQ差−2.206936、所得feedback差−7.440982、SQ側医療変化の除外＋0.013055兆円に分解できる。共通所得基礎差・旧年金/雇用差は0。VAT価格便益は比較定義で控除されるので、ここへ再度VAT価格負担を足さない。家計水準差と政策フロー差を同じものとして取り扱う説明は誤りとなる。

相手勘定は `N3_Household_Counterpart_Ledger.csv` に明記。税は政府、給与/現物は政府支出、減免は保険者、年金給付/拠出は公的制度と基金、運用益は国内家計/海外/追加VA候補を区別した。ただし国民経済全体の資金循環完全閉鎖を宣言するものではない。

## GDP差−47.631465兆円の実際の伝播

{gdptable}

消費目標は実際の家計フローにMPC0.72、国内比率0.8を掛け、名目→実質変換したものを調整する。ただし相続は専用MPC0.1、VAT数量は既存価格効果を置き換える、旧年金も専用消費額で置き換える、などの補正がある。一般MPCで一律に全フローへ効果を二重付与していない。

```text
Ctarget = 0.8 / coreD × [0.72×(家計フロー＋前年GDP所得feedback−旧社会給付)
          ＋旧給付の個別需要＋年金消費置換＋VAT数量置換＋相続MPC置換]
C_t = 0.4×C_(t−1) + 0.6×Ctarget_t
I_t = 0.4×I_(t−1) + 0.6×名目投資フロー/coreD
K_t = 0.95×K_(t−1) + I_t
supply_t = 0.1×0.95×K_(t−1)（教育追加はこのケース0）
```

同じ平滑化を各実現フローへ適用して線形に分けると、2055年消費差の主な内訳は、労働税−30.646945、金融税−1.441061、年金給付減−10.174233、運用益帰属−1.549960、前年GDP所得feedback−2.228856兆円。VAT価格・数量置換・賃金を合わせた寄与も別列に保存し、価格効果と数量の二重計上を避けた。これは**実現経路を記述する加法分解**であり、各政策を取り除いた際の総効果ではない。

フラット税なし・年金なし・MPC変更の既存単独感度は年次CSVに再利用し、選択8条件は実際に再実行して固定値と照合した。年次基礎・所得feedback・KPI等が相互に変わるため、単独アブレーション差を足して政策総効果にしない。例えばMPC0.5では2055年495.655504、0.9では469.410124兆円。負の純家計フローへ高いMPCを掛けるのでGDP低下が拡大する算術であり、係数の符号反転ミスではない。

政策増収が同年に家計へ還流する、政府の追加購入に変わる、分布別MPCで消費効果が変わる等の仕組みは、現状では十分に実装/較正されていない。増収を条件付き債務削減・資産へ振り向けてもマクロGDPへ戻らない構造が、この読みを左右する。

## 負の投資残余：既存説明の訂正

2045年の実際の名目投資フローは、法人税誘発＋2.839190、VAT−1.870769、その他0＝純＋0.968421兆円。雇主負担・年金雇主料・雇用補助の追加項はこの候補で0。旧Claude観察の「雇主コスト等で残余が負」という説明は、この実行値では支持されない。算術PASSや企業投資一回計上PASSを撤回するものではなく、**説明上の発生源をVAT帰着へ訂正**する。

VAT残余の内訳（兆円）は、通常家計標準税率−0.677266、食品−0.203180、非家計の通常取引−0.737923、医療−0.218191、教育−0.010910、家賃−0.021981、小規模等−0.001320。価格転嫁率0.8のため増税をすべて転嫁できず、企業/供給者側に残る負担へ投資応答率を掛けている。負の基礎資源を失った投資として計算しており、追加投資の二度加算ではない。各市場の実測転嫁・投資応答による較正は未完了。

企業現金約60.749兆円は、新しい企業資金勘定における2055年末ストック。税減額から配当・実現投資を引いた蓄積であり、全額をGDPへ追加していない。企業の使わない現金が消費・投資へ自動還流する仕組みもない。

## 接続不足・未裁定事項

**健康労働の未接続**：2055年の医療部品は健康労働減−3381.876人相当を計算する一方、N3の有効労働はSQと同じ。N3アダプタは雇用アンカーの労働だけを加え、健康労働列を追加していない。F側には健康労働の接続がある。`IMPLEMENTATION_MISMATCH` として記録し、修正は行わない。固定労働基礎だけへ仮接続した診断値は約−0.021237兆円で、実際のGDP差への寄与ではなく、−47.63兆円の主因でもない。臨床影響と労働変換係数自体の較正も別途未完了。

**年金帰属4候補**：国内移転基準に対し、2055年GDPはLEGACY/海外所得が＋1.596832、追加VAが＋4.466683兆円。LEGACYは源泉未配賦の対照、海外所得は国内生産へ直接加えず、追加VAは新規実サービスを仮定する反実仮想。動的賃金により拠出も変わり、基準候補の基金残高の4帰属間差は最大{extra['base_fund_asset_max_spread']:.6f}兆円。全新候補・全期間の最大差は{extra['fund_asset_max_spread']:.6f}兆円（{extra['fund_spread_case']['case']}・{extra['fund_spread_case']['year']}年）。「基金資産は帰属で同一」は動的基礎ケースには当てはまらない。採用判断なし。

**所得KPI**：2035年判定は2034/2033年の実行済み実質一人当たり所得proxy成長＋{extra['KPI_growth']:.6f}%。閾値0.175%なら非凍結、0.176%なら凍結となる近傍。原文は数値閾値を規定せず、経済目標・所得成長・ジニ指標も複数の書き方がある。原文の「凍結」と「ペース緩和」は同義ではない。実装は2035年後の税率を固定し、VAT2040年15%/20%へ分岐させる候補。閾値帯は既存の2035年観測を固定した診断で、正式閾値を採用していない。

## 条件付き財政

2055年の税差＋144.110059、歳出差−3.099275、既存利払の一次収支への再分類−0.002360から、政策一次収支差＋147.206974兆円。基準国地方PB−1.2に足すと候補PB＋146.006974兆円となる。

既存財政式と仮定を用いて再計算し、政策一次収支差の実現率1で債務ゼロ初年度{extra['first_zero_debt_year']}、2055年ゼロの損益分岐は実現率約{100*extra['fiscal_break_even_scale']:.3f}%。これは政策税だけを65%にした値ではなく、モデルの政策一次収支差全体を比例縮小する診断。国地方の公式基準、2041年以降名目据置、利率・資産運用・保険者補填仮定に依存する。

全国一般政府PB/債務・実発行/償還・外国人材の全費用は閉じておらず、財政からGDPへの新規feedbackもない。2047年債務ゼロや2055年黒字を、政策増収の実現や現実財政の自律の確証としない。

## 公的統計との限定照合

厚労省[令和8年版白書・資料編p.14](https://www.mhlw.go.jp/wp/hakusyo/kousei/26-2/dl/01.pdf)で、2025年調査/2024年所得の平均575.2万円を再確認し、入力値と一致した。所得階級の代表値から再集計した平均は574.176万円で、区間代表値化による小差がある。金融配賦は合成所得の約6.0%で、同資料の財産所得約2.8%とは定義・対象が同一でない。金融税の全税源として較正されたとは言えない。

財務省[2024年度一般会計決算](https://www.mof.go.jp/policy/budget/budger_workflow/account/fy2024/ke0711b.pdf)の所得税21.2、法人税17.9、消費税25.0兆円も桁と範囲の参考に再取得した。将来の合成世帯税と税目全体の実収入は、年度・個人/世帯・所得範囲・地方税・申告対象が違うため一致させていない。調査元の平均値の一致を全国課税基礎の妥当性PASSにはしない。

## 分類・検証・未完了

`N3_Diagnostic_Issue_Classification.csv` は次を分離する。

- `ARITHMETIC_CHECK_PASS`：今回対象とした税・現金・C/I/K・GDP・財政の再構成は一致。未検証の全コードに「誤りなし」とは拡大しない。
- `EXPLANATION_MISMATCH`：負の投資残余の旧説明をVATへ訂正。
- `IMPLEMENTATION_MISMATCH`：医療で計算した健康労働がN3マクロへ未接続。
- `UNCALIBRATED_ASSUMPTION`：世帯拡大・所得/年齢配賦・総額税率と旧税の対応・物価/賃金投影・MPC・投資応答。
- `UNDECIDED_POLICY_INTERPRETATION`：年金帰属、KPI閾値/指標/凍結方式、医療上限・保護コホート等。
- `STRUCTURAL_LIMITATION` / `NOT_IDENTIFIED`：全国税・財政の閉鎖、税収還流、共同分布、全金融税源、厳密な現金指標。

実装者の診断検査{result['checks']}件、失敗0。8ケース240ケース年を固定出力と照合し、税目別旧/新税、家計相手勘定、需要目標とチャネル別平滑化、資本・供給、GDP差残差、VAT投資内訳、国地方一次収支/債務を数値検査した。優先して検討すべき対象は税基礎の全国較正、健康労働未接続、税上限/税収還流の境界、KPIと帰属の未裁定であり、今回は修正を実装していない。新たなレビュー・承認工程も追加していない。

主要CSVと対応する式はこの報告と再現コードを参照。トレース原本・再計算表・ソース固定CommitとSHA-256・検査の誤差/未検証範囲は個別JSONに保存。固定資料のあるSPEチェックアウトで、標準ライブラリ＋gitにより次で再現できる。

```bash
python handoff/chatgpt-n3-policy-burden-diagnosis-20261122/N3_Policy_Burden_Diagnosis_Reproduce.py --outdir /workspace/scratch/n3-burden-reproduction
```

公的統計は取得済みの観測値とURLを保存し、再現計算ではその記録を用いる。現実の個票税源較正を再現するコードではない。全成果はDRAFT/NON-CANONICAL。政策・係数・共通エンジン・既存出力・承認状態、RP-023/M19–25 HOLD、RP-024 PENDINGを変更していない。
'''
 (out/'SPE_N3_Policy_Burden_Diagnosis_Report_DRAFT_20261122.md').write_text(text)
 # No mutable logs or self-hash. Runtime full outputs are reproducible; final trace/bridges are originals.
 names=[f for f in sorted(out.iterdir()) if f.is_file() and f.name not in ['N3_Policy_Burden_Diagnosis_Verification.json','Execution.log']]
 result['artifacts']=[dict(path=f.name,size=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in names]
 (out/'N3_Policy_Burden_Diagnosis_Verification.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--outdir',type=Path,required=True);p.add_argument('--draft',type=Path);a=p.parse_args();run(a.root.resolve(),a.outdir.resolve(),(a.draft or a.outdir/'fixed-draft-source').resolve())
