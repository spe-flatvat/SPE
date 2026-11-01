# SPE M19-CC09-IR-01｜受領・実バイト検証レシート DRAFT

**Status:** DRAFT / NON-CANONICAL / READ-ONLY AUDIT  
**日付:** 2026-11-01（JST）  
**既存原本・Owner裁定は変更しない。M19–25／RP-023 HOLD維持。**

## 1. 受領判定

**PASS（今回の固定入力取得・実バイト/Git blob/サイズ照合）。** 主比較3資料を直接取得できたため、ユーザー指示に従い追加の開始許可を待たず本文監査を実施した。これは規範合格・Owner承認・Freezeではない。

| 役割 | 固定Commit | Repository相対パス | bytes／行 | SHA-256 | Git blob SHA-1 |
|---|---|---|---|---|---|
| base | 754c1e2907bce67f7d58d10bf36813ac76fd1ed0 | reviews/M19-25/M19_FR_CV_07/SPE_M19_FR_CV_06_Rev2_Convergence_Candidate_DRAFT_20261031.md | 42852／544 | 94286b1e8b86d19c0684c3463e77a454b49be661574be3cbbdb5b952a333e3bd | 9d690954e16ba6cd0ceed4172d6d09b0fc10e823 |
| draft | edc47652f986b75341404154bfd3057da89e9329 | reviews/M19-25/M19_CC09_IR01/integrated_draft/SPE_M19_CC09_IR01_Rev2_Integrated_Amendment_DRAFT_20261101.md | 44489／520 | 5e19790560c9c84f5a00e58a33e6bafd1d0140c2f9b4b88ec14134247a877129 | 9211b29b673a72bed333a151e433d15fd72547c0 |
| workflow | 754c1e2907bce67f7d58d10bf36813ac76fd1ed0 | docs/Workflow.md | 3402／62 | b9727a775f8d0d25a7b5fc57bd4c74a8df289f92666ed6d8bd889bc084559e14 | 9293cbfce3532cc815c20ef20c4bd76377dd8598 |

## 2. 取得/照合方法

接続済みGitHub連携fetch_fileに固定refとencoding=base64を指定し、Base64復号した実バイトからSHA-256・サイズ・Git blob SHA-1をPython標準ライブラリで計算した。文字列再保存・改行正規化後のハッシュを代用していない。base/draftのcommit/treeを各指定Commitで取得し、パス・blob・sizeを照合。3/3一致。treeはtruncated=false。公開Web検索・既存4AI結論を本文取得の代用としていない。

主比較対象の期待SHAはユーザー指示には未記載。対象2本文は既存配布Manifestの94286b1e…／5e197905…とも一致する。Workflowは今回指定Commitのtreeと実バイトで確認し、今回の実測b9727a77…を記録した。独立の事前期待SHAとの照合が別途あったと創作しない。commit/tree自体のシリアライズSHA再計算・署名認証は未実施。両比較本文はUTF-8 BOMなし・CRなし・内部LF区切り・終端LFなしで一致しており、行対照で隠れる改行形式差はない。

## 3. 参考資料の受領

指定保全Commitから4AI原報告・横断報告・引継ぎ・2Manifest等を取得。評価骨格と全文diffの先行観察を作った後に4AI原本文を読んだ。原レビューは根拠の索引として扱い、原文差分を代替しない。

