"""Week 3 · Day 1: Alarms That Cry Wolf."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import BRAND as B, ORIGINALS
from svgcharts import line_svg, spark_svg
from webdeck import logos_title_block

CODE = "W3D1"
TITLE = "Alarms That Cry Wolf"

D4 = ORIGINALS / "week-04" / "data"
GREY = "#6F8399"
FLOOR = 20.0          # the "vendor" floor on solar-array current, amps
SOC_FLOOR = 82.0      # the fixed SoC floor from the original code book
TEMP_LIMIT = 22.0     # a fixed battery-temperature limit, °C


def _data():
    bus = pd.read_csv(D4 / "bus_power_telemetry_hourly.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    rf = pd.read_csv(D4 / "rf_link_quality_hourly.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    tw = pd.read_csv(D4 / "twta_thermal_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    bat = pd.read_csv(D4 / "battery_health_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    return bus, rf, tw, bat


def facts():
    """Every number used on the slides, computed from the data."""
    bus, rf, tw, bat = _data()
    a, ecl = bus["solar_array_current_a"], bus["eclipse_flag"] == 1
    floor = a < FLOOR
    smart = floor & ~ecl
    soc = bus["battery_soc_pct"] < SOC_FLOOR
    hot = bus["battery_temp_c"] > TEMP_LIMIT
    after = bus["eclipse_flag"].shift(1) == 1
    sun = a[~ecl]
    rec = pd.Series(False, index=bus.index)
    for t in bus.index[ecl]:
        rec.loc[t + pd.Timedelta("1h"):t + pd.Timedelta("3h")] = True
    rec &= ~ecl
    clean = a[~ecl & ~rec & (a >= FLOOR)]
    cn, m, rain = rf["cn_ratio_db"], rf["link_margin_db"], rf["rain_rate_mmhr"]
    out = m < 0
    cn_floor = cn.mean() - 3 * cn.std()
    dry = cn[rain == 0]
    dry_floor = dry.mean() - 3 * dry.std()
    t = tw["twta_temp_c"]
    cap = bat["est_capacity_ah"]
    ecl_days = bus.index[ecl]
    return dict(
        n=len(bus), n_ecl=int(ecl.sum()), ecl_hour=int(ecl_days.hour[0]), ecl_first=ecl_days.min(), ecl_last=ecl_days.max(),
        floor=int(floor.sum()), floor_ecl=int((floor & ecl).sum()), smart=int(smart.sum()), smart_times=list(bus.index[smart]),
        soc=int(soc.sum()), soc_ecl=int((soc & ecl).sum()), soc_min=bus["battery_soc_pct"].min(),
        hot=int(hot.sum()), hot_after=int((hot & after).sum()), hot_real=int((hot & ~after & ~ecl).sum()),
        sun_mean=sun.mean(), sun_sd=sun.std(), sun_lo=sun.mean() - 3 * sun.std(), sun_hi=sun.mean() + 3 * sun.std(),
        sun_flags=int(((sun < sun.mean() - 3 * sun.std()) | (sun > sun.mean() + 3 * sun.std())).sum()),
        clean_sd=clean.std(), clean_lo=clean.mean() - 3 * clean.std(), clean_hi=clean.mean() + 3 * clean.std(),
        clean_flags=int(((sun < clean.mean() - 3 * clean.std()) | (sun > clean.mean() + 3 * clean.std())).sum()),
        clean_rec=int((((a < clean.mean() - 3 * clean.std()) | (a > clean.mean() + 3 * clean.std())) & rec).sum()),
        drop_low=a[smart].mean(),
        rain_h=int((rain > 0).sum()), outages=int(out.sum()), cn_floor=cn_floor,
        cn_flags=int((cn < cn_floor).sum()), cn_real=int(((cn < cn_floor) & out).sum()),
        dry_floor=dry_floor, dry_flags=int((cn < dry_floor).sum()), dry_real=int(((cn < dry_floor) & out).sum()),
        persist=int((out & out.shift(1, fill_value=False)).sum()),
        up_corr=rf["uplink_power_dbm"].corr(rain),
        up_dry=rf.loc[rain == 0, "uplink_power_dbm"].mean(), up_rain=rf.loc[rain > 0, "uplink_power_dbm"].mean(),
        tw_lim=t.mean() + 3 * t.std(), tw_max=t.max(), tw_flags=int((t > t.mean() + 3 * t.std()).sum()),
        tw_pre=t.loc["2025-04-12":"2025-05-11"].mean(), tw_post=t.loc["2025-05-12":"2025-06-10"].mean(),
        cap0=cap.iloc[0], cap1=cap.iloc[-1], cap_min=cap.min(), cap95=int((cap < 95).sum()),
    )


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


def _Y(y, lo, hi, h):
    """Same vertical scale as svgcharts.line_svg (top 30, bottom h-60)."""
    T, Bm = 30, h - 60
    return Bm + (y - lo) / (hi - lo) * (T - Bm)


def _hline(y, lo, hi, w, h, col, lab, anchor="end", dash="10 8", below=False, x=None):
    yy = _Y(y, lo, hi, h)
    if x is None:
        x = w - 30 if anchor == "end" else 100
    ty = yy + 28 if below else yy - 10
    return (f'<line x1="90" x2="{w - 30}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{col}" stroke-width="2.5" stroke-dasharray="{dash}"/>'
            f'<text x="{x}" y="{ty:.1f}" fill="{col}" font-size="21" font-weight="800" text-anchor="{anchor}" '
            f'paint-order="stroke" stroke="#12233A" stroke-width="6">{lab}</text>')


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    f = facts()
    bus, rf, tw, bat = _data()
    a = bus["solar_array_current_a"]

    # eclipse fortnight: nightly drops to zero
    win = a.loc["2025-09-20":"2025-10-03 23:00"]
    days = pd.date_range("2025-09-20", "2025-10-03", freq="D")
    ecl_chart = line_svg(
        win.values, w=1420, h=380, ymin=0, ymax=31, area=False, stroke=2.5, max_points=2000,
        yticks=[(0, "0 A"), (10, "10 A"), (20, "20 A"), (30, "30 A")],
        xlabels=[(int((d - win.index[0]).total_seconds() // 3600), d.strftime("%-d %b")) for d in days[::3]],
        extra=_hline(FLOOR, 0, 31, 1420, 380, B["bad"], "vendor floor: 20 A", anchor="start", below=True, x=120), dur="3s")

    # battery temperature over five eclipse nights
    tw5 = bus["battery_temp_c"].loc["2025-09-22":"2025-09-26 23:00"]
    days5 = pd.date_range("2025-09-22", "2025-09-26", freq="D")
    temp_chart = line_svg(
        tw5.values, w=1420, h=340, ymin=17.5, ymax=24.5, area=False, stroke=3, color=B["amber_d"], max_points=2000,
        yticks=[(18, "18 °C"), (20, "20 °C"), (22, "22 °C"), (24, "24 °C")],
        xlabels=[(int((d - tw5.index[0]).total_seconds() // 3600), d.strftime("%-d %b")) for d in days5],
        extra=_hline(TEMP_LIMIT, 17.5, 24.5, 1420, 340, B["bad"], "fixed limit: 22 °C", anchor="start", x=290), dur="2.6s")

    # sunlit array current with the 3-sigma band (all 120 days)
    sun = a.where(bus["eclipse_flag"] == 0)
    lo, hi = 14, 31
    band_chart = line_svg(
        sun.values, w=1420, h=360, ymin=lo, ymax=hi, area=False, stroke=2, max_points=3000,
        yticks=[(15, "15 A"), (20, "20 A"), (25, "25 A"), (30, "30 A")],
        xlabels=[(0, "1 Aug"), (int((pd.Timestamp("2025-09-01") - a.index[0]).total_seconds() // 3600), "1 Sep"),
                 (int((pd.Timestamp("2025-10-01") - a.index[0]).total_seconds() // 3600), "1 Oct"),
                 (int((pd.Timestamp("2025-11-01") - a.index[0]).total_seconds() // 3600), "1 Nov"),
                 (len(a) - 1, "28 Nov")],
        extra=_hline(f["sun_lo"], lo, hi, 1420, 360, B["gold"], f"3σ floor {f['sun_lo']:.2f} A", anchor="start", below=True, x=430)
        + _hline(f["sun_hi"], lo, hi, 1420, 360, B["gold"], f"3σ ceiling {f['sun_hi']:.2f} A", anchor="start", x=430),
        dur="3s")

    # 50 alarm tiles: 46 eclipse + 4 real
    real_idx = {11, 23, 24, 39}
    tiles = "".join(
        f'<div class="anim a-pop" style="--d:{.2 + k * .03:.2f}s;width:64px;height:64px;border-radius:14px;display:flex;'
        f'align-items:center;justify-content:center;font-size:34px;'
        f'background:{"rgba(229,72,77,.22)" if k in real_idx else "#12233A"};'
        f'border:2px solid {"#FF6B6F" if k in real_idx else "#24384F"}">{"🚨" if k in real_idx else "🐺"}</div>'
        for k in range(f["floor"]))

    # three shapes
    sp_spike = spark_svg(a.loc["2025-08-15":"2025-08-21"].values, w=360, h=120, color=B["bad"], delay=".5s")
    sp_shift = spark_svg(tw["twta_temp_c"].loc["2025-03-01":"2025-07-31"].values, w=360, h=120, color=B["gold"], delay=".8s")
    sp_drift = spark_svg(bat["est_capacity_ah"].values, w=360, h=120, color=B["teal_d"], delay="1.1s")
    shapes = [
        ("📍", "Spike", "One odd reading, then back to normal.", sp_spike, "solar-array dropout, 18 Aug",
         "✅ a limit can catch it (with context)"),
        ("🪜", "Level shift", "Jumps to a new normal and stays there.", sp_shift, "amplifier temp, +2.2 °C in May",
         f"❌ fixed limit fires {f['tw_flags']} times"),
        ("🐢", "Drift", "Slides slowly. No single day looks strange.", sp_drift, "battery capacity, 3 years",
         f"❌ a 95 Ah limit fires {f['cap95']} times"),
    ]
    shape_cards = "".join(
        f'<div class="card anim" style="--d:{.2 + k * .3:.2f}s;padding:28px"><div style="font-size:56px">{e}</div>'
        f'<h3 style="margin-top:6px">{t}</h3><p style="font-size:23px;color:var(--muted);min-height:68px">{d}</p>{svg}'
        f'<div class="small" style="font-size:17px;margin-top:4px">{src}</div>'
        f'<p style="font-size:22px;margin-top:12px;font-weight:700">{verdict}</p></div>'
        for k, (e, t, d, svg, src, verdict) in enumerate(shapes))

    # outage strip: 12 one-hour outages
    out = rf["link_margin_db"] < 0
    out_days = [ts.strftime("%-d %b %H:00") for ts in rf.index[out]]
    out_strip = "".join(
        f'<div class="anim a-pop" style="--d:{.25 + k * .08:.2f}s;padding:12px 14px;border-radius:12px;background:rgba(229,72,77,.18);'
        f'border:2px solid #FF6B6F;font-size:19px;font-weight:700;text-align:center;min-width:150px">1 hour<br>'
        f'<span style="color:#FFC2C4;font-weight:600">{d}</span></div>' for k, d in enumerate(out_days))

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:20px;top:120px;width:560px;height:560px">
  <svg viewBox="0 0 560 560" width="560" height="560">
    <circle cx="280" cy="280" r="250" fill="none" stroke="#24384F" stroke-width="2" stroke-dasharray="6 10"/>
    <circle cx="280" cy="280" r="150" fill="#12233A" stroke="#E5484D" stroke-width="5" class="pulse"/>
    <text x="280" y="320" text-anchor="middle" font-size="150">🐺</text>
    <text x="280" y="470" text-anchor="middle" font-size="40" fill="#FF6B6F" font-weight="800" class="pulse">ALARM! ALARM!</text>
  </svg></div>
<div style="max-width:900px;margin-top:40px">
  <div class="kicker anim">Week 3 · Day 1</div>
  <h1 class="anim" style="--d:.2s">Alarms That<br><span class="hl">Cry Wolf</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Weeks 1–2 asked “what does this series look like?”<br>From today we ask: <b class="hl">“when is a reading WRONG?”</b> 🚨</p>
  <div class="anim" style="--d:.8s;margin-top:44px;display:flex;justify-content:flex-start">{logos_title_block()}</div>
</div>""",
          "Welcome to the anomaly-detection half of the course. Today: the alarms NIGCOMSAT already has, why they shout "
          "at the wrong time, and the first fix: context. No machine learning yet. Ask: who has been woken up by a false alarm?"),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Three moves</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:390px;padding:44px 30px"><div class="icon">🚨</div><h3>Meet your alarm</h3><p class="small">a fixed limit is already a model</p></div>
  <div class="arrow anim a-fade" style="--d:.6s"></div>
  <div class="box on anim a-pop" style="--d:.8s;min-width:390px;padding:44px 30px"><div class="icon">🐺</div><h3>Watch it cry wolf</h3><p class="small">46 eclipse nights, all “alarms”</p></div>
  <div class="arrow anim a-fade" style="--d:1.1s"></div>
  <div class="box on anim a-pop" style="--d:1.3s;min-width:390px;padding:44px 30px"><div class="icon">🧠</div><h3>Give it context</h3><p class="small">same limit, 4 alarms, all real</p></div>
