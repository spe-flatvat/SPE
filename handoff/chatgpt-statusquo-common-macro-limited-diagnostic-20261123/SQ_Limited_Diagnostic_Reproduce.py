#!/usr/bin/env python3
"""Separate SQ families; rerun exact variants and three single-change diagnostics.
Never edits a shared source/input or substitutes a diagnostic as the benchmark.
"""
import argparse,csv,hashlib,importlib.util,json,math,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
PIN='71bbfd6a31ceb58d34b1dfcf52eec7baadb16579'
OLD='handoff/f-statusquo-provisional-20261115';DIAG='handoff/chatgpt-sq-growth-diagnosis-20261122';ND='handoff/chatgpt-n3-f-parity-implementation-20261122';F='handoff/f-common-endoflife-finalization-20261121'
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,a):
 keys=list(dict.fromkeys(k for r in a for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(a)
def write(p,a):p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n')
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def run(root,out):
 out.mkdir(parents=True,exist_ok=True);checks=[]
 def ck(n,e,tol=1e-6):checks.append(dict(check=n,error=e,tolerance=tol,pass_=math.isfinite(e) and abs(e)<=tol))
 # Exact old adapter function calls, using the embedded original v6 engine;
 # only the four specified historical SQ families are executed.
 m=module('old_sq_model',root/OLD/'SPE_StatusQuo_Provisional_Model_DRAFT_20261115.py');cfg=json.loads((root/OLD/'SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json').read_text());src=cfg['sq_bundle']['sources']
 sonzei,oldlogs=m.sources_and_v02(cfg,root/OLD);sonzei={(r['case_id'],r['year']):r for r in sonzei}
 engine=m.load_module('limited_old_v6',src['prototype.py']['utf8']);wage=m.load_module('limited_old_wage',src['m14_wage_anchor.py']['utf8'])
 oldcases=['SQ_V5_CANDIDATE_29','SQ_POLICY9_LOW_29','SQ_POLICY9_HIGH_29','SQ_V5_LEGACY30'];oldruns={c:m.simulate(cfg,c,engine,wage,sonzei) for c in oldcases}
 oldfixed={(r['case'],int(r['year'])):r for r in rd(root/OLD/'SPE_F_StatusQuo_Annual_Comparison_DRAFT_20261115.csv') if r['record_type']=='PATH'}
 annual=[];decomposition=[];events=[];definitions=[];summ=[];provenance=[];traces={};comparison=[]
 for cid,a in oldruns.items():
  legacy=cid.endswith('30');family='OLD_V6_PROVISIONAL';priorY=580.;priorN=600.;priorP=121500000.
  for z in a:
   y=z['year'];initial=z['row_kind']=='INITIAL_STATE';D=z['nominal_gdp_trn']/z['real_gdp_trn'];pi=z['inflation_pct']/100 if z['inflation_pct'] is not None else None;g=z['real_growth_pct']/100 if z['real_growth_pct'] is not None else None
   for k in ['real_gdp_trn','nominal_gdp_trn','tax_revenue_trn','population_persons']:ck(cid+str(y)+':original_replay_'+k,z[k]-float(oldfixed[cid,y][k]))
   if not initial:
    ck(cid+str(y)+':nominal_additive',z['nominal_gdp_trn']-priorN*(1+g+pi));ck(cid+str(y)+':real_growth',z['real_gdp_trn']-priorY*(1+g))
   row=dict(series=cid,family=family,year=y,origin='NEW_EXACT_HISTORICAL_REPRODUCTION',row_kind=z['row_kind'],transitions=30 if legacy else 29,
    real_GDP_trn=z['real_gdp_trn'],nominal_GDP_trn=z['nominal_gdp_trn'],implicit_N_over_Y=D,implicit_D_2026_normalized100=100*D/(a[0]['nominal_gdp_trn']/a[0]['real_gdp_trn']),
    implemented_D='unknown; no independent price index state in v6',implemented_vs_implicit_D_residual='not applicable',inflation_input_pct=z['inflation_pct'] if z['inflation_pct'] is not None else 'scheduled2_not_applied_at_initial',
    real_growth_pct=z['real_growth_pct'],nominal_growth_pct=z['nominal_growth_pct'],implicit_deflator_growth_pct=None if initial else ((1+g+pi)/(1+g)-1)*100,
    price_pressure_fraction=0.,nominal_pressure_component_trn=0.,nominal_identity_residual_trn=z['nominal_gdp_trn']-z['real_gdp_trn']*D,
    population=z['population_persons'],effective_labor='unknown; population growth + ageing drag proxy only',tax_proxy_trn=z['tax_revenue_trn'],demand_supply_components='unknown; not calculated separately in v6',
    GDP_minus_initial580_trn=z['real_gdp_trn']-580.,nominal_minus_initial600_trn=z['nominal_gdp_trn']-600.,comparison_rule='WITHIN_THIS_VARIANT_ONLY; no causal cross-family subtraction')
   annual.append(row)
   labor=z['labor_force_growth_pct']/100 if not initial else 0.;base=z['base_growth_scheduled_pct']/100 if not initial else 0.;inv=z['investment_effect_scheduled_pp']/100 if not initial else 0.;risk=z['risk_applied_pct']/100
   terms=dict(base_growth_trn=priorY*base,labor_or_aging_trn=priorY*.65*labor,risk_trn=-priorY*risk,investment_hypothesis_trn=priorY*inv)
   dy=z['real_gdp_trn']-priorY if not initial else 0.;res=dy-sum(terms.values());ck(cid+str(y)+':growth_components',res)
   decomposition.append(dict(series=cid,year=y,**terms,real_GDP_change_trn=dy,accounting_residual_trn=res,source_formula='priorY*(base+policy_invest-risk+0.65*(population_growth+aging_drag));not CIGNX',independent_real_capital_or_demand='not present'))
   planned={k:0. for k in ['oil','conflict','quake','disaster','climate']}
   for name,on,v in [('oil',y==2026,.03),('conflict',y==2027,.05),('quake',y==2031,.03),('disaster',y>=2029 and (y-2029)%3==0,.01),('climate',y>=2027 and (y-2027)%2==0,.005)]:planned[name]=v if on else 0.
   ck(cid+str(y)+':event_roster',risk-(0. if initial else sum(planned.values())))
   events.append(dict(series=cid,year=y,climate_anchor=2027,**{k+'_scheduled_fraction':v for k,v in planned.items()},real_risk_applied_fraction=risk,
    applied_event_names='' if initial else ';'.join(k for k,v in planned.items() if v),scheduled_event_names=';'.join(k for k,v in planned.items() if v),
    actual_inflation_event_pp=z['inflation_risk_applied_pp'],quake_tax_factor=z['tax_event_factor_applied'],Engel_response='unknown/not modeled',oil_energy_logistics='not modeled as separate macro cost',
    recovery='NO_EXPLICIT_REBOUND; growth shock compounds into GDP level',initial_boundary='2026_TRANSITION' if legacy else '2026_STATE;2026_OIL_NOT_CARRIED_TO2027'))
   priorY=z['real_gdp_trn'];priorN=z['nominal_gdp_trn'];priorP=z['population_persons']
  definitions.append(dict(series=cid,type='EXACT_PRIOR_VARIANT_REPRODUCTION',family=family,changes='NONE; prior full definition retained',policy_adoption=False,one_change_counterfactual=False))
  provenance.append(dict(series=cid,source_commit=PIN,source_path=OLD,case=cid,implementation='embedded prototype.py + provisional driver/simulate',
   original_text_relation='v5 hypothesis' if 'V5' in cid else 'section9 endpoint bundle; other demographic/fiscal assumptions retained, not unique text-derived scenario',
   initial_real_nominal='580/600 at2026 initial state' if not legacy else '580/600 at2025-end reference then2026 transition',initial_population=121500000,
   transitions=30 if legacy else 29,base_growth='1% to2034;.6% to2044;.3% onward' if 'V5' in cid else '1%',inflation='2% + oil2pp/conflict5pp; nominal_growth=g+pi',
   labor='0.65*(population growth+aging drag)',demography='birth/death recursion + reverse-calibrated SQ migration357k ramp',climate_start=2027,elasticity='.85/.75' if 'V5' in cid else '1.5' if 'LOW' in cid else '2.0',
   investment='0' if 'V5' in cid else '.3pp' if 'LOW' in cid else '.5pp',price_pressure='NONE',comparable_to_current_common='NO: population/labor/growth/calendar/formulas differ',canonical=False))
 # Execute exact current common path and three one-change diagnostics in
 # independent subprocesses so adapter modules never leak between variants.
 modes=['BASE_REPLAY','MULTIPLICATIVE_NOMINAL','INITIAL_OIL_EXISTING_FLAG','NO_PRICE_PRESSURE']
 for mode in modes:
  cmd=[sys.executable,str(HERE/'SQ_Common_Runtime.py'),'--root',str(root),'--outdir',str(out),'--mode',mode]
  proc=subprocess.run(cmd,cwd=root,text=True,capture_output=True);print(proc.stdout,end='');assert proc.returncode==0,proc.stderr
  traces[mode]=json.loads((out/('Common_Trace_'+mode+'.json')).read_text())
 base=traces['BASE_REPLAY'];priortrace=json.loads((root/DIAG/'SQ_Unchanged_Engine_Trace.json').read_text())
 for mode,data in traces.items():
  cid='CURRENT_COMMON_'+mode;rs=data['years'];p=data['parameters'];prev=None
  for i,t in enumerate(rs):
   y=t['year'];D=t['coreD'];implicit=t['N']/t['Y'];pi=t['inflation'];g=t['growth'];pressure=t['pressure'] if t['price_feedback'] else 0.
   ck(cid+str(y)+':nominal_formula',t['N']-t['Y']*D*(1+pressure))
   if mode=='BASE_REPLAY':
    for k in ['Y','N','coreY','coreN','coreD','labor','C','I']:ck(cid+str(y)+':fixed_trace_'+k,t[k]-priortrace['years'][i][k])
   if prev:
    ck(cid+str(y)+':risk_applied_once_to_A',t['nonlabor_factor']-prev['nonlabor_factor']*(1+p['base_growth']-t['risk']))
    factor=(1+g)*(1+pi) if mode=='MULTIPLICATIVE_NOMINAL' else 1+g+pi
    ck(cid+str(y)+':coreN_formula',t['coreN']-prev['coreN']*factor)
    ck(cid+str(y)+':level_core_formula',t['coreY']-t['coreY_anchor']*t['nonlabor_factor']*(t['labor']/t['labor_anchor'])**p['labor_response'])
   if i or p['apply_oil_to_initial']:
    prior_tax=prev['tax'] if prev else 80.;prior_nominal=prev['N'] if prev else 600.
    expected_tax=min(prior_tax*(1+(t['N']/prior_nominal-1)*p['elasticity'])*(.9 if y==2031 else 1.),t['N']*p['tax_cap_ratio'])
    ck(cid+str(y)+':tax_2031_once_and_nominal_recurrence',t['tax']-expected_tax)
   if mode=='NO_PRICE_PRESSURE':
    ck(cid+str(y)+':price_negative_control_Y',t['Y']-base['years'][i]['Y']);ck(cid+str(y)+':price_negative_control_N',t['N']-base['years'][i]['N'])
   row=dict(series=cid,family='CURRENT_COMMON_LEVEL',year=y,origin='NEW_ISOLATED_ENGINE_EXECUTION',row_kind='INITIAL_STATE' if i==0 else 'TRANSITION',transitions=29,
    real_GDP_trn=t['Y'],nominal_GDP_trn=t['N'],implicit_N_over_Y=implicit,implicit_D_2026_normalized100=implicit/(rs[0]['N']/rs[0]['Y'])*100,
    implemented_D=D,implemented_vs_implicit_D_residual=implicit-D,normalized_implemented_D100=D/rs[0]['coreD']*100,
    inflation_input_pct=pi*100,real_growth_pct=None if not prev else (t['Y']/prev['Y']-1)*100,
    nominal_growth_pct=None if not prev else (t['N']/prev['N']-1)*100,
    implicit_deflator_growth_pct=None if not prev else (implicit/(prev['N']/prev['Y'])-1)*100,
    implemented_D_growth_pct=None if not prev else (D/prev['coreD']-1)*100,
    price_pressure_fraction=pressure,nominal_pressure_component_trn=t['N']-t['Y']*D,nominal_identity_residual_trn=t['N']-t['Y']*D*(1+pressure),
    population=t['population'],effective_labor=t['labor'],tax_proxy_trn=t['tax']+t['direct'],coreY=t['coreY'],coreN=t['coreN'],
    C_state_real=t['C'],I_state_real=t['I'],supply_real=t['supply'],capacity_real=t['capacity'],unmet_real=t['unmet'],
    medical_input_deflator=t['medical_input_deflator'],medical_input_minus_live_D=t['medical_input_deflator']-D,
    GDP_minus_initial580_trn=t['Y']-580.,nominal_minus_initial600_trn=t['N']-600.,
    comparison_rule='diagnostic differences only within matched CURRENT_COMMON family; never replace benchmark')
   annual.append(row)
   before=prev['coreY'] if prev else t['coreY'];q=(t['labor']/prev['labor'])**p['labor_response'] if prev else 1.;risk=t['risk'] if prev else 0.;bg=p['base_growth'] if prev else 0.
   terms=dict(base_growth_trn=before*bg,labor_or_aging_trn=before*(q-1),risk_trn=-before*risk,growth_risk_labor_interaction_trn=before*(bg-risk)*(q-1),
    consumption_state_change_trn=t['C']-(prev['C'] if prev else t['C']),investment_state_change_trn=t['I']-(prev['I'] if prev else t['I']),
    supply_absorption_change_trn=p['capacity_absorption']*(t['supply']-(prev['supply'] if prev else t['supply'])),
    education_change_trn=(t['education_nom']/D+t['education_level']+t['finite'])-((prev['education_nom']/prev['coreD']+prev['education_level']+prev['finite']) if prev else (t['education_nom']/D+t['education_level']+t['finite'])),
    service_change_trn=t['service_nominal']/D-(prev['service_nominal']/prev['coreD'] if prev else t['service_nominal']/D),unmet_change_trn=-t['unmet']+(prev['unmet'] if prev else t['unmet']))
   dy=t['Y']-prev['Y'] if prev else 0.;reset=dy-sum(terms.values())
   # Initial-oil flag changes t0 core but leaves LEVEL anchor unshocked; expose
   # that reset explicitly, do not distribute it to labor or calibration.
   if mode!='INITIAL_OIL_EXISTING_FLAG':ck(cid+str(y)+':real_decomposition',reset)
   decomposition.append(dict(series=cid,year=y,**terms,real_GDP_change_trn=dy,initial_anchor_reset_or_unexplained_trn=reset,source_formula='LEVEL core + realized C/I/supply/medical terms; not national CIGNX',price_into_real='nominal flows divided by live coreD; precomputed medical index retained'))
   planned=dict(oil=p['oil_gdp_loss'] if y==2026 else 0.,conflict=p['conflict_gdp_loss'] if y==2027 else 0.,quake=p['quake_gdp_loss'] if y==2031 else 0.,disaster=p['disaster_gdp_loss'] if y>=p['disaster_anchor'] and (y-p['disaster_anchor'])%3==0 else 0.,climate=p['climate_gdp_loss'] if y>=p['climate_anchor'] and (y-p['climate_anchor'])%2==0 else 0.)
   applied=dict(planned)
   if y==2026 and not p['apply_oil_to_initial']:applied['oil']=0.
   ck(cid+str(y)+':event_roster',t['risk']-sum(applied.values()))
   events.append(dict(series=cid,year=y,climate_anchor=p['climate_anchor'],**{k+'_scheduled_fraction':v for k,v in planned.items()},
    real_risk_applied_fraction=sum(applied.values()),scheduled_event_names=';'.join(k for k,v in planned.items() if v),applied_event_names=';'.join(k for k,v in applied.items() if v),
    actual_inflation_event_pp=0. if y==2026 and not p['apply_oil_to_initial'] else (pi-.02)*100,
    quake_tax_factor=.9 if y==2031 else 1.,Engel_response='unknown/not modeled',oil_energy_logistics='15% output metadata regardless oil flag; no separate GDP subtraction',
    recovery='NO_EXPLICIT_REBOUND; LEVEL A_t accumulates risks; initial oil flag has separate anchor-reset issue',
    initial_boundary='INITIAL_EVENT_DIAGNOSTIC_NO_FULL_DEMOGRAPHIC_TRANSITION' if mode=='INITIAL_OIL_EXISTING_FLAG' else '2026_ANCHORED_STATE;oil not shifted to2027'))
   prev=t
  definitions.append(dict(series=cid,type='BASE_REPLAY' if mode=='BASE_REPLAY' else 'ONE_CHANGE_UNADOPTED_DIAGNOSTIC',family='CURRENT_COMMON_LEVEL',
   changes={'BASE_REPLAY':'none','MULTIPLICATIVE_NOMINAL':'only coreN recurrence (1+g+pi) -> (1+g)*(1+pi)','INITIAL_OIL_EXISTING_FLAG':'only apply_oil_to_initial=False ->True using existing engine branch; no initial-anchor fix','NO_PRICE_PRESSURE':'only spec.price_feedback=False; negative control'}[mode],
   policy_adoption=False,one_change_counterfactual=mode!='BASE_REPLAY',price_medical_satellite_reinitialization='unchanged fixed dependency indices; not a fully re-calibrated policy comparison'))
  provenance.append(dict(series=cid,source_commit=PIN,source_path=ND,case='SQ_COMMON_ON',implementation='shared foreign/elder/medical/education adapters; LEVEL run_path',original_text_relation='section9 g1/inflation2 reference plus separate demographic/labor/response assumptions',
   initial_real_nominal='580/600 in pinned baseline; altered initial branch only in explicit diagnostic',initial_population=rs[0]['population'],transitions=29,base_growth='1%',
   inflation='nominal g+pi in base; pi is hardcoded .02+shock, implicit D growth differs',labor='L_t/L_2026 ^ .65',demography='shared age/sex labor trajectory; distinct from old recursive v5',climate_start=2028,elasticity='1.5',investment='no scalar+.3/.5pp SQ effect; replacement capital is proxy',price_pressure='unmet/coreY*.5; SQ inactive as unmet0',
   comparable_to_current_common='matched diagnostic only; do not use as adopted replacement',canonical=False))
 # Actual F reference variants: show, but do not mix pure-core SQ with commonON.
 fa=rd(root/F/'Annual.csv');fsq={int(x['year']):x for x in fa if x['case']=='SQ_FIXED'}
 fcommon={int(x['year']):x for x in rd(root/F/'SQ_Common_Annual.csv') if x['case']=='SQ_COMMON_ON'}
 n3fixed={(x['case'],int(x['year'])):x for x in rd(root/ND/'results/Annual_DOMESTIC_TRANSFER.csv')}
 comparisons=rd(root/F/'Comparison.csv');fcomp={int(x['year']):x for x in comparisons if x['case']=='LATEST_F'}
 for i,t in enumerate(base['years']):
  y=t['year'];q=fsq[y];c=fcommon[y];n=n3fixed['SQ_COMMON_ON',y]
  for label,x in [('F_common_ON',c),('N3_common_ON',n)]:
   for k,v in [('real_gdp_trn',t['Y']),('nominal_gdp_trn',t['N'])]:ck('reference_'+label+str(y)+k,float(x[k])-v,2e-6)
  ck('F_original_comparison_denominator'+str(y),float(fcomp[y]['real_gdp_trn'])-float(fcomp[y]['real_gdp_trn_minus_SQ_FIXED'])-float(q['real_gdp_trn']),2e-6)
  comparison.append(dict(year=y,F_original_comparison_SQ_fixed_real=float(q['real_gdp_trn']),F_common_ON_SQ_real=float(c['real_gdp_trn']),N3_comparison_SQ_common_ON_real=float(n['real_gdp_trn']),
    original_F_denominator_field='real_gdp_trn_minus_SQ_FIXED',matched_common_ON_comparison_file=F+'/Common_ON_F_SQ_Comparison.csv',
    rule='F_Comparison.csv uses pure-core SQ_FIXED; commonON matched table and N3 use SQ_COMMON_ON; same common core, tiny common-medical demand difference; never mix denominators',
    evidence=F+'/Comparison.csv; '+F+'/SQ_Common_Annual.csv; '+ND+'/results/Annual_DOMESTIC_TRANSFER.csv'))
  annual.append(dict(series='F_FIXED_SQ_CORE_REFERENCE',family='CURRENT_COMMON_CORE_REFERENCE',year=y,origin='REUSED_FIXED_F_DENOMINATOR',
    real_GDP_trn=float(q['real_gdp_trn']),nominal_GDP_trn=float(q['nominal_gdp_trn']),implicit_N_over_Y=float(q['nominal_gdp_trn'])/float(q['real_gdp_trn']),
    implemented_D=t['coreD'],GDP_minus_initial580_trn=float(q['real_gdp_trn'])-580.,nominal_minus_initial600_trn=float(q['nominal_gdp_trn'])-600.,
    comparison_rule='pure core denominator; no automatic replacement of matched commonON SQ'))
 provenance.append(dict(series='F_FIXED_SQ_CORE_REFERENCE',source_commit=PIN,source_path=F+'/Annual.csv and Comparison.csv',case='SQ_FIXED',implementation='common core without common medical ON adjustment',
  initial_real_nominal='580/600',initial_population=base['years'][0]['population'],transitions=29,base_growth='1%',inflation='shared current additive convention',labor='same common core',climate_start=2028,elasticity='1.5',
  comparable_to_current_common='different common-module ON scope; original F comparison denominator is not silently substituted',canonical=False))
 provenance.insert(0,dict(series='POLICY_TEXT_SECTION9',source_commit=PIN,source_path='policies/StatusQuo.md',implementation='SPECIFICATION_ONLY_NOT_A_UNIQUE_EXECUTABLE_MODEL',
  initial_real_nominal='580/600',initial_population=121500000,transitions='2026-2055 boundary choices not uniquely supplied',base_growth='1%',inflation='2%; nominal3% baseline wording',labor='not sufficiently specified',climate_start='biennial anchor not specified',elasticity='1.5-2',investment='+.3-.5%/year meaning not fully specified',comparable_to_current_common='text reference; no invented unique numeric output',canonical=False))
 # Year summaries are per series; no cross-family policy-gap columns.
 for cid in dict.fromkeys(x['series'] for x in annual):
  a=[x for x in annual if x['series']==cid];end=a[-1]
  for y in [2030,2035,2039,2055]:
   x=next(x for x in a if x['year']==y);summ.append(dict(series=cid,year=y,real_GDP_trn=x['real_GDP_trn'],nominal_GDP_trn=x['nominal_GDP_trn'],implicit_N_over_Y=x['implicit_N_over_Y'],
    real_below580_years=sum(z['real_GDP_trn']<580.-1e-7 for z in a),real_change_vs2026= x['real_GDP_trn']-a[0]['real_GDP_trn'],nominal_change_vs2026=x['nominal_GDP_trn']-a[0]['nominal_GDP_trn'],
    real_cumulative_change_pct=(x['real_GDP_trn']/a[0]['real_GDP_trn']-1)*100,nominal_cumulative_change_pct=(x['nominal_GDP_trn']/a[0]['nominal_GDP_trn']-1)*100,
    no_cross_family_causal_subtraction=True))
 cf=[]
 for mode in modes:
  for i,t in enumerate(traces[mode]['years']):
   b=base['years'][i];cf.append(dict(case=mode,year=t['year'],real_GDP=t['Y'],nominal_GDP=t['N'],core_real_GDP=t['coreY'],core_nominal_GDP=t['coreN'],implemented_D=t['coreD'],
    delta_vs_own_common_base_real=t['Y']-b['Y'],delta_vs_own_common_base_nominal=t['N']-b['N'],delta_vs_own_common_base_core_real=t['coreY']-b['coreY'],
    medical_input_D=t['medical_input_deflator'],medical_minus_live_D=t['medical_input_deflator']-t['coreD'],diagnostic_only=True,baseline_unchanged=True,
    note='only private runtime changed; no new risk strengths, recovery coefficients or shared source edits'))
 findings=[dict(item=a,classification=b,evidence=c,impact=d,next_executable=e,decision_or_data_gap=f,scope=g,formal_finding_close=False) for a,b,c,d,e,f,g in [
 ('SQ family separation','BASELINE_VARIANT','old v5 1/.6/.3 growth and pop+aging, climate2027 vs current LEVEL1% actuallabor climate2028','2055 endpoints differ; not a policy causal gap','retain explicit family/commit/denominator identifiers','which baseline contract to adopt remains future decision','F/N3/SQ'),
 ('Nominal-real divergence','STRUCTURAL_CHOICE','coreN growth=g+pi; D=coreN/coreY; Dgrowth=pi/(1+g)','real decline and nominal increase are arithmetically compatible; no evidence of double deflation in base','expose input inflation vs implicit deflator and pressure separately','is pi CPI or GDP-price growth; additive vs multiplicative convention','COMMON_MACRO'),
 ('Repeated risk persistence','STRUCTURAL_CHOICE;CALIBRATION_GAP','A_t*=1+base_growth-risk; no explicit rebound','repeated shocks leave lasting GDP level effects; labor falls separately','retain prior exact decomposition; estimate shock duration/recovery before future changes','no recovery coefficient or strength recalibration adopted','COMMON_MACRO'),
 ('Calendar differences','BASELINE_VARIANT;POLICY_SPEC_GAP','old climate starts2027; current profile forces2028; text says biennial without phase','old2027/2031 overlap climate; current2027/2031 do not','keep event-by-year roster with policy/profile provenance','choose calendar only in future SQ final review','F/N3/SQ'),
 ('2026 initial oil vs metadata','STRUCTURAL_CHOICE;POLICY_SPEC_GAP','base apply_oil_to_initial=False; core anchor580/600; energy metadata15 still output','oil GDP/extra inflation not applied or rolled to2027; output metadata does not prove economic shock','split scheduled/applied fields in outputs; no change to GDP series','2026 anchor vs event interpretation and any future2027 start','COMMON_MACRO'),
 ('Dormant initial-oil LEVEL anchor reset','STRUCTURAL_CHOICE;NOT_IDENTIFIABLE','existing flagTrue shocks2026 core but leaves coreY_anchor580;2027 LEVEL core resets to base','diagnostic initially lowers GDP but raises later nominal path via rebound-growth accounting; base flagFalse unaffected','specify initial boundary/anchor semantics before any fix; retain explicit reset residual','intended initial loss persistence is not specified, no confirmed bug claim','INACTIVE_BRANCH_COMMON_MACRO'),
 ('Price-pressure double application hypothesis','NOT_IDENTIFIABLE','SQ unmet=0; price_feedbackFalse reproduction identical','pressure contributes0 in base, cannot explain SQ nominal-real divergence','reuse negative-control result; inspect binding F cases only in separate work','no SQ pressure bug confirmed; F full reexecution not performed','SQ_CURRENT;F_IF_BINDING'),
 ('Conditional price propagation','CALIBRATION_GAP;STRUCTURAL_CHOICE','medical dependencies use precomputed deflators; diagnostic live coreD can differ','single nominal-formula diagnostic is not a fully reinitialized price-consistent F/N3 scenario','if convention changes later regenerate all dependent medical/VAT/population price paths and rerun all policies','no policy reranking from diagnostic endpoints','COMMON_SATELLITES'),
 ('Capital and C proxies','STRUCTURAL_CHOICE','capital_ratio*coreY, replacement investment derived; Cproxy mostly core income share','not independent observed capital shortage or full CIGNX decomposition','label stock/flow and core-linked proxies','national capital/labor/response calibration missing','COMMON_MACRO'),
 ('Hardcoded base inflation','STRUCTURAL_CHOICE','inflation=.02+event terms rather than p.base_inflation; current values equal','stored knob is inactive for this formula; no base-output inconsistency at .02','parameter-use audit before a future authorized refactor','not permission to change inflation or shared engine now','COMMON_MACRO'),
 ('Inflation shock parameter coupling','STRUCTURAL_CHOICE;POLICY_SPEC_GAP','current inflation uses conflict_gdp_loss for extra inflation; separate conflict_inflation_extra field equals.05 but not read here','no output discrepancy at equal defaults; GDP-strength changes would also change inflation if source reused','audit distinct GDP and price shock keys before future authorized refactor','separate inflation contract not adopted or changed in this diagnosis','COMMON_MACRO'),
 ('F comparison denominator scope','BASELINE_VARIANT','F Comparison.csv subtracts SQ_FIXED; common_ON matched table and N3 use SQ_COMMON_ON','same core, distinct common-care scope; small difference must stay identified','use explicit same-common-module denominator in future cross-policy comparisons','no prior outputs revised','F/N3_COMPARISON')]]
 dump(out/'SQ_Baseline_Variant_Provenance_And_Comparability.csv',provenance);dump(out/'SQ_Annual_Real_Nominal_Deflator_2026_2055.csv',annual);dump(out/'SQ_Real_GDP_Transmission_Decomposition.csv',decomposition)
 dump(out/'SQ_Risk_Event_Application_And_Overlap.csv',events);dump(out/'SQ_Limited_Diagnostic_Counterfactuals_2026_2055.csv',cf);dump(out/'SQ_Limited_Diagnostic_Case_Definitions.csv',definitions);dump(out/'SQ_Findings_And_Next_Executable_Fixes.csv',findings)
 dump(out/'SQ_Variant_Key_Years.csv',summ);dump(out/'F_N3_SQ_Denominator_Comparability_Check.csv',comparison)
 write(out/'Reused_SQ_Growth_Contribution_Summary.json',rd(root/DIAG/'SQ_Growth_Contribution_Summary.csv'))
 rec=[];paths=['policies/StatusQuo.md']+[str(p.relative_to(root)) for p in (root/OLD).iterdir() if p.is_file()]+[DIAG+'/SQ_Unchanged_Engine_Trace.json',DIAG+'/SQ_Growth_Diagnosis_Reproduce.py',DIAG+'/SQ_Growth_Diagnosis_Verification.json',DIAG+'/SQ_Growth_Contribution_Summary.csv',ND+'/Model.py',ND+'/Inputs.json',ND+'/Macro_Adapter.py',ND+'/Resolved_Macro_Source.py.txt',ND+'/results/Annual_DOMESTIC_TRANSFER.csv',F+'/Annual.csv',F+'/Comparison.csv',F+'/SQ_Common_Annual.csv',F+'/Common_ON_F_SQ_Comparison.csv','handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/Verification.json','handoff/chatgpt-n3-household-tax-path-review-20261123/Verification.json','handoff/chatgpt-n3-pension-path-review-20261123/Verification.json']
 for path in sorted(set(paths)):
  b=subprocess.check_output(['git','show',PIN+':'+path],cwd=root);assert b==(root/path).read_bytes();rec.append(dict(commit=PIN,path=path,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True,retrieval='git fetch fixed commit/git show'))
 req='handoff/chatgpt-statusquo-common-macro-limited-diagnostic-request-20261123/SPE_Work_StatusQuo_Common_Macro_Deflator_Risk_Baseline_Diagnostic_Request_20261123.md';b=subprocess.check_output(['git','show',PIN+':'+req],cwd=root);assert b==(root/req).read_bytes();rec.append(dict(commit=PIN,path=req,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True))
 draftpath='handoff/claude-n3-model-draft-20261121/SPE_N3_Medical_On_CommonSQ_Draft_DRAFT_20261121.py';b=subprocess.check_output(['git','show','3c77eafc2073fdaba4c129164817d2f57c9421b9:'+draftpath],cwd=root);rec.append(dict(commit='3c77eafc2073fdaba4c129164817d2f57c9421b9',path=draftpath,size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),match=True,retrieval='fixed git object extracted temporarily for unchanged adapter checks'))
 write(out/'Input_Source_Receipts.json',rec)
 assert not subprocess.check_output(['git','diff','--name-only',PIN],cwd=root,text=True).strip()
 failures=[x for x in checks if not x['pass_']];v=dict(status='PASS_LIMITED_COMMON_MACRO_DIAGNOSTICS' if not failures else 'FAIL',executed_paths=8,executed_annual_rows=240,reused_F_fixed_reference_rows=30,delivered_annual_rows=len(annual),limited_new_counterfactuals=3,checks=len(checks),failed=len(failures),failures=failures,
 source_files_checked=len(rec),prior_PASS_reused=[436,13928,8058,15590],SQ_originals_or_common_engine_changed=False,risk_strengths_or_recovery_recalibrated=False,policy_adopted=False,canonical_baseline_selected=False,
 primary_current_SQ2055_real=base['years'][-1]['Y'],primary_current_SQ2055_nominal=base['years'][-1]['N'],full_F_N3_recalculation=False)
 write(out/'Verification.json',v);report(out,v,summ,cf,findings,base,oldruns)
 print(json.dumps(v));assert not failures,failures[:4]

def report(out,v,summ,cf,findings,base,oldruns):
 lines=['# StatusQUO・共通マクロ構造の限定先行診断','DRAFT / NON-CANONICAL / 2026-11-23',
 '## 結論と対象範囲',
 '名目GDP上昇と実質GDP低下の併存は、この実装の物価/名目式と、労働減少・反復リスクの実質水準効果で算術的に説明できる。乖離自体をバグとは判定しない。旧11/15 v5候補と現行比較SQは、基調成長・人口/労働・気候暦等が異なる別系統。いずれも本件でCanonicalに指定せず、政策差へ混合しない。',
 f"旧4系統と現行基準＋3診断を計8経路240年次実行。固定F比較用SQ30年次を再利用。新規チェック{v['checks']}件・失敗{v['failed']}。旧436件のSQ成長診断とN3税/年金精査のPASSを再利用し、税/年金調査や旧リスク全除去感度を再実施していない。",
 '## 系統と基準比較',
 '旧v5は実質基調1→0.6→0.3%、税弾性0.85→0.75、歳出3%、人口増減+aging_dragを労働代理とし、気候を2027起点とする。原文§9端点は旧人口等を維持した別束で、本文から一意に定まる全仕様ではない。現行は基調1%、実就業proxyのLEVEL接続・弾性1.5・気候2028起点。現行初期人口122.618024百万人と旧/本文121.5百万人も異なる。',
 '|系列|年|実質GDP|名目GDP|名目/実質比|580未満年数|','|---|---:|---:|---:|---:|---:|']
 for z in summ:
  if z['year']==2055:lines.append(f"|{z['series']}|2055|{z['real_GDP_trn']:.6f}|{z['nominal_GDP_trn']:.6f}|{z['implicit_N_over_Y']:.6f}|{z['real_below580_years']}|")
 lines+=['水準の横並びは系統の識別であり、異系統を同一母集団の政策差として差し引いていない。各年2030/2035/2039/2055はKey_Years、全年はAnnualに格納。旧v5/原文端点/30遷移は別case。',
 'F元Comparison.csvはSQ_FIXED（2055年528.962458兆円）を控除。F common_ON比較表とN3比較はSQ_COMMON_ON（528.962336兆円）で、コアは同じでも共通医療ONの微小需要差がある。F−SQ_FIXEDとN3−SQ_COMMON_ONを無表示で混ぜない。既存F/N3出力は更新していない。',
 '## 名目・実質・価格指数',
 '現行の実質コアは`Ycore=580*A_t*(L_t/L_2026)^0.65`、`A_t=A_(t-1)*(1+0.01-risk_t)`。名目コアは`Ncore_t=Ncore_(t-1)*(1+g_t+pi_t)`、価格状態は`d=Ncore/Ycore`。実GDPはコアにC状態・I状態・供給吸収・医療等を接続し、最終名目は`N=Y*d*(1+price_pressure)`。このC/Iは差分proxyであり国民経済計算の完全CIGNXではない。',
 '入力インフレpiとGDP暗黙指数の成長率は別。加算名目式では`d_t/d_(t-1)=1+pi/(1+g)`となるため、g<0の年は指数上昇率がpiより大きい。CPIかGDP物価かの仕様は未確定で、単に二重物価と断定しない。最終暗黙比N/Yはさらにpressureを含み得る。現行SQのunmet/pressureは全年0で、名目/実質比と実装dは一致する。NO_PRICE_PRESSURE枝も全年同一となり、ここでの追加圧力二重適用仮説は支持されない。',
 '現行SQは2026実質580/名目600、2055実質528.962336/名目1023.329981。dは600/580=1.034483から1.934599へ。指数規格化100と生のN/Y比を別列にした。名目が増えた事実を実質的成長や財政需要の増加と取り違えない。',
 '## 実質縮小とリスク',
 '既存固定診断で2026→2055の−51.037664兆円は、基調成長+156.303873、有効労働−75.267623、紛争−29.000000、地震−16.659235、反復災害−48.518693、気候−37.678653、成長/リスク×労働の相互作用−0.217210、微小なC/医療等の差で再構成済み。これらはモデルの算術配分で実証因果推定ではない。今回の年次再実行でも式を照合した。',
 'リスクは翌年自動回復する一時的GDP差ではなく、乗算状態Aに水準損失が残る。原文は回復係数を確定しておらず、今回は任意の回復率/確率/デバフ弱体化を投入していない。人口・就業要因は労働の変化として別に入る。現在SQの供給上限は非拘束で、追加資本/Iはほぼ0、基礎資本はGDP比から作るproxy。資本不足を独立の実測原因と推測しない。',
 '2026初期行は経済遷移を行わず、予定オイルGDP−3%/追加インフレ+2ppを適用しない。2027へも繰り越さない。原文の物流15%は出力メタデータに残るが別GDP控除はなく、エンゲル+5ppの年次モデル系列もない。旧30遷移は2025末状態から2026に人口を含めて1回遷移する別境界。',
 '旧v5は気候2027起点なので2027紛争+気候5.5%、2031地震+気候3.5%。現行は2028起点なので2027/2031の気候はない。現行で災害と気候が重なる年は両方加算されるが、異種事象の同年加算だけでバグとしない。2031税収0.9倍は税の再帰式に一度適用し、同額をGDPから二度控除していない。',
 '## 最小限の隔離反実仮想',
 '|診断（現行系統内）|2055実GDP差|2055名目GDP差|','|---|---:|---:|']
 for name in ['MULTIPLICATIVE_NOMINAL','INITIAL_OIL_EXISTING_FLAG','NO_PRICE_PRESSURE']:
  z=next(x for x in cf if x['case']==name and x['year']==2055);lines.append(f"|{name}|{z['delta_vs_own_common_base_real']:+.9f}|{z['delta_vs_own_common_base_nominal']:+.9f}|")
 lines+=['MULTIPLICATIVEは名目コア式の加算を積へ1箇所変更しただけで、リスク強度・労働・実質コアを変えていない。各衛星の事前計算物価は固定依存のままなので、名目フロー実質化による微小なGDP差が残る。価格規約を正式変更する場合は全依存物価・F/N3/SQを再生成して同時比較する必要がある。本診断だけで政策順位を付けない。',
 'INITIAL_OILは既存apply_oil_to_initial=Trueの枝だけを有効化した診断。2026コア実質562.6・名目594へ変わる一方、LEVELのcoreY_anchorは580のままなので2027コアは基準へ戻る。これにより翌年成長率に機械的反騰が入って後年名目を押し上げる。原文の損失持続/回復・初期境界の期待値が未確定なので、現行base(False)のバグとは認定せず、休止枝の境界不整合候補として残す。勝手なアンカー修正はしていない。',
 '## 分類と次に必要な実務',
 '名目式の基調インフレは入力base_inflationではなく.02を直書きし、紛争の追加インフレにもconflict_gdp_lossを参照する。別のconflict_inflation_extraも現行値.05で一致するが、この式では使われていない。値が等しい現行出力に差はなく、将来ノブを調整する前の入力契約論点として記録した。',
 '現行基準で確定バグと断定する証拠は得られなかった。STRUCTURAL_CHOICE：加算名目式、回復なしリスク、proxy資本/消費、固定衛星価格。BASELINE_VARIANT：旧v5と現行、気候起点、人口基盤、FのSQ_FIXED対common_ON。CALIBRATION_GAP：実質潜在成長/労働反応/災害持続/物価/医療。POLICY_SPEC_GAP：原文の初期事象扱い・イベント位相・指数概念・将来開始年。NOT_IDENTIFIABLE：任意回復や全国再較正後のF/N3順位など。',
 'AIが継続できる技術実務：系列識別・scheduled/applied列・入力pi/実装d/最終暗黙比/pressureの表示分離、依存物価の参照先/初期境界テスト、不活性のbase_inflation入力（式は.02直書き）の追跡。正式な修正実装は別権限。Owner選択が残る点：SQの採用計算契約、災害の持続/回復/暦、価格規約と2026境界/将来2027開始。今回は新判断を要求せず候補だけ記録した。',
 f"検証{v['checks']}件・失敗{v['failed']}。原本{v['source_files_checked']}件を固定Commitの実バイトSHA-256/サイズで照合。既存原本・政策本文・SQデバフ・共通エンジン・mainの変更なし。",
 '再現：`python3 handoff/chatgpt-statusquo-common-macro-limited-diagnostic-20261123/SQ_Limited_Diagnostic_Reproduce.py --outdir /tmp/sq-common-replay`。標準Python/Git、指定固定履歴が必要。正式Acceptance・PR/merge・Finding Close・DecisionLog・Freeze・Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。']
 (out/'SPE_StatusQuo_Common_Macro_Limited_Diagnostic_Report_DRAFT_20261123.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.outdir.resolve())
