# SPE｜F損税モデル・ビジュアルレポート説明

Status: DRAFT / NON-CANONICAL / EXISTING RESULTS VISUALIZATION  
作成日: 2026-11-15（Asia/Tokyo、依頼日）

## 成果物と作業範囲

- `SPE_F_Sonzei_Visual_Report_DRAFT_20261115.html`：データ・日本語UI・SVGグラフ・操作JavaScriptを内包した単独HTML。
- `SPE_F_Sonzei_Visual_Report_Notes_DRAFT_20261115.md`：本説明書。

既存結果の抽出・単位換算・許容される同年合計のみを実施した。モデル再実行、係数変更、再推計、追加調査、計算コード修正、正式StatusQuo政策シナリオの新設は行っていない。既存の実装・独立検証PASSは再利用し、今回の表示機能の確認と分離する。

## 固定入力と取得状態

計算原本固定Commit：`5f7899dd4d3e1fdd5f7e8c8202d23795bbc8e914`。Repositoryは `spe-flatvat/SPE`、ディレクトリは `handoff/f-sonzei-calculation-20261115/`。

|原本|bytes|SHA-256|
|---|---:|---|
|`SPE_F_Sonzei_Three_Sector_Prototype_DRAFT_20261115.py`|31,746|`95ea3c5ca87dfebd42eb4551ddf97a2396734b89d47926d4b8c0e21ada5538a4`|
|`SPE_F_Sonzei_Three_Sector_Inputs_DRAFT_20261115.json`|137,774|`92d96a59888c50f97fe8c23a49109c9836856579971156b7e0970042dba8643d`|
|`SPE_F_StatusQuo_Sonzei_Annual_Diagnostics_DRAFT_20261115.csv`|926,134|`e4a0e91e3f24ffec14a831c95b7d44bc116afff7655ff1ba483b9066c2c6ed5a`|
|`SPE_F_Sonzei_Three_Sector_Run_Report_DRAFT_20261115.md`|13,377|`1c3995638500ac9a620fafc2ed5da9bacbcd2dc2978b0f4cfa7de998b471318c`|

前工程で固定Commitから事後取得・照合したローカル原本を再利用し、今回も保存済みバイトのSHAを上表と照合した。再計算による同一性の代替ではない。

Claude検証：固定Commit `f9493d7f076cb71ed3623d8a80e05aeb34454f3b`、`handoff/claude-sonzei-verification-20261115/SPE_F_Sonzei_Claude_Independent_Verification_DRAFT_20261115.md`。GitHub連携Base64原本を取得・読取。16,877 bytes、SHA-256 `7adf71e5131225651b816faa8fa04dd9003e82f945b7856176c5d13a02a88369`。実行再現性・式・入力範囲のPASSはClaudeの独立検証結果であり、今回Workが再実施したとの報告ではない。

画面参考：`work/chatgpt-handoff` の `handoff/f-visual-report-20261110/SPE_F_Visual_Report_DRAFT_20261110.html` をGitHub連携で取得した。208,867 bytes、Git blob `406871a5f009a221da9280146e038a1f2f11e847`、SHA-256 `ef7be4b48cb0a3c14a621f2f042eb07c7a0f84b249b0a1149e6a2defa6d1e739`。この参照だけはOwner指定のブランチ参照であり、損税計算の固定入力として代用していない。色調・年選択・入力/結果表示・元値と制約の構成を参考にした。

## 画面と操作

最初に2040年、Claude基準再現を表示する。年スライダー・年選択・前年/翌年・グラフの点・年次表で2026〜2055年を選択できる。

全国方式は次の**どちらか1方式のみ**。

1. `CLAUDE_BASELINE_*`：旧試作の再現。住宅κ=1は数式再現専用で、建物の将来控除を制度上認めたものではない。
2. `NATIONAL_GUARDED_*`：住宅の未確定条件を留保。2037年以降の住宅控除・残存損税等を空欄として保持する。

医療・教育の両方式は同値なので、方式を混ぜた合計を提供しない。同一方式・同一年の3部門だけを合算する。必要な3値のいずれかが欠損なら合計も「未算出」。既知2部門だけを3部門合計と表示しない。

部分ケースは部門→ケースの単一選択で60件を閲覧できる。施設平均は自動で百万円/施設/年、その他は兆円/年。円または兆円への切替も可能。既存補填の維持/撤回、税込/税抜、CF/PL、費目の束/内訳、用途按分、管理料率は個別ケースとして保持し、同時合算UIを設けていない。

図は7件：部門別損税F/SQ、部門別損税削減、税率/控除分解、部門別ベース拡大、選択年3部門比較、帰属差額/公費/差引診断、減税/課税化タイムライン。加えて部分ケースの損税図・補填図を表示する。タイムラインはスマートフォンで横スクロール可能。数値・縦線・凡例・説明・表は選択年に連動する。

## 元CSVとの対応