</div>
<div class="row anim" style="--d:1.7s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up</span>
</div>""",
          "Three moves. By the end, participants turn an alarm that fires 50 times into one that fires 4 times, and all 4 are real."),

        # 3 ─ hook NigComSat-1
        S("""
<div class="kicker anim">Why we're here</div>
<h2 class="anim" style="--d:.1s">November 2008. NigComSat-1 goes silent.</h2>
<div class="flow" style="margin-top:40px;align-items:stretch">
  <div class="box anim a-left" style="--d:.3s;flex:1;padding:36px 28px"><div class="big-emoji" style="font-size:110px">☀️</div><h3 style="margin-top:12px">Solar-array anomaly</h3>
    <p class="muted" style="font-size:24px">Not enough power. The battery couldn't carry it.</p></div>
  <div class="arrow anim a-fade" style="--d:.7s;align-self:center"></div>
  <div class="box anim a-pop" style="--d:.9s;flex:1;padding:36px 28px;border-color:#E5484D"><div class="big-emoji" style="font-size:110px">🛰️</div><h3 style="margin-top:12px">Satellite lost</h3>
    <p class="muted" style="font-size:24px">About four years with no Nigerian satellite.</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s;align-self:center"></div>
  <div class="box on anim a-right" style="--d:1.5s;flex:1;padding:36px 28px"><div class="big-emoji" style="font-size:110px">👀</div><h3 style="margin-top:12px" class="hl">Watch the array</h3>
    <p style="font-size:24px">Today's main character: <b>solar_array_current_a</b></p></div>
