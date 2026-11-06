# SPE RP-023｜Step 29H 16 Findings Resolution候補台帳 DRAFT

- Status: **DRAFT / NON-CANONICAL / NOT ADJUDICATED**
- Date: 2026-11-06
- Authority: 読取り・分析・新規DRAFTのみ。Owner正式Disposition、Finding Close、GitHub書込み、Freeze、HOLD解除なし。
- Repository: `spe-flatvat/SPE`
- Review target fixed commit: `5f27d4e2fba90cda2cd69ee534e865174c31ba1f`
- Original 4AI responses fixed commit: `51680012e2f3e803b373b1c43b3644c93c74068f`
- Cross-review DRAFT fixed commit: `ec308e9528519b68fc445f31580607f29e51b113`

## 1. 目的と判定境界

既存の4AI横断表にある16件の原Findingを、ID・Severityを保持したまま、Resolution候補・残余証拠・Owner留保へ対応づける。候補区分は作業用ラベルであり、正式Status/Dispositionではない。複数AIの同趣旨指摘を件数統合せず、原レビューの個別Status未記載を補作しない。

## 2. 全16件 Resolution候補

| AI | 原Finding ID | 原Severity | 作業区分 | 原論点 | Resolution候補・対照結果 | 暫定作業状態 | 留保 |
|---|---|---|---|---|---|---|---|
| ChatGPT | H29-01 | Major | 編集・整合 | Header Rulesの必須項目欠落 | 実欠落を確認。次版ヘッダ補完候補 | 要修正候補 | 実日付・Updated Byを創作しない |
| ChatGPT | H29-02 | Minor | 編集・整合 | OD-08旧未決表記 | 後続の案A承認と起案時点を分離 | 要修正候補 | 原承認の再認証は未実施 |
| ChatGPT | H29-03 | Minor | 説明・表現 | A未照合と限定判断の具体例 | 既存のPASS偽装禁止を維持し例示を検討 | 説明補強候補 | 新たな例外権限を創設しない |
| Claude | RP23-CLD-01 | Major | 編集・整合 | Owner-confirmed Snapshot明記 | 既存WorkflowのSnapshot要件と非代替性を参照 | 要修正候補 | 既存要件の再定義を避ける |
| Claude | RP23-CLD-02 | Minor | 編集・整合 | Header Rules・自己検証範囲 | ヘッダ補完とAC/NC自己検証の表現を分離 | 要修正候補 | H29-01と統合しない |
| Claude | RP23-CLD-03 | Minor | Owner判断留保 | 検証担当の独立性 | 別人必須化は新規義務の可能性。既存OD-06原文照合を優先 | 判断留保 | Owner裁定なしに役割義務を追加しない |
| Claude | RP23-CLD-04 | Minor | 証拠・原文対照 | 07A/P0裁定とDecisionLog | §2(2)記録義務参照、§10証拠状態注記、正式反映時の記録要否確認 | 残余あり・修正候補 | 07A原文全文/SHA未検証。裁定の不存在と扱わない |
| Claude | RP23-CLD-05 | Minor | 編集・整合 | OD-08状態 | 起案当時の未決と後続承認を明示 | 要修正候補 | H29-02とID維持 |
| Claude | RP23-CLD-06 | Minor | 説明・表現 | M19–25等の非遡及例示 | 既存承認事項の一般表現に置換を検討 | 説明補強候補 | M19–25を確定済みと断定しない |
| Claude | RP23-CLD-07 | Editorial | 証拠・原文対照 | §8該当性・2Commit・.diff・旧状態 | §8『該当する場合』、Commit役割注記、.diff未検証記録、時点別レシート | 4小論点整理済・修正候補 | 原.diff一致未検証、原文の遡及改変なし |
| Gemini | F-01 | Major | 証拠・原文対照 | B/C一律必須の懸念 | §3/4/8に区分別保護の明文あり | 既存保護あり・残余特定待ち | 原Major維持。問題の具体的箇所を未特定 |
| Gemini | F-02 | Major | 証拠・原文対照 | Workflow接続 | §2(6)/4/9にReview・waiver・consensus等の保護あり | 既存保護あり・残余特定待ち | Snapshot固有欠落はCLD-01と別 |
| Gemini | F-03 | Minor | 証拠・原文対照 | Header Rulesとの関係 | §4.3に遵守明文あり | 既存保護あり・残余特定待ち | 実ヘッダ欠落はH29-01/CLD-02と別 |
| Gemini | F-04 | Minor | 証拠・原文対照 | 非遡及 | §2(8)/7に非遡及明文あり | 既存保護あり・残余特定待ち | 例示リスクはCLD-06と別 |
| Grok | RP023-29H-Grok-01 | Minor | 証拠・原文対照 | 状態語彙enum | §3に新規必須enumに置換しない明文あり | 既存保護あり・残余特定待ち | 原Minor維持 |
| Grok | RP023-29H-Grok-02 | Editorial | 説明・表現 | Header/Status相互参照 | 既存Header Rules参照の明確化候補 | 説明補強候補 | 実欠落と同一視しない |

