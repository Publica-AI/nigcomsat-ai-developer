"""Week 5 · Day 3: Regression Forecasts + Honest Ranges (+ final-project Checkpoint 4)."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

import w6forecast as W
from common import BRAND as B
from webdeck import logos_title_block
from w6forecast import BASELINE_CODE, FEATURE_CODE, H, X_COLS, facts, load, make_features, walk_forward_errors

CODE = "W5D3"
TITLE = "Regression Forecasts + Honest Ranges"

GRID, AXIS = "#24384F", "#9DB0C6"
RED, GOLD, GREEN = "#FF6B6F", "#F5B83D", "#3CCB7F"


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


def dt(t):
    """3 Nov 2025 (no leading zero)."""
    t = pd.Timestamp(t)
    return f"{t.day} {t:%b %Y}"


def dm(t):
    t = pd.Timestamp(t)
    return f"{t.day} {t:%b}"


# =============================================================================
# EXTRA NUMBERS FOR TODAY (same shared functions, so same code as the notebook)
# =============================================================================
@lru_cache(maxsize=1)
def day_facts():
    F = facts()
    tickets, _, _ = load()
    feat = make_features(tickets)
    cut = feat.index[-H]
    train_f, test_f = feat.loc[:cut].iloc[:-1], feat.loc[cut:]
    act = test_f["target"].values.astype(float)
    pred = F["reg_pred"].values
    rate_fc = F["fc"]["rate_seasonal_naive"].values
    D = {"tickets": tickets, "feat": feat, "train_f": train_f, "test_f": test_f, "act": act, "pred": pred,
         "rate_fc": rate_fc, "lag1": test_f["tickets_lag1"].values}

    def inside(f, half):
        return (act >= f - half) & (act <= f + half)
    D["in_insample"] = inside(pred, F["band_insample"]["half"])
    D["in_wf"] = inside(pred, F["band_walkforward"]["half"])
    D["in_summer"] = inside(pred, F["band_summer_only"]["half"])
    D["in_rate"] = inside(rate_fc, F["band_rate"]["half"])
    for k, key in (("in_insample", "band_insample"), ("in_wf", "band_walkforward"),
                   ("in_summer", "band_summer_only"), ("in_rate", "band_rate")):
        assert int(D[k].sum()) == F[key]["covered"], k
    wf = walk_forward_errors(train_f, X_COLS, first=W.FIRST_ERR_ROW)
    D["wf_err"] = pd.Series(wf, index=train_f.index[W.FIRST_ERR_ROW:])
    D["wf_big"] = D["wf_err"].abs().idxmax()
    D["summer_row"] = int(train_f.index.get_loc(F["band_summer_only"]["from"]))
    D["context"] = tickets["tickets_raised"].iloc[-H - 8:-H]          # the 8 weeks before the test
    D["leak_weeks"] = tickets["tickets_raised"].loc["2025-10-06":"2025-11-10"]
    D["per_1000"] = F["coef"]["terminals"] * 1000
    D["gain_vs_onestep"] = F["onestep_naive_mae"] - F["reg_mae"]
    D["first_err"] = float(F["reg_err"].iloc[0])
    D["first_pred"] = float(pred[0])
    D["first_act"] = int(act[0])
    D["first_lag1"] = int(D["lag1"][0])
    D["n_year1"] = F["rows_lost"]
    D["woy_first_train"] = int(train_f.index[0].isocalendar().week)
    return D


# =============================================================================
# LOCAL SVG HELPERS
# =============================================================================
TABLE_CSS = ("<style>.sb{width:100%;border-collapse:separate;border-spacing:0 6px;font-size:23px}"
             ".sb th{color:#9DB0C6;font-size:18px;text-align:left;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:0 14px}"
             ".sb td{background:#12233A;padding:9px 14px}.sb td:first-child{border-radius:14px 0 0 14px}"
             ".sb td:last-child{border-radius:0 14px 14px 0}.sb tr.win td{background:#123A33}.sb tr.dim td{color:#9DB0C6}</style>")


def band_svg(D, fc, half, inside, *, label, color=GOLD, w=1420, h=440, d0=0.3):
    """Last 8 training weeks (grey), then the 8 held-out weeks: forecast, ± band, and the actual weeks as dots
    (green inside the band, red outside)."""
    ctx = D["context"].values.astype(float)
    act = D["act"]
    n_ctx, n = len(ctx), len(act)
    tot = n_ctx + n
    L, R, T, Bm = 80, w - 250, 24, h - 56
    lo_v, hi_v = 40, 90

    def X(i):
        return L + i / (tot - 1) * (R - L)

    def Y(v):
        v = min(max(v, lo_v), hi_v)
        return Bm - (v - lo_v) / (hi_v - lo_v) * (Bm - T)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for yv in range(40, 91, 10):
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}" stroke-width="1"/>'
                 f'<text x="{L - 14}" y="{Y(yv) + 7:.1f}" fill="{AXIS}" font-size="19" text-anchor="end">{yv}</text>')
    xd = (X(n_ctx - 1) + X(n_ctx)) / 2
    o.append(f'<line x1="{xd:.1f}" x2="{xd:.1f}" y1="{T}" y2="{Bm}" stroke="{AXIS}" stroke-width="2" stroke-dasharray="6 6"/>'
             f'<text x="{xd - 12:.1f}" y="{T + 22}" fill="{AXIS}" font-size="19" font-weight="700" text-anchor="end">← the past (training)</text>'
             f'<text x="{xd + 12:.1f}" y="{T + 22}" fill="#EAF2FB" font-size="19" font-weight="700">8 held-out weeks →</text>')
    pts = " L".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(ctx))
    o.append(f'<path class="draw" style="--d:{d0:.1f}s;--dur:1.2s" d="M{pts}" fill="none" stroke="#6F849C" stroke-width="3.5" stroke-linejoin="round"/>')
    up = [(X(n_ctx + i), Y(fc[i] + half)) for i in range(n)]
    dn = [(X(n_ctx + i), Y(fc[i] - half)) for i in range(n)][::-1]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in up + dn)
    o.append(f'<polygon class="anim a-fade" style="--d:{d0 + 1.0:.1f}s" points="{poly}" fill="{color}" fill-opacity=".22" stroke="{color}" stroke-opacity=".5"/>')
    fpts = " L".join(f"{X(n_ctx + i):.1f},{Y(v):.1f}" for i, v in enumerate(fc))
    o.append(f'<path class="anim a-fade" style="--d:{d0 + 1.0:.1f}s" d="M{fpts}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="10 7"/>')
    for i, v in enumerate(act):
        c = GREEN if inside[i] else RED
        x, y = X(n_ctx + i), Y(v)
        o.append(f'<g class="anim a-pop" style="--d:{d0 + 1.6 + i * .22:.2f}s;transform-origin:{x:.0f}px {y:.0f}px">'
                 f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{c}" stroke="{B["space"]}" stroke-width="3"/></g>')
    k = int(inside.sum())
    xr = R + 30
    o.append(f'<g class="anim a-pop" style="--d:{d0 + 1.8 + n * .22:.2f}s;transform-origin:{xr + 90:.0f}px {h / 2:.0f}px">'
             f'<text x="{xr + 100}" y="{h / 2 - 20:.0f}" fill="{GREEN if k >= 7 else RED}" font-size="76" font-weight="800" text-anchor="middle">{k}/8</text>'
             f'<text x="{xr + 100}" y="{h / 2 + 20:.0f}" fill="{AXIS}" font-size="20" font-weight="700" text-anchor="middle">weeks inside</text>'
             f'<text x="{xr + 100}" y="{h / 2 + 50:.0f}" fill="{color}" font-size="22" font-weight="800" text-anchor="middle">{label}</text></g>')
    idx = list(D["context"].index) + list(D["test_f"].index)
    for i in (0, n_ctx, tot - 1):
        anchor = "start" if i == 0 else ("end" if i == tot - 1 else "middle")
        o.append(f'<text x="{X(i):.1f}" y="{h - 18}" fill="{AXIS}" font-size="19" text-anchor="{anchor}">{dm(idx[i])}</text>')
    o.append("</svg>")
    return "".join(o)


def leak_svg(D, w=1420, h=300):
    """Six real weeks around the cut: shift(1) brings last week forward; shift(-1) drags next week back."""
    s = D["leak_weeks"]
    n = len(s)
    bw, gap, x0, y0 = 190, 36, 40, 120
    tgt = list(s.index).index(pd.Timestamp("2025-11-03"))
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">',
         '<defs><marker id="ah" markerUnits="userSpaceOnUse" markerWidth="20" markerHeight="20" refX="16" refY="10" orient="auto"><path d="M0,0 L20,10 L0,20 z" fill="#EAF2FB"/></marker>'
         f'<marker id="ahg" markerUnits="userSpaceOnUse" markerWidth="20" markerHeight="20" refX="16" refY="10" orient="auto"><path d="M0,0 L20,10 L0,20 z" fill="{GREEN}"/></marker>'
         f'<marker id="ahr" markerUnits="userSpaceOnUse" markerWidth="20" markerHeight="20" refX="16" refY="10" orient="auto"><path d="M0,0 L20,10 L0,20 z" fill="{RED}"/></marker></defs>']
    for i, (t, v) in enumerate(s.items()):
        x = x0 + i * (bw + gap)
        on = i == tgt
        fill = B["teal_d"] if on else ("#12233A" if i < tgt else "#2A1A22")
        o.append(f'<g class="anim a-pop" style="--d:{.2 + i * .12:.2f}s;transform-origin:{x + bw / 2:.0f}px {y0 + 45}px">'
                 f'<rect x="{x}" y="{y0}" width="{bw}" height="90" rx="14" fill="{fill}" stroke="{GOLD if on else GRID}" stroke-width="{4 if on else 2}"/>'
                 f'<text x="{x + bw / 2}" y="{y0 + 58}" fill="#fff" font-size="40" font-weight="800" text-anchor="middle">{int(v)}</text>'
                 f'<text x="{x + bw / 2}" y="{y0 + 122}" fill="{"#EAF2FB" if on else AXIS}" font-size="20" font-weight="700" text-anchor="middle">{dm(t)}</text></g>')
    xt = x0 + tgt * (bw + gap) + bw / 2
    xp = x0 + (tgt - 1) * (bw + gap) + bw / 2
    xn = x0 + (tgt + 1) * (bw + gap) + bw / 2
    o.append(f'<text class="anim a-fade" style="--d:.9s" x="{xt:.0f}" y="{y0 + 160}" fill="{GOLD}" font-size="21" font-weight="800" text-anchor="middle">the week we forecast</text>')
    o.append(f'<path class="draw" style="--d:1.2s;--dur:.8s" d="M{xp:.0f} {y0 - 8} Q{(xp + xt) / 2:.0f} {y0 - 70} {xt - 20:.0f} {y0 - 10}" fill="none" stroke="{GREEN}" stroke-width="4" marker-end="url(#ahg)"/>')
    o.append(f'<text class="anim a-fade" style="--d:1.6s" x="{(xp + xt) / 2 - 40:.0f}" y="{y0 - 74}" fill="{GREEN}" font-size="23" font-weight="800" text-anchor="middle">shift(1): last week ✅</text>')
    o.append(f'<path class="draw" style="--d:2.2s;--dur:.8s" d="M{xn:.0f} {y0 - 8} Q{(xn + xt) / 2:.0f} {y0 - 70} {xt + 20:.0f} {y0 - 10}" fill="none" stroke="{RED}" stroke-width="4" marker-end="url(#ahr)"/>')
    o.append(f'<text class="anim a-fade" style="--d:2.6s" x="{(xn + xt) / 2 + 60:.0f}" y="{y0 - 74}" fill="{RED}" font-size="23" font-weight="800" text-anchor="middle">shift(-1): next week ❌ 📰</text>')
    o.append("</svg>")
    return "".join(o)


def clock_svg(size=440):
    """Week of year as a clock face: sin52 and cos52 are where the week sits on the circle."""
    c, r = size / 2, size / 2 - 70
    o = [f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}">',
         f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{GRID}" stroke-width="2"/>']
    for wk in range(1, 53):
        a = 2 * np.pi * wk / 52
        x, y = c + r * np.sin(a), c - r * np.cos(a)
        rainy = 14 <= wk <= 44
        col = GOLD if wk == 52 else (B["teal_d"] if wk == 1 else ("#3B8BE0" if rainy else "#53657C"))
        rad = 13 if wk in (1, 52) else 7
        o.append(f'<circle class="anim a-pop" style="--d:{.2 + wk * .025:.2f}s;transform-origin:{x:.0f}px {y:.0f}px" cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{col}"/>')
    a1, a52 = 2 * np.pi / 52, 0
    o.append(f'<text x="{c + (r + 36) * np.sin(a1) + 18:.0f}" y="{c - (r + 36) * np.cos(a1) + 4:.0f}" fill="{B["teal_d"]}" font-size="22" font-weight="800">wk 1</text>')
    o.append(f'<text x="{c + (r + 36) * np.sin(a52) - 30:.0f}" y="{c - (r + 36) * np.cos(a52) + 4:.0f}" fill="{GOLD}" font-size="22" font-weight="800" text-anchor="end">wk 52</text>')
    o.append(f'<text x="{c}" y="{c - 6}" fill="#EAF2FB" font-size="26" font-weight="800" text-anchor="middle">neighbours,</text>'
             f'<text x="{c}" y="{c + 26}" fill="#EAF2FB" font-size="26" font-weight="800" text-anchor="middle">not 51 apart</text>'
             f'<text x="{c}" y="{size - 14}" fill="{AXIS}" font-size="19" text-anchor="middle">🔵 rainy-season weeks (Apr–Oct)</text>')
    o.append("</svg>")
    return "".join(o)


def split_svg(F, w=1420, h=220):
    """104 weeks as one bar: year 1 only feeds lag52; year 2 = 44 training rows + 8 test weeks."""
    n = F["n_weeks"]
    L, R = 20, w - 20

    def X(i):
        return L + i / n * (R - L)
    y1, ntr = F["rows_lost"], F["train_f"][2]
    ly, lh = 70, 70
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">',
         f'<rect class="anim a-left" style="--d:.3s" x="{X(0):.1f}" y="{ly}" width="{X(y1) - X(0) - 4:.1f}" height="{lh}" rx="14" fill="#33465E"/>',
         f'<text class="anim a-fade" style="--d:.6s" x="{(X(0) + X(y1)) / 2:.1f}" y="{ly + 44}" fill="#C9D6E5" font-size="24" font-weight="800" text-anchor="middle">'
         f'2024 · {y1} weeks · only feeds lag52</text>',
         f'<rect class="anim a-left" style="--d:.9s" x="{X(y1):.1f}" y="{ly}" width="{X(y1 + ntr) - X(y1) - 4:.1f}" height="{lh}" rx="14" fill="{B["blue_d"]}"/>',
         f'<text class="anim a-fade" style="--d:1.2s" x="{(X(y1) + X(y1 + ntr)) / 2:.1f}" y="{ly + 44}" fill="#fff" font-size="24" font-weight="800" text-anchor="middle">'
         f'🏋🏾 TRAIN · {ntr} rows</text>',
         f'<rect class="anim a-right" style="--d:1.5s" x="{X(y1 + ntr):.1f}" y="{ly}" width="{X(n) - X(y1 + ntr):.1f}" height="{lh}" rx="14" fill="{B["teal_d"]}"/>',
         f'<text class="anim a-fade" style="--d:1.8s" x="{(X(y1 + ntr) + X(n)) / 2:.1f}" y="{ly + 44}" fill="#fff" font-size="22" font-weight="800" text-anchor="middle">📝 {H}</text>',
         f'<text x="{X(0):.1f}" y="{ly - 18}" fill="{AXIS}" font-size="19">{dt(F["first_week"])}</text>',
         f'<text x="{X(y1):.1f}" y="{ly + lh + 34}" fill="{AXIS}" font-size="19">{dt(F["train_f"][0])}</text>',
         f'<text x="{X(y1 + ntr) - 8:.1f}" y="{ly + lh + 34}" fill="{AXIS}" font-size="19" text-anchor="end">{dt(F["train_f"][1])}</text>',
         f'<text x="{X(n):.1f}" y="{ly - 18}" fill="{AXIS}" font-size="19" text-anchor="end">test: {dm(F["holdout"][0])} – {dt(F["holdout"][1])}</text>',
         "</svg>"]
    return "".join(o)


def misses_svg(D, F, w=1420, h=400):
    """The 32 honest past misses of the regression (walk-forward, one week ahead), with the ±band they give."""
    e = D["wf_err"]
    n = len(e)
    half, half_s = F["band_walkforward"]["half"], F["band_summer_only"]["half"]
    L, R, T, Bm = 90, w - 30, 30, h - 56
    lim = 18

    def X(i):
        return L + (i + .5) / n * (R - L)

    def Y(v):
        return T + (lim - v) / (2 * lim) * (Bm - T)
    slot = (R - L) / n
    xs = L + (D["summer_row"] - W.FIRST_ERR_ROW) * slot
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">',
         f'<rect x="{L}" y="{T}" width="{xs - L:.1f}" height="{Bm - T}" fill="{GOLD}" fill-opacity=".08" rx="6"/>',
         f'<text x="{(L + xs) / 2:.1f}" y="{Bm - 12}" fill="{GOLD}" font-size="19" font-weight="800" text-anchor="middle">spring: the rains arrive</text>',
         f'<text x="{(xs + R) / 2:.1f}" y="{T + 24}" fill="{AXIS}" font-size="19" font-weight="800" text-anchor="middle">summer only (from {dm(F["band_summer_only"]["from"])}): calm weeks</text>']
    for yv in (-15, -10, -5, 0, 5, 10, 15):
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}" stroke-width="{2 if yv == 0 else 1}"/>'
                 f'<text x="{L - 12}" y="{Y(yv) + 7:.1f}" fill="{AXIS}" font-size="18" text-anchor="end">{yv:+d}</text>')
    for i, v in enumerate(e.values):
        col = RED if abs(v) > half else (GOLD if abs(v) > half_s else B["teal_d"])
        y0, y1 = (Y(v), Y(0)) if v >= 0 else (Y(0), Y(v))
        o.append(f'<rect class="anim a-pop" style="--d:{.3 + i * .05:.2f}s;transform-origin:{X(i):.0f}px {Y(0):.0f}px" x="{X(i) - slot * .32:.1f}" '
                 f'y="{y0:.1f}" width="{slot * .64:.1f}" height="{max(y1 - y0, 2):.1f}" rx="3" fill="{col}"/>')
    for hv, col, lab, d in ((half, "#EAF2FB", f"± {half:.2f}: 90% of ALL misses", 2.2), (half_s, GOLD, f"± {half_s:.2f}: summer misses only", 2.8)):
        for sgn in (1, -1):
            o.append(f'<line class="anim a-fade" style="--d:{d}s" x1="{L}" x2="{R}" y1="{Y(sgn * hv):.1f}" y2="{Y(sgn * hv):.1f}" stroke="{col}" stroke-width="2.5" stroke-dasharray="10 7"/>')
        o.append(f'<text class="anim a-fade" style="--d:{d}s" x="{R - 6}" y="{Y(-hv) + 26:.1f}" fill="{col}" font-size="20" font-weight="800" text-anchor="end">{lab}</text>')
    ib = list(e.index).index(D["wf_big"])
    o.append(f'<text class="anim a-fade" style="--d:2s" x="{X(ib) + 18:.1f}" y="{Y(e.iloc[ib]) + 8:.1f}" fill="{RED}" font-size="21" font-weight="800">'
             f'{dm(D["wf_big"])}: {e.iloc[ib]:+.1f} (rainy season starts)</text>')
    for m in (4, 6, 8, 10):
        i = int(np.searchsorted(e.index, pd.Timestamp(2025, m, 1)))
        o.append(f'<text x="{X(i):.1f}" y="{h - 16}" fill="{AXIS}" font-size="19" text-anchor="middle">{pd.Timestamp(2025, m, 1):%b}</text>')
    o.append("</svg>")
    return "".join(o)


def walk_svg(w=1420, h=280):
    """Walk forward: fit on the weeks before, forecast the next one, write down the miss, step on."""
    rows, cell, x0 = 4, 26, 160
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for r in range(rows):
        y = 18 + r * 56
        k = 12 + r
        d = .3 + r * .45
        o.append(f'<g class="anim a-left" style="--d:{d:.2f}s"><text x="0" y="{y + 26}" fill="#EAF2FB" font-size="21" font-weight="800">step {r + 1}</text>')
        for i in range(k):
            o.append(f'<rect x="{x0 + i * (cell + 4)}" y="{y}" width="{cell}" height="36" rx="5" fill="{B["blue_d"]}"/>')
        xf = x0 + k * (cell + 4)
        o.append(f'<rect x="{xf}" y="{y}" width="{cell}" height="36" rx="5" fill="{GOLD}"/>')
        o.append(f'<text x="{xf + cell + 20}" y="{y + 26}" fill="{GOLD}" font-size="20" font-weight="700">forecast it → write the miss</text></g>')
    o.append(f'<text x="{x0}" y="{h - 8}" fill="{AXIS}" font-size="19">🟦 weeks it may learn from (only the past) · 🟨 the next week, unseen</text>')
    o.append("</svg>")
    return "".join(o)


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    F = facts()
    D = day_facts()
    bm = F["baseline_mae"]
    reg, one, rate = F["reg_mae"], F["onestep_naive_mae"], bm["rate_seasonal_naive"]
    bi, bw, bs, br = F["band_insample"], F["band_walkforward"], F["band_summer_only"], F["band_rate"]
    ex_mid, ex_lo, ex_hi = F["rate_interval_example"]
    co = F["coef"]
    nwf = bw["n_errors"]

    coef_rows = "".join(
        f'<tr class="anim a-left{" win" if c == "terminals" else ""}" style="--d:{.4 + k * .15:.2f}s"><td class="mono">{c}</td>'
        f'<td class="mono" style="color:{GREEN if co[c] > 0 else GOLD};font-weight:800">{co[c]:+.4f}</td></tr>'
        for k, c in enumerate(X_COLS))

    like_rows = [
        ("naive (W5D2)", "8 weeks, blind", "the last training week", bm["naive"], ""),
        ("seasonal naive (W5D2)", "8 weeks, blind", "the same weeks last year", bm["seasonal_naive"], ""),
        ("one-step naive", "1 week", "last week's REAL count", one, ""),
        ("regression", "1 week", "last week's REAL count + 4 more columns", reg, ""),
        ("rate seasonal naive (W5D2)", "8 weeks, blind", "last year's tickets per terminal × terminals", rate, " win"),
    ]
    like_html = "".join(
        f'<tr class="anim a-left{cls}" style="--d:{.3 + k * .2:.2f}s"><td><b>{m}</b></td><td>{hz}</td><td class="small">{info}</td>'
        f'<td class="mono" style="font-weight:800;color:{GREEN if cls else "#EAF2FB"}">{v:.2f}</td></tr>'
        for k, (m, hz, info, v, cls) in enumerate(like_rows))

    cp_rows = [
        ("naive", "8 weeks, blind", f'{bm["naive"]:.2f}', "—", "—", ""),
        ("seasonal naive", "8 weeks, blind", f'{bm["seasonal_naive"]:.2f}', "—", "—", ""),
        ("rate seasonal naive", "8 weeks, blind", f"{rate:.2f}", f'± {br["half"]:.2f}', f'{br["covered"]} of 8', " win"),
        ("one-step naive", "1 week", f"{one:.2f}", "—", "—", ""),
        ("regression · code-book band", "1 week", f"{reg:.2f}", f'± {bi["half"]:.2f}', f'{bi["covered"]} of 8', " dim"),
        ("regression · honest band", "1 week", f"{reg:.2f}", f'± {bw["half"]:.2f}', f'{bw["covered"]} of 8', ""),
    ]
    cp_html = "".join(
        f'<tr class="anim a-left{cls}" style="--d:{.3 + k * .15:.2f}s"><td><b>{m}</b></td><td>{hz}</td><td class="mono">{v}</td>'
        f'<td class="mono">{b}</td><td class="mono">{c}</td></tr>'
        for k, (m, hz, v, b, c, cls) in enumerate(cp_rows))

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:70px;top:150px;width:560px;height:560px">
  <svg viewBox="0 0 560 560" width="560" height="560">
    <rect x="70" y="20" width="420" height="520" rx="46" fill="#12233A" stroke="#33465E" stroke-width="6" class="anim a-pop" style="--d:.2s;transform-origin:280px 280px"/>
    <g class="anim a-left" style="--d:.6s"><rect x="110" y="90" width="260" height="78" rx="24" fill="#33465E"/>
      <text x="240" y="140" font-size="28" font-weight="800" fill="#EAF2FB" text-anchor="middle">I'm on my way 🚗</text></g>
    <g class="anim a-right" style="--d:1.3s"><rect x="150" y="210" width="300" height="140" rx="24" fill="{B['teal_d']}"/>
      <text x="300" y="262" font-size="28" font-weight="800" fill="#fff" text-anchor="middle">30 to 90 minutes,</text>
      <text x="300" y="300" font-size="24" fill="#fff" text-anchor="middle">Third Mainland Bridge</text>
      <text x="300" y="332" font-size="24" fill="#fff" text-anchor="middle">permitting 🌉</text></g>
    <g class="anim a-pop" style="--d:2s;transform-origin:280px 440px"><text x="280" y="465" font-size="120" font-weight="800" fill="{GOLD}" text-anchor="middle">±</text></g>
  </svg></div>
<div style="max-width:880px;margin-top:40px">
  <div class="kicker anim">Week 5 · Day 3</div>
  <h1 class="anim" style="--d:.2s">Regression<br>Forecasts +<br><span class="hl">Honest Ranges</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">A forecast is a guess. An honest forecast says<br>how wrong it might be, and checks that it was right. ⚖️</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex">{logos_title_block()}</div>
</div>""",
          "Welcome back. Last time Grandma's forecast, adjusted for the bigger network, set a very high bar. Today: a regression forecast, a fair comparison, "
          "and the part most people skip: a range that tells the planner how much to trust the number. We finish with final-project Checkpoint 4."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">One rule, one fair fight, one honest range</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:260px;padding:40px 24px"><div class="icon">🔒</div><h3>Leak rule</h3><p class="small">features known before the week</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:260px;padding:40px 24px"><div class="icon">📈</div><h3>Regression</h3><p class="small">and like-with-like scoring</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:260px;padding:40px 24px"><div class="icon">↔️</div><h3>Honest range</h3><p class="small">a band you checked</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:260px;padding:40px 24px"><div class="icon">⚖️</div><h3>Checkpoint 4</h3><p class="small">your honest test</p></div>
