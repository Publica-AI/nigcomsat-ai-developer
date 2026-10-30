# W1D2 Instructor Notes: Charts That Don't Lie

> **The one idea for today:** *the right chart depends on the question.* A breach question needs the worst moment (minimum), not the average; a “who's worst?” question needs small multiples; a “who changed most?” question needs an index. And every chart gets a threshold line and a title that states the finding.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours |
| **Participants leave able to** | pick the right daily summary (min vs mean), resample hourly → daily, pivot long → wide, draw small multiples on a shared axis, index to a baseline, choose a y-axis range, write a finding title and a 4-sentence finding |
| **Covers (original)** | Week 3 Code Book: **A3 RF link quality** (mean vs minimum) and **B6 VSAT uptime by region** (long format, pivot); Week 3 quiz topic *visualising time-series and data storytelling* |
| **Datasets** | `rf_link_quality_hourly.csv`, `vsat_uptime_by_region_weekly.csv` (and `noc_tickets_daily.csv` for one axis example on the slides) |
| **Files you need open** | animated slides, your **solution** notebook, the rule book PDF |

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Warm-up** | 5-minute recap of Day 1: “what makes a time series?” “why `.asfreq()`?” Use Week 3 quiz Q1 and Q6 | 1–2 |
| 0:08 | **Hook** | DStv “No Signal” in heavy rain = rain fade. Did our link go down? | 3 |
| 0:12 | **Part 1: the average lies** | Meet the RF data, the hourly chart, **mean vs min** (the killer slide), the rule, cause vs response, one axis | 4–9 |
| 0:30 | **Part 2: six zones** | Long → wide, spaghetti vs small multiples, index to week 1, two questions two answers | 10–15 |
| 0:45 | **Part 3: honest rules** | Y-axis, the 5 rules, title upgrade, 4-sentence finding | 16–20 |
| 0:55 | **Hands-on** | Part A (30 min) then Part B (30 min). Walk the room | 21 |
| 1:50 | **Wrap-up** | Scoreboards up; 2–3 volunteers read their 4-sentence findings | 22 |

## Explain it like this (plain English)

- **Link margin**: signal left above the minimum, like fuel above the reserve line. Below 0 dB the link is down.
- **The average lies**: August had **12 outage hours on 11 different days**, all during heavy storms. But the *lowest daily average* in the month is **4.91 dB**: comfortably positive. A report on daily averages would say “no outages”. The daily **minimum** shows the truth. Rule: *breach questions need the worst moment.*
- **Cause vs response**: rain and uplink power correlate at **0.97**. The station turns up its power *because* it's raining (uplink power control): a response, not a separate fault. Average uplink: **41.2 dBm dry, 44.1 dBm in rain**.
- **One axis**: rain (mm/hr) and power (dBm) are different units. Put them in two stacked charts with a shared time axis, never two y-axes on one chart.
- **Long vs wide**: databases export long (one row per zone per week, 312 rows). Charts want wide (52 rows × 6 columns). `pivot` converts.
- **Small multiples on a shared y-axis**: one mini chart per zone, all with the same scale. If each panel had its own scale, every zone would look equally dramatic.
- **Index to week 1**: `wide / wide.iloc[0] * 100`. Everyone starts at 100; now you see *change from their own normal*.

## ⚠️ Know this before you teach (the original material is wrong here)

The original code book says *“South South starts lowest **and** falls furthest”*. Only the first half is true:

| Question | Answer from the data |
|---|---|
| Who is lowest? | **South South**: lowest average (97.67%), lowest week 1 (97.99%) and the worst single week (96.56%, mid-September) |
| Who fell furthest from their own week 1? | **South East**: its indexed line drops to **98.2**. South West reaches 98.3 and South South 98.5 |

This is actually the best teaching moment of the day: *lowest score ≠ biggest drop since last term.* The southern zones lose about **1 point** of uptime in the rainy season, the northern zones about **0.4**.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | “Same physics as your DStv in a Lagos storm.” | “Who has seen ‘No Signal’ in heavy rain?” |
| 5 | “Only one column matters today: link margin. Fuel above reserve.” | — |
| 6 | Count the dips below the red line with them: 12. | — |
| 7 | Show the average first. Pause. “All good?” Then press next: the minimum. | “Which chart would you send your unit head?” |
| 8 | Third Mainland Bridge: “average traffic was fine today.” | — |
| 9 | Correlation 0.97, but uplink power is the *reaction*. | “Does turning up the volume make it rain?” |
| 12 | Let them struggle to find South South for 10 seconds. | “Found it?” |
| 13 | Point out: same y-axis on all six. | “What would happen with six different axes?” |
| 14–15 | Two questions, two answers. | “Which question would your unit head ask?” |
| 17 | Uptime zooms in (say the range); tickets start at zero. | “Does Sunday really have no tickets?” |
| 20 | Read the 4 sentences slowly. Recommendation last. | — |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `"h"` | `"H"` → newer pandas rejects uppercase; or forgetting quotes |
| A2 | `(rf["link_margin_db"] < 0).sum()` → **12** | `rf["link_margin_db"].min()` gives a value, not a count |
| A3 | `daily_mean.min()` → **4.91** | — |
| A4 | `.min()` → **11** days | leaving `___` → AttributeError mentioning `'___'` |
| A5 | `THRESHOLD = 0`, any title ≥ 20 characters **with a number** | titles without a number fail on purpose |
| A6 | `"min"` | — |
| A7 | `"response"` | — |
| B1 | `"week_start"`, `"region"`, `"uptime_pct"` | swapping index and columns |
| B2 | `True` | `"True"` in quotes also fails: it's a Python value |
| B3 | `wide.mean().idxmin()` → **South South** | typing it by hand with a typo |
| B4 | `indexed.min().idxmin()` → **South East** | expecting South South (see the box above) |
| B5 | `"zero"`, `"tight"` | — |
| B6 | Situation, Observation, Implication, Recommendation | — |
| 🌶️ | `rf.loc[rf["link_margin_db"] < 0, "rain_rate_mmhr"].min()` → **39.3 mm/hr** | No outage happened below 37.3 mm/hr, and 44 rainy hours had no outage at all |

## Quiz link

Week 3 quiz (`Time-series/MCQ/week-03-mcq.csv`), topic **“visualising time-series and data storytelling”**, is exactly today: tight y-axis for bounded measures (slide 17), daily minimum for SLA (slide 7), small multiples on a shared axis (slide 13), index to week 1 (slide 14), finding titles (slide 19), recommendation last (slide 20). Use 2–3 of them as Day 3's warm-up.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ValueError: Invalid frequency: H` | lowercase `"h"` |
| `ValueError: Index contains duplicate entries, cannot reshape` in B1 | they put `region` as the index |
| Small multiples squashed or empty | re-run B1's pivot cell; check `wide.shape` is `(52, 6)` |
| Someone finishes early | Pepper task, then help a neighbour, then draft their 4 sentences |

## Notes on the original material

- Original code book section *A3* says the RF file is for “mean vs minimum”: confirmed. Its daily-mean claim (“stays comfortably positive on every day”) is correct: minimum daily mean is 4.91 dB.
- Original section *B6* claims South South “falls furthest”: **not true when indexed to week 1** (see above).
- The original uses `.asfreq("H")`, which crashes on pandas 3. Our notebook uses `"h"`.
