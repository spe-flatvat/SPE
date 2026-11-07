# SPE RP-023｜E-01〜E-04 4AI独立レビュー 配布Manifest（レビュワー用・再改訂候補）

**Document Status:** REVIEWER-FACING DISTRIBUTION MANIFEST CANDIDATE / NON-CANONICAL  
**発出日時:** 正式発出時に発出レシートで確定（本書は発出指示書ではない）  
**Repository:** `spe-flatvat/SPE`  
**Snapshot識別:** 主対象固定Commit `6b8406a966a464de5b29199b4c12e0535e6ac827`、共通依頼書固定Commit `2eb077ad229d1f38e7b6802a417822b07f511765`。本Manifest自身の最終固定CommitはGitHub格納後の発出レシートで外部固定する。  
**レビュー範囲:** E-01〜E-04限定修正後のRP-023 v0.3候補の4AI独立レビュー。正式Acceptance・Canonical化ではない。

## 1. 最初に読む事項（全AI共通）

1. **唯一の主レビュー対象**は `MAIN-TARGET`（20,128 bytes、SHA-256 `b0e770dd696da7f161d8a8e9c9372a88780c70a1224d6bf09a3bd73f58cb82e5`）。`PREVIOUS-TARGET` と `BASELINE-V03`、`BASELINE-V02` は比較資料であり主対象ではない。
2. **レビュー指示**は `COMMON-REQUEST`（4,971 bytes、SHA-256 `c49c05a4f645def90a1474da56535bbfedf20a7201b633b063c627e01de3628f`）。原16 Finding（Major 4 / Minor 10 / Editorial 2）のID・Severityを維持し、NR-01〜03、E-01〜04および副作用を検証する。
3. **ChatGPT／Claude／Grok**は以下のGitHub固定Commit＋パスから各原本を取得する。**Gemini**は同一22原本を収録した個別の統合Markdownを受け取る。GeminiにGitHubアクセスを必須としない。
4. 原本の受領と実バイトSHA-256・サイズを検証し、受領READYに到達した場合のみ、正式発出指示書の権限範囲で本文へ進む。技術的に実測できない項目は代替証拠の有無と限界を記録し、自己検証PASSと偽らない。
5. 収録原本内の古い `DRAFT`、`NOT ISSUED`、`GitHub未固定` 等は**当該原本が作成された時点の歴史的記述**である。現在の配布参照先は本Manifestの第2節と、発出時の固定Commit・受領レシートを優先する。ただし原本内容の改変や未成立のOwner承認を成立扱いする趣旨ではない。

## 2. 固定原本一覧（22件）

**参照規則:** 各行のURLは `https://github.com/spe-flatvat/SPE/blob/{固定Commit}/{パス}`。Commitは各原本ごとに固定されており、`main` の現在HEADへ読み替えない。SHA-256はUTF-8原本の実バイトに対する値であり、Git blob SHA-1とは異なる。

