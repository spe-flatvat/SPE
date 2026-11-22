"""Isolated mechanical sensitivity adapter. No pre-existing file is written."""
import copy,importlib.util,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SFA='handoff/chatgpt-n3-sfa-cash-reconciliation-20261122'
SEP='handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def build(root,out,definition):
 os.environ['SPE_PENSION_MODE']='DOMESTIC_TRANSFER'
 m=module('sensitivity_sfa',root/SFA/'N3_SFA_Reproduce.py')
 code=(root/SEP/'Resolved_Separation_Runtime.py.txt').read_text();ns=dict(m.T.previous.__dict__);exec(compile(code,'pinned_separation_runtime','exec'),ns)
 class Runner(m.Runner):
  simulate=ns['simulate']
  def authority_cap(self,s,y,k):return 0.
  def cash_budget(self,s,y,pb,interest,sfa,assets):
   super().cash_budget(s,y,pb,interest,sfa,assets) # retain required state for financing finalizer
   return 0.
  def component(self):
   co,md=super().component();self.live_component=co;self.live_md=md
   co.cfg.update(definition.get('config',{}));md.s.update(definition.get('component_spec',{}))
   return co,md
  def channels(self,s,y,t,w,co,md,prior):
   z=super().channels(s,y,t,w,co,md,prior)
   medical=copy.deepcopy(self.current_medical or {});medical.update(case=s['case'],year=y)
   self.medical_accounts.append(medical)
   return z
 r=Runner(root,out);r.medical_accounts=[]
 # Existing component has literals for these assumptions. Parameterize only an
 # in-memory method of the isolated module; defaults reproduce original bytes' behavior.
 raw=r.cm.old.source
 changes=[('.7*benefit',"ext.get('in_kind_substitution',.7)*benefit",3),
  ("in_kind*.3*ext.get('service_VA_ratio',.216)","in_kind*(1-ext.get('in_kind_substitution',.7))*ext.get('service_VA_ratio',.216)",1),
  ('phase(y,2030,6)',"phase(y,ext.get('employment_start',2030),ext.get('employment_ramp',6))",1),
  ('gov+=public_pension_cost*.5;ins-=public_pension_cost*.5',"gov+=public_pension_cost*ext.get('pension_public_share',.5);ins-=public_pension_cost*(1-ext.get('pension_public_share',.5))",1),
  ('government_cash_cost_delta_trn=public_pension_cost*.5,public_insurer_cash_delta_trn=-public_pension_cost*.5',"government_cash_cost_delta_trn=public_pension_cost*ext.get('pension_public_share',.5),public_insurer_cash_delta_trn=-public_pension_cost*(1-ext.get('pension_public_share',.5))",1)]
 for a,b,count in changes:
  assert raw.count(a)==count,(a,raw.count(a));raw=raw.replace(a,b)
 n=dict(r.cm.old.ns);exec(compile(raw,'isolated_parametrised_component','exec'),n);r.cm.old.Base.step=n['Components'].step
 r.resolved_component=raw
 r.medical_input['s'].update(definition.get('medical_spec',{}))
 # The companion component reads clinical allocation too: keep these medical
 # classification parameters in sync, instead of calling it an independent effect.
 for k,v in definition.get('medical_spec',{}).items():
  if k in ['clinical_public_fraction']:r.ci['s'][k]=v
 s=m.spec(definition['case'],cash_partition='SECTOR',q_central=0.,q_local=0.,GI_mode='OFF')
 s.update(definition.get('runtime',{}));assert s['GI_mode']=='OFF'
 return r,s
