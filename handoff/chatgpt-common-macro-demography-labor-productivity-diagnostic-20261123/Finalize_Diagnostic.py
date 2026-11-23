"""Deterministic source map, calibration gaps and report from executed results."""
import argparse,csv,json,hashlib
from pathlib import Path
NAME='SPE_Common_Macro_Demography_Labor_Productivity_Diagnostic_Report_DRAFT_20261123.md'
def js(p):return json.loads(p.read_text())
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(out):
 q=js(out/'Verification.json');last=q['keyyears'][-1];a=q['attribution2055'];f=q['F_impact2055'];maps=[]
 def add(item,source,code,status,definition):maps.append(dict(item=item,fixed_commit='77bbad59356407106ff333582040511590bbd7e4',source=source,actual_code=code,connection=status,definition=definition))
 add('population_2026','demography-improved-scenarios-20261118/Inputs.json:population_reference + official_initial_2025_oct','Model.py:demography P=ref+initial_offset+cum','CONNECTED','122618024 conditional 2025 observation + IPSS increment; policy text121500000 is NOT used')
 add('population_years','same inputs: common_foreign_net_flow303315.333333','demography: cum+=flow-baseflow; P,J,F ledger','CONNECTED','2027+historical mean fixed; no independent migrant-descendant cohort;2041+IPSS flow aggregate approximation')
 add('Japanese_age_sex','f-foreign-quantity-20261120/Inputs.json:stage1_inputs.previous_inputs.age_japanese_five_year + base population','embedded previous_model:age_rates and labor_trajectory','CONNECTED','five-year age/sex tables interpolate calendar years; Japanese broad-age totals rescaled to conditional population ledger')
 add('foreign_age_sex','same:age_all_five_year - age_japanese_five_year','embedded previous_model:age_rates(foreign=True), ef sum','CONNECTED','conditional foreign population times IPSS foreign age/sex shares; no independent migrant age evolution')
 add('employment_rates','same:employment_rates_2025 and parameters.foreign_employment_factor=1','embedded previous_model:employment_rate, em,ef','CONNECTED','age-sex employment/population rates; future rates fixed, not labor participation; initial L67.965671million')
 add('domestic_.8_.2_foreign_.7','demography-improved-scenarios-20261118/Model.py','older demography() overridden by later labor_trajectory()','NOT_CONNECTED_AS_FINAL_SQ_L','historical study settings; final current SQ uses age-sex rates instead')
 add('relative_VA','f-foreign-quantity-20261120/Inputs.json:reference.VA_yen/domestic_VA_yen','Model.py:calculate effective*VA/domestic_VA','CONNECTED_UNITY','9154003.810403556/9154003.810403556=1; national SNA average, not foreign marginal productivity; .8/.9 obsolete for current SQ')
 add('effective_L','actual c._trajectory and no SQ elderly policy increment','resolved SQ runtime: labornew=t[effective_productive_workers]+extra_workers','CONNECTED','SQ equals domestic+foreign employed proxies; quality weight1, no explicit working hours; F adds policy hours/health/education channels')
 add('elder_SQ_age_sex_ledger','fixed elder_ledger SQ rates and age-sex bins','c._elder; SQ enabled=False => extra_workers0','BASE_REFERENCE_NOT_ADDED_AGAIN','SQ elderly employment already in domestic employed; no duplicate elderly addition')
 add('nonlabor_A','base_growth=.01 and shared exogenous shock schedule','resolved SQ runtime: nonlabor_factor*=1+base_growth-risk','CONNECTED','A2055=1.0495937586730206; not measured TFP or hourly productivity')
 add('core_GDP','real_gdp580,L0=67965670.59606901, labor_response=.65','resolved SQ runtime: next_coreY=coreY_anchor*A*(L/L0)**alpha','CONNECTED','2026 anchor,29 transitions; nominal additive rule preserved')
 add('final_GDP','same runtime medical, C/I/supply','desired=coreY+capacity_absorption*supply+C+I+education/coreD+...+medical_service/coreD;Y=min(desired,capacity)','CONNECTED','small SQ medical demand adjustment retained; final differs from core by -0.000122051477 in2055')
 add('hours_SQ','no annual hour-by-age-sex-nationality input','no SQ hours multiplier','NOT_CONNECTED','F target entrant hour_weight and pension hours-equivalent are policy-specific; cannot treat SQ L as measured FTE')
 add('capital_TFP','core capital_ratio3; policy K stock','coreK=3*coreY; additional K enters supply','NOT_IDENTIFIABLE_AS_CORE_PRODUCTION_FACTORS','core capital follows GDP; no explicit aggregate capital-labor substitution or measured TFP series')
 add('N3_shared_core','N3 fixed states from SQ and PARITY_CONNECTED_CANDIDATE','Attribution_Runtime.build -> Sensitivity_Runtime -> cached Runner.base/sq','CONNECTED_FIXED_REFERENCE','common core change requires coherent base,price,medical,wage,tax references; adding SQ GDP change to N3 final is invalid')
 dump(out/'SQ_Population_Labor_Productivity_Source_And_Code_Map.csv',maps)
 gaps=[]
 def gap(cat,item,evidence,nextwork,rank):gaps.append(dict(classification=cat,item=item,evidence=evidence,next_executable_work=nextwork,priority=rank,adopted=False))
 gap('CONFIRMED_TECHNICAL_INCONSISTENCY','none found in scoped population/L/core arithmetic','live replay + independent age-sex cells and core formula agree','no corrective coefficient warranted by arithmetic',0)
 gap('STRUCTURAL_MODEL_CHOICE','LEVEL .65 labor response with fixed rates','10 live paths; A and L multiplicative, core capital follows Y','retain current reference; prototype explicit hours and capital channel in isolated copy once matched inputs exist',3)
 gap('DEMOGRAPHIC_CALIBRATION_GAP','conditional2026 population vs text and current estimates','122618024 vs121500000; earlier study2026 estimate122690000;2025 base not fully aligned','use same-version Statistics Bureau population by age-sex-nationality; bridge October stock and calendar flows; do not replace population without employment reinitialization',2)
 gap('DEMOGRAPHIC_CALIBRATION_GAP','migration/cohort/nationality residual','IPSS2023 conditional mean net migration; post2040 aggregate proxy; no migrant descendants','retrieve IPSS age-sex international migration/survival/fertility rates and resident nationality transfers; implement coherent cohort ledger with original scenario flow definition',3)
 gap('LABOR_CALIBRATION_GAP','baseline already age-sex calibrated, not fully nationally calibrated','2025 benchmark68031652.825 vs LFS68280000, gap-248347.175; different annual-vsOctober bases','first reconcile same-year employment versus labor force, resident scope, five-year ages, sex and October/annual timing using Statistics Bureau LFS detailed tables plus population; rerun SQ/F/N3 matched controls',1)
 gap('LABOR_CALIBRATION_GAP','foreign workers conditional domestic-rate application','employment_factor1, same age-sex rates; not observed foreign rates','use resident and employment tables matched dates; MHLW notification scope excludes special permanent residents, cannot divide by all residents without scope bridge',2)
 gap('PRODUCTIVITY_OR_CAPITAL_GAP','SQ hours absent and relative VA unity','SNA2024GDP634.226trn /69284000people=9154003.8104yen; price conversion2024->2026 held1','obtain same-year SNA real VA, total hours, employment and capital services; compare aggregate output/hour versus output/worker; keep national averages distinct from foreign marginal output',2)
 gap('PRODUCTIVITY_OR_CAPITAL_GAP','A not identified TFP; baseline capital determined by coreY','A mixes1%base growth with permanent event losses; no recovery term','document1%meaning and original shock recovery specification; estimate observed TFP only with separate labor-hours and capital inputs; do not raise A to offset demographic loss',3)
 gap('POLICY_SPEC_GAP','text121.5m vs modeled122.618m; shock anchor/recovery','2026 oil initial flagOFF;2027conflict,2028climate,2029disaster,2031quake; recoveryunknown','Owner decision only if adopting revised population baseline or recovery interpretation; no new review gate',3)
 gap('NOT_IDENTIFIABLE','migration causal GDP, TFP, capital substitution, future employment improvements','mix Shapley uses conditional accounting; future rates frozen','no causal migration claim, no invented productivity improvement; retain missing values',0)
 dump(out/'SQ_Labor_Productivity_Calibration_Gaps_And_Fixes.csv',gaps)
 rows=['# SPE｜共通マクロの人口・労働・生産性接続の限定精査','',
 '**2026-11-23 / DRAFT / NON-CANONICAL / ISOLATED DIAGNOSTIC**','',
 '## 結論と今回できるようになったこと','',
 '現行SQの2055年実質GDP528.962336兆円への低下は、人口減少と年齢・性別構成の変化が、固定された年齢別就業率の下で有効労働を2026年比80.5594%へ下げる経路から生じる。非労働係数Aは1.049594へ増え、低下を一部相殺する。就業率の年次低下や、外国人生産性800万円／国内900万円が現行の原因ではない。現行の年齢・性別就業率は将来固定、相対付加価値は1である。','',
 '今回、年齢×性別×国籍のセルから就業者とLを独自に再構成し、実コードの全年値と照合した。人口規模・国籍構成・大区分年齢構成・区分内年齢／性別構成・Aの5要因を、32組合せの厳密Shapley分解で比較できるようになった。さらに既存エンジン上でSQ8枝とF2対照、計300年次を実行し、共通労働低下を除いた場合のF−SQ差まで比較した。既存結果の再現だけが成果ではない。','',
 '## 固定原本・実行','',
 '- 依頼・実行入力固定：`77bbad59356407106ff333582040511590bbd7e4`。','- 既存3施策：`e981c924adbe9c7ca77b96d2dc94e40378186613`。','- Claude独立検算：`3611534d85fb52c976592c96120f7663dbfa63f5`。既存2845項目とWork2826項目のPASSは固定対象のみで再利用。本診断の独立検算済みとはしない。','- 両固定ディレクトリの個別原本をgit固定オブジェクトから実バイト取得し、自身でSHA-256・サイズ記録。実際に読まれた依存コードはopen監査と固定gitオブジェクトで照合。`Fixed_Source_Receipts.json`参照。','- 共通エンジン、政策本文、既存成果は変更せず、メモリ内のL接続・A蓄積のみ診断置換。全枝580／600の初期値、2026起点・29遷移、共通物価・イベント日程・SQ医療参照を保持。A固定枝だけは実質への基調成長とイベント蓄積を共に無効化する。','',
 '## 現行の計算経路','',
 '人口は11月18日研究の条件付き人口勘定を継承するが、その後の埋込み`previous_model`の`labor_trajectory()`が労働を上書きする。日本人は社人研の5歳階級・男女分布を年次補間し、人口勘定の3区分年齢人口へ再配分する。外国人は総人口−日本人の年齢・性別分布を常住外国人ストックへ配分する。双方に2025年の年齢・性別就業率を適用。日本人・外国人の就業者を合算してLへ接続する。','',
 '旧研究の国内15–64歳0.8／65歳以上0.2、外国人全住民就業割合0.7、800万円／900万円は後続実装で置換済みであり、現行SQの最終Lへそのまま使われていない。現行の915.400381万円は2024SNAの全国GDP／就業者に由来する参考値で、国内・外国人とも同値のため相対係数は1。全国平均を外国人の限界付加価値と承認したわけではない。','',
 'Lは条件付き就業人数を基礎とする有効労働proxyであり、SQの労働時間系列や実測FTEではない。Fでは外国人対象コーホート・高齢就労・年金の時間換算・教育・健康の追加労働が別途作用する。高齢者のSQ就業は国内就業者に既に含まれ、高齢就業台帳を再加算しない。','',
 '`A_t=Π(1+0.01−risk_t)`、`Ycore_t=580×A_t×(L_t/L2026)^0.65`。最終GDPはコアにC/I、追加資本供給、教育、医療サービスを足し、供給上限を適用する。AをTFPや時間当たり労働生産性と同義にしない。コア資本は3×コアGDPの会計規則であり、独立した資本投入による人口減少の代替を推定する生産関数ではない。','',
 '## 年次実値','',
 '|年|人口（万人）|L（万人）|A|コアGDP（兆円）|最終GDP（兆円）|','|---|---:|---:|---:|---:|---:|']
 for r in q['keyyears']:rows.append(f"|{r['year']}|{r['population']/1e4:.3f}|{r['L_used']/1e4:.3f}|{r['A']:.6f}|{r['core_real_GDP_trn']:.6f}|{r['final_real_GDP_trn']:.6f}|")
 rows+=['',f"580割れ初年は{q['below580_first']}年、2027–2055の{q['below580_years']}年すべてで580を下回る。2055年は580×{last['A']:.9f}×{last['labor_level_factor']:.9f}={last['core_real_GDP_trn']:.9f}兆円。最終との差{last['core_final_gap_trn']:.12f}兆円は既存SQ医療・需要項の純差であり、丸め誤差ではない。年次のC/I・供給・需要・価格圧力と残差は年次CSVと実行トレースへ格納。",'',
 '非労働係数の1%成長単独は2055年1.334504倍、イベント適用後は1.049594倍（成長単独比0.786505）。イベントは2027紛争5%、2031地震3%、2029起点3年毎災害1%、2028起点隔年気候0.5%。同年のリスクは合算後1+成長−riskへ一度反映する。回復項は存在せず、2026オイルは初期遷移がない既存仕様のため不適用。今回これらを変更していない。','',
 '## 2055年の要因分解','',
 '|要因|コアGDP変化（兆円）|','|---|---:|']
 labels=['非労働係数A','人口規模','国籍構成','大区分年齢構成','区分内年齢・性別構成']
 for label,r in zip(labels,a[:5]):rows.append(f"|{label}|{r['Shapley_core_change_trn']:+.6f}|")
 rows+=['',f"5要因の和は{sum(r['Shapley_core_change_trn'] for r in a[:5]):+.9f}兆円でコア変化へ一致。相互作用は全順序の平均として各要因に配賦した機械的分解で、統計的な因果推定ではない。国籍構成のプラスを移民政策の因果効果としない。国籍別出生・死亡・国際移動・国籍変更の未分離残差も構成に含まれる。",'',
 'A／Lの単独寄与は+28.764380／−76.031246兆円、積項は−3.770675兆円。A→L順なら+28.764380／−79.801922、逆順なら−76.031246／+24.993705。単純加算で相互作用を消していない。就業率そのものの時間変化、相対VAの時間変化は入力固定のため0。労働時間、観測TFP、資本代替は未識別であり0と置換しない。','',
 '## 隔離反実仮想','',
 '|枝|2055最終GDP（兆円）|現行差（兆円）|','|---|---:|---:|']
 labels={'BASE_SQ_REPLAY':'現行再実行','L_FIXED':'Lを2026固定','A_FIXED':'Aを1固定','POPULATION_ONLY':'人口規模のみ変化','AGE_SEX_FIXED':'国籍別年齢・性別構成固定','NATIONALITY_SHARE_FIXED':'国籍人口比固定','BROAD_AGE_FIXED':'国籍別3区分年齢比固定','WITHIN_AGE_SEX_FIXED':'区分内の年齢・性別比固定'}
 for r in q['counterfactual2055']:rows.append(f"|{labels[r['case']]}|{r['final_real_GDP_trn']:.6f}|{r['GDP_minus_BASE_SQ_trn']:+.6f}|")
 rows+=['',
 'L固定・人口／構成固定は労働接続だけの反実仮想で、人口・出生死亡・純移動・医療の帳簿自体は変えない。実現可能な人口政策や目標GDPへ合わせた係数ではない。就業率・付加価値・労働弾性は変更しない。就業割合0.6/0.7/0.8等の旧研究感度は条件の異なる既存研究として再利用し、現行SQの同条件感度として再掲しない。','',
 '## F・N3への波及','',f"FとSQへ同じ共通労働減少分を足し戻す最小対照を実行した。Fの全既存政策モジュールを再実行し、高齢就労・外国人材・年金・教育・健康の数値差を固定転記しない。2055年はSQ {f[0]['SQ_same_diagnostic_GDP_trn']:.6f}→{f[1]['SQ_same_diagnostic_GDP_trn']:.6f}、F {f[0]['real_GDP_trn']:.6f}→{f[1]['real_GDP_trn']:.6f}兆円。F−SQは{f[0]['GDP_minus_matched_SQ_trn']:.6f}→{f[1]['GDP_minus_matched_SQ_trn']:.6f}（+{f[1]['GDP_minus_matched_SQ_trn']-f[0]['GDP_minus_matched_SQ_trn']:.6f}兆円）。これは共通労働低下を除く構造診断で、正式修正案の予測効果ではない。",'',
 'N3は現行固定成果483.991492兆円を再利用。共通人口・労働・コアはSQと共通で、政府追加G/IはOFFのまま。L固定時には共有コアだけで2055年+79.801922兆円動くが、この額をN3最終GDPへ足してはいけない。N3はRunner.base/sq、医療初期化、給与・税・価格等の固定参照を読むため、整合した基底状態の再構築が必要。今回N3の新しい最終GDPは未計算・空欄とし、F／SQと同じ最小局所フックで有効なN3政策比較が完了したとは扱わない。依頼書がF/N3全政策再計算を完了条件にしない境界に従う。','',
 '## 不足の分類と次の実務','',
 '計算上の人口・L・GDP接続に確定的な技術不整合は見つからなかった。一方、年齢・性別較正の存在と全国較正完了は異なる。旧研究の不足を、そのまま現在も未接続だと判定しない。','',
 '最優先は既存の年齢・性別就業計算を維持しつつ、人口と就業者の基準年・対象・時点の整合を取ること。既存2025ベンチマークは68,031,652.825人、労働力調査年平均68,280,000人との差−248,347.175人を開示済みで、人口基準・10月／年平均が異なる。単純な全国人数への倍率合わせを先行しない。L/L0方式では全年度の一様倍率はGDPから相殺され、全国水準を合わせても将来の構成変化を検証したことにならない。','',
 '次いで、同年・同基準のSNA実質付加価値／総労働時間／就業者／資本と接続して、人数・FTE・時間当たり生産性を別系列にする。外国人雇用届出と常住人口は対象・日付を合わせる必要があり、単純除算を正式就業率にしない。資本代替や将来就業率改善は別の入力・仕様が必要で、1%基調成長や労働弾性の変更で代用しない。具体的な原典・実装箇所・不足分類は`SQ_Labor_Productivity_Calibration_Gaps_And_Fixes.csv`を参照。','',
 '人口122,618,024は2025実績を社人研2025→2026差で延長した条件付き値。原文121,500,000との差1,118,024人は仕様／基準差で、実装の加算ミスではない。2026人口の最新統計への全面再較正、移民の子孫出生・死亡・国籍移動コーホートは今回未実施。11月18日のSQ_COMMON2055GDP527.852兆円は別系列であり、現行528.962兆円との差を政策効果にしない。','',
 '## 検証・再現・引渡し','',
 f"本診断の検証は{q['checks']}項目、失敗0。実コードの現行SQとF固定結果、独自の年齢・性別セル計算、人口・外国人の橋渡し、L・A・コア、最終需要・供給恒等式、初期580/600、イベント・物価・医療参照の不変、5要因寄与と積項を検査。Python {q['python']}、標準ライブラリのみ。年齢セル数はCSVに全件保存。",'',
 '```bash','python Diagnostic_Reproduce.py --root <fixed-checkout-77bbad59> --out <empty-output>','python Finalize_Diagnostic.py --out <empty-output>','```','',
 '再生成の実バイト一致は`Reproduction_Verification.json`、GitHub指定保存先への格納・固定Commit事後取得のSHA-256／サイズ照合は`Custody_Verification.json`を参照。報告書は保全記録そのものの代替ではない。ZIPなし、個別原本で引き渡す。','',
 '正式Acceptance・PR・merge・Canonical化・Freeze、Finding Close、DecisionLog更新、HOLD解除は行わない。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。共通本体・政策原文の修正採用は本診断に含まない。']
 (out/NAME).write_text('\n'.join(rows)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out.resolve())
