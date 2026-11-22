#!/usr/bin/env python3
"""Historical stock evidence only; never injects it as usable 2026 treasury cash."""
from pathlib import Path
import argparse,csv,hashlib
import openpyxl
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();f=a.root/'handoff/chatgpt-national-fiscal-closure-20261121/SNA2024_Sector_Stocks.xlsx'
b=f.read_bytes();assert hashlib.sha256(b).hexdigest()=='5a5eb8d7ff206dfa9dddd5d776fb47d74a0b30522bcd725c1978b7a44834a8dc';s=openpyxl.load_workbook(f,data_only=True).worksheets[0];rows=[]
for col in range(122,126):
 rows.append(dict(year=2024,time_basis='CALENDAR_YEAR_END',sector=s.cell(6,col).value,currency_deposits_trn=s.cell(16,col).value/1000,source_sheet=s.title,source_cell=s.cell(16,col).coordinate,source_raw_billion_yen=s.cell(16,col).value,source_url='https://www.esri.cao.go.jp/jp/sna/data/data_list/kakuhou/files/2024/tables/2024ss3_jp.xlsx',usable_cash_2026_verified=False,legal_transfer_or_liquidity_verified=False,initial_cash_in_simulation_not_replaced=True))
with a.output.open('w',newline='') as h:w=csv.DictWriter(h,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print('EXTRACTED_2024_STOCK_ONLY',len(rows))
