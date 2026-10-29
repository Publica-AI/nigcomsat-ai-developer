# W4D3 Instructor Notes: Give the Model Eyes: Feature Engineering

> **The one idea for today:** *a model only sees the columns you give it. Give it history (past only), the operating state, and the relationships between sensors, and keep the columns few and sharp.* One good relationship column beats 32 raw ones.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours, including 20 minutes for the final-project Checkpoint 3 |
| **Participants leave able to** | build lag, difference and rolling features; apply the 14:00 test; build a relationship feature; check a feature on months it never saw; find and prune twin columns; explain a flag with z-scores |
| **Covers (original)** | Week 5 Code Book: *Proving EV02 is univariately invisible*, *Proving EV04 needs a derived feature*, *The feature matrix*, *Checking for near-duplicate features*; Week 5 quiz topic *feature engineering from time series* (Quiz 3, questions 16–22) |
| **Datasets** | `week-05/data/bus_telemetry_multivariate_hourly.csv`, `week-05/data/anomaly_labels_week5.csv` (both loaded by STEP 0) |
| **Files you need open** | animated slides, your **solution** notebook, the rule book PDF, the final-project checkpoint table |

## The day before: checklist

<ul class="check">
<li>Run the <b>solution</b> notebook top to bottom: 15 of 15 ✅ (under a minute; the forest cells take a few seconds each).</li>
<li>Re-read W4D2's ending: the forest in steady sun noticed EV04 on <b>1 hour of 672</b>, 615 hours late. Today starts from there.</li>
<li>Remind participants to bring their final-project method draft (Checkpoint 3), running on <b>their</b> data, on NIGCOMSAT systems.</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | NEPA brought light but the inverter isn't charging: EV02 on 2 May | 1–4 |
| 0:10 | **Why features** | Last time: EV04 seen on 1 hour of 672. The model cannot tell time; three kinds of eyes | 5–6 |
| 0:15 | **History** | Lags and rolling windows; the 14:00 test; 24 rows lost | 7–9 |
| 0:22 | **Relationships** | Raw temperature sleeps through EV04; `temp_per_drive` lights 605 hours; the 29σ trap | 10–13 |
| 0:32 | **Fewer, better** | 18 twin pairs; 32 columns vs 5; right answer, right reason | 14–17 |
| 0:38 | **Cliffhanger** | 5 of 5, but 40 false alarms and an exam it marked itself | 18 |
| 0:40 | **Hands-on** | Part A (15 min), Part B (20 min), Part C (20 min) | 20 |
| 1:35 | **Checkpoint 3** | one by one: method drafted (see below) | 19 |
| 1:55 | **Wrap-up** | recap; tease *No expo!* and Quiz 3 next time | 21 |

## Explain it like this (in plain English)

