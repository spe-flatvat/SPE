# SPE M19-CC09-IR-01｜統合改訂候補 4AI配布Manifest DRAFT

**Status:** PRE-DISTRIBUTION DRAFT / NON-CANONICAL / NOT ISSUED
**Repository:** `spe-flatvat/SPE`
**固定Commit:** `7308831c918c6579ea9b31c19143ab4a5167828d`
**固定ディレクトリ:** `reviews/M19-25/M19_CC09_IR01/integrated_draft/`
**対象AI:** ChatGPT / Claude / Gemini / Grok
**権限:** 読み取り・新規DRAFTのみ。配布、レビュー開始、GitHub書込み、原本変更、Owner裁定、Finding Close、Freeze、HOLD解除は本Manifestによって承認されない。

## A. 固定対象（3点）
| ファイル名 | 役割 | SHA-256（Termux実バイト検証済） | Bytes |
|---|---|---|---:|
| `SPE_M19_CC09_IR01_Rev2_Integrated_Amendment_DRAFT_20261101.md` | 主レビュー対象／統合全文 | `5e19790560c9c84f5a00e58a33e6bafd1d0140c2f9b4b88ec14134247a877129` | 44489 |
| `SPE_M19_CC09_IR01_Rev2_Integrated_Amendment_DIFF_20261101.patch` | 固定Rev.2からの変更差分 | `2df2c1519e74355e3d5860b1f5b178cb6f0a80b5148a86deec13a9408c0049a5` | 21779 |
| `SPE_M19_CC09_IR01_Integrated_DRAFT_Selfcheck_20261101.md` | 自己検証（独立レビューの代替ではない） | `a9e90ee93fe71ce814d0e82481d8d41ce643f6d826c0a6e38db6b470231a5610` | 2613 |

**証拠区分:** Termuxで3/3 SHA-256一致、Git indexとローカルCommit内の実バイト一致、GitHub固定Commitの3/3ファイル存在・冒頭読取を確認済み。**GitHubから全バイトを再取得したSHA-256照合は未実施**。Git blob SHA-1をSHA-256と取り違えない。

## B. 比較基準と参照資料
- Rev.2契約基準: Commit `754c1e2907bce67f7d58d10bf36813ac76fd1ed0`
- Rev.2 path: `reviews/M19-25/M19_FR_CV_07/SPE_M19_FR_CV_06_Rev2_Convergence_Candidate_DRAFT_20261031.md`
- Rev.2 SHA-256（配布元抽出バイト照合）: `94286b1e8b86d19c0684c3463e77a454b49be661574be3cbbdb5b952a333e3bd`
- IR主資料固定Commit: `c96e48d19c82f318a80b01eb14bf7832913db518`、`reviews/M19-25/M19_CC09_IR01/`の4文書
- 既存4AIレビュー原文保全Commit: `da4ca873b6518449dcbd2941f58ebfd9a6eab524`、`reviews/M19-25/M19_CC09_IR01/independent_reviews/`
- `docs/Workflow.md` は別途正式ガバナンス規範として参照。具体的な版・バイト検証は配布前に固定する。
- 開発存続判定根拠文書は背景資料でありOwner裁定ではない。
- 旧IR差分v0.2は旧統合候補を基準とするため、**今回の固定Rev.2への適用パッチとして扱わない**。

## C. Owner方針受領
- 留保以外の工程C修正候補：Owner承認済み（方針承認、本文最終承認ではない）
- B-OD-01=A、B-OD-02=A、B-OD-03=A'、B-OD-04=A、B-OD-05=A：Owner判断受領済み
- B-OD-03 A'：追跡対象は実行入力、実行出力、実行記録の閉じた3分類。歴史的統治証拠の無限再認証は対象外。
- **承認されたのは修正方針**。本統合英文全文の正式承認・レビュー合格・Freezeではない。

## D. 配布固定の前提
配布パケット自身のSHA-256、保存Commit、全参照資料の可読性、4AI同一版配布を別途確認する。未検証は未検証として記録し、実施したとみなさない。
