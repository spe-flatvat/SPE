# SPE｜F損税モデル・ChatGPT実装 Claude独立検証結果

**Status:** DRAFT / READ-ONLY VERIFICATION / NON-CANONICAL(Claude 作成、2026-11-15)
**対象:** 実装 Commit `5f7899dd4d3e1fdd5f7e8c8202d23795bbc8e914`、`handoff/f-sonzei-calculation-20261115/` の4原本
**依頼:** Owner 指示「SPE｜F損税モデル・ChatGPT実装のClaude独立検証依頼」(2026-11-15)。新規レビュー工程・追加調査・統計の再調査は行っていない。対象原本への書込みなし。本書のみを `work/claude-handoff` に格納(Owner 指示)。

## 0. 判定

| 区分 | 判定 | 範囲 |
|---|---|---|
| 実行再現性 | **PASS** | 固定 Commit の4原本の実バイト一致、コード再実行で 1,980 行の CSV が原本とバイト一致、旧Claude試作 90 行と数値一致(定義差1件は §4 で恒等式として説明) |
| 計算式 | **PASS** | 損税削減・課税ベース拡大・税率効果・既存補填・公費負担の式を、別途書いた再計算(付録A)で全 1,980 行の主要6列(8,554 セル)と照合し一致。空欄(未取得・未確定)3,326 セルも一致 |
| 入力適用範囲・混同防止 | **PASS(軽微な留意あり)** | 91行の入力候補の排他条件・二重計上・単位換算・欠損値、住宅賃貸の現行制限と将来Fの未確定条件、全国仮定・部分実測・条件付き推計の区別は、確認した範囲で混同なし |
| 政策推計の妥当性 | **判定対象外(未取得データ待ち)** | 全国の課税仕入率などは未取得。これを理由に、上の実装 PASS を取り消さない(Owner 指示)。数値は「出典付き部分値」または「全国仮定(無出典)」の診断で、全国推計の完成とは言えない |

Critical・Major の指摘なし。以下の指摘(V-01〜V-05)は、いずれも計算結果を変えない注意・軽微な改善で、実装 PASS の条件ではない。

## 1. 固定対象の取得と実バイト照合

固定 Commit `5f7899dd…`(`spe-flatvat/SPE`)から `git fetch --depth=1`(完全 SHA 指定)→ `git show` で取得。サイズ・SHA-256・Git blob SHA-1 を実測。

| 原本 | bytes | SHA-256 | blob SHA-1 |
|---|---:|---|---|
| `SPE_F_Sonzei_Three_Sector_Prototype_DRAFT_20261115.py` | 31,746 | `95ea3c5ca87dfebd42eb4551ddf97a2396734b89d47926d4b8c0e21ada5538a4` | `71e84308db4e19d8fbe288e0a29f496efe07284d` |
| `SPE_F_Sonzei_Three_Sector_Inputs_DRAFT_20261115.json` | 137,774 | `92d96a59888c50f97fe8c23a49109c9836856579971156b7e0970042dba8643d` | `015b7e4d4831f0c95c980bf051c448bdc624ce82` |
| `SPE_F_StatusQuo_Sonzei_Annual_Diagnostics_DRAFT_20261115.csv` | 926,134 | `e4a0e91e3f24ffec14a831c95b7d44bc116afff7655ff1ba483b9066c2c6ed5a` | `0ef275507b6ce32d402ec369f728cb9bbda48258` |
| `SPE_F_Sonzei_Three_Sector_Run_Report_DRAFT_20261115.md` | 13,377 | `1c3995638500ac9a620fafc2ed5da9bacbcd2dc2978b0f4cfa7de998b471318c` | `5b41f4f295752a51ea823dea6600d88a4f85dd41` |

