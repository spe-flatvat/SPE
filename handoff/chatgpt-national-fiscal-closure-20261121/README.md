# 全国財政・年次接続の部分成果

DRAFT / NON-CANONICAL / PARTIAL_CLOSURE。Report.mdとAccounting_and_Boundaries.mdが計算範囲を定義する。全国一般政府完全閉鎖ではない。

```sh
python handoff/chatgpt-national-fiscal-closure-20261121/Reproduce.py --outdir /tmp/spe-national-reproduce
```

Python標準ライブラリとgit。4候補×79ケースを実際に実行し、財政計算を2回、回帰/恒等式/実バイト照合、比較表作成まで行う。固定依存はRuntime_Pins.json。Fは固定参照。Excel再抽出を行う場合だけopenpyxlが必要（Extract_Statistics.py）。再現は保全済み統計原本を使用し、更新され得るURLへ依存しない。

- National_Fiscal.py / Fiscal_Inputs.json: 新財政計算コードと全候補仮定。金融資産/債務/借換/税と保険者の会計経路を分離。
- Annual79_With_Fiscal.csv: 国内移転79ケース×30年、旧184列そのまま＋財政73列。一般政府のnational_PB_trn等はnull、国地方候補はfiscal_CL_*。
- National_Fiscal_Annual.csv: 国内移転79ケース＋F固定の基本候補。National_Fiscal_Mode_*.csv: 他の年金帰属3候補。National_Fiscal_Scenario_*.csv: 国内移転＋Fの財政感度6条件。計23,910行。巨大な単一原本にせず条件別の個別CSVで扱う。
- Fiscal_Channels_All_Modes.csv / Transfer_Audit.csv: モデル差分、既存利払除去、内部移転相殺。VAT・相続・法人税の診断列を再加算しない。
- Key_Years_Fiscal_Comparison.csv / Key_Year_Differences.csv / Pension_Mode_Fiscal_Comparison.csv: 2026/2035/2045/2055の絶対値とSQ差/F差。財政候補・proxy・固定F・未較正を明示。
- Old_New_All79_Comparison.csv / Old_New_Column_Regression.csv / Old_New_Macro_Changed_Cells.csv: 旧版対照。旧マクロ差分0は意図的で、財政計算からGDPへの未採用feedbackを追加していない。
- Official_Fiscal_Baseline_2025_2040.csv / Fiscal_Baseline_Annual.csv: 公表基準と明示的尾部候補。SNA2024_Sector_Snapshot.csvは年度2024の実績推計のみで将来SSA基準へ外挿しない。
- 個別xlsx4件 / Statistical_Source_Receipts.json / Statistical_Cell_Map.csv / MOF_Anchor_References.csv: 公的原本、取得経路、サイズ/SHA、Excelセルと定義対照。ZIPなし。
- Verify.py / Checks.json / Validation.log / 各Macro_Execution.log / Full_Reproduction.log: 実装者検証。既存Claude57PASSとは別。
- Manifest.json / Delivery_Verification.json: 個別原本SHA-256・サイズ、GitHub格納後の固定Commit再取得照合。自己参照を避け、事後レシートは自身のManifestから除外。

国/地方配賦、全国一般政府税/保険料/財政、実債券償還/発行、SFA、経済年度較正、外国社会費用等の未接続範囲を維持。RP-023／M19–25 HOLD、RP-024 PENDING、政策原文・正式承認状態は変更しない。
