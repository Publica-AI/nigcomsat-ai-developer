# W6D3 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🎤 Showing your work

### 🎤 Demo
- **Plain English:** A short, live showing of your tool to the people who will use it: what problem, what data, what method, how you tested it, the tool running, and what to do next.
- **Naija analogy:** The owambe MC gives the groom's friends five minutes. When the time is up, the DJ takes over, ready or not.
- **Example:** Six beats in 5:00: problem 0:45, data 0:45, method 0:45, honest test 1:00, the tool live 1:00, recommendation 0:45.

### 📋 Rubric
- **Plain English:** The marking scheme: the list of what earns points and how many. Ours has six lines adding up to 100.
- **Naija analogy:** The WAEC marking scheme: the examiner isn't guessing, every mark has a reason.
- **Example:** Honest evaluation is the biggest line: 25 of 100 points.

### 🗣️ Recommendation (the 4 sentences)
- **Plain English:** The ending of your report and demo: **S**ituation, **O**bservation (with one number), **I**mplication, **R**ecommendation (what to do, with which tool).
- **Naija analogy:** The uncle in the front row: "Tell us in one sentence: what does it do, and why should we care?" Four sentences is your allowance.
- **Example:** "Use the rate forecast for the monthly roster, keep 'same as last week' for next week, and re-run the backtest every quarter."

### 🧭 Limitation
- **Plain English:** An honest statement of where your tool stops working: what it will miss, how late it is (or how far ahead it can see), and what you assumed was normal.
- **Naija analogy:** The mechanic who says "this one go hold till December, but no carry am go Kano." You trust him more, not less.
- **Example:** "Its 90% band is about ±7 tickets a week, and it assumes the rainy-season pattern repeats."

### ⭐ Two stars and a wish
- **Plain English:** A way to give feedback on someone's demo: two things that were good, one thing that would make it better.
- **Naija analogy:** How a good aunty corrects you at a party: praise first, then "but next time, my dear…".
- **Example:** The peer scoring sheet has a box for each star and the wish.

## 🧑🏾‍⚕️ Checking your own work

### 🧼 Series hygiene
- **Plain English:** The basic health check of a time series before any analysis: a time index, sorted, no repeated timestamps, no holes (or holes explained), a declared frequency, and a known time zone.
- **Naija analogy:** Washing your hands before you cook: nobody claps for it, but skip it and everybody gets sick.
- **Example:** Ada's export had one week exported twice and one week that never arrived.

### 🙈 Automatic leak test
- **Plain English:** A computer check of "could I have known this feature in time?": hide this week's answer and the whole future, rebuild the feature, and see if it changes. If it changes, it leaked.
- **Naija analogy:** Collecting the phones before the exam starts. If your answer changes when the phones are gone, it wasn't your answer.
- **Example:** `shift(1)` passes; `shift(-1)`, a centred window and `rolling(4).mean()` without a shift all fail.

### 🧹 Interpolation (filling a gap)
- **Plain English:** Filling a missing value with something between its neighbours, usually the straight-line average. It's an assumption, so you must say you did it.
- **Naija analogy:** You missed Tuesday's class, so you copy the notes from Monday and Wednesday and guess what came in between.
- **Example:** Ada's lost week (10 Mar 2025) became 50 tickets, between 48 and 52. Filling it with 0 would invent a week with no faults.

## 🚀 Putting it to work

### 🚀 Deployment
- **Plain English:** Putting your tool where its users can actually use it, every day, without you. For this course: on the **training server**, as a dashboard or a scheduled report.
- **Naija analogy:** Building the borehole is one thing. Deployment is when the whole street can fetch water without calling you.
- **Example:** A tool that only runs on your laptop earns at most half of the deployment marks.

### 🗓️ Scheduled report
- **Plain English:** A script the server runs on a timetable, which saves a dated chart and a short summary to a shared folder.
- **Naija analogy:** The newspaper vendor who drops the paper at your gate every morning at 7, whether you remember to ask or not.
- **Example:** `ticket-report-2025-12-22.png` and `ticket-report-2025-12-22.txt`: "about 65 tickets, plausibly 58 to 71".

### ⏰ Cron
- **Plain English:** The Linux timetable for scheduled jobs. A line has five time fields (minute, hour, day of month, month, day of week) and then the command. `*` means "every".
- **Naija analogy:** The church bell that rings at 6 a.m. every day. Nobody presses it; it's on the timetable.
- **Example:** `0 7 * * *` = 07:00, every day.

### 📊 Streamlit dashboard
- **Plain English:** A small web page written in Python (`streamlit run app.py`) that your unit opens in a browser to see the series, the threshold, the flags or forecast with its range, and a plain-language summary.
- **Naija analogy:** The scoreboard at the stadium: everybody looks at the same screen, nobody needs to read the referee's notebook.
- **Example:** Today's notebook writes a starter `app.py` for you to finish on the server.

### 📘 README and requirements.txt
- **Plain English:** Two files every project repository needs. `README.md` says what the tool does and how to run it; `requirements.txt` lists the Python packages it needs.
- **Naija analogy:** The manual and the parts list that come with the new generator. Without them, only the person who installed it can start it.
- **Example:** The README states where the tool runs on the training server and its URL or schedule.

### 🤖 AI-use note
- **Plain English:** One paragraph in your report saying what you used an AI assistant for, how you checked its output, and how you kept restricted data out of it.
- **Naija analogy:** Declaring what's in your luggage at the airport: honest and short, and everyone relaxes.
- **Example:** "I described the column names and the shape of the export; I never pasted rows. I tested every function on the course data first."
