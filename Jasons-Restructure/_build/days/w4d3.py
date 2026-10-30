"""Week 4 · Day 3: Give the Model Eyes: Feature Engineering (+ final-project Checkpoint 3)."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

import w5detector as w5
from common import BRAND as B
from svgcharts import _scale
from webdeck import logos_title_block

CODE = "W4D3"
TITLE = "Give the Model Eyes: Feature Engineering"

GRID, AXIS = "#24384F", "#9DB0C6"
RED, GOLD, GREEN = "#FF6B6F", "#F5B83D", "#3CCB7F"
NICE = {"solar_array_current_a": "array current", "bus_voltage_v": "bus voltage", "battery_soc_pct": "state of charge",
        "battery_temp_c": "battery temp", "temp_per_drive": "temp_per_drive"}


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# =============================================================================
# DATA: everything comes from the shared Week 5 detector module (plus a few views of it)
# =============================================================================
@lru_cache(maxsize=1)
def facts():
    F = dict(w5.facts())
    bus, labels, idx = F["bus"], F["labels"], F["bus"].index
    train, steady, ecl = F["train"], F["steady"], F["ecl"]

    # the hook: EV02 on 2 May
    arr = bus.loc[train & ~ecl, "solar_array_current_a"]
    F["arr_lo"], F["arr_hi"] = arr.mean() - 3 * arr.std(), arr.mean() + 3 * arr.std()
    soc = bus["battery_soc_pct"]
    F["soc9294_night"] = int((soc.between(92, 94) & ~steady).sum())
    F["soc9294_steady"] = int((soc.between(92, 94) & steady).sum())
    F["soc9294_steady_in_events"] = int((soc.between(92, 94) & steady & w5._inside(labels, idx)).sum())

    # the original 32-column builder: rows lost to the longest window
    F["sink_cols"] = F["sink_shape"][1]
    F["sink_rows"] = F["sink_shape"][0]

    # the code book's regression residual, hour by hour (same recipe as w5detector)
    from sklearn.linear_model import LinearRegression
    tw = bus["twta_temp_c"]
    doy = idx.day_of_year
    design = pd.DataFrame({"drive": bus["rf_drive_pct"], "sin": np.sin(2 * np.pi * doy / 365),
                           "cos": np.cos(2 * np.pi * doy / 365)}, index=idx)
    fit = idx < "2025-06-01"
    resid = tw - LinearRegression().fit(design[fit], tw[fit]).predict(design)
    assert abs(resid[fit].std() - F["resid_sd"]) < 1e-12
    F["resid"], F["resid_mean_fit"] = resid, resid[fit].mean()

    # temp_per_drive as the notebook computes it (reference = all training hours)
    tpd = tw / bus["rf_drive_pct"]
    F["tpd"] = tpd
    ref = tpd[train]
    F["tpd_nb_mean"], F["tpd_nb_sd"] = ref.mean(), ref.std()

    # why did the lean forest flag each event? median z of its flagged hours
    z, ff = F["lean_z"], F["lean_forest_flags"]
    reasons = {}
    for _, ev in labels.iterrows():
        sel = ff & (idx >= ev["start"]) & (idx <= ev["end"])
        med = z[sel].median()
        top = med.abs().sort_values(ascending=False)
        reasons[ev["event_id"]] = {"n": int(sel.sum()), "winner": z[sel].abs().idxmax(axis=1).value_counts().index[0],
                                   "top": [(c, med[c]) for c in top.index[:2] if abs(med[c]) >= 3]}
    F["reasons"] = reasons
    fa = ff & ~w5._inside(labels, idx)
    F["lean_fa_reason"] = z[fa].abs().idxmax(axis=1).value_counts().to_dict()
    F["lean_fa_months"] = fa[fa].index.month.value_counts().sort_index().to_dict()
    F["chart_lean_year"] = F["fight_year"]["Week 4 chart, lean features, steady sun"]
    return F


# =============================================================================
# LOCAL SVG HELPERS
# =============================================================================
def chart_svg(values, *, w=1400, h=420, ymin=None, ymax=None, color=B["blue_d"], band=None, hlines=(),
              xlabels=(), yticks=(), spans=(), stroke=2.2, delay=".3s", dur="2.4s", band_lab_at=None):
    """Full-resolution line. band=(lo, hi, colour, label) · hlines=[(y, label, colour, 'left'?)] ·
    spans=[(i0, i1, colour, label)] shaded time windows · xlabels=[(i, text)] · yticks=[(y, text)]"""
    v = np.asarray(values, dtype=float)
    n = len(v)
    lo = np.nanmin(v) if ymin is None else ymin
    hi = np.nanmax(v) if ymax is None else ymax
    L, R, T, Bm = 96, w - 24, 26, h - 56

    def X(i):
        return _scale(i, 0, n - 1, L, R)

    def Y(y):
        return _scale(y, lo, hi, Bm, T)

    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block" xmlns="http://www.w3.org/2000/svg">']
    for (i0, i1, col, lab) in spans:
        o.append(f'<rect class="anim a-fade" style="--d:.6s" x="{X(i0):.1f}" y="{T}" width="{max(X(i1) - X(i0), 6):.1f}" '
                 f'height="{Bm - T}" fill="{col}" fill-opacity=".18" rx="6"/>')
        if lab:
            o.append(f'<text class="anim a-fade" style="--d:.8s" x="{(X(i0) + X(i1)) / 2:.1f}" y="{T + 26}" fill="{col}" '
                     f'font-size="21" font-weight="800" text-anchor="middle">{lab}</text>')
    if band:
        blo, bhi, bcol, blab = band
        o.append(f'<rect x="{L}" y="{Y(bhi):.1f}" width="{R - L}" height="{Y(blo) - Y(bhi):.1f}" fill="{bcol}" fill-opacity=".14"/>')
        if blab and band_lab_at is None:
            o.append(f'<text x="{L + 12}" y="{Y(blo) - 10:.1f}" fill="{bcol}" font-size="20" font-weight="700">{blab}</text>')
        elif blab:
            o.append(f'<text x="{X(band_lab_at):.1f}" y="{Y(blo) + 26:.1f}" fill="{bcol}" font-size="20" font-weight="700" text-anchor="middle">{blab}</text>')
    for (yv, lab) in yticks:
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L - 12}" y="{Y(yv) + 7:.1f}" fill="{AXIS}" font-size="19" text-anchor="end">{lab}</text>')
    for (i, lab) in xlabels:
        anchor = "start" if i == 0 else ("end" if i >= n - 1 else "middle")
        o.append(f'<text x="{X(i):.1f}" y="{h - 18}" fill="{AXIS}" font-size="19" text-anchor="{anchor}">{lab}</text>')
    d = "M" + " L".join(f"{X(i):.1f},{Y(v[i]):.1f}" for i in range(n) if not np.isnan(v[i]))
    o.append(f'<path class="draw" style="--dur:{dur};--d:{delay}" d="{d}" fill="none" stroke="{color}" '
             f'stroke-width="{stroke}" stroke-linejoin="round" stroke-linecap="round"/>')
    for hl in hlines:
        yv, lab, col = hl[:3]
        left = len(hl) > 3 and hl[3] == "left"
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{col}" stroke-width="2.5" stroke-dasharray="10 8"/>')
        o.append(f'<text x="{(L + 10) if left else (R - 6)}" y="{Y(yv) - 10:.1f}" fill="{col}" font-size="21" font-weight="800" '
                 f'text-anchor="{"start" if left else "end"}">{lab}</text>')
    o.append("</svg>")
    return "".join(o)


def month_labels(idx, every=2):
    out = []
    for m in range(1, 13, every):
        t = pd.Timestamp(year=idx[0].year, month=m, day=1)
        out.append((idx.get_loc(t), t.strftime("%b")))
    return out + [(len(idx) - 1, "31 Dec")]


def window_svg(w=1400, h=150):
    """24 trailing boxes ending at 14:00, plus the future greyed out."""
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    n, cell, gap, x0 = 34, 34, 6, 30
    now = 26                                    # index of 14:00 in the strip
    for i in range(n):
        x = x0 + i * (cell + gap)
        hour = (i - now + 14) % 24
        inside = now - 23 <= i <= now
        col = "#3B8BE0" if inside else ("#2A4566" if i < now else "#1A2A3D")
        o.append(f'<rect class="anim a-pop" style="--d:{.2 + i * .03:.2f}s;transform-origin:{x + cell / 2:.0f}px 70px" x="{x}" y="50" '
                 f'width="{cell}" height="{cell + 6}" rx="7" fill="{col}"/>')
        if i == now:
            o.append(f'<rect x="{x - 4}" y="46" width="{cell + 8}" height="{cell + 14}" rx="9" fill="none" stroke="{GOLD}" stroke-width="4"/>')
            o.append(f'<text x="{x + cell / 2}" y="34" fill="{GOLD}" font-size="22" font-weight="800" text-anchor="middle">14:00 = NOW</text>')
        if i in (now - 23, now - 12):
            o.append(f'<text x="{x + cell / 2}" y="124" fill="{AXIS}" font-size="18" text-anchor="middle">{hour:02d}:00</text>')
    xa, xb = x0 + (now - 23) * (cell + gap), x0 + now * (cell + gap) + cell
    o.append(f'<path class="draw" style="--d:1.2s;--dur:1s" d="M{xa} 140 L{xb} 140" stroke="#3B8BE0" stroke-width="4"/>')
    fx = x0 + (now + 1) * (cell + gap)
    o.append(f'<text x="{fx + 120}" y="124" fill="{RED}" font-size="20" font-weight="800" text-anchor="middle">the future: off limits ⛔</text>')
    o.append("</svg>")
    return "".join(o)


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    F = facts()
    bus, idx = F["bus"], F["bus"].index
    e2 = F["ev02_array"], F["ev02_soc"], F["ev02_volt"]
    ev04 = F["ev04_mask"]
    i04a, i04b = int(np.argmax(ev04)), int(len(ev04) - 1 - np.argmax(ev04[::-1]))
    months = month_labels(idx)

    # hook: 30 Apr – 4 May, array current and state of charge
    win = bus.loc["2025-04-30 00:00":"2025-05-04 23:00"]
    j0 = win.index.get_loc(pd.Timestamp("2025-05-02 01:00"))
    j1 = win.index.get_loc(pd.Timestamp("2025-05-02 12:00"))
    days = [(win.index.get_loc(pd.Timestamp(d)), f"{pd.Timestamp(d).day} {pd.Timestamp(d):%b}") for d in
            ("2025-04-30", "2025-05-01", "2025-05-02", "2025-05-03", "2025-05-04")]
    hook_arr = chart_svg(win["solar_array_current_a"].values, w=680, h=300, ymin=25.5, ymax=29.5, color=B["blue_d"],
                         band=(F["arr_lo"], F["arr_hi"], B["teal_d"], "normal sunlit band"), spans=[(j0, j1, GOLD, "")],
                         yticks=[(26, "26 A"), (28, "28 A")], xlabels=days[::2])
    hook_soc = chart_svg(win["battery_soc_pct"].values, w=680, h=300, ymin=90, ymax=101.5, color=GOLD,
                         spans=[(j0, j1, GOLD, "")], yticks=[(92, "92%"), (96, "96%"), (100, "100%")], xlabels=days[::2])

    # raw amplifier temperature vs its ceiling
    twta_chart = chart_svg(bus["twta_temp_c"].values, h=330, ymin=58, ymax=69.5, color=B["teal_d"], stroke=1.2,
                           hlines=[(F["twta_ceiling"], f"3σ ceiling {F['twta_ceiling']:.1f} °C", RED, "left")],
                           spans=[(i04a, i04b, GOLD, "EV04")], yticks=[(60, "60 °C"), (64, "64 °C"), (68, "68 °C")],
                           xlabels=months)
    # temp_per_drive
    tpd_chart = chart_svg(F["tpd"].values, h=330, ymin=0.76, ymax=0.92, color=B["blue_d"], stroke=1.2,
                          hlines=[(F["tpd_ceiling"], f"3σ ceiling {F['tpd_ceiling']:.3f}", RED, "left")],
                          spans=[(i04a, i04b, GOLD, "EV04")], yticks=[(0.78, "0.78"), (0.82, "0.82"), (0.86, "0.86"), (0.90, "0.90")],
                          xlabels=months)
    # the code book's residual
    rm, rs = F["resid_mean_fit"], F["resid_sd"]
    res_chart = chart_svg(F["resid"].values, h=330, ymin=-1.5, ymax=6.5, color=B["teal_d"], stroke=1.2,
                          band=(rm - 3 * rs, rm + 3 * rs, "#9DB0C6", "normal ± 3σ"),
                          spans=[(0, idx.get_loc(pd.Timestamp("2025-05-31 23:00")), "#3CCB7F", "fitted here"),
                                 (idx.get_loc(pd.Timestamp("2025-10-01")), len(idx) - 1, RED, "Oct–Dec: every hour flagged")],
                          yticks=[(0, "0 °C"), (3, "+3 °C"), (6, "+6 °C")], xlabels=months,
                          band_lab_at=idx.get_loc(pd.Timestamp("2025-07-25")))

    w4 = F["w4d2_raw_steady"]["table"]
    tpc = F["tpd_chart_all"]
    ev04_lit = int(tpc["table"].loc["EV04", "hours_flagged"])
    ev04_len = int(tpc["table"].loc["EV04", "hours_long"])
    sink, lean = F["sink_forest"], F["lean_forest"]
    resid_y = F["resid_year"]
    oct_flag, oct_n = F["resid_octdec"]

    # sink vs lean event grid
    def cell(r, e):
        t = r["table"]
        if bool(t.loc[e, "caught"]):
            return f'<td class="mono" style="color:{GREEN};font-weight:800">✅ {int(t.loc[e, "hours_flagged"])}/{int(t.loc[e, "hours_long"])} h</td>'
        return f'<td class="mono" style="color:{RED};font-weight:800">❌ missed</td>'
    grid_rows = ""
    for k, (e, r) in enumerate(F["labels"].set_index("event_id").iterrows()):
        grid_rows += (f'<tr class="anim a-left" style="--d:{.3 + k * .15:.2f}s"><td><b>{e}</b> <span class="small" style="font-size:18px">· '
                      f'{r["type"].replace("_", " ")}</span></td>{cell(sink, e)}{cell(lean, e)}</tr>')
    grid_rows += (f'<tr class="anim a-left" style="--d:1.2s"><td><b>False alarms</b> <span class="small" style="font-size:18px">· whole year</span></td>'
                  f'<td class="mono" style="color:{RED};font-weight:800">about {round(sink["false_alarms"], -1)}</td>'
                  f'<td class="mono" style="color:{GOLD};font-weight:800">{lean["false_alarms"]}</td></tr>')
    table_css = ("<style>.sb{width:100%;border-collapse:separate;border-spacing:0 6px;font-size:24px}"
                 ".sb th{color:#9DB0C6;font-size:19px;text-align:left;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:0 16px}"
                 ".sb td{background:#12233A;padding:9px 16px}.sb td:first-child{border-radius:14px 0 0 14px}"
                 ".sb td:last-child{border-radius:0 14px 14px 0}</style>")

    # reasons table
    what = {"EV01": "array string dropout", "EV02": "battery not charging", "EV03": "array string dropout",
            "EV04": "amplifier hot for its drive", "EV05": "battery not charging (again)"}
    reason_rows = ""
    for k, (e, r) in enumerate(F["reasons"].items()):
        tops = " · ".join(f'<b style="color:{GOLD if c == "temp_per_drive" else "#EAF2FB"}">{NICE[c]}</b> '
                          f'<span class="mono">{v:+.1f}σ</span>' for c, v in r["top"])
        reason_rows += (f'<tr class="anim a-left" style="--d:{.3 + k * .15:.2f}s"><td><b>{e}</b></td><td>{what[e]}</td>'
                        f'<td>{tops}</td></tr>')

    pairs = F["sink_pairs"]
    pair_lines = "".join(f'<p class="mono anim a-left" style="--d:{.4 + k * .12:.2f}s;font-size:22px;margin:6px 0">'
                         f'{a} <span class="muted">↔</span> {b} <b class="{"bad" if v > .98 else "hl"}">{v:.3f}</b></p>'
                         for k, ((a, b), v) in enumerate(pairs.head(5).items()))

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:50px;top:170px;width:540px;height:520px">
  <svg viewBox="0 0 540 520" width="540" height="520">
    <path class="draw" style="--d:.2s;--dur:1.6s" d="M30 260 Q270 40 510 260 Q270 480 30 260 Z" fill="none" stroke="#3B8BE0" stroke-width="16" stroke-linejoin="round"/>
    <circle cx="270" cy="260" r="118" fill="#12233A" stroke="#16A394" stroke-width="16" class="anim a-pop" style="--d:.9s;transform-origin:270px 260px"/>
    <circle cx="270" cy="260" r="56" fill="#F5B83D" class="anim a-pop" style="--d:1.2s;transform-origin:270px 260px"/>
    <circle cx="292" cy="236" r="16" fill="#EAF2FB" class="anim a-fade" style="--d:1.5s"/>
    <text x="270" y="470" text-anchor="middle" font-size="30" font-weight="800" fill="#9DB0C6" class="anim a-fade" style="--d:1.8s">history · context · relationships</text>
  </svg></div>
<div style="max-width:880px;margin-top:40px">
  <div class="kicker anim">Week 4 · Day 3</div>
  <h1 class="anim" style="--d:.2s">Give the Model<br><span class="hl">Eyes</span> 👁️</h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Feature engineering: new columns that let<br>a model see what an engineer sees.</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex">{logos_title_block()}</div>
</div>""",
          "Welcome back. Last time the forest flagged eclipse hours and slept through a four-week amplifier fault. Today we give it eyes: features. Then the final-project Checkpoint 3."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Three kinds of eyes. Then your own method.</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:290px;padding:40px 26px"><div class="icon">🕰️</div><h3>History</h3><p class="small">lags + rolling windows,<br>no peeking ahead</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:290px;padding:40px 26px"><div class="icon">🔗</div><h3>Relationships</h3><p class="small">hot for its workload?</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:290px;padding:40px 26px"><div class="icon">✂️</div><h3>Fewer, better</h3><p class="small">32 columns vs 5</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:270px;padding:40px 26px"><div class="icon">🛠️</div><h3>Checkpoint 3</h3><p class="small">your method, drafted</p></div>
