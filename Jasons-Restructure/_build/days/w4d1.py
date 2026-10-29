"""Week 4 · Day 1: Scoring a Detector + Quiz 2."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

import quizkit
from common import BRAND as B, ORIGINALS, read_labels
from svgcharts import _scale
from webdeck import logos_title_block

CODE = "W4D1"
TITLE = "Scoring a Detector + Quiz 2"
QUIZ_SEED = 4104

D4 = ORIGINALS / "week-04" / "data"
GRID, AXIS = "#24384F", "#9DB0C6"
RED, GOLD, GREEN = "#FF6B6F", "#F5B83D", "#3CCB7F"


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# =============================================================================
# DATA + THE SAME DETECTORS THE NOTEBOOK BUILDS (every number on the slides comes from here)
# =============================================================================
def score_events(flags, labels, source_file, tol="1h"):
    events = labels[labels["source_file"] == source_file]
    tol = pd.Timedelta(tol)
    caught, inside_any = 0, pd.Series(False, index=flags.index)
    for _, ev in events.iterrows():
        window = (flags.index >= ev["start"] - tol) & (flags.index <= ev["end"] + tol)
        if flags[window].any():
            caught += 1
        inside_any |= window
    false_alarms = int((flags & ~inside_any).sum())
    alarms = caught + false_alarms
    return {"events": len(events), "caught": caught, "false_alarms": false_alarms,
            "recall": round(caught / len(events), 3),
            "precision": round(caught / alarms, 3) if alarms else float("nan")}


def cusum(z, k=0.5, h=5.0):
    s, out = 0.0, []
    for v in z:
        s = max(0.0, s + v - k)
        if s > h:
            out.append(True)
            s = 0.0
        else:
            out.append(False)
    return pd.Series(out, index=z.index)


@lru_cache(maxsize=1)
def facts():
    bus = pd.read_csv(D4 / "bus_power_telemetry_hourly.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    tw = pd.read_csv(D4 / "twta_thermal_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    bat = pd.read_csv(D4 / "battery_health_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    rf = pd.read_csv(D4 / "rf_link_quality_hourly.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    labels = read_labels(D4 / "telemetry_anomaly_labels.csv")
    F = {"bus": bus, "tw": tw, "bat": bat, "rf": rf, "labels": labels}
    F["n_readings"] = len(bus) + len(tw) + len(bat)
    F["acc_never"] = 1 - 6 / F["n_readings"]

    soc_flags = bus["battery_soc_pct"] < 82
    F["soc_flags"], F["soc"] = soc_flags, score_events(soc_flags, labels, "bus_power_telemetry_hourly.csv")

    x = bus["solar_array_current_a"]
    sun = x[bus["eclipse_flag"] == 0]
    m, s = sun.mean(), sun.std()
    F["cc_m"], F["cc_s"] = m, s
    cc_all = (x - m).abs() > 3 * s
    cc_sun = cc_all & (bus["eclipse_flag"] == 0)
    F["cc_all_flags"], F["cc_sun_flags"] = cc_all, cc_sun
    F["cc_all"] = score_events(cc_all, labels, "bus_power_telemetry_hourly.csv")
    F["cc_sun"] = score_events(cc_sun, labels, "bus_power_telemetry_hourly.csv")
    F["cc_fa_hours"] = sorted(set(cc_all[cc_all & (bus["eclipse_flag"] == 1)].index.hour))

    t = tw["twta_temp_c"]
    raw_flags = (t - t.mean()).abs() > 3 * t.std()
    F["tw_raw"] = score_events(raw_flags, labels, "twta_thermal_daily.csv", "1D")
    F["tw_ceiling"], F["tw_max"] = t.mean() + 3 * t.std(), t.max()
    doy = tw.index.day_of_year
    X = pd.DataFrame({"drive": tw["rf_drive_pct"], "sin": np.sin(2 * np.pi * doy / 365.25),
                      "cos": np.cos(2 * np.pi * doy / 365.25), "age": np.arange(len(tw)), "const": 1.0}, index=tw.index)
    fit = tw.index < pd.Timestamp("2025-01-01")
    coef, *_ = np.linalg.lstsq(X[fit].values, t[fit].values, rcond=None)
    resid = t - X.values @ coef
    rsd = resid[fit].std()
    F["resid"], F["resid_sd"] = resid, rsd
    rflags = resid.abs() > 3 * rsd
    F["resid_flags"], F["tw_resid"] = rflags, score_events(rflags, labels, "twta_thermal_daily.csv", "1D")
    cflags = cusum(resid / rsd)
    F["cusum_flags"], F["tw_cusum"] = cflags, score_events(cflags, labels, "twta_thermal_daily.csv", "1D")
    F["cusum_fa_dates"] = [d.date() for d in cflags[cflags & (cflags.index < pd.Timestamp("2025-05-12")) &
                                                     ~cflags.index.isin(pd.to_datetime(["2024-09-03", "2024-09-04"]))].index]
    F["ev04_z"] = resid.loc["2024-09-03"] / rsd

    cap = bat["est_capacity_ah"]
    F["cap"] = cap
    bflags = cap < 95
    F["bat_flags"], F["bat"] = bflags, score_events(bflags, labels, "battery_health_daily.csv", "1D")
    F["cap_min"] = cap.min()
    rate = cap.rolling(90).apply(lambda a: np.polyfit(np.arange(len(a)), a, 1)[0] * 365, raw=True)
    sflags = rate < -3.0
    F["rate"], F["slope"] = rate, score_events(sflags, labels, "battery_health_daily.csv", "1D")
    F["slope_first"] = sflags[sflags].index[0]
    F["slope_delay"] = (F["slope_first"] - pd.Timestamp("2025-04-01")).days

    cn = rf["cn_ratio_db"]
    rflag = cn < cn.mean() - 3 * cn.std()
    out = rf["link_margin_db"] < 0
    F["rf_flags"], F["rf_out"] = rflag, out
    F["rf_n_flags"], F["rf_real"] = int(rflag.sum()), int((rflag & out).sum())
    F["rf_rain"] = int((rf["rain_rate_mmhr"] > 0).sum())
    F["rf_in_rain"] = int((rflag & (rf["rain_rate_mmhr"] > 0)).sum())
    F["rf_line"] = cn.mean() - 3 * cn.std()

    F["pages_year"] = F["cc_all"]["false_alarms"] * 2
    F["hours_year"] = F["pages_year"] * 20 / 60
    return F


# =============================================================================
# LOCAL SVG HELPERS
# =============================================================================
def chart_svg(values, *, w=1400, h=420, ymin=None, ymax=None, color=B["blue_d"], band=None, hlines=(),
              dots=(), xlabels=(), yticks=(), stroke=2.5, delay=".3s", dur="2.4s", area=False):
    """Full-resolution line (no thinning, so single-hour spikes survive).
    band=(lo, hi, colour, label) · hlines=[(y, label, colour)] · dots=[(i, colour)] · xlabels=[(i, text)]"""
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
    if band:
        blo, bhi, bcol, blab = band
        o.append(f'<rect x="{L}" y="{Y(bhi):.1f}" width="{R - L}" height="{Y(blo) - Y(bhi):.1f}" fill="{bcol}" fill-opacity=".14"/>')
        if blab:
            o.append(f'<text x="{R - 12}" y="{Y(blo) + 26:.1f}" fill="{bcol}" font-size="20" font-weight="700" text-anchor="end">{blab}</text>')
    for (yv, lab) in yticks:
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L - 12}" y="{Y(yv) + 7:.1f}" fill="{AXIS}" font-size="19" text-anchor="end">{lab}</text>')
    for (i, lab) in xlabels:
        anchor = "start" if i == 0 else ("end" if i >= n - 1 else "middle")
        o.append(f'<text x="{X(i):.1f}" y="{h - 18}" fill="{AXIS}" font-size="19" text-anchor="{anchor}">{lab}</text>')
    pts = [(X(i), Y(v[i])) for i in range(n) if not np.isnan(v[i])]
    d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    if area:
        o.append(f'<path d="{d} L{pts[-1][0]:.1f},{Bm} L{pts[0][0]:.1f},{Bm} Z" fill="{color}" fill-opacity=".12" class="anim a-fade" style="--d:1.4s"/>')
    o.append(f'<path class="draw" style="--dur:{dur};--d:{delay}" d="{d}" fill="none" stroke="{color}" '
             f'stroke-width="{stroke}" stroke-linejoin="round" stroke-linecap="round"/>')
    for hl in hlines:
        yv, lab, col = hl[:3]
        left = len(hl) > 3 and hl[3] == "left"
        below = len(hl) > 4 and hl[4] == "below"
        ty = Y(yv) + 28 if below else Y(yv) - 10
        o.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{col}" stroke-width="2.5" stroke-dasharray="10 8"/>')
        o.append(f'<text x="{(L + 10) if left else (R - 6)}" y="{ty:.1f}" fill="{col}" font-size="21" font-weight="800" '
                 f'text-anchor="{"start" if left else "end"}">{lab}</text>')
    for k, (i, col) in enumerate(dots):
        o.append(f'<circle class="anim a-pop" style="--d:{2.2 + 0.01 * k:.2f}s;transform-origin:{X(i):.0f}px {Y(v[i]):.0f}px" '
                 f'cx="{X(i):.1f}" cy="{Y(v[i]):.1f}" r="8" fill="{col}" stroke="{B["space"]}" stroke-width="2"/>')
    o.append("</svg>")
    return "".join(o)


def dots_grid_svg(n, special, *, cols=106, cell=10.5, gap=2.6):
    """n tiny squares as ONE path (cheap), with the special ones drawn on top as pulsing red dots."""
    rows = int(np.ceil(n / cols))
    w, h = cols * (cell + gap), rows * (cell + gap)
    segs = []
    for i in range(n):
        r, c = divmod(i, cols)
        segs.append(f"M{c * (cell + gap):.1f} {r * (cell + gap):.1f}h{cell}v{cell}h-{cell}z")
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" width="100%" style="max-width:{w:.0f}px;display:block">',
         f'<path class="anim a-fade" style="--d:.2s" d="{"".join(segs)}" fill="#2A4566"/>']
    for k, i in enumerate(special):
        r, c = divmod(i, cols)
        cx, cy = c * (cell + gap) + cell / 2, r * (cell + gap) + cell / 2
        o.append(f'<circle class="anim a-pop" style="--d:{1.0 + k * .2:.1f}s;transform-origin:{cx:.0f}px {cy:.0f}px" cx="{cx:.1f}" cy="{cy:.1f}" r="13" fill="{RED}"/>')
        o.append(f'<circle class="pulse" cx="{cx:.1f}" cy="{cy:.1f}" r="22" fill="none" stroke="{RED}" stroke-width="3"/>')
    o.append("</svg>")
    return "".join(o)


def timeline_svg(F, w=1420, h=330):
    """Three lanes (one per file), each event marked where it sits in its own file."""
    lanes = [("🔋 Bus power · 120 days · hourly", F["bus"].index, ["EV01", "EV02", "EV03"], B["blue_d"]),
             ("🌡️ Amplifier (TWTA) · 2 years · daily", F["tw"].index, ["EV04", "EV05"], B["teal_d"]),
             ("🪫 Battery · 3 years · daily", F["cap"].index, ["EV06"], GOLD)]
    lab = F["labels"].set_index("event_id")
    L, R = 470, w - 30
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block">']
    for k, (name, idx, evs, col) in enumerate(lanes):
        y = 50 + k * 105
        o.append(f'<text x="0" y="{y + 8}" fill="#EAF2FB" font-size="25" font-weight="700">{name}</text>')
        o.append(f'<line x1="{L}" x2="{R}" y1="{y}" y2="{y}" stroke="{GRID}" stroke-width="10" stroke-linecap="round"/>')
        t0, t1 = idx[0], idx[-1]
        span = (t1 - t0).total_seconds()

        def X(t):
            return L + (pd.Timestamp(t) - t0).total_seconds() / span * (R - L)
        for j, e in enumerate(evs):
            s0, s1 = X(lab.loc[e, "start"]), X(lab.loc[e, "end"])
            d = 0.4 + 0.3 * (k * 2 + j)
            if s1 - s0 > 14:   # long event = a bar
                o.append(f'<rect class="anim a-fade" style="--d:{d:.1f}s" x="{s0:.1f}" y="{y - 13}" width="{s1 - s0:.1f}" height="26" rx="13" fill="{col}"/>')
                tx = (s0 + s1) / 2
            else:              # short event = a dot
                o.append(f'<circle class="anim a-pop" style="--d:{d:.1f}s;transform-origin:{s0:.0f}px {y}px" cx="{s0:.1f}" cy="{y}" r="15" fill="{col}"/>')
                tx = s0
            typ = lab.loc[e, "type"].replace("_", " ")
            o.append(f'<text class="anim a-fade" style="--d:{d + .2:.1f}s" x="{tx:.1f}" y="{y + 46}" fill="{col}" font-size="20" font-weight="800" text-anchor="middle">{e} · {typ}</text>')
    o.append("</svg>")
    return "".join(o)


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    F = facts()
    bus, tw, rf = F["bus"], F["tw"], F["rf"]

    # SoC through the eclipse season (hourly, full resolution so every dip shows)
    win = bus.loc["2025-09-01":"2025-10-20"]
    i0 = bus.index.get_loc(win.index[0])
    soc_dots = [bus.index.get_loc(t) - i0 for t in F["soc_flags"][F["soc_flags"]].index if t in win.index]
    soc_chart = chart_svg(win["battery_soc_pct"].values, h=360, ymin=74, ymax=102, color=B["blue_d"],
                          hlines=[(82, "alarm floor: 82%", RED)], dots=[(i, RED) for i in soc_dots],
                          yticks=[(80, "80%"), (90, "90%"), (100, "100%")],
                          xlabels=[(0, "1 Sep"), (len(win) // 2, "eclipse season"), (len(win) - 1, "20 Oct")])

    # array current, whole file, 3-sigma band
    x = bus["solar_array_current_a"].values
    m, s = F["cc_m"], F["cc_s"]
    ecl = [i for i, f in enumerate(F["cc_all_flags"] & (bus["eclipse_flag"] == 1)) if f]
    spk = [i for i, f in enumerate(F["cc_sun_flags"]) if f]
    cc_chart = chart_svg(x, h=360, ymin=-1, ymax=31, color=B["blue_d"], stroke=1.6,
                         band=(m - 3 * s, m + 3 * s, B["teal_d"], "normal sunlit band (±3σ)"),
                         dots=[(i, "#8FA3BA") for i in ecl] + [(i, GOLD) for i in spk],
                         yticks=[(0, "0 A"), (15, "15 A"), (28, "28 A")],
                         xlabels=[(0, "Aug"), (len(x) // 3, "Sep"), (2 * len(x) // 3, "Oct"), (len(x) - 1, "Nov")])

    # TWTA: raw vs residual
    t = tw["twta_temp_c"].values
    n = len(t)

    def ti(d):
        return int((pd.Timestamp(d) - tw.index[0]).days)
    tw_raw = chart_svg(t, w=680, h=330, ymin=58, ymax=71, color=B["teal_d"], stroke=2,
                       hlines=[(F["tw_ceiling"], f"3σ ceiling {F['tw_ceiling']:.1f} °C", RED)],
                       yticks=[(60, "60°"), (65, "65°"), (70, "70°")], xlabels=[(0, "2024"), (n - 1, "2025")])
    r = F["resid"].values
    rsd = F["resid_sd"]
    rflag_idx = [i for i, f in enumerate(F["resid_flags"]) if f]
    tw_res = chart_svg(r, w=680, h=330, ymin=-2, ymax=6, color=B["teal_d"], stroke=2,
                       band=(-3 * rsd, 3 * rsd, "#9DB0C6", ""),
                       dots=[(ti("2024-09-03"), GOLD), (ti("2024-09-04"), GOLD), (ti("2025-05-12"), GOLD)],
                       yticks=[(0, "0°"), (3, "+3°"), (6, "+6°")], xlabels=[(0, "2024"), (n - 1, "2025")])

    # battery: capacity vs 95 Ah, and the 90-day fade rate
    capv = F["cap"]
    nb = len(capv)
    knee = int((pd.Timestamp("2025-04-01") - capv.index[0]).days)
    bat_chart = chart_svg(capv.values, w=680, h=330, ymin=94, ymax=104, color=GOLD, stroke=2.4,
                          hlines=[(95, "fixed floor 95 Ah", RED, "left")], dots=[(knee, RED)],
                          yticks=[(95, "95"), (100, "100"), (104, "104 Ah")],
                          xlabels=[(0, "2023"), (nb - 1, "2025")])
    rate = F["rate"].values
    first = int((F["slope_first"] - capv.index[0]).days)
    rate_chart = chart_svg(rate, w=680, h=330, ymin=-4.2, ymax=-1.4, color=GOLD, stroke=2.4,
                           hlines=[(-3.0, "alarm: faster than −3 Ah/yr", RED, "left", "below")], dots=[(first, RED)],
                           yticks=[(-2, "−2"), (-3, "−3"), (-4, "−4 Ah/yr")],
                           xlabels=[(0, "2023"), (nb - 1, "2025")])

    # RF: C/N with the naive 3-sigma line
    cn = rf["cn_ratio_db"].values
    real = [i for i, (f, o) in enumerate(zip(F["rf_flags"], F["rf_out"])) if f and o]
    held = [i for i, (f, o) in enumerate(zip(F["rf_flags"], F["rf_out"])) if f and not o]
    rf_chart = chart_svg(cn, h=330, ymin=3, ymax=16, color=B["blue_d"], stroke=1.6,
                         hlines=[(F["rf_line"], "", RED)],
                         dots=[(i, RED) for i in real] + [(i, GOLD) for i in held],
                         yticks=[(5, "5 dB"), (10, "10 dB"), (15, "15 dB")],
                         xlabels=[(0, "1 Aug"), (len(cn) - 1, "31 Aug")])

    # scoreboard rows
    def pct(v):
        return "—" if v != v else f"{v:.2f}"
    board = [
        ("🔋", "SoC floor &lt; 82%", "bus power", F["soc"], "W3D1"),
        ("📊", "Control chart, all hours", "bus power", F["cc_all"], "W3D2"),
        ("🌞", "Control chart, sunlit only", "bus power", F["cc_sun"], "W3D2"),
        ("🌡️", "Raw 3σ on temperature", "TWTA", F["tw_raw"], "W3D2"),
        ("🧮", "Residual 3σ (drive + season + age)", "TWTA", F["tw_resid"], "W3D2"),
        ("➕", "CUSUM on the residual", "TWTA", F["tw_cusum"], "W3D3"),
        ("🪫", "Fixed floor 95 Ah", "battery", F["bat"], "W3D3"),
    ]
    rows = ""
    for k, (e, name, watch, r_, day) in enumerate(board):
        good = r_["recall"] == 1 and r_["false_alarms"] == 0
        bad = r_["recall"] == 0
        col = GREEN if good else (RED if bad else GOLD)
        rows += (f'<tr class="anim a-left" style="--d:{.2 + k * .18:.2f}s">'
                 f'<td style="font-size:26px">{e}</td><td><b>{name}</b> <span class="small" style="font-size:17px">· {watch} · {day}</span></td>'
                 f'<td class="mono" style="color:{col};font-weight:800">{r_["caught"]}/{r_["events"]}</td>'
                 f'<td class="mono">{r_["false_alarms"]}</td><td class="mono" style="color:{col}">{pct(r_["recall"])}</td>'
                 f'<td class="mono" style="color:{col}">{pct(r_["precision"])}</td></tr>')
    table_css = ("<style>.sb{width:100%;border-collapse:separate;border-spacing:0 6px;font-size:23px}"
                 ".sb th{color:#9DB0C6;font-size:19px;text-align:left;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:0 14px}"
                 ".sb td{background:#12233A;padding:7px 14px}.sb td:first-child{border-radius:14px 0 0 14px;width:60px;text-align:center}"
                 ".sb td:last-child{border-radius:0 14px 14px 0}</style>")

    soc, cca, ccs = F["soc"], F["cc_all"], F["cc_sun"]
    twr, twc = F["tw_resid"], F["tw_cusum"]
    acc = F["acc_never"] * 100

    # 4,706 readings with the 6 events placed in proportion to where they sit
    special = [300, 1350, 2050, 2600, 3420, 4400]

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:40px;top:150px;width:560px;height:560px">
  <svg viewBox="0 0 560 560" width="560" height="560">
    <circle cx="280" cy="280" r="250" fill="none" stroke="#24384F" stroke-width="22"/>
    <circle cx="280" cy="280" r="180" fill="none" stroke="#3B8BE0" stroke-width="22" class="anim a-fade" style="--d:.3s"/>
    <circle cx="280" cy="280" r="110" fill="none" stroke="#16A394" stroke-width="22" class="anim a-fade" style="--d:.5s"/>
    <circle cx="280" cy="280" r="42" fill="#F5B83D" class="anim a-pop" style="--d:.8s;transform-origin:280px 280px"/>
    <path class="draw" style="--d:1s;--dur:1.2s" d="M520 40 L300 262" stroke="#EAF2FB" stroke-width="8" stroke-linecap="round"/>
    <text x="280" y="292" text-anchor="middle" font-size="30" font-weight="800" fill="#0B1622" class="anim a-fade" style="--d:1.6s">✓</text>
  </svg></div>
<div style="max-width:900px;margin-top:40px">
  <div class="kicker anim">Week 4 · Day 1</div>
  <h1 class="anim" style="--d:.2s">Scoring a<br>Detector<br><span class="hl">+ Quiz 2</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">The answer key comes out.<br>Every alarm from last week gets a report card. 🎯</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex">{logos_title_block()}</div>
</div>""",
          "Welcome back. For three days they built detectors and argued about which is better. Today we stop arguing: the answer key comes out and every detector is scored with the same rules. Then Quiz 2."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Rules first. Then the report cards.</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:300px;padding:40px 28px"><div class="icon">🔑</div><h3>Open the key</h3><p class="small">6 real events, finally revealed</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:300px;padding:40px 28px"><div class="icon">🎯</div><h3>Score every alarm</h3><p class="small">recall, precision, false alarms</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:300px;padding:40px 28px"><div class="icon">💸</div><h3>Count the cost</h3><p class="small">false alarms → engineer hours</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:260px;padding:40px 28px"><div class="icon">📝</div><h3>Quiz 2</h3><p class="small">all of Week 3</p></div>
