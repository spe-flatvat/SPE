# 再実行

DRAFT / NON-CANONICAL。Python3.10以上、標準ライブラリ。リポジトリルートで実行する。

```bash
python handoff/f-medical-common-20261121/Model.py handoff/f-medical-common-20261121/Inputs.json --outdir handoff/f-medical-common-20261121
python handoff/f-medical-common-20261121/Verify.py --replay
```

Inputs.jsonの固定依存9原本と、既存入れ子依存を同じ相対パスで使用する。ロード時に固定実バイトを検証。原本教育モデルは改変しない。共通単独はCommonEndOfLife.calculate(year,demand,parameters,financing)で使用でき、Fモジュールをimportしない。

共通の単価・率の未指定値はCommonEndOfLife.py内の明示デフォルト（すべて未較正候補）。家計：保険外 病院20万/在宅25万/施設40万円、介護自己負担1万/8万/10万円、時給2000円、所得減割合40%、公認代理単価2万円、利用料1万円、低所得30%へ1万円補助、保証費回避3万円。変更2%/撤回1%、電子80%。人員換算：医師8時間/看護40時間、年間1600時間、24hチーム年100episode、研修は容量の2%。実測統計ではない。

Annual/Comparison/Summaryは統合結果、Common_EndOfLifeとHousehold_EndOfLifeは共通の過程と家計、Medical_Accounts/FiscalはFと共通の支払帰属、Household_Age_Incomeは代表請求、Education_Preservedは教育勘定、VAT_No_DoubleCountは既存税控除帰属。Policy_Statistics_Implementation.csvは対応表。Policy/Source_Retrieval.jsonは原本取得。ManifestとDelivery_Verificationは引渡し照合。
