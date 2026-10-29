"""The Week 5 detector story, shared by W4D2, W4D3 and W5D1.

The original Week 5 code book's headline result does not reproduce (see 01-REVIEW-OF-ORIGINALS.md, bug 3),
so these three days teach a detector that was designed and checked on the real file first:

  W4D2  a forest on the raw channels flags only eclipse hours ("rare is not broken");
        judging steady-sunlight hours only fixes most of it; k-means finds the operating modes.
  W4D3  one relationship feature, temp_per_drive, makes EV04 visible; more features is not better eyes.
  W5D1  honest split, then a fair fight on the same hours with the same scorer: the 3-sigma chart on the
        same features beats the forest, so we recommend the simpler detector.

The notebook code lives here as strings (SCORER_CODE, DETECTOR_CODE) and the build runs those exact strings,
so every number on a slide comes from the same code the participants run.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from common import ORIGINALS, read_labels

D5 = ORIGINALS / "week-05" / "data"
RAW = ["solar_array_current_a", "bus_voltage_v", "battery_soc_pct", "battery_temp_c", "twta_temp_c", "rf_drive_pct"]
HEALTH = RAW[:5]                       # rf_drive_pct is the load we command, not a health reading
LEAN = ["solar_array_current_a", "bus_voltage_v", "battery_soc_pct", "battery_temp_c", "temp_per_drive"]
SEED = 42
CONTAMINATION = 0.005
TRAIN_END = "2025-09-01"              # training = every hour before this (Jan to Aug)
TEST_START = "2025-09-02"             # 1 Sep is the 24-hour embargo (the longest feature window)

# ----------------------------------------------------------------------------- notebook code (run here too)
SCORER_CODE = '''def score_events(flags, labels, tol="1h"):
    """Event-level scoring, the same 4 rules as Week 4 Day 1. flags: a True/False Series with a time index.
    Events that fall outside the hours being scored are skipped."""
    tol = pd.Timedelta(tol)
    n_events, caught, inside_any = 0, 0, pd.Series(False, index=flags.index)
    for _, ev in labels.iterrows():
        window = (flags.index >= ev["start"] - tol) & (flags.index <= ev["end"] + tol)
        if not window.any():
            continue                     # this event is not in the hours being scored
        n_events += 1
        if flags[window].any():          # one flag or many = ONE catch
            caught += 1
        inside_any |= window
    false_alarms = int((flags & ~inside_any).sum())
    alarms = caught + false_alarms
    return {"events": n_events, "caught": caught, "false_alarms": false_alarms,
            "recall": round(caught / n_events, 3) if n_events else float("nan"),
            "precision": round(caught / alarms, 3) if alarms else float("nan")}

def event_table(flags, labels):
    """One row per event: caught? how many hours late was the first flag? how many of its hours lit up?"""
    rows = []
    for _, ev in labels.iterrows():
        inside = (flags.index >= ev["start"]) & (flags.index <= ev["end"])
        if not inside.any():
            continue
        window = (flags.index >= ev["start"] - pd.Timedelta("1h")) & (flags.index <= ev["end"] + pd.Timedelta("1h"))
        hits = flags[window]
        first = hits[hits].index.min() if hits.any() else None
        rows.append({"event": ev["event_id"], "type": ev["type"], "caught": bool(hits.any()),
                     "hours_late": None if first is None else int((first - ev["start"]) / pd.Timedelta("1h")),
                     "hours_flagged": int(flags[inside].sum()), "hours_long": int(inside.sum())})
    return pd.DataFrame(rows).set_index("event").astype({"hours_late": "Int64"})'''

DETECTOR_CODE = '''def steady_sun(bus):
    """True in steady sunlight: no eclipse this hour or in the 3 hours before.
    Eclipse (battery power) and the 3 recharge hours after it are normal states with their own normal."""
    return bus["eclipse_flag"].rolling(4).max() == 0

def lean_features(bus):
    """Four health channels plus ONE relationship: amplifier temperature per % of RF drive."""
    X = bus[["solar_array_current_a", "bus_voltage_v", "battery_soc_pct", "battery_temp_c"]].copy()
    X["temp_per_drive"] = bus["twta_temp_c"] / bus["rf_drive_pct"]
    return X

def chart_flags(X, fit_rows, judge_rows, k=3):
    """Week 4 control chart on every column: flag the hour if ANY column is more than k sigma from its normal."""
    ref = X[fit_rows]
    z = (X - ref.mean()) / ref.std()
    return (z.abs() > k).any(axis=1) & judge_rows

def forest_flags(X, fit_rows, judge_rows, contamination=0.005, seed=42):
    """Isolation forest, fitted on the reference rows only, judging the chosen rows."""
    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=seed)
    model.fit(X[fit_rows])
    return pd.Series(model.predict(X) == -1, index=X.index) & judge_rows'''

from sklearn.ensemble import IsolationForest  # noqa: E402  (the notebook code expects it in scope)

exec(SCORER_CODE)
exec(DETECTOR_CODE)


def make_features_orig(df):
    """The original code book's 32-column 'kitchen sink' builder (trailing windows only)."""
    f = pd.DataFrame(index=df.index)
    for c in ["solar_array_current_a", "battery_soc_pct", "twta_temp_c", "bus_voltage_v"]:
        f[c] = df[c]
        f[f"{c}_lag1"] = df[c].shift(1)
        f[f"{c}_lag24"] = df[c].shift(24)
        f[f"{c}_d1"] = df[c].diff(1)
        f[f"{c}_mean24"] = df[c].rolling(24).mean()
        f[f"{c}_std24"] = df[c].rolling(24).std()
        f[f"{c}_dev24"] = df[c] - f[f"{c}_mean24"]
    f["temp_per_drive"] = df["twta_temp_c"] / df["rf_drive_pct"]
    f["soc_gap"] = 100 - df["battery_soc_pct"]
    f["eclipse_flag"] = df["eclipse_flag"]
    f["hour"] = df.index.hour
    return f.dropna()


