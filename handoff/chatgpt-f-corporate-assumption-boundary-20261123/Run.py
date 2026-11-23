"""Execute one old-F counterfactual with verified fixed runtime sources."""
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True
root, prior, out = (Path(arg).resolve() for arg in sys.argv[1:4])
case = json.loads(Path(__file__).with_name("Inputs.json").read_text())["cases"][sys.argv[4]]
for entry in json.loads((prior / "Runtime_Sources.json").read_text()):
    data = (root / entry["path"]).read_bytes()
    assert len(data) == entry["size"]
    assert hashlib.sha256(data).hexdigest() == entry["sha256"], entry["path"]

source = root / "Prior_Worker.py"
worker = ModuleType("fixed_worker")
old = "trajectory_effective_L=v['c']"
new = """firm=v['firm'], firm_sources=v['firm_sources'],
               firm_investment=v['firm_investment'], firm_uninvested=v['firm_uninvested'],
               corporate_cash_stock=v['firm_cash_stock'], admin_firm=v['admin_firm'],
               vat_direct=v['f']['direct_tax'], vat_firm_cash=v['f'].get('_firm_cash',0.),
               education_firm_cash=v['z']['firm_training_cash_delta_trn'],
               trajectory_effective_L=v['c']"""
program = source.read_text()
assert program.count(old) == 1
exec(compile(program.replace(old, new), str(source), "exec"), worker.__dict__)
original_mod = worker.mod

def mod(name, path):
    module = original_mod(name, path)
    if name != "isolated_F_model":
        return module
    original_patch = module.patch

    def patch(engine, policy, medical, settings):
        ns = original_patch(engine, policy, medical, settings)
        if policy == "F":
            scope = ns["run_path"].__globals__
            original = scope["firm_policy"]

            def firm(p, year, nominal, initial, omit, halt):
                inputs = dict(p)
                if not case["hyper"]:
                    inputs["hyper_extra_deduction"] = 0.
                if not case["release"]:
                    inputs["governance_compliance"] = False
                return original(inputs, year, nominal, initial, omit, halt)

            scope["firm_policy"] = firm
        return ns

    module.patch = patch
    return module

worker.mod = mod
connection = root / "handoff/chatgpt-f-policy-cohort-fte-20261123/ANNUAL_FINE_WEEK_HOURS/Connection_Inputs.json"
inputs = json.loads(connection.read_text())
out.mkdir(parents=True, exist_ok=True)
worker.f(root, out, inputs["common_offset"], inputs["elder_delta"], 7)
