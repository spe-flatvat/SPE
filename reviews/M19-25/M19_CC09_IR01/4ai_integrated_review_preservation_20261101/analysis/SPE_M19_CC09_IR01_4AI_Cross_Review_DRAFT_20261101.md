# SPE M19-CC09-IR-01｜統合改訂DRAFT 4AI横断検証 DRAFT

**Status:** CROSS-REVIEW DRAFT / NOT OWNER-ADJUDICATED / NOT FROZEN / NOT COMMITTED
**対象Repository:** `spe-flatvat/SPE`
**統合DRAFT固定Commit:** `edc47652f986b75341404154bfd3057da89e9329`
**比較基準Commit:** `754c1e2907bce67f7d58d10bf36813ac76fd1ed0`
**資料:** ChatGPT最終報告、Gemini会話提示最終回答（抽出保全）、Grok最終報告、Claude最終報告、手元の統合DRAFT。
**注意:** 本文は各AIの自己申告・文書上の指摘を比較する二次分析。GitHub固定Commitへの独立アクセス・全SHA再計算・実装テストを本工程で実施したものではない。

## 1. 結論の横断比較

| AI | 受領 | 結論 | 指摘 | SHAの証拠境界 |
|---|---|---|---|---|
| ChatGPT | READY | ACCEPT | Editorial 2 | Owner承認の補完証拠採用。自身の全件直接SHA再計算とはしない |
| Gemini | READY | ACCEPT | Invariant 17の解釈留意等、ID付きFindingなし | Owner承認補完証拠。結合21文書＋Workflowの可読性は自己確認 |
| Grok | PASS | ACCEPT | Minor 1 / Editorial 2 | 主対象3件直接SHA一致申告。残り全件の直接照合申告なし |
| Claude | PASS | REVISE（軽微修正） | Minor 6 / Editorial 1 | 17/17直接SHA一致申告。Rev.A 3件は計算のみ（事前期待値なし）。DIFF適用結果バイト一致申告 |

**一致点:** CC-09削除・Reserved化の方向性、歴史的無限監査の排除、Gate A→C→B、fail-closed、年度末atomic/idempotent、予約とDecisionの寿命、比較契約の明示全条件、R4 precedence、既存計算意味論の保護について、4AIとも重大な問題を報告していない。全AI Critical/Major 0。

**不一致点:** 規範の有限記録・追記性、レシートの位置・根拠、微小な規範追加、版参照について、ClaudeはMinor 6件でREVISE。他AIのACCEPTはこれら個別論点の反証とは限らない。

## 2. 横断Findingマトリクス（正式Closeではない）

