# Review of the Original Materials (instructor eyes only)

I read every file in `Time-series/` and **ran all four code books from top to bottom** in two clean environments: pandas **2.2.2** (the version Colab has shipped recently) and pandas **3.1.0** (the newest). This page lists what's good, what's missing for beginners, and what is broken. Nothing in the originals has been changed.

---

## The verdict in one paragraph

The originals were made by someone who really knows the subject. The synthetic data is designed around NigComSat-1R itself (42.5°E, eclipse seasons, Ka-band rain fade, 28 transponders, Nigeria's six geopolitical zones), and the habits it teaches (honest evaluation, splitting by time, comparing with a baseline) are professional-grade. But the code books are **reference manuals, not lessons**. Most of the techniques the quizzes test have **no code anywhere in the repo**. There are **no exercises and no slides**, the notebooks **won't load data in Colab** as written, **three of the four crash outright on the newest pandas**, and **three contain bugs or results that contradict their own text**. The content is sound. What's missing is the packaging for beginners and the fixes.

---

## ✅ What's genuinely good, and we keep it

| Strength | Where |
|---|---|
| Realistic data built around the real satellite: eclipse at 21:00 UTC, rainy-season dips, weekend NOC rhythm, 6 geopolitical zones | all `data/` folders |
| "What to read in the output" notes after almost every cell. Great teaching habit | all code books |
| Answer keys (label files) let participants *score* detectors instead of arguing about them | `week-04/data`, `week-05/data` |
| Honest-evaluation mindset: event-level scoring, temporal splits, embargo, backtesting, "recommend the simpler model if it wins" | Weeks 4–6 |
| 120 scenario-based quiz questions, tagged beginner/intermediate/advanced, CSV and JSON agree | `MCQ/` |
| A capstone with a clear 100-point rubric tied to real NIGCOMSAT units | `module-project/` |

---

## ⚠️ Gaps for a Python-only audience

1. **Code books describe data; they don't teach techniques.** Week 3's quizzes cover rolling windows, decomposition and correlograms, but the Week 3 notebook only profiles the files. Week 4 has no control chart, residual detector or CUSUM code. Week 5 has no clustering code. We write all of that.
2. **No exercises.** Everything is a demo to read. Nothing asks participants to *do* anything.
3. **No slides, no instructor notes.**
4. **Weeks 1–2 are missing.** The folders start at `week-03`, and the text refers to "the Week 2 data restrictions", which participants will never have seen.
5. **Jargon is never explained for non-satellite people:** TWTA, C/N, SoC, DoD, CUSUM, embargo, lag, residual, contamination…
6. **Not Colab-ready.** `DATA = Path("data")` assumes the CSVs sit beside the notebook. In Colab, nothing loads.
7. **The capstone assumes a Publica training server** (Streamlit or cron deployment, max 5 concurrent users). Colab can't provide that.

---

## 🐞 Bugs and contradictions, verified by running the code

### Will break live

| # | Where | What happens | Our fix (originals untouched) |
|---|---|---|---|
| 0 | **Weeks 3, 4 and 5**, on **pandas 3** | They use the old hourly code `"H"` (`.asfreq("H")`). Pandas 3 removed it: `ValueError: Invalid frequency: H` at the first hourly file. Week 3 loses 3 sections, Week 4 loses its first detector, and **Week 5 fails completely** (every cell after setup). On pandas 2.2 they run, with warnings. Whether you hit this depends on Colab's pandas version on the day: check with `import pandas; pandas.__version__` | Ours use `"h"` and `"D"` and are tested on both 2.2 and 3.1 |
| 1 | **Week 4**, section *5. Anomaly ground truth* | `telemetry_anomaly_labels.csv` crashes on load (`ParserError: Expected 8 fields in line 5, saw 9`). Row EV04's cause text, *"Transient thermal excursion, cause not recorded"*, contains an unquoted comma. The scorer cell below then fails with `NameError: labels`. | Our notebooks repair that row when loading the file |
| 2 | **Week 5**, *Proving EV02 is univariately invisible* | The code checks **1 May**, but the label file (and the data) put EV02 on **2 May**. The output shows state of charge at a perfectly normal 100%, the opposite of what the text says it should show. The event table also says "1 May" and "29 Jun" where the data says 2 May and 30 Jun. | Use the dates from the label file |
| 3 | **Week 5**, *The detector* → *The honest comparison* | **The headline result does not reproduce.** The text promises that the Isolation Forest catches all 5 faults and the control chart catches 2. When run, the Isolation Forest catches **1 of 5** with 25 false alarms, and its "ten most anomalous hours" are all **normal eclipse hours** (21:00 in September). The control chart catches **5 of 5** (with 291 false alarms). Taught as written, the lesson argues against itself. | W4D2–W5D1 teach a detector checked on the data first: steady-sunlight context plus one relationship feature, `temp_per_drive`. On the held-out months (Sep–Dec) a 3σ chart on those features catches both events with **1** false alarm; the forest on the same features catches both with **25**. The days teach the honest verdict: recommend the simpler detector |
| 4 | **Week 6**, *Topic 6.4 RUL* | Propellant's predicted crossing date prints as **2021-01-01**, the first day of the data. `np.argmax` returns 0 when the trend never crosses the limit in the search window. | W6D2's `day_of_threshold` returns `None`, so it says "no crossing before 13 Dec 2034" (where the search ends). Extending the line gives **6 Dec 2035**, and the fuel-gauge sum (96.9 kg above the reserve ÷ 9.6 kg a year) agrees: about Jan 2036 |

### Will confuse people

| # | Where | Text says | Code actually outputs |
|---|---|---|---|
| 5 | Week 4, *1. Bus power* | sunlit sd ≈ 0.06 A, 3σ band 27.6–28.0 A | sd **0.594 A**, band **26.43–29.99 A** |
| 6 | Week 4, *4. RF link quality* | naive 3σ rule flags "roughly all 56 rainy hours", 79% false alarms | flags **18** hours, **12** of them real (33% false alarms) |
| 7 | Week 4, *3. Battery health* | fade −2.4 → −4.0 Ah/year | **−2.24 → −3.68** Ah/year |
| 8 | Week 3, *B7. Bandwidth* | lag-1 autocorrelation ≈ 0.83 | **0.58** (lag 7 is 0.99, so the main point still holds) |
| 9 | Week 3, *A4. TWTA* | after differencing, correlation "collapses" | **0.59 → 0.40**. It drops, but it doesn't collapse |
| 10 | Week 3, *B5 / B3* | weekly ticket mean ≈ 38; utilisation reaches "the low 80s" | mean **36.4**; utilisation peaks at **77.6%** |
| 11 | Week 3, *A1. Bus power* | "Four injected events" | lists **three** (matches the Week 4 label file) |
| 12 | Week 6, throughout | — | **38 lines of garbled characters** (`â€"` instead of `—`), an encoding accident |
| 12a | Week 3, *B6. VSAT uptime* | South South "starts lowest **and** falls furthest" | South South does start lowest, but indexed to week 1 **South East** falls furthest (98.2 vs South West 98.3, South South 98.5) |
| 12b | Week 3, *B1. Ka-band daily* | trend ≈ +0.05 points a year | about **+0.08** a year |
| 12c | Week 4, *1. Bus power* + Week 4 quiz Q2 | an SoC floor of 82% "fires on all 46 eclipse hours" | it fires on **18** (eclipse SoC ranges 77.3–99.6%). It's an array-current floor, or a 3σ chart on all hours, that fires on all 46 |
| 12d | Week 4 quiz Q23 | battery fade rate "roughly doubles" in April 2025 | −2.24 → −3.68 Ah/yr: about **1.6×** |
| 12e | Week 4, *2. TWTA* | the 12 May level shift is "invisible to a single-point 3σ rule" | true on the raw temperature and for rolling detectors, but a fixed-recipe residual (temperature vs drive + season, fitted on 2024) flags every day after the shift |
| 12f | `bus_power_telemetry_hourly` | — | **Data quirk:** 1 Sep 00:00 reads 29.48 A (a recharge-sized value) with no eclipse flagged before it. It's the one false alarm of a well-tuned control chart; W3D2's notes explain it |
| 12g | Week 5 label file + *Why three of these defeat Week 4* | EV02 and EV05 are `detectable_univariately = no` | Only true for **array current**, the one channel the proof checks. A sunlit-only 3σ chart on **bus voltage** (normal 50.40 ± 0.04 V, faults 50.12–50.24 V) catches both with **0** false alarms, and a plain 3σ chart on state of charge (lower limit 93.8%) catches both too. Only **EV04** truly needs two channels. Quiz Q8 ("Two") follows the label file |
| 12h | Week 5, *Proving EV04 needs a derived feature* | residual sd ≈ 0.18 °C, EV04 ≈ 3.9 °C ≈ **22σ** | The code's own recipe gives sd **0.162 °C**, EV04 **4.68 °C** = **28.9σ**. And the same feature, carried to the rest of the year, flags **all 2,208 hours of Oct–Dec**: five months can't separate the amplifier's yearly warming trend (about +3.7 °C a year in this file) from the sun-angle season. Impressive on the fault, useless in service. The plain ratio `temp_per_drive` is humbler (EV04 ≈ 3.9σ) but stays stable all year. Quiz Q18 follows the text |
| 12i | Week 5, *Setup* + quiz Q4 | the 0–29.8 vs 77–100 ranges are "why topic 1 insists on scaling" | Scaling changes **nothing** for an isolation forest: its scores with and without `StandardScaler` correlate 0.99999999. It matters for distance methods such as k-means. Q4's option "It does not matter for isolation forest" is also true |
| 12j | Week 5, *The feature matrix* | 32 trailing features | `soc_gap` is exactly `100 − battery_soc_pct` (correlation 1.000) and **18** pairs sit above 0.98, the code book's own pruning line, yet it fits on all of them. On steady-sunlight hours this 32-column forest misses EV01 and EV03 (the obvious 11 A dropouts) and raises about 70 false alarms; five chosen features catch all 5 |
| 12k | Week 5, *The detector* | "ten most anomalous hours should cluster in the labelled event windows"; scorer run on `F` | All ten are 21:00 eclipse hours. The forest's one "catch" (EV04) comes from September eclipse hours that happen to sit inside EV04's four-week window: a lucky catch. And the score covers the whole year, including the training months, so it isn't a held-out result |
| 12l | `bus_telemetry_multivariate_hourly` | — | **Data quirk:** the same 1 Sep 00:00 hour as 12f: 28.90 A and battery 21.8 °C (recharge values) with no eclipse flagged before it. It's one of the three false alarms of the W5D1 chart; the other two are the battery still recovering in the hour after EV02 and EV05 |

| 12m | Week 6, *the three files* + *`ops_tickets_weekly.csv`* | 104 weeks "2024-01-01 to 2025-12-29"; tickets range "from the high-20s to the mid-70s" | The last week is **22 Dec 2025** (104 Mondays). Tickets run **28–80** |
| 12n | Week 6, *Topic 6.1* | the four baselines are the bar; seasonal naive loses because it "misses that the network has since grown" | The numbers are right (naive 11.25, exponential smoothing 12.80, moving average 14.25, seasonal naive 15.25), but the code book never takes the obvious next step. **Tickets per terminal repeat almost exactly each year** (January 25.6 vs 25.9 per 1,000 terminals, April 39.4 vs 39.2…), so last year's rate × today's network forecasts all 8 weeks blind with **MAE 2.24**: better than every baseline and better than the one-week-ahead regression (5.85). Backtested from every 2025 week it wins 4 and 8 weeks ahead (3.21 / 3.18 vs naive 5.03 / 6.20) and ties naive one week ahead (3.29 vs 3.19). Also: on this one split even the flat training mean (7.77) beats all four baselines, yet backtested it is the worst (16.50). W5D2 and W6D1 teach both |
| 12o | Week 6, *Topic 6.3* | the band covers "about 6 of the 8 held-out weeks"; `z = 1.645` is "one-sided-flavoured but used two-sided" | It covers **5 of 8** (the quiz says 5). And 1.645 *is* the two-sided 90% value (5% in each tail). The main miss is the 3 Nov season step (−21 tickets): the model says 70.9, the week is 53. A smooth sin/cos wave can't make a step. A band built from walk-forward misses since late March covers 7 of 8 weeks; the same recipe on summer weeks only covers 2 of 8 (W5D3) |
| 12p | Week 6, *Topic 6.5*, battery check | the four-year call "goes a few days late"; the real crossing is 14 May 2025 | 14 May is the **first single day** below 80%. Daily readings bounce back above 80% until **24 Jul** (49 of those 72 days are below), and the 30-day mean crosses on **20 Jun**. Against that, all four calls are early (by 111, 74, 50 and 33 days). They're early because the fade slows every year (−4.81 → −4.34 % a year). Quiz Q29 uses the single-day definition; its answer stands (W6D2) |

### Traps in the data files

| # | File(s) | The trap |
|---|---|---|
| 13 | `battery_health_daily.csv`, `twta_thermal_daily.csv` | **Same name, different content** in `week-03/data` and `week-04/data`. Only the Week 4 versions contain the injected faults. Load the Week 3 copy for a Week 4 exercise and the detector "finds nothing". |
| 14 | `week-03/data/link_margin_hourly_aug2025.csv` | 720 rows, **documented nowhere**, and different from the link-margin column in `rf_link_quality_hourly.csv`. |
| 15 | Every notebook | `asfreq("H")` and `tol="1H"` print deprecation warnings on pandas 2.2 and **crash on pandas 3** (see bug 0). Ours use `"h"`. |

### Quiz and answer-key issues

| # | Issue | Our fix |
|---|---|---|
| 16 | **89 of 120 correct answers are option B (74%).** Anyone who always picks B scores about 74%. | Shuffled-option versions for Google Forms (originals kept). The weekly banks in `week-N/MCQ/` spread the answers evenly too |
| 16a | **Week 3 quiz, autocorrelation topic, last question**: says the amplifier-temperature vs RF-drive correlation "largely collapses" after differencing | On the real file it only drops from 0.59 to 0.40. The idea is still taught (W2D2 uses a clear made-up example), so Quiz 1 and the Week 2 bank (`week-2/MCQ/`) ask it with the suya example instead (0.97 → 0.06) |
| 16b | **Week 5 quiz, Q4, Q8 and Q18** follow the code book's text: Q4 (scaling) has a second true option, Q8 says two events are single-channel detectable (the data says four, see 12g), Q18 says "about 22 sigma" (the recipe gives 28.9σ and fails on Oct–Dec, see 12h) | Corrected in Quiz 3 and in the Week 4 bank (`week-4/MCQ/`): Q4 now asks about k-means, Q8's answer is "Four", Q18 uses 28.9σ and asks why the feature fails in service. W5D1's instructor notes explain each |
| 16c | **Week 6 quiz** | All 30 answers match the data (11.25, 15.25, 6.75, 2.84, 5 of 8, 1 May 2025, 13 days early, 1.27–7.67, naive 5 of 6). Q29 measures the battery call against the first single-day dip; W6D2 teaches that a crossing is a window |
| 16d | **Week 4 quiz, Q2 and Q23** repeat the code book's errors 12c and 12d ("all 46 eclipse hours", "roughly doubled") | Corrected in Quiz 2 and in the Week 3 bank (`week-3/MCQ/`): 18 firings, and −2.2 → −3.7 Ah a year |
| 17 | The repo is **public**, and the answer keys (label CSVs, "answer key" notes in the code books) are in it. Participants who browse the repo can see them. | Keep in mind when setting graded exercises |

---

## What I didn't review

`MODULE-01`, `MODULE-04`, `MODULE-05` and `shared/` are LLM/agent modules from a different track. I only checked that they're unrelated to time series.
