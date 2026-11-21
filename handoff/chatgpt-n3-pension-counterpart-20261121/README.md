# N3年金相手勘定・候補計算成果

DRAFT / NON-CANONICAL。`Gap_Annual.csv` は国内移転候補79×30年。正式採用ではない。

リポジトリのこの成果Commitをcheckoutし、Python標準ライブラリとgitで:

```sh
python handoff/chatgpt-n3-pension-counterpart-20261121/Reproduce.py --outdir /tmp/n3-pension-reproduce
```

国内候補、既存挙動、海外所得、追加VA、国内候補の再実行を行う（79ケースを計5回）。固定素案を一時detached worktreeで取得。旧原本を変更しない。再現には同じリポジトリ内の固定依存が必要（Dependency_Pins.jsonとInput_Receipt.json参照）。生の単一候補実行は `SPE_PENSION_MODE=DOMESTIC_TRANSFER`（またはLEGACY/FOREIGN_INCOME/ADDITIONAL_VA）で Gap_Model.py に設定する。

- Report.md / Comparability.md: 原因、会計候補、定量差、比較可能性、OPEN。
- Gap_Model.py / Gap_Components.py / Gap_Inputs.json / Build_Results.py: 実行原本。Gap_Model変更はメタデータの固定参照化のみ、会計接続はGap_Components。
- Gap_Annual.csv: 国内移転候補79ケース×30年。
- Before_After_All79.csv / Before_After_Cell_Differences.csv: 全79ケース主要列差分と全変化セル一覧。新規会計列は旧版にないため変化セル一覧の分母に含めない。
- Candidate_Sensitivity_Annual.csv: 4帰属候補×79×30年=9,480行の主要結果。LEGACY再現は旧固定全列と一致し、完全原本はInput_Receiptの固定参照を再利用。
- Pension_Source_Accounts.csv / Pension_Counterpart.csv / N3_Pension_Accounts.csv: 相手方源泉・給付・資産・家計控除。源泉未配賦はLEGACYのみ。
- Key_Years_Comparison.csv / SQ_F_N3_Comparison.csv / F_Reference_Annual.csv: SQ差/F差、F固定参照。比較可能性の制限はComparability.md。古いSQ_F_N3_ComparisonのDI同名列の非対称性はReportで明示しKey_Yearsでは定義整合別列を使用。
- 詳細各CSV: 旧仕様を引き継ぐ検証勘定。全国PB/債務の空欄は0ではない。
- Verify.py / Evaluate.py / Checks.json / Counterpart_Checks.json / 各Execution.log / Replay.log: 実装者検査と再現ログ。
- Manifest.json: 原本SHA-256/サイズ。Delivery_Verification.json: 格納後固定Commitからの再取得照合（後続の検証レシートは自己参照を除外）。ZIPなし。