- 原本の実行報告が記載する3件(コード・入力・CSV)の SHA-256 と、上の実測が一致。報告自身の SHA-256 は報告内に無く(「引渡し回答で提示」とある)、上の値は私の実測で、ChatGPT の引渡し値とは照合していない。
- 入力 JSON に埋め込まれた固定原本6件(Claude 試作3件=Commit `e87e4378…`、入力候補CSV・Notes=`05d2ea05…`、F基準書=`cc4a6054…`)を、それぞれの固定 Commit から取得し直し、埋め込み本文・サイズ・SHA-256 がバイト単位で一致することを確認(6/6)。
- 固定 Commit は浅い取得で、親 Commit の確認はしていない(依頼の対象外)。

## 2. 再実行と再生成

```text
python3 -I SPE_F_Sonzei_Three_Sector_Prototype_DRAFT_20261115.py SPE_F_Sonzei_Three_Sector_Inputs_DRAFT_20261115.json --outdir replay
```

- 実行環境: Python 3.13.17 / Linux(原本の実行報告は 3.12.14)。標準ライブラリのみ。出力末尾に `exit=0`、内蔵18項目すべて PASS、`rows=1980; profiles=60+6; years=2026..2055`。
- 再生成 CSV: 1,981 行(見出し+1,980 行)、**原本とバイト一致**(`cmp` 差なし)。再生成 JSON も入力とバイト一致。
- 再生成された実行報告は、原本と **1 行だけ**異なる(「実行環境: Python 3.13.17」と「3.12.14」)。環境表記による差で、数値・文面の差は無い。
- 66 ケース(部分計算・感度 60 + 全国仮定 6)× 30 年、case_id と年の重複なし。

## 3. 旧Claude試作 90 行との照合

旧試作(`e87e4378`、`SPE_sonzei_min_run_DRAFT.py`)の基準ケース出力 `base_yearly.csv`(90 行 = 3部門×30年)と、CSV の `CLAUDE_BASELINE_*`(90行)を、15 項目で照合(単位は兆円に換算)。

- R、P、L_SQ、L_F、損税削減、損税削減の税率部分・課税化部分、ΔT_base、旧 `dT_rate`(= `legacy_delta_tax_rate_prestart`)、出力税、控除、公費補填、消費者負担、事業者残存の **14 項目は 1,260 セル(90 行×14)すべてが絶対差 1e-9 以内で一致**。
- 残る 1 項目(旧 `dT_base_net_of_public` と、新 `delta_tax_after_future_public`)は**定義が異なる**ため一致しない。新=旧+`delta_tax_rate_all_years`(全年度の上流税率差)の恒等式が、90 行すべてで成り立つ(最大差 4.4e-16 兆円)。原本の実行報告が明記した変更(§4 V-01)。
- 原コード(`mod.selfcheck` と `mod.run`)を ChatGPT のコード内で実行する構造(埋め込みコードを `exec`)であることを確認。固定した本文(SHA 検査済み)のみを実行している。
- 旧試作の結果文書(2026-11-14)の2040年の値(損税削減 1.81、ΔT_base 3.53 兆円)は、CSV の基準ケース合算値と一致。

## 4. 指摘事項(いずれも計算は変えない)

