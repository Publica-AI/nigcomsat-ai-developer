# W3D1 Instructor Notes: Alarms That Cry Wolf

> **The one idea for today:** *a fixed alarm limit is already a model, and a model that ignores context cries wolf.* The fix is to add context (which state is the satellite in?), not to widen the limit.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours |
| **Participants leave able to** | build an alarm as a True/False column, count and time its alarms, add context with `&`, derive a limit from data (mean − 3σ), and name the three anomaly shapes |
| **Covers (original)** | Week 4 Code Book sections **1. Bus power** and **4. RF link quality**; Week 4 quiz topic *what your alarm software already does* (questions 1–6 of `week-04-mcq.csv`) |
| **Datasets** | `week-04/data/bus_power_telemetry_hourly.csv` (identical to the week-03 copy), `rf_link_quality_hourly.csv`, plus a peek at `twta_thermal_daily.csv` and `battery_health_daily.csv` (week-04 versions, which contain the faults) |
| **Withhold** | The label file `telemetry_anomaly_labels.csv`. It's the answer key, introduced on **W4D1**. Today's participant materials never show it |

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | NigComSat-1 lost in 2008 to a solar-array anomaly → "watch the array" | 1–3 |
| 0:10 | **The alarm you already have** | A limit is a model; the four tricks of alarm software; "where did that number come from?" | 4–7 |
| 0:22 | **Cry wolf** | Eclipse = the satellite's NEPA; 50 alarms, 46 useless; alarm fatigue; the context fix; battery temperature | 8–13 |
| 0:35 | **Where should the limit be?** | 3σ from sunlit data; what IS normal?; rain vs outage; persistence trap; leaking the answer; three shapes | 14–20 |
| 0:50 | **Hands-on** | Part A (20 min), Part B (15 min), Part C (25 min) | 21 |
| 1:50 | **Wrap-up** | Recap; ask each person to name one alarm in their unit that cries wolf | 22 |

## Explain it like this (in plain English)

- **A threshold is a model.** "Below 20 A = bad" is a tiny anomaly detector. It can be good or bad, and we can measure which.
- **Eclipse.** Twice a year, around the equinoxes, the Earth's shadow crosses the satellite once a night (here at 21:00 UTC, 22:00 in Lagos). The array current drops to zero and the battery takes over. It's the satellite's "NEPA has taken light", and it is completely normal.
- **Why the floor cries wolf.** A 20 A floor fires every eclipse night (46 times) and on the 4 real dropout hours. 46 of 50 alarms are useless, so the NOC learns to ignore the channel. That's alarm fatigue.
- **The fix.** `& (bus["eclipse_flag"] == 0)`: only check the limit in sunlight. 50 → 4 alarms, all real. Don't widen the limit; that would hide the dropouts too.
- **Where should the limit be?** Use normal data: mean − 3σ. But "normal" is slippery: the 4 dropouts alone stretch σ from about 0.17 to about 0.52 A, and the post-eclipse recharge boost stretches it to 0.59. Define normal per state. Day 2 does this properly with control charts.
- **Rain is not a fault.** In heavy rain C/N falls whether or not the link drops. Link margin below 0 dB is the honest outage definition.
- **Persistence.** "Only alarm after 2 hours" sounds wise, but every August outage lasted exactly 1 hour, so it catches none of them.
- **Leaking the answer.** Uplink power rises *because* of rain (power control). A detector fed with it learns "is it raining?", not "is the link broken?".
- **Three shapes.** Spike (a short dip), level shift (a new normal), drift (a slow slide). Fixed limits only really catch spikes.

## Numbers you'll quote (all computed from the data)

| What | Value |
|---|---|
| Bus power file | 2,880 hourly rows, 1 Aug – 28 Nov 2025, no gaps |
| Eclipse hours | **46**, all at 21:00 UTC, from 1 Sep to 16 Oct |
| Floor `array < 20 A` | **50** alarms = **46** eclipse + **4** real |
| With context (`eclipse_flag == 0`) | **4** alarms, all real |
| SoC floor `< 82%` | **18** alarms, **all 18** in eclipse (SoC ranges 77.3–99.6% across eclipse hours) |
| Battery temp `> 22 °C` | **50** alarms = **46** in the hour after eclipse + **4** real |
| Sunlit array current | mean **28.21 A**, σ **0.594 A** → 3σ band **26.43–29.99 A** → **4** hours outside (the dropouts) |
| Same, without recharge hours and dropouts | σ **0.169 A** → band **27.65–28.66 A** → **143** sunlit alarms, **138** of them recharge hours |
| RF, August | 744 hours, **56** rainy, **12** outages (margin < 0 dB), every outage 1 hour long, every one in rain ≥ 39.3 mm/hr |
| 3σ on C/N, all hours | floor **10.76 dB** → **18** alarms, **12** real, 6 just rain |
| 3σ on C/N, dry-hour baseline | floor **14.06 dB** → **49** alarms, **12** real (**76%** false) |
| 2-hours-in-a-row rule | catches **0** of 12 outages |
| Uplink power vs rain | correlation **0.97**; mean **41.2** dBm dry vs **44.1** dBm in rain |
| TWTA (week-04) | 3σ ceiling **69.8 °C**, hottest day **68.2 °C** (3 Sep 2024): fires **0** times; level shift **65.2 → 67.4 °C** in May 2025 |
| Battery capacity (week-04) | **103.3 → 95.4 Ah** (min 95.39); a 95 Ah limit fires **0** times |

