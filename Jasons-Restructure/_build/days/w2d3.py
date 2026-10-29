"""Week 2 · Day 3: Lab Day + Quiz 1 + Pick Your Project."""
from __future__ import annotations

import csv
import random

import numpy as np
import pandas as pd

from common import BRAND as B, ORIGINALS, SUB
from svgcharts import line_svg
from webdeck import logos_title_block

CODE = "W2D3"
TITLE = "Lab Day + Quiz 1 + Pick Your Project"

D3 = ORIGINALS / "week-03" / "data"
PRACTICE_LINE = 97.0   # made-up alert level for the lab, in amp-hours


def _bat():
    return pd.read_csv(D3 / "battery_health_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def _qa_card(k, q, a, step, emoji):
    return (f'<div class="card anim" style="--d:{.2 + k * .15:.2f}s;padding:26px 30px">'
            f'<h3 style="font-size:28px;line-height:1.3"><span style="margin-right:10px">{emoji}</span>{q}</h3>'
            f'<div class="step" data-step="{step}" style="margin-top:14px;padding:14px 18px;border-radius:16px;'
            f'background:rgba(22,163,148,.16);font-size:25px;line-height:1.4;color:#DFF7F3">{a}</div></div>')


def web_slides():
    bat = _bat()
    cap = bat["est_capacity_ah"]
    ecl = bat["eclipse_minutes"]
    n = len(cap)

    def i_of(date):
        return int((pd.Timestamp(date) - cap.index[0]).days)

    xl = [(0, "Jan 2023"), (i_of("2024-01-01"), "Jan 2024"), (i_of("2025-01-01"), "Jan 2025"), (n - 1, "Dec 2025")]
    cap_svg = line_svg(cap.values, w=760, h=360, ymin=95.5, ymax=104,
                       yticks=[(96, "96"), (98, "98"), (100, "100"), (102, "102"), (104, "104 Ah")],
                       xlabels=xl, hline=(PRACTICE_LINE, "", B["bad"]), dur="2.6s",
                       extra=f'<text x="104" y="{300 - (PRACTICE_LINE - 95.5) / 8.5 * 270 - 12:.0f}" fill="{B["bad"]}" '
                             f'font-size="22" font-weight="700">practice alert line: 97 Ah</text>')
    ecl_svg = line_svg(ecl.values, w=580, h=360, ymin=0, ymax=80, color=B["gold"],
                       yticks=[(0, "0"), (40, "40"), (72, "72 min")], xlabels=[(0, "2023"), (n - 1, "2025")],
                       dur="2.6s", delay=".6s")

    recap1 = "".join([
        _qa_card(0, "You shuffle the rows of a daily series. Still a time series?",
                 "❌ No. The <b>order</b> carries the information. Shuffle it and the story is gone.", 1, "🔀"),
        _qa_card(1, "An export has 1,093 rows for 1,096 days. What makes the gaps show up?",
                 "<b class='mono'>.asfreq(\"D\")</b>: one slot per day, missing days appear as <b>NaN</b>.", 1, "🕳️"),
        _qa_card(2, "August: 11 days had a link-down hour. How many of those days had a daily MEAN below zero?",
                 "<b>Zero.</b> The lowest daily mean was 4.91 dB. Report SLAs from the <b>minimum</b>, not the mean.", 2, "📉"),
        _qa_card(3, "Weekend NOC tickets are about half of weekday tickets. Which window smooths that out?",
                 "<b>7 days</b>: weekends average 3.4 tickets vs 7.1 on weekdays (48%). One window = one full week.", 2, "🗓️"),
    ])
    recap2 = "".join([
        _qa_card(0, "Live monitoring dashboard: trailing or centred rolling window?",
                 "<b>Trailing.</b> A centred window peeks at readings from the future. That is “expo”. 🙅🏾", 1, "👀"),
        _qa_card(1, "Decomposing daily NOC tickets: which period?",
                 "<b>7</b>, because the working week sets it. The <b>process</b> picks the period, not a default.", 1, "🧩"),
        _qa_card(2, "Throughput correlogram: lag 1 = 0.58, lag 7 = 0.99. What does that tell you?",
                 "The pattern repeats <b>weekly</b>: “same weekday last week” is a very strong guess.", 2, "📊"),
        _qa_card(3, "Amplifier temperature and RF drive correlate 0.59. Does drive cause the heat?",
                 "Not proven: after differencing it falls to <b>0.40</b>. Much of it is <b>shared trend</b>. Correlation ≠ cause.", 2, "🧊"),
    ])

    roadmap = [("📥", "Load", "the right file + asfreq"), ("🔍", "Profile", "rows, gaps, duplicates"),
               ("📈", "Plot", "threshold + finding title"), ("〰️", "Smooth", "rolling window"),
               ("🧩", "Decompose", "pick the period"), ("📊", "ACF", "confirm the period"),
               ("📝", "Finding", "4 sentences")]
    road_html = "".join(
        f'<div class="card anim a-pop" style="--d:{.25 + k * .18:.2f}s;padding:22px 16px;text-align:center">'
        f'<div style="font-size:54px">{e}</div><div class="num" style="margin:10px auto 8px;width:44px;height:44px;font-size:22px">{k + 1}</div>'
        f'<h3 style="font-size:27px;margin-bottom:4px">{t}</h3><p class="small" style="font-size:19px">{s}</p></div>'
        for k, (e, t, s) in enumerate(roadmap))

    briefs = [("🛰️", "A. Telemetry anomalies", "“Which hours did the satellite behave strangely, and why?”"),
              ("🔋", "B. Battery & power ageing", "“When will the battery be too tired to carry us through eclipse?”"),
              ("🌧️", "C. RF link quality", "“Will the rain cut our signal tomorrow?”"),
              ("🛣️", "D. Capacity", "“When will the expressway be full?”"),
              ("📡", "E. Site downtime", "“Which VSAT sites will give us wahala next week?”")]
    brief_html = "".join(
        f'<div class="card anim a-pop" style="--d:{.25 + k * .2:.2f}s;padding:26px 22px"><div style="font-size:58px">{e}</div>'
        f'<h3 style="font-size:26px;margin-top:10px">{t}</h3><p style="font-size:22px;color:var(--muted)">{q}</p></div>'
        for k, (e, t, q) in enumerate(briefs))

    checkpoints = [("🎯", "Week 2 · Day 3", "Brief chosen", "TODAY"), ("📥", "Week 3 · Day 3", "Data in hand + profiled", ""),
                   ("🛠️", "Week 4 · Day 3", "Method drafted", ""), ("⚖️", "Week 5 · Day 3", "Honest test vs baseline", ""),
                   ("🎤", "Week 6 · Day 3", "Demo day", "")]
    cp_html = "".join(
        f'<div class="anim a-pop" style="--d:{.4 + k * .3:.2f}s;flex:1;text-align:center;position:relative;z-index:1">'
        f'<div style="width:118px;height:118px;border-radius:50%;margin:0 auto;display:flex;align-items:center;justify-content:center;'
        f'font-size:56px;background:{"#F5B83D" if tag else "#12233A"};border:3px solid {"#F5B83D" if tag else "#3B8BE0"};'
        f'box-shadow:{"0 0 34px rgba(245,184,61,.55)" if tag else "none"}">{e}</div>'
        f'<div class="kicker" style="margin:16px 0 6px;font-size:18px;color:{"#F5B83D" if tag else "var(--teal)"}">{w}</div>'
        f'<h3 style="font-size:26px">{t}</h3>{"<span class=pill style=margin-top:6px>⬅ today</span>" if tag else ""}</div>'
        for k, (e, w, t, tag) in enumerate(checkpoints))

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:40px;top:150px;width:560px;height:560px">
  <svg viewBox="0 0 560 560" width="560" height="560">
    <circle cx="280" cy="280" r="250" fill="none" stroke="#24384F" stroke-width="2" stroke-dasharray="6 10"/>
    <circle cx="280" cy="280" r="170" fill="none" stroke="#24384F" stroke-width="2" stroke-dasharray="4 8"/>
    <g class="spin" style="--t:26s;transform-origin:280px 280px"><text x="280" y="44" font-size="58" text-anchor="middle">🔬</text></g>
    <g class="spin" style="--t:18s;transform-origin:280px 280px"><text x="450" y="300" font-size="58" text-anchor="middle">📝</text></g>
    <g class="spin" style="--t:34s;transform-origin:280px 280px"><text x="110" y="300" font-size="58" text-anchor="middle">🎯</text></g>
    <text x="280" y="310" font-size="110" text-anchor="middle" class="floaty">🔋</text>
  </svg></div>
<div style="max-width:960px;margin-top:40px">
  <div class="kicker anim">Week 2 · Day 3</div>
  <h1 class="anim" style="--d:.2s">Lab Day<br><span class="hl">+ Quiz 1</span><br>+ Pick Your Project</h1>
  <p class="sub anim" style="--d:.5s;margin-top:26px">Two weeks of skills, one real investigation,<br>one quiz, and the start of <i>your</i> project. 🚀</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex;justify-content:flex-start">{logos_title_block()}</div>
</div>""",
          "Today is different: less new theory, more doing. Recap game, a lab where they drive, Quiz 1, then the final project starts."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Four moves today</h2>
<div class="grid4" style="margin-top:50px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center;padding:40px 24px"><div class="icon">🎮</div><h3>Recap game</h3><p class="small">8 sharp-sharp questions</p><span class="pill" style="margin-top:14px">15 min</span></div>
  <div class="card anim a-pop" style="--d:.55s;text-align:center;padding:40px 24px"><div class="icon">🔬</div><h3>Mini investigation</h3><p class="small">is our battery getting tired?</p><span class="pill teal" style="margin-top:14px">50 min</span></div>
  <div class="card anim a-pop" style="--d:.8s;text-align:center;padding:40px 24px"><div class="icon">📝</div><h3>Quiz 1</h3><p class="small">30 questions, just you</p><span class="pill gold" style="margin-top:14px">20 min</span></div>
  <div class="card anim a-pop" style="--d:1.05s;text-align:center;padding:40px 24px"><div class="icon">🎯</div><h3>Project kickoff</h3><p class="small">pick your brief</p><span class="pill" style="margin-top:14px">25 min</span></div>
</div>
<p class="anim" style="--d:1.4s;margin-top:44px;text-align:center">+ 10 minutes to wrap up. <b class="hl">No new theory today: today you drive.</b> 🚗</p>""",
          "Set expectations: this is a consolidation day. They should feel how much they already know."),

        # 3 ─ recap round 1
        S(f"""
<div class="kicker anim">🎮 Sharp-sharp recap · round 1</div>
<h2 class="anim" style="--d:.1s;font-size:54px;margin-bottom:22px">Shout the answer before I click!</h2>
<div class="grid2" style="gap:24px">{recap1}</div>""",
          "Read each question, let the room shout, then click to reveal (2 clicks per slide). The August numbers come from rf_link_quality_hourly: "
          "11 days had at least one hour below 0 dB, and every one of those days still had a positive daily mean (lowest 4.91 dB)."),

        # 4 ─ recap round 2
        S(f"""
<div class="kicker anim">🎮 Sharp-sharp recap · round 2</div>
<h2 class="anim" style="--d:.1s;font-size:54px;margin-bottom:22px">Second round. Faster!</h2>
<div class="grid2" style="gap:24px">{recap2}</div>""",
          "Correlation numbers are from the Week 3 twta_thermal_daily file: 0.59 raw, 0.40 after differencing. Honest wording: it drops, it does not vanish."),

        # 5 ─ the lab question
        S(f"""
<div class="kicker anim">🔬 Mini investigation · battery_health_daily (week-03 version)</div>
<h2 class="anim" style="--d:.1s;font-size:52px">Your oga asks: <span class="hl">“Is our battery getting tired?”</span> 🔋</h2>
<div class="row" style="gap:26px;margin-top:6px">
  <div class="card anim" style="--d:.2s;padding:18px 20px;flex:1.3"><p class="small">Estimated battery capacity (amp-hours), 3 years</p>{cap_svg}</div>
  <div class="card anim" style="--d:.4s;padding:18px 20px;flex:1"><p class="small">Eclipse minutes per day: count the humps 👀</p>{ecl_svg}</div>
</div>
<div class="row anim" style="--d:2.6s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill"><span class="count" data-to="1096" data-d="2.7">0</span> days</span>
  <span class="pill teal">capacity {cap.iloc[0]:.1f} → {cap.iloc[-1]:.1f} Ah</span>
  <span class="pill gold">97 Ah = made-up line for practice</span>
  <span class="small" style="margin-left:auto">real limits come from the spacecraft engineers</span>
</div>""",
          "This is the brief-B kind of question (power and battery ageing). The 97 Ah line is invented for practice, so say that clearly. "
          "Don't reveal the crossing date or the eclipse months: they discover them in the lab."),

        # 6 ─ roadmap
        S(f"""
<div class="kicker anim">The lab in 7 steps · 50 minutes</div>
<h2 class="anim" style="--d:.1s">Everything from Weeks 1–2, in one go</h2>
<div style="display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:16px;margin-top:26px">{road_html}</div>
<div class="row" style="gap:20px;margin-top:36px">
  <div class="card step" data-step="1" style="flex:1;border-color:#C98205"><h3>⚠️ The trap</h3><p class="muted" style="font-size:24px">This file exists in <b style="color:#fff">two</b> original folders. Week-03 is clean; week-04 has planted faults for later. Load the right one!</p></div>
  <div class="card step" data-step="1" style="flex:1"><h3>🧭 Less hand-holding</h3><p class="muted" style="font-size:24px">Fewer hints today. Use your <b style="color:#fff">rule books</b> and <b style="color:#fff">glossaries</b> from Days 1–5.</p></div>
</div>""",
          "The week-03 vs week-04 file trap is real: same file name, different content. The lab's first task makes them choose."),

        # 7 ─ the finding
        S("""
<div class="kicker anim">How to write it up</div>
<h2 class="anim" style="--d:.1s">The 4-sentence finding 📝</h2>
<div class="col" style="gap:16px;margin-top:10px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:24px;align-items:center;padding:22px 30px"><span class="num" style="background:#3B8BE0">S</span><p><b>Situation:</b> The NOC staffs every day of the week the same way.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:24px;align-items:center;padding:22px 30px"><span class="num" style="background:#16A394">O</span><p><b>Observation:</b> Weekends average <b class="hl">3.4</b> tickets a day vs <b class="hl">7.1</b> on weekdays (48%).</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:24px;align-items:center;padding:22px 30px"><span class="num" style="background:#C98205">I</span><p><b>Implication:</b> Weekend shifts carry about half the load of weekday shifts.</p></div>
  <div class="card anim a-left" style="--d:1.05s;display:flex;gap:24px;align-items:center;padding:22px 30px"><span class="num" style="background:#E5484D">R</span><p><b>Recommendation:</b> Trial a lighter weekend roster with one engineer on call.</p></div>
</div>
<p class="anim small" style="--d:1.4s;margin-top:18px;text-align:center">Example built from <span class="mono">noc_tickets_daily</span>. The <b>Observation</b> always carries a number.</p>""",
          "This is quiz question 12 and the final-project report format. The numbers are real: weekday mean 7.06, weekend mean 3.36."),

        # 8 ─ quiz
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">📝 Quiz 1 · Weeks 1–2</div>
  <h2 class="anim" style="--d:.1s">30 questions. 20 minutes. Just you.</h2>
  <div class="col" style="gap:14px;margin-top:16px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Phones face down, notebooks closed, <b>no AI button</b> 🙅🏾</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">2</span><p>Read the whole question. Don't hunt for patterns in the letters 😉</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">3</span><p>Not sure? Eliminate the silly options first</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">4</span><p>We mark it <b>together</b>: every wrong answer is a lesson</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;padding:36px 40px">
  <p class="small" style="margin-bottom:14px">6 questions on each topic</p>
  <div class="col" style="gap:10px;font-size:26px">
   <div>⏱️ What makes a time series</div><div>📈 Charts that don't lie</div><div>〰️ Rolling windows</div>
   <div>🧩 Decomposition</div><div>📊 Autocorrelation</div></div>
 </div>
