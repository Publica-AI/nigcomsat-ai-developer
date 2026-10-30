# W5D2 Instructor Notes: Forecasting Baselines

> **The one idea for today:** *before any model, forecast the cheap way, lock the test weeks away and score every forecast with the same ruler.* On this series the winner is a two-line forecast the original code book never tries: last year's tickets **per terminal** × today's terminals. Its error, 2.24 tickets a week, is the bar every later model must beat.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours (10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up) |
| **Participants leave able to** | explain what a forecast, a horizon and a hold-out are; write naive, seasonal naive, moving average and exponential smoothing in pandas; score forecasts with MAE and say it in words; explain why seasonal naive lost on a seasonal series; turn a count into a rate and build the rate seasonal naive; distrust a single lucky split |
| **Covers (original)** | Week 6 Code Book: *the three files*, *ops_tickets_weekly*, *Topic 6.1 Forecasting baselines* (all its numbers reproduce); Week 6 quiz topic *forecasting baselines* (Quiz 4 Q1–Q6, sat in Week 6 · Day 2) |
| **Dataset** | `week-06/data/ops_tickets_weekly.csv` |
| **Files you need open** | animated slides, your **solution** notebook |

## The day before: checklist

<ul class="check">
<li>Run the <b>solution</b> notebook top to bottom: 14 of 14 ✅ (a few seconds).</li>
<li>Re-read slides 12–14 until you can explain in one breath why seasonal naive came <b>last</b> on a seasonal series: <i>"right season, wrong size: it copied a network 35% smaller."</i></li>
<li>Re-read slides 16–18 and do the sum on slide 17 yourself once: 42 ÷ 1,588 × 2,131 = 56.4.</li>
<li>Remind people who chose a forecasting or degradation brief that <b>Checkpoint 4</b> (⚖️ Honest test) is next session: they bring a temporal split and a baseline comparison table.</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | Grandma vs the ₦25 million consultant; from "is it wrong now?" to "what comes next?" | 1–4 |
| 0:10 | **Meet the series** | 104 weeks, trend + a season in steps + noise; lock the last 8 weeks away | 5–7 |
| 0:17 | **Four baselines** | What each assumes; unlock the 8 weeks; MAE in words; the scoreboard; why seasonal naive lost; why naive "won" | 8–14 |
| 0:30 | **Divide by the size** | The rate repeats; the formula; the result (2.24); the W4D3 callback; the bar | 15–20 |
| 0:38 | **One split can lie** | The flat average's lucky 7.77; teaser for Week 6 · Day 1 | 21 |
| 0:40 | **Hands-on** | Parts A–D (60 min). Walk the room | 22 |
| 1:40 | **Wrap-up** | Recap, 🌶️ α discussion, Checkpoint 4 reminder | 23 |

If time is tight, skip slide 19 (the W4D3 callback) and do Part D of the notebook together on the projector.

## Explain it like this (in plain English)

- **Forecast:** a guess about the future made only from the past. If it secretly used next week's number, it's expo (Week 5 · Day 1).
- **Origin, horizon, blind:** we stand on the last training week (27 Oct 2025) and guess the next 8 weeks (the horizon) in one go. The guess for 22 December can't use the real 15 December number.
- **Baseline:** the cheap forecast every fancier method must beat. If an expensive model can't beat Grandma, the invoice is for nothing.
- **Each baseline makes one assumption:**
  - **naive:** nothing changes;
  - **seasonal naive:** this year repeats last year;
  - **moving average:** the recent level, smoothed;
  - **exponential smoothing:** a running level that each week pulls 30% of the way (α = 0.3).
