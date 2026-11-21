#!/usr/bin/env python3
"""ChatGPT independent arithmetic audit. Never edits target or engine files.
usage: python Independent_Verify.py SOURCE_ROOT ENGINE_ROOT OUTPUT_DIR
Shared inputs: fixed demographic stocks, price index, episode/cost candidates.
Independent formulas: medical claim/cap/volume/payers/funding and VAT transactions.
The macro engine itself is replayed, not independently reimplemented.
"""
import sys,os,runpy,json,csv,math,hashlib,subprocess,platform,copy,contextlib,io,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
SRC,ENGINE,OUT=map(lambda s:Path(s).resolve(),sys.argv[1:4]);OUT.mkdir(parents=True,exist_ok=True)
D=SRC/'handoff/claude-n3-model-draft-20261121';F=ENGINE/'handoff/f-common-endoflife-finalization-20261121';sys.path.insert(0,str(F))
import Model as M, FMedical as FM

def read(p):return list(csv.DictReader(Path(p).open()))
def write(n,rows):M.dump(OUT/n,rows)
checks=[];failures=[]
def test(name,ok,detail):
 checks.append(dict(test=name,passed=bool(ok),detail=detail))
 if not ok:failures.append(checks[-1])
errors=[]
def compare(case,year,metric,expected,actual,unit='trillion_yen'):
 diff=float(actual)-expected;ok=math.isclose(float(actual),expected,abs_tol=2e-8 if unit=='trillion_yen' else 1e-5,rel_tol=3e-10)
 errors.append(dict(case=case,year=year,metric=metric,expected=expected,actual=float(actual),difference=diff,unit=unit,passed=ok))
 if not ok:failures.append(errors[-1])
