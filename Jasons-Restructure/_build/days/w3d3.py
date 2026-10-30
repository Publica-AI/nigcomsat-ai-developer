"""Week 3 · Day 3: The Slow Creep: Drift and CUSUM."""
from __future__ import annotations

import html as _html

import numpy as np
import pandas as pd

from common import BRAND as B, ORIGINALS
from svgcharts import bars_svg, line_svg, lines_svg, spark_svg
from webdeck import logos_title_block

CODE = "W3D3"
TITLE = "The Slow Creep: Drift and CUSUM"

D4 = ORIGINALS / "week-04" / "data"
D3 = ORIGINALS / "week-03" / "data"
SHIFT = pd.Timestamp("2025-05-12")      # where the amplifier's step shows up in the week-04 file
KNEE = pd.Timestamp("2025-04-01")       # where the battery starts fading faster
FAULT = pd.Timestamp("2025-02-10")      # the small practice fault WE add on purpose (+0.3 °C)
FAULT_SIZE = 0.3
TOY_X = [0.3, -0.2, 0.4, 1.0, 1.2, 0.9, 1.1]
TOY_K, TOY_H = 0.5, 2.0


# =============================================================================
# DATA + FACTS (every number on a slide comes from here)
# =============================================================================
def expected_temp(df):
    """'Normal' amplifier temperature, learned from 2024: drive level + sun angle + slow ageing.
    Two passes: the second ignores obvious one-off spikes so they don't bend 'normal'."""
    d = df.index.day_of_year.to_numpy()
    age = (df.index - pd.Timestamp("2024-01-01")).days.to_numpy()
    X = np.column_stack([np.ones(len(df)), df["rf_drive_pct"].to_numpy(),
                         np.sin(2 * np.pi * d / 365.25), np.cos(2 * np.pi * d / 365.25), age])
    y = df["twta_temp_c"].to_numpy()
    learn = df.index < "2025-01-01"
    coef, *_ = np.linalg.lstsq(X[learn], y[learn], rcond=None)
    r = y - X @ coef
    keep = learn & (np.abs(r) < 3 * r[learn].std())
    coef, *_ = np.linalg.lstsq(X[keep], y[keep], rcond=None)
    return pd.Series(X @ coef, index=df.index)


def cusum(values, k):
    S, out = 0.0, []
    for x in values:
        S = max(0.0, S + x - k)
        out.append(S)
    return out


def alarm_days(x, k, h):
    """CUSUM that resets to zero after each alarm (what you do once someone has looked at it)."""
    S, out = 0.0, []
    for day, v in x.items():
        S = max(0.0, S + v - k)
        if S > h:
            out.append(day)
            S = 0.0
    return out


def fade_rate(s):
    x = np.arange(len(s))
    return float(np.polyfit(x, s.to_numpy(), 1)[0] * 365)


def rolling_slope(s, window=90):
    x = np.arange(window)
    return s.rolling(window).apply(lambda w: np.polyfit(x, w, 1)[0] * 365, raw=True)


