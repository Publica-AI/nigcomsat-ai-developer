"""Week 1 · Day 1: Colab Bootcamp + Your First Time Series."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import BRAND as B, ORIGINALS
from svgcharts import line_svg, spark_svg
from webdeck import logos_title_block

CODE = "W1D1"
TITLE = "Colab Bootcamp + Your First Time Series"

D3 = ORIGINALS / "week-03" / "data"


def _data():
    ka = pd.read_csv(D3 / "ka_band_availability_daily.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("D")
    kam = pd.read_csv(D3 / "ka_band_availability_monthly.csv", parse_dates=["month"], index_col="month")
    util = pd.read_csv(D3 / "transponder_utilisation_monthly.csv", parse_dates=["month"], index_col="month")
    tkw = pd.read_csv(D3 / "noc_tickets_weekly.csv", parse_dates=["week_start"], index_col="week_start")
    return ka, kam, util, tkw


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    ka, kam, util, tkw = _data()
    s = ka["availability_pct"]
    n = len(s)

    def i_of(date):
        return int((pd.Timestamp(date) - s.index[0]).days)

    worst = s.idxmin()
    ka_chart = line_svg(
        s.values, w=1420, h=470, ymin=95.5, ymax=100,
        yticks=[(96, "96%"), (97, "97%"), (98, "98%"), (99, "99%"), (100, "100%")],
        xlabels=[(0, "Jan 2023"), (i_of("2024-01-01"), "Jan 2024"), (i_of("2025-01-01"), "Jan 2025"), (n - 1, "Dec 2025")],
        bands=[(i_of(f"{y}-07-01"), i_of(f"{y}-09-30"), B["gold"], .10, "🌧️ peak rain") for y in (2023, 2024, 2025)],
        markers=[(i_of(worst), f"worst day: {s.min():.1f}%", B["bad"])],
        dur="3.2s",
    )
    m = kam["availability_pct"].values
    rng = np.random.default_rng(7)
    shuffled = m[rng.permutation(len(m))]
    ordered_svg = line_svg(m, w=620, h=300, ymin=97.5, ymax=100.2, area=False, stroke=4,
                           xlabels=[(0, "2023"), (35, "2025")], dur="2s")
    shuffled_svg = line_svg(shuffled, w=620, h=300, ymin=97.5, ymax=100.2, area=False, stroke=4,
                            color=B["bad"], xlabels=[(0, "?"), (35, "?")], dur="2s", delay=".1s")

    # NEPA day: light on/off by hour
    light = [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
    nepa_blocks = "".join(
        f'<div class="anim a-pop" style="--d:{.25 + i * .07:.2f}s;width:50px;height:110px;border-radius:12px;'
        f'background:{"#F5B83D" if on else "#1B2B40"};box-shadow:{"0 0 22px rgba(245,184,61,.55)" if on else "none"};'
        f'display:flex;align-items:flex-end;justify-content:center;padding-bottom:8px;font-size:16px;'
        f'color:{"#3a2600" if on else "#6F8399"};font-weight:700">{i:02d}</div>'
        for i, on in enumerate(light))

    comps = [
        ("📈", "Trend", "The long direction. Like Lagos: more people every year.", spark_svg(util["util_pct"].values, color=B["blue_d"], delay=".5s"), "transponder use, 2023→2025"),
        ("🌧️", "Seasonality", "Repeats on a fixed calendar. Rainy season, every year.", spark_svg(kam["availability_pct"].values, color=B["teal_d"], delay=".8s"), "Ka-band availability, monthly"),
        ("🎢", "Cycle", "Ups and downs with NO fixed length. Boom years, slow years.", spark_svg(np.sin(np.linspace(0, 3.2 * np.pi, 80) ** 1.15) + np.linspace(0, .6, 80), color=B["gold"], delay="1.1s"), "illustration"),
        ("🎲", "Noise", "Random wobble. 38 tickets vs 41 tickets = same week.", spark_svg(tkw["tickets_raised"].values, color="#B9C7D8", delay="1.4s"), "NOC tickets per week, 2025"),
    ]
    comp_cards = "".join(
        f'<div class="card anim" style="--d:{.2 + k * .25:.2f}s;padding:28px"><div style="font-size:60px">{e}</div>'
        f'<h3 style="margin-top:8px">{t}</h3><p style="font-size:24px;color:var(--muted);min-height:100px">{d}</p>{svg}'
        f'<div class="small" style="font-size:17px;margin-top:4px">{src}</div></div>'
        for k, (e, t, d, svg, src) in enumerate(comps))

    days_row = []
    for i in range(1, 15):
        missing = i in (6, 7, 8)
        days_row.append(
            f'<div style="width:78px;height:78px;border-radius:14px;display:flex;align-items:center;justify-content:center;'
            f'font-size:24px;font-weight:800;'
            f'background:{"#12233A" if not missing else "transparent"};border:2px {"solid #24384F" if not missing else "dashed #FF6B6F"};'
            f'color:{"#EAF2FB" if not missing else "#FF6B6F"}">{"NaN" if missing else i}</div>')
    days_with_gap = "".join(days_row)
    days_hidden = "".join(
        f'<div style="width:78px;height:78px;border-radius:14px;display:flex;align-items:center;justify-content:center;'
        f'font-size:24px;font-weight:800;background:#12233A;border:2px solid #24384F">{i}</div>'
        for i in [1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14])

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:-120px;top:120px;width:640px;height:640px;opacity:.9">
  <svg viewBox="0 0 640 640" width="640" height="640">
    <defs><radialGradient id="earth" cx="40%" cy="35%"><stop offset="0" stop-color="#3B8BE0"/><stop offset=".7" stop-color="#0A3B73"/><stop offset="1" stop-color="#061a33"/></radialGradient></defs>
    <circle cx="320" cy="320" r="150" fill="url(#earth)"/>
    <path d="M250 250 q40 -30 70 0 t60 30 q-20 40 -60 30 t-70 -60z" fill="#16A394" opacity=".55"/>
    <circle cx="320" cy="320" r="270" fill="none" stroke="#24384F" stroke-width="2" stroke-dasharray="6 10"/>
    <g class="spin" style="--t:18s;transform-origin:320px 320px"><g transform="translate(590 320)">
      <rect x="-14" y="-14" width="28" height="28" rx="4" fill="#EAF2FB"/><rect x="-62" y="-8" width="40" height="16" fill="#3B8BE0"/><rect x="22" y="-8" width="40" height="16" fill="#3B8BE0"/>
      <circle cx="0" cy="0" r="40" fill="none" stroke="#F5B83D" stroke-width="2" class="pulse"/></g></g>
  </svg></div>
<div style="max-width:980px;margin-top:40px">
  <div class="kicker anim">Week 1 · Day 1</div>
  <h1 class="anim" style="--d:.2s">Colab Bootcamp<br><span class="hl">+ Your First<br>Time Series</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Today you open Google Colab, load real satellite-style data<br>and draw your first time-series chart. 🛰️</p>
  <div class="anim" style="--d:.8s;margin-top:44px;display:flex;justify-content:flex-start">{logos_title_block()}</div>
</div>""",
          "Welcome everyone. By the end of today every person in this room will have opened Colab, loaded a real "
          "NIGCOMSAT-style dataset and drawn a chart. No installs, no stress. Ask: who has used Jupyter or Colab before?"),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Three moves. That's all.</h2>
