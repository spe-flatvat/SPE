#!/usr/bin/env python3
"""SPE household A/B/C replacement model; DRAFT/NON-CANONICAL; stdlib only.
python Model.py Inputs.json --outdir replay
Old baseline/extra-zero and new package-OFF are deliberately distinct.
"""
import argparse,base64,builtins,copy,csv,hashlib,json,math,zlib
from pathlib import Path
TRN=1e12
YEARS=range(2026,2056)

def close(a,b):return math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10)
def dump(p,rows):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows({k:format(v,'.12g') if isinstance(v,float) else v for k,v in r.items()} for r in rows)
def unpack(x):
 b=zlib.decompress(base64.b64decode(x['zlib_base64']));assert len(b)==x['size'] and hashlib.sha256(b).hexdigest()==x['sha256'];return b
def phase(y,s):return max(0.,min(1.,(y-s['start_year']+1)/s['ramp_years']))
def reduction(income,maximum,s,threshold_index):
 upper=5000000*threshold_index;floor=2000000*threshold_index
 if income>upper:return 0.
 f=max(0.,min(1.,(upper-income)/(upper-floor)))
 if s['gradient']=='SQRT':f=math.sqrt(f)
 elif s['gradient']=='SQUARED':f*=f
 return min(1.,maximum*f)
def gini(cells,value):
 z=sorted((max(0.,r[value])/math.sqrt(r['size']),r['households']*r['size']) for r in cells)
 pop=sum(w for _,w in z);mass=sum(x*w for x,w in z)
 if not mass:return None
 cum=0.;diff=0.
 for x,w in z:diff+=w*(2*cum+w-pop)*x;cum+=w
 return diff/(pop*mass)
def equivalent_taxable(tax,year,pm):
 lo=0.;hi=1e8
 for _ in range(50):
  mid=(lo+hi)/2
  if pm['income_tax'](mid,year)<tax:lo=mid
  else:hi=mid
 return hi

def cells(c,s,base,i):
 st=c['stats'];q=base['macro'][i];y=q['year'];idx=q['common_deflator']/(600/580)
 nHH=base['foreign'][i]['population']/st['mean_household_size']*s['household_scale']
 out=[]
 for j,x in enumerate(c['income_cells']):
  weights={p['id']:x['elder_share'] if p['id']=='ELDER' else (1-x['elder_share'])*p['nonelder_weight'] for p in c['profiles']}
  den={k:sum(weights[p['id']]*p['insurance_weights'][k] for p in c['profiles']) for k in st['observed_components_yen']}
  qi=x['quintile'];cov=(st['paid_per_2000'][qi]-(st['amount_unknown_per_2000'][qi] if s['unknown_premiums']=='EXCLUDE' else 0))/2000
  components={k:v[qi] for k,v in st['observed_components_yen'].items()};normalizer=st['observed_premium_total_yen'][qi]/sum(components.values())
  for p in c['profiles']:
   n=nHH*x['share']*weights[p['id']]
   if not n:continue
   premiums={k:v*normalizer*cov*p['insurance_weights'][k]/den[k]*idx*s['income_uplift_2026'] if den[k] else 0. for k,v in components.items()}
   income=x['income_yen']*idx*s['income_uplift_2026']
   tax=st['income_tax_mean_paid_yen'][qi]*st['income_tax_paid_per2000'][qi]/2000*idx
   local=st['local_tax_mean_paid_yen'][qi]*st['local_tax_paid_per2000'][qi]/2000*idx
   di=max(0.,income-tax-local-sum(premiums.values()))
   current_group='LT1M' if income<1e6 else '1_2M' if income<2e6 else '2_3M' if income<3e6 else '3_4M' if income<4e6 else '4_5M' if income<5e6 else '5_8M' if income<8e6 else '8_12M' if income<12e6 else 'GE12M'
   out.append(dict(id=f'{j}_{p["id"]}',group=current_group,reference_income_group=x['group'],profile=p['id'],quintile=qi,households=n,size=p['size'],shares=p['earner_shares'],child=p['child'],care_use=p['care_use'],coverage=cov,gross_income_yen=income,premiums=premiums,premium_before_yen=sum(premiums.values()),baseline_tax_yen=tax,baseline_local_tax_yen=local,baseline_DI_yen=di,consumption_yen=di*x['apc'],mpc=min(1.,x['mpc']*s['mpc_scale']),idx=idx))
 return out

