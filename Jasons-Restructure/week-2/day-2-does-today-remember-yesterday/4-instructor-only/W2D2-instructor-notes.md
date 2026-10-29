# W2D2 Instructor Notes: Does Today Remember Yesterday?

> **The one idea for today:** *data has memory, and you can measure it.* Line a series up with its own past (a lag) and the correlation tells you how much it remembers. The pattern of that memory across lags (the correlogram) reveals the season, and warns you about trends and fake correlations.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours |
| **Participants leave able to** | make a lag with `.shift()`, compute `.autocorr()`, read a correlogram (spikes / slow decay / band), find a period from data, explain why random splits leak, and test a correlation with `.diff()` |
| **Covers (original)** | Week 3 Code Book **B7 Bandwidth throughput** (autocorrelation), **A4 TWTA thermal** (two trending series), **A3 RF link quality** (uplink power responds to rain), *Seasonal periods at a glance*; Week 3 quiz topic *autocorrelation in operational data* |
| **Datasets** | `bandwidth_throughput_daily`, `noc_tickets_daily`, `bus_power_telemetry_hourly`, `transponder_utilisation_monthly`, `twta_thermal_daily` (**week-03 version**), `ka_band_availability_daily` (bonus) |
| **Files you need open** | animated slides, your **solution** notebook, the rule book PDF |

## The day before: checklist

<ul class="check">
<li>Run the <b>solution</b> notebook top to bottom: 13 of 13 ✅ (about 30 seconds).</li>
<li>Re-read Part C below: the TWTA numbers do NOT match the original code-book text, so be ready to say why.</li>
<li>Share the exercise link and rule book PDF in the class group.</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Warm-up** | Quiz Q1–6 from Day 1's topic as a quick show of hands (optional) | — |
| 0:05 | **Hook** | Third Mainland Bridge: tomorrow (lag 1) vs next Monday (lag 7) | 1–4 |
| 0:15 | **Part 1: Memory** | Lag = shifted copy; autocorrelation scale; 8 weeks of throughput; the four numbers | 5–9 |
| 0:30 | **Part 2: Correlogram** | Bars per lag, lag 0, three shapes, finding periods, baseline teaser, random-split warning | 10–15 |
| 0:45 | **Part 3: Not cause** | Suya vs generators; TWTA honest numbers; rain → uplink power | 16–19 |
| 0:55 | **Hands-on** | Part A (20 min), Part B (25 min), Part C (15 min) | 20 |
| 1:50 | **Wrap-up** | Recap; volunteer: "what does a spike at lag 24 on hourly data mean?" | 21 |

## Explain it like this (in plain English)

- **Lag:** slide a copy of the column down by k rows. Now every row holds "today" and "k steps ago" side by side.
- **Autocorrelation:** the ordinary correlation between those two columns. Near +1 = today looks like k steps ago. Near 0 = no memory.
- **Why lag 7 beats lag 1 for throughput:** weekends dip. Friday → Saturday is a big jump (so lag 1 is only 0.58), but this Saturday looks almost exactly like last Saturday (lag 7 = 0.99).
- **Correlogram:** all the lags at once. The gap between spikes is the period. That's how you *confirm* the `period=7/12/24` values from the decomposition day instead of copying them.
- **Slow decay = trend:** if a series keeps rising, every value is close to the previous ones, so all lags stay high and fade slowly.
- **Random split leakage:** with this much memory, a random test day has near-identical twins in training. The score looks great and means nothing.
- **Spurious correlation:** two series that both trend will correlate even if unrelated. `.diff()` compares changes, which removes the shared trend.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | "You already reason about memory every morning in traffic." | "Tomorrow or next Monday: which is the safer guess?" |
| 6 | Press next to slide the copy in. Point at the NaN. | "Why does day 1 have no yesterday?" |
| 7 | Real values: lag 1 = **0.58**, lag 7 = **0.99**, lag 30 = **0.09**. | — |
| 9 | Mama/church joke. Lag 30 is a different weekday, so no memory. | "Why is lag 14 as high as lag 7?" |
| 11 | Lag 0 is always 1: ignore it. Spikes every 7. | "What's the period?" |
| 12 | Quiz Q2 and Q3 live here. | "Spikes, slow fade or flat: which one is a trend?" |
| 14 | Same-weekday-last-week error **0.062** vs same-as-yesterday **0.338** Gbps (about 5×). | — |
| 15 | WAEC expo. Quiz Q5. | "Why would a random split look too good?" |
| 17 | Made-up example, stated clearly. 0.97 → 0.06. | "Does suya sell generators?" |
| 18 | Be honest: 0.59 → 0.40. It drops, it doesn't collapse. | "What part is real physics?" |
| 19 | Rain → power control → uplink power up. r = 0.97. | "Can we make it rain by turning up the power?" 😄 |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A2 | `s.shift(1)` | `s.shift(-1)` (that's tomorrow: future data!) |
| A3 | `s.autocorr(lag=1)` → **0.58** | Calling it on `bw` (the DataFrame) → pick the column |
| A4 | `s.autocorr(lag=7)` → **0.99** | — |
| B2 | `7` | Answering 1 because lag 1 is the first bar |
| B3 | `1` | — |
| B4 | `7` (lag 7 = 0.72 vs lag 1 = 0.40) | — |
| B5 | `24` (lag 24 = 1.00; lag 12 ≈ −0.03) | Answering 1 (days) → the data is hourly |
| B6 | `"trend"` (0.90, 0.81, 0.73… fading) | "season" → no repeating spikes |
| B7 | `(s - s.shift(7)).abs().mean()` → **0.062** Gbps | Forgetting `.abs()` → errors cancel out |
| C2 | `suya.corr(gens)` → **0.97** | — |
| C3 | `suya.diff().corr(gens.diff())` → **0.06** | `.diff()` on only one series |
| C4 | **0.59** and **0.40** | — |
| 🌶️ | `int(acf_vals[300:].argmax()) + 300` → **365** | Answering 65 (forgot to add 300) |

## Quiz link

Original Week 3 quiz (`Time-series/MCQ/week-03-mcq.csv`), topic **"autocorrelation in operational data"**, questions 25–30 (rows 26–31 of the CSV): lag-1 definition (slide 7), spikes at 7/14/21 (slide 11), slow decay = trend (slide 12), lag 0 = 1 (slide 11), random splits (slide 15), two trending series (slides 17–18).

> ⚠️ **Heads-up on quiz Q6** ("…after differencing the correlation largely collapses. What explains the raw correlation?" → *mostly shared trend*): on the real TWTA file the drop is 0.59 → 0.40, which is not a collapse. The concept is still right, and the suya example shows a true collapse. If someone challenges it, praise them: they checked the data.

## Troubleshooting

| Problem | Fix |
|---|---|
| `plot_acf` errors about NaN / missing data | Add `.dropna()` |
| Correlogram looks squashed | They used `lags=400` in B1. Use 35 for daily data |
| Numbers differ slightly between `.autocorr()` and the correlogram | Normal: `plot_acf` uses a slightly different formula (lag 7: 0.98 vs 0.99). Both are fine |
| `NameError: make_sales` | STEP 0 not run since a restart |

## Notes on the original material

- The original Week 3 code book says throughput's lag-1 autocorrelation is "around 0.83". **The real file gives 0.58.** Lag 7 (0.99) is correct, so the main point (weekly memory) stands.
- The original says the TWTA correlation "collapses" after differencing. **It drops from 0.59 to 0.40.** We teach the honest version.
- The original has no correlogram code. `plot_acf` and the period-finding exercise are new here.
- Facts are in `toolkit/nigcomsat-fact-sheet.md`.