def facts():
    tw = pd.read_csv(D4 / "twta_thermal_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    t = tw["twta_temp_c"]
    f = {"tw": tw}
    f["mean"], f["sd"] = t.mean(), t.std()
    f["ceiling"] = f["mean"] + 3 * f["sd"]
    f["max"], f["max_day"] = t.max(), t.idxmax()
    f["n_point"] = int((t > f["ceiling"]).sum())
    pre = t[SHIFT - pd.Timedelta(days=30):SHIFT - pd.Timedelta(days=1)]
    post = t[SHIFT:SHIFT + pd.Timedelta(days=29)]
    f["pre_mean"], f["pre_sd"], f["post_mean"] = pre.mean(), pre.std(), post.mean()
    f["jump"] = f["post_mean"] - f["pre_mean"]
    f["jump_sigma"] = f["jump"] / f["pre_sd"]
    f["global_sigma_jump"] = f["jump"] / f["sd"]

    resid = t - expected_temp(tw)
    r24 = resid[:"2024-12-31"]
    sigma = r24[r24.abs() < 3 * r24.std()].std()
    f["resid"], f["sigma"] = resid, sigma
    f["k"], f["h"] = 0.5 * sigma, 5 * sigma
    f["after_mean"] = resid[SHIFT:].mean()
    f["before_2025_mean"] = resid["2025-01-01":SHIFT - pd.Timedelta(days=1)].mean()
    r25 = resid["2025-01-01":]
    S25 = pd.Series(cusum(r25.to_numpy(), f["k"]), index=r25.index)
    f["S25"] = S25
    f["first_alarm"] = S25[S25 > f["h"]].index.min()
    f["S_eve"] = S25[SHIFT - pd.Timedelta(days=1)]
    f["S_day"] = S25[SHIFT]
    f["spike_days"] = list(r24[r24.abs() >= 3 * r24.std()].index)

    # practice: the clean stretch before the real shift, minus the known hot spike, plus a small fault
    p = resid[:SHIFT - pd.Timedelta(days=1)]
    p = p[~((p.index < "2025-01-01") & (p.abs() > 3 * sigma))].copy()
    p.loc[FAULT:] += FAULT_SIZE
    f["practice"] = p
    Sp = pd.Series(cusum(p.to_numpy(), f["k"]), index=p.index)
    f["Sp"] = Sp
    f["p_alarm"] = Sp[Sp > f["h"]].index.min()
    zeros = Sp[:f["p_alarm"]]
    f["p_last_zero"] = zeros[zeros == 0].index.max()
    f["p_onset"] = f["p_last_zero"] + pd.Timedelta(days=1)
    f["p_point_hits_30"] = int((p[FAULT:FAULT + pd.Timedelta(days=29)] > 3 * sigma).sum())
    f["p_clean_days"] = int((p.index < FAULT).sum())
    table = []
    for m in (2, 3, 5, 8, 10):
        al = alarm_days(p, f["k"], m * sigma)
        fa = [a for a in al if a < FAULT]
        aft = [a for a in al if a >= FAULT]
        table.append((m, len(fa), (aft[0] - FAULT).days))
    f["tradeoff"] = table

    toy = cusum(TOY_X, TOY_K)
    f["toy"] = [round(v, 2) for v in toy]
    f["toy_alarm_day"] = next(i + 1 for i, v in enumerate(toy) if v > TOY_H)
    last0 = max(i + 1 for i, v in enumerate(toy[:f["toy_alarm_day"]]) if v == 0)
    f["toy_onset_day"] = last0 + 1

    bat = pd.read_csv(D4 / "battery_health_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    cap = bat["est_capacity_ah"]
    f["cap"] = cap
    f["cap_start"], f["cap_end"], f["cap_min"] = cap.iloc[0], cap.iloc[-1], cap.min()
    f["below95"] = int((cap < 95).sum())
    f["rate_before"] = fade_rate(cap[:KNEE - pd.Timedelta(days=1)])
    f["rate_after"] = fade_rate(cap[KNEE:])
    sl = rolling_slope(cap, 90)
    f["slope90"] = sl
    pre_sl = sl[:KNEE - pd.Timedelta(days=1)].dropna()
    f["slope_pre_lo"], f["slope_pre_hi"] = pre_sl.min(), pre_sl.max()
    f["warn_line"] = -3.0
    f["first_warning"] = sl[sl < f["warn_line"]].index.min()
    f["warn_delay"] = (f["first_warning"] - KNEE).days
    f["slope_end"] = sl.iloc[-1]
    b3 = pd.read_csv(D3 / "battery_health_daily.csv", parse_dates=["date"], index_col="date")["est_capacity_ah"]
    f["cap3_end"] = b3.iloc[-1]
    return f


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


def _d(ts):
    return f"{ts.day} {ts.strftime('%b %Y')}"


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    f = facts()
    t = f["tw"]["twta_temp_c"]
    n = len(t)

    def i_of(series, date):
        return int(series.index.get_indexer([pd.Timestamp(date)])[0])

    # title motif: a quiet line that creeps up a step
    rng = np.random.default_rng(5)
    creep = np.r_[rng.normal(0, .35, 40), rng.normal(2.2, .35, 30)]
    title_svg = spark_svg(creep, w=560, h=260, color=B["gold"], delay=".6s")

    # rent hook (illustration)
    rents = [500, 525, 550, 580, 610, 650]
    extra = sum(r - rents[0] for r in rents)
    rent_svg = bars_svg([f"Year {i + 1}" for i in range(6)], rents, w=860, h=380, ymin=0, ymax=720,
                        highlight=(5,), fmt="₦{:.0f}k")

    # three shapes
    x = np.arange(60)
    noise = np.random.default_rng(2).normal(0, .25, 60)
    spike = noise.copy()
    spike[34] += 3.2
    shift = noise + np.where(x >= 32, 1.8, 0)
    drift = noise + np.where(x >= 25, (x - 25) * .07, 0)
    shapes = [("⚡", "Spike", "one reading way off, then back", spike, B["bad"]),
              ("🪜", "Level shift", "a step to a new level that holds", shift, B["gold"]),
              ("🐌", "Drift", "a slow lean; the slope changes", drift, B["teal_d"])]
    shape_cards = "".join(
        f'<div class="card anim a-pop" style="--d:{.3 + k * .3:.1f}s;text-align:center;padding:28px">'
        f'<div style="font-size:64px">{e}</div><h3 style="margin-top:6px">{tt}</h3>'
        f'<p class="small" style="min-height:58px">{d}</p>{spark_svg(v, w=340, h=120, color=c, delay=f"{.6 + k * .3:.1f}s")}</div>'
        for k, (e, tt, d, v, c) in enumerate(shapes))

    # TWTA full chart
    xl = [(0, "Jan 2024"), (i_of(t, "2024-07-01"), "Jul 2024"), (i_of(t, "2025-01-01"), "Jan 2025"),
          (i_of(t, "2025-07-01"), "Jul 2025"), (n - 1, "Dec 2025")]
    twta_svg = line_svg(t.values, w=1420, h=440, ymin=58, ymax=71, yticks=[(60, "60 °C"), (64, "64"), (68, "68")],
                        xlabels=xl, hline=(f["ceiling"], f"3σ ceiling {f['ceiling']:.1f} °C: never crossed", B["bad"]),
                        markers=[(i_of(t, SHIFT), "the step", B["gold"])], dur="3s")

    # zoom: 30 days before/after
    z = t[SHIFT - pd.Timedelta(days=30):SHIFT + pd.Timedelta(days=29)]
    zn = len(z)
    pre_line = np.where(np.arange(zn) < 30, f["pre_mean"], np.nan)
    post_line = np.where(np.arange(zn) >= 30, f["post_mean"], np.nan)
    zoom_svg = lines_svg([dict(values=z.values, color="#EAF2FB", stroke=3, label=None, delay=".3s"),
                          dict(values=pre_line, color=B["teal_d"], stroke=3, dash="10 8", label=f"{f['pre_mean']:.2f}", delay="1.6s"),
                          dict(values=post_line, color=B["gold"], stroke=3, dash="10 8", label=f"{f['post_mean']:.2f}", delay="2.0s")],
                         w=900, h=420, ymin=64.3, ymax=68.3, yticks=[(65, "65 °C"), (66, "66"), (67, "67"), (68, "68")],
                         xlabels=[(0, _d(z.index[0])[:-5]), (30, _d(SHIFT)[:-5]), (zn - 1, _d(z.index[-1])[:-5])])

    # residuals 2025
    r25 = f["resid"]["2025-01-01":]
    r_svg = line_svg(r25.values, w=1420, h=330, ymin=-0.9, ymax=2.9, yticks=[(0, "0"), (1, "+1"), (2, "+2 °C")],
                     xlabels=[(0, "Jan 2025"), (i_of(r25, "2025-05-01"), "May"), (i_of(r25, "2025-09-01"), "Sep"), (len(r25) - 1, "Dec 2025")],
                     hline=(3 * f["sigma"], f"3σ of the leftovers = {3 * f['sigma']:.2f} °C", B["teal_d"]), dur="2.6s")

    # CUSUM on the real amplifier, zoomed around the step
    Sz = f["S25"][SHIFT - pd.Timedelta(days=18):SHIFT + pd.Timedelta(days=14)]
    cus_svg = line_svg(Sz.values, w=1420, h=380, ymin=0, ymax=float(Sz.max()) * 1.08,
                       yticks=[(0, "0"), (10, "10"), (20, "20")],
                       xlabels=[(0, _d(Sz.index[0])[:-5]), (18, _d(SHIFT)[:-5]), (len(Sz) - 1, _d(Sz.index[-1])[:-5])],
                       hline=(f["h"], f"h = 5σ = {f['h']:.2f}", B["bad"]),
                       markers=[(18, f"🚨 alarm on {_d(f['first_alarm'])[:-5]}", B["bad"])], dur="2.4s", area=True)

    # practice: point rule vs CUSUM
    p = f["practice"]["2025-01-01":]
    ip = i_of(p, FAULT)
    p_svg = line_svg(p.values, w=640, h=320, ymin=-0.9, ymax=1.2, area=False, stroke=2.5,
                     yticks=[(0, "0"), (3 * f["sigma"], "3σ")],
                     xlabels=[(0, "Jan"), (ip, "10 Feb"), (len(p) - 1, "May")],
                     hline=(3 * f["sigma"], "", B["teal_d"]), dur="2s")
    Spz = f["Sp"]["2025-01-01":"2025-03-01"]
    ia = i_of(Spz, f["p_alarm"])
    sp_svg = line_svg(Spz.values, w=640, h=320, ymin=0, ymax=float(Spz.max()) * 1.1, area=True, stroke=3,
                      color=B["gold"], xlabels=[(0, "Jan"), (len(Spz) - 1, "1 Mar")],
                      hline=(f["h"], "h", B["bad"]),
                      markers=[(ia, "🚨", B["bad"])], dur="2s")

    # battery
    cap = f["cap"]
    nb = len(cap)
    cap_svg = line_svg(cap.values, w=1420, h=400, ymin=94, ymax=104, yticks=[(95, "95 Ah"), (100, "100"), (103, "103")],
                       xlabels=[(0, "Jan 2023"), (i_of(cap, "2024-01-01"), "Jan 2024"), (i_of(cap, "2025-01-01"), "Jan 2025"), (nb - 1, "Dec 2025")],
                       hline=(95, "", B["bad"]),
                       markers=[(i_of(cap, KNEE), "fade speeds up", B["gold"])], dur="3s")
    sl = f["slope90"]["2024-01-01":]
    ns = len(sl)
    sl_svg = line_svg(sl.values, w=1420, h=380, ymin=-4.0, ymax=-1.0,
                      yticks=[(-1.5, "-1.5"), (-2.5, "-2.5"), (-3.5, "-3.5")],
                      xlabels=[(0, "Jan 2024"), (i_of(sl, "2024-07-01"), "Jul 2024"), (i_of(sl, "2025-01-01"), "Jan 2025"), (ns - 1, "Dec 2025")],
                      hline=(f["warn_line"], "", B["bad"]),
                      markers=[(i_of(sl, f["first_warning"]), f"crosses {_d(f['first_warning'])[:-5]}", B["gold"])], dur="2.8s", area=False)
    rate_svg = bars_svg(["before April 2025", "after April 2025"], [-f["rate_before"], -f["rate_after"]], w=760, h=380,
                        ymin=0, ymax=4.6, highlight=(1,), fmt="{:.2f} Ah/yr")

    # toy table
    toy_rows = "".join(
        f'<tr><td>Day {i + 1}</td><td>{x:+.1f}</td><td class="step" data-step="{i + 1}" style="font-weight:800;'
        f'color:{"#FF6B6F" if v > TOY_H else ("#F5B83D" if v > 0 else "#9DB0C6")}">{v:.1f}{" 🚨" if i + 1 == f["toy_alarm_day"] else ""}</td></tr>'
        for i, (x, v) in enumerate(zip(TOY_X, f["toy"])))

    trade_rows = "".join(
        f'<tr style="{"background:rgba(245,184,61,.12)" if m == 5 else ""}"><td><b>{m}σ</b></td><td>{fa}</td><td>{dl} day{"s" if dl != 1 else ""}</td></tr>'
        for m, fa, dl in f["tradeoff"])

    slides = [
        S(f"""
<div class="row" style="gap:40px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Week 3 · Day 3</div>
  <h1 class="anim" style="--d:.2s">The Slow Creep<br><span class="hl">Drift &amp; CUSUM</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:26px">Some faults never shout. Today you build a detector<br>that keeps the receipts. 🧾</p>
  <div class="anim" style="--d:.8s;margin-top:40px">{logos_title_block()}</div>
 </div>
 <div class="anim a-right" style="--d:.4s;flex:.8;text-align:center">{title_svg}<p class="small">no single reading looks scary… but something changed</p></div>
</div>""", "Welcome back. Days 1 and 2 caught readings that jump out. Today is about faults that creep: a step that holds, a slope that bends. "
             "By the end everyone has written a CUSUM detector from scratch."),

        S("""
<div class="kicker anim">Today's mission · 2 hours</div>
<h2 class="anim" style="--d:.1s">Three moves</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:380px;padding:40px 30px"><div class="icon">🙈</div><h3>See what 3σ misses</h3><p class="small">the amplifier's sneaky step</p></div>
  <div class="arrow anim a-fade" style="--d:.6s"></div>
  <div class="box on anim a-pop" style="--d:.8s;min-width:380px;padding:40px 30px"><div class="icon">🧾</div><h3>Build CUSUM</h3><p class="small">add up small leftovers</p></div>
  <div class="arrow anim a-fade" style="--d:1.1s"></div>
  <div class="box on anim a-pop" style="--d:1.3s;min-width:380px;padding:40px 30px"><div class="icon">🔋</div><h3>Watch the slope</h3><p class="small">a battery ageing faster</p></div>
</div>
<div class="row anim" style="--d:1.7s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min hook</span><span class="pill">🎤 30 min slides</span><span class="pill teal">🧑🏾‍💻 60 min hands-on</span><span class="pill gold">🏁 20 min wrap-up + project checkpoint</span>
</div>""", "Three moves. The hands-on is where the CUSUM gets written. We end with the final-project Checkpoint 2."),

        S(f"""
<div class="kicker anim">Quick question</div>
<h2 class="anim" style="--d:.1s">Did your landlord “increase” the rent? 🏠</h2>
<div class="row" style="gap:40px;align-items:center;margin-top:10px">
  <div class="anim" style="--d:.2s">{rent_svg}<p class="small">illustration, not real rent data 😅</p></div>
  <div class="col" style="flex:1;gap:20px">
    <div class="card step" data-step="1"><h3>Each year: “small-small” 🤏</h3><p class="muted">₦25k here, ₦30k there. No single year shocks you.</p></div>
    <div class="card step glow" data-step="2"><h3 class="hl">Add up the extra: ₦{extra}k</h3><p>Over 6 years you paid ₦{extra}k more than year 1. <b>That</b> is what CUSUM does: it keeps the receipts.</p></div>
  </div>
</div>
""",
          "Get the laugh. Everyone knows the landlord who adds a little every year. Looking at one year at a time, nothing looks wrong. "
          "Adding up the small extras makes the change obvious. That is the whole idea of CUSUM."),

        S(f"""
<div class="kicker anim">Three shapes of trouble</div>
<h2 class="anim" style="--d:.1s">Not every fault is a spike</h2>
<div class="grid3" style="margin-top:20px">{shape_cards}</div>
<p class="anim" style="--d:1.6s;margin-top:34px;text-align:center">Days 1–2 caught <b class="bad">spikes</b>. Today: the <b class="hl">level shift</b> and the <b class="teal">drift</b>.</p>""",
          "Quiz question: a step to a new level that holds is a LEVEL SHIFT. A drift is a slow lean. A spike goes up and comes back."),

        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">The amplifier's sneaky step</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">🌡️ TWTA: the satellite's loudspeaker. It pushes our signal down to Nigeria, and it gets hot.</p>""",
          "Section break. TWTA = travelling-wave tube amplifier. It amplifies the signal before it is beamed down. Heat is normal; a jump in heat is not.",
          cls="center"),

        S(f"""
<div class="kicker anim">twta_thermal_daily.csv · week-04 version</div>
<h2 class="anim" style="--d:.1s;font-size:52px">Two years of amplifier temperature</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{twta_svg}</div>
<div class="row anim" style="--d:2.8s;margin-top:20px;gap:14px;align-items:center">
  <span class="pill bad">3σ point rule: {f['n_point']} alarms</span>
  <span class="pill">hottest day {f['max']:.2f} °C ({_d(f['max_day'])})</span>
  <span class="pill gold">the step is in there. Can you see it?</span>
</div>""",
          f"Global mean {f['mean']:.2f} °C, sd {f['sd']:.2f}. The 3-sigma ceiling is {f['ceiling']:.2f}; the hottest day ever is {f['max']:.2f}. "
          f"So a single-point 3-sigma rule fires {f['n_point']} times in two years. The step is hiding inside the normal yearly swing."),

        S(f"""
<div class="kicker anim">Zoom in: 30 days before vs 30 days after</div>
<h2 class="anim" style="--d:.1s">Against its neighbours, it's a giant</h2>
<div class="row" style="gap:36px;align-items:center">
  <div class="card anim" style="--d:.2s;padding:14px 16px">{zoom_svg}</div>
  <div class="col" style="flex:1;gap:18px">
    <div class="card anim a-right" style="--d:.8s;padding:22px 26px"><div class="stat" style="font-size:80px">+<span class="count" data-to="{f['jump']:.2f}" data-dec="2" data-d="1">0</span> °C</div><div class="stat-label">jump in average</div></div>
    <div class="card anim a-right glow" style="--d:1.1s;padding:22px 26px"><div class="stat hl" style="font-size:80px"><span class="count" data-to="{f['jump_sigma']:.1f}" data-dec="1" data-d="1.3">0</span>σ</div><div class="stat-label">vs the local wobble ({f['pre_sd']:.2f} °C)</div></div>
    <div class="card anim a-right" style="--d:1.4s;padding:22px 26px"><div class="stat muted" style="font-size:80px">{f['global_sigma_jump']:.1f}σ</div><div class="stat-label">vs the whole two years (sd {f['sd']:.2f})</div></div>
  </div>
</div>""",
          f"30 days before 12 May 2025: {f['pre_mean']:.2f} °C with a local sd of {f['pre_sd']:.2f}. 30 days after: {f['post_mean']:.2f}. "
          f"Jump {f['jump']:.2f} °C = {f['jump_sigma']:.1f} sigma locally, but only {f['global_sigma_jump']:.1f} sigma against the whole series. "
          "That is quiz question: no single reading looks extreme against the whole series."),

        S(f"""
<div class="kicker anim">Step 1 · yesterday's trick</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Take away what you already know</h2>
<div class="flow anim" style="--d:.2s;margin-bottom:18px;justify-content:center">
  <div class="box"><h3>🌡️ actual</h3></div><div class="arrow"></div>
  <div class="box"><h3>➖ expected</h3><p class="small">drive level + sun angle + slow ageing, learned from 2024</p></div><div class="arrow"></div>
  <div class="box on"><h3>🧩 leftovers</h3><p class="small">residuals</p></div>
</div>
<div class="card anim" style="--d:.5s;padding:14px 16px">{r_svg}</div>
<div class="row anim" style="--d:2.6s;margin-top:16px;gap:14px">
  <span class="pill teal">Jan to 11 May 2025: leftovers average {f['before_2025_mean']:+.2f} °C</span>
  <span class="pill gold">from 12 May: +{f['after_mean']:.2f} °C, and it stays</span>
</div>""",
          f"Residual = actual minus expected. Expected is learned from 2024 only. In early 2025 the leftovers average {f['before_2025_mean']:+.2f} °C with sd {f['sigma']:.2f}. "
          f"From 12 May they sit at +{f['after_mean']:.2f} °C. That matches the +1.8 °C step hidden in the file."),

        S("""
<div class="kicker anim">Step 2 · the CUSUM idea</div>
<h2 class="anim" style="--d:.1s">Keep a running total of small leftovers 🧾</h2>
<pre class="code anim" style="--d:.3s;font-size:34px;text-align:center">S = max(0, S + leftover − k)        # every day</pre>
<div class="grid3" style="margin-top:30px">
  <div class="card anim a-pop" style="--d:.6s"><div class="icon">➕</div><h3>Add today's leftover</h3><p class="muted">a bit hot? S grows a bit</p></div>
  <div class="card anim a-pop" style="--d:.9s"><div class="icon">🤏</div><h3>Minus the slack k</h3><p class="muted">ordinary noise can't pile up</p></div>
  <div class="card anim a-pop" style="--d:1.2s"><div class="icon">🚨</div><h3>S above h → alarm</h3><p class="muted">h = how much evidence you need</p></div>
</div>
<p class="anim" style="--d:1.6s;margin-top:30px;text-align:center"><b>max(0, …)</b> means S never goes below zero: good days can't “bank” credit. 🏦❌</p>""",
          "Quiz question: CUSUM accumulates small deviations from target, so a sustained change becomes a clear slope. The max(0, ...) floor stops long calm periods hiding a later fault."),

        S(f"""
<div class="kicker anim">Do it by hand · k = {TOY_K}, h = {TOY_H}</div>
<h2 class="anim" style="--d:.1s">Seven days, one receipt book</h2>
<div class="row" style="gap:46px;align-items:flex-start">
  <table class="anim" style="--d:.2s;font-size:30px;border-collapse:collapse;min-width:560px" cellpadding="10">
    <tr style="color:var(--muted);font-size:24px"><td>day</td><td>leftover</td><td>S</td></tr>{toy_rows}</table>
  <div class="col" style="flex:1;gap:20px">
    <div class="card step" data-step="4"><h3 class="hl">The change started on day {f['toy_onset_day']}</h3><p class="muted">the day after S was last zero</p></div>
    <div class="card step" data-step="7" style="border-color:#E5484D"><h3 class="bad">The alarm rang on day {f['toy_alarm_day']}</h3><p>Alarm date ≠ start date. CUSUM needs time to collect evidence. ⏳</p></div>
  </div>
</div>""",
          f"Press next to fill S one day at a time. Days 1–3: S stays 0 (noise minus slack). Day 4 starts the climb. S passes h = {TOY_H} on day {f['toy_alarm_day']}. "
          f"Quiz: the alarm date is NOT the date the change began. Estimate the start as the day after S was last zero: day {f['toy_onset_day']}."),

        S(f"""
<div class="kicker anim">The two knobs</div>
<h2 class="anim" style="--d:.1s">k and h: set them from σ</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🤏</div><h3>k = 0.5 × σ: the slack</h3><p class="muted">Ignore wobble smaller than half a σ. Ordinary noise does <b>not</b> accumulate.</p>
    <p style="margin-top:12px">Our amplifier: σ = {f['sigma']:.2f} °C → <b class="hl">k = {f['k']:.2f} °C</b></p></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">🚨</div><h3>h = 5 × σ: the decision limit</h3><p class="muted">How much evidence before you shout. Low h = fast but noisy. High h = calm but late.</p>
    <p style="margin-top:12px">Our amplifier: <b class="hl">h = {f['h']:.2f} °C</b></p></div>
</div>""",
          "Quiz question: k = 0.5 sigma is slack, so ordinary noise does not accumulate. h is the decision threshold. Both are measured in sigma of the leftovers from a calm reference period (2024)."),

        S(f"""
<div class="kicker anim">CUSUM on the real amplifier · watching from Jan 2025</div>
<h2 class="anim" style="--d:.1s;font-size:52px">The receipts pile up on day one</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{cus_svg}</div>
<div class="row anim" style="--d:2.6s;margin-top:18px;gap:14px">
  <span class="pill">S on {_d(SHIFT - pd.Timedelta(days=1))[:-5]}: {f['S_eve']:.2f} (below h)</span>
  <span class="pill bad">S on {_d(SHIFT)[:-5]}: {f['S_day']:.2f} 🚨</span>
  <span class="pill gold">delay: {(f['first_alarm'] - SHIFT).days} days, because this step is big ({f['after_mean'] / f['sigma']:.0f}σ of leftovers)</span>
</div>""",
          f"Run CUSUM on the 2025 leftovers with k = {f['k']:.2f}, h = {f['h']:.2f}. First alarm: {_d(f['first_alarm'])}, the same day the step began. "
          "With the yearly swing removed, this step is huge. CUSUM really earns its keep on smaller faults: next slide."),

        S(f"""
<div class="kicker anim">Practice fault: we add +{FAULT_SIZE} °C on purpose</div>
<h2 class="anim" style="--d:.1s;font-size:54px">A small fault the point rule never sees</h2>
<div class="grid2">
  <div class="card anim" style="--d:.2s;padding:18px"><h3 style="font-size:26px">👀 Leftovers vs the 3σ line</h3>{p_svg}
    <p style="font-size:24px"><b class="bad">{f['p_point_hits_30']} hits</b> in the 30 days after the fault</p></div>
  <div class="card anim glow" style="--d:.5s;padding:18px"><h3 style="font-size:26px">🧾 CUSUM</h3>{sp_svg}
    <p style="font-size:24px">alarm <b class="hl">{_d(f['p_alarm'])}</b>, {(f['p_alarm'] - FAULT).days} days after it began</p></div>
</div>
<p class="anim step" data-step="1" style="margin-top:16px;text-align:center">Where did it start? S was last zero on {_d(f['p_last_zero'])[:-5]} → change began <b class="hl">{_d(f['p_onset'])}</b> ✅</p>""",
          f"We add +{FAULT_SIZE} °C (about {FAULT_SIZE / f['sigma']:.1f} sigma) to the calm leftovers from {_d(FAULT)}. "
          f"The point rule sees nothing for 30 days. CUSUM alarms on {_d(f['p_alarm'])}, and walking back to the last zero recovers the true start date."),

        S(f"""
<div class="kicker anim">Choosing h · same practice fault, {f['p_clean_days']} calm days</div>
<h2 class="anim" style="--d:.1s">Fast and noisy, or calm and late?</h2>
<div class="row" style="gap:40px;align-items:center">
  <div class="card anim" style="--d:.2s;padding:20px 26px"><table style="font-size:30px;border-collapse:collapse;min-width:660px" cellpadding="12">
    <tr style="color:var(--muted);font-size:22px"><td>h</td><td>false alarms</td><td>caught after</td></tr>{trade_rows}</table></div>
  <div class="col" style="flex:1;gap:20px">
    <div class="card anim a-right" style="--d:.6s"><h3>⚖️ Your choice depends on the cost</h3><p class="muted">Missing a hot amplifier = expensive. A wasted call-out = annoying. Pick h on purpose, and write it down.</p></div>
    <div class="card anim a-right" style="--d:.9s"><h3>🔄 After an alarm: reset</h3><p class="muted">Once someone has checked it, set S back to 0 (or re-learn “normal”). Otherwise CUSUM shouts every day.</p></div>
  </div>
</div>""",
          "This is the trade-off table from the bonus task. Very low h catches the fault in a day but cries wolf. Our h = 5 sigma: zero false alarms in the calm days, 3 days late. "
          "After an alarm is handled, reset S, otherwise it alarms every single day after a real step."),

        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">The battery that's ageing faster</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">🔋 The satellite's inverter battery: it carries us through every eclipse.</p>""",
          "Section break. Remind them: eclipse = NEPA taking light for the satellite, the battery is the inverter.", cls="center"),

        S(f"""
<div class="kicker anim">battery_health_daily.csv · week-04 version</div>
<h2 class="anim" style="--d:.1s;font-size:52px">Three years of usable capacity</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{cap_svg}</div>
<div class="row anim" style="--d:2.8s;margin-top:18px;gap:14px">
  <span class="pill">{f['cap_start']:.1f} → {f['cap_end']:.1f} Ah</span>
  <span class="pill bad">95 Ah alarm: {f['below95']} days below</span>
  <span class="pill gold">⚠️ week-03 twin file: no speed-up</span>
</div>""",
          f"Capacity falls from {f['cap_start']:.1f} to {f['cap_end']:.1f} Ah, lowest {f['cap_min']:.2f}, so a 95 Ah threshold fires {f['below95']} times. "
          "Remind them to use the week-04 file. The week-03 twin is the clean version without the speed-up."),

        S(f"""
<div class="kicker anim">The anomaly is in the slope</div>
<h2 class="anim" style="--d:.1s">Not lower. Faster. 🏃🏾</h2>
<div class="row" style="gap:40px;align-items:center">
  <div class="anim" style="--d:.2s">{rate_svg}</div>
  <div class="col" style="flex:1;gap:20px">
    <div class="card anim a-right" style="--d:.6s"><h3>Ah lost per year</h3><p class="muted">a straight line through each period, × 365 days</p></div>
    <div class="card anim a-right glow" style="--d:.9s"><h3 class="hl">{f['rate_after'] / f['rate_before']:.1f}× faster after April 2025</h3><p>No single day is unusual. The <b>speed</b> changed.</p></div>
  </div>
</div>""",
          f"Fade rate {f['rate_before']:.2f} Ah per year before April 2025 and {f['rate_after']:.2f} after. "
          "The original code book quotes -2.4 and -4.0; the data says -2.24 and -3.68. Quiz question: monitor the rolling slope, not the level."),

        S(f"""
<div class="kicker anim">Watch the speedometer, not the fuel gauge</div>
<h2 class="anim" style="--d:.1s;font-size:52px">90-day rolling slope (trailing)</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{sl_svg}</div>
<div class="row anim" style="--d:2.8s;margin-top:18px;gap:14px">
  <span class="pill bad">red line: −3.0 Ah/yr warning</span>
  <span class="pill teal">before Apr 2025: {f['slope_pre_lo']:.2f} to {f['slope_pre_hi']:.2f}</span>
  <span class="pill gold">crosses on {_d(f['first_warning'])} (+{f['warn_delay']} days)</span>
</div>""",
          f"A trailing 90-day window needs time to fill with the new behaviour, so it warns {f['warn_delay']} days after the true change on 1 April 2025. Same lesson as CUSUM: alarm date is not start date."),

        S("""
<div class="kicker anim">Your toolbox so far</div>
<h2 class="anim" style="--d:.1s">Right tool for each shape 🧰</h2>
<div class="grid3" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">⚡</div><h3>Spike</h3><p class="muted">point rule / control chart on the leftovers</p><p class="small" style="margin-top:10px">Days 1–2</p></div>
  <div class="card anim a-pop glow" style="--d:.6s"><div class="icon">🪜</div><h3>Level shift</h3><p class="muted">CUSUM on the leftovers</p><p class="small" style="margin-top:10px">today</p></div>
  <div class="card anim a-pop glow" style="--d:.9s"><div class="icon">🐌</div><h3>Drift / speed-up</h3><p class="muted">rolling slope vs a warning line</p><p class="small" style="margin-top:10px">today</p></div>
</div>
<p class="anim" style="--d:1.3s;margin-top:36px;text-align:center">Always first: <b class="hl">take away what you already know</b> (season, drive level, eclipse).</p>""",
          "Summary of Week 3. Next week Day 1 we score all these detectors properly with the answer key."),

        S("""
<div class="kicker anim">🏁 Final project · Checkpoint 2</div>
<h2 class="anim" style="--d:.1s">📥 Data in hand</h2>
<div class="grid2" style="margin-top:16px">
  <div class="card anim a-left" style="--d:.3s"><h3>Bring today</h3>
    <p class="muted">✅ your unit head's reply (the email)<br>✅ your data loaded with a DatetimeIndex + <span class="mono">.asfreq()</span><br>
    ✅ profiled: rows, range, gaps, duplicates<br>✅ one honest plot with the threshold drawn</p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#E5484D"><h3>Data rules</h3>
    <p class="muted">⛔ real NIGCOMSAT data stays on NIGCOMSAT systems (training server / work laptop), <b>not Colab</b><br>
    ⛔ no raw data on GitHub<br>⛔ describe the shape to AI tools, don't paste it</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:28px;text-align:center">Next checkpoint: <b class="hl">Week 4 · Day 3: method drafted</b> 🛠️</p>""",
          "15 minutes, one by one. No reply from the unit head yet? Agree a follow-up today. Anyone still on synthetic data needs written agreement from their unit head."),

        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Open the exercise notebook 🧑🏾‍💻</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">A</span><p>CUSUM by hand: write the one line</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">B</span><p>Catch the amplifier's step + a secret fault</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">C</span><p>Find when the battery started ageing faster</p></div>
   <div class="row anim" style="--d:.9s;gap:18px;align-items:center"><span class="num">🌶️</span><p>Bonus: how noisy is a jumpy h?</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:1.1s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">🧾</div>
  <h3 style="margin-top:16px">14 checks to pass</h3>
  <p class="muted">File → Save a copy in Drive first<br>Run STEP 0, then top to bottom</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""", "Walk the room. Most common slip: writing S + x - k without max(0, ...). Second: forgetting that k and h are multiples of sigma."),

        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🪜</span><p><b>A level shift</b> can be huge locally yet invisible to a whole-series 3σ rule.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🧾</span><p><b>CUSUM:</b> S = max(0, S + leftover − k). k = slack, h = evidence. Alarm date ≠ start date.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🐌</span><p><b>Drift:</b> watch the rolling <b class="hl">slope</b>, not the level.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:36px">Next time 👉 <b class="hl">Scoring a Detector + Quiz 2</b>: the answer key comes out. 🔑</p>""",
          "Recap. Ask: why did the 3-sigma rule miss the step? Why is the alarm date later than the start? Tease Week 4 Day 1: the answer key."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    f = facts()
    t = f["tw"]["twta_temp_c"]
    wk = t.resample("W-MON").mean()
    wk_labels = [d.strftime("%b %y") if d.day <= 7 and d.month in (1, 4, 7, 10) else "" for d in wk.index]
    cap = f["cap"].resample("W-MON").mean()
    cap_labels = [d.strftime("%b %y") if d.day <= 7 and d.month in (1, 7) else "" for d in cap.index]
    sl = f["slope90"]["2024-01-01":].resample("W-MON").last()
    sl_labels = [d.strftime("%b %y") if d.day <= 7 and d.month in (1, 4, 7, 10) else "" for d in sl.index]
    p = f["practice"]["2025-01-01":"2025-03-01"]
    Sp = f["Sp"]["2025-01-01":"2025-03-01"]
    p_labels = [d.strftime("%d %b") if d.day in (1, 10, 20) else "" for d in p.index]
    toy_rows = [[f"Day {i + 1}", f"{x:+.1f}", f"{v:.1f}" + ("  ← alarm" if i + 1 == f["toy_alarm_day"] else "")]
                for i, (x, v) in enumerate(zip(TOY_X, f["toy"]))]
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🧾", "kicker": "Week 3 · Day 3", "title": "The Slow Creep: Drift and CUSUM",
             "sub": "Some faults never shout. Build a detector that keeps the receipts",
             "notes": "Today: faults that creep. By the end everyone writes a CUSUM detector."},
            {"type": "flow", "title": "Today's mission: three moves", "steps": [
                ["🙈", "See what 3σ misses", "the amplifier's sneaky step"],
                ["🧾", "Build CUSUM", "add up small leftovers"],
                ["🔋", "Watch the slope", "a battery ageing faster"]],
             "footer": "10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up + project checkpoint",
             "notes": "Three moves."},
            {"type": "bar", "title": "The landlord's “small-small” increases add up",
             "labels": [f"Year {i + 1}" for i in range(6)], "values": [500, 525, 550, 580, 610, 650], "highlight": [5],
             "fmt": "0", "name": "rent (₦k)", "caption": "Illustration: ₦415k extra over 6 years. CUSUM keeps the receipts",
             "notes": "No single year shocks you. Adding up the extras does."},
            {"type": "cards", "title": "Three shapes of trouble", "cards": [
                ["⚡", "Spike", "one reading way off, then back"],
                ["🪜", "Level shift", "a step to a new level that holds"],
                ["🐌", "Drift", "a slow lean: the slope changes"]],
             "notes": "Days 1–2 caught spikes. Today: shifts and drifts."},
            {"type": "chart", "title": "Amplifier temperature: a 3σ rule fires 0 times",
             "labels": wk_labels, "values": [round(v, 2) for v in wk.values], "ymin": 58, "ymax": 70, "freq": 1, "name": "TWTA °C (weekly mean)",
             "caption": f"Daily 3σ ceiling {f['ceiling']:.1f} °C, hottest day {f['max']:.2f} °C: never crossed. The step from 12 May 2025 hides in the yearly swing",
             "notes": f"Global mean {f['mean']:.2f}, sd {f['sd']:.2f}."},
            {"type": "stats", "title": "Zoom in: 30 days before vs after 12 May 2025",
             "sub": "Against its neighbours it's a giant. Against the whole two years, a dwarf",
             "stats": [[f"{f['pre_mean']:.2f}", "°C average before"], [f"{f['post_mean']:.2f}", "°C average after"],
                       [f"{f['jump_sigma']:.1f}σ", f"jump vs local wobble ({f['pre_sd']:.2f})"], [f"{f['global_sigma_jump']:.1f}σ", "jump vs whole series"]],
             "notes": "Quiz: no single reading looks extreme against the whole series."},
            {"type": "flow", "title": "Step 1: take away what you already know", "steps": [
                ["🌡️", "Actual", "the reading"],
                ["➖", "Expected", "drive + sun angle + ageing, learned from 2024"],
                ["🧩", "Leftovers", f"σ = {f['sigma']:.2f} °C; after the step: +{f['after_mean']:.2f}"]],
             "notes": "Residual = actual minus expected."},
            {"type": "code", "title": "Step 2: the CUSUM line",
             "code": "def cusum(values, k):\n    S, out = 0, []\n    for x in values:\n        S = max(0, S + x - k)   # add leftover, minus slack, never below 0\n        out.append(S)\n    return out",
             "caption": "Alarm when S goes above h. k = 0.5σ (slack), h = 5σ (evidence)",
             "notes": "Quiz: CUSUM accumulates small deviations so a sustained change becomes a clear slope."},
            {"type": "table", "title": f"By hand: k = {TOY_K}, h = {TOY_H}", "header": ["Day", "Leftover", "S"], "rows": toy_rows,
             "colW": [3, 3, 6.13],
             "caption": f"Change began day {f['toy_onset_day']} (day after S was last 0). Alarm on day {f['toy_alarm_day']}. Alarm date ≠ start date",
             "notes": "Quiz: alarm date is not onset."},
            {"type": "compare", "title": "The two knobs, set from σ",
             "left": ["🤏", f"k = 0.5σ = {f['k']:.2f} °C", "Slack: ordinary noise does not pile up"],
             "right": ["🚨", f"h = 5σ = {f['h']:.2f} °C", "Decision limit: low = fast but noisy, high = calm but late"],
             "notes": "Both measured in sigma of the leftovers from 2024."},
            {"type": "stats", "title": "CUSUM on the real amplifier (watching from Jan 2025)",
             "sub": "With the yearly swing removed, this step is big, so CUSUM fires on day one",
             "stats": [[f"{f['S_eve']:.2f}", "S the day before"], [f"{f['S_day']:.2f}", "S on 12 May 2025"],
                       [f"{f['h']:.2f}", "h (5σ)"], [f"{(f['first_alarm'] - SHIFT).days} days", "delay"]],
             "notes": "CUSUM earns its keep on smaller faults: next slide."},
            {"type": "twochart", "title": f"Practice: a +{FAULT_SIZE} °C fault the point rule never sees",
             "left": {"label": f"Leftovers: {f['p_point_hits_30']} hits above 3σ in 30 days", "labels": p_labels, "values": [round(v, 3) for v in p.values],
                      "ymin": -0.9, "ymax": 1.2, "fmt": "0.0", "color": "0A5DB4", "good": True},
             "right": {"label": f"CUSUM: alarm {_d(f['p_alarm'])[:-5]}, start traced to {_d(f['p_onset'])[:-5]}", "labels": p_labels,
                       "values": [round(v, 3) for v in Sp.values], "ymin": 0, "ymax": round(float(Sp.max()) * 1.1, 1), "fmt": "0.0", "color": "C77700", "good": True},
             "notes": "The day after S was last zero is the start."},
            {"type": "table", "title": "Choosing h: fast and noisy, or calm and late?", "header": ["h", "False alarms", "Caught after"],
             "rows": [[f"{m}σ", str(fa), f"{dl} day{'s' if dl != 1 else ''}"] for m, fa, dl in f["tradeoff"]], "colW": [3, 4.5, 4.63],
             "caption": f"Same practice fault, {f['p_clean_days']} calm days. After an alarm is checked: reset S to 0",
             "notes": "Pick h on purpose and write it down."},
            {"type": "section", "kicker": "Part 2", "title": "The battery that's ageing faster", "sub": "The satellite's inverter for every eclipse",
             "notes": "Section break."},
            {"type": "chart", "title": "Battery capacity: a 95 Ah threshold fires 0 times",
             "labels": cap_labels, "values": [round(v, 2) for v in cap.values], "ymin": 94, "ymax": 104, "freq": 1, "name": "capacity Ah",
             "caption": f"{f['cap_start']:.1f} → {f['cap_end']:.1f} Ah, lowest {f['cap_min']:.2f}. Use the week-04 file: the week-03 twin has no speed-up",
             "notes": "Level never breaches."},
            {"type": "bar", "title": "Not lower. Faster", "labels": ["before April 2025", "after April 2025"],
             "values": [round(-f["rate_before"], 2), round(-f["rate_after"], 2)], "highlight": [1], "fmt": "0.00", "ymax": 4.6,
             "name": "Ah lost per year", "caption": f"{f['rate_after'] / f['rate_before']:.1f}× faster. No single day is unusual; the speed changed",
             "notes": "The original quotes -2.4 and -4.0; the data says -2.24 and -3.68."},
            {"type": "chart", "title": "Watch the speedometer: 90-day rolling slope",
             "labels": sl_labels, "values": [round(v, 3) for v in sl.values], "ymin": -4, "ymax": -1, "freq": 1, "name": "Ah per year", "fmt": "0.0",
             "caption": f"Crosses the −3.0 warning line on {_d(f['first_warning'])}: {f['warn_delay']} days after the speed-up began",
             "notes": "Trailing windows warn late."},
            {"type": "cards", "title": "Right tool for each shape", "cards": [
                ["⚡", "Spike", "point rule on the leftovers"],
                ["🪜", "Level shift", "CUSUM on the leftovers"],
                ["🐌", "Drift / speed-up", "rolling slope vs a warning line"]],
             "notes": "Always remove what you already know first."},
            {"type": "compare", "title": "Final project · Checkpoint 2: data in hand",
             "left": ["📥", "Bring today", "Unit head's reply; data loaded with .asfreq(); rows, range, gaps, duplicates; one honest plot"],
             "right": ["⛔", "Data rules", "Real NIGCOMSAT data stays on NIGCOMSAT systems (not Colab); no raw data on GitHub"],
             "notes": "Next checkpoint: Week 4 Day 3, method drafted."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🧑🏾‍💻", "steps": [
                "A: CUSUM by hand, write the one line", "B: catch the amplifier's step + a secret fault",
                "C: find when the battery started ageing faster", "Bonus: how noisy is a jumpy h?"],
             "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["🪜", "A level shift can be huge locally yet invisible to a whole-series 3σ rule"],
                ["🧾", "CUSUM: S = max(0, S + leftover − k). Alarm date ≠ start date"],
                ["🐌", "Drift: watch the rolling slope, not the level"]],
             "next": "Next: Scoring a Detector + Quiz 2",
             "notes": "Tease the answer key."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
