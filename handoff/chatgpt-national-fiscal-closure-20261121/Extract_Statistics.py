#!/usr/bin/env python3
"""Extract exact cells from the separately retained official workbooks.
Only this acquisition helper needs openpyxl; fiscal runtime uses stdlib CSV/JSON.
"""
from pathlib import Path
import csv,json,hashlib
P=Path(__file__).resolve().parent
def dump(path,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 import openpyxl
 source=[]
 for name,url in {'CAO_202607_Projections.xlsx':'https://www5.cao.go.jp/keizai2/keizai-syakai/shisan/keisuuhyo.xlsx','SNA2024_GFS.xlsx':'https://www.esri.cao.go.jp/jp/sna/data/data_list/kakuhou/files/2024/tables/2024s6_2_jp.xlsx','SNA2024_Sector_Accounts.xlsx':'https://www.esri.cao.go.jp/jp/sna/data/data_list/kakuhou/files/2024/tables/2024s6_jp.xlsx','SNA2024_Sector_Stocks.xlsx':'https://www.esri.cao.go.jp/jp/sna/data/data_list/kakuhou/files/2024/tables/2024ss3_jp.xlsx'}.items():
  b=(P/name).read_bytes();source.append(dict(file=name,url=url,size=len(b),sha256=hashlib.sha256(b).hexdigest(),retrieved_date_JST='2026-11-21',retrieval='PYTHON_URLLIB_PUBLIC_HTTPS',data_status='OFFICIAL_PUBLISHED_ESTIMATES_OR_PROJECTION_NOT_SPE_ASSUMPTION'))
 (P/'Statistical_Source_Receipts.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
 w=openpyxl.load_workbook(P/'CAO_202607_Projections.xlsx',data_only=True);s=w['財政の詳細計数表（現状投影・長期）'];macro=w['計数表 (長期)'];cols={s.cell(5,c).value:c for c in range(4,43)}
 rowmap={53:'CL_PB',55:'central_PB',57:'local_PB',59:'CL_balance',61:'central_balance',63:'local_balance',65:'CL_debt_end',67:'central_debt_end',69:'local_debt_end',28:'central_GA_expenditure',29:'central_GA_primary_expenditure',30:'central_GA_social_security',31:'central_GA_local_transfer',33:'central_GA_debt_service',34:'central_GA_debt_redemption_transfer',35:'central_GA_interest',36:'central_GA_nonbond_revenue',37:'central_GA_tax',38:'central_GA_other_revenue',39:'central_GA_PB',44:'local_ordinary_expenditure',45:'local_ordinary_debt_service',46:'local_ordinary_nonbond_revenue',47:'local_ordinary_tax',48:'local_ordinary_PB'}
 annual=[];cells=[]
 for year,c in cols.items():
  if year<2025:continue
  z=dict(year=year,time_basis='JAPAN_FISCAL_YEAR',unit='TRILLION_YEN_NOMINAL',official_case='CAO_202607_CURRENT_PROJECTION',CL_boundary='INCLUDING_RECONSTRUCTION_GX_AI_SEMICONDUCTORS_EXCLUDING_SOCIAL_SECURITY_FUNDS',official_status='OFFICIAL_ESTIMATE_OR_PROJECTION_NOT_REALIZED_OUTTURN')
  for r,k in rowmap.items():
   v=s.cell(r,c).value;assert isinstance(v,(int,float)),(r,c,v);z[k+'_trn']=v;cells.append(dict(file='CAO_202607_Projections.xlsx',sheet=s.title,cell=s.cell(r,c).coordinate,metric=k,year=year,raw=v,unit='TRILLION_YEN'))
  z['official_nominal_GDP_trn']=macro.cell(50,c).value
  assert z['official_nominal_GDP_trn']>0
  annual.append(z)
 dump(P/'Official_Fiscal_Baseline_2025_2040.csv',annual);dump(P/'Statistical_Cell_Map.csv',cells)
 # Snapshot audit, not a 2026 social-insurance forecast.
 w=openpyxl.load_workbook(P/'SNA2024_GFS.xlsx',data_only=True);g=w['経常・資本取引'];sna=openpyxl.load_workbook(P/'SNA2024_Sector_Accounts.xlsx',data_only=True).worksheets[0]
 sectors=['CENTRAL','LOCAL','SOCIAL_SECURITY','CONSOLIDATION_ADJUSTMENT','GENERAL_GOVERNMENT'];out=[]
 for idx,sector in enumerate(sectors):
  c=152+idx;z=dict(year=2024,time_basis='FISCAL_YEAR',sector=sector,unit='TRILLION_YEN',source='SNA2024_GFS')
  for r,k in {8:'revenue',9:'tax',44:'social_contributions',61:'internal_grants_received',66:'interest_received_GFS',85:'expense',94:'depreciation',95:'interest_paid_GFS',114:'internal_grants_paid',117:'social_benefits',146:'net_nonfinancial_asset_acquisition',160:'net_lending'}.items():z[k+'_trn']=g.cell(r,c).value/1000
  z['expenditure_including_net_capital_trn']=z['expense_trn']+z['net_nonfinancial_asset_acquisition_trn']
  if sector!='CONSOLIDATION_ADJUSTMENT':
   sc={'CENTRAL':123,'LOCAL':124,'SOCIAL_SECURITY':125,'GENERAL_GOVERNMENT':126}[sector]
   for r,k in {82:'SNA_net_lending',83:'SNA_PB',85:'interest_received_pre_FISIM',86:'interest_paid_pre_FISIM'}.items():z[k+'_trn']=sna.cell(r,sc).value/1000
  out.append(z)
 dump(P/'SNA2024_Sector_Snapshot.csv',out)
 print('Extracted',len(annual),'years and',len(cells),'source cells')
if __name__=='__main__':main()
