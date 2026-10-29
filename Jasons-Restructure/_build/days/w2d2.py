"""Week 2 · Day 2: Does Today Remember Yesterday? (autocorrelation)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf

from common import BRAND as B, ORIGINALS
from svgcharts import bars_svg, line_svg, lines_svg, spark_svg, _scale
from webdeck import logos_title_block

CODE = "W2D2"
TITLE = "Does Today Remember Yesterday?"

D3 = ORIGINALS / "week-03" / "data"

# The made-up suya/generator example lives in ONE place: the notebook's STEP 0 runs it,
# and the slides use exactly the same numbers.
SALES_CODE = r'''
def make_sales():
    """MADE-UP weekly sales at one Lagos market for a year (an illustration, not course data).
    Both rise toward December for their own reasons: festive suya, and generators for the holidays."""
    rng = np.random.default_rng(11)
    t = np.arange(52)
    idx = pd.RangeIndex(1, 53, name="week")
    suya = pd.Series(120 + 3.0 * t + rng.normal(0, 8, 52), index=idx, name="suya_sticks").round(1)
    gens = pd.Series(30 + 0.9 * t + rng.normal(0, 3, 52), index=idx, name="generators_sold").round(1)
    return suya, gens
'''


def _sales():
    ns: dict = {}
    exec(SALES_CODE, {"np": np, "pd": pd}, ns)
    return ns["make_sales"]()


def _data():
    bw = pd.read_csv(D3 / "bandwidth_throughput_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")["throughput_gbps"]
    tk = pd.read_csv(D3 / "noc_tickets_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")["tickets_raised"]
    bus = pd.read_csv(D3 / "bus_power_telemetry_hourly.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    tw = pd.read_csv(D3 / "twta_thermal_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    ka = pd.read_csv(D3 / "ka_band_availability_daily.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("D")["availability_pct"]
    util = pd.read_csv(D3 / "transponder_utilisation_monthly.csv", parse_dates=["month"], index_col="month")["util_pct"]
    rf = pd.read_csv(D3 / "rf_link_quality_hourly.csv", parse_dates=["timestamp"], index_col="timestamp")
    return bw, tk, bus, tw, ka, util, rf


def facts():
    """Every number used on the slides, computed from the data."""
    bw, tk, bus, tw, ka, util, rf = _data()
    suya, gens = _sales()
    a_ka = acf(ka, nlags=400)
    return {
        "r": {lag: bw.autocorr(lag) for lag in (1, 7, 14, 30)},
        "acf_bw": acf(bw, nlags=35),
        "band": 1.96 / np.sqrt(len(bw)),
        "tk_r1": tk.autocorr(1), "tk_r7": tk.autocorr(7),
        "bus_r24": bus["battery_soc_pct"].autocorr(24), "bus_r12": bus["battery_soc_pct"].autocorr(12),
        "ka_peak": int(a_ka[300:].argmax() + 300),
        "acf_util": acf(util, nlags=12),
        "mae_yesterday": (bw - bw.shift(1)).abs().mean(), "mae_last_week": (bw - bw.shift(7)).abs().mean(),
        "sales_raw": suya.corr(gens), "sales_diff": suya.diff().corr(gens.diff()),
        "twta_raw": tw["twta_temp_c"].corr(tw["rf_drive_pct"]),
        "twta_diff": tw["twta_temp_c"].diff().corr(tw["rf_drive_pct"].diff()),
        "rain_uplink": rf["rain_rate_mmhr"].corr(rf["uplink_power_dbm"]),
        "rain_cn": rf["rain_rate_mmhr"].corr(rf["cn_ratio_db"]),
    }


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# ---------------------------------------------------------------- local chart helpers
def acf_svg(vals, *, w=1420, h=440, band=None, highlight=(), label_every=7, ymin=-0.25, ymax=1.08,
            lag0_note=True, show_labels=True, delay0=.25, step=.035):
    """Correlogram bars that grow in. Lag 0 grey, highlighted lags gold, the chance band shaded."""
    n = len(vals)
    L, R, T, Bm = (80, w - 20, 20, h - 50) if show_labels else (10, w - 10, 10, h - 10)

    def X(i):
        return L + (i + 0.5) * (R - L) / n

    def Y(v):
        return _scale(v, ymin, ymax, Bm, T)

    bwid = (R - L) / n * 0.55
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    if band:
        out.append(f'<rect x="{L}" y="{Y(band):.1f}" width="{R - L}" height="{Y(-band) - Y(band):.1f}" fill="{B["blue_d"]}" fill-opacity=".16"/>')
    if show_labels:
        for yv in (0, 0.5, 1.0):
            out.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="#24384F" stroke-width="1"/>')
            out.append(f'<text x="{L - 12}" y="{Y(yv) + 7:.1f}" fill="#9DB0C6" font-size="20" text-anchor="end">{yv:.1f}</text>')
    out.append(f'<line x1="{L}" x2="{R}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="#9DB0C6" stroke-width="2"/>')
    for i, v in enumerate(vals):
        col = "#6F8399" if i == 0 else (B["gold"] if i in highlight else B["blue_d"])
        top, bot = Y(max(v, 0)), Y(min(v, 0))
        out.append(f'<rect class="anim" style="--d:{delay0 + i * step:.2f}s" x="{X(i) - bwid / 2:.1f}" y="{top:.1f}" '
                   f'width="{bwid:.1f}" height="{max(2, bot - top):.1f}" rx="3" fill="{col}"/>')
        if show_labels and i % label_every == 0:
            out.append(f'<text x="{X(i):.1f}" y="{h - 16}" fill="#9DB0C6" font-size="20" text-anchor="middle">{i}</text>')
    if show_labels and lag0_note:
        out.append(f'<text x="{X(0) + 22:.1f}" y="{Y(0.97) + 8:.1f}" fill="#9DB0C6" font-size="20">← lag 0 is always 1</text>'
                   f'<text x="{X(0) + 22:.1f}" y="{Y(0.85) + 8:.1f}" fill="#9DB0C6" font-size="20">ignore it</text>')
    out.append("</svg>")
    return "".join(out)


# ============================================================================== WEB SLIDES
def web_slides():
    f = facts()
    bw, tk, bus, tw, ka, util, rf = _data()
    suya, gens = _sales()
    r = f["r"]
    band = f["band"]

    # 8 weeks of throughput, weekends shaded (the file starts on a Monday)
    eight = bw.iloc[:56]
    is_we = eight.index.dayofweek >= 5
    wk_mean, we_mean = eight[~is_we].mean(), eight[is_we].mean()
    weekend_bands = [(k * 7 + 5 - .5, k * 7 + 6 + .5, B["gold"], .22, "") for k in range(8)]
    bw_chart = line_svg(eight.values, w=1420, h=400, ymin=2.2, ymax=3.8, area=False, stroke=4,
                        yticks=[(2.5, "2.5"), (3.0, "3.0"), (3.5, "3.5")],
                        xlabels=[(0, "week 1"), (21, "week 4"), (42, "week 7"), (55, "week 8")],
                        bands=weekend_bands, dur="2.6s")

    acf_big = acf_svg(f["acf_bw"], w=1420, h=440, band=band, highlight=(7, 14, 21, 28, 35))
    mini_kw = dict(w=380, h=170, show_labels=False, step=.02)
    shape_spikes = acf_svg(f["acf_bw"][:22], band=band, highlight=(7, 14, 21), **mini_kw)
    shape_trend = acf_svg(f["acf_util"], band=1.96 / np.sqrt(len(util)), delay0=.5, **mini_kw)
    rng = np.random.default_rng(3)
    shape_noise = acf_svg(acf(rng.normal(size=200), nlags=21), band=1.96 / np.sqrt(200), delay0=.8, **mini_kw)

    base_bars = bars_svg(["“same as yesterday”", "“same weekday last week”"],
                         [f["mae_yesterday"], f["mae_last_week"]], w=760, h=380, ymax=0.4,
                         highlight=(1,), fmt="{:.3f} Gbps")

    sidx = (suya / suya.iloc[:4].mean() * 100).values
    gidx = (gens / gens.iloc[:4].mean() * 100).values
    sales_chart = lines_svg([
        dict(values=sidx, color=B["gold"], stroke=4, label="suya", delay=".3s"),
        dict(values=gidx, color=B["teal_d"], stroke=4, label="generators", delay=".6s"),
    ], w=820, h=400, ymin=80, ymax=270, yticks=[(100, "100"), (200, "200")],
        xlabels=[(0, "week 1"), (51, "week 52")])

    tw_m = tw.resample("MS").mean()
    tw_temp = spark_svg(tw_m["twta_temp_c"].values, w=620, h=120, color=B["bad"], delay=".4s")
    tw_drive = spark_svg(tw_m["rf_drive_pct"].values, w=620, h=120, color=B["blue_d"], delay=".8s")

    # lag boxes: first 8 days of throughput
    v8 = bw.iloc[:8].round(2).tolist()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon"]

    def box(txt, col="#12233A", border="#24384F", fg="#EAF2FB"):
        return (f'<div style="width:132px;height:84px;border-radius:14px;background:{col};border:2px solid {border};color:{fg};'
                f'display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:800;flex:none">{txt}</div>')

    row_days = "".join(f'<div style="width:132px;text-align:center;color:#9DB0C6;font-size:22px;flex:none">{d}</div>' for d in days)
    row_today = "".join(box(f"{v:.2f}") for v in v8)
    row_shift1 = box("NaN", "transparent", "#FF6B6F", "#FF6B6F") + "".join(box(f"{v:.2f}", "#10263F", "#3B8BE0") for v in v8[:-1])
    match = box(f"{v8[7]:.2f}", "#3a2a06", "#F5B83D", "#FFE3A3")

    shift_cards = (
        f'<div class="col" style="gap:14px;margin-top:20px">'
        f'<div class="row" style="gap:12px;align-items:center"><div style="width:250px;font-size:24px;color:#9DB0C6">day</div>{row_days}</div>'
        f'<div class="row anim" style="--d:.3s;gap:12px;align-items:center"><div style="width:250px;font-size:24px"><b>today</b> <span class="mono small">s</span></div>{row_today}</div>'
        f'<div class="row step" data-step="1" style="gap:12px;align-items:center"><div style="width:250px;font-size:24px"><b class="blue">yesterday</b> <span class="mono small">s.shift(1)</span></div>{row_shift1}</div>'
        f'</div>')

    # random-split timeline: 21 days, random train/test colouring
    rs = np.random.default_rng(5).random(21) < 0.7          # True = train
    # a test day whose same weekday a week before AND after both sit in train (computed, not assumed)
    leak_day = next(d for d in range(8, 15) if not rs[d - 1] and rs[d - 8] and rs[d + 6])
    split_row = "".join(
        f'<div class="anim a-pop" style="--d:{.2 + i * .04:.2f}s;width:56px;height:56px;border-radius:12px;'
        f'background:{"#3B8BE0" if tr else "#F5B83D"};display:flex;align-items:center;justify-content:center;'
        f'font-size:18px;font-weight:800;color:#0B1622">{i + 1}</div>' for i, tr in enumerate(rs))
    time_row = "".join(
        f'<div style="width:56px;height:56px;border-radius:12px;background:{"#3B8BE0" if i < 15 else "#F5B83D"};'
        f'display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#0B1622">{i + 1}</div>'
        for i in range(21))

    # the -1..+1 scale with the three bandwidth lags on it
    def pos(v):
        return (v + 1) / 2 * 100

    scale = f"""
