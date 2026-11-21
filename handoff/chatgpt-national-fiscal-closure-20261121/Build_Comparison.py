#!/usr/bin/env python3
import csv,json,argparse
from pathlib import Path
from National_Fiscal import rd,n,dump,read_fiscal
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def main(out,macro):
 old=rd(ROOT/'handoff/chatgpt-n3-pension-counterpart-20261121/Gap_Annual.csv');by={(r['case'],r['year']):r for r in old};new=rd(out/'Annual79_With_Fiscal.csv');dif=[];sums=[];metriccounts={}
 for r in new:
  z=by[r['case'],r['year']];changes=0
  for k,v in z.items():
   metriccounts.setdefault(k,[0,0]);metriccounts[k][0]+=1
   if r[k]!=v:changes+=1;metriccounts[k][1]+=1;dif.append(dict(case=r['case'],year=r['year'],column=k,before=v,after=r[k]))
  sums.append(dict(case=r['case'],year=r['year'],old_columns_compared=len(z),old_columns_changed=changes,new_fiscal_columns=len(r)-len(z),new_CL_PB_candidate_trn=r['fiscal_CL_PB_candidate_trn'],new_CL_debt_candidate_trn=r['fiscal_CL_debt_end_candidate_trn'],old_national_PB_trn=z['national_PB_trn'],new_general_government_PB_trn=r['national_PB_trn'],old_national_debt_trn=z['national_debt_trn'],new_general_government_debt_trn=r['national_debt_trn'],old_macro_unchanged=True))
 dump(out/'Old_New_All79_Comparison.csv',sums)
 # Always retain a header for the intentionally empty macro differences.
 if dif:dump(out/'Old_New_Macro_Changed_Cells.csv',dif)
 else:(out/'Old_New_Macro_Changed_Cells.csv').write_text('case,year,column,before,after\n')
 dump(out/'Old_New_Column_Regression.csv',[dict(column=k,compared_rows=v[0],changed_rows=v[1],status='UNCHANGED' if v[1]==0 else 'CHANGED') for k,v in metriccounts.items()])
 A=read_fiscal(out);idx={(r['scenario'],r['case'],r['year']):r for r in A if r['mode']=='DOMESTIC_TRANSFER'};result=[]
 for r in rd(out/'Key_Years_Fiscal_Comparison.csv'):
  for k in ['real_gdp_trn','nominal_gdp_trn','model_tax_diagnostic_proxy_trn','model_expenditure_delta_trn','CL_PB_candidate_trn','CL_balance_candidate_trn','CL_net_interest_candidate_trn','CL_debt_end_candidate_trn','CL_new_cash_borrowing_candidate_trn','CL_gross_issue_with_assumed_refinancing_trn','macro_cash_DI_definition_matched_proxy_trn','clinical_cost_delta_trn','pension_benefit_delta_trn']:
   x=n(r,k);sq=n(idx[r['scenario'],'SQ_COMMON_ON',r['year']],k);f=n(idx[r['scenario'],'F_FIXED_REFERENCE',r['year']],k)
   result.append(dict(scenario=r['scenario'],case=r['case'],year=r['year'],metric=k,absolute=x,SQ_absolute=sq,F_fixed_absolute=f,minus_SQ=None if x is None or sq is None else x-sq,minus_F=None if x is None or f is None else x-f,scope='CONDITIONAL_CL_CANDIDATE_NOT_FULL_GG_NOT_CAUSAL_POLICY_RANKING',baseline_status=r['baseline_status']))
 dump(out/'Key_Year_Differences.csv',result)
 print(json.dumps(dict(old_macro_changed_cells=len(dif),compared_cells=sum(v[0] for v in metriccounts.values()),new_fiscal_columns=len(new[0])-len(old[0]),key_year_comparison_metric_rows=len(result))))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);ap.add_argument('--macro',type=Path,required=True);a=ap.parse_args();main(a.outdir,a.macro)
