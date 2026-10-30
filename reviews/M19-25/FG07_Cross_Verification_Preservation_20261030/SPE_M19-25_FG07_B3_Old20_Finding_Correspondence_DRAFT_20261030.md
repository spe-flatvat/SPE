# SPE M19–25｜FG-07 B3 旧20 Finding対応表 DRAFT

- 作成日：2026-10-30（JST）
- Status：DRAFT / NON-CANONICAL / OWNER DISPOSITION PENDING
- 工程：FG-07 横断検証本文（分析・新規DRAFTのみ）
- 固定入力：P=`789403ae904594a0973ed7c7a142745a75595320`／R=`d36ae4428d35105bed4fbedc72c7db1500330655`
- 対象統合候補SHA-256：`4a3b475abb1281c7bf25b27bc23c0e67b3f0abd3e494222404f607d7c6cc16c1`
- M19–25／RP-023：HOLD継続。正式Close／Review Acceptance／Canonical化／Freezeは実施しない。

## 1. 対象集合と方法

対象はPの固定crosswalkに列挙された旧20件（GPT-6 7／Claude 6／Gemini 1／Grok 6）。台帳だけに依拠せず、同梱の旧4原回答の各Finding本文を読み、新12件の原回答・統合候補と照合した。これは旧四AIレビュー全体を再実施したものではなく、本指示範囲の対応分析である。

各行の「文言修復」は保存原文の比較結果であり、Owner承認・正式Disposition・Closeとは別。新12件に直接対応がなくても、解消・無効・不要とは認定しない。1対多・多対1の参照を保持する。

## 2. 20/20対応一覧

