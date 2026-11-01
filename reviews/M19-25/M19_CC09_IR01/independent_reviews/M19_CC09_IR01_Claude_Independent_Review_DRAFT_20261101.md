# SPE M19-CC09-IR-01｜独立レビュー回答(Claude)— 原文保全用 DRAFT

CC-09削除および直接派生監査義務の限定レビューへの回答。正式承認、Finding の Close、Owner 裁定、Freeze、HOLD 解除のいずれでもない。

## A. 受領・取得の記録

- Reviewer:Claude(Anthropic、設定モデル識別子 claude-sonnet-5-5。実際の応答モデルは別でありうる)
- 実施日時(自己申告):2026-11-01 20:22 JST 開始
- Repository:`spe-flatvat/SPE`
- 固定 Commit(IR-01 の指定):
  - 主レビュー資料 `c96e48d1…`:`reviews/M19-25/M19_CC09_IR01/` の4文書を取得。
  - 比較基準 `754c1e29…`:Rev.2(`94286b1e…`)を主、2026-10-30 候補(`4a1f70e0…`)を補助として取得。`docs/Workflow.md` も同 commit から取得した。
  - 既存レビュー結果の参照 `857633d4…`:commit の取得とパス一覧の確認のみ。他AIの回答ファイルは開いていない。
- 取得経路:`add_repo`(読み取り)後の `git fetch --depth=1 <固定SHA>`。WebFetch・curl は使っていない。
- SHA-256(自分で計算した実バイト):
  - Development Continuity Decision Basis:`7c85a682…`
  - Review Packet v0.3:`6a5c8943…`
  - Direct Audit Obligations and Deletion Diff v0.2:`b19e51d5…`
  - Pre-Distribution Artifact Register v0.3:`35bce9d5…`
  - 比較基準:Rev.2 `94286b1e…`、10-30 候補 `4a1f70e0…`
- 照合:Artifact Register が列挙する3件の SHA-256 は、実バイトと一致した(Register 自身の SHA-256 は記載がなく、照合対象外)。IR-01 には Manifest と期待値の一覧がないため、これ以上の照合はできない。
- 例外・不一致:
  1. Review Packet v0.3 §2 は、差分根拠の SHA-256 を `0ad78fc0…`(旧版)としている。今回の4文書にある v0.2 差分は `b19e51d5…` で、Packet の記載と異なる。旧版は今回の入力に含まれず、確認できない。
  2. Packet v0.3 は、基準版が未指定であることを先決条件としているが、IR-01 の指定(Rev.2 を主基準)がこれを解消している。
- 独立性:今回の他AIの回答は参照していない。旧工程の終了条件、Finding 処理、歴史的証拠回収義務は承継していない(IR-01 の指定どおり)。自分の先行レビューと、当時入手した資料は参照した。
- 評価の姿勢:Development Continuity Decision Basis は、保存された会話記録で、Owner 裁定でも規範でもない(同文書と Packet §2A の明記どおり)。その記載内容(CC-09 削除を第一案とする推奨、Owner の意向表明)は入力としていない。評価は条項の内容のみに基づく。

## B. 独立レビュー結果

### B-1. 総合結論

**REVISE**(修正のうえで再提出を求める。REJECT ではない)。

適用範囲:IR-01 の4文書が提案する D-01〜D-08 の削除・置換案と、直接派生する監査義務の識別。比較基準は Rev.2(`94286b1e…`)。静的・文面上のレビューであり、動的 V&V は行っていない。

要旨:
- **方向は支持できる。** 無期限の歴史的裁定の再認証を生む部分(CC-09 の Governance traceability、Freeze 前の全件照合、回収不能な二次証拠の別裁定)を契約から外すことは、実行制御の安全性を損なわずに可能である。実行・比較・予約の「業務記録」と、「歴史的証跡の再認証」を分ける提案の考え方は妥当である。
- **ただし、現行の差分案のままでは目的を達成できない。** (1) 差分案が Rev.2 ではなく旧候補(2026-10-28 の統合版)を基礎にしており、Rev.2 に新設された証拠検証の条項が手つかずで残る。(2) Freeze 境界の残存文が明確に処理されていない。(3) 年度末の権限・実行者の識別という安全要件が、差分案の中で矛盾している。この3点は Major とした。
- 削除そのものによる、直接の条項衝突(参照切れを除く)は見つからなかった。

