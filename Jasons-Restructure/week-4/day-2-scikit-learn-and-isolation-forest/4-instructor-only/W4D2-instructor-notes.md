# W4D2 Instructor Notes: Meet scikit-learn + Isolation Forest

> **The one idea for today:** *a model finds what is **rare**; your job is to make sure rare means **broken**.* Give it context, check *why* it flagged each hour, and keep the old control chart in the fight.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours |
| **Participants leave able to** | build X, fit and use an isolation forest (`fit`, `predict`, `decision_function`), sanity-check the flag count, spot a lucky catch with `event_table`, restrict a model to steady sunlight, compare it fairly with a control chart, find operating modes with k-means (and say why it needs scaling), explain a flag with z-scores |
| **Covers (original)** | Week 5 Code Book: *Setup*, *Confirming the couplings*, *The detector*, *Explaining a flag*; Week 5 quiz topics *the scikit-learn workflow* (Q1–Q7) and *isolation forest and clustering* (Q8–Q15) |
| **Datasets** | `week-05/data/bus_telemetry_multivariate_hourly.csv` (8,760 hours, Jan–Dec 2025), `anomaly_labels_week5.csv` (5 events) |
| **Files you need open** | animated slides, your **solution** notebook, this page |

## The day before: checklist

<ul class="check">
<li>Run the <b>solution</b> notebook top to bottom: 15 of 15 ✅ (about a minute; the forests take a few seconds each).</li>
<li>Read the "Explain it like this" section below twice. This is the first machine-learning day: the vocabulary is new for everyone, including you.</li>
<li>Try the beach-party question on a friend: "How many yes/no questions to find the man in agbada? And a guest in shorts?"</li>
<li>Decide whether you will show the honest data note on slide 16 (bus voltage gives EV02 and EV05 away). It is true and useful, but it can derail a beginner room. Suggestion: keep it for the people who finish early.</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | Beach party: agbada man vs guest in shorts; the lifeguard twist | 1–4 |
| 0:10 | **scikit-learn in 3 verbs** | What ML adds; X; fit / predict / decision_function; the count check | 5–9 |
| 0:22 | **What did it find?** | 58 flags, all at 21:00; the lucky catch | 10–12 |
| 0:30 | **Context** | Steady sun; forest 4/5 with 16 false alarms; the chart 4/5 with 3 | 13–16 |
| 0:37 | **Clustering + explaining** | k-means finds eclipse and recharge; scaling; z-scores; the EV04 cliffhanger | 17–21 |
| 0:40 | **Hands-on** | Parts A–D (60 min). Walk the room. | 22 |
| 1:40 | **Wrap-up** | Pepper task results, recap, tease feature engineering | 23 |

If time is tight, skip Part D's unscaled k-means cell and the pepper task; they are not needed for W4D3.

## Explain it like this (in plain English)

- **Machine learning** means the computer learns the pattern from examples instead of you writing the rule. Today's model never sees the answer key: it is **unsupervised**. It only learns what is *common* in January–August, then points at what is *uncommon*.
- **scikit-learn** is the toolbox. Every model in it works the same way: **build X → make the model → `fit` → `predict`**. X is a table: one row per hour, one column per channel. Learn this once and the next 10 models are free.
- **Isolation forest:** draw a random cut through the data, keep the side your point is on, cut again, until the point is alone. Count the cuts. An odd point is alone after one or two cuts; a normal point in the middle of the crowd takes many. Do it with 200 random trees and average. **Few cuts = odd.** The beach slide shows the real procedure: 1 cut for the agbada man, 9 for a guest.
- **`decision_function`** is the score behind it: **lower = more odd**. **`predict`** just compares the score with a line: **-1 = odd**, 1 = normal.
- **`contamination`** sets that line: "flag the oddest 0.5% of the training hours." So you can predict the count before you look: 0.005 × 8,760 ≈ 44. We got 58 for the whole year (30 of them in the 5,832 training hours). If someone gets thousands, they flagged the normal hours (`== 1` instead of `== -1`).
- **`random_state`** fixes the randomness so everyone gets the same trees. Without it, results change every run.
- **Rare is not broken.** The rarest thing in this file is eclipse: 92 hours a year of zero array current and a sagging bus. The first forest flags *only* eclipse hours. It found the lifeguard.
- **Lucky catch.** The scorer says the first forest caught EV04. But EV04 is an *amplifier* fault lasting four weeks, and it overlaps the September eclipse season. The 21 flags inside it are all 21:00 eclipse hours. Right answer, wrong reason. `event_table` shows how many hours of each event lit up and how late: always look at it for long events.
- **Context** is the Week 3 Day 1 lesson again: eclipse (21:00) and the 3 recharge hours after it are normal states with their own normal. We fit and judge only **steady sunlight**: `rolling(4).max() == 0`, "no eclipse in this hour or the 3 before."
- **The old chart still wins some fights.** On the same steady hours, a 3σ chart per channel catches EV03 (a single 12 A drop in array current) which the forest misses. For single-channel spikes the chart is the right tool (quiz Q15).
- **Clustering** groups hours that look alike, without labels. k-means with 4 groups puts all 92 eclipse hours in one group and all 276 recharge hours in another: it rediscovers the operating modes (quiz Q13).
- **Scaling** matters for k-means because it measures *distance*: a column with big numbers would dominate. It does **not** matter for the forest, which only cuts between each column's min and max. **Pipeline** = scaler and model glued together, so the scaler fitted on training rows is the one used later (quiz Q5).
- **Explaining a flag:** compute each channel's z-score (distance from steady training normal in standard deviations). The biggest one is the sentence you give the duty engineer (quiz Q14).