def annual_accounts(c,s,base,i,f,p,pm,state,disabled=False):
 y=2026+i;idx=base['macro'][i]['common_deflator']/(600/580);active=phase(y,s) if not disabled else 0.
 st=c['stats'];grid=cells(c,s,base,i);thidx=idx*s['income_uplift_2026'] if s['threshold_index'] else 1.
 triggered=s['gini_switch'] and y>=2035 and s['gini_external_2035'] is not None and s['gini_external_2035']>.36
 rate=s['maximum_rate']
 if triggered:rate=rate+s['gini_increment'] if s['gini_mode']=='PP' else rate*(1+s['gini_increment'])
 # Tax reform itself stays untouched. Isolate price-related household effect by
 # removing the existing sector wage pass-through, not by editing VAT rates/bases.
 wagepass=0.
 tau=base['engine']['policy_rules'](p,y)['standard_tax_rate']
 tx=c['pension_inputs']['foreign_inputs']['stage1_inputs']['previous_inputs']['base']['tx_inputs']
 for sec,a in tx['sector_inputs'].items():
  R=a['R2025']*(1+p['sector_nominal_growth'])**(y-2025);P=a['p']*R
  credit=tau*P if y>=p.get('sector_starts',{}).get(sec,p['base_start']) else 0.
  wagepass+=a['wage']*(1-a['price'])*((.1-tau)*P+credit)
 if y==2026:wagepass=0.
 price_effect=f['household']-wagepass
 weight=sum(r['households']*r['consumption_yen'] for r in grid)
 c_weights=[]
 for r in grid:
  income=r['gross_income_yen'];premium=sum(r['premiums'][k] for k in s['scope']);r['premium_target_yen']=premium
  shares=r['shares'] if s['A_unit']=='INDIVIDUAL' else [1.]
  r['A_yen']=premium*sum(sh*reduction(income*sh,rate,s,thidx) for sh in shares)*active if s['A'] else 0.
  r['A_eligible_households']=r['households']*r['coverage'] if s['A'] and active and any(income*sh<=5000000*thidx for sh in shares) and premium>0 else 0.
  # B applies to residual services AFTER pre-existing public/F support. Existing
  # overlap deduction is explicit and uncalibrated, never automatic full benefits.
  incB=min(income*sh for sh in r['shares']) if s['B_unit']=='ANY_MEMBER' else income
  eligible=s['B'] and incB<=3000000*thidx and bool(active)
  face=(s['B_face_yen']['medical']+s['B_face_yen']['care']*r['care_use']+s['B_face_yen']['child']*r['child'])*idx*active if eligible else 0.
  used=face*s['B_utilization']*s['B_supply_capacity']*(1-s['B_existing_overlap'])
  residual_oop=(50000+30000*r['care_use']+60000*r['child'])*idx
  substitute=min(used*s['B_substitution_share'],residual_oop)
  r.update(B_eligible_households=r['households'] if eligible else 0.,B_face_yen=face,B_used_yen=used,B_substitute_yen=substitute,B_new_service_yen=used-substitute,B_service_cost_yen=used*s['B_cost_factor'],B_admin_yen=face*s['B_admin_rate'],fund_yen=0.)
  r['VAT_price_effect_yen']=price_effect*TRN*r['consumption_yen']/weight if weight else 0.
  incC=min(income*sh for sh in r['shares']) if s['C_unit']=='ANY_MEMBER' else income
  cw=r['households']*r['consumption_yen'] if incC<=5000000*thidx else 0.
  c_weights.append(cw)
 # Fund income reallocates already-modelled VAT receipts. No fictitious extra tax
 # receipt is added to the macro budget, and unspent earmarks are not expenditure.
 fund_income=.5*max(0.,base['VAT_reference'][i-1]['actual']-base['VAT_reference'][i-1]['expected'])*TRN if s['fund_switch'] and y>=s['fund_start_year'] and i else 0.
 state['fund_balance']+=fund_income
 capacity=[]
 for r in grid:
  inc=r['gross_income_yen'];mid=3000000*thidx<inc<=5000000*thidx
  capacity.append(max(0.,r['premium_target_yen']-r['A_yen'])*r['households'] if mid and not disabled else 0.)
 fund_used=min(state['fund_balance'],sum(capacity));state['fund_balance']-=fund_used
 for r,cap in zip(grid,capacity):r['fund_yen']=fund_used*cap/sum(capacity)/r['households'] if sum(capacity) else 0.
 # C interpretations are separate. Additional transfer requires another budget;
 # price reclassification is a display-only control with zero extra cash or cost.
 request=max(0.,f['relief'])*TRN*s['C_fraction']*active if s['C'] else 0.
 if not sum(c_weights):request=0.
 vat_increment=max(0.,f['direct_tax'])*TRN
 remaining_VAT=max(0.,vat_increment-fund_income)
 actualC=min(request,remaining_VAT) if s['C_mode']=='VAT_INCREMENT_POOL' else 0. if s['C_mode']=='RECLASSIFY_ONLY' else request
 C_funded=min(actualC,remaining_VAT) if s['C_mode']=='VAT_INCREMENT_POOL' else 0.
 for r,cw in zip(grid,c_weights):
  n=r['households'];qi=r['quintile'];cov=r['coverage']
  r['C_request_yen']=request*cw/sum(c_weights)/n if sum(c_weights) else 0.
  r['C_cash_yen']=actualC*cw/sum(c_weights)/n if sum(c_weights) else 0.
  premium_relief=r['A_yen']+r['fund_yen']
  paid_tax_fraction=st['income_tax_paid_per2000'][qi]/2000
  taxkey=(y,qi,idx)
  if taxkey not in state['taxbase']:state['taxbase'][taxkey]=equivalent_taxable(st['income_tax_mean_paid_yen'][qi]*idx,y,pm)
  equivalent=state['taxbase'][taxkey]
  ct=r['C_cash_yen'] if s['C_taxable'] else 0.
  released=premium_relief/cov if cov and s['deduction_adjusts'] else 0.
  increase=paid_tax_fraction*(cov*(pm['income_tax'](equivalent+released+ct,y)-pm['income_tax'](equivalent,y))+(1-cov)*(pm['income_tax'](equivalent+ct,y)-pm['income_tax'](equivalent,y)))
  local_increase=(premium_relief if s['deduction_adjusts'] else 0.)*.1*st['local_tax_paid_per2000'][qi]/2000+ct*.1*st['local_tax_paid_per2000'][qi]/2000
  cash=premium_relief+r['C_cash_yen']-increase-local_increase
  hhC=r['mpc']*(cash+r['B_substitute_yen'])-r['B_substitute_yen']
  govC=r['B_used_yen']
  r.update(tax_increase_yen=increase,local_tax_increase_yen=local_increase,premium_after_yen=sum(r['premiums'].values())-premium_relief,cash_DI_delta_yen=cash,cash_DI_after_yen=r['baseline_DI_yen']+cash,resources_after_yen=r['baseline_DI_yen']+cash+r['B_used_yen'],HH_consumption_delta_yen=hhC,HH_saving_delta_yen=cash-hhC,government_service_consumption_yen=govC,living_burden_reduction_yen=cash+r['B_substitute_yen'],expanded_resources_delta_yen=cash+r['B_used_yen'])
  assert r['premium_after_yen']>=-1e-6 and 0<=r['B_substitute_yen']<=r['B_used_yen']+1e-6
  assert close(r['B_used_yen'],r['B_substitute_yen']+r['B_new_service_yen'])
 def tot(k):return sum(r[k]*r['households'] for r in grid)/TRN
 A,F,C,Bcost,admin=tot('A_yen'),tot('fund_yen'),tot('C_cash_yen'),tot('B_service_cost_yen'),tot('B_admin_yen')
 tax=tot('tax_increase_yen')+tot('local_tax_increase_yen')
 backfill=A*s['government_backfill_share']+F
 reserve=A*s['reserve_finance_share']
 govt=backfill+Bcost*s['B_government_share']+C+admin
 insurer_loss=A+F
 insurer_balance=backfill-insurer_loss-Bcost*(1-s['B_government_share'])
 gov_balance=tax-govt
 consolidated=tax-insurer_loss-Bcost-C-admin
 earmark=F+C_funded/TRN
 govt_gap=max(0.,govt-tax-earmark)
 insurer_gap=max(0.,insurer_loss-backfill-reserve)+Bcost*(1-s['B_government_share'])
 out=dict(year=y,A_relief_trn=A,A_eligible_households=sum(r['A_eligible_households'] for r in grid),B_eligible_households=sum(r['B_eligible_households'] for r in grid),
  B_face_trn=tot('B_face_yen'),B_existing_overlap_removed_trn=tot('B_face_yen')*s['B_existing_overlap'],B_nonclaimed_trn=tot('B_face_yen')*(1-s['B_existing_overlap'])*(1-s['B_utilization']),B_supply_shortfall_trn=tot('B_face_yen')*(1-s['B_existing_overlap'])*s['B_utilization']*(1-s['B_supply_capacity']),B_used_trn=tot('B_used_yen'),B_substitute_trn=tot('B_substitute_yen'),B_new_service_trn=tot('B_new_service_yen'),B_service_cost_trn=Bcost,B_admin_trn=admin,
  VAT_price_effect_trn=price_effect,VAT_rate_relief_trn=f['relief'],C_requested_trn=request/TRN,C_cash_trn=C,C_reclassification_only_trn=request/TRN if s['C_mode']=='RECLASSIFY_ONLY' else 0.,C_earmarked_funding_trn=C_funded/TRN,
  VAT_actual_reference_trn=base['VAT_reference'][i]['actual'],VAT_expected_reference_trn=base['VAT_reference'][i]['expected'],VAT_lag_excess_reference_trn=max(0.,base['VAT_reference'][i-1]['actual']-base['VAT_reference'][i-1]['expected']) if i else 0.,VAT_positive_increment_pool_trn=vat_increment/TRN,C_remaining_pool_trn=remaining_VAT/TRN,
  gini_external_2035=s['gini_external_2035'] if s['gini_switch'] else None,gini_triggered=int(triggered),maximum_relief_rate=rate,fund_income_trn=fund_income/TRN,fund_relief_trn=F,fund_balance_trn=state['fund_balance']/TRN,
  tax_increase_trn=tax,cash_DI_delta_trn=tot('cash_DI_delta_yen'),in_kind_benefit_trn=tot('B_used_yen'),living_burden_reduction_trn=tot('living_burden_reduction_yen'),expanded_resources_delta_trn=tot('expanded_resources_delta_yen'),
  HH_consumption_direct_delta_trn=tot('HH_consumption_delta_yen'),HH_saving_direct_delta_trn=tot('HH_saving_delta_yen'),gov_service_consumption_trn=tot('government_service_consumption_yen'),total_consumption_direct_delta_trn=tot('HH_consumption_delta_yen')+tot('government_service_consumption_yen'),
  premium_before_trn=sum(sum(r['premiums'].values())*r['households'] for r in grid)/TRN,premium_after_trn=tot('premium_after_yen'),insurer_contribution_loss_trn=insurer_loss,government_backfill_trn=backfill,government_program_spending_trn=govt,
  insurer_program_spending_trn=Bcost*(1-s['B_government_share']),government_balance_direct_trn=gov_balance,insurer_balance_direct_trn=insurer_balance,consolidated_balance_direct_trn=consolidated,reserve_finance_trn=reserve,government_unassigned_funding_trn=govt_gap,insurer_unassigned_funding_trn=insurer_gap,total_unassigned_funding_trn=govt_gap+insurer_gap,
  synthetic_equivalized_gini_before=gini(grid,'baseline_DI_yen'),synthetic_equivalized_gini_after=gini(grid,'cash_DI_after_yen'),synthetic_resources_gini_after=gini(grid,'resources_after_yen'),national_gini=None,
  benefit_rights_preserved=int(s['rights']=='PRESERVE'),future_entitlement_reduction_trn=None if s['rights']=='REDUCE_FUTURE' else 0.,general_equilibrium_total_saving_trn=None)
 assert close(gov_balance+insurer_balance,consolidated)
 assert close(out['B_face_trn'],out['B_existing_overlap_removed_trn']+out['B_nonclaimed_trn']+out['B_supply_shortfall_trn']+out['B_used_trn'])
 assert close(out['cash_DI_delta_trn'],out['HH_consumption_direct_delta_trn']+out['HH_saving_direct_delta_trn'])
 assert close(out['premium_before_trn']-out['premium_after_trn'],A+F)
 assert C_funded+fund_income<=max(vat_increment,fund_income)+1e-3
 assert state['fund_balance']>=-1e-3
 return out,grid