- **What is a feature?** Just a column in the table the model reads. Raw sensor readings are features; so is anything you compute from them. Feature engineering = building the columns that let the model see what an engineer already knows.
- **"The model cannot tell time."** The isolation forest reads one row (one hour) at a time and compares it with other rows. It has no idea what happened an hour ago, or whether this is a sunny hour or an eclipse hour, unless a column says so.
- **History features.** `soc.shift(1)` copies the value from one hour earlier onto each row (a *lag*). `soc.diff(1)` is the change since the last hour. `soc.rolling(24).mean()` is the average of the last 24 rows, ending at the current one. All of these look **back**.
- **The 14:00 test.** At 14:00 in the control room, you only have data up to 14:00. `shift(-1)` copies the **next** hour back; `rolling(24, center=True)` uses 12 future hours. Both look brilliant in a notebook and are impossible live. In the exercise, both already "know" about EV02 at midnight, an hour before it began.
- **Rows lost.** A 24-hour window can't be filled for the first 23 hours, and the 24-hour lag needs a full day before it, so `dropna()` removes the first 24 rows: 8,760 → 8,736.
- **Why `temp_per_drive` works.** The amplifier's temperature rises with the drive level (the load) and with the season, so its raw values swing a lot. That swing makes σ big, and the 3σ ceiling (68.0 °C) sits above even the fault (hottest EV04 hour 67.0 °C). Divide by the drive and you ask a sharper question: *how hot is it for the work it's doing?* Normally 0.821 ± 0.013; during EV04, 0.870 (about +3.9σ). A plain 3σ chart on that one column catches EV04 in its first hour, lights **605 of its 672 hours**, and raises **0 false alarms all year**.
- **The 29σ trap.** The code book builds a cleverer feature: an *expected* temperature from drive plus a yearly sin/cos wave, fitted on January–May, and then the residual. EV04 sits **28.9σ** out. Impressive, until you look at the rest of the year: from June it drifts, and from October **every one of the 2,208 hours** is flagged (3,512 false alarms in the year). Why: the amplifier also warms slowly through the year (about +3.7 °C a year in this file), and five months can't tell that slow warming from the seasonal wave. The fitted wave guesses wrong for months it never saw. **The test of a feature is not how far out the fault sits; it's whether the feature stays quiet on normal months it never saw.**
- **Twins.** The code book's 32 columns contain 18 pairs above 0.98 correlation. `soc_gap` is exactly `100 − battery_soc_pct`. The forest picks a column at random for every cut, so two copies of a sensor give that sensor double the vote, and the noise of 32 columns drowns the obvious faults.
- **Lean 5 vs kitchen sink (same forest, same reference months, same steady-sun hours, whole year).** Kitchen sink: 3 of 5 (misses EV01 and EV03, the easy 11 A dropouts), about 70 false alarms. Lean 5 (array current, bus voltage, state of charge, battery temperature, `temp_per_drive`): **5 of 5**, every event within an hour of its start, **40** false alarms.
- **Right reason.** z = (value − normal) ÷ σ, with "normal" from the training months in steady sun. For each event, the biggest z-scores of the flagged hours: EV01/EV03 array current about −34σ and battery temperature about +25 to +27σ; EV02/EV05 state of charge −21.6σ and bus voltage about −5.5 to −5.9σ; EV04 `temp_per_drive` +3.8σ alone. The model's reason is the engineer's reason.
- **Why "steady sun" matters (context, from last time).** Eclipse (battery power) and the 3 recharge hours after it are normal states with their own normal. SoC between 92 and 94% happens on 35 eclipse-night hours a year; in steady sun it happens only during EV02 and EV05.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | "NEPA has brought light, but the inverter still shows 93% and won't climb." Each number is normal alone. | "Is 93% a problem?" (at night, no; in sunshine, yes) |
| 4 | Gold window = EV02, 2 May. The code book's proof looked at 1 May, where SoC is a normal 100%. | — |
| 5 | The forest "caught" EV04 on one hour, 25 days late. By the rules it counts; to an engineer it's a miss. | "Would you sign that off?" |
| 6 | Quiz Q16. Each row alone. Features carry history, context, relationships. | — |
| 9 | Quiz Q19, Q20, Q22. Read the test aloud and get the room to repeat it. | "Which of these could you compute at 14:00?" |
| 11 | The ceiling sits above the fault because σ is swollen by the seasons and the load. | — |
| 12 | Quiz Q17. Generator running hot on one bulb: the radiator is blocked. | "What else in your unit is only abnormal *for its load*?" |
| 13 | The quiz (Q18) says about 22σ; the code book's recipe gives 28.9σ. Either way it's huge, and either way it fails from October. | "Would you put this on the console?" |
| 15 | Quiz Q21. Two copies of SoC = SoC votes twice. | — |
| 16 | The sink misses the two **easiest** faults. Fewer, sharper eyes. | — |
| 17 | Quiz Q14. Point at EV04: one feature, the right one. | "What sentence do you give the duty engineer?" |
| 18 | Leave them hungry: the score includes the training months, and the simple chart never raced. | "What would make this an honest exam?" |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `HOURS_BACK = 1` | `-1` copies the next hour back: that's the leak in A3 |
| A2 | `WINDOW = 24` | `1` (that's just the value itself) |
| A3 | `{"b", "d"}` | Picking `c`: a trailing rolling mean only uses the past, so it's honest |
| A4 | `len(bus) - len(F)` = 24 | Guessing 23: the 24-hour lag (`shift(24)`) needs a full day before it |
| B1 | `bus["twta_temp_c"] / bus["rf_drive_pct"]` | Upside down (values near 1.2): temperature goes on top |
| B2 | `K = 3` → caught 1 of 5 (EV04), 0 false alarms | Expecting it to catch the battery events: it watches the amplifier only |
| B3 | `605` | Typing 672 (the event's length, not the hours lit) |
| B4 | `resid_flags.loc["2025-10-01":].sum()` = 2,208 (all of them) | — |
| B5 | `False` | — |
| C1 | `CUTOFF = 0.98` → 18 pairs | — |
| C2 | `CONTAMINATION = 0.005` → 3 of 5 caught, about 70 false alarms | Writing `0.5` flags half of all hours; writing `5` makes sklearn refuse. It's a fraction: `0.005` |
| C3 | `FIT_ROWS = train & steady` → 5 of 5, 40 false alarms, 358 EV04 hours lit | `steady` alone fits on the whole year, EV04 included: EV04 becomes "normal" (only 5 hours lit, 4 of 5 caught). The check rejects it |
| C4 | `"temp_per_drive"` | — |
| C5 | `False`: it trained on January–August, so EV01–EV03 sit inside its training months, and nobody raced the Week 4 chart yet | — |
| 🌶️ | `CHART_FIT_ROWS = train & steady` → 5 of 5, **3** false alarms | Keep it quiet: Week 5 Day 1 runs this race honestly on unseen months |

**Version note.** The forest counts (C2, C3) can shift by a few between pandas or scikit-learn versions. We checked pandas 2.2 and 3.1 with scikit-learn 1.6 and 1.9: everything matches except the kitchen sink (69 or 73 false alarms). The checks accept a range. The chart numbers (B2, BONUS) are exact.

## 🏁 Final project · Checkpoint 3: 🛠️ Method drafted (20 min)

Matches `week-6/final-project/Final-Project-Requirements.pdf`. Go round one by one:

| Check | Pass if |
|---|---|
| Method runs | the **minimum method for their brief** runs end to end on their data: detection (A, E) = a statistical baseline **plus** a multivariate detector on trailing features; degradation / capacity (B, D) = a trend-to-threshold estimate; forecasting (C, E) = a baseline forecast **plus** a regression |
| Normal in writing | the states or modes of their process (eclipse, rain, weekday/weekend, shift change…) and what they take away first (season, drive level, ageing) |
| Features | listed, each passing the **14:00 test**; at least one carries history or a relationship |
| Reference period | months their unit agrees were quiet, written down with the reason |
| Baseline named | the simple method they will race at the next checkpoint (control chart, threshold, naive forecast) |
| Data rules | real data on NIGCOMSAT systems only (not Colab); nothing raw on GitHub |

A first version that runs beats a perfect plan. Anyone still on synthetic data needs **written** agreement from their unit head. Next checkpoint: **Week 5 · Day 3: honest test** (split by time + a baseline comparison table).

## Troubleshooting

| Problem | Fix |
|---|---|
| `NameError: name 'steady_sun' …` / `'score_events'` | They skipped the 🧰 toolbox cell at the start of Part B |
| `NameError: name 'F' …` in Part C | They skipped the `make_features` cell in Part A |
| B1 fails with values near 1.2 | Division upside down |
| C2 raises `ValueError` about contamination | They wrote a percentage (`5`). It's a fraction: `0.005`. (`0.5` runs, but flags half the year) |
| C3 check fails although 5 of 5 caught | They fitted on `steady` (the whole year). EV04 then sits inside the training data and only a few of its hours light up |
| A neighbour's forest numbers differ slightly | Library versions; fine, the check allows a range |
| Fast finishers | 🌶️ race, then: "drop `temp_per_drive` from `X` and refit: what happens to EV04?" (Still 5 of 5, but EV04 lights only 42 of 672 hours, first flag 39 hours late, and false alarms double to 82) |

## Notes on the original material

- **The EV02 date.** The code book's *Proving EV02 is univariately invisible* checks **1 May** (SoC a normal 100% all day). The label file and the data put EV02 on **2 May 01:00–12:00**: array current 26.93–27.14 A, SoC 92.5–93.4%. The slides and the notebook use 2 May.
- **"Univariately invisible."** True only for array current, the one channel the proof checks. Bus voltage sags to 50.12–50.24 V (normal 50.40 ± 0.04 V), so a sunlit-only 3σ chart on voltage catches EV02 and EV05 with no false alarms. Slide 17 shows the voltage z-scores. Only EV04 truly needs two sensors. (Review file, 12g.)
- **The 22σ claim.** The code book says residual σ ≈ 0.18 °C and EV04 ≈ 22σ. Its own recipe gives σ **0.162 °C** and **28.9σ**, and the same feature flags all 2,208 hours of Oct–Dec. Quiz 3 Q18's official answer is "about 22 sigma": mark it as written, and tell the room the real number and the trap. (Review file, 12h.)
- **The 32 columns.** `soc_gap` duplicates `battery_soc_pct` exactly and 18 pairs sit above 0.98, the code book's own pruning line, yet it fits on all of them. On steady-sun hours that forest misses EV01 and EV03 and raises about 70 false alarms. (Review file, 12j.)
- **Why we judge steady-sun hours only.** Eclipse and recharge hours are known operating states; judged as faults, they swamp every detector (W4D2). We state this limit openly: a fault during an eclipse hour is left to the eclipse procedures.
