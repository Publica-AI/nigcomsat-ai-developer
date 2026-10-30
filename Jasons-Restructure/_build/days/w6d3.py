"""Week 6 · Day 3: Project Clinic and Demo Day."""
from __future__ import annotations

import re
from functools import lru_cache

import numpy as np
import pandas as pd

import w5detector as W5
import w6forecast as W6
from common import BRAND as B, DAYS, ROOT, SUB, WEEK_TITLES
from w6forecast import BASELINE_CODE, FEATURE_CODE, H, mae, rate_past_errors, rate_seasonal_naive
from webdeck import logos_title_block

CODE = "W6D3"
TITLE = "Project Clinic and Demo Day"

GRID, AXIS = "#24384F", "#9DB0C6"
RED, GOLD, GREEN = "#FF6B6F", "#F5B83D", "#3CCB7F"
K_CHART = "Week 4 chart, lean features, steady sun"      # the W5D1 fair-fight keys in w5detector.facts()
K_FOREST = "Isolation forest, lean features, steady sun"
GAP_WEEK = "2025-03-10"        # the week Ada's export lost (its neighbours average to its true value)
DUP_WEEK = "2025-06-16"        # the week Ada's export repeated
SHUFFLE_SEED = 7
ADA_HALF = 3.0                 # Ada's "tidy" band: forecast plus or minus 3 tickets, called a 90% band
STAMP = "%Y-%m-%d"
CRON = "0 7 * * *"


def S(html, notes="", cls="", foot=True):
    return {"html": html, "notes": notes, "cls": cls, "foot": foot}


def _def(code: str, name: str) -> str:
    """One top-level function from a code string (so the notebook shows only what it uses)."""
    for block in re.split(r"\n(?=def )", code):
        if block.startswith(f"def {name}("):
            return block.rstrip()
    raise KeyError(name)


# =============================================================================
# NOTEBOOK CODE (the build runs these exact strings, so the checks match)
# =============================================================================
SELFCHECK_CODE = '''def hygiene(df, freq):
    """Stage 1 self-check: index, order, duplicates, gaps, declared frequency, time zone, empty cells."""
    idx = df.index
    is_dt = isinstance(idx, pd.DatetimeIndex)
    report = {"rows": len(df),
              "datetime index": is_dt,
              "sorted in time": bool(idx.is_monotonic_increasing),
              "duplicate timestamps": int(idx.duplicated().sum()),
              "missing timestamps": len(pd.date_range(idx.min(), idx.max(), freq=freq).difference(idx)) if is_dt else None,
              "frequency declared": idx.freqstr if is_dt and idx.freq is not None else None,
              "time zone": str(idx.tz) if is_dt and idx.tz is not None else "not stored: write it in your report",
              "empty cells": int(df.isna().sum().sum())}
    want = {"datetime index": True, "sorted in time": True, "duplicate timestamps": 0, "missing timestamps": 0, "empty cells": 0}
    for k, v in report.items():
        if k in want:
            mark = "✅" if v == want[k] else "⚠️"
        elif k == "frequency declared":
            mark = "✅" if v else "⚠️"
        else:
            mark = "  "
        print(f"{mark} {k:22s} {v}")
    return report

def leak_test(make_feature, df, target="tickets_raised", n_checks=12):
    """The leak test, done by the computer. For several weeks t: hide the target at t and EVERY row after t,
    rebuild the feature, and compare its value at t. If it changes, the feature used something you couldn't know."""
    full = make_feature(df)
    for t in np.linspace(len(df) // 4, len(df) - 2, n_checks).astype(int):
        hidden = df.astype(float)
        hidden.iloc[t + 1:] = np.nan
        hidden.iloc[t, hidden.columns.get_loc(target)] = np.nan
        a, b = full.iloc[t], make_feature(hidden).iloc[t]
        if not ((pd.isna(a) and pd.isna(b)) or (not pd.isna(b) and np.isclose(a, b))):
            return False
    return True

def check_temporal_split(train_index, test_index, embargo="0D"):
    """Stage 3 rule 1: every training timestamp comes BEFORE every test timestamp, with a gap longer than the embargo."""
    last_train, first_test = pd.Index(train_index).max(), pd.Index(test_index).min()
    assert last_train < first_test, (f"❌ not a split by time: training reaches {last_train:%d %b %Y} "
                                     f"but the test starts {first_test:%d %b %Y}")
    gap = first_test - last_train
    assert gap > pd.Timedelta(embargo), f"❌ embargo too short: the gap is {gap}, it must be more than {embargo}"
    print(f"✅ split by time: training ends {last_train:%d %b %Y}, the test starts {first_test:%d %b %Y}")
    return gap

def compare(actual, forecasts, scorer=None):
    """Stage 3 rule 2: every method on the SAME weeks, with the SAME scorer. Returns a table, best first."""
    scorer = scorer or mae
    scores = {}
    for name, f in forecasts.items():
        f = np.asarray(f, float)
        assert len(f) == len(actual), f"❌ {name} has {len(f)} forecasts but the test has {len(actual)} weeks: not the same period"
        scores[name] = scorer(f, actual)
    return pd.Series(scores, name=scorer.__name__).sort_values().to_frame()

def coverage(actual, lower, upper):
    """Share of the real values that landed inside the band. A 90% band should score about 0.9 on held-out data."""
    a = np.asarray(actual, float)
    return float(np.mean((a >= np.asarray(lower, float)) & (a <= np.asarray(upper, float))))

def recommendation(situation, observation, implication, action):
    """The 4-sentence recommendation for your unit head. The observation must carry a number."""
    parts = {"Situation": situation, "Observation": observation, "Implication": implication, "Recommendation": action}
    for k, v in parts.items():
        print(f"{k:>15}: {str(v).strip()}")
    return " ".join(str(v).strip().rstrip(".") + "." for v in parts.values())'''

REPORT_CODE = '''def write_report(df, stamp_format, out_dir="reports"):
    """A scheduled report: one dated chart + one dated summary for the week after the data ends.
    On the training server, cron runs this every morning, so nobody has to remember."""
    y, term = df["tickets_raised"], df["active_vsat_terminals"]
    forecast = rate_seasonal_naive(y, term, 1)[0]
    misses = rate_past_errors(df, len(df), h=1)
    half = float(np.quantile(np.abs(misses), 0.9))
    next_week = df.index[-1] + pd.Timedelta("7D")
    stamp = df.index[-1].strftime(stamp_format)
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    fig, ax = plt.subplots()
    ax.plot(y.index, y.values, label="tickets per week")
    ax.errorbar([next_week], [forecast], yerr=[[half], [half]], fmt="o", capsize=6, label="next week, 90% band")
    ax.set_title(f"Next week: about {forecast:.0f} tickets, plausibly {forecast - half:.0f} to {forecast + half:.0f}")
    ax.set_ylabel("tickets per week")
    ax.legend(loc="upper left")
    fig.tight_layout()
    png = out / f"ticket-report-{stamp}.png"
    fig.savefig(png, dpi=100)
    plt.close(fig)
    txt = out / f"ticket-report-{stamp}.txt"
    txt.write_text(f"Week of {next_week:%d %b %Y}: about {forecast:.0f} tickets, plausibly {forecast - half:.0f} "
                   f"to {forecast + half:.0f} (90% band from {len(misses)} past one-week forecasts). "
                   "Method: last year's tickets per terminal x this week's terminals.\\n", encoding="utf-8")
    return [str(png), str(txt)]'''

PLANT_CODE = '''def plant_problems(tickets):
    """Ada's export: the real weekly tickets with two problems planted, like a real NOC export."""
    draft = tickets.drop(pd.Timestamp("@@GAP@@"))                                   # one week never arrived
    draft = pd.concat([draft, draft.loc[[pd.Timestamp("@@DUP@@")]]]).sort_index()   # one week exported twice
    return draft'''.replace("@@GAP@@", GAP_WEEK).replace("@@DUP@@", DUP_WEEK)

SUSPECTS_CODE = '''SUSPECTS = {
    "last week: shift(1)": lambda d: d["tickets_raised"].shift(1),
    "same week last year: shift(52)": lambda d: d["tickets_raised"].shift(52),
    "terminals this week": lambda d: d["active_vsat_terminals"],
    "next week: shift(-1)": lambda d: d["tickets_raised"].shift(-1),
    "4-week mean, centred": lambda d: d["tickets_raised"].rolling(4, center=True).mean(),
    "4-week mean, including this week": lambda d: d["tickets_raised"].rolling(4).mean(),
}'''

TOOLS_CODE = "\n\n".join(_def(BASELINE_CODE, n) for n in ("naive", "seasonal_naive", "rate_seasonal_naive", "mae")) + \
    "\n\n" + _def(FEATURE_CODE, "rate_past_errors")

exec(SELFCHECK_CODE)
exec(PLANT_CODE)
exec(SUSPECTS_CODE)


# =============================================================================
# NUMBERS FOR TODAY (same code as the notebook)
# =============================================================================
@lru_cache(maxsize=1)
def day_facts():
    from pathlib import Path
    import tempfile
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: F401  (write_report needs it in scope)

    F6, F5 = W6.facts(), W5.facts()
    D = {"F6": F6, "F5": F5}
    raw = pd.read_csv(W6.D6 / "ops_tickets_weekly.csv", parse_dates=["week_start"], index_col="week_start")
    tickets = raw.asfreq("W-MON")
    draft = plant_problems(raw)
    D["draft_rows"] = len(draft)
    D["n_dup"] = int(draft.index.duplicated().sum())
    D["n_missing"] = len(pd.date_range(draft.index.min(), draft.index.max(), freq="W-MON").difference(draft.index))
    clean = draft[~draft.index.duplicated(keep="first")].sort_index().asfreq("W-MON").interpolate()
    assert np.allclose(clean.values, tickets.values), "interpolating the lost week must restore the real value"
    D["gap_value"] = float(clean.loc[GAP_WEEK, "tickets_raised"])
    D["gap_neighbours"] = (int(tickets["tickets_raised"].shift(1).loc[GAP_WEEK]), int(tickets["tickets_raised"].shift(-1).loc[GAP_WEEK]))
    D["clean_rows"] = len(clean)
    # leak test on the suspects (real file)
    D["suspects"] = {name: leak_test(fn, clean) for name, fn in SUSPECTS.items()}
    D["fixed_feature_ok"] = leak_test(lambda d: d["tickets_raised"].rolling(4).mean().shift(1), clean)
    # Ada's shuffled split vs the split by time
    shuffled = clean.sample(frac=1, random_state=SHUFFLE_SEED)
    ada_train, ada_test = shuffled.iloc[:-H], shuffled.iloc[-H:]
    D["ada_split"] = (ada_train.index.max(), ada_test.index.min())
    cut = clean.index[-H]
    train, test = clean[clean.index < cut], clean[clean.index >= cut]
    D["cut"] = cut
    D["n_train"], D["n_test"] = len(train), len(test)
    ty, tt = train["tickets_raised"], train["active_vsat_terminals"]
    test_y = test["tickets_raised"]
    table = compare(test_y, {"naive": W6.naive(ty, H), "seasonal naive": W6.seasonal_naive(ty, H),
                             "rate seasonal naive": rate_seasonal_naive(ty, tt, H)})
    D["table"] = table
    D["best"] = table.index[0]
    D["best_mae"] = float(table.iloc[0, 0])
    fc = rate_seasonal_naive(ty, tt, H)
    D["ada_cov"] = coverage(test_y, fc - ADA_HALF, fc + ADA_HALF)
    past = rate_past_errors(clean, len(train), h=H)
    D["half"] = float(np.quantile(np.abs(past), 0.9))
    D["honest_cov"] = coverage(test_y, fc - D["half"], fc + D["half"])
    D["n_past"] = len(past)
    # the scheduled report, run once into a temp folder
    g = dict(globals())
    g.update({"Path": Path, "plt": plt, "rate_past_errors": rate_past_errors, "rate_seasonal_naive": rate_seasonal_naive})
    exec(REPORT_CODE, g)
    with tempfile.TemporaryDirectory() as tmp:
        png, txt = g["write_report"](clean, STAMP, out_dir=tmp)
        D["report_text"] = Path(txt).read_text(encoding="utf-8").strip()
        D["report_names"] = (Path(png).name, Path(txt).name)
    D["report_fc"] = float(rate_seasonal_naive(clean["tickets_raised"], clean["active_vsat_terminals"], 1)[0])
    D["report_stamp"] = clean.index[-1].strftime(STAMP)
    # the course's own verdicts, for the worked examples
    hz = F6["horizons"]
    D["h8_rate"], D["h8_naive"], D["h8_n"] = hz[8]["mean"]["rate_seasonal_naive"], hz[8]["mean"]["naive"], hz[8]["n"]
    D["h1_rate"], D["h1_naive"], D["h1_n"] = hz[1]["mean"]["rate_seasonal_naive"], hz[1]["mean"]["naive"], hz[1]["n"]
    D["fold_reg"], D["fold_naive"], D["naive_wins"] = F6["fold_means"]["regression"], F6["fold_means"]["naive"], F6["naive_beats_reg"]
    D["n_folds"] = len(F6["folds"])
    bc = F6["battery_cross"]
    D["bat_first"], D["bat_last"], D["bat_30"] = bc["first_dip"], bc["last_good_day"], bc["30_day_mean"]
    D["bat_window_days"] = F6["battery_window_days"]
    rep = F6["battery_repeat"].set_index("years_of_data")
    D["bat_call3"] = rep.loc[3, "predicted_crossing"]
    D["bat_err3"] = int(rep.loc[3, "days_vs_first_dip"])
    D["bat_warn3"] = int(rep.loc[3, "warning_days"])
    fight = F5["fight"]
    D["chart"], D["forest"] = fight[K_CHART], fight[K_FOREST]
    return D