| ID | 重大度 | 内容 | 影響範囲 | 最小修正案 |
|---|---|---|---|---|
| V-01 | Minor | 旧 `dT_base_net_of_public` と新 `delta_tax_after_future_public` は名前が近いが、後者は**全年度の税率差を含む**(上述の恒等式)。旧の列だけを前提にした集計が新 CSV を読むと、2027〜2035 年や 2038 年以降の値が食い違う | 旧試作の出力を使う後続スクリプト、旧結果文書の解釈 | CSV の列説明か実行報告に、対応表「新=旧+`delta_tax_rate_all_years`」を1行追記。実行報告の「系列の意味」節に既にほぼ記載があり、対応表の追加で足りる |
| V-02 | Minor(潜在) | `business_retained_credit_only` は `(1−θ)×credit_f` で、`credit_f − credit_sq` ではない。現行設定は `current_exempt_activity_input_credit=0` のため、`credit_sq=0` で結果は同じ。この係数を 0 以外にすると、損税解消による増分でなく控除総額を事業者残存として出す | 現行出力は影響なし。パラメータを変更した感度実行のみ | `(1−θ)×(credit_f−credit_sq)` に変更(行 193 付近)。係数 0 の現行出力は不変 |
| V-03 | Editorial | `CLAUDE_BASELINE_*` と `NATIONAL_GUARDED_*` は、医療・教育で全 30 年が数値一致(住宅のみ 2037 年以降 19 年で差)。同一系列が2つあり、部門でグループ化して合算すると二重計上になる。CSV には `aggregate_permission=NEVER_SUM_DIFFERENT_CASES` があり、意図的な構造だが、合算を防ぐ手段は注記のみ | 部門別・年別の集計を行う後続利用 | `duplicate_of`(または `series_family`)の列を追加。または実行報告に「医療・教育の2系列は同一値、比較用」と1行追記 |
| V-04 | Editorial | `year_value_class` は全 1,980 行が `PROJECTED_ASSUMPTION_NOT_OBSERVED` で、出典付き部分値(2023/24年の観測値を成長率で投影)・条件付き仮定(教育の按分、住宅の管理費率)・無出典の全国仮定の区別を持たない。区別は `scope`・`calculation_kind` にあり、混同はコード検査で確認済み(§5 の8) | 列を1つだけ見て読む利用 | `evidence_class`(SOURCED_PARTIAL / CONDITIONAL_ASSUMPTION / UNSOURCED_PLACEHOLDER)の列を追加(任意) |
| V-05 | 留意 | `delta_tax_attribution_total` は上流税率差(減税そのもの)を含む。将来 engine のマクロ側の減税(`tax_factor`)と接続すると重複する可能性。現状は `macro_GDP_addition=0` で未接続 | engine 接続時 | 接続する際は、旧構想メモ案3(別表示)を維持するか、税率差を除いた `delta_tax_base` だけを渡す。今回は対応不要 |

## 5. 依頼項目ごとの確認結果

1. **固定 Commit・実バイト SHA-256:** 一致(§1)。
2. **コード再実行・1,980 行の再生成:** 成功(§2)。
3. **再生成 CSV と原本の実バイト一致:** 一致(§2)。
4. **旧 Claude 試作 90 行との数値一致:** 14 項目一致、1 項目は定義差で恒等式により一致(§3)。
5. **91 行の入力候補:**
   - 排他条件: 税込/税抜の対(19 の `…-ACCOUNTING` グループ)が各2件で、同時選択はコードが拒否(`exclusive gross/net`)。親の束(`MED-BUNDLE-*`、n=732)と詳細の併用、回答標本の異なる費目の合算、重なる R の併用、重複指定も拒否する検査が通過。
   - 単位換算: 単位列(`JPY/facility/year`ほか)と `reported_amount_yen` の積が、数値と単位が両方ある行で全件一致(不一致 0)。20 組の GROSS/NET で、GROSS は `reported = net + vat`、NET は `reported = net`、`vat = net×税率`(医療 M11 と束は 8%/混在)が一致。束(`MED-BUNDLE-NET`)は M10〜M13 の合計と一致(1,173,208,000 円)。
   - 欠損値: `GAP-*` 6 行(`NO_DIRECT_REPLACEMENT`)と `MISSING_NOT_ZERO` 2 行は値が空で、プロファイルに選べない。出力 CSV の空欄 3,326 セルは未取得・条件未確定を表し、0 に埋めていない(実際の 0 は、開始前の控除 0 などの制度上の 0 のみ)。
   - 二重計上: 予定工事費(`RENT-PLAN`)や修繕(`NOT_ACTUAL_REPAIR_P`)を P に使う経路は拒否される。