</div>""",
          "Real history (fact sheet): NigComSat-1 launched 2007 and failed in November 2008 after a solar-array anomaly left it "
          "without power. NigComSat-1R replaced it in 2011. So the solar-array current is not just any column: it's the one that "
          "already cost Nigeria a satellite. Our data is synthetic, but the stakes are real."),

        # 4 ─ section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">The alarm you<br>already have 🚨</h1>""",
          "Section break.", cls="center"),

        # 5 ─ a threshold is a model
        S("""
<div class="kicker anim">Surprise</div>
<h2 class="anim" style="--d:.1s">Your NOC already does anomaly detection 🎉</h2>
<pre class="code anim" style="--d:.3s;font-size:40px;margin-top:30px;padding:40px 50px">if reading &lt; limit:
    raise_alarm()        # this is a model!</pre>
<div class="grid3" style="margin-top:36px">
  <div class="card anim a-pop" style="--d:.6s"><div class="icon">📏</div><h3>It has a rule</h3><p class="muted">“below 20 A is bad”</p></div>
  <div class="card anim a-pop" style="--d:.8s"><div class="icon">🧮</div><h3>It has a number</h3><p class="muted">someone chose 20</p></div>
  <div class="card anim a-pop" style="--d:1s"><div class="icon">⚖️</div><h3>It can be wrong</h3><p class="muted">too many alarms, or too few</p></div>
</div>""",
          "Quiz question: a fixed alarm threshold IS a simple anomaly-detection model (True). Everything this week is about "
          "making that model smarter, and measuring whether it really is."),

        # 6 ─ what alarm software does
        S("""
<div class="kicker anim">What alarm software already does</div>
<h2 class="anim" style="--d:.1s">Four tricks your NOC already uses</h2>
<div class="grid4" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s;padding:28px"><div class="icon">🟡🔴</div><h3>Yellow &amp; red limits</h3><p style="font-size:23px" class="muted">Warning first, then alarm. Like the fuel light, then the car stopping.</p></div>
  <div class="card anim a-pop" style="--d:.55s;padding:28px"><div class="icon">⏳</div><h3>Persistence</h3><p style="font-size:23px" class="muted">Only alarm if it stays bad for N readings. “Let me see if NEPA really took light.”</p></div>
  <div class="card anim a-pop" style="--d:.8s;padding:28px"><div class="icon">↕️</div><h3>Hysteresis</h3><p style="font-size:23px" class="muted">Alarm ON at one level, OFF at another, so it doesn't flap on/off all night.</p></div>
  <div class="card anim a-pop" style="--d:1.05s;padding:28px"><div class="icon">🎭</div><h3>State-based limits</h3><p style="font-size:23px" class="muted">Different “normal” for different modes: eclipse, recharge, sunlit.</p></div>
</div>
<p class="anim" style="--d:1.4s;margin-top:34px;text-align:center">Each trick buys <b class="good">quiet</b>… and each one can make you <b class="bad">blind</b>. Today we test them on data.</p>""",
          "Ground systems check telemetry against limit sets: yellow and red, often with a persistence count and hysteresis, and "
          "sometimes different limit sets per operating mode. Each trick reduces false alarms but can hide real events. We'll prove "
          "both sides with data."),

        # 7 ─ where did that number come from
        S("""
<div class="kicker anim">The most important question this week</div>
<h2 class="anim" style="--d:.1s">“Where did that number come from?” 🕵🏾</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s"><h3>Possible answers 🙈</h3>
    <p class="muted">“The vendor manual said so.”<br>“We copied it from the old satellite.”<br>“Oga set it years ago.”<br>“Nobody knows.”</p></div>
  <div class="card anim a-right glow" style="--d:.6s"><h3 class="hl">Good answers ✅</h3>
    <p>“From the design margin, with this reason.”<br>“From 6 months of normal data: mean ± 3σ.”<br>“Reviewed after the last eclipse season.”</p></div>
</div>
<p class="sub anim" style="--d:1s;margin-top:34px;text-align:center">Ask it of <b>every</b> limit in your unit. Write the answer down.</p>""",
          "Quiz question: the course asks of every existing alarm limit, where did that number come from? Make them say it out loud. "
          "It's also a great question to take back to their units."),

        # 8 ─ section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Watch it cry wolf 🐺</h1>""",
          "Section break.", cls="center"),

        # 9 ─ eclipse = NEPA took light
        S(f"""
<div class="kicker anim">Eclipse season</div>
<h2 class="anim" style="--d:.1s">{f['ecl_hour']}:00 UTC every night: NEPA takes light 🌘</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{ecl_chart}</div>
<div class="row anim" style="--d:3s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill">{f['n_ecl']} eclipse hours</span>
  <span class="pill teal">{f['ecl_first']:%-d %b} → {f['ecl_last']:%-d %b}</span>
  <span class="pill gold">🔋 runs on battery, like your inverter</span>
  <span class="small" style="margin-left:auto">solar-array current, 20 Sep – 3 Oct</span>
</div>""",
          "Around the equinoxes the Earth's shadow crosses the orbit once a night. At 21:00 UTC (22:00 in Lagos) the array current "
          "drops to zero and the battery carries the satellite, exactly like your inverter when NEPA takes light. This is NORMAL, "
          "it's physics, it happens every year."),

        # 10 ─ 50 alarms
        S(f"""
<div class="kicker anim">The vendor floor: array current &lt; {FLOOR:.0f} A</div>
<h2 class="anim" style="--d:.1s">{f['floor']} alarms. Only {f['floor'] - f['floor_ecl']} are real.</h2>
<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:16px;max-width:1420px">{tiles}</div>
<div class="row" style="margin-top:28px;gap:30px">
  <div class="card anim" style="--d:2s;flex:1;padding:22px 28px"><p>🐺 <b>{f['floor_ecl']}</b> eclipse nights: <span class="muted">technically correct, operationally useless</span></p></div>
  <div class="card anim" style="--d:2.2s;flex:1;padding:22px 28px;border-color:#E5484D"><p>🚨 <b>{f['floor'] - f['floor_ecl']}</b> real solar-array dropouts <span class="muted">hiding among them</span></p></div>
</div>""",
          f"Quiz question: why is a floor that fires on all {f['n_ecl']} eclipse hours a problem? Every alarm is technically correct but "
          f"operationally useless. Same story with the original code book's SoC floor: SoC below {SOC_FLOOR:.0f}% fires {f['soc']} times, "
          f"and all {f['soc_ecl']} are normal eclipse nights (the quiz says 46; with an 82% floor it's {f['soc']})."),

        # 11 ─ alarm fatigue
        S("""
<div class="row" style="gap:50px;align-items:center;margin-top:30px">
 <div style="flex:1.2">
  <div class="kicker anim">Alarm fatigue</div>
  <h2 class="anim" style="--d:.1s">The car alarm on your street 🚗</h2>
  <p class="sub anim" style="--d:.3s">It goes off every time a keke passes. Week 1: everyone runs outside. Week 3: nobody even looks.</p>
  <p class="anim" style="--d:.6s;margin-top:30px">Then one night, a real thief comes. 🦹🏾 <b class="bad">Nobody moves.</b></p>
  <p class="anim" style="--d:.9s;margin-top:30px">A NOC that gets 46 false alarms a season learns to <b class="hl">ignore the solar-array alarm</b>. That's how a NigComSat-1 story starts.</p>
 </div>
 <div class="card glow anim a-pop" style="--d:.5s;flex:.8;text-align:center;padding:50px">
  <div class="big-emoji floaty">😴</div>
  <h3 style="margin-top:16px">Too many wolves<br>= no shepherd</h3>
 </div>
</div>""",
          "Alarm fatigue is the real danger of a noisy alarm. It doesn't just waste time: it trains people to ignore the channel. "
          "Ask: which alarms in your unit does everyone ignore?"),

        # 12 ─ the fix: context
        S(f"""
<div class="kicker anim">The fix: don't widen the limit. Add context.</div>
<h2 class="anim" style="--d:.1s">Same limit. Ask one more question first.</h2>
<div class="flow" style="margin-top:20px;justify-content:center">
  <div class="box anim a-pop" style="--d:.3s;min-width:260px"><div class="icon">📥</div><h3>Reading</h3><p class="small">array current</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:300px"><div class="icon">🌘</div><h3>In eclipse?</h3><p class="small">eclipse_flag == 1 → normal, stay quiet</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:300px"><div class="icon">📏</div><h3>Below 20 A?</h3><p class="small">only now check the limit</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box anim a-pop" style="--d:1.5s;min-width:220px;border-color:#E5484D"><div class="icon">🚨</div><h3>Alarm</h3></div>
</div>
<pre class="code anim" style="--d:1.8s;margin-top:30px">smart_alarm = (bus["solar_array_current_a"] &lt; 20) &amp; (bus["eclipse_flag"] == 0)
# {f['floor']} alarms  →  {f['smart']} alarms, every one a real dropout</pre>""",
          "This is called conditioning on state. Don't make the limit wider (you'd miss the dropouts). Tell the alarm which mode the "
          "satellite is in. The eclipse_flag is the honest way to suppress seasonal false alarms."),

        # 13 ─ battery temperature
        S(f"""
<div class="kicker anim">Same trap, another sensor</div>
<h2 class="anim" style="--d:.1s">Battery &gt; {TEMP_LIMIT:.0f} °C: {f['hot']} alarms, {f['hot_after']} after eclipse</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{temp_chart}</div>
<p class="anim" style="--d:2.8s;margin-top:20px">Recharging warms the pack for an hour after every eclipse. <b>Normal.</b> Context fix: ignore the hour after eclipse → <b class="hl">{f['hot_real']} alarms left, all real.</b></p>""",
          f"The hour after eclipse (22:00 UTC) the battery is recharging hard and warms up past 22 °C. That's {f['hot_after']} normal "
          f"alarms. The {f['hot_real']} that remain are the same four solar-array dropout hours, seen from a second sensor."),

        # 14 ─ section
        S("""
<div class="kicker anim">Part 3</div>
<h1 class="anim" style="--d:.15s">Where should<br>the limit be? 📏</h1>""",
          "Section break.", cls="center"),

        # 15 ─ 3 sigma from the data
        S(f"""
<div class="kicker anim">Let the data choose the number</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Normal ± 3σ, from sunlit hours only</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{band_chart}</div>
<div class="row anim" style="--d:3s;margin-top:18px;gap:14px;align-items:center">
  <span class="pill">mean {f['sun_mean']:.2f} A</span><span class="pill teal">σ = {f['sun_sd']:.3f} A</span>
  <span class="pill gold">outside the band: {f['sun_flags']} hours = the 4 dropouts</span>
</div>""",
          f"σ (sigma) = standard deviation = the typical wobble. Mean ± 3σ from sunlit data gives {f['sun_lo']:.2f} to {f['sun_hi']:.2f} A, "
          f"and exactly the {f['sun_flags']} dropout hours fall outside. Note: the original code book says σ ≈ 0.06 A. The data says "
          f"{f['sun_sd']:.3f} A."),

        # 16 ─ honest normal
        S(f"""
<div class="kicker anim">But what IS normal?</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The faults you hunt <span class="hl">widen your own limits</span></h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><h3>📦 All sunlit hours</h3>
    <div class="stat" style="font-size:80px;margin-top:10px">σ = {f['sun_sd']:.2f}</div>
    <p class="muted" style="margin-top:12px">Includes the dropouts and the post-eclipse recharge boost. Band {f['sun_lo']:.1f}–{f['sun_hi']:.1f} A: <b style="color:#fff">wide, quiet</b>.</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#E5484D"><h3>🧼 “Clean” hours only</h3>
    <div class="stat" style="font-size:80px;margin-top:10px">σ = {f['clean_sd']:.2f}</div>
    <p class="muted" style="margin-top:12px">Remove every odd hour. Band {f['clean_lo']:.2f}–{f['clean_hi']:.2f} A: <b class="bad">{f['clean_flags']} alarms</b>, {f['clean_rec']} of them normal recharge hours. 🐺</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:30px;text-align:center">Normal needs <b class="hl">context</b> (sunlit? recharging? eclipse?), not just a mean and a σ. Day 2 builds this properly.</p>""",
          "The honest lesson: the 4 dropouts alone stretch sigma from about 0.17 to about 0.5 A. Throw away every odd hour and the band "
          "becomes so tight that every recharge hour cries wolf. There is no single magic sigma; you need to define normal per state. "
          "That's tomorrow's control-chart day."),

        # 17 ─ rain is not a fault
        S(f"""
<div class="kicker anim">The RF link: raining ≠ link down</div>
<h2 class="anim" style="--d:.1s;font-size:54px">A 3σ rule on C/N can't tell rain from outage</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><h3>3σ from ALL hours</h3>
    <div class="stat" style="font-size:90px;margin-top:8px"><span class="count" data-to="{f['cn_flags']}" data-d=".5">0</span></div>
    <p class="muted">alarms (floor {f['cn_floor']:.2f} dB) · <b class="good">{f['cn_real']} real</b> · <b class="bad">{f['cn_flags'] - f['cn_real']} just rain</b></p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#E5484D"><h3>3σ from DRY hours only</h3>
    <div class="stat" style="font-size:90px;margin-top:8px"><span class="count" data-to="{f['dry_flags']}" data-d=".8">0</span></div>
    <p class="muted">alarms (floor {f['dry_floor']:.2f} dB) · <b class="good">{f['dry_real']} real</b> · <b class="bad">{f['dry_flags'] - f['dry_real']} just rain</b> ({(f['dry_flags'] - f['dry_real']) / f['dry_flags']:.0%} false)</p></div>
</div>
<p class="anim" style="--d:1.1s;margin-top:30px;text-align:center">August had <b>{f['rain_h']}</b> rainy hours and <b>{f['outages']}</b> real outages. <b class="hl">Link margin below 0 dB = down.</b> Rain alone = not a fault.</p>""",
          f"In heavy rain C/N falls whether or not the link actually drops. A tight 'dry weather' normal flags {f['dry_flags']} hours, "
          f"{(f['dry_flags'] - f['dry_real']) / f['dry_flags']:.0%} of them false. The honest outage definition is link margin below 0 dB."),

        # 18 ─ persistence trap
        S(f"""
<div class="kicker anim">The persistence trick, tested</div>
<h2 class="anim" style="--d:.1s;font-size:54px">“Wait 2 hours” catches <span class="bad">{f['persist']}</span> of {f['outages']} outages</h2>
<div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:24px">{out_strip}</div>
<p class="anim" style="--d:1.6s;margin-top:34px">🙈 Every August outage lasted <b>exactly one hour</b>. A delay rule buys quiet by going <b class="bad">blind</b>.</p>""",
          "Every one of the 12 outage hours was a single hour. A 2-in-a-row persistence rule would have caught none of them. "
          "Persistence is a trade: fewer false alarms, slower and blinder detection. Always test it on real events before switching it on."),

        # 19 ─ leaking the answer
        S(f"""
<div class="kicker anim">Careful what you feed a detector</div>
<h2 class="anim" style="--d:.1s">Uplink power is the system's <span class="hl">reaction</span> to rain</h2>
<div class="flow" style="margin-top:30px;justify-content:center">
  <div class="box anim a-pop" style="--d:.3s"><div class="icon">🌧️</div><h3>Heavy rain</h3></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s"><div class="icon">📉</div><h3>Signal fades</h3></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s"><div class="icon">🔊</div><h3>Power control pushes harder</h3><p class="small">{f['up_dry']:.1f} → {f['up_rain']:.1f} dBm</p></div>
</div>
<div class="row" style="margin-top:34px;gap:30px">
  <div class="card anim" style="--d:1.4s;flex:1"><div class="stat" style="font-size:80px">{f['up_corr']:.2f}</div><div class="stat-label">correlation of uplink power with rain</div></div>
  <div class="card anim" style="--d:1.6s;flex:2"><p>Feed it to an outage detector and the detector just learns <b>“is it raining?”</b>. It <b class="bad">leaks the answer</b> instead of finding faults.</p></div>
</div>""",
          "Quiz question (advanced): why not feed uplink_power_dbm to the RF detector? Because it's a response to rain, so it leaks the "
          "answer. A detector built on it becomes a rain detector. Revisit this in Week 5 when we engineer features."),

        # 20 ─ three shapes
        S(f"""
<div class="kicker anim">The three shapes of trouble</div>
<h2 class="anim" style="--d:.1s">Spike, level shift, drift</h2>
<div class="grid3" style="margin-top:14px">{shape_cards}</div>""",
          f"Quiz questions: the three anomaly shapes in the Week 4 data are spike, level shift and drift. A fixed limit can catch a "
          f"spike (with context). It misses the amplifier's +{f['tw_post'] - f['tw_pre']:.1f} °C level shift (its 3σ limit "
          f"{f['tw_lim']:.1f} °C is never reached; the highest day is {f['tw_max']:.1f} °C). And the battery fades from "
          f"{f['cap0']:.1f} to {f['cap1']:.1f} Ah without a 95 Ah limit firing even once. That's silent degradation. Days 2 and 3 fix these."),

        # 21 ─ your turn
        S("""
<div class="row" style="gap:60px;align-items:center;min-height:700px">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Tame the wolves 🐺</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">1</span><p>Open <b class="hl">W3D1-exercise</b> in Colab, save a copy</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">2</span><p><b>Part A:</b> count the wolves, then add context</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">3</span><p><b>Part B:</b> let the data choose the limit</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">4</span><p><b>Part C:</b> rain, delays, leaks and the 3 shapes</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🚨</div>
  <h3 style="margin-top:16px">14 checks to pass</h3>
  <p class="muted">13 tasks + 🌶️ the pepper task</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Common problems: forgetting .asfreq('h'), using == '0' (text) instead of == 0 for the flag, and mixing up & and 'and'."),

        # 22 ─ recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🚨</span><p><b>A limit is a model.</b> Ask where every number came from.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🧠</span><p><b>Add context, don't widen.</b> Eclipse, recharge and rain are normal states, not faults.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🪜</span><p><b>Fixed limits catch spikes</b>, not level shifts or slow drift.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:40px">Next 👉 <b class="hl">Control Charts and Residuals</b>: a normal that moves with the data.</p>""",
          "Recap. Ask: which alarm in your own unit would you test first with what you learned today?"),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    f = facts()
    bus, rf, tw, bat = _data()
    a = bus["solar_array_current_a"].loc["2025-09-20":"2025-10-03 23:00"]
    labels = [ts.strftime("%-d %b") if ts.hour == 0 and ts.day % 3 == 2 else "" for ts in a.index]
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🐺", "kicker": "Week 3 · Day 1", "title": "Alarms That Cry Wolf",
             "sub": "From today we ask: when is a reading wrong?",
             "notes": "Welcome to the anomaly-detection half. Today: the alarms we already have, why they cry wolf, and context."},
            {"type": "flow", "title": "Today's mission: three moves", "steps": [
                ["🚨", "Meet your alarm", "a fixed limit is already a model"],
                ["🐺", "Watch it cry wolf", f"{f['n_ecl']} eclipse nights, all alarms"],
                ["🧠", "Give it context", f"same limit, {f['smart']} alarms, all real"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up", "notes": "Three moves."},
            {"type": "flow", "title": "November 2008: NigComSat-1 goes silent", "steps": [
                ["☀️", "Solar-array anomaly", "not enough power"],
                ["🛰️", "Satellite lost", "about four years without one"],
                ["👀", "Watch the array", "today's main character"]],
             "notes": "Real history from the fact sheet. Our data is synthetic, the stakes are real."},
            {"type": "section", "kicker": "Part 1", "title": "The alarm you already have", "sub": "A fixed limit is already a model",
             "notes": "Section break."},
            {"type": "code", "title": "Your NOC already does anomaly detection",
             "code": "if reading < limit:\n    raise_alarm()        # this is a model!",
             "caption": "It has a rule, it has a number, and it can be wrong", "notes": "Quiz: a threshold is a model (True)."},
            {"type": "cards4", "title": "Four tricks alarm software already knows", "cards": [
                ["🚦", "Yellow & red limits", "warning first, then alarm"],
                ["⏳", "Persistence", "alarm only if bad for N readings"],
                ["↕️", "Hysteresis", "on at one level, off at another"],
                ["🎭", "State-based limits", "different normal per mode"]],
             "notes": "Each trick buys quiet and can make you blind."},
            {"type": "compare", "title": "“Where did that number come from?”",
             "left": ["🙈", "Weak answers", "The vendor manual. The old satellite. Oga set it. Nobody knows."],
             "right": ["✅", "Good answers", "Design margin with a reason. Mean ± 3σ of normal data. Reviewed every season."],
             "notes": "Ask it of every limit in your unit."},
            {"type": "section", "kicker": "Part 2", "title": "Watch it cry wolf", "sub": "Eclipse season", "notes": "Section break."},
            {"type": "chart", "title": "Every night at 21:00 UTC the satellite runs on battery", "labels": labels,
             "values": a.round(2).tolist(), "ymin": 0, "ymax": 31, "freq": 24, "fmt": "0", "name": "array current (A)",
             "caption": f"{f['n_ecl']} eclipse hours, {f['ecl_first']:%-d %b} to {f['ecl_last']:%-d %b}: the satellite's own 'NEPA took light'",
             "notes": "Normal physics, every year."},
            {"type": "stats", "title": f"Array current below {FLOOR:.0f} A: {f['floor']} alarms", "sub": "The vendor floor, on all 120 days",
             "stats": [[str(f['floor']), "alarms in total"], [str(f['floor_ecl']), "normal eclipse nights"],
                       [str(f['floor'] - f['floor_ecl']), "real dropouts"], [f"{(f['floor'] - f['floor_ecl']) / f['floor']:.0%}", "of alarms are real"]],
             "notes": f"Every alarm technically correct, operationally useless. SoC < 82% fires {f['soc']} times, all eclipse."},
            {"type": "statement", "title": "Alarm fatigue", "icon": "😴", "big": "Too many wolves = no shepherd",
             "sub": "The car alarm that goes off for every keke: when the real thief comes, nobody moves",
             "notes": "Which alarms in your unit does everyone ignore?"},
            {"type": "code", "title": "The fix: add context, don't widen the limit",
             "code": f"too_low = bus[\"solar_array_current_a\"] < 20\nsunlit  = bus[\"eclipse_flag\"] == 0\nsmart_alarm = too_low & sunlit\n# {f['floor']} alarms  ->  {f['smart']} alarms, all real",
             "caption": "Ask 'which mode is the satellite in?' before checking the limit", "notes": "Conditioning on state."},
            {"type": "stats", "title": f"Battery temp above {TEMP_LIMIT:.0f} °C: same trap", "sub": "Recharging warms the pack for an hour after each eclipse",
             "stats": [[str(f['hot']), "alarms"], [str(f['hot_after']), "the hour after eclipse"], [str(f['hot_real']), "left after context"]],
             "notes": "The remaining 4 are the same solar-array dropout hours."},
            {"type": "section", "kicker": "Part 3", "title": "Where should the limit be?", "sub": "Let the data choose", "notes": "Section break."},
            {"type": "compare", "title": "The faults you want to catch widen your own limits",
             "left": ["📦", f"All sunlit hours: σ = {f['sun_sd']:.2f} A", f"Band {f['sun_lo']:.2f}–{f['sun_hi']:.2f} A catches exactly the {f['sun_flags']} dropouts"],
             "right": ["🧼", f"Clean hours only: σ = {f['clean_sd']:.2f} A", f"Band {f['clean_lo']:.2f}–{f['clean_hi']:.2f} A: {f['clean_flags']} alarms, {f['clean_rec']} normal recharge hours"],
             "notes": "Normal needs context. Day 2 builds it properly. Original says sigma ≈ 0.06; data says 0.59."},
            {"type": "stats", "title": "Raining is not the same as link down", "sub": f"August: {f['rain_h']} rainy hours, {f['outages']} real outages",
             "stats": [[str(f['cn_flags']), "alarms: 3σ from all hours"], [str(f['cn_real']), "of them real"],
                       [str(f['dry_flags']), "alarms: 3σ from dry hours"], [str(f['dry_real']), "of them real"]],
             "notes": "Link margin below 0 dB = down. Rain alone is not a fault."},
            {"type": "statement", "title": "The persistence trick, tested", "icon": "🙈",
             "big": f"“Only alarm after 2 hours” catches {f['persist']} of {f['outages']} outages",
             "sub": "Every August outage lasted exactly one hour", "notes": "Persistence buys quiet by going blind."},
            {"type": "flow", "title": "Uplink power is a reaction to rain: it leaks the answer", "steps": [
                ["🌧️", "Heavy rain", "the cause"],
                ["📉", "Signal fades", "C/N drops"],
                ["🔊", "Power control", f"{f['up_dry']:.1f} → {f['up_rain']:.1f} dBm (r\u00a0=\u00a0{f['up_corr']:.2f})"]],
             "notes": "Quiz: don't feed uplink_power_dbm to the detector."},
            {"type": "cards", "title": "Three shapes of trouble", "cards": [
                ["📍", "Spike", "a limit catches it, with context"],
                ["🪜", "Level shift", f"+{f['tw_post'] - f['tw_pre']:.1f} °C: fixed limit fires {f['tw_flags']} times"],
                ["🐢", "Drift", f"{f['cap0']:.0f} → {f['cap1']:.1f} Ah: a 95 Ah limit fires {f['cap95']} times"]],
             "notes": "Silent degradation. Days 2 and 3 fix these."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W3D1-exercise in Colab and save a copy", "Part A: count the wolves, add context",
                "Part B: let the data choose the limit", "Part C: rain, delays, leaks and the 3 shapes"],
             "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🚨", "A limit is a model: ask where every number came from"],
                ["🧠", "Add context, don't widen: eclipse, recharge and rain are normal states"],
                ["🪜", "Fixed limits catch spikes, not level shifts or slow drift"]],
             "next": "Next: Control Charts and Residuals", "notes": "Tease Day 2."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
def _bus():
    return pd.read_csv(data_path("bus_power_telemetry_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")

def _rf():
    return pd.read_csv(data_path("rf_link_quality_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")

def _num(x):
    return float(np.asarray(x).item()) if np.ndim(x) == 0 else float("nan")

def _c_a1(x):
    want = int(_bus()["eclipse_flag"].sum())
    return int(x) == want, f"{want} eclipse hours: one per night from 1 Sep to 16 Oct, always at 21:00 UTC.", \
        "Add up the eclipse_flag column: bus[\"eclipse_flag\"].sum()"

def _c_a2(x):
    want = int((_bus()["solar_array_current_a"] < 20).sum())
    return int(x) == want, f"{want} alarms from one innocent-looking limit. 🐺", "Count the True values: floor_alarm.sum()"

def _c_a3(x):
    b = _bus(); want = int(((b["solar_array_current_a"] < 20) & (b["eclipse_flag"] == 1)).sum())
    return int(x) == want, f"{want} of them are normal eclipse nights. Technically correct, operationally useless.", \
        "Combine both conditions with & and wrap each in brackets: (floor_alarm) & (bus[\"eclipse_flag\"] == 1)"

def _c_a4(x):
    b = _bus(); want = int((b["battery_soc_pct"] < 82).sum())
    ecl = int(((b["battery_soc_pct"] < 82) & (b["eclipse_flag"] == 1)).sum())
    return int(x) == want, f"{want} SoC alarms, and all {ecl} happen during eclipse. Not one of them is a fault.", \
        "Count where battery_soc_pct is below 82: (bus[\"battery_soc_pct\"] < 82).sum()"

def _c_a5(x):
    return int(x) == 0, "Yes: eclipse_flag == 0 means sunlit. Now the alarm only checks the limit when the sun is shining. 🌞", \
        "eclipse_flag is 1 in eclipse and 0 in sunlight. Which one do you want?"

def _c_b1(x):
    b = _bus(); s = b.loc[b["eclipse_flag"] == 0, "solar_array_current_a"]; want = s.mean() - 3 * s.std()
    return abs(_num(x) - want) < 0.02, f"Lower 3σ limit = {want:.2f} A. Now the number has a reason behind it.", \
        "mean minus three standard deviations: sunlit.mean() - 3 * sunlit.std()"

def _c_b2(x):
    b = _bus(); s = b.loc[b["eclipse_flag"] == 0, "solar_array_current_a"]; want = int((s < s.mean() - 3 * s.std()).sum())
    return int(x) == want, f"{want} hours below the band: exactly the solar-array dropouts. Zero false alarms. 🎯", \
        "Count the sunlit hours below low_limit: (sunlit < low_limit).sum()"

def _c_b3(x):
    b = _bus(); want = int(((b["battery_temp_c"] > 22) & (b["eclipse_flag"].shift(1) == 1)).sum())
    return int(x) == want, f"{want} temperature alarms are just the battery warming up after eclipse. Normal!", \
        "Combine hot and after_eclipse with &, then .sum()"

def _c_c1(x):
    r = _rf(); cn = r["cn_ratio_db"]; fl = cn < cn.mean() - 3 * cn.std(); real = fl & (r["link_margin_db"] < 0)
    want = (int(fl.sum()), int(real.sum()))
    return tuple(int(v) for v in x) == want, f"{want[0]} alarms, {want[1]} real outages: {want[0] - want[1]} times the rule just saw rain.", \
        "n_flags = cn_flags.sum(); n_real = (cn_flags & outage).sum()"

def _c_c2(x):
    r = _rf(); o = r["link_margin_db"] < 0; want = int((o & o.shift(1, fill_value=False)).sum())
    return int(x) == want, f"{want}! Every outage lasted one hour, so the 2-hour rule never fires. Quiet... and blind. 🙈", \
        "two_in_a_row.sum()"

def _c_c3(x):
    return str(x).strip().lower() == "no", "Correct: uplink power is the system reacting to rain. It would leak the answer. 🚰", \
        "Uplink power rises BECAUSE of rain. Is that a fault signal, or a rain signal?"

def _c_c4(x):
    norm = lambda s: str(s).strip().lower().replace("_", " ").replace("-", " ")
    got = tuple(norm(v) for v in x)
    want = ("spike", "level shift", "drift")
    wrong = [i + 1 for i, (g, w) in enumerate(zip(got, want)) if g != w and not (w == "level shift" and g == "shift")]
    return not wrong, "Spike, level shift, drift: the three shapes of trouble. Days 2 and 3 hunt the last two.", \
        f"Check chart(s) {wrong}. Choose from: spike, level shift, drift."

def _c_c5(x):
    bat = pd.read_csv(data_path("battery_health_daily"), parse_dates=["date"], index_col="date")
    want = int((bat["est_capacity_ah"] < 95).sum())
    return int(x) == want, f"{want}. Three years of fading and the alarm never says a word. That's silent degradation. 🐢", \
        "(bat[\"est_capacity_ah\"] < 95).sum()"

def _c_bonus(x):
    return str(pd.Timestamp(x).date()) == "2025-09-28", "28 September: the two-hour dropout. Both alarms are the same event. 🌶️", \
        "Look at the times printed by smart_alarm: which date appears twice?"

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "A5": _c_a5, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3,
          "C1": _c_c1, "C2": _c_c2, "C3": _c_c3, "C4": _c_c4, "C5": _c_c5, "BONUS": _c_bonus}
HINTS = {"C1": "Give two numbers: (n_flags, n_real)", "C4": "Give three words in quotes, e.g. (\"spike\", ...)"}
'''


def notebook_cells(setup_code):
    return [
        ("md", """# 🐺 Week 3 · Day 1: Alarms That Cry Wolf

**Today:** test the kind of alarm your NOC already uses, on satellite telemetry. Watch it cry wolf every eclipse night, then fix it with **context**, not a wider limit.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (**Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ First: **File → Save a copy in Drive**

**Rule book:** keep `W3D1-rulebook.pdf` open. It has every step and every common error."""),
        ("md", """## ▶️ STEP 0: Set up (run once, and again after every restart)

You should see `✅ Ready!`. If Colab says *"This notebook was not authored by Google"*, click **Run anyway**."""),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Count the wolves (20 min) 🐺

**The data:** `bus_power_telemetry_hourly`: four months of the satellite's power system, one row per hour.

| Column | Means |
|---|---|
| `solar_array_current_a` | power coming from the solar panels (amps). About 28 A in sunlight |
| `battery_soc_pct` | battery state of charge (%) |
| `battery_temp_c` | battery temperature (°C) |
| `eclipse_flag` | **1** = the Earth's shadow is on the satellite (it runs on battery), **0** = sunlit |

▶️ Load it with the recipe you know, then look at the solar-array current."""),
        ("code", 'bus = pd.read_csv(data_path("bus_power_telemetry_hourly"),\n                  parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n\ndisplay(bus.head())\nbus["solar_array_current_a"].plot(title="Solar-array current: every drop to zero is an eclipse night", lw=.8)\nplt.ylabel("amps")\nplt.show()'),
        ("md", """### A1 ✍️ How many eclipse hours?
`eclipse_flag` is 1 in eclipse and 0 otherwise. Adding up a column of 1s and 0s counts the 1s."""),
        ("task", 'eclipse_hours = ___\n\ncheck("A1", eclipse_hours)', 'eclipse_hours = bus["eclipse_flag"].sum()\n\ncheck("A1", eclipse_hours)'),
        ("md", """### A2 ✍️ The vendor's alarm: array current below 20 A
Imagine the alarm software says: *"solar-array current below 20 A = ALARM"*. The cell builds that alarm as a True/False column.
How many hours does it fire? (`.sum()` counts the Trues.)"""),
        ("task", 'floor_alarm = bus["solar_array_current_a"] < 20\n\nn_floor = ___\ncheck("A2", n_floor)',
         'floor_alarm = bus["solar_array_current_a"] < 20\n\nn_floor = floor_alarm.sum()\ncheck("A2", n_floor)'),
        ("md", """### A3 ✍️ How many of those alarms happened during eclipse?
Combine two True/False columns with **`&`** ("and"). Put each condition in brackets."""),
        ("task", 'n_floor_eclipse = ___\n\ncheck("A3", n_floor_eclipse)',
         'n_floor_eclipse = (floor_alarm & (bus["eclipse_flag"] == 1)).sum()\n\ncheck("A3", n_floor_eclipse)'),
        ("md", """### A4 ✍️ A second wolf: battery state of charge below 82%
The original code book suggests an alarm on `battery_soc_pct < 82`. How many times does it fire?"""),
        ("task", 'n_soc = ___\n\ncheck("A4", n_soc)', 'n_soc = (bus["battery_soc_pct"] < 82).sum()\n\ncheck("A4", n_soc)'),
        ("md", """### A5 ✍️ The fix: add context
Don't widen the limit. Tell the alarm to check it **only when the satellite is sunlit**.
Which value of `eclipse_flag` means *sunlit*? Then run the cell and look at the alarms that are left."""),
        ("task", 'SUNLIT = ___      # 0 or 1?\ncheck("A5", SUNLIT)\n\nassert SUNLIT is not None, "✍️ Fill in SUNLIT first."\nsmart_alarm = floor_alarm & (bus["eclipse_flag"] == SUNLIT)\nprint("alarms left:", smart_alarm.sum())\nprint(bus.index[smart_alarm].tolist())',
         'SUNLIT = 0        # 0 or 1?\ncheck("A5", SUNLIT)\n\nassert SUNLIT is not None, "✍️ Fill in SUNLIT first."\nsmart_alarm = floor_alarm & (bus["eclipse_flag"] == SUNLIT)\nprint("alarms left:", smart_alarm.sum())\nprint(bus.index[smart_alarm].tolist())'),
        ("md", """> 💡 Those few hours are **solar-array dropouts**: the array suddenly gives about half its power. NigComSat-1 was lost in 2008 after a solar-array failure. These are the alarms worth waking up for."""),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Where should the limit be? (15 min) 📏

*"Where did that number come from?"* The 20 A was a guess. Let the **data** choose: take the normal hours and use **mean − 3 × standard deviation** (3σ, "three sigma")."""),
        ("code", 'sunlit = bus.loc[bus["eclipse_flag"] == 0, "solar_array_current_a"]\nprint(f"sunlit mean = {sunlit.mean():.3f} A   standard deviation = {sunlit.std():.3f} A")'),
        ("md", """### B1 ✍️ The lower 3σ limit
Compute `mean − 3 × std` of `sunlit`."""),
        ("task", 'low_limit = ___\n\ncheck("B1", low_limit)', 'low_limit = sunlit.mean() - 3 * sunlit.std()\n\ncheck("B1", low_limit)'),
        ("md", """### B2 ✍️ How many sunlit hours fall below it?"""),
        ("task", 'n_below = ___\n\ncheck("B2", n_below)', 'n_below = (sunlit < low_limit).sum()\n\ncheck("B2", n_below)'),
        ("md", """### B3 ✍️ Same trap, different sensor: battery temperature
A fixed alarm says *battery hotter than 22 °C = ALARM*. ▶️ The cell plots five eclipse nights.
Then count how many alarms happen **in the hour right after an eclipse** (`.shift(1)` looks one row back)."""),
        ("code", 'hot = bus["battery_temp_c"] > 22\nafter_eclipse = bus["eclipse_flag"].shift(1) == 1      # True for the hour just after an eclipse hour\nprint("temperature alarms in total:", hot.sum())\n\nbus.loc["2025-09-22":"2025-09-26", "battery_temp_c"].plot(title="Battery temperature over five eclipse nights")\nplt.axhline(22, color="#E5484D", ls="--")\nplt.ylabel("°C")\nplt.show()'),
        ("task", 'n_hot_after_eclipse = ___\n\ncheck("B3", n_hot_after_eclipse)', 'n_hot_after_eclipse = (hot & after_eclipse).sum()\n\ncheck("B3", n_hot_after_eclipse)'),
        ("md", """> 💡 Recharging after an eclipse warms the battery. That's **normal**. With context (`hot & ~after_eclipse`), only the real events are left. (`~` means "not".)"""),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Rain, delays, leaks and the 3 shapes (25 min) 🌧️

**The data:** `rf_link_quality_hourly`: the Ka-band link in August, the wettest month.
`cn_ratio_db` = signal quality (C/N). `link_margin_db` = how far above "link dead" we are. **Below 0 dB = outage.**"""),
        ("code", 'rf = pd.read_csv(data_path("rf_link_quality_hourly"),\n                 parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n\ncn = rf["cn_ratio_db"]\noutage = rf["link_margin_db"] < 0\ncn_flags = cn < cn.mean() - 3 * cn.std()          # a "3-sigma" alarm on signal quality\nprint("rainy hours:", (rf["rain_rate_mmhr"] > 0).sum(), "   real outages:", outage.sum())'),
        ("md", """### C1 ✍️ Raining or really down?
How many hours does `cn_flags` fire, and how many of those are **real outages**? Give two numbers."""),
        ("task", 'n_flags = ___\nn_real = ___\n\ncheck("C1", (n_flags, n_real))', 'n_flags = cn_flags.sum()\nn_real = (cn_flags & outage).sum()\n\ncheck("C1", (n_flags, n_real))'),
        ("md", """### C2 ✍️ Test the "persistence" trick
Alarm software often waits: *"only alarm if it's bad 2 hours in a row"*. How many outage hours would that catch?"""),
        ("task", 'two_in_a_row = outage & outage.shift(1, fill_value=False)\n\ncaught = ___\ncheck("C2", caught)',
         'two_in_a_row = outage & outage.shift(1, fill_value=False)\n\ncaught = two_in_a_row.sum()\ncheck("C2", caught)'),
        ("md", """### C3 ✍️ Should uplink power go into the outage detector?
▶️ Run the first line: it shows how strongly uplink power moves with rain. Then answer `"yes"` or `"no"`."""),
        ("code", 'print("correlation of uplink power with rain:", round(rf["uplink_power_dbm"].corr(rf["rain_rate_mmhr"]), 2))'),
        ("task", 'use_uplink_power = ___     # "yes" or "no"\n\ncheck("C3", use_uplink_power)', 'use_uplink_power = "no"     # "yes" or "no"\n\ncheck("C3", use_uplink_power)'),
        ("md", """### C4 ✍️ Name the shape
▶️ The cell draws three real series. Which shape of trouble is each one: `"spike"`, `"level shift"` or `"drift"`?"""),
        ("code", 'tw = pd.read_csv(data_path("twta_thermal_daily"), parse_dates=["date"], index_col="date")\nbat = pd.read_csv(data_path("battery_health_daily"), parse_dates=["date"], index_col="date")\n\nfig, ax = plt.subplots(1, 3, figsize=(14, 3))\nbus.loc["2025-08-15":"2025-08-21", "solar_array_current_a"].plot(ax=ax[0], title="Chart 1: array current, one week")\ntw.loc["2025-03":"2025-07", "twta_temp_c"].plot(ax=ax[1], title="Chart 2: amplifier temperature")\nbat["est_capacity_ah"].plot(ax=ax[2], title="Chart 3: battery capacity, 3 years")\nplt.tight_layout()\nplt.show()'),
        ("task", 'shapes = (___, ___, ___)\n\ncheck("C4", shapes)', 'shapes = ("spike", "level shift", "drift")\n\ncheck("C4", shapes)'),
        ("md", """### C5 ✍️ Silent degradation
A fixed alarm says *battery capacity below 95 Ah = ALARM*. Over three years, how many days does it fire?"""),
        ("task", 'n_capacity_alarms = ___\n\ncheck("C5", n_capacity_alarms)', 'n_capacity_alarms = (bat["est_capacity_ah"] < 95).sum()\n\ncheck("C5", n_capacity_alarms)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task
Look back at the times printed by `smart_alarm` in A5. One **date** appears twice: the same dropout lasted two hours. Which date? (Type it as `"YYYY-MM-DD"`.)"""),
        ("task", 'double_alarm_date = ___\n\ncheck("BONUS", double_alarm_date)', 'double_alarm_date = "2025-09-28"\n\ncheck("BONUS", double_alarm_date)'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- **A fixed limit is already an anomaly-detection model.** Ask of every limit: *where did that number come from?*
- **Eclipse, recharge and rain are normal states, not faults.** A limit that ignores them cries wolf, and alarm fatigue sets in.
- **Fix it with context** (`& (bus["eclipse_flag"] == 0)`), not by widening the limit.
- **3σ from the data** gives a limit with a reason, but "normal" must be defined per state.
- **Persistence rules buy quiet by going blind** to short events.
- **Don't feed a detector a column that reacts to the cause** (uplink power leaks the rain).
- **Three shapes:** spike, level shift, drift. Fixed limits only really catch spikes.

**Next time:** *Control Charts and Residuals*: a normal that moves with the data. 📈

<sub>Data: synthetic teaching datasets from the original Week 4 code book (`Time-series/week-04`). Safe to use in AI assistants. Real NIGCOMSAT data is not.</sub>"""),
    ]