| 旧原ID | 主題 | 新12件との関係 | 統合候補での照合・留保 | Disposition |
|---|---|---|---|---|
| `GPT6-FG06-01` | 比較契約全条件の検証 | 直接対応する新Findingなし。CLD3-01は一般的証拠論点としてのみ関連。 | L286に包括的MUSTが復元されL284／290／292／439も保持。旧文言弱化は原文上直接修復を確認。CLD2-02の主体区別は別枠。採用根拠E1・正式処分は未検証。 | 未確定／未Close |
| `GPT6-FG06-02` | 実質追加規範の歴史的承認 | CLD3-01、CLD3-05に関連。FG06-GPT-RR-04／CLD3-04は表示・追跡面で関連。 | 現在の起案根拠と歴史的未検証はL5／14で分離。ただし将来向けE2レシートは歴史的承認の遡及証明ではない。未検証部分を保持。 | 未確定／未Close |
| `GPT6-FG06-03` | 意味論保護の別承認例外 | 直接対応する新Findingなし。CLD2-03は別枠。 | L59は例外なしの禁止。L61のmetadata別承認を意味論例外へ拡張しない。旧差分への文言対応を確認したが正式Closeではない。 | 未確定／未Close |
| `GPT6-FG06-04` | 2026 Gate Cの参照・候補可否 | FG06-GPT-RR-01、CLD3-02、GRK-LIM-01、CLD3-03、GEMINI-FG06-01に関連。 | L150でGate Cの2026／2027+参照分岐は明示された。候補生成権限とCC-06アンカーの残余は別に残る。旧件全体の解消を認定しない。 | 未確定／未Close |
| `GPT6-FG06-05` | 多年度pendingと現行Decision表現 | FG06-GPT-RR-03に関連。 | L113／125／127／309は既に履歴・現行適用性・切替認可を区別する。新件はその監査結果・プロセス参照の明確化。単一enumの実装方式は別契約。 | 未確定／未Close |
| `GPT6-FG06-06` | 未発効予約・年度末未成立時の処理 | FG06-GPT-RR-02に関連（同一ではない）。 | 新件は異常年度末成功時の証拠条件、旧件は年度末未成立・契約欠落時の未解決予約にも及ぶ。L413／415／423とL176–196を併読し、自動失効を作らない。 | 未確定／未Close |
| `GPT6-FG06-07` | 固定StatusとOD-12 | FG06-GPT-RR-04、CLD3-04に関連。CLD3-01は隣接する別論点。 | L4／7の固定状態と後続承認を外部追跡する。OD-12はRev.2四AI18件の規範上の処理に対する条件付き範囲を維持し、新候補全体の無条件受理へ拡張しない。 | 未確定／未Close |
| `CLD-01` | met/not_required持続時fail-closed削除 | 新12件に直接同一のFindingなし。CLD2-01は別枠。 | L105に明示文が復元。L80／96／98／127も併読。no switch等の残余は別レビュー参照として保持し、復元とCloseを分離。 | 未確定／未Close |
| `CLD-02` | CC-01別承認例外 | 新12件に直接同一なし。CLD2-03は別枠。 | L59で無条件禁止へ復元。将来別工程を全般禁止する意味には拡大しない。OwnerレシートのE1未照合と正式処分を留保。 | 未確定／未Close |
| `CLD-03` | CC-08実質検証MUST縮小 | 新12件に直接同一なし。CLD2-02は別枠。 | L286のcomparison operation MUST validateで全条件を直接要求。版照合L290だけに代替されていない。操作主体の名称に関する別残余とは分ける。 | 未確定／未Close |
| `CLD-04` | 2026候補とGate C | G-01の3件およびCLD3-03／GEMINI-FG06-01に関連。 | Gate C参照自体はL150で明示。旧件は候補可否も問うため、アンカー・生成経路の関連残余を維持。 | 未確定／未Close |
| `CLD-05` | Gate A/C失敗時のGate B記録 | 直接対応する新Findingなし。新回答のQ05で言及するが新IDはない。 | L217はチェックポイント未到達全般にNOT_EVALUATEDを要求し、Gate A/C失敗による未到達も条件として包含し得る。元Findingも一般規範の欠落ではなく原因例の明示を求める。任意の説明補強候補として保持、正式処分なし。 | 未確定／未Close |
| `CLD-06` | 固定冒頭とOD-12の別管理 | FG06-GPT-RR-04／CLD3-04に関連。 | 旧原回答自身が現時点で確定的問題なしと述べる。固定原本と限定OD-12を区別して維持。後続レビューによる正式受理は推定しない。 | 未確定／未Close |
| `GEMINI-01` | pending失効条件の監査証跡 | FG06-GPT-RR-03に関連（同一とはしない）。 | 旧件は失効条件・ログ、新件は現行適用性の判定結果とプロセス参照。L121／123／125／127／309の区別を保ち、新しい失効契機を自動追加しない。 | 未確定／未Close |
| `GRK-01` | 実質追加規範の承認根拠 | CLD3-01／CLD3-05に関連。 | E2の現在裁定・起案根拠は取得済みだが、原歴史的裁定の証明はNOT VERIFIED。条文の合理性、将来起案根拠、過去承認の3軸を分離。 | 未確定／未Close |
| `GRK-02` | 意味論変更の別承認窓口 | 新12件に直接同一なし。CLD2-03は別枠。 | L59で元の例外を除去。原Major（条件付き）を保持し、文言対応確認から正式Closeへ進まない。 | 未確定／未Close |
| `GRK-03` | 比較契約列挙外条件の脱落余地 | 新12件に直接同一なし。CLD2-02は別枠。 | L286にall expressly required contract conditionsが存在。原MinorとMajor再評価をしない旨の判断は保持し、他AIの旧Majorへ統一しない。 | 未確定／未Close |
| `GRK-04` | 2026 preceding-yearの誤読 | GRK-LIM-01、FG06-GPT-RR-01／CLD3-02、CLD3-03／GEMINI-FG06-01に関連。 | 旧提案のGate C参照明確化はL150に現れる。新Grok件はCC-06のアンカー参照へ焦点が移り、同一の旧文言欠落がそのまま残るわけではない。 | 未確定／未Close |
| `GRK-05` | 原本Statusと限定受理 | FG06-GPT-RR-04／CLD3-04に関連。 | 固定状態とOD-12範囲の別欄管理を継続。無断のヘッダ更新・正式受理拡張は行わない。 | 未確定／未Close |
| `GRK-06` | 旧GrokレビューのSHA未計測 | GRK-LIM-02と類似・関連だが別の受領事象。 | 旧件は原Rev.4（d1b6…）、新件は統合候補（4a3b…）を扱う。当時Grok本人の未計測を、今回の保存ファイル計測や補完証拠でPASSへ書き換えない。 | 未確定／未Close |

