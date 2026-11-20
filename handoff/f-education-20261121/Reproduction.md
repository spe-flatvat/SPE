# 再実行・成果物

Python 3.10以上、標準ライブラリのみ。DRAFT / NON-CANONICAL。ZIPは使用しない。

依存原本6件はInputs.jsonのruntime_dependenciesに固定Commit・サイズ・SHAを記載。リポジトリ内の同じ相対パスに個別取得する。既存integrationとVATの各Model.py／Inputs.json／Annual.csvが必要。旧依存原本は上書きしない。モデルは起動時と既存入れ子ローダーで原本を検証する。

```bash
python handoff/f-education-20261121/Model.py handoff/f-education-20261121/Inputs.json --outdir replay-education
python handoff/f-education-20261121/Verify.py
```

|ファイル|内容|
|---|---|
|Model.py／Inputs.json|教育コーホート・国債・既存統合接続、全候補パラメータ|
|Annual.csv|24条件×30年=720行、旧基準・SQ固定参照含む|
|Education.csv|教育・奨学金・訓練・人的資本・財源全分解|
|Education_Investment.csv|教育サービス・施設・置換・教員費用換算|
|Scholarship.csv／Scholarship_Groups.csv|既存上積み、新規・継続、進学・修了、消費・借入・貯蓄、合成所得区分|
|Corporate_Training.csv|既存費用、追加費用、税控除、参加回数・時間|
|Human_Capital.csv|技能・実効労働・賃金・GDP、旧Hとの区別|
|Fiscal_Bonds.csv|追加費用・税収フィードバック、国債発行・償還・残高・利払い|
|Comparison.csv／Summary.csv／Interactions.csv|旧維持・旧除外・新置換、単独・複合・感度・トリガー|
|Sources_and_Map.md／Dependencies_and_Sources.json|政策・制度・統計と実装対応、取得経路と実バイト記録|
|Report.md|数値・解釈・較正限界|
|Verify.py／Validation.json／Verification.json|新規接続・独立国債例・ラグ・トリガー・12出力完全再実行一致|
|SHA256SUMS.json|個別原本のサイズ・SHA、自分自身を除く|
|Delivery_Verification.json|格納後に追加する固定Commit事後取得照合|

LEGACYは旧教育維持、LEGACY_EXTRA_ZEROは旧経路に新効果ゼロ、REPLACED_ZEROは旧教育・訓練human経路も外した基準。COMBINEDは新教育3施策へ置換、C追加給付候補／既存外国人・年金MEDIUM。COMBINED_DIRECT_CとCOMBINED_POOL_CはC解釈の別条件。LEGACY_LEVEL_HYPOTHESISは原文のGDP0.3%・賃金0.2%という旧水準仮定を別にONにした参照で、新モデルの較正対象ではない。

AUTOは判定年の前年モデル成長を使う候補、EXTERNALは外生値。2035成長で2036発動する別条件も実行する。原文未確定の制度仕様を正式採用しない。未算定の純授業料・ユニーク訓練人数・全国国債・PB等は空欄。政策別債券残高と未充当cashを全国財政見通しと呼ばない。