def load():
    bus = pd.read_csv(D5 / "bus_telemetry_multivariate_hourly.csv", parse_dates=["timestamp"],
                      index_col="timestamp").asfreq("h")
    return bus, read_labels(D5 / "anomaly_labels_week5.csv")


def _res(flags, labels, test_only=False):
    f = flags.loc[TEST_START:] if test_only else flags
    out = score_events(f, labels)
    out["table"] = event_table(f, labels)
    out["which"] = [e for e, r in out["table"].iterrows() if r["caught"]]
    return out


@lru_cache(maxsize=1)
def facts():
    """Every number the three days show. Computed from the original data, never typed in."""
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import TimeSeriesSplit, train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    bus, labels = load()
    F: dict = {"bus": bus, "labels": labels}
    idx = bus.index
    ecl = bus["eclipse_flag"] == 1
    steady = steady_sun(bus)
    recharge = ~ecl & ~steady & (idx >= idx[3])          # the 3 hours after an eclipse
    train = pd.Series(idx < TRAIN_END, index=idx)
    test = pd.Series(idx >= TEST_START, index=idx)
    every = pd.Series(True, index=idx)
    ev04 = (idx >= "2025-09-03") & (idx < "2025-10-01")
    F.update(ecl=ecl, steady=steady, recharge=recharge, train=train, test=test, ev04_mask=ev04)
    F["n_rows"], F["n_eclipse"], F["n_steady"], F["n_recharge"] = len(bus), int(ecl.sum()), int(steady.sum()), int(recharge.sum())
    F["n_train"], F["n_test"], F["n_embargo"] = int(train.sum()), int(test.sum()), int((~train & ~test).sum())
    F["ranges"] = bus[RAW].agg(["min", "max"]).T
    F["corr_sunlit"] = bus.loc[~ecl, RAW].corr()

    # --- the dates the original got wrong
    ev02 = bus.loc["2025-05-02 01:00":"2025-05-02 12:00"]
    F["ev02_array"] = (ev02["solar_array_current_a"].min(), ev02["solar_array_current_a"].max())
    F["ev02_soc"] = (ev02["battery_soc_pct"].min(), ev02["battery_soc_pct"].max())
    F["ev02_volt"] = (ev02["bus_voltage_v"].min(), ev02["bus_voltage_v"].max())
    F["may1_soc"] = bus.loc["2025-05-01 01:00":"2025-05-01 12:00", "battery_soc_pct"].agg(["min", "max"]).tolist()

    # ============ W4D2: forest on raw channels, then context, then k-means
    raw = bus[RAW]
    f_all = forest_flags(raw, train, every)
    F["w4d2_raw_all"] = _res(f_all, labels)
    F["w4d2_raw_all_n"] = int(f_all.sum())
    F["w4d2_raw_all_hours"] = f_all[f_all].index.hour.value_counts().to_dict()
    F["w4d2_raw_all_eclipse"] = int((f_all & ecl).sum())
    model = IsolationForest(n_estimators=200, contamination=CONTAMINATION, random_state=SEED).fit(raw[train])
    score = pd.Series(model.decision_function(raw), index=idx)
    F["w4d2_top10"] = score.nsmallest(10)
    F["w4d2_score"] = score
    F["w4d2_raw_all_flags"] = f_all
    f_st = forest_flags(raw, train & steady, steady)
    F["w4d2_raw_steady"] = _res(f_st, labels)
    F["w4d2_raw_steady_flags"] = f_st
    F["w4d2_raw_steady_fa_months"] = f_st[f_st & ~_inside(labels, idx)].index.month.value_counts().sort_index().to_dict()
    F["chart_raw_steady"] = _res(chart_flags(bus[HEALTH], train & steady, steady), labels)
    # scaling: irrelevant to a forest, essential to k-means
    a = IsolationForest(n_estimators=200, random_state=SEED).fit(raw).decision_function(raw)
    b = make_pipeline(StandardScaler(), IsolationForest(n_estimators=200, random_state=SEED)).fit(raw).decision_function(raw)
    F["if_scale_corr"] = float(np.corrcoef(a, b)[0, 1])
    state = pd.Series(np.select([ecl, recharge], ["eclipse", "recharge"], "steady sun"), index=idx)
    km_s = make_pipeline(StandardScaler(), KMeans(4, n_init=10, random_state=SEED)).fit_predict(raw)
    km_u = KMeans(4, n_init=10, random_state=SEED).fit_predict(raw)
    F["kmeans_scaled"] = pd.crosstab(pd.Series(km_s, index=idx, name="cluster"), state)
    F["kmeans_unscaled"] = pd.crosstab(pd.Series(km_u, index=idx, name="cluster"), state)

    # ============ W4D3: features
    tw = bus["twta_temp_c"]
    ref = tw[train & steady]
    F["twta_ceiling"], F["twta_ev04_max"] = ref.mean() + 3 * ref.std(), tw[ev04].max()
    X = lean_features(bus)
    tpd = X["temp_per_drive"]
    r = tpd[train & steady]
    F["tpd_mean"], F["tpd_sd"], F["tpd_ceiling"] = r.mean(), r.std(), r.mean() + 3 * r.std()
    F["tpd_ev04_mean"] = tpd[ev04].mean()
    F["tpd_ev04_z"] = (tpd[ev04].mean() - r.mean()) / r.std()
    F["tpd_monthly"] = tpd[steady].resample("MS").mean()
    tpd_flags = chart_flags(X[["temp_per_drive"]], train, every)
    F["tpd_chart_all"] = _res(tpd_flags, labels)
    # the code book's "22 sigma" regression feature: big on the fault, wrong on months it never saw
    doy = idx.day_of_year
    design = pd.DataFrame({"drive": bus["rf_drive_pct"], "sin": np.sin(2 * np.pi * doy / 365),
                           "cos": np.cos(2 * np.pi * doy / 365)}, index=idx)
    fit = idx < "2025-06-01"
    lr = LinearRegression().fit(design[fit], tw[fit])
    resid = tw - lr.predict(design)
    rs = resid[fit].std()
    F["resid_sd"], F["resid_ev04_sigma"] = rs, (resid[ev04].mean() - resid[fit].mean()) / rs
    rflags = (resid - resid[fit].mean()).abs() > 3 * rs
    F["resid_year"] = _res(rflags, labels)
    F["resid_octdec"] = (int(rflags.loc["2025-10-01":].sum()), len(rflags.loc["2025-10-01":]))
    F["resid_monthly"] = resid.resample("MS").mean()
    # kitchen sink vs lean
    K = make_features_orig(bus)
    F["sink_shape"], F["sink_rows_lost"] = K.shape, len(bus) - len(K)
    c = K.corr().abs()
    pairs = c.where(np.triu(np.ones(c.shape), k=1).astype(bool)).stack().sort_values(ascending=False)
    F["sink_pairs"], F["sink_n_dupes"] = pairs.head(8), int((pairs > 0.98).sum())
    ks, kt = steady.reindex(K.index), train.reindex(K.index)
    f_sink = forest_flags(K, kt & ks, ks).reindex(idx, fill_value=False)
    F["sink_forest"] = _res(f_sink, labels)
    f_lean = forest_flags(X, train & steady, steady)
    F["lean_forest"] = _res(f_lean, labels)
    F["lean_forest_flags"] = f_lean
    ref = X[train & steady]
    F["lean_z"] = (X - ref.mean()) / ref.std()

    # ============ W5D1: honest split, expo, fair fight, rolling origin
    y = pd.Series(0, index=idx)
    for _, ev in labels.iterrows():
        y.loc[ev["start"]:ev["end"]] = 1
    knn = lambda: make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))  # noqa: E731
    Xa, Xb, ya, yb = train_test_split(X, y, test_size=0.33, random_state=SEED)
    pr = knn().fit(Xa, ya).predict(Xb)
    F["expo_random"] = float((pr[yb.values == 1] == 1).mean()), int((yb == 1).sum())
    pt = knn().fit(X[train], y[train]).predict(X[test])
    F["expo_temporal"] = float((pt[y[test].values == 1] == 1).mean()), int((y[test] == 1).sum())
    F["expo_temporal_events"] = _res(pd.Series(pt == 1, index=idx[test]), labels)["which"]

    sunlit = ~ecl
    fight = {
        "Week 4 chart, raw channels, sunlit only (as taught)": chart_flags(bus[HEALTH], train & sunlit, sunlit),
        "Week 4 chart, raw channels, steady sun": chart_flags(bus[HEALTH], train & steady, steady),
        "Isolation forest, lean features, steady sun": f_lean,
        "Week 4 chart, lean features, steady sun": chart_flags(X, train & steady, steady),
    }
    F["fight"] = {k: _res(v, labels, test_only=True) for k, v in fight.items()}
    F["fight_year"] = {k: _res(v, labels) for k, v in fight.items()}
    F["fight_flags"] = fight
    lucky = fight["Week 4 chart, raw channels, sunlit only (as taught)"] & ev04
    F["lucky_hours"] = lucky[lucky].index.hour.value_counts().sort_index().to_dict()
    chart_lean = fight["Week 4 chart, lean features, steady sun"]
    F["chart_lean_fa_times"] = list(chart_lean[chart_lean & ~_inside(labels, idx)].index)
    seeds = {}
    for s in (42, 0, 1, 7, 123):
        seeds[s] = _res(forest_flags(X, train & steady, steady, seed=s), labels, test_only=True)["false_alarms"]
    F["forest_seed_fa"] = seeds
    folds = []
    for a_, b_ in TimeSeriesSplit(n_splits=4, gap=24).split(X):
        fa_ = pd.Series(False, index=idx)
        fa_.iloc[a_] = True
        fb_ = pd.Series(False, index=idx)
        fb_.iloc[b_] = True
        rc = score_events(chart_flags(X, fa_ & steady, steady & fb_)[fb_], labels)
        rf = score_events(forest_flags(X, fa_ & steady, steady & fb_)[fb_], labels)
        folds.append({"train": (idx[a_[0]], idx[a_[-1]]), "test": (idx[b_[0]], idx[b_[-1]]), "chart": rc, "forest": rf})
    F["folds"] = folds
    # a dirty reference period: fit on the whole year, EV04 included
    F["dirty_forest_ev04"] = int((forest_flags(X, steady, steady) & ev04).sum())
    F["dirty_chart_ev04"] = int((chart_flags(X, steady, steady) & ev04).sum())
    F["clean_forest_ev04"] = int((f_lean & ev04).sum())
    F["clean_chart_ev04"] = int((chart_lean & ev04).sum())
    F["ev04_hours"] = int(ev04.sum())
    return F


