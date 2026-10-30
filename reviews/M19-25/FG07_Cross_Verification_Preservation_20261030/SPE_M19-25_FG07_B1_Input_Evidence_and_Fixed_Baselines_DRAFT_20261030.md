# SPE M19–25｜FG-07 B1 入力証拠一覧・固定基準表 DRAFT

- 作成日：2026-10-30（JST）
- Status：DRAFT / NON-CANONICAL / OWNER DISPOSITION PENDING
- 工程：FG-07 横断検証本文（分析・新規DRAFTのみ）
- 固定入力：P=`789403ae904594a0973ed7c7a142745a75595320`／R=`d36ae4428d35105bed4fbedc72c7db1500330655`
- 対象統合候補SHA-256：`4a3b475abb1281c7bf25b27bc23c0e67b3f0abd3e494222404f607d7c6cc16c1`
- M19–25／RP-023：HOLD継続。正式Close／Review Acceptance／Canonical化／Freezeは実施しない。

## 1. 受領確認と本工程の権限

2026-10-30、本会話に添付された「FG-07横断検証本文 Work作業指示書」と「発出レシート」を読取・受領した。指示書SHA-256はレシートの期待値と一致。今回は横断検証本文の読取・照合・分析・5種の新規DRAFT作成が許可されている。

準備工程の「本文開始HOLD」は、準備当時の記録として維持する。今回の別指示により本文分析に進んだことを新記録で示し、準備成果物や添付原本を書き換えない。M19–25／RP-023の全体HOLD解除・規範改訂・正式処分は許可されていない。

| 受領資料 | 期待値・計測 | 結果 |
|---|---|---|
| `SPE_M19-25_FG07_Cross_Verification_Work_Instruction_20261030.md` | 6,914 bytes／SHA-256 `e463ad96c556e1ca94e6886cad9c71fe7d396c104f6f069b69434572a78dc03f` | 読取 VERIFIED／レシート期待SHAと一致 |
| `SPE_M19-25_FG07_Cross_Verification_Issuance_Receipt_20261030.md` | 1,776 bytes／SHA-256 `4afb8c801032c50015e24020637e61ed77d2da311adecf83682c0a4b2fbdd395` | 読取 VERIFIED／今回計測値。外部期待SHA提示なし |

Work指示書の期待SHAは `e463ad96c556e1ca94e6886cad9c71fe7d396c104f6f069b69434572a78dc03f`。SHA一致は添付指示書の同一性確認であり、歴史的Owner裁定や規範内容の承認証明ではない。

## 2. 固定入力と版の分離

