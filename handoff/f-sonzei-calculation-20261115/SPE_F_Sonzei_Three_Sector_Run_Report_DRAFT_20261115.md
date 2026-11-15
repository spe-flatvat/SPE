# SPE｜F損税モデル・3部門試作 実行報告

Status: DRAFT / PROVISIONAL / NON-CANONICAL / DIAGNOSTIC ONLY  
入力固定日時: 2026-11-15T10:11:05+00:00  
実行環境: Python 3.12.14 / Linux。追加依存なし。

## 結果

**実装・ローカル実行PASS。** 固定Claude原コードを実行し、基準90行・金額15項目の再現、原報告の9年次抜粋×7指標の丸め一致を確認した。既存91行CSVを入力として読込み、60個の部分計算・感度ケースと、全国仮定3部門×2方式を、2026〜2055年の1,980行へ出力した。全国の出典付き完全推計が完成したという判定ではない。

1. `SPE_F_Sonzei_Three_Sector_Prototype_DRAFT_20261115.py`：計算・受領ハッシュ検査・入力選択防止・自己確認・レポート生成。
2. `SPE_F_Sonzei_Three_Sector_Inputs_DRAFT_20261115.json`：固定原本6件のUTF-8本文とSHA、元Claude入力、91行CSV、暫定政策条件、部分ケース定義を内包。オフライン再実行可能。
3. `SPE_F_StatusQuo_Sonzei_Annual_Diagnostics_DRAFT_20261115.csv`：全金額は円。空欄は未取得・条件未確定。ケース間単純合計禁止。
4. `SPE_F_Sonzei_Three_Sector_Run_Report_DRAFT_20261115.md`：本報告。実行ログと制限を含む。

## 固定入力・実バイト検証

固定CommitからGitHub連携のBase64で取得、デコードした実バイトのサイズ・SHA-256・Git blob SHA-1を確認した。91行CSVとNotesは前回の実測SHAとも一致。既存統計の再調査は行っていない。

|役割|固定Commit|ファイル|bytes|SHA-256|
|---|---|---|---:|---|
|prototype_code|`e87e43787ecac73297065ba026b6de41d4f072ee`|`SPE_sonzei_min_run_DRAFT.py`|8422|`b220c105469b0b393d85d40486032ffe704b0e833f590760e7c73d211d09f8e3`|
|prototype_inputs|`e87e43787ecac73297065ba026b6de41d4f072ee`|`SPE_sonzei_min_inputs_DRAFT.json`|3067|`9fdecef8404e3e4cd6320f21892c54c4443b21d7d4937a2e63ace292ca4c29ac`|
|prototype_report|`e87e43787ecac73297065ba026b6de41d4f072ee`|`SPE_損税モジュール_最小実装_結果_DRAFT_20261114.md`|7733|`d784ad6f8e21e8f090dd435b1328b36c363389a2dc074e0f8d01196719215c65`|
|candidate_csv|`05d2ea052ffbfb206193166d43d4656a6b7fdc36`|`SPE_F_Sonzei_Calculation_Input_Candidates_DRAFT_20261115.csv`|58122|`e3f45a64754f04c12abe6cbd26ead9aedc9fcab0a7f3e4423537396ec03462ac`|
|candidate_notes|`05d2ea052ffbfb206193166d43d4656a6b7fdc36`|`SPE_F_Sonzei_Input_Bridge_Notes_DRAFT_20261115.md`|14051|`15d6e65a28a2f903b4dbc5fa1856670aa6b99a735cce032098504adf95a4801e`|
|basis|`cc4a6054e716a3d63d2e30f76d0c102f2397e55c`|`SPE_F_Provisional_Implementation_Basis_20261114.md`|5560|`8b88636a5581b28939e340c4beaaac81b3c193caef201a2d7cf1e2770034594b`|

Claude資料は `handoff/claude-sonzei-min-20261114/`、入力候補は `handoff/f-sonzei-input-bridge-20261115/`、F基準は `handoff/SPE_F_Provisional_Implementation_Basis_20261114.md`。固定原本は変更していない。

## 再実行コマンド・実行ログ

```bash
python3 SPE_F_Sonzei_Three_Sector_Prototype_DRAFT_20261115.py SPE_F_Sonzei_Three_Sector_Inputs_DRAFT_20261115.json --outdir replay
```

原コードCLIも作業ディレクトリ内で実行：

```text
python3 sources/SPE_sonzei_min_run_DRAFT.py sources/SPE_sonzei_min_inputs_DRAFT.json claude-baseline
exit=0
selfcheck OK; cases: 21
2026 10.0 1.47 1.47 0.00 0.00 0.00 0.00 0.00
2040  5.0 1.81 0.00 1.81 3.53 0.00 0.93 0.63
2055  5.0 2.27 0.00 2.27 4.42 0.00 1.16 0.79
```

今回コードの実行確認（18項目）：

