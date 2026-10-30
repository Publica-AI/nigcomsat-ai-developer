# W2D3 Instructor Notes: Lab Day + Quiz 1 + Pick Your Project

> **The one idea for today:** *you already know enough to answer a real operational question from start to finish.* Today they prove it to themselves, then point that skill at their own unit's problem.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours (recap 15 · lab 50 · quiz 20 · project kickoff 25 · wrap-up 10) |
| **Participants leave able to** | run a full investigation unaided, write a 4-sentence finding, name their final-project brief and process, and send the unit-head email |
| **Covers (original)** | Week 3 review (all five Week 3 topics); the Week 3 quiz (`Time-series/MCQ/week-03-mcq.csv`); the capstone brief (`Time-series/module-project/`) |
| **Lab dataset** | `Time-series/week-03/data/battery_health_daily.csv` (**the week-03 version**) |
| **Files you need** | animated slides · your **solution** notebook · `2-exercise/quiz/` (Google Forms CSV + printable PDF) · `W2D3-quiz-1-answer-key.pdf` · `W2D3-project-kickoff-worksheet.pdf` · the final-project requirements PDF |

## The day before: checklist

<ul class="check">
<li>Run your <b>solution</b> notebook top to bottom: 11 of 11 ✅.</li>
<li>Decide how to run Quiz 1: <b>printed</b> (<code>W2D3-quiz-1.pdf</code>, one per person) or <b>online</b> (import <code>W2D3-quiz-1-google-forms.csv</code> into Google Forms with a quiz add-on, or type the 30 questions in; turn on “Make this a quiz”).</li>
<li>Print or share the <b>project kickoff worksheet</b>.</li>
<li>Have the <b>final-project requirements PDF</b> ready to share in the group chat.</li>
<li>Think of one real NIGCOMSAT process per unit in the room. It helps people who are stuck choosing.</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Recap game** | 8 rapid questions. Read, let the room shout, click to reveal | 1–4 |
| 0:15 | **Lab intro** | The oga's question, the 7 steps, the twin-file trap, the 4-sentence finding | 5–7 |
| 0:20 | **Lab** | Mini investigation, 10 checks + bonus. You walk the room | — |
| 1:05 | **Quiz 1** | 30 questions, 20 minutes, solo | 8 |
| 1:25 | **Project kickoff** | What it is, 5 briefs, how to choose, data rules, checkpoints, the email | 9–14 |
| 1:50 | **Wrap-up** | Read out the quiz letters, discuss the most-missed questions, recap | 15 |

## Recap game: answers and where the numbers come from

| # | Question | Answer | Source |
|---|---|---|---|
| 1 | Shuffle the rows: still a time series? | No: order carries information | W1D1 |
| 2 | 1,093 rows for 1,096 days | `.asfreq("D")` shows the 3 gaps as NaN | W1D1 B5 |
| 3 | 11 August days had a link-down hour; how many had a negative daily mean? | **Zero**: lowest daily mean was **4.91 dB**. SLAs come from the minimum | `rf_link_quality_hourly`: 12 outage hours over 11 days |
| 4 | Weekend tickets ≈ half of weekday | 7-day window. Weekend **3.36** vs weekday **7.06** (48%) | `noc_tickets_daily` |
| 5 | Trailing or centred for a live dashboard? | Trailing: centred uses the future | W1D3 |
| 6 | Period for daily NOC tickets | **7**: the working week | W2D1 |
| 7 | Lag 1 = 0.58, lag 7 = 0.99 | Weekly repeat: “same weekday last week” is a strong guess | `bandwidth_throughput_daily` |
| 8 | TWTA temp vs RF drive 0.59: cause? | Not proven: **0.40** after differencing (shared trend) | `twta_thermal_daily` (week-03) |

> ⚠️ The original Week 3 code book says the TWTA correlation “collapses” after differencing and that throughput lag-1 is “around 0.83”. The real numbers are 0.59 → 0.40 and 0.58. Use ours.

