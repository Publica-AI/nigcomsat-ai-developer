"""Week 1 · Day 2: Charts That Don't Lie."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import BRAND as B, ORIGINALS
from svgcharts import bars_svg, line_svg, lines_svg
from webdeck import logos_title_block

CODE = "W1D2"
TITLE = "Charts That Don't Lie"

D3 = ORIGINALS / "week-03" / "data"
ZONES = ["North West", "North East", "North Central", "South West", "South East", "South South"]
GREY = "#6F8399"


def _data():
    rf = pd.read_csv(D3 / "rf_link_quality_hourly.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    vsat = pd.read_csv(D3 / "vsat_uptime_by_region_weekly.csv", parse_dates=["week_start"])
    wide = vsat.pivot(index="week_start", columns="region", values="uptime_pct")[ZONES]
    tk = pd.read_csv(D3 / "noc_tickets_daily.csv", parse_dates=["date"], index_col="date")
    return rf, vsat, wide, tk


def _facts():
    rf, vsat, wide, tk = _data()
    m = rf["link_margin_db"]
    daily = m.resample("D").agg(["mean", "min"])
    idx = wide / wide.iloc[0] * 100
    out = m < 0
    return {
        "hours": len(rf), "outage_hours": int(out.sum()), "rain_hours": int((rf["rain_rate_mmhr"] > 0).sum()),
        "days": len(daily), "outage_days": int((daily["min"] < 0).sum()),
        "lowest_mean": round(float(daily["mean"].min()), 2), "lowest_min": round(float(daily["min"].min()), 2),
        "hour_avail": float((m >= 0).mean() * 100),
        "corr_rain_uplink": round(float(rf["rain_rate_mmhr"].corr(rf["uplink_power_dbm"])), 2),
        "uplink_wet": round(float(rf.loc[rf["rain_rate_mmhr"] > 0, "uplink_power_dbm"].mean()), 1),
        "uplink_dry": round(float(rf.loc[rf["rain_rate_mmhr"] == 0, "uplink_power_dbm"].mean()), 1),
        "lightest_outage_rain": round(float(rf.loc[out, "rain_rate_mmhr"].min()), 1),
        "lowest_zone": wide.mean().idxmin(), "lowest_zone_mean": round(float(wide.mean().min()), 2),
        "worst_week_val": round(float(wide.min().min()), 2), "worst_week_zone": wide.min().idxmin(),
        "fell_furthest": idx.min().idxmin(), "fell_furthest_idx": round(float(idx.min().min()), 1),
        "idx_min": idx.min().round(1).to_dict(), "means": wide.mean().round(2).to_dict(),
        "rows": len(vsat),
    }


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


def _small_multiples(wide, highlight):
    """3x2 grid of mini charts on ONE shared y-axis."""
    lo, hi = 96.4, 99.8
    n = len(wide)
    cells = []
    for k, z in enumerate(ZONES):
        col = B["gold"] if z == highlight else B["blue_d"]
        svg = line_svg(wide[z].values, w=440, h=190, ymin=lo, ymax=hi, area=True, stroke=3, color=col,
                       yticks=[(97, "97"), (98, "98"), (99, "99")], xlabels=[(0, "Jan"), (n - 1, "Dec")],
                       dur="1.8s", delay=f"{.2 + k * .15:.2f}s")
        svg = svg.replace('width="440" height="190"', 'width="100%"')
        cells.append(f'<div class="card anim" style="--d:{.1 + k * .12:.2f}s;padding:12px 14px 4px">'
                     f'<div style="display:flex;justify-content:space-between;font-size:22px;font-weight:800">'
                     f'<span style="color:{col}">{z}</span><span class="muted" style="font-weight:600">avg {wide[z].mean():.1f}%</span></div>'
                     f'<div style="width:100%;overflow:hidden">{svg}</div></div>')
    return f'<div class="grid3" style="gap:18px">{"".join(cells)}</div>'


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    rf, vsat, wide, tk = _data()
    f = _facts()
    m = rf["link_margin_db"]
    n = len(m)
    daily = m.resample("D").agg(["mean", "min"])
    nd = len(daily)

    def hi_of(ts):
        return int((pd.Timestamp(ts) - m.index[0]) / pd.Timedelta("1h"))

    week_lab = [(0, "1 Aug"), (hi_of("2025-08-08"), "8 Aug"), (hi_of("2025-08-15"), "15 Aug"),
                (hi_of("2025-08-22"), "22 Aug"), (n - 1, "31 Aug")]
    hourly = line_svg(m.values, w=1420, h=430, ymin=-5, ymax=7, area=False, stroke=2.5,
                      yticks=[(-4, "-4"), (0, "0"), (4, "+4")], xlabels=week_lab,
                      hline=(0, "0 dB = link down", B["bad"]), dur="3.2s")
    d_lab = [(0, "1 Aug"), (nd - 1, "31 Aug")]
    mean_svg = line_svg(daily["mean"].values, w=680, h=330, ymin=-5, ymax=7, area=False, stroke=4, color=B["teal_d"],
                        yticks=[(-4, "-4"), (0, "0"), (4, "+4")], xlabels=d_lab, hline=(0, "0 dB", B["bad"]), dur="2s")
    min_svg = line_svg(daily["min"].values, w=680, h=330, ymin=-5, ymax=7, area=False, stroke=4, color=B["gold"],
                       yticks=[(-4, "-4"), (0, "0"), (4, "+4")], xlabels=d_lab, hline=(0, "0 dB", B["bad"]), dur="2s")
    rain_svg = line_svg(rf["rain_rate_mmhr"].values, w=1420, h=190, ymin=0, ymax=60, area=True, stroke=2, color=B["teal_d"],
                        yticks=[(0, "0"), (50, "50")], xlabels=[], dur="2.6s")
    up_svg = line_svg(rf["uplink_power_dbm"].values, w=1420, h=200, ymin=40.5, ymax=48, area=False, stroke=2, color=B["blue_d"],
                      yticks=[(41, "41"), (47, "47")], xlabels=week_lab, dur="2.6s", delay=".9s")

    nw = len(wide)
    spaghetti = lines_svg([dict(values=wide[z].values, color=c, stroke=2.5, delay=f"{.2 + k * .1:.1f}s")
                           for k, (z, c) in enumerate(zip(ZONES, ["#3B8BE0", "#2F7BCB", "#4C9BEA", "#5AA9F0", "#2A6FB8", "#6BB3F2"]))],
                          w=1420, h=440, ymin=96.4, ymax=99.8, labels_right=False,
                          yticks=[(97, "97%"), (98, "98%"), (99, "99%")], xlabels=[(0, "Jan"), (nw - 1, "Dec")])
    idx = wide / wide.iloc[0] * 100
    south = {"South East": B["gold"], "South West": B["teal_d"], "South South": B["blue_d"]}
    idx_svg = lines_svg([dict(values=idx[z].values, color=south.get(z, GREY), stroke=4 if z in south else 2,
                              delay=f"{.3 + k * .15:.2f}s") for k, z in enumerate(ZONES)],
                        w=1420, h=400, ymin=97.9, ymax=100.8, labels_right=False, hline=(100, "", "#9DB0C6"),
                        yticks=[(98, "98"), (99, "99"), (100, "100")], xlabels=[(0, "week 1"), (nw - 1, "week 52")],
                        markers=[(int(np.argmin(idx["South East"].values)), float(idx["South East"].min()),
                                  f"South East: {idx['South East'].min():.1f}", B["gold"])])

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    wd = tk.groupby(tk.index.dayofweek)["tickets_raised"].mean().values
    bars_bad = bars_svg(days, wd, w=640, h=420, ymin=3, ymax=7.6, color=B["bad"], fmt="{:.1f}")
    bars_good = bars_svg(days, wd, w=640, h=420, ymin=0, ymax=8.2, color=B["teal_d"], fmt="{:.1f}")
    ss = wide["South South"].values
    flat_svg = line_svg(ss, w=640, h=400, ymin=0, ymax=100, area=False, stroke=4, color=GREY,
                        yticks=[(0, "0"), (50, "50"), (100, "100")], xlabels=[], dur="1.5s")
    zoom_svg = line_svg(ss, w=640, h=400, ymin=96, ymax=99, area=False, stroke=4, color=B["blue_d"],
                        yticks=[(96, "96"), (97, "97"), (98, "98"), (99, "99")], xlabels=[], dur="1.5s")

    # long -> wide visual
    long_rows = "".join(f'<tr><td>{r.week_start:%Y-%m-%d}</td><td>{r.region}</td><td>{r.uptime_pct:.2f}</td></tr>'
                        for r in vsat.head(6).itertuples())
    wide_head = "".join(f"<th>{z.replace('North ', 'N. ').replace('South ', 'S. ')}</th>" for z in ZONES)
    wide_rows = "".join("<tr><td>" + f"{ix:%Y-%m-%d}" + "</td>" + "".join(f"<td>{wide.loc[ix, z]:.2f}</td>" for z in ZONES) + "</tr>"
                        for ix in wide.index[:3])
    tbl = ("border-collapse:collapse;font-family:var(--mono);font-size:20px;width:100%")
    tbl_css = ('<style>.tb td,.tb th{border:1px solid #24384F;padding:8px 10px;text-align:left}'
               '.tb th{background:#07101A;color:#9EEBE0}</style>')

    tv = """
