"""Run the pinned integrated F worker with a narrow, non-adopted VAT override."""
import csv
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
root, out = (Path(p).resolve() for p in sys.argv[1:3])
case = sys.argv[3]
assert case in ('BASE', 'MEDICAL', 'MEDICAL_REBASE', 'MEDICAL_2038')
out.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('fixed_worker', root / 'Prior_Worker.py')
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
original_mod = worker.mod
inputs = json.loads((root / 'Diagnostic_Inputs.json').read_text())
burden = sum(count * amount for _, count, amount, _ in inputs['medical']) / 1e9
compensation = sum(count * amount for _, count, _, amount in inputs['medical']) / 1e9
growth = 1 + inputs['reference']['sector_growth']
start = 2036 if case == 'MEDICAL_2038' else 2035


def adapted_mod(name, path):
    model = original_mod(name, path)
    if name != 'isolated_F_model':
        return model
    original_load = model.load
    original_hook = model.vat_hook

    def load(config):
        result = original_load(config)
        integrated = result[3]
        execute = integrated.execute

        def capture(vat, vat_inputs, scenario):
            if case == 'MEDICAL_2038':
                scenario = dict(scenario, base_start=2036, base_ramp=3, year5=2038)
            result = execute(vat, vat_inputs, scenario)
            worker.save(out / 'Sector.json', result[2])
            return result
        integrated.execute = capture
        return result

    def hook(vat, medical, scenario):
        account = vat.sector_account

        def calibrated(config, vat_scenario, sector, year, rate):
            if case != 'BASE' and sector['id'] == 'medical' and year >= start:
                reference_sales = sector['R2025'] * sector['formerly_exempt_share']
                ratio = (2 * burden * growth / .10) / reference_sales
                sector = dict(sector, input_ratio=ratio)
                if case == 'MEDICAL_REBASE':
                    vat_scenario = dict(vat_scenario, medical_rebase=1.,
                                        medical_compensation_reference=compensation/(2*burden))
            return account(config, vat_scenario, sector, year, rate)

        vat.sector_account = calibrated
        original_hook(vat, medical, scenario)
        return account

    model.load = load
    model.vat_hook = hook
    return model


worker.mod = adapted_mod
connection = json.loads((root / 'handoff/chatgpt-f-policy-cohort-fte-20261123/'
                          'ANNUAL_FINE_WEEK_HOURS/Connection_Inputs.json').read_text())
worker.f(root, out, connection['common_offset'], connection['elder_delta'], 7)
