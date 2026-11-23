# 再現手順

本成果は DRAFT / NON-CANONICAL。Python標準ライブラリのみを使用する。

1. 本成果ディレクトリをRepository内の同じパスへ置く。
2. `Fixed_Source_Expected.json` の各原本を記載Commit・パスから接続済みGitHub連携で取得し、Repository内の同じパスへ置く。大きい原本はContentsの空contentを採用せず、Git blob SHAの取得を使う。既存checkoutを使う場合も次のコードが実バイトを検証する。認証のないHTTPS Git操作は不要。
3. Repositoryルートで `python handoff/chatgpt-f-policy-cohort-fte-20261123/Recalculate.py` を実行する。
4. `python handoff/chatgpt-f-policy-cohort-fte-20261123/Verify_Reproduction.py` で別の一時ディレクトリへ再生成し、全生成原本のSHA-256と実バイトを比較する。

外部APIやネットワーク通信は計算時に使用しない。既存エンジンと施策原本は変更しない。取得した原本のGit blob SHA-1とサイズを固定メタデータに照合し、SHA-256を自ら計算する。既存PASS件数は今回の新規検証件数に加えない。

`Annual_Comparison_All_Cases.csv` は6条件×30行。各条件ディレクトリの `Annual_Comparison_2026_2055.csv` は30行。`Key_Years.csv` は2026、2030、2035、2040、2045、2050、2055年を含む。

再計算の一時的な全医療会計・旧F再現出力は比較後に除去する。引渡し原本は年次比較CSV、最終Fトレース、接続入力、共通の政策基底台帳・実行ソース、対応表、検証記録である。Manifest・報告・保全記録は再計算数値とは別の引渡し原本として保持する。
