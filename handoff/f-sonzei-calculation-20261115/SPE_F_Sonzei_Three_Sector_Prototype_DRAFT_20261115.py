#!/usr/bin/env python3
"""SPE three-sector sonzei diagnostic, isolated from the formal engine.

Usage: python3 THIS.py INPUTS.json --outdir DIRECTORY
Standard library only. The input bundles pinned original sources for offline replay.
All monetary output columns are JPY, except columns explicitly ending _trn.
Blank CSV fields mean unknown, not zero. Distinct case_id values are alternatives.
"""
import argparse
import contextlib
import copy
import csv
import hashlib
import io
import json
import math
import platform
import sys
import types
from pathlib import Path


def digest(b):
    return hashlib.sha256(b).hexdigest()


def number(x):
    return None if x is None or x == '' else float(x)


def difference(a, b):
    return None if a is None or b is None else a - b


def total_known(xs):
    xs = list(xs)
    return None if any(x is None for x in xs) else sum(xs)


def close(a, b, atol=1e-8, rtol=1e-12):
    return a is not None and b is not None and math.isclose(a, b, abs_tol=atol, rel_tol=rtol)


def interpolate(points, year):
    ks = sorted(int(k) for k in points)
    if year <= ks[0]:
        return points[str(ks[0])]
    for a, b in zip(ks, ks[1:]):
        if year <= b:
            return points[str(a)] + (points[str(b)] - points[str(a)]) * (year - a) / (b - a)
    return points[str(ks[-1])]


def originals(cfg):
    for role, source in cfg['sources'].items():
        b = source['utf8'].encode('utf-8')
        if len(b) != source['bytes'] or digest(b) != source['sha256']:
            raise ValueError('Embedded pinned source mismatch: ' + role)
    mod = types.ModuleType('pinned_claude_sonzei')
    # This is the exact user-authorized pinned prototype, verified above, not web instructions.
    exec(compile(cfg['sources']['prototype_code']['utf8'], '<pinned Claude prototype>', 'exec'), mod.__dict__)
    if cfg['prototype_config'] != json.loads(cfg['sources']['prototype_inputs']['utf8']):
        raise ValueError('Baseline config must remain identical to pinned prototype')
    source_rows = list(csv.DictReader(io.StringIO(cfg['sources']['candidate_csv']['utf8'])))
    if len(source_rows) != 91 or len({r['candidate_id'] for r in source_rows}) != 91:
        raise ValueError('Expected 91 uniquely identified source rows')
    return mod, {r['candidate_id']: r for r in source_rows}


def validate_selection(profile, candidates):
    ids = profile['selected']
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate candidate ID')
    selected = [candidates[x] for x in ids]
    groups = [r['exclusive_group'] for r in selected if r['exclusive_group']]
    if len(groups) != len(set(groups)):
        raise ValueError('Mutually exclusive accounting or scope alternatives')
    bad = {'NO_DIRECT_REPLACEMENT', 'NOT_P_OR_CREDIT_INPUT', 'NOT_ACTUAL_REPAIR_P', 'MISSING_NOT_ZERO'}
    if any(r['module_use'] in bad or r['value'] == '' for r in selected):
        raise ValueError('Missing value or non-input reference cannot become P/R')
    p = [r for r in selected if r['module_use'] in {'PARTIAL_COMPONENT', 'CONDITIONAL_PARTIAL_P'}]
    revenue = [r for r in selected if r['module_use'] == 'SUBSET_R_ONLY']
    if len(p) > 1:
        raise ValueError('No summation of cross-sample components or parent/detail bundles')
    if len(revenue) > 1:
        raise ValueError('Use one pre-defined non-overlapping R subset, not combined totals and components')
    if any(r['module_use'] == 'COST_ENVELOPE_ONLY' for r in selected):
        if profile['kind'] != 'education_cost_sensitivity' or len(selected) != 1:
            raise ValueError('Cost envelope requires an explicit taxable-education share assumption')
    if any('NO_CROSS_SAMPLE_SUM' in r['aggregation_rule'] for r in selected) and len(selected) > 1:
        raise ValueError('Cross-sample combination rejected')
    return selected


