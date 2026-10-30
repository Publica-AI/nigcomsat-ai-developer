# W2D1 Instructor Notes: Take It Apart: Trend, Season and Noise

> **The one idea for today:** *every series is several simpler stories added together. Pull them apart, and the leftover (the residual) is where the surprises are.*

## At a glance

| | |
|---|---|
| **Length** | ~2 hours |
| **Participants leave able to** | decompose a series with `seasonal_decompose`, choose the right period from the process, choose additive vs multiplicative, read a residual, know when to reach for `STL(robust=True)` |
| **Covers (original)** | Week 3 Code Book: *Seasonal periods at a glance*, **A1 bus power**, **A2 battery health**, **B2 Ka-band monthly**, **B4 NOC tickets daily**, **C1 additive vs multiplicative**; Week 3 quiz topic *decomposing an operational time series* |
| **Datasets** | `ka_band_availability_monthly`, `noc_tickets_daily`, `additive_multiplicative_demo`, `bus_power_telemetry_hourly`, `battery_health_daily` (**week-03 version**) |
| **Files you need open** | animated slides, your **solution** notebook, the rule book PDF |

## The day before: checklist

<ul class="check">
<li>Run your <b>solution</b> notebook top to bottom: all 13 checks should be ✅ (about 30 seconds; STL takes a few seconds).</li>
<li>Re-read the 6 quiz questions for this topic in <code>Time-series/MCQ/week-03-mcq.csv</code>. Every one is covered by a slide (see the table below).</li>
<li>Practise the "Lagos traffic" hook out loud. It's the anchor for the whole day.</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Warm-up** | Week 1 in 3 lines; quick quiz from the room | 1–3 |
| 0:08 | **Hook** | Lagos traffic = trend + season + noise; the jollof analogy | 4 |
| 0:12 | **The equation** | observed = trend + seasonal + residual, on real Ka-band data | 5 |
| 0:18 | **Part 1: the tool** | `seasonal_decompose` recipe, the two errors, reading the 4 panels | 6–8 |
| 0:28 | **Choosing the period** | 24 / 7 / 12 from the process; the weekend in numbers; wrong period = more noise | 9–10 |
| 0:35 | **Part 2: add or multiply** | the fare analogy; the log trick | 11–13 |
| 0:42 | **Part 3: the residual** | the August fault; eclipse needs STL; one disaster August; three cycles; battery has two seasons | 14–19 |
| 0:55 | **Hands-on** | Part A (25 min), Part B (35 min). Walk the room. | 20 |
| 1:55 | **Wrap-up** | Recap, cold-call the periods, tease autocorrelation | 21 |

## Explain it like this (in plain English)

- **Decomposition** = splitting one line into three: a slow **trend**, a repeating **seasonal** pattern, and the **residual** leftovers. Additive means you can add them back together and get the original exactly (they prove it in A4).
- **The trend** comes from a moving average one period wide. That's why it's empty for half a period at each end (6 months for monthly data). That's normal; say so before someone asks.
- **The period** is the most important setting and the most common mistake. It's not "12 because seasons are yearly". It's *how many rows until the pattern repeats*: 24 for hourly data with a daily eclipse, 7 for daily data with a working week, 12 for monthly data with a yearly rainy season. Use the wrong period and the real pattern gets dumped into the noise (they see the noise nearly double).
- **Additive vs multiplicative:** look at the swing. Same size as the level rises → additive. Grows with the level → multiplicative (or take the log). Fare analogy: +₦100 every December vs +20% every December.
- **The residual** is the investigation list. For an incident review you look at the residual, not the raw series, because the raw series is full of "normal" patterns.
- **STL** is a smarter decomposition that lets the season change slowly. `robust=True` stops one disaster from spoiling the seasonal pattern.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 4 | "You feel the total. Decomposition separates the causes again." | "Why was your trip long today? Trend, season or noise?" |
| 5 | "Add the bottom three lines and you get the top line back. Exactly. They'll prove it in the notebook." | — |
| 8 | Trend runs **Jul 2023 → Jun 2025**: missing 6 months at each end. August's seasonal effect is **−1.10 points**. Biggest residual only **0.16**: a clean series. | "Why is the trend shorter than the data?" |
| 9 | "The period is a fact about the process." | "Daily NOC tickets: which period?" (quiz) |
| 10 | Sunday **−2.90** tickets, Saturday **−2.39**, Tuesday **+1.35**. Noise left: **1.23** with period 7 vs **2.27** with period 12. | "Why did the noise nearly double?" |
| 12 | Additive swing **0.29 → 0.28**; multiplicative **0.29 → 0.54**. | "Which one is a 20% fare increase?" (quiz) |
| 13 | After `np.log` the swing is **0.77 → 0.83**: nearly constant. | — |
| 15 | August residual: **18 Aug 09:00** is **11.6 A** off; the next biggest is only **0.59 A**. It's an injected solar-array dropout. Link to NigComSat-1 (2008). | "Where would an incident review look?" (quiz: the residual) |
| 16 | Classic decomposition over all 120 days: **all 46** of the top-46 leftovers are eclipse hours (it assumes the same day shape every day). STL robust: the 4 injected dropout hours rank **#4–#7**; after them nothing exceeds **1.75 A**. The top 3 are the first and last eclipse days (the season switching on and off). | — |
| 17 | Fake disaster: Aug 2024 = 94%. Classic August effect **−1.10 → −3.00**. STL robust keeps **−1.20** and puts **−3.99** in the residual. | (quiz, advanced) |
| 18 | 36 months = 3 rainy seasons = the minimum. | "How many cycles before you trust it?" (quiz) |
| 19 | Battery voltage dips in **March (−1.89 V)** and **September (−1.70 V)**; trend **49.76 → 49.55 V** (ageing). | "Why two dips, not one?" (two equinoxes) |