def dependencies(c):
 pm={'__name__':'fixed_pension'};exec(compile(unpack(c['pension_model']),'fixed_pension.py','exec'),pm)
 foreign,old,prev,dem,engine=pm['dependencies'](c['pension_inputs'])
 bases={}
 for bg,fname,pname in [('ZZ','HIST_ZERO','ZERO_ZERO'),('MM','HIST_COMBINED_MEDIUM','MEDIUM_COMBINED')]:
  b=pm['base_path'](c['pension_inputs'],foreign,old,prev,dem,engine,fname)
  source={};savedcompile=pm.get('compile',builtins.compile);savedmacro=foreign['macro'];capture={}
  def cc(src,filename,mode):
   if filename=='pension_macro.py':source['text']=src
   return builtins.compile(src,filename,mode)
  def mc(cfg,eng,d,sq,elder,pol,case,end_year=2055):
   rows=savedmacro(cfg,eng,d,sq,elder,pol,case,end_year)
   capture.update(d=copy.deepcopy(d),sq=copy.deepcopy(sq),elder=copy.deepcopy(elder),engine=eng,macro=rows)
   return rows
  pm['compile']=cc;foreign['macro']=mc
  spec=next(s for s in c['pension_inputs']['cases'] if s['id']==pname)
  try:r,_,_=pm['calculate'](c['pension_inputs'],spec,b,foreign)
  finally:pm['compile']=savedcompile;foreign['macro']=savedmacro
  capture.update(source=source['text'],foreign=b['foreign'],pension=r)
  # Explicit prospective forecast benchmark from the fixed old path. No future
  # measured tax or synthetic Gini is smuggled in as an observation.
  capture['VAT_reference']=[]
  tx=c['pension_inputs']['foreign_inputs']['stage1_inputs']['previous_inputs']['base']['tx_inputs']
  p,_,_,_,omit=capture['engine']['configure'](tx,dict(policy='F',profile='TEXT_ASSUMPTIONS'))
  for i,m in enumerate(capture['macro']):
   coreN=m['core_real_gdp_trn']*m['common_deflator']
   f=capture['engine']['tax_flows'](tx,p,2026+i,coreN,omit,False)
   actual=c['stats']['reference_VAT_national_budget_trn']/c['stats']['national_VAT_share']*coreN/600+(f['direct_tax'] if i else 0.)
   capture['VAT_reference'].append(dict(actual=actual,expected=actual))
  bases[bg]=capture
 # SQ is an immutable old model trajectory, not a new national pension estimate.
 return pm,foreign,bases