</div>
<div class="row anim" style="--d:1.8s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 55 min hands-on</span><span class="pill gold">🏁 25 min checkpoint + wrap-up</span>
</div>""",
          "Four moves. The hands-on builds every feature on the slides. We end with the final-project Checkpoint 3: method drafted."),

        # 3 ─ hook
        S(f"""
<div class="kicker anim">2 May · steady sunshine · EV02</div>
<h2 class="anim" style="--d:.1s">NEPA brought light… but the inverter isn't charging 💡🔋</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">💡</div><h3>The light is ON</h3>
    <p class="muted">Solar-array current: <b style="color:#fff">{e2[0][0]:.2f}–{e2[0][1]:.2f} A</b>.<br>Inside its normal sunlit band ({F['arr_lo']:.2f}–{F['arr_hi']:.2f} A). <b class="good">Looks fine.</b></p></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">🔋</div><h3>The battery is stuck</h3>
    <p class="muted">State of charge: <b style="color:#fff">{e2[1][0]:.1f}–{e2[1][1]:.1f}%</b> for 12 hours.<br>On eclipse nights it reads 92–94% for {F['soc9294_night']} hours a year. <b class="good">Normal… at night.</b></p></div>
</div>
<p class="sub step" data-step="1" style="margin-top:34px;text-align:center">Each number is normal <b>alone</b>. Together, in steady sun? <b class="bad">Only ever during a fault.</b> 🚨</p>""",
          f"Like NEPA bringing light while the inverter still shows 93% and won't climb: the charger is faulty. In the data, SoC between 92 and 94% appears on {F['soc9294_steady']} steady-sun hours, and every one of them is inside EV02 or EV05. "
          f"The other {F['soc9294_night']} are eclipse and recharge hours. The relationship broke, not the reading."),

        # 4 ─ hook chart
        S(f"""
