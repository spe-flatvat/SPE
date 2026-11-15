# SPE｜F／StatusQuo暫定モデル Claude独立検証結果

**Status:** DRAFT / READ-ONLY VERIFICATION / NON-CANONICAL(Claude 作成、2026-11-15)
**依頼:** Owner(2026-11-15 22:15)。依頼文は「チャット回答で可」だが、Owner が「Markdown としてhandoffに格納できるならそちら」と指示したため、本書を `work/claude-handoff` に格納。対象コード・入力・CSV・政策原本への書込みなし。
**対象:** `spe-flatvat/SPE` 固定 Commit `c0347270009a375dddf65b2d3e596845fb6b5157`、`handoff/f-statusquo-provisional-20261115/` の5ファイル

## 0. 判定

| 区分 | 判定 |
|---|---|
| 実行再現性(原本照合・再実行・CSV一致) | **PASS** |
| V-02 限定修正 | **PASS**(変更は1式のみ。基準ケース不変。`credit_SQ>0`・欠損の挙動も意図どおり) |
| StatusQuo 計算式・年次結果 | **PASS**(別実装の再計算で 7 経路×30 年の主要 7 指標 1,470 セルが一致) |
| F／StatusQuo の比較可能性 | **条件付きで成立**。同一の式・初期値・イベント暦・年次定義での「前提の違いに基づく数値比較」としては成立。**政策効果の推定や予測としては解釈できない**(§5) |
| 政策推計の妥当性 | **判定対象外**(SQ 主ケースは旧 v5 の [推定] 候補。全国値・損税の接続も未確定) |
| 比較レポート作成に進めるか | **進めてよい**。重大な計算の誤りはない。ただし、§6 の表示条件(SQ を単一線でなく帯で示す、差分を前提差の分解として示す等)を守ることを推奨 |

Critical なし。比較レポート前に要対応と考える事項が SQ-01・SQ-02(解釈・表示)の2件。ほかは Minor／情報。

## 1. 原本取得と実バイト照合

固定 Commit から `git fetch --depth=1`(完全 SHA)→ `git show` で取得。実測のサイズ・SHA-256・blob SHA-1:

| 原本 | bytes | SHA-256 | blob SHA-1 |
|---|---:|---|---|
| `SPE_F_Sonzei_V02_Fixed_DRAFT_20261115.py` | 31,779 | `5e8f0ede81961301a9dec9274163e231afd4ddd48ed778b89434f6048b83ed95` | `eb4b338d00cec293ef7bd0f9011ff48fb6a4962a` |
| `SPE_StatusQuo_Provisional_Model_DRAFT_20261115.py` | 28,367 | `a2ab04e2701900a97feffc681ca434de3bdcc39cc45da82b38017366256c2ee9` | `e1e14c3ffc3d5e9af23159860f5c4c878cbfc6df` |
| `SPE_F_StatusQuo_Annual_Comparison_DRAFT_20261115.csv` | 127,965 | `e424d159ce5aa1a586e317c136c89118143203438e972f35d02a17ee544a59ca` | `b0b39b18c7c08ad98a237d041e85af2649c8b4cf` |
| `SPE_StatusQuo_Implementation_Run_Report_DRAFT_20261115.md` | 14,954 | `49282fa0cd6d266316875b604f0f77734ac1244f3ac30d9dfc3f57b542fb09a2` | `5d2bed3380824566e76df1e0a12ed0f5c6f3af70` |
| `SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json` | 259,844 | `caa34a7e177e462213e15d398a629cf11626637d4209a8d248253c69226415f8` | `7876e00bf172df3c80162afd04054644f8b893ba` |

- 実行報告が記載する V-02 コード SHA(`5e8f0ede…`)と一致。Work の「5/5 実バイト照合」は、私の実測の結果を代替しない扱いとし、上表は私が取得して計算した値。
- 入力 JSON は、固定エンジン2原本、F の入力・出力・アダプタ、政策原本、v5、旧損税コード・CSV、Claude 検証書を内包する(`sq_bundle.sources`)。モデルは内包本文の SHA 検査を実行時に行う。

## 2. 再実行と CSV 一致