### B-2. Finding 一覧

ID は `CC09IR-CLD-xx`。行番号は Rev.2(`94286b1e…`)基準。

| ID | Severity | 対象質問 | 概要 | Confidence |
|---|---|---|---|---|
| CC09IR-CLD-01 | Major | Q1、Q5 | 差分案の基礎が Rev.2 でなく、Rev.2 の証拠検証条項が残る | 高 |
| CC09IR-CLD-02 | Major | Q1、Q3 | Freeze 境界の残存文(L521〜L527)が未処理で、同じループが残る。D-06 は適用できない形式 | 高 |
| CC09IR-CLD-03 | Major | Q2 | 年度末の実行者・権限の識別が、R04 と D-05 で矛盾し、Invariant 24 とも不整合 | 高 |
| CC09IR-CLD-04 | Minor | Q2 | 維持とされた安全要件の明文化が不足(append-only、原回答の保全、別承認の境界) | 高 |
| CC09IR-CLD-05 | Minor | Q3、Q5 | 残存する audit 語と不整合(L204、L227、L451、Invariant 14、HOLD の記載項目、評価契約の版) | 高 |
| CC09IR-CLD-06 | Minor | Q3、Q4 | 暫定レシートの接続不足(Rev.2 の「承認証拠」条項への接続、DecisionLog との関係) | 中〜高 |
| CC09IR-CLD-07 | Minor | Q4 | 暫定レシートの必須項目:`target_ref` の条件、原文の引用、発行者 | 中 |
| CC09IR-CLD-08 | Minor | Q2、Q7 | 保護対象の明示、IR-01 の「承継しない」の範囲、既存 Finding の取り扱い | 中 |
| CC09IR-CLD-09 | Editorial | Q5 | CC-09 の欠番表示、Packet の旧版 SHA の記載 | 高 |

#### CC09IR-CLD-01|差分案の基礎が Rev.2 でない(Major)

- 出典:Diff v0.2 の冒頭(「参照Commit 857633d4…、…M19_Control_Contract_Integrated_Candidate_DRAFT.md(Git blob 09b8d58e…)」「この参照版は…正式な配布固定版ではない」)、Packet v0.3 §1・§2。Rev.2 L121、L154、L156、L409。
- 事実:差分案は 2026-10-28 の統合候補に対して作られた。Rev.2 は、その後の CV05 の裁定の反映として、次の条項を持つ。L121(Decision なしの経路の非認可)、L154(「relied-upon authorization or requirement」ごとに、不変の権威ある参照、承認証拠、適用性を検証)、L156(2026年の切替の認可根拠)、L409(認可確認の結果と証拠参照の保持)。差分案の R 表(R01〜R18)も D-01〜D-08 も、これらを扱っていない。なお、差分案が引用する削除側の文は、私の確認では Rev.2 にも逐語で存在する(§0 の予約の定義の1文を除き、ここでは確認の対象外とした)。
- 機序:L154・L156・L409 は、実行時に「承認証拠」「権威ある参照」の検証を要求する。CC-09 を削除しても、これらが残る限り、「承認証拠のための証拠」の要求は契約内で再発しうる。差分案の R18(「レシート ID 等で権限を参照。参照元の原チャット再取得を要求しない」)は、これらの条項に接続されていない。
- 影響:Q1(追加証跡の無限照合を防げるか)に対して、現行の差分案は「防げない」。
- 最小修正案:基準版を Rev.2 に固定し、差分を再生成する。L121・L154・L156・L409 に対して、「暫定レシート(D-07)が、承認証拠および権限の根拠として十分」と接続する(CC09IR-CLD-06 を参照)。
- Owner 判断要否:不要(IR-01 が基準を指定済み)。作業の再実施のみ。
- 証拠制限:Rev.2 に対する逐条の再適用は行っていない(提案の評価であり、適用ではない)。

