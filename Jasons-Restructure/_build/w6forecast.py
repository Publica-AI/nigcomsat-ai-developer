"""The Week 5-6 forecasting and remaining-life story, shared by W5D2, W5D3, W6D1 and W6D2.

The original Week 6 code book's numbers mostly reproduce (so Quiz 4 matches the data), but it misses the one
idea that makes this series easy, and it has a few real bugs (see 01-REVIEW-OF-ORIGINALS.md, rows 4 and 12m-12q):

  W5D2  the four code-book baselines on the last 8 weeks (naive wins at 11.25), then the fix the code book
        never tries: tickets PER TERMINAL repeat almost exactly each year, so last year's rate x today's
        network ("rate seasonal naive") forecasts all 8 weeks blind with MAE 2.3.
  W5D3  the code-book regression (one week ahead, MAE 5.85) vs one-step naive (6.75); its 90% band covers
        5 of 8 weeks; a band built from honest past misses covers 7 of 8; the rate forecast still wins.
  W6D1  walk-forward on the code book's 6 folds (naive beats the regression 5 of 6), then every origin and
        three horizons: naive is the one-week champion, the rate forecast wins 4 and 8 weeks out.
  W6D2  trend-to-threshold with the propellant bug fixed, "crossing" defined three ways, the battery call
        repeated from 4 origins, and the fuel-gauge sum for the propellant.

The notebook code lives here as strings and the build runs those exact strings, so every number on a slide
comes from the same code the participants run.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from common import ORIGINALS

D6 = ORIGINALS / "week-06" / "data"
H = 8                                  # the code book's hold-out: the last 8 weeks (3 Nov - 22 Dec 2025)
PERIOD = 52
X_COLS = ["tickets_lag1", "tickets_lag52", "terminals", "sin52", "cos52"]
TRAIN_DAYS = 365 * 3                   # the code book's RUL call uses the first three years only
FIRST_ERR_ROW = 12                     # honest-band walk-forward starts once 12 rows exist (2 per number fitted)

# ----------------------------------------------------------------------------- notebook code (run here too)
BASELINE_CODE = '''def naive(series, h):
    """Grandma's forecast: the last value we saw, repeated h times."""
    return np.full(h, float(series.iloc[-1]))

def seasonal_naive(series, h, period=52):
    """The same weeks one season (52 weeks) ago."""
    last_season = series.iloc[-period:].values
    return np.tile(last_season, int(np.ceil(h / period)))[:h].astype(float)

def moving_average(series, h, window=8):
    """The mean of the last `window` weeks, held flat."""
    return np.full(h, float(series.iloc[-window:].mean()))

def exp_smoothing(series, h, alpha=0.3):
    """Simple exponential smoothing: a running level, each new week pulls it alpha of the way."""
    level = series.iloc[0]
    for v in series.iloc[1:]:
        level = alpha * v + (1 - alpha) * level
    return np.full(h, float(level))

def rate_seasonal_naive(series, terminals, h, period=52):
    """Grandma, adjusted for the bigger family: last year's tickets PER TERMINAL x today's terminals."""
    rate = series / terminals
    return rate.iloc[-period:].values[:h] * float(terminals.iloc[-1])

def mae(forecast, actual):
    """Mean absolute error: on a typical week, how many tickets were we off by?"""
    return float(np.mean(np.abs(np.asarray(forecast, float) - np.asarray(actual, float))))'''

FEATURE_CODE = '''def make_features(df):
    """The code book's feature table. Every column is known BEFORE the week starts."""
    f = pd.DataFrame(index=df.index)
    f["tickets_lag1"] = df["tickets_raised"].shift(1)     # last week (shift(+1) = the past)
    f["tickets_lag52"] = df["tickets_raised"].shift(52)   # same week, last year
    f["terminals"] = df["active_vsat_terminals"]
    woy = df.index.isocalendar().week.astype(int)
    f["sin52"] = np.sin(2 * np.pi * woy / 52)             # week of year as a smooth circle
    f["cos52"] = np.cos(2 * np.pi * woy / 52)
    f["target"] = df["tickets_raised"]
    return f.dropna()

