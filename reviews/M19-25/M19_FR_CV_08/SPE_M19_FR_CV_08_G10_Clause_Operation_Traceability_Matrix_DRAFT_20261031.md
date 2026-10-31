# SPE M19-FR-CV-08｜G10 条項×操作段階対応表（DRAFT）

**Status:** DRAFT / STATIC TRACEABILITY ONLY / NON-CANONICAL / HOLD
**基準保全Commit:** `3e7c1814e2d31fd9373f58e4d88410d382abd8bb`
**参照候補:** `SPE_M19_FR_CV_06_Rev2_Convergence_Candidate_DRAFT_20261031.md`（SHA-256 `94286b1e8b86d19c0684c3463e77a454b49be661574be3cbbdb5b952a333e3bd`）

## 1. 位置付け

G10「Gate・監査・理由コードへの具体的配置」を、既存のCV-07横断検証報告に記載された条項参照を起点に整理した**確認用マトリクス**。新しいスキーマ・義務・承認・Gate条件を創設しない。条項本文の網羅的逐条照合、実装テスト、29 invariants動的検証は未実施。

## 2. 操作段階別の静的追跡案

| 操作段階 | 既存資料で参照された条項・箇所 | 確認すべき既存要件 | 監査・理由コードへの接続状況 | 未解決／追加確認 |
|---|---|---|---|---|
| 候補生成 | CC-04 Rev.2 L154–156、CC-09 L315・319（CV07報告引用） | 2026 baseline検証と候補生成認可を区別。別承認根拠のID/版・適用範囲・生成／利用権限を確認 | 作成／checkpoint検証証拠、immutable referenceへの一般要件ありとの報告。操作別フィールド未確定 | creator列挙と新schema不創設の関係（G09）、作成時検証の証跡格納先 |
| 候補利用・比較 | CC-04 L154–156、CC-08、CC-09（CV07報告T05） | 比較契約・対象施策・年・認可・比較適格性 | 比較記録の一般要件は報告されるが、追加検証項目との1対1接続未確定 | 比較前必須検証と再検証時点、比較結果へのreason code紐付け |
| 予約前・Scheduling | CC-03 L89–96／L121、CC-12 L407／409、CC-05（CV07報告T05） | Trigger／attributable Decision、認可、reservation条件、依存範囲fail-closed | CC-12 L409に認可チェック結果の保持義務との報告。新検証ごとの証拠項目は未確定 | **予約前の要件をGate Bまで遅延させない**。Decision-free例外は現時点で非認可 |
| Gate A→C→B | CC-05、CC-09、CC-12、Gate B引用L215（CV07報告） | 各Gateの適用性、Decision authority/evidence、live reservation、destination/effective year、競合 | Gate Bの一般検証項目は存在。追加検証のGate別割当は未確定 | Gate B単独で事前検証を代替できない。失敗時の依存範囲と記録を確認 |
| 年度境界・効力発生 | CC-04 L154–156、CC-05、CC-12、CC-09 | 有効年、適用認可、予約状態、必要な再検証、incumbent継続 | 年度／checkpoint証拠と監査の一般要件ありとの報告 | 2026初期化・incumbent計算を誤って停止しない。再検証失敗のreason code対応未確定 |

## 3. 条項横断の確認点

1. **CC-03／CC-05／CC-12:** 現行Trigger/Decision証拠は維持。将来のDecision-free経路は別途明示Owner承認と条項間整合が必要。
2. **CC-04:** `other applicable approved requirements` は未特定の承認や優先順位を推定する根拠にならない。2026 baseline validationは2026 transition authorizationを兼ねない。
3. **CC-09:** 一般的な監査・不変参照の要求があることと、新検証を各Gate／reason code／記録項目へ明示的に接続済みであることは別。
4. **CC-08等:** 比較契約・適格性は対象段階に応じて検証する。原条項全文を照合していないため、厳密な実装要件の確定は保留。
5. **29 invariants:** 静的整合性への言及を動的PASSに読み替えない。

## 4. Owner判断の前に必要な証拠

- Rev.2候補の該当条項の原文・行位置の固定照合
- Gate A/C/B、CC-09監査記録、reason taxonomyの正式な定義・版・適用範囲
- 予約前／Gate B／年度checkpointの実装契約、検証ログ、失敗理由の記録先
- G09 creator要件の規範意図、G01/G02のOwner原証拠

**未確定事項:** どの検証をどのGate・監査フィールド・reason codeに必須接続するか、追加スキーマが必要か、正式承認前の実行ゲートをどこに置くか。これらは本表では裁定しない。

## 5. 終了条件

この表は調査・裁定準備用DRAFT。正式なCC修文、実装指示、証拠採用、Owner裁定、Finding Closure、GitHub書込、Freeze、HOLD解除は行わない。M19–M25／RP-023 HOLD維持。次工程へ自動移行しない。
