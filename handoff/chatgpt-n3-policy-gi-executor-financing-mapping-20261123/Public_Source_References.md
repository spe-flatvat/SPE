# 出典・原本・既存根拠の再利用

確認日：2026-11-23。固定政策・実装・前回26原本はInput_Source_Receipts.json。補完原本はPublic_Source_Receipts.json。前回の15手段・30G/I対応と21資料の確認記録を固定Commit c087a1a5af12b86cdb140d934754d75e5ee9c4efから再利用し、広域制度の再調査はしない。

| 根拠 | 版・箇所 | 確認できたこと | 確認しないこと |
|---|---|---|---|
| [内閣府ESR47](https://www.esri.cao.go.jp/jp/esri/esr/data/esr_047.pdf) | 2025年冬号、印刷p23-24、5/6節 | 雇用者報酬・中間投入等による政府サービス計測、現物社会移転、固定資本形成と維持修理・土地取引の区分 | 本モデルの既存費用を無調整で新Gに全額加えること、国地方帰属 |
| [地方公務員法](https://laws.e-gov.go.jp/law/325AC0000000261) | 取得現行XML、本則24/25条 | 給与条件は条例、条例に基づく支給 | N3の追加人数・自治体別給与予算 |
| [都市再生特別措置法](https://laws.e-gov.go.jp/law/414AC0000000022) | 取得現行XML、本則81条 | 市町村の単独・共同の立地適正化計画 | 全事業を市町村が所有・支払うこと、N3具体都市・額 |
| [国交省コンパクトシティ公式ポータル](https://www.mlit.go.jp/en/toshi/city_plan/compactcity_network.html) | 取得日現在、制度・手引きリンク・役割説明 | 市町村・都道府県・国・民間の連携、計画と支援の区別 | 全額補助や2030年度枠 |
| [国交省旧Q&A URL](https://www.mlit.go.jp/toshi/city_plan/content/001738454.pdf) | Web読取Q1/Q4、実行環境回収404 | Web読取で市町村計画等の説明を確認。現行法・公式ポータルで補完 | 実バイト取得・SHA一致は未実施、現行最新版の確定 |
| N3本文・共通Annex・F別紙 | 原文固定c087a1a、原文4.A〜D/5〜7。N3専用Annex未特定を継承 | 政策意図・期間・主題、F別紙との分離 | 原文外の事業、人数、費用、国地方分担 |
| N3_Components.py・Gap_Components.py・Components.py | 固定c087a1a、employment/relief/pension/institutions等 | 給与・給付・企業I・基金・構造出力の接続 | モデル仮定を政策承認や実際予算へ読み替えること |
| 前回Legal_Authority_MapとPublic_Source_References.md | 固定c087a1a、15手段・30対応 | 国地方・用途・権限・制度制約 | 2030N3確定資金額・負担割合 |
