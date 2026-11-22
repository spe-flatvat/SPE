#!/usr/bin/env python3
import argparse,csv,hashlib,importlib.util,json,math,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
PIN='2e2670bacdeb83ff12de13add733d9fb7a4f8b54';REQ='3cf17fdbbbb44f92899d2897c9e98870d57f8e96'
PREV='handoff/chatgpt-n3-assumptions-specification-calibration-separation-20261123'
COMP='handoff/chatgpt-n3-native-policy-completion-20261123'
BD='handoff/chatgpt-n3-policy-burden-diagnosis-20261122'
SEP='handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123'
SIM=SEP+'/Resolved_Separation_Runtime.py.txt'
BASE='handoff/chatgpt-n3-model-expansion-20261121/N3_Components.py'
GAP='handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Components.py'
PAR='handoff/chatgpt-n3-f-parity-implementation-20261122/Components.py'
TR='handoff/chatgpt-n3-transition-financing-full-dynamics-20261122/N3_Transition_Reproduce.py'
METRICS=['real_GDP_trn','nominal_GDP_trn','GDP_minus_SQ_trn','total_tax_diagnostic_proxy_trn','household_resource_DI_proxy_trn','consumption_real_trn','private_investment_real_trn','CL_PB_candidate_trn','CL_interest_candidate_trn','CL_assets_candidate_trn','CL_debt_candidate_trn']
TERMS=['GDP_core_difference_trn','GDP_C_difference_trn','GDP_I_difference_trn','GDP_G_domestic_trn','GDP_supply_difference_trn','GDP_other_difference_trn','GDP_unmet_difference_trn']
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def rd(p):return list(csv.DictReader(p.open()))
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def code_ref(root,p,token):return p+':'+','.join(str(i+1) for i,l in enumerate((root/p).read_text().splitlines()) if token in l)+' token='+token

