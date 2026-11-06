# SPE RP-023 v0.3｜4AI横断レビューMatrix DRAFT

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
|C|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP023_v03_ChatGPT_Independent_Review_20261106.md`|
|L|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/RP-023_v0.3_Claude_Receipt_and_Independent_Review_DRAFT_20261106.md`|
|K|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP-023_v03_Independent_Review_Report_Grok_20261106.md`|
|G1|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP023_v03_Gemini_G01_Full_Chat_Transcription_20261106.md`|
|G2|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP023_v03_Gemini_G02_Full_Chat_Transcription_20261106.md`|
|G3|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP023_v03_Gemini_G03_Full_Chat_Transcription_20261106.md`|
|GR|R|`reviews/RP-023/v0.3_distribution_draft_20261106/responses/SPE_RP023_v03_Gemini_Transcription_Custody_Verification_Receipt_20261107.md`|
|OC|O|`reviews/RP-023/step29h/responses/SPE_RP023_Step29H_ChatGPT_Independent_Review_20261103.md`|
|OL|O|`reviews/RP-023/step29h/responses/RP-023_Step29H_Claude_Independent_Review_DRAFT_20261103.md`|
|OG|O|`reviews/RP-023/step29h/responses/SPE_RP023_Step29H_Gemini_Independent_Review_Response_20261103.md`|
|OK|O|`reviews/RP-023/step29h/responses/SPE_RP-023_Step29H_Independent_Review_Report_Grok_20261103.md`|
|W|B|`docs/Workflow.md`|
|S|B|`docs/SPE_Documentation_Standard.md`|
|DL|B|`docs/DecisionLog.md`|

## 1. 総合判定・比較方法

|AI|原総合判定|範囲と制約|本工程での取扱い|
|---|---|---|---|
|ChatGPT|Revision Recommended（C:L5,20,86）|LIMITED READY、Owner代替証拠採用。GitHub実バイトSHAは当時未検証（C:L9–14）|今回のWork実測と別記。過去STOP・未検証は変更しない|
|Claude|Revision Recommended（L:L51–57）|新規Majorなし、追加Minor2・Editorial2。本文対応と原裁定の認証を分離|個別表16行と追加4件を採用し、内容を原文対照|
|Gemini|Revision Recommended（G2:L12–14、G3:L193–202）|全文転載3件。本人は個別13原本SHA未計算（G1:L16、G2:L7）|G2と補完G3の両方を読む。表記上の内部相違も保持|
|Grok|Accepted（K:L44–50）|13件取得・11件期待照合申告。原回答の一部詳細行未照合（K:L34,83）|Acceptedは重大副作用を検出しないとの評価。個別16件の充足証明とはしない|

3対1で結論を決めない。Grokは保護維持・重大副作用なしを受入理由とする一方、他3AIは証拠留保や修正候補を残す。Claudeはさらに旧HOLDガード削除等を具体的に指摘する。判断閾値・検証粒度の差を、Owner正式Acceptance・consensusの成立と混同しない（W:L27–31）。

作業語：確認済み＝当該AIが文面対応を明示した範囲、対応候補＝採用案があるだけ、部分対応＝残余あり、未対応＝要求された具体物なし、Owner判断留保＝AI未決定、言及なし＝当該原IDの個別評価なし。AIの原ラベルは引用的に保持し、Workの独立評価は右欄に分離する。

## 2. 原16 Finding Matrix

原SeverityはMajor4／Minor10／Editorial2、合計16。各行の原IDを維持し、同趣旨でも統合・減算しない。正式Statusがない原報告にOPEN/CLOSED等を補わない。以下の全件の正式Dispositionは本工程で未確定。

