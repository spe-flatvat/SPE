# SPE M19｜GitHub保全対象一覧（DRAFT）

**Status:** DRAFT / READ-ONLY INVESTIGATION / NOT OWNER ADJUDICATION
**Repository:** `spe-flatvat/SPE`  
**基準日:** 2026-11-03 PM（JST）  
**調査記録:** 2026-11-03T14:05:07+09:00 ～ 2026-11-03T14:15:57+09:00。継続的な監視ではない。
**状態維持:** M19–25・RP-023のHOLDを維持。正式受入、Finding Close、Canonical化、Freeze、GitHub保全実行を行わない。

## 1. 保全方針・新規性

**実行承認前の対象案であり、GitHubには何も追加していない。** 既存原本の内容・状態表記・旧バージョン名・タイムアウト記録を修正せず、原本を保全する。DRAFTや限定承認を全文承認へ昇格させない。

提案先ルート：`reviews/M19-25/M19_20261103_PM_handoff/`。今回の17 HEADのパス一覧にはこのルートはない。実行時に再確認する。以下はこのルートからの相対パス案。コードを`engine/`へ投入する案ではなく、**既存ZIPの証拠保全**である。

## 2. 既存GitHub保全済み：再追加しない

commit `049f47309df8d4c09610a1ce47f68bdfc71f35f2` の `reviews/M19-25/M19_CC09_IR01/normative_delta_audit_preservation_20261101/` に11月1日規範差分監査の5成果物とSHA一覧がある。今回SHA5/5一致を再確認した。新規の全文監査として再生成せず、commit・元パス・SHAで参照する。

その他のレビュー・配布・Owner裁定保全ブランチも現状報告の17 HEADに固定して参照する。treeで所在のみ確認したものと、実バイトを取得した9ファイルを区別する。既存の4AI回答・旧Findingを再統合・Closeしない。

## 3. 優先保全案：既存原本19件

取得元リンク・bytes・全SHAは証跡対応表／JSON索引にある。GitHub上に同一バイトが別名で保全されている可能性を完全には排除していないため、実行前にSHA比較する。今回、該当名称の成果を17 HEADで確認できなかった。