def run(root,out):
 out.mkdir(parents=True,exist_ok=True);R=module('attribution_runtime',HERE/'Attribution_Runtime.py');inputs=json.loads((HERE/'Counterfactual_Inputs.json').read_text())
 old=rd(root/PREV/'N3_Sensitivity_Annual_Comparison_2026_2055.csv');fixed={int(x['year']):x for x in old if x['case']=='BASE_REPLAY'}
 raw=[];mids=[];targets=[];fisc=[];cases=[];cache={};failures=[];count=0;decomp=[];events=[];cal=[];traces=[];originpaths=set()
 for definition in inputs['cases']:
  cid=definition['case'];r,s=R.build(root,out,definition);a,l,b=r.simulate(s)
  for x,lx in zip(a,l):
   y=x['year'];p=r.par;d=r.base[y]['coreD'];sq=r.sq[y];pre=cid+str(y)
   r.ck(pre+':GDP_component_sum_independent',x['real_GDP_trn']-sq['Y']-sum(x[k] for k in TERMS))
   # Actual nominal GDP formula has a pressure term, not blindly GDP*deflator.
   r.ck(pre+':nominal_formula',x['nominal_GDP_trn']-x['real_GDP_trn']*d*(1+p['price_pressure_coefficient']*x['unmet_demand_real_trn']/r.base[y]['coreY']))
   r.ck(pre+':GI_off',x['government_purchase_nominal_trn']+x['public_investment_nominal_trn'])
   r.ck(pre+':rates_unchanged',abs(x['policy_labor_rate']-.3)+abs(x['policy_financial_rate']-.2)+abs(x['policy_estate_rate']-.4)+abs(x['VAT_standard_rate']-float(fixed[y]['VAT_standard_rate']) if 'VAT_standard_rate' in fixed[y] else x['VAT_standard_rate']-r.vatrate[y]))
   for k in ['coreY','coreN','coreD','labor']:r.ck(pre+':shared_'+k,r.base[y][k]-sq[k])
   r.ck(pre+':same_population',r.base[y]['demography']['population']-sq['demography']['population'])
   r.ck(pre+':treasury_identity',lx['PB_trn']-lx['interest_trn']-lx['SFA_cash_need_trn']+lx['new_cash_borrowing_trn']-lx['cash_debt_redemption_trn']-lx['assets_end_trn']+lx['assets_begin_trn'])
   r.ck(pre+':firm_sources_uses',lx['firm_end_trn']-lx['firm_begin_trn']-lx['firm_source_tax_saving_trn']+lx['firm_dividend_trn']+lx['firm_original_investment_paid_trn']+lx['firm_additional_investment_paid_trn'])
   if cid=='BASE_REPLAY':
    for k in METRICS:r.ck(pre+':fixed_baseline_'+k,x[k]-float(fixed[y][k]),3e-6)
    comp=dict(year=y,N3_real_GDP_trn=x['real_GDP_trn'],SQ_real_GDP_trn=sq['Y'],GDP_gap_trn=x['GDP_minus_SQ_trn'],
      N3_nominal_GDP_trn=x['nominal_GDP_trn'],SQ_nominal_GDP_trn=sq['N'],common_deflator=d,
      N3_pressure_nominal_residual_trn=x['nominal_GDP_trn']-x['real_GDP_trn']*d,SQ_pressure_nominal_residual_trn=sq['N']-sq['Y']*d,
      **{k:x[k] for k in TERMS},GDP_identity_residual_trn=x['GDP_minus_SQ_trn']-sum(x[k] for k in TERMS),
      sum_realized_C_sources_trn=sum(t['filtered_C_state_real_trn'] for t in r.targets if t['year']==y),SQ_fixed_C_offset_trn=-sq['C'],
      N3_private_I_proxy=x['private_investment_real_trn'],SQ_private_I_proxy=x['SQ_private_investment_real_trn'],
      N3_desired_real_GDP_trn=x['desired_real_GDP_trn'],N3_supply_ceiling_real_trn=x['supply_ceiling_real_trn'],N3_unmet_real_trn=x['unmet_demand_real_trn'],SQ_unmet_real_trn=sq['unmet'],
      extra_G_nominal_trn=0.,extra_public_I_nominal_trn=0.,NX='unknown',total_G_final_consumption='unknown',
      interpretation='ACTUAL_ENGINE_COMPONENTS_PARTIAL_PROXY_NOT_NATIONAL_CIGNX_ACCOUNTS')
    r.ck(pre+':filtered_C_to_delta',comp['sum_realized_C_sources_trn']+comp['SQ_fixed_C_offset_trn']-x['GDP_C_difference_trn'])
    decomp.append(comp)
    # Shared event roster reconstructed read-only from pinned code/input.
    risks=dict(oil=p['oil_gdp_loss'] if y==2026 and p['apply_oil_to_initial'] else 0.,conflict=p['conflict_gdp_loss'] if y==2027 else 0.,quake=p['quake_gdp_loss'] if y==2031 else 0.,
      disaster=p['disaster_gdp_loss'] if y>=p['disaster_anchor'] and (y-p['disaster_anchor'])%3==0 else 0.,climate=p['climate_gdp_loss'] if y>=p['climate_anchor'] and (y-p['climate_anchor'])%2==0 else 0.)
    exkeys=['oil_gdp_loss','conflict_gdp_loss','quake_gdp_loss','disaster_gdp_loss','climate_gdp_loss','disaster_anchor','climate_anchor','apply_oil_to_initial','wage_shock_start','quake_tax_factor']
    trace=json.loads((root/BD/'N3_Unchanged_Execution_Trace.json').read_text());sqpar=trace['parameters']['SQ_COMMON_ON']
    for k in exkeys:r.ck(pre+':event_input_'+k,float(p[k])-float(sqpar[k]))
    events.append(dict(year=y,**{k+'_input_fraction':v for k,v in risks.items()},risk_sum=sum(risks.values()),stacked_distinct_events=';'.join(k for k,v in risks.items() if v),
      N3_core_real=r.base[y]['coreY'],SQ_core_real=sq['coreY'],core_difference=r.base[y]['coreY']-sq['coreY'],N3_population=r.base[y]['demography']['population'],SQ_population=sq['demography']['population'],
      N3_deflator=d,SQ_deflator=sq['coreD'],energy_logistics_metadata_pct=r.base[y]['macro_row']['energy_logistics_shock_pct'],
      source='handoff/chatgpt-n3-f-parity-implementation-20261122/Resolved_Macro_Source.py.txt:177-203',
      execution_note='fixed core already contains common risk; instrumented loop does not apply a second GDP shock; 2031 tax factor recalculated once within annual tax recurrence',
      review_candidate='2026 oilGDP disabled at initial anchor but energy metadata15 remains; common to N3/SQ, no edit' if y==2026 else 'overlap of different configured events, not established duplicate' if sum(v>0 for v in risks.values())>1 else 'NO_N3_SPECIFIC_EVENT_DIFFERENCE'))
   x.update(counterfactual_status=definition['type'],causal_scope='WITHIN_PARTIAL_MODEL_CONDITIONAL_NOT_REAL_WORLD_CAUSAL_ESTIMATE',
     common_population_persons=sq['demography']['population'],common_deflator=d,SQ_unchanged=True,extra_G_trn=0.,extra_public_I_trn=0.)
  if cid=='BASE_REPLAY':
   (out/'Resolved_Instrumented_Runtime.py.txt').write_text(r.resolved_runtime)
   baseline_runner=r
  cache[cid]=a;raw+=a;mids+=r.midpoints;targets+=r.targets;fisc+=l;count+=r.counter;failures+=r.checks
  cases.append(dict(case=cid,type=definition['type'],purpose=definition['purpose'],component_overrides=json.dumps(definition.get('component_spec',{})),runtime_overrides=json.dumps(definition.get('runtime',{})),macro_overrides=json.dumps(definition.get('macro_override',{})),GI='OFF',SQ='UNCHANGED',adoption='UNADOPTED_DIAGNOSTIC',independent_effects_additive=False))
  print(json.dumps(dict(case=cid,rows=len(a),checks=r.counter,failed=len(r.checks),GDPgap2030=a[4]['GDP_minus_SQ_trn'],GDPgap2055=a[-1]['GDP_minus_SQ_trn'])))
 base=cache['BASE_REPLAY'];bi={x['year']:x for x in base};summaries=[]
 for x in raw:
  for k in METRICS:x['difference_vs_N3_'+k]=x[k]-bi[x['year']][k]
 for cid,a in cache.items():
  below=[x['year'] for x in a if x['GDP_minus_SQ_trn']<-1e-7]
  for y in [2026,2029,2030,2035,2039,2055]:
   x=a[y-2026];summaries.append(dict(case=cid,year=y,SQ_below_years=len(below),first_below_year=min(below) if below else 'none',**{k:x[k] for k in METRICS},**{'difference_vs_N3_'+k:x[k]-bi[y][k] for k in METRICS}))
 # Matched 2x2 arithmetic identifies only the tax/pension interaction, leaving
 # the neither-block outcome minus fixed SQ as an explicit other-model remainder.
 interactions=[]
 def ck(name,error,tol=5e-7):
  nonlocal count
  count+=1
  if not math.isfinite(error) or abs(error)>tol:failures.append(dict(check=name,error=error,tolerance=tol))
 for i,y in enumerate(range(2026,2056)):
  B=cache['BASE_REPLAY'][i];NT=cache['NO_HH_FLAT_TAX'][i];NP=cache['NO_PENSION_BLOCK'][i];N=cache['NO_HH_TAX_OR_PENSION'][i]
  for k in METRICS:
   inter=B[k]-NT[k]-NP[k]+N[k];tax_first=NP[k]-N[k];pen_after=B[k]-NP[k];pen_first=NT[k]-N[k];tax_after=B[k]-NT[k]
   ck('matched_interaction:'+str(y)+k,B[k]-N[k]-tax_first-pen_first-inter)
   ck('orderA:'+str(y)+k,B[k]-N[k]-tax_first-pen_after);ck('orderB:'+str(y)+k,B[k]-N[k]-pen_first-tax_after)
   remainder=N[k]-B['SQ_real_GDP_trn'] if k=='real_GDP_trn' else 'unknown'
   if k=='real_GDP_trn':ck('gap_telescope:'+str(y),B['GDP_minus_SQ_trn']-remainder-tax_first-pen_first-inter)
   interactions.append(dict(year=y,metric=k,tax_effect_given_pension_off=tax_first,pension_effect_given_tax_off=pen_first,
    tax_effect_given_pension_on=tax_after,pension_effect_given_tax_on=pen_after,tax_pension_interaction=inter,
    neither_block_minus_SQ=remainder,total_joint_difference=B[k]-N[k],gap_closure_residual=0. if k!='real_GDP_trn' else B['GDP_minus_SQ_trn']-remainder-tax_first-pen_first-inter,
    interpretation='ORDER_DEPENDENT_MATCHED_MODEL_CONTRASTS; other OFF cases and prior sensitivity deltas must not be added'))
 # Exact current tax-cell reconstruction and limited calibration diagnostics.
 rr=baseline_runner;h=rr.ci['household'];mean=sum(z['share']*z['income_yen'] for z in h['income_cells']);stats=json.loads((root/BD/'Official_Statistics_Limited_Check.json').read_text())
 midbase={x['year']:x for x in mids if x['case']=='BASE_REPLAY'}
 for y in range(2026,2056):
  cells=[x for x in rr.baseline_cells if x['year']==y];m=midbase[y];idx=rr.ci['deflators'][y-2026]/rr.ci['deflators'][0];phase=m['phase_household'];oldlabor=oldfin=0.
  for cell in cells:
   original=h['income_cells'][cell['cell']];q=original['quintile'];old=h['stats']['income_tax_mean_paid_yen'][q]*h['stats']['income_tax_paid_per2000'][q]/2000*idx*m['lagged_wage_factor'];e=original['elder_share']
   oldlabor+=cell['households']*old*(.95*(1-e)+.20*e)/1e12;oldfin+=cell['households']*old*(.05*(1-e)+.10*e)/1e12
  lb=sum(z['labour_business_30_gross_base_trn'] for z in cells);fb=sum(z['financial20_gross_base_trn'] for z in cells)
  ld=phase*(.3*lb-oldlabor);fd=phase*(.2*fb-oldfin)
  ck('tax_cell_labour:'+str(y),ld-m['policy_labour_business_flat30_tax_delta_trn']);ck('tax_cell_finance:'+str(y),fd-m['policy_household_financial20_tax_delta_trn'])
  med=rr.medical_accounts[y-2026]
  pen=rr.live_component.pension[y-2026]
  cal.append(dict(year=y,labor_gross_proxy_trn=lb,financial_gross_proxy_trn=fb,allocated_baseline_labor_tax_before_phase_trn=oldlabor,allocated_baseline_financial_tax_before_phase_trn=oldfin,
   labor_flat_target_before_phase_trn=.3*lb,financial_flat_target_before_phase_trn=.2*fb,household_phase=phase,reconstructed_labor_wedge_trn=ld,reconstructed_financial_wedge_trn=fd,
   synthetic_cell_mean_reference_income_yen=mean,survey_mean_reference_income_yen=h['stats']['mean_income_yen'],synthetic_minus_survey_mean_yen=mean-h['stats']['mean_income_yen'],
   synthetic_to_survey_mean_ratio=mean/h['stats']['mean_income_yen'],income_scale=rr.ci['config']['income_scale'],lagged_wage_factor=m['lagged_wage_factor'],
   corporate_profit_base_proxy_trn=sum(z['profit_base_trn'] for z in rr.live_component.firms if z['year']==y),
   medical_baseline_patient_proxy_trn=med['baseline_patient_model_trn'],medical_patient_calibration_residual_trn=med['baseline_patient_calibration_residual_trn'],
   pension_delayed_recipients_proxy=pen['delayed_recipients_candidate'],pension_contribution_proxy_trn=pen['fund_contribution_trn'],
   national_tax_revenue_calibration_residual='unknown; different years/populations/tax scopes cannot be equated',real_world_GDP_effect_of_calibration_gap='unknown',
   evidence='fixed survey2025/income2024; current cells; pinned Official_Statistics_Limited_Check.json; candidate medical/fund ledgers',
   scope='DIAGNOSTIC_MISMATCHES_NOT_ALTERNATIVE_CALIBRATION_OR_EMPIRICAL_CAUSAL_EFFECT'))
 write(out/'Reused_Limited_Statistics_Check.json',stats)
 # Map realized transmission channels to policy, code, counterpart and limits.
 cmap={
 'labor_tax':('A_LABOR_TAX;A_ALLOWANCE',BASE,'target30','HH -> government','text30%, synthetic gross/source/oldtax bases'),
 'financial_tax':('A_FINANCIAL_TAX;A_ALLOWANCE',BASE,'target20','HH -> government','text20%, synthetic financial income bases'),
 'estate_tax':('A_ESTATE_GIFT',GAP,'estate_delta','HH -> government','reported subset; estate_MPC0.1; not all estates'),
 'corporate_dividend':('A_CORPORATE',BASE,'addedD','corporate -> HH after financial tax','profitbase10%, dividend40%, corporate eligibility and timing candidates'),
 'premium_relief':('B_RELIEF',BASE,'saved=','insurer -> HH','maximum35%, income2m-5m taper candidate'),
 'in_kind_expense_substitution':('B_IN_KIND',BASE,'.7*benefit','government -> service/HH expense replacement','30k/HH;70% expense replacement and complementary serviceVA'),
 'public_payroll':('C_EMPLOYMENT',BASE,'payroll=n','government -> existing HH employee','REGULARIZE100k wages3/4m; net-new0'),
 'pension_benefit':('B_PENSION',BASE,'pension_delta=-','public pension -> HH reduction','age75 original principle; coverage85%, cohort protection/ramp candidates'),
 'fund_payout':('B_PENSION',BASE,'fundpay','fund -> HH','candidate maturity and20yr payout'),
 'fund_domestic_return_debit':('B_PENSION',GAP,'debit=gain','HH property income -> pension fund','domestic transfer of2% return; not new GDP'),
 'semi_med_reserve':('B_MEDICAL',GAP,'reserve=claims','HH -> semi-med fund','reserve rate0; matched claim/premium reclassification'),
 'EITC_removal':('B_EITC',BASE,'oldeitc','unknown baseline entitlement','modeled removal0 != measured actual policy0'),
 'medical_household':('B_MEDICAL;B_EOL',TR,'medhh=','HH/patient/insurer/government/provider','claims/copay/medical-finance combined; common care retained'),
 'VAT_household':('A_VAT',TR,'vdt=','HH/producer/government','fixed original schedule; household incidence plus macro response'),
 'other_cash_unidentified':('UNIDENTIFIED',SIM,'cash=t','not assigned','arithmetic residual retained; do not label as policy'),
 'income_feedback':('MODEL_STRUCTURE',SIM,'feedback=','prior GDP gap -> HH resources -> C','income_feedback0.08;domestic0.8;MPC0.72;lambdaC0.6'),
 'quantity_volume':('A_VAT;MODEL_STRUCTURE',TR,'quantity=','VAT quantity -> C volume','elasticity0.25; price replacement prevents double counting'),
 'quantity_price_replacement':('A_VAT;MODEL_STRUCTURE',SIM,'Ctarget=','remove duplicate gross price effect from C target','must interpret with VAT HH incidence and volume, not independently'),
 'legacy_social':('SQ_COMMON_INPUT',SIM,'Ctarget=','fixed social baseline','weighted demand replacement, not extra policy'),
 'legacy_pension':('SQ_COMMON_INPUT',SIM,'Ctarget=','fixed legacy pension','weighted pension demand replacement; legacy satellite disabled')}
 for t in targets:
  if t['case']!='BASE_REPLAY':continue
  pid,path,token,actors,note=cmap[t['channel']]
  traces.append(dict(**t,policy_ids=pid,source_code=code_ref(root,path,token),GDP_code=code_ref(root,SIM,'Ctarget='),
   counterpart=actors,input_and_limit=note,step='nominal source -> domestic*MPC/deflator or specified volume adjustment -> lambdaC filtering -> desiredGDP -> min(capacity)',
   causal_interpretation='CONDITIONAL_REALIZED_TRAJECTORY_ACCOUNTING;not standalone ON/OFF or empirical policy effect'))
 # Retain 22 independent-axis cause rows; no invented numeric shares by gap type.
 gaprows=[];unidentified=[]
 offmap={'A_LABOR_TAX':'NO_HH_FLAT_TAX','A_FINANCIAL_TAX':'NO_HH_FLAT_TAX','A_ALLOWANCE':'NO_HH_FLAT_TAX','B_PENSION':'NO_PENSION_BLOCK','A_CORPORATE':'NO_CORPORATE_BLOCK','A_ESTATE_GIFT':'NO_ESTATE_BLOCK','B_RELIEF':'NO_RELIEF_INKIND_BLOCK','B_IN_KIND':'NO_RELIEF_INKIND_BLOCK','C_EMPLOYMENT':'NO_EMPLOYMENT_BLOCK'}
 for old in rd(root/PREV/'N3_22_Policy_Assumptions_And_Gaps.csv'):
  pid=old['policy_id'];channels=[k for k,v in cmap.items() if pid in v[0].split(';')];cf=offmap.get(pid,'NOT_IDENTIFIABLE_AS_INDEPENDENT_OFF_CASE')
  gaprows.append(dict(policy_id=pid,policy_spec_axis=old['policy_spec_status'],model_structure_axis=';'.join(channels) or 'STRUCTURAL_OR_UNIMPLEMENTED_NO_MONETARY_PATH',
   national_calibration_axis=old['calibration_status']+'; '+old['empirical_data_status'],SQ_common_input_axis='same fixed core/population/deflator/events; common EOL is shared' if pid=='B_EOL' else 'same fixed core/population/deflator/events',
   existing_implemented_effect_axis=cf,interaction_unidentified_axis='matched household-tax/pension interaction quantified; remaining interactions not exhaustively identified; empirical impact unknown',
   strict_GDP_amount_due_to_missing_spec='unknown',strict_GDP_amount_due_to_calibration='unknown',strict_GDP_amount_due_to_structure='unknown',
   implementation_note='no effect in selected model is not proof of zero real-world effect',evidence=old['evidence']))
  unidentified.append(dict(policy_id=pid,unidentified=old['policy_spec_status']+'; '+old['empirical_data_status']+'; '+old['accounting_status'],
   model_channel=';'.join(channels) or 'NO_UNIQUE_MONETARY_CHANNEL',GDP_loss_from_unimplemented_part='unknown',calibration_GDP_effect='unknown',
   executable_next=old['remaining_action'],required_external_data=old['empirical_data_status'],policy_choice_status=old['policy_spec_status'],
   owner_new_judgment_requested=False,formal_policy_or_SQ_edit=False))
 unidentified.append(dict(policy_id='OTHER_MODEL_AND_INTERACTIONS',unidentified='Neither household tax nor pension counterfactual is not SQ: other N3 effects and model state remain; 2x2 identifies no higher-order interactions with all other policies',
  model_channel='remainder explicitly reported, not allocated to missing policy/calibration',GDP_loss_from_unimplemented_part='unknown',calibration_GDP_effect='unknown',
  executable_next='trace remaining fixed VAT/medical/private-capital channels using existing ledgers; do not synthesize absent policies',owner_new_judgment_requested=False,formal_policy_or_SQ_edit=False))
 dump(out/'N3_SQ_Annual_GDP_Gap_Decomposition_2026_2055.csv',decomp);dump(out/'N3_GDP_Gap_Transmission_Trace.csv',traces);dump(out/'N3_GDP_Gap_Cause_Classification.csv',gaprows)
 dump(out/'N3_GDP_Gap_Counterfactual_Cases.csv',cases);dump(out/'N3_GDP_Gap_Counterfactual_Annual_2026_2055.csv',raw);dump(out/'N3_GDP_Gap_Counterfactual_Summary.csv',summaries)
 dump(out/'N3_GDP_Gap_Matched_Interaction_And_Order.csv',interactions);dump(out/'N3_GDP_Gap_Unidentified_And_Executable_Next.csv',unidentified)
 dump(out/'N3_GDP_Gap_All_Case_Intermediate_Accounts.csv',mids);dump(out/'N3_GDP_Gap_All_Case_C_Target_And_State.csv',targets);dump(out/'N3_GDP_Gap_Fiscal_Cash_Debt_Ledger.csv',fisc)
 dump(out/'N3_SQ_Shared_Events_And_Core_Check.csv',events);dump(out/'N3_GDP_Gap_Calibration_Diagnostics.csv',cal);dump(out/'N3_Baseline_Tax_Cells.csv',rr.baseline_cells)
 # Recheck only direct changed-path sources and fixed predecessor originals.
 paths=set(str(p.relative_to(root)) for p in (root/PREV).iterdir() if p.is_file())
 paths.update([SIM,BASE,GAP,PAR,TR,BD+'/N3_Unchanged_Execution_Trace.json',BD+'/Official_Statistics_Limited_Check.json',BD+'/N3_Policy_Burden_Diagnosis_Reproduce.py',
  'handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122/Component_Initialization.json',
  'handoff/chatgpt-n3-transition-financing-full-dynamics-20261122/Medical_Initialization.json',
  'handoff/chatgpt-n3-f-parity-implementation-20261122/Resolved_Macro_Source.py.txt','policies/New3linesPolicies.md',
  COMP+'/N3_Native_Completion_Annual_Comparison_2026_2055.csv',COMP+'/Verification.json'])
 receipts=[]
 for path in sorted(paths):
  b=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);assert b==(root/path).read_bytes(),path
  receipts.append(dict(commit=PIN,path=path,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True,retrieval='git fetch fixed commit / git show; earlier receipt for transitive originals reused'))
 request='handoff/chatgpt-n3-gdp-gap-causal-attribution-request-20261123/SPE_Work_N3_GDP_Gap_Attribution_Specification_Structure_Calibration_Request_20261123.md'
 b=subprocess.check_output(['git','show',REQ+':'+request],cwd=root);assert b==(root/request).read_bytes()
 receipts.append(dict(commit=REQ,path=request,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True,retrieval='connected GitHub fetch_file then git fixed commit bytes'))
 write(out/'Input_Source_Receipts.json',receipts)
 assert not subprocess.check_output(['git','diff','--name-only',REQ],cwd=root,text=True).strip()
 v=dict(status='PASS_GDP_GRAPH_AND_LIMITED_COUNTERFACTUAL_ATTRIBUTION' if not failures else 'FAIL',executed_cases=len(cases),executed_annual_rows=len(raw),
  checks=count,failed=len(failures),failures=failures,baseline_anchor2030=base[4]['GDP_minus_SQ_trn'],baseline_anchor2055=base[-1]['GDP_minus_SQ_trn'],
  SQ_below_years=sum(x['GDP_minus_SQ_trn']<-1e-7 for x in base),decomposition_rows=len(decomp),transmission_rows=len(traces),independent_cause_axis_rows=len(gaprows),
  max_GDP_identity_residual=max(abs(x['GDP_identity_residual_trn']) for x in decomp),max_other_cash_unidentified=max(abs(x['other_cash_unidentified']) for x in mids if x['case']=='BASE_REPLAY'),
  prior_PASS_reused=[32439,1754,5990],direct_source_files_checked=len(receipts),strict_spec_structure_calibration_partition_identified=False,
  SQ_shocks_modified=False,SQ_original_or_common_engine_modified=False,additional_GI=False,policy_adopted=False,remaining_empirical_policy_effects='unknown')
 write(out/'Verification.json',v);report(out,v,decomp,summaries,interactions,cal,mids)
 print(json.dumps(v));assert not failures,failures[:5]

