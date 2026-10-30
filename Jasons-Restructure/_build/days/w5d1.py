"""Week 5 · Day 1: No Expo! Honest Train/Test Splits + Quiz 3."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

import quizkit
import w5detector as W
from common import BRAND as B
from webdeck import logos_title_block
from w5detector import (DETECTOR_CODE, SCORER_CODE, TEST_START, TRAIN_END, chart_flags, event_table, facts,
                        forest_flags, lean_features, score_events)

CODE = "W5D1"
TITLE = "No Expo! Honest Train/Test Splits + Quiz 3"
QUIZ_SEED = 5103

GRID, AXIS = "#24384F", "#9DB0C6"
RED, GOLD, GREEN = "#FF6B6F", "#F5B83D", "#3CCB7F"
K1 = "Week 4 chart, raw channels, sunlit only (as taught)"
K2 = "Week 4 chart, raw channels, steady sun"
K3 = "Isolation forest, lean features, steady sun"
K4 = "Week 4 chart, lean features, steady sun"
SHORT = {K1: "Week 4 chart · raw · sunlit (as taught)", K2: "Week 4 chart · raw · steady sun",
         K3: "Isolation forest · lean features", K4: "Week 4 chart · lean features"}
BUDGETS = (0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.005)


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# =============================================================================
# EXTRA NUMBERS FOR TODAY (same shared functions, so same code as the notebook)
# =============================================================================
@lru_cache(maxsize=1)
def day_facts():
    F = facts()
    bus, labels = F["bus"], F["labels"]
    train, test, steady = F["train"], F["test"], F["steady"]
    X = lean_features(bus)
    D = {}
    # where the as-taught chart's test false alarms sit
    f1 = F["fight_flags"][K1]
    inside = pd.Series(False, index=bus.index)
    for _, ev in labels.iterrows():
        inside |= (bus.index >= ev["start"] - pd.Timedelta("1h")) & (bus.index <= ev["end"] + pd.Timedelta("1h"))
    fa1 = f1 & ~inside & test
    D["fa1_hours"] = fa1[fa1].index.hour.value_counts().sort_index().to_dict()
    D["fa1_months"] = fa1[fa1].index.month.value_counts().sort_index().to_dict()
    D["fa1_recharge"] = int((fa1 & F["recharge"]).sum())
    D["lucky_total"] = int(sum(F["lucky_hours"].values()))
    # the one test false alarm of the winner
    D["chart_fa_test"] = [t for t in F["chart_lean_fa_times"] if t >= pd.Timestamp(TEST_START)]
    # budgets for the forest: what the past says, what the test says
    rows = {}
    for c in BUDGETS:
        f = forest_flags(X, train & steady, steady, contamination=c)
        tr = score_events(f[train], labels)
        te = score_events(f[test], labels)
        trt = event_table(f[train], labels)
        rows[c] = {"train": tr, "test": te, "ev04": int(event_table(f[test], labels).loc["EV04", "hours_flagged"]),
                   "train_missed": [e for e, r in trt.iterrows() if not r["caught"]]}
    D["budgets"] = rows
    D["honest_c"] = min(c for c, r in rows.items() if r["train"]["caught"] == r["train"]["events"])
    perfect = [c for c, r in rows.items() if r["test"]["caught"] == r["test"]["events"] and r["test"]["false_alarms"] == 0]
    D["expo_c"] = max(perfect, key=lambda c: rows[c]["ev04"])
    D["fixed_c"] = W.CONTAMINATION
    chart_train = score_events(chart_flags(X, train & steady, steady)[train], labels)
    D["chart_train"] = chart_train
    D["expo_found"] = round(F["expo_temporal"][0] * F["expo_temporal"][1])
    D["lean_tpd_sd"] = F["tpd_sd"]
    return D


# =============================================================================
# LOCAL SVG HELPERS
# =============================================================================
def _x_of(idx, L, R):
    t0, t1 = idx[0], idx[-1]
    span = (t1 - t0).total_seconds()

    def X(t):
        return L + (pd.Timestamp(t) - t0).total_seconds() / span * (R - L)
    return X


def split_svg(F, w=1420, h=320):
    """The year as one bar: train | embargo | test, with the five events above it."""
    idx = F["bus"].index
    L, R = 20, w - 20
    X = _x_of(idx, L, R)
    ly, lh = 140, 70
    xt0, xt1, xe0, xe1 = X(idx[0]), X(TRAIN_END), X(TEST_START), X(idx[-1])
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">',
         f'<rect class="anim a-left" style="--d:.3s" x="{xt0:.1f}" y="{ly}" width="{xt1 - xt0:.1f}" height="{lh}" rx="16" fill="{B["blue_d"]}"/>',
         f'<text class="anim a-fade" style="--d:.6s" x="{(xt0 + xt1) / 2:.1f}" y="{ly + 45}" fill="#fff" font-size="28" font-weight="800" text-anchor="middle">'
         f'🏋🏾 TRAIN · Jan – Aug · {F["n_train"]:,} hours</text>',
         f'<rect class="anim a-right" style="--d:.9s" x="{xe0:.1f}" y="{ly}" width="{xe1 - xe0:.1f}" height="{lh}" rx="16" fill="{B["teal_d"]}"/>',
         f'<text class="anim a-fade" style="--d:1.2s" x="{(xe0 + xe1) / 2:.1f}" y="{ly + 45}" fill="#fff" font-size="26" font-weight="800" text-anchor="middle">'
         f'📝 TEST · {F["n_test"]:,} h</text>',
         f'<rect class="anim a-pop" style="--d:1.5s;transform-origin:{(xt1 + xe0) / 2:.0f}px {ly + lh / 2:.0f}px" x="{xt1 - 2:.1f}" y="{ly - 14}" '
         f'width="{max(xe0 - xt1, 6) + 4:.1f}" height="{lh + 28}" rx="4" fill="{GOLD}"/>',
         f'<text class="anim a-fade" style="--d:1.7s" x="{xt1 - 14:.1f}" y="{ly + lh + 44}" fill="{GOLD}" font-size="22" font-weight="800" text-anchor="end">'
         f'⛔ embargo: 1 Sep · {F["n_embargo"]} h</text>']
    for k, ev in enumerate(F["labels"].itertuples()):
        x0, x1 = X(ev.start), X(ev.end)
        d = 2.0 + k * .2
        if x1 - x0 > 12:
            o.append(f'<rect class="anim a-fade" style="--d:{d:.1f}s" x="{x0:.1f}" y="{ly - 54}" width="{x1 - x0:.1f}" height="22" rx="11" fill="{RED}"/>')
        else:
            o.append(f'<circle class="anim a-pop" style="--d:{d:.1f}s;transform-origin:{x0:.0f}px {ly - 43}px" cx="{x0:.1f}" cy="{ly - 43}" r="12" fill="{RED}"/>')
        o.append(f'<text class="anim a-fade" style="--d:{d + .1:.1f}s" x="{(x0 + x1) / 2:.1f}" y="{ly - 72}" fill="#FFC2C4" font-size="21" '
                 f'font-weight="800" text-anchor="middle">{ev.event_id}</text>')
    for m in range(1, 13):
        xm = X(f"2025-{m:02d}-15")
        o.append(f'<text x="{xm:.1f}" y="{h - 8}" fill="{AXIS}" font-size="19" text-anchor="middle">{pd.Timestamp(2025, m, 1):%b}</text>')
    o.append("</svg>")
    return "".join(o)


def strip_svg(w=1420, h=250):
    """Illustration (not data): a random split interleaves train and test hours; a time split doesn't."""
    n, cell, gap = 60, 19, 4.4
    rng = np.random.default_rng(11)
    rnd = rng.random(n) < 0.33
    x0 = 300
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">',
         f'<text x="0" y="62" fill="#EAF2FB" font-size="26" font-weight="800">🎲 Random split</text>',
         f'<text x="0" y="182" fill="#EAF2FB" font-size="26" font-weight="800">⏳ Split by time</text>']
    for i in range(n):
        x = x0 + i * (cell + gap)
        c1 = B["teal_d"] if rnd[i] else B["blue_d"]
        c2 = B["teal_d"] if i >= 42 else (GOLD if i == 41 else B["blue_d"])
        o.append(f'<rect class="anim a-pop" style="--d:{.2 + i * .012:.2f}s;transform-origin:{x + cell / 2:.0f}px 50px" x="{x:.1f}" y="40" width="{cell}" height="{cell * 1.6:.0f}" rx="4" fill="{c1}"/>')
        o.append(f'<rect class="anim a-pop" style="--d:{1.2 + i * .012:.2f}s;transform-origin:{x + cell / 2:.0f}px 170px" x="{x:.1f}" y="160" width="{cell}" height="{cell * 1.6:.0f}" rx="4" fill="{c2}"/>')
    # a fault stretch in the random strip: its hours sit on both sides
    fx0, fx1 = x0 + 20 * (cell + gap) - 6, x0 + 31 * (cell + gap) + 2
    o.append(f'<rect class="anim a-fade" style="--d:1.0s" x="{fx0:.1f}" y="30" width="{fx1 - fx0:.1f}" height="{cell * 1.6 + 20:.0f}" rx="8" fill="none" stroke="{RED}" stroke-width="3.5"/>')
    o.append(f'<text class="anim a-fade" style="--d:1.1s" x="{(fx0 + fx1) / 2:.1f}" y="22" fill="{RED}" font-size="19" font-weight="800" text-anchor="middle">one fault: its hours land on BOTH sides</text>')
    o.append(f'<text x="{x0}" y="{h - 8}" fill="{AXIS}" font-size="19">🟦 train hour  ·  🟩 test hour  ·  🟨 embargo</text>')
    o.append("</svg>")
    return "".join(o)


def embargo_svg(w=1420, h=230):
    """72 hours around the cut: Aug 31 (train), Sep 1 (embargo), Sep 2 (test), and a 24-hour window looking back."""
    cell, gap, x0 = 15.6, 3.4, 20
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    cols = [B["blue_d"]] * 24 + [GOLD] * 24 + [B["teal_d"]] * 24
    for i, c in enumerate(cols):
        x = x0 + i * (cell + gap)
        o.append(f'<rect class="anim a-pop" style="--d:{.1 + i * .01:.2f}s;transform-origin:{x + cell / 2:.0f}px 120px" x="{x:.1f}" y="100" width="{cell}" height="40" rx="3" fill="{c}"/>')
    for j, (lab, col) in enumerate((("31 Aug · last training day", B["blue_d"]), ("1 Sep · embargo", GOLD), ("2 Sep · first test day", B["teal_d"]))):
        xc = x0 + (j * 24 + 12) * (cell + gap)
        o.append(f'<text x="{xc:.1f}" y="172" fill="{col}" font-size="21" font-weight="800" text-anchor="middle">{lab}</text>')
    # the 24-hour window of the first test hour
    xa = x0 + 48 * (cell + gap) + cell / 2
    xb = x0 + 24 * (cell + gap)
    o.append(f'<path class="draw" style="--d:1.2s;--dur:1.2s" d="M{xa:.1f} 92 L{xa:.1f} 60 L{xb:.1f} 60 L{xb:.1f} 92" fill="none" stroke="#EAF2FB" stroke-width="3"/>')
    o.append(f'<text class="anim a-fade" style="--d:2s" x="{(xa + xb) / 2:.1f}" y="44" fill="#EAF2FB" font-size="21" font-weight="700" text-anchor="middle">'
             f'rolling(24) on 2 Sep 00:00 looks back 24 hours: it only reaches the embargo, never training</text>')
    o.append("</svg>")
    return "".join(o)


