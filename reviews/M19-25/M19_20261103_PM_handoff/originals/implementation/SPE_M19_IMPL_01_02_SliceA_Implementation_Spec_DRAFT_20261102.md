# SPE M19-IMPL-01-02｜Slice A最小実装仕様 DRAFT

**Status:** DRAFT / READ-ONLY DESIGN / NOT APPROVED / NOT IMPLEMENTED  
**Repository:** `spe-flatvat/SPE`  
**Source-code reference:** `754c1e2907bce67f7d58d10bf36813ac76fd1ed0`（調査用固定版。実装対象HEADの指定ではない）  
**Normative reference:** M19-CC09-IR-01統合改訂DRAFT `edc47652f986b75341404154bfd3057da89e9329`、OD20-01の限定承認（対象SHA-256 `151c8d7549f411d622a8b90585b846847fb76436c4e2c4b69073017640fc48ae`）。OD20-01は可変年度実装・正式稼働を承認しない。  
**Scope:** OD14-01案A＝legacy 2026起点、単一路線、政策遷移なし。F/N3/N/F3/R4の統合比較・Trigger・予約は対象外。ただし対象外機能の既存義務は免除しない。

## 1. 既存コードの実際の呼出し境界

- `engine/m10_results.py` の `advance(previous, *, risk_shock, aging_drag, tax_elasticity, expenditure_growth, real_wage_growth_rate=0.0)` は計算関数として再利用候補。
- **重要:** 同ファイルは関数定義後のトップレベルでシナリオJSONを読み、`sys.argv`を解釈し、2026固定初期状態から年次計算を実行し、2027/2028の検査とJSON出力を行う。従って `import m10_results` を副作用なしのライブラリ呼出しとみなせない。
- 実装案：既存CLIを変更せずに、承認済みシナリオをサブプロセス実行して全期間の結果を取得する**試作アダプタ**を第一候補とする。ただし、全期間一括計算とM19の年次Gate・年次確定順序の間に意味論上の不一致があるため、**これだけで正式な年次制御層は完成しない**。
- 正式実装案：`advance`等の純粋な計算機能を副作用のないモジュールに抽出するか、等価なAPIを設け、各年Gate PASS後に1年分だけ呼ぶ。既存M10 CLIの回帰同値性を確認することを変更の条件とする。M10数値意味論は変更しない。
- `m13_input_validate.validate_scenario` は2027以降の連続年度入力、2026アンカーを検証する。`m12_validate.validate_result` は結果構造を検証するが正式確定の権限は検証しない。
- `m18_evaluate.evaluate_result` は2026開始を要求し、2055終点フラグを返す。Slice Aでは既存の評価意味論を変更しない。初年度単年ではM18評価を呼ばない。

## 2. 最小コンポーネントと責務

| 仮称 | 責務 | 制約 |
|---|---|---|
| `m19_controller` | 年度入口、Gate A→C→B、計算attempt、正式確定、翌年度への継続 | 遷移なしの適用性も証拠で確定。Gate Bを自動PASSしない |
| `m19_contracts` | legacy初期状態・年次入力・アンカーの不変参照、適用性、型・単位・出典検証 | 承認されていない2026数値を正式初期値に昇格しない |
| `m19_records` | 実行文脈、Gate証跡、attempt、確定数値結果、正式年度末イベント | append-only／一意キー／不変参照／失敗時非確定 |
| `m19_adapter` | 既存計算意味論を保つ1年単位の呼出し境界 | import副作用を避ける。M10回帰同値性が必要 |
| `tests/test_m19_slice_a` | 正常・異常・再試行・重複・履歴・回帰 | テスト仕様であり、未実行 |

ファイル名・分割は提案であり固定していない。正式承認の前に現在のmainに合わせて変更対象を再固定する。

## 3. データ契約候補（概念スキーマ）

`RunContext`: `execution_id`, `path_id`, `mode=legacy`, `start_year=2026`, `end_year`, `effective_policy_ref`, `applicable_contract_refs`。IDは実行間の衝突を防ぐ。

`InitialStateContractRef`: `contract_id`, `version_or_digest`, `baseline_year`, `approved_state_ref`, `approval_evidence_ref`, `units/provenance_ref`, `applicability`。**Owner承認済み契約の存在を仮定しない**。不足時は正式実行STOP。

`AnnualInputRef`: `year`, `input_contract_id/version_or_digest`, `policy_effects_ref`, `anchor_refs`, `units/provenance_ref`。欠損・矛盾は該当年のGate C FAIL。

`GateRecord`: `execution_id/path_id/year`, `gate`, `applicability`, `checkpoint_reached`, `outcome`, `reason`, `dependency_scope`, `evidence_refs`。Gate B非適用はGate A/C通過後の正式チェックポイントでのみ `NOT_APPLICABLE`、未到達は `NOT_EVALUATED`。

`Attempt`: `attempt_id`, `execution_id/path_id/year`, `input_contract_ref`, `authorization_ref`, `status`, `reason`, `result_digest_if_any`。修復可能な失敗の再試行は正式年度末前、同一承認済み入力契約内に限定。

