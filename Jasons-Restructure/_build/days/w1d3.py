"""Week 1 · Day 3: Calm Down the Noise: Rolling Windows."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import BRAND as B, ORIGINALS
from svgcharts import bars_svg, lines_svg
from webdeck import logos_title_block

CODE = "W1D3"
TITLE = "Calm Down the Noise: Rolling Windows"

D3 = ORIGINALS / "week-03" / "data"
DAYS7 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SHORT7 = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
GREY = "#6F8399"


def _data():
    tk = pd.read_csv(D3 / "noc_tickets_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    tkw = pd.read_csv(D3 / "noc_tickets_weekly.csv", parse_dates=["week_start"], index_col="week_start")
    rf = pd.read_csv(D3 / "rf_link_quality_hourly.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    return tk, tkw, rf


def facts():
    """Every number used on the slides, computed from the data."""
    tk, tkw, rf = _data()
    s = tk["tickets_raised"]
    by_day = s.groupby(s.index.day_name()).mean().reindex(DAYS7)
    r3 = s.rolling(3).mean()
    r7 = s.rolling(7).mean()
    b3 = r3.groupby(s.index.day_name()).mean().reindex(DAYS7)
    b7 = r7.groupby(s.index.day_name()).mean().reindex(DAYS7)
    t30 = s.rolling(30).mean()
    c30 = s.rolling(30, center=True).mean()
    m = rf["link_margin_db"]
    q = tkw["tickets_raised"]
    p1 = tk["priority_1"]
    weekly = s.resample("W").sum()
    return dict(
        n=len(s), by_day=by_day, weekday=by_day.iloc[:5].mean(), weekend=by_day.iloc[5:].mean(),
        b3=b3, b7=b7, spread3=b3.max() - b3.min(), spread7=b7.max() - b7.min(),
        t30_peak=t30["2024"].idxmax(), c30_peak=c30["2024"].idxmax(),
        lag=(t30["2024"].idxmax() - c30["2024"].idxmax()).days,
        lag25=(t30["2025"].idxmax() - c30["2025"].idxmax()).days,
        raw_out=int((m < 0).sum()), smooth_out=int((m.rolling(24).mean() < 0).sum()),
        smooth_min=m.rolling(24).mean().min(), raw_min=m.min(),
        wmean=q.mean(), wsd=q.std(), wout=int(((q - q.mean()).abs() > 2 * q.std()).sum()),
        p1_zero=(p1 == 0).mean(), p1_mean=p1.mean(), p1_share=p1.sum() / s.sum(),
        n_weeks=len(weekly), last_week=int(weekly.iloc[-1]), first_week=int(weekly.iloc[0]),
    )


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


def _month_labels(idx, every=(1,), fmt="%b %y"):
    return [(i, d.strftime(fmt)) for i, d in enumerate(idx) if d.day == 1 and d.month in every]


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    tk, tkw, rf = _data()
    f = facts()
    s = tk["tickets_raised"]
    r7 = s.rolling(7).mean()

    # --- title: a noisy line calming down
    sl = s["2024-06-01":"2024-09-30"]
    title_svg = lines_svg(
        [dict(values=sl.values, color=GREY, stroke=2, dur="2s", delay=".2s"),
         dict(values=r7["2024-06-01":"2024-09-30"].values, color=B["gold"], stroke=6, dur="2.4s", delay="1.4s")],
        w=760, h=360, ymin=0, ymax=13, labels_right=False)

    # --- hook: tickets by day of week
    bd = f["by_day"]
    hook_bars = bars_svg(SHORT7, bd.values, w=960, h=380, ymax=8.6, highlight=(5, 6), fmt="{:.1f}")

    # --- sliding window over the first 14 days of the data
    first = s.iloc[:14]
    first_r7 = r7.iloc[:14]
    box = 82
    gap = 10
    pitch = box + gap
    vals_row = "".join(
        f'<div style="width:{box}px;height:{box}px;border-radius:14px;background:#12233A;border:2px solid #24384F;'
        f'display:flex;flex-direction:column;align-items:center;justify-content:center">'
        f'<span style="font-size:15px;color:#9DB0C6">{d.strftime("%a")}</span><b style="font-size:30px">{v}</b></div>'
        for d, v in first.items())
    mean_row = "".join(
        f'<div style="width:{box}px;height:56px;border-radius:12px;display:flex;align-items:center;justify-content:center;'
        f'font-size:22px;font-weight:800;{"color:#FF6B6F;border:2px dashed #FF6B6F" if np.isnan(v) else "color:#3a2600;background:#F5B83D"}">'
        f'{"NaN" if np.isnan(v) else f"{v:.1f}"}</div>'
        for v in first_r7.values)
    win_w = 7 * pitch - gap + 12
    slider_css = (
        "<style>@keyframes w1d3slide{0%,8%{transform:translateX(0)}"
        + "".join(f"{8 + k * 12}%,{14 + k * 12}%{{transform:translateX({k * pitch}px)}}" for k in range(1, 8))
        + "100%{transform:translateX(" + str(7 * pitch) + "px)}}"
        ".w1d3win{position:absolute;top:-6px;left:-6px;height:" + str(box + 12) + "px;width:" + str(win_w) + "px;border:4px solid #F5B83D;"
        "border-radius:18px;box-shadow:0 0 30px rgba(245,184,61,.5);animation:w1d3slide 9s ease-in-out infinite}"
        "body.print .w1d3win,body.shot .w1d3win{animation:none}</style>")

    # --- the real thing: 2 years raw vs 7-day
    idx = s.index
    xl = [(i, d.strftime("%b %y")) for i, d in enumerate(idx) if d.day == 1 and d.month in (1, 4, 7, 10)]
    rainy = [(int((pd.Timestamp(f"{y}-07-01") - idx[0]).days), int((pd.Timestamp(f"{y}-09-30") - idx[0]).days), B["gold"], .10, "🌧️ rainy season")
             for y in (2024, 2025)]
    big_svg = lines_svg(
        [dict(values=s.values, color="#4A5D73", stroke=1.4, dur="2.2s", delay=".2s"),
         dict(values=r7.values, color=B["blue_d"], stroke=4.5, dur="2.6s", delay="1.4s", label="7-day")],
        w=1420, h=440, ymin=0, ymax=13, xlabels=xl, yticks=[(0, "0"), (4, "4"), (8, "8"), (12, "12")],
        bands=rainy, max_points=800)

    # --- why 7: weekday spread for 3-day vs 7-day windows
    bars3 = bars_svg(SHORT7, f["b3"].values, w=660, h=330, ymax=8.2, color=B["bad"], fmt="{:.1f}")
    bars7 = bars_svg(SHORT7, f["b7"].values, w=660, h=330, ymax=8.2, color=B["teal_d"], fmt="{:.1f}")

    # --- 3 vs 7 vs 30 on the first half of 2024
    h1 = slice("2024-01-01", "2024-06-30")
    win_svg = lines_svg(
        [dict(values=s.rolling(3).mean()[h1].values, color=B["bad"], stroke=2.5, delay=".2s", label="3-day"),
         dict(values=s.rolling(7).mean()[h1].values, color=B["blue_d"], stroke=4, delay=".9s", label="7-day"),
         dict(values=s.rolling(30).mean()[h1].values, color=B["gold"], stroke=5, delay="1.6s", label="30-day")],
        w=1000, h=480, ymin=1, ymax=10, yticks=[(2, "2"), (5, "5"), (8, "8")], labels_right=False,
        xlabels=_month_labels(s[h1].index, every=range(1, 13), fmt="%b"))

    # --- trailing vs centred around the 2024 rainy-season peak
    t30 = s.rolling(30).mean()
    c30 = s.rolling(30, center=True).mean()
    pk = slice("2024-06-01", "2024-10-31")
    pidx = s[pk].index
    ti = int((f["t30_peak"] - pidx[0]).days)
    ci = int((f["c30_peak"] - pidx[0]).days)
    lag_svg = lines_svg(
        [dict(values=c30[pk].values, color=B["bad"], stroke=4, delay=".3s", label="centred"),
         dict(values=t30[pk].values, color=B["teal_d"], stroke=4, delay="1.1s", label="trailing")],
        w=1000, h=400, ymin=5, ymax=9.4, yticks=[(6, "6"), (7, "7"), (8, "8"), (9, "9")],
        xlabels=_month_labels(pidx, every=range(1, 13), fmt="%b"),
        markers=[(ci, float(c30[pk].iloc[ci]), "", B["bad"]), (ti, float(t30[pk].iloc[ti]), f"{f['lag']} days later", B["teal_d"])])

    # --- ewm: fast vs slow
    ew = slice("2024-06-01", "2024-08-31")
    ewm_svg = lines_svg(
        [dict(values=s[ew].values, color="#4A5D73", stroke=1.6, delay=".2s"),
         dict(values=s.ewm(alpha=0.5).mean()[ew].values, color=B["gold"], stroke=3.5, delay=".9s", label="α = 0.5"),
         dict(values=s.ewm(alpha=0.05).mean()[ew].values, color=B["blue_d"], stroke=5, delay="1.6s", label="α = 0.05")],
        w=900, h=420, ymin=0, ymax=13, yticks=[(0, "0"), (6, "6"), (12, "12")], labels_right=False,
        xlabels=_month_labels(s[ew].index, every=range(1, 13), fmt="%b"))

    # --- SLA: raw margin vs 24-hour smoothed
    m = rf["link_margin_db"]
    m24 = m.rolling(24).mean()
    sla_svg = lines_svg(
        [dict(values=m.values, color=B["bad"], stroke=1.8, delay=".2s", label="hourly"),
         dict(values=m24.values, color=B["teal_d"], stroke=4.5, delay="1.3s", label="24-h avg")],
        w=1420, h=400, ymin=-5, ymax=7, yticks=[(-4, "−4 dB"), (0, "0 dB"), (4, "4 dB")], labels_right=False,
        xlabels=[(i, d.strftime("%d %b")) for i, d in enumerate(m.index) if d.hour == 0 and d.day in (1, 8, 15, 22, 29)],
        hline=(0, "link DOWN below 0 dB", B["gold"]), max_points=800)

    # --- priority 1: 7 vs 30
    p1 = tk["priority_1"]
    p1_svg = lines_svg(
        [dict(values=p1.rolling(7).mean().values, color=B["bad"], stroke=2.5, delay=".3s", label="7-day"),
         dict(values=p1.rolling(30).mean().values, color=B["teal_d"], stroke=5, delay="1.2s", label="30-day")],
        w=900, h=360, ymin=0, ymax=2.2, yticks=[(0, "0"), (1, "1"), (2, "2")], max_points=800,
        xlabels=[(i, lab) for i, lab in xl if lab.startswith(("Jan", "Jul"))])

    # --- weekly noise band
    q = tkw["tickets_raised"]
    mu, sd = f["wmean"], f["wsd"]
    noise_svg = lines_svg(
        [dict(values=q.values, color=B["blue_d"], stroke=4, delay=".3s"),
         dict(values=[mu] * len(q), color=B["gold"], stroke=3, dash="10 8", delay="1.4s", label=f"mean {mu:.1f}"),
         dict(values=[mu + 2 * sd] * len(q), color=B["teal_d"], stroke=2, dash="4 8", delay="1.8s", label="+2 swings"),
         dict(values=[mu - 2 * sd] * len(q), color=B["teal_d"], stroke=2, dash="4 8", delay="1.8s", label="−2 swings")],
        w=1420, h=380, ymin=20, ymax=52, yticks=[(25, "25"), (35, "35"), (45, "45")],
        xlabels=[(i, d.strftime("%b")) for i, d in enumerate(q.index) if d.day <= 7 and d.month in (1, 4, 7, 10)],
        markers=[(int(np.argmax(q.values)), float(q.max()), f"{int(q.max())}: the only odd week", B["gold"])])

    # --- trailing vs centred timeline diagram
    def strip(centred: bool):
        """30 day-cells: trailing = 30 past days up to today; centred = 15 past + today marker + 15 future."""
        ks = range(-14, 16) if centred else range(-29, 1)
        cells = []
        for k in ks:
            bg = "#E5484D" if k > 0 else "#3B8BE0"
            cells.append(f'<div style="width:26px;height:54px;border-radius:6px;background:{bg}"></div>')
            if k == 0:
                cells.append('<div style="width:6px;height:78px;border-radius:3px;background:#F5B83D;margin:-12px 4px 0"></div>')
        return "".join(cells)

    slides = [
        # 1 ─ title
        S(f"""