def barcode_svg(F, keys, w=1420):
    """Every alarm in the test months, one row per detector. Green tick = inside an event, red = false alarm."""
    bus, labels = F["bus"], F["labels"]
    test = F["test"].values
    tidx = bus.index[test]
    n = len(tidx)
    L, R, top, rh, rg = 480, w - 16, 26, 74, 20
    h = top + len(keys) * (rh + rg) + 44

    def X(i):
        return L + i / (n - 1) * (R - L)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for r in range(len(keys)):          # row backgrounds first, so the event bands show on top of them
        o.append(f'<rect x="{L}" y="{top + 10 + r * (rh + rg)}" width="{R - L}" height="{rh}" rx="8" fill="#0E1C2E"/>')
    inside = np.zeros(n, bool)
    for _, ev in labels.iterrows():
        if ev["end"] < tidx[0]:
            continue
        i0 = int(np.searchsorted(tidx, max(ev["start"], tidx[0])))
        i1 = int(np.searchsorted(tidx, ev["end"]))
        o.append(f'<rect x="{X(i0) - 2:.1f}" y="{top + 4}" width="{max(X(i1) - X(i0), 3) + 4:.1f}" height="{h - top - 40}" rx="6" fill="{GOLD}" fill-opacity=".2"/>')
        o.append(f'<text x="{(X(i0) + X(i1)) / 2:.1f}" y="{top - 2}" fill="{GOLD}" font-size="18" font-weight="800" text-anchor="middle">{ev["event_id"]}</text>')
        win = (tidx >= ev["start"] - pd.Timedelta("1h")) & (tidx <= ev["end"] + pd.Timedelta("1h"))
        inside |= win
    for r, k in enumerate(keys):
        y0 = top + 10 + r * (rh + rg)
        res = F["fight"][k]
        f = F["fight_flags"][k].values[test]
        good = np.where(f & inside)[0]
        bad = np.where(f & ~inside)[0]
        d = .3 + r * .35
        o.append(f'<g class="anim a-left" style="--d:{d:.2f}s">')
        o.append(f'<text x="0" y="{y0 + 30}" fill="#EAF2FB" font-size="21" font-weight="800">{r + 1}. {SHORT[k]}</text>')
        col = GREEN if res["false_alarms"] <= 1 and res["caught"] == res["events"] else (RED if res["caught"] < res["events"] else GOLD)
        o.append(f'<text x="0" y="{y0 + 60}" fill="{col}" font-size="20" font-weight="700">caught {res["caught"]}/{res["events"]} · '
                 f'{res["false_alarms"]} false alarm{"s" if res["false_alarms"] != 1 else ""}</text>')
        if len(good):
            o.append(f'<path d="{"".join(f"M{X(i):.1f} {y0 + 8}v{rh - 16}" for i in good)}" stroke="{GREEN}" stroke-width="1.6"/>')
        if len(bad):
            o.append(f'<path d="{"".join(f"M{X(i):.1f} {y0 + 4}v{rh - 8}" for i in bad)}" stroke="{RED}" stroke-width="3"/>')
        o.append("</g>")
    for m in (9, 10, 11, 12):
        i = int(np.searchsorted(tidx, pd.Timestamp(2025, m, 1)))
        o.append(f'<text x="{X(i) + 6:.1f}" y="{h - 8}" fill="{AXIS}" font-size="19">{pd.Timestamp(2025, m, 1):%b}</text>')
    o.append("</svg>")
    return "".join(o)


def clock_svg(hours, size=430):
    """A 24-hour ring: the hours when the as-taught chart flagged EV04 light up."""
    c, ro, ri = size / 2, size / 2 - 40, size / 2 - 108
    o = [f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}">']
    for k in range(24):
        a0 = (k / 24) * 2 * np.pi - np.pi / 2 + 0.02
        a1 = ((k + 1) / 24) * 2 * np.pi - np.pi / 2 - 0.02

        def P(r, a):
            return f"{c + r * np.cos(a):.1f} {c + r * np.sin(a):.1f}"
        d = f"M{P(ro, a0)} A{ro} {ro} 0 0 1 {P(ro, a1)} L{P(ri, a1)} A{ri} {ri} 0 0 0 {P(ri, a0)} Z"
        if k in hours:
            o.append(f'<path class="anim a-pop" style="--d:{1.0 + .25 * (k % 22):.2f}s;transform-origin:{c}px {c}px" d="{d}" fill="{GOLD}"/>')
        elif k == 21:
            o.append(f'<path d="{d}" fill="#53657C"/>')
        else:
            o.append(f'<path d="{d}" fill="#1C3150"/>')
        if k in (0, 6, 12, 18, 21):
            am = (k + .5) / 24 * 2 * np.pi - np.pi / 2
            lab = "21 🌘" if k == 21 else f"{k:02d}"
            o.append(f'<text x="{c + (ro + 22) * np.cos(am):.1f}" y="{c + (ro + 22) * np.sin(am) + 7:.1f}" fill="{AXIS}" font-size="19" '
                     f'font-weight="700" text-anchor="middle">{lab}</text>')
    o.append(f'<text x="{c}" y="{c - 6}" fill="{GOLD}" font-size="44" font-weight="800" text-anchor="middle">22 · 23 · 00</text>')
    o.append(f'<text x="{c}" y="{c + 30}" fill="{AXIS}" font-size="20" text-anchor="middle">the 3 hours after eclipse</text>')
    o.append("</svg>")
    return "".join(o)


def folds_svg(F, w=1420):
    """Rolling origin: the training block only grows forwards; each fold tests the next block."""
    idx = F["bus"].index
    L, R = 130, 900
    X = _x_of(idx, L, R)
    rh, top = 78, 64
    h = top + 4 * rh + 20
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">',
         f'<text x="{L}" y="30" fill="{AXIS}" font-size="20" font-weight="700">🟦 train (grows)  ·  🟩 test block</text>',
         f'<text x="1040" y="30" fill="#EAF2FB" font-size="22" font-weight="800" text-anchor="middle">📊 chart</text>',
         f'<text x="1260" y="30" fill="#EAF2FB" font-size="22" font-weight="800" text-anchor="middle">🌲 forest</text>',
         f'<text x="1150" y="56" fill="{AXIS}" font-size="18" text-anchor="middle">false alarms in the test block</text>']
    for k, fo in enumerate(F["folds"]):
        y = top + k * rh + 10
        d = .3 + k * .35
        a0, a1 = X(fo["train"][0]), X(fo["train"][1])
        b0, b1 = X(fo["test"][0]), X(fo["test"][1])
        c, f = fo["chart"], fo["forest"]
        cc = GREEN if c["false_alarms"] <= 1 else GOLD
        fc = GREEN if f["false_alarms"] <= 1 else (RED if f["false_alarms"] > 20 else GOLD)
        o.append(f'<g class="anim a-left" style="--d:{d:.2f}s">')
        o.append(f'<text x="0" y="{y + 34}" fill="#EAF2FB" font-size="23" font-weight="800">Fold {k + 1}</text>')
        o.append(f'<rect x="{L}" y="{y + 10}" width="{R - L}" height="36" rx="8" fill="#12233A"/>')
        o.append(f'<rect x="{a0:.1f}" y="{y + 10}" width="{a1 - a0:.1f}" height="36" rx="8" fill="{B["blue_d"]}"/>')
        o.append(f'<rect x="{b0:.1f}" y="{y + 10}" width="{b1 - b0:.1f}" height="36" rx="8" fill="{B["teal_d"]}"/>')
        o.append(f'<text x="{(b0 + b1) / 2:.1f}" y="{y + 35}" fill="#fff" font-size="17" font-weight="700" text-anchor="middle">'
                 f'{fo["test"][0]:%d %b} – {fo["test"][1]:%d %b}</text>')
        o.append(f'<text x="1040" y="{y + 40}" fill="{cc}" font-size="38" font-weight="800" text-anchor="middle">{c["false_alarms"]}</text>')
        o.append(f'<text x="1260" y="{y + 40}" fill="{fc}" font-size="38" font-weight="800" text-anchor="middle">{f["false_alarms"]}'
                 f'{" ✗" if f["caught"] < f["events"] else ""}</text>')
        o.append("</g>")
    o.append("</svg>")
    return "".join(o)


def hbars_svg(rows, total, w=1420):
    """rows: [(label, value, colour)] as horizontal bars out of `total`."""
    L, R, rh = 470, w - 120, 64
    h = len(rows) * rh + 10
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for k, (lab, v, col) in enumerate(rows):
        y = k * rh + 8
        bw = max(v / total * (R - L), 3)
        d = .3 + k * .25
        o.append(f'<g class="anim a-left" style="--d:{d:.2f}s"><text x="0" y="{y + 32}" fill="#EAF2FB" font-size="23" font-weight="700">{lab}</text>'
                 f'<rect x="{L}" y="{y + 6}" width="{R - L}" height="38" rx="8" fill="#12233A"/>'
                 f'<rect x="{L}" y="{y + 6}" width="{bw:.1f}" height="38" rx="8" fill="{col}"/>'
                 f'<text x="{L + bw + 14:.1f}" y="{y + 34}" fill="{col}" font-size="26" font-weight="800">{v}</text></g>')
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
    fight = F["fight"]
    r1, r2, r3, r4 = (fight[k] for k in (K1, K2, K3, K4))
    t1, t3, t4 = r1["table"], r3["table"], r4["table"]
    ev04h = F["ev04_hours"]
    share_r, n_r = F["expo_random"]
    share_t, n_t = F["expo_temporal"]
    seeds = F["forest_seed_fa"]
    bud = D["budgets"]
    hc, ec, fc = D["honest_c"], D["expo_c"], D["fixed_c"]
    fa_test = D["chart_fa_test"][0]
    folds = F["folds"]
    chart_fold_fa = [fo["chart"]["false_alarms"] for fo in folds]
    forest_fold_fa = [fo["forest"]["false_alarms"] for fo in folds]

    def pct(v):
        return "—" if v != v else f"{v:.2f}"

    board = ""
    for k, key in enumerate((K1, K2, K3, K4)):
        r = fight[key]
        lit = int(r["table"].loc["EV04", "hours_flagged"]) if "EV04" in r["table"].index else 0
        win = key == K4
        col = GREEN if win else (RED if r["caught"] < r["events"] else GOLD)
        note = " 🍀 lucky" if key == K1 else ""
        board += (f'<tr class="anim a-left{" win" if win else ""}" style="--d:{.3 + k * .2:.2f}s">'
                  f'<td><b>{k + 1}. {SHORT[key]}</b></td>'
                  f'<td class="mono" style="color:{col};font-weight:800">{r["caught"]}/{r["events"]}</td>'
                  f'<td class="mono" style="color:{col};font-weight:800">{r["false_alarms"]}</td>'
                  f'<td class="mono">{lit} / {ev04h}{note}</td><td class="mono" style="color:{col}">{pct(r["precision"])}</td></tr>')

    def brow(label, c, r, cls=""):
        te = r["test"]
        past = f'{r["train"]["caught"]}/{r["train"]["events"]}' + (f' (misses {", ".join(r["train_missed"])})' if r["train_missed"] else "")
        return (f'<tr class="anim a-left{cls}" style="--d:{label[0]}s"><td><b>{label[1]}</b><br><span class="small">contamination = {c:.2%}</span></td>'
                f'<td class="mono">{past}</td><td class="mono">{te["caught"]}/{te["events"]}</td><td class="mono">{te["false_alarms"]}</td>'
                f'<td class="mono">{r["ev04"]} / {ev04h}</td></tr>')
    tune_rows = (brow((.3, "🔒 Fixed before the test (Week 4 Day 2)"), fc, bud[fc])
                 + brow((.55, "🧑🏾‍🔧 Honest tune: past labels only"), hc, bud[hc])
                 + brow((.8, "🙈 Expo tune: picked by peeking at Sep–Dec"), ec, bud[ec])
                 + f'<tr class="anim a-left win" style="--d:1.05s"><td><b>📊 Week 4 chart, k = 3</b><br><span class="small">no tuning at all</span></td>'
                   f'<td class="mono">{D["chart_train"]["caught"]}/{D["chart_train"]["events"]}</td><td class="mono">{r4["caught"]}/{r4["events"]}</td>'
                   f'<td class="mono">{r4["false_alarms"]}</td><td class="mono">{int(t4.loc["EV04", "hours_flagged"])} / {ev04h}</td></tr>')

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:70px;top:150px;width:520px;height:560px">
  <svg viewBox="0 0 520 560" width="520" height="560">
    <rect x="60" y="30" width="380" height="490" rx="22" fill="#EAF2FB" class="anim a-pop" style="--d:.2s;transform-origin:250px 275px"/>
    <rect x="100" y="80" width="200" height="16" rx="8" fill="#9DB0C6"/><rect x="100" y="120" width="300" height="12" rx="6" fill="#C9D6E5"/>
    <rect x="100" y="150" width="280" height="12" rx="6" fill="#C9D6E5"/><rect x="100" y="180" width="300" height="12" rx="6" fill="#C9D6E5"/>
    <rect x="100" y="210" width="240" height="12" rx="6" fill="#C9D6E5"/><rect x="100" y="240" width="290" height="12" rx="6" fill="#C9D6E5"/>
    <text x="250" y="400" font-size="150" font-weight="800" fill="#F5B83D" text-anchor="middle" class="anim a-pop" style="--d:.6s;transform-origin:250px 350px">A1</text>
    <path class="draw" style="--d:1.2s;--dur:.8s" d="M120 440 L400 300" stroke="#E5484D" stroke-width="16" stroke-linecap="round"/>
    <g class="anim a-pop" style="--d:1.8s;transform-origin:250px 480px"><rect x="150" y="445" width="220" height="70" rx="12" fill="none" stroke="#E5484D" stroke-width="7" transform="rotate(-8 260 480)"/>
    <text x="260" y="497" font-size="48" font-weight="800" fill="#E5484D" text-anchor="middle" transform="rotate(-8 260 480)">EXPO</text></g>
  </svg></div>