</div>""",
          "Use the Google Forms CSV or the printed quiz from 2-exercise/quiz/. Answer key is in 4-instructor-only. It's for learning, not ranking."),

        # 9 ─ project: what
        S("""
<div class="kicker anim">🎯 Final project kickoff</div>
<h2 class="anim" style="--d:.1s">One real problem. Your unit's data. A tool they can open.</h2>
<div class="flow" style="margin-top:34px;justify-content:center">
  <div class="box on anim a-pop" style="--d:.3s;min-width:196px;padding:26px 14px"><div class="icon" style="font-size:52px">🎯</div><h3 style="font-size:24px">Choose</h3></div><div class="arrow anim a-fade" style="--d:.4s;width:40px"></div>
  <div class="box anim a-pop" style="--d:.5s;min-width:196px;padding:26px 14px"><div class="icon" style="font-size:52px">🔍</div><h3 style="font-size:24px">Understand</h3></div><div class="arrow anim a-fade" style="--d:.6s;width:40px"></div>
  <div class="box anim a-pop" style="--d:.7s;min-width:196px;padding:26px 14px"><div class="icon" style="font-size:52px">🛠️</div><h3 style="font-size:24px">Build</h3></div><div class="arrow anim a-fade" style="--d:.8s;width:40px"></div>
  <div class="box anim a-pop" style="--d:.9s;min-width:196px;padding:26px 14px"><div class="icon" style="font-size:52px">⚖️</div><h3 style="font-size:24px">Test honestly</h3></div><div class="arrow anim a-fade" style="--d:1s;width:40px"></div>
  <div class="box anim a-pop" style="--d:1.1s;min-width:196px;padding:26px 14px"><div class="icon" style="font-size:52px">🚀</div><h3 style="font-size:24px">Deploy</h3></div><div class="arrow anim a-fade" style="--d:1.2s;width:40px"></div>
  <div class="box anim a-pop" style="--d:1.3s;min-width:196px;padding:26px 14px"><div class="icon" style="font-size:52px">🎤</div><h3 style="font-size:24px">Present</h3></div>
