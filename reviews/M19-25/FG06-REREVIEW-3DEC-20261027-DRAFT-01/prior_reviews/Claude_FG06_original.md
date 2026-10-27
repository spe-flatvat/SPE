# SPE M19–25｜FG-06 独立レビュー報告（Claude）

## 0. レビュー担当・実施日時・独立性

- レビュー担当：Claude（model ID: `claude-sonnet-5`）
- 実施日時：2026-10-25（日本時間、FG-06A-04受領確認の直後に実施）
- 独立性：本レビューは他AI（ChatGPT／Gemini／Grok）の今回回答を参照せず実施した。参照したのはFG-06共通パケット・Common Review Request・対象Rev.4・Rev.2・FG-05報告書・Step 6D-35転載・Workflow.md・DecisionLog.mdのみである。
- 本レビューはReview Acceptance正式化・Finding Close・Canonical化・Freezeのいずれも行わない。Ownerによる確認・保存を前提とする独立評価である。

## 1. 受領・証拠状態（本レビュー本文評価の前提）

| 対象 | 実バイトSHA-256（独立計算） | 期待値との一致 |
|---|---|---|
| `inputs/M19_Control_Contract_v0.4_DRAFT_Rev4_EDITORIAL_CANDIDATE.md` | `d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e` | 一致（指定値・SHA256SUMS.txt記載値と一致） |
| `inputs/M19_Control_Contract_v0.4_DRAFT_Rev2.md` | `6a55197c1e530fbbcd222f859107573c04326254c1dfb6524b7ab001d7b58cea` | 一致（SHA256SUMS.txt記載値と一致） |
| 元配布ZIP（`807e6634...`） | — | 未検証（展開済み個別ファイルからは原理的に再現不可。配布Manifest自身も外部の作成完了報告で照合する対象と明記） |

対象はコミット `b81f7057e84ad285e2e87e3263bffe6f31f8f9a9` から直接git checkoutした実ファイルであり、GitHub上の表示（レンダリング済みプレビュー）ではない。

## 2. Executive Verdict

**REVISE**

Critical（制御矛盾として致命的）に相当する指摘は認定しない。しかし、Rev.2→Rev.4の間で独立に検出した**新規のMajor指摘（CLD-01：CC-03の明示的fail-closed文の無断削除）**、および先行監査FG-05のMinor評価に対して**独立に重大度を引き上げたMajor指摘（CLD-03：CC-08比較契約検証義務の実質的弱化）**が存在する。これらは文言の整理ではなく規範的な強度変化であり、Owner裁定または原文修正のいずれかを要する。

本評価は候補の**規範品質**に対するものであり、Freeze承認ではない。歴史的承認根拠（D25系列、O/GATE/COMP/R/6D27/6D38等）の原裁定照合は本レビューの対象外・未実施であり、E-03／E-04は未検証のまま維持する。

## 3. Finding Register

Finding IDは `CLD-` を接頭辞とし、既存のFG05-N0x・6D35-F-0xのIDを上書きしない。

### CLD-01｜CC-03：met/not_requiredの明示的fail-closed文がRev.4で削除されている（新規・独立検出）
**重大度：Major**

- **対象箇所：** CC-03状態表、`met`/`not_required`行。Rev.2 L57、Rev.4 L102。
- **Rev.2原文：**
  > `met` | `not_required` | **Transient only** while requesting Decision; no switch; MUST settle to `pending`, `approved`, or `rejected` before Gate B completion. **Persistent occurrence fails closed for the dependent switch.**
- **Rev.4原文：**
  > `met`|`not_required`|Transient only while requesting Decision; MUST settle to `pending`, `approved`, or `rejected` before dependent Gate B completion.
