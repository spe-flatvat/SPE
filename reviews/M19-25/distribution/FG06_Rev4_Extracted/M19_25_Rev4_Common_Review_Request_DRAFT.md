# SPE M19–25｜Rev.4 Common Independent Review Request DRAFT
工程ID：FG-06／共通パケットID：SPE-M19-25-REV4-FG06-20261025-DRAFT-01  
受信したレビューモデルが自身の名前・版・実施日時を回答冒頭に記入してください。依頼内容は全モデル共通です。

## 1. 依頼
SPE M19–25 Control Contract Rev.4を、他の今回回答を参照せず、読み取り専用で独立レビューしてください。既存FG-05の結論を追認する依頼ではありません。原文を優先し、異論・重大度変更・新規Findingを許容します。
対象は `inputs/M19_Control_Contract_v0.4_DRAFT_Rev4_EDITORIAL_CANDIDATE.md` のみ。固定SHA-256：
`d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e`

入力はManifest、Common Packet、対象Rev.4、Rev.2、FG-05報告書、Step 6D-35転載、取得済みWorkflow/DecisionLogです。Rev.3や別Rev.4や古いManifestに置き換えないでください。
SHAを実計算できる場合は結果と方法を記録してください。実ファイルの値が異なる場合は中止して不一致を報告してください。本文を読めるが実バイト計算だけできない場合はSHA未検証と明記し、内容評価を行うか限定評価とするかを説明してください。本文そのものに到達できない場合は監査完了扱いにせず不足を報告してください。
必須資料に不足がある場合、どの設問を評価できないか明示し、推測で埋めないでください。

## 2. 現在状態と権限
- OD-12：Rev.4固定候補に対する条件付きReview Acceptance。対象はRev.2四AIレビュー18件の規範上の処理に限定。全仕様・歴史的証拠の全面承認へ拡張しない。
- Step 6D-35の5件：FG-05では規範対応5/5 PASS。ただしこれは先行監査の判断であり、今回のレビューアーを拘束しない。正式Finding Closeではない。
- E-03／E-04：未検証。
- Owner裁定の原記録：完全照合未了。未回収を直ちに未承認・不存在と判定しない。
- DecisionLog対応：正式Freeze前の確認事項。
- Rev.4：DRAFT／NON-CANONICAL。Canonical化・Freeze：未承認。
- 原本冒頭の NOT REVIEW-ACCEPTED は固定時点の記述として保存し、後続OD-12条件付き受理と別管理する。
本資料は新規DRAFTのレビュー準備資料であり、レビュー送付、正式Review Acceptance、Finding Close、DecisionLog更新、GitHub書き込み、commit/push/PR、Canonical化、Freezeを承認しない。Ownerが最終判断する。今回の条件付き移行判定はこれらの権限を代替しない。
5件の先行PASSは規範上の評価で、証拠回収・Owner承認・Closeではありません。Rev.2四AI18件を今回一括で再処分しないでください。

## 3. 評価質問
1. Rev.2からRev.4への規範保存・変更は妥当か。MUST/MUST NOT/MAY、定義・状態表・例外も比較してください。
2. FG05-N01〜N05の評価・重大度・修正要否は妥当か。先行重大度をそのまま採用する必要はありません。
3. CC-01〜CC-13に内部矛盾、欠落、曖昧な権限・実行条件がないか。
4. Gate A→C→B、2026初期状態/2027継承、年次計算・年度末の回数、Decision/Transition/予約/比較は整合するか。
5. 新MUST/MUST NOTは妥当か。内容上の妥当性と歴史的承認根拠の確認を分離してください。
6. 29 Invariantsと本文、Reason taxonomy、Freeze boundaryは整合するか。
7. 未検証の歴史的承認根拠を、レビュー時と正式Freeze時にどう区別して扱うべきか。
8. FG-05が見落とした新規Findingがあるか。6D35-F-01〜05の対応について異論も可能です。
9. レビュー後にOwnerの新たな裁定が必要な事項は何か。既存原裁定の回収で解消できる事項と分けてください。

