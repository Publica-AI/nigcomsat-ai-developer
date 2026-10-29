"""Week 6 · Day 1: Backtesting: Test It on the Past First."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from common import BRAND as B
from svgcharts import lines_svg
from webdeck import logos_title_block
from w6forecast import (BACKTEST_CODE, BASELINE_CODE, FEATURE_CODE, H, X_COLS, facts, load, make_features, mae,
                        rate_seasonal_naive, walk_forward_mae)

CODE = "W6D1"
TITLE = "Backtesting: Test It on the Past First"

GRID, AXIS = "#24384F", "#9DB0C6"
RED, GOLD, GREEN = "#FF6B6F", "#F5B83D", "#3CCB7F"
METHODS = {"regression": ("📈 Regression (1 week ahead)", B["blue_d"]),
           "naive": ("👵🏾 Naive (1 week ahead)", GOLD),
           "seasonal_naive": ("📅 Seasonal naive", AXIS),
           "rate_seasonal_naive": ("🧮 Rate seasonal naive (blind 4 weeks)", B["teal_d"])}


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


def d(t):
    return f"{pd.Timestamp(t).day} {pd.Timestamp(t):%b}"


# =============================================================================
# EXTRA NUMBERS FOR TODAY (same shared functions, so same code as the notebook)
# =============================================================================
@lru_cache(maxsize=1)
def day_facts():
    F = facts()
    tickets = load()[0]
    y, term = tickets["tickets_raised"], tickets["active_vsat_terminals"]
    fa = make_features(tickets)
    n = len(fa)
    cuts = list(range(int(n * 0.5), n - 4, 4))
    D = {"feat_start": fa.index[0], "feat_end": fa.index[-1], "n_feat": n, "cuts": cuts,
         "fold_ranges": [(fa.index[c], fa.index[c + 3], c) for c in cuts]}
    # the regression's one-step forecasts inside each fold (for the chart)
    pred = pd.Series(np.nan, index=fa.index)
    for c in cuts:
        m = LinearRegression().fit(fa[X_COLS].iloc[:c], fa["target"].iloc[:c])
        pred.iloc[c:c + 4] = m.predict(fa[X_COLS].iloc[c:c + 4])
    D["fold_pred"] = pred
    D["target"] = fa["target"]
    folds = F["folds"]
    D["rate_beats_reg"] = int((folds["rate_seasonal_naive"] < folds["regression"]).sum())
    D["spread_ratio"] = float(folds["regression"].max() / folds["regression"].min())
    D["reg_only_win"] = [t for t in folds.index if folds.loc[t, "regression"] < folds.loc[t, "naive"]]
    D["nov3_step"] = int(y.diff().loc["2025-11-03"])
    D["oct27"], D["nov3"] = int(y.loc["2025-10-27"]), int(y.loc["2025-11-03"])
    # 🌶️ refit every week: walk_forward_mae with step=1, h=1, compared on the same weeks
    wk = walk_forward_mae(tickets, make_features, X_COLS, step=1, h=1)
    weeks = fa.index[int(n * 0.5): int(n * 0.5) + len(wk)]
    nv = (fa.loc[weeks, "tickets_lag1"] - fa.loc[weeks, "target"]).abs().values
    rt = F["horizons"][1]["table"].loc[weeks, "rate_seasonal_naive"].values
    D["weekly"] = {"n": len(wk), "from": weeks[0], "to": weeks[-1], "reg": float(wk.mean()), "naive": float(nv.mean()),
                   "rate": float(rt.mean()), "reg_wins": int((wk < nv).sum()), "naive_wins": int((nv < wk).sum())}
    for h, v in F["horizons"].items():
        D[f"origins_{h}"] = (v["table"].index[0], v["table"].index[-1], v["n"])
    D["h8"] = F["horizons"][8]["table"]
    D["h8_naive_max"] = float(D["h8"]["naive"].max())
    D["h8_rate_max"] = float(D["h8"]["rate_seasonal_naive"].max())
    return D


# =============================================================================
# LOCAL SVG HELPERS
# =============================================================================
def hbars_svg(rows, total, w=1420, label_w=470):
    """rows: [(label, value, colour)] as horizontal bars out of `total`."""
    L, R, rh = label_w, w - 140, 62
    h = len(rows) * rh + 10
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for k, (lab, v, col) in enumerate(rows):
        y = k * rh + 8
        bw = max(v / total * (R - L), 3)
        dl = .3 + k * .22
        o.append(f'<g class="anim a-left" style="--d:{dl:.2f}s"><text x="0" y="{y + 32}" fill="#EAF2FB" font-size="23" font-weight="700">{lab}</text>'
                 f'<rect x="{L}" y="{y + 6}" width="{R - L}" height="38" rx="8" fill="#12233A"/>'
                 f'<rect x="{L}" y="{y + 6}" width="{bw:.1f}" height="38" rx="8" fill="{col}"/>'
                 f'<text x="{L + bw + 14:.1f}" y="{y + 34}" fill="{col}" font-size="26" font-weight="800">{v:.2f}</text></g>')
    o.append("</svg>")
    return "".join(o)


def walkforward_svg(F, D, w=1420):
    """The code book's 6 folds: training grows forwards, the 4-week test block slides, one MAE per fold."""
    t0, t1 = D["feat_start"], D["feat_end"]
    L, R = 150, 1030
    span = (t1 - t0).days

    def X(t):
        return L + (pd.Timestamp(t) - t0).days / span * (R - L)
    folds = F["folds"]
    worst = folds["regression"].idxmax()
    rh, top = 66, 70
    h = top + 6 * rh + 74
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">',
         f'<text x="{L}" y="30" fill="{AXIS}" font-size="20" font-weight="700">🟦 train on everything before the cut (refit)  ·  🟩 forecast + score the next 4 weeks</text>',
         f'<text x="1300" y="30" fill="#EAF2FB" font-size="22" font-weight="800" text-anchor="middle">📈 regression MAE</text>']
    for k, (s0, s1, c) in enumerate(D["fold_ranges"]):
        y = top + k * rh
        dl = .3 + k * .4
        v = folds.loc[s0, "regression"]
        col = RED if s0 == worst else (GREEN if v == folds["regression"].min() else "#EAF2FB")
        o.append(f'<g class="anim a-left" style="--d:{dl:.2f}s">')
        o.append(f'<text x="0" y="{y + 31}" fill="#EAF2FB" font-size="22" font-weight="800">Fold {k + 1}</text>')
        o.append(f'<rect x="{L}" y="{y + 6}" width="{R - L}" height="36" rx="8" fill="#12233A"/>')
        o.append(f'<rect x="{X(t0):.1f}" y="{y + 6}" width="{X(s0) - X(t0) - 3:.1f}" height="36" rx="8" fill="{B["blue_d"]}"/>')
        o.append(f'<text x="{X(t0) + 14:.1f}" y="{y + 31}" fill="#fff" font-size="17" font-weight="700">{c} weeks</text>')
        o.append(f'<rect x="{X(s0):.1f}" y="{y + 6}" width="{X(s1 + pd.Timedelta("7D")) - X(s0):.1f}" height="36" rx="8" fill="{B["teal_d"]}"/>')
        o.append(f'<text x="{X(s1) + 30:.1f}" y="{y + 31}" fill="{AXIS}" font-size="17" font-weight="700">{d(s0)} – {d(s1)}</text>')
        o.append(f'<text x="1320" y="{y + 36}" fill="{col}" font-size="36" font-weight="800" text-anchor="middle">{v:.2f}</text>')
        o.append("</g>")
    # the season step
    xs = X("2025-11-03")
    o.append(f'<line class="anim a-fade" style="--d:3s" x1="{xs:.1f}" x2="{xs:.1f}" y1="{top}" y2="{top + 6 * rh}" stroke="{RED}" stroke-width="3" stroke-dasharray="8 6"/>')
    o.append(f'<text class="anim a-fade" style="--d:3.1s" x="{xs:.1f}" y="{top + 6 * rh + 62}" fill="{RED}" font-size="20" font-weight="800" text-anchor="middle">'
             f'3 Nov: rains end, {str(D["nov3_step"]).replace("-", "−")} tickets in one week</text>')
    for m in (1, 3, 5, 7, 9):
        xm = X(pd.Timestamp(2025, m, 1))
        o.append(f'<text x="{xm:.1f}" y="{top + 6 * rh + 30}" fill="{AXIS}" font-size="18" text-anchor="middle">{pd.Timestamp(2025, m, 1):%b}</text>')
    o.append("</svg>")
    return "".join(o)


def foldline_svg(F, D, w=1400, h=440):
    """Second-year tickets with the 6 fold blocks, and the regression's one-step forecasts inside them."""
    tgt, pred = D["target"], D["fold_pred"]
    idx = tgt.index
    bands = []
    worst = F["folds"]["regression"].idxmax()
    for k, (s0, s1, c) in enumerate(D["fold_ranges"]):
        col = RED if s0 == worst else B["teal_d"]
        bands.append((c - .5, c + 3.5, col, .14 if s0 != worst else .22, f"{k + 1}"))
    xl = [(i, f"{t:%b}") for i, t in enumerate(idx) if t.day <= 7 and t.month in (1, 3, 5, 7, 9, 11)]
    i3 = idx.get_loc(pd.Timestamp("2025-11-03"))
    return lines_svg([dict(values=tgt.values, color="#EAF2FB", stroke=3.4, label="actual", dur="2.4s"),
                      dict(values=pred.values, color=B["blue_d"], stroke=3, dash="9 7", label="forecast", delay="1.6s")],
                     w=w, h=h, ymin=40, ymax=85, xlabels=xl, yticks=[(45, "45"), (60, "60"), (75, "75")], bands=bands,
                     markers=[(i3, float(tgt.iloc[i3]), f"3 Nov: {D['oct27']} → {D['nov3']}", RED)])


