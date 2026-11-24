# SPE｜共通マクロGDP低迷要因の定量分解・限定反実仮想
Status: OWNER AUTHORIZATION BY WORK MESSAGE / LIMITED EXECUTION / DRAFT / NON-CANONICAL
Repository: spe-flatvat/SPE
Branch: work/chatgpt-handoff
期間: 2026–2055
成果先: handoff/chatgpt-common-macro-gdp-attribution-20261124/

## 目的
短時間の一括実行で、SQを含む3系列が2027–2055年に初期実質GDP580兆円を下回る理由を定量化する。既存成果を再利用し、共通マクロ要因と政策実装固有差を区別する。政策改訂・本格モデル改修・全国較正は行わない。

## 固定参照
- Work共通指標最終版 8a8edb403b960cceb535f9b70461646e9374c229 / handoff/chatgpt-f-sq-n3-common-indicators-20261123/ （Report.md, Dependencies.json, Annual_Comparison.csv, Run.py 等）
- Claude独立検算 da79ab621de27a1a2df8dd3edf050e4f02fac63a / handoff/claude-f-sq-n3-common-indicators-verification-20261123/ （4,818件不一致0、PASS_WITH_LIMITATIONS）
- 比較レポート 80426e79ee17b42b49ea5eae183478eb4b3c501a / handoff/claude-f-sq-n3-common-report-20261123/
- 上流原票はDependencies.jsonの固定commit/pathから自己回収。既存SQ限定診断・N3 GDP差帰属の結果を再利用し、同一条件のPASSを再取得のためだけに再実行しない。
- SQ=CURRENT_REFERENCE_UNCHANGED_COMMON_ON、F=共通医療参照接続後、N3=BASE_REPLAY追加G/I OFF。固定系列を変更しない。

## 1. SQの年次原因分解
2026初期実質580兆円、名目600兆円、人口122,618,024人。実装の基調成長1%、労働弾性0.65、基調インフレ2%、供給余力、イベント適用と回復なしの条件を原票・コードで確認。2026初期オイルOFFを維持。
実質コアの基調成長、人口から有効労働への経路、労働投入、各リスクの累積損失、需要・供給制約、その他残差を2026–2055年次で分解する。人口と労働を二重計上しない。乗法交互作用は明示し、対数分解または順序明示の逐次差分で総GDP差に閉じる。コアGDPと最終GDPを区別。2030/2035/2045/2055の寄与を兆円・必要に応じ百分率で提示。

## 2. 限定反実仮想
SQについて現行、全実質リスクOFF、労働投入2026固定、基調成長OFF、リスク回復ありを比較する。必要なら災害・気候のみOFFを追加。回復ありは各イベントの実質損失を翌年以降5年で線形に解消する非採用診断（重複イベントは個別損失係数を乗算、発生年損失は保持）。既存コードに適合しない場合は同等の明示的診断式を隔離実装し、完全モデル再実行と区別する。物価ショックは実質リスクOFFと混同しない。各ケースで変更した入力だけを明示し、年次実質GDP・コア・需要供給制約・一人当たりGDPを可能な範囲で実計算。回復仮定は政策採用ではない。

## 3. F・SQ・N3共通波及
現行3系列について共通コア寄与と政策固有の労働・需要・供給等の差を年次で切り分ける。F/SQ/N3に同じリスクOFF・回復診断を適用可能なら再計算し、2055差の変化を示す。政策側の内生フィードバックを固定した診断なら明記し、完全再実行と混同しない。F desiredの最大0.62兆円残差、価格圧力休眠、N3のSQ労働継承は既存限界として保持。未検証内部を推測で埋めない。価格圧力の強制発火試験や需要側全面再実装は今回対象外。

## 成果と検証
個別原本としてReport.md、年次寄与CSV、反実仮想年次CSV、主要年比較、再実行コード、入力/依存固定参照、Validation、Manifest/Custodyを新規成果先へ格納。現行系列一致、年次完全性、寄与合計と残差、イベント発生・回復・重複、単位、再実行一致を検証。既存比較値2055 F540.275/SQ528.962/N3 483.991兆円は丸め表示であり原票精度を使用する。新規成果の固定commit事後取得・実バイトSHA-256/サイズ照合を実施。CUSTODY PASSは実照合時のみ。ZIP禁止。
時間・利用枠制約時はSQ原因分解と限定診断を優先して引渡し、3系列の未実施範囲を明記。新規承認・追加レビューは不要。Claude再検算は今回対象外。
main、固定F/SQ/N3、政策本文・Annex、DecisionLog、Acceptance/Freeze/Canonicalを変更しない。RP-023/M19–25 HOLD、RP-024 PENDING維持。書込みは指定新規handoff成果先のみ。
完了報告では新たに判明した定量寄与、回復仮定による差、政策固有差、未確認、検証件数、固定commit、成果リンク、保全状態を示す。計画のみでは未完了。
