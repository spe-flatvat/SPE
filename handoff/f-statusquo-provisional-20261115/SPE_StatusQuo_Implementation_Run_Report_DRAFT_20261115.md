# SPE｜V-02限定修正・StatusQuo暫定実装 実行報告

Status: DRAFT / PROVISIONAL / NON-CANONICAL  
作成日: 2026-11-15（Asia/Tokyo、依頼日）  
実行: Python 3.12.14 / Linux。標準ライブラリのみ。追加インストールなし。

## 結果

V-02は1式だけを変更し、現行1,980行の全CSV実バイト不変を確認。credit_SQ>0の試験では控除増分を使用し、他の列は不変だった。StatusQuoは2026初期状態から29回遷移する主ケースを実行し、2026〜2055年のF比較CSVを作成した。全国推計の妥当性や正式採用の承認ではない。

成果物は指定4件に、再実行用入力JSON1件を追加した。JSONは固定エンジン2原本、F入力・出力・アダプタ、政策原本/v5、旧損税コード・入力等を内包し、外部取得なしで再実行できる。ZIPは使用しない。

## V-02限定差分

```python
None if credit_f is None or credit_sq is None else (1-policy['theta'])*(credit_f-credit_sq)
```

変更前の控除総額基準から増分へ変更。欠損はNoneのまま。原コードに対してこの1式以外の差分がないことを機械確認した。V-01・V-03〜V-05は変更していない。新コードSHA-256：`5e8f0ede81961301a9dec9274163e231afd4ddd48ed778b89434f6048b83ed95`。現行credit_SQ=0のため出力CSVは固定原本SHA `e4a0e91e3f24ffec14a831c95b7d44bc116afff7655ff1ba483b9066c2c6ed5a` と一致する。

## 採用設定と優先関係

StatusQuo本文は既存制度の漸進的調整を継続する方針。主ケース `SQ_V5_CANDIDATE_29` はOwnerが候補指定した旧v5 §4-5を、再現可能な**推定パラメータ候補**として採用する。政策原本第9節を誤記・無効と判断したのではない。旧v5の「流用ミス」記載は旧文書の見解であり、本Workが原本第9節を取り消す裁定をしていない。

|項目|主SQ候補|F主・共通条件／差|
|---|---|---|
|実質基調成長|1.0%〜2034、0.6%2035〜44、0.3%2045〜|Fは1%＋既存F効果。SQの基調項が既存制度継続を含む縮約仮定|
|税収弾性|.85〜2034、.75以降|F 1.5→1.7→2.0の既存設定と分離|
|歳出成長|3%全期間|F 2.5→1.5→1.0%の既存設定と分離|
|消費刺激/教育/F追加投資|主SQでは個別上乗せなし|v5主ケース式による。既存制度の経済作用がゼロという意味ではない|
|純移民|2030〜34に35.7万人/年へ線形ランプ|F同じランプで40万人。35.7万人は旧人口目標からの逆算仮定で現行実績ではない。開始・刻みはFとの共通化仮定|
|死亡・出生|1.015、.975、出生賃金弾性φ=.15|v6実装の同じ関数。φは推定|
|賃金アンカー|400→472万円・幾何補間|F 400→860。いずれも外生アンカー。本文/仕様§1の実質初期380とは不一致を保持|
|ジニアンカー|.380→.415・線形補間|F .380→.348をv5から参考補足。既存Fコードの内生計算値ではなく、共通の表示用補間仮定|
|労働項|人口成長＋共通aging drag、資本α=.35|労働力人口の人数は未算出。移民の年齢構成も未実装|
|インフレ/名目GDP|2%＋イベント、名目成長=実質成長＋インフレ|複利の積ではなく既存v6の加算定義を共通使用|
|財政|弾性式・GDP30%cap・2031税収×.9|同じ式。歳出−税収正部は資金不足proxyだけ|

政策原本第9節の基調1%・弾性1.5〜2・投資+.3〜.5ppは、`SQ_POLICY9_LOW_29`（1.5/.3）と`SQ_POLICY9_HIGH_29`（2.0/.5）の**別感度**で計算した。中間値の創作なし。2つの同時端点ケースであり、統計的信頼区間や全条件の上下限ではない。歳出・賃金・移民等は比較のため主SQ候補と共通の仮定を維持し、本文だけから一意に決まるシナリオとは称さない。本文第9節の名目成長3%は基調1%＋インフレ2%の説明として参照し、イベントや人口項を含む実際の年次名目成長を毎年3%に固定してはいない。