def anchor(profile, candidates):
    selected = validate_selection(profile, candidates)
    out = dict(R=None, P=None, VAT=None, A=None, B=None)
    kind = profile['kind']
    if kind in {'purchase_partial', 'rental_management_partial'}:
        p = next(r for r in selected if r['module_use'] in {'PARTIAL_COMPONENT', 'CONDITIONAL_PARTIAL_P'})
        out['P'], out['VAT'] = number(p['net_taxable_base_yen']), number(p['input_vat_yen'])
        if kind == 'rental_management_partial':
            out['R'] = number(next(r['value'] for r in selected if r['module_use'] == 'SUBSET_R_ONLY'))
    elif kind == 'sales_partial':
        out['R'] = number(selected[0]['value'])
    elif kind == 'education_cost_sensitivity':
        share = profile['taxable_education_composite_share']
        if not 0 <= share <= 1:
            raise ValueError('Composite share outside [0,1]')
        out['P'] = number(selected[0]['value']) * share / 1.1
        out['VAT'] = out['P'] * .1
    elif kind == 'compensation_only':
        out['A'] = number(next(r['value'] for r in selected if r['parameter'] == 'compensation_A'))
        out['B'] = number(next(r['value'] for r in selected if r['parameter'] == 'tax_increase_B'))
    else:
        raise ValueError('Unknown profile kind: ' + kind)
    return out


def diagnose(policy, profile, base, year):
    scale = (1 + profile['growth_pct'] / 100) ** (year - profile['base_year'])
    scaled = {k: None if v is None else v * scale for k, v in base.items()}
    R, P, vat_sq = scaled['R'], scaled['P'], scaled['VAT']
    tau = interpolate(policy['tax_F_points'], year)
    tau0 = policy['tax_standard_statusquo']
    start = policy['start_years'][profile['sector']]
    started = year >= start
    # Preserve the 8/10 component mix in SQ; F converges to flat 5%, not 4%.
    # The interim min(current component rate, standard F rate) is provisional.
    if P is None:
        vat_f = None
    else:
        reduced_base = max(0.0, min(P, (.1 * P - vat_sq) / .02))
        standard_base = P - reduced_base
        vat_f = reduced_base * min(.08, tau) + standard_base * min(.1, tau)
    credit_sq = None if P is None else policy['current_exempt_activity_input_credit'] * vat_sq
    if not started:
        credit_f, eligible = (0.0 if P is not None else None), 'NOT_STARTED'
    elif P is None:
        credit_f, eligible = None, 'NO_INPUT_BASE'
    elif profile['credit_category'] == 'mixed_unknown':
        credit_f, eligible = None, 'BUILDING_SHARE_AND_F_RULE_UNRESOLVED'
    elif profile['credit_category'] == 'restricted_building':
        rule = policy['residential_building_credit_F']
        credit_f = 0.0 if rule == 'KEEP_RESTRICTION' else None
        eligible = 'RESTRICTION_RETAINED' if rule == 'KEEP_RESTRICTION' else 'F_BUILDING_RULE_UNRESOLVED'
    else:
        credit_f, eligible = policy['kappa'] * vat_f, 'ORDINARY_ELIGIBILITY_ASSUMED'
    L_sq, L_f = difference(vat_sq, credit_sq), difference(vat_f, credit_f)
    red = difference(L_sq, L_f)
    rate_red = difference(vat_sq, vat_f)
    base_red = difference(credit_f, credit_sq)
    output = 0.0 if not started else (None if R is None else tau * R)
    public = None if output is None else policy['phi'][profile['sector']] * output
    consumer = None if output is None else output - public
    dT_base = difference(output, base_red) if started else 0.0
    dT_rate = difference(vat_f, vat_sq)
    dT_total = total_known([dT_base, dT_rate])
    A_sq, B = scaled['A'], scaled['B']
    if A_sq is None:
        A_f, delta_A = None, (0.0 if not started else None)
    else:
        retention = profile.get('compensation_retention_after_start', 1)
        A_f = A_sq * (retention if started else 1)
        delta_A = A_f - A_sq
    # A is gross remuneration compensation, not a measured central-government cost.
    # Do not subtract delta_A from government balance without a public-financing share.
    delta_public_A = 0.0 if delta_A == 0 else None
    dT_after_future_public = difference(dT_total, public)
    net_public = difference(dT_after_future_public, delta_public_A)
    return {
        'case_id': profile['id'], 'sector': profile['sector'], 'year': year,
        'scope': profile['scope'], 'calculation_kind': profile['kind'],
        'source_candidate_ids': ';'.join(profile.get('selected', [])),
        'source_reference_year': profile['base_year'], 'year_value_class':'PROJECTED_ASSUMPTION_NOT_OBSERVED',
        'unit':'JPY', 'started_F':int(started), 'start_year_assumption':start,
        'tax_standard_SQ':tau0, 'tax_standard_F':tau,
        'R':R, 'P_net':P, 'input_VAT_SQ':vat_sq, 'input_VAT_F':vat_f,
        'input_credit_SQ':credit_sq, 'input_credit_F':credit_f,
        'credit_eligibility_F':eligible, 'L_SQ':L_sq, 'L_F':L_f,
        'L_reduction':red, 'L_reduction_rate_part':rate_red, 'L_reduction_credit_part':base_red,
        'output_VAT_SQ':0.0, 'output_VAT_F':output,
        'delta_tax_base':dT_base, 'delta_tax_rate_all_years':dT_rate,
        'delta_tax_attribution_total':dT_total,
        'legacy_delta_tax_rate_prestart':(dT_rate if not started else 0.0),
        'future_output_VAT_public_cost':public, 'future_output_VAT_consumer_cost':consumer,
        'delta_tax_after_future_public':dT_after_future_public,
        'historical_compensation_A_SQ':A_sq, 'historical_compensation_A_F':A_f,
        'historical_incremental_tax_B_reference':B,
        'historical_compensation_change':delta_A,
        'historical_compensation_public_cost_change':delta_public_A,
        'delta_public_budget_with_known_compensation':net_public,
        'business_retained_credit_only':None if credit_f is None else (1-policy['theta'])*credit_f,
        'macro_GDP_addition':0.0, 'aggregate_permission':'NEVER_SUM_DIFFERENT_CASES',
        'assumptions_ref':'INPUT_JSON:profiles/'+profile['id'] if profile.get('selected') else 'INPUT_JSON:prototype_config+policy',
    }


