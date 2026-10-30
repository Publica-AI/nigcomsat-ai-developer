# W3D3 Instructor Notes: The Slow Creep: Drift and CUSUM

> **The one idea for today:** *some faults never produce a single scary reading. You catch them by adding up small leftovers (CUSUM) or by watching the speed of change (rolling slope).*

## At a glance

| | |
|---|---|
| **Length** | ~2 hours, including 15 minutes for the final-project Checkpoint 2 |
| **Participants leave able to** | name spike / level shift / drift; write CUSUM from scratch; set k and h from σ; tell alarm date from start date; watch a rolling slope for drift |
| **Covers (original)** | Week 4 topic *change points and drift*; Week 4 Code Book sections **2. TWTA thermal** and **3. Battery health** |
| **Datasets** | `Time-series/week-04/data/twta_thermal_daily.csv`, `Time-series/week-04/data/battery_health_daily.csv` (the **week-04** versions, the notebook default) |
| **Files you need open** | animated slides, your **solution** notebook, the rule book PDF, the final-project checkpoint table |

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | Landlord's rent: small-small increases add up to ₦415k | 1–3 |
| 0:08 | **Three shapes** | spike vs level shift vs drift | 4 |
| 0:12 | **The amplifier** | 3σ rule fires 0 times; zoom: 6.9σ locally; take away what you know | 5–8 |
| 0:25 | **CUSUM** | the one line; by-hand table (press → to fill S); k and h | 9–11 |
| 0:35 | **CUSUM in action** | real step caught on day 1; small practice fault caught in 3 days; choosing h | 12–14 |
| 0:45 | **The battery** | never crosses 95 Ah; speed 1.6× faster; rolling slope crosses −3.0 | 15–18 |
| 0:50 | **Toolbox** | right tool for each shape | 19 |
| 0:52 | **Hands-on** | Part A (15 min), Part B (30 min), Part C (15 min) | 21 |
| 1:45 | **Checkpoint 2** | one by one: unit head's reply + profiled data (see below) | 20 |
| 1:55 | **Wrap-up** | recap; tease the answer key on Week 4 Day 1 | 22 |

## Explain it like this

- **Spike / level shift / drift.** A spike goes up and comes back. A level shift steps up and stays. A drift leans: the slope changes.
- **Why a 3σ rule misses the amplifier's step.** σ of the whole two years (1.97 °C) is inflated by the yearly sun-angle swing and the rising drive level, so the ceiling sits at 69.81 °C. The hottest day ever is 68.15 °C, so it fires 0 times. Against the 30 days before (σ 0.32 °C), the +2.17 °C jump is 6.9σ.
- **Take away what you already know.** `expected_temp()` learns "normal" from 2024: drive level + sun angle (sin/cos of day of year) + slow ageing (a straight line in time). Its second pass ignores the 2-day hot spike of 3–4 Sep 2024 so it doesn't bend "normal". The leftovers have σ = 0.20 °C, average −0.01 °C from January to 11 May 2025, and +1.83 °C from 12 May. That matches the +1.8 °C step hidden in the file.
- **CUSUM.** Every day: `S = max(0, S + leftover − k)`. Small positive leftovers pile up; the slack k stops ordinary noise piling up; the floor at zero stops calm days banking credit. Alarm when S > h.
- **k and h.** Both are multiples of σ of the leftovers in a calm period: k = 0.5σ (0.10 °C), h = 5σ (1.02 °C).
- **Alarm date ≠ start date.** CUSUM needs evidence, so it always rings after the change began. Best guess of the start: the day after S was last zero.
- **Rolling slope.** The battery never crosses 95 Ah, so a threshold sleeps. The fade speed goes from −2.24 to −3.68 Ah per year. A 90-day trailing slope crosses a −3.0 warning line 31 days after the true change, because a trailing window needs time to fill with the new behaviour.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | "No single year shocks you. The total does." | "Who has a landlord like this?" 😄 |
| 6 | "Zero alarms in two years. Is the amplifier fine?" | "Can you spot the step?" |
| 7 | 65.20 → 67.37 °C. 6.9σ locally, 1.1σ against the whole series. | "Why does the same jump look big and small?" |
| 10 | Press → seven times; S fills in. Day 4 starts the climb; day 7 alarms. | "When did it START?" (day 4) |
| 12 | S was 0.90 on 11 May, 2.86 on 12 May; h = 1.02. Same-day alarm because the step is ~9σ of leftovers. | — |
| 13 | The point rule saw 0 hits in 30 days. CUSUM: 13 Feb. Trace back: 10 Feb. ✅ | "How did we know it was 10 Feb?" |
| 14 | 2σ: 10 false alarms / 1 day. 5σ: 0 / 3 days. 10σ: 0 / 6 days. | "Which would you choose for an amplifier? For an email alert to the MD?" |
| 18 | 31 days late, and that is the price of a trailing window. | — |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `"spike"`, `"level shift"`, `"drift"` | "level_shift" or "Level Shift" are accepted |
| A2 | `S = max(0, S + x - k)` → `[0, 0, 0, 0.5, 1.2, 1.6, 2.2]` | forgetting `max(0, …)` → negative values; forgetting `- k` → noise piles up |
| A3 | start day **4**, alarm day **7** | answering 3 (the last zero), not the day after |
| A4 | `"b"` (slack) | "a": k is not the alarm line; that's h |
| B1 | **0** days above 69.81 °C | — |
| B2 | **6.9** σ (65.20 → 67.37 °C, local sd 0.32) | dividing by the whole-series sd gives 1.1 |
| B3 | **+1.83** °C | forgetting to fill `expected` |
| B4 | k = **0.102**, h = **1.016** °C (σ = 0.2031) | swapping k and h |
| B5 | **2025-05-12** (delay 0 days) | — |
| B6 | alarm **2025-02-13**, start **2025-02-10** | giving `last_zero` (9 Feb) instead of the day after |
| C1 | **0** days below 95 Ah (lowest 95.39) | using the week-03 file |
| C2 | **−2.24 → −3.68** Ah/yr (1.6× faster) | slicing `"2025-04-01"` into both halves |
| C3 | **2025-05-02** (31 days after 1 Apr 2025) | typing `3.0` instead of `-3.0` |
| 🌶️ | **10** false alarms with h = 2σ in 404 calm days | counting all alarms, not just those before the start |

