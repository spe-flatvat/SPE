#!/usr/bin/env python3
"""SPE VAT core limited replacement. DRAFT/NON-CANONICAL, Python stdlib only.
python Model.py Inputs.json --outdir replay
Uses immutable household/pension/macro models; replaces only VAT and C interfaces.
"""
import argparse,base64,builtins,copy,csv,hashlib,json,math,zlib
from pathlib import Path
YEARS=range(2026,2056)
def close(a,b):return math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10)
def dump(p,rows):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows({k:format(v,'.12g') if isinstance(v,float) else v for k,v in r.items()} for r in rows)
def unpack(x):
 b=zlib.decompress(base64.b64decode(x['zlib_base64']));assert len(b)==x['size'] and hashlib.sha256(b).hexdigest()==x['sha256'];return b

def sq_rates(y,s):
 food=.08
 # A proposal/stress condition, NOT asserted to be an enacted SQ reform.
 if s.get('sq_food_proposal'):
  food={2027:.02,2028:s['proposal_food_rate'],2029:.06}.get(y,.08)
 return .1,food

def rates(y,s):
 std,food=sq_rates(y,s)
 if not s['rate']:return std,food
 return (.1 if y<s['year8'] else .08 if y<s['year5'] else .05,
         .08 if y<s['food_zero_start'] else 0. if y<s['food_eight_start'] else .08 if y<s['year5'] else .05)
def ramp(y,start,n):return max(0.,min(1.,(y-start+1)/n))
def small_allowance(y):
 return {2026:.775,2027:.7,2028:.65,2029:.5,2030:.45,2031:.225}.get(y,.8 if y<2026 else 0.)

