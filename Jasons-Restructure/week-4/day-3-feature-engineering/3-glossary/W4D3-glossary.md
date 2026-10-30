# W4D3 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 👁️ Features

### 🧱 Feature
- **Plain English:** One column of the table you give a model. It can be a raw sensor reading or something you compute from the readings.
- **Naija analogy:** The questions a gateman asks before he opens the gate: who are you, who sent you, did you come yesterday? Each question is a feature.
- **Example:** `battery_soc_pct` is a raw feature; `temp_per_drive` is one we built.

### 🛠️ Feature engineering
- **Plain English:** Building new columns so the model can see what an engineer already knows: history, operating state, and how sensors relate.
- **Naija analogy:** Teaching a new apprentice mechanic *what to listen for*. The engine noise was always there; now he knows which knock matters.
- **Example:** Dividing amplifier temperature by RF drive turned four invisible weeks of EV04 into 605 flagged hours.

### ⏰ "The model cannot tell time"
- **Plain English:** A model like the isolation forest judges each row on its own. It doesn't know what happened an hour ago unless a column tells it.
- **Naija analogy:** A goldfish at the gate: every visitor is a stranger, even the one who came five minutes ago.
- **Example:** At 14:00 the forest sees 93% SoC, but not that it was 100% at midnight. `soc.shift(1)` gives it that memory.

### 🕰️ History feature (lag, difference, rolling statistic)
- **Plain English:** A column that carries the past onto the current row: the value an hour ago (`shift(1)`), the change since last hour (`diff(1)`), the average of the last day (`rolling(24).mean()`).
- **Naija analogy:** The landlord's receipt book: today's payment makes sense only next to last month's.
- **Example:** The code book's builder makes 6 history columns (plus the raw value) for each of 4 sensors.

### ➖ First difference (`diff`)
- **Plain English:** This hour's value minus the previous hour's: how much it just changed.
- **Naija analogy:** Not "how much fuel is in the tank?" but "how much did it drop since morning?"
- **Example:** `soc.diff(1)` jumps to about −7 at 01:00 on 2 May, when EV02 begins.

### 🕑 The 14:00 test (look-ahead leak)
- **Plain English:** Ask of every feature: *could I compute this at 14:00 using only what I knew at 14:00?* A feature that uses the future is a **leak**: it looks brilliant in testing and is impossible in the control room.
- **Naija analogy:** Reading tomorrow's newspaper to "predict" today's football results.
- **Example:** `soc.shift(-1)` and `rolling(24, center=True)` both "knew" about EV02 at midnight, an hour before it started. They cheat.

### 🕳️ Rows lost to the window
- **Plain English:** A 24-hour window or a 24-hour lag has nothing to work with during the first day, so those rows are empty (NaN) and get dropped.
- **Naija analogy:** You can't give a weekly average on Monday morning.
- **Example:** The 32-column builder turns 8,760 rows into 8,736.

## 🔗 Relationships

### 🔗 Relationship feature (cross-channel feature)
- **Plain English:** One column built from two or more sensors that normally move together, so the model sees when they stop agreeing.
- **Naija analogy:** NEPA has brought light but the inverter is still at 93%. Light alone is fine; 93% alone is fine (it happens every night). Together, in daylight, the charger is faulty.
- **Example:** `temp_per_drive`, and the steady-sun state for state of charge.

### 🌡️ temp_per_drive
- **Plain English:** Amplifier (TWTA) temperature divided by RF drive level: degrees per percent of drive. How hot it runs **for the work it's doing**.
- **Naija analogy:** A generator running hot while powering one bulb. The load didn't change, so something is blocking the cooling.
- **Example:** Normally 0.821 ± 0.013; during EV04 it averages 0.870, about 3.9σ high, while raw temperature never crosses its ceiling.

### 💔 Correlation break
- **Plain English:** Two sensors that normally move together stop doing so, even though each value is inside its own normal range.
- **Naija analogy:** Husband and wife who always arrive at church together. One day only one comes, smiling. Nothing is wrong with either face; something is wrong.
- **Example:** EV02 and EV05: sunlight is normal, yet the battery stops charging.

### 🌡️ Thermal decoupling
- **Plain English:** A component's temperature stops following the thing that normally drives it (here, RF drive).
- **Naija analogy:** Your phone getting hot while it's doing nothing.
- **Example:** EV04, cooling path degradation: the amplifier runs about 3 °C hot for its drive level for four weeks.

### 🪤 The big-sigma trap
- **Plain English:** A feature can put a fault very far out (many σ) and still be useless, because it is also wrong on normal months it never saw.
- **Naija analogy:** A gateman who catches every thief because he stops **everybody** after October.
- **Example:** The code book's regression feature puts EV04 at 28.9σ but flags all 2,208 hours of October to December.

### 🧭 Unseen months
- **Plain English:** Data the model or feature was not fitted on. The honest place to check whether it still behaves.
- **Naija analogy:** A new driver who has only driven in the dry season. Wait until he meets the July rain on Third Mainland Bridge.
- **Example:** Fitted on January to May, the residual drifts from June and breaks completely from October.

## ✂️ Fewer, better features

### 🧺 Kitchen-sink feature set
- **Plain English:** Throwing every column you can think of at the model and hoping it sorts them out.
- **Naija analogy:** Adding every spice in the market to one pot of stew. More is not tastier.
- **Example:** The code book's 32 columns caught 3 of 5 events and missed the two easiest; our 5 caught all 5.

### 👯 Twin (redundant) features
- **Plain English:** Two columns that carry the same information (correlation above about 0.98). In a forest, which picks columns at random, a twin doubles that sensor's vote.
- **Naija analogy:** The same person voting twice with two voter's cards.
- **Example:** `soc_gap` is exactly `100 − battery_soc_pct` (correlation 1.000). The builder has 18 such pairs.

### 🎯 Lean features
- **Plain English:** A small set of columns, each answering a question an engineer would ask.
- **Naija analogy:** A good doctor asks five sharp questions, not fifty random ones.
- **Example:** `lean_features()`: array current, bus voltage, state of charge, battery temperature, temp_per_drive.

### 🧑🏾‍🔧 Right reason
- **Plain English:** A flag is only useful if the feature that triggered it matches the real cause. Check with z-scores.
- **Naija analogy:** A student who gets the right answer by copying hasn't learnt anything. Show your working.
- **Example:** Every EV04 hour the forest flagged was flagged by `temp_per_drive`, exactly as the physics says.

## 🏁 Final project

### 🛠️ Method drafted (Checkpoint 3)
- **Plain English:** The first working version of your project's method, running end to end on your data, with your features, reference period and baseline written down.
- **Naija analogy:** The first coat of paint. Not the finish, but you can see the house.
- **Example:** A detection brief brings a statistical baseline plus a multivariate detector on trailing features.
