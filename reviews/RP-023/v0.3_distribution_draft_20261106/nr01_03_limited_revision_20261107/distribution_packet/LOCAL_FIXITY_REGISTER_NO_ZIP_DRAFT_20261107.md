# SPE RP-023 v0.3｜GitHub格納準備・個別原本SHA-256台帳（ZIP禁止）

**Status:** FINAL DRAFT / LOCAL BYTE VERIFICATION PASS / NOT CUSTODY PASS / NOT ISSUED  
**Owner禁止指示:** 2026-11-07 ZIP形式のパケット生成・配布・引渡し・保全禁止  
**7原本固定Commit:** `2d747d2b4162d11b915575ffc791607a37ef95df`  
**対象:** 3文書を個別Markdown原本として扱う。台帳自身も独立したMarkdown原本とする。

| 原本ファイル | bytes | SHA-256（実バイト） |
|---|---:|---|
| `SPE_RP023_NR01_03_Common_Review_Request_FINAL_DRAFT_20261107.md` | 4708 | `0b46b24d9cdf22a822d7a590197f1acedbe72567eff321a52e28dfb3c0542345` |
| `SPE_RP023_NR01_03_Review_Distribution_Manifest_FINAL_DRAFT_20261107.md` | 5718 | `6757e55403d9c162d07811c080e252b7f6baa9f6733217bb7301f3b321e7824d` |
| `SPE_RP023_NR01_03_Distribution_Checklist_FINAL_DRAFT_20261107.md` | 3672 | `31f2a2533d993cae79a7ee7fec002d72291af22ac081b6f6bd07486e82a24295` |

## 状態・引渡し条件

- 3文書は本実行環境で新規出力し、出力後の実バイトを読み直してサイズとSHA-256を計算した。
- 7原本のGitHub固定Commit照合は先行同一固定Commitの7/7 PASSを再利用。各原本の期待SHA-256はManifestに記載。
- この台帳自身のSHA-256は外部の検証結果で提示する。自己参照によるハッシュ固定は行わない。
- GitHub格納先ディレクトリ・新Commit・格納後の事後取得・SHA一致は未実施。保存先はOwnerの承認時に確定する。
- 新Snapshot Owner確認、正式発出、AI受領READY、CUSTODY PASSは未成立。
- ZIP形式の生成・配布・引渡し・保全は行わない。既存ZIPは今回の成果物に含めない。
- GitHub書込み・DecisionLog更新・Finding Close・Acceptance・Freeze・HOLD解除・Canonical化は行わない。