</div>
<div class="row anim" style="--d:1.8s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 25 min slides</span><span class="pill teal">🧑🏾‍💻 50 min hands-on</span><span class="pill gold">📝 25 min quiz + marking</span><span class="pill">🏁 10 min wrap-up</span>
</div>""",
          "Four moves. The quiz sits after the hands-on block so people have just used every idea it asks about."),

        # 3 ─ two guards
        S("""
<div class="kicker anim">Quick question</div>
<h2 class="anim" style="--d:.1s">Which mai-guard do you hire? 💂🏾</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">📢</div><h3>Musa shouts “Thief!” at every goat</h3>
    <p class="muted">10 thieves came this year. Musa caught <b style="color:#fff">9</b>.<br>He also shouted <b style="color:#fff">200 times</b>. The estate no longer wakes up.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill teal">catches almost everything</span><span class="pill bad">wakes the whole estate</span></div></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">😴</div><h3>Ade sleeps all night</h3>
    <p class="muted">Ade never shouts. On <b style="color:#fff">355 of 365</b> nights there was no thief, so Ade was “right” <b style="color:#fff">97% of the time</b>.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill gold">“97% accurate”</span><span class="pill bad">caught zero thieves</span></div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:36px;text-align:center">Neither. Today you learn the two numbers that expose both of them. 🎯</p>""",
          "Get the room to vote. Most pick Musa. Then point out Ade's 97 percent: a number that sounds great and means nothing. That's accuracy, and it's the trap."),

        # 4 ─ accuracy lies
        S(f"""