## 3. CLD-04 / CLD-07 残余確認の反映

### RP23-CLD-04（Minor）

- 原レビュー：`reviews/RP-023/step29h/responses/RP-023_Step29H_Claude_Independent_Review_DRAFT_20261103.md` L96–101。
- v0.2 §2(2) L19は明示チャット裁定の成立を認める。§10 L96–99は07A DR-01〜06とP0 OD-01/02/04/06/07を記載する。
- Workflow L11はガバナンス・レベルの決定のDecisionLog記録を要求。固定DecisionLogに当該IDの明示対応記録を特定できず。ただし履歴全体の不存在の証明ではない。
- 過去会話の案A採用経緯は支持材料。07A原発言全文・原本SHA-256照合は未完了。正式な証拠認証と区別する。
- 修正候補：§2(2)に『チャット上の裁定であっても、ガバナンス・レベルの決定に関する既存WorkflowのDecisionLog記録義務を免れない』趣旨を追記。§10に07A原証拠未検証の注記。正式反映前に記録要否と対応先を確認。
- 既裁定の再審議・自動無効化・DecisionLogへの無断書込みを行わない。

### RP23-CLD-07（Editorial）

- 原レビュー：同Claude回答 L117–121。4小論点は一つの原Finding ID内で管理。
- (1) §8共通項目の適用範囲：『該当する場合』等で必須性を明確化。ただし区分別必須要件を緩和しない。
- (2) v0.2の規範照合commitとManifestのEvidence HEAD：役割を明示。両commitの規範SHA一致はClaude原報告によるもので、今回独立再計算はしていない。
- (3) 07C-03別添 `.diff`：固定14件には含まれず原本一致は未検証。再生成差分を原添付と称さない。
- (4) 共通文書の旧発出状態：作成時点のDRAFT/NOT DISPATCHEDと後続のOwner承認・発出を別記。過去の固定原本を遡及改変しない。

## 4. 件数・作業区分チェック

- 原Finding：ChatGPT 3、Claude 7、Gemini 4、Grok 2 = **16件**。
- 原Severity：Major 4、Minor 10、Editorial 2 = **16件**。Severity変更なし。
- 作業区分：編集・整合 5、Owner判断留保 1、証拠・原文対照 7、説明・表現 3 = **16件**。
- 証拠・原文対照7件のうち、5件は既存明文の保護を確認、CLD-04/07は残余を具体化。5件も正式棄却/Closeではない。
- Additional候補1件は16原Findingと別枠。新しい17番目の原Findingとはしない。

## 5. 次工程の推奨（未実行）

1. 既存条文の明確化と編集修正の候補を、固定v0.2に手を触れず**次版差分DRAFT**として起案。ヘッダ、Snapshot、OD-08、§2(2)/§10、§8、非遡及例示を対象に限定。
2. Claude CLD-03（検証担当独立性）は新規規範となる可能性があるため、既存OD-06原裁定の照合またはOwner判断を待つ。
3. Gemini 4件/Grok-01の既存保護について、原文の具体的不足箇所を提示できるか追加対照し、Disposition判断材料を整える。
4. 正式Resolution・Review/consensus・Review Acceptance・Git/DecisionLog反映・Freeze・HOLD解除は既存WorkflowとOwner権限に従い別工程。

## 6. 取得・検証限界

- 今回の基礎：接続済みGitHubから固定cross-review DRAFTを取得し、ローカルのCLD-04/07残余報告と7件対照報告を読み込んだ。
- GitHub取得は本文のテキスト取得。今回、GitHub原本バイトのSHA-256独立再計算はしていない。cross-review DRAFTの既存の実バイト照合報告を、今回の再検証と混同しない。
- 07A原裁定全文、元`.diff`、Step28原承認、OD-06原裁定は本台帳では未認証。未取得を不存在と断定しない。
- 本台帳のSHA-256は生成したローカルファイルに対する実計算であり、GitHub保全の証明ではない。

## 7. STOP

本工程は16件Resolution候補台帳DRAFTのローカル生成・照合で終了。正式Disposition 0件、Finding Close 0件。RP-023／M19–25 HOLD継続。
