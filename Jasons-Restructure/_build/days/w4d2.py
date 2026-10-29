"""Week 4 · Day 2: Meet scikit-learn + Isolation Forest."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

import w5detector as w5
from common import BRAND as B
from svgcharts import _scale
from webdeck import logos_title_block

CODE = "W4D2"
TITLE = "Meet scikit-learn + Isolation Forest"

GRID, AXIS = "#24384F", "#9DB0C6"
RED, GOLD, GREEN = "#FF6B6F", "#F5B83D", "#3CCB7F"
CLUSTER_COLS = [B["blue_d"], GOLD, B["teal_d"], "#C084FC"]
SHORT = {"solar_array_current_a": "array A", "bus_voltage_v": "bus V", "battery_soc_pct": "SoC %",
         "battery_temp_c": "batt °C", "twta_temp_c": "TWTA °C", "rf_drive_pct": "drive %"}


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# =============================================================================
# DATA: the shared Week 5 facts, plus the few extra numbers only this day shows
# =============================================================================
def _score(flags, labels):
    r = w5.score_events(flags, labels)
    r["table"] = w5.event_table(flags, labels)
    r["which"] = [e for e, row in r["table"].iterrows() if row["caught"]]
    return r


@lru_cache(maxsize=1)
def facts():
    from sklearn.ensemble import IsolationForest

    F = dict(w5.facts())
    bus, labels = F["bus"], F["labels"]
    tr, st = F["train"], F["steady"]
    raw = bus[w5.RAW]
    f_all = F["w4d2_raw_all_flags"]
    F["raw_all_train_flags"] = int((f_all & tr).sum())
    F["expected_flags"] = w5.CONTAMINATION * len(bus)
    F["ev04_hours_all"] = sorted(set(f_all[f_all & F["ev04_mask"]].index.hour))
    ref = raw[tr & st]
    F["z6"] = (raw - ref.mean()) / ref.std()
    f_st = F["w4d2_raw_steady_flags"]
    jan = f_st & (bus.index.month == 1)
    F["jan_z"] = F["z6"][jan].mean()
    F["jan_first"], F["jan_last"] = f_st[jan].index.min(), f_st[jan].index.max()
    m2 = IsolationForest(n_estimators=200, contamination=w5.CONTAMINATION, random_state=w5.SEED).fit(raw[tr & st])
    s2 = pd.Series(m2.decision_function(raw), index=bus.index).where(st)
    F["ev03_rank"] = int((s2 < s2["2025-06-30 00:00"]).sum()) + 1
    F["ev04_flag_time"] = f_st[f_st & F["ev04_mask"]].index.min()
    F["seed_runs"] = {s: _score(w5.forest_flags(raw, tr & st, st, seed=s), labels) for s in (42, 0, 1, 7)}
    F["pepper"] = _score(w5.forest_flags(raw, tr & st, st, contamination=0.002), labels)
    F["chart_ev03_z"] = F["z6"].loc["2025-06-30 00:00"]
    arr, tw = bus["solar_array_current_a"], bus["twta_temp_c"]
    F["ev03_drop"] = arr["2025-06-29 23:00"] - arr["2025-06-30 00:00"]
    F["recharge_array"], F["recharge_batt"] = arr[F["recharge"]].mean(), bus.loc[F["recharge"], "battery_temp_c"].mean()
    F["v_sd"] = bus.loc[tr & st, "bus_voltage_v"].std()
    F["ev04_jump"] = tw["2025-09-03"].mean() - tw["2025-09-02"].mean()      # day-on-day jump at the fault's start
    F["seeds_no_ev04"] = [s for s, r in F["seed_runs"].items() if "EV04" not in r["which"]]
    # which steady-sun hours did k-means put with recharge? (warm-battery hours)
    from sklearn.cluster import KMeans
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    cl = pd.Series(make_pipeline(StandardScaler(), KMeans(4, n_init=10, random_state=w5.SEED)).fit_predict(raw), index=bus.index)
    rech_cluster = cl[F["recharge"]].mode()[0]
    odd = cl[(cl == rech_cluster) & ~F["recharge"] & ~F["ecl"]]
    F["km_warm_steady"] = list(odd.index)
    big = cl[st & (cl != rech_cluster)].value_counts()      # the two steady-sun clusters
    cool = big.index[-1]                                     # ... and the smaller one
    F["km_cool_months"] = cl[(cl == cool) & st].index.month.value_counts().sort_index()
    return F


# =============================================================================
# LOCAL SVG HELPERS
# =============================================================================
def chart_svg(values, *, w=1400, h=420, ymin=None, ymax=None, color=B["blue_d"], dots=(), xlabels=(), yticks=(),
              stroke=2.5, delay=".3s", dur="2.4s"):
    """Full-resolution line with optional dots: dots=[(i, colour)] · xlabels=[(i, text)] · yticks=[(y, text)]"""
    v = np.asarray(values, dtype=float)
    n = len(v)
    lo = np.nanmin(v) if ymin is None else ymin
    hi = np.nanmax(v) if ymax is None else ymax
    L, R, T, Bm = 92, w - 24, 26, h - 56

    def X(i):
        return _scale(i, 0, n - 1, L, R)

    def Y(y):
        return _scale(y, lo, hi, Bm, T)

    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block" xmlns="http://www.w3.org/2000/svg">']
    for (yv, lab) in yticks:
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L - 12}" y="{Y(yv) + 7:.1f}" fill="{AXIS}" font-size="19" text-anchor="end">{lab}</text>')
    for (i, lab) in xlabels:
        anchor = "start" if i == 0 else ("end" if i >= n - 1 else "middle")
        o.append(f'<text x="{X(i):.1f}" y="{h - 18}" fill="{AXIS}" font-size="19" text-anchor="{anchor}">{lab}</text>')
    d = "M" + " L".join(f"{X(i):.1f},{Y(v[i]):.1f}" for i in range(n) if not np.isnan(v[i]))
    o.append(f'<path class="draw" style="--dur:{dur};--d:{delay}" d="{d}" fill="none" stroke="{color}" '
             f'stroke-width="{stroke}" stroke-linejoin="round" stroke-linecap="round"/>')
    for k, (i, col) in enumerate(dots):
        o.append(f'<circle class="anim a-pop" style="--d:{2.2 + 0.01 * k:.2f}s;transform-origin:{X(i):.0f}px {Y(v[i]):.0f}px" '
                 f'cx="{X(i):.1f}" cy="{Y(v[i]):.1f}" r="7" fill="{col}" stroke="{B["space"]}" stroke-width="2"/>')
    o.append("</svg>")
    return "".join(o)


def _isolation_cuts(pts, target, rng):
    """The real isolation procedure on 2-D points: random axis, random cut between min and max, keep the target's side."""
    lo, hi = np.array([0.0, 0.0]), np.array([1.0, 1.0])
    idx, cuts = np.arange(len(pts)), []
    while len(idx) > 1:
        ax = int(rng.integers(2))
        a, b = pts[idx, ax].min(), pts[idx, ax].max()
        if a == b:
            continue
        c = rng.uniform(a, b)
        cuts.append((ax, c, lo.copy(), hi.copy()))
        if pts[target, ax] < c:
            hi[ax], idx = c, idx[pts[idx, ax] < c]
        else:
            lo[ax], idx = c, idx[pts[idx, ax] >= c]
    return cuts


@lru_cache(maxsize=1)
def _beach():
    """60 guests in shorts + the man in agbada. Find a seed where he takes <= 2 cuts and a guest takes >= 8."""
    rng = np.random.default_rng(7)
    guests = np.clip(rng.normal([0.42, 0.42], 0.11, size=(60, 2)), 0.06, 0.78)
    pts = np.vstack([guests, [[0.9, 0.86]]])
    agbada = len(pts) - 1
    guest = int(np.argmin(((guests - guests.mean(axis=0)) ** 2).sum(axis=1)))
    for seed in range(500):
        a = _isolation_cuts(pts, agbada, np.random.default_rng(seed))
        g = _isolation_cuts(pts, guest, np.random.default_rng(seed + 1000))
        if len(a) <= 2 and len(g) >= 8:
            return pts, agbada, guest, a, g
    raise RuntimeError("no demo seed found")


def iso_svg(which, w=640, h=470):
    pts, agbada, guest, a_cuts, g_cuts = _beach()
    target, cuts = (agbada, a_cuts) if which == "agbada" else (guest, g_cuts)
    P = 26

    def X(x):
        return P + x * (w - 2 * P)

    def Y(y):
        return h - P - y * (h - 2 * P)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">',
         f'<rect x="{P}" y="{P}" width="{w - 2 * P}" height="{h - 2 * P}" rx="16" fill="none" stroke="{GRID}" stroke-width="2"/>']
    for i, (x, y) in enumerate(pts):
        if i == target:
            continue
        col = B["teal_d"] if i != agbada else "#8FA3BA"
        o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="8" fill="{col}" fill-opacity=".85"/>')
    tx, ty = pts[target]
    tcol = GOLD if which == "agbada" else B["blue_d"]
    for k, (ax, c, lo, hi) in enumerate(cuts):
        d = 0.6 + 0.35 * k
        if ax == 0:
            x1 = x2 = X(c)
            y1, y2 = Y(lo[1]), Y(hi[1])
        else:
            y1 = y2 = Y(c)
            x1, x2 = X(lo[0]), X(hi[0])
        o.append(f'<path class="draw" style="--d:{d:.2f}s;--dur:.45s" d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" '
                 f'stroke="{RED}" stroke-width="{3.5 if len(cuts) < 4 else 2}" stroke-opacity=".9" fill="none"/>')
    o.append(f'<circle class="anim a-pop" style="--d:.3s;transform-origin:{X(tx):.0f}px {Y(ty):.0f}px" cx="{X(tx):.1f}" cy="{Y(ty):.1f}" '
             f'r="15" fill="{tcol}" stroke="#fff" stroke-width="3"/>')
    o.append("</svg>")
    return "".join(o)


