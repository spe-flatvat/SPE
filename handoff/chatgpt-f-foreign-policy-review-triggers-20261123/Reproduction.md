# 再現手順

Python標準ライブラリのみ。計算時にネットワーク通信はしない。

1. 本成果ディレクトリをRepository内の同一パスへ置く。
2. `Fixed_Source_Expected.json` の固定原本を記載Commit・パスから接続済みGitHub連携で取得し、同一Repositoryパスへ置く。既存原本は再利用する。大きいファイルのContentsが空contentならGit blob SHAを用いた連携取得へ切り替える。認証のないHTTPS Git操作は不要。
3. `python handoff/chatgpt-f-foreign-policy-review-triggers-20261123/Recalculate.py` を実行する。固定原本のサイズ・Git blob SHAを自己検証し、SHA-256を計算する。6共通労働条件それぞれでFを警戒前・後の2経路実行する。
4. `python handoff/chatgpt-f-foreign-policy-review-triggers-20261123/Verify_Reproduction.py` を実行する。別Pythonプロセス・別一時ディレクトリへ全生成原本を再生成し実バイト照合する。

各条件は30年次の警戒指標CSV・比較CSV、全体では警戒180行・F/SQ/N3比較180行。実行は12経路×30年＝360年次。非採用の受入制限6枝×30年は固定結果をそのまま再利用する。

人口比の初回逸脱年はその時点までの履歴で計算するため、発動前の年には将来の初回年を先取りしない。全期間の初回年と累積発動年数は `First_Warning_And_Duration.csv` に集計する。GDP比正式判定の空欄はN/Aを意味し、`gdp_formal_status` に理由を記載する。

一時的な全F出力・全医療会計は前後7原本の実バイト一致確認後、一時ディレクトリとともに除去する。個別成果原本はCSV、実装コード、入力固定情報、清書留意事項、報告、検証、Manifest、保全記録である。ZIPは作らない。
