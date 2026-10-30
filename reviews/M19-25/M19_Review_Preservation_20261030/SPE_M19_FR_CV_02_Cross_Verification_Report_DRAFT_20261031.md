# SPE M19｜M19-FR-CV-02 正式独立レビュー横断検証報告 DRAFT

**Status:** DRAFT / NON-CANONICAL / ANALYSIS ONLY  
**作成日:** 2026-10-31（JST）  
**Repository:** spe-flatvat/SPE  
**工程:** M19-FR-CV-02（M19正式独立レビュー。先行FG-07横断検証とは別工程）  
**権限:** READ-ONLY / ANALYSIS / NEW DRAFT REPORT ONLY  
**原32 Finding:** OPEN 32 / Close 0  
**M20–25／RP-023:** HOLD維持  
**最終判断権限:** Owner

## 1. Executive Summary

承認された横断検証本文の作成を完了した。4回答を相互に確認し、新規に採番された **8 Finding（ChatGPT 3、Grok 1、Claude 4）** を原ID・原Severityのまま整理した。Geminiには今回独自に採番されたFinding一覧がないが、論点別の評価と留保がある。「新規問題なし」とは扱わない。

主要な未決事項は、①CC-04のDecision要否の参照範囲、②Decisionを要求しない非裁量型を仮定した場合のCC-12予約条件との接続、③2026候補の別途認可・予約証拠、④原32件の個別根拠・参照版・ヘッダ識別である。4AIの結論は一致しておらず、多数決で裁定しない。

本検証では、裁量型についてCC-03の承認要件が消えたこと、または2026候補が自動的に認可されたことは確認できない。一方、非裁量型の別契約がDecisionを要求しない場合に標準予約経路をどう適用するかは、CC-04だけでは確定しない。これは条件付きの適用範囲問題であり、実在する承認済み経路の障害やfail-openを実証したものではない。

原32件はすべてOPENである。特にCLD3-01はMajorのまま、処分案がいう「別紙注記」の裏付けが固定パケット内では確認できない。本文上の修復候補、証拠留保、正式Closeを区別する。

**提出状態：横断検証DRAFT作成 COMPLETE／Owner判断待ち。** Control Contract改訂、Findingの統合・Close、Review Acceptance、Canonical化、Freeze、HOLD解除は行っていない。次工程を自動開始せず、本報告を提出して停止する。

## 2. 入力・固定基準・検証方法

### 2.1 開始承認と資料の役割

開始根拠は添付 `SPE_M19_FR_CV_02_Start_Authorization_and_Work_Instruction_Receipt_20261031.md`。Owner指示の記録「M19-FR-CV-02開始を承認します。レシート発出ください。」および同レシート§3〜5の作業範囲に従った。これは添付レシートの記載を根拠とするもので、別の過去チャット原メッセージを独立取得したものではない。

| 役割 | 固定基準／確認状況 |
|---|---|
| レビュー対象の配布固定Commit | a00c96252ee1260a909be8775511c420685b51d8 |
| 4AI回答保全Commit | b0e8ce05f34b56e6e6e23a48dedda31afffe64fe |
| 対象Branch | review/m19-convergence-preservation-20261030（本工程で移動・更新しない） |
| 対象ディレクトリ | reviews/M19-25/M19_Review_Preservation_20261030/ |
| 対象候補SHA-256 | 4a1f70e0c517c0a3e5d0389bb5176db2336bcdd935f2d34f1abf7a5b5f538ed2 |
| 開始承認レシート | 6,798 bytes／97行／実測SHA-256 2ccff8aa24e5e0d3a2e6685eb494b58e04e1901f264e1c43ee31c284e16ebec0。独立した既存期待SHAとの照合は未実施。 |
| 取得経路 | CV-01でGitHub連携から固定CのBase64実バイトを取得した16ファイルを再利用。CV-02で全16ファイルのSHA-256・サイズ・Git blob SHA-1を再計算し、取得時記録との不変性を確認。 |
| DとCの境界 | CV-01でDのパケット等12ファイルとCの対応物についてblob・サイズ一致を確認済み。本工程はその取得記録を使用し、mainや現在のbranch状態を新規照会していない。 |
| 行番号 | 現候補538行基準。CSVはBOM付きUTF-8を読み、物理行2〜33をデータ32件として参照。 |

### 2.2 証拠状態の定義

- **VERIFIED（今回）**：取得済み実バイトの再計算一致、現資料内にある文言・ID・OPEN状態の存在確認。
- **CV-01確認済み・本工程再照会なし**：固定Commitとの取得対応、DとCの同一blob対応。
- **レビュー原記録の主張**：各AIの当時のSHA検証、全体整合性、旧Findingへの評価。原文として保持し、今回の独立実行結果へ読み替えない。
- **NOT VERIFIED**：歴史的Owner原裁定、E1、E-03／E-04、CLD2の資料同定、旧32件の原レビュー全文との完全照合、実際の2026候補の認可・生成、エンジン実行、29 InvariantsのV&V。

SHA-256は取得文書の同一性確認に使う。過去のOwner承認の成立を証明しない。4回答の独立した既存期待SHAは未取得のため、本工程で実測できても「当時の独立期待SHAと一致」とはしない。ChatGPT当時0/11、Grok当時NOT VERIFIED等の自己申告を、今回の再計算で遡及的に書き換えない。

### 2.3 固定16ファイル台帳

以下はCV-01取得済みファイルの本工程再計算値。パケット4＋参照7の計11件は、既存SHA256SUMSとの一致をCV-01で確認済み。回答4件とSHA256SUMS自身はこの11件の検証対象に含まれない。表の行数は改行で数えた物理行数。

