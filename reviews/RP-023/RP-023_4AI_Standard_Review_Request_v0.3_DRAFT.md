# SPE RP-023｜標準4AI Review Request v0.3 DRAFT

- Version: v0.3
- Status: DRAFT / NOT SUBMITTED
- Last Updated: 2026-10-26
- Updated By: RP-023
- Drafting note: Owner指示に基づくAI支援起案。`Updated By` はAIモデル名やReviewer帰属を示さず、Ownerの正式承認も意味しない。

## Subject

RP-023｜要承認文書の発出・受領・完全性検証ルール — v0.2 DRAFT独立レビュー

## Purpose / Scope

固定対象 `specifications/RP-023_v0.2_DRAFT_07C-02.md`、SHA-256 `a7921e92d1cc4a9d15410ff84eb75f57b1edeeea18394748c04a6dbc851974f5` の既存規範整合性、F01〜F06、07C-03追跡可能性、07C-04 AC-01〜08・NC-01〜12、Header Rules、権限分離、OD-03/05の判断材料およびOD-08案Aの遵守状況、新規リスクを独立評価する。評価手順・証拠区分・STOP条件は添付の共通レビュー契約案に従う。ただしStep 28でOwner-confirmed SnapshotとOD-08案Aは承認済み。本依頼の固定・発出には別途Owner承認を要する。

## Out of Scope

他RPの再設計、既承認事項の無断再審、M19–25 FG-06のFinding Close、RP-022固有証拠規則の改変、Git操作、DecisionLog更新、正式承認、Canonical化、Freeze、Close。

## Expected Output

`Accepted` / `Revision Recommended` / `Rejected` のいずれか。各FindingにID・重大度・条項・証拠・影響・修正案・証拠限界を記載し、自己検証と独立検証を区別する。資料欠落・SHA不一致・未裁定事項は明示する。AI判定はOwner裁定ではない。

## Attachment

- Owner-confirmed Snapshot（**Step 28でOwner確認済み**：レビュー対象1件＋規範4件、各SHAはManifest参照）
- RP-023 v0.2 DRAFT固定対象
- `RP-023_4AI_Common_Review_Manifest_v0.3_DRAFT.md`
- `RP-023_4AI_Common_Review_Contract_v0.3_DRAFT.md`
- Manifest記載のRepository資料11件（配布時再ハッシュ要）。上記Manifest・契約・本Review Requestの3件とは別管理。
- 07A裁定原文は未取得。二次記録に基づく裁定済みとの報告のみ存在。

**DISPATCH GATE: HOLD — Snapshot・OD-08案Aは承認済み。v0.3パケット全件固定、受領照合方法のOwner確認、共通依頼文固定、別途発出承認が未了。**

## Step 29B 状態更新の根拠と境界

- Step 28 Owner承認記録：`RP-023_Step28_Owner_Snapshot_OD08_Approval_Receipt_PROVISIONAL.json`（二次記録、署名済み原本ではない）。
- 固定基準HEAD：`52ac73915beb5a3664ad8535cb5d7a4b80c28f91`。Step 27C 11/11 SHA PASSはOwner提示ログに基づく。
- 07A原本・原本SHAは未検証。OD-03・OD-05は未裁定。
- 本v0.3は未承認の起案物であり、Git保全、パケット最終固定、4AI発出、Review Acceptance、Finding Close、Canonical化、Freeze、Closeを意味しない。
