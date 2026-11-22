# SPE｜N3原文22項目の既存実装補完・年次再計算依頼

**Status:** OWNER-ISSUABLE DRAFT / ISOLATED EXECUTION / NON-CANONICAL  
**Repository:** `spe-flatvat/SPE`  
**Target branch:** `work/chatgpt-handoff`  
**Date:** 2026-11-23  
**Years:** 2026–2055

## 1. 目的・固定根拠

N3原文22項目のうち、既存モデルで部分実装・構造のみ・未計量・未解決となっている部分について、**原文と既存データから実装可能な機能を実際に補完し、隔離実行・比較・引渡しする**。原文にない金額・税制・施策・事業・制度を創作して全22項目を形式的にPASSさせない。計画や一覧の作成を実装の代わりにしない。

**主固定成果：** `f62f00a08e9db2ad05b472034c963de1a4f346c4`、`handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123/`。必須 `N3_Native_Policy_Implementation_Coverage.csv`、`SPE_N3_Native_vs_Diagnostic_Separation_Report_DRAFT_20261123.md`、`N3_Native_Diagnostic_Reproduce.py`、`Comparison_Contract_And_Inputs.json`、`N3_Native_vs_Diagnostic_Annual_Comparison_2026_2055.csv`、`N3_Native_vs_Diagnostic_Case_Summary.csv`、`Resolved_Separation_Runtime.py.txt`、`Verification.json`。N3本文 `policies/New3linesPolicies.md` は同固定Commitを読み取り、前段 `65227a9b86f198df62430f541fbee41e3e788b80` の22項目追跡・主体財源表を再利用。前回7経路210年次・差分帰属360行・5,990チェックPASSを再利用する。

既存分類：`IMPLEMENTED_IN_NATIVE` 1項目（VAT固定経路）、`PARTIAL_OR_PROXY` 15項目、`STRUCTURAL_ONLY` 3項目、`NOT_QUANTIFIED` 1項目、`UNRESOLVED` 2項目。**今回の主対象は後者21項目の不足部分**であり、21件すべての数値化を義務化しない。追加G/I診断枠は既存N3施策へ流用しない。

## 2. 補完の優先順位と境界

まず原文・既存コード・固定入力・既存成果を照合し、**原文と既存根拠で実行可能な未接続部分**から実装する。実装不能なものは理由を特定し `NOT_QUANTIFIABLE_FROM_TEXT`、`MISSING_DATA`、`OWNER_POLICY_CHOICE_REQUIRED`、`ALREADY_MODELED` などに分ける。未実装をゼロ効果と決めつけず、架空の予算や係数を導入しない。

重点候補（22項目CSVのpolicy_idに対応）：

- `A_VAT_SWITCH`／`KPI_REVIEW`：2035年の所得成長未達時の税率引上げ凍結、ジニ悪化時の所得連動減免補完等。既存フックと観測系列を確認し、**原文で確定する条件・既存入力で評価可能な部分のみ**を隔離枝で有効化する。観測値・閾値・期間・補完率が未定なら `unknown` を維持し、条件付き入力を別枝に分離。既存固定KPI枝を上書きしない。
- `A_LABOR_TAX`／`A_FINANCIAL_TAX`／`A_ALLOWANCE`／`A_CORPORATE`／`A_ESTATE_GIFT`：既存の税源・控除・法人投資条件・相続贈与の重複排除を保持。実装上の未接続・二重計上・期間のずれを既存資料で補正可能なら隔離補完。全国税源や地方税の未取得データを創作しない。企業残余資金75%再投資は原文確定値ではない既存診断仮定として明示・分離維持。
- `B_PENSION`／`B_MEDICAL`／`B_EOL`／`B_RELIEF`／`B_IN_KIND`：既存の家計・政府・保険者・基金勘定を保持し、原文に沿った未接続の年次経路、給付・負担帰属、制度切替を実装可能な範囲で補完。終末医療の新たな削減額やカード普及費を根拠なく創作しない。現物給付の政府購入G該当性を再加算しない。
- `C_EMPLOYMENT`／`S_PHASE1`／`S_PHASE2`：原文の雇用枠拡大と既存 `REGULARIZE`（純増雇用0）の違い、2030開始・6年ランプと原文2026–2032移行期間のずれを明示。原文にない人数・給与・純増雇用・年度配分を勝手に採用せず、既存モデルで計算できる部分を保持。
- `A_INVOICE`／`B_COOP`／`D_SMART`：インボイス簡素化、共済10〜15ブロック、コンパクト化の順位付けを既存構造から確認。原文だけで確定しない行政節約額、保険効率化額、都市別事業費・公共I額は `unknown`。既存構造に実行可能な非金銭機能があるなら補完するが、金銭効果を捏造しない。
- `S_PHASE3`：2039年以降の定着・最適化を、既存の年金・医療制度経路で表現できる範囲に限定。独自の財政節約額は原文から算出できなければ未計量。
- `B_EITC`／`C_FOREIGN`：EITC廃止の比較ベース未確認、外国人材GDP比5%の分母・定義未確定を維持。既存の外国人材スクリーン・人口接続を再利用し、原文にない移民人数・住宅G/I費を投入しない。