#### CC09IR-CLD-02|Freeze 境界の残存文と、D-06 の形式(Major)

- 出典:Rev.2 L519〜L527(Freeze boundary)。Diff D-06(削除側が「[全過去Owner裁定・4AI原文・Finding・DecisionLogの一律完全照合をFreeze要件とする部分]」というプレースホルダ)、R15(「置換／要Owner判断」)。
- 事実:CC-09 を削除しても、Freeze 境界に次の文が残る。L521「Review findings and dispositions MUST be individually traceable.」、L523「Original decisions and reviewer responses MUST remain distinguishable…」、L525「Acceptance of irretrievable secondary evidence for Freeze requires separate Owner adjudication.」、L527「Applicable review consensus or documented waiver, explicit Owner final resolution, and DecisionLog correspondence are prerequisites to formal Freeze.」。D-06 はどの文を削除・維持するかを示さず、プレースホルダを含むため、適用できない。
- 機序:L525 は「回収不能な二次証拠」を Freeze のたびに個別裁定の対象とし、L527 は DecisionLog との対応を前提とする。CC-09 の削除後も、これらがFreeze時に「証拠のための証拠」を再要求する経路になる。
- 影響:Q1・Q3 の目的に反する。ただし、L527 のうち「Owner の最終裁定」と「レビューの合意または waiver」は、`docs/Workflow.md` §4・§5 とも対応する正当な前提であり、全削除は適切でない。
- 最小修正案:文ごとに処置を明示する。例:L521〜L525 を削除(または「未検証は未検証として表示すれば足りる」に置換)。L527 は、「レビューの合意または Owner の最終裁定」と「Owner の最終裁定の DecisionLog への記録」に限定する(歴史的な裁定との照合は求めない)。L529(静的検証は再レビューの代わりにならない)、L531、L533(別承認の境界)は維持。
- Owner 判断要否:要(L527 の DecisionLog 対応の扱いは、Workflow §2 と関係するため。CC09IR-CLD-06 を参照)。
- 証拠制限:Workflow.md が Freeze に何を要求するかは、同文書の範囲で確認した(§2、§4、§5)。

#### CC09IR-CLD-03|年度末の実行者・権限の識別(Major)

- 出典:Rev.2 L182(CC-04:「The formal year-end operation MUST identify its authorized actor, authority, prerequisites, annual disposition, and applicable reservation-resolution evidence.」)、L190〜L192(失敗・停止の解決は「expressly authorized」な過程に限る)、Invariant 24(「Formal year-end requires authorized actor, prerequisites, atomicity, and idempotence」)。Diff R04(「年度処理の結果・再試行ID・完了状態の業務記録のみ」)、D-05(再試行の1文のみを置換)。
- 事実:R04 は、年度末の「actor/authority/prerequisites」を直接監査要求として列挙し、業務記録を「結果・再試行 ID・完了状態」に限る方向を示す。D-05 の差分は L170 の再試行文しか置換せず、L182 を変えない。R04 と D-05 が食い違う。R04 を文字どおり適用すると、L182 の識別義務が消え、Invariant 24 の「authorized actor」の根拠も失われる。
- 機序:異常年度末(6D38-01 の系統)の解決は「expressly authorized」であることを要する。誰が、どの権限で閉じたかを識別できなければ、「authorized」を判定する手がかりがなくなる。これは歴史的裁定の再認証ではなく、実行時の権限の識別であり、有限である。
- 影響:無権限の年度末確定や、失敗年度の黙示の成功扱いを、記録上区別できなくなる。
- 最小修正案:L182 を維持する(または「年度末操作の実行者と、根拠となる Owner 裁定レシート ID を記録する」に置換)。R04 の記述を D-05 に合わせる。Invariant 24 を維持する。
- Owner 判断要否:不要(文言の整合)。
- 証拠制限:なし(文面のみ)。

#### CC09IR-CLD-04|維持とされた安全要件の明文化(Minor)

