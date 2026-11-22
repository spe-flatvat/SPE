# SPE｜N3年金経路：75歳移行・基金運用益源泉・家計／政府／基金勘定の限定精査

**Status:** OWNER-ISSUABLE / ISOLATED EXECUTION / DRAFT NON-CANONICAL OUTPUT  
**Repository:** `spe-flatvat/SPE` / **Branch:** `work/chatgpt-handoff` / **Date:** 2026-11-23  
**対象:** 2026–2055年N3対固定StatusQUO（SQ）。本書はOwnerによるWorkへの正式発出時に実行・指定成果ディレクトリ書込みを承認する依頼書。

## 1. 目的と再利用原本

固定Commit `93b8393350eb73dd5ebd803b1ace429aaf4dfe1b` の `handoff/chatgpt-n3-gdp-gap-causal-attribution-20261123/` を再利用。必須：`SPE_N3_GDP_Gap_Attribution_Report_DRAFT_20261123.md`、`N3_GDP_Gap_Transmission_Trace.csv`、`N3_GDP_Gap_All_Case_Intermediate_Accounts.csv`、`N3_GDP_Gap_Fiscal_Cash_Debt_Ledger.csv`、`N3_GDP_Gap_Counterfactual_Annual_2026_2055.csv`、再現コード。前段固定Commit `2e2670bacdeb83ff12de13add733d9fb7a4f8b54` の年金勘定・利回り/政府負担感度、`e8bea03671225189c6af5ccc7a4ec5cbb27817f0` の年金実装補完、`policies/New3linesPolicies.md` のN3原文を必要範囲で使用。

現行N3−SQの2055年実質GDP差−44.970845兆円、年金ブロックOFFは−33.152556兆円（基準比+11.818289兆円）。年金OFFは75歳コホート移行・拠出振替・基金・国内家計運用益対応をまとめて停止する診断枝であり、制度撤回や原文効果の確定を意味しない。前回利回り2%→1%/3%で2055年GDP+0.831/−0.986兆円という逆向きの機械的反応は、国内家計所得から基金への振替構造に依存。政府負担50%→25/75%はGDP差0でもモデル現金に約−109/+109兆円の差がある。**本件はこの勘定と消費伝播が妥当かを実行で精査する**。

## 2. 実施内容

1. **制度・年次実装経路**：原文の75歳移行、対象コホート・受給人数、拠出・給付・基金運用・移行年・遅行、現行の既存コード・入力・実現値を2026–2055年で追跡。制度原文で未指定のコホート、給付率、移行条件、基金収益源は未確定と記録。
2. **三部門勘定の整合**：家計、政府、年金基金の期首残高・拠出・給付・運用益・政府負担・期末残高、資産/負債と現金のフローを追跡。国内家計から基金への「運用益相当振替」の原資、受益者、対応する家計所得減少と基金資産増を照合。**運用益を新たなGDP生産とみなさず**、二重控除・二重計上・純移転と純増所得の混同を検証。政府負担変更でGDP差0となる接続の有無を明示。
3. **消費・GDP伝播**：公的年金給付差、基金給付、基金運用益の家計源泉振替、拠出、税・可処分資源、Ctarget→C_state→GDPを再構成。報告書の2055年C状態源泉（公的年金−10.174233、基金給付+0.283110、運用益振替−1.551784兆円）を確認。源泉額と政策OFF因果差を区別。年金基金の運用利回りと消費への符号が経済的・会計的に妥当かを特定。
4. **限定反実仮想**：既存固定SQと家計課税ブロックを維持した基準N3を再現。必要な最少の隔離ケースで、国内家計振替の有無／原資の別勘定処理／二重計上修正候補／政府負担接続を**診断用の未採用枝**として2026–2055年比較。正しい構造を原文や実データで確定できない場合は、条件付き機械的試験として明示し、モデル本体へ採用しない。既存1%/2%/3%利回りと25%/50%/75%負担の結果を再利用し、同一試験を理由なく再実行しない。
5. **較正と識別限界**：年金対象人数、コホート、平均給付、拠出基礎、国内外資産配分、運用益の受益者・税扱い、政府負担の財源、物価・賃金スライドについて、根拠あり/代理/unknownを区別。全国較正後のGDP寄与額を捏造しない。税・年金相互作用（2055年+0.269451兆円）を独立効果へ勝手に配賦しない。
6. **結果比較**：2030/2035/2039/2055、SQ割れ年数、年次GDP差・C状態・基金・政府・家計残高、2026年起点実質GDPとの差を示す。当面の比較目標はSQ超えだが、目標合わせの調整は禁止。

## 3. 成果物・検証

`handoff/chatgpt-n3-pension-path-review-20261123/` に個別Markdown/CSV/JSON/隔離Python・ログで引渡し（ZIPなし）：
- `SPE_N3_Pension_Path_Review_Report_DRAFT_20261123.md`
- `N3_Pension_Cohort_Benefit_Contribution_Trace.csv`
- `N3_Pension_Household_Government_Fund_Annual_Ledger.csv`
- `N3_Pension_Investment_Return_Source_And_Transfers.csv`
- `N3_Pension_Consumption_GDP_Transmission.csv`
- `N3_Pension_Counterfactual_Annual_2026_2055.csv` とケース定義
- `N3_Pension_Calibration_Unknowns.csv`、隔離再現コード/入力、実行ログ、検証・保全記録。

**検証：** 基金残高恒等式、政府・家計・基金の移転対称性、資産運用益の原資・二重計上、現金/債務とGDPの非自動接続、年次名目・実質整合、既存税ブロック/SQ/追加G/I OFF不変、GDP算術残差、再現性。固定同一対象の前回PASSは再利用。必要な新規実行・検証のみ行う。

**実務完了：** 原本取得→年金実コード/勘定追跡→実行可能な限定構造反実仮想→2026–2055年比較→個別成果引渡し。正しい年金構造が特定不能なら未識別の根拠と未完了範囲を報告し、計画書だけで完了扱いにしない。

## 4. 権限境界

Ownerが本依頼書をWorkへ正式発出した場合、必要な読み取り・隔離実装・実行・検証と `work/chatgpt-handoff` の上記新規ディレクトリへのcommit/pushのみ承認。N3原文、税率・控除、年金の正式制度、SQ、共通エンジン、既存原本、mainは変更しない。PR/merge、正式Acceptance、DecisionLog、Freeze、Canonical化、HOLD解除なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。固定Commit事後取得・実バイトSHA-256・サイズ一致のときだけCUSTODY PASS。家計課税依頼とは独立実行可能とし、相互作用の数値統合は既存2×2結果を利用。新たな横断レビュー・Owner承認工程を追加しない。