さらに `SQ_V5_MIGRATION400_29` は移民定常値だけを40万人にする比較用反実仮想。主StatusQuo政策として採用せず、Fとの差に含まれる移民仮定の影響を分離する。`F_2026_TRANSITION_30` と `SQ_V5_LEGACY30` は境界差だけの参考で、主29回比較と混ぜない。

## 境界・イベント

主比較の2026は保存済み初期状態。両ケースで実質GDP580・名目600・税収80・歳出108兆円、人口121,500,000・死亡1,590,000・出生640,000を共有。2026オイルショックは予定入力に記録するが、**初期状態へ遷移ショックとして適用しない**。2027に繰り越してもいない。これは固定F主ケースの境界との一致を優先したため。

30回遷移参考だけは初期状態を2025末と表示して2026オイルGDP−3%・追加インフレ2ppを適用する。2027は中台5%＋気候.5%=5.5%、2031は南海3%＋気候.5%=3.5%と税収×.90。2029起点3年災害、2027起点隔年気候は重複年に両方加算する。F/SQのイベント暦・インフレ影響・aging dragの一致を全30年確認した。

## 計算式と比較可能範囲

```text
deaths_t = deaths_(t−1)×1.015
births_t = births_(t−1)×.975×(1+.15×wage_growth_t)
population_t = population_(t−1)+births_t−deaths_t+net_migration_t
labor_growth_t = population_growth_t + aging_drag_t
real_growth_t = base + consumption + investment + education − risk + .65×labor_growth_t
inflation_t = .02 + risk_inflation_t
nominal_growth_t = real_growth_t + inflation_t
tax_t = min(tax_(t−1)×(1+nominal_growth_t×elasticity_t)×event_factor_t, nominalGDP_t×.30)
expenditure_t = expenditure_(t−1)×(1+expenditure_growth_t)
funding_gap_proxy_t = max(expenditure_t−tax_t,0)
```

上記は固定v6関数をそのまま読み込み、暫定アダプタで政策別係数・歳出・capを適用。正式エンジンを書き換えていない。Fの60行（主＋参考）の10指標を固定F出力と照合した。

GDP・税収・歳出・人口/出生/死亡・労働成長率は同一定義で比較可能。賃金/ジニは外生アンカーの比較であり、内生的政策帰着ではない。労働力人口人数、実際の国債発行額、PB、所得中央値等は未算出。CSVの実際の国債発行/PB/労働力人口列は空欄とし、資金不足proxyで穴埋めしていない。初期国債28兆円は初期参照値だけで、将来国債系列へ接続しない。

## 主要年結果

GDP・財政は兆円、人口は万人、賃金は万円。丸め表示でありCSVの精度とは分ける。

|年|ケース|実質GDP|名目GDP|税収|歳出|資金不足proxy|人口・万人|賃金アンカー|ジニアンカー|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
|2026|F主|580.000000|600.000000|80.000000|108.000000|28.000000|12,150.0000|400.0000|0.380000|
|2026|SQ v5候補|580.000000|600.000000|80.000000|108.000000|28.000000|12,150.0000|400.0000|0.380000|
|2028|F主|562.503126|636.839830|87.421457|113.467500|26.046043|11,948.7887|421.6837|0.377793|
|2028|SQ v5候補|552.895840|626.366257|82.983413|114.577200|31.593787|11,948.2073|404.5921|0.382414|
|2031|F主|561.875878|675.084625|85.818095|122.192087|36.373992|11,642.8170|456.4329|0.374483|
|2031|SQ v5候補|531.941783|640.005052|76.068793|125.201600|49.132807|11,637.4589|411.5792|0.386034|
|2035|F主|580.991169|755.100616|103.042286|133.561326|30.519040|11,285.8255|507.2599|0.370069|
|2035|SQ v5候補|515.338730|671.559857|79.246718|140.915504|61.668785|11,260.7778|421.0835|0.390862|
|2040|F主|610.068708|874.583553|131.936149|143.883480|11.947331|10,782.9945|578.8253|0.364552|
|2040|SQ v5候補|491.157536|707.334935|82.396976|163.359690|80.962714|10,727.2975|433.2730|0.396897|
|2055|F主|682.375325|1,313.711587|294.385459|170.376704|0.000000|8,670.0144|860.0000|0.348000|
|2055|SQ v5候補|395.860261|770.549614|87.868051|254.509075|166.641024|8,510.2378|472.0000|0.415000|

