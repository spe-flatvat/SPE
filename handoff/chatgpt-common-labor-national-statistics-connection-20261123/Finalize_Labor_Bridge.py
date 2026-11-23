"""Deterministic definition map, limits, and result report. No model mutation."""
import argparse,csv,json
from pathlib import Path
NAME='SPE_Common_Labor_Definition_National_Statistics_Connection_Report_DRAFT_20261123.md'
def js(p):return json.loads(p.read_text())
def dump(p,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',newline='') as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def run(out):
 q=js(out/'Verification.json');s=js(out/'Statistics_Inputs.json');last=q['SNA2024'];maps=[]
 def add(var,unit,definition,source,code,status,future):maps.append(dict(variable=var,unit=unit,definition=definition,official_source=source,implementation=code,connection_status=status,future_scope=future))
 add('population15plus','persons','resident persons age15+; not whole-population employment denominator','LFS2025 I-B-1 row11;population-estimates202610;IPSS2023','model age/sex population cells summed age>=15','CONDITIONAL_PROXY','conditional October-origin population projection; not measured annual average')
 add('labor_force','persons','employed plus unemployed; participation=LF/pop15+','LFS2025 I-B-1 row12','2025 totals70040000;future column empty','SAME_DEFINITION_OFFICIAL_2025_ONLY','N/A future; do not label employed L as labor force')
 add('employed_persons','persons','resident employed incl not-at-work; one person, multiple work hours combined','LFS2025 I-B-1 row13','prior age-sex cells; detail candidate substitutes age15-64 observed E/P','CONDITIONAL_PROXY','new rates2025 fixed; age65+ existing detail preserved')
 add('employee_jobs','jobs','employees excluding self-employed/family workers;SNA job-basis','SNA2024 supplement3 calendar employees','same-year historical employees61842000; future N/A','SAME_DEFINITION_SNA_HISTORY_ONLY','do not multiply all employed by employee-only hours1661.5')
 add('SNA_employed_jobs','jobs','SNA domestic employment includes secondary jobs separately','SNA2024 supplement3 calendar employed;hours reference note20180330','69284000 jobs; 2024 hours per job1665.2','SAME_DEFINITION_SNA_HISTORY','not a one-to-one denominator for LFS persons')
 add('weekly_hours','person_hours_per_week','sum of hours across jobs; absentees have zero actual survey-week hours;unknown-hours excluded from mean denominator','LFS2025 I-B-9 AG aggregate weekly,AF mean;official terms p3','aggregateweekly / all employed; use each age/sex cell, retain published rounding','CONDITIONAL_PROXY','coefficients fixed2025;foreign-specific hours unavailable;65+pooled bysex')
 add('annual_actual_hours_SNA','job_hours_per_calendar_year','all-employed job count times matched annual reference hours; derived from rounded published cells','SNA2024hw and2024s3','2005-2024 total hours computed;2024=115371716800','SAME_DEFINITION_SNA_HISTORY','fixed2024 average is neutral diagnostic; not a future SNA forecast')
 add('annualized_weekly_hours','person_hours_per_diagnostic_year','52 times annual-average monthly survey-week aggregate coefficient','LFS2025 I-B-9','H=sum(pop_age_sex*employment_rate*52*aggregateweekly/employed)','CONDITIONAL_PROXY','not observed annual hours;month-end survey weeks and holiday coverage differ from annual series')
 add('FTE_diagnostic','2080hour_equivalents','H/(40*52); declared conversion convention only','no claim of official FTE measurement','FTE_reference_hours2080; ratio H/H0 unchanged by reference','CONDITIONAL_PROXY','official fulltime schedule/FTE remains N/A; convention not annual actual hours')
 add('effective_L','2026_anchor_equivalent_persons','current employment-based proxy;not measured hours or official FTE','prior pinned current SQ trace','engine_L=L0_current*(physical_labor_t/physical_labor_2026)','CONDITIONAL_PROXY','physical persons/hours exported separately;initial580/600 unchanged')
 add('value_added_per_job','yen_per_job','SNA same-year nominalGDP or chain-realGDP divided by domestic jobs','SNA2024 calendarGDP andjobseries','2024nominal9154003.8104;real8435874.0835','SAME_DEFINITION_SNA_HISTORY','not marginal foreign productivity or labor remuneration')
 add('real_value_per_hour','2020_chain_yen_per_hour','same-year realGDP or production subtotal divided by all-employed SNA hours','SNA2024 GDP584.4711trn;production subtotal587.5782trn;hoursreference','historical2005-2024;constant2024rate satellite only','SAME_DEFINITION_SNA_HISTORY;MODEL_SATELLITE_CONDITIONAL','not added to coreGDP;model real-price base correspondence N/A')
 add('A','dimensionless_level','product(1+base_growth-risk);mix of structural growth and shock effects','unchanged fixed common macro parameters','A retained exactly; no new productivity trend or multiplier','STRUCTURAL_MODEL_CHOICE','not observed TFP or hourly labor productivity')
 add('TFP','N/A','requires separate hours,capital services,and appropriate production accounting','not obtained as identified series','empty;not estimated as A','N/A','no future TFP generated')
 add('capital_services','N/A','input service flow distinct from investment/stock or3*GDPaccounting','no matched capital-service series connected','empty;coreK remains3*coreY existing rule','N/A','no invented capital substitution')
 add('foreign_resident_worker_status','persons orjobs according to source','resident foreigners, registered-residence holders,and employer notification populations differ','existing fixed foreign research;currentLFS tables lack nationality split','apply same age-sex rate/time conditionally;do not add MHLWnotification count','CONDITIONAL_PROXY','no foreign marginal productivity assumption;no population double addition')
 add('F_policy_labor','existing_equivalent_workers','baseline trajectory inclforeign/pension pluselderincrement+education+health once','F integrated inputs andmedical_education_integrated runtime','labor identity checked term-by-term,commonoffset applied once','CONDITIONAL_PROXY','no conversion of existing policy hours twice;not full policy cohort FTE')
 add('N3_fixed_common_core','same-as-SQ','N3 reads cached common baseline states,medical,wage,price,taxreferences','Attribution_Runtime->Sensitivity_Runtime->Runner.base/sq','native replay and algebraic neutral-unit compatibility;changed detailGDP N/A','CONDITIONAL_PROXY','changed bridge requires coherent base reconstruction;no SQdelta pasted into N3final')
 dump(out/'Labor_Employment_Hours_FTE_ValueAdded_Definition_Map.csv',maps)
 gaps=[]
 def gap(cat,item,done,missing,next):gaps.append(dict(classification=cat,item=item,executed_or_verified=done,remaining_gap=missing,next_executable_fix=next,adopted=False))
 gap('DATA_DEFINITION_ALIGNMENT','SNA persons vs jobs and employee vsall-employedhours','14official originals;411extractedcells;20same-vintagehistoricalyears','LFS-person to SNAjob person-level crosswalk unavailable','retain distinct columns; obtain main/secondaryjob bridge before national-level cross-scaling')
 gap('DATA_DEFINITION_ALIGNMENT','LFS denominator and actualhours','I-B-1 E/P;I-B-9 aggregatehours/E;absence and unknown denominator distinguished','2025annualized52week proxy not annual actual hours','obtain age-sex annual hours including absence and unknown-hours treatment;do not equate mean weekly35.9 withall-employedmean')
 gap('CALIBRATION_CANDIDATE','age15-64 fine-age E/P connection','2025fineagerates fixed on unchanged conditional population;30yearGDP executed','age65+fine detail preserved from old model;new table70+coarse cannot replace70-74/75+detail','obtain same2025age65-69/70-74/75+population andemployment thencomparecoherent refinement')
 gap('CALIBRATION_CANDIDATE','nationalbenchmark gap accounting','2025gap248347.175 split algebraically;rounding-10000 retained','timing-vs-populationbenchmark-vs-sampling causes not separately identified','same-year monthlyage-sexpopulation/exposure plusemployment totals; retain residual rather than scaleL')
 gap('CALIBRATION_CANDIDATE','foreign age-sex employment/hours','conditional shared age-sex coefficients;population countedonce','no nationality-specific matched employment/hours;notice-vsresident scopes differ','retrieve matched nationality-age-sex resident andemployed hours withcoveragebridge;do not divide incompatible counts')
 gap('STRUCTURAL_MODEL_CHOICE','hours andFTE input vs headcount','sixSQbranches,threeFcontrols,oneN3replay;2026boundaryandAunchanged','weeklyannualization52;FTE2080 convention;hoursweighted .65laborresponse not reestimated','retain isolated candidates;review labor elasticity only withidentifiedproductionmodel andinputs')
 gap('STRUCTURAL_MODEL_CHOICE','SNArealGDP/hour vs futureproductivity','historicalrealGDPandproduction-subtotal/hour;constant2024satellite','capital/institutionalcomposition included inobservedproductivity;not causal labor productivity','keep observedseries separate;requirematchedcapital-servicesbeforeTFPdecomposition')
 gap('POLICY_SPEC_REQUIRED','Fpolicycohort hoursunits','existingbaseline/elder/foreign/pension/education/health enter once;componentidentitychecked','commonoffsetcandidate doesnotrebuild age-sex-policycohort hour exposures','if adopted, define mapping for equivalent labor alreadyhoursweighted;rebuild jointly andrerunmatchedF/SQ')
 gap('STRUCTURAL_MODEL_CHOICE','N3changedcore reference rebuild','N3unchangednative replay;neutralunits algebra checked','changedhours/detailN3final N/A becausebase/sq/medical/wage/taxreferencecaches','coherently rebuild sharedSQandN3base references, thenrun existingnativeN3withoutextraGI')
 gap('NOT_IDENTIFIABLE','future employment gain,TFP,capital substitution','none inserted;missingcolumns N/A','no externally specified future hours orproductivity forecast','do not infer missingfutureimprovements fromhistoricaltrend')
 dump(out/'Labor_Statistics_Calibration_Gaps_And_Next_Fixes.csv',gaps)
 labels={'BASE_SQ_UNCHANGED':'現行SQ','HEADCOUNT_DETAIL_2025':'人数・2025細分年齢率','UNIFORM_LEVEL_CONTROL':'全国一様倍率の対照','SNA_HOURS_FIXED_CONTROL':'SNA全国平均時間一定','LFS_HOURS_BASE_RATES':'LFS時間・現行就業率','LFS_HOURS_DETAIL_RATES':'LFS時間・細分年齢率'}
 l=['# SPE｜共通労働投入の定義・全国統計接続の限定実装','',
 '**2026-11-23 / DRAFT / NON-CANONICAL / ISOLATED IMPLEMENTATION AND EXECUTION**','',
 '## 実成果と結論','',
 '就業人数ベースの現行Lを保持し、実際に取得した2025年労働力調査の年齢・性別人数と延週間時間、および2024年版SNAの同年GDP・就業者仕事数・年間時間を、別変数として接続する隔離コードを実装した。SQ6枝・F3対照・N3現行再実行1枝、計10経路300年次を実行。年齢×性別×国籍の人数・時間セル、診断FTE、過去20年の同基準時間当たり実質GDPが新たに計算可能になった。資料収集のみで終了していない。','',
 '全国人数の一様倍率と一定の全国平均時間はL/L0で相殺し、GDPは変わらない。細分年齢の就業率と時間構成を使う条件付き枝では2055年SQが527.366621兆円（現行比−1.595715）。統計接続によりGDPが上がるとの結果ではない。経済予測としての全国較正完了や正式採用は宣言しない。','',
 '## 固定原本・原典の取得','',
 '- 依頼固定：`ec98f9751cf8fc27a76d001c7e5425f904ece62c`。前回診断`9dcf953e949593e773bab906eb72577f0efec73e`、3施策`e981c924adbe9c7ca77b96d2dc94e40378186613`、Claude独立検算`3611534d85fb52c976592c96120f7663dbfa63f5`を実バイトで自己回収・照合。前回報告と較正不足表を最初に読んで再利用した。','- 原典14ファイルを直接HTTPS取得。Excel411セルを表・シート・座標付きで抽出し、原本実バイトは`Source_Originals/*.json`にbase64で個別保存。復号後SHA-256・サイズを検査。ZIP生成・配布なし。これは原本そのもののバイト保存で、検索結果の転記ではない。','- Web読取ツールはExcelの本文抽出に非対応だったが、実行環境からの直接取得・openpyxl抽出に成功。e-Statの一部詳細ページをWeb読取で取得できなかった場合も、公式年報一覧と実際のダウンロード原本で表ID・公開日・表題を確認した。','',
 '|原典|対象・基準|使用箇所|','|---|---|---|',
 '|[SNA2024年次推計](https://www.esri.cao.go.jp/jp/sna/data/data_list/kakuhou/files/2024/2024_kaku_top.html)|2020年基準・2008SNA、暦年、季調なし。支出側名目／実質、活動別実質、付表3就業者／雇用者|2005–2024暦年、付表3の行39、主要系列GDP行48、活動別小計行51|',
 '|[SNA就業者時間参考系列](https://www.esri.cao.go.jp/jp/sna/data/data_list/hours-worked/hw_top.html)|2020年基準、2005–2024、2026-01-30公表、全就業者の年間時間|仕事ベースの同年就業者×年平均時間。自営業等を含む参考推計|',
 '|[労働力調査2025年報](https://www.e-stat.go.jp/stat-search/files?cycle=7&layout=datalist&month=0&page=1&tclass1=000001227003&toukei=00200531&tstat=000001226891&year=20250)|2025暦年平均、2026-03-31表公開、季調なし、2020国勢調査基準の人口系列を参照|I-B-1男女計／男／女：000040440941/942/943。I-B-9：000040440953|',
 '|[人口推計2026年10月](https://www.stat.go.jp/data/jinsui/pdf/202610.pdf)・[社人研2023](https://www.ipss.go.jp/pp-zenkoku/j/zenkoku2023/pp2023_gaiyou.pdf)|人口は10月1日、社人研2020国勢調査基準、出生死亡暦年との時点差あり|既存2025観測→2026条件付き推計の出典確認。人口・移民モデル自体は不変|',
 '|[労働力調査用語](https://www.stat.go.jp/data/roudou/pdf/yougo_kaisetsu.pdf)・[SNA時間の推計説明](https://www.esri.cao.go.jp/jp/sna/data/data_list/hours-worked/pdf/hw_announce.pdf)|就業率、休業者、平均時間分母、仕事ベースを確認|人数・時間の母集団差と二重計上を区別|','',
 '個別原表の対象年、公表日、価格基準、母集団、単位、季調、年平均／10月時点、取得日、SHA・サイズは`Official_Statistics_Source_Definition_And_Receipts.csv`へ記録。SNA主要系列は2024年次推計のフロー公表2025-12-23を参照するが、個々の取得ファイルの改訂日を独立に確定していない部分はその旨を明記した。外国人雇用届出・在留統計は前回固定研究を再利用し、新しい同時点国籍別時間統計を得たとはしない。','',
 '## 定義接続：人数・仕事・時間を混ぜない','',
 '現行SQは、条件付き常住人口に2025年年齢×性別就業率を適用して合算した就業人数proxy。失業者を含む労働力人口ではなく、実測FTE・労働時間調整済み人数でもない。労働力調査の就業率は15歳以上人口に対する就業者割合で、労働参加率とは別である。雇用者も自営業主・無給家族従業者を含む就業者とは別変数にした。','',
 'SNAの就業者は仕事ベースで、同じ人の副業を別仕事として数える。SNA内の同年仕事数と年間時間は接続できるが、LFSの居住就業人数へSNA人数を合わせる倍率は較正しない。通常付表3の時間は雇用者向けであり、全就業者へ掛けない。全就業者用の別の時間参考系列を用いた。','',
 'LFSの公表平均週間時間は、延週間時間を、休業者と週間時間不詳を除く従業者数で割る。2025年の35.9時間を全就業者6828万人へ直接掛ける処理は不採用。本実装は同じ表の延時間AG÷全就業者Lを、全就業者1人当たりの公表延時間寄与として用いた。休業者の調査週時間0は公式定義。不詳者の時間を新たに推定・0補完していない。公表延時間の集計範囲と丸めの制約を引き継ぐ。','',
 '年齢×性別時間はI-B-9の15–19、20–24…60–64、65歳以上を使用。65歳以上の時間は性別内で同じ集計値を当てる条件付きproxyで、それ以上の細分値は発明しない。外国人の国籍別時間を取得できていないため、同じ年齢×性別係数を条件付きで適用する。外国人固有の実測時間・限界生産性ではない。','',
 '## 取得実績の計算','',
 f"2024年SNA：就業者{last['SNA_jobs']/1e4:,.1f}万仕事、雇用者{last['SNA_employee_jobs']/1e4:,.1f}万仕事。全就業者参考時間{last['annual_hours_per_job']:,.1f}時間／仕事、雇用者時間{last['employee_hours_not_all_workers']:,.1f}時間／仕事。前者による総時間は{last['total_hours_derived']/1e8:,.6f}億時間。実質GDP{last['real_GDP_2020_chain_trn']:.6f}兆円（2020年連鎖価格）／総時間＝{last['real_GDP_per_hour_yen']:,.6f}円／時間。活動別実質小計{last['real_production_subtotal_chain_trn']:.6f}兆円による比率は{last['real_production_subtotal_per_hour_yen']:,.6f}円／時間で、支出側GDPと区別。名目GDP634.226兆円／仕事は915.400381万円であり、実質GDP／仕事843.587408万円とは別である。",'',
 '2005–2024の全20年を同じ2020年基準・取得版で実計算した。連鎖実質の活動別小計は公表集計値を使用し、業種の連鎖系列を独自に加算してGDPと一致させない。過去のGDP／時間は資本・産業構成・帰属家賃等を含む平均生産性で、TFPや外国人の限界生産性ではない。SNAとLFSの年・母集団が異なる値同士を無理に除算しない。','',
 '## 隔離実装','',
 '人数枝は、公表2025 I-B-1の15–64歳の5歳階級別・男女別E/Pを、現行の同じ人口セルへ接続する。2025年率を将来固定し、就業率改善を外挿しない。65歳以上は取得表が70歳以上をまとめているため、現行65–69／70–74／75歳以上率を保持し、粗い値で上書きしない。これは部分的な定義・分解能の接続候補であり、全国人口への全面較正ではない。','',
 '時間枝は`H_t=Σ人口セル×就業率×(公表延週間時間／公表就業者数)×52`。52倍は診断用の年換算で、月末調査週から実測年間時間を復元したとはしない。将来の年齢・性別内時間は2025年値を固定。SNA2024年全国平均1665.2時間一定は別の中立対照に分離する。','',
 '診断FTEは`H/2080`（40時間×52週）と定義した単位換算。2080は今回の表示基準であり、統計から取得した年間フルタイム実労働時間や法定年労働時間ではない。公式FTE・将来のフルタイム実測値はN/A。FTE基準を変えてもH/H0とGDPは不変になる。','',
 'GDP接続は、物理的な人数／時間とエンジン単位を分け、`engine_L_t=L0_current×physical_L_t/physical_L_2026`とする。これにより各枝は自分の2026基準で正規化され、実質580／名目600を保持する。労働弾性0.65、人口・移民、基調成長1%、イベント日程、医療参照を変えない。単位換算係数はGDP目標へのフィットではない。','',
 '生産性は過去実績の接続と、2024年観測時間当たり実質GDPを将来時間proxyへ掛ける別表の一定係数サテライトに限定した。サテライトの絶対額は2020年連鎖価格で、SPE実質GDPの価格基準との対応はN/A。これを580へ倍率合わせしたり、GDP・Aへ足したりしていない。将来TFP・資本代替・時間当たり生産性上昇の新系列は作らず、Aとの二重計上を避けた。','',
 '## 2055年の比較','',
 '|枝|就業人数（万人）|年換算時間proxy（億時間）|診断FTE（万人）|実質GDP（兆円）|現行差（兆円）|','|---|---:|---:|---:|---:|---:|']
 for r in q['case2055']:
  h='N/A' if r['total_hours_proxy'] is None else f"{r['total_hours_proxy']/1e8:.3f}";ft='N/A' if r['FTE_diagnostic'] is None else f"{r['FTE_diagnostic']/1e4:.3f}"
  l.append(f"|{labels[r['case']]}|{r['headcount']/1e4:.3f}|{h}|{ft}|{r['real_GDP_trn']:.6f}|{r['GDP_minus_current_SQ_trn']:+.6f}|")
 l+=['',
 '2026/2030/2035/2039/2055は`SQ_Labor_Bridge_Key_Years.csv`、全30年は2つの年次・比較CSV、人口・性別・年齢・国籍セルは`SQ_Age_Sex_Employment_Hours_Bridge_Cells.csv`。現行の総時間を過去から既に持っていたようには表示せず、時間を接続しない枝の時間／FTEは空欄とする。','',
 f"2055年の2×2分解は、細分率の主差{q['interactions2055']['employment_definition_main_delta_trn']:+.6f}兆円、時間重みの主差{q['interactions2055']['time_weight_main_delta_trn']:+.6f}兆円、相互作用{q['interactions2055']['interaction_trn']:+.6f}兆円で、合計{q['interactions2055']['total_delta_trn']:+.6f}兆円へ閉じる。順序依存の差もCSVへ残した。前回5要因Shapleyは元のSQ条件で再利用し、異なる条件の時間寄与をそこへ直接足さない。因果推定や政策効果の順位ではない。",'',
 '## 2025全国就業人数差の説明範囲','',
 '|項目|人数差（人）|解釈|','|---|---:|---|']
 for r in q['benchmark_gap'][2:]:l.append(f"|{r['component']}|{r['persons']:+,.3f}|{r['interpretation']}|")
 l+=['',
 '旧68,031,652.825とLFS68,280,000の差248,347.175人を、取得表で説明できる代数的な項へ分離した。人口基準の差に暦年平均／10月時点・推計・年齢構成差が含まれるが、その原因別額を実証していない。高齢層の未分離差と公表丸め残差を消さず、全国総数へ合わせる一様倍率を正式接続には採用しない。一様倍率対照ではGDP差が浮動小数点誤差内0となることを実行確認した。','',
 '2026初期人口122,618,024は既存の条件付き推計を保持。2025年10月人口123,219,024／日本人119,379,692と社人研の2025→2026差から得た人口で、2025年平均LFS母集団や原文121,500,000と同一ではない。今回、最新人口へ自動補正しない。','',
 '## F・N3への波及と二重計上','',
 '|F対照|2055 F実質GDP|対応SQ|F−SQ|','|---|---:|---:|---:|']
 for r in q['F_N3_2055'][:3]:l.append(f"|{r['case']}|{r['real_GDP_trn']:.6f}|{r['matched_SQ_GDP_trn']:.6f}|{r['GDP_minus_matched_SQ_trn']:.6f}|")
 l+=['',
 'Fは既存政策モジュールを再実行し、共通基底への差`L0_current×bridge_ratio−L_SQ_current`だけを1回加える最小対照とした。既存外国人・年金時間換算はtrajectory内にあり、高齢追加就労・教育・医療健康を各1回だけ加える実行時恒等式を検査した。SQ既存高齢就業を再加算せず、人数×時間×付加価値をGDP追加額として重ねない。','',
 'ただしFの新規対象コーホートをすべて年齢×性別の時間で再構成した完全FTEモデルではない。既存の教育・健康は有効労働proxyで、年金・対象外国人には既存の時間換算がある。この部分へもう一度時間係数を掛けると二重調整になる。今回のF比較は共通基底の差を伝播させる条件付き対照として限定する。','',
 'N3は既存ネイティブモデルを30年再実行し、2055年483.991492兆円へ一致。政府追加G/IはOFF。一様倍率／一定時間の中立対照はL/L0が同じなので既存基底で互換性を確認できるが、変更後の細分率・時間枝のN3最終GDPはN/A。Runner.base/sq、医療初期化、価格・給与・税・財政参照の整合した再構築が必要であり、SQ差をN3最終GDPへ単純加算しない。この未計算部分を隠さず、N3全面再設計を今回の完了条件へ追加しない。','',
 '## 採用候補と残る不足','',
 '1. **DATA_DEFINITION_ALIGNMENT**：人数／仕事数、全就業者／雇用者時間、平均時間の分母、同年SNA実質／名目を分離するインターフェースと出典セル対応は実装済み。','2. **CALIBRATION_CANDIDATE**：15–64歳細分就業率、年齢・性別時間重みは隔離候補。外国人別時間、高齢層の同時点細分率、年平均／10月時点の人口橋渡しが残る。','3. **STRUCTURAL_MODEL_CHOICE**：週→年換算、FTE表示基準、時間ベースにも同じ0.65を使う構造、Aと資本の扱いは条件付き。全国統計を取得したことだけで経済的妥当性を承認しない。','4. **POLICY_SPEC_REQUIRED**：Fの政策追加労働を時間・技能・健康へ完全に分ける際の単位契約が必要。現在の有効労働追加を時間で再重複調整しない。','5. **NOT_IDENTIFIABLE**：将来就業率改善、生産性上昇、TFP、資本サービス／資本代替、外国人固有の限界生産性は未推定。欠測を0で埋めない。','',
 '次の実務は、月次・年齢性別の人口／就業者を同一時点へそろえ、65歳以上の細分就業率と年齢性別の年間時間を取得して、既存コホートへの接続を検証すること。変更枝を採用するならSQ・N3の基底参照も整合して再構築する。今回、不要な新レビュー・承認ゲートは設けない。詳細は`Labor_Statistics_Calibration_Gaps_And_Next_Fixes.csv`。','',
 '## 検証・再現・引渡し','',
 f"新規ブリッジ検証{q['new_bridge_checks']}項目、不一致0。N3再実行の既存実行時検証{q['N3_existing_runtime_checks']}項目、不一致0を別掲（合計{q['checks_total']}）。10経路300年次。原典14件の復号SHA・サイズ、411抽出セルを入力とし、固定SQ/F/N3再現、人口・就業セル、人数／時間／FTE単位、2026初期、L/L0、0.65、A不変、イベント・物価・医療参照、F追加労働の一回接続、GDP恒等式を検査した。Python {q['python']}、年次計算は標準ライブラリのみ。原典Excelの再抽出は{q['statistics_extraction']}を使用。",'',
 '既存3037件・Claude2845件は固定対象に限定して維持し、本新枝を独立検算済みとはしない。新規件数と再利用件数を混ぜない。','',
 '```bash','python Prepare_Statistics.py --out <packet>','python Labor_Bridge_Reproduce.py --root <fixed-ec98f975-checkout> --inputs <packet>/Statistics_Inputs.json --out <empty-output>','python Finalize_Labor_Bridge.py --out <output-with-Statistics_Inputs.json>','```','',
 '最初のコマンドは`Source_Originals`の実バイトからオフライン再抽出する。完全再生成ではその14入力原本を別出力先へコピー後に再抽出・年次実行・報告生成を行う。コピーした原本は再生成ファイル数に数えない。別出力先での再生成実バイト一致は`Reproduction_Verification.json`、指定ブランチ格納後の固定Commit事後取得SHA・サイズは`Custody_Verification.json`に記録。','',
 '既存SQ/F/N3原文・共通エンジン・固定成果・mainは変更しない。正式Acceptance・PR・merge・Canonical化・Freeze、Finding Close、DecisionLog更新、HOLD解除は行わない。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。']
 (out/NAME).write_text('\n'.join(l)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out.resolve())
