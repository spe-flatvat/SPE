# 再現手順

Python標準ライブラリのみ。実行中のネットワーク通信はない。

1. 本ディレクトリをRepository内の同一パスへ配置する。
2. `Fixed_Source_Expected.json` の各原本を記載固定Commitから接続済みGitHub連携で取得し、同一Repositoryパスへ置く。既存の原本があれば再利用する。大きいファイルのContents APIが空contentを返す場合は、記載Git blob SHAを `mcp__codex_apps__github_fetch` で取得する。認証のないHTTPS Git操作は不要。
3. Repositoryルートから `python handoff/chatgpt-f-foreign-workforce-policy-alignment-20261123/Recalculate.py` を実行する。53入力原本のサイズ・Git blob SHAを検証し、自らSHA-256を計算する。
4. `python handoff/chatgpt-f-foreign-workforce-policy-alignment-20261123/Verify_Reproduction.py` を実行する。別Pythonプロセス・一時ディレクトリへ全12経路を再生成し、すべての生成原本を実バイト照合する。

F_RETAINEDは6つの共通労働条件を再実行する。6診断枝はANNUAL_FINE_WEEK_HOURSだけで実行する。各枝・条件は30年次CSV、全体は360行。SQ/N3は固定成果を再利用し再計算しない。

一時的な全医療会計・全F行は比較CSV・労働トレース・外国人台帳へ必要項目を抽出した後、一時ディレクトリとともに除去する。計算結果・コード・定義・原文対応・検証は個別原本で渡す。ZIPは作らない。