## 2055年・感度と旧v5参考

|ケース|実質GDP・兆円|税収・兆円|資金不足proxy・兆円|人口・万人|
|---|---:|---:|---:|---:|
|F_2026_INITIAL_29|682.375325|294.385459|0.000000|8,670.0144|
|SQ_V5_CANDIDATE_29|395.860261|87.868051|166.641024|8,510.2378|
|SQ_POLICY9_LOW_29|486.384252|141.361947|113.147128|8,510.2378|
|SQ_POLICY9_HIGH_29|515.582288|197.216941|57.292134|8,510.2378|
|SQ_V5_MIGRATION400_29|398.971935|88.382485|166.126590|8,613.4378|
|F_2026_TRANSITION_30|661.523406|297.381326|0.000000|8,449.6430|
|SQ_V5_LEGACY30|381.253888|88.164538|173.979809|8,291.2808|

旧v5参考はGDP381.4兆円・人口8,298万人・『国債発行』174兆円。今回の主SQはそれぞれGDP差 `+14.460261`兆円、人口差 `+212.2378`万人。資金不足proxyと旧ラベル値の数値差は `-7.358976`兆円だが、実際の国債発行の差とは解釈しない。

境界を30回に戻した参考SQはGDP `381.253888`兆円・人口 `8291.2808`万人・proxy `173.979809`兆円。29/30の差はこの参考ケースで分離できる。残る旧v5との差は移民ランプの詳細、賃金補間・年度境界、v6実装への接続等が候補だが、旧試算の実行コード/全入力は今回の指定原本に無く、寄与を一意に分解できない。本文の結果値へ合わせる係数調整はしていない。

## 損税診断との距離

`sonzei_L_SQ_reference_trn` は固定した3部門R/P仮定のL_SQ合計を再利用し、すべてのマクロケースで同じ値を保持する。マクロGDPで売上を自動スケールしない。Fの旧再現L_Fと住宅条件留保後L_Fは別列。留保後は2037年以降の欠損合計を空欄とする。損税削減・税収帰属・公費負担を、マクロGDP・税収・実際の国債へ加算していない。マクロの税収弾性仮定と損税効果を二重計上しない。

## 実行・確認ログ

```bash
python3 SPE_StatusQuo_Provisional_Model_DRAFT_20261115.py SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json --outdir replay
# V02だけを旧CLIで試す場合（入力JSONは同じ）:
python3 SPE_F_Sonzei_V02_Fixed_DRAFT_20261115.py SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json --outdir v02-replay
```

V02単独CLIは元の出力名を使用するため、必ず独立出力ディレクトリを指定する。GitHub追加原本は今回の5件だけ。

```text
PASS V02 only one expression differs; current 1980-row CSV byte identical SHA256=e4a0e91e3f24ffec14a831c95b7d44bc116afff7655ff1ba483b9066c2c6ed5a
PASS credit_SQ>0 test: old=393823100996.125854 JPY, new=196911550498.062927 JPY; all other fields unchanged
PASS V02 missing credit remains unknown; loss/tax/public/GDP definitions unchanged
PASS F primary+legacy: 60 rows x 10 stored metrics reproduce fixed 30530ad2 results
PASS 7 paths x 30 continuous years; 29/30 transitions; nonnegative finite stocks; tax cap; missing indicators preserved
PASS common calendar: 2026 scheduled oil not transitioned in primary; 2027 conflict+climate 5.5%; 2031 quake+climate 3.5% and tax x.90
PASS SQ v5 parameter breaks, wage/Gini anchors; no F-specific add-ons; policy9 endpoints are separate sensitivities
PASS fixed L_SQ diagnostic reused unchanged across macro paths; no GDP/tax/debt automatic addition
PASS matched F−SQ difference rows share initial GDP/population and year definitions
PASS saved CSV reread: 240 rows; missing bond/PB indicators remain blank
exit=0
```

