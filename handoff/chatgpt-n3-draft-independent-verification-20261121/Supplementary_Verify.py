"""Additional interpretation and presentation checks, without modifying target.
usage: python Supplementary_Verify.py SOURCE_ROOT ENGINE_ROOT OUTPUT_DIR
"""
import sys,csv,json,hashlib,subprocess,math
from pathlib import Path
sys.dont_write_bytecode=True
SRC,ENGINE,P=map(lambda z:Path(z).resolve(),sys.argv[1:4]);sys.path.insert(0,str(P))
# Load only independent formula declarations, without rerunning the verification.
code=(P/'Independent_Verify.py').read_text();start=code.index('def coins0(');end=code.index('# Compare independent elementary claims')
ns=dict(math=math);exec(compile(code[start:end],'independent_claim_formulas','exec'),ns)
claim=ns['claim'];coins0=ns['coins0'];effective=ns['effective'];annual=ns['annual']
read=lambda p:list(csv.DictReader(Path(p).open()));A=read(P/'Replay_N3_Medical_Annual.csv');by={(r['case'],int(r['year'])):r for r in A}
# Distinguish interpolation of post-cap payments from interpolation of rate itself.
phase=[]
for y in range(2033,2039):
 ph=(y-2033+1)/6
 for age in ['PRESCHOOL','AGE6_69','AGE70_74','AGE75PLUS']:
  for g in ['TAXFREE','GENERAL','MIDDLE','HIGH']:
   for bill in [50000,100000,150000,200000,400000,1200000]:
    s=dict(copay=True,start_year=2033,ramp_years=6,cap_mode='PATIENT_CAP_DOWN',cap_change=0.)
    actual=effective(y,age,g,bill,1,s,.5,'ALL_AGES');rate=coins0(age,g)+(.5-coins0(age,g))*ph;other=annual(y,age,g,bill,1,rate,1)
    phase.append(dict(year=y,age=age,income=g,bill_yen=bill,phase=ph,interpolated_rate_candidate=rate,draft_payment_interpolation_yen=actual,alternative_rate_interpolation_yen=other,difference_yen=actual-other,status='INTERPRETATION_DIAGNOSTIC_NOT_ADOPTED_POLICY'))
keys=list(phase[0])
with (P/'Phase_Interpretation_Audit.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader();w.writerows(phase)
# Actual independently executed logs versus exact corresponding source sections.
D=SRC/'handoff/claude-n3-model-draft-20261121';log=(D/'SPE_N3_Draft_Output_DRAFT_20261121.txt').read_text();run=(P/'Replay_Run.txt').read_text();checks=(P/'Claude_Checks_Reexecuted.txt').read_text();selftest=(P/'Replay_Selftest.json').read_text()
run_expected=log.split('# --- run (progress) ---\n')[1].split('# --- selftest json ---')[0];check_expected=log.split('# --- checks ---\n')[1];self_expected=log.split('# --- selftest json ---\n')[1].split('# --- checks ---')[0]
logs=dict(full_log_byte_equal=False,reason='original log contains author headers and placeholder commands;outputs compared by exact sections',run_section_equal=run==run_expected,checks_section_equal=checks==check_expected,selftest_section_equal=selftest==self_expected)
assert all(logs[k] for k in ['run_section_equal','checks_section_equal','selftest_section_equal'])
(P/'Replay_Log_Comparison.json').write_text(json.dumps(logs,indent=2)+'\n')
# Fixed SQ regression and preactivation across all available core indicators.
ref=read(ENGINE/'handoff/f-common-endoflife-finalization-20261121/SQ_Common_Annual.csv');rf={(r['case'],int(r['year'])):r for r in ref};mx=0.;cells=0
for mine,theirs in [('SQ_COMMON_OFF','SQ_COMMON_OFF_REPLAY'),('SQ_COMMON_ON','SQ_COMMON_ON')]:
 for y in range(2026,2056):
  for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn']:
   d=abs(float(by[mine,y][k])-float(rf[theirs,y][k]));mx=max(mx,d);cells+=1
assert mx==0
# Policy and already-reviewed basis are provenance, not a new independent PASS.
refs=[]
repo=str(SRC)
for commit,path in [('5804388482864af08204ba0d0e76a46206dacdbd','policies/New3linesPolicies.md'),('3c77eafc2073fdaba4c129164817d2f57c9421b9','specifications/SimulationSpecification_v5.md'),('8437d285b179e30a9a93236cafe56daa4b571791','handoff/n3-draft-independent-verification-20261121/SPE_Work_N3_Draft_Independent_Verification_Instruction_20261121.md'),('4924c8e4be45e1f0b66013ef4aa87d139ff7c7b5','handoff/claude-common-endoflife-f-final-verification-20261121/SPE_CommonEndOfLife_F_Final_Claude_Independent_Verification_DRAFT_20261121.md')]:
 b=subprocess.check_output(['git','-C',repo,'show',commit+':'+path]);refs.append(dict(commit=commit,path=path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),route='fixed Git object'))
 if path.endswith('New3linesPolicies.md'):assert b==(SRC/path).read_bytes()
engine_commit=subprocess.check_output(['git','-C',str(ENGINE),'rev-parse','HEAD'],text=True).strip();assert engine_commit=='ff6210061615105de9a0d64767c256796be80ed2'
for p in [SRC,ENGINE]:assert subprocess.check_output(['git','-C',str(p),'status','--porcelain'],text=True)==''
result=dict(status='PASS',SQ_regression_cells=cells,SQ_max_difference=mx,log_comparison=logs,phase_interpretation_examples=len(phase),phase_interpretation_differing_examples=sum(abs(r['difference_yen'])>1e-7 for r in phase),phase_max_difference_yen=max(abs(r['difference_yen']) for r in phase),engine_commit=engine_commit,immutable_worktrees_unchanged=True,references=refs,policy_unchanged=True,v5_path_note='requested claude/ path absent;equivalent named specification found at specifications/SimulationSpecification_v5.md;not a target for output fitting')
(P/'Supplementary_Result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