- **問題と成立条件：** Rev.2はこの一時状態が未解消のまま持続した場合、当該依存する切替についてfail closedとする帰結を**行内に明示**していた。Rev.4はこの一文を削除し、「settleしなければならない」という義務のみを残して、持続した場合の制御上の帰結を本行では明示していない。CC-05の一般的な依存範囲別fail-closed原則やInvariant等から類推すれば同じ結論に到達できる可能性はあるが、少なくとも本行単体では規範の強度が弱まっている。これは編集上の整理ではなく、既存の明示的保証の削除である。
- **Rev.2との関係：** 直接の後退（regression）。FG-05の4.2差分表はCC-03全体を「KEEP＋ADD/REVIEW」としたが、このより具体的な一文削除自体はFG-05の指摘（FG05-N01、多年度pending関連）に明示的に含まれていない。
- **判断に必要な正確な根拠引用：** 上記Rev.2 L57およびRev.4 L102（L96–106付近の状態表全体）。
- **推奨修正（提案のみ）：** 当該行に「Persistent occurrence fails closed for the dependent switch（またはそれと同等の明示文）」を復元する。あるいは、CC-05の一般原則がこの行の持続状態に適用されることを本行から明示的に参照する一文を追加する。
- **Owner裁定の必要性：** 既存根拠照合（この削除が意図的なOwner裁定による整理か、単なる編集漏れか）を要する。新裁定は、削除を正式に承認するか復元するかの二択。
- **FG05-N01〜N05との対応：** 対応なし（独立に検出した新規論点）。
- **区分：** 確定的問題（Rev.2とRev.4の文言差分そのものは確定）。その帰結がCC-05等の一般原則で実質的に代替されているかは解釈上のリスク。

### CLD-02｜CC-01：既存モジュール意味論保護への「別承認」例外追加
**重大度：Major（FG05-N02と同一論点、独立に到達）**

- **対象箇所：** CC-01、Rev.2 L27 → Rev.4 L56。
- **Rev.2：** `It MUST NOT modify M10/M14/M17 calculation semantics or M18 evaluation semantics.`（無条件禁止）
- **Rev.4：** `It MUST NOT modify M10/M14/M17 calculation semantics or M18 evaluation semantics without separate approval.`（条件付き禁止）
- **問題と成立条件：** 無条件の禁止から、別途承認があれば変更を許容する条件付き禁止への変更。現時点での無承認変更は依然禁止されているが、将来の例外経路を新設した点で権限境界の実質変更であり、既存のRev.2禁止と同等とは言えない。
- **Rev.2との関係：** 実質変更（REPLACEに相当する可能性があるが、承認根拠未確認のためREVIEWとする）。
- **判断に必要な正確な根拠引用：** 上記2行。
- **推奨修正：** この例外句が既存Owner裁定（D25系列等）の射程内にあるかを確認し、射程内であれば根拠IDを本文に明示する。射程外であればRev.2の無条件禁止へ復元するか、別契約への委譲として明示的に分離する。
- **Owner裁定の必要性：** 既存根拠照合を第一に試みる。回収不能な場合は新裁定が必要。
- **FG05-N02との対応：** 完全対応（同一論点、独立に同じ結論へ到達）。
- **区分：** 確定的問題（文言差分）＋証拠不足（承認根拠未確認）。

### CLD-03｜CC-08：比較契約検証義務が「契約の自己宣言」へ縮小された可能性（FG05-N03の重大度を独立に引き上げ）
**重大度：Major（FG-05はMinor／条件付きMajorとしたが、本レビューは独立にMajorと評価する）**

- **対象箇所：** CC-08、Rev.2 L103 → Rev.4 L281, L285。
- **Rev.2：**
  > The comparison operation **MUST validate** the approved comparison contract's evaluation period, metric definitions, units, baseline and initial-state compatibility, and evaluation methodology, **plus all expressly required contract conditions**.
- **Rev.4：**
  > The approved comparison contract **MUST identify** an immutable contract ID and version, evaluation period, metrics, units, baseline and initial-state compatibility, methodology, and required dependencies.
  >
  > Before formal finalization or publication, the comparison operation MUST verify that the individual eligibility and mutual comparability determinations apply to the **exact approved contract and dependency versions**.