## GPT6-FG06-01｜比較契約全条件の検証

- 旧原文範囲：[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L63-L85) L63–85。
- 原Severity表現（そのまま引用）：

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L65) L65

> 重大度：Major｜解釈上のリスク

### 対応判断の根拠となる旧原文

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L73) L73

> Rev.4は比較契約に含むべき項目を列挙し、依存versionの再検証を義務化しています。しかし、比較契約に定義されたすべての明示的な必須条件を実際に検証するという包括的義務は、同等の明確さでは再掲されていません。

### 今回の対応・条文照合（Work分析）

直接対応する新Findingなし。CLD3-01は一般的証拠論点としてのみ関連。

L286に包括的MUSTが復元されL284／290／292／439も保持。旧文言弱化は原文上直接修復を確認。CLD2-02の主体区別は別枠。採用根拠E1・正式処分は未検証。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L276-L300) L276–300／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L431-L447) L431–447。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GPT6-FG06-02｜実質追加規範の歴史的承認

- 旧原文範囲：[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L87-L115) L87–115。
- 原Severity表現（そのまま引用）：

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L89) L89

> 重大度：Major｜証拠不足

### 対応判断の根拠となる旧原文

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L107) L107

> Rev.4 L11にはAuthority basisとして複数の裁定IDが列挙されていますが、原裁定の完全照合は未了です。

### 今回の対応・条文照合（Work分析）

CLD3-01、CLD3-05に関連。FG06-GPT-RR-04／CLD3-04は表示・追跡面で関連。

現在の起案根拠と歴史的未検証はL5／14で分離。ただし将来向けE2レシートは歴史的承認の遡及証明ではない。未検証部分を保持。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L5-L15) L5–15／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L325-L339) L325–339。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GPT6-FG06-03｜意味論保護の別承認例外

- 旧原文範囲：[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L117-L141) L117–141。
- 原Severity表現（そのまま引用）：

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L119) L119

> 重大度：Major｜解釈上のリスク・証拠不足

### 対応判断の根拠となる旧原文

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L129) L129

> > It MUST NOT modify M10/M14/M17 calculation semantics or M18 evaluation semantics without separate approval.

### 今回の対応・条文照合（Work分析）

直接対応する新Findingなし。CLD2-03は別枠。

L59は例外なしの禁止。L61のmetadata別承認を意味論例外へ拡張しない。旧差分への文言対応を確認したが正式Closeではない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L55-L63) L55–63。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GPT6-FG06-04｜2026 Gate Cの参照・候補可否

- 旧原文範囲：[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L143-L163) L143–163。
- 原Severity表現（そのまま引用）：

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L145) L145

> 重大度：Minor｜解釈上のリスク

### 対応判断の根拠となる旧原文

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L155) L155

> 通常の2027年以降の切替には実際の前年確定状態が必要ですが、2026年に有効化される切替候補が許容されるかどうかは明確ではありません。

### 今回の対応・条文照合（Work分析）

FG06-GPT-RR-01、CLD3-02、GRK-LIM-01、CLD3-03、GEMINI-FG06-01に関連。

L150でGate Cの2026／2027+参照分岐は明示された。候補生成権限とCC-06アンカーの残余は別に残る。旧件全体の解消を認定しない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L138-L154) L138–154／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L247-L251) L247–251。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GPT6-FG06-05｜多年度pendingと現行Decision表現

- 旧原文範囲：[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L165-L185) L165–185。
- 原Severity表現（そのまま引用）：

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L167) L167

> 重大度：Minor｜解釈上のリスク・新規Finding

### 対応判断の根拠となる旧原文

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L175) L175

> そのため、単一のDecision状態値が「現行の移行評価」と「存続する意思決定プロセス」のどちらを表すのか、実装時に曖昧になる可能性があります。

### 今回の対応・条文照合（Work分析）

FG06-GPT-RR-03に関連。