```text
python3 -I SPE_StatusQuo_Provisional_Model_DRAFT_20261115.py SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json --outdir replay
python3 -I SPE_F_Sonzei_V02_Fixed_DRAFT_20261115.py SPE_StatusQuo_Provisional_Inputs_DRAFT_20261115.json --outdir v02-replay
```

- 環境: Python 3.13.17 / Linux(Work は 3.12.14)。標準ライブラリのみ。ともに `exit=0`、内蔵チェック全 PASS。
- 再生成 CSV(240 行)は保存 CSV と**バイト一致**(SHA-256 `e424d159…59ca`)。再生成された実行報告は、Python 版数の1行だけ原本と異なる。
- V-02 単独 CLI が出した 1,980 行の損税診断 CSV は、修正前原本(`5f7899dd…`)の SHA-256 `e4a0e91e…ed5a` と**一致**。

## 3. V-02 限定修正の検証

- **差分の限定:** 修正前コード(`5f7899dd`、私の先行検証と同一バイト列)と V-02 コードの `diff` は、`business_retained_credit_only` の1行(193 行目)のみ。`(1-θ)×credit_f` が `credit_f` または `credit_sq` が欠損のとき None、それ以外は `(1-θ)×(credit_f−credit_sq)` になる。
- **基準ケース不変:** 現行設定(`current_exempt_activity_input_credit=0`)で 1,980 行の CSV が修正前とバイト一致(§2)。
- **`credit_SQ>0`(私が別に実行):** 係数を 0.0／0.5／1.0 に変えて旧・新両コードで 1,980 行を再生成。係数 0.0 は全列一致。係数 0.5・1.0 では、両者で異なる列は `business_retained_credit_only` のみ(1,481 行)で、新コードの値は全行 `(1−θ)(credit_F−credit_SQ)`(不一致 0)。損税・税収・公費負担の列は新旧で同一。
- **欠損:** 控除が欠損の行(住宅留保・部分ケースの欠損行)は None のまま。0 に埋めていない。
- **残る指摘:** V-01・V-03〜V-05 は今回も未変更(Work の報告どおり)。

## 4. StatusQuo 年次計算の検証

**独立再計算(付録A)。** 固定エンジン `prototype.py` を使わず、式(死亡・出生・人口、労働力成長、実質／名目成長、税収弾性、GDP 30% 上限、2031 年税収×0.9、歳出成長、資金不足 proxy)を私が別に書き、入力 JSON の係数だけから 7 経路を再計算した。実質GDP・名目GDP・税収・歳出・人口・出生・死亡の 7 指標×30 年×7 経路=**1,470 セルが相対差 7e-16 以内で一致**。アダプタの配線(F／SQ／感度ケースごとの係数の割り当て、2026 の扱い、移民ランプ、賃金アンカーと出生への入力)も、この再計算で確認できた。

