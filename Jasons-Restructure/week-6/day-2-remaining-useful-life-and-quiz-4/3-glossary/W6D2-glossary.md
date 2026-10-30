# W6D2 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## ⛽ Remaining useful life

### ⛽ Remaining useful life (RUL)
- **Plain English:** How long a part has left before its reading crosses an operational limit. Usually: (what's left above the limit) ÷ (how fast it's going).
- **Naija analogy:** The danfo driver: 20 litres left, 4 litres a trip, so 5 more trips before he's pushing the bus.
- **Example:** On 1 Jan 2024, the battery's line reaches 80% on 1 May 2025: a remaining useful life of 486 days.

### 📉 Degradation
- **Plain English:** The slow, one-way loss of performance as equipment ages: capacity, gain or fuel that won't come back.
- **Naija analogy:** Your phone battery: brand new it lasts two days, after three years it begs for the charger by afternoon.
- **Example:** Battery capacity fell from 99.86% to 77.84% over five years.

### 🚧 Operational limit (threshold)
- **Plain English:** The agreed value a reading must not cross, set by engineering, known up front. You forecast *when* it's reached, not what it is.
- **Naija analogy:** The red line on the fuel gauge: nobody forecasts where the red line is.
- **Example:** `degradation_thresholds.csv`: battery 80%, amplifier −2 dB, propellant 5 kg.

### 📏 Trend-to-threshold
- **Plain English:** Fit a trend to the past, extend it into the future, and read off the day it crosses the limit.
- **Naija analogy:** "At this rate, my landlord's rent will pass my salary by 2030."
- **Example:** A straight line through three years of battery data hits 80% on 1 May 2025.

### 🧮 np.polyfit (slope and intercept)
- **Plain English:** `np.polyfit(x, y, 1)` finds the best straight line through the points and returns two numbers: the **slope** (change per step) and the **intercept** (the value at step 0).
- **Naija analogy:** Slope = how much the price of a bag of rice goes up each month; intercept = what it cost when you started counting.
- **Example:** Battery slope −0.0126% per day, which is −4.59% a year; intercept 99.88%.

### 🔭 Extrapolation
- **Plain English:** Using a trend beyond the range of data it was fitted on. The further you reach, the less you should trust it.
- **Naija analogy:** "He scored in his first two matches, so he'll score 38 this season." Maybe. Maybe not.
- **Example:** The amplifier call reaches 9.3 years past the three years it was fitted on.

## 🐞 The bug and its fix

### 🐞 np.argmax on True/False
- **Plain English:** `np.argmax` returns the position of the largest value. On True/False it finds the **first True**. If there is **no** True, it quietly returns **0**.
- **Naija analogy:** Asking the gateman "who was the first visitor?" on a day nobody came, and he answers "the first name on the list" anyway.
- **Example:** The original code book printed 1 Jan 2021 (day 0) as the propellant's crossing date.

### 🔎 Search window
- **Plain English:** How far into the future the code looks for a crossing. If the trend crosses after the window ends, the honest answer is "no crossing inside the window".
- **Naija analogy:** Looking for your friend's car only on your own street: not finding it doesn't mean it doesn't exist.
- **Example:** The 4,000-day search ended on 13 Dec 2034; the propellant line reaches 5 kg on 6 Dec 2035.

### 🚫 None ("no crossing")
- **Plain English:** Python's way of saying "there is no answer". Our `day_of_threshold` returns `None` instead of a fake day 0.
- **Naija analogy:** "No light" is an answer. Pretending NEPA brought light at midnight is not.
- **Example:** `day, line = day_of_threshold(known["propellant_kg"], 5.0)` gives `day = None`.

### 🧾 Fuel-gauge sum (sanity check)
- **Plain English:** The no-model version of the answer: what's left above the limit ÷ what's used per year. If it disagrees with the model, look for a bug.
- **Naija analogy:** Counting the money in your pocket before trusting the bank app.
- **Example:** (101.93 − 5) kg ÷ 9.62 kg a year = 10.1 years: about January 2036. The line said December 2035.

## 🔍 Checking the call

