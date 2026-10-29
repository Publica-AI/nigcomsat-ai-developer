# Master Glossary

Every new word from every day, A to Z. The tag (e.g. `W1D1`) shows the day it was introduced. This file is rebuilt automatically from the daily glossaries.

### 0️⃣ Lag 0
- **Plain English:** The first bar of every correlogram. Always exactly 1, because a series matches itself perfectly.
- **Naija analogy:** Asking "do you look like yourself?" Of course you do. Ignore that question.
- **Example:** The grey bar at the far left of every correlogram today.

<span class="pill">W2D2</span>

### ✖️ 1.4826
- **Plain English:** The number that converts MAD into the same size as a standard deviation, so "3 robust σ" means what you expect.
- **Naija analogy:** The exchange rate between two currencies, so both prices mean the same thing.
- **Example:** `robust_sigma = MAD * 1.4826`

<span class="pill">W3D2</span>

### 1️⃣ Lag-1 autocorrelation
- **Plain English:** How much today matches yesterday.
- **Naija analogy:** If it rained heavily today, there's a good chance it rains tomorrow too in July.
- **Example:** `s.autocorr(lag=1)` gives 0.58 for throughput.

<span class="pill">W2D2</span>

### 3️⃣ 3-sigma rule
- **Plain English:** On normal data, only about 0.27% of readings fall outside ±3σ by chance.
- **Naija analogy:** Someone who is never more than 15 minutes late suddenly arriving 2 hours late: that's not chance, something happened.
- **Example:** About 8 chance alarms in 2,880 normal hours.

<span class="pill">W3D2</span>

### 🎯 3σ band (three-sigma)
- **Plain English:** Average ± 3 standard deviations. Readings outside it are rare if everything is normal.
- **Naija analogy:** "Normal fare is ₦500, give or take ₦100". ₦1,000 means something is up.
- **Example:** Sunlit 3σ band: 26.43 to 29.99 A. Only the 4 dropout hours fall outside.

<span class="pill">W3D1</span>

### 3️⃣ Three-cycle rule
- **Plain English:** Have at least three full cycles of data before you trust a seasonal pattern.
- **Naija analogy:** One friend says the new buka is sweet: gist. Three different friends: pattern.
- **Example:** 36 monthly rows = exactly 3 rainy seasons: the minimum.

<span class="pill">W2D1</span>

### 🗣️ 4-sentence finding
- **Plain English:** Situation → Observation → Implication → Recommendation. A whole report in four sentences.
- **Naija analogy:** How a good mechanic talks: “Your car is old (S). The brake pads are finished (O). You could crash (I). Change them today (R).”
- **Example:** The last slide of today's deck. The recommendation always comes last.

<span class="pill">W1D2</span>

### 🙅🏾 Accuracy (and why it lies)
- **Plain English:** The fraction of all readings a detector got "right". Useless when real events are rare.
- **Naija analogy:** Ade the guard sleeps all night and is "97% accurate", because most nights there's no thief.
- **Example:** A detector that never fires scores 99.87% on last week's 4,706 readings.

<span class="pill">W4D1</span>

### ➕ Additive model
- **Plain English:** observed = trend + seasonal + residual. The seasonal swing stays the same size even when the level rises.
- **Naija analogy:** December transport fare goes up by a fixed ₦100 every year, whatever the normal fare is.
- **Example:** `seasonal_decompose(series, model="additive", period=12)`

<span class="pill">W2D1</span>

### 🤖 AI button (Gemini)
- **Plain English:** Colab's built-in AI helper. Great for explaining code and errors.
- **Naija analogy:** A very smart friend who talks a lot. Never tell him company secrets.
- **Example:** OK to ask: “Explain this error.” Never paste real NIGCOMSAT telemetry.

<span class="pill">W1D1</span>

### 😴 Alarm fatigue
- **Plain English:** When there are so many false alarms that people stop paying attention, even to the real ones.
- **Naija analogy:** After the 10th "thief!" shout from the mai-guard, nobody comes out anymore.
- **Example:** A NOC that sees 46 useless solar-array alarms a season learns to ignore that channel.

<span class="pill">W3D1</span> <span class="pill">W4D1</span>

### 🔔 Alarm (limit check)
- **Plain English:** A rule that shouts when a reading crosses a fixed number.
- **Naija analogy:** The smoke detector in the kitchen: it doesn't know you're frying plantain, it just sees smoke.
- **Example:** `bus["solar_array_current_a"] < 20` fires an alarm.

<span class="pill">W3D1</span>

### 🚨 Alert line (threshold)
- **Plain English:** A value that, once crossed, means someone should act. Real ones are set by engineers.
- **Naija analogy:** The fuel light on your car's dashboard.
- **Example:** The lab's 97 Ah line is **made up for practice**.

<span class="pill">W2D3</span>

### 🎚️ Alpha
- **Plain English:** The setting for exponential smoothing. High alpha = follows the data closely and reacts fast. Low alpha = smooth and slow.
- **Naija analogy:** High alpha believes every WhatsApp broadcast immediately. Low alpha waits for three people to confirm.
- **Example:** alpha 0.5 hugs the daily line; alpha 0.05 is very calm.

<span class="pill">W1D3</span>

### 🚨 Anomaly
- **Plain English:** A reading that doesn't fit what normally happens.
- **Naija analogy:** Your quiet neighbour suddenly playing loud music at 3am. Something is off.
- **Example:** The solar-array current suddenly dropping to about half while the sun is shining.

<span class="pill">W3D1</span>

### 🔑 Answer key (labels / ground truth)
- **Plain English:** A list of the real events: what happened, where, and when. It turns "my detector seems fine" into a score.
- **Naija analogy:** The WAEC marking scheme. Without it, every student says "I passed".
- **Example:** `telemetry_anomaly_labels.csv`: 6 events, EV01 to EV06.

<span class="pill">W4D1</span>

### 📏 .asfreq()
- **Plain English:** Declares the rhythm of your data (e.g. daily) and creates an empty slot for any missing period.
- **Naija analogy:** A class register with every school day printed on it. An absent student shows as a blank, not a missing page.
- **Example:** `ka.asfreq("D")`. Missing days appear as `NaN`.

<span class="pill">W1D1</span>

### 🧠 Autocorrelation
- **Plain English:** How much a series looks like its own shifted copy. One number from −1 to +1.
- **Naija analogy:** How much your Monday looks like last Monday. Same traffic, same stress, same suya spot.
- **Example:** Throughput: lag 1 = 0.58, lag 7 = 0.99.

<span class="pill">W2D2</span>

### ✅ Availability
- **Plain English:** The percentage of time a link worked properly.
- **Naija analogy:** Out of 24 hours, how many did your network actually give you full bars?
- **Example:** 99.6% availability = about 6 minutes of bad service in a day.

<span class="pill">W1D1</span>

### 📏 Baseline
- **Plain English:** The simplest reasonable method, the one every fancier method must beat on the same test.
- **Naija analogy:** Grandma's weather forecast: “tomorrow will be like today”. Beat her or go home. 👵🏾
- **Example:** “Same weekday last week” as a forecast for throughput.

<span class="pill">W2D3</span>

### 👵🏾 Baseline forecast
- **Plain English:** The simplest possible forecast. Any clever model must beat it, or it's not worth using.
- **Naija analogy:** Grandma's weather forecast: "tomorrow will be like today." Hard to beat!
- **Example:** "Same as yesterday" and "same weekday last week".

<span class="pill">W2D2</span>

### 🎯 Brief
- **Plain English:** One of the five project types you can choose (A–E), each with its own operational question.
- **Naija analogy:** The topic the lecturer approves for your final-year project.
- **Example:** Brief B: “When will the battery be too tired to carry us through eclipse?”

<span class="pill">W2D3</span>

### 📶 C/N (carrier-to-noise ratio)
- **Plain English:** How strong the signal is compared to the background hiss, in dB. Higher is better.
- **Naija analogy:** How clearly you can hear your friend on the phone in a noisy bus park.
- **Example:** About 14.2 dB in clear sky; it falls in heavy rain.

<span class="pill">W3D1</span>

### 🥁 Cadence (frequency)
- **Plain English:** How often a reading is recorded: hourly, daily, weekly, monthly.
- **Naija analogy:** How often your landlord comes for rent: monthly? yearly? (Hopefully not weekly 😅)
- **Example:** `bus_power_telemetry` is hourly; `ka_band_availability` is daily.

<span class="pill">W1D1</span>

