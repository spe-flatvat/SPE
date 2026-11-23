"""Isolated F replay with the Annex §1C exemption-threshold sensitivity."""
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True
root, prior, out = (Path(arg).resolve() for arg in sys.argv[1:4])
name = sys.argv[4]
inputs = json.loads(Path(__file__).with_name("Inputs.json").read_text())
case = inputs["cases"][name]
bands = inputs["illustrative_residual_bands"]
cutoff = inputs["new_threshold_sales_man"]
eligible_base = sum(band["net_tax_inclusive_base_2026_trn"] for band in bands
                    if band["sales_man"] > cutoff)
manifest = (prior / "Runtime_Sources.json").read_bytes()
dependencies = json.loads(Path(__file__).with_name("Dependencies.json").read_text())
expected = next(row for row in dependencies if row["local"] == "prior/Runtime_Sources.json")
assert (len(manifest), hashlib.sha256(manifest).hexdigest()) == (expected["size"], expected["sha256"])
for row in json.loads(manifest):
    data = (root / row["path"]).read_bytes()
    assert (len(data), hashlib.sha256(data).hexdigest()) == (row["size"], row["sha256"]), row["path"]

source = root / "Prior_Worker.py"
program = source.read_text()
# Modify only the prior worker's injected source in memory.
needle = "   (out/'Resolved_F_Cohort_Runtime.py.txt').write_text(source)"
replacement = """   for old, new in coverage_replacements.items():
    assert source.count(old)==1, old
    source=source.replace(old,new)
""" + needle
assert program.count(needle) == 1
worker = ModuleType("coverage_worker")
worker.coverage_replacements = {
    "        refund=None": """        threshold_vat=_threshold(y, p, coreN, halt, omit)
        f['direct_tax']+=threshold_vat
        refund=None""",
    "admin_firm=value(admin_saving)": "admin_firm=-threshold_vat+value(admin_saving)",
}
exec(compile(program.replace(needle, replacement), str(source), "exec"), worker.__dict__)

accounts = {}

def threshold(year, p, nominal, halt, omit):
    active = case["enabled"] and year >= p["admin_start"] and not halt and "tax" not in omit
    rate = .10 if year < p["year8"] else .08 if year < p["year5"] else .05
    pool = eligible_base * case["residual_base_scale"] * nominal / inputs["reference_nominal_gdp_trn"] if active else 0.
    vat = pool * rate / (1 + rate)
    accounts[year] = dict(threshold_active=int(active), threshold_start=p["admin_start"],
                          threshold_man=cutoff if active else None,
                          threshold_rate=rate, threshold_residual_base_trn=pool,
                          threshold_incremental_vat_trn=vat, threshold_seller_cash_trn=-vat,
                          threshold_investment_target_trn=-vat*p["firm_investment_response"])
    return vat

original_mod = worker.mod

def mod(module_name, path):
    model = original_mod(module_name, path)
    if module_name != "isolated_F_model":
        return model
    original_patch, original_load = model.patch, model.load

    def patch(engine, policy, medical, settings):
        ns = original_patch(engine, policy, medical, settings)
        if policy == "F":
            ns["run_path"].__globals__["_threshold"] = threshold
        return ns

    def load(config):
        result = original_load(config)
        integ, vat_inputs = result[3], result[5]
        national = vat_inputs["reference"]["national_share"]
        original_fiscal = integ.fiscal

        def fiscal(row, macro, base, index, config):
            account = accounts[row["year"]]
            extra = account["threshold_incremental_vat_trn"]
            for key in ("modeled_VAT_trn", "VAT_delta_vs_fixed_reference_trn", "VAT_F_minus_current_SQ_trn"):
                row[key] += extra
            row["VAT_national_reference_trn"] += extra*national
            row["VAT_local_reference_trn"] += extra*(1-national)
            for key, fraction in (("VAT_delta_national_reference_trn", national),
                                  ("VAT_delta_local_reference_trn", 1-national)):
                row[key] += extra*fraction
            # Preserve the underlying covered-market C and windfall-fund inputs.
            row.update(account, corporate_cash_flow_proxy_trn=macro["corporate_cash_change"])
            return original_fiscal(row, macro, base, index, config)

        integ.fiscal = fiscal
        return result

    model.patch, model.load = patch, load
    return model

worker.mod = mod
connection = root / "handoff/chatgpt-f-policy-cohort-fte-20261123/ANNUAL_FINE_WEEK_HOURS/Connection_Inputs.json"
offsets = json.loads(connection.read_text())
out.mkdir(parents=True, exist_ok=True)
worker.f(root, out, offsets["common_offset"], offsets["elder_delta"], 7)