<div style="max-width:900px;margin-top:40px">
  <div class="kicker anim">Week 5 · Day 1</div>
  <h1 class="anim" style="--d:.2s">No Expo!<br>Honest Splits<br><span class="hl">+ Quiz 3</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">If you saw the questions before the exam,<br>the A1 is fake. Today our detectors sit a real exam. 📝</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex">{logos_title_block()}</div>
</div>""",
          "Welcome to Week 5. For two days we built a forest and gave it features. Today it sits a real exam: months it has never seen, scored "
          "with the same rules as the Week 4 chart. Then Quiz 3."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Spot the expo. Then a fair fight.</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:290px;padding:40px 26px"><div class="icon">🕵🏾</div><h3>Spot the expo</h3><p class="small">why random splits lie</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:290px;padding:40px 26px"><div class="icon">✂️</div><h3>Split by time</h3><p class="small">train · embargo · test</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:290px;padding:40px 26px"><div class="icon">🥊</div><h3>Fair fight</h3><p class="small">forest vs Week 4 chart</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:250px;padding:40px 26px"><div class="icon">📝</div><h3>Quiz 3</h3><p class="small">the machine-learning days</p></div>
</div>
<div class="row anim" style="--d:1.8s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 45 min hands-on</span><span class="pill gold">📝 20 min quiz</span><span class="pill">🏁 15 min mark + wrap</span>
</div>""",
          "Four moves. The quiz sits after the hands-on so people have just used every idea it asks about."),

        # 3 ─ hook
        S("""
<div class="kicker anim">Quick question</div>
<h2 class="anim" style="--d:.1s">Who do you put in the control room? 🛰️</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🤩</div><h3>Tunde: A1 in every subject</h3>
    <p class="muted">The night before WAEC, Tunde's cousin brought <b style="color:#fff">“expo”</b>: the actual questions. Tunde memorised the answers.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill gold">perfect score</span><span class="pill bad">saw the questions</span></div></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">📚</div><h3>Chika: B2 in maths</h3>
    <p class="muted">Chika studied past questions, then sat an exam she had <b style="color:#fff">never seen</b>.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill teal">honest score</span><span class="pill">a bit lower</span></div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:36px;text-align:center">Tunde's A1 measured the expo, not Tunde.<br>A detector tested on hours it has already seen is <b class="hl">Tunde</b>. 🙅🏾</p>""",
          "Let the room laugh: everyone knows someone who bought expo. Then land it: an exam only measures you if you haven't seen the questions. "
          "Same for a model. Today's whole day is about building an exam the model hasn't seen."),

        # 4 ─ three kinds of expo
        S("""
<div class="kicker anim">Expo in time series comes in three flavours</div>
<h2 class="anim" style="--d:.1s">Three ways a score gets faked</h2>
<div class="grid3" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">👥</div><h3>Neighbours in training</h3>
    <p class="muted">Shuffle the hours: the test hour at 10:00 has 09:00 and 11:00 in training. Almost the same reading.</p></div>
  <div class="card anim a-pop" style="--d:.55s"><div class="icon">🔮</div><h3>Features that peek ahead</h3>
    <p class="muted"><code>shift(-1)</code> or <code>rolling(..., center=True)</code> use readings that don't exist yet.</p></div>
  <div class="card anim a-pop" style="--d:.8s"><div class="icon">🔑</div><h3>Settings tuned on the key</h3>
    <p class="muted">Picking the threshold or contamination by looking at the <b style="color:#fff">test</b> answers.</p></div>
</div>
<p class="anim" style="--d:1.2s;margin-top:30px;text-align:center">All three give a score that won't survive the <b class="hl">next real day</b> in the control room.</p>""",
          "Week 4 Day 3 already covered flavour 2: the 14:00 test. Today we demonstrate flavour 1 with a copycat model, and flavour 3 when we try to tune the forest."),

        # 5 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">Catch the expo 🕵🏾</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">One model, two ways of splitting the year.</p>""",
          "Section break.", cls="center"),

        # 6 ─ copycat
        S("""
<div class="kicker anim">A side experiment</div>
<h2 class="anim" style="--d:.1s">Meet the copycat 🐱</h2>
<div class="row" style="gap:40px;margin-top:10px">
  <div class="col" style="flex:1.15;gap:20px">
    <p class="anim" style="--d:.25s">For each new hour it finds the <b class="hl">one most similar hour</b> it has seen and copies that hour's answer: fault or normal.</p>
    <pre class="code anim" style="--d:.45s;font-size:23px">copycat = make_pipeline(StandardScaler(),
            KNeighborsClassifier(n_neighbors=1))
copycat.fit(X_train, y_train)   # y = 1 inside a fault
copycat.predict(X_test)</pre>
    <p class="small anim" style="--d:.7s">It learns from the answer key (<b>supervised</b>). Our forest never sees labels. The copycat is only here to expose expo.</p>
  </div>
  <div class="card anim a-pop" style="--d:.9s;flex:.85;text-align:center;padding:30px">
    <svg viewBox="0 0 520 330" width="100%">
      <circle cx="90" cy="90" r="22" fill="#3B8BE0"/><circle cx="160" cy="250" r="22" fill="#3B8BE0"/><circle cx="420" cy="70" r="22" fill="#3B8BE0"/>
      <circle cx="330" cy="250" r="22" fill="#FF6B6F"/><circle cx="440" cy="270" r="22" fill="#FF6B6F"/>
      <circle cx="270" cy="180" r="26" fill="#F5B83D"/><text x="270" y="191" font-size="30" font-weight="800" text-anchor="middle" fill="#0B1622">?</text>
      <path class="draw" style="--d:1.4s;--dur:.8s" d="M286 198 L316 234" stroke="#EAF2FB" stroke-width="4" stroke-dasharray="8 6"/>
      <text x="260" y="320" font-size="24" fill="#9DB0C6" text-anchor="middle">🔵 normal hour · 🔴 fault hour · 🟡 new hour</text>
    </svg>
    <p style="font-size:26px;margin-top:6px">Nearest neighbour is a fault → <b class="bad">“fault!”</b></p>
  </div>
</div>""",
          "k-nearest neighbours with k = 1. It's the laziest possible model: no rules, just 'who do you look like?'. Scaling matters here because it measures distance (the Quiz 3 scaling question). "
          "Make clear this is a supervised side experiment: the forest and the chart never see the labels."),

        # 7 ─ the result
        S(f"""
<div class="kicker anim">Same model · same features · same answer key</div>
<h2 class="anim" style="--d:.1s;font-size:56px">How many fault hours did the copycat find?</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;text-align:center;border-color:#F5B83D"><div class="icon">🎲</div><h3>Random split</h3>
    <div class="stat hl count" data-to="{share_r * 100:.0f}" data-d=".6" style="font-size:120px">0</div><div class="stat-label">% of {n_r} test fault hours · “A1” 🎉</div></div>
  <div class="card anim a-right" style="--d:.9s;text-align:center;border-color:#16A394"><div class="icon">⏳</div><h3>Split by time</h3>
    <div class="stat teal" style="font-size:120px">{share_t * 100:.1f}</div><div class="stat-label">% of {n_t} test fault hours ({D["expo_found"]} found)</div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:30px;text-align:center">By time, it only caught <b class="hl">{", ".join(F["expo_temporal_events"])}</b>: a repeat of EV02, which it saw in May.<br>The only difference between 100 and {share_t * 100:.1f} is <b class="bad">expo</b>.</p>""",
          f"Random split (train_test_split, a third held out, random_state = 42): {n_r} fault hours land in the test set and the copycat finds {share_r:.0%} of them. "
          f"Train on Jan–Aug and test on Sep–Dec: it finds {share_t:.1%} of {n_t}, only EV05. EV05 is a recurrence of EV02's charge-controller fault, so the copycat recognises it. "
          "EV04 is a new kind of fault it has never seen: zero. That's the honest truth about supervised models: they recognise repeats, not novelties."),

        # 8 ─ why random lies
        S(f"""
<div class="kicker anim">Why the random split lies</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The test hours have twins in training 👥</h2>
<div class="card anim" style="--d:.2s;padding:26px 28px">{strip_svg()}</div>
<p class="anim" style="--d:1.6s;margin-top:24px;text-align:center">EV04 lasts {ev04h} hours. Shuffle them and every test hour inside it has its neighbour in training.<br>
The copycat isn't detecting the fault, it's <b class="hl">copying the answer from the next seat</b>.</p>""",
          "This is quiz question 23: the test hours have near-identical neighbours in the training set. Hourly telemetry changes slowly, so 10:00 and 11:00 look almost the same. "
          "The picture is an illustration, not the real split."),

        # 9 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Split by time ✂️</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Train on the past. Test on the future. Leave a gap.</p>""",
          "Section break.", cls="center"),

        # 10 ─ the split
        S(f"""
<div class="kicker anim">The honest split for the whole week</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Past to train, future to test</h2>
<div class="card anim" style="--d:.2s;padding:22px 26px">{split_svg(F)}</div>
<pre class="code anim" style="--d:2.2s;font-size:23px;margin-top:20px">train = bus.index &lt;  "{TRAIN_END}"     <span class="c"># Jan – Aug: {F["n_train"]:,} hours, EV01–EV03</span>
test  = bus.index &gt;= "{TEST_START}"     <span class="c"># 2 Sep – 31 Dec: {F["n_test"]:,} hours, EV04 + EV05</span>
assert bus.index[train].max() &lt; bus.index[test].min()   <span class="c"># fails loudly if they ever overlap</span></pre>""",
          f"Training is every hour before 1 September ({F['n_train']} hours). The test starts on 2 September ({F['n_test']} hours). 1 September ({F['n_embargo']} hours) is in neither: the embargo. "
          "The assert line is quiz question 24. Three events are in the past, two in the future, and EV04 is a kind of fault the training months never contained."),

        # 11 ─ embargo
        S(f"""
<div class="kicker anim">Why skip 1 September?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The embargo: an empty seat between candidates 🪑</h2>
<div class="card anim" style="--d:.2s;padding:22px 26px">{embargo_svg()}</div>
<div class="grid2" style="margin-top:22px;gap:24px">
  <div class="card anim a-left" style="--d:1.4s;padding:20px 26px"><p style="font-size:25px">Without a gap, a 24-hour feature on the first test hour <b class="bad">reads training hours</b>. The test isn't separate any more.</p></div>
  <div class="card anim a-right glow" style="--d:1.7s;padding:20px 26px"><p style="font-size:25px"><b class="hl">Rule:</b> embargo ≥ your longest feature window. Our longest is 24 hours, so we skip one day.</p></div>
</div>""",
          "Quiz question 25. In Week 4 Day 3 the history features used 24-hour windows. The embargo costs us 24 hours out of 8,760: a cheap price for a result you can defend."),

        # 12 ─ rules of the fair fight
        S(f"""
<div class="kicker anim">Write the rules BEFORE the fight</div>
<h2 class="anim" style="--d:.1s">Four rules of a fair fight 🧑🏾‍⚖️</h2>
<div class="grid2" style="margin-top:14px;gap:24px">
  <div class="card anim a-pop" style="--d:.3s;padding:24px 30px"><div class="row" style="gap:18px;align-items:center"><span class="num">1</span><h3 style="margin:0">Same held-out months</h3></div>
    <p class="muted" style="margin-top:10px">Everyone is judged on 2 Sep – 31 Dec only.</p></div>
  <div class="card anim a-pop" style="--d:.5s;padding:24px 30px"><div class="row" style="gap:18px;align-items:center"><span class="num">2</span><h3 style="margin:0">Same hours</h3></div>
    <p class="muted" style="margin-top:10px">Steady sunlight: eclipse and recharge have their own normal.</p></div>
  <div class="card anim a-pop" style="--d:.7s;padding:24px 30px"><div class="row" style="gap:18px;align-items:center"><span class="num">3</span><h3 style="margin:0">Same scorer</h3></div>
    <p class="muted" style="margin-top:10px"><code>score_events</code>: one flag inside = caught, outside = false alarm.</p></div>
  <div class="card anim a-pop glow" style="--d:.9s;padding:24px 30px"><div class="row" style="gap:18px;align-items:center"><span class="num">4</span><h3 style="margin:0">Settings fixed first</h3></div>
    <p class="muted" style="margin-top:10px">Chart k = 3 (Week 3). Forest contamination = {fc:.1%} (Week 4 Day 2).</p></div>
</div>""",
          "Quiz question 28: same held-out period and same scorer for both. Rule 4 is the anti-expo rule: nobody touches a setting after seeing the test."),

        # 13 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">The fair fight 🥊</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Four contenders. Two events in the test months: EV04 and EV05.</p>""",
          "Section break.", cls="center"),

        # 14 ─ the lucky catch
        S(f"""
<div class="kicker anim">Contender 1 · the Week 4 chart exactly as taught (sunlit hours)</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Caught {r1["caught"]}/{r1["events"]}… but look <span class="hl">when</span> 🍀</h2>
<div class="row" style="gap:44px;align-items:center;margin-top:6px">
  <div class="card anim a-pop" style="--d:.3s;padding:16px;flex:none">{clock_svg(F["lucky_hours"])}</div>
  <div class="col" style="flex:1;gap:20px">
    <div class="card anim a-right" style="--d:.8s;padding:22px 28px"><p style="font-size:27px">It lit <b class="hl">{int(t1.loc["EV04", "hours_flagged"])} of {ev04h}</b> EV04 hours, and <b>every one</b> was 22:00, 23:00 or 00:00: the battery recharging after the 21:00 eclipse.</p></div>
    <div class="card anim a-right" style="--d:1.2s;padding:22px 28px;border-color:#E5484D"><p style="font-size:27px">Plus <b class="bad">{r1["false_alarms"]} false alarms</b>: {"all of them" if D["fa1_recharge"] == r1["false_alarms"] else str(D["fa1_recharge"]) + " of them"} recharge hours in the autumn eclipse season.</p></div>
    <p class="anim" style="--d:1.6s;font-size:28px">Right answer, wrong reason = a <b class="hl">lucky catch</b>. The amplifier fault had nothing to do with it.</p>
  </div>
</div>""",
          f"The chart from Week 3 Day 1 judges every sunlit hour, and the 3 recharge hours after each eclipse look odd (warm battery, high array current). EV04's four weeks overlap the September eclipse season, "
          f"so recharge hours inside EV04 count as a catch. The event table makes it visible: hours_flagged {int(t1.loc['EV04', 'hours_flagged'])} of {ev04h}, all at 22, 23 and 00. Always ask WHY a flag fired."),

        # 15 ─ the barcode
        S(f"""
<div class="kicker anim">Every alarm in the test months · 2 Sep – 31 Dec</div>
<h2 class="anim" style="--d:.1s;font-size:52px">Same months, same hours, four detectors</h2>
<div class="card anim" style="--d:.2s;padding:22px 24px">{barcode_svg(F, (K1, K2, K3, K4))}</div>
<p class="small anim" style="--d:2s;margin-top:14px;text-align:center">🟩 tick = a flag inside a real event · 🟥 tick = a false alarm · gold band = the event</p>""",
          f"Read row by row. Row 1: red ticks in September and October (recharge hours), plus the lucky catch. Row 2: the raw chart on steady hours is quiet ({r2['false_alarms']} false alarm) but EV04 is empty: it can't see the amplifier fault. "
          f"Row 3: the forest lights EV04 ({int(t3.loc['EV04', 'hours_flagged'])} hours) and EV05, with {r3['false_alarms']} red ticks scattered through Oct–Dec. "
          f"Row 4: the same chart on the lean features lights EV04 solidly ({int(t4.loc['EV04', 'hours_flagged'])} hours) with {r4['false_alarms']} red tick."),

        # 16 ─ scoreboard
        S(f"""{TABLE_CSS}
<div class="kicker anim">The report card · test months only</div>
<h2 class="anim" style="--d:.1s;font-size:52px;margin-bottom:12px">One scorer. Four contenders.</h2>
<table class="sb"><tr class="anim" style="--d:.1s"><th>Detector</th><th>Caught</th><th>False alarms</th><th>EV04 hours lit</th><th>Precision</th></tr>{board}</table>
<p class="anim" style="--d:1.3s;margin-top:20px;text-align:center">Lean features = the 4 health channels + <b class="hl">temp_per_drive</b> (Week 4 Day 3).</p>""",
          f"Precision = caught ÷ (caught + false alarms). The winner's single false alarm is {fa_test:%d %b %H:%M}, the hour after EV05 ended: the battery was still climbing back from the fault. "
          "Contenders 3 and 4 use identical features, hours, months and scorer. The only difference is the model."),

        # 17 ─ verdict
        S(f"""
<div class="kicker anim">The verdict</div>
<h1 class="anim" style="--d:.15s;font-size:84px">The feature won,<br>not the <span class="hl">forest</span> 🏆</h1>
<div class="grid3" style="margin-top:34px">
  <div class="card anim a-pop" style="--d:.5s;text-align:center"><div class="stat good">{r4["false_alarms"]}</div><div class="stat-label">false alarm (forest: {r3["false_alarms"]})</div></div>
  <div class="card anim a-pop" style="--d:.75s;text-align:center"><div class="stat good">{int(t4.loc["EV04", "hours_flagged"])}</div><div class="stat-label">EV04 hours lit (forest: {int(t3.loc["EV04", "hours_flagged"])})</div></div>
  <div class="card anim a-pop" style="--d:1s;text-align:center"><div class="stat hl">k = 3</div><div class="stat-label">the only setting, chosen in Week 3</div></div>
</div>
<p class="sub anim" style="--d:1.4s;margin-top:30px">We recommend the <b class="hl">simpler detector</b>. Saying “my fancy model lost” is a professional result, not a failure.</p>""",
          "Quiz question 30. What earned the win was temp_per_drive and the steady-sun context: engineering judgement. Once the features carry the physics, a 3-sigma chart on each feature is enough, "
          "and the duty engineer can read why it fired. Hold this line even if someone is disappointed: this is exactly what a good analyst reports."),

        # 18 ─ can't we tune it?
        S(f"""{TABLE_CSS}
<div class="kicker anim">“But you can tune the forest!”</div>
<h2 class="anim" style="--d:.1s;font-size:50px;margin-bottom:10px">Tune it honestly: still no win</h2>
<table class="sb"><tr class="anim" style="--d:.1s"><th>Forest budget</th><th>Past events (Jan–Aug)</th><th>Test caught</th><th>Test false alarms</th><th>EV04 hours lit</th></tr>{tune_rows}</table>
<p class="anim" style="--d:1.4s;margin-top:18px;text-align:center">The 0-false-alarm budget exists only if you <b class="bad">peek at the test</b>, and it misses {", ".join(bud[ec]["train_missed"])} in the past.<br>At its honest best the forest still trails a chart that needed no tuning.</p>""",
          f"Honest tuning uses the PAST labels only: the smallest budget that catches all 3 training events is {hc:.2%}. On the test it gives {bud[hc]['test']['false_alarms']} false alarms. "
          f"The budget that looks perfect on Sep–Dec ({ec:.2%}) is expo flavour 3: you only know it by looking at the test answers, and it misses {', '.join(bud[ec]['train_missed'])} in Jan–Aug. "
          "A tie goes to the simpler detector."),

        # 19 ─ seeds
        S(f"""
<div class="kicker anim">Is {r3["false_alarms"]} just bad luck?</div>
<h2 class="anim" style="--d:.1s">Five seeds, five forests 🌲🌲🌲🌲🌲</h2>
<div class="grid5" style="margin-top:30px">
  {"".join(f'<div class="card anim a-pop" style="--d:{.3 + i * .2:.1f}s;text-align:center;padding:26px 10px"><div class="small">random_state = {s}</div><div class="stat" style="font-size:84px;color:{GOLD}">{v}</div><div class="stat-label">false alarms</div></div>' for i, (s, v) in enumerate(seeds.items()))}
</div>
<p class="sub anim" style="--d:1.5s;margin-top:34px;text-align:center">From {min(seeds.values())} to {max(seeds.values())}. The chart has no dice to roll: <b class="good">{r4["false_alarms"]}</b>, every time.</p>""",
          "A forest is built from random cuts, so the seed changes the result. Always set random_state so your result can be repeated, and report the spread if you can. "
          "The verdict doesn't depend on a lucky seed."),

        # 20 ─ rolling origin
        S(f"""
<div class="kicker anim">One cut = one possibly lucky number</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Rolling origin: four exams, not one 🔁</h2>
<div class="card anim" style="--d:.2s;padding:22px 26px">{folds_svg(F)}</div>
<p class="anim" style="--d:1.8s;margin-top:20px;text-align:center">Chart: {", ".join(map(str, chart_fold_fa))} · forest: {", ".join(map(str, forest_fold_fa))} <span class="small">(✗ = missed the fold's event)</span>.
Training only ever grows <b class="hl">forwards</b>. You get a spread, not one score.</p>""",
          "Quiz questions 26 and 27. TimeSeriesSplit(n_splits=4, gap=24): each fold trains on everything before it and tests on the next block, with a 24-hour embargo. "
          f"Even the chart has a bad fold ({max(chart_fold_fa)} false alarms in fold 2, when it had only seen winter and spring and summer looked new). The forest ranges from {min(forest_fold_fa)} to {max(forest_fold_fa)} and misses EV03 in fold 2."),

        # 21 ─ clean reference
        S(f"""
<div class="kicker anim">Where does “normal” come from?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">A dirty reference period makes the fault normal 🧽</h2>
<div class="card anim" style="--d:.2s;padding:26px 28px">{hbars_svg([("📊 Chart · clean (Jan–Aug)", F["clean_chart_ev04"], GREEN), ("🌲 Forest · clean (Jan–Aug)", F["clean_forest_ev04"], B["teal_d"]), ("📊 Chart · dirty (whole year)", F["dirty_chart_ev04"], GOLD), ("🌲 Forest · dirty (whole year)", F["dirty_forest_ev04"], RED)], ev04h)}
  <p class="small" style="margin-top:6px">EV04 hours lit, out of {ev04h}</p></div>
<p class="anim" style="--d:1.6s;margin-top:22px;text-align:center">Fit on a year that <b>contains</b> EV04 and the forest learns the hot amplifier as normal.<br>In production there are no labels: ask operations for a period they <b class="hl">believe was quiet</b>, and write it in your report.</p>""",
          f"Quiz question 29. With EV04 inside the reference, the forest lights {F['dirty_forest_ev04']} of {ev04h} EV04 hours (clean: {F['clean_forest_ev04']}). The chart's limits widen too: {F['dirty_chart_ev04']} instead of {F['clean_chart_ev04']}. "
          "The reference period is a decision you must state, not a default."),

        # 22 ─ when the forest earns its place
        S("""
<div class="kicker anim">So is machine learning useless? No.</div>
<h2 class="anim" style="--d:.1s">When does the forest earn its place?</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s;border-color:#16A394"><div class="icon">🧑🏾‍🔧</div><h3>Chart country (today)</h3>
    <p class="muted">6 channels. Known physics. One engineer can write the right feature and read every alarm.</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#F5B83D"><div class="icon">🌲</div><h3>Forest country</h3>
    <p class="muted">Hundreds of channels. Relationships nobody has written down. Faults that nudge many channels a little at once.</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:30px;text-align:center">Either way the method is the same: <b class="hl">split by time, fix the settings, same scorer, honest verdict</b>.</p>""",
          "The honest answer for the room. The forest is a tool for when you can't hand-write the relationships. Here we could, so the simple tool wins. "
          "Quiz question 15 says the same thing about single-channel spikes."),

        # 23 ─ quiz
        S("""
<div class="kicker anim">Quiz 3 · the machine-learning days</div>
<h2 class="anim" style="--d:.1s">30 questions. 20 minutes. Just you. 📝</h2>
<div class="grid4" style="margin-top:30px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="icon">📵</div><h3>Phones down</h3><p class="small">notebooks closed, no AI</p></div>
  <div class="card anim a-pop" style="--d:.5s;text-align:center"><div class="icon">✏️</div><h3>One letter</h3><p class="small">circle A, B, C or D (or True/False)</p></div>
  <div class="card anim a-pop" style="--d:.7s;text-align:center"><div class="icon">🔀</div><h3>No “always B”</h3><p class="small">answers are spread across A–D</p></div>
  <div class="card anim a-pop" style="--d:.9s;text-align:center"><div class="icon">✅</div><h3>Mark together</h3><p class="small">swap papers and tick</p></div>
</div>
<p class="anim" style="--d:1.2s;margin-top:34px;text-align:center">Covers scikit-learn + forests + clustering (W4D2) · features (W4D3) · honest splits (today).</p>""",
          "Hand out 2-exercise/quiz/W5D1-quiz-3.pdf, or import the Google Forms CSV. Answer key: 4-instructor-only/W5D1-quiz-3-answer-key.pdf. "
          "Q4, Q8 and Q18 are corrected versions of the original questions: the notes say what changed."),

        # 24 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 45 minutes</div>
  <h2 class="anim" style="--d:.1s">Referee the fight 🥊</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open <b class="hl">W5D1-exercise</b>, save a copy, run STEP 0</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">A</span><p>Catch the copycat's expo</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">B</span><p>Build the split + embargo</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">C</span><p>Run the fair fight, pick a winner</p></div>
   <div class="row anim" style="--d:1.1s;gap:18px;align-items:center"><span class="num">D</span><p>Rolling origin + a dirty reference</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.3s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🥊</div>
  <h3 style="margin-top:16px">14 checks to pass</h3>
  <p class="muted">🌶️ Pepper task: tune the forest the honest way, using only the past</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Common snags: typing 'steady' in quotes (it's a variable), and forgetting to run the helper cell at the top."),

        # 25 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:16px;margin-top:6px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">🕵🏾</span><p><b>Expo is everywhere:</b> random splits, features that peek, settings tuned on the test.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">✂️</span><p><b>Split by time</b> with an embargo ≥ your longest window, and <code>assert</code> it.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center;padding:24px 34px"><span class="icon" style="margin:0">🏆</span><p><b>Fair fight, honest verdict:</b> if the simple model wins or ties, recommend it.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:22px;font-size:30px">Next 👉 <b class="hl">Forecasting baselines</b>: Grandma's “tomorrow will be like today”. 👵🏾<br>
<span class="small">Final project: bring your own split-by-time + baseline table to Checkpoint 4 (Week 5 · Day 3).</span></p>""",
          "Recap. Tell them the exact recipe from today is what Checkpoint 4 asks for: a temporal split and a baseline comparison table, same scorer."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    F = facts()
    D = day_facts()
    fight = F["fight"]
    r1, r2, r3, r4 = (fight[k] for k in (K1, K2, K3, K4))
    ev04h = F["ev04_hours"]
    share_r, n_r = F["expo_random"]
    share_t, n_t = F["expo_temporal"]
    bud = D["budgets"]
    hc, ec, fc = D["honest_c"], D["expo_c"], D["fixed_c"]

    def lit(r):
        return int(r["table"].loc["EV04", "hours_flagged"]) if "EV04" in r["table"].index else 0

    def p(v):
        return "—" if v != v else f"{v:.2f}"
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "📝", "kicker": "Week 5 · Day 1", "title": "No Expo!\nHonest Splits + Quiz 3",
             "sub": "If you saw the questions before the exam, the A1 is fake. Today our detectors sit a real exam",
             "notes": "Today the forest sits an exam on months it has never seen. Then Quiz 3."},
            {"type": "flow", "title": "Today's mission", "steps": [
                ["🕵🏾", "Spot the expo", "why random splits lie"], ["✂️", "Split by time", "train · embargo · test"],
                ["🥊", "Fair fight", "forest vs Week 4 chart"], ["📝", "Quiz 3", "the machine-learning days"]],
             "footer": "10 min hook · 30 min slides · 45 min hands-on · 20 min quiz · 15 min mark + wrap", "notes": "Four moves."},
            {"type": "compare", "title": "Who do you put in the control room?",
             "left": ["🤩", "Tunde: A1 everywhere", "He bought expo the night before and memorised the answers"],
             "right": ["📚", "Chika: B2 in maths", "She studied, then sat an exam she had never seen"],
             "notes": "Tunde's A1 measured the expo, not Tunde."},
            {"type": "cards", "title": "Three ways a score gets faked", "cards": [
                ["👥", "Neighbours in training", "random split: 10:00 in test, 09:00 and 11:00 in training"],
                ["🔮", "Features that peek ahead", "shift(-1), rolling(center=True)"],
                ["🔑", "Settings tuned on the key", "threshold picked by looking at the test answers"]],
             "notes": "Flavour 2 was Week 4 Day 3's 14:00 test."},
            {"type": "section", "kicker": "Part 1", "title": "Catch the expo", "sub": "One model, two ways of splitting the year", "notes": "Section break."},
            {"type": "code", "title": "Meet the copycat: copy the most similar hour's answer",
             "code": "copycat = make_pipeline(StandardScaler(),\n            KNeighborsClassifier(n_neighbors=1))\ncopycat.fit(X_train, y_train)   # y = 1 inside a fault\ncopycat.predict(X_test)",
             "caption": "Supervised (it learns from the answer key). A side experiment: our forest never sees labels.",
             "notes": "k-nearest neighbours, k = 1."},
            {"type": "stats", "title": "How many fault hours did the copycat find?", "sub": "Same model, same features, same answer key",
             "stats": [[f"{share_r:.0%}", f"random split ({n_r} test fault hours)"], [f"{share_t:.1%}", f"split by time ({n_t} test fault hours)"],
                       [", ".join(F["expo_temporal_events"]), "the only event found by time: a repeat of EV02"]],
             "notes": "The only difference between the two numbers is expo."},
            {"type": "statement", "title": "Why the random split lies", "icon": "👥",
             "big": "The test hours have twins in training",
             "sub": f"EV04 lasts {ev04h} hours. Shuffle them and every test hour inside it has its neighbour in training. The copycat copies the answer from the next seat.",
             "notes": "Quiz question 23."},
            {"type": "section", "kicker": "Part 2", "title": "Split by time", "sub": "Train on the past, test on the future, leave a gap", "notes": "Section break."},
            {"type": "flow", "title": "The honest split for the whole week", "steps": [
                ["🏋🏾", "Train", f"Jan – Aug · {F['n_train']:,} h · EV01–EV03"], ["⛔", "Embargo", f"1 Sep · {F['n_embargo']} h"],
                ["📝", "Test", f"2 Sep – 31 Dec · {F['n_test']:,} h · EV04, EV05"]],
             "footer": "assert bus.index[train].max() < bus.index[test].min()", "notes": "Quiz question 24."},
            {"type": "statement", "title": "Why skip 1 September?", "icon": "🪑",
             "big": "Embargo ≥ your longest feature window",
             "sub": "A 24-hour feature on the first test hour would otherwise read training hours. Our longest window is 24 hours, so we skip one day.",
             "notes": "Quiz question 25."},
            {"type": "cards4", "title": "Four rules of a fair fight", "cards": [
                ["📅", "Same months", "2 Sep – 31 Dec only"], ["🌞", "Same hours", "steady sunlight"],
                ["🎯", "Same scorer", "score_events"], ["🔒", "Settings fixed first", f"k = 3 · contamination {fc:.1%}"]],
             "notes": "Quiz question 28."},
            {"type": "section", "kicker": "Part 3", "title": "The fair fight", "sub": "Four contenders, two events: EV04 and EV05", "notes": "Section break."},
            {"type": "statement", "title": "Contender 1: the Week 4 chart as taught", "icon": "🍀",
             "big": f"Caught {r1['caught']}/{r1['events']}, but only through recharge hours",
             "sub": f"It lit {lit(r1)} of {ev04h} EV04 hours, all at 22:00, 23:00 or 00:00 (right after the 21:00 eclipse), plus {r1['false_alarms']} false alarms. A lucky catch.",
             "notes": "Always ask why a flag fired."},
            {"type": "table", "title": "The report card: test months only", "header": ["Detector", "Caught", "False alarms", "EV04 hours lit", "Precision"],
             "rows": [[f"{k + 1}. {SHORT[key]}", f"{r['caught']}/{r['events']}", r["false_alarms"], f"{lit(r)} / {ev04h}", p(r["precision"])]
                      for k, (key, r) in enumerate(((K1, r1), (K2, r2), (K3, r3), (K4, r4)))],
             "colW": [5.0, 1.4, 1.9, 2.1, 1.73], "caption": "Lean features = 4 health channels + temp_per_drive. Rows 3 and 4 differ only in the model.",
             "notes": "Contender 1's EV04 catch is lucky."},
            {"type": "bar", "title": "False alarms in the test months",
             "labels": ["1. chart, raw, sunlit", "2. chart, raw, steady", "3. forest, lean", "4. chart, lean"],
             "values": [r1["false_alarms"], r2["false_alarms"], r3["false_alarms"], r4["false_alarms"]], "highlight": [3], "fmt": "0",
             "caption": f"Contender 2 misses EV04 entirely. Contender 4 catches both events and lights {lit(r4)} EV04 hours.",
             "notes": "Fewer is better, as long as both events are caught."},
            {"type": "statement", "title": "The verdict", "icon": "🏆", "big": "The feature won, not the forest",
             "sub": f"Same catches, {r4['false_alarms']} false alarm instead of {r3['false_alarms']}, {lit(r4)} EV04 hours instead of {lit(r3)}. We recommend the simpler detector.",
             "notes": "Quiz question 30."},
            {"type": "table", "title": "Tune the forest honestly: still no win", "header": ["Forest budget", "Past events", "Test caught", "Test false alarms", "EV04 hours lit"],
             "rows": [[f"Fixed first ({fc:.2%})", f"{bud[fc]['train']['caught']}/3", f"{bud[fc]['test']['caught']}/2", bud[fc]["test"]["false_alarms"], bud[fc]["ev04"]],
                      [f"Honest tune, past labels ({hc:.2%})", f"{bud[hc]['train']['caught']}/3", f"{bud[hc]['test']['caught']}/2", bud[hc]["test"]["false_alarms"], bud[hc]["ev04"]],
                      [f"Expo tune, peeked at test ({ec:.2%})", f"{bud[ec]['train']['caught']}/3", f"{bud[ec]['test']['caught']}/2", bud[ec]["test"]["false_alarms"], bud[ec]["ev04"]],
                      ["Week 4 chart, k = 3", f"{D['chart_train']['caught']}/3", f"{r4['caught']}/2", r4["false_alarms"], lit(r4)]],
             "colW": [4.6, 1.8, 1.8, 2.1, 1.83], "caption": f"The 0-false-alarm budget only exists if you peek, and it misses {', '.join(bud[ec]['train_missed'])} in the past.",
             "notes": "A tie goes to the simpler detector."},
            {"type": "bar", "title": "Five seeds, five forests: false alarms in the test months",
             "labels": [f"seed {s}" for s in F["forest_seed_fa"]], "values": list(F["forest_seed_fa"].values()), "fmt": "0",
             "caption": f"The chart has no dice to roll: {r4['false_alarms']} false alarm, every time.", "notes": "Always set random_state."},
            {"type": "table", "title": "Rolling origin: four exams, not one", "header": ["Fold", "Trains up to", "Tests on", "Chart false alarms", "Forest false alarms"],
             "rows": [[k + 1, f"{fo['train'][1]:%d %b}", f"{fo['test'][0]:%d %b} – {fo['test'][1]:%d %b}", fo["chart"]["false_alarms"],
                       f"{fo['forest']['false_alarms']}" + (" (missed the event)" if fo["forest"]["caught"] < fo["forest"]["events"] else "")]
                      for k, fo in enumerate(F["folds"])],
             "colW": [1.0, 2.2, 3.2, 2.6, 3.13], "caption": "TimeSeriesSplit(n_splits=4, gap=24): training only grows forwards; you get a spread, not one score.",
             "notes": "Quiz questions 26 and 27."},
            {"type": "bar", "title": "A dirty reference makes the fault normal",
             "labels": ["chart · clean", "forest · clean", "chart · dirty", "forest · dirty"],
             "values": [F["clean_chart_ev04"], F["clean_forest_ev04"], F["dirty_chart_ev04"], F["dirty_forest_ev04"]], "highlight": [3], "fmt": "0",
             "caption": f"EV04 hours lit, of {ev04h}. Clean = fitted on Jan–Aug; dirty = the whole year, EV04 included. Ask operations for a quiet period.",
             "notes": "Quiz question 29."},
            {"type": "compare", "title": "When does the forest earn its place?",
             "left": ["🧑🏾‍🔧", "Chart country (today)", "6 channels, known physics, one engineer can write the feature"],
             "right": ["🌲", "Forest country", "Hundreds of channels, unwritten relationships, faults that nudge many channels at once"],
             "notes": "Same method either way: split by time, fixed settings, same scorer."},
            {"type": "steps", "title": "Quiz 3: 30 questions, 20 minutes", "icon": "📝", "steps": [
                "Phones down, notebooks closed, no AI", "Circle one letter per question", "Answers are spread across A–D: no “always B”",
                "Swap papers and mark together"], "notes": "Use the PDF or the Google Forms CSV."},
            {"type": "steps", "title": "Your turn: 45 minutes", "icon": "🥊", "steps": [
                "Open W5D1-exercise, save a copy, run STEP 0", "Part A: catch the copycat's expo", "Part B: the split + embargo",
                "Part C: the fair fight · Part D: rolling origin"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🕵🏾", "Expo: random splits, peeking features, settings tuned on the test"],
                ["✂️", "Split by time, embargo ≥ longest window, assert it"],
                ["🏆", "Fair fight, honest verdict: recommend the simpler model if it wins or ties"]],
             "next": "Next: Forecasting baselines · Project Checkpoint 4 at Week 5 Day 3", "notes": "Recap."},
        ],
    }


# =============================================================================
# NOTEBOOK CHECKS (expected values filled in from the data at build time)
# =============================================================================
def _checks():
    F = facts()
    D = day_facts()
    fight = F["fight"]
    r1, r2, r3, r4 = (fight[k] for k in (K1, K2, K3, K4))
    vals = {
        "SHARE_R": f"{F['expo_random'][0]!r}", "SHARE_T": f"{F['expo_temporal'][0]!r}",
        "EXPO_EVENT": repr(F["expo_temporal_events"][0]),
        "N_TRAIN": str(F["n_train"]), "N_TEST": str(F["n_test"]), "EMB": str(F["n_embargo"]),
        "R1_FA": str(r1["false_alarms"]), "R2_FA": str(r2["false_alarms"]), "R3_FA": str(r3["false_alarms"]), "R4_FA": str(r4["false_alarms"]),
        "R2_C": str(r2["caught"]), "LUCKY": str(D["lucky_total"]), "EV04H": str(F["ev04_hours"]),
        "FOLDS": repr([fo["chart"]["false_alarms"] for fo in F["folds"]]),
        "DIRTY": str(F["dirty_chart_ev04"]), "CLEAN": str(F["clean_chart_ev04"]),
        "HONEST": repr(D["honest_c"]), "HONEST_FA": str(D["budgets"][D["honest_c"]]["test"]["false_alarms"]),
        "FIXED": repr(D["fixed_c"]),
    }
    code = r'''
def _near(x, want, tol):
    return abs(float(x) - want) <= tol

def _res(x, caught, fa):
    return isinstance(x, dict) and x.get("caught") == caught and x.get("false_alarms") == fa

def _c_a1(x):
    v = float(x)
    v = v / 100 if v > 1 else v
    return _near(v, @@SHARE_R@@, 0.001), \
        "100% of the fault hours found! An A1. Hold your applause: look at how the hours were split. 🤨", \
        "Share of the fault hours the copycat called a fault: pred[y_te == 1].mean()"

def _c_a2(x):
    v = float(x)
    v = v / 100 if v > 1 else v
    return _near(v, @@SHARE_T@@, 0.003), \
        f"{v:.1%}. Same model, same features: the A1 was expo. 😬", \
        "Train on Jan to Aug: CUT is the first day of September, written \"2025-09-01\"."

def _c_a3(x):
    return str(x).strip().upper() == @@EXPO_EVENT@@, \
        "EV05, a repeat of EV02 (May) that the copycat saw in training. It recognises repeats, not new kinds of fault like EV04.", \
        "Look at the table above: which row says caught = True?"

def _c_b1(x):
    return tuple(int(v) for v in x) == (@@N_TRAIN@@, @@N_TEST@@), \
        "@@N_TRAIN@@ training hours, @@N_TEST@@ test hours, and 1 September left out. The assert passed: no overlap. ✂️", \
        "TRAIN_END = \"2025-09-01\" (hours BEFORE it) and TEST_START = \"2025-09-02\" (hours FROM it)."

def _c_b2(x):
    return int(x) == @@EMB@@, "24 hours: the embargo must be at least as long as the longest feature window. One day it is. 🪑", \
        "rolling(24) looks back 24 hours, so the gap must be at least that many hours."

def _c_c1(x):
    return _res(x, 2, @@R1_FA@@), "Caught both events… with @@R1_FA@@ false alarms. Now look at WHEN it flagged EV04 (next cell). 👀", \
        "K is the classic number of standard deviations: 3."

def _c_c2(x):
    return str(x).strip().lower() == "lucky", \
        "Lucky! All @@LUCKY@@ EV04 flags were 22:00, 23:00 or 00:00: battery recharge after the eclipse, not the amplifier. 🍀", \
        "Every EV04 flag sits in the 3 hours after the 21:00 eclipse. Did the amplifier cause that?"

def _c_c3(x):
    return _res(x, @@R2_C@@, @@R2_FA@@), "Quiet: @@R2_FA@@ false alarm. But it caught only EV05: raw channels can't see the amplifier running hot for its drive.", \
        "Use the variable steady (no quotes): CONTEXT = steady"

def _c_c4(x):
    ok = isinstance(x, dict) and x.get("caught") == 2 and 5 <= x.get("false_alarms", -1) <= 70
    fa = x.get("false_alarms") if isinstance(x, dict) else "?"
    return ok, f"Both events caught, with {fa} false alarms. The features gave it eyes; the forest added noise. 🌲", \
        "The false-alarm budget fixed in Week 4 Day 2: 0.5%, written 0.005."

def _c_c5(x):
    return _res(x, 2, @@R4_FA@@), "Both events, ONE false alarm (the hour after EV05, battery still recovering). Same features as the forest. 🏆", \
        "K is the classic number of standard deviations: 3."

def _c_c6(x):
    return int(x) == 4, "Number 4: the chart on the lean features. The feature won, not the forest. Recommend the simpler detector. ✅", \
        "Pick the one that catches BOTH events with the fewest false alarms, for the right reason."

def _c_d1(x):
    return int(x[0]) == 24 and list(x[1]) == @@FOLDS@@, \
        "Four exams instead of one: the chart's false alarms run @@FOLDS@@. A spread, not one lucky number. 🔁", \
        "Use the same embargo as the main split: 24 hours."

def _c_d2(x):
    return int(x) == @@DIRTY@@, "@@DIRTY@@ instead of @@CLEAN@@: with EV04 inside the reference, the fault became part of 'normal'. 🧽", \
        "Fit on every steady hour of the year: DIRTY_FIT = steady"

def _c_bonus(x):
    return _near(x, @@HONEST@@, 1e-9), \
        "@@HONEST@@: the smallest budget that catches EV01, EV02 and EV03 in the past. On Sep–Dec: @@HONEST_FA@@ false alarms. Tuned honestly, the forest still doesn't beat the chart's @@R4_FA@@. 🌶️🏆", \
        "Read the list: the FIRST budget (smallest) where it catches 3 of 3 past events."

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "B1": _c_b1, "B2": _c_b2, "C1": _c_c1, "C2": _c_c2, "C3": _c_c3,
          "C4": _c_c4, "C5": _c_c5, "C6": _c_c6, "D1": _c_d1, "D2": _c_d2, "BONUS": _c_bonus}
HINTS = {"B1": "Two dates, as text: TRAIN_END and TEST_START.", "D1": "GAP is a number of hours."}
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
    return [
        ("md", """# 🥊 Week 5 · Day 1: No Expo! Honest Train/Test Splits

**Today:** you catch a model cheating, build an honest split by time, and referee a fair fight between the isolation forest and the Week 4 control chart.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**

**Rule book:** keep `W5D1-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up
Run it once every time you open the notebook (and after every restart). Wait for `✅ Ready!`."""),
        ("setup", setup_code),
        ("md", """### ▶️ The data and the answer key
The same year of hourly bus telemetry as Week 4 Days 2 and 3, and its answer key: 5 labelled events."""),
        ("code", 'from sklearn.ensemble import IsolationForest\nfrom sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.preprocessing import StandardScaler\nfrom sklearn.pipeline import make_pipeline\n'
                 'from sklearn.model_selection import train_test_split, TimeSeriesSplit\n\n'
                 'bus = pd.read_csv(data_path("bus_telemetry_multivariate_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n'
                 'labels = load_labels("anomaly_labels_week5")\n'
                 'print("hours:", len(bus), "· events:", len(labels))\n'
                 'display(labels[["event_id", "start", "end", "type"]])'),
        ("md", """### ▶️ Your tools from Week 4 (run both cells)
You built these pieces on Days 2 and 3: the scorer and its event table, steady sunlight, the lean features (4 health channels + `temp_per_drive`), the chart and the forest. Read them once, then run."""),
        ("code", SCORER_CODE + '\n\nprint("✅ score_events() and event_table() are ready")'),
        ("code", DETECTOR_CODE + '\n\nsteady = steady_sun(bus)\nX = lean_features(bus)\n'
                 'print("steady-sun hours:", int(steady.sum()), "· lean features:", list(X.columns))'),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Catch the expo (10 min) 🕵🏾

📖 Meet the **copycat**: for each new hour it finds the single most similar hour it has seen, and copies that hour's answer (fault or normal). It **learns from the answer key** (supervised). Our forest never sees labels; the copycat is only here to show how a split can cheat.

▶️ First the answer column `y`: 1 for every hour inside a labelled fault, 0 otherwise."""),
        ("code", 'y = pd.Series(0, index=bus.index)\nfor _, ev in labels.iterrows():\n    y.loc[ev["start"]:ev["end"]] = 1\n'
                 'print("fault hours in the year:", int(y.sum()))\n\n'
                 'def copycat():\n    """Copies the answer of the ONE most similar hour it has seen (1 nearest neighbour)."""\n'
                 '    return make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))'),
        ("md", """### A1 ✍️ The random split
The cell shuffles all hours and keeps a third for the test. Then: of the **real fault hours in the test**, what share did the copycat call a fault?
`pred` holds 1 (fault) or 0 (normal) for every test hour, so the share is the mean of `pred` over the fault hours: `pred[y_te == 1].mean()`."""),
        _task('X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.33, random_state=42)\n'
              'pred = copycat().fit(X_tr, y_tr).predict(X_te)\nprint("fault hours in the random test set:", int((y_te == 1).sum()))\n\n'
              'found_random = ___\n\nassert found_random is not None, "✍️ Fill in found_random first."\n'
              'print(f"share of fault hours found: {found_random:.1%}")\ncheck("A1", found_random)',
              'X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.33, random_state=42)\n'
              'pred = copycat().fit(X_tr, y_tr).predict(X_te)\nprint("fault hours in the random test set:", int((y_te == 1).sum()))\n\n'
              'found_random = pred[y_te == 1].mean()\n\nassert found_random is not None, "✍️ Fill in found_random first."\n'
              'print(f"share of fault hours found: {found_random:.1%}")\ncheck("A1", found_random)'),
        ("md", """### A2 ✍️ Now split by time
Same copycat, same features. This time it trains on **January to August** and is tested on September onwards (skipping one day: Part B explains why).
Type the first day of September as text, like `"2025-01-01"`."""),
        _task('CUT = ___\n\nassert CUT is not None, "✍️ Fill in CUT first."\nbefore = bus.index < CUT\n'
              'after = bus.index >= pd.Timestamp(CUT) + pd.Timedelta("1D")\n'
              'pred_time = pd.Series(copycat().fit(X[before], y[before]).predict(X[after]), index=X.index[after])\n'
              'found_time = pred_time[y[after] == 1].mean()\n'
              'print(f"share of fault hours found: {found_time:.1%} (of {int((y[after] == 1).sum())})")\ncheck("A2", found_time)',
              'CUT = "2025-09-01"\n\nassert CUT is not None, "✍️ Fill in CUT first."\nbefore = bus.index < CUT\n'
              'after = bus.index >= pd.Timestamp(CUT) + pd.Timedelta("1D")\n'
              'pred_time = pd.Series(copycat().fit(X[before], y[before]).predict(X[after]), index=X.index[after])\n'
              'found_time = pred_time[y[after] == 1].mean()\n'
              'print(f"share of fault hours found: {found_time:.1%} (of {int((y[after] == 1).sum())})")\ncheck("A2", found_time)'),
        ("md", """### A3 ✍️ Which event did it still catch?
▶️ The table shows each test event. Type the event id it caught (e.g. `"EV01"`)."""),
        _task('assert "pred_time" in globals(), "✍️ Finish A2 first, then run this cell."\n'
              'display(event_table(pred_time == 1, labels))\n\ncaught_event = ___\n\ncheck("A3", caught_event)',
              'assert "pred_time" in globals(), "✍️ Finish A2 first, then run this cell."\n'
              'display(event_table(pred_time == 1, labels))\n\ncaught_event = "EV05"\n\ncheck("A3", caught_event)'),
        ("md", """> 📖 **What just happened?** In the random split, every test hour inside a fault had its neighbour (one hour earlier or later) in training, and the copycat copied the answer from the next seat. That's **expo**. Split by time, it only recognised EV05, a repeat of EV02 that it had seen in May."""),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Split by time (8 min) ✂️

### B1 ✍️ Train, embargo, test
- **train** = every hour **before** 1 September
- **embargo** = 1 September: left out
- **test** = every hour **from** 2 September

Type both dates as text."""),
        _task('TRAIN_END = ___\nTEST_START = ___\n\nassert TRAIN_END is not None and TEST_START is not None, "✍️ Fill in both dates first."\n'
              'train = bus.index < TRAIN_END\ntest = bus.index >= TEST_START\n'
              'print("train hours:", int(train.sum()), "· test hours:", int(test.sum()), "· embargo hours:", int((~train & ~test).sum()))\n\n'
              'assert bus.index[train].max() < bus.index[test].min(), "leakage: training overlaps the test"\n'
              'print("no overlap:", bus.index[train].max(), "<", bus.index[test].min())\ncheck("B1", (train.sum(), test.sum()))',
              'TRAIN_END = "2025-09-01"\nTEST_START = "2025-09-02"\n\nassert TRAIN_END is not None and TEST_START is not None, "✍️ Fill in both dates first."\n'
              'train = bus.index < TRAIN_END\ntest = bus.index >= TEST_START\n'
              'print("train hours:", int(train.sum()), "· test hours:", int(test.sum()), "· embargo hours:", int((~train & ~test).sum()))\n\n'
              'assert bus.index[train].max() < bus.index[test].min(), "leakage: training overlaps the test"\n'
              'print("no overlap:", bus.index[train].max(), "<", bus.index[test].min())\ncheck("B1", (train.sum(), test.sum()))'),
        ("md", """### B2 ✍️ How long must the embargo be?
In Week 4 Day 3 the history features used `rolling(24)`: each value looks back 24 hours. Without a gap, that window on the first test hour would read training hours.
What's the shortest safe embargo, **in hours**?"""),
        _task('EMBARGO_HOURS = ___\n\ncheck("B2", EMBARGO_HOURS)', 'EMBARGO_HOURS = 24\n\ncheck("B2", EMBARGO_HOURS)'),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: The fair fight (20 min) 🥊

**The rules, written first:** same test months (2 Sep – 31 Dec), same scorer, settings fixed before looking at the test (chart `k = 3`, forest `contamination = 0.005`).

▶️ `on_test()` scores only the test months. Two events live there: **EV04** (the amplifier running hot) and **EV05** (the charge controller)."""),
        ("code", 'def on_test(flags):\n    """Score a detector on the held-out months only."""\n    return score_events(flags[test], labels)\n\n'
                 'HEALTH = ["solar_array_current_a", "bus_voltage_v", "battery_soc_pct", "battery_temp_c", "twta_temp_c"]\n'
                 'sunlit = bus["eclipse_flag"] == 0\nprint("ready: on_test(), HEALTH, sunlit, steady, X")'),
        ("md", """### C1 ✍️ Contender 1: the Week 4 chart exactly as taught
3σ on each raw health channel, limits from the training months, judging **sunlit** hours (the Week 3 Day 1 fix). Use the classic **K**."""),
        _task('K = ___\n\nassert K is not None, "✍️ Fill in K first."\nflags_1 = chart_flags(bus[HEALTH], train & sunlit, sunlit, k=K)\n'
              'result_1 = on_test(flags_1)\nprint(result_1)\ncheck("C1", result_1)',
              'K = 3\n\nassert K is not None, "✍️ Fill in K first."\nflags_1 = chart_flags(bus[HEALTH], train & sunlit, sunlit, k=K)\n'
              'result_1 = on_test(flags_1)\nprint(result_1)\ncheck("C1", result_1)'),
        ("md", "▶️ It caught EV04. But **when** did it flag EV04? Look at the hour of day of every flag inside it."),
        ("code", 'assert "flags_1" in globals(), "✍️ Finish C1 first, then run this cell."\n'
                 'display(event_table(flags_1[test], labels))\nin_ev04 = flags_1.loc["2025-09-03":"2025-09-30"]\n'
                 'in_ev04[in_ev04].index.hour.value_counts().sort_index().rename_axis("hour of day").to_frame("flags inside EV04")'),
        ("md", """### C2 ✍️ Real catch or lucky catch?
Eclipse is at 21:00. The 3 hours after it are the battery recharging. EV04 is the **amplifier** running hot. Type `"real"` or `"lucky"`."""),
        _task('lucky_or_real = ___\n\ncheck("C2", lucky_or_real)', 'lucky_or_real = "lucky"\n\ncheck("C2", lucky_or_real)'),
        ("md", """### C3 ✍️ Contender 2: the same chart on steady sunlight
Recharge hours have their own normal. Fit and judge only **steady** hours instead of sunlit hours. Type the variable name, **no quotes**."""),
        _task('CONTEXT = ___\n\nassert CONTEXT is not None, "✍️ Fill in CONTEXT first."\n'
              'assert not isinstance(CONTEXT, str), "✍️ Use the variable itself, without quotes: CONTEXT = steady"\n'
              'flags_2 = chart_flags(bus[HEALTH], train & CONTEXT, CONTEXT)\nresult_2 = on_test(flags_2)\nprint(result_2)\ncheck("C3", result_2)',
              'CONTEXT = steady\n\nassert CONTEXT is not None, "✍️ Fill in CONTEXT first."\n'
              'assert not isinstance(CONTEXT, str), "✍️ Use the variable itself, without quotes: CONTEXT = steady"\n'
              'flags_2 = chart_flags(bus[HEALTH], train & CONTEXT, CONTEXT)\nresult_2 = on_test(flags_2)\nprint(result_2)\ncheck("C3", result_2)'),
        ("md", """### C4 ✍️ Contender 3: the isolation forest on the lean features
Steady hours, fitted on the training months. Use the false-alarm budget fixed in Week 4 Day 2: **0.5%**, written as a fraction."""),
        _task('CONTAMINATION = ___\n\nassert CONTAMINATION is not None, "✍️ Fill in CONTAMINATION first."\n'
              'flags_3 = forest_flags(X, train & steady, steady, contamination=CONTAMINATION)\nresult_3 = on_test(flags_3)\nprint(result_3)\ncheck("C4", result_3)',
              'CONTAMINATION = 0.005\n\nassert CONTAMINATION is not None, "✍️ Fill in CONTAMINATION first."\n'
              'flags_3 = forest_flags(X, train & steady, steady, contamination=CONTAMINATION)\nresult_3 = on_test(flags_3)\nprint(result_3)\ncheck("C4", result_3)'),
        ("md", """### C5 ✍️ Contender 4: the Week 4 chart on the SAME lean features
Same hours, same months, same features as the forest. Only the model changes."""),
        _task('K = ___\n\nassert K is not None, "✍️ Fill in K first."\nflags_4 = chart_flags(X, train & steady, steady, k=K)\n'
              'result_4 = on_test(flags_4)\nprint(result_4)\ncheck("C5", result_4)',
              'K = 3\n\nassert K is not None, "✍️ Fill in K first."\nflags_4 = chart_flags(X, train & steady, steady, k=K)\n'
              'result_4 = on_test(flags_4)\nprint(result_4)\ncheck("C5", result_4)'),
        ("md", "▶️ The report card, with one extra column: how many of EV04's hours each detector lit up."),
        ("code", 'assert "result_4" in globals(), "✍️ Finish C1–C5 first, then run this cell."\n'
                 'ev04 = (bus.index >= "2025-09-03") & (bus.index < "2025-10-01")\ncard = pd.DataFrame([\n'
                 '    {"detector": "1. Week 4 chart, raw, sunlit (as taught)", **result_1, "EV04 hours lit": int((flags_1 & ev04).sum())},\n'
                 '    {"detector": "2. Week 4 chart, raw, steady sun", **result_2, "EV04 hours lit": int((flags_2 & ev04).sum())},\n'
                 '    {"detector": "3. Isolation forest, lean features", **result_3, "EV04 hours lit": int((flags_3 & ev04).sum())},\n'
                 '    {"detector": "4. Week 4 chart, lean features", **result_4, "EV04 hours lit": int((flags_4 & ev04).sum())},\n'
                 ']).set_index("detector")\ncard'),
        ("md", """### C6 ✍️ Your recommendation
Which detector number (1, 2, 3 or 4) goes on the console? Catching both events **for the right reason** comes first, then the fewest false alarms."""),
        _task('my_pick = ___\n\ncheck("C6", my_pick)', 'my_pick = 4\n\ncheck("C6", my_pick)'),

        # ---------------- PART D ----------------
        ("md", """---
# Part D: Is it just luck? (7 min) 🔁

### D1 ✍️ Rolling origin: four exams instead of one
`TimeSeriesSplit` cuts the year into blocks. Each fold trains on **everything before** a block and tests on the block. Training only ever grows forwards.
Leave the same embargo between each training block and its test block: how many hours?"""),
        _task('GAP = ___\n\nassert GAP is not None, "✍️ Fill in GAP first."\nrows = []\n'
              'for k, (fit_pos, test_pos) in enumerate(TimeSeriesSplit(n_splits=4, gap=GAP).split(X), start=1):\n'
              '    fit = np.zeros(len(X), dtype=bool)\n    fit[fit_pos] = True\n    judge = np.zeros(len(X), dtype=bool)\n    judge[test_pos] = True\n'
              '    c = score_events(chart_flags(X, fit & steady, steady)[judge], labels)\n'
              '    f = score_events(forest_flags(X, fit & steady, steady)[judge], labels)\n'
              '    rows.append({"fold": k, "test block": f"{X.index[test_pos[0]]:%d %b} – {X.index[test_pos[-1]]:%d %b}",\n'
              '                 "chart caught": f"{c[\'caught\']}/{c[\'events\']}", "chart false alarms": c["false_alarms"],\n'
              '                 "forest caught": f"{f[\'caught\']}/{f[\'events\']}", "forest false alarms": f["false_alarms"]})\n'
              'folds = pd.DataFrame(rows).set_index("fold")\ndisplay(folds)\ncheck("D1", (GAP, folds["chart false alarms"].tolist()))',
              'GAP = 24\n\nassert GAP is not None, "✍️ Fill in GAP first."\nrows = []\n'
              'for k, (fit_pos, test_pos) in enumerate(TimeSeriesSplit(n_splits=4, gap=GAP).split(X), start=1):\n'
              '    fit = np.zeros(len(X), dtype=bool)\n    fit[fit_pos] = True\n    judge = np.zeros(len(X), dtype=bool)\n    judge[test_pos] = True\n'
              '    c = score_events(chart_flags(X, fit & steady, steady)[judge], labels)\n'
              '    f = score_events(forest_flags(X, fit & steady, steady)[judge], labels)\n'
              '    rows.append({"fold": k, "test block": f"{X.index[test_pos[0]]:%d %b} – {X.index[test_pos[-1]]:%d %b}",\n'
              '                 "chart caught": f"{c[\'caught\']}/{c[\'events\']}", "chart false alarms": c["false_alarms"],\n'
              '                 "forest caught": f"{f[\'caught\']}/{f[\'events\']}", "forest false alarms": f["false_alarms"]})\n'
              'folds = pd.DataFrame(rows).set_index("fold")\ndisplay(folds)\ncheck("D1", (GAP, folds["chart false alarms"].tolist()))'),
        ("md", """### D2 ✍️ A dirty reference period
What if you fit on the **whole year**, EV04 included? Set `DIRTY_FIT` to every steady hour of the year (the variable, no quotes). The cell counts how many of EV04's hours each detector still lights up."""),
        _task('DIRTY_FIT = ___\n\nassert DIRTY_FIT is not None, "✍️ Fill in DIRTY_FIT first."\n'
              'assert not isinstance(DIRTY_FIT, str), "✍️ Use the variable itself, without quotes: DIRTY_FIT = steady"\n'
              'lit = pd.DataFrame({\n    "clean reference (Jan–Aug)": [int((flags_4 & ev04).sum()), int((flags_3 & ev04).sum())],\n'
              '    "dirty reference (whole year)": [int((chart_flags(X, DIRTY_FIT, steady) & ev04).sum()),\n'
              '                                     int((forest_flags(X, DIRTY_FIT, steady) & ev04).sum())],\n}, index=["chart", "forest"])\n'
              'print(f"EV04 hours lit, out of {int(ev04.sum())}:")\ndisplay(lit)\ncheck("D2", lit.loc["chart", "dirty reference (whole year)"])',
              'DIRTY_FIT = steady\n\nassert DIRTY_FIT is not None, "✍️ Fill in DIRTY_FIT first."\n'
              'assert not isinstance(DIRTY_FIT, str), "✍️ Use the variable itself, without quotes: DIRTY_FIT = steady"\n'
              'lit = pd.DataFrame({\n    "clean reference (Jan–Aug)": [int((flags_4 & ev04).sum()), int((flags_3 & ev04).sum())],\n'
              '    "dirty reference (whole year)": [int((chart_flags(X, DIRTY_FIT, steady) & ev04).sum()),\n'
              '                                     int((forest_flags(X, DIRTY_FIT, steady) & ev04).sum())],\n}, index=["chart", "forest"])\n'
              'print(f"EV04 hours lit, out of {int(ev04.sum())}:")\ndisplay(lit)\ncheck("D2", lit.loc["chart", "dirty reference (whole year)"])'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: tune the forest the honest way
*"The forest lost because 0.5% was the wrong budget!"* Fair. But you may only tune on the **past**: the training months and their labels (EV01, EV02, EV03). Looking at September to December to choose would be expo.

▶️ The cell tries several budgets on the training months. ✍️ Pick the **smallest** budget that catches all 3 past events, then see what it does on the test."""),
        _task('assert "result_4" in globals(), "✍️ Finish Part C first, then run this cell."\n'
              'for c in [0.001, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.005]:\n'
              '    r = score_events(forest_flags(X, train & steady, steady, contamination=c)[train], labels)\n'
              '    print(f"contamination {c:.4f}: caught {r[\'caught\']} of {r[\'events\']} past events, {r[\'false_alarms\']} false alarms")\n\n'
              'HONEST_CONTAMINATION = ___\n\nassert HONEST_CONTAMINATION is not None, "✍️ Pick HONEST_CONTAMINATION first."\n'
              'honest = on_test(forest_flags(X, train & steady, steady, contamination=HONEST_CONTAMINATION))\n'
              'print("\\nforest, honest budget, Sep–Dec:", honest)\nprint("chart, k = 3, Sep–Dec:          ", result_4)\ncheck("BONUS", HONEST_CONTAMINATION)',
              'assert "result_4" in globals(), "✍️ Finish Part C first, then run this cell."\n'
              'for c in [0.001, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.005]:\n'
              '    r = score_events(forest_flags(X, train & steady, steady, contamination=c)[train], labels)\n'
              '    print(f"contamination {c:.4f}: caught {r[\'caught\']} of {r[\'events\']} past events, {r[\'false_alarms\']} false alarms")\n\n'
              f'HONEST_CONTAMINATION = {day_facts()["honest_c"]!r}\n\nassert HONEST_CONTAMINATION is not None, "✍️ Pick HONEST_CONTAMINATION first."\n'
              'honest = on_test(forest_flags(X, train & steady, steady, contamination=HONEST_CONTAMINATION))\n'
              'print("\\nforest, honest budget, Sep–Dec:", honest)\nprint("chart, k = 3, Sep–Dec:          ", result_4)\ncheck("BONUS", HONEST_CONTAMINATION)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", f"""### 📝 What you learned today
- **Expo** fakes a score three ways: test hours with neighbours in training (random splits), features that peek ahead, and settings tuned on the test answers.
- **Split by time:** train on the past, test on the future, with an **embargo** at least as long as your longest feature window, and `assert` there's no overlap.
- **A fair fight** = same held-out months, same hours, same scorer, settings fixed first.
- **Ask why a flag fired.** A catch for the wrong reason is a lucky catch.
- **The feature won, not the forest.** On the same features, the Week 4 chart caught both events with {F['fight'][K4]['false_alarms']} false alarm; the forest needed {F['fight'][K3]['false_alarms']}. When the simple model wins or ties, recommend it.
- **One cut is one number.** Rolling origin gives a spread. And a reference period that contains the fault teaches the model that the fault is normal.

**Next time:** *Forecasting baselines*: Grandma's forecast, "tomorrow will be like today", and why she's hard to beat. 👵🏾

<sub>Data: synthetic teaching dataset from the original Week 5 code book (`Time-series/week-05`). Safe to use with AI tools; real NIGCOMSAT data is not.</sub>"""),
    ]


# =============================================================================
# EXTRAS: Quiz 3
# =============================================================================
def extra(d, foot):
    quiz = quizkit.write_quiz(d, foot, n=3, mcq_file="week-05-mcq.csv", seed=QUIZ_SEED, covers="Machine learning",
                              topic_map="the scikit-learn workflow → W4D2 · isolation forest and clustering → W4D2 · "
                                        "feature engineering from time series → W4D3 · temporal train-test discipline → W5D1")
    counts = {L: sum(q["letter"] == L for q in quiz if len(q["options"]) == 4) for L in "ABCD"}
    tf = {L: sum(q["letter"] == L for q in quiz if len(q["options"]) == 2) for L in "AB"}
    print(f"Quiz 3 answer positions: multiple choice {counts}, True/False {tf}")
    flagged = {q["number"]: q["letter"] for q in quiz if q["number"] in (4, 8, 18)}
    print(f"Quiz 3 corrected questions (number: letter): {flagged}")
