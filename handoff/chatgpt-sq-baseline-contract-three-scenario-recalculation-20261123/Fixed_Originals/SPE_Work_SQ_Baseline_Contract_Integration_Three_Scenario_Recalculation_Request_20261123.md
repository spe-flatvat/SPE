# SPE｜SQ共通計算仕様の整備・F/N3接続・3施策比較再計算

**Status:** OWNER-ISSUABLE / ISOLATED IMPLEMENTATION AND EXECUTION / DRAFT NON-CANONICAL  
**Repository:** `spe-flatvat/SPE`  
**Target branch:** `work/chatgpt-handoff`  
**Date:** 2026-11-23  
**Horizon:** 2026–2055（30年次）  
**Work priority:** SQ入力・価格・イベント契約 → SQ限定修正/再計算 → F/N3共通SQ接続 → 3施策同条件再計算 → Claude独立検算用パケットの引渡し

## 1. 目的

StatusQUO（SQ）をF・N3の**共通基準施策かつ比較ベースライン**として安定させる。前回診断で判明したSQ系列差、名目GDP加算式、物価入力の不活性/結合、2026年初期イベント境界、災害損失の永続性、FのSQ_FIXED対SQ_COMMON_ONの分母差を、既存証拠に基づき処理する。変更の必要性・根拠を確認し、根拠ある**限定修正だけ**隔離実装して2026–2055年再計算する。その後F・N3を**同じSQ・同じ初期値・同じ物価/イベント・同じ共通施策適用範囲**に接続し、3施策を比較する。

**政策目標に合わせたGDP調整は不可。** SQはF/N3に都合のよいデバフではなく、共通のリスク・マクロ基準である。N3の当面の評価はSQとの差、2026年実質GDP水準は長期目標の参考指標。3施策比較の「再計算」と「政策本文/制度の正式改訂」を混同しない。

## 2. 既存固定原本と再利用

- **直近SQ限定診断（最重要）**：固定Commit `149bbf03675884cb8f3fcea96689ebc9e975fac7`、`handoff/chatgpt-statusquo-common-macro-limited-diagnostic-20261123/`。報告書 `SPE_StatusQuo_Common_Macro_Limited_Diagnostic_Report_DRAFT_20261123.md`、`SQ_Findings_And_Next_Executable_Fixes.csv`、`SQ_Baseline_Variant_Provenance_And_Comparability.csv`、`F_N3_SQ_Denominator_Comparability_Check.csv`、年次CSV・8経路240年次・検証2199件PASS・再現コードを利用。現行SQ 2055実質528.962336兆円/名目1023.329981兆円、旧v5候補395.860261/770.549614兆円。**異系統差を政策効果と扱わない**。
- **N3 GDP差経路**：固定Commit `93b8393350eb73dd5ebd803b1ace429aaf4dfe1b`、`handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/`。N3とSQのコア・人口・価格・イベント入力一致、2055年N3−SQ実質GDP−44.970845兆円。税/年金ブロックOFFは診断枝であり政策採用ではない。
- **N3家計課税**：固定Commit `2f36fd5e957e62563a2a2809630386a022d9a8cf`、`handoff/chatgpt-n3-household-tax-path-review-20261123/`。6経路180年次、全国較正未完了。
- **N3年金**：固定Commit `b80f993232fff55800eb42d99ab85c92d1b354c9`、`handoff/chatgpt-n3-pension-path-review-20261123/`。5経路150年次、運用益原資とコホート未確定。
- **SQ原文・旧暫定**：`policies/StatusQuo.md`、`handoff/f-statusquo-provisional-20261115/`。旧v5、原文§9、現行比較SQは別系統。原文の未指定回復率・暦・価格概念を勝手に補完しない。
- **F原文・現行計算**：リポジトリからF政策本文・Annex、F暫定/原文準拠の現行固定成果、Fの比較CSV・再現コードを自己回収。F_FIXEDとCOMMON_ONの比較分母を区別し、同じ共通モジュールの条件を実測で合わせる。

同一固定対象・同一条件の既存PASSは再利用。原本未取得のときは代替取得を試し、可能な実行を継続。Ownerに既存資料の再提出を求めない。

## 3. Stage A：共通入力・価格・イベント契約の技術整備

