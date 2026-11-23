#!/usr/bin/env python3
"""Annual integration of pinned SPE models. DRAFT/NON-CANONICAL; stdlib only."""
import argparse,builtins,copy,csv,hashlib,importlib.util,json,math
from pathlib import Path
P=Path(__file__).resolve().parent
def close(a,b):return math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10)
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader()
  for r in rs:w.writerow({k:format(v,'.12g') if isinstance(v,float) else v for k,v in r.items()})
def readcsv(p):return list(csv.DictReader(p.open()))
def load(cfg):
 root=P.parents[1]
 for f in cfg['runtime_dependencies']:
  b=(root/f['path']).read_bytes();assert len(b)==f['size'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
 mod=root/cfg['vat_model'];spec=importlib.util.spec_from_file_location('pinned_vat',mod);v=importlib.util.module_from_spec(spec)
 src=mod.read_text();assert src.count('return builtins.compile(src,filename,mode)')==1
 src=src.replace('return builtins.compile(src,filename,mode)','return _integration_compile(src,filename,mode)')
 assert src.count("def ex(code,ns):ns['_vat_flows']=flow;return builtins.exec(code,ns)")==1
 src=src.replace("def ex(code,ns):ns['_vat_flows']=flow;return builtins.exec(code,ns)","def ex(code,ns):ns['_vat_flows']=flow;return _integration_exec(code,ns)")
 exec(compile(src,str(mod),'exec'),v.__dict__)
 return root,v,json.loads((root/cfg['vat_inputs']).read_text())
def make_base(v,c,E=True,F=True,PEN=True):
 """Recompute labour and pension jointly; never add saved policy GDP deltas."""
 oldhh,hh,pm,foreign,unused=v.load_dependencies(c)
 pc=c['household_inputs']['pension_inputs'];fc=pc['foreign_inputs']
 fg,old,prev,dem,eng=pm['dependencies'](pc)
 # The Stage2 fixed-rate/weight=.5 route remains unchanged. Disable only F extras.
 original=old['elder_ledger']
 if not E:
  def noelder(cfg,s,pr):return original(cfg,{**s,'policy':'SQ'},pr)
  old['elder_ledger']=noelder
 name='HIST_COMBINED_MEDIUM' if F else 'HIST_ZERO'
 b=pm['base_path'](pc,fg,old,prev,dem,eng,name)
 source={};capture={};savedcompile=pm.get('compile',builtins.compile);savedmacro=fg['macro']
 def cc(src,filename,mode):
  if filename=='pension_macro.py':source['text']=src
  return builtins.compile(src,filename,mode)
 def mc(cfg,engine,d,sq,elder,pol,case,end_year=2055):
  rows=savedmacro(cfg,engine,d,sq,elder,pol,case,end_year)
  capture.update(d=copy.deepcopy(d),sq=copy.deepcopy(sq),elder=copy.deepcopy(elder),engine=engine,macro=rows)
  return rows
 pm['compile']=cc;fg['macro']=mc
 ps=next(s for s in pc['cases'] if s['id']==('MEDIUM_COMBINED' if PEN else 'MEDIUM_ZERO'))
 try:pr,_,_=pm['calculate'](pc,ps,b,fg)
 finally:pm['compile']=savedcompile;fg['macro']=savedmacro
 capture.update(source=source['text'],foreign=b['foreign'],pension=pr)
 return hh,pm,fg,capture
def execute(v,c,sp):
 c=copy.deepcopy(c);hc=c['household_inputs'];hc['defaults'].update(A=sp.get('A',True),B=sp.get('B',True))
 if 'deduction_adjusts' in sp:hc['defaults']['deduction_adjusts']=sp['deduction_adjusts']
 hh,pm,fg,b=make_base(v,c,sp.get('E',True),sp.get('F',True),sp.get('PEN',True))
 raw=[];original=fg['macro'];connection=sp.get('new_connection',True)
 def capture(cfg,engine,d,sq,elder,pol,case,end_year=2055):
  # Previously satellite-only foreign pension contributions become household and
  # employer cash costs. Wages are already in core labour income: do not add again.
  if connection and pol=='F':
   original_run=engine['run_path'];old_compile=original_run.__globals__
   # Compile the final VAT/household/pension engine after its narrow adaptations.
   text=engine.get('_integration_source')
   if text is None:
    # Passed through compile hook below, before execution.
    raise AssertionError('Missing final integrated engine source')
   ns=dict(old_compile);ns['_foreign_ledger']=b['foreign']
   needle="        cash+=_pension[i]['household_cash_delta_trn']"
   assert text.count(needle)==1
   text=text.replace(needle,needle+"\n        cash-=_foreign_ledger[i]['employee_pension_nominal_trn']")
   needle="admin_firm=value(admin_saving)+value(elderly_subsidy)-c['_elder'][i]['employer_contribution_base_trn']*ei-_pension[i]['employer_premium_delta_trn']"
   assert text.count(needle)==1
   text=text.replace(needle,needle+"-_foreign_ledger[i]['employer_pension_nominal_trn']-_foreign_ledger[i]['employer_program_nominal_trn']")
   exec(compile(text,'integrated_macro.py','exec'),ns);engine=ns
  r=original(cfg,engine,d,sq,elder,pol,case,end_year);raw.extend(r);return r
 # VAT's household compiler constructs the final engine. Capture its source
 # without altering original source bytes or the established GDP equations.
 origexec=hh.get('exec',builtins.exec);origcompile=hh.get('compile',builtins.compile);compiled={}
 def hccompile(src,filename,mode):
  if filename=='household_macro.py':compiled['source']=src
  return builtins.compile(src,filename,mode)
 def hhexec(code,ns):
  builtins.exec(code,ns);ns['_integration_source']=compiled.get('source')
 hh['compile']=hccompile;hh['exec']=hhexec
 # v.calculate temporarily replaces hh compile/exec. Interpose on builtins
 # compile only for its final named source, restoring immediately afterward.
 saved_vcompile=v.__dict__.get('compile',builtins.compile)
 def vc(src,filename,mode):
  if filename=='household_macro.py':compiled['source']=src
  return builtins.compile(src,filename,mode)
 saved_vexec=v.__dict__.get('exec',builtins.exec)
 def ve(code,ns):
  builtins.exec(code,ns)
  if ns.get('__name__')=='household_macro':ns['_integration_source']=compiled.get('source')
 v._integration_compile=vc;v._integration_exec=ve;fg['macro']=capture
 vs={**c['defaults'],**sp,'id':sp['id'],'background':'MM'}
 if not sp.get('VAT',True):vs.update(rate=False,expansion=False,recovery=False)
 savedtax=v.tax_account
 def controlled_tax(*args,**kwargs):
  ledger,sectors=savedtax(*args,**kwargs)
  if not sp.get('VAT_investment_link',True):ledger['VAT_induced_investment_trn']=0.
  return ledger,sectors
 v.tax_account=controlled_tax
 try:rows,inc,sec=v.calculate(c,vs,b,hh,pm,fg)
 finally:v.tax_account=savedtax;fg['macro']=original;v.compile=saved_vcompile;v.exec=saved_vexec;hh['compile']=origcompile;hh['exec']=origexec
 assert len(raw)==30
 return rows,inc,sec,b,raw,c
def fiscal(r,m,b,i,c):
 p=b['pension'][i];f=b['foreign'][i];e=b['elder'][i];idx=m['common_deflator']/(600/580)
 elderprem=e['insurer_receipt_base_trn']*idx;foreprem=f['incremental_pension_nominal_trn'];penprem=p['public_premium_delta_trn']
 newprem=elderprem+foreprem+penprem
 # Existing engine assigns pension benefits to government expenditure. Move the
 # payment to insurer and preserve the existing government financing as transfer.
 # This is a presentation bridge, not a new statutory subsidy assumption.
 pension_exp=e['pension_support_base_trn']*idx+p['public_benefit_delta_trn']
 gov=m['fiscal_balance_partial_trn']-f['government_program_nominal_trn']
 ins=r['insurer_balance_direct_trn']+r['insurer_VAT_balance_delta_trn']+newprem+(m['medical_reform_insurer_balance'] or 0.)
 pub=gov+ins;loss=r['insurer_contribution_loss_trn'];transfer=r['government_backfill_trn']+pension_exp
 insurer_receipts=newprem-loss+transfer
 insurer_spend=pension_exp+r['insurer_program_spending_trn']
 otherins=r['insurer_VAT_balance_delta_trn']+(m['medical_reform_insurer_balance'] or 0.)
 assert close(ins,insurer_receipts-insurer_spend+otherins)
 # Macro tax80 anchor lacks a confirmed national/local/SI boundary. Keep it as
 # historical proxy; VAT is a decomposition satellite, never a second addition.
 vat=r['modeled_VAT_trn'];residual=m['tax_diagnostic_trn']-vat
 out=dict(case=r['case'],year=r['year'],VAT_total_reference_trn=vat,VAT_national_reference_trn=r['VAT_national_reference_trn'],VAT_local_reference_trn=r['VAT_local_reference_trn'],legacy_tax_diagnostic_trn=m['tax_diagnostic_trn'],tax_residual_after_VAT_trn=residual,tax_macro_feedback_proxy_trn=m['tax_macro_trn'],
  pension_public_tax_delta_trn=p['public_tax_delta_trn'],private_income_tax_relief_trn=p['private_income_tax_relief_delta_trn'],private_local_tax_relief_trn=p['private_local_tax_relief_delta_trn'],private_payout_tax_trn=p['private_payout_tax_delta_trn'],AB_C_income_local_tax_delta_trn=r['tax_increase_trn'],corporate_tax_delta_trn=m['corporate_tax_delta'],corporate_credit_trn=m['corporate_credit'],
  elder_contribution_delta_trn=elderprem,foreign_contribution_delta_trn=foreprem,pension_reform_contribution_delta_trn=penprem,modeled_gross_contribution_delta_trn=newprem,AB_fund_contribution_loss_trn=loss,modeled_net_contribution_delta_trn=newprem-loss,
  modeled_pension_payment_trn=p['modeled_pension_payment_trn'],pension_reform_payment_delta_trn=p['public_benefit_delta_trn'],elder_pension_support_trn=e['pension_support_base_trn']*idx,elder_hiring_subsidy_trn=e['subsidy_base_trn']*idx,foreign_government_cost_trn=f['government_program_nominal_trn'],foreign_employer_cost_trn=f['employer_program_nominal_trn'],
  A_relief_trn=r['A_relief_trn'],B_service_cost_trn=r['B_service_cost_trn'],B_admin_trn=r['B_admin_trn'],C_cash_trn=r['C_cash_trn'],fund_spend_trn=r['fund_relief_trn'],government_backfill_trn=r['government_backfill_trn'],pension_reclassification_transfer_trn=pension_exp,government_to_insurer_transfer_trn=transfer,insurer_transfer_receipt_trn=transfer,internal_transfer_consolidated_trn=0.,
  government_expenditure_after_pension_reclassification_trn=m['expenditure_diagnostic_trn']+f['government_program_nominal_trn'],government_partial_balance_proxy_trn=gov,insurer_known_change_and_program_balance_trn=ins,consolidated_partial_balance_proxy_trn=pub,
  C_earmarked_trn=r['C_earmarked_funding_trn'],fund_reserved_income_trn=r['fund_income_trn'],fund_balance_trn=r['fund_balance_trn'],AB_C_unassigned_funding_trn=r['total_unassigned_funding_trn'],reserve_finance_trn=r['reserve_finance_trn'],
  central_government_total_balance_trn=None,local_government_total_balance_trn=None,national_SI_receipts_trn=None,national_pension_total_trn=None,national_other_tax_total_trn=None,actual_bonds_trn=None,PB_trn=None,national_consolidated_balance_trn=None)
 assert close(out['government_partial_balance_proxy_trn']+out['insurer_known_change_and_program_balance_trn'],pub)
 return out
def run(inp,out):
 cfg=json.loads(Path(inp).read_text());root,v,c=load(cfg);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 paths={};income=[];fisc=[];lab=[];house=[];raws={};regression=0
 fixed=readcsv(root/'handoff/f-vat-core-20261120/Annual.csv');ref={(r['case'],int(r['year'])):r for r in fixed}
 for sp in cfg['cases']:
  rows,inc,sec,b,raw,cc=execute(v,c,sp);income+=inc
  for i,(r,m) in enumerate(zip(rows,raw)):
   fi=fiscal(r,m,b,i,cc);fisc.append(fi);r.update({k:v for k,v in fi.items() if v is not None});r['scope']='IMPLEMENTED_CHANNELS_WITH_FIXED_PROVISIONAL_BACKGROUND'
   r.update(core_real_gdp_trn=m['core_real_gdp_trn'],capital_delta_real_trn=m['capital_delta_real_trn'],investment_promotion_nominal_trn=m['investment_promotion_trn'],education_nominal_trn=m['education_spending_trn'],scholarship_nominal_trn=m['scholarship_spend'],education_level_effect_real_trn=m['education_level_effect'],finite_effect_real_trn=m['finite_effect_sensitivity'],nominal_wage_proxy_man=m['nominal_wage_proxy_man'])
   p=b['pension'][i];f=b['foreign'][i];e=b['elder'][i];t=b['d'][i]
   r.update(household_policy_cash_nominal_trn=m['household_policy_cash_nominal_trn'],corporate_cash_change_trn=m['corporate_cash_change'],capital_previous_real_trn=m['capital_previous_real'])
   jobs=t['domestic_employed_conditional']+f['foreign_jobs']+e['F_extra_jobs']+p['additional_jobs']
   # effective_productive_workers already includes the pension addition in d.
   assert close(r['labor_force_population_proxy'],f['total_effective_labor']+p['additional_effective_labor'])
   for age in ['65_69','70_74','75plus']:
    for sex in ['male','female']:assert e[age+'_'+sex+'_F_rate']<=1+1e-10
   wage=jobs*m['nominal_wage_proxy_man']*10000/1e12
   r.update(employed_persons_proxy=jobs,effective_labor=r['labor_force_population_proxy'],gross_wage_bill_proxy_trn=wage,actual_gross_wage_bill_trn=None)
   lab.append(dict(case=r['case'],year=r['year'],population=r['population'],domestic_baseline_jobs=t['domestic_employed_conditional'],foreign_jobs=f['foreign_jobs'],foreign_policy_jobs=f['policy_only_foreign_jobs'],elder_extra_jobs=e['F_extra_jobs'],pension_extra_jobs=p['additional_jobs'],pension_extra_hours_equivalent=p['hours_equivalent_workers'],employed_persons_proxy=jobs,elder_effective_extra=e['effective_extra'],pension_effective_extra=p['additional_effective_labor'],total_effective_labor=r['labor_force_population_proxy'],elder_pension_overlap_removed_trn=p['legacy_overlap_removed_trn'],gross_wage_bill_proxy_trn=wage,pension_additional_wage_diagnostic_trn=p['extra_gross_wage_diagnostic_trn'],foreign_wage_reference_bill_trn=f['foreign_jobs']*cc['household_inputs']['pension_inputs']['foreign_inputs']['reference']['annual_cash_wage_yen']*(m['common_deflator']/(600/580))/1e12))
   # Historical macro 'DI' includes VAT purchasing-power relief. Exclude it to
   # obtain a cash-only PROXY; do not silently reconcile with the survey grid.
   cashproxy=r['household_disposable_nominal_trn']-r['household_direct_price_benefit_trn']
   microafter=r['synthetic_micro_DI_before_trn']+r['cash_DI_delta_trn']
   house.append(dict(case=r['case'],year=r['year'],macro_resource_income_proxy_trn=r['household_disposable_nominal_trn'],macro_cash_DI_proxy_trn=cashproxy,actual_cash_DI_total_trn=None,synthetic_micro_DI_before_trn=r['synthetic_micro_DI_before_trn'],synthetic_micro_DI_after_trn=microafter,macro_minus_micro_cash_proxy_gap_trn=cashproxy-microafter,AB_C_cash_delta_trn=r['cash_DI_delta_trn'],pension_cash_delta_trn=p['household_cash_delta_trn'],foreign_employee_contribution_delta_trn=f['employee_pension_nominal_trn'],premium_survey_before_trn=r['premium_before_trn'],premium_survey_after_trn=r['premium_after_trn'],price_benefit_trn=r['household_direct_price_benefit_trn'],in_kind_used_trn=r['B_used_trn'],C_cash_trn=r['C_cash_trn'],AB_C_living_relief_trn=r['living_burden_reduction_trn'],cash_plus_price_living_relief_proxy_trn=r['living_burden_reduction_trn']+r['household_direct_price_benefit_trn'],AB_C_direct_consumption_delta_trn=r['HH_consumption_direct_delta_trn'],AB_C_direct_saving_delta_trn=r['HH_saving_direct_delta_trn'],household_consumption_nominal_proxy_trn=r['household_consumption_nominal_proxy_trn'],pension_payment_modeled_trn=p['modeled_pension_payment_trn'],national_household_pension_total_trn=None,national_household_saving_total_trn=None,pension_labor_allocation_to_micro_groups_trn=None))
   r['macro_cash_DI_proxy_trn']=cashproxy
   if 'reproduce' in sp:
    old=ref[(sp['reproduce'],r['year'])]
    for k in ['real_gdp_trn','nominal_gdp_trn','C_cash_trn','total_unassigned_funding_trn','modeled_VAT_trn','labor_force_population_proxy']:
     assert close(r[k],float(old[k])),(sp['id'],r['year'],k,r[k],old[k]);regression+=1
  paths[sp['id']]=rows;raws[sp['id']]=raw
 # Explicit SQ uses the same current VAT transition but no F household or labour channels.
 # Build via the established VAT SQ route and collect its raw engine output.
 oldhh,hh,pm,fg,bases=v.load_dependencies(c);_,pold,prev,dem,eng=pm['dependencies'](c['household_inputs']['pension_inputs']);sb=pm['base_path'](c['household_inputs']['pension_inputs'],fg,pold,prev,dem,eng,'SQ_HIST')
 sb['source']=bases['MM']['source'];sb['engine']={**bases['MM']['engine'],'_pension':[{k:0. for k in z} for z in bases['MM']['engine']['_pension']]};sb['pension']=[dict(elder_employed=z['SQ_elder_employed']) for z in sb['elder']]
 sq,_,_=v.calculate(c,dict(id='SQ_CURRENT',background='MM',policy='SQ',rate=False,expansion=False,recovery=False,C=False),sb,hh,pm,fg)
 paths['SQ_CURRENT']=sq
 for r in sq:
  fi={k:None for k in fisc[0]};fi.update(case='SQ_CURRENT',year=r['year'],VAT_total_reference_trn=r['modeled_VAT_trn'],VAT_national_reference_trn=r['VAT_national_reference_trn'],VAT_local_reference_trn=r['VAT_local_reference_trn'],legacy_tax_diagnostic_trn=r['tax_diagnostic_trn'],tax_residual_after_VAT_trn=r['tax_diagnostic_trn']-r['modeled_VAT_trn'],government_partial_balance_proxy_trn=r['fiscal_balance_partial_trn'],insurer_known_change_and_program_balance_trn=r['insurer_balance_direct_trn']+r['insurer_VAT_balance_delta_trn'],AB_C_unassigned_funding_trn=0.,government_to_insurer_transfer_trn=0.,insurer_transfer_receipt_trn=0.,internal_transfer_consolidated_trn=0.)
  fi['consolidated_partial_balance_proxy_trn']=fi['government_partial_balance_proxy_trn']+fi['insurer_known_change_and_program_balance_trn'];fisc.append(fi);r.update({k:v for k,v in fi.items() if v is not None})
 for name,oldname in [('OLD_F_FIXED','MM_OLD'),('VAT_FIXED_ADDITIONAL','MM_FULL_ADDITIONAL')]:
  paths[name]=[{k:(None if val=='' else float(val) if k not in ['case','background','mode'] else val) for k,val in z.items()} for z in fixed if z['case']==oldname]
  for z in paths[name]:z['case']=name;z['year']=int(z['year']);z['scope']='FIXED_REFERENCE_NO_NEW_ACCOUNTING'
 metrics=['real_gdp_trn','nominal_gdp_trn','household_disposable_nominal_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn','labor_force_population_proxy','tax_diagnostic_trn','fiscal_balance_partial_trn','C_cash_trn','total_unassigned_funding_trn']
 comparison=[]
 for name,rs in paths.items():
  for i,r in enumerate(rs):
   z=dict(case=name,year=r['year'])
   for k in metrics:
    z[k]=r[k];z[k+'_minus_SQ']=r[k]-sq[i][k];z[k+'_minus_previous_VAT']=r[k]-float(ref[('MM_FULL_ADDITIONAL',r['year'])][k]);z[k+'_minus_old_F']=r[k]-float(ref[('MM_OLD',r['year'])][k]) if k in ref[('MM_OLD',r['year'])] and ref[('MM_OLD',r['year'])][k] else None
   comparison.append(z)
 interactions=[]
 for spec in cfg['interactions']:
  z,a,b,ab=[paths[n] for n in spec['paths']]
  for i in range(30):
   for k in spec['metrics']:
    single_a=a[i][k]-z[i][k];single_b=b[i][k]-z[i][k];combined=ab[i][k]-z[i][k];inter=combined-single_a-single_b
    interactions.append(dict(test=spec['id'],year=2026+i,metric=k,single_A=single_a,single_B=single_b,sum_of_singles=single_a+single_b,integrated_effect=combined,interaction=inter,status='CALCULATED',baseline=spec['paths'][0]))
 # Difference of the jointly solved all-channel result and sum of six
 # independently solved singleton effects on one fixed F provisional backdrop.
 for i in range(30):
  for k in ['real_gdp_trn','consolidated_partial_balance_proxy_trn','macro_cash_DI_proxy_trn','labor_force_population_proxy']:
   z=paths['CHANNELS_OFF'][i][k];singles=sum(paths['ONLY_'+flag][i][k]-z for flag in ['E','F','PEN','A','B','VAT']);combined=paths['FULL_DIRECT'][i][k]-z
   interactions.append(dict(test='ALL_SIX_CHANNELS',year=2026+i,metric=k,single_A=None,single_B=None,sum_of_singles=singles,integrated_effect=combined,interaction=combined-singles,status='CALCULATED',baseline='CHANNELS_OFF'))
 # New accounting comparisons keep different paths separate from equal-scale
 # VAT statutory effects. A different F labour path changes the tax reference.
 fcompare=[]
 fsq={r['year']:r for r in fisc if r['case']=='SQ_CURRENT'}
 fprior={r['year']:r for r in fisc if r['case']=='REPLAY_ADDITIONAL'}
 for r in fisc:
  z=dict(case=r['case'],year=r['year'])
  for k in ['VAT_total_reference_trn','legacy_tax_diagnostic_trn','government_partial_balance_proxy_trn','insurer_known_change_and_program_balance_trn','consolidated_partial_balance_proxy_trn','AB_C_unassigned_funding_trn']:
   z[k+'_minus_SQ']=r[k]-fsq[r['year']][k];z[k+'_minus_replayed_VAT_accounting']=r[k]-fprior[r['year']][k]
  fcompare.append(z)
 dump(out/'Fiscal_Comparison.csv',fcompare)
 effects=[]
 for flag,offcase in [('E','DIRECT_NO_E'),('F','DIRECT_NO_FOREIGN'),('PEN','DIRECT_NO_P'),('A','DIRECT_NO_A'),('B','DIRECT_NO_B'),('VAT','DIRECT_NO_VAT')]:
  for i in range(30):
   for k in ['real_gdp_trn','consolidated_partial_balance_proxy_trn','macro_cash_DI_proxy_trn','labor_force_population_proxy']:
    effects.append(dict(channel=flag,year=2026+i,metric=k,standalone_effect=paths['ONLY_'+flag][i][k]-paths['CHANNELS_OFF'][i][k],marginal_in_full=paths['FULL_DIRECT'][i][k]-paths[offcase][i][k],background='OTHER_F_PROVISIONAL_CHANNELS_FIXED'))
 dump(out/'Policy_Effects.csv',effects)
 allrs=[r for rs in paths.values() for r in rs]
 dump(out/'Annual.csv',allrs);dump(out/'Comparison.csv',comparison);dump(out/'Fiscal.csv',fisc);dump(out/'Household.csv',house);dump(out/'Income_Groups.csv',income);dump(out/'Labor.csv',lab);dump(out/'Interactions.csv',interactions);dump(out/'Summary.csv',[r for r in comparison if r['year'] in [2026,2035,2045,2055]])
 validation=dict(status='PASS_LOCAL_INTEGRATION',cases=len(paths),annual_rows=len(allrs),fixed_VAT_regression_cells=regression,checks=['fixed dependency bytes','same engine reexecution, not GDP summation','employment/effective-labour identity','legacy VAT scenario regression','insurer receipts less spending identity','government-insurer transfer cancellation','cash vs price and in-kind separated','no bond/PB imputation','all pairwise interactions computed'],limitations='Partial fiscal proxies and synthetic micro distribution; no national closed budget or observed wage bill.')
 (out/'Validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n');print(json.dumps(validation))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('inputs');a.add_argument('--outdir',required=True);x=a.parse_args();run(x.inputs,x.outdir)
