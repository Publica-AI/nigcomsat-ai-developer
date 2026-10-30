"""Week 3 · Day 2: Control Charts and Residuals."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import BRAND as B, ORIGINALS
from svgcharts import AXIS_TXT, GRID, _scale, bars_svg, line_svg
from webdeck import logos_title_block

CODE = "W3D2"
TITLE = "Control Charts and Residuals"

D4 = ORIGINALS / "week-04" / "data"
WIN = 168                     # trailing window for rolling limits: 7 days of hours
SPIKE_DAYS = ("2024-09-03", "2024-09-04")
SHIFT_START = "2025-05-12"


# =============================================================================
# DATA + FACTS (every number on a slide comes from here)
# =============================================================================
def _bus():
    b = pd.read_csv(D4 / "bus_power_telemetry_hourly.csv", parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    e = b["eclipse_flag"]
    after = (e.shift(1, fill_value=0) + e.shift(2, fill_value=0) + e.shift(3, fill_value=0)) > 0
    b["state"] = np.where(e == 1, "eclipse", np.where(after, "recharge", "sunlit"))
    return b


def _robust(x, w):
    """Trailing rolling median and robust spread (median absolute residual × 1.4826). Never sees the current reading."""
    med = x.rolling(w, min_periods=min(48, w)).median().shift(1)
    rsd = (x - med).abs().rolling(w, min_periods=min(48, w)).median().shift(1) * 1.4826
    return (x - med) / rsd, med, rsd


def _twta():
    return pd.read_csv(D4 / "twta_thermal_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")


def _expected(tw, skip=()):
    doy = tw.index.dayofyear
    X = np.column_stack([np.ones(len(tw)), tw["rf_drive_pct"], np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)])
    train = (tw.index <= pd.Timestamp("2024-12-31")) & ~tw.index.isin(pd.to_datetime(list(skip)))
    coef, *_ = np.linalg.lstsq(X[train], tw["twta_temp_c"].values[train], rcond=None)
    return pd.Series(X @ coef, index=tw.index), train, coef


def _health(res, train):
    r = pd.Series(res[train])
    h1 = r.loc[:"2024-06-30"].std()
    h2 = r.loc["2024-07-01":"2024-12-31"].std()
    return dict(mean=float(r.mean()), lag1=float(r.autocorr(1)), h1=float(h1), h2=float(h2), sd=float(r.std()))


def _tamper(seed=42, n=2000):
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, n)
    adjust, tampered = 0.0, []
    for x in noise:
        reading = adjust + x
        tampered.append(reading)
        adjust -= reading                 # "correct" every wobble
    return noise, np.array(tampered)


def facts():
    bus = _bus()
    cur = bus["solar_array_current_a"]
    states = bus.groupby("state")["solar_array_current_a"].agg(["count", "mean", "std"])
    ref = cur.loc["2025-08-01":"2025-08-15"]
    centre, sigma = float(ref.mean()), float(ref.std())
    lcl, ucl = centre - 3 * sigma, centre + 3 * sigma
    sunlit = cur[bus["state"] == "sunlit"]
    outside = (sunlit < lcl) | (sunlit > ucl)
    x = cur.where(bus["state"] == "sunlit")
    z, med, rsd = _robust(x, WIN)
    flags = z.abs() > 3
    flag_times = list(z[flags].index)
    mu = x.rolling(WIN, min_periods=48).mean().shift(1)
    sd = x.rolling(WIN, min_periods=48).std().shift(1)
    zz = (x - mu) / sd
    big_drop = [t for t in flag_times if cur.loc[t] < 20]
    false_alarms = [t for t in flag_times if cur.loc[t] >= 20]
    calm, tampered = _tamper()

    tw = _twta()
    temp = tw["twta_temp_c"]
    exp1, train1, coef1 = _expected(tw)
    res1 = temp - exp1
    h1 = _health(res1, train1)
    worst = res1[train1].abs().idxmax()
    exp2, train2, coef2 = _expected(tw, SPIKE_DAYS)
    res2 = temp - exp2
    h2 = _health(res2, train2)
    sd2 = h2["sd"]
    z2 = res2 / sd2
    post = z2.loc[SHIFT_START:]
    rz, rmed, rrsd = _robust(temp, 30)
    cm7 = temp.rolling(7, center=True).mean()
    tm7 = temp.rolling(7).median().shift(1)
    return dict(
        bus=bus, cur=cur, states=states, ref=ref, centre=centre, sigma=sigma, lcl=lcl, ucl=ucl,
        n_sunlit=int(len(sunlit)), n_outside=int(outside.sum()), n_recharge=int((bus["state"] == "recharge").sum()),
        n_eclipse=int((bus["state"] == "eclipse").sum()),
        sd_all_sunlit=float(cur[bus["eclipse_flag"] == 0].std()), sd_sunlit=float(sunlit.std()),
        daily_sunlit=sunlit.resample("D").mean(), daily_min=sunlit.resample("D").min(),
        z=z, med=med, rsd=rsd, flags=int(flags.sum()), flag_times=flag_times, big_drop=big_drop, false_alarms=false_alarms,
        drop_min=float(cur.loc[big_drop].min()),
        mean2=int((zz.abs() > 2).sum()), mean3=int((zz.abs() > 3).sum()),
        sd_jump=float(sd.loc["2025-09-28 15:00"]), rsd_jump=float(rsd.loc["2025-09-28 15:00"]),
        rsd_typical=float(rsd.median()),
        f3=2880 * 0.0027, f2=2880 * 0.0455, tamper_ratio=float(tampered.std() / calm.std()),
        tw=tw, temp=temp, raw_mean=float(temp.mean()), raw_sd=float(temp.std()),
        raw_ceiling=float(temp.mean() + 3 * temp.std()), spike_max=float(temp.loc[SPIKE_DAYS[0]]),
        exp1=exp1, res1=res1, h1=h1, worst=worst, coef2=coef2, exp2=exp2, res2=res2, h2=h2, sd2=sd2, z2=z2,
        spike_sig=float(z2.loc[SPIKE_DAYS[0]]), spike_sig2=float(z2.loc[SPIKE_DAYS[1]]),
        spike_exp=float(exp2.loc[SPIKE_DAYS[0]]), spike_res=float(res2.loc[SPIKE_DAYS[0]]),
        n_post=int(len(post)), n_post_flag=int((post.abs() > 3).sum()), post_mean=float(res2.loc[SHIFT_START:].mean()),
        rz=rz, rz_spike=float(rz.loc[SPIKE_DAYS[0]]), roll_post_flags=int((rz.loc[SHIFT_START:].abs() > 3).sum()),
        roll_res=temp - rmed,
        cm7_res=float((temp - cm7).loc[SPIKE_DAYS[0]]), tm7_res=float((temp - tm7).loc[SPIKE_DAYS[0]]),
    )


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


# =============================================================================
# LOCAL SVG HELPER: a control chart (band + centre line + series + flags)
# =============================================================================
def band_svg(values, *, w=1380, h=430, ymin, ymax, lcl=None, ucl=None, centre=None, lo_arr=None, hi_arr=None,
             color=B["blue_d"], xlabels=(), yticks=(), flags=(), offchart=(), dur="2.6s", band_labels=True, step=1):
    v = np.asarray(values, dtype=float)
    n = len(v)
    L, R, T, Bm = 90, w - (150 if band_labels else 30), 24, h - 56

    def X(i):
        return _scale(i, 0, n - 1, L, R)

    def Y(y):
        return _scale(min(max(y, ymin), ymax), ymin, ymax, Bm, T)

    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    for (yv, lab) in yticks:
        out.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{L - 14}" y="{Y(yv) + 7:.1f}" fill="{AXIS_TXT}" font-size="20" text-anchor="end">{lab}</text>')
    tl = B["teal_d"]
    if lcl is not None:
        out.append(f'<rect class="anim a-fade" style="--d:.2s" x="{L}" y="{Y(ucl):.1f}" width="{R - L}" height="{Y(lcl) - Y(ucl):.1f}" fill="{tl}" fill-opacity=".16"/>')
        for yv, lab in ((ucl, "UCL"), (lcl, "LCL")):
            out.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{tl}" stroke-width="2.5" stroke-dasharray="10 7"/>')
            if band_labels:
                out.append(f'<text x="{R + 12}" y="{Y(yv) + 8:.1f}" fill="{tl}" font-size="21" font-weight="800">{lab} {yv:.2f}</text>')
    if lo_arr is not None:
        lo, hi = np.asarray(lo_arr, float), np.asarray(hi_arr, float)
        idx = [i for i in range(0, n, step) if not (np.isnan(lo[i]) or np.isnan(hi[i]))]
        top = " L".join(f"{X(i):.1f},{Y(hi[i]):.1f}" for i in idx)
        bot = " L".join(f"{X(i):.1f},{Y(lo[i]):.1f}" for i in reversed(idx))
        out.append(f'<path class="anim a-fade" style="--d:.2s" d="M{top} L{bot} Z" fill="{tl}" fill-opacity=".22"/>')
    if centre is not None:
        out.append(f'<line x1="{L}" x2="{R}" y1="{Y(centre):.1f}" y2="{Y(centre):.1f}" stroke="#EAF2FB" stroke-width="1.5" stroke-dasharray="4 6" opacity=".6"/>')
        if band_labels:
            out.append(f'<text x="{R + 12}" y="{Y(centre) + 8:.1f}" fill="#C9D6E5" font-size="21">centre</text>')
    for (i, lab) in xlabels:
        anchor = "start" if i == 0 else ("end" if i >= n - 1 else "middle")
        out.append(f'<text x="{X(i):.1f}" y="{h - 18}" fill="{AXIS_TXT}" font-size="20" text-anchor="{anchor}">{lab}</text>')
    segs, cur = [], []
    for i in range(n):
        if np.isnan(v[i]):
            if cur:
                segs.append(cur)
            cur = []
        else:
            cur.append((X(i), Y(v[i])))
    if cur:
        segs.append(cur)
    for seg in segs:
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in seg)
        out.append(f'<path class="draw" style="--dur:{dur};--d:.4s" d="{d}" fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round"/>')
    for k, (i, lab, col) in enumerate(flags):
        x, y = X(i), Y(v[i])
        anchor, dx = ("end", -16) if x > (L + R) / 2 else ("start", 16)
        out.append(f'<g class="anim a-pop" style="--d:{2.8 + .2 * k:.2f}s;transform-origin:{x:.0f}px {y:.0f}px">'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{col}" stroke="{B["space"]}" stroke-width="3"/>'
                   + (f'<text x="{x + dx:.1f}" y="{y - 12:.1f}" fill="{col}" font-size="22" font-weight="800" text-anchor="{anchor}">{lab}</text>' if lab else "")
                   + '</g>')
    for k, (i, lab) in enumerate(offchart):
        x = X(i)
        anchor, dx = ("end", -14) if x > (L + R) / 2 else ("start", 14)
        out.append(f'<g class="anim a-pop" style="--d:{2.9 + .2 * k:.2f}s;transform-origin:{x:.0f}px {Bm:.0f}px">'
                   f'<path d="M{x:.1f},{Bm - 46:.1f} L{x:.1f},{Bm - 6:.1f} M{x - 9:.1f},{Bm - 18:.1f} L{x:.1f},{Bm - 4:.1f} L{x + 9:.1f},{Bm - 18:.1f}" '
                   f'stroke="{B["bad"]}" stroke-width="4" fill="none" stroke-linecap="round"/>'
                   f'<text x="{x + dx:.1f}" y="{Bm - 26:.1f}" fill="{B["bad"]}" font-size="22" font-weight="800" text-anchor="{anchor}">{lab}</text></g>')
    out.append("</svg>")
    return "".join(out)


def _xl_hours(idx, labels=("2025-08-01", "2025-09-01", "2025-10-01", "2025-11-01")):
    out = []
    for d in labels:
        t = pd.Timestamp(d)
        if idx[0] <= t <= idx[-1]:
            out.append((int(idx.get_loc(t)), t.strftime("%-d %b")))
    return out


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    f = facts()
    bus, cur = f["bus"], f["cur"]
    st = f["states"]

    # Mama Put (illustration): a fortnight of tomato prices
    rng = np.random.default_rng(3)
    prices = 100 + rng.normal(0, 3, 14)
    prices[10] = 128
    mp_c, mp_s = float(np.mean(np.delete(prices, 10))), float(np.std(np.delete(prices, 10), ddof=1))
    mama = band_svg(prices, w=700, h=330, ymin=85, ymax=132, lcl=mp_c - 3 * mp_s, ucl=mp_c + 3 * mp_s, centre=mp_c,
                    band_labels=False, flags=[(10, "“Ehn?!”", B["bad"])], dur="1.6s",
                    xlabels=[(0, "day 1"), (13, "day 14")])

    # August with fixed limits
    aug = cur.loc["2025-08-01":"2025-08-31"]
    aug_drop = int(aug.index.get_loc(pd.Timestamp("2025-08-18 09:00")))
    aug_chart = band_svg(aug.values, ymin=27.4, ymax=28.5, lcl=f["lcl"], ucl=f["ucl"], centre=f["centre"],
                         yticks=[(27.5, "27.5 A"), (28.0, "28.0 A"), (28.5, "28.5 A")],
                         xlabels=[(0, "1 Aug"), (int(aug.index.get_loc(pd.Timestamp("2025-08-16"))), "16 Aug"), (len(aug) - 1, "31 Aug")],
                         offchart=[(aug_drop, f"{aug.loc['2025-08-18 09:00']:.1f} A: way below!")])

    # stale fixed limits: daily mean of sunlit hours
    dm = f["daily_sunlit"]
    stale = band_svg(dm.values, ymin=27.4, ymax=28.5, lcl=f["lcl"], ucl=f["ucl"], centre=f["centre"],
                     yticks=[(27.5, "27.5 A"), (28.0, "28.0 A"), (28.5, "28.5 A")],
                     xlabels=[(0, "1 Aug"), (31, "1 Sep"), (61, "1 Oct"), (92, "1 Nov"), (len(dm) - 1, "28 Nov")])

    # rolling robust limits on sunlit hours
    x = cur.where(bus["state"] == "sunlit")
    lo = f["med"] - 3 * f["rsd"]
    hi = f["med"] + 3 * f["rsd"]
    fl = [(int(cur.index.get_loc(t)), "false alarm", B["gold"]) for t in f["false_alarms"]]
    drop_days = sorted({t.normalize(): t for t in f["big_drop"]}.values())
    roll_chart = band_svg(x.values, ymin=27.4, ymax=29.9, lo_arr=lo.values, hi_arr=hi.values, band_labels=False,
                          yticks=[(27.5, "27.5"), (28.5, "28.5"), (29.5, "29.5 A")], xlabels=_xl_hours(cur.index),
                          flags=fl, step=3, dur="3s",
                          offchart=[(int(cur.index.get_loc(t)), "") for t in drop_days])

    # TWTA raw vs residual
    temp = f["temp"]
    tw_x = [(0, "Jan 2024"), (int(temp.index.get_loc(pd.Timestamp("2025-01-01"))), "Jan 2025"), (len(temp) - 1, "Dec 2025")]
    i_spike = int(temp.index.get_loc(pd.Timestamp(SPIKE_DAYS[0])))
    i_shift = int(temp.index.get_loc(pd.Timestamp(SHIFT_START)))
    raw_chart = band_svg(temp.values, w=1380, h=380, ymin=58.5, ymax=70.5, lcl=f["raw_mean"] - 3 * f["raw_sd"],
                         ucl=f["raw_ceiling"], centre=f["raw_mean"], yticks=[(60, "60 °C"), (65, "65 °C"), (70, "70 °C")],
                         xlabels=tw_x, flags=[(i_spike, f"spike {f['spike_max']:.1f} °C: still inside", B["gold"])])
    sd2 = f["sd2"]
    res_chart = band_svg(f["res2"].values, w=1380, h=380, ymin=-1.5, ymax=5.6, lcl=-3 * sd2, ucl=3 * sd2, centre=0,
                         yticks=[(0, "0"), (2.5, "+2.5"), (5, "+5 °C")], xlabels=tw_x,
                         flags=[(i_spike, f"{f['spike_sig']:.0f}σ!", B["bad"])])
    roll_tw = band_svg(f["roll_res"].values, w=1380, h=330, ymin=-1.5, ymax=5.6,
                       centre=0, band_labels=False,
                       yticks=[(0, "0"), (2.5, "+2.5"), (5, "+5 °C")], xlabels=tw_x,
                       flags=[(i_spike, "spike: caught", B["good"]), (i_shift + 6, "shift: fades in ~3 weeks", B["gold"])])

    sb = bars_svg(["eclipse", "sunlit", "recharge"],
                  [st.loc["eclipse", "mean"], st.loc["sunlit", "mean"], st.loc["recharge", "mean"]],
                  w=760, h=380, ymax=33, highlight=(0, 2), fmt="{:.1f} A")
    fa = bars_svg(["±2σ", "±3σ"], [f["f2"], f["f3"]], w=560, h=360, ymax=150, highlight=(0,), hcolor=B["bad"],
                  color=B["teal_d"], fmt="{:.0f}")

    s = [
        # 1 title
        S(f"""
