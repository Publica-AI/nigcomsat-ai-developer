# W2D3 Glossary: today's new words

New words from the lab, the quiz and the final-project kickoff: plain English, a Naija way to remember them, and an example.

## 🔋 Battery words (from the lab)

### 🌗 Eclipse season
- **Plain English:** The weeks when Earth's shadow crosses the satellite's orbit for a while each day, so it runs on battery. It happens twice a year.
- **Naija analogy:** NEPA's “scheduled outage” season, but it comes every March and September like clockwork.
- **Example:** `eclipse_minutes` rises from 0 to 72 minutes a day around each equinox.

### 🌍 Equinox
- **Plain English:** The two days a year (around 21 March and 23 September) when day and night are equal. Eclipse seasons are centred on them.
- **Naija analogy:** The two fixed “owambe Saturdays” of the satellite calendar: you can plan for them years ahead.
- **Example:** The seasonal bumps in the lab land in March and September.

### 🔋 Capacity (amp-hours, Ah)
- **Plain English:** How much charge a battery can still hold. It shrinks as the battery ages.
- **Naija analogy:** Your old phone that used to last all day and now dies before lunch.
- **Example:** `est_capacity_ah` falls from 103.3 Ah to 96.6 Ah over three years.

### 🪫 Depth of discharge
- **Plain English:** How far the battery was drained, as a percentage of what it holds.
- **Naija analogy:** How low your inverter battery went during last night's blackout.
- **Example:** Under 1% on normal days, up to about 22% on the deepest eclipse days.

### ⚡ End-of-discharge voltage
- **Plain English:** The battery's voltage at the end of a drain. Deeper drains and older batteries both pull it down.
- **Naija analogy:** How weak the fan is spinning just before the inverter gives up.
- **Example:** `eod_voltage_v`: smoothing it removes the eclipse dips and leaves the ageing.

### 🚨 Alert line (threshold)
- **Plain English:** A value that, once crossed, means someone should act. Real ones are set by engineers.
- **Naija analogy:** The fuel light on your car's dashboard.
- **Example:** The lab's 97 Ah line is **made up for practice**.

## 🔬 Investigation words

### 🔎 Investigation
- **Plain English:** Answering one question with data, from loading the file to writing the conclusion.
- **Naija analogy:** A mechanic's full diagnosis, not just “e don spoil”.
- **Example:** “Is our battery getting tired?”: load → profile → plot → smooth → decompose → ACF → finding.

### 📝 Finding (4-sentence)
- **Plain English:** A short write-up in four sentences: Situation, Observation, Implication, Recommendation.
- **Naija analogy:** How a good doctor explains: what's happening, what the test shows, what it means, what to do.
- **Example:** “Weekends average 3.4 tickets a day vs 7.1 on weekdays” is an Observation.

### 👯 Twin files
- **Plain English:** Two data files with the **same name** but different contents, in different folders.
- **Naija analogy:** Two people called “Emeka Okafor” in the same office: check the ID before you transfer money!
- **Example:** `battery_health_daily.csv` in week-03 (clean) vs week-04 (planted faults).

## 🎯 Final-project words

### 🎯 Brief
- **Plain English:** One of the five project types you can choose (A–E), each with its own operational question.
- **Naija analogy:** The topic the lecturer approves for your final-year project.
- **Example:** Brief B: “When will the battery be too tired to carry us through eclipse?”

### 🏭 Named process
- **Plain English:** A specific, real task your unit does regularly, with an owner. Not a general topic.
- **Naija analogy:** Not “food”: “Mama's Saturday jollof for the street party”.
- **Example:** “The weekly battery-health review on the bus subsystem.”

### 🧑🏾‍💼 Process owner
- **Plain English:** The person responsible for that process, who will use or approve your tool.
- **Naija analogy:** The oga at the top of that particular desk.
- **Example:** The shift lead who runs NOC fault escalation.

### 🏢 Unit head
- **Plain English:** The head of your department. They agree your project's scope by email.
- **Naija analogy:** Your HOD signing your project approval form.
- **Example:** Their reply email goes into your final submission.

### 📏 Baseline
- **Plain English:** The simplest reasonable method, the one every fancier method must beat on the same test.
- **Naija analogy:** Grandma's weather forecast: “tomorrow will be like today”. Beat her or go home. 👵🏾
- **Example:** “Same weekday last week” as a forecast for throughput.

### 🚩 Checkpoint
- **Plain English:** A short progress check at a fixed point in the course.
- **Naija analogy:** Police checkpoints on the expressway, but these ones help you. 😄
- **Example:** Week 3 · Day 3: bring your unit head's reply and your profiled data.

### 🔒 Restricted data
- **Plain English:** Real NIGCOMSAT data that must not leave NIGCOMSAT systems or go into outside tools without permission.
- **Naija analogy:** Your ATM PIN: useful, but you don't paste it into WhatsApp.
- **Example:** Real telemetry, RF records and network logs. Course data is synthetic and safe.

### 📦 Raw data
- **Plain English:** The original export from a system, before you clean or summarise it.
- **Naija analogy:** Unpeeled yam straight from the market.
- **Example:** Never commit raw NIGCOMSAT exports to GitHub: commit only your code.

### 🗂️ Repository (repo)
- **Plain English:** A project folder tracked by Git, often stored on GitHub, holding your code and its history.
- **Naija analogy:** Your project file at the registry, with every version stamped and dated.
- **Example:** Your final project's code, `requirements.txt` and `README.md` live in a repo.