</div>
<div class="row anim" style="--d:1.8s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 50 min hands-on</span><span class="pill gold">🏁 20 min Checkpoint 4</span><span class="pill">🎬 10 min wrap-up</span>
</div>""",
          "Four moves. The hands-on builds every number on the slides. The last 20 minutes are the final-project Checkpoint 4, one by one."),

        # 3 ─ hook
        S("""
<div class="kicker anim">Quick question</div>
<h2 class="anim" style="--d:.1s">Your friend is coming from the Island. 📱</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🚗</div><h3>Tobi: “I'm on my way”</h3>
    <p class="muted">One number, no warning. Could be 10 minutes. Could be 2 hours. You find out when the food is cold.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill gold">point forecast</span></div></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">🌉</div><h3>Amaka: “30 to 90 minutes, Third Mainland permitting”</h3>
    <p class="muted">A most-likely time, a range, and the thing that could blow it up.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill teal">interval forecast</span></div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:36px;text-align:center">You can <b class="hl">plan</b> around Amaka. And if she says “90% of the time” <br>she'd better be right 9 times in 10, not 5. 😏</p>""",
          "Let the room laugh: everyone has a Tobi. Then land it: the planner in the NOC needs Amaka's sentence, not Tobi's. "
          "Today's second half is about making Amaka's range honest, and checking it."),

        # 4 ─ the bar from last time
        S(f"""
<div class="kicker anim">Last time · the 8 held-out weeks ({dm(F["holdout"][0])} – {dt(F["holdout"][1])})</div>
<h2 class="anim" style="--d:.1s">The bar any model must clear</h2>
<div class="col" style="gap:14px;margin-top:20px">
  {"".join(f'<div class="row anim a-left" style="--d:{.3 + k * .2:.2f}s;gap:20px;align-items:center"><span style="width:420px;font-size:26px;font-weight:700">{lab}</span><div style="height:44px;width:{v / bm["seasonal_naive"] * 760:.0f}px;border-radius:10px;background:{col}"></div><b class="mono" style="font-size:30px;color:{col}">{v:.2f}</b></div>' for k, (lab, v, col) in enumerate((("seasonal naive", bm["seasonal_naive"], "#6F849C"), ("moving average", bm["moving_average"], "#6F849C"), ("exp. smoothing", bm["exp_smoothing"], "#6F849C"), ("naive", bm["naive"], B["blue_d"]), ("rate seasonal naive", rate, GREEN))))}
</div>
<p class="sub anim" style="--d:1.5s;margin-top:28px;text-align:center">MAE, tickets per week. Grandma + the bigger network: <b class="good">{rate:.2f}</b>, all 8 weeks forecast blind.</p>""",
          f"Recap of W5D2. Every bar is a mean absolute error on the same 8 held-out weeks. The rate seasonal naive (last year's tickets per terminal × today's terminals) scored {rate:.2f}. "
          "Any model we build today has to beat THAT, not the weakest baseline."),

        # 5 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">A forecast is a regression<br>with one rule 🔒</h1>""",
          "Section break.", cls="center"),

        # 6 ─ the leak rule
        S(f"""
<div class="kicker anim">The leak rule</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Every feature must be known <span class="hl">before the week starts</span></h2>
<div class="card anim" style="--d:.2s;padding:20px 24px;margin-top:10px">{leak_svg(D)}</div>
<div class="grid2" style="margin-top:20px;gap:24px">
  <div class="card anim a-left" style="--d:2.8s;padding:18px 26px"><p style="font-size:25px"><code>shift(1)</code>: on 3 Nov's row you see <b class="good">27 Oct's {D["first_lag1"]}</b>. You knew that on Monday morning. ✅</p></div>
  <div class="card anim a-right" style="--d:3.1s;padding:18px 26px;border-color:#E5484D"><p style="font-size:25px"><code>shift(-1)</code>: you see <b class="bad">10 Nov's {int(D["leak_weeks"].iloc[-1])}</b>. That's reading <b>tomorrow's newspaper</b>. 📰❌</p></div>
</div>""",
          "Quiz 4 questions 7 and 8. It's the 14:00 test from Week 4 Day 3, for weekly data: could I compute this on Monday morning, before the week's tickets arrive? "
          "shift with a positive number looks back. shift(-1) copies next week's answer onto this week's row: brilliant in a notebook, impossible in the NOC."),

        # 7 ─ the five columns
        S("""
<div class="kicker anim">The code book's feature table · <code>make_features(tickets)</code></div>
<h2 class="anim" style="--d:.1s">Five columns the model reads</h2>
<div class="grid2" style="margin-top:22px;gap:20px">
  <div class="card anim a-pop" style="--d:.3s;display:flex;gap:24px;align-items:center;padding:22px 28px"><span class="icon" style="margin:0">⏮️</span><div><h3 style="margin:0"><code>tickets_lag1</code></h3><p class="muted">last week's count: <code>shift(1)</code></p></div></div>
  <div class="card anim a-pop" style="--d:.5s;display:flex;gap:24px;align-items:center;padding:22px 28px"><span class="icon" style="margin:0">📅</span><div><h3 style="margin:0"><code>tickets_lag52</code></h3><p class="muted">the same week last year: <code>shift(52)</code></p></div></div>
  <div class="card anim a-pop" style="--d:.7s;display:flex;gap:24px;align-items:center;padding:22px 28px"><span class="icon" style="margin:0">📡</span><div><h3 style="margin:0"><code>terminals</code></h3><p class="muted">how big the network is this week</p></div></div>
  <div class="card anim a-pop" style="--d:.9s;display:flex;gap:24px;align-items:center;padding:22px 28px"><span class="icon" style="margin:0">🕰️</span><div><h3 style="margin:0"><code>sin52</code> + <code>cos52</code></h3><p class="muted">week of the year on a clock (next slide)</p></div></div>
</div>
<div class="card anim a-pop glow" style="--d:1.1s;margin-top:20px;display:flex;gap:24px;align-items:center;padding:22px 28px"><span class="icon" style="margin:0">🎯</span><div><h3 style="margin:0"><code>target</code></h3><p class="muted">this week's tickets: the answer the regression learns to reproduce</p></div></div>""",
          "Quiz 4 question 7: every column is knowable before the week starts. terminals is the number of terminals live this week; the planners know that from the rollout plan. "
          "The target is the column the regression tries to reproduce."),

        # 8 ─ clock face
        S(f"""
<div class="kicker anim">Why sin and cos?</div>
<h2 class="anim" style="--d:.1s">The year is a clock, not a ruler 🕰️</h2>
<div class="row" style="gap:50px;align-items:center;margin-top:6px">
  <div class="card anim a-pop" style="--d:.2s;padding:12px;flex:none">{clock_svg()}</div>
  <div class="col" style="flex:1;gap:20px">
    <div class="card anim a-right" style="--d:1.4s;padding:20px 26px"><p style="font-size:26px">As a plain number, week 52 and week 1 look <b class="bad">51 apart</b>. On the calendar they are next-door neighbours.</p></div>
    <div class="card anim a-right" style="--d:1.8s;padding:20px 26px"><p style="font-size:26px"><code>sin52</code> and <code>cos52</code> are where the week sits on the circle: <b class="hl">two columns instead of 52</b>, and the cycle joins up.</p></div>
    <pre class="code anim" style="--d:2.2s;font-size:22px">woy = df.index.isocalendar().week
f["sin52"] = np.sin(2 * np.pi * woy / 52)
f["cos52"] = np.cos(2 * np.pi * woy / 52)</pre>
  </div>
</div>""",
          "Quiz 4 question 10. Think of the hour hand: 11 o'clock and 1 o'clock are close, even though 11 and 1 are far apart as numbers. "
          "Keep one doubt for later: a circle is SMOOTH. Our rainy season doesn't ease in; it switches on in April and off in November."),

        # 9 ─ rows lost + the split
        S(f"""
<div class="kicker anim">Where the rows go</div>
<h2 class="anim" style="--d:.1s;font-size:54px">104 weeks → {F["feat_rows"]} usable rows</h2>
<div class="card anim" style="--d:.2s;padding:22px 26px">{split_svg(F)}</div>
<div class="grid2" style="margin-top:22px;gap:24px">
  <div class="card anim a-left" style="--d:2s;padding:20px 26px"><p style="font-size:25px"><code>shift(52)</code> has nothing to copy in 2024, so <code>dropna()</code> removes the first <b class="hl">{F["rows_lost"]} rows</b>.</p></div>
  <div class="card anim a-right" style="--d:2.3s;padding:20px 26px"><p style="font-size:25px">Train on <b>{F["train_f"][2]} weeks</b>, test on the same <b>8 weeks</b> as last time. Five columns, {F["train_f"][2]} rows: a small exam.</p></div>
</div>""",
          f"Quiz 4 question 9. 2024 is still used: it's where every lag52 value comes from. Training: {dt(F['train_f'][0])} to {dt(F['train_f'][1])} ({F['train_f'][2]} rows). "
          "Test: the same 8 weeks as Week 5 Day 2, so every number today can be compared with last time."),

        # 10 ─ fit + coefficients
        S(f"""{TABLE_CSS}
<div class="kicker anim">Fit, then read the coefficients like an engineer</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Does every sign make sense? 🧐</h2>
<div class="row" style="gap:40px;margin-top:6px;align-items:flex-start">
  <div class="col" style="flex:1.1;gap:18px">
    <pre class="code anim" style="--d:.2s;font-size:22px">reg = LinearRegression().fit(
    train_f[X_COLS], train_f["target"])
pred = reg.predict(test_f[X_COLS])</pre>
    <div class="card anim a-pop glow" style="--d:1.4s;padding:22px 26px"><p style="font-size:26px"><code>terminals</code> <b class="good">{co["terminals"]:+.4f}</b> per terminal = about <b class="hl">+{D["per_1000"]:.0f} tickets a week per 1,000 terminals</b>. Bigger network, more tickets. ✅</p></div>
    <p class="anim small" style="--d:1.8s">A <b class="bad">negative</b> terminals sign would be a warning: investigate before you trust anything.</p>
  </div>
  <div style="flex:.9"><table class="sb"><tr class="anim" style="--d:.3s"><th>column</th><th>coefficient</th></tr>{coef_rows}</table></div>
</div>""",
          f"Quiz 4 question 12. A coefficient is how much the forecast moves for one unit of that column, holding the others still. lag1 {co['tickets_lag1']:+.3f}: half of last week carries over. "
          f"The sin/cos pair together shape the yearly wave. The intercept is {F['intercept']:.1f}: meaningless on its own. Sanity-checking signs is cheap and catches broken features early."),

        # 11 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Like with like ⚖️</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Same weeks, same horizon, same information.</p>""",
          "Section break.", cls="center"),

        # 12 ─ the big claim
        S(f"""
<div class="kicker anim">The regression's score on the 8 held-out weeks</div>
<h2 class="anim" style="--d:.1s">“Half of naive's error!” 🎉</h2>
<div class="grid2" style="margin-top:30px">
  <div class="card anim a-left" style="--d:.3s;text-align:center"><div class="icon">👵🏾</div><h3>naive (W5D2)</h3><div class="stat" style="font-size:120px;color:#9DB0C6">{bm["naive"]:.2f}</div><div class="stat-label">tickets/week off</div></div>
  <div class="card anim a-right" style="--d:.7s;text-align:center;border-color:#F5B83D"><div class="icon">📈</div><h3>regression</h3><div class="stat hl" style="font-size:120px">{reg:.2f}</div><div class="stat-label">tickets/week off</div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:30px;text-align:center">Before you clap: <b class="bad">what did each one know</b> when it made each forecast? 🤔</p>""",
          "Let the room enjoy it for a moment. Then the question. Hold the answer for the next slide."),

        # 13 ─ unfair
        S(f"""
<div class="kicker anim">The head start</div>
<h2 class="anim" style="--d:.1s;font-size:54px">One sat the exam blind. One got hints. 🎁</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🙈</div><h3>naive: 8 weeks, blind</h3>
    <p class="muted">Stood on {dm(F["last_train_week"][0])} and said {F["last_train_week"][1]} for all 8 weeks. Never saw a single November count.</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#F5B83D"><div class="icon">🎁</div><h3>regression: 1 week ahead</h3>
    <p class="muted"><code>tickets_lag1</code> handed it <b style="color:#fff">last week's REAL count</b> every single week. That's a one-week-ahead forecast.</p></div>
</div>
<div class="card anim a-pop glow" style="--d:1.1s;margin-top:24px;padding:22px 30px;text-align:center"><p style="font-size:30px">Make naive the same way (last week's real count): <b class="hl">{one:.2f}</b> vs regression <b>{reg:.2f}</b>. A win of about <b class="good">{D["gain_vs_onestep"]:.1f} ticket</b>, not half.</p></div>""",
          f"Quiz 4 question 11. One-step naive = 'this week will be like last week', using the real count from last week. It scores {one:.2f}. "
          "The regression's honest advantage over that is under one ticket a week. Always compare like with like: same horizon, same information."),

        # 14 ─ like-with-like table
        S(f"""{TABLE_CSS}
<div class="kicker anim">The same 8 weeks · one scorer (MAE) · say how far ahead</div>
<h2 class="anim" style="--d:.1s;font-size:52px;margin-bottom:10px">Beat the BEST baseline, not the weakest</h2>
<table class="sb"><tr class="anim" style="--d:.1s"><th>Method</th><th>How far ahead</th><th>Information used</th><th>MAE</th></tr>{like_html}</table>
<p class="sub anim" style="--d:1.6s;margin-top:20px;text-align:center">Even with a hint every week, the regression ({reg:.2f}) loses to a forecast made <b class="hl">8 weeks blind</b> ({rate:.2f}). 🏆👵🏾</p>""",
          f"The bar from Week 5 Day 2 is the rate seasonal naive at {rate:.2f}. The regression has more columns and a head start and still doesn't beat it. "
          "That's not a failure; it's the result. Next week's backtest checks whether this holds over many origins, not just these 8 weeks."),

        # 15 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">Honest ranges ↔️</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Amaka's sentence, with a number on it, checked.</p>""",
          "Section break.", cls="center"),

        # 16 ─ the code book's band
        S(f"""
<div class="kicker anim">The code book's 90% band · forecast ± 1.645 × residual sd ({F["resid_sd"]:.2f}) = ± {bi["half"]:.2f}</div>
<h2 class="anim" style="--d:.1s;font-size:52px">A “90%” band that's right {bi["covered"]} times in 8 😬</h2>
<div class="card anim" style="--d:.2s;padding:18px 22px">{band_svg(D, D["pred"], bi["half"], D["in_insample"], label=f"± {bi['half']:.2f}")}</div>
<p class="anim" style="--d:4.4s;margin-top:16px;text-align:center">🟢 inside the band · 🔴 outside · gold dashes = the regression's forecast. <b class="hl">{bi["covered"] / 8:.1%}</b> is not 90%.</p>""",
          f"Quiz 4 questions 13 to 15. Residual = actual minus the fitted value on the training weeks; their sd is {F['resid_sd']:.2f}. 1.645 is the normal-curve number that leaves 5% in each tail, "
          f"so ± 1.645 sd is a two-sided 90% band. (The code book's comment calls it 'one-sided-flavoured': it isn't.) It covers {bi['covered']} of 8 held-out weeks. Too narrow."),

        # 17 ─ why
        S(f"""
<div class="kicker anim">Why so narrow?</div>
<h2 class="anim" style="--d:.1s">Two reasons, both fixable 🔍</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🏠</div><h3>It marked its own homework</h3>
    <p class="muted">Training misses: sd <b style="color:#fff">{F["resid_sd"]:.2f}</b>. Misses on weeks it never saw: sd <b class="bad">{F["reg_err_sd"]:.2f}</b>, and on average {abs(F["reg_err_mean"]):.1f} tickets <b style="color:#fff">too high</b>.</p></div>
  <div class="card anim a-right" style="--d:.7s;border-color:#E5484D"><div class="icon">🌧️➡️☀️</div><h3>The season switched off</h3>
    <p class="muted">3 Nov: the rains end. Last week was {D["first_lag1"]}, it forecast <b style="color:#fff">{D["first_pred"]:.1f}</b>, reality was <b class="bad">{D["first_act"]}</b> ({D["first_err"]:+.1f}). A smooth sin/cos wave can't make a step.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:30px;text-align:center">A band measured on easy weeks is <b class="hl">confident about the wrong things</b>.</p>""",
          f"Quiz 4 question 16. In-sample errors are always flattering: the model was fitted to those very weeks. On the held-out weeks the errors have sd {F['reg_err_sd']:.2f} and a bias of {F['reg_err_mean']:+.2f} "
          "(it over-forecasts, because it keeps carrying rainy-season counts into November). The biggest single miss is the first held-out week, the season switch."),

        # 18 ─ the honest recipe
        S(f"""
<div class="kicker anim">The honest recipe</div>
<h2 class="anim" style="--d:.1s;font-size:52px">Measure the misses it made <span class="hl">before it knew the answer</span></h2>
<div class="card anim" style="--d:.2s;padding:20px 26px">{walk_svg()}</div>
<div class="grid2" style="margin-top:20px;gap:24px">
  <div class="card anim a-left" style="--d:2.2s;padding:18px 26px"><p style="font-size:25px">Walk forward through the training weeks from <b>{dm(bw["from"])}</b>: fit, forecast the next week, write down the miss. <b class="hl">{nwf} honest misses.</b></p></div>
  <div class="card anim a-right glow" style="--d:2.5s;padding:18px 26px"><p style="font-size:25px">Band = forecast ± the <b class="hl">90th-percentile miss</b>. No bell-curve guess: just how wrong it actually was.</p></div>
</div>""",
          "This is a preview of Week 6 Day 1's backtesting. walk_forward_errors() refits the regression on every week before row k, forecasts row k, and stores actual minus forecast. "
          "Starting at row 12 means at least 12 rows to fit 6 numbers. The 90th percentile of the absolute misses is the half-width that covered 90% of past misses."),

        # 19 ─ the misses
        S(f"""
<div class="kicker anim">The regression's {nwf} honest past misses · one week ahead</div>
<h2 class="anim" style="--d:.1s;font-size:52px">The big misses live at the season change</h2>
<div class="card anim" style="--d:.2s;padding:18px 22px">{misses_svg(D, F)}</div>
<p class="anim" style="--d:3.2s;margin-top:14px;text-align:center">Include the spring weeks: <b class="good">± {bw["half"]:.2f}</b>. Use summer only: <b class="bad">± {bs["half"]:.2f}</b>.</p>""",
          f"Each bar is one week's miss (actual minus forecast) made with only the weeks before it. The tallest is {dm(D['wf_big'])}, when the rainy season switched on: {D['wf_err'].abs().max():.1f} tickets. "
          "The calm summer weeks are all small. Which weeks you measure the misses on decides how wide the band is."),

        # 20 ─ honest band result
        S(f"""
<div class="kicker anim">Same forecast · band from the honest misses · ± {bw["half"]:.2f}</div>
<h2 class="anim" style="--d:.1s;font-size:52px">{bw["covered"]} of 8. That's a band you can quote ✅</h2>
<div class="card anim" style="--d:.2s;padding:18px 22px">{band_svg(D, D["pred"], bw["half"], D["in_wf"], label=f"± {bw['half']:.2f}", color=GREEN)}</div>
<p class="anim" style="--d:4.4s;margin-top:16px;text-align:center">The one miss is the season switch, 3 Nov. Same forecast as before: <b class="hl">only the width changed</b>.</p>""",
          f"The point forecast is identical to slide 16; we only changed how we size the band. {bw['covered']} of 8 is close to the 90% we claim. "
          "With only 8 test weeks we can't measure coverage to the decimal; we're checking it isn't wildly off, like 5 of 8 was."),

        # 21 ─ the trap
        S(f"""
<div class="kicker anim">The trap</div>
<h2 class="anim" style="--d:.1s;font-size:54px">A band is only as honest as the weeks you measured it on</h2>
<div class="grid2" style="margin-top:26px">
  <div class="card anim a-left" style="--d:.3s;text-align:center;border-color:#16A394"><div class="icon">🌧️☀️</div><h3>Misses from {dm(bw["from"])}</h3><p class="small">includes the April switch</p>
    <div class="stat good" style="font-size:96px">{bw["covered"]}/8</div><div class="stat-label">± {bw["half"]:.2f}</div></div>
  <div class="card anim a-right" style="--d:.7s;text-align:center;border-color:#E5484D"><div class="icon">☀️</div><h3>Misses from {dm(bs["from"])}</h3><p class="small">summer only: calm weeks</p>
    <div class="stat bad" style="font-size:96px">{bs["covered"]}/8</div><div class="stat-label">± {bs["half"]:.2f}</div></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:30px;text-align:center">You're forecasting a season change? <b class="hl">Measure on season changes.</b></p>""",
          "Same code, same recipe, different starting week. Summer-only misses are small, so the band is narrow, and November punishes it. "
          "In your project: make sure your calibration weeks contain the kind of trouble you'll forecast."),

        # 22 ─ the rate forecast's band
        S(f"""
<div class="kicker anim">Grandma + the bigger network, with an honest band · ± {br["half"]:.2f}</div>
<h2 class="anim" style="--d:.1s;font-size:52px">The best forecast gets a band too 🏆</h2>
<div class="card anim" style="--d:.2s;padding:18px 22px">{band_svg(D, D["rate_fc"], br["half"], D["in_rate"], label=f"± {br['half']:.2f}", color=B["teal_d"])}</div>
<p class="anim" style="--d:4.4s;margin-top:16px;text-align:center">Misses of every 8-week rate forecast made from <b>{br["n_origins"]}</b> earlier starting weeks ({br["n_errors"]} misses) → <b class="good">{br["covered"]} of 8</b> inside.</p>""",
          f"rate_past_errors() stands at each earlier week, makes the 8-week rate forecast, and writes down all 8 misses. The 90th percentile of {br['n_errors']} misses is ± {br['half']:.2f}. "
          "Narrower than the regression's band, it covers every held-out week, and the forecast is made 8 weeks ahead without peeking."),

        # 23 ─ don't turn the knob + how to say it
        S(f"""
<div class="kicker anim">Two habits</div>
<h2 class="anim" style="--d:.1s">Don't turn the knob. Say it like Amaka.</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s;border-color:#E5484D"><div class="icon">🎛️❌</div><h3>Raising z until the test looks right</h3>
    <p class="muted">That's tuning on the answers: <b style="color:#fff">expo again</b>. The width must come from misses <b style="color:#fff">before</b> the test.</p></div>
  <div class="card anim a-right glow" style="--d:.7s"><div class="icon">🗣️</div><h3>The honest sentence</h3>
    <p style="font-size:27px">“Week of 3 Nov: most likely around <b class="hl">{ex_mid:.0f}</b>, plausibly <b class="hl">{ex_lo:.0f} to {ex_hi:.0f}</b>; expect bigger misses at season changes.”</p></div>
</div>
<p class="anim" style="--d:1.2s;margin-top:30px;text-align:center">Most likely · a range · the thing that could blow it up. Three parts, every time.</p>""",
          f"Quiz 4 questions 17 and 18. The rate forecast for the week of 3 Nov is {ex_mid:.1f}, band {ex_lo:.1f} to {ex_hi:.1f}. Actual: {D['first_act']}. "
          "A planner can staff for that. Never say '90% sure' about a band nobody checked."),

        # 24 ─ checkpoint 4
        S(f"""{TABLE_CSS}
<div class="kicker anim">🏁 Final project · Checkpoint 4</div>
<h2 class="anim" style="--d:.1s;font-size:52px;margin-bottom:8px">⚖️ Honest test: bring a table like this</h2>
<table class="sb" style="font-size:21px"><tr class="anim" style="--d:.1s"><th>Method</th><th>How far ahead</th><th>MAE</th><th>90% band</th><th>Coverage</th></tr>{cp_html}</table>
<div class="grid2" style="margin-top:16px;gap:20px">
  <div class="card anim a-left" style="--d:1.4s;padding:16px 24px"><p style="font-size:22px">✅ split by time + <code>assert</code> + embargo<br>✅ your baseline on the <b>same period, same scorer</b></p></div>
  <div class="card anim a-right" style="--d:1.6s;padding:16px 24px;border-color:#E5484D"><p style="font-size:22px">⛔ real data stays on NIGCOMSAT systems, not Colab<br>Next: <b class="hl">Week 6 · Day 3: 🎤 Demo day</b></p></div>
</div>""",
          "20 minutes, one by one. Detection briefs bring event-level precision and recall instead of MAE; degradation briefs bring a crossing date and window from more than one starting point. "
          "Every table says how far ahead and what information each method used. If the simple method wins, they say so."),

        # 25 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 50 minutes</div>
  <h2 class="anim" style="--d:.1s">Forecast + fence ↔️</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open <b class="hl">W5D3-exercise</b>, save a copy, run STEP 0</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">A</span><p>Features without a leak + the split</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">B</span><p>Fit, read the signs, compare like with like</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">C</span><p>Three bands: which ones are honest?</p></div>
   <div class="row anim" style="--d:1.1s;gap:18px;align-items:center"><span class="num">D</span><p>Your Checkpoint 4 table</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.3s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🌉</div>
  <h3 style="margin-top:16px">14 checks to pass</h3>
  <p class="muted">🌶️ Pepper task: write Amaka's sentence with real numbers</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Common snags: typing shift(-1) in A1, writing 90 instead of 0.9 in C2, and skipping the toolbox cell."),

        # 26 ─ recap
        S(f"""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:16px;margin-top:6px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">🔒</span><p><b>Leak rule:</b> every feature known before the week starts. <code>shift(1)</code>, never <code>shift(-1)</code>.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">⚖️</span><p><b>Like with like:</b> same weeks, same horizon, same information. Beat the <b>best</b> baseline ({rate:.2f}).</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">↔️</span><p><b>Honest band:</b> width from past misses that include the hard weeks, then check the coverage.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:22px;font-size:30px">Next 👉 <b class="hl">Backtesting</b>: one split of 8 weeks… is that enough? 🎰</p>""",
          "Recap. Next time we stop trusting one split: walk-forward backtests over many folds and every starting week."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    F = facts()
    D = day_facts()
    bm = F["baseline_mae"]
    reg, one, rate = F["reg_mae"], F["onestep_naive_mae"], bm["rate_seasonal_naive"]
    bi, bw, bs, br = F["band_insample"], F["band_walkforward"], F["band_summer_only"], F["band_rate"]
    ex_mid, ex_lo, ex_hi = F["rate_interval_example"]
    co = F["coef"]
    labels = [dm(t) for t in D["test_f"].index]

    def band_chart(title, fc, half, caption, notes):
        return {"type": "chart", "title": title, "labels": labels,
                "series": [{"name": "actual", "values": [float(v) for v in D["act"]], "color": "0B1622"},
                           {"name": "forecast", "values": [round(float(v), 1) for v in fc], "color": "C77700"},
                           {"name": "lower", "values": [round(float(v - half), 1) for v in fc], "color": "16A394"},
                           {"name": "upper", "values": [round(float(v + half), 1) for v in fc], "color": "16A394"}],
                "ymin": 40, "ymax": 90, "fmt": "0", "caption": caption, "notes": notes}
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🌉", "kicker": "Week 5 · Day 3", "title": "Regression Forecasts\n+ Honest Ranges",
             "sub": "A forecast is a guess. An honest forecast says how wrong it might be, and checks it",
             "notes": "Regression forecast, a fair comparison, an honest range. Then Checkpoint 4."},
            {"type": "flow", "title": "Today's mission", "steps": [
                ["🔒", "Leak rule", "features known before the week"], ["📈", "Regression", "like-with-like scoring"],
                ["↔️", "Honest range", "a band you checked"], ["⚖️", "Checkpoint 4", "your honest test"]],
             "footer": "10 min hook · 30 min slides · 50 min hands-on · 20 min Checkpoint 4 · 10 min wrap-up", "notes": "Four moves."},
            {"type": "compare", "title": "Your friend is coming from the Island",
             "left": ["🚗", "Tobi: “I'm on my way”", "One number, no warning: a point forecast"],
             "right": ["🌉", "Amaka: “30 to 90 minutes, Third Mainland permitting”", "Most likely, a range, and what could blow it up: an interval forecast"],
             "notes": "If Amaka says 90%, she'd better be right 9 times in 10."},
            {"type": "bar", "title": "Last time: the bar any model must clear (MAE, 8 held-out weeks)",
             "labels": ["seasonal naive", "moving average", "exp. smoothing", "naive", "rate seasonal naive"],
             "values": [round(bm["seasonal_naive"], 2), round(bm["moving_average"], 2), round(bm["exp_smoothing"], 2), round(bm["naive"], 2), round(rate, 2)],
             "highlight": [4], "fmt": "0.00",
             "caption": f"{dm(F['holdout'][0])} – {dt(F['holdout'][1])}. The rate seasonal naive forecast all 8 weeks blind.", "notes": "Beat the best, not the weakest."},
            {"type": "section", "kicker": "Part 1", "title": "A forecast is a regression with one rule", "sub": "Every feature known before the week starts", "notes": "Section break."},
            {"type": "compare", "title": "The leak rule: known before the week starts",
             "left": ["✅", "shift(1): last week", f"On 3 Nov's row you see 27 Oct's {D['first_lag1']}. You knew it on Monday morning"],
             "right": ["📰", "shift(-1): next week", f"You see 10 Nov's {int(D['leak_weeks'].iloc[-1])}: reading tomorrow's newspaper"],
             "notes": "Quiz 4 questions 7 and 8."},
            {"type": "cards5", "title": "Five columns the model reads", "cards": [
                ["⏮️", "tickets_lag1", "last week: shift(1)"], ["📅", "tickets_lag52", "same week last year"],
                ["📡", "terminals", "network size this week"], ["🕰️", "sin52 + cos52", "week of year on a clock"],
                ["🎯", "target", "this week's tickets"]],
             "notes": "All knowable before the week starts."},
            {"type": "statement", "title": "Why sin and cos?", "icon": "🕰️", "big": "The year is a clock, not a ruler",
             "sub": "As a number, week 52 and week 1 are 51 apart; on a circle they are neighbours. Two columns instead of 52.",
             "notes": "Quiz 4 question 10. Keep one doubt: a circle is smooth, the rainy season is a switch."},
            {"type": "flow", "title": f"104 weeks → {F['feat_rows']} usable rows", "steps": [
                ["🗓️", "2024", f"{F['rows_lost']} weeks, only feed lag52"], ["🏋🏾", "Train", f"{F['train_f'][2]} rows · {dm(F['train_f'][0])} – {dt(F['train_f'][1])}"],
                ["📝", "Test", f"8 weeks · {dm(F['holdout'][0])} – {dt(F['holdout'][1])}"]],
             "footer": "shift(52) has nothing to copy in 2024, so dropna() removes those rows", "notes": "Quiz 4 question 9."},
            {"type": "table", "title": "Fit, then read the coefficients like an engineer", "header": ["Column", "Coefficient", "Makes sense?"],
             "rows": [["tickets_lag1", f"{co['tickets_lag1']:+.4f}", "half of last week carries over"],
                      ["tickets_lag52", f"{co['tickets_lag52']:+.4f}", "a bit of last year"],
                      ["terminals", f"{co['terminals']:+.4f}", f"+{D['per_1000']:.0f} tickets/week per 1,000 terminals ✅"],
                      ["sin52", f"{co['sin52']:+.4f}", "together: the yearly wave"], ["cos52", f"{co['cos52']:+.4f}", "together: the yearly wave"]],
             "colW": [3.2, 2.6, 6.53], "caption": "A negative terminals sign would be a warning: investigate before you trust anything.",
             "notes": "Quiz 4 question 12."},
            {"type": "section", "kicker": "Part 2", "title": "Like with like", "sub": "Same weeks, same horizon, same information", "notes": "Section break."},
            {"type": "stats", "title": "“Half of naive's error!”", "sub": "MAE on the 8 held-out weeks, tickets per week",
             "stats": [[f"{bm['naive']:.2f}", "naive, 8 weeks blind"], [f"{reg:.2f}", "regression"],
                       [f"{one:.2f}", "naive made the same way (last week's real count)"]],
             "notes": "The regression got last week's real count every week: it's a one-week-ahead forecast."},
            {"type": "table", "title": "Beat the BEST baseline, not the weakest", "header": ["Method", "How far ahead", "Information used", "MAE"],
             "rows": [["naive (W5D2)", "8 weeks, blind", "the last training week", f"{bm['naive']:.2f}"],
                      ["seasonal naive (W5D2)", "8 weeks, blind", "the same weeks last year", f"{bm['seasonal_naive']:.2f}"],
                      ["one-step naive", "1 week", "last week's real count", f"{one:.2f}"],
                      ["regression", "1 week", "last week's real count + 4 more columns", f"{reg:.2f}"],
                      ["rate seasonal naive (W5D2)", "8 weeks, blind", "last year's tickets per terminal × terminals", f"{rate:.2f}"]],
             "colW": [3.5, 2.2, 5.03, 1.6], "caption": f"Even with a hint every week, the regression ({reg:.2f}) loses to a forecast made 8 weeks blind ({rate:.2f}).",
             "notes": "Quiz 4 question 11."},
            {"type": "section", "kicker": "Part 3", "title": "Honest ranges", "sub": "Amaka's sentence, with a number on it, checked", "notes": "Section break."},
            band_chart(f"The code book's “90%” band: right {bi['covered']} times in 8", D["pred"], bi["half"],
                       f"forecast ± 1.645 × residual sd ({F['resid_sd']:.2f}) = ± {bi['half']:.2f}. {bi['covered']} of 8 weeks inside: {bi['covered'] / 8:.1%}, not 90%.",
                       "Quiz 4 questions 13–15. 1.645 is the two-sided 90% value."),
            {"type": "compare", "title": "Why so narrow? Two reasons",
             "left": ["🏠", "It marked its own homework", f"Training misses sd {F['resid_sd']:.2f}; unseen weeks sd {F['reg_err_sd']:.2f}, on average {abs(F['reg_err_mean']):.1f} too high"],
             "right": ["🌧️", "The season switched off", f"3 Nov: forecast {D['first_pred']:.1f}, reality {D['first_act']} ({D['first_err']:+.1f}). A smooth wave can't make a step"],
             "notes": "Quiz 4 question 16."},
            {"type": "steps", "title": "The honest recipe: misses made before it knew the answer", "icon": "🚶🏾", "steps": [
                f"Walk forward through the training weeks from {dm(bw['from'])}", "Fit on the weeks before, forecast the next week",
                f"Write down the miss: {bw['n_errors']} honest misses", "Band = forecast ± the 90th-percentile miss"],
             "notes": "A preview of Week 6 Day 1's backtesting."},
            {"type": "bar", "title": "The regression's honest past misses (actual − forecast)",
             "labels": [dm(t) for t in D["wf_err"].index], "values": [round(float(v), 1) for v in D["wf_err"].values], "fmt": "0",
             "highlight": [list(D["wf_err"].index).index(D["wf_big"])], "ymin": -16, "ymax": 16,
             "caption": f"The tallest: {dm(D['wf_big'])}, the rains arrive ({D['wf_err'].abs().max():.1f}). All misses: ± {bw['half']:.2f}. Summer only: ± {bs['half']:.2f}.",
             "notes": "Which weeks you measure on decides the width."},
            band_chart(f"Band from the honest misses: {bw['covered']} of 8 ✅", D["pred"], bw["half"],
                       f"Same forecast, ± {bw['half']:.2f}. The one miss is the season switch, 3 Nov.", "Only the width changed."),
            {"type": "stats", "title": "A band is only as honest as the weeks you measured it on", "sub": "Same recipe, different starting week",
             "stats": [[f"{bw['covered']}/8", f"misses from {dm(bw['from'])} (includes the April switch): ± {bw['half']:.2f}"],
                       [f"{bs['covered']}/8", f"misses from {dm(bs['from'])} (summer only): ± {bs['half']:.2f}"]],
             "notes": "Forecasting a season change? Measure on season changes."},
            band_chart(f"The best forecast gets a band too: {br['covered']} of 8", D["rate_fc"], br["half"],
                       f"Rate seasonal naive ± {br['half']:.2f}, from {br['n_errors']} misses of 8-week forecasts made at {br['n_origins']} earlier weeks.",
                       "Forecast 8 weeks ahead without peeking."),
            {"type": "compare", "title": "Don't turn the knob. Say it like Amaka.",
             "left": ["🎛️", "Raising z until the test looks right", "Tuning on the answers: expo again"],
             "right": ["🗣️", "The honest sentence", f"“Week of 3 Nov: most likely around {ex_mid:.0f}, plausibly {ex_lo:.0f} to {ex_hi:.0f}; expect bigger misses at season changes.”"],
             "notes": "Quiz 4 questions 17 and 18."},
            {"type": "table", "title": "Final project · Checkpoint 4: honest test", "header": ["Method", "How far ahead", "MAE", "90% band", "Coverage"],
             "rows": [["naive", "8 weeks, blind", f"{bm['naive']:.2f}", "—", "—"],
                      ["seasonal naive", "8 weeks, blind", f"{bm['seasonal_naive']:.2f}", "—", "—"],
                      ["rate seasonal naive", "8 weeks, blind", f"{rate:.2f}", f"± {br['half']:.2f}", f"{br['covered']} of 8"],
                      ["one-step naive", "1 week", f"{one:.2f}", "—", "—"],
                      ["regression · code-book band", "1 week", f"{reg:.2f}", f"± {bi['half']:.2f}", f"{bi['covered']} of 8"],
                      ["regression · honest band", "1 week", f"{reg:.2f}", f"± {bw['half']:.2f}", f"{bw['covered']} of 8"]],
             "colW": [4.2, 2.4, 1.6, 2.0, 2.13],
             "caption": "Bring a table like this: split by time + assert + embargo, your baseline on the same period with the same scorer. Real data stays on NIGCOMSAT systems.",
             "notes": "Next checkpoint: Week 6 Day 3, demo day."},
            {"type": "steps", "title": "Your turn: 50 minutes", "icon": "🌉", "steps": [
                "Open W5D3-exercise, save a copy, run STEP 0", "Part A: features without a leak + the split",
                "Part B: fit, read the signs, like with like", "Part C: three bands · Part D: your Checkpoint 4 table"],
             "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🔒", "Leak rule: every feature known before the week starts"],
                ["⚖️", f"Like with like; beat the best baseline ({rate:.2f})"],
                ["↔️", "Honest band: width from past misses that include the hard weeks, then check coverage"]],
             "next": "Next: Backtesting: is one split of 8 weeks enough?", "notes": "Recap."},
        ],
    }