<div style="max-width:1000px;margin-top:40px">
  <div class="kicker anim">Week 3 · Day 2</div>
  <h1 class="anim" style="--d:.2s">Control Charts<br><span class="hl">and Residuals</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Know what “normal” looks like. Then anything outside it<br>jumps out at you, like a wrong price at the market. 🍅</p>
  <div class="anim" style="--d:.8s;margin-top:44px;display:flex">{logos_title_block()}</div>
</div>
<div class="anim a-pop floaty" style="--d:.6s;position:absolute;right:120px;top:200px;font-size:260px">📏</div>""",
          "Yesterday: fixed alarms cry wolf. Today: let the data tell us what normal is, then flag what leaves it."),

        # 2 Mama Put
        S(f"""
<div class="row" style="gap:50px;align-items:center">
 <div style="flex:1">
  <div class="kicker anim">You already do this</div>
  <h2 class="anim" style="--d:.1s">Mama Put knows her tomato prices 🍅</h2>
  <p class="sub anim" style="--d:.3s">Two weeks at the market and she knows the <b class="teal">normal range</b>. One day the basket costs way more.</p>
  <p class="anim" style="--d:.6s;margin-top:24px">She doesn't need a rulebook. She knows <b class="hl">normal</b>, so she spots <b class="bad">strange</b>.</p>
  <p class="small anim" style="--d:.8s;margin-top:20px">That's a control chart, running in her head.</p>
 </div>
 <div class="card anim a-right" style="--d:.3s;padding:16px"><p class="small" style="margin-left:10px">price of a basket (illustration)</p>{mama}</div>
