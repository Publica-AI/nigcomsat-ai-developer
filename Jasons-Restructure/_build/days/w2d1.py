"""Week 2 · Day 1: Take It Apart: Trend, Season and Noise (decomposition)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL, seasonal_decompose

from common import BRAND as B, ORIGINALS
from svgcharts import GRID, AXIS_TXT, _scale, line_svg, lines_svg, spark_svg
from webdeck import logos_title_block

CODE = "W2D1"
TITLE = "Take It Apart: Trend, Season and Noise"

D3 = ORIGINALS / "week-03" / "data"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# =============================================================================
# DATA + FACTS (every number on a slide comes from here)
# =============================================================================
def _data():
    kam = pd.read_csv(D3 / "ka_band_availability_monthly.csv", parse_dates=["month"], index_col="month").asfreq("MS")
    tk = pd.read_csv(D3 / "noc_tickets_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    bus = pd.read_csv(D3 / "bus_power_telemetry_hourly.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    demo = pd.read_csv(D3 / "additive_multiplicative_demo.csv", index_col="month_index")
    bat = pd.read_csv(D3 / "battery_health_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    return kam, tk, bus, demo, bat


def _swings(x):
    x = np.asarray(x, dtype=float)
    return [float(x[i * 12:(i + 1) * 12].max() - x[i * 12:(i + 1) * 12].min()) for i in range(len(x) // 12)]


def facts():
    kam, tk, bus, demo, bat = _data()
    ka = seasonal_decompose(kam["availability_pct"], model="additive", period=12)
    ka_season = pd.Series(ka.seasonal.iloc[:12].values, index=MONTHS)
    noc7 = seasonal_decompose(tk["tickets_raised"], period=7)
    noc12 = seasonal_decompose(tk["tickets_raised"], period=12)
    weekly = noc7.seasonal.groupby(noc7.seasonal.index.day_name()).mean().reindex(DAYS)
    aug = bus["solar_array_current_a"].loc[:"2025-08-31"]
    aug_res = seasonal_decompose(aug, period=24).resid
    full_res = seasonal_decompose(bus["solar_array_current_a"], period=24).resid
    stl_res = STL(bus["solar_array_current_a"], period=24, robust=True).fit().resid
    bad = kam["availability_pct"].copy()
    bad.loc["2024-08-01"] = 94.0
    cl_bad = seasonal_decompose(bad, period=12)
    st_bad = STL(bad, period=12, robust=True).fit()
    eod = bat["eod_voltage_v"].resample("MS").mean()
    eod_dec = seasonal_decompose(eod, period=12)
    eod_season = pd.Series(eod_dec.seasonal.iloc[:12].values, index=MONTHS)
    injected = pd.to_datetime(["2025-08-18 09:00", "2025-09-28 14:00", "2025-09-28 15:00", "2025-10-31 03:00"])
    stl_rank = stl_res.abs().rank(ascending=False)
    eclipse = bus["eclipse_flag"] == 1
    return dict(
        kam=kam, tk=tk, bus=bus, demo=demo, bat=bat, ka=ka, ka_season=ka_season, weekly=weekly,
        noc7_std=float(noc7.resid.std()), noc12_std=float(noc12.resid.std()),
        aug_res=aug_res, full_res=full_res, stl_res=stl_res,
        aug_top=aug_res.abs().idxmax(), aug_top_val=float(aug_res.abs().max()),
        aug_second=float(aug_res.abs().sort_values(ascending=False).iloc[1]),
        full_top_eclipse=int(eclipse.reindex(full_res.abs().sort_values(ascending=False).index[:46]).sum()),
        stl_ranks=[int(stl_rank.loc[t]) for t in injected],
        stl_8th=float(stl_res.abs().sort_values(ascending=False).iloc[7]),
        aug_clean=float(ka.seasonal[ka.seasonal.index.month == 8].iloc[0]),
        aug_classic_bad=float(cl_bad.seasonal[cl_bad.seasonal.index.month == 8].iloc[0]),
        aug_stl_bad=float(st_bad.seasonal.loc["2024-08-01"]),
        aug_stl_bad_resid=float(st_bad.resid.loc["2024-08-01"]),
        eod=eod, eod_dec=eod_dec, eod_season=eod_season,
        add_sw=_swings(demo["additive"]), mul_sw=_swings(demo["multiplicative"]),
        log_sw=_swings(np.log(demo["multiplicative"])),
    )


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# =============================================================================
# LOCAL SVG HELPERS
# =============================================================================
def stack_svg(rows, *, w=760, h=600, gap=18, labels_w=150, delay0=.3):
    """Classic decomposition picture: one band per component, each with its own scale.
    rows: [(label, values, color)]."""
    n = len(rows)
    band = (h - gap * (n - 1)) / n
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    for k, (lab, vals, col) in enumerate(rows):
        v = np.asarray(vals, dtype=float)
        top = k * (band + gap)
        lo, hi = np.nanmin(v), np.nanmax(v)
        pad = (hi - lo) * .12 or 1
        lo, hi = lo - pad, hi + pad
        L, R = labels_w, w - 10
        out.append(f'<rect x="{L}" y="{top:.1f}" width="{R - L}" height="{band:.1f}" rx="12" fill="#0E1D30" stroke="{GRID}"/>')
        out.append(f'<text x="{L - 16}" y="{top + band / 2 + 8:.1f}" fill="{col}" font-size="24" font-weight="800" text-anchor="end">{lab}</text>')
        pts = [(_scale(i, 0, len(v) - 1, L + 12, R - 12), _scale(y, lo, hi, top + band - 8, top + 8))
               for i, y in enumerate(v) if not np.isnan(y)]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        out.append(f'<path class="draw" style="--dur:1.8s;--d:{delay0 + k * .45:.2f}s" d="{d}" fill="none" stroke="{col}" '
                   f'stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append("</svg>")
    return "".join(out)


def div_bars_svg(labels, values, *, w=1380, h=420, color=B["blue_d"], neg=B["gold"], fmt="{:+.1f}", lo=None, hi=None, highlight=()):
    """Bars that go up or down from a zero line (for seasonal effects)."""
    v = np.asarray(values, dtype=float)
    lo = min(v.min() * 1.25, 0) if lo is None else lo
    hi = max(v.max() * 1.35, 0) if hi is None else hi
    L, R, T, Bm = 20, w - 20, 30, h - 56
    z = _scale(0, lo, hi, Bm, T)
    slot = (R - L) / len(v)
    bw = slot * .6
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">',
           f'<line x1="{L}" x2="{R}" y1="{z:.1f}" y2="{z:.1f}" stroke="#9DB0C6" stroke-width="2"/>']
    for i, (lab, val) in enumerate(zip(labels, v)):
        x = L + i * slot + (slot - bw) / 2
        y = _scale(val, lo, hi, Bm, T)
        col = neg if (val < 0 or i in highlight) else color
        top, hgt = (y, z - y) if val >= 0 else (z, y - z)
        ty = y - 12 if val >= 0 else y + 30
        out.append(f'<g class="anim a-fade" style="--d:{.25 + i * .08:.2f}s"><rect x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(hgt, 2):.1f}" rx="6" fill="{col}"/>'
                   f'<text x="{x + bw / 2:.1f}" y="{ty:.1f}" fill="#EAF2FB" font-size="22" font-weight="800" text-anchor="middle">{fmt.format(val)}</text>'
                   f'<text x="{x + bw / 2:.1f}" y="{h - 18}" fill="{AXIS_TXT}" font-size="21" text-anchor="middle">{lab}</text></g>')
    out.append("</svg>")
    return "".join(out)


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    f = facts()
    ka, kam = f["ka"], f["kam"]
    obs = kam["availability_pct"].values

    title_stack = stack_svg([("observed", obs, "#EAF2FB"), ("trend", ka.trend.values, B["blue_d"]),
                             ("season", ka.seasonal.values, B["teal_d"]), ("noise", ka.resid.values, B["gold"])],
                            w=660, h=560, labels_w=170)
    ka_stack = stack_svg([("observed", obs, "#EAF2FB"), ("trend", ka.trend.values, B["blue_d"]),
                          ("seasonal", ka.seasonal.values, B["teal_d"]), ("residual", ka.resid.values, B["gold"])],
                         w=820, h=620, labels_w=150)

    # illustration for the Lagos-traffic equation
    x = np.linspace(0, 1, 60)
    tr = 30 + 25 * x
    se = 8 * np.sin(np.linspace(0, 6 * np.pi, 60))
    rng = np.random.default_rng(3)
    no = rng.normal(0, 2.2, 60)
    no[41] += 11
    parts = [("📈", "City growing", "trend", spark_svg(tr, color=B["blue_d"], delay=".4s")),
             ("🔁", "Rush hour, rainy season", "seasonality", spark_svg(se, color=B["teal_d"], delay=".8s")),
             ("🛺", "One keke breakdown", "noise", spark_svg(no, color=B["gold"], delay="1.2s"))]
    eq_cards = []
    for k, (e, t, kind, svg) in enumerate(parts):
        eq_cards.append(f'<div class="card anim a-pop" style="--d:{.3 + k * .4:.1f}s;flex:1;padding:24px 26px;text-align:center">'
                        f'<div style="font-size:58px">{e}</div><h3 style="font-size:28px;margin-top:6px">{t}</h3>'
                        f'<p class="small" style="margin-bottom:8px">{kind}</p>{svg}</div>')
        if k < 2:
            eq_cards.append(f'<div class="anim a-pop" style="--d:{.5 + k * .4:.1f}s;font-size:70px;font-weight:800;color:var(--muted);align-self:center">+</div>')
    eq_cards.append('<div class="anim a-pop" style="--d:1.7s;font-size:70px;font-weight:800;color:var(--muted);align-self:center">=</div>')
    eq_cards.append(f'<div class="card glow anim a-pop" style="--d:1.9s;flex:1;padding:24px 26px;text-align:center"><div style="font-size:58px">🚗</div>'
                    f'<h3 style="font-size:28px;margin-top:6px">Your trip to work</h3><p class="small" style="margin-bottom:8px">what you actually feel</p>'
                    f'{spark_svg(tr + se + no, color="#EAF2FB", delay="2.1s")}</div>')

    # NOC weekly seasonal
    weekly = f["weekly"]
    week_bars = div_bars_svg([d[:3] for d in DAYS], weekly.values, w=1380, h=320, lo=-3.6, hi=2.2)

    # additive vs multiplicative
    demo = f["demo"]
    add_svg = line_svg(demo["additive"].values, w=640, h=300, ymin=.2, ymax=1.0, area=False, stroke=4,
                       xlabels=[(0, "year 1"), (47, "year 4")], color=B["blue_d"], dur="2s")
    mul_svg = line_svg(demo["multiplicative"].values, w=640, h=300, ymin=.2, ymax=1.0, area=False, stroke=4,
                       xlabels=[(0, "year 1"), (47, "year 4")], color=B["gold"], dur="2s")
    log_svg = line_svg(np.log(demo["multiplicative"].values), w=1380, h=330, area=False, stroke=4,
                       xlabels=[(0, "year 1"), (47, "year 4")], color=B["teal_d"], dur="2.2s")
    a_sw, m_sw, l_sw = f["add_sw"], f["mul_sw"], f["log_sw"]

    # August residual (clean month) with the spike
    ar = f["aug_res"]
    top_i = int(np.where(ar.index == f["aug_top"])[0][0])
    aug_svg = line_svg(ar.values, w=1380, h=380, area=False, stroke=2.5, color=B["teal_d"],
                       xlabels=[(0, "1 Aug"), (len(ar) - 1, "31 Aug")],
                       yticks=[(0, "0 A"), (-10, "−10 A")],
                       markers=[(top_i, f"18 Aug, 09:00 → {f['aug_top_val']:.1f} A off", B["bad"])], dur="2.6s", max_points=2000)

    # whole-season residuals: classic vs STL
    fr, sr = f["full_res"], f["stl_res"]
    inj = [int(np.where(sr.index == pd.Timestamp(t))[0][0]) for t in ("2025-08-18 09:00", "2025-09-28 14:00", "2025-10-31 03:00")]
    cl_svg = line_svg(fr.values, w=640, h=280, area=False, stroke=1.6, color=B["gold"], ymin=-30, ymax=30,
                      xlabels=[(0, "Aug"), (len(fr) - 1, "Nov")], dur="2.2s", max_points=3000,
                      bands=[(int(np.where(fr.index == pd.Timestamp("2025-09-01"))[0][0]),
                              int(np.where(fr.index == pd.Timestamp("2025-10-16"))[0][0]), B["gold"], .10, "eclipse season")])
    st_svg = line_svg(sr.values, w=640, h=280, area=False, stroke=1.6, color=B["teal_d"], ymin=-30, ymax=30,
                      xlabels=[(0, "Aug"), (len(sr) - 1, "Nov")], dur="2.2s", max_points=3000,
                      markers=[(i, "", B["bad"]) for i in inj])

    # one catastrophic August
    cat_bars = div_bars_svg(["clean data", "classic + 1 bad August", "STL robust + 1 bad August"],
                            [f["aug_clean"], f["aug_classic_bad"], f["aug_stl_bad"]], w=860, h=380,
                            lo=-3.6, hi=.6, fmt="{:+.2f}")

    # three cycles
    m = kam["availability_pct"].values
    cyc_svg = line_svg(m, w=1380, h=330, ymin=97.5, ymax=100.3, area=False, stroke=4,
                       xlabels=[(0, "Jan 2023"), (12, "Jan 2024"), (24, "Jan 2025"), (35, "Dec 2025")],
                       bands=[(0, 11, B["blue_d"], .10, "cycle 1"), (12, 23, B["teal_d"], .10, "cycle 2"), (24, 35, B["gold"], .10, "cycle 3")])

    # battery: monthly end-of-discharge voltage + trend
    eod, eodd = f["eod"], f["eod_dec"]
    bat_svg = lines_svg([dict(values=eod.values, color=B["blue_d"], label="monthly", delay=".3s"),
                         dict(values=eodd.trend.values, color=B["gold"], stroke=5, label="trend", delay="1.6s")],
                        w=1380, h=360, xlabels=[(0, "Jan 2023"), (12, "Jan 2024"), (24, "Jan 2025"), (35, "Dec 2025")],
                        yticks=[(48, "48 V"), (49, "49 V"), (50, "50 V")])
    es = f["eod_season"]

    tr_valid = ka.trend.dropna()
    noc7, noc12 = f["noc7_std"], f["noc12_std"]

    slides = [
        # 1 ─ title
        S(f"""
