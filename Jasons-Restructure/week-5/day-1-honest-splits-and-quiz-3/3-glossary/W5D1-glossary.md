# W5D1 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🕵🏾 Expo: how a score gets faked

### 🕵🏾 Expo (data leakage)
- **Plain English:** When information from the test sneaks into training or into your choices, so the score looks better than the model really is. Data scientists call it **leakage**.
- **Naija analogy:** WAEC "expo": you saw the questions the night before, so your A1 measures the expo, not you.
- **Example:** The copycat found 100% of fault hours with a random split, and 3.4% when split by time.

### 🔑 Tuning on the answer key
- **Plain English:** Choosing a setting (a threshold, `k`, `contamination`) because it scores best on the **test** answers. The test stops being a test.
- **Naija analogy:** Adjusting your answers after the teacher reads out the marking scheme.
- **Example:** A forest budget of 0.30% gives 0 false alarms on Sep–Dec, but you'd only know that by peeking, and it misses EV03 in the past.

### 👥 Near-identical neighbours
- **Plain English:** In hourly data, 10:00 and 11:00 look almost the same. Shuffle the hours and every test hour has a near-twin in training.
- **Naija analogy:** Writing an exam beside your twin who has the same answers you studied together.
- **Example:** Quiz 3, Q23: why a random split on hourly telemetry scores too well.

## ✂️ Splitting the data

### ✂️ Train/test split
- **Plain English:** Dividing your data into a part the model learns from (**train**) and a part it is judged on (**test**), which it must never see while learning.
- **Naija analogy:** Past questions to practise on; the real exam to be marked on.
- **Example:** Train = January to August; test = 2 September to 31 December.

### 🎲 Random split
- **Plain English:** Picking the test rows at random, for example with `train_test_split`. Fine for unrelated rows, wrong for time series.
- **Naija analogy:** Mixing the exam questions into the practice pile and hoping nobody notices.
- **Example:** `train_test_split(X, y, test_size=0.33, random_state=42)` put hours of EV04 on both sides.

### ⏳ Split by time (temporal split)
- **Plain English:** Every training hour comes **before** every test hour. It's the only honest split for time series, because tomorrow is always unseen.
- **Naija analogy:** You study the past, then you face tomorrow's exam. You can't study tomorrow.
- **Example:** `train = bus.index < "2025-09-01"`, `test = bus.index >= "2025-09-02"`.

### 📝 Held-out period
- **Plain English:** The stretch of time kept aside for the test: no fitting, no tuning, no peeking until the very end.
- **Naija analogy:** The sealed envelope of exam papers that only opens in the exam hall.
- **Example:** 2 Sep – 31 Dec: 2,904 hours, with EV04 and EV05 inside.

### 🪑 Embargo
- **Plain English:** A gap left out between training and test, at least as long as your longest feature window, so no feature on the first test hour can reach back into training.
- **Naija analogy:** The empty seat between two candidates in the exam hall.
- **Example:** 1 September (24 hours) is in neither set, because W4D3's features use 24-hour windows.

### ✅ assert
- **Plain English:** A line that checks something is true and stops the notebook with an error if it isn't. A guard that fails loudly.
- **Naija analogy:** The gateman who refuses entry if your name isn't on the list. No argument.
- **Example:** `assert bus.index[train].max() < bus.index[test].min()` proves the split has no overlap.

### 🔁 Rolling origin (TimeSeriesSplit)
- **Plain English:** Testing several times: each fold trains on everything before a block and tests on that block. Training only ever grows **forwards**. You get a spread of scores, not one lucky number.
- **Naija analogy:** Judging a striker on a whole season, not on one match.
- **Example:** `TimeSeriesSplit(n_splits=4, gap=24)`: the chart's false alarms per fold were 1, 23, 1 and 1.

## 🐱 The copycat experiment

### 🎓 Supervised vs unsupervised
- **Plain English:** A **supervised** model learns from the answer key (labels). An **unsupervised** model only sees the readings and learns what "normal" looks like. The isolation forest and the control chart are unsupervised.
- **Naija analogy:** Supervised = learning with the marking scheme. Unsupervised = learning what a normal day at the market feels like, then noticing when something is off.
- **Example:** The copycat (supervised) needs labels; the forest never sees them.

### 🐱 Nearest neighbour ("the copycat")
- **Plain English:** A model that answers by finding the most similar example it has seen and copying its answer. With `n_neighbors=1` it copies just one.
- **Naija analogy:** The student who copies from whoever sits closest.
- **Example:** `KNeighborsClassifier(n_neighbors=1)` recognised EV05 because it had seen EV02, but was blind to EV04, a kind of fault it had never seen.

## 🥊 The fair fight

### 🥊 Fair comparison
- **Plain English:** Two detectors judged on the same held-out months, the same hours and the same scorer, with settings fixed before the test. Anything else is an opinion.
- **Naija analogy:** Two strikers, same match, same referee, same goalposts.
- **Example:** The forest and the chart, both on steady hours of Sep–Dec, both through `score_events`.

### 📏 Baseline
- **Plain English:** The simple method you must beat before a fancier one has earned its place.
- **Naija analogy:** "Can your new generator beat NEPA plus my small inverter?"
- **Example:** The Week 4 control chart is the baseline for the isolation forest.

### 🍀 Lucky catch
- **Plain English:** A detector "catches" an event, but the flags fired for a different reason. Right answer, wrong reason.
- **Naija analogy:** Guessing C on every question and getting one right.
- **Example:** The sunlit chart lit 84 EV04 hours, all at 22:00, 23:00 or 00:00: battery recharge after the eclipse, not the hot amplifier.

### 🧽 Reference period
- **Plain English:** The stretch of data a detector learns "normal" from. If a fault sits inside it, the fault becomes part of normal.
- **Naija analogy:** Judging "normal traffic" using the week Third Mainland Bridge was closed.
- **Example:** Fitted on the whole year, EV04 included, the forest lit only 5 of 672 EV04 hours.

### 🏆 Recommend the simpler model
- **Plain English:** If a simple method wins or ties a complex one on a fair test, you recommend the simple one: easier to explain, check and maintain.
- **Naija analogy:** If the keke gets you there as fast as the SUV, take the keke.
- **Example:** The 3-sigma chart on the lean features: both test events, 1 false alarm. The forest: both events, 25 false alarms.
