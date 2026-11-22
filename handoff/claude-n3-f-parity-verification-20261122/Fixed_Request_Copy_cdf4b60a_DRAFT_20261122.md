# SPE｜Claude限定独立検算依頼：N3 F相当動学接続拡張（2026–2055）

**Status:** OWNER-REQUESTED / LIMITED INDEPENDENT VERIFICATION / DRAFT / NON-CANONICAL
**Date:** 2026-11-22
**Repository:** `spe-flatvat/SPE`
**Main target fixed commit:** `37c3399f9c553673a79ba1298fc68d758a77055e`
**Main target directory:** `handoff/chatgpt-n3-f-parity-implementation-20261122/`
**Claude output branch:** `work/claude-handoff`
**Claude output directory:** `handoff/claude-n3-f-parity-verification-20261122/`

## 1. 目的と境界

ChatGPT WorkがN3のF相当機能として追加した**新規24ケースと新しい年次動学経路**を、実装者のVerify.py・280,883 PASS申告から独立に検算する。既存79ケースの回帰、4年金帰属、国地方条件付き財政への接続が壊れていないことも検査する。全施策の再レビュー、SQの成長バフ疑惑や全シナリオGDP縮小の共通マクロ全体診断、モデル再設計、政策係数の較正・正式採用は今回の対象外。検算で見つかった明白な不具合は報告するが、主対象原本は修正しない。

「F相当」は**計算機能・年次伝播・検証可能性の水準**を意味し、GDP値の一致・政策効果の同等性・N3全施策の全国実装完了を意味しない。既存Fも暫定未較正である。

## 2. 取得・固定参照

**主対象（ディレクトリ一覧から全69原本を確認し、必要な原本を取得）**
https://github.com/spe-flatvat/SPE/tree/37c3399f9c553673a79ba1298fc68d758a77055e/handoff/chatgpt-n3-f-parity-implementation-20261122/

優先取得：`Report.md`, `Manifest.json`, `Source_Identity.json`, `Inputs.json`, `Components.py`, `Model.py`, `Macro_Adapter.py`, `Fiscal_Adapter.py`, `Package.py`, `Results.py`, `Reproduce.py`, `Verify.py`, `Old79_Exact_Regression.json`, `Replay_Verification.json`, `Resolved_Macro_Source.py.txt`, `results/Verification.json`, `results/Policy_Implementation_Map.csv`, `results/SQ_F_N3_Annual_Comparison.csv`, `results/Key_Years.csv`, `results/Sensitivity.csv`, `results/Conditional_National_Local_Fiscal.csv`, `results/Old79_Changed_Cells.csv`, `results/Annual_*.csv`, `results/*_Corporate_Funding_Stock.csv`, `results/*_Dynamic_Base_Audit.csv`, `results/*_KPI_Events.csv`。実際のファイル名・個数はGitHub一覧とManifestを正とし、推測した名前の404でSTOPしない。

既存固定参照：
- N3旧79ケース：`556953292e24615cee47d92bb27e85badf12329c` / `handoff/chatgpt-n3-gap-closure-20261121/`
- 年金4帰属修正：`76176ae118ee073677e990c0d8c4cfa498e3563d` / `handoff/chatgpt-n3-pension-counterpart-20261121/`
- 国地方条件付き財政：`747273674daed0d648c58aa8fdc07ebe203e6046` / `handoff/chatgpt-national-fiscal-closure-20261121/`
- Claude旧財政検算：`fffea93870e2e04a0f750ed8352c1bdcdee28afe` / `handoff/claude-national-fiscal-verification-20261121/`（62/62 PASS_WITH_LIMITATIONSは旧固定版限定）
- F比較：`ff6210061615105de9a0d64767c256796be80ed2`（固定参照、今回F未再実行）。F暫定動学資料は`handoff/f-macro-dynamic-20261116/`、DM04/05は`handoff/f-macro-dynamic-dm04-dm05-20261117/`。
- N3原文：`policies/New3linesPolicies.md`。政策原文を変更しない。

## 3. 独立検算項目

