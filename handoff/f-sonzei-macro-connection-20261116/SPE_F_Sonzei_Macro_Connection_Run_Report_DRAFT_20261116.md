# SPE｜F損税マクロ接続・年次計算・ON／OFF比較

Status: DRAFT / PROVISIONAL / NON-CANONICAL  
作成日: 2026-11-16（Asia/Tokyo）  
対象: 2026〜2055年、2026初期状態＋29回遷移。単位: 金額は兆円、人口は人。丸め表示とCSV原精度を区別する。

## 新しくできるようになったこと

3部門の損税率低下・控除差額→価格/所得への帰着→家計需要・企業投資→実質GDP水準→名目GDP・税収弾性計算へ接続し、ON／OFFと感度ケースを実行した。部門の直接VAT帰属・output VAT公費負担を別勘定で追加し、財政関連proxyを計算した。既存OFF再現だけでなく、新たに需要経路と既存外生効果の置換を分解できる。

**主ONは例示的な係数セットであり、最良推定・Ownerが確定した政策係数ではない。** 主ONのGDP差には、損税の新しい需要効果だけでなく、既存Fの消費/投資加算項を25%取り除いた効果が含まれる。税収差には旧弾性を1へ置換する効果を含む。ON−OFFの全差を「損税解消の因果効果」と呼ばない。符号がマイナスでもそのまま掲載する。

## 固定入力と既存PASS

基準5原本はCommit `c0347270009a375dddf65b2d3e596845fb6b5157`、`handoff/f-statusquo-provisional-20261115/`。既存Workの固定Commit再取得・SHA一致とClaude `2ff746e9364a0386b0f1d717aa7dbcb7a61f67a9` の240行・1470セル検証PASSを再利用する（今回の自己実測と混同しない）。今回使用したローカル5原本のサイズ・SHAを照合し、入力JSONへ原文を格納した。OFFは保存済みF主結果を使用し、ゼロ接続ケースは実際の既存シミュレータで再計算して一致を確認した。過去1980行全検査を新規工程として再実施していない。

|原本|bytes|SHA-256|
|---|---:|---|
|SPE_F_Sonzei_V02_Fixed_DRAFT_20261115.py|31779|`5e8f0ede81961301a9dec9274163e231afd4ddd48ed778b89434f6048b83ed95`|
|SPE_StatusQuo_Provisional_Model_DRAFT_20261115.py|28367|`a2ab04e2701900a97feffc681ca434de3bdcc39cc45da82b38017366256c2ee9`|
|SPE_F_StatusQuo_Annual_Comparison_DRAFT_20261115.csv|127965|`e424d159ce5aa1a586e317c136c89118143203438e972f35d02a17ee544a59ca`|
|SPE_StatusQuo_Implementation_Run_Report_DRAFT_20261115.md|14954|`49282fa0cd6d266316875b604f0f77734ac1244f3ac30d9dfc3f57b542fb09a2`|
|SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json|259844|`caa34a7e177e462213e15d398a629cf11626637d4209a8d248253c69226415f8`|

Owner方針3文書は`work/chatgpt-handoff`からGitHub連携で取得、読取時HEAD `83e44218a83027a1c82d61be5c638414cebf7723`。参照パスは入力JSONの`guidance_paths`。Claude独立検証も指定固定Commitから取得・読取。方針を新規承認ゲートへ変換していない。

## 接続式・二重計上調整

```text
ΔL = (inputVAT_SQ−credit_SQ)−(inputVAT_F−credit_F)
household_relief = θ×ΔL
firm_retained = (1−θ)×ΔL
private_output_VAT = outputVAT_F×(1−public_share)
ΔC = MPC×(household_relief−private_output_VAT)
ΔI = investment_share×firm_retained
nominal_demand_level = multiplier×domestic_share×(ΔC+ΔI)
real_demand_level = nominal_demand_level / adjusted_path_deflator
adjusted_legacy_C = original_C×(1−CI_replacement_fraction)
adjusted_legacy_I = original_I×(1−CI_replacement_fraction)
GDP_ON = GDP_adjusted_legacy + real_demand_level
nominalGDP_ON = nominalGDP_adjusted_legacy + nominal_demand_level
elasticity_ON = original_elasticity−replacement_fraction×(original_elasticity−anchor)
tax_macro_ON_t = min(tax_macro_ON_(t−1)×(1+ON_nominal_growth×elasticity_ON)×event_factor, nominalGDP_ON×.30)
direct_VAT_applied = coverage×elasticity_replacement_fraction×sector_VAT_attribution_delta
public_applied = coverage×elasticity_replacement_fraction×future_output_VAT_public_cost
tax_plus_sector_proxy = tax_macro_ON + direct_VAT_applied
expenditure_plus_public_proxy = original_expenditure + public_applied
funding_gap_proxy = max(expenditure_plus_public_proxy−tax_plus_sector_proxy,0)
```