def horizon_svg(F, w=1400, h=470):
    """Mean MAE against how many weeks ahead, for the blind baselines."""
    hz = F["horizons"]
    xs = {1: 0.0, 4: 0.5, 8: 1.0}
    L, R, T, Bm = 110, w - 380, 30, h - 70
    lo, hi = 0, 9

    def X(k):
        return L + xs[k] * (R - L)

    def Y(v):
        return Bm - (v - lo) / (hi - lo) * (Bm - T)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for v in (0, 2, 4, 6, 8):
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}"/>'
                 f'<text x="{L - 16}" y="{Y(v) + 7:.1f}" fill="{AXIS}" font-size="20" text-anchor="end">{v}</text>')
    for k in (1, 4, 8):
        o.append(f'<text x="{X(k):.1f}" y="{h - 30}" fill="{AXIS}" font-size="22" font-weight="700" text-anchor="middle">'
                 f'{k} week{"s" if k > 1 else ""} ahead</text>')
    lines = [("moving_average", "moving average", "#7E8FA6", 3), ("exp_smoothing", "exp. smoothing", B["blue_d"], 3),
             ("naive", "👵🏾 naive", GOLD, 5), ("rate_seasonal_naive", "🧮 rate seasonal naive", GREEN, 5)]
    for j, (key, lab, col, sw) in enumerate(lines):
        pts = [(X(k), Y(hz[k]["mean"][key])) for k in (1, 4, 8)]
        dp = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        dl = .3 + j * .5
        o.append(f'<path class="draw" style="--d:{dl:.1f}s;--dur:1.4s" d="{dp}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
        for (x, yy), k in zip(pts, (1, 4, 8)):
            o.append(f'<circle class="anim a-pop" style="--d:{dl + 1.2:.1f}s;transform-origin:{x:.0f}px {yy:.0f}px" cx="{x:.1f}" cy="{yy:.1f}" r="9" fill="{col}"/>')
            if key in ("naive", "rate_seasonal_naive"):
                above = (key == "naive") != (k == 1)          # at 1 week naive sits BELOW the rate forecast
                dy, dx, anc = (-18 if above else 36), (22 if k == 1 else 0), ("start" if k == 1 else "middle")
                o.append(f'<text class="anim a-fade" style="--d:{dl + 1.3:.1f}s" x="{x + dx:.1f}" y="{yy + dy:.1f}" fill="{col}" font-size="23" '
                         f'font-weight="800" text-anchor="{anc}">{hz[k]["mean"][key]:.2f}</text>')
        o.append(f'<text class="anim a-fade" style="--d:{dl + 1.3:.1f}s" x="{R + 22}" y="{pts[-1][1] + 8:.1f}" fill="{col}" font-size="23" font-weight="800">{lab}</text>')
    o.append("</svg>")
    return "".join(o)


def origin_svg(w=1420, h=330):
    """Illustration: at each origin, use only the past (blue), forecast h weeks blind, then step one week on."""
    cell, gap, x0, n = 26, 6, 250, 36
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for j, (start, hz, col) in enumerate(((12, 1, GOLD), (16, 4, B["teal_d"]), (20, 8, GREEN))):
        y = 20 + j * 92
        dl = .3 + j * .8
        o.append(f'<g class="anim a-left" style="--d:{dl:.1f}s">'
                 f'<text x="0" y="{y + 30}" fill="{col}" font-size="23" font-weight="800">{hz} week{"s" if hz > 1 else ""} ahead</text>')
        for i in range(n):
            x = x0 + i * (cell + gap)
            fill = B["blue_d"] if i < start else (col if i < start + hz else "#1C3150")
            o.append(f'<rect x="{x}" y="{y + 4}" width="{cell}" height="40" rx="5" fill="{fill}"/>')
        xs = x0 + start * (cell + gap) - gap / 2
        o.append(f'<path d="M{xs:.1f} {y - 6} L{xs:.1f} {y + 54}" stroke="#EAF2FB" stroke-width="4"/>')
        o.append(f'<text x="{xs + 10:.1f}" y="{y + 70}" fill="#EAF2FB" font-size="17" font-weight="700">🧍🏾 origin</text></g>')
    o.append(f'<text x="{x0}" y="{h - 6}" fill="{AXIS}" font-size="20">🟦 the past it may use · coloured = the weeks it forecasts blind · then step ONE week on, all year</text>')
    o.append("</svg>")
    return "".join(o)


def h8_line_svg(F, D, w=1400, h=420):
    """MAE of each 8-week forecast, one point per origin: naive spikes at season changes, the rate forecast doesn't."""
    t = D["h8"]
    idx = t.index
    xl = [(i, f"{x:%b}") for i, x in enumerate(idx) if x.day <= 7 and x.month in (1, 3, 5, 7, 9, 11)]
    return lines_svg([dict(values=t["naive"].values, color=GOLD, stroke=3.6, label="naive"),
                      dict(values=t["rate_seasonal_naive"].values, color=GREEN, stroke=3.6, label="rate", delay="1.4s")],
                     w=w, h=h, ymin=0, ymax=20, xlabels=xl, yticks=[(0, "0"), (5, "5"), (10, "10"), (15, "15"), (20, "20")])


TABLE_CSS = ("<style>.sb{width:100%;border-collapse:separate;border-spacing:0 6px;font-size:23px}"
             ".sb th{color:#9DB0C6;font-size:18px;text-align:left;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:0 14px}"
             ".sb td{background:#12233A;padding:9px 14px}.sb td:first-child{border-radius:14px 0 0 14px}"
             ".sb td:last-child{border-radius:0 14px 14px 0}.sb tr.win td{background:#123A33}.sb td.best{color:#3CCB7F;font-weight:800}"
             ".sb td.worst{color:#FF6B6F;font-weight:800}.sb tr.badrow td{background:#3A1E26}</style>")


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    F = facts()
    D = day_facts()
    folds = F["folds"]
    fm = F["fold_means"]
    hz = F["horizons"]
    bm = F["baseline_mae"]
    reg = folds["regression"]
    worst = F["worst_fold"]
    wk = D["weekly"]
    o1, o4, o8 = D["origins_1"], D["origins_4"], D["origins_8"]
    h8m = hz[8]["mean"]
    order8 = sorted(h8m, key=h8m.get)

    # the fold table
    cols = ["regression", "naive", "seasonal_naive", "rate_seasonal_naive"]
    trs = ""
    for k, (s0, s1, c) in enumerate(D["fold_ranges"]):
        best = min(cols, key=lambda m: folds.loc[s0, m])
        cells = "".join(f'<td class="mono{" best" if m == best else ""}">{folds.loc[s0, m]:.2f}</td>' for m in cols)
        trs += (f'<tr class="anim a-left{" badrow" if s0 == worst else ""}" style="--d:{.3 + k * .18:.2f}s">'
                f'<td><b>{k + 1}</b> · {d(s0)} – {d(s1)}</td>{cells}</tr>')
    trs += (f'<tr class="anim a-left" style="--d:1.5s"><td><b>Mean</b></td>'
            + "".join(f'<td class="mono{" best" if m == min(cols, key=fm.get) else ""}"><b>{fm[m]:.2f}</b></td>' for m in cols) + "</tr>")

    # the horizon table
    hnames = [("naive", "👵🏾 naive"), ("rate_seasonal_naive", "🧮 rate seasonal naive"), ("exp_smoothing", "exp. smoothing"),
              ("moving_average", "moving average"), ("seasonal_naive", "seasonal naive"), ("training_mean", "flat training mean")]
    htr = ""
    for j, (key, lab) in enumerate(hnames):
        cells = ""
        for k in (1, 4, 8):
            best = min(hz[k]["mean"], key=hz[k]["mean"].get)
            cells += f'<td class="mono{" best" if key == best else ""}">{hz[k]["mean"][key]:.2f} <span class="small">· {hz[k]["wins"].get(key, 0)} wins</span></td>'
        htr += f'<tr class="anim a-left" style="--d:{.3 + j * .15:.2f}s"><td><b>{lab}</b></td>{cells}</tr>'

    lucky_rows = [("📊 flat training mean", F["training_mean_mae"], GREEN), ("👵🏾 naive", bm["naive"], GOLD),
                  ("〰️ exp. smoothing", bm["exp_smoothing"], B["blue_d"]), ("📏 moving average", bm["moving_average"], B["blue_d"]),
                  ("📅 seasonal naive", bm["seasonal_naive"], AXIS)]
    many_rows = [(f"{'📊 flat training mean' if k == 'training_mean' else k.replace('_', ' ')}", h8m[k],
                  RED if k == "training_mean" else (GREEN if k == order8[0] else AXIS)) for k in order8]

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:70px;top:140px;width:540px;height:580px">
  <svg viewBox="0 0 540 580" width="540" height="580">
    <rect x="70" y="30" width="380" height="500" rx="22" fill="#EAF2FB" class="anim a-pop" style="--d:.2s;transform-origin:260px 280px"/>
    <text x="260" y="92" font-size="30" font-weight="800" fill="#0B1622" text-anchor="middle">🎟️ BET SLIP</text>
    <rect x="110" y="120" width="300" height="12" rx="6" fill="#C9D6E5"/><rect x="110" y="150" width="260" height="12" rx="6" fill="#C9D6E5"/>
    <rect x="110" y="180" width="290" height="12" rx="6" fill="#C9D6E5"/><rect x="110" y="210" width="240" height="12" rx="6" fill="#C9D6E5"/>
    <g class="anim a-pop" style="--d:.7s;transform-origin:260px 300px"><rect x="120" y="262" width="280" height="76" rx="12" fill="none" stroke="#1E9E5A" stroke-width="7" transform="rotate(-7 260 300)"/>
    <text x="260" y="314" font-size="40" font-weight="800" fill="#1E9E5A" text-anchor="middle" transform="rotate(-7 260 300)">SURE BANKER</text></g>
    <path class="draw" style="--d:1.3s;--dur:.9s" d="M110 470 C 180 380, 300 520, 420 400" stroke="#0A5DB4" stroke-width="10" fill="none" stroke-linecap="round"/>
    <text x="260" y="512" font-size="26" font-weight="800" fill="#0A5DB4" text-anchor="middle" class="anim a-fade" style="--d:2s">replayed on last season…</text>
  </svg></div>
<div style="max-width:880px;margin-top:40px">
  <div class="kicker anim">Week 6 · Day 1</div>
  <h1 class="anim" style="--d:.2s">Backtesting:<br>Test It on<br><span class="hl">the Past First</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Before you stake real money on a forecast,<br>replay it on weeks that already happened. 🔁</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex">{logos_title_block()}</div>
</div>""",
          "Welcome to Week 6. Last week we built forecasts and scored them on ONE stretch of 8 weeks. Today we ask: was that score luck? "
          "Backtesting = replaying a forecasting method on the past, many times, using only what was known at each moment."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">One score is a screenshot. Get the full record.</h2>
<div class="flow" style="margin-top:56px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:250px;padding:38px 24px"><div class="icon">📸</div><h3>One split lies</h3><p class="small">the lucky 8 weeks</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:250px;padding:38px 24px"><div class="icon">🚶🏾</div><h3>Walk forward</h3><p class="small">6 folds, refit each time</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:250px;padding:38px 24px"><div class="icon">🥊</div><h3>Same folds</h3><p class="small">every method, one scorer</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:250px;padding:38px 24px"><div class="icon">🔭</div><h3>How far ahead?</h3><p class="small">1, 4 and 8 weeks</p></div>
  <div class="arrow anim a-fade" style="--d:1.7s"></div>
  <div class="box on anim a-pop" style="--d:1.9s;min-width:230px;padding:38px 24px"><div class="icon">📝</div><h3>Verdict</h3><p class="small">4 sentences</p></div>
</div>
<div class="row anim" style="--d:2.2s;margin-top:56px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up</span>
</div>""",
          "Five moves. Everything today uses the same ticket file as Week 5 Days 2 and 3, and the same functions."),

        # 3 ─ hook
        S("""
<div class="kicker anim">Quick story</div>
<h2 class="anim" style="--d:.1s">Oga Tipster's WhatsApp status 📱</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🤑</div><h3>One screenshot</h3>
    <p class="muted">“10 odds, <b style="color:#fff">sure banker</b>, I don win again! ₦500 → ₦50,000. Subscribe for my VIP tips.”</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill gold">one big win</span><span class="pill bad">no record</span></div></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">📒</div><h3>Your cousin the accountant</h3>
    <p class="muted">“Send me his tips for <b style="color:#fff">every match last season</b>. I'll check them against the real results before anybody pays.”</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill teal">full record</span><span class="pill">boring, honest</span></div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:34px;text-align:center">Replaying a method on the past, using only what was known at the time,<br>is a <b class="hl">backtest</b>. Even the sure banker needs one. 🔁</p>""",
          "Keep it light: we are not recommending betting. The point: one screenshot of a win says nothing. The record over every match says everything. "
          "A forecast scored on one stretch of weeks is a screenshot."),

        # 4 ─ the lucky split
        S(f"""
<div class="kicker anim">Remember Week 5 · Day 2? The last 8 weeks.</div>
<h2 class="anim" style="--d:.1s">Look who won the four-baseline race 😳</h2>
<div class="anim a-fade" style="--d:.2s;margin-top:16px">{hbars_svg(lucky_rows, 16)}</div>
<p class="sub anim" style="--d:1.6s;margin-top:20px;text-align:center">A <b class="hl">flat average</b> of the training weeks scored <b class="hl">{F['training_mean_mae']:.2f}</b>, better than all four code-book baselines.<br>Genius? Or one lucky screenshot? 📸</p>""",
          f"MAE on the 8 held-out weeks {d(F['holdout'][0])} – {d(F['holdout'][1])} 2025. The flat average was never a good idea: the network grows every week. "
          f"It got lucky because the dry-season dip after 3 November pulled the real numbers down towards the old average. "
          f"(The rate seasonal naive from Week 5 Day 2 scored {bm['rate_seasonal_naive']:.2f} on the same weeks; we meet it again in Part 2.)"),

        # 5 ─ the answer
        S(f"""
<div class="kicker anim">The full record: forecast 8 weeks ahead from {o8[2]} different weeks</div>
<h2 class="anim" style="--d:.1s">Over many tries, the “genius” comes <span style="color:{RED}">last</span></h2>
<div class="anim a-fade" style="--d:.2s;margin-top:16px">{hbars_svg(many_rows, 18)}</div>
<p class="sub anim" style="--d:1.8s;margin-top:16px;text-align:center">Mean MAE over {o8[2]} origins: the flat mean is <b style="color:{RED}">{h8m['training_mean']:.2f}</b>, the worst of all.<br><b class="hl">One split is one screenshot.</b> A backtest is the full record.</p>""",
          f"Each method forecast 8 weeks ahead from every week between {d(o8[0])} 2024 and {d(o8[1])} 2025 ({o8[2]} starting points), using only the weeks before. "
          "Same scorer, same weeks. The flat mean's one great score was luck. Teach the phrase: one split is one screenshot."),

        # 6 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">Walk forward 🚶🏾</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Pretend it's June. Forecast. Check. Pretend it's July…</p>""",
          "Section break.", cls="center"),

        # 7 ─ walk-forward diagram
        S(f"""
<div class="kicker anim">The code book's walk-forward backtest · the Week 5 Day 3 regression</div>
<h2 class="anim" style="--d:.1s;margin-bottom:10px">Six exams, each on weeks it has never seen</h2>
{walkforward_svg(F, D)}
<p class="anim" style="--d:3.4s;margin-top:6px;text-align:center">At every cut: <b class="hl">refit</b> on the past only → forecast the next 4 weeks → score → slide 4 weeks on.</p>""",
          f"This is an expanding window: the training block only grows. Fold 1 trains on the first {D['fold_ranges'][0][2]} weeks of the feature table "
          f"({d(D['feat_start'])} 2024 – just before {d(D['fold_ranges'][0][0])}). Each fold is 4 weeks. The regression uses last week's real count, so inside a fold "
          "each forecast is one week ahead. The numbers on the right are each fold's MAE."),

        # 8 ─ code
        S("""
<div class="kicker anim">The whole idea in a few lines</div>
<h2 class="anim" style="--d:.1s">walk_forward_mae()</h2>
<pre class="code anim" style="--d:.3s;font-size:24px">def walk_forward_mae(df, feature_fn, x_cols, start_frac=0.5, step=4, h=4):
    feat_all = feature_fn(df)
    n = len(feat_all)
    errors = []
    for cut in range(int(n * start_frac), n - h, step):
        tr, te = feat_all.iloc[:cut], feat_all.iloc[cut:cut + h]   # past | next h weeks
        model = LinearRegression().fit(tr[x_cols], tr["target"])    # refit on the past ONLY
        errors.append(mae(model.predict(te[x_cols]), te["target"]))
    return np.array(errors)</pre>
<p class="anim" style="--d:.8s;margin-top:20px;text-align:center"><code>iloc[:cut]</code> = everything <b>before</b> the cut. <code>iloc[cut:cut + h]</code> = the next <code>h</code> weeks. Nothing from the future gets in.</p>""",
          "Walk through it line by line. start_frac=0.5 means the first fold starts halfway through the feature table. step=4 slides 4 weeks each time; h=4 scores 4 weeks."),

        # 9 ─ fold MAE bars + chart
        S(f"""
<div class="kicker anim">Six numbers, not one</div>
<h2 class="anim" style="--d:.1s;margin-bottom:6px">Mean {fm['regression']:.2f}… but look at fold 5</h2>
<div class="anim a-fade" style="--d:.2s">{foldline_svg(F, D)}</div>
<div class="row anim" style="--d:2.8s;gap:18px;justify-content:center;margin-top:8px">
  {"".join(f'<span class="pill{" bad" if t == worst else ""}">fold {k + 1}: {v:.2f}</span>' for k, (t, v) in enumerate(reg.items()))}
</div>""",
          f"White = what happened, dashed blue = the regression's one-week-ahead forecasts. Fold MAEs range from {reg.min():.2f} to {reg.max():.2f}: "
          f"the worst fold is {D['spread_ratio']:.0f} times worse than the best. Fold 5 ({d(worst)} – {d(D['fold_ranges'][4][1])}) contains 3 November, "
          f"when the rainy season ends and tickets fall from {D['oct27']} to {D['nov3']} in one week. A smooth wave can't make a step."),

        # 10 ─ report the spread
        S(f"""
<div class="kicker anim">What goes in your report</div>
<h2 class="anim" style="--d:.1s">Report the spread, and <span class="hl">when</span> it goes wrong</h2>
<div class="grid3" style="margin-top:34px">
  <div class="card anim a-pop" style="--d:.4s;text-align:center"><div class="stat">{fm['regression']:.2f}</div><div class="stat-label">mean MAE over 6 folds</div></div>
  <div class="card anim a-pop" style="--d:.65s;text-align:center"><div class="stat good">{reg.min():.2f} → <span style="color:{RED}">{reg.max():.2f}</span></div><div class="stat-label">best → worst fold</div></div>
  <div class="card anim a-pop" style="--d:.9s;text-align:center"><div class="stat hl">🌦️</div><div class="stat-label">worst = the fold with the season change</div></div>
</div>
<p class="sub anim" style="--d:1.3s;margin-top:34px;text-align:center">“Usually off by about 4 tickets a week, <b class="hl">up to 8 when the rains end</b>.”<br>That sentence is worth more than any single score.</p>""",
          "Quiz 4 question on reporting the spread: the right answer is the spread across folds and when the bad folds occur. "
          "A planner needs to know WHEN the forecast is weak, so they can add staff margin in those weeks."),

        # 11 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Same folds, every method 🥊</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">A model score means nothing on its own.</p>""",
          "Section break.", cls="center"),

        # 12 ─ fold table
        S(f"""{TABLE_CSS}
<div class="kicker anim">MAE per fold · lower is better · green = best in that fold</div>
<h2 class="anim" style="--d:.1s;font-size:50px;margin-bottom:10px">The fold-by-fold report card</h2>
<table class="sb"><tr class="anim" style="--d:.1s"><th>Fold</th><th>📈 Regression</th><th>👵🏾 Naive</th><th>📅 Seasonal naive</th><th>🧮 Rate seasonal naive</th></tr>{trs}</table>
<p class="anim small" style="--d:1.8s;margin-top:12px;text-align:center">Regression and naive forecast each week from last week's real count (1 week ahead). The rate forecast is made <b>once</b>, at the start of each fold, for all 4 weeks.</p>""",
          "Same six folds, same weeks, same scorer for everyone. Naive here is the one-step version: each week's forecast is the week before's real count, "
          "exactly the information the regression gets. That's like with like. Seasonal naive copies the same week last year."),

        # 13 ─ naive beats regression
        S(f"""
<div class="kicker anim">Grandma strikes again 👵🏾</div>
<h1 class="anim" style="--d:.15s;font-size:80px">Naive beats the regression<br>on <span class="hl">{F['naive_beats_reg']} of 6</span> folds</h1>
<div class="grid3" style="margin-top:34px">
  <div class="card anim a-pop" style="--d:.5s;text-align:center"><div class="stat good">{fm['naive']:.2f}</div><div class="stat-label">naive, mean MAE</div></div>
  <div class="card anim a-pop" style="--d:.75s;text-align:center"><div class="stat">{fm['regression']:.2f}</div><div class="stat-label">regression, mean MAE</div></div>
  <div class="card anim a-pop" style="--d:1s;text-align:center"><div class="stat bad">{fm['seasonal_naive']:.2f}</div><div class="stat-label">seasonal naive: ignores the growing network</div></div>
</div>
<p class="sub anim" style="--d:1.4s;margin-top:28px">The regression only wins the <b class="hl">{d(D['reg_only_win'][0])}</b> fold, when the December jump arrives.<br>On the Week 5 Day 3 split it won. Across six folds, it doesn't.</p>""",
          "This is the code book's own conclusion, and it reproduces exactly. Five columns of features and a fitted model, and 'same as last week' wins most folds. "
          "Quiz 4 has a question on exactly this (naive won five of six folds with lower mean error)."),

        # 14 ─ rate forecast on the same folds
        S(f"""
<div class="kicker anim">Bring back the Week 5 Day 2 trick: tickets per terminal</div>
<h2 class="anim" style="--d:.1s">The rate forecast, <span class="hl">blind 4 weeks ahead</span></h2>
<div class="grid3" style="margin-top:26px">
  <div class="card anim a-pop" style="--d:.4s;text-align:center"><div class="stat good">{fm['rate_seasonal_naive']:.2f}</div><div class="stat-label">mean MAE: the lowest, with the least information</div></div>
  <div class="card anim a-pop" style="--d:.65s;text-align:center"><div class="stat good">{folds.loc[worst, 'rate_seasonal_naive']:.2f}</div><div class="stat-label">on the season-change fold (naive {folds.loc[worst, 'naive']:.2f} · regression {folds.loc[worst, 'regression']:.2f})</div></div>
  <div class="card anim a-pop" style="--d:.9s;text-align:center"><div class="stat hl">{F['rate_beats_naive']} of 6</div><div class="stat-label">folds where it beats naive: honest, not a clean sweep</div></div>
</div>
<p class="sub anim" style="--d:1.3s;margin-top:30px;text-align:center">It knew the rains end in November: <b class="hl">last November's rate</b> showed it. ☀️</p>""",
          f"Important: naive and the regression saw last week's real count every week; the rate forecast saw nothing after the fold started. Still the lowest mean. "
          f"It beats the regression on {D['rate_beats_reg']} of 6 folds and naive on {F['rate_beats_naive']} of 6. In calm summer folds, last week is very hard to beat. "
          "Don't oversell it: say 'lowest average, best at the season change, not best every fold'."),

        # 15 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">How far ahead? 🔭</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Next week's shift and next month's roster are different questions.</p>""",
          "Section break.", cls="center"),

        # 16 ─ rolling origin illustration
        S(f"""
<div class="kicker anim">Rolling origin: stand at every week</div>
<h2 class="anim" style="--d:.1s">One origin per week, three horizons</h2>
<div class="anim a-fade" style="--d:.2s;margin-top:22px">{origin_svg()}</div>
<div class="grid3" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:2.8s;text-align:center;padding:20px"><h3>1 week ahead</h3><p class="small">{o1[2]} origins</p></div>
  <div class="card anim a-pop" style="--d:3.0s;text-align:center;padding:20px"><h3>4 weeks ahead</h3><p class="small">{o4[2]} origins</p></div>
  <div class="card anim a-pop" style="--d:3.2s;text-align:center;padding:20px"><h3>8 weeks ahead</h3><p class="small">{o8[2]} origins</p></div>
</div>""",
          f"The origin is the week you're standing in when you make the forecast. rolling_origin() stands at every week from {d(o1[0])} 2024, uses only the weeks before it, "
          "forecasts the next h weeks blind and scores them. Fewer origins for longer horizons, because the last ones would run past the end of the data."),

        # 17 ─ horizon chart
        S(f"""
<div class="kicker anim">Mean MAE by horizon · blind forecasts · every origin</div>
<h2 class="anim" style="--d:.1s;margin-bottom:6px">Grandma tires. The rate forecast doesn't. 🏃🏾</h2>
{horizon_svg(F)}
<p class="anim small" style="--d:3s;text-align:center">Off the chart: seasonal naive ({hz[1]['mean']['seasonal_naive']:.1f}–{hz[8]['mean']['seasonal_naive']:.1f}) and the flat training mean ({hz[1]['mean']['training_mean']:.1f}–{hz[8]['mean']['training_mean']:.1f}).</p>""",
          f"1 week ahead: naive {hz[1]['mean']['naive']:.2f}, rate {hz[1]['mean']['rate_seasonal_naive']:.2f}: a tie (naive wins {hz[1]['wins'].get('naive', 0)} origins, rate {hz[1]['wins'].get('rate_seasonal_naive', 0)}). "
          f"4 weeks: rate {hz[4]['mean']['rate_seasonal_naive']:.2f} vs naive {hz[4]['mean']['naive']:.2f}. 8 weeks: rate {hz[8]['mean']['rate_seasonal_naive']:.2f} vs naive {hz[8]['mean']['naive']:.2f}. "
          "Naive's error grows because 'last week' gets staler the further out you go. The rate forecast copies last year's pattern, which doesn't go stale."),

        # 18 ─ per-origin line
        S(f"""
<div class="kicker anim">Every 8-week forecast, one point per origin</div>
<h2 class="anim" style="--d:.1s;margin-bottom:6px">Naive's bad weeks: the season changes</h2>
<div class="anim a-fade" style="--d:.2s">{h8_line_svg(F, D)}</div>
<p class="anim" style="--d:2.6s;text-align:center">Worst 8-week MAE: naive <b style="color:{GOLD}">{D['h8_naive_max']:.2f}</b> · rate <b style="color:{GREEN}">{D['h8_rate_max']:.2f}</b>. When the rains start or stop, “same as last week” is wrong for weeks on end.</p>""",
          "Each point is one forecast: stand at that week, forecast the next 8 weeks, MAE. Naive's spikes are origins just before April (rains start) and just before November (rains stop). "
          "This is 'when the bad folds occur', drawn as a picture."),

        # 19 ─ table
        S(f"""{TABLE_CSS}
<div class="kicker anim">The full record · mean MAE · how many origins each method won</div>
<h2 class="anim" style="--d:.1s;font-size:50px;margin-bottom:10px">Which forecast, for which question?</h2>
<table class="sb"><tr class="anim" style="--d:.1s"><th>Method</th><th>1 week ahead ({o1[2]})</th><th>4 weeks ahead ({o4[2]})</th><th>8 weeks ahead ({o8[2]})</th></tr>{htr}</table>""",
          "Wins = the number of origins where that method had the lowest MAE. Read the green cells: naive at 1 week (by a hair), the rate forecast at 4 and 8."),

        # 20 ─ regression only does h=1
        S("""
<div class="kicker anim">And the regression?</div>
<h2 class="anim" style="--d:.1s">It can only see <span class="hl">one week</span> ahead</h2>
<div class="grid2" style="margin-top:26px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🔗</div><h3>It needs last week's real count</h3>
    <p class="muted"><code>tickets_lag1</code> is a feature. To forecast week 4, you'd need week 3's real count… which hasn't happened yet.</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#FF6B6F"><div class="icon">🗓️</div><h3>The month-ahead roster</h3>
    <p class="muted">The NOC plans shifts 4 weeks out. A forecast that only works 1 week ahead <b style="color:#fff">can't make that roster at all</b>.</p></div>
</div>
<p class="sub anim" style="--d:1s;margin-top:32px;text-align:center">Test at the horizon <b class="hl">the user actually needs</b>, not the one that flatters your model.</p>""",
          "The leak rule from Week 5 Day 3 again: every feature must be known when the forecast is made. Four weeks out, last week's count isn't known. "
          "So the regression simply isn't a candidate for the roster question."),

        # 21 ─ verdict
        S(f"""
<div class="kicker anim">The verdict, in 4 sentences</div>
<h2 class="anim" style="--d:.1s">What we tell the NOC manager 📝</h2>
<div class="col" style="gap:14px;margin-top:18px">
  <div class="card anim a-left" style="--d:.3s;padding:20px 30px"><p><b>1.</b> For <b class="hl">next week</b>, use naive, “same as last week” (mean error {hz[1]['mean']['naive']:.1f} tickets); the rate forecast ties it ({hz[1]['mean']['rate_seasonal_naive']:.1f}).</p></div>
  <div class="card anim a-left" style="--d:.55s;padding:20px 30px"><p><b>2.</b> For the <b class="hl">month-ahead roster</b>, use last year's tickets per terminal × today's terminals ({hz[4]['mean']['rate_seasonal_naive']:.1f} vs naive {hz[4]['mean']['naive']:.1f}).</p></div>
  <div class="card anim a-left" style="--d:.8s;padding:20px 30px"><p><b>3.</b> The regression doesn't earn its place: it loses to naive on {F['naive_beats_reg']} of 6 folds and can't forecast past one week.</p></div>
  <div class="card anim a-left" style="--d:1.05s;padding:20px 30px"><p><b>4.</b> Expect the biggest misses when the rains start or stop, so add staff margin in early April and early November.</p></div>
</div>""",
          "This is the same recommend-the-simpler-model lesson as Week 5 Day 1, now for forecasting. Four sentences: what to use, for which question, what not to use, and when to be careful. "
          "This exact shape is the recommendation in the final-project report."),

        # 22 ─ golden rules
        S("""
<div class="kicker anim">Golden rules of an honest backtest</div>
<h2 class="anim" style="--d:.1s">Five rules, every time</h2>
<div class="col" style="gap:10px;margin-top:8px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:24px;align-items:center;padding:13px 30px"><span class="icon" style="margin:0">⏳</span><p><b>Only the past at each origin</b>, and <b>refit</b> every time.</p></div>
  <div class="card anim a-left" style="--d:.5s;display:flex;gap:24px;align-items:center;padding:13px 30px"><span class="icon" style="margin:0">🥊</span><p><b>Same folds, same scorer</b> for every method, baselines included.</p></div>
  <div class="card anim a-left" style="--d:.7s;display:flex;gap:24px;align-items:center;padding:13px 30px"><span class="icon" style="margin:0">📊</span><p><b>Report the spread</b> and when the bad folds happen, not just the mean.</p></div>
  <div class="card anim a-left" style="--d:.9s;display:flex;gap:24px;align-items:center;padding:13px 30px"><span class="icon" style="margin:0">🔭</span><p>Test at the <b>horizon the user needs</b>.</p></div>
  <div class="card anim a-left" style="--d:1.1s;display:flex;gap:24px;align-items:center;padding:13px 30px"><span class="icon" style="margin:0">🔒</span><p><b>Never tune on the folds you report.</b> Fix the design (folds, step, horizon) first.</p></div>
</div>""",
          f"Rule 5 matters more than it looks. In the 🌶️ task, refitting EVERY week instead of every 4 changes the regression's score to {wk['reg']:.2f} vs naive {wk['naive']:.2f}: "
          f"a near tie that flips who wins ({wk['reg_wins']} weeks to {wk['naive_wins']}). The rate forecast still beats both ({wk['rate']:.2f}). Design choices move results, so fix them before you look."),

        # 23 ─ project link + your turn
        S("""
<div class="row" style="gap:56px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Audit the tipster 🔍</h2>
  <div class="col" style="gap:15px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">A</span><p>Expose the lucky split</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">B</span><p>Walk the regression forward</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">C</span><p>Same folds for the baselines</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">D</span><p>Every origin, three horizons</p></div>
   <div class="row anim" style="--d:1.1s;gap:18px;align-items:center"><span class="num">E</span><p>Write the 4-sentence verdict</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.3s;flex:1;text-align:center;padding:40px">
  <div class="big-emoji floaty">🔁</div>
  <h3 style="margin-top:14px">11 checks to pass</h3>
  <p class="muted">🌶️ Pepper task: refit every week. Does the verdict survive?</p>
  <p class="small" style="margin-top:16px">🏁 <b>Final project:</b> forecasting briefs must report a walk-forward spread across folds, not just the average.</p>
 </div>
</div>""",
          "Hands-on. Common snag: forgetting to run the ▶️ tools cell after a restart (NameError: walk_forward_mae). "
          "Project link: anyone on brief C or E (forecasting) must include a walk-forward table like today's in their report."),

        # 24 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:16px;margin-top:6px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">📸</span><p><b>One split is one screenshot.</b> A backtest replays the method on many past origins.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">🥊</span><p><b>Same folds, same scorer, every method:</b> report the spread and when it fails.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">🔭</span><p><b>The best method depends on the horizon.</b> Here the simple ones win: recommend them.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:22px;font-size:30px">Next 👉 <b class="hl">When will it break?</b> Remaining useful life, and we backtest a battery call. 🔋<br>