- **問題と成立条件：** Rev.2は比較操作（comparison operation）自身に、評価期間・指標定義・単位・ベースライン適合性・方法論・「明示的に要求される全契約条件」を**実際に検証する**義務を課していた。Rev.4では、これらの項目は契約が**識別・記載すべき**項目へと移動し、比較操作に残る検証義務は「正確な契約・依存バージョンに適合しているか」という**バージョン一致の検証**のみである。これは文言整理ではなく、「内容の実質検証」から「バージョンの形式一致検証」への**検証義務の縮小**である。CC-13 L432–434が比較判定成功を要求する点、CC-08 L289が非影響確認できない場合に出版を留保する点は維持されているため、全面的な検証義務の削除とまでは言えないが、"metric definitions"や"all expressly required contract conditions"のような、契約内容そのものの実質検証を明示的に要求する語が本文から消えている。
- **FG-05との不同意点：** FG-05はこれをMinor（条件付きMajor再評価）とし、「実装が列挙条件を検証しない解釈ならMajorへ再評価」と留保付きで評価した。本レビューは、Rev.4の文言そのものが「契約がMUST identify」という宣言義務と「比較操作がMUST verify（バージョン一致のみ）」という縮小された検証義務に明確に分離されている以上、解釈上のリスクではなく**現在の文言自体がすでに縮小している**と判断し、独立にMajorへ引き上げる。
- **Rev.2との関係：** 実質後退の可能性が高い変更（REVIEW、REPLACEとして未承認）。
- **推奨修正：** 比較操作に、契約が識別する各項目（評価期間・指標定義・単位・ベースライン適合性・方法論・必須依存条件）を**実際に検証する**義務を明示的に復元するか、Owner裁定によりバージョン一致検証への縮小を明示的に承認し、その理由を記録する。
- **Owner裁定の必要性：** 新裁定（意味保存の意図確認、または縮小の明示的承認）。
- **FG05-N03との対応：** 同一論点、重大度評価のみ独立に相違。
- **区分：** 確定的問題（文言構造の変化）＋解釈上のリスク（実装時にどちらで解釈されるか）。

### CLD-04｜CC-04／CC-05：2026年の切替候補とGate Cの「preceding-year state」の関係が未定義（FG05-N04と同一論点、独立に到達）
**重大度：Minor**

- **対象箇所：** CC-04 L147、CC-05 L200。
- **問題：** CC-04は2026をBaseline Initial-State Contractによる初期化、2027以降をGate Aによる「実際に確定した前年度状態」の検証と明確に区別する。一方、L145の「Year-entry sequence」は2026–2055の全年次に一律に適用され、L147の切替候補に対するGate C検証は「actual authorized preceding-year state」を要求する。2026年に切替候補が存在しうる場合、2026年には定義上「preceding-year state」が存在しないため、Gate CがBaseline Initial-State Contractをどのように代替的に検証するのかが本文上で明示されていない。
- **推奨修正：** 2026年に切替候補が許容されるか否かを明示する一文を追加する。許容する場合は、Gate CがBaseline Initial-State Contractをpreceding-year stateの特則として検証する旨を明記する。許容しない場合は、2026年の切替候補自体を無効とする一文を追加する。
- **FG05-N04との対応：** 完全対応（同一論点）。
- **区分：** 解釈上のリスク（境界条件の曖昧性。確定的な矛盾ではない）。

### CLD-05｜CC-05：Gate AまたはGate Cが失敗した場合のGate B記録状態が明示されていない（新規・独立検出）
**重大度：Minor／Editorial**

- **対象箇所：** CC-05 L206–218。
- **問題：** L210の規定は「Gate AとGate Cが通過し、正式なGate Bチェックポイントに到達し、Gate Bが非適用と確定した場合」にNOT_APPLICABLEを記録する義務を定める。L214は「正式チェックポイントに到達しなかった場合」にNOT_EVALUATEDを維持する義務を定める。しかし、Gate AまたはGate C自体が失敗した結果としてGate Bの正式チェックポイントに到達しなかった場合が、この「到達しなかった場合」に含まれることは文脈上推測できるが、本文で明示的に述べられていない。
- **推奨修正：** 「Gate AまたはGate Cの失敗によりGate Bの正式チェックポイントに到達しなかった場合も、評価状態はNOT_EVALUATEDのまま維持される」旨を一文で明示する。
- **区分：** 解釈上のリスク（文脈上は解決可能と考えられる軽微な完全性の欠落）。

### CLD-06｜冒頭ステータス表記とOD-12条件付き受理の併記（FG05-N05と同一論点）
**重大度：Editorial**