<div class="flow" style="margin-top:70px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:380px;padding:46px 34px"><div class="icon">💻</div><h3>Open Colab</h3><p class="small">your Python lives in the browser</p></div>
  <div class="arrow anim a-fade" style="--d:.6s"></div>
  <div class="box on anim a-pop" style="--d:.8s;min-width:380px;padding:46px 34px"><div class="icon">🛰️</div><h3>Load the data</h3><p class="small">3 years of Ka-band availability</p></div>
  <div class="arrow anim a-fade" style="--d:1.1s"></div>
  <div class="box on anim a-pop" style="--d:1.3s;min-width:380px;padding:46px 34px"><div class="icon">📈</div><h3>Draw the story</h3><p class="small">find the rainy-season dip yourself</p></div>
</div>
<div class="row anim" style="--d:1.7s;margin-top:70px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up</span>
</div>""",
          "Show the three moves. Tell them the hands-on block is the main event and the slides are just the trailer."),

        # 3 ─ NEPA hook
        S(f"""
<div class="kicker anim">Quick question</div>
<h2 class="anim" style="--d:.1s">Did NEPA bring light yesterday? 💡</h2>
<p class="sub anim" style="--d:.25s">Here is one house, hour by hour. Yellow = light. Dark = “NEPA has taken light.”</p>
<div style="display:flex;gap:8px;margin-top:46px">{nepa_blocks}</div>
<div class="row" style="margin-top:46px;gap:30px">
  <div class="card step" data-step="1" style="flex:1"><h3>🕐 A time</h3><p class="muted">every hour, 00 → 23</p></div>
  <div class="card step" data-step="1" style="flex:1"><h3>⚡ A value</h3><p class="muted">light on (1) or off (0)</p></div>
  <div class="card step glow" data-step="2" style="flex:1.3"><h3 class="hl">= a time series</h3><p>You have been collecting data all your life. “Up NEPA!” is a data point. 😄</p></div>
