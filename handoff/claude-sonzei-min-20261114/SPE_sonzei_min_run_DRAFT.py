#!/usr/bin/env python3
"""SPE 損税モジュール 最小試作 (DRAFT / PROVISIONAL / NON-CANONICAL / DIAGNOSTIC ONLY)

engine には接続しない(案3: 既存マクロ効果とは別表示)。入力は SPE_sonzei_min_inputs_DRAFT.json。
定義(部門 s, 年 t, 単位=兆円):
  R=非課税売上, P=課税仕入・設備投資(税抜)=p_ratio*R, tau=税率, kappa=仕入税額控除の実現率
  現行制度(StatusQuo): 損税 L_SQ = tau0*P
  F・開始前          : 損税 L_F  = tau_F*P            (税率低下のみの効果)
  F・開始後          : 損税 L_F  = (1-kappa)*tau_F*P  (残存)
  部門に帰属する国庫収入(上流で徴収された埋込税を含む):
    開始前 tau*P / 開始後 tau*R + (1-kappa)*tau*P
  課税ベース拡大効果 dT_base = (開始後) tau_F*R - kappa*tau_F*P   (同一税率で未開始とした場合との差)
  税率効果 dT_rate = (tau_F - tau0)*P (開始前のみ。マクロ側の減税と重複しうるため別掲)
  帰着: 公費補填 phi*tau_F*R, 消費者負担 (1-phi)*tau_F*R, 事業者残存利益 (1-theta)*kappa*tau_F*P
使い方: python3 SPE_sonzei_min_run_DRAFT.py inputs.json outdir
"""
import json, sys, os, csv, copy

def interp(points, year):
    ks = sorted(int(k) for k in points)
    if year <= ks[0]:
        return points[str(ks[0])]
    for a, b in zip(ks, ks[1:]):
        if a <= year <= b:
            fa, fb = points[str(a)], points[str(b)]
            return fa + (fb - fa) * (year - a) / (b - a)
    return points[str(ks[-1])]

def v(x):
    return x["value"] if isinstance(x, dict) and "value" in x else x

def run(cfg, p_mult=1.0, kappa=None, starts=None, phi_med=None):
    y0, y1 = cfg["years"]["start"], cfg["years"]["end"]
    g = v(cfg["nominal_growth_pct"]) / 100.0
    t0 = v(cfg["tau_statusquo_pct"]) / 100.0
    kap = v(cfg["kappa_realization"]) if kappa is None else kappa
    rows = []
    for t in range(y0, y1 + 1):
        tauF = interp(cfg["tau_F_path_pct"]["points"], t) / 100.0
        for key, s in cfg["sectors"].items():
            R = v(s["R_2025"]) * (1 + g) ** (t - 2025)
            P = v(s["p_ratio"]) * p_mult * R
            st = (starts or {}).get(key, v(s["start_year"]))
            phi = v(s["phi_public"])
            if key == "medical" and phi_med is not None:
                phi = phi_med
            th = v(s["theta_passthrough"])
            started = t >= st
            L_sq = t0 * P
            if started:
                L_f = (1 - kap) * tauF * P
                dT_base = tauF * R - kap * tauF * P
                dT_rate = 0.0
                gross_out = tauF * R
                credit = kap * tauF * P
                public = phi * gross_out
                consumer = (1 - phi) * gross_out
                biz_keep = (1 - th) * kap * tauF * P
            else:
                L_f = tauF * P
                dT_base = 0.0
                dT_rate = (tauF - t0) * P
                gross_out = credit = public = consumer = biz_keep = 0.0
            rows.append(dict(year=t, sector=key, started=int(started), tau_F=tauF, R=R, P=P,
                             L_statusquo=L_sq, L_F=L_f, L_reduction=L_sq - L_f,
                             L_reduction_rate_part=(L_sq - tauF * P),
                             L_reduction_base_part=(tauF * P - L_f),
                             dT_base=dT_base, dT_rate=dT_rate, output_tax_gross=gross_out,
                             input_credit=credit, public_compensation=public,
                             dT_base_net_of_public=dT_base - public,
                             consumer_burden=consumer, business_retained=biz_keep))
    return rows

def totals(rows, upto=None):
    keys = ["L_statusquo", "L_F", "L_reduction", "L_reduction_rate_part", "L_reduction_base_part",
            "dT_base", "dT_rate", "output_tax_gross", "input_credit", "public_compensation",
            "dT_base_net_of_public", "consumer_burden", "business_retained"]
    out = {}
    for r in rows:
        if upto and r["year"] > upto:
            continue
        for k in keys:
            out[(r["sector"], k)] = out.get((r["sector"], k), 0.0) + r[k]
            out[("ALL", k)] = out.get(("ALL", k), 0.0) + r[k]
    return out