### 必須論点
| 識別子 | 先行監査の重大度 | 独立評価で問うこと |
|---|---|---|
| FG05-N01 | Major | 多年度pending、再試行、atomic/idempotent年度末、異常年度末、比較再検証、予約/Decision寿命分離、新規Invariantsの規範妥当性と既存Owner裁定との整合性。根拠未取得と未承認を区別する |
| FG05-N02 | Major | CC-01の without separate approval は権限境界の変更か、別権限の明確化か。Rev.2の禁止と同等か、採否に裁定が必要か |
| FG05-N03 | Minor（条件付きMajor再評価） | Rev.2 CC-08の all expressly required contract conditions を実際に検証する義務がRev.4でも同じ強さか。宣言/識別と検証を区別し、実質欠落ならMajorへ再評価 |
| FG05-N04 | Minor | 2026切替候補の可否とGate Cの preceding-year state の意味。初期状態契約との関係を確認し、架空の2025最終状態を導入しない |
| FG05-N05 | Editorial | 固定ファイル状態と後続OD-12条件付き受理の別管理で対象誤認を防げるか。勝手に原本を編集しない |

2026の架空の2025最終状態を作らないでください。原裁定未回収を直ちに未承認・不存在にせず、文書から原Owner発言を創作しないでください。実装・政策思想・数値モデルの全面再設計へ範囲を広げないでください。
FG-05の閲覧による誘導を避けるため、可能なら原文比較で初期観察を作り、その後先行監査と照合してください。

## 4. 回答形式
### A. Executive Verdict
`ACCEPT / CONDITIONAL ACCEPT / REVISE / REJECT`のいずれか。候補の規範品質に対する評価でありFreeze承認ではありません。原本・SHA・比較元の取得状況、未実施検証、判定理由と条件を明記してください。
WorkflowのAccepted / Revision Recommended / Rejectedへの正式登録・読み替えは別工程のOwner判断とし、この4値を自動的に既存台帳へ登録しません。

### B. Finding Register
各Findingに独自IDを与え、以下を記録してください。
- Finding ID（自身が識別可能なprefixと連番。既存IDを上書きしない）
- Critical / Major / Minor / Editorial
- 対象ファイル・条項・行番号（行計算不可なら節と段落）
- 問題と成立条件、制御上の影響
- Rev.2との関係
- 判断に必要な正確な根拠引用
- 推奨修正（提案のみ。原ファイルを変更しない）
- Owner裁定の必要性。既存根拠照合と新裁定を区別
- FG05-N01〜N05との対応（対応なしも可）
- 確定的問題／解釈上のリスク／証拠不足の区分

FG05-N01〜N05ごとに、同意・不同意・限定同意・未検証等と理由を示してください。問題なしの判断でも省略しないでください。Findingを統合・重複排除した場合でも元対応を残してください。

### C. Normative Preservation Assessment
全18セクションについてKEEP / REPLACE / ADD / REVIEWで評価してください。複数分類も可能。
REPLACEを承認済み変更の意味で使う場合は検証できた承認根拠を示し、未取得ならREVIEWまたは「置換内容確認済み・承認根拠未検証」と明示してください。
見出しの存在、語数、行数だけで規範保存を証明しないでください。意図しない削除・弱化、新しい義務・禁止、条項間矛盾、編集と実質変更を区別してください。

### D. Residual Risks
権限・証拠・仕様・実装境界のリスクを分け、未確認を明示してください。E-03／E-04は未検証状態を維持してください。

### E. Review-to-Freeze Conditions
レビュー後、Freeze前に必要な根拠回収、修正、再レビュー、Owner裁定、DecisionLog対応を列挙してください。今すぐレビューできることとFreezeできることを区別してください。
正式Close、Canonical化、Freeze、GitHub書き込み等を実行・宣言しないでください。

## 5. 独立性
今回の他AI回答を見ず、各自のFinding IDと判断を保持してください。FG-05は参考資料であり先行AIの優先権はありません。全回答取得後の統合は今回の依頼外です。
