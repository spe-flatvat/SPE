# FG-06｜限定再レビュー 配布候補固定Manifest v0.2 DRAFT

- 状態：**CANDIDATE FIXED LOCALLY / NOT OWNER-APPROVED FOR DISPATCH / STOP**
- Repository: `spe-flatvat/SPE`; immutable commit `0a7e3af9e73f37821c3de05f06ebb043965b274e`
- Owner S-01〜S-04: 案A採用。4AI配布・レビュー開始は別途承認。
- 対象：限定・非極小 L1〜L4。差分全文、直接依存条項実質審査、CC-01〜13/29 invariants/既存Finding横断、必要原本照合。
- GitHub固定3DEC Git blob SHA-1: `6080ee8ba12b780ed6444695f907ede68cf5a15c`（接続済GitHubから取得）。同梱原本のGit blob再計算と一致。
- 固定3DECローカル実バイトSHA-256: `fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848`。
- 旧Finding原回答4件およびcrosswalkは、旧パケット内の固定コピーを再利用。各Findingの意味論的Dispositionを確定したものではない。
- `reference/` はレビュー上の必要箇所に参照する固定証拠。全件再監査の指示ではない。
- SHA-256はこの候補ZIPに収録したローカル実バイトに対する計算。GitHubで原本を確認したことと各ファイルのGitHub原本一致は区別する。

## 固定ファイル台帳