### 🔋 Capacity (amp-hours, Ah)
- **Plain English:** How much charge a battery can still hold. It shrinks as the battery ages.
- **Naija analogy:** Your old phone that used to last all day and now dies before lunch.
- **Example:** `est_capacity_ah` falls from 103.3 Ah to 96.6 Ah over three years.

<span class="pill">W2D3</span>

### ✅ Catch (true positive)
- **Plain English:** A real event the detector flagged.
- **Naija analogy:** The mai-guard shouts and there really is a thief at the gate.
- **Example:** The sunlit control chart catches all 3 solar-array dropouts.

<span class="pill">W4D1</span>

### 🧱 Cell (code cell / text cell)
- **Plain English:** One block in a notebook. A **code cell** runs Python; a **text cell** is just for reading.
- **Naija analogy:** One stop on a danfo route. You can't jump to Oshodi without passing the stops before it.
- **Example:** `print("Hello")` lives in a code cell. These instructions live in text cells.

<span class="pill">W1D1</span>

### ➖ Centre line
- **Plain English:** The middle line of a control chart: the average of the quiet reference period.
- **Naija analogy:** The "normal" fare for your usual bus route.
- **Example:** 27.87 A for 1–15 August.

<span class="pill">W3D2</span>

### 🔮 Centred window
- **Plain English:** A window with today in the middle: half the days are in the past, half in the **future**.
- **Naija analogy:** Marking a WAEC script after you've seen the answer sheet. Looks perfect, but it's cheating if you use it live.
- **Example:** `s.rolling(30, center=True).mean()` is empty for the last 15 days.

<span class="pill">W1D3</span>

### 📍 Change point
- **Plain English:** The moment a series switches to a new behaviour: a new level or a new speed.
- **Naija analogy:** The day the fuel price changed at the pump. Before and after are two different worlds.
- **Example:** 12 May 2025 for the amplifier; 1 April 2025 for the battery.

<span class="pill">W3D3</span>

### 🚩 Checkpoint
- **Plain English:** A short progress check at a fixed point in the course.
- **Naija analogy:** Police checkpoints on the expressway, but these ones help you. 😄
- **Example:** Week 3 · Day 3: bring your unit head's reply and your profiled data.

<span class="pill">W2D3</span>

### 🧼 Clean residual
- **Plain English:** A residual you can trust: mean near zero, no autocorrelation left, and the same spread all year.
- **Naija analogy:** A clean bill of health from the doctor before you start the race.
- **Example:** After removing the 2 spike days, lag-1 autocorrelation fell from 0.33 to 0.06.

<span class="pill">W3D2</span>

### 🌊 Common-cause variation
- **Plain English:** The everyday, built-in wobble of a stable process. Nothing to fix.
- **Naija analogy:** Lagos traffic being a bit slower on Tuesday than Monday.
- **Example:** Array current wobbling between 27.8 and 28.0 A.

<span class="pill">W3D2</span>

### 🧩 Component
- **Plain English:** One of the parts a decomposition produces.
- **Naija analogy:** One instrument in a highlife band. The song is all of them playing together.
- **Example:** `parts.trend`, `parts.seasonal`, `parts.resid`

<span class="pill">W2D1</span>

### 🌞 Conditioning on a known cause
- **Plain English:** Only judging readings where a known, normal cause is absent, instead of widening the alarm band for everyone.
- **Naija analogy:** You don't call an electrician when the lights go off during a scheduled NEPA load-shedding.
- **Example:** Adding `eclipse_flag == 0` took the control chart from 46 false alarms to 0.

<span class="pill">W4D1</span>

### 🟦 Confidence band
- **Plain English:** The shaded area in a correlogram. Bars inside it could easily be chance.
- **Naija analogy:** The "e no too matter" zone: small differences you shouldn't argue about.
- **Example:** For 730 days of data the band is about ±0.07.

<span class="pill">W2D2</span>

### 🎭 Context (state-based limits)
- **Plain English:** Checking which mode the system is in before deciding whether a reading is strange.
- **Naija analogy:** A dark house at midnight is normal. A dark house at noon with the gen running is not.
- **Example:** `floor_alarm & (bus["eclipse_flag"] == 0)` only checks the limit in sunlight.

<span class="pill">W3D1</span>

### 📏 Control chart
- **Plain English:** A chart with a centre line and two limits that shows when a reading leaves its normal range.
- **Naija analogy:** Mama Put's price sense: she knows the usual range for a basket of tomatoes, so one crazy price jumps out.
- **Example:** Solar-array current with a band from 27.65 A to 28.09 A.

<span class="pill">W3D2</span>

### ↕️ Control limits (UCL / LCL)
- **Plain English:** The upper and lower edges of "normal": centre ± 3σ. Outside them = unusual.
- **Naija analogy:** The fare range where you don't argue. Above it, you ask the conductor, "Ehn?!"
- **Example:** LCL 27.65 A, UCL 28.09 A.

<span class="pill">W3D2</span>

### 🔗 Correlation
- **Plain English:** A number from −1 to +1 showing how much two series move together. It does **not** tell you which one causes the other.
- **Naija analogy:** Umbrella sales and traffic jams both rise when it rains. Umbrellas don't cause traffic.
- **Example:** Rain and uplink power: correlation 0.97.

<span class="pill">W1D2</span>

### 🧭 Correlation ≠ cause
- **Plain English:** Moving together doesn't prove one causes the other. Even when there IS a cause, check which direction it runs.
- **Naija analogy:** Umbrella sales and rain go together. Selling umbrellas doesn't bring rain.
- **Example:** Rain and uplink power: r = 0.97, because rain makes the station turn up its power, not the other way round.

<span class="pill">W2D2</span>

### 🔗 Correlation (r)
- **Plain English:** How closely two different series move together, from −1 to +1.
- **Naija analogy:** How often Mama Ngozi and Mama Bisi show up at the same parties.
- **Example:** `a.corr(b)`

<span class="pill">W2D2</span>

### 📊 Correlogram (ACF plot)
- **Plain English:** A bar chart with one bar per lag, showing the autocorrelation at each.
- **Naija analogy:** A report card for memory: one score for yesterday, one for last week, one for last month.
- **Example:** `plot_acf(s.dropna(), lags=35)`.

<span class="pill">W2D2</span>

### 📄 CSV file
- **Plain English:** A plain-text table where commas separate the columns.
- **Naija analogy:** A list written in a jotter with commas instead of lines.
- **Example:** `date,tickets_raised` / `2024-01-01,8`

<span class="pill">W1D1</span>

### 🧾 CUSUM (cumulative sum)
- **Plain English:** A detector that keeps a running total of small leftovers and alarms when the total gets too big.
- **Naija analogy:** Your landlord's “small-small” rent increases. No single year shocks you, but add up the receipts and you've paid ₦415k extra.
- **Example:** `S = max(0, S + leftover - k)` caught the amplifier's step on 12 May 2025.

<span class="pill">W3D3</span>

### 🎢 Cycle
- **Plain English:** Ups and downs that repeat, but **with no fixed length**.
- **Naija analogy:** Business boom years and slow years. Nobody can tell you the exact date of the next boom.
- **Example:** Demand strong for 2 years, weak for 3, then rising again.

<span class="pill">W1D1</span>

### 〰️ Daily average (mean)
- **Plain English:** Add up all the readings in a day and divide by how many. Shows the typical level.
- **Naija analogy:** “On average, NEPA gave us 20 hours today”, which hides that the 4 missing hours were during the match.
- **Example:** `rf["link_margin_db"].resample("D").mean()`: never below 4.9 dB in August.

<span class="pill">W1D2</span>

### 📉 Daily minimum
- **Plain English:** The single lowest reading of each day: the worst moment.
- **Naija analogy:** The one hour you sat on Third Mainland Bridge: that's the hour you remember.
- **Example:** `resample("D").min()` showed an outage on 11 of 31 days.

<span class="pill">W1D2</span>

### 📋 DataFrame
- **Plain English:** pandas' name for a table: rows and named columns.
- **Naija analogy:** The class register: one row per student, one column per day.
- **Example:** `ka` is a DataFrame with 1,096 rows.

<span class="pill">W1D1</span>

### 📉 dB (decibel)
- **Plain English:** A unit for signal strength on a “times” scale: +3 dB is about double, −3 dB about half.
- **Naija analogy:** Like Richter scale for earthquakes: small number changes mean big real changes.
- **Example:** The worst hour in August hit −4.3 dB of margin.

<span class="pill">W1D2</span>