- 出典:Diff 09-03、09-04、09-10、R01、R10、D-05。Rev.2 L31、L86、L411、L417、L321〜L325、L343〜L345、L537。
- 事実:(a)「予約の append-only」は、§0(L31)、CC-12(L411「append-only `scheduled` event」、L417「linked append-only events」)に現れる。D-05 は §0 の表現を「recorded lifecycle-resolution events」に置換し(append-only が消える)、R01・R10 は「置換」とだけ書く。CC-12 の2文が維持されるのか、不明確である。予約の現在の有効性は、順序付きの解決イベントから再構成する(L86)ため、追記専用の性質に依存する。(b) 09-10 は「一部維持(原文の黙示的改変禁止、書込承認境界)」とするが、維持先の条項と文言が示されない。L343(原回答は正規化せずに保存)と L345(DecisionLog 更新、リポジトリ書込、Finding の closure、Freeze は別承認)は、CC-09 内の文である。L345 と同趣旨の文は L537(Freeze 境界)に残るが、CC09IR-CLD-02 の処置次第で変わる。(c) 09-04 の「予約 ID の再利用禁止」は CC-12 に重複して存在する(L411 の一意性、L417)。
- 影響:誤って安全要件が落ちる、または残ったかどうかの判断が人により割れる。
- 最小修正案:「維持」とした項目ごとに、維持先の条項と文言を差分に明記する。予約のイベントは追記専用であることを、CC-12 に残す。
- Owner 判断要否:不要。

#### CC09IR-CLD-05|残存する audit 語と不整合(Minor)

- 出典:Rev.2 L204、L227、L451、L486(Invariant 14)、L499(Invariant 27)、L447。Diff R14(「Invariants 20、24、26、27」)、D-04。
- 事実:
  - 差分案が扱っていない箇所:L204(「preserving observable sequencing, audit, and historical immutability」)、L227(「These classifications are audit attributes」)、L451(「separately audited Control Action」)、Invariant 14(「separately audited Control Action」)。R14 は Invariant 14 を挙げていない。
  - D-04 の CC-08 側の書き換え(HOLD_COMPARISON 発出時は「target, reason, related Comparison state」を記録)は、CC-13 L447(「comparison target, reason, related Comparison state, comparison-contract ID, and applicable result reference」)より狭い。D-04 が CC-13 のこの文を変えないなら、2条項の記載項目が食い違う。
  - CC-09 の Transition Decision Record にある「Trigger observations and evaluation-contract version」を求める条項は、CC-09 以外にない。CC-11(L388)は、真偽・評価実施・観測契約の有効性の記録を求めるが、評価に用いた契約の版は求めない。削除後は、再現に必要な評価ルールの版が記録されない。
- 最小修正案:該当箇所を R 表に追加し、語を「recorded／operational result」に揃える。HOLD の記載項目は CC-08 と CC-13 で一致させる(CC-13 の項目を採る)。CC-11 に「適用した評価契約の参照」を1項目だけ追加する(有限)。
- Owner 判断要否:不要。

#### CC09IR-CLD-06|暫定レシートの接続不足(Minor)

- 出典:Diff D-07・D-08、R03、R18。Rev.2 L117、L121、L154、L156、L409。`docs/Workflow.md` §2(「All governance-level resolutions must be recorded in DecisionLog.md.」)、§5.6(Logging)。DecisionLog(DL-010)。
- 事実:(a) D-07 の「レシートは裁定記録として十分」という規定は、Rev.2 が「attributable approval evidence」を要求する箇所(L154、L156、L409、L117)に接続されていない(CC09IR-CLD-01 を参照)。(b) D-07 は暫定レシートと DecisionLog の関係を述べていない。Workflow §2 は、ガバナンスレベルの裁定を DecisionLog に記録することを求める。CC-09 の削除自体もそれに当たりうる。暫定レシートは「暫定的な運用記録」であって、DecisionLog への記録を代替しない、と明記しなければ、2つの規範が衝突しうる。
- 最小修正案:D-07 に「レシートは L117・L121・L154・L156・L409 の承認証拠として十分」と書く。「ガバナンスレベルの裁定を DecisionLog に記録するか、免除するかは、Workflow.md に従い Owner が決める」と書く。
- Owner 判断要否:要(DecisionLog への記録の扱い)。

