"""Week 6 · Day 2: When Will It Break? Remaining Useful Life + Quiz 4."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

import quizkit
import w6forecast as W
from common import BRAND as B
from svgcharts import _scale
from webdeck import logos_title_block
from w6forecast import RUL_CODE, TRAIN_DAYS, day_of_threshold, facts, fit_trend

CODE = "W6D2"
TITLE = "When Will It Break? Remaining Useful Life + Quiz 4"
QUIZ_SEED = 6203

GRID, AXIS = "#24384F", "#9DB0C6"
RED, GOLD, GREEN, GREY = "#FF6B6F", "#F5B83D", "#3CCB7F", "#53657C"
COLS = ("battery_capacity_pct", "twta_gain_db", "propellant_kg")


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


def dt(t, fmt="%d %b %Y"):
    """1 May 2025 (no leading zero)."""
    return pd.Timestamp(t).strftime(fmt).lstrip("0")


# =============================================================================
# EXTRA NUMBERS FOR TODAY (same shared functions as the notebook)
# =============================================================================
@lru_cache(maxsize=1)
def day_facts():
    F = facts()
    _, degr, limits = W.load()
    D = {"degr": degr, "limits": limits}
    bat, gain, prop = degr["battery_capacity_pct"], degr["twta_gain_db"], degr["propellant_kg"]
    D["bat"], D["gain"], D["prop"] = bat, gain, prop
    known = degr.iloc[:TRAIN_DAYS]
    D["train_end"] = degr.index[TRAIN_DAYS - 1]          # 31 Dec 2023: the last day the call may use
    D["call_day"] = degr.index[TRAIN_DAYS]               # 1 Jan 2024: the morning the call is made
    for col in COLS:
        D[f"fit_{col}"] = fit_trend(known[col])
    c = F["rul_calls"]
    # the pepper task: a curve (degree 2) on the same three years
    hit, _ = day_of_threshold(known["battery_capacity_pct"], 80.0, degree=2)
    D["quad_call"] = degr.index[0] + pd.Timedelta(days=hit)
    # how far each call reaches past the data it was fitted on
    D["twta_reach_train"] = (c["twta_gain_db"]["date"] - D["call_day"]).days / 365.25
    D["prop_reach_train"] = (c["propellant_kg"]["unbounded_date"] - D["call_day"]).days / 365.25
    D["twta_reach_end"] = (F["twta_gain_db_repeat"][-1] - degr.index[-1]).days / 365.25
    tw, pr = F["twta_gain_db_repeat"], F["propellant_kg_repeat"]
    D["twta_span_months"] = (max(tw) - min(tw)).days / 30.44
    D["prop_span_days"] = (max(pr) - min(pr)).days
    # the battery call against the two definitions of "crossed"
    call = c["battery_capacity_pct"]["date"]
    D["early_first"] = (F["battery_cross"]["first_dip"] - call).days
    D["early_30"] = (F["battery_cross"]["30_day_mean"] - call).days
    D["prop_above_reserve"] = F["prop_last"] - F["prop_reserve"]
    D["bat_last"] = float(bat.iloc[-1])
    D["gain_last"] = float(gain.iloc[-1])
    return D


# =============================================================================
# LOCAL SVG HELPERS (all drawn from the real file)
# =============================================================================
def _poly(xs, ys, X, Y):
    return "M" + " L".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in zip(xs, ys))


def mini_svg(v, *, thr, lab, lo, hi, color, w=440, h=270, delay=".3s", lab_left=False):
    """One channel, five years, with its operational limit."""
    v = np.asarray(v, float)
    n = len(v)
    L, R, T, Bm = 12, w - 12, 16, h - 38

    def X(i):
        return _scale(i, 0, n - 1, L, R)

    def Y(y):
        return _scale(y, lo, hi, Bm, T)
    idx = np.arange(0, n, 3)
    yt = Y(thr)
    ly = yt + 30 if lab_left else (yt - 10 if yt > T + 40 else yt + 30)
    lx, anchor = (L, "start") if lab_left else (R, "end")
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block">'
            f'<line x1="{L}" x2="{R}" y1="{Bm}" y2="{Bm}" stroke="{GRID}" stroke-width="2"/>'
            f'<line x1="{L}" x2="{R}" y1="{yt:.1f}" y2="{yt:.1f}" stroke="{RED}" stroke-width="3" stroke-dasharray="9 7"/>'
            f'<text x="{lx}" y="{ly:.1f}" fill="{RED}" font-size="22" font-weight="800" text-anchor="{anchor}">{lab}</text>'
            f'<path class="draw" style="--dur:2.2s;--d:{delay}" d="{_poly(idx, v[idx], X, Y)}" fill="none" stroke="{color}" '
            f'stroke-width="3.5" stroke-linejoin="round"/>'
            f'<text x="{L}" y="{h - 8}" fill="{AXIS}" font-size="19">2021</text>'
            f'<text x="{R}" y="{h - 8}" fill="{AXIS}" font-size="19" text-anchor="end">2025</text></svg>')


def stairs_svg(D, F, days=120, w=1420, h=330):
    """The first months of propellant: flat, step, flat, step."""
    p = D["prop"].iloc[:days]
    v = p.values
    lo, hi = v.min() - .15, v.max() + .15
    L, R, T, Bm = 90, w - 20, 20, h - 46

    def X(i):
        return _scale(i, 0, days - 1, L, R)

    def Y(y):
        return _scale(y, lo, hi, Bm, T)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block">']
    for yv in np.arange(np.ceil(lo * 2) / 2, hi, .5):
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}"/>'
                 f'<text x="{L - 12}" y="{Y(yv) + 7:.1f}" fill="{AXIS}" font-size="19" text-anchor="end">{yv:.1f}</text>')
    o.append(f'<path class="draw" style="--dur:2.6s;--d:.3s" d="{_poly(range(days), v, X, Y)}" fill="none" stroke="{B["teal_d"]}" stroke-width="3.5"/>')
    for m in range(1, 5):
        i = (pd.Timestamp(2021, m, 1) - p.index[0]).days
        o.append(f'<text x="{X(i):.1f}" y="{h - 12}" fill="{AXIS}" font-size="19" text-anchor="{"start" if i == 0 else "middle"}">{pd.Timestamp(2021, m, 1):%b} 2021</text>')
    o.append(f'<text x="{R}" y="{T + 18}" fill="{AXIS}" font-size="19" text-anchor="end">kg of propellant left</text></svg>')
    return "".join(o)


def rul_svg(D, F, w=1420, h=470):
    """Fit a line on the 3 known years, extend it to the 80% floor, then (step) what really happened."""
    bat = D["bat"].values
    n = len(bat)
    model = D["fit_battery_capacity_pct"][0]
    hit = F["rul_calls"]["battery_capacity_pct"]["day"]
    lo, hi = 76, 101
    L, R, T, Bm = 80, w - 30, 24, h - 52

    def X(i):
        return _scale(i, 0, n - 1, L, R)

    def Y(y):
        return _scale(y, lo, hi, Bm, T)
    k = TRAIN_DAYS
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block">',
         f'<rect x="{L}" y="{T}" width="{X(k - 1) - L:.1f}" height="{Bm - T}" fill="{B["blue_d"]}" fill-opacity=".09" rx="8"/>',
         f'<text x="{(L + X(k - 1)) / 2:.1f}" y="{Bm - 18}" fill="{B["blue_d"]}" font-size="22" font-weight="800" text-anchor="middle">the 3 years we know</text>']
    for yv in (80, 85, 90, 95, 100):
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}"/>'
                 f'<text x="{L - 12}" y="{Y(yv) + 7:.1f}" fill="{AXIS}" font-size="19" text-anchor="end">{yv}%</text>')
    for yr in range(2021, 2026):
        i = (pd.Timestamp(yr, 1, 1) - D["degr"].index[0]).days
        o.append(f'<text x="{X(i):.1f}" y="{h - 16}" fill="{AXIS}" font-size="20" text-anchor="{"start" if i == 0 else "middle"}">{yr}</text>')
    o.append(f'<line x1="{L}" x2="{R}" y1="{Y(80):.1f}" y2="{Y(80):.1f}" stroke="{RED}" stroke-width="3" stroke-dasharray="10 8"/>'
             f'<text x="{L + 14}" y="{Y(80) + 30:.1f}" fill="{RED}" font-size="22" font-weight="800">80% floor</text>')
    idx = np.arange(0, k, 3)
    o.append(f'<path class="draw" style="--dur:2s;--d:.3s" d="{_poly(idx, bat[idx], X, Y)}" fill="none" stroke="{B["blue_d"]}" stroke-width="3"/>')
    xs = np.array([0, hit + 40])
    o.append(f'<path class="draw" style="--dur:1.6s;--d:1.9s" d="{_poly(xs, model(xs), X, Y)}" fill="none" stroke="{GOLD}" stroke-width="5" stroke-linecap="round"/>')
    o.append(f'<line x1="{X(k):.1f}" x2="{X(k):.1f}" y1="{T}" y2="{Bm}" stroke="#EAF2FB" stroke-width="2" stroke-dasharray="6 6"/>'
             f'<text x="{X(k) + 10:.1f}" y="{T + 26}" fill="#EAF2FB" font-size="21" font-weight="700">📅 the call is made: {dt(D["call_day"])}</text>')
    x, y = X(hit), Y(80)
    o.append(f'<g class="anim a-pop" style="--d:3.4s;transform-origin:{x:.0f}px {y:.0f}px"><circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{GOLD}" stroke="{B["space"]}" stroke-width="3"/>'
             f'<text x="{x - 22:.1f}" y="{y + 46:.1f}" fill="{GOLD}" font-size="26" font-weight="800" text-anchor="end" stroke="#12233A" stroke-width="8" stroke-linejoin="round" paint-order="stroke">line hits 80% → {dt(F["rul_calls"]["battery_capacity_pct"]["date"])}</text></g>')
    idx2 = np.arange(k, n, 3)
    o.append(f'<g class="step" data-step="1"><path d="{_poly(idx2, bat[idx2], X, Y)}" fill="none" stroke="#9DB0C6" stroke-width="2.5" stroke-opacity=".8"/>'
             f'<text x="{R}" y="{Y(bat[-1]) + 34:.1f}" fill="#C9D6E5" font-size="21" font-weight="700" text-anchor="end">what really happened next</text></g>')
    o.append("</svg>")
    return "".join(o)


def prop_svg(D, F, w=1420, h=440):
    """Propellant: the line runs past the end of the 4,000-day search before it reaches 5 kg."""
    c = F["rul_calls"]["propellant_kg"]
    d0 = D["degr"].index[0]
    cross = (c["unbounded_date"] - d0).days
    stop = (c["search_end"] - d0).days
    n = cross + 260
    p = D["prop"].values
    model = D["fit_propellant_kg"][0]
    lo, hi = 0, 155
    L, R, T, Bm = 80, w - 30, 24, h - 52

    def X(i):
        return _scale(i, 0, n - 1, L, R)

    def Y(y):
        return _scale(y, lo, hi, Bm, T)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block">',
         f'<rect x="{L}" y="{T}" width="{X(stop) - L:.1f}" height="{Bm - T}" fill="{B["blue_d"]}" fill-opacity=".07" rx="8"/>']
    for yv in (0, 50, 100, 150):
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}"/>'
                 f'<text x="{L - 12}" y="{Y(yv) + 7:.1f}" fill="{AXIS}" font-size="19" text-anchor="end">{yv}</text>')
    for yr in range(2021, 2037, 3):
        i = (pd.Timestamp(yr, 1, 1) - d0).days
        o.append(f'<text x="{X(i):.1f}" y="{h - 16}" fill="{AXIS}" font-size="20" text-anchor="{"start" if i == 0 else "middle"}">{yr}</text>')
    o.append(f'<line x1="{L}" x2="{R}" y1="{Y(5):.1f}" y2="{Y(5):.1f}" stroke="{RED}" stroke-width="3" stroke-dasharray="10 8"/>'
             f'<text x="{L + 14}" y="{Y(5) - 12:.1f}" fill="{RED}" font-size="22" font-weight="800">5 kg de-orbit reserve</text>')
    idx = np.arange(0, TRAIN_DAYS, 4)
    o.append(f'<path class="draw" style="--dur:1.4s;--d:.3s" d="{_poly(idx, p[idx], X, Y)}" fill="none" stroke="{B["teal_d"]}" stroke-width="4"/>')
    xs = np.array([0, n - 1])
    o.append(f'<path class="draw" style="--dur:2.4s;--d:1.5s" d="{_poly(xs, model(xs), X, Y)}" fill="none" stroke="{GOLD}" stroke-width="4" stroke-linecap="round"/>')
    o.append(f'<g class="anim a-fade" style="--d:3s"><line x1="{X(stop):.1f}" x2="{X(stop):.1f}" y1="{T}" y2="{Bm}" stroke="#EAF2FB" stroke-width="3" stroke-dasharray="7 6"/>'
             f'<text x="{X(stop) - 12:.1f}" y="{T + 30}" fill="#EAF2FB" font-size="22" font-weight="800" text-anchor="end">🛑 the 4,000-day search stops: {dt(c["search_end"])}</text></g>')
    x, y = X(cross), Y(5)
    o.append(f'<g class="step" data-step="1"><circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{GOLD}" stroke="{B["space"]}" stroke-width="3"/>'
             f'<text x="{x - 6:.1f}" y="{y - 72:.1f}" fill="{GOLD}" font-size="26" font-weight="800" text-anchor="end" stroke="#12233A" stroke-width="8" stroke-linejoin="round" paint-order="stroke">line reaches 5 kg: {dt(c["unbounded_date"])}</text>'
             f'<path d="M{x - 20:.1f} {y - 62:.1f} L{x - 4:.1f} {y - 18:.1f}" stroke="{GOLD}" stroke-width="3"/></g>')
    o.append("</svg>")
    return "".join(o)


def cross_svg(D, F, w=1420, h=440):
    """2025, day by day: when did the battery 'cross' 80%?"""
    bat = D["bat"]
    s = bat.loc["2025-03-01":"2025-09-15"]
    r30 = bat.rolling(30).mean().loc[s.index]
    n = len(s)
    lo, hi = np.floor(s.min() * 2) / 2, np.ceil(s.max() * 2) / 2
    L, R, T, Bm = 90, w - 24, 70, h - 50

    def X(i):
        return _scale(i, 0, n - 1, L, R)

    def Y(y):
        return _scale(y, lo, hi, Bm, T)

    def I(t):
        return s.index.get_loc(pd.Timestamp(t))
    cr = F["battery_cross"]
    i0, i1, i2 = I(cr["first_dip"]), I(cr["30_day_mean"]), I(cr["last_good_day"])
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block">',
         f'<rect class="anim a-fade" style="--d:2.2s" x="{X(i0):.1f}" y="{T}" width="{X(i2) - X(i0):.1f}" height="{Bm - T}" fill="{GOLD}" fill-opacity=".2" rx="8"/>']
    for yv in np.arange(lo, hi + .01, .5):
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}"/>'
                 f'<text x="{L - 12}" y="{Y(yv) + 7:.1f}" fill="{AXIS}" font-size="19" text-anchor="end">{yv:.1f}%</text>')
    for m in range(3, 10):
        i = I(pd.Timestamp(2025, m, 1)) if pd.Timestamp(2025, m, 1) in s.index else None
        if i is not None:
            o.append(f'<text x="{X(i):.1f}" y="{h - 14}" fill="{AXIS}" font-size="20" text-anchor="{"start" if i == 0 else "middle"}">{pd.Timestamp(2025, m, 1):%b}</text>')
    o.append(f'<line x1="{L}" x2="{R}" y1="{Y(80):.1f}" y2="{Y(80):.1f}" stroke="{RED}" stroke-width="3" stroke-dasharray="10 8"/>')
    dots = []
    for i, v in enumerate(s.values):
        col = RED if v < 80 else B["blue_d"]
        dots.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4.2" fill="{col}"/>')
    o.append(f'<g class="anim a-fade" style="--d:.3s">{"".join(dots)}</g>')
    o.append(f'<path class="draw" style="--dur:2s;--d:.9s" d="{_poly(range(n), r30.values, X, Y)}" fill="none" stroke="{B["teal_d"]}" stroke-width="4.5"/>')
    for k, (i, lab, col) in enumerate(((i0, f"① first dip: {dt(cr['first_dip'], '%d %b')}", GOLD),
                                       (i1, f"② 30-day mean: {dt(cr['30_day_mean'], '%d %b')}", B["teal_d"]),
                                       (i2, f"③ last good day: {dt(cr['last_good_day'], '%d %b')}", GREEN))):
        o.append(f'<g class="anim a-pop" style="--d:{2.4 + .4 * k:.1f}s;transform-origin:{X(i):.0f}px {T}px">'
                 f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{T - 8}" y2="{Bm}" stroke="{col}" stroke-width="3"/>'
                 f'<text x="{X(i):.1f}" y="{T - 18}" fill="{col}" font-size="22" font-weight="800" text-anchor="{["end", "middle", "start"][k]}">{lab}</text></g>')
    o.append("</svg>")
    return "".join(o)


def calls_svg(D, F, w=1420):
    """The battery call made from 4 starting points: when it was made, where it landed, the real window."""
    rep = F["battery_repeat"]
    cr = F["battery_cross"]
    t0, t1 = pd.Timestamp("2021-10-01"), pd.Timestamp("2025-10-01")
    L, R, top, rh = 250, w - 330, 46, 84
    h = top + len(rep) * rh + 50

    def X(t):
        return L + (pd.Timestamp(t) - t0).days / (t1 - t0).days * (R - L)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block">',
         f'<rect x="{X(cr["first_dip"]):.1f}" y="{top - 14}" width="{X(cr["last_good_day"]) - X(cr["first_dip"]):.1f}" height="{h - top - 30}" fill="{GOLD}" fill-opacity=".3" rx="6"/>',
         f'<text x="{X(cr["first_dip"]) - 8:.1f}" y="{top - 22}" fill="{GOLD}" font-size="19" font-weight="800" text-anchor="end">the real crossing window</text>',
         f'<text x="{R + 24}" y="{top - 22}" fill="{AXIS}" font-size="18" font-weight="700">warning · vs first dip · vs 30-day</text>']
    for yr in range(2022, 2026):
        o.append(f'<text x="{X(pd.Timestamp(yr, 1, 1)):.1f}" y="{h - 10}" fill="{AXIS}" font-size="20" text-anchor="middle">{yr}</text>'
                 f'<line x1="{X(pd.Timestamp(yr, 1, 1)):.1f}" x2="{X(pd.Timestamp(yr, 1, 1)):.1f}" y1="{top - 10}" y2="{h - 38}" stroke="{GRID}"/>')
    for k, r in rep.iterrows():
        y = top + k * rh + 30
        a, b = X(r["call_made_on"]), X(r["predicted_crossing"])
        d = .3 + k * .45
        col = GREEN if abs(r["days_vs_first_dip"]) <= 15 else GOLD
        o.append(f'<g class="anim a-left" style="--d:{d:.2f}s">'
                 f'<text x="0" y="{y + 8}" fill="#EAF2FB" font-size="23" font-weight="800">{r["years_of_data"]} year{"s" if r["years_of_data"] > 1 else ""} of data</text>'
                 f'<line x1="{a:.1f}" x2="{b:.1f}" y1="{y}" y2="{y}" stroke="{B["blue_d"]}" stroke-width="5"/>'
                 f'<circle cx="{a:.1f}" cy="{y}" r="11" fill="{B["blue_d"]}"/>'
                 f'<path d="M{b:.1f} {y - 15} L{b + 15:.1f} {y} L{b:.1f} {y + 15} L{b - 15:.1f} {y} Z" fill="{col}"/>'
                 f'<text x="{R + 24}" y="{y + 8}" fill="#EAF2FB" font-size="22" font-weight="700">{r["warning_days"]:,} d · '
                 f'<tspan fill="{col}">{r["days_vs_first_dip"]:+d}</tspan> · <tspan fill="{GOLD}">{r["days_vs_30_day_mean"]:+d}</tspan></text></g>')
    o.append(f'<text x="{R + 24}" y="{h - 10}" fill="{AXIS}" font-size="18">🔵 call made · 🔶 predicted crossing</text>')
    o.append("</svg>")
    return "".join(o)


def hbars_svg(rows, total, w=1420, unit="", fmt="{:.1f}", L=470):
    """rows: [(label, value, colour)] as horizontal bars out of `total`."""
    R, rh = w - 170, 66
    h = len(rows) * rh + 10
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block">']
    for k, (lab, v, col) in enumerate(rows):
        y = k * rh + 8
        bw = max(abs(v) / total * (R - L), 3)
        o.append(f'<g class="anim a-left" style="--d:{.3 + k * .25:.2f}s"><text x="0" y="{y + 33}" fill="#EAF2FB" font-size="24" font-weight="700">{lab}</text>'
                 f'<rect x="{L}" y="{y + 6}" width="{R - L}" height="40" rx="8" fill="#12233A"/>'
                 f'<rect x="{L}" y="{y + 6}" width="{bw:.1f}" height="40" rx="8" fill="{col}"/>'
                 f'<text x="{L + bw + 14:.1f}" y="{y + 36}" fill="{col}" font-size="27" font-weight="800">{fmt.format(v)}{unit}</text></g>')
    o.append("</svg>")
    return "".join(o)


def reach_svg(dates, labels, t0, t1, *, marks=(), color=GOLD, w=1300, h=164):
    """Calls made from different amounts of data, on one timeline."""
    L, R = 30, w - 30

    def X(t):
        return L + (pd.Timestamp(t) - t0).days / (t1 - t0).days * (R - L)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block">',
         f'<line x1="{L}" x2="{R}" y1="78" y2="78" stroke="{GRID}" stroke-width="4"/>']
    m = pd.Timestamp(t0.year, t0.month, 1)
    while m <= t1:
        if m >= t0:
            o.append(f'<line x1="{X(m):.1f}" x2="{X(m):.1f}" y1="70" y2="86" stroke="{AXIS}" stroke-width="2"/>'
                     f'<text x="{X(m):.1f}" y="{h - 6}" fill="{AXIS}" font-size="18" text-anchor="middle">{m:%b %y}</text>')
        m = m + pd.DateOffset(months=1)
    groups = []                                   # calls within 12 days share one label
    for t, lab in sorted(zip(dates, labels)):
        if groups and (t - groups[-1][-1][0]).days <= 12:
            groups[-1].append((t, lab))
        else:
            groups.append([(t, lab)])
    for k, g in enumerate(groups):
        up = k % 2 == 0
        for j, (t, _) in enumerate(g):
            x = X(t)
            o.append(f'<circle class="anim a-pop" style="--d:{.3 + k * .3 + j * .1:.1f}s;transform-origin:{x:.0f}px 78px" cx="{x:.1f}" cy="78" r="12" '
                     f'fill="{color}" stroke="{B["space"]}" stroke-width="3"/>')
        xm = sum(X(t) for t, _ in g) / len(g)
        o.append(f'<text class="anim a-fade" style="--d:{.4 + k * .3:.1f}s" x="{xm:.1f}" y="{44 if up else 120}" fill="{color}" font-size="20" '
                 f'font-weight="800" text-anchor="middle">{" · ".join(lab for _, lab in sorted(g, key=lambda p: p[1]))}</text>')
    for t, lab, col in marks:
        x = X(t)
        o.append(f'<g class="anim a-pop" style="--d:2s;transform-origin:{x:.0f}px 78px"><rect x="{x - 11:.1f}" y="67" width="22" height="22" fill="{col}" transform="rotate(45 {x:.1f} 78)"/>'
                 f'<text x="{x + 20:.1f}" y="40" fill="{col}" font-size="20" font-weight="800">{lab}</text></g>')
    o.append("</svg>")
    return "".join(o)


def gauge_svg(size=470):
    """Illustration (not data): a fuel gauge, needle sliding towards E."""
    c, r = size / 2, size / 2 - 50
    o = [f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}">']
    for k in range(9):
        a = np.pi + k / 8 * np.pi
        x1, y1 = c + (r - 6) * np.cos(a), c + (r - 6) * np.sin(a)
        x2, y2 = c + (r - 38) * np.cos(a), c + (r - 38) * np.sin(a)
        col = RED if k <= 1 else "#C9D6E5"
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{8 if k % 4 == 0 else 5}" stroke-linecap="round"/>')
    o.append(f'<path d="M{c - r:.1f} {c:.1f} A{r} {r} 0 0 1 {c + r:.1f} {c:.1f}" fill="none" stroke="#24384F" stroke-width="10"/>')
    o.append(f'<text x="{c - r + 18:.1f}" y="{c + 52:.1f}" fill="{RED}" font-size="46" font-weight="800">E</text>'
             f'<text x="{c + r - 48:.1f}" y="{c + 52:.1f}" fill="#C9D6E5" font-size="46" font-weight="800">F</text>')
    a = np.pi + 0.16 * np.pi
    nx, ny = c + (r - 46) * np.cos(a), c + (r - 46) * np.sin(a)
    o.append(f'<path class="draw" style="--d:.8s;--dur:1.4s" d="M{c:.1f} {c:.1f} L{nx:.1f} {ny:.1f}" stroke="{GOLD}" stroke-width="12" stroke-linecap="round"/>'
             f'<circle cx="{c}" cy="{c}" r="22" fill="{GOLD}"/>'
             f'<text x="{c}" y="{c + 120}" font-size="96" text-anchor="middle" class="anim a-pop" style="--d:1.6s;transform-origin:{c}px {c + 90}px">🛰️</text></svg>')
    return "".join(o)


TABLE_CSS = ("<style>.sb{width:100%;border-collapse:separate;border-spacing:0 6px;font-size:23px}"
             ".sb th{color:#9DB0C6;font-size:18px;text-align:left;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:0 14px}"
             ".sb td{background:#12233A;padding:9px 14px}.sb td:first-child{border-radius:14px 0 0 14px}"
             ".sb td:last-child{border-radius:0 14px 14px 0}.sb tr.win td{background:#123A33}.sb tr.bad td{background:#3A1A22}</style>")


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    F = facts()
    D = day_facts()
    c = F["rul_calls"]
    cb, ca, cp = c["battery_capacity_pct"], c["twta_gain_db"], c["propellant_kg"]
    cr = F["battery_cross"]
    burns = F["burns"]
    rep = F["battery_repeat"]
    sl = F["battery_slope_by_year"]
    tw, pr = F["twta_gain_db_repeat"], F["propellant_kg_repeat"]
    slope_b = D["fit_battery_capacity_pct"][1][0] * 365

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:60px;top:140px">{gauge_svg()}</div>
<div style="max-width:900px;margin-top:40px">
  <div class="kicker anim">Week 6 · Day 2</div>
  <h1 class="anim" style="--d:.2s">When Will<br>It Break? <span class="hl">⛽</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Remaining useful life: draw the trend, find the limit,<br>and say <b class="hl">when</b>, honestly. Then <b>Quiz 4</b>. 📝</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex">{logos_title_block()}</div>
</div>""",
          "Last teaching day of the course. Weeks 3 to 5 asked 'is this reading wrong now?'. Yesterday and the day before asked 'what happens next week?'. "
          "Today asks the question a fleet manager loses sleep over: how long until this part reaches its limit? Then Quiz 4."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Find the limit. Draw the line. Check the call.</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:290px;padding:40px 26px"><div class="icon">📉</div><h3>Three shapes</h3><p class="small">how parts grow old</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:290px;padding:40px 26px"><div class="icon">📏</div><h3>Draw the line</h3><p class="small">trend to threshold</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:290px;padding:40px 26px"><div class="icon">🔍</div><h3>Check the call</h3><p class="small">was the battery right?</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:250px;padding:40px 26px"><div class="icon">📝</div><h3>Quiz 4</h3><p class="small">forecasting + remaining life</p></div>
