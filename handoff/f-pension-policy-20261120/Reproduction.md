# 再実行・検証

DRAFT / NON-CANONICAL。標準Python 3.10以上、追加ライブラリ・実行時ネットワーク不要。

```bash
cd handoff/f-pension-policy-20261120
python3 Model.py Inputs.json --outdir replay
python3 Verify.py
```

ModelとInputsに固定依存コード・入力・旧比較CSVが埋め込まれているため、このディレクトリの個別ファイルだけでも実行できる。圧縮はJSON内の依存ソース符号化でありZIP配布ではない。出力先は既存固定成果から分離する。Inputsの候補条件を変える場合は別版へ保存し、元のSHA一致を主張しない。

生成される8計算出力：Annual.csv、StatusQuo.csv、Comparison.csv、Summary.csv、Interactions.csv、Public_Strata.csv、Private_Distribution.csv、Validation.json。Validationはローカル検証結果であり、GitHub格納・保全PASSではない。

Verifyは手計算の支給停止例・国税例、全年の給付・保険料・資産勘定、70歳以上保険料ゼロ、人口・外国人不変、ゼロ就業・ゼロ拠出・全額振替・下振れの対照、相互作用を確認する。さらに一時フォルダへ全条件を再実行し、8出力が実バイトで一致することと、SHA256SUMS.txtに列挙された原本を検証する。SHA256SUMS自体は自己ハッシュ対象外。

旧結果の維持：入力にある固定外国人モデルを再実行し、SQ_HIST、HIST_ZERO、HIST_COMBINED_MEDIUMの30年×7項目=630セルを旧CSVと照合。年金ゼロの2背景×30年×6集計項目=360セルを旧エンジンと照合。計990セル。旧PASSの条件を越えて全国の政策効果を実証したとは扱わない。

基準の外国人係数・高齢者率・初期GDP・他F施策は変更しない。年金候補の開始年・閾値・追加枠・反応・純貯蓄割合・運用率・新規加入・給付税率をInputsで変更できる。未算定の全国総額を埋めるオプションはない。

引渡しは `work/chatgpt-handoff` の新設フォルダへ限定。非強制ref更新で取得時HEADを照合し、既存全ファイルを維持する。格納後に新規取得した固定Commitの各成果物についてサイズ・SHA-256をローカル原本と比較する。事後照合前にはCUSTODY PASSを宣言しない。公的Web原本の恒久保全・正式採用はこの検証には含まれない。
