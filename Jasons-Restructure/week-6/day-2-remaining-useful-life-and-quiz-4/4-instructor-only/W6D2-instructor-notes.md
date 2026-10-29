# W6D2 Instructor Notes: When Will It Break? Remaining Useful Life + Quiz 4

> **The one idea for today:** *remaining useful life = fit the trend on the past, extend it until it crosses a limit that is known up front, then say honestly how sure you are.* Honestly means three things: never let "no crossing" turn into a fake date, define "crossed" before you score a call, and report a window that says how far past the data you reached.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours, including Quiz 4 (20 min + 10 min marking) |
| **Participants leave able to** | fit a trend with `np.polyfit`, extend it to a threshold and turn the day number into a date; spot and fix the `np.argmax` "day 0" bug; check a model with a fuel-gauge sum; define a crossing three ways; backtest a remaining-useful-life method from several starting points; explain why a straight line calls a slowing fade early; write a planning figure with a range |
| **Covers (original)** | Week 6 Code Book: *Topic 6.4 Trend-to-threshold: remaining useful life* and the battery half of *Topic 6.5* (the 3-year call checked, and repeated from several origins); Week 6 quiz topic *trend-to-threshold and remaining useful life* (6 questions) plus Q29–30 from *backtesting*; Quiz 4 = the whole Week 6 MCQ file |
| **Datasets** | `week-06/data/degradation_assets_daily.csv` (1,825 days, 1 Jan 2021 – 30 Dec 2025, no gaps), `degradation_thresholds.csv` |
| **Files you need open** | animated slides, your **solution** notebook, `W6D2-quiz-4-answer-key.pdf` |

## The day before: checklist

<ul class="check">
<li>Run the <b>solution</b> notebook top to bottom: 13 of 13 ✅ (it takes a few seconds).</li>
<li>Print <code>2-exercise/quiz/W6D2-quiz-4.pdf</code> (one per person), <b>or</b> import <code>W6D2-quiz-4-google-forms.csv</code> into Google Forms / your LMS.</li>
<li>Print or open <code>4-instructor-only/W6D2-quiz-4-answer-key.pdf</code>. Don't share it until marking.</li>
<li>Re-read slides 11–14 until you can tell the propellant story in one breath: <i>"the original printed the first day of the data; the line actually crosses after the search stopped; the fuel-gauge sum agrees."</i></li>
<li>Remind everyone that next session is <b>demo day</b>: five minutes each, with a working tool, a report and an honest test table.</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | The danfo driver's fuel sum; NigComSat-1R's design life and the 2A/2B targets | 1–4 |
| 0:10 | **Three shapes** | Battery, amplifier, propellant and their limits; the propellant staircase | 5–7 |
| 0:15 | **Draw the line** | Trend-to-threshold; the two functions; the three calls; the argmax bug; solving the line; the fuel-gauge sum | 8–14 |
| 0:27 | **Check the call** | When did it cross (three answers); 13 vs 50 days early; backtest from 4 origins; why early; eclipse ageing; the long reach; golden rules | 15–22 |
| 0:40 | **Hands-on** | Parts A–C (45 min). Walk the room. | 24 |
| 1:25 | **Quiz 4** | 20 minutes, phones down, no AI | 23 |
| 1:45 | **Mark + wrap** | Swap and mark, recap, demo-day reminder | 25 |

If time is tight, skip slides 20 and 21 (eclipse ageing, long reach): Part C of the notebook covers both.

## Explain it like this (in plain English)