</div>""",
          "Ask: how does anyone know a price is 'too high'? Because they've seen the normal range. A control chart is exactly that, written down."),

        # 3 section
        S("""
<div class="kicker anim">Part 1</div>
<h1 class="anim" style="--d:.15s">Control charts 📏</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">A centre line, two limits, and the discipline to leave normal alone.</p>""",
          "Section break.", cls="center"),

        # 4 anatomy
        S(f"""
<div class="kicker anim">Anatomy</div>
<h2 class="anim" style="--d:.1s">Three lines, all learned from a quiet stretch</h2>
<div class="grid3" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">➖</div><h3>Centre line</h3><p class="muted">the <b style="color:#fff">mean</b> of a known-good <b style="color:#fff">reference period</b></p></div>
  <div class="card anim a-pop" style="--d:.55s"><div class="icon">⬆️</div><h3>UCL</h3><p class="muted">upper control limit = centre <b style="color:#fff">+ 3σ</b></p></div>
  <div class="card anim a-pop" style="--d:.8s"><div class="icon">⬇️</div><h3>LCL</h3><p class="muted">lower control limit = centre <b style="color:#fff">− 3σ</b></p></div>
</div>
<div class="grid2" style="margin-top:30px">
  <div class="card step" data-step="1" style="border-color:#E5484D"><h3 class="bad">❌ Not the min and max ever seen</h3><p class="muted">One bad day would stretch them forever.</p></div>
  <div class="card step" data-step="1" style="border-color:#E5484D"><h3 class="bad">❌ Not the engineering design limits</h3><p class="muted">Those say “broken”. Control limits say “unusual”.</p></div>
</div>""",
          "Quiz: control limits = 3 standard deviations either side of the reference-period mean. Not min/max, not design limits, not percentiles."),

        # 5 reference period
        S(f"""
<div class="kicker anim">Step 1 · pick a quiet reference period</div>
<h2 class="anim" style="--d:.1s">1–15 August: sunlit, no eclipse yet, nothing strange</h2>
<div class="grid4" style="margin-top:26px">
  <div class="card anim" style="--d:.3s"><div class="stat count" style="font-size:84px" data-to="{len(f['ref'])}" data-d=".4">0</div><div class="stat-label">hours of solar-array current</div></div>
  <div class="card anim" style="--d:.45s"><div class="stat" style="font-size:84px"><span class="count" data-to="{f['centre']:.2f}" data-dec="2" data-d=".5">0</span></div><div class="stat-label">centre line (amps)</div></div>
  <div class="card anim" style="--d:.6s"><div class="stat" style="font-size:84px"><span class="count" data-to="{f['sigma']:.3f}" data-dec="3" data-d=".6">0</span></div><div class="stat-label">σ, the normal wobble (amps)</div></div>
  <div class="card anim glow" style="--d:.75s"><div class="stat hl" style="font-size:40px;line-height:84px;white-space:nowrap">{f['lcl']:.2f}–{f['ucl']:.2f}</div><div class="stat-label">control limits (amps)</div></div>
</div>
<pre class="code anim" style="--d:1s;margin-top:30px">ref = bus.loc["2025-08-01":"2025-08-15", "solar_array_current_a"]
centre, sigma = ref.mean(), ref.std()
ucl, lcl = centre + 3 * sigma, centre - 3 * sigma</pre>""",
          f"The original code book says sd ≈ 0.06 A. That's right only for a clean fortnight like this ({f['sigma']:.3f} A). "
          f"Over all sunlit hours it's {f['sd_all_sunlit']:.3f} A, because recharge hours and the dropouts get mixed in."),

        # 6 August chart
        S(f"""
<div class="kicker anim">Step 2 · watch new readings against the band</div>
<h2 class="anim" style="--d:.1s;font-size:54px">August: one hour falls straight through the floor</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{aug_chart}</div>
<p class="anim" style="--d:3.2s;margin-top:18px">18 Aug, 09:00: the array gave <b class="bad">{aug.loc['2025-08-18 09:00']:.2f} A</b> in full sun. About half its normal output. Remember NigComSat-1 in 2008? 🛰️</p>""",
          "The dropout is so big it's off the chart. Point out the band is narrow because the reference period really was calm."),

        # 7 false-alarm budget
        S(f"""
<div class="row" style="gap:50px;align-items:center">
 <div style="flex:1.1">
  <div class="kicker anim">Why 3σ and not 2σ?</div>
  <h2 class="anim" style="--d:.1s">Every alarm costs attention</h2>
  <p class="sub anim" style="--d:.3s">On perfectly normal data, how many hours land outside the limits by pure chance in <b>2,880 hours</b> (120 days)?</p>
  <div class="col" style="gap:14px;margin-top:26px">
   <div class="card anim" style="--d:.6s;padding:20px 26px"><p><b class="bad">±2σ</b> → 4.6% of hours → <b class="bad">≈ {f['f2']:.0f} false alarms</b> 😩</p></div>
   <div class="card anim" style="--d:.8s;padding:20px 26px"><p><b class="teal">±3σ</b> → 0.27% of hours → <b class="teal">≈ {f['f3']:.0f} false alarms</b> 😌</p></div>
  </div>
  <p class="small anim" style="--d:1.1s;margin-top:20px">On our bus data with rolling limits: ±2σ fires {f['mean2']} times, ±3σ fires {f['mean3']}.</p>
 </div>
 <div class="card anim a-right" style="--d:.4s;padding:16px">{fa}<p class="small" style="text-align:center">expected false alarms per 2,880 normal hours</p></div>
</div>""",
          "Quiz: about 8 false alarms in 2,880 hours at 3 sigma. At 2 sigma it's about 130, and the duty engineer stops listening. That's the alarm-fatigue story from yesterday."),

        # 8 operating states
        S(f"""
<div class="row" style="gap:50px;align-items:center">
 <div style="flex:1">
  <div class="kicker anim">Operating states</div>
  <h2 class="anim" style="--d:.1s">One satellite, three moods 🌗</h2>
  <p class="sub anim" style="--d:.3s">In eclipse the array gives ~0 A. Just after eclipse it works <b>extra</b> to recharge the battery.</p>
  <div class="card step glow" data-step="1" style="margin-top:24px"><h3 class="hl">Rule: separate limits for each state</h3>
   <p class="muted">Mixed, σ grows from <b style="color:#fff">{f['sigma']:.3f}</b> to <b style="color:#fff">{f['sd_all_sunlit']:.3f} A</b> and nothing fires. Don't delete hours or drop to 2σ.</p></div>
 </div>
 <div class="card anim a-right" style="--d:.3s;padding:16px">{sb}
  <p class="small" style="text-align:center">{f['n_eclipse']} eclipse hours · {f['n_recharge']} recharge hours (3 h after each eclipse) · {f['n_sunlit']:,} sunlit hours</p></div>
</div>""",
          "Quiz: eclipse hours are excluded from the reference because they're a different operating state and would widen the limits. Right fix: one set of limits per state."),

        # 9 stale reference
        S(f"""
<div class="kicker anim">The catch</div>
<h2 class="anim" style="--d:.1s;font-size:54px">A fixed reference goes stale: “normal” slowly moves</h2>
<div class="card anim" style="--d:.2s;padding:16px 18px">{stale}</div>
<div class="row anim" style="--d:3s;margin-top:18px;gap:14px;align-items:center">
  <span class="pill bad">{f['n_outside']:,} of {f['n_sunlit']:,} sunlit hours outside the August limits</span>
  <span class="pill">daily average of sunlit current</span>
  <span class="small" style="margin-left:auto">sun angle slowly raises the output through the season</span>
</div>""",
          "The array's normal output creeps up from about 27.9 A to 28.3 A as the season changes. A band learned in early August can't follow. That's not a fault, it's a stale reference."),

        # 10 rolling robust limits
        S(f"""
<div class="kicker anim">The fix · rolling limits</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Learn “normal” from the last 7 days, every hour</h2>
<div class="card anim" style="--d:.2s;padding:14px 18px">{roll_chart}</div>
<div class="row anim" style="--d:3.2s;margin-top:16px;gap:14px;align-items:center">
  <span class="pill teal">band = rolling median ± 3 robust σ (trailing, sunlit hours only)</span>
  <span class="pill bad">{f['flags']} flags = {len(f['big_drop'])} dropout hours + {len(f['false_alarms'])} false alarm</span>
</div>""",
          f"Trailing window of {WIN} hours. The band follows the slow climb and the recharge hours are excluded. Result: the 4 big dropout hours plus one tiny false alarm."),

        # 11 robust
        S(f"""
<div class="kicker anim">Why median and MAD?</div>
<h2 class="anim" style="--d:.1s">One bad hour should not move “normal”</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;border-color:#E5484D"><h3>Mean + standard deviation</h3>
    <p class="muted">Right after the first 28 Sep dropout hour, the rolling σ jumps to</p><div class="stat bad" style="font-size:96px">{f['sd_jump']:.2f} A</div>
    <p class="muted">One wild point poisoned the ruler.</p></div>
  <div class="card anim a-right" style="--d:.5s;border-color:#1E9E5A"><h3>Median + MAD (robust)</h3>
    <p class="muted">Same hour, the robust σ is still</p><div class="stat good" style="font-size:96px">{f['rsd_jump']:.2f} A</div>
    <p class="muted">A few extreme points can't move it.</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:28px;text-align:center"><b class="hl">MAD × 1.4826</b> = same size as σ for normal data, so “3 robust σ” means what you expect.</p>""",
          "Quiz: median and MAD are used because a few extreme points cannot move them. The 1.4826 makes MAD comparable to a standard deviation."),

        # 12 tampering
        S(f"""
<div class="row" style="gap:50px;align-items:center">
 <div style="flex:1.2">
  <div class="kicker anim">Common cause vs special cause</div>
  <h2 class="anim" style="--d:.1s">Don't touch normal wobble 🙅🏾</h2>
  <div class="col" style="gap:16px;margin-top:10px">
   <div class="card anim" style="--d:.3s;padding:20px 26px"><p><b class="teal">Common cause</b>: the everyday wobble inside the band. Leave it.</p></div>
   <div class="card anim" style="--d:.5s;padding:20px 26px"><p><b class="bad">Special cause</b>: outside the band, or a strange pattern. Investigate.</p></div>
   <div class="card step glow" data-step="1" style="padding:20px 26px"><p><b class="hl">Tampering</b> = reacting to common-cause wobble as if it were special. It makes things <b>worse</b>.</p></div>
  </div>
 </div>
 <div class="card anim a-right" style="--d:.4s;flex:.8;text-align:center;padding:36px">
  <div class="big-emoji">🚗</div>
  <p class="muted" style="margin-top:10px">The driver who jams the brake for every small bump on the expressway</p>
  <div class="stat bad count" style="margin-top:14px" data-to="{(f['tamper_ratio'] - 1) * 100:.0f}" data-suf="%" data-d=".8">0</div>
  <div class="stat-label">more wobble when you “correct” every reading (simulation)</div>
 </div>
</div>""",
          "Quiz: reacting to common-cause variation as if it were special cause is called tampering. The simulation: adjusting by the last error every time makes the spread about 41% bigger."),

        # 13 run rules
        S(f"""
<div class="kicker anim">Run rules</div>
<h2 class="anim" style="--d:.1s">Not just “one point outside”</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">💥</div><h3>Rule 1: one point beyond 3σ</h3><p class="muted">Catches <b style="color:#fff">spikes</b> and dropouts.</p>
    <svg viewBox="0 0 560 150" width="100%"><rect x="0" y="40" width="560" height="70" fill="#16A394" fill-opacity=".16"/>
      <path class="draw" d="M10,78 L60,72 L110,84 L160,70 L210,80 L260,14 L310,76 L360,82 L410,71 L460,79 L550,74" fill="none" stroke="#3B8BE0" stroke-width="4"/>
      <circle cx="260" cy="14" r="10" fill="#E5484D"/></svg></div>
  <div class="card anim a-pop" style="--d:.55s"><div class="icon">🪜</div><h3>Rule 2: nine in a row on one side</h3><p class="muted">Catches <b style="color:#fff">level shifts</b>: nothing extreme, just “stuck high”.</p>
    <svg viewBox="0 0 560 150" width="100%"><rect x="0" y="40" width="560" height="70" fill="#16A394" fill-opacity=".16"/>
      <line x1="0" x2="560" y1="75" y2="75" stroke="#EAF2FB" stroke-dasharray="4 6" opacity=".6"/>
      <path class="draw" d="M10,82 L50,70 L90,84 L130,72 L170,60 L210,56 L250,63 L290,54 L330,58 L370,52 L410,61 L450,55 L490,59 L550,53" fill="none" stroke="#3B8BE0" stroke-width="4"/>
      {''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="#F5B83D"/>' for x, y in [(170,60),(210,56),(250,63),(290,54),(330,58),(370,52),(410,61),(450,55),(490,59)])}</svg>
    <p class="small">illustration</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:26px;text-align:center">Keep Rule 2 in your pocket. Tomorrow's slow-creep detector (CUSUM) is its big brother. 👀</p>""",
          "Quiz: run rule 2 (nine consecutive points on one side of the centre line) is most sensitive to level shifts."),

        # 14 section
        S("""
<div class="kicker anim">Part 2</div>
<h1 class="anim" style="--d:.15s">Residuals 🔍</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Stop asking “is this number big?”. Ask “is this number <b>surprising</b>?”</p>""",
          "Section break.", cls="center"),

        # 15 residual flow
        S(f"""
<div class="kicker anim">The idea</div>
<h2 class="anim" style="--d:.1s">Residual = what happened − what you expected</h2>
<div class="flow" style="margin-top:34px;justify-content:center">
  <div class="box anim a-pop" style="--d:.3s"><div class="icon">🌡️</div><h3>Observed</h3><p class="small">today's amplifier temp</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on step" data-step="1"><div class="icon">🧮</div><h3>Expected</h3><p class="small">from a recipe: drive level<br>+ time of year</p></div>
  <div class="arrow step" data-step="1"></div>
  <div class="box on step" data-step="2"><div class="icon">➖</div><h3>Residual</h3><p class="small">observed − expected</p></div>
  <div class="arrow step" data-step="2"></div>
  <div class="box on step" data-step="3"><div class="icon">🚩</div><h3>Flag it</h3><p class="small">if |residual| &gt; 3σ</p></div>
</div>
<p class="anim" style="--d:.8s;margin-top:40px;text-align:center">Mama Put expects tomatoes to be dear when they're scarce. High price in the scarce season? <b>Expected.</b> High price when the market is flooded? <b class="hl">Surprise.</b></p>""",
          "Quiz: a residual is observed value minus expected value. The expected value already includes everything we understand: drive level, season."),

        # 16 raw misses
        S(f"""
<div class="kicker anim">Amplifier (TWTA) temperature · two years, daily</div>
<h2 class="anim" style="--d:.1s;font-size:54px">On the raw chart, the spike hides inside the band</h2>
<div class="card anim" style="--d:.2s;padding:14px 18px">{raw_chart}</div>
<p class="anim" style="--d:3.2s;margin-top:16px">Temperature also rises with <b>drive level</b> and the <b>sun angle</b>, so the raw band must be wide (σ = {f['raw_sd']:.2f} °C). The {f['spike_max']:.1f} °C day never crosses {f['raw_ceiling']:.1f} °C.</p>""",
          "This is why raw thresholds fail on telemetry with known drivers. The band has to make room for normal ups and downs, so real surprises fit inside it."),

        # 17 recipe + residual chart
        S(f"""
<div class="kicker anim">Expected = a recipe learned from 2024</div>
<h2 class="anim" style="--d:.1s;font-size:50px">temp ≈ {f['coef2'][0]:.1f} + {f['coef2'][1]:.2f} × drive + sun-angle wave</h2>
<div class="card anim" style="--d:.2s;padding:14px 18px">{res_chart}</div>
<div class="row anim" style="--d:3.2s;margin-top:14px;gap:14px;align-items:center">
  <span class="pill teal">σ {sd2:.2f} °C (raw: {f['raw_sd']:.2f})</span>
  <span class="pill bad">spike +{f['spike_res']:.1f} °C = {f['spike_sig']:.0f}σ</span>
  <span class="pill gold">after 12 May 2025: {f['n_post_flag']} of {f['n_post']} days flagged</span>
</div>""",
          f"On 3 Sep 2024 the recipe expected {f['spike_exp']:.1f} °C; it was {f['spike_max']:.1f}. The band shrinks from ±{3*f['raw_sd']:.1f} to ±{3*sd2:.2f} °C. "
          "And look at the gold: from 12 May every single day is high. That's not a spike, it's a new normal. Hold that thought."),

        # 18 clean residual checks
        S(f"""
<div class="kicker anim">Is your residual clean?</div>
<h2 class="anim" style="--d:.1s">Three health checks before you trust it</h2>
<div class="grid3" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">⚖️</div><h3>Mean near zero</h3><p class="muted">the recipe isn't biased high or low</p></div>
  <div class="card anim a-pop" style="--d:.5s"><div class="icon">🔗</div><h3>No autocorrelation left</h3><p class="muted">today's surprise doesn't predict tomorrow's</p></div>
  <div class="card anim a-pop" style="--d:.7s"><div class="icon">📏</div><h3>Constant spread</h3><p class="muted">same wobble in every part of the year</p></div>
</div>
<div class="card step glow" data-step="1" style="margin-top:26px"><table style="width:100%;font-size:26px;border-collapse:collapse">
  <tr style="color:var(--muted)"><td></td><td>mean</td><td>lag-1 autocorr</td><td>spread Jan–Jun / Jul–Dec</td></tr>
  <tr><td><b>Recipe fitted on all of 2024</b></td><td>{f['h1']['mean']:.2f}</td><td class="bad">{f['h1']['lag1']:.2f}</td><td class="bad">{f['h1']['h1']:.2f} / {f['h1']['h2']:.2f}</td></tr>
  <tr><td><b>Refit without the 2 spike days</b></td><td>{f['h2']['mean']:.2f}</td><td class="good">{f['h2']['lag1']:.2f}</td><td class="good">{f['h2']['h1']:.2f} / {f['h2']['h2']:.2f}</td></tr>
</table><p class="small" style="margin-top:10px">Two bad days in the training data spoiled the recipe. “Values all above zero” is <b>not</b> a health check: half should be below!</p></div>""",
          "Quiz: the three checks are mean near zero, no autocorrelation left, constant spread over time. 'Values all above zero' is the wrong one."),

        # 19 centred cheats
        S(f"""
<div class="kicker anim">Careful with centred windows</div>
<h2 class="anim" style="--d:.1s">A centred window swallows part of the spike</h2>
<div class="grid2" style="margin-top:22px">
  <div class="card anim a-left" style="--d:.3s;border-color:#1E9E5A"><h3>Trailing 7-day median</h3><p class="muted">expected = the week <b style="color:#fff">before</b></p>
    <div class="stat good" style="font-size:96px">+{f['tm7_res']:.1f} °C</div><p class="muted">residual on 3 Sep 2024</p></div>
  <div class="card anim a-right" style="--d:.5s;border-color:#E5484D"><h3>Centred 7-day mean</h3><p class="muted">expected includes the spike itself (and the future)</p>
    <div class="stat bad" style="font-size:96px">+{f['cm7_res']:.1f} °C</div><p class="muted">residual on 3 Sep 2024</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:28px;text-align:center">The spike is <b>inside</b> its own window, so it drags “expected” up and hides part of itself. Wider windows hide less, but it's still cheating with the future. Trailing only. 🔮🚫</p>""",
          "Quiz: true, a centred 61-day rolling mean can absorb part of the spike it's meant to detect. On our data the 61-day version absorbs only a little; the 7-day one shows it clearly."),

        # 20 shapes / cliffhanger
        S(f"""
<div class="kicker anim">Three shapes of trouble</div>
<h2 class="anim" style="--d:.1s;font-size:54px">A rolling “expected” follows slow change… so it misses it</h2>
<div class="card anim" style="--d:.2s;padding:12px 18px">{roll_tw}</div>
<div class="grid3" style="margin-top:16px;gap:20px">
  <div class="card anim" style="--d:3s;padding:16px 22px"><p style="font-size:24px"><b class="good">💥 Spike</b>: caught ({f['rz_spike']:.0f} robust σ)</p></div>
  <div class="card anim" style="--d:3.2s;padding:16px 22px"><p style="font-size:24px"><b class="hl">🪜 Level shift</b>: <b>{f['roll_post_flags']}</b> flags after 12 May</p></div>
  <div class="card anim" style="--d:3.4s;padding:16px 22px"><p style="font-size:24px"><b class="bad">🐢 Slow drift</b>: never seen</p></div>
</div>""",
          "Quiz: a rolling-model residual detector is useless on slow drift. Cliffhanger for tomorrow: CUSUM keeps a running total so slow change can't hide."),

        # 21 your turn
        S("""
<div class="row" style="gap:60px;align-items:center;height:100%">
 <div style="flex:1.2">
  <div class="kicker anim">Your turn · 60 minutes</div>
  <h2 class="anim" style="--d:.1s">Open the W3D2 exercise 🧑🏾‍💻</h2>
  <div class="col" style="gap:16px;margin-top:20px">
   <div class="row anim" style="--d:.3s;gap:18px;align-items:center"><span class="num">A</span><p>Build a control chart for the solar array, and watch it go stale</p></div>
   <div class="row anim" style="--d:.5s;gap:18px;align-items:center"><span class="num">B</span><p>Rolling robust limits, then residuals on the amplifier</p></div>
   <div class="row anim" style="--d:.7s;gap:18px;align-items:center"><span class="num">🌶️</span><p>Bonus: prove tampering makes things worse</p></div>
  </div>
 </div>
 <div class="card glow anim a-pop" style="--d:.9s;flex:1;text-align:center;padding:44px">
  <div class="big-emoji floaty">📏</div>
  <h3 style="margin-top:16px">14 checks to pass</h3>
  <p class="muted">File → Save a copy in Drive first!<br>Run STEP 0, then top to bottom.</p>
  <p class="small" style="margin-top:18px">Keep the <b>rule book</b> open next to you.</p>
 </div>
</div>""",
          "Hands-on. Most common problems: forgetting .loc with dates, mixing up observed − expected order, using the wrong state."),

        # 22 recap
        S("""
<div class="kicker anim">Today in 3 lines</div>
<h2 class="anim" style="--d:.1s">What you now know</h2>
<div class="col" style="gap:22px;margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">📏</span><p><b>Control chart:</b> centre ± 3σ from a quiet reference, <b class="hl">one set of limits per operating state</b>, refreshed so it doesn't go stale.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🛡️</span><p><b>Robust:</b> median + MAD × 1.4826, so one wild hour can't move “normal”. Don't tamper with common-cause wobble.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center"><span class="icon" style="margin:0">🔍</span><p><b>Residual</b> = observed − expected. Check it's clean. Great for spikes, weak on shifts, useless on slow drift.</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:28px">Next 👉 <b class="hl">The Slow Creep: Drift and CUSUM</b> 🏠</p>""",
          "Recap and tease W3D3."),
    ]
    return s


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    f = facts()
    st = f["states"]
    dmin = f["daily_min"]
    dm = f["daily_sunlit"]
    labels = [d.strftime("%-d %b") if d.day in (1, 15) else "" for d in dm.index]
    temp, res2 = f["temp"], f["res2"]
    tlab = [d.strftime("%b %y") if d.day == 1 and d.month in (1, 4, 7, 10) else "" for d in temp.index]
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "📏", "kicker": "Week 3 · Day 2", "title": "Control Charts and Residuals",
             "sub": "Learn what normal looks like, then flag what leaves it", "notes": "Yesterday fixed alarms cried wolf. Today the data sets the limits."},
            {"type": "statement", "title": "Mama Put knows the price of tomatoes", "icon": "🍅",
             "big": "Know the normal range, and the strange price jumps out",
             "sub": "A control chart is that market instinct, written down", "notes": "Ask how anyone knows a price is too high."},
            {"type": "section", "kicker": "Part 1", "title": "Control charts", "sub": "Centre line, two limits, and the discipline to leave normal alone", "notes": "Section break."},
            {"type": "cards", "title": "Three lines, learned from a quiet stretch", "cards": [
                ["➖", "Centre line", "mean of a known-good reference period"],
                ["⬆️", "UCL", "centre + 3σ"],
                ["⬇️", "LCL", "centre − 3σ (not min/max, not design limits)"]],
             "notes": "Control limits = 3 standard deviations either side of the reference-period mean."},
            {"type": "stats", "title": "Reference period: 1–15 August", "sub": "Solar-array current, sunlit, before the eclipse season",
             "stats": [[f"{len(f['ref'])}", "hours"], [f"{f['centre']:.2f} A", "centre line"], [f"{f['sigma']:.3f} A", "σ (normal wobble)"],
                       [f"{f['lcl']:.2f}–{f['ucl']:.2f}", "control limits (A)"]],
             "notes": f"Original code book's 0.06 A only holds for a clean fortnight. All sunlit hours: {f['sd_all_sunlit']:.3f} A."},
            {"type": "chart", "title": "Daily lowest current: dropouts fall through the floor",
             "labels": labels, "series": [
                 {"name": "daily minimum (A)", "values": dmin.round(2).tolist(), "color": "0A5DB4"},
                 {"name": "LCL", "values": [round(f["lcl"], 2)] * len(dmin), "color": "008C7E"}],
             "ymin": 14, "ymax": 30, "fmt": "0",
             "notes": f"Three days drop to about 15 A, roughly half the normal output. Lowest: {f['drop_min']:.2f} A."},
            {"type": "bar", "title": "Why 3σ: false alarms in 2,880 normal hours", "labels": ["±2σ", "±3σ"],
             "values": [round(f["f2"]), round(f["f3"])], "highlight": [0], "fmt": "0",
             "caption": f"Theory on normal data. On our bus data with rolling limits: ±2σ fires {f['mean2']} times, ±3σ fires {f['mean3']}.",
             "notes": "About 8 false alarms at 3 sigma, about 130 at 2 sigma."},
            {"type": "bar", "title": "One satellite, three operating states", "labels": ["eclipse", "sunlit", "recharge"],
             "values": [round(st.loc["eclipse", "mean"], 2), round(st.loc["sunlit", "mean"], 2), round(st.loc["recharge", "mean"], 2)],
             "highlight": [0, 2], "fmt": "0.0", "ymax": 33,
             "caption": f"Separate limits per state. Mixing them grows σ from {f['sigma']:.3f} A to {f['sd_all_sunlit']:.3f} A.",
             "notes": "Fix false alarms with one set of limits per state, not wider limits or deleting data."},
            {"type": "chart", "title": "A fixed reference goes stale",
             "labels": labels, "series": [
                 {"name": "daily mean sunlit current", "values": dm.round(3).tolist(), "color": "0A5DB4"},
                 {"name": "UCL", "values": [round(f["ucl"], 3)] * len(dm), "color": "C77700"},
                 {"name": "LCL", "values": [round(f["lcl"], 3)] * len(dm), "color": "008C7E"}],
             "ymin": 27.4, "ymax": 28.5, "fmt": "0.0",
             "notes": f"{f['n_outside']:,} of {f['n_sunlit']:,} sunlit hours outside the August limits: the normal level climbs with the season."},
            {"type": "compare", "title": "Rolling limits, robust statistics",
             "left": ["📉", f"Mean + σ: {f['sd_jump']:.2f} A", "Right after a dropout hour the rolling σ explodes. One wild point poisons the ruler"],
             "right": ["🛡️", f"Median + MAD: {f['rsd_jump']:.2f} A", f"Barely moves. Trailing 7-day rolling limits give {f['flags']} flags: {len(f['big_drop'])} dropouts + {len(f['false_alarms'])} false alarm"],
             "notes": "MAD × 1.4826 makes it comparable to a standard deviation."},
            {"type": "cards", "title": "Common cause, special cause, tampering", "cards": [
                ["🌊", "Common cause", "everyday wobble inside the band: leave it"],
                ["🚨", "Special cause", "outside the band or a strange run: investigate"],
                ["🚗", "Tampering", f"reacting to normal wobble: spread grows ~{(f['tamper_ratio'] - 1) * 100:.0f}%"]],
             "notes": "Reacting to common-cause variation as if it were special cause is tampering."},
            {"type": "compare", "title": "Run rules",
             "left": ["💥", "Rule 1: one point beyond 3σ", "catches spikes and dropouts"],
             "right": ["🪜", "Rule 2: nine in a row", "all on one side of the centre: catches level shifts (tomorrow: CUSUM)"],
             "notes": "Run rule 2 is most sensitive to level shifts."},
            {"type": "section", "kicker": "Part 2", "title": "Residuals", "sub": "Not “is it big?” but “is it surprising?”", "notes": "Section break."},
            {"type": "flow", "title": "Residual = observed − expected", "steps": [
                ["🌡️", "Observed", "today's amplifier temperature"],
                ["🧮", "Expected", "recipe: drive level + time of year"],
                ["🚩", "Residual", "flag it if bigger than 3σ"]],
             "footer": "Dear tomatoes in the scarce season: expected. Dear tomatoes in a glut: surprise.", "notes": "Residual is observed minus expected."},
            {"type": "twochart", "title": "Amplifier temperature: raw vs residual",
             "left": {"label": f"Raw: the {f['spike_max']:.1f} °C spike stays under the {f['raw_ceiling']:.1f} °C ceiling", "labels": tlab,
                      "values": temp.round(2).tolist(), "ymin": 58, "ymax": 71, "fmt": "0", "freq": 1, "good": True},
             "right": {"label": f"Residual: the spike is {f['spike_sig']:.0f}σ; every day after 12 May is high", "labels": tlab,
                       "values": res2.round(2).tolist(), "ymin": -2, "ymax": 6, "fmt": "0", "freq": 1},
             "notes": f"Residual σ {f['sd2']:.2f} °C vs raw σ {f['raw_sd']:.2f} °C."},
            {"type": "table", "title": "Is the residual clean?", "header": ["Recipe", "Mean", "Lag-1 autocorr", "Spread H1 / H2"],
             "rows": [["Fitted on all of 2024", f"{f['h1']['mean']:.2f}", f"{f['h1']['lag1']:.2f}", f"{f['h1']['h1']:.2f} / {f['h1']['h2']:.2f}"],
                      ["Refit without the 2 spike days", f"{f['h2']['mean']:.2f}", f"{f['h2']['lag1']:.2f}", f"{f['h2']['h1']:.2f} / {f['h2']['h2']:.2f}"]],
             "colW": [4.6, 2.1, 2.6, 2.83],
             "caption": "Checks: mean near zero · no autocorrelation left · constant spread. Never “all above zero”.",
             "notes": "Two bad days in the training data spoiled the recipe."},
            {"type": "cards", "title": "Three shapes of trouble", "cards": [
                ["💥", "Spike", f"residuals catch it ({f['spike_sig']:.0f}σ)"],
                ["🪜", "Level shift", f"fixed recipe: {f['n_post_flag']}/{f['n_post']} days. Rolling: {f['roll_post_flags']} flags"],
                ["🐢", "Slow drift", "rolling residual: useless. Tomorrow: CUSUM"]],
             "notes": "Centred windows also swallow part of a spike and peek at the future. Trailing only."},
            {"type": "steps", "title": "Your turn: 60 minutes", "icon": "🧑🏾‍💻", "steps": [
                "Open W3D2-exercise in Colab", "File → Save a copy in Drive", "Run STEP 0, then top to bottom",
                "Replace every ___, run, get the green tick"], "notes": "Walk the room."},
            {"type": "recap", "title": "What you now know", "points": [
                ["📏", "Control chart: centre ± 3σ, one set of limits per operating state, keep it fresh"],
                ["🛡️", "Robust: median + MAD × 1.4826; never tamper with common-cause wobble"],
                ["🔍", "Residual = observed − expected; check it's clean; weak on slow drift"]],
             "next": "Next: The Slow Creep: Drift and CUSUM", "notes": "Tease W3D3."},
        ],
    }