6. **計算式:** 付録Aの独立再計算(式を別に書き直し、入力 JSON だけから 66 ケース×30 年を再計算)で、`input_VAT_SQ/F`、`input_credit_F`、`L_SQ`、`L_F`、`output_VAT_F` が全 8,554 セルで相対差 0、空欄の位置も 3,326 セルで一致。恒等式(`L=VAT−控除`、損税削減=税率部分+課税化部分、帰属差額=税ベース差額+税率差額、公費+消費者=出力税、`delta_tax_after_future_public`=帰属差額−公費)も 90 行で確認。8%/10% 混在の仕入は 5% へ収束し、8% 成分を比例縮小した 4% にならない。
7. **住宅賃貸:** 現行制度の非課税売上に対応する仕入の控除なし(`current_exempt_activity_input_credit=0`)と、将来 F の建物仕入の控除(`residential_building_credit_F=UNRESOLVED`)は別のパラメータ。`NATIONAL_GUARDED_rental` は開始後の控除・残存損税・税ベース差額が空欄(未確定)で、`CLAUDE_BASELINE_rental` は「旧κ=1の式の再現専用」と明記。管理費 3/5/10% の3ケースは通常の仕入として扱い、建物特例とは混ぜていない。
8. **全国仮定・部分実測・条件付き推計:** `scope` が3群に分離(`NATIONAL_PLACEHOLDER_NOT_SOURCED_ESTIMATE` は基準・全国仮定の6系列のみ。部分値は施設・収入部分集合・補填のみ)。部分値と全国仮定の合算・全国化は、CSV の構造上できず、コード検査(`scopes`)も通過。軽微な区別上の留意は V-03・V-04。

## 6. 限界(私の検証が確認していないこと)

- 検証の独立性: 付録Aの再計算は、式の実装を別に書いたものだが、入力 JSON(同一の91行CSVと政策条件)に依存する。入力の元の統計値(2023/24年の観測値など)は、出典と照合していない(依頼で再調査不要)。
- 住宅の建物仕入税額控除の現行条文や、F の将来条件そのものの正誤は検証していない(コードが未確定として扱うことだけを確認)。
- 税率経路、部門別開始年、φ、θ、κ、成長率は、固定 Claude 試作の暫定値のままで、政策確定値ではない。
- 実行報告が「再実行で確認」とする18項目のうち、コード内の検査が妥当かの観点は、私は付録Aと上記の観察で補ったが、すべての境界条件の網羅は主張しない。
- 実ブラウザ・実環境の差(Python 3.13.17 と 3.12.14)で数値差は出なかった。他環境は未確認。

## 7. 引き継ぎ・次の入力

- 出典付きの全国値(医療・教育・不動産賃貸の非課税売上と課税仕入率)が入った時に、入力 JSON の `prototype_config` と `profiles` を差し替えて再実行できる構造。検証手順(§2・付録A)をそのまま再利用できる。
- RP-023／M19–25 の HOLD、RP-024 の PENDING は維持。Finding Close、正式 Acceptance、engine 変更、政策本文変更、新規 RP は行っていない。

## 付録A: 独立再計算スクリプト(`indep_recalc.py`、参考。本書以外のファイルとしては格納しない)

使い方: `python3 -I indep_recalc.py <入力JSON> <CSV>`。結果: `independent recompute: cells 8554 blank-consistent 3326 max rel diff 0 profiles 66`。