def rubric():
    """The 100-point rubric, read from the final-project requirements so the two can never disagree."""
    md = (ROOT / "week-6" / "final-project" / "Final-Project-Requirements.md").read_text(encoding="utf-8")
    sec = md.split("## 6. How it's graded")[1].split("\n## ")[0]
    rows = []
    for line in sec.splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*\*\*(\d+)\*\*\s*\|", line)
        if m:
            rows.append((m.group(1), m.group(2), int(m.group(3))))
    assert sum(r[2] for r in rows) == 100, rows
    return rows


def _d(t):
    return f"{pd.Timestamp(t).day} {pd.Timestamp(t):%b %Y}"


# =============================================================================
# LOCAL SVG / HTML HELPERS
# =============================================================================
SHORT = {"W1D1": "Colab + first series", "W1D2": "Charts that don't lie", "W1D3": "Rolling windows",
         "W2D1": "Trend · season · noise", "W2D2": "Autocorrelation", "W2D3": "Quiz 1 + your brief",
         "W3D1": "Alarms that cry wolf", "W3D2": "Control charts", "W3D3": "Drift + CUSUM",
         "W4D1": "Scoring + Quiz 2", "W4D2": "Isolation forest", "W4D3": "Feature engineering",
         "W5D1": "No expo + Quiz 3", "W5D2": "Baselines", "W5D3": "Regression + ranges",
         "W6D1": "Backtesting", "W6D2": "RUL + Quiz 4", "W6D3": "Demo day 🎤"}
assert set(SHORT) == {d.code for d in DAYS}
WEEK_Q = {1: ("🔎", "What does this series look like?"), 2: ("🧩", "What is it made of?"),
          3: ("🚨", "When is a reading wrong?"), 4: ("🎯", "Can a machine spot the odd one?"),
          5: ("⚖️", "Is the test honest? What comes next?"), 6: ("🔮", "When will it break? Show us!")}
STAGES = [("🎯", "Choose", "brief + unit head's OK", "Week 2 · Day 3"),
          ("📥", "Understand", "load, profile, plot", "Week 3 · Day 3"),
          ("🛠️", "Build", "your method", "Week 4 · Day 3"),
          ("⚖️", "Test honestly", "split by time + baseline", "Week 5 · Day 3"),
          ("🚀", "Deploy", "on the training server", "by today"),
          ("🎤", "Present", "report + 5-minute demo", "TODAY")]
DEMO = [("Problem", "unit · named process · who uses it", 45, B["blue_d"]),
        ("Data", "source · span · cadence · what you fixed", 45, B["teal_d"]),
        ("Method", "what, and why it suits the brief", 45, "#7A6CF0"),
        ("Honest test", "split by time · baseline · the table", 60, GOLD),
        ("The tool, live", "dashboard or today's report", 60, GREEN),
        ("Recommend", "4 sentences + one limitation", 45, RED)]
assert sum(s for _, _, s, _ in DEMO) == 300
STATIONS = [("🔎", "Data & leaks", "hygiene report · leak_test() on every feature · the time zone written down"),
            ("⚖️", "Honest test", "split assert · same period, same scorer · spread or coverage reported"),
            ("🚀", "Deployment", "runs on the training server · README · cron or Streamlit · no raw data in Git"),
            ("🗣️", "The story", "4 sentences · 3 limitations · a timed 5-minute run-through")]
TRAPS = [("🎲", "A random split", "shuffled weeks or hours: the score is expo"),
         ("🙈", "No baseline", "“my model scores 4.0”… compared with what?"),
         ("📏", "A band never checked", "“90%” with no coverage on held-out data"),
         ("🎯", "Accuracy for rare events", "99% by never raising an alarm: use event-level recall"),
         ("☁️", "Real data in Colab or AI", "real NIGCOMSAT data stays on NIGCOMSAT systems"),
         ("💻", "Laptop-only tool", "if it doesn't run on the server, it isn't deployed")]
TRAP_SHORT = {"A random split": "Random split", "No baseline": "No baseline", "A band never checked": "Unchecked band",
              "Accuracy for rare events": "Accuracy", "Real data in Colab or AI": "Real data out", "Laptop-only tool": "Laptop only"}


def journey_html():
    cols = []
    for w in range(1, 7):
        icon, q = WEEK_Q[w]
        chips = "".join(f'<div style="background:#0B1622;border:1px solid #24384F;border-radius:12px;padding:6px 8px;font-size:17px;'
                        f'margin-top:7px;{"border-color:#F5B83D;color:#FFE3A3;font-weight:800" if d.code == CODE else "color:#C9D6E5"}">'
                        f'{SHORT[d.code]}</div>' for d in DAYS if d.week == w)
        hot = w == 6
        cols.append(f'<div class="card anim a-pop{" glow" if hot else ""}" style="--d:{.3 + (w - 1) * .22:.2f}s;padding:20px 16px;text-align:center'
                    f'{";border-color:#F5B83D" if hot else ""}"><div style="font-size:54px;line-height:1">{icon}</div>'
                    f'<div class="small" style="margin-top:8px;letter-spacing:.12em;text-transform:uppercase">Week {w}</div>'
                    f'<p style="font-size:22px;line-height:1.25;font-weight:800;margin-top:6px;min-height:84px">{q}</p>{chips}</div>')
    road = ('<svg viewBox="0 0 1420 40" width="100%" style="display:block;margin-top:14px"><path class="draw" style="--d:.2s;--dur:2.4s" '
            'd="M20 20 L1400 20" stroke="#3B8BE0" stroke-width="6" stroke-linecap="round"/>'
            '<text x="1400" y="34" fill="#F5B83D" font-size="30" text-anchor="end">🏁</text></svg>')
    return (f'<div style="display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:16px;margin-top:6px">{"".join(cols)}</div>{road}'
            '<p class="anim" style="--d:1.8s;margin-top:18px;text-align:center">Every project uses pieces from <b class="hl">at least three</b> of these weeks.</p>')


def stages_html():
    cells = []
    for k, (icon, name, what, when) in enumerate(STAGES):
        today = when == "TODAY"
        tick = "🎤 TODAY" if today else ("✅ " + when if when.startswith("Week") else when)
        cells.append(f'<div class="card anim a-pop{" glow" if today else ""}" style="--d:{.3 + k * .2:.2f}s;padding:22px 14px;text-align:center'
                     f'{";border-color:#F5B83D" if today else ""}"><div style="font-size:56px;line-height:1">{icon}</div>'
                     f'<div class="small" style="margin-top:6px">Stage {k}</div><h3 style="font-size:28px;margin:4px 0 6px">{name}</h3>'
                     f'<p class="muted" style="font-size:20px;line-height:1.3;min-height:54px">{what}</p>'
                     f'<span class="pill {"gold" if today else "teal"}" style="font-size:17px;padding:5px 12px;margin:10px 0 0">{tick}</span></div>')
    return f'<div style="display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:16px;margin-top:20px">{"".join(cells)}</div>'


RUBRIC_SHORT = {"Problem framing and data": "named process · agreement · real data",
                "Understanding the series": "clean index · honest chart · season",
                "Method": "suits the brief · leak-free",
                "Honest evaluation": "split by time · same scorer · spread",
                "Deployment": "runs on the training server",
                "Communication and AI use": "4 sentences · limits · on time"}


def rubric_html():
    rows = rubric()
    assert set(RUBRIC_SHORT) == {r[0] for r in rows}, "rubric names changed: update RUBRIC_SHORT"
    out = []
    for k, (name, _, pts) in enumerate(rows):
        hot = pts == max(p for _, _, p in rows)
        col = GOLD if hot else B["blue_d"]
        out.append(f'<div class="anim a-left" style="--d:{.3 + k * .18:.2f}s;display:grid;grid-template-columns:400px 1fr 80px;gap:20px;align-items:center;margin:11px 0">'
                   f'<div style="font-size:25px;font-weight:800;text-align:right;white-space:nowrap">{name}</div>'
                   f'<div style="background:#0B1622;border-radius:14px;height:50px">'
                   f'<div style="width:{pts * 4}%;height:100%;background:{col};border-radius:14px;display:flex;align-items:center;padding-left:18px;'
                   f'font-size:20px;font-weight:700;color:#0B1622;white-space:nowrap;overflow:hidden">{RUBRIC_SHORT[name]}</div></div>'
                   f'<div class="mono" style="font-size:34px;font-weight:800;color:{col}">{pts}</div></div>')
    return "".join(out)


def demo_html():
    """The six beats as columns whose widths are their seconds."""
    cols, t = [], 0
    for k, (name, what, sec, col) in enumerate(DEMO):
        d = .3 + k * .25
        cols.append(f'<div class="anim a-left" style="--d:{d:.2f}s"><div class="mono" style="font-size:20px;color:{AXIS};font-weight:700">{t // 60}:{t % 60:02d}</div>'
                    f'<div style="background:{col};border-radius:16px;height:76px;display:flex;align-items:center;justify-content:center;margin-top:8px;'
                    f'font-size:24px;font-weight:800;color:#0B1622;text-align:center;line-height:1.1;padding:0 6px">{name}</div>'
                    f'<p style="font-size:19px;line-height:1.3;color:#EAF2FB;text-align:center;margin-top:12px">{what}</p>'
                    f'<p class="small" style="font-size:18px;text-align:center;margin-top:4px">{sec} s</p></div>')
        t += sec
    widths = " ".join(f"{sec}fr" for _, _, sec, _ in DEMO)
    return (f'<div style="display:grid;grid-template-columns:{widths};gap:10px">{"".join(cols)}</div>'
            f'<div class="mono" style="text-align:right;color:{GOLD};font-size:20px;font-weight:800;margin-top:-4px">5:00 ⏰</div>')


def leak_svg(w=1420, h=200):
    """Weeks as boxes: the past stays, week t's answer and everything after are hidden."""
    n, L = 16, 20
    bw = (w - 2 * L) / n
    t = 10
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" style="display:block">']
    for i in range(n):
        x = L + i * bw
        col = B["blue_d"] if i < t else ("#C77700" if i == t else "#24384F")
        d = .2 + i * .05
        o.append(f'<rect class="anim a-pop" style="--d:{d:.2f}s;transform-origin:{x + bw / 2:.0f}px 85px" x="{x + 4:.1f}" y="50" '
                 f'width="{bw - 8:.1f}" height="70" rx="12" fill="{col}"/>')
        if i >= t:
            o.append(f'<text class="anim a-fade" style="--d:{1.2 + (i - t) * .05:.2f}s" x="{x + bw / 2:.1f}" y="97" fill="#EAF2FB" '
                     f'font-size="28" text-anchor="middle">{"?" if i == t else "🙈"}</text>')
    xt = L + t * bw + bw / 2
    o.append(f'<text x="{L + t * bw / 2:.1f}" y="160" fill="#BFDcff" font-size="22" font-weight="700" text-anchor="middle">what you knew: stays</text>')
    o.append(f'<text x="{xt:.1f}" y="35" fill="{GOLD}" font-size="22" font-weight="800" text-anchor="middle">week t</text>')
    o.append(f'<text class="anim a-fade" style="--d:1.6s" x="{(xt + w - L) / 2 + 20:.1f}" y="160" fill="{AXIS}" font-size="22" font-weight="700" '
             f'text-anchor="middle">this week\'s answer + the future: hidden</text>')
    o.append("</svg>")
    return "".join(o)