# =============================================================================
# NOTEBOOK CHECKS (expected values filled in from the data at build time)
# =============================================================================
def _checks():
    F = facts()
    D = day_facts()
    bi, bw, bs, br = F["band_insample"], F["band_walkforward"], F["band_summer_only"], F["band_rate"]
    vals = {
        "LOST": str(F["rows_lost"]), "NTR": str(F["train_f"][2]),
        "REG": f"{F['reg_mae']!r}", "ONE": f"{F['onestep_naive_mae']!r}", "RATE2": f"{F['baseline_mae']['rate_seasonal_naive']:.2f}",
        "TCOEF": f"{F['coef']['terminals']!r}", "PER1000": f"{D['per_1000']:.0f}",
        "COV_IN": str(bi["covered"]), "HALF_IN": f"{bi['half']:.2f}",
        "HALF_WF": f"{bw['half']!r}", "COV_WF": str(bw["covered"]), "HALF_WF2": f"{bw['half']:.2f}",
        "HALF_S": f"{bs['half']!r}", "COV_S": str(bs["covered"]), "HALF_S2": f"{bs['half']:.2f}",
        "HALF_R": f"{br['half']!r}", "COV_R": str(br["covered"]), "HALF_R2": f"{br['half']:.2f}",
        "LOW": f"{F['rate_interval_example'][1]!r}", "HIGH": f"{F['rate_interval_example'][2]!r}",
        "MID0": f"{F['rate_interval_example'][0]:.0f}", "LOW0": f"{F['rate_interval_example'][1]:.0f}", "HIGH0": f"{F['rate_interval_example'][2]:.0f}",
        "ERRSD": f"{F['reg_err_sd']:.2f}", "RSD": f"{F['resid_sd']:.2f}",
    }
    code = r'''
def _near(x, want, tol):
    return abs(float(x) - want) <= tol

def _c_a1(x):
    v = int(x)
    hint = ("shift(-1) copies NEXT week's count back: tomorrow's newspaper. You need the past: a positive number."
            if v < 0 else "Last week is ONE week back.")
    return v == 1, "shift(1) puts LAST week's count on this week's row: 74 on 3 Nov. You knew it on Monday morning. 🔒", hint

def _c_a2(x):
    return int(x) == @@LOST@@, "@@LOST@@ rows: shift(52) has nothing to copy in the first year, so dropna() drops all of 2024.", \
        "Count the rows that disappeared: len(tickets) - len(feat)"

def _c_a3(x):
    return tuple(int(v) for v in x) == (@@NTR@@, 8), \
        "@@NTR@@ training weeks, 8 test weeks, and the assert passed: training ends before the test begins. ✂️", \
        "Hold out the last 8 weeks, like last time: H = 8"

def _c_b1(x):
    return _near(x, @@REG@@, 0.01), f"MAE {float(x):.2f}: half of naive's 11.25! 🎉 …hold the applause until B3.", \
        "The column the model learns to reproduce is called \"target\" (in quotes)."

def _c_b2(x):
    v = float(x)
    return _near(v, @@TCOEF@@, 1e-4) and v > 0, \
        "+@@PER1000@@ tickets a week per 1,000 extra terminals. Bigger network, more tickets: the sign makes sense ✅. A negative sign would be a warning.", \
        "Read it from the Series: coefs[\"terminals\"]"

def _c_b3(x):
    return _near(x, @@ONE@@, 0.01), f"{float(x):.2f}: naive with the same hint (last week's real count). The regression's real edge is under 1 ticket. ⚖️", \
        "One-step naive = last week's REAL count, which is the column \"tickets_lag1\"."

def _c_b4(x):
    return x is False, "Right: even with a hint every week, the regression loses to the rate seasonal naive (@@RATE2@@), forecast 8 weeks blind. 🏆👵🏾", \
        "Look at the table: which MAE is smallest? Answer True or False (no quotes)."

def _c_c1(x):
    z, cov = x
    return _near(z, 1.645, 0.0011) and int(cov) == @@COV_IN@@, \
        "± @@HALF_IN@@ covers only @@COV_IN@@ of 8 weeks. A “90%” band that's right @@COV_IN@@ times in 8: too narrow. 😬", \
        "The 90% two-sided normal number: 1.645"

def _c_c2(x):
    half, cov = x
    return _near(half, @@HALF_WF@@, 0.01) and int(cov) == @@COV_WF@@, \
        "± @@HALF_WF2@@ covers @@COV_WF@@ of 8: a band you can quote. Same forecast, only the width changed. ✅", \
        "90th percentile, written as a fraction: Q = 0.9"

def _c_c3(x):
    half, cov = x
    return _near(half, @@HALF_S@@, 0.01) and int(cov) == @@COV_S@@, \
        "Summer-only misses → ± @@HALF_S2@@ → @@COV_S@@ of 8. A band is only as honest as the weeks you measured it on. 🌧️", \
        "Type the date as text: \"2025-05-19\""

def _c_c4(x):
    half, cov = x
    return _near(half, @@HALF_R@@, 0.01) and int(cov) == @@COV_R@@, \
        "± @@HALF_R2@@ and @@COV_R@@ of 8 inside: the best forecast, with an honest band. 🏆", \
        "The first test week sits at position len(tickets) - H"

def _c_c5(x):
    return x is False, "False. Raising z until the test looks right is tuning on the answers: expo again. The width must come from misses BEFORE the test.", \
        "Is choosing z by looking at the test weeks honest? True or False (no quotes)."

def _c_d1(x):
    return "rate" in str(x).lower(), "The rate seasonal naive: lowest MAE, 8 weeks ahead without peeking, and an honest band that covered 8 of 8. Recommend the simpler model. ⚖️", \
        "Lowest MAE with an honest, checked band. Type its name in quotes."

def _c_bonus(x):
    lo, hi = x
    return _near(lo, @@LOW@@, 1.0) and _near(hi, @@HIGH@@, 1.0), \
        "“Week of 3 Nov: most likely around @@MID0@@, plausibly @@LOW0@@ to @@HIGH0@@; expect bigger misses at season changes.” That's Amaka. 🌉", \
        "rate_fc[0] - half_rate and rate_fc[0] + half_rate, as a pair (low, high)"

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4,
          "C1": _c_c1, "C2": _c_c2, "C3": _c_c3, "C4": _c_c4, "C5": _c_c5, "D1": _c_d1, "BONUS": _c_bonus}
HINTS = {"A1": "LAG is a whole number.", "A3": "H is a number of weeks.", "C2": "Q is a fraction between 0 and 1.",
         "C3": "SUMMER_START is a date in quotes, like \"2025-05-19\".", "C4": "ORIGIN is a whole number: len(tickets) - H",
         "BONUS": "Give a pair: (low, high)."}
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
    bw = F["band_walkforward"]
    return [
        ("md", """# 🌉 Week 5 · Day 3: Regression Forecasts + Honest Ranges

**Today:** you build the code book's regression forecast without leaking the future, score it like with like, and fence it with a 90% band that you **check**. Then you build your Checkpoint 4 table.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**

**Rule book:** keep `W5D3-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up
Run it once every time you open the notebook (and after every restart). Wait for `✅ Ready!`."""),
        ("setup", setup_code),
        ("md", """### ▶️ The data
Two years of weekly NOC tickets and the network size, the same file as last time."""),
        ("code", 'from sklearn.linear_model import LinearRegression\n\n'
                 'tickets = pd.read_csv(data_path("ops_tickets_weekly"), parse_dates=["week_start"], index_col="week_start").asfreq("W-MON")\n'
                 'print("weeks:", len(tickets), "· gaps:", int(tickets.isna().sum().sum()), "·", tickets.index[0].date(), "to", tickets.index[-1].date())\n'
                 'tickets.tail(3)'),
        ("md", """### ▶️ 🧰 Your toolbox (run it once)
The baselines from last time (`naive`, `seasonal_naive`, `rate_seasonal_naive`, `mae` …), the code book's feature builder `make_features`, and two helpers for honest past misses. Read them once, then run."""),
        ("code", BASELINE_CODE + "\n\n" + FEATURE_CODE + "\n\n"
                 'def coverage(forecast, half, actual):\n    """How many weeks fall inside forecast ± half."""\n'
                 '    actual = np.asarray(actual, float)\n    return int(((actual >= forecast - half) & (actual <= forecast + half)).sum())\n\n'
                 'print("✅ toolbox ready: naive, seasonal_naive, rate_seasonal_naive, mae, make_features, walk_forward_errors, rate_past_errors, coverage")'),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Features without a leak (12 min) 🔒

📖 **The leak rule:** every feature must be known **before the week starts**. On Monday morning you know last week's tickets, not this week's and certainly not next week's.

### A1 ✍️ Last week's count
`shift(LAG)` moves the column down by `LAG` rows. Which `LAG` puts **last week's** count on this week's row? Look at the table it prints around 3 November."""),
        _task('LAG = ___\n\nassert LAG is not None, "✍️ Fill in LAG first."\n'
              'peek = pd.DataFrame({"tickets": tickets["tickets_raised"], f"shift({LAG})": tickets["tickets_raised"].shift(LAG)})\n'
              'display(peek.loc["2025-10-20":"2025-11-17"])\ncheck("A1", LAG)',
              'LAG = 1\n\nassert LAG is not None, "✍️ Fill in LAG first."\n'
              'peek = pd.DataFrame({"tickets": tickets["tickets_raised"], f"shift({LAG})": tickets["tickets_raised"].shift(LAG)})\n'
              'display(peek.loc["2025-10-20":"2025-11-17"])\ncheck("A1", LAG)'),
        ("md", """### A2 ✍️ The feature table
▶️ `make_features` builds the code book's five columns plus the `target`. ✍️ How many rows did it lose? (Compare its length with `tickets`.)"""),
        _task('feat = make_features(tickets)\nprint("feature table:", feat.shape)\ndisplay(feat.head(3).round(3))\n\nrows_lost = ___\n\ncheck("A2", rows_lost)',
              'feat = make_features(tickets)\nprint("feature table:", feat.shape)\ndisplay(feat.head(3).round(3))\n\nrows_lost = len(tickets) - len(feat)\n\ncheck("A2", rows_lost)'),
        ("md", """### A3 ✍️ The split by time
Hold out the **last 8 weeks** (3 Nov – 22 Dec 2025), exactly as last time. Training = every row **before** them."""),
        _task('H = ___\n\nassert H is not None, "✍️ Fill in H first."\nCUT = feat.index[-H]\n'
              'train_f = feat.loc[:CUT].iloc[:-1]      # strictly before the test weeks\ntest_f = feat.loc[CUT:]\n'
              'assert train_f.index.max() < test_f.index.min(), "leakage: training overlaps the test"\n'
              'print("train:", len(train_f), "weeks,", train_f.index[0].date(), "to", train_f.index[-1].date())\n'
              'print("test: ", len(test_f), "weeks,", test_f.index[0].date(), "to", test_f.index[-1].date())\ncheck("A3", (len(train_f), len(test_f)))',
              'H = 8\n\nassert H is not None, "✍️ Fill in H first."\nCUT = feat.index[-H]\n'
              'train_f = feat.loc[:CUT].iloc[:-1]      # strictly before the test weeks\ntest_f = feat.loc[CUT:]\n'
              'assert train_f.index.max() < test_f.index.min(), "leakage: training overlaps the test"\n'
              'print("train:", len(train_f), "weeks,", train_f.index[0].date(), "to", train_f.index[-1].date())\n'
              'print("test: ", len(test_f), "weeks,", test_f.index[0].date(), "to", test_f.index[-1].date())\ncheck("A3", (len(train_f), len(test_f)))'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: The regression, scored like with like (15 min) 📈

### B1 ✍️ Fit and score
`LinearRegression` finds the weights that make *weight × column + weight × column + …* closest to the target on the training weeks. Which column is the target?"""),
        _task('assert "train_f" in globals(), "✍️ Finish A3 first."\nX_COLS = ["tickets_lag1", "tickets_lag52", "terminals", "sin52", "cos52"]\n\nTARGET = ___\n\n'
              'assert TARGET is not None, "✍️ Fill in TARGET first."\nreg = LinearRegression().fit(train_f[X_COLS], train_f[TARGET])\n'
              'pred = reg.predict(test_f[X_COLS])\nreg_mae = mae(pred, test_f["target"])\n'
              'print(f"regression MAE on the 8 held-out weeks: {reg_mae:.2f} tickets/week")\ncheck("B1", reg_mae)',
              'assert "train_f" in globals(), "✍️ Finish A3 first."\nX_COLS = ["tickets_lag1", "tickets_lag52", "terminals", "sin52", "cos52"]\n\nTARGET = "target"\n\n'
              'assert TARGET is not None, "✍️ Fill in TARGET first."\nreg = LinearRegression().fit(train_f[X_COLS], train_f[TARGET])\n'
              'pred = reg.predict(test_f[X_COLS])\nreg_mae = mae(pred, test_f["target"])\n'
              'print(f"regression MAE on the 8 held-out weeks: {reg_mae:.2f} tickets/week")\ncheck("B1", reg_mae)'),
        ("md", """### B2 ✍️ Read the signs like an engineer
A coefficient says how much the forecast moves for one more unit of that column. More terminals should mean more tickets. Pull out the `terminals` coefficient."""),
        _task('assert "reg" in globals(), "✍️ Finish B1 first."\ncoefs = pd.Series(reg.coef_, index=X_COLS)\nprint(coefs.round(4))\n\nterminals_coef = ___\n\ncheck("B2", terminals_coef)',
              'assert "reg" in globals(), "✍️ Finish B1 first."\ncoefs = pd.Series(reg.coef_, index=X_COLS)\nprint(coefs.round(4))\n\nterminals_coef = coefs["terminals"]\n\ncheck("B2", terminals_coef)'),
        ("md", """### B3 ✍️ Like with like
📖 The regression was handed **last week's real count** (`tickets_lag1`) for every test week: it's a **one-week-ahead** forecast. Last time's naive forecast all 8 weeks blind. Make naive the same way: "this week = last week's real count". Which column holds that?"""),
        _task('assert "test_f" in globals(), "✍️ Finish A3 first."\n\nNAIVE_COL = ___\n\nassert NAIVE_COL is not None, "✍️ Fill in NAIVE_COL first."\n'
              'onestep_naive_mae = mae(test_f[NAIVE_COL], test_f["target"])\nprint(f"one-step naive MAE: {onestep_naive_mae:.2f}")\ncheck("B3", onestep_naive_mae)',
              'assert "test_f" in globals(), "✍️ Finish A3 first."\n\nNAIVE_COL = "tickets_lag1"\n\nassert NAIVE_COL is not None, "✍️ Fill in NAIVE_COL first."\n'
              'onestep_naive_mae = mae(test_f[NAIVE_COL], test_f["target"])\nprint(f"one-step naive MAE: {onestep_naive_mae:.2f}")\ncheck("B3", onestep_naive_mae)'),
        ("md", "▶️ Every method on the same 8 weeks, with how far ahead it forecast and what it knew."),
        ("code", 'assert "onestep_naive_mae" in globals() and "reg_mae" in globals(), "✍️ Finish B1 and B3 first."\n'
                 'train_y = tickets["tickets_raised"].iloc[:-H]\ntrain_t = tickets["active_vsat_terminals"].iloc[:-H]\nactual = tickets["tickets_raised"].iloc[-H:]\n'
                 'like = pd.DataFrame([\n'
                 '    {"method": "naive (W5D2)", "how far ahead": "8 weeks, blind", "MAE": mae(naive(train_y, H), actual)},\n'
                 '    {"method": "seasonal naive (W5D2)", "how far ahead": "8 weeks, blind", "MAE": mae(seasonal_naive(train_y, H), actual)},\n'
                 '    {"method": "rate seasonal naive (W5D2)", "how far ahead": "8 weeks, blind", "MAE": mae(rate_seasonal_naive(train_y, train_t, H), actual)},\n'
                 '    {"method": "one-step naive", "how far ahead": "1 week", "MAE": onestep_naive_mae},\n'
                 '    {"method": "regression", "how far ahead": "1 week", "MAE": reg_mae},\n'
                 ']).set_index("method").round(2)\nlike'),
        ("md", """### B4 ✍️ Did the regression beat the best baseline?
Answer `True` or `False` (no quotes)."""),
        _task('regression_beats_best_baseline = ___\n\ncheck("B4", regression_beats_best_baseline)',
              'regression_beats_best_baseline = False\n\ncheck("B4", regression_beats_best_baseline)'),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Honest ranges (18 min) ↔️

### C1 ✍️ The code book's 90% band
Band = forecast ± **z** × (the spread of the training misses). For a two-sided 90% band on a bell curve, z = **1.645**. `coverage()` counts how many of the 8 real weeks land inside."""),
        _task('assert "pred" in globals(), "✍️ Finish B1 first."\nresid = train_f["target"] - reg.predict(train_f[X_COLS])\nresid_sd = resid.std()\n'
              'print(f"training residual sd: {resid_sd:.2f}")\n\nZ = ___\n\nassert Z is not None, "✍️ Fill in Z first."\n'
              'half_insample = Z * resid_sd\ncovered_insample = coverage(pred, half_insample, test_f["target"])\n'
              'print(f"band: forecast ± {half_insample:.2f} → covers {covered_insample} of {len(test_f)} held-out weeks")\ncheck("C1", (Z, covered_insample))',
              'assert "pred" in globals(), "✍️ Finish B1 first."\nresid = train_f["target"] - reg.predict(train_f[X_COLS])\nresid_sd = resid.std()\n'
              'print(f"training residual sd: {resid_sd:.2f}")\n\nZ = 1.645\n\nassert Z is not None, "✍️ Fill in Z first."\n'
              'half_insample = Z * resid_sd\ncovered_insample = coverage(pred, half_insample, test_f["target"])\n'
              'print(f"band: forecast ± {half_insample:.2f} → covers {covered_insample} of {len(test_f)} held-out weeks")\ncheck("C1", (Z, covered_insample))'),
        ("md", "▶️ Why so narrow? Look at the misses on the weeks it never saw, especially **3 November**, the week the rains end."),
        ("code", 'assert "pred" in globals(), "✍️ Finish B1 first."\nmisses = pd.DataFrame({"last week (lag1)": test_f["tickets_lag1"], "forecast": pred,\n'
                 '                       "actual": test_f["target"], "miss": test_f["target"] - pred}).round(1)\ndisplay(misses)\n'
                 'print(f"spread of the training misses: {resid_sd:.2f} · spread of the held-out misses: {misses[\'miss\'].std():.2f}")'),
        ("md", f"""### C2 ✍️ An honest band: misses made before it knew the answer
📖 `walk_forward_errors` walks through the training weeks from row 12 ({dm(bw["from"])}): fit on the weeks **before**, forecast the next week, write down the miss. Then: band = forecast ± the **90th-percentile** miss.
Write 90th percentile as a fraction for `Q`."""),
        _task('assert "pred" in globals(), "✍️ Finish B1 first."\npast_misses = walk_forward_errors(train_f, X_COLS, first=12)\n'
              'print(len(past_misses), "honest past misses, from", train_f.index[12].date())\n\nQ = ___\n\nassert Q is not None, "✍️ Fill in Q first."\n'
              'half_wf = np.quantile(np.abs(past_misses), Q)\ncovered_wf = coverage(pred, half_wf, test_f["target"])\n'
              'print(f"band: forecast ± {half_wf:.2f} → covers {covered_wf} of 8")\ncheck("C2", (half_wf, covered_wf))',
              'assert "pred" in globals(), "✍️ Finish B1 first."\npast_misses = walk_forward_errors(train_f, X_COLS, first=12)\n'
              'print(len(past_misses), "honest past misses, from", train_f.index[12].date())\n\nQ = 0.9\n\nassert Q is not None, "✍️ Fill in Q first."\n'
              'half_wf = np.quantile(np.abs(past_misses), Q)\ncovered_wf = coverage(pred, half_wf, test_f["target"])\n'
              'print(f"band: forecast ± {half_wf:.2f} → covers {covered_wf} of 8")\ncheck("C2", (half_wf, covered_wf))'),
        ("md", """### C3 ✍️ The trap: measure on calm weeks only
Same recipe, but start the misses on **19 May 2025**, after the April season switch (summer only). Type that date as text, like `"2025-01-01"`."""),
        _task('assert "half_wf" in globals(), "✍️ Finish C2 first."\n\nSUMMER_START = ___\n\nassert SUMMER_START is not None, "✍️ Fill in SUMMER_START first."\n'
              'first = int(train_f.index.searchsorted(pd.Timestamp(SUMMER_START)))\nsummer_misses = walk_forward_errors(train_f, X_COLS, first=first)\n'
              'half_summer = np.quantile(np.abs(summer_misses), 0.9)\ncovered_summer = coverage(pred, half_summer, test_f["target"])\n'
              'print(f"{len(summer_misses)} summer misses → band ± {half_summer:.2f} → covers {covered_summer} of 8")\ncheck("C3", (half_summer, covered_summer))',
              'assert "half_wf" in globals(), "✍️ Finish C2 first."\n\nSUMMER_START = "2025-05-19"\n\nassert SUMMER_START is not None, "✍️ Fill in SUMMER_START first."\n'
              'first = int(train_f.index.searchsorted(pd.Timestamp(SUMMER_START)))\nsummer_misses = walk_forward_errors(train_f, X_COLS, first=first)\n'
              'half_summer = np.quantile(np.abs(summer_misses), 0.9)\ncovered_summer = coverage(pred, half_summer, test_f["target"])\n'
              'print(f"{len(summer_misses)} summer misses → band ± {half_summer:.2f} → covers {covered_summer} of 8")\ncheck("C3", (half_summer, covered_summer))'),
        ("md", """### C4 ✍️ The best forecast gets an honest band too
The rate seasonal naive from last time forecasts all 8 weeks at once. `rate_past_errors` stands at every earlier week, makes the same 8-week forecast, and writes down its misses.
✍️ `ORIGIN` = the position (row number) of the first test week in `tickets`: the total number of weeks minus `H`."""),
        _task('assert "H" in globals(), "✍️ Finish A3 first."\n\nORIGIN = ___\n\nassert ORIGIN is not None, "✍️ Fill in ORIGIN first."\n'
              'rate_misses = rate_past_errors(tickets, ORIGIN, h=H)\nhalf_rate = np.quantile(np.abs(rate_misses), 0.9)\n'
              'rate_fc = rate_seasonal_naive(tickets["tickets_raised"].iloc[:ORIGIN], tickets["active_vsat_terminals"].iloc[:ORIGIN], H)\n'
              'covered_rate = coverage(rate_fc, half_rate, test_f["target"])\n'
              'print(f"{len(rate_misses) // H} past forecasts, {len(rate_misses)} misses → band ± {half_rate:.2f} → covers {covered_rate} of 8")\n'
              'check("C4", (half_rate, covered_rate))',
              'assert "H" in globals(), "✍️ Finish A3 first."\n\nORIGIN = len(tickets) - H\n\nassert ORIGIN is not None, "✍️ Fill in ORIGIN first."\n'
              'rate_misses = rate_past_errors(tickets, ORIGIN, h=H)\nhalf_rate = np.quantile(np.abs(rate_misses), 0.9)\n'
              'rate_fc = rate_seasonal_naive(tickets["tickets_raised"].iloc[:ORIGIN], tickets["active_vsat_terminals"].iloc[:ORIGIN], H)\n'
              'covered_rate = coverage(rate_fc, half_rate, test_f["target"])\n'
              'print(f"{len(rate_misses) // H} past forecasts, {len(rate_misses)} misses → band ± {half_rate:.2f} → covers {covered_rate} of 8")\n'
              'check("C4", (half_rate, covered_rate))'),
        ("md", """### C5 ✍️ True or False?
*"If the band covers too few test weeks, the honest fix is to raise z until the test coverage looks right."* Answer `True` or `False` (no quotes)."""),
        _task('raise_z_until_it_fits = ___\n\ncheck("C5", raise_z_until_it_fits)', 'raise_z_until_it_fits = False\n\ncheck("C5", raise_z_until_it_fits)'),

        # ---------------- PART D ----------------
        ("md", """---
# Part D: Your Checkpoint 4 table (5 min) ⚖️
▶️ This is the shape of table Checkpoint 4 asks for: every method on the **same weeks** with the **same scorer**, how far ahead it forecast, and a band whose coverage was **checked**."""),
        ("code", 'assert "covered_rate" in globals(), "✍️ Finish Part C first."\nhonest = pd.DataFrame([\n'
                 '    {"method": "naive", "how far ahead": "8 weeks, blind", "MAE": mae(naive(train_y, H), actual), "90% band": "—", "coverage (of 8)": "—"},\n'
                 '    {"method": "seasonal naive", "how far ahead": "8 weeks, blind", "MAE": mae(seasonal_naive(train_y, H), actual), "90% band": "—", "coverage (of 8)": "—"},\n'
                 '    {"method": "rate seasonal naive", "how far ahead": "8 weeks, blind", "MAE": mae(rate_fc, actual), "90% band": f"± {half_rate:.2f}", "coverage (of 8)": covered_rate},\n'
                 '    {"method": "one-step naive", "how far ahead": "1 week", "MAE": onestep_naive_mae, "90% band": "—", "coverage (of 8)": "—"},\n'
                 '    {"method": "regression · code-book band", "how far ahead": "1 week", "MAE": reg_mae, "90% band": f"± {half_insample:.2f}", "coverage (of 8)": covered_insample},\n'
                 '    {"method": "regression · honest band", "how far ahead": "1 week", "MAE": reg_mae, "90% band": f"± {half_wf:.2f}", "coverage (of 8)": covered_wf},\n'
                 ']).set_index("method").round(2)\nhonest'),
        ("md", """### D1 ✍️ Your recommendation
Which method do you recommend to the NOC planners? Lowest MAE, honest about how far ahead, and a band that held up. Type its name in quotes."""),
        _task('recommend = ___\n\ncheck("D1", recommend)', 'recommend = "rate seasonal naive"\n\ncheck("D1", recommend)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: say it like Amaka
Give the planners the range for the **week of 3 November** from the rate forecast and its honest band: a pair `(low, high)`."""),
        _task('assert "half_rate" in globals(), "✍️ Finish C4 first."\n\nband_week1 = ___\n\ncheck("BONUS", band_week1)\n'
              'print(f"Week of 3 Nov: most likely around {rate_fc[0]:.0f}, plausibly {band_week1[0]:.0f} to {band_week1[1]:.0f}; "\n'
              '      "expect bigger misses at season changes.")',
              'assert "half_rate" in globals(), "✍️ Finish C4 first."\n\nband_week1 = (rate_fc[0] - half_rate, rate_fc[0] + half_rate)\n\ncheck("BONUS", band_week1)\n'
              'print(f"Week of 3 Nov: most likely around {rate_fc[0]:.0f}, plausibly {band_week1[0]:.0f} to {band_week1[1]:.0f}; "\n'
              '      "expect bigger misses at season changes.")'),
        ("md", """---
## 🏁 Final project · Checkpoint 4: ⚖️ Honest test
Tick these off with your trainer today (on **your** data, on NIGCOMSAT systems, not in Colab):

- [ ] Split **by time**, with an `assert` that every training timestamp comes before every test timestamp
- [ ] An **embargo** at least as long as your longest feature window
- [ ] Your **simple baseline** scored on the **same period** with the **same scorer** as your method
- [ ] A comparison table like Part D: each method, **how far ahead** it forecast and **what it knew**
- [ ] Forecasting briefs: a **90% band** whose **coverage** you checked on held-out data · detection briefs: event-level precision and recall, rules written first · degradation briefs: the call from more than one starting point
- [ ] If the simple method wins or ties, you say so
- [ ] Raw data **not** on GitHub; nothing restricted pasted into an AI tool

Next checkpoint: **Week 6 · Day 3: 🎤 Demo day** (working tool, report, 5-minute demo)

## Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", f"""### 📝 What you learned today
- **The leak rule:** every feature known before the week starts. `shift(1)` looks back; `shift(-1)` reads tomorrow's newspaper.
- **The year is a clock:** `sin52` + `cos52` make week 52 a neighbour of week 1. But a smooth wave can't make the rainy season's on/off step.
- **Like with like:** the regression ({F['reg_mae']:.2f}) had last week's real count; made the same way, naive scores {F['onestep_naive_mae']:.2f}. And the best baseline, forecast 8 weeks blind, scored {F['baseline_mae']['rate_seasonal_naive']:.2f}.
- **Read the signs:** terminals {F['coef']['terminals']:+.4f} is positive, as it should be.
- **An honest band** takes its width from misses made before the answer was known, including the hard weeks, and then you **check its coverage**: {F['band_insample']['covered']} of 8 (code book) → {F['band_walkforward']['covered']} of 8 (honest) → {F['band_rate']['covered']} of 8 (rate forecast).
- **Never raise z until the test looks right.** That's expo.

**Next time:** *Backtesting*: is one split of 8 weeks enough? 🎰

<sub>Data: synthetic teaching dataset from the original Week 6 code book (`Time-series/week-06`). Safe to use with AI tools; real NIGCOMSAT data is not.</sub>"""),
    ]