## Lab answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| L1 | `"week-03"`, `"date"`, `"D"` | Choosing week-04 → “that's the twin with planted faults; we use it in Week 3” |
| L2 | **1,096** rows, **0** empty cells, **0** duplicates | Using `.isna().sum()` (per column) instead of `.sum().sum()` (whole table) |
| L3 | **2025-09-24** (inside the September eclipse season) | Using `>` instead of `<`; taking `[-1]` instead of `[0]` |
| L4 | Any finding sentence | “Capacity” alone is a label, not a finding |
| L5 | Accept **175–190** or **355–370** days. Solution uses 365 | Choosing 7 or 30: that smooths noise, not the half-year pattern |
| L6 | **0.222 V** with a 365-day window (0.279 V with 183 days). The check uses *their* window | Forgetting `.dropna()`, so `iloc[0]` is NaN |
| L7 | **12** (calendar year, 3 full cycles) or **6** (half-year, one eclipse season to the next): both accepted | Choosing 7 (“that's for the working week, not monthly battery data”) |
| L8 | **March and September**: the equinoxes, two eclipse seasons a year | Picking only one month |
| L9 | **6**: the tallest bar after lag 1 (0.83). Lag 12 is next (0.67) | Counting lag 0 (always 1.0) |
| L10 | Four sentences of 25+ characters, with a number in the Observation | Missing number; a Recommendation that's not an action |
| 🌶️ | **2025-04-03**: week-04 fades faster from there (last day 95.42 Ah vs 96.57 Ah) | Comparing different columns |

**Why the lab works on this file:** the battery has two eclipse seasons a year, so decomposition and the correlogram both reveal a **6-month** rhythm that a “one hump a year” assumption would miss. That's the “period comes from the process” lesson in action. The capacity fade is also a mini version of final-project brief B.

**Note on lag 6 vs 12:** `statsmodels` `acf()` / `plot_acf()` (used in the notebook) puts lag 6 on top. pandas' `Series.autocorr(12)` gives 0.998 vs 0.986 at lag 6, because it computes each lag on a shorter overlap. If someone uses `autocorr`, explain the difference and point them to the correlogram.

## Quiz 1

- **Source:** the original 30 Week 3 questions (`Time-series/MCQ/week-03-mcq.csv`; that file is unchanged). Two are edited here: Q5 no longer mentions "the code book", and Q30 uses the suya example because the original's TWTA claim doesn't match the data. The answer key lists both.
- **Our version:** options reshuffled so the correct answers are spread across A–D. In the original, **74% of correct answers were option B**: anyone who always picks B scores about 74%. Don't mention this to participants.
- **Files:** `2-exercise/quiz/W2D3-quiz-1.pdf` (printable, no answers), `W2D3-quiz-1-google-forms.csv` (for quiz tools), `4-instructor-only/W2D3-quiz-1-answer-key.pdf`.
- **Marking:** read out the letters in the wrap-up; re-explain any question more than a third of the room missed, using that day's slides.

## Project kickoff: talking points

| Slide | Say this |
|---|---|
| 9 | “This is individual, on your own unit's real data, and it ends with a tool your colleagues can open.” |
| 10 | Read each brief's Naija question. Ask: “Whose unit does this sound like?” |
| 11 | The most common failure is a vague topic. Push everyone to name a process **with an owner**. |
| 12 | The data rules are not optional. **Real data does not go into Colab** unless the unit head agrees in writing. Committing restricted data is a serious failure. |
| 13–14 | Homework: worksheet + email before Week 3 · Day 3. A reply email is enough as the agreement. |

**Good example processes to suggest** (adapt to who's in the room): weekly battery-health review on the bus subsystem (B) · VSAT site fault escalation in the NOC (E) · transponder capacity planning for sales (D) · earth-station link monitoring during the rainy season (C) · daily telemetry review by the satellite control team (A).

## Troubleshooting

| Problem | Fix |
|---|---|
| `KeyError: 'timestamp'` in L1 | This file's time column is `date`. Look at the CSV header |
| Decomposition error “must have 2 complete cycles” | Period too big: 36 months allows at most 18 |
| Someone finishes the lab in 25 minutes | 🌶️ bonus, then ask them to review a neighbour's 4-sentence finding |
| Someone can't think of a process | Pair them with someone from the same unit; use the example list above |
| “My unit's data isn't accessible” | They still pick a brief and process today, and ask the unit head about access in the email. The synthetic files only count if the unit head confirms in writing that no real data is available |