### 🪟 Crossing window
- **Plain English:** For a noisy reading, "the day it crossed" isn't one day: readings bounce either side of the limit for a while. Report the window.
- **Naija analogy:** "When did harmattan start?" Some mornings are dusty in November, but you only stop arguing in December.
- **Example:** The battery's first daily dip below 80% was 14 May 2025; it was last at or above 80% on 24 Jul 2025. 49 of the 72 days in between were below.

### 💧 First dip
- **Plain English:** The first single reading below the limit. Early warning, but noise can trigger it.
- **Naija analogy:** The first raindrop of the season: real, but not yet the rainy season.
- **Example:** 14 May 2025. The 3-year call (1 May) is 13 days early against it.

### 📊 Rolling-mean crossing
- **Plain English:** The first day the average of the last N days (here 30) is below the limit. Slower, but noise can't fool it.
- **Naija analogy:** Judging a footballer by his last 30 matches, not his worst one.
- **Example:** 20 Jun 2025. The 3-year call is 50 days early against it.

### 🔁 Backtesting the method
- **Plain English:** Repeating the whole forecasting recipe as if you stood at several earlier dates, with only the data you had then, and checking each call against what happened.
- **Naija analogy:** Testing your football-prediction system on the last four seasons, not just last Saturday.
- **Example:** Battery calls made from 1, 2, 3 and 4 years of data: −74, −37, −13 and +4 days against the first dip.

### ⏳ Warning time (lead time)
- **Plain English:** How long you have to act between making the call and the crossing. More data gives a closer call but less time to act.
- **Naija analogy:** Knowing about the exam a month ahead versus the night before.
- **Example:** 1,229 days of warning with 1 year of data; only 134 with 4.

### 🐢 Decelerating fade
- **Plain English:** The loss rate itself gets smaller over time, so the trend is a gentle curve. A straight line fitted on early years then overstates the later fade and calls the crossing early.
- **Naija analogy:** A new car loses value fast in the first years, then more slowly.
- **Example:** Battery fade per year: −4.81, −4.69, −4.55, −4.45, −4.34%.

### 🌘 Eclipse season
- **Plain English:** The weeks around the equinoxes when a geostationary satellite passes through the Earth's shadow every night and runs on battery.
- **Naija analogy:** The NEPA-heavy months when your inverter works every single night.
- **Example:** 27 Feb – 13 Apr and 1 Sep – 16 Oct: 24.7% of the days, but 43.4% of the battery's fade.

### 🚀 Station-keeping burn
- **Plain English:** A short thruster firing that pushes a geostationary satellite back into its assigned box. Each burn uses a little propellant.
- **Naija analogy:** The danfo driver nudging back into his lane every few minutes on Third Mainland Bridge.
- **Example:** About one every 14 days, roughly 0.39 kg each, about 26 a year.

### 🧰 De-orbit reserve
- **Plain English:** Propellant kept back so that at end of life the satellite can be moved out of the busy geostationary ring. It's a limit, not spare fuel.
- **Naija analogy:** The transport fare you never spend at the party, so you can get home.
- **Example:** 5 kg, from `degradation_thresholds.csv`.

### ⏲️ Design life
- **Plain English:** How long the manufacturer built a satellite to operate. Real satellites can outlive it or fall short; remaining-useful-life analysis tells you which way it's going.
- **Naija analogy:** "This generator is rated for 10 years", but how you use it decides the real answer.
- **Example:** NigComSat-1R, launched December 2011, has a 15-year design life.

### 🎯 Planning figure
- **Plain English:** A forecast stated as a range, with how far it reaches and when it will be re-checked. Built for decisions, not for showing off precision.
- **Naija analogy:** "We'll travel for Christmas sometime in mid-December, I'll confirm by November."
- **Example:** "Amplifier: around 2033 (calls span March to November), more than 7 years past our data; we re-estimate every year."

### 〰️ Polynomial fit (degree 2)
- **Plain English:** A curve with one bend instead of a straight line: `np.polyfit(x, y, 2)`. It can follow a slowing fade, but it can go wild when stretched far into the future.
- **Naija analogy:** A road that bends with the hill. Great on this hill; don't assume it keeps bending the same way to Abuja.
- **Example:** On the same three years, a degree-2 curve calls the battery crossing on 14 Jun 2025, inside the real window.