def sector_account(c,s,a,y,std):
 ref=c['reference'];scale=(1+ref['sector_growth'])**(y-2025)
 scope=a['formerly_exempt_share']
 if a['id']=='land_asset':scope*=s['land_scope']
 if a['kind']=='SMALL_BUSINESS':scope*=s['small_new_share']
 R=a['R2025']*scale*scope;P=R*min(.95,a['input_ratio']*s['input_ratio_scale'])
 ph=ramp(y,s['small_start_year'] if a['kind']=='SMALL_BUSINESS' else s['base_start'],s['base_ramp'])
 e=ph*min(1.,s['coverage_scale']) if s['expansion'] else 0.
 recover=ph*min(1.,s['coverage_scale']) if s['recovery'] else 0.
 if y==2026:e=recover=0.
 is_small=a['kind']=='SMALL_BUSINESS'
 sq_credit=R*.1/1.1*a['business']*a['buyer_eligible']*small_allowance(y) if is_small else 0.
 input_sq=.1*P;input_f=std*P
 credit=input_f*recover;unrec=input_f-credit
 rate_release=input_sq-input_f;total_release=input_sq-unrec
 costpass=min(1.,a['input_price_pass']*s['input_price_pass_scale'])
 comp=min(input_sq*s['medical_compensation_reference'],credit)*s['medical_rebase'] if a['id']=='medical' else 0.
 # Exposed and still-exempt parts have different price/credit changes.
 exposed_gross=e*(R+s['output_pass']*std*R-costpass*rate_release)-costpass*input_f*min(e,recover)
 other_gross=(1-e)*(R-costpass*rate_release)-costpass*input_f*max(0.,recover-e)
 # Counterfactual input refunds without output taxation: diagnostic, not a law.
 if e:exposed_gross-=comp
 else:other_gross-=comp
 gross=exposed_gross+other_gross
 if R==0:q=1.
 else:q=max(.7,min(1.3,(max(gross/R,.05))**(-s['quantity_elasticity']*a['household'])))
 output=exposed_gross*std/(1+std)
 buyer_credit=output*a['business']*a['buyer_eligible']*s['buyer_credit_scale']
 # Remaining exempt small suppliers retain the legislated transitional deduction.
 buyer_credit+=(1-e)*sq_credit
 new_gov=output+input_f-credit-buyer_credit
 old_gov=input_sq-sq_credit
 delta_gov=new_gov-old_gov
 price_delta=gross-R
 provider=price_delta-output+input_sq-unrec
 h=-price_delta*a['household'];g=-price_delta*a['government'];ins=-price_delta*a['insurer'];b=-price_delta*a['business']+buyer_credit-sq_credit
 premium=-ins*a['premium_pass'];h-=premium;ins+=premium
 fixed_identity=h+g+ins+b+provider+delta_gov
 assert close(fixed_identity,0.),(a['id'],y,fixed_identity)
 # Full transaction/quantity transfer ledger includes additional upstream supplies.
 buyers_actual=R-gross*q+buyer_credit*q-sq_credit
 provider_actual=(gross-output-P-unrec)*q-(R-P-input_sq)
 government_actual=new_gov*q-old_gov
 upstream_actual=P*(q-1)
 assert close(buyers_actual+provider_actual+government_actual+upstream_actual,0.)
 # Decompose newly available input credits before output-tax absorption/rebasing.
 price_credit=credit*costpass;firm_credit=credit-price_credit
 wage_credit=firm_credit*a['wage_share'];invest_credit=firm_credit*a['investment_share'];profit_credit=firm_credit-wage_credit-invest_credit
 assert close(credit,price_credit+wage_credit+invest_credit+profit_credit)
 # Rate-only input savings and newly recovered input tax enter once. Absorbed
 # output VAT and reimbursement offset affect profit; never invent a GDP windfall.
 firm_released=(1-costpass)*total_release
 wage=firm_released*a['wage_share'];investment=firm_released*a['investment_share']
 if a['kind']=='NONPRODUCED_ASSET':wage=investment=0.
 return dict(year=y,sector=a['id'],kind=a['kind'],counterfactual=int(s['recovery'] and not s['expansion']),
  market_turnover_reference_trn=R,taxable_inputs_trn=P,coverage=e,recovery_coverage=recover,quantity_ratio=q,
  SQ_input_VAT_trn=input_sq,F_input_VAT_trn=input_f,SQ_unrecoverable_trn=input_sq,F_unrecoverable_fixed_volume_trn=unrec,new_input_credit_trn=credit,
  rate_only_input_relief_trn=rate_release,total_input_cost_release_trn=total_release,
  output_VAT_fixed_volume_trn=output,buyer_credit_fixed_volume_trn=buyer_credit,SQ_buyer_transition_credit_trn=sq_credit,
  modeled_chain_VAT_trn=new_gov*q,SQ_modeled_chain_VAT_trn=old_gov,chain_VAT_delta_trn=government_actual,
  seller_remittance_trn=(output-credit)*q,upstream_VAT_trn=input_f*q,buyer_credit_trn=buyer_credit*q,
  price_ratio=gross/R if R else 1.,price_change_fixed_volume_trn=price_delta,
  household_price_benefit_trn=h,government_purchase_benefit_trn=g,insurer_price_benefit_trn=ins,business_buyer_benefit_trn=b,
  insurer_premium_change_trn=premium,provider_operating_benefit_fixed_volume_trn=provider,
  wages_trn=wage,induced_investment_trn=investment,retained_profit_and_other_trn=provider-wage-investment,
  newly_recovered_to_price_trn=price_credit,newly_recovered_to_wages_trn=wage_credit,newly_recovered_to_investment_trn=invest_credit,newly_recovered_to_profit_other_trn=profit_credit,
  medical_reimbursement_rebase_trn=comp,fixed_volume_government_delta_trn=delta_gov,
  actual_buyer_resources_delta_trn=buyers_actual,actual_provider_resources_delta_trn=provider_actual,actual_upstream_receipts_delta_trn=upstream_actual,
  actual_transfer_residual_trn=buyers_actual+provider_actual+government_actual+upstream_actual,
  land_principal_direct_GDP_addition_trn=0.,full_national_sector_estimate=None)

def reference_base(c,s):
 z={**s,'rate':False,'expansion':False,'recovery':False,'sq_food_proposal':False}
 sectors=[sector_account(c,z,a,2026,.1) for a in c['sectors']]
 baseVAT=c['reference']['VAT_national_budget_2026_trn']/c['reference']['national_share']
 hh=c['reference']['HH_taxexclusive_base_2026_trn'];food=c['reference']['HH_food_share']
 residual=(baseVAT-sum(r['SQ_modeled_chain_VAT_trn'] for r in sectors)-hh*((1-food)*.1+food*.08))/.1
 assert residual>0
 return baseVAT,residual

