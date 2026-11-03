# SPE M19-CC09-IR-01｜工程16 Slice A最小実装契約 DRAFT

**Status:** DRAFT / READ-ONLY DESIGN / NOT APPROVED / NOT IMPLEMENTED  
**Date:** 2026-11-02  
**Owner scope decision:** OD14-01 案A（単一路線・遷移なしの段階的実装）  
**Repository:** `spe-flatvat/SPE`  
**Normative reference:** commit `edc47652f986b75341404154bfd3057da89e9329`, `reviews/M19-25/M19_CC09_IR01/integrated_draft/SPE_M19_CC09_IR01_Rev2_Integrated_Amendment_DRAFT_20261101.md`  
**Existing engine inspection reference:** commit `754c1e2907bce67f7d58d10bf36813ac76fd1ed0` (`engine/m10_results.py`, `m12_validate.py`, `m13_input_validate.py`, `m18_evaluate.py`)  

## 1. 目的と権限境界

既存M10/M14/M17計算意味論とM18評価意味論を変更せず、単一路線・遷移なしの年次計算を制御層から実行できるようにする最小の入出力境界、Gate判定、正式年度末確定、翌年度引継ぎを設計する。**本書は実装契約候補であり、Owner承認・コード変更・テスト実行・Freeze・HOLD解除ではない。**

## 2. 現行規範とPlayer可変化提案の分離

### 2.1 現行DRAFTで明記されている事項（変更なし）

- CC-04: **2026年**はOwner-approved Baseline Initial-State Contractで初期化。契約は年度、必須変数、値、単位、provenance、document anchorsと推定値の区別、Owner approval IDを識別する。数値そのものは未承認。
- CC-04/CC-05: 2026〜2055の各年にGate A→Gate C→Gate B（適用時）を評価。2027年以降のGate Aは実際の前年度正式確定状態を検証。
- CC-04: 同一execution/path/yearにつき正式年次結果と成功した正式年度末は各最大1件。正式年度末の原子性・冪等性・回復機構は別途実装契約承認が必要。
- CC-05: Gate Bが非適用で正式チェックポイントに達した場合、`NOT_APPLICABLE` と理由を記録。単一路線・遷移なしでも「何も記録しない」とはしない。
- Freeze boundary: 2026初期数値契約、M10 adapter、M18 integration、machine-readable schema、実V&Vは未承認。

### 2.2 User/Ownerからの新提案（規範変更候補、未採用）

長寿命化のため、**開始年度と初期値のテンプレートだけをシステム側が提供し、具体的な年度・初期値をPlayerが指定する**。この提案は合理的だが、現行CC-04/05の固定2026境界・2026〜2055期間・Owner-approved baselineをそのまま読み替えることはできない。

設計上の分離案：

1. **Template（構造）**：変数名、型、単位、必須/任意、許容値、出典欄、初期年度、policy/path、schema version。テンプレート自体に2026の数値を既定の承認値として埋め込まない。
2. **Player Configuration（値）**：Playerが開始年度・初期数値・出典を入力し、入力検証を受ける。Player入力は承認済みOwner初期状態契約と同一視しない。
3. **Run Authorization / Baseline Contract（権限）**：現行契約に基づく正式実行ではOwner-approved baselineとの一致・適用範囲を検証する。将来のPlayer裁量型正式実行を可能にするには、適用契約の改訂・承認が必要。
4. **Exploratory Mode（検討候補）**：未承認Player設定での試行計算を認める場合、正式年次結果、正式年度末、比較適格性とは区別する。これは現行契約にない実行モードの**提案**であり、今ここで新しいドメイン値や権限を創設しない。

**重要：** Playerによる値の指定と、値の妥当性検証・正式実行の許可は別の責務。各実行ごとにOwnerの政治的承認を要求する案でもない。テンプレートの承認範囲内でPlayer設定を許容する委任方式は、別途明文化すれば検討可能。

## 3. Slice A最小実装境界（現行規範準拠案）