</div>
<div class="row anim" style="--d:1.8s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 45 min hands-on</span><span class="pill gold">📝 20 min quiz</span><span class="pill">🏁 15 min mark + wrap</span>
</div>""",
          "Four moves, same rhythm as Quiz 3 day: the quiz sits after the hands-on."),

        # 3 ─ hook: the danfo driver
        S("""
<div class="kicker anim">Quick question</div>
<h2 class="anim" style="--d:.1s">“Driver, fuel go reach Ojota?” 🚐</h2>
<div class="row" style="gap:40px;margin-top:20px;align-items:stretch">
  <div class="card anim a-left" style="--d:.3s;flex:1"><div class="icon">🧑🏾‍✈️</div><h3>The danfo driver's sum</h3>
    <p class="muted">He doesn't guess. He looks at the gauge, remembers what one trip burns, and divides.</p>
    <pre class="code" style="font-size:25px;margin-top:16px">litres_left   = 20
litres_a_trip = 4
trips_left    = 20 / 4   # 5 trips</pre></div>
  <div class="card anim a-right" style="--d:.7s;flex:1;border-color:#F5B83D"><div class="icon">⛽</div><h3>That is remaining useful life</h3>
    <p class="muted">How much is left <b style="color:#fff">above the limit</b>, divided by how fast it is going.</p>
    <p class="step" data-step="1" style="font-size:27px;margin-top:22px">And the smart driver fills up <b class="hl">before</b> the light comes on, not at Ojota under the bridge. 😅</p></div>