|原ID|原Severity|原要求・原出典|ChatGPT評価|Claude評価|Gemini評価|Grok評価|一致点／相違点|Work暫定評価・固定本文根拠|未検証・次に必要な確認|
|---|---|---|---|---|---|---|---|---|---|
|H29-01|Major|Header必須項目；OC:L29–35|文面対応 C:L50|対応 L:L123,144–149|候補あり・実日付未実施 G3:L15–22|H29-01等の群評価のみ K:L65|C/Lは実装確認、Gは未反映と記す|確認済み（文面）：V3:L1–6で5項目充足、日付実値あり|Gの候補表記は固定本文と不一致。日付の出来事真正性までSHAで証明しない|
|H29-02|Minor|OD-08時点差；OC:L37–43|条件付対応 C:L51|対応・原証拠留保 L:L124,151–156|部分対応 G3:L25–32|言及なし（ChatGPT系の群のみ）|時点分離は一致、原承認は留保|部分対応：V3:L99,108に後続報告と未認証注記|Step28原発言未取得。旧ガード削除はB-01と別管理|
|H29-03|Minor|A未照合→限定判断の具体例；OC:L45–51|部分対応 C:L52|未対応（候補のみ）、規範安全装置あり L:L125,158–163|部分対応／現状維持 G3:L35–42|言及なし（群のみ）|安全装置ありは一致、例示の充足評価に差|未対応（具体例）：V3:L52,56,66–70は既存保護、具体例追加なし|例示は任意補強候補。新規例外権限を作らない|
|RP23-CLD-01|Major|Snapshot／DL-010と非代替；OL:L75–80|文面対応 C:L53|概ね対応、相互参照・DL残余 L:L126,165–171|候補あり G3:L45–52|個別言及なし（Claude群 K:L66）|Snapshot明記は一致、完備度の差|確認済み（中核）：V3:L28に非代替性とB/C新ゲート否定|§4.3/§5とDL-010への参照は任意候補、成立履歴の認証は別|
|RP23-CLD-02|Minor|Header＋自己検証範囲；OL:L82–87|文面対応・過去履歴維持 C:L54|概ね対応、AC/NC記録残余 L:L127,173–178|候補あり G3:L55–62|個別言及なし（Claude群）|Header改善と過去自己検証は別|部分対応：V3:L1–6は充足。旧07C-04を改訂した証拠ではない|旧自己検証の訂正必要性はOwner判断、過去PASSを遡及変更しない|
|RP23-CLD-03|Minor|検証担当の定義・独立性；OL:L89–94|Owner判断留保 C:L55,74|Owner判断留保 L:L128,180–186|未対応（Owner留保）G3:L65–72|新規MUSTなし K:L58|4AIは別人MUSTの不追加を肯定|Owner判断留保：V3:L83,89の担当規定は元のまま|OD-06原裁定未照合。別人必須化は規範追加となり得る|
|RP23-CLD-04|Minor|チャット裁定とDecisionLog；OL:L96–101|条件付対応 C:L56|文面対応・原証拠留保 L:L129,188–194|部分対応 G3:L75–82|具体修正候補、記録要否残 K:L66,84|記録義務参照は一致、実際の記録の充足は別|部分対応：V3:L24,105とW:L11が整合|07A/P0原発言・DL個別対応未検証。延期許可は追加されていない|
|RP23-CLD-05|Minor|OD-08旧状態；OL:L103–108|条件付対応 C:L57|文面対応・原証拠留保 L:L130,196–200|部分対応 G3:L85–92|個別言及なし（Claude群）|H29-02と関連するがID別|部分対応：V3:L99,108|Step28レシート未取得、時点整序と採否を分離|
|RP23-CLD-06|Minor|非遡及の個別例示；OL:L110–115|文面対応 C:L58|対応 L:L131,202–206|候補あり G3:L95–102|個別言及なし、非遡及全体維持 K:L59|一般化の維持は概ね一致|確認済み（文面）：V3:L81。個別状態の断定削除|実案件の状態を再裁定しない。「本書の例示」の参照先は編集残余|
|RP23-CLD-07|Editorial|§8／2Commit／元diff／旧状態の4小論点；OL:L117–121|部分対応 C:L59|概ね対応 L:L132,208–215|部分対応 G3:L105–112|修正候補ありの群評価 K:L66|証拠限界の維持は一致|部分対応：V3:L15,91,117。4小論点を一つの原ID内で保持|E完全SHA・N/E比較は今回確認。元07C-03.diffは未取得、§8運用は追加候補と関連|
|Gemini F-01|Major|B/C一律要求の懸念；OG:L24–31|既存保護確認 C:L60|既存保護、不足特定不能 L:L133,217–222|既存保護あり（部分）G3:L115–122|既存保護の群評価 K:L67|一律ファイル要求の具体箇所が未特定|確認済み（保護）：V3:L25,37–38,48,52,89。旧版にも保護あり|原Majorは維持。具体的な反例が出ればその範囲のみ再評価|
|Gemini F-02|Major|Workflow手続接続；OG:L33–40|部分対応 C:L61|既存保護、相互参照は任意 L:L134,224–229|既存保護あり（部分）G3:L125–132|既存保護の群評価 K:L67|Review/waiver/consensusの維持は一致|確認済み（保護）：V3:L28,62,99。Snapshot固有論点と分離|運用実行ログは対象外。相互参照不足を手続削除と同一視しない|
|Gemini F-03|Minor|Header Rulesと状態軸；OG:L42–49|既存保護＋文面改善 C:L62|対応 L:L135,231–234|既存保護あり（部分）G3:L135–142|個別言及なし（Gemini群）|状態軸とHeader参照は既存保護|確認済み（文面）：V3:L58およびL1–6|G3のH29-01評価とは分ける。他文書のHeader全件適合は対象外|
|Gemini F-04|Minor|非遡及の強調；OG:L51–58|既存保護確認 C:L63|対応 L:L136,236–239|既存保護あり（部分）G3:L145–152|既存保護の群評価 K:L67|非遡及条項の維持で一致|確認済み（保護）：V3:L30,81,85|個別既存承認の真正性の認証ではない|
|RP023-29H-Grok-01|Minor|新規必須enumへ置換しない；OK:L64|既存保護確認 C:L64|既存保護、追加任意 L:L137,241–245|既存保護あり（部分）G3:L155–162|既存保護の群評価 K:L68|enum非置換の明文ありで一致|確認済み（保護）：V3:L42はV2:L37と同文|新enumは追加しない。運用実態まで確認したものではない|
|RP023-29H-Grok-02|Editorial|Header/Status参照；OK:L65|文面対応 C:L65|対応、追加不要 L:L138,247–250|説明補強候補 G3:L165–172|既存保護の群評価 K:L68|明文化の追加必要性に差|確認済み（中核）：V3:L58、冒頭Header|必須フィールド欠落と相互参照の簡潔さは別。任意補強を必須化しない|