<div class="kicker anim">30 April → 4 May, hour by hour</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The current barely moves. The battery stops charging.</h2>
<div class="grid2" style="gap:26px">
  <div class="card anim a-left" style="--d:.2s;padding:18px 20px"><h3 style="font-size:26px">💡 Solar-array current</h3>{hook_arr}</div>
  <div class="card anim a-right" style="--d:.4s;padding:18px 20px"><h3 style="font-size:26px">🔋 State of charge</h3>{hook_soc}</div>
</div>
<div class="row anim" style="--d:2.4s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill gold">gold = EV02, 2 May 01:00–12:00</span><span class="pill">bus voltage sags too: {e2[2][0]:.2f}–{e2[2][1]:.2f} V</span>
  <span class="small" style="margin-left:auto">the code book looked at 1 May by mistake (SoC {F['may1_soc'][0]:.0f}% all day)</span>
</div>""",
          "Point at the gold window. The array dips about one amp, still inside its band; SoC drops to 93% and sits there. The original code book's proof checked 1 May, where SoC is a perfectly normal 100%. The label file and the data say 2 May."),

        # 5 ─ last time
        S(f"""
<div class="kicker anim">Last time · the forest on raw channels, steady sun</div>
<h2 class="anim" style="--d:.1s">4 of 5 caught… but look at EV04 👀</h2>
<div class="grid3" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="stat good" style="font-size:86px">4/5</div><div class="stat-label">events “caught”</div></div>
  <div class="card anim a-pop" style="--d:.55s;text-align:center;border-color:#E5484D"><div class="stat bad" style="font-size:86px">{int(w4.loc['EV04', 'hours_flagged'])}/{int(w4.loc['EV04', 'hours_long'])}</div><div class="stat-label">EV04 hours it noticed</div></div>
  <div class="card anim a-pop" style="--d:.8s;text-align:center;border-color:#E5484D"><div class="stat bad" style="font-size:86px">{int(w4.loc['EV04', 'hours_late']) // 24} days</div><div class="stat-label">late, the first (and only) time</div></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:34px;text-align:center">For four weeks the amplifier ran hot <b>for its workload</b>.<br>The forest can't see “for its workload”. <b class="hl">Today we give it eyes.</b></p>""",
          f"From W4D2: fitted on Jan–Aug steady-sun hours, the forest flagged EV04 on exactly {int(w4.loc['EV04', 'hours_flagged'])} hour, {int(w4.loc['EV04', 'hours_late'])} hours after it began. By the scoring rules that's a catch; to the engineer it's a miss. It also missed EV03, an 11 A drop."),

        # 6 ─ the model cannot tell time
        S("""
<div class="kicker anim">Why features?</div>
<h2 class="anim" style="--d:.1s">The model <span class="hl">cannot tell time</span> ⏰</h2>
<div class="flow" style="margin-top:20px;justify-content:center">
  <div class="box anim a-pop" style="--d:.3s;min-width:360px"><p class="mono" style="font-size:22px;text-align:left">13:00 · 27.0 A · 93.0%<br>14:00 · 27.1 A · 92.8%<br>15:00 · 27.0 A · 93.1%</p><p class="small">rows of a table</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:260px"><div class="icon">🌲</div><p class="small">judges ONE row at a time</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box anim a-pop" style="--d:1.1s;min-width:300px"><p style="font-size:26px">No yesterday.<br>No “compared with what?”</p></div>
</div>
<div class="grid3" style="margin-top:34px">
  <div class="card anim a-pop" style="--d:1.4s;padding:24px 28px"><div class="icon" style="font-size:54px">🕰️</div><h3>History</h3><p class="muted">What was it an hour ago? Over the last day?</p></div>
  <div class="card anim a-pop" style="--d:1.6s;padding:24px 28px"><div class="icon" style="font-size:54px">🌘</div><h3>Context</h3><p class="muted">Steady sun, eclipse or recharge?</p></div>
  <div class="card anim a-pop" style="--d:1.8s;padding:24px 28px"><div class="icon" style="font-size:54px">🔗</div><h3>Relationship</h3><p class="muted">Hot for its drive level?</p></div>
</div>""",
          "Quiz 3, question 16. Each row is judged on its own unless the columns themselves carry history. A feature is just a new column you compute from the old ones. Context (steady sun) came last time; today is history and relationships."),

        # 7 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">History, without cheating 🕰️</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Give every row a memory of the past. Only the past.</p>""",
          "Section break.", cls="center"),

        # 8 ─ history features
        S(f"""
<div class="kicker anim">Five lines of pandas</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Every window ends <span class="hl">now</span></h2>
<pre class="code anim" style="--d:.2s;font-size:25px">soc.shift(1)                     # an hour ago
soc.shift(24)                    # same hour yesterday
soc.diff(1)                      # change since last hour
soc.rolling(24).mean()           # average of the last 24 hours
soc - soc.rolling(24).mean()     # how far from its own last day</pre>
<div class="card anim" style="--d:.6s;padding:14px 20px;margin-top:20px">{window_svg()}</div>""",
          "A lag copies an older value onto today's row. A rolling window summarises the last 24 rows, including this one: at 14:00 it covers 15:00 yesterday to 14:00 today. The blue boxes are the window; the gold box is now; the future is off limits."),

        # 9 ─ the 14:00 test
        S(f"""
<div class="kicker anim">The one question to ask of every feature</div>
<h2 class="anim" style="--d:.1s;font-size:52px">“Could I compute this at 14:00, using only what I knew at 14:00?”</h2>
<div class="grid2" style="margin-top:14px">
  <div class="card anim a-left" style="--d:.3s;border-color:#16A394"><h3>✅ Honest</h3>
    <pre class="code" style="font-size:24px;margin-top:10px">soc.shift(1)
soc.rolling(24).mean()</pre><p class="muted" style="margin-top:12px">the past only</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#E5484D"><h3>❌ Cheats</h3>
    <pre class="code" style="font-size:24px;margin-top:10px">soc.shift(-1)
soc.rolling(24, center=True).mean()</pre><p class="muted" style="margin-top:12px">reads tomorrow's newspaper today 🗞️</p></div>
</div>
<div class="row anim" style="--d:1s;margin-top:24px;gap:14px;align-items:center">
  <span class="pill gold">longest window 24 h</span><span class="pill">the first 24 rows have no full history</span>
  <span class="pill teal">{F['n_rows']:,} → {F['sink_rows']:,} rows</span>
</div>""",
          f"Quiz 3, questions 19, 20 and 22. shift(-1) copies the NEXT hour back; center=True mixes 12 future hours in. Both look brilliant in testing and are impossible in the control room. "
          f"The code book's 32-column builder drops {F['sink_rows_lost']} rows because its longest window is 24 hours."),

        # 10 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Hot for its workload 🔗</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">One column that ties two sensors together.</p>""",
          "Section break.", cls="center"),

        # 11 ─ raw twta
        S(f"""
<div class="kicker anim">EV04 · cooling path degraded · 3–30 September</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Raw temperature: four weeks, <span class="bad">zero alarms</span></h2>
<div class="card anim" style="--d:.2s;padding:18px 20px">{twta_chart}</div>
<div class="row anim" style="--d:2.4s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill bad">hottest EV04 hour {F['twta_ev04_max']:.1f} °C</span><span class="pill">ceiling {F['twta_ceiling']:.1f} °C (Jan–Aug, steady sun)</span>
  <span class="small" style="margin-left:auto">the yearly swing hides a 3 °C fault</span>
</div>""",
          "The amplifier's temperature swings with the seasons and climbs as drive goes up. That swing makes sigma big, so the ceiling sits above everything, even the fault. A Week 3 chart sleeps through four weeks of a cooling problem."),

        # 12 ─ temp_per_drive
        S(f"""
<div class="kicker anim">One new column: temp_per_drive = twta_temp_c ÷ rf_drive_pct</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Divide by the workload and EV04 <span class="hl">jumps out</span></h2>
<div class="card anim" style="--d:.2s;padding:18px 20px">{tpd_chart}</div>
<div class="row anim" style="--d:2.4s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill">normal {F['tpd_mean']:.3f} ± {F['tpd_sd']:.3f}</span><span class="pill gold">EV04 {F['tpd_ev04_mean']:.3f} = +{F['tpd_ev04_z']:.1f}σ</span>
  <span class="pill teal">{ev04_lit} of {ev04_len} EV04 hours lit</span><span class="pill teal">{tpc['false_alarms']} false alarms all year</span>
</div>""",
          f"Quiz 3, question 17. Degrees per percent of drive: how hot it runs for the work it's doing. Like a generator that runs hot while powering one bulb: the load didn't change, so something is blocking the cooling. "
          f"A plain 3σ chart on this one column catches EV04 in its first hour and lights {ev04_lit} of its {ev04_len} hours, with {tpc['false_alarms']} false alarms in the whole year."),

        # 13 ─ the 29 sigma trap
        S(f"""
<div class="kicker anim">The code book's feature · temperature vs drive + season, fitted on January–May</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The <span class="bad">{F['resid_ev04_sigma']:.0f}σ</span> trap 🪤</h2>
<div class="card anim" style="--d:.2s;padding:14px 20px">{res_chart}</div>
<div class="grid2" style="margin-top:16px;gap:24px">
  <div class="card anim a-left" style="--d:2.4s;padding:14px 24px"><p style="font-size:24px">🧮 <b>Code book residual:</b> EV04 = <b class="hl">{F['resid_ev04_sigma']:.1f}σ</b><br><span class="muted">but {oct_flag:,} of {oct_n:,} Oct–Dec hours flagged · <b class="bad">{resid_y['false_alarms']:,} false alarms</b></span></p></div>
  <div class="card anim a-right glow" style="--d:2.7s;padding:14px 24px"><p style="font-size:24px">➗ <b>Humble ratio:</b> EV04 = <b class="hl">{F['tpd_ev04_z']:.1f}σ</b><br><span class="muted">and <b class="good">{tpc['false_alarms']} false alarms</b> all year</span></p></div>
</div>""",
          f"The code book promises about 22 sigma; its own recipe gives {F['resid_ev04_sigma']:.1f}. Impressive, until you carry it to months it never saw: from June it drifts, and from October every single hour is flagged. "
          "Five months of data can't tell the amplifier's slow yearly warming from the season. Lesson: a big sigma on the fault is not the test. The test is: does it stay quiet on normal months it never saw?"),

        # 14 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s;font-size:84px">More features ≠ better eyes ✂️</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">The code book's 32 columns against our 5.</p>""",
          "Section break.", cls="center"),

        # 15 ─ kitchen sink duplicates
        S(f"""
<div class="kicker anim">The code book's builder · {F['sink_cols']} columns from 6 sensors</div>
<h2 class="anim" style="--d:.1s;font-size:54px"><span class="bad">{F['sink_n_dupes']}</span> pairs of near-twins 👯</h2>
<div class="row" style="gap:36px;margin-top:10px">
  <div class="card anim" style="--d:.2s;flex:1.35;padding:24px 30px"><h3 style="font-size:26px">Most alike (correlation)</h3>{pair_lines}</div>
  <div class="col" style="flex:1;gap:20px">
    <div class="card anim a-right" style="--d:.9s;padding:24px"><p style="font-size:25px"><b class="hl">soc_gap</b> is just <span class="mono">100 − SoC</span>. Same column, wearing a different cap. 🧢</p></div>
    <div class="card anim a-right" style="--d:1.2s;padding:24px"><p style="font-size:25px">The forest picks a column <b>at random</b> for every cut. Two copies of SoC = SoC gets <b class="bad">double the vote</b>.</p></div>
  </div>
</div>""",
          f"Quiz 3, question 21. Anything above about 0.98 is a duplicate. The code book's own check would prune these {F['sink_n_dupes']} pairs, then it fits on all of them anyway."),

        # 16 ─ sink vs lean
        S(f"""{table_css}
<div class="kicker anim">Same forest · fitted on Jan–Aug steady sun · scored on the whole year</div>
<h2 class="anim" style="--d:.1s;font-size:52px;margin-bottom:10px">32 columns vs 5 columns</h2>
<table class="sb"><tr class="anim" style="--d:.1s"><th>Event</th><th>🧺 Kitchen sink ({F['sink_cols']})</th><th>🎯 Lean 5 (4 sensors + temp_per_drive)</th></tr>{grid_rows}</table>
<p class="anim" style="--d:1.6s;margin-top:14px;text-align:center">The sink misses the two <b>easiest</b> faults: an 11 A drop drowned in 32 columns of noise.</p>""",
          f"Hours shown are how many of the event's hours lit up. Kitchen sink: {sink['caught']} of 5, about 70 false alarms (73 on the newest pandas, 69 on pandas 2.2: rolling statistics differ in the last decimal). "
          f"Lean 5: all 5, every one within an hour of its start, {lean['false_alarms']} false alarms. Fewer, sharper eyes."),

        # 17 ─ right reasons
        S(f"""{table_css}
<div class="kicker anim">Explain every flag · z = (value − normal) ÷ σ</div>
<h2 class="anim" style="--d:.1s;font-size:52px;margin-bottom:10px">Right answer, <span class="hl">right reason</span></h2>
<table class="sb"><tr class="anim" style="--d:.1s"><th>Event</th><th>What broke</th><th>Biggest z-scores of the flagged hours</th></tr>{reason_rows}</table>
<p class="anim" style="--d:1.4s;margin-top:14px;text-align:center">The model's reason matches the engineer's reason. That's the sentence you give the duty engineer. 🧑🏾‍🔧</p>""",
          "Quiz 3, question 14. For each flagged hour, how far every feature sits from its Jan–Aug steady-sun normal, in sigmas. EV04 is flagged by temp_per_drive alone, exactly as the physics says. "
          "Note how EV02 and EV05 also show in bus voltage: they are not as invisible to a single sensor as the label file claims."),

        # 18 ─ cliffhanger
        S(f"""
<div class="kicker anim">So… is it ready for the control room?</div>
<h2 class="anim" style="--d:.1s">5 of 5! 🎉 &nbsp;But hold on…</h2>
<div class="grid3" style="margin-top:24px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">📟</div><h3>{lean['false_alarms']} false alarms</h3><p class="muted">about one page every {365 / lean['false_alarms']:.0f} days</p></div>
  <div class="card anim a-pop" style="--d:.55s"><div class="icon">📝</div><h3>Marked its own homework</h3><p class="muted">EV01–EV03 sit inside the months it trained on</p></div>
  <div class="card anim a-pop" style="--d:.8s"><div class="icon">🥊</div><h3>No race yet</h3><p class="muted">the Week 4 chart never got the same eyes</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:36px;text-align:center">Next time 👉 <b class="hl">No expo!</b> An honest exam on months the model has never seen.</p>""",
          "Leave them hungry. 5 of 5 sounds great, but the score includes the training months, and nobody raced the simple chart on the same features. Week 5 Day 1 runs that honest exam."),

        # 19 ─ checkpoint 3
        S("""
<div class="kicker anim">🏁 Final project · Checkpoint 3</div>
<h2 class="anim" style="--d:.1s">🛠️ Method drafted</h2>
<div class="grid2" style="margin-top:16px">
  <div class="card anim a-left" style="--d:.3s"><h3>Bring today</h3>
    <p class="muted">✅ the minimum method for your brief, <b>running</b> on your data<br>✅ your “normal” in writing: states and what you take away first<br>
    ✅ your features, each passing the 14:00 test<br>✅ your reference period: quiet months, agreed<br>✅ the simple baseline you'll race</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#E5484D"><h3>Data rules</h3>
    <p class="muted">⛔ real NIGCOMSAT data stays on NIGCOMSAT systems (training server / work laptop), <b>not Colab</b><br>
    ⛔ no raw data on GitHub<br>⛔ describe the shape to AI tools, don't paste it</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:28px;text-align:center">Next checkpoint: <b class="hl">Week 5 · Day 3: honest test</b> ⚖️</p>""",
          "20 minutes, one by one. A first version that runs end to end beats a perfect plan. Detection briefs: a statistical baseline plus a multivariate detector on trailing features. Degradation: trend-to-threshold. Forecasting: a baseline forecast plus a regression."),

        # 20 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 55 minutes</div>
  <h2 class="anim" style="--d:.1s">Build the eyes 👁️</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open <b class="hl">W4D3-exercise</b>, save a copy, run STEP 0</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">A</span><p>History features + the 14:00 test</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">B</span><p>temp_per_drive, then spring the 29σ trap</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">C</span><p>32 columns vs 5, and explain every flag</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">👁️</div>
  <h3 style="margin-top:16px">15 checks to pass</h3>
  <p class="muted">🌶️ Pepper task: give the old Week 4 chart the same eyes. Who wins?</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Common snags: dividing drive by temperature (upside down), and skipping the toolbox cell before Part B. The forest cells take a few seconds each."),

        # 21 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🕰️</span><p><b>The model can't tell time.</b> Lags and rolling windows give it memory. Past only: the 14:00 test.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🔗</span><p><b>One relationship beats many raw columns.</b> Check every feature on months it never saw.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">✂️</span><p><b>Fewer, sharper features.</b> Prune twins; explain every flag with z-scores.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:34px;font-size:30px">Next time 👉 <b class="hl">No expo!</b> Honest train/test splits + Quiz 3. 📝</p>""",
          "Recap, then Checkpoint 3 if you haven't run it yet. Quiz 3 is next session: it covers W4D2, today and W5D1."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    F = facts()
    bus = F["bus"]
    e2 = F["ev02_array"], F["ev02_soc"]
    w4 = F["w4d2_raw_steady"]["table"]
    tpc = F["tpd_chart_all"]
    sink, lean = F["sink_forest"], F["lean_forest"]
    win = bus.loc["2025-04-30 00:00":"2025-05-04 23:00"]
    hlab = [f"{t.day} {t:%b}" for t in win.index]
    daily_max = bus["twta_temp_c"].resample("D").max()
    daily_tpd = F["tpd"].resample("D").mean()
    dlab = [d.strftime("%b") if d.day == 1 else "" for d in daily_max.index]

    def cell(r, e):
        t = r["table"]
        return f"✅ {int(t.loc[e, 'hours_flagged'])}/{int(t.loc[e, 'hours_long'])} h" if bool(t.loc[e, "caught"]) else "❌ missed"
    grid = [[e, typ.replace("_", " "), cell(sink, e), cell(lean, e)] for e, typ in zip(F["labels"]["event_id"], F["labels"]["type"])]
    grid.append(["False alarms", "whole year", f"about {round(sink['false_alarms'], -1)}", str(lean["false_alarms"])])
    what = {"EV01": "array string dropout", "EV02": "battery not charging", "EV03": "array string dropout",
            "EV04": "amplifier hot for its drive", "EV05": "battery not charging (again)"}
    reasons = [[e, what[e], " · ".join(f"{NICE[c]} {v:+.1f}σ" for c, v in r["top"])] for e, r in F["reasons"].items()]
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "👁️", "kicker": "Week 4 · Day 3", "title": "Give the Model Eyes",
             "sub": "Feature engineering: new columns that let a model see what an engineer sees",
             "notes": "Last time the forest slept through a four-week amplifier fault. Today: features."},
            {"type": "flow", "title": "Today's mission", "steps": [
                ["🕰️", "History", "lags + rolling windows"], ["🔗", "Relationships", "hot for its workload?"],
                ["✂️", "Fewer, better", "32 columns vs 5"], ["🛠️", "Checkpoint 3", "your method, drafted"]],
             "footer": "10 min hook · 30 min slides · 55 min hands-on · 25 min checkpoint + wrap-up", "notes": "Four moves."},
            {"type": "compare", "title": "NEPA brought light… but the inverter isn't charging",
             "left": ["💡", "The light is ON", f"Array current {e2[0][0]:.2f}–{e2[0][1]:.2f} A: inside its normal sunlit band"],
             "right": ["🔋", "The battery is stuck", f"State of charge {e2[1][0]:.1f}–{e2[1][1]:.1f}% for 12 hours. Normal on eclipse nights; in steady sun, only during a fault"],
             "notes": "Each number is normal alone; together they are a fault. EV02, 2 May (the code book checked 1 May by mistake)."},
            {"type": "twochart", "title": "EV02: the current barely moves, the battery stops charging",
             "left": {"label": "Solar-array current (A), 30 Apr → 4 May", "labels": hlab, "values": win["solar_array_current_a"].round(2).tolist(),
                      "ymin": 25.5, "ymax": 29.5, "freq": 24, "fmt": "0.0"},
             "right": {"label": "State of charge (%), 30 Apr → 4 May", "labels": hlab, "values": win["battery_soc_pct"].round(1).tolist(),
                       "ymin": 90, "ymax": 101, "freq": 24, "fmt": "0"},
             "notes": "EV02 is 2 May 01:00–12:00."},
            {"type": "statement", "title": "Last time: the forest on raw channels", "icon": "👀",
             "big": f"EV04: {int(w4.loc['EV04', 'hours_flagged'])} of {int(w4.loc['EV04', 'hours_long'])} hours noticed, {int(w4.loc['EV04', 'hours_late']) // 24} days late",
             "sub": "The amplifier ran hot for its workload for four weeks. The forest can't see “for its workload”.",
             "notes": "Today we give it eyes."},
            {"type": "cards", "title": "The model cannot tell time: give it eyes", "cards": [
                ["🕰️", "History", "What was it an hour ago? Over the last day?"],
                ["🌘", "Context", "Steady sun, eclipse or recharge?"],
                ["🔗", "Relationship", "Hot for its drive level?"]],
             "notes": "Quiz 3 Q16: each row is judged alone unless features carry history."},
            {"type": "section", "kicker": "Part 1", "title": "History, without cheating", "sub": "Only the past", "notes": "Section break."},
            {"type": "code", "title": "Five lines of pandas: every window ends now",
             "code": "soc.shift(1)                    # an hour ago\nsoc.shift(24)                   # same hour yesterday\n"
                     "soc.diff(1)                     # change since last hour\nsoc.rolling(24).mean()          # average of the last 24 hours\n"
                     "soc - soc.rolling(24).mean()    # how far from its own last day",
             "caption": "At 14:00 the window covers 15:00 yesterday to 14:00 today. Never the future.",
             "notes": "Lags copy older values onto today's row; rolling windows summarise the last 24 rows."},
            {"type": "compare", "title": "The 14:00 test: could I compute this at 14:00?",
             "left": ["✅", "Honest", "soc.shift(1) · soc.rolling(24).mean(): the past only"],
             "right": ["❌", "Cheats", "soc.shift(-1) · rolling(24, center=True): reads tomorrow's newspaper today"],
             "notes": f"Quiz 3 Q19, Q20, Q22. The 32-column builder drops {F['sink_rows_lost']} rows: its longest window is 24 hours."},
            {"type": "section", "kicker": "Part 2", "title": "Hot for its workload", "sub": "One column that ties two sensors together", "notes": "Section break."},
            {"type": "chart", "title": "Raw temperature: four weeks of EV04, zero alarms", "labels": dlab,
             "series": [{"name": "hottest hour each day (°C)", "values": daily_max.round(2).tolist(), "color": "008C7E"},
                        {"name": f"3σ ceiling {F['twta_ceiling']:.1f} °C", "values": [round(F["twta_ceiling"], 2)] * len(daily_max), "color": "E5484D"}],
             "ymin": 58, "ymax": 70, "fmt": "0",
             "caption": f"Hottest EV04 hour {F['twta_ev04_max']:.1f} °C. The yearly swing makes σ big, so the ceiling sits above the fault.",
             "notes": "A Week 3 chart sleeps through four weeks of a cooling problem."},
            {"type": "chart", "title": "temp_per_drive = temperature ÷ drive: EV04 jumps out", "labels": dlab,
             "series": [{"name": "daily average temp_per_drive", "values": daily_tpd.round(4).tolist(), "color": "0A5DB4"},
                        {"name": f"3σ ceiling {F['tpd_ceiling']:.3f}", "values": [round(F["tpd_ceiling"], 4)] * len(daily_tpd), "color": "E5484D"}],
             "ymin": 0.78, "ymax": 0.9, "fmt": "0.00",
             "caption": f"Normal {F['tpd_mean']:.3f} ± {F['tpd_sd']:.3f}; EV04 {F['tpd_ev04_mean']:.3f} (+{F['tpd_ev04_z']:.1f}σ). {int(tpc['table'].loc['EV04', 'hours_flagged'])} of 672 EV04 hours lit, {tpc['false_alarms']} false alarms all year.",
             "notes": "Quiz 3 Q17. Like a generator running hot on one bulb: something is blocking the cooling."},
            {"type": "compare", "title": f"The {F['resid_ev04_sigma']:.0f}σ trap: check features on months they never saw",
             "left": ["🧮", f"Code book residual: {F['resid_ev04_sigma']:.1f}σ", f"Fitted Jan–May. Flags {F['resid_octdec'][0]:,} of {F['resid_octdec'][1]:,} Oct–Dec hours: {F['resid_year']['false_alarms']:,} false alarms"],
             "right": ["➗", f"Humble ratio: {F['tpd_ev04_z']:.1f}σ", f"{tpc['false_alarms']} false alarms all year. Stable on months it never saw"],
             "notes": "The code book says about 22σ; the recipe gives 28.9σ (Quiz 3 Q18 uses the real number). Five months can't tell the yearly warming from the season."},
            {"type": "section", "kicker": "Part 3", "title": "More features ≠ better eyes", "sub": "32 columns against 5", "notes": "Section break."},
            {"type": "table", "title": f"The code book's {F['sink_cols']} columns: {F['sink_n_dupes']} pairs of near-twins",
             "header": ["Column", "Its twin", "Correlation"],
             "rows": [[a, b, f"{v:.3f}"] for (a, b), v in F["sink_pairs"].head(5).items()],
             "colW": [4.6, 4.6, 3.13], "caption": "soc_gap = 100 − SoC. The forest picks columns at random, so a twin doubles that sensor's vote.",
             "notes": "Quiz 3 Q21: prune pairs above about 0.98."},
            {"type": "table", "title": "Same forest: 32 columns vs 5 (whole year, steady sun)",
             "header": ["Event", "Type", f"Kitchen sink ({F['sink_cols']})", "Lean 5"], "rows": grid,
             "colW": [2.0, 3.4, 3.4, 3.53], "caption": "The sink misses the two easiest faults. Hours = how many of the event's hours lit up.",
             "notes": "Kitchen sink about 70 false alarms (73 pandas 3, 69 pandas 2.2)."},
            {"type": "table", "title": "Right answer, right reason (z-scores of the flagged hours)",
             "header": ["Event", "What broke", "Biggest z-scores"], "rows": reasons, "colW": [1.5, 4.3, 6.53],
             "caption": "The model's reason matches the engineer's. EV04 is flagged by temp_per_drive alone.",
             "notes": "Quiz 3 Q14."},
            {"type": "cards", "title": "5 of 5! But hold on…", "cards": [
                ["📟", f"{lean['false_alarms']} false alarms", f"about one page every {365 / lean['false_alarms']:.0f} days"],
                ["📝", "Marked its own homework", "EV01–EV03 sit inside its training months"],
                ["🥊", "No race yet", "the Week 4 chart never got the same eyes"]],
             "notes": "Next: No expo! An honest exam on months the model never saw."},
            {"type": "compare", "title": "Final project · Checkpoint 3: method drafted",
             "left": ["🛠️", "Bring today", "Your brief's minimum method running on your data; your normal in writing; features that pass the 14:00 test; a reference period; the baseline you'll race"],
             "right": ["⛔", "Data rules", "Real NIGCOMSAT data stays on NIGCOMSAT systems (not Colab); no raw data on GitHub"],
             "notes": "Next checkpoint: Week 5 Day 3, honest test."},
            {"type": "steps", "title": "Your turn: 55 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W4D3-exercise, save a copy, run STEP 0", "A: history features + the 14:00 test",
                "B: temp_per_drive, then the 29σ trap", "C: 32 columns vs 5, explain every flag"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🕰️", "The model can't tell time: lags and rolling windows, past only"],
                ["🔗", "One relationship beats many raw columns; test features on unseen months"],
                ["✂️", "Fewer, sharper features; explain every flag with z-scores"]],
             "next": "Next: No expo! Honest train/test splits + Quiz 3", "notes": "Recap."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
