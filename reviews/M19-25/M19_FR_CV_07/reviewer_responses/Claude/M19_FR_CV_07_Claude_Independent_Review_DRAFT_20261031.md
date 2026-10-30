# SPE M19-FR-CV-07｜独立レビュー回答(Claude)— 原文保全用 DRAFT

本回答は、受領検証結果(A)と独立レビュー本文(B)、最終状態(C)を一つの連続した文書として提出する。Review Acceptance、Finding の Close、正式承認、Freeze、HOLD 解除のいずれでもない。

## A. 受領検証結果

- Reviewer:Claude(Anthropic、モデル識別子 claude-sonnet-5-5。実際に応答したモデルは別でありうる)
- 実施日時(自己申告):2026-10-31 07:00〜07:10 JST ごろ
- Repository:`spe-flatvat/SPE`
- 固定 Commit:`e195b9ecdc0e6930f44fce2b598e2c60887c92e4`(`git rev-parse` で完全一致を確認。ブランチ最新への置換なし)
- 配布ディレクトリ:`reviews/M19-25/M19_FR_CV_07/`(`reviewer_responses/` は固定 commit のこのディレクトリに存在せず、開いていない)
- Manifest:`CV07_Distribution_Manifest_Rev4a_DRAFT_20261031.md`(自身の SHA-256:`d9ff1a55c0eb14058bba0938b0f34281e6f5853cf3fb480cf03a1c352b63677d`。Manifest の規定どおり、自己ハッシュは Manifest に含まれず、発出記録との照合用に記録する)
- 取得ファイル数・読取結果:配布ディレクトリ内14ファイル(Manifest 1 + payload 13)。Manifest 記載の13件の存在と相対パス、件数(13)が一致。14件すべてを読了した(Rev.2 全文と source 全文は、変更箇所と条項横断を重点に通読)。
- SHA-256 照合:Manifest の13件すべてについて、取得した実バイト列から `sha256sum -c` で照合し、**13/13 一致**。Git blob ID・GitHub 画面・他者の検証報告は使っていない。
- 追加の独立再現:
  1. source(`4a1f70e0…`)に正本パッチを適用すると、Rev.2(`94286b1e…`)とバイト一致。パッチは3 hunk。
  2. source の Git blob SHA-1 を再計算し、`b254ac77…` と一致(ただし、これは SHA-256 の代わりではない)。
  3. source と Rev.2 の先頭52行(ヘッダ)は同一。ヘッダは変更されていない。
  4. バイト数:source 39,815、Rev.2 42,852、パッチ 5,745 は、レシート記載値と一致。
- **受領判定:PASS**
- 未検証事項と検証経路:
  - 経路:`add_repo`(読み取り)後に `git fetch --depth=1 <固定SHA>` と `git archive`。WebFetch・curl は使っていない。
  - Owner 応答原文(CV05-N01〜N03)は、レシートに転記された「帰属付きの転記」であり、原会話の真正性は検証できない(Common Review Request の指示どおり)。
  - 固定 commit `a00c9625…`、`0e3860e6…` は、本受領の対象外であり取得していない。source は配布ディレクトリ内の `references/` のコピーで検証した。
  - Manifest と Request の旧記述(「NOT DISTRIBUTED」「NO REVIEW START」等)は、本発出指示書により上書きされるものとして扱った。

## B. 独立レビュー結果

### B-1. 総合結論

**REVISE(軽微修正)。** 適用範囲は、Rev.2 全文候補 `94286b1e…` に対する静的・文面上のレビューに限る。ACCEPT でも正式承認でもなく、動的 V&V、29 Invariants の実行、数値モデルの検証は行っていない。

要点:
- Rev.2 は、CV05-N01=A(Decision 省略を現時点で許可しない)、N02=B(外部要件参照の限定)、N03=A(2026年の初期状態検証と切替認可の分離)を、実質的に反映している。新規のMajor、およびfail-openになる確定的な条項衝突は見つからなかった。
- 前回(私の正式レビュー)の CLD4-02(CC-12 の Decision 証拠が無条件のまま、CC-04 と不整合)は、Rev.2 の追加2段落で解消した。CLD4-01(L152 の条件句の循環)は部分的に解消し、残余は CLD5-01 に統合した。
- 残る指摘は、Decision 要件の表現が3通りに分かれていること、N03 の適用範囲の曖昧さ、N03=A の定義との差、新設義務の Gate・監査への未接続、packet の追跡性、レシートの表記である。
- 前回の CLD3-01(Major、ヘッダの「R-01–07」)は、ヘッダが無変更のため未解消のまま。

### B-2. 必須質問への回答