`FinalAnnualResult`: `execution_id/path_id/year` を一意キーとして、成功attempt、結果digest、前年度正式結果ref、適用契約refを保持。`YearEndEvent`: 同一文脈で成功イベント最大1件、`actor`, `authority`, `prerequisites`, `disposition`, `reservation_resolution_ref_if_applicable`, `final_result_ref`。未適用の予約証拠を捏造しない。

これらは論理フィールドの候補であり、現行規範が要求しない独立した新しい証拠文書や全項目の新規MUSTを自動創設するものではない。既存参照で同等の証明が可能なら再利用する。

## 4. Gate／計算／正式年度末の処理順序

1. 実行文脈と契約参照を固定し、開始年度・モード・政策経路の適用性を検証。
2. `Gate A`: 2026は承認済みBaseline Initial-State Contractと照合。2027以降は同じ経路の**直前年度正式確定数値状態**と必要履歴を検証。異常年度末イベントのみでは通さない。
3. `Gate C`: 対象年の数値入力、政策効果、アンカー、単位、出典、契約参照の整合性を検証。暗黙デフォルトは禁止。
4. `Gate B`: A/C通過後、遷移なしを根拠付きで非適用と確定できる場合のみ `NOT_APPLICABLE` を記録。適用性不明は非適用にしない。
5. 年次計算attemptを開始し、既存数値意味論で年次状態を算出。成功・失敗・契約参照を記録。
6. 年次結果と成功年度末イベントを**同一永続化トランザクション**で確定。実装例はSQLiteトランザクション＋文脈一意制約＋不変digest照合。方式自体はOwner承認対象。
7. 同じ確定要求の再送は同一結果を返す（冪等）。異なる競合確定や確定後再試行は拒否。部分失敗は成功確定とみなさない。
8. 次年度は正式確定数値結果を読み出してGate Aに渡す。年度末異常解決の回復・再初期化は本Sliceの正式実行対象外。

## 5. 原子性・障害復旧（承認候補）

- SQLite等の単一永続化ストアに `UNIQUE(execution_id,path_id,year)` の正式結果、成功年度末イベントの一意制約を設ける。成功結果と年度末イベントは単一commitで書き込む。
- attempt記録は正式結果と分離し、失敗後も不変履歴として残す。クラッシュ後は成功年度末の有無をトランザクション境界で再確認し、確定済みなら再計算しない。
- 同じ要求の再送時に契約・結果digestが異なるなら競合としてSTOPし、既存正式結果を上書きしない。
- 保存場所、トランザクション実装、並行実行制御、故障注入試験は**提案**。現行規範CC04は実装機構の別途承認を要求しているため、IMPL-01-03の承認対象に含める。

## 6. 受入・回帰テスト候補

| ケース | 期待結果 | 前提 |
|---|---|---|
| SA-01 初年度 | 承認済み2026初期契約でGate A/C/B記録と2026初期状態の適切な確定 | 実契約がない場合はfixture試験のみ |
| SA-02 翌年度 | 2027のGate Aが2026正式結果を参照 | 正式結果の永続化 |
| SA-03 Gate C欠損 | 該当年度STOP、正式結果なし | 欠損fixture |
| SA-04 B非適用 | A/C通過後に理由付き `NOT_APPLICABLE`、人工PASSなし | 非遷移の証拠 |
| SA-05 Retry | 失敗attemptと成功attemptが区別され正式結果1件 | 承認入力契約内 |
| SA-06 重複確定 | 冪等再送は同一確定、競合は拒否 | 永続ストア |
| SA-07 クラッシュ | 部分書込みで成功年度末なし、再開時に重複なし | 故障注入 |
| SA-08 M10回帰 | 既存CLI出力と1年APIの同値性（許容誤差明示） | 同一入力・同一版 |
| SA-09 M18回帰 | legacy 2026開始の既存評価結果が変わらない | 既存評価fixture |

工程12の `AT-R01/R02/R03` にSA-05〜07を対応。Trigger `AT-T01/T02`、正式比較 `AT-C01/C02/C03` は後続Sliceで扱い、消滅させない。**実行0件、PASS0件**。

## 7. 承認境界・残課題

**IMPL-01-03で一括判断可能:** (a) 変更対象と固定HEAD、(b) 1年API抽出／アダプタ方式、(c) 永続化・原子性・冪等性の実装機構、(d) 試作／テスト実行の権限、(e) 受入テスト基準、(f) 承認範囲と除外、固定SHA付き承認証跡。

**実装着手と別に正式稼働前までに必要:** 実際のOwner承認済み2026初期状態契約、Gate C数値契約・アンカー・provenance、正式結果の検証、テストPASS、必要な最終受入。これらを満たさずに正式実行したと宣言しない。

**対象外:** configurable開始年度・Player設定の具体的委任契約、政策遷移、R4 Trigger、予約、正式比較、M18評価意味論変更、異常年度末後の数値復旧。OD20-01の限定承認を拡大解釈しない。

**Status:** DRAFT / NOT IMPLEMENTED / NOT APPROVED。GitHub書込み・DecisionLog更新・Finding Close・Freeze・HOLD解除なし。
