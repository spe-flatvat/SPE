# SPE M19｜正式独立レビュー報告(Claude)— DRAFT

提出日:2026-10-31／対象AI:Claude／区分:独立レビュー回答(DRAFT)。Review Acceptance、Finding Close、正式承認、Freeze、HOLD解除のいずれでもない。

## 0. 実施記録

- 対象:固定 commit `a00c96252ee1260a909be8775511c420685b51d8` の `reviews/M19-25/M19_Review_Preservation_20261030/`(12ファイル、受領検証は READY・SHA-256 11/11)。
- 評価対象:収束候補(`4a1f70e0…`)の全文(CC-01〜CC-13、Reason taxonomy、Invariants 29件、Freeze境界)。共通パケット4件、パッチ2件、検証レシート、統合検証報告、32件処分案(CSV・報告)。
- 独立性:他AIの今回回答、およびパケット外の保全ファイルは開いていない。同一 commit 内の他ディレクトリも開いていない。
- 開示:32件のうち CLD3-01〜05 は、私自身の前回(限定再レビュー)のFindingである。その処分案の評価では、自分の指摘への処分を評価することになるため、根拠の記載の有無に限定して判断した。
- 独自に再現した確認(いずれも実バイト):
  1. FG-06 配布 commit `789403ae…` の統合候補(`4a3b475a…`)に FG06 パッチを適用すると、収束候補とバイト一致(`4a1f70e0…`)。
  2. 収束候補から FG-07-07 パッチを逆適用すると、レシート記載の `dc8d22dd…` と一致。
  3. 収束候補の先頭52行(ヘッダ)は、`4a3b475a…` のヘッダと同一。ヘッダは変更されていない。
  4. CC-01〜CC-13 は13/13。CSV は32行・ID重複なし・全行 OPEN、区分は 11/10/11 でレポートと一致。

## A. Verdict

**REVISE(軽微修正)。**

理由:
- 収束候補の変更は CC-04 の1段落と CC-06 の1文だけで、意図した範囲に収まっている。2026年の再基準化の矛盾(前回の CLD3-02)は本文上解消し、2026年の切替候補を生成する経路は規範上作られていない(CLD3-03 の趣旨)。この2点は評価できる。
- 一方、今回の修文で入った条件句 `where required by those contracts or other applicable approved requirements` は、(i) 参照先が未承認の本契約自身を含みうる循環があり、(ii) CC-12 の予約条件と整合しない(CLD4-01、CLD4-02)。いずれも Minor。
- 前回の CLD3-01(Major)は、候補本文のヘッダが無変更のため、本文上は未解消のまま。処分案が頼る「別紙注記」はパケット内に存在しない。
- 新規の Major はない。直接の条項衝突(fail-open になる確定的な衝突)も検出していない。

## B. 新規Finding(原Findingと区別するため、ID は CLD4-xx)

### CLD4-01|CC-04 L152:条件句が循環し、範囲が開いている(Minor／解釈上のリスク)

- 引用:「A candidate targeting 2026 may be used only if its creation and use are separately authorized under applicable approved contracts and, where required by those contracts or other applicable approved requirements, attributable Decisions, …」
- 問題:
  (a) `other applicable approved requirements` の「approved」の主体・特定方法が不明である。CC-03 の Decision 要件は本契約の一部だが、本契約はまだ承認されていない(L4、L21)。承認前は、Decision 要件を課す「approved requirement」に本契約自身が含まれない読みが成り立つ。
  (b) 別途承認された契約が Decision を要求しない場合、2026年を対象とする候補が Decision なしで使えうる。裁量型の切替には CC-03(`met/approved`)が別に課されるが、この文からは参照されていない。
  (c) 構文上、`attributable Decisions` が authorization の別の源として読める。
- 失敗シナリオ:承認前または Freeze 前の検証で、2026年の候補について「該当する承認済み要件がない」ため Decision 不要と判定される。
- 最小修正案:`attributable Decisions` を次のように具体化する。「attributable Decisions (required under CC-03 for discretionary switches, and for other switch types as required by their separately approved contracts)」。`other applicable approved requirements` は削除するか、「identified by immutable reference」を付ける。
- 再評価条件:Owner が「別契約で Decision なしの2026候補を許容する」と決めた場合は Major。

### CLD4-02|CC-12 L403 / CC-05 L211:Decision 証拠が無条件のまま(Minor)

- 引用:CC-12「Before scheduling, the controller MUST validate … attributable Trigger and Decision evidence」(L403)。CC-05 Gate B「attributable Decision authority and evidence」(L211)。
- 問題:CC-04 の改訂は「Decision は必要な場合のみ」と読める方向だが、CC-12 は予約を作るすべての候補に Decision 証拠を要求している。CC-03 は非裁量型の切替を「別途承認された契約」に委ねており、その契約が Decision を持たなければ、CC-04 と CC-12 が衝突する。CC-04 の修文は、意図(CC-04 レシートの「既存の承認済み契約その他の適用要件へ委ねる趣旨」)を、CC-12 の側では達成していない。
- 最小修正案:L403 を「…attributable Trigger evidence and, where required under CC-03 or the applicable approved transition contract, Decision evidence」とする。別案:非裁量型は現時点で存在しないと Owner が確認し、CLD4-01 と合わせて Decision 要件を単一の参照先(CC-03)に集約する。いずれの場合も、CC-04 だけの修文では不整合が残る。

