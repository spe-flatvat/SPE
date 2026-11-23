"""Replay the pinned F baseline and capture the synthetic household cells."""
import hashlib
import json
from pathlib import Path

def load(path):
    return json.loads(path.read_bytes())

def replay(runtime, prior, out):
    import sys
    from types import ModuleType

    sys.dont_write_bytecode = True
    runtime, prior, out = (p.resolve() for p in (runtime, prior, out))
    manifest = (prior/"Runtime_Sources.json").read_bytes()
    dependency = next(r for r in load(Path(__file__).with_name("Dependencies.json"))
                      if r["local"] == "prior/Runtime_Sources.json")
    assert (len(manifest), hashlib.sha256(manifest).hexdigest()) == (dependency["size"], dependency["sha256"])
    for entry in json.loads(manifest):
        data = (runtime/entry["path"]).read_bytes()
        assert (len(data), hashlib.sha256(data).hexdigest()) == (entry["size"], entry["sha256"]), entry["path"]
    worker = ModuleType("fixed_worker")
    source = runtime/"Prior_Worker.py"
    exec(compile(source.read_bytes(), str(source), "exec"), worker.__dict__)
    original_mod = worker.mod
    cells = {}

    def mod(name, path):
        model = original_mod(name, path)
        if name != "isolated_F_model":
            return model
        original_load = model.load

        def model_load(*args):
            result = original_load(*args)
            vat = result[4]
            original_dependencies = vat.load_dependencies

            def dependencies(*args):
                loaded = original_dependencies(*args)
                household = loaded[1]
                original_accounts = household["annual_accounts"]

                def accounts(*args, **kwargs):
                    ledger, grid = original_accounts(*args, **kwargs)
                    year = ledger["year"]
                    assert year not in cells
                    cells[year] = grid
                    return ledger, grid

                household["annual_accounts"] = accounts
                return loaded

            vat.load_dependencies = dependencies
            return result

        model.load = model_load
        return model

    worker.mod = mod
    connection = load(runtime/"handoff/chatgpt-f-policy-cohort-fte-20261123/ANNUAL_FINE_WEEK_HOURS/Connection_Inputs.json")
    out.mkdir(parents=True, exist_ok=True)
    worker.f(runtime, out, connection["common_offset"], connection["elder_delta"], 7)
    worker.save(out/"Household_Cells.json", cells)

if __name__ == "__main__":
    import sys
    replay(*map(Path, sys.argv[1:]))
