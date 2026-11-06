# SPE RP-023 v0.3｜NR-01〜03 限定独立レビュー

**Status:** DRAFT / NON-CANONICAL / NOT ISSUED  
**Repository:** `spe-flatvat/SPE`  
**配布候補固定Commit:** `2d747d2b4162d11b915575ffc791607a37ef95df`  
**作成日:** 2026-11-07  

> 本書はレビュー準備の新規DRAFT。Owner-confirmed Snapshotの新規承認、正式発出、GitHub格納、レビュー開始を宣言しない。旧2026-11-06版§8限定改訂Snapshotを取り消さず、今回のNR-01〜03統合版とは別対象として識別する。

## 1. 7原本の固定所在・識別

以下のサイズとGit blob SHA-1は接続済みGitHubから指定Commitの再帰ツリーを取得して確認した値。SHA-256は**今回、接続済みGitHubの指定固定Commitから取得したUTF-8原文をバイト列として再計算**した値。7/7の実バイト長がGitHubツリーのサイズと一致し、既存記録5/5と一致。先行値の単なる転記ではない。

| 区分 | 固定Commit相対パス | bytes | Git blob SHA-1 | SHA-256（今回独立計算） |
|---|---|---:|---|---|
| 主対象 | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_v03_NR01_NR03_Full_Integrated_Revision_DRAFT_20261107.md` | 19595 | `09175698562a080112cc0d05a51b321cfdaa5d75` | `744181ddb4f696f72300dd5ae80d55e8e3aba07a34c6800c16a830b3e2202f19` |
| 全文差分 | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_v03_NR01_NR03_Full_Integrated_Revision_20261107.diff` | 6403 | `6debeea198d42134a582f97d57796c9395291847` | `2e67ad55e836ff0594a54bb2b2382b5eae1cab99464081428651d53f67bf89db` |
| 副作用監査 | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_v03_NR01_NR03_Normative_Delta_and_Side_Effect_Audit_DRAFT_20261107.md` | 4622 | `f3aadad98996db544aec7e28cfb648efb669349e` | `a67f02c2042f29451be898b1ba1ff38c86f21a8ffcebdcf1de27768831a8d3de` |
| NR-01裁定レシート | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/owner_decisions/SPE_RP023_v03_NR01_Owner_Decision_Receipt_20261107.md` | 3573 | `01771102727845fb8532f08372cf3e9d9e4d3dba` | `8a46a5fc881255e8ae264adaf3e98be509d7fb77560f58a299ba886a74275b6e` |
| NR-02裁定レシート | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/owner_decisions/SPE_RP023_v03_NR02_Owner_Decision_Receipt_20261107.md` | 4126 | `e2f34c775490f655eac71b86a2f3e6fc4820282a` | `3eee74a2b4b695dcde1c31034c9ed08d3752bbc5f506a51d564ec71ea54b06db` |
| NR-03裁定レシート | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/owner_decisions/SPE_RP023_v03_NR03_Owner_Decision_Receipt_20261107.md` | 4679 | `b21486f84f25bf7c8aa3f726a6599199c07dd9bc` | `20a01c3a9ac4f7dd1fb0170a00a2be70856c02a7fd8f820bf7f29fb63fa433ea` |
| 統合裁定台帳 | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/owner_decisions/SPE_RP023_v03_NR01_NR03_Integrated_Owner_Decision_Register_DRAFT_20261107.md` | 7739 | `d2ff930e840e9be9684422c45cc1afeb534970ff` | `fbfb41a72552ee908e0031e684ddd1d6ff253d88d22785427c81fc4ac492bb38` |

## 2. 比較基準と補助資料

- v0.3編集基準：`f4939211f1ab5b5848d3aa5293078bb651e2028b`、旧§8限定改訂本文（17,154 bytes、先行記録SHA-256 `4f99df2849d0264938cb9b223e9c020a89e6e33eabd7e1f84a06259c0fa62c56`）。これは**今回の主対象ではない**。
- v0.2比較基準：`5f27d4e2fba90cda2cd69ee534e865174c31ba1f` の `specifications/RP-023_v0.2_DRAFT_07C-02.md`。
- Step29H原16 Findingの原回答、`docs/Workflow.md`、`docs/SPE_Documentation_Standard.md`、横断監査4文書を固定参照。補助資料は発出時に正確な固定Commit・パス・必須／参考区分を確定する。
- OD-03/05/06/08原裁定の独立認証、DecisionLog個別対応、07C-03原diffは未検証。未検証を裁定不存在や不承認と同一視しない。

## 3. 配布パケットの状態

- 7/7 GitHubツリー上存在：PASS。7/7 固定Commit原文取得・実バイト長照合・SHA-256計算：**今回PASS**。先行期待値があった5件は5/5一致。残り2件は新規計測値として記録。
- 本Manifest／共通依頼書／Checklist：新規ローカルDRAFT。GitHub未格納。ファイル自体の実バイトSHA-256は生成後のローカル計測値を別途添付可能。
- 旧2026-11-06版配布候補に記載されたSnapshot確認は、その対象限定の時点記録。NR-01〜03新主対象のOwner-confirmed Snapshotへ自動転用しない。
- 最終配布経路、全AI到達性、発出時刻、期限、waiver、Owner正式発出承認：未確定。

## 4. 最終DRAFT確定時の制約

- 本書と別個のCommon Review Request、Distribution Checklistは**ローカル最終DRAFT**。これら3文書のSHA-256は別紙 `LOCAL_FIXITY_REGISTER_NO_ZIP_DRAFT_20261107.md` に記録する。
- 3文書の将来のGitHub格納Commitは未確定。**7原本の固定Commit `2d747d2b…` と配布3文書の格納Commitを混同しない**。
- 7原本の固定Commitを変えないまま3文書を追加する場合、格納後の新Commitから3文書を事後取得してSHA-256一致を検証し、CUSTODY PASSを別途判定する。
- 新NR-01〜03主対象のOwner-confirmed Snapshotと正式発出は未承認。

## 5. ZIP禁止・個別原本受渡し

Ownerの2026-11-07明示指示によりZIP形式のパケット生成・配布・引渡し・保全利用は禁止。配布3文書と7原本は個別のMarkdown／diffファイルとして管理する。旧ZIPは引渡し対象・保全対象から除外する。