</div>
<div class="grid3" style="margin-top:40px">
  <div class="card step" data-step="1"><h3>👤 Individual</h3><p class="muted" style="font-size:24px">Your own project, your own unit.</p></div>
  <div class="card step" data-step="1"><h3>🏢 Real data</h3><p class="muted" style="font-size:24px">From a named process your unit really runs.</p></div>
  <div class="card step" data-step="1"><h3>📊 Working tool</h3><p class="muted" style="font-size:24px">A dashboard or daily report, on the training server.</p></div>
</div>""",
          "Requirements PDF: week-6/final-project/Final-Project-Requirements.pdf. Grading out of 100 points; honesty counts more than fancy models."),

        # 10 ─ briefs
        S(f"""
<div class="kicker anim">Choose ONE brief</div>
<h2 class="anim" style="--d:.1s">Five briefs, in plain Naija</h2>
<div class="grid5" style="margin-top:24px">{brief_html}</div>
<p class="anim" style="--d:1.5s;margin-top:34px;text-align:center">Your process doesn't fit exactly? You can <b class="hl">adapt a brief</b> with your unit head's OK. Say what you changed.</p>""",
          "A anomalies, B degradation, C RF prediction, D capacity, E site downtime. Today's battery lab is a mini version of brief B."),

        # 11 ─ how to choose
        S("""
<div class="kicker anim">How to choose</div>
<h2 class="anim" style="--d:.1s">Name a <span class="hl">process</span>, not a topic</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s;border-color:#E5484D"><div class="icon">❌</div><h3>Too vague</h3>
    <p class="muted">“Satellite data”<br>“Network performance”<br>“Something with AI”</p></div>
  <div class="card anim a-right" style="--d:.55s;border-color:#1E9E5A"><div class="icon">✅</div><h3>A named process with an owner</h3>
    <p class="muted">“The weekly battery-health review on the bus subsystem”<br>“VSAT site fault escalation in the NOC”</p></div>
</div>
<div class="row" style="gap:18px;margin-top:30px;justify-content:center">
  <span class="pill step" data-step="1">1 · Is it in <b>my</b> unit?</span>
  <span class="pill teal step" data-step="1">2 · Can I get the <b>data</b>?</span>
  <span class="pill gold step" data-step="1">3 · Does someone <b>own</b> the process?</span>
</div>""",
          "Three yes answers = a good project. If any answer is no, pick another process."),

        # 12 ─ data rules
        S("""
<div class="kicker anim">The data rules · read them twice</div>
<h2 class="anim" style="--d:.1s">Real data. Real care.</h2>
<div class="grid3" style="margin-top:26px">
  <div class="card anim a-pop" style="--d:.3s;border-color:#E5484D"><div class="icon">🏢</div><h3>Stays inside NIGCOMSAT</h3><p class="muted" style="font-size:24px">Colab runs on Google's servers. Real data does <b style="color:#fff">not</b> go there unless your unit head agrees in writing.</p></div>
  <div class="card anim a-pop" style="--d:.55s;border-color:#E5484D"><div class="icon">🚫</div><h3>No raw data on GitHub</h3><p class="muted" style="font-size:24px">Commit your <b style="color:#fff">code</b>, never the export. Load data from a path in a config file.</p></div>
  <div class="card anim a-pop" style="--d:.8s;border-color:#E5484D"><div class="icon">🤖</div><h3>AI never sees it</h3><p class="muted" style="font-size:24px">Describe the <b style="color:#fff">shape</b> of your data. Never paste restricted data into any AI tool.</p></div>
</div>
<p class="anim" style="--d:1.2s;margin-top:34px;text-align:center"><b class="bad">Committing restricted data is a serious failure</b>, whatever the rest of the work looks like.</p>""",
          "Rule 2 of the requirements PDF: develop with real data on the training server or the work laptop, not in Colab."),

        # 13 ─ checkpoints
        S(f"""
<div class="kicker anim">The road to demo day</div>
<h2 class="anim" style="--d:.1s">Five checkpoints</h2>
<div style="position:relative;margin-top:60px">
  <svg style="position:absolute;left:0;top:52px" width="1420" height="20"><path class="draw" style="--dur:2.2s;--d:.3s" d="M140 10 L1280 10" stroke="#3B8BE0" stroke-width="5" stroke-linecap="round"/></svg>
  <div class="row" style="gap:10px">{cp_html}</div>