1. **Q1 P-01〜P-04 は N01=A、N02=B、N03=A を正確に実装しているか。** 権限の拡大(規範採用、切替、歴史的承認の認定)は見られない。ただし次の2点は完全ではない。(a) N02=B は、Rev.1 の修文案では句の置換だったが、Rev.2 は `other applicable approved requirements` を残したまま検証義務を追記する形で実現している(実質は限定、文言は未置換)。(b) N03=A の定義が列挙する「生成者」を、Rev.2 は意図的に外している(CLD5-03)。
2. **Q2 CC-03 は裁量型の `met/approved` を維持し、現時点で Decision なしの非裁量型の経路を避けているか。将来の別契約は現時点の免除ではないと明確か。** はい。L121(P-01)が「Decision-free pathway is not authorized」と明記し、将来の経路は別の Owner 承認と CC-03/05/12 の整合を要するとしている。L119 の「Non-discretionary switch types require separately approved contracts」自体は無変更で、単独で読むと「別契約があれば足りる」と受け取れる。L121 との相互参照が無い点は Editorial(CLD5-01 に含める)。
3. **Q3 CC-04 は外部の承認済み要件、不変 ID/版、証拠、(明示承認された場合のみの)優先関係、Decision の適用性を特定できるか。承認や階層を創作していないか。** 概ね。L154 は、不変の権威ある参照(contract ID/version または artifact/digest)、承認証拠、適用性の検証を要求し、優先関係は「expressly approved rule」がある場合に限り、推定を禁止している。契約階層も作っていない。残余:Decision の要否が L154 では「where required by those contracts or other applicable approved requirements」のままで、L121・L407・L409 の無条件の表現と二重になっている(CLD5-01)。
4. **Q4 2026年の初期状態検証・独立に正当な incumbent 計算と、2026年の切替候補の生成・使用・予約・効力発生は区別されているか。** はい。L156 が明確に分離し、独立に正当な2026年の初期化と incumbent 計算を止めず、架空の2025年状態も禁止している。ただし L156 の第2文は適用範囲が曖昧(CLD5-02)で、N03=A が列挙する要素のうち「生成者」が外されている(CLD5-03)。
5. **Q5 CC-12 は Trigger/Decision 証拠と予約のライフサイクル、競合、Gate 検証を、意図しない例外なしに維持しているか。** はい。L407 は無変更で、L409 が「No Decision-free reservation pathway is currently approved」「非裁量型の label、未特定の外部要件、2026ベースライン検証は免除にならない」と明記した。予約・失効・復活禁止の既存条項に影響はない。
6. **Q6 CC-03/04/05/09/11/12 と Gate A→C→B は整合しているか。失敗の依存範囲と監査可能性は。** 順序と依存範囲は整合している。fail-closed は、いずれも依存する切替に限定され、incumbent 計算は止めない。ただし、新設した検証義務(L154、L156、L409)が、CC-05 の Gate B の列挙(L215)にも、CC-09 の Transition Decision Record(L315)にも接続されておらず、理由コードの例もない(CLD5-04)。
7. **Q7 CC-01/02/06/07/08/10/13、理由分類、29 Invariants、既存 Finding との衝突はあるか。** 直接の衝突は見つからなかった。CC-06 の2026年の再基準化(前回の収束候補で修正済み)は、L156 と矛盾しない。Invariants は無変更で、新設した3つの境界(Decision 省略の禁止、2026年の認可分離、外部要件の不変参照検証)を直接カバーするものがない(CLD5-06)。意図しない意味論の変更は見つからなかった。
8. **Q8 source→patch→Rev.2 の再現性はレシートで支持されるか。** はい。私の独立再現は A のとおり3点とも一致した。ただしレシートは、これらを局所の静的検査として扱っており、レビュー・承認・動的 V&V と混同してはならない。レシート §4 の「29 invariants: PASS」は、実行していないのに PASS と表示しており、表記が誤解を招く(CLD5-06)。
9. **Q9 歴史的 Owner 裁定、DecisionLog 照合、E-1/E-2、原32件 OPEN、新8件の未裁定、CLD3-01 は、未了として明確に維持されているか。** 個別レシートと統合記録は、これらを維持している。ただし、packet に「新8件」の ID の一覧が無く、私は特定できない(NOT VERIFIED)。CLD3-01 は、ヘッダ無変更のため実質的に未解消。
10. **Q10 判定。** REVISE(軽微修正)。ACCEPT は正式承認・Freeze を意味しない。

### B-3. Finding 一覧

ID は、既存の ID と衝突しないよう `CLD5-xx` を用いる。行番号は Rev.2 全文(`94286b1e…`)基準。

