# SPE M19-CC09-IR-01｜工程17 可変開始年度・Player初期値設定の規範改訂 DRAFT

**Status:** DRAFT / NORMATIVE CHANGE PROPOSAL ONLY / NOT APPROVED / STOP  
**Date:** 2026-11-02  
**Repository:** `spe-flatvat/SPE`  
**Owner decisions:** OD14-01 案A（Slice A単一路線・遷移なし）、OD16-01 案A（可変開始年度・初期値テンプレート＋Player設定を将来方針として採用）  
**Baseline under review:** commit `edc47652f986b75341404154bfd3057da89e9329`, `reviews/M19-25/M19_CC09_IR01/integrated_draft/SPE_M19_CC09_IR01_Rev2_Integrated_Amendment_DRAFT_20261101.md`  
**Existing code inspection:** commit `754c1e2907bce67f7d58d10bf36813ac76fd1ed0`, `engine/m10_results.py`, `engine/m13_input_validate.py`, `engine/m18_evaluate.py`  
**Input:** 工程16最小実装契約DRAFT、OD16-01 Owner裁定

## 1. 目的・変更境界

OD16-01に従い、シミュレーション開始年度と初期値をPlayerがテンプレートから設定できる将来仕様について、現行規範との差分と最小改訂文案を作成する。**本書は既存Control Contractの改訂そのものではない。** Ownerの別途承認、GitHub書込み、実装着手、Freeze、HOLD解除を含まない。

「Playerが数値を指定する」ことと「その数値が正式な実行入力として適格である」ことを分ける。Ownerは規範・委任範囲・テンプレート契約を承認し、Playerの委任範囲内の個別設定ごとにOwner承認を繰り返すことを既定としない。数値の妥当性は承認済みテンプレートと適用検証契約で判定する。

## 2. 原文固定前提と衝突箇所

| 領域 | 現行DRAFTの根拠 | 改訂要否 |
|---|---|---|
| CC-04 初期化 | 2026年、Owner-approved Baseline Initial-State Contract。年度・変数・値・単位・出典・Owner承認ID | **要**：Owner承認対象をテンプレート/委任規則へ一般化し、Playerの値と混同しない |
| CC-04 年次範囲 | `t in 2026–2055`、2027年以降は前年度正式確定状態 | **要**：初年度 `s` と翌年度 `t>s` を定義。終点 `e` は別論点 |
| CC-04 2026遷移 | 2026対象遷移の別承認・禁止境界、架空2025状態禁止 | **要**：初年度遷移の扱いは単純置換しない。独立の遷移権限は維持 |
| CC-05 Gate A | 2026契約検証、2027以降前年度正式状態 | **要**：初年度／継続年度へ一般化 |
| CC-05 Gate C | 数値入力、効果、アンカー、単位、provenance、immutable refs | **維持＋適用年度の明示** |
| CC-08 正式比較 | 比較契約、基準・期間・方法・全明示条件、M18等の参照 | **維持**：開始年度の違いは契約適格性で評価し自動的に比較可能としない |
| M18評価 | 現行コードは2026開始必須、2055終点判定 | **別実装変更が必要**：本工程では意味論変更を承認しない |
| Freeze境界 | 2026数値契約・M10 adapter・M18 integration・V&V等は未承認 | **維持** |

## 3. 規範改訂候補（置換・追記の提案文。未承認）

以下の `PROPOSED` は文案であり、現行MUSTではない。既存の制約を残すべき箇所は「維持」とする。

### P17-01｜CC-04 Initialization：置換候補

> **PROPOSED — Initialization:** For an authorized simulation run, the initial year `s` and the initial numerical state SHALL be selected by the Player within the scope of an Owner-approved Initial-State Template and its applicable delegation/validation contract. The template SHALL define required variables, types, units, admissibility and consistency checks, provenance requirements, version and applicability. The Player configuration SHALL identify `s`, values, provenance and the applicable immutable template/validation-contract references. A Player selection is not itself an Owner approval or a waiver of validation. A run SHALL NOT be formally initialized when required values, references, delegation applicability or validation are missing, contradictory or invalid. A separately approved fixed-baseline run MAY continue to use an Owner-approved numerical baseline contract.

**注:** `SHALL`は本DRAFTの改訂候補に限る。templateの実際の変数・許容範囲・委任対象は未承認。承認済みテンプレートがない状態で任意値を正式実行できるとはしない。

### P17-02｜CC-04 年次・Gate A：置換候補

> **PROPOSED — Annual sequencing:** For a run with authorized start year `s` and authorized end year `e`, the controller SHALL process each applicable year `t` in `[s,e]` in Gate A → Gate C → Gate B order, where Gate B is applicable. At `t=s`, Gate A SHALL validate the approved template, delegation scope and Player initial-state configuration (or the separately approved fixed numerical baseline). For `t>s`, Gate A SHALL validate the actual finalized numerical state and required history for `t−1`. No fictitious finalized state for `s−1` SHALL be required or fabricated. An abnormal year-end event alone SHALL NOT satisfy next-year numerical continuation.

**注:** `e` のPlayer自由指定は本提案では承認しない。現行2055終点を保持する暫定案と、終点契約を別途承認する案を区別する。`s<=e`、必要最低年数、年次連続性はテンプレート・実行契約で定義する。

### P17-03｜CC-05 Gate A/C：最小追記候補

> **PROPOSED — Gate A:** On the authorized initial year, validate the applicable initial-state template, delegation/validation contract and Player-selected initial state, or the applicable approved fixed-baseline contract. On each subsequent year, validate the actual finalized preceding-year numerical state and required history. **Gate C** continues to validate numerical inputs, policy effects, segment anchors, coverage, units, provenance and immutable numerical-contract references for the actual target year; missing values SHALL NOT be silently defaulted.