GrokのK:L61–70は4行の群別表である。「全16件を個別に追跡」との自己申告（L70）はあるが、H29-02等の個別評価は表に示されない。未記載の個別評価をAcceptedから補完しない。Gemini G3:L19,59はヘッダを候補・未反映と記すが、同じ報告が指定する固定SHAのV3:L1–6には実値がある。これは実体対照の不一致であり、原Finding正式棄却やGemini回答全体無効の認定ではない。

## 3. M01〜M07・§8限定修正の評価差

|対象|ChatGPT|Claude|Gemini|Grok|Work独立結果|
|---|---|---|---|---|---|
|M01|文面PASS C:L26|形式充足 L:L65|G2:L21は整序肯定、G3:L19,59は候補扱い|全体肯定 K:L50,54|本文Headerは充足。実日時の原出来事認証とは別|
|M02|文面PASS C:L27|参照追加、新ゲートなし L:L66,78–81|保護維持 G2:L21|非代替性肯定 K:L55|W§3と一致、全B/C受領への拡張なし|
|M03|CONDITIONAL C:L28|既存記録義務参照 L:L67,83–84|維持 G2:L21|追記候補として肯定 K:L56|本文規定は整合、実DL対応は未検証|
|M04|文面PASS C:L29|弱化なし、参照曖昧 L:L68|維持 G2:L21|非遡及維持 K:L59|一般化＋限定HOLD維持。個別案件認定なし|
|M05|文面PASS・運用留保 C:L30|適用外の余地 L:L69,264–270|保護維持 G2:L21|維持 K:L54|必須非減免は保持、共通項目の適用外基準は残余|
|M06|CONDITIONAL C:L31|旧HOLDガード削除を追加指摘 L:L70,256–262|時点分離肯定・原記録留保 G2:L30–33|状態明確化・副作用なし K:L50,57|B-01 PARTIAL。削除事実と保護全体の効果を分離|
|M07|CONDITIONAL C:L32|注記の本文混在がEditorial L:L71,272–284|二次記録維持 G3:L109–112|概括的に副作用なし K:L50|役割区別は妥当。E完全SHA・N/E比較は今回独立確認|
|RD-01|「なお」独立段落を確認 C:L36|旧段落全文保持 L:L72|近接重複が残ると指摘 G2:L50–53、G3:L185–190|可読性向上 K:L54|固定版は既に解消。前版と限定Diffも今回照合PASS|

