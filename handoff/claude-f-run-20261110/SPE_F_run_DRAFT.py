#!/usr/bin/env python3
"""SPE F施策 実行スクリプト(DRAFT・非正式・作業用)

目的: v6エンジン関数(spe-flatvat/spe の engine/prototype.py, engine/m14_wage_anchor.py)を使い、
      入力ファイル SPE_F_inputs_DRAFT.json の条件で F施策を年次実行し、年ごとの値と要約を表示する。

使い方:
  python3 SPE_F_run_DRAFT.py <engineディレクトリ> [入力JSON] [--csv 出力CSV]
  例: python3 SPE_F_run_DRAFT.py ./spe/engine SPE_F_inputs_DRAFT.json --csv F_result.csv

前提:
  - Python 3.8 以上。外部ライブラリ不要。
  - engine は GitHub spe-flatvat/spe の commit a40f070e (または同じ内容のもの)。このスクリプトは書込みをしない。
  - 入力JSONの値のタグ(v5/v6/推定/近似/仮定)を確認すること。「仮定」は仕様に値がなく作成者が置いたもの。

出力に含まれるもの: 入力JSONとこのスクリプトのSHA-256、年次表、要約、v5 §8 との比較。
"""
import sys, json, hashlib, csv
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pw(table, t):
    """区間表 [{from,value}...] から年tの値を返す(from が t 以下の最後の行)。"""
    v = None
    for row in table:
        if t >= row["from"]:
            v = row["value"]
    return v


def risk_pct(rules, t):
    s = 0.0
    for r in rules:
        if r["type"] == "once" and t == r["year"]:
            s += r["pct"]
        elif r["type"] == "every" and t >= r["start"] and (t - r["start"]) % r["step"] == 0:
            s += r["pct"]
    return s