def grid_svg(flags, ecl, start="2025-09-03", days=28, cw=25, ch=12.5):
    """One cell per hour of EV04's window: rows = days, columns = hour of day. Grey = eclipse hour, red = flagged."""
    t0 = pd.Timestamp(start)
    L, T = 70, 34
    w, h = L + 24 * cw + 10, T + days * ch + 8
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" width="100%" style="max-width:{w:.0f}px;display:block">']
    for hr in (0, 6, 12, 18, 21):
        o.append(f'<text x="{L + hr * cw + cw / 2:.1f}" y="22" fill="{GOLD if hr == 21 else AXIS}" font-size="17" '
                 f'font-weight="{800 if hr == 21 else 400}" text-anchor="middle">{hr:02d}h</text>')
    for dday in (0, 7, 14, 21, days - 1):
        o.append(f'<text x="{L - 10}" y="{T + dday * ch + ch - 1:.1f}" fill="{AXIS}" font-size="16" text-anchor="end">'
                 f'{(t0 + pd.Timedelta(days=dday)):%d %b}</text>')
    base, grey, red = [], [], []
    for dday in range(days):
        for hr in range(24):
            t = t0 + pd.Timedelta(days=dday, hours=hr)
            seg = f"M{L + hr * cw + 1:.1f} {T + dday * ch + 1:.1f}h{cw - 2}v{ch - 2}h-{cw - 2}z"
            (red if flags.get(t, False) else grey if ecl.get(t, False) else base).append(seg)
    o.append(f'<path d="{"".join(base)}" fill="#22405F"/>')
    o.append(f'<path d="{"".join(grey)}" fill="#8FA3BA"/>')
    if red:
        o.append(f'<path class="anim a-fade" style="--d:.9s" d="{"".join(red)}" fill="{RED}"/>')
    o.append("</svg>")
    return "".join(o)


def state_bars_svg(tab, w=680, h=300):
    """100% bar per operating state, split by the cluster k-means put each hour in."""
    rows = [("eclipse", "🌘 eclipse"), ("recharge", "🔋 recharge"), ("steady sun", "🌞 steady sun")]
    L, R = 190, w - 20
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for k, (st, lab) in enumerate(rows):
        y = 30 + k * 88
        col = tab[st]
        tot = col.sum()
        o.append(f'<text x="0" y="{y + 34}" fill="#EAF2FB" font-size="23" font-weight="700">{lab}</text>')
        x = L
        for cl, n in col.items():
            if n == 0:
                continue
            wd = (R - L) * n / tot
            o.append(f'<rect class="anim a-fade" style="--d:{.3 + k * .25:.2f}s" x="{x:.1f}" y="{y}" width="{max(wd, 3):.1f}" height="52" '
                     f'rx="8" fill="{CLUSTER_COLS[int(cl) % 4]}" stroke="{B["space2"]}" stroke-width="2"/>')
            if wd > 70:
                o.append(f'<text class="anim a-fade" style="--d:{.5 + k * .25:.2f}s" x="{x + wd / 2:.1f}" y="{y + 34}" fill="#0B1622" '
                         f'font-size="20" font-weight="800" text-anchor="middle">{n:,}</text>')
            x += wd
    o.append("</svg>")
    return "".join(o)


def z_table(F, rows):
    """HTML table of per-channel z-scores; the loudest channel in each row is gold."""
    z = F["z6"]
    head = "".join(f"<th>{SHORT[c]}</th>" for c in w5.RAW)
    body = ""
    for k, (t, lab) in enumerate(rows):
        r = z.loc[t]
        top = r.abs().idxmax()
        cells = "".join(f'<td class="mono" style="color:{GOLD if c == top else "#EAF2FB"};font-weight:{800 if c == top else 400}">'
                        f'{r[c]:+.1f}</td>' for c in w5.RAW)
        body += f'<tr class="anim a-left" style="--d:{.3 + k * .25:.2f}s"><td><b>{lab}</b><br><span class="small">{t:%d %b %H:%M}</span></td>{cells}</tr>'
    css = ("<style>.zt{width:100%;border-collapse:separate;border-spacing:0 8px;font-size:25px}"
           ".zt th{color:#9DB0C6;font-size:19px;text-align:center;font-weight:700;padding:0 10px}"
           ".zt td{background:#12233A;padding:10px 12px;text-align:center}.zt td:first-child{text-align:left;border-radius:14px 0 0 14px;width:300px}"
           ".zt td:last-child{border-radius:0 14px 14px 0}</style>")
    return f'{css}<table class="zt"><tr class="anim" style="--d:.1s"><th></th>{head}</tr>{body}</table>'


def event_cards(r, notes_by_event):
    """Five little cards: ✅ / ❌ per event, with a one-line reason."""
    t = r["table"]
    out = ""
    for k, (e, row) in enumerate(t.iterrows()):
        ok = bool(row["caught"])
        col = GREEN if ok else RED
        extra = notes_by_event.get(e, f'{int(row["hours_flagged"])} of {int(row["hours_long"])} h lit')
        out += (f'<div class="card anim a-pop" style="--d:{.3 + k * .18:.2f}s;padding:18px 16px;text-align:center;border-color:{col}">'
                f'<div style="font-size:44px">{"✅" if ok else "❌"}</div><h3 style="font-size:28px;margin:6px 0 4px">{e}</h3>'
                f'<p class="small" style="font-size:19px">{row["type"].replace("_", " ")}</p>'
                f'<p style="font-size:20px;margin-top:8px;color:{col}">{extra}</p></div>')
    return f'<div class="grid5" style="gap:18px">{out}</div>'


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    F = facts()
    bus = F["bus"]
    ra, rs, cs = F["w4d2_raw_all"], F["w4d2_raw_steady"], F["chart_raw_steady"]
    ev04a = ra["table"].loc["EV04"]
    ev04s = rs["table"].loc["EV04"]
    _, _, _, a_cuts, g_cuts = _beach()
    n_flag = F["w4d2_raw_all_n"]
    hour = max(F["w4d2_raw_all_hours"], key=F["w4d2_raw_all_hours"].get)
    ecl = bus["eclipse_flag"] == 1
    flags_all, flags_st = F["w4d2_raw_all_flags"], F["w4d2_raw_steady_flags"]
    jan_z = F["jan_z"]
    km_s, km_u = F["kmeans_scaled"], F["kmeans_unscaled"]
    rech_u = sorted((int(v) for v in km_u["recharge"] if v > 0), reverse=True)
    tw_ceiling, tw_max = F["twta_ceiling"], F["twta_ev04_max"]
    ranges = F["ranges"]

    # whole-year array current with the forest's flags
    x = bus["solar_array_current_a"].values
    pos = {t: i for i, t in enumerate(bus.index)}
    year_chart = chart_svg(x, h=330, ymin=-1, ymax=31, color=B["blue_d"], stroke=1.1,
                           dots=[(pos[t], RED) for t in flags_all[flags_all].index],
                           yticks=[(0, "0 A"), (15, "15 A"), (28, "28 A")],
                           xlabels=[(0, "Jan"), (pos[pd.Timestamp("2025-03-01")], "Mar"), (pos[pd.Timestamp("2025-06-01")], "Jun"),
                                    (pos[pd.Timestamp("2025-09-01")], "Sep"), (len(x) - 1, "Dec")])
    top10 = "".join(f'<span class="pill {"gold" if t.hour == hour else "bad"}" style="font-size:20px">{t:%d %b} · {t:%H:%M}</span>'
                    for t in F["w4d2_top10"].index)

    head = bus[w5.RAW].head(4)
    xrows = "".join("<tr>" + f'<td class="mono" style="color:#9DB0C6">{t:%d %b %H:%M}</td>' +
                    "".join(f'<td class="mono">{v:.2f}</td>' for v in r) + "</tr>" for t, r in head.iterrows())
    xhead = "".join(f"<th>{SHORT[c]}</th>" for c in w5.RAW)
    xcss = ("<style>.xm{border-collapse:separate;border-spacing:0 6px;font-size:24px;width:100%}"
            ".xm th{color:#F5B83D;font-size:20px;padding:4px 12px;font-weight:800}.xm td{background:#12233A;padding:8px 12px;text-align:center}</style>")

    n_checks = _checks().count("\ndef _c_")
    z2, z1, zj = F["z6"].loc["2025-05-02 01:00"], F["z6"].loc["2025-02-19 11:00"], F["z6"].loc[F["jan_first"]]

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:60px;top:170px;width:560px">
  <div class="card anim a-pop" style="--d:.4s;padding:14px">{iso_svg("agbada", w=540, h=400)}</div>
</div>
<div style="max-width:880px;margin-top:40px">
  <div class="kicker anim">Week 4 · Day 2</div>
  <h1 class="anim" style="--d:.2s">Meet<br>scikit-learn<br><span class="hl">+ Isolation Forest</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Your first machine-learning detector.<br>Watch it look at six channels at once. 🌲🌲🌲</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex">{logos_title_block()}</div>
