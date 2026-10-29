# W2D1 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🔧 Taking a series apart

### 🔧 Decomposition
- **Plain English:** Splitting one time series into separate parts: trend, seasonal and residual.
- **Naija analogy:** Tasting the jollof and naming each ingredient: rice, tomato base, and that one pepper that surprised you.
- **Example:** `seasonal_decompose(kam["availability_pct"], period=12)`

### 🧩 Component
- **Plain English:** One of the parts a decomposition produces.
- **Naija analogy:** One instrument in a highlife band. The song is all of them playing together.
- **Example:** `parts.trend`, `parts.seasonal`, `parts.resid`

### 📈 Trend component
- **Plain English:** The slow, long-term direction once the seasonal ups and downs are averaged away.
- **Naija analogy:** Lagos traffic getting worse year after year as the city grows, whatever the day of the week.
- **Example:** Ka-band availability trend rising slowly from about 99.24% to 99.40%.

### 🔁 Seasonal component
- **Plain English:** The pattern that repeats exactly every period: the same 12 numbers every year, or the same 7 numbers every week.
- **Naija analogy:** Rush hour at 7am every weekday, like clockwork.
- **Example:** August is about 1.1 points below the yearly average every year.

### 🎲 Residual
- **Plain English:** What's left after the trend and season are removed. Mostly noise, but big residuals are surprises worth investigating.
- **Naija analogy:** After you've explained the traffic by "it's Monday" and "it's raining", whatever delay is left is the keke that broke down.
- **Example:** In August, the biggest residual points straight at an injected solar-array dropout.

### 🥁 Period
- **Plain English:** How many rows until the seasonal pattern repeats. It comes from the process, not from a default.
- **Naija analogy:** How often your esusu (contribution) group meets: weekly means 7 days, monthly means 12 times a year.
- **Example:** 24 for hourly bus power, 7 for daily tickets, 12 for monthly availability.

## ➕✖️ Add or multiply?

### ➕ Additive model
- **Plain English:** observed = trend + seasonal + residual. The seasonal swing stays the same size even when the level rises.
- **Naija analogy:** December transport fare goes up by a fixed ₦100 every year, whatever the normal fare is.
- **Example:** `seasonal_decompose(series, model="additive", period=12)`

### ✖️ Multiplicative model
- **Plain English:** observed = trend × seasonal × residual. The seasonal swing grows as the level grows.
- **Naija analogy:** December fare goes up 20%. When fares are higher, 20% is more naira.
- **Example:** The `multiplicative` column in `additive_multiplicative_demo`: swing grows from about 0.29 to 0.54.

### 🪄 Logarithm (log)
- **Plain English:** A maths function that turns multiplying into adding. `np.log()` in Python.
- **Naija analogy:** A translator who turns "times" talk into "plus" talk so everybody understands.
- **Example:** `np.log(demo["multiplicative"])`: the swing stops growing.

## 🧰 Tools and rules

### 📦 statsmodels
- **Plain English:** A Python library for statistics and time-series models. Already installed in Colab.
- **Naija analogy:** The big toolbox in the mechanic's shop. pandas is the spanner; statsmodels has the special tools.
- **Example:** `from statsmodels.tsa.seasonal import seasonal_decompose`

### 🔧 seasonal_decompose
- **Plain English:** The classic decomposition function. Simple and fast, but it assumes the season looks the same every cycle.
- **Naija analogy:** A tailor who uses one measurement for you every year, even if you've added weight. 😅
- **Example:** `parts = seasonal_decompose(series, model="additive", period=7)`

### 🧠 STL
- **Plain English:** A smarter decomposition (Seasonal-Trend decomposition using LOESS) that lets the season change slowly over time.
- **Naija analogy:** A tailor who measures you again before every new outfit.
- **Example:** `STL(series, period=24, robust=True).fit()`

### 🛡️ Robust
- **Plain English:** A method that doesn't let a few extreme values pull the result around.
- **Naija analogy:** One bad experience at one buka shouldn't make you blacklist every buka in Lagos.
- **Example:** With one fake disaster August, robust STL keeps August's seasonal effect near −1.2 instead of −3.0.

### 〰️ Moving average (centred)
- **Plain English:** The average of a window of values around each point. Classic decomposition uses one to find the trend, so the trend is missing for half a window at each end.
- **Naija analogy:** Judging a student by the average of the tests around each week. You can't do it for the first and last weeks.
- **Example:** The Ka-band trend is empty for the first and last 6 months.

### 3️⃣ Three-cycle rule
- **Plain English:** Have at least three full cycles of data before you trust a seasonal pattern.
- **Naija analogy:** One friend says the new buka is sweet: gist. Three different friends: pattern.
- **Example:** 36 monthly rows = exactly 3 rainy seasons: the minimum.

## 🛰️ Satellite words

### 🌘 Eclipse season
- **Plain English:** The weeks around each equinox (March and September) when the Earth's shadow crosses the satellite's orbit for up to 72 minutes a day.
- **Naija analogy:** NEPA's scheduled load-shedding season, but for the satellite. It switches to battery.
- **Example:** Eclipse hours sit at 21:00 UTC from 1 September to 16 October in the bus-power file.

### 🔋 End-of-discharge voltage
- **Plain English:** The battery's voltage at the end of an eclipse, when it has worked hardest. Lower means a deeper discharge or an older battery.
- **Naija analogy:** How much power is left in your inverter battery just before NEPA brings light back.
- **Example:** `eod_voltage_v` dips in March and September and slowly drifts down over the years.

### 🌞 Solar-array current
- **Plain English:** The electric current coming from the satellite's solar panels. About 27.8 A in full sunlight.
- **Naija analogy:** The output of your rooftop solar panel on a sunny afternoon.
- **Example:** A sudden drop to about 16 A with no eclipse is a fault: a "string dropout".
