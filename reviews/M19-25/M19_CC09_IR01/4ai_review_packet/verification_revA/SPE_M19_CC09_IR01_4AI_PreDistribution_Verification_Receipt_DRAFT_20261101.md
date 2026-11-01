# SPE M19-CC09-IR-01｜4AI配布前・GitHub固定版受領検証レシート DRAFT

**Status:** DRAFT / EVIDENCE ONLY / NON-CANONICAL / NOT ISSUED
**Repository:** `spe-flatvat/SPE`
**主対象固定Commit:** `c3310a510f44c9c5ea36b1423814aafc7bda6e1d`
**検証日:** 2026-11-01

## 検証手段と限界

接続済みGitHub連携の `fetch_file` で指定Commitの各文書を全文取得し、取得されたUTF-8文字列をUTF-8バイト列へ変換してSHA-256を算出した。SHA-256実装は既知テスト文字列 `abc` に対する標準値 `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` と一致した。主対象7件は事前固定SHA-256と一致した。参照10件は固定Commitから全文取得し、SHA-256を記録した（Rev.2のみ事前固定値との一致確認あり）。これはGitHub APIが返した全文に対する照合であり、GitHubのGit Blob IDをSHA-256と同一視しない。

## 検証結果（17件）

| 区分 | 固定Commit | Repository相対パス | SHA-256 | UTF-8 Bytes | 判定 |
|---|---|---|---|---:|---|
| MAIN | `c3310a510f44c9c5ea36b1423814aafc7bda6e1d` | `reviews/M19-25/M19_CC09_IR01/4ai_review_packet/SPE_M19_CC09_IR01_Integrated_4AI_Manifest_DRAFT_20261101.md` | `39e392ac4f6bffa680176110e4e0f4c6d589feac0f80e0a56aaf111f60b416cc` | 3218 | PASS（事前値一致） |
| MAIN | `c3310a510f44c9c5ea36b1423814aafc7bda6e1d` | `reviews/M19-25/M19_CC09_IR01/4ai_review_packet/SPE_M19_CC09_IR01_Integrated_4AI_Common_Packet_DRAFT_20261101.md` | `c9a791f1849959f3348279228c8be1afb8d84e205d8ffe3934657645e18ebb0b` | 4692 | PASS（事前値一致） |
| MAIN | `c3310a510f44c9c5ea36b1423814aafc7bda6e1d` | `reviews/M19-25/M19_CC09_IR01/4ai_review_packet/SPE_M19_CC09_IR01_Integrated_4AI_Common_Request_DRAFT_20261101.md` | `f9f3793c57c4edbbdff4e1eb26caf852e2d1c88b8eb0462d9b5aa5737fcf1b4e` | 1481 | PASS（事前値一致） |
| MAIN | `c3310a510f44c9c5ea36b1423814aafc7bda6e1d` | `reviews/M19-25/M19_CC09_IR01/4ai_review_packet/SPE_M19_CC09_IR01_Integrated_4AI_Distribution_Checklist_DRAFT_20261101.md` | `12aeebf8e374214de372f4ce8650dcfe16c03c2466c77055dd4bcf77695015f5` | 1475 | PASS（事前値一致） |
| MAIN | `c3310a510f44c9c5ea36b1423814aafc7bda6e1d` | `reviews/M19-25/M19_CC09_IR01/integrated_draft/SPE_M19_CC09_IR01_Rev2_Integrated_Amendment_DRAFT_20261101.md` | `5e19790560c9c84f5a00e58a33e6bafd1d0140c2f9b4b88ec14134247a877129` | 44489 | PASS（事前値一致） |
| MAIN | `c3310a510f44c9c5ea36b1423814aafc7bda6e1d` | `reviews/M19-25/M19_CC09_IR01/integrated_draft/SPE_M19_CC09_IR01_Rev2_Integrated_Amendment_DIFF_20261101.patch` | `2df2c1519e74355e3d5860b1f5b178cb6f0a80b5148a86deec13a9408c0049a5` | 21779 | PASS（事前値一致） |
| MAIN | `c3310a510f44c9c5ea36b1423814aafc7bda6e1d` | `reviews/M19-25/M19_CC09_IR01/integrated_draft/SPE_M19_CC09_IR01_Integrated_DRAFT_Selfcheck_20261101.md` | `a9e90ee93fe71ce814d0e82481d8d41ce643f6d826c0a6e38db6b470231a5610` | 2613 | PASS（事前値一致） |
| REF | `754c1e2907bce67f7d58d10bf36813ac76fd1ed0` | `reviews/M19-25/M19_FR_CV_07/SPE_M19_FR_CV_06_Rev2_Convergence_Candidate_DRAFT_20261031.md` | `94286b1e8b86d19c0684c3463e77a454b49be661574be3cbbdb5b952a333e3bd` | 42852 | PASS（事前値一致） |
| REF | `754c1e2907bce67f7d58d10bf36813ac76fd1ed0` | `docs/Workflow.md` | `b9727a775f8d0d25a7b5fc57bd4c74a8df289f92666ed6d8bd889bc084559e14` | 3402 | PASS（取得・算出） |
| REF | `c96e48d19c82f318a80b01eb14bf7832913db518` | `reviews/M19-25/M19_CC09_IR01/SPE_Development_Continuity_Decision_Basis_CC09_20261101.md` | `7c85a68295d9904960eff954ae8b8d0a3e24aac2038f27b6ad7409a1d12f1eb1` | 3741 | PASS（取得・算出） |
| REF | `c96e48d19c82f318a80b01eb14bf7832913db518` | `reviews/M19-25/M19_CC09_IR01/SPE_M19_CC09_IR01_Direct_Audit_Obligations_and_Deletion_Diff_DRAFT_v02_20261101.md` | `b19e51d5a96d60c8175e559b75e81f9b0673c4aef866730a01d8dfe5d0522f35` | 14627 | PASS（取得・算出） |
| REF | `c96e48d19c82f318a80b01eb14bf7832913db518` | `reviews/M19-25/M19_CC09_IR01/SPE_M19_CC09_IR01_PreDistribution_Artifact_Register_DRAFT_v03_20261101.md` | `35bce9d55c2c5bfecdf79c4d1418ebb88b3e7f142f59b546056c6a1f25465085` | 1125 | PASS（取得・算出） |
| REF | `c96e48d19c82f318a80b01eb14bf7832913db518` | `reviews/M19-25/M19_CC09_IR01/SPE_M19_CC09_IR01_Review_Packet_PreDistribution_DRAFT_v03_20261101.md` | `6a5c89437cdaa972744db50c66e653a70f5e066e3bd75393978199a199304911` | 10554 | PASS（取得・算出） |
| REF | `da4ca873b6518449dcbd2941f58ebfd9a6eab524` | `reviews/M19-25/M19_CC09_IR01/independent_reviews/M19_CC09_IR01_Claude_Independent_Review_DRAFT_20261101.md` | `65a9c56fbce29b1a1fbe178a295c2ea7266c016120c0d9cd0af87d5a38c11f8b` | 23760 | PASS（取得・算出） |
| REF | `da4ca873b6518449dcbd2941f58ebfd9a6eab524` | `reviews/M19-25/M19_CC09_IR01/independent_reviews/SPE_M19-CC09-IR-01_Independent_Review_Report_Grok_20261101.md` | `89fbc0f954136bdc5d13dd7bb9f2b8032c5a0b59999a3b216cf9dc5388c377c7` | 6834 | PASS（取得・算出） |
| REF | `da4ca873b6518449dcbd2941f58ebfd9a6eab524` | `reviews/M19-25/M19_CC09_IR01/independent_reviews/SPE_M19_CC09_IR01_ChatGPT_Independent_Review_20261101.md` | `9f2ae8d39a832ea378abd6e7726ea4176a645babf75277daeb8b2be86d60f549` | 6840 | PASS（取得・算出） |
| REF | `da4ca873b6518449dcbd2941f58ebfd9a6eab524` | `reviews/M19-25/M19_CC09_IR01/independent_reviews/SPE_M19_CC09_IR01_Gemini_Independent_Review_20261101.md` | `523a5a3e0c44f024f88b9d6d30600535140235842f5ae7af0a1c90f23e176140` | 8953 | PASS（取得・算出） |

## 保留事項

- 旧4AIレビュー保全文書の元AI会話・原回答との独立した同一性証明は未実施。保全文書の受領と内容真正性の保証は異なる。
- 既存4AI Findingの正式Close、Owner裁定、規範内容の独立再レビュー、Freezeは未実施。
- このレシートは取得・照合結果の記録であり、配布・レビュー開始承認ではない。
- 本レシート自体のGitHub保全Commitは未固定。配布に先立ち新規DRAFTを限定Commit・Pushし、GitHub固定Commitで再検証すること。
