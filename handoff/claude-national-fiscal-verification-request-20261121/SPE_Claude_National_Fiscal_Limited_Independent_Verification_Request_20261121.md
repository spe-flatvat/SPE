# SPE｜Claude限定独立検算依頼：全国財政勘定接続・79ケース年次計算・SQ/F/N3比較

**Status:** OWNER-REQUESTED / INDEPENDENT VERIFICATION ONLY / READ-ONLY INPUT / DRAFT / NON-CANONICAL  
**Date:** 2026-11-21  
**Target:** Claude  
**Repository:** `spe-flatvat/SPE`  
**Input fixed commit:** `747273674daed0d648c58aa8fdc07ebe203e6046`  
**Input directory:** `handoff/chatgpt-national-fiscal-closure-20261121/`  
**Claude output branch:** `work/claude-handoff`  
**Claude output directory:** `handoff/claude-national-fiscal-verification-20261121/`

## 1. 目的と境界

ChatGPT Workが新規実装した国地方の**条件付き財政勘定接続**について、実装者の`Verify.py`/`Checks.json`のPASS申告をそのまま独立検算PASSにせず、原本から独立に会計恒等式・統計入力・ストック/フロー・旧版回帰・SQ/F/N3比較境界を検算する。政策の採用、一般政府財政の未接続部分の穴埋め、追加施策の実装、既存のRP-023レビュー制度の復活は目的としない。

特に2055年N3の**国地方債務0・追加現金資産524.610061兆円・純利払−7.657204兆円**は未較正税差分、2040年以降の名目据置、条件付き利率・現金ロールの産物である。**計算上の整合、統計境界、経済的妥当性、政策優位の主張を分けて評価**する。一般政府全国PB・債務・実際の国債発行/償還は未接続`null`のまま。日本語で「閉鎖」と呼ぶ際は「財政勘定の整合・接続」と明記し、行政機能の閉鎖と混同しない。

## 2. 固定参照原本

**今回の主対象（全50ファイルの一覧をまず取得）**  
https://github.com/spe-flatvat/SPE/tree/747273674daed0d648c58aa8fdc07ebe203e6046/handoff/chatgpt-national-fiscal-closure-20261121

優先読取：`Report.md`、`Accounting_and_Boundaries.md`、`README.md`、`National_Fiscal.py`、`Fiscal_Inputs.json`、`Reproduce.py`、`Verify.py`、`Checks.json`、`Runtime_Pins.json`、`Statistical_Source_Receipts.json`、`Statistical_Cell_Map.csv`、`Official_Fiscal_Baseline_2025_2040.csv`、`SNA2024_Sector_Snapshot.csv`、`Fiscal_Baseline_Annual.csv`、`National_Fiscal_Annual.csv`、`National_Fiscal_Mode_*.csv`、`National_Fiscal_Scenario_*.csv`、`Annual79_With_Fiscal.csv`、`Transfer_Audit.csv`、`Key_Years_Fiscal_Comparison.csv`、`Old_New_Column_Regression.csv`、`Manifest.json`、`Delivery_Verification.json`。公的統計xlsx4原本も同梱。ファイル名を推測して404となったらディレクトリ一覧・Manifestから自己探索する。

**先行固定入力・既存PASS：**
- N3年金修正版：`76176ae118ee073677e990c0d8c4cfa498e3563d` / `handoff/chatgpt-n3-pension-counterpart-20261121/`
- Claude年金独立検算：`fbcfa37a47239b4084498847f66316eccc67cd19` / `handoff/claude-n3-pension-counterpart-verification-20261121/`。57項目PASSは**年金修正版のみ**に適用。
- 旧N3 79ケース：`556953292e24615cee47d92bb27e85badf12329c` / `handoff/chatgpt-n3-gap-closure-20261121/`
- F固定参照：`ff6210061615105de9a0d64767c256796be80ed2`、正確なF原本パスは`Runtime_Pins.json`から取得。Fは今回再実行されていない。
- Work元指示：`93e77c97d271d03bdec9f9d177407ebe3c4b821f` / `handoff/national-fiscal-closure-work-20261121/SPE_Work_National_Fiscal_Closure_One_Run_Execution_Instruction_20261121.md`

## 3. 優先検算事項（新規財政計算に限定）