| 確認項目 | 結果 |
|---|---|
| F と SQ の初期値・年次境界 | 2026 初期行の実質GDP 580、名目 600、税収 80、歳出 108、人口・死亡・出生が F／SQ で完全一致。主比較は 2027〜2055 の 29 回遷移、参考の2経路は 30 回(2026 を遷移として適用) |
| リスクイベント | F／SQ の `risk`・`event`・`inflation_risk`・`tax_event_factor`・`aging_drag` 列が全 30 年で一致。2027 年 5.5%(中台 5%＋気候 0.5%)、2031 年 3.5%(南海 3%＋気候 0.5%)で税収×0.90。v5 §3 の 2029 年起点 3 年毎災害・2027 年起点隔年気候と整合 |
| 2026 年オイルショックの扱い | 主 29 回遷移では**適用しない**(F 主ケースの境界との一致を優先)と実行報告・CSV(`risk_scheduled` 3%／`risk_applied` 0)に明示。F／SQ で対称。30 回参考(`*_30`)では適用 |
| 人口・出生・死亡 | `死亡×1.015`、`出生×0.975×(1+0.15×賃金成長)`、`人口+出生−死亡+純移民` と再計算が一致。純移民は 2030〜34 に線形ランプ(F 40 万、SQ 35.7 万=v5 の逆算値) |
| 労働成長率・GDP | `労働力成長=人口成長+エイジングドラッグ`、`実質成長=基調+消費+投資+教育−リスク+(1−α)×労働成長`(α=0.35)。SQ 主は消費・投資・教育の上乗せなし(CSV の予定列でも全 0) |
| 税収・歳出・proxy | `税収=min(前年×(1+名目成長×弾性)×イベント係数, 名目GDP×30%)`。SQ 弾性 0.85(〜2034)→0.75、歳出成長 3.0%。上限は主要経路で未到達。proxy=max(歳出−税収,0)。実際の国債発行額・PB・労働力人口は全行で空欄(proxy で埋めていない) |
| 旧 v5 パラメータとの対応 | SQ 主の基調成長 1.0／0.6／0.3%、弾性 0.85／0.75、歳出 3.0%、移民 35.7 万、賃金 400→472、ジニ 0.380→0.415 は、v5 §4-5(「現状維持(オプションB)」)の記載と一致。v5 の注記:確定本文9章が N3 と同一で「流用ミス」と判断したため、これらは[推定]として維持されたもの |
| v5 2055 との関係 | 30 回参考 `SQ_V5_LEGACY30` は実質GDP 381.25(v5:381.4、−0.04%)、人口 8,291 万(v5:8,298、−0.08%)、proxy 173.98(v5 の『国債発行』174)で、旧 v5 をほぼ再現する。主 29 回との差(GDP +14.5 兆円、人口 +212 万人)は、おおむね境界(2026 年の遷移とショック)の違いで説明できる(旧 v5 への一致の要求はなし) |
| F 固有効果の SQ への混入 | なし。SQ 主・移民 40 万反実仮想は、消費刺激・投資促進・教育・F の弾性・F の歳出成長・F の賃金アンカーを使わない。`SQ_POLICY9_LOW/HIGH` の投資 +0.3／+0.5pp と弾性 1.5／2.0 は、政策原本第 9 節に基づく別感度として分離 |
| 感度と主ケース | `case` 列で7経路が分離され、差分行(`record_type=DIFFERENCE`、`F_MINUS_SQ_V5_29`)は経路として合算しない設計。差分 30 行は F 主−SQ 主の PATH 行の差と全列で一致(最大差 0)、未知の指標は差分でも空欄 |

## 5. F／StatusQuo の比較可能性(依頼 D 1〜5)

### 5-1. 共通条件の数値比較として成立しているか
**成立する(条件付き)。** 同一の v6 関数・同一の初期状態・同一のリスク暦・同一のエイジングドラッグ・同一の名目成長定義・同一の年次定義で動いており、違いは次の「前提パラメータ」に限られる。差分は、この前提の違いが生む結果としての数値比較。

### 5-2. 差分の解釈範囲(私の分解)
F 主を出発点に、前提を SQ 主へ1つずつ入れ替える形で、2055 年の差を分解した(逐次分解のため順序に依存し、寄与は目安。付録B)。

| 前提の切替(SQ 主→F 主の方向) | 実質GDP | 税収 | 歳出 | proxy | 人口(万人) |
|---|---:|---:|---:|---:|---:|
| SQ 主(v5 候補) | 395.9 | 87.9 | 254.5 | 166.6 | 8,510 |
| +移民 40 万(F と同) | +3.1 | +0.5 | | | +103 |
| +賃金アンカー F(860) | +1.7 | +0.3 | | | +57 |
| +基調成長 1% 一定(F と同) | +50.3 | +8.1 | | | |
| +投資促進効果 | +67.7 | +10.9 | | | |
| +消費刺激効果 | +109.1 | +16.8 | | | |
| +教育効果 | +54.7 | +8.2 | | | |
| +税収弾性 F(1.5→1.7→2.0) | 0 | **+161.8** | | | |
| +歳出成長 F(2.5→1.5→1.0%) | 0 | 0 | **−84.1** | | |
| F 主 | 682.4 | 294.4 | 170.4 | 0.0 | 8,670 |

