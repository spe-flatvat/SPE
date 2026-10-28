# SPE M19–25｜FG-06 独立再レビュー報告（Claude）

Packet ID：`SPE-M19-25-FG06-REREVIEW-3DEC-20261027-DRAFT-01`
区分：独立レビュー報告のみ。Review Acceptance・Finding Close・Canonical化・Freeze・DecisionLog更新・GitHub書込みは行わない。M19–25／RP-023 HOLDは継続。最終裁定権限はOwner。

## 0. 受領記録（本文レビューの証拠とは分離して記録）

- レビュー担当：Claude（`claude-sonnet-5-5`）／実施：2026-10-28（JST）
- 取得経路：固定commit `13c24ae8beb917289691a52f45cdd0beaeda02f9` をgitで取得・checkout（HEAD一致確認済み）。実ファイルの実バイトを使用。
- 他AIの**今回**の再レビュー回答：参照していない。`prior_reviews/` の旧4AI原回答は、共通パケットが指定する証拠資料として、候補本文と原本の比較を先に行ってから読んだ。

| 項目 | 結果 |
|---|---|
| 配布23ファイル | 全て存在・取得可。SHA256SUMS記載22件は `sha256sum -c` で全件OK、一覧に過不足なし |
| 評価対象 `inputs/FG06_CAND_Rev4_3DEC.md`（38,214 bytes、532行） | 実バイトSHA-256 `fce55ac8...b848` が指定値と一致 |
| 比較原本 `inputs/FG06_ORIG_Rev4.md`（37,939 bytes、530行） | `d1b6e64c...` 一致 |
| 3変更差分 `inputs/FG06_DIFF_3DEC.patch` | `3a1235ed...` 一致。原本にpatchを適用すると候補と**バイト単位で一致**（`fce55ac8...`） |
| 配布ZIP `9559c222...` | **未検証**（ZIP自体は入手しておらず、展開済み23ファイルで同一内容を確認） |
| 変更局所性 | 独立に `diff` で確認。**変更は3か所のみ**（候補 L56、L102、L282–283）。CRLF混入なし。STOP条件には該当しない |

**受領記録上の差異（本文評価の根拠には使っていない）**
1. Request L20は「新配布セットへの実バイト同梱と版照合は未完了」と書くが、実際にはRev.2・FG-05・Step 6D-35・Workflow・DecisionLogは `old_packet/` に同梱され、SHA256SUMSと一致した。Request側の記述が古い。
2. Request・Packet・Checklistの「未配布・Owner承認待ち」表示は作成時点の状態（Owner案内のとおり）。
3. `FG06_4AI_CROSSWALK_DRAFT.md` は旧4AI原回答の実バイトSHA未照合と書くが、Packet・Manifestは照合済みと書く。文書間で状態が食い違う。私の確認範囲は、同梱ファイルがSHA256SUMSと一致することまで。うちClaude原回答は私の保存版とバイト同一。ChatGPT／Gemini／Grokの3件が回答時の原本と同一かは、独立には確認できない。
4. Step 6D-35転記と元Owner発言の逐語同一性、Owner原裁定の所在、E-03／E-04は**未検証**のまま保持する。

## A. Executive Verdict

**CONDITIONAL ACCEPT**（候補の規範品質に対する評価。Freeze承認ではない）

理由：
- 3変更は、いずれもRev.2の該当文と**逐語同一**の文言復元で、局所的・最小限である。CLD-01／CLD-02／CLD-03の指摘した欠落は、本文上は解消している。
- 3変更に起因する矛盾・新規回帰は確認できなかった。CC-03の復元文は、transient扱い、Gate B、依存切替、incumbent継続、多年度pendingと整合する。
- 残る指摘は、いずれもMinor／Editorialである。うち3件（CLD2-01、CLD2-03、CLD2-05）は3変更に起因せず、元のRev.4から存在する。
- 条件：正式Freezeの前に、(1)実質追加規範のOwner原裁定の照合（GPT6-FG06-02、GRK-01。未了で、未承認とは断定しない）、(2)3裁定自体の原記録の照合（本セットではDRAFTレシートのみ）、(3)下記Minor指摘のOwner判断、が必要。

前回の私のREVISE（CLD-01〜03のMajor3件が根拠）から判定を変える。変更の根拠は、その3件が本文上解消した点にある。

## B. Finding Register（新規）

ID接頭辞は `CLD2-`。既存のID・重大度は上書きしない。

