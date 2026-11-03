# SPE M19-IMPL-01｜05BQ 継続検証報告（LOCAL DRAFT）

**状態:** DRAFT／GitHub書込みなし／M19–25・RP-023 HOLD維持

## 1. 05BP未完走分の解消

05BP ZIPを展開し、テスト単位の逐次ログを記録して単一コマンド全件回帰を再実行。`python -m unittest discover -s tests -v`：**188/188 PASS、30.562秒、終了コード0**。前回の150秒上限到達は今回再現せず。前回の停止原因は特定できていない。

## 2. 追加異常系（05BQ）

`tests/test_strict_lease_boundary_05BQ.py` に3テストを新規追加。製品コードの変更なし。

1. 期限切れleaseを新所有者が取得した後、旧所有者によるreleaseが拒否され、新所有者の年度実行が成功する。
2. 不正TTL（0、負値、上限超過、boolean、文字列）が拒否され、leaseテーブルおよびトランザクションが汚染されない。
3. 所有者IDが同じでもgenerationが古いfenceは拒否され、annualが書き込まれない。

追加限定回帰：**3/3 PASS**。

## 3. 最終回帰

- 通常全件：`python -m unittest discover -s tests -q`、**191/191 PASS、29.951秒、終了コード0**。
- ResourceWarningエラー化：`PYTHONWARNINGS=error::ResourceWarning python -m unittest discover -s tests -q`、**191/191 PASS、29.642秒、終了コード0**。
- unittest収集：191件／ユニーク191件／重複0件。

## 4. 残存する境界

この結果はローカルSQLite fixtureの試験結果。複数ホスト、外部承認の真正性、実際の年度確定途中でのOSレベル強制停止まで保証しない。`m19_execution_api.py` のdocstringも、正規APIがPythonモジュール境界であって改変コードに対するセキュリティ境界ではないことを明記している。

## 5. 判定

**FULL REGRESSION PASS / WARNING CHECK PASS / LOCAL DRAFT**。Owner承認障壁なし。正式受入・Freeze・HOLD解除・GitHub書込みなし。