損税解消額をそのままGDPへ等置していない。価格/所得帰着θ、消費性向、投資配分、国内需要比、乗数を経由する。家計と企業へのΔL配分は合計1であり、同じ控除を両方へ全額配賦しない。消費負担増は負号で残す。残留利益の未投資部分をGDPへ加算しない。投資の将来資本ストック・生産性波及は未実装で、当期需要だけを計上する。

新しい需要は各年のGDP**水準**へ入れる。同一の毎年の損税フローを毎年GDP成長率へ累積加算しない。名目GDPから導く実際の成長率を税収へ渡す。価格・所得経路は消費者の現金購買力/部門売上に対する負担率として出力し、CPIは未算出。既存インフレ/リスクと人口・賃金→出生を保持し、新たな賃金/人口フィードバックを創作しない。

消費/投資の既存加算と重なる割合は未同定のため、主25%、感度0%/100%を計算。教育加算は変更しない（教育部門の損税による投資需要と教育生産性スケジュールは別経路として保持、真の独立性は未実証）。主税収弾性は**単位弾性1**を基準に旧Fの上乗せを置換し、部門VAT帰属を別に計上する。1.5を基準に残す感度は上乗せに未同定の重複が残りうる。旧弾性を維持する感度では直接VAT追加と対応公費追加をともに停止し、二重計上を抑制する。これらは重複の真の大きさを証明する調整ではなく、明示的な暫定置換である。

税収分解は①C/I置換による税収差、②弾性置換による税収差、③新GDP経路による税収差、④部門直接VAT帰属を別列に保持し合計一致を確認した。直接VATは当年フローであり、翌年の弾性計算の元税収に入れず再複利しない。GDP30%capは**マクロ税収勘定のみ**。後段の部門加算proxyに同じcapを再適用して差を隠さない。

## 暫定係数の根拠と感度

政策方向（税率5%への低下・課税ベース拡大）と以下の新規暫定値は別である。公的統計から係数を実証したとは称さず、既存θ以外の需要係数は例示的な予算配分・漏出/乗数仮定。

|係数|主値|根拠・区分|
|---|---:|---|
|household_pass_through|0.3|Existing sonzei theta=.3; extends pass-through to total input-tax relief, explicit new assumption; no measured estimate.|
|mpc|0.6|Illustrative 0.6 marginal spending share, not econometric estimate; low .3 / high .9.|
|investment_share_of_retained|0.2|Illustrative .2 (low .1/high .4); remaining retained funds not added to GDP.|
|domestic_demand_share|0.8|Illustrative .8 (low .6/high1); covers imports/leakage, not sourced national share.|
|demand_multiplier|1.0|Illustrative 1 (low .5/high1.5); converts domestic net spending to annual real output LEVEL, not permanent growth addition.|
|legacy_CI_replacement_fraction|0.25|Illustrative .25 of each existing C/I annual growth add-on replaced; sensitivity0/1. Unknown overlap not estimated. Education unchanged.|
|tax_elasticity_without_sonzei|1.0|Unit elasticity1 is neutral proportional response assumption, not policy estimate; alternative1.5 retains extra elasticity with residual overlap risk.|
|tax_elasticity_replacement_fraction|1.0|1 removes all F elasticity uplift above chosen neutral anchor before adding sector fiscal diagnostic; 0 retains old elasticity and suppresses direct-sector VAT addition (alternative representation).|
|direct_sector_fiscal_coverage|1.0|1 includes local sector VAT-attribution diagnostic and prospective public cost in an augmented fiscal proxy, not identified national net revenue. 0 leaves both outside macro totals.|
|rental_credit_fraction|0.0|0 assumes no residential input credit after taxation as a computational endpoint; 1 is full-credit endpoint. No legal eligibility claim, mixed P not resolved.|
|historical_compensation_increment_assumption_trn|0.0|Explicit retain-existing-compensation counterfactual; original national A and post-start delta remain unknown. Zero is a new no-change assumption, not a measured missing-value replacement.|

