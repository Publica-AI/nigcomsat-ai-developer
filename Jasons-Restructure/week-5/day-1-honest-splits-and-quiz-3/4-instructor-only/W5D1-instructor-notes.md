# W5D1 Instructor Notes: No Expo! Honest Train/Test Splits + Quiz 3

> **The one idea for today:** *a score only counts if the model never saw the test, and two detectors can only be compared on the same months, the same hours and the same scorer, with settings fixed first.* When that fair fight is run on this data, the simple Week 4 chart on good features beats the isolation forest, and we say so.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours, including Quiz 3 (20 min + 10 min marking) |
| **Participants leave able to** | spot the three kinds of expo, split a time series by time with an embargo and an `assert`, run a fair comparison with one scorer, recognise a lucky catch, read a rolling-origin table, explain why the reference period must be clean, and recommend the simpler model without embarrassment |
| **Covers (original)** | Week 5 Code Book: *The temporal split*, *Scoring, and the comparison the deliverable asks for*, *The honest comparison*; Week 5 quiz topic *temporal train-test discipline* (all 8 questions); Quiz 3 = the whole Week 5 MCQ file |
| **Datasets** | `week-05/data/bus_telemetry_multivariate_hourly.csv`, `anomaly_labels_week5.csv` |
| **Files you need open** | animated slides, your **solution** notebook, `W5D1-quiz-3-answer-key.pdf` |

## The day before: checklist

<ul class="check">
<li>Run the <b>solution</b> notebook top to bottom: 14 of 14 ✅ (about a minute; Part D fits 8 small models).</li>
<li>Print <code>2-exercise/quiz/W5D1-quiz-3.pdf</code> (one per person), <b>or</b> import <code>W5D1-quiz-3-google-forms.csv</code> into Google Forms / your LMS.</li>
<li>Print or open <code>4-instructor-only/W5D1-quiz-3-answer-key.pdf</code>. Don't share it until marking.</li>
<li>Read the <b>Quiz 3</b> section below: three questions follow the original text where the data disagrees.</li>
<li>Re-read slides 14–18 until you can say the verdict in one breath: <i>"same catches, 1 false alarm instead of 25: the feature won, not the forest."</i></li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | Tunde's expo A1 vs Chika's honest B2; the three kinds of expo | 1–4 |
| 0:10 | **Catch the expo** | The copycat: 100% with a random split, 3.4% by time | 5–8 |
| 0:18 | **Split by time** | Train · embargo · test; the `assert`; the four rules of a fair fight | 9–12 |
| 0:25 | **The fair fight** | Lucky catch; the alarm barcode; report card; verdict; "can't we tune it?"; seeds; rolling origin; clean reference; when the forest earns its place | 13–22 |
| 0:40 | **Hands-on** | Parts A–D (45 min). Walk the room. | 24 |
| 1:25 | **Quiz 3** | 20 minutes, phones down, no AI | 23 |
| 1:45 | **Mark + wrap** | Swap and mark, discuss Q4, Q8 and Q18, recap, Checkpoint 4 reminder | 25 |

If time is tight, skip slides 19 and 21 (seeds, dirty reference): the notebook covers both in Part D.

## Explain it like this (in plain English)

- **Expo:** any way the test leaks into training or into your choices. The score then measures the leak, not the model.
- **Why random splits lie on time series:** neighbouring hours are near-twins. Shuffle them and every test hour has its twin in training. A model can "copy from the next seat" without understanding anything.
- **The copycat** (1-nearest-neighbour) is only a demonstration model. It's supervised (learns from the labels); our forest and chart never see labels. Use it to make expo visible, then put it away.
- **Split by time:** train on Jan–Aug, test on 2 Sep – 31 Dec. Tomorrow is always unseen, so the test must be unseen too.
- **Embargo:** leave out at least your longest feature window between train and test. W4D3's features look back 24 hours, so we skip 1 September.
- **Fair fight:** same months, same hours (steady sunlight), same scorer, settings fixed before the test. Without that, "the ML model is better" is an opinion.
- **Lucky catch:** the scorer says "caught", but look at *when* it fired. Contender 1 only touched EV04 at 22:00–00:00, the battery recharging after eclipse. The amplifier fault had nothing to do with it.
- **The verdict:** on identical features, the Week 4 chart catches both test events with 1 false alarm; the forest catches both with 25. The feature `temp_per_drive` did the work. Recommend the chart.
- **Rolling origin:** one cut is one number, possibly lucky. Four cuts give a spread. Training only grows forwards.
- **Clean reference:** if the fault sits inside the months you learn "normal" from, the model learns the fault as normal.