| 取得原本名 | 保全先相対パス案 | SHA-256 |
| --- | --- | --- |
| SPE_M19_CC09_IR01_Stage20_Consolidated_Approval_Candidate_DRAFT_20261102.md | originals/normative/SPE_M19_CC09_IR01_Stage20_Consolidated_Approval_Candidate_DRAFT_20261102.md | 151c8d7549f411d622a8b90585b846847fb76436c4e2c4b69073017640fc48ae |
| SPE_M19_CC09_IR01_Stage20_Owner_Approval_Packet_DRAFT_20261102.md | originals/normative/SPE_M19_CC09_IR01_Stage20_Owner_Approval_Packet_DRAFT_20261102.md | bdbcc86b8e28d139d9d3243b0df2d52f479c04b00baf4a16bc1d8a38a34c2b5b |
| SPE_M19_CC09_IR01_Stage20_Change_Diff_20261102.patch | originals/normative/SPE_M19_CC09_IR01_Stage20_Change_Diff_20261102.patch | 69fd8bc3772be3b4dab351b8277d9330cf65da2fd6e1b8ec28d93f1b506d2ef0 |
| SPE_M19_CC09_IR01_OD20_01_Owner_Approval_Receipt_ISSUED_20261102.md | originals/authority/SPE_M19_CC09_IR01_OD20_01_Owner_Approval_Receipt_ISSUED_20261102.md | df95e6a62180e65f130c6a206a85720d6bdf5d03b89df3e02241c0bbb58b1f18 |
| SPE_M19_IMPL_01_02_SliceA_Implementation_Spec_DRAFT_20261102.md | originals/implementation/SPE_M19_IMPL_01_02_SliceA_Implementation_Spec_DRAFT_20261102.md | 7223ba3910155ff074100da0dbcc91301093df00f0761c34c70565c76ca5731e |
| SPE_M19_IMPL_01_03_Implementation_Start_Decision_Packet_DRAFT_20261102.md | originals/implementation/SPE_M19_IMPL_01_03_Implementation_Start_Decision_Packet_DRAFT_20261102.md | adb3e613ae624b5acf9a0f38eea365cf57eda8dd76723149401779b9f757cace |
| SPE_M19_IMPL_01_04_Execution_Report_DRAFT_20261102.md | originals/implementation/SPE_M19_IMPL_01_04_Execution_Report_DRAFT_20261102.md | ac653dfa41472625a55105471e1fc3741d84b86acaf11767656d3a267770d44c |
| SPE_M19_IMPL_01_05K_Original_M10_M18_E2E_Report_DRAFT_20261103.md | originals/implementation/SPE_M19_IMPL_01_05K_Original_M10_M18_E2E_Report_DRAFT_20261103.md | e5f44ffc029a08b6b78041ea4707c16bf8d08ba79a0ff7bb0b798c0b9289c5fa |
| M19_IMPL_01_05BM_05BO_Combined_Report_DRAFT.md | originals/implementation/M19_IMPL_01_05BM_05BO_Combined_Report_DRAFT.md | 827c30234836e6b386212717814d2aeb69e2bf4acffbec74a2ba1b5535e55ae4 |
| M19_IMPL_01_05BP_Continuation_Report_DRAFT.md | originals/implementation/M19_IMPL_01_05BP_Continuation_Report_DRAFT.md | d8c5783d0afb75db830838847bd944c8df1090e3da505b28315fa813ed90f281 |
| M19_IMPL_01_05BQ_Continuation_Report_DRAFT.md | originals/implementation/M19_IMPL_01_05BQ_Continuation_Report_DRAFT.md | 92dfb9c5407f4d07d4da72f49a62f4cf55d3b8718721ed820aeffe0cf5b0c5b7 |
| M19_IMPL_01_05BQ_Local_DRAFT.zip | originals/implementation/M19_IMPL_01_05BQ_Local_DRAFT.zip | 5d65d9df18d3ab12863cf6b7cbbec08c7055ef0c0a3a8cd5b72ee506b7d17b12 |
| 05BQ_full.log | originals/implementation/05BQ_full.log | bcb77279f890a39d10ba2cd2c0bc6530e5eb6f1518c346dc669c1d69ed2466e7 |
| 05BQ_warnings.log | originals/implementation/05BQ_warnings.log | 629edd970b00515c2951d2f4d9140d28e3c9c834302b312ff3083ced4cf4e297 |
| 05BQ_repeat.log | originals/implementation/05BQ_repeat.log | d6405a8662745016571a07ea3c116bcd4d63b752afed94376fd1a67f06309497 |
| SPE_M19_IMPL_01_SliceA_Acceptance_Packet_DRAFT.md | originals/implementation/SPE_M19_IMPL_01_SliceA_Acceptance_Packet_DRAFT.md | ce9db1a46bb9d813b649bed4b8f6e964f003155e1060cc82a04ea3ca75bb2f2f |
| SPE_SliceA_Acceptance_Regression.log | originals/implementation/SPE_SliceA_Acceptance_Regression.log | 8084d43b06f4682f8275355e401651a9efc4019fccb7f7026816a42e8bd6272d |
| SPE_M19_IMPL_01_SliceA_Acceptance_Evidence_DRAFT.zip | originals/implementation/SPE_M19_IMPL_01_SliceA_Acceptance_Evidence_DRAFT.zip | f13007a91efa446e809af002f421f258307e006f925b6342ea5a53462077db12 |
| SPE_M19_IMPL_01_SliceA_Independent_Technical_Review_Owner_Authorization_Receipt_20261103.md | originals/authority/SPE_M19_IMPL_01_SliceA_Independent_Technical_Review_Owner_Authorization_Receipt_20261103.md | eeec02c48d3201155906479e7d4d7a3c875a271694b5349db0845a7ec9bcf064 |