L113／125／127／309は既に履歴・現行適用性・切替認可を区別する。新件はその監査結果・プロセス参照の明確化。単一enumの実装方式は別契約。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L111-L133) L111–133／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L307-L315) L307–315。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GPT6-FG06-06｜未発効予約・年度末未成立時の処理

- 旧原文範囲：[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L187-L207) L187–207。
- 原Severity表現（そのまま引用）：

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L189) L189

> 重大度：Minor｜解釈上のリスク・新規Finding

### 対応判断の根拠となる旧原文

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L199) L199

> ただし、Gate失敗後に年度末が正常終了しない場合や、異常年度末の権限契約自体が欠ける場合、予約の解決をどの時点で必須とするかが明確ではありません。

### 今回の対応・条文照合（Work分析）

FG06-GPT-RR-02に関連（同一ではない）。

新件は異常年度末成功時の証拠条件、旧件は年度末未成立・契約欠落時の未解決予約にも及ぶ。L413／415／423とL176–196を併読し、自動失効を作らない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L176-L196) L176–196／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L409-L423) L409–423。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GPT6-FG06-07｜固定StatusとOD-12

- 旧原文範囲：[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L209-L227) L209–227。
- 原Severity表現（そのまま引用）：

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L211) L211

> 重大度：Editorial｜証拠・表示上のリスク

### 対応判断の根拠となる旧原文

[ChatGPT_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/ChatGPT_Rev4_FG06_20261025.md#L221) L221

> この二つは時点と適用範囲が異なり、必ずしも矛盾しません。

### 今回の対応・条文照合（Work分析）

FG06-GPT-RR-04、CLD3-04に関連。CLD3-01は隣接する別論点。

L4／7の固定状態と後続承認を外部追跡する。OD-12はRev.2四AI18件の規範上の処理に対する条件付き範囲を維持し、新候補全体の無条件受理へ拡張しない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L4-L17) L4–17／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L325-L339) L325–339。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## CLD-01｜met/not_required持続時fail-closed削除

- 旧原文範囲：[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L32-L46) L32–46。
- 原Severity表現（そのまま引用）：

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L33) L33

> **重大度：Major**

### 対応判断の根拠となる旧原文

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L40) L40

> - **問題と成立条件：** Rev.2はこの一時状態が未解消のまま持続した場合、当該依存する切替についてfail closedとする帰結を**行内に明示**していた。Rev.4はこの一文を削除し、「settleしなければならない」という義務のみを残して、持続した場合の制御上の帰結を本行では明示していない。CC-05の一般的な依存範囲別fail-closed原則やInvariant等から類推すれば同じ結論に到達できる可能性はあるが、少なくとも本行単体では規範の強度が弱まっている。これは編集上の整理ではなく、既存の明示的保証の削除である。

### 今回の対応・条文照合（Work分析）

新12件に直接同一のFindingなし。CLD2-01は別枠。

L105に明示文が復元。L80／96／98／127も併読。no switch等の残余は別レビュー参照として保持し、復元とCloseを分離。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L80-L80) L80–80／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L96-L109) L96–109。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## CLD-02｜CC-01別承認例外

- 旧原文範囲：[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L48-L60) L48–60。
- 原Severity表現（そのまま引用）：

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L49) L49

> **重大度：Major（FG05-N02と同一論点、独立に到達）**

### 対応判断の根拠となる旧原文

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L54) L54

> - **問題と成立条件：** 無条件の禁止から、別途承認があれば変更を許容する条件付き禁止への変更。現時点での無承認変更は依然禁止されているが、将来の例外経路を新設した点で権限境界の実質変更であり、既存のRev.2禁止と同等とは言えない。

### 今回の対応・条文照合（Work分析）

新12件に直接同一なし。CLD2-03は別枠。

L59で無条件禁止へ復元。将来別工程を全般禁止する意味には拡大しない。OwnerレシートのE1未照合と正式処分を留保。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L55-L63) L55–63。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## CLD-03｜CC-08実質検証MUST縮小

- 旧原文範囲：[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L62-L78) L62–78。
- 原Severity表現（そのまま引用）：

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L63) L63