```text
PASS fixed Claude selfcheck + 90 rows x 15 monetary fields reproduced (trillion JPY abs tolerance 1e-9)
PASS 9 original published excerpt years x 7 metrics match rounding
PASS thousand-yen / yen / trillion-yen conversion
PASS exclusive gross/net selection rejected
PASS cross-sample P summation rejected
PASS parent bundle + detail double count rejected
PASS combined R subset + constituent rejected
PASS duplicate candidate rejected
PASS missing remains unknown, real zero preserved, missing input rejected
PASS planned construction cost cannot become current investment P
PASS residential building restriction and unresolved eligibility guard
PASS loss/tax/public incidence identities; no macro GDP addition
PASS start-year and kappa=0 boundaries
PASS reduced-rate component converges to flat 5%, not proportional 4%
PASS historical compensation not misread as input VAT
PASS sourced partial profiles and national placeholders remain separate
PASS 2026–2055 complete coverage, no duplicate case-year
PASS saved CSV reread, row count and unknown fields remain blank
rows=1980; profiles=60+6; period=2026..2055
exit=0（全確認・CSV再読取完了後）
```

新たな多AIレビュー工程は設けていない。ここでの自己確認は実行コードの境界・計算検査であり、後続Claudeの独立検証PASSではない。

## 基準ケース再現（全て従来の全国仮定、兆円／年）

|年|L_SQ|L_F|損税削減|税ベース拡大ΔT|税率効果・全年度|新output VAT公費負担|
|---|---:|---:|---:|---:|---:|---:|
|2026|1.471750000|1.471750000|-0.000000000|0.000000000|0.000000000|0.000000000|
|2028|1.516233644|0.758116822|0.758116822|0.000000000|-0.758116822|0.000000000|
|2036|1.708025959|0.765666809|0.942359150|0.265038511|-0.854012980|0.070676936|
|2037|1.733646349|0.538028177|1.195618171|1.225508626|-0.866823174|0.071737090|
|2038|1.759651044|0.000000000|1.759651044|3.428285654|-0.879825522|2.530256846|
|2040|1.812836497|0.000000000|1.812836497|3.531905588|-0.906418248|2.606733859|
|2055|2.266466320|0.000000000|2.266466320|4.415701623|-1.133233160|3.259022260|

R2025=医療45・教育6・住宅20兆円、p=.20/.25/.20、年成長1.5%、税率10→7.5→5%、開始2038/2036/2037、φ=.9/.2/0、κ=1は固定Claude試作の暫定値を維持した。**出典付き全国値への置換ではない。** 減税先行・5%目標・2038完了というF基準と、未決の具体年次・係数を区別する。

旧コードの `dT_rate` は開始前だけを表示する。再現欄 `legacy_delta_tax_rate_prestart` はこの仕様を維持。一方、今回の `delta_tax_rate_all_years` は開始後も上流input VATの税率差を表示する。全年度差額を求めるときに、旧 `dT_base+dT_rate` だけを使わない。これは原コードの改変ではなく、新規コードで比較系列を明示したもの。

## 出典付き部分計算の2040年例（金額は円）

|case_id|R|P_net|損税削減|output VAT F|既存補填変更額|
|---|---:|---:|---:|---:|---:|
|MED-M14-GROSS|未算出|362,950,631.847148895|36,295,063.184714891|未算出|未算出|
|MED-BUNDLE-GROSS|未算出|1,354,047,187.077743292|134,736,809.314525664|未算出|未算出|
|EDU-SALES-CASH-SUBSET|713,712,096,626.696166992|未算出|未算出|35,685,604,831.334808350|未算出|
|EDU-PURCHASE-SHARE-50|未算出|814,965,591,168.019042969|81,496,559,116.801910400|未算出|未算出|
|RENT-MANAGEMENT-3|17,699,450,599,919.792968750|482,712,289,088.721618652|48,271,228,908.872161865|884,972,529,995.989746094|未算出|
|MED-COMP-病院-WITHDRAW|未算出|未算出|未算出|未算出|-58,877,122.454511136|
|NATIONAL_GUARDED_rental|25,004,641,333,087.355468750|5,000,928,266,617.471679688|未算出|1,250,232,066,654.367919922|未算出|

施設別の金額は**1施設当たり**、教育・住宅部分集合は各対象集合。異なる単位範囲の行を合算しない。2023/2024の元値を1.5%名目成長で投影した2026〜2055値は実測ではない。人口・GDPエンジンとは接続していない。源泉の会計・税率の未確定条件も残す。

### 医療

施設別公表費用・当期投資について税込/税抜の排他的ケースを作成。材料8%/その他10%等はCSVの条件を継承。SQの8%/10%構成を保存し、Fの各成分税率は暫定的にmin(当該現行税率, F標準税率)とする。したがって到達時は両成分5%であり、8%成分を比例縮小した4%にはしない。中間経路・具体年次は政策確定値としない。費消額・在庫調整、介護/診療・附属事業の用途配賦は未了。

回答標本が違う経常費と投資を足していない。n=732の既存4費目束と構成費目も別ケース。施設数を掛けて全国化しない。投資の将来系列は同規模の**毎年新規取得**を仮定するため、2024取得ストックを年々再控除したものではないが、実際の更新投資計画は未取得。