<svg viewBox="0 0 520 420" width="520" height="420">
  <rect x="20" y="20" width="480" height="300" rx="26" fill="#07101A" stroke="#3B8BE0" stroke-width="6"/>
  <g class="pulse"><text x="260" y="160" text-anchor="middle" font-size="46" font-weight="800" fill="#EAF2FB">No Signal</text>
  <text x="260" y="210" text-anchor="middle" font-size="24" fill="#9DB0C6">E48-32 · please wait…</text></g>
  <rect x="200" y="330" width="120" height="16" rx="6" fill="#24384F"/><rect x="150" y="346" width="220" height="12" rx="6" fill="#24384F"/>
  <g style="stroke:#7FB8FF;stroke-width:3;stroke-linecap:round;opacity:.75">
""" + "".join(f'<line x1="{x}" y1="0" x2="{x - 14}" y2="40" class="rain" style="animation-delay:{(x * 37 % 100) / 100:.2f}s"/>'
              for x in range(30, 520, 38)) + """
  </g></svg>
<style>@keyframes w1d2rain{0%{transform:translateY(-60px);opacity:0}15%{opacity:1}100%{transform:translateY(430px);opacity:0}}
.rain{animation:w1d2rain 1.1s linear infinite}body.print .rain,body.shot .rain{display:none}</style>"""

    slides = [
        # 1 title
        S(f"""
<div style="position:absolute;right:40px;top:150px" class="anim a-pop" >{tv}</div>
<div style="max-width:900px;margin-top:40px">
  <div class="kicker anim">Week 1 · Day 2</div>
  <h1 class="anim" style="--d:.2s">Charts That<br><span class="hl">Don't Lie</span> 📊</h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">The same data can tell the truth or tell a lie.<br>Today you learn to draw the truth.</p>
  <div class="anim" style="--d:.8s;margin-top:44px;display:flex">{logos_title_block()}</div>
