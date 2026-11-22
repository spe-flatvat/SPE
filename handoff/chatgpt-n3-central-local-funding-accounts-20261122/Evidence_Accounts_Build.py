#!/usr/bin/env python3
"""Build official account maps and inventory from retrieved source bytes.
Run after N3_Central_Local_Reproduce.py. Original downloaded bytes stay in cache;
receipts record their fingerprints. No future availability is inferred from stocks.
"""
import argparse,csv,json,hashlib,re,urllib.request,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
P=Path(__file__).resolve().parent
class Table(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None;self.text=[]
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  if t in ['td','th']:self.cell=''
 def handle_data(self,d):
  self.text.append(d)
  if self.cell is not None:self.cell+=d
 def handle_endtag(self,t):
  if t in ['td','th'] and self.row is not None and self.cell is not None:self.row.append(' '.join(self.cell.split()));self.cell=None
  if t=='tr' and self.row:self.rows.append(self.row);self.row=None

def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def main(out,cache):
 receipts=json.loads((out/'Public_Source_Receipts.json').read_text());src={r['id']:r for r in receipts};checked=[]
 def data(k):
  r=src[k];p=cache/Path(r['scratch_path']).name
  if not p.exists():p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(urllib.request.urlopen(r['url'],timeout=60).read())
  b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256'],('SOURCE_CHANGED',k)
  checked.append(k);return b
 def html(k,enc='utf-8'):
  h=Table();h.feed(data(k).decode(enc));return h
 def csvrows(k):
  b=data(k)
  try:t=b.decode('utf-8-sig')
  except UnicodeDecodeError:t=b.decode('cp932')
  return list(csv.reader(t.splitlines()))
 def inventory(sector,item,amount,source,location,date,status='OFFICIAL_OBSERVED',constraint='USES_AND_AUTHORITY_UNVERIFIED'):
  return dict(sector=sector,item=item,date=date,amount_trn=amount,unit='TRILLION_YEN_NOMINAL',evidence_status=status,source_id=source,source_url=src[source]['url'] if source in src else source,source_location=location,availability_2030_trn='unknown',confirmed_credit_lower_trn=0.,conditional_upper_trn='unknown',legal_authority='unknown',liquidity_2030='unknown',nonduplication='unknown',restriction=constraint,bridge_to_2026='unknown',retrieved_date='2026-11-23')
 inv=[];local=html('LOCAL_WHITEPAPER','shift_jis');text=' '.join(local.text)
 assert '29兆4,802億円' in text and '151兆964億円' in text
 funds=csvrows('LOCAL_FUNDS_TABLE');debt=csvrows('LOCAL_DEBT_TABLE');rev=csvrows('LOCAL_REVENUE_TABLE')
 # Parse embedded-newline labels using the full CSV text.
 import io
 raw=data('LOCAL_FUNDS_TABLE')
 try:funds=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
 except UnicodeDecodeError:funds=list(csv.reader(io.StringIO(raw.decode('cp932'))))
 for row in funds:
  if len(row)>3 and row[0].replace('\n','') in ['財政調整基金','減債基金','その他特定目的基金','合計']:
   inv.append(inventory('LOCAL',row[0].replace('\n',''),float(row[3].replace(',',''))/10000,'LOCAL_FUNDS_TABLE','第14表 FY2024末 計列; original 億円 /10000','2025-03-31',constraint='ORDINANCE_PURPOSE; REDEMPTION_RESERVE_EXCLUDES_BULLET_FUND; DO_NOT_ADD_TO_SNA_DEPOSITS'))
 inv+= [inventory('LOCAL','ordinary_account_debt_net_of_bullet_reserves',137.0991,'LOCAL_DEBT_TABLE','第12表 地方債現在高 計列 億円/10000','2025-03-31'),inventory('LOCAL','ordinary_account_debt_including_bullet_reserves',151.0964,'LOCAL_WHITEPAPER','第1部2(7)ア; this is debt NOT usable assets','2025-03-31'),inventory('LOCAL','bullet_redemption_reserve_corresponding_stock_difference',13.9973,'LOCAL_WHITEPAPER','151.0964-137.0991; derived boundary difference NOT unrestricted cash','2025-03-31','CALCULATED_BOUNDARY_DIFFERENCE'),inventory('LOCAL','bond_revenue_ordinary_account_FY2024',8.8506,'LOCAL_REVENUE_TABLE','第5表 地方債 令和6年度 億円/10000','FY2024','OFFICIAL_OBSERVED_FLOW')]
 assert any(x['item']=='合計' and abs(x['amount_trn']-29.4802)<1e-9 for x in inv)
 h=html('MOF_ACCOUNT_ASSETS');assert '20.2兆円' in ' '.join(h.text)
 for sector,item,amount in [('CENTRAL_GA','cash_deposits',20.2),('CENTRAL_DEBT_FUND','financial_assets_total',28.6),('CENTRAL_FILP','loans',124.8),('CENTRAL_FILP','cash_deposits',1.8),('CENTRAL_FX','cash_deposits',27.3),('CENTRAL_PENSION_ACCOUNT','cash_deposits',13.4)]:
  inv.append(inventory(sector,item,amount,'MOF_ACCOUNT_ASSETS','FY2024 会計別 主な資産; rounded; nonadditive across accounts','2025-03-31',constraint='ACCOUNT_PURPOSE_AND_CONSOLIDATION; NOT_SNA_CENTRAL_SECTOR'))
 # Exact debt fund financial statement values, validated against the fetched PDF text.
 pdf=data('DEBT_FUND_FY2024');import subprocess
 pdfpath=cache/Path(src['DEBT_FUND_FY2024']['scratch_path']).name
 txt=subprocess.check_output(['pdftotext','-layout',str(pdfpath),'-'],text=True)
 for marker in ['402,110','10,779,088','17,206,992']:assert marker in txt
 for item,amount,loc in [('cash_deposits',.402110,'附属明細書1(1)① 政府預金 402110百万円'),('BOJ_repo_loan',10.779088,'同③ 対日本銀行買現先 10779088百万円'),('securities_non_held_to_maturity',17.206992,'同②ア 17206992百万円')]:
  inv.append(inventory('CENTRAL_DEBT_FUND',item,amount,'DEBT_FUND_FY2024',loc+' /1000000','2025-03-31',constraint='REDEMPTION_USE; INTERNAL_TBILLS_NOT_EXTERNAL_WEALTH'))
 balancepdf=data('MOF_BALANCE_SHEET');balancepath=cache/Path(src['MOF_BALANCE_SHEET']['scratch_path']).name
 baltext=subprocess.check_output(['pdftotext','-layout',str(balancepath),'-'],text=True)
 assert '55.2' in baltext and '65.4' in re.sub(r'\s+','',baltext) and '3.9兆円' in baltext
 inv.append(inventory('CENTRAL_GA_SA_CONSOLIDATED','cash_deposits',55.2,'MOF_BALANCE_SHEET','FY2024末 現金・預金 row; previous FY2023末65.4; rounded','2025-03-31',constraint='AFTER_CLOSING_PERIOD_RECEIPTS_NOT_ACTUAL_MARCH31_BALANCE; NOT_SNA_CENTRAL'))
 inv.append(inventory('CENTRAL_TREASURY','actual_government_deposit_excluding_foreign',3.9,'MOF_BALANCE_SHEET','主な科目の特徴及び留意点①; accounting deposits55.2, excluding foreign33.6 are after closing period','2025-03-31',constraint='ACTUAL_TREASURY_BOUNDARY; NOT_SNA_CENTRAL; FUTURE_AUTHORITY_UNKNOWN'))
 gov=html('MOF_DEPOSITS_2025Q4');gt=' '.join(gov.text)
 for marker in ['5兆1,342億円','2兆1,575億円']:assert marker in gt
 inv+=[inventory('CENTRAL_TREASURY','BOJ_government_deposit',5.1342,'MOF_DEPOSITS_2025Q4','第3政府預金 前期末 FY2025 Q3末=2025-12-31; 億円/10000','2025-12-31'),inventory('CENTRAL_TREASURY','BOJ_government_deposit',2.1575,'MOF_DEPOSITS_2025Q4','第3政府預金 FY2025 Q4末; 億円/10000','2026-03-31')]
 # Narrow treasury boundary observed bridge, independent of SNA stocks.
 hist=[dict(sector='CENTRAL_TREASURY',period='2026Q1_calendar_FY2025Q4',cash_begin_trn=5.1342,private_cash_net_receipt_trn=27.0527,BOJ_cash_net_receipt_trn=-30.0294,cash_end_trn=2.1575,source_id='MOF_DEPOSITS_2025Q4',source_url=src['MOF_DEPOSITS_2025Q4']['url'],unit='TRILLION_YEN',status='OFFICIAL_OBSERVED_ROUNDED_DIFFERENT_BOUNDARY_FROM_SNA',bridge_to_SNA_central='unknown')]
 for z in hist:assert abs(z['cash_begin_trn']+z['private_cash_net_receipt_trn']+z['BOJ_cash_net_receipt_trn']-z['cash_end_trn'])<.00011
 dump(out/'Historical_Treasury_Cash_Bridge.csv',hist)
 # Forecast has an extra empty cell in 2026, stripped before numerical extraction.
 forecast=[]
 for row in html('MOF_FUND_FORECAST_2026').rows:
  row=[x for x in row if x]
  if len(row)<11 or not re.fullmatch(r'\(20\d\d\)',row[1]):continue
  year=int(row[1][1:-1]);vals=[float(x.replace(',',''))/10000 for x in row[2:]]
  keys=['required_redemption_trn','refinancing_receipts_trn','regular_discount_transfers_trn','GA_return_trn','investment_income_trn','total_sources_trn','fund_end_trn','debt_end_trn','interest_and_admin_trn']
  z=dict(year=year,**dict(zip(keys,vals)),status='OFFICIAL_HYPOTHETICAL_FORECAST_NOT_N3_OR_COMMITTED_BUDGET',source_url=src['MOF_FUND_FORECAST_2026']['url'],source_location='FY'+str(year)+' row; original 億円/10000',available_increment_trn='unknown',certified_free_fund_credit_trn=0.,scope='EXCLUDES_RECONSTRUCTION_GX_CHILD_SEMICONDUCTOR_AI; INCLUDES_PENSION_SPECIAL_BOND')
  z['sources_minus_redemption_rounding_trn']=z['total_sources_trn']-z['required_redemption_trn'];assert abs(z['sources_minus_redemption_rounding_trn'])<.011
  assert abs(sum(z[k] for k in keys[1:5])-z['total_sources_trn'])<.011
  forecast.append(z)
  if year<=2032:inv.append(inventory('CENTRAL_DEBT_FUND','hypothetical_year_end_fund',z['fund_end_trn'],'MOF_FUND_FORECAST_2026',z['source_location'],str(year)+'-FY-END','OFFICIAL_HYPOTHETICAL_FORECAST',constraint='REDEMPTION_BUFFER_NOT_FREE_INCREMENT; DIFFERENT_BASELINE'))
 assert len(forecast)==10
 # Existing SNA stock evidence is reused, kept separate from fiscal-year government accounts.
 for sec,amount in [('CENTRAL_SNA',43.308),('LOCAL_SNA',49.974)]:
  inv.append(inventory(sec,'currency_deposits_SNA',amount,'REUSED_ccadca9_Historical_Currency_Deposits_2024.csv','2024ss3_jp.xlsx stocks DR16/DS16/DT16/DU16; see fixed receipt','2024-12-31'))
 for y in range(2024,2033):
  for sec in ['CENTRAL','LOCAL']:
   inv.append(inventory(sec,'usable_cash_for_new_N3_execution','unknown','UNKNOWN','sector authority / liquidity / existing obligations bridge incomplete',str(y)+'-12-31','unknown'))
 dump(out/'N3_Central_Local_Cash_Asset_Inventory.csv',inv);dump(out/'MOF_Debt_Fund_Hypothetical_Forecast_2026_2035.csv',forecast)
 # Attach official future plan as separate-reference columns, never substitute into N3 flows.
 forecasts={x['year']:x for x in forecast};ledger=rd(out/'N3_Central_Local_Source_Use_Ledger_2026_2055.csv')
 for row in ledger:
  f=forecasts.get(int(row['year'])) if row['sector']=='CENTRAL' else None
  for key in ['required_redemption_trn','refinancing_receipts_trn','regular_discount_transfers_trn','fund_end_trn']:
   row['MOF_separate_reference_'+key]=f[key] if f else 'unknown'
  row['MOF_reference_status']='OFFICIAL_HYPOTHETICAL_DIFFERENT_BOUNDARY_NOT_N3_INPUT' if f else 'unknown'
 dump(out/'N3_Central_Local_Source_Use_Ledger_2026_2055.csv',ledger);dump(out/'Detail_2029_2032.csv',[x for x in ledger if 2029<=int(x['year'])<=2032])
 accounts=[
 ('CENTRAL','government_deposits','MOF_TREASURY','国庫収支(1)・主な国内指定預金','国庫は一般・特会等の資金管理境界。SNA中央政府と一致せず地方を対民収支に含む','国庫内振替は連結で相殺。国内指定預金への組替は新規歳入ではない','2030残高・支出権限unknown'),
 ('CENTRAL','temporary_surplus_cash','MOF_CASH_MANAGEMENT','国庫余裕金の繰替使用','一般会計の新支出へ恒久流用する制度と解釈しない','特会年度内、外為・財融1年内返還。予算総則の限度額に従う','恒久財源算入なし'),
 ('CENTRAL','GA_financial_assets','MOF_ACCOUNT_ASSETS','一般会計・特別会計資産概要','国の財務書類は発生主義参考。SNA現金預金と時点・境界が異なる','GA国債整理基金28.2と基金特会28.6を二重加算しない','用途・2025末橋渡し・2030売却予定unknown'),
 ('CENTRAL','redemption_fund','MOF_FUND_PURPOSE','設置目的・60年償還','整理基金と特会の歳入歳出・歳入歳出外経理を区別','特会法42条定率等繰入、46条借換、47条前倒','満期償還の任意不払いは償還抑制と別'),
 ('CENTRAL','bond_issuance','ISSUANCE_FY2026_REVISED','p1 発行根拠法別','FY2026補正後 総額183.8055/新規32.6975/借換135.7586/財投13.0兆円','財投債はCAO公債等外。年度間調整と暦年市場発行を区別','2030 N3発行枠ではない'),
 ('CENTRAL','fund_future_plan','MOF_FUND_FORECAST_2026','2030行・前提1-8','FY2030 要償還154.14/借換134.29/繰入等19.66/繰戻.01/運用.18/期末基金3兆円','公式仮定計算。CAO202607と異なる境界・前提。収入の全てに償還用途あり','3兆円の新支出利用は未確認'),
 ('LOCAL','ordinary_accounts_funds','LOCAL_FUNDS_TABLE','第14表 FY2024末','普通会計積立金29.4802、財調9.7786、減債3.0938、特定16.6078兆円','満期一括償還基金除外。SNA預金へ上乗せしない','各自治体条例・予算・用途確認必要'),
 ('LOCAL','ordinary_accounts_debt','LOCAL_WHITEPAPER','第1部2(7)ア・第12表','地方債137.0991、満期一括償還基金対応分を含む151.0964兆円','基金積立は公債費、対応分を債務残高から除く。現金償還・積立を区別','2030満期表・基金取崩予定unknown'),
 ('LOCAL','bond_revenue_and_transfers','LOCAL_REVENUE_TABLE','第5表 FY2024','地方債8.8506、地方交付税19.9346、国庫支出金20.1862兆円','地方交付税・国庫支出金は国地方統合で相殺。2030額へ外挿しない','新規移転権限・額unknown'),
 ('LOCAL','public_enterprise_and_fund_scope','LOCAL_WHITEPAPER','第1部2(7)オ','普通会計負担の企業債・交付税特会借入は普通会計地方債とは境界が違う','公営企業会計・SNA公的企業・一般政府を機械的統合しない','企業勘定連結・内部債権控除未了'),
 ('LOCAL','fund_legal_restrictions','LOCAL_AUTONOMY_LAW','本則241条、235条の3','基金は条例目的に拘束。一時借入は歳出予算内・年度歳入償還','地方財調でも国庫所有資金ではない。基金廃止等の個別手続未確認','全国一括流用不可とする入力'),
 ('LOCAL','debt_legal_restrictions','LOCAL_FINANCE_LAW','本則5条・5条の3','起債対象・協議等の制度制約あり。公共投資の対象適合と経常購入を区別','モデルG50/I25の全額を地方債で賄えるとはしない','自治体別起債枠未確認'),
 ('CENTRAL','expenditure_authority','FINANCE_LAW','本則4条','国債財源は財政法・特例法と年度予算の権限に従う','借換債収入を経常追加支出の自由財源としない','2030追加発行・支出予算未確認')]
 maps=[]
 for sec,item,sid,loc,bound,rule,unk in accounts:
  data(sid);maps.append(dict(sector=sec,account=item,source_id=sid,source_url=src[sid]['url'],version='FY2024_OUTTURN_OR_FY2026_PLAN_OR_RETRIEVED_LAW; see source_location',source_location=loc,unit='TRILLION_YEN_UNLESS_LEGAL_DEFINITION',retrieved_date='2026-11-23',account_boundary=bound,restriction_or_reconciliation=rule,unknown=unk,future_usable_cash_amount_trn='unknown'))
 dump(out/'N3_Central_Local_Official_Account_Map.csv',maps)
 # Symbolic transfer cancellation is an algebra check, not evidence of a real transfer.
 symbolic=[dict(term='central_to_local_T',central_cash_coefficient=-1,local_cash_coefficient=1,consolidated_coefficient=0,amount='unknown',status='ALGEBRA_ONLY_NOT_OBSERVED_TRANSFER'),dict(term='local_to_central_U',central_cash_coefficient=1,local_cash_coefficient=-1,consolidated_coefficient=0,amount='unknown',status='ALGEBRA_ONLY_NOT_OBSERVED_TRANSFER')]
 for x in symbolic:assert x['central_cash_coefficient']+x['local_cash_coefficient']==0
 dump(out/'Transfer_Consolidation_Algebra.csv',symbolic)
 for sid in src:data(sid)
 (out/'Evidence_Verification.json').write_text(json.dumps(dict(source_byte_hashes_checked=len(set(checked)),official_fund_plan_rows=len(forecast),official_plan_source_use_checks=20,local_fund_total_and_scope_verified=True,transfer_cancellation_symbolic_checks=2,sector_N3_cash_closure=False,source_receipts_sha256=hashlib.sha256((out/'Public_Source_Receipts.json').read_bytes()).hexdigest()),indent=2)+'\n')
 print('Evidence accounts built; cash availability and sector N3 closure remain unknown.')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--outdir',type=Path,default=P);a.add_argument('--source-cache',type=Path,default=Path('/tmp/n3-official'));z=a.parse_args();main(z.outdir,z.source_cache)