| ID | 役割 | bytes | SHA-256 | 固定Commit | Repository内パス |
|---|---|---:|---|---|---|
| `COMMON-REQUEST` | 共通指示 | 4,971 | `c49c05a4f645def90a1474da56535bbfedf20a7201b633b063c627e01de3628f` | `2eb077ad229d1f38e7b6802a417822b07f511765` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_E01_E04_4AI_Common_Review_Request_PRE_DISPATCH_DRAFT_20261107.md` |
| `DISTRIBUTION-MANIFEST` | 旧Manifest証拠 | 7,821 | `81c1ec546dbbb4f44478fdc9007b48068d969a58ee3415d891a3fc3843062ec1` | `2eb077ad229d1f38e7b6802a417822b07f511765` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_E01_E04_Distribution_Manifest_PRE_DISPATCH_DRAFT_20261107.md` |
| `MAIN-TARGET` | 唯一の主対象 | 20,128 | `b0e770dd696da7f161d8a8e9c9372a88780c70a1224d6bf09a3bd73f58cb82e5` | `6b8406a966a464de5b29199b4c12e0535e6ac827` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_v03_NR01_NR03_Post_Cross_Audit_Revision_Candidate_DRAFT_20261107.md` |
| `PREVIOUS-TARGET` | 直前候補比較 | 19,595 | `744181ddb4f696f72300dd5ae80d55e8e3aba07a34c6800c16a830b3e2202f19` | `2d747d2b4162d11b915575ffc791607a37ef95df` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_v03_NR01_NR03_Full_Integrated_Revision_DRAFT_20261107.md` |
| `E01-E04-DIFF` | 限定差分 | 6,804 | `35811cb56c2c9c31a5ad41d1c3d3b88e5a9b933f2e11687cc4fb60478b76430f` | `2eb077ad229d1f38e7b6802a417822b07f511765` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/RP023_E01_E04_full_diff_READONLY.diff` |
| `OWNER-APPROVAL-RECEIPT` | 承認根拠 | 2,179 | `965df96c4c2a3fcd81384bbdd9db833f7652702f2bd16be22ad9a9363b3d49c2` | `2eb077ad229d1f38e7b6802a417822b07f511765` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_NR01_03_Cross_Audit_Owner_Approval_Receipt_20261107.md` |
| `CONCRETE-EDITS` | 修正内容 | 5,588 | `91b999b1a4fa2a6bf924c8af02ba05599a9075be47a36087b13bfa26a0227456` | `2eb077ad229d1f38e7b6802a417822b07f511765` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_NR01_03_Post_Cross_Audit_Concrete_Edits_DRAFT_20261107.md` |
| `CUSTODY-RECEIPT` | 保全証拠 | 3,078 | `fcc47cf907632c5fe7f91cd423863dc433a4afe40c05be09e61e6690ca4cc967` | `2eb077ad229d1f38e7b6802a417822b07f511765` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_E01_E04_GitHub_Custody_PASS_Receipt_20261107.md` |
| `ORIGINAL-CHATGPT` | 原レビュー回答 | 11,031 | `9235d3ac0a40d9770508a8c3d2fc572ffe974760a9136f69eba131f45a3c6b1f` | `6b8406a966a464de5b29199b4c12e0535e6ac827` | `reviews/RP-023/step29h/responses/SPE_RP023_Step29H_ChatGPT_Independent_Review_20261103.md` |
| `ORIGINAL-CLAUDE` | 原レビュー回答 | 20,473 | `83a7084a4e410a4e7a9199aba5d959bb41c3d4617bfe5cd9542c43815bdf6af7` | `6b8406a966a464de5b29199b4c12e0535e6ac827` | `reviews/RP-023/step29h/responses/RP-023_Step29H_Claude_Independent_Review_DRAFT_20261103.md` |
| `ORIGINAL-GEMINI` | 原レビュー回答 | 6,962 | `8a2315cf75995d108bf0596f7b46eae235c232b6909ed7a49f56207e082c283d` | `6b8406a966a464de5b29199b4c12e0535e6ac827` | `reviews/RP-023/step29h/responses/SPE_RP023_Step29H_Gemini_Independent_Review_Response_20261103.md` |
| `ORIGINAL-GROK` | 原レビュー回答 | 6,465 | `ff0f55709a26de2fffc21a66a8162decf388c829eac1df64e2621f9699889bee` | `6b8406a966a464de5b29199b4c12e0535e6ac827` | `reviews/RP-023/step29h/responses/SPE_RP-023_Step29H_Independent_Review_Report_Grok_20261103.md` |
| `WORKFLOW` | 運用規則 | 3,402 | `b9727a775f8d0d25a7b5fc57bd4c74a8df289f92666ed6d8bd889bc084559e14` | `6b8406a966a464de5b29199b4c12e0535e6ac827` | `docs/Workflow.md` |
| `DOCUMENTATION-STANDARD` | 文書規則 | 2,280 | `18ed16d9fa23bbfaf0e1c15da25c7b3de5261af9c4430a39fa5693b9ce15c89a` | `6b8406a966a464de5b29199b4c12e0535e6ac827` | `docs/SPE_Documentation_Standard.md` |
| `OLD-FULL-DIFF` | 比較・裁定証拠 | 6,403 | `2e67ad55e836ff0594a54bb2b2382b5eae1cab99464081428651d53f67bf89db` | `2d747d2b4162d11b915575ffc791607a37ef95df` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_v03_NR01_NR03_Full_Integrated_Revision_20261107.diff` |
| `OLD-SIDE-EFFECT-AUDIT` | 比較・裁定証拠 | 4,622 | `a67f02c2042f29451be898b1ba1ff38c86f21a8ffcebdcf1de27768831a8d3de` | `2d747d2b4162d11b915575ffc791607a37ef95df` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/SPE_RP023_v03_NR01_NR03_Normative_Delta_and_Side_Effect_Audit_DRAFT_20261107.md` |
| `NR01` | 比較・裁定証拠 | 3,573 | `8a46a5fc881255e8ae264adaf3e98be509d7fb77560f58a299ba886a74275b6e` | `2d747d2b4162d11b915575ffc791607a37ef95df` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/owner_decisions/SPE_RP023_v03_NR01_Owner_Decision_Receipt_20261107.md` |
| `NR02` | 比較・裁定証拠 | 4,126 | `3eee74a2b4b695dcde1c31034c9ed08d3752bbc5f506a51d564ec71ea54b06db` | `2d747d2b4162d11b915575ffc791607a37ef95df` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/owner_decisions/SPE_RP023_v03_NR02_Owner_Decision_Receipt_20261107.md` |
| `NR03` | 比較・裁定証拠 | 4,679 | `20a01c3a9ac4f7dd1fb0170a00a2be70856c02a7fd8f820bf7f29fb63fa433ea` | `2d747d2b4162d11b915575ffc791607a37ef95df` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/owner_decisions/SPE_RP023_v03_NR03_Owner_Decision_Receipt_20261107.md` |
| `OWNER-REGISTER` | 比較・裁定証拠 | 7,739 | `fbfb41a72552ee908e0031e684ddd1d6ff253d88d22785427c81fc4ac492bb38` | `2d747d2b4162d11b915575ffc791607a37ef95df` | `reviews/RP-023/v0.3_distribution_draft_20261106/nr01_03_limited_revision_20261107/owner_decisions/SPE_RP023_v03_NR01_NR03_Integrated_Owner_Decision_Register_DRAFT_20261107.md` |
| `BASELINE-V03` | v0.3比較基準 | 17,154 | `4f99df2849d0264938cb9b223e9c020a89e6e33eabd7e1f84a06259c0fa62c56` | `f4939211f1ab5b5848d3aa5293078bb651e2028b` | `reviews/RP-023/v0.3_distribution_draft_20261106/SPE_RP023_v03_Section8_Limited_Revision_DRAFT_20261106.md` |
| `BASELINE-V02` | v0.2比較基準 | 13,182 | `a7921e92d1cc4a9d15410ff84eb75f57b1edeeea18394748c04a6dbc851974f5` | `5f27d4e2fba90cda2cd69ee534e865174c31ba1f` | `specifications/RP-023_v0.2_DRAFT_07C-02.md` |

## 3. 配布経路・原本の扱い

- **3AI GitHub経路:** 第2節の22件の固定参照先と `COMMON-REQUEST` を使用する。`DISTRIBUTION-MANIFEST` 行は当時の旧Manifest原本の**比較証拠**であり、本書の配布規則を上書きしない。
- **Gemini統合Markdown経路:** 22個の `SPE-SOURCE-BYTES-START` / `SPE-SOURCE-BYTES-END` 枠に囲まれた原文を使用する。SOURCE一覧の `DISTRIBUTION-MANIFEST` は歴史的原本であり、配布規則は**本Manifestと正式発出指示書**が優先する。統合Markdown本体のSHA-256・サイズ・識別は、発出時の別レシートに明記する。
- `CHECKLIST` はPLの発出前管理資料であり、22件のレビュワー必須原本には含めない。
- レビュー対象は1件。22件をそれぞれ独立のレビュー対象と数えない。各原本の役割・版・SHAを混同しない。

## 4. 受領判定と独立レビュー回答

- レビュワーは自身の取得・検証経路、原本識別、実バイトSHA-256／サイズ照合、取得不能・代替証拠を明記する。受領READYとレビュー本文開始の条件は**正式発出指示書**の明示的承認に従う。
- 共通依頼書の重点質問に従い、原16 Findingを個別に評価する。新規Findingは別枠とし、原Findingの件数・Severityを勝手に変更しない。
- 回答は単一の個別Markdown原本とする。ZIP禁止。結果は Accepted / Revision Recommended / Rejected のいずれかを根拠とともに示す。
- TECHNICAL STOP、EVIDENCE STOP、NORMATIVE STOP、OWNER AUTHORIZATION PENDINGを区別し、既存PASSと未検証範囲を残す。
- レビュワーによるGitHub書込み、正式Acceptance、Finding Close、DecisionLog更新、Freeze、HOLD解除、Canonical化は禁止。

## 5. Snapshotの識別境界

本Manifestは**原本集合・取得先・受領検証条件**を固定する文書であり、GitHub保全実績や送達履歴の逐次管理台帳ではない。Manifest自体の最終Commit／SHA-256、Gemini統合Markdownの最終SHA-256、OwnerによるSnapshot承認・正式発出日時・送達証拠は、**本書とは別の発出レシート**に記載し、本書とセットでレビュワーへ提示する。発出レシートが存在しない状態で本書単独を正式発出指示と解釈しない。

---

**配布管理注記（レビュー本文ではない）:** このファイルはOwnerのCommit裁定に供する改訂候補。GitHub書込み・Gemini再更新・正式発出は本ファイル生成だけでは実行されない。