Gate Bの適用判定・チェックポイント・`NOT_APPLICABLE`理由記録は変更しない。Player初期値設定だけで政策遷移、予約、Decisionが自動承認されることはない。

### P17-04｜初年度遷移の非自動化：CC-04境界維持・一般化候補

> **PROPOSED — Initial-year transition boundary:** Validation of an initial state for year `s` SHALL NOT by itself authorize a transition candidate targeting `s`. Any such candidate requires the independently applicable transition authorization, Decision, reservation, destination-contract and Gate validations. Missing or conflicting required authorization fails closed for the dependent transition, without blocking independently authorized initialization or incumbent-policy calculation. No fictitious finalized state for `s−1` may supply authorization or numerical history.

既存2026遷移に固有の条項を単純削除せず、旧2026実行における同等の禁止効果を保存すること。

### P17-05｜CC-08・比較／評価：追記候補

> **PROPOSED — Comparison and evaluation boundary:** Configurable initialization SHALL NOT imply that runs with different start years, initial states, template versions or evaluation periods are formally comparable. Formal comparison eligibility remains subject to every expressly required condition of the approved comparison contract, including period, baseline compatibility, metric definitions, methodology and required M18 references. The existing M18 evaluation semantics remain unchanged until separately approved and tested.

## 4. 後方互換性・移行

1. 既存2026初期値と2027以降入力は**歴史的再現用の固定設定**として保存する。2026数値を一般テンプレートの暗黙既定値／普遍的承認値にしない。
2. 既存の2026開始・2055終点の計算・M18評価は、既存意味論と回帰出力を維持する。旧形式の参照・契約版を新形式へ黙って書き換えない。
3. 新方式の正式実行は、Owner承認済みテンプレート・委任/検証契約・適用範囲が存在する場合のみ認める。未承認のPlayer設定を正式年次結果と誤認しない。
4. 年度可変化はM10初期状態、M13の2027開始/2026アンカー、M18の2026開始制約に波及する。コード修正・schema・V&Vは別途承認する。
5. 2055終点の固定維持案は実装移行を小さくするが、将来の2056以降の寿命を保証しない。終点の可変化・評価期間の一般化は別の承認論点として保持する。

## 5. 影響分析・未解決事項

| ID | 論点 | 判定・扱い |
|---|---|---|
| G17-01 | Owner-approved numerical baselineからPlayer値への権限境界変更 | **Major / Owner承認が必要**。テンプレート承認と値の個別承認を分離する |
| G17-02 | `2026–2055`、2026/2027 Gate A境界の一般化 | **Major / Owner承認が必要**。年次履歴の偽造禁止を維持 |
| G17-03 | 2026遷移禁止の一般化と独立承認根拠 | **Major / 条項ごと再照合**。初年度遷移を暗黙許可しない |
| G17-04 | M10/M13/M18の年度固定 | **Implementation OPEN**。既存コード対応済みとは認定しない |
| G17-05 | 終点2055・M18評価・2056以降 | **OPEN / 別裁定**。開始年度変更だけでは長寿命化を完遂しない |
| G17-06 | 初期値の変数集合、許容範囲、出典、アンカー、テンプレート版 | **OPEN / schema・検証契約待ち**。具体値を創作しない |
| G17-07 | 正式比較での異なる開始年・初期値の扱い | **既存CC-08適格性維持**。自動比較適格としない |

## 6. 最小検証ケース（未実行）

- V17-01: Playerが承認済みテンプレートの範囲内で開始年・初期値を設定 → 初年度Gate Aで検証可能。個別Owner承認を追加要求しない。
- V17-02: 必須初期値・単位・出典・契約参照が欠落 → 依存正式初期化をfail-closed。
- V17-03: 初年度 `s` に架空の `s−1` 正式結果を要求しない。`s+1` では実際の `s` 正式結果を要求。
- V17-04: 初年度に遷移候補があるが独立承認がない → 遷移だけを停止し、独立に承認された初期化を妨げない。
- V17-05: 既存2026固定シナリオ → 既存数値・M18評価が回帰一致。
- V17-06: 異なる開始年・初期値の比較 → 比較契約の全条件を検証し、未充足なら正式比較を停止。
- V17-07: 2027/2030等の可変年度実行 → M10/M13/M18の別途改修とテスト完了前はREADYと判定しない。

**実行:** 0/7、PASS: 0/7。

## 7. Owner判断候補（今回のOD16-01で自動承認されない）

**OD17-01（提案）:** P17-01〜P17-05を規範改訂の検討基準として採用するか。採用しても本文改訂・Freeze・実装権限は別途。

**OD17-02（必要時のみ）:** 初期実装では2055終点を維持し、終点可変化を別工程とするか。これはエンジン寿命に影響するため、無断で決定しない。

**OD17-03（後続）:** テンプレート／委任範囲／入力検証契約の具体仕様と実装承認。Player個別設定のたびにOwner承認を要求することを既定としない。

## 8. 工程17判定・STOP

**NORMATIVE AMENDMENT DRAFT READY / OWNER APPROVAL PENDING / IMPLEMENTATION NOT AUTHORIZED.**

本書はOD16-01の将来方針を具体化したDRAFT。規範の正式改訂、数値初期値の承認、テンプレート承認、コード修正、GitHub書込み、DecisionLog更新、Finding Close、Freeze、M19–25/RP-023 HOLD解除は行わない。工程17でSTOP。