def expected_temp(df):
    """'Normal' amplifier temperature for each day, learned from 2024 only:
    drive level + sun angle (a yearly wave) + slow ageing. Second pass ignores one-off spikes."""
    d = df.index.day_of_year.to_numpy()
    age = (df.index - pd.Timestamp("2024-01-01")).days.to_numpy()
    X = np.column_stack([np.ones(len(df)), df["rf_drive_pct"].to_numpy(),
                         np.sin(2 * np.pi * d / 365.25), np.cos(2 * np.pi * d / 365.25), age])
    y = df["twta_temp_c"].to_numpy()
    learn = df.index < "2025-01-01"
    coef, *_ = np.linalg.lstsq(X[learn], y[learn], rcond=None)
    r = y - X @ coef
    keep = learn & (np.abs(r) < 3 * r[learn].std())
    coef, *_ = np.linalg.lstsq(X[keep], y[keep], rcond=None)
    return pd.Series(X @ coef, index=df.index)

def fade_rate(s):
    """Slope of a straight line through the series, in units per YEAR."""
    x = np.arange(len(s))
    return np.polyfit(x, s.to_numpy(), 1)[0] * 365

def rolling_slope(s, window=90):
    """Trailing rolling slope (units per year): looks back only, never ahead."""
    x = np.arange(window)
    return s.rolling(window).apply(lambda w: np.polyfit(x, w, 1)[0] * 365, raw=True)