<div class="row" style="gap:30px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Week 2 · Day 1</div>
  <h1 class="anim" style="--d:.2s">Take It Apart:<br><span class="hl">Trend, Season<br>and Noise</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:26px">One line on a chart is really three stories<br>stacked on top of each other. Today we pull them apart. 🔧</p>
  <div class="anim" style="--d:.8s;margin-top:38px;display:flex">{logos_title_block()}</div>
 </div>
 <div class="anim a-right" style="--d:.4s">{title_stack}</div>
</div>""",
          "Welcome to Week 2. Last week we learnt to read a series. Today we take one apart, like a mechanic opening an engine. "
          "The picture on the right is the real Ka-band series and its three parts. By the end of today, everyone can make it."),

        # 2 ─ last week
        S("""
<div class="kicker anim">Week 1 in 3 lines</div>
<h2 class="anim" style="--d:.1s">Quick warm-up before we open the engine</h2>
<div class="col" style="gap:22px;margin-top:16px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">⏱️</span><p><b>Order matters.</b> Shuffle a time series and the story dies.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">📉</span><p><b>Averages can hide trouble.</b> Look at the minimum when the question is “did we breach?”</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🪟</span><p><b>A 7-day window</b> smooths away the weekend rhythm.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:34px">Today's question: <b class="hl">that weekend rhythm and that rainy-season dip… can we measure them?</b></p>""",
          "Two-minute recap. Ask the room to finish each sentence before you reveal it."),

        # 3 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Three moves</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:380px;padding:44px 30px"><div class="icon">🔧</div><h3>Split it</h3><p class="small">trend + season + residual</p></div>
  <div class="arrow anim a-fade" style="--d:.6s"></div>
  <div class="box on anim a-pop" style="--d:.8s;min-width:380px;padding:44px 30px"><div class="icon">🥁</div><h3>Pick the rhythm</h3><p class="small">the period comes from the process</p></div>
  <div class="arrow anim a-fade" style="--d:1.1s"></div>
  <div class="box on anim a-pop" style="--d:1.3s;min-width:380px;padding:44px 30px"><div class="icon">🔍</div><h3>Read the leftovers</h3><p class="small">the residual is where trouble hides</p></div>
