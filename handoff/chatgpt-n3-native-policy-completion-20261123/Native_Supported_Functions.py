"""Nonmonetary text rules. None means unknown, never false or zero saving."""
import math

def phase(year):
    return 'PHASE1' if year <= 2032 else 'PHASE2' if year <= 2038 else 'PHASE3'

def kpi_review(year, income_growth=None, income_target=None, gini=None, gini_reference=None,
               relief_increment=None, relief_end=None, fund_return=None, return_floor=None):
    if year != 2035:
        return dict(review_status='NOT_REVIEW_YEAR',freeze_required=None,relief_required=None,
                    relief_executable=False,competition_required=None)
    freeze=None if income_growth is None or income_target is None else income_growth<income_target
    relief=None if gini is None or gini_reference is None else gini>gini_reference
    competition=None if fund_return is None or return_floor is None else fund_return<return_floor
    return dict(review_status='EVALUATED_WITH_UNKNOWNS',freeze_required=freeze,relief_required=relief,
                relief_executable=relief is True and relief_increment is not None and relief_end is not None,
                competition_required=competition)

def coop_partition(blocks, prefectures, mapping):
    """Validate an externally supplied complete partition; never invent geography."""
    if blocks is None or prefectures is None or mapping is None:
        return dict(status='MISSING_DATA',valid=None,efficiency_saving_trn=None)
    valid=(isinstance(blocks,int) and not isinstance(blocks,bool) and 10<=blocks<=15 and
           len(prefectures)==len(set(prefectures)) and len(prefectures)>0 and
           set(mapping)==set(prefectures) and len(set(mapping.values()))==blocks and
           all(v is not None for v in mapping.values()))
    return dict(status='VALID_EXTERNAL_PARTITION' if valid else 'INVALID_EXTERNAL_PARTITION',valid=valid,
                efficiency_saving_trn=None)

def smart_frontiers(regions):
    """Only dominance in original density/productivity; no invented weighted score/budget."""
    pending={r['id']:r for r in regions};result=[];tier=0
    if len(pending)!=len(regions):raise ValueError('duplicate region id')
    for r in regions:
        if any(not isinstance(r.get(k),(float,int)) or not math.isfinite(r[k]) or r[k]<0 for k in ['density','productivity']):
            raise ValueError('density/productivity missing or invalid')
    while pending:
        tier+=1
        ids=[i for i,a in pending.items() if not any(b['density']>=a['density'] and b['productivity']>=a['productivity'] and
            (b['density']>a['density'] or b['productivity']>a['productivity']) for j,b in pending.items() if j!=i)]
        for i in sorted(ids):result.append(dict(region=i,dominance_tier=tier,total_order='unknown',public_I_trn=None));del pending[i]
    return result

def invoice_transition(simplified,small_business_relief_preserved):
    if simplified is None or small_business_relief_preserved is None:return dict(valid=None,status='MISSING_REFORM_SPECIFICATION',saving_trn=None)
    ok=bool(simplified and small_business_relief_preserved)
    return dict(valid=ok,status='TEXT_CONSTRAINTS_SATISFIED' if ok else 'TEXT_CONSTRAINT_VIOLATION',saving_trn=None)

def foreign_eligibility(n_level,regional_assignment,gdp_ratio,ratio_definition):
    # JLPT N1 is above N4; N5 fails. GDP denominator/definition must be external.
    language=None if n_level is None else n_level in [1,2,3,4]
    region=None if regional_assignment is None else bool(regional_assignment)
    cap=None if gdp_ratio is None or ratio_definition is None else 0<=gdp_ratio<=.05
    decisions=[language,region,cap]
    accepted=False if False in decisions else None if None in decisions else True
    return dict(N4_pass=language,region_pass=region,GDP_cap_pass=cap,eligible=accepted,new_admissions=None)