<div style="position:relative;height:200px;margin:30px 20px 0">
  <div style="position:absolute;left:0;right:0;top:80px;height:18px;border-radius:9px;background:linear-gradient(90deg,#E5484D,#24384F 50%,#3B8BE0)"></div>
  <div style="position:absolute;left:0;top:112px;font-size:24px;color:#FF9EA1">−1<br><span class="small">opposite</span></div>
  <div style="position:absolute;left:50%;transform:translateX(-50%);top:112px;font-size:24px;text-align:center">0<br><span class="small">no memory</span></div>
  <div style="position:absolute;right:0;top:112px;font-size:24px;text-align:right;color:#BFDcff">+1<br><span class="small">perfect copy</span></div>
  {''.join(f'<div class="anim a-pop" style="--d:{d}s;position:absolute;left:calc({pos(v):.1f}% - 70px);top:0;width:140px;text-align:center">'
           f'<div style="font-size:24px;font-weight:800;color:{c}">{lab}</div><div style="font-size:22px;color:{c}">{v:.2f}</div>'
           f'<div style="width:4px;height:22px;background:{c};margin:4px auto 0"></div></div>'
           for v, lab, c, d in ((r[30], "lag 30", "#9DB0C6", .5), (r[1], "lag 1", B["teal_d"], .8), (r[7], "lag 7", B["gold"], 1.1)))}
</div>"""

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:40px;top:150px;width:620px;height:480px">
  {acf_svg(f["acf_bw"][:29], w=620, h=430, band=band, highlight=(7, 14, 21, 28), show_labels=False, step=.05, delay0=.6)}
  <div class="small anim" style="--d:2.2s;text-align:center;margin-top:6px">the “memory” of 2 years of satellite throughput</div>
</div>
<div style="max-width:920px;margin-top:40px">
  <div class="kicker anim">Week 2 · Day 2</div>
  <h1 class="anim" style="--d:.2s">Does Today<br><span class="hl">Remember<br>Yesterday?</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Autocorrelation: how to measure a series' memory,<br>and how to spot a fake correlation. 🕵🏾</p>
  <div class="anim" style="--d:.8s;margin-top:44px;display:flex;justify-content:flex-start">{logos_title_block()}</div>
</div>""",
          "Today is about memory. Some data remembers yesterday, some remembers last week, and some remembers nothing. "
          "We measure it, then use it to find the season length ourselves instead of being told."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Three moves</h2>
<div class="flow" style="margin-top:70px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:380px;padding:46px 34px"><div class="icon">🪞</div><h3>Shift a copy</h3><p class="small">line today up with yesterday (a “lag”)</p></div>
  <div class="arrow anim a-fade" style="--d:.6s"></div>
  <div class="box on anim a-pop" style="--d:.8s;min-width:380px;padding:46px 34px"><div class="icon">🧠</div><h3>Measure the memory</h3><p class="small">autocorrelation, lag by lag</p></div>
  <div class="arrow anim a-fade" style="--d:1.1s"></div>
  <div class="box on anim a-pop" style="--d:1.3s;min-width:380px;padding:46px 34px"><div class="icon">🔎</div><h3>Read the correlogram</h3><p class="small">find the season; catch fake links</p></div>
</div>
<div class="row anim" style="--d:1.7s;margin-top:70px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up</span>
</div>""",
          "Three moves today. The hands-on is where it clicks."),

        # 3 ─ hook
        S("""
