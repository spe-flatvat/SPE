#!/usr/bin/env python3
"""Checks for the N3 medical/VAT draft run (DRAFT). Read-only.
usage: python3 -I THIS.py <tree_root_of_ff621006> <outdir_of_N3_run>"""
import sys,csv,json,math
from pathlib import Path
tree=Path(sys.argv[1]);out=Path(sys.argv[2])
F=tree/'handoff/f-common-endoflife-finalization-20261121'
rd=lambda p:list(csv.DictReader(open(p)))
A=rd(out/'N3_Medical_Annual.csv');C=rd(out/'N3_Medical_Common.csv');ref=rd(F/'SQ_Common_Annual.csv')
by={(r['case'],int(r['year'])):r for r in A};rf={(r['case'],int(r['year'])):r for r in ref}
res=[]
def rec(name,ok,detail):res.append((name,ok,detail));print(('PASS ' if ok else 'FAIL ')+name+' | '+str(detail))
# 1 regression vs fixed CommonBaseline outputs
mx=0.
for y in range(2026,2056):
    for mine,theirs in [('SQ_COMMON_OFF','SQ_COMMON_OFF_REPLAY'),('SQ_COMMON_ON','SQ_COMMON_ON')]:
        for k in ['real_gdp_trn','nominal_gdp_trn','tax_diagnostic_trn','household_consumption_nominal_proxy_trn','I_policy_real_trn','capital_total_real_trn']:
            mx=max(mx,abs(float(by[mine,y][k])-float(rf[theirs,y][k])))
rec('regression: SQ common OFF/ON equal fixed SQ_Common_Annual (6 metrics x 30y x 2)',mx==0.,'max abs diff=%g'%mx)
# 2 claim identity patient+public+insurer=clinical
mx=max(abs(float(r['patient_payment_delta_trn'])+float(r['public_clinical_payment_delta_trn'])+float(r['insurer_clinical_payment_delta_trn'])-float(r['clinical_cost_delta_trn'])) for r in A)
rec('claim identity patient+public+insurer=clinical cost',mx<1e-9,'max abs=%g rows=%d'%(mx,len(A)))
# 3 protection invariants of the common module
bad=[(r['case'],r['year']) for r in C if any(float(r[k])!=0 for k in ['registration_changes_benefits','registration_changes_copay','registration_changes_palliative_priority','treatment_automatically_stopped','unknown_wish_assumed_refusal','active_life_termination'])]
rec('protection invariants zero in every case-year',not bad,'rows=%d violations=%d'%(len(C),len(bad)))
# 4 common module set-independence: patient-side differences only across N3 medical rules (transitions/unmet identical when common ON)
ons=[c for c in dict.fromkeys(r['case'] for r in C) if not c.endswith('COMMON_OFF') and c!='SQ_COMMON_OFF']
cb={(r['case'],int(r['year'])):r for r in C};mx=0.
for y in range(2026,2056):
    for c in ons:
        for k in ['transition_need','chosen_transitions','transition_unmet','universal_palliative_served','resource_units_used','transition_capacity']:
            mx=max(mx,abs(float(cb[c,y][k])-float(cb['SQ_COMMON_ON',y][k])))
rec('common module physical quantities do not depend on N3 coinsurance/VAT/case (same SQ population)',mx<1e-6,'max abs diff across %d common-ON cases=%g'%(len(ons),mx))
# 5 COMMON_OFF cases have zero transitions
z=max(abs(float(cb[c,y]['chosen_transitions'])) for c in ['SQ_COMMON_OFF','N3_MED_50_COMMON_OFF'] for y in range(2026,2056))
rec('common OFF => no transitions',z==0.,'max=%g'%z)
# 6 pre-start years: N3 medical rule has no effect before its start year
pre=max(abs(float(by['N3_MED_50_CAP_SAME',y][k])-float(by['SQ_COMMON_ON',y][k])) for y in range(2026,2033) for k in ['patient_payment_delta_trn','household_cash_delta_trn','real_gdp_trn'])
rec('N3 medical rule inactive before 2033 start (equals SQ common ON; patient, household cash, real GDP)',pre<1e-9,'max abs diff 2026-2032=%g'%pre)
# 7 VAT experiment: before 2030 equals SQ; VAT path monotone non-decreasing std rate; freeze holds 15% from 2035
sq=max(abs(float(by['N3_VAT_PATH_ONLY',y]['real_gdp_trn'])-float(by['SQ_COMMON_ON',y]['real_gdp_trn'])) for y in range(2026,2030))
rec('VAT experiment: identical to SQ through 2029',sq<1e-9,'max abs real GDP diff=%g'%sq)
rates=[float(by['N3_VAT_PATH_ONLY',y]['standard_rate']) for y in range(2026,2056)]
rec('VAT path standard rate non-decreasing and reaches 0.20 in 2040',all(b>=a for a,b in zip(rates,rates[1:])) and rates[2040-2026]==.2,'2031=%s 2032=%s 2034=%s 2038=%s 2040=%s'%tuple(rates[y-2026] for y in (2031,2032,2034,2038,2040)))
fr=[float(by['N3_VAT_FREEZE2035_ONLY',y]['standard_rate']) for y in range(2035,2056)]
rec('VAT freeze case holds 0.15 from 2035',set(fr)=={.15},sorted(set(fr)))
# 8 VAT revenue sanity: modeled VAT rises with standard rate (statement of direction, not validation)
ok=all(float(by['N3_VAT_PATH_ONLY',y]['modeled_VAT_trn'])>=float(by['SQ_COMMON_ON',y]['modeled_VAT_trn'])-1e-9 for y in range(2026,2056))
rec('VAT experiment: modeled VAT >= SQ in every year (direction only)',ok,'')
print('SUMMARY',sum(1 for r in res if r[1]),'/',len(res),'PASS')
sys.exit(0 if all(r[1] for r in res) else 1)
