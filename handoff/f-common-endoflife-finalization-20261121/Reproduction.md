# 再実行

DRAFT / NON-CANONICAL。Python 3.10以上、標準ライブラリのみ。リポジトリルートから実行。

```bash
python handoff/f-common-endoflife-finalization-20261121/Model.py handoff/f-common-endoflife-finalization-20261121/Inputs.json --outdir handoff/f-common-endoflife-finalization-20261121
python handoff/f-common-endoflife-finalization-20261121/CommonBaseline.py
python handoff/f-common-endoflife-finalization-20261121/Finalize.py
python handoff/f-common-endoflife-finalization-20261121/Verify.py --replay
python handoff/f-common-endoflife-finalization-20261121/ExtendedVerify.py
python handoff/f-common-endoflife-finalization-20261121/ReportResults.py
```

ReportResultsは通常のPython起動で実行（`-I`は使用しない）。旧Results.pyは新ディレクトリに採用していない。Inputs.runtime_dependenciesの12原本と入れ子依存は既存パスのまま必要。load時に実バイトサイズ/SHAを検証。旧版比較は固定6986bb7のf-medical-corrected-integrated-20261121/を使用。FinalizeはClaude固定995cbca9のgit objectを読むため、必要なら先に `git fetch origin 995cbca98935752234452c6a6760150e639b312d` を実行する。

FMedical → CommonInterface.run_common → CommonEndOfLife.calculate が実接続。呼出元が需要、費用、配賦、任意の患者請求関数を注入する。共通インターフェースは施策セットの名前によって挙動を変えない。N3等の値は呼出試験候補で政策採用値ではない。

既存55条件にはOVERLAP_EQUAL_ACCESS（移行は緩和対象の部分集合）とEXTRA_TRANSITION_RESOURCE（移行に追加1資源単位）、上限感度、episode1/3/6月、家計/VA/財源/普及感度を含む。いずれも未較正・Owner未裁定。Universal needは全episodeの70%候補で、本人意思確認に基づく移行候補全員を含むと仮定する。登録者と未登録者に同じ緩和提供確率を適用し、移行は明示意思要件を満たす提供者の部分集合に限る。

共通SQは既存SQエンジンに医療支出、家計現金、財源税・保険料、投資を注入して再実行。固定SQを上書きしない。SQ医療VAT数量・健康/QOLは未接続。Common_ON_F_SQ_Comparisonはこの接続範囲差を明示する。

Manifest.jsonはDelivery_VerificationとManifest自身を除く個別原本。Delivery_Verificationは原本Commitを固定して事後取得したサイズ/SHA照合を記録する。記録Commitは原本Commitと別。再実行で成果を変更した場合、以前の保全結果を新結果へ流用しない。