1. まず現行SQの2026–2055年固定再現を確認。原文・旧v5・現行SQ・F/N3参照SQの系列ID、原本Commit、年境界、初期値、共通モジュール範囲、価格指数規約、リスク暦を機械可読で出力する。**現行SQを採用済みCanonicalと宣言しない**。
2. 現行名目式 `Ncore_t=Ncore_(t-1)*(1+g_t+pi_t)` と乗算候補、実質コア `Ycore=580*A_t*(L_t/L_2026)^0.65`、実装指数 `d=Ncore/Ycore`、最終 `N=Y*d*(1+price_pressure)` を追跡。入力インフレと暗黙GDPデフレーターは別列。現行SQの価格圧力は全期間0である既存PASSを再利用。
3. 価格入力 `base_inflation` が式では直書き `.02` により不活性、`conflict_inflation_extra` と `conflict_gdp_loss` が同じ既定値でも別意味なのに後者が価格式へ参照される件を確認。**同一既定値で結果が不変であること**と、ノブ独立性の必要性を分離。入力キーの正しい接続は、既存仕様/コード上の明確な意味論が確認できた場合だけ隔離修正し、非既定値の最小テストで差を検証する。
4. 2026初期行（580/600、遷移なし）と2026オイル予定イベント、2027以降のイベント適用・気候起点、29/30遷移を予定/実適用/状態持続として明示。休止枝の初期オイルONで2027 LEVELアンカーが基準へ戻る現象を既存証拠から扱い、**仕様未確定の初期ショックを正式にONにしない**。
5. 反復災害・気候損失がA状態へ永続的に残る点について、**回復を採用すべきと推測しない**。原文/証拠にない回復率、災害確率、イベント位相を創作せず、未確定仕様として別記。価格規約を乗算型へ正式変更することも本依頼だけでは自動決定しない。
6. 実装可能な「既存意味論を保護する入力接続・比較系列ID・scheduled/applied出力・不活性キーの検査・二重適用防止」に限って**隔離コピー上で修正**し、変更前後の実値・影響を示す。複数候補がある場合は採用未定の独立枝として比較し、勝手に共通本体へ統合しない。

**Stage A出口：** SQ基準再現、仕様/バグ/較正不足の分類、限定修正候補の年次影響、未決事項の明示。仕様判断が必要で正式基準を一意に決められない場合は、既存SQを`CURRENT_REFERENCE_UNCHANGED`として固定して次段へ進め、未採用候補を混入させない。

## 4. Stage B：SQ基準の固定・F/N3への接続

1. **計算上の固定参照**として、既存現行SQまたは根拠が一意に確定した隔離技術修正SQを、`SQ_COMPARISON_REFERENCE`としてバージョン/Commit/入力/再現コマンド付きで記録する。これは正式政策採用・Canonical化・Freezeではない。正式な価格規約・イベント回復/暦・2026境界をOwnerが裁定していなければ、既存SQを維持する。
2. Fの`SQ_FIXED`（2055実質528.962458兆円）とN3の`SQ_COMMON_ON`（528.962336兆円）等、共通医療モジュールの適用差を同条件で揃える。微小差でも同一SQと無表示で混ぜない。F・N3の政策本体、未採用追加G/I、条件付き雇用・税/年金診断枝は混入させない。
3. 共通エンジンに修正が必要な場合、**共有本体は直接変更せず**隔離実装上でSQ/F/N3の同時再計算を行い、基準差・共通変更差・政策差を別列で保存。原文のない補正係数で数値を合わせない。
4. 既存F/N3の原文準拠・現行実装のどの経路を再実行したかを明記。未実装・未較正部分を「実装済み」と扱わず、F/N3双方の再計算可能な経路を優先。どちらかの経路が再現不能なら、同条件比較を捏造せず部分実行とSTOP範囲を明示。

## 5. Stage C：区切りの3施策再計算（SQ・F・N3）

Stage A/Bの比較契約が再現可能になった時点で、**追加開始承認なしに**SQ・F・N3の3施策を同一2026初期値・同一価格/イベント・同一共通モジュール条件で2026–2055年再計算。3施策の各30年次と、必要な旧版対照を別系列で出力。原文/既存実装にない施策の効果を創作しない。

