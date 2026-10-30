# W3D1 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🚨 Alarm words

### 🚨 Anomaly
- **Plain English:** A reading that doesn't fit what normally happens.
- **Naija analogy:** Your quiet neighbour suddenly playing loud music at 3am. Something is off.
- **Example:** The solar-array current suddenly dropping to about half while the sun is shining.

### 🔔 Alarm (limit check)
- **Plain English:** A rule that shouts when a reading crosses a fixed number.
- **Naija analogy:** The smoke detector in the kitchen: it doesn't know you're frying plantain, it just sees smoke.
- **Example:** `bus["solar_array_current_a"] < 20` fires an alarm.

### 🧪 Detector (model)
- **Plain English:** Any rule or method that decides "normal" or "not normal". Even a fixed limit is a simple one.
- **Naija analogy:** A gateman deciding who looks suspicious. Some gatemen are better than others.
- **Example:** The 20 A floor is a detector. So is mean − 3σ.

### 🐺 False alarm
- **Plain English:** An alarm when nothing is actually wrong.
- **Naija analogy:** The boy who cried wolf. Or the car alarm that goes off for every keke.
- **Example:** The 46 eclipse-night alarms from the 20 A floor.

### 😴 Alarm fatigue
- **Plain English:** When there are so many false alarms that people stop paying attention, even to the real ones.
- **Naija analogy:** After the 10th "thief!" shout from the mai-guard, nobody comes out anymore.
- **Example:** A NOC that sees 46 useless solar-array alarms a season learns to ignore that channel.

### 🚦 Yellow and red limits
- **Plain English:** Two levels: yellow = warning, red = act now.
- **Naija analogy:** The fuel light comes on (yellow), then the car stops on Third Mainland Bridge (red).
- **Example:** Ground-station software often has a yellow and a red limit on each telemetry channel.

### ⏳ Persistence rule
- **Plain English:** Only alarm if the reading stays bad for N readings in a row.
- **Naija analogy:** Not shouting "NEPA has taken light!" until the light has been off for a full minute.
- **Example:** A 2-hours-in-a-row rule caught 0 of the 12 one-hour outages in August.

### ↕️ Hysteresis
- **Plain English:** Switching the alarm ON at one level and OFF at a different level, so it doesn't flicker on and off.
- **Naija analogy:** The air-conditioner that starts at 26 °C but only stops at 23 °C, instead of clicking on and off all night.
- **Example:** Alarm on when margin drops below 2 dB, cleared only when it rises above 3 dB.

### 🎭 Context (state-based limits)
- **Plain English:** Checking which mode the system is in before deciding whether a reading is strange.
- **Naija analogy:** A dark house at midnight is normal. A dark house at noon with the gen running is not.
- **Example:** `floor_alarm & (bus["eclipse_flag"] == 0)` only checks the limit in sunlight.

### 🕵🏾 "Where did that number come from?"
- **Plain English:** The question to ask of every alarm limit. A good limit has a reason you can write down.
- **Naija analogy:** "Who told you the price is ₦5,000?" before you pay at the market.
- **Example:** 20 A was a guess; mean − 3σ of sunlit data (about 26.4 A) has a reason.

## 🛰️ Satellite power words

### 🌘 Eclipse
- **Plain English:** The hour when the Earth's shadow covers the satellite, so the solar panels give no power and the battery takes over.
- **Naija analogy:** The satellite's own "NEPA has taken light". The battery is its inverter.
- **Example:** 46 eclipse hours in this file, every one at 21:00 UTC (22:00 in Lagos).

### 🔋 State of charge (SoC)
- **Plain English:** How full the battery is, in percent.
- **Naija analogy:** The battery bar on your phone.
- **Example:** `battery_soc_pct` drops to 77.3% on the deepest eclipse night.

### ⚡ Recharge hour
- **Plain English:** The hour after an eclipse, when the panels push extra current to refill the battery and the battery warms up.
- **Naija analogy:** When NEPA brings light back and every phone and power bank in the house charges at once.
- **Example:** Battery temperature goes above 22 °C in the hour after every eclipse: normal.

## 📏 Statistics words

### 📐 Standard deviation (σ, "sigma")
- **Plain English:** The typical size of the wobble around the average.
- **Naija analogy:** How much your danfo fare moves around the usual price on a normal day.
- **Example:** Sunlit array current has σ ≈ 0.59 A when all sunlit hours are counted.

### 🎯 3σ band (three-sigma)
- **Plain English:** Average ± 3 standard deviations. Readings outside it are rare if everything is normal.
- **Naija analogy:** "Normal fare is ₦500, give or take ₦100". ₦1,000 means something is up.
- **Example:** Sunlit 3σ band: 26.43 to 29.99 A. Only the 4 dropout hours fall outside.

## 📡 RF and fault-shape words

### 📶 C/N (carrier-to-noise ratio)
- **Plain English:** How strong the signal is compared to the background hiss, in dB. Higher is better.
- **Naija analogy:** How clearly you can hear your friend on the phone in a noisy bus park.
- **Example:** About 14.2 dB in clear sky; it falls in heavy rain.

### ❌ Outage
- **Plain English:** The link is actually down: link margin below 0 dB.
- **Naija analogy:** Not "the network is slow", but "no network at all".
- **Example:** 12 outage hours in August, each lasting one hour.

### 🚰 Leaking the answer
- **Plain English:** Giving a detector a column that is a reaction to the thing you're trying to detect, so it cheats without knowing.
- **Naija analogy:** Judging who studied for the exam by who looks tired the next morning. You're measuring the after-effect, not the cause.
- **Example:** `uplink_power_dbm` rises because it rains (correlation 0.97). Feed it in and you build a rain detector.

### 🪜 Level shift
- **Plain English:** The series jumps to a new normal and stays there.
- **Naija analogy:** Rent goes up and never comes back down.
- **Example:** The amplifier runs about 2 °C hotter from May 2025 onward.

### 🐢 Drift
- **Plain English:** A slow, steady slide. No single day looks strange.
- **Naija analogy:** Your eyesight getting a little worse every year until one day you can't read the danfo number.
- **Example:** Battery capacity fading from 103 to 95.4 Ah over three years.

### 🤫 Silent degradation
- **Plain English:** Something wearing out without any alarm firing.
- **Naija analogy:** Tyres going bald slowly. No warning light, until the blow-out.
- **Example:** A 95 Ah capacity limit fires 0 times in three years of fading.
