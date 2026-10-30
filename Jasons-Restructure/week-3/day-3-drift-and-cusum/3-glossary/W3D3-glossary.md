# W3D3 Glossary: today's new words

The new words from today, each with a plain meaning, a Naija way to remember it and an example from the course. (Level shift, drift, residual and expected value were introduced earlier in the week.)

## 🧾 CUSUM words

### 🧾 CUSUM (cumulative sum)
- **Plain English:** A detector that keeps a running total of small leftovers and alarms when the total gets too big.
- **Naija analogy:** Your landlord's “small-small” rent increases. No single year shocks you, but add up the receipts and you've paid ₦415k extra.
- **Example:** `S = max(0, S + leftover - k)` caught the amplifier's step on 12 May 2025.

### ➕ Running total
- **Plain English:** A number you keep adding to, day after day, instead of looking at each day alone.
- **Naija analogy:** Your esusu/ajo contribution book: one day's ₦2,000 is small, the month's total is not.
- **Example:** CUSUM's `S` is a running total of leftovers minus slack.

### 🎯 Target
- **Plain English:** The value you expect when everything is normal. CUSUM measures how far each reading is from it.
- **Naija analogy:** The fuel gauge level you expect after buying ₦20,000 of fuel.
- **Example:** For leftovers (actual − expected), the target is 0.

### 🤏 Slack (k)
- **Plain English:** A small allowance taken away every day, so ordinary noise doesn't pile up.
- **Naija analogy:** The “abeg, small change” the bus conductor never returns. Too small to fight over.
- **Example:** `k = 0.5 × σ` = 0.10 °C for the amplifier.

### 🚨 Decision limit (h)
- **Plain English:** How big the running total must get before CUSUM raises the alarm.
- **Naija analogy:** How many times your neighbour's generator must wake you before you go and knock.
- **Example:** `h = 5 × σ` = 1.02 °C. Lower h = faster but noisier.

### 🔄 Reset
- **Plain English:** Setting the running total back to zero after someone has checked an alarm.
- **Naija analogy:** Clearing the tab at the mama put after you've paid. You don't keep paying for last week.
- **Example:** Without a reset, CUSUM alarms every single day after the real step.

### 🏁 Onset (start date)
- **Plain English:** The day a change really began, as opposed to the day the alarm rang.
- **Naija analogy:** The day your tyre started leaking vs the day you noticed it was flat.
- **Example:** The practice fault began 10 Feb 2025; the alarm rang 13 Feb 2025.

### ⏳ Detection delay
- **Plain English:** How many days pass between the onset and the alarm.
- **Naija analogy:** The time between “I don pay” and the bank alert landing.
- **Example:** 3 days for the practice fault with h = 5σ; 6 days with h = 10σ.

### 📍 Change point
- **Plain English:** The moment a series switches to a new behaviour: a new level or a new speed.
- **Naija analogy:** The day the fuel price changed at the pump. Before and after are two different worlds.
- **Example:** 12 May 2025 for the amplifier; 1 April 2025 for the battery.

### 🧪 Practice (injected) fault
- **Plain English:** A small fault you add to clean data on purpose, so you know the right answer and can test your detector.
- **Naija analogy:** A fire drill: you know there is no fire, but you learn exactly how fast everyone gets out.
- **Example:** `practice_residuals()` hides +0.3 °C in the amplifier's calm leftovers.

## 🔋 Drift words

### 🏎️ Rolling slope
- **Plain English:** The speed of change over the last N days, recalculated every day.
- **Naija analogy:** Your car's speedometer: it tells you how fast you're going right now, not how far you've gone.
- **Example:** `rolling_slope(cap, 90)` crossed −3.0 Ah/yr on 2 May 2025.

### 📉 Fade rate
- **Plain English:** How much capacity a battery loses per year.
- **Naija analogy:** How fast your new phone's battery stops lasting the whole day.
- **Example:** −2.24 Ah/yr before April 2025, −3.68 after.

### 🚧 Warning line
- **Plain English:** A limit you set on a speed or rate (not on the level) that triggers a check.
- **Naija analogy:** The speed limit sign: you can still be far from your destination and be going too fast.
- **Example:** −3.0 Ah per year on the battery's rolling slope.

## 🛰️ Satellite words

### 📢 TWTA (travelling-wave tube amplifier)
- **Plain English:** The satellite part that makes our signal strong enough to reach the ground. It runs hot.
- **Naija analogy:** The loudspeaker at a party: bigger volume, more heat, and you notice when it starts overheating.
- **Example:** `twta_thermal_daily.csv` tracks its daily temperature.

### 👯 Twin files
- **Plain English:** Two files with the same name but different contents, in different folders.
- **Naija analogy:** Two cousins both called Chinedu at the same family meeting. Always check which one you're talking to.
- **Example:** `battery_health_daily.csv` in week-03 is clean; the week-04 one has the speed-up.