def migration(m, t):
    if t < m["ramp_start"]:
        return 0
    if t >= m["ramp_start"] + m["ramp_years"]:
        return m["steady_per_year"]
    return m["steady_per_year"] * (t - m["ramp_start"] + 1) / m["ramp_years"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    csv_out = sys.argv[sys.argv.index("--csv") + 1] if "--csv" in sys.argv else None
    if csv_out in args:
        args.remove(csv_out)
    if not args:
        print(__doc__)
        sys.exit(1)
    engine = Path(args[0])
    inp = Path(args[1]) if len(args) > 1 else Path(__file__).with_name("SPE_F_inputs_DRAFT.json")
    sys.path.insert(0, str(engine))
    from prototype import SimulationState, transition_year, transition_year_demographics
    from m14_wage_anchor import wage_growth_rate

    c = json.loads(inp.read_text(encoding="utf-8"))
    s0 = c["initial_state_2025_end"]
    first = 2026 if c["include_2026"] else 2027
    end = c["end_year"]
    alpha, phi = c["alpha"]["value"], c["phi"]["value"]
    anchors = {int(k): float(v) for k, v in c["wage_anchor_man_yen"]["anchors"].items()}
    st = SimulationState(year=first - 1, real_gdp=s0["real_gdp"], nominal_gdp=s0["nominal_gdp"],
                         tax_revenue=s0["tax_revenue"], expenditure=s0["expenditure"],
                         population=s0["population"], deaths=s0["deaths"], births=s0["births"])
    rows, max_ratio = [], 0.0
    for t in range(first, end + 1):
        wg = 0.0 if t == first and t == min(anchors) else wage_growth_rate(anchors, t)
        wage = anchors[min(anchors)] * (anchors[max(anchors)] / anchors[min(anchors)]) ** ((t - min(anchors)) / (max(anchors) - min(anchors)))
        mig = migration(c["migration"], t)
        dem = transition_year_demographics(previous_state=st, death_rate_coefficient=c["death_rate_coefficient"]["value"],
                                           birth_decline_coefficient=c["birth_decline_coefficient"]["value"], phi=phi,
                                           real_wage_growth_rate=wg, net_migration=mig)
        pg = dem.population / st.population - 1
        pe = c["policy_effects_pct"]
        r = transition_year(st, death_rate_coefficient=c["death_rate_coefficient"]["value"],
                            birth_decline_coefficient=c["birth_decline_coefficient"]["value"], phi=phi,
                            real_wage_growth_rate=wg, net_migration=mig, total_population_growth_rate=pg,
                            aging_drag=pw(c["aging_drag_pp"]["table"], t) / 100,
                            base_growth_rate=c["base_growth_rate_pct"]["value"] / 100,
                            consumption_stimulus_effect=pw(pe["consumption_stimulus"], t) / 100,
                            investment_promotion_effect=pw(pe["investment_promotion"], t) / 100,
                            education_effect=pw(pe["education"], t) / 100,
                            risk_shock=risk_pct(c["risk_shock_pct"]["rules"], t) / 100, alpha=alpha,
                            base_inflation_rate=c["base_inflation_rate_pct"]["value"] / 100,
                            risk_event_inflation_impact=c["inflation_extra_pp"]["by_year"].get(str(t), 0.0) / 100,
                            consumption_tax_transitional_factor=0.0,
                            tax_elasticity=pw(c["tax_elasticity"]["table"], t))
        real = st.real_gdp * (1 + r.real_gdp_growth_rate)
        nom = st.nominal_gdp * (1 + r.nominal_gdp_growth_rate)
        tax = r.tax_revenue_before_cap * c["tax_factor_by_year"].get(str(t), 1.0)
        tax = min(tax, nom * c["tax_cap_ratio_of_nominal_gdp"]["value"])
        exp = st.expenditure * (1 + pw(c["expenditure_growth_pct"]["table"], t) / 100)
        st = SimulationState(year=t, real_gdp=real, nominal_gdp=nom, tax_revenue=tax, expenditure=exp,
                             population=dem.population, deaths=dem.deaths, births=dem.births)
        max_ratio = max(max_ratio, tax / nom)
        rows.append([t, round(real, 2), round(nom, 2), round(tax, 2), round(exp, 2), round(max(exp - tax, 0), 2),
                     round(dem.population / 1e4, 1), round(wage, 1), round(tax / nom * 100, 2),
                     round(r.real_gdp_growth_rate * 100, 2)])
    head = ["year", "real_gdp", "nominal_gdp", "tax", "expenditure", "jgb_issue", "population_man", "wage_man_yen(anchor)", "tax_to_gdp_pct", "real_growth_pct"]
    n = end - first + 1
    last = rows[-1]
    print("SPE F施策 実行結果(DRAFT・非正式)")
    print(f"入力JSON: {inp.name} SHA-256 {sha(inp)}")
    print(f"スクリプト: {Path(__file__).name} SHA-256 {sha(__file__)}")
    print(f"engine: {engine} (prototype.py SHA-256 {sha(engine / 'prototype.py')[:16]}…)")
    print(f"期間: {first}〜{end} ({n}期間)  2026年を含める: {c['include_2026']}")
    print("\t".join(head))
    for row in rows:
        print("\t".join(str(x) for x in row))
    cagr = ((last[1] / s0["real_gdp"]) ** (1 / n) - 1) * 100
    print(f"\n要約: 実質GDP {last[1]} 兆円 / CAGR {cagr:+.2f}% / 人口 {last[6]:.0f} 万人 / 税収GDP比最大 {max_ratio * 100:.1f}% / {end}年国債発行 {last[5]}")
    ref = c.get("reference_v5_section8", {})
    if ref:
        print(f"v5 §8 参考: {ref['real_gdp']} 兆円 / {ref['cagr_pct']:+.2f}% / {ref['population_man']} 万人 / {ref['tax_to_gdp_max_pct']}% / {ref['bonds_2055']}")
    if csv_out:
        with open(csv_out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows(rows)
        print(f"CSV: {csv_out}")


if __name__ == "__main__":
    main()
