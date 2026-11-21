# N3限定未接続領域・実装成果

DRAFT / NON-CANONICAL。政策値の採用・正式Acceptanceではない。

再現: リポジトリをcloneし、`python handoff/chatgpt-n3-gap-closure-20261121/Reproduce.py --outdir /tmp/n3-gap-reproduction`。Python標準ライブラリとGitのみ。必要な旧Claude原本は固定Commitをfetchし、一時的なdetached worktreeで読み取る。旧モデルは上書きしない。

- `Report.md`: 実行結果・進歩・OPEN・判断事項。
- `Gap_Model.py` / `Gap_Components.py` / `Gap_Inputs.json`: 実行コードと全候補設定。
- `Gap_Annual.csv`: 旧46＋新規候補の2026–2055年実行。全国PB・債務等の空欄は未接続であり0ではない。
- `SQ_F_N3_Comparison.csv` / `F_Reference_Annual.csv` / `Key_Years.csv`: 絶対値とSQ/F差。Fは固定参照、今回再実行したという意味ではない。
- `VAT_Price_Quantity_Income.csv`: 課税家計2市場の価格・数量・支出・企業売上・VAT・実質GDP。非家計税収等価ベースは実消費に入れない。
- `Partial_Fiscal_Financing.csv`: 部分政府収支と追加未配賦資金勘定の0/2/4%金利感度。全国財政閉鎖ではない。
- `Gap_Foreign_Bridge.csv` / `Gap_Semi_Medical.csv` / `Pension_Counterpart.csv`: 外国人材の限定VA接続と人口労働ブリッジ、半官営保険・年金資産相手方。
- `N3_Income_Distribution.csv` / `N3_Corporate_Accounts.csv` / `N3_Policy_Accounts.csv`等: 旧部品の回帰結果＋新候補詳細。
- `Sensitivity.csv` / `Interactions.csv`: 感度、削除限界差、差分差。単独差の和を因果寄与としない。タイミング不一致の診断は名称に明記。
- `Research_and_Boundaries.md` / `Dependency_Pins.json`: 固定原本と調査・未接続境界。
- `Checks.json` / `Execution.log` / `Replay.log`: 実装者検査・実行ログ。独立検算ではない。
- `Manifest.json` / `Delivery_Verification.json`: 実バイトSHA-256・サイズ・保存先とGitHub固定Commit事後照合。

数値は兆円/年（特記の人数・円・比率・ストックを除く）。quantity_nominal_volume_deltaは当年デフレータ単位の旧税込基準価格数量変化で、当年税込支出差とは異なる。DIと世帯分布は代理・合成値。外国追加人口/有効労働は別列ブリッジで、共有SQ人口モデルを変更した値ではない。

RP-023／M19–25 HOLD、RP-024 PENDING、政策原文・正式承認状態を維持。ZIPなし。
