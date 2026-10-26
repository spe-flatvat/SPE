# RP-023｜4AI共通レビュー資料Manifest v0.3 DRAFT

- Version: v0.3
- Status: DRAFT / NOT APPROVED / NOT DISPATCHED
- Last Updated: 2026-10-26
- Updated By: RP-023
- Drafting note: Owner指示に基づくAI支援起案。`Updated By` はAIモデル名やReviewer帰属を示さず、Ownerの正式承認も意味しない。
- Repository: `spe-flatvat/SPE`
- Branch: `rp-023/document-issuance-draft`
- Evidence HEAD: `52ac73915beb5a3664ad8535cb5d7a4b80c28f91`

## 1. 配布候補ファイルとSHA-256

| 証拠区分 | Repository相対パス | SHA-256 |
|---|---|---|
| review_target | `specifications/RP-023_v0.2_DRAFT_07C-02.md` | `a7921e92d1cc4a9d15410ff84eb75f57b1edeeea18394748c04a6dbc851974f5` |
| historical | `specifications/RP-023_v0.1_DRAFT.md` | `145e09297f1f757cb8f70aafcf8a03d361bb5e3b8b28ad269ecbf47405126905` |
| self_check | `reviews/RP-023/RP-023_07C-03_Diff_Traceability_Report.md` | `3b477c65fdee6d3ddc65c2b01ec12ab82d5bc01974e513383f750d85b37328b1` |
| self_check | `reviews/RP-023/RP-023_07C-04_AC_NC_Self_Check.md` | `d1ddc939ff9e533da04f5e45115350a0b4bc5cc0b336f42f107334dea2c107db` |
| supplement | `reviews/RP-023/RP-023_07C-05_Owner_Report_Supplement_DRAFT.md` | `351da38fcaac74c9e9b8d787b30f732c3c58c3cc179561cdee62c25de0019512` |
| historical_audit_v0.1 | `reviews/RP-023/RP_023_Existing_Norm_Compatibility_Audit_DRAFT.md` | `ad99ed6785c17214ec9e68997273b3d57694a3a0276a05ba4d1ab3519567743d` |
| nonbinding_recommendations | `reviews/RP-023/RP_023_Revision_Recommendations_DRAFT.md` | `58a7f3f69f8e0187216e60b9ecc01219222535b0f0e38655871693b028a5ca4f` |
| normative_baseline_owner_confirmed | `docs/Workflow.md` | `b9727a775f8d0d25a7b5fc57bd4c74a8df289f92666ed6d8bd889bc084559e14` |
| normative_baseline_owner_confirmed | `docs/SPE_Documentation_Standard.md` | `18ed16d9fa23bbfaf0e1c15da25c7b3de5261af9c4430a39fa5693b9ce15c89a` |
| normative_baseline_owner_confirmed | `docs/DecisionLog.md` | `a9863a6c3b5b5bf32aa1de6e328c6f6ad7e007bbda4ffd35bfd8af63788f0ae1` |
| normative_baseline_owner_confirmed | `docs/Errata.md` | `66d87a8c56c249ccbab08bb332efe0a43752618c4ba5082594e3ba7a7cf4941f` |

## 2. 証拠の効力と限界

- SHAはOwner提示Termuxログに基づく。Step 27Cで11/11の実バイト照合PASSを確認したが、本起案環境からGitHub実バイトの独立再取得は実施していない。配布時・受領時にも再照合する。
- 07AのDR-01〜06はv0.2 §10および07C-03/07C-05で参照されるが、独立したOwner裁定原文・原本SHAは未取得。**Owner裁定済みとの報告は存在／原本完全性未検証**として扱う。
- 07C-03と07C-04のPASSは自己検証であり、独立検証ではない。
- Work監査のF01〜F06はv0.1対象。v0.2のFinding Closeを示さない。推奨R01〜R06は未採択。
- 既存規範の上記4ファイルはStep 28でOwner-confirmed Snapshotとして確認済み。対象v0.2のSHAも同時確認済み。
- M19–25 Control Contract Rev.4は未承認DRAFTであり、本Manifestの規範基準には含めない。

## 3. パケット全体の管理範囲

上表の11件はRepository内のReview Target・補助証拠・規範候補であり、**共通レビューパケット全体の全ファイル一覧ではない**。別途、以下の起案3文書を配布候補として管理する。

| Packet document | 状態 | SHA-256の扱い |
|---|---|---|
| `RP-023_4AI_Common_Review_Manifest_v0.3_DRAFT.md` | 本文書・未承認 | 本文書の外部レシートで固定（自己参照SHAは記載しない） |
| `RP-023_4AI_Common_Review_Contract_v0.3_DRAFT.md` | 未承認 | Step 29Bの外部検証記録で固定候補を管理 |
| `RP-023_4AI_Standard_Review_Request_v0.3_DRAFT.md` | 未承認 | Step 29Bの外部検証記録で固定候補を管理 |

実際の配布に含める全ファイルの確定リスト・SHA・配布手段・受領検証は、Owner承認後の別工程で固定する。Step 29Bの生成ファイルのSHAは、SPEリポジトリ側11ファイルの再ハッシュを意味しない。

## 4. 配布前Gate

1. Step 28でOwnerがReview Targetと既存規範のSnapshotを明示確認済み。発出前に固定SHAとの一致を再照合する。
2. Step 27Cで11/11 PASS済み。配布時にも全件照合し、受領側の検証方法を確定する。
3. Step 28で07A原文欠落の扱いとレビュー受入条件（OD-08案A）をOwnerが承認済み。原本未検証は維持する。
4. 共通レビュー契約・Review Requestを固定し、Ownerが発出を別途承認する。

**Current state: DRAFT / NOT DISPATCHED.**

## Step 29B 状態更新の根拠と境界

- Step 28 Owner承認記録：`RP-023_Step28_Owner_Snapshot_OD08_Approval_Receipt_PROVISIONAL.json`（二次記録、署名済み原本ではない）。
- 固定基準HEAD：`52ac73915beb5a3664ad8535cb5d7a4b80c28f91`。Step 27C 11/11 SHA PASSはOwner提示ログに基づく。
- 07A原本・原本SHAは未検証。OD-03・OD-05は未裁定。
- 本v0.3は未承認の起案物であり、Git保全、パケット最終固定、4AI発出、Review Acceptance、Finding Close、Canonical化、Freeze、Closeを意味しない。