</div>""",
          "Welcome back. Quick 5-minute warm-up: ask 2 people what a time series is (order matters) and why we use .asfreq() "
          "(missing periods show up). Today: the same numbers can be charted honestly or dishonestly."),
        # 2 mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Three moves</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:380px;padding:46px 34px"><div class="icon">🕵🏾</div><h3>Catch the lie</h3><p class="small">the average hid every outage</p></div>
  <div class="arrow anim a-fade" style="--d:.6s"></div>
  <div class="box on anim a-pop" style="--d:.8s;min-width:380px;padding:46px 34px"><div class="icon">🗺️</div><h3>Compare 6 zones</h3><p class="small">small multiples + index to week 1</p></div>
  <div class="arrow anim a-fade" style="--d:1.1s"></div>
  <div class="box on anim a-pop" style="--d:1.3s;min-width:380px;padding:46px 34px"><div class="icon">🗣️</div><h3>Tell the story</h3><p class="small">a title + 4 sentences your boss reads</p></div>
</div>
<div class="row anim" style="--d:1.7s;margin-top:70px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up</span>
</div>""", "Three moves. The exercise follows exactly this order."),
        # 3 hook
        S("""
<div class="kicker anim">Be honest</div>
<h2 class="anim" style="--d:.1s">Who has seen this during heavy rain? 📺🌧️</h2>
<div class="flow" style="margin-top:50px;justify-content:center">
  <div class="box anim a-left" style="--d:.3s;min-width:300px"><div class="icon floaty">🛰️</div><h3>Satellite</h3><p class="small">sends the signal down</p></div>
  <div class="arrow anim a-fade" style="--d:.6s;width:120px"></div>
  <div class="box on anim a-pop" style="--d:.8s;min-width:340px;border-color:#E5484D"><div class="icon">⛈️</div><h3>Heavy rain</h3><p class="small">soaks up the signal</p></div>
  <div class="arrow anim a-fade" style="--d:1.1s;width:120px"></div>
  <div class="box anim a-right" style="--d:1.3s;min-width:300px"><div class="icon">📡</div><h3>Your dish</h3><p class="small">too weak = “No Signal”</p></div>
</div>
<div class="card step glow" data-step="1" style="margin-top:46px;text-align:center"><p>That's <b class="hl">rain fade</b>. Ka-band suffers it most. Today's question:<br><b>did our Ka-band link actually go down in August, and would our charts show it?</b></p></div>""",
          "Everybody has seen DStv or GOtv drop during a heavy downpour. Same physics on our Ka-band link. Today's whole lesson is about whether our charts would SHOW those drops or hide them."),
        # 4 section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">The average lies 🤥</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">One month of hourly Ka-band link data. One big trap.</p>""", "Section break.", cls="center"),
        # 5 meet the data
        S(f"""
<div class="kicker anim">Today's first dataset · rf_link_quality_hourly.csv</div>
<h2 class="anim" style="--d:.1s">August, hour by hour: {f['hours']} rows</h2>
<div class="grid4" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">🌧️</div><h3 style="font-size:27px">rain_rate_mmhr</h3><p class="muted">rain at the earth station</p></div>
  <div class="card anim a-pop" style="--d:.5s"><div class="icon">📶</div><h3 style="font-size:27px">cn_ratio_db</h3><p class="muted">signal quality (carrier-to-noise)</p></div>
  <div class="card anim a-pop" style="--d:.7s"><div class="icon">🔊</div><h3 style="font-size:27px">uplink_power_dbm</h3><p class="muted">how loud we transmit</p></div>
  <div class="card anim a-pop glow" style="--d:.9s"><div class="icon">⛽</div><h3 style="font-size:27px">link_margin_db</h3><p class="muted">signal left above the minimum</p></div>
</div>
<div class="card anim" style="--d:1.3s;margin-top:30px;display:flex;gap:30px;align-items:center">
  <div class="big-emoji" style="font-size:90px">⛽</div>
  <p><b>Link margin is like fuel above the reserve line.</b> Positive = you're fine. <b class="bad">Below 0 dB = the link is DOWN.</b></p></div>""",
          "Only one column really matters today: link_margin_db. Think of it as fuel above the reserve line. Below zero, the link is down."),
        # 6 hourly chart
        S(f"""
<div class="kicker anim">Every hour of August</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Link margin dived below 0 dB <span class="bad">{f['outage_hours']} times</span></h2>
<div class="card anim" style="--d:.2s;padding:16px 20px">{hourly}</div>
<div class="row anim" style="--d:2.8s;margin-top:20px;gap:14px">
  <span class="pill bad"><span class="count" data-to="{f['outage_hours']}" data-d="2.9">0</span> outage hours</span>
  <span class="pill teal">{f['rain_hours']} hours had rain</span>
  <span class="pill gold">every outage came during heavy rain</span>
  <span class="pill bad">worst hour: {f['lowest_min']} dB</span>
</div>""",
          f"The hourly truth: {f['outage_hours']} hours below 0 dB, all of them during heavy storms. Worst hour {f['lowest_min']} dB on 26 August. Now watch what happens when we summarise by day."),
        # 7 mean vs min
        S(f"""
<div class="kicker anim">Same data. Two daily summaries.</div>
<h2 class="anim" style="--d:.1s;font-size:54px">One says “all good”. One tells the truth.</h2>
<div class="grid2">
  <div class="card anim" style="--d:.3s;padding:20px 22px"><h3 class="teal">Daily AVERAGE</h3>{mean_svg}
    <p style="font-size:24px">Never below <b>{f['lowest_mean']} dB</b>. Zero outages. 😎</p></div>
  <div class="card step" data-step="1" style="padding:20px 22px;border-color:#F5B83D"><h3 class="hl">Daily MINIMUM</h3>{min_svg}
    <p style="font-size:24px"><b class="bad">{f['outage_days']} of {f['days']} days</b> had an outage. 😱</p></div>
</div>""",
          f"The killer slide. The daily mean never drops below {f['lowest_mean']} dB, so a report built on it says no outages. "
          f"The daily minimum shows {f['outage_days']} of {f['days']} days had at least one outage hour. This is quiz question 2."),
        # 8 rule
        S("""
<div class="kicker anim">The rule</div>
<h2 class="anim" style="--d:.1s">“Did we breach?” → plot the <span class="hl">worst moment</span></h2>
<div class="grid2" style="margin-top:30px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">📉</div><h3>Daily minimum</h3><p class="muted">SLA, outages, “did it ever go down?”</p></div>
  <div class="card anim a-right" style="--d:.5s"><div class="icon">⚖️</div><h3>Daily average</h3><p class="muted">typical level, long-term trend</p></div>
</div>
<div class="card step glow" data-step="1" style="margin-top:34px;display:flex;gap:28px;align-items:center"><div class="big-emoji" style="font-size:90px">🌉</div>
  <p>“Average traffic on Third Mainland Bridge was fine today.”<br><b>Tell that to the man who sat there for 3 hours.</b> 😤</p></div>""",
          "Pick the summary that matches the question. Breach questions need the minimum (or maximum for things like temperature). Averages smooth away exactly the moments you care about."),
        # 9 response not cause + one axis
        S(f"""
<div class="kicker anim">Two measures? Two charts, one time axis</div>
<h2 class="anim" style="--d:.1s;font-size:52px">Uplink power rises <i>because</i> it rains</h2>
<div class="card anim" style="--d:.2s;padding:10px 20px 0"><p class="small" style="color:#9EEBE0">🌧️ rain (mm/hr)</p>{rain_svg}</div>
<div class="card anim" style="--d:.5s;padding:10px 20px 0;margin-top:14px"><p class="small" style="color:#BFDcff">🔊 uplink power (dBm)</p>{up_svg}</div>
<p class="step" data-step="1" style="margin-top:12px;font-size:25px">Correlation <b class="hl">{f['corr_rain_uplink']}</b>: the station turns up the volume to fight the rain. A <b>response</b>, not a second problem. Two units → <b>two stacked charts</b>, never two y-axes.</p>""",
          f"Correlation between rain and uplink power is {f['corr_rain_uplink']}: uplink power control reacts to rain. "
          f"Average uplink {f['uplink_dry']} dBm when dry vs {f['uplink_wet']} dBm in rain. Also the layout lesson: different units go in separate stacked charts, not a dual axis."),
        # 10 section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Six zones, one picture 🗺️</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">VSAT uptime for Nigeria's six geopolitical zones, every week.</p>""", "Section break.", cls="center"),
        # 11 long vs wide
        S(f"""{tbl_css}
<div class="kicker anim">vsat_uptime_by_region_weekly.csv · {f['rows']} rows</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Long format → <span class="teal">pivot</span> → wide format</h2>
<div class="row" style="gap:30px;align-items:flex-start">
  <div class="card anim a-left" style="--d:.3s;flex:.8;padding:20px"><p class="small">LONG: one row per zone per week</p>
    <table class="tb" style="{tbl}"><tr><th>week_start</th><th>region</th><th>uptime</th></tr>{long_rows}</table></div>
  <div class="card step glow" data-step="1" style="flex:1.2;padding:20px"><p class="small">WIDE: one row per week, one column per zone</p>
    <table class="tb" style="{tbl};font-size:17px"><tr><th>week</th>{wide_head}</tr>{wide_rows}</table></div>
</div>
<pre class="code anim" style="--d:.6s;margin-top:22px;font-size:24px">wide = vsat.pivot(index="week_start", columns="region", values="uptime_pct")</pre>""",
          "Long format is how databases export. Charts want wide format: one column per line. pivot does the reshaping."),
        # 12 spaghetti
        S(f"""
<div class="kicker anim">Option A</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Six lines on one chart. Find South South. 🍝</h2>
<div class="card anim" style="--d:.2s;padding:16px 20px">{spaghetti}</div>
<p class="anim" style="--d:2.4s;margin-top:18px;text-align:center">Spaghetti! Colours fight, lines cross, nobody can read it. 😵‍💫</p>""",
          "Let the room struggle for 10 seconds. Nobody can find South South. That's the problem with spaghetti charts."),
        # 13 small multiples
        S(f"""
<div class="kicker anim">Option B · small multiples</div>
<h2 class="anim" style="--d:.1s;font-size:50px">One mini chart per zone, <span class="hl">same y-axis</span></h2>
{_small_multiples(wide, f['lowest_zone'])}
<p class="anim" style="--d:1.6s;margin-top:12px;font-size:24px">Instantly clear: <b class="hl">{f['lowest_zone']}</b> sits lowest all year (avg {f['lowest_zone_mean']}%), and the 3 southern zones dip harder in the rainy season.</p>""",
          f"Small multiples on a SHARED y-axis (quiz question 3). Shared is essential: if each panel had its own axis, every zone would look equally bad. {f['lowest_zone']} averages {f['lowest_zone_mean']}%."),
        # 14 index
        S(f"""
<div class="kicker anim">A different question</div>
<h2 class="anim" style="--d:.1s;font-size:50px">Who fell furthest from <span class="hl">their own</span> normal?</h2>
<pre class="code anim" style="--d:.2s;font-size:24px;padding:16px 24px">indexed = wide / wide.iloc[0] * 100      # every zone starts at 100</pre>
<div class="card anim" style="--d:.4s;padding:14px 20px;margin-top:14px">{idx_svg}</div>
<div class="row anim" style="--d:2.4s;margin-top:12px;gap:12px"><span class="pill gold">South East</span><span class="pill teal">South West</span><span class="pill">South South</span><span class="pill" style="background:rgba(111,131,153,.25);color:#C9D6E5">the 3 northern zones</span></div>""",
          f"Indexing divides each zone by its own week-1 value. Now the question is 'how far did you fall from where you started?'. "
          f"South East fell furthest, to {f['idx_min']['South East']} (South West {f['idx_min']['South West']}, South South {f['idx_min']['South South']}). Quiz question 4."),
        # 15 two questions
        S(f"""
<div class="kicker anim">Two questions, two different answers</div>
<h2 class="anim" style="--d:.1s">The chart you draw depends on the question</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🏚️</div><h3>“Who is worst?”</h3><p class="muted">raw uptime, small multiples</p>
    <p style="margin-top:14px"><b class="hl">{f['lowest_zone']}</b>: lowest average ({f['lowest_zone_mean']}%) and the worst single week ({f['worst_week_val']}%).</p></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">📉</div><h3>“Who dropped most from normal?”</h3><p class="muted">indexed to week 1</p>
    <p style="margin-top:14px"><b class="hl">{f['fell_furthest']}</b>: fell to {f['fell_furthest_idx']} (week 1 = 100), just ahead of South West.</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:30px;text-align:center">Like comparing students: <b>lowest score</b> is not the same as <b>biggest drop since last term</b>. 📚</p>""",
          "Both answers are correct; they answer different questions. Ask participants which question their unit head would ask."),
        # 16 section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">Honest-chart rules ✅</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Five habits that make your charts trustworthy.</p>""", "Section break.", cls="center"),
        # 17 axes
        S(f"""
<div class="kicker anim">Where should the y-axis start?</div>
<h2 class="anim" style="--d:.1s;font-size:52px">It depends on <span class="hl">what you measure</span></h2>
<div class="grid2" style="margin-top:6px">
  <div class="card anim a-left" style="--d:.2s;padding:18px 20px"><h3>📈 Percentages near the top</h3><p class="small">South South uptime</p>
    <div class="row" style="gap:10px"><div style="flex:1"><p class="small">0–100: flat, useless</p>{flat_svg.replace('width="640" height="400"', 'width="100%"')}</div>
    <div style="flex:1"><p class="small hl">96–99: story visible ✅</p>{zoom_svg.replace('width="640" height="400"', 'width="100%"')}</div></div>
    <p style="font-size:22px;margin-top:8px">Zoom in, and <b>write the range on the chart</b>.</p></div>
  <div class="card anim a-right" style="--d:.4s;padding:18px 20px"><h3>🎫 Counts (tickets)</h3><p class="small">average NOC tickets per weekday</p>
    <div class="row" style="gap:10px"><div style="flex:1"><p class="small bad">axis from 3 ❌ Sunday looks dead</p>{bars_bad.replace('width="640" height="420"', 'width="100%"')}</div>
    <div style="flex:1"><p class="small teal">axis from 0 ✅ honest</p>{bars_good.replace('width="640" height="420"', 'width="100%"')}</div></div>
    <p style="font-size:22px;margin-top:8px">Things you can add up: <b>start at zero</b>.</p></div>
</div>""",
          "Quiz question 1. Tight axes are right for bounded measures that live near the top (availability, uptime), as long as the range is stated. "
          "Counts start at zero, otherwise small differences look huge."),
        # 18 five rules
        S("""
<div class="kicker anim">Before you share any chart</div>
<h2 class="anim" style="--d:.1s">The 5 honest-chart rules</h2>
<div class="grid5" style="margin-top:40px">
  <div class="card anim a-pop" style="--d:.3s;padding:30px 24px"><div class="icon">🚧</div><h3>Threshold line</h3><p class="small">draw the limit (0 dB, SLA %)</p></div>
  <div class="card anim a-pop" style="--d:.5s;padding:30px 24px"><div class="icon">📰</div><h3>Title = finding</h3><p class="small">say what it SHOWS</p></div>
  <div class="card anim a-pop" style="--d:.7s;padding:30px 24px"><div class="icon">📏</div><h3>Sensible axis</h3><p class="small">and say the range</p></div>
  <div class="card anim a-pop" style="--d:.9s;padding:30px 24px"><div class="icon">☝🏾</div><h3>One y-axis</h3><p class="small">two units? two charts</p></div>
  <div class="card anim a-pop" style="--d:1.1s;padding:30px 24px"><div class="icon">🏷️</div><h3>Units</h3><p class="small">dB, %, tickets…</p></div>
</div>
<p class="anim" style="--d:1.5s;margin-top:44px;text-align:center">Think of your chart as <b>evidence in court</b>. The other lawyer will check all five. ⚖️</p>""",
          "These five rules are in the rule book and in today's exercise."),
        # 19 title upgrade
        S(f"""
<div class="kicker anim">Upgrade your title</div>
<h2 class="anim" style="--d:.1s">A title should state the finding</h2>
<div class="card anim" style="--d:.3s;margin-top:30px;border-color:#E5484D"><p class="small bad">❌ Names the data</p><h3 style="font-size:44px;margin-top:8px">Link margin, August</h3></div>
<div class="card step glow" data-step="1" style="margin-top:26px;border-color:#1E9E5A"><p class="small good">✅ States the finding (with a number)</p>
  <h3 style="font-size:44px;margin-top:8px">Ka-band link went down on {f['outage_days']} of {f['days']} August days, all during heavy rain</h3></div>""",
          "Quiz question 5 (True). A busy unit head reads the title and nothing else. Make the title do the work."),
        # 20 four sentences
        S(f"""
<div class="kicker anim">The 4-sentence finding</div>
<h2 class="anim" style="--d:.1s;font-size:54px">How to report it to your unit head</h2>
<div class="col" style="gap:14px;margin-top:6px">
  <div class="card anim a-left" style="--d:.2s;display:flex;gap:22px;align-items:center;padding:18px 26px"><span class="num">1</span><p style="font-size:25px"><b class="blue">Situation:</b> The Ka-band Nigeria beam carries customer traffic through the rainy season.</p></div>
  <div class="card anim a-left" style="--d:.45s;display:flex;gap:22px;align-items:center;padding:18px 26px"><span class="num">2</span><p style="font-size:25px"><b class="blue">Observation:</b> In August the link was down for {f['outage_hours']} hours across {f['outage_days']} days, yet the daily average never fell below {f['lowest_mean']} dB.</p></div>
  <div class="card anim a-left" style="--d:.7s;display:flex;gap:22px;align-items:center;padding:18px 26px"><span class="num">3</span><p style="font-size:25px"><b class="blue">Implication:</b> Reports built on daily averages would show zero outages and miss every SLA breach.</p></div>
  <div class="card anim a-left glow" style="--d:.95s;display:flex;gap:22px;align-items:center;padding:18px 26px"><span class="num" style="background:#C98205">4</span><p style="font-size:25px"><b class="hl">Recommendation:</b> Report availability from hourly minimums, with the 0 dB line on every chart.</p></div>
</div>""",
          "Situation, Observation, Implication, Recommendation. The recommendation always comes LAST (quiz question 6). Participants write their own in the exercise."),
        # 21 your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Open the W1D2 exercise 🧑🏾‍💻</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p><b class="hl">Open in Colab</b> → <b>Save a copy in Drive</b> 💾</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">2</span><p>Run <b>STEP 0</b>, then top to bottom</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">3</span><p>Part A: catch the average in its lie</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">4</span><p>Part B: six zones, one honest picture</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">📊</div>
  <h3 style="margin-top:16px">14 checks to pass</h3>
  <p class="muted">Part A: the average lies<br>Part B: six zones<br>🌶️ Bonus: what rain kills the link?</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on time. Most common problems: forgetting the quotes in pivot arguments, and typing 'H' instead of 'h' for hourly."),
        # 22 recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">📉</span><p><b>Breach questions → plot the minimum.</b> The average hid 12 outage hours.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🗺️</span><p><b>Many groups → small multiples</b> on one shared axis. <b>Change from normal → index</b> to week 1.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🗣️</span><p><b>Tell it:</b> a title that states the finding + Situation → Observation → Implication → <b class="hl">Recommendation</b>.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:30px">Next time 👉 <b class="hl">Calm Down the Noise</b>: why even faults rest on Sunday 😴</p>""",
          "Recap. Ask: which daily summary for an SLA question? What does indexing to week 1 tell you? What comes last in the 4 sentences?"),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    rf, vsat, wide, tk = _data()
    f = _facts()
    m = rf["link_margin_db"]
    daily = m.resample("D").agg(["mean", "min"])
    dlab = [f"{d.day} Aug" if d.day in (1, 8, 15, 22, 29) else "" for d in daily.index]
    idx = wide / wide.iloc[0] * 100
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "📺", "kicker": "Week 1 · Day 2", "title": "Charts That Don't Lie",
             "sub": "The same data can tell the truth or tell a lie. Learn to draw the truth.",
             "notes": "Warm-up: what is a time series? Why .asfreq()?"},
            {"type": "flow", "title": "Today's mission: three moves", "steps": [
                ["🕵🏾", "Catch the lie", "the average hid every outage"],
                ["🗺️", "Compare 6 zones", "small multiples + index"],
                ["🗣️", "Tell the story", "a title + 4 sentences"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up", "notes": "Three moves."},
            {"type": "statement", "title": "“No Signal” during heavy rain", "icon": "⛈️",
             "big": "Heavy rain soaks up the satellite signal: that's rain fade",
             "sub": "Ka-band suffers it most. Did our link go down in August, and would our charts show it?",
             "notes": "Everybody has seen DStv drop in a downpour."},
            {"type": "section", "kicker": "Part 1", "title": "The average lies", "sub": "One month of hourly Ka-band link data",
             "notes": "Section break."},
            {"type": "cards4", "title": f"rf_link_quality_hourly: {f['hours']} hours of August", "cards": [
                ["🌧️", "Rain", "rain_rate_mmhr: rain at the earth station"],
                ["📶", "Signal quality", "cn_ratio_db: carrier-to-noise"],
                ["🔊", "Uplink power", "uplink_power_dbm: how loud we transmit"],
                ["⛽", "Link margin", "link_margin_db: below 0 dB = link DOWN"]],
             "notes": "Link margin is like fuel above the reserve line."},
            {"type": "twochart", "title": "Same data, two daily summaries",
             "left": {"label": f"Daily AVERAGE: never below {f['lowest_mean']} dB", "labels": dlab, "values": daily["mean"].round(2).tolist(),
                      "ymin": -5, "ymax": 7, "freq": 1, "color": "008C7E", "good": True},
             "right": {"label": f"Daily MINIMUM: {f['outage_days']} of {f['days']} days below 0 dB", "labels": dlab, "values": daily["min"].round(2).tolist(),
                       "ymin": -5, "ymax": 7, "freq": 1, "color": "C77700"},
             "notes": "The average says zero outages. The minimum shows the truth."},
            {"type": "compare", "title": "“Did we breach?” → plot the worst moment",
             "left": ["📉", "Daily minimum", "SLA, outages: “did it ever go down?”"],
             "right": ["⚖️", "Daily average", "typical level, long-term trend. It hides short outages"],
             "notes": "Third Mainland Bridge: average traffic was fine, tell that to the man stuck for 3 hours."},
            {"type": "statement", "title": "Uplink power rises because it rains", "icon": "🔊",
             "big": f"Rain vs uplink power: correlation {f['corr_rain_uplink']}",
             "sub": f"Uplink averages {f['uplink_dry']} dBm when dry, {f['uplink_wet']} dBm in rain. It's a response, not a second problem. Two units? Two stacked charts, never two y-axes.",
             "notes": "Uplink power control reacts to rain."},
            {"type": "section", "kicker": "Part 2", "title": "Six zones, one picture", "sub": "VSAT uptime by geopolitical zone, weekly",
             "notes": "Section break."},
            {"type": "code", "title": "Long format → pivot → wide format",
             "code": '# long: 312 rows (52 weeks x 6 zones)\nvsat = pd.read_csv(data_path("vsat_uptime_by_region_weekly"),\n                   parse_dates=["week_start"])\n\n# wide: 52 rows x 6 zone columns\nwide = vsat.pivot(index="week_start",\n                  columns="region",\n                  values="uptime_pct")',
             "caption": "Charts want one column per line: pivot does the reshaping", "notes": "Long is how databases export."},
            {"type": "bar", "title": f"Average uptime by zone: {f['lowest_zone']} is lowest",
             "labels": ZONES, "values": [round(f["means"][z], 2) for z in ZONES], "highlight": [ZONES.index(f["lowest_zone"])],
             "ymin": 97, "ymax": 99.5, "fmt": "0.00", "caption": "Tight axis (97–99.5%) because uptime lives near the top: range stated",
             "notes": "In the notebook they draw small multiples on a shared y-axis."},
            {"type": "chart", "title": "Indexed to week 1: who fell furthest from their own normal?",
             "labels": [d.strftime("%b") if d.day <= 7 else "" for d in idx.index],
             "series": [{"name": z, "values": idx[z].round(2).tolist(),
                         "color": {"South East": "C77700", "South West": "008C7E", "South South": "0A5DB4"}.get(z, "B9C7D8")} for z in ZONES],
             "ymin": 97.5, "ymax": 101, "fmt": "0.0", "notes": f"South East fell furthest, to {f['fell_furthest_idx']}."},
            {"type": "table", "title": "Two questions, two different answers",
             "header": ["Question", "Chart", "Answer"],
             "rows": [["Who is worst?", "raw uptime, small multiples", f"{f['lowest_zone']} (avg {f['lowest_zone_mean']}%, worst week {f['worst_week_val']}%)"],
                      ["Who dropped most from normal?", "indexed to week 1 = 100", f"{f['fell_furthest']} (fell to {f['fell_furthest_idx']})"]],
             "colW": [3.6, 3.6, 4.93], "caption": "Lowest score is not the same as biggest drop since last term",
             "notes": "Both answers are right. They answer different questions."},
            {"type": "section", "kicker": "Part 3", "title": "Honest-chart rules", "sub": "Five habits that make charts trustworthy",
             "notes": "Section break."},
            {"type": "compare", "title": "Where should the y-axis start?",
             "left": ["📈", "Percentages near the top", "Zoom in (e.g. 96–100%) and write the range on the chart"],
             "right": ["🎫", "Counts you can add up", "Start at zero, or small differences look huge"],
             "notes": "Quiz question 1."},
            {"type": "cards5", "title": "The 5 honest-chart rules", "cards": [
                ["🚧", "Threshold line"], ["📰", "Title = finding"], ["📏", "Sensible axis"], ["☝🏾", "One y-axis"], ["🏷️", "Units"]],
             "notes": "Evidence in court: the other lawyer checks all five."},
            {"type": "compare", "title": "A title should state the finding",
             "left": ["❌", "Names the data", "Link margin, August"],
             "right": ["✅", "States the finding", f"Ka-band link went down on {f['outage_days']} of {f['days']} August days, all during heavy rain"],
             "notes": "Quiz question 5."},
            {"type": "steps", "title": "The 4-sentence finding", "icon": "🗣️", "steps": [
                "Situation: what the unit does", "Observation: what the data showed, with a number",
                "Implication: why it matters", "Recommendation: what to do next (always LAST)"],
             "notes": "Quiz question 6: recommendation comes last."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W1D2-exercise in Colab, then Save a copy in Drive", "Run STEP 0, then top to bottom",
                "Part A: catch the average in its lie", "Part B: six zones, one honest picture"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["📉", "Breach questions → plot the minimum, not the average"],
                ["🗺️", "Many groups → small multiples on one axis; change → index to week 1"],
                ["🗣️", "Title states the finding; 4 sentences end with the recommendation"]],
             "next": "Next: Calm Down the Noise (rolling windows)", "notes": "Tease Day 3."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
def _rf():
    return pd.read_csv(data_path("rf_link_quality_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")

def _wide():
    v = pd.read_csv(data_path("vsat_uptime_by_region_weekly"), parse_dates=["week_start"])
    return v.pivot(index="week_start", columns="region", values="uptime_pct")

def _c_a1(x):
    return x == "h", "Correct: \"h\" = hourly. 744 hours = 31 days × 24.", \
        "The code for HOURLY, in quotes, lowercase. (Old code used \"H\"; new pandas refuses it.)"

def _c_a2(x):
    want = int((_rf()["link_margin_db"] < 0).sum())
    return int(x) == want, f"{want} hours of outage in one month. Each one is a customer staring at “No Signal”. 📺", \
        "Count the hours where link_margin_db < 0. Use (...).sum()."

def _c_a3(x):
    want = _rf()["link_margin_db"].resample("D").mean().min()
    return abs(float(x) - want) < 0.01, f"{want:.2f} dB. The WORST daily average is still comfortably positive. Suspicious… 🤨", \
        "Take daily_mean and find its smallest value with .min()."

def _c_a4(x):
    want = int((_rf()["link_margin_db"].resample("D").min() < 0).sum())
    return int(x) == want, f"{want} of 31 days had an outage hour. The average showed ZERO. Caught it! 🕵🏾", \
        "Did you use .min() in the blank? Then count days where daily_min < 0."

def _c_a5(x):
    thr, title = x
    ok = float(thr) == 0 and isinstance(title, str) and len(title.strip()) >= 20 and any(ch.isdigit() for ch in title)
    return ok, "Threshold drawn at 0 dB and a title with a real number in it. Report-ready! 📰", \
        "The threshold for 'link down' is 0 dB. Your title needs a finding WITH a number (e.g. how many days)."

def _c_a6(x):
    return str(x).strip().lower() in {"min", "minimum", "daily minimum", "daily min"}, \
        "Yes: breach questions need the WORST moment of each day. 💯", \
        "Which daily summary showed the outages: the mean or the min?"

def _c_a7(x):
    return str(x).strip().lower() == "response", \
        "Correct: the station turns up uplink power BECAUSE it's raining. Response, not cause. 🔊", \
        "Does uplink power make it rain, or does rain make the station turn up the power?"

def _c_b1(x):
    return tuple(x) == ("week_start", "region", "uptime_pct"), "Pivoted! 52 weeks × 6 zones. 🗺️", \
        "Rows come from the week column, columns from the zone column, values from the uptime column. All in quotes."

def _c_b2(x):
    return x is True, "Shared y-axis: now the panels are fair to compare. ⚖️", \
        "Should the six panels use the SAME y-axis? True or False (no quotes)."

def _c_b3(x):
    want = _wide().mean().idxmin()
    return str(x).strip().lower() == want.lower(), f"{want}: lowest average uptime all year. 🌧️", \
        "wide.mean() gives each zone's average. Which one is smallest? .idxmin() tells you the name."

def _c_b4(x):
    w = _wide(); want = (w / w.iloc[0] * 100).min().idxmin()
    return str(x).strip().lower() == want.lower(), \
        f"{want}! Not the lowest zone, but the one that fell furthest from its OWN week 1. Different question, different answer. 🎓", \
        "Use indexed.min().idxmin(): the zone whose indexed line went lowest."

def _c_b5(x):
    a, b = (str(v).strip().lower() for v in x)
    return (a, b) == ("zero", "tight"), "Counts start at zero; bounded % near the top can zoom in (say the range!). 📏", \
        "Tickets are counts you can add up. Availability lives between 97 and 100. Answer \"zero\" or \"tight\" for each."

def _c_b6(x):
    got = [str(v).strip().lower() for v in x]
    return got == ["situation", "observation", "implication", "recommendation"], \
        "Situation → Observation → Implication → Recommendation. The boss reads the last line first. 😉", \
        "Choose from: Situation, Observation, Implication, Recommendation. What do you say first? What comes LAST?"

def _c_bonus(x):
    r = _rf(); want = r.loc[r["link_margin_db"] < 0, "rain_rate_mmhr"].min()
    return abs(float(x) - want) < 0.05, f"{want:.1f} mm/hr. Light rain? No wahala. A real storm (about 40 mm/hr+)? Link down. ⛈️", \
        "Filter the outage hours (link_margin_db < 0), then take the smallest rain_rate_mmhr."

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "A5": _c_a5, "A6": _c_a6, "A7": _c_a7,
          "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4, "B5": _c_b5, "B6": _c_b6, "BONUS": _c_bonus}
HINTS = {"A5": "Give a number for the threshold and a sentence (in quotes) for the title.",
         "B1": "Three column names, each in quotes.", "B6": "Four words in a list, in quotes, e.g. [\"Situation\", ...]"}
'''


def notebook_cells(setup_code):
    f = _facts()
    return [
        ("md", """# 📊 Week 1 · Day 2: Charts That Don't Lie

**Today:** catch a daily *average* hiding a whole month of outages, compare Nigeria's six zones fairly, and write a chart title and a 4-sentence finding your unit head will actually read.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (**Shift + Enter**) |
| ✍️ | Your turn: replace every `___` |
| ✅ / ❌ | The check tells you if you got it right |
| 🌶️ | Bonus for fast finishers |

> ## ⚠️ FIRST: **File → Save a copy in Drive**
> Work in your copy (the tab whose title starts with *Copy of*).

**Rule book:** keep `W1D2-rulebook.pdf` open beside you."""),
        ("md", """## ▶️ STEP 0: Set up (run once, and again after every restart)
Click the cell and press **Shift + Enter**. Wait for `✅ Ready!`. If Colab warns the notebook wasn't authored by Google, click **Run anyway**."""),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: The average lies (30 min) 🤥

**The data:** `rf_link_quality_hourly.csv`: every hour of August for the Ka-band link, at the wettest point of the rainy season.
The column that matters is **`link_margin_db`**: how much signal is left above the minimum the receiver needs.
Think of it as **fuel above the reserve line**. **Below 0 dB, the link is DOWN.** 📺❌

### A1 ✍️ Load it with the 3-line recipe
The data is **hourly**. What's the frequency code for hourly? (Daily was `"D"` on Day 1. Hourly is one **lowercase** letter.)"""),
        ("task", 'FREQ = ___\n\ncheck("A1", FREQ)', 'FREQ = "h"\n\ncheck("A1", FREQ)'),
        ("code", 'assert FREQ is not None, "✍️ Do A1 first: fill in FREQ above, then run this cell again."\n\n'
                 'rf = pd.read_csv(data_path("rf_link_quality_hourly"),\n                 parse_dates=["timestamp"],\n                 index_col="timestamp")\n'
                 'rf = rf.asfreq(FREQ)\n\nprint("rows:", len(rf))\nrf.head()'),
        ("md", """### A2 ✍️ How many hours was the link actually DOWN?
`rf["link_margin_db"] < 0` gives True/False for every hour. `.sum()` counts the Trues."""),
        ("task", 'outage_hours = ___\n\ncheck("A2", outage_hours)', 'outage_hours = (rf["link_margin_db"] < 0).sum()\n\ncheck("A2", outage_hours)'),
        ("md", """### A3 ✍️ Now summarise by DAY, using the average
`.resample("D").mean()` turns 744 hours into 31 daily averages. What is the **lowest** daily average in the whole month?"""),
        ("task", 'daily_mean = rf["link_margin_db"].resample("D").mean()\n\nlowest_daily_mean = ___\nprint("lowest daily average:", lowest_daily_mean)\n\ncheck("A3", lowest_daily_mean)',
         'daily_mean = rf["link_margin_db"].resample("D").mean()\n\nlowest_daily_mean = daily_mean.min()\nprint("lowest daily average:", lowest_daily_mean)\n\ncheck("A3", lowest_daily_mean)'),
        ("md", """🤨 If the worst daily average is that healthy, the link never went down… right? Let's check the daily **worst moment** instead.

### A4 ✍️ Summarise by day using the MINIMUM
Fill the blank with the method name for the smallest value (no quotes, it's a method), then count the days that dipped below 0."""),
        ("task", 'daily_min = rf["link_margin_db"].resample("D").___()\n\ndays_with_outage = (daily_min < 0).sum()\nprint("days with at least one outage hour:", days_with_outage)\n\ncheck("A4", days_with_outage)',
         'daily_min = rf["link_margin_db"].resample("D").min()\n\ndays_with_outage = (daily_min < 0).sum()\nprint("days with at least one outage hour:", days_with_outage)\n\ncheck("A4", days_with_outage)'),
        ("md", """> 💡 If you got `AttributeError: 'Resampler' object has no attribute '___'`, you haven't replaced the blank yet.

### A5 ✍️ Draw the honest chart
Both lines on one chart, plus a **threshold line** at the level where the link goes down, plus a **title that states the finding** (include a number!)."""),
        ("task", 'THRESHOLD = ___\nmy_title = ___\n\nassert THRESHOLD is not None and my_title is not None, "✍️ Fill in THRESHOLD and my_title first."\n'
                 'ax = daily_mean.plot(label="daily average", lw=2)\ndaily_min.plot(ax=ax, label="daily minimum", lw=2)\n'
                 'plt.axhline(THRESHOLD, color="red", ls="--", label="link down")\nplt.title(my_title)\nplt.ylabel("link margin (dB)")\nplt.legend()\nplt.show()\n\n'
                 'check("A5", (THRESHOLD, my_title))',
         f'THRESHOLD = 0\nmy_title = "Ka-band link went down on {f["outage_days"]} of 31 August days, yet the daily average looks perfect"\n\n'
         'assert THRESHOLD is not None and my_title is not None, "✍️ Fill in THRESHOLD and my_title first."\n'
         'ax = daily_mean.plot(label="daily average", lw=2)\ndaily_min.plot(ax=ax, label="daily minimum", lw=2)\n'
         'plt.axhline(THRESHOLD, color="red", ls="--", label="link down")\nplt.title(my_title)\nplt.ylabel("link margin (dB)")\nplt.legend()\nplt.show()\n\n'
         'check("A5", (THRESHOLD, my_title))'),
        ("md", """### A6 ✍️ The SLA question
Your unit head asks: *“Did the link breach its SLA this month?”* Which daily summary should you plot: `"mean"` or `"min"`?"""),
        ("task", 'sla_summary = ___\n\ncheck("A6", sla_summary)', 'sla_summary = "min"\n\ncheck("A6", sla_summary)'),
        ("md", """### A7 ✍️ Cause or response?
▶️ Run the first cell: it draws rain and uplink power as **two stacked charts sharing one time axis** (two units → two charts, never two y-axes), and prints their correlation.
Then answer: does uplink power **cause** the rain problem, or is it the station's **response** to rain? Type `"cause"` or `"response"`."""),
        ("code", 'fig, axes = plt.subplots(2, 1, figsize=(11, 5), sharex=True)\nrf["rain_rate_mmhr"].plot(ax=axes[0], color="#008C7E", title="Rain at the earth station (mm/hr)")\n'
                 'rf["uplink_power_dbm"].plot(ax=axes[1], color="#0A5DB4", title="Uplink power (dBm): the station turns up the volume")\nplt.tight_layout()\nplt.show()\n\n'
                 'print("correlation:", round(rf["rain_rate_mmhr"].corr(rf["uplink_power_dbm"]), 2))'),
        ("task", 'cause_or_response = ___\n\ncheck("A7", cause_or_response)', 'cause_or_response = "response"\n\ncheck("A7", cause_or_response)'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Six zones, one honest picture (30 min) 🗺️

**The data:** `vsat_uptime_by_region_weekly.csv`: average VSAT terminal uptime for each of Nigeria's six geopolitical zones, every week of the year.
It's in **long format**: one row per zone per week. ▶️ Run it and look."""),
        ("code", 'vsat = pd.read_csv(data_path("vsat_uptime_by_region_weekly"), parse_dates=["week_start"])\n\nprint("rows:", len(vsat), "= 52 weeks × 6 zones")\nvsat.head(8)'),
        ("md", """### B1 ✍️ Pivot: long → wide
Charts want **one column per line**. `pivot` reshapes the table. Which column becomes the **rows** (index), which becomes the **columns**, and which holds the **values**?"""),
        ("task", 'INDEX_COL = ___\nCOLUMNS_COL = ___\nVALUES_COL = ___\n\ncheck("B1", (INDEX_COL, COLUMNS_COL, VALUES_COL))',
         'INDEX_COL = "week_start"\nCOLUMNS_COL = "region"\nVALUES_COL = "uptime_pct"\n\ncheck("B1", (INDEX_COL, COLUMNS_COL, VALUES_COL))'),
        ("code", 'assert None not in (INDEX_COL, COLUMNS_COL, VALUES_COL), "✍️ Do B1 first."\n\nwide = vsat.pivot(index=INDEX_COL, columns=COLUMNS_COL, values=VALUES_COL)\nprint(wide.shape)\nwide.head(3)'),
        ("md", """### B2 ✍️ Small multiples
First, ▶️ run the **spaghetti** version: six lines on one axis. Try to find South South. 🍝"""),
        ("code", 'wide.plot(figsize=(11, 4), title="Six lines on one chart: can you find South South?")\nplt.show()'),
        ("md", "Now one mini chart per zone. Should all six panels use the **same y-axis** so they're fair to compare? `True` or `False` (no quotes)."),
        ("task", 'SAME_AXIS = ___\n\nassert SAME_AXIS is not None, "✍️ Fill in SAME_AXIS first."\n'
                 'wide.plot(subplots=True, layout=(2, 3), sharey=SAME_AXIS, figsize=(12, 5), legend=False, title=list(wide.columns))\n'
                 'plt.suptitle("Weekly VSAT uptime (%) by zone", fontweight="bold")\nplt.tight_layout()\nplt.show()\n\ncheck("B2", SAME_AXIS)',
         'SAME_AXIS = True\n\nassert SAME_AXIS is not None, "✍️ Fill in SAME_AXIS first."\n'
         'wide.plot(subplots=True, layout=(2, 3), sharey=SAME_AXIS, figsize=(12, 5), legend=False, title=list(wide.columns))\n'
         'plt.suptitle("Weekly VSAT uptime (%) by zone", fontweight="bold")\nplt.tight_layout()\nplt.show()\n\ncheck("B2", SAME_AXIS)'),
        ("md", """### B3 ✍️ Who is worst?
`wide.mean()` gives each zone's average for the year. `.idxmin()` returns the **name** of the smallest. Type the zone's name in quotes."""),
        ("code", "wide.mean().round(2).sort_values()"),
        ("task", 'lowest_zone = ___\n\ncheck("B3", lowest_zone)', 'lowest_zone = wide.mean().idxmin()\n\ncheck("B3", lowest_zone)'),
        ("md", """### B4 ✍️ Who fell furthest from their OWN normal?
A different question! We **index** every zone to its own week 1: divide by week 1 and multiply by 100. Every line now starts at 100.
▶️ Run the chart, then find the zone whose indexed line goes **lowest** (`indexed.min().idxmin()`)."""),
        ("code", 'indexed = wide / wide.iloc[0] * 100\n\nindexed.plot(figsize=(11, 4), title="Uptime indexed to week 1 (= 100)")\nplt.axhline(100, color="grey", ls="--")\nplt.show()\n\nindexed.min().round(2).sort_values()'),
        ("task", 'fell_furthest = ___\n\ncheck("B4", fell_furthest)', 'fell_furthest = indexed.min().idxmin()\n\ncheck("B4", fell_furthest)'),
        ("md", """> 🎓 The lowest zone and the zone that fell furthest are **not the same**. Lowest score ≠ biggest drop since last term. Always ask: *which question am I answering?*

### B5 ✍️ Where should the y-axis start?
For each chart, answer `"zero"` (start the axis at 0) or `"tight"` (zoom in, and write the range on the chart):
1. A bar chart of **NOC tickets per weekday** (counts you can add up)
2. A line chart of **Ka-band availability**, which lives between 97% and 100%"""),
        ("task", 'tickets_axis = ___\navailability_axis = ___\n\ncheck("B5", (tickets_axis, availability_axis))',
         'tickets_axis = "zero"\navailability_axis = "tight"\n\ncheck("B5", (tickets_axis, availability_axis))'),
        ("md", """### B6 ✍️ The 4-sentence finding
Put these four in the right order: `"Implication"`, `"Recommendation"`, `"Situation"`, `"Observation"`."""),
        ("task", 'order = [___, ___, ___, ___]\n\ncheck("B6", tuple(order))',
         'order = ["Situation", "Observation", "Implication", "Recommendation"]\n\ncheck("B6", tuple(order))'),
        ("md", """✍️ **Now write your own** 4-sentence finding about the six zones (not checked: your trainer will pick a few to read out 🎤). Double-click this cell and type:

1. **Situation:** …
2. **Observation:** … (use a number from B3 or B4)
3. **Implication:** …
4. **Recommendation:** …"""),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: how heavy must the rain be to kill the link?
Filter the hours where the link was down (`rf["link_margin_db"] < 0`) and find the **smallest** `rain_rate_mmhr` among them. That's the lightest rain that caused an outage."""),
        ("task", '# hint: rf.loc[ condition , "column" ].min()\nlightest_killer_rain = ___\n\ncheck("BONUS", lightest_killer_rain)',
         'lightest_killer_rain = rf.loc[rf["link_margin_db"] < 0, "rain_rate_mmhr"].min()\nprint(lightest_killer_rain, "mm/hr")\n\ncheck("BONUS", lightest_killer_rain)'),
        ("md", "---\n## 🏁 Finish line\n▶️ Run the scoreboard, then **File → Save**."),
        ("code", "scoreboard()"),
        ("md", f"""### 📝 What you learned today
- **Breach / SLA questions → plot the daily minimum.** The average stayed above {f['lowest_mean']} dB while the link was down {f['outage_hours']} hours on {f['outage_days']} days.
- **Correlation ≠ cause:** uplink power rises *because* of rain (a response).
- **Two units → two stacked charts**, never two y-axes.
- **Long → wide** with `pivot`; **many groups → small multiples on a shared y-axis**.
- **Index to week 1** answers *“who fell furthest from their own normal?”*, a different question from *“who is lowest?”*.
- **Axes:** counts start at zero; bounded % near the top can zoom in (state the range).
- **Tell it:** a title that states the finding, then Situation → Observation → Implication → **Recommendation**.

**Next time:** *Calm Down the Noise*: rolling windows, and why even faults rest on Sunday. 😴

<sub>Data: synthetic teaching datasets from the original Week 3 code book (`Time-series/week-03`). Safe for AI assistants. Real NIGCOMSAT data is not.</sub>"""),
    ]