# Source identity is verified against fixed git objects, never another AI's receipt.
identity=[]
for f in sorted(D.iterdir()):
 if not f.is_file():continue
 path=str(f.relative_to(SRC));b=subprocess.check_output(['git','-C',str(SRC),'show','3c77eafc2073fdaba4c129164817d2f57c9421b9:'+path]);assert b==f.read_bytes()
 identity.append(dict(commit='3c77eafc2073fdaba4c129164817d2f57c9421b9',path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
test('eight_fixed_source_originals',len(identity)==8,len(identity));(OUT/'Source_Identity.json').write_text(json.dumps(identity,indent=2)+'\n')
# Observe immutable engine calls without changing any returned values.
instances=[];executions=[];taxcalls=[]
OriginalMedical=FM.Medical
class ObservedMedical(OriginalMedical):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);instances.append(self)
FM.Medical=ObservedMedical
original_load=M.load

def observed_load(c):
 r=original_load(c);root,edu,ec,integ,v,vc=r;ex=integ.execute;ta=v.tax_account
 def tax(cfg,s,y,N):
  ledger,records=ta(cfg,s,y,N)
  if s.get('policy')=='SQ':taxcalls.append((copy.deepcopy(s),y,N,copy.deepcopy(ledger),copy.deepcopy(records)))
  return ledger,records
 v.tax_account=tax
 def execute(*a,**kw):
  z=ex(*a,**kw);executions.append(z);return z
 integ.execute=execute
 return r
M.load=observed_load
with tempfile.TemporaryDirectory(prefix='spe-n3-observed-') as td:
 sys.argv=[str(D/'SPE_N3_Medical_On_CommonSQ_Draft_DRAFT_20261121.py'),str(ENGINE),td]
 capture=io.StringIO()
 with contextlib.redirect_stdout(capture):ns=runpy.run_path(str(D/'SPE_N3_Medical_On_CommonSQ_Draft_DRAFT_20261121.py'),run_name='__main__')
 (OUT/'Observed_Replay_Run.txt').write_text(capture.getvalue())
 replay=[]
 for short in ['Annual','Common','vs_SQ_Common_On']:
  f=Path(td)/('N3_Medical_'+short+'.csv');target=D/('SPE_N3_Medical_'+short+'_DRAFT_20261121.csv');b=f.read_bytes();o=target.read_bytes();rows=read(f);orig=read(target)
  numeric=rows==orig
  replay.append(dict(file=target.name,replayed_size=len(b),replayed_sha256=hashlib.sha256(b).hexdigest(),source_size=len(o),source_sha256=hashlib.sha256(o).hexdigest(),byte_equal=b==o,rows=len(rows),columns=len(rows[0]),parsed_equal=numeric))
  (OUT/('Replay_'+f.name)).write_bytes(b)
 A=read(Path(td)/'N3_Medical_Annual.csv');C=read(Path(td)/'N3_Medical_Common.csv');CMP=read(Path(td)/'N3_Medical_vs_SQ_Common_On.csv')
 (OUT/'Replay_Selftest.json').write_bytes((Path(td)/'N3_Selftest.json').read_bytes())
(OUT/'Replay_Comparison.json').write_text(json.dumps(replay,indent=2)+'\n')
test('420_rows_14_cases_all_three_CSV_byte_equal',all(r['byte_equal'] and r['rows']==420 for r in replay),replay)
by={(r['case'],int(r['year'])):r for r in A};cb={(r['case'],int(r['year'])):r for r in C}
c=ns['c'];specs={x[0]:x for x in ns['CASES']};mds={md.s['id']:md for md in instances}
# Closed-form claim independent of FM.patient_claim / annual_patient / n3_claim.
# The legacy cap numbers are model inputs, not independently validated law.
def coins0(age,group):
 if age=='PRESCHOOL':return .2
 if age=='AGE70_74' and group in ['TAXFREE','GENERAL']:return .2
 if age=='AGE75PLUS' and group in ['TAXFREE','GENERAL']:return .1
 return .3

def claim(age,group,bill,months,regime,coins,capfactor):
 elder=age in ['AGE70_74','AGE75PLUS'];old=regime=='PRE2026AUG'
 if group=='TAXFREE':limit=([24600,25700] if elder else [35400,36900])[not old];repeat=24600;annual=math.inf if old else 290000
 elif group=='GENERAL':limit=57600 if old else 61500;repeat=34500 if regime=='POST2027AUG' else 44400;annual=math.inf if old else 410000
 elif group=='MIDDLE':limit=(80100 if old else 85800)+.01*max(0,bill-(267000 if old else 286000));repeat=44400;annual=math.inf if old else 530000
 else:limit=(167400 if old else 179100)+.01*max(0,bill-(558000 if old else 597000));repeat=93000;annual=math.inf if old else 1110000
 first=min(months,3)*min(coins*bill,limit*capfactor);later=max(months-3,0)*min(coins*bill,repeat*capfactor)
 return min(first+later,annual*capfactor)

def annual(y,age,group,bill,months,rate,cf):
 w=[('PRE2026AUG',7/12),('POST2026AUG',5/12)] if y==2026 else [('POST2026AUG',7/12),('POST2027AUG',5/12)] if y==2027 else [('POST2027AUG',1)]
 return math.fsum(weight*claim(age,group,bill,months,reg,rate,cf) for reg,weight in w)

def fraction(y,start,ramp):return min(1,max(0,(y-start+1)/ramp))

def effective(y,age,group,bill,months,s,rate,scope):
 b=annual(y,age,group,bill,months,coins0(age,group),1)
 if not s['copay']:return b
 ph=fraction(y,s['start_year'],s['ramp_years']);rr=coins0(age,group) if scope=='ONLY_CURRENT_30' and coins0(age,group)!=.3 else rate
 cf=1+(-1 if s['cap_mode']=='PATIENT_CAP_DOWN' else 1)*s['cap_change']*ph
 return b+ph*(annual(y,age,group,bill,months,rr,cf)-b)
# Compare independent elementary claims over rates, scopes, all regimes and cap boundaries.
boundaries=[];original_claim=ns['n3_claim']
for rate in [.3,.4,.5]:
 for scope in ['ALL_AGES','ONLY_CURRENT_30']:
  ns['N3'].update(coinsurance=rate,scope=scope)
  for age in ['PRESCHOOL','AGE6_69','AGE70_74','AGE75PLUS']:
   for group in c['income_weights']:
    for regime in ['PRE2026AUG','POST2026AUG','POST2027AUG']:
     for months in [0,1,3,4,6,12]:
      for bill in [0,24600/.5,286000,597000,1200000]:
       for cf in [.9,1,1.1]:
        rr=coins0(age,group) if scope=='ONLY_CURRENT_30' and coins0(age,group)!=.3 else rate
        expected=claim(age,group,bill,months,regime,rr,cf);actual=original_claim(age,group,dict(bill_yen=bill,months=months),regime,True,cf)
        ok=math.isclose(expected,actual,abs_tol=1e-7)
        boundaries.append(dict(rate=rate,scope=scope,age=age,income=group,regime=regime,months=months,bill_yen=bill,capfactor=cf,expected_yen=expected,actual_yen=actual,passed=ok))
test('independent_claim_boundaries',all(x['passed'] for x in boundaries),dict(examples=len(boundaries),max_error_yen=max(abs(x['expected_yen']-x['actual_yen']) for x in boundaries)))
write('Independent_Claim_Boundaries.csv',boundaries)
# All ordinary medical claims recomputed from input budget/population weights.
common_payer_errors=[];phase_rows=[]
for cid,md in mds.items():
 s=md.s;spec=specs[cid];rate=spec[3];scope=spec[8];debt=asset=0.
 for i,w in enumerate(md.rows):
  y=w['year'];ph=fraction(y,s['start_year'],s['ramp_years']);idx=ns['defs'][i]/ns['defs'][0]
  # Use fixed demography/cost data as shared inputs; no original claim function.
  import Demand
  episodes,ep,aw,_=Demand.calculate(y,md.trajectory,md.elder,c['population_reference'],c['demand_parameters'],s['demand_mode'])
  total=c['observations']['medical_total_2024_trn']*idx*sum(aw.values())/sum(c['age_cost_weights'].values());baseoop=reformoop=gross=static=necessary=0
  refcost=sum(pr['probability']*pr['bill_yen']*pr['months'] for pr in c['claim_profiles'])
  for age,weight in aw.items():
   for group,iw in c['income_weights'].items():
    persons=total*weight/sum(aw.values())*iw*1e12/(refcost*idx)
    for pr in c['claim_profiles']:
     bill=pr['bill_yen']*idx;n=persons*pr['probability'];months=pr['months'];a=n*annual(y,age,group,bill,months,coins0(age,group),1)/1e12;b=n*effective(y,age,group,bill,months,s,rate,scope)/1e12
     q=max(.7,min(1.2,(max(b,1e-12)/max(a,1e-12))**(-s['demand_elasticity']))) if s['copay'] else 1
     bb=n*bill*months/1e12;gross+=bb*q;baseoop+=a;reformoop+=b*q;static+=b-a;necessary+=max(0,bb*(1-q))*s['necessary_care_share']
  co=md.common[i];cp={**c['common_parameters'],**s['common_overrides'],'enabled':s['common']}
  if s['universal_palliative']:cp.update(universal_palliative=True,palliative_additional_yen=0.)
  # Independent common clinical delta and same-person marginal copay, per age/income/setting.
  chosen=co['chosen_transitions'];served=co['universal_palliative_served'];baseunit=sum(cp['baseline_setting_shares'][k]*cp['baseline_cost_yen'][k] for k in cp['baseline_setting_shares']);destunit=sum(cp['destination_shares'][k]*cp['destination_cost_yen'][k] for k in cp['destination_shares'])
  cp_patient=0.;univ_patient=0.;age_map={'U15':'PRESCHOOL','A15_64':'AGE6_69','65_69':'AGE6_69','70_74':'AGE70_74','75plus':'AGE75PLUS'}
  for ag,n in ep.items():
   for group,iw in c['income_weights'].items():
    def oop(cost):return effective(y,age_map[ag],group,cost*idx/s['episode_months'],s['episode_months'],s,rate,scope)
    oldp=sum(cp['baseline_setting_shares'][k]*oop(cp['baseline_cost_yen'][k]) for k in cp['baseline_setting_shares']);newp=sum(cp['destination_shares'][k]*oop(cp['destination_cost_yen'][k]+cp['palliative_additional_yen']) for k in cp['destination_shares'])
    weight=n/episodes*iw;cp_patient+=chosen*weight*(newp-oldp)/1e12
    u=cp.get('universal_palliative_unit_yen',100000)
    margin0=sum(cp['baseline_setting_shares'][k]*(oop(cp['baseline_cost_yen'][k]+u)-oop(cp['baseline_cost_yen'][k])) for k in cp['baseline_setting_shares']);margin1=sum(cp['destination_shares'][k]*(oop(cp['destination_cost_yen'][k]+u)-oop(cp['destination_cost_yen'][k])) for k in cp['destination_shares'])
    univ_patient+=weight*((served-chosen)*margin0+chosen*margin1)/1e12
  cp_patient+=univ_patient
  commonclinical=chosen*(destunit-baseunit+cp['palliative_additional_yen'])*idx/1e12+served*cp.get('universal_palliative_unit_yen',100000)*idx/1e12
  clinical=gross-total+commonclinical;patient=reformoop-baseoop+cp_patient;benefit=clinical-patient;public=benefit*s['clinical_public_fraction'];insurer=benefit-public
  premium=insurer*s['premium_pass'];backfill=insurer*s['government_insurer_backfill_share'];gov=public+co['common_program_cost_trn']+backfill;insbalance=premium+backfill-insurer;interest=debt*s['medical_debt_rate'];need=gov-insbalance+interest
  financed=need*s['finance_fraction'];tax=financed*s['finance_mix']['TAX'];fp=financed*s['finance_mix']['PREMIUM'];crowd=financed*s['finance_mix']['OTHER_SPENDING'];flow=financed*s['finance_mix']['DEBT'];issue=max(0,flow);redemption=min(debt,max(0,-flow));added=max(0,-flow-redemption);debt+=issue-redemption;asset+=added
  cash=-patient-premium-co['extra_household_cash_burden_trn']-tax-fp
  vals=dict(baseline_medical_bill_trn=total,baseline_patient_model_trn=baseoop,reform_medical_bill_before_common_trn=gross,patient_static_transfer_trn=static,demand_volume_cost_delta_trn=gross-total,necessary_care_foregone_cost_proxy_trn=necessary,clinical_cost_delta_trn=clinical,patient_payment_delta_trn=patient,public_clinical_payment_delta_trn=public,insurer_clinical_payment_delta_trn=insurer,household_cash_delta_trn=cash,government_cost_delta_trn=gov+interest-crowd,insurer_balance_delta_trn=insbalance+fp,medical_financing_tax_trn=tax,medical_financing_premium_trn=fp,medical_other_spending_crowded_trn=crowd,medical_policy_debt_issue_trn=issue,medical_unassigned_direct_cash_requirement_trn=gov-insbalance,medical_unassigned_after_sources_trn=need-financed,medical_policy_debt_stock_trn=debt,medical_policy_financial_asset_stock_trn=asset)
  for k,expected in vals.items():compare(cid,y,k,expected,w[k])
  compare(cid,y,'common_patient_payment_delta_trn',cp_patient,co['patient_payment_delta_trn']);compare(cid,y,'universal_patient_payment_trn',univ_patient,co['universal_palliative_patient_trn'])
  phase_rows.append(dict(case=cid,year=y,phase=ph,target_rate_candidate=rate,scope=scope,capfactor=1+(-1 if s['cap_mode']=='PATIENT_CAP_DOWN' else 1)*s['cap_change']*ph,unassigned_after_sources_trn=need-financed,debt_stock_trn=debt,financial_asset_stock_trn=asset,household_cash_delta_trn=cash))
write('Independent_Medical_Finance.csv',phase_rows)
# VAT: algebra reduced for the actually executed SQ switches (no F expansion/recovery).
vc=ns['vc'];reference=vc['reference'];defaults=vc['defaults'];vatrows=[];sectors=[]
def vat_rates(y,mode):
 z=min(y,2035) if mode=='FREEZE2035' else y
 standard=.1+sum(bump for threshold,bump in [(2032,.02),(2034,.03),(2038,.03),(2040,.02)] if z>=threshold) if mode else .1
 food=.08 if y<2030 or not mode else standard
 return (.1,.08) if y==2026 else (standard,food)

def sector_inputs(y,std):
 out=[]
 for a in vc['sectors']:
  scope=a['formerly_exempt_share']*(defaults['land_scope'] if a['id']=='land_asset' else defaults['small_new_share'] if a['kind']=='SMALL_BUSINESS' else 1)
  R=a['R2025']*(1+reference['sector_growth'])**(y-2025)*scope;P=R*min(.95,a['input_ratio']*defaults['input_ratio_scale']);costpass=min(1,a['input_price_pass']*defaults['input_price_pass_scale']);release=(.1-std)*P
  allowance={2026:.775,2027:.7,2028:.65,2029:.5,2030:.45,2031:.225}.get(y,0.)
  deduction=R*.1/1.1*a['business']*a['buyer_eligible']*allowance if a['kind']=='SMALL_BUSINESS' else 0
  price=-costpass*release;premium=-(-price*a['insurer'])*a['premium_pass'];hh=-price*a['household']-premium
  out.append(dict(sector=a['id'],kind=a['kind'],P=P,VAT=std*P-deduction,oldVAT=.1*P-deduction,HH=hh,price=price,release=release,wage=0 if a['kind']=='NONPRODUCED_ASSET' else (1-costpass)*release*a['wage_share'],investment=0 if a['kind']=='NONPRODUCED_ASSET' else (1-costpass)*release*a['investment_share']))
 return out
baseVAT=reference['VAT_national_budget_2026_trn']/reference['national_share'];base_records=sector_inputs(2026,.1);H0=reference['HH_taxexclusive_base_2026_trn'];foodshare=reference['HH_food_share'];nonHH=(baseVAT-sum(x['oldVAT'] for x in base_records)-H0*(.1*(1-foodshare)+.08*foodshare))/.1
unique={}
for s,y,N,ledger,records in taxcalls:
 cid=s['id'];unique[cid,y]=(N,ledger,records)
for (cid,y),(N,ledger,records) in unique.items():
 spec=specs[cid];mode=spec[-1];std,food=vat_rates(y,mode);scale=N/600;hhbase=H0*scale
 tax=price=wage=investment=0.
 for B,oldr,newr,hh in [(hhbase*(1-foodshare),.1,std,1),(hhbase*foodshare,.08,food,1),(nonHH*scale,.1,std,0)]:
  pricechange=defaults['rate_pass']*(newr-oldr)*B
  # q=1 exactly because quantity_elasticity=0 in the fixed candidate settings.
  taxed=(B*(1+oldr)+pricechange)*newr/(1+newr);producer=pricechange-(taxed-B*oldr)
  tax+=taxed;price-=pricechange*hh;wage+=producer*defaults['retained_wage_share'];investment+=producer*defaults['retained_investment_share']
 rr=sector_inputs(y,std);tax+=sum(x['VAT'] for x in rr);price+=sum(x['HH'] for x in rr if x['kind']!='NONPRODUCED_ASSET');wage+=sum(x['wage'] for x in rr);investment+=sum(x['investment'] for x in rr)
 fixed=(baseVAT-sum(x['oldVAT'] for x in base_records))*scale+sum(x['oldVAT'] for x in base_records)*(1+reference['sector_growth'])**(y-2026)
 for k,x in dict(standard_rate=std,food_rate=food,modeled_VAT_trn=tax,VAT_delta_vs_fixed_reference_trn=tax-fixed,household_direct_price_benefit_trn=price,household_wage_allocation_trn=wage,VAT_induced_investment_trn=investment).items():compare(cid,y,k,x,ledger[k])
 for row,observed in zip(rr,records):
  compare(cid,y,'sector_'+row['sector']+'_VAT',row['VAT'],observed['modeled_chain_VAT_trn']);compare(cid,y,'sector_'+row['sector']+'_price',row['price'],observed['price_change_fixed_volume_trn']);sectors.append(dict(case=cid,year=y,sector=row['sector'],independent_VAT_trn=row['VAT'],observed_VAT_trn=observed['modeled_chain_VAT_trn'],quantity_ratio=observed['quantity_ratio']))
 vatrows.append(dict(case=cid,year=y,standard_rate=std,food_rate=food,VAT_trn=tax,household_price_effect_trn=price,macro_base_nominal_trn=N,quantity_elasticity=defaults['quantity_elasticity'],rate_pass=defaults['rate_pass']))
write('Independent_VAT.csv',vatrows);write('Independent_VAT_Sectors.csv',sectors)
test('VAT_actual_case_years',len(unique)==420,len(unique));test('VAT_candidate_quantity_elasticity_zero',defaults['quantity_elasticity']==0,defaults['quantity_elasticity'])
# Comparison arithmetic uses actual independent replay rows, not reported rounded values.
comparison=read(OUT/'Replay_N3_Medical_vs_SQ_Common_On.csv')
for r in comparison:
 cid=r['case'];y=int(r['year']);ref=by['SQ_COMMON_ON',y]
 for k,val in r.items():
  if k.endswith('_minus_SQ_COMMON_ON') and val!='':
   metric=k.removesuffix('_minus_SQ_COMMON_ON');compare(cid,y,k,float(by[cid,y][metric])-float(ref[metric]),val)
# Fixed common physical quantities and behavioral input tests, not flags alone.
from CommonInterface import run_common
from CommonEndOfLife import calculate
common_tests=[]
demand=dict(price_index=1.,population_scale=1.,registry_population=c['registry_population_reference'],clinical_strata=c['clinical_strata'],age_demand_episodes=450000)
params={**c['common_parameters'],'universal_palliative':True,'palliative_additional_yen':0.}
for y in [2026,2031,2032,2035,2040,2055]:
 for label,updates,dm in [('BASE',{},{}),('NO_REGISTRATION',{'adoption_target':0},{}),('WITHDRAW_ALL',{'withdrawn_share':1},{}),('UNKNOWN_WISH',{'confirmed_share':0},{}),('NO_EXPLICIT_PREFERENCE',{'explicit_preference_share':0},{}),('NO_CAPACITY',{'transition_capacity':0},{}),('NO_DEMAND',{}, {'age_demand_episodes':0}),('LARGE_CAPACITY',{'transition_capacity':1e8},{}),('EXTRA_TIME',{'capacity_allocation':'EXTRA_TRANSITION_RESOURCE'},{}),('DISABLED',{'enabled':False},{})]:
  p={**params,**updates};inp={**demand,**dm};r=run_common(y,inp,p,c['common_financing'])
  eligible=r['transition_need'];target=max(r['universal_palliative_need']*r['implementation_phase'],eligible) if r['universal_palliative_need'] else 0
  units=2 if label=='EXTRA_TIME' else 1;denom=target+(units-1)*eligible if target else eligible;access=min(1,r['transition_capacity']/denom) if denom else 0
  compare(label,y,'resource_use_closed_form',denom*access,r['resource_units_used'],'patients')
  assert r['resource_units_used']<=r['transition_capacity']+1e-6
  if label in ['NO_REGISTRATION','WITHDRAW_ALL','UNKNOWN_WISH','NO_EXPLICIT_PREFERENCE','NO_CAPACITY','NO_DEMAND','DISABLED']:test('no_automatic_transition_'+label+'_'+str(y),r['chosen_transitions']==0,r['chosen_transitions'])
  common_tests.append(dict(test_case=label,year=y,chosen=r['chosen_transitions'],served=r['universal_palliative_served'],unmet=r['universal_palliative_unmet'],resources=r['resource_units_used'],capacity=r['transition_capacity'],expected_resources=denom*access))
 # Equal access under varying registration, and identical tariff at same bill.
 regs=[run_common(y,demand,{**params,'adoption_target':adopt},c['common_financing']) for adopt in [0,.3,.6]]
 test('registration_does_not_change_palliative_access_'+str(y),len({r['universal_palliative_served'] for r in regs})==1,[r['universal_palliative_served'] for r in regs])
write('Common_Behavior_Boundaries.csv',common_tests)
physical=['chosen_transitions','transition_unmet','universal_palliative_served','universal_palliative_unmet','transition_capacity','resource_units_used']
for cid,md in mds.items():
 for i,r in enumerate(md.common):
  y=r['year'];ref=mds['SQ_COMMON_ON'].common[i]
  if md.s['common']:
   for k in physical:compare(cid,y,'common_physical_'+k,ref[k],r[k],'patients')
  else:compare(cid,y,'common_OFF_transition',0,r['chosen_transitions'],'patients')
  compare(cid,y,'patient_union_identity',r['chosen_transitions']+r['universal_palliative_served']-r['overlap_patients'],r['unique_patients_served'],'patients')
  test('capacity_'+cid+'_'+str(y),r['resource_units_used']<=r['transition_capacity']+1e-7,r['resource_units_used']-r['transition_capacity'])
# Medical activation boundaries for all candidates (not VAT-combined paths).
for cid,spec in specs.items():
 if not spec[2] or spec[-1]:continue
 for y in range(2026,spec[6]):
  ref='SQ_COMMON_ON' if spec[1] else 'SQ_COMMON_OFF'
  for k in ['patient_payment_delta_trn','household_cash_delta_trn','real_gdp_trn']:compare(cid,y,'pre_activation_'+k,float(by[ref,y][k]),by[cid,y][k])
write('Independent_Cell_Comparisons.csv',errors)
# Keep verdict based on computed checks; no hard-coded PASS on failures.
result=dict(status='PASS_INDEPENDENT_ARITHMETIC' if not failures else 'FAIL',source_originals=len(identity),replay=replay,claim_boundary_examples=len(boundaries),medical_case_years=sum(len(md.rows) for md in instances),VAT_case_years=len(unique),independent_numeric_comparisons=len(errors),max_absolute_numeric_difference=max(abs(x['difference']) for x in errors),failed_checks=len(failures),checks=checks,failures=failures,macro_independent_reimplementation=False,shared_inputs=['demography/cost-age weights from fixed Demand module','price indices','candidate costs/income weights','common program and extra cash ledgers for finance reconstruction'],python=sys.version,platform=platform.platform())
(OUT/'Independent_Result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['checks','failures','replay']},ensure_ascii=False))
if failures:print(json.dumps(failures[:10],ensure_ascii=False));sys.exit(1)
