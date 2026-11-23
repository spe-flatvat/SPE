"""Pinned existing engines, isolated physical labor connections. No network needed."""
import argparse,base64,csv,hashlib,json,math,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
PIN='8a117759906f0d89c8a57e0899c03e3697be70a1'
P='handoff/chatgpt-common-labor-national-statistics-connection-20261123'
D='handoff/chatgpt-common-macro-demography-labor-productivity-diagnostic-20261123'
T='handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123'
HERE=Path(__file__).resolve().parent
SQ=['BASE_SQ_UNCHANGED','PREVIOUS_FINE_AGE_HOURS','ANNUAL_SAME_SURVEY_UNDER65','OLDER_FINE_RATES_ONLY','ANNUAL_ALIGNED_FULL_RATES','OCTOBER_NEAR_FULL_RATES','ANNUAL_FINE_WEEK_HOURS','ANNUAL_MONTH_HOURS_PROFILE','UNIFORM_LEVEL_CONTROL']
F_MATCH={'F_BASE_UNCHANGED':'BASE_SQ_UNCHANGED','F_PREVIOUS_FINE_AGE_HOURS':'PREVIOUS_FINE_AGE_HOURS','F_ANNUAL_ALIGNED_FULL_RATES':'ANNUAL_ALIGNED_FULL_RATES','F_OCTOBER_NEAR_FULL_RATES':'OCTOBER_NEAR_FULL_RATES','F_ANNUAL_FINE_WEEK_HOURS':'ANNUAL_FINE_WEEK_HOURS','F_ANNUAL_MONTH_HOURS_PROFILE':'ANNUAL_MONTH_HOURS_PROFILE'}
def js(p):return json.loads(p.read_text())
def read(p):return list(csv.DictReader(p.open()))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(root,out,inputs):
 out.mkdir(parents=True,exist_ok=True);s=js(inputs);checks=[]
 def ck(n,a,b=0.,tol=1e-7):
  err=abs(a-b);ok=math.isfinite(err) and err<=tol+1e-12*abs(b);checks.append(dict(check=n,error=err,tolerance=tol,passed=ok));assert ok,(n,a,b)
 # Own verification of prior and runtime source bytes, never another AI's PASS.
 source=[]
 for folder,commit in [(P,'78858034a8659fb21d01421168de6be0173ff0c5'),(D,'9dcf953e949593e773bab906eb72577f0efec73e'),(T,'e981c924adbe9c7ca77b96d2dc94e40378186613'),('handoff/claude-three-scenario-verification-20261123','3611534d85fb52c976592c96120f7663dbfa63f5')]:
  for path in subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--',folder],cwd=root,text=True).splitlines():
   b=subprocess.check_output(['git','show',commit+':'+path],cwd=root)
   if (root/path).exists():ck('fixed_local_bytes:'+path,0 if (root/path).read_bytes()==b else 1,0,0)
   source.append(dict(path=path,commit=commit,size=len(b),sha256=hashlib.sha256(b).hexdigest(),local_compared=(root/path).exists()))
 for f in sorted((inputs.parent/'Source_Originals').glob('*.json')):
  d=js(f);b=base64.b64decode(d['base64']);ck('officialsize:'+f.name,len(b),d['size'],0);ck('officialsha:'+f.name,0 if hashlib.sha256(b).hexdigest()==d['sha256'] else 1,0,0)
 # Statistical identities and coverage, separate from engine arithmetic.
 for r in s['rates']:
  ck('EoverP:'+r['period']+r['sex']+str(r['age_lower']),r['rate']*r['population'],r['employed'],1e-5)
  ck('ratebounds:'+r['period']+r['sex']+str(r['age_lower']),0 if 0<=r['employed']<=r['population'] else 1,0,0)
 for r in s['hours']:
  ck('hourspositive:'+r['series']+r['sex']+str(r['age_lower']),0 if r['annual_hours_per_employed']>0 else 1,0,0)
  if r['series']=='DETAILED_WEEK52':ck('weekunits:'+r['sex']+str(r['age_lower']),r['annual_hours_per_employed']*r['employed'],52*r['weekly_aggregate_hours'],1e-4)
  else:ck('monthunits:'+r['sex']+str(r['age_lower']),r['annual_hours_per_employed'],12*r['published_mean_monthly_hours'])
 for sex in ['both','male','female']:
  for age in range(0,101,5):ck('archive12months:'+sex+str(age),len([r for r in s['population_estimates'] if r['sex']==sex and r['age_lower']==age]),12,0)
 for year,months in [(2025,12),(2026,9)]:
  ck('observedmonths:'+str(year),len(set(r['month'] for r in s['LFS_monthly'] if r['year']==year)),months,0)
 ck('no_unpublished2026months',len([r for r in s['LFS_monthly'] if r['year']==2026 and r['month']>9]),0,0)
 for name,col,target in [('population','population',109730000),('employed','employed',68280000)]:
  vals=[r[col] for r in s['LFS_monthly'] if r['year']==2025 and r['sex']=='both' and r['age_group']=='15+'];ck('roundedannual:'+name,sum(vals)/12,target,5000.)
 for r in read(inputs.parent/'Older_Coarse_Fine_And_Existing_Rate_Comparison.csv'):
  ck('older_rounding_E:'+r['sex']+r['age_lower'],float(r['fine_rounded_E_residual']),0.,20000.)
  ck('older_rounding_P:'+r['sex']+r['age_lower'],float(r['fine_rounded_P_residual']),0.,20000.)
 prior=js(root/D/'BASE_SQ_REPLAY/Common_Trace_BASE_SQ_REPLAY.json')['years'];L0=prior[0]['labor'];previnputs=js(root/P/'Fixed_Labor_Bridge_Case_Inputs.json');oldstats=js(root/P/'Statistics_Inputs.json');originalcells=read(root/D/'SQ_Age_Sex_Employment_Cells_2026_2055.csv')
 rates={(r['period'],r['sex'],r['age_lower']):r['rate'] for r in s['rates']};hours={(r['series'],r['sex'],r['age_lower']):r['annual_hours_per_employed'] for r in s['hours']}
 oldfine={(r['sex'],r['age_lower']):r['employment_rate'] for r in oldstats['LFS_age_sex_population_employment']};oldh={(r['sex'],r['age_lower']):r['annualized_hours_per_employed_proxy'] for r in oldstats['LFS_age_sex_hours']}
 cases={c:dict(physical_labor=[],headcount=[],hours=[],engine_L=[]) for c in SQ};cellrows=[];meta=[];uniform=68280000/68031652.825
 for y in range(2026,2056):
  yearcells=[r for r in originalcells if int(r['year'])==y];sums={c:[0.,0.,0.] for c in SQ}
  for r in yearcells:
   a=int(r['age_lower']);sex=r['sex'];pop=float(r['persons']);old=float(r['employment_rate']);annual=rates[('ANNUAL_2025',sex,min(a,85))] if a>=15 else 0.;october=rates[('OCTOBER_2025',sex,min(a,85))] if a>=15 else 0.;under=oldfine[(sex,a)] if 15<=a<65 else old
   weekly=hours[('DETAILED_WEEK52',sex,min(a,75))] if a>=15 else 0.;monthly=hours[('MONTH_MEAN12_PROFILE',sex,min(a,65))] if a>=15 else 0.;previoush=oldh[(sex,min(a,65))] if a>=15 else 0.
   variants={'BASE_SQ_UNCHANGED':(old,None),'PREVIOUS_FINE_AGE_HOURS':(under,previoush),'ANNUAL_SAME_SURVEY_UNDER65':(under,None),'OLDER_FINE_RATES_ONLY':(annual if a>=65 else old,None),'ANNUAL_ALIGNED_FULL_RATES':(annual,None),'OCTOBER_NEAR_FULL_RATES':(october,None),'ANNUAL_FINE_WEEK_HOURS':(annual,weekly),'ANNUAL_MONTH_HOURS_PROFILE':(annual,monthly),'UNIFORM_LEVEL_CONTROL':(old*uniform,None)}
   cellrows.append(dict(year=y,nationality=r['nationality'],sex=sex,age_lower=a,population=pop,old_rate=old,annual_same_LFS_rate=annual,october_same_LFS_rate=october,annual_employed=pop*annual,october_employed=pop*october,annual_week52_hours_coefficient=weekly if a>=15 else None,annual_month12_profile_coefficient=monthly if a>=15 else None,annual_week52_total_hours=pop*annual*weekly,annual_month12_profile_total_hours=pop*annual*monthly,rate85plus_shared=a>=85,hours75plus_shared=a>=75,month65plus_shared=a>=65,foreign_rate_time_measured=False))
   for c,(rate,h) in variants.items():
    e=pop*rate;sums[c][0]+=e if h is None else e*h;sums[c][1]+=e;sums[c][2]+=0 if h is None else e*h
  Ptotal=sum(float(r['persons']) for r in yearcells);P15=sum(float(r['persons']) for r in yearcells if int(r['age_lower'])>=15);ck('population:'+str(y),Ptotal,prior[y-2026]['population'],1e-5);ck('oldLsum:'+str(y),sums['BASE_SQ_UNCHANGED'][1],prior[y-2026]['labor'],1e-5)
  for c,vs in sums.items():
   physical,E,H=vs;istime=c in ['PREVIOUS_FINE_AGE_HOURS','ANNUAL_FINE_WEEK_HOURS','ANNUAL_MONTH_HOURS_PROFILE'];cases[c]['physical_labor'].append(physical);cases[c]['headcount'].append(E);cases[c]['hours'].append(H if istime else None)
   meta.append(dict(case=c,year=y,population=Ptotal,population15plus=P15,employed=E,employment_rate15plus=E/P15,older65plus_employed=sum(z['population']*(z['old_rate'] if c in ['BASE_SQ_UNCHANGED','ANNUAL_SAME_SURVEY_UNDER65','PREVIOUS_FINE_AGE_HOURS','UNIFORM_LEVEL_CONTROL'] else z['october_same_LFS_rate'] if c=='OCTOBER_NEAR_FULL_RATES' else z['annual_same_LFS_rate'])*(uniform if c=='UNIFORM_LEVEL_CONTROL' else 1.) for z in cellrows if z['year']==y and z['age_lower']>=65),total_hours_conditional=H if istime else None,annual_hours_observed=None,FTE_diagnostic=H/2080 if istime else None,official_FTE=None,time_definition='CONDITIONAL_MONTH_MEAN12_PROFILE;known-at-work profile transferred toall-employed;65+pooled' if c=='ANNUAL_MONTH_HOURS_PROFILE' else 'CONDITIONAL_WEEK52;surveyweek notactualannual;75+pooled' if c=='ANNUAL_FINE_WEEK_HOURS' else 'PRIOR_CONDITIONAL_WEEK52;65+pooled' if istime else 'N/A_HEADCOUNT_ONLY',rate_observation='2025-10 LFS;near Oct1 notexact' if c=='OCTOBER_NEAR_FULL_RATES' else '2025annual fixed future profile;modelpopulation remainsconditional',nationality_specific_observation=False,TFP=None,capital_substitution=None,unobserved_future_improvement=None,not_adopted=True))
 for c,d in cases.items():d['engine_L']=[L0*x/d['physical_labor'][0] for x in d['physical_labor']]
 for i in range(30):ck('priorbranch_L:'+str(i),cases['PREVIOUS_FINE_AGE_HOURS']['engine_L'][i],previnputs['cases']['LFS_HOURS_DETAIL_RATES']['engine_L'][i],1e-5)
 definition=dict(fixed_dependency_commit=PIN,cases=cases,F_offsets={f:[cases[c]['engine_L'][i]-prior[i]['labor'] for i in range(30)] for f,c in F_MATCH.items()},additional_TFP=False,initial_real=580,initial_nominal=600,annual_transitions=29,labor_elasticity=.65,price_medical_event_fixed=True)
 save(out/'Fixed_Aligned_Case_Inputs.json',definition);dump(out/'Aligned_Age_Sex_Nationality_Cells.csv',cellrows)
 logs=[];traces={}
 for c in SQ+list(F_MATCH)+['N3_BASE_UNCHANGED']:
  cmd=[sys.executable,str(HERE/'Aligned_Worker.py'),'--root',str(root),'--out',str(out/c),'--case',c,'--inputs',str(out/'Fixed_Aligned_Case_Inputs.json')];z=subprocess.run(cmd,capture_output=True,text=True)
  logs.append(dict(case=c,exit_code=z.returncode,stdout=z.stdout,stderr=z.stderr));save(out/'Execution_Log.json',logs);assert z.returncode==0,(c,z.stderr);print(c,z.stdout.strip(),flush=True)
  if c in SQ:traces[c]=js(out/c/('Common_Trace_'+('BASE_SQ_REPLAY' if c=='BASE_SQ_UNCHANGED' else c)+'.json'))
 base=traces['BASE_SQ_UNCHANGED']['years'];previous=traces['PREVIOUS_FINE_AGE_HOURS']['years'];annual=[];compar=[]
 for c,data in traces.items():
  for i,t in enumerate(data['years']):
   b=base[i];m=next(r for r in meta if r['case']==c and r['year']==t['year']);d=cases[c];ratio=d['physical_labor'][i]/d['physical_labor'][0]
   ck('labor:'+c+str(i),t['labor'],d['engine_L'][i],1e-5);ck('ratio:'+c+str(i),t['labor']/L0,ratio);ck('core:'+c+str(i),t['coreY'],580*b['nonlabor_factor']*ratio**.65)
   for k in ['population','working_age_population','foreign_population','risk','inflation','nonlabor_factor','medical_input_deflator']:ck('fixed:'+c+str(i)+k,t[k],b[k])
   ck('GDPidentity:'+c+str(i),t['Y'],t['desired']-t['unmet']);ck('priceidentity:'+c+str(i),t['N'],t['Y']*t['coreD']*(1+t['pressure']))
   if i==0:ck('initialY:'+c,t['Y'],580);ck('initialN:'+c,t['N'],600);ck('elasticity:'+c,data['parameters']['labor_response'],.65);ck('growth:'+c,data['parameters']['base_growth'],.01)
   if m['total_hours_conditional'] is not None:ck('FTE:'+c+str(i),m['FTE_diagnostic']*2080,m['total_hours_conditional'],1e-4)
   if c=='BASE_SQ_UNCHANGED' or c=='UNIFORM_LEVEL_CONTROL':ck('oldGDP:'+c+str(i),t['Y'],prior[i]['Y']);ck('oldNominal:'+c+str(i),t['N'],prior[i]['N'])
   if c=='PREVIOUS_FINE_AGE_HOURS':
    old=js(root/P/'LFS_HOURS_DETAIL_RATES/Common_Trace_LFS_HOURS_DETAIL_RATES.json')['years'][i];ck('previousY:'+str(i),t['Y'],old['Y']);ck('previousN:'+str(i),t['N'],old['N'])
   row=dict(**m,engine_L=t['labor'],L_ratio=ratio,A=t['nonlabor_factor'],core_GDP_trn=t['coreY'],real_GDP_trn=t['Y'],nominal_GDP_trn=t['N'],GDP_minus_current_SQ_trn=t['Y']-b['Y'],GDP_minus_previous_hours_trn=t['Y']-previous[i]['Y'],NA_reason='No measured annual age-sex hours/officialFTE/TFP/capital; conditional coefficients only')
   annual.append(row);compar.append({k:row[k] for k in ['case','year','employed','older65plus_employed','total_hours_conditional','FTE_diagnostic','L_ratio','A','real_GDP_trn','GDP_minus_current_SQ_trn','GDP_minus_previous_hours_trn','time_definition']})
 dump(out/'SQ_Annual_Aligned_Labor_Hours_FTE_GDP_2026_2055.csv',annual);dump(out/'SQ_Timing_65Plus_Hours_Case_Comparison.csv',compar);dump(out/'Key_Years.csv',[r for r in compar if r['year'] in [2026,2030,2035,2039,2055]])
 # Old-vs-new rates2x2: do not add incompatible prior Shapley accounting.
 attrib=[]
 for i,b in enumerate(base):
  under=traces['ANNUAL_SAME_SURVEY_UNDER65']['years'][i]['Y']-b['Y'];older=traces['OLDER_FINE_RATES_ONLY']['years'][i]['Y']-b['Y'];full=traces['ANNUAL_ALIGNED_FULL_RATES']['years'][i]['Y']-b['Y'];interaction=full-under-older
  week=traces['ANNUAL_FINE_WEEK_HOURS']['years'][i]['Y']-traces['ANNUAL_ALIGNED_FULL_RATES']['years'][i]['Y'];month=traces['ANNUAL_MONTH_HOURS_PROFILE']['years'][i]['Y']-traces['ANNUAL_ALIGNED_FULL_RATES']['years'][i]['Y'];ck('rateinteraction:'+str(i),under+older+interaction,full)
  attrib.append(dict(year=b['year'],under65_rate_delta_trn=under,older_rate_delta_trn=older,interaction_trn=interaction,full_rate_delta_trn=full,week_hours_conditional_after_full_rates_trn=week,month_profile_after_full_rates_trn=month,label='ACCOUNTING_NOT_CAUSAL;profile alternatives not added together'))
 dump(out/'Rate_Time_Accounting_And_Interactions.csv',attrib)
 # Full2025benchmark gap with archived Oct/mean population bridge; residual causes not falsely identified.
 stage1=js(root/'handoff/f-foreign-quantity-20261120/Inputs.json')['stage1_inputs']['previous_inputs'];ip=stage1['age_all_five_year']['2025'];oldrate=stage1['employment_rates_2025'];parts=dict(old_model=0.,IPSS_to_Oct_population_basis=0.,Oct_to_firstday_monthly_mean_timing_proxy=0.,firstday_mean_to_LFS_population_coverage_residual=0.,same_LFS_fine_rate_definition=0.)
 for sex,ix in [('male',0),('female',1)]:
  for a in range(15,86,5):
   ages=[b for b in range(15,101,5) if b==a or a==85 and b>=85];Pold=sum(ip[str(b)][ix] for b in ages);ridx=0 if a<25 else 1 if a<35 else 2 if a<45 else 3 if a<55 else 4 if a<60 else 5 if a<65 else 6 if a<70 else 7 if a<75 else 8;r=oldrate[sex][ridx]
   rr=next(x for x in s['rates'] if x['period']=='ANNUAL_2025' and x['sex']==sex and x['age_lower']==a);pp=[x for x in s['population_estimates'] if x['sex']==sex and x['age_lower'] in ages];octp=sum(x['population'] for x in pp if x['month']==10);meanp=sum(x['population'] for x in pp)/12
   parts['old_model']+=Pold*r;parts['IPSS_to_Oct_population_basis']+=(octp-Pold)*r;parts['Oct_to_firstday_monthly_mean_timing_proxy']+=(meanp-octp)*r;parts['firstday_mean_to_LFS_population_coverage_residual']+=(rr['population']-meanp)*r;parts['same_LFS_fine_rate_definition']+=rr['employed']-rr['population']*r
 ck('oldbenchmark',parts['old_model'],68031652.825,1e-5);fine=sum(r['employed'] for r in s['rates'] if r['period']=='ANNUAL_2025' and r['sex']!='both');parts['published_rounding_residual']=68280000-fine;ck('gapclosure',sum(v for k,v in parts.items() if k!='old_model'),68280000-parts['old_model'],1e-5)
 dump(out/'Benchmark_Gap_Timing_Accounting.csv',[dict(component=k,persons=v,label='proxy reference and definition accounting;notcausal identification of census vs sampling vs timing') for k,v in parts.items()]+[dict(component='LFS_minus_old',persons=68280000-parts['old_model'])])
 # Elder coarse/fine published sums leave rounded residuals; never balance by fabricating workers.
 residuals=[]
 for period in ['ANNUAL_2025','OCTOBER_2025']:
  n='annual-employment.xlsx' if period=='ANNUAL_2025' else 'oct-employment.xlsx'
  for sex in ['both','male','female']:
   rr=[r for r in s['rates'] if r['period']==period and r['sex']==sex];tot=sum(r['employed'] for r in rr);oldtot=68280000 if sex=='both' and period=='ANNUAL_2025' else None
   residuals.append(dict(period=period,sex=sex,fine_sum_employed=tot,published_total=oldtot,rounding_residual=oldtot-tot if oldtot is not None else None))
 dump(out/'Published_Group_Rounding_Residuals.csv',residuals)
 impacts=[]
 fbase=js(out/'F_BASE_UNCHANGED/F_Actual_Annual.json')
 for f,c in F_MATCH.items():
  rows=js(out/f/'F_Actual_Annual.json');trace=js(out/f/'F_Runtime_Trace.json')['years']
  for i,(r,t) in enumerate(zip(rows,trace)):
   ck('Fsinglecount:'+f+str(i),t['labor'],t['trajectory_effective_L']+t['education_effective_added']+t['health_effective_added']+t['elder_effective_added']+definition['F_offsets'][f][i],1e-5);ck('Fidentity:'+f+str(i),t['Y'],t['desired']-t['unmet']);ck('Frisk:'+f+str(i),t['risk'],base[i]['risk']);ck('Finflation:'+f+str(i),t['inflation'],base[i]['inflation'])
   if i==0:ck('FinitialY:'+f,r['real_gdp_trn'],580);ck('FinitialN:'+f,r['nominal_gdp_trn'],600)
   if f=='F_BASE_UNCHANGED':ck('Fbase:'+str(i),r['real_gdp_trn'],js(root/T/'F/F_Actual_Annual.json')[i]['real_gdp_trn'])
   if f=='F_PREVIOUS_FINE_AGE_HOURS':ck('Fprevious:'+str(i),r['real_gdp_trn'],js(root/P/'F_HOURS_DETAIL/F_Actual_Annual.json')[i]['real_gdp_trn'])
   impacts.append(dict(case=f,year=r['year'],matched_SQ=c,real_GDP_trn=r['real_gdp_trn'],matched_SQ_GDP_trn=traces[c]['years'][i]['Y'],F_minus_matched_SQ_trn=r['real_gdp_trn']-traces[c]['years'][i]['Y'],delta_F_base_trn=r['real_gdp_trn']-fbase[i]['real_gdp_trn'],common_L_offset=definition['F_offsets'][f][i],policy_additional_labor_once=True,limitation='COMMON_OFFSET_ONLY;notfullFcohorthours;existingelderforeignpensioneducationhealth equivalents preserved once'))
 nr=js(out/'N3_BASE_UNCHANGED/N3_Actual_Annual.json');nc=js(out/'N3_BASE_UNCHANGED/N3_Runtime_Checks.json');assert not nc['failures']
 for i,r in enumerate(nr):
  ck('N3base:'+str(i),r['real_GDP_trn'],js(root/T/'N3/N3_Actual_Annual.json')[i]['real_GDP_trn']);ck('N3GIoff:'+str(i),r['government_purchase_nominal_trn']+r['public_investment_nominal_trn'])
  impacts.append(dict(case='N3_BASE_UNCHANGED',year=r['year'],real_GDP_trn=r['real_GDP_trn'],limitation='existingnative replay;notnewchangedbridge'))
  impacts.append(dict(case='N3_ALIGNED_BRANCH_NOT_EXECUTED',year=r['year'],real_GDP_trn=None,limitation='Runner.base/sq cached policy ledgers,medicalinit,wagesprofitspricesfiscal refs require coherent shared-base rebuild; SQoffset only invalid;N/A'))
 dump(out/'F_N3_Aligned_Labor_Impact_And_Compatibility.csv',impacts)
 # Verify every externally opened runtime input against the request-fixed git object.
 runtime={}
 for c in SQ+list(F_MATCH)+['N3_BASE_UNCHANGED']:
  for name in ['Runtime_Source_Receipts.json','Bridge_Runtime_Source_Receipts.json']:
   if (out/c/name).exists():
    for rec in js(out/c/name):
     path=rec['path']
     if path.startswith('handoff/chatgpt-labor-timing-older-workers-annual-hours-20261123/'):continue
     runtime[path]=rec
 for path,rec in sorted(runtime.items()):
  b=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);ck('runtimebytes:'+path,0 if len(b)==rec['size'] and hashlib.sha256(b).hexdigest()==rec['sha256'] else 1,0,0)
 save(out/'Fixed_Dependency_Receipts.json',source);save(out/'Runtime_Dependency_Receipts.json',list(runtime.values()));dump(out/'Verification_Checks.csv',checks)
 save(out/'Verification.json',dict(status='PASS',new_checks=len(checks),failed=0,N3_existing_checks=nc['checks'],N3_existing_failed=len(nc['failures']),SQ_paths=len(SQ),F_paths=len(F_MATCH),N3_replay_paths=1,annual_rows=(len(SQ)+len(F_MATCH)+1)*30,new_changed_N3_executed=False,originals=len(list((inputs.parent/'Source_Originals').glob('*.json'))),statistics_cells=len(read(inputs.parent/'Official_Extracted_Cells.csv')),key2055=[r for r in compar if r['year']==2055],F2055=[r for r in impacts if r['year']==2055],benchmark_gap=parts,RP023_M1925='HOLD',RP024='PENDING',formal_acceptance=False))
 print(json.dumps(dict(PASS=True,new_checks=len(checks),annual_rows=(len(SQ)+len(F_MATCH)+1)*30)),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.out.resolve(),a.inputs.resolve())