### CLD2-01｜CC-03：復元行に残る周辺の曖昧さ
**Minor／解釈上のリスク／3変更に起因しない（Rev.2からの継続）**
- 対象：候補 L102（`met/not_required` 行）。
- 内容：(a) Rev.2 L57にあった `no switch;` が、復元後も行内に戻っていない（`met/pending` 行には `No switch` がある）。切替不可は L86–91（Decision=approvedを要求）から導けるが、行内では明示されない。(b) `Persistent` の基準が未定義。文脈上は「依存Gate B完了までに settle しない状態」と読めるが、本文には書かれていない。(c) 他行は `STOP_*` 系の理由コードを持つが、この行のfail-closedの理由コードは未指定。
- 根拠：Rev.2 L57 `Transient only while requesting Decision; no switch; MUST settle ... Persistent occurrence fails closed for the dependent switch.` と候補 L102 の対比。
- 影響：実装間で、持続判定の時点と記録される理由コードが分かれうる。
- 推奨：(3変更の局所性を保つなら次回改訂で) `no switch` の復元、持続の定義、理由コードの指定。
- Owner裁定：不要（編集で可）。
- 対応：CLD-01の残余。GPT6-FG06-05とも隣接。

### CLD2-02｜CC-08：復元した検証MUSTの主体が、適格性付与の主体と同一とは書かれていない
**Minor／解釈上のリスク／3変更に起因（復元文の接続）**
- 対象：候補 L283（復元文）、L273–275、L428、L434、L436。
- 内容：復元文の主体は「the comparison operation」。一方、`eligible` を付与できるのは「the designated comparison validation operation」（L273–275、L428）。L275は「successful validation」の後に付与するとするが、その validation の内容を定義していない。L283の全条件検証が、個別適格性の付与前にも要求されるのか、相互比較の確定段階だけなのかが、文面上は定まらない。Rev.2も同じ二名称を持つので回帰ではないが、復元によって検証義務が明示された今、帰属の曖昧さが目立つ。
- 追加：Rev.2にあった「契約が未承認・未評価・不合格なら公開を留保する」は、CC-08には残らず、L291（影響不能の場合）とL436（`successful required validation` なしでは進めない）の組合せで間接的に満たされる。同等だが、検証失敗→留保の連結は間接的。
- 推奨：L283に、「個別適格性の付与前に、指定された検証操作がこの検証を含む」または「相互比較確定段階のみ」のどちらかを明示する。
- Owner裁定：意図の確認（既存根拠照合で足りる可能性が高い）。
- 対応：GPT6-FG06-01／CLD-03／GRK-03の残余。

### CLD2-03｜CC-01：保護はRev.2と同等に戻ったが、`select only` の「only」が失われたまま
**Minor／確定的な文言差／3変更に起因しない（元のRev.4から存在）**
- 対象：候補 L52。
- 根拠：Rev.2 L27 `The controller MUST select only explicitly defined policy paths` ／ 候補 `MUST select explicitly defined policy paths`。
- 内容：「定義済みの経路のみ選ぶ」という排他性が、「定義済みの経路を選ぶ」という義務に弱まっている。L54（捏造禁止）、CC-03 L116（優先順位の捏造禁止）等で大部分は補われるため、実害は限定的。
- 推奨：`only` の復元、または排他性が他条項で担保されている旨の確認。
- Owner裁定：不要（編集で可）。ただし、元Rev.4での削除が意図的だったかは原裁定の確認が望ましい。
- 対応：Q2（Rev.2同等性）への回答として、「別承認例外の除去では同等に戻ったが、CC-01全体の完全同等ではない」という留保。

### CLD2-04｜候補の自己識別と権限根拠の記載が更新されていない
**Minor／証拠・トレーサビリティ／3変更に起因**
- 対象：候補 L1、L4、L10、L11。
- 内容：候補のヘッダは原本と同一で、`Rev.4 Candidate`、`Immediate source: Rev3`、`NOT REVIEW-ACCEPTED` のまま。Authority basis（L11）にも、今回の3裁定（案A）は含まれない。つまり、バイト列の異なる2本の文書が同一の自己ラベルを持ち、3変更の権限根拠は文書自身には記録されず、Packet内の**DRAFTレシート**にしかない。Requestの局所性要件（3か所以外の変更はSTOP）のもとでは、ヘッダ追記自体が禁止される。
- 推奨：本文は変えず、外部の台帳（Manifest／受領記録）で、候補SHAと3裁定の対応を固定する。正式な版ラベルは、Freeze前の別工程で付与する。
- Owner裁定：3裁定の原記録（Ownerの案A選択）の所在を、Ownerが照合する。本セットでは、Request L12とPacket §2の記述以外にその原記録を確認できなかった。**未検証**。
- 対応：GPT6-FG06-07／CLD-06／GRK-05（固定状態の別管理）と隣接。FG05-N05。