> **重大度：Major（FG-05はMinor／条件付きMajorとしたが、本レビューは独立にMajorと評価する）**

### 対応判断の根拠となる旧原文

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L72) L72

> - **問題と成立条件：** Rev.2は比較操作（comparison operation）自身に、評価期間・指標定義・単位・ベースライン適合性・方法論・「明示的に要求される全契約条件」を**実際に検証する**義務を課していた。Rev.4では、これらの項目は契約が**識別・記載すべき**項目へと移動し、比較操作に残る検証義務は「正確な契約・依存バージョンに適合しているか」という**バージョン一致の検証**のみである。これは文言整理ではなく、「内容の実質検証」から「バージョンの形式一致検証」への**検証義務の縮小**である。CC-13 L432–434が比較判定成功を要求する点、CC-08 L289が非影響確認できない場合に出版を留保する点は維持されているため、全面的な検証義務の削除とまでは言えないが、"metric definitions"や"all expressly required contract conditions"のような、契約内容そのものの実質検証を明示的に要求する語が本文から消えている。

### 今回の対応・条文照合（Work分析）

新12件に直接同一なし。CLD2-02は別枠。

L286のcomparison operation MUST validateで全条件を直接要求。版照合L290だけに代替されていない。操作主体の名称に関する別残余とは分ける。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L276-L300) L276–300／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L431-L447) L431–447。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## CLD-04｜2026候補とGate C

- 旧原文範囲：[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L80-L87) L80–87。
- 原Severity表現（そのまま引用）：

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L81) L81

> **重大度：Minor**

### 対応判断の根拠となる旧原文

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L84) L84

> - **問題：** CC-04は2026をBaseline Initial-State Contractによる初期化、2027以降をGate Aによる「実際に確定した前年度状態」の検証と明確に区別する。一方、L145の「Year-entry sequence」は2026–2055の全年次に一律に適用され、L147の切替候補に対するGate C検証は「actual authorized preceding-year state」を要求する。2026年に切替候補が存在しうる場合、2026年には定義上「preceding-year state」が存在しないため、Gate CがBaseline Initial-State Contractをどのように代替的に検証するのかが本文上で明示されていない。

### 今回の対応・条文照合（Work分析）

G-01の3件およびCLD3-03／GEMINI-FG06-01に関連。

Gate C参照自体はL150で明示。旧件は候補可否も問うため、アンカー・生成経路の関連残余を維持。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L138-L154) L138–154／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L247-L251) L247–251。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## CLD-05｜Gate A/C失敗時のGate B記録

- 旧原文範囲：[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L89-L95) L89–95。
- 原Severity表現（そのまま引用）：

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L90) L90

> **重大度：Minor／Editorial**

### 対応判断の根拠となる旧原文

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L93) L93

> - **問題：** L210の規定は「Gate AとGate Cが通過し、正式なGate Bチェックポイントに到達し、Gate Bが非適用と確定した場合」にNOT_APPLICABLEを記録する義務を定める。L214は「正式チェックポイントに到達しなかった場合」にNOT_EVALUATEDを維持する義務を定める。しかし、Gate AまたはGate C自体が失敗した結果としてGate Bの正式チェックポイントに到達しなかった場合が、この「到達しなかった場合」に含まれることは文脈上推測できるが、本文で明示的に述べられていない。

### 今回の対応・条文照合（Work分析）

直接対応する新Findingなし。新回答のQ05で言及するが新IDはない。

L217はチェックポイント未到達全般にNOT_EVALUATEDを要求し、Gate A/C失敗による未到達も条件として包含し得る。元Findingも一般規範の欠落ではなく原因例の明示を求める。任意の説明補強候補として保持、正式処分なし。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L148-L154) L148–154／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L211-L235) L211–235。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## CLD-06｜固定冒頭とOD-12の別管理

- 旧原文範囲：[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L97-L101) L97–101。
- 原Severity表現（そのまま引用）：

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L98) L98

> **重大度：Editorial**

### 対応判断の根拠となる旧原文