## Quiz coverage (original Week 3 quiz, topic "decomposing an operational time series")

| Quiz question | Answer | Where it's taught |
|---|---|---|
| How does the observed series relate to its parts (additive)? | trend + seasonal + residual | Slide 5, task A4 |
| Which period for daily NOC tickets? | 7 | Slides 9–10, tasks B1–B3 |
| Swing grows with the level: which model? | Multiplicative | Slides 12–13, tasks B4–B5 |
| Where should an incident review look for unusual months? | The residual | Slide 15, task B6 |
| Minimum full cycles before trusting a seasonal profile? | Three | Slide 18, task A2 |
| One catastrophic August makes every August look bad: fix? | STL with robust=True | Slide 17, bonus |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `"MS"` | `"M"` → "M means month **end** (and is being renamed); our labels are month **starts**" |
| A2 | `len(kam) // 12` → 3 | `/` gives 3.0, which is also accepted |
| A3 | `12` | `7` → "that's for daily data" |
| A4 | `parts.trend + parts.seasonal + parts.resid` → gap 0 | — |
| A5 | `parts.seasonal.idxmin().month` → 8 (August) | Using `.min()` gives the value, not the date |
| B1 | `7` | `12` or `365` |
| B2 | `round(weekly.loc["Sunday"], 1)` → −2.9 | Typing 2.9 without the minus sign |
| B3 | `12` | Answering 7 (the good one) |
| B4 | `"multiplicative"` | — |
| B5 | `np.log(demo["multiplicative"])` | Logging the whole `demo` table |
| B6 | `aug_parts.resid.abs().idxmax()` → 2025-08-18 09:00 | Forgetting `.abs()`: the dropout is a **negative** residual, so `.idxmax()` alone finds the wrong hour |
| B7 | `[3, 9]` | Giving month names; numbers are needed |
| 🌶️ | `robust=True` → August seasonal ≈ −1.20 | Leaving it blank: plain STL still says ≈ −2.5 |

## Troubleshooting

| Problem | Fix |
|---|---|
| `x must have 2 complete cycles` | Too few rows for the period. Usually the wrong period (e.g. 365 on 2 years of data) |
| `does not handle missing values` | NaN inside the series. In this course the files are clean, so check they didn't create gaps themselves |
| The decomposition picture appears twice | They wrote `parts.plot()` as the last line. Use `fig = parts.plot()` then `plt.show()` |
| STL feels slow on hourly data | Normal: a few seconds for 2,880 rows |
| Someone loaded the battery file without `week="week-03"` | They get the Week 4 version, whose extra fault is in the capacity column. For `eod_voltage_v` the answers come out the same, but ask them to fix it: it matters in Week 3 |

## Notes on the original material

- The original Week 3 code book **describes** decomposition (periods, components) but contains **no decomposition code**. Everything in today's notebook is new.
- The code book says the Ka-band trend is "about +0.05 points a year". Measured from the decomposition, the trend rises from 99.24% to 99.40% over 23 months (about +0.08 a year). The slides quote the measured numbers.
- The `battery_health_daily.csv` in `week-03/data` and `week-04/data` are **different files**. Today uses the Week 3 one (no injected faults).
