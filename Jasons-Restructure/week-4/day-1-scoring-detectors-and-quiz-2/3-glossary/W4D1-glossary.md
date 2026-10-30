# W4D1 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🔑 The answer key

### 🔑 Answer key (labels / ground truth)
- **Plain English:** A list of the real events: what happened, where, and when. It turns "my detector seems fine" into a score.
- **Naija analogy:** The WAEC marking scheme. Without it, every student says "I passed".
- **Example:** `telemetry_anomaly_labels.csv`: 6 events, EV01 to EV06.

### 📌 Event
- **Plain English:** One real problem with a start and an end. It can last one hour or many months.
- **Naija analogy:** One power outage. Whether NEPA takes light for 5 minutes or 5 days, it's one outage.
- **Example:** EV05, the amplifier's cooling-loop blockage, lasts 233 days.

### 🧑🏾‍⚖️ Scoring rules
- **Plain English:** The agreement on what counts as a catch and what counts as a false alarm, written down **before** anyone computes a score.
- **Naija analogy:** Agreeing the rules of the five-a-side match before kick-off, not after your team concedes.
- **Example:** One flag inside an event = caught; many flags inside one event = one catch.

### 🎯 Event-level scoring
- **Plain English:** Scoring per event (caught or missed), not per row. A 233-day event is one thing to catch.
- **Naija analogy:** A teacher marks "did you answer question 4?", not "how many lines did you write for question 4?".
- **Example:** Flagging one day of EV05 counts as one catch, not 233.

### ↔️ Tolerance
- **Plain English:** A small grace window around an event, so a flag one step early or late still counts.
- **Naija analogy:** "Service starts 10 a.m." but nobody is marked absent at 10:01.
- **Example:** `tol="1h"` for hourly files, `tol="1D"` for daily files.

## 📟 The outcomes

### ✅ Catch (true positive)
- **Plain English:** A real event the detector flagged.
- **Naija analogy:** The mai-guard shouts and there really is a thief at the gate.
- **Example:** The sunlit control chart catches all 3 solar-array dropouts.

### 🙈 Miss (false negative)
- **Plain English:** A real event the detector never flagged.
- **Naija analogy:** The guard was sleeping when the thief came.
- **Example:** Every value-based detector missed EV06, the battery fade speeding up.

### 📟 False alarm (false positive)
- **Plain English:** A flag when nothing was really wrong. Each one costs someone's time.
- **Naija analogy:** Musa shouting "Thief!" at the neighbour's goat. Again.
- **Example:** The SoC floor raised 18 false alarms, all on normal eclipse nights.

### 🧑🏾‍🔧 Duty engineer / page
- **Plain English:** The engineer on shift who gets alerted (paged) when an alarm fires, and must check it.
- **Naija analogy:** The one who gets the 2 a.m. "Oga, come and see" phone call.
- **Example:** Every false alarm is one page to the duty engineer.

## 📏 The numbers

### 🕸️ Recall
- **Plain English:** Of all the real events, the fraction the detector caught. "Did we miss anything?"
- **Naija analogy:** Of the 10 thieves who came this year, how many did the guard catch?
- **Example:** Musa: 9 ÷ 10 = 0.90. Sunlit control chart: 3 ÷ 3 = 1.00.

### 📟 Precision
- **Plain English:** Of all the alarms, the fraction that were real. "When it pages me, is it real?"
- **Naija analogy:** Of all the times Musa shouted "Thief!", how many were actual thieves?
- **Example:** Musa: 9 ÷ 200 = 0.045. All-hours control chart: 0.06.

### 🙅🏾 Accuracy (and why it lies)
- **Plain English:** The fraction of all readings a detector got "right". Useless when real events are rare.
- **Naija analogy:** Ade the guard sleeps all night and is "97% accurate", because most nights there's no thief.
- **Example:** A detector that never fires scores 99.87% on last week's 4,706 readings.

### 🐘 Rare events (class imbalance)
- **Plain English:** When the thing you're hunting is tiny compared with everything else, so "always say no" looks great.
- **Naija analogy:** Looking for 6 fake ₦1,000 notes in a bag of 4,706 genuine ones.
- **Example:** 6 events in 4,706 readings.

### ⚖️ Recall-first vs precision-first
- **Plain English:** Deciding which number matters more for a system, based on what a miss costs vs what a false alarm costs.
- **Naija analogy:** A smoke alarm should be recall-first (better a false alarm than a burnt house). A car alarm that screams at every keke is a precision problem.
- **Example:** Battery and power: recall first. Rain-fade dashboards: precision first.

### 😩 Alarm fatigue
- **Plain English:** When alarms fire so often for nothing that people stop paying attention to them, including the real ones.
- **Naija analogy:** The estate gateman who has heard Musa shout 200 times now just turns over and sleeps.
- **Example:** 92 pointless eclipse pages a year from the all-hours control chart.

### ⏱️ Shift hours (the cost of false alarms)
- **Plain English:** False alarms × minutes to check each one, turned into engineer hours. The number a manager can decide on.
- **Naija analogy:** Counting how much fuel the generator wasted while nobody was home.
- **Example:** 46 per season × 2 seasons × 20 minutes ≈ 31 hours a year, about 4 shifts.

## 🧰 Detector words

### 🌞 Conditioning on a known cause
- **Plain English:** Only judging readings where a known, normal cause is absent, instead of widening the alarm band for everyone.
- **Naija analogy:** You don't call an electrician when the lights go off during a scheduled NEPA load-shedding.
- **Example:** Adding `eclipse_flag == 0` took the control chart from 46 false alarms to 0.

### 🐢 Detection delay
- **Plain English:** How long after an event starts the detector first raises a flag.
- **Naija analogy:** Noticing your tyre is flat only after you've driven 2 km on the rim.
- **Example:** The 90-day fade-rate alarm flagged EV06 31 days after the knee.

### 📐 Slope alarm (fade-rate alarm)
- **Plain English:** An alarm on how **fast** something is changing, not on its value. It catches drifts that never cross a fixed line.
- **Naija analogy:** Your fuel gauge says half a tank, but it was full an hour ago. The level is fine; the speed of dropping is the problem.
- **Example:** Fade faster than −3 Ah a year → alarm. It catches EV06 with zero false alarms.

### 🌧️ Unusual ≠ anomaly
- **Plain English:** A reading can be statistically rare yet perfectly explained by known physics. Not everything rare is a fault.
- **Naija analogy:** Heavy traffic on Third Mainland Bridge at 6 p.m. on a Friday is unusual compared with 3 a.m., but nobody calls it an emergency.
- **Example:** Rain fade drops C/N below the naive line, but only 12 of the 18 flagged hours were real outages.