def walk_forward_errors(feat, x_cols, first=12):
    """Honest past misses: for each week from row `first`, fit on the rows BEFORE it, forecast it, keep the miss."""
    errors = []
    for k in range(first, len(feat)):
        model = LinearRegression().fit(feat[x_cols].iloc[:k], feat["target"].iloc[:k])
        errors.append(feat["target"].iloc[k] - model.predict(feat[x_cols].iloc[[k]])[0])
    return np.array(errors)

def rate_past_errors(df, origin, h=8, period=52):
    """Misses of every h-week rate forecast made from an earlier origin whose h weeks end before `origin`."""
    errors = []
    for o in range(period, origin - h + 1):
        f = rate_seasonal_naive(df["tickets_raised"].iloc[:o], df["active_vsat_terminals"].iloc[:o], h, period)
        errors.extend(df["tickets_raised"].iloc[o:o + h].values - f)
    return np.array(errors)'''

BACKTEST_CODE = '''def walk_forward_mae(df, feature_fn, x_cols, start_frac=0.5, step=4, h=4):
    """The code book's expanding-window backtest: refit at each cut, forecast h weeks, score, slide forward."""
    feat_all = feature_fn(df)
    n = len(feat_all)
    errors = []
    for cut in range(int(n * start_frac), n - h, step):
        tr, te = feat_all.iloc[:cut], feat_all.iloc[cut:cut + h]
        model = LinearRegression().fit(tr[x_cols], tr["target"])
        errors.append(mae(model.predict(te[x_cols]), te["target"]))
    return np.array(errors)

def rolling_origin(df, forecasters, h, first=52):
    """Stand at EVERY week from `first` on, forecast the next h weeks with each method, score each one."""
    rows = []
    for o in range(first, len(df) - h + 1):
        past, future = df.iloc[:o], df["tickets_raised"].iloc[o:o + h]
        row = {"origin": df.index[o]}
        for name, fn in forecasters.items():
            row[name] = mae(fn(past, h), future)
        rows.append(row)
    return pd.DataFrame(rows).set_index("origin")'''

RUL_CODE = '''def fit_trend(series, degree=1):
    """Fit day-number vs value. Returns the fitted line (callable) and its numbers (slope, intercept)."""
    x = np.arange(len(series))
    coef = np.polyfit(x, series.values, degree)
    return np.poly1d(coef), coef

def day_of_threshold(series, threshold, direction="falls_below", degree=1, extra_days=4000):
    """Extend the trend forward until it crosses the threshold. Returns (day number, line).
    FIXED: returns None when it does not cross inside the search window (the original said day 0)."""
    model, coef = fit_trend(series, degree)
    y_future = model(np.arange(len(series) + extra_days))
    crossed = y_future < threshold if direction == "falls_below" else y_future > threshold
    if not crossed.any():
        return None, model
    return int(np.argmax(crossed)), model