</div>""",
          "Let the room enjoy the danfo driver: he does remaining-useful-life sums every day without the name. The numbers on this slide are a story, not data. "
          "Two ideas to plant: RUL = what's left above the limit ÷ how fast it's going; and you act before the crossing, not on it (Quiz 4 question 24)."),

        # 4 ─ the national question
        S("""
<div class="kicker anim">Why this matters to NIGCOMSAT</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Remaining useful life is a national question 🇳🇬</h2>
<div class="grid3" style="margin-top:24px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="icon">🚀</div><h3>December 2011</h3><p class="muted">NigComSat-1R launched to 42.5° East</p></div>
  <div class="card anim a-pop" style="--d:.55s;text-align:center"><div class="icon">⏳</div><h3>15-year design life</h3><p class="muted">2011 + 15 ≈ 2026</p></div>
  <div class="card anim a-pop" style="--d:.8s;text-align:center"><div class="icon">🛰️</div><h3>2028 · 2029</h3><p class="muted">targets for NIGCOMSAT-2A and 2B</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:34px;text-align:center">Will the battery, the amplifiers and the fuel hold until the new ones arrive?<br>That is a <b class="hl">trend-to-threshold</b> question.</p>
<p class="small anim" style="--d:1.5s;margin-top:18px;text-align:center">Today's data: a <b>synthetic</b> GEO platform made for teaching. Same questions, made-up numbers. Not NigComSat-1R telemetry.</p>""",
          "Facts from the toolkit fact sheet: NigComSat-1R launched in December 2011, 15-year design life; NIGCOMSAT-2A and 2B are targeted for 2028 and 2029 (agency targets, earlier plans slipped). "
          "Be very clear that our file is synthetic: it continues the Week 5 platform, it is not real NigComSat-1R telemetry."),

        # 5 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">Three ways to grow old 📉</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">One satellite, three parts, three limits.</p>""",
          "Section break.", cls="center"),

        # 6 ─ three shapes
        S(f"""
<div class="kicker anim">degradation_assets_daily · {F["degr_span"][2]:,} days · {dt(F["degr_span"][0])} – {dt(F["degr_span"][1])}</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Same satellite, three shapes</h2>
<div class="grid3" style="margin-top:8px;gap:22px">
  <div class="card anim a-pop" style="--d:.3s;padding:22px 22px 16px"><h3 style="margin:0 0 6px">🔋 Battery capacity</h3>
    {mini_svg(D["bat"], thr=80, lab="80% floor", lo=76, hi=101, color=B["blue_d"], delay=".5s", lab_left=True)}
    <p class="small" style="margin-top:8px">Curves down. <b class="hl">Almost at its floor.</b></p></div>
  <div class="card anim a-pop" style="--d:.55s;padding:22px 22px 16px"><h3 style="margin:0 0 6px">📡 Amplifier gain</h3>
    {mini_svg(D["gain"], thr=-2.0, lab="−2 dB floor", lo=-2.25, hi=.3, color=B["teal_d"], delay=".8s")}
    <p class="small" style="margin-top:8px">Fades slowly, in a straight line. Far from its floor.</p></div>
  <div class="card anim a-pop" style="--d:.8s;padding:22px 22px 16px"><h3 style="margin:0 0 6px">⛽ Propellant</h3>
    {mini_svg(D["prop"], thr=5.0, lab="5 kg reserve", lo=0, hi=158, color=GOLD, delay="1.1s")}
    <p class="small" style="margin-top:8px">Steps down at every burn. Far from its reserve.</p></div>
</div>
<p class="anim" style="--d:1.6s;margin-top:18px;text-align:center">The limits come from <code>degradation_thresholds.csv</code>: they are <b class="hl">known up front</b>, not forecast.</p>""",
          f"Battery capacity in % of new, its floor 80% (below it the battery can't safely carry the eclipse-season discharge). Amplifier gain in dB, floor −2 dB (below it the link budget loses its margin). "
          f"Propellant in kg, reserve 5 kg kept for the end-of-mission de-orbit burn. Last readings: battery {D['bat_last']:.2f}%, gain {D['gain_last']:.3f} dB, propellant {F['prop_last']:.2f} kg. "
          "Ask: which one would you worry about first? (The battery: it is already touching its floor.)"),

        # 7 ─ the staircase
        S(f"""
<div class="kicker anim">Zoom in: propellant, the first four months</div>
<h2 class="anim" style="--d:.1s;font-size:54px">A staircase, not a slope 🪜</h2>
<div class="card anim" style="--d:.2s;padding:20px 24px">{stairs_svg(D, F)}</div>
<div class="grid4" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:1.2s;text-align:center;padding:18px"><div class="stat hl" style="font-size:64px">~{burns["days_between"]:.0f}</div><div class="stat-label">days between burns</div></div>
  <div class="card anim a-pop" style="--d:1.4s;text-align:center;padding:18px"><div class="stat hl" style="font-size:64px">{burns["kg_each"]:.2f}</div><div class="stat-label">kg per burn (typical)</div></div>
  <div class="card anim a-pop" style="--d:1.6s;text-align:center;padding:18px"><div class="stat hl" style="font-size:64px">~{burns["per_year"]:.0f}</div><div class="stat-label">burns a year</div></div>
  <div class="card anim a-pop" style="--d:1.8s;text-align:center;padding:18px"><div class="stat hl" style="font-size:64px">{F["prop_kg_per_year"]:.2f}</div><div class="stat-label">kg used a year</div></div>
</div>""",
          f"A geostationary satellite drifts, so every couple of weeks the thrusters fire to put it back in its box: a station-keeping burn. Between burns the reading only wobbles (gauge noise). "
          f"Across the five years we count {burns['n']} burns, about one every {burns['days_between']:.0f} days. A straight line through a staircase is an approximation: fine over years, wrong between two burns. "
          "Quiz 4 question 23."),

        # 8 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Draw the line 📏</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Fit the trend on the past. Extend it until it hits the limit.</p>""",
          "Section break.", cls="center"),

        # 9 ─ trend to threshold
        S(f"""
<div class="kicker anim">Trend-to-threshold · stand on {dt(D["call_day"])} with 3 years of data</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Where does the line hit the floor?</h2>
<div class="card anim" style="--d:.2s;padding:20px 24px">{rul_svg(D, F)}</div>
<p class="anim" style="--d:3.6s;margin-top:16px;text-align:center">Slope: <b class="hl">{slope_b:.2f}% a year</b>. Remaining useful life on the day of the call: <b class="hl">{(cb["date"] - D["call_day"]).days} days</b> (about {(cb["date"] - D["call_day"]).days / 30.44:.0f} months).</p>""",
          f"The code book's honest rule: make the call using only the first three years (1 Jan 2021 – {dt(D['train_end'])}), as if it were the morning of {dt(D['call_day'])}. "
          f"np.polyfit draws the best straight line, {slope_b:.2f} percentage points a year. Extend it: it reaches 80% on {dt(cb['date'])}. "
          "Click once to reveal what the battery really did next. Remaining useful life = the time from the call to that crossing."),

        # 10 ─ the code
        S(f"""
<div class="kicker anim">The whole method is two small functions</div>
<h2 class="anim" style="--d:.1s;font-size:54px">fit_trend + day_of_threshold</h2>
<pre class="code anim" style="--d:.3s;font-size:23px">x = np.arange(len(series))                  # day number 0, 1, 2, ...
slope, intercept = np.polyfit(x, series.values, 1)   # the best straight line

line = np.poly1d([slope, intercept])
future = line(np.arange(len(series) + 4000))         # extend it 4,000 days
crossed = future &lt; threshold                         # True where it is below the limit
day = np.argmax(crossed)                             # the FIRST True</pre>
<div class="grid2" style="margin-top:22px;gap:24px">
  <div class="card anim a-left" style="--d:.9s;padding:20px 26px"><p style="font-size:25px"><code>np.polyfit(x, y, 1)</code> gives <b class="hl">slope and intercept</b>: two numbers for a straight line.</p></div>
  <div class="card anim a-right" style="--d:1.2s;padding:20px 26px"><p style="font-size:25px"><code>np.argmax</code> of True/False returns the position of the <b class="hl">first True</b>. Remember that. 👀</p></div>
</div>""",
          "Quiz 4 question 20: np.polyfit(x, y, 1) returns the slope and intercept. Walk through the six lines slowly. The argmax line is where the original code book trips up on the next slides."),

        # 11 ─ the three calls
        S(f"""
<div class="kicker anim">The code book's calls · 3 years of data each</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Two sensible dates… and one strange one</h2>
<div class="grid3" style="margin-top:26px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="icon">🔋</div><h3>Battery → 80%</h3><div class="stat good" style="font-size:66px">{dt(cb["date"])}</div></div>
  <div class="card anim a-pop" style="--d:.6s;text-align:center"><div class="icon">📡</div><h3>Amplifier → −2 dB</h3><div class="stat good" style="font-size:66px">{dt(ca["date"])}</div></div>
  <div class="card anim a-pop glow" style="--d:.9s;text-align:center;border-color:#E5484D"><div class="icon">⛽</div><h3>Propellant → 5 kg</h3><div class="stat bad pulse" style="font-size:66px">{dt(cp["original_print"])}</div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:34px;text-align:center">{dt(cp["original_print"])} is the <b class="bad">first day of the data</b>.<br>The fuel ran out before the satellite even started? 🤔</p>""",
          f"These are the three dates the original code book prints. Battery {dt(cb['date'])} and amplifier {dt(ca['date'])} look reasonable. Propellant prints {dt(cp['original_print'])}: "
          "day 0. Ask the room what went wrong before you show the next slide."),

        # 12 ─ the bug
        S(f"""
<div class="kicker anim">The bug · Week 6 code book, topic 6.4</div>
<h2 class="anim" style="--d:.1s;font-size:54px">np.argmax of “never” is 0 🐞</h2>
<div class="row" style="gap:36px;margin-top:14px">
  <div class="col" style="flex:1.1;gap:18px">
    <pre class="code anim" style="--d:.3s;font-size:23px">crossed = [False, False, False, False]
np.argmax(crossed)        # 0 !!!

# FIXED in day_of_threshold:
if not crossed.any():
    return None           # "no crossing"</pre>
  </div>
  <div class="col" style="flex:.9;gap:18px">
    <div class="card anim a-right" style="--d:.7s;padding:22px 26px"><p style="font-size:25px">The line never reaches 5 kg inside the 4,000-day search (it stops on <b>{dt(cp["search_end"])}</b>). Every value is False, and <code>argmax</code> quietly says <b class="bad">0</b>.</p></div>
    <div class="card anim a-right glow" style="--d:1.1s;padding:22px 26px"><p style="font-size:25px">Honest answer: <b class="hl">“no crossing before {dt(cp["search_end"])}”</b>. Then look further.</p></div>
  </div>
</div>""",
          f"np.argmax returns the position of the largest value. For True/False, True is the largest, so it finds the first True. If there is no True at all, every value ties and argmax returns position 0, "
          f"which the code turns into day 0 = {dt(cp['original_print'])}. No error, no warning: a confident wrong date. Our day_of_threshold checks crossed.any() first and returns None. "
          "Lesson: a function that can't fail loudly needs you to check its 'nothing found' case."),

        # 13 ─ look further
        S(f"""
<div class="kicker anim">Propellant · fitted on the same 3 years</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The line gets there, just later 🔭</h2>
<div class="card anim" style="--d:.2s;padding:20px 24px">{prop_svg(D, F)}</div>
<p class="anim" style="--d:3.4s;margin-top:16px;text-align:center">Solve the line directly: <code>day = (5 − intercept) / slope</code> → <b class="hl">{dt(cp["unbounded_date"])}</b>, about {D["prop_reach_train"]:.0f} years past the data it was fitted on.</p>""",
          f"The 3-year line falls {abs(cp['slope_per_year']):.2f} kg a year. It reaches 5 kg on {dt(cp['unbounded_date'])}, just under a year after the search window ended. "
          "A straight line can be solved for the crossing with one subtraction and one division: no search needed. Click to show the crossing point."),

        # 14 ─ fuel-gauge sum
        S(f"""
<div class="kicker anim">The danfo driver's check</div>
<h2 class="anim" style="--d:.1s">The fuel-gauge sum agrees ⛽</h2>
<div class="flow" style="margin-top:44px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:260px;padding:34px 22px"><div class="icon">🛢️</div><h3>{F["prop_last"]:.2f} kg</h3><p class="small">left on {dt(F["degr_span"][1])}</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:260px;padding:34px 22px"><div class="icon">🧰</div><h3>− {F["prop_reserve"]:.0f} kg</h3><p class="small">de-orbit reserve</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:260px;padding:34px 22px"><div class="icon">➗</div><h3>÷ {F["prop_kg_per_year"]:.2f} kg/yr</h3><p class="small">burned each year</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:260px;padding:34px 22px;border-color:#F5B83D"><div class="icon">📅</div><h3 class="hl">{F["prop_years_left"]:.1f} years</h3><p class="small">≈ {dt(F["prop_gauge_date"], "%b %Y")}</p></div>
</div>
<p class="sub anim" style="--d:1.9s;margin-top:40px;text-align:center">{D["prop_above_reserve"]:.1f} kg ÷ {F["prop_kg_per_year"]:.2f} = {F["prop_years_left"]:.1f} years. The line said {dt(cp["unbounded_date"], "%b %Y")}. <b class="hl">Two methods, one story.</b></p>""",
          f"Arithmetic you can do on a phone: {F['prop_last']:.2f} kg left minus the {F['prop_reserve']:.0f} kg reserve = {D['prop_above_reserve']:.1f} kg usable. The five-year average burn is {F['prop_kg_per_year']:.2f} kg a year. "
          f"{D['prop_above_reserve']:.1f} ÷ {F['prop_kg_per_year']:.2f} = {F['prop_years_left']:.1f} years after the end of the data, about {dt(F['prop_gauge_date'], '%B %Y')}. "
          "When a simple sum and the model agree, you can trust both a little more. When they disagree, one of them has a bug."),

        # 15 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">Was the battery call right? 🔍</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">We have the next two years. Let's check.</p>""",
          "Section break. The battery is the only call we can check, because it crosses inside the data.", cls="center"),

        # 16 ─ when did it cross
        S(f"""
<div class="kicker anim">Battery capacity, every day of spring and summer 2025</div>
<h2 class="anim" style="--d:.1s;font-size:54px">When did it “cross” 80%? Pick one…</h2>
<div class="card anim" style="--d:.2s;padding:18px 22px">{cross_svg(D, F)}</div>
<p class="small anim" style="--d:1s;margin-top:8px;text-align:center">🔵 a day at or above 80% · 🔴 a day below · teal line = 30-day mean · gold = the crossing window</p>
<p class="anim" style="--d:3.8s;margin-top:10px;text-align:center">Between the first dip and the last good day, <b class="hl">{F["battery_daily_below_in_window"]} of {F["battery_window_days"]}</b> days are below 80%. A noisy reading doesn't cross on a day: it crosses over a <b class="hl">window</b>.</p>""",
          f"Three honest definitions. ① The first single day below 80%: {dt(cr['first_dip'])}. ② The first day the 30-day average is below 80%: {dt(cr['30_day_mean'])}. "
          f"③ The last day any reading is still at or above 80%: {dt(cr['last_good_day'])}. The daily noise is about ±0.15 points, so readings bounce either side of the floor for {F['battery_window_days']} days. "
          "Which definition is right depends on the decision. Agree it BEFORE you score the forecast."),

        # 17 ─ scoring the call
        S(f"""
<div class="kicker anim">The 3-year call was {dt(cb["date"])}</div>
<h2 class="anim" style="--d:.1s">Early by how much? It depends ⚖️</h2>
<div class="grid2" style="margin-top:26px">
  <div class="card anim a-left" style="--d:.3s;text-align:center;border-color:#F5B83D"><div class="icon">①</div><h3>vs the first dip ({dt(cr["first_dip"], "%d %b")})</h3>
    <div class="stat hl count" data-to="{D["early_first"]}" data-d=".6" style="font-size:120px">0</div><div class="stat-label">days early · the code book's answer</div></div>
  <div class="card anim a-right" style="--d:.8s;text-align:center;border-color:#16A394"><div class="icon">②</div><h3>vs the 30-day mean ({dt(cr["30_day_mean"], "%d %b")})</h3>
    <div class="stat teal count" data-to="{D["early_30"]}" data-d=".6" style="font-size:120px">0</div><div class="stat-label">days early</div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:30px;text-align:center">Same forecast, two scores. <b class="hl">Define “crossed” before you score</b>, and write it in your report.</p>""",
          f"Quiz 4 question 29 uses the first-dip definition: {D['early_first']} days early. Against the 30-day mean it's {D['early_30']} days early. Neither is cheating, but choosing the definition after seeing the scores would be. "
          "For a battery, early is the safe side: you plan the change before it bites."),

        # 18 ─ backtest the method
        S(f"""
<div class="kicker anim">One good call could be luck · callback to Week 6 Day 1</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Backtest the METHOD: four starting points</h2>
<div class="card anim" style="--d:.2s;padding:22px 24px">{calls_svg(D, F)}</div>
<p class="anim" style="--d:2.4s;margin-top:16px;text-align:center">More data → closer call, but <b class="bad">less warning</b>: {rep["warning_days"].iloc[0]:,} days of warning with 1 year, only {rep["warning_days"].iloc[-1]} with 4.</p>""",
          f"Stand at the end of year 1, 2, 3 and 4, make the call with only what you had, and compare it with what happened. Against the first dip: "
          f"{', '.join(f'{v:+d}' for v in rep['days_vs_first_dip'])} days. Against the 30-day mean: {', '.join(f'{v:+d}' for v in rep['days_vs_30_day_mean'])} days. "
          "The code book says the 4-year call 'goes a few days late': only against the single noisy first dip. Against the 30-day mean every call is early. "
          "Quiz 4 question 30: the trade-off is accuracy versus warning time."),

        # 19 ─ why early
        S(f"""
<div class="kicker anim">Why does the straight line call it early?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The fade is slowing down 🐢</h2>
<div class="card anim" style="--d:.2s;padding:26px 28px">{hbars_svg([(f"{yr}", -v, B["blue_d"] if yr < 2025 else B["teal_d"]) for yr, v in sl.items()], 5.2, unit=" % a year", fmt="−{:.2f}")}</div>
<p class="anim" style="--d:1.7s;margin-top:20px;text-align:center">A line fitted on the early, faster years <b class="hl">overstates</b> the later fade, so it reaches 80% too soon.<br>Early is the <b class="good">safe side</b> for a battery. But you only know which way you err because you backtested.</p>""",
          f"Slope of a line through each calendar year: {', '.join(f'{v:.2f}' for v in sl.values())} % a year. The fade is decelerating, a gentle curve. "
          "A straight line can't bend, so calls from early data land early. The pepper task in the notebook tries a curve (degree 2) instead."),

        # 20 ─ eclipse
        S(f"""
<div class="kicker anim">Look closer at the battery</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The battery ages when it works 🌘</h2>
<div class="card anim" style="--d:.2s;padding:26px 28px">{hbars_svg([("🗓️ eclipse days: share of the calendar", F["eclipse_share_days"] * 100, B["blue_d"]), ("🔋 eclipse days: share of all the fade", F["eclipse_share_fade"] * 100, GOLD)], 100, unit="%", L=560)}</div>
<p class="anim" style="--d:1.2s;margin-top:22px;text-align:center">In eclipse season ({F["eclipse_seasons"][0]} – {F["eclipse_seasons"][1]}, {F["eclipse_seasons"][2]} – {F["eclipse_seasons"][3]}) the battery carries the satellite through the shadow every night,<br>
and loses capacity <b class="hl">{F["eclipse_fade_ratio"]:.1f}× faster</b> per day. Like your inverter battery in a month of heavy NEPA cuts. 🔌</p>""",
          f"Compare each day's change in capacity on eclipse days and on sunlit days. Eclipse days are {F['eclipse_share_days']:.1%} of the calendar but carry {F['eclipse_share_fade']:.1%} of the total fade, "
          f"{F['eclipse_fade_ratio']:.2f} times faster per day. Physically sensible: a battery wears out by being charged and discharged, and that only happens in the shadow. "
          "It also means a forecast made in the middle of an eclipse season sees a steeper slope than one made in summer."),

        # 21 ─ long reach
        S(f"""
<div class="kicker anim">Calls made from 1, 2, 3, 4 and 5 years of data</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The long reach: give a range, not a day 🎯</h2>
<div class="card anim" style="--d:.2s;padding:14px 26px"><h3 style="margin:0">📡 Amplifier → −2 dB</h3>
  {reach_svg(tw, [f"{k}y" for k in range(1, 6)], pd.Timestamp("2033-01-01"), pd.Timestamp("2034-01-15"), color=B["teal_d"])}
  <p class="small">The calls span about <b class="hl">{D["twta_span_months"]:.0f} months</b> of 2033, and even the 5-year call reaches {D["twta_reach_end"]:.1f} years past the data.</p></div>
<div class="card anim" style="--d:.6s;padding:14px 26px;margin-top:14px"><h3 style="margin:0">⛽ Propellant → 5 kg</h3>
  {reach_svg(pr, [f"{k}y" for k in range(1, 6)], pd.Timestamp("2035-09-01"), pd.Timestamp("2036-03-01"), color=GOLD, marks=[(F["prop_gauge_date"], "fuel-gauge sum", GREEN)])}
  <p class="small">Very steady (all within {D["prop_span_days"]} days), because the burns are regular. True only <b class="hl">if the burn plan doesn't change</b>.</p></div>""",
          f"Amplifier calls: {', '.join(dt(t) for t in tw)}. Report it as a planning figure: 'around 2033, give or take a few months, re-estimated every year' (Quiz 4 question 22). "
          f"The 3-year call reaches {D['twta_reach_train']:.1f} years past its data. Propellant calls: {', '.join(dt(t) for t in pr)}, and the fuel-gauge sum says {dt(F['prop_gauge_date'], '%b %Y')}. "
          "Steady calls are not the same as certain: a change of orbit strategy or an extra manoeuvre changes the slope overnight."),

        # 22 ─ golden rules + how to say it
        S(f"""
<div class="kicker anim">Five golden rules for remaining useful life</div>
<h2 class="anim" style="--d:.1s;font-size:54px">How a professional says it 🧑🏾‍🔧</h2>
<div class="grid2" style="gap:22px;margin-top:10px">
  <div class="col" style="gap:12px">
    <div class="row anim a-left" style="--d:.3s;gap:16px;align-items:center"><span class="num">1</span><p>Report a <b class="hl">window</b>, never a single day</p></div>
    <div class="row anim a-left" style="--d:.45s;gap:16px;align-items:center"><span class="num">2</span><p>Say <b class="hl">how far past the data</b> you reach</p></div>
    <div class="row anim a-left" style="--d:.6s;gap:16px;align-items:center"><span class="num">3</span><p>Act <b class="hl">before</b> the crossing</p></div>
    <div class="row anim a-left" style="--d:.75s;gap:16px;align-items:center"><span class="num">4</span><p><b class="hl">Re-estimate</b> regularly</p></div>
    <div class="row anim a-left" style="--d:.9s;gap:16px;align-items:center"><span class="num">5</span><p>“No crossing” is an <b class="hl">answer</b>, not day 0</p></div>
  </div>
  <div class="card anim a-right glow" style="--d:1.1s;padding:24px 28px">
    <p style="font-size:23px">🔋 <b>Battery:</b> first dips below 80% in mid-May 2025, below for good by late July. Act before May.</p>
    <p style="font-size:23px;margin-top:12px">📡 <b>Amplifier:</b> around 2033 (calls span Mar–Nov), 7+ years past our data. Re-check every year.</p>
    <p style="font-size:23px;margin-top:12px">⛽ <b>Propellant:</b> late 2035 to early 2036 if the burn plan holds.</p>
  </div>
</div>""",
          "Rule 3 is Quiz 4 question 24 (True). Lead time matters because the action (changing eclipse-season loads, planning a replacement, reserving fuel for de-orbit) takes months to organise. "
          "The three sentences on the right are the model answer for the notebook's C3 task and a template for the final-project report."),

        # 23 ─ quiz
        S("""
<div class="kicker anim">Quiz 4 · forecasting and remaining life</div>
<h2 class="anim" style="--d:.1s">30 questions. 20 minutes. Just you. 📝</h2>
<div class="grid4" style="margin-top:30px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="icon">📵</div><h3>Phones down</h3><p class="small">notebooks closed, no AI</p></div>
  <div class="card anim a-pop" style="--d:.5s;text-align:center"><div class="icon">✏️</div><h3>One letter</h3><p class="small">circle A, B, C or D (or True/False)</p></div>
  <div class="card anim a-pop" style="--d:.7s;text-align:center"><div class="icon">🔀</div><h3>No “always B”</h3><p class="small">answers are spread across A–D</p></div>
  <div class="card anim a-pop" style="--d:.9s;text-align:center"><div class="icon">✅</div><h3>Mark together</h3><p class="small">swap papers and tick</p></div>
</div>
<p class="anim" style="--d:1.2s;margin-top:34px;text-align:center">Covers baselines (W5D2) · regression + ranges (W5D3) · backtesting (W6D1) · remaining life (today).</p>""",
          "Hand out 2-exercise/quiz/W6D2-quiz-4.pdf, or import the Google Forms CSV. Answer key: 4-instructor-only/W6D2-quiz-4-answer-key.pdf. "
          "All 30 answers match the data. Q29 says it scores against the first dip (13 days early): mention the window."),

        # 24 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 45 minutes</div>
  <h2 class="anim" style="--d:.1s;font-size:56px">Call it, check it 🔍</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open <b class="hl">W6D2-exercise</b>, save a copy, run STEP 0</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">A</span><p>Draw the line, find the bug, do the fuel sum</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">B</span><p>Check the battery call from 4 starting points</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">C</span><p>Eclipse ageing, the long reach, the honest report</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.3s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">⛽</div>
  <h3 style="margin-top:16px">13 checks to pass</h3>
  <p class="muted">🌶️ Pepper task: bend the line (a curve, degree 2). Where does it land?</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Common snags: typing 80 where the cell asks for a column name, and running Part B before Part A (it needs the calls table)."),

        # 25 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:16px;margin-top:6px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">📏</span><p><b>Remaining useful life</b> = extend the trend until it crosses the known limit. Check “no crossing” honestly.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">🔍</span><p><b>Backtest the method</b> from several starting points, with “crossed” defined first.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">🎯</span><p><b>Report a window</b>, say how far you reach, act before the crossing, re-estimate.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:22px;font-size:30px">Next 👉 <b class="hl">Project clinic & demo day</b>: five minutes to show your unit what you built. 🎤<br>