def _near(x, want, tol):
    return abs(float(x) - want) <= tol

def _c_a1(x):
    ok = isinstance(x, pd.Series) and pd.isna(x.iloc[0]) and float(x.loc["2025-05-02 01:00"]) == 100.0 \
        and float(x.loc["2025-05-02 02:00"]) == 93.2
    return ok, "shift(1): each row now carries the hour before. At 02:00 it remembers 93.2% from 01:00. 🕰️", \
        "Shift by ONE hour into the past: a positive number."

def _c_a2(x):
    ok = isinstance(x, pd.Series) and x.first_valid_index() == pd.Timestamp("2025-01-01 23:00") \
        and 95 < float(x.loc["2025-05-02 12:00"]) < 100
    return ok, "A 24-hour trailing average. The first 23 rows are empty: not enough history yet.", \
        "One day of hourly rows is how many rows?"

def _c_a3(x):
    got = {str(v).strip().lower() for v in x}
    return got == {"b", "d"}, "b and d cheat. At midnight on 2 May nothing had gone wrong yet, but both already 'knew'. 🗞️", \
        "Look at the printed values at 00:00: which columns already show the fault that starts at 01:00?"

def _c_a4(x):
    return int(x) == 24, "24 rows: the longest window is 24 hours, so the first day has no full history.", \
        "Rows in bus minus rows in F: len(bus) - len(F)"

