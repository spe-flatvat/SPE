"""Generate a self-contained F report from existing results; NEVER rerun the engine.
Usage: python3 SPE_F_Visual_Report_Builder_20261110.py INPUT_DIR OUTPUT_DIR
INPUT_DIR: the six files at SPE commit 30530ad2b012ce33715db662fa0c5ca06a2f10ed,
          handoff/f-provisional-20261110/ . Standard Python library only.
CSV numeric values are read as supplied; differences/formatting are presentation arithmetic.
"""
import csv,hashlib,html,json,sys
from pathlib import Path
COMMIT='30530ad2b012ce33715db662fa0c5ca06a2f10ed'
ENGINE='4389951293b5ff91bbfec58a613b30458e1fb544'
BASE='handoff/f-provisional-20261110/'
NAMES=['SPE_F_Provisional_Execution_Report_DRAFT_20261110.md','SPE_F_Provisional_Inputs_DRAFT_20261110.json','SPE_F_Annual_Inputs_Expanded_DRAFT_20261110.csv','SPE_F_Annual_Results_DRAFT_20261110.csv','SPE_F_Historical_Comparison_DRAFT_20261110.csv','SPE_F_Provisional_Run_20261110.py']
CASES=['F_2026_INITIAL_29','F_2026_TRANSITION_30']
RISK_NAMES=['石油ショック','中台紛争','南海トラフ地震','中規模災害','気候変動ドラッグ']
GROUPS=[
 ('消費・投資・教育','計算反映済み（外生係数）',['consumption_stimulus_effect','investment_promotion_effect','education_effect'],'policy_effects_pct','transition_year → calculate_real_gdp_growth_rate'),
 ('純移民','暫定仮定（線形刻み）',['net_migration'],'migration','transition_year_demographics → transition_population'),
 ('人口動態・賃金','暫定仮定を含む',['death_rate_coefficient','birth_decline_coefficient','phi','real_wage_growth_rate'],'death_rate_coefficient / birth_decline_coefficient / phi / wage_anchor_man_yen','M14賃金入力補間 → transition_births/deaths'),
 ('労働項・基調成長','暫定仮定を含む',['aging_drag','alpha','base_growth_rate'],'aging_drag_pp / alpha / base_growth_rate_pct','人口成長率 + aging_drag → (1−alpha)倍'),
 ('税収','計算反映済み／切替境界は暫定',['tax_elasticity','tax_event_factor','tax_cap_ratio'],'tax_elasticity / tax_factor_by_year / tax_cap_ratio_of_nominal_gdp','calculate_tax_revenue_before_cap → 係数補正 → cap'),
 ('歳出','計算反映済み（外生系列）',['expenditure_growth'],'expenditure_growth_pct','adapter: previous.expenditure × (1+expenditure_growth)'),
 ('インフレ','計算反映済み／VAT要因0は暫定',['base_inflation_rate','risk_event_inflation_impact','consumption_tax_transitional_factor'],'base_inflation_rate_pct / inflation_extra_pp','calculate_inflation_rate → nominal_growth')]
POLICIES=[
 {'policy':'消費税5%フラット化・広基化・食料品0→8→5%','text':'本体§4・5','status':'未実装（制度別）','actual':'税率・課税ベース・価格転嫁を直接計算しない。消費刺激係数0.3→0.5→0.7ppは計算済みだが、税率改革による効果の実証値ではない。'},
 {'policy':'法人税・ハイパー償却・企業統治','text':'本体§4','status':'暫定係数・代理変数で反映','actual':'投資促進0.3→0.5ppのみ。法人税率・償却・投資額・企業行動は未実装。'},
 {'policy':'社会保険料軽減・現物給付・中間層還元','text':'本体§4・7','status':'未実装','actual':'所得階層別の保険料・給付・手取りを計算しない。歳出率を各制度の効果と同一視しない。'},
 {'policy':'医療改革・緩和ケア・高額療養費','text':'本体§4／別紙§4','status':'未実装','actual':'受療・費用・医療給付・終末医療の制度モデルなし。死亡係数1.015は政策の医療効果ではない。'},
 {'policy':'在職老齢年金・私的年金税制優遇','text':'本体§4','status':'未実装','actual':'受給者・給付・保険料・就業行動の制度計算なし。'},
 {'policy':'教育国債・給付奨学金・教育訓練','text':'本体§4','status':'暫定係数・代理変数で反映','actual':'2028年以降の教育効果+0.3ppのみ。事業費・財源・人的資本の蓄積や教育国債を個別に計算しない。'},
 {'policy':'外国人材パッケージ','text':'本体§4／別紙§5','status':'計算反映済み（純移民のみ）＋暫定仮定','actual':'2030年8万人から年8万人ずつ増加、2034年40万人、2035年以降40万人/年。2030〜34年の刻みは仮定。選別・GDP比上限・支援費・年齢構成は未実装。'},
 {'policy':'高齢者就業促進','text':'本体§4','status':'未実装（制度別）','actual':'aging_dragという集計的労働項はあるが、就業促進制度の人数・効果を識別する計算ではない。'},
 {'policy':'2035年の成長・Gini・人口トリガー','text':'本体§7','status':'未実装','actual':'閾値監視・Decision・教育拡大・保険料軽減・移民上限+20%を実行していない。2035年に予定通り外生歳出率が変わることとは別。'},
 {'policy':'損税解消・追加資金・返済','text':'本体§4／v5§4-2政治調整版','status':'未実装','actual':'課税ベース・損税・追加国債120兆円の配分や返済は未実装。資金不足proxyを実際の国債発行と呼ばない。'}]
