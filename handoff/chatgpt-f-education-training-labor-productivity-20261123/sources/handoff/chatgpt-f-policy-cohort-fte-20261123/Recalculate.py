"""Isolated F cohort time bridge. Python stdlib; no network, policy or engine edits."""
import csv,hashlib,json,math,subprocess,sys,shutil
from pathlib import Path
sys.dont_write_bytecode=True
import Pinned_F_Adapter as A
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PRIOR=ROOT/'handoff/chatgpt-labor-timing-older-workers-annual-hours-20261123'
CASES=['BASE_SQ_UNCHANGED','PREVIOUS_FINE_AGE_HOURS','ANNUAL_ALIGNED_FULL_RATES','OCTOBER_NEAR_FULL_RATES','ANNUAL_FINE_WEEK_HOURS','ANNUAL_MONTH_HOURS_PROFILE']
def js(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def main(out):
 out.mkdir(parents=True,exist_ok=True);checks=[]
 def ck(name,a,b,tol=1e-7):
  error=abs(a-b);passed=math.isfinite(error) and error<=tol+1e-11*abs(b)
  checks.append(dict(check=name,error=error,tolerance=tol,passed=passed));assert passed,(name,a,b)
 receipts=[]
 for e in js(HERE/'Fixed_Source_Expected.json'):
  b=(ROOT/e['path']).read_bytes();blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
  ck('source_size:'+e['path'],len(b),e['size'],0);ck('source_git_blob:'+e['path'],int(blob!=e['git_blob_sha1']),0,0)
  receipts.append(dict(**e,sha256=hashlib.sha256(b).hexdigest(),retrieval='connected GitHub fetch/fetch_file, pinned commit/blob',comparison='OWN_BYTES_MATCH'))
 save(out/'Fixed_Source_Receipts.json',receipts)
 inp=js(PRIOR/'Fixed_Aligned_Case_Inputs.json');stats=js(PRIOR/'Statistics_Inputs.json')
 hours={(r['series'],r['sex'],r['age_lower']):r['annual_hours_per_employed'] for r in stats['hours']}
 refs=list(csv.DictReader((ROOT/'handoff/chatgpt-n3-aligned-labor-baseline-20261123/SQ_F_N3_Aligned_Labor_Annual_2026_2055.csv').open()))
 ref={(r['labor_case'],int(r['year'])):r for r in refs};cohorts=[];compar=[];logs=[]
 for case in CASES:
  oldcase='F_BASE_UNCHANGED' if case=='BASE_SQ_UNCHANGED' else 'F_'+case
  old=js(PRIOR/oldcase/'F_Actual_Annual.json');ot=js(PRIOR/oldcase/'F_Runtime_Trace.json')['years']
  offset=inp['F_offsets'][oldcase]
  # Execute unchanged full F engine first, including coherent prior common offset.
  replay=out/(case+'_REPLAY');replay.mkdir(exist_ok=True)
  A.f(ROOT,replay,offset,[0.]*30)
  rb=js(replay/'F_Actual_Annual.json');ledger=js(replay/'Policy_Base_Ledgers.json')
  common=inp['cases'][case];L0=inp['cases']['BASE_SQ_UNCHANGED']['engine_L'][0]
  H0=common['hours'][0];units_per_hour=L0/H0 if H0 else 1/2080
  series='MONTH_MEAN12_PROFILE' if case=='ANNUAL_MONTH_HOURS_PROFILE' else 'DETAILED_WEEK52'
  delta=[];elderhours=[]
  for i,e in enumerate(ledger['elder']):
   h=0.;jobs=0.
   for age,label in [(65,'65_69'),(70,'70_74'),(75,'75plus')]:
    for sex in ['male','female']:
     n=e[label+'_'+sex+'_extra_jobs'];lookup=min(age,65) if series=='MONTH_MEAN12_PROFILE' else age
     coefficient=hours[series,sex,lookup];h+=n*coefficient;jobs+=n
     cohorts.append(dict(case=case,year=2026+i,cohort='ELDER_ADDITIONAL',age_group=label,sex=sex,headcount=n,annual_hours_coefficient=coefficient,conditional_hours=n*coefficient,conditional_FTE_2080=n*coefficient/2080,engine_units=n*coefficient*units_per_hour,definition='2025 pooled observed profile transferred to marginal F workers; conditional annualization, not actual annual hours',start_year=2028,assumption_retained='policy conversion probabilities and headcounts fixed; no observed marginal-worker hours',source='existing elder ledger; Statistics_Inputs.json hours',original='FreedomPolicies.md 4; Annex 4B'))
   ck(case+':elder_headcount:'+str(i),jobs,e['F_extra_jobs'],1e-5)
   delta.append(h*units_per_hour-e['effective_extra']);elderhours.append(h)
   for kind,key,fields in [('FOREIGN','foreign',('policy_only_foreign_jobs','foreign_effective_labor')),('PENSION','pension',('additional_jobs','additional_effective_labor'))]:
    r=ledger[key][i];cohorts.append(dict(case=case,year=2026+i,cohort=kind,headcount=r.get(fields[0]),engine_units=r.get(fields[1]) if kind=='PENSION' else None,existing_total_foreign_effective_labor=r.get(fields[1]) if kind=='FOREIGN' else None,existing_hours_equivalent_workers=r.get('hours_equivalent_workers'),annual_hours_coefficient=None,conditional_hours=None,conditional_FTE_2080=None,definition='EXISTING_ASSUMPTION_PRESERVED; not observed FTE',assumption_retained='No invented age-sex allocation or nationality-specific hours; foreign total effective stock is not policy addition',source='existing '+key+' ledger',original='FreedomPolicies.md 4; Annex 5' if kind=='FOREIGN' else 'FreedomPolicies.md 4 pension'))
  target=out/case;target.mkdir(exist_ok=True);A.f(ROOT,target,offset,delta)
  new=js(target/'F_Actual_Annual.json');nt=js(target/'F_Runtime_Trace.json')['years']
  save(target/'Connection_Inputs.json',dict(common_offset=offset,elder_delta=delta,engine_units_per_hour=units_per_hour,FTE_reference_hours=2080,hours_series=series,foreign_pension_education_health='existing assumptions preserved; physical FTE N/A'))
  annual=[]
  for i,(r,o,t) in enumerate(zip(new,old,nt)):
   y=2026+i;rr=ref[case,y];e=ledger['elder'][i];p=ledger['pension'][i];fo=ledger['foreign'][i]
   for metric in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','household_disposable_nominal_trn','labor_force_population_proxy']:
    ck('replay:'+case+str(y)+metric,rb[i][metric],o[metric],1e-6)
   for k in ['risk','inflation']:ck('fixed:'+case+str(y)+k,t[k],ot[i][k])
   for k in ['education_effective_added','health_effective_added','trajectory_effective_L','elder_effective_added']:ck('retained_channel:'+case+str(y)+k,t[k],ot[i][k],1e-5)
   ck('F_reference:'+case+str(y),float(rr['F_real_GDP_trn']),o['real_gdp_trn'],1e-6)
   ck('one_common_and_one_cohort:'+case+str(y),t['labor'],t['trajectory_effective_L']+t['education_effective_added']+t['health_effective_added']+t['elder_effective_added']+offset[i]+(delta[i] if i else 0),1e-5)
   ck('GDPidentity:'+case+str(y),t['Y'],t['desired']-t['unmet'])
   for k in ['population']:ck('fixed_demography:'+case+str(y)+k,r[k],o[k])
   ck('FTEidentity:'+case+str(y),elderhours[i]/2080*2080,elderhours[i],1e-4)
   if y==2026:
    ck('anchor_real:'+case,r['real_gdp_trn'],580);ck('anchor_nominal:'+case,r['nominal_gdp_trn'],600)
   if y<2028:ck('no_early_cohort:'+case+str(y),delta[i],0)
   for kind,k in [('EDUCATION','education_effective_added'),('HEALTH','health_effective_added')]:
    cohorts.append(dict(case=case,year=y,cohort=kind,headcount=None,engine_units=t[k],annual_hours_coefficient=None,conditional_hours=None,conditional_FTE_2080=None,definition='EXISTING_PRODUCTIVITY_OR_TIME_EQUIVALENT; not additional persons',assumption_retained='existing model response and denominators retained; no invented cohort distribution',source='F education/medical model',original='FreedomPolicies.md 4; Annex 4'))
   row=dict(case=case,year=y,old_F_real_GDP_trn=o['real_gdp_trn'],new_F_real_GDP_trn=r['real_gdp_trn'],delta_real_GDP_trn=r['real_gdp_trn']-o['real_gdp_trn'],SQ_real_GDP_trn=float(rr['SQ_real_GDP_trn']),N3_real_GDP_trn=float(rr['N3_real_GDP_trn']),new_F_minus_SQ_trn=r['real_gdp_trn']-float(rr['SQ_real_GDP_trn']),new_F_minus_N3_trn=r['real_gdp_trn']-float(rr['N3_real_GDP_trn']),old_engine_L=ot[i]['labor'],new_engine_L=t['labor'],delta_engine_L=t['labor']-ot[i]['labor'],common_offset_once=offset[i],elder_headcount=e['F_extra_jobs'],elder_conditional_hours=elderhours[i],elder_conditional_FTE_2080=elderhours[i]/2080,elder_old_effective=e['effective_extra'],elder_new_engine_units=elderhours[i]*units_per_hour,cohort_direct_engine_delta=delta[i],total_employed_persons_proxy=ledger['d'][i]['domestic_employed_conditional']+fo['foreign_jobs']+e['F_extra_jobs']+p['additional_jobs'],total_actual_hours=None,total_actual_FTE=None,foreign_specific_hours=None,physical_hours_coverage='ELDER_ONLY; others preserved assumptions, total N/A',hours_series=series)
   for metric in ['nominal_gdp_trn','nominal_wage_proxy_man','real_wage_proxy_man','tax_diagnostic_trn','government_partial_balance_proxy_trn','consolidated_partial_balance_proxy_trn','household_disposable_nominal_trn','capital_total_real_trn']:
    row['new_'+metric]=r.get(metric);row['old_'+metric]=o.get(metric);row['delta_'+metric]=r[metric]-o[metric] if isinstance(r.get(metric),(int,float)) and isinstance(o.get(metric),(int,float)) else None
   annual.append(row)
  ck('30_years:'+case,len(annual),30,0);dump(target/'Annual_Comparison_2026_2055.csv',annual);compar+=annual
  logs.append(dict(case=case,replay_rows=len(rb),changed_rows=len(new),SQ_N3_recalculated=False))
 # Retain required annual comparisons, trace, connection inputs and one shared
 # unchanged policy ledger/source. Full intermediate medical/replay files are
 # reproducible working data, not separate handoff deliverables.
 first=out/CASES[0];shared_ledger=(first/'Policy_Base_Ledgers.json').read_bytes();shared_source=(first/'Resolved_F_Cohort_Runtime.py.txt').read_bytes()
 (out/'Policy_Base_Ledgers.json').write_bytes(shared_ledger);(out/'Resolved_F_Cohort_Runtime.py.txt').write_bytes(shared_source)
 for case in CASES:
  d=out/case
  ck('shared_policy_ledger:'+case,int((d/'Policy_Base_Ledgers.json').read_bytes()!=shared_ledger),0,0)
  ck('shared_runtime_source:'+case,int((d/'Resolved_F_Cohort_Runtime.py.txt').read_bytes()!=shared_source),0,0)
  for p in d.iterdir():
   if p.name not in ['F_Runtime_Trace.json','Connection_Inputs.json','Annual_Comparison_2026_2055.csv']:p.unlink()
  shutil.rmtree(out/(case+'_REPLAY'))
 dump(out/'Annual_Comparison_All_Cases.csv',compar);dump(out/'Key_Years.csv',[r for r in compar if r['year'] in [2026,2030,2035,2040,2045,2050,2055]])
 dump(out/'Policy_Cohort_Headcount_Hours_FTE_Map.csv',cohorts);dump(out/'Validation_Checks.csv',checks)
 save(out/'Validation.json',dict(new_checks=len(checks),failed=sum(not r['passed'] for r in checks),paths=12,executed_year_rows=360,comparison_rows=180,conditional_elder_FTE_only=True,full_observed_cohort_FTE=False,RP023_M1925='HOLD',RP024='PENDING',formal_acceptance=False));save(out/'Execution_Log.json',logs)
if __name__=='__main__':main(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE)