- 対象ファイルの冒頭 `NOT REVIEW-ACCEPTED` は固定時点のバイト列の記述であり、今回のOwner指示によるOD-12条件付きReview Acceptanceとは別管理する必要がある。FG-05の見解に同意する。配布文書（本Common Review Request等）では両者が別表示されており、現時点で誤解を招く表示はないと判断する。
- **区分：** 編集上の明確化のみ。現状、確定的な問題は生じていない。

## 4. FG05-N01〜N05への個別応答（Common Review Request §3必須論点）

| ID | FG-05の重大度 | 本レビューの応答 |
|---|---|---|
| FG05-N01（多年度pending等の実質追加の承認根拠未確認） | Major | **限定同意。** 多年度pending処理（CC-03）、試行/異常年度末の区別（CC-04）、予約/Decision寿命分離（CC-12）は、いずれも本レビュー担当が先行して実施したRev.2独立レビュー（N-1, N-2, N-3）で指摘した未解決論点に直接対応する追加であり、**規範内容としては内部整合的**と判断する。残る論点は純粋に**承認根拠（これらの具体的文言をOwnerが実際に承認したか）**であり、これはFG-05と同様、本レビューでも原裁定照合ができておらず未検証のまま維持する。内容の健全性と承認provenanceの未確認は区別して記録すべきである。 |
| FG05-N02（CC-01別承認例外） | Major | **同意。** CLD-02として独立に同一結論に到達した。 |
| FG05-N03（CC-08比較契約検証の強度） | Minor（条件付きMajor） | **不同意（重大度のみ）。** CLD-03として独立にMajorへ引き上げる。文言構造そのものが検証義務を縮小しているとみるため、解釈上のリスクに留めず確定的な文言変化として扱うべきである。 |
| FG05-N04（2026切替候補とGate C） | Minor | **同意。** CLD-04として独立に同一結論に到達した。 |
| FG05-N05（冒頭状態とOD-12の別管理） | Editorial | **同意。** CLD-06として記録。 |

## 5. Normative Preservation Assessment（全18セクション）

複数分類可。REPLACEは承認根拠未検証のため、原則「置換内容確認済み・承認根拠未検証」として記録する。

| セクション | 分類 | 根拠 |
|---|---|---|
| §0（文書状態・定義・namespace） | KEEP＋ADD | F3政策source境界（D25-01拡張）の追加は健全。既存定義・原則は維持。 |
| CC-01 | KEEP＋REVIEW | CLD-02。無条件禁止から条件付き禁止への変更、承認根拠未検証。 |
| CC-02 | KEEP＋ADD | 6ドメイン・enum値はRev.2と完全一致。予約の順序付き履歴復元義務は健全な追加。 |
| CC-03 | KEEP＋ADD＋**REVIEW（新規）** | 多年度pending条項は健全な追加だが、CLD-01（met/not_required行のfail-closed文削除）により単純なKEEP＋ADDとはしない。 |
| CC-04 | KEEP＋ADD＋REVIEW | 2026初期化・継続義務はKEEP。試行/確定/年度末の分解・異常年度末（6D38-01）は健全なADDと評価するが、承認根拠（Authority basis）の個別照合はREVIEW。CLD-04の境界条件も残る。 |
| CC-05 | KEEP＋ADD＋REVIEW（軽微） | Gate B適用性・地点・結果の分離は健全なADD。CLD-05（Gate A/C失敗時のGate B記録の明示性）は軽微なREVIEW。 |
| CC-06 | KEEP＋ADD | 非先取り原則は完全維持。Gate C事前検証の権限限界明示は健全な補強。 |
| CC-07 | KEEP＋ADD | stop_path/branch、HOLD非状態の区別を維持。自然言語holdのenum解決義務は健全な明確化。 |
| CC-08 | KEEP＋**REVIEW（重大度引き上げ）** | CLD-03。契約の自己宣言義務への移行は実質的な検証義務の縮小とみる。 |
| CC-09 | KEEP＋ADD＋REVIEW | 監査record拡張は健全。Governance traceability拡張（D22/23/24照合等）は維持されているが、個別裁定との照合未了。 |
| CC-10 | KEEP | Rev.2と実質同一。差分なし。 |
| CC-11 | KEEP＋ADD | 観測妥当性分離は維持。新規Decision/予約作成禁止の追加は健全。 |
| CC-12 | KEEP＋ADD | 予約寿命分離・target-year Gate失敗の扱いは本レビュー担当の先行Rev.2レビュー（N-2）への対応として健全。 |
| CC-13 | KEEP＋ADD | 比較適格性の権限構造を維持。監査義務の補強は健全。 |
| Reason taxonomy | KEEP | 全例示を維持。装飾差のみ。 |
| Invariants（17→29） | KEEP＋ADD＋REVIEW | 元17項目の主旨は維持。12項目追加は本文の実質追加（CC-03, CC-04, CC-12等）に対応するが、これらの承認根拠はCC本文と同じ留保を継承する。 |
| Freeze boundary | KEEP＋ADD | 除外範囲は維持。F3実政策承認・回復機構除外、二次証拠の別裁定要件の追加は健全。 |
| Editorial notes | KEEP＋ADD | 証拠留保（Claude日付、Grok未検証等）を維持。18件/5件の別管理を明示した点は健全。 |

