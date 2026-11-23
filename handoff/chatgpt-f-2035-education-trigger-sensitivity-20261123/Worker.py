"""Isolated, non-adopted 2036 education sensitivity over pinned F worker."""
import importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
root,out,scenario_file=map(lambda p:Path(p).resolve(),sys.argv[1:4])
scenario=json.loads(scenario_file.read_text());out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('prior_worker',root/'Prior_Worker.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
original_mod=A.mod
def adapted_mod(name,path):
 m=original_mod(name,path)
 if name=='isolated_F_model':
  original_load=m.load
  def load(c):
   result=original_load(c);edu=result[1];Base=edu.Education
   class TimedEducation(Base):
    def step(self,y,previous,workers):
     base=dict(self.s)
     active=scenario['fired'] and y>=scenario['effective_year']
     factor=scenario['multiplier'] if active else 1.
     # The shared annual envelope also funds scholarships: scale only E shares.
     # Training scales the statutory credit parameter, not realized credit twice.
     self.s.update(facility_share=base['facility_share']*factor,service_share=base['service_share']*factor,credit_rate=base['credit_rate']*factor,trigger_mode='OFF')
     try:r=super().step(y,previous,workers)
     finally:self.s=base
     r.update(applied_E_multiplier=factor,applied_training_credit_parameter_multiplier=factor,applied_S_multiplier=1.,training_credit_parameter=base['credit_rate']*factor,baseline_trigger_growth=scenario['baseline_growth'],diagnostic_threshold=scenario['threshold'],diagnostic_decision_fired=scenario['fired'],diagnostic_active=active,diagnostic_effective_year=scenario['effective_year'],diagnostic_continuation='EVERY_YEAR_2036_2055',policy_adopted=False)
     return r
   edu.Education=TimedEducation
   return result
  m.load=load
 return m
A.mod=adapted_mod
ci=json.loads((root/'handoff/chatgpt-f-policy-cohort-fte-20261123/ANNUAL_FINE_WEEK_HOURS/Connection_Inputs.json').read_text())
A.f(root,out,ci['common_offset'],ci['elder_delta'],7)