CSVは7経路×30年＋F主−SQ主の30差分行、計240行。`record_type=DIFFERENCE` は経路として合算しない。DIFFERENCEの実質GDP等はF−SQ、賃金/ジニ差もアンカー差であり、未知の指標は差分でも空欄。PATHの`*_scheduled`は当年の予定係数で、2026初期行で適用済みとはしない。列名`_trn`は兆円、`_persons`は人、`_pct`/`_pp`は%、ポイント。

保存CSVを再読取し、年次・欠損・単位を確認する。再実行のバイト一致は引渡し回答で報告する。後続Claude検証や比較HTMLは今回実施しない。実装PASSと政策推計妥当性を分離する。

再開時には前回DRAFTを別名退避した。前回コードの2031年リスク検査に浮動小数点の完全一致比較が残っていたため、既存の許容誤差付きclose検査へ変更した。3.5%という予定値・計算式・CSVの数値はこの修正で変えていない。最終実行は上記すべてPASS。これは利用制限そのものの原因を特定したという報告ではない。

## 出典原本・同一性

StatusQuo/v5のOwner指定ブランチ参照は作業開始時HEAD `0986799393e651caa4a106dbbf0a66fe12a3d870` に固定した。GitHubから取得した本文・blob・SHAを記録。旧損税入力・原本と検証は既存保存原本のSHA一致を再利用。JSONは原文を含み、原本を編集していない。

|入力原本|固定Commit|bytes|SHA-256|
|---|---|---:|---|
|`StatusQuo.md`|`0986799393e651caa4a106dbbf0a66fe12a3d870`|8686|`eb5a95df122292465fc79c68a12b9e7c6f8c0e0f97f367eb28ed0b27f6264e30`|
|`SimulationSpecification_v5.md`|`0986799393e651caa4a106dbbf0a66fe12a3d870`|17708|`fd10290c97daa3a77bd1348ac4c2a1536da634a7b9408737dcd7713adc671b65`|
|`SPE_F_Provisional_Run_20261110.py`|`30530ad2b012ce33715db662fa0c5ca06a2f10ed`|5311|`b48c461662e6c365ad9e8943fd9c554e129b8348df836ec96f105bb06faa96e8`|
|`SPE_F_Provisional_Inputs_DRAFT_20261110.json`|`30530ad2b012ce33715db662fa0c5ca06a2f10ed`|5102|`eac26d99bbfb71b41087021b2166d7bdac9879962decb258fbe43c4eaa1da810`|
|`SPE_F_Annual_Results_DRAFT_20261110.csv`|`30530ad2b012ce33715db662fa0c5ca06a2f10ed`|14355|`199b18f662abb07aaa73097b0d0d923c0b84a9507b2e7a3165cbe413b350dd68`|
|`prototype.py`|`4389951293b5ff91bbfec58a613b30458e1fb544`|7826|`3c1f7485fa96e649f06a96f0f844a9b270ffe43b5e0b6f696b75bb904612cff6`|
|`m14_wage_anchor.py`|`4389951293b5ff91bbfec58a613b30458e1fb544`|1650|`363c330a74a9834e68c18c225da37209def3724d8834745179e1f129b2317c26`|
|`sonzei_original.py`|`5f7899dd4d3e1fdd5f7e8c8202d23795bbc8e914`|31746|`95ea3c5ca87dfebd42eb4551ddf97a2396734b89d47926d4b8c0e21ada5538a4`|
|`sonzei_original.csv`|`5f7899dd4d3e1fdd5f7e8c8202d23795bbc8e914`|926134|`e4a0e91e3f24ffec14a831c95b7d44bc116afff7655ff1ba483b9066c2c6ed5a`|
|`Claude_verification.md`|`f9493d7f076cb71ed3623d8a80e05aeb34454f3b`|16877|`7adf71e5131225651b816faa8fa04dd9003e82f945b7856176c5d13a02a88369`|

GitHub保存対象は `work/chatgpt-handoff` の `handoff/f-statusquo-provisional-20261115/` に指定4件＋入力JSON1件のみ。既存原本・main・正式エンジン・政策本文・旧v5・ビジュアル・DecisionLogは未変更。正式Acceptance、Finding Close、Freeze、Canonical化、新規RP・追加レビューなし。RP-023／M19–25 HOLD、RP-024 PENDING維持。引渡し後停止。