<span class="small">Then Quiz 4 on all the forecasting days.</span></p>""",
          "Recap. Next session: trend-to-threshold on the satellite's battery, amplifier and fuel, and the same backtesting idea applied to a remaining-life call. Then Quiz 4."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    F = facts()
    D = day_facts()
    folds = F["folds"]
    fm = F["fold_means"]
    hz = F["horizons"]
    bm = F["baseline_mae"]
    reg = folds["regression"]
    worst = F["worst_fold"]
    o8 = D["origins_8"]
    h8m = hz[8]["mean"]
    order8 = sorted(h8m, key=h8m.get)
    nice = {"naive": "naive", "seasonal_naive": "seasonal naive", "moving_average": "moving average", "exp_smoothing": "exp. smoothing",
            "rate_seasonal_naive": "rate seasonal naive", "training_mean": "flat training mean"}
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🔁", "kicker": "Week 6 · Day 1", "title": "Backtesting:\nTest It on the Past First",
             "sub": "Before you stake real money on a forecast, replay it on weeks that already happened",
             "notes": "Today: was last week's score luck? Replay the methods on the past."},
            {"type": "flow", "title": "Today's mission", "steps": [
                ["📸", "One split lies", "the lucky 8 weeks"], ["🚶🏾", "Walk forward", "6 folds, refit each time"],
                ["🥊", "Same folds", "every method, one scorer"], ["🔭", "How far ahead?", "1, 4 and 8 weeks"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up", "notes": "Then the 4-sentence verdict."},
            {"type": "compare", "title": "Oga Tipster's WhatsApp status",
             "left": ["🤑", "One screenshot", "“Sure banker, ₦500 → ₦50,000. Subscribe for VIP tips.”"],
             "right": ["📒", "The full record", "Check his tips against every match last season, before anybody pays"],
             "notes": "Replaying a method on the past, with only what was known then, is a backtest."},
            {"type": "bar", "title": "The last 8 weeks: look who won",
             "labels": ["flat training mean", "naive", "exp. smoothing", "moving average", "seasonal naive"],
             "values": [round(F["training_mean_mae"], 2), round(bm["naive"], 2), round(bm["exp_smoothing"], 2),
                        round(bm["moving_average"], 2), round(bm["seasonal_naive"], 2)], "highlight": [0], "fmt": "0.00",
             "caption": "MAE on the Week 5 Day 2 hold-out. A flat average beat all four code-book baselines. Genius, or one lucky screenshot?",
             "notes": "The dry-season dip pulled the real numbers down towards the old average."},
            {"type": "bar", "title": f"The full record: 8 weeks ahead from {o8[2]} origins",
             "labels": [nice[k] for k in order8], "values": [round(h8m[k], 2) for k in order8],
             "highlight": [len(order8) - 1], "fmt": "0.00",
             "caption": f"Mean MAE. The flat mean is the worst of all ({h8m['training_mean']:.2f}). One split is one screenshot.",
             "notes": "Same scorer, same weeks, only past data at each origin."},
            {"type": "section", "kicker": "Part 1", "title": "Walk forward", "sub": "Pretend it's June. Forecast. Check. Pretend it's July…", "notes": "Section break."},
            {"type": "table", "title": "Six exams, each on weeks it has never seen",
             "header": ["Fold", "Trains on (weeks)", "Tests on", "Regression MAE"],
             "rows": [[k + 1, c, f"{d(s0)} – {d(s1)}", f"{reg.loc[s0]:.2f}"] for k, (s0, s1, c) in enumerate(D["fold_ranges"])],
             "colW": [1.2, 3.0, 4.6, 3.53], "caption": "Refit on the past only → forecast 4 weeks → score → slide 4 weeks on.",
             "notes": "Expanding window: the training block only grows."},
            {"type": "code", "title": "walk_forward_mae()",
             "code": "for cut in range(int(n * 0.5), n - h, step):\n    tr, te = feat.iloc[:cut], feat.iloc[cut:cut + h]\n"
                     "    model = LinearRegression().fit(tr[x_cols], tr[\"target\"])\n    errors.append(mae(model.predict(te[x_cols]), te[\"target\"]))",
             "caption": "iloc[:cut] = everything before the cut. Nothing from the future gets in.", "notes": "start_frac=0.5, step=4, h=4."},
            {"type": "stats", "title": "Report the spread, and when it goes wrong", "sub": "The regression over 6 folds",
             "stats": [[f"{fm['regression']:.2f}", "mean MAE"], [f"{reg.min():.2f} → {reg.max():.2f}", "best → worst fold"],
                       [d(worst), f"worst fold: contains 3 Nov, tickets {D['oct27']} → {D['nov3']}"]],
             "notes": "Usually off by about 4 tickets, up to 8 when the rains end."},
            {"type": "section", "kicker": "Part 2", "title": "Same folds, every method", "sub": "A model score means nothing on its own", "notes": "Section break."},
            {"type": "table", "title": "The fold-by-fold report card (MAE)",
             "header": ["Fold", "Regression", "Naive", "Seasonal naive", "Rate seasonal naive"],
             "rows": [[f"{k + 1} · {d(s0)}", f"{folds.loc[s0, 'regression']:.2f}", f"{folds.loc[s0, 'naive']:.2f}",
                       f"{folds.loc[s0, 'seasonal_naive']:.2f}", f"{folds.loc[s0, 'rate_seasonal_naive']:.2f}"]
                      for k, (s0, s1, c) in enumerate(D["fold_ranges"])]
                     + [["Mean", f"{fm['regression']:.2f}", f"{fm['naive']:.2f}", f"{fm['seasonal_naive']:.2f}", f"{fm['rate_seasonal_naive']:.2f}"]],
             "colW": [2.6, 2.2, 2.2, 2.5, 2.83],
             "caption": "Regression and naive: 1 week ahead from last week's real count. Rate forecast: made once per fold, blind for 4 weeks.",
             "notes": "Like with like."},
            {"type": "statement", "title": "Grandma strikes again", "icon": "👵🏾",
             "big": f"Naive beats the regression on {F['naive_beats_reg']} of 6 folds",
             "sub": f"Mean {fm['naive']:.2f} vs {fm['regression']:.2f}. The regression only wins the {d(D['reg_only_win'][0])} fold (the December jump).",
             "notes": "The code book's own conclusion; it reproduces exactly."},
            {"type": "stats", "title": "The rate forecast, blind 4 weeks ahead", "sub": "Last year's tickets per terminal × today's terminals",
             "stats": [[f"{fm['rate_seasonal_naive']:.2f}", "mean MAE: the lowest"],
                       [f"{folds.loc[worst, 'rate_seasonal_naive']:.2f}", f"season-change fold (naive {folds.loc[worst, 'naive']:.2f}, regression {folds.loc[worst, 'regression']:.2f})"],
                       [f"{F['rate_beats_naive']} of 6", "folds where it beats naive: not a clean sweep"]],
             "notes": "It knew the rains end in November because last November's rate showed it."},
            {"type": "section", "kicker": "Part 3", "title": "How far ahead do you need?", "sub": "Next week's shift and next month's roster are different questions", "notes": "Section break."},
            {"type": "chart", "title": "Grandma tires, the rate forecast doesn't",
             "labels": ["1 week", "4 weeks", "8 weeks"], "ymin": 0, "ymax": 9, "fmt": "0.0",
             "series": [{"name": "naive", "values": [round(hz[k]["mean"]["naive"], 2) for k in (1, 4, 8)], "color": "C77700"},
                        {"name": "rate seasonal naive", "values": [round(hz[k]["mean"]["rate_seasonal_naive"], 2) for k in (1, 4, 8)], "color": "008C7E"},
                        {"name": "exp. smoothing", "values": [round(hz[k]["mean"]["exp_smoothing"], 2) for k in (1, 4, 8)], "color": "0A5DB4"},
                        {"name": "moving average", "values": [round(hz[k]["mean"]["moving_average"], 2) for k in (1, 4, 8)], "color": "9DB0C6"}],
             "caption": f"Every origin, blind forecasts. 1 week: a tie ({hz[1]['mean']['naive']:.2f} vs {hz[1]['mean']['rate_seasonal_naive']:.2f}). 8 weeks: {hz[8]['mean']['rate_seasonal_naive']:.2f} vs {hz[8]['mean']['naive']:.2f}.",
             "notes": "Naive's error grows because last week gets staler."},
            {"type": "table", "title": "Which forecast, for which question?",
             "header": ["Method", "1 week ahead", "4 weeks ahead", "8 weeks ahead"],
             "rows": [[nice[k]] + [f"{hz[h]['mean'][k]:.2f} ({hz[h]['wins'].get(k, 0)} wins)" for h in (1, 4, 8)]
                      for k in ("naive", "rate_seasonal_naive", "exp_smoothing", "moving_average", "seasonal_naive", "training_mean")],
             "colW": [3.6, 2.9, 2.9, 2.93], "caption": f"Mean MAE over {D['origins_1'][2]} / {D['origins_4'][2]} / {o8[2]} origins; wins = origins where it was best.",
             "notes": "Naive at 1 week by a hair; the rate forecast at 4 and 8."},
            {"type": "compare", "title": "The regression can only see one week ahead",
             "left": ["🔗", "It needs last week's real count", "To forecast week 4 you'd need week 3's count, which hasn't happened yet"],
             "right": ["🗓️", "The month-ahead roster", "The NOC plans shifts 4 weeks out: the regression can't make that roster"],
             "notes": "Test at the horizon the user needs."},
            {"type": "steps", "title": "The verdict, in 4 sentences", "icon": "📝", "steps": [
                f"Next week: naive ({hz[1]['mean']['naive']:.1f}); the rate forecast ties ({hz[1]['mean']['rate_seasonal_naive']:.1f})",
                f"Month-ahead roster: rate seasonal naive ({hz[4]['mean']['rate_seasonal_naive']:.1f} vs {hz[4]['mean']['naive']:.1f})",
                f"Regression: loses {F['naive_beats_reg']} of 6 folds to naive, can't go past 1 week",
                "Biggest misses when the rains start or stop: add margin"], "notes": "Recommend the simpler model."},
            {"type": "cards5", "title": "Five rules of an honest backtest", "cards": [
                ["⏳", "Only the past", "refit at every origin"], ["🥊", "Same folds", "same scorer, every method"],
                ["📊", "The spread", "and when it fails"], ["🔭", "Right horizon", "the one the user needs"],
                ["🔒", "No tuning", "on the folds you report"]], "notes": "Fix the design before you look."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🔍", "steps": [
                "Open W6D1-exercise, save a copy, run STEP 0", "A: expose the lucky split · B: walk forward",
                "C: same folds for the baselines · D: three horizons", "E: write the 4-sentence verdict"],
             "notes": "Final project: forecasting briefs must report the spread across folds."},
            {"type": "recap", "title": "What you now know", "points": [
                ["📸", "One split is one screenshot: backtest on many past origins"],
                ["🥊", "Same folds, same scorer, every method; report the spread and when it fails"],
                ["🔭", "The best method depends on the horizon: here the simple ones win"]],
             "next": "Next: When will it break? Remaining useful life + Quiz 4", "notes": "Recap."},
        ],
    }


# =============================================================================
# NOTEBOOK CHECKS (expected values filled in from the data at build time)
# =============================================================================
def _checks():
    F = facts()
    D = day_facts()
    folds = F["folds"]
    hz = F["horizons"]
    worst = F["worst_fold"]
    vals = {
        "TMEAN": f"{F['training_mean_mae']!r}", "N8": str(hz[8]["n"]), "TMEAN8": f"{hz[8]['mean']['training_mean']!r}",
        "FOLDS": repr([round(float(v), 4) for v in folds["regression"]]), "REGMEAN": f"{F['fold_means']['regression']!r}",
        "WORST": repr(f"{worst:%Y-%m-%d}"), "WORSTD": d(worst),
        "NAIVE": repr([round(float(v), 4) for v in folds["naive"]]), "NAIVEMEAN": f"{F['fold_means']['naive']:.2f}",
        "NWINS": str(F["naive_beats_reg"]), "REGONLY": d(D["reg_only_win"][0]),
        "RATEMEAN": f"{F['fold_means']['rate_seasonal_naive']!r}", "RATEWORST": f"{folds.loc[worst, 'rate_seasonal_naive']!r}",
        "N1": f"{hz[1]['mean']['naive']!r}", "R1": f"{hz[1]['mean']['rate_seasonal_naive']!r}",
        "N4": f"{hz[4]['mean']['naive']!r}", "R4": f"{hz[4]['mean']['rate_seasonal_naive']!r}",
        "N8M": f"{hz[8]['mean']['naive']!r}", "R8": f"{hz[8]['mean']['rate_seasonal_naive']!r}",
        "N1F": f"{hz[1]['mean']['naive']:.2f}", "R1F": f"{hz[1]['mean']['rate_seasonal_naive']:.2f}",
        "N4F": f"{hz[4]['mean']['naive']:.2f}", "R4F": f"{hz[4]['mean']['rate_seasonal_naive']:.2f}",
        "N8F": f"{hz[8]['mean']['naive']:.2f}", "R8F": f"{hz[8]['mean']['rate_seasonal_naive']:.2f}",
        "WREG": f"{D['weekly']['reg']!r}", "WNAIVE": f"{D['weekly']['naive']:.2f}", "WRATE": f"{D['weekly']['rate']:.2f}",
        "WREGW": str(D["weekly"]["reg_wins"]), "WNAIVEW": str(D["weekly"]["naive_wins"]),
    }
    code = r'''
def _near(x, want, tol):
    return abs(float(x) - want) <= tol

def _c_a1(x):
    return _near(x, @@TMEAN@@, 0.01), \
        f"{float(x):.2f}: the flat average beat all four code-book baselines on these 8 weeks. Genius… or one lucky screenshot? 📸", \
        "The flat average of the training weeks: train.mean()"

def _c_a2(x):
    n, m = x
    return int(n) == @@N8@@ and _near(m, @@TMEAN8@@, 0.01), \
        f"{int(n)} origins, mean MAE {float(m):.2f}: over the full record the 'genius' is the worst of all. One split is one screenshot. 🙈", \
        "The lucky split forecast 8 weeks ahead: H_AHEAD = 8"

def _c_b1(x):
    v = [round(float(a), 4) for a in x]
    want = @@FOLDS@@
    return len(v) == len(want) and all(abs(a - b) < 0.01 for a, b in zip(v, want)), \
        f"Six folds: {', '.join(f'{a:.2f}' for a in v)}. Six exams, not one. 🚶🏾", \
        "The code book slides 4 weeks each time and scores 4 weeks: STEP = 4, H_FOLD = 4"

def _c_b2(x):
    m, w = x
    return _near(m, @@REGMEAN@@, 0.01) and pd.Timestamp(w) == pd.Timestamp(@@WORST@@), \
        f"Mean {float(m):.2f}, worst fold starts @@WORSTD@@: it contains 3 November, when the rains end. Report the spread AND when. 🌦️", \
        "MEAN = fold_mae.mean() and WORST_FOLD = folds[\"regression\"].idxmax()"

def _c_c1(x):
    v = [round(float(a), 4) for a in x]
    want = @@NAIVE@@
    return len(v) == len(want) and all(abs(a - b) < 0.01 for a, b in zip(v, want)), \
        "Naive, made the same way as the regression: each week = last week's real count. Mean @@NAIVEMEAN@@. 👵🏾", \
        "One-step naive is the column that holds last week's count: NAIVE_COLUMN = \"tickets_lag1\""

def _c_c2(x):
    return int(x) == @@NWINS@@, \
        "@@NWINS@@ of 6: Grandma beats the regression on five folds. It only wins the @@REGONLY@@ fold (the December jump). 👵🏾🏆", \
        "Count the folds where naive's MAE is smaller: int((folds[\"naive\"] < folds[\"regression\"]).sum())"

def _c_c3(x):
    m, w = x
    return _near(m, @@RATEMEAN@@, 0.01) and _near(w, @@RATEWORST@@, 0.01), \
        f"Mean {float(m):.2f}, the lowest, and {float(w):.2f} on the season-change fold, forecasting all 4 weeks blind. 🧮", \
        "The rate forecast is made once per fold, for the whole fold: RATE_H = 4"

def _c_d1(x):
    t = x
    ok = list(t.index) == [1, 4, 8] and all(_near(t.loc[h, k], v, 0.01) for h, k, v in (
        (1, "naive", @@N1@@), (1, "rate_seasonal_naive", @@R1@@), (4, "naive", @@N4@@),
        (4, "rate_seasonal_naive", @@R4@@), (8, "naive", @@N8M@@), (8, "rate_seasonal_naive", @@R8@@)))
    return ok, "Naive: @@N1F@@ → @@N4F@@ → @@N8F@@ as you look further ahead. Rate: @@R1F@@ → @@R4F@@ → @@R8F@@. Grandma tires; the rate forecast doesn't. 🏃🏾", \
        "Three horizons, in weeks, as a list: HORIZONS = [1, 4, 8]"

def _c_d2(x):
    a, b = (str(v).strip() for v in x)
    return a == "naive" and b == "rate_seasonal_naive", \
        "1 week ahead: naive, by a hair over the rate forecast. 8 weeks ahead: the rate forecast, by a mile. The horizon decides. 🔭", \
        "Lowest number in each row: BEST_1 = summary.loc[1].idxmin(), BEST_8 = summary.loc[8].idxmin()"

def _c_e1(x):
    return int(x) == 4, \
        "4: the roster needs 4 weeks ahead. The regression can't run that far, and naive's error grows. Rate seasonal naive. ✅", \
        "The roster is 4 weeks out. Which method can forecast 4 weeks blind, with the lowest error in Part D?"

def _c_bonus(x):
    return _near(x, @@WREG@@, 0.01), \
        f"{float(x):.2f} vs naive @@WNAIVE@@: refit every week and the regression edges ahead (@@WREGW@@ weeks to @@WNAIVEW@@). The rate forecast scores @@WRATE@@ on the same weeks, and it's the only one that works 8 weeks out. A design choice moved the result: fix yours BEFORE you look. 🌶️", \
        "Refit every week, forecast one week: STEP_EVERY = 1"

CHECKS = {"A1": _c_a1, "A2": _c_a2, "B1": _c_b1, "B2": _c_b2, "C1": _c_c1, "C2": _c_c2, "C3": _c_c3,
          "D1": _c_d1, "D2": _c_d2, "E1": _c_e1, "BONUS": _c_bonus}
HINTS = {"A2": "H_AHEAD is a number of weeks.", "B1": "STEP and H_FOLD are numbers of weeks.",
         "B2": "MEAN is a number; WORST_FOLD is the date the worst fold starts.", "D1": "HORIZONS is a list of numbers.",
         "D2": "Two method names, as text, from the summary table's columns.", "E1": "A number from 1 to 4."}
'''
    for k, v in vals.items():
        code = code.replace(f"@@{k}@@", v)
    assert "@@" not in code
    return code


CHECKS = _checks()


# =============================================================================
# NOTEBOOK
# =============================================================================
def _task(blank: str, filled: str):
    return ("task", blank, filled)


def notebook_cells(setup_code):
    F = facts()
    D = day_facts()
    hz = F["horizons"]
    forecasters_code = ('forecasters = {\n'
                        '    "naive": lambda past, h: naive(past["tickets_raised"], h),\n'
                        '    "seasonal_naive": lambda past, h: seasonal_naive(past["tickets_raised"], h),\n'
                        '    "moving_average": lambda past, h: moving_average(past["tickets_raised"], h),\n'
                        '    "exp_smoothing": lambda past, h: exp_smoothing(past["tickets_raised"], h),\n'
                        '    "rate_seasonal_naive": lambda past, h: rate_seasonal_naive(past["tickets_raised"],\n'
                        '                                                               past["active_vsat_terminals"], h),\n'
                        '}\n')
    d1_tail = ('by_h = {}\nfor h in HORIZONS:\n    by_h[h] = rolling_origin(tickets, forecasters, h)\n'
               '    print(f"{h} week(s) ahead: {len(by_h[h])} origins, from {by_h[h].index[0]:%d %b %Y} to {by_h[h].index[-1]:%d %b %Y}")\n\n'
               'summary = pd.DataFrame({h: r.mean() for h, r in by_h.items()}).T     # rows = weeks ahead, columns = methods\n'
               'summary.index.name = "weeks ahead"\ndisplay(summary.round(2))\ncheck("D1", summary)')
    return [
        ("md", """# 🔁 Week 6 · Day 1: Backtesting: Test It on the Past First