<div class="kicker anim">Quick question</div>
<h2 class="anim" style="--d:.1s">Third Mainland Bridge was jammed at 8am today. 🚗🚗🚗</h2>
<div class="grid2" style="margin-top:30px">
  <div class="card step" data-step="1"><div class="icon">📅</div><h3>Will it be jammed <span class="teal">tomorrow</span> at 8am?</h3>
    <p class="muted">Probably. Today tells you a lot about tomorrow. That's memory at <b style="color:#fff">lag 1</b>.</p></div>
  <div class="card step glow" data-step="2"><div class="icon">🗓️</div><h3>Will it be jammed <span class="hl">next Monday</span> at 8am?</h3>
    <p class="muted">Even more likely! Mondays look like Mondays. That's memory at <b style="color:#fff">lag 7</b>.</p></div>
</div>
<p class="sub step" data-step="3" style="margin-top:40px;text-align:center">Today we measure that memory with one number. Your satellite data has it too. 🛰️</p>""",
          "Ask the room both questions and let them answer. Most people instinctively know that next Monday is a better guess than tomorrow for a weekly pattern."),

        # 4 ─ bridge
        S("""
<div class="kicker anim">Last time 👉 today</div>
<h2 class="anim" style="--d:.1s">Yesterday we were <span class="muted">told</span> the season.<br>Today we <span class="hl">find it ourselves.</span></h2>
<div class="grid2" style="margin-top:36px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">📦</div><h3>Decomposition</h3>
    <p class="muted">You needed <span class="mono hl">period=7</span>, <span class="mono hl">12</span> or <span class="mono hl">24</span>. Somebody gave you the number.</p></div>
  <div class="card anim a-right glow" style="--d:.6s"><div class="icon">🔎</div><h3>Autocorrelation</h3>
    <p class="muted">The data <b style="color:#fff">shows you</b> the period. No guessing, no copying from the code book.</p></div>
