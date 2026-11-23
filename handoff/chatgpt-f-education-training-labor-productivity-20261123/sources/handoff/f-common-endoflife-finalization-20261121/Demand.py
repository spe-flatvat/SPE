"""Age demand candidates driven by the existing yearly Japanese/foreign trajectory.
No mortality-driven saving. Sub-65 split and terminal incidence are uncalibrated.
"""
def close(a,b):assert abs(a-b)<max(1e-5,abs(b)*1e-10),(a,b)
def age_population(t,e):
 # Elder sub-age shares from existing age-sex stock ledger; rescale to the
 # integrated trajectory elderly count to avoid mixing inconsistent totals.
 es={k:sum(e[k+'_'+sex+'_population'] for sex in ['male','female']) for k in ['65_69','70_74','75plus']}
 es={k:v*t['elderly']/sum(es.values()) for k,v in es.items()}
 r={'U15':t['under15'],'A15_64':t['working_age'],**es}
 close(sum(r.values()),t['population']);return r

def calculate(y,trajectory,elder,reference,inputs,mode):
 i=y-2026;t=trajectory[i];base=age_population(trajectory[0],elder[0]);pop=age_population(t,elder[i]);q=reference[str(y)]
 # Nationality composition conditional on IPSS Japanese broad-age proportions;
 # common scale enforces integrated Japanese stock, foreign is exact residual.
 raw={'U15':q['japanese_under15'],'A15_64':q['japanese_working_age']}
 for k in ['65_69','70_74','75plus']:raw[k]=q['japanese_elderly']*pop[k]/t['elderly']
 jap={k:v*t['japanese']/sum(raw.values()) for k,v in raw.items()}
 assert all(jap[k]<=pop[k]+1e-4 for k in pop)
 foreign={k:pop[k]-jap[k] for k in pop};close(sum(foreign.values()),t['foreign'])
 rates=inputs['episode_rates'];refsum=sum(base[k]*rates[k] for k in base)
 norm=inputs['episodes_2026_anchor']/refsum
 ep={k:pop[k]*rates[k]*norm for k in pop}
 total=sum(ep.values()) if mode=='AGE' else inputs['episodes_2026_anchor']*t['population']/trajectory[0]['population']
 if mode!='AGE':ep={k:v/sum(ep.values())*total for k,v in ep.items()}
 # Repartition 2024 observed cost shares only by relative age population changes.
 def clinical_age(a):return {'PRESCHOOL':a['U15']*inputs['under15_preschool_share'],'AGE6_69':a['U15']*(1-inputs['under15_preschool_share'])+a['A15_64']+a['65_69'],'AGE70_74':a['70_74'],'AGE75PLUS':a['75plus']}
 bp,ap=clinical_age(base),clinical_age(pop)
 costs={k:v*(ap[k]/bp[k] if mode=='AGE' else t['population']/trajectory[0]['population']) for k,v in inputs['cost_weights_2024'].items()}
 rows=[dict(year=y,age=k,population=pop[k],japanese=jap[k],foreign=foreign[k],terminal_episode_rate_candidate=rates[k]*norm,terminal_episodes=ep[k],medical_demand_mode=mode,rate_status='UNCALIBRATED_CANDIDATE',nationality_method='IPSS_BROAD_SHARE_RESCALED_TO_INTEGRATED_STOCK',deaths_used_as_saving_trigger=False) for k in pop]
 return total,ep,costs,rows