def national_profiles(cfg, guarded):
    c = cfg['prototype_config']
    answer=[]
    for sector, s in c['sectors'].items():
        R=s['R_2025']['value']*1e12
        p={'id':('NATIONAL_GUARDED_' if guarded else 'CLAUDE_BASELINE_')+sector,
           'sector':sector,'kind':'national_assumption_guarded' if guarded else 'legacy_baseline_reference',
           'scope':'NATIONAL_PLACEHOLDER_NOT_SOURCED_ESTIMATE','base_year':2025,
           'growth_pct':c['nominal_growth_pct']['value'],
           'credit_category':'mixed_unknown' if guarded and sector=='rental' else 'ordinary',
           'assumptions':'R/p/phi/kappa/開始年等は固定Claude試作の無出典仮定。住宅の旧基準κ適用は再現専用で法的控除認定ではない'}
        base={'R':R,'P':R*s['p_ratio']['value'],'VAT':.1*R*s['p_ratio']['value'],'A':None,'B':None}
        answer.append((p,base))
    return answer


def all_rows(cfg, candidates):
    profiles=national_profiles(cfg,False)+national_profiles(cfg,True)
    profiles += [(p,anchor(p,candidates)) for p in cfg['profiles']]
    a,b=cfg['policy']['years']
    return [diagnose(cfg['policy'],p,base,y) for p,base in profiles for y in range(a,b+1)]