</div>""",
          "Bridge from the decomposition day. The original code book has a table of periods; today they learn to confirm those periods from the data."),

        # 5 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">Memory 🧠</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Line a series up with its own past and see how alike they are.</p>""",
          "Section break.", cls="center"),

        # 6 ─ what is a lag
        S(f"""
<div class="kicker anim">What is a lag?</div>
<h2 class="anim" style="--d:.1s">A copy of the series, pushed back in time</h2>
<p class="sub anim" style="--d:.2s">Satellite throughput (Gbps), the first 8 days of the file</p>
{shift_cards}
<div class="row step" data-step="2" style="margin-top:34px;gap:24px;align-items:center">
  <pre class="code" style="font-size:26px;padding:18px 26px;margin:0">s.shift(1)   # yesterday
s.shift(7)   # same weekday last week</pre>
  <p style="flex:1">Now every row has <b>today</b> and <b class="blue">yesterday</b> side by side. Day 1 has no yesterday, so it gets <b class="bad">NaN</b>.</p>
</div>""",
          "Press next to slide the copy across. Lag = how many steps you push the copy. Lag 1 = yesterday, lag 7 = same weekday last week, lag 24 on hourly data = same hour yesterday."),

        # 7 ─ autocorrelation definition + scale
        S(f"""
<div class="kicker anim">Autocorrelation</div>
<h2 class="anim" style="--d:.1s">How much does the series look like<br><span class="hl">its own shifted copy?</span></h2>
<p class="sub anim" style="--d:.25s">One number between −1 and +1. “Auto” = with itself.</p>
{scale}
<pre class="code anim" style="--d:1.4s;margin-top:20px">s.autocorr(lag=1)    # {r[1]:.2f}  today vs yesterday
s.autocorr(lag=7)    # {r[7]:.2f}  today vs same weekday last week</pre>""",
          f"Real numbers from bandwidth_throughput_daily: lag 1 = {r[1]:.2f}, lag 7 = {r[7]:.2f}, lag 30 = {r[30]:.2f}. "
          "Note: the original code book says lag 1 is about 0.83. The real file gives 0.58. Trust the data, not the text."),

        # 8 ─ bandwidth chart
        S(f"""
<div class="kicker anim">Today's main dataset · bandwidth_throughput_daily.csv</div>
<h2 class="anim" style="--d:.1s;font-size:52px">8 weeks of throughput: spot the rhythm</h2>
<div class="card anim" style="--d:.2s;padding:18px 20px">{bw_chart}</div>
<div class="row anim" style="--d:2.8s;margin-top:22px;gap:14px;align-items:center">
  <span class="pill gold">🟨 weekends</span><span class="pill">weekdays ≈ {wk_mean:.1f} Gbps</span><span class="pill teal">weekends ≈ {we_mean:.1f} Gbps</span>
  <span class="small" style="margin-left:auto">synthetic teaching data · {len(bw):,} days</span>
</div>""",
          "Every weekend the throughput dips: offices close. So today looks less like yesterday (Friday vs Saturday is a big change) "
          "but very much like the same day last week. That's why lag 7 beats lag 1."),

        # 9 ─ the numbers
        S(f"""
<div class="kicker anim">The memory, in numbers</div>
<h2 class="anim" style="--d:.1s">It remembers <span class="teal">yesterday</span> a little.<br>It remembers <span class="hl">last Monday</span> a lot.</h2>
<div class="grid4" style="margin-top:30px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="stat count" data-to="{r[1]:.2f}" data-dec="2" data-d=".4">0</div><div class="stat-label">lag 1<br>yesterday</div></div>
  <div class="card anim a-pop glow" style="--d:.5s;text-align:center"><div class="stat count hl" data-to="{r[7]:.2f}" data-dec="2" data-d=".6">0</div><div class="stat-label">lag 7<br>last week</div></div>
  <div class="card anim a-pop" style="--d:.7s;text-align:center"><div class="stat count hl" data-to="{r[14]:.2f}" data-dec="2" data-d=".8">0</div><div class="stat-label">lag 14<br>2 weeks ago</div></div>
  <div class="card anim a-pop" style="--d:.9s;text-align:center"><div class="stat count muted" data-to="{r[30]:.2f}" data-dec="2" data-d="1">0</div><div class="stat-label">lag 30<br>a month ago</div></div>
</div>
<p class="anim" style="--d:1.4s;margin-top:40px;text-align:center">Like your mama: she forgets what you said yesterday, but <b class="hl">never</b> forgets you skipped church last Sunday. 😄</p>""",
          f"Lag 7 and 14 are both {r[7]:.2f}. The weekly pattern is very strong. Lag 30 is {r[30]:.2f}: 30 days ago is a different weekday, so almost no memory."),

        # 10 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">The Correlogram 📊</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Every lag at once, on one chart.</p>""",
          "Section break.", cls="center"),

        # 11 ─ correlogram
        S(f"""
<div class="kicker anim">plot_acf(s, lags=35)</div>
<h2 class="anim" style="--d:.1s;font-size:52px">The correlogram: one bar per lag</h2>
<div class="card anim" style="--d:.2s;padding:18px 20px">{acf_big}</div>
<div class="row anim" style="--d:2s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill gold">spikes at 7 · 14 · 21 · 28 · 35</span><span class="pill">shaded band = could be chance</span>
  <span class="pill teal">gap between spikes = the period</span>
</div>""",
          f"Bars are statsmodels ACF values (slightly smaller than .autocorr, e.g. lag 7 is {f['acf_bw'][7]:.2f} here vs {r[7]:.2f}; both are fine). "
          "Lag 0 is always 1: the series compared with itself. Ignore it. Spikes every 7 = weekly season, period 7."),

        # 12 ─ three shapes
        S(f"""
<div class="kicker anim">Reading a correlogram</div>
<h2 class="anim" style="--d:.1s">Three shapes you'll meet</h2>
<div class="grid3" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s;padding:26px"><h3>🎯 Regular spikes</h3>{shape_spikes}
    <p style="font-size:24px;margin-top:10px">= a <b class="hl">season</b>. Period = gap between spikes.</p><p class="small">throughput, daily</p></div>
  <div class="card anim a-pop" style="--d:.6s;padding:26px"><h3>🐢 Slow decay</h3>{shape_trend}
    <p style="font-size:24px;margin-top:10px">= a <b class="teal">trend</b>. Every month looks like the last.</p><p class="small">transponder use, monthly</p></div>
  <div class="card anim a-pop" style="--d:.9s;padding:26px"><h3>🎲 All inside the band</h3>{shape_noise}
    <p style="font-size:24px;margin-top:10px">= <b class="muted">no memory</b>. Pure noise.</p><p class="small">illustration</p></div>
</div>""",
          "Quiz questions 2 and 3. Spikes at regular lags = season. High bars that fade slowly = trend. Everything inside the shaded band = noise, nothing to learn."),

        # 13 ─ find the period
        S(f"""
<div class="kicker anim">Find the period from the data</div>
<h2 class="anim" style="--d:.1s">The spikes tell you the season length</h2>
<div class="grid4" style="margin-top:24px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">📶</div><h3>Throughput</h3><p class="small">daily · spikes at 7, 14, 21</p><div class="stat hl" style="font-size:80px;margin-top:14px">7</div><p class="small">working week</p></div>
  <div class="card anim a-pop" style="--d:.5s"><div class="icon">🎫</div><h3>NOC tickets</h3><p class="small">daily · lag 7 = {f['tk_r7']:.2f}</p><div class="stat hl" style="font-size:80px;margin-top:14px">7</div><p class="small">weekends are quiet</p></div>
  <div class="card anim a-pop" style="--d:.7s"><div class="icon">🔋</div><h3>Battery charge</h3><p class="small">hourly · lag 24 = {f['bus_r24']:.2f}</p><div class="stat hl" style="font-size:80px;margin-top:14px">24</div><p class="small">eclipse at 21:00 every day</p></div>
  <div class="card anim a-pop" style="--d:.9s"><div class="icon">🌧️</div><h3>Ka-band</h3><p class="small">daily · peak at lag {f['ka_peak']}</p><div class="stat hl" style="font-size:80px;margin-top:14px">{f['ka_peak']}</div><p class="small">rainy season, yearly</p></div>
</div>
<p class="anim" style="--d:1.3s;margin-top:30px;text-align:center">The period is a property of <b class="hl">the process</b>, not a default setting. Check it, don't assume it.</p>""",
          "These confirm the periods table in the original Week 3 code book, but this time from evidence. The Ka-band one is the bonus task in the notebook."),

        # 14 ─ baseline teaser
        S(f"""
<div class="kicker anim">Sneak peek of Week 5</div>
<h2 class="anim" style="--d:.1s">Memory = a free forecast 🎁</h2>
<div class="row" style="gap:50px;align-items:center;margin-top:10px">
  <div class="card anim" style="--d:.2s;padding:20px">{base_bars}</div>
  <div class="col" style="flex:1;gap:22px">
    <p class="anim" style="--d:.6s">Average daily error of two lazy forecasts on 2 years of throughput:</p>
    <p class="anim" style="--d:1s"><b class="hl">“Same weekday last week”</b> is about <b class="hl">{f['mae_yesterday'] / f['mae_last_week']:.0f}× more accurate</b> than “same as yesterday”.</p>
    <p class="anim small" style="--d:1.4s">Because lag 7 ({r[7]:.2f}) remembers more than lag 1 ({r[1]:.2f}).</p>
  </div>
</div>""",
          f"MAE same-as-yesterday = {f['mae_yesterday']:.3f} Gbps, same-weekday-last-week = {f['mae_last_week']:.3f} Gbps. "
          "This is the seasonal naive baseline from Week 5. Any fancy model must beat it."),

        # 15 ─ random split warning
        S(f"""
<div class="kicker anim">Why memory matters for testing</div>
<h2 class="anim" style="--d:.1s">Never split time data at random 🙅🏾</h2>
<div class="card anim" style="--d:.2s;margin-top:10px"><p class="small">Random split: <span style="color:#3B8BE0">■ train</span> <span style="color:#F5B83D">■ test</span></p>
  <div style="display:flex;gap:8px;margin-top:12px">{split_row}</div>
  <p style="margin-top:14px;font-size:26px">Day {leak_day} is in test, but days {leak_day - 7} and {leak_day + 7} (the same weekday, r = {r[7]:.2f}) are in train. <b class="bad">The answer leaked.</b></p></div>
<div class="card step glow" data-step="1" style="margin-top:22px"><p class="small">Split by time: train on the past, test on the future</p>
  <div style="display:flex;gap:8px;margin-top:12px">{time_row}</div>
  <p style="margin-top:14px;font-size:26px">Like WAEC: if you saw the questions before the exam, your score is fake. 📝 ✅ Honest.</p></div>""",
          "Quiz question 5. Neighbouring rows (and same-weekday rows) are near-copies, so a random split lets test answers leak into training. Week 5 Day 1 goes deep on this."),

        # 16 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">Correlation is not cause 🕵🏾</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">When two series move together, ask why before you believe it.</p>""",
          "Section break.", cls="center"),

        # 17 ─ suya vs generators
        S(f"""
<div class="kicker anim">A made-up story from one Lagos market</div>
<h2 class="anim" style="--d:.1s">Suya sales and generator sales rise together</h2>
<div class="row" style="gap:36px;align-items:center;margin-top:6px">
  <div class="card anim" style="--d:.2s;padding:16px 18px">{sales_chart}<p class="small" style="margin-left:20px">weekly sales, indexed (first month = 100)</p></div>
  <div class="col" style="flex:1;gap:22px">
    <div class="card anim a-pop" style="--d:1.2s;text-align:center"><div class="stat-label">correlation of the levels</div><div class="stat count hl" data-to="{f['sales_raw']:.2f}" data-dec="2" data-d="1.3">0</div><p class="small">“Suya sells generators!” 🤔</p></div>
    <div class="card step glow" data-step="1" style="text-align:center"><div class="stat-label">after <span class="mono">.diff()</span> (week-to-week changes)</div><div class="stat teal">{f['sales_diff']:.2f}</div><p class="small">collapses: it was just <b style="color:#fff">shared trend</b> (Detty December 🎉)</p></div>
  </div>
</div>""",
          f"Both rise toward December for their own reasons. The levels correlate at {f['sales_raw']:.2f}. "
          f"Compare week-to-week changes instead (.diff()) and it drops to {f['sales_diff']:.2f}. Shared trend, not a link."),

        # 18 ─ TWTA honest
        S(f"""
<div class="kicker anim">The real satellite case · twta_thermal_daily.csv</div>
<h2 class="anim" style="--d:.1s">Amplifier temperature vs RF drive</h2>
<div class="row" style="gap:36px;margin-top:10px;align-items:center">
  <div class="card anim" style="--d:.2s;flex:1.1;padding:22px 26px">
    <p class="small">🌡️ amplifier temperature (monthly)</p>{tw_temp}
    <p class="small" style="margin-top:12px">📡 RF drive level (monthly)</p>{tw_drive}</div>
  <div class="col" style="flex:1;gap:20px">
    <div class="card anim a-pop" style="--d:1s;text-align:center"><div class="stat-label">levels</div><div class="stat hl">{f['twta_raw']:.2f}</div></div>
    <div class="card step" data-step="1" style="text-align:center"><div class="stat-label">after <span class="mono">.diff()</span></div><div class="stat teal">{f['twta_diff']:.2f}</div></div>
  </div>
</div>
<p class="step" data-step="2" style="margin-top:26px;text-align:center">It <b class="hl">drops but survives</b>: part of it was shared trend, part is real physics (more drive → more heat).</p>""",
          f"Be honest here: the original code book says the correlation 'collapses' after differencing. It doesn't: {f['twta_raw']:.2f} → {f['twta_diff']:.2f}. "
          "When it collapses (suya) it was all shared trend. When it drops but survives (TWTA), part is trend and part is a real link."),

        # 19 ─ rain causes power
        S(f"""
<div class="kicker anim">Real correlation, one direction</div>
<h2 class="anim" style="--d:.1s">Rain and uplink power: r = <span class="hl">{f['rain_uplink']:.2f}</span></h2>
<div class="flow" style="margin-top:44px;justify-content:center">
  <div class="box on anim a-pop" style="--d:.3s;min-width:330px"><div class="icon">🌧️</div><h3>Heavy rain</h3><p class="small">signal fades</p></div>
  <div class="arrow anim a-fade" style="--d:.7s;width:120px"></div>
  <div class="box on anim a-pop" style="--d:.9s;min-width:330px"><div class="icon">🎚️</div><h3>Power control</h3><p class="small">ground station turns up the power</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s;width:120px"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:330px"><div class="icon">📡</div><h3>Uplink power rises</h3><p class="small">a <b>response</b>, not a cause</p></div>
</div>
<p class="anim" style="--d:2s;margin-top:44px;text-align:center">Turning up the power doesn't make it rain. 😄 Ask: <b class="hl">which one causes which?</b></p>""",
          f"From rf_link_quality_hourly: rain vs uplink power r = {f['rain_uplink']:.2f}, rain vs C/N r = {f['rain_cn']:.2f}. "
          "Correlation can be real AND causal, but direction matters. Feeding uplink power into a rain-fade detector leaks the answer (Week 4)."),

        # 20 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Open the exercise notebook 🧑🏾‍💻</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open <b class="hl">W2D2-exercise</b> in Colab</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">2</span><p><b>File → Save a copy in Drive</b> 💾</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">3</span><p>Run <b>STEP 0</b>, then go top to bottom</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">4</span><p>Replace every <span class="mono hl">___</span>, run, get the ✅</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🧠</div>
  <h3 style="margin-top:16px">13 checks to pass</h3>
  <p class="muted">Part A: memory (lags)<br>Part B: the correlogram<br>Part C: correlation ≠ cause<br>🌶️ Bonus: find the yearly season</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Common problems: forgetting .dropna() before plot_acf, typing s.autocorr(7) on the DataFrame instead of the column, mixing up the period with the lag value."),

        # 21 ─ recap
        S(f"""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🧠</span><p><b>Autocorrelation:</b> how much a series matches its own copy shifted by a <b class="hl">lag</b>.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">📊</span><p><b>Correlogram:</b> spikes = season (gap = period), slow decay = trend, inside the band = noise.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🕵🏾</span><p><b>Two trending series?</b> <span class="mono">.diff()</span> first. Correlation ≠ cause, and direction matters.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:40px">Next time 👉 <b class="hl">Lab Day + Quiz 1</b>, and you pick your final project. 🎯</p>""",
          "Recap. Ask a volunteer: what does a spike at lag 24 on hourly data mean? (a daily season). Tease Lab Day."),
    ]
    return slides