[Claude_FG06_original.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Claude_FG06_original.md#L100) L100

> - 対象ファイルの冒頭 `NOT REVIEW-ACCEPTED` は固定時点のバイト列の記述であり、今回のOwner指示によるOD-12条件付きReview Acceptanceとは別管理する必要がある。FG-05の見解に同意する。配布文書（本Common Review Request等）では両者が別表示されており、現時点で誤解を招く表示はないと判断する。

### 今回の対応・条文照合（Work分析）

FG06-GPT-RR-04／CLD3-04に関連。

旧原回答自身が現時点で確定的問題なしと述べる。固定原本と限定OD-12を区別して維持。後続レビューによる正式受理は推定しない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L4-L17) L4–17／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L509-L525) L509–525。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GEMINI-01｜pending失効条件の監査証跡

- 旧原文範囲：[Gemini_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Gemini_Rev4_FG06_20261025.md#L22-L22) L22–22。
- 原Severity表現（そのまま引用）：

[Gemini_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Gemini_Rev4_FG06_20261025.md#L22) L22

> | GEMINI-01 | Minor | CC-03 (L108-130) | マルチイヤーpending Decisionの継続条件において、Triggerが not_met や unknown に変化した際の不整合防止策が明記されているが、当該プロセスの失効条件の監査証跡要件をより明示することが望ましい。 | 推奨修正（提案のみ）。実効性を高めるため、失効時のログ記録義務を追記する検討（本文変更はOwner承認後）。 | 新規Finding |

### 対応判断の根拠となる旧原文

[Gemini_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Gemini_Rev4_FG06_20261025.md#L22) L22

> | GEMINI-01 | Minor | CC-03 (L108-130) | マルチイヤーpending Decisionの継続条件において、Triggerが not_met や unknown に変化した際の不整合防止策が明記されているが、当該プロセスの失効条件の監査証跡要件をより明示することが望ましい。 | 推奨修正（提案のみ）。実効性を高めるため、失効時のログ記録義務を追記する検討（本文変更はOwner承認後）。 | 新規Finding |

### 今回の対応・条文照合（Work分析）

FG06-GPT-RR-03に関連（同一とはしない）。

旧件は失効条件・ログ、新件は現行適用性の判定結果とプロセス参照。L121／123／125／127／309の区別を保ち、新しい失効契機を自動追加しない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L121-L133) L121–133／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L307-L315) L307–315。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GRK-01｜実質追加規範の承認根拠

- 旧原文範囲：[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L43-L53) L43–53。
- 原Severity表現（そのまま引用）：

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L44) L44

> - **重大度:** Major（規範追加の承認根拠未検証）

### 対応判断の根拠となる旧原文

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L46) L46

> - **問題:** 多年度 `pending`、計算再試行、atomic/idempotent 年度末、異常年度末と数値継続の分離、比較再検証・予約/Decision寿命分離など、Rev.2に無かった**実質義務・例外構造**が追加されている。条文としては整合的だが、**既存 Owner 原裁定との対応は本パケット証拠では未検証**。

### 今回の対応・条文照合（Work分析）

CLD3-01／CLD3-05に関連。

E2の現在裁定・起案根拠は取得済みだが、原歴史的裁定の証明はNOT VERIFIED。条文の合理性、将来起案根拠、過去承認の3軸を分離。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L5-L15) L5–15／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L325-L339) L325–339。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GRK-02｜意味論変更の別承認窓口

- 旧原文範囲：[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L55-L67) L55–67。
- 原Severity表現（そのまま引用）：

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L56) L56

> - **重大度:** Major（条件付き）

### 対応判断の根拠となる旧原文

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L58) L58

> - **問題:** Rev.2 は M10/M14/M17/M18 意味論の変更を**無条件禁止**。Rev.4 は `without separate approval` を付し、**別承認付き変更を許容**する読みになる。

### 今回の対応・条文照合（Work分析）

新12件に直接同一なし。CLD2-03は別枠。

L59で元の例外を除去。原Major（条件付き）を保持し、文言対応確認から正式Closeへ進まない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L55-L63) L55–63。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GRK-03｜比較契約列挙外条件の脱落余地

