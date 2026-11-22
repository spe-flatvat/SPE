# SPE｜N3原文準拠経路と追加G/I診断経路の分離・年次再計算依頼

**Status:** OWNER-ISSUABLE DRAFT / ISOLATED EXECUTION / NON-CANONICAL  
**Repository:** `spe-flatvat/SPE`  
**Branch:** `work/chatgpt-handoff`  
**Date:** 2026-11-23  
**Period:** 2026–2055

## 1. 目的

N3の既存原文準拠モデルと、未採用の追加政府購入G・公共投資Iを投入するGDP補強診断モデルを**独立した比較経路**として再現可能に分離する。政策本文に実際に存在する効果と、後から加えたG50/I25診断枠による増分を混同しない。政策原文・共通エンジン・税率・控除は変更せず、既存隔離ランタイムを再利用して年次実行・差分照合・成果引渡しを行う。

固定主成果Commit：`65227a9b86f198df62430f541fbee41e3e788b80`、`handoff/chatgpt-n3-policy-gi-executor-financing-mapping-20261123/`。最低限 `SPE_N3_Policy_GI_Executor_Financing_Mapping_Report_DRAFT_20261123.md`、`N3_Policy_Implementation_Expenditure_Trace.csv`、`N3_2030_GI_Allocation_And_Unresolved_Shares.csv`、`N3_Policy_GI_Annual_Comparison_2026_2055.csv`、`N3_Existing_Native_Payroll_Benefits_And_Priority.csv`、`N3_Policy_GI_Mapping_Reproduce.py`、`Conditional_Executor_Routing_Inputs.json`、`N3_Case_Definitions.csv`、`Verification.json`、`Artifact_SHA256.json`を取得・再利用。

N3原文：`policies/New3linesPolicies.md`（同固定Commit）。必要に応じ前段 `c087a1a5af12b86cdb140d934754d75e5ee9c4ef`（財源権限・有限枠）、`5c2cdad05119d453e2c0bf002cca4795e5de26b5`（国地方現金）、`ccadca9f5435be5db4cbda1c9f5170c13ee0bf0b`（SFA）を参照。前回4ケース・120年次／3,580チェック、別途120マクロ同値比較、既存の検証PASSを再利用し、無意味な全件再監査を行わない。

**前回確定した区別：** 2030年既存給与差額0.018672318768兆円、現物給付0.275091249212兆円、合計既存N3固有政府費用差0.293763567980兆円は基礎経路内の効果であり、追加Gへ再加算しない。コンパクト化は仮想地域順位付けまでで、原文事業費・主体・財源は未実装。2030年の追加G8.603651217988兆円・I2.581095365396兆円は未採用G50/I25診断の実執行候補で、原文費目・国地方予算への配賦は全額未確定。統合借入候補11.185302765540兆円はSFA全額現金用途等の条件付き値であり、実際の2030年発行枠ではない。

## 2. 作業A：比較契約の固定と実装経路分離

同一のSQ定義、初期条件、外生ショック、人口、価格、税・控除、利率、SFA仮定、既存N3部品、計算期間を維持し、差分の原因を**追加G/Iの有無とその資金制約**へ限定する。既存の基礎モデルに既に含まれるN3政策効果は残す。

最低限の経路：
- `SQ_REFERENCE`：既存固定のSQ参照年次系列をそのまま利用。SQ定義を新規創作・変更しない。
- `N3_NATIVE_EXISTING`：原文対応の既存実装・既存政府費用・家計・企業・税・医療・年金等を保持し、未承認の追加G/I診断枠をオフにした経路。既存の `NO_UNAPPROVED_ASSIGNMENT` との同一性を年次で検証し、同一なら再利用、異なるなら差異の原因を特定。**「原文全施策を完全実装済み」の意味ではない**。
- `N3_PLUS_GI_DIAGNOSTIC`：既存の `CONDITIONAL_FINITE_GI_BUDGETS` または同一最終G/Iの `CONDITIONAL_CENTRAL_EXECUTOR`／`CONDITIONAL_MIXED_WITH_TRANSFERS` を再利用。未採用G50/I25・企業75%、有限年度G/I上限・統合現金借入上限を保持。2030年G8.603651218、I2.581095365兆円は条件付き追加支出であってN3原文の予算ではない。
- 必要な場合のみ `N3_PLUS_G_ONLY_DIAGNOSTIC` と `N3_PLUS_I_ONLY_DIAGNOSTIC` を隔離計算してGとIの寄与・交互作用を確認。ただし既存比較枝で正確に代用できる場合は再計算しない。G/Iの寄与は非線形・動学相互作用があるため単純加算を強制しない。

`N3_NATIVE_EXISTING` と診断枝で、SFA現金用途・借入上限・予算上限等の設定が違う場合は**「追加G/Iの純効果」ではなく「追加G/I＋資金制約の複合効果」**として表示する。可能なら共通資金制約の下で追加G/Iのみ切り替えた対照ペアを限定追加し、純増効果と資金条件差を分離する。実行不能なら理由を明示し、混合差分を純効果と呼ばない。追加借入を無制限・実際承認済みとは扱わない。