# ============================================================================== POWERPOINT
def pptx_spec():
    f = facts()
    bw, tk, bus, tw, ka, util, rf = _data()
    r = f["r"]
    eight = bw.iloc[:56]
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    labels8 = [f"wk{i // 7 + 1}" if i % 7 == 0 else "" for i in range(56)]
    first5 = bw.iloc[:5]
    shifted = bw.shift(1).iloc[:5]
    suya, gens = _sales()
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🧠", "kicker": "Week 2 · Day 2", "title": "Does Today Remember Yesterday?",
             "sub": "Autocorrelation: measure a series' memory, find its season, and catch fake correlations",
             "notes": "Today is about memory: some data remembers yesterday, some remembers last week."},
            {"type": "flow", "title": "Today's mission: three moves", "steps": [
                ["🪞", "Shift a copy", "line today up with yesterday"],
                ["🧠", "Measure the memory", "autocorrelation, lag by lag"],
                ["🔎", "Read the correlogram", "find the season, catch fake links"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up", "notes": "Three moves."},
            {"type": "compare", "title": "Third Mainland Bridge was jammed at 8am today",
             "left": ["📅", "Tomorrow at 8am?", "Probably. Today tells you about tomorrow: memory at lag 1"],
             "right": ["🗓️", "Next Monday at 8am?", "Even more likely: Mondays look like Mondays. Memory at lag 7"],
             "notes": "Ask the room both questions."},
            {"type": "section", "kicker": "Part 1", "title": "Memory", "sub": "Line a series up with its own past",
             "notes": "Section break."},
            {"type": "table", "title": "A lag is a copy pushed back in time: s.shift(1)",
             "header": ["Day", "today (Gbps)", "yesterday = s.shift(1)"],
             "rows": [[days[i], f"{first5.iloc[i]:.3f}", "NaN" if np.isnan(shifted.iloc[i]) else f"{shifted.iloc[i]:.3f}"] for i in range(5)],
             "colW": [3, 4.5, 4.63], "caption": "Day 1 has no yesterday, so it gets NaN",
             "notes": "Lag 1 = yesterday, lag 7 = same weekday last week, lag 24 on hourly data = same hour yesterday."},
            {"type": "statement", "title": "Autocorrelation", "icon": "🪞",
             "big": "How much does the series look like its own shifted copy?",
             "sub": "One number from −1 (opposite) through 0 (no memory) to +1 (perfect copy): s.autocorr(lag=7)",
             "notes": "Auto = with itself."},
            {"type": "chart", "title": "8 weeks of satellite throughput: weekends dip", "labels": labels8,
             "values": eight.round(3).tolist(), "ymin": 2.2, "ymax": 3.8, "fmt": "0.0", "freq": 7, "name": "Gbps",
             "caption": f"bandwidth_throughput_daily.csv · first 8 weeks: weekdays ≈ {eight[eight.index.dayofweek < 5].mean():.1f} Gbps, weekends ≈ {eight[eight.index.dayofweek >= 5].mean():.1f} Gbps",
             "notes": "Friday to Saturday is a big change, so lag 1 is weak; same day last week is strong."},
            {"type": "stats", "title": "It remembers last Monday far better than yesterday",
             "sub": "Autocorrelation of daily throughput at four lags",
             "stats": [[f"{r[1]:.2f}", "lag 1 · yesterday"], [f"{r[7]:.2f}", "lag 7 · last week"],
                       [f"{r[14]:.2f}", "lag 14 · two weeks ago"], [f"{r[30]:.2f}", "lag 30 · a month ago"]],
             "notes": f"The original code book says lag 1 is about 0.83; the real file gives {r[1]:.2f}."},
            {"type": "section", "kicker": "Part 2", "title": "The Correlogram", "sub": "Every lag at once, on one chart",
             "notes": "Section break."},
            {"type": "bar", "title": "The correlogram: spikes every 7 days", "labels": [str(i) for i in range(22)],
             "values": [round(float(x), 2) for x in f["acf_bw"][:22]], "highlight": [7, 14, 21], "fmt": "0.0", "ymin": 0, "ymax": 1.1,
             "name": "autocorrelation", "caption": "Lag 0 is always 1: ignore it. Gap between spikes = the period (7)",
             "notes": "plot_acf(s, lags=35) draws this. Spikes at 7, 14, 21 = weekly season."},
            {"type": "cards", "title": "Three shapes you'll meet", "cards": [
                ["🎯", "Regular spikes", "A season. Period = the gap between spikes"],
                ["🐢", "Slow decay", "A trend. Every step looks like the last (transponder use)"],
                ["🎲", "All inside the band", "No memory. Pure noise"]],
             "notes": "Quiz questions 2 and 3."},
            {"type": "table", "title": "The spikes tell you the season length",
             "header": ["Dataset", "Cadence", "What the correlogram shows", "Period"],
             "rows": [["Throughput", "daily", "spikes at 7, 14, 21", "7"],
                      ["NOC tickets", "daily", f"lag 7 = {f['tk_r7']:.2f} vs lag 1 = {f['tk_r1']:.2f}", "7"],
                      ["Battery charge", "hourly", f"lag 24 = {f['bus_r24']:.2f}", "24"],
                      ["Ka-band availability", "daily", f"peak at lag {f['ka_peak']}", str(f["ka_peak"])]],
             "colW": [3.2, 1.8, 5.1, 2.03], "caption": "The period comes from the process. Check it, don't assume it",
             "notes": "The Ka-band one is the bonus task."},
            {"type": "bar", "title": "Memory gives you a free forecast", "labels": ["same as yesterday", "same weekday last week"],
             "values": [round(f["mae_yesterday"], 3), round(f["mae_last_week"], 3)], "highlight": [1], "fmt": "0.000", "ymin": 0, "ymax": 0.4,
             "name": "average error (Gbps)",
             "caption": f"Average daily error over 2 years: last week's same weekday is about {f['mae_yesterday'] / f['mae_last_week']:.0f}× more accurate",
             "notes": "This is the seasonal naive baseline from Week 5."},
            {"type": "compare", "title": "Never split time data at random",
             "left": ["🎲", "Random split", f"Same-weekday rows (r = {r[7]:.2f}) land in both train and test. The answer leaks"],
             "right": ["⏩", "Split by time", "Train on the past, test on the future. Honest, like an exam with no expo"],
             "notes": "Quiz question 5."},
            {"type": "section", "kicker": "Part 3", "title": "Correlation is not cause", "sub": "When two series move together, ask why",
             "notes": "Section break."},
            {"type": "chart", "title": "Made-up: suya and generator sales rise together",
             "labels": [f"wk{i}" if i % 4 == 1 else "" for i in suya.index],
             "series": [{"name": "suya (index)", "values": (suya / suya.iloc[:4].mean() * 100).round(1).tolist(), "color": "C77700"},
                        {"name": "generators (index)", "values": (gens / gens.iloc[:4].mean() * 100).round(1).tolist(), "color": "008C7E"}],
             "ymin": 80, "ymax": 270, "fmt": "0",
             "notes": "Illustration only, not course data."},
            {"type": "compare", "title": "Compare the changes, not the levels: .diff()",
             "left": ["📈", f"Levels: r = {f['sales_raw']:.2f}", "“Suya sells generators!” Looks convincing"],
             "right": ["🔍", f"Changes: r = {f['sales_diff']:.2f}", "Collapses: it was only shared trend (Detty December)"],
             "notes": "When differencing makes it collapse, it was shared trend."},
            {"type": "compare", "title": "The real case: amplifier temperature vs RF drive",
             "left": ["🌡️", f"Levels: r = {f['twta_raw']:.2f}", "Both drift upward over two years"],
             "right": ["📡", f"After .diff(): r = {f['twta_diff']:.2f}", "Drops but survives: part shared trend, part real physics"],
             "notes": "Be honest: it does not collapse, despite what the original text says."},
            {"type": "flow", "title": f"Rain and uplink power: r = {f['rain_uplink']:.2f}, but one direction", "steps": [
                ["🌧️", "Heavy rain", "signal fades"],
                ["🎚️", "Power control", "station turns up the power"],
                ["📡", "Uplink power rises", "a response, not a cause"]],
             "footer": "Turning up the power doesn't make it rain. Ask which causes which",
             "notes": "Feeding uplink power into a rain-fade detector leaks the answer."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W2D2-exercise in Colab", "File → Save a copy in Drive", "Run STEP 0, then top to bottom",
                "Replace every ___, run, get the green tick"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🧠", "Autocorrelation: how much a series matches its own copy shifted by a lag"],
                ["📊", "Correlogram: spikes = season (gap = period), slow decay = trend, inside band = noise"],
                ["🕵🏾", "Two trending series? .diff() first. Correlation ≠ cause, and direction matters"]],
             "next": "Next: Lab Day + Quiz 1, and you pick your final project", "notes": "Tease Lab Day."},
        ],
    }


