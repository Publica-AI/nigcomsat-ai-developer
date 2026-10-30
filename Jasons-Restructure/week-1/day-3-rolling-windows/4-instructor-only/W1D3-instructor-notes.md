# W1D3 Instructor Notes: Calm Down the Noise: Rolling Windows

> **The one idea for today:** *a rolling window averages the last N rows and slides forward. It makes the real level visible, but it always costs something: a delay, a peek at the future (if centred), or hidden short events.*

## At a glance

| | |
|---|---|
| **Length** | ~2 hours |
| **Participants leave able to** | smooth a series with `.rolling()`, explain why 7 days suits daily tickets, tell trailing from centred windows, use `.ewm()`, tell `.rolling` from `.resample`, and refuse to report an SLA from a smoothed line |
| **Covers (original)** | Week 3 Code Book: **B4 NOC tickets daily**, **B5 NOC tickets weekly**, and the mean-vs-minimum lesson from **A3 RF link quality**; Week 3 quiz topic *rolling windows and smoothing* |
| **Datasets** | `noc_tickets_daily.csv`, `noc_tickets_weekly.csv`, `rf_link_quality_hourly.csv` (all `Time-series/week-03/data/`) |
| **Files you need open** | animated slides (`1-slides/web-animated/`), your **solution** notebook, the rule book PDF |

## The day before: checklist

<ul class="check">
<li>Run your <b>solution</b> notebook top to bottom: all 14 checks should be ✅.</li>
<li>Open the animated slides and let slide 6 (the sliding window) play once, so you know what it shows.</li>
<li>Share the exercise link and the rule book PDF in the class group chat.</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | Quiz warm-up from Day 2, then “Which day do faults rest?” | 1–3 |
| 0:10 | **The moving average** | Fuel-money analogy, the sliding window, the 2-year chart | 4–7 |
| 0:25 | **Choosing a window** | Why 7, then 3 vs 7 vs 30 | 8–9 |
| 0:35 | **What smoothing costs** | Trailing vs centred, the lag, `.ewm`, the SLA trap, sparse counts, rolling vs resample, noise | 10–17 |
| 1:00 | **Hands-on** | Part A (15 min) then Part B (45 min). Walk the room. | 18 |
| 1:45 | **Wrap-up** | Scoreboards up, recap, three “why” questions | 19 |
| 1:55 | **Exit** | Share the glossary PDF. Tease Week 2. | — |

## Explain it like this (in plain English)

