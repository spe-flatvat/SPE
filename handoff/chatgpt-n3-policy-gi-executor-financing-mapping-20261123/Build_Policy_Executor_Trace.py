#!/usr/bin/env python3
"""Policy use -> existing flow -> candidate executor. No new policy amounts.
Reuses previous authority map; captured current supplemental originals are hashed.
"""
import argparse,csv,json,hashlib,urllib.request,xml.etree.ElementTree as ET,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];AUTH=ROOT/'handoff/chatgpt-n3-financing-authority-feasibility-20261123';NATIVE='handoff/chatgpt-n3-model-expansion-20261121/N3_Components.py'
def rd(p):return list(csv.DictReader(p.open()))
def dump(p,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def run(out,cache):
 policy=(ROOT/'policies/New3linesPolicies.md').read_text().splitlines();code=(ROOT/NATIVE).read_text().splitlines()
 def location(marker,lines):
  hits=[i+1 for i,s in enumerate(lines) if marker in s];assert hits,marker;return ';'.join(map(str,hits))
 items=[
 ('A_VAT','4.A','消費税の段階的20%化','TAX_CHANGE','vat=PATH; vat native tax_account; fixed KPI branch','household/VAT/remittances not added G','2030;2032;2034;2038;2040','VAT taxpayer/remitter; government revenue; final payer separate','IMPLEMENTATION_EVIDENCED'),
 ('A_VAT_SWITCH','4.A,6,7','2035年時点で経済状況','REGULATORY_INSTITUTIONAL','Components.py KPI income-growth event; active diagnostic KPI fixed','no new G; threshold and observations not supplied by original','2035 review','national tax-law decision; implementation may freeze only selected diagnostic branch','IMPLEMENTATION_EVIDENCED'),
 ('A_INVOICE','4.A','インボイス制度の大幅簡素化','REGULATORY_INSTITUTIONAL','N3_Components.institutions(invoice_saving_yen)','structure-only; no monetized administration saving','phase1 not exact year','national tax administrator/private compliance; cost owner unallocated','IMPLEMENTATION_EVIDENCED'),
 ('A_LABOR_TAX','4.A','30%ゾーン：給与・事業所得','TAX_CHANGE','N3_Components.step household loop; labour_business_flat30_tax_delta_trn','tax wedge already mapped; no second tax or G credit','phase1; modeled2030-2032','tax jurisdiction assignment unresolved, local tax redesign OPEN','IMPLEMENTATION_EVIDENCED'),
 ('A_FINANCIAL_TAX','4.A','20%ゾーン：金融所得','TAX_CHANGE','household_financial20_tax_delta_trn','financial income tax not new government purchase','phase1; modeled2030-2032','national/local revenue split unknown','IMPLEMENTATION_EVIDENCED'),
 ('A_ALLOWANCE','4.A','全控除廃止と3段階','TAX_CHANGE','flat_hh branch, gross synthetic category tax bases','not expenditure; do not call deduction removal G spending','phase1','tax administrator; exact local treatment unknown','IMPLEMENTATION_EVIDENCED'),
 ('A_CORPORATE','4.A','企業優遇インセンティブ','TAX_CHANGE_AND_PRIVATE_INVESTMENT','corporate eligibility, firms; Components funding_rows; firm_rate75 diagnostic','corporate investment is private I, not public I; response/denominator candidate','phase1; existing investment start input','private firms final investor; tax authority revenue impact','IMPLEMENTATION_EVIDENCED'),
 ('A_ESTATE_GIFT','4.A','40%ゾーン：相続・贈与税','TAX_CHANGE','Gap_Components estate_reported/gift_reported alternatives; Transition estate price link','do not add estate and overlapping gift bases; no G','phase1; modeled household ramp','revenue administrator, legal tax changes unadopted','IMPLEMENTATION_EVIDENCED'),
 ('B_PENSION','4.B','年金および医療を半官営強制加入型','CASH_TRANSFER_AND_FINANCIAL_FUND','pension75; pension_benefit_delta; fund contribution/return/payout; DOMESTIC_TRANSFER','benefit/contribution/property-income transfer not G; no second fund return GDP','2033-2038; benefit age75','fund/insurer/public pension; institutional SNA sector and sovereign shares unknown','IMPLEMENTATION_EVIDENCED'),
 ('B_MEDICAL','4.B','医療負担の適正化','INSURANCE_BENEFIT_AND_SOCIAL_TRANSFER_IN_KIND','native FMedical N3 claims/cap interpolation; govt/HH/insurer payer ledger','in-kind market purchases may enter SNA G; existing treatment already connected, no full-claim G readdition','phase2','provider final service producer; payer can government/insurer/HH; do not confuse operator and funder','IMPLEMENTATION_EVIDENCED'),
 ('B_EOL','4.B','終末医療は緩和ケア主体','SERVICE_REFORM_AND_POTENTIAL_G','common palliative/end-of-life medical satellite','shared baseline medical service/cost retained; no new budget created for card promotion','phase2; common path','medical provider/payers; national promotion/local implementation candidates not costed','IMPLEMENTATION_EVIDENCED'),
 ('B_COOP','4.B','自治体共済の広域化','REGULATORY_INSTITUTIONAL','institutions(coop_blocks=12 candidate)','10-15 block structure is not 10-15 approved government entities or fiscal sources','phase2 not exact year','wide-area mutual organization candidate; legal entity and public/private classification unknown','IMPLEMENTATION_EVIDENCED'),
 ('B_EITC','4.B','EITC廃止','TAX_TRANSFER_REMOVAL','EITC_removal_trn; eitc_per_household_yen=None','baseline unknown; modeled zero is absence of measured baseline, not proved fiscal saving','phase1','national/local tax-benefit administrator unresolved','IMPLEMENTATION_EVIDENCED'),
 ('B_RELIEF','4.B','社会保険料の所得連動減免','PREMIUM_REDUCTION','relief; premium_relief_trn; insurer negative balance/backfill interface','not direct G; payer counterpart must remain; no second HH cash credit','phase1; modeled2030 household ramp','insurer collection/payers; sovereign compensation shares unknown','IMPLEMENTATION_EVIDENCED'),
 ('B_IN_KIND','4.B','現物給付に特化','SOCIAL_TRANSFER_IN_KIND_POTENTIAL_G','in_kind_trn; gov+=in_kind; cash substitution .7; service .3*VA ratio','cash transfer distinct; government market purchase could be G but already modeled; do not add full amount again','phase1; model2030 household ramp','supplier/household service recipient; final public purchaser unidentified','IMPLEMENTATION_EVIDENCED'),
 ('C_EMPLOYMENT','4.C','公務員正規雇用枠を拡大','G_COMPENSATION_COMPONENT_CANDIDATE','N3_Components.step employment REGULARIZE; payroll; Components lagged bases','existing payroll charged once to government and HH; new extra G is not automatically this payroll','phase1; model2030-2035 ramp','national/prefectural/municipal employer unspecified; appointing authority vs wage payer separate','IMPLEMENTATION_EVIDENCED'),
 ('C_FOREIGN','4.C','リスク低減型外国人材政策','REGULATORY_AND_PRIVATE_LABOR','Gap_Components foreign_screen/pilot/VA; external GDP5% definition candidate','not automatic public I or G; housing/medical/social costs unallocated','phase1 no exact year','national admission/N4 qualification; regional employers, municipalities and households vary','IMPLEMENTATION_EVIDENCED'),
 ('D_SMART','4.D','戦略的コンパクト化','INSTITUTIONAL_PRIORITY_AND_POTENTIAL_PUBLIC_I','institutions ranks density*productivity/cost; smart_priority B;A;C','no native national public-I amount/asset ledger; diagnostic I25 separate; core replacement investment may overlap unknown','unspecified in original','municipal planning; national/prefectural/local/private project owners conditional, actual shares unknown','IMPLEMENTATION_EVIDENCED'),
 ('S_PHASE1','5','フェーズ1（2026-2032年）','IMPLEMENTATION_TIMING','household_start2030/ramp3; employment fixed2030/ramp6','original timing range not a budget; modeled ramp is candidate','2026-2032','multiple institutions, budget owners unknown','TEXT_CONFIRMED'),
 ('S_PHASE2','5','フェーズ2（2033-2038年）','IMPLEMENTATION_TIMING','medical/pension phase and age75 cohort, partial coverage','no extra G/I source created by transition','2033-2038','insurers/funds/providers/central/local regulators','TEXT_CONFIRMED'),
 ('S_PHASE3','5','フェーズ3（2039年以降）','REGULATORY_INSTITUTIONAL','retained semi-med/pension candidate loop','structural aspiration not a quantified saving or free fund','2039 onward','institutional owner unspecified','TEXT_CONFIRMED'),
 ('KPI_REVIEW','6,7','公平性指標（ジニ係数）悪化','CONDITIONAL_INSTITUTIONAL_TRIGGER','Components.py gini_lagged observations; relief candidate; insurer competition signal only','external observations/size/duration absent; no new quantified public G','2035 review','Owner policy choice needed for supplemental duration/size','OWNER_POLICY_DECISION_REQUIRED')]
 rows=[]
 for ident,sec,marker,classification,impl,overlap,start,executor,status in items:
  loc=location(marker,policy);rows.append(dict(policy_id=ident,original_path='policies/New3linesPolicies.md',original_commit='c087a1a5af12b86cdb140d934754d75e5ee9c4ef',original_section=sec,original_line=loc,original_summary=next(s.strip() for s in policy if marker in s),economic_classification=classification,start_timing=start,implementation_reference=NATIVE+'; '+impl,implementation_fields=impl,implementation_status=status,original_content_status='TEXT_CONFIRMED',sector_and_amount_status='UNKNOWN',unapproved_option_status='OWNER_POLICY_DECISION_REQUIRED',administrative_operator_and_final_payer=executor,original_2030_amount_trn='unknown',original_central_local_share='unknown',increment_GI_monetary_assignment_credit_trn=0.,overlap_and_nonduplication=overlap))
 dump(out/'N3_Policy_Implementation_Expenditure_Trace.csv',rows)
 # Link original-use candidate executors to unchanged preceding instrument map.
 legal={x['instrument']:x for x in rd(AUTH/'N3_Central_Local_Financing_Legal_Authority_Map.csv')}
 links=[
 ('C_EMPLOYMENT','G','CENTRAL_EMPLOYER','national agency appointing/employing authority','government employer pays compensation; not an HH transfer program',['CENTRAL_SPECIAL_DEFICIT_BOND','NET_CASH_REDEMPTION_ROOM'],'CONDITIONAL_OPTION','national salary rules and posts plus annual expenditure/issuance budget'),
 ('C_EMPLOYMENT','G','PREFECTURAL_EMPLOYER','prefecture appointing authority','prefectural government employer; amounts not selected',['LOCAL_FISCAL_ADJUSTMENT_FUND','LOCAL_ALLOCATION_TAX','NATIONAL_GRANT_SUBSIDY'],'CONDITIONAL_OPTION','local salary ordinance/positions/budget; generic local construction borrowing excluded'),
 ('C_EMPLOYMENT','G','MUNICIPAL_EMPLOYER','municipal appointing authority','municipal government employer; no pro-rata allocation',['LOCAL_FISCAL_ADJUSTMENT_FUND','LOCAL_ALLOCATION_TAX','NATIONAL_GRANT_SUBSIDY'],'CONDITIONAL_OPTION','local salary ordinance/positions/budget; original text does not choose municipality'),
 ('D_SMART','G','MUNICIPAL_PLAN_OPERATOR','municipal planning section','plan preparation/ordinary maintenance only if actual expense identified',['LOCAL_ALLOCATION_TAX','NATIONAL_GRANT_SUBSIDY'],'CONDITIONAL_OPTION','urban planning role is evidenced; no automatic GI budget or capital eligibility'),
 ('D_SMART','I','CENTRAL_ASSET_OWNER','national project administrator if nationally owned/commissioned eligible asset','public asset investor, contractor can private',['CENTRAL_CONSTRUCTION_BOND','CENTRAL_SPECIAL_DEFICIT_BOND'],'CONDITIONAL_OPTION','actual project and asset owner, appropriation and bond eligibility unknown'),
 ('D_SMART','I','PREFECTURAL_ASSET_OWNER','prefectural project administrator where eligible','prefectural final investor, not coordinator automatically',['LOCAL_ORDINARY_CONSTRUCTION_BOND','LOCAL_FISCAL_ADJUSTMENT_FUND','NATIONAL_GRANT_SUBSIDY'],'CONDITIONAL_OPTION','project/year/charging ratio/consent/budget required'),
 ('D_SMART','I','MUNICIPAL_ASSET_OWNER','municipality asset/project owner if eligible','planning authority alone does not establish final asset ownership',['LOCAL_ORDINARY_CONSTRUCTION_BOND','LOCAL_ALLOCATION_TAX','NATIONAL_GRANT_SUBSIDY'],'CONDITIONAL_OPTION','same project cannot counted as national and municipal I'),
 ('D_SMART','PRIVATE_I','PRIVATE_ASSET_OWNER','private developer/service operator if private asset','private I must not be classified public I',['NATIONAL_GRANT_SUBSIDY'],'CONDITIONAL_OPTION','public capital grant is transfer; private final formation separate'),
 ('B_IN_KIND','POTENTIAL_G','PUBLIC_FINAL_PURCHASER_OR_INSURER','insurer/benefit administrator unknown','provider final service output versus purchaser sector distinguish',['NATIONAL_GRANT_SUBSIDY','LOCAL_ALLOCATION_TAX'],'UNKNOWN','social in-kind purchases may be SNA G; underlying govt cost already counted'),
 ('B_RELIEF','PREMIUM_REDUCTION','INSURER','premium-collecting institution','household relief and insurer liability, not automatic new public G',['NATIONAL_GRANT_SUBSIDY'],'UNKNOWN','backfill and institutional sector required; no new G allocation'),
 ('B_COOP','INSTITUTIONAL','WIDE_AREA_MUTUAL_ENTITY','10-15 block operator not legally constituted in evidence','not presumed sovereign central/local expenditure owner',['NATIONAL_GRANT_SUBSIDY'],'UNKNOWN','institutional form, membership, claims and contributions not approved')]
 eligibility=[]
 for pid,gi,exe,operator,payer,instruments,status,condition in links:
  for instrument in instruments:
   x=legal[instrument];eligibility.append(dict(policy_id=pid,GI=gi,candidate_final_executor=exe,institution_operator=operator,final_payer_and_asset_owner=payer,instrument=instrument,eligible_in_principle=x['G_eligibility'] if gi=='G' else x['I_eligibility'] if gi=='I' else 'CONDITIONAL_USE_CHECK',mapping_status=status,**{'2030_budget_approved':'unknown','2030_amount_verified':'unknown'},required_authority=condition+'; '+x['authority_holder_and_procedure'],source_evidence=x['source_url']+'; '+x['legal_article_or_location'],unknown_reason='original executor, actual project, annual appropriation, sector tax cash and financing split absent',conditional_option_not_adopted=True,intergovernment_transfer_GDP_credit_trn=0.))
 dump(out/'N3_GI_Executor_Financing_Eligibility_Map.csv',eligibility)
 # Existing statutory categories, not invented N3 projects or budget choices.
 types=[
  ('PLAN_PREPARATION','municipal planning operator','G_OR_INTERMEDIATE_SERVICE_IF_PURCHASED','urban law81; MLIT roles','no capital budget inferred from planning role','common government administration overlap unknown'),
  ('INDUCED_FACILITY_CAPITAL','asset owner central/local/private unknown','PUBLIC_I_ONLY_IF_PUBLIC_ASSET; otherwise privateI','urban law81(2)4イ','asset acquisition/improvement distinct from grants and operating cost','medical/welfare facilities and core replacement may overlap; asset register absent'),
  ('ACCOMPANYING_PUBLIC_UTILITY_CAPITAL','actual public asset investor unknown','POTENTIAL_PUBLIC_I_FOR_NEW_OR_CAPITAL_IMPROVEMENT','urban law81(2)4ロ','existing replacement not second investment; identify incremental physical asset first','core replacement investment geographic/project mapping absent'),
  ('ORDINARY_MAINTENANCE','actual service purchaser unknown','G_INTERMEDIATE_CONSUMPTION_NOT_FIXED_CAPITAL','ESRI47 p24','ordinary repairs cannot relabel as I to satisfy bond eligibility','existing maintenance G boundaries unknown'),
  ('PURE_LAND_OWNERSHIP_TRANSFER','asset purchaser unknown','ASSET_TRANSACTION_NOT_NEW_GDP','ESRI47 p24','land development/improvement distinct; no land-price GDP credit','no proposed N3 land purchase identified'),
  ('CAPITAL_GRANT_TO_PROJECT_OWNER','funding government versus final investor','TRANSFER_NOT_SECOND_G_OR_I','urban law81 and prior subsidy law','cancel public-to-public grant; private asset investment remains privateI','check against final owner capital entry, none identified')]
 dump(out/'N3_Compact_Project_Type_Eligibility_And_Overlap.csv',[dict(candidate_type=t,executor_candidate=e,economic_classification=c,source_scope=src,nonduplication_rule=n,overlap_status=o,policy_status='CONDITIONAL_CLASSIFICATION_ONLY_NOT_PROJECT_ADOPTION',N3_project_or_location='unknown',amount2030_trn='unknown',evidence_monetary_assignment_credit_trn=0.) for t,e,c,src,n,o in types])
 # Cross-scenario same G/I allocations must produce identical consolidated dynamics.
 ann=rd(out/'N3_Policy_GI_Annual_Comparison_2026_2055.csv');idx={(x['case'],x['year']):x for x in ann};checks=0
 for y in range(2026,2056):
  c=idx['CONDITIONAL_CENTRAL_EXECUTOR',str(y)];t=idx['CONDITIONAL_MIXED_WITH_TRANSFERS',str(y)]
  for k in ['real_GDP_trn','total_tax_diagnostic_proxy_trn','CL_debt_candidate_trn','CL_assets_candidate_trn']:
   assert abs(float(c[k])-float(t[k]))<1e-8;checks+=1
 native=rd(out/'N3_Existing_Native_Payroll_Benefits_And_Priority.csv')
 assert all(float(x['public_added_jobs'])==0 for x in native)
 n30=next(x for x in native if x['case']=='CONDITIONAL_CENTRAL_EXECUTOR' and x['year']=='2030')
 assert abs(float(n30['existing_policy_government_cost_delta_trn'])-float(n30['existing_public_payroll_delta_trn'])-float(n30['existing_in_kind_trn']))<1e-8
 # Supplemental originals: fetch missing bytes, never substitute revised contents.
 receipt=json.loads((out/'Public_Source_Receipts.json').read_text());verified=[];article=[]
 for x in receipt:
  if x['status']!='BYTES_RETRIEVED':continue
  p=cache/Path(x['local_path']).name
  if not p.exists():p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(urllib.request.urlopen(x['url'],timeout=60).read())
  b=p.read_bytes();assert len(b)==x['size'] and hashlib.sha256(b).hexdigest()==x['sha256'];verified.append(x['id'])
  if x['id'] in ['LOCAL_CIVIL_SERVICE','URBAN_RENAISSANCE']:
   rt=ET.fromstring(b);body=rt.find('.//MainProvision');title='第二十四条' if x['id']=='LOCAL_CIVIL_SERVICE' else '第八十一条';a=next(a for a in body.iter('Article') if a.findtext('ArticleTitle')==title);text=' '.join(''.join(a.itertext()).split());assert ('条例' if x['id']=='LOCAL_CIVIL_SERVICE' else '市町村') in text;article.append(dict(id=x['id'],article=title,main_provision=True,sha256=hashlib.sha256(text.encode()).hexdigest(),status='VERIFIED_OPERATOR_OR_SALARY_RULE_NOT_N3_AMOUNT'))
 (out/'Supplemental_Article_Verification.json').write_text(json.dumps(article,indent=2)+'\n')
 (out/'Mapping_Verification.json').write_text(json.dumps(dict(policy_trace_rows=len(rows),executor_finance_links=len(eligibility),cross_route_macro_neutrality_checks=checks,existing_payroll_and_in_kind_cost2030_sum_verified=True,new_jobs_in_existing_REGULARIZE_branch=0,extra_GI_evidence_monetary_assignment='unknown',monetary_assignment_credit_lower_trn=0.,supplemental_source_bytes_verified=verified,previous_legal_map_reused_commit='c087a1a5af12b86cdb140d934754d75e5ee9c4ef',sector_cash_closure=False),indent=2)+'\n');print('Policy trace',len(rows),'executor-finance links',len(eligibility),'macro route neutrality checks',checks)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--outdir',type=Path,default=P);a.add_argument('--source-cache',type=Path,default=Path('/tmp/n3-mapping-sources'));z=a.parse_args();run(z.outdir,z.source_cache)