def _sentences():
    """The worked 4-sentence recommendation for the ticket forecast, built from the backtest numbers."""
    D = day_facts()
    return ("The NOC sets its month-ahead duty roster from last week's ticket count.",
            f"Backtested from {D['h8_n']} starting weeks, last year's tickets per terminal times this week's network missed by "
            f"{D['h8_rate']:.1f} tickets a week, 8 weeks ahead, against {D['h8_naive']:.1f} for “same as last week”.",
            "A roster built on the rate forecast would be about half as far off, at no extra cost.",
            "Use the rate forecast for the monthly roster, keep “same as last week” for next week, and re-run the backtest every quarter.")


def _limits():
    D = day_facts()
    return ("Sudden changes the calendar can't know about, such as a new region going live or a long outage.",
            f"It looks 1 to 8 weeks ahead; its 90% band is about ±{D['half']:.0f} tickets a week.",
            "It assumes the 2024–2025 rainy-season pattern repeats and that the terminal count is reported on time.")


# =============================================================================
# WEB SLIDES (animated)
# =============================================================================
def web_slides():
    D = day_facts()
    s1, s2, s3, s4 = _sentences()
    rows = rubric()
    honest_pts = max(p for _, _, p in rows)
    ch, fo = D["chart"], D["forest"]
    sus = D["suspects"]
    sus_rows = "".join(
        f'<div class="anim a-left" style="--d:{1.2 + k * .15:.2f}s;display:flex;justify-content:space-between;align-items:center;'
        f'background:#0B1622;border-radius:14px;padding:9px 18px;margin:7px 0"><span class="mono" style="font-size:21px">{name}</span>'
        f'<b style="font-size:21px;color:{GREEN if ok else RED}">{"✅ honest" if ok else "🚨 leaks"}</b></div>'
        for k, (name, ok) in enumerate(sus.items()))
    stations = "".join(
        f'<div class="card anim a-pop" style="--d:{.3 + k * .2:.2f}s;padding:28px 24px;text-align:center"><div class="icon">{i}</div>'
        f'<span class="num" style="margin:0 auto 10px">{k + 1}</span><h3 style="font-size:30px">{n}</h3><p class="muted" style="font-size:21px;line-height:1.35">{w}</p></div>'
        for k, (i, n, w) in enumerate(STATIONS))
    traps = "".join(f'<div class="row anim a-right" style="--d:{.5 + k * .15:.2f}s;gap:14px;align-items:center;margin:8px 0">'
                    f'<span style="font-size:36px">{i}</span><p style="font-size:22px;line-height:1.3"><b>{n}:</b> <span class="muted">{w}</span></p></div>'
                    for k, (i, n, w) in enumerate(TRAPS))
    split_last, split_first = D["ada_split"]
    sentences = "".join(
        f'<div class="card anim a-left" style="--d:{.3 + k * .3:.2f}s;display:grid;grid-template-columns:330px 1fr;gap:20px;align-items:center;padding:18px 26px;margin:10px 0">'
        f'<div style="display:flex;align-items:center;gap:14px;white-space:nowrap"><span class="num" style="background:{c}">{k + 1}</span><b style="font-size:26px">{lab}</b></div>'
        f'<p style="font-size:24px;line-height:1.35">{txt}</p></div>'
        for k, (lab, c, txt) in enumerate((("Situation", B["blue_d"], s1), ("Observation", GOLD, s2), ("Implication", B["teal_d"], s3), ("Recommendation", RED, s4))))

    slides = [
        # 1 ─ title
        S(f"""
<div style="position:absolute;right:80px;top:130px;width:520px;height:600px">
  <svg viewBox="0 0 520 600" width="520" height="600">
    <circle cx="260" cy="300" r="230" fill="none" stroke="#3B8BE0" stroke-width="3" stroke-dasharray="10 12" class="spin" style="--t:40s;transform-origin:260px 300px"/>
    <g class="anim a-pop" style="--d:.3s;transform-origin:260px 260px">
      <rect x="205" y="120" width="110" height="190" rx="55" fill="#C9D6E5"/>
      <rect x="215" y="130" width="90" height="170" rx="45" fill="#9DB0C6"/>
      <line x1="215" y1="180" x2="305" y2="180" stroke="#7F93AA" stroke-width="4"/><line x1="215" y1="215" x2="305" y2="215" stroke="#7F93AA" stroke-width="4"/>
      <line x1="215" y1="250" x2="305" y2="250" stroke="#7F93AA" stroke-width="4"/>
      <path d="M180 270 Q180 360 260 360 Q340 360 340 270" fill="none" stroke="#EAF2FB" stroke-width="10" stroke-linecap="round"/>
      <rect x="252" y="360" width="16" height="90" fill="#EAF2FB"/><rect x="200" y="450" width="120" height="16" rx="8" fill="#EAF2FB"/>
    </g>
    <g class="anim a-fade" style="--d:.9s">
      <rect x="70" y="90" width="22" height="10" rx="3" fill="#F5B83D" transform="rotate(30 80 95)"/><rect x="420" y="120" width="22" height="10" rx="3" fill="#3CCB7F" transform="rotate(-25 430 125)"/>
      <rect x="100" y="420" width="22" height="10" rx="3" fill="#FF6B6F" transform="rotate(60 110 425)"/><rect x="410" y="430" width="22" height="10" rx="3" fill="#3B8BE0" transform="rotate(-50 420 435)"/>
      <circle cx="140" cy="170" r="8" fill="#16A394"/><circle cx="390" cy="230" r="8" fill="#F5B83D"/><circle cx="380" cy="520" r="8" fill="#FF6B6F"/>
    </g>
  </svg></div>
<div style="max-width:900px;margin-top:40px">
  <div class="kicker anim">Week 6 · Day 3 · the last session</div>
  <h1 class="anim" style="--d:.2s">Demo Day 🎤<br><span class="hl">+ Project Clinic</span></h1>
  <p class="sub anim" style="--d:.5s;margin-top:28px">Six weeks. One tool for your unit. Five minutes to show it.</p>
  <div class="anim" style="--d:.8s;margin-top:40px;display:flex">{logos_title_block()}</div>
</div>""",
          "Welcome to the last day. Make it feel like an occasion: music while people arrive, unit heads welcomed by name. "
          "Today nobody learns a new method. Today everybody shows what they built."),

        # 2 ─ mission
        S("""
<div class="kicker anim">Today's plan · 2 hours</div>
<h2 class="anim" style="--d:.1s">Fix it. Show it. Celebrate it.</h2>
<div class="flow" style="margin-top:60px">
  <div class="box on anim a-pop" style="--d:.3s;min-width:270px;padding:40px 22px"><div class="icon">👋🏾</div><h3>Welcome</h3><p class="small">the order of demos</p></div>
  <div class="arrow anim a-fade" style="--d:.5s"></div>
  <div class="box on anim a-pop" style="--d:.7s;min-width:270px;padding:40px 22px"><div class="icon">🩺</div><h3>Clinic</h3><p class="small">4 help stations</p></div>
  <div class="arrow anim a-fade" style="--d:.9s"></div>
  <div class="box on anim a-pop" style="--d:1.1s;min-width:270px;padding:40px 22px"><div class="icon">🎤</div><h3>Demos</h3><p class="small">5 minutes + 1 question</p></div>
  <div class="arrow anim a-fade" style="--d:1.3s"></div>
  <div class="box on anim a-pop" style="--d:1.5s;min-width:270px;padding:40px 22px"><div class="icon">🎉</div><h3>Celebrate</h3><p class="small">certificates + what next</p></div>
</div>
<div class="row anim" style="--d:1.8s;margin-top:60px;gap:18px">
  <span class="pill">⏱️ 10 min welcome</span><span class="pill teal">🩺 30 min clinic</span><span class="pill gold">🎤 60 min demos</span><span class="pill">🎉 20 min wrap-up</span>
</div>""",
          "Four blocks. If the cohort is bigger than 10, split the demos into two rooms (see the instructor notes) so everybody presents inside the hour."),

        # 3 ─ hook
        S("""
<div class="kicker anim">Two people you already know</div>
<h2 class="anim" style="--d:.1s">The MC and the uncle 🎉</h2>
<div class="grid2" style="margin-top:24px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🎤</div><h3>The owambe MC</h3>
    <p class="muted">“Groom's friends, <b style="color:#fff">five minutes</b>! After that, the DJ takes the floor.” And he means it: the music starts on time.</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill gold">keeps to time</span></div></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">👴🏾</div><h3>The uncle in the front row</h3>
    <p class="muted">“Ehen, my son. Tell us in <b style="color:#fff">one sentence</b>: what does it do, and why should we care?”</p>
    <div class="row" style="gap:12px;margin-top:16px"><span class="pill teal">wants the point</span></div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:36px;text-align:center">Today you satisfy both: <b class="hl">five minutes</b>, and a point your unit head can repeat.</p>""",
          "Get a laugh: everyone has met both. Then land it: the timer is the MC, and the unit head is the uncle. A demo that runs over or never says the point loses both of them."),

        # 4 ─ journey
        S(f"""
<div class="kicker anim">Look how far you've come</div>
<h2 class="anim" style="--d:.1s;font-size:54px">18 days in one picture 🛣️</h2>
{journey_html()}""",
          "Walk the road in 60 seconds. Week 1: read a series. Week 2: take it apart. Week 3: spot a wrong reading. Week 4: score detectors and meet machine learning. "
          "Week 5: honest tests and the first forecasts. Week 6: backtesting, remaining life, and today. Every project uses pieces from at least three of these weeks."),

        # 5 ─ stages
        S(f"""
<div class="kicker anim">The final project, stage by stage</div>
<h2 class="anim" style="--d:.1s;font-size:54px">Four checkpoints done. Today is the fifth.</h2>
{stages_html()}
<p class="anim" style="--d:1.8s;margin-top:34px;text-align:center">Today you bring: a <b class="hl">working tool</b>, the <b class="hl">2–4 page report</b> and a <b class="hl">5-minute demo</b>.</p>""",
          "These are the stages from the requirements PDF and the checkpoints from Weeks 2 to 5. If somebody missed a checkpoint, the clinic is where it gets fixed."),

        # 6 ─ rubric
        S(f"""
<div class="kicker anim">How it's graded · 100 points</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The biggest slice is honesty ⚖️</h2>
<div style="margin-top:12px">{rubric_html()}</div>
<p class="anim" style="--d:1.6s;margin-top:20px;text-align:center">No model has to win. <b class="hl">The test has to be honest</b> ({honest_pts} of 100 points).</p>""",
          "The rubric comes straight from the requirements PDF (and the original Publica brief). Honest evaluation is the biggest single criterion. "
          "A model that loses to the baseline can still score full marks there, if the comparison is fair and the report recommends the simpler method."),

        # 7 ─ penalties
        S("""
<div class="kicker anim">Read this twice</div>
<h2 class="anim" style="--d:.1s">What costs marks, and what doesn't</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s;border-color:#E5484D"><div class="icon">🚫</div><h3>Automatic penalties</h3>
    <p class="muted" style="font-size:24px;line-height:1.5">a random train/test split<br>a feature that uses the future<br>an accuracy figure for rare events<br>
    a remaining-life date with no window<br><b style="color:#FFC2C4">real data committed to GitHub</b></p></div>
  <div class="card anim a-right" style="--d:.6s;border-color:#16A394"><div class="icon">✅</div><h3>Not penalised</h3>
    <p class="muted" style="font-size:24px;line-height:1.5">a model that <b style="color:#fff">loses</b> to the simple baseline,<br>as long as the comparison is fair<br>
    and you <b class="hl">recommend the simpler method</b>.</p>
    <p class="small" style="margin-top:16px">We did exactly that in W5D1 and W6D1.</p></div>
</div>""",
          "These five penalties are in the requirements PDF and the original grading notes. Committed restricted data is treated as a serious failure and reported to the programme lead. "
          "Say the right-hand card slowly: recommending against your own model is a respected result."),

        # 8 ─ section: clinic
        S("""
<div class="kicker anim">Part 1 · 30 minutes</div>
<h1 class="anim" style="--d:.15s">The clinic 🩺</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">Last fixes before the stage. Go where you need help most.</p>""",
          "Section break.", cls="center"),

        # 9 ─ stations
        S(f"""
<div class="kicker anim">Four help stations · pick the ONE you need</div>
<h2 class="anim" style="--d:.1s">Clinic stations</h2>
<div class="grid4" style="margin-top:14px">{stations}</div>
<p class="anim" style="--d:1.3s;margin-top:28px;text-align:center">15 minutes at a station, then <b class="hl">rotate</b> or rehearse with a partner. Bring your laptop and your report.</p>""",
          "Put a sign on four tables. You (or a strong participant) staff each one. Station 1 runs the hygiene report and the leak test on their features. "
          "Station 2 checks the split assert and the comparison table. Station 3 checks it really runs on the training server. Station 4 times a run-through and reads the 4 sentences."),

        # 10 ─ self-check notebook
        S("""
<div class="kicker anim">Let the computer be your reviewer</div>
<h2 class="anim" style="--d:.1s;font-size:56px">The self-check notebook 🧑🏾‍⚕️</h2>
<div class="grid3" style="margin-top:14px;gap:22px">
  <div class="card anim a-pop" style="--d:.3s;padding:24px 26px"><h3 class="mono" style="font-size:26px">hygiene()</h3><p class="muted" style="font-size:22px">index · order · repeats · holes · frequency · time zone</p></div>
  <div class="card anim a-pop" style="--d:.45s;padding:24px 26px"><h3 class="mono" style="font-size:26px">leak_test()</h3><p class="muted" style="font-size:22px">hide the future, rebuild the feature: did it change?</p></div>
  <div class="card anim a-pop" style="--d:.6s;padding:24px 26px"><h3 class="mono" style="font-size:26px">check_temporal_split()</h3><p class="muted" style="font-size:22px">train before test, with the embargo, or it fails loudly</p></div>
  <div class="card anim a-pop" style="--d:.75s;padding:24px 26px"><h3 class="mono" style="font-size:26px">compare()</h3><p class="muted" style="font-size:22px">every method, same weeks, same scorer, best first</p></div>
  <div class="card anim a-pop" style="--d:.9s;padding:24px 26px"><h3 class="mono" style="font-size:26px">coverage()</h3><p class="muted" style="font-size:22px">did the 90% band catch about 90% of held-out weeks?</p></div>
  <div class="card anim a-pop" style="--d:1.05s;padding:24px 26px"><h3 class="mono" style="font-size:26px">recommendation()</h3><p class="muted" style="font-size:22px">4 sentences, one number, one action</p></div>
</div>
<p class="anim" style="--d:1.4s;margin-top:26px;text-align:center">Rehearse on Colab with course data. Then <b class="hl">download it</b> and run it on the training server with your real data.</p>""",
          "Today's notebook is a reviewer, not a lesson. Parts A to D rehearse on a synthetic export with planted problems. Part E is for their own data, on the training server only. "
          "Remind the room: real NIGCOMSAT data never goes into Colab."),

        # 11 ─ leak test
        S(f"""
<div class="kicker anim">The leak test, done by the computer</div>
<h2 class="anim" style="--d:.1s;font-size:52px">Hide the future. Did the feature change? 🙈</h2>
<div class="card anim" style="--d:.2s;padding:12px 24px">{leak_svg()}</div>
<div class="row" style="gap:36px;margin-top:16px;align-items:center">
  <p class="anim" style="--d:.9s;flex:.8;font-size:26px">For several weeks <b class="hl">t</b>: blank out week t's answer and every row after it, rebuild the feature, compare. If the value moved, the feature <b class="bad">needed something you couldn't know</b>.</p>
  <div style="flex:1.2">{sus_rows}</div>
</div>""",
          "This automates the question from W4D3 and W5D3: could I have computed this at the moment the forecast was needed? Six suspects on the real ticket file. "
          "shift(1), shift(52) and this week's terminal count pass. shift(-1), a centred window, and a window that includes this week all leak. "
          "The last one is sneaky: it contains the very number you're forecasting."),

        # 12 ─ Ada's draft
        S(f"""
<div class="kicker anim">Rehearsal · Ada's draft project</div>
<h2 class="anim" style="--d:.1s;font-size:54px">What the self-check found 🔎</h2>
<div class="grid4" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center;padding:26px 18px"><div class="icon">👯🏾</div><div class="stat hl" style="font-size:88px">{D["n_dup"]}</div><div class="stat-label">week exported twice</div></div>
  <div class="card anim a-pop" style="--d:.5s;text-align:center;padding:26px 18px"><div class="icon">🕳️</div><div class="stat hl" style="font-size:88px">{D["n_missing"]}</div><div class="stat-label">week that never arrived</div></div>
  <div class="card anim a-pop" style="--d:.7s;text-align:center;padding:26px 18px"><div class="icon">🎲</div><div class="stat bad" style="font-size:60px;line-height:1.5">shuffled</div>
    <div class="stat-label">training reaches {_d(split_last)}, the test starts {_d(split_first)}</div></div>
  <div class="card anim a-pop" style="--d:.9s;text-align:center;padding:26px 18px"><div class="icon">📏</div><div class="stat bad" style="font-size:88px">{D["ada_cov"] * H:.0f}/{H}</div>
    <div class="stat-label">weeks inside her “90%” band (±{ADA_HALF:.0f})</div></div>
</div>
<p class="sub step" data-step="1" style="margin-top:30px;text-align:center;font-size:30px">Fixed: fill the gap, split by time, band from <b class="hl">honest past misses</b> (±{D["half"]:.1f}): {D["honest_cov"] * H:.0f}/{H}.</p>""",
          f"Ada is a made-up colleague; her export is the real ops_tickets_weekly file with two planted problems. The hygiene report finds the repeated week ({DUP_WEEK}) and the lost one ({GAP_WEEK}). "
          f"Her random split fails the assert. Her ±{ADA_HALF:.0f} band, called 90%, caught {D['ada_cov'] * H:.0f} of {H} test weeks. The band from {D['n_past']} honest past misses (W5D3's recipe) caught {D['honest_cov'] * H:.0f} of {H}. "
          "Participants do exactly these fixes in Parts A and B of the notebook."),

        # 13 ─ section: demos
        S("""
<div class="kicker anim">Part 2 · 60 minutes</div>
<h1 class="anim" style="--d:.15s">Demo time 🎤</h1>
<p class="sub anim" style="--d:.35s;margin-top:24px">5 minutes to show it. 1 minute for one question. The timer is the MC.</p>""",
          "Section break. Put the timer on the big screen or a phone the presenter can see.", cls="center"),

        # 14 ─ demo template
        S(f"""
<div class="kicker anim">The 5-minute demo, second by second</div>
<h2 class="anim" style="--d:.1s;font-size:56px">Six beats. No slide is longer than its beat. ⏱️</h2>
<div class="card anim" style="--d:.2s;padding:24px 22px;margin-top:10px">{demo_html()}</div>
<div class="grid3" style="margin-top:22px;gap:22px">
  <div class="card anim a-pop" style="--d:1.9s;padding:18px 22px"><p style="font-size:23px">🧪 <b>Show the tool live</b>, not a screenshot. Have the screenshot as backup.</p></div>
  <div class="card anim a-pop" style="--d:2.1s;padding:18px 22px"><p style="font-size:23px">📊 <b>One table</b> for the honest test: your method vs the baseline, same period.</p></div>
  <div class="card anim a-pop" style="--d:2.3s;padding:18px 22px"><p style="font-size:23px">🗣️ <b>End on the recommendation</b>, not on “any questions?”</p></div>
</div>""",
          "The template adds up to exactly 5:00. The honest test and the live tool get the most time because they carry the most marks (honest evaluation and deployment). "
          "Tell them to rehearse it once with a partner during the clinic, with a timer."),

        # 15 ─ 4 sentences
        S(f"""
<div class="kicker anim">The last 45 seconds · the uncle's question</div>
<h2 class="anim" style="--d:.1s;font-size:54px">The 4-sentence recommendation 🗣️</h2>
{sentences}""",
          "The worked example uses the real backtest from Week 6 Day 1, so every number is from the data. Situation: what the unit does today. Observation: one number from the evaluation. "
          "Implication: what it means for operations. Recommendation: what to do, with which tool."),

        # 16 ─ two more worked examples
        S(f"""
<div class="kicker anim">Two more observations from this course</div>
<h2 class="anim" style="--d:.1s;font-size:54px">One number, said plainly 🔢</h2>
<div class="grid2" style="margin-top:20px">
  <div class="card anim a-left" style="--d:.3s"><div class="icon">🔋</div><h3>Battery (W6D2)</h3>
    <p style="font-size:24px;line-height:1.4">“Daily capacity first dipped below 80% on <b class="hl">{_d(D["bat_first"])}</b> and was last at or above it on <b class="hl">{_d(D["bat_last"])}</b>:
    a {D["bat_window_days"]}-day crossing window. A straight line on three years of data called <b>{_d(D["bat_call3"])}</b>, {abs(D["bat_err3"])} days before the first dip.”</p></div>
  <div class="card anim a-right" style="--d:.6s"><div class="icon">🛰️</div><h3>Detector (W5D1)</h3>
    <p style="font-size:24px;line-height:1.4">“On the held-out months both detectors caught <b class="hl">{ch["caught"]} of {ch["events"]}</b> events. The control chart raised
    <b class="hl">{ch["false_alarms"]}</b> false alarm; the isolation forest raised <b class="bad">{fo["false_alarms"]}</b>. We recommend the chart.”</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:26px;text-align:center">A window, not a single day. The same events, the same scorer. <b class="hl">Then</b> the verdict.</p>""",
          f"Both come from the course's own verified results. Battery: the 3-year call ({_d(D['bat_call3'])}) gave {D['bat_warn3']} days of warning before the first dip. "
          f"Detector: both catch EV04 and EV05; {ch['false_alarms']} false alarm against {fo['false_alarms']}. Either sentence could close a demo."),

        # 17 ─ strong vs traps
        S(f"""
<div class="kicker anim">The judges have seen these before</div>
<h2 class="anim" style="--d:.1s;font-size:54px">A strong demo vs the six traps</h2>
<div class="row" style="gap:36px;margin-top:10px">
  <div class="card anim a-left" style="--d:.3s;flex:.9;border-color:#16A394;padding:28px 30px"><div class="icon">💪🏾</div><h3>Strong</h3>
    <p class="muted" style="font-size:23px;line-height:1.55">names the process and its owner<br>says what was fixed in the data<br>split by time, with the assert<br>
    beats (or honestly loses to) a baseline<br>a window or a band, with its coverage<br>runs live on the training server</p></div>
  <div class="card anim a-right" style="--d:.5s;flex:1.1;border-color:#E5484D;padding:24px 30px"><h3>🚨 Traps</h3>{traps}</div>
</div>""",
          "Each trap maps to a rubric line or an automatic penalty. The 'accuracy for rare events' trap is from W4D1: a detector that never alarms scores 99% accuracy and catches nothing."),

        # 18 ─ limitations
        S(f"""
<div class="kicker anim">Say it before the uncle asks</div>
<h2 class="anim" style="--d:.1s">Three honest limitations 🧭</h2>
<div class="grid3" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s"><div class="icon">🙈</div><h3>What will it miss?</h3><p class="muted" style="font-size:22px">{_limits()[0]}</p></div>
  <div class="card anim a-pop" style="--d:.55s"><div class="icon">⏳</div><h3>How late / how far?</h3><p class="muted" style="font-size:22px">{_limits()[1]}</p></div>
  <div class="card anim a-pop" style="--d:.8s"><div class="icon">📅</div><h3>What did you call normal?</h3><p class="muted" style="font-size:22px">{_limits()[2]}</p></div>
</div>
<p class="anim" style="--d:1.1s;margin-top:28px;text-align:center">Unit heads trust the engineer who says <b class="hl">where the tool stops working</b>.</p>""",
          "These are the three limitation questions from the requirements PDF, answered for the ticket forecast. Each participant's report needs its own three answers."),

        # 19 ─ peer feedback
        S("""
<div class="kicker anim">While others present</div>
<h2 class="anim" style="--d:.1s">Two stars and a wish ⭐⭐🙏🏾</h2>
<div class="grid3" style="margin-top:24px">
  <div class="card anim a-pop" style="--d:.3s;text-align:center"><div class="icon">⭐</div><h3>Star 1</h3><p class="muted" style="font-size:23px">one thing that was clear or clever</p></div>
  <div class="card anim a-pop" style="--d:.5s;text-align:center"><div class="icon">⭐</div><h3>Star 2</h3><p class="muted" style="font-size:23px">one thing you'll steal for your own work</p></div>
  <div class="card anim a-pop" style="--d:.7s;text-align:center"><div class="icon">🙏🏾</div><h3>A wish</h3><p class="muted" style="font-size:23px">one thing that would make it stronger</p></div>
</div>
<p class="anim" style="--d:1s;margin-top:30px;text-align:center">Use the <b class="hl">peer scoring sheet</b>: the six rubric lines, a quick score, then your stars and wish.<br><span class="small">Kind, specific, about the work. The instructor's mark is the official one.</span></p>""",
          "Hand out 2-exercise/demo-day/W6D3-peer-scoring-sheet.pdf. Peer scores are feedback, not grades. Collect the sheets and give each presenter theirs at the end."),

        # 20 ─ celebrate
        S("""
<div style="position:absolute;inset:0;pointer-events:none">
  <svg viewBox="0 0 1600 900" width="1600" height="900">
    <g class="anim a-fade" style="--d:.2s">
      <rect x="140" y="120" width="26" height="12" rx="3" fill="#F5B83D" transform="rotate(25 150 125)"/><rect x="1380" y="160" width="26" height="12" rx="3" fill="#3CCB7F" transform="rotate(-30 1390 165)"/>
      <rect x="260" y="700" width="26" height="12" rx="3" fill="#FF6B6F" transform="rotate(60 270 705)"/><rect x="1300" y="690" width="26" height="12" rx="3" fill="#3B8BE0" transform="rotate(-50 1310 695)"/>
      <circle cx="420" cy="180" r="10" fill="#16A394"/><circle cx="1180" cy="240" r="10" fill="#F5B83D"/><circle cx="1120" cy="740" r="10" fill="#FF6B6F"/><circle cx="520" cy="760" r="10" fill="#3B8BE0"/>
    </g>
  </svg></div>
<div class="big-emoji floaty anim a-pop" style="--d:.3s">🎉</div>
<h1 class="anim" style="--d:.5s;margin-top:20px">Oya, you don finish!</h1>
<p class="sub anim" style="--d:.8s;margin-top:20px">Certificates · a group photo · a round of applause for every presenter.</p>
<div class="row anim" style="--d:1.1s;margin-top:40px;gap:18px;justify-content:center">
  <span class="pill gold">🏅 certificates</span><span class="pill teal">📸 group photo</span><span class="pill">👏🏾 applause</span>
</div>""",
          "Make it a moment. Thank the unit heads who came. Call each participant up by name for the certificate.", cls="center"),

        # 21 ─ what next
        S("""
<div class="kicker anim">The course ends. The tool doesn't.</div>
<h2 class="anim" style="--d:.1s">What next? 🚀</h2>
<div class="grid4" style="margin-top:20px">
  <div class="card anim a-pop" style="--d:.3s;padding:28px 22px"><div class="icon">🔁</div><h3 style="font-size:28px">Keep it running</h3><p class="muted" style="font-size:21px">re-run the backtest or the remaining-life call every month or quarter</p></div>
  <div class="card anim a-pop" style="--d:.5s;padding:28px 22px"><div class="icon">📨</div><h3 style="font-size:28px">Hand it over</h3><p class="muted" style="font-size:21px">send your unit head the report, the README and the link</p></div>
  <div class="card anim a-pop" style="--d:.7s;padding:28px 22px"><div class="icon">📚</div><h3 style="font-size:28px">Keep the toolkit</h3><p class="muted" style="font-size:21px">rule books, the master glossary, every notebook</p></div>
  <div class="card anim a-pop" style="--d:.9s;padding:28px 22px"><div class="icon">📡</div><h3 style="font-size:28px">Ask for better data</h3><p class="muted" style="font-size:21px">time sync, longer archives, structured tickets (requirements PDF, section 8)</p></div>
</div>
<p class="sub anim" style="--d:1.2s;margin-top:40px;text-align:center">And remember: the <b class="hl">honest</b> result is always the respectable one.</p>""",
          "The most valuable thing a participant can do next week is keep the tool running and give it to its owner. The data-collection recommendations in section 8 of the requirements PDF are the shopping list for better projects next time."),

        # 22 ─ thank you
        S(f"""
<div class="kicker anim">Six weeks in three lines</div>
<h2 class="anim" style="--d:.1s">What you can now do</h2>
<div class="col" style="gap:16px;margin-top:6px">
  <div class="card anim a-left" style="--d:.3s;display:flex;gap:26px;align-items:center;padding:22px 34px"><span class="icon" style="margin:0">📈</span><p><b>Read a series</b>: clean it, plot it honestly, take it apart.</p></div>
  <div class="card anim a-left" style="--d:.55s;display:flex;gap:26px;align-items:center;padding:22px 34px"><span class="icon" style="margin:0">🚨</span><p><b>Catch what goes wrong</b>, and score it with event-level rules.</p></div>
  <div class="card anim a-left" style="--d:.8s;display:flex;gap:26px;align-items:center;padding:22px 34px"><span class="icon" style="margin:0">🔮</span><p><b>Say what comes next</b>, with a range, tested on the past first.</p></div>
</div>
<div class="anim" style="--d:1.2s;margin-top:30px;display:flex;justify-content:center;transform:scale(.8)">{logos_title_block()}</div>""",
          "Close. Thank the room, the unit heads and the helpers. Remind them where the materials live, and that the honest result is always the respectable one."),
    ]
    return slides