### 🚨 Decision limit (h)
- **Plain English:** How big the running total must get before CUSUM raises the alarm.
- **Naija analogy:** How many times your neighbour's generator must wake you before you go and knock.
- **Example:** `h = 5 × σ` = 1.02 °C. Lower h = faster but noisier.

<span class="pill">W3D3</span>

### 🔧 Decomposition
- **Plain English:** Splitting one time series into separate parts: trend, seasonal and residual.
- **Naija analogy:** Tasting the jollof and naming each ingredient: rice, tomato base, and that one pepper that surprised you.
- **Example:** `seasonal_decompose(kam["availability_pct"], period=12)`

<span class="pill">W2D1</span>

### 🪫 Depth of discharge
- **Plain English:** How far the battery was drained, as a percentage of what it holds.
- **Naija analogy:** How low your inverter battery went during last night's blackout.
- **Example:** Under 1% on normal days, up to about 22% on the deepest eclipse days.

<span class="pill">W2D3</span>

### ⏳ Detection delay
- **Plain English:** How many days pass between the onset and the alarm.
- **Naija analogy:** The time between “I don pay” and the bank alert landing.
- **Example:** 3 days for the practice fault with h = 5σ; 6 days with h = 10σ.

<span class="pill">W3D3</span> <span class="pill">W4D1</span>

### 🧪 Detector (model)
- **Plain English:** Any rule or method that decides "normal" or "not normal". Even a fixed limit is a simple one.
- **Naija analogy:** A gateman deciding who looks suspicious. Some gatemen are better than others.
- **Example:** The 20 A floor is a detector. So is mean − 3σ.

<span class="pill">W3D1</span>

### ➖ Differencing (.diff())
- **Plain English:** Replacing each value with the change since the previous step. It removes the trend.
- **Naija analogy:** Instead of asking "how much money do you have?", asking "how much did you gain or lose this week?"
- **Example:** Suya vs generators: 0.97 on levels, 0.06 on changes.

<span class="pill">W2D2</span>

### 🐢 Drift
- **Plain English:** A slow, steady slide. No single day looks strange.
- **Naija analogy:** Your eyesight getting a little worse every year until one day you can't read the danfo number.
- **Example:** Battery capacity fading from 103 to 95.4 Ah over three years.

<span class="pill">W3D1</span>

### ☝🏾 Dual axis (avoid it)
- **Plain English:** Two different y-axes on one chart, one on each side. It lets you make any two lines look related.
- **Naija analogy:** Two referees on one pitch with different rule books.
- **Example:** Rain and uplink power go in two stacked charts instead.

<span class="pill">W1D2</span>

### 👯 Duplicate timestamp
- **Plain English:** The same time appearing twice: usually an export mistake.
- **Naija analogy:** Being charged twice on one POS transaction.
- **Example:** Two rows both saying `2024-03-06`.

<span class="pill">W1D1</span>

### 🧑🏾‍🔧 Duty engineer / page
- **Plain English:** The engineer on shift who gets alerted (paged) when an alarm fires, and must check it.
- **Naija analogy:** The one who gets the 2 a.m. "Oga, come and see" phone call.
- **Example:** Every false alarm is one page to the duty engineer.

<span class="pill">W4D1</span>

### 🌘 Eclipse
- **Plain English:** The hour when the Earth's shadow covers the satellite, so the solar panels give no power and the battery takes over.
- **Naija analogy:** The satellite's own "NEPA has taken light". The battery is its inverter.
- **Example:** 46 eclipse hours in this file, every one at 21:00 UTC (22:00 in Lagos).

<span class="pill">W3D1</span>

### 🌘 Eclipse season
- **Plain English:** The weeks around each equinox (March and September) when the Earth's shadow crosses the satellite's orbit for up to 72 minutes a day.
- **Naija analogy:** NEPA's scheduled load-shedding season, but for the satellite. It switches to battery.
- **Example:** Eclipse hours sit at 21:00 UTC from 1 September to 16 October in the bus-power file.

<span class="pill">W2D1</span> <span class="pill">W2D3</span>

### 🔋 End-of-discharge voltage
- **Plain English:** The battery's voltage at the end of an eclipse, when it has worked hardest. Lower means a deeper discharge or an older battery.
- **Naija analogy:** How much power is left in your inverter battery just before NEPA brings light back.
- **Example:** `eod_voltage_v` dips in March and September and slowly drifts down over the years.

<span class="pill">W2D1</span> <span class="pill">W2D3</span>

### 🌍 Equinox
- **Plain English:** The two days a year (around 21 March and 23 September) when day and night are equal. Eclipse seasons are centred on them.
- **Naija analogy:** The two fixed “owambe Saturdays” of the satellite calendar: you can plan for them years ahead.
- **Example:** The seasonal bumps in the lab land in March and September.

<span class="pill">W2D3</span>

### 📌 Event
- **Plain English:** One real problem with a start and an end. It can last one hour or many months.
- **Naija analogy:** One power outage. Whether NEPA takes light for 5 minutes or 5 days, it's one outage.
- **Example:** EV05, the amplifier's cooling-loop blockage, lasts 233 days.

<span class="pill">W4D1</span>

### 🎯 Event-level scoring
- **Plain English:** Scoring per event (caught or missed), not per row. A 233-day event is one thing to catch.
- **Naija analogy:** A teacher marks "did you answer question 4?", not "how many lines did you write for question 4?".
- **Example:** Flagging one day of EV05 counts as one catch, not 233.

<span class="pill">W4D1</span>

### 🧮 Expected value (model)
- **Plain English:** What a reading *should* be, given what we already know (drive level, time of year…).
- **Naija analogy:** Mama Put expects tomatoes to be dear in the scarce season. That's her model.
- **Example:** On 3 Sep 2024 the recipe expected 63.1 °C.

<span class="pill">W3D2</span>

### 📰 Exponential smoothing (`.ewm`)
- **Plain English:** A smoother that gives the newest values the most weight and older values less and less.
- **Naija analogy:** How you rate a footballer: last week's match counts most, matches from last season count a little.
- **Example:** `s.ewm(alpha=0.3).mean()`

<span class="pill">W1D3</span>

### 📉 Fade rate
- **Plain English:** How much capacity a battery loses per year.
- **Naija analogy:** How fast your new phone's battery stops lasting the whole day.
- **Example:** −2.24 Ah/yr before April 2025, −3.68 after.

<span class="pill">W3D3</span>

### 🐺 False alarm
- **Plain English:** An alarm when nothing is actually wrong.
- **Naija analogy:** The boy who cried wolf. Or the car alarm that goes off for every keke.
- **Example:** The 46 eclipse-night alarms from the 20 A floor.

<span class="pill">W3D1</span>

### 🔕 False-alarm budget
- **Plain English:** How many pointless alarms you can afford before people stop listening.
- **Naija analogy:** The car alarm on your street that goes off for every keke. After a week, nobody even looks.
- **Example:** ±2σ ≈ 131 false alarms per 2,880 hours; ±3σ ≈ 8.

<span class="pill">W3D2</span>

### 📟 False alarm (false positive)
- **Plain English:** A flag when nothing was really wrong. Each one costs someone's time.
- **Naija analogy:** Musa shouting "Thief!" at the neighbour's goat. Again.
- **Example:** The SoC floor raised 18 false alarms, all on normal eclipse nights.

<span class="pill">W4D1</span>

### 📝 Finding (4-sentence)
- **Plain English:** A short write-up in four sentences: Situation, Observation, Implication, Recommendation.
- **Naija analogy:** How a good doctor explains: what's happening, what the test shows, what it means, what to do.
- **Example:** “Weekends average 3.4 tickets a day vs 7.1 on weekdays” is an Observation.

<span class="pill">W2D3</span>

### 📰 Finding title
- **Plain English:** A chart title that states what the chart shows, ideally with a number.
- **Naija analogy:** A newspaper headline: “Eagles win 2–0”, not “Football match”.
- **Example:** “Ka-band link went down on 11 of 31 August days”.

<span class="pill">W1D2</span>

### 🕵🏾 Gap
- **Plain English:** A period with no reading at all, e.g. a missing day.
- **Naija analogy:** The days in your diary when you were “too busy” to write. 🙈
- **Example:** In B5 we found 3 missing days in March 2024.

<span class="pill">W1D1</span>

### 🛰️ GEO (geostationary) satellite
- **Plain English:** A satellite about 36,000 km up that moves with the Earth's spin, so it stays over the same spot.
- **Naija analogy:** A security light on a high pole: it always shines on the same compound.
- **Example:** NigComSat-1R sits at 42.5° East.

