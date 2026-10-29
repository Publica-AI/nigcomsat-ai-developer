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
| 3 | **Week 5**, *The detector* → *The honest comparison* | **The headline result does not reproduce.** The text promises that the Isolation Forest catches all 5 faults and the control chart catches 2. When run, the Isolation Forest catches **1 of 5** with 25 false alarms, and its "ten most anomalous hours" are all **normal eclipse hours** (21:00 in September). The control chart catches **5 of 5** (with 291 false alarms). Taught as written, the lesson argues against itself. | Rebuild the Week 5 demo so the multivariate detector actually earns its place (Step 4 of the plan) |
| 4 | **Week 6**, *Topic 6.4 RUL* | Propellant's predicted crossing date prints as **2021-01-01**, the first day of the data. `np.argmax` returns 0 when the trend never crosses the limit in the search window. | Report "no crossing within N years" instead |

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

### Traps in the data files

| # | File(s) | The trap |
|---|---|---|
| 13 | `battery_health_daily.csv`, `twta_thermal_daily.csv` | **Same name, different content** in `week-03/data` and `week-04/data`. Only the Week 4 versions contain the injected faults. Load the Week 3 copy for a Week 4 exercise and the detector "finds nothing". |
| 14 | `week-03/data/link_margin_hourly_aug2025.csv` | 720 rows, **documented nowhere**, and different from the link-margin column in `rf_link_quality_hourly.csv`. |
| 15 | Every notebook | `asfreq("H")` and `tol="1H"` print deprecation warnings on pandas 2.2 and **crash on pandas 3** (see bug 0). Ours use `"h"`. |

### Quiz and answer-key issues

| # | Issue | Our fix |
|---|---|---|
| 16 | **89 of 120 correct answers are option B (74%).** Anyone who always picks B scores about 74%. | Shuffled-option versions for Google Forms (originals kept) |
| 16a | **Week 3 quiz, autocorrelation topic, last question**: says the amplifier-temperature vs RF-drive correlation "largely collapses" after differencing | On the real file it only drops from 0.59 to 0.40. The idea is still taught (W2D2 uses a clear made-up example), and the instructor notes flag the question |
| 17 | The repo is **public**, and the answer keys (label CSVs, "answer key" notes in the code books) are in it. Participants who browse the repo can see them. | Keep in mind when setting graded exercises |

---

## What I didn't review

`MODULE-01`, `MODULE-04`, `MODULE-05` and `shared/` are LLM/agent modules from a different track. I only checked that they're unrelated to time series.