<div class="kicker anim">Why “accuracy” lies</div>
<h2 class="anim" style="--d:.1s">A detector that <span class="bad">never fires</span> scores <span class="hl">{acc:.2f}%</span></h2>
<div class="row" style="gap:40px;margin-top:10px;align-items:center">
  <div class="card anim" style="--d:.2s;flex:1.6;padding:22px">{dots_grid_svg(F["n_readings"], special)}</div>
  <div class="col" style="flex:1;gap:20px">
    <div class="card anim" style="--d:.6s;padding:24px"><div class="stat count" style="font-size:80px" data-to="{F['n_readings']}" data-d=".7">0</div><div class="stat-label">readings in last week's three files</div></div>
    <div class="card anim" style="--d:.9s;padding:24px;border-color:#E5484D"><div class="stat bad" style="font-size:80px">6</div><div class="stat-label">real events hiding inside them</div></div>
    <p class="anim" style="--d:1.3s;font-size:26px">Say “no problem” every time and you're right {F['n_readings'] - 6:,} times out of {F['n_readings']:,}. <b class="hl">Useless.</b></p>
  </div>
</div>""",
          f"Quiz question 1. {F['n_readings']} readings: 2,880 bus-power hours, 730 TWTA days, 1,096 battery days. 6 events. Never firing = 1 − 6/{F['n_readings']} = {acc:.2f}%. When events are rare, accuracy rewards doing nothing. We never report it for rare events."),

        # 5 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">The answer key 🔑</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">For three days it was hidden. Now we open it.</p>""",
          "Section break. Remind them the original programme deliberately withheld the labels until people had built their own detectors.", cls="center"),

        # 6 ─ the six events
        S(f"""
<div class="kicker anim">telemetry_anomaly_labels.csv · 6 rows</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Six real events, three files</h2>
<div class="card anim" style="--d:.2s;padding:26px 30px">{timeline_svg(F)}</div>
<div class="row anim" style="--d:2.2s;margin-top:22px;gap:14px;align-items:center">
  <span class="pill">3 spikes in bus power</span><span class="pill teal">1 spike + 1 level shift in the amplifier</span><span class="pill gold">1 slow drift in the battery</span>
  <span class="small" style="margin-left:auto">EV05 lasts 233 days · EV06 lasts 275</span>
</div>""",
          "Walk the three lanes. Dots are short events (an hour or two). Bars are long events: EV05 is the cooling-loop blockage that lasts to the end of the file; EV06 is the battery fade speeding up. "
          "Note: the original labels file crashes pandas because of a stray comma in EV04's description; our load_labels() repairs it."),

        # 7 ─ rules
        S("""
<div class="kicker anim">Write the rules BEFORE you compute anything</div>
<h2 class="anim" style="--d:.1s">Four scoring rules</h2>
<div class="grid2" style="margin-top:14px;gap:24px">
  <div class="card anim a-pop" style="--d:.3s;padding:26px 30px"><div class="row" style="gap:18px;align-items:center"><span class="num">1</span><h3 style="margin:0">One flag inside = caught</h3></div>
    <p class="muted" style="margin-top:10px">A flag anywhere inside the event's start→end (±1 step) catches it.</p></div>
  <div class="card anim a-pop" style="--d:.5s;padding:26px 30px"><div class="row" style="gap:18px;align-items:center"><span class="num">2</span><h3 style="margin:0">Many flags = still ONE catch</h3></div>
    <p class="muted" style="margin-top:10px">EV02 flagged on both of its hours is one catch, not two.</p></div>
  <div class="card anim a-pop" style="--d:.7s;padding:26px 30px"><div class="row" style="gap:18px;align-items:center"><span class="num">3</span><h3 style="margin:0">Outside every event = false alarm</h3></div>
    <p class="muted" style="margin-top:10px">Each one is a page to the duty engineer at 2 a.m. 📟</p></div>
  <div class="card anim a-pop glow" style="--d:.9s;padding:26px 30px"><div class="row" style="gap:18px;align-items:center"><span class="num">4</span><h3 style="margin:0">A 233-day event is ONE event</h3></div>
    <p class="muted" style="margin-top:10px">Flag one day of EV05 and you caught it once, not 233 times.</p></div>
</div>
<p class="anim" style="--d:1.3s;margin-top:24px;text-align:center">Decide the rules first, so nobody can bend them after seeing the score. 🧑🏾‍⚖️</p>""",
          "Quiz question 4 is rule 4. Rule 3 is where alarm fatigue lives. Agree these out loud with the room before anyone runs code."),

        # 8 ─ recall vs precision
        S("""
<div class="kicker anim">The two numbers that matter</div>
<h2 class="anim" style="--d:.1s">Recall and precision</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;border-color:#16A394"><div class="icon">🕸️</div><h3>Recall</h3>
    <p style="font-size:28px">Of the <b>real events</b>, how many did we catch?</p>
    <pre class="code" style="font-size:24px;margin-top:16px">recall = caught / real_events</pre>
    <p class="muted" style="margin-top:12px">Musa: 9 ÷ 10 = <b class="good">0.90</b> 👍🏾</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#F5B83D"><div class="icon">📟</div><h3>Precision</h3>
    <p style="font-size:28px">When it <b>shouts</b>, how often is something really there?</p>
    <pre class="code" style="font-size:24px;margin-top:16px">precision = caught / all_alarms</pre>
    <p class="muted" style="margin-top:12px">Musa: 9 ÷ 200 = <b class="bad">0.045</b> 😩</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:28px;text-align:center">Ade the sleeper: recall <b class="bad">0</b>. Precision? He never shouted, so there's nothing to measure.</p>""",
          "Quiz questions 2 and 3. Recall answers 'did we miss anything?'. Precision answers the duty engineer's question: 'when this thing pages me, is it real?'"),

        # 9 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Report cards 🎯</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Same scorer. Same rules. Every detector from last week.</p>""",
          "Section break.", cls="center"),

        # 10 ─ SoC floor
        S(f"""
<div class="kicker anim">Detector 1 · the alarm software's fixed floor</div>
<h2 class="anim" style="--d:.1s;font-size:54px">State of charge &lt; 82%: <span class="bad">{soc['false_alarms']} alarms, 0 real</span></h2>
<div class="card anim" style="--d:.2s;padding:18px 20px">{soc_chart}</div>
<div class="row anim" style="--d:2.6s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill bad">recall {soc['recall']:.2f}</span><span class="pill bad">precision {soc['precision']:.2f}</span>
  <span class="pill gold">every alarm = a normal eclipse night</span>
  <span class="small" style="margin-left:auto">real faults were in array current, not here</span>
</div>""",
          f"The floor fires {soc['false_alarms']} times, every one on a deep eclipse night, when the battery is doing its job. It catches none of the 3 solar-array dropouts. Correct alarms, useless alarms."),

        # 11 ─ control chart
        S(f"""
<div class="kicker anim">Detector 2 · 3σ control chart on solar-array current</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Same chart, one condition, a different life</h2>
<div class="card anim" style="--d:.2s;padding:18px 20px">{cc_chart}</div>
<div class="grid2" style="margin-top:18px;gap:24px">
  <div class="card anim a-left" style="--d:2.6s;padding:16px 24px"><p style="font-size:24px"><b>All hours:</b> caught <b class="good">{cca['caught']}/3</b> · <b class="bad">{cca['false_alarms']} false alarms</b><br><span class="muted">grey dots, every one at {F['cc_fa_hours'][0]}:00 UTC (eclipse) · precision {cca['precision']:.2f}</span></p></div>
  <div class="card anim a-right glow" style="--d:2.9s;padding:16px 24px"><p style="font-size:24px"><b>Sunlit hours only:</b> caught <b class="good">{ccs['caught']}/3</b> · <b class="good">{ccs['false_alarms']} false alarms</b><br><span class="muted">gold dots = the real dropouts · precision</span> <b class="good">{ccs['precision']:.2f}</b> ✅</p></div>
</div>""",
          f"Band = sunlit mean {m:.2f} A ± 3 × {s:.3f} A. Gold dots are the real dropouts (about 15.5 A). Grey dots are eclipse hours: physics, not faults. Adding eclipse_flag == 0 takes precision from {cca['precision']:.2f} to {ccs['precision']:.2f}. Condition on the known cause; don't just widen the band."),

        # 12 ─ TWTA raw vs residual
        S(f"""
<div class="kicker anim">Detectors 3 + 4 · the amplifier (TWTA)</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Raw values hide it. The residual shouts.</h2>
<div class="grid2" style="margin-top:6px;gap:26px">
  <div class="card anim a-left" style="--d:.2s;padding:18px 20px"><h3 style="font-size:26px">🌡️ Raw temperature, 3σ ceiling</h3>{tw_raw}
    <p style="font-size:23px;margin-top:8px">Highest day {F['tw_max']:.1f} °C never reaches {F['tw_ceiling']:.1f} °C → caught <b class="bad">0/2</b></p></div>
  <div class="card anim a-right" style="--d:.4s;padding:18px 20px"><h3 style="font-size:26px">🧮 Residual = actual − expected</h3>{tw_res}
    <p style="font-size:23px;margin-top:8px">Spike = {F['ev04_z']:.0f}σ, shift stays above the band → caught <b class="good">{twr['caught']}/2</b>, <b class="good">{twr['false_alarms']}</b> false alarms</p></div>
</div>""",
          f"Expected temperature = a fit on 2024 using drive level, a yearly sun-angle wave and ageing. Residual sd {rsd:.3f} °C. The EV04 spike is {F['ev04_z']:.0f} sigma in residual terms; the raw series hides it inside its own yearly swing."),

        # 13 ─ CUSUM
        S(f"""
<div class="kicker anim">Detector 5 · CUSUM on the same residual</div>
<h2 class="anim" style="--d:.1s">More sensitive is <span class="hl">not free</span></h2>
<div class="grid3" style="margin-top:24px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="stat good">{twc['caught']}/2</div><div class="stat-label">events caught (same as the residual rule)</div></div>
  <div class="card anim a-pop" style="--d:.55s;text-align:center;border-color:#E5484D"><div class="stat bad">{twc['false_alarms']}</div><div class="stat-label">false alarms: {', '.join(d.strftime('%d %b') for d in F['cusum_fa_dates'])}</div></div>
  <div class="card anim a-pop" style="--d:.8s;text-align:center"><div class="stat hl">{twc['precision']:.2f}</div><div class="stat-label">precision (residual rule: {twr['precision']:.2f})</div></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:34px;text-align:center">CUSUM adds up small pushes, so it also adds up small <i>innocent</i> pushes.<br>The scorer is how you find out which one wins <b>on your data</b>.</p>""",
          "CUSUM with k = 0.5 sigma and decision line h = 5 sigma. Both detectors catch EV05 on its first day here, because the residual model already removed most of the noise. CUSUM earns its keep when a shift is small compared with the noise; this one isn't. No winner by reputation: the scorer decides."),

        # 14 ─ battery
        S(f"""
<div class="kicker anim">Detector 6 · the battery</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The fault no value-alarm can see 🪫</h2>
<div class="grid2" style="margin-top:6px;gap:26px">
  <div class="card anim a-left" style="--d:.2s;padding:18px 20px"><h3 style="font-size:26px">Capacity vs a fixed 95 Ah floor</h3>{bat_chart}
    <p style="font-size:23px;margin-top:8px">Lowest day {F['cap_min']:.1f} Ah: never below 95 → caught <b class="bad">0/1</b></p></div>
  <div class="card anim a-right" style="--d:.4s;padding:18px 20px"><h3 style="font-size:26px">🌶️ 90-day fade rate (the slope)</h3>{rate_chart}
    <p style="font-size:23px;margin-top:8px">Rate alarm catches EV06 <b class="good">{F['slope_delay']} days</b> after the knee, <b class="good">0</b> false alarms</p></div>
</div>""",
          f"EV06 is a change in SLOPE: fade goes from about −2.2 to about −3.7 Ah a year from 1 April 2025. No single day is unusual, so every value detector scores zero. The slope detector (today's pepper task) catches it {F['slope_delay']} days late. Forecasting the date it will cross a limit is Week 6."),

        # 15 ─ scoreboard
        S(f"""{table_css}
<div class="kicker anim">The report card</div>
<h2 class="anim" style="--d:.1s;font-size:52px;margin-bottom:12px">One scorer. Seven detectors.</h2>
<table class="sb"><tr class="anim" style="--d:.1s"><th></th><th>Detector</th><th>Caught</th><th>False alarms</th><th>Recall</th><th>Precision</th></tr>{rows}</table>""",
          "Read the table bottom-up for the lessons: a value rule can't see a slope; raw values hide what residuals show; conditioning on eclipse beats widening the band; and the fixed SoC floor is pure noise."),

        # 16 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">Count the cost 💸</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Managers don't decide on “precision 0.06”. They decide on hours.</p>""",
          "Section break.", cls="center"),

        # 17 ─ shift hours
        S(f"""
<div class="kicker anim">False alarms → engineer hours</div>
<h2 class="anim" style="--d:.1s">The all-hours chart costs <span class="hl">{F['hours_year']:.0f} hours a year</span></h2>
<div class="flow" style="margin-top:40px;justify-content:center">
  <div class="box anim a-pop" style="--d:.3s;min-width:250px"><div class="stat" style="font-size:72px">{cca['false_alarms']}</div><p class="small">false alarms per eclipse season</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box anim a-pop" style="--d:.7s;min-width:220px"><div class="stat" style="font-size:72px">× 2</div><p class="small">eclipse seasons a year</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box anim a-pop" style="--d:1.1s;min-width:250px"><div class="stat" style="font-size:72px">× 20</div><p class="small">minutes to check each one (assumption)</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:270px"><div class="stat hl" style="font-size:72px">{F['hours_year']:.0f} h</div><p class="small">≈ {F['hours_year'] / 8:.0f} full 8-hour shifts</p></div>
</div>
<p class="sub anim" style="--d:1.9s;margin-top:44px;text-align:center">“Add one condition and get {F['hours_year'] / 8:.0f} shifts back” is a decision a manager can make. 🧑🏾‍💼</p>""",
          f"Quiz question 5. {cca['false_alarms']} false alarms per season × 2 seasons = {F['pages_year']} pages a year. At 20 minutes each (change it to your unit's real number) that's {F['hours_year']:.1f} hours. The statistical choice becomes an operations decision."),

        # 18 ─ RF
        S(f"""
<div class="kicker anim">The RF file · August, hourly</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Unusual is <span class="bad">not</span> the same as anomaly 🌧️</h2>
<div class="card anim" style="--d:.2s;padding:18px 20px">{rf_chart}</div>
<div class="row anim" style="--d:2.6s;margin-top:18px;gap:14px;align-items:center">
  <span class="pill">{F['rf_n_flags']} flagged hours</span><span class="pill bad">🔴 {F['rf_real']} real outages</span>
  <span class="pill gold">🟡 {F['rf_n_flags'] - F['rf_real']} rain, link held</span><span class="pill teal">precision {F['rf_real'] / F['rf_n_flags']:.2f}</span>
  <span class="small" style="margin-left:auto">dashed line = naive 3σ ({F['rf_line']:.1f} dB)</span>
</div>""",
          f"Quiz question 6 (answer: False). All {F['rf_n_flags']} flagged hours were during rain ({F['rf_rain']} rainy hours in the month). Rain fade is physics, not a fault. The useful alarm is on the service (margin below 0 dB), and a rain gauge tells the engineer the cause. "
          "Note: the original code book says this naive rule flags 'roughly all 56 rainy hours, 79% false alarms'. The data says 18 flags, 6 false (33%)."),

        # 19 ─ recall vs precision first
        S("""
<div class="kicker anim">Which number leads?</div>
<h2 class="anim" style="--d:.1s">It depends on what a miss costs</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s;border-color:#16A394"><div class="icon">🛰️</div><h3>Recall first</h3>
    <p class="muted">Battery, power, propulsion. A miss can cost the satellite.<br><b style="color:#fff">NigComSat-1 was lost in 2008 after a solar-array failure.</b> Accept some extra pages.</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#F5B83D"><div class="icon">📟</div><h3>Precision first</h3>
    <p class="muted">Rain fade, NOC dashboards, anything that pages people all night.<br>Too many false alarms and engineers <b style="color:#fff">stop reading the pager</b>. That's alarm fatigue.</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:30px;text-align:center">Write down which one leads <b class="hl">before</b> you score, and say why. ✍🏾</p>""",
          "The NigComSat-1 fact is in the toolkit fact sheet. Recall-first doesn't mean 'ignore precision': it means you accept more pages to avoid the miss you can't afford."),

        # 20 ─ quiz
        S("""
<div class="kicker anim">Quiz 2 · Week 3: anomaly detection</div>
<h2 class="anim" style="--d:.1s">30 questions. 20 minutes. Just you. 📝</h2>
<div class="grid4" style="margin-top:30px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="icon">📵</div><h3>Phones down</h3><p class="small">notebooks closed, no AI</p></div>
  <div class="card anim a-pop" style="--d:.5s;text-align:center"><div class="icon">✏️</div><h3>One letter</h3><p class="small">circle A, B, C or D (or True/False)</p></div>
  <div class="card anim a-pop" style="--d:.7s;text-align:center"><div class="icon">🔀</div><h3>No “always B”</h3><p class="small">answers are spread across A–D</p></div>
  <div class="card anim a-pop" style="--d:.9s;text-align:center"><div class="icon">✅</div><h3>Mark together</h3><p class="small">10 minutes, swap and tick</p></div>
</div>
<p class="anim" style="--d:1.2s;margin-top:34px;text-align:center">Covers alarms (W3D1) · control charts + residuals (W3D2) · drift + CUSUM (W3D3) · scoring (today).</p>""",
          "Hand out 2-exercise/quiz/W4D1-quiz-2.pdf, or import the Google Forms CSV. Answer key: 4-instructor-only/W4D1-quiz-2-answer-key.pdf. In the original MCQ file most answers were option B; this version spreads them out."),

        # 21 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 50 minutes</div>
  <h2 class="anim" style="--d:.1s">Be the referee 🧑🏾‍⚖️</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open <b class="hl">W4D1-exercise</b>, save a copy, run STEP 0</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">A</span><p>Rules first: accuracy trap, Musa's numbers</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">B</span><p>Score 6 detectors with one scorer</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">C</span><p>Turn false alarms into hours; the rain lesson</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🎯</div>
  <h3 style="margin-top:16px">14 checks to pass</h3>
  <p class="muted">🌶️ Pepper task: build the slope alarm that finally catches EV06</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Common snags: comparing a number with ___ before filling it (the friendly assert catches that), and forgetting quotes around the source_file name."),

        # 22 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🙅🏾</span><p><b>Accuracy lies</b> when events are rare. Never report it for a detector.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🎯</span><p><b>Recall</b> = did we miss anything? <b>Precision</b> = when it pages, is it real? Rules written <b class="hl">first</b>.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">💸</span><p><b>False alarms cost hours.</b> Say it in hours and managers can decide.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:34px;font-size:30px">Next time 👉 <b class="hl">Meet scikit-learn</b>: faults hiding between two normal-looking sensors. 🔍</p>""",
          "Recap, then the quiz if you haven't run it yet. Tease W4D2: the multivariate faults no single-sensor alarm can see."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    F = facts()
    soc, cca, ccs = F["soc"], F["cc_all"], F["cc_sun"]

    def p(v):
        return "—" if v != v else f"{v:.2f}"
    board = [("SoC floor < 82%", soc), ("Control chart, all hours", cca), ("Control chart, sunlit only", ccs),
             ("Raw 3σ, amplifier temp", F["tw_raw"]), ("Residual 3σ, amplifier", F["tw_resid"]),
             ("CUSUM on residual", F["tw_cusum"]), ("Fixed floor 95 Ah, battery", F["bat"])]
    # daily minimum SoC across the file (120 points) for a native chart
    daily_min = F["bus"]["battery_soc_pct"].resample("D").min()
    labels = [d.strftime("%d %b") if d.day in (1, 15) else "" for d in daily_min.index]
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🎯", "kicker": "Week 4 · Day 1", "title": "Scoring a Detector\n+ Quiz 2",
             "sub": "The answer key comes out, and every alarm from last week gets a report card",
             "notes": "Today we stop arguing about detectors and score them with the same rules."},
            {"type": "flow", "title": "Today's mission", "steps": [
                ["🔑", "Open the key", "6 real events revealed"], ["🎯", "Score every alarm", "recall, precision, false alarms"],
                ["💸", "Count the cost", "false alarms → hours"], ["📝", "Quiz 2", "all of Week 3"]],
             "footer": "10 min hook · 25 min slides · 50 min hands-on · 25 min quiz · 10 min wrap-up", "notes": "Four moves."},
            {"type": "compare", "title": "Which mai-guard do you hire?",
             "left": ["📢", "Musa shouts at every goat", "Caught 9 of 10 thieves, but shouted 200 times"],
             "right": ["😴", "Ade sleeps all night", "Never shouts. “97% accurate”. Caught zero thieves"],
             "notes": "Vote, then reveal: neither."},
            {"type": "statement", "title": "Why accuracy lies", "icon": "🙅🏾",
             "big": f"A detector that never fires scores {F['acc_never'] * 100:.2f}%",
             "sub": f"6 real events in {F['n_readings']:,} readings. Saying “no problem” every time is almost always “right”.",
             "notes": "Quiz question 1."},
            {"type": "section", "kicker": "Part 1", "title": "The answer key", "sub": "Six real events, three files", "notes": "Section break."},
            {"type": "table", "title": "The six events", "header": ["Event", "File", "Type", "When", "Severity"],
             "rows": [[r.event_id, r.source_file.replace(".csv", ""), r.type.replace("_", " "),
                       r.start.strftime("%d %b %Y") + ("" if r.end == r.start else " → " + r.end.strftime("%d %b %Y")), r.severity]
                      for r in F["labels"].itertuples()],
             "colW": [1.2, 3.6, 1.8, 3.8, 1.73], "caption": "Our loader repairs the stray comma that crashes the original file",
             "notes": "Short events are spikes; EV05 and EV06 last months."},
            {"type": "cards4", "title": "Four scoring rules, written first", "cards": [
                ["🎯", "One flag = caught", "anywhere inside start→end, ±1 step"], ["🔂", "Many flags = one catch", "EV02 twice is still one"],
                ["📟", "Outside = false alarm", "a page to the duty engineer"], ["📏", "Long event = one event", "233 days of EV05 is one catch"]],
             "notes": "Quiz question 4 is rule 4."},
            {"type": "compare", "title": "Recall and precision",
             "left": ["🕸️", "Recall", "Of the real events, how many did we catch? caught ÷ real events. Musa: 9 ÷ 10 = 0.90"],
             "right": ["📟", "Precision", "When it shouts, how often is it real? caught ÷ all alarms. Musa: 9 ÷ 200 = 0.045"],
             "notes": "Quiz questions 2 and 3."},
            {"type": "section", "kicker": "Part 2", "title": "Report cards", "sub": "Same scorer, every detector", "notes": "Section break."},
            {"type": "chart", "title": f"SoC floor < 82%: {soc['false_alarms']} alarms, 0 real", "labels": labels,
             "series": [{"name": "lowest state of charge each day (%)", "values": daily_min.round(1).tolist(), "color": "0A5DB4"},
                        {"name": "alarm floor 82%", "values": [82.0] * len(daily_min), "color": "E5484D"}],
             "ymin": 74, "ymax": 101, "fmt": "0",
             "caption": "Every alarm is a deep eclipse night: the battery doing its job. The real faults were in array current.",
             "notes": "Correct alarms, useless alarms."},
            {"type": "compare", "title": "Control chart: one condition changes everything",
             "left": ["📊", f"All hours: {cca['false_alarms']} false alarms", f"Caught {cca['caught']}/3, but every eclipse hour fires. Precision {cca['precision']:.2f}"],
             "right": ["🌞", "Sunlit hours only: 0 false alarms", f"Caught {ccs['caught']}/3. Precision {ccs['precision']:.2f}. Condition on the known cause"],
             "notes": "Don't widen the band; condition on eclipse."},
            {"type": "compare", "title": "Amplifier: raw values hide it, the residual shouts",
             "left": ["🌡️", "Raw 3σ: caught 0 of 2", f"Highest day {F['tw_max']:.1f} °C never reaches the {F['tw_ceiling']:.1f} °C ceiling"],
             "right": ["🧮", f"Residual 3σ: caught {F['tw_resid']['caught']} of 2", f"Actual − expected. The spike is {F['ev04_z']:.0f}σ; {F['tw_resid']['false_alarms']} false alarms"],
             "notes": "Expected = drive + season + ageing, fitted on 2024."},
            {"type": "table", "title": "The report card", "header": ["Detector", "Caught", "False alarms", "Recall", "Precision"],
             "rows": [[n, f"{r['caught']}/{r['events']}", r["false_alarms"], p(r["recall"]), p(r["precision"])] for n, r in board],
             "colW": [4.6, 1.6, 2.1, 1.8, 2.03], "caption": f"CUSUM: same catches, {F['tw_cusum']['false_alarms']} extra false alarms. The battery drift beats every value rule.",
             "notes": "Read bottom-up for the lessons."},
            {"type": "section", "kicker": "Part 3", "title": "Count the cost", "sub": "Managers decide in hours", "notes": "Section break."},
            {"type": "flow", "title": f"False alarms → {F['hours_year']:.0f} engineer hours a year", "steps": [
                ["📟", f"{cca['false_alarms']} per season", "all-hours control chart"], ["🌘", "× 2 seasons", "eclipse twice a year"],
                ["⏱️", "× 20 minutes", "to check each (assumption)"], ["💸", f"≈ {F['hours_year']:.0f} hours", f"about {F['hours_year'] / 8:.0f} full shifts"]],
             "footer": "“Add one condition, get shifts back” is a decision a manager can make", "notes": "Quiz question 5."},
            {"type": "bar", "title": "Rain fade: unusual is not the same as anomaly",
             "labels": ["rainy hours", "below naive 3σ", "real outages", "link held"],
             "values": [F["rf_rain"], F["rf_n_flags"], F["rf_real"], F["rf_n_flags"] - F["rf_real"]], "highlight": [2], "fmt": "0",
             "caption": "Alarm on the service (margin < 0 dB); use a rain gauge to explain the cause",
             "notes": "Quiz question 6: False."},
            {"type": "compare", "title": "Which number leads? It depends on the cost of a miss",
             "left": ["🛰️", "Recall first", "Battery, power, propulsion. NigComSat-1 was lost in 2008 after a solar-array failure"],
             "right": ["📟", "Precision first", "Rain fade, NOC dashboards. Too many pages and people stop reading them"],
             "notes": "Decide before you score."},
            {"type": "steps", "title": "Quiz 2: 30 questions, 20 minutes", "icon": "📝", "steps": [
                "Phones down, notebooks closed, no AI", "Circle one letter per question", "Answers are spread across A–D: no “always B”",
                "Swap papers and mark together"], "notes": "Use the PDF or the Google Forms CSV."},
            {"type": "steps", "title": "Your turn: 50 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W4D1-exercise, save a copy, run STEP 0", "Part A: rules first, the accuracy trap",
                "Part B: score 6 detectors with one scorer", "Part C: false alarms → hours, the rain lesson"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🙅🏾", "Accuracy lies when events are rare"], ["🎯", "Recall = did we miss anything? Precision = is the page real?"],
                ["💸", "False alarms cost hours: say it in hours"]],
             "next": "Next: Meet scikit-learn + Isolation Forest", "notes": "Tease W4D2."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