def _c_b1(x):
    ok = isinstance(x, pd.Series) and np.allclose(x.values, (bus["twta_temp_c"] / bus["rf_drive_pct"]).values)
    return ok, "temp_per_drive: degrees per % of drive. How hot it runs FOR ITS WORKLOAD. 🔗", \
        "Temperature divided by drive: bus[\"twta_temp_c\"] / bus[\"rf_drive_pct\"]"

def _c_b2(x):
    ok = isinstance(x, dict) and x.get("caught") == 1 and x.get("false_alarms") == 0
    return ok, "One column, a Week 3 chart: EV04 caught, ZERO false alarms all year. 👁️", \
        "K is the classic number of standard deviations: 3."

def _c_b3(x):
    return int(x) == 605, "605 of 672 hours: the alarm stays on while the fault lasts, not one lucky blip.", \
        "Read hours_flagged in the EV04 row of the table above."

def _c_b4(x):
    return int(x) == 2208, "Every one of the 2,208 Oct–Dec hours. Huge sigma on the fault, useless in service. 🪤", \
        "resid_flags.loc[\"2025-10-01\":].sum()"

def _c_b5(x):
    return x is False or str(x).strip().lower() == "false", \
        "False! Check a feature on months it never saw. The humble 3.9σ ratio stays quiet; the 29σ one cries wolf.", \
        "Did the 29-sigma feature stay quiet in October?"

