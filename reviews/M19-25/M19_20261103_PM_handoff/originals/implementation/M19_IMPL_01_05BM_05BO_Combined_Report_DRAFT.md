# SPE M19-IMPL-01｜05BM–05BO 連続異常系検証報告（DRAFT）

**状態：LOCAL DRAFT / READ-ONLY GITHUB / NO OWNER DECISION**

## 実施範囲

05BJ–05BLローカルDRAFTを入力とし、`tests/test_process_recovery_adversarial.py` に5件のテストを追加。製品コード変更なし。

1. 別プロセスが未コミットのSQLite書込みを保持中に強制終了された場合、ロールバックされること。
2. 別プロセスが有効leaseを取得できないこと。
3. lease所有者交代後、旧workerのfenced recoveryが拒否され、新workerがPENDING attemptをFAILEDへ回復し、再試行可能なこと。
4. 年度確定後の孤立PENDING attemptは通常のpending recoveryで拒否され、明示的なfinalized reconciliationでのみ処理されること。
5. 旧workerが確定済み年度のreconciliationを実行できないこと。

## 実行証跡

- 追加5件の限定実行：**5/5 PASS**、1.372秒。
- 追加3件時点の全件回帰：**180/180 PASS**、30.330秒。
- 最終5件追加後の単一コマンド全件回帰：**182/182 PASS**、33.182秒、終了コード0。
- 実行コマンド：`python -m unittest discover -s tests -q`
- 最終ログ：`M19_IMPL_01_05BM_05BO_Full_Regression.log`。
- 中間の全件回帰は実行上限で中断したが、後続再実行で182/182 PASSを確認。

## 限界・残存リスク

- 実プロセス強制終了はSQLiteの未コミットトランザクションに対して実施。年度確定処理中のプロセスを厳密なタイミングで強制停止する試験ではない。
- 複数ホスト、分散DB、OSクラッシュ、ストレージ障害、実際のOwner承認真正性は未検証。
- テストはローカルfixture用の契約・入力を利用しており、本番運用適格性の証明ではない。

## 権限・状態

M19–25およびRP-023 HOLD維持。GitHub書込みなし。正式受入・Freeze・Owner裁定なし。
