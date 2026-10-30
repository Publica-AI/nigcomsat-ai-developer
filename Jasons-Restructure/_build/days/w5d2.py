"""Week 5 · Day 2: Forecasting Baselines."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from common import BRAND as B
from webdeck import logos_title_block
from w6forecast import BASELINE_CODE, H, PERIOD, exp_smoothing, facts, load, mae

CODE = "W5D2"
TITLE = "Forecasting Baselines"

GRID, AXIS = "#24384F", "#9DB0C6"
RED, GOLD, GREEN, WHITE = "#FF6B6F", "#F5B83D", "#3CCB7F", "#EAF2FB"
BASE4 = ["naive", "seasonal_naive", "moving_average", "exp_smoothing"]
NICE = {"naive": "Naive", "seasonal_naive": "Seasonal naive", "moving_average": "Moving average (8)",
        "exp_smoothing": "Exp. smoothing (α 0.3)", "rate_seasonal_naive": "Rate seasonal naive", "training_mean": "Flat training average"}
SHORT = {"naive": "Naive", "seasonal_naive": "Seasonal naive", "moving_average": "Moving avg", "exp_smoothing": "Smoothing",
         "rate_seasonal_naive": "Rate seas. naive", "training_mean": "Flat average"}
COL = {"naive": B["blue_d"], "seasonal_naive": RED, "moving_average": "#B58CFF", "exp_smoothing": B["teal_d"],
       "rate_seasonal_naive": GREEN, "training_mean": GOLD}


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# =============================================================================
# THE NOTEBOOK CODE: BASELINE_CODE from w6forecast, cut into its functions
# =============================================================================
def _blocks():
    parts = BASELINE_CODE.split("\n\ndef ")
    blocks = [parts[0]] + ["def " + p for p in parts[1:]]
    out = {b.split("(")[0][4:]: b for b in blocks}
    assert "\n\n".join(out.values()) == BASELINE_CODE
    return out


FN = _blocks()


def _blank(name, old):
    """The participants' version of one function: `old` replaced by ___ (fails loudly if the shared code changes)."""
    src = FN[name]
    assert src.count(old) == 1, (name, old)
    return src.replace(old, "___")


# =============================================================================
# EXTRA NUMBERS FOR TODAY (same shared functions, so same code as the notebook)
# =============================================================================
@lru_cache(maxsize=1)
def day_facts():
    F = facts()
    tickets, _, _ = load()
    y, term = tickets["tickets_raised"], tickets["active_vsat_terminals"]
    train, actual = y.iloc[:-H], y.iloc[-H:]
    tterm = term.iloc[:-H]
    fc = F["fc"]
    D = {"y": y, "term": term, "train": train, "actual": actual, "tterm": tterm}
    D["naive_err"] = (fc["naive"] - actual.values).abs().astype(int).tolist()
    D["naive_value"] = float(fc["naive"].iloc[0])
    D["ma_value"] = float(fc["moving_average"].iloc[0])
    D["es_value"] = float(fc["exp_smoothing"].iloc[0])
    D["sn_weeks"] = (train.index[-PERIOD], train.index[-PERIOD + H - 1])
    D["sn_terms"] = (int(tterm.iloc[-PERIOD]), int(tterm.iloc[-PERIOD + H - 1]))
    D["growth"] = F["term_origin"] / F["term_year_before"]
    # the rate forecast for the first test week, as one sum
    D["ly_tickets"], D["ly_terms"], D["now_terms"] = int(train.iloc[-PERIOD]), int(tterm.iloc[-PERIOD]), int(tterm.iloc[-1])
    D["ly_rate"] = D["ly_tickets"] / D["ly_terms"] * 1000
    D["rate_w1"] = float(fc["rate_seasonal_naive"].iloc[0])
    D["times_better"] = F["baseline_mae"]["naive"] / F["baseline_mae"]["rate_seasonal_naive"]
    D["rate_err"] = (fc["rate_seasonal_naive"] - actual.values).abs().tolist()
    rb = F["rate_by_month"]
    D["year_gap"] = float((rb[2025] - rb[2024]).abs().max())
    D["year_gap_month"] = int((rb[2025] - rb[2024]).abs().idxmax())
    # alpha stretch: what the test weeks would "say" (we look only to show why you mustn't choose this way)
    D["alpha"] = {a: (float(exp_smoothing(train, H, a)[0]), mae(exp_smoothing(train, H, a), actual)) for a in (0.1, 0.3, 0.9)}
    D["actual_mean"] = float(actual.mean())
    D["train_mean"] = float(train.mean())
    D["naive_over_all"] = bool((fc["naive"].values > actual.values).all())
    return D


def _fmt_date(t):
    return f"{t.day} {t:%b %Y}"


# =============================================================================
# LOCAL SVG HELPERS (viewBox + width 100%, so they never overflow a card)
# =============================================================================
def _axes(w, h, L, R, T, Bm, lo, hi, ticks):
    def Y(v):
        return Bm - (v - lo) / (hi - lo) * (Bm - T)
    o = []
    for v in ticks:
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L - 12}" y="{Y(v) + 7:.1f}" fill="{AXIS}" font-size="19" text-anchor="end">{v}</text>')
    return Y, o


def series_svg(D, w=1420, h=430, rainy=False, steps=None):
    """The 96 training weeks of tickets (+ terminals on a second scale), the last 8 weeks locked away."""
    y, term = D["y"].values.astype(float), D["term"].values.astype(float)
    n = len(y)
    L, R, T, Bm = 70, w - 110, 24, h - 52
    X = lambda i: L + i / (n - 1) * (R - L)       # noqa: E731
    Y, o = _axes(w, h, L, R, T, Bm, 20, 85, (20, 40, 60, 80))
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">'] + o
    idx = D["y"].index
    if rainy:
        for yr in (2024, 2025):
            i0 = idx.get_indexer([pd.Timestamp(f"{yr}-04-01")], method="bfill")[0]
            i1 = idx.get_indexer([pd.Timestamp(f"{yr}-10-31")], method="ffill")[0]
            o.append(f'<rect class="anim a-fade" style="--d:.2s" x="{X(i0):.1f}" y="{T}" width="{X(i1) - X(i0):.1f}" height="{Bm - T}" fill="{B["blue_d"]}" fill-opacity=".14" rx="8"/>')
            o.append(f'<text class="anim a-fade" style="--d:.3s" x="{(X(i0) + X(i1)) / 2:.1f}" y="{Bm - 14}" fill="#9CC7F5" font-size="21" font-weight="800" text-anchor="middle">🌧️ rainy season {yr}</text>')
    nt = n - H
    # locked box over the hold-out
    o.append(f'<rect class="anim a-pop" style="--d:1.9s;transform-origin:{(X(nt) + X(n - 1)) / 2:.0f}px {(T + Bm) / 2:.0f}px" x="{X(nt) - 6:.1f}" y="{T}" '
             f'width="{X(n - 1) - X(nt) + 12:.1f}" height="{Bm - T}" fill="{GOLD}" fill-opacity=".16" stroke="{GOLD}" stroke-width="2.5" stroke-dasharray="9 7" rx="8"/>')
    o.append(f'<text class="anim a-fade" style="--d:2.1s" x="{(X(nt) + X(n - 1)) / 2:.1f}" y="{(T + Bm) / 2 + 14:.1f}" font-size="44" text-anchor="middle">🔒</text>')
    # terminals on its own scale (1,000 to 2,300), thin teal line
    tY = lambda v: Bm - (v - 1000) / (2300 - 1000) * (Bm - T)     # noqa: E731
    td = "M" + " L".join(f"{X(i):.1f},{tY(term[i]):.1f}" for i in range(nt))
    o.append(f'<path class="draw" style="--d:.5s;--dur:2.2s" d="{td}" fill="none" stroke="{B["teal_d"]}" stroke-width="3"/>')
    o.append(f'<text class="anim a-fade" style="--d:2.4s" x="{X(nt - 1) - 8:.1f}" y="{tY(term[nt - 1]) + 74:.1f}" fill="{B["teal_d"]}" font-size="20" font-weight="800" text-anchor="end">{int(term[nt - 1]):,} terminals</text>')
    o.append(f'<text class="anim a-fade" style="--d:2.4s" x="{X(0) + 8:.1f}" y="{tY(term[0]) + 28:.1f}" fill="{B["teal_d"]}" font-size="20" font-weight="800">{int(term[0]):,} terminals</text>')
    d = "M" + " L".join(f"{X(i):.1f},{Y(y[i]):.1f}" for i in range(nt))
    o.append(f'<path d="{d} L{X(nt - 1):.1f},{Bm} L{X(0):.1f},{Bm} Z" fill="{B["blue_d"]}" fill-opacity=".10" class="anim a-fade" style="--d:1.4s"/>')
    o.append(f'<path class="draw" style="--d:.3s;--dur:2.4s" d="{d}" fill="none" stroke="{B["blue_d"]}" stroke-width="4" stroke-linejoin="round"/>')
    for k, (date, lab) in enumerate((steps or {}).items()):
        i = idx.get_loc(pd.Timestamp(date))
        col = RED if lab.startswith("−") else GREEN
        o.append(f'<g class="anim a-pop" style="--d:{2.6 + .3 * k:.1f}s;transform-origin:{X(i):.0f}px {Y(y[i]):.0f}px">'
                 f'<circle cx="{X(i):.1f}" cy="{Y(y[i]):.1f}" r="10" fill="{col}" stroke="{B["space"]}" stroke-width="3"/>'
                 f'<text x="{X(i) + 14:.1f}" y="{Y(y[i]) + (36 if lab.startswith("−") else -16):.1f}" fill="{col}" font-size="26" font-weight="800">{lab}</text></g>')
    for yr in (2024, 2025):
        i = idx.get_loc(pd.Timestamp(f"{yr}-01-01") if yr == 2024 else idx[idx.year == 2025][0])
        o.append(f'<text x="{X(i):.1f}" y="{h - 14}" fill="{AXIS}" font-size="20">Jan {yr}</text>')
    o.append(f'<text x="{X(nt):.1f}" y="{h - 14}" fill="{GOLD}" font-size="20" font-weight="700">3 Nov</text>')
    o.append(f'<text x="{L - 12}" y="{T - 4}" fill="{AXIS}" font-size="18" text-anchor="end">tickets</text>')
    o.append("</svg>")
    return "".join(o)


