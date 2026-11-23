"""Export and verify integrated and corporate accounts."""
import ast
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

runs, replay, out = map(Path, sys.argv[1:])
here = Path(__file__).resolve().parent
inputs = json.loads((here/'Inputs.json').read_text())
fixed = {int(r['year']): r for r in csv.DictReader((here/'Fixed_F_BASE_OFF_Excerpt.csv').open())}
cases = inputs['scenarios']
metrics = '''real_gdp_trn nominal_gdp_trn I_policy_real_trn capital_total_real_trn corporate_tax_delta
corporate_credit corporate_induced_investment
tax_diagnostic_trn real_wage_proxy_man nominal_wage_proxy_man consolidated_partial_balance_proxy_trn'''.split()
paths = {}
annual, accounts, schedules, diffs = [], [], [], []
count = 0
reproduction = {}

def check(a, b):
    global count
    assert math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10), (a,b)
    count += 1

def data(folder, case, name):
    return (folder/case/(name+'.json')).read_bytes()

def write(name, rows):
    with (out/name).open('w',newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0], lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

for case, spec in cases.items():
    for file in ('F_Actual_Annual','F_Runtime_Trace','Corporate'):
        a = data(runs,case,file)
        check(a == data(replay,case,file), True)
        reproduction[f'{case}/{file}.json'] = hashlib.sha256(a).hexdigest()
    path = json.loads(data(runs,case,'F_Actual_Annual'))
    trace = json.loads(data(runs,case,'F_Runtime_Trace'))
    account = json.loads(data(runs,case,'Corporate'))
    paths[case] = (path,account)
    life = inputs['normal_tax_life']
    bonus = trace['parameters']['hyper_extra_deduction'] * spec.get('bonus_multiplier',1.)
    allocation = {}
    for row in account:
        basis = row['eligible_basis']
        if not basis:
            continue
        vintage = row['year']
        normal, accelerated = [], []
        for offset in range(life):
            year = vintage + offset
            n = basis/life
            a = n + basis*(bonus if offset == 0 else -bonus/(life-1))
            normal.append(n)
            accelerated.append(a)
            schedules.append(dict(case=case,vintage=vintage,year=year,normal=n,accelerated=a,shift=a-n))
            pair = allocation.setdefault(year,[0.,0.])
            pair[0] += n
            pair[1] += a
            check(a >= 0, True)
        check(sum(normal),basis)
        check(sum(accelerated),basis)
    for i,(r,c,y) in enumerate(zip(path,account,range(2026,2056),strict=True)):
        check(r['year'],y)
        r.update(corporate_tax_delta=r['corporate_tax_delta_trn'], corporate_credit=r['corporate_credit_trn'],
                 corporate_induced_investment=c['engine']['investment'] or 0.)
        check(c['year'],y)
        check(c['retained_close'],c['retained_open']+(c['net_income']-c['dividends'] if i else 0))
        check(c['normal_depreciation'],allocation.get(y,[0,0])[0])
        check(c['accelerated_depreciation'],allocation.get(y,[0,0])[1])
        check(c['analytical_tax'] >= 0,True)
        check(c['payout_ratio']*c['net_income'],c['dividends'])
        check(c['cash_proxy_after_dividend_and_incremental_investment'],
              c['net_income']-c['dividends']-c['hyper_investment']-c['guideline_equipment'])
        check(c['tax_link_active'],bool(spec.get('tax_link') and y>=2030))
        check(c['guideline_applies'],bool(spec.get('guideline') and y>=2028))
        check(c['disclosure_flag'],bool(c['guideline_applies'] and
              (c['payout_ratio'] < .4 if spec.get('rule') == 'ANNEX_LT' else c['payout_ratio'] > .4)))
        if i:
            check(r['capital_delta_real_trn'],(1-trace['parameters']['depreciation'])*path[i-1]['capital_delta_real_trn']+r['I_policy_real_trn'])
            check(c['retained_open'],account[i-1]['retained_close'])
        if case == 'LEGACY_F':
            for k in metrics:
                if k in fixed[y]:
                    check(r[k],float(fixed[y][k]))
        else:
            check(r['corporate_credit'],0)
            reference_rate = trace['parameters']['corp_reference_rate']
            normal_delta = c['taxable_normal']*(c['rate']-reference_rate) if y>=2028 else 0.
            check(r['corporate_tax_delta'],normal_delta-c['hyper_tax_relief'])
        annual.append(dict(case=case,year=y,**{k:r[k] for k in metrics},
                           SQ_real_GDP=fixed[y]['SQ_real_GDP_trn'],N3_real_GDP=fixed[y]['N3_real_GDP_trn']))
        accounts.append(dict(case=case,**{k:v for k,v in c.items() if k!='engine'}))
for case,(path,account) in paths.items():
    for i,(r,c) in enumerate(zip(path,account,strict=True)):
        legacy, legacy_c = (a[i] for a in paths['LEGACY_F'])
        off, off_c = (a[i] for a in paths['BOTH_OFF'])
        if case in ('GUIDELINE_ONLY','BOTH_ANNEX_RULE','HYPER_TIMING_ONLY') or i<2:
            comparator = paths['BOTH_ON'][0][i] if case=='BOTH_ANNEX_RULE' else off
            for k in metrics:
                if case=='HYPER_TIMING_ONLY' and k not in ('real_gdp_trn','nominal_gdp_trn','I_policy_real_trn','capital_total_real_trn'):
                    continue
                check(r[k],comparator[k])
        base = dict(case=case,year=r['year'])
        for k in metrics:
            base[f'{k}_vs_legacy']=r[k]-legacy[k]
            base[f'{k}_vs_off']=r[k]-off[k]
        for k in ('analytical_tax','retained_close','dividends'):
            base[f'{k}_vs_legacy']=c[k]-legacy_c[k]
            base[f'{k}_vs_off']=c[k]-off_c[k]
        diffs.append(base)
source = ast.parse((here/'Run.py').read_text())
scope = {}
func = next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='loss_account')
exec(compile(ast.Module(body=[func],type_ignores=[]),str(here/'Run.py'),'exec'),scope)
loss = scope['loss_account']
for actual,want in zip(loss(-10,0,.23)+loss(6,10,.23)+loss(8,4,.23),(0,10,0,4,.92,0),strict=True):
    check(actual,want)
out.mkdir(parents=True,exist_ok=True)
write('Integrated_Annual.csv',annual)
write('Corporate_Annual.csv',accounts)
write('Vintage_Schedules.csv',schedules)
write('Comparison.csv',diffs)
(out/'Validation.json').write_text(json.dumps(dict(checks=count,failures=0,annual_rows=len(annual),branches=len(cases),
    reproduction_sha256=reproduction),indent=2)+'\n')