<span class="small">Bring your working tool, your report and your honest test table.</span></p>""",
          "Recap. Remind everyone that next session is demo day: five minutes each. Anyone doing brief B (battery or solar-array degradation) should copy today's notebook structure."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    F = facts()
    D = day_facts()
    c = F["rul_calls"]
    cb, ca, cp = c["battery_capacity_pct"], c["twta_gain_db"], c["propellant_kg"]
    cr = F["battery_cross"]
    rep = F["battery_repeat"]
    burns = F["burns"]
    sl = F["battery_slope_by_year"]
    tw, pr = F["twta_gain_db_repeat"], F["propellant_kg_repeat"]
    slope_b = D["fit_battery_capacity_pct"][1][0] * 365
    bat = D["bat"]
    weekly = bat.iloc[::7]
    model = D["fit_battery_capacity_pct"][0]
    x_week = np.arange(0, len(bat), 7)
    fit_vals = [round(float(v), 2) for v in model(x_week)]
    data_vals = [round(float(v), 2) for v in weekly.values]
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "⛽", "kicker": "Week 6 · Day 2", "title": "When Will It Break?\nRemaining Useful Life + Quiz 4",
             "sub": "Draw the trend, find the limit, and say when, honestly",
             "notes": "Last teaching day: how long until a part reaches its limit? Then Quiz 4."},
            {"type": "flow", "title": "Today's mission", "steps": [
                ["📉", "Three shapes", "how parts grow old"], ["📏", "Draw the line", "trend to threshold"],
                ["🔍", "Check the call", "was the battery right?"], ["📝", "Quiz 4", "forecasting + remaining life"]],
             "footer": "10 min hook · 30 min slides · 45 min hands-on · 20 min quiz · 15 min mark + wrap", "notes": "Four moves."},
            {"type": "compare", "title": "“Driver, fuel go reach Ojota?”",
             "left": ["🧑🏾‍✈️", "The danfo driver's sum", "20 litres left ÷ 4 litres a trip = 5 trips (a story, not data)"],
             "right": ["⛽", "That is remaining useful life", "What's left above the limit ÷ how fast it's going. Fill up before the light comes on"],
             "notes": "RUL in one sum. Act before the crossing: Quiz 4 Q24."},
            {"type": "cards", "title": "Remaining useful life is a national question", "cards": [
                ["🚀", "December 2011", "NigComSat-1R launched to 42.5° East"], ["⏳", "15-year design life", "2011 + 15 ≈ 2026"],
                ["🛰️", "2028 · 2029", "targets for NIGCOMSAT-2A and 2B"]],
             "notes": "Facts from the toolkit fact sheet. Today's data is a synthetic teaching platform, not NigComSat-1R telemetry."},
            {"type": "section", "kicker": "Part 1", "title": "Three ways to grow old", "sub": "One satellite, three parts, three limits", "notes": "Section break."},
            {"type": "cards", "title": "Same satellite, three shapes", "cards": [
                ["🔋", "Battery capacity", f"curves down, floor 80%: last reading {D['bat_last']:.2f}%"],
                ["📡", "Amplifier gain", f"straight, slow fade, floor −2 dB: last reading {D['gain_last']:.3f} dB"],
                ["⛽", "Propellant", f"steps at every burn, reserve 5 kg: last reading {F['prop_last']:.2f} kg"]],
             "notes": f"{F['degr_span'][2]:,} days, {dt(F['degr_span'][0])} – {dt(F['degr_span'][1])}. Limits are known up front, from degradation_thresholds.csv."},
            {"type": "stats", "title": "Propellant: a staircase, not a slope", "sub": "Station-keeping burns, counted in the five years of data",
             "stats": [[f"~{burns['days_between']:.0f} days", "between burns"], [f"{burns['kg_each']:.2f} kg", "per burn (typical)"],
                       [f"~{burns['per_year']:.0f}", "burns a year"], [f"{F['prop_kg_per_year']:.2f} kg", "used a year"]],
             "notes": "Quiz 4 Q23. A straight line through a staircase is an approximation."},
            {"type": "section", "kicker": "Part 2", "title": "Draw the line", "sub": "Fit the trend on the past, extend it to the limit", "notes": "Section break."},
            {"type": "chart", "title": f"Trend-to-threshold: 3 years of battery data, line extended to 80%",
             "labels": [f"{t:%b %Y}" for t in weekly.index],
             "series": [{"name": "battery capacity (all 5 years)", "values": data_vals, "color": "3B8BE0"},
                        {"name": "line fitted on the first 3 years, extended", "values": fit_vals, "color": "C98205"}],
             "ymin": 76, "ymax": 101, "fmt": "0",
             "caption": f"Slope {slope_b:.2f}% a year. The line hits 80% on {dt(cb['date'])}: {(cb['date'] - D['call_day']).days} days after the call on {dt(D['call_day'])}.",
             "notes": "Only the first three years are used, as if it were 1 Jan 2024."},
            {"type": "code", "title": "The whole method: fit_trend + day_of_threshold",
             "code": "x = np.arange(len(series))\nslope, intercept = np.polyfit(x, series.values, 1)\n\nline = np.poly1d([slope, intercept])\nfuture = line(np.arange(len(series) + 4000))\ncrossed = future < threshold\nday = np.argmax(crossed)        # the FIRST True",
             "caption": "np.polyfit(x, y, 1) → slope and intercept. np.argmax of True/False → position of the first True.",
             "notes": "Quiz 4 Q20."},
            {"type": "stats", "title": "The code book's calls, 3 years of data each", "sub": "Two sensible dates and one strange one",
             "stats": [[dt(cb["date"]), "battery → 80%"], [dt(ca["date"]), "amplifier → −2 dB"], [dt(cp["original_print"]), "propellant → 5 kg ?!"]],
             "notes": f"{dt(cp['original_print'])} is the first day of the data."},
            {"type": "code", "title": "The bug: np.argmax of “never” is 0",
             "code": "crossed = [False, False, False, False]\nnp.argmax(crossed)      # 0 !!!\n\n# FIXED in day_of_threshold:\nif not crossed.any():\n    return None         # \"no crossing\"",
             "caption": f"The line never reaches 5 kg before the search stops on {dt(cp['search_end'])}. Say “no crossing before {dt(cp['search_end'])}”, then look further.",
             "notes": "A confident wrong date with no error. Check the 'nothing found' case."},
            {"type": "statement", "title": "Propellant: the line gets there, just later", "icon": "🔭",
             "big": f"day = (5 − intercept) / slope → {dt(cp['unbounded_date'])}",
             "sub": f"The 3-year line falls {abs(cp['slope_per_year']):.2f} kg a year and reaches the reserve about {D['prop_reach_train']:.0f} years past the data it was fitted on.",
             "notes": "A straight line can be solved for the crossing directly."},
            {"type": "flow", "title": "The fuel-gauge sum agrees", "steps": [
                ["🛢️", f"{F['prop_last']:.2f} kg", f"left on {dt(F['degr_span'][1])}"], ["🧰", f"− {F['prop_reserve']:.0f} kg", "de-orbit reserve"],
                ["➗", f"÷ {F['prop_kg_per_year']:.2f} kg/yr", "burned each year"], ["📅", f"{F['prop_years_left']:.1f} years", f"≈ {dt(F['prop_gauge_date'], '%b %Y')}"]],
             "footer": f"The line said {dt(cp['unbounded_date'], '%b %Y')}. Two methods, one story.", "notes": "Simple sums are the best bug detectors."},
            {"type": "section", "kicker": "Part 3", "title": "Was the battery call right?", "sub": "We have the next two years. Let's check", "notes": "Section break."},
            {"type": "stats", "title": "When did the battery “cross” 80%? Three honest answers", "sub": "Daily readings bounce around the floor",
             "stats": [[dt(cr["first_dip"], "%d %b"), "① first day below 80%"], [dt(cr["30_day_mean"], "%d %b"), "② 30-day mean below 80%"],
                       [dt(cr["last_good_day"], "%d %b"), "③ last day at or above 80%"]],
             "notes": f"{F['battery_daily_below_in_window']} of the {F['battery_window_days']} days in between are below 80%. A crossing is a window."},
            {"type": "compare", "title": f"The 3-year call ({dt(cb['date'])}): early by how much?",
             "left": ["①", f"{D['early_first']} days early", f"vs the first dip ({dt(cr['first_dip'], '%d %b')}): the code book's answer"],
             "right": ["②", f"{D['early_30']} days early", f"vs the 30-day mean ({dt(cr['30_day_mean'], '%d %b')})"],
             "notes": "Define 'crossed' before you score. Quiz 4 Q29 uses the first dip."},
            {"type": "table", "title": "Backtest the method: the battery call from four starting points",
             "header": ["Data used", "Call made on", "Predicted crossing", "vs first dip", "vs 30-day mean", "Warning"],
             "rows": [[f"{r['years_of_data']} year{'s' if r['years_of_data'] > 1 else ''}", dt(r["call_made_on"]), dt(r["predicted_crossing"]),
                       f"{r['days_vs_first_dip']:+d} d", f"{r['days_vs_30_day_mean']:+d} d", f"{r['warning_days']:,} d"] for _, r in rep.iterrows()],
             "colW": [1.6, 2.2, 2.3, 1.9, 2.2, 1.93],
             "caption": "More data → closer call, but less warning. Against the 30-day mean, every call is early.", "notes": "Quiz 4 Q30."},
            {"type": "bar", "title": "Why early? The fade is slowing down (% a year)",
             "labels": [str(y) for y in sl], "values": [round(-v, 2) for v in sl.values()], "fmt": "0.00", "ymin": 0,
             "caption": "A line fitted on the early, faster years overstates the later fade. Early is the safe side for a battery.",
             "notes": "Capacity lost per year, from a line through each calendar year."},
            {"type": "stats", "title": "The battery ages when it works", "sub": f"Eclipse seasons: {F['eclipse_seasons'][0]} – {F['eclipse_seasons'][1]} and {F['eclipse_seasons'][2]} – {F['eclipse_seasons'][3]}",
             "stats": [[f"{F['eclipse_share_days']:.1%}", "of the days are eclipse days"], [f"{F['eclipse_share_fade']:.1%}", "of all the fade happens on them"],
                       [f"{F['eclipse_fade_ratio']:.1f}×", "faster per day than in sunlight"]],
             "notes": "Batteries wear out by charging and discharging, which only happens in the shadow."},
            {"type": "table", "title": "The long reach: calls from 1 to 5 years of data",
             "header": ["Data used", "Amplifier → −2 dB", "Propellant → 5 kg"],
             "rows": [[f"{k} year{'s' if k > 1 else ''}", dt(a), dt(p)] for k, (a, p) in enumerate(zip(tw, pr), start=1)],
             "colW": [3.0, 4.66, 4.67],
             "caption": f"Amplifier: around 2033, calls span ~{D['twta_span_months']:.0f} months. Propellant: within {D['prop_span_days']} days, if the burn plan holds; fuel-gauge sum {dt(F['prop_gauge_date'], '%b %Y')}.",
             "notes": "Quiz 4 Q22: a planning figure with a range, re-estimated every year."},
            {"type": "steps", "title": "Golden rules for remaining useful life", "icon": "🧑🏾‍🔧", "steps": [
                "Report a window, never a single day", "Say how far past the data you reach",
                "Act before the crossing, and re-estimate regularly", "“No crossing” is an answer, not day 0"],
             "notes": "Battery: dips below 80% mid-May 2025, below for good by late July. Amplifier: around 2033, re-check yearly. Propellant: late 2035 to early 2036 if the burn plan holds."},
            {"type": "steps", "title": "Quiz 4: 30 questions, 20 minutes", "icon": "📝", "steps": [
                "Phones down, notebooks closed, no AI", "Circle one letter per question", "Answers are spread across A–D: no “always B”",
                "Swap papers and mark together"], "notes": "Use the PDF or the Google Forms CSV."},
            {"type": "steps", "title": "Your turn: 45 minutes", "icon": "⛽", "steps": [
                "Open W6D2-exercise, save a copy, run STEP 0", "Part A: draw the line, find the bug, do the fuel sum",
                "Part B: check the battery call from 4 starting points", "Part C: eclipse ageing, the long reach, the honest report"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["📏", "RUL = extend the trend until it crosses the known limit; check “no crossing” honestly"],
                ["🔍", "Backtest the method from several starting points, with “crossed” defined first"],
                ["🎯", "Report a window, say how far you reach, act before the crossing, re-estimate"]],
             "next": "Next: Project clinic & demo day · bring your tool, report and honest test table", "notes": "Recap."},
        ],
    }


# =============================================================================
# NOTEBOOK CHECKS (expected values filled in from the data at build time)
# =============================================================================
def _checks():
    F = facts()
    D = day_facts()
    c = F["rul_calls"]
    cr = F["battery_cross"]
    rep = F["battery_repeat"]
    calls = {c[col]["asset"]: (None if c[col]["date"] is None else str(c[col]["date"].date())) for col in COLS}
    vals = {
        "SLOPE": repr(float(D["fit_battery_capacity_pct"][1][0] * 365)),
        "CALLS": repr(calls),
        "BATT_CALL": dt(c["battery_capacity_pct"]["date"]), "AMP_CALL": dt(c["twta_gain_db"]["date"]),
        "SEARCH_END": dt(c["propellant_kg"]["search_end"]), "ORIG": dt(c["propellant_kg"]["original_print"]),
        "PROP_LINE": repr(str(c["propellant_kg"]["unbounded_date"].date())), "PROP_LINE_TXT": dt(c["propellant_kg"]["unbounded_date"]),
        "YEARS_LEFT": repr(float(F["prop_years_left"])), "GAUGE": dt(F["prop_gauge_date"], "%B %Y"),
        "CROSS": repr(tuple(str(cr[k].date()) for k in ("first_dip", "30_day_mean", "last_good_day"))),
        "FIRST": dt(cr["first_dip"]), "MEAN30": dt(cr["30_day_mean"]), "LAST": dt(cr["last_good_day"]),
        "EARLY": repr((D["early_first"], D["early_30"])), "E1": str(D["early_first"]), "E30": str(D["early_30"]),
        "REP_ERR": repr([int(v) for v in rep["days_vs_first_dip"]]), "REP_WARN": repr([int(v) for v in rep["warning_days"]]),
        "WARN1": f"{int(rep['warning_days'].iloc[0]):,}", "WARN4": str(int(rep["warning_days"].iloc[-1])),
        "SHARE": repr(float(F["eclipse_share_fade"])), "SHARE_TXT": f"{F['eclipse_share_fade']:.1%}",
        "DAYS_TXT": f"{F['eclipse_share_days']:.1%}", "RATIO": f"{F['eclipse_fade_ratio']:.1f}",
        "REACH": repr(float(D["twta_reach_end"])), "REACH_TXT": f"{D['twta_reach_end']:.1f}",
        "QUAD": repr(str(D["quad_call"].date())), "QUAD_TXT": dt(D["quad_call"]),
    }
    code = r'''
def _near(x, want, tol):
    return abs(float(x) - want) <= tol

def _day(x):
    return None if x is None or pd.isna(x) else str(pd.Timestamp(x).date())

def _c_a1(x):
    return _near(x, @@SLOPE@@, 0.01), \
        f"{float(x):.2f}% a year: the battery loses about four and a half points of capacity every year. 📉", \
        "A slope per day times the number of days in a year: 365."

def _c_a2(x):
    got = {r["asset"]: _day(r["predicted_date"]) for _, r in x.iterrows()}
    return got == @@CALLS@@, \
        "Battery @@BATT_CALL@@, amplifier @@AMP_CALL@@, and the propellant says None: no crossing inside the search window. Next task: what did the original say? 🤔", \
        "The limit value lives in the column called \"threshold\". Type it as text, with quotes."

def _c_a3(x):
    return bool(x[0]) is False and int(x[1]) == 0, \
        "Never crossed, so every value is False, and np.argmax of all-False is 0: day 0 = @@ORIG@@. A confident wrong date with no error. 🐞", \
        "Look at the print: how many days in the window are below 5 kg? If none, did it cross?"

def _c_a4(x):
    return _day(x) == @@PROP_LINE@@, \
        "@@PROP_LINE_TXT@@: the line does reach 5 kg, just after the 4,000-day search stopped (@@SEARCH_END@@). 🔭", \
        "Solve the straight line for the threshold: (5.0 - intercept) / slope"

def _c_a5(x):
    return _near(x, @@YEARS_LEFT@@, 0.01), \
        f"{float(x):.1f} years, about @@GAUGE@@. The danfo-driver sum agrees with the line (@@PROP_LINE_TXT@@). ⛽", \
        "The reserve in degradation_thresholds.csv is 5 kg: RESERVE_KG = 5.0"

def _c_b1(x):
    got = tuple(_day(x[k]) for k in ("first_dip", "30_day_mean", "last_good_day"))
    return got == @@CROSS@@, \
        "First dip @@FIRST@@, 30-day mean @@MEAN30@@, last good day @@LAST@@: the crossing is a window, not a day. 🪟", \
        "The battery's floor, in %: FLOOR = 80.0"

def _c_b2(x):
    return tuple(int(v) for v in x) == @@EARLY@@, \
        "@@E1@@ days early against the first dip (the code book's answer), @@E30@@ against the 30-day mean. Same forecast, two scores: define 'crossed' first. ⚖️", \
        "Use the key exactly as printed in cross: \"30_day_mean\""

def _c_b3(x):
    return [int(v) for v in x["days_vs_first_dip"]] == @@REP_ERR@@ and [int(v) for v in x["warning_days"]] == @@REP_WARN@@, \
        "More data, closer call, less warning: from @@WARN1@@ days of warning down to @@WARN4@@. That trade-off is the whole game. ⏳", \
        "A list of the four amounts of data: YEARS = [1, 2, 3, 4]"

def _c_b4(x):
    return "slow" in str(x).lower(), \
        "It slows. A line fitted on the early, faster years overstates the later fade, so the calls land early: the safe side. 🐢", \
        "Read the slopes: is the yearly loss getting bigger or smaller? Type \"slows\" or \"speeds up\"."

def _c_c1(x):
    v = float(x)
    v = v / 100 if v > 1 else v
    return _near(v, @@SHARE@@, 0.002), \
        "@@SHARE_TXT@@ of the fade happens on eclipse days, which are only @@DAYS_TXT@@ of the calendar: @@RATIO@@x faster. The battery ages when it works. 🌘", \
        "Eclipse days have eclipse_flag equal to 1: ECLIPSE = 1"

def _c_c2(x):
    return _near(x, @@REACH@@, 0.02), \
        "@@REACH_TXT@@ years past the end of the data, and that's the BEST call (5 years of data). Give a range and re-estimate every year. 🎯", \
        "The last day of data is degr.index[-1]: LAST = -1"

def _c_c3(x):
    return str(x).strip().upper() == "B", \
        "B: a planning figure with a range, how far it reaches, and when you'll check again. That is how a professional reports it. 🧑🏾‍🔧", \
        "A gives one exact day; C refuses to say anything. Which one helps the planner AND tells the truth?"

def _c_bonus(x):
    return _day(x) == @@QUAD@@, \
        "@@QUAD_TXT@@: a curve that bends with the slowing fade lands INSIDE the real window. Careful though: curves can go wild over long reaches like the amplifier's. 🌶️", \
        "A curve with one bend is degree 2: DEGREE = 2"

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "A5": _c_a5, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3,
          "B4": _c_b4, "C1": _c_c1, "C2": _c_c2, "C3": _c_c3, "BONUS": _c_bonus}
HINTS = {"A2": "COLUMN is the NAME of a column of limits, as text.", "B3": "YEARS is a list of numbers, like [1, 2, 3, 4]."}
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

    a2 = '''COLUMN = {v}

assert COLUMN is not None, "✍️ Fill in COLUMN first."
assert isinstance(COLUMN, str), "✍️ COLUMN is the NAME of a column, as text in quotes."
rows = []
for _, row in limits.iterrows():
    day, _ = day_of_threshold(known[row["channel"]], row[COLUMN], row["direction"])
    rows.append({{"asset": row["asset"], "channel": row["channel"], "limit": row[COLUMN],
                 "predicted_day": day,
                 "predicted_date": None if day is None else (degr.index[0] + pd.Timedelta(days=day)).date()}})
calls = pd.DataFrame(rows)
display(calls)
check("A2", calls)'''

    b3 = '''YEARS = {v}

assert YEARS is not None, "✍️ Fill in YEARS first."
assert "cross" in globals(), "✍️ Finish B1 first, then run this cell."
first_dip, mean30 = cross["first_dip"], cross["30_day_mean"]
rows = []
for years in YEARS:
    n_days = 365 * years
    day, _ = day_of_threshold(bat.iloc[:n_days], 80.0)
    call = degr.index[0] + pd.Timedelta(days=day)
    rows.append({{"years_of_data": years, "call_made_on": degr.index[n_days].date(), "predicted_crossing": call.date(),
                 "days_vs_first_dip": (call - first_dip).days, "days_vs_30_day_mean": (call - mean30).days,
                 "warning_days": (first_dip - degr.index[n_days]).days}})
repeat = pd.DataFrame(rows)
display(repeat)
check("B3", repeat)'''

    c2 = '''LAST = {v}

assert LAST is not None, "✍️ Fill in LAST first."
gain = degr["twta_gain_db"]
amp_calls = []
for years in [1, 2, 3, 4, 5]:
    model, (slope, intercept) = fit_trend(gain.iloc[:365 * years])
    amp_calls.append(degr.index[0] + pd.Timedelta(days=int((-2.0 - intercept) / slope)))
for years, t in zip([1, 2, 3, 4, 5], amp_calls):
    print(f"{{years}} year(s) of data → gain reaches -2 dB on {{t.date()}}")

reach_years = (amp_calls[-1] - degr.index[LAST]).days / 365.25
print(f"\\nthe 5-year call reaches {{reach_years:.1f}} years past the last day of data")
check("C2", reach_years)'''

    return [
        ("md", """# ⛽ Week 6 · Day 2: When Will It Break? Remaining Useful Life