def regular_account(B,rate0,rate,passrate,household,govshare,wageshare,investshare,elasticity):
 gross0=B*(1+rate0);pricechange=passrate*(rate-rate0)*B;gross=gross0+pricechange
 q=max(.7,min(1.3,(gross/gross0)**(-elasticity*household))) if gross0 else 1.
 VAT=gross*rate/(1+rate);oldVAT=B*rate0
 producer=pricechange-(VAT-oldVAT)
 h=-pricechange*household;g=-pricechange*govshare;business=-pricechange*(1-household-govshare)
 assert close(h+g+business+producer+(VAT-oldVAT),0.)
 return dict(base=B,old_VAT=oldVAT,VAT=VAT*q,price_HH=h,price_government=g,business_buyer=business,producer=producer,
             wage=producer*wageshare,investment=producer*investshare,quantity=q,rate_effect=(rate-rate0)*B,pass_quantity_residual=VAT*q-oldVAT-(rate-rate0)*B)

def tax_account(c,s,y,N):
 s={**c['defaults'],**s};std,food=rates(y,s)
 if y==2026:std,food=.1,.08
 baseVAT,nonHH=reference_base(c,s);scale=N/600
 records=[sector_account(c,s,a,y,std) for a in c['sectors']]
 # Legacy 180trn household-facing base is retained; the remainder is explicitly
 # a revenue-equivalent residual, not observed taxable sales or household spending.
 H=c['reference']['HH_taxexclusive_base_2026_trn']*scale;ff=c['reference']['HH_food_share']
 regs=[regular_account(H*(1-ff),.1,std,s['rate_pass'],1.,0.,s['retained_wage_share'],s['retained_investment_share'],s['quantity_elasticity']),
       regular_account(H*ff,.08,food,s['rate_pass'],1.,0.,s['retained_wage_share'],s['retained_investment_share'],s['quantity_elasticity']),
       regular_account(nonHH*scale,.1,std,s['rate_pass'],0.,s['regular_nonHH_government_share'],s['retained_wage_share'],s['retained_investment_share'],0.)]
 # Budget-calibrated no-reform benchmark at the same year/scale; invoice changes
 # shared by SQ/F remain identifiable and are never counted as F-only resources.
 fixed={**s,'rate':False,'expansion':False,'recovery':False,'sq_food_proposal':False}
 fixed_sector=[sector_account(c,fixed,a,2026,.1) for a in c['sectors']]
 fixed_reference=(baseVAT-sum(r['SQ_modeled_chain_VAT_trn'] for r in fixed_sector))*scale+sum(r['SQ_modeled_chain_VAT_trn'] for r in fixed_sector)*(1+c['reference']['sector_growth'])**(y-2026)
 totalVAT=sum(r['VAT'] for r in regs)+sum(r['modeled_chain_VAT_trn'] for r in records)
 h=sum(r['price_HH'] for r in regs)+sum(r['household_price_benefit_trn'] for r in records if r['kind']!='NONPRODUCED_ASSET')
 gov=sum(r['price_government'] for r in regs)+sum(r['government_purchase_benefit_trn'] for r in records)
 ins=sum(r['insurer_price_benefit_trn'] for r in records)
 land_h=sum(r['household_price_benefit_trn'] for r in records if r['kind']=='NONPRODUCED_ASSET')
 business=sum(r['business_buyer']+r['producer'] for r in regs)+sum(r['business_buyer_benefit_trn']+r['provider_operating_benefit_fixed_volume_trn'] for r in records)
 common_credit_delta=sum(r['SQ_buyer_transition_credit_trn'] for r in records)-sum(r['SQ_buyer_transition_credit_trn'] for r in fixed_sector)*(1+c['reference']['sector_growth'])**(y-2026)
 business+=common_credit_delta
 wage=sum(r['wage'] for r in regs)+sum(r['wages_trn'] for r in records)
 investment=sum(r['investment'] for r in regs)+sum(r['induced_investment_trn'] for r in records)
 regular_rate=sum(r['rate_effect'] for r in regs);price_residual=sum(r['pass_quantity_residual'] for r in regs)
 old_sectors=sum(r['SQ_modeled_chain_VAT_trn'] for r in records)
 old_regular=sum(r['old_VAT'] for r in regs)
 ledger=dict(year=y,standard_rate=std,food_rate=food,modeled_VAT_trn=totalVAT,budget_scaled_reference_VAT_trn=fixed_reference,
  VAT_national_reference_trn=totalVAT*c['reference']['national_share'],VAT_local_reference_trn=totalVAT*(1-c['reference']['national_share']),VAT_delta_national_reference_trn=(totalVAT-fixed_reference)*c['reference']['national_share'],VAT_delta_local_reference_trn=(totalVAT-fixed_reference)*(1-c['reference']['national_share']),
  VAT_delta_vs_fixed_reference_trn=totalVAT-fixed_reference,regular_reference_taxexclusive_base_trn=H+nonHH*scale,
  residual_nonHH_revenue_equivalent_base_trn=nonHH*scale,regular_rate_effect_trn=regular_rate,regular_pass_quantity_effect_trn=price_residual,
  sector_chain_VAT_effect_trn=totalVAT-sum(r['VAT'] for r in regs)-old_sectors,
  invoice_and_reference_bridge_trn=old_regular+old_sectors-fixed_reference,common_invoice_business_credit_delta_trn=common_credit_delta,
  household_direct_price_benefit_trn=h,household_land_asset_cash_benefit_trn=land_h,government_purchase_benefit_trn=gov,insurer_VAT_balance_delta_trn=ins,business_total_fixed_volume_benefit_trn=business,
  household_wage_allocation_trn=wage,VAT_induced_investment_trn=investment,
  gross_SQ_unrecoverable_trn=sum(r['SQ_unrecoverable_trn'] for r in records if r['kind']=='EXEMPT_SERVICE'),
  new_recovered_input_VAT_trn=sum(r['new_input_credit_trn'] for r in records),
  rate_input_relief_trn=sum(r['rate_only_input_relief_trn'] for r in records),
  total_input_cost_release_trn=sum(r['total_input_cost_release_trn'] for r in records),
  F_remaining_unrecoverable_trn=sum(r['F_unrecoverable_fixed_volume_trn'] for r in records),
  output_VAT_covered_sectors_trn=sum(r['output_VAT_fixed_volume_trn']*r['quantity_ratio'] for r in records),
  seller_input_credit_trn=sum(r['new_input_credit_trn']*r['quantity_ratio'] for r in records),
  buyer_input_credit_trn=sum(r['buyer_credit_trn'] for r in records),
  land_principal_GDP_addition_trn=0.,unidentified_other_nonfinancial_taxbase_trn=None,all_F_transactions_VAT_total_trn=None)
 assert close(totalVAT-fixed_reference,regular_rate+price_residual+ledger['sector_chain_VAT_effect_trn']+ledger['invoice_and_reference_bridge_trn'])
 return ledger,records