# =============================================================================
# POWERPOINT (static, simpler)
# =============================================================================
def pptx_spec():
    D = day_facts()
    s1, s2, s3, s4 = _sentences()
    lim = _limits()
    rows = rubric()
    ch, fo = D["chart"], D["forest"]
    split_last, split_first = D["ada_split"]
    return {
        "code": CODE, "title": TITLE,
        "slides": [
            {"type": "title", "icon": "🎤", "kicker": "Week 6 · Day 3 · the last session", "title": "Demo Day\n+ Project Clinic",
             "sub": "Six weeks. One tool for your unit. Five minutes to show it",
             "notes": "Today nobody learns a new method. Today everybody shows what they built."},
            {"type": "flow", "title": "Today's plan", "steps": [
                ["👋🏾", "Welcome", "the order of demos"], ["🩺", "Clinic", "4 help stations"],
                ["🎤", "Demos", "5 minutes + 1 question"], ["🎉", "Celebrate", "certificates + what next"]],
             "footer": "10 min welcome · 30 min clinic · 60 min demos · 20 min wrap-up", "notes": "Split the demos into two rooms if the cohort is bigger than 10."},
            {"type": "compare", "title": "The MC and the uncle",
             "left": ["🎤", "The owambe MC", "“Groom's friends, five minutes!” And the music starts on time"],
             "right": ["👴🏾", "The uncle in the front row", "“Tell us in one sentence: what does it do, and why should we care?”"],
             "notes": "Today you satisfy both: five minutes, and a point your unit head can repeat."},
            {"type": "table", "title": "18 days in one picture", "header": ["Week", "The big question", "The three days"],
             "rows": [[f"Week {w}", WEEK_Q[w][1], " · ".join(SHORT[d.code] for d in DAYS if d.week == w)] for w in range(1, 7)],
             "colW": [1.9, 4.3, 5.93], "caption": "Every project uses pieces from at least three of these weeks.", "notes": "Walk the road in 60 seconds."},
            {"type": "table", "title": "Four checkpoints done. Today is the fifth.", "header": ["Stage", "What", "Checkpoint"],
             "rows": [[f"{k}. {n}", w, wh] for k, (i, n, w, wh) in enumerate(STAGES)],
             "colW": [3.4, 4.6, 4.13], "caption": "Today: a working tool, the 2–4 page report and a 5-minute demo.",
             "notes": "If somebody missed a checkpoint, the clinic is where it gets fixed."},
            {"type": "bar", "title": "How it's graded: 100 points", "labels": [r[0] for r in rows], "values": [r[2] for r in rows],
             "highlight": [k for k, r in enumerate(rows) if r[2] == max(x[2] for x in rows)], "fmt": "0",
             "caption": "No model has to win. The test has to be honest.", "notes": "From the requirements PDF and the original brief."},
            {"type": "compare", "title": "What costs marks, and what doesn't",
             "left": ["✅", "Not penalised", "A model that loses to the simple baseline, if the comparison is fair and you recommend the simpler method"],
             "right": ["🚫", "Automatic penalties", "Random split · future-peeking feature · accuracy for rare events · RUL date with no window · real data on GitHub"],
             "notes": "Committed restricted data is a serious failure, reported to the programme lead."},
            {"type": "section", "kicker": "Part 1 · 30 minutes", "title": "The clinic", "sub": "Last fixes before the stage. Go where you need help most", "notes": "Section break."},
            {"type": "cards4", "title": "Clinic stations: pick the ONE you need", "cards": [[i, n, w] for i, n, w in STATIONS],
             "notes": "15 minutes at a station, then rotate or rehearse with a partner."},
            {"type": "table", "title": "The self-check notebook", "header": ["Function", "What it catches"],
             "rows": [["hygiene()", "wrong index, disorder, repeated or missing timestamps, no frequency, no time zone"],
                      ["leak_test()", "features that need something you couldn't know yet"],
                      ["check_temporal_split()", "a split that isn't by time, or an embargo that's too short"],
                      ["compare()", "methods scored on different weeks or with different scorers"],
                      ["coverage()", "a “90%” band that isn't"],
                      ["recommendation()", "a story without a number or an action"]],
             "colW": [3.4, 8.73], "caption": "Rehearse on Colab with course data, then download it to the training server for your real data.",
             "notes": "Real NIGCOMSAT data never goes into Colab."},
            {"type": "table", "title": "The leak test on six suspects (real ticket file)", "header": ["Feature", "Verdict"],
             "rows": [[n, "honest" if ok else "LEAKS"] for n, ok in D["suspects"].items()],
             "colW": [8.0, 4.13], "caption": "Hide week t's answer and the future, rebuild the feature: if it changes, it leaked.",
             "notes": "The last suspect contains the very number you're forecasting."},
            {"type": "stats", "title": "Rehearsal: what the self-check found in Ada's draft", "sub": "The real ticket file with planted problems",
             "stats": [[str(D["n_dup"]), "week exported twice"], [str(D["n_missing"]), "week that never arrived"],
                       ["shuffled", f"training reaches {_d(split_last)}, the test starts {_d(split_first)}"],
                       [f"{D['ada_cov'] * H:.0f}/{H}", f"weeks inside her “90%” band (±{ADA_HALF:.0f}); honest band (±{D['half']:.1f}): {D['honest_cov'] * H:.0f}/{H}"]],
             "notes": "Participants do these fixes in Parts A and B."},
            {"type": "section", "kicker": "Part 2 · 60 minutes", "title": "Demo time", "sub": "5 minutes to show it. 1 minute for one question. The timer is the MC", "notes": "Section break."},
            {"type": "table", "title": "The 5-minute demo, beat by beat", "header": ["Starts at", "Beat", "What to say or show", "Seconds"],
             "rows": [[f"{t // 60}:{t % 60:02d}", n, w, s] for (n, w, s, _), t in zip(DEMO, np.cumsum([0] + [x[2] for x in DEMO[:-1]]).tolist())],
             "colW": [1.6, 2.4, 6.53, 1.6], "caption": "Show the tool live, one table for the honest test, end on the recommendation.",
             "notes": "Rehearse once with a partner during the clinic, with a timer."},
            {"type": "table", "title": "The 4-sentence recommendation", "header": ["", "Worked example: the ticket forecast"],
             "rows": [["1 · Situation", s1], ["2 · Observation", s2], ["3 · Implication", s3], ["4 · Recommendation", s4]],
             "colW": [2.6, 9.53], "caption": "One number in the Observation. One action in the Recommendation.", "notes": "Numbers from the Week 6 Day 1 backtest."},
            {"type": "compare", "title": "One number, said plainly",
             "left": ["🔋", "Battery (W6D2)", f"First dip below 80%: {_d(D['bat_first'])}; last day at or above: {_d(D['bat_last'])}. "
                                          f"The 3-year straight line called {_d(D['bat_call3'])}, {abs(D['bat_err3'])} days before the first dip"],
             "right": ["🛰️", "Detector (W5D1)", f"Both caught {ch['caught']} of {ch['events']} events. Control chart: {ch['false_alarms']} false alarm; "
                                               f"isolation forest: {fo['false_alarms']}. We recommend the chart"],
             "notes": "A window, not a single day. The same events, the same scorer. Then the verdict."},
            {"type": "cards", "title": "Six traps the judges have seen before", "cards": [[i, TRAP_SHORT[n], w] for i, n, w in TRAPS[:3]],
             "notes": "First three traps."},
            {"type": "cards", "title": "…and three more", "cards": [[i, TRAP_SHORT[n], w] for i, n, w in TRAPS[3:]],
             "notes": "Each trap maps to a rubric line or an automatic penalty."},
            {"type": "cards", "title": "Three honest limitations", "cards": [["🙈", "What it misses", lim[0]], ["⏳", "How late or far", lim[1]],
                                                                           ["📅", "What was normal", lim[2]]],
             "notes": "Answered for the ticket forecast. Each report needs its own three answers."},
            {"type": "cards", "title": "Two stars and a wish", "cards": [["⭐", "Star 1", "one thing that was clear or clever"],
                                                                     ["⭐", "Star 2", "one thing you'll steal for your own work"],
                                                                     ["🙏🏾", "A wish", "one thing that would make it stronger"]],
             "notes": "Use the peer scoring sheet. Kind, specific, about the work."},
            {"type": "statement", "title": "Celebrate", "icon": "🎉", "big": "Oya, you don finish!",
             "sub": "Certificates · a group photo · a round of applause for every presenter", "notes": "Call each participant up by name."},
            {"type": "cards4", "title": "What next?", "cards": [["🔁", "Re-run", "the backtest or RUL call, monthly"],
                                                               ["📨", "Hand over", "report, README and link to your unit head"],
                                                               ["📚", "Toolkit", "rule books, glossary, notebooks"],
                                                               ["📡", "Better data", "requirements PDF, section 8"]],
             "notes": "The course ends. The tool doesn't."},
            {"type": "recap", "title": "What you can now do", "points": [
                ["📈", "Read a series: clean it, plot it honestly, take it apart"],
                ["🚨", "Catch what goes wrong, and score it with event-level rules"],
                ["🔮", "Say what comes next, with a range, tested on the past first"]],
             "next": "Thank you · Publica Academy × NIGCOMSAT", "notes": "Close."},
        ],
    }