**Today:** you make the code book's remaining-useful-life calls, find (and fix) the bug that sends the propellant back to day 0, then check the battery call against what really happened, from four different starting points.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**

**Rule book:** keep `W6D2-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up
Run it once every time you open the notebook (and after every restart). Wait for `✅ Ready!`."""),
        ("setup", setup_code),
        ("md", """### ▶️ The data and the limits
Five years of daily readings from one **synthetic** GEO satellite (the same made-up platform as Week 5), and a small table of operational limits. The limits are **known up front**: we forecast *when* they are reached, not what they are."""),
        ("code", 'degr = pd.read_csv(data_path("degradation_assets_daily"), parse_dates=["date"], index_col="date").asfreq("D")\n'
                 'limits = pd.read_csv(data_path("degradation_thresholds"))\n'
                 'print("days:", len(degr), "·", degr.index[0].date(), "to", degr.index[-1].date(), "· gaps:", int(degr.isna().sum().sum()))\n'
                 'display(limits[["asset", "channel", "unit", "threshold", "direction"]])'),
        ("code", '''fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
for ax, (_, row) in zip(axes, limits.iterrows()):
    ax.plot(degr.index, degr[row["channel"]], lw=0.8)
    ax.axhline(row["threshold"], color="#C0504D", ls="--", label=f"limit: {row['threshold']} {row['unit']}")
    ax.set_title(f"{row['asset']}: {row['channel']}")
    ax.legend(loc="upper right")
plt.tight_layout()
plt.show()'''),
        ("md", """### ▶️ Your tools for today
Three small functions (read them once, then run):
- `fit_trend(series)` fits the best straight line through day number vs value. It returns the line and its two numbers, **slope** and **intercept**.
- `day_of_threshold(series, threshold)` extends that line forward until it crosses the limit, and returns the **day number**. If it never crosses inside the search window, it returns **`None`** (the original code book had a bug here: you'll find it in A3).
- `crossing_dates(series, threshold)` answers *"when did it actually cross?"* three ways (Part B)."""),
        ("code", RUL_CODE + '\n\nprint("✅ fit_trend(), day_of_threshold() and crossing_dates() are ready")'),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Draw the line (15 min) 📏

📖 The honest rule from the code book: make the call using **only the first three years**, as if it were the morning of 1 January 2024. The two later years are kept aside to check the call in Part B.

### A1 ✍️ How fast is the battery fading?
`fit_trend` gives the slope **per day**. Turn it into a slope **per year**: how many days are in a year?"""),
        _task('TRAIN_DAYS = 365 * 3\nknown = degr.iloc[:TRAIN_DAYS]\nmodel, (slope_per_day, intercept) = fit_trend(known["battery_capacity_pct"])\n'
              'print(f"slope: {slope_per_day:.5f} % per day · intercept: {intercept:.2f} %")\n\n'
              'DAYS_PER_YEAR = ___\n\nassert DAYS_PER_YEAR is not None, "✍️ Fill in DAYS_PER_YEAR first."\n'
              'slope_per_year = slope_per_day * DAYS_PER_YEAR\nprint(f"slope: {slope_per_year:.2f} % per year")\ncheck("A1", slope_per_year)',
              'TRAIN_DAYS = 365 * 3\nknown = degr.iloc[:TRAIN_DAYS]\nmodel, (slope_per_day, intercept) = fit_trend(known["battery_capacity_pct"])\n'
              'print(f"slope: {slope_per_day:.5f} % per day · intercept: {intercept:.2f} %")\n\n'
              'DAYS_PER_YEAR = 365\n\nassert DAYS_PER_YEAR is not None, "✍️ Fill in DAYS_PER_YEAR first."\n'
              'slope_per_year = slope_per_day * DAYS_PER_YEAR\nprint(f"slope: {slope_per_year:.2f} % per year")\ncheck("A1", slope_per_year)'),
        ("md", """### A2 ✍️ The three calls
The loop makes the call for every row of `limits`. `day_of_threshold` needs each part's limit value: which **column** of `limits` holds it? Type the column name as text, like `"unit"`."""),
        _task(a2.format(v="___"), a2.format(v='"threshold"')),
        ("md", f"""### A3 ✍️ What did the original code book print for the propellant?
The original searched **4,000 days** past the data and took `np.argmax` of "is the line below the limit?". It printed **{dt(F["rul_calls"]["propellant_kg"]["original_print"])}** for the propellant: the first day of the data. ▶️ Run the cell and read the two prints.
Then ✍️: did the line cross 5 kg inside the search window, `True` or `False`?"""),
        _task('model_p, coef_p = fit_trend(known["propellant_kg"])\ny_future = model_p(np.arange(len(known) + 4000))   # the 4,000-day search\n'
              'crossed = y_future < 5.0\nprint("days in the search window below 5 kg:", int(crossed.sum()))\n'
              'original_day = np.argmax(crossed)\nprint("np.argmax says day", original_day, "→", (degr.index[0] + pd.Timedelta(days=int(original_day))).date())\n\n'
              'crossed_in_window = ___\n\ncheck("A3", (crossed_in_window, original_day))',
              'model_p, coef_p = fit_trend(known["propellant_kg"])\ny_future = model_p(np.arange(len(known) + 4000))   # the 4,000-day search\n'
              'crossed = y_future < 5.0\nprint("days in the search window below 5 kg:", int(crossed.sum()))\n'
              'original_day = np.argmax(crossed)\nprint("np.argmax says day", original_day, "→", (degr.index[0] + pd.Timedelta(days=int(original_day))).date())\n\n'
              'crossed_in_window = False\n\ncheck("A3", (crossed_in_window, original_day))'),
        ("md", """> 📖 **The bug:** `np.argmax` returns the position of the *first* `True`. When there is no `True` at all, every value ties and it returns **0**. No error, no warning: a confident wrong date. Our `day_of_threshold` checks `crossed.any()` first and returns `None`, so the honest answer is *"no crossing inside the search window"*.

### A4 ✍️ Look further: solve the line
A straight line is `value = slope × day + intercept`. Set the value to the 5 kg reserve and solve for the day: `(5.0 - intercept) / slope`."""),
        _task('slope, intercept = coef_p\nprint(f"propellant line: {slope * 365:.2f} kg per year")\n\n'
              'crossing_day = ___\n\nassert crossing_day is not None, "✍️ Fill in crossing_day first."\n'
              'prop_line_date = degr.index[0] + pd.Timedelta(days=int(crossing_day))\n'
              'print("the line reaches 5 kg on", prop_line_date.date())\ncheck("A4", prop_line_date)',
              'slope, intercept = coef_p\nprint(f"propellant line: {slope * 365:.2f} kg per year")\n\n'
              'crossing_day = (5.0 - intercept) / slope\n\nassert crossing_day is not None, "✍️ Fill in crossing_day first."\n'
              'prop_line_date = degr.index[0] + pd.Timedelta(days=int(crossing_day))\n'
              'print("the line reaches 5 kg on", prop_line_date.date())\ncheck("A4", prop_line_date)'),
        ("md", """### A5 ✍️ The danfo driver's fuel-gauge sum
No model at all: what's left **above the reserve**, divided by what is burned in a year. How many kg must stay in the tank for the de-orbit burn?"""),
        _task('prop = degr["propellant_kg"]\nkg_per_year = (prop.iloc[0] - prop.iloc[-1]) / (len(prop) - 1) * 365\n'
              'print(f"left on {prop.index[-1].date()}: {prop.iloc[-1]:.2f} kg · burned: {kg_per_year:.2f} kg per year")\n\n'
              'RESERVE_KG = ___\n\nassert RESERVE_KG is not None, "✍️ Fill in RESERVE_KG first."\n'
              'years_left = (prop.iloc[-1] - RESERVE_KG) / kg_per_year\nempty_date = prop.index[-1] + pd.Timedelta(days=years_left * 365.25)\n'
              'print(f"years left: {years_left:.1f} → about {empty_date:%B %Y}")\ncheck("A5", years_left)',
              'prop = degr["propellant_kg"]\nkg_per_year = (prop.iloc[0] - prop.iloc[-1]) / (len(prop) - 1) * 365\n'
              'print(f"left on {prop.index[-1].date()}: {prop.iloc[-1]:.2f} kg · burned: {kg_per_year:.2f} kg per year")\n\n'
              'RESERVE_KG = 5.0\n\nassert RESERVE_KG is not None, "✍️ Fill in RESERVE_KG first."\n'
              'years_left = (prop.iloc[-1] - RESERVE_KG) / kg_per_year\nempty_date = prop.index[-1] + pd.Timedelta(days=years_left * 365.25)\n'
              'print(f"years left: {years_left:.1f} → about {empty_date:%B %Y}")\ncheck("A5", years_left)'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Was the battery call right? (15 min) 🔍

### B1 ✍️ When did it actually cross?
Daily readings are noisy, so "crossed" has more than one honest meaning. `crossing_dates` gives three: the **first day below**, the first day the **30-day mean** is below, and the **last day still at or above**. What is the battery's floor, in %?"""),
        _task('bat = degr["battery_capacity_pct"]\n\nFLOOR = ___\n\nassert FLOOR is not None, "✍️ Fill in FLOOR first."\n'
              'cross = crossing_dates(bat, FLOOR, window=30)\nfor name, day in cross.items():\n    print(f"{name:14s} {day.date()}")\n'
              'window = bat.loc[cross["first_dip"]:cross["last_good_day"]]\n'
              'print(f"\\nin between: {int((window < FLOOR).sum())} of {len(window)} days are below {FLOOR}%")\ncheck("B1", cross)',
              'bat = degr["battery_capacity_pct"]\n\nFLOOR = 80.0\n\nassert FLOOR is not None, "✍️ Fill in FLOOR first."\n'
              'cross = crossing_dates(bat, FLOOR, window=30)\nfor name, day in cross.items():\n    print(f"{name:14s} {day.date()}")\n'
              'window = bat.loc[cross["first_dip"]:cross["last_good_day"]]\n'
              'print(f"\\nin between: {int((window < FLOOR).sum())} of {len(window)} days are below {FLOOR}%")\ncheck("B1", cross)'),
        ("md", """### B2 ✍️ Score the 3-year call
`CALL` is the battery date from your A2 table. The first score is done for you. ✍️ Score it again against the 30-day mean: type that key of `cross`, exactly as printed above."""),
        _task('assert "calls" in globals(), "✍️ Finish A2 first, then run this cell."\n'
              'CALL = pd.Timestamp(calls.loc[calls["asset"] == "BATT-A", "predicted_date"].iloc[0])\nprint("the 3-year call:", CALL.date())\n\n'
              'KEY = ___\n\nassert KEY is not None, "✍️ Fill in KEY first."\n'
              'early_vs_first_dip = (cross["first_dip"] - CALL).days\nearly_vs_30_day = (cross[KEY] - CALL).days\n'
              'print(f"days early vs the first dip: {early_vs_first_dip} · vs the 30-day mean: {early_vs_30_day}")\ncheck("B2", (early_vs_first_dip, early_vs_30_day))',
              'assert "calls" in globals(), "✍️ Finish A2 first, then run this cell."\n'
              'CALL = pd.Timestamp(calls.loc[calls["asset"] == "BATT-A", "predicted_date"].iloc[0])\nprint("the 3-year call:", CALL.date())\n\n'
              'KEY = "30_day_mean"\n\nassert KEY is not None, "✍️ Fill in KEY first."\n'
              'early_vs_first_dip = (cross["first_dip"] - CALL).days\nearly_vs_30_day = (cross[KEY] - CALL).days\n'
              'print(f"days early vs the first dip: {early_vs_first_dip} · vs the 30-day mean: {early_vs_30_day}")\ncheck("B2", (early_vs_first_dip, early_vs_30_day))'),
        ("md", """### B3 ✍️ Backtest the method: four starting points
One good call could be luck (Week 6 Day 1). Make the call as if you were standing at the end of year 1, 2, 3 and 4, with only the data you had then. ✍️ `YEARS` is the list of those four amounts of data.
Negative = the call came **early**. `warning_days` = how long you had to act before the first dip."""),
        _task(b3.format(v="___"), b3.format(v="[1, 2, 3, 4]")),
        ("md", """### B4 ✍️ Why do the calls land early?
▶️ The cell fits a line through each calendar year separately. ✍️ Is the yearly fade getting bigger or smaller? Type `"slows"` or `"speeds up"`."""),
        _task('slopes = {year: fit_trend(bat[str(year)])[1][0] * 365 for year in range(2021, 2026)}\n'
              'for year, s in slopes.items():\n    print(f"{year}: {s:.2f} % per year")\n\nfade_is = ___\n\ncheck("B4", fade_is)',
              'slopes = {year: fit_trend(bat[str(year)])[1][0] * 365 for year in range(2021, 2026)}\n'
              'for year, s in slopes.items():\n    print(f"{year}: {s:.2f} % per year")\n\nfade_is = "slows"\n\ncheck("B4", fade_is)'),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Look closer, reach further (12 min) 🎯

### C1 ✍️ Does the battery age faster in eclipse season?
In the eclipse seasons the battery carries the satellite through the Earth's shadow every night. `daily` is each day's change in capacity (negative = fade). ✍️ Eclipse days have `eclipse_flag` equal to what number?"""),
        _task('daily = bat.diff().dropna()\n\nECLIPSE = ___\n\nassert ECLIPSE is not None, "✍️ Fill in ECLIPSE first."\n'
              'in_eclipse = degr["eclipse_flag"].loc[daily.index] == ECLIPSE\n'
              'share_of_days = in_eclipse.mean()\nshare_of_fade = daily[in_eclipse].sum() / daily.sum()\n'
              'print(f"eclipse days: {share_of_days:.1%} of the calendar · {share_of_fade:.1%} of all the fade")\n'
              'print(f"fade per day, eclipse vs sunlight: {daily[in_eclipse].mean() / daily[~in_eclipse].mean():.1f}x")\ncheck("C1", share_of_fade)',
              'daily = bat.diff().dropna()\n\nECLIPSE = 1\n\nassert ECLIPSE is not None, "✍️ Fill in ECLIPSE first."\n'
              'in_eclipse = degr["eclipse_flag"].loc[daily.index] == ECLIPSE\n'
              'share_of_days = in_eclipse.mean()\nshare_of_fade = daily[in_eclipse].sum() / daily.sum()\n'
              'print(f"eclipse days: {share_of_days:.1%} of the calendar · {share_of_fade:.1%} of all the fade")\n'
              'print(f"fade per day, eclipse vs sunlight: {daily[in_eclipse].mean() / daily[~in_eclipse].mean():.1f}x")\ncheck("C1", share_of_fade)'),
        ("md", """### C2 ✍️ The long reach: the amplifier
The amplifier is nowhere near −2 dB yet, so its call can't be checked. ▶️ The cell makes the call from 1 to 5 years of data. ✍️ How far past the **last day of data** does even the best (5-year) call reach? The last day is `degr.index[LAST]`: what position is the last item of a list?"""),
        _task(c2.format(v="___"), c2.format(v="-1")),
        ("md", """### C3 ✍️ The honest report
Which sentence would you send to the fleet planner about the amplifier? Type `"A"`, `"B"` or `"C"`.
- **A.** "The amplifier gain will fall below −2 dB on 5 May 2033."
- **B.** "Around 2033 (calls made from 1 to 5 years of data span March to November 2033). That is more than 7 years past our data, so we will re-estimate every year."
- **C.** "We can't say anything until it fails.\""""),
        _task('honest = ___\n\ncheck("C3", honest)', 'honest = "B"\n\ncheck("C3", honest)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: bend the line
The fade is slowing, so a straight line calls early. `day_of_threshold` can fit a **curve** instead: `degree=1` is a straight line, a curve with one bend is the next degree up. ✍️ Same three years of data: where does the curve land?"""),
        _task('DEGREE = ___\n\nassert DEGREE is not None, "✍️ Fill in DEGREE first."\n'
              'day, _ = day_of_threshold(known["battery_capacity_pct"], 80.0, degree=DEGREE)\n'
              'curve_call = degr.index[0] + pd.Timedelta(days=day)\n'
              'print("curve call:", curve_call.date(), "· real window:", cross["first_dip"].date(), "to", cross["last_good_day"].date())\ncheck("BONUS", curve_call)',
              'DEGREE = 2\n\nassert DEGREE is not None, "✍️ Fill in DEGREE first."\n'
              'day, _ = day_of_threshold(known["battery_capacity_pct"], 80.0, degree=DEGREE)\n'
              'curve_call = degr.index[0] + pd.Timedelta(days=day)\n'
              'print("curve call:", curve_call.date(), "· real window:", cross["first_dip"].date(), "to", cross["last_good_day"].date())\ncheck("BONUS", curve_call)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", f"""### 📝 What you learned today
- **Remaining useful life** = fit the trend, extend it until it crosses the known limit. The battery's 3-year line hits 80% on **{dt(F["rul_calls"]["battery_capacity_pct"]["date"])}**.
- **Check the "never" case.** `np.argmax` of all-False is 0, which made the original print {dt(F["rul_calls"]["propellant_kg"]["original_print"])}. Say "no crossing inside the window", then solve the line: **{dt(F["rul_calls"]["propellant_kg"]["unbounded_date"])}**. The fuel-gauge sum agrees ({F["prop_years_left"]:.1f} years).
- **"Crossed" is a window**, from the first dip ({dt(F["battery_cross"]["first_dip"])}) to the last good day ({dt(F["battery_cross"]["last_good_day"])}). Define it before you score.
- **Backtest the method** from several starting points: more data gives a closer call but less warning. The straight line errs early because the fade slows.
- **Report a window**, say how far past the data you reach, act before the crossing, and re-estimate regularly.

**Next time:** *Project clinic & demo day*: five minutes to show your unit what you built. 🎤

<sub>Data: synthetic teaching dataset from the original Week 6 code book (`Time-series/week-06`). Safe to use with AI tools; real NIGCOMSAT data is not.</sub>"""),
    ]


# =============================================================================
# EXTRAS: Quiz 4
# =============================================================================
def extra(d, foot):
    quiz = quizkit.write_quiz(d, foot, n=4, mcq_file="week-06-mcq.csv", seed=QUIZ_SEED, covers="Forecasting and remaining life",
                              topic_map="forecasting baselines → W5D2 · regression-based forecasting → W5D3 · "
                                        "uncertainty and prediction intervals → W5D3 · trend-to-threshold and remaining useful life → W6D2 · "
                                        "backtesting → W6D1 (Q29–30 → W6D2)")
    counts = {L: sum(q["letter"] == L for q in quiz if len(q["options"]) == 4) for L in "ABCD"}
    tf = {L: sum(q["letter"] == L for q in quiz if len(q["options"]) == 2) for L in "AB"}
    print(f"Quiz 4 answer positions: multiple choice {counts}, True/False {tf}")