def report(out,v,decomp,summaries,interactions,cal,mids):
 lines=['# N3対StatusQUO GDP差の発生源特定','DRAFT / NON-CANONICAL / ISOLATED MODEL DIAGNOSTIC / 2026-11-23',
 '## 結論',
 '現行N3が固定SQを下回る計算上の主経路は、合成課税基礎に対する給与・事業/金融課税の追加負担と、75歳年金移行・基金国内振替による家計資源減少が、消費状態へ伝播する経路。追加G/I OFFのため財政改善を追加需要へ戻す経路はない。投資・資本供給のプラスがあるが、消費差を相殺しない。この結論は現行の部分実装・構造・較正仮定に条件付くモデル内の説明であり、N3政策原文の最終効果や現実の因果効果ではない。',
 f"基準再現と限定対照を{v['executed_cases']}経路・{v['executed_annual_rows']}年次実行。新規チェック{v['checks']}件、失敗{v['failed']}。前回32,439件等のPASSを固定対象の範囲で再利用し、前回25感度枝を再実行/原因寄与へ転用していない。",
 '## GDPの実装式と算術分解',
 '`Y = min(coreY + capacity_absorption*supply + C_state + I_state + residual_private_I + education_nominal/d + education_level + finite + service_nominal/d + extra_G*domestic/d + extra_public_I_real, capacity)`。国民経済計算C/I/G/NXの完全恒等式ではなく、固定コアに代理需要・供給差を接続した式。NXや政府最終消費総額はunknown。名目GDPは`Y*d*(1+price_pressure*unmet/coreY)`。',
 '`Ctarget = domestic_share/d * [MPC*(cash + income_feedback - legacy_social_HH) + legacy_social_weighted + legacy_pension_weighted - MPC*legacy_pension_HH + quantity - MPC*replaced_price + (MPC-estate_MPC)*estate_tax]`。`C_state(t)=(1-lambdaC)*C_state(t-1)+lambdaC*Ctarget(t)`、初期年は状態0を維持。基準のdomestic_share0.8、MPC0.72、lambdaC0.6、所得還流係数0.08は既存仮定。',
 '|年|N3−SQ|消費状態差|投資差|資本供給吸収差|医療等その他差|コア差/G差/超過需要差|恒等式残差|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for y in [2026,2029,2030,2035,2039,2055]:
  z=decomp[y-2026];lines.append(f"|{y}|{z['GDP_gap_trn']:+.9f}|{z['GDP_C_difference_trn']:+.9f}|{z['GDP_I_difference_trn']:+.9f}|{z['GDP_supply_difference_trn']:+.9f}|{z['GDP_other_difference_trn']:+.9f}|{z['GDP_core_difference_trn']+z['GDP_G_domestic_trn']+z['GDP_unmet_difference_trn']:+.9f}|{z['GDP_identity_residual_trn']:.2g}|")
 lines+=['単位は実質兆円。最初のSQ割れは許容−1e−7兆円基準で2030年、2055年まで26年継続。全30年で式を照合。算術残差が小さいことと政策原因を現実に識別できたことは別。',
 '## 家計・企業等の中間経路',
 'Transmission_Traceは実現した軌道上で、税/年金/医療/VAT/給付等の名目家計源泉→実質C目標→平滑化されたC状態を分解したもの。固定SQのC状態控除を別列に保持。各源泉は同じ内生賃金・所得・価格状態で評価されており、独立の因果寄与として外した場合の差と同一ではない。',
 '|中間経路（実現軌道のC状態）|2030年|2055年|','|---|---:|---:|']
 t=rd(out/'N3_GDP_Gap_Transmission_Trace.csv')
 for channel,label in [('labor_tax','給与・事業税'),('financial_tax','金融税'),('pension_benefit','公的年金給付差'),('fund_payout','基金給付'),('fund_domestic_return_debit','基金運用益の家計所得からの振替'),('income_feedback','所得還流'),('corporate_dividend','法人改革の手取配当')]:
  a=[next(float(z['filtered_C_state_real_trn']) for z in t if int(z['year'])==y and z['channel']==channel) for y in [2030,2055]]
  lines.append(f'|{label}|{a[0]:+.6f}|{a[1]:+.6f}|')
 lines+=['VATは家計価格/所得、数量変化、既に家計へ入れた価格効果の置換を併せて扱う。数量と価格置換を独立施策の恩恵として数えない。現物給付は家計支出代替0.7と残部0.3×VA比0.216が別経路であり、政府費用を新規Gへ再加算しない。給与差額は政府→既存家計に一度、純増雇用は0。',
 '企業改革は法人税節減→配当/既存投資/企業残余→追加民間投資→資本ストック→供給吸収へ伝播。残余投資75%は原文の投資20%資格条件ではない。財政PB・利払・償還・現金は会計へ接続するが、追加G/I OFFでは余剰が自動的にGDP需要へ還流しない。2055年候補債務0/現金蓄積はこの部分財政モデルの帰結であり、全国財政閉合や実利用可能現金の証明ではない。',
 '## 限定反実仮想と相互作用',
 '給与・事業/金融課税ブロックと年金ブロックについて2×2対照を作り、他のN3施策・共通SQ条件を保持した。年金OFFは75歳コホート遅延・拠出振替・基金・国内家計運用益対応をまとめて除去する。税OFFは給与/金融課税の既存差額をまとめて除去し、相続は維持。いずれも診断スイッチであり税率原文を改訂していない。',
 '|経路|GDP−SQ 2030|GDP−SQ 2055|基準N3との差2055|','|---|---:|---:|---:|']
 for cid in dict.fromkeys(z['case'] for z in summaries):
  a=next(z for z in summaries if z['case']==cid and z['year']==2030);b=next(z for z in summaries if z['case']==cid and z['year']==2055)
  lines.append(f"|{cid}|{a['GDP_minus_SQ_trn']:+.6f}|{b['GDP_minus_SQ_trn']:+.6f}|{b['difference_vs_N3_real_GDP_trn']:+.6f}|")
 lines+=['2×2での厳密なモデル内恒等式：`基準N3−SQ = 両ブロックOFF−SQ + 税効果(年金OFF) + 年金効果(税OFF) + 相互作用`。',
 '|年|両OFF−SQ（他経路残り）|税効果・年金OFF|年金効果・税OFF|相互作用|合計|','|---|---:|---:|---:|---:|---:|']
 for y in [2030,2055]:
  z=next(z for z in interactions if z['year']==y and z['metric']=='real_GDP_trn');a=z['neither_block_minus_SQ'];b=z['tax_effect_given_pension_off'];c=z['pension_effect_given_tax_off'];d=z['tax_pension_interaction'];lines.append(f'|{y}|{a:+.9f}|{b:+.9f}|{c:+.9f}|{d:+.9f}|{a+b+c+d:+.9f}|')
 lines+=['順序を変えると税/年金に割り当てる差が変わり、その差が相互作用。両OFF−SQは未実装施策効果や純粋な較正誤差ではなく、VAT・相続・法人・医療・給付など残る経路と構造を含む。独立原因へ便宜配賦していない。他の単独OFF差や前回感度差をこの表へ足すことは禁止。構造診断（所得還流0、政策税源等の内生更新OFF、残余追加投資OFF）は政策OFFとも区別する。',
 '## 仕様・構造・全国較正の識別限界',
 '仕様未実装：KPI所得/ジニ/運用の発動仕様、EITC比較基準、純増雇用、外国人GDP5%定義、実共済区割り、インボイス制度/費用、実都市投資と2039以降固有最適化効果など。モデルに未接続のため選択枝の追加金銭効果はないが、現実効果が0と判明したわけではない。GDP不足を何兆円埋めるかはunknown。',
 '構造：医療で計算される健康労働proxyは、現行の固定コア/労働へ新たに接続していない。この未接続のモデル内追加寄与は0だが実際の政策効果はunknown。家計資源の減少がMPC/国内比/平滑化でCを減らし、所得還流と税源更新が再帰的に作用する。年金運用益の国内家計振替、原文非確定の現物配分、政府/保険者配分、G/I OFF、REGULARIZE純増0等が結果を条件付ける。構造診断の差はそのモデル条件を変えた場合の対照であり、欠落施策の正しい効果を推定した値ではない。',
 '較正：税率30%等は原文にあるが、その全国税源・所得源泉配分・従前税額・控除処理を合成世帯へ適用する部分は別問題。追加労働/金融税額を現行セルから再構成した。基金受給者、医療請求・患者負担、法人利益/投資の同一母集団も候補。全国代表性や需要反応の較正がないため、大きなC減を原文政策そのものの確定損失と断定しない。',
 f"合成セルの基準平均所得は{cal[0]['synthetic_cell_mean_reference_income_yen']:.3f}円、固定調査平均入力は{cal[0]['survey_mean_reference_income_yen']:.3f}円、比率{cal[0]['synthetic_to_survey_mean_ratio']:.6f}。さらにincome_scale1.04、物価、遅行賃金で拡大する。医療患者負担の較正残差、年金対象人数、課税基礎・従前税額はCalibration_Diagnosticsへ出力。過去年の実税収と将来の代理税額を同じ母集団とせず、全国較正残差・較正不足のGDP寄与額はunknown。外部新統計の収集や新係数採用は行っていない。",
 '税額の具体的発生源（名目兆円）：2030年の労働・事業総額proxy295.817492×30%=88.745248、割当従前税14.770375との差を移行率1/3で適用し、追加負担24.658291。金融所得proxy22.156912×20%=4.431382、従前0.952983との差×1/3で1.159466。2055年は労働・事業proxy410.520954×30%=123.156286、従前20.497600との差102.658687、金融追加4.827151。これらの家計控除が実質化・平滑化され、消費差へ入る。原文率と、未較正の課税基礎・従前税割当を分けて読む必要がある。',
 '合成セル平均と調査平均がほぼ一致しても、全国の所得源泉・納税者・控除・税収の分母が一致したことにはならない。平均所得の誤差だけでGDP差を説明したり、医療患者負担較正残差をそのままGDP損失へ換算したりしていない。',
 '## SQ共通条件の確認',
 'N3とSQの固定コア実質/名目GDP、デフレーター、人口・労働系列、外生イベント入力を全30年照合し差は0。N3−SQのコア差も0。これは共通イベントの影響が消えたという意味ではなく、同じ条件の下で政策/モデルの反応差が生じるという意味。イベント強度そのものの妥当性・政策との相互作用を独立識別していない。',
 '読取上の精査候補：2026年はapply_oil_to_initial=FalseでGDP580/名目600の初期アンカーを優先する一方、エネルギー物流15%のメタデータが残る。災害・気候の同年重なりは異なる設定イベントの加算であり、それだけで重複誤適用とは判定しない。固定コアに既に入ったGDPショックを隔離年次ループで再適用していない。SQ原本・デバフは一切変更していない。',
 '## 未識別範囲と次に実装できること',
 '算術上は実GDP差とC状態を追跡・再構成できた。ただし「政策仕様不足が何兆円、構造が何兆円、較正不足が何兆円」という排他的100%配分は識別不能。原文税率と合成税源・行動係数が同時に作用するため、現行軌道の源泉額だけから原因軸別の実効果へ分離できない。両ブロック以外の高次相互作用、未実装施策の効果、全国較正後のGDPは未識別のまま。',
 '既存コードで前進できる作業：同一税源母集団の明示、所得源泉別/控除別基礎の差替え契約、KPI年/遅行/unknown契約、法人・雇用の独立移行日程、医療/年金の部門勘定対応、現物給付の最終購入者/SNA分類。原文が欠く政策選択や実予算をAIが採用しない。Fとの将来比較では同じSQ・税源定義・家計資源/支出代替・基金運用益源泉・財政からGDPへの帰還の条件を揃え、F優位/N3劣位を未較正モデル差で確定しない。',
 f"検証{v['checks']}件・失敗{v['failed']}。GDP算術残差の絶対最大{v['max_GDP_identity_residual']:.3g}兆円、基準家計未帰属源泉の絶対最大{v['max_other_cash_unidentified']:.3g}兆円。微小丸め残差を実政策原因へ配賦していない。原本{v['direct_source_files_checked']}件を固定Commit実バイト照合。",
 '`python3 handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/N3_GDP_Gap_Attribution_Reproduce.py --root . --outdir /tmp/n3-gdp-gap-replay`。既存原本・税率・控除・共通エンジン・SQを変更せず隔離コードだけで実行。正式政策採用・PR/merge・Acceptance・DecisionLog・Freeze・Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。']
 (out/'SPE_N3_GDP_Gap_Attribution_Report_DRAFT_20261123.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.outdir.resolve())
