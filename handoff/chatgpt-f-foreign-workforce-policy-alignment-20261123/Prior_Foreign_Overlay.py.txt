#!/usr/bin/env python3
"""F foreign-policy quantity overlay. DRAFT/NON-CANONICAL, stdlib only.
Keeps fixed Stage2 elder rates/weight, macro equations and immutable inputs.
python3 Model.py Inputs.json --outdir replay
"""
import argparse
import base64
import builtins
import copy
import csv
import hashlib
import json
import math
import zlib
from pathlib import Path

YEARS = range(2026, 2056)


def close(a, b):
    return math.isclose(a, b, abs_tol=1e-6, rel_tol=1e-10)


def dump(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({k: format(v, '.12g') if isinstance(v, float) else v
                             for k, v in row.items()})


def dependencies(c):
    code = zlib.decompress(base64.b64decode(c['stage1_model_zlib_base64']))
    assert hashlib.sha256(code).hexdigest() == c['stage1_model_sha']
    old = {'__name__': 'immutable_stage1_functions'}
    exec(compile(code, 'immutable_stage1.py', 'exec'), old)
    prev, dem, engine = old['dependency'](c['stage1_inputs'])
    return old, prev, dem, engine


def phase(y, n):
    return max(0., min(1., (y - 2030 + 1) / n))


def base_trajectory(c, prev, dem, mode):
    d, _ = prev['labor_trajectory'](
        c['stage1_inputs']['previous_inputs'],
        dict(id='SQ_' + mode, policy='SQ', mode='COMMON' if mode == 'HIST' else mode), dem)
    return d


def macro(c, engine, d, sq, elder, policy, case, end_year=2055):
    tx = copy.deepcopy(c['stage1_inputs']['previous_inputs']['base']['tx_inputs'])
    tx['_trajectory'] = d
    tx['_common_trajectory'] = sq
    tx['_elder'] = elder
    tx['initial'].update(population=d[0]['population'], births=d[0]['births_calendar'],
                         deaths=d[0]['deaths_calendar'])
    tx['common_model']['slack'] = .02
    tx['policy_inputs']['elderly_additional_workers'] = 0.
    spec = dict(id=case, policy=policy, profile='TEXT_ASSUMPTIONS', supply_cap=True,
                _link='LEVEL', _elder='MEDIUM',
                migration_override=dict(foreign_initial_stock=d[0]['foreign'],
                                        enforcement_mode='NONE_REFERENCE'))
    # Evaluate an already completed prefix for a lagged-GDP cap; no dummy future is fabricated.
    engine['range'] = lambda *args: builtins.range(2026, end_year+1) if args == (2026, 2056) else builtins.range(*args)
    try:
        return engine['run_path'](tx, spec)
    finally:
        engine.pop('range', None)


def pension_work_share(c, prev, y):
    pc = c['stage1_inputs']['previous_inputs']
    profile = prev['age_rates'](pc, y, True)
    count = lambda a, sex, n: n * prev['employment_rate'](pc, int(a), sex)
    employed = sum(count(a, sex, n) for a, v in profile.items() for sex, n in enumerate(v))
    under70 = sum(count(a, sex, n) for a, v in profile.items()
                  for sex, n in enumerate(v) if int(a) < 70)
    return under70 / employed


def calculate(c, spec, old, prev, dem, engine):
    s = {**c['defaults'], **spec}
    for key in ['target_entry_share','n4_additional_loss','screening_loss','scope_loss',
                'transition_dip','pension_coverage','public_support_share']:
        if not 0. <= s[key] <= 1.:
            raise ValueError('Invalid probability: ' + key)
    if s['ramp_years'] < 1 or not 0 < s['exit_hazard'] < 1:
        raise ValueError('Invalid ramp or exit hazard')
    reference = base_trajectory(c, prev, dem, s['path'])
    b = c['stage1_inputs']
    elder = old['elder_ledger'](b, dict(policy=s['policy'], elder='MEDIUM', weight=.5), prev)
    sqelder = old['elder_ledger'](b, dict(policy='SQ', elder='MEDIUM', weight=.5), prev)
    baseline_macro = macro(c, engine, reference, reference, elder, s['policy'], s['id'] + '_zero')
    # Eligibility restrictions and integration affect only post-2030 covered entrant cohorts.
    # Existing residents are not retrospectively expelled or relabelled as new admissions.
    T = T0 = 0.
    trajectory = []
    ledger = []
    previous_nominal = baseline_macro[0]['nominal_gdp_trn']
    previous_deflator = baseline_macro[0]['common_deflator'] / (600. / 580.)
    relaxed = False
    h = s['exit_hazard']
    for i, ref in enumerate(reference):
        y = ref['year']
        p = phase(y, s['ramp_years']) if s['policy'] == 'F' else 0.
        selection = p if s['selection'] else 0.
        support = p if s['support'] else 0.
        # Reference gross admission is an explicit closure of a fixed SQ net-flow path.
        # It excludes offsetting temporary trips; neither gross nor hazards are forecasts.
        Fprev = reference[i-1]['foreign'] if i else ref['foreign']
        M0 = ref['foreign_net_migration']
        O0 = h * Fprev if i else 0.
        A0 = M0 + O0 if i else 0.
        assert A0 >= 0.
        exposed = A0 * s['target_entry_share'] if y >= 2030 else 0.
        untreated = A0 - exposed
        N4loss = exposed * selection * s['n4_additional_loss']
        afterN4 = exposed - N4loss
        screening_loss = afterN4 * selection * s['screening_loss']
        after_screening = afterN4 - screening_loss
        scope_loss = after_screening * selection * s['scope_loss']
        transition_loss = (after_screening - scope_loss) * s['transition_dip'] * (
            1. - p) if s['selection'] and p else 0.
        request = after_screening - scope_loss - transition_loss
        hF = h * (1. - support * s['exit_hazard_reduction'])
        assert 0 <= hF <= 1.
        Tret = T * (1. - hF)
        T0ret = T0 * (1. - h)
        target_return = hF * T
        target_return0 = h * T0
        rate = ref['foreign_employed_conditional'] / ref['foreign']
        target_rate = rate + (1. - rate) * support * s['employment_gap_closure']
        target_rate += (1. - target_rate) * selection * s['ready_job_gap_closure']
        assert 0 <= target_rate <= 1.
        hour_weight = 1. + support * s['target_hours_change']
        assert hour_weight > 0.
        # Same nonmigration reference residual as the old model; no invented births or naturalisation.
        no_target_stock = ref['foreign'] + (Tret - T0ret) - exposed
        # no_target_stock includes the surviving targeted cohort but not its new admissions.
        unaffected_stock = no_target_stock - Tret
        assert unaffected_stock >= 0.
        cap = None
        factor = 1.2 if relaxed else 1.
        if y == 2035:
            # One-off source review; prior-year population is an explicit information lag.
            relaxed = reference[i-1]['population'] + (T - T0) < 1e8
            factor = 1.2 if relaxed else 1.
        if s['policy'] == 'F' and p and s['cap_mode'] != 'NONE':
            budget = previous_nominal * .05 * factor * 1e12
            coefficient = (c['reference']['VA_yen'] if s['cap_mode'] == 'GDP_VA_STOCK'
                           else c['reference']['labor_cost_yen']) * previous_deflator
            if s['cap_mode'] == 'GDP_INTAKE_COST':
                mandatory = untreated if s['cap_scope'] == 'ALL' else 0.
                cap = max(0., budget / coefficient - mandatory)
            else:
                existing_workers = Tret * target_rate
                if s['cap_scope'] == 'ALL':
                    existing_workers += unaffected_stock * rate
                cap = max(0., (budget / coefficient - existing_workers) / target_rate)
            # Phase in only the new entrant restriction. Existing/other-status inflows remain untouched.
            accepted = min(request, max(0., (1. - p) * request + p * cap))
        else:
            accepted = request
        cap_rejection = request - accepted
        admissions = untreated + accepted
        exits = O0 - target_return0 + target_return
        assert min(admissions, exits) >= -1e-6
        migration = admissions - exits
        Tnew = Tret + accepted
        T0new = T0ret + exposed
        difference = Tnew - T0new
        t = copy.deepcopy(ref)
        t['foreign'] += difference
        t['population'] += difference
        t['foreign_net_migration'] = migration
        assert t['foreign'] > 0.
        # Same conditional age mix for stock differences; Japanese population/rates fixed.
        if difference:
            raw = prev['age_rates'](b['previous_inputs'], y, True)
            denominator = sum(sum(v) for v in raw.values())
            wa = sum(sum(v) for a, v in raw.items() if 15 <= int(a) < 65) / denominator
            el = sum(sum(v) for a, v in raw.items() if int(a) >= 65) / denominator
            t['working_age'] += difference * wa
            t['elderly'] += difference * el
            t['under15'] = t['population'] - t['working_age'] - t['elderly']
        non_target = t['foreign'] - Tnew
        jobs = non_target * rate + Tnew * target_rate
        effective = non_target * rate + Tnew * target_rate * hour_weight
        t['foreign_employed_conditional'] = jobs
        t['effective_productive_workers'] = t['domestic_employed_conditional'] + (
            effective * c['reference']['VA_yen'] / c['reference']['domestic_VA_yen'])
        trajectory.append(t)
        if i:
            assert close(t['foreign'] - trajectory[i-1]['foreign'],
                         migration + ref['foreign_nonmigration_reference_residual'])
            assert close(t['population'] - trajectory[i-1]['population'],
                         ref['births_calendar'] - ref['deaths_calendar'] + migration
                         + ref['population_reference_bridge'])
        assert close(t['population'], t['foreign'] + t['japanese'])
        assert 0 <= jobs <= t['foreign']
        assert close(admissions, A0 - N4loss - screening_loss - scope_loss
                     - transition_loss - cap_rejection)
        # Annual fiscal support is in base-year prices. Incidence is diagnostic, no invented demand multiplier.
        screening = exposed * p * s['screening_unit_yen'] if s['selection'] else 0.
        orientation = accepted * p * s['orientation_unit_yen'] if s['support'] else 0.
        annual_support = Tnew * p * s['support_unit_yen'] if s['support'] else 0.
        extra_jobs = jobs - ref['foreign_employed_conditional']
        # Only incremental pension contributions, not a second addition to aggregate tax.
        covered_jobs = extra_jobs * pension_work_share(c, prev, y) * s['pension_coverage']
        pension = covered_jobs * c['reference']['annual_cash_wage_yen'] * .183
        govcost = screening + s['public_support_share'] * (orientation + annual_support)
        employer_cost = (1. - s['public_support_share']) * (orientation + annual_support)
        ledger.append(dict(
            year=y, phase=p, population=t['population'], japanese=t['japanese'],
            foreign_resident_stock=t['foreign'], residence_permit_stock=None,
            foreign_jobs=jobs, foreign_effective_labor=effective,
            foreign_base_employment_rate=rate, target_employment_rate=target_rate,
            target_hours_weight=hour_weight, target_stock=Tnew, target_zero_stock=T0new,
            target_new_admissions=accepted, requested_target_admissions=request,
            all_new_admissions=admissions, baseline_new_admissions=A0,
            reference_returns=O0, all_returns=exits,
            foreign_net_migration=migration, baseline_net_migration=M0,
            target_returns=target_return, target_zero_returns=target_return0,
            annual_retention=1. - hF, baseline_retention=1. - h,
            resident_stock_delta=difference,
            foreign_reference_residual=ref['foreign_nonmigration_reference_residual'],
            population_reference_bridge=ref['population_reference_bridge'],
            n4_rejected=N4loss, screening_rejected=screening_loss, scope_rejected=scope_loss,
            transition_rejected=transition_loss, cap_rejected=cap_rejection,
            conditional_target_admission_cap=cap, cap_relaxation_multiplier=factor,
            population_ratio=t['foreign'] / t['population'],
            policy_only_foreign_jobs=extra_jobs,
            domestic_jobs=t['domestic_employed_conditional'] + elder[i]['F_extra_jobs'],
            elder_extra_jobs=elder[i]['F_extra_jobs'], elder_effective_extra=elder[i]['effective_extra'],
            total_effective_labor=t['effective_productive_workers'] + elder[i]['effective_extra'],
            screening_base_trn=screening / 1e12,
            orientation_base_trn=orientation / 1e12, annual_support_base_trn=annual_support / 1e12,
            government_program_base_trn=govcost / 1e12,
            employer_program_base_trn=employer_cost / 1e12,
            incremental_pension_base_trn=pension / 1e12,
            insurer_health_cost=None, full_lifetime_fiscal_balance=None,
            status_transfers_net_population_effect=0., status_transfer_volume=None,
            covered_pension_jobs_delta=covered_jobs,
            F_source2035_relaxation=int(relaxed),
            population_annual_relaxation_monitor=int(p and t['population'] < 1e8)))
        T, T0 = Tnew, T0new
        # Population and employment are causal inputs, GDP is solved by the preserved engine.
        # For cap scenarios use the previous year's actual solved GDP, not a hidden fixed forecast.
        if s['cap_mode'] != 'NONE' and s['policy'] == 'F' and p:
            provisional = macro(c, engine, trajectory, reference, elder, s['policy'], s['id'], end_year=y)
            previous_nominal = provisional[i]['nominal_gdp_trn']
            previous_deflator = provisional[i]['common_deflator'] / (600. / 580.)
        else:
            previous_nominal = baseline_macro[i]['nominal_gdp_trn']
            previous_deflator = baseline_macro[i]['common_deflator'] / (600. / 580.)
    results = macro(c, engine, trajectory, reference, elder, s['policy'], s['id'])
    rows = []
    for i, (r, t, z) in enumerate(zip(results, trajectory, ledger)):
        D = r['common_deflator'] / (600. / 580.)
        row = dict(case=s['id'], policy=s['policy'], SQ_path=s['path'], kind=s['kind'],
                   cap_mode=s['cap_mode'], cap_scope=s['cap_scope'], **z)
        for key in ['real_gdp_trn', 'nominal_gdp_trn', 'core_real_gdp_trn',
                    'common_deflator', 'tax_diagnostic_trn', 'expenditure_diagnostic_trn',
                    'fiscal_balance_partial_trn', 'funding_gap_proxy_trn',
                    'I_policy_real_trn', 'capital_total_real_trn', 'supply_binding']:
            row[key] = r[key]
        row['core_GDP_zero_quantity_trn'] = baseline_macro[i]['core_real_gdp_trn']
        row['GDP_zero_quantity_trn'] = baseline_macro[i]['real_gdp_trn']
        row['quantity_policy_GDP_effect_trn'] = (r['real_gdp_trn'] - baseline_macro[i]['real_gdp_trn']) if s['policy'] == 'F' else 0.
        row['quantity_policy_tax_effect_trn'] = r['tax_diagnostic_trn'] - baseline_macro[i]['tax_diagnostic_trn']
        row['government_program_nominal_trn'] = z['government_program_base_trn'] * D
        row['employer_program_nominal_trn'] = z['employer_program_base_trn'] * D
        row['incremental_pension_nominal_trn'] = z['incremental_pension_base_trn'] * D
        row['employee_pension_nominal_trn'] = row['incremental_pension_nominal_trn'] * .5
        row['employer_pension_nominal_trn'] = row['incremental_pension_nominal_trn'] * .5
        row['extended_expenditure_partial_trn'] = r['expenditure_diagnostic_trn'] + row['government_program_nominal_trn']
        row['extended_fiscal_balance_partial_trn'] = r['tax_diagnostic_trn'] - row['extended_expenditure_partial_trn']
        row['policy_incremental_known_public_balance_trn'] = (
            row['extended_fiscal_balance_partial_trn'] - baseline_macro[i]['fiscal_balance_partial_trn']
            + row['incremental_pension_nominal_trn'])
        row['foreign_VA_ratio_diagnostic'] = z['foreign_jobs'] * c['reference']['VA_yen'] * D / (r['nominal_gdp_trn'] * 1e12)
        row['foreign_labor_cost_ratio_diagnostic'] = z['foreign_jobs'] * c['reference']['labor_cost_yen'] * D / (r['nominal_gdp_trn'] * 1e12)
        row['intake_cost_ratio_diagnostic'] = z['all_new_admissions'] * c['reference']['labor_cost_yen'] * D / (r['nominal_gdp_trn'] * 1e12)
        row['cap_denominator_lag_nominal_trn'] = results[i-1]['nominal_gdp_trn'] if i else None
        assert not r['circuit_halted']
        assert close(r['labor_force_population_proxy'], z['total_effective_labor'])
        assert close(row['employee_pension_nominal_trn'] + row['employer_pension_nominal_trn'], row['incremental_pension_nominal_trn'])
        rows.append(row)
    return rows


def run(inputs, outdir):
    original = Path(inputs).read_bytes()
    c = json.loads(original)
    old, prev, dem, engine = dependencies(c)
    paths = {}
    for spec in c['cases']:
        paths[spec['id']] = calculate(c, spec, old, prev, dem, engine)
    annual = []
    regression = 0
    for name, path in paths.items():
        for row in path:
            y = row['year']
            sq = paths['SQ_' + row['SQ_path']][y-2026]
            row['F_minus_SQ_GDP_trn'] = row['real_gdp_trn'] - sq['real_gdp_trn'] if row['policy'] == 'F' else 0.
            row['F_other_policy_GDP_trn'] = row['GDP_zero_quantity_trn'] - sq['real_gdp_trn'] if row['policy'] == 'F' else 0.
            row['population_vs_SQ'] = row['population'] - sq['population']
            row['foreign_jobs_vs_SQ'] = row['foreign_jobs'] - sq['foreign_jobs']
            baseline = next(z for z in c['stage2_reference'] if int(z['year']) == y and z['policy'] == row['policy'])
            row['GDP_vs_previous_stage2_trn'] = row['real_gdp_trn'] - float(baseline['real_gdp_trn'])
            if row['policy'] == 'F':
                assert close(row['F_minus_SQ_GDP_trn'], row['F_other_policy_GDP_trn'] + row['quantity_policy_GDP_effect_trn'])
            if name in ['SQ_HIST', 'HIST_ZERO']:
                for key, new in [('real_gdp_trn','real_gdp_trn'), ('nominal_gdp_trn','nominal_gdp_trn'),
                                 ('tax_diagnostic_trn','tax_diagnostic_trn'), ('population','population'),
                                 ('foreign','foreign_resident_stock'), ('foreign_employed','foreign_jobs'),
                                 ('effective_labor','total_effective_labor')]:
                    assert close(row[new], float(baseline[key])), (name, y, key, row[new], baseline[key])
                    regression += 1
            if y < 2030:
                zero = paths['SQ_' + row['SQ_path']] if row['policy'] == 'SQ' else paths[row['SQ_path'] + '_ZERO']
                for key in ['population','foreign_jobs','real_gdp_trn']:
                    assert close(row[key], zero[y-2026][key]), (name, y, key)
            annual.append(row)
    interactions = []
    for mode in ['HIST','LATEST','IPSS']:
        for intensity in ['LOW','MEDIUM','HIGH']:
            for i, y in enumerate(YEARS):
                z = paths[mode + '_ZERO'][i]
                a = paths[mode + '_SELECT_' + intensity][i]
                b = paths[mode + '_SUPPORT_' + intensity][i]
                ab = paths[mode + '_COMBINED_' + intensity][i]
                row = dict(SQ_path=mode, intensity=intensity, year=y)
                for metric in ['all_new_admissions','foreign_net_migration','foreign_resident_stock',
                               'foreign_jobs','foreign_effective_labor','population','real_gdp_trn',
                               'extended_fiscal_balance_partial_trn']:
                    row[metric + '_selection'] = a[metric] - z[metric]
                    row[metric + '_support'] = b[metric] - z[metric]
                    row[metric + '_combined'] = ab[metric] - z[metric]
                    row[metric + '_interaction'] = ab[metric] - a[metric] - b[metric] + z[metric]
                    assert close(row[metric + '_combined'], row[metric + '_selection'] + row[metric + '_support'] + row[metric + '_interaction'])
                interactions.append(row)
    # Falsification: no exposure => selection/retention/rate effects have no quantity channel.
    z = next(x for x in c['cases'] if x['id'] == 'HIST_ZERO')
    t = calculate(c, {**z, 'id':'NO_EXPOSURE_CHECK', 'selection':True, 'support':True,
                      'target_entry_share':0.}, old, prev, dem, engine)
    for a, b in zip(t, paths['HIST_ZERO']):
        for k in ['foreign_resident_stock','foreign_jobs','real_gdp_trn']:
            assert close(a[k], b[k]), k
    # Restrictions cannot create admissions; support can be negative as well as positive.
    for intensity in ['LOW','MEDIUM','HIGH']:
        for a, z in zip(paths['HIST_SELECT_'+intensity], paths['HIST_ZERO']):
            assert a['all_new_admissions'] <= z['all_new_admissions'] + 1e-6
            assert a['foreign_resident_stock'] <= z['foreign_resident_stock'] + 1e-6
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    dump(out/'Annual.csv', annual)
    dump(out/'Comparison.csv', [r for r in annual if r['year'] in [2030,2035,2038,2045,2055]])
    dump(out/'Summary.csv', [r for r in annual if r['year']==2055])
    dump(out/'Interactions.csv', interactions)
    checks = dict(cases=len(paths), annual_rows=len(annual), reference_regression_cells=regression,
                  accounting='PASS', no_pre2030_quantity_effect='PASS',
                  no_exposure_falsification='PASS', factorial_identities='PASS',
                  stable_elder_policy='FIXED_RATES_WEIGHT_0.5', GDP_link='PRESERVED_LEVEL_0.65')
    (out/'Validation.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2)+'\n')
    (out/'Report.md').write_text(report(c, paths, interactions, checks), encoding='utf-8')
    assert Path(inputs).read_bytes() == original
    print(json.dumps(checks, ensure_ascii=False))


def report(c, paths, interactions, checks):
    lines = ['# F外国人材受入政策：数量効果実装・実行比較', '',
             '2026-11-20 / DRAFT / NON-CANONICAL。RP-023／M19–25 HOLD、RP-024 PENDING維持。', '',
             '## 新たに計算できること', '',
             'N4等の追加選別・審査・移行減、就業率と定着の改善、時間投入、GDP比上限の解釈を独立入力として実装した。新規受入、帰国、純移動、外国人常住人口、就業頭数、実効投入を別勘定にした。既存の制度フラグだけの版から、これらの条件を変えて2026〜2055の人口・GDP・部分財政を比較できるようになった。効果係数の因果推定・正式政策定義の確定はしていない。', '',
             '## 2055年：主な条件付き結果', '',
             '|SQ経路・条件|総人口万人|外国人常住万人|就業万人|実質GDP兆円|F−対応SQ兆円|外国人政策のみGDP兆円|',
             '|---|---:|---:|---:|---:|---:|---:|']
    for mode in ['HIST','LATEST','IPSS']:
        for name in ['SQ_'+mode,mode+'_ZERO',mode+'_SELECT_MEDIUM',mode+'_SUPPORT_MEDIUM',mode+'_COMBINED_MEDIUM']:
            r = paths[name][-1]
            lines.append('|'+name+'|'+'|'.join(f'{v:,.6f}' for v in [r['population']/1e4, r['foreign_resident_stock']/1e4, r['foreign_jobs']/1e4, r['real_gdp_trn'], r['F_minus_SQ_GDP_trn'], r['quantity_policy_GDP_effect_trn']])+'|')
    lines += ['', 'F−SQ全体には既存F税制・教育・高齢者等も含む。「外国人政策のみ」は同じSQ数量経路・他のF施策を固定したZEROとの差である。政府の制度移行・実績増をF効果に加算しない。', '',
              '## 2030〜2055：選別・支援・相互作用（HIST MEDIUM）', '',
              '|年|選別のみGDP差|支援のみGDP差|相互作用|複合GDP差|複合の人口差万人|複合の追加就業万人|',
              '|---|---:|---:|---:|---:|---:|---:|']
    for y in [2030,2035,2038,2045,2055]:
        r = next(r for r in interactions if r['year']==y and r['SQ_path']=='HIST' and r['intensity']=='MEDIUM')
        q = paths['HIST_COMBINED_MEDIUM'][y-2026]
        vals = [r['real_gdp_trn_selection'],r['real_gdp_trn_support'],r['real_gdp_trn_interaction'],r['real_gdp_trn_combined'],q['population_vs_SQ']/1e4,q['foreign_jobs_vs_SQ']/1e4]
        lines.append('|'+str(y)+'|'+'|'.join(f'{v:,.6f}' for v in vals)+'|')
    lines += ['', '支援は選別で減った人数を自動補填しない。複合−選別−支援＋ZEROを相互作用として全年出力する。マイナスは算術失敗ではない。', '',
              '## 数量勘定と適用範囲', '',
              '既存SQの純移動M0とストックS0を維持し、帰国O0=h×前年S0、新規受入A0=M0+O0へ分解する。hは後述の2025年構造図の帰国37万人／常住384万人からの条件付き参照。将来の観測定着率でも個人コーホート残存率でもなく、総受入・帰国の識別不足を閉じるモデル仮定。年0.05／0.15も比較する。HIST／LATEST／IPSS純移動経路を保ったままなので、68万人を毎年の確定受入にしていない。年次は既存10月人口間隔、構造図は暦年・概数であり時点差がある。', '',
              '2030以降の受入のうち対象割合を仮定し、A_targetへN4追加不適合・審査・対象資格・一時移行の減少率を順に適用する。既存制度で既に満たすN4要件分を再び全員から控除しない。中間ケースの対象割合35%は未較正であり、実績在留資格ストック比を入国比へ置換した値ではない。対象外受入は維持し、資格変更は人口を増やさない。本人の出入国・資格変更は個票追跡せず、数量未識別部分を残す。', '',
              '対象コーホートTは2030年新規入国分から開始。T=(1−hF)×前年T+当年対象受入、hF=h×(1−段階導入×定着改善)。ZEROでも同じ対象コーホートT0を作り、外国人人口=S0+(T−T0)、総人口=P0+(T−T0)。日本人人口・出生死亡・国籍異動を含む参照残差と橋渡し項は固定。入国者と同じ人の就業を人口に再加算しない。追加移民の出生死亡・子孫・帰化の反応は未実装。', '',
              '就業率は既存の年齢男女構成から得るpに対し、対象コーホートだけp+(1−p)×支援係数×段階導入。頭数と時間比の実効投入を分ける。対象者年齢構成の国籍別実測較正は未達。地域分散による人数・生産性効果は未識別で、支援係数へ独立の実証効果を足していない。', '',
              '## GDP接続・財政', '',
              '高齢者第2弾の固定率・実効投入0.5、初期580／600兆円、LEVEL労働弾性0.65、資本・消費投資・供給上限・税収式を維持した。外国人915.400381万円／国内同係数の相対重みを一回だけ使用。就業者×915.4万円をGDPへ再加算せず、外国人固有の限界生産性と呼ばない。', '',
              '既存税収・歳出・部分収支を維持し、別列で追加審査、入国時教育、在留中支援費を計上。実証単価は未取得のため感度値。既存SQ講習・F拠点予算への追加サービス費という比較仮定であり、既存予算全額を重ねていない。実データで重複排除できた意味ではない。政府負担と企業負担を分離し、政府費だけをextended_expenditureへ加える。支援費から新たな乗数効果を発明せず、民間費の賃金・投資への波及は未算定（GDPは数量経路）。保険料は外国人追加就業の70歳未満参照割合×加入仮定×年収参照×18.3%の増分診断。年収参照378.99万円は2025年9月月額×12に2024年賞与を足した合成年率で、実測年収ではない。本人・企業折半、税収に合算しない。医療・全社会保障給付・家族サービス費・生涯財政・実国債発行・PBは未算定。支援費・保険料の診断は一般均衡の家計企業勘定に戻していないため、extended指標を完全財政収支と呼ばない。', '',
              '## GDP比5%・人口比3〜5%・緩和', '',
              'GDP比の分子は原文だけでは未指定。NONEは監視のみ。GDP_VA_STOCKは外国人就業者×VA参照、GDP_COST_STOCKは同×800万円人件費仮定、GDP_INTAKE_COSTは当年新規受入×800万円を仮の分子として比較。ALLとTARGETEDの適用範囲も分ける。費用・寄与・流量は異なる概念で、いずれも正式定義ではない。', '',
              '上限は前年の実行済み名目GDPを分母とする条件付き年次割当へ換算し、2030から段階適用する。分子の2026年価格係数は前年の共通デフレーターで名目化する。現在ストック・対象外受入は強制削減しないため、既存人数だけで5%を超える場合、対象入国をゼロにしても5%を達成できない。診断比率は当年GDP・デフレーターで別途出し、前年割当と同年比率を混同しない。人口比3〜5%は監視・目標として出力し、人口比5%をGDP上限へ読み替えない。', '',
              '2035中間評価で人口1億未満なら上限枠を1.2倍とする候補を実装。情報ラグは前年人口と明記し、別に年次監視列を出す。閾値未到達でも実装済み。上限緩和を受入人数の20%自動増にしない。具体的評価時点と分子はOwnerの制度定義が必要。', '',
              '## 主要な感度・2055年', '',
              '|条件|年間対象受入万人|外国人常住万人|人口比%|実質GDP兆円|外国人政策のみGDP兆円|追加既知公的収支兆円|',
              '|---|---:|---:|---:|---:|---:|---:|']
    for n in c['report_sensitivities']:
        r=paths[n][-1]
        lines.append('|'+n+'|'+'|'.join(f'{v:,.6f}' for v in [r['target_new_admissions']/1e4,r['foreign_resident_stock']/1e4,r['population_ratio']*100,r['real_gdp_trn'],r['quantity_policy_GDP_effect_trn'],r['policy_incremental_known_public_balance_trn']])+'|')
    lines += ['', 'LOW／MEDIUM／HIGHは係数強度の仮定であり、成果順位・信頼区間ではない。選別の増加と支援の増加を同時に変えるためHIGHがGDP最大とも限らない。政策係数のゼロ・負の支援反応・適用範囲・時間・費用・純移動の不確実性を比較し、単一効果は採用しない。Inputs.jsonに全値と出典区分を保存。', '',
              '## 再実行・検証', '', '```bash',
              'python3 Model.py Inputs.json --outdir replay', '```', '',
              json.dumps(checks, ensure_ascii=False), '',
              '標準ライブラリのみ・ネット接続不要。Stage1コードと固定入力は圧縮文字列としてInputsへ埋込み、SHA確認してロードする（ZIPパケットではない）。旧第2弾F/SQの人口・外国人・就業・実効投入・GDP・名目GDP・税収を420セル照合。2030前の政策ゼロ、ストックフロー、人口分割、保険料折半、相互作用合計、対象ゼロ反証を検査。旧Claudeの38経路検算PASSは旧固定対象だけ再利用し、本版への独立検算と呼ばない。再実行のファイル一致と追加境界検証はReproduction.mdを参照。', '',
              '## 原文・公的統計・較正と未較正', '',
              'Policy_and_Sources.mdに原文8項目の実装対応、一次統計、定義と取得制約、未較正事項を記録した。政策原文・main・既存固定成果は無変更。入国時N4と現行A1／講習・到達A2の差は確認できるが、試験受験者合格率を移民候補全体の通過率へ転用していない。外国人就業者の統計は届出範囲、在留者は資格範囲、モデル人口は常住範囲で異なる。', '',
              'Owner判断が必要なのはGDP比5%の分子・対象・基準年、対象資格・既存者適用、人口比目標の母集団、2035中間評価の時点、支援費の負担主体である。未定義でも感度計算は完遂した。今後の効果実証・正式仕様採用は本成果の完了条件へ追加しない。', '',
              '## 引渡し', '',
              '作業ブランチwork/chatgpt-handoff、保存先handoff/f-foreign-quantity-20261120/。Source_Integrity.jsonは取得した旧原本・固定Commit・サイズ・実バイトSHAを記録。SHA256SUMS.txtは今回成果の保存前ハッシュ。保存Commitと事後取得結果は最終回答で示す。正式Acceptance・Finding Close・Freeze・Canonical化・HOLD解除はしていない。']
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs')
    parser.add_argument('--outdir', required=True)
    args = parser.parse_args()
    run(args.inputs, args.outdir)
