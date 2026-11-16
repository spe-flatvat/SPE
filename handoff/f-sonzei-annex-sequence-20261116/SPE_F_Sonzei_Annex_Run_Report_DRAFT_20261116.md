# SPE｜F損税マクロ接続 Annexシーケンス修正

Status: DRAFT / PROVISIONAL / NON-CANONICAL  
作成日: 2026-11-16（Asia/Tokyo）。標準ライブラリのみ、追加依存なし。

## 新しい実成果

標準税率10→8→5、給付先行、部門別開始、段階導入を入力で変え、2026〜2055年を実計算した。OFF＋16 ONケースの510 PATH行と差分480行、計990行を出力。従来の2027年からの一律置換を撤去し、主ケースは置換なし、感度のみ開始済み部門の実際の控除額に対応するP加重・段階導入比で適用した。CL-06の既存7,251セルPASSは旧実装の算術検証として維持し、今回の政策時期適合の証明へ転用しない。

## 原文

指定2政策原本をGitHub連携で直接取得、ブランチをCommit `14e0e15b903d21e792fac1ba330c95d2fe428905`へ固定した。

- `policies/FreedomPolicies.md` §5: 「2035年頃：消費税5%完全フラット化」。本計算は2035を暫定年度化。
- 同§4: 「暫定食料品0% → 8% → 5%全品目フラット化」。これは食料品措置。標準税率10→8→5とは別で、食料品売上・期間が未指定のため**食料品0%措置の効果は未算定**。標準税率へ0%を流用しない。
- Annex §6A: 「消費税5%への減税」を先行、「課税ベース拡大」を後続フェーズへ。本体の税率/ベース設計を変更せず順序を反映。
- Annex §6Gの2038年完了・累積120兆円等は原文の旧試算記載。今回の計算をその値へ強制一致させず、国債/返済を新規算定したとは扱わない。

8%は原文に年指定なし。2030を例示し可変化。給付開始2027・期間2027〜2029・年間1兆円は**新規の暫定入力**。なし/2兆円を比較。社会保険料還元給付の政策方向は原文§4/§6にあるが金額と具体年は確定していない。原文を改訂していない。

比較基準は既存F `c0347270009a375dddf65b2d3e596845fb6b5157`。旧接続は`14e0e15b903d21e792fac1ba330c95d2fe428905`、CL-06追補は`b2d97202bfd89e88dccef7a07f402152fc1ed647`（今回の読取は後者）。初回`487f40d...`の検証結果は追補に記載された既存PASSとして利用する。

|原本|bytes|SHA-256|
|---|---:|---|
|SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json|259844|`caa34a7e177e462213e15d398a629cf11626637d4209a8d248253c69226415f8`|
|SPE_F_StatusQuo_Annual_Comparison_DRAFT_20261115.csv|127965|`e424d159ce5aa1a586e317c136c89118143203438e972f35d02a17ee544a59ca`|
|SPE_F_Sonzei_V02_Fixed_DRAFT_20261115.py|31779|`5e8f0ede81961301a9dec9274163e231afd4ddd48ed778b89434f6048b83ed95`|
|FreedomPolicies.md|9241|`0dedd2c1126613c30a7d96732d226cc787f6597437137424845d64d041db0204`|
|FreedomPolicies_Annex.md|12319|`ee62de32582a0f6d559029e7e9810b161c6a975ff22b498493d9ca960ca29e83`|
|Claude_Updated.md|11335|`cd14462fb85afda0ad42646a4e8df90179f623d96a837736b49f5be57c1476d1`|

## 変更点

基準ANNEX_BASE: 8%2030、5%2035、教育2036・住宅2037・医療2038。1年導入。SIMULTANEOUSは全2035。DELAYEDは各元開始を3年遅らせ教育2039・住宅2040・医療2041（5%は2035で維持）。入力のphase_yearsで3年等のランプへ変更可。phase=0ならoutput VATもcreditも0。部門開始<5%到達はエラーとして拒否。