def _twta():
    return pd.read_csv(data_path("twta_thermal_daily"), parse_dates=["date"], index_col="date").asfreq("D")

def _resid_sigma():
    tw = _twta()
    r = tw["twta_temp_c"] - expected_temp(tw)
    r24 = r[:"2024-12-31"]
    return r, r24[r24.abs() < 3 * r24.std()].std()

def _cus(values, k):
    S, out = 0.0, []
    for x in values:
        S = max(0.0, S + x - k)
        out.append(S)
    return out

def practice_residuals():
    """The amplifier's calm leftovers (Jan 2024 to the day before the real step), with the known 2-day
    hot spike left out, plus a SMALL secret fault we add on purpose. Your job: find when it started."""
    r, s = _resid_sigma()
    p = r[:"2025-05-11"]
    p = p[~((p.index < "2025-01-01") & (p.abs() > 3 * s))].copy()
    p.loc["2025-02-10":] += 0.3
    return p

def _bat():
    return pd.read_csv(data_path("battery_health_daily"), parse_dates=["date"], index_col="date").asfreq("D")["est_capacity_ah"]

def _same_day(a, b):
    return pd.Timestamp(a).normalize() == pd.Timestamp(b).normalize()

def _c_a1(x):
    want = ("spike", "level shift", "drift")
    got = tuple(str(v).strip().lower().replace("-", " ").replace("_", " ") for v in x)
    wrong = [i + 1 for i, (g, w) in enumerate(zip(got, want)) if g != w]
    return not wrong, "Spike, level shift, drift: you can name all three shapes of trouble.", \
        f"Check statement(s) {wrong}. Choose from: spike, level shift, drift."