1. **固定原本・再現:** Manifestの各原本SHA-256・サイズを実バイトで照合可能な範囲で確認。Workの`Delivery_Verification.json`と`Verify.py`のPASSは申告として扱い、独立PASSの根拠としない。固定依存・Python環境を自力取得して`Reproduce.py`の再実行を試み、4帰属×103ケース×30年＝**12,360ケース年**と主要CSVの数値/実バイト一致を記録。全件不可でも取得済み原本で独立検算を進める。
2. **旧79ケース回帰:** 旧79×30年×4帰属の旧184列、**436,080セル**が旧固定版と一致することをClaude自身が照合。新24ケース・修正前出力と混同しない。初回実行→改革前所得税基礎修正→再実行の経緯を追い、修正後のみが最終成果であることを確認。
3. **前年所得/企業利益の動的基礎:** 前年賃金/SQ賃金・前年GDP/SQ GDPに応じた家計税・保険料減免・年金拠出・法人利益の倍率を、独立式で複数年・複数候補再計算。改革後税と改革前税の**双方**が同じ所得基礎に更新され、マクロ税収へ税差分だけ渡るか。2026初期条件、2027以降の一期間遅れ、SQ分母0/欠測、符号・単位・二重計上を確認。
4. **企業資金と投資・資本:** 税減額→配当/投資/残余配賦、企業現金期首＋流入−流出＝期末、投資平滑化、投資開始年、減耗付き資本→翌年供給能力、需要と供給制約の接続を独立に検算。企業勘定に表示した投資をGDP/資本へ再加算していないことを検査。NO_CARRY等の診断例外は仕様どおり扱う。
5. **2035 KPI・自動調整:** 2034/2033実行所得proxyを参照した2035判定、所得成長未達でVAT引上げが15%で停止する高閾値候補、低閾値の非発火、判定時期・将来波及を独立に確認。所得proxyは実測中央値でない。外部ジニ観測による軽減候補は外部入力時のみ、保険運用不振は競争シグナルのみで架空のGDP効果を生んでいないか。
6. **4年金帰属・保険者・国地方財政:** LEGACY / DOMESTIC_TRANSFER / FOREIGN_INCOME / ADDITIONAL_VAの4候補を未採用のまま保持。基金拠出・運用益の相手勘定、保険者/政府移転中立、VAT・法人・所得税一回計上。新マクロ出力から`Fiscal_Adapter.py`経由で条件付き国地方PB/債務へ渡る値を独立照合し、全国一般政府PB/債務・実際の国債発行/償還のnullを維持しているか。
7. **主要年・感度・比較限界:** 2026/2035/2045/2055のSQ・F固定参照・旧N3複合・新PARITY_CONNECTED_CANDIDATEを再集計。報告値（実質GDP兆円）2026全580、2035 SQ539.172/F547.910/旧498.602/新499.271、2045 SQ533.524/F544.461/旧480.604/新481.331、2055 SQ528.962/F540.275/旧480.747/新481.331の再導出と丸めを確認。MPC/投資率/開始年/減耗/労働/資本持越しの感度で変化が適切な年・経路へ出るか。Fは固定参照で未再実行、政策範囲非同質、未較正のため因果的な優劣順位を付けない。
8. **未実装境界:** `Policy_Implementation_Map.csv`と原文を突合し、インボイス全国費用、共済広域化、スマート・シュリンク、EITC比較基準、外国人材追加社会費用、全国ジニ・中央値、全控除廃止税源等のOPEN/PARTIAL/STRUCTURE_ONLYが完成扱いされていないか。F相当「主要機能」とN3全国量的「全施策完成」を区別。

**独立性:** 既存モデルの実行は再現性確認として可。ただし新計算経路の重要な恒等式・KPI・税差分・企業資金は、可能な限りClaude独自の計算コード/式でCSVから再導出し、実装者Verify.pyの呼出しだけでPASSにしない。全セルを検証できなければ実測範囲を明示。数値誤差許容・比較対象の定義を記録。

## 4. 判定・成果・権限

各項目と総合を **PASS / PASS_WITH_LIMITATIONS / FAIL / NOT_VERIFIED** で評価。FAILがあればケース・帰属候補・年・列・期待値/実測値・最小再現手順を記す。未較正/未実装の政策効果は算術バグと混同しない。重大論点は優先度順に最大5件。SQバフ疑惑と全施策GDP低下は**次工程の診断対象として引継ぎ事項に記すだけ**で、今回の全体診断・修正を要求しない。

成果物を**個別原本**として`work/claude-handoff`の新規`handoff/claude-n3-f-parity-verification-20261122/`へ格納：
- `SPE_N3_F_Parity_Limited_Independent_Verification_Report_DRAFT_20261122.md`（総合判定、検証範囲、数値、差分、未完了、次工程への限定引継ぎ）
- Claude独自の検算コード、必要な結果CSV/JSON、実行ログ
- 固定参照と実バイトSHA-256/サイズの証拠表、格納後の事後取得照合記録（できた範囲）

ZIP禁止。GitHub書込みは**Claude側新規handoffのみ**。主対象・政策本文・main・他AIブランチ変更禁止。最終固定Commitからの事後取得と実バイト照合が成立したファイルに限りCUSTODY PASS。GitHub格納不能時は成果本文・制約を報告し、成功と装わない。

RP-023／M19–25 HOLD、RP-024 PENDING、正式Acceptance、Finding Close、DecisionLog、Freeze、Canonical化、未採用政策条件は維持。追加の4AIレビュー制度・Owner裁定・承認ゲートを作らず、**取得→独立検算→成果引渡しを一括実行**する。