### CLD2-05｜29 Invariantsが、復元した義務を直接はカバーしない
**Editorial／V&V網羅性／3変更に起因しない（Rev.2からの継続）**
- 対象：Invariants（候補 L462–490付近）。
- 内容：Invariant 5は `met/not_required` の transient 性までで、持続時のfail-closedは含まない。CC-08の全条件検証（L283）に対応するInvariantもない（26は影響再検証のみ）。CC-01の意味論非変更もInvariantにない（Rev.2も同様）。
- 推奨：次回改訂で、各MUSTにV&V対応を追加する（今回は局所性要件のため変更不可）。
- Owner裁定：不要。

## B-2. 既存20件の追跡（3裁定で自動Closeしない）

状態の区分：DIRECTLY ADDRESSED／POSSIBLY AFFECTED／UNCHANGED／NOT VERIFIED。

| 既存ID | 状態 | 備考 |
|---|---|---|
| CLD-01 | **DIRECTLY ADDRESSED** | 文言はRev.2と逐語同一。残余はCLD2-01。権限根拠は未検証 |
| GPT6-FG06-03／CLD-02／GRK-02 | **DIRECTLY ADDRESSED** | 例外句を除去し、Rev.2と同一の無条件禁止に復元。残余はCLD2-03、権限根拠は未検証 |
| GPT6-FG06-01／CLD-03／GRK-03 | **DIRECTLY ADDRESSED** | 全条件検証MUSTを復元（Rev.2と逐語同一）。重大度の相違（Major／Minor）は本文上は解消。残余はCLD2-02 |
| GPT6-FG06-05 | POSSIBLY AFFECTED | CC-03表が編集された。復元文は「切替」のみに限定され、L108–110（進行中のpendingは別評価）と矛盾しない。`not_required` は「現在有効な請求なし」（L75）なので、有効な多年度pendingは `pending` と読め、衝突しない。ただし単一のDecision値の境界の曖昧さは未解決 |
| GPT6-FG06-07／CLD-06／GRK-05 | POSSIBLY AFFECTED | 原本とバイトが異なる文書が同一ヘッダを持つ（CLD2-04）。本質は未解決 |
| GPT6-FG06-02／GRK-01 | **NOT VERIFIED**（CC-08の一部のみ POSSIBLY AFFECTED） | 実質追加規範の歴史的権限。3裁定の対象外。原裁定の照合が未了で、未承認とも断定しない |
| GPT6-FG06-04／CLD-04／GRK-04 | UNCHANGED | CC-04は未変更 |
| GPT6-FG06-06 | UNCHANGED | CC-04／CC-12は未変更 |
| GEMINI-01 | UNCHANGED | |
| CLD-05 | UNCHANGED | |
| GRK-06 | UNCHANGED | Grok原レビュー自身の証拠留保 |

FG05-N01：NOT VERIFIED。N02：DIRECTLY ADDRESSED。N03：DIRECTLY ADDRESSED。N04：UNCHANGED。N05：POSSIBLY AFFECTED（CLD2-04）。いずれも**Closeしない**。

## B-3. 必須質問への回答（要点）

1. **CC-03：** 復元された。transient扱い（L77）、表のintro（L95）、`Other combinations`（L106）、L108–110、incumbent継続（L128、L153）、観測契約失敗（L228：Decision請求禁止）と**矛盾しない**。観測契約が失敗してDecisionを請求できない場合に `met/not_required` が持続する経路を、復元文が閉じる点で、むしろ整合を高める。
2. **CC-01：** 別承認例外の除去により、M10／M14／M17／M18の保護はRev.2と同等。メタデータ条項の `unless separately authorized`（L58）はRev.2の `unless separately approved` と同等で、新規の衝突はない。完全同等ではない点はCLD2-03。
3. **CC-08：** 全条件検証MUSTが復元され、ID／version（L281、L287）、影響再検証（L289–291）、CC-13（L428、L434、L436）と矛盾しない。主体の曖昧さのみCLD2-02。
4. **変更局所性：** 3か所に限定（独立確認済み）。MUST／MUST NOT／MAY、状態表の他行、Reason taxonomy、Invariants、Freeze boundaryに意図しない変更はない。
5. **横断整合性：** CC-01〜13、A→C→B、2026初期状態と2027継承、Decision／Trigger／予約／比較／HOLDに新たな矛盾はない。架空の2025最終状態は導入されていない。
6. **残余Finding：** B-2のとおり。
7. **歴史的権限：** 未取得は未承認の根拠にならない。レビュー時は内容の妥当性を評価できるが、承認の断定はできない。Freeze時は、CC-09の照合か、Ownerによる個別裁定が必要。
8. **新規回帰：** 3変更に起因する新規の回帰は検出していない。3変更に起因するのはCLD2-02（接続の曖昧さ）とCLD2-04（トレーサビリティ）のみ。
9. **Rev.2との規範保存：** Cを参照。