def load_dependencies(c):
 src=unpack(c['household_model']).decode();oldhh={'__name__':'immutable_household'};exec(compile(src,'immutable_household.py','exec'),oldhh)
 # Three narrow adaptations: new price measure, new C reference, actual F-only pool.
 adapted=src
 for before,after in [("price_effect=f['household']-wagepass","price_effect=f.get('_price_effect',f['household']-wagepass)"),
                      ("request=max(0.,f['relief'])*TRN", "request=max(0.,f.get('_C_reference',f['relief']))*TRN"),
                      ("vat_increment=max(0.,f['direct_tax'])*TRN","vat_increment=max(0.,f.get('_C_available_budget',f['direct_tax']))*TRN")]:
  assert adapted.count(before)==1;adapted=adapted.replace(before,after)
 hh={'__name__':'household_VAT_interfaces'};exec(compile(adapted,'household_VAT_interfaces.py','exec'),hh)
 pm,foreign,bases=oldhh['dependencies'](c['household_inputs'])
 return oldhh,hh,pm,foreign,bases

def calculate(c,s,base,hh,pm,foreign):
 s={**c['defaults'],**s};assert s['year8']<s['year5'] and s['food_zero_start']<s['food_eight_start']<s['year5']
 for k in ['rate_pass','output_pass','small_new_share','land_scope','medical_rebase']:assert 0<=s[k]<=1,k
 account=[];sectors=[];state={}
 base=copy.copy(base)
 # Forecast is computed from a named fixed revised model, not inferred from the
 # realised path's future surprise. Scenario-specific deviations then remain visible.
 forecast_spec={**c['defaults'],'C':False}
 base['VAT_reference']=[]
 for r in base['macro']:
  l,_=tax_account(c,forecast_spec,r['year'],r['core_real_gdp_trn']*r['common_deflator'])
  base['VAT_reference'].append(dict(actual=l['modeled_VAT_trn'],expected=l['modeled_VAT_trn']))
 proto=base['engine']['tax_flows'];original_macro=foreign['macro'];original_compile=hh.get('compile',builtins.compile);original_exec=hh.get('exec',builtins.exec);original_annual=hh['annual_accounts']
 def flow(tx,p,y,N,omit,halt):
  l,rr=tax_account(c,s,y,N)
  sqspec={**s,'rate':False,'expansion':False,'recovery':False}
  sq,_=tax_account(c,sqspec,y,N)
  l['VAT_F_minus_current_SQ_trn']=l['modeled_VAT_trn']-sq['modeled_VAT_trn']
  l['price_F_minus_current_SQ_trn']=l['household_direct_price_benefit_trn']-sq['household_direct_price_benefit_trn']
  l['SQ_modeled_VAT_trn']=sq['modeled_VAT_trn']
  l['C_government_net_additional_resource_trn']=l['VAT_F_minus_current_SQ_trn']+l['government_purchase_benefit_trn']-sq['government_purchase_benefit_trn']
  # For comparability the older rate-only C source is also retained separately.
  H=c['reference']['HH_taxexclusive_base_2026_trn']*N/600;rsq,fsq=sq_rates(y,s)
  rate_C=H*((1-c['reference']['HH_food_share'])*(rsq-l['standard_rate'])+c['reference']['HH_food_share']*(fsq-l['food_rate']))
  reference=rate_C if s['C_source']=='RATE_ONLY' else l['price_F_minus_current_SQ_trn']
  l['C_reference_trn']=max(0.,reference);l['C_old_rate_reference_trn']=rate_C
  state[y]=l;account.append(l);sectors.extend(rr)
  # Reuse the exact existing output schema; new statutory/economic rows are separate.
  f=proto(tx,p,y,N,omit,halt)
  for k,v in list(f.items()):
   if isinstance(v,(int,float)) or v is None:f[k]=0.
  if y==2026:return f
  f.update(household=l['household_direct_price_benefit_trn']+l['household_wage_allocation_trn'],direct_tax=l['VAT_delta_vs_fixed_reference_trn'],investment=l['VAT_induced_investment_trn'],public=-l['government_purchase_benefit_trn'],relief=max(0.,reference),food_relief=H*c['reference']['HH_food_share']*(fsq-l['food_rate']),
           _price_effect=l['household_direct_price_benefit_trn'],_C_reference=max(0.,reference),_C_available_budget=l['C_government_net_additional_resource_trn'],_firm_cash=l['business_total_fixed_volume_benefit_trn']-l['household_wage_allocation_trn'])
  med=next(z for z in rr if z['sector']=='medical');v=med['output_VAT_fixed_volume_trn']*med['quantity_ratio'];cr=med['new_input_credit_trn']*med['quantity_ratio']
  f.update(medical_output_vat=v,medical_patient_vat=v*.1,medical_insurer_vat=v*.25,medical_initial_premium=v*.125,medical_extra_premium=0.,medical_public_vat=v*.65,medical_public_topup=0.,medical_internal=0.,medical_unallocated=v*.125,medical_insurer_operating_balance=-v*.125,medical_insurer_financing_balance=-v*.125,medical_input_credit=cr,
           input_credit=l['seller_input_credit_trn'],output_vat=l['output_VAT_covered_sectors_trn'])
  return f
 def cc(src,filename,mode):
  if filename=='household_macro.py':
   needle='        refund=None';assert src.count(needle)==1;src=src.replace(needle,"        f=_vat_flows(c,p,y,coreN,omit,halt)\n"+needle)
   needle="firm_sources=value(firm['credit'])-value(firm['tax_delta'])+value(firm['release'])+admin_firm";assert src.count(needle)==1;src=src.replace(needle,needle+"+f.get('_firm_cash',0.)")
   needle="firm_investment=value(firm['investment'])+firm_response*admin_firm";assert src.count(needle)==1;src=src.replace(needle,needle+"+f['investment']")
   old_sq="if not enabled:req(close(cash,0.) and close(I,0.) and close(K,0.) and close(direct,0.),'StatusQuo F-channel leakage')"
   assert src.count(old_sq)==1
   src=src.replace(old_sq,"if not enabled:req(close(cash,f['household']) and close(direct,f['direct_tax']) and close(invest_nom,f['investment']) and close(education_nom,0.),'StatusQuo VAT-only changes; no other F channels')")
  return builtins.compile(src,filename,mode)
 def ex(code,ns):ns['_vat_flows']=flow;return builtins.exec(code,ns)
 def aa(cfg,spec,b,i,f,p,pens,st,disabled=False):
  for year,val in state.items():b['VAT_reference'][year-2026]['actual']=val['modeled_VAT_trn']
  return original_annual(cfg,spec,b,i,f,p,pens,st,disabled)
 hh['compile']=cc;hh['exec']=ex;hh['annual_accounts']=aa
 hs=dict(id=s['id'],background=s['background'],mode='REPLACE',C=s['C'],C_mode=s['C_mode'],C_fraction=s['C_fraction'],fund_switch=s['fund_switch'],forecast_gap=s['forecast_gap'],gini_switch=s['gini_switch'])
 if s.get('policy')=='SQ':
  def routed_macro(cfg,eng,d,sq,elder,pol,case,end_year=2055):return original_macro(cfg,eng,d,sq,elder,'SQ',case,end_year)
  foreign['macro']=routed_macro
 try:rows,income,detail=hh['calculate'](c['household_inputs'],hs,base,pm,foreign)
 finally:hh['compile']=original_compile;hh['exec']=original_exec;hh['annual_accounts']=original_annual;foreign['macro']=original_macro
 assert len(account)==30
 for r,l in zip(rows,account):r.update(l)
 return rows,income,sectors

