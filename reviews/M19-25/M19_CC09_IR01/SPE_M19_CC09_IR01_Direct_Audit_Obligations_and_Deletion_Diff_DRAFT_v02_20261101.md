# SPE M19-CC09-IR-01｜CC-09削除後の残存監査義務・削除／置換／維持候補差分 DRAFT

- Status: **DRAFT / NON-CANONICAL / FOR OWNER PRE-REVIEW ONLY**
- 作成日: 2026-11-01
- 調査対象: `spe-flatvat/SPE`、参照Commit `857633d4f281a768187fc7122e44902dde47071a`、`reviews/M19-25/FG06-LIMITED-REREVIEW-DISTRIBUTION-20261028/required/M19_Control_Contract_Integrated_Candidate_DRAFT.md`
- Git blob SHA: `09b8d58e7f354bf09f8c19b812075e7e3c825c76`
- 注意: この参照版は **INTEGRATED DRAFT / NON-CANONICAL**。M19-CC09-IR-01の正式な配布固定版ではない。本文のSHA-256実バイト照合・他の改訂版との全差分確認は本調査では未実施。
- 権限: 読取・分析・新規DRAFTのみ。既存原本変更、Owner裁定、GitHub書込、Freeze、HOLD解除なし。

## 1. 判定原則

「削除」はCC-09固有の過剰な監査レコード・統治来歴の強制照合を外す候補。「置換」は必要最小限の**業務状態の記録**に限定。「維持」は実行制御の正当性、比較の正確性、予約の重複防止など、監査認証ではなく動作安全性に必要な条件を残す候補。分類は**提案**であり承認ではない。

**重要な分離**: (a) Owner裁定レシート、(b) シミュレーション実行・比較の業務記録、(c) 歴史的チャット原証拠の追加認証は別物。(a)は最小レシートで足りる候補、(b)は必要な操作結果を有限に記録、(c)は一般的な必須条件にしない。

## 2. CC-09自身の削除・移設候補

| ID | 原文所在・要求の要旨 | 候補 | 代替先／理由 |
|---|---|---|---|
| 09-01 | 3種類の監査レコードに多数の属性を一律MUST | **削除** | 汎用の3分類監査義務は廃止。操作別の最低限の業務記録に置換するなら個別条項で定義 |
| 09-02 | 全参照をimmutable版／digestへ解決 | **置換** | 計算契約・比較契約等の実行入力に限り、既存の版参照を維持。過去裁定の原証拠の完全認証へ拡張しない |
| 09-03 | 監査記録append-only、修正は新規連結レコード | **置換** | 確定済み計算・予約の非遡及性はCC-04/12等で維持。全統治記録に普遍的な追記専用方式を強制しない |
| 09-04 | 予約ID再利用禁止、年度末atomic/idempotent、部分失敗の成功扱い禁止 | **維持（移設）** | CC-04/12の既存動作規定と整合。CC-09削除で誤って失効させない |
| 09-05 | HOLD_COMPARISON発出時の詳細監査 | **置換** | CC-08/13に、発出時の対象・理由・状態参照の最小記録を残す。独立した監査認証義務は削除 |
| 09-06 | Owner裁定・4AI原文・ハッシュ・二次証拠等の区分義務 | **削除／限定置換** | レシートと二次資料の表示上の区別は推奨可能だが、原証拠完全回収を必須にしない |
| 09-07 | Governance traceability entryの多項目必須記録 | **削除** | 下記の暫定Owner裁定レシートに置換。独立タイムスタンプ検証は不要 |
| 09-08 | Freeze前D22/D23/D24、4AI原文、全Finding、DecisionLogとの照合 | **削除** | 全歴史照合を一律のFreeze条件にしない。別に既存Workflowが要求する正式レビュー・Owner判断の範囲は要確認 |
| 09-09 | 回収不能二次証拠のFreeze採用に別Owner裁定 | **削除候補** | 既存レシートの有効性を追加裁定に依存させない。具体的矛盾は個別照会 |
| 09-10 | 原回答の保存、要約追跡、DecisionLog等の別承認 | **一部維持** | 既存原文の黙示的改変禁止・書込承認境界は維持。原回答再回収を一律要件としない |

## 3. CC-09削除後に残る条項別の直接監査要求