def _c_a2(x):
    want = _cus([0.3, -0.2, 0.4, 1.0, 1.2, 0.9, 1.1], 0.5)
    ok = len(x) == len(want) and all(v is not None for v in x) and np.allclose(x, want)
    return ok, "Your CUSUM works: [0, 0, 0, 0.5, 1.2, 1.6, 2.2]. Noise days stay at zero; the change piles up.", \
        "The line is S = max(0, S + x - k): add today's leftover, take away the slack, never go below zero."

def _c_a3(x):
    return tuple(int(v) for v in x) == (4, 7), \
        "Started day 4, alarm day 7. The alarm date is NOT the start date: CUSUM needs time to collect evidence.", \
        "Start = the day AFTER S was last zero. Alarm = the first day S is above h = 2."

def _c_a4(x):
    return str(x).strip().lower().strip("()") == "b", "Correct: k is slack, so ordinary noise doesn't pile up.", \
        "k is not the alarm line (that's h). Think: what stops small everyday wobble from adding up?"

def _c_b1(x):
    t = _twta()["twta_temp_c"]
    return int(x) == int((t > t.mean() + 3 * t.std()).sum()) == 0, \
        "Zero alarms in two years. The step hides inside the yearly swing: a whole-series 3σ rule is blind to it.", \
        "Count the days above the ceiling: (tw[\"twta_temp_c\"] > ceiling).sum()"