def _near(x, want, tol):
    return abs(float(x) - want) <= tol

def _res(x, caught, fa):
    return isinstance(x, dict) and x.get("caught") == caught and x.get("false_alarms") == fa

def _c_a1(x):
    v = float(x)
    v = v / 100 if v > 1 else v
    return _near(v, 1 - 6 / 4706, 0.0002), \
        "99.87%! A detector that NEVER fires looks almost perfect. That's why we never report accuracy for rare events.", \
        "1 minus (events ÷ readings): 1 - n_events / n_readings"

def _c_a2(x):
    ok = str(x[0]).strip().lower() == "yes" and int(x[1]) == 1
    return ok, "Rules agreed: one flag inside = caught, and many flags inside one event = ONE catch.", \
        "Rule 1: one flag anywhere inside counts. Rule 2: two flags inside one event are still one catch."

def _c_a3(x):
    return _near(x[0], 0.9, 0.001) and _near(x[1], 0.045, 0.001), \
        "Recall 0.90, precision 0.045. Musa misses little but wakes the whole estate for nothing. 📢🐐", \
        "recall = caught ÷ real thieves (9 ÷ 10). precision = caught ÷ all shouts (9 ÷ 200)."

def _c_b1(x):
    return _res(x, 0, 18), "18 alarms, 0 real: every one was a normal eclipse night. Correct alarms, useless alarms.", \
        "Use SOC_FLOOR = 82 and score with source_file \"bus_power_telemetry_hourly.csv\"."

