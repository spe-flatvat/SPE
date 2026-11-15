# SPE｜F損税 ビジュアルレポート Claude 突き合わせ記録

**Status:** DRAFT / READ-ONLY CROSSCHECK / NON-CANONICAL(Claude 作成、2026-11-15)
**依頼:** Owner(2026-11-15 20:05、レポートのリンク共有。20:08 に本記録の格納を指示)。対象への書込みなし。
**対象:** `spe-flatvat/SPE` ブランチ `work/chatgpt-handoff`(取得時の先端 `0986799393e651caa4a106dbbf0a66fe12a3d870`)の `handoff/f-sonzei-visual-report-20261115/`
- `SPE_F_Sonzei_Visual_Report_DRAFT_20261115.html`:700,557 bytes、SHA-256 `e5bc076bbb9d3df35fe9d5ef654a0b2ac011eb6e52432b0736a00256ce0585a1`、blob SHA-1 `a1000746820483fb1b1621150cdad63bc0856c86`(Commit `f5dd4c78…`)
- `SPE_F_Sonzei_Visual_Report_Notes_DRAFT_20261115.md`:9,268 bytes、blob `18e26b6ba09ffcacc13dfdad5233967b2df3fb64`(読取りのみ。SHA-256 は計算していない)

## 結果

表示データは元 CSV と全件一致。headless Chromium での実表示も、確認した範囲で問題なし。計算の独立検証(`handoff/claude-sonzei-verification-20261115/`、Commit `f9493d7f…`)は変更なし。

## 確認内容

1. **データ一致:** 埋め込み JSON の 66 系列×30 年×25 列 = 49,500 セルを、`SPE_F_StatusQuo_Sonzei_Annual_Diagnostics_DRAFT_20261115.csv`(SHA-256 `e4a0e91e…ed5a`、Commit `5f7899dd…` から取得し直したもの)と照合。**不一致 0**。空欄 22,379 セルは null として保持(Notes の記載と一致)。
2. **設定の一致:** 埋め込みの政策条件・試作設定が入力 JSON(`92d96a59…643d`)と同一。出典 6 件のファイル名・SHA が入力 JSON と同一。66 系列のうち、メタ情報は部分ケース 60 件に全国仮定 6 件を加えた形(部分ケースのスコープはすべて一致)。
3. **実ブラウザ表示(Playwright/Chromium、1200px と 390px):** ページエラー 0。年スライダー・方式切替が動作。2040 年・基準再現の表示は 損税 SQ 1.8128、F 0.0000、損税削減 1.8128、ベース拡大 3.5319、将来 output VAT 公費負担 2.6067、帰属差額 2.6255、公費控除後 0.0188(兆円/年)で、CSV の計算値と整合(帰属差額=ベース拡大−税率部分 0.9064、公費控除後=帰属差額−公費負担)。2028 年は損税削減 0.7581(すべて税率部分)。「住宅控除を留保」方式の 2040 年は、損税 F・損税削減・控除増分・ベース拡大・帰属差額・公費控除後が「未算出」となり、0 に埋めていない(3 部門合計に欠損が含まれるため)。図(SVG)は 9 点を描画。390px 幅でレイアウトの崩れなし。
4. **通信:** CSP は `default-src 'none'; connect-src 'none'`。fetch・XHR・WebSocket・外部スクリプトの参照なし(出典リンクは利用者が開くときのみ)。

## 軽微な点(表示のみ。計算には影響しない)

- 2026 年の「損税削減」「税率低下部分」が「-0.0000」と表示される(元 CSV の -0.000122 円という浮動小数の誤差)。
- 2026 年の損税 F が 1.4718、SQ が 1.4717 と表示される(同値 1.47175 の丸め)。
- Android 実機のタッチ操作は私も未確認。

## 範囲・限界

- 私が確認したのは、データの一致、PC 幅・スマートフォン幅の headless Chromium での表示・操作、エラーの有無。全図の見栄え(色・文字の重なり)の詳細確認、Safari・Firefox・実機は未実施。
- V-01〜V-05(独立検証の指摘)はレポートの注記には反映済み(Notes)。計算原本(`handoff/f-sonzei-calculation-20261115/`)には未反映のまま。
- 全国値は暫定仮定で、政策推計の妥当性は判定対象外。RP-023／M19–25 HOLD、RP-024 PENDING は維持。正式 Acceptance・Finding Close・engine 変更・政策本文変更は行っていない。