<span class="pill">W1D1</span>

### 🗺️ Geopolitical zones
- **Plain English:** Nigeria's six regional groupings: North West, North East, North Central, South West, South East, South South.
- **Naija analogy:** The six “houses” at inter-house sports.
- **Example:** The `region` column in the VSAT file.

<span class="pill">W1D2</span>

### 💻 Google Colab
- **Plain English:** A free website where you write and run Python. Google's computer does the work; yours just shows the screen.
- **Naija analogy:** A cyber café computer that lives in your browser, never runs out of fuel and never asks for ₦200 per hour.
- **Example:** You open `W1D1-exercise.ipynb` in Colab and run it without installing anything.

<span class="pill">W1D1</span>

### ↕️ Hysteresis
- **Plain English:** Switching the alarm ON at one level and OFF at a different level, so it doesn't flicker on and off.
- **Naija analogy:** The air-conditioner that starts at 26 °C but only stops at 23 °C, instead of clicking on and off all night.
- **Example:** Alarm on when margin drops below 2 dB, cleared only when it rises above 3 dB.

<span class="pill">W3D1</span>

### 🧷 Index (DatetimeIndex)
- **Plain English:** The row labels of a table. When they're dates, pandas can do time tricks with them.
- **Naija analogy:** The page numbers of a book. Put dates there and you can jump straight to “August 2024.”
- **Example:** `index_col="timestamp"` makes the dates the index.

<span class="pill">W1D1</span>

### 💯 Index to a baseline
- **Plain English:** Divide every value by a starting value and multiply by 100, so everything starts at 100 and you see *change*.
- **Naija analogy:** Comparing students by how much they improved since last term, not by raw score.
- **Example:** `wide / wide.iloc[0] * 100`: South East fell furthest from its own start.

<span class="pill">W1D2</span>

### 🔎 Investigation
- **Plain English:** Answering one question with data, from loading the file to writing the conclusion.
- **Naija analogy:** A mechanic's full diagnosis, not just “e don spoil”.
- **Example:** “Is our battery getting tired?”: load → profile → plot → smooth → decompose → ACF → finding.

<span class="pill">W2D3</span>

### 📶 Ka-band
- **Plain English:** A high-frequency radio band that carries lots of data but is very sensitive to rain.
- **Naija analogy:** A sports car: very fast, but it hates bad roads (here: heavy rain).
- **Example:** The Ka-band Nigeria spot beam in today's dataset.

<span class="pill">W1D1</span>

### 🪞 Lag
- **Plain English:** How many steps back you look. Lag 1 = one step ago, lag 7 = seven steps ago.
- **Naija analogy:** "Last week this time" when people gist about what happened last week at this same hour.
- **Example:** On daily data, lag 7 = the same weekday last week. On hourly data, lag 24 = the same hour yesterday.

<span class="pill">W2D2</span>

### ⏰ Lag (delay)
- **Plain English:** How late a smoothed line reacts to a real change. For a trailing window, about half the window.
- **Naija analogy:** News reaching the village two weeks after it happened in Abuja.
- **Example:** The trailing 30-day peak came 14 days after the centred one.

<span class="pill">W1D3</span>

### 🚰 Leaking the answer
- **Plain English:** Giving a detector a column that is a reaction to the thing you're trying to detect, so it cheats without knowing.
- **Naija analogy:** Judging who studied for the exam by who looks tired the next morning. You're measuring the after-effect, not the cause.
- **Example:** `uplink_power_dbm` rises because it rains (correlation 0.97). Feed it in and you build a rain detector.

<span class="pill">W3D1</span>

### 🪜 Level shift
- **Plain English:** The series jumps to a new normal and stays there.
- **Naija analogy:** Rent goes up and never comes back down.
- **Example:** The amplifier runs about 2 °C hotter from May 2025 onward.

<span class="pill">W3D1</span> <span class="pill">W3D2</span>

### ⛽ Link margin (dB)
- **Plain English:** How much signal is left above the minimum the receiver needs. Below 0 dB the link is down.
- **Naija analogy:** Fuel above the reserve line. Positive: you can still drive. Zero: you're pushing the car. 🚗
- **Example:** `link_margin_db` in `rf_link_quality_hourly`.

<span class="pill">W1D2</span>

### 🪄 Logarithm (log)
- **Plain English:** A maths function that turns multiplying into adding. `np.log()` in Python.
- **Naija analogy:** A translator who turns "times" talk into "plus" talk so everybody understands.
- **Example:** `np.log(demo["multiplicative"])`: the swing stops growing.

<span class="pill">W2D1</span>

### 📏 Long format
- **Plain English:** One row per group per time: many rows, few columns. How databases usually export.
- **Naija analogy:** A class register written as one line per student per day.
- **Example:** `vsat_uptime_by_region_weekly`: 312 rows = 52 weeks × 6 zones.

<span class="pill">W1D2</span>

### 📐 MAD (median absolute deviation)
- **Plain English:** The median distance from the median: a wobble measure that ignores a few wild points.
- **Naija analogy:** Asking "how far do people usually live from the office?" without letting the one person who commutes from Ibadan spoil the answer.
- **Example:** Robust σ stayed 0.09 A while ordinary σ jumped to 1.08 A after a dropout.

<span class="pill">W3D2</span>

### 📏 MAE (mean absolute error)
- **Plain English:** The average size of a forecast's mistakes, ignoring whether they were too high or too low.
- **Naija analogy:** How many minutes late your friend usually is, on average. 😅
- **Example:** `(s - s.shift(7)).abs().mean()`

<span class="pill">W2D2</span>

### 🎯 Median
- **Plain English:** The middle value when you sort the numbers. Wild values can't drag it.
- **Naija analogy:** The salary of the middle person in the office. The MD's big salary doesn't move it.
- **Example:** The rolling median of the last 168 sunlit hours.

<span class="pill">W3D2</span>

### 🙈 Miss (false negative)
- **Plain English:** A real event the detector never flagged.
- **Naija analogy:** The guard was sleeping when the thief came.
- **Example:** Every value-based detector missed EV06, the battery fade speeding up.

<span class="pill">W4D1</span>

### 〰️ Moving average (centred)
- **Plain English:** The average of a window of values around each point. Classic decomposition uses one to find the trend, so the trend is missing for half a window at each end.
- **Naija analogy:** Judging a student by the average of the tests around each week. You can't do it for the first and last weeks.
- **Example:** The Ka-band trend is empty for the first and last 6 months.

<span class="pill">W2D1</span>

### 🧮 Moving (rolling) average
- **Plain English:** The average of the last N values, recalculated every day as the window moves forward.
- **Naija analogy:** Your average fuel spend over the last 7 days. One big fill-up on Monday doesn't make you panic.
- **Example:** The 7-day average of NOC tickets sits around 6 a day in the dry season.

<span class="pill">W1D3</span>

### ✖️ Multiplicative model
- **Plain English:** observed = trend × seasonal × residual. The seasonal swing grows as the level grows.
- **Naija analogy:** December fare goes up 20%. When fares are higher, 20% is more naira.
- **Example:** The `multiplicative` column in `additive_multiplicative_demo`: swing grows from about 0.29 to 0.54.

<span class="pill">W2D1</span>

### 🏭 Named process
- **Plain English:** A specific, real task your unit does regularly, with an owner. Not a general topic.
- **Naija analogy:** Not “food”: “Mama's Saturday jollof for the street party”.
- **Example:** “The weekly battery-health review on the bus subsystem.”

<span class="pill">W2D3</span>

### 🧠 NameError
- **Plain English:** Python's way of saying “I don't know this name.” Usually you skipped a cell, restarted, or forgot quotes.
- **Naija analogy:** Calling someone “Chief” at a party when nobody has introduced him to you yet.
- **Example:** `NameError: name 'ka' is not defined` → run the cells above.

<span class="pill">W1D1</span>

### 🕳️ NaN
- **Plain English:** “Not a Number”. pandas' symbol for an empty or missing value.
- **Naija analogy:** The empty seat at a wedding where the guest didn't come.
- **Example:** After `.asfreq("D")`, the 3 deleted days show `NaN`.

<span class="pill">W1D1</span>

### 🎧 NOC (Network Operations Centre)
- **Plain English:** The team that watches the network 24/7 and opens a ticket for every fault.
- **Naija analogy:** The control room of a big estate, where security watches all the CCTV.
- **Example:** `noc_tickets_daily.csv` counts their tickets.