# =============================================================================
# NOTEBOOK
# =============================================================================
CHECKS = r'''
def _bus():
    b = pd.read_csv(data_path("bus_power_telemetry_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")
    e = b["eclipse_flag"]
    after = (e.shift(1, fill_value=0) + e.shift(2, fill_value=0) + e.shift(3, fill_value=0)) > 0
    b["state"] = np.where(e == 1, "eclipse", np.where(after, "recharge", "sunlit"))
    return b

def _ref():
    return _bus().loc["2025-08-01":"2025-08-15", "solar_array_current_a"]

def _limits():
    r = _ref()
    return r.mean() - 3 * r.std(), r.mean() + 3 * r.std()

def _close(a, b, tol):
    return abs(float(a) - float(b)) <= tol

def _tw_resid(skip=()):
    tw = pd.read_csv(data_path("twta_thermal_daily"), parse_dates=["date"], index_col="date").asfreq("D")
    doy = tw.index.dayofyear
    X = np.column_stack([np.ones(len(tw)), tw["rf_drive_pct"], np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)])
    train = (tw.index <= pd.Timestamp("2024-12-31")) & ~tw.index.isin(pd.to_datetime(list(skip)))
    coef, *_ = np.linalg.lstsq(X[train], tw["twta_temp_c"].values[train], rcond=None)
    return tw["twta_temp_c"] - X @ coef, train

def _c_a1(x):
    n = int((_bus()["state"] == "recharge").sum())
    return int(x) == n, f"{n} recharge hours: the array works overtime for 3 hours after every eclipse. 🔋", \
        "Count the rows where bus[\"state\"] == \"recharge\" (True counts as 1, so .sum() works)."

def _c_a2(x):
    r = _ref()
    ok = _close(x[0], r.mean(), 0.005) and _close(x[1], r.std(), 0.002)
    return ok, f"Centre {r.mean():.2f} A, σ {r.std():.3f} A. A calm fortnight has a tiny wobble.", \
        "centre = ref.mean() and sigma = ref.std()"

def _c_a3(x):
    lo, hi = _limits()
    ok = _close(x[0], lo, 0.005) and _close(x[1], hi, 0.005)
    return ok, f"Limits {lo:.2f} A to {hi:.2f} A. Mama Put's price range, in amps. 🍅", \
        "lcl = centre - 3 * sigma, ucl = centre + 3 * sigma (in that order: low first)."

def _c_a4(x):
    b = _bus(); lo, hi = _limits()
    s = b.loc[b["state"] == "sunlit", "solar_array_current_a"]
    n = int(((s < lo) | (s > hi)).sum())
    return int(x) == n, f"{n:,} of {len(s):,} sunlit hours! Not faults: 'normal' slowly climbs with the season. A fixed reference goes stale.", \
        "outside is True/False per hour. Count the Trues with outside.sum()."

def _c_a5(x):
    ok = _close(x[0], 2880 * 0.0027, 0.6) and _close(x[1], 2880 * 0.0455, 3)
    return ok, "About 8 vs about 131. That's why we use 3σ: fewer pointless alarms at 3am. 😴", \
        "false_3sigma = hours * 0.0027 and false_2sigma = hours * 0.0455"

def _robust_flags():
    b = _bus()
    x = b["solar_array_current_a"].where(b["state"] == "sunlit")
    med = x.rolling(168, min_periods=48).median().shift(1)
    rsd = (x - med).abs().rolling(168, min_periods=48).median().shift(1) * 1.4826
    return ((x - med) / rsd).abs() > 3

def _c_b1(x):
    n = int(_robust_flags().sum())
    return int(x) == n, f"{n} flags: 4 real dropout hours and just 1 false alarm in 120 days. Rolling + robust = calm and sharp. 🎯", \
        "Count where the robust z is beyond 3 either way: (z.abs() > 3).sum()"

def _c_b2(x):
    a, b2 = (str(v).strip().lower() for v in x)
    return (a == "b") and (b2 == "c"), "Yes: median/MAD ignore a few wild points, and × 1.4826 makes MAD the same size as σ.", \
        "Re-read the two questions: one is about extreme points, the other about matching σ."

def _c_b3(x):
    r, _ = _tw_resid()
    ok = isinstance(x, pd.Series) and len(x) == len(r) and _close(x.loc["2024-09-03"], r.loc["2024-09-03"], 0.01)
    return ok, f"Residual on 3 Sep 2024: {r.loc['2024-09-03']:+.2f} °C. Hot for its drive level and time of year! 🌡️", \
        "residual = observed - expected = tw[\"twta_temp_c\"] - expected (a whole column, not one number)."

def _c_b4(x):
    return str(x).strip().lower() in {"no", "n", "false"}, \
        "Correct: lag-1 autocorrelation is high and the second half of 2024 wobbles twice as much. Something in the training data is spoiling the recipe.", \
        "Compare against the 3 checks: mean near 0? lag-1 near 0? same spread in both halves?"

def _c_b5(x):
    r, train = _tw_resid()
    w = r[train].abs().idxmax()
    return pd.Timestamp(x) == w, f"{pd.Timestamp(x).date()}: the transient spike. It was hiding inside the training data. 🕵🏾", \
        "Use residual[train].abs().idxmax(): the date with the biggest surprise."

def _c_b6(x):
    r, train = _tw_resid(("2024-09-03", "2024-09-04"))
    s = r.loc["2024-09-03"] / r[train].std()
    return _close(x, s, 0.6), f"{s:.0f}σ! On the raw chart it was invisible; as a residual it screams. 📢", \
        "spike_sigmas = residual2.loc[\"2024-09-03\"] / sigma2"

def _c_b7(x):
    r, train = _tw_resid(("2024-09-03", "2024-09-04"))
    z = r / r[train].std()
    post = z.loc["2025-05-12":]
    n = int((post.abs() > 3).sum())
    return int(x) == n, f"{n} of {len(post)} days: every single one. That's not a spike, it's a NEW NORMAL (a level shift).", \
        "Count where z2 after 12 May 2025 is beyond 3: (z2.loc[\"2025-05-12\":].abs() > 3).sum()"

def _c_b8(x):
    t = pd.read_csv(data_path("twta_thermal_daily"), parse_dates=["date"], index_col="date").asfreq("D")["twta_temp_c"]
    med = t.rolling(30).median().shift(1)
    rsd = (t - med).abs().rolling(30).median().shift(1) * 1.4826
    n = int(((t - med) / rsd).loc["2025-05-12":].abs().gt(3).sum())
    return int(x) == n, f"{n}! The rolling window swallowed the shift. Slow change hides from rolling detectors. Tomorrow: CUSUM. 👀", \
        "Count where rz after 12 May 2025 is beyond 3."

def _c_bonus(x):
    return 1.25 <= float(x) <= 1.6, f"{float(x):.2f}×: 'correcting' every wobble made the spread ~{(float(x) - 1) * 100:.0f}% WORSE. That's tampering. 🙅🏾", \
        "ratio = tampered.std() / calm.std()"

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "A5": _c_a5,
          "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4, "B5": _c_b5, "B6": _c_b6, "B7": _c_b7, "B8": _c_b8,
          "BONUS": _c_bonus}
HINTS = {"A2": "Two numbers: centre = ref.mean(), sigma = ref.std().", "A3": "Two numbers: lcl first, then ucl.",
         "B3": "residual must be the whole column: observed column minus the expected column.",
         "B5": "idxmax() returns the date of the biggest value."}
'''