読み取り:
- **実質GDP差 286.5 兆円のうち、F の効果スケジュール(投資・消費・教育)が +231.5(81%)**、SQ の基調成長の減速(0.6→0.3%)との差が +50.3(18%)、移民・賃金が +4.8(2%)。これらは仕様に書かれた**加算項の差**で、内生的に導かれた政策効果ではない。
- **税収差 206.5 兆円のうち +161.8(78%)は税収弾性の仮定差**(F 1.5→2.0 対 SQ 0.85／0.75)。損税の経路から導かれた値ではない(先の整理どおり)。
- **proxy の差は、税収弾性と歳出成長の前提で決まる。** 歳出は F が 84 兆円少ない。
- **人口差 160 万人の 65% は移民前提(40 万 対 35.7 万)、35% は賃金アンカー(F 860 対 SQ 472)経由の出生**。賃金アンカーは「外生で、表示用」ではなく、出生を通じて人口とGDPに入る(SQ-03)。

したがって、差分は「Fの前提(施策効果・弾性・歳出・移民・賃金)を置いた場合と、SQ 主候補の前提を置いた場合の差」として示す範囲までは解釈できる。**F の施策が 286 兆円のGDPを生む**といった因果・予測の表現は、この計算からは言えない。

### 5-3. 外生アンカーと計算値の区別
実行報告・CSV(`wage_gini_status=EXOGENOUS_ANCHORS_NOT_ENDOGENOUS_RESULTS`、差分行では `ANCHOR_DIFFERENCE_NOT_DISTRIBUTION_EFFECT`)で区別されている。ジニアンカーはどこにも入力されず表示のみ(`.380` から終端への線形補間)。ただし賃金アンカーは出生に入る点と、列名の問題が残る(SQ-03)。

### 5-4. 損税診断のマクロ未接続・二重計上防止
維持されている。`sonzei_GDP_addition_trn`・`sonzei_tax_addition_trn` は全 210 行で 0、`sonzei_macro_link=FIXED_SECTOR_ASSUMPTIONS_NOT_LINKED_TO_THIS_MACRO_PATH`。`L_SQ` 参照値は全経路で同一(マクロGDPで自動スケールしない)。差分行には損税列を持ち込んでいない。なお F の弾性 1.7→2.0 は損税由来と断定できない値で、将来接続する際は SQ-08 の留意が要る。

### 5-5. 比較レポート前に修正が必要な重大問題
**なし**(計算・実装の誤りは見つからなかった)。表示と解釈の条件を §6 にまとめる。

## 6. 指摘事項と比較レポートでの扱い(最小修正案)

