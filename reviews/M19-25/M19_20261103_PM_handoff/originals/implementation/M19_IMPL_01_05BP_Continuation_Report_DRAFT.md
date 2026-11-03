# SPE M19-IMPL-01｜05BP 連続検証報告（LOCAL DRAFT）

**状態:** DRAFT / GitHub書込みなし / M19–25・RP-023 HOLD維持

## 実施内容

05BM–05BOのローカルDRAFTから継続。`tests/test_strict_fence_contract_05BP.py` に6件を追加した。製品コードは変更していない。

- fence=None、所有者ID空白、boolean世代番号、ゼロ世代番号、list型fence、余分な要素を含むtupleを検証。
- いずれも `ContractError` により拒否され、gates/attempts/annual/year_endの書込みなし、トランザクション未残存を確認。

## 実行証跡

1. 新規限定回帰：6/6 PASS。
2. 単一コマンド全件回帰：188/188 PASS、28.472秒、終了コード0。
3. `PYTHONWARNINGS=error::ResourceWarning` 全件回帰：188/188 PASS、29.659秒、終了コード0。
4. 再現性確認のための3回目の全件回帰：呼出し全体の150秒上限に達し、最終結果未取得。標準出力をリダイレクトしていたため中断位置は不明。**PASSと記録しない**。

## 判定

**FULL REGRESSION PASS (2 runs) / REPEAT RUN INCOMPLETE**。

上限到達の原因は未特定。3回目の実行中断を製品不具合またはテスト失敗と断定しない。次回はテスト単位の逐次ログを記録し、時間変動・外部プロセス待ちを切り分ける。

正式受入・Freeze・HOLD解除・GitHub書込みは実施していない。Owner承認障壁なし。