# ============================================================================== NOTEBOOK
CHECKS = SALES_CODE + r'''

def _bw():
    return pd.read_csv(data_path("bandwidth_throughput_daily"), parse_dates=["date"], index_col="date").asfreq("D")["throughput_gbps"]

def _near(x, want, tol):
    return abs(float(x) - float(want)) <= tol

def _c_a2(x):
    s = _bw()
    ok = isinstance(x, pd.Series) and len(x) == len(s) and np.isnan(x.iloc[0]) and np.allclose(x.iloc[1:].values, s.iloc[:-1].values)
    return ok, "Yes! Every value slid down one day. Day 1 has no yesterday, so it's NaN.", \
        "Use s.shift(1): it pushes the whole column down by one step."

def _c_a3(x):
    v = _bw().autocorr(lag=1)
    return _near(x, v, 0.005), f"r = {v:.2f}. Today remembers yesterday… a little.", "Try s.autocorr(lag=1)"

def _c_a4(x):
    v = _bw().autocorr(lag=7)
    return _near(x, v, 0.005), f"r = {v:.2f}! Last week's same day is almost a perfect copy. Mondays look like Mondays.", \
        "Same as A3, but lag=7."

def _c_b2(x):
    return int(x) == 7, "Period 7: spikes at 7, 14, 21, 28 = the working week. 💼", \
        "Look at WHERE the tall bars are (ignore lag 0). What's the gap between them?"

def _c_b3(x):
    return float(x) == 1.0, "Lag 0 is always 1: the series compared with itself. Ignore that bar.", \
        "What do you get if you compare anything with an exact copy of itself?"

def _c_b4(x):
    return int(x) == 7, "7 again: even faults rest at the weekend. 😄", "Same idea as B2: the gap between the tall spikes."

def _c_b5(x):
    return int(x) == 24, "24 hours: the eclipse hits at 21:00 every day, so the battery repeats daily. 🔋", \
        "This data is HOURLY. Where is the first big spike after lag 0?"

def _c_b6(x):
    return str(x).strip().lower() == "trend", "Trend! High bars that fade slowly = every month looks like the last.", \
        "Choose: season, trend or noise. No spikes, slow fade…"

def _c_b7(x):
    s = _bw(); v = (s - s.shift(7)).abs().mean()
    return _near(x, v, 0.0005), f"{v:.3f} Gbps: about {(s - s.shift(1)).abs().mean() / v:.0f}× smaller than 'same as yesterday'. Free forecast! 🎁", \
        "Copy the mae_yesterday line, but shift by 7."

def _c_c2(x):
    suya, gens = make_sales(); v = suya.corr(gens)
    return _near(x, v, 0.005), f"r = {v:.2f}. Wow, suya sells generators?! 🤔 (Hold on…)", "Use suya.corr(gens)"

def _c_c3(x):
    suya, gens = make_sales(); v = suya.diff().corr(gens.diff())
    return _near(x, v, 0.005), f"r = {v:.2f}. Collapsed! It was only shared trend (Detty December). 🎉", \
        "Use suya.diff().corr(gens.diff())"

def _c_c4(x):
    tw = pd.read_csv(data_path("twta_thermal_daily", week="week-03"), parse_dates=["date"], index_col="date").asfreq("D")
    raw = tw["twta_temp_c"].corr(tw["rf_drive_pct"]); dif = tw["twta_temp_c"].diff().corr(tw["rf_drive_pct"].diff())
    return _near(x[0], raw, 0.005) and _near(x[1], dif, 0.005), \
        f"{raw:.2f} → {dif:.2f}: it drops but survives. Part shared trend, part real physics (more drive → more heat).", \
        "Same two lines as C2 and C3, but with twta['twta_temp_c'] and twta['rf_drive_pct']."

def _c_bonus(x):
    return 360 <= int(x) <= 370, f"Lag {int(x)}: about a year! The rainy season comes back every 365 days. 🌧️", \
        "acf_vals[300:].argmax() gives the position INSIDE the slice. Add 300 back."

CHECKS = {"A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4, "B5": _c_b5,
          "B6": _c_b6, "B7": _c_b7, "C2": _c_c2, "C3": _c_c3, "C4": _c_c4, "BONUS": _c_bonus}
HINTS = {"C4": "Give two numbers: twta_raw and twta_diff.", "BONUS": "acf_vals[300:].argmax() + 300"}
'''