</div>
<div class="row anim" style="--d:1.7s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up</span>
</div>""",
          "Three moves. Split, pick the rhythm, read the leftovers."),

        # 4 ─ Lagos traffic hook
        S(f"""
<div class="kicker anim">Why is your trip to work so long?</div>
<h2 class="anim" style="--d:.1s">Lagos traffic = three things added 🚦</h2>
<div class="row" style="gap:18px;margin-top:26px;align-items:stretch">{''.join(eq_cards)}</div>
<p class="anim" style="--d:2.6s;margin-top:34px;text-align:center">Like jollof: you taste <b>one</b> pot, but it's rice + tomato base + that one surprise pepper. 🍛
<br><b class="hl">Decomposition = tasting each ingredient on its own.</b></p>""",
          "Ask: why was your trip long today? Lagos is growing every year (trend). Every weekday 7am is bad, and the rainy season is worse (seasonality). "
          "And sometimes one keke breaks down on Third Mainland Bridge (noise). You feel the total. Decomposition separates them again."),

        # 5 ─ the equation
        S(f"""
<div class="row" style="gap:50px;align-items:center;height:100%">
 <div style="flex:1">
  <div class="kicker anim">The one equation</div>
  <h2 class="anim" style="--d:.1s">observed =<br><span class="blue">trend</span> + <span class="teal">seasonal</span><br>+ <span class="hl">residual</span></h2>
  <p class="anim" style="--d:.4s;margin-top:10px">That's the <b>additive</b> model. Add the three bottom lines together and you get the top line back <b>exactly</b>.</p>
  <div class="card anim" style="--d:.7s;margin-top:28px;padding:22px 28px">
    <p style="font-size:26px">🔁 <b>Seasonal</b> repeats every period</p>
    <p style="font-size:26px">📈 <b>Trend</b> is what's left when the season is averaged away</p>
    <p style="font-size:26px">🎲 <b>Residual</b> is whatever is left over</p></div>
 </div>
 <div class="anim a-right" style="--d:.3s">{ka_stack}</div>