## 6. Residual Risks

- **権限境界リスク：** CC-01の「without separate approval」例外（CLD-02）は、将来的にM10/M14/M17/M18の計算意味論が本契約の枠外で変更される経路を正式に開いた。この経路自体の悪用リスクは低いが、承認手続きの具体的な記録要件（CC-09の監査記録にこの種の承認がどう反映されるか）は本文に明記されていない。
- **証拠・承認provenanceリスク：** D25-01〜12、O-01〜05、GATE-01、COMP-01、R-01〜07、6D27-01〜02、6D38-01の個別内容と、Rev.4各条項との対応は、Authority basis（L11）の列挙のみでは独立に確認できない。E-03／E-04は未検証のまま維持する。
- **仕様境界リスク：** CLD-04（2026切替候補とGate Cの関係）は、現時点では実装が存在しないため実害はないが、将来の実装がこの曖昧性をどちらかに解釈した場合、解釈違いがそのまま制御上の相違になる。
- **実装境界：** atomicity/idempotence、recovery/reinitializationの具体的機構は本契約が意図的に対象外としている（Freeze boundaryに明記）。これは欠落ではなく明示的な範囲外化であり、残存リスクとしては低い。

## 7. Review-to-Freeze Conditions

今すぐレビュー可能な事項と、正式Freezeに必要な事項を区別する。

**レビュー時点で解消可能（原文修正または明示的なOwner裁定で足りる）：**
1. CLD-01：met/not_required行のfail-closed文の復元またはその削除が意図的である旨の明示。
2. CLD-02：CC-01の別承認例外の承認根拠確認、または文言の復元・限定。
3. CLD-03：CC-08比較操作の検証義務の復元、または縮小を明示的に承認した記録の追加。
4. CLD-04／CLD-05：境界条件の明示的な一文追加（いずれも軽微な文言追加で解消可能）。

**正式Freeze前に必要（原裁定照合・証拠回収・他AI結果統合を要する）：**
1. D22/D23/D24/D25系列、O/GATE/COMP/R/6D27/6D38の個別原裁定とRev.4条項の対応照合、またはOwnerによる回収不能部分の個別裁定。
2. 四AI独立レビュー原本（Rev.2 18件）の個別処分。本レビューはこれらを一括再処分していない。
3. Step 6D-35の5件の正式Finding Close（本レビューはFG-05同様、規範対応の確認のみで正式Closeは行っていない）。
4. Canonical DecisionLog対応の記録、GitHub書き込み・commit/push/PR、Freezeの各個別authorization。

本レビューはこれらのいずれも実行・宣言しない。Owner最終判断に委ねる。

## 8. 独立性に関する記録

本レビューは他AI（ChatGPT／Gemini／Grok）の今回回答を参照していない。FG-05は先行監査として参照したが、その結論（6D35-F-01〜05のPASS判定、CONDITIONAL READY判定）を拘束的前提とせず、CC-08（CLD-03）とCC-03（CLD-01）について独立に異なる評価・新規指摘に到達した。本報告のFinding IDおよび判断は、統合・重複排除工程（全回答取得後の別工程）まで保持される。