def _c_b2(x):
    t = _twta()["twta_temp_c"]
    pre, post = t["2025-04-12":"2025-05-11"], t["2025-05-12":"2025-06-10"]
    want = (post.mean() - pre.mean()) / pre.std()
    return abs(float(x) - want) < 0.05, f"{want:.1f}σ against its neighbours. A giant up close, a dwarf from far away. 🔭", \
        "(post.mean() - pre.mean()) / pre.std()"

def _c_b3(x):
    r, s = _resid_sigma()
    want = r["2025-05-12":].mean()
    return abs(float(x) - want) < 0.005, f"+{want:.2f} °C of leftovers after the step: almost exactly the +1.8 °C fault hidden in the file. 🎯", \
        "First expected = expected_temp(tw). Then resid[\"2025-05-12\":].mean()"

def _c_b4(x):
    r, s = _resid_sigma()
    return abs(float(x[0]) - 0.5 * s) < 1e-6 and abs(float(x[1]) - 5 * s) < 1e-6, \
        f"k = {0.5 * s:.3f} °C (slack) and h = {5 * s:.3f} °C (decision limit). Both measured in σ of the leftovers.", \
        "k = 0.5 * sigma and h = 5 * sigma"

def _c_b5(x):
    return _same_day(x, "2025-05-12"), "12 May 2025: the very first day of the step. Big steps get caught fast. 🚨", \
        "S[S > h].index.min() gives the first day S is above h."

def _c_b6(x):
    a, o = x
    return _same_day(a, "2025-02-13") and _same_day(o, "2025-02-10"), \
        "Alarm 13 Feb 2025, start traced back to 10 Feb 2025. Exactly where we hid it. Detective work! 🕵🏾", \
        "Alarm: Sp[Sp > h].index.min(). Start: the day after the last day S was 0 before the alarm."

def _c_c1(x):
    return int(x) == int((_bat() < 95).sum()) == 0, \
        "Zero days below 95 Ah. A threshold detector would sleep through the whole problem. 😴", \
        "(cap < 95).sum()"