</div>
<div class="card glow anim" style="--d:2s;margin-top:50px;display:flex;gap:26px;align-items:center">
  <span style="font-size:60px">📧</span><p><b>Today's homework:</b> fill in the <b class="hl">project kickoff worksheet</b> and send the email to your unit head.
  Bring the reply to Week 3 · Day 3.</p></div>""",
          "Each checkpoint is a 15-minute slot at the end of that day. The email template is on the worksheet and in the requirements PDF."),

        # 14 ─ email
        S("""
<div class="kicker anim">Your homework, already half-written</div>
<h2 class="anim" style="--d:.1s">The email to your unit head ✉️</h2>
<div class="card anim" style="--d:.25s;background:#fff;color:#1f2a37;padding:40px 46px;font-size:29px;line-height:1.7;margin-top:10px">
  <div style="color:#5B6B7D;font-size:24px;border-bottom:1px solid #DCE4EC;padding-bottom:14px;margin-bottom:18px">
    <b>Subject:</b> Time-series training: final-project scope for approval</div>
  Dear <span class="step" data-step="1" style="background:#FFF1CC;padding:0 8px;border-radius:6px">[Name]</span>,<br>
  For my final project I'd like to build a small monitoring tool for <span class="step" data-step="1" style="background:#FFF1CC;padding:0 8px;border-radius:6px">[named process]</span>.<br>
  • <b>Brief:</b> <span class="step" data-step="2" style="background:#FFF1CC;padding:0 8px;border-radius:6px">[A–E]</span> &nbsp; • <b>Data:</b> <span class="step" data-step="2" style="background:#FFF1CC;padding:0 8px;border-radius:6px">[system, span, cadence]</span>, staying on NIGCOMSAT systems<br>
  • <b>Who it's for:</b> <span class="step" data-step="3" style="background:#FFF1CC;padding:0 8px;border-radius:6px">[team / role]</span> &nbsp; • <b>Output:</b> <span class="step" data-step="3" style="background:#FFF1CC;padding:0 8px;border-radius:6px">[dashboard / daily report]</span> on the training server<br>
  Could you confirm by replying to this email? Thank you.
