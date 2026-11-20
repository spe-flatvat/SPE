# 再実行と検証

DRAFT / NON-CANONICAL。Python3.10以上、標準ライブラリのみ。実行時ネットワーク不要。

```bash
cd handoff/f-household-social-20261120
python3 Model.py Inputs.json --outdir replay
python3 Verify.py
```

Model.pyとInputs.jsonは固定年金モデル・入力・旧比較値を内包する。このフォルダだけでも再実行できる。元の固定成果を上書きせず別出力先を使う。

計算出力10件：Annual.csv、Household_Income.csv、Household_Detail.csv、Fiscal_Insurer.csv、Comparison.csv、Interactions.csv、Summary.csv、StatusQuo.csv、Triggers.csv、Validation.json。

Verify.pyは保険料勾配の手計算、統計原バイトSHAと五分位対応、所得階層集計と年次集計、家計消費・貯蓄恒等式、現物使途分解、政府＋保険者統合、補填率変更の移転相殺、基金50%・前年差・残高、ジニ厳密閾値、PP/相対率、C表示振替の追加効果ゼロ、全8条件の相互作用を確認する。別プロセスで53条件を完全再実行し10出力の実バイト一致、SHA256SUMSの一致を確認する。

旧基準はMM/ZZそれぞれOLDとEXTRA_ZEROの30年×6集計項目、計720セルを年金固定結果と照合する。M0は旧社会保障を外した新比較対照であり、OLD一致を要求しない。旧結果を再現したことを新しい政策数量較正の証明とはしない。

マクロ接続は年金適用後のエンジンのsocial部分を置換し、所得控除減等の直接税差を税診断へ渡す。保険者の全額補填前提の恒等式を未補填額を含む式へ一般化する。既存GDP式・供給制約・消費調整・VAT本体・人口・就業・年金条件は保持する。

候補パラメータはInputsのdefaults/casesで設定可能。変更時は別版へ保存し、旧出力と同一のSHAとはしない。NONEや空欄の未算定を推測で埋めない。年度料率年率化のStatutory_Examplesは説明用で、主計算は観測五分位負担を参照する。

引渡しはwork/chatgpt-handoffの新規フォルダ限定。更新前HEADを確認し非強制更新する。格納後の固定Commitから新規取得し、原成果サイズ・SHAを照合する。その記録は事後に追加するため、検証対象の原成果Commitと記録追加Commitは異なる。記録自体の保全は最終Commitから別に確認する。SHA256SUMSは自己ハッシュと事後追加の記録を対象外とする。