| 識別子 | 固定先 | 用途 |
|---|---|---|
| P | `789403ae904594a0973ed7c7a142745a75595320` | 配布パケット。[FG06_Distribution_Manifest_v0.2_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/FG06_Distribution_Manifest_v0.2_DRAFT.md)。Manifest＋18件 |
| R | `d36ae4428d35105bed4fbedc72c7db1500330655` | 今回4AI回答＋保全台帳。[FG06_Limited_4AI_Response_Preservation_Register_DRAFT_20261029.md](https://github.com/spe-flatvat/SPE/blob/d36ae4428d35105bed4fbedc72c7db1500330655/reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/FG06_Limited_4AI_Response_Preservation_Register_DRAFT_20261029.md) |
| 統合候補 | [M19_Control_Contract_Integrated_Candidate_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md) | 今回の条項照合対象。SHA-256 `4a3b475abb1281c7bf25b27bc23c0e67b3f0abd3e494222404f607d7c6cc16c1` |
| 3DEC候補 | Pのreference/inputs/FG06_CAND_Rev4_3DEC.md | 直前統合元。SHA-256 `fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848` |
| 原Rev.4 | Pの先行パケットinputs/FG06_ORIG_Rev4.md | SHA-256 `d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e`。統合候補と別版・不変 |
| 先行保存基準 | `0a7e3af9e73f37821c3de05f06ebb043965b274e` | Request等の作成時固定元。P/Rの代替にしない |
| 旧レビュー基準 | `231a983d4467c3427f6a782bf336e5b3f49ced2f` | 旧20 Findingの原回答基準。今回はP同梱コピーを照合 |
| 歴史的Owner-confirmed baseline | `e2238922193107f204805d9f25d6ddd6f764eced` | 本文の歴史的参照。今回mainの再確認・変更を意味しない |

## 3. 取得経路と再利用の検査

準備工程が接続済みGitHub連携からP/Rを指定して取得した26ファイルを再利用した。各ファイルの保存SHA-256を準備時inventoryと比較し26/26一致、準備4成果物も4/4変更なし。指示書B1に従い、不要な再ダウンロード・GitHub呼出・再受領工程は実行していない。

先行検査は返却テキストをUTF-8保存しGit blobを再計算した経路であり、26/26でtreeのGit blobと一致、Manifest記載18件と回答台帳記載4件のサイズ／SHAが一致した。この事実を維持するが、raw/Base64直接転送の検査とは呼ばない。今回の再利用確認もGrok／ChatGPT本人の過去の受領SHA未完了をPASSへ変更しない。

Claudeは添付原本保存との台帳記載があるが、元添付との独立別経路照合は未実施。ChatGPT／Gemini／Grokの3回答はチャット貼付からの再構成版で、元AI出力とのバイト一致はNOT VERIFIED。以下の引用はRに固定された保存版の行を指す。

| AI | 原Verdict（維持） | 新ID数 | 保存版の同一性 | 元出力との関係 |
|---|---|---:|---|---|
| ChatGPT | REVISE | 4 | 9850 bytes／`1717b82dcd5a0fff683a9d68b1710b4a0fe47c41e6364df5ca968f082fc13223` | 再構成保存版。元AI出力同一性NOT VERIFIED |
| Claude | REVISE（軽微修正との説明を含む。原文L16） | 5 | 16592 bytes／`af1fdcddb76db53b248ffeee2744dd6b71896314d505b3589820df2c1e37d50d` | 添付保存との記載。今回の別経路原本照合は未実施 |
| Gemini | CONDITIONAL ACCEPT | 1 | 9405 bytes／`90836efda65ca339763064517e0ec013604a629f414238352d3e0770a546fb14` | 再構成保存版。元AI出力同一性NOT VERIFIED |
| Grok | CONDITIONAL ACCEPT | 2 | 7467 bytes／`27cf4e312d7d82b6885f8b9e159b79e2fbdda84d91a7dc15c842284a108f466c` | 再構成保存版。元AI出力同一性NOT VERIFIED |

## 4. GitHub固定資料26件

全行の取得経路は準備工程の接続済みGitHub連携→保存テキスト、今回の再利用SHA照合。読取・保存版識別はVERIFIED。資料中の承認主張、実行結果や元AI同一性が自動的にVERIFIEDになるものではない。

| 資料 | commit | bytes／行 | 保存SHA-256 | 本文参照 |
|---|---|---|---|---|
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/FG06_Distribution_Manifest_v0.2_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/FG06_Distribution_Manifest_v0.2_DRAFT.md) | P | 6172／48 | `cc2d1e083142caa6e3ecaf4010b96405b009891b82286163761bf0b787d4c4a2` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/references/FG06_4AI_CROSSWALK_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/references/FG06_4AI_CROSSWALK_DRAFT.md) | P | 7461／75 | `7379d6b2e41c0d0d440543e23bebd627600227ac0ee89c172c9ce640f5819ccf` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Common_Review_Request_v0.1_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Common_Review_Request_v0.1_DRAFT.md) | P | 2755／28 | `dc67e6e358cb9f8a766b6ffbaddae0f63c3829d951c28afa3672af332be157b8` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Integrated_Changes.patch](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Integrated_Changes.patch) | P | 3156／32 | `1f6a8ab716d470f665b39ff24561cfcbc71f9dacf9fcd09a16033cb8e233f220` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Limited_Review_Scope_Contract_v0.1_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Limited_Review_Scope_Contract_v0.1_DRAFT.md) | P | 3202／28 | `37ba62609d1775d937f532b40ed1f6dce937a249a44813c70a105247dd0cd5f7` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_R01_R07_Integrated_Decision_Register_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_R01_R07_Integrated_Decision_Register_DRAFT.md) | P | 3229／42 | `d0d943fa5e696f841b1a729c6773d2da7a9522085e7e12869c48c5032b1f0072` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Review_Checklist_v0.1_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Review_Checklist_v0.1_DRAFT.md) | P | 1722／30 | `d19f98a0ef1bbd77a9a94b1cb43caaf193330628b560256ba623411bffbdc43f` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Traceability_Regression_Report_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/FG06_Traceability_Regression_Report_DRAFT.md) | P | 4158／50 | `e80956fc6e99bf84d480bae8a09c999a51414c5778aa44a4ce2c32bc0275a391` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md) | P | 39146／536 | `4a3b475abb1281c7bf25b27bc23c0e67b3f0abd3e494222404f607d7c6cc16c1` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/FG06_Limited_4AI_Response_Preservation_Register_DRAFT_20261029.md](https://github.com/spe-flatvat/SPE/blob/d36ae4428d35105bed4fbedc72c7db1500330655/reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/FG06_Limited_4AI_Response_Preservation_Register_DRAFT_20261029.md) | R | 3009／41 | `7f730e884ef9925210c9fd18f433debc1674a63240fd7ffff990c75a2a152de9` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/M19_25_ChatGPT_FG06_Limited_Rereview_Independent_Review_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/d36ae4428d35105bed4fbedc72c7db1500330655/reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/M19_25_ChatGPT_FG06_Limited_Rereview_Independent_Review_DRAFT.md) | R | 9850／175 | `1717b82dcd5a0fff683a9d68b1710b4a0fe47c41e6364df5ca968f082fc13223` | 新回答の原ID・原文・Severity |
| [reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/M19_25_Claude_FG06_Limited_Rereview_Independent_Review_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/d36ae4428d35105bed4fbedc72c7db1500330655/reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/M19_25_Claude_FG06_Limited_Rereview_Independent_Review_DRAFT.md) | R | 16592／114 | `af1fdcddb76db53b248ffeee2744dd6b71896314d505b3589820df2c1e37d50d` | 新回答の原ID・原文・Severity |
| [reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/M19_25_Gemini_FG06_Limited_Rereview_Independent_Review_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/d36ae4428d35105bed4fbedc72c7db1500330655/reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/M19_25_Gemini_FG06_Limited_Rereview_Independent_Review_DRAFT.md) | R | 9405／83 | `90836efda65ca339763064517e0ec013604a629f414238352d3e0770a546fb14` | 新回答の原ID・原文・Severity |
| [reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/M19_25_Grok_FG06_Limited_Rereview_Independent_Review_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/d36ae4428d35105bed4fbedc72c7db1500330655/reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/M19_25_Grok_FG06_Limited_Rereview_Independent_Review_DRAFT.md) | R | 7467／107 | `27cf4e312d7d82b6885f8b9e159b79e2fbdda84d91a7dc15c842284a108f466c` | 新回答の原ID・原文・Severity |
| [docs/DecisionLog.md](https://github.com/spe-flatvat/SPE/blob/d36ae4428d35105bed4fbedc72c7db1500330655/docs/DecisionLog.md) | R | 7691／114 | `a9863a6c3b5b5bf32aa1de6e328c6f6ad7e007bbda4ffd35bfd8af63788f0ae1` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/inputs/FG06_CAND_Rev4_3DEC.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/inputs/FG06_CAND_Rev4_3DEC.md) | P | 38214／533 | `fce55ac833abb06085340e6bb903939c2121bc6387d07c4d04ddd23cfde6b848` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/inputs/M19_Control_Contract_v0.4_DRAFT_Rev2.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/inputs/M19_Control_Contract_v0.4_DRAFT_Rev2.md) | P | 28034／183 | `6a55197c1e530fbbcd222f859107573c04326254c1dfb6524b7ab001d7b58cea` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/inputs/SPE_M19_25_FG05_Rev2_Rev4_Independent_Audit_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/inputs/SPE_M19_25_FG05_Rev2_Rev4_Independent_Audit_20261025.md) | P | 38515／362 | `d3cc9aa36577cefcdfa6c049ccbb6d4a0d90b5d5b288aac3cf2cd18bf65c5099` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/inputs/Step_6D35_Owner_Provided_Audit_Transcript_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/inputs/Step_6D35_Owner_Provided_Audit_Transcript_DRAFT.md) | P | 9689／183 | `55ab7ad1b9f7edac54685eadc4a546525a2eccb65af9564575b79c6fbc7837ed` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/references/docs/DecisionLog.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/references/docs/DecisionLog.md) | P | 7691／114 | `a9863a6c3b5b5bf32aa1de6e328c6f6ad7e007bbda4ffd35bfd8af63788f0ae1` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/references/docs/Workflow.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/old_packet/references/docs/Workflow.md) | P | 3402／62 | `b9727a775f8d0d25a7b5fc57bd4c74a8df289f92666ed6d8bd889bc084559e14` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md) | P | 22074／398 | `736bcd20e6e8d3817ca908ee692d4cc324c0de9e584753889bc1b80b76e295be` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md) | P | 21473／165 | `913aea30d653f3667a4b1f82f8a20f63e4f1f600d8f11317df8e94c0237a0591` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Gemini_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Gemini_Rev4_FG06_20261025.md) | P | 9288／60 | `4b3094f899cd468c205e75f4de19d73abc72b4f17d77f711085bc0e5b63b1433` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md) | P | 11920／194 | `6f5b58146acca3dc6890364b95cc99b25060db69c6e903dfbb94d7467ecb22c3` | 固定根拠・条文・履歴・参考資料 |
| [reviews/M19-25/FG06-REREVIEW-3DEC-20261027-DRAFT-01/inputs/FG06_ORIG_Rev4.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-REREVIEW-3DEC-20261027-DRAFT-01/inputs/FG06_ORIG_Rev4.md) | P | 37939／531 | `d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e` | 固定根拠・条文・履歴・参考資料 |

## 5. 裁定関連E2資料

以下14件は準備工程でLibraryから全文読取した資料を参照。返却本文を保存したもので、Library原ファイルraw再取得のSHA照合はしていない。Owner原メッセージの直接参照、本人性、原発言日時は未検証。レシートの作成日と発言日時を同一視しない。

| 資料 | 出典 | 役割・制限 |
|---|---|---|
| `SPE_FG06_R01_Owner_Decision_A_Receipt_20261028.md` | [SPE_FG06_R01_Owner_Decision_A_Receipt_20261028.md](https://chatgpt.com/library?file_id=libfile_388c227e85b481918035c1be61e1f5d8&account_id=personal)／46行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_FG06_R01_R07_Owner_Decision_Status_Register_20261028_DRAFT.md` | [SPE_FG06_R01_R07_Owner_Decision_Status_Register_20261028_DRAFT.md](https://chatgpt.com/library?file_id=libfile_385d9fb12b888191a57a97e9d04379c0&account_id=personal)／27行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_M19-25_FG06_DEC-CAND-03_CC-08_Owner_Decision_Receipt_DRAFT_20261027.md` | [SPE_M19-25_FG06_DEC-CAND-03_CC-08_Owner_Decision_Receipt_DRAFT_20261027.md](https://chatgpt.com/library?file_id=libfile_f994624ff19481918df2dddbe9a31b20&account_id=personal)／54行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_M19-25_FG06_DEC-CAND-02_CC-01_Owner_Decision_Receipt_DRAFT_20261027.md` | [SPE_M19-25_FG06_DEC-CAND-02_CC-01_Owner_Decision_Receipt_DRAFT_20261027.md](https://chatgpt.com/library?file_id=libfile_ecbdaa96b3048191af447b8d7c1cb7e5&account_id=personal)／48行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_M19-25_FG06_DEC-CAND-01_CC-03_Owner_Decision_Receipt_DRAFT_20261027.md` | [SPE_M19-25_FG06_DEC-CAND-01_CC-03_Owner_Decision_Receipt_DRAFT_20261027.md](https://chatgpt.com/library?file_id=libfile_d98c5c2285008191bed3b32bebbfc13b&account_id=personal)／38行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_FG06_R02_Owner_Decision_R03_Transition_Receipt_20261028.md` | [SPE_FG06_R02_Owner_Decision_R03_Transition_Receipt_20261028.md](https://chatgpt.com/library?file_id=libfile_653dd01ea5b0819192245f658baef234&account_id=personal)／20行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_FG06_R03_Owner_Decision_R04_Transition_Receipt_20261028.md` | [SPE_FG06_R03_Owner_Decision_R04_Transition_Receipt_20261028.md](https://chatgpt.com/library?file_id=libfile_41225431ab608191a10c6f9b1e3ccfc7&account_id=personal)／21行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_FG06_R04_Owner_Decision_R05_Transition_Receipt_20261028.md` | [SPE_FG06_R04_Owner_Decision_R05_Transition_Receipt_20261028.md](https://chatgpt.com/library?file_id=libfile_1aed01081ba481919a10a37549e3ca34&account_id=personal)／12行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_FG06_R05_Owner_Decision_R06_Transition_Receipt_20261028.md` | [SPE_FG06_R05_Owner_Decision_R06_Transition_Receipt_20261028.md](https://chatgpt.com/library?file_id=libfile_965f91f9dc5c81918dc1b9bef2886131&account_id=personal)／29行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_FG06_R06_Owner_Decision_R07_Transition_Receipt_20261028.md` | [SPE_FG06_R06_Owner_Decision_R07_Transition_Receipt_20261028.md](https://chatgpt.com/library?file_id=libfile_64f5584aaf5481918504103b6c2428e4&account_id=personal)／25行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_FG06_R07_Owner_Decision_Receipt_20261028.md` | [SPE_FG06_R07_Owner_Decision_Receipt_20261028.md](https://chatgpt.com/library?file_id=libfile_a9ce39c7bb6c8191a07f5103321efda5&account_id=personal)／22行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `FG06_DIST_ROUTE_01_Owner_Decision_A_Receipt_20261029.md` | [FG06_DIST_ROUTE_01_Owner_Decision_A_Receipt_20261029.md](https://chatgpt.com/library?file_id=libfile_fd2bd50e250c81919cfd0eede57aeb58&account_id=personal)／48行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `FG06_INPUT_RECOVERY_GATE_RECEIPT_DRAFT.md` | [FG06_INPUT_RECOVERY_GATE_RECEIPT_DRAFT.md](https://chatgpt.com/library?file_id=libfile_138505ea57708191b58587f3c73f1a09&account_id=personal)／31行 | E2。原メッセージへの直接照合NOT VERIFIED |
| `SPE_FG06_R01_Reapproval_Scope_and_Owner_Decision_Proposal_v0.1_DRAFT.md` | [SPE_FG06_R01_Reapproval_Scope_and_Owner_Decision_Proposal_v0.1_DRAFT.md](https://chatgpt.com/library?file_id=libfile_1c762efdb1ec819187cc1b41dc8e7900&account_id=personal)／78行 | E2。原メッセージへの直接照合NOT VERIFIED |

本指示書§3は、2026-10-27 DEC-CAND3件と2026-10-28 FG-06 R系列7件をE2として限定分析に利用することを許可している。これはE1格上げ・歴史的承認の確定・将来Freezeへの二次証拠採用を許可するものではない。

準備時の過去チャット検索は `Personal context is unavailable for this conversation.` と返った。今回再試行しておらず、原記録を新規回収したと記録しない。歴史的R系列と2026-10-28 R系列は、E2の説明・日付・対象を付けて区別し、同名IDだけで対応付けない。

## 6. VERIFIED／NOT VERIFIEDの軸

| 軸 | 今回の状態 |
|---|---|
| 指示書の受領・期待SHA | VERIFIED |
| 再利用保存版26件と準備4成果物の不変 | VERIFIED |
| 新12・旧20のID所在、原Severityの該当表現 | VERIFIED（保存原文の範囲） |
| 今回の条文文字列・静的差分 | VERIFIED（原文比較） |
| 歴史的Owner承認、R系列の一次原文、E-03/E-04 | NOT VERIFIED／局所留保 |
| 再構成3回答と元AI出力のバイト一致 | NOT VERIFIED |
| raw/Base64直接取得による今回の全件再検証 | NOT PERFORMED |
| 全29 Invariantsの実V&V、エンジン実行 | NOT PERFORMED |
| 原Findingの正式Disposition／Close | 未確定／未実施 |

## 7. 参照した準備4成果物

- `SPE_M19-25_FG07A05_Reference_and_Primary_Evidence_Locations_DRAFT_20261030.md`：SHA-256 `074fc0a902c9db97803256f02a2ce637a2969abfc7448c5985612387d48eb444`。設計・取得状況の参考であり正式規範ではない。
- `SPE_M19-25_FG07_Fixed_Baseline_Acquisition_and_Limits_DRAFT_20261030.md`：SHA-256 `d5bdc4fbd79a564ea19748c445d7f0c41982d663bf8d541b16ec3f30f38dadeb`。設計・取得状況の参考であり正式規範ではない。
- `SPE_M19-25_FG07_Cross_Verification_Instruction_Recommendations_DRAFT_20261030.md`：SHA-256 `18148fcbea076e6a1e36e4217626fd7dd09d11ca7788b0621302f117a9053d2c`。設計・取得状況の参考であり正式規範ではない。
- `SPE_M19-25_FG07_Preparation_Owner_Report_DRAFT_20261030.md`：SHA-256 `facd19c006293f3da19aad2631e9c089dbb435a25cfc284d663e6619c1f2aa80`。設計・取得状況の参考であり正式規範ではない。

本B1は独立した新規DRAFTである。準備ファイル・原回答・候補本文・発出物を上書きしていない。