### CLD4-03|処分案CSV:行番号引用が収束候補に対して2行ずれている／根拠欄の一部が定型文(Minor／台帳)

- 事実:CSV が引用する L217、L286、L284／290／292／439、L309、L413／415／423 は、`4a3b475a…` の行番号である。収束候補では L152 に2行が挿入されたため、L152 以降は+2ずれる(確認:CSV の `L217`=現候補の L219。`L286`=現候補の L288。`L309`=L311。`L413/415/423`=L415/417/425)。L59、L105、L150 は一致。
- 追加事実:根拠欄 `改訂文案／既存条項／証拠整理を照合` が、FG06-GPT-RR-04、CLD3-04、CLD3-05 の3行で同一の定型文であり、個別の条項引用がない。`Original Severity` 欄は書式が統一されていない(`GEMINI-01` の行は、原回答の表の1行がそのまま入っている)。
- 影響:処分案の根拠を条項で追跡する場合に、誤った文を読むおそれがある。規範内容には影響しない。
- 修正:引用行番号を収束候補基準に更新する(または「`4a3b475a…` 基準」と明記する)。3行に個別の根拠を書く。Severity 欄を正規化する(または別欄に原文を残す)。

### CLD4-04|収束候補のヘッダ:変更の根拠が記載されていない／自己識別(Editorial)

- ヘッダは `4a3b475a…` と同一で、Document ID `M19-CC-v0.4-DRAFT` と本文の見出し「FG-06 R-01–R-07 Integrated Candidate DRAFT」を保持している。今回の CC-04 追加段落と CC-06 の変更は、Integration basis(L5)にも出典として現れない。
- 同一 ID の別バイト列が、`4a3b475a…`、`dc8d22dd…`(FG-07-07)、`4a1f70e0…` の3つになった。L7 の「has not been independently re-reviewed」も、現時点では古い自己言及である。
- 修正:Status、Integration basis、Document ID にこの収束版の識別と、追加2変更の権限根拠(Owner の限定再開の範囲)を書く。CLD3-04 の継続。

## C. 共通レビュー依頼書の質問への回答

1. **Q1 CC-04 の条件句は、Decision 義務を意図せず増減するか。**
   - 裁量型:`other applicable approved requirements` の循環により、承認前は減る側に読まれうる(CLD4-01)。CC-03 の `met/approved` 要件自体は本文で維持されており、明文の削除はない。
   - 非裁量型:増減の意図が CC-12 L403 では実現しておらず、不整合が残る(CLD4-02)。
2. **Q2 2026年と2027年以降の整合、2026候補の暗黙の認可。**
   - 参照分岐(Gate A、Gate C、CC-06)は整合した。暗黙の認可は、規範として作られていない(L152)。
   - 構造的な補足:候補は Post-year decision boundary(L172)で作られる一方、2026年の前年(2025年)は計算対象ではない(L138)。2026年を対象とする候補は、年次の流れでは生成できない。したがって L150 の2026分岐は、別契約が存在しない限り到達不能で、現時点では安全側に働く。ただし、別契約が存在した場合の条件は CLD4-01 が示すとおり。
3. **Q3 CC-01/03/08/09/10/11/13 とFreeze境界のセーフガード。**
   - 変更点以外は無変更で、弱化は見つからなかった(L59、L105、L288、CC-13 L441 は維持)。
   - 前回から継続の指摘は未対応のまま:CLD2-01(L105 の `no switch;` 欠落、`Persistent` の基準と理由コード)、CLD2-02(L288 の `comparison operation` と、`eligible` を付与する `designated comparison validation operation` の名称差)、CLD2-03(L55 の `select only` の `only` 欠落)、CLD2-05(Invariants が復元義務を直接カバーしない)。いずれも Minor／Editorial。
   - CLD-05 の趣旨:L219 の `NOT_EVALUATED` は、Gate A／C 失敗による未到達を明示していない。
4. **Q4 32件の処分案の評価。** D節。
5. **Q5 規範上の衝突・曖昧さ。** B節(CLD4-01、02)。意味論の変更を要するもの:CLD4-02 の方向性の選択。文言のみ:CLD4-01、CLD4-03、CLD4-04、CLD2 系。
6. **Q6 新たな Owner 判断が要るもの／既存裁定での文言修正で足りるもの。**
   - Owner 判断:(1) 別契約による2026年の切替候補を、Decision なしでも許容するか。(2) 非裁量型の切替を現時点で想定するか(CLD4-02)。(3) CLD3-01:ヘッダの `R-01–07`(歴史的な裁定群)と、FG-06 の `R-01〜R-07`(2026-10-28)の関係の確認。
   - 文言修正:上記以外(CLD4-01 の具体化、CLD4-03、CLD4-04、CLD2 系)。

## D. 32件の個別評価(Close はしない／原ID・原Severity・OPEN を維持)

