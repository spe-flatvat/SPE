# 再実行手順

DRAFT / NON-CANONICAL。Python 3.10以上・標準ライブラリのみ。リポジトリルートから実行する。

```bash
python handoff/f-medical-corrected-integrated-20261121/Model.py handoff/f-medical-corrected-integrated-20261121/Inputs.json --outdir handoff/f-medical-corrected-integrated-20261121
python handoff/f-medical-corrected-integrated-20261121/Verify.py --replay
python handoff/f-medical-corrected-integrated-20261121/Results.py
```

Inputs.jsonの固定依存12原本とその既存入れ子依存を同じパスへ置く。load時にサイズ・SHA-256を検証する。旧医療・教育原本を上書きしない。ModelはGDP差分の足算ではなく、教育/VAT/外国人/年金/高齢者/家計の既存年次エンジンの同一年内フローを置換し、資本・消費状態を30年連鎖で再実行する。

既存Claude検算報告・2スクリプト・出力はClaude_接頭辞で保存。Source_Reuse.jsonの取得元固定Commitとサイズ・SHAで同一性を記録し、過去PASSを再利用する。旧スクリプトは旧医療固定版専用で、新修正版への独立検算PASSを主張しない。

CommonEndOfLife.calculateはFモデルをimportしない。payer_calculatorの省略時は呼出側の明示配賦、F接続時は同一患者の年齢/所得/episode月額と高額上限を通す。universalの増分は既存請求に追加した限界差で計算し、別請求として上限をリセットしない。共通関数の異なる需要・能力・配賦での実呼出テストを保存する。N3等フルモデルは作らない。

主要入力：Inputs.defaultsのdemand_mode/payer_mode/universal_palliative/medical_import_share/medical_intermediate_share/medical_VA_scale/medical_displacement_share/finance_fraction/finance_mix/medical_debt_rate、common_overridesの家計単価・率。未指定共通デフォルトはCommonEndOfLife.pyの明示値で、全て未較正候補。最新Fと呼ぶLATEST_FはVA尺度50%・財源対応50%の感度ラベルであり正式採用値でない。VA尺度は輸入/中間控除後の比率へさらに掛かるため、VA100でも支出額100%のGDP算入ではない。

医療財源債はプログラム増分のみ。負の財源必要額は税/保険料軽減、他支出拡大、当該債償還/資産積立として対称に扱う。全国債務や国債発行と呼ばない。利払いは既存債残高×候補2%、債権者受取は域外/未配分の金融所得として別勘定、家計への自動再配分なし。固定SQは共通OFFであり共通政策込みの他セット比較ではない。

成果：Annual/Comparison/Summaryは統合値、Demography_Demandは年齢/日本人外国人/候補episode、Medical_Accounts/Common_EndOfLife/Household/Fiscalは経路別、Household_Sensitivityは主感度幅、VAT_Medicalは医療量反応、Education/Laborは既存接続、Policy_Effectsはfull-minus-off限界差、Interactionsは共通×Fと教育×医療/VAT×医療、Claims_Examplesは代表請求、Policy_Mapは実装/代理/未較正/未実装。Resultsは需要差・GDP分解・結果診断・短報を生成。Manifest/Delivery_Verificationは個別原本保全。