<div class="anim a-fade" style="--d:.1s;position:absolute;right:30px;top:150px">{title_svg}</div>
<div style="max-width:820px;margin-top:40px">
  <div class="kicker anim">Week 1 · Day 3</div>
  <h1 class="anim" style="--d:.2s">Calm Down<br><span class="hl">the Noise</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Rolling windows: how to see the real story<br>inside a jumpy, wiggly series. 〰️ → ➖</p>
  <div class="anim" style="--d:.8s;margin-top:44px;display:flex;justify-content:flex-start">{logos_title_block()}</div>
</div>""",
          "Welcome back. Today we take the jumpy NOC ticket series and calm it down without lying about it. "
          "Ask: who has ever looked at a chart and thought 'this thing is just shaking up and down'?"),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Three moves</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:380px;padding:46px 34px"><div class="icon">📅</div><h3>Spot the rhythm</h3><p class="small">tickets drop every weekend</p></div>
  <div class="arrow anim a-fade" style="--d:.6s"></div>
  <div class="box on anim a-pop" style="--d:.8s;min-width:380px;padding:46px 34px"><div class="icon">🌊</div><h3>Smooth it</h3><p class="small">a 7-day rolling window</p></div>
  <div class="arrow anim a-fade" style="--d:1.1s"></div>
  <div class="box on anim a-pop" style="--d:1.3s;min-width:380px;padding:46px 34px"><div class="icon">🙈</div><h3>Know what it hides</h3><p class="small">lag, the future, and short outages</p></div>
</div>
<div class="row anim" style="--d:1.7s;margin-top:70px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up</span>
</div>""",
          "Three moves today. The third one is the most important: smoothing always hides something."),

        # 3 ─ hook
        S(f"""
<div class="kicker anim">Quick question</div>
<h2 class="anim" style="--d:.1s">Which day do faults take a rest? 😴</h2>
<div class="row" style="gap:40px;align-items:center;margin-top:6px">
  <div class="card anim" style="--d:.2s;padding:18px 20px">{hook_bars}
    <p class="small" style="margin-top:4px">Average NOC tickets per day, {f['n']} days of data</p></div>
  <div class="col" style="flex:1;gap:22px">
    <div class="card step" data-step="1" style="padding:18px 26px"><div class="stat" style="font-size:64px">{f['weekday']:.1f}</div><div class="stat-label">tickets on a weekday</div></div>
    <div class="card step" data-step="1" style="padding:18px 26px"><div class="stat hl" style="font-size:64px">{f['weekend']:.1f}</div><div class="stat-label">tickets on a weekend day</div></div>
    <p class="step" data-step="2" style="font-size:25px"><b class="hl">Even faults rest on Sunday.</b> Weekends ≈ <b>half</b> of weekdays. 😄</p>
  </div>
</div>""",
          f"Real numbers from noc_tickets_daily: weekday average {f['weekday']:.2f}, weekend {f['weekend']:.2f}. Sunday is the quietest day "
          f"({bd['Sunday']:.2f}). Ask: why? Fewer staff logging tickets, fewer business users. This weekly rhythm makes the daily chart zig-zag."),

        # 4 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">The moving average 🌊</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Average the last few days, then slide forward one day. Repeat.</p>""",
          "Section break.", cls="center"),

        # 5 ─ analogy
        S("""
<div class="kicker anim">You already do this</div>
<h2 class="anim" style="--d:.1s">“How much do I spend on fuel?” ⛽</h2>
<div class="grid3" style="margin-top:24px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">😱</div><h3>Look at one day</h3><p class="muted">Monday you filled the tank: ₦40,000. Tuesday: ₦0. Panic, then relief. Every day tells a different story.</p></div>
  <div class="card anim a-pop" style="--d:.6s"><div class="icon">🧮</div><h3>Average the last 7 days</h3><p class="muted">One big fill-up gets shared across the week. The number stops jumping.</p></div>
  <div class="card glow anim a-pop" style="--d:.9s"><div class="icon">➡️</div><h3>Slide it every day</h3><p class="muted">Tomorrow, drop the oldest day and add the newest. That's a <b style="color:#fff">rolling (moving) average</b>.</p></div>
</div>
<p class="anim" style="--d:1.3s;margin-top:38px;text-align:center">Same money. <b class="hl">Calmer story.</b></p>""",
          "Illustration only (naira amounts are made up). The point: one day is noisy, a 7-day average is calm, and it slides forward every day."),

        # 6 ─ sliding window
        S(f"""
{slider_css}
<div class="kicker anim">How it works</div>
<h2 class="anim" style="--d:.1s;font-size:54px">A 7-day window sliding over real tickets</h2>
<p class="small anim" style="--d:.2s">The first 14 days of <span class="mono">noc_tickets_daily</span></p>
<div class="anim" style="--d:.3s;position:relative;display:flex;gap:{gap}px;margin-top:26px">{vals_row}<div class="w1d3win"></div></div>
<div class="anim" style="--d:.6s;display:flex;gap:{gap}px;margin-top:22px">{mean_row}</div>
<pre class="code anim" style="--d:.8s;margin-top:30px;font-size:26px">tk["roll7"] = tk["tickets_raised"].rolling(7).mean()   # gold = 7-day average</pre>
<p class="anim" style="--d:1s;margin-top:18px;font-size:26px"><b class="bad">NaN</b> = not 7 days yet. A 7-day average genuinely doesn't exist until day 7.</p>""",
          "Let the animation run. The gold frame covers 7 days; its average is the gold box below. The first 6 days are NaN because a 7-day "
          "average genuinely doesn't exist until day 7. That's quiz question 16."),

        # 7 ─ the real thing
        S(f"""
<div class="kicker anim">The whole two years</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Grey = every day. Blue = the 7-day average.</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{big_svg}</div>
<div class="row anim" style="--d:2.8s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill">grey zig-zag = weekdays vs weekends</span><span class="pill teal">blue = the real level</span>
  <span class="pill gold">🌧️ busier every rainy season</span>
</div>""",
          "The grey line is unreadable: it zig-zags every week. The blue 7-day line shows the real story: the level climbs every rainy season "
          "(July to September) and calms down in the dry months."),

        # 8 ─ why 7
        S(f"""
<div class="kicker anim">Why 7, and not 3?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">7 days = every weekday exactly once</h2>
<div class="grid2" style="margin-top:10px">
  <div class="card anim a-left" style="--d:.2s;padding:20px 22px"><h3 class="bad">3-day window</h3><p class="small">average of the window, by day of week</p>{bars3}
    <p style="font-size:24px">Still jumps by <b class="bad">{f['spread3']:.1f}</b> tickets across the week</p></div>
  <div class="card glow anim a-right" style="--d:.5s;padding:20px 22px"><h3 class="teal">7-day window</h3><p class="small">average of the window, by day of week</p>{bars7}
    <p style="font-size:24px">Jumps by only <b class="teal">{f['spread7']:.2f}</b>: the weekend effect cancels</p></div>
</div>""",
          f"Quiz question 13. Every 7-day window contains exactly one Monday, one Tuesday ... one Sunday, so the weekend dip is always inside it. "
          f"A 3-day window sometimes contains the weekend and sometimes doesn't, so it still zig-zags (spread {f['spread3']:.2f} vs {f['spread7']:.3f})."),

        # 9 ─ choose the window
        S(f"""
<div class="kicker anim">Pick your window</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Short = jumpy. Long = calm but slow.</h2>
<div class="row" style="gap:30px;align-items:stretch">
  <div class="card anim" style="--d:.2s;padding:16px 18px">{win_svg}<p class="small">Tickets, Jan to Jun 2024</p></div>
  <div class="col" style="flex:1;gap:16px">
    <div class="card anim a-right" style="--d:.5s;padding:20px 24px"><h3 class="bad">3 days</h3><p class="small">still feels the weekend</p></div>
    <div class="card anim a-right" style="--d:.8s;padding:20px 24px"><h3 class="blue">7 days</h3><p class="small">removes the weekly rhythm: start here</p></div>
    <div class="card anim a-right" style="--d:1.1s;padding:20px 24px"><h3 class="hl">30 days</h3><p class="small">shows the season, reacts slowly</p></div>
  </div>
</div>""",
          "No window is 'correct'. The right window depends on the question. For daily tickets, 7 is the natural first choice."),

        # 10 ─ section 2
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">What smoothing costs 🙈</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Every smooth line pays for its calm with something. Know the price.</p>""",
          "Section break.", cls="center"),

        # 11 ─ trailing vs centred
        S(f"""
<div class="kicker anim">Where does the window sit?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Trailing looks back. Centred peeks at the future. 🔮</h2>
<div class="col" style="gap:26px;margin-top:16px">
  <div class="card anim a-left" style="--d:.3s;padding:24px 28px"><h3 class="teal">Trailing window (pandas default)</h3>
    <div style="display:flex;gap:6px;margin:14px 0;align-items:center">{strip(False)}<span style="font-size:22px;margin-left:12px" class="hl">◀ today</span></div>
    <p class="small">Uses only the past 30 days. Safe for live monitoring.</p></div>
  <div class="card anim a-right" style="--d:.7s;padding:24px 28px;border-color:#E5484D"><h3 class="bad">Centred window (<span class="mono">center=True</span>)</h3>
    <div style="display:flex;gap:6px;margin:14px 0;align-items:center">{strip(True)}<span style="font-size:22px;margin-left:12px"><span class="hl">gold = today</span><br><span class="bad">red = the future</span></span></div>
    <p class="small">Uses 15 days of the FUTURE. Fine for a report about last year. <b style="color:#FF9EA1">Never for live monitoring or forecasts.</b></p></div>
</div>""",
          "Quiz question 15. A centred window lines up beautifully with events because it cheats: it uses tomorrow's data. On the last day of your "
          "data a centred window has no value at all. In Week 5 this cheating has a name: leakage."),

        # 12 ─ the lag
        S(f"""
<div class="kicker anim">The price of the trailing window</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Safe, but about half a window late ⏳</h2>
<div class="row" style="gap:30px;align-items:center">
  <div class="card anim" style="--d:.2s;padding:16px 18px">{lag_svg}<p class="small">30-day average of tickets, rainy season 2024</p></div>
  <div class="col" style="flex:1;gap:18px">
    <div class="card anim a-pop" style="--d:2.4s"><div class="stat hl" style="font-size:72px;white-space:nowrap">{f['lag']} days</div><div class="stat-label">the trailing peak arrives after the centred one (2024 and 2025 alike)</div></div>
    <p class="anim" style="--d:2.8s;font-size:26px">30-day window → about <b>15 days</b> late. Bigger window, bigger delay.</p>
  </div>
</div>""",
          f"Quiz question 14. Trailing 30-day peak: {f['t30_peak'].date()}; centred peak: {f['c30_peak'].date()}: {f['lag']} days apart "
          f"(the same {f['lag25']}-day gap in 2025). That's roughly half the window. Like news that reaches the village two weeks after it happened."),

        # 13 ─ ewm
        S(f"""
<div class="kicker anim">Another way: exponential smoothing</div>
<h2 class="anim" style="--d:.1s;font-size:54px">.ewm(alpha) = how fast you believe news 📰</h2>
<div class="row" style="gap:30px;align-items:center">
  <div class="card anim" style="--d:.2s;padding:16px 18px">{ewm_svg}<p class="small">Tickets, Jun to Aug 2024</p></div>
  <div class="col" style="flex:1;gap:18px">
    <div class="card anim a-right" style="--d:.8s;padding:22px 26px"><h3 class="hl">High alpha (0.5)</h3><p class="small">believes today's gist immediately: follows the data closely, reacts fast</p></div>
    <div class="card anim a-right" style="--d:1.3s;padding:22px 26px"><h3 class="blue">Low alpha (0.05)</h3><p class="small">waits for confirmation: very smooth, reacts slowly</p></div>
    <pre class="code anim" style="--d:1.6s;font-size:22px;padding:16px 20px">s.ewm(alpha=0.5).mean()</pre>
  </div>
</div>""",
          "Quiz question 17. Exponential smoothing gives recent days more weight. High alpha = follows the data closely and reacts fast. "
          "Low alpha = smooth and slow. Unlike rolling(7) it has no NaN warm-up rows."),

        # 14 ─ SLA
        S(f"""
<div class="kicker anim">The most expensive mistake</div>
<h2 class="anim" style="--d:.1s;font-size:52px">Never report an SLA from a smoothed line 🚫</h2>
<div class="card anim" style="--d:.2s;padding:14px 16px">{sla_svg}</div>
<div class="row" style="margin-top:20px;gap:24px">
  <div class="card anim a-pop" style="--d:2.6s;flex:1;padding:18px 24px;border-color:#E5484D"><div class="stat bad" style="font-size:70px">{f['raw_out']} hours</div><div class="stat-label"><b class="bad">red hourly line</b>: the link was really DOWN</div></div>
  <div class="card anim a-pop" style="--d:3s;flex:1;padding:18px 24px"><div class="stat teal" style="font-size:70px">{f['smooth_out']} hours</div><div class="stat-label"><b class="teal">green 24-hour average</b>: never below {f['smooth_min']:.1f} dB</div></div>
</div>""",
          f"Quiz question 18. rf_link_quality_hourly: {f['raw_out']} hours with negative margin (link down; worst {f['raw_min']:.2f} dB). "
          f"The 24-hour rolling average never drops below {f['smooth_min']:.2f} dB, so every outage vanishes inside the average. "
          "Short outages hide in averages. SLAs come from the raw readings."),

        # 15 ─ sparse counts
        S(f"""
<div class="kicker anim">Small counts need wider windows</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Priority-1 tickets: rare and jumpy 🚨</h2>
<div class="row" style="gap:30px;align-items:center">
  <div class="card anim" style="--d:.2s;padding:16px 18px">{p1_svg}<p class="small">Priority-1 tickets per day, rolling average</p></div>
  <div class="col" style="flex:1;gap:16px">
    <div class="card anim a-pop" style="--d:.6s;padding:20px 24px"><div class="stat" style="font-size:66px">{f['p1_mean']:.1f}</div><div class="stat-label">P1 tickets on an average day</div></div>
    <div class="card anim a-pop" style="--d:.9s;padding:20px 24px"><div class="stat hl" style="font-size:66px">{f['p1_zero'] * 100:.0f}%</div><div class="stat-label">of days had zero P1 tickets</div></div>
  </div>
</div>
<p class="anim" style="--d:1.4s;margin-top:22px">With 0, 1 or 2 tickets a day, a 7-day line still jumps. The 30-day line shows the real level.</p>""",
          f"priority_1 averages {f['p1_mean']:.2f} per day, {f['p1_share'] * 100:.0f}% of all tickets, and {f['p1_zero'] * 100:.0f}% of days have none. "
          "When counts are this small, one extra ticket is a big jump, so use a wider window."),

        # 16 ─ resample vs rolling
        S(f"""
<div class="kicker anim">Two different questions</div>
<h2 class="anim" style="--d:.1s;font-size:54px"><span class="mono">.rolling(7)</span> vs <span class="mono">.resample("W")</span></h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🌊</div><h3>rolling(7).mean()</h3>
    <p class="muted">“What's the average of the <b style="color:#fff">last 7 days</b>, as of today?”</p>
    <p style="margin-top:12px"><span class="pill">one value per DAY</span><span class="pill teal">{f['n']} rows</span></p></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">🪣</div><h3>resample("W").sum()</h3>
    <p class="muted">“How many tickets in <b style="color:#fff">each calendar week</b>?” Days go into weekly buckets.</p>
    <p style="margin-top:12px"><span class="pill">one value per WEEK</span><span class="pill teal">{f['n_weeks']} rows</span></p></div>
</div>
<p class="step" data-step="1" style="margin-top:30px;text-align:center">⚠️ Watch the edges: the last bucket holds only 2 days, so it shows <b class="bad">{f['last_week']}</b> tickets. It's not a quiet week, just an incomplete one.</p>""",
          f"Rolling slides: one value per day. Resample buckets: one value per week ({f['n_weeks']} weekly rows). The last weekly bucket only has "
          f"2 days in it ({f['last_week']} tickets), so always check partial periods at the edges."),

        # 17 ─ noise
        S(f"""
<div class="kicker anim">Noise: don't call a meeting for it</div>
<h2 class="anim" style="--d:.1s;font-size:54px">38 vs 41 tickets = the same week twice</h2>
<div class="card anim" style="--d:.2s;padding:14px 16px">{noise_svg}</div>
<div class="row anim" style="--d:2.4s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill">noc_tickets_weekly · 52 weeks</span><span class="pill gold">mean {mu:.1f} tickets/week</span>
  <span class="pill teal">typical swing ± {sd:.0f}</span><span class="pill bad">only {f['wout']} odd week of 52</span>
</div>""",
          f"The weekly file has already removed the weekend effect. What's left is mostly noise around a mean of {mu:.1f} (the original code book "
          f"says 'about 38'; the data says {mu:.1f}). Typical swing (standard deviation) {sd:.1f}. Only {f['wout']} week of 52 sits outside mean ± 2 swings: "
          "47 tickets, in August, in the rainy season. Moving from 38 to 41 is noise."),

        # 18 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Open the exercise notebook 🧑🏾‍💻</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Click <b class="hl">Open in Colab</b> on W1D3-exercise</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">2</span><p><b>File → Save a copy in Drive</b> 💾</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">3</span><p>Run <b>STEP 0</b>, then go top to bottom</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">4</span><p>Replace every <span class="mono hl">___</span>, run, get the ✅</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🧘🏾</div>
  <h3 style="margin-top:16px">14 checks to pass</h3>
  <p class="muted">Part A: the weekly rhythm<br>Part B: windows and their price<br>🌶️ Bonus: spot the odd week</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on time. Common problems: rolling(7) on the whole DataFrame instead of one column, forgetting center=True, "
          "and counting NaN wrong."),

        # 19 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🌊</span><p><b>Rolling window:</b> average the last N rows, slide forward. <b class="hl">7 days</b> cancels the weekly rhythm.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">⏳</span><p><b>Trailing</b> is safe but ~half a window late. <b class="bad">Centred</b> peeks at the future: reports only.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🚫</span><p><b>Smoothing hides short events.</b> SLAs come from raw readings, never from an average.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:40px">Next week 👉 <b class="hl">Take It Apart</b>: splitting any series into trend, season and noise. 🧩</p>""",
          "Recap. Ask: why 7? Why not centred? Why not report SLAs from the smooth line? Tease Week 2."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    tk, tkw, rf = _data()
    f = facts()
    s = tk["tickets_raised"]
    r7 = s.rolling(7).mean()
    lab_days = [d.strftime("%b %y") if (d.day == 1 and d.month in (1, 4, 7, 10)) else "" for d in s.index]
    pk = slice("2024-06-01", "2024-10-31")
    t30 = s.rolling(30).mean()[pk]
    c30 = s.rolling(30, center=True).mean()[pk]
    lab_pk = [d.strftime("%b") if d.day == 1 else "" for d in t30.index]
    m = rf["link_margin_db"]
    m24 = m.rolling(24).mean()
    lab_rf = [d.strftime("%d %b") if (d.hour == 0 and d.day in (1, 8, 15, 22, 29)) else "" for d in m.index]
    q = tkw["tickets_raised"]
    lab_q = [d.strftime("%b") if d.day <= 7 else "" for d in q.index]

    def clean(x):
        return [round(float(v), 2) for v in x]

    # charts can't hold empty values: start each chart where every line has a value
    s, r7, lab_days = s.iloc[6:], r7.iloc[6:], lab_days[6:]
    m, m24, lab_rf = m.iloc[23:], m24.iloc[23:], lab_rf[23:]

    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🛰️", "kicker": "Week 1 · Day 3", "title": "Calm Down the Noise: Rolling Windows",
             "sub": "How to see the real story inside a jumpy series, and what smoothing hides",
             "notes": "Today we calm down the NOC ticket series without lying about it."},
            {"type": "flow", "title": "Today's mission: three moves", "steps": [
                ["📅", "Spot the rhythm", "tickets drop every weekend"],
                ["🌊", "Smooth it", "a 7-day rolling window"],
                ["🙈", "Know what it hides", "lag, the future, short outages"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up", "notes": "The third move matters most."},
            {"type": "bar", "title": "Even faults rest on Sunday", "labels": SHORT7, "values": [round(v, 2) for v in f["by_day"].values],
             "highlight": [5, 6], "fmt": "0.0", "ymax": 8.5,
             "caption": f"Average NOC tickets per day: weekdays {f['weekday']:.1f}, weekends {f['weekend']:.1f} (about half)",
             "notes": "The weekly rhythm makes the daily chart zig-zag."},
            {"type": "section", "kicker": "Part 1", "title": "The moving average", "sub": "Average the last few days, slide forward one day, repeat",
             "notes": "Section break."},
            {"type": "cards", "title": "You already do this with fuel money", "cards": [
                ["😱", "Look at one day", "One big fill-up, then nothing. Every day tells a different story"],
                ["🧮", "Average the last 7 days", "The big day gets shared across the week"],
                ["➡️", "Slide it every day", "Drop the oldest day, add the newest: a rolling average"]],
             "notes": "Illustration: one day is noisy, a 7-day average is calm."},
            {"type": "code", "title": "One line of pandas",
             "code": 'tk["roll7"] = tk["tickets_raised"].rolling(7).mean()\n\n# first 6 rows are NaN:\n# a 7-day average does not exist until day 7',
             "caption": "rolling(7) = average of the 7 rows up to and including today", "notes": "Quiz question 16: the first 6 NaN are honest."},
            {"type": "chart", "title": "Grey = every day. Blue = the 7-day average", "labels": lab_days,
             "series": [{"name": "daily tickets", "values": clean(s.values), "color": "9DB0C6"},
                        {"name": "7-day average", "values": clean(r7.values), "color": "0A5DB4"}],
             "ymin": 0, "ymax": 13, "fmt": "0", "notes": "The 7-day line shows the rainy-season rise."},
            {"type": "table", "title": "Why 7 days? Every weekday exactly once",
             "header": ["Window", "Weekday-to-weekday swing", "What it shows", "Use it for"],
             "rows": [["3 days", f"{f['spread3']:.2f} tickets", "still feels the weekend", "rarely"],
                      ["7 days", f"{f['spread7']:.2f} tickets", "weekly rhythm removed", "start here for daily tickets"],
                      ["30 days", "almost none", "the season, but slowly", "small counts, long trends"]],
             "colW": [2.0, 3.4, 3.4, 3.33], "caption": "Swing = biggest minus smallest average of the window, by day of week",
             "notes": "Quiz question 13."},
            {"type": "section", "kicker": "Part 2", "title": "What smoothing costs", "sub": "Every smooth line pays for its calm", "notes": "Section break."},
            {"type": "compare", "title": "Trailing looks back. Centred peeks at the future",
             "left": ["⬅️", "Trailing (default)", "Uses only the past. Safe for live monitoring, but about half a window late"],
             "right": ["🔮", "Centred (center=True)", "Uses future days. OK for last year's report, never for live monitoring or forecasts"],
             "notes": "Quiz question 15. A centred window has no value on the last days of the data."},
            {"type": "chart", "title": f"The trailing peak arrives {f['lag']} days late", "labels": lab_pk,
             "series": [{"name": "centred 30-day", "values": clean(c30.values), "color": "E5484D"},
                        {"name": "trailing 30-day", "values": clean(t30.values), "color": "008C7E"}],
             "ymin": 5, "ymax": 9.5, "fmt": "0", "notes": f"Quiz question 14: trailing 30-day peak {f['t30_peak'].date()}, centred {f['c30_peak'].date()}."},
            {"type": "compare", "title": "Exponential smoothing: .ewm(alpha)",
             "left": ["⚡", "High alpha (0.5)", "Follows the data closely, reacts fast"],
             "right": ["🐢", "Low alpha (0.05)", "Very smooth, reacts slowly"],
             "notes": "Quiz question 17."},
            {"type": "chart", "title": "Never report an SLA from a smoothed line", "labels": lab_rf,
             "series": [{"name": "hourly link margin (dB)", "values": clean(m.values), "color": "E5484D"},
                        {"name": "24-hour average", "values": clean(m24.values), "color": "008C7E"}],
             "ymin": -5, "ymax": 7, "fmt": "0",
             "notes": f"Quiz question 18: {f['raw_out']} hours below 0 dB in the raw data, {f['smooth_out']} in the 24-hour average."},
            {"type": "stats", "title": "Small counts need wider windows", "sub": "Priority-1 tickets are rare: a 7-day line still jumps",
             "stats": [[f"{f['p1_mean']:.1f}", "P1 tickets on an average day"], [f"{f['p1_zero'] * 100:.0f}%", "days with zero P1 tickets"],
                       [f"{f['p1_share'] * 100:.0f}%", "share of all tickets"], ["30", "days: a better window for P1"]],
             "notes": "With counts of 0, 1 or 2 a day, one extra ticket is a big jump."},
            {"type": "compare", "title": "rolling(7) and resample(\"W\") answer different questions",
             "left": ["🌊", "rolling(7).mean()", f"Average of the last 7 days, as of today. One value per day ({f['n']} rows)"],
             "right": ["🪣", "resample(\"W\").sum()", f"Total per calendar week. One value per week ({f['n_weeks']} rows). Watch partial weeks at the edges"],
             "notes": f"The last weekly bucket has only 2 days ({f['last_week']} tickets)."},
            {"type": "chart", "title": "38 vs 41 tickets = the same week twice", "labels": lab_q,
             "series": [{"name": "tickets per week", "values": [int(v) for v in q.values], "color": "0A5DB4"},
                        {"name": f"mean ({f['wmean']:.1f})", "values": [round(f["wmean"], 1)] * len(q), "color": "C77700"}],
             "ymin": 20, "ymax": 52, "fmt": "0",
             "notes": f"Mean {f['wmean']:.1f}, typical swing {f['wsd']:.1f}. Only {f['wout']} week of 52 is outside mean ± 2 swings."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W1D3-exercise in Colab", "File → Save a copy in Drive", "Run STEP 0, then top to bottom",
                "Replace every ___, run, get the green tick"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🌊", "Rolling window: average the last N rows; 7 days cancels the weekly rhythm"],
                ["⏳", "Trailing is safe but late; centred peeks at the future"],
                ["🚫", "Smoothing hides short events: SLAs come from raw readings"]],
             "next": "Next week: Take It Apart (trend, season and noise)", "notes": "Tease Week 2."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
def _tk():
    return pd.read_csv(data_path("noc_tickets_daily"), parse_dates=["date"], index_col="date").asfreq("D")

def _c_a1(x):
    return x == "date", "Yes! The time column is called \"date\". Same recipe as Day 1, different file.", \
        "Look at the CSV's first column name. Remember the quotes."

def _c_a2(x):
    t = str(x).strip().lower()
    ok = t in {"half", "a half", "1/2", "0.5"} or (isinstance(x, (int, float)) and abs(x - 0.5) < 0.06)
    return ok, "Half! Weekends run at about half of weekdays. Even faults rest on Sunday. 😴", \
        "Compare the weekday and weekend averages printed above. Is it a quarter, half or the same?"

def _c_b1(x):
    return int(x) == 7, "7! One full week in every window, so every weekday appears exactly once.", \
        "How many days are in one week?"

def _c_b2(x):
    return int(x) == 6, "6 NaN rows: a 7-day average genuinely does not exist until day 7. Nothing is broken. 👍", \
        "Count the NaN values at the top of roll7, or use tk[\"roll7\"].isna().sum()."

def _c_b3(x):
    return int(x) == 3, "The 3-day line still zig-zags: sometimes the weekend is inside the window, sometimes not.", \
        "Which line still jumps up and down every week? 3, 7 or 30?"

def _c_b4(x):
    s = _tk()["tickets_raised"]
    b = s.rolling(7).mean().groupby(s.index.day_name()).mean()
    real = b.max() - b.min()
    return abs(float(x) - real) < 0.01, f"Spread of only {real:.2f} tickets: the weekend effect has cancelled out. That's why 7 is the natural first choice.", \
        "Copy the 3-day line above: roll7_by_day.max() - roll7_by_day.min()"

def _c_b5(x):
    return x is True, "center=True puts the window in the middle: 15 days back AND 15 days into the future. 🔮", \
        "To centre the window, set CENTER to True (no quotes, capital T)."

def _c_b6(x):
    return str(x).strip().lower() in {"no", "false"}, \
        "Correct: the centred line is empty (NaN) on the last days, because the future hasn't happened yet. Reports only, never live monitoring.", \
        "Look at the last 3 values of the centred line printed above. Are they numbers?"

def _c_b7(x):
    real = len(_tk()["tickets_raised"].resample("W").sum())
    return int(x) == real, f"{real} weekly buckets (one value per week), versus 730 rolling values (one per day). Different question, different answer.", \
        "Use len(weekly)."

def _c_b8(x):
    return str(x).strip().lower() == "high", "High alpha follows the data closely and reacts fast. Low alpha is smooth and slow. 🐢", \
        "Which line hugs the grey daily line: alpha 0.5 or alpha 0.05? 0.5 is the HIGH one."

def _c_b9(x):
    real = (_tk()["priority_1"] == 0).mean()
    return abs(float(x) - real) < 0.005, f"{real:.1%} of days had zero priority-1 tickets. Small counts jump around, so they need wider windows.", \
        "Try (tk[\"priority_1\"] == 0).mean(): the share of True values."

def _c_b10(x):
    rf = pd.read_csv(data_path("rf_link_quality_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    m = rf["link_margin_db"]
    want = (int((m < 0).sum()), int((m.rolling(24).mean() < 0).sum()))
    got = (int(x[0]), int(x[1]))
    return got == want, f"{want[0]} real outage hours, {want[1]} on the smoothed line. The average swallowed every outage. SLAs come from raw data! 🚫", \
        "Count with (margin < 0).sum() for the raw line and (smooth < 0).sum() for the 24-hour average."

def _c_b11(x):
    q = pd.read_csv(data_path("noc_tickets_weekly"), parse_dates=["week_start"], index_col="week_start")["tickets_raised"]
    ok = abs(float(x[0]) - q.mean()) < 0.05 and str(x[1]).strip().lower() in {"no", "false"}
    return ok, f"Mean {q.mean():.1f} tickets a week, and 38 → 41 is just noise. Don't call a meeting. ☕", \
        "First answer: weekly[\"tickets_raised\"].mean(). Second: \"yes\" or \"no\": is a 3-ticket change bigger than the usual wobble?"

def _c_bonus(x):
    q = pd.read_csv(data_path("noc_tickets_weekly"), parse_dates=["week_start"], index_col="week_start")["tickets_raised"]
    real = int(((q - q.mean()).abs() > 2 * q.std()).sum())
    return int(x) == real, f"Only {real} odd week in the whole year, in the rainy season. That's the one worth a question. 🌶️", \
        "Count weeks where (value - mean).abs() > 2 * std."

CHECKS = {"A1": _c_a1, "A2": _c_a2, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4, "B5": _c_b5, "B6": _c_b6,
          "B7": _c_b7, "B8": _c_b8, "B9": _c_b9, "B10": _c_b10, "B11": _c_b11, "BONUS": _c_bonus}
HINTS = {"B10": "Give two numbers: (raw_outage_hours, smooth_outage_hours)", "B11": "Give the mean and \"yes\"/\"no\""}
'''


def notebook_cells(setup_code):
    return [
        ("md", """# 🌊 Week 1 · Day 3: Calm Down the Noise: Rolling Windows

**Today:** daily NOC tickets zig-zag every week. You'll smooth them with a **rolling window**, then find out exactly what smoothing **hides**.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then press **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**
> Work in your copy (the new tab), not the original.

**Rule book:** keep `W1D3-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up (run this once, every time you open the notebook)

Click the cell below and press **Shift + Enter**. Wait for `✅ Ready!`. If Colab says *"This notebook was not authored by Google"*, click **Run anyway**."""),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: The weekly rhythm (15 min) 📅

**The data:** `noc_tickets_daily.csv`: how many fault tickets the Network Operations Centre raised **each day** for two years, plus how many were **priority 1** (the most urgent).

### A1 ✍️ Load it with the Day 1 recipe
What is the name of the time column in this file? (Hint: it's not `timestamp` this time. It's a simpler word.)"""),
        ("task", 'TIME_COL = ___\n\ncheck("A1", TIME_COL)', 'TIME_COL = "date"\n\ncheck("A1", TIME_COL)'),
        ("code", 'assert TIME_COL is not None, "✍️ Do A1 first: fill in TIME_COL above, then run this cell again."\n\n'
                 'tk = pd.read_csv(data_path("noc_tickets_daily"), parse_dates=[TIME_COL], index_col=TIME_COL).asfreq("D")\n'
                 'print(len(tk), "days, from", tk.index.min().date(), "to", tk.index.max().date())\ntk.head()'),
        ("md", "### A2 ▶️ Tickets by day of the week\nRun it. Look at the bars, then read the two averages printed below the chart."),
        ("code", 'order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]\n'
                 'by_day = tk.groupby(tk.index.day_name())["tickets_raised"].mean().reindex(order)\n'
                 'by_day.plot(kind="bar", title="Average NOC tickets by day of the week")\nplt.show()\n\n'
                 'weekday = by_day.iloc[:5].mean()\nweekend = by_day.iloc[5:].mean()\n'
                 'print(f"weekday average: {weekday:.2f}    weekend average: {weekend:.2f}")'),
        ("md", "✍️ Weekend volume is roughly what of weekday volume? Type `\"a quarter\"`, `\"half\"` or `\"the same\"`."),
        ("task", 'weekend_vs_weekday = ___\n\ncheck("A2", weekend_vs_weekday)', 'weekend_vs_weekday = "half"\n\ncheck("A2", weekend_vs_weekday)'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Rolling windows and their price (45 min) 🌊

### B1 ✍️ Your first rolling average
A rolling window averages the last **N** rows, then slides forward one row. To cancel the weekly rhythm, the window should hold exactly **one week** of days."""),
        ("task", 'WINDOW = ___     # how many days in one week?\n\ncheck("B1", WINDOW)', 'WINDOW = 7     # how many days in one week?\n\ncheck("B1", WINDOW)'),
        ("md", "▶️ Now smooth it and look at the last 120 days: grey = every day, blue = the 7-day average."),
        ("code", 'assert WINDOW is not None, "✍️ Do B1 first: fill in WINDOW above."\n\n'
                 'tk["roll7"] = tk["tickets_raised"].rolling(WINDOW).mean()\n\n'
                 'last = tk.iloc[-120:]\nlast["tickets_raised"].plot(color="#9DB0C6", lw=1, label="daily")\n'
                 'last["roll7"].plot(lw=3, label="7-day average", title="Daily tickets vs the 7-day rolling average")\nplt.legend()\nplt.show()'),
        ("md", "### B2 ✍️ Why are the first rows empty?\n▶️ Look at the top of the table, then count the `NaN` values at the start of `roll7`."),
        ("code", 'tk.head(8)'),
        ("task", 'nan_rows = ___\n\ncheck("B2", nan_rows)', 'nan_rows = tk["roll7"].isna().sum()\n\ncheck("B2", nan_rows)'),
        ("md", """### B3 ✍️ Pick your window: 3, 7 or 30?
▶️ Run the chart (January to June 2024). **Which window still zig-zags every week?** Answer with the number."""),
        ("code", 'h1 = tk.loc["2024-01-01":"2024-06-30", "tickets_raised"]\n'
                 'for w, lw in [(3, 1.5), (7, 2.5), (30, 3.5)]:\n    h1.rolling(w).mean().plot(lw=lw, label=f"{w}-day")\n'
                 'plt.title("Three window sizes, same data")\nplt.legend()\nplt.show()'),
        ("task", 'zigzag_window = ___\n\ncheck("B3", zigzag_window)', 'zigzag_window = 3\n\ncheck("B3", zigzag_window)'),
        ("md", """### B4 ✍️ Prove that 7 cancels the weekend
For each day of the week, average the rolling line. If the weekly rhythm is gone, all seven numbers are almost the same, so the **spread** (biggest minus smallest) is tiny.
The 3-day version is done for you. Do the same for `roll7`."""),
        ("code", 'roll3_by_day = tk["tickets_raised"].rolling(3).mean().groupby(tk.index.day_name()).mean()\n'
                 'print("3-day window, spread across the week:", round(roll3_by_day.max() - roll3_by_day.min(), 2))\n\n'
                 'roll7_by_day = tk["roll7"].groupby(tk.index.day_name()).mean()\nroll7_by_day.round(2)'),
        ("task", 'spread7 = ___      # biggest minus smallest, like the 3-day line above\n\ncheck("B4", spread7)',
         'spread7 = roll7_by_day.max() - roll7_by_day.min()      # biggest minus smallest, like the 3-day line above\n\ncheck("B4", spread7)'),
        ("md", """### B5 ✍️ Trailing vs centred 🔮
By default pandas puts the window **behind** today (trailing): it only uses the past.
`center=True` puts today in the **middle**, so the window also uses days that haven't happened yet.
Set `CENTER` so the second line is a **centred** window."""),
        ("task", 'CENTER = ___      # True or False\n\ncheck("B5", CENTER)', 'CENTER = True      # True or False\n\ncheck("B5", CENTER)'),
        ("code", 'assert CENTER is not None, "✍️ Do B5 first: fill in CENTER above."\n\n'
                 'trailing = tk["tickets_raised"].rolling(30).mean()\n'
                 'centred = tk["tickets_raised"].rolling(30, center=CENTER).mean()\n\n'
                 'rainy = slice("2024-06-01", "2024-10-31")\n'
                 'centred[rainy].plot(lw=3, label="centred 30-day")\ntrailing[rainy].plot(lw=3, label="trailing 30-day")\n'
                 'plt.title("Same window size, different position")\nplt.legend()\nplt.show()\n\n'
                 'lag = (trailing[rainy].idxmax() - centred[rainy].idxmax()).days\n'
                 'print("trailing peak:", trailing[rainy].idxmax().date(), "   centred peak:", centred[rainy].idxmax().date())\n'
                 'print("the trailing line is", lag, "days late: about half the window")\n'
                 'print("\\nlast 3 values of the centred line:", centred.tail(3).values)'),
        ("md", "### B6 ✍️ Live monitoring test\nOn the **last day** of the data, does the centred line give you a number you could use for live monitoring? Type `\"yes\"` or `\"no\"`."),
        ("task", 'centred_ok_for_live = ___\n\ncheck("B6", centred_ok_for_live)', 'centred_ok_for_live = "no"\n\ncheck("B6", centred_ok_for_live)'),
        ("md", """### B7 ✍️ `.rolling` vs `.resample`: two different questions
`.rolling(7)` gives **one value per day** (“average of the last 7 days”). `.resample("W")` puts days into **weekly buckets** (“total for each calendar week”).
▶️ Run it, then count how many weekly rows you got. Look closely at the **last** row: is that really a quiet week?"""),
        ("code", 'weekly = tk["tickets_raised"].resample("W").sum()\nprint(weekly.head(3))\nprint("...")\nprint(weekly.tail(3))'),
        ("task", 'n_weeks = ___\n\ncheck("B7", n_weeks)', 'n_weeks = len(weekly)\n\ncheck("B7", n_weeks)'),
        ("md", """### B8 ✍️ Exponential smoothing: `.ewm(alpha)`
Exponential smoothing gives recent days more weight. **alpha** decides how much it trusts the newest day.
▶️ Run the chart. Which alpha follows the grey daily line more closely: the **high** one (0.5) or the **low** one (0.05)? Type `"high"` or `"low"`."""),
        ("code", 'summer = tk.loc["2024-06-01":"2024-08-31", "tickets_raised"]\n'
                 'summer.plot(color="#9DB0C6", lw=1, label="daily")\n'
                 'summer.ewm(alpha=0.5).mean().plot(lw=2, label="alpha = 0.5")\n'
                 'summer.ewm(alpha=0.05).mean().plot(lw=3, label="alpha = 0.05")\n'
                 'plt.title("Exponential smoothing: high vs low alpha")\nplt.legend()\nplt.show()'),
        ("task", 'follows_closely = ___\n\ncheck("B8", follows_closely)', 'follows_closely = "high"\n\ncheck("B8", follows_closely)'),
        ("md", """### B9 ✍️ Small counts: priority-1 tickets 🚨
P1 tickets are rare. What **share of days** had **zero** P1 tickets? (Hint: `(tk["priority_1"] == 0)` is True/False for each day, and `.mean()` of True/False gives the share.)"""),
        ("task", 'zero_share = ___\n\ncheck("B9", zero_share)', 'zero_share = (tk["priority_1"] == 0).mean()\n\ncheck("B9", zero_share)'),
        ("code", 'tk["priority_1"].rolling(7).mean().plot(lw=1.5, label="7-day")\n'
                 'tk["priority_1"].rolling(30).mean().plot(lw=3, label="30-day")\n'
                 'plt.title("Priority-1 tickets: small counts need a wider window")\nplt.legend()\nplt.show()'),
        ("md", """### B10 ✍️ The expensive mistake: SLAs from a smoothed line 🚫
New file: `rf_link_quality_hourly` (Ka-band link, August, hour by hour). When `link_margin_db` goes **below 0**, the link is **down**.
▶️ Run the cell, then count the **down hours** in the raw line and in the 24-hour average."""),
        ("code", 'rf = pd.read_csv(data_path("rf_link_quality_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n'
                 'margin = rf["link_margin_db"]\nsmooth = margin.rolling(24).mean()\n\n'
                 'margin.plot(lw=1, label="hourly")\nsmooth.plot(lw=3, label="24-hour average")\n'
                 'plt.axhline(0, color="#E5484D", ls="--", label="link down below here")\n'
                 'plt.title("Ka-band link margin: raw vs smoothed")\nplt.legend()\nplt.show()'),
        ("task", 'raw_outage_hours = ___\nsmooth_outage_hours = ___\n\ncheck("B10", (raw_outage_hours, smooth_outage_hours))',
         'raw_outage_hours = (margin < 0).sum()\nsmooth_outage_hours = (smooth < 0).sum()\n\ncheck("B10", (raw_outage_hours, smooth_outage_hours))'),
        ("md", """### B11 ✍️ Noise: don't call a meeting for it ☕
`noc_tickets_weekly` already has one row per week. Find the **mean** tickets per week.
Then: last week had 38 tickets, this week 41. Should the shift lead investigate? Type `"yes"` or `"no"`."""),
        ("code", 'wk = pd.read_csv(data_path("noc_tickets_weekly"), parse_dates=["week_start"], index_col="week_start")\n'
                 'wk["tickets_raised"].plot(lw=2, title="NOC tickets per week")\n'
                 'plt.axhline(wk["tickets_raised"].mean(), color="#C77700", ls="--")\nplt.show()\n'
                 'print("typical week-to-week wobble (standard deviation):", round(wk["tickets_raised"].std(), 1))'),
        ("task", 'weekly_mean = ___\ninvestigate_38_to_41 = ___\n\ncheck("B11", (weekly_mean, investigate_38_to_41))',
         'weekly_mean = wk["tickets_raised"].mean()\ninvestigate_38_to_41 = "no"\n\ncheck("B11", (weekly_mean, investigate_38_to_41))'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task (bonus): spot the odd week
A simple “is this week unusual?” rule: a week is odd if it sits more than **2 standard deviations** away from the mean.
How many weeks in `wk` break that rule?"""),
        ("task", 'q = wk["tickets_raised"]\n\nodd_weeks = ___      # hint: ((q - q.mean()).abs() > 2 * q.std()).sum()\ncheck("BONUS", odd_weeks)',
         'q = wk["tickets_raised"]\n\nodd_weeks = ((q - q.mean()).abs() > 2 * q.std()).sum()\nprint(q[(q - q.mean()).abs() > 2 * q.std()])\ncheck("BONUS", odd_weeks)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- **Rolling window** = average the last N rows, slide forward one row. `s.rolling(7).mean()`.
- **7 days** holds every weekday exactly once, so the weekend effect cancels. The first 6 values are honestly `NaN`.
- **Short window = jumpy, long window = calm but slow.** Small counts (like P1 tickets) need wider windows.
- **Trailing** (default) is safe for live monitoring but about **half a window late**. **Centred** peeks at the future: reports only.
- **`.ewm(alpha)`**: high alpha reacts fast, low alpha is smooth.
- **`.rolling` ≠ `.resample`**: one value per day vs one value per bucket. Watch partial buckets at the edges.
- **Never report SLAs from a smoothed line**: short outages vanish inside the average.

**Next week:** *Take It Apart*: splitting any series into trend, season and noise. 🧩

<sub>Data: synthetic teaching datasets from the original Week 3 code book (`Time-series/week-03`). They are safe to use in AI assistants. Real NIGCOMSAT data is not.</sub>"""),
    ]