**The secret fault** (instructor only): `practice_residuals()` adds **+0.3 °C (≈1.5σ) from 10 Feb 2025** to the amplifier's calm leftovers (Jan 2024 to 11 May 2025, minus the 2 spike days). A 3σ point rule catches 0 of the first 30 days.

## Quiz link

Original Week 4 quiz (`Time-series/MCQ/week-04-mcq.csv`), topic **"change points and drift"**, questions **19–24**:

| Q | Taught on |
|---|---|
| 19 Shift vs drift | slide 4, task A1 |
| 20 What CUSUM accumulates | slide 9, task A2 |
| 21 The slack k | slide 11, tasks A4, B4 |
| 22 Alarm date vs onset (False) | slides 10, 13, task A3, B6 |
| 23 Battery fade knee → rolling slope | slides 17–18, task C3 |
| 24 TWTA 6.9σ missed by a 3σ point rule | slides 6–7, tasks B1–B2 |

These come up again in Quiz 2 on Week 4 Day 1.

## 🏁 Final project · Checkpoint 2: 📥 Data in hand (15 min)

Matches `week-6/final-project/Final-Project-Requirements.pdf`. Go round one by one:

| Check | Pass if |
|---|---|
| Unit head's agreement | an **email reply** naming the process, the data and who it's for |
| Data in hand | loaded with a DatetimeIndex, one time zone, `.asfreq()` |
| Profile | rows, date range, gaps, duplicated timestamps reported |
| Honest plot | the operational threshold drawn, with a title that states a finding |
| Data rules | real data on NIGCOMSAT systems only (not Colab); nothing raw on GitHub |

No reply yet? Agree a follow-up date with them today. Anyone planning to use only synthetic data needs **written** agreement from their unit head that no real data can be made available. Next checkpoint: **Week 4 · Day 3: method drafted.**

## Troubleshooting

| Problem | Fix |
|---|---|
| CUSUM fires in January | `- k` is missing in the loop, or k and h were swapped |
| B6 start one day early | they returned `last_zero`; it must be `last_zero + pd.Timedelta(days=1)` |
| Battery numbers don't match | they loaded `week="week-03"`; use the default (week-04) |
| `rolling_slope` feels slow | it fits 1,000+ small lines; a few seconds is normal |

## Notes on the original material

- The original Week 4 code book has **no CUSUM code**; we wrote it from scratch.
- Original battery fade rates: *"−2.4 Ah/year before, −4.0 after"*. The data gives **−2.24 and −3.68** (a straight-line fit before and after 1 April 2025). The slides use the data's numbers.
- The original says the TWTA step is *"6.9σ against local spread"*: correct (65.20 → 67.37 °C, local sd 0.32).
- The **week-03** and **week-04** files named `battery_health_daily.csv` and `twta_thermal_daily.csv` differ: only week-04 has the step, the 2-day hot spike and the fade speed-up. The notebook default is week-04.
