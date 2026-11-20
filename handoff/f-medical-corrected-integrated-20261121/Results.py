#!/usr/bin/env python3
"""Deterministic comparison tables; sensitivities are not calibrated forecasts."""
import csv,json
from pathlib import Path
P=Path(__file__).resolve().parent
from Model import dump
def read(n):return list(csv.DictReader((P/n).open()))
def run():
 a=read('Annual.csv');by={(r['case'],int(r['year'])):r for r in a};co={(r['case'],int(r['year'])):r for r in read('Common_EndOfLife.csv')};hh={(r['case'],int(r['year'])):r for r in read('Household.csv')}
 c=json.loads((P/'Inputs.json').read_text());demand=[];decomp=[];diagnostic=[]
 for y in [2035,2040,2055]:
  for name in ['LATEST_F','POP_PROPORTIONAL']:
   r=by[name,y];z=co[name,y];h=hh[name,y]
   demand.append(dict(year=y,case=name,episode_count=r['terminal_episodes'],clinical_medical_bill_trn=r['baseline_medical_bill_trn'],common_supported_choices=z['chosen_transitions'],universal_palliative_need=z['universal_palliative_need'],universal_palliative_served=z['universal_palliative_served'],capacity_unmet=z['universal_palliative_unmet'],common_household_direct_burden_trn=h['household_direct_cash_burden_delta_trn'],public_clinical_delta_trn=r['public_clinical_payment_delta_trn'],insurer_clinical_delta_trn=r['insurer_clinical_payment_delta_trn'],status='UNCALIBRATED_AGE_RATE_COMPARISON'))
 # Corrected sequential counterfactual uses actual independently solved paths.
 chain=['F_ONLY','F_ONLY_NO_COPAY','F_ONLY_NO_COPAY_NO_PREVENT_SAVING','ZERO_COMMON_CLINICAL_SAVING']
 old=[.1891,.0734,.0218]
 for i,(left,right) in enumerate(zip(chain,chain[1:])):
  decomp.append(dict(step=i+1,from_case=left,to_case=right,year=2055,corrected_GDP_difference_trn=float(by[right,2055]['real_gdp_trn'])-float(by[left,2055]['real_gdp_trn']),Claude_original_approx_difference_trn=old[i],original_source='c8405cd2 report4-2',interpretation=['Remove_copay:HH_cash_volume_harm','Remove_prevention_saving:more_medical_production_and_financing','Add_common:universal_care_registry_proxy_and_neutral_transition'][i]))
 # Predeclared diagnostics expose, rather than conceal, abrupt level changes.
 for y in range(2027,2056):
  r=by['LATEST_F',y];prev=by['LATEST_F',y-1]
  delta=float(r['real_gdp_trn'])-float(prev['real_gdp_trn']);oldchange=float(by['OLD_MEDICAL_F',y]['real_gdp_trn'])-float(by['OLD_MEDICAL_F',y-1]['real_gdp_trn'])
  event=[]
  if y==2028:event.append('F medical+education start;uniform copay ramp begins')
  if y in [2030,2035]:event.append('inherited VAT/other timing;check original schedule in fixed inputs')
  if y==2031:event.append('registry/reference/proxy rollout starts')
  if y==2032:event.append('clinical implementation starts')
  if y==2033:event.append('F transition/palliative subsidy endpoint;health lag begins')
  if y==2035:event.append('nationwide operation and end of F8-year ramp')
  if y==2040:event.append('registry and supply target phase reached')
  diagnostic.append(dict(year=y,real_GDP_change_trn=delta,old_medical_GDP_change_trn=oldchange,change_in_new_minus_old_trn=delta-oldchange,supply_binding=r.get('supply_binding'),clinical_cost_delta_trn=r['clinical_cost_delta_trn'],household_cash_delta_trn=r['household_cash_delta_trn'],event=';'.join(event),flag_new_correction_jump=abs(delta-oldchange)>.1))
 dump(P/'Demand_Comparison.csv',demand);dump(P/'GDP_Decomposition.csv',decomp);dump(P/'Diagnostics.csv',diagnostic)
 def fmt(n):return f'{float(n):.6f}'
 text='''# SPE 医療限定修正・最新F実装済み施策の統合計算

DRAFT / NON-CANONICAL。2026-11-21 JST。Owner依頼固定Commit fa66e4b73dd135ede5322d489f2a875c4eb3d989に基づく。旧原本・policies/Inbox/main・正式承認・HOLDは変更しない。

## 実行と変更

'''+f"{len(c['cases'])}条件を2026〜2055年の30年連鎖で再実行し、固定SQ・旧教育F・旧医療Fの3参照を合わせ{len(a)}行。旧医療を全除去し、最新教育コーホート、VAT、外国人、高齢者、年金、家計A/B/C、投資・企業の既存実装へ接続した。全政策原文の完全な因果実装を意味しない。実装/暫定代理/未較正/未実装はPolicy_Map.csvに明記。\n\n"+'''
- M-1：既存人口軌道の年齢3区分＋既存高齢者年齢性別stockから5区分人口を構成。日本人/外国人の合計を実行条件のstockに合わせる。年齢別episode率を分離し、2026候補45万件へ規格化。高齢者細分は元stock比率を当該年の高齢者合計へ再尺度化する。日本人内訳はIPSS広域年齢比率を日本人stockへ再尺度化し、外国人は差。医療費は2024年齢別費用を各年齢人口比で伸縮。総人口比例比較も維持。
- M-2：医療サービスの輸入、中間投入、既存生産置換、VA尺度を入力化。医療追加投資も同様の国内VA近似。財源は税/保険料/政策別債/他支出を区分し、未充当を残す。VA尺度0/50/100%×財源対応0/50/100%と財源別4条件を並走。LATEST_Fは中間感度ラベルで、採用された政策・確定中央予測ではない。
- M-3：共通episodeの療養先別請求を年齢・合成所得・月額・上限・F一律3割へ接続。共通緩和ケアも既存請求への追加限界自己負担として計算し、上限を別請求でリセットしない。旧11.762%平均率はLEGACY_PAYER。上限引下げ/引上げは別候補。
- M-4：家族所得減、保証費回避、在宅保険外、公認代理カバー、家族時間を感度出力。主出力に符号・単位・幅を保存。公費節減を家計へ振替えない。
- M-5：登録率0/30/60%、全撤回、意思不明で患者ルール・給付・全員緩和供給の出力を比較。全員緩和は登録に依存せず、登録移行に伴う経路費用と分離。独立した2つの需要/能力/配賦条件で共通関数を実呼出。F以外の新規モデルは作らない。

Claude固定c8405cd2の報告・2検算コード・実出力を実バイト回収し再利用。work/claude-handoff先頭も同Commitで、claude/配下は存在せず既知handoff原本を採用。46170セル不一致0・14出力一致・教育回帰480はClaude既存証拠であり、今回の新コード独立検算PASSとは呼ばない。今回の変更影響は医療OFF対旧医療除外240セル、各会計、保護入力、年次GDP/資本恒等式、全生成出力再実行で確認する。

## 年齢需要の差

年齢別利用率は観測値ではなく未較正候補。死亡数を節減式へ入力しない。IPSS2023の年次広域人口は既存モデルから再利用し、元出典URL/年次はInputs.population_sources。sub-65就学前年齢40%や終末期率、2026の45万規格化も候補である。新たな将来疾病別コーホート推計を得たという主張はしない。

|年|年齢方式episode|旧人口比例episode|年齢方式・全員緩和必要件数|供給可能件数|
|---|---:|---:|---:|---:|
'''
 for y in [2035,2040,2055]:
  r=by['LATEST_F',y];z=co['LATEST_F',y];text+=f"|{y}|{float(r['terminal_episodes']):,.0f}|{float(by['POP_PROPORTIONAL',y]['terminal_episodes']):,.0f}|{float(z['universal_palliative_need']):,.0f}|{float(z['universal_palliative_served']):,.0f}|\n"
 text+='''
## F主要指標

兆円。部分収支は全国PBではない。所得・賃金・雇用は既存マクロ代理。SQは共通OFF固定参照なので、共通政策込みのセット間優位性には使わない。

|条件|2055実質GDP|名目GDP|家計現金DI代理|税収診断|部分公的収支|
|---|---:|---:|---:|---:|---:|
'''
 for name in ['SQ_FIXED','OLD_EDUCATION_F','OLD_MEDICAL_F','LATEST_F','POP_PROPORTIONAL','LEGACY_PAYER','LOW','HIGH','VA0_FIN0','VA100_FIN100','FINANCE_TAX','FINANCE_DEBT','FINANCE_CROWD']:
  r=by[name,2055];text+='|'+name+'|'+'|'.join((fmt(r[k]) if r.get(k) not in [None,''] else '—') for k in ['real_gdp_trn','nominal_gdp_trn','macro_cash_DI_proxy_trn','tax_diagnostic_trn','consolidated_partial_balance_proxy_trn'])+'|\n'
 text+='''
名目/実質GDP・消費・投資・資本・人口・労働・賃金・税・教育/年金/医療/保険者/部分公費をAnnual/各勘定に出力。政策金利、全国国債・PB、中央値、実測ジニ、エンゲル、出生死亡の政策効果は空欄。教育債と医療追加財源債の残高/発行/償還/資産積立は部分政策勘定に限定する。株式配当・内部留保・企業統治の独立因果効果も既存代理の範囲を超えて推計しない。

医療GDPは粗支出を直接加算しない。既定候補ではサービス差×(1−輸入10%)×(1−中間40%)×VA尺度50%×(1−既存置換20%)、他支出圧迫×候補VA60%を控除。支出の21.6%相当を需要側VA近似として接続し、既存消費平滑化・供給上限・資本恒等式を維持する。国内VAの厳密なSNA産業連関モデルではない。財源対応50%の候補mixは税/保険料/債/他支出各25%。負の必要財源は税保険料軽減・他支出拡大・債償還/資産化で対称処理し、節減の符号を強制反転しない。

## GDP符号の説明

旧版ZERO_CLINICAL_SAVING−F_COMBINEDの2055差+0.284241兆円はClaude原本の算術PASSを維持。約0.1891はcopay除外、0.0734は予防節減除外、0.0218は費用中立共通追加。修正後の対応する逐次反事実は次表（追加の全員緩和を含み、旧版と制度内容が同一という意味ではない）。

|修正後ステップ|2055GDP差・兆円|
|---|---:|
'''
 for r in decomp:text+=f"|{r['interpretation']}|{float(r['corrected_GDP_difference_trn']):.6f}|\n"
 text+='''
医療費増による測定生産増と、家計可処分所得・財源負担の反対効果は別経路であり、GDP符号を政策効果の良否へ置き換えない。健康労働は既存未較正係数を継承し、費用節減が健康悪化/改善を自動意味しない。全員緩和の便益QALYは未推計。

## 家計は感度幅で読む

共通の直接現金負担、億円/年、正は増、負は軽減。保険料・財源税は別列であり本表へ混入しない。

|条件|2035|2040|2055|
|---|---:|---:|---:|
'''
 for name in ['LATEST_F','LEGACY_PAYER','HH_NO_INCOME_LOSS','HH_NO_GUARANTEE_AVOIDED','HH_HOME_COST_HIGH','HH_PROXY_LOW','HH_FAMILY_HOURS_HIGH','HH_GUARANTEE_HIGH','HH_HH_COMBINED_STRESS']:
  text+='|'+name+'|'+'|'.join(f"{float(hh[name,y]['household_direct_cash_burden_delta_trn'])*1e4:.2f}" for y in [2035,2040,2055])+'|\n'
 text+='''
旧+0.32億円が所得減0%で−9.8億/保証回避0で+31.8億となるClaude結果は旧11.76%モデルの前提依存性を示す証拠として維持する。修正後は年齢需要・Fの上限付き限界患者負担・全員緩和を反映するため同じ値へ合わせない。保証費回避10万円条件等の符号反転は候補の比較であり便益確定ではない。貯蓄/借入は差額の80/20配分代理で、資産残高・個人の借入確率ではない。家族の休業/離職の人数は推計せず、時間価値×所得減率のみ。

## 重複・会計・残る限界

Policy_Effectsは12施策のfull-minus-off限界差で、寄与を足せば合計になる一意分解ではない。Interactionsは共通×F医療、教育×医療、VAT×医療の差分差を同一エンジンで計算する。旧教育・旧医療重複は除去。新医療サービス量を既存VAT部門のR2025へ逆算して数量応答させ、既存VAT関数で課税/控除/価格/所得/投資を再計算する。課税差は既存税経路に一度だけ入り、新規に税収へ再加算しない。医療の追加量は臨床・予防・運営を対象、登録/代理管理や資本設備のVAT衛星は未構築。診療報酬とVAT税抜価格の厳密制度対応は候補。VAT反応は「損税解消をもう一度計上する」操作ではない。

付随受取は保険外/介護受取、代理利用料、保証費受取減、家族逸失所得の反対側へ分解し、補助・利息・他支出相殺を別記。これは全国産業別SAM閉鎖ではなく、逸失所得の雇用主側・介護保険給付全額は未構築。単一の残余合わせ項を検証根拠に使わない。金融資産の利回りや全国国債需給/金利は未モデル化。

年次診断Diagnostics.csvは補正前後の前年比差・供給拘束・医療費・家計を保存し、新旧差の年次変化0.1兆円超を検出する。原モデルの2028教育医療開始、VAT/食料税日程、2031登録、2032施行、2033移行補助期限/健康ラグ、2035全国運用、2040普及到達というイベントを併記する。GDP水準の長期低下は共通人口/労働のcore経路を継承したもので、医療効果と混同しない。供給上限や線形資金応答による局所的な単調性はモデル構造であり、実証的な一般法則でない。

## N3へ進む前の残課題

共通呼出インターフェースは利用可能だが、N3の政策原文対応、税・家計・保険制度、財源/VAの同一感度契約と公平な共通政策ONのSQ/N3経路は未実装。Fにも全国財政閉鎖、因果較正、個人の疾病/所得分布、施設別成果連動、先進医療技術別費用効果、人材供給の労働市場接続が残る。これらを今回の無制限な追加条件や新規承認ゲートにはしない。N3実装は開始していない。

## 引渡し

実装/計算/比較は本ディレクトリの個別原本。Manifest.jsonにサイズ・実バイトSHA-256を保存。GitHub格納後の固定原本Commitと事後取得結果はDelivery_Verification.jsonで別記し、記録Commitも区別する。正式Acceptance/Canonical化は実施しない。
'''
 (P/'Report.md').write_text(text)
 print(json.dumps(dict(rows=len(a),cases=len(c['cases'])+3,report_bytes=len(text.encode()))))
if __name__=='__main__':run()