</div>""",
          "Get them laughing. Ask: how many hours of light did you get yesterday? Then reveal: a time + a value, "
          "recorded in order = a time series. The satellite does exactly this, every hour, for every sensor."),

        # 4 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">Colab Bootcamp 💻</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Your free Python computer that lives inside Google Chrome.</p>""",
          "Section break. Ask everyone to open Chrome and sign in to their Google account now.", cls="center"),

        # 5 ─ what is colab
        S("""
<div class="kicker anim">What is Colab?</div>
<h2 class="anim" style="--d:.1s">Your laptop just shows the screen.<br><span class="teal">Google's computer does the work.</span></h2>
<div class="flow" style="margin-top:50px;justify-content:center">
  <div class="box anim a-left" style="--d:.3s;min-width:300px"><div class="icon">💻</div><h3>Your laptop</h3><p class="small">only needs Chrome</p></div>
  <div class="arrow anim a-fade" style="--d:.7s;width:140px"></div>
  <div class="box on anim a-pop" style="--d:.9s;min-width:400px"><div class="icon floaty">☁️</div><h3>Google's computer</h3><p class="small">already has Python, pandas, matplotlib, scikit-learn</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s;width:140px"></div>
  <div class="box anim a-right" style="--d:1.5s;min-width:300px"><div class="icon">📊</div><h3>Your answers</h3><p class="small">tables + charts, back on your screen</p></div>
</div>
<p class="anim" style="--d:1.9s;margin-top:50px;text-align:center">Like a cyber café computer… <b class="hl">but free, and it never runs out of fuel.</b> ⛽😄</p>""",
          "Key idea: nothing to install. The computer doing the work is in Google's data centre, so even a small laptop is fine. "
          "Bonus: the data downloads happen on Google's side, not on our office network."),

        # 6 ─ anatomy
        S("""
<div class="kicker anim">Find your way around</div>
<h2 class="anim" style="--d:.1s" >The Colab screen in 5 parts</h2>
<div class="row" style="gap:40px;margin-top:6px">
 <div class="anim a-left" style="--d:.2s;flex:1.35;background:#fff;border-radius:22px;overflow:hidden;color:#1f2a37;box-shadow:0 30px 80px rgba(0,0,0,.5)">
  <div style="background:#F1F3F4;padding:14px 22px;display:flex;align-items:center;gap:14px;font-size:22px">
    <span style="background:#F9AB00;color:#fff;border-radius:8px;padding:2px 10px;font-weight:800">CO</span><b>W1D1-exercise.ipynb</b>
    <span style="margin-left:auto;font-size:18px;color:#5f6368">File · Edit · View · Insert · <b style="color:#0A5DB4;outline:3px solid #F5B83D;border-radius:6px;padding:0 6px">Runtime</b> · Tools</span></div>
  <div style="display:flex">
   <div style="width:70px;background:#F8F9FA;border-right:1px solid #E0E0E0;display:flex;flex-direction:column;align-items:center;gap:22px;padding:20px 0;font-size:30px">
     <span>☰</span><span style="outline:3px solid #F5B83D;border-radius:8px">📁</span><span>🔑</span></div>
   <div style="flex:1;padding:22px 24px;display:flex;flex-direction:column;gap:16px">
     <div style="font-size:22px;outline:3px dashed #16A394;border-radius:10px;padding:10px 14px"><b>📖 Text cell:</b> instructions live here</div>
     <div style="display:flex;gap:12px;align-items:flex-start">
       <div style="width:44px;height:44px;border-radius:50%;background:#1f2a37;color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px;outline:3px solid #F5B83D;outline-offset:3px">▶</div>
       <div style="flex:1;background:#F7F7F7;border-radius:10px;padding:14px 16px;font-family:Menlo,monospace;font-size:21px;outline:3px solid #3B8BE0">print("Hello NIGCOMSAT 🛰️")</div></div>
     <div style="font-family:Menlo,monospace;font-size:21px;padding-left:58px;color:#0A5DB4">Hello NIGCOMSAT 🛰️</div>
   </div></div>
 </div>
 <div class="col" style="flex:1;gap:16px">
  <div class="row step" data-step="1" style="gap:18px;align-items:center"><span class="num">1</span><p><b>▶ Run button</b>: runs one cell. Shortcut: <b class="hl">Shift + Enter</b></p></div>
  <div class="row step" data-step="2" style="gap:18px;align-items:center"><span class="num">2</span><p><b>Code cell</b> <span class="blue">(blue box)</span>: Python goes here</p></div>
  <div class="row step" data-step="3" style="gap:18px;align-items:center"><span class="num">3</span><p><b>Text cell</b> <span class="teal">(green box)</span>: reading, not running</p></div>
  <div class="row step" data-step="4" style="gap:18px;align-items:center"><span class="num">4</span><p><b>📁 Files panel</b>: data you download or upload</p></div>
  <div class="row step" data-step="5" style="gap:18px;align-items:center"><span class="num">5</span><p><b>Runtime menu</b>: restart and “Run all”</p></div>
 </div>
</div>""",
          "Click through the five numbered parts. Have everyone find each one on their own screen before moving on."),

        # 7 ─ golden rules
        S("""
<div class="kicker anim">Colab's 3 golden rules</div>
<h2 class="anim" style="--d:.1s">Follow these and Colab won't embarrass you</h2>
<div class="grid3" style="margin-top:30px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">💾</div><h3>1. Save a copy first</h3><p class="muted">File → <b style="color:#fff">Save a copy in Drive</b>. Otherwise your work vanishes when you close the tab.</p></div>
  <div class="card anim a-pop" style="--d:.6s"><div class="icon">⬇️</div><h3>2. Top to bottom</h3><p class="muted">Run cells <b style="color:#fff">in order</b> with Shift + Enter. Skipping a cell is like skipping a step in a recipe.</p></div>
  <div class="card anim a-pop" style="--d:.9s"><div class="icon">🔄</div><h3>3. Confused? Restart</h3><p class="muted">Runtime → <b style="color:#fff">Restart session and run all</b>. It fixes 80% of weird problems.</p></div>
</div>
<p class="anim" style="--d:1.3s;margin-top:40px;text-align:center" ><span class="pill bad">Rule 1 is the big one. Do it now, before anything else.</span></p>""",
          "Make everyone do Rule 1 right now: File → Save a copy in Drive. Walk the room and check. People who skip this lose their work."),

        # 8 ─ short memory
        S("""
<div class="kicker anim">Why do I get NameError?</div>
<h2 class="anim" style="--d:.1s">Colab has a short memory 🧠</h2>
<div class="row" style="gap:28px;margin-top:20px">
  <div class="card" style="flex:1"><p class="small">What Colab remembers right now</p>
    <div class="col" style="gap:14px;margin-top:16px;font-family:var(--mono);font-size:26px">
      <div class="anim" style="--d:.3s;background:#07101A;border-radius:12px;padding:12px 18px">hours_in_year = <span class="n">8760</span></div>
      <div class="anim" style="--d:.5s;background:#07101A;border-radius:12px;padding:12px 18px">ka = <span class="muted">[1096 rows]</span></div>
      <div class="anim" style="--d:.7s;background:#07101A;border-radius:12px;padding:12px 18px">TIME_COLUMN = <span class="s">"timestamp"</span></div>
    </div></div>
  <div class="col" style="flex:1;gap:20px">
    <div class="card step" data-step="1"><h3>🔄 Restart session…</h3><p class="muted">…or leave Colab idle for too long. The memory is wiped. 🧹</p></div>
    <div class="card step" data-step="2" style="border-color:#E5484D"><pre class="code" style="font-size:22px;padding:16px 20px;color:#FF9EA1;border:none;background:transparent">NameError: name 'ka' is not defined</pre>
      <p>Translation: <b class="hl">“I don't remember. Run the cells above again.”</b></p></div>
  </div>
</div>""",
          "This is the error they will see most this week. Demo it live: restart, run a lower cell, see NameError, then run STEP 0 and the cells above."),

        # 9 ─ AI rule
        S("""
<div class="kicker anim">The AI button (Gemini) in Colab</div>
<h2 class="anim" style="--d:.1s">AI can help you. It must never see restricted data.</h2>
<div class="grid2" style="margin-top:30px">
  <div class="card anim a-left" style="--d:.3s;border-color:#1E9E5A"><div class="icon">🟢</div><h3>OK to paste</h3>
    <p class="muted">This course's training data (it is synthetic, made for teaching)<br>Your own code and error messages<br>“Explain this line to me”</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#E5484D"><div class="icon">⛔</div><h3>Never paste</h3>
    <p class="muted">Real NIGCOMSAT telemetry, RF records, network logs<br>Customer or staff details<br>Anything your unit has not cleared</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:36px;text-align:center">Not sure? <b class="hl">Describe the shape</b> (“a table of hourly voltages”), <b class="hl">don't paste the data.</b></p>""",
          "This is a data-protection rule, not a suggestion. The training files are synthetic and safe. Real operational data is restricted."),

        # 10 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">What is a time series? ⏱️</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">One idea. Once you get it, the whole course makes sense.</p>""",
          "Section break.", cls="center"),

        # 11 ─ order matters
        S(f"""
<div class="kicker anim">The one big idea</div>
<h2 class="anim" style="--d:.1s">A time series is a table where<br><span class="hl">the ORDER of the rows carries meaning</span></h2>
<div class="grid2" style="margin-top:18px">
  <div class="card anim" style="--d:.3s;padding:24px 28px"><h3>✅ In time order</h3><p class="small">Ka-band availability, 36 months</p>{ordered_svg}
    <p style="font-size:24px">You can see the yearly rainy-season dip.</p></div>
  <div class="card step" data-step="1" style="padding:24px 28px;border-color:#E5484D"><h3 class="bad">🔀 Same numbers, shuffled</h3><p class="small">exactly the same 36 values</p>{shuffled_svg}
    <p style="font-size:24px">The story is gone. Order <b>is</b> information.</p></div>
</div>""",
          "Show the ordered chart, then press next to shuffle. Same numbers, no story. A shopping list can be shuffled; a time series cannot. This is quiz question 1."),

        # 12 ─ anatomy of a ts
        S("""
<div class="kicker anim">Anatomy</div>
<h2 class="anim" style="--d:.1s">Every time series has 3 things</h2>
<div class="row" style="gap:30px;margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s;flex:1"><div class="icon">🕐</div><h3>A timestamp</h3><p class="muted">when it happened</p><pre class="code" style="font-size:22px;margin-top:14px;padding:14px 18px">2025-08-01T21:00</pre></div>
  <div class="card anim a-pop" style="--d:.55s;flex:1"><div class="icon">🔢</div><h3>A value</h3><p class="muted">what was measured</p><pre class="code" style="font-size:22px;margin-top:14px;padding:14px 18px">battery_soc_pct = 77.3</pre></div>
  <div class="card anim a-pop" style="--d:.8s;flex:1"><div class="icon">🥁</div><h3>A rhythm (cadence)</h3><p class="muted">how often it is recorded</p>
    <div style="margin-top:14px"><span class="pill">hourly</span><span class="pill teal">daily</span><span class="pill gold">weekly</span><span class="pill">monthly</span></div></div>
</div>
<p class="anim" style="--d:1.2s;margin-top:40px;text-align:center">Like checking your phone: some people check <b>every minute</b>, some <b>once a day</b>. Same life, different cadence. 📱</p>""",
          "Timestamp, value, cadence. In the course files: bus power is hourly, Ka-band is daily, VSAT uptime is weekly, transponder utilisation is monthly."),

        # 13 ─ satellite
        S("""
<div class="row" style="gap:40px">
 <div class="col" style="flex:1.15;gap:0">
  <div class="kicker anim">Meet the star of the course</div>
  <h2 class="anim" style="--d:.1s">NigComSat-1R 🛰️</h2>
  <p class="sub anim" style="--d:.25s">Nigeria's communications satellite, parked over the equator at <b class="hl">42.5° East</b>.</p>
  <div class="grid2" style="margin-top:28px;gap:20px">
    <div class="card anim" style="--d:.4s;padding:20px 26px"><div class="stat count" style="font-size:78px" data-to="28" data-d=".5">0</div><div class="stat-label">active transponders</div></div>
    <div class="card anim" style="--d:.55s;padding:20px 26px"><div class="stat" style="font-size:78px"><span class="count" data-to="36000" data-d=".6">0</span></div><div class="stat-label">km above the Earth (approx.)</div></div>
    <div class="card anim" style="--d:.7s;padding:20px 26px"><div class="stat" style="font-size:54px;line-height:78px;white-space:nowrap">C·Ku·Ka·L</div><div class="stat-label">four frequency bands</div></div>
    <div class="card anim" style="--d:.85s;padding:20px 26px"><div class="stat count" style="font-size:78px" data-to="15" data-suf=" yrs" data-d=".9">0</div><div class="stat-label">design life (launched 2011)</div></div>
  </div>
 </div>
 <div style="flex:1;display:flex;align-items:center;justify-content:center">
  <svg viewBox="0 0 600 600" width="560" height="560">
   <defs><radialGradient id="e2" cx="40%" cy="35%"><stop offset="0" stop-color="#3B8BE0"/><stop offset=".7" stop-color="#0A3B73"/><stop offset="1" stop-color="#061a33"/></radialGradient></defs>
   <circle cx="300" cy="300" r="120" fill="url(#e2)"/>
   <text x="300" y="306" text-anchor="middle" font-size="26" fill="#EAF2FB" font-weight="700">Earth</text>
   <circle cx="300" cy="300" r="250" fill="none" stroke="#24384F" stroke-width="2" stroke-dasharray="6 10"/>
   <g class="spin" style="--t:30s;transform-origin:300px 300px"><g transform="translate(550 300)">
     <rect x="-12" y="-12" width="24" height="24" rx="4" fill="#EAF2FB"/><rect x="-52" y="-7" width="34" height="14" fill="#3B8BE0"/><rect x="18" y="-7" width="34" height="14" fill="#3B8BE0"/></g></g>
   <path class="draw" style="--d:1s;--dur:2s" d="M422 300 L536 300" stroke="#F5B83D" stroke-width="3"/>
   <text x="480" y="282" text-anchor="middle" font-size="22" fill="#F5B83D">≈36,000 km</text>
   <text x="300" y="590" text-anchor="middle" font-size="22" fill="#9DB0C6">geostationary orbit: it stays over the same spot</text>
  </svg>
 </div>
</div>""",
          "Facts: launched December 2011 on a Chinese Long March rocket, replaced NigComSat-1 (lost in 2008 after a solar-array failure). "
          "28 transponders across C, Ku, Ka and L bands. The course data is SYNTHETIC but built to behave like this satellite."),

        # 14 ─ today's data
        S(f"""
<div class="kicker anim">Today's dataset · ka_band_availability_daily.csv</div>
<h2 class="anim" style="--d:.1s;font-size:52px">3 years of the Ka-band spot beam over Nigeria</h2>
<div class="card anim" style="--d:.2s;padding:18px 20px">{ka_chart}</div>
<div class="row anim" style="--d:2.8s;margin-top:22px;gap:14px;align-items:center">
  <span class="pill"><span class="count" data-to="1096" data-d="2.9">0</span> days</span>
  <span class="pill teal">no gaps</span>
  <span class="pill gold">🌧️ dips every rainy season = rain fade</span>
  <span class="small" style="margin-left:auto">synthetic teaching data</span>
</div>""",
          "This is the actual file they load today. Point at the dips: every year, rainy season. Ka-band is very sensitive to rain. "
          "Same reason DStv picture freezes in heavy Lagos rain. The worst single day sits in July 2023."),

        # 15 ─ pandas recipe
        S("""
<div class="kicker anim">Teach pandas about time</div>
<h2 class="anim" style="--d:.1s">The 3-line recipe you will use every day</h2>
<div class="flow" style="margin-top:16px">
  <div class="box anim a-pop" style="--d:.25s"><div class="icon">📄</div><h3>CSV</h3><p class="small">dates are just text</p></div>
  <div class="arrow anim a-fade" style="--d:.45s"></div>
  <div class="box on step" data-step="1"><div class="icon">🗓️</div><h3>parse_dates</h3><p class="small">text → real dates</p></div>
  <div class="arrow step" data-step="1"></div>
  <div class="box on step" data-step="2"><div class="icon">🧷</div><h3>index_col</h3><p class="small">time becomes the row label</p></div>
  <div class="arrow step" data-step="2"></div>
  <div class="box on step" data-step="3"><div class="icon">📏</div><h3>.asfreq("D")</h3><p class="small">declare the rhythm</p></div>
</div>
<pre class="code anim" style="--d:.6s;margin-top:34px">ka = pd.read_csv(data_path("ka_band_availability_daily"),
                 parse_dates=["timestamp"],      # 1. text -> dates
                 index_col="timestamp")          # 2. time is the row label
ka = ka.asfreq("D")                              # 3. one row per day, gaps show up</pre>""",
          "Walk the flow one box at a time. The exercise makes them fill in the column name themselves."),

        # 16 ─ asfreq
        S(f"""
<div class="kicker anim">Why .asfreq()?</div>
<h2 class="anim" style="--d:.1s">Missing days must <span class="bad">show up</span>, not hide</h2>
<div class="card anim" style="--d:.25s;margin-top:16px"><p class="small">Export from a system: day 6, 7 and 8 never arrived. Can you see it?</p>
  <div style="display:flex;gap:12px;margin-top:16px">{days_hidden}</div>
  <p style="margin-top:14px;font-size:26px">11 rows. Looks fine. <b class="bad">It is lying.</b> 🙈</p></div>
<div class="card step glow" data-step="1" style="margin-top:24px"><p class="small">After <span class="mono hl">.asfreq("D")</span>: one slot for every day</p>
  <div style="display:flex;gap:12px;margin-top:16px">{days_with_gap}</div>
  <p style="margin-top:14px;font-size:26px">14 rows. The 3 missing days appear as <b class="bad">NaN</b> (“Not a Number” = empty). Now you can count them. ✅</p></div>""",
          "This is quiz question 6. Without asfreq, a gap silently disappears and your averages and charts quietly lie."),

        # 17 ─ 5 questions
        S("""
<div class="kicker anim">Before you trust any new data</div>
<h2 class="anim" style="--d:.1s">Inspect it like a tokunbo car 🚗🔍</h2>
<div class="grid5" style="margin-top:50px">
  <div class="card anim a-pop" style="--d:.3s;padding:34px 26px"><div class="icon">🔢</div><h3>Rows?</h3><p class="small">how many readings</p></div>
  <div class="card anim a-pop" style="--d:.5s;padding:26px"><div class="icon">📅</div><h3>Range?</h3><p class="small">first and last date</p></div>
  <div class="card anim a-pop" style="--d:.7s;padding:26px"><div class="icon">🕳️</div><h3>Gaps?</h3><p class="small">missing periods</p></div>
  <div class="card anim a-pop" style="--d:.9s;padding:26px"><div class="icon">👯</div><h3>Duplicates?</h3><p class="small">same time twice</p></div>
  <div class="card anim a-pop" style="--d:1.1s;padding:26px"><div class="icon">❓</div><h3>Missing?</h3><p class="small">empty cells (NaN)</p></div>
</div>
<p class="anim" style="--d:1.5s;margin-top:44px;text-align:center">You check the engine, tyres and papers <b>before</b> you pay. Check these 5 <b class="hl">before</b> you analyse. 💸</p>""",
          "The five profiling questions from the original Week 3 code book. Real exports always fail at least one of them."),

        # 18 ─ time zones
        S("""
<div class="kicker anim">Time zones</div>
<h2 class="anim" style="--d:.1s">Satellites speak <span class="blue">UTC</span>. Lagos speaks <span class="teal">WAT</span>.</h2>
<div class="row" style="justify-content:center;gap:120px;margin-top:30px">
  <div class="anim a-pop" style="--d:.3s;text-align:center">
    <svg viewBox="0 0 260 260" width="260" height="260"><circle cx="130" cy="130" r="118" fill="#12233A" stroke="#3B8BE0" stroke-width="6"/>
      <line x1="130" y1="130" x2="130" y2="40" stroke="#EAF2FB" stroke-width="7" stroke-linecap="round" transform="rotate(270 130 130)"/>
      <line x1="130" y1="130" x2="130" y2="30" stroke="#3B8BE0" stroke-width="4" stroke-linecap="round"/></svg>
    <h3 style="margin-top:12px">21:00 <span class="blue">UTC</span></h3><p class="small">satellite telemetry: eclipse time</p></div>
  <div class="anim a-pop" style="--d:.6s;text-align:center">
    <svg viewBox="0 0 260 260" width="260" height="260"><circle cx="130" cy="130" r="118" fill="#12233A" stroke="#16A394" stroke-width="6"/>
      <line x1="130" y1="130" x2="130" y2="40" stroke="#EAF2FB" stroke-width="7" stroke-linecap="round" transform="rotate(300 130 130)"/>
      <line x1="130" y1="130" x2="130" y2="30" stroke="#16A394" stroke-width="4" stroke-linecap="round"/></svg>
    <h3 style="margin-top:12px">22:00 <span class="teal">WAT</span></h3><p class="small">Lagos / Abuja clock: UTC + 1, all year</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:30px;text-align:center"><b class="hl">Rule:</b> use ONE time zone before joining two tables. (Nigeria has no daylight saving 🙌)</p>""",
          "Quiz question 7. Telemetry is usually UTC, ticket systems usually local time. Mixing them shifts events by an hour and breaks joins."),

        # 19 ─ 4 components
        S(f"""
<div class="kicker anim">Sneak peek of Week 2</div>
<h2 class="anim" style="--d:.1s">Every series is made of 4 characters</h2>
<div class="grid4" style="margin-top:14px">{comp_cards}</div>""",
          "Quiz questions 2, 3 and 4. Seasonality has a fixed calendar; a cycle does not. Noise is the wobble you must NOT react to: 38 vs 41 tickets is the same week twice."),

        # 20 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Open the exercise notebook 🧑🏾‍💻</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Click <b class="hl">Open in Colab</b> on W1D1-exercise</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">2</span><p><b>File → Save a copy in Drive</b> 💾</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">3</span><p>Run <b>STEP 0</b>, then go top to bottom</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">4</span><p>Replace every <span class="mono hl">___</span>, run, get the ✅</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">✅</div>
  <h3 style="margin-top:16px">12 checks to pass</h3>
  <p class="muted">Part A: Colab warm-up<br>Part B: your first time series<br>🌶️ Bonus: the pepper task</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on time. Walk the room. The most common problems: forgot to run STEP 0, ran cells out of order, typed timestamp without quotes."),

        # 21 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">💾</span><p><b>Colab:</b> save a copy, run top to bottom, restart when confused.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">⏱️</span><p><b>Time series:</b> a table where <b class="hl">order matters</b>: timestamp + value + cadence.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">📏</span><p><b>pandas recipe:</b> parse_dates → index_col → .asfreq() so gaps can't hide.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:40px">Next time 👉 <b class="hl">Charts That Don't Lie</b>: why the <i>average</i> hid a whole rain outage. 🌧️</p>""",
          "Recap. Ask two volunteers to explain 'order matters' and 'why asfreq' in their own words. Tease Day 2."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)  -> consumed by build_pptx.js