| 資料パス | Commit | bytes／行 | 実測SHA-256 | Git blob SHA-1 |
|---|---|---|---|---|
| reviews/M19-25/M19_CC09_IR01/4ai_integrated_review_preservation_20261101/SHA256SUMS.txt | 987bb4309255ce27586c703ce10c8889f098d4ec | 845／6 | a8a7f54768dcabd8a004cfdd6e015e5c8da0aca6664b394087ddc33db84de76a | ee461f2d5d44a69c82a55e24c0433749cbff70d4 |
| reviews/M19-25/M19_CC09_IR01/4ai_integrated_review_preservation_20261101/SHA256_MANIFEST_DRAFT_20261101.json | 987bb4309255ce27586c703ce10c8889f098d4ec | 1666／42 | 27af6f8022d7ad853bf01e1c5496d03650590c23da1d05de4c12aaf2876e4a06 | 49636e48e848c83afd004717be199d16d8a11dc4 |
| reviews/M19-25/M19_CC09_IR01/4ai_integrated_review_preservation_20261101/analysis/SPE_M19_CC09_IR01_4AI_Cross_Review_DRAFT_20261101.md | 987bb4309255ce27586c703ce10c8889f098d4ec | 7489／62 | d4e39b8a16eab56033887b670b71113f6d5eff473aba44e6285b68be4fc032fa | c5109facae8703a576f0266e069068a21f31d4c8 |
| reviews/M19-25/M19_CC09_IR01/4ai_integrated_review_preservation_20261101/analysis/SPE_M19_CC09_IR01_Termux_Handoff_DRAFT_20261101.md | 987bb4309255ce27586c703ce10c8889f098d4ec | 1839／24 | 7a56825be7fcfce63683e216e51b9cc2f238f7c80d8fa81b3ebc6b8fb92cf30f | b27a02ecb00bcc96c56fc43efe015c6f98a4977f |
| reviews/M19-25/M19_CC09_IR01/4ai_integrated_review_preservation_20261101/originals/M19_CC09_IR01_Integrated_DRAFT_Claude_Independent_Review_DRAFT_20261101.md | 987bb4309255ce27586c703ce10c8889f098d4ec | 20014／169 | 807bbbf24944ca3d2562b33ad7d1e81ea3d5caf7a2aaaf6b88f8fbaea5ec756f | ef40bf6ddc4fe26df13dec8f298b74e7d3498779 |
| reviews/M19-25/M19_CC09_IR01/4ai_integrated_review_preservation_20261101/originals/SPE_M19-CC09-IR-01_Integrated_Independent_Review_Report_Grok_20261101.md | 987bb4309255ce27586c703ce10c8889f098d4ec | 6506／139 | 758bfd622c26e3a5897c1d28e46aa85b5f6a046b4d670ac3a0c5e16937c2be0b | 1021fc285342d37200529aa9f54338ddbdc6f8cc |
| reviews/M19-25/M19_CC09_IR01/4ai_integrated_review_preservation_20261101/originals/SPE_M19_CC09_IR01_ChatGPT_Final_Independent_Review_20261101.md | 987bb4309255ce27586c703ce10c8889f098d4ec | 10018／162 | 180ed9855aba2dbd745e5a052ed5cd8a8511c39a175003962aa6707afa0013f2 | 789b57544aba8e1687f869f755c34140f58bfbad |
| reviews/M19-25/M19_CC09_IR01/4ai_integrated_review_preservation_20261101/originals/SPE_M19_CC09_IR01_Gemini_Integrated_Review_Conversation_Extract_20261101.md | 987bb4309255ce27586c703ce10c8889f098d4ec | 3502／48 | 9bd3874b1939779bc8fe9f9ca71bc4a7428ea1f8ededc354b42393f10c56ae91 | e81650909bed2b643beb3b704cfcd05d6cc7a7aa |
| reviews/M19-25/M19_CC09_IR01/4ai_review_packet/SPE_M19_CC09_IR01_Integrated_4AI_Common_Packet_DRAFT_20261101.md | 987bb4309255ce27586c703ce10c8889f098d4ec | 4692／42 | c9a791f1849959f3348279228c8be1afb8d84e205d8ffe3934657645e18ebb0b | d37104ff60d083faf5a8ac3d373f9de4c15cdb6e |
| reviews/M19-25/M19_CC09_IR01/4ai_review_packet/SPE_M19_CC09_IR01_Integrated_4AI_Manifest_DRAFT_20261101.md | 987bb4309255ce27586c703ce10c8889f098d4ec | 3218／36 | 39e392ac4f6bffa680176110e4e0f4c6d589feac0f80e0a56aaf111f60b416cc | 41361eeb6a236c7b5b000a18cf17348c1dffdfdc |
| reviews/M19-25/M19_CC09_IR01/SPE_Development_Continuity_Decision_Basis_CC09_20261101.md | 987bb4309255ce27586c703ce10c8889f098d4ec | 3741／49 | 7c85a68295d9904960eff954ae8b8d0a3e24aac2038f27b6ad7409a1d12f1eb1 | cfedf5b44bb6052bf05d4c38557eacc77815aa01 |

4AI保全ディレクトリのSHA256SUMSは原報告4＋分析2＝6/6一致。JSON manifestの6件も同じサイズ・SHAと一致。SUMSとJSON自身は自己ハッシュ期待値の対象外。Gemini資料は非逐語の会話抽出と明記されており、元回答の完全保全・真正性を認定しない。他3資料も保存ファイル同一性と元AI発話真正性は別。

## 4. STOP/未検証

取得失敗・期待値不一致・指定版同定不能は検出しなかった。動的実行、全歴史原記録、Owner原会話の独立認証、DecisionLogの現登録状態、Rev.A配布3資料の期待値照合は未実施。これらを本監査開始の追加ゲートにせず、既決B-OD-01〜05の再審議・原会話全回収も要求しない。最終原本SHA再照合は5番の自己監査に記録する。