def notebook_cells(setup_code):
    return [
        ("md", """# 🧠 Week 2 · Day 2: Does Today Remember Yesterday?

**Today:** measure how much a series remembers its own past (**autocorrelation**), read a **correlogram** to find the season yourself, and catch a **fake correlation** before it fools your boss.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then press **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**
> Work in your copy (the new tab), not the original.

**Rule book:** keep `W2D2-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up (run this once, every time you open the notebook)

Click the cell below and press **Shift + Enter**. Wait for `✅ Ready!`. If Colab says *"This notebook was not authored by Google"*, click **Run anyway**."""),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: How much does today remember? (20 min) 🧠

**The data:** `bandwidth_throughput_daily.csv`: total data carried by the Nigeria spot beam each day, in Gbps (gigabits per second), for two years. Synthetic, built to behave like NigComSat-1R.

### A1 ▶️ Load it and look at 8 weeks
The same 3-line recipe from Day 1. Look at the chart: what happens every weekend?"""),
        ("code", 'bw = pd.read_csv(data_path("bandwidth_throughput_daily"), parse_dates=["date"], index_col="date").asfreq("D")\n'
                 's = bw["throughput_gbps"]          # one column = one series. We\'ll call it s\n\n'
                 's.iloc[:56].plot(title="8 weeks of throughput: dips every weekend", marker="o", ms=3)\n'
                 'plt.ylabel("Gbps")\nplt.show()'),
        ("md", """### A2 ✍️ Make "yesterday"
A **lag** is a copy of the series pushed back in time. `s.shift(1)` slides every value down one row, so each day sits next to **yesterday's** value.
Create the lag-1 copy."""),
        ("task", 'yesterday = ___\n\ncheck("A2", yesterday)', 'yesterday = s.shift(1)\n\ncheck("A2", yesterday)'),
        ("md", "▶️ See them side by side. Day 1 has no yesterday, so it shows `NaN`."),
        ("code", 'assert yesterday is not None, "✍️ Do A2 first: fill in yesterday above, then run this cell again."\n\n'
                 'pd.DataFrame({"today": s, "yesterday": yesterday, "same day last week": s.shift(7)}).head(9)'),
        ("md", """### A3 ✍️ Lag-1 autocorrelation
**Autocorrelation** = how much a series looks like its own shifted copy: one number from −1 to +1.
pandas does it in one line: `s.autocorr(lag=1)`."""),
        ("task", 'r1 = ___\nprint("today vs yesterday:", r1)\n\ncheck("A3", r1)', 'r1 = s.autocorr(lag=1)\nprint("today vs yesterday:", r1)\n\ncheck("A3", r1)'),
        ("md", """### A4 ✍️ Lag-7 autocorrelation
Now compare each day with the **same weekday last week**."""),
        ("task", 'r7 = ___\nprint("today vs same day last week:", r7)\n\ncheck("A4", r7)', 'r7 = s.autocorr(lag=7)\nprint("today vs same day last week:", r7)\n\ncheck("A4", r7)'),
        ("md", "▶️ A few more lags. Which ones remember, which ones forget?"),
        ("code", 'for lag in [1, 2, 7, 14, 30]:\n    print(f"lag {lag:>2}: {s.autocorr(lag=lag):.2f}")'),
        ("md", """> 💡 Lag 30 is close to 0 because 30 days ago was a **different weekday**. The memory here is weekly. Like your mama: she forgets what you said yesterday, but never forgets you skipped church last Sunday. 😄"""),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: The correlogram (25 min) 📊

A **correlogram** (ACF plot) draws the autocorrelation for **every lag at once**: one bar per lag.
- The **shaded band**: bars inside it could be chance.
- **Spikes at regular lags** = a season. The **gap between spikes = the period.**

### B1 ▶️ Draw the correlogram of throughput"""),
        ("code", 'from statsmodels.graphics.tsaplots import plot_acf\n\n'
                 'plot_acf(s.dropna(), lags=35)          # always .dropna() first\n'
                 'plt.title("Correlogram: daily throughput")\nplt.xlabel("lag (days)")\nplt.show()'),
        ("md", """### B2 ✍️ What's the period?
Ignore the bar at lag 0. Where do the tall spikes appear? The **gap** between them is the period."""),
        ("task", 'period_throughput = ___\n\ncheck("B2", period_throughput)', 'period_throughput = 7\n\ncheck("B2", period_throughput)'),
        ("md", """### B3 ✍️ The lag-0 bar
Look at the very first bar (lag 0). What is its height, every single time, for any series?"""),
        ("task", 'lag0_value = ___\n\ncheck("B3", lag0_value)', 'lag0_value = 1\n\ncheck("B3", lag0_value)'),
        ("md", """### B4 ✍️ Your turn: NOC tickets
▶️ Run the cell: daily NOC fault tickets and their correlogram. Then write the period you see."""),
        ("code", 'tk = pd.read_csv(data_path("noc_tickets_daily"), parse_dates=["date"], index_col="date").asfreq("D")\n\n'
                 'plot_acf(tk["tickets_raised"].dropna(), lags=35)\nplt.title("Correlogram: NOC tickets per day")\nplt.xlabel("lag (days)")\nplt.show()'),
        ("task", 'period_tickets = ___\n\ncheck("B4", period_tickets)', 'period_tickets = 7\n\ncheck("B4", period_tickets)'),
        ("md", """### B5 ✍️ Hourly satellite telemetry
This file is **hourly**: battery state of charge on the satellite. Careful: here one lag = **one hour**. Where's the first big spike?"""),
        ("code", 'bus = pd.read_csv(data_path("bus_power_telemetry_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n\n'
                 'plot_acf(bus["battery_soc_pct"].dropna(), lags=72)\nplt.title("Correlogram: battery charge, hourly")\nplt.xlabel("lag (hours)")\nplt.show()'),
        ("task", 'period_battery_hours = ___\n\ncheck("B5", period_battery_hours)', 'period_battery_hours = 24\n\ncheck("B5", period_battery_hours)'),
        ("md", """### B6 ✍️ Name the shape
Monthly transponder utilisation: what does this correlogram look like? Type `"season"`, `"trend"` or `"noise"`.

| Shape | Means |
|---|---|
| spikes at regular lags | season |
| high bars that fade slowly | trend |
| everything inside the band | noise |"""),
        ("code", 'util = pd.read_csv(data_path("transponder_utilisation_monthly"), parse_dates=["month"], index_col="month").asfreq("MS")\n\n'
                 'plot_acf(util["util_pct"].dropna(), lags=12)\nplt.title("Correlogram: transponder utilisation, monthly")\nplt.xlabel("lag (months)")\nplt.show()'),
        ("task", 'shape = ___\n\ncheck("B6", shape)', 'shape = "trend"\n\ncheck("B6", shape)'),
        ("md", """### B7 ✍️ Memory = a free forecast 🎁
Two lazy forecasts for throughput: **"same as yesterday"** and **"same weekday last week"**.
We measure each one's average mistake (MAE = mean absolute error). The first is done. Write the second."""),
        ("task", 'mae_yesterday = (s - s.shift(1)).abs().mean()\nmae_last_week = ___\n\n'
                 'print(f"same as yesterday      : {mae_yesterday:.3f} Gbps")\ncheck("B7", mae_last_week)',
         'mae_yesterday = (s - s.shift(1)).abs().mean()\nmae_last_week = (s - s.shift(7)).abs().mean()\n\n'
         'print(f"same as yesterday      : {mae_yesterday:.3f} Gbps")\ncheck("B7", mae_last_week)'),
        ("md", """> 💡 This is the **seasonal naive** forecast you'll meet again in Week 5. Every fancy model must beat it.
>
> ⚠️ **Memory also means danger:** because neighbouring days (and same weekdays) are near-copies, **never split time data at random** into train and test. The test answers would leak into training. Like WAEC expo. 📝"""),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Correlation is not cause (15 min) 🕵🏾

