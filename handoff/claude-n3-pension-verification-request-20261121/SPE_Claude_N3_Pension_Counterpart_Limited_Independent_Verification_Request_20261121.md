# SPE｜N3年金運用益相手勘定是正・79ケース限定独立検算 Claude実行依頼書

**Status:** OWNER-DIRECTED / LIMITED INDEPENDENT CALCULATION / DRAFT / NON-CANONICAL  
**Date:** 2026-11-21  
**Repository:** `spe-flatvat/SPE`  
**Reviewer:** Claude  
**Fixed target commit:** `76176ae118ee073677e990c0d8c4cfa498e3563d`  
**Target directory:** `handoff/chatgpt-n3-pension-counterpart-20261121/`  
**Output branch:** `work/claude-handoff`  
**Output directory (new):** `handoff/claude-n3-pension-counterpart-verification-20261121/`

## 1. 目的・権限・完了条件

ChatGPT Workが実装した**N3年金運用益の金融部門相手勘定の限定是正**について、Claude自身のコード実行と独立計算で会計・マクロ伝播・79ケース回帰・比較可能性を検証する。対象は2026〜2055年の79ケース×30年=2,370年次行、4帰属候補で計9,480行。前回ClaudeのN3 79ケース検算76項目PASSを同一固定範囲に限って再利用し、今回は**変更箇所と副作用**に集中する。

Ownerは固定原本の取得・ローカル再実行・独立検算コード/結果生成・指定Claude側GitHub新規ディレクトリへの書込みを承認する。入力原本・政策原文・他ブランチの改変、merge、正式Acceptance、Finding Close、DecisionLog更新、Freeze、Canonical化、HOLD解除は禁止。RP-023／M19–25 HOLD、RP-024 PENDING維持。新たな4AIレビュー、開始承認、手続文書を要求しない。

**完了条件:** 固定原本の取得と検証、主要な修正経路の独立算術検算、実コード再実行と旧版比較、限定評価、Claude側GitHub成果引渡し。既存テストを実行しただけ、報告書を書いただけでは完了としない。

## 2. 固定入力

1. **主対象:** Commit `76176ae118ee073677e990c0d8c4cfa498e3563d`、`handoff/chatgpt-n3-pension-counterpart-20261121/`。特に `Report.md`, `README.md`, `Comparability.md`, `Gap_Components.py`, `Gap_Model.py`, `Build_Results.py`, `Reproduce.py`, `Gap_Annual.csv`, `Candidate_Sensitivity_Annual.csv`, `Before_After_All79.csv`, `Before_After_Cell_Differences.csv`, `Pension_Source_Accounts.csv`, `Pension_Counterpart.csv`, `N3_Pension_Accounts.csv`, `Key_Years_Comparison.csv`, `Checks.json`, `Counterpart_Checks.json`, `Dependency_Pins.json`, `Manifest.json`, `Delivery_Verification.json`。実在名はREADME/Manifest/Git treeで確認し、必要な依存原本を自己回収。
2. **修正前79ケース:** Commit `556953292e24615cee47d92bb27e85badf12329c`、`handoff/chatgpt-n3-gap-closure-20261121/`。
3. **前回Claude検算:** Commit `cc032bcd6975105376e31fd00b9a00032d3c0b82`、`handoff/claude-n3-gap-independent-verification-20261121/`。76項目PASS、旧46ケース回帰の報告は同一範囲のみ再利用。実際のファイル名はGit treeから探索。
4. **共通F/SQ固定参照:** Commit `ff6210061615105de9a0d64767c256796be80ed2`、`handoff/f-common-endoflife-finalization-20261121/`。Fは今回再実行されていない。
5. **N3政策原文:** Commit `5804388482864af08204ba0d0e76a46206dacdbd`、`policies/New3linesPolicies.md`。

Workの引渡し記録は`Delivery_Verification.json`に**51 payload原本（Manifest含む）＋検証記録自身の計52ファイル**、固定Commitからの再取得とSHA-256/サイズ一致を報告している。Claude自身が実際に取得した固定原本を独立照合し、Workの申告を自己照合PASSと呼ばない。単一ファイル取得失敗で全体STOPにせず、取得可能範囲を維持する。

## 3. 重点検算（優先順位）

### A. 年金運用益の資金源・相手方・ストック/フロー

`Gap_Components.py` の変更箇所を旧版と差分で読み、拠出→基金資産→運用益→基金留保/給付→家計所得→消費→GDP/税の経路を独立に再構成。期首資産＋拠出＋運用益−給付＝期末資産、相手方負担と基金受取の対応、拠出の二重控除なし、当年運用益全額を家計消費したと誤認しないことを確認。資産評価益・海外所得・国内移転・金融サービス新規VAを混同せず、**国内移転だからGDP変化0に固定するのも、基金運用益を直接GDPから引くのも誤り**である点を検証。国内家計金融所得プールという仮定が実証済み相手方ではないことを明示。