既存補填A/Bは別標本の独立系列。維持と課税化後全撤回の2感度を計算し、Aをinput VATへ読み替えない。補填Aは診療報酬の増分で全額国庫支出とは限らず、公費・保険料・患者負担の分解が未取得。したがって撤回Aを丸ごと国庫節減として差し引かず `historical_compensation_public_cost_change` を未算出とする。

### 教育

公立・国立CF・国立PL・私立のRは範囲・会計系列ごとに分離。P未取得の売上ケースはoutput VATとφの帰着のみ計算でき、損税額・税収純増は空欄。国立の購入CF1.392兆円に対して教育用途かつ課税対象である合成割合25/50/75%を明示仮定し、税込10%除去後の**部分P感度**を計算した。これは教育用途を実測したものではなく、全国p=.25の置換ではない。

給与CF・投資CF・教育PLを購入CFへ足さず、減価償却・附属病院等の未分離も維持。売上と購入額の対象範囲が違うため、RケースとP感度を勝手に結合した「教育全国結果」を作っていない。

### 住宅

管理費3/5/10%・委託率100%というCSV既存感度を計算。Rは専用住宅の既知家賃proxy、Pは管理だけで、修繕・建物取得は含まれない。予定工事費は数値があってもPへの採用をコードが拒否する。

`CLAUDE_BASELINE_rental` は旧κ=1の数式再現だけで、現在の建物控除制限解除を認定しない。`NATIONAL_GUARDED_rental` はPのうち建物の比率も将来制限の取扱いも不明なので、開始後の控除・残存損税・税ベース差額を空欄にする。管理費ケースの通常仕入控除仮定と建物特例を混同しない。国税庁の既存調査済み制度条件は入力Notesを再利用し、今回再調査していない。

## 系列の意味

```text
L_SQ = input_VAT_SQ − input_credit_SQ
L_F  = input_VAT_F  − input_credit_F
損税削減 = (input_VAT_SQ−input_VAT_F) + (input_credit_F−input_credit_SQ)
税ベース差額 = output_VAT_F − (input_credit_F−input_credit_SQ)
税率差額 = input_VAT_F − input_VAT_SQ（開始後も別掲）
税収帰属差額 = 税ベース差額 + 税率差額
将来output VAT公費負担 = phi × output_VAT_F
既存補填変更 = A_F − A_SQ（input VATとは別）
```

税収帰属差額は部門上流の埋込税を含む旧モデルと同じ限定的な会計帰属指標で、国全体の税収純増ではない。全体効果は行動・価格・他部門・補填の公的負担分等が不足。`delta_public_budget_with_known_compensation` は必要系列がすべて既知の場合だけ計算し、unknownを0で埋めない。将来φの負担と歴史的補填を同一系列にしない。`macro_GDP_addition=0` は意図的に接続しない構造ゼロであり、経済効果がゼロという評価ではない。

CSVは同じケースのF/SQを横持ちし、排他ケースはcase_idで分離。assumptions_refは同梱JSONのprofilesのid、全国仮定はprototype_config+policyを参照する。全ケース合計・全国と施設平均の合計は提供しない。欠損の合計も未算出。JSONのケースを編集する場合でも同一排他群・二重計上・未取得値・計画額の誤採用は検査で拒否する。

## 成果物のローカル同一性

|ファイル|bytes|SHA-256|
|---|---:|---|
|`SPE_F_Sonzei_Three_Sector_Prototype_DRAFT_20261115.py`|31746|`95ea3c5ca87dfebd42eb4551ddf97a2396734b89d47926d4b8c0e21ada5538a4`|
|`SPE_F_Sonzei_Three_Sector_Inputs_DRAFT_20261115.json`|137774|`92d96a59888c50f97fe8c23a49109c9836856579971156b7e0970042dba8643d`|
|`SPE_F_StatusQuo_Sonzei_Annual_Diagnostics_DRAFT_20261115.csv`|926134|`e4a0e91e3f24ffec14a831c95b7d44bc116afff7655ff1ba483b9066c2c6ed5a`|

本報告自身のサイズ・SHAは引渡し回答で提示する。原コード実行の `claude-baseline/` と取得原本、補助ログはローカル作業用であり、GitHub追加対象は指定4件だけ。完成4件の事後再取得はGitHub保存後に別途確認し、書込み前の本報告では保全PASSを先取りしない。

## 残余と終了

全国値・実際の将来投資・医療補填の公的負担内訳・教育用途按分・住宅建物の将来控除制度は未確定。成功済みの基準再現・部分計算・年次CSV生成は維持する。後続Claudeは同じ4原本から再実行し、独立に確認可能。

正式エンジン・政策原本・main・DecisionLogは未変更。正式Acceptance、Finding Close、Freeze、Canonical化、HOLD解除、新規RP・多AIレビュー工程は実施しない。RP-023／M19–25 HOLD、RP-024 PENDING維持。4原本の引渡し後停止。
