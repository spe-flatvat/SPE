#!/usr/bin/env python3
"""Reclassify the same fixed SFA between cash transactions and remaining adjustment.
Native policy dynamics are inherited unchanged. q is a scenario, not an estimate.
"""
import argparse,copy,csv,hashlib,importlib.util,json,math,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PREV='handoff/chatgpt-n3-transition-financing-full-dynamics-20261122';ROB='handoff/chatgpt-n3-gdp-robustness-fiscal-dynamics-20261122';FD='handoff/chatgpt-national-fiscal-closure-20261121';PIN='423924065a4bb2a0d2e745a3489a3dbae936de2f';REQUEST='82525955b57dc1166fa17bfb4e3157a30b7b1133'
def module(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def rd(p):return list(csv.DictReader(p.open()))
def n(r,k):return float(r.get(k) or 0.)
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
T=module('fixed_transition',ROOT/PREV/'N3_Transition_Reproduce.py')
def spec(cid,q=0.,**kw):
 flags=dict(vat_dynamic=True,medical_dynamic=True,medical_VAT_scope=True,estate_dynamic=True)
 s=T.spec(cid,cash_basis='CASH_ONLY',**flags);s.update(q=q,cash_partition='TOTAL_RESIDUAL',asset_channel='UNIDENTIFIED_BELOW_LINE',use_other_assets=False,q_central=0.,q_local=0.);s.update(kw);return s
class Runner(T.Runner):
 def __init__(self,root,out):
  super().__init__(root,out);self.sfa_bridge=[];self.partition={}
  for y in range(2026,2041):
   o=self.official[y];p=self.official[y-1];rc=o['central_debt_end_trn']-p['central_debt_end_trn']+o['central_balance_trn'];rl=o['local_debt_end_trn']-p['local_debt_end_trn']+o['local_balance_trn'];total=self.fb[y]['stock_flow_adjustment_unallocated_trn'];self.partition[y]=dict(central=rc,local=rl,rounding=total-rc-rl)
 def channel_start(self,s):
  super().channel_start(s);self.other_assets=0.;self.other_sale=0.;self.sfa_rows=[]
 def cash_part(self,s,y,sfa):
  if s['cash_partition']=='SECTOR' and y<=2040:return s['q_central']*max(0.,self.partition[y]['central'])+s['q_local']*max(0.,self.partition[y]['local'])
  return s['q']*max(0.,sfa)
 def cash_budget(self,s,y,pb,interest,sfa,assets):
  cost=self.cash_part(s,y,sfa);cash=max(0.,pb-interest-cost);available=max(0.,assets) if s['use_assets'] else 0.
  if s['asset_channel']=='FINANCIAL_ASSET_EXCHANGE' and s['use_other_assets'] and y>=2030:available+=self.other_assets
  repay=min(self.bridge_outstanding,self.bridge_used/max(1,s['repay_end']-s['repay_start']+1)) if s['repay_start']<=y<=s['repay_end'] else 0.
  self.repay_requirement=repay;allowance=min(s['bridge_cap'],max(0.,s['bridge_total_cap']-self.bridge_used)) if s['bridge_start']<=y<=s['bridge_end'] else 0.
  self.current_allowance=allowance
  return max(0.,cash+available-repay)+(0. if s['min_to_SQ'] else allowance)
 def finalize_room(self,s,y,z,room,evalroom,interest,sfa,assets):
  z,room=super().finalize_room(s,y,z,room,evalroom,interest,sfa,assets);cost=self.cash_part(s,y,sfa);begin_other=self.other_assets;sale=0.
  if s['asset_channel']=='FINANCIAL_ASSET_EXCHANGE' and s['use_other_assets'] and y>=2030:
   sale=min(begin_other,max(0.,z['spend']-(z['pbpre']-interest-cost)-assets))
  acquisition=cost if s['asset_channel']=='FINANCIAL_ASSET_EXCHANGE' else 0.
  self.other_assets=begin_other+acquisition-sale;self.other_sale=sale
  e=self.extra_map[y];paid=min(e['repayment_requested_trn'],max(0.,z['pbpre']-interest-cost+sale-z['spend']));self.bridge_outstanding+=e['scheduled_bridge_repayment_reserved_trn']-paid
  e.update(scheduled_bridge_repayment_reserved_trn=paid,unserved_repayment_trn=e['repayment_requested_trn']-paid,bridge_authority_outstanding_trn=self.bridge_outstanding,actual_new_cash_need_after_assets_trn=max(0.,z['spend']-(z['pbpre']-interest-cost+sale)-assets))
  self.sfa_rows.append(dict(case=s['case'],year=y,q=s['q'],cash_partition=s['cash_partition'],asset_channel=s['asset_channel'],SFA_total_boundary_residual_trn=sfa,SFA_cash_need_assumed_trn=cost,SFA_remaining_stock_adjustment_trn=sfa-cost,identified_cash_need_trn=None,unallocated_original_SFA_trn=sfa,hypothetical_other_asset_begin_trn=begin_other,hypothetical_other_asset_acquisition_trn=acquisition,hypothetical_other_asset_sale_trn=sale,hypothetical_other_asset_end_trn=self.other_assets,legal_liquidity_verified=False,official_q_estimate=False))
  return z,room

def install_runtime(out):
 T.install_runtime(out);source=(out/'Resolved_Transition_Simulate.py.txt').read_text()
 def sub(old,new):
  nonlocal source
  assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
 sub("sqz=self.fp.finance(ssqdebt,ssqassets,sqpb,sqinterest,sfa,s['rollover'])", "cash_cost=self.cash_part(s,y,sfa);remaining_sfa=sfa-cash_cost\n  sqz=self.fp.finance(ssqdebt,ssqassets,sqpb-cash_cost,sqinterest,remaining_sfa,s['rollover'])")
 sub("fin=self.fp.finance(debt,assets,pb,interest,sfa,s['rollover'])", "fin=self.fp.finance(debt,assets,pb-cash_cost+self.other_sale,interest,remaining_sfa,s['rollover'])")
 sub("+pb-interest-sfa)", "+pb-interest-sfa+self.other_sale)")
 sub("+fin['CL_gross_redemption_with_assumed_refinancing_trn']-sfa)", "+fin['CL_gross_redemption_with_assumed_refinancing_trn']-remaining_sfa)")
 sub("self.ck(pre+'asset_identity'", "self.ck(pre+'asset_identity'") if "self.ck(pre+'asset_identity'" in source else None
 sub("self.connections.extend(self.local_connection)", "self.sfa_bridge.extend(self.sfa_rows)\n self.connections.extend(self.local_connection)")
 # Record both stock interpretations and independent cash checks for every year.
 sub("closure.append(c)", "c.update(SFA_cash_need_trn=cash_cost,SFA_remaining_adjustment_trn=remaining_sfa,cash_after_SFA_before_financing_trn=pb-interest-cash_cost+self.other_sale,other_asset_sale_trn=self.other_sale,other_financial_assets_hypothetical_trn=self.other_assets,net_debt_cash_only_trn=debt-assets,net_debt_including_hypothetical_assets_trn=debt-assets-self.other_assets,PB_excludes_below_line_SFA_cash=True,actual_total_bond_issue=None)\n  if record:\n   self.ck(s['case']+str(y)+':treasury_cash',pb-interest-cash_cost+self.other_sale+fin['CL_new_cash_borrowing_candidate_trn']-fin['CL_cash_surplus_debt_redemption_candidate_trn']-(assets-abegin))\n   self.ck(s['case']+str(y)+':SFA_single_classification',cash_cost+remaining_sfa-sfa)\n   self.ck(s['case']+str(y)+':debt_stock',debt-dbegin-fin['CL_new_cash_borrowing_candidate_trn']+fin['CL_cash_surplus_debt_redemption_candidate_trn']-remaining_sfa)\n  closure.append(c)")
 ns=dict(T.previous.__dict__);exec(compile(source,'isolated_sfa_runtime.py','exec'),ns);Runner.simulate=ns['simulate'];(out/'Resolved_SFA_Simulate.py.txt').write_text(source)

def run(root,out):
 out.mkdir(parents=True,exist_ok=True);install_runtime(out);r=Runner(root,out);annual=[];ledger=[];defs=[];summ=[];cache={};bounds=[];receipts=[]
 for f in sorted((root/PREV).iterdir()):
  if not f.is_file():continue
  path=str(f.relative_to(root));b=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);assert f.read_bytes()==b;receipts.append(dict(commit=PIN,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 for path in [FD+'/Official_Fiscal_Baseline_2025_2040.csv',FD+'/Statistical_Cell_Map.csv',FD+'/CAO_202607_Projections.xlsx',FD+'/National_Fiscal.py',ROB+'/Fiscal_Official_Baseline_Boundary_Map.csv','handoff/chatgpt-n3-sfa-cash-reconciliation-request-20261122/SPE_Work_N3_SFA_Cash_Needs_Reconciliation_Request_20261122.md']:
  b=subprocess.check_output(['git','show',REQUEST+':'+path],cwd=root);assert (root/path).read_bytes()==b;receipts.append(dict(commit=REQUEST,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 def execute(s):
  a,l,b=r.simulate(s);annual.extend(a);ledger.extend(l);defs.append(s);z=T.previous.summary(s,a,l);z.update(gap2030=next(x['GDP_minus_SQ_trn'] for x in a if x['year']==2030),cash_SFA_cumulative_trn=sum(x['SFA_cash_need_trn'] for x in l),cash_new_borrow_2030_onward_trn=sum(x['new_cash_borrowing_trn'] for x in l if x['year']>=2030),binding_years=';'.join(str(x['year']) for x in r.extra_ledger if x['case']==s['case'] and x['earliest_cash_constraint_binding']),q=s['q'],asset_channel=s['asset_channel'],financial_assets_other2055=r.other_assets);summ.append(z);cache[s['case']]=(a,l,b);return z
 for q in [0.,.25,.5,.75,1.]:execute(spec('Q'+str(int(q*100)),q))
 # A reference preserving the predecessor's accounting display, never recomputed as fact.
 stress=dict(tail='SQ_NOMINAL',ss_growth=.03,sfa_tail='PLUS1GDP',backfill=True,interest_mode='ALL_STOCK',rate=.04,rollover=.2)
 for q in [0.,.5,1.]:execute(spec('STRESS_Q'+str(int(q*100)),q,**stress))
 for q in [.25,.5,1.]:
  execute(spec('MIN_SQ_Q'+str(int(q*100)),q,min_to_SQ=True,bridge_cap=20.,bridge_total_cap=20.))
  execute(spec('CASH_ASSETS_Q'+str(int(q*100)),q,use_assets=True))
 execute(spec('LOCAL_RESIDUAL_CASH',cash_partition='SECTOR',q_local=1.))
 execute(spec('CENTRAL_RESIDUAL_CASH',cash_partition='SECTOR',q_central=1.))
 execute(spec('ASSET_EXCHANGE_Q50',.5,asset_channel='FINANCIAL_ASSET_EXCHANGE'))
 execute(spec('ASSET_SELL_Q50',.5,asset_channel='FINANCIAL_ASSET_EXCHANGE',use_other_assets=True))
 # 2041+ hypotheses from preceding work, not official observations.
 execute(spec('MEAN5_Q50',.5,sfa_tail='MEAN5'))
 execute(spec('GDP1_Q50',.5,sfa_tail='PLUS1GDP'))
 # Hold the macro path fixed to verify q reclassification alone does not create debt.
 execute(spec('FIXED_SPEND_Q0',0.,room_mode='FIXED_PRIMARY'))
 execute(spec('FIXED_SPEND_Q100',1.,room_mode='FIXED_PRIMARY'))
 for x,y in zip(cache['FIXED_SPEND_Q0'][0],cache['FIXED_SPEND_Q100'][0]):
  for k in ['real_GDP_trn','CL_debt_candidate_trn','CL_assets_candidate_trn']:r.ck('reclassification_neutral_fixed_spend:'+str(x['year'])+k,x[k]-y[k],3e-6)
 prior={(x['case'],int(x['year'])):x for x in rd(root/PREV/'N3_Transition_Financing_Case_Comparison.csv')}
 # q=0 and q=1 preserve the earlier macro/debt paths, but q=1 corrects gross cash flows.
 for new,old in [('Q0','ALL_CASH_ONLY'),('Q100','ALL_DEBT_LIMIT'),('STRESS_Q0','ALL_CASH_STRESS')]:
  for a in cache[new][0]:
   for k in ['real_GDP_trn','total_tax_diagnostic_proxy_trn','CL_PB_candidate_trn','CL_debt_candidate_trn']:r.ck('limited_prior_reproduction:'+new+str(a['year'])+k,a[k]-n(prior[old,a['year']],k),3e-6)
 # 2030 and all-years endpoints are tested separately.
 probes=[]
 for target in ['2030','ALL']:
  def test(q):
   a,l,b=r.simulate(spec('SEARCH',q),record=False);score=next(z['GDP_minus_SQ_trn'] for z in a if z['year']==2030) if target=='2030' else min(z['GDP_minus_SQ_trn'] for z in a);return score,a,l
  scores=[]
  for i in range(21):
   score,a,l=test(i/20);scores.append(score);probes.append(dict(target=target,q=i/20,score_GDP_trn=score,all_years=all(z['GDP_minus_SQ_trn']>=-1e-7 for z in a)))
  r.ck('q_monotonic_grid:'+target,sum(max(0.,b-a) for a,b in zip(scores,scores[1:])),2e-6)
  lo=0.;hi=1.
  for _ in range(26):
   mid=(lo+hi)/2
   if test(mid)[0]>=-1e-7:lo=mid
   else:hi=mid
  for label,q in [('PASS',lo),('FAIL',hi)]:
   s=spec('BOUND_'+target+'_'+label,q);z=execute(s);row=dict(target=target,side=label,q=q,q_width=hi-lo,all_years_SQ=z['all_years_SQ'],gap2030=z['gap2030'],below_years=z['below_years'],worst_year=z['worst_year'],worst_gap=z['worst_gap_trn'],debt2055=z['debt2055'],cash_need2030=q*max(0.,r.fb[2030]['stock_flow_adjustment_unallocated_trn']),q_is_estimated=False);bounds.append(row)
 # Supplemental q root for the stress path: do not infer any q can rescue it.
 bounds.append(dict(target='STRESS_ALL',side='FAIL_AT_Q0',q=0.,all_years_SQ=False,below_years=next(z['below_years'] for z in summ if z['case']=='STRESS_Q0'),q_is_estimated=False))
 ids={s['case'] for s in defs};sf={(z['case'],z['year']):z for z in r.sfa_bridge if z['case'] in ids};extra={(z['case'],z['year']):z for z in r.extra_ledger if z['case'] in ids};ai={(z['case'],z['year']):z for z in annual};combined=[]
 for l in ledger:
  key=l['case'],l['year'];x=sf[key];a=ai[key];e=extra[key];z={**l,**{k:v for k,v in x.items() if k not in l},**{k:v for k,v in e.items() if k not in l and k not in x}}
  z.update(GDP_minus_SQ_trn=a['GDP_minus_SQ_trn'],PB_cash_proxy_trn=l['PB_trn']-l['interest_trn'],actual_cash_balance_verified=False)
  base0=cache['Q0'][1][l['year']-2026]
  z.update(new_borrowing_change_vs_q0_trn=l['new_cash_borrowing_trn']-base0['new_cash_borrowing_trn'],redemption_reduction_vs_q0_trn=base0['cash_debt_redemption_trn']-l['cash_debt_redemption_trn'],cash_asset_draw_change_vs_q0_trn=l['asset_draw_trn']-base0['asset_draw_trn'],government_spend_change_vs_q0_trn=l['government_spend_trn']-base0['government_spend_trn'],debt_change_vs_q0_trn=l['debt_end_trn']-base0['debt_end_trn'])
  if l['case'].startswith('MIN_SQ_Q'):
   baseline=cache[l['case'].replace('MIN_SQ_','')][1][l['year']-2026]
   z.update(new_borrowing_increment_for_SQ_vs_same_q_trn=l['new_cash_borrowing_trn']-baseline['new_cash_borrowing_trn'],government_spend_increment_for_SQ_vs_same_q_trn=l['government_spend_trn']-baseline['government_spend_trn'])
  combined.append(z)
  r.ck('cash_allocation_asset:'+str(key),x['hypothetical_other_asset_end_trn']-x['hypothetical_other_asset_begin_trn']-x['hypothetical_other_asset_acquisition_trn']+x['hypothetical_other_asset_sale_trn'])
  r.ck('cash_uses_identity:'+str(key),l['PB_trn']-l['interest_trn']-l['SFA_cash_need_trn']+l['other_asset_sale_trn']+l['new_cash_borrowing_trn']-l['cash_debt_redemption_trn']-(l['assets_end_trn']-l['assets_begin_trn']))
  if sfaq:=next((s for s in defs if s['case']==l['case']),None):
   if not sfaq['min_to_SQ'] and sfaq['room_mode']=='CASH_NEUTRAL':r.ck('spend_resource_limit:'+str(key),max(0.,l['government_spend_trn']-(l['cash_budget_after_interest_SFA_trn'])),1e-6)
 # Exact 2030 source bridge and geographic residuals, including rounding only as rounding.
 for y in range(2026,2041):r.ck('official_SFA_sector_sum:'+str(y),r.partition[y]['central']+r.partition[y]['local']+r.partition[y]['rounding']-r.fb[y]['stock_flow_adjustment_unallocated_trn'])
 dump(out/'N3_SFA_GDP_Annual_Comparison_2026_2055.csv',annual);dump(out/'N3_SFA_Cash_Debt_Bridge_2026_2055.csv',combined);dump(out/'N3_SFA_Case_Summary.csv',summ);dump(out/'N3_SFA_Case_Definitions.csv',defs);dump(out/'N3_SFA_Cash_Sensitivity_Boundaries.csv',bounds);dump(out/'Boundary_Monotonicity_Probes.csv',probes);dump(out/'Detail_2029_2032.csv',[z for z in combined if 2029<=z['year']<=2032]);classify(r,out)
 (out/'Input_Source_Receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 result=dict(status='PASS_CONDITIONAL_SFA_MAPPING' if not r.checks else 'FAIL',checks=r.counter,failed=len(r.checks),failures=r.checks,cases=len(defs),annual_rows=len(annual),prior_checks_reused=25478,earlier_checks_reused=[35281,12311],prior_full_audit=False,SFA_cash_q_identified=False,geographic_residual_identified=True,official_future_SFA_cash_breakdown_unallocated=True,double_counting_excluded=True,native_dynamics_preserved=True,general_government_closed=False,policy_adopted=False,source_originals_modified=False)
 (out/'N3_SFA_Verification.json').write_text(json.dumps(result,indent=2)+'\n');report(out,summ,bounds,result)
 print(json.dumps(result));assert not r.checks,r.checks[:8]

def classify(r,out):
 rows=[];cells=rd(r.root/FD/'Statistical_Cell_Map.csv');ci={(int(x['year']),x['metric']):x['cell'] for x in cells}
 url='https://www5.cao.go.jp/keizai2/keizai-syakai/shisan/keisuuhyo.xlsx';note='https://www5.cao.go.jp/keizai2/keizai-syakai/shisan/2607hontai.pdf'
 for y in range(2026,2056):
  f=r.fb[y];parts=r.partition.get(y,{});source='OFFICIAL_FORECAST_BOUNDARY_RECONSTRUCTION' if y<=2040 else 'UNADOPTED_TAIL_ASSUMPTION_ZERO'
  for key,amount in [('TOTAL',f['stock_flow_adjustment_unallocated_trn']),('CENTRAL',parts.get('central')),('LOCAL',parts.get('local')),('AGGREGATION_ROUNDING',parts.get('rounding'))]:
   if y>2040 and key!='TOTAL':continue
   prefix={'TOTAL':'CL','CENTRAL':'central','LOCAL':'local'}.get(key)
   coords=''
   if prefix and y<=2040:coords=';'.join(str(z) for z in [ci.get((y-1,prefix+'_debt_end')),ci.get((y,prefix+'_debt_end')),ci.get((y,prefix+'_balance'))])
   evidence='CALCULATED_FROM_FIXED_OFFICIAL_STOCK_AND_BALANCE' if y<=2040 else '2040_NOMINAL_FLOW_HOLD_ZERO_SFA_IS_NOT_OFFICIAL'
   rows.append(dict(year=y,classification=key,amount_trn=amount,status=source,evidence=evidence,source_url=url,source_sheet='財政の詳細計数表（現状投影・長期）',source_cells=coords,unit='TRILLION_YEN_NOMINAL_FISCAL_YEAR',retrieved_date='2026-11-22',known_cash_amount_trn=None,cash_need_ratio_estimate=None,unallocated_cash_nature=True,causal_amount_allocation_verified=False))
  candidates=[
   ('FINANCIAL_ASSET_ACQUISITION_OR_DEPOSIT','https://www5.cao.go.jp/keizai3/econome/ef2rrrrrr-equ.pdf','M_FAGLD/M_FLGLD and Z_LGFND/Z_RLGFND','Official local fund/financial asset linkage exists; amount of this residual attributable to each asset is not supplied'),
   ('DEBT_VALUATION_OR_PREMIUM','https://www.boj.or.jp/statistics/outline/exp/faqsj.htm','Stock-flow-adjustment and valuation definitions; compare model Z_EXPGBRF','Mechanisms in broader statistics only; not identified as a cause or amount in this particular future residual'),
   ('BUDGET_EXECUTION_TIMING',note,'footnote26 printed pp14-15','Budget-year issuance vs expenditure execution timing explained; future annual attributable amount absent'),
   ('INTERNAL_TRANSFER_OR_COVERAGE_DIFFERENCE',note,'footnote24 printed p13','Limited public debt boundary confirmed; do not fabricate a transfer or coverage adjustment amount'),
   ('REMAINING_UNIDENTIFIED_CAUSES',url,'fixed official table residual','No causal amount allocation; record unknown rather than invent a cash or noncash decomposition')]
  for candidate,curl,section,evidence in candidates:
   rows.append(dict(year=y,classification=candidate,amount_trn=None,status='UNALLOCATED_NO_CAUSAL_AMOUNT_ASSIGNED',evidence=evidence,source_url=curl,source_section=section,unit='TRILLION_YEN_NOMINAL_FISCAL_YEAR',retrieved_date='2026-11-22',known_cash_amount_trn=None,cash_need_ratio_estimate=None,unallocated_cash_nature=True,causal_amount_allocation_verified=False))
 dump(out/'N3_SFA_Classification_and_Evidence.csv',rows)
 detail=[]
 for y,p in r.partition.items():
  o=r.official[y];b=r.official[y-1];detail.append(dict(year=y,CL_debt_begin_trn=b['CL_debt_end_trn'],CL_debt_end_trn=o['CL_debt_end_trn'],CL_balance_trn=o['CL_balance_trn'],CL_PB_trn=o['CL_PB_trn'],CL_net_interest_trn=o['CL_PB_trn']-o['CL_balance_trn'],CL_SFA_trn=r.fb[y]['stock_flow_adjustment_unallocated_trn'],central_debt_change_trn=o['central_debt_end_trn']-b['central_debt_end_trn'],central_balance_trn=o['central_balance_trn'],central_boundary_residual_trn=p['central'],local_debt_change_trn=o['local_debt_end_trn']-b['local_debt_end_trn'],local_balance_trn=o['local_balance_trn'],local_boundary_residual_trn=p['local'],rounding_aggregation_residual_trn=p['rounding'],causal_financial_asset_allocation=None,official_future_cash_need=None))
 dump(out/'Official_SFA_Reconstruction_2026_2040.csv',detail)

def report(out,summ,bounds,v):
 ix={z['case']:z for z in summ};b=next(z for z in bounds if z['target']=='ALL' and z['side']=='PASS')
 lines=['# N3 SFA実体・現金需要とGDP成立条件','DRAFT / NON-CANONICAL / ISOLATED EXECUTION / NO POLICY ADOPTION',
 '## 判定','①算術整合：'+('PASS' if not v['failed'] else 'FAIL')+'。②モデル内の全期間SQ以上：qに条件付けて成立。③SFA実体・全国財政・較正を含む頑健性：未確認。SFAの国／地方という数値的発生境界は分けられたが、将来の費目別現金需要額は未配賦。qは推計値でも確率でもない。',
 '## 定義・公式証拠','本件のR（従来SFA）は年度末の国地方公債等残高差＋同年度国地方財政収支。赤字の収支は負、債務増は正。日本のFY、名目兆円。これは日銀の調整表や一般政府の全債務について定義されたSFAと同じ対象ではなく、二つの公表系列を接続した境界残余である。',
 '内閣府2026年7月試算本文・脚注24/26（印刷pp13〜15、PDF pp15〜17）を確認。債務対象には財投債・政府短期証券等が含まれない。公債等残高への予算年度の発行反映とPBの執行時認識の時間差があり、推計後年度のその他要因は主として地方黒字の一部を積立へ回す仮定に由来する説明がある。2026年の前倒債発行上限の影響にも言及がある。ただし本件の2030年13.9兆円の費目別配賦表ではない。主本文は復興等を除く表が中心で、本件は計数表の含む系列を使うため、説明の存在を含む系列の金額配賦へ読み替えない。',
 '公式の経済財政モデル方程式・変数表、財務省の債務対象の比較、日本銀行のフロー／残高／調整の説明も確認。金融資産、評価差、発行条件、内部移転、対象範囲・認識時点は区別が必要だが、一般論だけで残余の金額をこれらへ配賦していない。将来SFAの現金需要を0または全額と確定できる証拠は得られていない。参照表と取得原本SHAはPublic_Source_References.md / Public_Source_Receipts.json。',
 '## 2030年の13.9兆円と12.051兆円','固定公式見通しの2030年国地方残高は1371.9→1400.5兆円、財政収支−14.7兆円。R=28.6−14.7=13.9兆円。国は残高1232.3→1265.3、収支−27.3なので国残余5.7。地方は139.6→135.2、収支＋12.6なので地方残余8.2。合計13.9。この8.2を全額自由な基金・預金と確定したわけではない。2029/2031/2032も独立再構成し、合算丸め差は別列にした。',
 'N3での2030年PB候補29.151280−純利払候補17.100000=12.051280兆円は、国地方SNA系列へ政策差を接続した収支proxy。公式の国庫・自治体現金預金の実測残高ではないため、現金黒字として利用可能な額が確定したという前回説明への留保を明確化する。',
 '## 現金需要の再分類と二重計上防止','未配賦正Rの仮定現金部分F=q×max(R,0)。PBは非金融収支候補のまま変更しない。資金収支へFを一度だけ入れ、残るストック調整をR−Fへ減らす。金融資産取得・預金振替等のbelow-line現金用途という条件付き接続であり、すでにPBへ含まれる経常支出をもう一度控除する処理ではない。既存PBに含まれる費目と判明した場合にはこのq感度へ再追加しない。',
 '現金恒等式：Δ現金=PB−利払−F＋仮定資産売却＋新規現金借入−現金償還。債務恒等式：Δ債務=新規現金借入−現金償還＋(R−F)。既存現金の取崩し→残る需要の借入、余剰は償還→債務消滅後の現金積増という既存順序を継承。R全額を債務へ加えてからFを別の借入として再加算しない。固定支出経路でqだけ変えるとGDP・債務が不変となる中立性を検証した。',
 '正のRに対する仮定Fの識別範囲を限定する。Qの残部を確定評価差と呼ばず、未配賦ストック調整のまま残した。','q=1のGDP・債務は前回ALL_DEBT_LIMITを再現するが、総現金借入・償還の内訳は異なる。前回のq相当条件は支出枠だけを制限する保守的診断であり、SFA現金用途への支払いを台帳に再分類した実行ではなかった。q=0は前回ALL_CASH_ONLYを再現する。いずれも原本を変更していない。',
 '## 主結果（GDP−SQは実質兆円、借入・債務は名目兆円）','| ケース | 2030 | 2035 | 2044 | 2055 | SQ割れ年数 | 最悪年 | 最悪差 | 2055債務 | 2030年以降新規現金借入合計 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for cid in ['Q0','Q25','Q50','Q75','Q100','MIN_SQ_Q25','MIN_SQ_Q50','MIN_SQ_Q100','CASH_ASSETS_Q50','LOCAL_RESIDUAL_CASH','CENTRAL_RESIDUAL_CASH','ASSET_EXCHANGE_Q50','ASSET_SELL_Q50','MEAN5_Q50','GDP1_Q50','STRESS_Q0','STRESS_Q50','STRESS_Q100']:
  z=ix[cid];lines.append(f"| {cid} | {z['gap2030']:+.6f} | {z['gap2035']:+.6f} | {z['gap2044']:+.6f} | {z['gap2055']:+.6f} | {z['below_years']} | {z['worst_year']} | {z['worst_gap_trn']:+.6f} | {z['debt2055']:.6f} | {z['cash_new_borrow_2030_onward_trn']:.6f} |")
 lines+=['公表方程式のM_FAGLD/M_FLGLDとZ_LGFNDは、地方積立と金融資産・負債を別に記録する構造を確認できる。ただし将来の全外生値・調整項がなく、方程式だけから8.2兆円を特定預金へ配賦しない。既存2024年末SNAには中央43.308兆円・地方49.974兆円の現金預金があるが、2025年末への橋渡しと用途拘束を確認できないため初期残高へ注入していない。Historical_Currency_Deposits_2024.csvにセルを記録。','## 成立境界',f"全期間の成功側最大qは {b['q']:.10f}、同年2030年Fは {b['cash_need2030']:.9f}兆円。隣接失敗側との幅は{b['q_width']:.3g}。2030年のみの境界を別に探索しBoundary CSVへ記録。qの0〜1を0.05刻みで単調性確認後26回二分探索した。GDP差の判定許容は−1e−7兆円。この境界は所与のG50/I25・企業75%、国内比0.8・公共資本係数0.1、前回のネイティブ部分動学・財政前提に依存し、公的推計qではない。",'| 判定対象 | 側 | q | 2030年現金需要 | SQ割れ年数 | 最悪差 |','|---|---|---:|---:|---:|---:|']
 for z in bounds:
  if z['target']!='STRESS_ALL':lines.append(f"| {z['target']} | {z['side']} | {z['q']:.10f} | {z['cash_need2030']:.9f} | {z['below_years']} | {z['worst_gap']:+.9f} |")
 lines+=['元公表値には0.1兆円単位の丸めがある。二分探索の細かい幅は数値解法の精度であり、実際のqの統計精度・信頼区間ではない。','MIN_SQは2030〜2032年だけ追加調達を許し、所与配分で不足する政府実執行を逐年最小化する未採用候補。総借入との差は既存黒字・償還減少を優先した結果。前回の約11.185兆円は支出権限であり、本件ではSFA現金需要を実際に支払うための借入を別計算する。借入後の利払い、2035〜2040年の補償的償還枠、期末債務・現金・仮定総発行を同時計算。全期間最適化の大域最小ではない。',
 '資金源の比較はBridgeのnew_borrowing_change_vs_q0、redemption_reduction_vs_q0、cash_asset_draw_change_vs_q0で表示。償還差は符号付きであり、支出削減で逆に償還が増える年もある。MINケースは同じqの無追加調達ケースとの差も別列にした。','金融資産活用は二種類。CASH_ASSETSは実際のモデル内期首現金だけを使う（移行期初期残高はゼロ）。ASSET_EXCHANGEはFが金融資産取得であったと仮定して同額の非現金金融資産を積み立て、ASSET_SELLはその実在する仮定残高内だけ2030年以降に売却する。公的証拠から確認された売却可能な政府資産ではなく、地方積立を国へ移す権限・流動性は未確認。資産売却をPB歳入や新GDPへ直接加算しない。通常の純債務列は国地方候補債務−モデル現金だけで、一般政府純債務ではない。仮定の他金融資産を含む列は別にした。',
 '## 残る未配賦・実行限界','公式表から2026〜2040年のRと国地方別残余は再構成できた。地方積立・認識時点差・2026前倒債という機序の公的説明は取得できた。一方、将来の実際の資産取得／預金／評価差／調整の年次金額、支出執行予定、既存現金・満期別借換と地域間の流用権限は未配賦。したがって識別済み現金額を0と記録せずnullとした。qは未配賦全額についての感度であり、識別済み費目の金額ではない。',
 '2041〜2055年ゼロ・2036〜2040平均・GDP比1%は前回の未採用仮定を継承。SNA国地方収支から現金への発生主義／認識時点調整、一般政府社会保障基金・内部移転・財投・対象外債務、実際の満期別発行、全国課税基礎較正は未完了。完全N3動学も未完了。③は未確認であり、q境界が精密でも実現可能性の証明ではない。',
 f"新規{v['cases']}ケース・{v['annual_rows']}年次、算術等チェック{v['checks']}件・失敗{v['failed']}件。前回25,478件等を再利用し全件再監査はしていない。q再分類、GDP年次ループ、源泉使途、債務・現金、仮定資産、限定基準再現、境界・単調性を検証。",'再現：`python3 handoff/chatgpt-n3-sfa-cash-reconciliation-20261122/N3_SFA_Reproduce.py --root . --outdir /tmp/n3-sfa-replay`。元エンジン・税率・控除・本文・前回原本は変更せず、隔離ランタイムのみ新規作成。暫定改訂版・正式採用・PR/mergeなし。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。']
 (out/'SPE_N3_SFA_Cash_Reconciliation_Report_DRAFT_20261122.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--outdir',type=Path,required=True);z=a.parse_args();run(z.root.resolve(),z.outdir.resolve())