| 横断ID | 原Finding | 主題 | 他AIとの関係 | 暫定仕分け・次の検証 |
|---|---|---|---|---|
| X-01 | CLD-02 | 運用実行記録の一般的上書き禁止の消失 | 他AIの安全性PASSとは異なる粒度。直接反証なし | **実質規範欠落候補**。CC-09削除前後とCC-04/05/08/12・Invariant17の適用範囲を対照。全操作への追記専用MUST再導入がB-ODの最小化に抵触するか要評価 |
| X-02 | CLD-03 | CC-09 Reserved見出し下の暫定レシートMUSTとFreeze対象外 | 他AIは7項目・Workflow整合を肯定、配置問題への直接反証なし | **文書構造・適用範囲の不整合候補**。別見出し/付録へ移す場合の規範範囲とFreeze境界を明示。Owner選択候補 |
| X-03 | CLD-05 | CC-04再試行・CC-05 Gate Bの新規要求範囲 | 他AIは既存意味論保全と評価、増分の有無には判断差 | **追加規範候補**。Rev.2との主語・条件・MUST対象の差分を文単位で比較。Owner確認候補 |
| X-04 | CLD-01 | Freeze時の既存レシート依拠基準と任意issuer | Geminiは7必須項目を必要十分と評価 | **境界明確化候補**。7必須項目を変えず既存裁定記録との接続を示せるか。issuerは任意提案であり追加必須化はしない。Owner確認候補 |
| X-05 | CLD-04 | 暫定レシートとDecisionLogの非代替関係 | 他AIはWorkflowとの矛盾なしと評価 | **明確化候補**。`does not authorize` と `does not satisfy/replace` の論理差を確認。Workflow既存義務を増やさない修文を検討 |
| X-06 | CLD-06 | Trigger評価規則・観測契約の版参照 | 他AIはInvariant17の版参照を十分と評価 | **明示化候補**。Invariant17(iii)が既に包含するかを確認。必要なら例示にとどめる |
| X-07 | Grok-01 / Gemini Q3 / ChatGPT旧INT-01 | Invariant17の閉じた3分類と歴史的統治記録の混入防止 | 3AIの評価差（Grok Minor、Gemini留意、ChatGPT対応済み） | **解釈境界候補**。現行の排除文の有無を確認し、重複したMUSTを増やさない |
| X-08 | Grok-02 | DIFF・DRAFT参照切れ「可能性」 | Claudeはpatch適用後バイト一致と報告 | **未特定のEditorial**。具体的参照先が示されていないため確定Findingと扱わない。patch一致は参照の意味整合を必ずしも証明しない |
| X-09 | Grok-03 / ChatGPT FINAL-01 / Claude-07 | 固定Commit階層・配布表示の不統一 | 複数AIが同方向 | **Editorial統合候補**。配布固定Commit、前段Commit、Rev.A Commitを役割別に明記 |
| X-10 | ChatGPT FINAL-02 / Claude CLD-08追跡 | 旧Finding処理の追跡表 | Claudeは既存18件の個別照合未了を明記 | **追跡可能性候補**。旧Findingを自動Closeせず、対応・未検証・非承継を区分した台帳を作る |
| X-11 | Claude-07 | Document ID重複、空行、NOT ISSUED、Rev.A期待SHA未登録 | 他AIの主要結論と独立 | **Editorial/配布管理**。原本を改変せず次版DRAFT・配布補遺で扱う |

## 3. 原文対照で確認できた限定事項

手元の `SPE_M19_CC09_IR01_Rev2_Integrated_Amendment_DRAFT_20261101.md` では `## CC-09 — Reserved / Deleted` の直下に `### M19-only provisional Owner decision receipt boundary` があり、その節に `MUST` が存在する。よってCLD-03の**構造上の観察は原文と整合**する。ただし、それが正式な契約違反に当たるか、Freeze節の意図的な適用除外かは未裁定。

同文書の暫定レシート節は `Issuance of a receipt does not ... authorize a canonical DecisionLog update.` と記す。`does not satisfy or replace any DecisionLog recording` とは異なるため、CLD-04の指摘には文言上の根拠がある。既存Workflow義務の解釈と、追加規範ではなく明確化で足りるかを要確認。

## 4. Owner判断候補（未発出・未裁定）

- **OD-CAND-01:** 7必須項目を維持したまま任意 `issuer` を追加するか。加えない場合、既存裁定への依拠をどう明文化するか。
- **OD-CAND-02:** 暫定レシート境界をCC-09 Reserved配下から独立節/付録へ移すか、Freeze対象に含めるか。
- **OD-CAND-03:** CC-04再試行とCC-05 Gate Bの増分要求を採用するか、Rev.2の要求条件へ戻すか。

**補足:** CLD-02の追記専用一般則の復元は「Owner判断不要」とClaudeは評価したが、CC-09の旧全般MUSTを再導入するリスクがあるため、横断評価前に無条件の機械修正をしない。追加裁定要否は未確定。

## 5. 推奨する後続順序（本書では実施しない）

1. 原文と各Findingの根拠を文単位で照合し、必要最小限の修正候補を作る。
2. Owner裁定候補を選択肢・副作用・B-OD-01〜05との関係付きで提示する。
3. Owner承認後にのみ次版DRAFT、DIFF、Selfcheck、Manifestを作る。
4. GitHub格納・SHA固定・レビュー再配布・正式Close・Freezeは別工程とする。

## 6. 停止境界

現時点では**4AI回答のローカル保全と横断検証DRAFTのみ**。GitHubへの書込み、DecisionLog更新、原本変更、Finding正式Close、Owner裁定、Freeze、HOLD解除は未実施。正式なGitHub保全はTermux等での明示的な格納作業を要する。
