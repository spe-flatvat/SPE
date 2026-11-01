# SPE M19-CC09-IR-01｜4AI配布前チェックリスト Rev.A DRAFT

**Status:** DRAFT / PRE-DISTRIBUTION / NOT ISSUED
**元Checklist:** `SPE_M19_CC09_IR01_Integrated_4AI_Distribution_Checklist_DRAFT_20261101.md`（不変更）
**主対象固定Commit:** `c3310a510f44c9c5ea36b1423814aafc7bda6e1d`

## 受領・検証

- [x] 主対象7件をGitHub固定Commitから全文取得・SHA-256 7/7 事前固定値一致
- [x] Rev.2原本を固定Commitから全文取得・事前固定SHA-256一致
- [x] `docs/Workflow.md` を固定Commitから全文取得・SHA-256算出
- [x] IR-01旧資料4件を固定Commitから全文取得・SHA-256算出
- [x] 既存4AIレビュー保全文書4件を固定Commitから全文取得・SHA-256算出
- [x] 検証結果を新規レシート・Manifest補遺に記録
- [ ] 旧4AI原回答と保全文書の独立した原証拠照合（本限定配布の必須条件かはOwner判断。未検証を明示）

## 配布直前の固定化・権限

- [ ] 新規3文書（検証レシート、Manifest補遺、Rev.A Checklist）を限定Commit・Push
- [ ] 新規3文書のGitHub固定CommitとSHA-256を再検証
- [ ] 4AIに配布する**最終固定Commit**を確定し、元4文書・新3文書・主対象3文書を同一参照体系で案内
- [ ] Ownerによる最終配布承認（今回の作成・整合性更新承認とは区別）
- [ ] 各AIの受領PASS確認後、Ownerによる独立レビュー本文開始承認

## STOP条件

固定版・SHA-256不一致、必須資料取得不能、Owner未承認の補完証拠採用、配布対象版の不統一、未承認の正式配布・レビュー開始。既存原本変更、Finding Close、DecisionLog更新、Freeze、HOLD解除は禁止。

**現在判定:** TECHNICAL RECEIPT PASS / DISTRIBUTION HOLD。元の配布パケット4文書は改変しない。
