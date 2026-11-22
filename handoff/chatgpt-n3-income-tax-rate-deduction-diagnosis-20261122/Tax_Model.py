"""Conditional personal income-tax arithmetic, 2026 annual national rules.
A/B/C/D are hypothetical comparisons, not a national microsimulation.
"""
from pathlib import Path
import json,math
RULES=json.loads((Path(__file__).parent/'Tax_Rules_2026.json').read_text())
BOUNDARIES=list(RULES['deduction_boundaries'])
def salary_income(gross):
 x=max(0.,gross)
 if x<741000:return 0.
 if x<2191000:return x-740000
 if x<2193000:return 1451000.
 if x<2196000:return 1453000.
 if x<2200000:return 1456000.
 b=math.floor(x/4000)*4000
 if x<3600000:return b*.7-80000
 if x<6600000:return b*.8-440000
 if x<8500000:return x*.9-1100000
 return x-1950000

def basic(total):
 for limit,value in RULES['basic_deduction_by_total_income']:
  if limit is None or total<=limit:return value

def spouse(total,eligible):
 if not eligible:return 0.
 return 380000. if total<=9000000 else 260000. if total<=9500000 else 130000. if total<=10000000 else 0.

def progressive(taxable):
 t=max(0.,taxable)
 for limit,rate,offset in RULES['progressive_brackets_yen']:
  if limit is None or t<limit:return max(0.,t*rate-offset),rate if t else 0.

def profile(name):
 p=dict(id=name,kind='SALARY',splits=[1.],social_rate=.15,spouse0=False,child_age=None,blue=0.,credit=0.)
 if 'SI0' in name:p['social_rate']=0.
 if 'SPOUSE' in name:p['spouse0']=True
 if 'COLLEGE' in name:p['child_age']=20
 if 'CHILD10' in name:p['child_age']=10
 if 'CHILD17' in name:p['child_age']=17
 if 'DUAL_EQUAL' in name:p['splits']=[.5,.5]
 if 'DUAL_70_30' in name:p['splits']=[.7,.3]
 if 'BUSINESS' in name:p['kind']='BUSINESS'
 if 'BLUE65' in name:p['blue']=650000.
 if 'CREDIT100K' in name:p['credit']=100000.
 return p

def person(income,p,case,boundary,earner=0):
 keep_personal=case in ['A','B'];keep_earned=keep_personal or not boundary.startswith('INCLUDING_EARNED');keep_credit=keep_personal or boundary.endswith('KEEP_CREDITS');flat=case in ['B','D']
 x=max(0.,income);child=p['child_age'];has_child=child is not None and child<23
 if p['kind']=='SALARY':
  current_income=salary_income(x);adjust=math.ceil(max(0.,min(x,10000000)-8500000)*.1) if has_child else 0.;current_income=max(0.,current_income-adjust);earned_ded=x-current_income
 else:earned_ded=min(x,p['blue']);current_income=x-earned_ded;adjust=0.
 inc=current_income if keep_earned else x
 # Eligibility is evaluated on the corresponding current income. Non-labor income supplied zero.
 social=x*p['social_rate'];bd=basic(current_income) if keep_personal else 0.;sd=spouse(current_income,p['spouse0'] and earner==0) if keep_personal else 0.
 fd=(630000. if child is not None and 19<=child<=22 else 380000. if child is not None and 16<=child else 0.) if keep_personal and earner==0 else 0.
 deductions=bd+sd+fd+(social if keep_personal else 0.)
 taxable=math.floor(max(0.,inc-deductions)/1000+1e-10)*1000
 raw,rate=(taxable*.30,.30 if taxable else 0.) if flat else progressive(taxable)
 credit=min(raw,p['credit'] if keep_credit and earner==0 else 0.)
 ordinary=max(0.,raw-credit);surtax=math.floor(ordinary*.021+1e-8);total=ordinary+surtax
 return dict(input_yen=x,current_income_after_earned_deduction_yen=current_income,earned_income_deduction_yen=earned_ded if keep_earned else 0.,income_adjustment_included_yen=adjust if keep_earned else 0.,basic_deduction_yen=bd,spouse_deduction_yen=sd,dependent_deduction_yen=fd,social_payment_yen=social,social_deduction_yen=social if keep_personal else 0.,income_before_personal_deductions_yen=inc,personal_deductions_yen=deductions,taxable_yen=taxable,ordinary_before_credit_yen=raw,tax_credit_yen=credit,ordinary_tax_yen=ordinary,surtax_yen=surtax,total_tax_yen=total,annual_floor100_tax_yen=math.floor(total/100)*100,statutory_top_rate=rate,tax_after_social_disposable_yen=x-social-total)

def household(income,p,case,boundary,marginal=False):
 people=[person(income*share,p,case,boundary,i) for i,share in enumerate(p['splits'])]
 keys=[k for k in people[0] if k!='statutory_top_rate'];r={k:sum(z[k] for z in people) for k in keys};r['statutory_top_rate']=max(z['statutory_top_rate'] for z in people);r['earners']=len(people)
 r['effective_on_case_total_income_pct']=100*r['total_tax_yen']/r['income_before_personal_deductions_yen'] if r['income_before_personal_deductions_yen']>0 else None;r['effective_on_current_total_income_pct']=100*r['total_tax_yen']/r['current_income_after_earned_deduction_yen'] if r['current_income_after_earned_deduction_yen']>0 else None
 r['effective_on_gross_pct']=100*r['total_tax_yen']/income if income>0 else None;r['effective_on_taxable_pct']=100*r['total_tax_yen']/r['taxable_yen'] if r['taxable_yen']>0 else None
 if marginal:r['marginal_gross_10k_pct']=100*(household(income+10000,p,case,boundary)['total_tax_yen']-r['total_tax_yen'])/10000
 return r

def decompose(vals):
 a,b,c,d=[vals[k] for k in 'ABCD'];rate=b-a;ded=c-a;cross=d-b-c+a;sr=.5*((b-a)+(d-c));sd=.5*((c-a)+(d-b))
 return dict(A=a,B=b,C=c,D=d,rate_B_minus_A=rate,deduction_C_minus_A=ded,interaction=cross,total_D_minus_A=d-a,symmetric_rate=sr,symmetric_deduction=sd,additive_residual=d-a-rate-ded-cross,symmetric_residual=d-a-sr-sd)
