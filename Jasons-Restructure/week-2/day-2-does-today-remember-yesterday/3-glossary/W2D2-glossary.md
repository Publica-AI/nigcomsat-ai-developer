# W2D2 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🧠 Memory words

### 🪞 Lag
- **Plain English:** How many steps back you look. Lag 1 = one step ago, lag 7 = seven steps ago.
- **Naija analogy:** "Last week this time" when people gist about what happened last week at this same hour.
- **Example:** On daily data, lag 7 = the same weekday last week. On hourly data, lag 24 = the same hour yesterday.

### ⏪ .shift()
- **Plain English:** The pandas command that makes a lagged copy by sliding every value down.
- **Naija analogy:** Everyone in the queue moving one seat back so a latecomer can sit in front.
- **Example:** `s.shift(1)` puts yesterday's value on today's row.

### 🧠 Autocorrelation
- **Plain English:** How much a series looks like its own shifted copy. One number from −1 to +1.
- **Naija analogy:** How much your Monday looks like last Monday. Same traffic, same stress, same suya spot.
- **Example:** Throughput: lag 1 = 0.58, lag 7 = 0.99.

### 1️⃣ Lag-1 autocorrelation
- **Plain English:** How much today matches yesterday.
- **Naija analogy:** If it rained heavily today, there's a good chance it rains tomorrow too in July.
- **Example:** `s.autocorr(lag=1)` gives 0.58 for throughput.

### 🧩 Persistence (memory)
- **Plain English:** A series "has memory" when its past values help you guess its next values.
- **Naija analogy:** A neighbour who has been borrowing sugar every week will likely knock again next week. 😅
- **Example:** Throughput has strong weekly memory; random noise has none.

## 📊 Correlogram words

### 📊 Correlogram (ACF plot)
- **Plain English:** A bar chart with one bar per lag, showing the autocorrelation at each.
- **Naija analogy:** A report card for memory: one score for yesterday, one for last week, one for last month.
- **Example:** `plot_acf(s.dropna(), lags=35)`.

### 0️⃣ Lag 0
- **Plain English:** The first bar of every correlogram. Always exactly 1, because a series matches itself perfectly.
- **Naija analogy:** Asking "do you look like yourself?" Of course you do. Ignore that question.
- **Example:** The grey bar at the far left of every correlogram today.

### 📈 Spike
- **Plain English:** A bar much taller than its neighbours, sticking above the shaded band.
- **Naija analogy:** The one day in the month when everyone rushes to the bank: salary day.
- **Example:** Throughput spikes at lags 7, 14, 21, 28, 35.

### 🔁 Period
- **Plain English:** The length of one full season, from one repeat to the next. In a correlogram, it's the gap between spikes.
- **Naija analogy:** How long until your landlord's next visit. For rent, the period is one year. 😬
- **Example:** Period 7 (throughput), 24 (hourly battery charge), about 365 (Ka-band rainy season).

### 🟦 Confidence band
- **Plain English:** The shaded area in a correlogram. Bars inside it could easily be chance.
- **Naija analogy:** The "e no too matter" zone: small differences you shouldn't argue about.
- **Example:** For 730 days of data the band is about ±0.07.

### 🐢 Slow decay
- **Plain English:** Bars that start high and fade gently, lag after lag. It's the fingerprint of a trend.
- **Naija analogy:** Lagos rent: this year looks like last year, which looked like the year before… all going one way.
- **Example:** Transponder utilisation: 0.90, 0.81, 0.73, 0.64…

### 📐 plot_acf / statsmodels
- **Plain English:** `statsmodels` is a Python library for statistics; `plot_acf` is its correlogram function. Colab already has it.
- **Naija analogy:** A specialist mechanic: pandas is the general workshop, statsmodels is the one who knows engines.
- **Example:** `from statsmodels.graphics.tsaplots import plot_acf`

## 🎁 Forecast words (sneak peek)

### 👵🏾 Baseline forecast
- **Plain English:** The simplest possible forecast. Any clever model must beat it, or it's not worth using.
- **Naija analogy:** Grandma's weather forecast: "tomorrow will be like today." Hard to beat!
- **Example:** "Same as yesterday" and "same weekday last week".

### 🗓️ Seasonal naive ("same weekday last week")
- **Plain English:** Forecast each day with the value from one period ago.
- **Naija analogy:** Expecting this Friday's traffic to be like last Friday's traffic.
- **Example:** For throughput its average error is 0.062 Gbps, about 5× better than "same as yesterday" (0.338).

### 📏 MAE (mean absolute error)
- **Plain English:** The average size of a forecast's mistakes, ignoring whether they were too high or too low.
- **Naija analogy:** How many minutes late your friend usually is, on average. 😅
- **Example:** `(s - s.shift(7)).abs().mean()`

### 🚫 Random-split leakage
- **Plain English:** If you split time data randomly, the test set's near-copies sit in the training set, so the answers leak.
- **Naija analogy:** WAEC expo: if you saw the questions before the exam, your score is fake.
- **Example:** Day 8 in test, days 1 and 15 (same weekday, r = 0.99) in training.

## 🕵🏾 Correlation words

### 🔗 Correlation (r)
- **Plain English:** How closely two different series move together, from −1 to +1.
- **Naija analogy:** How often Mama Ngozi and Mama Bisi show up at the same parties.
- **Example:** `a.corr(b)`

### 🎭 Spurious correlation
- **Plain English:** A strong correlation between two things that are NOT really linked.
- **Naija analogy:** Suya sales and generator sales both rise toward December. Suya doesn't sell generators. 😄
- **Example:** Made-up suya vs generators: r = 0.97.

### 📈 Shared trend
- **Plain English:** Two series both rising (or falling) over time for their own reasons, which makes them look linked.
- **Naija analogy:** Your salary and the price of garri both rose over 5 years. One didn't cause the other.
- **Example:** Amplifier temperature and RF drive both drift up over two years.

### ➖ Differencing (.diff())
- **Plain English:** Replacing each value with the change since the previous step. It removes the trend.
- **Naija analogy:** Instead of asking "how much money do you have?", asking "how much did you gain or lose this week?"
- **Example:** Suya vs generators: 0.97 on levels, 0.06 on changes.

### 🧭 Correlation ≠ cause
- **Plain English:** Moving together doesn't prove one causes the other. Even when there IS a cause, check which direction it runs.
- **Naija analogy:** Umbrella sales and rain go together. Selling umbrellas doesn't bring rain.
- **Example:** Rain and uplink power: r = 0.97, because rain makes the station turn up its power, not the other way round.

## 🛰️ Satellite words

### 📶 Throughput (Gbps)
- **Plain English:** How much data a link carries, in gigabits per second.
- **Naija analogy:** How many cars pass through the toll gate per minute.
- **Example:** Over two years, about 3.9 Gbps on an average weekday and 3.0 at weekends.

### 🌡️ TWTA and RF drive
- **Plain English:** The TWTA (travelling-wave tube amplifier) boosts the signal before it's sent down. RF drive is how hard it's being pushed.
- **Naija analogy:** A generator: the harder you load it, the hotter it runs.
- **Example:** `twta_thermal_daily.csv`: temperature vs drive, r = 0.59 on levels, 0.40 on changes.

### 🎚️ Uplink power control
- **Plain English:** The ground station automatically raises its transmit power when rain weakens the signal.
- **Naija analogy:** Talking louder on the phone when the network starts breaking.
- **Example:** `uplink_power_dbm` rises in heavy rain: a response, not a cause.
