"""Offline extraction of individually retained official bytes; openpyxl and pdftotext required."""
import argparse,base64,csv,hashlib,io,json,re,subprocess,tempfile,unicodedata,warnings
from pathlib import Path
import openpyxl
warnings.filterwarnings('ignore',category=UserWarning,module='openpyxl')
PRIOR='handoff/chatgpt-common-labor-national-statistics-connection-20261123'
URLS={
 'older-series.xlsx':('000001082684','0','LFS historical3-3','2025 annual','2026-01-30'),
 'older-pop.xlsx':('000001082682','0','LFS historical3-1','2025 annual','2026-01-30'),
 'oct-employment.xlsx':('000040373820','0','LFS I-2','2025-10','2025-11-28'),
 'oct-hours.xlsx':('000040373831','0','LFS II-4','2025-10','2025-11-28'),
 'annual-employment.xlsx':('000040403919','0','LFS I-2','2025 annual','2026-01-30'),
 'annual-monthhours.xlsx':('000040403931','0','LFS II-4','2025 annual','2026-01-30'),
 'annual-weekhours.xlsx':('000040403936','0','LFS II-9','2025 annual','2026-01-30'),
 'annual-hours.xlsx':('000040403941','0','LFS II-11-4','2025 annual','2026-01-30'),
 'monthly-pop.xlsx':('000031831366','0','LFS1-b-1 original series','2025-01 to2026-09','2026-10-30'),
 'monthly-employed.xlsx':('000031831359','0','LFS1-a-2 original series','2025-01 to2026-09','2026-10-30'),
 'population2025-rebased.xlsx':('000040526742','4','Population estimates table1;2025 census rebased','2025-10-01','2026-11-20')}