def calculate(c,s,base,pm,foreign):
 s={**c['defaults'],**s};assert s['ramp_years']>=1
 for key in ['maximum_rate','B_utilization','B_supply_capacity','B_existing_overlap','B_substitution_share','B_government_share','C_fraction','government_backfill_share','reserve_finance_share']:assert 0<=s[key]<=1,key
 assert s['government_backfill_share']+s['reserve_finance_share']<=1+1e-12
 base=copy.copy(base);base['VAT_reference']=[dict(actual=r['actual'],expected=r['actual']*(1-s['forecast_gap'])) for r in base['VAT_reference']]
 ledgers=[];grids=[];state={'fund_balance':0.,'taxbase':{}};source=base['source']
 call="ss=social(p,y,f['relief'],giniadd,refund,'social' in omit or halt or not i)"
 assert source.count(call)==1
 source=source.replace(call,"ss=_household_social(p,y,f,giniadd,refund,'social' in omit or halt or not i)")
 needle="        taxdiag=tax+direct;"
 assert source.count(needle)==1
 source=source.replace(needle,"        direct+=_hh_tax[y]\n"+needle)
 old_identity="req(close(value(ss['insurer_contribution_loss']),value(ss['insurer_backfill'])),'Social insurer transfer')"
 assert source.count(old_identity)==1
 source=source.replace(old_identity,"req(close(value(ss['insurer_contribution_loss']),value(ss['insurer_backfill'])+ss.get('insurer_unbackfilled',0.)),'Social insurer transfer including explicit unbackfilled loss')")
 hh_tax={}
 def social(p,y,f,giniadd,refund,disabled):
  accounts_s={**s,'A':False,'B':False,'C':False,'gini_switch':False,'fund_switch':False} if s['mode']=='LEGACY' else s
  ledger,grid=annual_accounts(c,accounts_s,base,y-2026,f,p,pm,state,disabled)
  if s['mode']=='LEGACY':
   ss=base['engine']['social'](p,y,f['relief'],giniadd,refund,disabled)
   hh_tax[y]=0.;ledger['legacy_household_cash_trn']=ss['household'];ledger['legacy_government_spending_trn']=ss['government']
   ledger.update(legacy_A_trn=ss['premium_relief'],legacy_B_as_cash_trn=ss['in_kind'],legacy_C_trn=ss['vat_return'],legacy_refund_trn=ss['refund'])
  else:
   hh_tax[y]=ledger['tax_increase_trn']
   ss=dict(premium_relief=ledger['A_relief_trn'],in_kind=ledger['B_used_trn'],vat_return=0.,refund=ledger['fund_relief_trn'],household=ledger['cash_DI_delta_trn'],government=ledger['government_program_spending_trn'],weighted_demand=ledger['total_consumption_direct_delta_trn'],insurer_contribution_loss=ledger['insurer_contribution_loss_trn'],insurer_backfill=ledger['government_backfill_trn'],insurer_unbackfilled=ledger['insurer_contribution_loss_trn']-ledger['government_backfill_trn'])
   ledger['legacy_household_cash_trn']=None;ledger['legacy_government_spending_trn']=None
   ledger.update(legacy_A_trn=None,legacy_B_as_cash_trn=None,legacy_C_trn=None,legacy_refund_trn=None)
  ledgers.append(ledger);grids.append(grid);return ss
 ns={'__name__':'household_macro','_pension':base['engine']['_pension'],'_household_social':social,'_hh_tax':hh_tax}
 exec(compile(source,'household_macro.py','exec'),ns)
 macro=foreign['macro'](c['pension_inputs']['foreign_inputs'],ns,base['d'],base['sq'],base['elder'],'F',s['id'])
 rows=[];income=[];detail=[];gov_state=0.
 for i,(m,l,grid) in enumerate(zip(macro,ledgers,grids)):
  # Separate household from government consumption within the unchanged aggregate
  # smoothing equation. Additional feedback/demand stays with the household proxy.
  idx=m['common_deflator'];tx=c['pension_inputs']['foreign_inputs']['stage1_inputs']['previous_inputs']['base']['tx_inputs'];par={**tx['common_model'],**tx['policy_inputs']}
  target=par['domestic_share']*l['gov_service_consumption_trn']/idx if s['mode']!='LEGACY' else 0.
  if i:gov_state=(1-par['lambda_C'])*gov_state+par['lambda_C']*target
  row=dict(case=s['id'],background=s['background'],mode=s['mode'],**l)
  for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn','household_disposable_nominal_trn','household_consumption_real_proxy_trn','C_demand_real_trn','I_policy_real_trn','capital_total_real_trn','common_deflator','labor_force_population_proxy','supply_binding']:row[k]=m[k]
  row.update(population=base['foreign'][i]['population'],foreign_jobs=base['foreign'][i]['foreign_jobs'],elder_employed=base['pension'][i]['elder_employed'],
   old_real_gdp_trn=base['macro'][i]['real_gdp_trn'],GDP_vs_old_trn=m['real_gdp_trn']-base['macro'][i]['real_gdp_trn'],
   household_consumption_nominal_proxy_trn=(m['household_consumption_real_proxy_trn']-gov_state)*idx,
   government_service_demand_state_trn=gov_state*idx,
   synthetic_micro_DI_before_trn=sum(r['baseline_DI_yen']*r['households'] for r in grid)/TRN,
   preserved_foreign_program_cost_trn=base['foreign'][i]['government_program_nominal_trn'])
  row['extended_government_balance_trn']=m['fiscal_balance_partial_trn']-row['preserved_foreign_program_cost_trn']
  rows.append(row)
  if s['mode']=='LEGACY':continue
  for group in sorted({r['group'] for r in grid}):
   gs=[r for r in grid if r['group']==group];n=sum(r['households'] for r in gs)
   a=dict(case=s['id'],year=m['year'],income_group=group,households=n,A_eligible_households=sum(r['A_eligible_households'] for r in gs),B_eligible_households=sum(r['B_eligible_households'] for r in gs),C_cash_beneficiary_households=sum(r['households'] for r in gs if r['C_cash_yen']>0))
   keys=['gross_income_yen','baseline_tax_yen','baseline_local_tax_yen','baseline_DI_yen','premium_before_yen','premium_target_yen','A_yen','fund_yen','B_face_yen','B_used_yen','B_substitute_yen','B_new_service_yen','C_request_yen','C_cash_yen','tax_increase_yen','local_tax_increase_yen','premium_after_yen','cash_DI_delta_yen','cash_DI_after_yen','HH_consumption_delta_yen','HH_saving_delta_yen','VAT_price_effect_yen','living_burden_reduction_yen','expanded_resources_delta_yen']
   for k in keys:a[k.replace('_yen','_per_HH_yen')]=sum(r[k]*r['households'] for r in gs)/n
   income.append(a)
  if s['id'] in ['MM_M7','ZZ_M7']:
   for r in grid:
    detail.append(dict(case=s['id'],year=m['year'],cell=r['id'],income_group=r['group'],reference_income_group=r['reference_income_group'],profile=r['profile'],households=r['households'],coverage=r['coverage'],gross_income_yen=r['gross_income_yen'],baseline_premium_yen=sum(r['premiums'].values()),**{k:r[k] for k in ['A_yen','B_used_yen','B_substitute_yen','C_cash_yen','cash_DI_delta_yen','HH_consumption_delta_yen','HH_saving_delta_yen']}))
 return rows,income,detail