# =============================================================================
# NOTEBOOK CHECKS (expected values filled in from the data at build time)
# =============================================================================
def _checks():
    D = day_facts()
    vals = {"ROWS": str(D["clean_rows"]), "NDUP": str(D["n_dup"]), "NMISS": str(D["n_missing"]), "GAP": GAP_WEEK,
            "GAPVAL": repr(D["gap_value"]), "NB": f"{D['gap_neighbours'][0]} and {D['gap_neighbours'][1]}",
            "NTRAIN": str(D["n_train"]), "NTEST": str(D["n_test"]), "BEST": repr(D["best"]), "BESTMAE": repr(D["best_mae"]), "BESTMAE2": f"{D['best_mae']:.2f}",
            "ADACOV": repr(D["ada_cov"]), "ADAIN": f"{D['ada_cov'] * H:.0f}", "H": str(H), "ADAHALF": f"{ADA_HALF:.0f}",
            "HALF": f"{D['half']:.1f}", "HCOV": repr(D["honest_cov"]), "HIN": f"{D['honest_cov'] * H:.0f}",
            "STAMP": D["report_stamp"], "FC": f"{D['report_fc']:.0f}", "CRON": repr(CRON)}
    code = r'''
def ready(*names):
    """True when every name exists (the earlier task is done); otherwise says what to finish first."""
    missing = [n for n in names if globals().get(n) is None]
    if missing:
        print(f"✍️  Finish the task that makes {', '.join(missing)} first, then run this cell again.")
    return not missing

def _words(s, n):
    return isinstance(s, str) and len(s.split()) >= n

def _c_a1(x):
    return str(x).strip().upper() == "W-MON", \
        "W-MON: weekly, on Mondays. Now read the report: two ⚠️ lines. 🔎", \
        "Weekly on Mondays is written \"W-MON\" (with the dash)."

def _c_a2(x):
    return tuple(int(v) for v in x) == (@@NDUP@@, @@NMISS@@), \
        "One week exported twice, one week that never arrived. Real exports do this all the time. 👯🏾🕳️", \
        "Read the two ⚠️ lines: duplicate timestamps first, then missing timestamps."

def _c_a3(x):
    if not isinstance(x, pd.DataFrame):
        return False, "", "Run the cell with GAP_FILL filled in."
    v = float(x.loc[pd.Timestamp("@@GAP@@"), "tickets_raised"])
    ok = (len(x) == @@ROWS@@ and x.index.is_unique and x.index.freq is not None and x.index.freqstr == "W-MON"
          and int(x.isna().sum().sum()) == 0 and abs(v - @@GAPVAL@@) < 1e-9)
    hint = ("0 tickets is a week that never happened: it drags every forecast down. Use \"interpolate\"."
            if v == 0 else "GAP_FILL = \"interpolate\": the lost week becomes the average of the weeks either side.")
    return ok, f"Clean: @@ROWS@@ weeks, no repeats, no holes, frequency declared. The lost week (@@GAP@@) became {v:.0f}, between its neighbours @@NB@@. Write that in your report. 🧹", hint

def _c_a4(x):
    return int(x[0]) == 1 and x[1] is True, \
        "shift(1): the 4 weeks BEFORE this one. The leak test says honest. 🛡️", \
        "shift(1) moves every value one week later, so week t only sees weeks t-4 to t-1. Then leak_test must say True."

def _c_b1(x):
    return tuple(int(v) for v in x) == (@@NTRAIN@@, @@NTEST@@), \
        "@@NTRAIN@@ training weeks, @@NTEST@@ test weeks (3 Nov to 22 Dec 2025), and the assert passed. ✂️", \
        "CUT = \"2025-11-03\": the first test week. Train = the weeks before it, test = from it on."

def _c_b2(x):
    ok = isinstance(x, pd.DataFrame) and x.index[0] == @@BEST@@ and abs(float(x.iloc[0, 0]) - @@BESTMAE@@) < 1e-6
    return ok, "Same 8 weeks, same scorer: the rate seasonal naive wins with MAE @@BESTMAE2@@. That's the table your demo needs. 📊", \
        "TERMINALS = train[\"active_vsat_terminals\"]: the training weeks' network size."

def _c_b3(x):
    return abs(float(x) - @@ADACOV@@) < 1e-9, \
        "Ada's “90%” band caught @@ADAIN@@ of @@H@@ weeks. Too narrow for a 90% claim. 📏", \
        "coverage(test_y, fc - @@ADAHALF@@, fc + @@ADAHALF@@)"

def _c_b4(x):
    q, cov = x
    return abs(float(q) - 0.9) < 1e-9 and abs(float(cov) - @@HCOV@@) < 1e-9, \
        "The 90th-percentile past miss is ±@@HALF@@ tickets, and that band caught @@HIN@@ of @@H@@ held-out weeks. Honest. ✅", \
        "For a 90% band, take the 90% quantile of the past misses: 0.9"

def _c_c1(x):
    from pathlib import Path as _P
    ok = (isinstance(x, (list, tuple)) and len(x) == 2 and all(_P(p).exists() and "@@STAMP@@" in _P(p).name for p in x)
          and "about @@FC@@ tickets" in _P(x[1]).read_text(encoding="utf-8"))
    return ok, "A dated chart and a dated summary. On the server, cron writes a new pair every morning. 🗓️", \
        "STAMP_FORMAT = \"%Y-%m-%d\": year first, so the files sort by date."

def _c_c2(x):
    return " ".join(str(x).split()) == @@CRON@@, \
        "0 7 * * *: minute 0, hour 7, every day, every month, every weekday. Your report is ready before the 8:00 meeting. ⏰", \
        "Five fields: minute, hour, day of month, month, day of week. A star means every. 07:00 daily = \"0 7 * * *\""

def _c_d1(x):
    ok = len(x) == 4 and all(_words(s, 4) for s in x) and any(ch.isdigit() for ch in x[1])
    hint = ("Put ONE number from the evaluation in the Observation sentence."
            if len(x) == 4 and all(_words(s, 4) for s in x) else "Write all four sentences, each at least 4 words.")
    return ok, "Four sentences, one number, one action. That's how your demo ends. 🗣️", hint

def _c_d2(x):
    return len(x) == 3 and all(_words(s, 3) for s in x), \
        "Three honest limits: what it misses, how far it reaches, what you called normal. Unit heads trust this. 🧭", \
        "Answer all three, each in a short sentence (at least 3 words)."

CHECKS = {"A1": _c_a1, "A2": _c_a2, "A3": _c_a3, "A4": _c_a4, "B1": _c_b1, "B2": _c_b2, "B3": _c_b3, "B4": _c_b4,
          "C1": _c_c1, "C2": _c_c2, "D1": _c_d1, "D2": _c_d2}
HINTS = {"A2": "Two whole numbers: (duplicates, missing).", "B4": "Two things: the quantile (0.9) and the coverage the cell computes.",
         "D1": "Four sentences, as text in quotes."}
'''
    for k, v in vals.items():
        code = code.replace(f"@@{k}@@", v)
    assert "@@" not in code
    return PLANT_CODE + "\n" + code