- **Remaining useful life (RUL):** how long until a reading crosses its limit. The danfo driver does it every day: litres left ÷ litres per trip. A satellite engineer does the same with capacity, gain or fuel.
- **The limit is known up front.** It comes from engineering (`degradation_thresholds.csv`). What we forecast is *when* it's reached.
- **Trend-to-threshold:** `np.polyfit(x, y, 1)` gives a slope and an intercept. Extend that line into the future; the first day it's below the limit is the call.
- **Honest data rule:** the code book makes its calls with only the first three years (as if it were the morning of 1 Jan 2024), so the battery call can be checked against the two years that follow. Same idea as the Week 5 time split.
- **The bug:** `np.argmax` finds the first True. If there is no True at all it returns 0, so "never" becomes "day 0" = 1 Jan 2021. No error, no warning. Our `day_of_threshold` returns `None` instead.
- **Solving a straight line:** `value = slope × day + intercept`, so the day the value equals the limit is `(limit − intercept) / slope`. No search window needed.
- **The fuel-gauge sum** is the best bug detector there is: what's left above the reserve ÷ what's used a year. If it disagrees with the model, one of them is wrong.
- **"Crossed" has three honest meanings** for a noisy reading: the first day below, the first day the 30-day mean is below, the last day still at or above. Pick one *before* you score, and say which in the report.
- **Backtest the method, not just one call:** stand at the end of year 1, 2, 3 and 4 and make the call with what you had then. You learn how far off the method is, which way it errs (early or late), and how much warning it gives.
- **Why the straight line calls early here:** the battery's fade slows a little every year. A line from the faster early years overstates the later fade. For a battery, early is the safe side.
- **Long reach:** the amplifier call reaches about 9 years past its data. Report a planning figure (a range, how far it reaches, when you'll re-check), never a precise date.

## The numbers (computed from the data)

**The three parts** (last reading on 30 Dec 2025, limit, 3-year line):

| Part | Last reading | Limit | Slope of the 3-year line | 3-year call |
|---|---|---|---|---|
| 🔋 Battery capacity | 77.84 % | 80 % | −4.59 % a year | **1 May 2025** (486 days after the call on 1 Jan 2024) |
| 📡 Amplifier gain | −0.783 dB | −2 dB | −0.162 dB a year | **5 May 2033** (9.3 years past the data it was fitted on) |
| ⛽ Propellant | 101.93 kg | 5 kg | −9.72 kg a year | original prints **1 Jan 2021** (bug); fixed: no crossing before **13 Dec 2034** (end of the 4,000-day search); the line reaches 5 kg on **6 Dec 2035** |

**Propellant burns:** 128 station-keeping burns in five years, one about every **14 days**, about **0.39 kg** each, about **26** a year. Five-year average use: **9.62 kg a year**.

**Fuel-gauge sum:** (101.93 − 5) = 96.9 kg ÷ 9.62 kg a year = **10.1 years** after 30 Dec 2025: about **January 2036**. The line says 6 Dec 2035. Two methods, one story.

**When did the battery cross 80%?**

| Definition | Date | The 3-year call (1 May 2025) is… |
|---|---|---|
| ① first day below 80% | **14 May 2025** | **13 days early** (the code book's answer, Quiz 4 Q29) |
| ② first day the 30-day mean is below 80% | **20 Jun 2025** | **50 days early** |
| ③ last day at or above 80% | **24 Jul 2025** | — |

Between ① and ③, **49 of 72** days are below 80%: the readings bounce around the floor (daily noise is about ±0.15 points).

**Backtest the method: the battery call from four starting points:**

| Data used | Call made on | Predicted crossing | vs first dip | vs 30-day mean | Warning (to the first dip) |
|---|---|---|---|---|---|
| 1 year | 1 Jan 2022 | 1 Mar 2025 | −74 days | −111 days | 1,229 days |
| 2 years | 1 Jan 2023 | 7 Apr 2025 | −37 days | −74 days | 864 days |
| 3 years | 1 Jan 2024 | 1 May 2025 | −13 days | −50 days | 499 days |
| 4 years | 31 Dec 2024 | 18 May 2025 | +4 days | −33 days | 134 days |

The original code book says "only the four-year call goes a few days late". True only against the single noisy first dip; against the 30-day mean, **every** call is early.

**Why early:** a line through each calendar year gives −4.81, −4.69, −4.55, −4.45 and −4.34 % a year. The fade slows, so lines from early data land early. (The pepper task fits a curve, degree 2, on the same three years: **14 Jun 2025**, inside the real window.)

**Eclipse ageing:** eclipse seasons (27 Feb – 13 Apr and 1 Sep – 16 Oct) are **24.7%** of the days but carry **43.4%** of the battery's fade: **2.34×** faster per day than in sunlight.

**The long reach** (the line solved directly, fitted on 1–5 years of data):

| Data used | Amplifier → −2 dB | Propellant → 5 kg |
|---|---|---|
| 1 year | 27 Nov 2033 | 23 Oct 2035 |
| 2 years | 26 Jul 2033 | 13 Dec 2035 |
| 3 years | 4 May 2033 | 6 Dec 2035 |
| 4 years | 17 Mar 2033 | 14 Dec 2035 |
| 5 years | 24 Mar 2033 | 15 Dec 2035 |

The amplifier calls span about **8 months**; even the 5-year call reaches **7.2 years** past the last day of data. The propellant calls all sit within **53 days**, because the burns are so regular, but that holds only if the burn plan doesn't change. (The 3-year amplifier call shows as 4 May here and 5 May in A2: the formula rounds the fractional day down, `day_of_threshold` takes the first whole day below. Same line.)

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | "The danfo driver does remaining-useful-life sums every day without the name." The numbers are a story. | "When does the smart driver buy fuel?" (before the light comes on: Quiz Q24) |
| 4 | Facts from the toolkit fact sheet only. Our data is a **synthetic** platform. | "Would you bet the 2A/2B dates won't slip?" |
| 6 | Three shapes. The limits are known up front. | "Which part would you worry about first?" (the battery) |
| 7 | A burn every ~14 days. A straight line through a staircase is fine over years, wrong between two burns. | Quiz Q23 |
| 9 | Stand on 1 Jan 2024 with three years. Click to reveal what really happened. | "Is the gold line a good forecast?" |
| 10 | Six lines of code. `np.polyfit(x, y, 1)` → slope and intercept. Point at `np.argmax`. | Quiz Q20 |
| 11 | Battery and amplifier look fine… propellant says 1 Jan 2021. | "What went wrong?" (let them guess before slide 12) |
| 12 | `argmax` of all-False is 0. A confident wrong date with no error. | "Where else could a 'nothing found' turn into a fake answer?" |
| 13 | The line does reach 5 kg, just after the search stopped. Solve it directly. | — |
| 14 | The fuel-gauge sum agrees. Simple sums catch bugs. | — |
| 16 | Daily dots bounce around 80% for 72 days. Three honest definitions. | "Which one would operations care about?" |
| 17 | 13 days early or 50 days early: same forecast, two scores. | Quiz Q29 |
| 18 | Four starting points. More data, closer call, less warning. | Quiz Q30 |
| 19 | The fade slows, so a straight line from early data calls early. Early is the safe side for a battery. | "Would 'late' be safe for a battery?" (no) |
| 20 | The battery ages when it works: inverter in a NEPA-heavy month. | — |
| 21 | Amplifier: a planning figure with a range, re-estimated every year. | Quiz Q22 |
| 22 | Five rules, and the model sentences on the right. | Quiz Q24 |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `DAYS_PER_YEAR = 365` → −4.59 % a year | Typing 12 (months): the slope is per **day** |
| A2 | `COLUMN = "threshold"` → battery 1 May 2025, amplifier 5 May 2033, propellant `None` | Typing `80` or `threshold` without quotes: the cell asks for a column **name**, as text |
| A3 | `crossed_in_window = False` (and `np.argmax` said day 0) | `True` because "it printed a date": that's exactly the trap |
| A4 | `crossing_day = (5.0 - intercept) / slope` → 6 Dec 2035 | Swapping the order `(intercept - 5.0)`: gives a negative day; slope is negative, so keep `(5.0 - intercept)` |
| A5 | `RESERVE_KG = 5.0` → 10.1 years, about January 2036 | Typing 0: the reserve is not spare fuel |
| B1 | `FLOOR = 80.0` → 14 May, 20 Jun, 24 Jul 2025 | — |
| B2 | `KEY = "30_day_mean"` → (13, 50) | Spaces instead of underscores (KeyError): copy the key from the print |
| B3 | `YEARS = [1, 2, 3, 4]` → −74, −37, −13, +4 days; warning 1,229, 864, 499, 134 days | `YEARS = 4`: it must be a list |
| B4 | `"slows"` | "speeds up" because the line goes down faster… read the numbers: the yearly loss gets smaller |
| C1 | `ECLIPSE = 1` → 43.4% of the fade (on 24.7% of the days) | `True` also works (1 == True in Python) |
| C2 | `LAST = -1` → 7.2 years | `0` (that's the first day: gives about 12 years) |
| C3 | `"B"` | `"A"` because it's precise: a precise date 7 years out is false confidence |
| 🌶️ | `DEGREE = 2` → 14 Jun 2025, inside the real window | Warn: curves can go wild over long reaches; don't use degree 2 for the amplifier's 9 years |

## Quiz 4

- **Files:** `2-exercise/quiz/W6D2-quiz-4.pdf` (printable, no answers), `W6D2-quiz-4-google-forms.csv` (import), `4-instructor-only/W6D2-quiz-4-answer-key.pdf`.
- **Source:** the original `Time-series/MCQ/week-06-mcq.csv`, unchanged wording. Options reshuffled with a fixed seed (6203) so the correct letters are spread: multiple choice A ×6, B ×7, C ×6, D ×7; True/False A ×2, B ×2. (In the original file, most answers were option B.)
- **Topic → day:** forecasting baselines → W5D2 · regression-based forecasting → W5D3 · uncertainty and prediction intervals → W5D3 · backtesting → W6D1 (Q29–30 → today) · trend-to-threshold and remaining useful life → today.
- **All 30 answers match the data** (we re-ran every number: MAE 11.25 and 15.25, one-step naive 6.75, residual sd 2.84, held-out error sd about 7, coverage 5 of 8, battery call 1 May 2025, 13 days early, fold MAEs 1.27–7.67 with mean 4.01, naive wins 5 of 6 folds). No contested questions this time. Two notes for marking:
  - **Q29** ("the real crossing was 14 May 2025… how far off?", answer **13 days early**) uses the **first-dip** definition of "crossed". The answer stands. Use it to repeat today's point: against the 30-day mean the same call is 50 days early, so always say which definition you used.
  - **Q22** ("the amplifier call reaches about 9 years past the data") means past the **three years it was fitted on**: 1 Jan 2024 to 5 May 2033 is 9.3 years. From the end of the whole file (30 Dec 2025) it's about 7 years. Either way: a planning figure with a range.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `✅ Ready!` never appears | No internet in Colab, or the GitHub branch isn't public yet | Runtime → Restart session; check the link opens in a browser |
| A participant's dates are one day off a neighbour's | Formula (rounds down) vs `day_of_threshold` (first whole day below) | Same line. Say so and move on |
| `TypeError` with `NoneType` | They used `day_of_threshold`'s `None` as a number | That's the honest "no crossing": solve the line instead (A4) |
| The plot cell is slow | Three panels of 1,825 days | Wait a few seconds; it's fine |
| Someone asks "is this real NigComSat-1R data?" | — | **No.** A synthetic platform from the original code book. Real telemetry stays inside NIGCOMSAT (final-project data rules) |

## Final-project link

Brief **B (power and battery degradation)** and brief **D (capacity)** use exactly today's method. Their minimum method in the requirements: *a trend-to-threshold estimate giving a crossing date **and a window** (never a single day), with the assumptions stated*, and in the honest test: *the call repeated from several starting points, showing how the date and the warning time change*. Today's Part B table is the template. Next session is **demo day** 🎤.
