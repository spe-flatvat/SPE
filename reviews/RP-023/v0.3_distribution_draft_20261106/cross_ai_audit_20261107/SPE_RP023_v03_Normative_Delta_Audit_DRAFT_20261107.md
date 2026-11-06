# SPE RP-023 v0.3｜規範差分・証拠監査 DRAFT

Version: v0.1
Status: DRAFT / NON-CANONICAL / NOT OWNER ADJUDICATED
Created: 2026-11-07T03:32:08+09:00 (Asia/Tokyo)
Updated By: RP-023

権限：Ownerの2026-11-07付指示に基づく読取り・分析・新規DRAFT作成のみ。工程A〜Cを同一実行で実施。GitHub書込み、既存原本変更、DecisionLog更新、正式Acceptance、Finding Close、規範発効、Canonical化、Freeze、HOLD解除は未実施。RP-023／M19–25 HOLD継続。

固定参照：Repository `spe-flatvat/SPE`。R（回答）=`8f0964fae445a66f377a3e04d180a72d44a14f6f`、D（配布）=`f4939211f1ab5b5848d3aa5293078bb651e2028b`、B（v0.2比較）=`5f27d4e2fba90cda2cd69ee534e865174c31ba1f`、O（Step29H原回答）=`51680012e2f3e803b373b1c43b3644c93c74068f`。補助E（Evidence HEAD）=`52ac73915beb5a3664ad8535cb5d7a4b80c28f91`、N（旧規範照合基準）=`8e46e5b8af6f2c5936d3d166d1b8c69680713d72`。最新HEADによる代替なし。

証拠区分：RのChatGPT／Claude／Grokは保全されたレビュー報告書。Gemini G1〜G3はOwnerによる全文転載であり、Geminiサービス原本バイトとの同一性は未検証。索引・抽出版を代用していない。Dのv0.3は未承認規範候補、Bの規範文書は指定比較基準。SHA一致は承認・発言者真正性の証明ではない。

受領判定：READY（本指示の限定範囲）。主回答6件、Geminiレシート、配布13件、v0.2・規範比較資料を取得。6回答の既存期待SHAとDの13件期待値はWork自身の実バイト計算で一致。原裁定等の未検証は各論点に限定して維持する。過去AIの受領状態は遡及変更しない。

以下の略号は「ファイル名・パス・固定Commit」を指し、L番号は取得したUTF-8原文の1始まりの行番号。全入力インベントリ・取得経路・SHA・未検証範囲は同梱の Evidence Gap Register に記載。