def _inside(labels, idx, tol="1h"):
    m = pd.Series(False, index=idx)
    for _, ev in labels.iterrows():
        m |= (idx >= ev["start"] - pd.Timedelta(tol)) & (idx <= ev["end"] + pd.Timedelta(tol))
    return m


if __name__ == "__main__":
    import sklearn
    F = facts()
    pd.set_option("display.width", 200)
    print("sklearn", sklearn.__version__, "pandas", pd.__version__)
    print(f"rows {F['n_rows']} · eclipse {F['n_eclipse']} · steady {F['n_steady']} · recharge {F['n_recharge']} · "
          f"train {F['n_train']} · embargo {F['n_embargo']} · test {F['n_test']}")
    print("EV02 (2 May): array", F["ev02_array"], "SoC", F["ev02_soc"], "volt", F["ev02_volt"], "| 1 May SoC", F["may1_soc"])

    def line(name, r):
        t = r["table"]
        cov = ", ".join(f"{e}:{int(t.loc[e, 'hours_flagged'])}/{int(t.loc[e, 'hours_long'])}"
                        f"@{t.loc[e, 'hours_late']}h" for e in r["which"])
        print(f"  {name:52s} caught {r['caught']}/{r['events']} fa {r['false_alarms']:4d}  [{cov}]")
    print("W4D2")
    line("forest raw6, all hours", F["w4d2_raw_all"])
    print("     flagged", F["w4d2_raw_all_n"], "eclipse", F["w4d2_raw_all_eclipse"], "hours", F["w4d2_raw_all_hours"])
    print("     top10", [t.strftime("%d %b %H:%M") for t in F["w4d2_top10"].index])
    line("forest raw6, steady sun", F["w4d2_raw_steady"])
    print("     FA months", F["w4d2_raw_steady_fa_months"])
    line("chart raw health5, steady sun", F["chart_raw_steady"])
    print("     IF scaled vs unscaled corr", round(F["if_scale_corr"], 8))
    print(F["kmeans_scaled"]); print(F["kmeans_unscaled"])
    print("W4D3")
    print(f"  twta ceiling {F['twta_ceiling']:.2f} vs EV04 max {F['twta_ev04_max']:.2f}")
    print(f"  tpd mean {F['tpd_mean']:.4f} sd {F['tpd_sd']:.4f} ceiling {F['tpd_ceiling']:.4f} EV04 mean {F['tpd_ev04_mean']:.4f} z {F['tpd_ev04_z']:.1f}")
    line("tpd chart alone, all hours", F["tpd_chart_all"])
    print(f"  resid feature: sd {F['resid_sd']:.3f}, EV04 {F['resid_ev04_sigma']:.1f} sigma, Oct-Dec flagged {F['resid_octdec']}")
    line("resid 3-sigma (code book recipe)", F["resid_year"])
    print("  sink", F["sink_shape"], "lost", F["sink_rows_lost"], "dupes>0.98", F["sink_n_dupes"]); print(F["sink_pairs"].round(3))
    line("forest kitchen sink 32, steady", F["sink_forest"])
    line("forest lean 5, steady", F["lean_forest"])
    print("W5D1")
    print("  expo random", F["expo_random"], "temporal", F["expo_temporal"], F["expo_temporal_events"])
    for k, v in F["fight"].items():
        line("TEST " + k, v)
    for k, v in F["fight_year"].items():
        line("YEAR " + k, v)
    print("  lucky EV04 hours (as-taught chart):", F["lucky_hours"])
    print("  chart lean FA times:", F["chart_lean_fa_times"])
    print("  forest seeds test FA:", F["forest_seed_fa"])
    for i, fo in enumerate(F["folds"], 1):
        print(f"  fold {i} {fo['train'][1]:%d %b} | {fo['test'][0]:%d %b}-{fo['test'][1]:%d %b}: chart {fo['chart']['caught']}/{fo['chart']['events']} fa {fo['chart']['false_alarms']} · forest {fo['forest']['caught']}/{fo['forest']['events']} fa {fo['forest']['false_alarms']}")
    print(f"  EV04 hours lit (of {F['ev04_hours']}): clean ref forest {F['clean_forest_ev04']} chart {F['clean_chart_ev04']} | dirty ref forest {F['dirty_forest_ev04']} chart {F['dirty_chart_ev04']}")