def run(inp,out):
 c=json.loads(Path(inp).read_text());out=Path(out);out.mkdir(parents=True,exist_ok=True);oldhh,hh,pm,foreign,bases=load_dependencies(c)
 paths={};income=[];sectors=[];regression=0
 _,pold,prev,dem,pengine=pm['dependencies'](c['household_inputs']['pension_inputs'])
 sqbase=pm['base_path'](c['household_inputs']['pension_inputs'],foreign,pold,prev,dem,pengine,'SQ_HIST')
 sqbase['source']=bases['MM']['source'];sqbase['engine']={**bases['MM']['engine'],'_pension':[{k:0. for k in z} for z in bases['MM']['engine']['_pension']]}
 sqbase['pension']=[dict(elder_employed=z['SQ_elder_employed']) for z in sqbase['elder']]
 for name,proposal in [('SQ_CURRENT',False),('SQ_PROPOSAL_FOOD0',True)]:
  ss=dict(id=name,background='MM',policy='SQ',rate=False,expansion=False,recovery=False,C=False,sq_food_proposal=proposal)
  rr,_,_=calculate(c,ss,sqbase,hh,pm,foreign);paths[name]=rr

 for s in c['cases']:
  if s.get('mode')=='LEGACY':
   spec=next(x for x in c['household_inputs']['cases'] if x['id']==s['background']+'_M7')
   r,_,_=oldhh['calculate'](c['household_inputs'],spec,bases[s['background']],pm,foreign)
   for x in r:x['case']=s['id']
   paths[s['id']]=r
   prior={int(x['year']):x for x in c['old_reference'] if x['case']==s['background']+'_M7'}
   for x in r:
    for k in ['real_gdp_trn','nominal_gdp_trn','cash_DI_delta_trn','C_cash_trn','total_unassigned_funding_trn','consolidated_balance_direct_trn']:
     assert close(x[k],float(prior[x['year']][k]));regression+=1
  else:
   r,d,z=calculate(c,s,bases[s['background']],hh,pm,foreign);paths[s['id']]=r;income+=d;sectors += [dict(case=s['id'],**v) for v in z]
 annual=[];comparison=[];tax=[];funding=[]
 # The current-SQ macro is kept as the immutable SQ reference plus known VAT-only
 # transitions. No other F measure is introduced into the SQ model.
 sq_rows=c['household_inputs']['sq_reference']
 for name,rs in paths.items():
  if name.startswith('SQ_'):continue
  bg=rs[0]['background'];off=paths[bg+'_OFF'];old=paths[bg+'_OLD']
  for i,r in enumerate(rs):
   oldrow=old[i];r['GDP_vs_previous_household_trn']=r['real_gdp_trn']-oldrow['real_gdp_trn'];r['GDP_vs_new_VAT_OFF_trn']=r['real_gdp_trn']-off[i]['real_gdp_trn']
   r['F_minus_fixed_SQ_GDP_trn']=r['real_gdp_trn']-float(sq_rows[i]['real_gdp_trn'])
   matched='SQ_PROPOSAL_FOOD0' if name=='MM_SQ_PROPOSED_FOOD0' else 'SQ_CURRENT'
   r['F_minus_matched_SQ_GDP_trn']=r['real_gdp_trn']-paths[matched][i]['real_gdp_trn']
   r['C_vs_previous_trn']=r['C_cash_trn']-oldrow['C_cash_trn'];r['unassigned_vs_previous_trn']=r['total_unassigned_funding_trn']-oldrow['total_unassigned_funding_trn']
   r['government_balance_vs_previous_trn']=r['fiscal_balance_partial_trn']-oldrow['fiscal_balance_partial_trn']
   r['insurer_VAT_balance_delta_trn']=r.get('insurer_VAT_balance_delta_trn',None)
   r['consolidated_balance_vs_new_OFF_trn']=(r['fiscal_balance_partial_trn']-off[i]['fiscal_balance_partial_trn']+r['insurer_balance_direct_trn']-off[i]['insurer_balance_direct_trn']+float(r['insurer_VAT_balance_delta_trn'] or 0.)-float(off[i]['insurer_VAT_balance_delta_trn'] or 0.))
   annual.append(r)
   comparison.append({k:r[k] for k in ['case','background','year','real_gdp_trn','nominal_gdp_trn','GDP_vs_previous_household_trn','GDP_vs_new_VAT_OFF_trn','F_minus_fixed_SQ_GDP_trn','F_minus_matched_SQ_GDP_trn','C_cash_trn','C_vs_previous_trn','total_unassigned_funding_trn','unassigned_vs_previous_trn','government_balance_vs_previous_trn','consolidated_balance_vs_new_OFF_trn']})
   if 'modeled_VAT_trn' in r:
    tax.append({k:r[k] for k in ['case','year','standard_rate','food_rate','modeled_VAT_trn','VAT_national_reference_trn','VAT_local_reference_trn','VAT_delta_national_reference_trn','VAT_delta_local_reference_trn','SQ_modeled_VAT_trn','VAT_F_minus_current_SQ_trn','budget_scaled_reference_VAT_trn','regular_reference_taxexclusive_base_trn','residual_nonHH_revenue_equivalent_base_trn','regular_rate_effect_trn','regular_pass_quantity_effect_trn','sector_chain_VAT_effect_trn','invoice_and_reference_bridge_trn','VAT_delta_vs_fixed_reference_trn','output_VAT_covered_sectors_trn','seller_input_credit_trn','buyer_input_credit_trn','unidentified_other_nonfinancial_taxbase_trn','all_F_transactions_VAT_total_trn']})
    funding.append({k:r[k] for k in ['case','year','household_direct_price_benefit_trn','C_reference_trn','C_old_rate_reference_trn','C_cash_trn','C_earmarked_funding_trn','C_vs_previous_trn','VAT_F_minus_current_SQ_trn','C_government_net_additional_resource_trn','government_program_spending_trn','total_unassigned_funding_trn','unassigned_vs_previous_trn','fund_income_trn','fund_relief_trn','fund_balance_trn','VAT_actual_reference_trn','VAT_expected_reference_trn']})
   for k in ['population','foreign_jobs','elder_employed','labor_force_population_proxy']:assert close(r[k],oldrow[k])
 # Output all columns with explicit blanks for older schemas, without invented values.
 keys=list(dict.fromkeys(k for r in annual for k in r));annual=[{k:r.get(k) for k in keys} for r in annual]
 for bg in ['MM','ZZ']:
  for a,b in zip(paths[bg+'_FULL_DIRECT'],paths[bg+'_FULL_RECLASSIFY']):assert close(a['real_gdp_trn'],b['real_gdp_trn']) and close(b['C_cash_trn'],0.)
 for r in sectors:
  assert close(r['new_input_credit_trn'],sum(r[k] for k in ['newly_recovered_to_price_trn','newly_recovered_to_wages_trn','newly_recovered_to_investment_trn','newly_recovered_to_profit_other_trn']))
  assert close(r['land_principal_direct_GDP_addition_trn'],0.)
 validation=dict(status='PASS_LOCAL_MODEL_CHECKS',cases=len(paths)-2,SQ_paths=2,annual_rows=len(annual),previous_model_regression_cells=regression,household_income_rows=len(income),sector_rows=len(sectors),input_sha256=hashlib.sha256(Path(inp).read_bytes()).hexdigest(),checks=['immutable dependencies','old and extra-zero reproduction','tax decomposition','seller and buyer input credits','fixed and quantity transfer identities','sonzei allocation','land not directly GDP','C price display no extra benefit','fund and C separate pools','unchanged population and labor','capital and GDP original engine identities'],limitations='Budget-anchored covered-market VAT estimates; turnover/input/price/quantity shares partly hypothetical. Full all-transaction totals unestimated. Quantity sensitivities adjust tax bases, not a second GDP volume increment.')
 for n,rs in [('Annual.csv',annual),('Comparison.csv',comparison),('Tax_Decomposition.csv',tax),('Sonzei_Incidence.csv',sectors),('Household_Income.csv',income),('C_Funding.csv',funding),('Summary.csv',[r for r in comparison if r['year'] in [2026,2030,2035,2045,2055]])]:dump(out/n,rs)
 dump(out/'StatusQuo_Fixed.csv',sq_rows)
 dump(out/'Price_Incidence.csv',[{k:r[k] for k in ['case','year','standard_rate','food_rate','household_direct_price_benefit_trn','household_land_asset_cash_benefit_trn','government_purchase_benefit_trn','insurer_VAT_balance_delta_trn','business_total_fixed_volume_benefit_trn','household_wage_allocation_trn','VAT_induced_investment_trn','VAT_price_effect_trn','cash_DI_delta_trn','C_cash_trn','household_disposable_nominal_trn','household_consumption_real_proxy_trn','household_consumption_nominal_proxy_trn','HH_saving_direct_delta_trn']} for r in annual if r.get('modeled_VAT_trn') is not None])
 interactions=[]
 for bg in ['MM','ZZ']:
  for i,y in enumerate(YEARS):
   for metric in ['real_gdp_trn','modeled_VAT_trn','household_direct_price_benefit_trn']:
    v=lambda tag:paths[bg+'_'+tag][i][metric]
    interactions.append(dict(background=bg,year=y,metric=metric,rate_only=v('RATE_ONLY')-v('OFF'),base_without_credit=v('BASE_NO_RECOVERY')-v('OFF'),credit_counterfactual=v('SONZEI_CF')-v('OFF'),rate_base_interaction=v('RATE_BASE_NO_RECOVERY')-v('RATE_ONLY')-v('BASE_NO_RECOVERY')+v('OFF'),credit_at_final_rates=v('FULL_DIRECT')-v('RATE_BASE_NO_RECOVERY'),full_delta=v('FULL_DIRECT')-v('OFF'),additional_C=v('FULL_ADDITIONAL')-v('FULL_DIRECT')))
 dump(out/'Interactions.csv',interactions)
 dump(out/'StatusQuo_Updated.csv',[{k:r[k] for k in ['case','year','real_gdp_trn','nominal_gdp_trn','modeled_VAT_trn','budget_scaled_reference_VAT_trn','VAT_delta_vs_fixed_reference_trn','household_direct_price_benefit_trn','tax_diagnostic_trn','expenditure_diagnostic_trn','fiscal_balance_partial_trn']} for name in ['SQ_CURRENT','SQ_PROPOSAL_FOOD0'] for r in paths[name]])
 (out/'Validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n');print(json.dumps(validation,ensure_ascii=False))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('inputs');a.add_argument('--outdir',default='replay');v=a.parse_args();run(v.inputs,v.outdir)