CHECKS = _checks()


# =============================================================================
# NOTEBOOK
# =============================================================================
def _task(blank: str, filled: str):
    return ("task", blank, filled)


APP_CODE = '''import pandas as pd
import streamlit as st

# Run on the training server:  streamlit run app.py
# Real data is read from a path on the server (set in .env or a config file), never from Git.
DATA = "/data/my_unit/export.csv"
THRESHOLD = 80.0

st.title("My unit's monitor")
df = pd.read_csv(DATA, parse_dates=["timestamp"], index_col="timestamp")
st.line_chart(df["value"])
st.write(f"Threshold: {THRESHOLD}")
st.write("One paragraph in plain words: what the chart shows, the latest forecast or flags with their range, and what to do.")'''


def notebook_cells(setup_code):
    D = day_facts()
    s1, s2, s3, s4 = _sentences()
    l1, l2, l3 = _limits()
    return [
        ("md", """# 🎤 Week 6 · Day 3: Project Self-Check

**Today:** you play the reviewer. A colleague, **Ada**, has a draft project with problems planted in it. You find them with six small self-check functions, fix them, then rehearse the deployment and the last minute of your demo.

| Symbol | Means |
|---|---|
| 📖 | Read this |
| ▶️ | Run the cell below (click it, then **Shift + Enter**) |
| ✍️ | Your turn: replace every `___` with your answer |
| ✅ / ❌ | The check tells you if you got it right, with a hint if not |

> ## ⚠️ Do this FIRST: **File → Save a copy in Drive**

### Two ways to use this notebook
1. **In Colab, today:** Parts A–D rehearse on Ada's export, which is built from a **synthetic** course file. Safe for Colab.
2. **On the training server, for your project:** **File → Download → Download .ipynb**, open it on the server, and fill in **Part E** with your real data.

> 🔒 **Real NIGCOMSAT data never goes into Colab or into an AI tool** (unless your unit head agreed in writing). Part E is for the training server only.

**Rule book:** keep `W6D3-rulebook.pdf` open next to you."""),
        ("md", """## ▶️ STEP 0: Set up
Run it once every time you open the notebook (and after every restart). Wait for `✅ Ready!`."""),
        ("setup", setup_code),
        ("md", """### ▶️ Your self-check toolkit
Six small functions. Read them once: they're short on purpose, so you can copy them into your own project.

| Function | The question it answers |
|---|---|
| `hygiene(df, freq)` | Is the series clean: time index, in order, no repeats, no holes, frequency declared, time zone known? |
| `leak_test(make_feature, df)` | Could this feature have been computed before the week started? |
| `check_temporal_split(train_index, test_index, embargo)` | Is every training timestamp before every test timestamp, with a gap? |
| `compare(actual, forecasts)` | Same weeks, same scorer: which method wins? |
| `coverage(actual, lower, upper)` | Did the band catch the share it promised? |
| `recommendation(...)` | Are the 4 sentences there, with a number? |"""),
        ("code", TOOLS_CODE + "\n\n" + SELFCHECK_CODE + '\n\nprint("✅ self-check toolkit and the Week 5–6 forecasting tools are ready")'),

        # ---------------- PART A ----------------
        ("md", """---
# Part A: Data & leaks (clinic station 1) 🔎

📖 Ada exported two years of weekly NOC tickets from the "NOC system". Real exports are messy: weeks go missing, weeks get exported twice. This one has **two** planted problems.

▶️ Load Ada's export exactly as it arrived (no `.asfreq()` yet)."""),
        ("code", 'raw = pd.read_csv(data_path("ops_tickets_weekly"), parse_dates=["week_start"], index_col="week_start")\n'
                 'draft = plant_problems(raw)          # Ada\'s export: the real file + 2 planted problems\n'
                 'print("rows in Ada\'s export:", len(draft))\ndraft.head()'),
        ("md", """### A1 ✍️ Run the hygiene report
`hygiene()` needs the frequency the series **should** have. Ticket weeks start on Mondays. Type the pandas frequency for "weekly, on Mondays", as text."""),
        _task('FREQ = ___\n\nreport = hygiene(draft, FREQ) if FREQ else None\ncheck("A1", FREQ)',
              'FREQ = "W-MON"\n\nreport = hygiene(draft, FREQ) if FREQ else None\ncheck("A1", FREQ)'),
        ("md", """### A2 ✍️ What did the report find?
Read the two ⚠️ lines. How many **duplicate** timestamps, and how many **missing** timestamps? Two whole numbers."""),
        _task('n_duplicates = ___\nn_missing = ___\n\ncheck("A2", (n_duplicates, n_missing))',
              f'n_duplicates = {D["n_dup"]}\nn_missing = {D["n_missing"]}\n\ncheck("A2", (n_duplicates, n_missing))'),
        ("md", """### A3 ✍️ Fix the export
The cell drops the repeated week, puts time in order and declares the frequency. Declaring it makes the lost week appear as an **empty** row. You choose how to fill it:
- `"interpolate"`: the average of the weeks either side
- `"zero"`: pretend the NOC raised 0 tickets that week

Whichever you choose, your report must **say what you did**."""),
        _task('GAP_FILL = ___\n\nclean = None\nif GAP_FILL:\n'
              '    clean = draft[~draft.index.duplicated(keep="first")].sort_index().asfreq("W-MON")\n'
              '    clean = clean.interpolate() if GAP_FILL == "interpolate" else clean.fillna(0)\n'
              '    hygiene(clean, "W-MON")\ncheck("A3", clean)',
              'GAP_FILL = "interpolate"\n\nclean = None\nif GAP_FILL:\n'
              '    clean = draft[~draft.index.duplicated(keep="first")].sort_index().asfreq("W-MON")\n'
              '    clean = clean.interpolate() if GAP_FILL == "interpolate" else clean.fillna(0)\n'
              '    hygiene(clean, "W-MON")\ncheck("A3", clean)'),
        ("md", """### ▶️ The leak test, done by the computer
📖 The question from Week 5: *"Could I have computed this feature at the moment the forecast was needed?"* `leak_test()` asks it for you. For several weeks it **hides that week's answer and every row after it**, rebuilds the feature, and checks whether the value changed. If it changed, the feature used something you couldn't have known.

▶️ Six suspects, on the clean file."""),
        ("code", SUSPECTS_CODE + '\n\nif ready("clean"):\n    for name, make in SUSPECTS.items():\n'
                 '        print(f"{\'✅ honest\' if leak_test(make, clean) else \'🚨 LEAKS \'}   {name}")'),
        ("md", """### A4 ✍️ Fix the leaky 4-week mean
`rolling(4).mean()` on its own includes **this** week: the very number you're trying to forecast. Shift it so week *t* only sees the 4 weeks **before** it. How many weeks do you shift by?"""),
        _task('SHIFT = ___\n\npassed = None\nif SHIFT is not None and ready("clean"):\n'
              '    past_4_weeks = lambda d: d["tickets_raised"].rolling(4).mean().shift(SHIFT)\n'
              '    passed = leak_test(past_4_weeks, clean)\n    print("leak test:", "✅ honest" if passed else "🚨 still leaks")\n'
              'check("A4", (SHIFT, passed))',
              'SHIFT = 1\n\npassed = None\nif SHIFT is not None and ready("clean"):\n'
              '    past_4_weeks = lambda d: d["tickets_raised"].rolling(4).mean().shift(SHIFT)\n'
              '    passed = leak_test(past_4_weeks, clean)\n    print("leak test:", "✅ honest" if passed else "🚨 still leaks")\n'
              'check("A4", (SHIFT, passed))'),

        # ---------------- PART B ----------------
        ("md", f"""---
# Part B: The honest test (clinic station 2) ⚖️

▶️ Ada split her weeks **at random** ("everyone does `train_test_split`!"). Watch `check_temporal_split()` catch it."""),
        ("code", f'if ready("clean"):\n    shuffled = clean.sample(frac=1, random_state={SHUFFLE_SEED})       # Ada\'s random split\n'
                 f'    ada_train, ada_test = shuffled.iloc[:-{H}], shuffled.iloc[-{H}:]\n'
                 '    try:\n        check_temporal_split(ada_train.index, ada_test.index)\n'
                 '    except AssertionError as e:\n        print(e)\n        print("👆 That is why it fails: the test weeks are mixed in with the training weeks.")'),
        ("md", """### B1 ✍️ Split by time instead
Keep the **last 8 weeks** for the test, like Week 5 Day 2. The first test week is **3 November 2025**. Type it as text, like `"2025-01-01"`."""),
        _task('CUT = ___\n\nsplit = None\nif CUT and ready("clean"):\n    train = clean[clean.index < CUT]\n    test = clean[clean.index >= CUT]\n'
              '    test_y = test["tickets_raised"]\n    check_temporal_split(train.index, test.index)\n    split = (len(train), len(test))\n'
              '    print("training weeks:", len(train), "· test weeks:", len(test))\ncheck("B1", split)',
              'CUT = "2025-11-03"\n\nsplit = None\nif CUT and ready("clean"):\n    train = clean[clean.index < CUT]\n    test = clean[clean.index >= CUT]\n'
              '    test_y = test["tickets_raised"]\n    check_temporal_split(train.index, test.index)\n    split = (len(train), len(test))\n'
              '    print("training weeks:", len(train), "· test weeks:", len(test))\ncheck("B1", split)'),
        ("md", f"""### B2 ✍️ The comparison table: same weeks, same scorer
`compare()` scores every forecast on the **same {H} test weeks** with the **same scorer** (MAE), best first. It refuses a forecast for a different number of weeks.
The rate seasonal naive (Week 5 Day 2) needs the training weeks' **terminal counts**. Fill them in."""),
        _task(f'TERMINALS = ___\n\ntable = None\nif TERMINALS is not None and ready("train", "test_y"):\n    ty = train["tickets_raised"]\n'
              f'    table = compare(test_y, {{"naive": naive(ty, {H}), "seasonal naive": seasonal_naive(ty, {H}),\n'
              f'                             "rate seasonal naive": rate_seasonal_naive(ty, TERMINALS, {H})}})\n    display(table)\ncheck("B2", table)',
              f'TERMINALS = train["active_vsat_terminals"]\n\ntable = None\nif TERMINALS is not None and ready("train", "test_y"):\n    ty = train["tickets_raised"]\n'
              f'    table = compare(test_y, {{"naive": naive(ty, {H}), "seasonal naive": seasonal_naive(ty, {H}),\n'
              f'                             "rate seasonal naive": rate_seasonal_naive(ty, TERMINALS, {H})}})\n    display(table)\ncheck("B2", table)'),
        ("md", f"""### B3 ✍️ Ada's "90%" band
Ada put **±{ADA_HALF:.0f} tickets** around the rate forecast "because it looked tidy", and called it a 90% band. What share of the {H} test weeks did it actually catch? Use `coverage(actual, lower, upper)`."""),
        _task(f'fc = rate_seasonal_naive(train["tickets_raised"], train["active_vsat_terminals"], {H}) if ready("train") else None\n\n'
              'cov_ada = ___\n\nif cov_ada is not None:\n    print(f"Ada\'s band caught {cov_ada:.0%} of the test weeks")\ncheck("B3", cov_ada)',
              f'fc = rate_seasonal_naive(train["tickets_raised"], train["active_vsat_terminals"], {H}) if ready("train") else None\n\n'
              f'cov_ada = coverage(test_y, fc - {ADA_HALF:.0f}, fc + {ADA_HALF:.0f})\n\nif cov_ada is not None:\n    print(f"Ada\'s band caught {{cov_ada:.0%}} of the test weeks")\ncheck("B3", cov_ada)'),
        ("md", f"""### B4 ✍️ The honest band (Week 5 Day 3's recipe)
Make the same {H}-week forecast from every **earlier** week, record every miss, and use the miss you beat 90% of the time as the half-width. Which quantile gives a 90% band?"""),
        _task(f'Q = ___\n\nresult = None\nif Q is not None and ready("train", "fc"):\n    misses = rate_past_errors(clean, len(train), h={H})\n'
              '    half = np.quantile(np.abs(misses), Q)\n    cov_honest = coverage(test_y, fc - half, fc + half)\n'
              '    print(f"{len(misses)} past misses · half-width ±{half:.1f} tickets · caught {cov_honest:.0%} of the test weeks")\n'
              '    result = (Q, cov_honest)\ncheck("B4", result)',
              f'Q = 0.9\n\nresult = None\nif Q is not None and ready("train", "fc"):\n    misses = rate_past_errors(clean, len(train), h={H})\n'
              '    half = np.quantile(np.abs(misses), Q)\n    cov_honest = coverage(test_y, fc - half, fc + half)\n'
              '    print(f"{len(misses)} past misses · half-width ±{half:.1f} tickets · caught {cov_honest:.0%} of the test weeks")\n'
              '    result = (Q, cov_honest)\ncheck("B4", result)'),

        # ---------------- PART C ----------------
        ("md", """---
# Part C: Deployment (clinic station 3) 🚀

📖 Your tool must **run on the training server**, not only on your laptop. Two options:
- a **scheduled report**: a script the server runs every morning, writing a dated chart and summary to a shared folder
- a **Streamlit dashboard**: a small web page your unit opens in a browser

▶️ Here is a scheduled report for the ticket forecast. Read it: it forecasts the week after the data ends, with its honest band, and saves two dated files."""),
        ("code", "from pathlib import Path\nfrom IPython.display import Image\n\n" + REPORT_CODE + '\n\nprint("✅ write_report() is ready")'),
        ("md", """### C1 ✍️ Name the files by date
Every morning's report needs its own file name. Choose a date format so the files **sort in date order** in the folder. Python's codes: `%Y` = year, `%m` = month, `%d` = day."""),
        _task('STAMP_FORMAT = ___\n\npaths = None\nif STAMP_FORMAT and ready("clean"):\n    paths = write_report(clean, STAMP_FORMAT)\n'
              '    print(paths)\n    print(Path(paths[1]).read_text())\n    display(Image(paths[0]))\ncheck("C1", paths)',
              f'STAMP_FORMAT = "{STAMP}"\n\npaths = None\nif STAMP_FORMAT and ready("clean"):\n    paths = write_report(clean, STAMP_FORMAT)\n'
              '    print(paths)\n    print(Path(paths[1]).read_text())\n    display(Image(paths[0]))\ncheck("C1", paths)'),
        ("md", """### C2 ✍️ Schedule it
On the training server (Linux), **cron** runs a command on a timetable. A cron line has **five** fields, then the command:

```
minute  hour  day-of-month  month  day-of-week   command
```

A `*` means "every". Write the five fields for **07:00 every day**, as text."""),
        _task('CRON_TIME = ___\n\nif CRON_TIME:\n    print("crontab line:", CRON_TIME, "cd /home/me/project && python report.py")\ncheck("C2", CRON_TIME)',
              f'CRON_TIME = "{CRON}"\n\nif CRON_TIME:\n    print("crontab line:", CRON_TIME, "cd /home/me/project && python report.py")\ncheck("C2", CRON_TIME)'),
        ("md", """### ▶️ Or a Streamlit dashboard
This writes a starter `app.py` (Files panel 📁 → right-click → Download). On the server: `pip install streamlit`, then `streamlit run app.py`. Streamlit doesn't run inside Colab, so this cell only writes the file."""),
        ("code", "APP = '''" + APP_CODE + "'''\nPath(\"app.py\").write_text(APP, encoding=\"utf-8\")\nprint(APP)"),

        # ---------------- PART D ----------------
        ("md", """---
# Part D: The story (clinic station 4) 🗣️

📖 Your demo ends with the 4-sentence recommendation, and your report states three limitations. Rehearse both on the ticket forecast, using the numbers from Week 6 Day 1's backtest:"""),
        ("md", f"""| From the Week 6 Day 1 backtest ({D['h8_n']} starting weeks, 8 weeks ahead) | MAE (tickets per week) |
|---|---|
| Rate seasonal naive: last year's tickets per terminal × this week's terminals | **{D['h8_rate']:.2f}** |
| Naive: "same as last week" | {D['h8_naive']:.2f} |
| The regression | can only forecast 1 week ahead (it needs last week's real count) |"""),
        ("md", """### D1 ✍️ Write the 4 sentences
1. **Situation:** what the unit does today, and the problem.
2. **Observation:** what the evaluation showed: **one number**.
3. **Implication:** what it means for operations.
4. **Recommendation:** what to do next, and with which tool."""),
        _task('situation = ___\nobservation = ___\nimplication = ___\naction = ___\n\n'
              'if None not in (situation, observation, implication, action):\n    text = recommendation(situation, observation, implication, action)\n'
              'check("D1", (situation, observation, implication, action))',
              f'situation = {s1!r}\nobservation = {s2!r}\nimplication = {s3!r}\naction = {s4!r}\n\n'
              'if None not in (situation, observation, implication, action):\n    text = recommendation(situation, observation, implication, action)\n'
              'check("D1", (situation, observation, implication, action))'),
        ("md", """### D2 ✍️ Three honest limitations
Answer each in one short sentence."""),
        _task('what_it_misses = ___\nhow_late_or_far = ___\nwhat_was_normal = ___\n\ncheck("D2", (what_it_misses, how_late_or_far, what_was_normal))',
              f'what_it_misses = {l1!r}\nhow_late_or_far = {l2!r}\nwhat_was_normal = {l3!r}\n\ncheck("D2", (what_it_misses, how_late_or_far, what_was_normal))'),
        ("md", """---
## 🏁 Finish line
▶️ Run the scoreboard, then **File → Save**."""),
        ("code", "scoreboard()"),

        # ---------------- PART E ----------------
        ("md", """---
# Part E: On your own project (training server only) 🔒

📖 Download this notebook (**File → Download → Download .ipynb**) and open it on the **training server**. Fill in the five settings below. While `PROJECT_CSV` is `None`, every cell here politely skips, so the notebook still runs in Colab.

> 🔒 Never put real NIGCOMSAT data in Colab, an AI tool or GitHub."""),
        ("code", 'PROJECT_CSV = None        # e.g. "/data/my_unit/battery_export.csv" (a path on the server)\n'
                 'TIME_COL = None           # e.g. "timestamp"\nVALUE_COL = None          # e.g. "battery_capacity_pct"\n'
                 'PROJECT_FREQ = None       # e.g. "h", "D" or "W-MON"\nTHRESHOLD = None          # your operational limit, e.g. 80.0 (or None)\n\n'
                 'mine = None\nif PROJECT_CSV is None:\n    print("⏭️  Skipped: set PROJECT_CSV on the training server to check your own data.")\nelse:\n'
                 '    mine = pd.read_csv(PROJECT_CSV, parse_dates=[TIME_COL], index_col=TIME_COL).sort_index()\n'
                 '    hygiene(mine, PROJECT_FREQ)'),
        ("code", 'if mine is None:\n    print("⏭️  Skipped: no project data loaded.")\nelse:\n    ax = mine[VALUE_COL].plot(title="✍️ Write a title that states your finding")\n'
                 '    if THRESHOLD is not None:\n        ax.axhline(THRESHOLD, color="#E5484D", ls="--", label=f"threshold {THRESHOLD}")\n        ax.legend()\n    plt.show()'),
        ("code", '# Your split: set the first test timestamp and your longest feature window (the embargo)\nPROJECT_CUT = None        # e.g. "2025-09-01"\n'
                 'PROJECT_EMBARGO = "0D"    # e.g. "24h" for a 24-hour rolling window\n\n'
                 'if mine is None or PROJECT_CUT is None:\n    print("⏭️  Skipped: set PROJECT_CUT once your data is loaded.")\nelse:\n'
                 '    my_train = mine[mine.index < PROJECT_CUT]\n'
                 '    my_test = mine[mine.index >= pd.Timestamp(PROJECT_CUT) + pd.Timedelta(PROJECT_EMBARGO)]\n'
                 '    check_temporal_split(my_train.index, my_test.index, PROJECT_EMBARGO)'),
        ("md", f"""### 📝 Before you present
- **Hygiene:** no repeats, no holes (or holes explained), frequency declared, time zone written down.
- **Leak test:** every feature passes `leak_test()`.
- **Honest test:** split by time with the assert, the baseline on the same period with the same scorer, and the spread (folds), the repeated calls (remaining life) or the coverage (bands).
- **Deployed:** it runs on the training server; the README says how.
- **The story:** 4 sentences with one number, 3 limitations, and a 5-minute run-through with a timer.

**Congratulations: that's the course.** 🎉 Go and show your unit what you built.

<sub>Data: the synthetic `ops_tickets_weekly.csv` from the original Week 6 code book (`Time-series/week-06`), with two problems planted for the rehearsal. Safe to use with AI tools; real NIGCOMSAT data is not.</sub>"""),
    ]


