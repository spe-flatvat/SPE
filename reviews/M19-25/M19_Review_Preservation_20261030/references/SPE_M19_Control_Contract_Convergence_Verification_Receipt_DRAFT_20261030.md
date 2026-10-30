# SPE M19｜Control Contract収束候補 検証レシート DRAFT

- Date: 2026-10-30
- Status: DRAFT / NOT OWNER-FINAL-APPROVED / NOT REVIEW-ACCEPTED / NOT FROZEN
- Owner authority: M19限定再開（DRAFT改訂・差分検証）、CC-04最終判断はM19全体収束時に留保
- Baseline: FG-06 fixed integrated candidate (commit `789403ae904594a0973ed7c7a142745a75595320`)
- Baseline SHA-256 (local byte check): `4a3b475abb1281c7bf25b27bc23c0e67b3f0abd3e494222404f607d7c6cc16c1`
- Input FG-07-07 SHA-256: `dc8d22dd6fa593d12bedde3f716af4bc8b39c41dc66eb17b408477b20b9ce917`
- Convergence candidate SHA-256: `4a1f70e0c517c0a3e5d0389bb5176db2336bcdd935f2d34f1abf7a5b5f538ed2`
- Incremental patch SHA-256: `9c7b30d99adf788a360fb4524b3aa095caa1df8007b69806960c56f5c6c9e669`
- Full baseline patch SHA-256: `1b6e085facece3d332715f28c0c1f7cab2b62c73166a516148446f5300ebf6d2`

## 変更内容

FG-07-07全文候補のCC-04にある `and attributable Decisions` の1箇所を、`and, where required by those contracts or other applicable approved requirements, attributable Decisions` に置換。Decisionの要否は既存の承認済み契約その他の適用要件へ委ねる趣旨。CC-03の非裁量型別契約要件、CC-04 Gate C／B・予約条件、CC-05 segment anchor、CC-06の2026/2027分岐は不変更。

## 検証結果

- 入力の一致／置換対象1箇所／変更箇所限定：PASS（静的文字列検証）
- FG-07-07との差分：CC-04内の1箇所のみ。PASS（機械差分）
- FG-06固定統合候補との差分：CC-04追記1段落とCC-06置換1文。PASS（機械差分）
- CC-03非裁量型別契約文とCC-06アンカー文の保持：PASS（静的存在検証）
- 意味論不変：**暫定的整合見込み／正式PASSではない**。`other applicable approved requirements` の適用範囲や非裁量型のDecision要否は、承認済み契約の実体確認なしには確定できない。
- 新32／旧20等のFinding正式処分：未実施。32件追跡表は既存FG-07-07版を引継ぎ、正式Close 0/32。

## 留保・停止境界

CC-04最終採否はM19全体収束時のOwner一括判断項目。遡及的な証跡探索や独立したCC-04裁定工程は開始しない。明示的な規範衝突が判明した場合のみ、該当条項・差分・影響を固定して報告。GitHub書込み、DecisionLog更新、正式レビュー、Freeze、M20–25／RP-023 HOLD解除は未実施。