## C. Normative Preservation Assessment（18セクション）

REPLACEは、承認根拠を検証できないため、承認済み変更の意味では使わない。

| セクション | 分類 | 所見 |
|---|---|---|
| §0 | KEEP＋ADD/REVIEW | F3政策source境界の追加。承認根拠は未検証 |
| CC-01 | KEEP＋REVIEW | 保護はRev.2と同等に復元。`only` の欠落（CLD2-03） |
| CC-02 | KEEP＋ADD | enum不変。予約の履歴再構成の追加 |
| CC-03 | KEEP＋ADD/REVIEW | 表は復元。多年度pendingは追加で承認根拠未検証。行内の残余（CLD2-01） |
| CC-04 | KEEP＋ADD/REVIEW | 3変更の対象外。試行／確定／異常年度末は追加で、承認根拠未検証 |
| CC-05 | KEEP＋ADD | 対象外 |
| CC-06 | KEEP＋ADD | 対象外 |
| CC-07 | KEEP＋ADD | 対象外 |
| CC-08 | KEEP＋ADD/REVIEW | 検証MUSTは復元。ID／再検証の追加は承認根拠未検証。主体の曖昧さ（CLD2-02） |
| CC-09 | KEEP＋ADD/REVIEW | 対象外。照合義務は維持 |
| CC-10 | KEEP | 実質同一 |
| CC-11 | KEEP＋ADD | 対象外 |
| CC-12 | KEEP＋ADD/REVIEW | 対象外 |
| CC-13 | KEEP＋ADD | 復元したCC-08と整合 |
| Reason taxonomy | KEEP | 変更なし |
| Invariants | KEEP＋ADD/REVIEW | 変更なし。復元義務への対応が弱い（CLD2-05） |
| Freeze boundary | KEEP＋ADD | 変更なし |
| Editorial notes | KEEP＋ADD | 変更なし |

機械的な文単位の照合（Rev.2のMUST／MAY文を候補と突合）でも、3変更以外の新たな欠落は検出していない。再編に伴う文の分割・言い換えがほとんどで、上記以外に実質的な弱化は見つかっていない。

## D. Residual Risks

| 区分 | 内容 |
|---|---|
| 権限 | 実質追加規範（多年度pending、再試行・年度末・異常年度末、比較再検証、予約とDecisionの寿命分離、新Invariants）のOwner原裁定が未照合。3裁定自体も本セットではDRAFTレシートのみ |
| 証拠 | E-03／E-04は未検証。Step 6D-35転記の元発言との同一性は未検証。旧4AI原回答3件の原本との同一性は独立には未確認。ZIP SHA-256は未検証 |
| 仕様 | CLD2-01〜03。2026切替候補とGate C（CLD-04系）、多年度pendingの境界（GPT6-FG06-05）は未解決 |
| 実装 | atomic／idempotent、回復・再初期化の機構は別契約。比較契約の承認主体は本文に明記がない（形式化は別工程） |

## E. Review-to-Freeze Conditions

**今回のレビューで確認できたこと：** 変更局所性（独立に確認）、3変更の本文上の妥当性、矛盾・回帰の不在、既存20件の状態の追跡。

**Freeze前にOwnerが別途判断・実施すべきこと（本報告は実行・宣言しない）：**
1. 実質追加規範の原裁定の回収・照合。回収不能な部分は、二次証拠の採用可否を個別に裁定する。
2. 3裁定（案A）の原記録の照合と、候補SHAとの対応の外部台帳への固定（CLD2-04）。
3. CLD2-01〜05の採否。編集で足りるものは次回改訂で、本文変更は再レビューを伴う。
4. 未解決の既存Finding（2026切替候補、多年度pendingの境界、予約と異常年度末、Gate B記録状態、ヘッダ状態）の処分。
5. 4AIの今回回答の統合、Workflowに沿う合意またはwaiver、Owner-confirmed snapshot、DecisionLog対応。
6. Review Acceptance、Finding Close、Canonical化、Freeze、GitHub書込みは、それぞれ別の明示的承認による。HOLDの解除もOwner判断。

## 独立性・権限の記録

本報告は、固定commitのファイル以外には依拠していない。ファイルの変更、commit、push、PR作成は行っていない。Findingの採用、重大度の確定、後続工程への移行はOwnerに留保される。
