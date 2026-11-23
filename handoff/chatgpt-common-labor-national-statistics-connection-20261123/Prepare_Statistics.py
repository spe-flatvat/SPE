"""Extract only documented cells; retain exact downloaded bytes in individual JSON envelopes.
Requires openpyxl for extraction only. Annual engine uses extracted JSON and stdlib.
python Prepare_Statistics.py --rawdir <downloaded originals> --out <new output>
"""
import argparse,base64,csv,hashlib,io,json
from pathlib import Path
import openpyxl
SNA='https://www.esri.cao.go.jp/jp/sna/data/data_list/'
URLS={
 '2024hw_jp.xlsx':SNA+'hours-worked/tables/2024hw_jp.xlsx',
 **{k:SNA+'kakuhou/files/2024/tables/'+k for k in ['2024s3_jp.xlsx','2024fcm1n_jp.xlsx','2024fcm1rn_jp.xlsx','2024fcm3rn_jp.xlsx']},
 **{'LFS_'+i+'.xlsx':'https://www.e-stat.go.jp/stat-search/file-download?statInfId='+i+'&fileKind=0' for i in ['000040440941','000040440942','000040440943','000040440953']},
 'hw_announce.pdf':SNA+'hours-worked/pdf/hw_announce.pdf',
 'yougo_kaisetsu.pdf':'https://www.stat.go.jp/data/roudou/pdf/yougo_kaisetsu.pdf',
 'note01-j.pdf':'https://www.stat.go.jp/data/roudou/pdf/note01-j.pdf',
 '202610.pdf':'https://www.stat.go.jp/data/jinsui/pdf/202610.pdf',
 'pp2023_gaiyou.pdf':'https://www.ipss.go.jp/pp-zenkoku/j/zenkoku2023/pp2023_gaiyou.pdf'}
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(rawdir,out):
 out.mkdir(parents=True,exist_ok=True);orig=out/'Source_Originals';orig.mkdir(exist_ok=True);receipts=[];raws={}
 for name,url in URLS.items():
  raw=(rawdir/name).read_bytes() if rawdir else base64.b64decode(json.loads((orig/(name+'.json')).read_text())['base64'])
  sha=hashlib.sha256(raw).hexdigest();raws[name]=raw
  value=dict(original_filename=name,url=url,retrieval_date_JST='2026-11-23',route='direct HTTPS urllib; original bytes retained, not web-excerpt transcription',size=len(raw),sha256=sha,base64=base64.b64encode(raw).decode())
  if rawdir:save(orig/(name+'.json'),value)
  else:
   old=json.loads((orig/(name+'.json')).read_text());assert old['sha256']==sha and old['size']==len(raw)
  isL=name.startswith('LFS');isS=name.endswith('.xlsx') and not isL
  receipts.append(dict(file=name,url=url,table_or_series='2025 LFS annual report I-B-1' if '44094' in name else '2025 LFS annual report I-B-9' if '440953' in name else 'SNA reference hours employed persons' if name=='2024hw_jp.xlsx' else 'SNA2024 annual national accounts' if isS else 'IPSS2023 median projection tables1-1/1-5/4-4' if name=='pp2023_gaiyou.pdf' else 'Statistics Bureau October2026 population report' if name=='202610.pdf' else 'official definition note',reference_period='2025 calendar annual average' if isL else '2005-2024 calendar years' if name=='2024hw_jp.xlsx' else '1994-2024 calendar years; extraction uses2005-2024' if isS else '2025/2026 October1' if name=='202610.pdf' else 'metadata / projection',release_date='2026-03-31 annual-report table release' if isL else '2026-01-30' if name in ['2024s3_jp.xlsx','2024hw_jp.xlsx'] else 'annual-flow release2025-12-23; individual current file revision date not independently identified' if isS else '2026-10-20' if name=='202610.pdf' else '2023-04-26' if name=='pp2023_gaiyou.pdf' else '2018-03-30' if name=='hw_announce.pdf' else 'date not printed in downloaded definition note',price_basis='2020 chain prices for real;current prices for nominal' if isS else 'not applicable',population_scope='resident persons age15+ incl eligible foreign residents; persons not jobs' if isL else 'domestic jobs; secondary jobs counted separately' if isS else 'see original',seasonal_adjustment='UNADJUSTED_CALENDAR_ANNUAL_AVERAGE' if isL else 'UNADJUSTED_CALENDAR_YEAR' if isS else 'N/A',retrieval_date='2026-11-23',size=len(raw),sha256=sha,storage='Source_Originals/'+name+'.json (base64 exact input bytes)',verification='DECODE_SIZE_SHA256_VERIFIED'))
 def wb(name):return openpyxl.load_workbook(io.BytesIO(raws[name]),data_only=True)
 cells=[]
 def val(book,sheet,cell):
  w=wb(book);s=w[sheet] if sheet else w.active;z=s[cell].value
  assert isinstance(z,(int,float)),(book,s.title,cell,z)
  cells.append(dict(file=book,sheet=s.title,cell=cell,value=z));return z
 # Same-vintage national SNA series; employment is jobs, hours per job is reference series.
 hist=[];s=wb('2024hw_jp.xlsx').active
 for col in range(2,s.max_column+1):
  y=int(s.cell(7,col).value);hc=s.cell(39,col).coordinate;ec=openpyxl.utils.get_column_letter(y-1994+2)
  hours=val('2024hw_jp.xlsx',None,hc);jobs=val('2024s3_jp.xlsx','暦年（１）就業者',ec+'39')*10000;employees=val('2024s3_jp.xlsx','暦年（２）雇用者',ec+'39')*10000;employeehours=val('2024s3_jp.xlsx','暦年（３）労働時間数',ec+'39')
  real=val('2024fcm1rn_jp.xlsx','実数',ec+'48')/1000;nom=val('2024fcm1n_jp.xlsx','実数',ec+'48')/1000;gva=val('2024fcm3rn_jp.xlsx','実数',ec+'51')/1000;total=jobs*hours
  hist.append(dict(year=y,SNA_jobs=jobs,SNA_employee_jobs=employees,annual_hours_per_job=hours,employee_hours_not_all_workers=employeehours,total_hours_derived=total,real_GDP_2020_chain_trn=real,nominal_GDP_current_trn=nom,real_production_subtotal_chain_trn=gva,real_GDP_per_job_yen=real*1e12/jobs,nominal_GDP_per_job_yen=nom*1e12/jobs,real_GDP_per_hour_yen=real*1e12/total,real_production_subtotal_per_hour_yen=gva*1e12/total,connection='SAME_YEAR_SNA_JOBS_REFERENCE_HOURS;rounded published cells',capital_services=None,TFP=None))
 lfs=[];sheets={};columns=['S','V','W','X','Y','Z','AA','AB','AC','AD','AE'];ages=list(range(15,65,5))+[65]
 for sex,name in [('both','LFS_000040440941.xlsx'),('male','LFS_000040440942.xlsx'),('female','LFS_000040440943.xlsx')]:
  s=wb(name).active;sheets[sex]=s
  for age,col in zip(ages,columns):
   P=val(name,None,col+'11')*10000;E=val(name,None,col+'13')*10000;LF=val(name,None,col+'12')*10000
   lfs.append(dict(sex=sex,age_lower=age,age_upper=age+4 if age<65 else None,resident_population=P,employed=E,labor_force=LF,employment_rate=E/P,labor_force_participation=LF/P,file=name,population_cell=col+'11',employment_cell=col+'13',nationality_split='NOT_AVAILABLE',year=2025))
 hours=[]
 for sex,start in [('both',15),('male',29),('female',43)]:
  for age,row in zip(ages,range(start,start+11)):
   E=val('LFS_000040440953.xlsx',None,'L'+str(row))*10000;at=val('LFS_000040440953.xlsx',None,'N'+str(row))*10000;absent=val('LFS_000040440953.xlsx',None,'M'+str(row))*10000;mean=val('LFS_000040440953.xlsx',None,'AF'+str(row));agg=val('LFS_000040440953.xlsx',None,'AG'+str(row))*1e8
   hours.append(dict(sex=sex,age_lower=age,age_upper=age+4 if age<65 else None,employed=E,at_work=at,not_at_work=absent,mean_weekly_hours_excludes_absent_and_unknown=mean,aggregate_weekly_hours=agg,observed_weekly_hours_per_all_employed=agg/E,annualized_hours_per_employed_proxy=52*agg/E,year=2025,annualization='52 fixed weeks is diagnostic conversion; not observed annual hours',nationality_split='NOT_AVAILABLE',rounding='counts10000 persons;aggregate hours0.01*1e8;do not force sums'))
 totals={k:val('LFS_000040440941.xlsx',None,cell)*10000 for k,cell in [('population15plus','R11'),('labor_force','R12'),('employed','R13'),('at_work','R14'),('absent','R17')]}
 totals['weekly_hours']=val('LFS_000040440953.xlsx',None,'AG14')*1e8;totals['published_mean_weekly_hours']=val('LFS_000040440953.xlsx',None,'AF14')
 save(out/'Statistics_Inputs.json',dict(status='DRAFT_NOT_ADOPTED',SNA_history=hist,LFS_age_sex_population_employment=lfs,LFS_age_sex_hours=hours,LFS2025_totals=totals,FTE_reference_hours=2080,FTE_reference_definition='40*52 diagnostic hours conversion only; not observed fulltime annual schedule or official FTE',future_time_assumption='observed2025 age/sex weekly coefficients fixed; SNA2024 mean fixed only neutral unit control',future_productivity_assumption='NO_NEW_SERIES;SNA2024 observed hourly value retained only separate constant satellite; no addition to A',extraction_dependency='openpyxl '+openpyxl.__version__))
 dump(out/'Official_Statistics_Source_Definition_And_Receipts.csv',receipts);dump(out/'Official_Statistics_Extracted_Cells.csv',cells);dump(out/'SNA_Observed_Employment_Hours_Productivity_2005_2024.csv',hist);dump(out/'LFS_2025_Age_Sex_Employment.csv',lfs);dump(out/'LFS_2025_Age_Sex_Hours.csv',hours)
 print(json.dumps(dict(originals=len(receipts),extracted_cells=len(cells),SNA2024=hist[-1],LFS2025=totals),ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--rawdir',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.rawdir,a.out.resolve())