## The numbers (computed from the data, same scorer for all)

**The split:** train = every hour before 1 Sep (**5,832** hours, EV01–EV03 inside); embargo = 1 Sep (**24** hours); test = 2 Sep – 31 Dec (**2,904** hours, EV04 + EV05 inside). EV04 lasts **672** hours.

**The copycat (Part A):** random split (a third held out, `random_state=42`): **241 of 241** test fault hours found (100%). Split by time: **24 of 696** (3.4%), all of them EV05. EV05 is a recurrence of EV02's charge-controller fault, which the copycat saw in May. It never caught a single hour of EV04, a new kind of fault.

**The fair fight (test months only, steady-sun hours for contenders 2–4):**

| # | Detector | Caught | False alarms | EV04 hours lit | Precision |
|---|---|---|---|---|---|
| 1 | Week 4 chart, raw health channels, sunlit hours (as taught in W3D1/W4D1) | 2/2 | 50 | 84 / 672 🍀 | 0.04 |
| 2 | Week 4 chart, raw health channels, steady sun | 1/2 (EV05) | 1 | 0 / 672 | 0.50 |
| 3 | Isolation forest, lean features, steady sun (`contamination=0.005`, `random_state=42`) | 2/2 | 25 | 358 / 672 | 0.07 |
| 4 | **Week 4 chart, lean features, steady sun (`k = 3`)** | **2/2** | **1** | **502 / 672** | **0.67** |

- Contender 1's 84 EV04 hours are all at 22:00, 23:00 and 00:00 (28 each): recharge hours. Its 50 false alarms are also all recharge hours (2 in September, 48 in October, the autumn eclipse season).
- Contender 4's one false alarm is **18 Nov 21:00**, two hours after EV05 ends: state of charge 97.3% and still climbing back. It's the tail of a real fault.
- Lean features = solar-array current, bus voltage, state of charge, battery temperature, and `temp_per_drive` (W4D3).

**"Can't we tune the forest?" (slide 18):**

| Forest budget (`contamination`) | Past events (Jan–Aug) | Test caught | Test false alarms | EV04 hours lit |
|---|---|---|---|---|
| 0.50%, fixed in W4D2 | 3/3 (15 false alarms) | 2/2 | 25 | 358 |
| 0.35%, honest tune: the smallest budget that catches all 3 past events | 3/3 (6 false alarms) | 2/2 | 2 | 186 |
| 0.30%, expo tune: looks perfect on Sep–Dec | 2/3 (misses EV03) | 2/2 | 0 | 144 |
| Chart, `k = 3`, no tuning | 3/3 (1 false alarm) | 2/2 | 1 | 502 |

The chart isn't on a knife-edge either: any `k` from 2.5 to 5 gives 2/2 with 1 false alarm on the test (only `k = 2` jumps to 80).

**Seeds:** the forest's test false alarms with `random_state` 42, 0, 1, 7, 123 = **25, 25, 36, 20, 28**. The chart has no randomness: 1 every time.

**Rolling origin** (`TimeSeriesSplit(n_splits=4, gap=24)`, lean features, steady sun):

| Fold | Trains on | Tests on | Chart | Forest |
|---|---|---|---|---|
| 1 | 1 Jan – 13 Mar | 15 Mar – 26 May | 1/1, 1 false alarm | 1/1, 3 |
| 2 | 1 Jan – 25 May | 27 May – 7 Aug | 1/1, 23 | **0/1**, 50 |
| 3 | 1 Jan – 6 Aug | 8 Aug – 19 Oct | 1/1, 1 | 1/1, 63 |
| 4 | 1 Jan – 18 Oct | 20 Oct – 31 Dec | 1/1, 1 | 1/1, 0 |

Fold 2 is the chart's bad fold: trained on winter and spring only, it finds summer strange. Honest, and exactly why one cut is not enough.