def split_svg(w=1420, h=150):
    """96 training weeks | 8 locked test weeks, one square each."""
    n, gap = 104, 2.2
    cell = (w - 40 - gap * (n - 1)) / n
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for i in range(n):
        x = 20 + i * (cell + gap)
        col = GOLD if i >= n - H else B["blue_d"]
        o.append(f'<rect class="anim a-pop" style="--d:{.2 + i * .012:.2f}s;transform-origin:{x + cell / 2:.0f}px 60px" x="{x:.1f}" y="30" width="{cell:.1f}" height="60" rx="2.5" fill="{col}"/>')
    o.append(f'<text x="20" y="128" fill="{B["blue_d"]}" font-size="24" font-weight="800">🏋🏾 96 training weeks · 1 Jan 2024 – 27 Oct 2025</text>')
    o.append(f'<text x="{w - 20}" y="128" fill="{GOLD}" font-size="24" font-weight="800" text-anchor="end">🔒 8 test weeks</text>')
    o.append("</svg>")
    return "".join(o)


def forecast_svg(D, F, names, w=1420, h=440, tail=20, labels=True):
    """The last `tail` training weeks, then the 8 test weeks: actual (white) and each forecast (coloured)."""
    y = D["y"].values.astype(float)
    n = len(y)
    s = n - H - tail
    L, R, T, Bm = 70, w - (310 if labels else 40), 24, h - 52
    X = lambda i: L + (i - s) / (n - 1 - s) * (R - L)     # noqa: E731
    Y, o = _axes(w, h, L, R, T, Bm, 35, 85, (40, 50, 60, 70, 80))
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">'] + o
    nt = n - H
    o.append(f'<rect x="{X(nt) - 10:.1f}" y="{T}" width="{X(n - 1) - X(nt) + 20:.1f}" height="{Bm - T}" fill="{GOLD}" fill-opacity=".08" rx="8"/>')
    o.append(f'<text x="{(X(nt) + X(n - 1)) / 2:.1f}" y="{h - 14}" fill="{GOLD}" font-size="20" font-weight="700" text-anchor="middle">the 8 test weeks · 3 Nov – 22 Dec 2025</text>')
    o.append(f'<text x="{X(s):.1f}" y="{h - 14}" fill="{AXIS}" font-size="20">{D["y"].index[s]:%d %b}</text>')
    d = "M" + " L".join(f"{X(i):.1f},{Y(y[i]):.1f}" for i in range(s, nt))
    o.append(f'<path class="draw" style="--d:.2s;--dur:1.2s" d="{d}" fill="none" stroke="{B["blue_d"]}" stroke-width="4" stroke-linejoin="round"/>')
    used = []
    for k, nm in enumerate(names):
        v = F["fc"][nm].values
        dd = f"M{X(nt - 1):.1f},{Y(y[nt - 1]):.1f} " + " L".join(f"{X(nt + i):.1f},{Y(v[i]):.1f}" for i in range(H))
        dl = 1.3 + .45 * k
        o.append(f'<path class="draw" style="--d:{dl:.2f}s;--dur:.9s" d="{dd}" fill="none" stroke="{COL[nm]}" stroke-width="4.5" stroke-dasharray="12 7" stroke-linejoin="round"/>')
        if labels:
            ly = Y(v[-1]) + 8
            while any(abs(ly - u) < 30 for u in used):
                ly += 30
            used.append(ly)
            o.append(f'<text class="anim a-fade" style="--d:{dl + .5:.2f}s" x="{R + 18:.1f}" y="{ly:.1f}" fill="{COL[nm]}" font-size="22" font-weight="800">'
                     f'{SHORT[nm]} · {F["baseline_mae"][nm]:.2f}</text>')
    da = f"M{X(nt - 1):.1f},{Y(y[nt - 1]):.1f} " + " L".join(f"{X(i):.1f},{Y(y[i]):.1f}" for i in range(nt, n))
    dl = 1.3 + .45 * len(names) + .2
    o.append(f'<path class="draw" style="--d:{dl:.2f}s;--dur:1s" d="{da}" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linejoin="round"/>')
    for i in range(nt, n):
        o.append(f'<circle class="anim a-pop" style="--d:{dl + .1 * (i - nt):.2f}s;transform-origin:{X(i):.0f}px {Y(y[i]):.0f}px" cx="{X(i):.1f}" cy="{Y(y[i]):.1f}" r="7" fill="{WHITE}"/>')
    if labels:
        o.append(f'<text class="anim a-fade" style="--d:{dl + .6:.2f}s" x="{X(nt) - 16:.1f}" y="{Y(y[nt]) + 8:.1f}" fill="{WHITE}" font-size="22" font-weight="800" text-anchor="end">actual</text>')
    o.append("</svg>")
    return "".join(o)


def errors_svg(D, F, w=1420, h=380):
    """Naive's 8 misses: the flat forecast, the actual dots and a red stick for each error."""
    a = D["actual"].values.astype(float)
    v = F["fc"]["naive"].values
    L, R, T, Bm = 70, w - 40, 24, h - 56
    X = lambda i: L + 40 + i / (H - 1) * (R - L - 80)     # noqa: E731
    Y, o = _axes(w, h, L, R, T, Bm, 45, 80, (50, 60, 70, 80))
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">'] + o
    o.append(f'<line class="draw" style="--d:.2s;--dur:.8s" x1="{X(0) - 30:.1f}" x2="{X(H - 1) + 30:.1f}" y1="{Y(v[0]):.1f}" y2="{Y(v[0]):.1f}" stroke="{B["blue_d"]}" stroke-width="5" stroke-dasharray="12 7"/>')
    o.append(f'<text class="anim a-fade" style="--d:.6s" x="{X(0) - 30:.1f}" y="{Y(v[0]) - 14:.1f}" fill="{B["blue_d"]}" font-size="22" font-weight="800">naive says {v[0]:.0f}, every week</text>')
    for i in range(H):
        d = .8 + i * .22
        o.append(f'<line class="anim a-fade" style="--d:{d:.2f}s" x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{Y(v[i]):.1f}" y2="{Y(a[i]):.1f}" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>')
        o.append(f'<circle class="anim a-pop" style="--d:{d:.2f}s;transform-origin:{X(i):.0f}px {Y(a[i]):.0f}px" cx="{X(i):.1f}" cy="{Y(a[i]):.1f}" r="9" fill="{WHITE}"/>')
        o.append(f'<text class="anim a-fade" style="--d:{d + .1:.2f}s" x="{X(i):.1f}" y="{Y(a[i]) + 36:.1f}" fill="{RED}" font-size="26" font-weight="800" text-anchor="middle">{abs(v[i] - a[i]):.0f}</text>')
        o.append(f'<text x="{X(i):.1f}" y="{h - 16}" fill="{AXIS}" font-size="19" text-anchor="middle">{D["actual"].index[i]:%d %b}</text>')
    o.append("</svg>")
    return "".join(o)


def rate_bars_svg(F, w=1420, h=420):
    """Tickets per 1,000 terminals, month by month: 2024 next to 2025 (training weeks only)."""
    rb = F["rate_by_month"]
    L, R, T, Bm = 70, w - 20, 30, h - 56
    Y, o = _axes(w, h, L, R, T, Bm, 0, 46, (0, 10, 20, 30, 40))
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">'] + o
    slot = (R - L) / 12
    bw = slot * .36
    for m in range(1, 13):
        x0 = L + (m - 1) * slot + slot * .1
        rainy = 4 <= m <= 10
        if rainy:
            o.append(f'<rect x="{L + (m - 1) * slot:.1f}" y="{T}" width="{slot:.1f}" height="{Bm - T}" fill="{B["blue_d"]}" fill-opacity=".07"/>')
        for j, yr in enumerate((2024, 2025)):
            val = rb.loc[m, yr]
            x = x0 + j * (bw + 4)
            d = .2 + (m - 1) * .1 + j * .05
            if val != val:
                o.append(f'<text class="anim a-fade" style="--d:{d:.2f}s" x="{x + bw / 2:.1f}" y="{Bm - 14}" font-size="30" text-anchor="middle">🔒</text>')
                continue
            col = B["blue_d"] if yr == 2024 else B["teal_d"]
            o.append(f'<g class="anim" style="--d:{d:.2f}s"><rect x="{x:.1f}" y="{Y(val):.1f}" width="{bw:.1f}" height="{Bm - Y(val):.1f}" rx="5" fill="{col}"/>'
                     f'<text x="{x + bw / 2:.1f}" y="{Y(val) - 9:.1f}" fill="{WHITE}" font-size="15" font-weight="800" text-anchor="middle">{val:.1f}</text></g>')
        o.append(f'<text x="{L + (m - .5) * slot:.1f}" y="{h - 18}" fill="{AXIS}" font-size="21" text-anchor="middle">{pd.Timestamp(2025, m, 1):%b}</text>')
    o.append(f'<text x="{L + 8}" y="{T + 4}" fill="{B["blue_d"]}" font-size="21" font-weight="800">▇ 2024</text>'
             f'<text x="{L + 110}" y="{T + 4}" fill="{B["teal_d"]}" font-size="21" font-weight="800">▇ 2025</text>')
    o.append("</svg>")
    return "".join(o)


def hbars_svg(rows, top, w=1420):
    """rows: [(label, value, colour)] as horizontal bars, longest = `top`. Shorter is better here."""
    L, R, rh = 520, w - 150, 66
    h = len(rows) * rh + 10
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for k, (lab, v, col) in enumerate(rows):
        y = k * rh + 8
        bw = max(v / top * (R - L), 3)
        d = .3 + k * .25
        o.append(f'<g class="anim a-left" style="--d:{d:.2f}s"><text x="0" y="{y + 33}" fill="{WHITE}" font-size="25" font-weight="700">{lab}</text>'
                 f'<rect x="{L}" y="{y + 6}" width="{R - L}" height="40" rx="8" fill="#12233A"/>'
                 f'<rect x="{L}" y="{y + 6}" width="{bw:.1f}" height="40" rx="8" fill="{col}"/>'
                 f'<text x="{L + bw + 14:.1f}" y="{y + 36}" fill="{col}" font-size="28" font-weight="800">{v:.2f}</text></g>')
    o.append("</svg>")
    return "".join(o)


TABLE_CSS = ("<style>.sb{width:100%;border-collapse:separate;border-spacing:0 6px;font-size:23px}"
             ".sb th{color:#9DB0C6;font-size:18px;text-align:left;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:0 14px}"
             ".sb td{background:#12233A;padding:9px 14px}.sb td:first-child{border-radius:14px 0 0 14px}"
             ".sb td:last-child{border-radius:0 14px 14px 0}.sb tr.win td{background:#123A33}</style>")


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    F = facts()
    D = day_facts()
    M = F["baseline_mae"]
    st = F["season_steps"]
    rb = F["rate_by_month"]
    lw, lv = F["last_train_week"]
    sn0, sn1 = D["sn_weeks"]
    ranked = sorted(BASE4, key=lambda k: M[k])
    worst = ranked[-1]
    a0 = int(D["actual"].iloc[0])

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:80px;top:150px;width:520px;height:560px">
  <svg viewBox="0 0 520 560" width="520" height="560">
    <circle cx="260" cy="270" r="230" fill="#12233A" class="anim a-pop" style="--d:.2s;transform-origin:260px 270px"/>
    <text x="260" y="330" font-size="230" text-anchor="middle" class="anim a-pop" style="--d:.5s;transform-origin:260px 260px">👵🏾</text>
    <g class="anim a-pop" style="--d:1.1s;transform-origin:400px 100px"><rect x="270" y="40" width="250" height="104" rx="24" fill="#F5B83D"/>
    <text x="395" y="84" font-size="24" font-weight="800" fill="#0B1622" text-anchor="middle">Tomorrow go be</text>
    <text x="395" y="120" font-size="24" font-weight="800" fill="#0B1622" text-anchor="middle">like today. 🙂</text></g>
    <path class="draw" style="--d:1.6s;--dur:1.2s" d="M60 500 L140 470 L220 480 L300 440 L380 450 L460 410" stroke="#3B8BE0" stroke-width="8" fill="none" stroke-linecap="round"/>
    <path class="draw" style="--d:2.6s;--dur:.6s" d="M460 410 L500 410" stroke="#F5B83D" stroke-width="8" stroke-dasharray="12 8" fill="none"/>
  </svg></div>