def crossing_dates(series, threshold, window=30):
    """Three honest answers to "when did it cross?" for a falling series."""
    below = series < threshold
    smooth = series.rolling(window).mean()
    return {"first_dip": series.index[below.values.argmax()],
            f"{window}_day_mean": smooth.index[(smooth < threshold).values.argmax()],
            "last_good_day": series[~below].index[-1]}'''

exec(BASELINE_CODE)
exec(FEATURE_CODE)
exec(BACKTEST_CODE)
exec(RUL_CODE)


def load():
    tickets = pd.read_csv(D6 / "ops_tickets_weekly.csv", parse_dates=["week_start"],
                          index_col="week_start").asfreq("W-MON")
    degr = pd.read_csv(D6 / "degradation_assets_daily.csv", parse_dates=["date"], index_col="date").asfreq("D")
    limits = pd.read_csv(D6 / "degradation_thresholds.csv")
    return tickets, degr, limits


def _blind(name):
    """The baselines (and the flat training mean) as forecasters for rolling_origin: f(past_df, h) -> h numbers."""
    return {"naive": lambda p, h: naive(p["tickets_raised"], h),
            "seasonal_naive": lambda p, h: seasonal_naive(p["tickets_raised"], h),
            "moving_average": lambda p, h: moving_average(p["tickets_raised"], h),
            "exp_smoothing": lambda p, h: exp_smoothing(p["tickets_raised"], h),
            "rate_seasonal_naive": lambda p, h: rate_seasonal_naive(p["tickets_raised"], p["active_vsat_terminals"], h),
            "training_mean": lambda p, h: np.full(h, float(p["tickets_raised"].mean()))}[name]


def _date(degr, day):
    return None if day is None else degr.index[0] + pd.Timedelta(days=int(day))


@lru_cache(maxsize=1)
def facts():
    """Every number the four days show. Computed from the original data, never typed in."""
    tickets, degr, limits = load()
    y, term = tickets["tickets_raised"], tickets["active_vsat_terminals"]
    F = {"n_weeks": len(tickets), "first_week": tickets.index[0], "last_week": tickets.index[-1],
         "gaps": int(tickets.isna().sum().sum()), "term_first": int(term.iloc[0]), "term_last": int(term.iloc[-1]),
         "y_min": int(y.min()), "y_max": int(y.max()), "y_mean_by_year": y.groupby(y.index.year).mean().round(1).to_dict()}

    # ---------------------------------------------------------------- W5D2 baselines on the last 8 weeks
    train, actual = y.iloc[:-H], y.iloc[-H:]
    tterm = term.iloc[:-H]
    fc = pd.DataFrame({"naive": naive(train, H), "seasonal_naive": seasonal_naive(train, H),
                       "moving_average": moving_average(train, H), "exp_smoothing": exp_smoothing(train, H),
                       "rate_seasonal_naive": rate_seasonal_naive(train, tterm, H)}, index=actual.index)
    fc["actual"] = actual.values
    F["holdout"] = (actual.index[0], actual.index[-1])
    F["fc"] = fc
    F["baseline_mae"] = {c: mae(fc[c], actual) for c in fc.columns if c != "actual"}
    F["training_mean_mae"] = mae(np.full(H, train.mean()), actual)
    F["term_origin"] = int(tterm.iloc[-1])
    F["term_year_before"] = int(tterm.iloc[-1 - PERIOD])
    F["sn_source"] = train.iloc[-PERIOD:].values[:H].tolist()
    F["last_train_week"] = (train.index[-1], int(train.iloc[-1]))
    # the rate story: tickets per 1,000 terminals by month and year (seen in TRAINING weeks only)
    rate = y / term * 1000
    tr_rate = rate.iloc[:-H]
    F["rate_by_month"] = tr_rate.groupby([tr_rate.index.month, tr_rate.index.year]).mean().unstack().round(1)
    rainy = y.index.month.isin(range(4, 11))
    F["rate_rainy"] = float(rate[rainy].mean()); F["rate_dry"] = float(rate[~rainy].mean())
    F["rainy_lift"] = F["rate_rainy"] / F["rate_dry"] - 1
    F["rate_dec"] = float(rate[y.index.month == 12].mean()); F["rate_nov"] = float(rate[y.index.month == 11].mean())
    F["season_steps"] = {d: int(y.diff().loc[d]) for d in ["2024-04-01", "2024-11-04", "2025-04-07", "2025-11-03"]}

    # ---------------------------------------------------------------- W5D3 regression + intervals
    feat = make_features(tickets)
    cut = feat.index[-H]
    train_f, test_f = feat.loc[:cut].iloc[:-1], feat.loc[cut:]
    reg = LinearRegression().fit(train_f[X_COLS], train_f["target"])
    pred = reg.predict(test_f[X_COLS])
    F["feat_rows"] = len(feat); F["rows_lost"] = len(tickets) - len(feat)
    F["train_f"] = (train_f.index[0], train_f.index[-1], len(train_f))
    F["coef"] = dict(zip(X_COLS, reg.coef_)); F["intercept"] = float(reg.intercept_)
    F["reg_pred"] = pd.Series(pred, index=test_f.index)
    F["reg_mae"] = mae(pred, test_f["target"])
    F["onestep_naive_mae"] = mae(test_f["tickets_lag1"], test_f["target"])
    err = test_f["target"].values - pred
    F["reg_err"] = pd.Series(err, index=test_f.index)
    F["reg_err_sd"] = float(np.std(err, ddof=1)); F["reg_err_mean"] = float(err.mean())
    resid = train_f["target"] - reg.predict(train_f[X_COLS])
    F["resid_sd"] = float(resid.std())
    half_in = 1.645 * F["resid_sd"]
    covered = lambda half, f: int(((test_f["target"].values >= f - half) & (test_f["target"].values <= f + half)).sum())
    F["band_insample"] = {"half": half_in, "covered": covered(half_in, pred)}
    wf = walk_forward_errors(train_f, X_COLS, first=FIRST_ERR_ROW)
    half_wf = float(np.quantile(np.abs(wf), 0.9))
    F["band_walkforward"] = {"half": half_wf, "covered": covered(half_wf, pred), "n_errors": len(wf),
                             "from": train_f.index[FIRST_ERR_ROW], "sd": float(np.std(wf, ddof=1)),
                             "max": float(np.abs(wf).max())}
    # the same recipe, but only summer errors (from row 20 = mid-May): the trap
    wf20 = walk_forward_errors(train_f, X_COLS, first=20)
    half20 = float(np.quantile(np.abs(wf20), 0.9))
    F["band_summer_only"] = {"half": half20, "covered": covered(half20, pred), "from": train_f.index[20]}
    origin = len(tickets) - H
    rerr = rate_past_errors(tickets, origin, h=H)
    half_r = float(np.quantile(np.abs(rerr), 0.9))
    rate_fc = fc["rate_seasonal_naive"].values
    F["band_rate"] = {"half": half_r, "covered": covered(half_r, rate_fc), "n_errors": len(rerr),
                      "n_origins": len(rerr) // H}
    F["rate_interval_example"] = (rate_fc[0], rate_fc[0] - half_r, rate_fc[0] + half_r)

    # ---------------------------------------------------------------- W6D1 backtesting
    bt = walk_forward_mae(tickets, make_features, X_COLS)
    fa = make_features(tickets); n = len(fa); rows = []
    for k, c in enumerate(range(int(n * 0.5), n - 4, 4)):
        te = fa.iloc[c:c + 4]
        o = tickets.index.get_loc(te.index[0])
        rows.append({"fold_start": te.index[0], "regression": bt[k],
                     "naive": mae(te["tickets_lag1"], te["target"]),
                     "seasonal_naive": mae(te["tickets_lag52"], te["target"]),
                     "rate_seasonal_naive": mae(rate_seasonal_naive(y.iloc[:o], term.iloc[:o], 4), te["target"])})
    folds = pd.DataFrame(rows).set_index("fold_start")
    F["folds"] = folds
    F["fold_means"] = folds.mean().to_dict()
    F["naive_beats_reg"] = int((folds["naive"] < folds["regression"]).sum())
    F["rate_beats_naive"] = int((folds["rate_seasonal_naive"] < folds["naive"]).sum())
    F["worst_fold"] = folds["regression"].idxmax()
    names = ["naive", "seasonal_naive", "moving_average", "exp_smoothing", "rate_seasonal_naive", "training_mean"]
    F["horizons"] = {}
    for h in [1, 4, 8]:
        r = rolling_origin(tickets, {k: _blind(k) for k in names}, h)
        F["horizons"][h] = {"n": len(r), "mean": r.mean().to_dict(), "wins": r.idxmin(axis=1).value_counts().to_dict(),
                            "table": r}

    # ---------------------------------------------------------------- W6D2 remaining useful life
    known = degr.iloc[:TRAIN_DAYS]
    calls = {}
    for _, row in limits.iterrows():
        col = row["channel"]
        hit, model = day_of_threshold(known[col], row["threshold"], row["direction"])
        a, b = model.c
        calls[col] = {"asset": row["asset"], "threshold": float(row["threshold"]), "unit": row["unit"],
                      "day": hit, "date": _date(degr, hit), "slope_per_year": float(a * 365),
                      "unbounded_date": _date(degr, (row["threshold"] - b) / a),
                      "search_end": _date(degr, TRAIN_DAYS + 4000 - 1)}
        # the original's bug, reproduced: argmax on "never True" is 0
        y_future = model(np.arange(TRAIN_DAYS + 4000))
        calls[col]["original_print"] = _date(degr, int(np.argmax(y_future < row["threshold"])))
    F["rul_calls"] = calls
    bat = degr["battery_capacity_pct"]
    F["battery_cross"] = crossing_dates(bat, 80.0)
    F["battery_daily_below_in_window"] = int((bat.loc[F["battery_cross"]["first_dip"]:F["battery_cross"]["last_good_day"]] < 80).sum())
    F["battery_window_days"] = len(bat.loc[F["battery_cross"]["first_dip"]:F["battery_cross"]["last_good_day"]])
    F["battery_slope_by_year"] = {yr: float(np.polyfit(np.arange(len(bat[str(yr)])), bat[str(yr)].values, 1)[0] * 365)
                                  for yr in range(2021, 2026)}
    first_dip = F["battery_cross"]["first_dip"]; sustained = F["battery_cross"]["30_day_mean"]
    rep = []
    for years in [1, 2, 3, 4]:
        nd = 365 * years
        hit, _ = day_of_threshold(bat.iloc[:nd], 80.0)
        call = _date(degr, hit)
        rep.append({"years_of_data": years, "call_made_on": degr.index[nd], "predicted_crossing": call,
                    "days_vs_first_dip": (call - first_dip).days, "days_vs_30_day_mean": (call - sustained).days,
                    "warning_days": (first_dip - degr.index[nd]).days})
    F["battery_repeat"] = pd.DataFrame(rep)
    e = degr["eclipse_flag"]; db = bat.diff().dropna(); ee = e.loc[db.index]
    F["eclipse_share_days"] = float(ee.mean()); F["eclipse_share_fade"] = float(db[ee == 1].sum() / db.sum())
    F["eclipse_fade_ratio"] = float(db[ee == 1].mean() / db[ee == 0].mean())
    F["eclipse_seasons"] = ("27 Feb", "13 Apr", "1 Sep", "16 Oct")
    for col in ["twta_gain_db", "propellant_kg"]:
        thr = float(limits.set_index("channel").loc[col, "threshold"])
        reps = []
        for years in [1, 2, 3, 4, 5]:
            s = degr[col].iloc[:365 * years]
            model, (a, b) = fit_trend(s)
            reps.append(_date(degr, (thr - b) / a))
        F[f"{col}_repeat"] = reps
    p = degr["propellant_kg"]
    fwd = p[::-1].rolling(5).median()[::-1].shift(-1); bwd = p.rolling(5).median()
    jump = (fwd - bwd)[lambda s: s < -0.2].sort_values()
    burns = []
    for t0, v in jump.items():
        if all(abs((t0 - t1).days) >= 7 for t1, _ in burns):
            burns.append((t0, v))
    burns = pd.Series(dict(burns)).sort_index()
    F["burns"] = {"n": len(burns), "per_year": float(len(burns) / (len(p) / 365)), "kg_each": float(-burns.mean()),
                  "days_between": float(pd.Series(burns.index).diff().dt.days.median())}
    F["prop_last"] = float(p.iloc[-1]); F["prop_reserve"] = 5.0
    F["prop_kg_per_year"] = float((p.iloc[0] - p.iloc[-1]) / (len(p) - 1) * 365)
    F["prop_years_left"] = (F["prop_last"] - 5.0) / F["prop_kg_per_year"]
    F["prop_gauge_date"] = degr.index[-1] + pd.Timedelta(days=F["prop_years_left"] * 365.25)
    F["degr_span"] = (degr.index[0], degr.index[-1], len(degr))
    return F


if __name__ == "__main__":
    import sklearn
    F = facts()
    pd.set_option("display.width", 200)
    d = lambda t: t.strftime("%d %b %Y") if t is not None else "None"
    print("sklearn", sklearn.__version__, "pandas", pd.__version__)
    print(f"tickets {F['n_weeks']} weeks {d(F['first_week'])} - {d(F['last_week'])}, gaps {F['gaps']}, terminals "
          f"{F['term_first']} -> {F['term_last']}, tickets {F['y_min']}-{F['y_max']}, mean by year {F['y_mean_by_year']}")
    print("W5D2 hold-out", d(F["holdout"][0]), "-", d(F["holdout"][1]))
    print(F["fc"].round(1))
    print("  MAE", {k: round(v, 2) for k, v in F["baseline_mae"].items()}, "| training mean", round(F["training_mean_mae"], 2))
    print("  terminals at origin", F["term_origin"], "a year before", F["term_year_before"], "| SN copies", F["sn_source"],
          "| last train week", d(F["last_train_week"][0]), F["last_train_week"][1])
    print("  rate per 1000 terminals by month (training weeks):"); print(F["rate_by_month"])
    print(f"  rainy {F['rate_rainy']:.1f} dry {F['rate_dry']:.1f} lift {F['rainy_lift']:.1%} | Nov {F['rate_nov']:.1f} Dec {F['rate_dec']:.1f} | steps {F['season_steps']}")
    print("W5D3 features", F["feat_rows"], "lost", F["rows_lost"], "train", d(F["train_f"][0]), d(F["train_f"][1]), F["train_f"][2])
    print("  coef", {k: round(v, 4) for k, v in F["coef"].items()}, "intercept", round(F["intercept"], 2))
    print("  reg MAE", round(F["reg_mae"], 2), "one-step naive", round(F["onestep_naive_mae"], 2))
    print("  reg errors", F["reg_err"].round(1).tolist(), "sd", round(F["reg_err_sd"], 2), "mean", round(F["reg_err_mean"], 2))
    print("  resid sd", round(F["resid_sd"], 3), "band in-sample", {k: round(v, 2) for k, v in F["band_insample"].items()})
    print("  band walk-forward", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in F["band_walkforward"].items()})
    print("  band summer-only", F["band_summer_only"])
    print("  band rate", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in F["band_rate"].items()},
          "example", np.round(F["rate_interval_example"], 1))
    print("W6D1 folds"); print(F["folds"].round(2))
    print("  means", {k: round(v, 2) for k, v in F["fold_means"].items()}, "naive beats reg", F["naive_beats_reg"],
          "rate beats naive", F["rate_beats_naive"], "worst", d(F["worst_fold"]))
    for h, v in F["horizons"].items():
        print(f"  h={h}: {v['n']} origins, mean", {k: round(x, 2) for k, x in v["mean"].items()}, "wins", v["wins"])
    print("W6D2 span", d(F["degr_span"][0]), d(F["degr_span"][1]), F["degr_span"][2])
    for col, c in F["rul_calls"].items():
        print(f"  {col}: day {c['day']} -> {d(c['date'])} | original prints {d(c['original_print'])} | slope/yr {c['slope_per_year']:.4f}"
              f" | line crosses {d(c['unbounded_date'])} | search ends {d(c['search_end'])}")
    print("  battery crossing", {k: d(v) for k, v in F["battery_cross"].items()}, "below in window",
          F["battery_daily_below_in_window"], "of", F["battery_window_days"])
    print("  battery slope by year", {k: round(v, 2) for k, v in F["battery_slope_by_year"].items()})
    print(F["battery_repeat"])
    print(f"  eclipse: {F['eclipse_share_days']:.1%} of days, {F['eclipse_share_fade']:.1%} of fade, {F['eclipse_fade_ratio']:.2f}x per day")
    print("  twta repeat", [d(t) for t in F["twta_gain_db_repeat"]])
    print("  prop repeat", [d(t) for t in F["propellant_kg_repeat"]])
    print("  burns", F["burns"], "| prop last", F["prop_last"], "kg/yr", round(F["prop_kg_per_year"], 2), "years left",
          round(F["prop_years_left"], 2), "gauge date", d(F["prop_gauge_date"]))