LABELS={'consumption_stimulus_effect':'消費刺激','investment_promotion_effect':'投資促進','education_effect':'教育','net_migration':'純移民','death_rate_coefficient':'死亡倍率','birth_decline_coefficient':'出生減少倍率','phi':'出生・賃金弾性φ','real_wage_growth_rate':'賃金入力成長率','aging_drag':'aging drag','alpha':'資本分配率α','base_growth_rate':'基調成長','tax_elasticity':'税収弾性','tax_event_factor':'税収イベント倍率','tax_cap_ratio':'税収上限/GDP','expenditure_growth':'歳出成長率','base_inflation_rate':'基調インフレ','risk_event_inflation_impact':'リスク追加インフレ','consumption_tax_transitional_factor':'VAT一時インフレ','risk_shock':'合算リスク'}
PCT={'consumption_stimulus_effect','investment_promotion_effect','education_effect','real_wage_growth_rate','aging_drag','base_growth_rate','expenditure_growth','base_inflation_rate','risk_event_inflation_impact','consumption_tax_transitional_factor','risk_shock','tax_cap_ratio'}
def fmt(k,v):
 if k=='net_migration':return f'{v:,.0f}人/年'
 if k in PCT:return f'{v*100:.6g}'+('%' if k in ['real_wage_growth_rate','expenditure_growth','tax_cap_ratio'] else 'pp')
 return f'{v:.8g}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 src,out=map(Path,sys.argv[1:3]);out.mkdir(exist_ok=True)
 # The code file is read for source traceability, never imported or executed.
 originals={n:(src/n).read_bytes() for n in NAMES}
 code=originals[NAMES[5]].decode('utf-8'); assert 'transition_year(prev,**args)' in code
 cfg=json.loads(originals[NAMES[1]])
 annual={int(r['year']):{k:float(v) for k,v in r.items() if k!='year'} for r in csv.DictReader(originals[NAMES[2]].decode('utf-8').splitlines())}
 results={case:[] for case in CASES}
 for r in csv.DictReader(originals[NAMES[3]].decode('utf-8').splitlines()):
  row={k:(v if k in ['case','row_kind'] else (None if v=='' else float(v))) for k,v in r.items()};row['year']=int(row['year']);results[r['case']].append(row)
 history=list(csv.DictReader(originals[NAMES[4]].decode('utf-8').splitlines()))
 assert len(history)==275
 registry={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'path':BASE+n} for n,b in originals.items()}
 events=[]; years=[]
 def event(y,name,value,status,source,columns,formula,changed):
  rec={'scenario':'F','year':y,'event_name':name,'input_value':value,'reflection_status':status,'initial_case_application':'初期状態のみ・当年遷移なし' if y==2026 else '当年遷移へ適用','legacy_case_application':'当年遷移へ適用','condition_change':changed,'source':source,'csv_columns':columns,'calculation_item':formula};events.append(rec);return rec
 for y,params in annual.items():
  ev=[]; risks=[]
  for name,rule in zip(RISK_NAMES,cfg['risk_shock_pct']['rules']):
   active=rule['type']=='once' and y==rule['year'] or rule['type']=='every' and y>=rule['start'] and (y-rule['start'])%rule['step']==0
   if active:
    risks.append({'name':name,'pct':rule['pct']});ev.append(event(y,name,f"実質成長から−{rule['pct']}pp",'計算反映済み','JSON:risk_shock_pct.rules','risk_shock','calculate_real_gdp_growth_rate: −risk_shock','当年発生'))
  if not risks:ev.append(event(y,'リスクイベントなし','risk_shock=0','計算反映済み','JSON:risk_shock_pct.rules','risk_shock','実質GDP成長率','発生なし'))
  for name,status,keys,jkey,formula in GROUPS:
   changes=[k for k in keys if y==2026 or params[k]!=annual[y-1][k]]
   value=' / '.join(LABELS[k]+'='+fmt(k,params[k]) for k in keys)
   change='初期設定' if y==2026 else ('変更: '+', '.join(LABELS[k] for k in changes) if changes else '前年から条件変更なし')
   ev.append(event(y,name,value,status,'JSON:'+jkey,';'.join(keys),formula,change))
  changes=[LABELS[k]+' '+fmt(k,v) for k,v in params.items() if k!='risk_shock' and (y==2026 or v!=annual[y-1][k])]
  years.append({'year':y,'params':params,'risks':risks,'changes':changes,'condition_change_text':'初期設定' if y==2026 else (' / '.join(changes) if changes else '前年から係数・受入人数の変更なし'),'event_rows':ev})
 for y,name,desc,ref in [(2026,'税制・企業統治改革（政策本文の予定）','2026〜28年の制度予定。税率・償却・統治の個別計算は未実装','policies/FreedomPolicies.md §4/5'),(2028,'医療・年金改革（政策本文の予定）','2028〜32年の予定。制度別費用・給付は未実装','policies/FreedomPolicies.md §4/5'),(2035,'消費税5%化・中間評価トリガー','本文の予定／条件。税率直結・Gini監視・自動変更は未実装','policies/FreedomPolicies.md §5/7')]:
  event(y,name,desc,'未実装・未算出',f'{ENGINE}:{ref}','なし','制度別モデルなし','本文の予定。計算への反映なし')
 with (out/'SPE_F_Event_Policy_Timeline_DRAFT_20261110.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(events[0]));w.writeheader();w.writerows(sorted(events,key=lambda r:r['year']))
 selected={case:{r['year']:r for r in vals} for case,vals in results.items()}
 def number(case,y,k):return selected[case][y][k]
 def mdf(v):return '—' if v is None else f'{v:,.4f}'
 md=f'''# F施策暫定計算：イベント年表と可視化解説

Status: DRAFT / EXISTING RESULTS VISUALIZATION / NON-CANONICAL  
日付: 2026-11-10（JST）  
既存成果物固定Commit: `{COMMIT}`  
エンジン・F本文参照固定Commit: `{ENGINE}`

## 読み方

このレポートは既存CSVの可視化であり、エンジンの再実行・数式変更・新しい政策条件の追加を行っていない。HTMLは外部通信・ライブラリ不要の単独ファイル。年・ケースを選ぶと、当年のイベント、全入力群、主要値と前年差、原入力列名を確認できる。グラフ上の点・縦線には年を付し、クリックで年を選択できる。

2026年初期状態ケースは2026の入力値を当年遷移へ適用せず、2027〜2055年の29遷移。過去互換ケースは初期値を2025末へ仮置きし、2026の石油ショックも含めた30遷移。2026の入力が年次入力CSVに存在することと、初期状態ケースで適用されたことは同じではない。2026の前年比成長率は初期状態ケースで未算出（空欄）。CSVにある0でない値を補間して埋めていない。

両ケースは同じ政策・係数系列だが境界が異なる。差をFの政策効果、実証的な因果効果と解釈しない。

## 計算概要と2055年

|指標|2026初期状態・29遷移|2026遷移・30期間|
|---|---:|---:|
'''
 for label,k,scale in [('実質GDP（兆円）','real_gdp',1),('名目GDP（兆円）','nominal_gdp',1),('税収（兆円）','tax_revenue',1),('歳出（兆円）','expenditure',1),('資金不足proxy（兆円）','funding_gap_proxy',1),('人口（万人）','population',1e4),('出生（万人/年）','births',1e4),('死亡（万人/年）','deaths',1e4),('賃金アンカー入力（万円）','real_wage_anchor_man_yen',1)]:
  md+=f'|{label}|{number(CASES[0],2055,k)/scale:,.4f}|{number(CASES[1],2055,k)/scale:,.4f}|\n'
 md+='''
2026初期値は実質GDP580兆円、名目600兆円、税収80兆円、歳出108兆円、人口1億2150万人。資金不足proxyはmax(歳出−税収,0)であり、国債総発行・債務残高・利払い・償還・PBではない。賃金400→860万円は入力アンカーの幾何補間であり、内生的賃金予測ではない。

既存v6 prototypeの人口・成長率・税収関数とM14補間を、ローカルadapterから呼び出した既存結果を参照した。税率→税収基盤や社会保障制度は実装されていない。前年差・比率・万人換算は表示用の算術であり、新しいシミュレーションではない。

## 状態ラベル

- **計算反映済み**：入力列にあり、該当年の遷移で利用された条件。2026初期状態行は適用除外。
- **暫定仮定**：計算には反映したが、政策上の確定値や実証係数とは扱えない条件。線形移民刻み、賃金中間年、弾性切替の境界、α/φ、VATインフレ0等。計算反映済みと仮定の有無は別軸。
- **未実装・未算出**：本文に記載があっても、当該制度・効果をこの計算へ接続していないもの。

## 全年イベント・政策条件年表

係数はpp（成長率への加減算）。税収弾性は倍率、歳出成長率は%。移民は人/年。全行で死亡倍率1.015、出生減少倍率0.975、φ=0.15、α=0.35、基調成長1pp、基調インフレ2pp、税収上限30%、VAT一時インフレ0。定数も年表CSV・HTMLの年別詳細に掲載する。

|年|リスク（全件）／合算|消費/投資/教育 pp|移民 人/年|aging drag pp|弾性/歳出%|追加インフレpp／税収補正|その他変更|
|---|---|---|---:|---:|---|---|---|
'''
 for yy in years:
  y=yy['year'];v=yy['params'];rs='＋'.join(f"{r['name']} {r['pct']:g}" for r in yy['risks']) or 'なし'
  misc=yy['condition_change_text'];md+=f"|{y}|{rs}／{v['risk_shock']*100:g}|{v['consumption_stimulus_effect']*100:g}/{v['investment_promotion_effect']*100:g}/{v['education_effect']*100:g}|{v['net_migration']:,.0f}|{v['aging_drag']*100:g}|{v['tax_elasticity']:g}/{v['expenditure_growth']*100:g}|{v['risk_event_inflation_impact']*100:g}／×{v['tax_event_factor']:g}|{misc}|\n"
 md+='''
2026の全条件は過去互換ケースの遷移には適用、2026初期状態ケースには不適用。2026の出生・死亡は初期値の年間件数であり、今回関数が再計算した値ではない。条件変更なしの年にも、前年状態の継承と出生・死亡等の累積計算は進む。定期リスクの再発と係数変更は別に表示している。

## 施策本文と今回実装の対応

本文は`policies/FreedomPolicies.md`、別紙は`policies/FreedomPolicies_Annex.md`を、エンジン固定Commit438995…で参照した。次は文書の制度一覧を実装済みと誤認しないための対応表であり、追加政策の計算ではない。

|政策・制度|本文位置|区分|今回の計算内容・限界|
|---|---|---|---|
'''
 for r in POLICIES:md+=f"|{r['policy']}|{r['text']}|{r['status']}|{r['actual']}|\n"
 md+='''
## 入力列・キー・式の対応

|項目|入力JSONキー|年次入力CSV列|計算への接続|
|---|---|---|---|
|リスク|risk_shock_pct.rules|risk_shock|prototype.calculate_real_gdp_growth_rate の減算。複数リスクは加算して入力|
'''
 for name,status,keys,jkey,formula in GROUPS:md+=f"|{name}|{jkey}|{', '.join(keys)}|{formula}|\n"
 md+='''
人口成長率＝当年人口/前年人口−1。実質GDP成長率＝基調＋消費＋投資＋教育−risk＋(1−α)×(人口成長率＋aging_drag)。名目成長率＝実質成長率＋基調インフレ＋追加インフレ＋VAT一時要因（今回は0）。税収＝前年税収×(1＋名目成長率×弾性)をイベント補正し名目GDP30%でcap。歳出は前年×(1＋外生歳出率)。

## 変曲点：入力と既存出力の対応

次の数値は既存結果CSVから読んだもので、反実仮想を新たに実行した因果推定ではない。制度名とモデル上の外生効果を区別する。

|年|当年の入力・イベント|初期状態ケースの実質GDP成長率|前年との差 pp|コード上確認できること・限界|
|---|---|---:|---:|---|
'''
 explanations={2027:'中台5pp＋気候0.5pp。消費0.3・投資0.3、追加インフレ5pp。2026は初期なので成長前年差なし。実質への減算と名目へのインフレ加算が別経路。',2028:'消費0.5ppへ、教育0.3pp開始、前年の中台ショックなし。前年のリスク消失と効果増加が重なる。',2031:'南海3pp＋気候0.5pp、税収×0.9。GDPの減算と税収への直接補正が二重の別経路。',2033:'aging drag −0.0525→−0.8123pp、弾性1.5→1.7、気候0.5pp。弾性は税収経路、agingは実質成長経路。',2035:'歳出率2.5→1.5%、移民定常期、気候0.5pp。本文の自動トリガーは未実装。',2041:'弾性1.7→2.0、中規模災害1pp＋気候0.5pp。税収とGDPの経路が異なる。',2043:'気候0.5pp。資金不足proxyは初めて0。制度的な国債償還・PB達成ではない。',2044:'aging drag −0.8123→−0.3737pp、リスクなし。成長率へ正方向の式上寄与。',2045:'歳出率1.5→1%、気候0.5pp。成長差と歳出の鈍化を分離して読む。',2046:'aging drag −0.3737→−0.1683pp、リスクなし。人口・出生・死亡の累積も継続。'}
 for y,ex in explanations.items():
  g=number(CASES[0],y,'real_growth_pct');prev=number(CASES[0],y-1,'real_growth_pct');delta=None if prev is None else g-prev
  md+=f'|{y}|{ex}|{mdf(g)}|{mdf(delta)}|上記関数接続による条件付きモデル挙動。政策の実証的な因果効果・寄与額は未推定。|\n'
 md+='''
## グラフ構成と比較上の注意

HTMLには①実質GDP、②名目GDP、③実質成長率、④人口、⑤出生/死亡、⑥純移民入力、⑦税収/歳出/資金不足proxy、⑧税収比率/30%cap、⑨消費/投資/教育/リスク入力、⑩賃金アンカー入力、⑪人口関連係数の11パネルを収録した。金額・人数・率を別軸へ分離し、各パネルの単位を表示。実質/名目の成長と価格効果を混同しない。

実線＝2026初期状態、破線＝過去互換。入力系列は共通であり、入力パネルの2026値は初期状態ケースの計算結果ではない。グラフは年次点を結ぶ表示であり、中間年/月の値を新たに推計したものではない。2026成長率空欄は描画せず、0で埋めない。金額・人数の差分は単位付きで表示する。

過去コードとの一致は30期間ケースの30年×9指標、元出力の丸め精度内270/270。これは既存比較CSVを再利用した記録であり、新たなエンジン再実行はない。v5§8端点661.9兆円と今回661.5234056兆円には差があり、完全再現と称さない。旧F docx系列は版・指標・入力未照合のため数値比較に混ぜない。

主ケースでは2026石油ショックを再適用しないため、2ケースの2055年GDP差は政策差ではなく境界による差。賃金・移民・弾性境界等の仮定も維持。人口目標や所得分配の達成判定を新たに行わない。

## 表示・操作の確認範囲

JavaScript構文検査と、ブラウザを使用しない隔離DOMスタブでの年・ケース全60組の処理、11パネル・30年表、2031年の重複リスク、2026欠測、2055表示値、無効SVG座標なしを確認した。生成SVG11パネルはオフライン画像化してグラフ・文字・注記を目視確認した。これはHTML全体のブラウザ実画面確認ではない。Chromiumはsocket権限制限で起動できず、Cloud Browserはfile URLを許可しないため、実画面・モバイル配置・実際のクリック操作の確認は未検証。制限を迂回せず、既存計算結果のPASSは維持する。

## 他施策との共通化

CSVにscenario/year/event_name/input_value/reflection_status/source/csv_columns/calculation_item/適用ケースを持たせ、年・ケース選択、同一単位の系列、イベント一覧、未実装表を共通部品として再利用できる構成にした。F以外の係数・結果は今回追加していない。比較時は2026境界・イベント年・税収proxy・単位を揃える必要がある。

政策金利、配当、内部留保、労働者人口人数、非正規率、所得中央値、エンゲル係数、ジニの内生変化、実際の債務・償還・PBはこのデータでは評価できない。

## 再生成方法

```bash
python3 SPE_F_Visual_Report_Builder_20261110.py INPUT_DIR OUTPUT_DIR
```

INPUT_DIRに固定Commitの6成果物を置く。再生成コードは既存結果・入力を読み取ってHTML/Markdown/CSVだけを生成し、エンジン・旧計算コードをimport/実行しない。Python標準ライブラリのみ、HTMLは外部スクリプト/画像/フォント取得なし。GitHub上のHTML表示はソース表示となるため、ファイルをHTMLとして開くと年次選択・グラフを利用できる。

既存6原本は未変更。正式Acceptance・Finding Close・DecisionLog更新・Freeze・Canonical化・HOLD解除なし。RP-023／M19–25 HOLD、RP-024 PENDINGを維持する。

## 入力証拠

既存の固定Commit再取得・原本一致PASSを再利用し、その保存済み原本バイトを今回の表示入力とした。元シミュレーションの再検証は行っていない。

|Path（固定Commit下）|bytes|SHA-256|
|---|---:|---|
'''
 for n,r in registry.items():md+=f"|{r['path']}|{r['bytes']}|`{r['sha256']}`|\n"
 md+=f'\nF本文参照：[本体](https://github.com/spe-flatvat/SPE/blob/{ENGINE}/policies/FreedomPolicies.md)、[別紙](https://github.com/spe-flatvat/SPE/blob/{ENGINE}/policies/FreedomPolicies_Annex.md)。\n'
 (out/'SPE_F_Visual_Explanation_DRAFT_20261110.md').write_text(md,encoding='utf-8')
 payload={'commit':COMMIT,'engine':ENGINE,'years':years,'results':results,'policies':POLICIES,'registry':registry,'labels':LABELS,'caseNames':{CASES[0]:'2026初期状態｜29遷移',CASES[1]:'過去試算互換｜30遷移'},'unimplemented':explanations}
 data=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 page=PAGE.replace('DATA_PAYLOAD',data)
 (out/'SPE_F_Visual_Report_DRAFT_20261110.html').write_text(page,encoding='utf-8')
 print(json.dumps({'result_rows':sum(map(len,results.values())),'timeline_rows':len(events),'input_files':6,'simulation_executed':False,'outputs':[str(p) for p in out.iterdir() if p.suffix in ['.html','.md','.csv']]},ensure_ascii=False))

PAGE=r'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SPE · F施策 年次レポート</title>
<style>
:root{--ink:#173431;--muted:#60746d;--jade:#176c60;--orange:#c57b35;--blue:#326eac;--red:#bc5157;--purple:#8064a8;--paper:#f5f6f0;--line:#dbe3da}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.75 -apple-system,BlinkMacSystemFont,"Noto Sans CJK JP","Yu Gothic",sans-serif}a{color:var(--jade)}main{max-width:1340px;margin:auto;padding:40px 32px 64px}header{padding:15px 0 32px;border-bottom:1px solid var(--line)}.eyebrow{font-size:12px;letter-spacing:.16em;font-weight:700;color:var(--jade)}h1{font-size:42px;line-height:1.35;letter-spacing:-.035em;margin:12px 0}h2{font-size:23px;margin:0 0 12px}h3{font-size:16px;margin:0 0 5px}p{margin:8px 0}.muted,small{color:var(--muted)}.lede{max-width:900px}.badge{font-size:11px;background:#e8eee4;padding:5px 9px;border-radius:20px;display:inline-block}.badge.warn{background:#f5e8d6;color:#805522}.hero-cards{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:24px 0}.hero-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px 24px;border-top:3px solid var(--jade)}.hero-card.legacy{border-top-color:var(--orange)}.big{font-size:36px;font-weight:650;letter-spacing:-.04em}.unit{font-size:14px;margin-left:6px}.nav{display:flex;gap:20px;flex-wrap:wrap;margin:18px 0;font-size:13px}.controls{position:sticky;top:0;z-index:10;background:#f5f6f0f5;border-bottom:1px solid var(--line);padding:14px 0;display:flex;gap:16px;align-items:center;flex-wrap:wrap;backdrop-filter:blur(8px)}select,button{font:inherit;border:1px solid #becdc2;border-radius:6px;background:white;color:var(--ink);padding:7px 12px}button{cursor:pointer}button:hover{background:#e8efe8}input[type=range]{accent-color:var(--jade);flex:1;min-width:140px}.year-big{font-size:24px;min-width:65px;font-weight:700}section{margin-top:30px;scroll-margin-top:100px}.panel{background:white;border:1px solid var(--line);border-radius:12px;padding:22px;margin-top:16px}.notes{background:#ebf0e7;border-left:3px solid #7b956f;padding:14px 18px;border-radius:5px}.warning{background:#faf0e3;border-left-color:#c57b35}.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0}.kpi{padding:14px;background:#f5f7f2;border-radius:9px}.kpi-value{font-size:22px;font-weight:650}.delta{font-size:12px;color:var(--muted)}.split{display:grid;grid-template-columns:1fr 1fr;gap:16px}.events{list-style:none;padding:0;margin:0}.events li{padding:10px 0;border-bottom:1px solid #edf0e9}.tag{font-size:11px;display:inline-block;margin-right:8px;border-radius:4px;padding:1px 5px;background:#e9f1eb}.tag.assumed{background:#f7eddf}.tag.off{background:#f0e9e8}.charts{display:grid;grid-template-columns:1fr 1fr;gap:18px}.chart{margin:0;background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 16px}.chart.wide{grid-column:1/-1}.chart-head{display:flex;justify-content:space-between;gap:10px}.chart-id{font:12px monospace;color:#91a29a}.chart p{font-size:12px;color:var(--muted);line-height:1.6;min-height:38px}svg{width:100%;height:auto;display:block;overflow:visible}.legend{display:flex;gap:12px;flex-wrap:wrap;font-size:11px;line-height:1.4;margin-top:5px}.swatch{display:inline-block;width:17px;margin-right:4px;vertical-align:middle;border-top:2px solid}.swatch.dashed{border-top-style:dashed}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:12px}th,td{text-align:left;vertical-align:top;padding:10px 11px;border-bottom:1px solid #e7ece3}th{font-weight:650;background:#edf2e9;white-space:nowrap}td code{font-size:10px;word-break:break-word}tbody tr.active{background:#e8f1e7}tbody tr.year-row{cursor:pointer}.min-table{min-width:920px}.source-table{min-width:780px}.source-table td:last-child{font-family:monospace;font-size:10px;overflow-wrap:anywhere}.pill{background:#e6eee2;padding:2px 7px;border-radius:4px}.section-number{font-size:12px;letter-spacing:.1em;color:var(--jade);font-weight:bold;margin-bottom:6px}footer{border-top:1px solid var(--line);padding-top:22px;margin-top:40px;font-size:12px}.formula{font-family:monospace;font-size:12px;line-height:1.9;overflow-wrap:anywhere}details{margin-top:14px}summary{cursor:pointer;font-weight:600}.year-cursor{pointer-events:none}#insight{font-size:13px}#timeline-note{font-size:12px}.chart-tooltip{position:fixed;background:#173431;color:#fff;padding:8px 12px;border-radius:6px;font-size:12px;pointer-events:none;z-index:30;display:none}
@media(max-width:780px){main{padding:24px 16px}h1{font-size:31px}.hero-cards,.split,.charts{grid-template-columns:1fr}.chart.wide{grid-column:auto}.kpis{grid-template-columns:repeat(2,1fr)}.controls{gap:9px}select{max-width:220px;font-size:12px}.big{font-size:30px}.panel{padding:16px}.chart{padding:15px}body{font-size:14px}}@media print{.controls{position:static}body{background:white}.panel,.chart{break-inside:avoid}.charts{display:block}.chart{margin-bottom:16px}main{padding:0}a{color:inherit}h1{font-size:30px}}
</style></head><body><main>
<header><div class="eyebrow">SUZUME POLICYCRAFT ENGINE / F SCENARIO</div><h1>F施策を、年ごとに読む。</h1><p class="lede">2026–2055年の既存暫定計算を、イベントと入力条件からたどる。<br>実線は2026年初期状態、破線は過去試算互換。政策制度の実装と、外生係数による近似を分けて表示します。</p><p><span class="badge">DRAFT · NON-CANONICAL</span> <span class="badge warn">新たなシミュレーション実行なし</span> <span class="badge">外部通信不要 · 単独HTML</span></p>
<div class="hero-cards"><div class="hero-card"><small>2026初期状態 · 29遷移 / 2055年実質GDP</small><div class="big">682.38<span class="unit">兆円</span></div><div class="muted">2026年はGDP580兆円を初期値として維持</div></div><div class="hero-card legacy"><small>過去試算互換 · 30遷移 / 2055年実質GDP</small><div class="big">661.52<span class="unit">兆円</span></div><div class="muted">2026年にも石油ショック等を適用</div></div></div>
<nav class="nav"><a href="#year-detail">年次を確認</a><a href="#plots">11のグラフ</a><a href="#timeline">全年表</a><a href="#policy-map">制度と実装</a><a href="#limits">評価の境界</a></nav></header>
<div class="controls"><label for="case">表示ケース</label><select id="case"><option value="F_2026_INITIAL_29">2026初期状態｜29遷移</option><option value="F_2026_TRANSITION_30">過去試算互換｜30遷移</option></select><button id="prev" aria-label="前年">←</button><output class="year-big" id="year-label">2027</output><button id="next" aria-label="翌年">→</button><input id="year" aria-label="選択年" type="range" min="2026" max="2055" value="2027"><select id="year-select" aria-label="年を直接選択"></select></div>
<section id="year-detail"><div class="section-number">01 / YEAR EXPLORER</div><h2><span id="detail-year">2027</span>年に何が起きたか</h2><div id="boundary" class="notes"></div><div id="kpis" class="kpis"></div><div class="split"><div class="panel"><h3>当年のイベントと条件変更</h3><ul class="events" id="event-list"></ul><p id="insight"></p></div><div class="panel"><h3>当年の入力条件</h3><div class="scroll"><table><thead><tr><th>項目・状態</th><th>値／対応列</th></tr></thead><tbody id="input-detail"></tbody></table></div></div></div><p class="muted" style="font-size:12px">前年差は保存済み結果の当年−前年。2026には比較可能な保存済み前年がなく「—」。賃金アンカー値は入力の補間表示で、政策により内生的に算出された賃金ではありません。</p></section>
<section id="plots"><div class="section-number">02 / ANNUAL SERIES</div><h2>入力と結果を、同じ年でつなぐ</h2><div class="notes">実線＝2026初期状態、破線＝過去互換。共有入力は一つの系列として表示。点・グラフをクリックすると年を選択できます。注記のない年も定期リスクや継承計算があり、全年表を併せて確認してください。</div><div class="charts" id="charts"></div></section>
<section id="timeline"><div class="section-number">03 / EVENT & PARAMETER TIMELINE</div><h2>2026–2055年 全年表</h2><p id="timeline-note">重複リスクは省略せず併記。消費・投資・教育・aging dragはpp、歳出は%、移民は人/年。行を選択して詳細へ反映できます。</p><div class="panel scroll"><table class="min-table"><thead><tr><th>年</th><th>リスク全件 / 合算</th><th>消費/投資/教育</th><th>純移民</th><th>aging drag</th><th>弾性 / 歳出</th><th>追加インフレ / 税収補正</th><th>係数変更</th></tr></thead><tbody id="timeline-body"></tbody></table></div><p class="muted">共通定数：死亡倍率1.015、出生減少倍率0.975、φ=0.15、α=0.35、基調成長1pp、基調インフレ2pp、税収cap30%、VAT一時インフレ0（省略仮定）。</p></section>
<section id="policy-map"><div class="section-number">04 / POLICY ↔ IMPLEMENTATION</div><h2>制度が書かれていることと、計算したことを分ける</h2><p>政策本文の制度名を、そのまま実装済みの効果とみなしません。係数として反映した項目も、制度別の効果検証ではありません。</p><div class="panel scroll"><table class="min-table"><thead><tr><th>F施策本文の制度</th><th>参照</th><th>実装区分</th><th>今回反映したこと／していないこと</th></tr></thead><tbody id="policy-body"></tbody></table></div></section>
<section id="limits"><div class="section-number">05 / INTERPRETATION</div><h2>この計算で確認できる範囲</h2><div class="split"><div class="panel"><h3>計算関係</h3><p class="formula">実質成長 = 基調 + 消費 + 投資 + 教育 − risk + (1−α) × (人口成長 + aging drag)<br>名目成長 = 実質成長 + 基調インフレ + 追加インフレ + VAT一時要因<br>税収 = min(前年税収 × (1+名目成長×弾性) × イベント倍率, 名目GDP×30%)<br>歳出 = 前年歳出 × (1+歳出成長率)<br>資金不足proxy = max(歳出−税収, 0)</p><p>イベントの式上の接続は確認できますが、反実仮想比較による実証的な因果効果を推定したものではありません。</p></div><div class="panel"><h3>未算出・暫定仮定</h3><p>税率→税収基盤、医療・年金の制度別収支、所得分配、政策金利、配当、内部留保、労働者人口人数、非正規率、所得中央値、エンゲル、ジニの内生変化、実際の国債・債務・PBは評価できません。</p><p>移民の線形刻み、賃金中間年、税収弾性の境界、α/φ、aging dragの組込みは仮定を含みます。v5の実質賃金初期値380とFアンカー400の相違は裁定せず、今回は既存計算の400を保持しています。</p></div></div><div class="notes warning" style="margin-top:16px"><b>過去試算との比較：</b>30期間ケースは過去コード出力の270項目と丸め精度内で一致（既存証拠の再利用）。v5§8の端点661.9兆円とは約−0.3766兆円の差。旧F docx系列は原本・版・定義未照合のため混ぜません。2ケースの差は境界差であり、政策差ではありません。</div></section>
<section id="evidence"><div class="section-number">06 / FIXED INPUTS</div><h2>使用した6原本</h2><p>固定Commit <code>30530ad2b012ce33715db662fa0c5ca06a2f10ed</code>。既存再取得PASSの原本を再利用し、コード再実行なしで可視化しました。</p><div class="panel scroll"><table class="source-table"><thead><tr><th>原本</th><th>bytes</th><th>SHA-256</th></tr></thead><tbody id="source-body"></tbody></table></div></section>
<footer>表示確認の範囲：年・ケース60組の処理とSVG生成をスクリプト検査。実ブラウザ画面・モバイル配置は環境制約により未検証です。<br>2026-11-10 / SPE · F provisional scenario · DRAFT / RP-023・M19–25 HOLD、RP-024 PENDING維持。正式Acceptance・Freeze・政策採用判断ではありません。</footer>
</main><div class="chart-tooltip" id="tip"></div><script id="report-data" type="application/json">DATA_PAYLOAD</script><script>
const D=JSON.parse(document.getElementById('report-data').textContent),cases=Object.keys(D.results);let year=2027,selected=cases[0];const $=id=>document.getElementById(id),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),num=(v,d=2)=>v==null?'—':Number(v).toLocaleString('ja-JP',{maximumFractionDigits:d,minimumFractionDigits:d}),sign=(v,d=2)=>v==null?'—':(v>0?'+':'')+num(v,d),p=(v,d=3)=>num(v*100,d),r=(c,y)=>D.results[c].find(r=>r.year===y),Y=y=>D.years.find(x=>x.year===y);
for(let y=2026;y<=2055;y++)$('year-select').insertAdjacentHTML('beforeend',`<option value="${y}">${y}年</option>`);
const J='#176c60',B='#326eac',O='#c57b35',R='#bc5157',P='#8064a8',G='#667e54';
function pair(key,label,color,scale=1){return cases.map((c,i)=>({label:label+' / '+(i?'過去互換':'初期状態'),color,dash:!!i,case:c,vals:D.results[c].map(x=>({year:x.year,value:x[key]==null?null:x[key]/scale}))}));}
function input(key,label,color,scale=100){return {label,color,input:true,vals:D.years.map(x=>({year:x.year,value:x.params[key]*scale}))};}
const charts=[
{id:'real',title:'実質GDP',unit:'兆円',desc:'価格効果を除いた既存出力。2027年中台・2031年南海のリスクと、後半の人口・労働項を確認。',series:pair('real_gdp','実質GDP',J),marks:[2027,2031,2033,2046]},
{id:'nom',title:'名目GDP',unit:'兆円',desc:'実質成長にインフレ率を加算して累積。2027年は実質押下げと追加インフレ5ppが別経路で作用。',series:pair('nominal_gdp','名目GDP',B),marks:[2027,2031,2041]},
{id:'growth',title:'実質GDP成長率',unit:'% / 年',desc:'2026初期状態の成長率は未算出のため欠測表示。点を0で埋めず、年次値だけを結びます。',series:pair('real_growth_pct','実質成長率',J),marks:[2027,2028,2031,2033,2044,2046],zero:true},
{id:'pop',title:'人口',unit:'万人',desc:'出生・死亡・純移民を反映した人口ストック。境界差の累積を2ケースで比較。',series:pair('population','人口',J,1e4),marks:[2030,2035,2046]},
{id:'birthdeath',title:'出生・死亡',unit:'万人 / 年',desc:'出生は賃金入力成長率とφ、死亡は倍率1.015で推移。初期状態の2026件数は初期値。',series:[...pair('births','出生',J,1e4),...pair('deaths','死亡',R,1e4)],marks:[2027,2035]},
{id:'migration',title:'純移民入力',unit:'万人 / 年',desc:'2030年8万人から線形に増加。2034年に40万人到達、2035年以降も40万人。刻みは暫定仮定。',series:[input('net_migration','純移民（暫定入力）',P,1e-4)],marks:[2030,2034,2035],zero:true},
{id:'fiscal',title:'税収・歳出・資金不足proxy',unit:'兆円',desc:'2031年税収×0.9、2033/2041年弾性変更、2035/2045年歳出率変更。proxy 0は実債務の解消ではない。',series:[...pair('tax_revenue','税収',J),...pair('expenditure','歳出',B),...pair('funding_gap_proxy','資金不足proxy',O)],marks:[2031,2033,2035,2041,2043,2045],wide:true,zero:true},
{id:'ratio',title:'税収 / 名目GDP と cap',unit:'%',desc:'税収比率の既存出力とモデル上限30%。制度的な税負担やPBの合否判定とは別。',series:[...pair('tax_to_gdp_pct','税収比率',J),input('tax_cap_ratio','モデル上限30%',R)],marks:[2031,2033,2041],zero:true},
{id:'effects',title:'政策効果とリスクの入力',unit:'pp / 年',desc:'成長率へ加える消費・投資・教育。リスクは減算方向の負値で表示。共通入力であり、2026初期状態では当年遷移に不適用。',series:[input('consumption_stimulus_effect','消費刺激',J),input('investment_promotion_effect','投資促進',B),input('education_effect','教育',P),input('risk_shock','リスク（減算表示）',R,-100)],marks:[2027,2028,2030,2031,2032],zero:true},
{id:'wage',title:'実質賃金アンカー入力',unit:'万円',desc:'2026年400→2055年860の入力アンカーを既存M14で幾何補間した列。内生的な賃金予測ではない。',series:[{label:'共通の補間入力',color:P,input:true,vals:D.results[cases[0]].map(x=>({year:x.year,value:x.real_wage_anchor_man_yen}))}],marks:[2026,2055]},
{id:'demo',title:'人口関連の係数入力',unit:'%・pp（各系列を参照）',desc:'出生減少率−2.5%、死亡増加率+1.5%、aging dragはpp、賃金入力成長率は%。φ=0.15は別途年次詳細に表示。',series:[input('birth_decline_coefficient','出生倍率−1（%）',J,0),input('death_rate_coefficient','死亡倍率−1（%）',R,0),input('aging_drag','aging drag（pp）',O),input('real_wage_growth_rate','賃金入力成長率（%）',P)],marks:[2027,2033,2044,2046],zero:true}
];
charts[10].series[0].vals=D.years.map(x=>({year:x.year,value:(x.params.birth_decline_coefficient-1)*100}));charts[10].series[1].vals=D.years.map(x=>({year:x.year,value:(x.params.death_rate_coefficient-1)*100}));
const markNames={2026:'初期/石油',2027:'中台＋気候',2028:'消費・教育',2030:'投資・移民',2031:'南海＋気候',2032:'消費0.7',2033:'aging・弾性',2034:'移民40万',2035:'歳出1.5%',2041:'弾性2.0',2043:'proxy 0',2044:'aging緩和',2045:'歳出1%',2046:'aging緩和',2055:'終点'};
function drawCharts(){ $('charts').innerHTML='';charts.forEach((c,idx)=>{const card=document.createElement('figure');card.className='chart'+(c.wide?' wide':'');card.innerHTML=`<div class="chart-head"><h3>${esc(c.title)}</h3><span class="chart-id">${String(idx+1).padStart(2,'0')}</span></div><p>${esc(c.desc)}</p><div class="plot"></div><div class="legend">${c.series.map(s=>`<span><i class="swatch ${s.dash?'dashed':''}" style="border-color:${s.color}"></i>${esc(s.label)}</span>`).join('')}</div>`;$('charts').appendChild(card);
 const W=c.wide?1120:560,l=57,rr=15,b=39,pw=W-l-rr;const mx=y=>l+(y-2026)/29*pw;const lanes=[];const overrides={migration:{2030:'移民8万',2034:'移民40万',2035:'定常期'},pop:{2030:'移民開始',2035:'移民定常期'},birthdeath:{2035:'移民定常期'},wage:{2026:'入力400万円',2055:'入力860万円'},demo:{2027:'賃金補間成長'}};const marks=c.marks.map(y=>{const label=y+' '+(overrides[c.id]?.[y]||markNames[y]||'');const width=[...label].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?9:5),0);const left=Math.max(l,Math.min(W-rr-width,mx(y)-width/2));let lane=0;while(lanes[lane]!==undefined&&lanes[lane]+8>left)lane++;lanes[lane]=left+width;return {year:y,label,left,lane};});const t=42+lanes.length*15,H=t+210+b,ph=H-t-b,vals=c.series.flatMap(s=>s.vals.filter(v=>v.value!==null).map(v=>v.value));let lo=Math.min(...vals),hi=Math.max(...vals);if(c.zero){lo=Math.min(0,lo);hi=Math.max(0,hi)}const pad=(hi-lo||1)*.10;lo-=pad;hi+=pad;
 const x=y=>l+(y-2026)/29*pw,yy=v=>t+(hi-v)/(hi-lo)*ph;let svg=`<svg font-family="Noto Sans CJK JP, sans-serif" role="img" aria-label="${esc(c.title)}、単位${esc(c.unit)}" viewBox="0 0 ${W} ${H}"><text x="${l}" y="14" font-size="11" fill="#60746d">${esc(c.unit)}</text>`;
 for(let k=0;k<=4;k++){let v=lo+(hi-lo)*k/4,y=yy(v);svg+=`<line x1="${l}" x2="${W-rr}" y1="${y}" y2="${y}" stroke="#e6ece2"/><text x="${l-7}" y="${y+4}" font-size="10" text-anchor="end" fill="#60746d">${num(v,Math.abs(v)<10?1:0)}</text>`;}
 for(let y of [2026,2030,2035,2040,2045,2050,2055])svg+=`<text x="${x(y)}" y="${H-12}" font-size="10" text-anchor="middle" fill="#60746d">${y}</text>`;
 marks.forEach(m=>{const y=m.year;svg+=`<line x1="${x(y)}" x2="${x(y)}" y1="${t}" y2="${H-b}" stroke="#c9d4c5" stroke-dasharray="2 4"/><text x="${m.left}" y="${28+m.lane*15}" text-anchor="start" font-size="9" fill="#75816e">${esc(m.label)}</text>`;});
 c.series.forEach(s=>{let path='',open=false;for(const v of s.vals){if(v.value===null){open=false;continue}path+=(open?'L':'M')+x(v.year).toFixed(2)+','+yy(v.value).toFixed(2);open=true;}
 const opacity=s.case&&s.case!==selected?.6:1;svg+=`<path d="${path}" fill="none" stroke="${s.color}" stroke-width="${s.dash?1.8:2.3}" ${s.dash?'stroke-dasharray="6 4"':''} opacity="${opacity}"/>`;
 s.vals.forEach(v=>{if(v.value!==null)svg+=`<circle class="data-dot" data-year="${v.year}" data-tip="${esc(s.label+' / '+v.year+'年 / '+num(v.value,4)+' '+c.unit)}" cx="${x(v.year)}" cy="${yy(v.value)}" r="2.3" fill="${s.color}" opacity="${opacity}"><title>${esc(s.label)} ${v.year}年 ${num(v.value,4)} ${esc(c.unit)}</title></circle>`;});});
 svg+=`<line class="year-cursor" x1="${x(year)}" x2="${x(year)}" y1="${t-2}" y2="${H-b}" stroke="#173431" stroke-width="1.3" opacity=".7"/><text x="${x(year)}" y="${H-b+13}" font-size="10" text-anchor="middle" fill="#173431">${year}</text></svg>`;card.querySelector('.plot').innerHTML=svg;
 const el=card.querySelector('svg');el.addEventListener('click',e=>{const rect=el.getBoundingClientRect();setYear(Math.max(2026,Math.min(2055,Math.round(2026+((e.clientX-rect.left)/rect.width*W-l)/pw*29))));});card.querySelectorAll('.data-dot').forEach(dot=>{dot.addEventListener('mousemove',e=>{const tip=$('tip');tip.textContent=dot.dataset.tip;tip.style.display='block';tip.style.left=Math.min(e.clientX+12,window.innerWidth-250)+'px';tip.style.top=Math.max(8,e.clientY-45)+'px'});dot.addEventListener('mouseleave',()=>{$('tip').style.display='none'});}); });}
