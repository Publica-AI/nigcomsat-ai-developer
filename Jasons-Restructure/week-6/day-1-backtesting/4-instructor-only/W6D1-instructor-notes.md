# W6D1 Instructor Notes: Backtesting: Test It on the Past First

> **The one idea for today:** *one score on one stretch of weeks is a screenshot, not a record. Replay the method on the past many times, using only what was known at each moment, score every method on the same folds, and report the spread and when it fails.* When we do that on the ticket data, the simple forecasts win, and the right one depends on how far ahead the NOC needs to see.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours (10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up) |
| **Participants leave able to** | explain why one split can lie, run a walk-forward backtest and read its folds, score baselines on the same folds, run a rolling-origin backtest at several horizons, pick a method for a stated horizon, and write a 4-sentence recommendation |
| **Covers (original)** | Week 6 Code Book, *Topic 6.5 Backtesting*: the walk-forward backtest and the baselines on the same folds (the battery-call backtest in 6.5 is taught in W6D2); Week 6 quiz topic *backtesting* (the first four of its six questions; the two battery questions belong to W6D2) |
| **Dataset** | `week-06/data/ops_tickets_weekly.csv` (the same file as W5D2 and W5D3) |
| **Files you need open** | animated slides, your **solution** notebook |

## The day before: checklist

<ul class="check">
<li>Run the <b>solution</b> notebook top to bottom: 11 of 11 ✅ (about 20 seconds; Part D runs a few hundred small forecasts).</li>
<li>Re-read the W5D2 and W5D3 slides on the rate seasonal naive and the regression: today replays both.</li>
<li>Practise the verdict until you can say it in one breath: <i>"naive for next week, the rate forecast for the month-ahead roster, not the regression, and watch out when the rains start or stop."</i></li>
<li>Decide how you'll handle the betting hook in your room (see "If someone asks…").</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | Oga Tipster's screenshot vs the full record; the lucky flat average | 1–5 |
| 0:10 | **Walk forward** | The six folds; the code; the spread and when it fails | 6–10 |
| 0:20 | **Same folds** | The fold-by-fold report card; Grandma wins 5 of 6; the rate forecast, blind | 11–14 |
| 0:30 | **How far ahead?** | Rolling origin; MAE vs horizon; the regression can only do one week; the verdict; five rules | 15–22 |
| 0:40 | **Hands-on** | Parts A–E (60 min). Walk the room. | 23 |
| 1:40 | **Wrap-up** | Two or three people read their 4-sentence verdict aloud; recap; project link; next time | 24 |

If time is tight, skip slides 8 (the code: the notebook shows it) and 18 (the per-origin line).

## Explain it like this (in plain English)

- **Backtest:** pretend it's an earlier date, make the forecast with only the data you'd have had then, check it against what really happened, and repeat for many dates. It's the tipster's full record instead of one screenshot.
- **Why one split lies:** the last 8 weeks happened to start just after the rains ended, so the real numbers dropped back towards the old average. A flat average looked brilliant there (MAE 7.77) and is terrible everywhere else (16.50 over 45 origins).
- **Walk forward:** cut, train on everything before the cut, forecast the next 4 weeks, score, slide the cut 4 weeks on. The training block only grows. Each fold is an exam on weeks the model has never seen.
- **Fold MAEs, not one MAE:** six numbers tell you how good it usually is AND when it fails. Here the worst fold holds 3 November, when the rains stop and tickets fall from 74 to 53 in a week.
- **Same folds for everyone:** a model's score means nothing alone. Score the baselines on exactly the same weeks with the same scorer. The fair naive gets the same information as the regression: last week's real count.
- **Horizon:** how far ahead you forecast. "Next week" and "the month-ahead roster" are different questions and can have different winners.
- **One-step vs blind:** the regression and one-step naive see last week's real count before each forecast. The rate forecast is made once at the start and covers the whole block blind. Blind is harder, so the rate forecast winning with less information is a big deal.
- **The verdict:** naive for next week (tie with the rate forecast), the rate forecast for 4+ weeks, not the regression. Recommend the simpler model: the same lesson as W5D1, now for forecasting.

