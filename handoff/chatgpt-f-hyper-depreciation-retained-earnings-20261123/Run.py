"""Run pinned F with a separate corporate tax timing and disclosure diagnostic."""
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

def load(path):
    return json.loads(path.read_text())

root, out = (Path(p).resolve() for p in sys.argv[1:3])
name = sys.argv[3]
out.mkdir(parents=True, exist_ok=True)
inputs = load(Path(__file__).with_name('Inputs.json'))
scenario = inputs['scenarios'][name]
spec = importlib.util.spec_from_file_location('fixed_worker', root/'Prior_Worker.py')
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
original_mod = worker.mod
ledger = {}
vintages = {}
carry = {'normal': 0., 'accelerated': 0.}
stocks = []
retained = inputs['opening_retained_earnings_trn']

def loss_account(taxable, opening, rate):
    return max(taxable-opening, 0.)*rate, max(opening-taxable, 0.)


def adapted_mod(module_name, path):
    model = original_mod(module_name, path)
    if module_name != 'isolated_F_model':
        return model
    original_patch = model.patch

    def patch(engine, policy, medical, settings):
        namespace = original_patch(engine, policy, medical, settings)
        if policy != 'F':
            return namespace
        globals_ = namespace['run_path'].__globals__
        original_firm = globals_['firm_policy']

        def firm(p, year, nominal, initial, omit, halt):
            global retained
            old = original_firm(p, year, nominal, initial, omit, halt)
            if year in ledger:
                return ledger[year]['engine']
            scale = nominal / initial
            operating = p['corp_profit_base'] * scale
            rate = (.23 * (1 + globals_['schedule'](p['defense_surcharge_schedule'], year))
                    if year >= p['corp_start'] else p['corp_reference_rate'])
            active = not halt and 'firm' not in omit
            life = inputs['normal_tax_life']
            max_bonus = (life - 1) / life
            bonus = p['hyper_extra_deduction'] * scenario.get('bonus_multiplier', 1.)
            assert 0 <= bonus <= max_bonus
            applies = active and scenario.get('guideline', False) and year >= inputs['governance_start']
            link = bool(applies and year >= 2030 and scenario.get('tax_link'))
            uplift = 1 + inputs['tax_link_eligible_uplift'] * link
            cohort = (uplift * p['hyper_eligible_investment'] * scale * scenario.get('eligible_multiplier', 1.)
                      if active and scenario.get('hyper') and year >= p['investment_start'] else 0.)
            if cohort:
                vintages[year] = cohort
            ordinary = sum(basis/life for vintage,basis in vintages.items() if 0 <= year-vintage < life)
            adjustment = sum(basis * (bonus if year == vintage else -bonus/(life-1))
                             for vintage,basis in vintages.items() if 0 <= year-vintage < life)
            accelerated = ordinary + adjustment

            def usable(key, taxable):
                opening = carry[key]
                paid, carry[key] = loss_account(taxable, opening, rate)
                return paid, opening

            # Existing profit base is treated as after ordinary tax depreciation.
            normal_tax, opening_normal = usable('normal', operating)
            accelerated_tax, opening_accelerated = usable('accelerated', operating - adjustment)
            relief = normal_tax - accelerated_tax
            incremental_hyper_investment = relief * p['firm_investment_response'] * scenario.get('response_multiplier', 1.)
            # Disclosure-only default. Sensitivity deploys current-year cash, never the retained stock.
            dividend = inputs['reference_dividends_trn'] * scale
            cash_before_deployment = operating - accelerated_tax - dividend
            equipment = (max(0., cash_before_deployment) * p['governance_release_fraction']
                         * scenario.get('deployment_multiplier', 0.) if applies else 0.)
            if scenario.get('legacy'):
                new = old
                net_tax = normal_tax - (old['credit'] or 0.)
            else:
                isolated = dict(p, hyper_extra_deduction=0., governance_compliance=False)
                new = original_firm(isolated, year, nominal, initial, omit, halt)
                if active:
                    new['tax_delta'] -= relief
                    new['investment'] += incremental_hyper_investment + equipment
                net_tax = accelerated_tax
            net_income = operating - net_tax
            payout = dividend / net_income if net_income > 0 else None
            rule = scenario.get('rule', 'BODY_GT')
            cutoff = inputs['disclosure_threshold']
            flagged = bool(applies and payout is not None and
                           (payout > cutoff if rule == 'BODY_GT' else payout < cutoff))
            previous = retained
            if year > 2026:
                retained += net_income - dividend
            # Reporting reference only where three preceding simulated closing stocks exist.
            average = sum(stocks[-3:])/3 if len(stocks) >= 3 else None
            stocks.append(retained)
            ledger[year] = dict(engine=new, year=year, eligible_basis=cohort,
                                normal_depreciation=ordinary, accelerated_depreciation=accelerated,
                                deduction_shift=adjustment, rate=rate, taxable_normal=operating,
                                taxable_accelerated=operating-adjustment,
                                opening_normal_loss=opening_normal, opening_accelerated_loss=opening_accelerated,
                                normal_loss=carry['normal'], accelerated_loss=carry['accelerated'],
                                normal_tax=normal_tax, analytical_tax=net_tax, hyper_tax_relief=relief,
                                hyper_investment=incremental_hyper_investment, guideline_equipment=equipment,
                                guideline_applies=int(bool(applies)), tax_link_active=int(link), rule=rule, disclosure_flag=int(flagged),
                                retained_open=previous, retained_close=retained, net_income=net_income, dividends=dividend,
                                payout_ratio=payout, trailing_3yr_retained=average,
                                plan_equipment=equipment if applies else None,
                                plan_research=None, plan_human_and_wages=None,
                                plan_shareholder_returns=None, plan_additions=None, plan_other=None,
                                outside_director_opinion='UNOBSERVED' if applies else 'N/A',
                                actual_deployable_cash='N/A', actual_external_funding='N/A',
                                 buybacks=0., research=0.,
                                training=0., wages=0., cash_proxy_after_dividend_and_incremental_investment=
                                net_income-dividend-incremental_hyper_investment-equipment)
            return new

        globals_['firm_policy'] = firm
        return namespace

    model.patch = patch
    return model

worker.mod = adapted_mod
ci = load(root/'handoff/chatgpt-f-policy-cohort-fte-20261123/ANNUAL_FINE_WEEK_HOURS/Connection_Inputs.json')
worker.f(root, out, ci['common_offset'], ci['elder_delta'], 7)
worker.save(out/'Corporate.json', list(ledger.values()))