def _c_c2(x):
    cap = _bat()
    b, a = fade_rate(cap[:"2025-03-31"]), fade_rate(cap["2025-04-01":])
    ok = abs(float(x[0]) - b) < 0.01 and abs(float(x[1]) - a) < 0.01
    return ok, f"{b:.2f} → {a:.2f} Ah per year: {a / b:.1f}× faster. No day is unusual; the SPEED changed.", \
        "fade_rate(cap[:\"2025-03-31\"]) and fade_rate(cap[\"2025-04-01\":])"

def _c_c3(x):
    s = rolling_slope(_bat(), 90)
    want = s[s < -3.0].index.min()
    return _same_day(x, want), f"{want.date()}: {(want - pd.Timestamp('2025-04-01')).days} days after the speed-up began. Trailing windows warn late, so plan for it.", \
        "WARNING_LINE should be -3.0 (minus three, in Ah per year)."

def _c_bonus(x):
    p = practice_residuals()
    r, s = _resid_sigma()
    S_, n = 0.0, 0
    for day, v in p.items():
        S_ = max(0.0, S_ + v - 0.5 * s)
        if S_ > 2 * s:
            n += day < pd.Timestamp("2025-02-10")
            S_ = 0.0
    return int(x) == n, f"{n} false alarms with h = 2σ (h = 5σ gave none). Fast, yes. But the duty engineer will stop picking up the phone. 📵", \
        "Count the alarm days that come BEFORE the start you found in B6."

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4,
          "B5": _c_b5, "B6": _c_b6, "C1": _c_c1, "C2": _c_c2, "C3": _c_c3, "BONUS": _c_bonus}
HINTS = {"A2": "Inside the loop: S = max(0, S + x - k)", "B6": "Give two dates: (practice_alarm, start)",
         "C2": "Give two numbers: (rate_before, rate_after)"}