## 3. 作業B：原文準拠の実装範囲を明示

N3原文22項目と既存実装追跡表を再利用し、各施策を `IMPLEMENTED_IN_NATIVE`、`PARTIAL_OR_PROXY`、`STRUCTURAL_ONLY`、`NOT_QUANTIFIED`、`UNRESOLVED` に区分。開始年、既存数値仮定、経済経路、出力系列、原文との差、追加G/Iとの重複可能性を記録。

特に雇用REGULARIZE（対象10万人等は原文にない既存仮定、2030年開始、純増雇用0）、既存現物給付、社会保障・税・企業投資、コンパクト化の仮想順位、2035 KPI切替、共通医療・資本更新との接続を確認する。未実装施策を勝手なパラメータで埋めて「完全原文準拠」に昇格させない。N3専用Annex未特定の既存結果を維持し、F用Annexを転用しない。

政策効果の帰属は二重計上を避ける。既存給与差額・現物給付を追加G8.603651から自動控除したり、追加Gへ再加算したりしない。コンパクト化の仮想順位を追加I2.581095の事業費と呼ばない。G/I診断をオフにしてもN3本体の政策効果が残ることを年次で検証する。

## 4. 作業C：2026〜2055年次実行と差分

原文既存経路、SQ、追加G/I診断経路の2026〜2055年を揃え、最低限、実質・名目GDP、GDP−SQ、名目G・公的I・民間I、家計所得・消費、税収、PB、利払、国債・債務、現金・資金不足、既存給与・現物給付、人口・価格・ショックの比較可能な系列を引き渡す。元モデルにない系列は `unknown` とし創作しない。

各年について `native_minus_SQ`、`diagnostic_minus_SQ`、`diagnostic_minus_native`、必要なら共通資金条件での追加G/I純差分を計算。2029〜2032年と2055年を重点に、2030年の差、全期間SQ割れ年数、最悪年・累積差、2055年債務等を報告。差分の整合（診断−SQ＝（原文既存−SQ）＋（診断−原文既存））と基礎N3部品の保持、名目実質単位、G/Iと移転の非重複を検証。

直前の `NO_UNAPPROVED_ASSIGNMENT` の2030 GDP−SQ −7.595361兆円、`CONDITIONAL_CENTRAL_EXECUTOR` のほぼ0、条件付き借入11.185303兆円、SQ割れ0年という結果は**照合基準**であり、必ず新しい数値が改善することを目的としない。既存結果と一致するなら「再現性確認」とし、今回新たにできたこと（N3本体と診断増分の独立比較・政策別実装範囲の可視化）を明示する。

## 5. 判定と成果物

保存先：`handoff/chatgpt-n3-native-vs-diagnostic-separation-20261123/`。ZIPでなく個別ファイル：
1. `SPE_N3_Native_vs_Diagnostic_Separation_Report_DRAFT_20261123.md`：比較契約、施策別実装範囲、年次結果、純増効果と複合効果、未完了。
2. `N3_Native_Policy_Implementation_Coverage.csv`：22項目と原文・既存コード・実装状態・未実装。
3. `N3_Native_vs_Diagnostic_Annual_Comparison_2026_2055.csv`：SQ、原文既存、追加G/I、差分の年次系列。
4. `N3_Native_vs_Diagnostic_Case_Summary.csv`：2030・2055・SQ割れ年数、資金・債務。
5. `N3_Diagnostic_Increment_And_Funding_Attribution.csv`：追加G/I純効果と資金条件差の識別状態。
6. 隔離再現コード、比較契約・入力、実行ログ、検証JSON、固定原本照合記録。

判定は①N3既存経路の再現、②診断経路の再現、③比較条件の同一性・差分整合、④原文施策の実装充足、⑤2030年の現実財源・支出権限、⑥全期間SQの現実成立を分ける。④〜⑥は根拠なくPASSとしない。**本依頼の実成果は原文既存と追加診断の独立した年次系列・差分・再現コードの引渡し**であり、2030年現実財源の確定や原文の全面実装を完了条件に追加しない。

## 6. 権限と引渡し

Ownerが本依頼書をWorkへ発出した場合、既存固定成果・N3原文の読取、必要な隔離実装・年次実行・検証、`work/chatgpt-handoff` の上記新規保存先への個別ファイルcommit/pushを許可。main・既存原本・政策本文・税率・控除・共通エンジンの変更、PR/merge、正式Acceptance、DecisionLog更新、Freeze、Canonical化、HOLD解除は禁止。RP-023／M19–25 HOLD、RP-024 PENDING維持。追加レビューや承認工程を自動追加しない。

成果物のCUSTODY PASSは固定Commitからの事後取得・原本との実バイトSHA-256とサイズ一致を確認したものだけに限定。生成・実行・検証・成果引渡し・保全を分けて報告し、実行不能部分は具体的制約を記録。現実の2030年予算・国地方資金閉合・SQ成立は引き続き未確定として扱う。