<span class="pill">W1D3</span>

### 🎲 Noise
- **Plain English:** Random wobble that means nothing. Don't react to it.
- **Naija analogy:** Weighing yourself after eating amala: 2 kg up doesn't mean you're getting fat. 😄
- **Example:** NOC tickets 38 one week, 41 the next = the same week twice.

<span class="pill">W1D1</span>

### ☕ Noise (again)
- **Plain English:** Random week-to-week wobble with no meaning. Don't react to it.
- **Naija analogy:** Your weight after a heavy plate of pounded yam. Wait a week before you worry.
- **Example:** 38 vs 41 tickets a week, when the mean is about 36 and the usual swing is about 5.

<span class="pill">W1D3</span>

### 📓 Notebook
- **Plain English:** A document that mixes reading (text) and code you can run, in one page.
- **Naija analogy:** A recipe book where you can cook each step right on the page and taste it immediately.
- **Example:** Files ending in `.ipynb` are notebooks.

<span class="pill">W1D1</span>

### 🏁 Onset (start date)
- **Plain English:** The day a change really began, as opposed to the day the alarm rang.
- **Naija analogy:** The day your tyre started leaking vs the day you noticed it was flat.
- **Example:** The practice fault began 10 Feb 2025; the alarm rang 13 Feb 2025.

<span class="pill">W3D3</span>

### 🌗 Operating state
- **Plain English:** A distinct mode the system runs in, each with its own normal behaviour.
- **Naija analogy:** Your house on NEPA light vs on generator vs on inverter: different "normal" noise, different normal bills.
- **Example:** eclipse (~0 A), recharge (~29.6 A), sunlit (~28.1 A).

<span class="pill">W3D2</span>

### ❌ Outage
- **Plain English:** The link is actually down: link margin below 0 dB.
- **Naija analogy:** Not "the network is slow", but "no network at all".
- **Example:** 12 outage hours in August, each lasting one hour.

<span class="pill">W3D1</span>

### 🐼 pandas
- **Plain English:** The Python library for working with tables of data.
- **Naija analogy:** Microsoft Excel, but you control it by typing instructions, so it never gets tired.
- **Example:** `import pandas as pd`, then `pd.read_csv(...)`.

<span class="pill">W1D1</span>

### 🗓️ parse_dates
- **Plain English:** Tells pandas “this column is a date, not just text.”
- **Naija analogy:** Telling the gateman, “this is not just any paper, it's my ID card.”
- **Example:** `pd.read_csv(..., parse_dates=["timestamp"])`

<span class="pill">W1D1</span>

### ✂️ Partial period
- **Plain English:** A bucket at the edge of the data that doesn't have all its days.
- **Naija analogy:** Judging a football match at half-time and saying the team scored few goals.
- **Example:** The last weekly bucket has only 2 days, so it shows just 9 tickets.

<span class="pill">W1D3</span>

### 🥁 Period
- **Plain English:** How many rows until the seasonal pattern repeats. It comes from the process, not from a default.
- **Naija analogy:** How often your esusu (contribution) group meets: weekly means 7 days, monthly means 12 times a year.
- **Example:** 24 for hourly bus power, 7 for daily tickets, 12 for monthly availability.

<span class="pill">W2D1</span> <span class="pill">W2D2</span>

### 🧩 Persistence (memory)
- **Plain English:** A series "has memory" when its past values help you guess its next values.
- **Naija analogy:** A neighbour who has been borrowing sugar every week will likely knock again next week. 😅
- **Example:** Throughput has strong weekly memory; random noise has none.

<span class="pill">W2D2</span>

### ⏳ Persistence rule
- **Plain English:** Only alarm if the reading stays bad for N readings in a row.
- **Naija analogy:** Not shouting "NEPA has taken light!" until the light has been off for a full minute.
- **Example:** A 2-hours-in-a-row rule caught 0 of the 12 one-hour outages in August.

<span class="pill">W3D1</span>

### 🔄 pivot
- **Plain English:** The pandas command that reshapes long → wide.
- **Naija analogy:** Rearranging wedding guests from one long queue into tables by family.
- **Example:** `vsat.pivot(index="week_start", columns="region", values="uptime_pct")`

<span class="pill">W1D2</span>

### 📐 plot_acf / statsmodels
- **Plain English:** `statsmodels` is a Python library for statistics; `plot_acf` is its correlogram function. Colab already has it.
- **Naija analogy:** A specialist mechanic: pandas is the general workshop, statsmodels is the one who knows engines.
- **Example:** `from statsmodels.graphics.tsaplots import plot_acf`

<span class="pill">W2D2</span>

### 🧪 Practice (injected) fault
- **Plain English:** A small fault you add to clean data on purpose, so you know the right answer and can test your detector.
- **Naija analogy:** A fire drill: you know there is no fire, but you learn exactly how fast everyone gets out.
- **Example:** `practice_residuals()` hides +0.3 °C in the amplifier's calm leftovers.

<span class="pill">W3D3</span>

### 📟 Precision
- **Plain English:** Of all the alarms, the fraction that were real. "When it pages me, is it real?"
- **Naija analogy:** Of all the times Musa shouted "Thief!", how many were actual thieves?
- **Example:** Musa: 9 ÷ 200 = 0.045. All-hours control chart: 0.06.

<span class="pill">W4D1</span>

### 🚨 Priority-1 ticket
- **Plain English:** The most urgent kind of fault ticket. Rare, but serious.
- **Naija analogy:** A call from your MD at 11pm: it doesn't happen often, but when it does, everybody moves.
- **Example:** About 1 a day, and 17% of days have none.

<span class="pill">W1D3</span>

### 🧑🏾‍💼 Process owner
- **Plain English:** The person responsible for that process, who will use or approve your tool.
- **Naija analogy:** The oga at the top of that particular desk.
- **Example:** The shift lead who runs NOC fault escalation.

<span class="pill">W2D3</span>

### 🔍 Profiling
- **Plain English:** Quick checks before you trust a dataset: rows, date range, gaps, duplicates, missing values.
- **Naija analogy:** Inspecting a tokunbo car before you pay: engine, tyres, papers.
- **Example:** `len(ka)`, `ka.index.min()`, `ka.isna().sum()`.

<span class="pill">W1D1</span>

### 🌧️ Rain fade
- **Plain English:** Heavy rain absorbs the satellite signal, so quality drops or the link goes down.
- **Naija analogy:** DStv showing “No signal” during a heavy Lagos downpour.
- **Example:** The yearly dips in availability, worst in July and August.

<span class="pill">W1D1</span> <span class="pill">W1D2</span>

### 🚫 Random-split leakage
- **Plain English:** If you split time data randomly, the test set's near-copies sit in the training set, so the answers leak.
- **Naija analogy:** WAEC expo: if you saw the questions before the exam, your score is fake.
- **Example:** Day 8 in test, days 1 and 15 (same weekday, r = 0.99) in training.

<span class="pill">W2D2</span>

### 🐘 Rare events (class imbalance)
- **Plain English:** When the thing you're hunting is tiny compared with everything else, so "always say no" looks great.
- **Naija analogy:** Looking for 6 fake ₦1,000 notes in a bag of 4,706 genuine ones.
- **Example:** 6 events in 4,706 readings.

<span class="pill">W4D1</span>

### 📦 Raw data
- **Plain English:** The original export from a system, before you clean or summarise it.
- **Naija analogy:** Unpeeled yam straight from the market.
- **Example:** Never commit raw NIGCOMSAT exports to GitHub: commit only your code.

<span class="pill">W2D3</span>

### 🕸️ Recall
- **Plain English:** Of all the real events, the fraction the detector caught. "Did we miss anything?"
- **Naija analogy:** Of the 10 thieves who came this year, how many did the guard catch?
- **Example:** Musa: 9 ÷ 10 = 0.90. Sunlit control chart: 3 ÷ 3 = 1.00.

<span class="pill">W4D1</span>

### ⚖️ Recall-first vs precision-first
- **Plain English:** Deciding which number matters more for a system, based on what a miss costs vs what a false alarm costs.
- **Naija analogy:** A smoke alarm should be recall-first (better a false alarm than a burnt house). A car alarm that screams at every keke is a precision problem.
- **Example:** Battery and power: recall first. Rain-fade dashboards: precision first.

<span class="pill">W4D1</span>

### ⚡ Recharge hour
- **Plain English:** The hour after an eclipse, when the panels push extra current to refill the battery and the battery warms up.
- **Naija analogy:** When NEPA brings light back and every phone and power bank in the house charges at once.
- **Example:** Battery temperature goes above 22 °C in the hour after every eclipse: normal.