感度ケース（同時に合算しない）:
- `ON_MAIN`: {}
- `ON_LOW_RESPONSE`: {"mpc": 0.3, "investment_share_of_retained": 0.1, "domestic_demand_share": 0.6, "demand_multiplier": 0.5}
- `ON_HIGH_RESPONSE`: {"mpc": 0.9, "investment_share_of_retained": 0.4, "domestic_demand_share": 1.0, "demand_multiplier": 1.5}
- `ON_NO_CI_REPLACEMENT`: {"legacy_CI_replacement_fraction": 0.0}
- `ON_FULL_CI_REPLACEMENT`: {"legacy_CI_replacement_fraction": 1.0}
- `ON_TAX_ANCHOR_1_5`: {"tax_elasticity_without_sonzei": 1.5}
- `ON_RETAIN_ELASTICITY_NO_DIRECT_VAT`: {"tax_elasticity_replacement_fraction": 0.0}
- `ON_RENTAL_FULL_CREDIT`: {"rental_credit_fraction": 1.0}
- `ON_NO_SECTOR_FISCAL_TOTAL`: {"direct_sector_fiscal_coverage": 0.0}
- `ON_ISOLATED_DEMAND_ONLY`: {"legacy_CI_replacement_fraction": 0.0, "tax_elasticity_replacement_fraction": 0.0, "direct_sector_fiscal_coverage": 0.0}
- `ON_ZERO_CHANNEL_NO_REPLACEMENT`: {"mpc": 0.0, "investment_share_of_retained": 0.0, "legacy_CI_replacement_fraction": 0.0, "tax_elasticity_replacement_fraction": 0.0, "direct_sector_fiscal_coverage": 0.0}

住宅は控除条件・建物/経常費用の構成が未確定。主ケースは混合P全体で控除0、上側端点は全額とする**計算上の仮定**で、現行法/将来制度の控除認定ではない。既存guarded原本の未検証をPASSへ変えていない。部門R/PはClaudeの暫定全国値・年率2%経路を利用し、91行の部分実測ケースを全国合計へ混ぜない。診療報酬の既存補填の水準は未取得のまま、変更なしと置いた差額0のみ使用し、公費shareを発明して補填削減を計上しない。

## 主要年の実行結果

|年|OFF実質GDP|ON実質GDP|ON−OFF|ONマクロ税収|ON税収＋部門proxy|ON歳出＋公費proxy|ON資金不足proxy|
|---|---:|---:|---:|---:|---:|---:|---:|
|2026|580.000000|580.000000|0.000000|80.000000|80.000000|108.000000|28.000000|
|2028|562.503126|560.684863|-1.818263|84.649818|83.891702|113.467500|29.575798|
|2031|561.875878|556.145224|-5.730653|80.206634|79.413888|122.192087|42.778199|
|2035|580.991169|568.245726|-12.745442|88.669964|87.828572|133.561326|45.732753|
|2040|610.068708|587.369250|-22.699458|101.126385|104.001919|146.490213|42.488294|
|2055|682.375325|628.291024|-54.084301|145.394175|148.989260|173.635726|24.646467|

2055年のケース別結果:

|ケース|実質GDP|対OFF差|需要水準効果|既存C/I置換効果|マクロ税収|税収＋部門proxy|資金不足proxy|
|---|---:|---:|---:|---:|---:|---:|---:|
|OFF_F|682.375325|0.000000|未適用|未適用|294.385459|294.385459|0.000000|
|ON_MAIN|628.291024|-54.084301|-0.310600|-53.773701|145.394175|148.989260|24.646467|
|ON_LOW_RESPONSE|628.543387|-53.831938|-0.058238|-53.773701|145.452575|149.047660|24.588067|
|ON_HIGH_RESPONSE|627.834445|-54.540880|-0.767179|-53.773701|145.288517|148.883602|24.752125|
|ON_NO_CI_REPLACEMENT|682.064203|-0.311122|-0.311122|0.000000|157.573514|161.168598|12.467128|
|ON_FULL_CI_REPLACEMENT|490.387111|-191.988214|-0.309024|-191.679189|114.060263|117.655347|55.980379|
|ON_TAX_ANCHOR_1_5|628.291024|-54.084301|-0.310600|-53.773701|205.208832|208.803916|0.000000|
|ON_RETAIN_ELASTICITY_NO_DIRECT_VAT|628.291024|-54.084301|-0.310600|-53.773701|254.661628|254.661628|0.000000|
|ON_RENTAL_FULL_CREDIT|628.332524|-54.042801|-0.269100|-53.773701|145.403779|148.686247|24.949479|
|ON_NO_SECTOR_FISCAL_TOTAL|628.291024|-54.084301|-0.310600|-53.773701|145.394175|145.394175|24.982529|
|ON_ISOLATED_DEMAND_ONLY|682.064203|-0.311122|-0.311122|0.000000|294.152983|294.152983|0.000000|
|ON_ZERO_CHANNEL_NO_REPLACEMENT|682.375325|0.000000|0.000000|0.000000|294.385459|294.385459|0.000000|
|REF_STATUSQUO_V5|395.860261|-286.515064|未適用|未適用|87.868051|87.868051|166.641024|