## The numbers (computed from the data)

**The lucky split (slides 4–5, Part A).** Hold-out = the last 8 weeks, 3 Nov – 22 Dec 2025. MAE: flat training mean (57.9 tickets/week) **7.77**; naive 11.25; exponential smoothing 12.80; moving average 14.25; seasonal naive 15.25. (The W5D2 rate forecast scored 2.24 on the same weeks.)
Forecasting 8 weeks ahead from every possible origin (**45** origins, 30 Dec 2024 to 3 Nov 2025): rate seasonal naive **3.18**, naive 6.20, exponential smoothing 7.42, moving average 8.19, seasonal naive 16.25, flat training mean **16.50** (the worst).

**Walk forward, the code book's design (slides 7–10, Part B).** `start_frac=0.5, step=4, h=4` on the 52-row feature table (30 Dec 2024 – 22 Dec 2025):

| Fold | Trains on | Tests on | Regression | One-step naive | Seasonal naive | Rate seasonal naive (blind) |
|---|---|---|---|---|---|---|
| 1 | 26 weeks | 30 Jun – 21 Jul | 2.46 | 2.00 | 17.75 | **1.39** |
| 2 | 30 weeks | 28 Jul – 18 Aug | 4.67 | **1.75** | 18.50 | 3.82 |
| 3 | 34 weeks | 25 Aug – 15 Sep | 2.81 | **1.00** | 20.25 | 3.72 |
| 4 | 38 weeks | 22 Sep – 13 Oct | 1.27 | **1.00** | 20.00 | 2.49 |
| 5 | 42 weeks | 20 Oct – 10 Nov | 7.67 | 6.75 | 14.50 | **2.01** |
| 6 | 46 weeks | 17 Nov – 8 Dec | 5.15 | 6.25 | 16.00 | **2.46** |
| **Mean** | | | 4.01 | 3.12 | 17.83 | **2.65** |

- Regression: range **1.27 – 7.67** (the worst fold is 6 times the best), mean **4.01**.
- Naive beats the regression on **5 of 6** folds; the regression only wins the 17 Nov fold (the December jump).
- The rate forecast has the lowest mean while forecasting each fold **blind**. It beats naive on 3 of 6 folds (1, 5, 6) and the regression on 4 of 6. Don't oversell it: best on average and at the season change, not best every fold.
- Fold 5 contains **3 November**: tickets 74 → 53 (−21), the end of the rains. Every one-step method struggles there; the rate forecast knew because last November's rate showed the same drop.

**Rolling origin, three horizons (slides 16–19, Part D).** Stand at every week, forecast blind, mean MAE (and how many origins each method won):

| Method | 1 week ahead (52 origins) | 4 weeks ahead (49) | 8 weeks ahead (45) |
|---|---|---|---|
| Naive | **3.19** (19) | 5.03 (14) | 6.20 (11) |
| Rate seasonal naive | 3.29 (17) | **3.21** (22) | **3.18** (21) |
| Exponential smoothing | 4.56 (6) | 5.98 (4) | 7.42 (2) |
| Moving average | 5.68 (4) | 6.70 (6) | 8.19 (10) |
| Seasonal naive | 16.13 (0) | 16.10 (0) | 16.25 (0) |
| Flat training mean | 14.79 (6) | 15.42 (3) | 16.50 (1) |

- At 1 week naive and the rate forecast tie (3.19 vs 3.29). Naive's error grows with the horizon; the rate forecast's doesn't.
- Worst single 8-week forecast: naive **18.38** (origin 7 Apr 2025, right as the rains start), rate forecast **5.14**. Naive's bad origins are March–early April and mid-October: the season changes.
- The regression isn't in this table: it needs last week's real count, so it can only forecast 1 week ahead.