| 資料（固定Cで取得） | bytes／行 | SHA-256 |
|---|---|---|
| ChatGPT_M19_Formal_Independent_Review_Response_20261031.md | 9424／169 | 0b7265948e9e16522dde6e82ac460859df8016e2d500eee948c933b020ba9386 |
| Gemini_M19_Formal_Independent_Review_Response_20261030.md | 7523／83 | 982d8419a04501f7ae0abed3a39ea3d1ea1eb9812227aabfdf99223daf9abc43 |
| Grok_M19_Formal_Independent_Review_Response_20261031.md | 9809／190 | d172935890035825aad97a401bd19e2409d9dbed4ff971a7b31eea154cb752b1 |
| M19_Claude_Formal_Independent_Review_DRAFT_20261031.md | 14625／135 | 11aa3b913eb9436c5704189dd0678f54ea4600b75a47b7d85974707c25dc0da0 |
| references/SPE_M19_Control_Contract_Convergence_Verification_Receipt_DRAFT_20261030.md | 2454／28 | b36d9652a12f8d5f5d02b96ce3a7cfec62a4a07c94763b36e9b5b6d9299ca230 |
| references/SPE_M19_Control_Contract_Convergence_vs_FG06_Fixed_20261030.patch | 2026／20 | 1b6e085facece3d332715f28c0c1f7cab2b62c73166a516148446f5300ebf6d2 |
| references/SPE_M19_Control_Contract_Convergence_vs_FG07-07_20261030.patch | 1674／11 | 9c7b30d99adf788a360fb4524b3aa095caa1df8007b69806960c56f5c6c9e669 |
| references/SPE_M19_Integrated_Verification_Report_DRAFT_20261030.md | 5873／64 | 5347665b13484efee5b6356a91ca56d211e88850b4069f7a487007237083add9 |
| M19_Review_Packet/Common_Review_Request.md | 2180／20 | b85826b3690202d61447fd4203824ee71b217cf495baa7271ff6b3c5a84f4217 |
| M19_Review_Packet/Evidence_Index.md | 2326／21 | 376bcdbc5a88f1d0dda521788f466be634e378593ba6e3944d3d7a289b05d943 |
| M19_Review_Packet/Manifest.md | 1995／30 | b494515522fae923e37127ddddd050c3134237c5348cee3cb9282445e72154f6 |
| M19_Review_Packet/Review_Checklist.md | 1048／18 | 34bc7b14728a30f3307d2c9efea592decb42bd10bcbff87d629cb9a94b9e32d1 |
| SHA256SUMS.txt | 1401／11 | 08dc945cb221c6bca6d7fa9d9c9e3dde74eeec2b9df90eb5bebd027fa677f708 |
| references/SPE_M19_32_Finding_Disposition_Proposal_DRAFT_20261030.csv | 11957／33 | 5e4dfcb3a72f08fca8564427ec68442957115bff93852aca23083f83eab3ac8f |
| references/SPE_M19_32_Finding_Disposition_Proposal_Report_DRAFT_20261030.md | 2942／37 | 015216b907721b6e6011f53689cd4178c8aec6a9f124d6f79a0805e80233193c |
| references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md | 39815／538 | 4a1f70e0c517c0a3e5d0389bb5176db2336bcdd935f2d34f1abf7a5b5f538ed2 |

共通パケットのManifest・依頼文・Evidence Index・Checklistはレビュー範囲の証拠、CSV・処分案報告・統合検証報告・検証レシート・2差分patchは提案と検証経緯の証拠として使用した。patchは参照のみで、既存ファイルに適用していない。統合報告のTermux 4/4や各AIの検証自己申告は今回実行したテストではない。

## 3. 4AI原Verdict・新規Finding・評価前提