function initTables(){for(const yy of D.years){const a=yy.params;const tr=document.createElement('tr');tr.className='year-row';tr.dataset.year=yy.year;tr.innerHTML=`<td><b>${yy.year}</b></td><td>${yy.risks.length?yy.risks.map(x=>esc(x.name)+' '+x.pct+'pp').join('<br>'):'発生なし'}<br><small>合算 ${p(a.risk_shock,1)}pp</small></td><td>${p(a.consumption_stimulus_effect,1)} / ${p(a.investment_promotion_effect,1)} / ${p(a.education_effect,1)} pp</td><td>${num(a.net_migration,0)}</td><td>${p(a.aging_drag,4)}</td><td>${a.tax_elasticity} / ${p(a.expenditure_growth,1)}%</td><td>${p(a.risk_event_inflation_impact,1)}pp / ×${a.tax_event_factor}</td><td>${esc(yy.condition_change_text)}</td>`;tr.onclick=()=>setYear(yy.year);$('timeline-body').appendChild(tr)}
 $('policy-body').innerHTML=D.policies.map(p=>`<tr><td>${esc(p.policy)}</td><td>${esc(p.text)}</td><td><span class="tag ${p.status.startsWith('未実装')?'off':'assumed'}">${esc(p.status)}</span></td><td>${esc(p.actual)}</td></tr>`).join('');
 $('source-body').innerHTML=Object.entries(D.registry).map(([n,s])=>`<tr><td><a href="https://github.com/spe-flatvat/SPE/blob/${D.commit}/${s.path}" target="_blank" rel="noreferrer">${esc(n)}</a></td><td>${num(s.bytes,0)}</td><td>${s.sha256}</td></tr>`).join('');}
