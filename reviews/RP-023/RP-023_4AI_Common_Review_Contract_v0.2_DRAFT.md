# RP-023｜4AI共通独立レビュー契約 v0.2 DRAFT

- Version: v0.2
- Status: DRAFT / OWNER APPROVAL PENDING / NOT DISPATCHED
- Last Updated: 2026-10-26
- Updated By: RP-023
- Drafting note: Owner指示に基づくAI支援起案。`Updated By` はAIモデル名やReviewer帰属を示さず、Ownerの正式承認も意味しない。
- Repository: `spe-flatvat/SPE`
- Branch: `rp-023/document-issuance-draft`
- Evidence HEAD: `5ceeb2c8e8db27453d7eb5263fd9313bc46e9133`

## 1. 対象と権限

対象は `specifications/RP-023_v0.2_DRAFT_07C-02.md`（SHA-256 `a7921e92d1cc4a9d15410ff84eb75f57b1edeeea18394748c04a6dbc851974f5`）。本契約は独立レビューの条件案であり、OD-08の裁定、Owner-confirmed Snapshot、レビュー開始のいずれも代替しない。

## 2. 証拠区分

- Normative baseline: Owner-confirmed Snapshotとして明示確認された既存規範のみ。
- Review target: 固定v0.2 DRAFT。
- Historical evidence: v0.1、v0.1対象Work監査、関連記録。
- Self-check evidence: 07C-03/07C-04（自己検証のPASSは独立PASSでない）。
- Nonbinding supplement: 07C-05および未採択の修正推奨。
- Evidence gap: 07A裁定原文と原本SHA未取得。二次資料の記載を原文照合済みと扱わない。
- Pending Owner decisions: OD-03、OD-05、OD-08。

## 3. 独立レビューの問い

1. v0.2が既存Workflow（Owner-confirmed Snapshot、Review Template、review/waiver/consensus/Owner裁定）、Documentation Standard（Header Rules、Updated By）、DecisionLog、Errataと整合するか。
2. v0.1対象F01〜F06がv0.2でどの程度解消・残存・変質したか。正式Finding Closeとは区別する。
3. 07C-03の差分・トレーサビリティ、および07C-04のAC-01〜08・NC-01〜12を独立再検証できるか。証拠不足は明記する。
4. A/B/C区分、技術的受領、発出権限、内容判断、Review Acceptance、Git反映、Canonical化、Freezeの独立性が保たれるか。
5. OD-03（A区分PDF）、OD-05（発効日・組込み先）、OD-08（レビュー範囲・受入条件）について、未決を維持したままOwner向け判断材料を示す。
6. 新規の重大な競合、曖昧さ、証拠欠落がないか。

## 4. Reviewer運用

- ChatGPT、Claude、Gemini、Grokは初回レビューを相互独立に行い、いずれにも優先権を与えない。
- 利用不能ReviewerのwaiverはOwner判断と理由記録を要する。自動waiverは行わない。
- 異なる判定の調整、最終裁定、再提出はWorkflowに従う。
- Reviewerはファイル変更、Git操作、正式承認、Finding Close、DecisionLog更新を行わない。

## 5. 出力契約

- Workflowの判定表記：`Accepted` / `Revision Recommended` / `Rejected`。
- 各Finding：ID、Severity、対象条項、根拠ファイル・該当箇所、問題、影響、推奨措置、証拠限界。
- F01〜F06、AC01〜08、NC01〜12を個別に扱い、未検証項目はPASSにしない。
- 自己検証PASSと独立検証PASS、AIのAcceptedとOwnerのReview Acceptanceを混同しない。

## 6. パケット完全性の境界

Manifest内のRepository資料11件と、Manifest自身を含む起案パケット3文書は別集合である。配布候補14件の全件固定・実バイト照合は未了であり、Step 23Bの3文書SHAは別の外部検証記録に置く。Owner-confirmed Snapshotが成立するまで既存規範4件を確定済みのレビュー基準とは扱わない。

## 7. STOP・保留

- 固定対象SHA不一致、必須ファイル未受領、Owner-confirmed Snapshot不成立、重大な基準不明時は該当評価をSTOPしOwnerに報告する。
- 07A裁定原文未取得は開示されたEvidence Gapとして扱い、原文との厳密照合は未判定とする。これを自動的にレビュー全体の停止条件にも、無条件の免除にもせず、OD-08でOwnerが扱いを裁定する。
- 配布と正式レビュー開始には別途Owner承認が必要。

**Current state: DRAFT / NOT DISPATCHED.**
