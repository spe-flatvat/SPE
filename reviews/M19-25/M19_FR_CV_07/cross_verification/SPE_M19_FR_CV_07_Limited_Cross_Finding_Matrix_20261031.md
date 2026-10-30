# SPE M19-FR-CV-07｜限定横断Finding対応表 DRAFT

**Status:** DRAFT / NON-CANONICAL / CONDITIONAL MAINTAINED  
**固定D:** e195b9ecdc0e6930f44fce2b598e2c60887c92e4  
**固定C:** d1c13df4f18246e1b52f50640dece5477132beb5  
**日付:** 2026-10-31（JST）  
**最終Disposition:** 本工程では一切設定しない。M19–M25／RP-023 HOLD維持。

## 1. 比較方法・識別境界

本表は15原IDを保持した暫定分析であり、正式なFinding統合台帳ではない。T01〜T09は本報告内の論点ラベルで、新規Finding ID・裁定IDではない。一原IDが複数Tへ対応し、一Tが複数原IDを参照する。原Severity・Statusを変更せず、重大度の平均・多数決・正式Closeを行わない。

Status未記載は未記載とする。ChatGPTの暫定Findingという全体注記は保持し、レビュー全体のSTOP／ACCEPT／REVISEを個別Finding Statusへ転用しない。Geminiの全主張には派生物と14正本の「対応未検証」を適用する。

**A列**は局所的な根拠の直接性・今回の検証状況、**B列**は当該AIが実施した範囲の網羅性で、互いに独立する。Aが直接確認でもBの全文網羅は推定しない。原引用・資料の存在確認は、その主張全体の採否認定ではない。

## 2. 原Findingの識別・主張・前提（15件）

