# W4D2 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🤖 Machine learning basics

### 🤖 Machine learning (ML)
- **Plain English:** Instead of writing the rule yourself ("alarm below 20 A"), you show the computer lots of examples and it works out the pattern.
- **Naija analogy:** Nobody gave the Lagos danfo conductor a rule book. He has watched ten thousand passengers, and he knows who will not pay before they climb in.
- **Example:** The isolation forest learns what a normal hour looks like from January–August, then judges the whole year.

### 🧰 scikit-learn (sklearn)
- **Plain English:** The free Python library of ready-made machine-learning models. Colab already has it.
- **Naija analogy:** Alaba market for models: whatever you need, someone has a stall, and every stall uses the same POS machine.
- **Example:** `from sklearn.ensemble import IsolationForest`

### 🧮 X (the feature matrix)
- **Plain English:** The table of numbers you feed a model. **Rows are the things you judge (hours), columns are what you know about each one (channels).**
- **Naija analogy:** The class register: one row per student, one column per subject score.
- **Example:** `X = bus[CHANNELS]`: 8,760 hours × 6 channels.

### 🏋🏾 fit
- **Plain English:** Training: the model studies the rows you give it and learns what is normal.
- **Naija analogy:** The new apprentice spends his first month just watching the master mechanic.
- **Example:** `model.fit(X[train])` learns from January–August only.

### 🔮 predict
- **Plain English:** Asking the trained model about rows. For an isolation forest: **-1 means odd**, 1 means looks normal.
- **Naija analogy:** After his month of watching, the apprentice says "this engine sound no correct".
- **Example:** `model.predict(X) == -1` gives the True/False flags.

### 📉 decision_function (anomaly score)
- **Plain English:** A number for every row saying how odd it is. **Lower = more odd.** `predict` is just this score compared with a line.
- **Naija analogy:** Instead of "pass/fail", the full exam mark. You can rank everyone by it.
- **Example:** `score.nsmallest(10)`: the ten oddest hours of the year.

### 🙈 Unsupervised
- **Plain English:** Learning without an answer key. The model never sees the labels; it only learns what is common.
- **Naija analogy:** Learning which neighbours are "normal" just by living on the street for a year, without anyone telling you who is a thief.
- **Example:** `fit()` gets X only. The labels are used afterwards, to **score** it.

### 🎲 random_state
- **Plain English:** A fixed starting number for the randomness, so the model gives the same answer every run.
- **Naija analogy:** Shuffling the Ludo dice the same way every time, so everyone gets the same game.
- **Example:** `random_state=42`. With 0 or 1 instead, the steady-sun forest loses its one EV04 hour.

## 🌲 The isolation forest

### 🌲 Isolation forest
- **Plain English:** A detector that draws random cuts through the data and counts how many cuts it takes to get each point alone. **Few cuts = odd.** 200 random trees vote.
- **Naija analogy:** Spot the man in agbada at a beach party: one question ("who is wearing agbada?") and he's alone. A guest in shorts takes many questions.
- **Example:** In our demo the agbada point was isolated in 1 cut; a guest in the crowd took 9.

### ✂️ Random cut
- **Plain English:** One split of the data along one column, at a random value between that column's smallest and largest value.
- **Naija analogy:** "Everyone taller than this, step left." Repeat with random questions until one person is alone.
- **Example:** One cut on array current at 10 A puts all 92 eclipse hours (at most 0.05 A) on one side and every other hour (at least 16 A) on the other.

### 🌳 n_estimators
- **Plain English:** How many random trees the forest grows. More trees = steadier scores, slower fit.
- **Naija analogy:** Asking 200 aunties instead of one. One aunty can be wrong; 200 rarely agree on nonsense.
- **Example:** `n_estimators=200`.