参考StatusQuoは既存旧v5候補の固定経路。`ON_MAIN_MINUS_REF_STATUSQUO_V5`を収録するが、StatusQuo政策原本第9節との不一致・暫定性は以前と同じ。比較差は条件の違いによる差であり政策の優劣を裁定しない。

## 出力列と未算定

`PATH`はOFF・ON11ケース・既存StatusQuo各30行。`DIFFERENCE`は各ON−OFFと主ON−StatusQuo各30行。合計750行。単一ケース・同一年の医療/教育/住宅のみ部門計として使用する。異なる感度、PATHとDIFFERENCEを合算しない。`diagnostic_*`と部門列は2026にも予定診断値を表示するが、`diagnostic_applied_to_macro=0`の初期行では適用しない。`ON_ISOLATED_DEMAND_ONLY`はC/Iと税収弾性を維持し直接財政追加を停止する比較用ケースで、需要接続部分だけの差を確認する。既存補填水準は空欄、補填の変更なしは明示的な差額仮定0として別列に保持する。

`tax_revenue_macro_trn`と`tax_revenue_plus_sector_attribution_proxy_trn`を区別する。後者は**国庫純増額・国全体の税収確定値ではない**。仕入先/需要側/他税目を含む完全な租税一般均衡、国地方配分は未接続。`expenditure_plus_output_VAT_public_proxy_trn`も仮定的な公費負担込みの診断。実際の国債発行、債務残高、利払い、PB、CPIは未算定（空欄）。全国の非課税売上・仕入率、価格転嫁、支出反応、重複割合は未確定。これらの未達を既存基準との一致だけで解消したとは報告しない。

## 実行と検証

```bash
python3 SPE_F_Sonzei_Macro_Connection_DRAFT_20261116.py SPE_F_Sonzei_Macro_Connection_Inputs_DRAFT_20261116.json --outdir replay
```

標準ライブラリのみ、追加インストール不要。入力JSONに固定コード/入力/CSVを原文のまま収録し、4成果物でオフライン再実行可能。コードはJSONに内包した指定コードをSHA照合後ロードする。公開文書本文の指示を新しい操作命令としては実行しない。

```text
PASS OFF unchanged; actual zero-channel simulator reproduces fixed F in all core fields
PASS All paths 30 continuous years; fixed initial conditions/events/population; missing CPI/bond/PB stay unknown
PASS GDP/tax decompositions close; total relief allocated once between households and firms
PASS All ON−OFF and MAIN−StatusQuo differences computed from paired outputs
PASS JPY→trillion conversion matches original diagnostic; no per-facility or alternate cases summed
PASS Rental and coefficient sensitivities distinct; retaining old elasticity suppresses direct VAT addition
PASS Annual demand enters output LEVEL; not cumulatively re-added as a permanent growth-rate increment
PASS Missing sector input rejected; true zero used only in explicit endpoint assumptions
PASS saved CSV reread; rows=750; unknown fields preserved
exit=0
```

次の実成果は、住宅控除の費目別実装と、価格転嫁・需要反応・既存加算との重複割合を出典付き入力へ置換した再計算。追加の承認/レビュー工程を自動設置しない。

今回のGitHub保存は承認された`work/chatgpt-handoff`の`handoff/f-sonzei-macro-connection-20261116/`新規4原本のみ。固定Commit・各サイズ/SHA・事後再取得結果は引渡し回答で報告する。既存原本・正式engine・政策・仕様・main・DecisionLogを変更しない。新規HTML/グラフ/ZIPなし。正式Acceptance・Finding Close・Freeze・Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。