必須比較：実質/名目GDP、実装価格指数と暗黙デフレーター、実質成長、人口/労働、消費/投資/資本、税収/財政/債務/基金（各経路で実測可能な項目のみ）、2030/2035/2039/2055、SQとの差、SQ割れ年数、2026年実質GDP起点との差。**政策差と共通マクロ改変差、名目/実質乖離、F/N3の未較正・未実装を明確に分離**。3施策の比較条件が一致しない項目はN/Aと明示し、順位を強制しない。

同一初期値の既存F/N3比較を単にコピーした場合は「再計算」と称さず、再実行コマンド・実行ログ・年次CSV・差分・検証結果を残す。

## 6. Stage D：Claude独立検算用パケット（発出は別途）

3施策の結果が再現可能になった時点で、Claudeへ渡す**個別ファイルの検算パケット**を作成。内容：
- 3施策同条件の比較CSV、年次各ケース、ケース定義、モデル入力・参照固定Commit、隔離再現コード、再現コマンド、実行ログ、検証結果、実バイトSHA256・サイズManifest。
- Claudeへの短い検算依頼案（計算式、名目/実質変換、デフレーター、2026境界、イベント暦、SQ比較分母、差分・順位、SHA/サイズ、再現性、未知値を独立確認）。
- **Claudeによる検算実施・承認・回答をWorkが代行したと申告しない。** Ownerが後日別途Claudeへ発出する。レビュー制度の恒常化や追加承認ゲートを設けない。

## 7. 個別成果物と検証

保存先：`handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123/`。ZIPなし、個別原本：
1. `SPE_SQ_Baseline_And_Three_Scenario_Recalculation_Report_DRAFT_20261123.md`
2. `SQ_Common_Macro_Contract_And_Variant_Provenance.csv`
3. `SQ_Price_Event_Parameter_Trace.csv`
4. `SQ_Baseline_2026_2055.csv`
5. `SQ_Change_Candidates_And_Impact.csv`
6. `F_N3_SQ_Common_Condition_Compatibility.csv`
7. `SPE_Three_Scenario_Annual_Comparison_2026_2055.csv`
8. `SPE_Three_Scenario_Key_Years_And_Gaps.csv`
9. `SPE_Three_Scenario_Change_Attribution.csv`
10. `SPE_Three_Scenario_Case_Definitions.json`
11. `SPE_Claude_Independent_Recalculation_Request_DRAFT_20261123.md`
12. `SPE_Claude_Verification_Packet_Manifest.json`
13. 隔離実装/再現コード、必要入力、実行ログ、検証・事後保全記録。

検証：原本参照の固定性、初期値/遷移境界、予定/実適用イベント、価格キーの独立性、名目/実質会計式、共通医療・他共通モジュール一致、GDP分解残差、税・年金未採用診断の不混入、各年・各施策の入力一致、比較分母一致、再生成一致、固定Commit事後取得SHA256/サイズ照合。既存PASSは同一固定対象/条件なら再利用。

**実務完了条件：** 実原本回収→SQ限定修正または現行維持の根拠→F/N3共通接続→3施策の実行・検証→個別成果引渡し・事後保全。3施策が再計算できない場合は未完了と明記し、可能なStageの成果のみ引渡す。単なる資料作成や再現PASSだけを政策改善と評価しない。

## 8. 権限・STOP境界

本書をOwnerがWorkへ正式発出した場合に限り、固定原本の読み取り、隔離コードの作成・実行、上記新規ディレクトリへのcommit/pushを承認。**既存の共通エンジン、SQ/F/N3原文、既存成果、main、正式規範の直接変更は禁止**。必要な正式モデル変更・政策改訂・SQ採用契約は候補提示に留め、Owner判断を要する。PR/merge、正式Acceptance、Finding Close、DecisionLog更新、Freeze、Canonical化、HOLD解除は禁止。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。

GitHub引渡しの際は固定Commitから全成果原本を事後取得し、実バイトSHA256・サイズ・保存先を照合。条件成立時のみCUSTODY PASSとする。AI間で原本を引き継ぐ際、Claude自身による独立照合を要し、Workの申告をClaudeの自己検証PASSと扱わない。