# =============================================================================
# EXTRAS: demo-day peer scoring sheet + final report template
# =============================================================================
LOOK_FOR = {
    "Problem framing and data": "Did they name the unit, the process and who uses the tool? Is the data real, described, and kept off GitHub?",
    "Understanding the series": "Did they say what was wrong with the data and what they fixed? Is the threshold on the chart?",
    "Method": "Does the method fit the brief? Did every feature pass the leak test?",
    "Honest evaluation": "Split by time? A baseline on the same period, same scorer? Spread, repeated calls or coverage shown?",
    "Deployment": "Did it run live from the training server (or today's scheduled report)?",
    "Communication and AI use": "4 sentences with a number? Limitations said out loud? On time?",
}


def scoring_sheet() -> str:
    rows = rubric()
    assert set(LOOK_FOR) == {r[0] for r in rows}, "rubric names changed: update LOOK_FOR"
    table = "\n".join(f"| **{name}** | {LOOK_FOR[name]} | ___/{pts} |" for name, _, pts in rows)
    one = f"""| Presenter | Brief (A–E) and process |
|---|---|
| <div style="height:34px"></div> | |

| Rubric line | What to look for in the demo | Score |
|---|---|---|
{table}

**Total: ______ / 100**

| ⭐ Star 1: one thing that was clear or clever | ⭐ Star 2: one thing I'll steal for my own work | 🙏🏾 A wish: one thing that would make it stronger |
|---|---|---|
| <div style="height:130px"></div> | | |
"""
    return f"""# Demo Day: Peer Scoring Sheet

One sheet per presenter. Score from what you **saw and heard** in the 5 minutes; the instructor scores the report and the code. Peer scores are **feedback, not grades**: kind, specific, about the work.

{one}
<div class="pagebreak"></div>

{one}
<div class="pagebreak"></div>

## Instructor tally (one line per presenter)

| # | Presenter | Brief | On time? (5:00) | Peer average | Instructor score | Unit head present? |
|---|---|---|---|---|---|---|
""" + "\n".join(f"| {k} | | | ☐ | | | ☐ |" for k in range(1, 16)) + "\n"