|略号|固定Commit|Repository相対パス|
|---|---|---|
|V3|D|`reviews/RP-023/v0.3_distribution_draft_20261106/SPE_RP023_v03_Section8_Limited_Revision_DRAFT_20261106.md`|
|V2|B|`specifications/RP-023_v0.2_DRAFT_07C-02.md`|
|FD|D|`reviews/RP-023/v0.3_distribution_draft_20261106/SPE_RP023_v02_to_v03_Section8Fixed_Full_Unified_Diff_DRAFT_20261106.diff`|
|MA|D|`reviews/RP-023/v0.3_distribution_draft_20261106/SPE_RP023_M01_M07_Normative_Diff_Audit_DRAFT_20261106.md`|
|MP|D|`reviews/RP-023/v0.3_distribution_draft_20261106/SPE_RP023_M01_M07_Revised_Minimal_Diff_DRAFT_20261106.md`|
|SV|D|`reviews/RP-023/v0.3_distribution_draft_20261106/SPE_RP023_v03_Section8_Limited_Revision_Verification_DRAFT_20261106.md`|
|SN|D|`reviews/RP-023/v0.3_distribution_draft_20261106/SPE_RP023_v03_Owner_Snapshot_Receipt_DRAFT_20261106.md`|
|W|B|`docs/Workflow.md`|
|S|B|`docs/SPE_Documentation_Standard.md`|
|DL|B|`docs/DecisionLog.md`|
|BM|B|`reviews/RP-023/RP-023_4AI_Common_Review_Manifest_v0.3_DRAFT.md`|
|BC|B|`reviews/RP-023/RP-023_4AI_Common_Review_Contract_v0.3_DRAFT.md`|
|C|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP023_v03_ChatGPT_Independent_Review_20261106.md`|
|L|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/RP-023_v0.3_Claude_Receipt_and_Independent_Review_DRAFT_20261106.md`|
|G2|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP023_v03_Gemini_G02_Full_Chat_Transcription_20261106.md`|
|G3|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP023_v03_Gemini_G03_Full_Chat_Transcription_20261106.md`|
|K|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP-023_v03_Independent_Review_Report_Grok_20261106.md`|

## 1. 独立監査の結論

**工程B：PARTIAL。** 固定本文・全文Diff・§8限定Diffの再現、主要保護維持はPASS。旧§10の局所HOLD文の削除も確認したが、後続Owner方針原証拠の一部は未取得であり、その採用根拠まで無条件PASSにできない。現在の原本未照合を「裁定未決」と同義には扱わず、存在しない新規一律HOLDゲートを設けない。

Geminiの近接重複が現存するという前提は固定v0.3と不一致。ヘッダ未反映というG3の評価も実本文と異なる。これらは個別の事実対照であり、AI報告の正式棄却・Finding Closeではない。

## 2. 機械検証・網羅性

- V2：13,182 bytes／103行。V3：17,154 bytes／117行、SHA-256 `4f99df2849d0264938cb9b223e9c020a89e6e33eabd7e1f84a06259c0fa62c56`。
- FDの既存期待SHA一致。独立difflib再生成でFDと実バイト完全一致。供給Diffの5 hunkを、V2の各文脈行・削除行と厳密照合して逐次適用し、V3と完全一致。既存AIのPASSを転記したものではない。
- 行差分は14変更ブロック。以下で全14を分類。未変更規範の保持は§別・義務文別に確認し、単なる見出し一致に依存しない。
- 補助回収した先行17,123-byte統合DRAFTは既存期待SHA `3945f1e172804315c9e065409fa8ec0d87a06a641f6a77106350282e7af7d8be` と一致。2,931-byte §8限定Diffも期待SHA一致、独立再生成と完全一致。これらの原本はLibrary回収であり、D固定版の代替対象ではない。
- §§1,4,5の全文は不変。§11本文も不変（§12追加に伴う区切り改行のみ）。§§2/3/6/7/8/9/10は下表で追跡、§12は新設。

## 3. 全変更ブロック台帳

分類は変更の存在と意味を分ける。CLARIFIEDは無承認でも採用可という意味ではない。REVIEW／PARTIALは後続裁定原証拠を要する部分であり、既裁定を再審議しない。

|変更ID|V2原文位置|V3位置|M対応|存在分類|規範効果・独立評価|
|---|---|---|---|---|---|
|ND-01|L2直後|L3–7|M01|ADDED／EDITORIAL|英語Version/Status/Last Updated/Updated By追加。S:L179–189の既存必須5項目を実装。新規文書所有者権限なし|
|ND-02|L4|L8–9間|M01|DELETED／EDITORIAL|日本語の版行削除、英語Versionへ正規化。v0.2派生の表示は冒頭に不足するが参照Commit注記は残る|
|ND-03|L6–7|L10–11|M01/M06|REPLACED／CLARIFIED＋REVIEW|状態補足に置換、OD05後続方針・具体未確定・未発効を記載。Git未反映の対象は編集曖昧|
|ND-04|L10直後|L15|M07|ADDED|N/E参照役割、二次報告限定。新たな一致必須ゲートは導入せず。E完全SHA・4文書比較は今回別途確認|
|ND-05|L19|L24|M03|ADDED／CLARIFIED|ガバナンス裁定のチャット成立後もDecisionLog記録義務を免れない。W:L11の参照であり履行延期許可なし|
|ND-06|L23|L28|M02|ADDED／CLARIFIED|Snapshot非代替性をW§3に接続。B/C全受領へ新たなOwner承認を強制しない|
|ND-07|L31|L36|M06|REPLACED／REVIEW|A表のPDF任意欄を後続方針に更新。A必須列は同一。旧版にPDF一律必須義務は未成立であり、その義務を削除したとはいえない|
|ND-08|L70|L75|M06|REPLACED／REVIEW|§6のOD03未決から後続方針報告へ。原裁定未取得。内容上の原本・SHA義務は不変|
|ND-09|L76|L81|M04|REPLACED／CLARIFIED|個別名列挙を一般化。終結・成立済み判断を含み、取消し禁止と依存限定HOLDは保持。実案件状態認定はしない|
|ND-10|L80|L85|M06|REPLACED／CLARIFIED＋REVIEW|未決表記を後続案Aへ。正式レビュー後の個別Owner決定が必要と明示し、自動発効・遡及を否定。旧条件より自動的に緩くなったとはいえない|
|ND-11|L84後|L90–91|M05/RD-01|ADDED|旧§8共通段落は完全保持。「未実施／未確認／適用外を区別して記録」「必須非減免」「偽装禁止」を明文化。記録運用の具体化・手順義務増加であり、規範影響ゼロとはしない|
|ND-12|L92|L99|M06|REPLACED／CLARIFIED＋REVIEW|旧レビュー版・SHA・手段・開始・受入の個別判断文を、OD08承認報告と非認証注記へ置換。W優先、Review/consensus/Acceptance/発効の分離は保持|
|ND-13|L98|L105–108|M03/M06|DELETED＋ADDED／局所明示性低下|旧P1未決列挙＋「別途Owner判断までHOLDする」を削除。原証拠留保と各後続状態へ。具体的保護文がなくなった事実は確認。全体の権限制約まで廃止とは認定しない|
|ND-14|L103末尾|L114–117|M07|ADDED|§12に原diff非代替・旧状態の時点分離・原本遡及改変禁止。証拠取扱いの明文化。過渡的な説明を規範本文に置く編集リスク|

## 4. 不変規範と強弱

|検査対象|V2→V3原文位置|結果・理由|
|---|---|---|
|A/B/C必須要件|V2:L31–38,43,47,84 → V3:L36–42,48,52,89|PASS。Aの原本・サイズ・SHA照合、Bの一意識別、Cの出典・固定・限界を保持。A表任意欄のOD03状態更新は別論点|
|Review/waiver/consensus|V2:L23,57,92 → V3:L28,62,99|PASS。省略禁止・理由付きwaiver・Owner留保を保持。Snapshot追記が全B/Cゲートに拡張されない|
|技術PASSと権限|V2:L18,22,47,51,57 → V3:L23,27,52,56,62|PASS。未照合をPASS化しない。限定判断は既存規範内、下流権限は個別条件|
|DecisionLog記録|W:L11、V3:L24,105|PASS（義務の接続）。裁定成立と記録充足を分離し延期許可なし。実際のID対応はUNVERIFIED|
|非遡及・限定HOLD|V2:L25,76,80 → V3:L30,81,85|PASS。直接依存新規操作限定、過去見直しは別手続。個別名削除は保護対象の自動削除ではない|
|検証担当独立性|V2:L78,84 → V3:L83,89|PASS（不追加）。担当語2か所、元の文章は維持。発出者と別人MUSTは追加なし。定義欠落の解消とは別|
|既存Owner権限|V3:L40,56,62,83,85,113|PASS（維持）。新規の正式裁定・自動発効・HOLD解除権限を付与しない|
|MUST/SHOULD等|全14差分を日本語の「要する／記録する／しない」も含め確認|英語大文字の新規MUSTがなくても§8には運用指示が増加。W由来の既存義務参照と新しい具体的記録規則を区別する|

## 5. B-01：OD-03/05/08と旧HOLD保護

**PARTIAL。削除事実PASS、承認根拠の完全認証UNVERIFIED、全体弱化の断定は留保。**

V2:L98：「推奨案を採択済みとして扱わず、別途Owner判断までHOLDする。」はV3にない。これは旧未決3事項の局所保護の明示性の低下である。Claude追加01の削除指摘は原文で支持される。

ただし旧文は「未決」の扱いであり、あらゆる「原レシート未認証」に同一のHOLDを自動適用する規範とは書かれていない。未認証を未決・裁定不存在と同義にするClaudeの解釈まで無条件に採用しない。V3:L12,23,29,56,62,81,85,99,113の留保・既存Workflow優先・未発効・個別権限は残るため、正式レビューやOwner承認をバイパスできるとの断定は支持されない。

- OD03：V2のA表はPDFを任意欄に置き「必須化未決」。V3は後続の任意方針と記載。旧版の成立済みPDF必須義務を弱化したものではない。後続方針の原記録は未取得なので確定根拠はUNVERIFIED。
- OD05：Libraryから判断レシートを回収（EG-03参照）。「正式レビューとOwner承認が完了するまで発効しない」「別途Owner明示指定」「自動発効・遡及なし」の記録を確認。V3:L85と趣旨は整合。ただし当該レシート自身は旧OD05との厳密対応未照合と留保する。Owner原メッセージの独立認証・具体発効決定は未了。
- OD08：Bの共通Manifest/ContractはStep28案A承認済みと報告（BM:L53、BC:L14,24）。V3は報告と原承認未認証を区別する。既存承認の取り直しを求めない。

推奨は、後続方針の出典・証拠区分の参照を§3/§6にも付す最小の編集補強。未認証中の運用を一律HOLDとする新規義務を追加する場合は規範変更案としてOwner判断へ分離する。今回の読取り工程で新しい原証拠ゲートを設置しない。

## 6. B-02：§8の固定版対照

**PASS（現固定版の整序・再現性）。FAIL（重複が残るというGeminiの事実前提）。**

V3:L89は「共通項目は、」、空行後のL91は「なお、共通項目の記録に際しては、」。同じ「共通項目は、」の開始句は§8中1回。G2:L52／G3:L189の連続重複は存在しない。Geminiの別版受領やサービス内誤認を推定せず、指定SHAの本文との不一致として記録する。

SV:L17は既に同じ限定修正を報告する。今回はLibrary回収した先行版・限定Diffでも実バイト再生成一致を確認した。旧段落の全必須文言は保持されている。したがって同じRD-01編集を再実行する必要はない。

一方、L91の「等」「適用しない項目」の運用余地は別問題。Claude追加02とChatGPT NEW-01が関連する。L91の必須非減免但書でA/B/C要件・§4.1識別義務の弱化は防がれるが、§8の他の共通項目の適用外判断基準までは完備していない。ここはPARTIAL。理由の記録義務や「発生し得ない場合のみ」へ限定する案は新規義務・適用変更となり得る。

## 7. B-03：原16 Findingの残余

Matrixの16行を参照。Headerは実装済みでありGeminiの「候補のみ」は固定本文に合わない。H29-03は新しい運用具体例を追加していないため、候補の存在を要求充足へ転換しない。CLD03はOwner留保、CLD04は条文接続と原証拠・記録充足を分離する。CLD07の4小論点は分割Closeせず、今回確認したE完全SHA・N/E比較以外を残す。Grokの群評価は個別16件の肯定証拠ではない。

## 8. B-04：証拠の真正性と適用範囲

**PARTIAL。** 今回解消したのは、E完全SHAの所在、N/Eの4規範実バイト一致、OD05判断レシートの回収、§8先行版限定Diff同一性、配布13件の外部期待SHA所在である。これらの原本・取得経路はEvidence Gap Registerに記録する。未取得の07A/P0、OD03/06/08のOwner原発言、元07C-03.diff、DLの個別対応はUNVERIFIEDで維持する。不存在・裁定無効と断定しない。

## 9. B-05：限定受領例外の一般化防止

**PASS（確認可能な記述範囲）。** C:L9,14,42,80は対象AI・本レビュー・D固定Commit限定とし、一般的A区分必須要件の緩和先例ではないと明記する。V3:L26,52,56,66–70は代替移送と技術的PASS・下流権限を分離し、A原本照合義務は保持する。本工程の実バイト検証は、当時のGitHub原本／ローカル補完資料の同一性を遡及証明しない。例外の原Owner指示全文と実際の将来運用は未検証であり、全運用で一般化が起きないことを証明したものではない。

## 10. 終了・権限制約

全14差分を分類し、主保護と残余を切り分けた。後続裁定原証拠依存の採用可否は留保したまま、工程Cの選択肢へ接続する。必要な証拠不足を他の本文分析全体のSTOPへ拡張しない。本工程で正式Acceptance・Finding Close・規範修正・原本改変はしない。