受入証拠ZIPには受入パケット・受入ログ・05BQ報告の3原本が内包され、別取得物とのSHAは3/3一致した。これは既存の正当な同梱構造として保持する。個別ファイルも保全するかZIP＋索引で足りるかはOwnerが選べる。**新たに同内容の原本を再生成しない。**

## 4. 補助資料：既存原本6件

| 原本 | 用途 | SHA-256 |
| --- | --- | --- |
| SPE_M19_CC09_IR01_Stage14_Initial_Scope_and_SliceA_Entry_DRAFT_20261102.md | 段階的裁定・仕様形成の経緯。裁定前DRAFTと後続ISSUEDを併読 | 6c8c2d2693821a565e74200faf0a08e604ebbb33c301e28965b70ad47fff3ffc |
| SPE_M19_CC09_IR01_Stage16_SliceA_Minimal_Implementation_Contract_DRAFT_20261102.md | 段階的裁定・仕様形成の経緯。裁定前DRAFTと後続ISSUEDを併読 | 2f45d2f2cc36704d921c6c1b1de9fb3b3eacd2b844b851cf3f905a00a2a53607 |
| SPE_M19_CC09_IR01_Stage17_Player_Configurable_Initialization_Normative_Amendment_DRAFT_20261102.md | 段階的裁定・仕様形成の経緯。裁定前DRAFTと後続ISSUEDを併読 | 3adb3ac95c6f11255cc3b6d93cc92c4c22bc5f14b4c372379c65580849926cf7 |
| SPE_M19_CC09_IR01_Stage19_Final_Normative_Delta_and_Approval_Readiness_Audit_DRAFT_20261102.md | 段階的裁定・仕様形成の経緯。裁定前DRAFTと後続ISSUEDを併読 | c16f4ddc2114cc79ad50b2006beb036e5ee2a442dfb947f6ae266405fecf2f32 |
| SPE_M19_CC09_IR01_Stage5_Minimal_Revision_and_Owner_Decisions_DRAFT_20261102.md | 段階的裁定・仕様形成の経緯。裁定前DRAFTと後続ISSUEDを併読 | 7ef084c067d9128307089238be593953f7dafcbfc0e3d05aa1c8759248ed428a |
| SPE_M19_IMPL_01_01_Implementation_Preparation_Investigation_DRAFT_20261102.md | 段階的裁定・仕様形成の経緯。裁定前DRAFTと後続ISSUEDを併読 | f0acfc1766a6ceea5f088571688cf2364cddb3e66788eb1d0fe5973b80cf645a |

これらは優先19件の文脈を補う候補であり、すべてを再承認対象にする提案ではない。ファイル名末尾`(1)`等の類似項目も一覧上にあったが、今回選択しなかった項目のバイト同一性は未検証。名称・サイズだけで重複と断定せず、既存の重複を削除しない。

## 5. 今回新規作成するDRAFT

`status/`に現状報告、証跡対応表、本一覧、残作業表、実施可否・手順書の5文書、および証拠索引JSON・SHA一覧を保存する案。新規DRAFTの対象外資料はZIPへ再梱包せず参照に留める。今回の配布用ZIPはこの新規DRAFT集合のみを格納する。

本一覧とレシート原文をGitHubへ保全しても、新たなOwner裁定・実装受入・正式レビュー受理にはならない。GitHub commitの日時も、過去のOwner承認時刻・試験時刻の代用にしない。

## 6. 未取得であり、保全済み扱いにできないもの

- 実装着手Option Aの原チャット発言・単独ISSUEDレシート。04/05Kによる後続報告は取得済みなので、承認不存在としない。
- 11月3日承認に基づくTechnical Verification Report／Authority & Evidence Boundary Statement／Independent Review Request & Manifestの完成版・提出記録。今回の対象一覧範囲では未確認。
- 正式受入の新たなOwner裁定・本番適格性認定。取得資料はNOT ACCEPTED／準備のみと記載する。
- 後続実装のGit commit・リモート実装ブランチ、過去実行環境の完全な再現情報。

これらを推測で新規作成・補完しない。GitHub保全は別途Ownerが対象・親commit・新規ブランチ・書込範囲を承認するまでSTOP。