</div>""",
          "Welcome to machine learning. Today participants train their first model with scikit-learn, the Python library every "
          "data scientist uses. The picture on the right is the whole idea of the isolation forest in one image; we come back to it in a minute."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Three verbs, one forest, one honest look</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:270px;padding:36px 24px"><div class="icon">🧰</div><h3>fit · predict</h3><p class="small">the scikit-learn pattern</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:270px;padding:36px 24px"><div class="icon">🌲</div><h3>Isolation forest</h3><p class="small">six channels at once</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:270px;padding:36px 24px"><div class="icon">🌞</div><h3>Add context</h3><p class="small">the Week 3 lesson, again</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:270px;padding:36px 24px"><div class="icon">🧩</div><h3>Clustering</h3><p class="small">let the data find its modes</p></div>
</div>
<div class="row anim" style="--d:1.8s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up</span>
</div>""",
          "Four moves. The theme of the whole day: a model finds what is RARE. Our job is to make sure rare means BROKEN."),

        # 3 ─ beach party
        S(f"""
<div class="kicker anim">Quick game 🏖️</div>
<h2 class="anim" style="--d:.1s">Spot the man in agbada at a beach party</h2>
<div class="grid2" style="margin-top:10px;gap:30px">
  <div class="card anim a-left" style="--d:.2s;padding:16px 18px">{iso_svg("agbada")}
    <p style="font-size:25px;margin-top:6px">🟡 The man in agbada: <b class="good">{len(a_cuts)} cut{"s" if len(a_cuts) != 1 else ""}</b> and he's alone.</p></div>
  <div class="card anim a-right" style="--d:.5s;padding:16px 18px">{iso_svg("guest")}
    <p style="font-size:25px;margin-top:6px">🔵 One guest in shorts: <b class="bad">{len(g_cuts)} cuts</b> to get him alone.</p></div>
</div>""",
          f"Each red line is one random question, like 'is he left or right of here?'. The odd one out is isolated in {len(a_cuts)} "
          f"cut(s); someone in the middle of the crowd needs {len(g_cuts)}. That's the whole isolation forest: draw random cuts, "
          "count how many it takes to get a point alone, repeat with 200 different random trees, and average. FEW cuts = ODD. "
          "These cuts were drawn by the real procedure, not by hand."),

        # 4 ─ the lifeguard
        S("""
<div class="kicker anim">The twist</div>
<h2 class="anim" style="--d:.1s">The lifeguard in red shorts also stands out 🛟</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🧥</div><h3>The man in agbada</h3>
    <p class="muted">Rare <b style="color:#fff">and</b> out of place. Somebody should ask him why he's here.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill bad">rare + wrong = a fault</span></div></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">🛟</div><h3>The lifeguard</h3>
    <p class="muted">Just as rare, just as easy to isolate. But he <b style="color:#fff">belongs</b> there. Every evening.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill gold">rare + expected = eclipse 🌘</span></div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:36px;text-align:center">A forest finds what is <b class="hl">rare</b>. Rare is <b class="bad">not</b> the same as broken.</p>""",
          "Plant the idea now: the satellite's lifeguard is eclipse. 92 hours a year the array current goes to zero, the bus "
          "sags and the battery takes over. Rare, dramatic, completely normal. Keep this slide in mind: we hit it in 15 minutes."),

        # 5 ─ what ML adds
        S(f"""
<div class="kicker anim">What machine learning adds</div>
<h2 class="anim" style="--d:.1s">Week 3 watched one channel. This looks at <span class="hl">all six at once</span></h2>
<div class="row" style="gap:40px;margin-top:20px;align-items:center">
  <div class="col" style="flex:1;gap:12px">
    {"".join(f'<div class="card anim a-left" style="--d:{.2 + k * .12:.2f}s;padding:12px 22px;display:flex;justify-content:space-between"><b>{SHORT[c]}</b><span class="mono small">{ranges.loc[c, "min"]:.2f} → {ranges.loc[c, "max"]:.2f}</span></div>' for k, c in enumerate(w5.RAW))}
  </div>
  <div class="arrow anim a-fade" style="--d:1s;width:90px;height:4px;background:linear-gradient(90deg,#3B8BE0,#16A394)"></div>
  <div class="card glow anim a-pop" style="--d:1.2s;flex:1;text-align:center;padding:40px">
    <div class="big-emoji">🌲</div><h3 style="margin-top:14px">One score per hour</h3>
    <p class="muted">“How easy is this <b style="color:#fff">combination</b> to isolate?”</p></div>
</div>
<p class="anim" style="--d:1.6s;margin-top:26px;text-align:center">It can notice when the <b class="hl">relationship</b> between channels breaks, even if each one looks fine alone.</p>""",
          "Quiz question 1: ML can notice when the relationship between channels breaks. The ranges on the left are the real min and max "
          "of each channel for the whole year (file: bus_telemetry_multivariate_hourly, 8,760 hours, Week 5 data). A Week 3 control chart "
          "looks at one of these boxes. The forest looks at the whole row."),

        # 6 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">scikit-learn in 3 verbs 🧰</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Learn it once. Every model in the library works the same way.</p>""",
          "Section break.", cls="center"),

        # 7 ─ the X matrix
        S(f"""{xcss}
<div class="kicker anim">Step 1 · build X</div>
<h2 class="anim" style="--d:.1s">Rows are <span class="hl">hours</span>. Columns are <span class="hl">channels</span>.</h2>
<div class="card anim" style="--d:.2s;padding:20px 26px">
<table class="xm"><tr><th>hour</th>{xhead}</tr>{xrows}</table>
<p class="small" style="text-align:center;margin-top:8px">… {len(bus):,} rows in all</p></div>
<div class="row anim" style="--d:.8s;margin-top:26px;gap:16px;align-items:center;justify-content:center">
  <span class="pill" style="font-size:28px">X = bus[CHANNELS]</span><span class="pill teal" style="font-size:28px">{len(bus):,} hours × {len(w5.RAW)} channels</span>
</div>""",
          "Quiz question 3. X is just a DataFrame of numbers: one row per hour, one column per channel. No timestamps inside the "
          "numbers, no labels. Notice eclipse_flag is NOT in X today; we'll give the model context a different way."),

        # 8 ─ fit / predict
        S("""
<div class="kicker anim">Steps 2–4 · the pattern</div>
<h2 class="anim" style="--d:.1s">Make it. Fit it. Ask it.</h2>
<pre class="code anim" style="--d:.2s;font-size:26px"><span class="k">from</span> sklearn.ensemble <span class="k">import</span> IsolationForest

model = <span class="f">IsolationForest</span>(n_estimators=<span class="n">200</span>, contamination=<span class="n">0.005</span>, random_state=<span class="n">42</span>)
model.<span class="f">fit</span>(X[train])                  <span class="c"># learn what normal looks like (Jan–Aug)</span>
model.<span class="f">predict</span>(X)                     <span class="c"># -1 = odd, 1 = looks normal</span>
model.<span class="f">decision_function</span>(X)           <span class="c"># a score: LOWER = more odd</span></pre>
<div class="grid3" style="margin-top:26px;gap:22px">
  <div class="card anim a-pop" style="--d:.8s;padding:20px 24px"><h3 style="font-size:28px">🌲 n_estimators</h3><p class="small">how many random trees vote</p></div>
  <div class="card anim a-pop" style="--d:1s;padding:20px 24px"><h3 style="font-size:28px">🎚️ contamination</h3><p class="small">the share of hours you allow it to flag</p></div>
  <div class="card anim a-pop" style="--d:1.2s;padding:20px 24px"><h3 style="font-size:28px">🎲 random_state</h3><p class="small">same random cuts every run</p></div>
</div>""",
          "Quiz questions 2 and 11. fit, predict, score: the same verbs for k-means, linear regression, everything. "
          "decision_function: lower means more anomalous. We fit on the hours before 1 September (January to August) and then ask about the whole year."),

        # 9 ─ sanity + unsupervised
        S(f"""
<div class="kicker anim">Before you trust it: two checks</div>
<h2 class="anim" style="--d:.1s">It never saw the answer key. So check the count.</h2>
<div class="grid3" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="icon">🙈</div><h3>Unsupervised</h3><p class="muted">No labels in <code>fit()</code>. It only learns what is common.</p></div>
  <div class="card anim a-pop" style="--d:.55s;text-align:center"><div class="stat hl" style="font-size:84px">≈ {F['expected_flags']:.0f}</div><div class="stat-label">0.005 × {len(bus):,} hours: what you should expect</div></div>
  <div class="card anim a-pop" style="--d:.8s;text-align:center"><div class="stat good" style="font-size:84px">{n_flag}</div><div class="stat-label">what it flagged ({F['raw_all_train_flags']} in the training months) ✅</div></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:30px;text-align:center">Asked for 0.5% and got 4,000 flags? <b class="bad">Something is wrong in the code.</b> Stop and check.</p>""",
          f"Quiz questions 6, 7 and 12. contamination sets the line so that 0.5% of the TRAINING hours are flagged: "
          f"{F['raw_all_train_flags']} of {F['n_train']:,}. Over the whole year we got {n_flag}, the same ballpark as "
          f"0.005 × {len(bus):,} ≈ {F['expected_flags']:.0f}. Thousands would mean a bug (typically predict() == 1 instead of == -1)."),

        # 10 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">What did the forest find? 🔍</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Six raw channels. Fit on January–August. Look at the whole year.</p>""",
          "Section break. Ask the room to predict before you show the next slide: what will the 'oddest' hours of the year be?", cls="center"),

        # 11 ─ all eclipse
        S(f"""
<div class="kicker anim">The first forest · 6 raw channels · all hours</div>
<h2 class="anim" style="--d:.1s;font-size:54px">{n_flag} flags. <span class="hl">All {F['w4d2_raw_all_eclipse']}</span> at {hour}:00. Eclipse. 🌘</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{year_chart}</div>
<div class="anim" style="--d:2.6s;margin-top:16px"><span class="small">The 10 “oddest” hours of the year:</span><br>{top10}</div>""",
          f"Every red dot sits on the floor of the chart: array current at zero, eclipse. All {F['w4d2_raw_all_eclipse']} flags are at "
          f"{hour}:00 UTC, the eclipse hour, in the March and September seasons. The forest found the lifeguard, {n_flag} times. "
          "It's not wrong: eclipse IS the rarest thing in the file. It's just not a fault."),

        # 12 ─ lucky catch
        S(f"""
<div class="kicker anim">Score it with the Week 4 scorer</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Caught {ra['caught']} of {ra['events']}… by <span class="bad">luck</span></h2>
<div class="row" style="gap:34px;margin-top:6px;align-items:center">
  <div class="card anim a-left" style="--d:.2s;padding:16px 18px;flex:1.1"><h3 style="font-size:24px">EV04 · 3–30 Sep · every hour of the window</h3>{grid_svg(flags_all, ecl)}</div>
  <div class="col" style="flex:1;gap:18px">
    <div class="card anim a-right" style="--d:.5s;padding:20px 24px"><p><b class="bad">{int(ev04a['hours_flagged'])} of {int(ev04a['hours_long'])}</b> hours flagged, every one at <b class="hl">{hour}:00</b></p></div>
    <div class="card anim a-right" style="--d:.8s;padding:20px 24px"><p>First flag <b>{int(ev04a['hours_late'])} hours</b> after the fault began</p></div>
    <div class="card anim a-right glow" style="--d:1.1s;padding:20px 24px"><p>EV04 is an <b>amplifier</b> fault. The forest was looking at <b class="hl">eclipse</b>.</p></div>
    <p class="anim small" style="--d:1.4s">{ra['false_alarms']} false alarms outside the events. Grey = eclipse hour · red = flagged.</p>
  </div>
</div>""",
          f"The scorer says 'caught EV04'. Look WHY: EV04 lasts four weeks (672 hours) and it overlaps the September eclipse season, "
          f"so eclipse flags land inside its window. Right answer, wrong reason: like guessing C in WAEC and getting it. That's a "
          f"lucky catch. New habit from today: for a long event, look at how many of its hours lit up and at what time (event_table)."),

        # 13 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">Give it context 🌞</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Week 3, Day 1 all over again: condition on the known cause.</p>""",
          "Section break.", cls="center"),

        # 14 ─ steady sun
        S(f"""
<div class="kicker anim">Three states, three normals</div>
<h2 class="anim" style="--d:.1s">Only judge <span class="hl">steady sunlight</span></h2>
<div class="flow" style="margin-top:20px;justify-content:center">
  <div class="box anim a-pop" style="--d:.3s;min-width:300px"><div class="icon">🌘</div><h3>Eclipse</h3><p class="small">21:00 · on battery · {F['n_eclipse']} h</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box anim a-pop" style="--d:.7s;min-width:300px"><div class="icon">🔋</div><h3>Recharge</h3><p class="small">the 3 hours after · {F['n_recharge']} h</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:320px"><div class="icon">🌞</div><h3>Steady sun</h3><p class="small">everything else · {F['n_steady']:,} h</p></div>
</div>
<pre class="code anim" style="--d:1.5s;margin-top:34px"><span class="k">def</span> <span class="f">steady_sun</span>(bus):
    <span class="c"># no eclipse in this hour or the 3 before it</span>
    <span class="k">return</span> bus[<span class="s">"eclipse_flag"</span>].rolling(<span class="n">4</span>).max() == <span class="n">0</span></pre>""",
          f"NEPA takes light at 21:00 (eclipse), then the inverter charges hard for 3 hours (recharge: array current above normal, "
          f"battery warm). Both are normal, each with its own normal. Steady sun = no eclipse in this hour or the 3 before it. "
          f"{F['n_steady']:,} of {len(bus):,} hours. We fit the forest on steady training hours only, and only judge steady hours. "
          f"(Recharge hours average {F['recharge_array']:.1f} A and a {F['recharge_batt']:.1f} °C battery.)"),

        # 15 ─ forest on steady sun
        S(f"""
<div class="kicker anim">Forest · 6 raw channels · steady sun only</div>
<h2 class="anim" style="--d:.1s;font-size:54px">{rs['caught']} of {rs['events']} caught, {rs['false_alarms']} false alarms</h2>
{event_cards(rs, {"EV03": f"a {F['ev03_drop']:.0f} A drop, missed!", "EV04": f"{int(ev04s['hours_flagged'])} of {int(ev04s['hours_long'])} h · {int(ev04s['hours_late']) // 24} days late"})}
<div class="grid2" style="margin-top:22px;gap:24px">
  <div class="card anim a-left" style="--d:1.4s;padding:18px 24px"><p style="font-size:24px">📅 All {rs['false_alarms']} false alarms in <b>January</b>: the lightest load and coolest amplifier it had seen. The edge of its experience.</p></div>
  <div class="card anim a-right" style="--d:1.7s;padding:18px 24px"><p style="font-size:24px">🎲 EV04 here is one hour on {F['ev04_flag_time']:%d %b}. With random_state {" or ".join(str(s) for s in F['seeds_no_ev04'])} it's gone completely.</p></div>
</div>""",
          f"Huge improvement: no eclipse flags at all. The charge-controller faults EV02 and EV05 light up every hour. But look closely. "
          f"EV03, a blatant 11 A dropout (array current {F['chart_ev03_z']['solar_array_current_a']:.0f} sigma from normal), ranks "
          f"{F['ev03_rank']} in the forest's list and is missed. EV04 is 'caught' by one hour, {int(ev04s['hours_late'])} hours late: "
          f"practically missed. The January false alarms sit at drive {jan_z['rf_drive_pct']:+.1f} sigma and amplifier "
          f"{jan_z['twta_temp_c']:+.1f} sigma: the start of the year, the edge of what it learned. Why does it miss EV03? Each tree only "
          "cuts between the smallest and largest values in its own small sample; a sample without a dropout never cuts below normal, "
          "so the dropout rides along with the lowest normal hours."),

        # 16 ─ chart vs forest
        S(f"""
<div class="kicker anim">Same hours · same scorer · the old tool</div>
<h2 class="anim" style="--d:.1s">The Week 3 chart is <span class="hl">still</span> a good tool</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🌲</div><h3>Forest, steady sun</h3>
    <p style="font-size:30px">caught <b>{rs['caught']}/{rs['events']}</b> · <b class="bad">{rs['false_alarms']}</b> false alarms</p>
    <p class="muted" style="margin-top:10px">misses EV03, the {F['ev03_drop']:.0f} A drop</p></div>
  <div class="card anim a-right glow" style="--d:.6s"><div class="icon">📊</div><h3>3σ chart per channel, steady sun</h3>
    <p style="font-size:30px">caught <b>{cs['caught']}/{cs['events']}</b> · <b class="good">{cs['false_alarms']}</b> false alarms</p>
    <p class="muted" style="margin-top:10px">EV03 is {abs(F['chart_ev03_z']['solar_array_current_a']):.0f}σ low: impossible to miss</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:30px;text-align:center">For a single-channel spike, the simple chart can be the <b class="hl">better</b> tool. 💡<br>
<span class="small">Bonus surprise: bus voltage alone gives EV02 and EV05 away. Week 5 Day 1 comes back to this.</span></p>""",
          f"Quiz question 15 (answer: True). Both miss EV04, both catch EV02 and EV05. The chart (mean ± 3 sigma per channel, from steady "
          f"January–August hours) catches EV03 and raises {cs['false_alarms']} false alarms against the forest's {rs['false_alarms']}. "
          "New is not automatically better. The label file says EV02 and EV05 are 'not detectable with one channel'; on steady-sun hours "
          "the bus voltage alone sags far below its normal band. Keep that for the instructor discussion, not the slide."),

        # 17 ─ section
        S("""
<div class="kicker anim">Part 4</div>
<h1 class="anim" style="--d:.15s">Clustering 🧩</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Don't tell it the states. Let it find them.</p>""",
          "Section break.", cls="center"),

        # 18 ─ k-means finds the modes
        S(f"""
<div class="kicker anim">KMeans(4) · no labels, no eclipse_flag</div>
<h2 class="anim" style="--d:.1s;font-size:54px">It found eclipse and recharge <span class="hl">by itself</span></h2>
<div class="grid2" style="margin-top:6px;gap:26px">
  <div class="card anim a-left glow" style="--d:.2s;padding:18px 22px"><h3 style="font-size:26px">✅ Scaled first (StandardScaler)</h3>{state_bars_svg(km_s)}
    <p style="font-size:22px">eclipse → one cluster ({int(km_s['eclipse'].max())}/{F['n_eclipse']}) · recharge → one cluster ({int(km_s['recharge'].max())}/{F['n_recharge']})</p></div>
  <div class="card anim a-right" style="--d:.5s;padding:18px 22px"><h3 style="font-size:26px">❌ Not scaled</h3>{state_bars_svg(km_u)}
    <p style="font-size:22px">recharge smeared over {len(rech_u)} clusters ({" / ".join(str(v) for v in rech_u)})</p></div>
</div>""",
          f"Quiz question 13: clustering finds the operating modes. Colours are cluster numbers. With scaling, k-means gives eclipse its own "
          f"cluster and recharge its own cluster, without ever being told. The 3 'steady' hours it put with recharge are "
          f"{', '.join(t.strftime('%d %b %H:%M') for t in F['km_warm_steady'])}: warm-battery hours (two are the dropouts EV01 and EV03). "
          "The two steady-sun clusters split the cool start of the year from the rest. Without scaling, the channels with big numbers "
          "dominate the distance and recharge gets smeared."),

        # 19 ─ scaling
        S(f"""
<div class="kicker anim">So when does scaling matter?</div>
<h2 class="anim" style="--d:.1s">Distances care about units. Cuts don't.</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;border-color:#16A394"><div class="icon">📏</div><h3>k-means: scale it</h3>
    <p class="muted">It measures distance. In steady sun bus voltage wobbles ~{F['v_sd']:.2f} V; array current spans {ranges.loc['solar_array_current_a', 'max']:.0f} A. Unscaled, the big numbers shout loudest.</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#F5B83D"><div class="icon">🌲</div><h3>Forest: makes no difference</h3>
    <p class="muted">It cuts between min and max of each column, whatever the units. Scores with and without scaling agree: <b style="color:#fff">r = {F['if_scale_corr']:.8f}</b></p></div>
</div>
<pre class="code anim" style="--d:1s;margin-top:26px"><span class="c"># a pipeline: scaler + model travel together</span>
km = make_pipeline(StandardScaler(), KMeans(<span class="n">4</span>, n_init=<span class="n">10</span>, random_state=<span class="n">42</span>))</pre>""",
          "Quiz questions 4 and 5. A pipeline glues the scaler to the model, so the scaler fitted on the training rows is the very one "
          "used at prediction time. Honest note: the original code book says the different channel ranges are 'why we insist on scaling' "
          "for the forest. For the forest it makes no difference (quiz Q4's option 'it does not matter for isolation forest' is also true). "
          "It matters for distance methods like k-means."),

        # 20 ─ explain a flag
        S(f"""
<div class="kicker anim">“The algorithm says so” is not an answer</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Explain every flag with z-scores</h2>
{z_table(F, [(pd.Timestamp("2025-05-02 01:00"), "EV02 · charge controller"), (pd.Timestamp("2025-02-19 11:00"), "EV01 · array dropout"),
             (F["jan_first"], "January false alarm")])}
<p class="anim" style="--d:1.2s;margin-top:20px;text-align:center">z = (value − normal) ÷ normal spread, from steady Jan–Aug hours. The <b class="hl">gold</b> number is your sentence for the duty engineer.</p>""",
          f"Quiz question 14: per-channel z-scores against the training baseline are the cheapest explanation. EV02: 'state of charge "
          f"{z2['battery_soc_pct']:+.1f} sigma and bus voltage {z2['bus_voltage_v']:+.1f} sigma, in full sun.' EV01: 'array current "
          f"{z1['solar_array_current_a']:+.1f} sigma, battery {z1['battery_temp_c']:+.1f} sigma warm.' January: 'nothing broken: RF drive "
          f"{zj['rf_drive_pct']:+.1f} sigma, the lowest load it has seen.' That last one is how you dismiss a false alarm in ten seconds."),

        # 21 ─ cliffhanger EV04
        S(f"""
<div class="kicker anim">The one it can't see</div>
<h2 class="anim" style="--d:.1s;font-size:54px">EV04: hot <span class="hl">for its workload</span>, for four weeks</h2>
<div class="row" style="gap:34px;margin-top:6px;align-items:center">
  <div class="card anim a-left" style="--d:.2s;padding:16px 18px;flex:1.1"><h3 style="font-size:24px">Steady-sun forest · EV04's 672 hours</h3>{grid_svg(flags_st, ecl)}</div>
  <div class="col" style="flex:1;gap:18px">
    <div class="card anim a-right" style="--d:.5s;padding:20px 24px"><p>Amplifier peak <b>{tw_max:.1f} °C</b>, its 3σ ceiling <b>{tw_ceiling:.1f} °C</b>: <span class="good">looks fine alone</span></p></div>
    <div class="card anim a-right" style="--d:.8s;padding:20px 24px"><p>But the RF drive didn't go up. It jumped <b class="bad">~{F['ev04_jump']:.0f}&nbsp;°C</b>: hot for the work it's doing.</p></div>
    <div class="card anim a-right glow" style="--d:1.1s;padding:20px 24px"><p>The forest saw <b class="bad">{int(ev04s['hours_flagged'])}</b> hour. It has no column for “hot for its workload”.</p></div>
  </div>
</div>""",
          f"Cliffhanger for Day 3. The cooling path degraded: on 3 September the amplifier's daily mean jumped {F['ev04_jump']:.1f} °C with no rise in drive, and stayed hot, every "
          "hour for four weeks. Raw temperature never breaks its limit, because the amplifier's normal temperature swings with the "
          "seasons and with load. The model can only judge the columns we give it. Next time we give it a column that means "
          "'temperature per unit of work': we give the model eyes."),

        # 22 ─ your turn
        S(f"""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Train your first model</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open <b class="hl">W4D2-exercise</b>, save a copy, run STEP 0</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">A</span><p>X, fit, predict: your first forest</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">B</span><p>What did it find? Score it, spot the luck</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">C</span><p>Steady sun: forest vs the Week 3 chart</p></div>
   <div class="row anim" style="--d:1.1s;gap:18px;align-items:center"><span class="num">D</span><p>k-means finds the modes; explain a flag</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.3s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🌲</div>
  <h3 style="margin-top:16px">{n_checks} checks to pass</h3>
  <p class="muted">🌶️ Pepper task: turn the contamination dial until only the surest faults remain</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Common snags: predict() returns -1 for odd (not True); forgetting '& steady' when fitting; KMeans without the scaler. "
          "If a forest number is off by one or two from a neighbour's, check random_state and the scikit-learn version first."),

        # 23 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🧰</span><p><b>fit · predict · score.</b> X = hours × channels. One pattern for every scikit-learn model.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🛟</span><p><b>Rare is not broken.</b> Give the model context (steady sun) and check <b class="hl">why</b> it flagged.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">📊</span><p><b>Old tools still win</b> some fights: the chart caught the spike the forest missed.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:34px;font-size:30px">Next time 👉 <b class="hl">Give the model eyes</b>: one new column makes EV04 light up. 👀</p>""",
          "Recap. Tease W4D3: feature engineering. One column, temperature per unit of drive, turns EV04 from invisible to obvious."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    F = facts()
    ra, rs, cs = F["w4d2_raw_all"], F["w4d2_raw_steady"], F["chart_raw_steady"]
    _, _, _, a_cuts, g_cuts = _beach()
    hour = max(F["w4d2_raw_all_hours"], key=F["w4d2_raw_all_hours"].get)
    ev04a, ev04s = ra["table"].loc["EV04"], rs["table"].loc["EV04"]
    km_s, km_u = F["kmeans_scaled"], F["kmeans_unscaled"]
    z = F["z6"]

    def zrow(t, lab):
        return [lab] + [f"{z.loc[t, c]:+.1f}" for c in w5.RAW]

    def ev_row(e, r):
        row = r["table"].loc[e]
        return "✅" if row["caught"] else "❌"
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🌲", "kicker": "Week 4 · Day 2", "title": "Meet scikit-learn\n+ Isolation Forest",
             "sub": "Your first machine-learning detector: six channels at once",
             "notes": "Today participants train their first model."},
            {"type": "flow", "title": "Today's mission", "steps": [
                ["🧰", "fit · predict", "the scikit-learn pattern"], ["🌲", "Isolation forest", "six channels at once"],
                ["🌞", "Add context", "the Week 3 lesson again"], ["🧩", "Clustering", "the data finds its modes"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up", "notes": "Rare is not the same as broken."},
            {"type": "compare", "title": "Spot the man in agbada at a beach party",
             "left": ["🧥", f"The man in agbada: {len(a_cuts)} cut{'s' if len(a_cuts) != 1 else ''}",
                      "Random cuts isolate the odd one out almost at once"],
             "right": ["🩳", f"A guest in shorts: {len(g_cuts)} cuts", "Someone in the crowd takes many cuts to get alone"],
             "notes": "Few cuts = odd. 200 random trees vote. That's the isolation forest."},
            {"type": "compare", "title": "The twist: the lifeguard also stands out",
             "left": ["🧥", "Agbada at the beach", "Rare and out of place: a fault"],
             "right": ["🛟", "The lifeguard", "Just as rare, but he belongs there: eclipse"],
             "notes": "A forest finds what is rare. Rare is not the same as broken."},
            {"type": "code", "title": "scikit-learn in 3 verbs",
             "code": "X = bus[CHANNELS]            # rows = hours, columns = channels\n"
                     "model = IsolationForest(n_estimators=200,\n                        contamination=0.005, random_state=42)\n"
                     "model.fit(X[train])           # learn normal (Jan–Aug)\n"
                     "model.predict(X)              # -1 = odd, 1 = normal\n"
                     "model.decision_function(X)    # lower = more odd",
             "caption": "The same pattern works for every model in the library", "notes": "Quiz questions 2, 3, 11."},
            {"type": "stats", "title": "It never saw the labels, so check the count", "sub": "contamination = the share of hours you allow it to flag",
             "stats": [["≈ " + f"{F['expected_flags']:.0f}", f"expected: 0.005 × {F['n_rows']:,} hours"],
                       [str(F["w4d2_raw_all_n"]), f"flagged over the year ({F['raw_all_train_flags']} in training)"],
                       ["4,000?", "a bug: stop and check the code"]],
             "notes": "Quiz questions 6, 7, 12."},
            {"type": "section", "kicker": "Part 2", "title": "What did the forest find?", "sub": "Six raw channels, fit on Jan–Aug", "notes": "Ask for predictions."},
            {"type": "statement", "title": "The first forest", "icon": "🌘",
             "big": f"{F['w4d2_raw_all_n']} flags. All {F['w4d2_raw_all_eclipse']} at {hour}:00. Eclipse.",
             "sub": "It found the lifeguard: the rarest thing in the file is normal physics",
             "notes": "Rare is not broken."},
            {"type": "stats", "title": f"Caught {ra['caught']} of {ra['events']}, by luck", "sub": "EV04 is an amplifier fault; the forest was looking at eclipse",
             "stats": [[f"{int(ev04a['hours_flagged'])}/{int(ev04a['hours_long'])}", f"EV04 hours flagged, all at {hour}:00"],
                       [f"{int(ev04a['hours_late'])} h", "late for its first flag"],
                       [str(ra["false_alarms"]), "false alarms outside the events"]],
             "notes": "A lucky catch: right answer, wrong reason. Check how many hours of a long event lit up, and when."},
            {"type": "section", "kicker": "Part 3", "title": "Give it context", "sub": "Only judge steady sunlight", "notes": "Week 3 lesson again."},
            {"type": "flow", "title": "Three states, three normals", "steps": [
                ["🌘", "Eclipse", f"21:00 · on battery · {F['n_eclipse']} h"], ["🔋", "Recharge", f"3 hours after · {F['n_recharge']} h"],
                ["🌞", "Steady sun", f"everything else · {F['n_steady']:,} h"]],
             "footer": 'steady = bus["eclipse_flag"].rolling(4).max() == 0', "notes": "No eclipse this hour or the 3 before."},
            {"type": "table", "title": f"Steady-sun forest: {rs['caught']} of {rs['events']}, {rs['false_alarms']} false alarms",
             "header": ["Detector (steady sun)", "EV01", "EV02", "EV03", "EV04", "EV05", "False alarms"],
             "rows": [["Isolation forest, 6 channels"] + [ev_row(e, rs) for e in rs["table"].index] + [rs["false_alarms"]],
                      ["3σ chart per channel"] + [ev_row(e, cs) for e in cs["table"].index] + [cs["false_alarms"]]],
             "colW": [4.0, 1.2, 1.2, 1.2, 1.2, 1.2, 2.13],
             "caption": f"The forest's EV04 is 1 hour, {int(ev04s['hours_late'])} h late. The chart catches EV03, the {F['ev03_drop']:.0f} A drop.",
             "notes": "Quiz question 15: for single-channel spikes the chart can be the better tool."},
            {"type": "section", "kicker": "Part 4", "title": "Clustering", "sub": "Let the data find its modes", "notes": "Section break."},
            {"type": "compare", "title": "KMeans(4) finds eclipse and recharge by itself",
             "left": ["✅", "Scaled first", f"Eclipse: one cluster ({int(km_s['eclipse'].max())}/{F['n_eclipse']}). "
                                           f"Recharge: one cluster ({int(km_s['recharge'].max())}/{F['n_recharge']})"],
             "right": ["❌", "Not scaled", "Recharge smeared over " + str(int((km_u['recharge'] > 0).sum())) + " clusters: big numbers dominate"],
             "notes": f"Quiz questions 4, 5, 13. The forest doesn't care about scaling (r = {F['if_scale_corr']:.8f})."},
            {"type": "table", "title": "Explain every flag with z-scores",
             "header": ["Hour"] + [SHORT[c] for c in w5.RAW],
             "rows": [zrow(pd.Timestamp("2025-05-02 01:00"), "EV02 · 2 May 01:00"), zrow(pd.Timestamp("2025-02-19 11:00"), "EV01 · 19 Feb 11:00"),
                      zrow(F["jan_first"], f"January false alarm · {F['jan_first']:%d %b %H:%M}")],
             "colW": [3.9, 1.4, 1.4, 1.4, 1.4, 1.4, 1.43],
             "caption": "z = (value − normal) ÷ spread, from steady Jan–Aug hours. The biggest number is your explanation.",
             "notes": "Quiz question 14."},
            {"type": "statement", "title": "The one it can't see", "icon": "🌡️",
             "big": f"EV04: amplifier peak {F['twta_ev04_max']:.1f} °C vs ceiling {F['twta_ceiling']:.1f} °C, yet ~{F['ev04_jump']:.0f} °C hot for its drive",
             "sub": f"The forest saw {int(ev04s['hours_flagged'])} of {int(ev04s['hours_long'])} hours. It has no column for “hot for its workload”.",
             "notes": "Next time: give the model eyes."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W4D2-exercise, save a copy, run STEP 0", "Parts A + B: fit a forest, score it, spot the lucky catch",
                "Part C: steady sun, forest vs chart", "Part D: k-means and explaining a flag"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🧰", "fit · predict · score: one pattern for every scikit-learn model"],
                ["🛟", "Rare is not broken: add context and check why it flagged"],
                ["📊", "Old tools still win some fights"]],
             "next": "Next: Give the model eyes (feature engineering)", "notes": "Tease W4D3."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
def _checks() -> str:
    F = facts()
    ra, rs, cs = F["w4d2_raw_all"], F["w4d2_raw_steady"], F["chart_raw_steady"]
    hour = max(F["w4d2_raw_all_hours"], key=F["w4d2_raw_all_hours"].get)
    ev04a = ra["table"].loc["EV04"]
    km = F["kmeans_scaled"]
    pep = F["pepper"]
    loud = F["z6"].loc["2025-05-02 01:00"].abs().idxmax()
    return f'''
def _near(x, want, tol):
    return abs(float(x) - want) <= tol

def _res(x, caught, fa, tol=0):
    return isinstance(x, dict) and x.get("caught") == caught and abs(x.get("false_alarms", -999) - fa) <= tol

def _c_a1(x):
    return tuple(x) == ({F["n_rows"]}, {len(w5.RAW)}), \\
        "{F['n_rows']:,} rows (hours) × {len(w5.RAW)} columns (channels). That's X. 🧮", \\
        "Pick the six channel columns out of bus: bus[CHANNELS]"

def _c_a2(x):
    return int(x) == {F["n_train"]}, "{F['n_train']:,} training hours: 1 January to 31 August. The forest learns 'normal' from these.", \\
        "Every hour BEFORE 1 September: TRAIN_END = \\"2025-09-01\\""

def _c_a3(x):
    return getattr(x, "contamination", None) == {w5.CONTAMINATION} and hasattr(x, "offset_"), \\
        "Forest trained: 200 random trees, allowed to flag 0.5% of hours. 🌲", \\
        "0.5% written as a fraction is 0.005. Then run the cell so model.fit() happens."

def _c_a4(x):
    return _near(x, {F["expected_flags"]:.3f}, 0.6), "About {F['expected_flags']:.0f} hours. Remember that number: it's your sanity check. ✅", \\
        "contamination × number of hours: CONTAMINATION * len(X)"

def _c_a5(x):
    return _near(x, {F["w4d2_raw_all_n"]}, 5), \\
        "{F['w4d2_raw_all_n']} flags: the same ballpark as {F['expected_flags']:.0f}. If you had thousands, you'd know something was wrong.", \\
        "predict() says -1 for odd and 1 for normal. Which one is a flag? (Thousands of flags = you picked the wrong one.)"

def _c_b1(x):
    return int(x) == {hour}, "{hour}:00 UTC: eclipse time, every single flag. 🌘 The forest found the lifeguard.", \\
        "Read the top of the value_counts() output: which hour of the day appears?"

def _c_b2(x):
    return _res(x, {ra["caught"]}, {ra["false_alarms"]}, 5), \\
        "Caught {ra['caught']} of {ra['events']}... Before you celebrate, look at WHICH event and WHEN in the next cell.", \\
        "Score the forest's True/False flags: my_flags = flags_all"

def _c_b3(x):
    return x is False or str(x).strip().lower() == "false", \\
        "Correct: a lucky catch. EV04 is an amplifier fault; every flag inside it was an eclipse hour. Right answer, wrong reason.", \\
        "Look at the hours flagged inside EV04: all at {hour}:00. Is that the amplifier?"

def _c_c1(x):
    return int(x) == 4, "4 hours: this one and the 3 before it. Eclipse + 3 recharge hours are now 'not judged'. 🌞", \\
        "Eclipse is one hour (21:00) and recharge is the next 3 (22, 23, 00). This hour + the 3 before = ?"

def _c_c2(x):
    return _res(x, {rs["caught"]}, {rs["false_alarms"]}, 5), \\
        "{rs['caught']} of {rs['events']}, {rs['false_alarms']} false alarms, no eclipse flags. Big improvement. Now read the event table below. 👇", \\
        "Fit on rows that are training AND steady sun: FIT_ROWS = train & steady"

def _c_c3(x):
    return _res(x, {cs["caught"]}, {cs["false_alarms"]}), \\
        "{cs['caught']} of {cs['events']} with only {cs['false_alarms']} false alarms, and it catches EV03. The old tool still bites. 📊", \\
        "The classic control chart: K = 3"

def _c_c4(x):
    return "chart" in str(x).strip().lower(), "The chart! EV03's array current is {abs(F['chart_ev03_z']['solar_array_current_a']):.0f}σ low. A spike in ONE channel is the chart's home ground.", \\
        "Compare the two event tables: which one has EV03 = True? Answer \\"chart\\" or \\"forest\\"."

def _c_d1(x):
    return int(x["eclipse"].max()) == {int(km["eclipse"].max())} and int(x["recharge"].max()) == {int(km["recharge"].max())}, \\
        "Eclipse got its own cluster ({int(km['eclipse'].max())}/{F['n_eclipse']}) and so did recharge ({int(km['recharge'].max())}/{F['n_recharge']}). Nobody told it. 🧩", \\
        "k-means measures distance, so scale first: SCALER = StandardScaler()"

def _c_d2(x):
    return str(x).strip() == "{loud}", "{loud}: state of charge {F['z6'].loc['2025-05-02 01:00', loud]:+.1f}σ in full sun. That's the sentence for the duty engineer.", \\
        "Find the number furthest from zero (ignore the sign) and copy its column name, in quotes."

def _c_bonus(x):
    return isinstance(x, dict) and x.get("caught", 0) >= 2 and x.get("false_alarms", 99) <= 3, \\
        "Strict and sure: only the battery-not-charging faults survive. The forest's most confident finds are EV02 and EV05. 🌶️🏆", \\
        "Make contamination smaller (e.g. 0.002) until false alarms are 3 or fewer, while still catching 2 events."

CHECKS = {{"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "A5": _c_a5, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3,
          "C1": _c_c1, "C2": _c_c2, "C3": _c_c3, "C4": _c_c4, "D1": _c_d1, "D2": _c_d2, "BONUS": _c_bonus}}
HINTS = {{"D1": "Pass the crosstab table itself."}}
'''


CHECKS = _checks()              # the answers come from the data, like every number on the slides


def _steady_code() -> str:
    """steady_sun() exactly as the shared detector code defines it."""
    return "def steady_sun" + w5.DETECTOR_CODE.split("def steady_sun", 1)[1].split("\n\ndef ", 1)[0]


def notebook_cells(setup_code):
    F = facts()
    return [
        ("md", """# 🌲 Week 4 · Day 2: Meet scikit-learn + Isolation Forest

**Today:** you train your first machine-learning model. It looks at **six channels at once** and points at the hours that are hardest to explain. Then you check *why* it pointed, because rare is not the same as broken.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**

**Rule book:** keep `W4D2-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up
Run it once every time you open the notebook (and after every restart). Wait for `✅ Ready!`."""),
        ("setup", setup_code),
        ("md", """▶️ Load a full year of hourly telemetry (six channels + the eclipse flag), the answer key, and the scikit-learn tools.
Colab already has scikit-learn installed."""),
        ("code", 'bus = pd.read_csv(data_path("bus_telemetry_multivariate_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n'
                 'labels = load_labels("anomaly_labels_week5")\n\n'
                 'from sklearn.ensemble import IsolationForest\nfrom sklearn.cluster import KMeans\n'
                 'from sklearn.preprocessing import StandardScaler\nfrom sklearn.pipeline import make_pipeline\nimport sklearn\n\n'
                 'print("hours:", len(bus), "· eclipse hours:", int(bus["eclipse_flag"].sum()), "· scikit-learn", sklearn.__version__)\n'
                 'display(labels[["event_id", "start", "end", "type", "channels_involved"]])'),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Your first forest (15 min) 🧰

scikit-learn always works the same way: **build X → make a model → `fit` → `predict`**.

### A1 ✍️ Build X
X is a table of numbers: **one row per hour, one column per channel**. Pick the six channels out of `bus`."""),
        ("task", 'CHANNELS = ["solar_array_current_a", "bus_voltage_v", "battery_soc_pct",\n            "battery_temp_c", "twta_temp_c", "rf_drive_pct"]\n\nX = ___\n\nassert X is not None, "✍️ Fill in X first, then run this cell again."\nprint(X.shape)\ncheck("A1", X.shape)',
         'CHANNELS = ["solar_array_current_a", "bus_voltage_v", "battery_soc_pct",\n            "battery_temp_c", "twta_temp_c", "rf_drive_pct"]\n\nX = bus[CHANNELS]\n\nassert X is not None, "✍️ Fill in X first, then run this cell again."\nprint(X.shape)\ncheck("A1", X.shape)'),
        ("md", """### A2 ✍️ The months it learns from
The forest learns what "normal" looks like from **January to August**: every hour *before* 1 September. Write that date as text, like `"2025-01-31"`."""),
        ("task", 'TRAIN_END = ___\n\nassert TRAIN_END is not None, "✍️ Fill in TRAIN_END first."\ntrain = bus.index < TRAIN_END\nprint("training hours:", train.sum(), "· from", bus.index[train][0], "to", bus.index[train][-1])\ncheck("A2", int(train.sum()))',
         'TRAIN_END = "2025-09-01"\n\nassert TRAIN_END is not None, "✍️ Fill in TRAIN_END first."\ntrain = bus.index < TRAIN_END\nprint("training hours:", train.sum(), "· from", bus.index[train][0], "to", bus.index[train][-1])\ncheck("A2", int(train.sum()))'),
        ("md", """### A3 ✍️ Make the model and fit it
`contamination` is the share of hours you **allow** it to flag. We allow **0.5%**. Write it as a fraction.
`random_state=42` makes the random trees the same every time you run it (and the same as your neighbour's)."""),
        ("task", 'CONTAMINATION = ___\n\nassert CONTAMINATION is not None, "✍️ Fill in CONTAMINATION first."\nmodel = IsolationForest(n_estimators=200, contamination=CONTAMINATION, random_state=42)\nmodel.fit(X[train])          # no labels here: it only learns what is common\ncheck("A3", model)',
         'CONTAMINATION = 0.005\n\nassert CONTAMINATION is not None, "✍️ Fill in CONTAMINATION first."\nmodel = IsolationForest(n_estimators=200, contamination=CONTAMINATION, random_state=42)\nmodel.fit(X[train])          # no labels here: it only learns what is common\ncheck("A3", model)'),
        ("md", """### A4 ✍️ Sanity check BEFORE you look
If you allow 0.5% of the year's hours, about how many flags should you expect? (Work it out from `CONTAMINATION` and `len(X)`.)"""),
        ("task", 'expected_flags = ___\n\nprint("expect about", expected_flags, "flags")\ncheck("A4", expected_flags)',
         'expected_flags = CONTAMINATION * len(X)\n\nprint("expect about", expected_flags, "flags")\ncheck("A4", expected_flags)'),
        ("md", """### A5 ✍️ Ask it: which hours look odd?
`model.predict(X)` gives **1** for "looks normal" and **-1** for "looks odd". Which value is a flag?"""),
        ("task", 'pred = model.predict(X)\nprint(pd.Series(pred).value_counts())\n\nODD = ___\n\nassert ODD is not None, "✍️ Fill in ODD first."\nflags_all = pd.Series(pred == ODD, index=X.index)\nprint("flagged hours:", flags_all.sum(), "· expected about", round(expected_flags))\ncheck("A5", int(flags_all.sum()))',
         'pred = model.predict(X)\nprint(pd.Series(pred).value_counts())\n\nODD = -1\n\nassert ODD is not None, "✍️ Fill in ODD first."\nflags_all = pd.Series(pred == ODD, index=X.index)\nprint("flagged hours:", flags_all.sum(), "· expected about", round(expected_flags))\ncheck("A5", int(flags_all.sum()))'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: What did it find? (15 min) 🔍

▶️ `decision_function` gives every hour a score. **Lower = more odd.** Here are the ten oddest hours of the year."""),
        ("code", 'score = pd.Series(model.decision_function(X), index=X.index)\nscore.nsmallest(10)'),
        ("md", """### B1 ✍️ What hour of the day are the flags?
▶️ The cell counts the flags by hour of day. Type the hour you see (a number, e.g. `9`)."""),
        ("task", 'print(flags_all[flags_all].index.hour.value_counts())\n\nflag_hour = ___\n\ncheck("B1", flag_hour)',
         f'print(flags_all[flags_all].index.hour.value_counts())\n\nflag_hour = {max(F["w4d2_raw_all_hours"], key=F["w4d2_raw_all_hours"].get)}\n\ncheck("B1", flag_hour)'),
        ("md", """▶️ The **scorer** from Week 4 Day 1, with one extra helper. `score_events` uses the same 4 rules. `event_table` shows, for each event: caught or not, how many hours late the first flag was, and how many of the event's hours lit up."""),
        ("code", w5.SCORER_CODE + '\n\nprint("✅ score_events() and event_table() are ready")'),
        ("md", """### B2 ✍️ Score the forest
Which Series holds the forest's True/False flags?"""),
        ("task", 'my_flags = ___\n\nassert my_flags is not None, "✍️ Fill in my_flags first."\nresult_all = score_events(my_flags, labels)\nprint(result_all)\ncheck("B2", result_all)',
         'my_flags = flags_all\n\nassert my_flags is not None, "✍️ Fill in my_flags first."\nresult_all = score_events(my_flags, labels)\nprint(result_all)\ncheck("B2", result_all)'),
        ("md", """▶️ Before you celebrate: **which** event, and **when**? EV04 lasts four weeks. Look at what time of day its flags were."""),
        ("code", 'display(event_table(flags_all, labels))\n\nin_ev04 = flags_all & (bus.index >= "2025-09-03") & (bus.index < "2025-10-01")\nprint("EV04 flags by hour of day:", in_ev04[in_ev04].index.hour.value_counts().to_dict())'),
        ("md", """### B3 ✍️ Real catch or lucky catch?
EV04 is an **amplifier** fault (cooling path). Every flag inside it came at eclipse time. Did the forest really see the amplifier problem? Answer `True` or `False` (no quotes)."""),
        ("task", 'ev04_is_a_real_catch = ___\n\ncheck("B3", ev04_is_a_real_catch)', 'ev04_is_a_real_catch = False\n\ncheck("B3", ev04_is_a_real_catch)'),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Give it context (15 min) 🌞

Eclipse (21:00) and the **3 recharge hours** after it are normal states with their own normal: NEPA takes light, then the inverter charges hard.
So we only fit on, and only judge, **steady sunlight**: no eclipse in this hour **or the 3 hours before it**.

### C1 ✍️ How long is the window?
This hour plus the 3 before it is a window of how many hours?"""),
        ("task", 'window_hours = ___\n\ncheck("C1", window_hours)', 'window_hours = 4\n\ncheck("C1", window_hours)'),
        ("md", "▶️ Here is the function. `rolling(4).max() == 0` means: the biggest eclipse_flag in the last 4 hours is 0, so no eclipse at all."),
        ("code", _steady_code() + '\n\nsteady = steady_sun(bus)\n'
                 'print("steady-sun hours:", steady.sum(), "· not judged:", (~steady).sum(), "(eclipse, recharge and the first 3 hours of the file)")'),
        ("md", """### C2 ✍️ The forest, steady sun only
Fit on rows that are **training AND steady sun** (`&` means "and"). Then keep only the flags in steady sun."""),
        ("task", 'model2 = IsolationForest(n_estimators=200, contamination=0.005, random_state=42)\n\nFIT_ROWS = ___\n\nassert FIT_ROWS is not None, "✍️ Fill in FIT_ROWS first."\nmodel2.fit(X[FIT_ROWS])\nflags_steady = pd.Series(model2.predict(X) == -1, index=X.index) & steady\nresult_steady = score_events(flags_steady, labels)\nprint(result_steady)\ncheck("C2", result_steady)',
         'model2 = IsolationForest(n_estimators=200, contamination=0.005, random_state=42)\n\nFIT_ROWS = train & steady\n\nassert FIT_ROWS is not None, "✍️ Fill in FIT_ROWS first."\nmodel2.fit(X[FIT_ROWS])\nflags_steady = pd.Series(model2.predict(X) == -1, index=X.index) & steady\nresult_steady = score_events(flags_steady, labels)\nprint(result_steady)\ncheck("C2", result_steady)'),
        ("md", "▶️ Read the event table carefully: which one did it miss, and how late was EV04? Then: in which months are the false alarms?"),
        ("code", 'display(event_table(flags_steady, labels))\n\n'
                 'inside = pd.Series(False, index=bus.index)\nfor _, ev in labels.iterrows():\n'
                 '    inside |= (bus.index >= ev["start"] - pd.Timedelta("1h")) & (bus.index <= ev["end"] + pd.Timedelta("1h"))\n'
                 'false_alarms = flags_steady & ~inside\nprint("false alarms by month:", false_alarms[false_alarms].index.month.value_counts().sort_index().to_dict())'),
        ("md", """### C3 ✍️ The Week 3 control chart on the same hours
Same hours, same scorer, the old tool: mean ± **K** standard deviations per channel, from steady training hours. Use the classic **K**."""),
        ("task", 'HEALTH = ["solar_array_current_a", "bus_voltage_v", "battery_soc_pct", "battery_temp_c", "twta_temp_c"]\nref = bus.loc[train & steady, HEALTH]\nz = (bus[HEALTH] - ref.mean()) / ref.std()\n\nK = ___\n\nassert K is not None, "✍️ Fill in K first."\nchart_steady = (z.abs() > K).any(axis=1) & steady\nresult_chart = score_events(chart_steady, labels)\nprint(result_chart)\ndisplay(event_table(chart_steady, labels))\ncheck("C3", result_chart)',
         'HEALTH = ["solar_array_current_a", "bus_voltage_v", "battery_soc_pct", "battery_temp_c", "twta_temp_c"]\nref = bus.loc[train & steady, HEALTH]\nz = (bus[HEALTH] - ref.mean()) / ref.std()\n\nK = 3\n\nassert K is not None, "✍️ Fill in K first."\nchart_steady = (z.abs() > K).any(axis=1) & steady\nresult_chart = score_events(chart_steady, labels)\nprint(result_chart)\ndisplay(event_table(chart_steady, labels))\ncheck("C3", result_chart)'),
        ("md", f"""### C4 ✍️ Who caught EV03?
EV03 is a {F['ev03_drop']:.0f} A drop in array current for one hour. Which detector caught it: `"forest"` or `"chart"`?"""),
        ("task", 'catches_ev03 = ___\n\ncheck("C4", catches_ev03)', 'catches_ev03 = "chart"\n\ncheck("C4", catches_ev03)'),

        # ---------------- PART D ----------------
        ("md", """---
# Part D: Clustering, and explaining a flag (10 min) 🧩

▶️ First, the **true** state of every hour (we only use it to *check* the clusters, never to make them)."""),
        ("code", 'state = pd.Series(np.select([bus["eclipse_flag"] == 1, bus["eclipse_flag"].shift(1).rolling(3).max() == 1],\n'
                 '                             ["eclipse", "recharge"], "steady sun"), index=bus.index)\nstate.value_counts()'),
        ("md", """### D1 ✍️ Let k-means find the modes
k-means groups hours that are **close** to each other. Distance cares about units, so put a scaler in front of it. Which scikit-learn tool turns every column into "standard deviations from its mean"?"""),
        ("task", 'SCALER = ___\n\nassert SCALER is not None, "✍️ Fill in SCALER first."\nkm = make_pipeline(SCALER, KMeans(4, n_init=10, random_state=42))\ncluster = km.fit_predict(X)\ntable = pd.crosstab(cluster, state)\ndisplay(table)\ncheck("D1", table)',
         'SCALER = StandardScaler()\n\nassert SCALER is not None, "✍️ Fill in SCALER first."\nkm = make_pipeline(SCALER, KMeans(4, n_init=10, random_state=42))\ncluster = km.fit_predict(X)\ntable = pd.crosstab(cluster, state)\ndisplay(table)\ncheck("D1", table)'),
        ("md", "▶️ The same k-means **without** the scaler. Where did the recharge hours go?"),
        ("code", 'pd.crosstab(KMeans(4, n_init=10, random_state=42).fit_predict(X), state)'),
        ("md", """### D2 ✍️ Explain a flag
A score with no reason won't survive the duty engineer. ▶️ The cell shows each channel's **z-score** (how many standard deviations from steady training normal) for the first hour of EV02.
Which channel is furthest from normal? Copy its name, in quotes."""),
        ("task", 'ref6 = bus.loc[train & steady, CHANNELS]\nz6 = (bus[CHANNELS] - ref6.mean()) / ref6.std()\nprint(z6.loc["2025-05-02 01:00"].round(1))\n\nloudest_channel = ___\n\ncheck("D2", loudest_channel)',
         f'ref6 = bus.loc[train & steady, CHANNELS]\nz6 = (bus[CHANNELS] - ref6.mean()) / ref6.std()\nprint(z6.loc["2025-05-02 01:00"].round(1))\n\nloudest_channel = "{F["z6"].loc["2025-05-02 01:00"].abs().idxmax()}"\n\ncheck("D2", loudest_channel)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: turn the dial
`contamination` is a dial. Turn it **down** and the forest only flags what it is surest about.
✍️ Find a contamination that keeps **3 or fewer** false alarms while still catching **at least 2** events (steady sun, same as C2). Which events survive?"""),
        ("task", 'PEPPER_CONTAMINATION = ___\n\nassert PEPPER_CONTAMINATION is not None, "✍️ Pick PEPPER_CONTAMINATION first."\nm = IsolationForest(n_estimators=200, contamination=PEPPER_CONTAMINATION, random_state=42).fit(X[train & steady])\npepper_flags = pd.Series(m.predict(X) == -1, index=X.index) & steady\npepper_result = score_events(pepper_flags, labels)\nprint(pepper_result)\ndisplay(event_table(pepper_flags, labels))\ncheck("BONUS", pepper_result)',
         'PEPPER_CONTAMINATION = 0.002\n\nassert PEPPER_CONTAMINATION is not None, "✍️ Pick PEPPER_CONTAMINATION first."\nm = IsolationForest(n_estimators=200, contamination=PEPPER_CONTAMINATION, random_state=42).fit(X[train & steady])\npepper_flags = pd.Series(m.predict(X) == -1, index=X.index) & steady\npepper_result = score_events(pepper_flags, labels)\nprint(pepper_result)\ndisplay(event_table(pepper_flags, labels))\ncheck("BONUS", pepper_result)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- **scikit-learn in 3 verbs:** build X (rows = hours, columns = channels) → `fit` → `predict` / `decision_function` (lower = more odd).
- **Sanity-check the count:** contamination 0.5% of ~8,760 hours ≈ 44 flags. Thousands = a bug.
- **Rare is not broken:** the raw forest flagged only eclipse hours. Its one "catch" was luck. Always check *which* hours and *why*.
- **Context first:** fitting and judging steady sunlight only removed every eclipse flag.
- **The old chart still wins some fights:** it caught EV03, the single-channel spike the forest missed.
- **k-means finds operating modes**, but only after scaling. The forest doesn't care about scaling.
- **Explain every flag** with z-scores: the biggest one is your sentence for the duty engineer.

**Next time:** *Give the model eyes*: one new column makes EV04 light up. 👀

<sub>Data: synthetic teaching dataset from the original Week 5 code book (`Time-series/week-05`). Safe to use with AI tools; real NIGCOMSAT data is not.</sub>"""),
    ]
