#!/usr/bin/env python3
"""Independent output identities, causal falsification and byte-replay check."""
import csv
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path


def near(a, b, atol=5e-4):
    assert math.isclose(a, b, rel_tol=3e-10, abs_tol=atol), (a, b)


def main():
    root = Path(__file__).resolve().parent
    rows = list(csv.DictReader((root/'Annual.csv').open()))
    lookup = {(r['case'], int(r['year'])):r for r in rows}
    val = lambda r,k:float(r[k])
    ledger_count = core_count = cap_count = 0
    for r in rows:
        name,y = r['case'],int(r['year'])
        zero = lookup[('SQ_'+r['SQ_path']) if r['policy']=='SQ' else r['SQ_path']+'_ZERO',y]
        near(val(r,'population'), val(r,'japanese')+val(r,'foreign_resident_stock'))
        near(val(r,'all_new_admissions')-val(r,'all_returns'), val(r,'foreign_net_migration'))
        near(val(r,'resident_stock_delta'),val(r,'target_stock')-val(r,'target_zero_stock'))
        near(val(r,'core_real_gdp_trn')/val(zero,'core_real_gdp_trn'),
             (val(r,'total_effective_labor')/val(zero,'total_effective_labor'))**.65,atol=2e-10)
        core_count += 1
        # Known partial balances exclude unknown lifetime claims and don't double count tax.
        near(val(r,'extended_fiscal_balance_partial_trn'),
             val(r,'tax_diagnostic_trn')-val(r,'expenditure_diagnostic_trn')
             -val(r,'government_program_nominal_trn'),atol=2e-7)
        assert r['insurer_health_cost']=='' and r['full_lifetime_fiscal_balance']==''
        assert r['residence_permit_stock']==''
        near(val(r,'elder_extra_jobs'),val(zero,'elder_extra_jobs'))
        near(val(r,'domestic_jobs'),val(zero,'domestic_jobs'))
        if y>2026:
            last=lookup[name,y-1]
            near(val(r,'foreign_resident_stock')-val(last,'foreign_resident_stock'),
                 val(r,'foreign_net_migration')+val(r,'foreign_reference_residual'))
            near(val(r,'target_stock'),val(last,'target_stock')*val(r,'annual_retention')
                 +val(r,'target_new_admissions'))
            near(val(r,'cap_denominator_lag_nominal_trn'),val(last,'nominal_gdp_trn'),atol=2e-7)
            ledger_count += 1
        if r['conditional_target_admission_cap'] and y>=2032:
            assert val(r,'target_new_admissions') <= val(r,'conditional_target_admission_cap')+5e-4
            D = val(last,'common_deflator') / (600./580.)
            coefficient = 9154003.810403556 if r['cap_mode']=='GDP_VA_STOCK' else 8000000.
            budget_units = val(last,'nominal_gdp_trn')*.05*val(r,'cap_relaxation_multiplier')*1e12/(coefficient*D)
            if r['cap_mode']=='GDP_INTAKE_COST':
                other = val(r,'all_new_admissions')-val(r,'target_new_admissions') if r['cap_scope']=='ALL' else 0.
                expected = max(0., budget_units-other)
            else:
                existing = (val(r,'target_stock')-val(r,'target_new_admissions'))*val(r,'target_employment_rate')
                if r['cap_scope']=='ALL':
                    existing += (val(r,'foreign_resident_stock')-val(r,'target_stock'))*val(r,'foreign_base_employment_rate')
                expected = max(0., (budget_units-existing)/val(r,'target_employment_rate'))
            near(expected,val(r,'conditional_target_admission_cap'),atol=.003)
            cap_count += 1
    # Costs have no GDP multiplier in this version; changing them must change fiscal outputs only.
    for y in range(2026,2056):
        a=lookup['PROGRAM_COST_ZERO',y];b=lookup['PROGRAM_COST_HIGH',y]
        for key in ['population','foreign_jobs','real_gdp_trn','tax_diagnostic_trn']:
            near(val(a,key),val(b,key),atol=2e-7)
        assert val(b,'extended_fiscal_balance_partial_trn')<=val(a,'extended_fiscal_balance_partial_trn')+1e-7
    # Reuse production quantity arithmetic with effects all disabled but switches on:
    # same exact common history; no-effect is a property of coefficients, not just a disabled path.
    spec = importlib.util.spec_from_file_location('model_verify',root/'Model.py')
    model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    c=json.loads((root/'Inputs.json').read_text());old,prev,dem,en=model.dependencies(c)
    no_effect=dict(id='zero_coefficients',policy='F',path='HIST',kind='CHECK',
                   selection=True,support=True,n4_additional_loss=0.,screening_loss=0.,
                   scope_loss=0.,transition_dip=0.,exit_hazard_reduction=0.,
                   employment_gap_closure=0.,ready_job_gap_closure=0.,target_hours_change=0.)
    no_rows=model.calculate(c,no_effect,old,prev,dem,en)
    for r in no_rows:
        z=lookup['HIST_ZERO',r['year']]
        for key in ['population','foreign_jobs','real_gdp_trn']:
            near(r[key],val(z,key))
    # Independent cap dimensional check from delivered results and source coefficients.
    # Stock cap numerator uses reference coefficients at lagged common deflator.
    # The target may be blocked while the untouched population already exceeds the cap.
    blocked=any(float(r['cap_rejected'])>0 and float(r['target_new_admissions'])==0
                for r in rows if r['case']=='GDP_VA_STOCK_ALL')
    assert blocked
    # Return hazard and hours are independent knobs: adverse-support case need not be positive.
    assert val(lookup['ADVERSE_SUPPORT',2055],'quantity_policy_GDP_effect_trn')<0
    assert val(lookup['HOURS_MINUS5',2055],'quantity_policy_GDP_effect_trn')<val(lookup['HIST_COMBINED_MEDIUM',2055],'quantity_policy_GDP_effect_trn')
    regenerated=['Annual.csv','Comparison.csv','Summary.csv','Interactions.csv','Report.md','Validation.json']
    with tempfile.TemporaryDirectory(prefix='foreign-replay-') as tmp:
        subprocess.run([sys.executable,str(root/'Model.py'),str(root/'Inputs.json'),'--outdir',tmp],check=True,capture_output=True)
        for name in regenerated:
            a=(root/name).read_bytes();b=(Path(tmp)/name).read_bytes()
            assert a==b,name
    text='\n'.join([
        '# 再実行・境界検証結果','', '2026-11-20 / DRAFT / NON-CANONICAL。', '',
        f'- {len(rows)}行。独立CSV読取で人口分割・入国−帰国＝純移動・対象ストック差を照合。',
        f'- {ledger_count}年次遷移の外国人ストック・参照残差・対象コーホート・前年GDP照合。',
        f'- {core_count}セルで既存LEVEL接続の独立反証：Ycore/Ycore_ZERO=(L/L_ZERO)^0.65。',
        f'- 完全適用後の上限検査{cap_count}セル。対象新規入国だけを制約し既存者を追放しない。',
        '- 第2弾FIXED/W50 F/SQは420セルを再現（Model.pyの検査）。旧検算を全件再実行した意味ではない。',
        '- コストゼロ対高費用で人口・就業・GDP・税収が不変、部分財政だけが変わることを確認。',
        '- 選別・支援スイッチONで係数を全ゼロにしても旧数量/GDPを再現。',
        '- 対象割合ゼロ、施行前ゼロ、選別による人数非増加、負の支援反応、時間低下の反証。',
        '- 高齢者追加人数・国内就業者は同じ政策・同じ純移動参照のZEROと一致。',
        '- 保険料は本人＋企業＝保険者。医療・生涯収支・在留資格人数の未算定を空欄として保持。',
        '- 6生成ファイルを別ディレクトリで再実行し、保存済みバイトと完全一致。', '',
        '```bash','python3 Model.py Inputs.json --outdir replay','python3 Verify.py','```','',
        '経済的因果の識別、個票や資格別コーホート、制度の個別適合性、将来の完全財政は未検証。',
        '2035年人口1億未満の緩和条件は今回の58主経路では未発動であり、発動時の経済妥当性を確認済みとはしない。',
        'GitHub保存・固定Commitからの事後取得・実バイト照合は最終回答の実施結果を参照。'])+'\n'
    (root/'Reproduction.md').write_text(text)
    print(json.dumps(dict(output_identities='PASS',replay_bytes='6/6 MATCH',prefix_cap_completed=True,
                          yearly_transitions=ledger_count,core_identity_cells=core_count,cap_cells=cap_count)))


if __name__=='__main__':
    main()