'''


def notebook_cells(setup_code):
    return [
        ("md", """# 🧾 Week 3 · Day 3: The Slow Creep: Drift and CUSUM

**Today:** some faults never shout. You'll build **CUSUM**, a detector that adds up small leftovers, catch an amplifier step that a 3σ rule can't see, and find when a battery started ageing faster.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (**Shift + Enter**) |
| ✍️ | Your turn: replace every `___` |
| ✅ / ❌ | The check tells you if you got it right |
| 🌶️ | Bonus for fast finishers |

> ## ⚠️ First: **File → Save a copy in Drive**
> Then run STEP 0. Keep `W3D3-rulebook.pdf` open next to you."""),
        ("md", "## ▶️ STEP 0: Set up (run once, and again after any restart)\nYou should see `✅ Ready!`. This cell also brings in three helpers you'll use today: `expected_temp`, `fade_rate`, `rolling_slope`."),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: CUSUM by hand (15 min) 🧾

### A1 ✍️ Name the shape
Three faults, three shapes. Write `"spike"`, `"level shift"` or `"drift"` for each:

1. One reading jumps way up, and the next day everything is back to normal.
2. The temperature steps up by 2 °C one day **and stays there**.
3. The battery loses capacity a little **faster** every month."""),
        ("task", 's1 = ___\ns2 = ___\ns3 = ___\n\ncheck("A1", (s1, s2, s3))',
         's1 = "spike"\ns2 = "level shift"\ns3 = "drift"\n\ncheck("A1", (s1, s2, s3))'),
        ("md", """### A2 ✍️ Write the one line that makes CUSUM work
Every day: **add today's leftover, take away the slack `k`, and never go below zero.**
In Python: `max(0, S + x - k)`. Put it in the blank inside the loop."""),
        ("task", 'def cusum(values, k):\n    S = 0\n    out = []\n    for x in values:\n        S = ___          # ✍️ the CUSUM line\n        out.append(S)\n    return out\n\ntoy = [0.3, -0.2, 0.4, 1.0, 1.2, 0.9, 1.1]      # 7 days of leftovers\nprint(cusum(toy, k=0.5))\ncheck("A2", cusum(toy, k=0.5))',
         'def cusum(values, k):\n    S = 0\n    out = []\n    for x in values:\n        S = max(0, S + x - k)          # ✍️ the CUSUM line\n        out.append(S)\n    return out\n\ntoy = [0.3, -0.2, 0.4, 1.0, 1.2, 0.9, 1.1]      # 7 days of leftovers\nprint(cusum(toy, k=0.5))\ncheck("A2", cusum(toy, k=0.5))'),
        ("md", "### A3 ✍️ When did it start, and when did the alarm ring?\n▶️ Run the table first. Use **h = 2**. The change **started** the day *after* S was last zero. The **alarm** is the first day S is above h."),
        ("code", 'assert cusum([1.0], 0.0)[0] == 1.0, "✍️ Do A2 first: write the CUSUM line, then run this again."\n\nfor day, (x, s) in enumerate(zip(toy, cusum(toy, k=0.5)), start=1):\n    print(f"day {day}: leftover {x:+.1f}  ->  S = {s:.1f}" + ("   🚨 above h=2" if s > 2 else ""))'),
        ("task", 'start_day = ___\nalarm_day = ___\n\ncheck("A3", (start_day, alarm_day))', 'start_day = 4\nalarm_day = 7\n\ncheck("A3", (start_day, alarm_day))'),
        ("md", """### A4 ✍️ What is the slack `k` for?
- **a)** it is the alarm threshold
- **b)** it is slack, so ordinary everyday noise does not pile up
- **c)** it is the value S resets to after an alarm

Type the letter in quotes."""),
        ("task", 'k_is_for = ___\n\ncheck("A4", k_is_for)', 'k_is_for = "b"\n\ncheck("A4", k_is_for)'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: The amplifier's sneaky step (30 min) 🌡️

**The data:** `twta_thermal_daily` (the **week-04** version, which `data_path` gives you by default): two years of the TWTA amplifier's daily temperature and its RF drive level.

### B1 ✍️ Does a whole-series 3σ rule see anything?
▶️ The cell computes the ceiling (mean + 3σ of the whole series). Count the days **above** it."""),
        ("code", 'tw = pd.read_csv(data_path("twta_thermal_daily"), parse_dates=["date"], index_col="date").asfreq("D")\nceiling = tw["twta_temp_c"].mean() + 3 * tw["twta_temp_c"].std()\nprint(f"3σ ceiling: {ceiling:.2f} °C   hottest day: {tw[\'twta_temp_c\'].max():.2f} °C")\n\ntw["twta_temp_c"].plot(title="TWTA temperature, two years", lw=1)\nplt.axhline(ceiling, color="#E5484D", ls="--", label="3σ ceiling")\nplt.axvline(pd.Timestamp("2025-05-12"), color="#C77700", ls=":", label="12 May 2025")\nplt.legend(); plt.ylabel("°C"); plt.show()'),
        ("task", 'n_point_alarms = ___          # how many days are above the ceiling?\n\ncheck("B1", n_point_alarms)', 'n_point_alarms = (tw["twta_temp_c"] > ceiling).sum()          # how many days are above the ceiling?\n\ncheck("B1", n_point_alarms)'),
        ("md", "### B2 ✍️ Zoom in: how big is the step against its neighbours?\nCompare the 30 days after 12 May 2025 with the 30 days before, in units of the **local** wobble: `(post.mean() - pre.mean()) / pre.std()`."),
        ("task", 't = tw["twta_temp_c"]\npre = t["2025-04-12":"2025-05-11"]\npost = t["2025-05-12":"2025-06-10"]\n\njump_in_sigma = ___\nprint(f"before {pre.mean():.2f} °C  after {post.mean():.2f} °C")\ncheck("B2", jump_in_sigma)',
         't = tw["twta_temp_c"]\npre = t["2025-04-12":"2025-05-11"]\npost = t["2025-05-12":"2025-06-10"]\n\njump_in_sigma = (post.mean() - pre.mean()) / pre.std()\nprint(f"before {pre.mean():.2f} °C  after {post.mean():.2f} °C")\ncheck("B2", jump_in_sigma)'),
        ("md", """### B3 ✍️ Take away what you already know
`expected_temp(tw)` (from STEP 0) gives the **normal** temperature for every day, learned from 2024: drive level + sun angle + slow ageing.
The **leftovers** (residuals) = actual − expected. Fill in `expected`, then the average leftover from 12 May 2025 onward."""),
        ("task", 'expected = ___\nassert expected is not None, "✍️ Fill in expected first: expected_temp(tw)"\nresid = tw["twta_temp_c"] - expected\n\nr24 = resid[:"2024-12-31"]\nsigma = r24[r24.abs() < 3 * r24.std()].std()      # the normal wobble of the leftovers (2024, spikes ignored)\nprint(f"sigma of leftovers: {sigma:.3f} °C")\n\nafter_mean = ___\ncheck("B3", after_mean)',
         'expected = expected_temp(tw)\nassert expected is not None, "✍️ Fill in expected first: expected_temp(tw)"\nresid = tw["twta_temp_c"] - expected\n\nr24 = resid[:"2024-12-31"]\nsigma = r24[r24.abs() < 3 * r24.std()].std()      # the normal wobble of the leftovers (2024, spikes ignored)\nprint(f"sigma of leftovers: {sigma:.3f} °C")\n\nafter_mean = resid["2025-05-12":].mean()\ncheck("B3", after_mean)'),
        ("md", "### B4 ✍️ Set the two knobs from σ\nSlack **k = 0.5 × σ**. Decision limit **h = 5 × σ**."),
        ("task", 'k = ___\nh = ___\n\ncheck("B4", (k, h))', 'k = 0.5 * sigma\nh = 5 * sigma\n\ncheck("B4", (k, h))'),
        ("md", "### B5 ✍️ Run CUSUM on 2025 and find the first alarm\nWe start watching on 1 Jan 2025 (the model learned from 2024). `S[S > h].index.min()` gives the first day S is above h."),
        ("task", 'assert k is not None and h is not None, "✍️ Do B4 first."\nr25 = resid["2025-01-01":]\nS = pd.Series(cusum(r25.to_numpy(), k), index=r25.index)\n\nS["2025-04-15":"2025-05-20"].plot(title="CUSUM around the step", lw=2)\nplt.axhline(h, color="#E5484D", ls="--", label="h"); plt.legend(); plt.show()\n\nfirst_alarm = ___\ncheck("B5", first_alarm)',
         'assert k is not None and h is not None, "✍️ Do B4 first."\nr25 = resid["2025-01-01":]\nS = pd.Series(cusum(r25.to_numpy(), k), index=r25.index)\n\nS["2025-04-15":"2025-05-20"].plot(title="CUSUM around the step", lw=2)\nplt.axhline(h, color="#E5484D", ls="--", label="h"); plt.legend(); plt.show()\n\nfirst_alarm = S[S > h].index.min()\ncheck("B5", first_alarm)'),
        ("md", """### B6 ✍️ The secret fault 🕵🏾
`practice_residuals()` gives you the calm leftovers **before** the real step, with a **small** fault (about 1.5σ) hidden somewhere. ▶️ The first lines show the point rule seeing almost nothing.
Find (1) the **alarm date** and (2) the **start date** = the day after S was last zero before the alarm."""),
        ("task", 'p = practice_residuals()\nprint("days above the 3σ point-rule line:", int((p > 3 * sigma).sum()))\nSp = pd.Series(cusum(p.to_numpy(), k), index=p.index)\n\npractice_alarm = ___\nbefore = Sp[:practice_alarm]\nlast_zero = before[before == 0].index.max()\nstart = ___                 # the day AFTER last_zero  (hint: last_zero + pd.Timedelta(days=1))\n\nprint("alarm:", practice_alarm, "  start:", start)\ncheck("B6", (practice_alarm, start))',
         'p = practice_residuals()\nprint("days above the 3σ point-rule line:", int((p > 3 * sigma).sum()))\nSp = pd.Series(cusum(p.to_numpy(), k), index=p.index)\n\npractice_alarm = Sp[Sp > h].index.min()\nbefore = Sp[:practice_alarm]\nlast_zero = before[before == 0].index.max()\nstart = last_zero + pd.Timedelta(days=1)                 # the day AFTER last_zero  (hint: last_zero + pd.Timedelta(days=1))\n\nprint("alarm:", practice_alarm, "  start:", start)\ncheck("B6", (practice_alarm, start))'),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: The battery that's ageing faster (15 min) 🔋

**The data:** `battery_health_daily`, the **week-04** version (the default). ⚠️ The week-03 file with the same name is a clean twin **without** today's problem.

### C1 ✍️ Does a 95 Ah threshold ever fire?"""),
        ("code", 'cap = pd.read_csv(data_path("battery_health_daily"), parse_dates=["date"], index_col="date").asfreq("D")["est_capacity_ah"]\ncap.plot(title="Battery usable capacity", lw=1.5)\nplt.axhline(95, color="#E5484D", ls="--", label="95 Ah alarm line")\nplt.legend(); plt.ylabel("Ah"); plt.show()'),
        ("task", 'days_below_95 = ___\n\ncheck("C1", days_below_95)', 'days_below_95 = (cap < 95).sum()\n\ncheck("C1", days_below_95)'),
        ("md", "### C2 ✍️ Measure the speed: before vs after April 2025\n`fade_rate(series)` fits a straight line and returns the change **per year**. Use `cap[:\"2025-03-31\"]` and `cap[\"2025-04-01\":]`."),
        ("task", 'rate_before = ___\nrate_after = ___\n\nprint(f"{rate_before:.2f} Ah/yr  ->  {rate_after:.2f} Ah/yr" if rate_after is not None else "")\ncheck("C2", (rate_before, rate_after))',
         'rate_before = fade_rate(cap[:"2025-03-31"])\nrate_after = fade_rate(cap["2025-04-01":])\n\nprint(f"{rate_before:.2f} Ah/yr  ->  {rate_after:.2f} Ah/yr" if rate_after is not None else "")\ncheck("C2", (rate_before, rate_after))'),
        ("md", "### C3 ✍️ Watch the speedometer, not the fuel gauge\nA **90-day trailing rolling slope** shows the speed every day. Set a warning line at **−3.0 Ah per year** and find the first day the slope drops below it."),
        ("task", 'slope90 = rolling_slope(cap, 90)\n\nWARNING_LINE = ___\nassert WARNING_LINE is not None, "✍️ Fill in WARNING_LINE first."\nslope90["2024-01-01":].plot(title="90-day rolling slope of capacity (Ah per year)", lw=2)\nplt.axhline(WARNING_LINE, color="#E5484D", ls="--"); plt.show()\n\nfirst_warning = slope90[slope90 < WARNING_LINE].index.min()\nprint("first warning:", first_warning, "  days after 1 Apr 2025:", (first_warning - pd.Timestamp("2025-04-01")).days)\ncheck("C3", first_warning)',
         'slope90 = rolling_slope(cap, 90)\n\nWARNING_LINE = -3.0\nassert WARNING_LINE is not None, "✍️ Fill in WARNING_LINE first."\nslope90["2024-01-01":].plot(title="90-day rolling slope of capacity (Ah per year)", lw=2)\nplt.axhline(WARNING_LINE, color="#E5484D", ls="--"); plt.show()\n\nfirst_warning = slope90[slope90 < WARNING_LINE].index.min()\nprint("first warning:", first_warning, "  days after 1 Apr 2025:", (first_warning - pd.Timestamp("2025-04-01")).days)\ncheck("C3", first_warning)'),

        # ---------------- BONUS ----------------
        ("md", """---
## 🌶️ Pepper task: how noisy is a jumpy h?
`alarm_days` below runs CUSUM **with a reset** after every alarm (what you do once someone has checked it).
Run it on the practice leftovers with **h = 2σ** instead of 5σ, and count the alarms that come **before** the start you found in B6. Those are false alarms."""),
        ("task", 'def alarm_days(x, k, h):\n    S, out = 0.0, []\n    for day, v in x.items():\n        S = max(0.0, S + v - k)\n        if S > h:\n            out.append(day)\n            S = 0.0          # reset after each alarm\n    return out\n\njumpy = alarm_days(p, k, 2 * sigma)\nfalse_alarms = ___          # how many of the jumpy alarms come before `start`?\ncheck("BONUS", false_alarms)',
         'def alarm_days(x, k, h):\n    S, out = 0.0, []\n    for day, v in x.items():\n        S = max(0.0, S + v - k)\n        if S > h:\n            out.append(day)\n            S = 0.0          # reset after each alarm\n    return out\n\njumpy = alarm_days(p, k, 2 * sigma)\nfalse_alarms = sum(day < start for day in jumpy)          # how many of the jumpy alarms come before `start`?\ncheck("BONUS", false_alarms)'),

        ("md", """---
## 🏁 Final project · Checkpoint 2: 📥 Data in hand
Tick these off with your trainer today (on **your** data, on NIGCOMSAT systems, not in Colab):

- [ ] Your unit head's **email reply** agreeing the process, the data and who it's for
- [ ] Data loaded with a `DatetimeIndex`, one time zone, and `.asfreq()`
- [ ] Profiled: **rows, date range, gaps, duplicated timestamps**
- [ ] One honest plot with your **operational threshold** drawn on it
- [ ] Raw data **not** on GitHub; nothing restricted pasted into an AI tool

Next checkpoint: **Week 4 · Day 3: method drafted** 🛠️

## Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- **Three shapes:** spike (point rule), **level shift** (CUSUM), **drift** (rolling slope).
- A shift can be **6.9σ** against its neighbours yet invisible to a whole-series 3σ rule.
- **Take away what you already know first** (drive, sun angle, ageing), then watch the leftovers.
- **CUSUM:** `S = max(0, S + leftover − k)`, k = 0.5σ slack, h = 5σ evidence. Reset after an alarm is handled.
- **Alarm date ≠ start date.** Trace the start back to the day after S was last zero.
- Low h = fast but noisy; high h = calm but late. Choose on purpose.

**Next time:** *Scoring a Detector + Quiz 2*. The answer key comes out. 🔑

<sub>Data: synthetic teaching datasets from the original Week 4 code book (`Time-series/week-04`). Safe to use in AI assistants. Real NIGCOMSAT data is not.</sub>"""),
    ]