**Clean vs dirty reference (EV04 hours lit, of 672):** clean (Jan–Aug): chart 502, forest 358. Dirty (whole year, EV04 inside): chart 150, forest **5**.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | "Tunde's A1 measured the expo, not Tunde." | "Who goes in the control room?" |
| 4 | Three flavours. Flavour 2 was W4D3's 14:00 test. | "Which one have you seen at work?" |
| 6 | The copycat copies the nearest hour's answer. Supervised, a side experiment only. | — |
| 7 | 100 vs 3.4. Same model, same features. | "What changed?" (only the split) |
| 8 | In a random split, EV04's hours land on both sides. | Quiz Q23 |
| 10 | Read the three code lines aloud. The `assert` fails loudly. | Quiz Q24 |
| 11 | The empty seat between candidates. 24 hours because W4D3 used 24-hour windows. | Quiz Q25 |
| 12 | Agree the four rules *before* the fight. Thumbs up from the room. | Quiz Q28 |
| 14 | The clock: every EV04 flag sits right after the 21:00 eclipse. | "Did the amplifier cause that?" |
| 15 | Read the barcode row by row: red = false alarm, green = inside an event. | "Which row would you want on your pager?" |
| 16 | Rows 3 and 4 differ only in the model. | — |
| 17 | "The feature won, not the forest." Say it proudly. | Quiz Q30 |
| 18 | Honest tuning uses the past only. The perfect-looking budget is expo flavour 3. | "How would you have found 0.30% without the test answers?" (you couldn't) |
| 20 | One cut is one possibly lucky number. Even the chart has a bad fold. | Quiz Q26, Q27 |
| 21 | Fit on a year that contains the fault, and the fault becomes "normal". | Quiz Q29 |
| 22 | Machine learning isn't useless: it's for when you can't write the relationships yourself. | — |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `pred[y_te == 1].mean()` = 1.0 (241 of 241) | `pred.mean()` (that's the share of ALL test hours called a fault) |
| A2 | `CUT = "2025-09-01"` → 0.034 (24 of 696) | Writing the date without quotes (SyntaxError) |
| A3 | `"EV05"` | `"EV04"`: look at the `caught` column |
| B1 | `TRAIN_END = "2025-09-01"`, `TEST_START = "2025-09-02"` → 5,832 and 2,904 hours, 24 embargoed | Swapping them (the `assert` catches it) |
| B2 | `24` | `1` (that's days, the question asks for hours) |
| C1 | `K = 3` → 2/2, 50 false alarms | — |
| C2 | `"lucky"` | `"real"`: point at the hour-of-day table (22, 23, 0 only) |
| C3 | `CONTEXT = steady` → 1/2, 1 false alarm | Typing `"steady"` in quotes (the cell says so) |
| C4 | `CONTAMINATION = 0.005` → 2/2, 25 false alarms | Typing `0.5` (that's 50%, the forest flags half the year) |
| C5 | `K = 3` → 2/2, 1 false alarm | — |
| C6 | `4` | `1` because "it caught everything": remind them of the 50 false alarms and the lucky catch |
| D1 | `GAP = 24` → chart false alarms 1, 23, 1, 1 | Any other gap gives slightly different blocks; the check expects 24 |
| D2 | `DIRTY_FIT = steady` → chart 150, forest 5 EV04 hours | Typing `train & steady` (that's the clean one) |
| 🌶️ | `HONEST_CONTAMINATION = 0.0035` → test 2/2, 2 false alarms | Picking 0.003 because it scores 0 on the test: that's expo, and it misses EV03 in the past |

The forest's numbers (C4, the pepper task) were identical on scikit-learn 1.6.1 and 1.9.1 and on pandas 2.2 and 3.1 in our tests. If Colab shows a slightly different false-alarm count, the C4 check accepts anything from 5 to 70 as long as both events are caught.

## Quiz 3

- **Files:** `2-exercise/quiz/W5D1-quiz-3.pdf` (printable, no answers), `W5D1-quiz-3-google-forms.csv` (import), `4-instructor-only/W5D1-quiz-3-answer-key.pdf`.
- **Source:** the original `Time-series/MCQ/week-05-mcq.csv`, unchanged wording. Options reshuffled with a fixed seed (5103) so the correct letters are spread: multiple choice A ×7, B ×6, C ×6, D ×7; True/False A ×3, B ×1. (In the original file, most answers were option B.)
- **Topic → day:** the scikit-learn workflow → W4D2 · isolation forest and clustering → W4D2 · feature engineering → W4D3 · temporal train-test discipline → today.
- **Three questions follow the original text where the data disagrees.** Mark them as below, then use them as a 3-minute discussion: "the answer key can be wrong too, so check it against the data."
  - **Q4** (scaling, official answer **A**: "Without scaling, channels with large ranges dominate distance-based methods"). Option **D**, "It does not matter for isolation forest", is **also true**: in W4D2 the forest's scores with and without `StandardScaler` correlated 0.99999999. Scaling matters for distance methods such as k-means and the copycat. **Accept A or D.**
  - **Q8** (how many events are single-channel detectable, official answer **C**, "Two", from the label file). On the data, a steady-sun chart on single channels catches **four**: EV02 and EV05 show plainly in bus voltage (50.12–50.24 V against a normal 50.40 ± 0.04 V; a sunlit bus-voltage chart catches both with 0 false alarms). Today's Contender 2 caught EV05 with raw single channels. Only **EV04** truly needs two channels. "Four" isn't an option, so **mark C as correct**, then tell the room.
  - **Q18** (EV04 modelled against drive, official answer **D**, "About 22 sigma"). Running the code book's own recipe gives **28.9σ**, and the same feature flags all 2,208 hours of Oct–Dec because five months can't separate the amplifier's yearly warming from the season (W4D3). "Far outside" is the idea. **Mark D as correct**; praise anyone who remembers W4D3's warning.
- Q30 ("recommending the simpler detector is legitimate", **True**) is today's verdict. If anyone got it wrong, re-show slide 17.

## Troubleshooting

| Problem | Fix |
|---|---|
| `NameError: chart_flags` / `X` / `steady` | They skipped the ▶️ "tools from Week 4" cells under STEP 0. Run them |
| `NameError: train` | They skipped B1. Part C needs the split |
| C3 or D2: "Use the variable itself, without quotes" | They typed `"steady"`. It's a variable: `steady` |
| C4 gives hundreds of false alarms | They typed `0.5` (50%). The budget is `0.005` |
| A forest number differs from the slides by a few | Library version or seed. The verdict doesn't change: see the seeds slide |
| Part D takes 10–30 seconds | Normal: it fits 10 small models. Let it run |
| `ParserError` loading the labels | Someone used `pd.read_csv` on the labels. Use `load_labels("anomaly_labels_week5")` |
| Fast finishers | 🌶️ honest tuning, then: "try `k = 2` and `k = 5` in C5" (k = 2: 80 false alarms; k = 2.5 to 5: still 1). Ask them why the chart is less touchy than the forest's budget |

## If someone asks…

- **"So machine learning is useless?"** No. It earns its place with hundreds of channels, relationships nobody has written down, and faults that nudge many channels a little at once. Here, six channels and one good feature written by an engineer were enough. The method (split by time, fixed settings, same scorer) is the same either way.
- **"Isn't `k = 3` tuned too?"** It's the textbook default from Week 3, chosen before anyone saw this file, and the result doesn't hang on it: anything from 2.5 to 5 gives the same 2/2 with 1 false alarm.
- **"Two test events is a tiny exam."** True, and worth saying. That's why we also look at the training months (chart 3/3 with 1 false alarm; forest 3/3 with 15) and at rolling origin (the chart catches the event in all four folds; the forest misses one and swings from 0 to 63 false alarms, beating the chart only in fold 4, by one). Every view points the same way.
- **"The copycat caught EV05. Isn't supervised learning good?"** It's good at **repeats** of faults it has seen (EV05 repeats EV02). It's blind to **new** kinds (EV04). Anomaly detection exists for the faults nobody has labelled yet.
- **"Contender 1 caught everything. Why not pick it?"** Ask when it fired. 84 EV04 hours, all recharge hours: a lucky catch, plus 50 false alarms. A detector you can't trust for the right reason will fail on the next fault.

## Notes on the original material

- The original's *honest comparison* scores the forest over the **whole year**, including the training months it was fitted on (review row 12k). Ours scores the held-out months only.
- The original's Week 4 baseline is a per-channel 3σ chart on **all hours** with no eclipse context (it caught 5/5 with 291 false alarms when run). Ours uses the chart exactly as W3D1/W4D1 taught it (sunlit hours) and the steady-sun version, so the baseline is the best of what participants already know.
- The original's forest (on its 32 features) catches 1 of 5 when run, through eclipse hours inside EV04's window (review bug 3). Our forest uses the lean features from W4D3.
- The original says "expect about 48 embargoed rows". Its code embargoes 47 (31 Aug 01:00 to 1 Sep 23:00). Ours embargoes exactly 1 Sep: 24 hours.
- The original says a random split "will report a better score" but never shows it. For the unsupervised forest there are no labels to copy, so we show it with the supervised copycat.
- Rolling-origin validation (quiz Q26, Q27) has no code in the original. Part D adds it.
- Quiz Q4, Q8 and Q18: see the Quiz 3 section above and review rows 12g, 12h, 12i, 16b.