優先度は「既存コード・データだけで動く未接続機能」→「根拠付き小規模補完」→「根拠不足で停止」の順。全21項目の数値改善を目標にしない。既存の実装済み1項目や部分実装の効果を消さない。

## 3. 実行・比較

1. 既存 `N3_NATIVE_EXISTING` を固定比較基準として2026〜2055年を再利用する。
2. **補完後のN3既存施策経路** `N3_NATIVE_COMPLETED_SUPPORTED` を新しい隔離ランタイムで年次実行する。追加G/I診断はオフ、既存の税率・控除・政策原文・共通エンジンを変更しない。必要な新規枝は根拠と入力を別ファイルで明示。
3. 原文に閾値・金額・実施時期等の欠落があり、実装には未採用仮定が必要な場合は `N3_NATIVE_CONDITIONAL_OPTION` として別枝に隔離し、**補完後の原文根拠あり経路へ混ぜない**。条件付き枝は必要なものだけ実行。
4. 既存 `N3_PLUS_GI_DIAGNOSTIC` は原則固定比較対象として再利用。補完後に追加G/Iを重ねる比較が実装可能なら `N3_COMPLETED_PLUS_GI_DIAGNOSTIC` を独立診断として計算し、政策補完と追加G/Iを区別。未採用診断のSQ到達を原文準拠の成果と呼ばない。
5. 年次実質・名目GDP、GDP−SQ、税収、家計所得・消費、民間投資、既存G関連費用・公的I、PB、利払、現金、債務、年金・医療・雇用・保険者・KPIの利用可能な指標を比較。元モデルに存在しない系列はunknown。
6. 2030、2035、2039、2055年、SQ割れ年数、政策別の新規接続、既存経路との差分を報告。**差がゼロなら機能実装の成果と数値効果ゼロ／未発動を区別**し、何が新たにできるようになったかを示す。

## 4. 検証

- 原文22項目の `before_status`、`after_status`、`new_executable_behavior`、`evidence`、`still_missing`、`conditional_only` を全件記録。
- 既存給与差額（2030年0.018672318768兆円）、現物給付（0.275091249212兆円）、既存政府費用合計（0.293763567980兆円）を二重加算しない。コンパクト化順位を公共投資額へ置換しない。
- 年次会計、税・家計・政府・保険者・基金の対応、政府間移転の相殺、名目・実質単位、原文施策と診断G/Iの分離、既存共通系列・固定SQとの比較、原本再現性を検証。
- 既存PASSを再利用し、必要な変更箇所・新規機能のテストだけ追加。追加の4AIレビュー、全面制度再調査、承認工程は自動追加しない。
- 原文全22項目が完全実装されたとの宣言、全国較正、現実の2030年予算・発行権限・国地方別資金閉合のPASSは証拠がない限り禁止。

## 5. 成果物・引渡し

新規保存先 `handoff/chatgpt-n3-native-policy-completion-20261123/` に個別原本で格納（ZIP禁止）：

1. `SPE_N3_Native_Policy_Implementation_Completion_Report_DRAFT_20261123.md`：実装した機能、未実装理由、数値差分、2026–2055結果、実際の進歩。
2. `N3_22_Policy_Coverage_Before_After.csv`：原文22項目の前後比較・根拠・未完了。
3. `N3_Native_Completion_Annual_Comparison_2026_2055.csv`：既存・補完後・条件付き診断・SQの年次比較。
4. `N3_Native_Completion_Case_Summary.csv`：2030/2035/2039/2055、SQ割れ年数、債務・資金の比較。
5. `N3_Implemented_Functions_And_Residual_Unknowns.csv`：実際に動作する新機能と残る制約。
6. 隔離再現コード、入力・ケース定義、検証JSON、実行ログ、固定原本取得・実バイトSHA-256照合記録。

## 6. 権限とSTOP境界

Ownerが本依頼書をWorkへ正式発出した場合、固定原本・既存実装の読取、必要な隔離コード作成・年次実行・検証、`work/chatgpt-handoff` の新規保存先への個別ファイルcommit/pushを許可。既存原本・N3本文・税率・控除・共通エンジン・mainの変更、PR/merge、正式Acceptance、DecisionLog更新、Freeze、Canonical化、HOLD解除は禁止。RP-023／M19–25 HOLD、RP-024 PENDINGを維持。

個別の未計量項目で根拠が欠ける場合はその項目だけSTOPし、実装可能な項目を続行。Ownerに新たな政策判断を強制しない。CUSTODY PASSは固定Commitからの事後取得・原本との実バイトSHA-256とサイズ一致を確認した原本に限定。**実装・年次実行・成果引渡しが未実施なら未完了**と報告し、文書化だけで完了扱いしない。