REPORT_TEMPLATE = """# Final Report Template

Copy this into your own file (Markdown or Word, then PDF). Keep it to **2–4 pages**. Replace the hints in each section with your own words. The rubric line each section earns is shown in **[brackets]**.

## Title: one line that states the finding

> e.g. *"The battery-health review can see the 80% floor coming about 4 months ahead"*

**Name · Unit · Brief (A–E) · Date of the unit head's agreement**

## 1. The process and the agreement **[Problem framing and data · 15]**

| | Your answer |
|---|---|
| **Unit** | |
| **Named process** (with its owner) | |
| **Who uses the tool** | |
| **The question it answers** | |
| **Unit head's agreement** | attach the email (appendix) |
| **Adapted brief?** | what you changed, and that your unit head agreed |

## 2. The data **[Problem framing and data · Understanding the series]**

| | Your answer |
|---|---|
| **Source system / export** | |
| **Span** (from – to) and **cadence** | |
| **Time zone** | |
| **Problems found** (gaps, duplicates, sampling changes) | |
| **What you did about each one** | |
| **Seasonal period** (from the correlogram) | |
| **Restrictions** | what is restricted, and how you kept it on NIGCOMSAT systems |

Paste **one honest chart**: sensible axis, the operational threshold drawn, a title that states the finding.

## 3. The method **[Method · 20]**

- What it is, in two or three sentences, and **why it suits this process**.
- Every feature, and the result of its **leak test**.
- The settings, and **when** you fixed them (before the test).

## 4. The honest test **[Honest evaluation · 25]**

- **Split:** train from ____ to ____, test from ____ to ____, embargo ____ (= the longest feature window). The `assert` passed.
- **Scorer and rules, written first:** e.g. event-level precision and recall with a ±1 h window, or MAE in units per week.

| Method | Period | Score | Spread / coverage / repeated calls |
|---|---|---|---|
| Simple baseline | | | |
| Your method | | | |

- Detection: event-level precision and recall, **never accuracy**.
- Forecasting: the walk-forward spread across folds, and the coverage of your band on held-out data.
- Remaining life: the call repeated from several starting points, with the warning time each one gave. A **window**, never a single date.
- If the simple method won or tied: say so, and recommend it.

## 5. The tool **[Deployment · 15]**

- Streamlit dashboard **or** scheduled report: what it shows (series, threshold, flags or forecast with its range, a plain-language paragraph).
- Where it runs on the training server, its URL or its schedule (e.g. cron `0 7 * * *`).
- How to run it: see the `README.md` in the repository. No raw data in the repository.

## 6. Recommendation: four sentences **[Communication · 10]**

1. **Situation:**
2. **Observation** (one number):
3. **Implication:**
4. **Recommendation:**

## 7. Limitations

- **What will it miss?**
- **How late will it be, or how far ahead can it see?**
- **What did you assume was normal?** (the reference / training period)

## 8. AI-use note (one paragraph)

What you used an AI assistant for, how you checked its output, and how you kept restricted data out of it (e.g. "I described the column names and shape; I never pasted rows").

## Appendix

- The unit head's email
- The repository link and the `requirements.txt`

<div class="box warn" markdown="1">
**Before you submit:** no random split · no feature that uses the future · no accuracy figure for rare events · no remaining-life date without a window · **no real NIGCOMSAT data in the repository**.
</div>
"""


def extra(d, foot):
    import pdfdoc

    folder = d.folder / SUB["exercise"] / "demo-day"
    folder.mkdir(parents=True, exist_ok=True)
    sheet = folder / f"{CODE}-peer-scoring-sheet.md"
    sheet.write_text(scoring_sheet(), encoding="utf-8")
    pdfdoc.md_to_pdf(sheet, sheet.with_suffix(".pdf"), kicker="Week 6 · Day 3 · Demo day", title="Peer Scoring Sheet",
                     subtitle="Two stars and a wish, against the six rubric lines.", foot=foot)
    tmpl = folder / f"{CODE}-final-report-template.md"
    tmpl.write_text(REPORT_TEMPLATE, encoding="utf-8")
    pdfdoc.md_to_pdf(tmpl, tmpl.with_suffix(".pdf"), kicker="Week 6 · Day 3 · Final project", title="Final Report Template",
                     subtitle="2–4 pages your unit head can read in ten minutes.", foot=foot)