- **MAE:** take each week's miss, drop the minus sign, average. Same unit as the data, so you can say it to a duty manager: "off by about 11 tickets on a typical week".
- **Why seasonal naive came last:** right season, wrong size. It copied Nov–Dec 2024, when the network had 1,581 terminals; now it has 2,131 (+35%). Every copied week is too low.
- **Why naive "won":** right size, wrong season. It copied 74, a rainy-season week, into the dry season (3 Nov: 53). It won a bad race.
- **Divide by the size:** tickets per 1,000 terminals is almost the same number in the same month of both years. The growth divides out; the season stays. Last year's rate × today's terminals uses both halves of the story.
- **Same move as W4D3:** `temp_per_drive` divided out the amplifier's workload; today we divide out the network's size. *A rate travels, a count doesn't.*
- **One split can lie:** a flat average scored 7.77 here because two errors cancelled. You only trust a method after testing it on many splits (Week 6 · Day 1).

## The numbers (computed from the data)

**The file:** 104 weeks, 1 Jan 2024 – **22 Dec 2025** (Mondays), 0 gaps. Tickets 28–80 a week (mean 50.2 in 2024, 66.6 in 2025). Terminals 1,200 → 2,181.

**The season comes in steps:** +17 tickets in the week of 1 Apr 2024, −15 in the week of 4 Nov 2024, +16 in the week of 7 Apr 2025, −21 in the week of 3 Nov 2025 (that last one is inside the test weeks).

**The split:** train = 96 weeks (1 Jan 2024 – 27 Oct 2025); test = the last 8 weeks (3 Nov – 22 Dec 2025). Actual tickets in the test weeks: 53, 54, 58, 55, 68, 73, 69, 72 (mean 62.75).

**The forecasts and their MAE (same 8 weeks, all blind from 27 Oct):**

| Forecast | The 8 numbers | MAE |
|---|---|---|
| 🎯 **Rate seasonal naive** (ours) | 56.4, 56.1, 58.5, 55.6, 69.8, 66.8, 67.7, 70.0 | **2.24** |
| Flat training average (Part D) | 57.9 every week | 7.77 |
| Naive | 74 every week | 11.25 |
| Exponential smoothing (α = 0.3) | 75.6 every week | 12.80 |
| Moving average (8 weeks) | 77 every week | 14.25 |
| Seasonal naive (52 weeks) | 42, 42, 44, 42, 53, 51, 52, 54 | 15.25 |

- Naive's misses: 21, 20, 16, 19, 6, 1, 5, 2. Total 90 ÷ 8 = 11.25. It's too high every single week, by 16–21 all November.
- The rate forecast's misses: 3.4, 2.1, 0.5, 0.6, 1.8, 6.2, 1.3, 2.0. That's about 5× smaller than naive.
- The four code-book baselines match the original code book and Quiz 4 exactly.

**Network growth:** 1,581 terminals on 28 Oct 2024 → 2,131 on 27 Oct 2025 = ×1.348 (+35%).

**Tickets per 1,000 terminals, by month (training weeks only):**

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | 25.6 | 26.7 | 29.1 | 39.4 | 40.2 | 40.2 | 40.9 | 37.8 | 37.2 | 36.5 | 26.6 | 31.7 |
| 2025 | 25.9 | 27.4 | 28.9 | 39.2 | 38.5 | 39.8 | 38.6 | 37.7 | 37.7 | 35.5 | 🔒 | 🔒 |

- **Year-to-year gap:** the same month never differs by more than 2.3 (July).
- **Rainy-season lift:** rainy months (Apr–Oct) average 38.5 per 1,000 against 28.0 for dry months, a lift of **37.5%** (all 104 weeks). The code book says "about 35%".
- **December bump:** December 32.0 against November 26.1 (all weeks).

**The rate forecast for 3 Nov, as one sum:** 4 Nov 2024 had 42 tickets from 1,588 terminals = 26.4 per 1,000. × 2,131 terminals today = **56.4** (actual 53).

