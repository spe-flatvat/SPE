"""Create readable findings from actual executed outputs; does not run engines or adopt candidates."""
import argparse,csv,json,hashlib,platform,subprocess
from pathlib import Path
from Reproduce_Timing_Bridge import js,read,save,dump
P='handoff/chatgpt-common-labor-national-statistics-connection-20261123'
NAME='SPE_Labor_Timing_65Plus_Annual_Hours_Connection_Report_DRAFT_20261123.md'
def run(root,out):
 q=js(out/'Verification.json');s=js(out/'Statistics_Inputs.json');rows=read(out/'SQ_Annual_Aligned_Labor_Hours_FTE_GDP_2026_2055.csv');coarse=read(out/'Older_Coarse_Fine_And_Existing_Rate_Comparison.csv');timing=read(out/'Population_Employment_Same_Time_Bridge.csv')
 gaps=[dict(classification=c,topic=t,executed=e,remaining=g,next_executable_fix=f,adopted=False) for c,t,e,g,f in [
 ('DATA_DEFINITION_ALIGNMENT','annual vs October timing','2025 matched LFS P/E plus12firstday archive and2026JanSep','firstday vs surveyweek and populationcoverage notexact','obtain samebenchmark monthly exposure definition before converting to a single series'),
 ('CALIBRATION_CANDIDATE','elder finerates','65-69/70-74/75-79/80-84/85+ eachsex observed counts','85+ profile shared over85-89...100+; foreignsameprofile','obtain nationality and finer85+ survey exposure before replacing conditional population basis'),
 ('DATA_DEFINITION_ALIGNMENT','population2025 censusrevision','latesttable122973thousand keptseparate;oldOct123219thousand archived','benchmark revision distinctfromtime;no LFS2025 rebenchmark applied','jointly rebenchmark LFS and population after comparable official revisions; donot overwrite model2026'),
 ('CALIBRATION_CANDIDATE','hours oldercohorts','weekly aggregate65-69/70-74/75+;monthmean65+;conditionalannualbranches run','age75-79/80-84/85+ hoursnotseparatelyobserved;monthly65+pooled','obtain age-sex matched monthly at-work knownhours denominators or official annual fine-age hours'),
 ('STRUCTURAL_MODEL_CHOICE','annual hours definition','weekly52 andmonthly12profiles explicitlydifferent;official sexannualmeans retained','no age-sex measured actualannual orcomplete allemployed total;monthly derivedfromweek/daycounts','use twelve monthly knownhours numerators and exposure denominators underofficialannual definition;keep missingunknownhoursN/A'),
 ('POLICY_SPEC_REQUIRED','F extra laborunit','6 matched Fcontrols;trajectory+elder+education+health+commonoffset identity','F policycohortshaveexistinghour-equivalents;notfullage-sexFTE','specify and rebuild extra-cohort age-sex/time units before full Fhours adoption'),
 ('STRUCTURAL_MODEL_CHOICE','N3changedbase','native replay30yrs;Runner.base/sq/medical/wage/fiscal readsinspected','changedbase ledgerchain notrebuilt;N3changedGDP N/A','rebuild underlying SQ and nativeN3 policybaseline traces plusmedicalinit,thencachedreferences,wage/tax/fiscal,thenrerun'),
 ('NOT_IDENTIFIABLE','future ratesproductivitycapital','all2025 rates/hours held;Aunchanged','2026OctDecunobserved;futureimprovement/TFP/capitalnotestimated','useonlypublishedspecifiedseries;nointerpolationofunpublishedmonths')]]
 dump(out/'Remaining_Statistics_Gaps_And_Next_Executable_Fixes.csv',gaps)
 deps=[]
 for path,terms in [('handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123/Resolved_Separation_Runtime.py.txt',['self.base','self.sq','wage0=','medical']),('handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123/Three_Scenario_Worker.py',['def n3','Medical_Initialization','medical_defs','medical_pop']),('handoff/chatgpt-n3-assumptions-specification-calibration-separation-20261123/Sensitivity_Runtime.py',['medical_input','def build'])]:
  b=(root/path).read_bytes();deps.append(dict(path=path,commit='8a117759906f0d89c8a57e0899c03e3697be70a1',size=len(b),sha256=hashlib.sha256(b).hexdigest(),read_sites=[dict(line=i,text=l) for i,l in enumerate(b.decode().splitlines(),1) if any(t in l for t in terms)]))
 save(out/'N3_Shared_Base_Dependency_Read_Sites.json',dict(status='READ_ONLY_DEPENDENCY_ANALYSIS',changed_branch_executed=False,reason='Existing adapters expose common L shift for F, not coherent N3 baseline ledger/cache rebuild. No SQ GDP delta added to N3.',files=deps))
 labels={'BASE_SQ_UNCHANGED':'現行SQ','PREVIOUS_FINE_AGE_HOURS':'前回細分率＋時間','ANNUAL_SAME_SURVEY_UNDER65':'15–64歳同調査率','OLDER_FINE_RATES_ONLY':'65歳以上細分率のみ','ANNUAL_ALIGNED_FULL_RATES':'年平均・全年齢細分率','OCTOBER_NEAR_FULL_RATES':'10月近接時点・細分率','ANNUAL_FINE_WEEK_HOURS':'年平均細分率＋細分週時間×52','ANNUAL_MONTH_HOURS_PROFILE':'年平均細分率＋月平均時間×12','UNIFORM_LEVEL_CONTROL':'全国一様倍率の中立対照'}
 lines=['# SPE｜人口・就業者の統計時点統一／65歳以上細分就業率・年間労働時間の限定接続','',
 '**2026-11-23 / DRAFT / NON-CANONICAL / ISOLATED EXECUTED CANDIDATES**','',
 '## 実成果・前回から進んだ点','',
 '同じ2025年年次原表の人口・就業者から、65–69／70–74／75–79／80–84／85歳以上×男女別の就業率を計算し、同じ原表構造の2025年10月値と比較した。2025年の12か月について2020年国勢調査基準の人口推計確定値を当時の原本から回収し、各月1日平均と10月1日を区別して、労働力調査の年平均・10月調査週へ対応づけた。2026年は取得版に載る1–9月だけを観測列に残し、10–12月を埋めていない。',
 '前回の65歳以上一括時間から、65–69／70–74／75歳以上の男女別延週間時間へ細分できた。年間時間は週×52と月平均×12を異なる条件付き系列として実行した。実測年間時間の年齢細分や、欠測者・外国人固有の時間を取得したとはしない。',
 f"SQ{q['SQ_paths']}枝・F{q['F_paths']}対照・N3現行{q['N3_replay_paths']}枝、計16経路・{q['annual_rows']}年次を実コードで実行。現行SQ・前回時間枝・既存F・N3再現を保持した。統計表の列挙だけで終了していない。",'',
 '## 固定原本・統計原典','',
 '依頼固定Commitは`8a117759906f0d89c8a57e0899c03e3697be70a1`、前回接続成果は`78858034a8659fb21d01421168de6be0173ff0c5`。前回107個別原本（データ106＋事後照合記録）を実バイト照合。人口労働診断`9dcf953e949593e773bab906eb72577f0efec73e`、3施策比較`e981c924adbe9c7ca77b96d2dc94e40378186613`、Claude検算`3611534d85fb52c976592c96120f7663dbfa63f5`の固定原本を再利用。Claudeの2845項目は今回の新枝には適用しない。',
 f"今回の新取得28原本はExcel11件・人口月報PDF12件・公式メタデータHTML5件。Excel{q['statistics_cells']}数値セル、人口推計756行（21年齢区分×男女計/男/女×12か月）、LFS月次441行を抽出した。原本は個別JSONのbase64に実バイトを保存し、復号SHA-256とサイズを検証。Excelの内部形式とは別に、配布用ZIPは生成していない。",'',
 '|原典|取得版・時点|接続|','|---|---|---|',
 '|[LFS2025年次I-2](https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid=000040403919)|2026-01-30公表、2025年平均、万人、季調なし|同一版の15歳以上人口／就業者、男女別、85歳以上まで|',
 '|[LFS2025年10月I-2](https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid=000040373820)|2025-11-28公表、2025年10月、万人、季調なし|同月P/E。人口推計10月1日とは近接時点proxy|',
 '|[LFS年次II-9](https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid=000040403936)|2025年平均、2026-01-30、全産業・万人／万時間|男女別65–69／70–74／75歳以上の延週間時間|',
 '|[LFS年次II-4](https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid=000040403931)|同年・同公表日、月間就業時間・従業者・不詳|15–64歳5歳階級、65歳以上一括の月平均時間|',
 '|[LFS年次II-11-4](https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid=000040403941)|同年、男女別全産業の平均年間時間|年齢別ではない。全就業者人数へ無条件に乗じない|',
 '|[LFS長期月次人口](https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid=000031831366)／[就業者](https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid=000031831359)|2026-10-30取得版、原数値、2025年12月まで・2026年9月まで|年平均と10月差、未公表月を分離|',
 '|[人口推計過去月報](https://www.stat.go.jp/data/jinsui/8.html)|2025年6月報〜2026年5月報の各5か月前確定値、2020年国勢調査基準|2025年1〜12月1日、千人、男女・5歳階級|',
 '|[2025年10月人口・新改定版](https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid=000040526742)|2026-11-20公開、2025年国勢調査基準|別記のみ。既定人口・LFS基準へ混入せず|','',
 '当初、人口表をExcel通常リンクfileKind=0で取得すると404となった。公式詳細ページの実際のリンクfileKind=4へ切り替えて取得成功。全体STOPや同条件の反復は行っていない。各原典の公表日、単位、対象月・年、人口基準、セルとSHA・サイズはソースCSVと抽出セル／PDF原行へ保存した。', '',
 '## 時点・母集団の接続と残差','',
 '「同定義接続可」はLFS内の同年・同月・同男女年齢セルのPとEに限定する。人口推計は月1日、LFSは調査月末の調査週（12月は調査日程が異なる）であり、12か月の月初平均とLFS年平均は厳密な同一時点・同母集団ではない。対象者の除外、推計、丸め、時点の違いは未分離残差に残す。2025年10月I-2と人口推計10月1日は「近接月proxy」であり、Eを別人口で割って全国率を作る処理は実行しない。',
 '人口推計の2025年10月旧基準総人口123,219千人に対し、2025年国勢調査改定版は122,973千人（差−246千人）。この改定差を10月→年平均の時点差に含めない。モデルの2026年条件付き人口122,618,024人、移民・年齢性別国籍別セルの推移は変更しない。2025年観測率をこの将来人口へ適用する段階は、同一時点の実測人口への全面較正ではなく、2025年固定率による条件付き橋渡しである。','',
 '全国就業者差248,347.175人の新たな会計分解（政策効果・原因の因果推定ではない）：','',
 '|項目|人|','|---|---:|']
 for k,v in q['benchmark_gap'].items():lines.append(f'|{k}|{v:,.3f}|')
 lines+=['',
 '人口基準差、月初平均↔10月の時点proxy差、LFSとの人口・対象差、細分率定義差を順番に分けた。元のIPSS人口と当時の人口推計との差を純粋な「人口推計誤差」とも、LFSとの残差を純粋な「対象者除外」とも断定しない。丸め残差がこの全国男女・最細分合計で0なのは取得表の結果であり、0へ強制調整していない。高齢者粗区分と細分の個別差は別CSVに残した。','',
 '## 65歳以上・時間・単位','',
 '|年齢|男の年平均E/P|女の年平均E/P|','|---|---:|---:|']
 for a in [65,70,75,80,85]:
  v={r['sex']:r['rate'] for r in s['rates'] if r['period']=='ANNUAL_2025' and r['age_lower']==a};lines.append('|'+(f'{a}–{a+4}歳' if a<85 else '85歳以上')+f"|{100*v['male']:.6f}%|{100*v['female']:.6f}%|")
 lines+=['',
 '85歳以上は85–89、90–94等へ同じ観測集計係数を条件付き適用し、それ以上の細分率を発明しない。75歳以上の旧一括率との差は、その内部年齢構成が変わる将来に効く。丸められた公表率と公表人数E/Pの違いは、既存率を不正な値と断定せず比較表へ記録した。',
 '週間時間は同じII-9表の延週間時間／就業者数を使い、65–69／70–74／75歳以上を区別する。75–79／80–84／85歳以上の時間自体は取得できていないため75歳以上の集計係数を共用する。休業者の調査週時間0は公式定義。不詳者の時間は推定・0埋めせず、公表延時間の対象範囲を引き継ぐ。年換算52倍はCONDITIONAL_ANNUALIZED_PROXYであり、年間実測値ではない。',
 '月平均時間は公式定義でも「週間時間÷月末週の就業日数×月間就業日数」による推計を含む。年平均II-4の公表月平均×12を別の条件付き年換算プロファイルにした。公表平均の従業者・不詳除外の分母をモデルの全就業人数へ移す仮定を明記し、欠測者や休業者の実労働時間を補完したものとはしない。65歳以上は男女別一括係数で、細分時間の実測と扱わない。この枝は週時間枝とは対象・集計方法が異なる感度対照で、両枝の差を純粋な年間時間の改善効果とは断定しない。',
 '公式の全産業平均年間時間（男女計1788.3、男1985.3、女1551.2時間）は取得したが、これは産業・職業別表で年齢別ではなく、既知の月間時間を持つ従業者の平均を用いる公式推計である。SNAの仕事ベース時間や全就業者1人当たり年間実測時間とは別で、これらを年齢・国籍へ無根拠に配分しない。年齢別の実測年間総時間列はN/Aのままである。',
 '診断FTEはH/2080（40×52の表示基準）。公式FTEではない。有効労働への接続はL0_current×physical_L_t/physical_L_2026、初期実質580／名目600を維持。L、人数、時間、FTE、A、GDPを別列で保存。A・基調成長1%・労働弾性0.65・29遷移・イベント・価格・医療参照は保持。SNA GDP/時間やTFP・資本代替をGDPへ再乗算しない。外国人には同じ年齢・性別率／時間を条件付き適用し、外国人固有の実測値とは記さない。','',
 '## 年次実行結果','',
 '|2055年SQ枝|就業人数（万人）|時間proxy（億時間）|診断FTE（万人）|実質GDP（兆円）|現行差|前回時間枝差|','|---|---:|---:|---:|---:|---:|---:|']
 for r in q['key2055']:
  hours='N/A' if r['total_hours_conditional'] is None else f"{r['total_hours_conditional']/1e8:.3f}";fte='N/A' if r['FTE_diagnostic'] is None else f"{r['FTE_diagnostic']/1e4:.3f}"
  lines.append(f"|{labels[r['case']]}|{r['employed']/1e4:.3f}|{hours}|{fte}|{r['real_GDP_trn']:.6f}|{r['GDP_minus_current_SQ_trn']:+.6f}|{r['GDP_minus_previous_hours_trn']:+.6f}|")
 lines+=['',
 '全国一様倍率はL/L0で相殺し、GDPは浮動小数点誤差内で現行SQと同じ。時間の絶対水準を変えるだけでも正規化で相殺するため、今回の差は率・年齢構成・時間構成の経路差である。年平均率と10月率の差には季節性・標本・時点が含まれ、10月率を将来の就業率改善とはしない。',
 '15–64歳率変更・高齢細分率変更の2×2会計分解には相互作用を開示した。時間の追加差は全年齢率枝からの逐次差として別記し、月時間と週時間の代替枝を足さない。前回の5要因Shapleyへ異なる条件の差を直接加算しない。全30年は年次CSV、2026/2030/2035/2039/2055はKey_Years.csv。','',
 '## F同条件対照・N3境界','',
 '|F対照（2055）|F実質GDP|対応SQ|F−SQ|','|---|---:|---:|---:|']
 for r in q['F2055']:
  if r['case'].startswith('F_'):lines.append(f"|{r['case']}|{r['real_GDP_trn']:.6f}|{r['matched_SQ_GDP_trn']:.6f}|{r['F_minus_matched_SQ_trn']:.6f}|")
 lines+=['',
 'Fは共通基底のL変更差のみを一度加える最小対照。既存trajectoryの高齢就業・外国人・年金の時間換算と、追加高齢就労・教育・医療健康を重複加算しない実行時恒等式を検査した。ただし政策対象コホート全体を年齢性別時間へ組み直した完全FTEモデルではない。既に時間換算された有効労働へさらに時間を掛けていない。',
 'N3現行を30年再実行し、2055年483.991492兆円へ一致。追加政府G/IはOFF。変更枝は未構築・最終GDP=N/A。Runner.base/sqには旧基底の政策・税・医療状態がキャッシュされ、賃金初期値・価格・前年GDPに依存する税・年金／財政参照もある。今回のF共通L差用adapterだけではN3の整合した全基底再構築にならないため、SQ GDP差の単純加算やキャッシュ一部の差し替えを実行しなかった。必要な最小接続は、変更SQとネイティブN3の基底traceを再生成し、医療初期化とbase/sq、給与・税・財政の参照チェーンを一緒に更新する隔離adapterである。読取箇所・行・固定SHAはN3依存分析JSONへ記録。この未計算を計算済みとしない。','',
 '## 検証・再生成・引渡し','',
 f"新規実行で{q['new_checks']}件の入力・統計定義・年次会計・基準年・再現・単位・F重複防止検証、不一致0。N3既存実行時{q['N3_existing_checks']}件、不一致0は別掲。先行4763件・Claude2845件を今回の新規件数へ加えていない。件数は独立した統計的妥当性や因果識別の保証ではない。",'',
 '再現環境はPython '+platform.python_version()+'、年次計算は標準ライブラリ、Excel再抽出はopenpyxl3.1.5、PDF原行再抽出はpdftotext。取得通信なしで以下を実行できる。固定依存原本を含む依頼Commitのcheckoutと、今回の個別成果が必要。','',
 '```bash','python Prepare_Timing_Statistics.py --root <request-fixed-root> --out <packet-with-Source_Originals>','python Reproduce_Timing_Bridge.py --root <request-fixed-root> --inputs <packet>/Statistics_Inputs.json --out <new-output>','python Finalize_Timing_Packet.py --root <request-fixed-root> --out <new-output-with-statistics-inputs>','```','',
 '完全再生成時はSource_Originalsの28原本を別出力先へ個別コピーして再抽出する。再生成一致の対象・件数・SHAはReproduction_Verification.json、指定work/chatgpt-handoff格納後の固定Commit事後取得・実バイトSHA／サイズ照合はCustody_Verification.jsonへ記録する。前回固定107原本と新規成果の検証を分けた。空欄はN/Aであり欠測0ではない。',
 '政策原文・共通エンジン・既存固定成果・mainは変更しない。正式Acceptance、PR、merge、Canonical化、Freeze、Finding Close、DecisionLog更新、HOLD解除は行わない。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。',
 '本依頼の実装・実行・比較・個別引渡しは実施し、統計時点の厳密同一化、年齢別実測年間時間、外国人固有率／時間、変更N3の整合基底再構築は未達として明記する。']
 (out/NAME).write_text('\n'.join(lines)+'\n')
 save(out/'Acquisition_Route_Notes.json',dict(failed_route='population2025 statInfId000040526742 fileKind0 HTTP404',successful_alternative='officialmetadata href fileKind4;binaryxlsx decoded',monthly_unavailable_2026=[10,11,12],official_annual_hours_age_detail='not in obtained industry-occupation table',prior_definitions_reused={'commit':'78858034a8659fb21d01421168de6be0173ff0c5','files':['Source_Originals/yougo_kaisetsu.pdf.json','Source_Originals/note01-j.pdf.json']},no_missing_future_improvements_inserted=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.out.resolve())