| ZIP内パス | 区分 | bytes | SHA-256 | Git blob SHA-1 |
|---|---|---:|---|---|
| `reference/inputs/FG06_CAND_Rev4_3DEC.md` | 条件付き参照（固定同梱） | 38214 | `fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848` | `6080ee8ba12b780ed6444695f907ede68cf5a15c` |
| `reference/old_packet/inputs/M19_Control_Contract_v0.4_DRAFT_Rev2.md` | 条件付き参照（固定同梱） | 28034 | `6a55197c1e530fbbcd222f859107573c04326254c1dfb6524b7ab001d7b58cea` | `f00fe1208de0ced322c39846ee565ca39ecf2882` |
| `reference/old_packet/inputs/SPE_M19_25_FG05_Rev2_Rev4_Independent_Audit_20261025.md` | 条件付き参照（固定同梱） | 38515 | `d3cc9aa36577cefcdfa6c049ccbb6d4a0d90b5d5b288aac3cf2cd18bf65c5099` | `12f3a8c961dd1321c78cc93ec81706bcacd2d6cb` |
| `reference/old_packet/inputs/Step_6D35_Owner_Provided_Audit_Transcript_DRAFT.md` | 条件付き参照（固定同梱） | 9689 | `55ab7ad1b9f7edac54685eadc4a546525a2eccb65af9564575b79c6fbc7837ed` | `2ce5f8eb9607475c566f6a82627df0f26da42eae` |
| `reference/old_packet/references/docs/DecisionLog.md` | 条件付き参照（固定同梱） | 7691 | `a9863a6c3b5b5bf32aa1de6e328c6f6ad7e007bbda4ffd35bfd8af63788f0ae1` | `9d1fdbe86567be56c19be051262f92746a984704` |
| `reference/old_packet/references/docs/Workflow.md` | 条件付き参照（固定同梱） | 3402 | `b9727a775f8d0d25a7b5fc57bd4c74a8df289f92666ed6d8bd889bc084559e14` | `9293cbfce3532cc815c20ef20c4bd76377dd8598` |
| `reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md` | 条件付き参照（固定同梱） | 22074 | `736bcd20e6e8d3817ca908ee692d4cc324c0de9e584753889bc1b80b76e295be` | `77ee33a1e4a0af48a0bee79b3ae94121373cffb0` |
| `reference/prior_reviews/Claude_FG06_original.md` | 条件付き参照（固定同梱） | 21473 | `913aea30d653f3667a4b1f82f8a20f63e4f1f600d8f11317df8e94c0237a0591` | `22d7995aa3cad1080f5535c56fd971c12e1eddbb` |
| `reference/prior_reviews/Gemini_Rev4_FG06_20261025.md` | 条件付き参照（固定同梱） | 9288 | `4b3094f899cd468c205e75f4de19d73abc72b4f17d77f711085bc0e5b63b1433` | `501a25d6845fa63e51808139ff3f89e8926dde39` |
| `reference/prior_reviews/Grok_Rev4_FG06_20261025.md` | 条件付き参照（固定同梱） | 11920 | `6f5b58146acca3dc6890364b95cc99b25060db69c6e903dfbb94d7467ecb22c3` | `aa3bbf92cb5d220a6f1beed3549e9fe20a171771` |
| `reference/references/FG06_4AI_CROSSWALK_DRAFT.md` | 条件付き参照（固定同梱） | 7461 | `7379d6b2e41c0d0d440543e23bebd627600227ac0ee89c172c9ce640f5819ccf` | `ae1b807e8dd4e79af1b682883373d5d44ad5aa33` |
| `required/FG06_Common_Review_Request_v0.1_DRAFT.md` | 必読 | 2755 | `dc67e6e358cb9f8a766b6ffbaddae0f63c3829d951c28afa3672af332be157b8` | `8f65c283c89b714682bb14273068ac829c0d3b1a` |
| `required/FG06_Integrated_Changes.patch` | 必読 | 3156 | `1f6a8ab716d470f665b39ff24561cfcbc71f9dacf9fcd09a16033cb8e233f220` | `e3c64f0710703599f0a6f70d6e9866c4e1edeb53` |
| `required/FG06_Limited_Review_Scope_Contract_v0.1_DRAFT.md` | 必読 | 3202 | `37ba62609d1775d937f532b40ed1f6dce937a249a44813c70a105247dd0cd5f7` | `fb8e7449ca79b08db5f58eedfdf4ca63729fd6a0` |
| `required/FG06_R01_R07_Integrated_Decision_Register_DRAFT.md` | 必読 | 3229 | `d0d943fa5e696f841b1a729c6773d2da7a9522085e7e12869c48c5032b1f0072` | `54abe15768a244d066d235ce8c49cd2697c42449` |
| `required/FG06_Review_Checklist_v0.1_DRAFT.md` | 必読 | 1722 | `d19f98a0ef1bbd77a9a94b1cb43caaf193330628b560256ba623411bffbdc43f` | `58cef3f161f1eeae63c78d9c1bb58a3b2bc54cf1` |
| `required/FG06_Traceability_Regression_Report_DRAFT.md` | 必読 | 4158 | `e80956fc6e99bf84d480bae8a09c999a51414c5778aa44a4ce2c32bc0275a391` | `5ca85531f867e840a3b4ce199c8d6cd0efd18a15` |
| `required/M19_Control_Contract_Integrated_Candidate_DRAFT.md` | 必読 | 39146 | `4a3b475abb1281c7bf25b27bc23c0e67b3f0abd3e494222404f607d7c6cc16c1` | `09b8d58e7f354bf09f8c19b812075e7e3c825c76` |

## 配布前受領ゲート

1. Ownerがこの固定候補の版・内容・SHAと4AI配布を**別途明示承認**する。
2. 各AIに同一ZIP実バイト、同一Request/Scope/Checklistを配布する。
3. 各AIは受領時にZIPおよびManifest記載の実バイトSHA-256を確認する。全件照合不可なら未了と記録し、Ownerの個別代替承認なしにレビュー開始しない。
4. AI間の回答相互閲覧は禁止。証拠不足やMajor依存を発見した場合、範囲拡張理由を記録しOwnerに照会する。
5. Finding Close、Review Acceptance、Freeze、GitHub書き込み、DecisionLog更新はこの工程で許可しない。

## 残存する証拠上の限界

- E-03/E-04の歴史的原承認は未検証。R-01の新規起案根拠は歴史的証明ではない。
- 旧パケット原回答とcrosswalkはコピーの実バイトを固定したものであり、4AI Finding全件の独立再評価は未実施。
- 4AI配布・受領、独立レビュー、29 Invariantsの実V&Vは未実施。