|表示|原CSV列|
|---|---|
|損税 SQ／F|`L_SQ` / `L_F`|
|損税削減|`L_reduction`|
|税率低下部分／控除増分|`L_reduction_rate_part` / `L_reduction_credit_part`|
|課税ベース拡大効果|`delta_tax_base`|
|全年度の上流税率差|`delta_tax_rate_all_years`|
|税収帰属差額|`delta_tax_attribution_total`|
|将来output VAT公費負担|`future_output_VAT_public_cost`|
|公費負担控除後の診断|`delta_tax_after_future_public`|
|既存補填・SQ／F|`historical_compensation_A_SQ` / `historical_compensation_A_F`|
|過去5→10%負担・参考|`historical_incremental_tax_B_reference`|
|補填変更／その公費分|`historical_compensation_change` / `historical_compensation_public_cost_change`|

円→兆円は÷10^12、円→百万円は÷10^6。カード・表の小数4桁は表示丸めで、元精度の向上ではない。グラフはSVG座標として数値化するが、データ内には25金額列×1,980行の**原CSV文字列49,500セル**を丸めず保持し、詳細表で表示する。空欄はJSON nullとして保持し、値0と区別した。合算値はブラウザの倍精度演算なので最下位桁の差を含み得る。

グラフの極小浮動小数誤差により不要な負軸余白が生じる場合は表示軸だけを調整する。元値・合算・元値表は改変しない。欠損区間に線を引かず、未算出の棒を0の棒として作らない。

## V-01〜V-05の反映

- V-01：`新delta_tax_after_future_public = 旧dT_base_net_of_public + delta_tax_rate_all_years` を明記。旧診断相当/税率差/新診断を選択年別に表示する。
- V-02：事業者残存列は控除総額ベース。現行credit_SQ=0で増分と同値という射程を記し、原本を変更しない。
- V-03：比較用の重複2方式は単一選択で合算禁止。医療・教育が同値である旨を明記。
- V-04：全国無出典仮定、出典付き部分集合、条件付き按分/料率仮定の区分を表示。将来値はすべて投影で実測ではない。
- V-05：全年度上流税率差を既存Fマクロへ自動加算しない。GDP未接続と重複リスクを説明。

## 今回の確認結果

|確認|結果・範囲|
|---|---|
|固定計算原本の保存済みSHA|4/4一致。既存固定Commit事後照合PASSを再利用|
|元CSV→表示データ|49,500セルの原文字列一致PASS。うち22,379セルの欠損位置を維持|
|全国2方式×30年|60状態で操作ロジックPASS。住宅留保後の欠損合計を保持|
|部分60ケース×3年|2026/2040/2055の180状態でPASS。無効なSVG座標なし|
|操作イベント|スライダー・年選択・前後ボタン・部門/ケース/単位変更ハンドラーの同期をNode VM＋DOMスタブで確認|
|表示データの数値例|2040基準合計の損税削減は1.8128兆円（表示4桁）。約1.81兆円の説明と対応|
|静的グラフの目視|7図＋部分/補填の2図をInkscapeでPNGへ描画し確認。これはブラウザ全画面の確認ではない|
|スマートフォン向け構成|レスポンシブCSSと390px相当のグラフ座標分岐を実装・ロジック確認。Android実機の表示・タッチ動作は未検証|
|外部通信|外部script/CSS/CDN・fetch・XHR・WebSocketなし。CSP `connect-src 'none'`。出典リンクは利用者が開くときだけ外部移動|
|実ブラウザ表示|**未検証**。ローカルChromium起動がsocket権限制約で失敗。Cloud Browserのfile://表示もプロトコルポリシーで拒否。迂回していない|

論理・DOMスタブ検査は終了コード0。独立検証や実ブラウザPASSへ読み替えない。静的描画でクリック用透明矩形の表示互換問題を見つけ、非描画のクリック領域へ修正した。計算結果の修正はない。

## 制約・引渡し

全国R・pは未確定。2040約1.81兆円は全国暫定仮定。税収帰属差額・公費控除後の診断は国庫純増額ではない。既存診療報酬補填の公的負担分、住宅建物の将来控除条件などは未確定。正式StatusQuoマクロ政策シナリオは未作成。マクロGDPへの自動加算なし。

生成・データ対応・操作ロジック・静的グラフ描画は確認済み、**実ブラウザとAndroid実機の見え方は未検証**という限定で引き渡す。追加レビュー・Owner承認ゲートを設けない。

GitHub保存先は `work/chatgpt-handoff` の `handoff/f-sonzei-visual-report-20261115/`、指定2件のみ。確定Commit・保存後再取得サイズ/SHAは引渡し回答で報告する。本Notesを事後追記のために上書きしない。

main・既存計算原本・正式エンジン・政策本文・DecisionLogを変更しない。RP-023／M19–25 HOLD、RP-024 PENDING維持。2成果物の提出後停止。