| ID | Severity | 対象箇所 | 概要 | Confidence |
|---|---|---|---|---|
| CLD5-01 | Minor | L154、L156、L121、L407、L409 | Decision 要件の表現が二重 | 高 |
| CLD5-02 | Minor | L156 第2文 | 適用範囲が2026年に限定されていない | 中 |
| CLD5-03 | Minor(Owner 確認要) | L156 末文、N03 レシート §2 | N03=A の定義との差(生成者) | 中 |
| CLD5-04 | Minor | L154、L156、L409 と L215、L315、L278 | 新設義務が Gate・監査・理由コードに未接続 | 中 |
| CLD5-05 | Minor | packet(`e750f613…`、`ddb86d69…`、`9b6ed7f5…`) | Rev.2 の逐文トレーサビリティが無い | 高 |
| CLD5-06 | Editorial | 厳密差分レシート §4、L471 以降 | 「29 invariants: PASS」の表記と Invariants の未更新 | 高 |

**CLD5-01|Decision 要件の表現が、無条件と条件付きで二重になっている(Minor)**
- 対象:L154「…and, where required by those contracts or other applicable approved requirements, attributable Decisions…」。L156「…together with the Decision, reservation, numerical-contract, and Gate validations required by the approved contracts」。一方、L121「A Decision-free pathway is not authorized」、L407・L409 は無条件。
- 根拠:CV05-N01=A は、現時点で Decision 省略を許さない。L154・L156 は、Decision の要否を外部契約に委ねるように読める条件付きの表現を残している。L154 は「MUST NOT infer … Decision waiver」を併記するため、衝突は避けられるが、特則と一般則の優先関係が明文化されていない。
- 影響:将来の別契約が Decision 不要と主張した場合に、読み方が割れうる。fail-open の確定ではない。
- 修正案:L154 と L156 の Decision 部分を「the Decision evidence required by CC-03, CC-05 and CC-12」に揃える。L119 に「see the Prospective Decision-omission boundary below」の相互参照を足す(Editorial)。
- 前回の CLD4-01 との関係:(a) 未承認の本契約を指せない循環は、各要件に承認証拠を要求する L154 で解消。(b) Decision なしの2026候補は、L121・L409 で解消。(c) 構文の曖昧さが残る。

**CLD5-02|L156 第2文の適用範囲(Minor)**
- 引用:「Each dependent transition operation MUST have an attributable separately approved authorization basis covering its applicable creation/use …」
- 第1文は2026年に限定されているが、第2文は「Each dependent transition operation」で、文面上は2027年以降の切替も含む。2027年以降は、CC-03 の4条件と CC-12 が既に規律しており、「別途承認された認可根拠」を一律に求めると新しい要件になる。
- 修正案:「Each dependent operation on a transition candidate targeting 2026 …」。

**CLD5-03|N03=A の定義との差(Minor、Owner 確認が必要)**
- 事実:N03 レシート §2 は、案Aの内容として、対象施策・**生成者**・適用年・Decision要否・予約条件・数値契約・Gate条件の特定を挙げる。Rev.2 L156 は、「creator-identity approval schema を新設しない」と明記し、生成者を外した。
- 根拠:CV-06 横断検証の F03 は「creator は N03 に明示されていない」としたが、N03 レシート §2 と基準パケット §5 に生成者が明示されており、前提が成り立たない。ただし、Owner の原発言は「案Aを採用します」だけで、A の定義は受領レシートとパケットに依存する(receipt レベルの証拠)。
- 付記:「Decision要否」は、N01(Decision 省略を許さない)と緊張する。統合記録 §3 が N01 を優先するとしており、Rev.2 もそうしている。この解決の経緯をトレーサビリティに残すとよい。
- 影響:2026年の切替候補の fail-closed の条件が、Owner 裁定の定義より狭くなる。現時点で2026候補の経路は存在しないため、実害は限定的。
- 修正案:生成・使用の根拠が「誰または何が」承認したかを含むと明記するか、Owner が「生成者は creation/use の根拠に包含される」と確認し、記録する。

**CLD5-04|新設した検証義務が Gate・監査・理由コードに未接続(Minor)**
- L154(不変参照の検証)、L156(認可根拠)、L409(認可確認の結果の保持)は、いずれも新しい検証義務を課すが、CC-05 の Gate B の列挙(L215)に含まれず、CC-09 の Transition Decision Record(L315)に項目がなく、CC-07 の理由コード(L278 の要請)にも対応がない。L409 は「no new audit schema is approved」とする一方で、証拠参照の保持を MUST としている。
- 影響:どの Gate で検証し、どこに記録し、どの理由で止めるかが実装者の裁量になる。
- 修正案:「verified at Gate B and recorded in the Transition Decision Record (CC-09)」の一文と、理由コードの例の追加(正規の列挙は別契約でよい)。