def _c_c1(x):
    return int(x) == 18, "18 pairs above 0.98. Each twin doubles a sensor's vote in the forest. 👯", \
        "The pruning line from the slides: 0.98"

def _c_c2(x):
    ok = isinstance(x, dict) and x.get("events") == 5 and x.get("caught") == 3 and 40 <= x.get("false_alarms", -1) <= 120
    return ok, f"Only {x.get('caught')} of 5, and {x.get('false_alarms')} false alarms. 32 columns drowned the obvious dropouts.", \
        "contamination is a share of hours: half a percent is 0.005"

def _c_c3(x):
    r = score_events(x, labels)
    lit = int(x.loc["2025-09-03":"2025-09-30 23:00"].sum())
    ok = r["caught"] == 5 and 20 <= r["false_alarms"] <= 80 and lit > 200
    return ok, f"5 of 5, {r['false_alarms']} false alarms, {lit} EV04 hours lit. Fewer, sharper eyes. 🎯", \
        "Fit on the reference: training months AND steady sun: train & steady"

def _c_c4(x):
    return str(x).strip() == "temp_per_drive", "temp_per_drive, every time. Right answer, right reason. 🧑🏾‍🔧", \
        "Copy the column name at the top of the counts, in quotes."

def _c_c5(x):
    return x is False or str(x).strip().lower() == "false", \
        "False. It trained on Jan–Aug, so EV01–EV03 were in its homework. Next time: an honest exam. ⚖️", \
        "Which months did the forest train on? Which events sit in those months?"

def _c_bonus(x):
    ok = isinstance(x, dict) and x.get("caught") == 5 and x.get("false_alarms") == 3
    return ok, "5 of 5 with only 3 false alarms. Keep that result secret until Week 5 Day 1… 🤫🌶️", \
        "Same fit rows as the forest: train & steady"

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4,
          "B5": _c_b5, "C1": _c_c1, "C2": _c_c2, "C3": _c_c3, "C4": _c_c4, "C5": _c_c5, "BONUS": _c_bonus}
HINTS = {"A3": "A set of letters, e.g. {\"a\", \"c\"}.", "C3": "Run the toolbox cell first (Part B)."}
'''


MAKE_FEATURES = '''def make_features(df):
    """The original code book's builder. Trailing windows only, positive shifts only."""
    f = pd.DataFrame(index=df.index)
    for c in ["solar_array_current_a", "battery_soc_pct", "twta_temp_c", "bus_voltage_v"]:
        f[c]             = df[c]
        f[f"{c}_lag1"]   = df[c].shift(1)
        f[f"{c}_lag24"]  = df[c].shift(24)
        f[f"{c}_d1"]     = df[c].diff(1)
        f[f"{c}_mean24"] = df[c].rolling(24).mean()
        f[f"{c}_std24"]  = df[c].rolling(24).std()
        f[f"{c}_dev24"]  = df[c] - f[f"{c}_mean24"]
    f["temp_per_drive"] = df["twta_temp_c"] / df["rf_drive_pct"]     # relationship
    f["soc_gap"]        = 100 - df["battery_soc_pct"]                 # ... a twin of battery_soc_pct
    f["eclipse_flag"]   = df["eclipse_flag"]                          # known physics
    f["hour"]           = df.index.hour
    return f.dropna()