#### CC09IR-CLD-07|暫定レシートの必須項目(Minor)

- 出典:Diff D-07(必須7項目)、Packet §5。
- 評価:7項目(`decision_id`、`subject`、`decision_result`、`authority`、`decided_at`、`receipt_issued_at`、`receipt_status`)は、日時の扱い(推定しない、精度を明示、独立認証は求めない)を含め、最小限の方針として妥当である。次の3点を提案する。
  1. `target_ref` は、「版の特定に不可欠な場合のみ」ではなく、裁定の対象が版のある成果物である場合は必須とする。M19 の裁定はほぼすべてが版のある候補・パケットに対するものであり、版が特定されない「案Aを採用」は意味が不定になる。
  2. `decision_result` が起票者の要約になることを避けるため、Owner の発言の原文(逐語)を1項目として持つ(任意でなく推奨以上)。
  3. 発行者(`issuer`)。レシートは AI が起票することが多く、「発行されたレシートを受容する」十分性規定は、起票の誤りを検出する手段を持たない。発行者の記録と、Owner がレシートを確認した旨で足りる。
- 最小の代案:上記は「3項目の追加・条件変更」で、独立タイムスタンプ認証や原本回収を求めるものではない。
- Owner 判断要否:要(項目の採否)。

#### CC09IR-CLD-08|保護対象の明示、「承継しない」の範囲、既存 Finding(Minor)

- 出典:IR-01「4. 独立性・権限境界」、Packet §4(維持すべき動作安全性)。CV05 の裁定に由来する Rev.2 の条項(L121、L154、L156、L409)。
- 事実:(a) Packet §4 の保護リストは、Gate の順序、Trigger/Decision の区別、予約、年度末、比較を挙げるが、CV05 由来の安全条項(Decision なしの経路の非認可、2026年の切替の認可の分離、承認済み契約の検証と fail-closed)を明示していない。IR-01 は「旧工程の終了条件、Finding 処理、歴史的証拠回収義務を承継しない」とする。これらの安全条項は終了条件でも回収義務でもなく、実行時の制御であるため、承継の対象外にならないはずだが、明示がなければ誤読されうる。(b) CC-09 の削除により、CC-09 を前提とする既存の OPEN Finding(私の CLD5-04、CLD2 系など)の一部は、前提が消える。Continuity Basis は、これらの再評価を示唆する。自動的に消滅・Close となるのではなく、対応表が要る。
- 最小修正案:保護対象のリストに CV05 由来の安全条項を加える。削除の影響を受ける既存 Finding の対応表(影響なし／前提が消滅／再評価が要る)を、後続の作業とする。いずれも Close は Owner 裁定による。
- Owner 判断要否:対応表の作成の可否は要。

#### CC09IR-CLD-09|欠番表示と記載の食い違い(Editorial)

- CC-09 の欠番を「Reserved / Deleted」の欠番表示にするか、番号を詰めるかは、Owner 裁定事項と差分が述べる。他の文書とレビュー記録は CC-09 を参照するため、欠番表示(番号を詰めない)を推奨する。
- Packet v0.3 §2 の差分根拠の SHA-256(`0ad78fc0…`)は旧版を指す。今回の v0.2(`b19e51d5…`)に更新する。

### B-3. 質問への回答(Packet §6 の Q1〜Q7)

