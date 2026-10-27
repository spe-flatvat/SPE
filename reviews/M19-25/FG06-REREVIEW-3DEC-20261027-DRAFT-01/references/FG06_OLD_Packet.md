# SPE M19–25｜Rev.4 Common Review Packet DRAFT
工程ID：FG-06／2026-10-25／DRAFT・NON-CANONICAL  
共通パケットID：SPE-M19-25-REV4-FG06-20261025-DRAFT-01

## 1. 対象と読み方
唯一の評価対象は inputs/M19_Control_Contract_v0.4_DRAFT_Rev4_EDITORIAL_CANDIDATE.md。SHA-256：
`d1b6e64caead960972f0e8c2b2edebb24deb36522cc41d65947ff0580a1bd04e`
Rev.2は変更元、Step 6D-35はRev.3統合由来の指摘、FG-05は先行独立監査である。他のRev.4候補・Rev.3・過去Manifestを対象候補の代用にしない。

まず原文と比較元を読んで独立の初期観察を整理し、その後FG-05および本パケットの論点と照合する方法を推奨する。先行判定と異なる結論・重大度・新規Findingを歓迎する。本パケットの概要は規範本文の代わりではない。

## 2. 入力
1. [M19_Control_Contract_v0.4_DRAFT_Rev4_EDITORIAL_CANDIDATE.md](inputs/M19_Control_Contract_v0.4_DRAFT_Rev4_EDITORIAL_CANDIDATE.md)：添付実バイトの無変更コピー。
2. [M19_Control_Contract_v0.4_DRAFT_Rev2.md](inputs/M19_Control_Contract_v0.4_DRAFT_Rev2.md)：保存済みRev.2取得テキストのコピー。今回失敗した添付コピーを読んだとは扱わない。
3. [SPE_M19_25_FG05_Rev2_Rev4_Independent_Audit_20261025.md](inputs/SPE_M19_25_FG05_Rev2_Rev4_Independent_Audit_20261025.md)：先行監査。今回の結論を拘束しない。
4. [Step_6D35_Owner_Provided_Audit_Transcript_DRAFT.md](inputs/Step_6D35_Owner_Provided_Audit_Transcript_DRAFT.md)：Ownerが今回会話へ提示した監査原文の全文転記。元チャットの原日時・原リンク・バイト列は未検証。表の空白等は配布用に整形。
5. references/docs/Workflow.md、references/docs/DecisionLog.md：GitHub連携で基準版から取得した参照資料。

各ファイルの正確なバイト数・行数・SHAはM19_25_Rev4_Independent_Review_Manifest_DRAFT.mdとSHA256SUMS.txtで確認する。

## 3. 承認・証拠状態
- OD-12：Rev.4固定候補に対する条件付きReview Acceptance。対象はRev.2四AIレビュー18件の規範上の処理に限定。全仕様・歴史的証拠の全面承認へ拡張しない。
- Step 6D-35の5件：FG-05では規範対応5/5 PASS。ただしこれは先行監査の判断であり、今回のレビューアーを拘束しない。正式Finding Closeではない。
- E-03／E-04：未検証。
- Owner裁定の原記録：完全照合未了。未回収を直ちに未承認・不存在と判定しない。
- DecisionLog対応：正式Freeze前の確認事項。
- Rev.4：DRAFT／NON-CANONICAL。Canonical化・Freeze：未承認。
- 原本冒頭の NOT REVIEW-ACCEPTED は固定時点の記述として保存し、後続OD-12条件付き受理と別管理する。

元のStep 6D-35の5件、Rev.2四AIレビュー18件、FG05-N01〜N05は別集合である。今回18件を一括して再審査・正式Closeする依頼ではない。ただしRev.4の規範そのものへの異論は可能。
本資料は新規DRAFTのレビュー準備資料であり、レビュー送付、正式Review Acceptance、Finding Close、DecisionLog更新、GitHub書き込み、commit/push/PR、Canonical化、Freezeを承認しない。Ownerが最終判断する。今回の条件付き移行判定はこれらの権限を代替しない。

## 4. Rev.4の概要と差分の見取り図
| 領域 | Rev.4で評価する点 | 参照行（Rev.4） |
|---|---|---|
| §0/CC-01 | F3政策とF3 Boundary、政策source境界、既存モジュール意味論保護 | 32–60 |
| CC-02/03 | 6ドメイン、Action非第7domain、Trigger/Decisionの分離、多年度pending | 64–132 |
| CC-04/05 | 2026初期契約、2027継承、A→C→B、正常年次MUST、試行と確定、正式/異常年度末、Gate監査 | 135–232 |
| CC-06/07 | 非先取り、共通prefix、anchor隔離、依存範囲別停止、HOLDとの区別 | 236–269 |
| CC-08/13 | 個別適格性と相互比較、全契約条件の検証、ID/依存versionと再検証、HOLD発行MAY | 273–299, 426–442 |
| CC-09 | 3監査分類、immutable/append-only、先行裁定・レビュー原本・処分・DecisionLog照合 | 302–336 |
| CC-10/11 | R4 Ch4/5/10順位、shock例外、観測妥当性とTrigger決定性、Decision要求禁止 | 339–391 |
| CC-12 | 予約生成/解決/失効/再予約、新予約固有証拠、既存Decision有効範囲 | 394–422 |
| 横断 | Reason taxonomy、29 Invariants、Freeze境界、証拠留保 | 444–531 |