**The 🌶️ α task (look, don't choose):** α = 0.1 → level 75.43, MAE 12.68 · α = 0.3 → 75.55, MAE 12.80 · α = 0.9 → 73.94, MAE 11.19. α = 0.9 "beats" naive by a hair on these 8 weeks, but you only know that by peeking at the test.

**For you only, a preview of Week 6 · Day 1 (don't spoil it).** Stand at every week of 2025 and forecast blind, then average the MAE:

| Forecast | 1 week ahead (52 origins) | 4 weeks ahead (49) | 8 weeks ahead (45) |
|---|---|---|---|
| Naive | **3.19** | 5.03 | 6.20 |
| Rate seasonal naive | 3.29 | **3.21** | **3.18** |
| Flat training average | 14.79 | 15.42 | 16.50 |

- The flat average's 7.77 today was luck: over 45 origins it's the worst forecast at 8 weeks ahead.
- The rate forecast's win is not luck at 4 and 8 weeks ahead.
- One week ahead, naive and the rate forecast tie.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | "If the AI can't beat Grandma, the invoice is for nothing." | "Who has seen a vendor demo with no comparison?" |
| 4 | A forecast uses only the past. Anything else is expo. | — |
| 5 | Blue: tickets. Teal: terminals. The last 8 weeks are locked. | "What do you see?" (growth, jumps) |
| 6 | The season is a **step**, not a wave: rain arrives in April, leaves in November. | "Why would rain raise tickets?" (rain fade on VSAT links, W1D2) |
| 7 | Read the code aloud. Origin = 27 Oct 2025. Blind. | — |
| 9 | One assumption each. Read the big numbers. | Quiz 4 Q1, Q2, Q5 |
| 10 | Open the envelope. White = what really happened. | "Which one looks best?" |
| 11 | Point at the red sticks: the four big ones are the dry season starting. | Quiz 4 Q3 |
| 12 | Naive wins, seasonal naive last. | "Why would the seasonal one lose on a seasonal series?" |
| 13 | Right season, wrong size. | Quiz 4 Q4 |
| 14 | Right size, wrong season. Winning a bad race. | — |
| 16 | Divide by the network: the bars match year to year. Only training weeks. | "What stays the same when the network grows?" |
| 17 | Do the sum aloud: 42 ÷ 1,588 × 2,131. | — |
| 18 | 2.24 vs 11.25: about 5× better, blind, nothing fitted. | — |
| 19 | Same move as `temp_per_drive`. | "Where else at work would a rate beat a count?" |
| 20 | Beat the **best** baseline, not the easiest. | Quiz 4 Q6 |
| 21 | 7.77 from a flat line: luck or skill? Leave it open. | "How would you find out?" (test on many periods) |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `FREQ = "W-MON"` → 104 weeks, 0 gaps | `"W"` gives 103 weeks and 206 gaps: pandas' `"W"` means weeks ending on **Sunday**, and every date here is a Monday |
| A2 | `H = 8` → 96 training weeks, 8 test weeks from 3 Nov 2025 | — |
| B1 | `series.iloc[-1]` → 74 every week | `series.iloc[0]` (that's the first week, 31 tickets in Jan 2024) |
| B2 | `period=52` | `period=7` or `12`: weekly data, yearly season, so 52 |
| B3 | `window=8` | — |
| B4 | `(1 - alpha)` | `alpha` again (then the old level counts as much as the new week) or `0.7` (works for α = 0.3 only, so the check fails on α = 0.5) |
| B5 | `COMPARE_WITH = actual` → naive 11.25, smoothing 12.80, moving average 14.25, seasonal naive 15.25 | `train` (wrong length, comparing with the past) |
| B6 | `WEEKS_BACK = 52` → ×1.348 | `1` (that's last week) |
| C1 | `DIVIDE_BY = train_terminals` → the table above | Typing it in quotes (the cell says so) |
| C2 | `4` (April) | `11`: that's when it drops |
| C3 | `series / terminals` | `terminals / series` (terminals per ticket: the forecast comes out tiny) |
| C4 | `HORIZON = H` (or `8`) → rate seasonal naive 2.24 | — |
| D1 | `FLAT = train.mean()` → 7.77 | `actual.mean()`: that's peeking at the test weeks (it scores 7.75, a hair better, and that's exactly the expo) |
| 🌶️ | `0.9` | `0.1`: a small α is smooth and slow |

## Troubleshooting

| Problem | Fix |
|---|---|
| `NameError: name 'W' is not defined` in A1 | The frequency needs quotes: `"W-MON"` |
| B1–B4 say "❌ Not yet … (Python said: TypeError)" | The `___` inside the function is still there. Point at the `def` line or the body |
| "Get B1 to B4 to ✅ first" | The forecast-table cell waits until all four functions pass. Find the ❌ one |
| `NameError: mae` | They skipped the ▶️ `def mae` cell at the top of Part B |
| The plot in Part A shows a gold band at the far right | That's intended: the locked test weeks. The line stops before it |
| C1 table shows numbers like 0.03 | They forgot the ×1000 (it's in the cell; they may have edited it). Rerun the cell as given |
| Fast finishers | 🌶️ α task, then: "what would seasonal naive score if you multiplied it by the growth, 1.348?" (MAE 2.34: the growth fix by hand, almost the rate forecast) and "why can't you use the terminals of the test weeks?" (you won't know them on 27 Oct) |

## If someone asks…

- **"Isn't using today's terminals cheating?"** No. The count on 27 Oct is known on 27 Oct, and we hold it flat for all 8 weeks: we never use the test weeks' terminals. If the NOC has a written rollout plan made **before** the forecast, using planned terminals would be fair too. Say which one you used.
- **"Didn't you invent the rate trick after seeing the answers?"** The idea comes from the training weeks only (the table on slide 16 stops at October 2025), and the forecast has no setting to tune. It's still one split, which is why Week 6 · Day 1 tests it on 45 different 8-week stretches. It keeps winning 4 and 8 weeks ahead.
- **"Why MAE and not percentage error?"** MAE is in tickets, so anyone can picture it. Percentage errors blow up near zero, and squared errors (RMSE) punish one big miss more. MAE is the course's ruler; just use the same ruler for everyone.
- **"Exponential smoothing is a real method. Why does it lose?"** The simple version has a level but no trend and no season, so it can't know November drops. Fancier versions (Holt-Winters) add trend and season. On this series they must still beat 2.24.
- **"What if the season changes next year?"** Then last year's rate is wrong. Every seasonal method assumes the pattern repeats; write that assumption in your report.
- **"So should the NOC use naive or the rate forecast?"** For the month-ahead roster, the rate forecast. For next week only, they tie (Week 6 · Day 1 shows it). The honest answer depends on the horizon the planner needs.

## Notes on the original material

- The original's numbers for Topic 6.1 reproduce exactly: naive 11.25, exponential smoothing 12.80, moving average 14.25, seasonal naive 15.25. Quiz 4 uses them, so we kept the same split (the last 8 weeks).
- The code book's tables say the file runs "2024-01-01 to 2025-12-29". It ends on **22 Dec 2025**: 104 Mondays. It also says tickets range "from the high-20s to the mid-70s"; the range is 28–80.
- The code book says the rainy season lifts tickets "by about 35%". Per terminal, it's 37.5%. Close enough, and the idea stands.
- The code book explains naive's win correctly but stops there. It never tries dividing by the network, which is the one idea that makes this series easy (rate seasonal naive, MAE 2.24).
- The original's baseline functions return pandas Series with a dummy index. Ours return plain numpy arrays (simpler, and the numbers are identical).
- The original Week 6 notebook has garbled characters (`â€”` instead of `—`) in its text. Ours don't (review row 12).

## Final project

- Checkpoint 4 (⚖️ **Honest test**) is next session (Week 5 · Day 3). Participants bring a **temporal split** of their own data and a **baseline comparison table**: every method, the same test period, the same scorer.
- Today's scoreboard is the template.
- **Detection briefs (A, E):** the baseline is the Week 4 control chart, scored with `score_events`.
- **Degradation briefs (B, D):** the baseline is a straight-line trend to the threshold (Week 6 · Day 2).