def reject(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError('Invalid input was accepted')


def run_checks(cfg,candidates,mod,rows):
    log=[]
    def check(name,fn):
        fn(); log.append('PASS '+name)
    def baseline_check():
        assert mod.selfcheck(cfg['prototype_config']) is True
        reference=mod.run(cfg['prototype_config'])
        own={(r['year'],r['sector']):r for r in rows if r['case_id'].startswith('CLAUDE_BASELINE_')}
        mapping={'R':'R','P':'P_net','L_statusquo':'L_SQ','L_F':'L_F','L_reduction':'L_reduction',
                 'L_reduction_rate_part':'L_reduction_rate_part','L_reduction_base_part':'L_reduction_credit_part',
                 'dT_base':'delta_tax_base','dT_rate':'legacy_delta_tax_rate_prestart',
                 'output_tax_gross':'output_VAT_F','input_credit':'input_credit_F',
                 'public_compensation':'future_output_VAT_public_cost',
                 'consumer_burden':'future_output_VAT_consumer_cost','business_retained':'business_retained_credit_only'}
        for ref in reference:
            r=own[(ref['year'],ref['sector'])]
            assert r['started_F']==ref['started']
            for old,new in mapping.items():
                assert close(r[new]/1e12,ref[old],atol=1e-9),(old,new,r,ref)
            assert close((r['delta_tax_base']-r['future_output_VAT_public_cost'])/1e12,ref['dT_base_net_of_public'],atol=1e-9)
    check('fixed Claude selfcheck + 90 rows x 15 monetary fields reproduced (trillion JPY abs tolerance 1e-9)',baseline_check)
    def report_rounding():
        mapping=[('L_SQ',2),('L_F',3),('L_reduction',4),('delta_tax_base',5),('legacy_delta_tax_rate_prestart',6)]
        n=0
        for line in cfg['sources']['prototype_report']['utf8'].splitlines():
            cells=[x.strip() for x in line.split('|')[1:-1]]
            if len(cells)!=9 or not cells[0].isdigit(): continue
            y=int(cells[0]);rs=[r for r in rows if r['year']==y and r['case_id'].startswith('CLAUDE_BASELINE_')]
            for col,pos in mapping:
                expect=float(cells[pos].replace('−','-'))
                assert abs(sum(r[col] for r in rs)/1e12-expect)<=.00501,(y,col)
            assert abs(sum(r['delta_tax_base']-r['future_output_VAT_public_cost'] for r in rs)/1e12-float(cells[7]))<=.00501
            assert abs(sum(r['business_retained_credit_only'] for r in rs)/1e12-float(cells[8]))<=.00501
            n+=1
        assert n==9
    check('9 original published excerpt years x 7 metrics match rounding',report_rounding)
    def unit():
        r=candidates['MED-M14-GROSS']; assert close(number(r['reported_amount_yen']),314618*1000)
        assert close(number(r['net_taxable_base_yen']),314618000/1.1)
        assert close(number(candidates['EDU-R-CASH-SUBSET']['value'])/1e12,.554115552)
        assert close(number(candidates['RENT-R-KNOWN']['value'])/1e12,13.7415925632)
    check('thousand-yen / yen / trillion-yen conversion',unit)
    def exclusive():
        p=copy.deepcopy(cfg['profiles'][0]);p['selected']=['MED-M14-GROSS','MED-M14-NET']
        reject(lambda:validate_selection(p,candidates))
    check('exclusive gross/net selection rejected',exclusive)
    def cross_sample():
        p=copy.deepcopy(cfg['profiles'][0]);p['selected']=['MED-M01-NET','MED-M14-NET']
        reject(lambda:validate_selection(p,candidates))
    check('cross-sample P summation rejected',cross_sample)
    def bundle():
        p=copy.deepcopy(cfg['profiles'][0]);p['selected']=['MED-BUNDLE-NET','MED-M10-NET']
        reject(lambda:validate_selection(p,candidates))
    check('parent bundle + detail double count rejected',bundle)
    def overlapping_R():
        p=copy.deepcopy(cfg['profiles'][0]);p['selected']=['EDU-R-CASH-SUBSET','EDU-R-NAT-CASH']
        reject(lambda:validate_selection(p,candidates))
    check('combined R subset + constituent rejected',overlapping_R)
    def duplicate():
        p=copy.deepcopy(cfg['profiles'][0]);p['selected']=['MED-M14-NET']*2
        reject(lambda:validate_selection(p,candidates))
    check('duplicate candidate rejected',duplicate)
    def missing():
        assert number('') is None and number('0')==0
        assert total_known([1,None]) is None
        p=copy.deepcopy(cfg['profiles'][0]);p['selected']=['GAP-medical-p_ratio']
        reject(lambda:validate_selection(p,candidates))
    check('missing remains unknown, real zero preserved, missing input rejected',missing)
    def planned():
        p=copy.deepcopy(cfg['profiles'][0]);p['selected']=['RENT-PLAN']
        reject(lambda:validate_selection(p,candidates))
    check('planned construction cost cannot become current investment P',planned)
    def restricted():
        p={'id':'test','sector':'rental','kind':'test','scope':'SYNTHETIC_TEST_ONLY','base_year':2025,'growth_pct':0,'credit_category':'restricted_building','assumptions':'test'}
        b={'R':200,'P':100,'VAT':10,'A':None,'B':None}
        r=diagnose(cfg['policy'],p,b,2040);assert r['input_credit_F'] is None and r['L_F'] is None
        pol=copy.deepcopy(cfg['policy']);pol['residential_building_credit_F']='KEEP_RESTRICTION'
        r=diagnose(pol,p,b,2040);assert r['input_credit_F']==0 and close(r['L_F'],5)
        r=next(r for r in rows if r['case_id']=='NATIONAL_GUARDED_rental' and r['year']==2040)
        assert r['input_credit_F'] is None and r['delta_tax_base'] is None
    check('residential building restriction and unresolved eligibility guard',restricted)
    def identities():
        for r in rows:
            if r['L_reduction'] is not None:
                assert close(r['L_reduction'],r['L_reduction_rate_part']+r['L_reduction_credit_part'],atol=.01)
            if r['delta_tax_attribution_total'] is not None:
                assert close(r['delta_tax_attribution_total'],r['delta_tax_base']+r['delta_tax_rate_all_years'],atol=.01)
            assert r['macro_GDP_addition']==0
            if r['output_VAT_F'] is not None:
                assert close(r['future_output_VAT_public_cost']+r['future_output_VAT_consumer_cost'],r['output_VAT_F'],atol=.01)
    check('loss/tax/public incidence identities; no macro GDP addition',identities)
    def start():
        p=copy.deepcopy(cfg['policy']);p['start_years']={s:2100 for s in p['start_years']}
        profile,base=national_profiles(cfg,False)[0]
        assert diagnose(p,profile,base,2055)['delta_tax_base']==0
        p=copy.deepcopy(cfg['policy']);p['kappa']=0
        r=diagnose(p,profile,base,2040);assert close(r['L_reduction_credit_part'],0)
    check('start-year and kappa=0 boundaries',start)
    def flat_target():
        p=copy.deepcopy(cfg['profiles'][0]);p['id']='REDUCED_RATE_TEST';p['base_year']=2025;p['growth_pct']=0
        b={'R':None,'P':100,'VAT':8,'A':None,'B':None}
        assert close(diagnose(cfg['policy'],p,b,2026)['input_VAT_F'],8)
        assert close(diagnose(cfg['policy'],p,b,2027)['input_VAT_F'],7.5)
        assert close(diagnose(cfg['policy'],p,b,2028)['input_VAT_F'],5)
    check('reduced-rate component converges to flat 5%, not proportional 4%',flat_target)
    def separate():
        rs=[r for r in rows if r['case_id'].startswith('MED-COMP-') and r['year']==2040]
        assert all(r['input_VAT_SQ'] is None and r['L_SQ'] is None for r in rs)
        assert any(r['historical_compensation_change']<0 for r in rs)
    check('historical compensation not misread as input VAT',separate)
    def scopes():
        for r in rows:
            if r['case_id'].startswith(('CLAUDE_BASELINE_','NATIONAL_GUARDED_')):
                assert r['scope']=='NATIONAL_PLACEHOLDER_NOT_SOURCED_ESTIMATE'
            else: assert r['scope']!='NATIONAL_PLACEHOLDER_NOT_SOURCED_ESTIMATE'
    check('sourced partial profiles and national placeholders remain separate',scopes)
    def coverage():
        keys={(r['case_id'],r['year']) for r in rows}
        ids={r['case_id'] for r in rows}
        assert len(keys)==len(rows)==len(ids)*30
        assert all((i,y) in keys for i in ids for y in range(2026,2056))
        assert len(ids)==len(cfg['profiles'])+6
    check('2026–2055 complete coverage, no duplicate case-year',coverage)
    return log


def fnum(x, scale=1):
    return '未算出' if x is None else f'{x/scale:,.9f}'


def report_text(cfg,rows,checks,outdir):
    baseline=[r for r in rows if r['case_id'].startswith('CLAUDE_BASELINE_')]
    highlights=[]
    for y in [2026,2028,2036,2037,2038,2040,2055]:
        r=[x for x in baseline if x['year']==y]
        highlights.append('|'+str(y)+'|'+'|'.join(fnum(sum(x[k] for x in r),1e12) for k in ['L_SQ','L_F','L_reduction','delta_tax_base','delta_tax_rate_all_years','future_output_VAT_public_cost'])+'|')
    ids=['MED-M14-GROSS','MED-BUNDLE-GROSS','EDU-SALES-CASH-SUBSET','EDU-PURCHASE-SHARE-50','RENT-MANAGEMENT-3','MED-COMP-病院-WITHDRAW','NATIONAL_GUARDED_rental']
    examples=[]
    for id in ids:
        r=next(r for r in rows if r['case_id']==id and r['year']==2040)
        examples.append('|'+id+'|'+'|'.join(fnum(r[k]) for k in ['R','P_net','L_reduction','output_VAT_F','historical_compensation_change'])+'|')
    sources='\n'.join('|'+role+'|`'+s['fixed_commit']+'`|`'+s['filename']+'`|'+str(s['bytes'])+'|`'+s['sha256']+'`|' for role,s in cfg['sources'].items())
    artifacts=[]
    for role in ['code','inputs','annual']:
        p=Path(__file__) if role=='code' else outdir/cfg['artifacts'][role]
        if p.exists():
            b=p.read_bytes();artifacts.append('|`'+p.name+'`|'+str(len(b))+'|`'+digest(b)+'`|')
    return f'''# SPE｜F損税モデル・3部門試作 実行報告

Status: DRAFT / PROVISIONAL / NON-CANONICAL / DIAGNOSTIC ONLY  
入力固定日時: {cfg['created_at']}  
実行環境: Python {platform.python_version()} / {platform.system()}。追加依存なし。

## 結果

**実装・ローカル実行PASS。** 固定Claude原コードを実行し、基準90行・金額15項目の再現、原報告の9年次抜粋×7指標の丸め一致を確認した。既存91行CSVを入力として読込み、{len(cfg['profiles'])}個の部分計算・感度ケースと、全国仮定3部門×2方式を、2026〜2055年の{len(rows):,}行へ出力した。全国の出典付き完全推計が完成したという判定ではない。

1. `{cfg['artifacts']['code']}`：計算・受領ハッシュ検査・入力選択防止・自己確認・レポート生成。
2. `{cfg['artifacts']['inputs']}`：固定原本6件のUTF-8本文とSHA、元Claude入力、91行CSV、暫定政策条件、部分ケース定義を内包。オフライン再実行可能。
3. `{cfg['artifacts']['annual']}`：全金額は円。空欄は未取得・条件未確定。ケース間単純合計禁止。
4. `{cfg['artifacts']['report']}`：本報告。実行ログと制限を含む。

## 固定入力・実バイト検証

固定CommitからGitHub連携のBase64で取得、デコードした実バイトのサイズ・SHA-256・Git blob SHA-1を確認した。91行CSVとNotesは前回の実測SHAとも一致。既存統計の再調査は行っていない。

|役割|固定Commit|ファイル|bytes|SHA-256|
|---|---|---|---:|---|
{sources}

Claude資料は `handoff/claude-sonzei-min-20261114/`、入力候補は `handoff/f-sonzei-input-bridge-20261115/`、F基準は `handoff/SPE_F_Provisional_Implementation_Basis_20261114.md`。固定原本は変更していない。

## 再実行コマンド・実行ログ

```bash
python3 {cfg['artifacts']['code']} {cfg['artifacts']['inputs']} --outdir replay
```

原コードCLIも作業ディレクトリ内で実行：

```text
python3 sources/SPE_sonzei_min_run_DRAFT.py sources/SPE_sonzei_min_inputs_DRAFT.json claude-baseline
exit=0
selfcheck OK; cases: 21
2026 10.0 1.47 1.47 0.00 0.00 0.00 0.00 0.00
2040  5.0 1.81 0.00 1.81 3.53 0.00 0.93 0.63
2055  5.0 2.27 0.00 2.27 4.42 0.00 1.16 0.79
```

今回コードの実行確認（{len(checks)}項目）：

```text
{chr(10).join(checks)}
rows={len(rows)}; profiles={len(cfg['profiles'])}+6; period=2026..2055
exit=0（全確認・CSV再読取完了後）
```

新たな多AIレビュー工程は設けていない。ここでの自己確認は実行コードの境界・計算検査であり、後続Claudeの独立検証PASSではない。

## 基準ケース再現（全て従来の全国仮定、兆円／年）

|年|L_SQ|L_F|損税削減|税ベース拡大ΔT|税率効果・全年度|新output VAT公費負担|
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(highlights)}

R2025=医療45・教育6・住宅20兆円、p=.20/.25/.20、年成長1.5%、税率10→7.5→5%、開始2038/2036/2037、φ=.9/.2/0、κ=1は固定Claude試作の暫定値を維持した。**出典付き全国値への置換ではない。** 減税先行・5%目標・2038完了というF基準と、未決の具体年次・係数を区別する。

旧コードの `dT_rate` は開始前だけを表示する。再現欄 `legacy_delta_tax_rate_prestart` はこの仕様を維持。一方、今回の `delta_tax_rate_all_years` は開始後も上流input VATの税率差を表示する。全年度差額を求めるときに、旧 `dT_base+dT_rate` だけを使わない。これは原コードの改変ではなく、新規コードで比較系列を明示したもの。

## 出典付き部分計算の2040年例（金額は円）

|case_id|R|P_net|損税削減|output VAT F|既存補填変更額|
|---|---:|---:|---:|---:|---:|
{chr(10).join(examples)}

施設別の金額は**1施設当たり**、教育・住宅部分集合は各対象集合。異なる単位範囲の行を合算しない。2023/2024の元値を1.5%名目成長で投影した2026〜2055値は実測ではない。人口・GDPエンジンとは接続していない。源泉の会計・税率の未確定条件も残す。

### 医療

施設別公表費用・当期投資について税込/税抜の排他的ケースを作成。材料8%/その他10%等はCSVの条件を継承。SQの8%/10%構成を保存し、Fの各成分税率は暫定的にmin(当該現行税率, F標準税率)とする。したがって到達時は両成分5%であり、8%成分を比例縮小した4%にはしない。中間経路・具体年次は政策確定値としない。費消額・在庫調整、介護/診療・附属事業の用途配賦は未了。

回答標本が違う経常費と投資を足していない。n=732の既存4費目束と構成費目も別ケース。施設数を掛けて全国化しない。投資の将来系列は同規模の**毎年新規取得**を仮定するため、2024取得ストックを年々再控除したものではないが、実際の更新投資計画は未取得。

既存補填A/Bは別標本の独立系列。維持と課税化後全撤回の2感度を計算し、Aをinput VATへ読み替えない。補填Aは診療報酬の増分で全額国庫支出とは限らず、公費・保険料・患者負担の分解が未取得。したがって撤回Aを丸ごと国庫節減として差し引かず `historical_compensation_public_cost_change` を未算出とする。

### 教育

公立・国立CF・国立PL・私立のRは範囲・会計系列ごとに分離。P未取得の売上ケースはoutput VATとφの帰着のみ計算でき、損税額・税収純増は空欄。国立の購入CF1.392兆円に対して教育用途かつ課税対象である合成割合25/50/75%を明示仮定し、税込10%除去後の**部分P感度**を計算した。これは教育用途を実測したものではなく、全国p=.25の置換ではない。

給与CF・投資CF・教育PLを購入CFへ足さず、減価償却・附属病院等の未分離も維持。売上と購入額の対象範囲が違うため、RケースとP感度を勝手に結合した「教育全国結果」を作っていない。

### 住宅

管理費3/5/10%・委託率100%というCSV既存感度を計算。Rは専用住宅の既知家賃proxy、Pは管理だけで、修繕・建物取得は含まれない。予定工事費は数値があってもPへの採用をコードが拒否する。

`CLAUDE_BASELINE_rental` は旧κ=1の数式再現だけで、現在の建物控除制限解除を認定しない。`NATIONAL_GUARDED_rental` はPのうち建物の比率も将来制限の取扱いも不明なので、開始後の控除・残存損税・税ベース差額を空欄にする。管理費ケースの通常仕入控除仮定と建物特例を混同しない。国税庁の既存調査済み制度条件は入力Notesを再利用し、今回再調査していない。

## 系列の意味

```text
L_SQ = input_VAT_SQ − input_credit_SQ
L_F  = input_VAT_F  − input_credit_F
損税削減 = (input_VAT_SQ−input_VAT_F) + (input_credit_F−input_credit_SQ)
税ベース差額 = output_VAT_F − (input_credit_F−input_credit_SQ)
税率差額 = input_VAT_F − input_VAT_SQ（開始後も別掲）
税収帰属差額 = 税ベース差額 + 税率差額
将来output VAT公費負担 = phi × output_VAT_F
既存補填変更 = A_F − A_SQ（input VATとは別）
```

税収帰属差額は部門上流の埋込税を含む旧モデルと同じ限定的な会計帰属指標で、国全体の税収純増ではない。全体効果は行動・価格・他部門・補填の公的負担分等が不足。`delta_public_budget_with_known_compensation` は必要系列がすべて既知の場合だけ計算し、unknownを0で埋めない。将来φの負担と歴史的補填を同一系列にしない。`macro_GDP_addition=0` は意図的に接続しない構造ゼロであり、経済効果がゼロという評価ではない。

CSVは同じケースのF/SQを横持ちし、排他ケースはcase_idで分離。assumptions_refは同梱JSONのprofilesのid、全国仮定はprototype_config+policyを参照する。全ケース合計・全国と施設平均の合計は提供しない。欠損の合計も未算出。JSONのケースを編集する場合でも同一排他群・二重計上・未取得値・計画額の誤採用は検査で拒否する。

## 成果物のローカル同一性

|ファイル|bytes|SHA-256|
|---|---:|---|
{chr(10).join(artifacts)}

本報告自身のサイズ・SHAは引渡し回答で提示する。原コード実行の `claude-baseline/` と取得原本、補助ログはローカル作業用であり、GitHub追加対象は指定4件だけ。完成4件の事後再取得はGitHub保存後に別途確認し、書込み前の本報告では保全PASSを先取りしない。

## 残余と終了

全国値・実際の将来投資・医療補填の公的負担内訳・教育用途按分・住宅建物の将来控除制度は未確定。成功済みの基準再現・部分計算・年次CSV生成は維持する。後続Claudeは同じ4原本から再実行し、独立に確認可能。

正式エンジン・政策原本・main・DecisionLogは未変更。正式Acceptance、Finding Close、Freeze、Canonical化、HOLD解除、新規RP・多AIレビュー工程は実施しない。RP-023／M19–25 HOLD、RP-024 PENDING維持。4原本の引渡し後停止。
'''


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('inputs',type=Path)
    ap.add_argument('--outdir',type=Path,default=Path('.'))
    args=ap.parse_args();cfg=json.loads(args.inputs.read_text(encoding='utf-8'))
    mod,candidates=originals(cfg)
    rows=all_rows(cfg,candidates)
    checks=run_checks(cfg,candidates,mod,rows)
    args.outdir.mkdir(parents=True,exist_ok=True)
    csvpath=args.outdir/cfg['artifacts']['annual']
    with csvpath.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    with csvpath.open(encoding='utf-8',newline='') as f:
        reread=list(csv.DictReader(f))
    assert len(reread)==len(rows)
    guarded=next(r for r in reread if r['case_id']=='NATIONAL_GUARDED_rental' and r['year']=='2040')
    assert guarded['input_credit_F']=='' and guarded['L_F']==''
    checks.append('PASS saved CSV reread, row count and unknown fields remain blank')
    # The input remains one independent original; replay needs no external source files.
    input_dst=args.outdir/cfg['artifacts']['inputs']
    if input_dst.resolve()!=args.inputs.resolve():
        input_dst.write_bytes(args.inputs.read_bytes())
    report=args.outdir/cfg['artifacts']['report']
    report.write_text(report_text(cfg,rows,checks,args.outdir),encoding='utf-8',newline='\n')
    for line in checks: print(line)
    print(f'rows={len(rows)}; profiles={len(cfg["profiles"])}+6; years=2026..2055; exit=0')
    for path in [Path(__file__),input_dst,csvpath,report]:
        b=path.read_bytes();print(path.name,len(b),digest(b))


if __name__=='__main__':
    main()