<span class="pill">W3D1</span>

### 🔋 Recharge hours
- **Plain English:** The hours just after an eclipse when the solar array works extra to refill the battery.
- **Naija analogy:** Charging your phone to 100% the moment light comes back.
- **Example:** 138 recharge hours in the bus-power file.

<span class="pill">W3D2</span>

### 🗓️ Reference period
- **Plain English:** A calm, known-good stretch of data used to learn what normal looks like.
- **Naija analogy:** Judging your new neighbour by a quiet fortnight, not by the night of their wedding party.
- **Example:** 1–15 August 2025: sunlit, no eclipse yet, nothing strange.

<span class="pill">W3D2</span>

### 📈 Regression (line of best fit)
- **Plain English:** A way to learn a recipe like "temp ≈ base + k × drive" from past data.
- **Naija analogy:** Working out from past trips that every extra 10 km adds about the same to your fuel cost.
- **Example:** temp ≈ 49.5 + 0.17 × drive + sun-angle wave.

<span class="pill">W3D2</span>

### 🗂️ Repository (repo)
- **Plain English:** A project folder tracked by Git, often stored on GitHub, holding your code and its history.
- **Naija analogy:** Your project file at the registry, with every version stamped and dated.
- **Example:** Your final project's code, `requirements.txt` and `README.md` live in a repo.

<span class="pill">W2D3</span>

### 🔁 resample
- **Plain English:** Change the time step of a series (hourly → daily) and choose how to summarise each new step.
- **Naija analogy:** Turning a daily sales diary into a weekly report: you must decide to add, average or take the best day.
- **Example:** `.resample("D").min()`

<span class="pill">W1D2</span> <span class="pill">W1D3</span>

### 🔄 Reset
- **Plain English:** Setting the running total back to zero after someone has checked an alarm.
- **Naija analogy:** Clearing the tab at the mama put after you've paid. You don't keep paying for last week.
- **Example:** Without a reset, CUSUM alarms every single day after the real step.

<span class="pill">W3D3</span>

### 🎲 Residual
- **Plain English:** What's left after the trend and season are removed. Mostly noise, but big residuals are surprises worth investigating.
- **Naija analogy:** After you've explained the traffic by "it's Monday" and "it's raining", whatever delay is left is the keke that broke down.
- **Example:** In August, the biggest residual points straight at an injected solar-array dropout.

<span class="pill">W2D1</span>

### ↩️ Response (vs cause)
- **Plain English:** Something that changes *because of* something else.
- **Naija analogy:** You carry an umbrella because it's raining. The umbrella didn't bring the rain.
- **Example:** Uplink power is a response to rain.

<span class="pill">W1D2</span>

### 🔒 Restricted data
- **Plain English:** Real NIGCOMSAT data that must not leave NIGCOMSAT systems or go into outside tools without permission.
- **Naija analogy:** Your ATM PIN: useful, but you don't paste it into WhatsApp.
- **Example:** Real telemetry, RF records and network logs. Course data is synthetic and safe.

<span class="pill">W2D3</span>

### 🛡️ Robust
- **Plain English:** A method that doesn't let a few extreme values pull the result around.
- **Naija analogy:** One bad experience at one buka shouldn't make you blacklist every buka in Lagos.
- **Example:** With one fake disaster August, robust STL keeps August's seasonal effect near −1.2 instead of −3.0.

<span class="pill">W2D1</span>

### 🧭 Robust z-score
- **Plain English:** How many robust σ a reading sits from the rolling median.
- **Naija analogy:** "How many times more than usual is this bill?"
- **Example:** The dropouts sat about 140 robust σ below normal.

<span class="pill">W3D2</span>

### 🏎️ Rolling slope
- **Plain English:** The speed of change over the last N days, recalculated every day.
- **Naija analogy:** Your car's speedometer: it tells you how fast you're going right now, not how far you've gone.
- **Example:** `rolling_slope(cap, 90)` crossed −3.0 Ah/yr on 2 May 2025.

<span class="pill">W3D3</span>

### 〽️ Rolling standard deviation
- **Plain English:** How much the values jumped around inside the window. A measure of wobble.
- **Naija analogy:** How much your neighbour's generator noise goes up and down in one evening.
- **Example:** `s.rolling(7).std()`

<span class="pill">W1D3</span>

### 🌊 Rolling window
- **Plain English:** A fixed number of rows that slides along the series one row at a time. You calculate something (usually the average) inside it.
- **Naija analogy:** A danfo with exactly 7 seats: every time one passenger enters at the front, the oldest one drops at the back.
- **Example:** `tk["tickets_raised"].rolling(7).mean()`

<span class="pill">W1D3</span>

### 🪜 Run rules
- **Plain English:** Extra alarm rules that look at patterns, not just single points. Rule 1: one point beyond 3σ. Rule 2: nine in a row on one side of the centre.
- **Naija analogy:** One late payment is chance. Nine late payments in a row means something has changed.
- **Example:** Rule 2 is best at catching level shifts.

<span class="pill">W3D2</span>

### ➕ Running total
- **Plain English:** A number you keep adding to, day after day, instead of looking at each day alone.
- **Naija analogy:** Your esusu/ajo contribution book: one day's ₦2,000 is small, the month's total is not.
- **Example:** CUSUM's `S` is a running total of leftovers minus slack.

<span class="pill">W3D3</span>

### 🔄 Runtime / session
- **Plain English:** The live connection to Google's computer, plus everything it currently remembers.
- **Naija analogy:** A phone call. Hang up (restart) and the other person forgets what you were saying.
- **Example:** *Runtime → Restart session* wipes the memory. Run STEP 0 again after it.

<span class="pill">W1D1</span>

### 💾 Save a copy in Drive
- **Plain English:** Makes your own editable copy of the notebook in your Google Drive.
- **Naija analogy:** Photocopying the class notes before writing on them, so you don't scribble on the original.
- **Example:** *File → Save a copy in Drive*. Your copy lands in Drive → *Colab Notebooks*.

<span class="pill">W1D1</span>

### 🧑🏾‍⚖️ Scoring rules
- **Plain English:** The agreement on what counts as a catch and what counts as a false alarm, written down **before** anyone computes a score.
- **Naija analogy:** Agreeing the rules of the five-a-side match before kick-off, not after your team concedes.
- **Example:** One flag inside an event = caught; many flags inside one event = one catch.

<span class="pill">W4D1</span>

### 🔁 Seasonal component
- **Plain English:** The pattern that repeats exactly every period: the same 12 numbers every year, or the same 7 numbers every week.
- **Naija analogy:** Rush hour at 7am every weekday, like clockwork.
- **Example:** August is about 1.1 points below the yearly average every year.

<span class="pill">W2D1</span>

### 🔧 seasonal_decompose
- **Plain English:** The classic decomposition function. Simple and fast, but it assumes the season looks the same every cycle.
- **Naija analogy:** A tailor who uses one measurement for you every year, even if you've added weight. 😅
- **Example:** `parts = seasonal_decompose(series, model="additive", period=7)`

<span class="pill">W2D1</span>

### 🗓️ Seasonal naive ("same weekday last week")
- **Plain English:** Forecast each day with the value from one period ago.
- **Naija analogy:** Expecting this Friday's traffic to be like last Friday's traffic.
- **Example:** For throughput its average error is 0.062 Gbps, about 5× better than "same as yesterday" (0.338).

<span class="pill">W2D2</span>

### 🌧️ Seasonality
- **Plain English:** A pattern that repeats on a **fixed calendar**: every day, every week, every year.
- **Naija analogy:** Harmattan every December, rainy season every year, traffic every weekday morning.
- **Example:** Ka-band availability dips every August.

<span class="pill">W1D1</span>

### 📈 Shared trend
- **Plain English:** Two series both rising (or falling) over time for their own reasons, which makes them look linked.
- **Naija analogy:** Your salary and the price of garri both rose over 5 years. One didn't cause the other.
- **Example:** Amplifier temperature and RF drive both drift up over two years.

<span class="pill">W2D2</span>

### ⏪ .shift()
- **Plain English:** The pandas command that makes a lagged copy by sliding every value down.
- **Naija analogy:** Everyone in the queue moving one seat back so a latecomer can sit in front.
- **Example:** `s.shift(1)` puts yesterday's value on today's row.

<span class="pill">W2D2</span>