```text
tax_rate = 10% (year<year8), 8% (year8<=year<year5), 5% (year>=year5)
phase_s = clip((year−start_s+1)/phase_years_s, 0, 1)
rate_relief_s = inputVAT_SQ_s−inputVAT_F_s
credit_relief_s = phase_s×eligible_input_credit_F_s
private_VAT_s = phase_s×tax_rate×R_s×(1−public_share_s)
ΔC_rate = MPC×theta×rate_relief
ΔI_rate = investment_share×(1−theta)×rate_relief
ΔC_credit = MPC×theta×credit_relief
ΔI_credit = investment_share×(1−theta)×credit_relief
ΔC_burden = −MPC×private_VAT
ΔC_benefit_residual = MPC×benefit×(1−benefit_already_in_legacy_share)
active_weight = Σ(P_s×phase_s×credit_fraction_s) / ΣP_s
CI_fraction = specified_CI_overlap×active_weight
elasticity_fraction = specified_elasticity_overlap×active_weight
GDP_ON = GDP_adjusted_CI + domestic_share×multiplier×(ΔC+ΔI)/deflator_adjusted
```

需要は**水準**として各年へ反映、恒久的成長率への累積加算はしない。標準税率変更による3部門の部分効果を分けるが、**一般消費税減税の全国効果は算定していない**。既存入力に全国課税消費ベースがなく、3部門だけで外挿しない。`general_tax_beyond_three_sectors_trn`は空欄。

基準のlegacy_CI_overlap/elasticity_overlapは0。既存F消費・投資・教育のスケジュールと税収弾性を維持するので、それらに既に含まれる将来政策時期を完全に再構成したモデルではない。今回修正したのは**明示的な損税接続経路**。重複不明を解消したとは称さない。感度は25%/50%だが時期ゲート後にのみP加重で置換する。

直接VATはF旧税収弾性との重複範囲が不明なので、基準では`direct_fiscal_inclusion=0`。別表示の診断値を効果ゼロとみなさない。財政感度1は直接部門VATを税収proxy、公費output VATを歳出proxyへ加算する**非連結診断**で国庫純増ではない。

給付は既存F刺激に全額包含と置く基準（share1）では需要を追加せず、なしとありのGDP差は0。予算への包含は未特定なので、今回の給付額は追加支出として計上し、なし/ありで財政差を表示する。この需要/予算の非対称は明示的仮定である。`benefit_already_in_legacy_share=0`では追加需要が出る代替ケース。実測による根拠ではない。

主ケースのその他係数:

|係数|値|根拠|
|---|---:|---|
|household_pass_through|0.3|Existing theta .3, applied to total relief; provisional incidence split|
|mpc|0.6|.6 illustrative, not empirical estimate|
|investment_share|0.2|.2 of retained relief illustrative; no capital-stock accumulation|
|domestic_share|0.8|.8 illustrative leakage adjustment|
|multiplier|1.0|1 illustrative annual output LEVEL multiplier|
|legacy_CI_overlap|0.0|Base0 per Owner; sensitivity25% applies only to actual phase×credit-weighted sectors|
|elasticity_overlap|0.0|Base0 per Owner; sensitivity is weighted and gated at sector start, not global 2→1|
|elasticity_anchor|1.0|1 only sensitivity endpoint, not identified non-sonzei elasticity|
|benefit_already_in_legacy_share|1.0|Base1 assumes early grant is contained in existing F consumption stimulus; only residual is added. Sensitivity0 is alternative, never summed.|
|direct_fiscal_inclusion|0.0|Base0: sector attribution not added to existing tax/expenditure totals because overlap is unidentified. Sensitivity1 is separate augmented proxy, not national net revenue.|
|rental_credit_fraction|0.0|0 computational endpoint; full1 sensitivity, no legal credit eligibility finding|

住宅控除0/全額は計算端点で、現行/将来制度の法的適格性を認定しない。部分実測施設と全国仮定を合算しない。価格/所得のcash帰着を計算するがCPIは未算定。既存賃金→出生は固定、ここに新たな波及は入れない。

## 年次結果

単位は兆円。値は表示で丸め、CSV原精度を保持する。

