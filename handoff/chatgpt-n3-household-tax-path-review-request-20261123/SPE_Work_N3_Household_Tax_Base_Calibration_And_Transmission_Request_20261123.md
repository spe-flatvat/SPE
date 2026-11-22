# SPE｜N3家計課税経路：全国課税基礎・従前税額・控除・消費伝播の限定精査

**Status:** OWNER-ISSUABLE / ISOLATED EXECUTION / DRAFT NON-CANONICAL OUTPUT  
**Repository:** `spe-flatvat/SPE` / **Branch:** `work/chatgpt-handoff` / **Date:** 2026-11-23  
**対象:** 2026–2055年のN3対固定StatusQUO（SQ）比較。**本書はWorkへの正式発出時に限り実行・指定ディレクトリ書込みを承認する依頼書**。

## 1. 目的と固定根拠

直近の原因分析固定Commit `93b8393350eb73dd5ebd803b1ace429aaf4dfe1b`、`handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/` の原本を再利用。必須：`SPE_N3_GDP_Gap_Attribution_Report_DRAFT_20261123.md`、`N3_Baseline_Tax_Cells.csv`、`N3_GDP_Gap_Calibration_Diagnostics.csv`、`N3_GDP_Gap_Transmission_Trace.csv`、`N3_GDP_Gap_All_Case_Intermediate_Accounts.csv`、`N3_GDP_Gap_Counterfactual_Annual_2026_2055.csv`、隔離再現コード。前段の22施策原文対応・97設定・25感度枝は固定Commit `2e2670bacdeb83ff12de13add733d9fb7a4f8b54` 等から必要分のみ再利用。原文は `policies/New3linesPolicies.md`。

既存N3−SQの実質GDP差：2030年−7.595361兆円、2055年−44.970845兆円。給与・事業/金融課税ブロックOFFの2055年差は−11.157268兆円（基準N3比+33.813577兆円）。これは**原文の税制撤回案でも、正しい税源較正後の政策効果でもない**。本作業は、なぜ家計追加負担がこれほど大きいかを実コード・入力・全国母集団で精査し、根拠ある範囲だけ隔離補完・再計算する。

## 2. 作業範囲

1. **課税基礎の完全追跡**：労働・事業所得、金融所得、従前税額、合成所得セル、人数・世帯・所得源泉、控除、非課税・重複所得、名目／実質、年次移行率の実コード・参照入力・集計分母を追跡。2030年の労働・事業proxy295.817492兆円×30%と従前税14.770375兆円、移行1/3による追加負担24.658291兆円、金融追加1.159466兆円、2055年労働・事業追加102.658687兆円、金融追加4.827151兆円を再現・説明。原文の税率と未較正の税源・従前税割当を区別。
2. **母集団・会計整合**：所得セルの平均一致だけで全国較正PASSとしない。税収・給与総額・事業/金融所得・納税者/世帯・所得控除と従前負担の母集団、対象年、価格基準、税源重複、他税目への波及を検証。固定資料に根拠ある実数値があれば利用し、外部資料の取得可否・年次適合を明記。根拠のない全国税源、税額、控除、税率、移行日程を創作しない。
3. **消費・GDP伝播**：税負担→家計可処分資源→Ctarget→C_state→GDP、所得還流と内生課税基礎、MPC0.72・国内比0.8・平滑化0.6等の既存仮定を追跡。税源変更と行動係数変更を混同しない。金融課税と給与・事業課税を識別可能な範囲で分離し、年金・法人・VAT・相続・医療等の経路を固定する。
4. **限定隔離反実仮想**：基準N3・固定SQを再現し、**根拠のある**税源・従前税額・控除等の補正候補のみ隔離ケースで2026–2055年再計算。データ不足なら、同一基準で「識別可能な機械的境界・感度」と「較正値不明」を明示して実行し、政策採用としない。原文の30%・金融20%等を任意に変更してSQ超えを演出しない。年金ブロックは既存基準で固定し、相互作用が残る場合はそのまま記録。
5. **比較・識別限界**：基準N3・固定SQ・課税ブロックOFF・実行した較正候補を年次比較。GDP差、C状態、税収proxy、家計所得、PB/現金等を提示。SQ割れ年数、2030/2035/2039/2055、2055年の2026年開始水準との差も参考として表示するが、**当面の比較目標はSQ超え**。未実装政策の現実効果はunknown。

## 3. 引渡し成果物

`handoff/chatgpt-n3-household-tax-path-review-20261123/` に個別ファイル（ZIP禁止）で保存：
- `SPE_N3_Household_Tax_Path_Review_Report_DRAFT_20261123.md`（結論、根拠、補正前後、未解決）
- `N3_Household_Tax_Base_And_Prior_Tax_Trace.csv`（年・税源別・分母・控除・従前税・移行率・コード・出典）
- `N3_Household_Tax_Calibration_Gaps.csv`（実測、代理、unknown、必要データ）
- `N3_Household_Tax_Consumption_Transmission.csv`（家計→Ctarget→Cstate→GDP）
- `N3_Household_Tax_Annual_Counterfactual_2026_2055.csv` とケース定義
- 再現用隔離コード/入力、実行ログ、検証結果、原本取得と保全照合記録。

**検証：** GDP恒等式残差、税源/従前税/控除の二重計上、名目・実質変換、所得セルの集計母集団、固定SQと年金ブロック不変、追加G/I OFF、再現性。前段13,928件・32,439件の同一固定対象PASSは再利用。新規部分だけ必要な検証を実行。

**実務完了：** 原本取得→経路追跡→実行可能な限定補正/反実仮想→年次比較→個別成果引渡し。全国較正ができない場合は実行済み診断と未達を明示し、資料作成だけを完了としない。

## 4. 権限と制約

本依頼書がOwnerからWorkへ正式発出された場合に限り、必要な読み取り、隔離実装・実行・検証、`work/chatgpt-handoff` の上記新規成果ディレクトリへのcommit/pushを承認。既存原本、N3政策本文、税率・控除の正式値、SQデバフ、共通エンジン、main、年金本体は変更禁止。PR/merge、正式Acceptance、DecisionLog、Freeze、Canonical化、HOLD解除なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。固定Commit事後取得と実バイトSHA-256・サイズ一致が確認できた場合のみCUSTODY PASS。Ownerへの既存資料再提出要求や追加レビュー工程は不要。