### ⌨️ Shift + Enter
- **Plain English:** The keyboard shortcut that runs the current cell and moves to the next.
- **Naija analogy:** “Next please!” at the bank queue.
- **Example:** Click a cell, press Shift + Enter, see the output.

<span class="pill">W1D1</span>

### ⏱️ Shift hours (the cost of false alarms)
- **Plain English:** False alarms × minutes to check each one, turned into engineer hours. The number a manager can decide on.
- **Naija analogy:** Counting how much fuel the generator wasted while nobody was home.
- **Example:** 46 per season × 2 seasons × 20 minutes ≈ 31 hours a year, about 4 shifts.

<span class="pill">W4D1</span>

### 🤫 Silent degradation
- **Plain English:** Something wearing out without any alarm firing.
- **Naija analogy:** Tyres going bald slowly. No warning light, until the blow-out.
- **Example:** A 95 Ah capacity limit fires 0 times in three years of fading.

<span class="pill">W3D1</span>

### 📜 SLA (Service Level Agreement)
- **Plain English:** The promise to a customer, e.g. “the link will be up 99.5% of the time”.
- **Naija analogy:** The landlord's promise of “24 hours light and water” in the house advert. 😅
- **Example:** “Did we breach the SLA?” is answered with daily **minimums**, not averages.

<span class="pill">W1D2</span> <span class="pill">W1D3</span>

### 🤏 Slack (k)
- **Plain English:** A small allowance taken away every day, so ordinary noise doesn't pile up.
- **Naija analogy:** The “abeg, small change” the bus conductor never returns. Too small to fight over.
- **Example:** `k = 0.5 × σ` = 0.10 °C for the amplifier.

<span class="pill">W3D3</span>

### 📐 Slope alarm (fade-rate alarm)
- **Plain English:** An alarm on how **fast** something is changing, not on its value. It catches drifts that never cross a fixed line.
- **Naija analogy:** Your fuel gauge says half a tank, but it was full an hour ago. The level is fine; the speed of dropping is the problem.
- **Example:** Fade faster than −3 Ah a year → alarm. It catches EV06 with zero false alarms.

<span class="pill">W4D1</span>

### 🐢 Slow decay
- **Plain English:** Bars that start high and fade gently, lag after lag. It's the fingerprint of a trend.
- **Naija analogy:** Lagos rent: this year looks like last year, which looked like the year before… all going one way.
- **Example:** Transponder utilisation: 0.90, 0.81, 0.73, 0.64…

<span class="pill">W2D2</span>

### 🐢 Slow drift
- **Plain English:** A gradual change, a little every day. No single day looks unusual.
- **Naija analogy:** Your trousers getting tighter small-small since December. 😅
- **Example:** A rolling "expected" follows a slow drift, so its residual never notices.

<span class="pill">W3D2</span>

### 🖼️ Small multiples
- **Plain English:** A grid of small, identical charts, one per group, sharing the same y-axis.
- **Naija analogy:** Passport photos of the whole family: same size, same background, so you can compare faces.
- **Example:** Six mini charts, one per geopolitical zone, `sharey=True`.

<span class="pill">W1D2</span>

### 🌀 Smoothing
- **Plain English:** Removing the small, fast wiggles so the slower, real movement is easier to see.
- **Naija analogy:** Ironing a shirt: the shape is still there, the creases are gone.
- **Example:** The 7-day line shows the rainy-season rise hidden inside the daily zig-zag.

<span class="pill">W1D3</span>

### 🌞 Solar-array current
- **Plain English:** The electric current coming from the satellite's solar panels. About 27.8 A in full sunlight.
- **Naija analogy:** The output of your rooftop solar panel on a sunny afternoon.
- **Example:** A sudden drop to about 16 A with no eclipse is a fault: a "string dropout".

<span class="pill">W2D1</span>

### 🍝 Spaghetti chart
- **Plain English:** Too many lines on one chart. Nobody can follow any of them.
- **Naija analogy:** Ten danfo routes drawn on one map with the same blue pen.
- **Example:** Six zones on one axis: try finding South South.

<span class="pill">W1D2</span>

### 🔢 Sparse (small) counts
- **Plain English:** Counts that are usually 0, 1 or 2. One extra event is a big jump, so they need wider windows.
- **Naija analogy:** Counting how many times NEPA brings light at 3am. Mostly zero, sometimes one.
- **Example:** Priority-1 tickets per day.

<span class="pill">W1D3</span>

### 🚨 Special-cause variation
- **Plain English:** A change with a real reason behind it: worth investigating.
- **Naija analogy:** Traffic not moving at all because a tanker fell on the bridge.
- **Example:** The array dropping to 15.3 A in full sun.

<span class="pill">W3D2</span>

### 📈 Spike
- **Plain English:** A bar much taller than its neighbours, sticking above the shaded band.
- **Naija analogy:** The one day in the month when everyone rushes to the bank: salary day.
- **Example:** Throughput spikes at lags 7, 14, 21, 28, 35.

<span class="pill">W2D2</span>

### 🔦 Spot beam
- **Plain English:** A satellite beam aimed at one region, not the whole continent.
- **Naija analogy:** A torchlight pointed at one spot instead of a bulb lighting the whole room.
- **Example:** “Nigeria spot beam” in the `beam` column.

<span class="pill">W1D1</span>

### 🎭 Spurious correlation
- **Plain English:** A strong correlation between two things that are NOT really linked.
- **Naija analogy:** Suya sales and generator sales both rise toward December. Suya doesn't sell generators. 😄
- **Example:** Made-up suya vs generators: r = 0.97.

<span class="pill">W2D2</span>

### 🥖 Stale reference
- **Plain English:** Limits learned long ago that no longer match today's normal.
- **Naija analogy:** Last year's price list at the market: everything looks "too expensive" now.
- **Example:** 1,861 of 2,696 sunlit hours fall outside the August band by November.

<span class="pill">W3D2</span>

### 📐 Standard deviation (σ, "sigma")
- **Plain English:** The typical size of the wobble around the average.
- **Naija analogy:** How much your danfo fare moves around the usual price on a normal day.
- **Example:** Sunlit array current has σ ≈ 0.59 A when all sunlit hours are counted.

<span class="pill">W3D1</span> <span class="pill">W3D2</span>

### 🔋 State of charge (SoC)
- **Plain English:** How full the battery is, in percent.
- **Naija analogy:** The battery bar on your phone.
- **Example:** `battery_soc_pct` drops to 77.3% on the deepest eclipse night.

<span class="pill">W3D1</span>

### 📦 statsmodels
- **Plain English:** A Python library for statistics and time-series models. Already installed in Colab.
- **Naija analogy:** The big toolbox in the mechanic's shop. pandas is the spanner; statsmodels has the special tools.
- **Example:** `from statsmodels.tsa.seasonal import seasonal_decompose`

<span class="pill">W2D1</span>

### 🧠 STL
- **Plain English:** A smarter decomposition (Seasonal-Trend decomposition using LOESS) that lets the season change slowly over time.
- **Naija analogy:** A tailor who measures you again before every new outfit.
- **Example:** `STL(series, period=24, robust=True).fit()`

<span class="pill">W2D1</span>

### 🌞 Sun-angle wave (sin / cos)
- **Plain English:** A smooth yearly up-and-down added to the recipe so it knows the time of year.
- **Naija analogy:** Knowing harmattan is cold and March is hot, without being told each year.
- **Example:** `np.sin(2π × day_of_year / 365.25)` and its `cos` partner.

<span class="pill">W3D2</span>

### 🧪 Synthetic data
- **Plain English:** Made-up data designed to behave like the real thing. It's safe to share and safe to use with AI.
- **Naija analogy:** A mock exam: same style as WAEC, no real stakes.
- **Example:** All course datasets are synthetic, built to behave like NigComSat-1R.

<span class="pill">W1D1</span>

### 🙅🏾 Tampering
- **Plain English:** Reacting to common-cause wobble as if it were special cause. It makes things worse.
- **Naija analogy:** The driver who jams the brake for every small bump on the expressway: passengers suffer more, not less.
- **Example:** "Correcting" after every reading made the spread about 39% bigger in the simulation.

<span class="pill">W3D2</span>

### 🎯 Target
- **Plain English:** The value you expect when everything is normal. CUSUM measures how far each reading is from it.
- **Naija analogy:** The fuel gauge level you expect after buying ₦20,000 of fuel.
- **Example:** For leftovers (actual − expected), the target is 0.

<span class="pill">W3D3</span>

