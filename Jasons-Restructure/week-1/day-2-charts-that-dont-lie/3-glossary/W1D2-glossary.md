# W1D2 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 📡 Link words

### 🌧️ Rain fade
- **Plain English:** Heavy rain soaks up the satellite signal, so quality drops or the link goes down.
- **Naija analogy:** DStv showing “No Signal” in the middle of a Lagos downpour, right before the penalty kick.
- **Example:** All 12 August outage hours came during heavy storms.

### ⛽ Link margin (dB)
- **Plain English:** How much signal is left above the minimum the receiver needs. Below 0 dB the link is down.
- **Naija analogy:** Fuel above the reserve line. Positive: you can still drive. Zero: you're pushing the car. 🚗
- **Example:** `link_margin_db` in `rf_link_quality_hourly`.

### 🔊 Uplink power
- **Plain English:** How strongly the ground station transmits up to the satellite. It's turned up automatically when rain weakens the signal.
- **Naija analogy:** Shouting louder when the generator next door starts. You shout *because* of the noise.
- **Example:** Uplink power averages about 41 dBm when dry and about 44 dBm in rain.

### 📉 dB (decibel)
- **Plain English:** A unit for signal strength on a “times” scale: +3 dB is about double, −3 dB about half.
- **Naija analogy:** Like Richter scale for earthquakes: small number changes mean big real changes.
- **Example:** The worst hour in August hit −4.3 dB of margin.

### 📜 SLA (Service Level Agreement)
- **Plain English:** The promise to a customer, e.g. “the link will be up 99.5% of the time”.
- **Naija analogy:** The landlord's promise of “24 hours light and water” in the house advert. 😅
- **Example:** “Did we breach the SLA?” is answered with daily **minimums**, not averages.

## 📊 Summary words

### 〰️ Daily average (mean)
- **Plain English:** Add up all the readings in a day and divide by how many. Shows the typical level.
- **Naija analogy:** “On average, NEPA gave us 20 hours today”, which hides that the 4 missing hours were during the match.
- **Example:** `rf["link_margin_db"].resample("D").mean()`: never below 4.9 dB in August.

### 📉 Daily minimum
- **Plain English:** The single lowest reading of each day: the worst moment.
- **Naija analogy:** The one hour you sat on Third Mainland Bridge: that's the hour you remember.
- **Example:** `resample("D").min()` showed an outage on 11 of 31 days.

### 🔁 resample
- **Plain English:** Change the time step of a series (hourly → daily) and choose how to summarise each new step.
- **Naija analogy:** Turning a daily sales diary into a weekly report: you must decide to add, average or take the best day.
- **Example:** `.resample("D").min()`

### 🔗 Correlation
- **Plain English:** A number from −1 to +1 showing how much two series move together. It does **not** tell you which one causes the other.
- **Naija analogy:** Umbrella sales and traffic jams both rise when it rains. Umbrellas don't cause traffic.
- **Example:** Rain and uplink power: correlation 0.97.

### ↩️ Response (vs cause)
- **Plain English:** Something that changes *because of* something else.
- **Naija analogy:** You carry an umbrella because it's raining. The umbrella didn't bring the rain.
- **Example:** Uplink power is a response to rain.

## 🗺️ Comparing groups

### 📏 Long format
- **Plain English:** One row per group per time: many rows, few columns. How databases usually export.
- **Naija analogy:** A class register written as one line per student per day.
- **Example:** `vsat_uptime_by_region_weekly`: 312 rows = 52 weeks × 6 zones.

### ↔️ Wide format
- **Plain English:** One row per time, one column per group. What charts want.
- **Naija analogy:** The same register as a grid: students across the top, days down the side.
- **Example:** `wide` has 52 rows and 6 zone columns.

### 🔄 pivot
- **Plain English:** The pandas command that reshapes long → wide.
- **Naija analogy:** Rearranging wedding guests from one long queue into tables by family.
- **Example:** `vsat.pivot(index="week_start", columns="region", values="uptime_pct")`

### 🍝 Spaghetti chart
- **Plain English:** Too many lines on one chart. Nobody can follow any of them.
- **Naija analogy:** Ten danfo routes drawn on one map with the same blue pen.
- **Example:** Six zones on one axis: try finding South South.

### 🖼️ Small multiples
- **Plain English:** A grid of small, identical charts, one per group, sharing the same y-axis.
- **Naija analogy:** Passport photos of the whole family: same size, same background, so you can compare faces.
- **Example:** Six mini charts, one per geopolitical zone, `sharey=True`.

### 💯 Index to a baseline
- **Plain English:** Divide every value by a starting value and multiply by 100, so everything starts at 100 and you see *change*.
- **Naija analogy:** Comparing students by how much they improved since last term, not by raw score.
- **Example:** `wide / wide.iloc[0] * 100`: South East fell furthest from its own start.

### 🗺️ Geopolitical zones
- **Plain English:** Nigeria's six regional groupings: North West, North East, North Central, South West, South East, South South.
- **Naija analogy:** The six “houses” at inter-house sports.
- **Example:** The `region` column in the VSAT file.

## ✅ Honest-chart words

### 🚧 Threshold line
- **Plain English:** A line drawn at the level that matters (0 dB, the SLA target), so readers instantly see breaches.
- **Naija analogy:** The red line on a fuel gauge.
- **Example:** `plt.axhline(0, color="red", ls="--")`

### 📏 Y-axis range
- **Plain English:** Where the vertical axis starts and ends. Counts should start at 0; percentages that live near the top may zoom in, if you say so on the chart.
- **Naija analogy:** A “before and after” photo zoomed onto the waist: fair if you say it's zoomed. 😄
- **Example:** Availability on 96–100%; tickets per weekday from 0.

### ☝🏾 Dual axis (avoid it)
- **Plain English:** Two different y-axes on one chart, one on each side. It lets you make any two lines look related.
- **Naija analogy:** Two referees on one pitch with different rule books.
- **Example:** Rain and uplink power go in two stacked charts instead.

### 📰 Finding title
- **Plain English:** A chart title that states what the chart shows, ideally with a number.
- **Naija analogy:** A newspaper headline: “Eagles win 2–0”, not “Football match”.
- **Example:** “Ka-band link went down on 11 of 31 August days”.

### 🗣️ 4-sentence finding
- **Plain English:** Situation → Observation → Implication → Recommendation. A whole report in four sentences.
- **Naija analogy:** How a good mechanic talks: “Your car is old (S). The brake pads are finished (O). You could crash (I). Change them today (R).”
- **Example:** The last slide of today's deck. The recommendation always comes last.