| 境界 | 入力 | 処理 | 出力・証跡 | 未充足時 |
|---|---|---|---|---|
| Run context | execution/path ID、適用契約ID/版、対象年 | 単一路線・遷移なしを確認 | 実行文脈と契約参照 | 当該実行を停止 |
| Initialization / Gate A | 2026初期状態契約、Owner承認参照、値・単位・出典 | 2026は承認済み契約を検証。以後は前年度正式確定数値状態を照合 | Gate A結果・根拠・対象範囲 | 当該年の依存計算停止 |
| Gate C | 年次入力、政策効果、anchor、単位、数値契約参照 | 欠損を勝手に補完せず検証 | Gate C結果・理由 | 当該計算停止 |
| Gate B | 遷移候補の有無、適用性 | 遷移なしの正式チェックポイント到達時、非適用を確認 | `NOT_APPLICABLE` と理由・checkpoint・scope | 適用性不明なら推定通過しない |
| Numerical adapter | 検証済み前年度状態、年次パラメータ | 既存計算意味論を保持して年次結果を得る | attempt識別子、入力参照、出力候補 | 失敗attemptを正式結果と混同しない |
| Finalization | 成功候補、権限、前提条件、年度文脈 | 1結果・1成功年度末、原子性・冪等性を保証する設計が必要 | 不変正式結果・年度末記録 | 部分失敗を成功と記録しない |
| Next-year carry | 前年度正式確定数値結果 | 当該path/yearの正式結果のみを参照 | 次年度Gate Aの参照 | 異常年度末だけでは継続不可 |

**境界注意：** 既存 `engine/m10_results.py` は2026初期状態をソース内に保持し、2027以降の年次入力を処理してJSONを出力する。これをそのまま「任意年度・任意初期値に対応」と認定しない。M12/M13は既存schema検証、M18は指標算出であり、Gateや正式年度末の代替ではない。

## 4. 最小インターフェース候補（承認前・概念レベル）

```text
BaselineTemplate: template_version, fields[{name,type,unit,required,provenance_rule}], start_year_field
PlayerConfiguration: selected_start_year, initial_values, source_references, selected_policy_path
ApprovedBaselineReference: contract_id, contract_version, approval_reference, applicable_scope
ExecutionContext: execution_id, path_id, year, immutable_input_contract_ref
GateOutcome: gate, applicability, checkpoint_reached, disposition, reason, dependency_scope
CalculationAttempt: attempt_id, execution_ref, input_contract_ref, disposition, output_ref_or_failure_reason
FinalizedYear: execution_ref, path_ref, year, result_ref, finalization_event_ref
```

これらは**設計フィールド候補**であり、機械可読スキーマの承認、新規監査台帳の義務化、既存ドメイン列挙値の追加を意味しない。既存の識別子・記録で充足する場合は重複定義しない。

## 5. 最小回帰・受入境界

- 既存M10/M12/M13/M18の代表ケースと数値結果を変更しない。
- 2026の未承認初期値は正式Gate Aを通さない。承認済み契約が与えられた場合だけ契約適合性を検証できる設計とする。
- 2027の入力は2026の**正式確定**結果を参照し、別pathや未確定attemptから継続しない。
- Gate順序A→C→B、遷移なしでのGate B非適用記録を確認。
- 同一年度の重複finalize・retryで二重確定しない。異常年度末は次年度の数値前提にならない。
- Player可変開始年度については、現行規範準拠の正式受入テストに混ぜず、将来の契約改訂候補として別管理する。

**実施状況：** テスト設計のみ。実行0件、PASS認定0件。既存コードの静的読取であり、網羅的リポジトリ監査ではない。

## 6. Ownerへの最小判断提案（実装承認ではない）

**OD16-01（提案）開始年度・初期値の長寿命化方針**

- **A（推奨）**：テンプレートとPlayer設定を将来の正式仕様方針として採用する。ただし現行CC-04/05と権限境界の改訂案を別途作成し、承認までは2026固定契約を維持する。
- B：2026固定を維持し、テンプレート化のみを先行する。
- C：将来方針を保留し、現行固定契約のみ設計する。

**OD16-02（後続・必要時のみ）**：Player設定がどの条件で正式実行に使用できるか、テンプレート/委任範囲/入力検証/承認境界を規範改訂案で確定する。Playerの各設定変更ごとにOwner承認を要求することは本提案の既定ではない。

**OD16-03（別途）**：正式年度末の原子性・冪等性・障害回復の実装契約とコード変更権限を明示的に承認する。OD16-01だけでは着手不可。

## 7. 判定・STOP

**ENGINE DESIGN DRAFT READY / PLAYER-CONFIGURABLE START NORMATIVE CHANGE PENDING / IMPLEMENTATION NOT AUTHORIZED.**

工程16でSTOP。GitHub書込み、DecisionLog更新、実装変更、正式Finding Close、Freeze、M19–25/RP-023 HOLD解除なし。
