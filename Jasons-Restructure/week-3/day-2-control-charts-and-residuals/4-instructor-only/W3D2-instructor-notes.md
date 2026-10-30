# W3D2 Instructor Notes: Control Charts and Residuals

> **The one idea for today:** *an alarm should fire when a reading is surprising, not when it is big.* A control chart learns "normal" from a quiet stretch; a residual compares each reading with what we expected.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours |
| **Participants leave able to** | build a control chart from a reference period, explain 3σ as a false-alarm budget, keep one set of limits per operating state, use rolling robust limits (median + MAD × 1.4826), compute and health-check a residual, and say why rolling detectors miss shifts and drift |
| **Covers (original)** | Week 4 Code Book: *1. Bus power*, *2. TWTA thermal*; Week 4 quiz topics **statistical process control** (Q7–12) and **residual-based detection** (Q13–18) |
| **Datasets** | `Time-series/week-04/data/bus_power_telemetry_hourly.csv`, `Time-series/week-04/data/twta_thermal_daily.csv` (the **week-04** version, which has the injected events) |
| **Files you need open** | animated slides, your **solution** notebook, the rule book PDF |

> 🤫 **Don't show the label (answer-key) file today.** It's introduced on W4D1 when we score detectors. The checks know the answers without revealing the file.

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | Mama Put's tomato prices: knowing "normal" lets you spot "strange" | 1–2 |
| 0:08 | **Control charts** | Anatomy → reference period → August dropout → why 3σ | 3–7 |
| 0:25 | **States & staleness** | Three operating states; the August band goes stale; rolling robust fix | 8–11 |
| 0:40 | **Tampering & run rules** | Common vs special cause; Rule 2 for level shifts | 12–13 |
| 0:48 | **Residuals** | Observed − expected; raw chart misses the spike, residual nails it; health checks; centred windows; three shapes | 14–20 |
| 1:00 | **Hands-on** | Part A (25 min), Part B (35 min). Walk the room. | 21 |
| 1:45 | **Wrap-up** | Scoreboards, recap, tease CUSUM | 22 |

## Explain it like this (plain English)

- **Control chart:** learn the average and the wobble (σ) from a calm stretch. Anything beyond 3 wobbles from the average is unusual.
- **Why 3σ:** it's a budget. On normal data, ±3σ is crossed by chance about 0.27% of the time (≈ 8 alarms in 2,880 hours). ±2σ: ≈ 131 alarms, and people stop listening.
- **Operating states:** eclipse, recharge and sunlit are three different "normals". Mix them and σ grows from 0.073 A to 0.594 A, and the chart goes blind. Fix: one set of limits per state. Not wider limits, not deleting eclipse hours, not 2σ.
- **Stale reference:** the array's normal output slowly climbs through the season (about 27.9 → 28.3 A daily average). A fixed August band flags 1,861 of 2,696 sunlit hours by November. Fix: rolling limits learned from the trailing week.
- **Robust:** the median and MAD ignore a few wild points; mean and σ don't. × 1.4826 converts MAD to the same size as σ.
- **Tampering:** reacting to everyday wobble as if it were a real change. Adjusting after every reading makes things worse (spread +39% in our simulation; theory says +41%).
- **Residual:** observed − expected. The amplifier runs hotter with higher drive and with the sun angle, so a big temperature isn't automatically a surprise. The recipe removes what we understand; what's left is the surprise.
- **The three shapes:** a residual catches **spikes**. A *fixed* recipe also shows a **level shift** (every day after 12 May is flagged), but a *rolling* "expected" swallows the shift in about three weeks and never sees a **slow drift**. That's tomorrow's CUSUM.

## Numbers you'll quote (all computed from the data)