**CLD5-05|Rev.2 の逐文トレーサビリティが無い(Minor、packet)**
- Amendment and Traceability(`e750f613…`)と Cross Validation Report(`ddb86d69…`)は、Rev.1 の P-01〜P-04 を引用している。Rev.2 の実文と異なる(例:Rev.1 の P-02 は句を置換する案、Rev.2 は句を残して追記)。Rev.2 の厳密差分レシートは、CV06-F01〜F05 への対応のみで、Rev.2 の各文と N01〜N03 の対応表が無い。Request の Q1 の「P-01..P-04」は、2つの版の文言が存在する。
- 修正案:Rev.2 基準の対応表(文 → 裁定 → 根拠 → 限界)を追加するか、Rev.1 の2文書に「superseded」と明記する。

**CLD5-06|レシートの表記と Invariants(Editorial)**
- 厳密差分レシート §4 は「29 invariants: PASS」とするが、§5 で未実行と述べている。テキスト存在の確認なので「UNCHANGED／NOT EXECUTED」と表記するのが適切。
- Invariants(L471〜)は無変更で、Invariant 6 は裁量型の切替に限られ、Decision 省略の禁止、2026年の認可の分離、不変参照の検証を直接カバーしない(前回の CLD2-05 の類型)。将来の V&V 義務として追加を検討。

### B-4. 継続管理する既知の指摘(重複計上しない)

- **CLD3-01(Major、OPEN):** ヘッダ L14 の「R-01–07」。Rev.2 のヘッダは source と同一で、未解消。
- **CLD4-03(Minor):** 32件処分案CSVの行番号引用の更新。CSV は今回の packet に含まれない。評価対象外。
- **CLD4-04(Editorial):** Document ID `M19-CC-v0.4-DRAFT` が、バイト列の異なる複数版(`4a3b475a…`、`dc8d22dd…`、`4a1f70e0…`、`94286b1e…`)で共通。Integration basis(L5)は CV05 の裁定に触れていない。L7「has not been independently re-reviewed」は古い自己言及。
- **CLD2-01、02、03、05 系**(L105 の `no switch;`、CC-08 の主体名称、CC-01 の `select only`、Invariants の網羅性)は、変更されておらず継続。CLD-05(Gate A/C 失敗時の NOT_EVALUATED の明示)も継続。
- 原32件の OPEN、新8件の未裁定は、変更しない。

### B-5. 条項間整合性と Owner 裁定トレーサビリティ

- N01→L121・L409、N02→L154、N03→L156 の対応は成立。N01 と N03 の定義の緊張(Decision要否)は、統合記録 §3 の解決(N01 優先)に沿って Rev.2 が処理している。
- 裁定の効力は将来の方針にとどまり、歴史的な承認(D25、O、GATE、COMP、R、6D 系)の遡及的な証明ではない。この区別は packet 全体で保たれている。
- Gate A→C→B の順序、依存範囲(`stop_branch`)、incumbent の継続性、新たな優先関係・権限の不創設は、維持されている。

### B-6. 証拠不足・未実施検証

- Owner 応答原文の真正性(原会話との照合)。
- 歴史的 Owner 裁定、E-1(非裁量型の別途承認契約の所在)、E-2(2026候補の生成・使用・予約の権限)。未発見は不存在の証明ではない。
- 新8件の Finding の ID と内容。32件処分案の再評価(packet に含まれない)。
- 動的検証:29 Invariants、エンジン実行、数値モデル、M10/M14/M17/M18 の意味論の不変性。
- 固定 commit `a00c9625…` および `0e3860e6…` の実取得(今回の対象外)。

### B-7. 未解決事項と HOLD 条件

- Owner 判断が要る事項:(1) CLD5-03 の「生成者」を Rev.2 のままとするか。(2) CLD3-01 の R 系列 ID の関係の確認。(3) CLD5-01 の Decision 要件の表現を一本化するか。
- 最小修正は、CLD5-01/02/04 の文言修正、CLD5-05 の対応表、CLD5-06 の表記修正。いずれも Owner 承認後の別工程。
- M19〜M25、RP-023 の HOLD は継続。

## C. 最終状態

- 受領検証:完了(PASS、13/13)
- 独立レビュー:完了(静的・文面上のレビューに限る。結論は REVISE(軽微修正))
- GitHub への書込:なし
- Finding の裁定、正式承認、Freeze:なし
- M19〜M25 の HOLD:継続
- 他AIの回答は参照していない(`reviewer_responses/` は開いていない)。