- 旧原文範囲：[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L69-L79) L69–79。
- 原Severity表現（そのまま引用）：

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L70) L70

> - **重大度:** Minor

### 対応判断の根拠となる旧原文

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L72) L72

> - **問題:** Rev.2 の「all expressly required contract conditions」が、Rev.4 では列挙（ID/version/period/metrics/…/required dependencies）＋版一致検証に置換。列挙外の契約条件が落ちる余地。

### 今回の対応・条文照合（Work分析）

新12件に直接同一なし。CLD2-02は別枠。

L286にall expressly required contract conditionsが存在。原MinorとMajor再評価をしない旨の判断は保持し、他AIの旧Majorへ統一しない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L284-L300) L284–300。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GRK-04｜2026 preceding-yearの誤読

- 旧原文範囲：[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L81-L91) L81–91。
- 原Severity表現（そのまま引用）：

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L82) L82

> - **重大度:** Minor

### 対応判断の根拠となる旧原文

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L84) L84

> - **問題:** 2026 で切替候補がある場合、Gate C の「preceding-year state」が初期状態契約を指すことは読めるが、用語が「year」前提に見えやすい。

### 今回の対応・条文照合（Work分析）

GRK-LIM-01、FG06-GPT-RR-01／CLD3-02、CLD3-03／GEMINI-FG06-01に関連。

旧提案のGate C参照明確化はL150に現れる。新Grok件はCC-06のアンカー参照へ焦点が移り、同一の旧文言欠落がそのまま残るわけではない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L138-L154) L138–154／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L247-L251) L247–251。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GRK-05｜原本Statusと限定受理

- 旧原文範囲：[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L93-L99) L93–99。
- 原Severity表現（そのまま引用）：

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L94) L94

> - **重大度:** Editorial

### 対応判断の根拠となる旧原文

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L96) L96

> - **問題:** 原本 `NOT REVIEW-ACCEPTED` と後続条件付き受理の併存はパケットで説明済み。対象誤認防止は運用依存。

### 今回の対応・条文照合（Work分析）

FG06-GPT-RR-04／CLD3-04に関連。

固定状態とOD-12範囲の別欄管理を継続。無断のヘッダ更新・正式受理拡張は行わない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L4-L17) L4–17／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L325-L339) L325–339。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## GRK-06｜旧GrokレビューのSHA未計測

- 旧原文範囲：[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L101-L106) L101–106。
- 原Severity表現（そのまま引用）：

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L102) L102

> - **重大度:** Editorial

### 対応判断の根拠となる旧原文