</div>""",
          "Quiz question: observed = trend + seasonal + residual. In the notebook they prove it: add the three parts and the difference from the original is zero. "
          "The chart is the real monthly Ka-band availability; each panel has its own scale."),

        # 6 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">One function does it all 🔧</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">statsmodels' <span class="mono hl">seasonal_decompose</span>: already installed in Colab.</p>""",
          "Section break.", cls="center"),

        # 7 ─ code
        S("""
<div class="kicker anim">The recipe</div>
<h2 class="anim" style="--d:.1s">Three lines, three parts</h2>
<pre class="code anim" style="--d:.3s;margin-top:4px;font-size:24px;padding:22px 30px">from statsmodels.tsa.seasonal import seasonal_decompose
parts = seasonal_decompose(kam["availability_pct"],
                           model="additive",    # or "multiplicative"
                           period=12)           # one rainy season = 12 months
parts.trend      # the slow direction
parts.seasonal   # the repeating pattern
parts.resid      # the leftovers</pre>
<div class="row" style="gap:22px;margin-top:20px">
  <div class="card step" data-step="1" style="flex:1;padding:22px 30px"><h3>⚠️ No gaps allowed</h3><p class="muted">NaN inside the series → <span class="mono">ValueError</span>. Fill or trim first.</p></div>
  <div class="card step" data-step="2" style="flex:1;padding:22px 30px"><h3>⚠️ Two full cycles minimum</h3><p class="muted">period=12 needs at least 24 rows, or it refuses to run.</p></div>
</div>""",
          "Walk the code line by line. The two warnings are the two errors they will hit most."),

        # 8 ─ ka decomposed with callouts
        S(f"""
<div class="row" style="gap:40px;align-items:center">
 <div class="anim a-left" style="--d:.2s">{ka_stack}</div>
 <div class="col" style="flex:1;gap:18px">
  <div class="kicker anim">Ka-band availability, decomposed</div>
  <div class="card anim" style="--d:.5s;padding:22px 26px"><p class="small">🔁 Seasonal: worst month</p><div class="stat" style="font-size:68px;color:var(--teal)">Aug {f['aug_clean']:+.1f}</div><p class="small">points below the yearly average: rainy season</p></div>
  <div class="card anim" style="--d:.8s;padding:22px 26px"><p class="small">📈 Trend</p><div class="stat" style="font-size:68px;color:var(--blue)">{tr_valid.iloc[0]:.2f} → {tr_valid.iloc[-1]:.2f}</div><p class="small">slowly improving (ground-station upgrades)</p></div>
  <div class="card anim" style="--d:1.1s;padding:22px 26px"><p class="small">🎲 Residual: biggest leftover</p><div class="stat" style="font-size:68px;color:var(--gold)">{ka.resid.abs().max():.2f}</div><p class="small">points. Nothing strange this time ✅</p></div>
 </div>
</div>""",
          f"Read the three numbers. Point out the trend has no values for the first and last 6 months: a 12-month moving average needs 6 months "
          f"on each side. That's normal, not missing data. Trend runs {tr_valid.index[0]:%b %Y} to {tr_valid.index[-1]:%b %Y}."),

        # 9 ─ period from the process
        S("""
<div class="kicker anim">The most common mistake</div>
<h2 class="anim" style="--d:.1s">The period comes from the <span class="hl">process</span>, not a default</h2>
<div class="grid3" style="margin-top:26px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">🛰️</div><h3>Bus power · hourly</h3><div class="stat" style="font-size:90px;color:var(--blue)">24</div><p class="muted">the eclipse comes once a day, at 21:00 UTC</p></div>
  <div class="card anim a-pop" style="--d:.6s"><div class="icon">🎫</div><h3>NOC tickets · daily</h3><div class="stat" style="font-size:90px;color:var(--teal)">7</div><p class="muted">the working week repeats every 7 days</p></div>
  <div class="card anim a-pop" style="--d:.9s"><div class="icon">🌧️</div><h3>Ka-band · monthly</h3><div class="stat" style="font-size:90px;color:var(--gold)">12</div><p class="muted">one rainy season every 12 months</p></div>
</div>
<p class="anim" style="--d:1.3s;margin-top:30px;text-align:center">Ask: <b class="hl">“how many rows until it repeats?”</b> That's your period.</p>""",
          "Quiz question: which period for daily NOC tickets? 7. Not 12 just because 12 feels like a 'season'. The period is a fact about the process."),

        # 10 ─ weekly pattern + wrong period
        S(f"""
<div class="kicker anim">NOC tickets · period = 7</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Even faults rest on Sunday 😄 (now measured)</h2>
<div class="card anim" style="--d:.2s;padding:16px 20px">{week_bars}</div>
<div class="row" style="gap:22px;margin-top:18px">
  <div class="card step" data-step="1" style="flex:1;border-color:#1E9E5A;padding:20px 30px"><h3>✅ period=7</h3><p class="muted">noise left over: <b style="color:#fff">{noc7:.2f}</b> tickets</p></div>
  <div class="card step" data-step="1" style="flex:1;border-color:#E5484D;padding:20px 30px"><h3>❌ period=12</h3><p class="muted">noise left: <b style="color:#fff">{noc12:.2f}</b> tickets (weekend stuck in the noise)</p></div>
</div>""",
          f"Seasonal effect per weekday, in tickets above or below the trend: Sunday {weekly['Sunday']:+.2f}, Saturday {weekly['Saturday']:+.2f}, "
          f"Tuesday {weekly['Tuesday']:+.2f}. With the wrong period (12) the leftover noise almost doubles ({noc7:.2f} → {noc12:.2f})."),

        # 11 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Add or multiply? ➕✖️</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Look at the swing. Does it stay the same size, or grow?</p>""",
          "Section break.", cls="center"),

        # 12 ─ additive vs multiplicative
        S(f"""
<div class="kicker anim">additive_multiplicative_demo.csv</div>
<h2 class="anim" style="--d:.1s;font-size:56px">Same trend, same season… different maths</h2>
<div class="grid2" style="margin-top:6px">
  <div class="card anim" style="--d:.25s;padding:22px 26px"><h3 class="blue">➕ Additive</h3>{add_svg}
    <p style="font-size:24px">Yearly swing: <b>{a_sw[0]:.2f} → {a_sw[-1]:.2f}</b>. Stays the same size.</p>
    <p class="small">🚌 Like December fare going up <b>₦100</b> every year: a fixed amount.</p></div>
  <div class="card anim" style="--d:.5s;padding:22px 26px"><h3 class="hl">✖️ Multiplicative</h3>{mul_svg}
    <p style="font-size:24px">Yearly swing: <b>{m_sw[0]:.2f} → {m_sw[-1]:.2f}</b>. Grows with the level.</p>
    <p class="small">🚌 Like December fare going up <b>20%</b>: 20% of a bigger fare is more naira.</p></div>
</div>""",
          "Quiz question: the seasonal swing grows as the level rises → multiplicative. In the course data, tickets and throughput behave multiplicatively; "
          "availability and battery capacity behave additively."),

        # 13 ─ log trick
        S(f"""
<div class="kicker anim">The log trick</div>
<h2 class="anim" style="--d:.1s">Take the log, and <span class="hl">multiply becomes add</span></h2>
<div class="card anim" style="--d:.2s;padding:18px 22px">{log_svg}</div>
<div class="row anim" style="--d:2.4s;margin-top:24px;gap:22px">
  <div class="card" style="flex:1"><p class="small">swing before the log</p><div class="stat" style="font-size:64px;color:var(--gold)">{m_sw[0]:.2f} → {m_sw[-1]:.2f}</div></div>
  <div class="card glow" style="flex:1"><p class="small">swing after <span class="mono">np.log()</span></p><div class="stat" style="font-size:64px;color:var(--teal)">{l_sw[0]:.2f} → {l_sw[-1]:.2f}</div></div>
</div>""",
          "np.log turns 'times' into 'plus'. After the log the swing is roughly constant, so an additive decomposition works. Or just pass model='multiplicative'."),

        # 14 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">Read the leftovers 🔍</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">When trend and season are explained, what's left is the interesting part.</p>""",
          "Section break.", cls="center"),

        # 15 ─ residual spike in August
        S(f"""
<div class="kicker anim">Bus power · solar-array current · August · period = 24</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The residual points straight at the fault 🎯</h2>
<div class="card anim" style="--d:.2s;padding:16px 20px">{aug_svg}</div>
<div class="row anim" style="--d:2.9s;margin-top:20px;gap:22px;align-items:center">
  <span class="pill bad">biggest leftover: {f['aug_top_val']:.1f} A</span><span class="pill">next biggest: only {f['aug_second']:.2f} A</span>
  <p class="small" style="margin-left:auto">NigComSat-1 was lost in 2008 to a solar-array failure. This is why we watch the array.</p>
</div>""",
          f"For an incident review, look at the residual, not the raw series (quiz question). In August there is no eclipse yet, so the daily season is clean, and "
          f"one hour sticks out: {f['aug_top']:%d %b %H:%M}, {f['aug_top_val']:.1f} A off its expected value. It's an injected solar-array string dropout. Week 3 builds detectors on exactly this idea."),

        # 16 ─ eclipse: classic vs STL
        S(f"""
<div class="kicker anim">Bus power · all 4 months · period = 24</div>
<h2 class="anim" style="--d:.1s;font-size:52px">A season that comes and goes needs a smarter tool</h2>
<div class="grid2" style="margin-top:6px">
  <div class="card anim" style="--d:.25s;padding:20px 24px"><h3>😵 classic <span class="mono" style="font-size:24px">seasonal_decompose</span></h3>{cl_svg}
    <p style="font-size:23px">Uses the <b>same</b> daily pattern for all 120 days, so the eclipse hours flood the residual. <b>{f['full_top_eclipse']}</b> of the top 46 leftovers are just eclipse.</p></div>
  <div class="card anim" style="--d:.5s;padding:20px 24px;border-color:#16A394"><h3>🙌 <span class="mono" style="font-size:24px">STL(robust=True)</span></h3>{st_svg}
    <p style="font-size:23px">Lets the season change slowly. The injected array dropouts rank <b>#{min(f['stl_ranks'])}–#{max(f['stl_ranks'])}</b>; after them nothing is bigger than <b>{f['stl_8th']:.2f} A</b>.</p></div>
</div>""",
          f"Classic decomposition assumes the same daily pattern every day. The eclipse season switches on and off, so it can't. STL can. With STL robust, "
          f"the top 3 leftovers are the first and last eclipse days (the season switching), then ranks {f['stl_ranks']} are the 4 injected dropout hours."),

        # 17 ─ one catastrophic August
        S(f"""
<div class="kicker anim">What if one August was a disaster?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Don't let one bad month spoil every August</h2>
<div class="row" style="gap:30px;align-items:center;margin-top:6px">
 <div class="card anim" style="--d:.2s;padding:16px 20px;flex:none">{cat_bars}</div>
 <div class="col" style="flex:1;gap:16px">
  <div class="card step" data-step="1"><p style="font-size:24px">We faked <b>Aug 2024 = 94%</b>. Classic decomposition now says <b class="bad">every</b> August is {f['aug_classic_bad']:+.1f}.</p></div>
  <div class="card step glow" data-step="2"><p style="font-size:24px"><span class="mono hl">STL(robust=True)</span> keeps August at {f['aug_stl_bad']:+.1f} and puts the disaster in the residual ({f['aug_stl_bad_resid']:+.1f}). ✅</p></div>
 </div>
</div>
<p class="anim" style="--d:1.4s;margin-top:24px;text-align:center">One bad experience at one buka shouldn't make you blacklist every buka in Lagos. 🍲</p>""",
          "Quiz question (advanced): one catastrophic August makes every August look bad → use STL with robust=True. Robust means outliers get less weight."),

        # 18 ─ three cycles
        S(f"""
<div class="kicker anim">How much history do you need?</div>
<h2 class="anim" style="--d:.1s">At least <span class="hl">three</span> full cycles</h2>
<div class="card anim" style="--d:.2s;padding:16px 20px">{cyc_svg}</div>
<div class="row anim" style="--d:2.4s;margin-top:22px;gap:22px">
  <div class="card" style="flex:1"><p style="font-size:24px">🌧️ Ka-band monthly: <b>{len(kam)} months = {len(kam)//12} rainy seasons</b>. That's the minimum, not a comfortable margin. Say so in your report.</p></div>
  <div class="card" style="flex:1"><p style="font-size:24px">🗣️ One friend says the new buka is sweet: <b>gist</b>. Three different friends: <b>pattern</b>. Now you go.</p></div>
</div>""",
          "Quiz question: three cycles is the minimum before trusting a seasonal profile. statsmodels technically runs with two, but two is not enough to trust."),

        # 19 ─ battery: two seasons a year
        S(f"""
<div class="kicker anim">battery_health_daily (Week 3 version) · end-of-discharge voltage, monthly</div>
<h2 class="anim" style="--d:.1s;font-size:52px">Not every season is one hump a year 🔋</h2>
<div class="card anim" style="--d:.2s;padding:16px 20px">{bat_svg}</div>
<div class="row anim" style="--d:2.6s;margin-top:20px;gap:22px">
  <div class="card" style="flex:1"><p style="font-size:24px">🔁 Seasonal dips in <b>March ({es['Mar']:+.2f} V)</b> and <b>September ({es['Sep']:+.2f} V)</b>: two eclipse seasons, one at each equinox.</p></div>
  <div class="card" style="flex:1"><p style="font-size:24px">📈 Trend: <b>{eodd.trend.dropna().iloc[0]:.2f} V → {eodd.trend.dropna().iloc[-1]:.2f} V</b>. The battery is slowly ageing. Decomposition separates the two effects.</p></div>
</div>""",
          "Two causes in one column: eclipse depth (seasonal, twice a year) and ageing (trend). This is the battery Week 6 forecasts to a threshold."),

        # 20 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Open the W2D1 exercise 🧑🏾‍💻</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open in Colab → <b>File → Save a copy in Drive</b> 💾</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">2</span><p><b>Part A:</b> take the Ka-band series apart</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">3</span><p><b>Part B:</b> right period, right model, read the leftovers</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">4</span><p>Replace every <span class="mono hl">___</span>, run, get the ✅</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🔧</div>
  <h3 style="margin-top:16px">13 checks to pass</h3>
  <p class="muted">12 tasks + 🌶️ the robust-August bonus</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on time. Most common problems: wrong period, forgetting asfreq, passing a column with NaN, forgetting quotes around 'multiplicative'."),

        # 21 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🔧</span><p><b>observed = trend + seasonal + residual.</b> Multiply when the swing grows.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🥁</span><p><b>The period comes from the process:</b> 24 · 7 · 12. Trust 3+ cycles.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🔍</span><p><b>Investigate the residual.</b> <span class="mono">STL(robust=True)</span> for messy seasons.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:36px">Next time 👉 <b class="hl">Does Today Remember Yesterday?</b> Find the period, don't guess it. 🔁</p>""",
          "Recap. Ask: what's the period for hourly bus power? For daily tickets? Where do you look for an unusual month?"),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    f = facts()
    ka, kam = f["ka"], f["kam"]
    labels = [d.strftime("%b %y") if d.month in (1, 4, 7, 10) else "" for d in kam.index]
    tr = ka.trend
    weekly = f["weekly"]
    demo = f["demo"]
    a_sw, m_sw, l_sw = f["add_sw"], f["mul_sw"], f["log_sw"]
    ar = f["aug_res"]
    aug_labels = [t.strftime("%d %b") if t.hour == 0 and t.day in (1, 8, 15, 22, 29) else "" for t in ar.index]
    eod, eodd = f["eod"], f["eod_dec"]
    es = f["eod_season"]
    tr_valid = tr.dropna()

    def nn(x):
        return [None if pd.isna(v) else round(float(v), 3) for v in x]

    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🔧", "kicker": "Week 2 · Day 1", "title": "Take It Apart: Trend, Season and Noise",
             "sub": "One line on a chart is three stories stacked together. Today we pull them apart",
             "notes": "Welcome to Week 2. Today we take a series apart like a mechanic opening an engine."},
            {"type": "flow", "title": "Today's mission: three moves", "steps": [
                ["🔧", "Split it", "trend + season + residual"],
                ["🥁", "Pick the rhythm", "the period comes from the process"],
                ["🔍", "Read the leftovers", "where trouble hides"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up", "notes": "Three moves."},
            {"type": "cards", "title": "Lagos traffic is three things added together", "cards": [
                ["📈", "Trend", "Lagos grows every year"],
                ["🔁", "Seasonality", "7am rush hour, rainy season"],
                ["🛺", "Noise", "one keke breakdown on the bridge"]],
             "notes": "Your trip = trend + season + noise. Decomposition separates them, like tasting each ingredient in the jollof."},
            {"type": "statement", "title": "The one equation", "icon": "🧮",
             "big": "observed = trend + seasonal + residual",
             "sub": "The additive model. Add the three parts back together and you get the original series exactly",
             "notes": "Quiz question 1 of this topic."},
            {"type": "section", "kicker": "Part 1", "title": "One function does it all", "sub": "statsmodels seasonal_decompose: already in Colab",
             "notes": "Section break."},
            {"type": "code", "title": "The recipe",
             "code": 'from statsmodels.tsa.seasonal import seasonal_decompose\n\nparts = seasonal_decompose(kam["availability_pct"],\n            model="additive",   # or "multiplicative"\n            period=12)          # 12 months = 1 rainy season\nparts.trend      # the slow direction\nparts.seasonal   # the repeating pattern\nparts.resid      # the leftovers',
             "caption": "No gaps allowed, and you need at least two full cycles (24 rows for period=12)",
             "notes": "The two warnings are the two errors they will hit most."},
            {"type": "chart", "title": "Ka-band availability: observed and its trend", "labels": labels,
             "series": [{"name": "observed (monthly)", "values": nn(kam["availability_pct"]), "color": "0A5DB4"},
                        {"name": "trend", "values": nn(tr), "color": "C77700"}],
             "ymin": 97.5, "ymax": 100.2, "fmt": "0.0",
             "notes": f"Trend runs {tr_valid.iloc[0]:.2f} to {tr_valid.iloc[-1]:.2f}: slowly improving. It's missing 6 months at each end; a 12-month moving average needs 6 months on each side."},
            {"type": "bar", "title": "The seasonal part: every month's effect, in points", "labels": MONTHS,
             "values": [round(float(v), 2) for v in f["ka_season"].values], "highlight": [6, 7, 8], "fmt": "+0.0;-0.0",
             "ymin": -1.4, "ymax": 0.8, "caption": f"August is {f['aug_clean']:+.1f} points: peak rainy season",
             "notes": "The seasonal component is the same 12 numbers repeated every year."},
            {"type": "table", "title": "The period comes from the process, not a default",
             "header": ["Series", "Cadence", "Period", "Why"],
             "rows": [["Bus power telemetry", "hourly", "24", "eclipse once a day, at 21:00 UTC"],
                      ["NOC tickets", "daily", "7", "the working week"],
                      ["Ka-band availability", "monthly", "12", "one rainy season a year"]],
             "colW": [3.2, 1.8, 1.4, 5.73], "notes": "Quiz: which period for daily NOC tickets? 7."},
            {"type": "bar", "title": "NOC tickets, period 7: even faults rest on Sunday", "labels": [d[:3] for d in DAYS],
             "values": [round(float(v), 2) for v in weekly.values], "highlight": [5, 6], "fmt": "+0.0;-0.0", "ymin": -3.5, "ymax": 2.0,
             "caption": f"Leftover noise: {f['noc7_std']:.2f} tickets with period=7 vs {f['noc12_std']:.2f} with the wrong period=12",
             "notes": "With the wrong period, the weekend gets stuck in the noise."},
            {"type": "section", "kicker": "Part 2", "title": "Add or multiply?", "sub": "Does the swing stay the same size, or grow?",
             "notes": "Section break."},
            {"type": "twochart", "title": "Same trend, same season, different maths",
             "left": {"label": f"Additive: swing stays {a_sw[0]:.2f} → {a_sw[-1]:.2f}", "labels": [str(i) for i in demo.index],
                      "values": [round(float(v), 3) for v in demo["additive"]], "ymin": 0.2, "ymax": 1.0, "fmt": "0.0", "good": True},
             "right": {"label": f"Multiplicative: swing grows {m_sw[0]:.2f} → {m_sw[-1]:.2f}", "labels": [str(i) for i in demo.index],
                       "values": [round(float(v), 3) for v in demo["multiplicative"]], "ymin": 0.2, "ymax": 1.0, "fmt": "0.0", "color": "C77700", "good": True},
             "notes": "Additive = fare goes up ₦100 every December. Multiplicative = fare goes up 20%."},
            {"type": "compare", "title": "The log trick: multiply becomes add",
             "left": ["✖️", f"Before: {m_sw[0]:.2f} → {m_sw[-1]:.2f}", "the yearly swing grows with the level"],
             "right": ["➕", f"After np.log(): {l_sw[0]:.2f} → {l_sw[-1]:.2f}", "the swing is roughly constant, so additive works"],
             "notes": "Or pass model='multiplicative' directly."},
            {"type": "section", "kicker": "Part 3", "title": "Read the leftovers", "sub": "Once trend and season are explained, what's left is the interesting part",
             "notes": "Section break."},
            {"type": "chart", "title": "August residual: one hour sticks out", "labels": aug_labels,
             "values": [round(float(v), 2) if not pd.isna(v) else None for v in ar.values], "ymin": -14, "ymax": 4, "fmt": "0", "color": "008C7E",
             "caption": f"{f['aug_top']:%d %b, %H:%M}: {f['aug_top_val']:.1f} A off expected. The next biggest is only {f['aug_second']:.2f} A",
             "notes": "It's an injected solar-array dropout. Week 3 builds detectors on this idea."},
            {"type": "compare", "title": "A season that comes and goes needs a smarter tool",
             "left": ["😵", "Classic decompose", f"Same daily pattern for 120 days: {f['full_top_eclipse']} of the top 46 leftovers are just eclipse hours"],
             "right": ["🙌", "STL(robust=True)", f"Season can change. Injected dropouts rank #{min(f['stl_ranks'])} to #{max(f['stl_ranks'])}; nothing else above {f['stl_8th']:.2f} A"],
             "notes": "The top 3 STL leftovers are the first and last eclipse days."},
            {"type": "bar", "title": "One disaster August: classic vs robust", "labels": ["clean data", "classic + bad Aug", "STL robust + bad Aug"],
             "values": [round(f["aug_clean"], 2), round(f["aug_classic_bad"], 2), round(f["aug_stl_bad"], 2)], "highlight": [1], "fmt": "+0.00;-0.00",
             "ymin": -3.5, "ymax": 0.5, "caption": "We faked Aug 2024 = 94%. Robust STL keeps August's seasonal effect and puts the disaster in the residual",
             "notes": "Quiz (advanced): one catastrophic August → STL with robust=True."},
            {"type": "stats", "title": "How much history? At least three full cycles", "sub": "Ka-band monthly: exactly the minimum",
             "stats": [[str(len(kam)), "months of Ka-band data"], [str(len(kam) // 12), "full rainy seasons"], ["3", "the minimum to trust"], ["6", "battery eclipse seasons in the same 3 years"]],
             "notes": "One friend = gist. Three friends = pattern."},
            {"type": "bar", "title": "Battery voltage: two seasons a year", "labels": MONTHS,
             "values": [round(float(v), 2) for v in es.values], "highlight": [2, 8], "fmt": "+0.00;-0.00", "ymin": -2.2, "ymax": 0.8,
             "caption": f"Dips in March and September (the two equinox eclipse seasons). Trend {eodd.trend.dropna().iloc[0]:.2f} → {eodd.trend.dropna().iloc[-1]:.2f} V: slow ageing",
             "notes": "Use the Week 3 version of battery_health_daily."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W2D1-exercise in Colab, Save a copy in Drive", "Part A: take the Ka-band series apart",
                "Part B: right period, right model, read the leftovers", "Replace every ___, run, get the green tick"],
             "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🔧", "observed = trend + seasonal + residual (multiply when the swing grows)"],
                ["🥁", "The period comes from the process: 24 · 7 · 12. Trust 3+ cycles"],
                ["🔍", "Investigate the residual; use STL(robust=True) for messy seasons"]],
             "next": "Next: Does Today Remember Yesterday?", "notes": "Tease autocorrelation."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
from statsmodels.tsa.seasonal import seasonal_decompose as _sd, STL as _STL

def _kam():
    return pd.read_csv(data_path("ka_band_availability_monthly"), parse_dates=["month"], index_col="month").asfreq("MS")

def _swings(x):
    x = np.asarray(x, dtype=float)
    return [x[i*12:(i+1)*12].max() - x[i*12:(i+1)*12].min() for i in range(len(x)//12)]

def _c_a1(x):
    return str(x).strip() == "MS", "\"MS\" = Month Start. Every month now has exactly one row.", \
        "Monthly data, labelled by the first day of each month. The code is two capital letters, in quotes."

def _c_a2(x):
    return int(x) == 3, "3 full rainy seasons: exactly the minimum to trust a seasonal pattern. Not a lot, but enough.", \
        "36 months ÷ 12 months per cycle."

def _c_a3(x):
    return int(x) == 12, "12! One rainy season = 12 monthly rows.", \
        "How many MONTHLY rows until the rainy season comes back?"

def _c_a4(x):
    k = _kam()["availability_pct"]
    err = float((x - k).abs().max())
    return err < 1e-9, f"Gap = {err:.0e}. Trend + seasonal + residual gives back the original EXACTLY. That's the additive model.", \
        "Add the three parts: parts.trend + parts.seasonal + parts.resid"

def _c_a5(x):
    return str(x).strip().lower() in {"8", "august", "aug"}, "August. Peak rainy season, the same story as Week 1, now measured.", \
        "parts.seasonal.idxmin() gives the date of the lowest seasonal value. Take its .month"

def _c_b1(x):
    return int(x) == 7, "7! The NOC works a weekly rhythm, so the pattern repeats every 7 daily rows.", \
        "Daily rows. What repeats every week?"

def _c_b2(x):
    tk = pd.read_csv(data_path("noc_tickets_daily"), parse_dates=["date"], index_col="date").asfreq("D")
    s = _sd(tk["tickets_raised"], period=7).seasonal
    want = s.groupby(s.index.day_name()).mean()["Sunday"]
    return abs(float(x) - want) < 0.06, f"About {want:.1f} tickets below normal on a Sunday. Even faults rest on Sunday 😄", \
        "Look up \"Sunday\" in the weekly table: weekly.loc[\"Sunday\"]"

def _c_b3(x):
    return int(x) == 12, "Right: the wrong period (12) leaves the weekend pattern stuck in the noise, so the noise is bigger.", \
        "Compare the two numbers printed above. Which period left MORE noise?"

def _c_b4(x):
    return str(x).strip().lower() == "multiplicative", "Multiplicative: the swing grows as the level grows, like a 20% fare increase.", \
        "Does the swing in the second chart stay the same size, or grow? Answer \"additive\" or \"multiplicative\"."

def _c_b5(x):
    demo = pd.read_csv(data_path("additive_multiplicative_demo"), index_col="month_index")
    ok = np.allclose(np.asarray(x, dtype=float), np.log(demo["multiplicative"].values))
    sw = _swings(x) if ok else [1, 2]
    return ok and sw[-1] / sw[0] < 1.15, f"After the log the swing barely moves ({sw[0]:.2f} → {sw[-1]:.2f}). Multiply has become add. 🪄", \
        "Use np.log(demo[\"multiplicative\"])"

def _c_b6(x):
    bus = pd.read_csv(data_path("bus_power_telemetry_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    want = _sd(bus["solar_array_current_a"].loc[:"2025-08-31"], period=24).resid.abs().idxmax()
    return pd.Timestamp(x) == want, f"{want:%d %b, %H:%M}: an injected solar-array dropout. The residual pointed straight at it. 🎯", \
        "aug_parts.resid.abs().idxmax() gives the TIME of the biggest leftover"

def _c_b7(x):
    return sorted(int(v) for v in x) == [3, 9], "March and September: the two eclipse seasons, one at each equinox. Not every season is one hump! 🔋", \
        "Give a list of two month numbers, e.g. [1, 2]. Read them from the seasonal bar chart."

def _c_bonus(x):
    return -1.6 < float(x) < -0.9, f"Robust STL keeps August at {float(x):+.2f}. The disaster went into the residual, not into every August. 🙌", \
        "Did you set robust=True? The answer should be close to the clean August (about −1.1)."

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "A5": _c_a5, "B1": _c_b1, "B2": _c_b2,
          "B3": _c_b3, "B4": _c_b4, "B5": _c_b5, "B6": _c_b6, "B7": _c_b7, "BONUS": _c_bonus}
HINTS = {"A4": "rebuilt should be parts.trend + parts.seasonal + parts.resid",
         "B6": "Pass the timestamp returned by idxmax()", "B7": "A list like [3, 9]"}
'''


def notebook_cells(setup_code):
    return [
        ("md", """# 🔧 Week 2 · Day 1: Take It Apart: Trend, Season and Noise

**Today:** one line on a chart is really three stories added together. You'll pull them apart, measure each one, and read the leftovers, where faults hide.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**
> Work in your copy (the new tab), not the original.

**Rule book:** keep `W2D1-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up (run this once, every time you open the notebook)
You should see `✅ Ready!`. If Colab says *"This notebook was not authored by Google"*, click **Run anyway**."""),
        ("setup", setup_code),
        ("md", """▶️ **The tool for today.** `seasonal_decompose` lives in the `statsmodels` library, already installed in Colab. `STL` is its smarter cousin (you'll meet it in Part B)."""),
        ("code", "from statsmodels.tsa.seasonal import seasonal_decompose, STL\nprint(\"🔧 Decomposition tools loaded\")"),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Take the Ka-band series apart (25 min) 🛰️

**The data:** `ka_band_availability_monthly`: the monthly average availability of the Ka-band Nigeria spot beam, 2023–2025.

### A1 ✍️ Declare the rhythm
This data has one row per month, labelled by the **first day** of the month. pandas' frequency code for "month start" is two capital letters. Fill it in (in quotes)."""),
        ("task", 'FREQ = ___\n\ncheck("A1", FREQ)', 'FREQ = "MS"\n\ncheck("A1", FREQ)'),
        ("code", 'assert FREQ is not None, "✍️ Do A1 first: fill in FREQ above, then run this cell again."\n\nkam = pd.read_csv(data_path("ka_band_availability_monthly"), parse_dates=["month"], index_col="month").asfreq(FREQ)\n\nkam["availability_pct"].plot(title="Ka-band availability, monthly: a dip every rainy season", marker="o")\nplt.ylabel("% of month the link was OK")\nplt.show()\nprint("rows:", len(kam))'),
        ("md", """### A2 ✍️ How many full cycles?
The rainy season comes once every 12 months. How many **full** rainy seasons are in this data? Use `len(kam)` and integer division `//`.

> 📖 **The rule:** you need **at least three full cycles** before you trust a seasonal pattern. One rainy season is gist. Three is a pattern."""),
        ("task", 'n_cycles = ___\nprint("full cycles:", n_cycles)\n\ncheck("A2", n_cycles)', 'n_cycles = len(kam) // 12\nprint("full cycles:", n_cycles)\n\ncheck("A2", n_cycles)'),
        ("md", """### A3 ✍️ Choose the period, then decompose
The **period** is how many rows until the pattern repeats. For monthly data with a yearly rainy season, what is it?"""),
        ("task", 'PERIOD = ___\n\ncheck("A3", PERIOD)', 'PERIOD = 12\n\ncheck("A3", PERIOD)'),
        ("code", 'assert PERIOD is not None, "✍️ Do A3 first: fill in PERIOD above."\n\nparts = seasonal_decompose(kam["availability_pct"], model="additive", period=PERIOD)\n\nfig = parts.plot()\nfig.set_size_inches(11, 7)\nplt.show()'),
        ("md", """📖 **Read the 4 panels, top to bottom:** the observed series, the **trend** (slow direction), the **seasonal** part (the same 12-month shape repeated) and the **residual** (leftovers).

Notice the trend is **missing for the first and last 6 months**. The trend is a 12-month moving average, so it needs 6 months on each side. That's normal, not missing data.

### A4 ✍️ Prove the equation
The additive model says **observed = trend + seasonal + residual**. Rebuild the series by adding the three parts, and the check measures the biggest gap from the original."""),
        ("task", 'rebuilt = ___\n\ncheck("A4", rebuilt)', 'rebuilt = parts.trend + parts.seasonal + parts.resid\n\ncheck("A4", rebuilt)'),
        ("md", """### A5 ✍️ Which month does the season hit hardest?
`parts.seasonal.idxmin()` returns the **date** of the lowest seasonal value. Add `.month` to get the month number."""),
        ("task", 'worst_season_month = ___\nprint("worst month number:", worst_season_month)\n\ncheck("A5", worst_season_month)',
         'worst_season_month = parts.seasonal.idxmin().month\nprint("worst month number:", worst_season_month)\n\ncheck("A5", worst_season_month)'),
        ("code", '# ▶️ the 12 seasonal numbers, one per calendar month\nseason = pd.Series(parts.seasonal.iloc[:12].values, index=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])\nseason.plot(kind="bar", title="Seasonal effect by month (points above/below the trend)")\nplt.axhline(0, color="grey")\nplt.show()\nseason.round(2)'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Right period, right model, read the leftovers (35 min) 🔍

### B1 ✍️ The period for daily NOC tickets
`noc_tickets_daily` has **one row per day**. The NOC works a weekly roster. What period should you use?

> 📖 The period comes from the **process**, never from a default."""),
        ("task", 'NOC_PERIOD = ___\n\ncheck("B1", NOC_PERIOD)', 'NOC_PERIOD = 7\n\ncheck("B1", NOC_PERIOD)'),
        ("code", 'assert NOC_PERIOD is not None, "✍️ Do B1 first: fill in NOC_PERIOD above."\n\ntk = pd.read_csv(data_path("noc_tickets_daily"), parse_dates=["date"], index_col="date").asfreq("D")\nnoc_parts = seasonal_decompose(tk["tickets_raised"], model="additive", period=NOC_PERIOD)\n\n# average seasonal effect for each day of the week\nweekly = noc_parts.seasonal.groupby(noc_parts.seasonal.index.day_name()).mean()\nweekly = weekly.reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])\nweekly.plot(kind="bar", title="Weekly seasonal effect: tickets above/below the trend")\nplt.axhline(0, color="grey")\nplt.show()\nweekly.round(2)'),
        ("md", """### B2 ✍️ How quiet is Sunday?
Read the Sunday value from the `weekly` table above (it's negative: below normal). Round to 1 decimal place."""),
        ("task", 'sunday_effect = ___\n\ncheck("B2", sunday_effect)', 'sunday_effect = round(weekly.loc["Sunday"], 1)\n\ncheck("B2", sunday_effect)'),
        ("md", """### B3 ✍️ What happens with the WRONG period?
▶️ Run the cell: it decomposes the same tickets with period 7 and with period 12, and prints how much **noise** (residual spread) is left over each time."""),
        ("code", 'def noise_left(period):\n    """How much leftover wobble is there after decomposing with this period?"""\n    return seasonal_decompose(tk["tickets_raised"], period=period).resid.std()\n\nprint(f"noise left with period 7 : {noise_left(7):.2f} tickets")\nprint(f"noise left with period 12: {noise_left(12):.2f} tickets")'),
        ("md", "✍️ Which period leaves **more** noise behind? (That's the wrong one: the weekend pattern got stuck in the noise.)"),
        ("task", 'noisier_period = ___\n\ncheck("B3", noisier_period)', 'noisier_period = 12\n\ncheck("B3", noisier_period)'),
        ("md", """### B4 ✍️ Add or multiply?
▶️ Run the cell to see two made-up series with the same trend and season. Look at the **size of the yearly swing**: does it stay the same, or grow as the level rises?"""),
        ("code", 'demo = pd.read_csv(data_path("additive_multiplicative_demo"), index_col="month_index")\n\nfig, axes = plt.subplots(1, 2, figsize=(12, 3.2), sharey=True)\ndemo["additive"].plot(ax=axes[0], title="Column 1: additive")\ndemo["multiplicative"].plot(ax=axes[1], title="Column 2: ???", color="#C77700")\nplt.show()'),
        ("md", "✍️ Which model fits **column 2**? Type `\"additive\"` or `\"multiplicative\"`."),
        ("task", 'model_for_column_2 = ___\n\ncheck("B4", model_for_column_2)', 'model_for_column_2 = "multiplicative"\n\ncheck("B4", model_for_column_2)'),
        ("md", """### B5 ✍️ The log trick
Taking the **logarithm** turns "multiply" into "add". Apply `np.log()` to the multiplicative column and watch the swing stop growing."""),
        ("task", 'log_series = ___\n\nif log_series is not None:\n    log_series.plot(title="log(multiplicative): the swing no longer grows", color="#008C7E")\n    plt.show()\ncheck("B5", log_series)',
         'log_series = np.log(demo["multiplicative"])\n\nif log_series is not None:\n    log_series.plot(title="log(multiplicative): the swing no longer grows", color="#008C7E")\n    plt.show()\ncheck("B5", log_series)'),
        ("md", """### B6 ✍️ Read the leftovers: find the fault 🎯
Satellite **solar-array current** for **August** (no eclipse yet, so every day has the same shape). Period = 24 hours. Decompose it, then find the hour with the **biggest leftover** (absolute residual)."""),
        ("code", 'bus = pd.read_csv(data_path("bus_power_telemetry_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\naug = bus["solar_array_current_a"].loc[:"2025-08-31"]\n\naug_parts = seasonal_decompose(aug, model="additive", period=24)\naug_parts.resid.plot(title="August residual: solar-array current (A)", color="#008C7E")\nplt.show()'),
        ("task", 'biggest_leftover_time = ___\nprint("biggest leftover at:", biggest_leftover_time)\n\ncheck("B6", biggest_leftover_time)',
         'biggest_leftover_time = aug_parts.resid.abs().idxmax()\nprint("biggest leftover at:", biggest_leftover_time)\n\ncheck("B6", biggest_leftover_time)'),
        ("md", """> 📖 That hour is a **solar-array string dropout**, planted in the data on purpose. NigComSat-1 was lost in 2008 after a solar-array failure, and next week you'll build detectors that catch this automatically.

### B7 ✍️ Two seasons in one year? 🔋
Battery **end-of-discharge voltage** drops during eclipse seasons. ▶️ Run the cell (note `week="week-03"`: we want the Week 3 version of this file), then read the bar chart: which **two** months dip?"""),
        ("code", 'bat = pd.read_csv(data_path("battery_health_daily", week="week-03"), parse_dates=["date"], index_col="date").asfreq("D")\neod = bat["eod_voltage_v"].resample("MS").mean()     # monthly average\n\neod_parts = seasonal_decompose(eod, model="additive", period=12)\neod_season = pd.Series(eod_parts.seasonal.iloc[:12].values, index=range(1, 13))\neod_season.plot(kind="bar", title="Battery voltage: seasonal effect by month number (V)")\nplt.axhline(0, color="grey")\nplt.show()\nprint("trend: from", round(eod_parts.trend.dropna().iloc[0], 2), "V to", round(eod_parts.trend.dropna().iloc[-1], 2), "V")'),
        ("task", 'dip_months = ___   # a list of two month numbers, e.g. [1, 2]\n\ncheck("B7", dip_months)', 'dip_months = [3, 9]   # a list of two month numbers, e.g. [1, 2]\n\ncheck("B7", dip_months)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task (bonus): one disaster August
Imagine **August 2024** was a catastrophe: availability fell to **94%**. The classic decomposition then says **every** August is terrible.
`STL` with `robust=True` gives less weight to one-off disasters. Set `robust` correctly, then read August 2024's **seasonal** value."""),
        ("code", 'bad = kam["availability_pct"].copy()\nbad.loc["2024-08-01"] = 94.0          # the pretend disaster\n\nclassic = seasonal_decompose(bad, period=12)\nprint("classic: August seasonal =", round(classic.seasonal.loc["2024-08-01"], 2), " <- every August now looks this bad")'),
        ("task", 'robust_parts = STL(bad, period=12, robust=___).fit()\n\nrobust_aug = robust_parts.seasonal.loc["2024-08-01"]\nprint("STL robust: August seasonal =", round(robust_aug, 2))\nprint("STL robust: Aug 2024 residual =", round(robust_parts.resid.loc["2024-08-01"], 2), " <- the disaster lives here now")\ncheck("BONUS", robust_aug)',
         'robust_parts = STL(bad, period=12, robust=True).fit()\n\nrobust_aug = robust_parts.seasonal.loc["2024-08-01"]\nprint("STL robust: August seasonal =", round(robust_aug, 2))\nprint("STL robust: Aug 2024 residual =", round(robust_parts.resid.loc["2024-08-01"], 2), " <- the disaster lives here now")\ncheck("BONUS", robust_aug)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard. Then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- **observed = trend + seasonal + residual** (additive). When the swing grows with the level, use **multiplicative**, or take the **log**.
- **The period comes from the process:** 24 for hourly telemetry, 7 for daily tickets, 12 for monthly data. The wrong period leaves the pattern stuck in the noise.
- **Trust a seasonal pattern only with 3+ full cycles.**
- **Investigate the residual.** That's where faults hide.
- **`STL(robust=True)`** handles seasons that change and one-off disasters.

**Next time:** *Does Today Remember Yesterday?*: how to **find** the period from the data instead of guessing. 🔁

<sub>Data: synthetic teaching datasets from the original Week 3 code book (`Time-series/week-03`). Safe to use in AI assistants. Real NIGCOMSAT data is not.</sub>"""),
    ]