| AI | 原Verdict（表現を保持） | 新規採番 | 前提・限界／出典 |
|---|---|---|---|
| Gemini | REVISE（条件付き受入・残余事項明記の上での文言精査） | 独自採番の一覧なし | 項目別評価あり。32件は区分集計中心で、全件の個別支持とはしない。[GEM L21–40](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/Gemini_M19_Formal_Independent_Review_Response_20261030.md#L21-L40) |
| ChatGPT | REVISE（新規Minor 3件、既存Finding 32件の原Severity維持） | M19-GPT-NEW-01〜03 | 当時SHA 0/11留保。32件個別表は処分案要約に依存。[GPT L158–165](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/ChatGPT_M19_Formal_Independent_Review_Response_20261031.md#L158-L165) |
| Grok | ACCEPT（条件付き・DRAFT） | GRK-M19-01 | 無条件ACCEPTではない。スポット＋差分焦点、当時SHA未検証。[GRK L18](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/Grok_M19_Formal_Independent_Review_Response_20261031.md#L18)／[GRK L157–178](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/Grok_M19_Formal_Independent_Review_Response_20261031.md#L157-L178) |
| Claude | REVISE(軽微修正)。 | CLD4-01〜04 | 自分の前回CLD3系については処分案根拠の有無を中心に評価。原Major未解消の指摘あり。[CLD L10–25](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L10-L25) |

| 原Finding ID | 原Severity | 対象 | 原主張の要旨（今回の裁定ではない） | 出典 |
|---|---|---|---|---|
| M19-GPT-NEW-01 | Minor（意味論上の曖昧さ） | CC-04 L152 | 他の適用要件／Decision不要の根拠契約を監査で特定。直ちに衝突とはしない。 | [GPT L31–47](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/ChatGPT_M19_Formal_Independent_Review_Response_20261031.md#L31-L47) |
| M19-GPT-NEW-02 | Minor（条件付きの運用リスク） | CC-04／CC-12 | 2026候補の予約証拠時点。別途認可の有無をOwner判断事項として残す。 | [GPT L49–63](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/ChatGPT_M19_Formal_Independent_Review_Response_20261031.md#L49-L63) |
| M19-GPT-NEW-03 | Minor（追跡可能性） | 処分案CSV | FG06-GPT-RR-04、CLD3-04／05の個別根拠不足。 | [GPT L65–81](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/ChatGPT_M19_Formal_Independent_Review_Response_20261031.md#L65-L81) |
| GRK-M19-01 | Minor（解釈上のリスク） | CC-04 L152 | 契約外にも広がるDecision参照範囲。削除・限定は意味論に触れ、Owner判断要。 | [GRK L119–127](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/Grok_M19_Formal_Independent_Review_Response_20261031.md#L119-L127) |
| CLD4-01 | Minor／解釈上のリスク | CC-04 L152 | 未承認の本契約を参照しうる循環、範囲、構文。Decisionなし2026候補をOwnerが許容した場合Majorとの再評価条件を原文のまま留保。 | [CLD L29–38](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L29-L38) |
| CLD4-02 | Minor | CC-12 L403／CC-05 L211 | Decision不要の別途承認非裁量型を仮定したときの予約証拠要件との接続。 | [CLD L40–44](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L40-L44) |
| CLD4-03 | Minor／台帳 | 処分案CSV | 行番号2行ずれ、一部定型根拠、Severity欄書式。 | [CLD L46–51](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L46-L51) |
| CLD4-04 | Editorial | 現候補ヘッダ | 自己識別、統合根拠、古い自己言及。CLD3-04に関連するが別ID保持。 | [CLD L53–57](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L53-L57) |

8件は原報告の分類ではMinor系7件、Editorial 1件。CLD4-01のMajor再評価は条件付き提案であり、今回重大度を変更しない。Geminiの未採番評価には新しいFinding IDを発行していない。原32件との合算・新台帳への登録・正式Dispositionは未実施。

## 4. 原IDを保持した横断対応

以下のCV-A〜CV-Fは報告内の比較行ラベルであり、新Finding IDや正式統合IDではない。

| 比較行 | 対応する原ID／評価 | 関係候補 | 一致・相違と扱い |
|---|---|---|---|
| CV-A | M19-GPT-NEW-01／GRK-M19-01／CLD4-01 | 同一の文言を対象とする論点群。ただし要求範囲差あり | GPTは適用性根拠の監査、Grokは参照範囲限定、Claudeは循環・構文も問題化。免除が実証されたとの一致ではない。統合しない。 |
| CV-B | M19-GPT-NEW-02／CLD4-02 | 関連・補完 | GPTは2026予約証拠の時点、ClaudeはDecision不要の非裁量型全般とCC-12の接続。年に依存する問題と経路分類の問題を分ける。 |
| CV-C | M19-GPT-NEW-03／CLD4-03 | 3件の定型根拠について一致、全体は部分重複 | Claudeには行番号・Severity欄の追加論点がある。GPTの根拠不足に集約して失わない。 |
| CV-D | CLD4-04／CLD3-04・05／CLD3-01 | 版識別・権限追跡の関連 | ヘッダ編集問題と、MajorのR系列裁定追跡・別紙根拠問題は同一とは認定しない。 |
| CV-E | Gemini Q1・Q2／Claude CLD4-01・02／Grok Q5／ChatGPT NEW-01 | 結論・評価範囲の相違 | Geminiは追加／免除なし・内部整合と評価。Claudeは条件付き接続不整合、GPT／Grokは確定衝突を認定しない。多数決で整合とはしない。 |
| CV-F | 原32のCLD3-01：GPT「支持」／Claude「I」 | 支持対象の違いを含む相違 | 証拠留保の分類への支持と、別紙がありMajorが解消されたとの認定は別。原Major・OPENを維持。 |

[GEM L35](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/Gemini_M19_Formal_Independent_Review_Response_20261030.md#L35)（原文）

> - **結論:** 意図しないDecision義務の追加や免除は生じておらず、CC-03の非裁量型別契約要件と矛盾しません。

[CLD L43](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L43)（原文）

> - 問題:CC-04 の改訂は「Decision は必要な場合のみ」と読める方向だが、CC-12 は予約を作るすべての候補に Decision 証拠を要求している。CC-03 は非裁量型の切替を「別途承認された契約」に委ねており、その契約が Decision を持たなければ、CC-04 と CC-12 が衝突する。CC-04 の修文は、意図(CC-04 レシートの「既存の承認済み契約その他の適用要件へ委ねる趣旨」)を、CC-12 の側では達成していない。

[GPT L45](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/ChatGPT_M19_Formal_Independent_Review_Response_20261031.md#L45)（原文）

> したがって、これを直ちに規範衝突とは認定しませんが、**Decision不要と判定した根拠契約を監査上特定できること**を明確にする余地があります。

これらの相違は、同じ現候補の文言を見ても「規範束として適用するか」「Decision不要の非裁量型の承認契約が実在するか」「CC-12標準予約手順まで適用するか」という前提が異なるために生じうる。前提と反例を明示してOwnerに渡し、採否を代行しない。

## 5. Control Contractの規範整合性検証

### 5.1 CC-04の参照範囲と裁量型Decision要件

[CC L152](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L152)（原文）

> The 2026 reference branch in this clause does not establish a transition-candidate creation, approval, scheduling, or effectuation pathway. A candidate targeting 2026 may be used only if its creation and use are separately authorized under applicable approved contracts and, where required by those contracts or other applicable approved requirements, attributable Decisions, with all required reservation, numerical-contract, and Gate validations. No such separate authorization is established by this clause.

[CC L89–96](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L89-L96)（原文）

> For a discretionary policy switch, a transition candidate requires:
> 
> - `Trigger=met`;
> - `Decision=approved`;
> - an expressly authorized destination and effective year;
> - no unresolved competing transition.
> 
> This combination does not itself authorize `Transition=effective`. CC-05 and CC-12 remain applicable.

[CC L119](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L119)（原文）

> The controller MUST NOT invent priority among competing switches. Non-discretionary switch types require separately approved contracts.

[CC L237](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L237)（原文）

> Gate applicability, results, reasons, and dependency scope MUST be independently auditable. Ambiguous dependent authorization MUST fail closed without automatically stopping unrelated operations.

**今回の静的評価：裁量型のDecision義務の消失は確認できない。** CC-04 L152は別途認可の必要条件を述べ、CC-03の裁量型要件を明文で解除していない。L89〜96を同時に読む限り、裁量型は`met/approved`等を満たし、さらにCC-05／12に従う。DRAFTが未承認であること自体も、実運用を許す権限にはならない。

したがって、CLD4-01の「承認前にはapproved requirementにCC-03が含まれない読み」はレビュー上の解釈リスクとして保持するが、これだけで裁量型fail-openが成立したとは判定しない。規範束としての将来適用と、承認前DRAFTの検証用シナリオを分ける必要がある。

一方、`other applicable approved requirements`の特定方法・承認主体・版はL152だけでは限定されていない。CC-09 L315、L327〜335は不変参照と証拠分類を要求するため、Decision適用性を記録する根拠にはなるが、どの外部規範が適用されるかを代わりに裁定するものではない。

**修正時の注意：** 他要件句の単純削除は、別の適用承認要件を落とす可能性がある。逆に無条件Decisionを戻すだけでは、別途承認非裁量型の意図を変えうる。どちらも無条件にEditorial／意味論不変と断定できない。適用する権限・契約範囲を先に確認する。

### 5.2 非裁量型、CC-05 Gate B、CC-12予約証拠

[CC L211](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L211)（原文）

> **Gate B — authorization where applicable:** Validate the dependent Trigger, mandatory observation contract, attributable Decision authority and evidence, live reservation, destination, effective year, and competing-transition conflicts.

[CC L225](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L225)（原文）

> All applicable gates MUST pass before the dependent calculation or transition becomes effective.

[CC L403](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L403)（原文）

> Before scheduling, the controller MUST validate the approved destination, effective year, attributable Trigger and Decision evidence, and competing reservations.

[CC L419–425](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L419-L425)（原文）

> Replacement reservation: A replacement reservation MUST receive a new immutable reservation ID and fresh reservation-specific attributable evidence.
> 
> Its authorization basis MAY refer to an existing approved Decision only within that Decision's expressly approved scope and validity.
> 
> The controller MUST revalidate the authorization basis, target, effective year, and competing-transition constraints when creating the replacement reservation and at the applicable Gate B checkpoint.
> 
> Reservation expiry MUST NOT by itself imply expiry of the underlying Decision.

**条件付きの接続問題を確認した。** 仮に①別途承認された非裁量型契約が存在し、②Decisionを要求せず、③本候補の通常予約手順を使用し、④その契約がCC-12の適用除外・優先順位を明示しない場合、L152ではDecisionを条件付きとしていても、L403の無条件なTrigger／Decision証拠検証が残る。Decision証拠なしでは通常予約条件を満たせない可能性がある。

この反例は「許可されてはいけない切替が通る」という実証ではなく、「許可する意図の経路でも標準予約条件に接続できない」条件付き充足不能・適用範囲未確定である。実在する承認済み非裁量型契約、そのDecision要否、通常予約手順への適用を取得していないため、現在の実運用障害を確定しない。

CC-05の`where applicable`はGate Bの適用性を示すが、CC-12の予約条件まで自動的に免除するとは読めない。CC-03 L109の承認済み例外は当該裁量型状態組合せの文脈にあり、L403全般の暗黙の上書き根拠としない。

Ownerには、(a)対象候補にDecisionが常に必要なのか、(b)Decision不要の経路を想定するならどの別契約・予約範囲・優先順位が適用されるのか、を確認する必要がある。CLD4-02の条件句追加はその選択後の改訂案であり、今回採用していない。単にL403を緩めて裁量型の必須Decisionまで弱化させてはならない。

### 5.3 2026候補の生成・予約証拠と2027以降の継承

[CC L138–150](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L138-L150)（原文）

> **Initialization:** Year 2026 MUST be validated under an Owner-approved Baseline Initial-State Contract, not a fictitious 2025 final-state record.
> 
> The contract MUST identify the baseline year, required variables, values, units, provenance, distinctions between document anchors and inferred values, and Owner approval ID.
> 
> Missing or contradictory required fields fail closed within dependency scope. Scenarios sharing a baseline MUST share identical approved 2026 initial-prefix data and immutable references.
> 
> This clause approves no numerical initial values.
> 
> **Continuation:** From 2027 onward, Gate A MUST validate the actual finalized preceding-year state and required history. A year MUST NOT silently inherit an unrelated policy baseline.
> 
> **Year-entry sequence:** For each year `t` in 2026–2055, the controller MUST evaluate Gate A, then Gate C, then Gate B where applicable.
> 
> Where a valid transition candidate targets `t`, Gate C MUST validate the candidate destination policy's target-year numerical contract against the Owner-approved 2026 Baseline Initial-State Contract when `t=2026`, or against the actual authorized finalized preceding-year state when `t>=2027`, together with applicable segment references. This 2026 boundary rule does not approve initial numerical values or a policy transition.

[CC L172](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L172)（原文）

> **Post-year decision boundary:** Following an authorized finalized annual result, the controller MUST validate required year-end observation contracts separately from Trigger truth, evaluate applicable Triggers, request and record required attributable Decisions, and append authorized reservation or resolution events.

[CC L249](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L249)（原文）

> Upon switching, a new anchor schedule MUST be expressly authorized and rebased on the Owner-approved 2026 Baseline Initial-State Contract when the effective year is 2026, or on the actual authorized finalized preceding-year result when the effective year is 2027 or later.

**参照境界は現文言上整合する。** Gate A／CおよびCC-06アンカーは、2026には承認済み初期状態契約、2027以降には同一実行・経路の実際の前年確定状態を要求する。架空の2025最終状態を要求しない。この参照先の整合は、2026候補の生成・承認・予約・有効化が認可されたことを意味しない。

CC-04 L172は年次確定後の通常の観測・Trigger・予約処理を述べる。2026を最初の計算年とする場合、これだけでは2026年有効予約の事前生成証拠を与えない。他方、L152は別途認可による候補を一律禁止してもいない。承認済み初期契約・候補生成経路・利用権限・予約時点の実証はNOT VERIFIEDのままとする。

従ってM19-GPT-NEW-02は、アンカー修復だけでは消えない関連論点である。2026候補の存在、作成日、承認日、入力値を本報告で補完しない。別契約が見つからないことと、存在しないことを区別する。

### 5.4 Gate状態・非先取り・依存範囲停止・比較・年度末

[CC L215–221](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L215-L221)（原文）

> Where Gate A and Gate C pass, the formal Gate B checkpoint is reached, and Gate B is established as nonapplicable, the controller MUST record `NOT_APPLICABLE` with an attributable reason.
> 
> It MUST NOT record an artificial PASS or imply political approval.
> 
> Where the formal checkpoint was not reached, the evaluation status MUST remain `NOT_EVALUATED`. Nonapplicability MUST NOT be inferred solely from the absence of a result.
> 
> Where Gate B applies and is formally evaluated, the result MUST be PASS or FAIL with attributable evidence and dependency scope.

[CC L288](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L288)（原文）

> The comparison operation MUST validate the approved comparison contract's evaluation period, metric definitions, units, baseline and initial-state compatibility, and evaluation methodology, plus all expressly required contract conditions.

[CC L260](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L260)（原文）

> Stop scope MUST follow actual dependency boundaries. Unaffected operations MUST remain executable.

[CC L497](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L497)（原文）

> These are future V&V obligations, not executed or certified tests.

| 条項 | 静的確認した保護要件（現候補行） | 結論・制限 |
|---|---|---|
| CC-01 | L55〜61：明示政策選択、捏造禁止、M10／14／17計算・M18評価意味論変更禁止 | L59禁止は無条件。L61のmetadata別承認を意味論例外へ拡張しない。実装一致は未検証。 |
| CC-02 | L65〜86：6ドメイン、監査属性とenumの分離、予約履歴再構成 | 新しいDecision enumを作らない。スキーマ実装未検証。 |
| CC-03 | L89〜133：裁量型必須組合せ、多年度pending、履歴と現行適用性、別途承認非裁量型 | CC-04条件句との読みは§5.1。非裁量型の具体的契約未取得。 |
| CC-04 | L138〜202：2026／2027+、A→C→B、正常年MUST、試行／確定／年度末の区別 | 同一contextで年次確定最大1・成功年度末最大1。再試行や異常年度末に別承認要件。候補権限は未立証。 |
| CC-05 | L205〜237：Gate A/C/B、適用性、NOT_EVALUATED／NOT_APPLICABLE、欠損時fail-closed | CC-12とのDecision適用範囲は未決。Gate未到達と非適用を混同しない。 |
| CC-06 | L241〜253：非先取り、共通prefix、承認segment、2026アンカー分岐 | 現L249で参照矛盾を確認できない。政策・数値アンカーそのものの承認ではない。 |
| CC-07 | L256〜274：依存範囲別停止、無断再開・欠損代入禁止、比較HOLD分離 | 無関係な計算の継続を保護。HOLDは比較状態の書換えではない。 |
| CC-08 | L278〜306：指定検証操作、全要求条件MUST、版整合、再検証 | L288包括条件は存在。実際の比較契約・結果・主体識別の完全実装は未検証。 |
| CC-09 | L309〜343：3監査分類、immutable、append-only、Owner原裁定照合 | 根拠を記録する規範と、既に原裁定を回収したという主張を区別。 |
| CC-10 | L346〜376：R4 Chapter4／5優先、10参照、shock単独認可禁止 | 契約内の保護を確認。政策原文・Owner原裁定との独立再監査はしていない。 |
| CC-11 | L380〜398：Trigger論理と必須観測を分離、欠陥contextの新Decision要求・予約禁止 | 観測不備をDecision捏造で迂回できない。観測・数値実行は未実施。 |
| CC-12 | L401〜429：予約ID、明示解決、新予約固有証拠、Decision寿命分離 | 失効予約の復活禁止。Decision証拠適用範囲は§5.2の条件付き留保。 |
| CC-13 | L433〜449：適格性判断・比較結果、未検証公開禁止、監査MUST／Action MAY | 指定operationの名称差CLD2系は台帳外・原文未取得の別問題。 |
| Invariants／Freeze | L467〜495：29項目／L499〜527：権限・証拠・Freeze境界 | 項目存在の静的確認のみ。全29件の実行PASSではない。 |

これらは指定焦点に対する現候補の静的照合である。全ての実行状態や外部承認契約を網羅する形式証明ではなく、「他に矛盾なし」「保護要件の実装検証済み」とは結論しない。

## 6. 原32 Finding処分案との対応

### 6.1 管理状態と評価の読み方

CSVを直接集計し、32行・ID重複なし・OPEN 32／Close 0を確認した。区分は文言対応確認候補11、既存条項対応・条件付き候補10、証拠留保・非規範注記候補11。これは処分案の分類件数であり、修復済み・Close済みの件数ではない。

下表はCSV順を保持する。SeverityはCSVの原欄を文字列として保持し、Markdown表内の区切り記号だけエスケープした。旧32件各原報告全文がパケットにないため、CSV欄と歴史的原Severityの完全一致はNOT VERIFIED。特にGEMINI-01は原表1行全体を含む異形欄であり、今回勝手にMinorへ置換しない。

Claude凡例：S＝引用本文で支持、S*＝支持・留保あり、I＝根拠不十分／本文未確認、E＝証拠留保分類が適切。SやEはCloseを意味しない。ChatGPTの「支持」も分類支持と修復認定を区別する。Geminiは全32件について集計評価のみで、個別IDごとの賛否は未提示。Grokは具体的ID言及と「等」を含む群評価を区別する。

| 原ID（CSV物理行） | CSVの原Severity欄 | 処分案区分 | ChatGPT個別評価 | Claude個別評価 | Grok記載範囲 |
|---|---|---|---|---|---|
| FG06-GPT-RR-01（L2） | Major | 文言 | 条件付き支持 | S* | L97個別：Major OPEN／条件付き |
| FG06-GPT-RR-02（L3） | Minor | 既存・条件付 | 支持 | S* | L104群内明記 |
| FG06-GPT-RR-03（L4） | Minor | 既存・条件付 | 支持 | S | L104群内明記 |
| FG06-GPT-RR-04（L5） | Editorial | 証拠留保 | **根拠補強要** | E | 個別ID言及は本節で未確認／群総論のみ |
| CLD3-01（L6） | Major／権限・トレーサビリティ（制御意味論には影響しない） | 証拠留保 | 支持 | I | L109証拠留保群内明記 |
| CLD3-02（L7） | Minor（CLD3-03でOwnerが2026年切替候補を許容すると決めた場合は Major に再評価） | 文言 | 条件付き支持 | S | L98個別：条件付き重大度OPEN |
| CLD3-03（L8） | Minor／解釈上のリスク | 既存・条件付 | 条件付き支持 | S* | L104群内明記 |
| CLD3-04（L9） | Editorial（見出し原文） | 証拠留保 | **根拠補強要** | I | 個別ID言及は本節で未確認／群総論のみ |
| CLD3-05（L10） | Editorial（見出し原文） | 証拠留保 | **根拠補強要** | I | 個別ID言及は本節で未確認／群総論のみ |
| GEMINI-FG06-01（L11） | Editorial | 既存・条件付 | 支持 | S* | L104群内明記 |
| GRK-LIM-01（L12） | Minor | 文言 | 条件付き支持 | S | L99個別言及 |
| GRK-LIM-02（L13） | Editorial（受領記録） | 証拠留保 | 支持 | E | L109証拠留保群内明記 |
| GPT6-FG06-01（L14） | 重大度：Major｜解釈上のリスク | 文言 | 支持 | S* | L100群内明記 |
| GPT6-FG06-02（L15） | 重大度：Major｜証拠不足 | 証拠留保 | 支持 | E | L109証拠留保群内明記 |
| GPT6-FG06-03（L16） | 重大度：Major｜解釈上のリスク・証拠不足 | 文言 | 支持 | S* | L100群内明記 |
| GPT6-FG06-04（L17） | 重大度：Minor｜解釈上のリスク | 既存・条件付 | 条件付き支持 | S* | L104範囲表記内 |
| GPT6-FG06-05（L18） | 重大度：Minor｜解釈上のリスク・新規Finding | 既存・条件付 | 支持 | S* | L104範囲表記内 |
| GPT6-FG06-06（L19） | 重大度：Minor｜解釈上のリスク・新規Finding | 既存・条件付 | 条件付き支持 | S* | L104範囲表記内 |
| GPT6-FG06-07（L20） | 重大度：Editorial｜証拠・表示上のリスク | 証拠留保 | 支持 | E | L109証拠留保群内明記 |
| CLD-01（L21） | **重大度：Major** | 文言 | 支持 | S* | L100群内明記 |
| CLD-02（L22） | **重大度：Major（FG05-N02と同一論点、独立に到達）** | 文言 | 支持 | S | L100群内明記 |
| CLD-03（L23） | **重大度：Major（FG-05はMinor／条件付きMajorとしたが、本レビューは独立にMajorと評価する）** | 文言 | 支持 | S* | L100群内明記 |
| CLD-04（L24） | **重大度：Minor** | 既存・条件付 | 条件付き支持 | S* | L104群内明記 |
| CLD-05（L25） | **重大度：Minor／Editorial** | 既存・条件付 | 支持 | S* | L104群内明記 |
| CLD-06（L26） | **重大度：Editorial** | 証拠留保 | 支持 | E | L109証拠留保群内明記 |
| GEMINI-01（L27） | \| GEMINI-01 \| Minor \| CC-03 (L108-130) \| マルチイヤーpending Decisionの継続条件において、Triggerが not_met や unknown に変化した際の不整合防止策が明記されているが、当該プロセスの失効条件の監査証跡要件をより明示することが望ましい。 \| 推奨修正（提案のみ）。実効性を高めるため、失効時のログ記録義務を追記する検討（本文変更はOwner承認後）。 \| 新規Finding \| | 既存・条件付 | 支持 | S* | L104群内明記 |
| GRK-01（L28） | - **重大度:** Major（規範追加の承認根拠未検証） | 証拠留保 | 支持 | E | L109証拠留保群内明記 |
| GRK-02（L29） | - **重大度:** Major（条件付き） | 文言 | 支持 | S | L100群内明記 |
| GRK-03（L30） | - **重大度:** Minor | 文言 | 支持 | S | L100群内明記 |
| GRK-04（L31） | - **重大度:** Minor | 文言 | 条件付き支持 | S* | L100群内明記 |
| GRK-05（L32） | - **重大度:** Editorial | 証拠留保 | 支持 | E | L109証拠留保群内明記 |
| GRK-06（L33） | - **重大度:** Editorial | 証拠留保 | 支持 | E | L109証拠留保群内明記 |

対応表の出典：[CSV L1–33](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_32_Finding_Disposition_Proposal_DRAFT_20261030.csv#L1-L33)／[GPT L107–144](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/ChatGPT_M19_Formal_Independent_Review_Response_20261031.md#L107-L144)／[CLD L77–118](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L77-L118)／[GRK L93–110](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/Grok_M19_Formal_Independent_Review_Response_20261031.md#L93-L110)／[GEM L60–67](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/Gemini_M19_Formal_Independent_Review_Response_20261030.md#L60-L67)。

この表により原32IDの全件を追跡できるが、旧原レビュー32件の原文を再取得・再審査したことにはならない。CV-02の新規8ID、Rev.2四AI18件、6D35の5件、CLD2台帳外は別管理である。

### 6.2 未解消Majorと分類支持の限界

[CLD L24](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L24)（原文）

> - 前回の CLD3-01(Major)は、候補本文のヘッダが無変更のため、本文上は未解消のまま。処分案が頼る「別紙注記」はパケット内に存在しない。

[CSV L6](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_32_Finding_Disposition_Proposal_DRAFT_20261030.csv#L6)（原文）

> CLD3-01,新12,Major／権限・トレーサビリティ（制御意味論には影響しない）,証拠留保・非規範注記候補,R系列の同名を時点・出典で区別する別紙注記。歴史的原裁定はNOT VERIFIED。,証拠境界・出典・版系譜を維持し、規範改訂と分離,OPEN / 0 Close,YES (M19収束時に一括確認)

[CC L14](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L14)（原文）

> - Historical authority references (NOT independently verified): D25-01–12, O-01–05, GATE-01, COMP-01, R-01–07, 6D27-01–02, and 6D38-01. Current drafting authority: FG-06 R-01–R-07 Owner decisions of 2026-10-28, within their expressly limited scope.

**CLD3-01の扱い：** CSVの「別紙注記」は、その内容・版・固定パスを独立にたどれる資料として今回の16ファイルに確認できない。候補L14には歴史的R系列と現FG-06系列を分ける記載があるが、それだけで処分案の別紙やOwner原裁定との対応を代用できない。「資料が世界のどこにも存在しない」とは断定しない。

Claudeはこの点をI／Major未解消と評価し、ChatGPTは証拠留保分類を支持する。両者は必ずしも同じ命題への賛否ではない。**証拠留保区分に置くことはMajor解消ではない。** 原Severityを保持し、権限・追跡の充足と最終DispositionをOwner判断待ちにする。

Majorを含む他の原IDもOPENである。CC-01 L59、CC-03 L105、CC-08 L288に対応文言がある項目については「文言が存在する」と言えるが、原指摘全条件・歴史的承認根拠・台帳外残余の解消まで証明できない。GPT6-FG06-02、GRK-01等の歴史的追加規範承認はNOT VERIFIEDを維持する。CLD3-02やGRK-02の条件付き重大度も自動変更しない。

### 6.3 根拠欄・参照行・ヘッダの独立確認

FG06-GPT-RR-04、CLD3-04、CLD3-05のSpecific basis欄が、3件とも`改訂文案／既存条項／証拠整理を照合`であることを直接確認した。この文字列は各問題の出典、対応内容、未対応部分を独立に特定できない。個別根拠を追記する場合も、原文未取得部分はNOT VERIFIEDとし、定型文を具体的な修復済み主張へ置き換えない。

CSVの参照先は、固定候補の現在の行番号と一致しない箇所がある。現パケットの差分patchにL152の段落＋空行挿入があり、挿入後の参照は次のとおり照合できる。旧版全文を別途取得して版間行マッピングを全面証明したものではない。

| CSV等の旧参照 | 現候補の該当行 | 現行原文（抜粋ではなく当該行全文） |
|---|---|---|
| L217 | [CC L219](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L219) | Where the formal checkpoint was not reached, the evaluation status MUST remain `NOT_EVALUATED`. Nonapplicability MUST NOT be inferred solely from the absence of a result. |
| L284 | [CC L286](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L286) | The approved comparison contract MUST identify an immutable contract ID and version, evaluation period, metrics, units, baseline and initial-state compatibility, methodology, and required dependencies. |
| L286 | [CC L288](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L288) | The comparison operation MUST validate the approved comparison contract's evaluation period, metric definitions, units, baseline and initial-state compatibility, and evaluation methodology, plus all expressly required contract conditions. |
| L290 | [CC L292](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L292) | Before formal finalization or publication, the comparison operation MUST verify that the individual eligibility and mutual comparability determinations apply to the exact approved contract and dependency versions. |
| L292 | [CC L294](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L294) | Changed dependencies MUST undergo explicit impact analysis. Affected determinations MUST be revalidated. |
| L309 | [CC L311](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L311) | 2. **Transition Decision Record:** Execution/path/record ID, year, Trigger observations and evaluation-contract version, mandatory observation-contract validity, attributable Decision authority and evidence, historical Decision identity and current applicability, destination/effective year, immutable reservation ID, creation/checkpoint validation evidence, linked lifecycle-resolution events, and applicable R4 source section or exception. |
| L413 | [CC L415](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L415) | A target-year Gate failure MUST be recorded but MUST NOT itself constitute formal year-end or automatically invalidate the underlying Decision. |
| L415 | [CC L417](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L417) | A reservation that does not become effective MUST be explicitly resolved under the applicable authorized year-end process and MUST NOT silently persist as live in a later year. |
| L423 | [CC L425](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L425) | Reservation expiry MUST NOT by itself imply expiry of the underlying Decision. |
| L439 | [CC L441](https://github.com/spe-flatvat/SPE/blob/a00c96252ee1260a909be8775511c420685b51d8/reviews/M19-25/M19_Review_Preservation_20261030/references/SPE_M19_Control_Contract_Convergence_Candidate_DRAFT_20261030.md#L441) | Formal comparison finalization and publication MUST NOT proceed without successful required validation. |

L59・L105・L150は挿入前で同じ行番号。範囲参照は始点・終点を別々に確認し、全てに機械的な「+2」を適用しない。旧版基準を併記する方法でも追跡可能性は改善できる。行番号ずれそのものは制御規範の変更ではない。

GPT6-FG06-04、CLD-04等の「CC-06アンカー残余」という旧要約については、現L249に既に2026／2027+の分岐がある。現在も未確定な生成・利用権限と、修復済み候補文言を分けて記す必要がある。旧原Finding全文なしに原件全体の解消を認定しない。

ヘッダは現候補L1〜15を直接確認した。Document ID、過去のIntegration basis、`has not been independently re-reviewed`等を含む。現4回答が存在するという外部の状態と、固定時点の自己記述を分離する。既存候補を無断修正せず、将来の改訂版に文書ID・不変digest・統合根拠・状態履歴を付す候補として扱う。独立レビューの受領だけでNOT REVIEW-ACCEPTEDを正式受理へ変更できない。

## 7. 台帳外・歴史的証拠の別管理

[CLD L118](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L118)（原文）

> 加えて、**32件の台帳に含まれない既知の指摘**がある:私の CLD2-01、02、03、05(3DEC 再レビュー由来。上記の継続分)。パケットが使う `CLD2` という語は、定義がなく、これらを指すのか別の歴史的資料を指すのか判別できない(NOT VERIFIED の注記と併せて、ID 衝突のおそれ)。台帳での追跡対象にするかは Owner 判断。

| 参照された台帳外ID | 今回回答がいう関連先 | 確認範囲／扱い |
|---|---|---|
| CLD2-01 | CLD-01／CC-03のno switch等の残余 | Claude現回答L69、L102の二次的言及。旧原文全文未取得。32へ追加せず、処分未定。 |
| CLD2-02 | GPT6-FG06-01／CLD-03、比較validation主体の区別 | Claude現回答L69、L95、L104の関連言及。現CC-08全条件MUSTとは別問題。原文未確認。 |
| CLD2-03 | GPT6-FG06-03、CC-01のonlyに関する残余 | Claude現回答L69、L97の言及。既存計算意味論保護L59の有無と別問題。原文未確認。 |
| CLD2-05 | Invariantsが復元義務を直接カバーしないとの継続指摘 | 現回答L69／L118で言及を確認。旧原文の正確な要求全文・範囲は未取得。 |
| 資料名としてのCLD2 | パケット内NOT VERIFIED表示の指示対象 | 上記ID系列と同じ資料を意味するかNOT VERIFIED。名称を対応済みとしない。 |

上記4件について、Claude現回答L69の原Severity表現は「いずれも Minor／Editorial」。個別にどちらかを推定せず、この表現を保持する。CLD2-01には`no switch;`の欠落、`Persistent`の基準と理由コード、CLD2-02には比較operationの名称差、CLD2-03には`select only`の`only`欠落という具体的な二次的言及がある。[CLD L69](https://github.com/spe-flatvat/SPE/blob/b0e8ce05f34b56e6e6e23a48dedda31afffe64fe/reviews/M19-25/M19_Review_Preservation_20261030/M19_Claude_Formal_Independent_Review_DRAFT_20261031.md#L69)。

上記は今回のClaude回答の保存事実を根拠にした「由来の申告」の記録で、旧原レビューの原証拠ではない。追跡対象に採用するか、今回32件にどう関連づけるかはOwner判断に残す。歴史的R-01〜07とFG-06 R-01〜R-07、E1とE2、過去と今回のGrok未計測事象を混同しない。

先行FG-07横断検証の裁定・結論を根拠として流用していない。現パケット内に含まれる旧版とのpatch、CSVの由来記述、レシートは現在の入力としてのみ参照し、そこにない承認原文を補わない。M19収束のために新たな独立遡及調査ワークフローを自動設置していない。

## 8. Owner裁定候補・文言修正候補・証拠不足の分離

O／W／Eは報告内の判断候補ラベルであり、新たな正式Decision IDではない。下表の「Owner判断」は本報告が裁定を下す意味ではない。

### 8.1 Ownerによる規範選択・最終判断が必要

| 候補 | 判断事項 | 理由・境界 |
|---|---|---|
| O-1 | 裁量型／非裁量型に対するDecision要否とCC-12適用範囲 | 現CC-03裁量型要件は維持。Decision不要の別契約を許容するなら予約・Gate B・監査の明示的整合が必要。存在しないとの推定を裁定の代用にしない。 |
| O-2 | CC-04のother applicable approved requirementsの参照範囲と最終文言 | 削除・契約に限定・不変参照による特定のいずれも影響評価を要する。単なるEditorialと断定せずM19収束時に判断。 |
| O-3 | 2026候補の別途生成・利用・予約証拠の認可状況 | 初期状態参照契約から候補生成権限を導かない。未取得の承認を未承認と断定せず、確認できた証拠範囲で判断。 |
| O-4 | CLD3-01 Major、R系列識別と別紙の根拠充足 | 分類が証拠留保であることを解消認定にしない。M19最終Dispositionと歴史的証拠の扱いを分ける。 |
| O-5 | 原32件の最終Disposition、新規8件・台帳外CLD2の追跡方法 | 原ID保持。正式統合、削除、Close、Severity再評価を今回代行しない。 |
| O-6 | 改訂案提出後のReview Acceptance／Freezeへの条件 | 独立レビュー受領や本報告完成は承認ではない。M20–25／RP-023 HOLDの解除は別指示。 |

### 8.2 規範選択を伴わない整理・修文候補（実施していない）

以下は既存の意味・原記録を変えず、出典を明確にする範囲の提案である。本工程ではCSV、ヘッダ、DecisionLog、候補本文を一切修正していない。実際の改訂は次工程の権限に従う。

| 候補 | 修正候補 | 裁定なしで整理できる範囲／超えてはいけない範囲 |
|---|---|---|
| W-1 | 行番号に対象Commit・候補digest・版名を併記 | 現行への参照訂正または旧版基準の明記。規範本文の変更・原引用の改変はしない。 |
| W-2 | 3件の定型根拠を個別化する補助欄の作成 | 取得済み出典、現在確認できた事実、未取得部分を分ける。「修復・承認済み」と創作しない。 |
| W-3 | Severityの原文欄と表示用抽出欄の分離 | GEMINI-01等の原文字列を保持したまま別欄で表示を補助。原Severityの正規化上書きや重大度変更は禁止。 |
| W-4 | 固定時点ヘッダと現在状態の外部説明 | 配布表紙などに候補名・SHA・レビュー受領状況を明記する案。固定原本を改変せず、正式Review Acceptanceと混同しない。 |
| W-5 | 関連・同一候補の比較表を維持 | 8IDを保持して論点群を表示。実質的統合や原Findingの削除に進まない。 |

**この範囲に入らないもの：** CC-04の他要件句削除、DecisionをCC-03だけへ集約する変更、CC-12を条件付きにする変更、2026候補の許容・禁止は、O-1〜O-3の選択に依存する。裁定不要の修文として実行しない。

### 8.3 追加証拠が必要な事項

| 候補 | 不足証拠 | 今回の扱い |
|---|---|---|
| E-1 | 実際に適用される承認済み非裁量型契約・Decision要否・予約適用範囲 | 未取得。条件付きの反例分析に限定し、実在・非実在を断定しない。 |
| E-2 | 2026候補の生成・利用権限、対象年、予約固有証拠、入力契約承認 | 未取得。数値を補完しない。 |
| E-3 | CLD3-01の別紙の固定版、原裁定との追跡 | 16ファイル内で確認不能。現候補L14を別紙の代用にしない。 |
| E-4 | 32原レビュー全文、CLD2各原文・資料名の同定 | 処分案要約と今回回答への依存を明示。必要ならOwnerが次工程範囲を指定。 |
| E-5 | 歴史的E1、E-03／E-04、R系列原裁定、四回答の独立期待SHA | NOT VERIFIED維持。今回取得文書のSHAを過去承認証拠へ変換しない。 |

## 9. 残余リスク・実施境界・次工程

### 9.1 残余リスク

- **権限境界**：Decision条件句と予約条件の適用範囲はOwnerの規範選択を要する。DRAFTの文言だけを実行認可に用いると誤用の余地がある。
- **仕様境界**：2026参照先修復と候補生成・予約経路の承認は別。非裁量型の契約・優先順位が未取得のため、全経路整合を保証できない。
- **証拠境界**：現4回答の本文は取得済みだが、その自己申告のSHA、旧32原報告、歴史的Owner承認は独立検証と区別する。E-03／E-04を検証済みへ変更しない。
- **文書境界**：ヘッダの同一ID、旧参照行、定型根拠により、版と修復状態を誤認しうる。識別補助と規範改訂を分離する。
- **実装境界**：静的条文照合のみ。エンジン実行、数値、テスト、29 InvariantsのV&V、実際のGate・予約・年度末処理は未実施。実装上のfail-open／deadlockの実証ではない。

### 9.2 実施／未実施

| 操作 | 状態 |
|---|---|
| 開始承認レシートを読取り | 実施。記載された承認範囲と禁止事項を確認。 |
| 固定16ファイル再計算 | 実施。SHA-256・サイズ・Git blob SHA-1を既存取得記録と再照合、16/16不変。 |
| 4回答横断、原ID・Severity・Verdict保持 | 実施。新規採番8件、Gemini未採番評価を区別。 |
| 32件CSV集計・個別対応・条件付き留保 | 実施。32ID一意、OPEN 32、Close 0、区分11/10/11。Claude評価6/15/3/8を再集計。 |
| 条項照合・参照行ずれ・ヘッダ読取り | 実施。CC-03/04/05/12焦点とCC-01〜13保護要件を静的確認。 |
| 新規DRAFT報告作成 | 実施。本ファイルのみがユーザー向け成果物。 |
| GitHub照会の再実行／main更新確認 | 本工程では未実施。CV-01の固定Commit取得証拠とローカル実バイトを使用。 |
| エンジン・回帰テスト・29 Invariants V&V | 未実施。テストPASS件数を報告しない。 |
| 旧レビュー原文・歴史的Owner裁定の新規探索 | 未実施。自動の独立遡及ワークフローは起こしていない。 |
| Git commit／push／PR／設定変更／既存ファイル変更 | すべて未実施。新規作業ディレクトリ内の報告・生成補助・検証記録のみ作成。 |
| Finding正式統合・削除・Close／Severity変更 | すべて未実施。処分案・原報告を保持。 |
| Owner裁定／Review Acceptance／Canonical化／Freeze／HOLD解除 | すべて未実施。Owner次工程指示待ち。 |

### 9.3 次工程への推奨と停止状態

1. OwnerがO-1〜O-3の適用契約・Decision要否・2026候補の認可境界を確認する。回答の相違は前提付きで判断し、投票で採否を決めない。
2. 次工程が承認される場合、W-1〜W-4の追跡性補助と、Ownerの規範選択に基づく本文改訂を別々に実施する。元の固定候補・4回答は保持する。
3. 原32件、今回新規8件、台帳外CLD2を別系列で管理し、原Severity・未検証表示・OPENを維持したまま最終処分案をOwnerへ戻す。
4. 改訂版の同一性と影響範囲を確認した後にのみ、再レビュー範囲や正式受理条件をOwnerが決める。本工程からはReview AcceptanceやFreezeを宣言しない。

**M19-FR-CV-02：横断検証DRAFT提出完了。作業を停止し、Ownerの次工程指示を待つ。**

## 付録A. 機械確認方法・証拠上の限界

検証にはPython 3標準ライブラリのみを使用した。`Path.read_bytes()`で読んだ各取得物について`hashlib.sha256`、バイト長、`sha1(b"blob "+size+b"\0"+data)`を計算し、CV-01 inventoryと比較した。CSVは`csv.DictReader`（UTF-8 BOM対応）で解析した。原32IDの一意性とOPEN状態、Claude個別表の件数、新規8ID一意性、報告内の原文引用と取得物の行一致を検証した。依存追加インストール、ネットワーク経由のshell操作、Git操作はしていない。

原文引用は、固定取得物の行文字列から直接生成した。行番号・Commit・資料名をリンクで併記する。GitHubリンクは固定Commit上の出典位置であり、本工程中にリンク先を全件再取得した意味ではない。対象候補・パケット類はD、回答はCを参照し、D/C同一blob対応はCV-01取得記録に依拠する。

本ファイル自身のSHA-256は保存後の実バイトから別途計算し、完了報告に示す。自己参照でファイル内容を変更し続けることを避けるため、本ファイル内に自身のSHAを埋め込まない。SHA計測は文書の同一性検証であり、Owner承認の代替ではない。

