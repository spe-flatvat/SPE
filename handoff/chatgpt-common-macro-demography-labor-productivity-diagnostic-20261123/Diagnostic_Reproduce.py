"""Stdlib: python Diagnostic_Reproduce.py --root <fixed checkout> --out <empty dir>.
Reconstruct age/sex cells independently; run fixed SQ engine with isolated L/A hooks.
"""
import argparse,base64,copy,csv,hashlib,itertools,json,math,platform,subprocess,sys,zlib
from pathlib import Path
sys.dont_write_bytecode=True
PIN='77bbad59356407106ff333582040511590bbd7e4'
TARGET='e981c924adbe9c7ca77b96d2dc94e40378186613'
CLAUDE='3611534d85fb52c976592c96120f7663dbfa63f5'
T='handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123'
HERE=Path(__file__).resolve().parent
CASES=['BASE_SQ_REPLAY','L_FIXED','A_FIXED','POPULATION_ONLY','AGE_SEX_FIXED','NATIONALITY_SHARE_FIXED','BROAD_AGE_FIXED','WITHIN_AGE_SEX_FIXED']
def js(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def raw(root,pin,path):return subprocess.check_output(['git','show',pin+':'+path],cwd=root)
def run(root,out):
 out.mkdir(parents=True,exist_ok=True);checks=[]
 def ck(name,a,b,tol=1e-7):
  error=abs(a-b);ok=math.isfinite(error) and error<=tol+1e-12*abs(b)
  checks.append(dict(check=name,error=error,tolerance=tol,passed=ok));assert ok,(name,a,b)
 receipts=[]
 # Read all fixed comparison and independent verification originals as bytes.
 for pin,folder in [(TARGET,T),(CLAUDE,'handoff/claude-three-scenario-verification-20261123')]:
  paths=subprocess.check_output(['git','ls-tree','-r','--name-only',pin,'--',folder],cwd=root,text=True).splitlines()
  for path in paths:
   b=raw(root,pin,path);local=root/path
   if local.exists():ck('fixed_local:'+path,0 if local.read_bytes()==b else 1,0,0)
   receipts.append(dict(commit=pin,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),route='git show fixed commit after GitHub clone',local_matches_fixed=local.read_bytes()==b if local.exists() else 'NOT_MATERIALIZED'))
 sq=js(root/T/'BASE_REPLAY/Common_Trace_BASE_REPLAY.json')['years']
 # Actual SQ demography exported by prior runtime; validate against new live capture below.
 olddemo=list(csv.DictReader((root/'handoff/chatgpt-sq-growth-diagnosis-20261122/SQ_Demography_Labor_Accounting.csv').open()))
 fc=js(root/'handoff/f-foreign-quantity-20261120/Inputs.json');c=fc['stage1_inputs']['previous_inputs'];b=c['base'];rates=c['employment_rates_2025']
 embedded=zlib.decompress(base64.b64decode(fc['stage1_inputs']['previous_model_zlib_base64']))
 ck('embedded_labor_source_sha',0 if hashlib.sha256(embedded).hexdigest()==fc['stage1_inputs']['previous_model_sha'] else 1,0,0)
 (out/'Resolved_Embedded_Age_Sex_Labor.py.txt').write_bytes(embedded)
 def profile(key,y):
  lo=y//5*5;hi=min(lo+5,2055);f=(y-lo)/5 if hi>lo else 0
  return {int(a):[(1-f)*c[key][str(lo)][a][s]+f*c[key][str(hi)][a][s] for s in [0,1]] for a in c[key][str(lo)]}
 def group(a):return 0 if a<15 else 1 if a<65 else 2
 def er(a,s):
  if a<15:return 0.
  ix=0 if a<25 else 1 if a<35 else 2 if a<45 else 3 if a<55 else 4 if a<60 else 5 if a<65 else 6 if a<70 else 7 if a<75 else 8
  return rates['male' if s==0 else 'female'][ix]
 cells=[];states=[]
 for i,y in enumerate(range(2026,2056)):
  t={k:float(v) for k,v in olddemo[i].items() if v and k!='year'};P=t['population'];F=t['foreign'];J=t['japanese'];ref=b['population_reference'][str(y)];r25=b['population_reference']['2025'];obs=b['official_initial_2025_oct'];df=obs['foreign']-r25['foreign']
  jw=ref['japanese_working_age']+obs['working_age']-r25['working_age']-df*(r25['working_age']-r25['japanese_working_age'])/r25['foreign']
  je=ref['japanese_elderly']+obs['elderly']-r25['elderly']-df*(r25['elderly']-r25['japanese_elderly'])/r25['foreign'];targets=[J-jw-je,jw,je]
  jp=profile('age_japanese_five_year',y);total=profile('age_all_five_year',y);fp={a:[total[a][s]-jp[a][s] for s in [0,1]] for a in jp}
  den=[sum(v[s] for a,v in jp.items() for s in [0,1] if group(a)==g) for g in range(3)];fd=sum(sum(v) for v in fp.values());counts={}
  for nat,prof in [('J',jp),('F',fp)]:
   pop=J if nat=='J' else F;counts[nat]={}
   for a,v in prof.items():
    for s in [0,1]:
     n=v[s]/den[group(a)]*targets[group(a)] if nat=='J' else v[s]/fd*F
     rate=er(a,s);counts[nat][(a,s)]=n/pop
     cells.append(dict(year=y,nationality=nat,age_lower=a,sex='male' if s==0 else 'female',broad_age=group(a),persons=n,employment_rate=rate,employed_conditional=n*rate,relative_VA_weight=1.,hours_adjustment='NOT_CONNECTED_SQ'))
  E={nat:sum(w*er(a,s) for (a,s),w in counts[nat].items()) for nat in ['J','F']}
  ck('independent_domestic_employment:'+str(y),J*E['J'],t['domestic_employed_conditional'],1e-5);ck('independent_foreign_employment:'+str(y),F*E['F'],t['foreign_employed_conditional'],1e-5)
  ck('independent_L:'+str(y),J*E['J']+F*E['F'],sq[i]['labor'],1e-5)
  states.append(dict(year=y,P=P,f=F/P,dist=counts,t=t))
 def dist(st,nat,broadstate,withinstate):
  actual=st['dist'][nat];bd=broadstate['dist'][nat];wd=withinstate['dist'][nat]
  bg={g:sum(v for (a,s),v in bd.items() if group(a)==g) for g in range(3)}
  wg={g:sum(v for (a,s),v in wd.items() if group(a)==g) for g in range(3)}
  return sum(bg[group(a)]*v/wg[group(a)]*er(a,s) for (a,s),v in wd.items())
 def labor(st,Pst=None,Nst=None,Bst=None,Wst=None):
  P=(Pst or st)['P'];f=(Nst or st)['f'];Bst=Bst or st;Wst=Wst or st
  return P*((1-f)*dist(st,'J',Bst,Wst)+f*dist(st,'F',Bst,Wst))
 init=states[0];L0=sq[0]['labor'];labs={k:[] for k in CASES}
 for st in states:
  for cid in CASES:
   value=L0 if cid=='L_FIXED' else labor(st,Pst=st,Nst=init,Bst=init,Wst=init) if cid=='POPULATION_ONLY' else labor(st,Bst=init,Wst=init) if cid=='AGE_SEX_FIXED' else labor(st,Nst=init) if cid=='NATIONALITY_SHARE_FIXED' else labor(st,Bst=init) if cid=='BROAD_AGE_FIXED' else labor(st,Wst=init) if cid=='WITHIN_AGE_SEX_FIXED' else sq[st['year']-2026]['labor']
   labs[cid].append(value)
 inputs=dict(fixed_commit=PIN,initial_real=580,initial_nominal=600,labor=labs,common_L_offset=[L0-r['labor'] for r in sq],employment_rates=rates,relative_VA_weight=1.,cases={k:dict(status='ISOLATED_NOT_ADOPTED',population_ledger_changed=False,real_A_events_removed=k=='A_FIXED',inflation_events_unchanged=True) for k in CASES+['F_BASE','F_COMMON_L_FIXED']})
 save(out/'Fixed_Diagnostic_Inputs.json',inputs);dump(out/'SQ_Age_Sex_Employment_Cells_2026_2055.csv',cells)
 logs=[];results={}
 for case in CASES+['F_BASE','F_COMMON_L_FIXED']:
  cmd=[sys.executable,str(HERE/'Diagnostic_Worker.py'),'--root',str(root),'--out',str(out/case),'--case',case,'--inputs',str(out/'Fixed_Diagnostic_Inputs.json')]
  z=subprocess.run(cmd,text=True,capture_output=True);logs.append(dict(case=case,command='python Diagnostic_Worker.py --root <fixed-root> --out <out>/'+case+' --case '+case+' --inputs <out>/Fixed_Diagnostic_Inputs.json',exit_code=z.returncode,stdout=z.stdout,stderr=z.stderr));save(out/'Execution_Log.json',logs)
  if z.returncode:raise RuntimeError(z.stderr)
  print(case,z.stdout.strip(),flush=True)
  if case in CASES:results[case]=js(out/case/('Common_Trace_'+case+'.json'))
 base=results['BASE_SQ_REPLAY']['years'];p=results['BASE_SQ_REPLAY']['parameters'];alpha=p['labor_response']
 annual=[];counter=[];attrib=[];events=[];A=1.;growth_only=1.
 for i,(st,r) in enumerate(zip(states,base)):
  y=st['year'];t=r['demography'];old=sq[i];P=st['P'];f=st['f']
  for k in ['Y','N','coreY','coreN','coreD','labor','risk','inflation','population']:ck('base_replay:'+str(y)+k,r[k],old[k])
  for k in ['population','foreign','japanese','working_age','elderly','domestic_employed_conditional','foreign_employed_conditional','effective_productive_workers']:ck('live_demography:'+str(y)+k,t[k],st['t'][k],1e-5)
  ck('population_split:'+str(y),t['population'],t['japanese']+t['foreign']);ck('age_split:'+str(y),P,t['under15']+t['working_age']+t['elderly'])
  if i:
   prev=base[i-1]['demography'];ck('population_bridge:'+str(y),P-prev['population'],t['births_calendar']-t['deaths_calendar']+t['foreign_net_migration']+t['population_reference_bridge']);ck('foreign_bridge:'+str(y),t['foreign']-prev['foreign'],t['foreign_net_migration']+t['foreign_nonmigration_reference_residual'])
   A*=1+p['base_growth']-r['risk'];growth_only*=1+p['base_growth']
  ck('A:'+str(y),A,r['nonlabor_factor']);core=580*A*(r['labor']/L0)**alpha;ck('independent_core:'+str(y),core,r['coreY']);ck('final_identity:'+str(y),r['Y'],r['desired']-r['unmet']);ck('full_final_decomposition:'+str(y),r['Y']-r['coreY'],p['capacity_absorption']*r['supply']+r['C']+r['I']+r['education_nom']/r['coreD']+r['education_level']+r['finite']+r['service_nominal']/r['coreD']-r['unmet']);ck('nominal_identity:'+str(y),r['N'],r['Y']*r['coreD']*(1+r['pressure']))
  for cid,data in results.items():
   q=data['years'][i];expect=580*(1 if cid=='A_FIXED' else A)*(labs[cid][i]/L0)**alpha
   ck('counter_core:'+cid+str(y),q['coreY'],expect);ck('counter_labor:'+cid+str(y),q['labor'],labs[cid][i],1e-5)
   ck('counter_initial_boundary:'+cid, data['years'][0]['Y'],580);ck('counter_nominal_boundary:'+cid,data['years'][0]['N'],600)
   ck('events_unchanged:'+cid+str(y),q['risk'],r['risk']);ck('inflation_unchanged:'+cid+str(y),q['inflation'],r['inflation']);ck('medical_ref_unchanged:'+cid+str(y),q['medical_input_deflator'],r['medical_input_deflator'])
   counter.append(dict(case=cid,year=y,L_used=q['labor'],A_used=q['nonlabor_factor'],population_unchanged=q['population'],core_real_GDP_trn=q['coreY'],final_real_GDP_trn=q['Y'],nominal_GDP_trn=q['N'],GDP_minus_BASE_SQ_trn=q['Y']-r['Y'],C=q['C'],I=q['I'],supply=q['supply'],desired=q['desired'],capacity=q['capacity'],unmet=q['unmet'],pressure=q['pressure'],risk_schedule=q['risk'],input_inflation=q['inflation'],status='REAL_A_FIXED_REMOVES_REAL_BASE_GROWTH_AND_EVENT_ACCUMULATION' if cid=='A_FIXED' else 'ISOLATED_L_CONNECTION_ONLY'))
  # Five factor exact Shapley allocation of core GDP level difference: all 32 subsets.
  factors=['A','population_scale','nationality_mix','broad_age_mix','within_age_sex_mix'];values={}
  for mask in range(32):
   L=labor(st,Pst=st if mask&2 else init,Nst=st if mask&4 else init,Bst=st if mask&8 else init,Wst=st if mask&16 else init)
   values[mask]=580*(A if mask&1 else 1)*(L/L0)**alpha
  contributions=[]
  for j,name in enumerate(factors):
   v=0.
   for mask in range(32):
    if not mask&(1<<j):
     n=mask.bit_count();v+=math.factorial(n)*math.factorial(4-n)/math.factorial(5)*(values[mask|1<<j]-values[mask])
   contributions.append(v);attrib.append(dict(year=y,factor=name,Shapley_core_change_trn=v,method='exact 32 coalitions; age shares mechanical identification; fixed observed-reference rates',identified=True))
  ck('shapley_closure:'+str(y),sum(contributions),r['coreY']-580)
  ax=580*(A-1);lx=580*((r['labor']/L0)**alpha-1);cross=580*(A-1)*((r['labor']/L0)**alpha-1)
  ck('A_L_product_closure:'+str(y),ax+lx+cross,r['coreY']-580)
  for name,value,status in [('A_standalone',ax,'IDENTIFIED'),('L_standalone',lx,'IDENTIFIED'),('A_x_L',cross,'IDENTIFIED'),('A_then_L_first',ax,'ORDERED'),('A_then_L_second',lx+cross,'ORDERED'),('L_then_A_first',lx,'ORDERED'),('L_then_A_second',ax+cross,'ORDERED'),('employment_rate_time_change',0.,'RATES_FIXED_NOT_OBSERVED_FUTURE'),('relative_VA_time_change',0.,'UNITY_FIXED_NOT_PRODUCTIVITY_FORECAST'),('hours_change',None,'NOT_CONNECTED'),('TFP_or_capital_substitution',None,'NOT_IDENTIFIABLE')]:attrib.append(dict(year=y,factor=name,Shapley_core_change_trn=value,method=status,identified=value is not None))
  annual.append(dict(year=y,**{k:t[k] for k in ['population','japanese','foreign','under15','working_age','elderly','domestic_employed_conditional','foreign_employed_conditional','effective_productive_workers','foreign_net_migration','population_reference_bridge','foreign_nonmigration_reference_residual']},L_used=r['labor'],L_ratio=r['labor']/L0,labor_elasticity=alpha,labor_level_factor=(r['labor']/L0)**alpha,A=A,base_growth_only_factor=growth_only,risk_relative_accumulation=A/growth_only,core_real_GDP_trn=r['coreY'],final_real_GDP_trn=r['Y'],core_final_gap_trn=r['Y']-r['coreY'],independent_core_residual=core-r['coreY'],C=r['C'],I=r['I'],additional_capital=r['K'],supply=r['supply'],desired=r['desired'],capacity=r['capacity'],unmet=r['unmet'],price_pressure=r['pressure'],domestic_employment_per_resident=t['domestic_employed_conditional']/t['japanese'],foreign_employment_per_resident=t['foreign_employed_conditional']/t['foreign'],employment_rates='2025_AGE_SEX_CONSTANT',hours='NOT_CONNECTED',relative_VA=1.,TFP='NOT_IDENTIFIABLE',capital_core_rule='3*coreY_ENDOGENOUS_ACCOUNTING_NOT_INDEPENDENT_INPUT'))
  events.append(dict(year=y,risk=r['risk'],base_multiplier=1.01,actual_A_multiplier=1 if not i else 1.01-r['risk'],risk_relative_multiplier=1 if not i else (1.01-r['risk'])/1.01,permanent_no_recovery=True,initial_transition=i>0))
 dump(out/'SQ_Annual_Population_Labor_A_Core_GDP_2026_2055.csv',annual);dump(out/'SQ_Limited_Labor_Productivity_Counterfactuals_2026_2055.csv',counter);dump(out/'SQ_Labor_Decline_Attribution_And_Interactions.csv',attrib);dump(out/'SQ_Nonlabor_Growth_Event_Accumulation.csv',events)
 # F minimal live control: remove same SQ common decline, retain all F endogenous increments.
 fr=js(out/'F_BASE/F_Actual_Annual.json');ft=js(out/'F_BASE/F_Runtime_Trace.json')['years'];ff=js(out/'F_COMMON_L_FIXED/F_Actual_Annual.json');fft=js(out/'F_COMMON_L_FIXED/F_Runtime_Trace.json')['years'];oldf=js(root/T/'F/F_Actual_Annual.json');n3=js(root/T/'N3/N3_Actual_Annual.json');impact=[]
 for i,r in enumerate(base):
  y=r['year'];q=results['L_FIXED']['years'][i]
  ck('F_base_replay_Y:'+str(y),fr[i]['real_gdp_trn'],oldf[i]['real_gdp_trn']);ck('F_base_replay_N:'+str(y),fr[i]['nominal_gdp_trn'],oldf[i]['nominal_gdp_trn'])
  # F policy modules may respond to changed lagged GDP; preserve inputs, not numerical policy deltas.
  for cid,arr,tr,sqref in [('F_BASE',fr,ft,r),('F_COMMON_L_FIXED',ff,fft,q)]:
   z=tr[i];ck('F_initial_real:'+cid,arr[0]['real_gdp_trn'],580);ck('F_initial_nominal:'+cid,arr[0]['nominal_gdp_trn'],600);ck('F_event:'+cid+str(y),z['risk'],r['risk']);ck('F_inflation:'+cid+str(y),z['inflation'],r['inflation'])
   impact.append(dict(case=cid,year=y,real_GDP_trn=arr[i]['real_gdp_trn'],SQ_same_diagnostic_GDP_trn=sqref['Y'],GDP_minus_matched_SQ_trn=arr[i]['real_gdp_trn']-sqref['Y'],labor=z['labor'],common_labor_offset=0 if cid=='F_BASE' else inputs['common_L_offset'][i],scope='LIVE_F_SAME_SHARED_SQ_L_OFFSET_ALL_EXISTING_POLICY_MODULES_REEXECUTED',status='DIAGNOSTIC_NOT_ADOPTED'))
  impact.append(dict(case='N3_BASE_REUSED',year=y,real_GDP_trn=n3[i]['real_GDP_trn'],SQ_same_diagnostic_GDP_trn=r['Y'],GDP_minus_matched_SQ_trn=n3[i]['real_GDP_trn']-r['Y'],labor=r['labor'],common_labor_offset=0,scope='FIXED_CORE_SQ_POP_L;GI_GOVERNMENT_OFF',status='EXISTING_FIXED_RESULT_REUSED'))
  impact.append(dict(case='N3_L_FIXED_CORE_ONLY',year=y,real_GDP_trn=None,SQ_same_diagnostic_GDP_trn=q['Y'],GDP_minus_matched_SQ_trn=None,labor=L0,common_labor_offset=inputs['common_L_offset'][i],scope='shared core would change '+str(q['coreY']-r['coreY'])+' trn; must rebuild cached SQ and N3 base states, price, wage, tax, medical references',status='FINAL_N3_NOT_RECALCULATED_NO_VALID_MINIMAL_SHARED_CORE_OVERRIDE'))
 dump(out/'F_N3_Common_Labor_Connection_Impact.csv',impact)
 # Runtime reads: actual bytes verified against request fixed tree independently.
 seen={}
 for folder in ['handoff/demography-improved-scenarios-20261118','handoff/demography-foreign-research-20261118','handoff/chatgpt-sq-growth-diagnosis-20261122']:
  for path in sorted((root/folder).rglob('*')):
   if path.is_file() and '__pycache__' not in str(path):
    z=path.read_bytes();seen[str(path.relative_to(root))]=dict(path=str(path.relative_to(root)),size=len(z),sha256=hashlib.sha256(z).hexdigest())
 for path in ['policies/StatusQuo.md']:
  z=(root/path).read_bytes();seen[path]=dict(path=path,size=len(z),sha256=hashlib.sha256(z).hexdigest())
 for case in CASES+['F_BASE','F_COMMON_L_FIXED']:
  for rec in js(out/case/'Runtime_Source_Receipts.json'):seen[rec['path']]=rec
 for path,rec in sorted(seen.items()):
  z=raw(root,PIN,path);ck('runtime_fixed_source:'+path,0 if hashlib.sha256(z).hexdigest()==rec['sha256'] and len(z)==rec['size'] else 1,0,0);receipts.append(dict(commit=PIN,route='runtime open audit and fixed Git object comparison',**rec))
 save(out/'Fixed_Source_Receipts.json',receipts);dump(out/'Verification_Checks.csv',checks)
 summary=dict(status='PASS',checks=len(checks),failures=0,executed_paths=10,annual_rows=300,SQ_paths=8,F_paths=2,N3_new_final_paths=0,source_receipts=len(receipts),python=platform.python_version(),initial_population=base[0]['population'],policy_text_initial_population=121500000,initial_population_difference=base[0]['population']-121500000,below580_first=next(r['year'] for r in base if r['Y']<580),below580_years=sum(r['Y']<580 for r in base),keyyears=[r for r in annual if r['year'] in [2026,2030,2035,2039,2055]],counterfactual2055=[r for r in counter if r['year']==2055],attribution2055=[r for r in attrib if r['year']==2055],F_impact2055=[r for r in impact if r['year']==2055],previous_2826_and_Claude_2845='REUSED_FIXED_TARGET_ONLY; not independent verification of new branches',originals_changed=False,RP023_M1925='HOLD',RP024='PENDING')
 save(out/'Verification.json',summary);print(json.dumps(dict(status='PASS',checks=len(checks),rows=300)),flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--out',type=Path,required=True);x=a.parse_args();run(x.root.resolve(),x.out.resolve())