def run(inp,out):
 c=json.loads(Path(inp).read_text());out=Path(out);out.mkdir(parents=True,exist_ok=True);pm,foreign,bases=dependencies(c)
 paths={};income=[];detail=[]
 for spec in c['cases']:
  rows,a,b=calculate(c,spec,bases[spec['background']],pm,foreign);paths[spec['id']]=rows;income+=a;detail+=b
 oldrefs={bg:{int(r['year']):r for r in c['pension_reference'] if r['case']==name} for bg,name in [('ZZ','ZERO_ZERO'),('MM','MEDIUM_COMBINED')]}
 sq={int(r['year']):r for r in c['sq_reference']};regression=0
 for bg in ['ZZ','MM']:
  for i in range(30):
   for name in ['OLD','EXTRA_ZERO']:
    r=paths[bg+'_'+name][i]
    for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','household_disposable_nominal_trn','labor_force_population_proxy']:
     assert close(r[k],float(oldrefs[bg][r['year']][k])),(bg,name,r['year'],k);regression+=1
 metrics=['real_gdp_trn','nominal_gdp_trn','cash_DI_delta_trn','HH_consumption_direct_delta_trn','HH_saving_direct_delta_trn','B_used_trn','government_program_spending_trn','consolidated_balance_direct_trn','tax_diagnostic_trn','extended_government_balance_trn']
 interactions=[]
 for bg in ['ZZ','MM']:
  for i,y in enumerate(YEARS):
   z=[paths[bg+'_M'+str(mask)][i] for mask in range(8)];r=dict(background=bg,year=y)
   for k in metrics:
    a,b,cc=z[1][k]-z[0][k],z[2][k]-z[0][k],z[4][k]-z[0][k]
    ab=z[3][k]-z[1][k]-z[2][k]+z[0][k];ac=z[5][k]-z[1][k]-z[4][k]+z[0][k];bc=z[6][k]-z[2][k]-z[4][k]+z[0][k]
    triple=z[7][k]-z[3][k]-z[5][k]-z[6][k]+z[1][k]+z[2][k]+z[4][k]-z[0][k]
    r.update({k+'_A':a,k+'_B':b,k+'_C':cc,k+'_AB_interaction':ab,k+'_AC_interaction':ac,k+'_BC_interaction':bc,k+'_ABC_interaction':triple,k+'_combined':z[7][k]-z[0][k]})
    assert close(r[k+'_combined'],a+b+cc+ab+ac+bc+triple)
   interactions.append(r)
 annual=[];fiscal=[];comparison=[]
 for name,path in paths.items():
  for i,r in enumerate(path):
   off=paths[r['background']+'_M0'][i];base=bases[r['background']]['macro'][i]
   r['ABC_GDP_vs_OFF_trn']=r['real_gdp_trn']-off['real_gdp_trn'] if r['mode']!='LEGACY' else None
   r['F_minus_SQ_GDP_trn']=r['real_gdp_trn']-float(sq[r['year']]['real_gdp_trn'])
   r['government_balance_vs_old_trn']=r['fiscal_balance_partial_trn']-base['fiscal_balance_partial_trn']
   r['consolidated_public_balance_vs_OFF_trn']=r['fiscal_balance_partial_trn']-off['fiscal_balance_partial_trn']+r['insurer_balance_direct_trn'] if r['mode']!='LEGACY' else None
   # Fixed prior pension insurer increment and foreign costs are common to cases.
   annual.append(r)
   fiscal.append({k:r[k] for k in ['case','year','mode','A_relief_trn','fund_relief_trn','C_cash_trn','B_service_cost_trn','B_admin_trn','tax_increase_trn','insurer_contribution_loss_trn','government_backfill_trn','government_program_spending_trn','insurer_program_spending_trn','government_balance_direct_trn','insurer_balance_direct_trn','consolidated_balance_direct_trn','reserve_finance_trn','government_unassigned_funding_trn','insurer_unassigned_funding_trn','total_unassigned_funding_trn','fund_income_trn','fund_balance_trn','consolidated_public_balance_vs_OFF_trn']})
   comparison.append({k:r[k] for k in ['case','background','mode','year','real_gdp_trn','nominal_gdp_trn','GDP_vs_old_trn','ABC_GDP_vs_OFF_trn','F_minus_SQ_GDP_trn','A_relief_trn','B_used_trn','C_cash_trn','cash_DI_delta_trn','HH_consumption_direct_delta_trn','HH_saving_direct_delta_trn','living_burden_reduction_trn','expanded_resources_delta_trn','government_balance_vs_old_trn','consolidated_public_balance_vs_OFF_trn','total_unassigned_funding_trn','gini_triggered','fund_relief_trn']})
   for v in r.values():assert not isinstance(v,float) or math.isfinite(v)
 # Falsification and trigger boundary controls.
 assert all(close(r['B_used_trn'],0.) for r in paths['MM_B_ZERO_USE'])
 assert all(close(r['B_used_trn'],0.) for r in paths['MM_B_FULL_OVERLAP'])
 assert all(not r['gini_triggered'] for r in paths['MM_GINI_AT_THRESHOLD'])
 assert all(close(r['fund_relief_trn'],0.) for r in paths['MM_FUND_NO_EXCESS'])
 for r,z in zip(paths['MM_C_RECLASSIFY'],paths['MM_M3']):assert close(r['real_gdp_trn'],z['real_gdp_trn']) and close(r['C_cash_trn'],0.)
 for bg in ['ZZ','MM']:
  for name,rows in paths.items():
   if not name.startswith(bg+'_'):continue
   for r,o in zip(rows,paths[bg+'_OLD']):
    for k in ['population','foreign_jobs','elder_employed','labor_force_population_proxy']:assert close(r[k],o[k])
 validation=dict(status='PASS_LOCAL_CHECKS',cases=len(paths),annual_rows=len(annual),income_rows=len(income),household_detail_rows=len(detail),old_reference_cells=regression,input_sha256=hashlib.sha256(Path(inp).read_bytes()).hexdigest(),checks=['immutable pension bytes','old and extra-zero regression','premium payer identity','B utilization and substitution identities','household disposable-consumption-saving identity','government+insurer consolidated identity','fund balance nonnegative','no reuse of VAT pool','all factorial interactions','zero use and full overlap','strict Gini boundary','zero VAT excess','C reclassification control','unchanged population and labor'],limitations='Synthetic household joint distributions; no observed national Gini; unassigned funding is not an actual debt forecast.')
 for n,rows in [('Annual.csv',annual),('Household_Income.csv',income),('Household_Detail.csv',detail),('Fiscal_Insurer.csv',fiscal),('Comparison.csv',comparison),('Interactions.csv',interactions),('Summary.csv',[r for r in comparison if r['year'] in [2026,2030,2035,2045,2055]])]:dump(out/n,rows)
 dump(out/'StatusQuo.csv',c['sq_reference'])
 dump(out/'Triggers.csv',[{k:r[k] for k in ['case','year','gini_external_2035','gini_triggered','maximum_relief_rate','VAT_actual_reference_trn','VAT_expected_reference_trn','VAT_lag_excess_reference_trn','fund_income_trn','fund_relief_trn','fund_balance_trn','VAT_positive_increment_pool_trn','C_remaining_pool_trn','C_earmarked_funding_trn','A_relief_trn']} for r in annual if r['mode']!='LEGACY'])
 (out/'Validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n');print(json.dumps(validation,ensure_ascii=False))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('inputs');a.add_argument('--outdir',default='replay');v=a.parse_args();run(v.inputs,v.outdir)