**Today:** you expose a lucky score, replay the Week 5 forecasts on the past many times (a **backtest**), and decide which forecast the NOC should use for next week and for next month's roster.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**

**Rule book:** keep `W6D1-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up
Run it once every time you open the notebook (and after every restart). Wait for `✅ Ready!`."""),
        ("setup", setup_code),
        ("md", """### ▶️ The data
The same weekly NOC ticket file as Week 5 Days 2 and 3: tickets raised each week, and how many VSAT terminals were live."""),
        ("code", 'from sklearn.linear_model import LinearRegression\n\n'
                 'tickets = pd.read_csv(data_path("ops_tickets_weekly"), parse_dates=["week_start"],\n'
                 '                      index_col="week_start").asfreq("W-MON")\n'
                 'print("weeks:", len(tickets), "· from", tickets.index[0].date(), "to", tickets.index[-1].date(),\n'
                 '      "· gaps:", int(tickets.isna().sum().sum()))\ntickets.tail(3)'),
        ("md", """### ▶️ Your tools from Week 5 (run all three cells)
The baselines and the MAE scorer (Week 5 Day 2), the feature table (Week 5 Day 3), and today's two backtest functions. Read them once, then run."""),
        ("code", BASELINE_CODE + '\n\nprint("✅ naive, seasonal_naive, moving_average, exp_smoothing, rate_seasonal_naive, mae: ready")'),
        ("code", FEATURE_CODE + f'\n\nX_COLS = {X_COLS!r}\nprint("✅ make_features and X_COLS: ready")'),
        ("code", BACKTEST_CODE + '\n\nprint("✅ walk_forward_mae and rolling_origin: ready")'),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Expose the lucky split (10 min) 📸

📖 In Week 5 Day 2 we held out the **last 8 weeks** and scored four baselines on them. Let's add a fifth contender that nobody would bet on: the **flat average** of every training week.

### A1 ✍️ The flat training mean
Make an 8-week forecast that is the training average, repeated: replace `___` with the average of `train`."""),
        _task(f'H = {H}\ntrain, actual = tickets["tickets_raised"].iloc[:-H], tickets["tickets_raised"].iloc[-H:]\n'
              'board = pd.Series({\n    "naive": mae(naive(train, H), actual),\n    "seasonal_naive": mae(seasonal_naive(train, H), actual),\n'
              '    "moving_average": mae(moving_average(train, H), actual),\n    "exp_smoothing": mae(exp_smoothing(train, H), actual),\n})\n\n'
              'flat = ___\n\nassert flat is not None, "✍️ Fill in flat first."\nmean_forecast = np.full(H, flat)\n'
              'board["training_mean"] = mae(mean_forecast, actual)\n'
              'display(board.sort_values().round(2).to_frame("MAE, last 8 weeks"))\ncheck("A1", board["training_mean"])',
              f'H = {H}\ntrain, actual = tickets["tickets_raised"].iloc[:-H], tickets["tickets_raised"].iloc[-H:]\n'
              'board = pd.Series({\n    "naive": mae(naive(train, H), actual),\n    "seasonal_naive": mae(seasonal_naive(train, H), actual),\n'
              '    "moving_average": mae(moving_average(train, H), actual),\n    "exp_smoothing": mae(exp_smoothing(train, H), actual),\n})\n\n'
              'flat = train.mean()\n\nassert flat is not None, "✍️ Fill in flat first."\nmean_forecast = np.full(H, flat)\n'
              'board["training_mean"] = mae(mean_forecast, actual)\n'
              'display(board.sort_values().round(2).to_frame("MAE, last 8 weeks"))\ncheck("A1", board["training_mean"])'),
        ("md", """### A2 ✍️ The full record
📖 `rolling_origin()` stands at **every** week of the second year, uses only the weeks before it, forecasts the next `h` weeks and scores them.
Each forecaster is a small function: it gets `past` (the weeks before the origin) and `h`, and returns `h` numbers.

✍️ Set `H_AHEAD` to the same horizon as the lucky split (how many weeks did A1 forecast?)."""),
        _task('forecasters_a = {\n    "naive": lambda past, h: naive(past["tickets_raised"], h),\n'
              '    "training_mean": lambda past, h: np.full(h, past["tickets_raised"].mean()),\n}\n\n'
              'H_AHEAD = ___\n\nassert H_AHEAD is not None, "✍️ Fill in H_AHEAD first."\n'
              'many = rolling_origin(tickets, forecasters_a, h=H_AHEAD)\nprint("origins:", len(many))\n'
              'display(many.mean().round(2).to_frame("mean MAE over every origin"))\ncheck("A2", (len(many), many["training_mean"].mean()))',
              'forecasters_a = {\n    "naive": lambda past, h: naive(past["tickets_raised"], h),\n'
              '    "training_mean": lambda past, h: np.full(h, past["tickets_raised"].mean()),\n}\n\n'
              'H_AHEAD = 8\n\nassert H_AHEAD is not None, "✍️ Fill in H_AHEAD first."\n'
              'many = rolling_origin(tickets, forecasters_a, h=H_AHEAD)\nprint("origins:", len(many))\n'
              'display(many.mean().round(2).to_frame("mean MAE over every origin"))\ncheck("A2", (len(many), many["training_mean"].mean()))'),
        ("md", """▶️ One score per origin. The flat mean's lucky week is in there, but so are all its terrible ones."""),
        ("code", 'assert "many" in globals(), "✍️ Finish A2 first, then run this cell."\n'
                 'ax = many.plot(figsize=(11, 3.6), title="MAE of each 8-week forecast, one point per origin")\n'
                 'ax.set_ylabel("MAE (tickets/week)")\nplt.tight_layout()\nplt.show()'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Walk the regression forward (15 min) 🚶🏾

📖 The code book's walk-forward backtest for the Week 5 Day 3 regression: start halfway through the feature table, **refit** on everything before the cut, forecast the next weeks, score, slide on.

### B1 ✍️ Six folds
The code book slides **4 weeks** at a time and scores **4 weeks** per fold. Fill in `STEP` and `H_FOLD`."""),
        _task('STEP = ___\nH_FOLD = ___\n\nassert STEP is not None and H_FOLD is not None, "✍️ Fill in STEP and H_FOLD first."\n'
              'fold_mae = walk_forward_mae(tickets, make_features, X_COLS, step=STEP, h=H_FOLD)\n\n'
              'feat_all = make_features(tickets)\nn = len(feat_all)\ncuts = list(range(int(n * 0.5), n - H_FOLD, STEP))\n'
              'folds = pd.DataFrame({"fold_start": [feat_all.index[c] for c in cuts], "train_weeks": cuts,\n'
              '                      "regression": fold_mae}).set_index("fold_start")\ndisplay(folds.round(2))\ncheck("B1", fold_mae)',
              'STEP = 4\nH_FOLD = 4\n\nassert STEP is not None and H_FOLD is not None, "✍️ Fill in STEP and H_FOLD first."\n'
              'fold_mae = walk_forward_mae(tickets, make_features, X_COLS, step=STEP, h=H_FOLD)\n\n'
              'feat_all = make_features(tickets)\nn = len(feat_all)\ncuts = list(range(int(n * 0.5), n - H_FOLD, STEP))\n'
              'folds = pd.DataFrame({"fold_start": [feat_all.index[c] for c in cuts], "train_weeks": cuts,\n'
              '                      "regression": fold_mae}).set_index("fold_start")\ndisplay(folds.round(2))\ncheck("B1", fold_mae)'),
        ("md", """### B2 ✍️ The spread, and when it goes wrong
Fill in the **mean** of the six fold MAEs, and the **start date of the worst fold** (`idxmax()` gives the index label of the biggest value)."""),
        _task('assert "folds" in globals(), "✍️ Finish B1 first, then run this cell."\n\nMEAN = ___\nWORST_FOLD = ___\n\n'
              'assert MEAN is not None and WORST_FOLD is not None, "✍️ Fill in MEAN and WORST_FOLD first."\n'
              'print(f"mean {MEAN:.2f} · best fold {fold_mae.min():.2f} · worst fold {fold_mae.max():.2f}, starting {pd.Timestamp(WORST_FOLD):%d %b %Y}")\n'
              'check("B2", (MEAN, WORST_FOLD))',
              'assert "folds" in globals(), "✍️ Finish B1 first, then run this cell."\n\nMEAN = fold_mae.mean()\nWORST_FOLD = folds["regression"].idxmax()\n\n'
              'assert MEAN is not None and WORST_FOLD is not None, "✍️ Fill in MEAN and WORST_FOLD first."\n'
              'print(f"mean {MEAN:.2f} · best fold {fold_mae.min():.2f} · worst fold {fold_mae.max():.2f}, starting {pd.Timestamp(WORST_FOLD):%d %b %Y}")\n'
              'check("B2", (MEAN, WORST_FOLD))'),
        ("md", """▶️ What happened in the worst fold? Look at the weeks around the start of November."""),
        ("code", 'assert "folds" in globals(), "✍️ Finish B1 first, then run this cell."\n'
                 'print(tickets.loc["2025-10-13":"2025-11-17", "tickets_raised"].to_frame()\n'
                 '      .assign(change_from_last_week=lambda t: t["tickets_raised"].diff()))\n'
                 'ax = folds["regression"].plot(kind="bar", color="#0A5DB4", title="Regression MAE by fold")\n'
                 'ax.set_xticklabels([f"{t:%d %b}" for t in folds.index], rotation=0)\nax.set_ylabel("MAE (tickets/week)")\n'
                 'plt.tight_layout()\nplt.show()'),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Same folds for the baselines (15 min) 🥊

📖 A model score means nothing on its own. Score the baselines on **exactly the same weeks**.

The regression gets last week's real count every week, so the fair naive does too: each week's forecast is the week before's real count. That's already a column in the feature table.

### C1 ✍️ One-step naive on every fold
Type the name of the feature-table column that holds **last week's ticket count** (look at `make_features`)."""),
        _task('assert "folds" in globals(), "✍️ Finish Part B first, then run this cell."\n\nNAIVE_COLUMN = ___\n\n'
              'assert NAIVE_COLUMN is not None, "✍️ Fill in NAIVE_COLUMN first."\nrows = []\nfor c in cuts:\n'
              '    te = feat_all.iloc[c:c + 4]\n    rows.append({"fold_start": te.index[0],\n'
              '                 "naive": mae(te[NAIVE_COLUMN], te["target"]),            # last week, one step ahead\n'
              '                 "seasonal_naive": mae(te["tickets_lag52"], te["target"])})  # same week last year\n'
              'folds = folds[["train_weeks", "regression"]].join(pd.DataFrame(rows).set_index("fold_start"))\n'
              'display(folds.round(2))\ncheck("C1", folds["naive"])',
              'assert "folds" in globals(), "✍️ Finish Part B first, then run this cell."\n\nNAIVE_COLUMN = "tickets_lag1"\n\n'
              'assert NAIVE_COLUMN is not None, "✍️ Fill in NAIVE_COLUMN first."\nrows = []\nfor c in cuts:\n'
              '    te = feat_all.iloc[c:c + 4]\n    rows.append({"fold_start": te.index[0],\n'
              '                 "naive": mae(te[NAIVE_COLUMN], te["target"]),            # last week, one step ahead\n'
              '                 "seasonal_naive": mae(te["tickets_lag52"], te["target"])})  # same week last year\n'
              'folds = folds[["train_weeks", "regression"]].join(pd.DataFrame(rows).set_index("fold_start"))\n'
              'display(folds.round(2))\ncheck("C1", folds["naive"])'),
        ("md", """### C2 ✍️ Who wins more folds?
Count the folds where naive's MAE is **smaller** than the regression's. (`(a < b)` gives True/False for each fold; `.sum()` counts the Trues.)"""),
        _task('assert "folds" in globals() and "naive" in folds, "✍️ Finish C1 first, then run this cell."\n\nnaive_wins = ___\n\n'
              'assert naive_wins is not None, "✍️ Fill in naive_wins first."\nprint("naive beats the regression on", int(naive_wins), "of", len(folds), "folds")\n'
              'display(folds[["regression", "naive", "seasonal_naive"]].mean().round(2).to_frame("mean MAE"))\ncheck("C2", naive_wins)',
              'assert "folds" in globals() and "naive" in folds, "✍️ Finish C1 first, then run this cell."\n\nnaive_wins = int((folds["naive"] < folds["regression"]).sum())\n\n'
              'assert naive_wins is not None, "✍️ Fill in naive_wins first."\nprint("naive beats the regression on", int(naive_wins), "of", len(folds), "folds")\n'
              'display(folds[["regression", "naive", "seasonal_naive"]].mean().round(2).to_frame("mean MAE"))\ncheck("C2", naive_wins)'),
        ("md", """### C3 ✍️ Add the rate forecast (blind!)
📖 Week 5 Day 2's trick: last year's tickets **per terminal** × today's terminals. Here it stands at the **start** of each fold and forecasts the whole fold in one go: no peeking at any week inside the fold.

✍️ How many weeks must it forecast, from the start of a fold? Fill in `RATE_H`."""),
        _task('assert "folds" in globals() and "naive" in folds, "✍️ Finish C1 first, then run this cell."\n\nRATE_H = ___\n\n'
              'assert RATE_H is not None, "✍️ Fill in RATE_H first."\nrate_col = []\nfor c in cuts:\n'
              '    o = tickets.index.get_loc(feat_all.index[c])          # the origin: the first week of the fold\n'
              '    past = tickets.iloc[:o]                                 # only the weeks BEFORE it\n'
              '    f = rate_seasonal_naive(past["tickets_raised"], past["active_vsat_terminals"], RATE_H)\n'
              '    rate_col.append(mae(f, feat_all["target"].iloc[c:c + 4]))\n'
              'folds["rate_seasonal_naive"] = rate_col\ndisplay(folds.round(2))\n'
              'display(folds.drop(columns="train_weeks").mean().round(2).to_frame("mean MAE"))\n'
              'check("C3", (folds["rate_seasonal_naive"].mean(), folds["rate_seasonal_naive"].loc[WORST_FOLD]))',
              'assert "folds" in globals() and "naive" in folds, "✍️ Finish C1 first, then run this cell."\n\nRATE_H = 4\n\n'
              'assert RATE_H is not None, "✍️ Fill in RATE_H first."\nrate_col = []\nfor c in cuts:\n'
              '    o = tickets.index.get_loc(feat_all.index[c])          # the origin: the first week of the fold\n'
              '    past = tickets.iloc[:o]                                 # only the weeks BEFORE it\n'
              '    f = rate_seasonal_naive(past["tickets_raised"], past["active_vsat_terminals"], RATE_H)\n'
              '    rate_col.append(mae(f, feat_all["target"].iloc[c:c + 4]))\n'
              'folds["rate_seasonal_naive"] = rate_col\ndisplay(folds.round(2))\n'
              'display(folds.drop(columns="train_weeks").mean().round(2).to_frame("mean MAE"))\n'
              'check("C3", (folds["rate_seasonal_naive"].mean(), folds["rate_seasonal_naive"].loc[WORST_FOLD]))'),

        # ---------------- PART D ----------------
        ("md", """---
# Part D: Every origin, three horizons (15 min) 🔭

📖 Next week's shift and next month's roster are different questions. Stand at **every** week, and forecast **1**, **4** and **8** weeks ahead with every blind baseline.

### D1 ✍️ The horizons
Fill in `HORIZONS` as a list of the three horizons, in weeks. (It runs about 250 small forecasts per horizon: a few seconds.)"""),
        _task(forecasters_code + '\nHORIZONS = ___\n\nassert HORIZONS is not None, "✍️ Fill in HORIZONS first."\n' + d1_tail,
              forecasters_code + '\nHORIZONS = [1, 4, 8]\n\nassert HORIZONS is not None, "✍️ Fill in HORIZONS first."\n' + d1_tail),
        ("md", """▶️ Draw it: how does each method's error change as you look further ahead?"""),
        ("code", 'assert "summary" in globals(), "✍️ Finish D1 first, then run this cell."\n'
                 'ax = summary.drop(columns=["seasonal_naive"]).plot(marker="o", figsize=(9, 4),\n'
                 '                                                    title="Mean MAE by horizon (seasonal naive is off the chart)")\n'
                 'ax.set_xticks(HORIZONS)\nax.set_xlabel("weeks ahead")\nax.set_ylabel("mean MAE (tickets/week)")\nplt.tight_layout()\nplt.show()\n\n'
                 'print("How many origins did each method win (lowest MAE), 1 week ahead?")\nprint(by_h[1].idxmin(axis=1).value_counts().to_string())'),
        ("md", """### D2 ✍️ The best method at each horizon
Which method has the **lowest** mean MAE **1 week** ahead, and which **8 weeks** ahead? (`summary.loc[1]` is the 1-week row; `.idxmin()` gives the name of its smallest value.)"""),
        _task('assert "summary" in globals(), "✍️ Finish D1 first, then run this cell."\n\nBEST_1 = ___\nBEST_8 = ___\n\n'
              'assert BEST_1 is not None and BEST_8 is not None, "✍️ Fill in BEST_1 and BEST_8 first."\n'
              'print("1 week ahead :", BEST_1, f"({summary.loc[1, BEST_1]:.2f})")\nprint("8 weeks ahead:", BEST_8, f"({summary.loc[8, BEST_8]:.2f})")\n'
              'check("D2", (BEST_1, BEST_8))',
              'assert "summary" in globals(), "✍️ Finish D1 first, then run this cell."\n\nBEST_1 = summary.loc[1].idxmin()\nBEST_8 = summary.loc[8].idxmin()\n\n'
              'assert BEST_1 is not None and BEST_8 is not None, "✍️ Fill in BEST_1 and BEST_8 first."\n'
              'print("1 week ahead :", BEST_1, f"({summary.loc[1, BEST_1]:.2f})")\nprint("8 weeks ahead:", BEST_8, f"({summary.loc[8, BEST_8]:.2f})")\n'
              'check("D2", (BEST_1, BEST_8))'),

        # ---------------- PART E ----------------
        ("md", """---
# Part E: The verdict (10 min) 📝

### E1 ✍️ The month-ahead roster
The NOC plans staff shifts **4 weeks** ahead. Which forecast should they use?

| # | Method |
|---|---|
| 1 | Naive: "same as last week" |
| 2 | Seasonal naive: "same week last year" |
| 3 | The Week 5 Day 3 regression |
| 4 | Rate seasonal naive: last year's tickets per terminal × today's terminals |

Remember: the regression needs **last week's real count** as a feature."""),
        _task('ROSTER_PICK = ___\n\ncheck("E1", ROSTER_PICK)', 'ROSTER_PICK = 4\n\ncheck("E1", ROSTER_PICK)'),
        ("md", """### E2 ✍️ Your 4-sentence recommendation (no check: your trainer reads it)
Write it for the NOC manager, in plain words:
1. What to use for **next week**, with its typical error.
2. What to use for the **month-ahead roster**, with its typical error.
3. What **not** to use, and why.
4. **When** to expect the biggest misses."""),
        _task('RECOMMENDATION = """\n1. ___\n2. ___\n3. ___\n4. ___\n"""\nprint(RECOMMENDATION)',
              f'RECOMMENDATION = """\n'
              f'1. For next week, use naive ("same as last week"): it is usually off by about {hz[1]["mean"]["naive"]:.1f} tickets; the rate forecast ties it ({hz[1]["mean"]["rate_seasonal_naive"]:.1f}).\n'
              f'2. For the month-ahead roster, use last year\'s tickets per terminal x today\'s terminals: about {hz[4]["mean"]["rate_seasonal_naive"]:.1f} tickets off 4 weeks out, against {hz[4]["mean"]["naive"]:.1f} for naive.\n'
              f'3. Don\'t use the regression: it loses to naive on {F["naive_beats_reg"]} of 6 backtest folds and cannot forecast more than one week ahead.\n'
              f'4. Expect the biggest misses when the rains start (early April) or stop (early November): add staff margin then.\n"""\nprint(RECOMMENDATION)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: refit every week
*"The regression lost because you only refitted every 4 weeks!"* Fair question. Refit it **every week** and forecast **one week** at a time, on the same stretch of weeks, then compare with naive and the rate forecast on exactly those weeks.

✍️ Fill in `STEP_EVERY` (how many weeks between refits?)."""),
        _task('assert "by_h" in globals(), "✍️ Finish Part D first, then run this cell."\n\nSTEP_EVERY = ___\n\n'
              'assert STEP_EVERY is not None, "✍️ Fill in STEP_EVERY first."\n'
              'weekly = walk_forward_mae(tickets, make_features, X_COLS, step=STEP_EVERY, h=1)\n'
              'weeks = feat_all.index[int(n * 0.5): int(n * 0.5) + len(weekly)]\n'
              'same_weeks = pd.DataFrame({"regression": weekly,\n'
              '                           "naive": (feat_all.loc[weeks, "tickets_lag1"] - feat_all.loc[weeks, "target"]).abs().values,\n'
              '                           "rate_seasonal_naive": by_h[1].loc[weeks, "rate_seasonal_naive"].values}, index=weeks)\n'
              'print(len(weeks), "weeks,", f"{weeks[0]:%d %b} to {weeks[-1]:%d %b %Y}")\n'
              'display(same_weeks.mean().round(2).to_frame("mean MAE, 1 week ahead"))\n'
              'print("weeks the regression beats naive:", int((same_weeks["regression"] < same_weeks["naive"]).sum()))\n'
              'check("BONUS", weekly.mean())',
              'assert "by_h" in globals(), "✍️ Finish Part D first, then run this cell."\n\nSTEP_EVERY = 1\n\n'
              'assert STEP_EVERY is not None, "✍️ Fill in STEP_EVERY first."\n'
              'weekly = walk_forward_mae(tickets, make_features, X_COLS, step=STEP_EVERY, h=1)\n'
              'weeks = feat_all.index[int(n * 0.5): int(n * 0.5) + len(weekly)]\n'
              'same_weeks = pd.DataFrame({"regression": weekly,\n'
              '                           "naive": (feat_all.loc[weeks, "tickets_lag1"] - feat_all.loc[weeks, "target"]).abs().values,\n'
              '                           "rate_seasonal_naive": by_h[1].loc[weeks, "rate_seasonal_naive"].values}, index=weeks)\n'
              'print(len(weeks), "weeks,", f"{weeks[0]:%d %b} to {weeks[-1]:%d %b %Y}")\n'
              'display(same_weeks.mean().round(2).to_frame("mean MAE, 1 week ahead"))\n'
              'print("weeks the regression beats naive:", int((same_weeks["regression"] < same_weeks["naive"]).sum()))\n'
              'check("BONUS", weekly.mean())'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", f"""### 📝 What you learned today
- **One split is one screenshot.** On the last 8 weeks a flat average scored {F['training_mean_mae']:.2f} and beat four real baselines; over {hz[8]['n']} origins it was the worst ({hz[8]['mean']['training_mean']:.2f}).
- **Walk forward:** refit on the past only, forecast the next weeks, score, slide on. The regression's six folds ran from {F['folds']['regression'].min():.2f} to {F['folds']['regression'].max():.2f}: report the **spread** and **when** it fails (the season change).
- **Same folds, same scorer, every method.** One-step naive beat the regression on {F['naive_beats_reg']} of 6 folds. The rate forecast, blind for 4 weeks, had the lowest mean ({F['fold_means']['rate_seasonal_naive']:.2f}).
- **The horizon decides.** 1 week ahead: naive and the rate forecast tie. 4 and 8 weeks ahead: the rate forecast wins easily. The regression can't go past 1 week at all.
- **Fix the backtest design before you look.** Refitting every week instead of every 4 moves the regression to a near tie with naive.
- **Recommend the simpler model** when it wins or ties, in four plain sentences.

**Next time:** *When will it break?* Remaining useful life for the satellite's battery, amplifier and fuel, and a backtest of a battery call. Then **Quiz 4**. 🔋

<sub>Data: synthetic teaching dataset from the original Week 6 code book (`Time-series/week-06`). Safe to use with AI tools; real NIGCOMSAT data is not.</sub>"""),
    ]
