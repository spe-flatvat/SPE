# 公的資料と確認範囲

取得日：2026-11-23。全17資料の実バイト指紋はPublic_Source_Receipts.json。国地方の口座帰属・法的権限・年度流動性・既存用途非重複の全条件を満たす2030年の認定資金額は未確定。

| 資料 | 版・場所・単位 | 確認範囲 | 未確認 |
|---|---|---|---|
| [LOCAL_WHITEPAPER](https://www.soumu.go.jp/menu_seisaku/hakusyo/chihou/r08data/2026data/r08czb01-02.html) | 令和8年版/FY2024、第1部2(7)ア・ウ・オ、兆円 | 地方債残高・満期一括基金調整・用途別基金の定義 | 2030取崩・自由資金額 |
| [LOCAL_FUNDS_TABLE](https://www.soumu.go.jp/menu_seisaku/hakusyo/chihou/r08data/2026data/csv/h-014.csv) | 第14表、FY2024末/2025-3-31、D列計、億円 | 財調97786/減債30938/特定166078/計294802 | 口座・自治体別利用権限 |
| [LOCAL_DEBT_TABLE](https://www.soumu.go.jp/menu_seisaku/hakusyo/chihou/r08data/2026data/csv/h-012.csv) | 第12表、FY2024末、E列計、億円 | 地方債1370991 | 実際の満期別償還 |
| [LOCAL_REVENUE_TABLE](https://www.soumu.go.jp/menu_seisaku/hakusyo/chihou/r08data/2026data/csv/h-005.csv) | 第5表、FY2024、C列、億円 | 地方債88506/交付税199346/国庫支出金201862 | 2030移転額・起債枠 |
| [MOF_ACCOUNT_ASSETS](https://www.mof.go.jp/policy/budget/report/public_finance_fact_sheet/fy2024/20260130sagaku02.html) | FY2024末、会計別概要、兆円 | 一般会計預金20.2/基金28.6/財投貸付124.8等 | SNA連結調整・自由資金 |
| [MOF_TREASURY](https://www.mof.go.jp/policy/exchequer/summary/index.htm) | 国庫制度概要、口座と国庫収支、制度説明 | 国庫内部振替・対民収支・政府預金境界 | SNA現金調整額 |
| [MOF_CASH_MANAGEMENT](https://www.mof.go.jp/policy/exchequer/exchequer_cash_management/index.htm) | 国庫余裕金の繰替使用、制度説明 | 限度・返還期限・短期資金繰り | 恒久新規財源額 |
| [DEBT_FUND_FY2024](https://www.mof.go.jp/about_mof/mof_budget/special_account/kokusaiseiri/kokusaiseiri_zaimu2024.pdf) | FY2024附属明細書1(1)①②③、百万円 | 現金402110/有価証券17206992/買現先10779088 | 2030の追加支出権限・利用残高 |
| [ISSUANCE_FY2026_REVISED](https://www.mof.go.jp/jgbs/issuance_plan/fy2026/issuanceplan260603.pdf) | 2026-6-3補正後、p1、億円 | 総額1838055/新規326975/借換1357586/財投130000 | 2030発行枠 |
| [LOCAL_AUTONOMY_LAW](https://laws.e-gov.go.jp/api/1/lawdata/322AC0000000067) | e-Gov取得XML 本則241条・235条の3、法令 | 基金目的と処分、一時借入の年度償還 | 自治体別条例・予算 |
| [LOCAL_FINANCE_LAW](https://laws.e-gov.go.jp/api/1/lawdata/323AC0000000109) | e-Gov取得XML 本則5条・5条の3、法令 | 起債対象と協議等の制度 | N3各支出の適格性・枠 |
| [FINANCE_LAW](https://laws.e-gov.go.jp/api/1/lawdata/322AC0000000034) | e-Gov取得XML 本則4条、法令 | 国債財源に係る原則 | 2030特例法・支出予算の個別実行枠 |
| [SPECIAL_ACCOUNTS_LAW](https://laws.e-gov.go.jp/api/1/lawdata/419AC0000000023) | e-Gov取得XML 本則15/42/46/47条、法令 | 繰替・基金繰入・借換・前倒発行 | 自由な追加経常支出への流用額 |
| [MOF_BALANCE_SHEET](https://www.mof.go.jp/policy/budget/fiscal_condition/related_data/202610_05.pdf) | 2026-10財政資料/FY2024末、PDF | 会計現金預金55.2（出納整理後）・外貨除外会計33.6・実際の年度末政府預金3.9兆円。外為資産は対応債務償還に原則充当 | SNA中央43.308との全調整 |
| [MOF_FUND_FORECAST_2026](https://www.mof.go.jp/policy/budget/topics/outlook/sy2026b.htm) | 2026-2仮定計算、2026〜2035表・前提1〜8、億円 | 2030償還1541400/借換1342900/繰入196600/基金30000 | N3の計画・確定予算 |
| [MOF_DEPOSITS_2025Q4](https://www.mof.go.jp/policy/exchequer/reference/exchequer_report/fy2025_4th_quarter/index.html) | FY2025第4四半期 第3政府預金、億円 | 2025-12末51342→2026-3末21575 | SNA同境界の2025末・2030自由資金 |
| [MOF_FUND_PURPOSE](https://www.mof.go.jp/about_mof/mof_budget/special_account/kokusaiseiri/kokusaiseiri.htm) | 設置目的・制度説明 | 基金は償還・利払いのための区分経理 | 新支出に使える余剰 |

## 継承した出典

内閣府2026年7月計数表の固定Excel・Statistical_Cell_Map.csv、SNA2024部門別ストックはccadca9固定成果と前段原本を再利用。SNA中央・地方の2024現金預金と新取得会計残高は異なる対象のため足し算・差額の機械接続をしない。

## 取得経路

総務省ページはWeb読取で取得不能だったが、実行環境HTTPSでは取得成功。財務省・e-Govは公式URLから実バイト回収。e-Govの動的Web本文が空でもXML APIの本則を読み、附則の同条番号と区別した。制度説明から個別の2030資金額を推定しない。