</div>
<p class="anim small" style="--d:.8s;margin-top:20px;text-align:center">Full template: <span class="mono">W2D3-project-kickoff-worksheet.pdf</span> and the final-project requirements PDF.</p>""",
          "Click three times to light up the blanks. A reply email is enough as the unit head's agreement; it goes into the final submission."),

        # 15 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you did today</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🔬</span><p><b>Ran a full investigation:</b> load → profile → plot → smooth → decompose → ACF → finding.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">📝</span><p><b>Quiz 1 done:</b> Weeks 1–2 checked. Every wrong answer is tomorrow's strength.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🎯</span><p><b>Project started:</b> brief picked, process named, email to your unit head on its way.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:40px">Next week 👉 <b class="hl">Alarms That Cry Wolf</b>: when is a reading actually <i>wrong</i>? 🚨</p>""",
          "Close Week 2. Week 3 starts anomaly detection on the bus-power telemetry."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    bat = _bat()
    m = bat["est_capacity_ah"].resample("MS").mean()
    labels = [d.strftime("%b %y") if d.month in (1, 4, 7, 10) else "" for d in m.index]
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🔋", "kicker": "Week 2 · Day 3", "title": "Lab Day + Quiz 1 + Pick Your Project",
             "sub": "One real investigation, one quiz, and the start of your final project",
             "notes": "Consolidation day: recap game, lab, Quiz 1, project kickoff."},
            {"type": "cards4", "title": "Today's mission: four moves", "cards": [
                ["🎮", "Recap game", "8 quick questions · 15 min"],
                ["🔬", "Mini investigation", "is our battery getting tired? · 50 min"],
                ["📝", "Quiz 1", "30 questions, just you · 20 min"],
                ["🎯", "Project kickoff", "pick your brief · 25 min"]],
             "notes": "Plus 10 minutes to wrap up."},
            {"type": "table", "title": "Sharp-sharp recap: Weeks 1–2", "colW": [6.2, 5.93],
             "header": ["Question", "Answer"],
             "rows": [
                 ["Shuffle the rows of a series: still a time series?", "No: the order carries the information"],
                 ["1,093 rows for 1,096 days: what reveals the gaps?", ".asfreq(\"D\"): missing days appear as NaN"],
                 ["11 August days had a link-down hour. How many had a negative daily mean?", "Zero. Report SLAs from the minimum"],
                 ["Weekend tickets ≈ half of weekday. Which window?", "7 days: one full week"],
                 ["Live dashboard: trailing or centred window?", "Trailing: centred peeks at the future"],
                 ["Decompose daily NOC tickets: which period?", "7: the working week sets it"],
                 ["Lag 1 = 0.58, lag 7 = 0.99. Meaning?", "Weekly repeat: same weekday last week"],
                 ["Temperature vs drive: 0.59. Cause?", "Not proven: 0.40 after differencing (shared trend)"]],
             "notes": "Ask first, then reveal. Numbers come from the Week 3 data files."},
            {"type": "chart", "title": "The lab: is our battery getting tired?",
             "labels": labels, "ymin": 95, "ymax": 104, "fmt": "0", "series": [
                 {"name": "capacity (Ah, monthly mean)", "values": m.round(2).tolist(), "color": "0A5DB4"},
                 {"name": "practice alert line (97 Ah, made up)", "values": [PRACTICE_LINE] * len(m), "color": "E5484D"}],
             "notes": "battery_health_daily, week-03 version. 97 Ah is a made-up line for practice."},
            {"type": "table", "title": "The lab in 7 steps", "colW": [0.9, 3.0, 8.23],
             "header": ["#", "Step", "The tool"],
             "rows": [["1", "Load", "the week-03 file, parse_dates, index_col, .asfreq(\"D\")"],
                      ["2", "Profile", "rows, empty cells, duplicate timestamps"],
                      ["3", "Plot", "threshold line + a title that states a finding"],
                      ["4", "Smooth", "a trailing rolling window long enough to swallow the eclipse pattern"],
                      ["5", "Decompose", "seasonal_decompose with a period the process justifies"],
                      ["6", "ACF", "the correlogram confirms the period"],
                      ["7", "Finding", "Situation · Observation · Implication · Recommendation"]],
             "notes": "Warn about the trap: the same file name exists in week-03 and week-04."},
            {"type": "table", "title": "The 4-sentence finding", "colW": [2.6, 9.53],
             "header": ["Sentence", "Example (from noc_tickets_daily)"],
             "rows": [["Situation", "The NOC staffs every day of the week the same way."],
                      ["Observation", "Weekends average 3.4 tickets a day vs 7.1 on weekdays (48%)."],
                      ["Implication", "Weekend shifts carry about half the load of weekday shifts."],
                      ["Recommendation", "Trial a lighter weekend roster with one engineer on call."]],
             "caption": "The Observation always carries a number",
             "notes": "Same format as the final-project report."},
            {"type": "statement", "title": "Quiz 1: Weeks 1–2", "icon": "📝",
             "big": "30 questions · 20 minutes · just you",
             "sub": "Phones down, notebooks closed, no AI button. We mark it together.",
             "notes": "Google Forms CSV and printable quiz are in 2-exercise/quiz/."},
            {"type": "section", "kicker": "Final project", "title": "Pick Your Project",
             "sub": "One real problem · your unit's data · a tool they can open", "notes": "Kickoff."},
            {"type": "cards5", "title": "Choose ONE brief", "cards": [
                ["🛰️", "A. Telemetry anomalies"], ["🔋", "B. Battery ageing"], ["🌧️", "C. RF link quality"],
                ["🛣️", "D. Capacity"], ["📡", "E. Site downtime"]],
             "notes": "Naija versions: strange satellite hours; tired battery; rain cutting signal; full expressway; VSAT sites giving wahala."},
            {"type": "compare", "title": "Name a process, not a topic",
             "left": ["❌", "Too vague", "“Satellite data”, “Network performance”, “Something with AI”"],
             "right": ["✅", "Named process + owner", "“The weekly battery-health review on the bus subsystem”"],
             "notes": "Three checks: my unit? data available? someone owns the process?"},
            {"type": "cards", "title": "The data rules", "cards": [
                ["🏢", "Stays in-house", "Real NIGCOMSAT data does not go into Colab without written OK"],
                ["🚫", "Code only on GitHub", "Commit code, never the raw export"],
                ["🤖", "AI never sees it", "Describe the shape, never paste restricted data"]],
             "notes": "Committing restricted data is a serious failure."},
            {"type": "table", "title": "Five checkpoints to demo day", "colW": [3.0, 2.8, 6.33],
             "header": ["When", "Checkpoint", "Bring"],
             "rows": [["Week 2 · Day 3 (today)", "Brief chosen", "Your brief, the named process, the draft email"],
                      ["Week 3 · Day 3", "Data in hand", "Unit head's reply + your data loaded and profiled"],
                      ["Week 4 · Day 3", "Method drafted", "First version of your method"],
                      ["Week 5 · Day 3", "Honest test", "Temporal split + baseline comparison table"],
                      ["Week 6 · Day 3", "Demo day", "Working tool, report, 5-minute demo"]],
             "notes": "Fifteen minutes at the end of each of those days."},
            {"type": "steps", "title": "Homework before Week 3 · Day 3", "icon": "📧", "steps": [
                "Fill in the project kickoff worksheet", "Name your process and its owner",
                "Send the email to your unit head", "Bring the reply to Week 3 · Day 3"],
             "notes": "Template is on the worksheet."},
            {"type": "recap", "title": "What you did today", "points": [
                ["🔬", "Ran a full investigation: load → profile → plot → smooth → decompose → ACF → finding"],
                ["📝", "Quiz 1 done: Weeks 1–2 checked"],
                ["🎯", "Project started: brief picked, process named, email on its way"]],
             "next": "Next week: Alarms That Cry Wolf", "notes": "Close Week 2."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
def _bat(week="week-03"):
    return pd.read_csv(data_path("battery_health_daily", week=week), parse_dates=["date"], index_col="date").asfreq("D")

_MONTHS = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
def _month_no(x):
    s = str(x).strip().lower()
    if s.isdigit():
        return int(s)
    return _MONTHS.index(s[:3]) + 1

def _c_l1(x):
    want = ("week-03", "date", "D")
    got = tuple(str(v).strip() for v in x)
    wrong = [n for n, g, w in zip(["WEEK", "TIME_COL", "FREQ"], got, want) if g != w]
    return not wrong, "Right file, right time column, right rhythm. The clean week-03 version is loaded. 🔋", \
        f"Check {wrong}. Week folder looks like \"week-03\", the time column is in head(), daily is \"D\"."

def _c_l2(x):
    b = _bat()
    want = (len(b), int(b.isna().sum().sum()), int(b.index.duplicated().sum()))
    return tuple(int(v) for v in x) == want, f"{want[0]:,} days, {want[1]} empty cells, {want[2]} duplicates. Clean data: rare in real life, enjoy it! 😄", \
        "len(bat), bat.isna().sum().sum(), bat.index.duplicated().sum()"

def _c_l3(x):
    b = _bat()
    want = b.index[b["est_capacity_ah"] < 97][0]
    return pd.Timestamp(x) == want, f"{want.date()}: right inside the September eclipse season. The battery works hardest then. 🌗", \
        "bat.index[bat[\"est_capacity_ah\"] < PRACTICE_LINE][0] gives the first date under the line."

def _c_l4(x):
    return isinstance(x, str) and len(x.strip()) >= 15 and x.strip().lower() not in {"capacity", "battery", "est_capacity_ah"}, \
        "A title with a finding. Your oga can read the answer without reading the chart. 👌🏾", \
        "Write a sentence (at least 15 characters) that says what the chart SHOWS."

def _c_l5(x):
    w = int(x)
    ok = 175 <= w <= 190 or 355 <= w <= 370
    return ok, f"{w} days swallows the eclipse pattern ({'half a year: one season to the next' if w < 300 else 'a full year: both seasons'}).", \
        "Eclipse seasons come about half a year apart. Pick a window of about half a year or a full year, in days."

def _c_l6(x):
    w = int(globals().get("WINDOW") or 365)
    r = _bat()["eod_voltage_v"].rolling(w).mean()
    want = round(float(r.dropna().iloc[0] - r.iloc[-1]), 3)
    return abs(float(x) - want) < 0.002, f"The smoothed voltage fell {want:.3f} V: that's the ageing, with the eclipse noise removed.", \
        "smooth.dropna().iloc[0] - smooth.iloc[-1]  (first full value minus the last value)"

def _c_l7(x):
    p = int(x)
    msg = {12: "12 = one calendar year. 36 months = 3 full cycles, the minimum to trust it.",
           6: "6 = half a year, one eclipse season to the next. The process justifies it!"}
    return p in msg, msg.get(p, ""), "Monthly data with a calendar-year pattern. How many months in a year? (Half a year also works.)"

def _c_l8(x):
    got = {_month_no(v) for v in x}
    return got == {3, 9}, "March and September: the equinoxes, when Earth's shadow crosses the orbit. Two eclipse seasons a year! 🌍🌗", \
        "Look at the seasonal bar chart: which TWO months stick up the most?"

def _c_l9(x):
    from statsmodels.tsa.stattools import acf
    m = _bat()["depth_of_discharge_pct"].resample("MS").mean()
    a = acf(m, nlags=18)
    want = int(np.argmax(a[2:]) + 2)
    return int(x) == want, f"Lag {want}: the pattern repeats every {want} months, twice a year. The correlogram confirmed the process. 🎯", \
        "Ignore lag 0 and lag 1. Which bar after that is the tallest?"

def _c_l10(x):
    parts = [str(v).strip() for v in x]
    short = [n for n, p in zip(["situation", "observation", "implication", "recommendation"], parts) if len(p) < 25]
    has_num = any(ch.isdigit() for ch in parts[1])
    ok = not short and has_num
    hint = (f"Make these longer (25+ characters each): {short}. " if short else "") + ("" if has_num else "Your OBSERVATION needs a number.")
    return ok, "Four solid sentences. That's the format your final-project report uses. 📝", hint

def _c_bonus(x):
    a, b = _bat("week-03"), _bat("week-04")
    d = (a["est_capacity_ah"] - b["est_capacity_ah"]).abs()
    want = d[d > 1e-9].index[0]
    return pd.Timestamp(x) == want, f"{want.date()}: from there the week-04 file fades faster (the planted fault for Week 3). Same name, different data! 🕵🏾", \
        "Subtract the two capacity columns, keep the rows where the difference isn't zero, take the first date."

CHECKS = {"L1": _c_l1, "L2": _c_l2, "L3": _c_l3, "L4": _c_l4, "L5": _c_l5, "L6": _c_l6, "L7": _c_l7,
          "L8": _c_l8, "L9": _c_l9, "L10": _c_l10, "BONUS": _c_bonus}
HINTS = {"L3": "Give a date, e.g. bat.index[...][0]", "L8": "Give two month names, e.g. (\"Jan\", \"Feb\")"}
'''


def notebook_cells(setup_code):
    return [
        ("md", """# 🔬 Week 2 · Day 3: Mini Investigation, *Is our battery getting tired?* 🔋

**The story:** you've just joined the power-subsystem desk. Your oga asks two questions:
1. *Is the battery ageing?*
2. *Does anything about it repeat, and how often?*

You have **three years of daily battery data** and **everything you learned in Weeks 1–2**. Less hand-holding today: you drive. 🚗

| Symbol | Means |
|---|---|
| ▶️ | Run the cell (**Shift + Enter**) |
| ✍️ | Your turn: replace every `___` |
| ✅ / ❌ | The check marks it, with a hint if needed |
| 🌶️ | Bonus for fast finishers |

> ## ⚠️ First: **File → Save a copy in Drive**

**Help:** `W2D3-rulebook.pdf`, plus your rule books and glossaries from Days 1–5."""),
        ("md", "## ▶️ STEP 0: Set up\nRun it and wait for `✅ Ready!`. (After any restart, run it again.)"),
        ("setup", setup_code),

        # ---------------- 1. LOAD & PROFILE ----------------
        ("md", """---
# 1 · Load and profile (10 min) 📥

⚠️ **The trap:** `battery_health_daily.csv` exists in **two** original folders. `week-03` is the clean version. `week-04` has faults planted on purpose for Week 3 of our course.
Today you want the **clean** one.

### L1 ✍️ Three settings
- `WEEK`: which folder? (`"week-03"` or `"week-04"`)
- `TIME_COL`: the name of the time column (peek at the CSV: it's a date per row)
- `FREQ`: the rhythm code for **daily**"""),
        ("task", 'WEEK = ___\nTIME_COL = ___\nFREQ = ___\n\ncheck("L1", (WEEK, TIME_COL, FREQ))',
         'WEEK = "week-03"\nTIME_COL = "date"\nFREQ = "D"\n\ncheck("L1", (WEEK, TIME_COL, FREQ))'),
        ("code", 'assert None not in (WEEK, TIME_COL, FREQ), "✍️ Do L1 first: fill in all three settings, then run this cell again."\n\n'
                 'bat = pd.read_csv(data_path("battery_health_daily", week=WEEK),\n'
                 '                  parse_dates=[TIME_COL], index_col=TIME_COL).asfreq(FREQ)\nbat.head()'),
        ("md", """| Column | In plain words |
|---|---|
| `eclipse_minutes` | how long the satellite sat in Earth's shadow that day (running on battery, like your inverter when NEPA takes light) |
| `depth_of_discharge_pct` | how far the battery was drained that day (%) |
| `eod_voltage_v` | battery voltage at the end of the drain (volts) |
| `est_capacity_ah` | how much charge the battery can still hold (amp-hours). **This is the “tiredness” number.** |
| `cycle_count` | total charge/discharge cycles so far |

### L2 ✍️ Profile it: the tokunbo-car inspection 🚗🔍
Three numbers: how many **rows**, how many **empty cells** in the whole table, how many **duplicate timestamps**."""),
        ("task", 'n_rows = ___\nn_missing = ___\nn_dups = ___\n\ncheck("L2", (n_rows, n_missing, n_dups))',
         'n_rows = len(bat)\nn_missing = bat.isna().sum().sum()\nn_dups = bat.index.duplicated().sum()\n\ncheck("L2", (n_rows, n_missing, n_dups))'),

        # ---------------- 2. HONEST PLOT ----------------
        ("md", """---
# 2 · An honest plot (10 min) 📈

Real limits come from the spacecraft engineers. For practice we use a **made-up alert line: 97 Ah**.

### L3 ✍️ When did capacity FIRST drop below the line?
Hint: filter the index where the capacity is below the line, then take the first one: `[0]`."""),
        ("task", 'PRACTICE_LINE = 97   # amp-hours, made up for practice\n\nfirst_below = ___\n\ncheck("L3", first_below)',
         'PRACTICE_LINE = 97   # amp-hours, made up for practice\n\nfirst_below = bat.index[bat["est_capacity_ah"] < PRACTICE_LINE][0]\n\ncheck("L3", first_below)'),
        ("md", "### L4 ✍️ Draw it with the line on the chart, and a title that states the finding\nRun it once to look, then write your title sentence."),
        ("task", 'my_title = ___\n\nbat["est_capacity_ah"].plot(title=my_title, lw=1.2)\nplt.axhline(PRACTICE_LINE, color="#E5484D", ls="--", label="practice alert line (97 Ah)")\nplt.ylabel("capacity (Ah)")\nplt.legend()\nplt.show()\n\ncheck("L4", my_title)',
         'my_title = "Battery capacity fades steadily and first dips below the 97 Ah practice line in late 2025"\n\nbat["est_capacity_ah"].plot(title=my_title, lw=1.2)\nplt.axhline(PRACTICE_LINE, color="#E5484D", ls="--", label="practice alert line (97 Ah)")\nplt.ylabel("capacity (Ah)")\nplt.legend()\nplt.show()\n\ncheck("L4", my_title)'),

        # ---------------- 3. SMOOTH ----------------
        ("md", """---
# 3 · Smooth it (10 min) 〰️

`eod_voltage_v` mixes two stories: **(1)** deep drains during eclipse seasons, and **(2)** slow ageing.
To see only the ageing, use a **trailing** rolling window long enough to swallow the eclipse pattern.

▶️ First, look at the raw voltage. How far apart are the dips?"""),
        ("code", 'bat["eod_voltage_v"].plot(title="End-of-discharge voltage: raw", lw=0.8)\nplt.ylabel("volts")\nplt.show()'),
        ("md", "### L5 ✍️ Choose the window, in days\nThe dips come about **half a year apart**. A window that covers a whole pattern cancels it out (like 7 days cancelled the weekend effect on Day 3)."),
        ("task", 'WINDOW = ___\n\ncheck("L5", WINDOW)', 'WINDOW = 365\n\ncheck("L5", WINDOW)'),
        ("code", 'assert WINDOW is not None, "✍️ Do L5 first: choose WINDOW, then run this cell again."\n\n'
                 'smooth = bat["eod_voltage_v"].rolling(WINDOW).mean()      # trailing: only looks backwards\n\n'
                 'bat["eod_voltage_v"].plot(lw=0.6, alpha=.5, label="raw")\nsmooth.plot(lw=2.5, label=f"{WINDOW}-day trailing mean")\n'
                 'plt.title("Smoothing removes the eclipse dips and leaves the ageing trend")\nplt.ylabel("volts")\nplt.legend()\nplt.show()'),
        ("md", "### L6 ✍️ How many volts did the smoothed line fall?\nFirst **full** smoothed value minus the **last** one. (The first `WINDOW - 1` values are `NaN`: `.dropna()` skips them.)"),
        ("task", 'voltage_drop = ___\nprint(f"smoothed voltage fell by {voltage_drop:.3f} V" if voltage_drop is not None else "")\n\ncheck("L6", voltage_drop)',
         'voltage_drop = smooth.dropna().iloc[0] - smooth.iloc[-1]\nprint(f"smoothed voltage fell by {voltage_drop:.3f} V" if voltage_drop is not None else "")\n\ncheck("L6", voltage_drop)'),

        # ---------------- 4. DECOMPOSE ----------------
        ("md", """---
# 4 · Take it apart (10 min) 🧩

We decompose the **monthly average depth of discharge**. Monthly data, and a pattern tied to the calendar year.

▶️ Make the monthly series:"""),
        ("code", 'monthly = bat["depth_of_discharge_pct"].resample("MS").mean()\nprint(len(monthly), "months")\nmonthly.plot(title="Monthly average depth of discharge (%)", marker="o")\nplt.show()'),
        ("md", "### L7 ✍️ Choose the period\nThe **process** decides, not a default. Think: how often does the calendar repeat for monthly data?"),
        ("task", 'PERIOD = ___\n\ncheck("L7", PERIOD)', 'PERIOD = 12\n\ncheck("L7", PERIOD)'),
        ("code", 'from statsmodels.tsa.seasonal import seasonal_decompose\n\n'
                 'assert PERIOD is not None and 2 <= int(PERIOD) <= 18, "✍️ Do L7 first: PERIOD must be a whole number between 2 and 18."\n\n'
                 'parts = seasonal_decompose(monthly, model="additive", period=int(PERIOD))\nparts.plot()\nplt.show()\n\n'
                 'season = parts.seasonal.groupby(parts.seasonal.index.month).mean()\n'
                 'season.index = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]\n'
                 'season.plot(kind="bar", title="Seasonal part: average by calendar month")\nplt.axhline(0, color="grey", lw=1)\nplt.show()'),
        ("md", "### L8 ✍️ Which TWO months stick up the most?\nGive two month names, e.g. `(\"Jan\", \"Feb\")`."),
        ("task", 'peak_months = ___\n\ncheck("L8", peak_months)', 'peak_months = ("Mar", "Sep")\n\ncheck("L8", peak_months)'),

        # ---------------- 5. ACF ----------------
        ("md", """---
# 5 · Confirm it with the correlogram (5 min) 📊

The decomposition *assumed* a period. The correlogram *measures* how often the pattern repeats. ▶️ Run it:"""),
        ("code", 'from statsmodels.graphics.tsaplots import plot_acf\nfrom statsmodels.tsa.stattools import acf\n\n'
                 'plot_acf(monthly, lags=18, title="Correlogram: monthly depth of discharge")\nplt.xlabel("lag (months)")\nplt.show()\n\n'
                 'print(pd.Series(acf(monthly, nlags=18), name="autocorrelation").round(2).to_string())'),
        ("md", "### L9 ✍️ Ignoring lag 0 and lag 1, which lag has the TALLEST bar?"),
        ("task", 'strongest_lag = ___\n\ncheck("L9", strongest_lag)', 'strongest_lag = 6\n\ncheck("L9", strongest_lag)'),

        # ---------------- 6. FINDING ----------------
        ("md", """---
# 6 · Write the finding (10 min) 📝

Four sentences, for your oga. The **Observation must contain a number** from your investigation.

| Sentence | Answers | Example (from NOC tickets) |
|---|---|---|
| **Situation** | What's going on? | The NOC staffs every day of the week the same way. |
| **Observation** | What did the data show? (a number!) | Weekends average 3.4 tickets a day vs 7.1 on weekdays. |
| **Implication** | So what? | Weekend shifts carry about half the load. |
| **Recommendation** | What should we do? | Trial a lighter weekend roster with one engineer on call. |

### L10 ✍️ Your turn, about the battery"""),
        ("task", 'situation = ___\nobservation = ___\nimplication = ___\nrecommendation = ___\n\ncheck("L10", (situation, observation, implication, recommendation))',
         'situation = "The power desk reviews battery health on the bus subsystem every week."\n'
         'observation = "Capacity fell from 103.3 Ah to 96.6 Ah in three years and first crossed the 97 Ah practice line during the September eclipse season."\n'
         'implication = "The battery is ageing steadily, and it works hardest twice a year when eclipse seasons drain it deepest."\n'
         'recommendation = "Track capacity monthly against an agreed limit and plan eclipse-season checks every March and September."\n\n'
         'check("L10", (situation, observation, implication, recommendation))'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: the twin-file trap
Load the **week-04** version of the same file. On what **date** does its `est_capacity_ah` first differ from the week-03 version?
*(Hint: subtract the two columns, keep the rows where the difference isn't zero, take the first date.)*"""),
        ("task", 'bat4 = ___   # load the week-04 version, same recipe as section 1\n\nfirst_diff = ___\ncheck("BONUS", first_diff)',
         'bat4 = pd.read_csv(data_path("battery_health_daily", week="week-04"), parse_dates=["date"], index_col="date").asfreq("D")\n\n'
         'gap = (bat["est_capacity_ah"] - bat4["est_capacity_ah"]).abs()\nfirst_diff = gap[gap > 0].index[0]\n'
         'print("last-day capacity: week-03", bat["est_capacity_ah"].iloc[-1], "Ah · week-04", bat4["est_capacity_ah"].iloc[-1], "Ah")\n'
         'check("BONUS", first_diff)'),
        ("md", "---\n## 🏁 Finish line\n▶️ Run the scoreboard, then **File → Save**."),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you practised today
- **Load the right file**, declare the rhythm, **profile** before you trust.
- **Honest plot:** threshold on the chart, finding in the title.
- **Smoothing:** a trailing window as long as the pattern cancels the pattern.
- **Decomposition:** the process picks the period. **The correlogram confirms it.**
- **The 4-sentence finding:** Situation · Observation (with a number) · Implication · Recommendation.

**Next week:** *Alarms That Cry Wolf*: when is a reading actually **wrong**? 🚨

<sub>Data: synthetic teaching data from the original Week 3 code book (`Time-series/week-03`). Safe for AI assistants; real NIGCOMSAT data is not.</sub>"""),
    ]


# =============================================================================
# EXTRAS: Quiz 1 (shuffled), answer key, project-kickoff worksheet
# =============================================================================
QUIZ_SEED = 2603
LETTERS = "ABCD"


def shuffled_quiz():
    """Week-3 MCQ with answer positions spread evenly. True/False stay True/False (original order)."""
    src = list(csv.DictReader(open(ORIGINALS / "MCQ" / "week-03-mcq.csv", encoding="utf-8")))
    rng = random.Random(QUIZ_SEED)
    mc = [i for i, r in enumerate(src) if len(r["options"].split("|")) == 4]
    targets = [0, 1, 2, 3] * (len(mc) // 4) + rng.sample([0, 1, 2, 3], len(mc) % 4)
    rng.shuffle(targets)
    tgt = dict(zip(mc, targets))
    out = []
    for i, r in enumerate(src):
        opts = r["options"].split("|")
        ans = r["answer"]
        assert ans in opts, r["question"]
        if i in tgt:
            others = [o for o in opts if o != ans]
            rng.shuffle(others)
            others.insert(tgt[i], ans)
            opts = others
        out.append({"number": i + 1, "topic": r["title"], "tests": r["description"], "type": r["type"],
                    "difficulty": r["difficulty"], "question": r["question"], "options": opts, "answer": ans,
                    "letter": LETTERS[opts.index(ans)]})
    return out


def extra(d, foot):
    import pdfdoc

    quiz = shuffled_quiz()
    qdir = d.folder / SUB["exercise"] / "quiz"
    qdir.mkdir(parents=True, exist_ok=True)

    # 1) CSV for Google Forms / quiz tools
    with open(qdir / f"{CODE}-quiz-1-google-forms.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["number", "question", "options", "answer", "topic", "type"])
        for q in quiz:
            w.writerow([q["number"], q["question"], "|".join(q["options"]), q["answer"], q["topic"], q["type"]])

    # 2) printable quiz (no answers)
    lines = ["# Quiz 1: Weeks 1–2", "",
             "**30 questions · 20 minutes · just you.** Phones face down, notebooks closed, no AI tools. "
             "Circle **one** letter per question. True/False questions have two options.", "",
             "Name: ______________________________ &nbsp;&nbsp; Unit: ______________________", ""]
    topic = None
    for q in quiz:
        if q["topic"] != topic:
            topic = q["topic"]
            lines += ["", f"## {topic[0].upper() + topic[1:]}", ""]
        lines.append(f"**{q['number']}.** {q['question']}")
        lines.append("")
        for k, o in enumerate(q["options"]):
            lines.append(f"- **{LETTERS[k]}.** {o}")
        lines.append("")
    qmd = qdir / f"{CODE}-quiz-1.md"
    qmd.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pdfdoc.md_to_pdf(qmd, qmd.with_suffix(".pdf"), kicker="Week 2 · Day 3 · Quiz 1", title="Quiz 1: Weeks 1–2",
                     subtitle="30 questions · 20 minutes · just you", foot=foot)

    # 3) answer key (instructor only)
    counts = {L: sum(q["letter"] == L for q in quiz if len(q["options"]) == 4) for L in LETTERS}
    tf = sum(len(q["options"]) == 2 for q in quiz)
    key = ["# Quiz 1 Answer Key", "",
           "> 🧑🏾‍🏫 **Instructor only.** Built from the original `Time-series/MCQ/week-03-mcq.csv` (unchanged). "
           f"Options were reshuffled with a fixed seed ({QUIZ_SEED}) so the correct letters are spread out: "
           f"multiple-choice answers sit at A ×{counts['A']}, B ×{counts['B']}, C ×{counts['C']}, D ×{counts['D']} "
           f"(in the original, 74% of all answers were option B). The {tf} True/False questions keep their original order.", "",
           "| # | Answer | Correct option | What it tests | Level |", "|---|---|---|---|---|"]
    for q in quiz:
        key.append(f"| {q['number']} | **{q['letter']}** | {q['answer']} | {q['tests']} | {q['difficulty']} |")
    key += ["", "## Marking it together (10 minutes)", "",
            "1. Read out the letters; everyone marks their own paper.",
            "2. Ask for hands up on each question. Any question that more than a third of the room got wrong, explain it again with the matching day's slide.",
            "3. Map each topic back to its day: structure → W1D1 · charts → W1D2 · rolling windows → W1D3 · decomposition → W2D1 · autocorrelation → W2D2.",
            "", "## Quick topic tally", "", "| Topic | Questions |", "|---|---|"]
    topics = {}
    for q in quiz:
        topics.setdefault(q["topic"], []).append(str(q["number"]))
    for t, nums in topics.items():
        key.append(f"| {t} | {', '.join(nums)} |")
    kmd = d.folder / SUB["instructor"] / f"{CODE}-quiz-1-answer-key.md"
    kmd.write_text("\n".join(key) + "\n", encoding="utf-8")
    pdfdoc.md_to_pdf(kmd, kmd.with_suffix(".pdf"), kicker="Week 2 · Day 3 · Instructor only", title="Quiz 1 Answer Key",
                     subtitle="Weeks 1–2 · shuffled version", foot=foot)

    # 4) project-kickoff worksheet
    wmd = d.folder / SUB["exercise"] / "project-kickoff" / f"{CODE}-project-kickoff-worksheet.md"
    wmd.parent.mkdir(parents=True, exist_ok=True)
    wmd.write_text(WORKSHEET, encoding="utf-8")
    pdfdoc.md_to_pdf(wmd, wmd.with_suffix(".pdf"), kicker="Week 2 · Day 3 · Final project", title="Project Kickoff Worksheet",
                     subtitle="Fill it in, then send the email to your unit head.", foot=foot)


WORKSHEET = """# Project Kickoff Worksheet

Fill this in **today**, then send the email in section 5. Bring your unit head's reply to **Week 3 · Day 3**.
Full rules and grading: `week-6/final-project/Final-Project-Requirements.pdf`.

## 1. Pick ONE brief

| ✔ | Brief | The question in Naija words |
|---|---|---|
| ☐ | **A. Telemetry anomaly detection** | “Which hours did the satellite behave strangely, and what was the cause?” |
| ☐ | **B. Power and battery degradation** | “When will the battery be too tired to carry us through eclipse?” |
| ☐ | **C. RF link-quality prediction** | “Will the rain cut our signal tomorrow?” |
| ☐ | **D. Carrier and capacity monitoring** | “When will the expressway be full?” |
| ☐ | **E. Site-downtime prediction** | “Which VSAT sites will give us wahala next week?” |

Adapting a brief? Write what you'd change (needs your unit head's OK):

______________________________________________________________________________

## 2. Name the process (not a topic)

<div class="box bad" markdown="1">
❌ Too vague: “satellite data”, “network performance”, “something with AI”
</div>
<div class="box good" markdown="1">
✅ A named process with an owner: “the weekly battery-health review on the bus subsystem”, “VSAT site fault escalation in the NOC”
</div>

| | Your answer |
|---|---|
| **My unit** | |
| **The named process** | |
| **Who owns it** (name / role) | |
| **Who will use my tool** | |
| **The question my tool answers** | |

## 3. The data

| | Your answer |
|---|---|
| **Source system / export** | |
| **What one row is** (e.g. one hour of one channel) | |
| **Time span available** (how many months/years) | |
| **Cadence** (hourly / daily / weekly / monthly) | |
| **Time zone of the timestamps** (UTC or WAT?) | |
| **Known gaps or problems** | |
| **Labels / ground truth?** (maintenance log, tickets, operator notes) | |

## 4. Data restrictions: tick every box

<ul class="check">
<li>I know which parts of this data are <b>restricted</b>.</li>
<li>Real data stays on <b>NIGCOMSAT systems</b> (training server or work laptop). It does not go into Colab without written agreement.</li>
<li>I will commit <b>code only</b> to GitHub, never the raw export.</li>
<li>I will <b>describe the shape</b> of the data to AI tools, never paste it.</li>
</ul>

## 5. The email to your unit head

> **Subject:** Time-series training: final-project scope for approval
>
> Dear __________________,
>
> For my final project in the NIGCOMSAT time-series programme, I'd like to build a small monitoring tool for **__________________________________________** (named process).
> - **Brief:** ____ (A–E)
> - **Data I'd use:** __________________ (system/export), __________________ (span), ____________ (cadence). It stays on NIGCOMSAT systems; nothing is uploaded to outside tools.
> - **Who it's for:** __________________________________
> - **Output:** a ☐ dashboard / ☐ daily report on the training server.
>
> Could you confirm by replying to this email? Thank you.

<ul class="check">
<li>Email sent</li>
<li>Reply received (keep it: it goes into your final submission)</li>
</ul>

## 6. My checkpoint plan

| Checkpoint | When | What I'll bring | Done |
|---|---|---|---|
| 🎯 Brief chosen | Week 2 · Day 3 | This worksheet + the draft email | ☐ |
| 📥 Data in hand | Week 3 · Day 3 | Unit head's reply + data loaded and profiled | ☐ |
| 🛠️ Method drafted | Week 4 · Day 3 | First version of my detector / forecast / trend-to-threshold | ☐ |
| ⚖️ Honest test | Week 5 · Day 3 | Temporal split + comparison with a simple baseline | ☐ |
| 🎤 Demo day | Week 6 · Day 3 | Working tool, 2–4 page report, 5-minute demo | ☐ |

> 💡 **Three yes answers = a good project:** Is it in *my* unit? Can I get the *data*? Does someone *own* the process?
"""