PDFMONTHS=[f'2025{x:02d}' for x in range(6,13)]+[f'2026{x:02d}' for x in range(1,6)]
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(root,out,rawdir=None):
 out.mkdir(parents=True,exist_ok=True);orig=out/'Source_Originals';orig.mkdir(exist_ok=True);sources=[];raw={};cells=[]
 def original(name,url,table,period,release,basis='2020 census benchmark; see original LFS coverage'):
  if rawdir:
   b=(rawdir/name).read_bytes();d=dict(filename=name,url=url,table=table,period=period,release=release,basis=basis,retrieved='2026-11-23',size=len(b),sha256=hashlib.sha256(b).hexdigest(),base64=base64.b64encode(b).decode());save(orig/(name+'.json'),d)
  else:
   d=json.loads((orig/(name+'.json')).read_text());b=base64.b64decode(d['base64']);assert len(b)==d['size'] and hashlib.sha256(b).hexdigest()==d['sha256']
  raw[name]=b;sources.append(dict(file=name,url=url,table_id=table,reference_period=period,release_date=release,population_benchmark=basis,seasonal_adjustment='UNADJUSTED',unit='see extracted source cell',retrieved='2026-11-23',size=len(b),sha256=hashlib.sha256(b).hexdigest(),storage='Source_Originals/'+name+'.json',verification='DECODED_SHA256_SIZE_PASS'))
 for name,(i,k,t,p,d) in URLS.items():original(name,'https://www.e-stat.go.jp/stat-search/file-download?statInfId='+i+'&fileKind='+k,t,p,d,'2025 census rebased; NOT used to rebase model or LFS' if name=='population2025-rebased.xlsx' else '2020 census benchmark; LFS resident survey coverage')
 for i,m in enumerate(PDFMONTHS):original('pop-final-'+m+'.pdf','https://www.stat.go.jp/data/jinsui/pdf/'+m+'.pdf','Population estimates monthly report page1 table; final reference column',f'2025-{i+1:02d}-01',m+' publication month; exact date in original','2020 census benchmark; archived final estimates, not2025 rebase')
 for name,url in [('annual-original-list.html','https://www.e-stat.go.jp/stat-search/files?cycle=7&layout=datalist&month=0&page=1&tclass1=000001226584&tclass2=000001226585&toukei=00200531&tstat=000001226583&year=20250'),('oct2025-list.html','https://www.e-stat.go.jp/stat-search/files?cycle=1&layout=datalist&month=24101210&tclass1=000001226584&tclass2=000001226585&toukei=00200531&tstat=000001226583&year=20250'),('population2025-page.html','https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid=000040526742'),('long-basic.html','https://www.e-stat.go.jp/stat-search/files?cycle=0&layout=datalist&page=1&tclass1=000001226851&tclass2=000001226852&toukei=00200531&tstat=000001226583'),('jinsui.html','https://www.stat.go.jp/data/jinsui/2.html')]:original(name,url,'official source metadata','retrieval snapshot2026-11-23','see document','metadata')
 books={n:openpyxl.load_workbook(io.BytesIO(b),data_only=True) for n,b in raw.items() if n.endswith('.xlsx')}
 def val(n,s,c):
  x=books[n][s][c].value;assert isinstance(x,(int,float)),(n,s,c,x);cells.append(dict(file=n,sheet=s,cell=c,value=x));return x
 cols=dict(zip(range(15,65,5),['R','U','Y','Z','AB','AC','AE','AF','AH','AI']));cols.update({65:'AK',70:'AM',75:'AO',80:'AP',85:'AQ'})
 rates=[]
 for period,n in [('ANNUAL_2025','annual-employment.xlsx'),('OCTOBER_2025','oct-employment.xlsx')]:
  for sex,sheet in [('both','1'),('male','2'),('female','3')]:
   for age,c in cols.items():
    P=val(n,sheet,c+'14')*10000;E=val(n,sheet,c+'16')*10000;rates.append(dict(period=period,sex=sex,age_lower=age,age_upper=age+4 if age<85 else None,population=P,employed=E,rate=E/P,source_file=n,sheet=sheet,pop_cell=c+'14',employment_cell=c+'16',definition='SAME_LFS_PERIOD_POPULATION_AND_EMPLOYED',nationality_specific=False))
 # No silently finer-than85 split; 85+ profile repeated over existing85-89...100+ cells.
 previous=json.loads((root/PRIOR/'Statistics_Inputs.json').read_text());stage1=json.loads((root/'handoff/f-foreign-quantity-20261120/Inputs.json').read_text())['stage1_inputs']['previous_inputs'];oldrates=stage1['employment_rates_2025']
 def oldrate(age,sex):return oldrates[sex][0 if age<25 else 1 if age<35 else 2 if age<45 else 3 if age<55 else 4 if age<60 else 5 if age<65 else 6 if age<70 else 7 if age<75 else 8]
 older=[]
 for r in rates:
  if r['age_lower']<65:continue
  older.append(dict(**r,observed_not_allocated=True,old_model_rate=oldrate(r['age_lower'],r['sex']) if r['sex']!='both' else None,model_cell_mapping='85+ shared coefficient;not finer observation' if r['age_lower']==85 else 'same5year model group',fulltime_hours_observed=None))
 dump(out/'Older_65Plus_Age_Sex_Employment_Rates.csv',older)
 cross=[]
 for sex,sheet in [('both','総数'),('male','男'),('female','女')]:
  for age,col,ratecol in [(65,'O','AU'),(70,'P','AV'),(75,'Q','AW')]:
   P=val('older-pop.xlsx',sheet,col+'68')*10000;E=val('older-series.xlsx',sheet,col+'68')*10000;pub=val('older-series.xlsx',sheet,ratecol+'68')/100
   rr=[r for r in rates if r['period']=='ANNUAL_2025' and r['sex']==sex and (r['age_lower']==age if age<75 else r['age_lower']>=75)]
   cross.append(dict(sex=sex,age_lower=age,historical_population=P,historical_employed=E,historical_published_rate=pub,original_fine_P_sum=sum(r['population'] for r in rr),original_fine_E_sum=sum(r['employed'] for r in rr),fine_rounded_P_residual=P-sum(r['population'] for r in rr),fine_rounded_E_residual=E-sum(r['employed'] for r in rr),old_model_rate=oldrate(age,sex) if sex!='both' else None,rate_difference_from_old=E/P-oldrate(age,sex) if sex!='both' else None))
 dump(out/'Older_Coarse_Fine_And_Existing_Rate_Comparison.csv',cross)

 # Weekly aggregate by65-69/70-74/75+ is directly reported; annual hours are explicitly proxies.
 hours=[]
 for sex,sheet in [('both','1'),('male','3'),('female','5')]:
  for age,row in list(zip(range(15,65,5),range(16,26)))+[(65,27),(70,29),(75,30)]:
   E=val('annual-weekhours.xlsx',sheet,'O'+str(row))*10000;H=val('annual-weekhours.xlsx',sheet,'AM'+str(row))*10000;absence=val('annual-weekhours.xlsx',sheet,'P'+str(row))*10000;unknown=val('annual-weekhours.xlsx',sheet,'AK'+str(row))*10000
   hours.append(dict(series='DETAILED_WEEK52',sex=sex,age_lower=age,age_upper=age+4 if age<75 else None,employed=E,absent=absence,unknown_hours=unknown,weekly_aggregate_hours=H,annual_hours_per_employed=52*H/E,annual_hours_observed=None,label='CONDITIONAL_ANNUALIZED_PROXY',formula='52*published_weekly_aggregate/all_employed',absence_unknown='absence0 byofficialweeklydefinition; unknown not imputed;publishedaggregatecoverage',source_file='annual-weekhours.xlsx',sheet=sheet,cell='AM'+str(row)+'/O'+str(row)))
 monthrows=dict(zip(range(15,65,5),[31,32,34,35,37,38,40,41,43,44]))
 monthrows[65]=45
 for sex,sheet in [('both','1'),('male','2'),('female','3')]:
  for age,row in monthrows.items():
   E=val('annual-monthhours.xlsx',sheet,'O'+str(row))*10000;active=val('annual-monthhours.xlsx',sheet,'P'+str(row))*10000;unknown=val('annual-monthhours.xlsx',sheet,'BT'+str(row))*10000;mean=val('annual-monthhours.xlsx',sheet,'BU'+str(row))
   hours.append(dict(series='MONTH_MEAN12_PROFILE',sex=sex,age_lower=age,age_upper=age+4 if age<65 else None,employed=E,at_work=active,unknown_month_hours=unknown,published_mean_monthly_hours=mean,annual_hours_per_employed=12*mean,annual_hours_observed=None,label='CONDITIONAL_ANNUALIZED_PROFILE_NOT_ALL_EMPLOYED_MEASUREMENT',formula='12*annual_table_published_mean_monthhours; selection-profile transfer to model employed',absence_unknown='officialmean excludes unknown and non-at-work per terms; no missingperson hours imputed;transferisconditional',source_file='annual-monthhours.xlsx',sheet=sheet,cell='BU'+str(row)))
 dump(out/'Older_Age_Sex_Annual_Hours_Bridge.csv',hours)
 annualstat=[]
 for sex,sheet in [('both','1'),('male','3'),('female','5')]:annualstat.append(dict(sex=sex,annual_mean_hours=val('annual-hours.xlsx',sheet,'O12'),denominator='at-work persons with known monthlyhours; annual average count',age_detail_available=False,source='LFS II-11-4; industry/occupation not age',not_SNA_jobs=True,not_individual_panel_annual_actual=True))
 # Decode archived population report final columns. Check original lines and units; first3numbers are provisional and deliberately ignored.
 pop=[]
 for i,m in enumerate(PDFMONTHS):
  n='pop-final-'+m+'.pdf'
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'input.pdf';f.write_bytes(raw[n]);text=subprocess.check_output(['pdftotext','-f','1','-l','1','-layout',str(f),'-'],text=True)
  lines=unicodedata.normalize('NFKC',text).splitlines();seen=set()
  date=re.search(r'令和\s*(\d+)年\s*(\d+)月\s*(\d+)日',unicodedata.normalize('NFKC',text))
  if date:
   next(r for r in sources if r['file']==n)['release_date']=f'{2018+int(date[1]):04d}-{int(date[2]):02d}-{int(date[3]):02d}'
  for li,line in enumerate(lines):
   mt=re.match(r'^\s*(\d+)\s*~\s*(\d+)',line);is100=re.match(r'^\s*100歳以上',line)
   if not mt and not is100:continue
   age=int(mt[1]) if mt else 100
   if age%5 or age>100 or age in seen:continue
   values=re.findall(r'\d[\d,]*(?:\.\d+)?',line)
   # Exclude the percentage table and regrouped15-64 rows.
   if len(values)!=(14 if mt else 13):continue
   v=[float(x.replace(',',''))*1000 for x in values[-9:]]
   if any('.' in x for x in values[-9:]):continue
   seen.add(age)
   for sex,ix in [('both',0),('male',1),('female',2)]:pop.append(dict(year=2025,month=i+1,age_lower=age,sex=sex,population=v[ix],japanese=v[ix+3],foreign=v[ix+6],source_file=n,source_page=1,source_line=li+1,source_line_text=line,benchmark='2020 census final archive;first day'))
  assert seen==set(range(0,101,5)),(n,seen)
 dump(out/'Population_Estimates_2025_First_Day_Monthly_Archive.csv',pop)
 # Same-survey monthly P/E; use original series and actual available months only.
 monthly=[]
 popcols={'both':('E','G','H','I','J','K','L'),'male':('N','P','Q','R','S','T','U'),'female':('W','Y','Z','AA','AB','AC','AD')}
 ecols={'both':('E','G','H','I','J','K','L'),'male':('N','P','Q','R','S','T','U'),'female':('W','Y','Z','AA','AB','AC','AD')}
 # Both raw-series workbooks have9-column sexblocks; verify headers rather than assuming seasonally adjusted layout.
 for n in ['monthly-pop.xlsx','monthly-employed.xlsx']:
  assert '男' in str(books[n]['原数値']['N6'].value) and '女' in str(books[n]['原数値']['W6'].value)
 for year,start,months in [(2025,647,12),(2026,659,9)]:
  for mo in range(1,months+1):
   row=start+mo-1
   for sex in ['both','male','female']:
    for group,cp,ce in zip([15,15.1,25,35,45,55,65],popcols[sex],ecols[sex]):
     P=val('monthly-pop.xlsx','原数値',cp+str(row))*10000;E=val('monthly-employed.xlsx','原数値',ce+str(row))*10000
     monthly.append(dict(year=year,month=mo,sex=sex,age_group='15+' if group==15 else '15-24' if group==15.1 else str(group)+'+' if group==65 else str(group)+'-'+str(group+9),population=P,employed=E,rate=E/P,pop_source_cell=cp+str(row),employed_source_cell=ce+str(row),label='SAME_LFS_MONTH_ORIGINAL_SERIES',missing_months_not_filled=True))
 dump(out/'LFS_Observed_Monthly_Timing_2025_2026.csv',monthly)
 timing=[]
 for r in rates:
  a=r['age_lower'];sex=r['sex'];group=[x for x in pop if x['sex']==sex and (x['age_lower']==a if a<85 else x['age_lower']>=85)];octp=sum(x['population'] for x in group if x['month']==10);meanp=sum(x['population'] for x in group)/12
  timing.append(dict(period=r['period'],sex=sex,age_lower=a,LFS_population=r['population'],LFS_employed=r['employed'],same_LFS_rate=r['rate'],population_estimates_firstday_mean2025=meanp,population_estimates_oct1_2025=octp,matched_estimate_population=meanp if r['period']=='ANNUAL_2025' else octp,population_estimate_minus_LFS=(meanp if r['period']=='ANNUAL_2025' else octp)-r['population'],classification='CONDITIONAL_REFERENCE_TIMING_PROXY;notexact same population/benchmark exposure',strict_same_time_definition='LFS P/E same survey; population estimates firstday vs LFS surveyweek notexact',cross_population_division_used=False))
 dump(out/'Population_Employment_Same_Time_Bridge.csv',timing)
 # New census revision deliberately not injected in established model population.
 rev=[]
 for c in ['J','K','L','M','N','O','P','Q','R']:rev.append(dict(source_cell=c+'19',value_thousand=val('population2025-rebased.xlsx','第１表',c+'19'),used_for_model=False,reason='2025 census vintage differs from LFS2020 benchmark and established conditionalpopulation'))
 save(out/'Statistics_Inputs.json',dict(rates=rates,hours=hours,population_estimates=pop,LFS_monthly=monthly,LFS_published_annual_hours=annualstat,rebased_population=rev,prior_statistics_sha256=hashlib.sha256((root/PRIOR/'Statistics_Inputs.json').read_bytes()).hexdigest(),FTE_reference=2080,not_forecast=True,monthly_missing_2026=[10,11,12]))
 dump(out/'Official_Extracted_Cells.csv',cells);dump(out/'Official_Population_Employment_Timing_And_65Plus_Source_Receipts.csv',sources)
 print(json.dumps(dict(originals=len(sources),cells=len(cells),fine_rates=len(rates),population_cells=len(pop),monthly_observations=len(monthly))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--rawdir',type=Path);a=p.parse_args();run(a.root,a.out,a.rawdir)