def _c_b2(x):
    return _res(x, 3, 46), "Caught all 3 dropouts… plus 46 false alarms, all at 21:00 UTC = eclipse time. 🌘", \
        "K is the number of standard deviations in the band: 3."

def _c_b3(x):
    return _res(x, 3, 0), "3 of 3 caught, ZERO false alarms. One condition on the known cause did it. 🌞", \
        "Sunlit hours have eclipse_flag == 0."

def _c_b4(x):
    return _res(x, 2, 0), "Both amplifier events caught, no false alarms. The residual saw what the raw series hid. 🧮", \
        "Use the same 3-sigma rule on the residual: resid.abs() > 3 * resid_sd"

def _c_b5(x):
    return _res(x, 2, 2), "Same 2 catches as the residual rule, plus 2 false alarms. More sensitive is not free.", \
        "Use the standard decision line H = 5."

def _c_b6(x):
    return str(x).strip().upper() == "EV06", "EV06, the battery's fade speeding up. A change in SLOPE, not in value. Pepper task below! 🌶️", \
        "Look at the report card: which event has nobody's name next to it? It's in the battery file."

def _c_b7(x):
    return int(x) == 3, "Control chart, sunlit only: recall 1.00, precision 1.00. That goes on the console. ✅", \
        "Pick the row with recall 1 and zero false alarms."