function renderYear(){const row=r(selected,year),prev=r(selected,year-1),yr=Y(year);$('year-label').textContent=year;$('detail-year').textContent=year;$('year').value=year;$('year-select').value=year;
 $('boundary').className='notes'+(year===2026?' warning':'');$('boundary').textContent=year===2026?(selected===cases[0]?'初期状態：2026年のリスク・政策係数・人口遷移をこの行には適用していません。成長率・前年差は未算出。':'過去互換：初期値を2025末へ仮置きし、2026年の石油ショックと当年入力を適用した計算結果です。保存済み前年結果がないため前年差は表示しません。'):'当年入力を前年状態へ適用した既存エンジン出力。外生係数・補間値を含む暫定計算です。';
 const metrics=[['実質GDP','real_gdp','兆円',1],['名目GDP','nominal_gdp','兆円',1],['実質成長率','real_growth_pct','%',1],['人口','population','万人',1e4],['税収','tax_revenue','兆円',1],['歳出','expenditure','兆円',1],['資金不足proxy','funding_gap_proxy','兆円',1],['賃金アンカー入力','real_wage_anchor_man_yen','万円',1]];
 $('kpis').innerHTML=metrics.map(([label,k,u,scale])=>{const delta=prev&&prev[k]!=null&&row[k]!=null?(row[k]-prev[k])/scale:null;return `<div class="kpi"><small>${label}</small><div class="kpi-value">${num(row[k]===null?null:row[k]/scale)}<span class="unit">${u}</span></div><div class="delta">前年差 ${sign(delta)} ${k==='real_growth_pct'?'pp':u}${delta===null?'（比較不可）':''}</div></div>`}).join('');
 let ev=yr.risks.map(x=>`<li><span class="tag">リスク</span><b>${esc(x.name)}</b>：実質成長から−${x.pct}pp</li>`);if(!ev.length)ev.push('<li><span class="tag">リスク</span>当年の発生なし</li>');ev.push(`<li><span class="tag assumed">条件変更</span>${esc(yr.condition_change_text)}</li>`);if([2026,2028,2035].includes(year))ev.push('<li><span class="tag off">未実装</span>'+({2026:'税制・企業統治改革の制度別計算',2028:'医療・年金改革の制度別計算',2035:'消費税5%化・成長/Gini/人口による自動トリガー'})[year]+'。本文の予定と実行済み条件を区別。</li>');$('event-list').innerHTML=ev.join('');$('insight').textContent=D.unimplemented[String(year)]||'条件変更がなくても前年状態を継承し、人口・GDP・税収・歳出は累積的に変化します。';
 $('input-detail').innerHTML=yr.event_rows.filter(e=>!e.event_name.includes('リスクイベントなし')&&!yr.risks.some(x=>x.name===e.event_name)).map(e=>`<tr><td><b>${esc(e.event_name)}</b><br><span class="tag ${e.reflection_status.includes('暫定')?'assumed':''}">${esc(e.reflection_status)}</span></td><td>${esc(e.input_value)}<br><code>${esc(e.csv_columns)}</code><br><small>${esc(e.source)} → ${esc(e.calculation_item)}</small></td></tr>`).join('');
 document.querySelectorAll('#timeline-body tr').forEach(tr=>tr.classList.toggle('active',Number(tr.dataset.year)===year));$('prev').disabled=year===2026;$('next').disabled=year===2055;drawCharts();}
function setYear(y){year=Number(y);$('tip').style.display='none';renderYear()}
$('year').oninput=e=>setYear(e.target.value);$('year-select').onchange=e=>setYear(e.target.value);$('case').onchange=e=>{selected=e.target.value;renderYear()};$('prev').onclick=()=>setYear(Math.max(2026,year-1));$('next').onclick=()=>setYear(Math.min(2055,year+1));initTables();renderYear();
</script></body></html>'''
if __name__=='__main__':main()