### 🚧 Threshold line
- **Plain English:** A line drawn at the level that matters (0 dB, the SLA target), so readers instantly see breaches.
- **Naija analogy:** The red line on a fuel gauge.
- **Example:** `plt.axhline(0, color="red", ls="--")`

<span class="pill">W1D2</span>

### 📶 Throughput (Gbps)
- **Plain English:** How much data a link carries, in gigabits per second.
- **Naija analogy:** How many cars pass through the toll gate per minute.
- **Example:** Over two years, about 3.9 Gbps on an average weekday and 3.0 at weekends.

<span class="pill">W2D2</span>

### ⏱️ Time series
- **Plain English:** Measurements recorded one after another in time, where the **order matters**.
- **Naija analogy:** Your NEPA light diary: “06:00 light came, 09:00 light gone…” Shuffle it and it means nothing.
- **Example:** Daily Ka-band availability from 2023 to 2025.

<span class="pill">W1D1</span>

### 🕐 Timestamp
- **Plain English:** The date and time attached to a reading.
- **Naija analogy:** The time printed on your POS receipt.
- **Example:** `2025-08-01T21:00` = 1 August 2025, 9pm UTC.

<span class="pill">W1D1</span>

### ↔️ Tolerance
- **Plain English:** A small grace window around an event, so a flag one step early or late still counts.
- **Naija analogy:** "Service starts 10 a.m." but nobody is marked absent at 10:01.
- **Example:** `tol="1h"` for hourly files, `tol="1D"` for daily files.

<span class="pill">W4D1</span>

### ⬅️ Trailing window
- **Plain English:** A window that ends today and only looks at the past. pandas does this by default.
- **Naija analogy:** Driving using only your rear-view mirror: safe information, but always a bit late.
- **Example:** `s.rolling(30).mean()` is trailing.

<span class="pill">W1D3</span>

### 📡 Transponder
- **Plain English:** A channel on the satellite that receives a signal and sends it back down. NigComSat-1R has 28 active ones.
- **Naija analogy:** One lane on a busy expressway. More lanes = more traffic carried.
- **Example:** `transponder_utilisation_monthly.csv` tracks how busy they are.

<span class="pill">W1D1</span>

### 📈 Trend
- **Plain English:** The long-term direction: up, down or flat.
- **Naija analogy:** Lagos population: more people every year.
- **Example:** Transponder utilisation climbing from about 50% to about 78%.

<span class="pill">W1D1</span>

### 📈 Trend component
- **Plain English:** The slow, long-term direction once the seasonal ups and downs are averaged away.
- **Naija analogy:** Lagos traffic getting worse year after year as the city grows, whatever the day of the week.
- **Example:** Ka-band availability trend rising slowly from about 99.24% to 99.40%.

<span class="pill">W2D1</span>

### 👯 Twin files
- **Plain English:** Two data files with the **same name** but different contents, in different folders.
- **Naija analogy:** Two people called “Emeka Okafor” in the same office: check the ID before you transfer money!
- **Example:** `battery_health_daily.csv` in week-03 (clean) vs week-04 (planted faults).

<span class="pill">W2D3</span> <span class="pill">W3D3</span>

### 🌡️ TWTA and RF drive
- **Plain English:** The TWTA (travelling-wave tube amplifier) boosts the signal before it's sent down. RF drive is how hard it's being pushed.
- **Naija analogy:** A generator: the harder you load it, the hotter it runs.
- **Example:** `twta_thermal_daily.csv`: temperature vs drive, r = 0.59 on levels, 0.40 on changes.

<span class="pill">W2D2</span>

### 📢 TWTA (travelling-wave tube amplifier)
- **Plain English:** The satellite part that makes our signal strong enough to reach the ground. It runs hot.
- **Naija analogy:** The loudspeaker at a party: bigger volume, more heat, and you notice when it starts overheating.
- **Example:** `twta_thermal_daily.csv` tracks its daily temperature.

<span class="pill">W3D3</span>

### 🏢 Unit head
- **Plain English:** The head of your department. They agree your project's scope by email.
- **Naija analogy:** Your HOD signing your project approval form.
- **Example:** Their reply email goes into your final submission.

<span class="pill">W2D3</span>

### 🌧️ Unusual ≠ anomaly
- **Plain English:** A reading can be statistically rare yet perfectly explained by known physics. Not everything rare is a fault.
- **Naija analogy:** Heavy traffic on Third Mainland Bridge at 6 p.m. on a Friday is unusual compared with 3 a.m., but nobody calls it an emergency.
- **Example:** Rain fade drops C/N below the naive line, but only 12 of the 18 flagged hours were real outages.

<span class="pill">W4D1</span>

### 🔊 Uplink power
- **Plain English:** How strongly the ground station transmits up to the satellite. It's turned up automatically when rain weakens the signal.
- **Naija analogy:** Shouting louder when the generator next door starts. You shout *because* of the noise.
- **Example:** Uplink power averages about 41 dBm when dry and about 44 dBm in rain.

<span class="pill">W1D2</span>

### 🎚️ Uplink power control
- **Plain English:** The ground station automatically raises its transmit power when rain weakens the signal.
- **Naija analogy:** Talking louder on the phone when the network starts breaking.
- **Example:** `uplink_power_dbm` rises in heavy rain: a response, not a cause.

<span class="pill">W2D2</span>

### 🌍 UTC
- **Plain English:** The world's reference clock. Satellites and telemetry usually record in UTC.
- **Naija analogy:** The “master clock” everyone agrees on, like full-time at Old Trafford: the same moment for the whole world.
- **Example:** The eclipse happens at 21:00 UTC.

<span class="pill">W1D1</span>

### 🕳️ Warm-up NaN
- **Plain English:** The empty values at the start of a rolling result, before the window has enough rows.
- **Naija analogy:** You can't average 7 days of salary when you only started work 3 days ago.
- **Example:** `rolling(7)` gives 6 `NaN` values at the start.

<span class="pill">W1D3</span>

### 🚧 Warning line
- **Plain English:** A limit you set on a speed or rate (not on the level) that triggers a check.
- **Naija analogy:** The speed limit sign: you can still be far from your destination and be going too fast.
- **Example:** −3.0 Ah per year on the battery's rolling slope.

<span class="pill">W3D3</span>

### 🇳🇬 WAT
- **Plain English:** West Africa Time, Nigeria's clock. Always **UTC + 1**, with no daylight saving.
- **Naija analogy:** Lagos time is UTC time plus one hour. (“African time” is another matter 😄)
- **Example:** 21:00 UTC = 22:00 WAT.

<span class="pill">W1D1</span>

### 🎶 Weekly rhythm (day-of-week effect)
- **Plain English:** A pattern that repeats every 7 days because people work Monday to Friday.
- **Naija analogy:** Lagos traffic: wahala on weekdays, free roads on Sunday morning.
- **Example:** Weekdays average about 7 tickets, weekends about 3.4.

<span class="pill">W1D3</span>

### 🕵🏾 "Where did that number come from?"
- **Plain English:** The question to ask of every alarm limit. A good limit has a reason you can write down.
- **Naija analogy:** "Who told you the price is ₦5,000?" before you pay at the market.
- **Example:** 20 A was a guess; mean − 3σ of sunlit data (about 26.4 A) has a reason.

<span class="pill">W3D1</span>

### ↔️ Wide format
- **Plain English:** One row per time, one column per group. What charts want.
- **Naija analogy:** The same register as a grid: students across the top, days down the side.
- **Example:** `wide` has 52 rows and 6 zone columns.

<span class="pill">W1D2</span>

### 📏 Window size
- **Plain English:** How many rows go into each calculation. Bigger = smoother but slower.
- **Naija analogy:** How many days of gossip you collect before you believe a rumour.
- **Example:** 3, 7 and 30-day windows on the same ticket data.

<span class="pill">W1D3</span>

### 📏 Y-axis range
- **Plain English:** Where the vertical axis starts and ends. Counts should start at 0; percentages that live near the top may zoom in, if you say so on the chart.
- **Naija analogy:** A “before and after” photo zoomed onto the waist: fair if you say it's zoomed. 😄
- **Example:** Availability on 96–100%; tickets per weekday from 0.

<span class="pill">W1D2</span>

### 🚦 Yellow and red limits
- **Plain English:** Two levels: yellow = warning, red = act now.
- **Naija analogy:** The fuel light comes on (yellow), then the car stops on Third Mainland Bridge (red).
- **Example:** Ground-station software often has a yellow and a red limit on each telemetry channel.

<span class="pill">W3D1</span>