```python
import json,csv,io,math,sys
cfg=json.load(open(sys.argv[1],encoding='utf-8'))
cand={r['candidate_id']:r for r in csv.DictReader(io.StringIO(cfg['sources']['candidate_csv']['utf8']))}
pol=cfg['policy']
def f(x):
    try: return float(x)
    except: return None
def tauF(y):
    pts=sorted((int(k),v) for k,v in pol['tax_F_points'].items())
    if y<=pts[0][0]: return pts[0][1]
    for (a,va),(b,vb) in zip(pts,pts[1:]):
        if y<=b: return va+(vb-va)*(y-a)/(b-a)
    return pts[-1][1]
def base_for(p):
    sel=[cand[i] for i in p['selected']]
    k=p['kind']; d=dict(R=None,P=None,V=None,A=None,B=None)
    if k in('purchase_partial','rental_management_partial'):
        c=[r for r in sel if r['module_use'] in('PARTIAL_COMPONENT','CONDITIONAL_PARTIAL_P')][0]
        d['P']=f(c['net_taxable_base_yen']); d['V']=f(c['input_vat_yen'])
        if k=='rental_management_partial': d['R']=f([r for r in sel if r['module_use']=='SUBSET_R_ONLY'][0]['value'])
    elif k=='sales_partial': d['R']=f(sel[0]['value'])
    elif k=='education_cost_sensitivity':
        P=f(sel[0]['value'])*p['taxable_education_composite_share']/1.1; d['P']=P; d['V']=P*.1
    elif k=='compensation_only':
        d['A']=f([r for r in sel if r['parameter']=='compensation_A'][0]['value']); d['B']=f([r for r in sel if r['parameter']=='tax_increase_B'][0]['value'])
    return d
def calc(p,d,y):
    g=(1+p['growth_pct']/100)**(y-p['base_year'])
    s={k:(None if v is None else v*g) for k,v in d.items()}
    R,P,V=s['R'],s['P'],s['V']; t=tauF(y); st=pol['start_years'][p['sector']]; on=y>=st
    out={}
    if P is not None:
        # split P into 8% and 10% parts from V
        rb=max(0,min(P,(0.1*P-V)/0.02)); sb=P-rb
        Vf=rb*min(.08,t)+sb*min(.1,t)
        cf=0.0 if not on else (None if p['credit_category']=='mixed_unknown' else pol['kappa']*Vf)
        out.update(Vsq=V,Vf=Vf,cf=cf,Lsq=V,Lf=None if cf is None else Vf-cf)
    else: out.update(Vsq=None,Vf=None,cf=None,Lsq=None,Lf=None)
    out['ov']=0.0 if not on else (None if R is None else t*R)
    return out,s
rows=list(csv.DictReader(open(sys.argv[2],encoding='utf-8')))
idx={(r['case_id'],int(r['year'])):r for r in rows}
mx=0;n=0;blankmis=0
profiles=[]
for p in cfg['profiles']: profiles.append((p,base_for(p)))
for sec,s in cfg['prototype_config']['sectors'].items():
    R=s['R_2025']['value']*1e12; pr=s['p_ratio']['value']
    for pre,cat in(('CLAUDE_BASELINE_','ordinary'),('NATIONAL_GUARDED_','mixed_unknown' if sec=='rental' else 'ordinary')):
        p=dict(id=pre+sec,sector=sec,base_year=2025,growth_pct=cfg['prototype_config']['nominal_growth_pct']['value'],credit_category=cat)
        profiles.append((p,dict(R=R,P=R*pr,V=.1*R*pr,A=None,B=None)))
for p,d in profiles:
    for y in range(2026,2056):
        o,s=calc(p,d,y); r=idx[(p['id'],y)]
        for key,val in (('input_VAT_SQ',o['Vsq']),('input_VAT_F',o['Vf']),('input_credit_F',o['cf']),('L_SQ',o['Lsq']),('L_F',o['Lf']),('output_VAT_F',o['ov'])):
            c=f(r[key])
            if val is None: 
                assert r[key]=='' ,(p['id'],y,key,r[key]); blankmis+=1
            else:
                assert c is not None,(p['id'],y,key)
                mx=max(mx,abs(c-val)/max(1,abs(val))); n+=1
print('independent recompute: cells',n,'blank-consistent',blankmis,'max rel diff',mx,'profiles',len(profiles))
```

---
*本書は、実装の再現性・計算式・入力の取り扱いの確認で、政策の推奨・数値の保証ではありません。*