<div style="max-width:880px;margin-top:40px">
  <div class="kicker anim">Week 5 · Day 2</div>
  <h1 class="anim" style="--d:.2s">Forecasting<br><span class="hl">Baselines</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Grandma's forecast: “tomorrow will be like today.”<br>She's harder to beat than you think. 👵🏾</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex">{logos_title_block()}</div>
</div>""",
          "Welcome to the forecasting half of the course. Weeks 3 to 5 asked 'is this reading wrong right now?'. From today we ask 'what happens next?'. "
          "And before any fancy model, we meet the simplest forecasts there are: the baselines."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Beat Grandma. Then set the bar.</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:270px;padding:40px 22px"><div class="icon">🧾</div><h3>Meet the series</h3><p class="small">trend · season · noise</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:270px;padding:40px 22px"><div class="icon">👵🏾</div><h3>Four baselines</h3><p class="small">the cheapest forecasts</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:270px;padding:40px 22px"><div class="icon">📏</div><h3>Score them</h3><p class="small">MAE, in tickets</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:270px;padding:40px 22px"><div class="icon">➗</div><h3>Divide by size</h3><p class="small">the trick that wins</p></div>
</div>
<div class="row anim" style="--d:1.8s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up</span>
</div>""",
          "Four moves. The last one is the surprise of the day: a two-line forecast that beats everything in the original code book."),

        # 3 ─ hook
        S("""
<div class="kicker anim">Quick question</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Who forecasts next week's NOC tickets? 🧾</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">👵🏾</div><h3>Grandma</h3>
    <p class="muted">“How many tickets tomorrow? The same as today, my child.” No laptop. No model. Fifty years of being right.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill teal">free</span><span class="pill">one line of code</span></div></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">🧑🏾‍💼</div><h3>The consultant</h3>
    <p class="muted">Big slides, a machine-learning model, a ₦25 million invoice. “Our AI forecasts tickets.”</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill gold">expensive</span><span class="pill bad">never compared</span></div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:26px;text-align:center">If the AI can't beat Grandma, the invoice is for nothing.<br>Grandma's forecast has a name: a <b class="hl">baseline</b>. 👵🏾</p>""",
          "Let the room enjoy it. Everybody has a grandma who forecasts like this. The point: a forecast only has value if it beats the cheap, obvious one. "
          "Today we build four cheap ones, score them honestly, and find the one every later model must beat."),

        # 4 ─ from now to next
        S("""
<div class="kicker anim">A new question for the last two weeks</div>
<h2 class="anim" style="--d:.1s;font-size:54px">From “is it wrong now?” to “what comes next?”</h2>
<div class="row" style="gap:40px;margin-top:30px">
  <div class="card anim a-left" style="--d:.3s;flex:1"><div class="icon">🚨</div><h3>Weeks 3–5: detection</h3>
    <p class="muted">Look at a reading that already happened. Is it normal? Control charts, CUSUM, the forest.</p></div>
  <div class="card anim a-right glow" style="--d:.6s;flex:1"><div class="icon">🔮</div><h3>Weeks 5–6: forecasting</h3>
    <p class="muted">Guess a reading that <b style="color:#fff">hasn't happened yet</b>. How many tickets next week? When will the battery reach its limit?</p></div>
</div>
<div class="card anim" style="--d:1s;margin-top:30px;padding:22px 30px;text-align:center">
  <p style="font-size:32px">A forecast is a guess about the future made <b class="hl">only from the past</b>.<br><span class="small">If your forecast secretly used next week's number, it's not a forecast. It's expo. 🙅🏾</span></p></div>""",
          "Connect to W5D1: the no-expo rule matters even more for forecasting, because the whole job is to guess what you can't see yet."),

        # 5 ─ the data
        S(f"""
<div class="kicker anim">ops_tickets_weekly · Week 6 data folder</div>
<h2 class="anim" style="--d:.1s;font-size:54px">NOC tickets, every week for two years</h2>
<div class="card anim" style="--d:.2s;padding:20px 24px">{series_svg(D)}</div>
<div class="row anim" style="--d:2.4s;gap:16px;margin-top:18px;justify-content:center">
  <span class="pill">📅 {F["n_weeks"]} weeks · {_fmt_date(F["first_week"])} – {_fmt_date(F["last_week"])}</span><span class="pill teal">🕳️ {F["gaps"]} gaps</span>
  <span class="pill">🧾 {F["y_min"]}–{F["y_max"]} tickets a week</span><span class="pill gold">📡 {F["term_first"]:,} → {F["term_last"]:,} terminals</span>
</div>""",
          f"Blue: tickets raised each week (all causes). Teal, on its own scale: active VSAT terminals, the size of the network. "
          f"The last 8 weeks are locked: we'll forecast them, so we don't look at them yet. One small trap: the original code book says the file ends on 29 December. "
          f"It ends on {_fmt_date(F['last_week'])}: 104 Mondays from 1 January 2024."),

        # 6 ─ ingredients
        S(f"""
<div class="kicker anim">What's inside the series</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Trend + a season that comes in <span class="hl">steps</span> + noise</h2>
<div class="card anim" style="--d:.2s;padding:18px 24px">{series_svg(D, h=380, rainy=True, steps={"2024-04-01": f"+{st['2024-04-01']}", "2024-11-04": f"−{-st['2024-11-04']}", "2025-04-07": f"+{st['2025-04-07']}"})}</div>
<div class="grid3" style="margin-top:16px;gap:22px">
  <div class="card anim a-pop" style="--d:2.8s;padding:16px 24px"><h3 style="font-size:28px">📈 Trend</h3><p class="small">The network grows every week, and tickets grow with it.</p></div>
  <div class="card anim a-pop" style="--d:3.1s;padding:16px 24px"><h3 style="font-size:28px">🌧️ Season</h3><p class="small">Rain arrives in April: a jump. It leaves in November: a drop. December adds a bump.</p></div>
  <div class="card anim a-pop" style="--d:3.4s;padding:16px 24px"><h3 style="font-size:28px">🎲 Noise</h3><p class="small">Week-to-week wobble no forecast should chase.</p></div>
</div>""",
          f"The season is not a smooth wave. Tickets jump by {st['2024-04-01']} in the first week of April 2024, drop by {-st['2024-11-04']} in the first week of November, "
          f"and jump by {st['2025-04-07']} again in April 2025. Rain fade on the VSAT links, the same story as W1D2. Remember the steps: they explain every result today."),

        # 7 ─ the rule
        S(f"""
<div class="kicker anim">The rule from Week 5 · Day 1</div>
<h2 class="anim" style="--d:.1s">Lock the last 8 weeks away 🔒</h2>
<div class="card anim" style="--d:.2s;padding:26px 28px">{split_svg()}</div>
<pre class="code anim" style="--d:1.8s;font-size:25px;margin-top:22px">H = 8                                   <span class="c"># forecast 8 weeks ahead</span>
train, actual = y.iloc[:-H], y.iloc[-H:]    <span class="c"># 96 weeks to learn from, 8 to be judged on</span>
assert train.index.max() &lt; actual.index.min()</pre>
<p class="anim" style="--d:2.2s;margin-top:18px;text-align:center">Every forecast today is made on <b class="hl">27 Oct 2025</b> and must guess all 8 weeks <b>blind</b>. No expo.</p>""",
          "Same split-by-time idea as W5D1, with a forecast horizon instead of an embargo. Standing on 27 October, nobody knows November's numbers yet. "
          "Blind means: the forecast for 22 December can't use the real number from 15 December."),

        # 8 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">Four baselines 👵🏾</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">The cheapest forecasts there are. Every one is a real forecast.</p>""",
          "Section break.", cls="center"),

        # 9 ─ four baselines
        S(f"""
<div class="kicker anim">Cheapest first · each makes ONE assumption</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Four ways Grandma could think</h2>
<div class="grid4" style="margin-top:14px;gap:22px">
  <div class="card anim a-pop" style="--d:.3s;padding:24px 22px"><div class="icon">👵🏾</div><h3 style="font-size:28px">Naive</h3>
    <p class="small">“Same as last week.”</p><pre class="code" style="font-size:17px;padding:12px 14px;margin-top:12px">series.iloc[-1]</pre>
    <div class="stat" style="font-size:64px;color:{COL['naive']};margin-top:14px">{D['naive_value']:.0f}</div><div class="stat-label" style="font-size:19px">every week</div></div>
  <div class="card anim a-pop" style="--d:.55s;padding:24px 22px"><div class="icon">📅</div><h3 style="font-size:28px">Seasonal naive</h3>
    <p class="small">“Same week last year.”</p><pre class="code" style="font-size:17px;padding:12px 14px;margin-top:12px">series.iloc[-52:]</pre>
    <div class="stat" style="font-size:64px;color:{COL['seasonal_naive']};margin-top:14px">{min(F['sn_source']):.0f}–{max(F['sn_source']):.0f}</div><div class="stat-label" style="font-size:19px">copied from Nov–Dec 2024</div></div>
  <div class="card anim a-pop" style="--d:.8s;padding:24px 22px"><div class="icon">🧮</div><h3 style="font-size:28px">Moving average</h3>
    <p class="small">“The average of the last 8 weeks.”</p><pre class="code" style="font-size:17px;padding:12px 14px;margin-top:12px">series.iloc[-8:].mean()</pre>
    <div class="stat" style="font-size:64px;color:{COL['moving_average']};margin-top:14px">{D['ma_value']:.0f}</div><div class="stat-label" style="font-size:19px">every week</div></div>
  <div class="card anim a-pop" style="--d:1.05s;padding:24px 22px"><div class="icon">🫖</div><h3 style="font-size:28px">Exp. smoothing</h3>
    <p class="small">“A running level: each week pulls it 30% of the way.”</p><pre class="code" style="font-size:17px;padding:12px 14px;margin-top:12px">a*v + (1-a)*level</pre>
    <div class="stat" style="font-size:64px;color:{COL['exp_smoothing']};margin-top:14px">{D['es_value']:.1f}</div><div class="stat-label" style="font-size:19px">every week (α = 0.3)</div></div>
</div>""",
          f"Read each one as an assumption about the world. Naive: nothing changes. Seasonal naive: this year repeats last year (52 weeks back, because the data is weekly and the season is yearly). "
          f"Moving average: the recent level, smoothed. Exponential smoothing: a level that updates every week, alpha = 0.3 means each new week pulls it 30% of the way towards itself. "
          f"The big numbers are what each one forecasts for the 8 locked weeks. Quiz 4 Q1, Q2 and Q5 live on this slide."),

        # 10 ─ forecasts vs actual
        S(f"""
<div class="kicker anim">Unlock the 8 weeks 🔓</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Four forecasts vs what really happened</h2>
<div class="card anim" style="--d:.2s;padding:20px 24px">{forecast_svg(D, F, BASE4)}</div>
<p class="anim" style="--d:3.6s;margin-top:16px;text-align:center">White = actual. Naive and smoothing sail over November; seasonal naive sits <b class="bad">far below</b> all 8 weeks.</p>""",
          f"Now we open the envelope. The white line drops from {lv} to {a0} on 3 November: the rainy season has ended. Then it climbs back in December. "
          f"None of the four sees both the drop and the growth. The numbers at the right are each one's MAE: next slide explains it."),

        # 11 ─ MAE
        S(f"""
<div class="kicker anim">How wrong, in plain words?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">MAE: the typical miss, in tickets 📏</h2>
<div class="card anim" style="--d:.2s;padding:18px 24px">{errors_svg(D, F)}</div>
<div class="row anim" style="--d:2.8s;gap:30px;margin-top:16px;align-items:center;justify-content:center">
  <pre class="code" style="font-size:24px;padding:16px 26px">({" + ".join(map(str, D["naive_err"]))}) ÷ 8 = <span class="n">{M["naive"]:.2f}</span></pre>
  <p style="font-size:28px;max-width:560px">“On a typical week, naive was off by about <b class="hl">{M["naive"]:.0f} tickets</b>.”</p>
</div>""",
          f"Mean absolute error: take each week's miss, drop the minus sign, average. It's in the same unit as the data, tickets, so a duty manager understands it. "
          f"Naive's misses: {', '.join(map(str, D['naive_err']))}. The four big November misses are the rainy season ending. Quiz 4 Q3: 'MAE 11.25 = off by about 11 tickets on a typical week'."),

        # 12 ─ scoreboard
        S(f"""
<div class="kicker anim">Same 8 weeks · same scorer · lower is better</div>
<h2 class="anim" style="--d:.1s">The scoreboard 🏁</h2>
<div class="card anim" style="--d:.2s;padding:28px 30px">{hbars_svg([(f"{k + 1}. {NICE[n]}", M[n], COL[n]) for k, n in enumerate(ranked)], M[worst] * 1.05)}</div>
<p class="sub anim" style="--d:1.6s;margin-top:26px;text-align:center">Grandma's naive wins: <b class="hl">{M["naive"]:.2f}</b>. Seasonal naive comes <b class="bad">last</b>, on a seasonal series. 🤔</p>""",
          f"Naive {M['naive']:.2f}, exponential smoothing {M['exp_smoothing']:.2f}, moving average {M['moving_average']:.2f}, seasonal naive {M['seasonal_naive']:.2f}. "
          "These are exactly the numbers in the original code book and in Quiz 4. Ask the room: why would the seasonal method lose on a seasonal series?"),

        # 13 ─ why SN lost
        S(f"""
<div class="kicker anim">Why did seasonal naive come last?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">It copied a <span class="hl">smaller</span> network 📡</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;text-align:center"><div class="small">a year before the forecast (28 Oct 2024)</div>
    <div class="stat" style="color:{B['blue_d']};margin-top:10px">{F["term_year_before"]:,}</div><div class="stat-label">terminals</div>
    <p class="muted" style="margin-top:16px">Nov–Dec 2024: {min(F['sn_source'])}–{max(F['sn_source'])} tickets a week</p></div>
  <div class="card anim a-right" style="--d:.7s;text-align:center;border-color:#F5B83D"><div class="small">the forecast origin (27 Oct 2025)</div>
    <div class="stat hl count" data-to="{F['term_origin']}" data-d=".9" style="margin-top:10px">0</div><div class="stat-label">terminals: <b class="hl">+{D['growth'] - 1:.0%}</b></div>
    <p class="muted" style="margin-top:16px">same weeks, a much bigger network</p></div>
</div>
<p class="sub anim" style="--d:1.6s;margin-top:28px;text-align:center">The season was right. The <b>size</b> was wrong. It missed by {M["seasonal_naive"]:.2f} tickets a week, every week too low.</p>""",
          f"Seasonal naive repeats last year's weeks exactly ({', '.join(map(str, F['sn_source']))}). The shape is right: low in November, up in December. "
          f"But the network has grown by {D['growth'] - 1:.0%} since then, so every number is too small. That's Quiz 4 Q4."),

        # 14 ─ why naive won
        S(f"""
<div class="kicker anim">And why did naive “win”?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">It copied the <span class="hl">wrong season</span> 🌧️→☀️</h2>
<div class="row" style="gap:40px;margin-top:20px;align-items:center">
  <div class="card anim a-left" style="--d:.3s;flex:1;text-align:center"><div class="small">last training week · {lw:%d %b %Y} · rainy season</div>
    <div class="stat" style="color:{COL['naive']};margin-top:10px">{lv}</div><div class="stat-label">tickets</div></div>
  <div class="arrow anim a-fade" style="--d:.6s;width:90px;height:6px;background:linear-gradient(90deg,#3B8BE0,#F5B83D)"></div>
  <div class="card anim a-right" style="--d:.8s;flex:1;text-align:center"><div class="small">first test week · 3 Nov 2025 · dry season</div>
    <div class="stat" style="color:{WHITE};margin-top:10px">{a0}</div><div class="stat-label">tickets</div></div>
</div>
<p class="sub anim" style="--d:1.4s;margin-top:30px;text-align:center">Naive was too high <b>{"every" if D["naive_over_all"] else "most"}</b> week: off by 16–21 tickets all November.<br>It won because the others were <b class="bad">even worse</b>, not because it was good.</p>""",
          "Naive knows the level (a big network) but not the season. It copied a rainy-season week into the dry season. In December the season bumped back up, so naive looked fine again by luck. "
          "Winning a bad race is not the same as being good."),

        # 15 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Divide by the size ➗</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">The trick the original code book never tries.</p>""",
          "Section break.", cls="center"),

        # 16 ─ the rate repeats
        S(f"""
<div class="kicker anim">Tickets per 1,000 terminals · training weeks only</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Divide by the network: the season <span class="hl">repeats</span></h2>
<div class="card anim" style="--d:.2s;padding:18px 24px">{rate_bars_svg(F)}</div>
<p class="anim" style="--d:2.2s;margin-top:16px;text-align:center">January {rb.loc[1, 2024]:.1f} then {rb.loc[1, 2025]:.1f}. April {rb.loc[4, 2024]:.1f} then {rb.loc[4, 2025]:.1f}. Never more than <b class="hl">{D["year_gap"]:.1f}</b> apart.
The rainy season lifts the rate by <b class="hl">{F["rainy_lift"]:.1%}</b>.</p>""",
          f"Divide each week's tickets by that week's terminals (times 1,000). The growth disappears and what's left is the season, almost identical in both years. "
          f"Biggest gap between the two years for the same month: {D['year_gap']:.1f} per 1,000 ({pd.Timestamp(2025, D['year_gap_month'], 1):%B}). "
          f"Rainy months (April to October) run at {F['rate_rainy']:.1f} per 1,000 terminals, dry months at {F['rate_dry']:.1f}: a {F['rainy_lift']:.1%} lift. "
          "We only used training weeks to see this: November and December 2025 stay locked."),

        # 17 ─ the formula
        S(f"""
<div class="kicker anim">Grandma, adjusted for the bigger family 👵🏾➕</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Rate seasonal naive</h2>
<div class="flow" style="margin-top:26px;justify-content:center">
  <div class="box on anim a-pop" style="--d:.3s;min-width:300px"><div class="icon">📅</div><h3>Last year's rate</h3><p class="small">{D["ly_tickets"]} tickets ÷ {D["ly_terms"]:,} terminals</p>
    <p class="mono" style="color:#F5B83D;font-size:30px;margin-top:8px">{D["ly_rate"]:.1f} per 1,000</p></div>
  <div class="anim a-fade" style="--d:.6s;font-size:70px;padding:0 26px">×</div>
  <div class="box on anim a-pop" style="--d:.8s;min-width:300px"><div class="icon">📡</div><h3>Today's network</h3><p class="small">at the forecast origin</p>
    <p class="mono" style="color:#F5B83D;font-size:30px;margin-top:8px">{D["now_terms"]:,} terminals</p></div>
  <div class="anim a-fade" style="--d:1.1s;font-size:70px;padding:0 26px">=</div>
  <div class="box on anim a-pop" style="--d:1.3s;min-width:260px;border-color:#3CCB7F"><div class="icon">🎯</div><h3>Forecast</h3><p class="small">week of 3 Nov 2025</p>
    <p class="mono" style="color:#3CCB7F;font-size:34px;margin-top:8px">{D["rate_w1"]:.1f}</p></div>
</div>
<pre class="code anim" style="--d:1.7s;font-size:24px;margin-top:28px">rate = series / terminals                                       <span class="c"># per terminal</span>
return rate.iloc[-52:].values[:h] * float(terminals.iloc[-1])   <span class="c"># x today's size</span></pre>""",
          f"Two lines of code. For the week of 3 November: a year earlier, {D['ly_tickets']} tickets came from {D['ly_terms']:,} terminals, a rate of {D['ly_rate']:.1f} per 1,000. "
          f"Today the network has {D['now_terms']:,} terminals, so expect {D['rate_w1']:.1f}. The actual was {a0}. Everything it uses was known on 27 October: still blind."),

        # 18 ─ the result
        S(f"""
<div class="kicker anim">Same 8 weeks · same scorer · still blind</div>
<h2 class="anim" style="--d:.1s;font-size:54px">It follows the drop <b>and</b> the growth 🎯</h2>
<div class="card anim" style="--d:.2s;padding:18px 24px">{forecast_svg(D, F, ["naive", "rate_seasonal_naive"], h=400)}</div>
<div class="row anim" style="--d:3s;gap:30px;margin-top:14px;justify-content:center;align-items:center">
  <div class="stat good count" data-to="{M['rate_seasonal_naive']:.2f}" data-dec="2" data-d="3.1" style="font-size:90px">0</div>
  <p style="font-size:30px">tickets a week, against naive's {M["naive"]:.2f}.<br><b class="hl">{D["times_better"]:.0f}× better</b>, and it forecast all 8 weeks on 27 Oct.</p>
</div>""",
          f"MAE {M['rate_seasonal_naive']:.2f} versus {M['naive']:.2f}: about {D['times_better']:.0f} times smaller. It knows the season (from last year's rate) and the size (from today's terminals). "
          "Nothing was fitted, nothing was tuned, and no test week was used."),

        # 19 ─ callback
        S("""
<div class="kicker anim">You've done this before</div>
<h2 class="anim" style="--d:.1s">Divide out what you already know</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🌡️</div><h3>Week 4 · Day 3</h3>
    <p class="muted">Amplifier temperature <b style="color:#fff">÷ RF drive</b>. Hot because it works hard is normal; hot for its drive is EV04.</p>
    <p class="mono" style="color:#F5B83D;margin-top:12px">temp_per_drive</p></div>
  <div class="card anim a-right glow" style="--d:.6s"><div class="icon">🧾</div><h3>Today</h3>
    <p class="muted">Tickets <b style="color:#fff">÷ terminals</b>. More tickets because the network grew is normal; the rate shows the season.</p>
    <p class="mono" style="color:#F5B83D;margin-top:12px">tickets_per_terminal</p></div>
</div>
<p class="sub anim" style="--d:1s;margin-top:34px;text-align:center;font-size:30px">NEPA bill per room, fuel per kilometre, jollof per guest: <b class="hl">a rate travels, a count doesn't</b>. 🍛</p>""",
          "This is the same move as W4D3. A raw count mixes two things: how big the system is and how it behaves. Dividing by the size you already know leaves the behaviour, and behaviour repeats."),

        # 20 ─ the bar
        S(f"""
<div class="kicker anim">The bar for every later model</div>
<h2 class="anim" style="--d:.1s">Every fancier model must beat <span class="hl">this</span> 🪜</h2>
<div class="card anim" style="--d:.2s;padding:28px 30px">{hbars_svg([("🎯 Rate seasonal naive", M["rate_seasonal_naive"], GREEN)] + [(f"{NICE[n]}", M[n], COL[n]) for n in ranked], M[worst] * 1.05)}</div>
<p class="sub anim" style="--d:1.8s;margin-top:24px;text-align:center">Not the baseline its name suggests. Not the one that's easy to beat. <b class="hl">The best one.</b></p>""",
          "Next session a linear regression with five features tries to earn its place. It has to beat the best baseline on the same weeks with the same scorer. "
          "Quiz 4 Q6: a model that only ties the best baseline has NOT earned its place."),

        # 21 ─ one split can lie
        S(f"""
<div class="kicker anim">Before you celebrate…</div>
<h2 class="anim" style="--d:.1s;font-size:54px">One split can lie 🎲</h2>
<div class="row" style="gap:40px;margin-top:20px;align-items:center">
  <div class="card anim a-pop" style="--d:.3s;flex:1;text-align:center;border-color:#F5B83D"><div class="icon">😴</div><h3>The flat training average</h3>
    <p class="muted">Average all 96 training weeks ({D["train_mean"]:.1f}) and say it every week. The forecast the code book calls “the wrong baseline”.</p>
    <div class="stat hl" style="margin-top:16px">{F["training_mean_mae"]:.2f}</div><div class="stat-label">MAE on these 8 weeks</div></div>
  <div class="col anim a-right" style="--d:.8s;flex:1;gap:18px">
    <p style="font-size:30px">It “beat” all four code-book baselines here. 😳</p>
    <p class="muted" style="font-size:27px">The dry-season drop and the network growth happened to cancel out on these 8 weeks.</p>
    <p style="font-size:30px">Skill or luck? <b class="hl">Week 6 · Day 1</b> tests every method on dozens of different 8-week stretches.</p>
  </div>
</div>""",
          f"The average of the training weeks is {D['train_mean']:.1f}. The actual 8 weeks averaged {D['actual_mean']:.2f}. Two wrongs made a right on this one split. "
          "Don't resolve it today: the backtesting day (W6D1) does, by standing at every week of 2025 and forecasting from there."),

        # 22 ─ your turn
        S(f"""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Beat Grandma yourself 👵🏾</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open <b class="hl">W5D2-exercise</b>, save a copy, run STEP 0</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">A</span><p>Load the weeks, lock the last 8 away</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">B</span><p>Write the four baselines, score them</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">C</span><p>Divide by the size: the rate forecast</p></div>
   <div class="row anim" style="--d:1.1s;gap:18px;align-items:center"><span class="num">D</span><p>The flat average's lucky score</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.3s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🎯</div>
  <h3 style="margin-top:16px">{len(_CHECK_NAMES)} checks to pass</h3>
  <p class="muted">🌶️ Pepper task: change α and see the expo trap</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Each baseline is a 2-line function with one blank. Common snags: typing \"W-MON\" without quotes, and running cells out of order."),

        # 23 ─ recap
        S(f"""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:16px;margin-top:6px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">👵🏾</span><p><b>Baselines first:</b> naive, seasonal naive, moving average, smoothing. Cheap, and real forecasts.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">📏</span><p><b>Score honestly:</b> lock the last weeks away, forecast blind, MAE in tickets, same weeks for all.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">➗</span><p><b>Divide by the size:</b> last year's rate × today's network = {M["rate_seasonal_naive"]:.2f}. That's the bar.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:22px;font-size:30px">Next 👉 <b class="hl">Regression forecasts + honest ranges</b>: “I'm on my way” vs “30 to 90 minutes”. 🚗<br>
<span class="small">Final project: bring your temporal split + baseline comparison table to Checkpoint 4 (next session).</span></p>""",
          "Recap. Remind them that Checkpoint 4 is next session: their own project's split by time and a baseline comparison table, same scorer. Today's scoreboard is the template."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    F = facts()
    D = day_facts()
    M = F["baseline_mae"]
    st = F["season_steps"]
    rb = F["rate_by_month"]
    lw, lv = F["last_train_week"]
    ranked = sorted(BASE4, key=lambda k: M[k])
    weeks = [f"{t:%d %b}" for t in D["actual"].index]
    a0 = int(D["actual"].iloc[0])
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "👵🏾", "kicker": "Week 5 · Day 2", "title": "Forecasting\nBaselines",
             "sub": "Grandma's forecast: “tomorrow will be like today.” She's harder to beat than you think",
             "notes": "From today we ask: what happens next?"},
            {"type": "flow", "title": "Today's mission", "steps": [
                ["🧾", "Meet the series", "trend · season · noise"], ["👵🏾", "Four baselines", "the cheapest forecasts"],
                ["📏", "Score them", "MAE, in tickets"], ["➗", "Divide by size", "the trick that wins"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up", "notes": "Four moves."},
            {"type": "compare", "title": "Who forecasts next week's NOC tickets?",
             "left": ["👵🏾", "Grandma", "“The same as today, my child.” Free, one line of code"],
             "right": ["🧑🏾‍💼", "The consultant", "An AI model and a ₦25 million invoice, never compared with Grandma"],
             "notes": "If the AI can't beat Grandma, the invoice is for nothing. Grandma's forecast is a baseline."},
            {"type": "compare", "title": "From “is it wrong now?” to “what comes next?”",
             "left": ["🚨", "Weeks 3–5: detection", "Is a reading that already happened normal?"],
             "right": ["🔮", "Weeks 5–6: forecasting", "Guess a reading that hasn't happened yet, only from the past"],
             "notes": "A forecast that used next week's number is expo."},
            {"type": "chart", "title": "NOC tickets, every week for two years",
             "labels": [(f"{t:%b %Y}" if t.month in (1, 4, 7, 10) and t.day <= 7 else "") for t in D["y"].index[:-H]], "values": [int(v) for v in D["train"].values], "ymin": 20, "ymax": 85, "fmt": "0", "freq": 1,
             "caption": f"{F['n_weeks']} weeks, {_fmt_date(F['first_week'])} – {_fmt_date(F['last_week'])}, {F['gaps']} gaps · {F['y_min']}–{F['y_max']} tickets a week · "
                        f"{F['term_first']:,} → {F['term_last']:,} terminals. The last 8 weeks are locked away.",
             "notes": "The code book says the file ends on 29 December: it ends on 22 December."},
            {"type": "cards", "title": "Trend + a season that comes in steps + noise", "cards": [
                ["📈", "Trend", "the network grows every week; tickets grow with it"],
                ["🌧️", "Season", f"April: +{st['2024-04-01']} / +{st['2025-04-07']} tickets in one week. November: −{-st['2024-11-04']}. December bump"],
                ["🎲", "Noise", "week-to-week wobble no forecast should chase"]],
             "notes": "The season is a step, not a smooth wave."},
            {"type": "code", "title": "Lock the last 8 weeks away",
             "code": "H = 8\ntrain, actual = y.iloc[:-H], y.iloc[-H:]\nassert train.index.max() < actual.index.min()",
             "caption": "96 training weeks to learn from, 8 test weeks to be judged on. Every forecast is made on 27 Oct 2025, blind.",
             "notes": "Same split-by-time idea as W5D1."},
            {"type": "section", "kicker": "Part 1", "title": "Four baselines", "sub": "The cheapest forecasts there are", "notes": "Section break."},
            {"type": "cards4", "title": "Four ways Grandma could think", "cards": [
                ["👵🏾", "Naive", f"same as last week: {D['naive_value']:.0f}"],
                ["📅", "Seasonal naive", f"same week last year: {min(F['sn_source'])}–{max(F['sn_source'])}"],
                ["🧮", "Moving average", f"mean of the last 8 weeks: {D['ma_value']:.0f}"],
                ["🫖", "Exp. smoothing", f"a running level (α 0.3): {D['es_value']:.1f}"]],
             "notes": "Each makes one assumption about the world."},
            {"type": "chart", "title": "Four forecasts vs what really happened", "labels": weeks, "ymin": 35, "ymax": 85, "fmt": "0",
             "series": [{"name": "actual", "values": [int(v) for v in D["actual"].values], "color": "0B1622"}] +
                       [{"name": NICE[n], "values": [round(float(v), 1) for v in F["fc"][n].values], "color": COL[n].lstrip("#")} for n in BASE4],
             "caption": "Naive and smoothing sail over November; seasonal naive sits far below all 8 weeks.", "notes": "Open the envelope."},
            {"type": "statement", "title": "MAE: the typical miss, in tickets", "icon": "📏",
             "big": f"({' + '.join(map(str, D['naive_err']))}) ÷ 8 = {M['naive']:.2f}",
             "sub": f"Naive's 8 misses, minus signs dropped, averaged: on a typical week it was off by about {M['naive']:.0f} tickets.",
             "notes": "Quiz 4 Q3."},
            {"type": "bar", "title": "The scoreboard: MAE, lower is better",
             "labels": [NICE[n] for n in ranked], "values": [round(M[n], 2) for n in ranked], "highlight": [0], "fmt": "0.00",
             "caption": "Naive wins. Seasonal naive comes last, on a seasonal series.", "notes": "Same numbers as the code book and Quiz 4."},
            {"type": "stats", "title": "Why did seasonal naive come last?", "sub": "It copied the right season from a much smaller network",
             "stats": [[f"{F['term_year_before']:,}", "terminals a year before the forecast"], [f"{F['term_origin']:,}", "terminals at the forecast origin"],
                       [f"+{D['growth'] - 1:.0%}", "growth: every copied week is too low"]],
             "notes": "Quiz 4 Q4."},
            {"type": "stats", "title": "And why did naive “win”?", "sub": "It copied the wrong season",
             "stats": [[str(lv), f"tickets, {lw:%d %b} (rainy season)"], [str(a0), "tickets, 3 Nov (dry season)"], ["16–21", "tickets too high, every November week"]],
             "notes": "Winning a bad race is not the same as being good."},
            {"type": "section", "kicker": "Part 2", "title": "Divide by the size", "sub": "The trick the original code book never tries", "notes": "Section break."},
            {"type": "table", "title": "Tickets per 1,000 terminals: the season repeats", "header": ["Year"] + [f"{pd.Timestamp(2025, m, 1):%b}" for m in range(1, 13)],
             "rows": [[str(yr)] + [("locked" if rb.loc[m, yr] != rb.loc[m, yr] else f"{rb.loc[m, yr]:.1f}") for m in range(1, 13)] for yr in (2024, 2025)],
             "colW": [1.17] + [0.93] * 12,
             "caption": f"Training weeks only (Nov–Dec 2025 are the locked test weeks). Never more than {D['year_gap']:.1f} apart. The rainy season lifts the rate by {F['rainy_lift']:.1%}.",
             "notes": "Divide by the network and the season repeats."},
            {"type": "flow", "title": "Rate seasonal naive: Grandma, adjusted", "steps": [
                ["📅", "Last year's rate", f"{D['ly_tickets']} ÷ {D['ly_terms']:,} = {D['ly_rate']:.1f} per 1,000"],
                ["📡", "× today's network", f"{D['now_terms']:,} terminals"],
                ["🎯", "= the forecast", f"{D['rate_w1']:.1f} for 3 Nov (actual {a0})"]],
             "footer": "rate = series / terminals  ·  rate.iloc[-52:].values[:h] * terminals.iloc[-1]", "notes": "Two lines of code, still blind."},
            {"type": "chart", "title": "It follows the drop and the growth", "labels": weeks, "ymin": 35, "ymax": 85, "fmt": "0",
             "series": [{"name": "actual", "values": [int(v) for v in D["actual"].values], "color": "0B1622"},
                        {"name": "naive", "values": [round(float(v), 1) for v in F["fc"]["naive"].values], "color": COL["naive"].lstrip("#")},
                        {"name": "rate seasonal naive", "values": [round(float(v), 1) for v in F["fc"]["rate_seasonal_naive"].values], "color": "1E9E5A"}],
             "caption": f"MAE {M['rate_seasonal_naive']:.2f} against naive's {M['naive']:.2f}: {D['times_better']:.0f}× better, all 8 weeks forecast on 27 Oct.",
             "notes": "Nothing fitted, nothing tuned."},
            {"type": "compare", "title": "Divide out what you already know",
             "left": ["🌡️", "Week 4 · Day 3", "amplifier temperature ÷ RF drive = temp_per_drive"],
             "right": ["🧾", "Today", "tickets ÷ terminals = the season, repeating"],
             "notes": "A rate travels, a count doesn't."},
            {"type": "bar", "title": "Every fancier model must beat this",
             "labels": ["Rate seasonal naive"] + [NICE[n] for n in ranked], "values": [round(M["rate_seasonal_naive"], 2)] + [round(M[n], 2) for n in ranked],
             "highlight": [0], "fmt": "0.00", "caption": "The best baseline, not the one its name suggests.", "notes": "Quiz 4 Q6."},
            {"type": "statement", "title": "One split can lie", "icon": "🎲",
             "big": f"The flat training average scored {F['training_mean_mae']:.2f}",
             "sub": "It “beat” all four code-book baselines on these 8 weeks. Skill or luck? Week 6 · Day 1 tests every method on dozens of stretches.",
             "notes": "Don't resolve it today."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🎯", "steps": [
                "Open W5D2-exercise, save a copy, run STEP 0", "Part A: load, lock the last 8 weeks", "Part B: four baselines + the scoreboard",
                "Part C: the rate forecast · Part D: the lucky average"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["👵🏾", "Baselines first: naive, seasonal naive, moving average, smoothing"],
                ["📏", "Score honestly: lock the last weeks away, forecast blind, MAE in tickets"],
                ["➗", f"Divide by the size: last year's rate × today's network = {M['rate_seasonal_naive']:.2f}"]],
             "next": "Next: Regression forecasts + honest ranges · Project Checkpoint 4 next session", "notes": "Recap."},
        ],
    }


# =============================================================================
# NOTEBOOK CHECKS (expected values filled in from the data at build time)
# =============================================================================
_CHECK_NAMES = ["A1", "A2", "B1", "B2", "B3", "B4", "B5", "B6", "C1", "C2", "C3", "C4", "D1", "BONUS"]


def _checks():
    F = facts()
    D = day_facts()
    M = F["baseline_mae"]
    rb = F["rate_by_month"]
    expected_rate = {(int(m), int(yr)): round(float(rb.loc[m, yr]), 1) for m in rb.index for yr in rb.columns if rb.loc[m, yr] == rb.loc[m, yr]}
    vals = {
        "N": str(F["n_weeks"]), "FIRST_TEST": repr(str(F["holdout"][0].date())),
        "NAIVE": f"{D['naive_value']:.0f}", "LAST_WEEK": f"{F['last_train_week'][0]:%d %b}",
        "SN_SRC": ", ".join(map(str, F["sn_source"])), "MA": f"{D['ma_value']:.0f}", "ES": f"{D['es_value']:.2f}",
        "M4": repr({k: round(M[k], 4) for k in BASE4}), "M_NAIVE": f"{M['naive']:.2f}", "M_SN": f"{M['seasonal_naive']:.2f}",
        "GROWTH": repr(round(D["growth"], 6)), "GROWTH_PCT": f"{D['growth'] - 1:.0%}", "T_THEN": f"{F['term_year_before']:,}", "T_NOW": f"{F['term_origin']:,}",
        "RATE": repr(expected_rate), "GAP": f"{D['year_gap']:.1f}",
        "RATE_W1": f"{D['rate_w1']:.1f}", "A0": str(int(D["actual"].iloc[0])),
        "M_RATE": repr(round(M["rate_seasonal_naive"], 4)), "M_RATE_S": f"{M['rate_seasonal_naive']:.2f}", "TIMES": f"{D['times_better']:.0f}",
        "M_MEAN": repr(round(F["training_mean_mae"], 4)), "M_MEAN_S": f"{F['training_mean_mae']:.2f}",
        "ES9": f"{D['alpha'][0.9][1]:.2f}",
    }
    code = r'''
def _near(x, want, tol):
    return abs(float(x) - want) <= tol

def _same(got, want, tol=1e-6):
    got = np.asarray(got, dtype=float)
    return got.shape == np.asarray(want).shape and bool(np.allclose(got, want, atol=tol))

def _c_a1(x):
    freq, rows, gaps = x
    ok = str(freq).upper() == "W-MON" and rows == @@N@@ and gaps == 0
    return ok, "@@N@@ Mondays in a row, 0 gaps. A clean weekly series. 📅", \
        "Every row is a Monday: the weekly code that starts on Monday is \"W-MON\" (in quotes)."

def _c_a2(x):
    return tuple(x) == (96, 8, @@FIRST_TEST@@), \
        "96 weeks to learn from, 8 locked away (from 3 Nov 2025). Forecasts are made on 27 Oct, blind. 🔒", \
        "The last 8 weeks: H = 8."

def _c_b1(x):
    s = pd.Series([3.0, 5.0, 9.0])
    return _same(x(s, 4), [9, 9, 9, 9]), \
        "Grandma's forecast: @@NAIVE@@ tickets every week (the last training week, @@LAST_WEEK@@). 👵🏾", \
        "The LAST value of the series is position -1: series.iloc[-1]."

def _c_b2(x):
    s = pd.Series(np.arange(1, 105, dtype=float))
    return _same(x(s, 8), np.arange(53, 61, dtype=float)), \
        "It copies 4 Nov – 23 Dec 2024: @@SN_SRC@@. 📅", \
        "Weekly data, yearly season: one season is 52 weeks, so period=52."

def _c_b3(x):
    s = pd.Series(np.arange(1, 21, dtype=float))
    return _same(x(s, 3), [16.5, 16.5, 16.5]), \
        "The mean of the last 8 training weeks: @@MA@@ tickets, held flat. 🧮", \
        "The window is the last 8 weeks: window=8."

def _c_b4(x):
    s = pd.Series([10.0, 20.0])
    return _same(x(s, 2, 0.3), [13.0, 13.0]) and _same(x(s, 1, 0.5), [15.0]), \
        "Each week pulls the level alpha of the way; the rest, (1 - alpha), stays. Level: @@ES@@ tickets. 🫖", \
        "New level = alpha x new week + (what's left) x old level. What's left of 1 after taking alpha?"

def _c_b5(x):
    s = pd.Series(x)
    want = @@M4@@
    ok = all(_near(s[k], v, 0.005) for k, v in want.items())
    return ok, "Naive wins with @@M_NAIVE@@ tickets a week. Seasonal naive comes LAST (@@M_SN@@), on a seasonal series! 🤔", \
        "Compare each forecast with what really happened in the 8 weeks: COMPARE_WITH = actual"

def _c_b6(x):
    return _near(x, @@GROWTH@@, 0.0005), \
        "@@T_THEN@@ → @@T_NOW@@ terminals: the network is @@GROWTH_PCT@@ bigger than when seasonal naive's weeks were recorded. 📡", \
        "A year ago, in weeks: WEEKS_BACK = 52"

def _c_c1(x):
    want = @@RATE@@
    ok = all(_near(x.loc[m, y], v, 0.051) for (m, y), v in want.items())
    return ok, "Divide by the network and the season repeats: the same month never differs by more than @@GAP@@ per 1,000. ➗", \
        "Divide the tickets by the terminals of the same weeks: DIVIDE_BY = train_terminals"

def _c_c2(x):
    return int(x) == 4, "April: the rain arrives and the rate jumps from about 29 to about 39 per 1,000 terminals. 🌧️", \
        "Find the month where the number jumps by about 10."

def _c_c3(x):
    s = pd.Series([10.0, 20.0, 30.0, 40.0])
    t = pd.Series([100.0, 100.0, 200.0, 200.0])
    return _same(x(s, t, 2, period=4), [20.0, 40.0]), \
        "Last year's rate × today's terminals. For the week of 3 Nov: @@RATE_W1@@ tickets (actual: @@A0@@). 🎯", \
        "The rate is tickets per terminal: rate = series / terminals"

def _c_c4(x):
    s = pd.Series(x)
    ok = _near(s["rate_seasonal_naive"], @@M_RATE@@, 0.005) and _near(s["naive"], @@M_NAIVE@@, 0.005)
    return ok, "@@M_RATE_S@@ tickets a week: about @@TIMES@@× better than naive, all 8 weeks forecast blind. That's the bar. 🏆", \
        "Forecast all 8 locked weeks: HORIZON = H (or 8)."

def _c_d1(x):
    return _near(x, @@M_MEAN@@, 0.005), \
        "@@M_MEAN_S@@: the flat average 'beat' all four code-book baselines on these 8 weeks. Skill or luck? Week 6 Day 1 finds out. 🎲", \
        "The flat forecast is the mean of the training weeks: FLAT = train.mean()"

def _c_bonus(x):
    return _near(x, 0.9, 1e-9), \
        "α = 0.9 chases the latest week. On these 8 weeks it scores @@ES9@@, a hair better than naive. Switch to 0.9 now? No: you only know because you peeked. That's expo. 🌶️", \
        "A big alpha gives the newest week a big pull."

CHECKS = {"A1": _c_a1, "A2": _c_a2, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4, "B5": _c_b5, "B6": _c_b6,
          "C1": _c_c1, "C2": _c_c2, "C3": _c_c3, "C4": _c_c4, "D1": _c_d1, "BONUS": _c_bonus}
HINTS = {"B1": "Replace the ___ inside the function with the position of the LAST value.",
         "B2": "Replace the ___ with the season length in weeks.",
         "B3": "Replace the ___ with the number of weeks to average.",
         "B4": "Replace the ___ with the share of the OLD level that stays.",
         "C3": "Replace the ___ with tickets divided by terminals.",
         "C1": "DIVIDE_BY = train_terminals (no quotes)."}
'''
    for k, v in vals.items():
        code = code.replace(f"@@{k}@@", v)
    assert "@@" not in code
    names = [n for n in _CHECK_NAMES]
    assert all(f'"{n}": _c_' in code for n in names)
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
    M = F["baseline_mae"]

    def fn_task(name, old, check_tag, note=""):
        """One baseline function: blank version for participants, the shared code for the solution."""
        tail = f'\n\n{note}check("{check_tag}", {name})'
        return _task(_blank(name, old) + tail, FN[name] + tail)

    return [
        ("md", """# 👵🏾 Week 5 · Day 2: Forecasting Baselines

**Today:** you lock the last 8 weeks of NOC tickets away, forecast them four cheap ways, score every forecast with the same ruler, then find the two-line trick that beats them all.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**

**Rule book:** keep `W5D2-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up
Run it once every time you open the notebook (and after every restart). Wait for `✅ Ready!`."""),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Meet the weeks, lock the last 8 away (10 min) 🔒

### A1 ✍️ Load the weekly tickets
`ops_tickets_weekly` has one row per week: tickets raised at the NOC and the number of active VSAT terminals. Every date is a **Monday**.
Tell pandas the frequency: the weekly code that starts on Monday, as text (in quotes)."""),
        _task('FREQ = ___\n\nassert FREQ is not None, "✍️ Fill in FREQ first."\n'
              'tickets = pd.read_csv(data_path("ops_tickets_weekly"), parse_dates=["week_start"], index_col="week_start").asfreq(FREQ)\n'
              'gaps = int(tickets.isna().sum().sum())\nprint("weeks:", len(tickets), "· gaps:", gaps, "·", tickets.index[0].date(), "to", tickets.index[-1].date())\n'
              'display(tickets.head(3))\ncheck("A1", (FREQ, len(tickets), gaps))',
              'FREQ = "W-MON"\n\nassert FREQ is not None, "✍️ Fill in FREQ first."\n'
              'tickets = pd.read_csv(data_path("ops_tickets_weekly"), parse_dates=["week_start"], index_col="week_start").asfreq(FREQ)\n'
              'gaps = int(tickets.isna().sum().sum())\nprint("weeks:", len(tickets), "· gaps:", gaps, "·", tickets.index[0].date(), "to", tickets.index[-1].date())\n'
              'display(tickets.head(3))\ncheck("A1", (FREQ, len(tickets), gaps))'),
        ("md", """### A2 ✍️ Lock the last weeks away
We'll forecast the **last 8 weeks** as if we were standing on the last training week, not knowing them yet. How many weeks is the horizon `H`?"""),
        _task('H = ___\n\nassert H is not None, "✍️ Fill in H first."\nassert "tickets" in globals(), "✍️ Finish A1 first, then run this cell."\n'
              'y = tickets["tickets_raised"]\nterminals = tickets["active_vsat_terminals"]\n'
              'train, actual = y.iloc[:-H], y.iloc[-H:]\ntrain_terminals = terminals.iloc[:-H]\n'
              'assert train.index.max() < actual.index.min(), "leakage: training overlaps the test"\n'
              'print("train:", len(train), "weeks, to", train.index[-1].date(), "· test:", len(actual), "weeks, from", actual.index[0].date())\n'
              'check("A2", (len(train), len(actual), str(actual.index[0].date())))',
              'H = 8\n\nassert H is not None, "✍️ Fill in H first."\nassert "tickets" in globals(), "✍️ Finish A1 first, then run this cell."\n'
              'y = tickets["tickets_raised"]\nterminals = tickets["active_vsat_terminals"]\n'
              'train, actual = y.iloc[:-H], y.iloc[-H:]\ntrain_terminals = terminals.iloc[:-H]\n'
              'assert train.index.max() < actual.index.min(), "leakage: training overlaps the test"\n'
              'print("train:", len(train), "weeks, to", train.index[-1].date(), "· test:", len(actual), "weeks, from", actual.index[0].date())\n'
              'check("A2", (len(train), len(actual), str(actual.index[0].date())))'),
        ("md", "▶️ Look at the **training** weeks only (the test weeks stay locked). Notice the trend, and the **steps** every April and November."),
        ("code", 'assert "train" in globals(), "✍️ Finish A2 first, then run this cell."\n'
                 'fig, ax = plt.subplots()\nax.plot(train.index, train, lw=2.5, label="tickets per week")\n'
                 'ax.axvspan(actual.index[0], actual.index[-1], color="#F5B83D", alpha=.25, label="🔒 locked: the 8 test weeks")\n'
                 'ax2 = ax.twinx()\nax2.plot(train_terminals.index, train_terminals, color="#008C7E", lw=1.5, label="active terminals")\n'
                 'ax2.set_ylabel("terminals")\nax.set_ylabel("tickets")\nax.set_title("NOC tickets grow with the network, and jump every rainy season")\n'
                 'ax.legend(loc="upper left")\nplt.show()'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Four baselines, one scorer (25 min) 👵🏾

📖 Each baseline is a tiny function: give it the **training series** and the horizon `h`, it gives back `h` numbers. Each one makes **one assumption** about the world.

▶️ First the scorer you'll use for every forecast today: **MAE**, the mean absolute error. On a typical week, how many tickets were we off by?"""),
        ("code", FN["mae"] + '\n\nprint("example: forecasts 10, 10 vs actual 12, 7 → MAE", mae([10, 10], [12, 7]))'),
        ("md", """### B1 ✍️ Naive: "same as last week"
Repeat the **last** value of the series. Which position is the last value? (Python counts from the end with minus numbers.)"""),
        fn_task("naive", "series.iloc[-1]", "B1"),
        ("md", """### B2 ✍️ Seasonal naive: "same week last year"
Copy the same weeks one **season** ago. The data is weekly and the season is yearly: how many weeks in a season? Put it as the default `period`."""),
        fn_task("seasonal_naive", "period=52", "B2"),
        ("md", """### B3 ✍️ Moving average: "the average of the last 8 weeks"
Fill in the default `window`."""),
        fn_task("moving_average", "window=8", "B3"),
        ("md", """### B4 ✍️ Exponential smoothing: "a running level"
Walk through the weeks, keeping a **level**. Each new week pulls the level `alpha` of the way towards itself; the **rest of the old level stays**. With `alpha = 0.3`, 30% comes from the new week and how much from the old level? Write it with `alpha`."""),
        fn_task("exp_smoothing", "(1 - alpha)", "B4"),
        ("md", "▶️ All four forecasts for the 8 locked weeks, next to what really happened. **Now** we unlock the test weeks."),
        ("code", 'assert all(SCORE.get(t) for t in ("B1", "B2", "B3", "B4")), "✍️ Get B1 to B4 to ✅ first, then run this cell."\n'
                 'BASELINES = ["naive", "seasonal_naive", "moving_average", "exp_smoothing"]\n'
                 'fc = pd.DataFrame({\n    "naive": naive(train, H),\n    "seasonal_naive": seasonal_naive(train, H),\n'
                 '    "moving_average": moving_average(train, H),\n    "exp_smoothing": exp_smoothing(train, H),\n}, index=actual.index)\n'
                 'fc["actual"] = actual.values\ndisplay(fc.round(1))\n\n'
                 'fig, ax = plt.subplots()\nax.plot(y.iloc[-30:], color="black", lw=2.5, label="actual")\n'
                 'for name in BASELINES:\n    ax.plot(fc.index, fc[name], "--", lw=2, label=name)\n'
                 'ax.axvspan(actual.index[0], actual.index[-1], color="#F5B83D", alpha=.15)\n'
                 'ax.set_title("Four baselines vs the 8 test weeks")\nax.legend(ncol=5, fontsize=9)\nplt.show()'),
        ("md", """### B5 ✍️ The scoreboard
Score every baseline with `mae(forecast, ...)`. What do you compare each forecast **with**? (A variable, no quotes.)"""),
        _task('COMPARE_WITH = ___\n\nassert COMPARE_WITH is not None, "✍️ Fill in COMPARE_WITH first."\nassert "fc" in globals(), "✍️ Run the forecast-table cell above first."\n'
              'scores = pd.Series({name: mae(fc[name], COMPARE_WITH) for name in BASELINES}).sort_values()\n'
              'print("MAE, tickets per week (lower is better):")\nprint(scores.round(2).to_string())\ncheck("B5", scores)',
              'COMPARE_WITH = actual\n\nassert COMPARE_WITH is not None, "✍️ Fill in COMPARE_WITH first."\nassert "fc" in globals(), "✍️ Run the forecast-table cell above first."\n'
              'scores = pd.Series({name: mae(fc[name], COMPARE_WITH) for name in BASELINES}).sort_values()\n'
              'print("MAE, tickets per week (lower is better):")\nprint(scores.round(2).to_string())\ncheck("B5", scores)'),
        ("md", """### B6 ✍️ Why did seasonal naive come last?
It copied last year's weeks. How much bigger is the network now than **one year** before the forecast was made? Go back how many weeks?"""),
        _task('WEEKS_BACK = ___\n\nassert WEEKS_BACK is not None, "✍️ Fill in WEEKS_BACK first."\nassert "train_terminals" in globals(), "✍️ Finish A2 first, then run this cell."\n'
              'now = train_terminals.index[-1]\nthen = now - pd.Timedelta(weeks=WEEKS_BACK)\n'
              'growth = train_terminals[now] / train_terminals[then]\n'
              'print(f"{then.date()}: {train_terminals[then]:,} terminals → {now.date()}: {train_terminals[now]:,} terminals = x{growth:.3f}")\n'
              'check("B6", growth)',
              'WEEKS_BACK = 52\n\nassert WEEKS_BACK is not None, "✍️ Fill in WEEKS_BACK first."\nassert "train_terminals" in globals(), "✍️ Finish A2 first, then run this cell."\n'
              'now = train_terminals.index[-1]\nthen = now - pd.Timedelta(weeks=WEEKS_BACK)\n'
              'growth = train_terminals[now] / train_terminals[then]\n'
              'print(f"{then.date()}: {train_terminals[then]:,} terminals → {now.date()}: {train_terminals[now]:,} terminals = x{growth:.3f}")\n'
              'check("B6", growth)'),
        ("md", f"""> 📖 **What just happened?** Seasonal naive had the right **season** but the wrong **size**: every copied week came from a network about a third smaller. Naive had the right size but the wrong season: it copied {F['last_train_week'][1]} tickets, a rainy-season week, into the dry season. Each knows half the story."""),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Divide by the size (15 min) ➗

### C1 ✍️ Tickets per 1,000 terminals
Divide each training week's tickets by that week's terminals (×1,000), then average by month for each year. What do you divide by? (A variable, no quotes.)"""),
        _task('DIVIDE_BY = ___\n\nassert DIVIDE_BY is not None, "✍️ Fill in DIVIDE_BY first."\nassert not isinstance(DIVIDE_BY, str), "✍️ Use the variable itself, without quotes: DIVIDE_BY = train_terminals"\n'
              'per_1000 = 1000 * train / DIVIDE_BY\n'
              'rate_table = per_1000.groupby([per_1000.index.month, per_1000.index.year]).mean().unstack().round(1)\n'
              'rate_table.index.name, rate_table.columns.name = "month", "year"\ndisplay(rate_table)\ncheck("C1", rate_table)',
              'DIVIDE_BY = train_terminals\n\nassert DIVIDE_BY is not None, "✍️ Fill in DIVIDE_BY first."\nassert not isinstance(DIVIDE_BY, str), "✍️ Use the variable itself, without quotes: DIVIDE_BY = train_terminals"\n'
              'per_1000 = 1000 * train / DIVIDE_BY\n'
              'rate_table = per_1000.groupby([per_1000.index.month, per_1000.index.year]).mean().unstack().round(1)\n'
              'rate_table.index.name, rate_table.columns.name = "month", "year"\ndisplay(rate_table)\ncheck("C1", rate_table)'),
        ("md", """### C2 ✍️ When does the rain arrive?
Read the table. In which month (1–12) does the rate **jump**, in both years?"""),
        _task('RAIN_MONTH = ___\n\ncheck("C2", RAIN_MONTH)', 'RAIN_MONTH = 4\n\ncheck("C2", RAIN_MONTH)'),
        ("md", """### C3 ✍️ Rate seasonal naive: Grandma, adjusted for the bigger family
Last year's tickets **per terminal**, times **today's** terminals. Fill in the rate: tickets per terminal, every week."""),
        fn_task("rate_seasonal_naive", "series / terminals", "C3"),
        ("md", """### C4 ✍️ Score it on the same 8 weeks
Forecast all the locked weeks at once (blind), then rebuild the scoreboard. How many weeks ahead?"""),
        _task('HORIZON = ___\n\nassert HORIZON is not None, "✍️ Fill in HORIZON first."\nassert SCORE.get("C3") and "fc" in globals(), "✍️ Get C3 to ✅ and run the forecast-table cell first."\n'
              'fc["rate_seasonal_naive"] = rate_seasonal_naive(train, train_terminals, HORIZON)\n'
              'scores_all = pd.Series({name: mae(fc[name], actual) for name in fc.columns if name != "actual"}).sort_values()\n'
              'print(scores_all.round(2).to_string())\n\n'
              'fig, ax = plt.subplots()\nax.plot(y.iloc[-30:], color="black", lw=2.5, label="actual")\n'
              'ax.plot(fc.index, fc["naive"], "--", lw=2, label="naive")\nax.plot(fc.index, fc["rate_seasonal_naive"], "--", lw=3, color="#1E9E5A", label="rate seasonal naive")\n'
              'ax.axvspan(actual.index[0], actual.index[-1], color="#F5B83D", alpha=.15)\nax.legend()\nax.set_title("Divide by the size: the rate forecast follows the drop AND the growth")\nplt.show()\n'
              'check("C4", scores_all)',
              'HORIZON = H\n\nassert HORIZON is not None, "✍️ Fill in HORIZON first."\nassert SCORE.get("C3") and "fc" in globals(), "✍️ Get C3 to ✅ and run the forecast-table cell first."\n'
              'fc["rate_seasonal_naive"] = rate_seasonal_naive(train, train_terminals, HORIZON)\n'
              'scores_all = pd.Series({name: mae(fc[name], actual) for name in fc.columns if name != "actual"}).sort_values()\n'
              'print(scores_all.round(2).to_string())\n\n'
              'fig, ax = plt.subplots()\nax.plot(y.iloc[-30:], color="black", lw=2.5, label="actual")\n'
              'ax.plot(fc.index, fc["naive"], "--", lw=2, label="naive")\nax.plot(fc.index, fc["rate_seasonal_naive"], "--", lw=3, color="#1E9E5A", label="rate seasonal naive")\n'
              'ax.axvspan(actual.index[0], actual.index[-1], color="#F5B83D", alpha=.15)\nax.legend()\nax.set_title("Divide by the size: the rate forecast follows the drop AND the growth")\nplt.show()\n'
              'check("C4", scores_all)'),
        ("md", f"""> 📖 **The bar is set.** About {D['times_better']:.0f}× smaller error than naive, with nothing fitted and nothing tuned. Every fancier model from now on must beat **this** number, on the same weeks, with the same scorer."""),

        # ---------------- PART D ----------------
        ("md", """---
# Part D: One split can lie (5 min) 🎲

### D1 ✍️ The flat training average
The code book calls a flat average "the wrong baseline" for a growing series. Try it anyway: say the **mean of the training weeks** every week."""),
        _task('FLAT = ___\n\nassert FLAT is not None, "✍️ Fill in FLAT first."\nassert "fc" in globals(), "✍️ Run the forecast-table cell first."\n'
              'fc["training_mean"] = np.full(H, float(FLAT))\nflat_mae = mae(fc["training_mean"], actual)\n'
              'print(f"flat average {float(FLAT):.1f} every week → MAE {flat_mae:.2f}")\ncheck("D1", flat_mae)',
              'FLAT = train.mean()\n\nassert FLAT is not None, "✍️ Fill in FLAT first."\nassert "fc" in globals(), "✍️ Run the forecast-table cell first."\n'
              'fc["training_mean"] = np.full(H, float(FLAT))\nflat_mae = mae(fc["training_mean"], actual)\n'
              'print(f"flat average {float(FLAT):.1f} every week → MAE {flat_mae:.2f}")\ncheck("D1", flat_mae)'),
        ("md", """> 📖 **Skill or luck?** The flat average "beat" all four code-book baselines on these 8 weeks: the dry-season drop and the network's growth happened to cancel out. One split is one result. **Week 6 · Day 1** (backtesting) checks every method on dozens of different 8-week stretches."""),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: change α, and spot the expo trap
▶️ The cell runs exponential smoothing with three values of `alpha`. ✍️ Which value makes the forecast **follow the latest week closely**?

⚠️ The cell also prints each one's MAE on the test weeks. **Don't** pick `alpha` from those numbers: choosing a setting by looking at the test answers is expo (Week 5 · Day 1). Pick your settings from the training weeks, or keep the default."""),
        _task('assert "train" in globals(), "✍️ Finish A2 first, then run this cell."\n'
              'print(f"last training week: {train.iloc[-1]}")\nfor a in (0.1, 0.3, 0.9):\n'
              '    f = exp_smoothing(train, H, alpha=a)\n    print(f"alpha {a}: level {f[0]:.2f} · MAE on the test weeks {mae(f, actual):.2f}  (look, but don\'t choose with this!)")\n\n'
              'FOLLOWS_LATEST = ___\n\ncheck("BONUS", FOLLOWS_LATEST)',
              'assert "train" in globals(), "✍️ Finish A2 first, then run this cell."\n'
              'print(f"last training week: {train.iloc[-1]}")\nfor a in (0.1, 0.3, 0.9):\n'
              '    f = exp_smoothing(train, H, alpha=a)\n    print(f"alpha {a}: level {f[0]:.2f} · MAE on the test weeks {mae(f, actual):.2f}  (look, but don\'t choose with this!)")\n\n'
              'FOLLOWS_LATEST = 0.9\n\ncheck("BONUS", FOLLOWS_LATEST)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", f"""### 📝 What you learned today
- A **forecast** is a guess about the future made only from the past. Lock the test weeks away and forecast them **blind**.
- **Baselines** are the cheapest forecasts: naive (last week), seasonal naive (same week last year), moving average, exponential smoothing. Each makes one assumption.
- **MAE** is the typical miss in the data's own unit. Naive scored {M['naive']:.2f}: "off by about {M['naive']:.0f} tickets on a typical week".
- Seasonal naive came last ({M['seasonal_naive']:.2f}) on a seasonal series because it copied a network {D['growth'] - 1:.0%} smaller. Naive "won" by copying the wrong season.
- **Divide by the size:** tickets per terminal repeat every year. Last year's rate × today's terminals scored **{M['rate_seasonal_naive']:.2f}**. That's the bar every later model must beat.
- **One split can lie:** even a flat average scored {F['training_mean_mae']:.2f} here. Week 6 · Day 1 tests on many splits.

**Next time:** *Regression forecasts + honest ranges*: "I'm on my way" vs "30 to 90 minutes, Third Mainland Bridge permitting". 🚗

<sub>Data: synthetic teaching dataset from the original Week 6 code book (`Time-series/week-06`). Safe to use with AI tools; real NIGCOMSAT data is not.</sub>"""),
    ]