[Grok_Rev4_FG06_20261025.md](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/reference/prior_reviews/Grok_Rev4_FG06_20261025.md#L104) L104

> - **問題:** 本レビューの対象同一性は raw 本文に依拠。表示 SHA とのバイト一致は未証明。

### 今回の対応・条文照合（Work分析）

GRK-LIM-02と類似・関連だが別の受領事象。

旧件は原Rev.4（d1b6…）、新件は統合候補（4a3b…）を扱う。当時Grok本人の未計測を、今回の保存ファイル計測や補完証拠でPASSへ書き換えない。

対象：[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L7-L14) L7–14／[統合候補](https://github.com/spe-flatvat/SPE/blob/789403ae904594a0973ed7c7a142745a75595320/reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md#L325-L337) L325–337。

原文の所在・該当文言はVERIFIED。意味上の対応はWorkの分析（E3）、承認根拠E1未回収部分はNOT VERIFIED。Dispositionは未確定。

## 3. 旧3修復の比較事実

| 旧問題 | 原Rev.4 → 3DEC → 統合候補 | 結論の限界 |
|---|---|---|
| CC-01別承認例外 | 原Rev.4 L56のwithout separate approvalを3DEC L56で除去。統合候補L59へ維持 | 例外の除去を文字列・本文で確認。原承認・正式Closeではない |
| CC-03明示fail-closed | 原Rev.4 L102にない明示文を3DEC L102で復元。統合候補L105へ維持 | 復元を確認。CLD2-01のその他の要求は別 |
| CC-08全条件検証 | 原Rev.4では包括句なし。3DEC L283に挿入、統合候補L286へ維持 | 比較操作自身のMUSTを確認。CLD2-02の名称・権限境界は別 |

この3件に対応する旧IDは7件（CLD-01、GPT6-FG06-03／CLD-02／GRK-02、GPT6-FG06-01／CLD-03／GRK-03）。「7件の文言対応確認」を「7件Close」として扱わない。DEC-CANDのE2記録は後続の復元方針の説明として使用し、過去の変更承認を遡及証明しない。

## 4. 継続CLD2系列（別集合・原回答未取得）


[M19_25_Claude_FG06_Limited_Rereview_Independent_Review_DRAFT.md](https://github.com/spe-flatvat/SPE/blob/d36ae4428d35105bed4fbedc72c7db1500330655/reviews/M19-25/FG06_Limited_4AI_Response_Fix_20261029/M19_25_Claude_FG06_Limited_Rereview_Independent_Review_DRAFT.md#L67-L72) L67–72

> ### 前回から継続（統合候補では未対応、重複計上しない）
> - CLD2-01（CC-03 `met/not_required` 行：`no switch;` の欠落、「Persistent」の基準と理由コードの未指定）：Minor。
> - CLD2-02（CC-08 L286：検証MUSTの主体と、`eligible` 付与の主体が別名称）：Minor。
> - CLD2-03（CC-01 L55：`select only` の「only」の欠落）：Minor。
> - CLD2-05（Invariantsが復元・追加した義務を直接はカバーしない）：Editorial。
> - CLD2-04（候補の自己識別）：CLD3-04に統合・部分改善。

| 継続ID | CLD3中の表記 | 統合候補との限定照合 | 証拠・処分 |
|---|---|---|---|
| CLD2-01 | Minor。no switch、Persistentの基準・理由コード | L105にfail-closed、L96／98に発効・Gate B制限がある。Persistentや理由コードの詳細化は実装契約との境界。本文に新IDや閾値を創作しない | 原CLD2未取得。NOT VERIFIED、追加計数・Closeなし |
| CLD2-02 | Minor。全条件検証とeligible付与の主体名 | L276／278／431は個別eligibleの指定操作、L286／437は比較操作・相互比較可能性。機能分離があるため、名称差だけで権限矛盾とは断定できない。プロセスの対応を別途追跡する余地 | 同上 |
| CLD2-03 | Minor。select onlyのonly欠落 | L55は明示政策を選択、L57は捏造禁止。R-06 E2レシートL13はonly相当追加不要と記録する。レシートを無視して自動復元せず、原報告・採用案・原裁定の照合をOwnerへ留保 | 同上。裁定衝突と断定せずE1未取得留保 |
| CLD2-04 | CLD3-04に統合・部分改善との説明 | Workはその統合を実行せず、系譜上の参照として保持 | 元Severity・全文は原回答未取得のため断定しない |
| CLD2-05 | Editorial。Invariantsが復元・追加義務を直接カバーしない | 29件を全制御規範の網羅的テスト一覧とはみなさない。B5に本文との参照表を作り、未記載の検証命題を将来V&V設計候補として区別 | 原CLD2未取得。テストPASS・追加採用なし |

これは範囲内のCLD3参照の照合であり、CLD2原報告の全面再監査ではない。必要な原本を追加取得する場合はOwner指示に従う。

## 5. 証拠・時点を混同しない事項

- 旧GRK-06と新GRK-LIM-02は、同じ「SHA未計測」という類型でも別レビュー・別候補。片方の後続取得を他方の当時の自己検証へ転記しない。
- 旧Status／OD-12の問題と、新候補のNOT FOR DISPATCH等の履歴表示は関連するが同じ承認行為ではない。OD-12の条件付き範囲は拡張しない。
- Gemini旧原回答L11／14には6D35の5件をFG05-N01〜N05と結び付けた表現がある。両集合を同一視せず、同回答自身の独立新規IDはGEMINI-01のみとして追跡した。この由来の混同を引き継がない。
- 旧crosswalkの「未裁定・継続」等は作成当時の記載。後続の裁定レシート・本文対応を別の列で示し、原表を上書きしない。