def _c_c1(x):
    return _near(x, 46 * 2 * 20 / 60, 0.2), \
        f"About {46 * 2 * 20 / 60:.0f} hours a year, roughly 4 full shifts. Now a manager can decide. 🧑🏾‍💼", \
        "false_alarms_per_season × seasons_per_year × MINUTES_PER_FALSE_ALARM ÷ 60"

def _c_c2(x):
    return _near(x, 12 / 18, 0.002), "0.67: a third of the 'outage' pages were rain the link survived. 🌧️", \
        "precision = real outages among the flags ÷ all flags = n_real / n_flags"

def _c_c3(x):
    return x is False or str(x).strip().lower() == "false", \
        "False! Rain fade is physics, not a fault. Alarm on the SERVICE (margin < 0 dB) and use a rain gauge to explain it.", \
        "Is 'statistically unusual' the same as 'something is wrong'? Think DStv in a storm."

def _c_bonus(x):
    return _res(x, 1, 0), "Caught EV06 with zero false alarms: you just built a slope alarm. Week 6 forecasts WHEN it hits the limit. 🌶️🏆", \
        "Pick a line between the normal fade (about -2.6 at worst) and the fast fade (below -3.5), e.g. -3."

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4,
          "B5": _c_b5, "B6": _c_b6, "B7": _c_b7, "C1": _c_c1, "C2": _c_c2, "C3": _c_c3, "BONUS": _c_bonus}
HINTS = {"A2": "Two answers: \"yes\"/\"no\" and a number.", "A3": "Two numbers: recall and precision."}
'''


SCORER = '''def score_events(flags, labels, source_file, tol="1h"):
    """Event-level scoring, using the 4 rules. flags: a True/False Series with a time index."""
    events = labels[labels["source_file"] == source_file]
    tol = pd.Timedelta(tol)
    caught, inside_any = 0, pd.Series(False, index=flags.index)
    for _, ev in events.iterrows():
        window = (flags.index >= ev["start"] - tol) & (flags.index <= ev["end"] + tol)
        if flags[window].any():          # rules 1 + 2 + 4: one flag or many = ONE catch
            caught += 1
        inside_any |= window
    false_alarms = int((flags & ~inside_any).sum())   # rule 3: every flag outside every event
    alarms = caught + false_alarms
    return {"events": len(events), "caught": caught, "false_alarms": false_alarms,
            "recall": round(caught / len(events), 3),
            "precision": round(caught / alarms, 3) if alarms else float("nan")}