def selfcheck(cfg):
    # 恒等式・境界条件の検算
    rows = run(cfg)
    for r in rows:
        assert abs(r["L_reduction"] - (r["L_reduction_rate_part"] + r["L_reduction_base_part"])) < 1e-9
        if not r["started"]:
            assert r["dT_base"] == 0 and r["output_tax_gross"] == 0
        else:
            assert abs(r["dT_base"] - (r["output_tax_gross"] - r["input_credit"])) < 1e-9
            assert abs(r["public_compensation"] + r["consumer_burden"] - r["output_tax_gross"]) < 1e-9
    # kappa=0: 損税は解消されず、base_part=0、ΔT_base=課税売上税額
    for r in run(cfg, kappa=0.0):
        if r["started"]:
            assert abs(r["L_reduction_base_part"]) < 1e-9 and abs(r["dT_base"] - r["output_tax_gross"]) < 1e-9
    # 税率を現行と同一(tauF=tau0)にすれば rate_part=0
    c2 = copy.deepcopy(cfg)
    c2["tau_F_path_pct"]["points"] = {"2026": 10.0, "2055": 10.0}
    assert all(abs(r["L_reduction_rate_part"]) < 1e-9 for r in run(c2))
    # 開始年を2100にすれば base 効果ゼロ
    assert all(r["dT_base"] == 0 for r in run(cfg, starts={"medical": 2100, "education": 2100, "rental": 2100}))
    return True

def main(inp, outdir):
    cfg = json.load(open(inp, encoding="utf-8"))
    selfcheck(cfg)
    os.makedirs(outdir, exist_ok=True)
    base = run(cfg)
    with open(os.path.join(outdir, "base_yearly.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(base[0].keys()))
        w.writeheader()
        w.writerows(base)
    sens = cfg["sensitivity"]
    cases = []
    for pm in sens["p_multiplier"]:
        for tn, tv in [("staggered", None), ("all_2038", sens["timing"]["all_2038"]), ("all_2034", sens["timing"]["all_2034"])]:
            for kp in sens["kappa"]:
                cases.append(dict(p_mult=pm, timing=tn, kappa=kp, phi_med=None, starts=tv))
    for ph in sens["phi_medical"]:
        cases.append(dict(p_mult=1.0, timing="staggered", kappa=v(cfg["kappa_realization"]), phi_med=ph, starts=None))
    summary = []
    for c in cases:
        rows = run(cfg, p_mult=c["p_mult"], kappa=c["kappa"], starts=c["starts"], phi_med=c["phi_med"])
        t38 = totals(rows, 2038)
        t55 = totals(rows)
        r2040 = [r for r in rows if r["year"] == 2040]
        s40 = {k: sum(r[k] for r in r2040) for k in ["L_statusquo", "L_F", "L_reduction", "dT_base", "dT_base_net_of_public", "business_retained"]}
        summary.append(dict(case={k: c[k] for k in ["p_mult", "timing", "kappa", "phi_med"]},
                            y2040=s40,
                            cum_to_2038={k: t38[("ALL", k)] for k in ["L_reduction", "dT_base", "dT_rate", "dT_base_net_of_public"]},
                            cum_to_2055={k: t55[("ALL", k)] for k in ["L_reduction", "dT_base", "dT_rate", "dT_base_net_of_public", "public_compensation", "consumer_burden", "business_retained"]}))
    with open(os.path.join(outdir, "sensitivity_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    # 基準ケースの年次抜粋(全部門合算)
    pick = [2026, 2027, 2028, 2030, 2034, 2036, 2037, 2038, 2040, 2045, 2050, 2055]
    lines = []
    for y in pick:
        rs = [r for r in base if r["year"] == y]
        f = lambda k: sum(r[k] for r in rs)
        lines.append((y, rs[0]["tau_F"] * 100, f("L_statusquo"), f("L_F"), f("L_reduction"), f("dT_base"), f("dT_rate"), f("dT_base_net_of_public"), f("business_retained")))
    with open(os.path.join(outdir, "base_excerpt.json"), "w") as fh:
        json.dump(lines, fh)
    print("selfcheck OK; cases:", len(cases))
    print("year tauF% L_SQ L_F Lred dT_base dT_rate dT_net_pub biz_keep")
    for l in lines:
        print(l[0], "%.1f" % l[1], " ".join("%.2f" % x for x in l[2:]))
    print("-- sensitivity (cum to 2055 of L_reduction / dT_base_net_of_public; 2040 L_reduction)")
    for s in summary:
        print(s["case"], "L_red55=%.1f" % s["cum_to_2055"]["L_reduction"], "dTbase55=%.1f" % s["cum_to_2055"]["dT_base"], "dTnetpub55=%.1f" % s["cum_to_2055"]["dT_base_net_of_public"], "L_red2040=%.2f" % s["y2040"]["L_reduction"])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
