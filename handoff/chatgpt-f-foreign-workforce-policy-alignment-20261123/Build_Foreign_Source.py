"""Explicit NON-ADOPTED interpretation branches of the prior quantity overlay."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
BRANCHES={
 'F_RETAINED':dict(mode='NONE',timing='SOURCE_2035',adopted=False,status='UNCHANGED_CANDIDATE; definitions unresolved'),
 'D_GDP_VA_2035':dict(mode='GDP_VA',timing='SOURCE_2035'),
 'D_GDP_VA_ANNUAL':dict(mode='GDP_VA',timing='ANNUAL_LAG'),
 'D_GDP_LABOR_2035':dict(mode='GDP_LABOR',timing='SOURCE_2035'),
 'D_GDP_PROGRAM_2035':dict(mode='GDP_PROGRAM',timing='SOURCE_2035'),
 'D_POP3_2035':dict(mode='POP_CEILING',ratio=.03,timing='SOURCE_2035'),
 'D_POP5_2035':dict(mode='POP_CEILING',ratio=.05,timing='SOURCE_2035')}
def trigger(y,previous_population,prior,timing):
 if y<2030:return False
 if timing=='SOURCE_2035':return previous_population<1e8 if y==2035 else prior
 if timing=='ANNUAL_LAG':return previous_population<1e8
 raise ValueError(timing)
def admission_cap(mode,budget,coefficient,target_rate,retained,unaffected,base_rate,japanese,ratio,screening,p,orientation,support):
 if mode in ['GDP_VA','GDP_LABOR']:
  return max(0.,(budget/coefficient-retained*target_rate-unaffected*base_rate)/target_rate)
 if mode=='GDP_PROGRAM':return max(0.,(budget-screening-retained*p*support)/max(p*(orientation+support),1e-20))
 if mode=='POP_CEILING':return max(0.,ratio*japanese/(1-ratio)-retained-unaffected)
 raise ValueError(mode)
def build(branch,nominal,deflator):
 s=BRANCHES[branch];source=(HERE/'Prior_Foreign_Overlay.py.txt').read_text()
 if branch=='F_RETAINED':return None
 def sub(a,b):
  nonlocal source
  assert source.count(a)==1,a;source=source.replace(a,b)
 sub("    s = {**c['defaults'], **spec}","    s = {**c['defaults'], **spec}\n    diagnostic="+repr(s)+"\n    fixed_nominal="+repr(nominal)+"\n    fixed_deflator="+repr(deflator))
 start=source.index('        cap = None\n');end=source.index('        cap_rejection = request - accepted',start)
 block='''        cap = None
        # NON-ADOPTED diagnostics. Lagged FTE-F GDP/deflator held fixed,
        # never labelled as the newly solved branch's GDP denominator.
        previous_population = reference[i-1]['population'] + (T-T0) if i else ref['population']
        relaxed = _alignment_trigger(y,previous_population,relaxed,diagnostic['timing'])
        factor = 1.2 if relaxed else 1.
        budget = fixed_nominal[max(0,i-1)] * .05 * factor * 1e12
        coefficient = (c['reference']['VA_yen'] if diagnostic['mode']=='GDP_VA' else c['reference']['labor_cost_yen']) * fixed_deflator[max(0,i-1)]
        screening_reference = exposed*p*s['screening_unit_yen']*fixed_deflator[max(0,i-1)] if s['selection'] else 0.
        ceiling_ratio = min(.999,diagnostic.get('ratio',.05)*factor)
        if s['policy']=='F' and p:
            cap = _alignment_cap(diagnostic['mode'],budget,coefficient,target_rate,Tret,unaffected_stock,rate,ref['japanese'],ceiling_ratio,screening_reference,p,s['orientation_unit_yen']*fixed_deflator[max(0,i-1)],s['support_unit_yen']*fixed_deflator[max(0,i-1)])
            # Restrict only new covered entrants; never expel existing stocks.
            # Unlike the legacy ramp cap, diagnostic limit binds immediately.
            accepted = min(request,cap)
        else:
            accepted = request
'''
 source=source[:start]+block+source[end:]
 sub("            conditional_target_admission_cap=cap, cap_relaxation_multiplier=factor,", "            conditional_target_admission_cap=cap, cap_relaxation_multiplier=factor,diagnostic_mode=diagnostic['mode'],diagnostic_GDP_denominator_trn=fixed_nominal[max(0,i-1)],diagnostic_deflator=fixed_deflator[max(0,i-1)],diagnostic_budget_yen=budget,diagnostic_coefficient=coefficient,diagnostic_previous_population=previous_population,diagnostic_population_ceiling=ceiling_ratio,")
 # Diagnostics deliberately use an external pinned lagged GDP denominator;
 # remove an otherwise unused internal prefix GDP solve.
 start=source.index("        if s['cap_mode'] != 'NONE' and s['policy'] == 'F' and p:")
 end=source.index('    results = macro(',start)
 source=source[:start]+source[end:]
 source="from Build_Foreign_Source import trigger as _alignment_trigger, admission_cap as _alignment_cap\n"+source
 return source
