#!/usr/bin/env python3
"""Independent edge examples, ledger checks and byte-identical numerical replay."""
import csv,hashlib,importlib.util,json,math,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('vat_model',P/'Model.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
c=json.loads((P/'Inputs.json').read_text());s=c['defaults'];checks=[]
def eq(a,b):assert math.isclose(a,b,abs_tol=2e-8,rel_tol=2e-10),(a,b)
def rows(n):return list(csv.DictReader((P/n).open()))
# Hand example: sales100, taxable inputs20, 10% tax, full output and input price pass.
a=dict(id='example',kind='EXEMPT_SERVICE',R2025=100.,formerly_exempt_share=1.,input_ratio=.2,input_price_pass=1.,wage_share=0.,investment_share=0.,household=1.,government=0.,insurer=0.,business=0.,buyer_eligible=0.,premium_pass=0.)
cc=json.loads(json.dumps(c));cc['reference']['sector_growth']=0
ss={**s,'base_start':2027,'base_ramp':1,'output_pass':1.,'input_price_pass_scale':1.}
r=m.sector_account(cc,ss,a,2035,.1)
eq(r['new_input_credit_trn'],2.);eq(r['price_change_fixed_volume_trn'],8.);eq(r['output_VAT_fixed_volume_trn'],108/11);eq(r['modeled_chain_VAT_trn'],108/11)
r0=m.sector_account(cc,{**ss,'recovery':False},a,2035,.1)
eq(r0['new_input_credit_trn'],0.);eq(r0['price_change_fixed_volume_trn'],10.);eq(r0['modeled_chain_VAT_trn'],12.)
# No taxation/recovery must leave the old input-tax chain unchanged at same rate.
r0=m.sector_account(cc,{**ss,'expansion':False,'recovery':False},a,2035,.1);eq(r0['chain_VAT_delta_trn'],0.)
checks+=['independent seller/output/input-credit examples including disabled recovery']
for sp in c['cases']:
 if sp.get('mode')=='LEGACY':continue
 ss={**s,**sp}
 for y in [2026,2028,2035,2037,2055]:
  l,rs=m.tax_account(c,ss,y,600.)
  eq(l['VAT_delta_vs_fixed_reference_trn'],sum(l[k] for k in ['regular_rate_effect_trn','regular_pass_quantity_effect_trn','sector_chain_VAT_effect_trn','invoice_and_reference_bridge_trn']))
  eq(l['VAT_national_reference_trn']+l['VAT_local_reference_trn'],l['modeled_VAT_trn'])
  if ss['quantity_elasticity']==0:
   eq(l['VAT_delta_vs_fixed_reference_trn']+sum(l[k] for k in ['household_direct_price_benefit_trn','household_land_asset_cash_benefit_trn','government_purchase_benefit_trn','insurer_VAT_balance_delta_trn','business_total_fixed_volume_benefit_trn']),0.)
  for r in rs:
   eq(r['modeled_chain_VAT_trn'],r['seller_remittance_trn']+r['upstream_VAT_trn']-r['buyer_credit_trn'])
   eq(r['new_input_credit_trn'],sum(r[k] for k in ['newly_recovered_to_price_trn','newly_recovered_to_wages_trn','newly_recovered_to_investment_trn','newly_recovered_to_profit_other_trn']))
   eq(r['actual_transfer_residual_trn'],0.)
   if r['kind']=='NONPRODUCED_ASSET':eq(r['wages_trn']+r['induced_investment_trn']+r['land_principal_direct_GDP_addition_trn'],0.)
l,_=m.tax_account(c,{**s,'rate':False,'expansion':False,'recovery':False},2026,600.)
eq(l['modeled_VAT_trn'],26.688/.78)
checks+=['2026 budget anchor','tax decomposition and national/local reference sum','fixed-volume household/business/government/insurer/land transfer closure','seller and buyer credit chain','credit incidence sum','quantity transaction closure including upstream supplies','land principal no direct GDP or induced investment']
a=rows('Annual.csv');by={(r['case'],r['year']):r for r in a}
for r in a:
 if not r['modeled_VAT_trn']:continue
 n=lambda k:float(r[k])
 eq(n('C_cash_trn'),n('C_requested_trn') if r['case'].endswith('_FULL_ADDITIONAL') else n('C_cash_trn'))
 assert n('C_earmarked_funding_trn')<=max(0.,n('C_government_net_additional_resource_trn')-n('fund_income_trn'))+1e-8
 eq(n('VAT_positive_increment_pool_trn'),max(0.,n('C_government_net_additional_resource_trn')))
 if 'RECLASSIFY' in r['case']:eq(n('C_cash_trn'),0.);eq(n('real_gdp_trn'),float(by[(r['background']+'_FULL_DIRECT',r['year'])]['real_gdp_trn']))
 if 'POOL' in r['case']:eq(n('C_cash_trn'),n('C_earmarked_funding_trn'))
 if r['case'] in ['MM_FUND_ON','MM_FUND_C_POOL','MM_GINI_AND_FUND'] and int(r['year'])>=2035:
  eq(n('fund_income_trn'),.5*n('VAT_lag_excess_reference_trn'))
for y in range(2026,2056):
 eq(float(by[('MM_LAND_NONE',str(y))]['real_gdp_trn']),float(by[('MM_FULL_ADDITIONAL',str(y))]['real_gdp_trn']))
checks+=['C and fund resource separation','reclassification no extra cash/GDP','pool constrained to net government resources','50% lagged excess fund rule','land scope changes tax but no mechanical GDP gain']
# Exercise a genuinely positive funding pool, including its competition with the fund.
_,hh,pm,foreign,bases=m.load_dependencies(c)
for fund in [False,True]:
 sp=dict(id='VERIFY_POSITIVE_POOL',background='MM',rate=False,expansion=True,recovery=True,output_pass=0.,C=True,C_mode='VAT_INCREMENT_POOL',fund_switch=fund,forecast_gap=.1)
 rr,_,_=m.calculate(c,sp,bases['MM'],hh,pm,foreign)
 assert any(r['C_government_net_additional_resource_trn']>0 for r in rr)
 if not fund:assert any(r['C_cash_trn']>0 for r in rr)
 for r in rr:
  assert r['C_earmarked_funding_trn']<=max(0.,r['C_government_net_additional_resource_trn']-r['fund_income_trn'])+1e-8
  eq(r['C_cash_trn'],r['C_earmarked_funding_trn'])
checks+=['positive-resource C payment and competing fund edge scenarios']
# Replay into temporary directory; no tracked output overwritten.
with tempfile.TemporaryDirectory(prefix='spe_vat_replay_') as td:
 m.run(P/'Inputs.json',td)
 replay=[]
 for f in sorted(Path(td).iterdir()):
  assert f.read_bytes()==(P/f.name).read_bytes(),f.name
  replay.append(dict(file=f.name,size=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
checks+=['all numerical outputs byte-identical on fresh execution','720 old/extra-zero regression cells and unchanged population/labor (model assertions)']
print(json.dumps(dict(status='PASS',checks=checks,replayed_outputs=replay),indent=2))
