# SPE｜共通リスク別回復期間の限定感度計算
Status: OWNER AUTHORIZATION BY WORK MESSAGE / LIMITED EXECUTION / NON-CANONICAL
Repository: spe-flatvat/SPE
Branch: work/chatgpt-handoff
成果先: handoff/chatgpt-risk-specific-recovery-20261124/
期間: 2026–2055

## 目的・固定参照
前回のGDP原因分解の実成果を再利用し、リスク別回復期間によるF・SQ・N3の実質GDP経路の差を実計算する。前回最終固定Commit adb373d87c5beb68b35f84be9e504c84d67014e0、handoff/chatgpt-common-macro-gdp-attribution-20261124/ の Report.md、Run.py、Dependencies.json、Event_Schedule.csv、Recovery_Events.csv 等を使用。共通比較固定版 8a8edb403b960cceb535f9b70461646e9374c229、Claude検算 da79ab621de27a1a2df8dd3edf050e4f02fac63a の既存PASSを再利用する。固定系列はSQ_COMMON_ON、共通医療参照接続F、N3 BASE_REPLAY追加G/I OFF。

## 1. 原本優先
固定Commitの policies/ 全施策原本・Annex、specifications/ のv5/v6等を確認し、リスク発生年、損失率、継続・回復期間の明示を引用箇所とともに短く記録。明示値を優先し、今回の仮定と矛盾する場合は原本準拠枝を優先、仮定枝は別表示。未記載を永続損失の正式指定と解釈しない。GDP水準回復と税収・物価・賃金ショックの期間を混同しない。原本変更なし。

## 2. 4条件比較
A 現行永続損失、B 全イベント5年線形回復は前回原票を再利用。
C 大規模5年・小規模1年、D 大規模5年・小規模2年を新規実計算。
大規模: 2027中台紛争5%、2031南海トラフ3%。小規模: 2029起点3年毎災害1%、2028起点隔年気候0.5%、オイルショック3%（現行2026初期適用OFFを維持し、C/Dでも発動させない）。回復年数は原本に明示がない場合の非採用診断。発生年の年間損失を保持し、翌年から線形に縮小、発生年+n年に残存損失ゼロ。1年は翌年ゼロ（年度内回復の年次近似）、2年は翌年半分・翌々年ゼロ。重複イベントは個別残存係数の乗算。前回Bと同一の回復式・固定非コア需要・供給上限再計算を用い、Aとの加算/乗算規約差を明示。気候の恒久的生産性損失は今回新設しない。価格・財政・政策内生フィードバックは固定または対象外。完全動学再実行と称さない。

## 3. 実成果
C/D×3系列×30年=180新規ケース年次を計算。A/B既存180ケース年次と区別し、4条件×3系列の実質GDP、コア、人口、一人当たり実質GDP、供給制約、残存リスク係数、F−SQ/N3−SQ/F−N3差を比較。2026/2030/2035/2045/2055主要年、初期580回復年（未回復なら明示）、2055差、期間累積GDP差（年次フロー合計、兆円・年相当）を報告。前回リスクOFFも参照可。C/D差とリスク別寄与を明示し、寄与の交互作用・順序を記録。原本条件による追加枝が必要なら別記。政策優劣・回復期間の正式採用は判断しない。

## 4. 検証・引渡し
前回A/Bの原票を照合し、発生年・回復完了年・重複・初期オイルOFF・年次完全性・差分・再実行一致を新規検証。既存PASSを新規件数に加えない。Report.md、年次比較CSV、イベント残存係数CSV、主要年表、再実行コード、依存固定参照、Validation、Manifest/Custodyを個別原本で指定新規成果先へ格納。固定Commitから事後取得し実バイトSHA-256・サイズを照合した場合のみCUSTODY PASS。ZIP禁止。短時間で実計算と引渡しを優先し、未達は明記。追加レビュー・Claude再検算は対象外。
main、固定F/SQ/N3、政策本文・Annex、DecisionLog、Acceptance/Freeze/Canonical、RP-023/M19–25 HOLD、RP-024 PENDING、既存承認ゲートを維持。書込みは指定新規成果先のみ。