## 4. 追加Finding・残余索引（原16件とは別）

原IDのある追加候補はそのまま維持。Gemini候補には原IDがないため出典節で識別する。追加Finding候補7件＋ChatGPTの証拠／運用残余2件。原16件を25件の正式Findingへ拡大したものではない。

|原追加ID／出典|原Severity|内容・根拠|他AIとの対応（明示／関連を分離）|Work暫定評価・必要確認|
|---|---|---|---|---|
|RP23V3-CLD-01|Minor|OD03/05/08後続状態、旧HOLD削除 L:L256–262|C:M06条件付／G2時点整合肯定／K副作用なし。完全同一追加IDへの言及はなし|削除事実確認。旧未決と未認証は別概念。B-01で局所明示性低下をPARTIAL、全体保護廃止とは認定しない|
|RP23V3-CLD-02|Minor|§8「等」「適用外」 L:L264–270|C:NEW-01と運用境界が部分重複。Geminiは編集重複のみ、K個別言及なし|必須非減免保持。理由付け必須化・適用外限定は規範変更の可能性|
|RP23V3-CLD-03|Editorial|起案注記・AI名の本文混在 L:L272–277|他3AIは同一追加論点への言及なし|参照管理の編集候補。Updated By違反ではないというClaude留保も維持|
|RP23V3-CLD-04|Editorial|見出し、Git未反映、例示参照、系譜の4小論点 L:L279–284|他3AIは4項目の個別指摘なし|4項目保持。時点注記・main限定・基準版追記の候補。OD05具体未指定が残るので「未決項目皆無」とは断定しない|
|ChatGPT NEW-01|Minor候補|未実施／未確認／適用外の運用境界 C:L78|Claude02と部分重複。推奨はCが例示、Lが適用外基準の制約追加で異なる|同じ対照資料を使えるが推奨意味論が異なる。原IDを統合しない|
|ChatGPT NEW-02|Severity付与なし・証拠残余|元07C-03.diffと今回Diffの非同一 C:L79|旧CLD07(3)・Claude証拠留保と関連|元添付未取得を維持。今回Diffの再現PASSは代用にならない|
|ChatGPT NEW-03|Severity付与なし・運用残余|LIMITED READYの一般化防止 C:L80|Claude／Gemini／Grokは同じ例外経路の個別評価をしていない|B-05 PASS（限定記録を確認）。原Owner指示の直接認証は未検証|
|Gemini追加Editorial候補 G2§3／G3§C（原IDなし）|Editorial候補（G3の表記）|§8「共通項目は」近接重複 G2:L50–53、G3:L185–190|C:L36と対立、L:L72は旧文保持。Kは可読性向上の概括評価|FAIL（固定版で重複が残るという事実前提）。V3:L89,91、RD-01で解消済み。正式Closeはしない|
|RP023-v03-Grok-01|Editorial|Custody二文書の外部自己SHA対応 K:L72–76|他AIも自己SHA期待値留保を持つが同一IDの評価はなし|外部実行レシートを今回回収しD13/13期待値一致。所在注記を次版資料に付す候補、原レシート真正性とは別|

## 5. 工程Aの終了状態

**PASS（Matrix作成・原ID追跡の範囲）**。内容の採否、4AIの優劣、正式consensus・Dispositionは未決定。Bの規範・証拠監査とCの候補は別成果物に接続する。未記載個別評価・原裁定未照合を残したまま、次工程を自動開始しない。