- **Rolling window:** take the last 7 days, average them, write the answer next to today. Tomorrow, drop the oldest day, add the newest, average again.
- **Why 7 for daily tickets:** every 7-day window contains exactly one Monday, one Tuesday … one Sunday. The quiet weekend is always inside, so it can't make the line jump. A 3-day window sometimes holds the weekend and sometimes doesn't, so it still zig-zags.
- **The first 6 NaN:** not a bug. On day 3 there are only 3 days to average, so a 7-day average genuinely doesn't exist yet.
- **Trailing vs centred:** trailing only looks back (safe, but late by about half the window). Centred looks back *and forward*. It lines up beautifully with events because it uses tomorrow's data. Fine for last year's report; never for live monitoring or forecasting. In Week 5 this mistake has a name: *leakage*.
- **`.ewm(alpha)`:** exponential smoothing. Recent days count more. High alpha follows the data and reacts fast; low alpha is calm and slow.
- **`.rolling(7)` vs `.resample("W")`:** rolling gives one value per day (“last 7 days as of today”); resample gives one value per calendar week (“total for that week”). Watch partial buckets at the edges.
- **The SLA rule:** an average spreads a 2-hour outage across 24 hours, and it disappears. SLA breaches are counted from raw readings.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | Weekday 7.1 tickets, weekend 3.4: about half. Sunday is the quietest (3.1). | “Why are weekends quieter?” |
| 5 | Naira amounts are illustration only. The idea is what matters. | “Who checks their spending day by day? Week by week?” |
| 6 | Let the gold frame slide. The yellow number is the average inside the frame. | “Why is day 3 NaN?” |
| 7 | Grey is unreadable; blue shows the rainy-season rise. | “Which months are busiest?” (July to September) |
| 8 | 3-day swing across the week: **2.79** tickets. 7-day swing: **0.02**. | “Why does 7 work?” |
| 11 | Point at the red cells: days that haven't happened yet. | “Would you trust a forecast that used tomorrow's data?” |
| 12 | Trailing 30-day peak: 27 Aug 2024. Centred: 13 Aug 2024. **14 days** late (same gap in 2025). | “Bigger window: more or less delay?” |
| 14 | **12** real outage hours in August; **0** on the 24-hour average (it never drops below 4.55 dB). | “What would the customer say?” |
| 15 | P1: about 1.1 a day, 17% of days have none. | — |
| 16 | 105 weekly buckets; the last one has only 2 days (9 tickets). | “Was that really a quiet week?” |
| 17 | Weekly mean **36.4** (the original code book says 38, which is wrong); typical swing ±5. Only 1 week in 52 is outside mean ± 2 swings: 47 tickets, in August. | “38 → 41: call a meeting?” |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `"date"` | Typing `"timestamp"` (that was Day 1's file) |
| A2 | `"half"` | — |
| B1 | `7` | `"7"` in quotes → `ValueError` |
| B2 | `6` (`tk["roll7"].isna().sum()`) | Counting 7 |
| B3 | `3` | — |
| B4 | `roll7_by_day.max() - roll7_by_day.min()` → **0.02** | Forgetting the brackets on `.max()` |
| B5 | `True` | `"True"` with quotes |
| B6 | `"no"` (the centred line is NaN on the last 15 days) | — |
| B7 | `len(weekly)` → **105** | — |
| B8 | `"high"` | Confusing “smooth” with “close”: low alpha is smooth, high alpha is close |
| B9 | `(tk["priority_1"] == 0).mean()` → **0.171** | Using `.sum()` (gives 125 days, not a share) |
| B10 | `(margin < 0).sum()` → **12**, `(smooth < 0).sum()` → **0** | — |
| B11 | `wk["tickets_raised"].mean()` → **36.42**, `"no"` | — |
| 🌶️ | **1** (the week of 18 Aug 2025: 47 tickets) | — |

## Quiz link

The original Week 3 quiz (`Time-series/MCQ/week-03-mcq.csv`), topic **“rolling windows and smoothing”**, questions **13–18**, maps exactly to today:

| Quiz question | Covered on slide |
|---|---|
| 13 · Why seven days | 8 |
| 14 · Trailing windows react late | 12 |
| 15 · Centred windows are not for forecasts | 11 |
| 16 · First rows are NaN | 6 |
| 17 · Exponential smoothing alpha | 13 |
| 18 · Never report SLAs from a smoothed line | 14 |

Use them as a 5-minute warm-up at the start of Week 2 Day 1.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ValueError: window must be an integer` | They typed `WINDOW = "7"`. Remove the quotes |
| `KeyError: 'roll7'` | The B1 cell after the blank wasn't run. Run it |
| B5 shows ❌ although they typed True | They wrote `"True"` in quotes |
| The rolling line looks identical to the raw line | They ran `rolling(1)` or forgot `.mean()` |
| Someone finishes early | 🌶️ bonus, then: “try `rolling(7).std()` and tell me which season is more wobbly” (rainy season: about 2.6 vs 1.9 in Jan–Mar) |

## Notes on the original material

- The original code book says the weekly ticket mean is “about 38”. The data says **36.4**. Use the real number.
- The original code book's day-of-week table is printed alphabetically (Friday, Monday, …). Our version orders Monday to Sunday.
- The original never shows code for rolling windows, centring or `.ewm`. That's all new here, written to match the quiz questions.
