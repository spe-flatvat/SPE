# 再実行手順・独立性の範囲

Python 3.10以上、標準ライブラリのみ。原本・共通基盤は変更しない。ZIPを作成しない。

固定Git objectを取得し、別のdetached worktreeを用意する（既存作業treeをresetしない）。

```bash
git fetch origin 3c77eafc2073fdaba4c129164817d2f57c9421b9
git fetch origin ff6210061615105de9a0d64767c256796be80ed2
git fetch origin 8437d285b179e30a9a93236cafe56daa4b571791
git fetch origin 4924c8e4be45e1f0b66013ef4aa87d139ff7c7b5
git fetch origin 5804388482864af08204ba0d0e76a46206dacdbd
git worktree add --detach /tmp/spe-n3-verification-source 3c77eafc2073fdaba4c129164817d2f57c9421b9
git worktree add --detach /tmp/spe-n3-fixed-engine ff6210061615105de9a0d64767c256796be80ed2
```

以下は成果ディレクトリから実行する。OUTは新たな出力先の絶対パスとする。原本成果を上書きする場合、従前のCUSTODY記録は変更後出力の根拠にならない。

```bash
export PYTHONDONTWRITEBYTECODE=1
python /tmp/spe-n3-verification-source/handoff/claude-n3-model-draft-20261121/SPE_N3_Medical_On_CommonSQ_Draft_DRAFT_20261121.py /tmp/spe-n3-fixed-engine /tmp/spe-n3-replay > Replay_Run.txt 2>&1
python -I /tmp/spe-n3-verification-source/handoff/claude-n3-model-draft-20261121/SPE_N3_Draft_Checks_DRAFT_20261121.py /tmp/spe-n3-fixed-engine /tmp/spe-n3-replay > Claude_Checks_Reexecuted.txt 2>&1
python Independent_Verify.py /tmp/spe-n3-verification-source /tmp/spe-n3-fixed-engine "$PWD" > Independent_Run.txt 2>&1
python Supplementary_Verify.py /tmp/spe-n3-verification-source /tmp/spe-n3-fixed-engine "$PWD" > Supplementary_Run.txt 2>&1
python Build_Report.py
```

Independent_Verifyは観測用ラッパーでMedicalのインスタンスとVAT呼出引数/出力を捕捉するが、原本ファイルや戻り値は変更しない。ターゲットをもう一度実行し、14条件を保存後、独立閉形式で請求/上限/多数回/年額上限、通常医療量、公費/保険者/家計、共通の限界請求、財源、VAT取引を検算する。再利用した元コードの自己検査とは別。

独立算術は人口/年齢費用比（固定Demand関数）、価格指数、所得比率、費用候補、共通プログラム費/保険外現金台帳を共有入力にする。通常医療の請求関数は呼ばず、データを用いて別式で集計。共通の資源配分は別閉形式と直接境界呼出で確認する。VATは実行されたSQ条件（課税範囲拡大なし、仕入控除回復なし、数量弾力性0）に代数的に縮約した独立式を使用。別設定への一般的妥当性は主張しない。

共通請求のU15をPRESCHOOLへ対応づける粗い年齢代理や、高額療養費の世帯/所得/年額適用等の近似も継承する。ONLY_CURRENT_30はこのモデル区分内での感度で、現実の全年齢・所得の受給者を正確に抽出したものではない。動学マクロ全体・法令/外部統計・N3未実装施策の独立検証は対象外。

Supplementary_Verifyは負担額補間と率補間の違い、固定SQ360セル、ログ3節、固定政策原文/仕様/指示/既存Claude報告の取得同一性、作業tree不変更を確認する。異なる補間方式は検算用候補で、政策採用でも素案修正でもない。

ManifestはDelivery_Verificationと自身を除く各原本のサイズ/SHA。GitHub格納後の原本固定Commit・事後取得照合はDelivery_Verification.json。照合記録自体は後続記録Commitからも取得確認し、無限に自己参照するManifestは作らない。