4候補を独立確認：
- `LEGACY`: 源泉未配賦の再現対照。閉鎖済みと呼ばない。
- `DOMESTIC_TRANSFER`: 家計金融所得から基金への国内移転。国内新規一次所得0、家計消費の時点差によるGDP変化は可能。
- `FOREIGN_INCOME`: 海外純財産所得。国内GDP直接追加0、完全GNIは未実装。
- `ADDITIONAL_VA`: 新規国内サービスVAという反実仮想。根拠未確認で政策採用不可。

### B. 2055年主要数値・4候補の独立再計算

`N3_CONNECTED_COMPONENTS_A` 2055年実質GDP（兆円）を、固定原本の入力・式から別計算する：
- LEGACY `477.587252101`
- DOMESTIC_TRANSFER `475.923625914`（差 `-1.663626187`）
- FOREIGN_INCOME `477.587252101`
- ADDITIONAL_VA `480.566616773`（差 `+2.979364672`）

国内移転候補の2055税proxy差 `-0.710505920`、DI proxy差 `-5.763875768`、基金資産差 `0` も検算。`PENSION_COUNTERPART_R0` は全候補GDP `518.507629544`、`R0p02` は国内移転 `516.912231237`、`R0p04` は国内移転 `514.665206158`。旧R4−R0の `0.157022376`兆円は**旧利回り感度**であり、相手勘定修正額ではないことを確認。数値一致を修正の正当性そのものと同一視しない。

### C. 79ケース回帰・候補間不変性・再現性

旧79ケース×30年の旧列412,380セル中、**15ケース・330ケース年・8列＝2,640セル変化、409,740セル厳密一致**というWork報告を独立に比較。意図的変更列は実質/名目GDP、税proxy、消費proxy、部分連結収支、DI proxy、政策家計現金、全家計現金。利回り0・年金なし・開始前は一致、基金拠出・運用益・給付・資産・人口・医療・外国人材・税制設定は不変であることを確認。4候補×79×30＝9,480行の欠落・重複を検査。

README指定の `python handoff/chatgpt-n3-pension-counterpart-20261121/Reproduce.py --outdir /tmp/n3-pension-reproduce` を可能なら実行。元の23 CSVの実バイト一致を照合し、環境パスなど非数値差があれば分類。Workの`Verify.py`や`Counterpart_Checks.json`を**独立検算の代用にしない**。数値一致と会計意味論を別々に判定する。

### D. SQ/F/N3比較可能性の限定確認

`Comparability.md`, `Key_Years_Comparison.csv`, `SQ_F_N3_Comparison.csv`を照合し、2026/2035/2045/2055の実質/名目GDP、消費、投資、税、DI proxy、年金/医療、PB/国債、人口/労働について、**直接比較可能／定義整合proxyで限定比較／比較不能**を独立に確認。特にN3 `macro_cash_DI_proxy_trn`とFのcash proxyは定義が異なり、同名直接比較は不可。Fは固定参照で今回の再実行なし。全国PB/国債はnull（PARTIAL_CLOSURE）、EITC・税源・外国社会費用・MPC/弾力性・健康QOL等はOPEN。政策優劣や正式採用を断定しない。

## 4. 判定・不一致時の取扱い

項目別に `PASS`、`PASS_WITH_LIMITATIONS`、`FAIL`、`NOT_VERIFIED` を付す。FAILならケース/年/列/期待値/実測値/差/再現方法/影響範囲を記載。係数未較正、相手方帰属未裁定、会計恒等式の不成立、コードバグを区別。実装を勝手に修正してPASSに合わせない。重大不一致があっても検算可能な他領域と成果引渡しは続け、修正は別途Ownerの指示を待つ。新規レビュー制度や形式的承認ゲートを追加しない。

## 5. Claude側GitHubへの実成果引渡し

**書込み先:** `work/claude-handoff` の新規 `handoff/claude-n3-pension-counterpart-verification-20261121/` のみ。既存原本・他ブランチ変更禁止。ZIP禁止。

最低限、(1)実際の独立検算を記述したMarkdown報告、(2)独立計算コードと再実行方法、(3)ケース/年/列ごとの検算数値・差分CSV/JSON、(4)再実行・回帰検査ログ、(5)個別原本のSHA-256・サイズ・保存先・固定Commit事後取得照合結果を個別ファイルで格納。

保存後に**Claude側の最終固定Commit**から成果原本を再取得し、ローカル原本との実バイトSHA-256・サイズを確認できた範囲でのみARTIFACT READY/CUSTODY PASSと宣言。対象の原本取得・独立実行・独立検算・成果保存・事後照合を区別し、未達があれば未完了と明記。

Ownerへの最終報告は、固定Commit・成果ディレクトリURL・独立検算項目数・PASS/FAIL・重要な差分・限定事項・次の最小アクションに絞る。N3完成、政策値採用、正式Acceptanceは宣言しない。