1. **原本・統計セル・境界：** 固定Commitの原本とManifest SHA/sizeを実バイトで照合可能な範囲で確認。2026年7月CAO国地方見通し（復旧復興/GX/AI半導体を含む現状投影）、FY2024 SNA/GFS中央/地方/社会保障基金/連結調整、MOF当初国債発行計画の出所・表・セル・年度・単位・会計範囲を独立に確認。公表推計/実績/シナリオ仮定を混同しない。2025末国地方債務1270.2兆円、FY2026末1304.3兆円、FY2026 PB−4.4兆円・純利払9.0兆円・財政収支−13.4兆円、残差SFA20.7兆円の計算・解釈を検証。SFAを財源・発行と誤称しない。
2. **独立会計恒等式：** 実装者`Verify.py`を唯一の検証根拠にせず、独立コード/式で`PB−純利払＝財政収支`、`期末債務＝期首債務＋借入−償還＋SFA`、現金資産・借入・償還ロール、負債/資産非負、税/VAT/相続/法人の再加算防止、既存医療/教育利払の二重計上防止を年・ケース・候補横断で確認。SNA/GFSの一般政府連結で部門間移転を相殺し、社会保険料と税の重複を検査。SFAの未配賦内訳は未解決として扱う。
3. **制度間移転と感度：** 保険者補填率0→100%で政府PBと保険者側が相殺され、既知連結一次収支は不変か。借換10→20%で候補総発行/償還のみ変わり、純債務・PBは不変か。利率0/2/4%、税feedback倍率0.5、2040年以降STRICT nullと名目据置、4年金帰属候補の影響範囲を確認。財政サテライトの新規計算がマクロGDPを再feedbackしていないことを明記。
4. **再実行・回帰：** 固定依存を使って`Reproduce.py`を可能なら実行し、79×30×4＝9,480マクロケース年、23,910財政行、旧184列436,080セル不変、追加73財政列、基本79×30＝2,370行を再計算/独立照合。既存Workの17ファイル実バイト一致と20出力再現性を、Claude自身が確認した範囲と申告引用に分離。再計算が困難でも取得済みCSVから独立検算できる項目は実行する。
5. **重要年・比較妥当性：** 2026/2035/2045/2055のSQ、固定F、N3のPB・利払・債務・現金資産・借入を再導出。特に2055 N3債務0・現金資産524.610061兆円・純利払−7.657204兆円の経路と仮定依存を検査。FY2026 CAO名目GDP689.3兆円対SPE 600兆円、SPE年→FY年の仮対応、F固定/政策接続範囲差、国地方候補と一般政府全国nullを区別し、政策優位や財政完全自律の実証と誤認させない。
6. **実装リスクの特定：** 正しい恒等式を満たしてもモデルの政策差分が国地方へ全額配賦される仮定、基準債務の利払比例縮減、SFA残差の据置/扱い、余剰資金の即時償還・現金蓄積、税源較正不足などが結果を過大/過小評価し得るか、**根拠付きで最大5件**の重大論点を挙げる。実証未了はバグと混同しない。

## 4. 判定と成果物

検算対象ごとに **PASS / PASS_WITH_LIMITATIONS / FAIL / NOT_VERIFIED** とし、数値・再計算コード・差分・根拠原本・未検証範囲を示す。最終総合判定も同じ4分類で示す。誤りがあれば最小再現例（ケース・年・列・期待/実測）と影響範囲を明記。独立検算で未実施のことをPASSとしない。**新たな政策裁定、全国一般政府完全整合、財政からマクロへのfeedback実装は依頼しない。**

成果は以下のように**個別ファイル**で`work/claude-handoff`の新規`handoff/claude-national-fiscal-verification-20261121/`へ格納する：
- `SPE_National_Fiscal_Limited_Independent_Verification_Report_DRAFT_20261121.md`（総合判定・論点・比較限界）
- Claude独自の検算コード（例：`Independent_Fiscal_Check.py`）と実行ログ、検算結果CSV/JSON（必要なもののみ）
- 原本・依存固定Commitと実バイトSHA-256・サイズ・検証対象範囲を示すManifestまたは簡潔な証拠表

ZIP禁止。可能なら最終固定Commitから保存済み原本を事後再取得して実バイトSHA-256とサイズを照合し、照合できた原本に限りCUSTODY PASS。レシートの自己参照を避ける。GitHub格納に失敗した場合は成果本文と具体的技術的制約を提示し、成功したと装わない。

**権限境界：** 主対象固定Commit・ChatGPT Work成果・既存政策原文の変更禁止。Claude側新規handoffへの成果格納のみ。RP-023／M19–25 HOLD、RP-024 PENDING、正式Acceptance、Finding Close、DecisionLog、Freeze、Canonical化、政策採用を変更しない。追加レビューやOwner承認待ちの工程を設けず、取得→独立検算→成果格納→報告まで一括実行する。