| ID | 所在 | 残存要求（原文の意味） | 候補 | 限定的な候補修文の方向 |
|---|---|---|---|---|
| R01 | §0 `transition reservation` | append-only lifecycle evidence | **置換** | 予約の作成・解決イベントを識別可能に記録。全証拠の追加認証は不要 |
| R02 | CC-01 | controller emits attributable audit evidence | **置換** | 「各操作の結果・必要な権限参照を記録する」に限定 |
| R03 | CC-03 | Decision authority/evidence, pending status, historical identity | **維持／限定** | 裁定レシートIDを根拠参照とし、チャット原本追加認証を要求しない |
| R04 | CC-04 | retry attributable audit evidence; year-end actor/authority/prerequisites/resolution | **置換** | 年度処理の結果・再試行ID・完了状態の業務記録のみ |
| R05 | CC-05 | Gate B audit: applicability/checkpoint/result/reason; independently auditable gates | **置換** | Gate Bの判定結果を有限な構造化記録で残す。独立第三者認証は不要 |
| R06 | CC-07 | reasons/applicability/dependencies MUST be recorded | **維持** | STOP対象の誤拡大を防ぐ業務記録。証跡連鎖の完全証明は不要 |
| R07 | CC-08 | comparison results and withholding reasons MUST be audited; `HOLD_COMPARISON` under CC-09 | **置換** | 比較判定・保留理由を記録。CC-09参照を削除 |
| R08 | CC-10 | political Decision and source clause MUST be recorded | **維持／限定** | Owner裁定レシートIDまたは適切な決定参照を用いる |
| R09 | CC-11 | Trigger truth/evaluation/observation validity recorded | **維持** | 検証結果の業務記録であり歴史監査とは別 |
| R10 | CC-12 | scheduling and resolution append-only events; Gate failure recorded; replacement evidence | **置換** | 予約の一意性・有効性・解決履歴を保持し、監査用原証拠の完全回収は不要 |
| R11 | CC-13 | comparison validation contract ID, authority, outcome, references; audit outcomes | **置換** | 判定結果・必要参照を記録。専用監査認証を要求しない |
| R12 | Reason taxonomy | reason codes are audit attributes | **置換** | reason codes are operational result attributes |
| R13 | Invariants 17 | immutable end-to-end provenance and governance traceability | **削除／置換** | 計算入力と確定結果の再現に必要な版参照へ限定。統治履歴の全連鎖認証を削除 |
| R14 | Invariants 20, 24, 26, 27 | Gate B・年度末・比較監査の要件 | **一部維持／置換** | 動作検証は維持。監査義務は業務記録に限定 |
| R15 | Freeze boundary / Review and Freeze acceptance | 4AI、原裁定、Finding、DecisionLogのトレースとFreeze前照合 | **置換／要Owner判断** | 正式レビュー・Owner最終判断は維持。過去原証拠の完全照合を必須とする文言を除去 |
| R16 | Editorial / evidence notes | historical receipt date, Grok SHA等の追加reconciliation | **置換** | 未検証と表示して終了可能にする。再探索を自動必須化しない |
| R17 | CC-08、CC-13 | immutable comparison contract/result references, dependency impact revalidation | **維持** | 現行比較の整合性検証であり、Owner裁定の原証拠認証とは別 |
| R18 | CC-05、CC-12 | gate・reservation authorization evidence | **限定維持** | レシートID等で権限を参照。参照元の原チャット再取得を要求しない |

注: `MUST record`を全面廃止する案ではない。**有限の業務結果記録**と**無期限の裁定原証拠照合**を切断する案である。

## 4. 候補差分（提案、未適用）

### D-01 CC-09全節

```diff
- ## CC-09 — Three audit record classes, action audit, and immutability
- [CC-09本文全体：三分類レコード、統治証跡の完全照合、Freeze前再照合等]
+ [CC-09節を削除。番号の再割当ては行わず、CC-09をReserved / Deletedと表示するかはOwner裁定事項]
```

### D-02 CC-01

```diff
- ... determine execution and comparison dispositions, and emit attributable audit evidence.
+ ... determine execution and comparison dispositions, and record the resulting operational dispositions and their necessary references.
```

### D-03 CC-05 Gate B

```diff
- Gate B audit MUST separately identify applicability, whether the formal evaluation checkpoint was reached, and the evaluated result.
+ The Gate B operational result MUST identify applicability, whether the formal evaluation checkpoint was reached, and the evaluated result.
- Gate applicability, results, reasons, and dependency scope MUST be independently auditable.
+ Gate applicability, results, reasons, and dependency scope MUST be recorded for the affected operation.
```

### D-04 CC-08 / CC-13

```diff
- Comparison validation outcomes, publication dispositions, and withholding reasons MUST be audited whether or not `HOLD_COMPARISON` is issued.
+ Comparison validation outcomes, publication dispositions, and withholding reasons MUST be recorded as part of the comparison operation, whether or not `HOLD_COMPARISON` is issued.
- Issuance of `HOLD_COMPARISON` is MAY. If issued, it MUST be audited under CC-09.
+ Issuance of `HOLD_COMPARISON` is MAY. If issued, its target, reason, and related Comparison state MUST be recorded.
- Validation outcomes and withholding reasons MUST be audited even when no dedicated Control Action is issued.
+ Validation outcomes and withholding reasons MUST be recorded by the comparison operation even when no dedicated Control Action is issued.
```

### D-05 CC-04 / CC-12 / §0