## The numbers (all computed from the data)

| Detector (fit on Jan–Aug, scored on the whole year) | Caught | False alarms | EV04 hours lit | Notes |
|---|---|---|---|---|
| Forest, 6 raw channels, all hours | 1/5 (EV04) | 37 | 21 of 672, first 189 h late | all 58 flags at 21:00 = eclipse; a lucky catch |
| Forest, 6 raw channels, steady sun only | 4/5 (EV01, EV02, EV04, EV05) | 16 | 1 of 672 (28 Sep 15:00), 615 h late | misses EV03; all 16 false alarms between 1 and 9 January |
| 3σ chart per health channel, steady sun only | 4/5 (EV01, EV02, EV03, EV05) | 3 | 0 | misses EV04 |
| 🌶️ Forest, steady sun, contamination 0.002 | 2/5 (EV02, EV05) | 1 | 0 | the forest's surest finds |

Supporting numbers:
- Training months: 5,832 hours (1 Jan – 31 Aug); 5,645 of them steady sun. Steady sun all year: 8,389 hours; eclipse 92; recharge 276; plus the first 3 hours of the file (the 4-hour window isn't full yet).
- The ten "oddest" hours of the raw forest: all 21:00, mostly 13–23 March plus 18 September.
- Why the January false alarms? z-scores average **−3.0σ** on RF drive and **−2.2σ** on amplifier temperature: the lightest load and coolest amplifier in the training months. The start of the year is the edge of what the forest learned. Nothing is broken.
- Why does the forest miss EV03 (array current −34σ, battery +27.5σ)? It ranks 224th. Each tree is grown on a small random sample (256 hours). In most samples there is no dropout, so no cut ever falls between 16 A and normal; the dropout ends up in the same leaf as the lowest normal hours. A forest is not a guarantee for one obvious spike; a chart is.
- The seed matters: with `random_state` 0 or 1 the steady forest loses its one EV04 hour; with 7 it also catches EV03. Same false-alarm count (15–17) every time.
- k-means (scaled): clusters = cool start of the year (Jan–Mar steady hours), the rest of the steady hours, eclipse (92/92), recharge (276/276 **plus 3 steady hours**). Those 3 are 19 Feb 11:00 (EV01), 30 Jun 00:00 (EV03) and 1 Sep 00:00: warm-battery hours. Unscaled: recharge is smeared over three clusters (164 / 95 / 17).
- Forest scores with and without `StandardScaler` correlate at r = 0.99999999.
- EV02's first hour (2 May 01:00): state of charge −20.7σ, bus voltage −6.8σ, array current −2.3σ. EV01: array −33.8σ, battery +24.8σ.
- EV04: amplifier peak 67.0 °C against a 3σ ceiling of 68.0 °C (steady training hours), but its daily mean jumped 2.8 °C on 3 September with no rise in drive.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | "Each red line is one random question. The odd one is alone after one." | "How many questions to find the agbada man? And the guest?" |
| 4 | "The lifeguard is rare too. He belongs there." | "What's the satellite's lifeguard?" (eclipse) |
| 5 | "Week 3 judged one channel at a time. This judges the whole row." | — |
| 8 | Point at the three verbs. "Every model in scikit-learn: same three." | "Which number means odd: -1 or 1?" |
| 9 | "Predict the count before you look." | "We asked for 0.5%. How many flags should we get?" |
| 11 | Pause on the chart: every red dot is on the floor (0 A). | "What happens at 21:00?" |
| 12 | "The scorer says caught. Look at the column: all 21:00." | "Did it see the amplifier?" (no) |
| 14 | NEPA takes light → the inverter charges hard → normal day. | — |
| 15 | "Big improvement. Now read the cards." | "Why would it miss a 12 A drop?" |
| 16 | "New is not automatically better." | Quiz Q15: True or False? |
| 18 | "Nobody told it about eclipse." | "Why did recharge get smeared without scaling?" |
| 20 | Read the gold numbers as sentences. | "What would you tell the duty engineer about the January hour?" |
| 21 | "It can only judge the columns we give it." | "What column would show 'hot for its workload'?" (W4D3) |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `X = bus[CHANNELS]` → (8760, 6) | `bus["CHANNELS"]` with quotes (a KeyError): CHANNELS is a variable |
| A2 | `TRAIN_END = "2025-09-01"` → 5,832 hours | `"2025-08-31"` (loses the last day of August); a number without quotes |
| A3 | `CONTAMINATION = 0.005` | `0.5` or `5`: contamination is a fraction (0.5% = 0.005) |
| A4 | `CONTAMINATION * len(X)` = 43.8 | — |
| A5 | `ODD = -1` → 58 flags | `1` gives 8,702 flags: "thousands = a bug" (quiz Q7) |
| B1 | `21` | — |
| B2 | `my_flags = flags_all` → caught 1, 37 false alarms | — |
| B3 | `False` | "But the scorer says caught!" → show the hours: all 21:00 |
| C1 | `4` | `3` (forgot the current hour) |
| C2 | `FIT_ROWS = train & steady` → caught 4, 16 false alarms | `steady` alone (that fits on September–December too: it has seen the future) |
| C3 | `K = 3` → caught 4, 3 false alarms | — |
| C4 | `"chart"` | — |
| D1 | `SCALER = StandardScaler()` | Forgetting the brackets `()`; leaving the scaler out |
| D2 | `"battery_soc_pct"` | Picking the most *positive* number: it's the biggest **distance from zero** |
| 🌶️ | `0.002` (anything that leaves ≤ 3 false alarms and ≥ 2 catches) → EV02 + EV05, 1 false alarm | Going so low that nothing is caught |

The forest checks allow ±5 false alarms, because Colab's scikit-learn version may differ slightly from ours. Catches must match exactly.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: sklearn` | Not on Colab? `pip install scikit-learn`. On Colab it is pre-installed |
| Thousands of flags | `predict() == 1` instead of `== -1` |
| Someone's forest result differs by a few false alarms | Check `random_state=42` and `n_estimators=200`; then the scikit-learn version (printed in the loading cell). Small differences are fine |
| `InvalidParameterError` on contamination | It must be a fraction between 0 and 0.5 |
| k-means check fails | No scaler, or `StandardScaler` without `()` |
| `KeyError: '2025-05-02 01:00'` in D2 | They re-ran a cell that changed `bus`. Runtime → Restart session and run all |
| Fast finishers | 🌶️ dial; then "set random_state to 7 in C2: what changes?" (EV03 gets caught; EV04 still only 1 hour) |

## Honest notes on the original material

- **The headline result doesn't reproduce** (review row 3). The code book promises the forest catches all five events. A forest on the raw channels flags only eclipse hours; its "ten most anomalous hours" are all 21:00 (review row 12k). Today teaches that honestly and fixes it step by step over three days.
- **The lucky catch** is a property of the labels plus event-level scoring: EV04's window is 672 hours long and covers part of the eclipse season, so anything that flags eclipse hours "catches" it. Teach participants to read `event_table`.
- **Scaling and the forest** (review row 12i). The code book says the different channel ranges are "why topic 1 insists on scaling". For an isolation forest scaling changes nothing (r = 0.99999999). It matters for distance methods (k-means). Quiz Q4's intended answer is about distance methods; its option "it does not matter for isolation forest" is also true.
- **"Not detectable with one channel"** (review row 12g). The label file marks EV02 and EV05 as univariately invisible. That's only true for array current, the one channel the code book checks. In steady sun, bus voltage sits at 50.40 ± 0.04 V; during EV02 and EV05 it reads 50.12–50.24 V, far outside, and the chart in C3 catches both with no help from the forest. Only EV04 truly needs two channels. Quiz Q8 ("Two") follows the label file; W5D1 discusses it.
- **The dates.** The code book checks EV02 on 1 May and its event table says 1 May and 29 June. The labels and the data put EV02 on **2 May** and EV03 on **30 June** (review row 2). Our notebook uses the label file.
- **The original code** uses `.asfreq("H")`, which crashes on pandas 3. Ours uses `"h"`.