凡例:**S**=処分案は引用された本文で支持される。**S\***=支持されるが留保あり。**I**=根拠が不十分または本文で未確認。**E**=証拠留保の分類が適切(本文では判断できない)。行番号は収束候補基準。

| ID | 評価 | 理由 |
|---|---|---|
| FG06-GPT-RR-01 | S\* | L150／L152／L249(CC-06)で分岐は整合。2026候補の可否は未承認のまま。CLD4-01 が残余 |
| FG06-GPT-RR-02 | S\* | L190–198、L417 の既存要件で扱う。自動失効は作られていない |
| FG06-GPT-RR-03 | S | L125／L127／L311 が履歴と現行適用性を区別 |
| FG06-GPT-RR-04 | E | 根拠欄が定型文(CLD4-03)。分類自体は妥当 |
| CLD3-01 | **I** | ヘッダは無変更で、「別紙注記」はパケットに存在しない。Major のまま未解消 |
| CLD3-02 | S | L249 が2026／2027+ を分岐。矛盾は解消 |
| CLD3-03 | S\* | L152 が経路を作らないと明記。CLD4-01 の残余 |
| CLD3-04 | I | ヘッダ無変更。根拠欄が定型文 |
| CLD3-05 | I | 同上 |
| GEMINI-FG06-01 | S\* | L152 で非創設を明記。外部根拠は NOT VERIFIED |
| GRK-LIM-01 | S | L249 で前年参照不成立を解消 |
| GRK-LIM-02 | E | 受領留保の維持が妥当 |
| GPT6-FG06-01 | S\* | L288 に包括的 MUST。CLD2-02 の主体名称差が残る |
| GPT6-FG06-02 | E | 歴史的承認原本は未検証。本文では決まらない |
| GPT6-FG06-03 | S\* | L59 は無条件。CLD2-03(`only`)が残る |
| GPT6-FG06-04 | S\* | L150／L152。候補可否の残余は CLD4-01 |
| GPT6-FG06-05 | S\* | L125／L127／L311 を確認。原文はパケットにないため、案の要約に基づく評価 |
| GPT6-FG06-06 | S\* | L190–198 と L415–425 の併読で成立。自動失効なし |
| GPT6-FG06-07 | E | L4／L7 は古いまま(CLD4-04)。分類は妥当 |
| CLD-01 | S\* | L105 に復元文。CLD2-01 が残る |
| CLD-02 | S | L59 |
| CLD-03 | S\* | L288。CSV の引用 `L286` は誤り(CLD4-03) |
| CLD-04 | S\* | L150／L152／L249 |
| CLD-05 | S\* | CSV の引用 `L217` は L219 が正しい。Gate A／C 失敗の明示は無く、任意の補強として維持 |
| CLD-06 | E | 妥当 |
| GEMINI-01 | S\* | 失効契機を追加しない扱いは L123 と整合。Severity 欄の書式に難(CLD4-03) |
| GRK-01 | E | 過去承認は未検証 |
| GRK-02 | S | L59 |
| GRK-03 | S | L288 |
| GRK-04 | S\* | L150／L249 |
| GRK-05 | E | 妥当 |
| GRK-06 | E | 妥当 |

集計:S 6、S\* 15、I 3、E 8(計32)。「S」も、正式 Close を意味しない。

加えて、**32件の台帳に含まれない既知の指摘**がある:私の CLD2-01、02、03、05(3DEC 再レビュー由来。上記の継続分)。パケットが使う `CLD2` という語は、定義がなく、これらを指すのか別の歴史的資料を指すのか判別できない(NOT VERIFIED の注記と併せて、ID 衝突のおそれ)。台帳での追跡対象にするかは Owner 判断。

## E. NOT VERIFIED／残余リスク

- NOT VERIFIED:歴史的 Owner 裁定の原本(E1)、E-03／E-04、`CLD2` の指す資料、FG-06 R-01〜R-07 と歴史的 R-01〜07 の原文、32件の各原レビュー全文(パケットに無く、案の要約に依存)。
- 静的な契約レビューのみ。エンジン実行、29 Invariants の V&V、数値モデルの検証は行っていない。「衝突が検出されない」は整合性の証明ではない。
- 範囲:Rev.2 の18件と Step 6D-35 の5件は32件に含まれず、今回は扱っていない。

## F. 推奨する最小修正(Owner 承認後に実施する想定)

1. CLD4-01:L152 の条件句を具体化する(CC-03 と承認済み契約を明示、`other applicable approved requirements` を削除または特定)。
2. CLD4-02:CC-12 L403 に「where required」を入れるか、Decision 要件の参照先を CC-03 に一本化する。
3. CLD3-01:ヘッダの `R-01–07` を時点・出典で修飾し、Owner 原文と照合する。
4. CLD4-04:Status、Integration basis、Document ID の更新。
5. CLD4-03:CSV の行番号引用の更新と、3行の根拠の個別化。
6. 継続:CLD2-01／02／03／05、CLD-05 の補強。

以上。GitHub への書き込み、Finding の Close、Owner 裁定の代行は行っていない。