1. **Q1 CC-09 全節削除と D-02〜D-08 で、追加証跡の無限照合を防げるか。** 現行の案では防げない。残存する抜け道:(a) Rev.2 L154・L156・L409 の承認証拠・権威ある参照の検証(CC09IR-CLD-01)。(b) Freeze 境界 L525・L527(CC09IR-CLD-02)。(c) 暫定レシートの十分性が各条項に接続されていないこと(CC09IR-CLD-06)。これらを直せば、無限照合の経路は塞げると判断する。
2. **Q2 動作安全性の必須条件を誤って削除していないか。** 年度末の実行者・権限の識別が危うい(CC09IR-CLD-03)。そのほかは、維持の明文化が不足する(CC09IR-CLD-04)。Gate の順序、fail-closed、Trigger/Decision の区別、予約の一意性、確定結果の非遡及性、比較契約の版参照・再検証は、削除対象ではなく維持されている(R06、R09、R17 など)。
3. **Q3 Invariant 17、Freeze 関連、CC-01/05/08/13、§0、CC-03/04/10/12、Reason taxonomy の直接依存。** CC09IR-CLD-02(Freeze)、-03(CC-04)、-05(残存語と不整合)を参照。Invariant 17 の置換案(D-06)は方向として妥当である。
4. **Q4 暫定レシートの7必須項目は必要十分か。** 日時の扱いは妥当。`target_ref` の条件、原文の引用、発行者の追加を提案する(CC09IR-CLD-07)。DecisionLog との関係の明記が要る(CC09IR-CLD-06)。
5. **Q5 CC-09 削除に伴う参照切れ・欠番・副作用。** 直接の参照切れ:L306(CC-08)の「audited under CC-09」(D-04 が処理)。残る語:L204、L227、L451、Invariant 14(CC09IR-CLD-05)。欠番の扱い(CC09IR-CLD-09)。
6. **Q6 結論。** REVISE。Finding は Major 3、Minor 5、Editorial 1。
7. **Q7 開発存続判定根拠を Owner 裁定済みの規範と誤認していないか。** していない。同文書は保存された会話記録で、正式裁定ではなく、その推奨は入力としていない。ただし、背景資料が推奨を含むため、評価の独立性を保つには、結論をこの資料に依存させない注記が要る(Packet §2A がこれを行っている)。

### B-4. 条項間整合性とトレーサビリティ

- 削除の対象は、CC-09 の「三分類レコードの属性の一律 MUST」と「統治来歴の全件照合」に集約でき、これらを外すことが安全性を損なうとは見えなかった。
- フィールド単位では、CC-09 の三分類にある項目の多くは、CC-03(Decision の権限と証拠)、CC-04(試行の識別、年度末)、CC-05(Gate)、CC-07(理由、依存範囲)、CC-08(比較契約と結果の ID、影響分析)、CC-11(観測契約の有効性)、CC-12(予約 ID、イベント)、CC-13(検証の記録)に重複して存在する。失われる可能性が高いのは、年度末の実行者・権限(CC09IR-CLD-03)と、評価契約の版(CC09IR-CLD-05)である。
- `docs/Workflow.md` §4・§6 は、Owner の最終裁定、非 Canonical 資料の再検討の禁止、承認済みガバナンス裁定の再開禁止を定める。これらは、本提案(歴史的証拠の再回収を求めない)と矛盾しない。Workflow の「合意に至るまで再提出」(§4.4・§4.6)は、CC-09 とは独立に残る。

### B-5. 未検証事項

- Rev.2 へ差分を適用した結果の全文(提案の評価であり、適用はしていない)。
- 動的 V&V、29 Invariants の実行。
- Owner 原会話、歴史的裁定の原本、DecisionLog との一対一照合(IR-01 により回収義務を負わない)。
- 他AIの回答。

### B-6. 未解決事項と HOLD 条件

- Owner 判断が要る事項:Freeze 境界 L527 の DecisionLog 対応の扱い(CC09IR-CLD-02、-06)、暫定レシートの項目の採否(-07)、既存 Finding の対応表の作成(-08)、CC-09 の欠番表示(-09)。
- M19〜M25、RP-023 の HOLD は継続。

## C. 最終状態

- 取得・SHA-256 の照合:完了(4文書と比較基準。Manifest は IR-01 に無いため、限定的)
- 独立レビュー:完了(静的・文面上のレビュー。結論は REVISE)
- GitHub への書込、原本の変更:なし
- Finding の正式 Close、Owner 裁定、正式承認、Freeze:なし
- 次工程への自動移行:なし。本回答の提出時点で STOP
- M19〜M25、RP-023 の HOLD:継続
