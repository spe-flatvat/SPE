# 再実行・ファイル案内

DRAFT / NON-CANONICAL。Python 3.10以上、標準ライブラリのみ。個別ファイルで取得し、ZIPは使わない。

## 取得と実行

本ディレクトリの原本を取得し、同じリポジトリ内で次の依存3件を所定位置に置く。

- `handoff/f-vat-core-20261120/Model.py`
- `handoff/f-vat-core-20261120/Inputs.json`
- `handoff/f-vat-core-20261120/Annual.csv`

依存3件の固定Commitは `76aca9274151139cf0791365f5f9307fcc6f8fa6`。サイズ・SHA-256はInputs.json。モデルは起動時に照合する。VAT Inputs内の圧縮埋込み原本は既存ローダーがサイズ・SHAを検証する。依存は既存Python/JSON原本の内部表現でありZIP配布ではない。

```bash
python handoff/f-integrated-20261121/Model.py handoff/f-integrated-20261121/Inputs.json --outdir replay-integration
python handoff/f-integrated-20261121/Verify.py
```

既存成果を上書きしないよう別outdirを使う。Verify.pyは一時ディレクトリで全再計算し、11出力を原本と実バイト比較する。依存原本が欠けた場合、欠けたパスを取得して同じ配置へ置く。固定版の混用は避ける。

## 出力

|ファイル|内容|
|---|---|
|Model.py／Inputs.json|統合実行と条件・接続変更、固定依存3件|
|Dependencies.json|回収済み96原本の固定参照・SHA、Stage2照合|
|Annual.csv|37条件×30年=1110行。34再計算条件＋SQ＋旧F固定＋VAT固定|
|Comparison.csv／Summary.csv|F−SQ、旧F・直近VAT差、主要年|
|Fiscal.csv／Fiscal_Comparison.csv|部分政府・保険者・統合収支、税収・保険料・給付・内部移転・未充当|
|Household.csv|現金／現物／価格分離、macroと合成microの差額|
|Income_Groups.csv|所得階層別A/B/C・税控除・保険料。年金等の未配賦を捏造しない|
|Labor.csv|国内・外国・高齢者・年金の頭数と実効投入|
|Policy_Effects.csv|6施策の単独効果と全部実施時の限界効果|
|Interactions.csv|8相互作用群、計算ゼロと未算定を区別|
|Policy_Map.csv|実装・固定暫定背景・未実装・未較正|
|Report.md|数値・会計範囲・前回差・解釈・限界|
|Validation.json／Verification.json／Verify.py|内蔵恒等式、新規接続対照試験、再実行一致|
|SHA256SUMS.json|原本サイズ・SHA-256、自分自身を除く|
|Delivery_Verification.json|格納後に追加する固定Commit事後取得照合|

## 比較上の注意

FULL_DIRECTは追加Cなし、FULL_ADDITIONALは未裁定追加C候補、FULL_POOLは追加公的原資内、FULL_OLD_Cは前回税率軽減額算式。LOW/HIGHは前回VAT感度の同じ係数組合せ。E/F/PEN/A/B/VATは高齢者・外国人材・年金・保険料軽減・現物給付・VAT。ONLYとCHANNELS_OFFは他の旧F暫定背景を共通に保持する識別条件。

REPLAYは新しい外国人cash接続をOFFにした直近固定版の再現。これを新モデルの改善効果とは呼ばない。旧F／VAT_FIXED参照は保存結果の引用で、新しい財政総額を推定していない。

全国税収・年金・保険料・中央地方収支・PB・国債を閉じるデータはない。部分proxyとA/B/C未充当を正式財政赤字・新規国債と同一視しない。実測DI／賃金／国民所得分配の推計ではない。