### 🎚️ Contamination
- **Plain English:** The share of training rows you **allow** the forest to flag. It sets the line on the score.
- **Naija analogy:** Telling the gateman "you can stop at most 5 cars in every 1,000 for searching".
- **Example:** `contamination=0.005` (0.5%) on ~8,760 hours ≈ 44 flags expected. We got 58: same ballpark.

### ✅ Sanity check (the count)
- **Plain English:** Before reading results, check the number of flags is roughly what you asked for. Thousands = a bug.
- **Naija analogy:** You sent ₦5,000 and the bank app says ₦500,000 left your account. Don't celebrate or panic: check.
- **Example:** Writing `predict() == 1` by mistake flags 8,702 hours: the normal ones.

## 🔍 Reading the results

### 🛟 Rare is not broken
- **Plain English:** A model finds what is unusual. Some unusual things are normal physics with a known cause.
- **Naija analogy:** The lifeguard in red shorts stands out at the beach every evening. He belongs there.
- **Example:** The raw forest's 58 flags were all 21:00 eclipse hours.

### 🍀 Lucky catch
- **Plain English:** The scorer says "caught", but the flag inside the event had nothing to do with the fault.
- **Naija analogy:** Guessing C in WAEC and getting it. The mark is real; the knowledge isn't.
- **Example:** EV04 (an amplifier fault) was "caught" by 21 eclipse-hour flags, all at 21:00.

### 🌞 Steady sun
- **Plain English:** Hours with no eclipse in this hour or the 3 before: not on battery, not recharging. The state we judge today.
- **Naija analogy:** Not "NEPA just took light" and not "NEPA just brought light and the inverter is charging": normal daytime.
- **Example:** `bus["eclipse_flag"].rolling(4).max() == 0`: 8,389 of 8,760 hours.

### 🔀 Multivariate
- **Plain English:** Looking at several channels together, so you can notice a **combination** that never happens, even if each channel looks fine alone.
- **Naija analogy:** NEPA light is on, the inverter is at 93%, and it's not charging. Each fact is normal; together they are wrong.
- **Example:** EV02: array current normal, state of charge stuck at 93% in full sun.

### 🔢 z-score (explaining a flag)
- **Plain English:** How many standard deviations a reading is from its normal. Per channel, it tells you **which** channel made the hour odd.
- **Naija analogy:** "Your blood pressure is fine, your sugar is fine, but your temperature is 40." The doctor points at the one number that's off.
- **Example:** EV02's first hour: state of charge −20.7σ. That's the sentence for the duty engineer.

## 🧩 Clustering

### 🧩 Clustering
- **Plain English:** Grouping rows that look alike, without being told the groups. Useful for finding operating **modes**.
- **Naija analogy:** At a wedding, without any seating plan, the groom's people, the bride's people and the gate-crashers still end up at different tables.
- **Example:** k-means put every eclipse hour (92 of 92) in one cluster and every recharge hour (276 of 276) in another.

### 📍 k-means
- **Plain English:** A clustering method: choose k centres, put each row with its nearest centre, move the centres, repeat.
- **Naija analogy:** Four bus stops in a new estate: people walk to the nearest one, then the stops are moved to where the crowds are.
- **Example:** `KMeans(4, n_init=10, random_state=42)`.

### 📏 Scaling (StandardScaler)
- **Plain English:** Turning every column into "standard deviations from its mean", so no column wins just because its numbers are big.
- **Naija analogy:** Comparing a ₦ price and a $ price without converting first: the naira one always looks bigger.
- **Example:** Without scaling, k-means smears the recharge hours over 3 clusters. The forest doesn't care either way.

### 🔗 Pipeline
- **Plain English:** Gluing the scaler and the model together, so the scaler fitted on the training rows is exactly the one used at prediction time.
- **Naija analogy:** The tailor keeps your measurements with your cloth. Nobody sews your agbada with someone else's tape-measure numbers.
- **Example:** `make_pipeline(StandardScaler(), KMeans(4, n_init=10, random_state=42))`.