| AI／原ID | 原Severity | 原Status | 対象箇所 | 原主張の要旨（派生要約） | 依拠する前提／証拠 | 原報告位置 |
|---|---|---|---|---|---|---|
| ChatGPT／CV07-GPT-01 | Minor | 暫定Finding（L39、全件共通）。個別Statusなし | CC-04／P-02、Patch第2 hunk | 不変の参照と、その参照先の規範的承認権限の有効性を別々に検証する旨を明示する提案。 | 不変digestだけでは承認権限を証明しない。現文が既に要求する承認証拠との関係を区別。 P-02 immutable authoritative source reference | [SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md L33](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/ChatGPT/SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md#L33) |
| ChatGPT／CV07-GPT-02 | Minor | 暫定Finding（L39、全件共通）。個別Statusなし | CC-03／P-01、CC-12／P-04 | 将来Decision-free経路においてもTrigger証拠・競合予約・Gate検証の保持条件を明確化する提案。 | 将来例外は別承認・整合改訂が必要で、今のDecision省略許可ではない。 将来改訂とP-01／P-04 | [SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md L34](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/ChatGPT/SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md#L34) |
| ChatGPT／CV07-GPT-03 | Minor | 暫定Finding（L39、全件共通）。個別Statusなし | CC-04／P-03 | creation/useとscheduling/reservation/effectuationを一括許可と誤読しない検証マトリクスを求める提案。 | 操作別の適用範囲は分離されるべきだが、その実装証拠はない。 2026候補に関するP-03 | [SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md L35](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/ChatGPT/SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md#L35) |
| ChatGPT／CV07-GPT-04 | Major（証拠条件） | 暫定Finding（L39、全件共通）。個別Statusなし | CV05裁定レシート／歴史的裁定 | Owner転記は独立認証された原記録でなく、N01=A／N02=B／N03=Aへの依拠と歴史的裁定の確認完了を区別する。 | 原会話一次認証が未取得。将来方向の選択は過去承認の証明ではない。 CV05個別レシート、証拠階層 | [SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md L36](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/ChatGPT/SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md#L36) |
| ChatGPT／CV07-GPT-05 | Major（検証条件） | 暫定Finding（L39、全件共通）。個別Statusなし | Rev.2全体／29 Invariants | 静的PASSは動的V&Vを証明しない。正式承認前に実行検証と証拠対応が必要とする。 | 動的V&V未実施。正式承認前というゲート時点は原報告の要求であり、その採用は別判断。 厳密差分レシート、29 Invariants | [SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md L37](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/ChatGPT/SPE_M19_FR_CV_07_ChatGPT_Independent_Review_CHAT_TRANSCRIPT_20261031.md#L37) |
| Gemini／CV07-GEM-01 | Editorial | 個別Status未記載 | CV06 Rev.2候補／CC-04、P-03 | authorized source and creatorの残存を文書間の微小な表現ゆれとし、実質意味差なしとして用語統一を推奨。 | creator削除は実質変更でないという評価。派生閲覧物と14正本の対応未検証。 CV06条項横断検証報告Source09と修文案Source10 | [SPE_M19_FR_CV_07_Gemini_Independent_Review_CHAT_TRANSCRIPT_20261031.md L57](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Gemini/SPE_M19_FR_CV_07_Gemini_Independent_Review_CHAT_TRANSCRIPT_20261031.md#L57) |
| Gemini／CV07-GEM-02 | Minor | 個別Status未記載 | 全体（CV07 Packet）、CC-04 P-02 | 複数外部契約競合時の優先順位解決が未定義の場合、厳格fail-closedの運用注記を補強する提案。 | 解決スキーム未定義と意図されたfail-closedを分離。対応未検証。 P-02 expressly approved rule applicable to the conflict | [SPE_M19_FR_CV_07_Gemini_Independent_Review_CHAT_TRANSCRIPT_20261031.md L58](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Gemini/SPE_M19_FR_CV_07_Gemini_Independent_Review_CHAT_TRANSCRIPT_20261031.md#L58) |
| Grok／GRK-CV07-01 | Editorial | 個別Status未記載 | CC-04 L154付近 | other applicable approved requirementsの語の広さが残る。後続義務で制約されるが任意で語を限定する提案。 | 後続検証義務は有効と読む。範囲の明確化と実質縮小は別。 N02案B・P-02 | [SPE_M19_FR_CV_07_Grok_Independent_Review_CHAT_TRANSCRIPT_20261031.md L69](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Grok/SPE_M19_FR_CV_07_Grok_Independent_Review_CHAT_TRANSCRIPT_20261031.md#L69) |
| Grok／GRK-CV07-02 | Editorial | 個別Status未記載 | 受領／証拠 | 本人実バイトSHA未計算・Termux補完依存の記録を維持し、本人PASSへ書き換えない。 | 本人独立計測と補完採用を区別。元のOwner会話は未認証。 Owner代替裁定の記録 | [SPE_M19_FR_CV_07_Grok_Independent_Review_CHAT_TRANSCRIPT_20261031.md L70](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Grok/SPE_M19_FR_CV_07_Grok_Independent_Review_CHAT_TRANSCRIPT_20261031.md#L70) |
| Claude／CLD5-01 | Minor | 個別Status未記載 | Rev.2 L154／156／121／407／409 | Decision条件付き・無条件の表現が二重。CC-03／05／12への参照を揃える提案。 | fail-open確定ではない。条件句と現在の禁止境界が併存する。 CV05-N01=A、現候補各条文、詳細L65–70 | [M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md L58](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Claude/M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md#L58) |
| Claude／CLD5-02 | Minor | 個別Status未記載 | Rev.2 L156第2文 | Each dependent transition operationが2027年以降にも読めるため、2026対象を明示する提案。 | 見出し・前後文で2026に限定する読解と、単文の広い読解が競合しうる。 L156第1文・第2文、詳細L72–75 | [M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md L59](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Claude/M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md#L59) |
| Claude／CLD5-03 | Minor(Owner 確認要) | 個別Status未記載 | Rev.2 L156末文、N03レシート§2 | 案A定義にある生成者と、Rev.2のcreator-identity approval schema不創設の関係を問題化しOwner確認を求める。 | 案Aの定義は転記レシート・パケット依存。原報告の「経路は存在しない」は今回裏付け不可。 N03 L17、NP §5、CROSS F03、詳細L77–82 | [M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md L60](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Claude/M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md#L60) |
| Claude／CLD5-04 | Minor | 個別Status未記載 | L154／156／409とL215／315／278 | 新設義務のGate・監査・理由コードへの接続不足を指摘し、Gate B検証とTransition Record記録等を提案。 | 一般的な検証・監査要求は存在するが、新設項目の明示参照がない。 現候補新設文と既存Gate B／監査／理由、詳細L84–87 | [M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md L61](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Claude/M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md#L61) |
| Claude／CLD5-05 | Minor | 個別Status未記載 | packet e750f613…／ddb86d69…／9b6ed7f5… | 旧P文案とRev.2実文が異なり、逐文で裁定・根拠・限界を追える表を追加する提案。 | P-01〜04という同じラベルが異なる段階の文言に用いられる。 TRACE、CROSS、DR、詳細L89–91 | [M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md L62](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Claude/M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md#L62) |
| Claude／CLD5-06 | Editorial | 個別Status未記載 | 厳密差分レシート§4、Rev.2 L471以降 | 29 invariants: PASSを未実行と区別して表示し、新境界の将来V&V対応も検討する提案。 | テキスト／差分確認と動的テストは別。網羅性の追加要求は別判断。 DR L47／51／58、Invariants、詳細L93–95 | [M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md L63](https://github.com/spe-flatvat/SPE/blob/d1c13df4f18246e1b52f50640dece5477132beb5/reviews/M19-25/M19_FR_CV_07/reviewer_responses/Claude/M19_FR_CV_07_Claude_Independent_Review_DRAFT_20261031.md#L63) |

## 3. 暫定対応・A根拠強度・B網羅性・Owner判断待ち

| 原ID→論点 | A：根拠の直接性・検証状況 | B：当該AIのレビュー網羅性 | 残余リスク | 提案分類／Owner判断待ち |
|---|---|---|---|---|
| CV07-GPT-01 → T01 | 現CC L154に不変参照・attributable approval evidence・applicabilityが並列MUSTとして存在することを直接確認。追加の手続分離が必要かは未確定。 | 原報告L27／57で全文逐条・網羅確認未完了。今回の局所根拠が直接でも、そのAIの無指摘箇所を問題なしとは扱わない。 | 義務の欠落と、既存義務の説明補強を混同するリスク。 | 修文候補（DRAFT）／具体的承認証拠は補完要。別々の確認の意味・正式採用。新承認権限を生成しない。 |
| CV07-GPT-02 → T02／T05 | CC L121／407／409に現在の証拠保護と将来別承認がある。将来の例外契約は未取得。 | 原報告L27／57で全文逐条・網羅確認未完了。今回の局所根拠が直接でも、そのAIの無指摘箇所を問題なしとは扱わない。 | 将来設計の推奨を、現時点の追加MUSTや例外承認へ変換するリスク。 | 修文候補（DRAFT）／将来Owner裁定要。将来例外の許容・要件・実装範囲。現在許可を推認しない。 |
| CV07-GPT-03 → T03／T05 | CC L156第1文に操作列挙、第2文にauthorization basis等がある。実装マトリクスと実行証拠は未取得。 | 原報告L27／57で全文逐条・網羅確認未完了。今回の局所根拠が直接でも、そのAIの無指摘箇所を問題なしとは扱わない。 | 資料整理の提案と、未承認の実装スキーマ義務追加の混同。 | 修文・追跡表候補（DRAFT）／証拠補完要。検証マトリクスを資料として要求する範囲と規範採用を分ける。 |
| CV07-GPT-04 → T07 | N01／N02／N03の転記は固定資料で確認。Request L15–30にも証拠制限がある。原会話は未取得。 | 原報告L27／57で全文逐条・網羅確認未完了。今回の局所根拠が直接でも、そのAIの無指摘箇所を問題なしとは扱わない。 | 今回SHA一致をOwner過去承認の真正性証明へ昇格させるリスク。 | 証拠補完要／採用範囲はOwner裁定要。原証拠の補完・二次証拠を用いる範囲。原Majorを勝手に解消しない。 |
| CV07-GPT-05 → T08 | DR L47／51／58およびCC L503は静的／未実行を明示。正式承認前の実行必須化が既存の確定工程条件かは未検証。 | 原報告L27／57で全文逐条・網羅確認未完了。今回の局所根拠が直接でも、そのAIの無指摘箇所を問題なしとは扱わない。 | 実V&V未実施という事実から、新しい承認順序・ゲート条件を自動設定するリスク。 | 証拠補完要／検証ゲート時点はOwner裁定要。どの承認・実装・Freeze段階で何を要求するか。Major保持・Closeなし。 |
| CV07-GEM-01 → T04／T06 | TRACE L43にcreator、CROSS L40に削除推奨、CC L156にschema不創設がある。N03 L17とNP L43には生成者の列挙がある。意味差なしという評価は未裁定。対応未検証。 | 原報告はQ1〜10等の広い確認を申告。ただし派生物と14正本の対応未検証。本人の個別payload検証も未完了。 | Owner案A定義にある生成者をEditorialとして無断削除するリスク。 | Owner裁定要／解説整理はその後のDRAFT候補。生成者の特定と固定creator-identity schema新設の差を解釈。原Editorialは変更しない。 |
| CV07-GEM-02 → T01 | CC L154には承認済み優先規則のみ使用・推定禁止・解決不能ならfail-closedが既にある。新しい優先順位を必要とする根拠はない。対応未検証。 | 原報告はQ1〜10等の広い確認を申告。ただし派生物と14正本の対応未検証。本人の個別payload検証も未完了。 | 解説補強を口実に未承認の自動調停・階層を導入するリスク。 | 修文候補（DRAFT）。優先規則新設は別Owner裁定。説明の必要性。新しい調停規則を現規範としない。 |
| GRK-CV07-01 → T01／T02 | CC L154に語が残存し、検証義務も追記されていることを直接確認。許容される要件集合自体の確定は未取得。 | Q1〜10の静的レビュー完了申告。本人SHA計測・patch再実行・動的V&Vは未実施。網羅性の独立証明ではない。 | 単純削除が正当な他要件を落とす可能性。語の存在だけで免除成立とはならない。 | 修文候補（DRAFT）／範囲が変わる場合Owner裁定要。N02の起案範囲内か、採用に別承認が必要かを判断。 |
| GRK-CV07-02 → T09 | Grok L18–20／保全レシートL20–21で未実施申告を直接確認。実行ログと元会話の独立認証は未取得。 | Q1〜10の静的レビュー完了申告。本人SHA計測・patch再実行・動的V&Vは未実施。網羅性の独立証明ではない。 | Workの現在のSHA一致で過去のGrok検証を完了扱いするリスク。 | 証拠留保維持／必要なら補完証拠取得。追加証拠採用の範囲。原記録の変更不要。 |
| CLD5-01 → T02／T01 | 条件句L154／156と、Decision-free非認可L121／409およびL407を直接確認。適用優先の読みは解釈の残余。 | 14件読了・全文を重点通読・13/13検証との自己申告。静的範囲であり、全状態網羅・動的V&V・真正性の認証ではない。 | 表現統一で現在義務を拡張・弱化させる可能性。旧CLD4解消申告は正式Closeでない。 | 修文候補（DRAFT）／意味選択はOwner裁定要。相互参照追加と要件変更を区別し、将来例外機構も保持。 |
| CLD5-02 → T03 | 見出しと第1文は2026、次文の主語に2026の再掲がないことを直接確認。実際の2027追加義務成立は未確定。 | 14件読了・全文を重点通読・13/13検証との自己申告。静的範囲であり、全状態網羅・動的V&V・真正性の認証ではない。 | 局所的曖昧さを全年度義務追加の確定と誤認するリスク。 | 修文候補（DRAFT）／適用範囲はOwner確認。2026限定を確認するか、より広い規範選択を要するか。 |
| CLD5-03 → T04／T07 | N03 L17／NP L43の生成者記載、CROSS L40のnot expressly present主張、CC L156末文の差を直接確認。元Owner意図とE-2の不存在は未認証。 | 14件読了・全文を重点通読・13/13検証との自己申告。静的範囲であり、全状態網羅・動的V&V・真正性の認証ではない。 | 生成者の列挙と特定スキーマ承認を同一視する／未発見を不存在にするリスク。 | Owner裁定要／原会話・案A定義は証拠補完要。誰が生成・認可するかの識別が既存creation/use根拠に包含されるか、別要件か。 |
| CLD5-04 → T05 | L215／315／319に既存の承認証拠・checkpoint・不変参照がある。新設義務の名指し接続が薄いことと、監査義務全面欠落は別。 | 14件読了・全文を重点通読・13/13検証との自己申告。静的範囲であり、全状態網羅・動的V&V・真正性の認証ではない。 | 全チェックをGate B一箇所へ集約し、予約前・生成前チェックを後回しにする副作用。 | 修文・追跡表候補（DRAFT）／実装契約はOwner裁定。操作時点・予約前・target年checkpointの配置、スキーマ／理由コードの承認範囲。 |
| CLD5-05 → T06 | TRACE L33の置換案と現CC L154／PATCH L17の追記、P03 creator差を直接確認。DRは局所観測への対応表を持つが全逐文表ではない。 | 14件読了・全文を重点通読・13/13検証との自己申告。静的範囲であり、全状態網羅・動的V&V・真正性の認証ではない。 | 旧案を固定レビュー対象に代用する／起案方針を正式採用とする誤読。 | 追跡表・版の説明候補（DRAFT）。別紙の採用・旧資料の位置づけ。既存資料へsuperseded等を無断追記しない。 |
| CLD5-06 → T08 | PASS表示と未実行注記を直接確認。現29リストとsource同一性は静的比較可能。全要件に対する充足・実行はNOT VERIFIED。 | 14件読了・全文を重点通読・13/13検証との自己申告。静的範囲であり、全状態網羅・動的V&V・真正性の認証ではない。 | Editorial表示修正と新しいInvariant追加という実質規範変更の混同。 | 表示注記DRAFT／V&V網羅性は証拠補完・Owner裁定。今後の試験対応と承認ゲート。既存29項目を自動変更しない。 |

## 4. 論点対応関係（正式統合ではない）

| 論点／対象原ID | 区分 | 一致・相違・前提 | A：根拠の直接性 | B：レビュー網羅性 | 暫定分析（非裁定） |
|---|---|---|---|---|---|
| T01：外部参照・承認有効性・優先順位／CV07-GPT-01／GRK-CV07-01／CV07-GEM-02、CLD5-01関連 | 関連するが別論点／部分一致 | 不変性と有効な承認、語の広さ、競合処理は異なる。明示承認規則のない優先順位を創作しない点に共通性。 | CC L154、N02 L16を直接確認。Gemini依拠の派生物対応未検証。 | GPTは限定的。Grokは静的Q対応。Geminiは対応未検証。ClaudeはDecision表現の焦点で関与。 | 現L154に参照・承認証拠・適用性・解決不能時fail-closedの要求がある。文言補強の必要性と既存義務欠落を分ける。 |
| T02：Decisionの現在義務と将来例外／CV07-GPT-02／CLD5-01、GRK-CV07-01関連 | 部分一致／関連するが別論点 | GPTは将来例外でも他の保護要件保持、Claudeは現在の条件付き／無条件表現の二重性。 | CC L121／154／156／407／409を直接確認。将来承認契約は未取得。 | GPTの全文未精査を維持。Claudeの局所比較、Grokの語の提案を全経路整合証明に拡大しない。 | 現条文から現在Decision-free経路の許可は導けないが、表現の参照整理という残余を保持する。 |
| T03：2026の操作別認可と年度範囲／CV07-GPT-03／CLD5-02 | 関連するが別論点 | 操作ごとの一括許可リスクと、L156第2文の年度範囲は異なる。 | L156の2026見出し・第1文とEach dependent transition operationを直接確認。 | GPTの限界を維持。Claudeの指摘は局所的文面、網羅的な年度別実装検証ではない。 | 2026限定と読む文脈はある。2027+への義務追加が確定したとも、限定が完全無曖昧とも断定しない。 |
| T04：生成者の列挙とcreator-identity schema／CV07-GEM-01／CLD5-03 | 部分一致＋評価前提の矛盾 | 表現差の存在は関連するが、Geminiの実質差なしとClaudeのOwner案Aとの差には判断の相違。 | N03 L17／NP L43に生成者、TRACE L43にcreator、CROSS L40、CC L156末文を直接確認。Gemini対応未検証。 | Geminiの網羅性申告は対応未検証。Claudeは資料を示す局所主張であり原Owner意図認証ではない。 | 文面差とレシート定義の生成者記載を確認。誰／何の識別と新schema承認は同じ命題ではなく、規範効果はOwner判断待ち。 |
| T05：Gate・監査・検証マトリクス／CLD5-04／CV07-GPT-02／CV07-GPT-03 | 関連するが別論点 | 明示接続不足、将来例外条件、操作別マトリクスは補完的だが同一要求ではない。 | CC L154／156／215／278／315／319／407／409を直接確認。実装契約未取得。 | GPTは限定。Claudeも静的指摘。誰も当該実装の動的検証完了を示していない。 | 一般的監査要求は既存文にある。名指し接続が薄いことを監査義務ゼロと同一視しない。Gate Bへの全件集約は時点副作用を要検討。 |
| T06：Pラベルの版と逐文追跡／CLD5-05／CV07-GEM-01関連 | AI固有の要求／関連するが別論点 | ClaudeはRev.2逐文対応、Geminiはcreator用語。Pラベル共有でも異なる版の実文がある。 | TRACE L33／43、CROSS、PATCH L17／19、CC L154／156、DR §3を直接確認。 | Claudeの局所追跡要求とGemini対応未検証を保持。全パケット無誤りの認定ではない。 | 旧案→局所指摘→Rev.2→厳密差分の役割を別記するDRAFTは有用。原資料を無断更新しない。 |
| T07：Owner転記・歴史的証拠／CV07-GPT-04、CLD5-03の前提と関連 | AI固有の採番／共通の証拠留保 | MajorはGPT原Severity。他AIも証拠留保に言及するが、同じMajor Findingを提出したと数えない。 | CV05個別レシートの転記とREQ L15–30を直接確認。一次原会話は未取得。 | 4AIの証拠留保表明とレビュー網羅性を分離。Geminiの無条件的評価語も対応未検証のまま保持。 | 転記資料への条件付き文面比較は可能だが、歴史的承認確認・正式受理へ昇格させない。 |
| T08：静的PASS・29 Invariants・承認前V&V／CV07-GPT-05／CLD5-06 | 部分一致／要求範囲は別 | 未実行の事実は共通。GPTの承認前実行要求とClaudeの表示修正・将来項目追加は同じではない。 | DR L47／51／58、CC L471–503を直接確認。実行証跡なし。 | GPTも全体未精査。Claudeは静的。Gemini/Grokの未実施申告を第三者実行証拠にしない。 | 静的PASSは動的PASSでない。正式承認前の必須実行という工程条件と、追加Invariantの採用はOwner留保。 |
| T09：受領例外・本人未計測・真正性／GRK-CV07-02、各AI受領記録 | AI固有のFinding／共通証拠境界 | Grok本人未計測の保持。ChatGPT限定確認・Gemini派生対応・転記真正性は別の留保。 | Grok L18–20、各レシートを直接読取。未取得ログ・元会話はNOT VERIFIED。 | 受領整合性とレビュー全文網羅性は異なる。Workの22件再計算で当時の本人作業は変わらない。 | 現在の同一性確認と過去の検証行為を区別して保存する。新たなOwner補完採用はしない。 |

**一致として扱える限定命題：** SHA一致が過去の本人実行やOwner承認を証明しないこと、動的V&V未実施を実行PASSにしないことは、複数報告の留保に共通する。これは全Findingの採否一致を意味しない。T04の実質意味差については評価前提が対立し、原Owner意図までの確定は判断不能。AI固有の採番は「他AIが見落とした証明」でもない。

## 5. 原報告がいう既存Findingの状態（別集合）

下表は原報告の申告を保存する。Ownerの正式Dispositionではなく、本工程による旧原指摘の完全再監査でもない。旧32 OPEN、旧8未裁定、今回15新規局所IDを混算しない。

| 既存ID | 原報告位置 | 原報告の申告 | 本工程の境界 |
|---|---|---|---|
| CLD3-01 | ChatGPT L75、Gemini L50、Grok L106、Claude L99 | Major OPENの保持（GPTの当該行はMajor表記なし） | CC L14と旧ヘッダは存在。R系列の歴史的関係・原裁定照合は未検証。継続申告を正式処分にしない。 |
| CLD4-01 | Claude L35／70 | 部分解消・残余をCLD5-01に統合との申告 | 条件句等の局所文言は確認。統合・正式Closeを本工程で採用しない。 |
| CLD4-02 | Claude L35 | Rev.2追加2段落で解消との申告 | L121／409追加の文面は確認。旧原文全条件の充足・正式Closeは未検証。 |
| CLD4-03 | Claude L100 | Minor、CSVなし・評価対象外 | CSVは今回の14正本に含まれない。今回パケットから修復を推定しない。 |
| CLD4-04 | Claude L101 | Editorial、継続管理する既知指摘 | 現ヘッダのID・Integration basis・自己言及を確認。固定原本は無断修正しない。 |
| CLD2-01／02／03／05、CLD-05 | Claude L102 | 変更されておらず継続との申告。個別Severityは当該行に未記載 | CC-01／03／08、Invariants、Gate未到達規則との関連を記録。旧原報告未取得で正式再判定しない。 |
| CV06-F01〜F04 | Grok L74、DR L31〜34 | ドラフト上対処との申告。正式Closeではない | 元CROSSは局所観測（F01〜04 Minor/REVISE）。DRはADDRESSED IN DRAFT。歴史的4AI Findingと統合しない。 |

CV06-F05はDRの再現証拠対応として参照される局所観測で、新規15件へ追加しない。旧32／旧8の全原文・全IDは固定パケットだけでは補完できない。指摘が原報告で省略されていることを「解消済み」にしない。

**本表の終了状態：15原ID追跡、A/B分離、暫定論点対応を完了。正式採否・統合・Close・Severity変更・Owner裁定は未実施。**