# =============================================================================
def pptx_spec():
    ka, kam, util, tkw = _data()
    monthly = kam["availability_pct"]
    rng = np.random.default_rng(7)
    shuffled = monthly.values[rng.permutation(len(monthly))]
    labels = [d.strftime("%b %y") if d.month in (1, 4, 7, 10) else "" for d in monthly.index]
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🛰️", "kicker": "Week 1 · Day 1", "title": "Colab Bootcamp + Your First Time Series",
             "sub": "Open Google Colab, load satellite-style data, draw your first time-series chart",
             "notes": "Welcome. By the end of today everyone has opened Colab, loaded data and drawn a chart."},
            {"type": "flow", "title": "Today's mission: three moves", "steps": [
                ["💻", "Open Colab", "Python in your browser"],
                ["🛰️", "Load the data", "3 years of Ka-band availability"],
                ["📈", "Draw the story", "find the rainy-season dip"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up",
             "notes": "The hands-on block is the main event."},
            {"type": "cards", "title": "Every “Up NEPA!” is a data point", "cards": [
                ["🕐", "A time", "every hour, 00 to 23"],
                ["⚡", "A value", "light on (1) or off (0)"],
                ["📊", "= a time series", "values recorded in time order"]],
             "notes": "Ask how many hours of light they had yesterday. A time + a value in order = a time series."},
            {"type": "section", "kicker": "Part 1", "title": "Colab Bootcamp", "sub": "Your free Python computer inside Chrome",
             "notes": "Everyone opens Chrome and signs in to Google."},
            {"type": "flow", "title": "Your laptop shows the screen. Google's computer does the work", "steps": [
                ["💻", "Your laptop", "only needs Chrome"],
                ["☁️", "Google's computer", "Python + pandas ready"],
                ["📊", "Your answers", "tables and charts"]],
             "footer": "Like a cyber café computer, but free",
             "notes": "Nothing to install."},
            {"type": "cards", "title": "Colab's 3 golden rules", "cards": [
                ["💾", "1. Save a copy first", "File → Save a copy in Drive"],
                ["⬇️", "2. Top to bottom", "Run cells in order: Shift + Enter"],
                ["🔄", "3. Confused? Restart", "Runtime → Restart session and run all"]],
             "notes": "Make everyone do Rule 1 now."},
            {"type": "compare", "title": "NameError = “I don't remember”",
             "left": ["🧠", "Colab remembers", "Every variable you created, until a restart or a long idle"],
             "right": ["🧹", "After a restart", "Memory is wiped. Run STEP 0 and the cells above again"],
             "notes": "Demo it live."},
            {"type": "compare", "title": "The AI button: help yes, restricted data never",
             "left": ["🟢", "OK to paste", "Course training data (synthetic), your code, error messages"],
             "right": ["⛔", "Never paste", "Real NIGCOMSAT telemetry, RF records, network logs, customer data"],
             "notes": "If unsure, describe the shape of the data instead of pasting it."},
            {"type": "section", "kicker": "Part 2", "title": "What is a time series?", "sub": "One idea that unlocks the whole course",
             "notes": "Section break."},
            {"type": "twochart", "title": "Order carries the information",
             "left": {"label": "In time order: the rainy-season dip is visible", "labels": labels, "values": monthly.round(2).tolist()},
             "right": {"label": "Same 36 numbers, shuffled: no story", "labels": [str(i + 1) for i in range(len(shuffled))], "values": np.round(shuffled, 2).tolist()},
             "notes": "Same numbers, no story. That is the definition of a time series."},
            {"type": "cards", "title": "Every time series has 3 things", "cards": [
                ["🕐", "A timestamp", "when it happened"],
                ["🔢", "A value", "what was measured"],
                ["🥁", "A cadence", "hourly · daily · weekly · monthly"]],
             "notes": "Timestamp, value, cadence."},
            {"type": "stats", "title": "Meet NigComSat-1R", "sub": "Nigeria's communications satellite at 42.5° East",
             "stats": [["28", "active transponders"], ["≈36,000 km", "above the Earth"], ["C·Ku·Ka·L", "frequency bands"], ["15 yrs", "design life (launched 2011)"]],
             "notes": "Course data is synthetic but built to behave like this satellite."},
            {"type": "chart", "title": "Today's data: Ka-band availability, monthly average",
             "labels": labels, "values": monthly.round(2).tolist(), "ymin": 97.5, "ymax": 100.2,
             "caption": "1,096 daily rows · dips every rainy season (Ka-band rain fade)",
             "notes": "Point at the dips. Same reason DStv freezes in heavy rain."},
            {"type": "code", "title": "The 3-line pandas recipe",
             "code": 'ka = pd.read_csv(data_path("ka_band_availability_daily"),\n                 parse_dates=["timestamp"],   # text -> dates\n                 index_col="timestamp")       # time = row label\nka = ka.asfreq("D")                           # gaps show up as NaN',
             "caption": ".asfreq() makes missing days appear instead of silently disappearing",
             "notes": "Walk through each line."},
            {"type": "cards5", "title": "Inspect new data like a tokunbo car", "cards": [
                ["🔢", "Rows?"], ["📅", "Range?"], ["🕳️", "Gaps?"], ["👯", "Duplicates?"], ["❓", "Missing?"]],
             "notes": "The five profiling questions."},
            {"type": "compare", "title": "Satellites speak UTC. Lagos speaks WAT",
             "left": ["🛰️", "21:00 UTC", "telemetry: eclipse time"],
             "right": ["🇳🇬", "22:00 WAT", "Lagos/Abuja: UTC + 1, no daylight saving"],
             "notes": "Convert to one time zone before joining tables."},
            {"type": "cards4", "title": "The 4 characters in every series", "cards": [
                ["📈", "Trend", "the long direction"],
                ["🌧️", "Seasonality", "fixed calendar repeat"],
                ["🎢", "Cycle", "ups and downs, no fixed length"],
                ["🎲", "Noise", "random wobble: don't react"]],
             "notes": "Seasonality has a fixed calendar; a cycle does not."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W1D1-exercise in Colab", "File → Save a copy in Drive", "Run STEP 0, then top to bottom",
                "Replace every ___, run, get the green tick"],
             "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["💾", "Colab: save a copy, run top to bottom, restart when confused"],
                ["⏱️", "Time series: order matters (timestamp + value + cadence)"],
                ["📏", "Recipe: parse_dates → index_col → .asfreq()"]],
             "next": "Next: Charts That Don't Lie",
             "notes": "Tease Day 2."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
def _ka():
    return pd.read_csv(data_path("ka_band_availability_daily"), parse_dates=["timestamp"], index_col="timestamp").asfreq("D")

def _c_a2(x):
    return int(x) == 8760, "8,760 hours in a year. That is how many rows an hourly sensor makes every year!", "24 hours × 365 days."

def _c_b1(x):
    return str(x).strip().lower() in {"text", "string", "str", "object"}, \
        "Correct: pandas read the dates as plain TEXT. It does not yet know they are dates.", \
        "Look at the dtype printed next to timestamp. Is it a number, a date, or text?"

def _c_b2(x):
    return x == "timestamp", "Yes! The time column is called \"timestamp\".", \
        "Look at the column names in the table above. Remember the quotes: \"...\""

def _c_b3(x):
    return int(x) == len(_ka()), f"{len(_ka()):,} days. Three full years (2024 was a leap year: 365 + 366 + 365).", \
        "Use len(ka) to count the rows."

def _c_b4(x):
    k = _ka(); first, last = pd.Timestamp(x[0]), pd.Timestamp(x[1])
    return (first == k.index.min()) and (last == k.index.max()), \
        f"From {k.index.min().date()} to {k.index.max().date()}.", "Try ka.index.min() and ka.index.max()."

def _c_b5(x):
    return int(x) == 3, "3 missing days found! Without .asfreq() they were invisible.", \
        "After .asfreq(\"D\"), count the empty values with .isna().sum()."

def _c_b6(x):
    t = pd.Timestamp(x)
    return t == _ka()["availability_pct"].idxmin(), \
        f"{t.date()}: in July, right in the rainy season. That's Ka-band rain fade. 🌧️", \
        "Use ka[\"availability_pct\"].idxmin(): it returns the DATE of the smallest value."

def _c_b7(x):
    return isinstance(x, str) and len(x.strip()) >= 15 and x.strip().lower() not in {"my chart", "chart", "title"}, \
        "Nice: a title that states a finding beats a title that just names the data.", \
        "Write a sentence of at least 15 characters that says what the chart SHOWS."

def _c_b8(x):
    return str(x).strip().lower() in {"august", "aug", "8"}, "August! Peak rainy season = lowest availability.", \
        "Find the month with the lowest bar in the monthly chart."

def _c_b9(x):
    want = ("seasonality", "trend", "noise", "cycle")
    got = tuple(str(v).strip().lower() for v in x)
    wrong = [i + 1 for i, (g, w) in enumerate(zip(got, want)) if g != w]
    return not wrong, "All four correct. You can now name the 4 characters in any series.", \
        f"Check statement(s) {wrong}. Choose from: trend, seasonality, cycle, noise."

def _c_b10(x):
    return int(x) == 22, "22:00 in Lagos (WAT = UTC + 1). The eclipse happens around Nollywood-movie time. 🎬", \
        "WAT is UTC plus ONE hour."

def _c_bonus(x):
    return str(x).strip().lower() == "sunday", "Sunday! Even faults rest on Sunday. You'll use this on Day 3. 😄", \
        "Look at the averages by day name. Which is smallest?"

CHECKS = {"A2": _c_a2, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4, "B5": _c_b5, "B6": _c_b6,
          "B7": _c_b7, "B8": _c_b8, "B9": _c_b9, "B10": _c_b10, "BONUS": _c_bonus}
HINTS = {"B4": "Give two dates, e.g. first_day = ka.index.min()", "B6": "idxmin() gives the date of the minimum."}
'''


def notebook_cells(setup_code):
    return [
        ("md", f"""# 🛰️ Week 1 · Day 1: Colab Bootcamp + Your First Time Series

**Today:** learn to drive Google Colab, then load three years of Ka-band link data and find the rainy season *yourself*.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then press **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**
> If you skip this, your work disappears when you close the tab. Your copy opens in a new tab: work there.

**Rule book:** keep `W1D1-rulebook.pdf` open next to you. It lists every step and every common error with its fix."""),
        ("md", """## ▶️ STEP 0: Set up (run this once, every time you open the notebook)

Click the cell below and press **Shift + Enter** (or click the ▶ on its left). It prepares Python and the answer checker.
You should see `✅ Ready!`. If Colab warns *"This notebook was not authored by Google"*, click **Run anyway**: that's normal."""),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Colab warm-up (15 min) 💻

### A1 ▶️ Your first cell
Click the cell below and press **Shift + Enter**. Then change the message to include your name and run it again."""),
        ("code", 'print("Hello from NIGCOMSAT! 🛰️")'),
        ("md", """### A2 ✍️ Colab is a calculator too
An **hourly** sensor sends one reading every hour. How many readings does it send in one (non-leap) year?
Replace `___` with a Python calculation (hint: hours in a day × days in a year)."""),
        ("task", 'hours_in_year = ___\n\ncheck("A2", hours_in_year)', 'hours_in_year = 24 * 365\n\ncheck("A2", hours_in_year)'),
        ("md", """### A3 🧠 Colab's short memory (try it!)
1. Run the cell below: it prints `hours_in_year`.
2. Now go to the menu **Runtime → Restart session**, click **Yes**.
3. Run the cell below again. You get a **`NameError`**. That means *"I forgot. Run the cells above again."*
4. Fix it: run **STEP 0** and **A2** again, then this cell. ✅

> 💡 **Remember:** after every restart, run STEP 0 first."""),
        ("code", "print(hours_in_year)"),
        ("md", """### A4 📖 Text cells
This cell is a **text cell**. Double-click it to see how it's written, then press **Shift + Enter** to make it pretty again.
Try it: double-click here and add your name after the arrow 👉

### A5 📖 Where the files live
Click the **📁 folder icon** on the left edge of Colab. That's the *Files panel*. The data files you download today will appear there.
Want to use your own CSV later? Drag it into the Files panel (or click the upload icon). It disappears when the session ends, so keep the original on your laptop."""),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Your first time series (45 min) ⏱️

**The data:** `ka_band_availability_daily.csv`: for every day of 2023–2025, the percentage of the day the **Ka-band Nigeria spot beam** was working properly.
It's synthetic teaching data, built to behave like NigComSat-1R, so it's safe to use with AI tools.

### B1 ▶️ Load it the *naive* way and look
Run the cell. `head()` shows the first 5 rows; `dtypes` shows the TYPE pandas gave each column."""),
        ("code", 'ka_raw = pd.read_csv(data_path("ka_band_availability_daily"))\n\ndisplay(ka_raw.head())\nprint(ka_raw.dtypes)'),
        ("md", """✍️ Look at the type next to `timestamp`. Does pandas think it's a **date** or plain **text**? (`object` or `str` means text.)
Type `"date"` or `"text"` (with the quotes)."""),
        ("task", 'timestamp_type = ___\n\ncheck("B1", timestamp_type)', 'timestamp_type = "text"\n\ncheck("B1", timestamp_type)'),
        ("md", """### B2 ✍️ Teach pandas about time
Our 3-line recipe needs the **name of the time column**. Write it in quotes. The next cell uses it."""),
        ("task", 'TIME_COLUMN = ___\n\ncheck("B2", TIME_COLUMN)', 'TIME_COLUMN = "timestamp"\n\ncheck("B2", TIME_COLUMN)'),
        ("md", "▶️ Now the recipe: **parse_dates** (text → dates), **index_col** (time becomes the row label), **.asfreq(\"D\")** (one row per day, so gaps can't hide)."),
        ("code", 'assert TIME_COLUMN is not None, "✍️ Do B2 first: fill in TIME_COLUMN above, then run this cell again."\n\nka = pd.read_csv(data_path("ka_band_availability_daily"),\n                 parse_dates=[TIME_COLUMN],\n                 index_col=TIME_COLUMN)\nka = ka.asfreq("D")\n\nka.head()'),
        ("md", """### B3 ✍️ How many days of data?
`len(something)` counts rows."""),
        ("task", 'n_days = ___\n\ncheck("B3", n_days)', 'n_days = len(ka)\n\ncheck("B3", n_days)'),
        ("md", """### B4 ✍️ First and last day
The dates are now the **index**. `ka.index.min()` gives the earliest one. What gives the latest?"""),
        ("task", 'first_day = ___\nlast_day = ___\n\ncheck("B4", (first_day, last_day))',
         'first_day = ka.index.min()\nlast_day = ka.index.max()\n\ncheck("B4", (first_day, last_day))'),
        ("md", """### B5 ✍️ Catch the hidden gap 🕵🏾
Real exports lose rows. Below we **pretend** an export glitch deleted three days in March 2024.
`len()` says it's fine… but is it? Fill in the frequency code for **daily** (look at the recipe in B2!). The cell then re-declares the rhythm and counts the empty cells with `.isna().sum()`."""),
        ("code", 'broken = ka.drop(pd.to_datetime(["2024-03-06", "2024-03-07", "2024-03-08"]))\nprint("rows in the broken export:", len(broken), " <- looks normal, right?")'),
        ("task", 'FREQ = ___          # the code for "daily", in quotes\nfixed = broken.asfreq(FREQ) if FREQ else broken\nmissing_days = fixed["availability_pct"].isna().sum()\nprint("missing days revealed:", missing_days)\n\ncheck("B5", missing_days)',
         'FREQ = "D"          # the code for "daily", in quotes\nfixed = broken.asfreq(FREQ) if FREQ else broken\nmissing_days = fixed["availability_pct"].isna().sum()\nprint("missing days revealed:", missing_days)\n\ncheck("B5", missing_days)'),
        ("md", """### B6 ✍️ The worst day in three years
`.idxmin()` returns the **date** (the index) where a column is smallest. Find the worst day for `availability_pct`."""),
        ("task", 'worst_day = ___\n\nif worst_day is not None:\n    print(worst_day, "→", ka.loc[worst_day, "availability_pct"], "%")\ncheck("B6", worst_day)',
         'worst_day = ka["availability_pct"].idxmin()\n\nif worst_day is not None:\n    print(worst_day, "→", ka.loc[worst_day, "availability_pct"], "%")\ncheck("B6", worst_day)'),
        ("md", """### B7 ✍️ Draw it, with a title that tells the STORY
A bad title names the data (*"Availability"*). A good title states the finding (*"Availability dips every rainy season"*).
Run it first, look at the chart, then write your own title sentence."""),
        ("task", 'my_title = ___\n\nka["availability_pct"].plot(title=my_title, lw=1)\nplt.ylabel("% of day link was OK")\nplt.show()\n\ncheck("B7", my_title)',
         'my_title = "Ka-band availability dips every rainy season, worst in July–August"\n\nka["availability_pct"].plot(title=my_title, lw=1)\nplt.ylabel("% of day link was OK")\nplt.show()\n\ncheck("B7", my_title)'),
        ("md", """### B8 ✍️ Which month is worst on average?
▶️ Run the first cell: it averages each calendar month across the 3 years and draws a bar chart. Then answer with the month's **name**."""),
        ("code", 'by_month = ka["availability_pct"].groupby(ka.index.month).mean()\nby_month.index = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]\nby_month.plot(kind="bar", title="Average availability by calendar month (2023–2025)", ylim=(97.5, 100))\nplt.show()'),
        ("task", 'worst_month = ___\n\ncheck("B8", worst_month)', 'worst_month = "August"\n\ncheck("B8", worst_month)'),
        ("md", """### B9 ✍️ Name the character
Every series is built from **trend**, **seasonality**, **cycle** and **noise**. Which one is each statement?

1. Ka-band availability drops **every August** during the rainy season.
2. The VSAT network **keeps growing** year after year.
3. NOC tickets went from **38 last week to 41 this week**.
4. Capacity demand was strong for two years, weak for three, and is now rising again (**no fixed length**)."""),
        ("task", 's1 = ___\ns2 = ___\ns3 = ___\ns4 = ___\n\ncheck("B9", (s1, s2, s3, s4))',
         's1 = "seasonality"\ns2 = "trend"\ns3 = "noise"\ns4 = "cycle"\n\ncheck("B9", (s1, s2, s3, s4))'),
        ("md", """### B10 ✍️ Time zones
The satellite's eclipse happens at **21:00 UTC**. What hour is that on a Lagos clock (WAT = UTC + 1)? Give just the hour as a number."""),
        ("task", 'eclipse_hour_lagos = ___\n\ncheck("B10", eclipse_hour_lagos)', 'eclipse_hour_lagos = 22\n\ncheck("B10", eclipse_hour_lagos)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task (bonus): a new file, all by yourself
Load `noc_tickets_daily` (time column: `date`) using the same 3-line recipe, then average `tickets_raised` by **day name**.
Which day of the week has the **fewest** tickets? Type the day's name."""),
        ("task", '# load it here (copy the recipe from B2!)\ntk = ___\n\n# average by day name\n# tk.groupby(tk.index.day_name())["tickets_raised"].mean()\n\nquietest_day = ___\ncheck("BONUS", quietest_day)',
         'tk = pd.read_csv(data_path("noc_tickets_daily"), parse_dates=["date"], index_col="date").asfreq("D")\n\ndisplay(tk.groupby(tk.index.day_name())["tickets_raised"].mean().round(2).sort_values())\n\nquietest_day = "Sunday"\ncheck("BONUS", quietest_day)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard. Then **File → Save** (your copy is in Google Drive → *Colab Notebooks*)."""),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- **Colab:** save a copy, run top to bottom, restart when confused, run STEP 0 after every restart.
- **A time series** is a table where the **order of rows carries information**: timestamp + value + cadence.
- **The recipe:** `parse_dates` → `index_col` → `.asfreq()` so missing periods show up as `NaN` instead of hiding.
- **Inspect before you trust:** rows, range, gaps, duplicates, missing values.
- **The 4 characters:** trend, seasonality, cycle, noise.

**Next time:** *Charts That Don't Lie*: how a daily **average** hid a whole rain outage. 🌧️

<sub>Data: synthetic teaching datasets from the original Week 3 code book (`Time-series/week-03`). They are safe to use in AI assistants. Real NIGCOMSAT data is not.</sub>"""),
    ]