| ID | 重大度 | 内容 | 影響範囲 | 最小の扱い |
|---|---|---|---|---|
| SQ-01 | 要対応(解釈・表示) | SQ 主ケースは旧 v5 §4-5 の [推定] 候補(基調 1.0/0.6/0.3%、弾性 0.85/0.75、歳出 3%)で、現行の政策原本第 9 節(基調 1%、弾性 1.5〜2、投資 +0.3〜0.5)と異なる。v5 は第 9 節を「N3 と同一の流用ミス」と判断した。Work は両方を計算している(主+`SQ_POLICY9_LOW/HIGH`)。2055 年の実質GDPは 395.9／486.4／515.6 兆円、F との差は 286.5／196.0／166.8 兆円、proxy は 166.6／113.1／57.3 兆円 | 比較レポートの結論の大きさ | SQ を単一の線で示さず、**主候補+政策原本第 9 節の2端点の帯**で示す。主候補が v5 [推定] で、原本第 9 節と相違していることを図の注記に必ず置く |
| SQ-02 | 要対応(解釈・表示) | F−SQ の差は、事前に置かれた加算スケジュール・弾性・歳出前提の差の合算(§5-2)。内生的な効果や予測ではない | 差分図の解釈 | 差分の説明に「前提の違いによる差」と明記。可能なら §5-2 の分解(前提ごとの寄与)を併記。「Fによる〇〇兆円の増加」といった因果表現を避ける |
| SQ-03 | Minor | 賃金アンカーは表示用でなく、出生(φ=0.15)を通じて人口とGDPに入る(2055 年の人口差の約 35%、GDP差の約 0.6%)。列名 `real_wage_anchor_man_yen` の初期値は 400 で、v5・政策原本の名目賃金中央値 400(実質は 380)。名目か実質かの表示が不整合(380／400 の食い違いは先から未裁定) | 賃金表示、人口差の解釈 | 比較レポートでは「賃金アンカー(外生。出生に入る)」と表記し、実質賃金とは呼ばない。380／400 の裁定は Owner(未裁定のまま) |
| SQ-04 | Minor | 政策原本第 6 節は SQ の帰結として「実質賃金の一貫した下落」と述べるが、SQ 主の賃金アンカーは 400→472(上昇)。これは v5 の [推定] | SQ 賃金・ジニの表示 | SQ の賃金・ジニの線を「SQ の結果」として示さず、外生アンカーの比較と明記。原本の記述との不整合があることを注記 |
| SQ-05 | 情報 | `funding_gap_proxy` は歳出−税収の正部の**年次フロー**で、債務残高・利払い・PB・実際の国債発行ではない。2026 の 28 兆円は初期国債参照値と同値(108−80)だが別概念 | 「国債発行」と書く表示 | レポートの語は「資金不足 proxy(年次)」。累積の債務や発散の断定をしない |
| SQ-06 | 情報 | 主 29 回遷移は 2026 年のオイルショックを適用しない(F／SQ 対称、実行報告に明記)。30 回参考では SQ 381.3、F 661.5 兆円。旧 v5 への近似は 30 回側 | 水準の読み | 図の注記に「2026 は初期状態、ショックは未適用」を維持 |
| SQ-07 | 情報 | V-01・V-03〜V-05(損税診断の列名対応・重複系列・year_value_class・全年度税率差の重複)は計算原本に未反映のまま | 損税診断の利用 | 未反映のまま。F／SQ の比較レポートでは損税をマクロへ加算しないので、今回は影響なし |
| SQ-08 | 情報 | F の税収弾性 1.5→1.7→2.0 は、F 文書 §6 で損税解消効果が一部含まれるとされる一方、損税の経路から導かれた値ではない。将来、損税診断をマクロに接続する際は二重計上の恐れ | 将来の接続時 | 今回は接続なし(維持)。接続時は別表示(案3)か、弾性の出所の整理が先 |

## 7. 限界(私が確認していないこと)

- 再計算は入力 JSON の係数に依存する。v5 の係数との照合は §4-5(SQ)・F の入力(既に F 主の再現で確認済みの固定 `30530ad2` と同一)に限る。エイジングドラッグの表(v5 §7)は、F 主が固定結果(661.5/682.4)を再現することで間接的に確認したにとどまり、IPSS 等の原データとは照合していない。
- v5 の 2055 年値の再現(381.4 等)は、30 回参考で近似することを確認したが、v5 が実際に用いたコード・全入力は無く、一致の寄与分解は行っていない。
- 政策原本の解釈(第 9 節を有効とみなすか、v5 の判断を採るか)、SQ の弾性・歳出の妥当性、F の効果スケジュールの妥当性は判定対象外。
- 実ブラウザ・他環境(Python 3.13.17 と 3.12.14 以外)の確認なし。

## 8. 範囲

読み取り専用の検証。HOLD(RP-023／M19–25)・PENDING(RP-024)は維持。Finding Close・正式 Acceptance・engine 変更・政策本文変更・新規 RP は行っていない。

## 付録A: 独立再計算(`indep_sq.py`、参考。本書以外のファイルとしては格納しない)

使い方: `python3 -I indep_sq.py <入力JSON> <比較CSV>`。結果: `independent SQ/F recompute: cases 7 cells 1470 max rel diff 6.89e-16`。