| What | Value |
|---|---|
| Hours / states | 2,880 hours: 46 eclipse, 138 recharge (3 h after each eclipse), 2,696 sunlit |
| Mean current by state | eclipse 0.03 A · sunlit 28.14 A · recharge 29.59 A |
| Reference period 1–15 Aug | 360 hours, centre 27.87 A, σ 0.073 A, limits 27.65–28.09 A |
| σ over all sunlit hours incl. recharge | 0.594 A (8× bigger) |
| Fixed August band, whole file | 1,861 of 2,696 sunlit hours outside |
| Dropouts (in sunlit hours) | 18 Aug 09:00 · 28 Sep 14:00 & 15:00 · 31 Oct 03:00, all ≈ 15.3–15.5 A (about 55% of normal) |
| Rolling robust limits (168 h trailing, sunlit only) | 5 flags = the 4 dropout hours + 1 false alarm (1 Sep 00:00) |
| The 1 false alarm | 1 Sep 00:00 reads 29.48 A, a recharge-sized value with no eclipse flagged before it. Most likely the season's first, very short eclipse didn't show up in the hourly flag. A real "special cause", not a fault |
| Mean/σ rolling version | ±2σ: 31 flags · ±3σ: 5 flags |
| σ right after the first 28 Sep dropout hour | plain 1.08 A vs robust 0.09 A |
| Tampering simulation | spread × 1.39 |
| TWTA raw | mean 63.90 °C, σ 1.97 °C, 3σ ceiling 69.81 °C; spike 68.15 °C on 3 Sep 2024: **inside** the raw band |
| Recipe (refit without spike days) | temp ≈ 49.5 + 0.174 × drive + sun-angle wave; residual σ 0.22 °C |
| Spike as residual | +5.0 °C = 23σ on 3 Sep (15σ on 4 Sep) |
| Health checks | all 2024: lag-1 0.33, spread 0.22 / 0.49 → **not clean**; without the 2 spike days: lag-1 0.06, spread 0.22 / 0.22 → clean |
| After 12 May 2025 | 233 of 233 days beyond 3σ; mean residual +2.59 °C |
| Rolling 30-day median detector | spike 11 robust σ (caught); 0 flags after 12 May (shift swallowed in ~3 weeks) |
| Centred vs trailing 7-day window at the spike | centred mean residual +4.0 °C vs trailing median +5.3 °C |

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 2 | "Mama Put never studied statistics, but she has a control chart in her head." | "How do you know a price is too high?" |
| 5 | The original code book says σ ≈ 0.06 A. That's only true for a clean fortnight like this one. | — |
| 6 | 18 Aug: half the normal output in full sun. NigComSat-1 was lost in 2008 to a solar-array problem; this is why we watch the array. | "Fault or normal?" |
| 7 | 3σ is a budget, not a magic number. | "Would you answer 131 alarms in 4 months?" |
| 8 | Click to reveal the rule: one set of limits per state. | "What happens to σ if we mix eclipse hours in?" |
| 9 | Not 1,861 faults. The *reference* is stale. | "Is the satellite broken in November?" |
| 12 | Tell the brake-pumping driver story. | "Who has worked with a boss who tampers?" 😄 |
| 16 | The raw band has to be wide because temperature has known drivers. | "Can a 3σ line on raw temperature catch this spike?" |
| 18 | Click to show the table. Two bad days spoiled the recipe; the health checks caught it. | — |
| 20 | Cliffhanger: rolling detectors are blind to slow change. | "How would *you* catch a landlord who adds small-small?" |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `(bus["state"] == "recharge").sum()` → **138** | Counting eclipse hours (46) instead |
| A2 | `ref.mean()` → **27.87**, `ref.std()` → **0.073** | Using the whole file instead of `ref` |
| A3 | `centre - 3 * sigma` → **27.65**, `centre + 3 * sigma` → **28.09** | Giving ucl first (order is lcl, ucl) |
| A4 | `outside.sum()` → **1,861** | Thinking it's wrong because it's huge. It's the lesson: stale reference |
| A5 | `hours * 0.0027` → **7.8**, `hours * 0.0455` → **131** | — |
| B1 | `(z.abs() > 3).sum()` → **5** | Forgetting `.abs()` (counts only one side) |
| B2 | `"b"`, `"c"` | — |
| B3 | `tw["twta_temp_c"] - expected` (on 3 Sep 2024: **+4.95 °C**) | Reversing the order (expected − observed) |
| B4 | `"no"` (lag-1 0.33, spread 0.22 vs 0.49) | Saying "yes" because the mean is 0. One check isn't enough |
| B5 | `residual[train].abs().idxmax()` → **2024-09-03** | Using `idxmin()` |
| B6 | `residual2.loc["2024-09-03"] / sigma2` → **≈ 22.8** | Dividing by the raw σ (1.97) |
| B7 | `(z2.loc["2025-05-12":].abs() > 3).sum()` → **233** (of 233) | — |
| B8 | `(rz.loc["2025-05-12":].abs() > 3).sum()` → **0** | Thinking 0 is a bug. It's the cliffhanger |
| 🌶️ | `tampered.std() / calm.std()` → **≈ 1.39** | — |

## Quiz link (original Week 4 quiz, `Time-series/MCQ/week-04-mcq.csv`)

| Q | Tests | Where it's taught |
|---|---|---|
| 7 | Common vs special cause → *tampering* | slide 12, bonus |
| 8 | Control limits = 3σ around the reference mean | slide 4, A2–A3 |
| 9 | 3σ budget: ≈ 8 false alarms in 2,880 hours | slide 7, A5 |
| 10 | Exclude eclipse hours from the reference | slide 8, A1 |
| 11 | Run rule 2 → level shifts | slide 13 |
| 12 | One chart (set of limits) per operating state | slide 8 |
| 13 | Residual = observed − expected | slide 15, B3 |
| 14 | Median + MAD: extreme points can't move them | slide 11, B2 |
| 15 | MAD × 1.4826 ≈ σ | slide 11, B2 |
| 16 | A centred window absorbs part of the spike (True) | slide 19 |
| 17 | Rolling residual detector is useless on slow drift | slide 20, B8 |
| 18 | "Values all above zero" is NOT a health check | slide 18, B4 |

## Troubleshooting

| Problem | Fix |
|---|---|
| A chart cell fails with the "Do A2 and A3 first" message | Normal: they skipped a task. Fill the blanks above |
| B-part `NameError: name 'bus' is not defined` | Runtime restarted. Run STEP 0 and Part A again |
| Someone's B6 is about 13 | They used `residual` (spoiled recipe) instead of `residual2` |
| Fast finishers | Ask them to change the trailing window in B1 from 168 to 24 hours and see what happens to the false alarms |

## Notes on the original material

- The original says the sunlit baseline σ is ~0.06 A with a 27.6–28.0 A band. On the real file, all sunlit hours give σ 0.594 A (band 26.43–29.99 A) because recharge hours and the dropouts are mixed in. Only a clean reference fortnight gives a small σ (0.073 A). We teach exactly that difference.
- The original's Week 3 table says the TWTA file has no anomalies. That's the **week-03** copy; the **week-04** copy (used today) has the 3 Sep 2024 spike and the 12 May 2025 shift.
- The original names "four injected events" in the bus file in one place and three in another. There are **three events (four hours)**: 18 Aug, 28 Sep (two hours), 31 Oct.
