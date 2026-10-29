# W3D2 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 📏 Control-chart words

### 📏 Control chart
- **Plain English:** A chart with a centre line and two limits that shows when a reading leaves its normal range.
- **Naija analogy:** Mama Put's price sense: she knows the usual range for a basket of tomatoes, so one crazy price jumps out.
- **Example:** Solar-array current with a band from 27.65 A to 28.09 A.

### ➖ Centre line
- **Plain English:** The middle line of a control chart: the average of the quiet reference period.
- **Naija analogy:** The "normal" fare for your usual bus route.
- **Example:** 27.87 A for 1–15 August.

### ↕️ Control limits (UCL / LCL)
- **Plain English:** The upper and lower edges of "normal": centre ± 3σ. Outside them = unusual.
- **Naija analogy:** The fare range where you don't argue. Above it, you ask the conductor, "Ehn?!"
- **Example:** LCL 27.65 A, UCL 28.09 A.

### 🗓️ Reference period
- **Plain English:** A calm, known-good stretch of data used to learn what normal looks like.
- **Naija analogy:** Judging your new neighbour by a quiet fortnight, not by the night of their wedding party.
- **Example:** 1–15 August 2025: sunlit, no eclipse yet, nothing strange.

### 📊 Standard deviation (sigma, σ)
- **Plain English:** The typical size of the wobble around the average.
- **Naija analogy:** How many minutes late your friend usually is. Some people's σ is 5 minutes; "African time" people's σ is 2 hours. 😄
- **Example:** σ = 0.073 A in the reference fortnight.

### 3️⃣ 3-sigma rule
- **Plain English:** On normal data, only about 0.27% of readings fall outside ±3σ by chance.
- **Naija analogy:** Someone who is never more than 15 minutes late suddenly arriving 2 hours late: that's not chance, something happened.
- **Example:** About 8 chance alarms in 2,880 normal hours.

### 🔕 False-alarm budget
- **Plain English:** How many pointless alarms you can afford before people stop listening.
- **Naija analogy:** The car alarm on your street that goes off for every keke. After a week, nobody even looks.
- **Example:** ±2σ ≈ 131 false alarms per 2,880 hours; ±3σ ≈ 8.

### 🌗 Operating state
- **Plain English:** A distinct mode the system runs in, each with its own normal behaviour.
- **Naija analogy:** Your house on NEPA light vs on generator vs on inverter: different "normal" noise, different normal bills.
- **Example:** eclipse (~0 A), recharge (~29.6 A), sunlit (~28.1 A).

### 🔋 Recharge hours
- **Plain English:** The hours just after an eclipse when the solar array works extra to refill the battery.
- **Naija analogy:** Charging your phone to 100% the moment light comes back.
- **Example:** 138 recharge hours in the bus-power file.

### 🥖 Stale reference
- **Plain English:** Limits learned long ago that no longer match today's normal.
- **Naija analogy:** Last year's price list at the market: everything looks "too expensive" now.
- **Example:** 1,861 of 2,696 sunlit hours fall outside the August band by November.

### 🌊 Common-cause variation
- **Plain English:** The everyday, built-in wobble of a stable process. Nothing to fix.
- **Naija analogy:** Lagos traffic being a bit slower on Tuesday than Monday.
- **Example:** Array current wobbling between 27.8 and 28.0 A.

### 🚨 Special-cause variation
- **Plain English:** A change with a real reason behind it: worth investigating.
- **Naija analogy:** Traffic not moving at all because a tanker fell on the bridge.
- **Example:** The array dropping to 15.3 A in full sun.

### 🙅🏾 Tampering
- **Plain English:** Reacting to common-cause wobble as if it were special cause. It makes things worse.
- **Naija analogy:** The driver who jams the brake for every small bump on the expressway: passengers suffer more, not less.
- **Example:** "Correcting" after every reading made the spread about 39% bigger in the simulation.

### 🪜 Run rules
- **Plain English:** Extra alarm rules that look at patterns, not just single points. Rule 1: one point beyond 3σ. Rule 2: nine in a row on one side of the centre.
- **Naija analogy:** One late payment is chance. Nine late payments in a row means something has changed.
- **Example:** Rule 2 is best at catching level shifts.

## 🛡️ Robust words

### 🎯 Median
- **Plain English:** The middle value when you sort the numbers. Wild values can't drag it.
- **Naija analogy:** The salary of the middle person in the office. The MD's big salary doesn't move it.
- **Example:** The rolling median of the last 168 sunlit hours.

### 📐 MAD (median absolute deviation)
- **Plain English:** The median distance from the median: a wobble measure that ignores a few wild points.
- **Naija analogy:** Asking "how far do people usually live from the office?" without letting the one person who commutes from Ibadan spoil the answer.
- **Example:** Robust σ stayed 0.09 A while ordinary σ jumped to 1.08 A after a dropout.

### ✖️ 1.4826
- **Plain English:** The number that converts MAD into the same size as a standard deviation, so "3 robust σ" means what you expect.
- **Naija analogy:** The exchange rate between two currencies, so both prices mean the same thing.
- **Example:** `robust_sigma = MAD * 1.4826`

### 🧭 Robust z-score
- **Plain English:** How many robust σ a reading sits from the rolling median.
- **Naija analogy:** "How many times more than usual is this bill?"
- **Example:** The dropouts sat about 140 robust σ below normal.

## 🔍 Residual words

### 🧮 Expected value (model)
- **Plain English:** What a reading *should* be, given what we already know (drive level, time of year…).
- **Naija analogy:** Mama Put expects tomatoes to be dear in the scarce season. That's her model.
- **Example:** On 3 Sep 2024 the recipe expected 63.1 °C.

### 📈 Regression (line of best fit)
- **Plain English:** A way to learn a recipe like "temp ≈ base + k × drive" from past data.
- **Naija analogy:** Working out from past trips that every extra 10 km adds about the same to your fuel cost.
- **Example:** temp ≈ 49.5 + 0.17 × drive + sun-angle wave.

### 🌞 Sun-angle wave (sin / cos)
- **Plain English:** A smooth yearly up-and-down added to the recipe so it knows the time of year.
- **Naija analogy:** Knowing harmattan is cold and March is hot, without being told each year.
- **Example:** `np.sin(2π × day_of_year / 365.25)` and its `cos` partner.

### 🧼 Clean residual
- **Plain English:** A residual you can trust: mean near zero, no autocorrelation left, and the same spread all year.
- **Naija analogy:** A clean bill of health from the doctor before you start the race.
- **Example:** After removing the 2 spike days, lag-1 autocorrelation fell from 0.33 to 0.06.

### 🪜 Level shift
- **Plain English:** The series jumps to a new level and stays there.
- **Naija analogy:** The landlord announcing new rent: not one expensive month, a new normal.
- **Example:** From 12 May 2025 the amplifier ran about 2.6 °C hotter than expected, on average, and every single day was flagged.

### 🐢 Slow drift
- **Plain English:** A gradual change, a little every day. No single day looks unusual.
- **Naija analogy:** Your trousers getting tighter small-small since December. 😅
- **Example:** A rolling "expected" follows a slow drift, so its residual never notices.