```python
import json,csv,math,sys
cfg=json.load(open(sys.argv[1],encoding='utf-8')); b=cfg['sq_bundle']; c=b['f_config']; a=b['assumptions']
rows=list(csv.DictReader(open(sys.argv[2],encoding='utf-8')))
idx={(r['case'],int(r['year'])):r for r in rows if r['record_type']=='PATH'}
def pw(tab,t): return [x['value'] for x in tab if x['from']<=t][-1]
def risk(t):
    s=0
    for r in c['risk_shock_pct']['rules']:
        if r['type']=='once' and t==r['year']: s+=r['pct']
        if r['type']=='every' and t>=r['start'] and (t-r['start'])%r['step']==0: s+=r['pct']
    return s/100
def wage_g(anch,t):
    ys=sorted(anch)
    for s,e in zip(ys,ys[1:]):
        if s<t<=e: return (anch[e]/anch[s])**(1/(e-s))-1
def run(case):
    isf=case.startswith('F_'); legacy=case.endswith('30')
    anch={int(k):float(v) for k,v in (c['wage_anchor_man_yen']['anchors'] if isf else a['wage_anchors_sq_man_yen']).items()}
    i=c['initial_state_2025_end']; R,N,T,E,P,D,B=[i[k] for k in ['real_gdp','nominal_gdp','tax_revenue','expenditure','population','deaths','births']]
    out={}
    low=case=='SQ_POLICY9_LOW_29'; high=case=='SQ_POLICY9_HIGH_29'
    if not legacy: out[2026]=(R,N,T,E,P,B,D)
    for t in range(2026 if legacy else 2027,2056):
        mig_ss=400000 if (isf or case=='SQ_V5_MIGRATION400_29') else a['sq_migration_steady']
        net=0 if t<2030 else mig_ss*min((t-2030+1)/5,1)
        wg=0 if t==2026 else wage_g(anch,t)
        D2=D*c['death_rate_coefficient']['value']; B2=B*c['birth_decline_coefficient']['value']*(1+c['phi']['value']*wg)
        P2=P+B2-D2+net; pg=P2/P-1
        lab=pg+pw(c['aging_drag_pp']['table'],t)/100
        base=.01 if (isf or low or high) else (.01 if t<=2034 else .006 if t<=2044 else .003)
        cons=pw(c['policy_effects_pct']['consumption_stimulus'],t)/100 if isf else 0
        inv=pw(c['policy_effects_pct']['investment_promotion'],t)/100 if isf else (.003 if low else .005 if high else 0)
        edu=pw(c['policy_effects_pct']['education'],t)/100 if isf else 0
        rg=base+cons+inv+edu-risk(t)+(1-c['alpha']['value'])*lab
        infl=.02+c['inflation_extra_pp']['by_year'].get(str(t),0)/100
        ng=rg+infl
        el=pw(c['tax_elasticity']['table'],t) if isf else (1.5 if low else 2.0 if high else (.85 if t<=2034 else .75))
        N2=N*(1+ng); R2=R*(1+rg)
        T2=min(T*(1+ng*el)*c['tax_factor_by_year'].get(str(t),1.0),N2*.3)
        eg=pw(c['expenditure_growth_pct']['table'],t)/100 if isf else .03
        E2=E*(1+eg)
        R,N,T,E,P,D,B=R2,N2,T2,E2,P2,D2,B2; out[t]=(R,N,T,E,P,B,D)
    return out
cases=sorted({k[0] for k in idx}); mx=0;n=0
for case in cases:
    o=run(case)
    for t,v in o.items():
        r=idx[(case,t)]
        for val,k in zip(v,['real_gdp_trn','nominal_gdp_trn','tax_revenue_trn','expenditure_trn','population_persons','births_persons','deaths_persons']):
            ref=float(r[k]); d=abs(val-ref)/max(1,abs(ref)); mx=max(mx,d); n+=1
            assert d<1e-9,(case,t,k,val,ref)
print('independent SQ/F recompute: cases',len(cases),'cells',n,'max rel diff',mx)
```

## 付録B: 前提の逐次入れ替えによる分解(2055 年、手順)

付録A と同じ式で、SQ 主の係数から出発し、(1)移民 40 万、(2)賃金アンカー 860、(3)基調成長 1% 一定、(4)投資促進、(5)消費刺激、(6)教育、(7)F の弾性、(8)F の歳出成長、の順に F の値へ切り替えた。最終段階は F 主(実質GDP 682.38、税収 294.39、歳出 170.38、人口 8,670.0 万)と一致し、分解の閉じ方に誤りがないことを確認した。順序を変えると各段の寄与は多少変わる(特に GDP の加算項の相互作用)。

---
*本書は、実装の再現性・計算式・比較可能性の確認で、政策の推奨・数値の保証ではありません。*