Rev.2の17 InvariantsからRev.4の29へ増加。S35の「27」は当時のRev.3候補の記載でありRev.4件数へ代用しない。
順序A→C→B自体はRev.2 CC-04にもある。単にGate説明の見出し順だけで新規順序・矛盾と判定しない。
「MUST/MAYを含む行数」は改行分割の影響を受けるため、義務数・規範保存の証明に使わない。

## 5. 必須の未解決論点
| 識別子 | 先行監査の重大度 | 独立評価で問うこと |
|---|---|---|
| FG05-N01 | Major | 多年度pending、再試行、atomic/idempotent年度末、異常年度末、比較再検証、予約/Decision寿命分離、新規Invariantsの規範妥当性と既存Owner裁定との整合性。根拠未取得と未承認を区別する |
| FG05-N02 | Major | CC-01の without separate approval は権限境界の変更か、別権限の明確化か。Rev.2の禁止と同等か、採否に裁定が必要か |
| FG05-N03 | Minor（条件付きMajor再評価） | Rev.2 CC-08の all expressly required contract conditions を実際に検証する義務がRev.4でも同じ強さか。宣言/識別と検証を区別し、実質欠落ならMajorへ再評価 |
| FG05-N04 | Minor | 2026切替候補の可否とGate Cの preceding-year state の意味。初期状態契約との関係を確認し、架空の2025最終状態を導入しない |
| FG05-N05 | Editorial | 固定ファイル状態と後続OD-12条件付き受理の別管理で対象誤認を防げるか。勝手に原本を編集しない |

### 先行規範監査の位置づけ
FG-05は6D35-F-01〜05を文言対応としてPASS、移行判定をCONDITIONAL READYとした。各AIは原文で再評価できる。相違があれば理由・正確な引用・適用条件を記録し、先行PASSを前提にしない。

## 6. 歴史的証拠と参照資料の制約
任意参照3台帳とOwner裁定原記録はGitHub連携で回収を試みたが今回未取得。検索した範囲は固定基準 e2238922193107f204805d9f25d6ddd6f764eced と取得時main 8e46e5b8af6f2c5936d3d166d1b8c69680713d72 の非省略再帰ツリー、および reviews/M19-25/ 配下の3既知ファイル名に対する履歴API。履歴応答は各空配列。全履歴・全ブランチの不存在証明ではない。
docs/Workflow.mdとdocs/DecisionLog.mdは基準SHAを指定して連携GETし、保存テキストのGit blob SHA-1が取得ツリー記載と一致した。取得したDecisionLog本文ではD22/D23/D24/D25/6D38等の指定IDは検出されなかったが、歴史的原裁定の不存在は意味しない。
Rev.4 L11のAuthority basisの列挙、文書内のOwner-approvedという形容、内容の合理性、SHA一致はいずれも過去の承認行為の単独証明ではない。
回収不能な二次証拠をFreezeに採用する判断は別のOwner裁定が必要。今回原裁定を作成・再構成しない。

WorkflowはOwner-confirmed snapshotを要求する。候補が参照する基準SHAは技術的に取得できたが、今回の配布セットに対するOwnerの確認欄は未記入。取得時mainを自動的に新baselineとして採用しない。過去承認済み事項の再オープンは避け、承認根拠未確認と規範の妥当性を分けて報告する。新しい候補DRAFT自体の規範レビューは本依頼の対象である。

## 7. 対象・対象外
対象：CC-01〜13、MUST/MUST NOT/MAY、状態とGate、年次回数・予約・比較・監査・Invariants・Reason・Freeze境界、および必要なOwner裁定。
対象外：政策思想の優劣、数値モデルの全面妥当性、係数最適化、実装コード変更、未実施V&Vの認証。必要な境界問題を指摘することは可能だが、無制限に再設計しない。

## 8. 独立性・配布
Claude・Gemini・Grokには同じZIPと同じCommon Review RequestをOwnerが配布する。今回の他AI回答は初期レビュー終了まで相互非開示。
各AI固有Finding IDを保ち、統合・重複排除・処分は全回答取得後の別工程。
配布実施・Owner承認は今回未実施。M19_25_Rev4_Distribution_Checklist_DRAFT.mdの未記入欄を先に確認する。