def notebook_cells(setup_code):
    return [
        ("md", """# 📏 Week 3 · Day 2: Control Charts and Residuals

**Today:** learn what "normal" looks like for the satellite's solar array, draw the limits, then catch surprises in the amplifier using *expected vs observed*.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |
| 🌶️ | Bonus task for fast finishers |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**
> Work in your copy (the new tab), not the original.

**Rule book:** keep `W3D2-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up (run this once, every time you open the notebook)
You should see `✅ Ready!`. If Colab says *"This notebook was not authored by Google"*, click **Run anyway**."""),
        ("setup", setup_code),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: A control chart for the solar array (25 min) ☀️

**The data:** `bus_power_telemetry_hourly`: 120 days of hourly power telemetry. We watch `solar_array_current_a`, the current from the solar panels.

▶️ Run this. It loads the file and labels every hour with its **operating state**:
- **eclipse**: the Earth blocks the sun, the array gives ~0 A (the satellite's own "NEPA has taken light")
- **recharge**: the 3 hours just after an eclipse, when the array works extra to refill the battery
- **sunlit**: normal life"""),
        ("code", 'bus = pd.read_csv(data_path("bus_power_telemetry_hourly"), parse_dates=["timestamp"], index_col="timestamp").asfreq("h")\n\n'
                 '# label each hour with its operating state\n'
                 'e = bus["eclipse_flag"]\n'
                 'just_after_eclipse = (e.shift(1, fill_value=0) + e.shift(2, fill_value=0) + e.shift(3, fill_value=0)) > 0\n'
                 'bus["state"] = np.where(e == 1, "eclipse", np.where(just_after_eclipse, "recharge", "sunlit"))\n\n'
                 'bus.groupby("state")["solar_array_current_a"].agg(["count", "mean", "std"]).round(3)'),
        ("md", """### A1 ✍️ How many recharge hours?
Three moods, three very different currents. That's why each state needs **its own** limits."""),
        ("task", 'n_recharge = ___\n\ncheck("A1", n_recharge)', 'n_recharge = (bus["state"] == "recharge").sum()\n\ncheck("A1", n_recharge)'),
        ("md", """### A2 ✍️ The reference period: Mama Put's two weeks at the market 🍅
1–15 August is calm: sunlit, no eclipse season yet, nothing strange. Learn **normal** from it: the centre (mean) and the wobble (standard deviation, σ)."""),
        ("task", 'ref = bus.loc["2025-08-01":"2025-08-15", "solar_array_current_a"]\n\ncentre = ___      # the mean of ref\nsigma = ___       # the standard deviation of ref\n\ncheck("A2", (centre, sigma))',
         'ref = bus.loc["2025-08-01":"2025-08-15", "solar_array_current_a"]\n\ncentre = ref.mean()      # the mean of ref\nsigma = ref.std()       # the standard deviation of ref\n\ncheck("A2", (centre, sigma))'),
        ("md", "### A3 ✍️ The control limits\nLower and upper control limits sit **3σ** either side of the centre."),
        ("task", 'lcl = ___      # centre minus 3 sigma\nucl = ___      # centre plus 3 sigma\n\ncheck("A3", (lcl, ucl))',
         'lcl = centre - 3 * sigma      # centre minus 3 sigma\nucl = centre + 3 * sigma      # centre plus 3 sigma\n\ncheck("A3", (lcl, ucl))'),
        ("md", "▶️ Draw August against the band. Something drops straight through the floor on 18 August…"),
        ("code", 'assert ucl is not None and lcl is not None, "✍️ Do A2 and A3 first, then run this cell again."\n\n'
                 'aug = bus.loc["2025-08-01":"2025-08-31", "solar_array_current_a"]\n'
                 'ax = aug.plot(lw=1, title="August: one hour falls through the floor")\n'
                 'ax.axhspan(lcl, ucl, color="#008C7E", alpha=.15, label="control limits")\n'
                 'ax.set_ylim(27.3, 28.6); ax.set_ylabel("amps"); ax.legend()\n'
                 'plt.show()\n'
                 'print("Lowest August reading:", aug.min(), "A at", aug.idxmin())'),
        ("md", """### A4 ✍️ Does the August band still work in November?
Apply the same fixed limits to **every sunlit hour** in the file. How many hours land outside?"""),
        ("task", 'assert ucl is not None and lcl is not None, "✍️ Do A3 first."\n\nsunlit = bus.loc[bus["state"] == "sunlit", "solar_array_current_a"]\noutside = (sunlit < lcl) | (sunlit > ucl)\n\nn_outside = ___\n\ncheck("A4", n_outside)',
         'assert ucl is not None and lcl is not None, "✍️ Do A3 first."\n\nsunlit = bus.loc[bus["state"] == "sunlit", "solar_array_current_a"]\noutside = (sunlit < lcl) | (sunlit > ucl)\n\nn_outside = outside.sum()\n\ncheck("A4", n_outside)'),
        ("code", 'sunlit.resample("D").mean().plot(title="Daily average sunlit current vs the August band")\nplt.axhspan(lcl, ucl, color="#008C7E", alpha=.15)\nplt.ylabel("amps"); plt.show()'),
        ("md", """📖 The array's normal output slowly **climbs** as the season changes. The band learned in August can't follow: the reference has gone **stale**. Fix coming in Part B.

### A5 ✍️ The false-alarm budget
On perfectly normal data, ±3σ is crossed by chance about **0.27%** of the time, and ±2σ about **4.55%**. How many false alarms would each give in 2,880 hours?"""),
        ("task", 'hours = 2880\nfalse_3sigma = ___\nfalse_2sigma = ___\n\ncheck("A5", (false_3sigma, false_2sigma))',
         'hours = 2880\nfalse_3sigma = hours * 0.0027\nfalse_2sigma = hours * 0.0455\n\ncheck("A5", (false_3sigma, false_2sigma))'),

        # ---------------- PART B ----------------
        ("md", """---
# Part B: Rolling robust limits, then residuals (35 min) 🔍

### B1 ✍️ Rolling limits that follow "normal"
▶️ The code learns "normal" from the **last 7 days** (168 hours) before each hour, sunlit hours only:
- **rolling median** = the typical value (Mama Put's usual price)
- **robust σ** = median of the distances from it × 1.4826
- **z** = how many robust σ this hour is from normal

`.shift(1)` means each hour is judged only by the hours **before** it. No peeking. Count the hours with z beyond ±3."""),
        ("task", 'x = bus["solar_array_current_a"].where(bus["state"] == "sunlit")      # other states become NaN\n'
                 'med = x.rolling(168, min_periods=48).median().shift(1)\n'
                 'robust_sigma = (x - med).abs().rolling(168, min_periods=48).median().shift(1) * 1.4826\n'
                 'z = (x - med) / robust_sigma\n\n'
                 'n_flags = ___\n\ncheck("B1", n_flags)',
         'x = bus["solar_array_current_a"].where(bus["state"] == "sunlit")      # other states become NaN\n'
         'med = x.rolling(168, min_periods=48).median().shift(1)\n'
         'robust_sigma = (x - med).abs().rolling(168, min_periods=48).median().shift(1) * 1.4826\n'
         'z = (x - med) / robust_sigma\n\n'
         'n_flags = (z.abs() > 3).sum()\n\ncheck("B1", n_flags)'),
        ("code", 'flagged = bus.loc[z.abs() > 3, ["solar_array_current_a", "state"]].assign(z=z[z.abs() > 3].round(1))\nflagged'),
        ("md", """### B2 ✍️ Why robust?
▶️ First run this: right after the first 28 Sep dropout hour, compare a normal rolling σ with the robust σ."""),
        ("code", 'plain_sigma = x.rolling(168, min_periods=48).std().shift(1)\nprint("plain rolling σ at 2025-09-28 15:00:", round(plain_sigma.loc["2025-09-28 15:00"], 3), "A")\nprint("robust σ at the same hour:          ", round(robust_sigma.loc["2025-09-28 15:00"], 3), "A")'),
        ("md", """Now answer with a letter, in quotes:

**Q1.** Why use the median and MAD instead of the mean and standard deviation?
(a) they're faster to compute  (b) a few extreme points can't move them  (c) they remove the trend

**Q2.** Why multiply MAD by 1.4826?
(a) to widen the limit to 4σ  (b) to convert °C to kelvin  (c) to make it the same size as a standard deviation"""),
        ("task", 'q1 = ___\nq2 = ___\n\ncheck("B2", (q1, q2))', 'q1 = "b"\nq2 = "c"\n\ncheck("B2", (q1, q2))'),
        ("md", """### B3 ✍️ Residual = observed − expected (the amplifier)
**The data:** `twta_thermal_daily`: two years of the amplifier's daily temperature. It runs hotter when **drive** is higher and when the **sun angle** heats that side of the satellite, so a big number isn't automatically a surprise.

▶️ The function below is the **recipe** for "expected": it learns `temp ≈ base + k × drive + sun-angle wave` from the 2024 days. Run it, then compute the residual."""),
        ("code", 'tw = pd.read_csv(data_path("twta_thermal_daily"), parse_dates=["date"], index_col="date").asfreq("D")\n\n'
                 'def expected_temp(tw, skip_days=()):\n'
                 '    """The recipe: base + k × drive + yearly sun-angle wave, learned from 2024 (minus any skipped days)."""\n'
                 '    doy = tw.index.dayofyear\n'
                 '    X = np.column_stack([np.ones(len(tw)), tw["rf_drive_pct"],\n'
                 '                         np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)])\n'
                 '    train = (tw.index <= pd.Timestamp("2024-12-31")) & ~tw.index.isin(pd.to_datetime(list(skip_days)))\n'
                 '    coef, *_ = np.linalg.lstsq(X[train], tw["twta_temp_c"].values[train], rcond=None)\n'
                 '    return pd.Series(X @ coef, index=tw.index), train\n\n'
                 'expected, train = expected_temp(tw)\n'
                 'tw.assign(expected=expected.round(2)).head()'),
        ("task", 'residual = ___      # observed minus expected (the whole column)\n\ncheck("B3", residual)',
         'residual = tw["twta_temp_c"] - expected      # observed minus expected (the whole column)\n\ncheck("B3", residual)'),
        ("md", """### B4 ✍️ Health check: is the residual clean?
▶️ Run the three checks on the **2024** residuals: mean near zero? lag-1 autocorrelation near zero? same spread in both halves of the year? Then answer `"yes"` or `"no"`."""),
        ("code", 'assert residual is not None, "✍️ Do B3 first."\nr24 = residual[train]\nprint("mean               :", round(r24.mean(), 3))\nprint("lag-1 autocorr     :", round(r24.autocorr(1), 2))\nprint("spread Jan–Jun 2024:", round(r24.loc[:"2024-06-30"].std(), 3))\nprint("spread Jul–Dec 2024:", round(r24.loc["2024-07-01":].std(), 3))'),
        ("task", 'is_clean = ___\n\ncheck("B4", is_clean)', 'is_clean = "no"\n\ncheck("B4", is_clean)'),
        ("md", "### B5 ✍️ Find the troublemaker\nWhich 2024 day has the biggest surprise (largest residual, up or down)?"),
        ("task", 'worst_day = ___\n\ncheck("B5", worst_day)', 'worst_day = residual[train].abs().idxmax()\n\ncheck("B5", worst_day)'),
        ("md", """### B6 ✍️ Refit without the bad days, then measure the spike
▶️ The spike (3–4 Sep 2024) was teaching the recipe bad habits. Refit without those two days and the residual becomes clean. Then: how many σ is 3 Sep?"""),
        ("code", 'expected2, train2 = expected_temp(tw, skip_days=("2024-09-03", "2024-09-04"))\n'
                 'residual2 = tw["twta_temp_c"] - expected2\n'
                 'sigma2 = residual2[train2].std()\n'
                 'r = residual2[train2]\n'
                 'print("clean now? mean", round(r.mean(), 3), "| lag-1", round(r.autocorr(1), 2),\n'
                 '      "| spread", round(r.loc[:"2024-06-30"].std(), 3), "vs", round(r.loc["2024-07-01":].std(), 3))\n'
                 'print("residual σ:", round(sigma2, 3), "°C")\n'
                 'residual2.plot(lw=1, title="Amplifier temperature: surprise vs the recipe")\n'
                 'plt.axhspan(-3 * sigma2, 3 * sigma2, color="#008C7E", alpha=.15); plt.ylabel("°C"); plt.show()'),
        ("task", 'spike_sigmas = ___      # residual2 on 2024-09-03, divided by sigma2\n\ncheck("B6", spike_sigmas)',
         'spike_sigmas = residual2.loc["2024-09-03"] / sigma2      # residual2 on 2024-09-03, divided by sigma2\n\ncheck("B6", spike_sigmas)'),
        ("md", "### B7 ✍️ What happens after 12 May 2025?\nCount the days from 12 May 2025 onward where `z2` is beyond ±3."),
        ("task", 'z2 = residual2 / sigma2\n\nn_after = ___\nprint("days after 12 May:", len(z2.loc["2025-05-12":]))\n\ncheck("B7", n_after)',
         'z2 = residual2 / sigma2\n\nn_after = (z2.loc["2025-05-12":].abs() > 3).sum()\nprint("days after 12 May:", len(z2.loc["2025-05-12":]))\n\ncheck("B7", n_after)'),
        ("md", """### B8 ✍️ And a rolling detector?
▶️ This one learns "expected" as the **trailing 30-day median** of the raw temperature, the same robust idea as B1. How many days after 12 May does it flag?"""),
        ("task", 't = tw["twta_temp_c"]\nroll_med = t.rolling(30).median().shift(1)\nroll_sigma = (t - roll_med).abs().rolling(30).median().shift(1) * 1.4826\nrz = (t - roll_med) / roll_sigma\n\nn_rolling_after = ___\n\ncheck("B8", n_rolling_after)',
         't = tw["twta_temp_c"]\nroll_med = t.rolling(30).median().shift(1)\nroll_sigma = (t - roll_med).abs().rolling(30).median().shift(1) * 1.4826\nrz = (t - roll_med) / roll_sigma\n\nn_rolling_after = (rz.loc["2025-05-12":].abs() > 3).sum()\n\ncheck("B8", n_rolling_after)'),
        ("code", '(t - roll_med).loc["2025-04-15":"2025-07-15"].plot(title="Rolling residual: the shift fades as the window swallows it")\nplt.axhline(0, color="grey", lw=1); plt.ylabel("°C"); plt.show()'),
        ("md", """📖 The rolling window **follows** slow change, so a level shift fades out of its residual in about three weeks, and a slow drift never shows at all. Tomorrow: **CUSUM**, which keeps a running total so slow change can't hide.

---
## 🌶️ Pepper task (bonus): does "correcting" every wobble help?
▶️ The simulation below runs a calm process (pure common-cause noise), and an over-eager operator who "corrects" the setting after **every** reading by the full error. Compute how much bigger the tampered spread is: `tampered.std() / calm.std()`."""),
        ("task", 'rng = np.random.default_rng(42)\ncalm = rng.normal(0, 1, 2000)          # leave the process alone\n\nadjust, tampered = 0.0, []\nfor wobble in calm:\n    reading = adjust + wobble\n    tampered.append(reading)\n    adjust -= reading                    # "correct" every wobble\ntampered = np.array(tampered)\n\nratio = ___\ncheck("BONUS", ratio)',
         'rng = np.random.default_rng(42)\ncalm = rng.normal(0, 1, 2000)          # leave the process alone\n\nadjust, tampered = 0.0, []\nfor wobble in calm:\n    reading = adjust + wobble\n    tampered.append(reading)\n    adjust -= reading                    # "correct" every wobble\ntampered = np.array(tampered)\n\nratio = tampered.std() / calm.std()\ncheck("BONUS", ratio)'),
        ("md", "---\n## 🏁 Finish line\n▶️ Run the scoreboard. Then **File → Save**."),
        ("code", "scoreboard()"),
        ("md", """### 📝 What you learned today
- **Control chart:** centre ± 3σ learned from a **quiet reference period**, not min/max or design limits.
- **One set of limits per operating state** (eclipse, recharge, sunlit). Never widen limits or delete data to silence false alarms.
- **3σ beats 2σ** on alarm fatigue: ~8 vs ~131 chance alarms in 2,880 hours.
- A **fixed** reference goes stale; **rolling, robust** limits (median + MAD × 1.4826) follow normal and ignore wild points.
- **Tampering** (reacting to common-cause wobble) makes things worse.
- **Residual = observed − expected.** Check it's clean: mean ≈ 0, no autocorrelation, constant spread.
- Residuals catch **spikes**; a rolling "expected" **swallows level shifts and slow drift**.

**Next time:** *The Slow Creep: Drift and CUSUM*. 🏠

<sub>Data: synthetic teaching datasets from the original Week 4 code book (`Time-series/week-04`). They are safe to use in AI assistants. Real NIGCOMSAT data is not.</sub>"""),
    ]