**🌶️ Refit every week (Bonus).** `walk_forward_mae(..., step=1, h=1)`: 25 weeks, 30 Jun – 15 Dec 2025. Regression **2.96**, one-step naive **3.16**, rate forecast **2.69** on the same weeks; the regression beats naive on 13 weeks, naive wins 12. So refitting every week turns "naive wins 5 of 6 folds" into a near tie. The rate forecast is still best, and the verdict stands (a tie goes to the simpler model, and the regression still can't make a 4-week roster). The lesson: **the backtest design is part of the result.** Fix it before you look, and say what you chose.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | "One screenshot isn't a record." Keep it light; we're not recommending betting. | "Who has a tipster in their WhatsApp?" |
| 4 | The flat average won the 8-week race. | "Would you hire it?" |
| 5 | Over 45 origins it's last. One split is one screenshot. | — |
| 7 | Walk the folds row by row: training grows, the test block slides. | "Why must the training block stop BEFORE the test block?" |
| 9 | Point at fold 5 and the 3 Nov drop. | "What happened in early November?" (the rains ended) |
| 10 | "Usually off by 4, up to 8 when the rains end." | Quiz 4: reporting the spread |
| 12 | Same folds, same weeks, same scorer. Green = best in that row. | "Which column would you bet on?" |
| 13 | Grandma wins 5 of 6. The code book says so too. | Quiz 4: the baseline backtest |
| 14 | Blind 4 weeks and still the lowest mean. Not a clean sweep: say so. | "Why is blind harder?" |
| 16 | Stand at every week, three horizons. | — |
| 17 | Naive's line climbs, the rate line stays flat. | "Which do you want for the roster?" |
| 20 | The regression needs last week's count; it can't make a 4-week roster. | "What would you need to know to forecast week 4?" |
| 21 | Read the four sentences slowly. This is the shape for the project report. | — |
| 22 | Rule 5: fix the design first. Mention the 🌶️ result. | — |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `flat = train.mean()` → MAE 7.77 | `actual.mean()`: that peeks at the test weeks (expo!) |
| A2 | `H_AHEAD = 8` → 45 origins, flat mean 16.50 | `H_AHEAD = 1`: same idea, but the lucky split forecast 8 weeks |
| B1 | `STEP = 4`, `H_FOLD = 4` → 2.46, 4.67, 2.81, 1.27, 7.67, 5.15 | Other values run fine but give different folds; the check expects the code book's design |
| B2 | `MEAN = fold_mae.mean()` (4.01), `WORST_FOLD = folds["regression"].idxmax()` (20 Oct 2025) | `.max()` gives the worst MAE, not its date: `idxmax()` gives the label |
| C1 | `NAIVE_COLUMN = "tickets_lag1"` → mean 3.12 | `"tickets_lag52"`: that's seasonal naive (same week last year) |
| C2 | `int((folds["naive"] < folds["regression"]).sum())` → 5 | Counting the other way round gives 1 |
| C3 | `RATE_H = 4` → mean 2.65, season-change fold 2.01 | `RATE_H = 1` runs but gives wrong numbers; more than 4 raises a broadcast error |
| D1 | `HORIZONS = [1, 4, 8]` | A single number: it must be a list |
| D2 | `summary.loc[1].idxmin()` = `"naive"`, `summary.loc[8].idxmin()` = `"rate_seasonal_naive"` | Using `.min()` (gives the number, not the name) |
| E1 | `4` (rate seasonal naive) | `3`: the regression can't forecast 4 weeks ahead. `1`: naive's error grows to 5.03 at 4 weeks |
| E2 | Free text. Look for: a method per horizon with its typical error, what not to use and why, and when to expect misses | A single "best model" with no horizon |
| 🌶️ | `STEP_EVERY = 1` → regression 2.96 (naive 3.16, rate 2.69) | — |

## Troubleshooting

| Problem | Fix |
|---|---|
| `NameError: walk_forward_mae` / `rolling_origin` / `make_features` / `X_COLS` | They skipped (or lost, after a restart) the three ▶️ tool cells under STEP 0. Run them |
| `NameError: name 'tickets_lag1' is not defined` | No quotes around the column name: `"tickets_lag1"` |
| C3: `ValueError: operands could not be broadcast together` | `RATE_H` bigger than 4. The fold is 4 weeks |
| B2 ❌ although the date "looks right" | They typed `"20 Oct"`: pandas guesses the year. Use `folds["regression"].idxmax()` |
| D1 takes a few seconds | Normal: about 250 small forecasts per horizon |
| Numbers differ from a neighbour's | Someone changed `STEP`/`H_FOLD` or skipped a cell. **Runtime → Restart session and run all** |
| Fast finishers | 🌶️ weekly refit; then: "change `start_frac` to 0.3 in `walk_forward_mae` and see how the fold MAEs move" (more folds, smaller training sets) |

## If someone asks…

- **"Are you encouraging betting?"** No. The tipster is the classic case of a claim with no record. The lesson is the accountant's: check the whole record before anybody pays.
- **"Isn't the rate forecast just lucky too?"** That's exactly what a backtest answers. It was scored from 45 to 52 different origins and wins clearly at 4 and 8 weeks. At 1 week it only ties naive, and we say so.
- **"Why does naive do so well one week ahead?"** Ticket counts change slowly most weeks, so last week is close. Naive only fails at the season steps (early April, early November), and those failures get worse the further ahead you look.
- **"Can't we put the rate idea into the regression?"** You can try. It would need to beat the rate forecast **in the same backtest**, by enough to be worth the extra moving parts, and it would still need a version that works 4 weeks ahead. That's a fine project idea.
- **"Shouldn't we refit every week?"** Maybe; it's a design choice. The 🌶️ task shows it moves the regression to a near tie with naive. Choose the design before you look, write it down, and use it for every method.
- **"Two years of data is not much."** True. The rate forecast needs a full year of history, so only one year of origins can be scored. Say so in the report, and rerun the backtest as new weeks arrive.

## Final project link

- **Forecasting briefs (C, E):** the report must include a walk-forward or rolling-origin table: every method (baselines included) on the same folds, with the spread and when the bad folds happen, at the horizon the unit actually needs.
- **Degradation briefs (B, D):** next session shows the same idea for a remaining-life call: repeat the call from several starting points.
- **Detection briefs (A, E):** W5D1's rolling origin is the same idea for detectors.
- The 4-sentence verdict on slide 21 is the shape of the **recommendation** the requirements ask for.

## Notes on the original material

- The code book's Topic 6.5 numbers **reproduce exactly**: six folds, regression 2.46 / 4.67 / 2.81 / 1.27 / 7.67 / 5.15 (mean 4.01, worst 7.67); naive 3.12 and seasonal naive 17.83 on the same folds; naive wins 5 of 6; the regression wins only the 17 Nov fold, which the code book calls "the December fold". Quiz 4's backtesting questions match.
- The code book says a flat average is the wrong baseline. It is, across many origins (16.50, the worst), but on the code book's own 8-week hold-out the flat average (7.77) beats all four of its baselines. We use that as today's opening: one split lies.
- The code book backtests one-step forecasts only and never asks about the horizon. We add rolling origin at 1, 4 and 8 weeks, which shows the regression can't serve a month-ahead roster at all.
- The code book never tries the rate seasonal naive (W5D2). On the same folds, blind, it has the lowest mean (2.65).
- The code book refits every 4 weeks without saying it's a choice. Refitting every week makes the regression a near tie with naive (🌶️ task). We teach "fix the design before you look".
- The battery remaining-life backtest at the end of Topic 6.5 is taught in **W6D2** together with Topic 6.4.
