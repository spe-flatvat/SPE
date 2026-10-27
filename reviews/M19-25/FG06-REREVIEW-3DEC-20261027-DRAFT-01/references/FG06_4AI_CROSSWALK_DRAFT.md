# SPE M19–25｜FG-06 4AI原回答完全性照合・全Finding対応表 DRAFT

- 追跡ID：`FG06-4AI-ORIGINAL-FINDINGS-20261027-01`
- 状態：`CONTENT RECOVERED / BLOB IDENTIFIED / RAW SHA-256 NOT YET VERIFIED / DISPATCH HOLD`
- 権限：読み取り・分析・DRAFTのみ。Owner最終判断。
- 調査基準：GitHub接続済み連携、固定commit `231a983d4467c3427f6a782bf336e5b3f49ced2f`。`main`へ読み替えない。

## 1. 原回答所在・取得結果

| AI | 固定commit内の原回答 | Git blob SHA-1 | 原回答判定 | 独立Finding数 |
|---|---|---|---|---:|
| ChatGPT / GPT-6 | [原回答](https://github.com/spe-flatvat/SPE/blob/231a983d4467c3427f6a782bf336e5b3f49ced2f/reviews/M19-25/responses/ChatGPT_Rev4_FG06_20261025.md) | `77ee33a1e4a0af48a0bee79b3ae94121373cffb0` | REVISE | 7 |
| Claude | [原回答](https://github.com/spe-flatvat/SPE/blob/231a983d4467c3427f6a782bf336e5b3f49ced2f/reviews/M19-25/independent_reviews/M19_25_Claude_FG06_Rev4_Independent_Review.md) | `22d7995aa3cad1080f5535c56fd971c12e1eddbb` | REVISE | 6 |
| Gemini | [原回答](https://github.com/spe-flatvat/SPE/blob/231a983d4467c3427f6a782bf336e5b3f49ced2f/reviews/M19-25/responses/Gemini_Rev4_FG06_20261025.md) | `501a25d6845fa63e51808139ff3f89e8926dde39` | CONDITIONAL ACCEPT | 1 |
| Grok | [原回答](https://github.com/spe-flatvat/SPE/blob/231a983d4467c3427f6a782bf336e5b3f49ced2f/reviews/M19-25/responses/Grok_Rev4_FG06_20261025.md) | `aa3bbf92cb5d220a6f1beed3549e9fe20a171771` | CONDITIONAL ACCEPT | 6 |

4件ともGitHub連携の `fetch_file`（commit指定）で全文テキスト取得成功。各 `result.sha` はGit blob SHA-1であり、SHA-256ではない。今回の環境ではGitHub返却テキストを原ファイルの実バイトとして保存・再計測していないため、**原回答の実バイトSHA-256照合は未了**。元レビュー担当者の自己申告SHA検証と本工程の検証を混同しない。

## 2. 全Finding個別対応表（独立ID保持）

| Finding ID | 原回答重大度 | 対象 | 論点（要約） | 3裁定との関係 | 現状 |
|---|---|---|---|---|---|
| GPT6-FG06-01 | Major | CC-08/13 | 比較契約全条件検証の弱化 | CC-08裁定A | 3裁定反映候補の再レビュー対象 |
| GPT6-FG06-02 | Major | CC-03/04/08/09/12, invariants | 実質追加規範の歴史的承認根拠 | 別論点 | 原裁定照合未了 |
| GPT6-FG06-03 | Major | CC-01 | 別承認例外による権限境界変更 | CC-01裁定A | 3裁定反映候補の再レビュー対象 |
| GPT6-FG06-04 | Minor | CC-04/05 | 2026切替候補とGate C参照状態 | 別論点 | 未裁定・継続 |
| GPT6-FG06-05 | Minor | CC-02/03/09 | 多年度pendingとDecision現行状態の境界 | 別論点 | 未裁定・継続 |
| GPT6-FG06-06 | Minor | CC-04/12 | 予約未発効解決と異常年度末の接続 | 別論点 | 未裁定・継続 |
| GPT6-FG06-07 | Editorial | ヘッダ/OD-12 | 固定時点の状態と後続条件付き受理 | 別論点 | 表示・証拠管理継続 |
| CLD-01 | Major | CC-03 | met/not_required明示fail-closed削除 | CC-03裁定A | 3裁定反映候補の再レビュー対象 |
| CLD-02 | Major | CC-01 | 別承認例外 | CC-01裁定A | 3裁定反映候補の再レビュー対象 |
| CLD-03 | Major | CC-08 | 比較契約検証義務弱化 | CC-08裁定A | 3裁定反映候補の再レビュー対象 |
| CLD-04 | Minor | CC-04/05 | 2026切替候補とGate C | 別論点 | 未裁定・継続 |
| CLD-05 | Minor/Editorial | CC-05 | Gate A/C失敗時のGate B記録状態 | 別論点 | 未裁定・継続 |
| CLD-06 | Editorial | ヘッダ/OD-12 | 固定時点の状態と後続条件付き受理 | 別論点 | 表示・証拠管理継続 |
| GEMINI-01 | Minor | CC-03 | pending失効条件の監査ログ明示 | 別論点 | 未裁定・継続 |
| GRK-01 | Major | CC-03/04, invariants | 実質追加規範のOwner承認根拠 | 別論点 | 原裁定照合未了 |
| GRK-02 | Major（条件付き） | CC-01 | 別承認例外 | CC-01裁定A | 3裁定反映候補の再レビュー対象 |
| GRK-03 | Minor | CC-08 | 比較契約全条件検証弱化 | CC-08裁定A | 3裁定反映候補の再レビュー対象 |
| GRK-04 | Minor | CC-04 | 2026切替候補とGate C | 別論点 | 未裁定・継続 |
| GRK-05 | Editorial | ヘッダ/OD-12 | 固定時点の状態と後続条件付き受理 | 別論点 | 表示・証拠管理継続 |
| GRK-06 | Editorial | 証拠/SHA | Grok原レビューの実バイトSHA未計測 | 別論点 | 原回答自身の証拠留保 |

**独立Finding総数20件**（GPT-6 7件／Claude 6件／Gemini 1件／Grok 6件）。GeminiのFG05-N01〜N05再掲は独立新規Findingと重複計数しない。各AIのFinding IDを改名・統合・Closeしない。

## 3. 横断論点の対応（統合は分析上の参照のみ）

| 横断論点 | 対応する原回答ID | 3裁定の対象か |
|---|---|---|
| CC-03 明示fail-closed文削除 | CLD-01 | YES（CC-03案A） |
| CC-01 別承認例外 | GPT6-FG06-03, CLD-02, GRK-02, FG05-N02, GeminiのFG05-N02再評価 | YES（CC-01案A） |
| CC-08 比較契約全条件検証 | GPT6-FG06-01, CLD-03, GRK-03, FG05-N03, GeminiのFG05-N03再評価 | YES（CC-08案A） |
| 実質追加規範のOwner原裁定 | GPT6-FG06-02, GRK-01, FG05-N01, GeminiのFG05-N01再評価 | NO（未検証継続） |
| 2026切替候補・Gate C | GPT6-FG06-04, CLD-04, GRK-04, FG05-N04, GeminiのFG05-N04再評価 | NO |
| 多年度pending/Decision表示 | GPT6-FG06-05, GEMINI-01（同一Findingではない） | NO |
| 予約未発効解決・異常年度末 | GPT6-FG06-06 | NO |
| Gate A/C失敗時Gate B状態 | CLD-05 | NO |
| 固定ファイル状態・OD-12表示 | GPT6-FG06-07, CLD-06, GRK-05, FG05-N05, GeminiのFG05-N05再評価 | NO |
| SHA/取得証拠の留保 | GRK-06 | NO |

## 4. FG05-N01〜N05の追跡

- FG05-N01：実質追加規範の原裁定未照合。4AIとも承認根拠を留保（規範品質評価とは別）。
- FG05-N02：CC-01別承認例外。Owner裁定A反映候補で再レビュー対象。
- FG05-N03：CC-08比較契約検証義務。重大度はAI間で異なる（ClaudeはMajor、GrokはMinor、GeminiはMinor/条件付きMajor）。重大度を勝手に統一しない。
- FG05-N04：2026切替候補とGate C。未裁定の残余論点。
- FG05-N05：固定時点NOT REVIEW-ACCEPTEDと後続OD-12。別管理の表示・証拠論点。

## 5. 完全性とゲート判定

- **PASS**：固定commitにおける4原回答の所在特定、全文テキスト取得、Git blob SHA-1取得、20独立Finding IDの抽出と対応表作成。
- **NOT VERIFIED**：Git blob SHA-1のローカル実バイト再計算、4原回答の実バイトSHA-256、各原回答の配布時原ファイルとGitHub保存版のバイト同一性、元ZIPのバイト同一性。
- **NOT DONE**：原回答の各主張をRev.4本文・Owner原裁定と行単位で全件再検証する作業、Owner原裁定の完全照合、Finding Close。
- **NEXT**：必要ならGitHub commitのblobをTermuxで `git show COMMIT:PATH | sha256sum` によりOwner独立計測し、AI側も実バイトを別経路で取得して突合。その後、新候補専用の共通再レビュー依頼書・パケットを起案。
- **STOP**：M19–25／RP-023 HOLD継続。配布・レビュー開始・DecisionLog変更・GitHub書込み・正式Review Acceptance・Canonical化・Freezeは未実施。