F = make_features(bus)
print("feature matrix:", F.shape)'''


def notebook_cells(setup_code):
    toolbox = ("from sklearn.ensemble import IsolationForest\n\n" + w5.SCORER_CODE + "\n\n" + w5.DETECTOR_CODE +
               '\n\nsteady = steady_sun(bus)\nprint("✅ toolbox ready ·", int(steady.sum()), "steady-sun hours of", len(bus))')
    return [
        ("md", """# 👁️ Week 4 · Day 3: Give the Model Eyes

**Today:** the forest can't tell time and can't see "hot for its workload". You build the columns that let it: **history**, **relationships**, and then you cut 32 columns down to 5.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**

**Rule book:** keep `W4D3-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up
Run it once every time you open the notebook (and after every restart). Wait for `✅ Ready!`."""),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: The model cannot tell time (15 min) 🕰️

▶️ Load the year of hourly telemetry (6 sensors + the eclipse flag) and the Week 5 answer key."""),
        ("code", 'bus = pd.read_csv(data_path("bus_telemetry_multivariate_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n'
                 'labels = load_labels("anomaly_labels_week5")\n'
                 'print("hours:", len(bus), "· columns:", list(bus.columns))\n'
                 'display(labels[["event_id", "start", "end", "type", "channels_involved"]])'),
        ("md", """### 💡🔋 NEPA brought light, but the inverter isn't charging
▶️ EV02, 2 May. The sun is shining (`eclipse_flag` is 0) and array current is only a little low, yet state of charge drops to about 93% and stays there.
(The original code book looked at **1 May** by mistake: that day the battery was a normal 100%.)"""),
        ("code", 'bus.loc["2025-05-02 00:00":"2025-05-02 14:00", ["solar_array_current_a", "battery_soc_pct", "bus_voltage_v", "eclipse_flag"]]'),
        ("md", """### A1 ✍️ History feature 1: the lag
The forest judges **one row at a time**: it has no idea what happened an hour ago. A **lag** copies an older value onto today's row.
`soc.shift(n)` moves the series `n` hours later. Fill in `HOURS_BACK` so the new column means *"state of charge one hour ago"*."""),
        ("task", 'soc = bus["battery_soc_pct"]\nHOURS_BACK = ___\n\nassert HOURS_BACK is not None, "✍️ Fill in HOURS_BACK first, then run this cell again."\nsoc_lag1 = soc.shift(HOURS_BACK)\n\nprint(pd.DataFrame({"soc": soc, "soc_1h_ago": soc_lag1}).loc["2025-05-02 00:00":"2025-05-02 03:00"])\ncheck("A1", soc_lag1)',
         'soc = bus["battery_soc_pct"]\nHOURS_BACK = 1\n\nassert HOURS_BACK is not None, "✍️ Fill in HOURS_BACK first, then run this cell again."\nsoc_lag1 = soc.shift(HOURS_BACK)\n\nprint(pd.DataFrame({"soc": soc, "soc_1h_ago": soc_lag1}).loc["2025-05-02 00:00":"2025-05-02 03:00"])\ncheck("A1", soc_lag1)'),
        ("md", """### A2 ✍️ History feature 2: the rolling mean
A **rolling window** summarises the last few rows, ending at the current one. Fill in `WINDOW`: how many hourly rows make **one day**?"""),
        ("task", 'WINDOW = ___\n\nassert WINDOW is not None, "✍️ Fill in WINDOW first."\nsoc_mean24 = soc.rolling(WINDOW).mean()\n\nprint("first hour with a full window:", soc_mean24.first_valid_index())\nprint("average of the last day at 2 May 12:00:", round(soc_mean24.loc["2025-05-02 12:00"], 2))\ncheck("A2", soc_mean24)',
         'WINDOW = 24\n\nassert WINDOW is not None, "✍️ Fill in WINDOW first."\nsoc_mean24 = soc.rolling(WINDOW).mean()\n\nprint("first hour with a full window:", soc_mean24.first_valid_index())\nprint("average of the last day at 2 May 12:00:", round(soc_mean24.loc["2025-05-02 12:00"], 2))\ncheck("A2", soc_mean24)'),
        ("md", """### A3 ✍️ The 14:00 test
Ask of every feature: ***"Could I compute this at 14:00, using only what I knew at 14:00?"***
▶️ Four candidate features, printed at **midnight on 2 May**, one hour **before** EV02 began. Which of them already "know" about the fault?"""),
        ("code", 'candidates = pd.DataFrame({\n    "a": soc.shift(1),\n    "b": soc.shift(-1),\n    "c": soc.rolling(24).mean(),\n    "d": soc.rolling(24, center=True).mean(),\n})\n'
                 'candidates.loc["2025-05-01 23:00":"2025-05-02 01:00"].round(2)'),
        ("task", 'cheaters = ___        # a set of letters, e.g. {"a", "c"}\n\ncheck("A3", cheaters)',
         'cheaters = {"b", "d"}        # a set of letters, e.g. {"a", "c"}\n\ncheck("A3", cheaters)'),
        ("md", """### A4 ✍️ The code book's feature builder
▶️ The original builder makes lags, differences and 24-hour rolling statistics for 4 sensors, plus a few extras. Every window is trailing. Run it."""),
        ("code", MAKE_FEATURES),
        ("md", "✍️ The data has 8,760 hours. How many rows did the builder lose, and why? (`dropna()` removed every row that had an empty window.)"),
        ("task", 'rows_lost = ___\n\nprint("rows lost:", rows_lost)\ncheck("A4", rows_lost)',
         'rows_lost = len(bus) - len(F)\n\nprint("rows lost:", rows_lost)\ncheck("A4", rows_lost)'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Hot for its workload (20 min) 🔗

EV04, 3–30 September: the amplifier's cooling path degraded. For four weeks it ran about 3 °C hot **for its drive level**.

### B1 ✍️ Build the relationship
Amplifier temperature divided by RF drive: *degrees per percent of drive*. Fill in the formula."""),
        ("task", 'temp_per_drive = ___\n\nassert temp_per_drive is not None, "✍️ Fill in the formula first."\nprint(temp_per_drive.describe().round(4))\ncheck("B1", temp_per_drive)',
         'temp_per_drive = bus["twta_temp_c"] / bus["rf_drive_pct"]\n\nassert temp_per_drive is not None, "✍️ Fill in the formula first."\nprint(temp_per_drive.describe().round(4))\ncheck("B1", temp_per_drive)'),
        ("md", """### 🧰 The toolbox
▶️ This cell defines today's helpers: the **scorer** (Week 4 Day 1's rules), `event_table()` (caught? how late? how many hours lit?), `steady_sun()` from last time, `lean_features()`, `chart_flags()` and `forest_flags()`. Read them: each is a few lines.
`train` = the reference months, **January to August**."""),
        ("code", toolbox + '\n\ntrain = bus.index < "2025-09-01"          # the reference months: January to August'),
        ("md", "▶️ First the old way: 3σ on the **raw** amplifier temperature (limits from January–August, steady sun)."),
        ("code", 'twta = bus["twta_temp_c"]\nref_t = twta[train & steady]\nceiling = ref_t.mean() + 3 * ref_t.std()\n'
                 'print(f"3-sigma ceiling: {ceiling:.2f} C  ·  hottest EV04 hour: {twta.loc[\'2025-09-03\':\'2025-09-30\'].max():.2f} C")\n\n'
                 'twta.plot(title="Raw amplifier temperature: four weeks of EV04, zero alarms", lw=.6)\n'
                 'plt.axhline(ceiling, color="#E5484D", ls="--"); plt.axvspan("2025-09-03", "2025-10-01", color="#C77700", alpha=.18); plt.show()'),
        ("md", """### B2 ✍️ A Week 3 chart on the new column
Same 3σ idea, but on `temp_per_drive`, with the normal learned from the training months. How many standard deviations wide is the band?"""),
        ("task", 'assert temp_per_drive is not None, "✍️ Finish B1 first."\nref = temp_per_drive[train]\nz_tpd = (temp_per_drive - ref.mean()) / ref.std()\n\nK = ___\n\nassert K is not None, "✍️ Fill in K first."\n'
                 'tpd_flags = z_tpd.abs() > K\ntpd_result = score_events(tpd_flags, labels)\n'
                 'print(f"normal: {ref.mean():.3f} ± {ref.std():.3f}  ·  ceiling {ref.mean() + K * ref.std():.3f}")\nprint(tpd_result)\ncheck("B2", tpd_result)',
         'assert temp_per_drive is not None, "✍️ Finish B1 first."\nref = temp_per_drive[train]\nz_tpd = (temp_per_drive - ref.mean()) / ref.std()\n\nK = 3\n\nassert K is not None, "✍️ Fill in K first."\n'
         'tpd_flags = z_tpd.abs() > K\ntpd_result = score_events(tpd_flags, labels)\n'
         'print(f"normal: {ref.mean():.3f} ± {ref.std():.3f}  ·  ceiling {ref.mean() + K * ref.std():.3f}")\nprint(tpd_result)\ncheck("B2", tpd_result)'),
        ("md", "▶️ The picture, and the event table: was it caught, how many hours late, and how many of its hours lit up?"),
        ("code", 'assert "tpd_flags" in globals(), "✍️ Finish B2 first."\ntemp_per_drive.plot(title="temp_per_drive: EV04 jumps out", lw=.6)\n'
                 'plt.axhline(ref.mean() + 3 * ref.std(), color="#E5484D", ls="--"); plt.axvspan("2025-09-03", "2025-10-01", color="#C77700", alpha=.18); plt.show()\n'
                 'event_table(tpd_flags, labels)'),
        ("md", """### B3 ✍️ A real catch, not a lucky blip
Last time the forest noticed EV04 on **1** hour. How many of EV04's 672 hours does this one column light up? Read it from the table."""),
        ("task", 'ev04_hours_lit = ___\n\ncheck("B3", ev04_hours_lit)', 'ev04_hours_lit = 605\n\ncheck("B3", ev04_hours_lit)'),
        ("md", """### 🪤 The 29σ trap
▶️ The original code book builds a cleverer feature: an **expected** temperature from drive level and the season (sin/cos of the day of year), fitted on **January to May**, then the residual = actual − expected. Look how far out EV04 sits… then look at the rest of the year."""),
        ("code", 'from sklearn.linear_model import LinearRegression\n\ndoy = bus.index.day_of_year\n'
                 'design = pd.DataFrame({"drive": bus["rf_drive_pct"], "sin": np.sin(2 * np.pi * doy / 365),\n'
                 '                       "cos": np.cos(2 * np.pi * doy / 365)}, index=bus.index)\n'
                 'fit = bus.index < "2025-06-01"                     # the code book fits on January to May\n'
                 'expected = LinearRegression().fit(design[fit], twta[fit]).predict(design)\n'
                 'resid = twta - expected\nresid_sd = resid[fit].std()\n'
                 'ev04_sigma = (resid.loc["2025-09-03":"2025-09-30"].mean() - resid[fit].mean()) / resid_sd\n'
                 'print(f"residual spread Jan-May: {resid_sd:.3f} C  ·  EV04 sits {ev04_sigma:.1f} sigma out")\n\n'
                 'resid_flags = (resid - resid[fit].mean()).abs() > 3 * resid_sd\n'
                 'resid.plot(title="The code book residual: fitted Jan-May, carried to December", lw=.6)\n'
                 'plt.axhspan(resid[fit].mean() - 3 * resid_sd, resid[fit].mean() + 3 * resid_sd, color="#9DB0C6", alpha=.3)\n'
                 'plt.axvspan("2025-09-03", "2025-10-01", color="#C77700", alpha=.18); plt.show()\nprint(score_events(resid_flags, labels))'),
        ("md", """### B4 ✍️ How many October–December hours does it flag?
`resid_flags` is True for every hour outside the ±3σ band. Count the ones from 1 October onwards."""),
        ("task", 'octdec_flagged = ___\n\nprint(octdec_flagged, "of", len(resid_flags.loc["2025-10-01":]), "hours")\ncheck("B4", octdec_flagged)',
         'octdec_flagged = resid_flags.loc["2025-10-01":].sum()\n\nprint(octdec_flagged, "of", len(resid_flags.loc["2025-10-01":]), "hours")\ncheck("B4", octdec_flagged)'),
        ("md", """### B5 ✍️ True or False?
*"A feature that puts the fault 29σ out is always better than one that puts it 4σ out."* Answer `True` or `False` (no quotes)."""),
        ("task", 'big_sigma_always_wins = ___\n\ncheck("B5", big_sigma_always_wins)', 'big_sigma_always_wins = False\n\ncheck("B5", big_sigma_always_wins)'),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Fewer, better eyes (20 min) ✂️

### C1 ✍️ Find the twins
▶️ + ✍️ The code book's 32 columns, every pair ranked by how alike they are. Pairs above about **0.98** are duplicates. Fill in that cutoff."""),
        ("task", 'c = F.corr().abs()\npairs = c.where(np.triu(np.ones(c.shape), k=1).astype(bool)).stack().sort_values(ascending=False)\nprint(pairs.head(6).round(3))\n\n'
                 'CUTOFF = ___\n\nassert CUTOFF is not None, "✍️ Fill in CUTOFF first."\nn_twins = int((pairs > CUTOFF).sum())\nprint("pairs above the cutoff:", n_twins)\ncheck("C1", n_twins)',
         'c = F.corr().abs()\npairs = c.where(np.triu(np.ones(c.shape), k=1).astype(bool)).stack().sort_values(ascending=False)\nprint(pairs.head(6).round(3))\n\n'
         'CUTOFF = 0.98\n\nassert CUTOFF is not None, "✍️ Fill in CUTOFF first."\nn_twins = int((pairs > CUTOFF).sum())\nprint("pairs above the cutoff:", n_twins)\ncheck("C1", n_twins)'),
        ("md", """### C2 ✍️ The kitchen-sink forest
Fit the forest on all 32 columns (reference = training months in steady sun) and score the whole year. Last time we let it flag **half a percent** of hours. Fill that in as a fraction. (Takes a few seconds.)"""),
        ("task", 'sink_steady = steady.reindex(F.index)\nsink_train = pd.Series(train, index=bus.index).reindex(F.index)\n\nCONTAMINATION = ___\n\n'
                 'assert CONTAMINATION is not None, "✍️ Fill in CONTAMINATION first."\n'
                 'sink_flags = forest_flags(F, sink_train & sink_steady, sink_steady, contamination=CONTAMINATION).reindex(bus.index, fill_value=False)\n'
                 'sink_result = score_events(sink_flags, labels)\nprint(sink_result)\ncheck("C2", sink_result)',
         'sink_steady = steady.reindex(F.index)\nsink_train = pd.Series(train, index=bus.index).reindex(F.index)\n\nCONTAMINATION = 0.005\n\n'
         'assert CONTAMINATION is not None, "✍️ Fill in CONTAMINATION first."\n'
         'sink_flags = forest_flags(F, sink_train & sink_steady, sink_steady, contamination=CONTAMINATION).reindex(bus.index, fill_value=False)\n'
         'sink_result = score_events(sink_flags, labels)\nprint(sink_result)\ncheck("C2", sink_result)'),
        ("md", """### C3 ✍️ The lean five
▶️ `lean_features(bus)` keeps four health sensors and adds **one** relationship, `temp_per_drive`. (RF drive and raw temperature drift with the load and the seasons, so they stay out.)
✍️ Set `FIT_ROWS` to the **reference rows**: the training months **and** steady sun."""),
        ("task", 'X = lean_features(bus)\nprint(list(X.columns))\n\nFIT_ROWS = ___\n\nassert FIT_ROWS is not None, "✍️ Fill in FIT_ROWS first."\nlean_flags = forest_flags(X, FIT_ROWS, steady)\n\nlean_result = score_events(lean_flags, labels)\nprint(lean_result)\ncheck("C3", lean_flags)',
         'X = lean_features(bus)\nprint(list(X.columns))\n\nFIT_ROWS = train & steady\n\nassert FIT_ROWS is not None, "✍️ Fill in FIT_ROWS first."\nlean_flags = forest_flags(X, FIT_ROWS, steady)\n\nlean_result = score_events(lean_flags, labels)\nprint(lean_result)\ncheck("C3", lean_flags)'),
        ("md", "▶️ Side by side, event by event."),
        ("code", 'assert "sink_flags" in globals() and "lean_flags" in globals(), "✍️ Finish C2 and C3 first."\npd.concat({"kitchen sink (32)": event_table(sink_flags, labels)[["caught", "hours_late", "hours_flagged"]],\n'
                 '           "lean 5": event_table(lean_flags, labels)[["caught", "hours_late", "hours_flagged"]]}, axis=1)'),
        ("md", """### C4 ✍️ Right answer, right reason
A flag with no reason won't survive the duty engineer. **z-score** = how many σ a feature sits from its normal (training months, steady sun).
▶️ + ✍️ For EV04's flagged hours, which feature has the biggest |z| most often?"""),
        ("task", 'assert "lean_flags" in globals(), "✍️ Finish C3 first."\nref_x = X[train & steady]\nz = (X - ref_x.mean()) / ref_x.std()\n\nev04_flagged = lean_flags & (bus.index >= "2025-09-03") & (bus.index < "2025-10-01")\nprint(z[ev04_flagged].abs().idxmax(axis=1).value_counts())\n\n'
                 'top_reason_ev04 = ___\n\ncheck("C4", top_reason_ev04)',
         'assert "lean_flags" in globals(), "✍️ Finish C3 first."\nref_x = X[train & steady]\nz = (X - ref_x.mean()) / ref_x.std()\n\nev04_flagged = lean_flags & (bus.index >= "2025-09-03") & (bus.index < "2025-10-01")\nprint(z[ev04_flagged].abs().idxmax(axis=1).value_counts())\n\n'
         'top_reason_ev04 = "temp_per_drive"\n\ncheck("C4", top_reason_ev04)'),
        ("md", "▶️ The same check for every event: the median z of its flagged hours. Read each row like an engineer."),
        ("code", 'assert "z" in globals(), "✍️ Finish C4 first."\nreasons = {}\nfor _, ev in labels.iterrows():\n    hours = lean_flags & (bus.index >= ev["start"]) & (bus.index <= ev["end"])\n    reasons[ev["event_id"]] = z[hours].median()\npd.DataFrame(reasons).T.round(1)'),
        ("md", """### C5 ✍️ True or False?
*"5 of 5 on the whole year is an honest exam score for this forest."* Think about which months it trained on. Answer `True` or `False`."""),
        ("task", 'honest_exam = ___\n\ncheck("C5", honest_exam)', 'honest_exam = False\n\ncheck("C5", honest_exam)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: race the old chart
Give the **Week 4 control chart** the same five eyes: `chart_flags()` flags an hour if **any** column is more than 3σ from its normal. Set `CHART_FIT_ROWS` to the same reference rows as the forest. Who wins on the whole year?"""),
        ("task", 'CHART_FIT_ROWS = ___\n\nassert CHART_FIT_ROWS is not None, "✍️ Fill in CHART_FIT_ROWS first."\nchart_lean = chart_flags(X, CHART_FIT_ROWS, steady)\n\nchart_result = score_events(chart_lean, labels)\nprint("forest:", lean_result)\nprint("chart: ", chart_result)\ncheck("BONUS", chart_result)',
         'CHART_FIT_ROWS = train & steady\n\nassert CHART_FIT_ROWS is not None, "✍️ Fill in CHART_FIT_ROWS first."\nchart_lean = chart_flags(X, CHART_FIT_ROWS, steady)\n\nchart_result = score_events(chart_lean, labels)\nprint("forest:", lean_result)\nprint("chart: ", chart_result)\ncheck("BONUS", chart_result)'),

        ("md", """---
## 🏁 Final project · Checkpoint 3: 🛠️ Method drafted
Tick these off with your trainer today (on **your** data, on NIGCOMSAT systems, not in Colab):

- [ ] The **minimum method** for your brief runs end to end on your data (detection: a statistical baseline **plus** a multivariate detector on trailing features · degradation/capacity: a trend-to-threshold estimate · forecasting: a baseline forecast **plus** a regression)
- [ ] Your **"normal" in writing**: the states or modes (eclipse, rain, weekend…) and what you take away first (season, drive level…)
- [ ] Your **features** listed, each passing the **14:00 test**, at least one carrying history or a relationship
- [ ] Your **reference period**: months your unit agrees were quiet, written down
- [ ] The **simple baseline** you will race next checkpoint
- [ ] Raw data **not** on GitHub; nothing restricted pasted into an AI tool

Next checkpoint: **Week 5 · Day 3: honest test** ⚖️ (split by time + a baseline comparison table)

## Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- **The model cannot tell time.** Lags (`shift(1)`) and rolling windows (`rolling(24)`) give each row a memory.
- **The 14:00 test:** past only. `shift(-1)` and `center=True` read tomorrow's newspaper.
- **One relationship column** (`temp_per_drive`) turned four invisible weeks into 605 lit hours with zero false alarms.
- **A big sigma is not the test.** The 29σ feature flagged every Oct–Dec hour. Check features on months they never saw.
- **Fewer, sharper features:** prune twins above 0.98; 5 good columns caught what 32 missed.
- **Explain every flag** with z-scores: right answer, right reason.

**Next time:** *No expo! Honest train/test splits + Quiz 3.* ⚖️

<sub>Data: synthetic teaching datasets from the original Week 5 code book (`Time-series/week-05`). Safe to use with AI tools; real NIGCOMSAT data is not.</sub>"""),
    ]