### C1 ▶️ A made-up story
At one Lagos market, **suya sales** and **generator sales** both rise all year toward December. STEP 0 already created the data for you with `make_sales()`. **It's made up, an illustration.**"""),
        ("code", 'suya, gens = make_sales()\n\n'
                 'ax = (suya / suya.iloc[:4].mean() * 100).plot(label="suya", lw=2)\n'
                 '(gens / gens.iloc[:4].mean() * 100).plot(ax=ax, label="generators", lw=2)\n'
                 'plt.title("Made-up: both rise toward December (first month = 100)")\nplt.legend()\nplt.show()'),
        ("md", """### C2 ✍️ Correlate the levels
`a.corr(b)` gives the correlation between two series. What do you get for suya vs generators?"""),
        ("task", 'raw_corr = ___\nprint("levels:", raw_corr)\n\ncheck("C2", raw_corr)', 'raw_corr = suya.corr(gens)\nprint("levels:", raw_corr)\n\ncheck("C2", raw_corr)'),
        ("md", """### C3 ✍️ Correlate the CHANGES
If two things truly move together, their **week-to-week changes** should match too. `.diff()` turns levels into changes. Try it."""),
        ("task", 'diff_corr = ___\nprint("changes:", diff_corr)\n\ncheck("C3", diff_corr)', 'diff_corr = suya.diff().corr(gens.diff())\nprint("changes:", diff_corr)\n\ncheck("C3", diff_corr)'),
        ("md", """### C4 ✍️ The real satellite case
Amplifier (TWTA) temperature vs RF drive level. Both drift up over two years. Do the same two tests.
(We use the **Week 3** version of this file: `week="week-03"`.)"""),
        ("code", 'twta = pd.read_csv(data_path("twta_thermal_daily", week="week-03"), parse_dates=["date"], index_col="date").asfreq("D")\n'
                 'twta.resample("MS").mean().plot(subplots=True, figsize=(11, 4), title="Monthly averages")\nplt.show()'),
        ("task", 'twta_raw = ___\ntwta_diff = ___\nprint("levels:", twta_raw, "  changes:", twta_diff)\n\ncheck("C4", (twta_raw, twta_diff))',
         'twta_raw = twta["twta_temp_c"].corr(twta["rf_drive_pct"])\ntwta_diff = twta["twta_temp_c"].diff().corr(twta["rf_drive_pct"].diff())\n'
         'print("levels:", twta_raw, "  changes:", twta_diff)\n\ncheck("C4", (twta_raw, twta_diff))'),
        ("md", """> 💡 **Two lessons:**
> - Suya: the correlation **collapses** after `.diff()`, so it was only shared trend.
> - TWTA: it **drops but survives**. Part was shared trend, part is real physics (more drive → more heat).
>
> And even a real link has a **direction**: rain makes the ground station turn up its uplink power, but turning up the power doesn't make it rain. 😄"""),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task (bonus): find the YEARLY season
Ka-band availability dips every rainy season. Use the correlogram numbers (not the picture) to find the lag, between 300 and 400 days, where the memory peaks.
`acf(series, nlags=400)` returns the 401 bar heights as an array. `acf_vals[300:]` keeps lags 300 to 400, and `.argmax()` gives the position of the biggest one **inside that slice**."""),
        ("task", 'from statsmodels.tsa.stattools import acf\n\n'
                 'ka = pd.read_csv(data_path("ka_band_availability_daily"), parse_dates=["timestamp"], index_col="timestamp").asfreq("D")\n'
                 'acf_vals = acf(ka["availability_pct"].dropna(), nlags=400)\n\n'
                 'peak_lag = ___\ncheck("BONUS", peak_lag)',
         'from statsmodels.tsa.stattools import acf\n\n'
         'ka = pd.read_csv(data_path("ka_band_availability_daily"), parse_dates=["timestamp"], index_col="timestamp").asfreq("D")\n'
         'acf_vals = acf(ka["availability_pct"].dropna(), nlags=400)\n\n'
         'peak_lag = int(acf_vals[300:].argmax()) + 300\ncheck("BONUS", peak_lag)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- A **lag** is the series shifted back in time: `s.shift(1)` = yesterday, `s.shift(7)` = same weekday last week.
- **Autocorrelation** (`s.autocorr(lag=k)`) measures how much a series matches its own lag-k copy, from −1 to +1.
- A **correlogram** (`plot_acf`) shows every lag. Lag 0 is always 1 (ignore it). **Spikes = season** (the gap is the period), **slow decay = trend**, **inside the band = noise**.
- **Find the period from the data**: 7 for throughput and tickets, 24 for hourly battery charge, about 365 for Ka-band.
- **Memory is a free forecast** ("same weekday last week"), and a reason **never to split time data at random**.
- **Two trending series?** Compare `.diff()` before you believe the correlation. Correlation ≠ cause, and direction matters.

**Next time:** *Lab Day + Quiz 1*, and you pick your final project. 🎯

<sub>Data: synthetic teaching datasets from the original Week 3 code book (`Time-series/week-03`). The suya/generator data is made up for illustration.</sub>"""),
    ]