## 🔒 The hidden events (instructor only)

These are in the label file that participants see on W4D1. Today they find them without it.

| Event | When | What | How it shows today |
|---|---|---|---|
| EV01 | 18 Aug 2025 09:00 | Solar-array dropout (minor) | array 15.34 A, battery 23.0 °C |
| EV02 | 28 Sep 2025 14:00–15:00 | Two-hour dropout with thermal excursion (major) | array ~15.5 A, battery ~22.9 °C (the bonus date) |
| EV03 | 31 Oct 2025 03:00 | Solar-array dropout (minor) | array 15.54 A |
| EV04 | 3–4 Sep 2024 | TWTA transient spike | 68.15 °C, below the 3σ ceiling |
| EV05 | from 12 May 2025 | TWTA level shift (cooling-loop blockage) | the "level shift" chart in C4 |
| EV06 | from 1 Apr 2025 | Battery fade speeds up 1.6× (the label file says "roughly doubles") | the "drift" chart in C4 |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `bus["eclipse_flag"].sum()` → **46** | — |
| A2 | `floor_alarm.sum()` → **50** | — |
| A3 | `(floor_alarm & (bus["eclipse_flag"] == 1)).sum()` → **46** | `and` instead of `&` → "ambiguous truth value" error |
| A4 | `(bus["battery_soc_pct"] < 82).sum()` → **18** | — |
| A5 | `SUNLIT = 0` → 4 alarms left | Writing `"0"` (text) |
| B1 | `sunlit.mean() - 3 * sunlit.std()` → **26.43** | Using `bus["solar_array_current_a"]` (includes eclipse: band 17.0–38.5 A) |
| B2 | `(sunlit < low_limit).sum()` → **4** | — |
| B3 | `(hot & after_eclipse).sum()` → **46** | — |
| C1 | `(cn_flags.sum(), (cn_flags & outage).sum())` → **(18, 12)** | Giving one number |
| C2 | `two_in_a_row.sum()` → **0** | They expect a positive number. That's the lesson |
| C3 | `"no"` | — |
| C4 | `("spike", "level shift", "drift")` | Mixing up shift and drift. A shift jumps, a drift slides |
| C5 | `(bat["est_capacity_ah"] < 95).sum()` → **0** | — |
| 🌶️ | `"2025-09-28"` | — |

## Quiz link

Week 4 quiz (`Time-series/MCQ/week-04-mcq.csv`), topic **"what your alarm software already does"**, questions 1–6: threshold is a model (slide 5), seasonal false alarms (slide 10), silent degradation (slide 20 + C5), three shapes (slide 20 + C4), leaking the answer (slide 19 + C3), where thresholds come from (slide 7). Quiz 2 runs on **W4D1**.

## Troubleshooting

| Problem | Fix |
|---|---|
| "The truth value of a Series is ambiguous" | They used `and`/`or`. Use `&`/<code>&#124;</code> with brackets around each comparison |
| A5 gives 0 alarms | They wrote `SUNLIT = 1` or `"0"`. Sunlit is the number `0` |
| The C4 charts look empty | `tw`/`bat` didn't load. Re-run the C4 code cell |
| Someone asks "can we see the real answer key?" | "On Week 4 Day 1. First you build detectors without peeking, just like real life" |

## Notes on the original material

- **The SoC example doesn't match the data.** The Week 4 code book and quiz say a SoC < 82% floor "fires on all 46 eclipse hours". It fires **18** times (all in eclipse). Eclipse SoC ranges 77.3–99.6%; only a floor above 99.6% would catch all 46. The lesson (correct but useless) holds, so slides use the honest 18 and the array-current floor for the 46. Quiz 2 Q2 uses the honest 18 too.
- **The sunlit standard deviation.** The code book says σ ≈ 0.06 A and a band of 27.6–28.0 A. The data gives σ = **0.594 A** and **26.43–29.99 A**, because the post-eclipse recharge hours (up to 29.8 A) and the dropouts themselves are in "sunlit". Even with both removed, σ is 0.169 A. Monthly σ is 0.07–0.10 A, closest to the original's figure.
- **RF naive rule.** The code book says a 3σ rule on C/N flags "roughly all 56 rainy hours, 79% false alarms". With σ from all hours it flags **18** (6 false). The original figure matches a *dry-hour* baseline: **49** flags, 76% false. Both are shown on slide 17.