```diff
- ... with attributable audit evidence.
+ ... with a recorded attempt identity, disposition, and necessary input references.
- A transition reservation is an immutable scheduling event with a unique ID and append-only lifecycle evidence ...
+ A transition reservation is an identifiable scheduling event with a unique ID and recorded lifecycle-resolution events ...
```

予約ID再利用禁止、確定済み年度結果の不変性、年度末atomic/idempotent、既存予約の有効性判定は変更しない。

### D-06 Invariant 17 / Freeze boundary

```diff
- Immutable end-to-end provenance and governance traceability.
+ Version-identifiable numerical inputs, finalized results, and operational decision references within the applicable execution scope.
- [全過去Owner裁定・4AI原文・Finding・DecisionLogの一律完全照合をFreeze要件とする部分]
+ [現行の対象候補に対する指定されたレビュー・Owner最終判断・必要な決定レシート参照を確認。歴史的原証拠の完全再取得は一律要件にしない]
```

### D-07 暫定Owner裁定レシート最小仕様（CC-09外の独立短文として提案）

**必須7項目（改訂候補 v0.2）:** `decision_id`（一意識別子）、`subject`（裁定対象）、`decision_result`（裁定内容）、`authority`（Owner）、`decided_at`（裁定日時）、`receipt_issued_at`（レシート発行日時）、`receipt_status`（`DRAFT` / `ISSUED`）。裁定対象版の特定に不可欠な場合のみ `target_ref` を追加必須とする案を4AIに比較評価させる。

**日時記録:** `decided_at` と `receipt_issued_at` は別項目とし、確認できる日時をタイムゾーン付きISO 8601で記録する。確認できない秒・日時を推定して補完しない。日時精度が分単位などに限られる場合は精度を明示する。日時の記録は必須だが、独立タイムスタンプ認証、チャット原本の再取得、自動ログスクリプトによる立証は一律に要求しない。未確認の過去裁定日時を埋めるために裁定を再認証する義務は設けない。

**書式例（架空、実裁定ではない）:**
```yaml
decision_id: EXAMPLE-OD-01
subject: CC-09 deletion proposal
decision_result: APPROVE
authority: Owner
decided_at: "2026-11-01T19:28:00+09:00"
receipt_issued_at: "2026-11-01T19:30:00+09:00"
receipt_status: ISSUED
```

**十分性:** 上記の裁定レシートを裁定の記録として受容し、チャット原本、独立タイムスタンプ、自動ログ、第三者証明、歴史的ハッシュ連鎖を一般的な有効要件にしない。レシートの欠落・内容矛盾・改変の具体的疑義は当該事項に限定してOwnerへ照会し、探索を無期限の一般要件にしない。RP-023正式仕様の採否は対象外、非遡及。

### D-08 CC-10 / CC-03

```diff
- ... attributable Decision authority and evidence ...
+ ... attributable Decision authority, identified by an applicable Owner decision receipt or expressly approved equivalent ...
```

上記は一般的な置換方向の例示であり、各Decisionが必ずOwner裁定かどうか、政策上の別の権限者が存在するかは別途確認を要する。Ownerレシートをあらゆる政治Decisionへ機械的に強制しない。

## 5. 4AIレビューに渡すべき限定論点

1. CC-09全削除と、直接依存条項の最小限の書換えで無限監査の再発を防げるか。
2. CC-04/05/08/12/13に残す業務記録は、数値・状態の安全性に必要かつ有限か。
3. Invariant 17およびFreeze境界の文言から、歴史的原証拠の全件認証義務が再発しないか。
4. 暫定レシートの7必須項目（`decided_at` と `receipt_issued_at` を含む）は必要十分か。日時記録と日時の独立認証を分離できているか。対象版の明示が必要な場合の最小条件は何か。
5. RP-023の未レビューをM19独立レビューの停止条件とせず、制度詳細をRP-023側に留保できるか。

## 6. 未検証・留保

- この参照候補と工程12/13の最終レビュー対象版の一致は未検証。**4AI配布前にOwnerが固定対象版を指定する必要がある**。
- 原条項以外の `docs/Workflow.md`、`docs/DecisionLog.md`、G10成果物等との完全な逐条横断照合は未完了。
- 本表の「削除／置換／維持」は規範改訂案であり、過去Owner裁定の変更権限を示さない。
- 動作記録の具体的スキーマ、API、実装・V&Vは対象外。
- 本成果物はGitHubへ書き込んでいない。M19–25およびRP-023のHOLDは継続。

## 7. 次の限定工程への入口

Ownerが参照候補版と削除・置換方針を確認した後、原文の完全引用差分・影響表・暫定レシート仕様・共通レビュー質問を同一パケットとして固定し、4AIに配布する。4AI全員一致や過去証跡の完全回収をレビュー完了条件としない。異論は限定範囲でOwnerに提示する。