print("✅ score_events() is ready")'''


def notebook_cells(setup_code):
    return [
        ("md", """# 🎯 Week 4 · Day 1: Scoring a Detector

**Today:** the answer key comes out. You score every alarm from Week 3 with **one** scorer and **one** set of rules, and then turn false alarms into engineer hours.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**

**Rule book:** keep `W4D1-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up
Run it once every time you open the notebook (and after every restart). Wait for `✅ Ready!`."""),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Rules before numbers (15 min) 🧑🏾‍⚖️

### A1 ✍️ The accuracy trap
Last week's three files hold **2,880** bus-power hours, **730** amplifier days and **1,096** battery days. Hidden inside them are **6** real events.
A lazy detector says *"no problem"* every single time. What fraction of readings does it get "right"? (That fraction is called **accuracy**.)"""),
        ("task", 'n_readings = 2880 + 730 + 1096\nn_events = 6\n\naccuracy_never_fires = ___\n\nprint("accuracy of doing nothing:", accuracy_never_fires)\ncheck("A1", accuracy_never_fires)',
         'n_readings = 2880 + 730 + 1096\nn_events = 6\n\naccuracy_never_fires = 1 - n_events / n_readings\n\nprint("accuracy of doing nothing:", accuracy_never_fires)\ncheck("A1", accuracy_never_fires)'),
        ("md", """### 🔑 The answer key
▶️ For three days this file was hidden. Here it is. `load_labels()` (from STEP 0) also repairs a stray comma that makes the original file crash."""),
        ("code", 'labels = load_labels()\nlabels["days"] = (labels["end"] - labels["start"]).dt.days + 1\ndisplay(labels[["event_id", "source_file", "column", "start", "end", "days", "type", "severity"]])'),
        ("md", """### A2 ✍️ Write the rules BEFORE you score
Our 4 rules:
1. A flag anywhere inside an event's start→end (±1 time step) **catches** it.
2. Many flags inside one event still count as **one** catch.
3. A flag outside every event is a **false alarm** (one page to the duty engineer).
4. A long event is still **one** event.

Now answer: **(a)** EV05 lasts 233 days. If a detector flags just ONE of those days, is EV05 caught? (`"yes"` or `"no"`) **(b)** A detector flags EV02 on both of its hours. How many catches is that?"""),
        ("task", 'one_day_counts = ___        # "yes" or "no"\ncatches_for_two_flags = ___\n\ncheck("A2", (one_day_counts, catches_for_two_flags))',
         'one_day_counts = "yes"        # "yes" or "no"\ncatches_for_two_flags = 1\n\ncheck("A2", (one_day_counts, catches_for_two_flags))'),
        ("md", """### A3 ✍️ Musa the mai-guard 💂🏾
This year **10** thieves came to the estate. Musa shouted "Thief!" **200** times. **9** of the thieves were caught by one of those shouts.
- **Recall** = of the real thieves, how many were caught?
- **Precision** = of all the shouts, how many were a real thief?"""),
        ("task", 'musa_recall = ___\nmusa_precision = ___\n\ncheck("A3", (musa_recall, musa_precision))',
         'musa_recall = 9 / 10\nmusa_precision = 9 / 200\n\ncheck("A3", (musa_recall, musa_precision))'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Report cards for every detector (35 min) 🎯

▶️ First, the **scorer**. Read it: each rule from A2 is one line. Every detector today goes through this exact function."""),
        ("code", SCORER),
        ("md", "▶️ Load last week's three files (the Week 4 versions, which contain the injected faults)."),
        ("code", 'bus = pd.read_csv(data_path("bus_power_telemetry_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n'
                 'tw  = pd.read_csv(data_path("twta_thermal_daily"), parse_dates=["date"], index_col="date").asfreq("D")\n'
                 'bat = pd.read_csv(data_path("battery_health_daily"), parse_dates=["date"], index_col="date").asfreq("D")\n'
                 'print("bus:", len(bus), "hours · twta:", len(tw), "days · battery:", len(bat), "days")'),
        ("md", """### B1 ✍️ Detector 1: the alarm software's fixed floor
The ground software pages someone when state of charge drops below **82%**. Fill in the floor and score it against the bus-power events."""),
        ("task", 'SOC_FLOOR = ___\n\nassert SOC_FLOOR is not None, "✍️ Fill in SOC_FLOOR first, then run this cell again."\nsoc_flags = bus["battery_soc_pct"] < SOC_FLOOR\nsoc_result = score_events(soc_flags, labels, "bus_power_telemetry_hourly.csv")\nprint(soc_result)\ncheck("B1", soc_result)',
         'SOC_FLOOR = 82\n\nassert SOC_FLOOR is not None, "✍️ Fill in SOC_FLOOR first, then run this cell again."\nsoc_flags = bus["battery_soc_pct"] < SOC_FLOOR\nsoc_result = score_events(soc_flags, labels, "bus_power_telemetry_hourly.csv")\nprint(soc_result)\ncheck("B1", soc_result)'),
        ("md", """### B2 ✍️ Detector 2: a control chart on solar-array current
The normal band is the sunlit mean ± **K** standard deviations. Use the classic **K**."""),
        ("task", 'current = bus["solar_array_current_a"]\nsunlit = current[bus["eclipse_flag"] == 0]\nm, s = sunlit.mean(), sunlit.std()\n\nK = ___\n\nassert K is not None, "✍️ Fill in K first."\ncc_all_flags = (current - m).abs() > K * s\ncc_all = score_events(cc_all_flags, labels, "bus_power_telemetry_hourly.csv")\nprint(f"band: {m - K*s:.2f} to {m + K*s:.2f} A ->", cc_all)\ncheck("B2", cc_all)',
         'current = bus["solar_array_current_a"]\nsunlit = current[bus["eclipse_flag"] == 0]\nm, s = sunlit.mean(), sunlit.std()\n\nK = 3\n\nassert K is not None, "✍️ Fill in K first."\ncc_all_flags = (current - m).abs() > K * s\ncc_all = score_events(cc_all_flags, labels, "bus_power_telemetry_hourly.csv")\nprint(f"band: {m - K*s:.2f} to {m + K*s:.2f} A ->", cc_all)\ncheck("B2", cc_all)'),
        ("md", "▶️ Where are those false alarms? Look at the **hour of day** of every flag."),
        ("code", 'cc_all_flags[cc_all_flags].index.hour.value_counts()'),
        ("md", """### B3 ✍️ Fix it with ONE condition
21:00 UTC is eclipse time: the array *should* drop to zero then. Only judge **sunlit** hours. What value does `eclipse_flag` have in sunlight?"""),
        ("task", 'cc_sun_flags = cc_all_flags & (bus["eclipse_flag"] == ___)\n\ncc_sun = score_events(cc_sun_flags, labels, "bus_power_telemetry_hourly.csv")\nprint(cc_sun)\ncheck("B3", cc_sun)',
         'cc_sun_flags = cc_all_flags & (bus["eclipse_flag"] == 0)\n\ncc_sun = score_events(cc_sun_flags, labels, "bus_power_telemetry_hourly.csv")\nprint(cc_sun)\ncheck("B3", cc_sun)'),
        ("md", """### 🌡️ The amplifier (TWTA)
▶️ First the naive way: 3σ on the raw temperature. Then the smart way: build an **expected** temperature from drive level, the yearly sun-angle wave and ageing (fitted on 2024 only), and look at the **residual** = actual − expected."""),
        ("code", 'temp = tw["twta_temp_c"]\nraw_flags = (temp - temp.mean()).abs() > 3 * temp.std()\ntw_raw = score_events(raw_flags, labels, "twta_thermal_daily.csv", tol="1D")\nprint("raw 3-sigma:", tw_raw)\n\n'
                 'doy = tw.index.day_of_year\nX = pd.DataFrame({"drive": tw["rf_drive_pct"], "sin": np.sin(2 * np.pi * doy / 365.25),\n'
                 '                  "cos": np.cos(2 * np.pi * doy / 365.25), "age": np.arange(len(tw)), "const": 1.0}, index=tw.index)\n'
                 'fit = tw.index < "2025-01-01"\ncoef, *_ = np.linalg.lstsq(X[fit].values, temp[fit].values, rcond=None)\n'
                 'resid = temp - X.values @ coef\nresid_sd = resid[fit].std()\nprint(f"residual spread on the clean year: {resid_sd:.3f} C")\n\n'
                 'resid.plot(title="Amplifier residual: actual minus expected", lw=1)\nplt.axhline(3 * resid_sd, color="#C77700", ls="--"); plt.axhline(-3 * resid_sd, color="#C77700", ls="--")\nplt.show()'),
        ("md", """### B4 ✍️ Detector 3: 3σ on the residual
Same 3σ idea, but on the residual. How many residual-standard-deviations wide is the band?"""),
        ("task", 'N_SIGMA = ___\n\nassert N_SIGMA is not None, "✍️ Fill in N_SIGMA first."\nresid_flags = resid.abs() > N_SIGMA * resid_sd\ntw_resid = score_events(resid_flags, labels, "twta_thermal_daily.csv", tol="1D")\nprint(tw_resid)\ncheck("B4", tw_resid)',
         'N_SIGMA = 3\n\nassert N_SIGMA is not None, "✍️ Fill in N_SIGMA first."\nresid_flags = resid.abs() > N_SIGMA * resid_sd\ntw_resid = score_events(resid_flags, labels, "twta_thermal_daily.csv", tol="1D")\nprint(tw_resid)\ncheck("B4", tw_resid)'),
        ("md", """### B5 ✍️ Detector 4: CUSUM on the same residual
CUSUM keeps a running total of small pushes above normal (allowance `k = 0.5`) and alarms when the total passes a decision line **H**. Use the standard `H = 5`."""),
        ("task", 'def cusum(z, k=0.5, h=5.0):\n    s, out = 0.0, []\n    for v in z:\n        s = max(0.0, s + v - k)       # add today\'s push, never below zero\n        if s > h:\n            out.append(True)\n            s = 0.0                     # alarm, then start counting again\n        else:\n            out.append(False)\n    return pd.Series(out, index=z.index)\n\n'
         'H = ___\n\nassert H is not None, "✍️ Fill in H first."\ncusum_flags = cusum(resid / resid_sd, k=0.5, h=H)\ntw_cusum = score_events(cusum_flags, labels, "twta_thermal_daily.csv", tol="1D")\nprint(tw_cusum)\ncheck("B5", tw_cusum)',
         'def cusum(z, k=0.5, h=5.0):\n    s, out = 0.0, []\n    for v in z:\n        s = max(0.0, s + v - k)       # add today\'s push, never below zero\n        if s > h:\n            out.append(True)\n            s = 0.0                     # alarm, then start counting again\n        else:\n            out.append(False)\n    return pd.Series(out, index=z.index)\n\n'
         'H = 5\n\nassert H is not None, "✍️ Fill in H first."\ncusum_flags = cusum(resid / resid_sd, k=0.5, h=H)\ntw_cusum = score_events(cusum_flags, labels, "twta_thermal_daily.csv", tol="1D")\nprint(tw_cusum)\ncheck("B5", tw_cusum)'),
        ("md", "▶️ Detector 5: the battery's fixed floor at **95 Ah**. Then the full report card."),
        ("code", 'bat_flags = bat["est_capacity_ah"] < 95\nbat_result = score_events(bat_flags, labels, "battery_health_daily.csv", tol="1D")\nprint("lowest capacity:", bat["est_capacity_ah"].min().round(2), "Ah ->", bat_result)\n\n'
                 'assert "tw_cusum" in globals(), "✍️ Finish B1–B5 first, then run this cell."\n'
                 'card = pd.DataFrame([\n    {"detector": "1. SoC floor < 82%", **soc_result},\n    {"detector": "2. Control chart, all hours", **cc_all},\n'
                 '    {"detector": "3. Control chart, sunlit only", **cc_sun},\n    {"detector": "4. Raw 3-sigma, amplifier", **tw_raw},\n'
                 '    {"detector": "5. Residual 3-sigma, amplifier", **tw_resid},\n    {"detector": "6. CUSUM on residual", **tw_cusum},\n'
                 '    {"detector": "7. Fixed floor 95 Ah, battery", **bat_result},\n]).set_index("detector")\ncard'),
        ("md", """### B6 ✍️ Which event did EVERY detector miss?
Type its event id (e.g. `"EV01"`)."""),
        ("task", 'missed_by_all = ___\n\ncheck("B6", missed_by_all)', 'missed_by_all = "EV06"\n\ncheck("B6", missed_by_all)'),
        ("md", """### B7 ✍️ Your pick for the bus-power console
Which detector number (1, 2 or 3) would you put on the console that watches solar-array current?"""),
        ("task", 'my_console_detector = ___\n\ncheck("B7", my_console_detector)', 'my_console_detector = 3\n\ncheck("B7", my_console_detector)'),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Count the cost (15 min) 💸

### C1 ✍️ False alarms → engineer hours
The all-hours control chart fires on every eclipse hour. The file holds **one** eclipse season; there are **two** a year.
Assume each false alarm takes **20 minutes** to check and close (change it to your unit's real number later). How many hours a year is that?"""),
        ("task", 'MINUTES_PER_FALSE_ALARM = 20\nfalse_alarms_per_season = cc_all["false_alarms"]\nseasons_per_year = 2\n\nhours_per_year = ___\n\nprint(f"{hours_per_year} hours a year")\ncheck("C1", hours_per_year)',
         'MINUTES_PER_FALSE_ALARM = 20\nfalse_alarms_per_season = cc_all["false_alarms"]\nseasons_per_year = 2\n\nhours_per_year = false_alarms_per_season * seasons_per_year * MINUTES_PER_FALSE_ALARM / 60\n\nprint(f"{hours_per_year} hours a year")\ncheck("C1", hours_per_year)'),
        ("md", """### C2 ✍️ The rain lesson 🌧️
▶️ The cell below runs a naive 3σ rule on carrier-to-noise in August and compares the flags with the **real outages** (link margin below 0 dB). Then compute its precision."""),
        ("code", 'rf = pd.read_csv(data_path("rf_link_quality_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n'
                 'cn = rf["cn_ratio_db"]\nrf_flags = cn < cn.mean() - 3 * cn.std()\nreal_outage = rf["link_margin_db"] < 0\n'
                 'n_flags = int(rf_flags.sum())\nn_real = int((rf_flags & real_outage).sum())\n'
                 'print("flagged hours:", n_flags, "· real outages among them:", n_real,\n      "· flagged hours with rain:", int((rf_flags & (rf["rain_rate_mmhr"] > 0)).sum()))'),
        ("task", 'rf_precision = ___\n\ncheck("C2", rf_precision)', 'rf_precision = n_real / n_flags\n\ncheck("C2", rf_precision)'),
        ("md", """### C3 ✍️ True or False?
*"In the RF file, every rain-fade excursion should be raised as an anomaly because it is statistically unusual."* Answer `True` or `False` (no quotes)."""),
        ("task", 'rain_fade_is_an_anomaly = ___\n\ncheck("C3", rain_fade_is_an_anomaly)', 'rain_fade_is_an_anomaly = False\n\ncheck("C3", rain_fade_is_an_anomaly)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: catch EV06
Every value-alarm missed the battery event, because nothing about any single day is unusual: the **fade speeds up**.
▶️ The cell computes the **fade rate** (Ah per year) over the last 90 days, every day. ✍️ Choose an alarm line (a negative number) so the alarm catches EV06 with **zero** false alarms."""),
        ("task", 'cap = bat["est_capacity_ah"]\nfade_rate = cap.rolling(90).apply(lambda a: np.polyfit(np.arange(len(a)), a, 1)[0] * 365, raw=True)\nprint("fade rate before April 2025: from", fade_rate[:"2025-03-31"].min().round(2), "to", fade_rate[:"2025-03-31"].max().round(2), "Ah/year")\n\n'
         'RATE_LINE = ___\n\nassert RATE_LINE is not None, "✍️ Pick RATE_LINE first."\nslope_flags = fade_rate < RATE_LINE\nslope_result = score_events(slope_flags, labels, "battery_health_daily.csv", tol="1D")\nif slope_flags.any():\n    print("first alarm:", slope_flags[slope_flags].index[0].date())\nprint(slope_result)\ncheck("BONUS", slope_result)',
         'cap = bat["est_capacity_ah"]\nfade_rate = cap.rolling(90).apply(lambda a: np.polyfit(np.arange(len(a)), a, 1)[0] * 365, raw=True)\nprint("fade rate before April 2025: from", fade_rate[:"2025-03-31"].min().round(2), "to", fade_rate[:"2025-03-31"].max().round(2), "Ah/year")\n\n'
         'RATE_LINE = -3.0\n\nassert RATE_LINE is not None, "✍️ Pick RATE_LINE first."\nslope_flags = fade_rate < RATE_LINE\nslope_result = score_events(slope_flags, labels, "battery_health_daily.csv", tol="1D")\nif slope_flags.any():\n    print("first alarm:", slope_flags[slope_flags].index[0].date())\nprint(slope_result)\ncheck("BONUS", slope_result)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- **Accuracy lies** when events are rare: doing nothing scores 99.87%.
- **Write the scoring rules first.** One flag inside an event = caught; many flags = one catch; outside = false alarm; a long event is one event.
- **Recall** = of the real events, how many we caught. **Precision** = when it pages, how often it's real.
- **Condition on the known cause** (eclipse) instead of widening the band.
- **Residuals** reveal what raw values hide; **more sensitive** (CUSUM) can cost false alarms; a **slope** problem needs a slope detector.
- **Say it in hours:** false alarms × minutes = shifts a manager can win back.

**Next time:** *Meet scikit-learn + Isolation Forest*: faults that hide between two sensors that each look normal. 🔍

<sub>Data: synthetic teaching datasets from the original Week 4 code book (`Time-series/week-04`). Safe to use with AI tools; real NIGCOMSAT data is not.</sub>"""),
    ]


# =============================================================================
# EXTRAS: Quiz 2
# =============================================================================
def extra(d, foot):
    quiz = quizkit.write_quiz(d, foot, n=2, mcq_file="week-04-mcq.csv", seed=QUIZ_SEED, covers="Week 3",
                              topic_map="what your alarm software already does → W3D1 · statistical process control → W3D2 · "
                                        "residual-based detection → W3D2 · change points and drift → W3D3 · evaluating a detector → W4D1")
    counts = {L: sum(q["letter"] == L for q in quiz if len(q["options"]) == 4) for L in "ABCD"}
    tf = {L: sum(q["letter"] == L for q in quiz if len(q["options"]) == 2) for L in "AB"}
    print(f"Quiz 2 answer positions: multiple choice {counts}, True/False {tf}")