|年|OFF GDP|ANNEX GDP|GDP差|OFF税収|ANNEX税収|税収差|
|---|---:|---:|---:|---:|---:|---:|
|2026|580.000000|580.000000|0.000000|80.000000|80.000000|0.000000|
|2028|562.503126|562.503126|0.000000|87.421457|87.421457|0.000000|
|2030|572.031418|572.099339|0.067921|95.033196|95.049825|0.016629|
|2035|580.991169|581.156899|0.165731|103.042286|103.089111|0.046825|
|2036|589.342714|589.422352|0.079638|109.063758|109.086114|0.022356|
|2038|596.987306|596.649957|-0.337348|119.097252|118.982647|-0.114605|
|2040|610.068708|609.734517|-0.334190|131.936149|131.812985|-0.123163|
|2055|682.375325|682.064203|-0.311122|294.385459|294.163182|-0.222277|

### 2055年感度

|ケース|GDP|税収|資金不足proxy|
|---|---:|---:|---:|
|OFF_F|682.375325|294.385459|0.000000|
|ANNEX_BASE|682.064203|294.163182|0.000000|
|SIMULTANEOUS|682.064203|294.160233|0.000000|
|DELAYED|682.064203|294.164710|0.000000|
|TIMING_EARLY|682.064203|294.160757|0.000000|
|TIMING_LATE|682.064203|294.171173|0.000000|
|NO_BENEFIT|682.064203|294.163182|0.000000|
|DOUBLE_BENEFIT|682.064203|294.163182|0.000000|
|BENEFIT_NOT_IN_LEGACY|682.064203|294.164853|0.000000|
|OVERLAP_25|655.661013|253.263566|0.000000|
|OVERLAP_50|630.226358|220.628044|0.000000|
|RENTAL_FULL|682.105773|294.192087|0.000000|
|PHASE_3|682.064203|294.162529|0.000000|
|FISCAL_DIAGNOSTIC|682.064203|294.163182|0.000000|
|LOW_RESPONSE|682.316990|294.343791|0.000000|
|HIGH_RESPONSE|681.606858|293.831569|0.000000|
|ZERO_CHANNEL|682.375325|294.385459|0.000000|

従来値との違い（主ケース。改善は因果的な政策便益を意味しない）:

|年|従来GDP差|新GDP差|変化|
|---|---:|---:|---:|
|2027|-0.783900|0.000000|0.783900|
|2028|-1.818263|0.000000|1.818263|
|2035|-12.745442|0.165731|12.911173|
|2055|-54.084301|-0.311122|53.773179|

## 確認

```text
PASS All 16 ON paths continuous; rates 10→8→5; no 7.5%; gates/phase-weighted replacement verified
PASS OFF exact stored match; actual zero-channel calculation matches existing F
PASS ANNEX_BASE keeps old C/I and elasticity; 2035 matches 5%; no unsupported 25% replacement
PASS Changing activation years changes actual GDP and taxes
PASS CL-06 regression: overlap case equals Annex base before activation
PASS Benefit on/off and sizes affect budgets; legacy-contained vs residual demand are exclusive alternatives
PASS Pre-5% base expansion rejected, not silently moved to another year
PASS Unknown debt/PB/CPI remain blank; source-fixed GDP data not treated as policy validity proof
PASS saved CSV 990 rows; unknown values preserved; differences read back
exit=0
```

コード/JSONでオフライン再実行可能。実行:

```bash
python3 SPE_F_Sonzei_Annex_Sequence_Model_DRAFT_20261116.py SPE_F_Sonzei_Annex_Sequence_Inputs_DRAFT_20261116.json --outdir replay
```

新規コードの差分検証が対象。旧基準の1980行・240行全検査を工程として追加していない。食料品0%、全国減税税収、国債発行、債務残高、PB、CPI、投資の将来資本効果、所得分布、制度別詳細は未算定。原文が要求する最終的な全F動学モデルの完成とは異なる。

成果4原本は`work/chatgpt-handoff`の`handoff/f-sonzei-annex-sequence-20261116/`に新規保全し、固定Commit・SHA・サイズは回答で報告する。既存原本・政策・main・仕様・DecisionLogは未変更。正式Acceptance・Finding Close・Freeze・Canonical化なし。RP-023／M19–25 HOLD、RP-024 PENDING維持。
