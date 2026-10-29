# W6D3 Instructor Notes: Project Clinic and Demo Day

> **The one idea for today:** *a tool only counts when its owner can use it and believe it.* Today every participant shows, in five minutes, a tool that runs on the training server, tested honestly against a simple baseline, ending in four sentences their unit head can repeat. Nobody learns a new method today. Your job is to run a calm clinic, a tight demo hour, and a warm celebration.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours: 10 min welcome · 30 min clinic · 60 min demos · 20 min wrap-up |
| **Participants leave having** | presented their project in 5 minutes, received peer feedback, handed in (or fixed the last gaps in) their report, and celebrated finishing |
| **Covers (original)** | The capstone brief (`Time-series/module-project/time-series-project.md`): Stage 4 deployment, the deliverables list (report, AI-use note, 5-minute demo) and the 100-point rubric |
| **Final-project checkpoint** | 🎤 **Demo day:** working tool, 2–4 page report, 5-minute demo |
| **Files you need open** | animated slides, `W6D3-solution.ipynb`, the requirements PDF (`week-6/final-project/`), a timer, the **peer scoring sheets** printed (2 per presenter is plenty) |

## The week before: checklist

<ul class="check">
<li><b>Book the training server</b> for demo time. Server access is rostered (at most 5 participants at once), so agree a demo order and who logs in when. A shared presenter laptop that already has the VPN and the server bookmarks saves the most time.</li>
<li>Send the <b>demo order</b> and the <b>5-minute template</b> (slide 14) to participants. Ask them to rehearse once with a timer.</li>
<li>Invite the <b>unit heads</b> with the time of their participant's demo. They don't need to stay for all of it.</li>
<li>Print the <b>peer scoring sheet</b> (<code>2-exercise/demo-day/W6D3-peer-scoring-sheet.pdf</code>) and share the <b>final report template</b> (<code>2-exercise/demo-day/W6D3-final-report-template.pdf</code>).</li>
<li>Check with Publica how <b>certificates</b> are handled (printed for the day, or sent after). Have the list of names ready.</li>
<li>Run the <b>solution</b> notebook top to bottom: <b>12 of 12</b> ✅ (under a minute).</li>
<li>Decide the room plan: <b>one room</b> if 10 or fewer present; <b>two rooms</b> (you plus a co-assessor) if more. See "Running the demos".</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Welcome** | The MC and the uncle; 18 days in one picture; the stages; the rubric; what costs marks | 1–7 |
| 0:10 | **Clinic** | Four help stations; the self-check notebook; Ada's draft as the warm-up | 8–12 |
| 0:40 | **Demos** | 5 minutes + 1 question each, timer on screen; peers fill in the scoring sheet | 13–19 (template on screen between demos) |
| 1:40 | **Celebrate** | Certificates, photo, applause | 20 |
| 1:50 | **What next + close** | Keep it running, hand it over, the toolkit, better data | 21–22 |

**If time is tight:** skip slide 12 (Ada's draft) and slide 16 (extra worked examples). Never shorten the demos: move the clinic earlier instead.

## Explain it like this (in plain English)

- **Why a demo at all?** A tool nobody sees is a tool nobody uses. Five minutes forces the point out: what it does, whether it works, what to do next.
- **The six beats** (slide 14): problem 0:45 · data 0:45 · method 0:45 · honest test 1:00 · the tool live 1:00 · recommendation 0:45. That adds up to exactly 5:00. The honest test and the live tool get a full minute because they carry the most marks (honest evaluation 25, deployment 15).
- **The 4 sentences:** Situation, Observation (one number), Implication, Recommendation. It's the same "4-sentence finding" from W2D3, now aimed at a decision.
- **"Not penalised":** a model that loses to the simple baseline is fine if the comparison is fair and the report recommends the simpler method. We did exactly that in W5D1 (the chart beat the forest) and W6D1 (the rate forecast and naive beat the regression).
- **The self-check notebook** is a reviewer, not a lesson: six small functions that catch the problems the rubric penalises. Participants rehearse on Ada's draft (synthetic data), then run Part E on the training server with their real data.
- **The automatic leak test** (slide 11): for several weeks it hides that week's answer and everything after it, rebuilds the feature, and checks whether the value changed. If it changed, the feature needed information nobody had yet. It's the W4D3/W5D3 question, asked by the computer.

## The numbers (computed from the data)

**The rehearsal (Ada's draft).** Ada's export is the real `ops_tickets_weekly.csv` (104 weeks) with two planted problems: week **16 Jun 2025** exported twice, and week **10 Mar 2025** missing. So it still has 104 rows, but one is a repeat and one week is a hole.

- Interpolating the lost week gives **50** tickets, exactly between its neighbours (**48** and **52**), which is also the true value in the original file. Filling with 0 would invent a week with no faults and drag every forecast down.
- **Leak test on six suspects:** `shift(1)` ✅, `shift(52)` ✅, this week's terminal count ✅; `shift(-1)` 🚨, a centred 4-week mean 🚨, and `rolling(4).mean()` without a shift 🚨 (it includes the very week being forecast). `rolling(4).mean().shift(1)` passes.
- **Ada's random split** fails the assert: her training weeks reach **22 Dec 2025** while her test starts **10 Jun 2024**.
- **Split by time** at 3 Nov 2025: **96** training weeks, **8** test weeks.
- **Comparison table** (same 8 weeks, MAE): rate seasonal naive **2.24**, naive **11.25**, seasonal naive **15.25**. These match Week 5 Day 2.
- **Ada's ±3 "90%" band** caught **6 of 8** test weeks (75%): too narrow for a 90% claim.
- **The honest band** (W5D3's recipe): the 90th-percentile miss of **296** past 8-week forecasts is **±7.0** tickets, and it caught **8 of 8**.
- **The scheduled report** writes `ticket-report-2025-12-22.png` and `.txt`: *"Week of 29 Dec 2025: about 65 tickets, plausibly 58 to 71 (90% band from 52 past one-week forecasts)."*

**The worked examples on slides 15–16** (from the shared Week 5–6 modules, the same code as those days):

| Example | The numbers |
|---|---|
| Tickets (W6D1 backtest) | From **45** starting weeks, 8 weeks ahead: rate seasonal naive MAE **3.18**, naive **6.20**. One week ahead (52 starting weeks) they tie: naive **3.19**, rate **3.29**. On the code book's 6 folds naive beats the regression **5 of 6** (mean **3.13** vs **4.01**). |
| Battery (W6D2) | Daily capacity first dipped below 80% on **14 May 2025**, the 30-day mean crossed on **20 Jun 2025**, and the last day at or above 80% was **24 Jul 2025**: a **72-day** window. The 3-year straight-line call said **1 May 2025**, 13 days before the first dip, with **499 days** of warning. |
| Detector (W5D1) | Held-out months: both the chart and the forest caught **2 of 2** events; the chart raised **1** false alarm, the forest **25**. |

## Running the clinic (30 minutes)

Put a sign on four tables. Staff each one with yourself, a co-trainer, or a strong participant who's already finished.

| Station | Who should go | What the helper does |
|---|---|---|
| 🔎 **1. Data & leaks** | Anyone unsure about gaps, duplicates, time zones or features | Run `hygiene()` and `leak_test()` on their features (on the training server). Make sure they've **written down** every fix |
| ⚖️ **2. Honest test** | Anyone without a baseline, an assert, or a coverage / spread number | Check the split assert, that the baseline uses the same period and scorer, and that a band's coverage is measured on held-out data |
| 🚀 **3. Deployment** | Anyone whose tool only runs on a laptop | Get it running on the server: a scheduled report (cron) is often faster to rescue than a dashboard. Check the README |
| 🗣️ **4. The story** | Everyone, if nothing else is broken | Time a run-through. Read their 4 sentences aloud. Ask the uncle's question: "in one sentence, what does it do?" |

- **Fast finishers / everything done:** Parts A–D of the notebook (Ada's draft), then station 4.
- **15 minutes per station**, then rotate or rehearse with a partner.
- Remind the room twice: **real data stays on NIGCOMSAT systems.** The Colab notebook only ever touches the synthetic course file.

## Running the demos (60 minutes)

- **Timing:** 5 minutes + 1 question = 6 minutes, plus about 1 minute to swap. That's **8 presenters per hour per room.** For 9–16 participants use **two rooms** (you and a co-assessor, both with the same scoring sheet). For more than 16, schedule a second demo slot.
- **The timer is the MC.** Put a big countdown on screen or hold up cards: **1 minute left**, then **time**. At 5:00 say warmly, "Your recommendation, please," and let them finish that sentence only.
- **Order:** start with a confident presenter, put anyone with a unit head present at a time the unit head can attend, and end on a strong demo.
- **The one question:** if nobody asks, ask the uncle's question or "What would make you stop trusting this tool?"
- **Between demos,** leave slide 14 (the template) on screen.
- **Peers** fill in one scoring sheet per presenter: six rubric lines, a quick score, two stars and a wish. Collect the sheets and give each presenter theirs at the end. **Peer scores are feedback, not grades.**

## How to score (your mark is the official one)

Score the demo **and** the report + repository against the six rubric lines from the requirements PDF. A quick guide:

| Rubric line | Full marks look like | Half marks look like | Points |
|---|---|---|---|
| Problem framing and data | Named process with an owner, unit head's email attached, real data described (source, span, cadence), nothing restricted committed | "Satellite data" with no named process, or no agreement attached | 15 |
| Understanding the series | DatetimeIndex, declared frequency, one time zone, gaps/duplicates handled **and explained**, honest chart with the threshold, period from a correlogram + decomposition | Clean data but no explanation of what was fixed, or no threshold on the chart | 15 |
| Method | Suits the brief (see the requirements PDF, Stage 2); every feature passes the leak test | Right idea but a feature that peeks ahead, or a remaining-life call with no window | 20 |
| Honest evaluation | Split by time with assert + embargo; baseline on the same period with the same scorer; spread / repeated calls / coverage reported; the conclusion follows the evidence (including "the simple method wins") | A baseline but on a different period, or no spread / coverage | 25 |
| Deployment | Runs on the training server (dashboard or scheduled report); README says how | Works, but only on a laptop (**at most half**, by the original grading notes) | 15 |
| Communication and AI use | 4 sentences with a number, limitations stated, readable by the unit head, AI-use note, demo delivered on time | Demo over time or no limitations; AI-use note missing | 10 |

**Automatic penalties** (from the requirements PDF and the original grading notes): a random train/test split · a feature that uses future information · an accuracy figure for rare-event detection · a degradation estimate as a single date with no window or assumptions · **committed restricted data** (a serious failure, reported to the programme lead regardless of the rest).

**Never penalise** a model that loses to the baseline when the comparison is fair and the report recommends the simpler method. The original grading notes say this explicitly. Extra credit, at your discretion, for a tool the unit actually adopts.

## Notebook answers (solution: 12 of 12)

| Task | Answer | What the check shows |
|---|---|---|
| A1 | `FREQ = "W-MON"` | the hygiene report with two ⚠️ lines |
| A2 | `n_duplicates = 1`, `n_missing = 1` | one repeated week, one lost week |
| A3 | `GAP_FILL = "interpolate"` | 104 clean weeks; the lost week becomes 50 (between 48 and 52) |
| A4 | `SHIFT = 1` | the 4-week mean now passes the leak test |
| B1 | `CUT = "2025-11-03"` | 96 training weeks, 8 test weeks, assert passed |
| B2 | `TERMINALS = train["active_vsat_terminals"]` | rate seasonal naive 2.24 < naive 11.25 < seasonal naive 15.25 |
| B3 | `cov_ada = coverage(test_y, fc - 3, fc + 3)` | 0.75: 6 of 8 weeks |
| B4 | `Q = 0.9` | ±7.0 tickets, 8 of 8 weeks |
| C1 | `STAMP_FORMAT = "%Y-%m-%d"` | two files dated 2025-12-22, "about 65 tickets, plausibly 58 to 71" |
| C2 | `CRON_TIME = "0 7 * * *"` | the crontab line |
| D1 | any 4 sentences (4+ words each) with a number in the Observation | the printed recommendation |
| D2 | any 3 short sentences (3+ words each) | — |

D1 and D2 accept any sensible text: the check only makes sure all parts are there and the Observation carries a number. Read a few aloud at station 4.

## Troubleshooting on the day

| Problem | What to do |
|---|---|
| **The dashboard won't load** mid-demo (VPN, server slot, port) | Say "Let me show you the screenshot," switch to it, and keep the clock running. Fix it afterwards. Score deployment from the README and a re-run after the session. Don't let one failure eat the next presenter's time. |
| **Someone has no real data yet** (the unit head never replied, or access is still pending) | They present on the synthetic course files **as a rehearsal**, and say plainly what's missing. By the original grading notes, a synthetic-only submission doesn't meet the brief **unless** the unit head confirms in writing that no real data could be made available. Agree a deadline with them and their unit head. |
| **The unit head can't attend** | Record the demo (screen + voice) if the participant agrees, or send the 4 sentences and the report by email. Ask the unit head to reply with one line of feedback. |
| **A demo shows raw restricted data** to outsiders | Ask them to switch to the chart or the summary. Don't dwell on it in front of the room; talk to them privately afterwards. |
| **A demo runs long** | At 5:00: "Your recommendation, please." One sentence, then applause. |
| **Nobody asks a question** | Ask: "What would make you stop trusting this tool?" |
| **A participant's model lost to the baseline and they're embarrassed** | Say it out loud: "That's the result we teach. You tested it fairly and you're recommending the simpler method. Full marks for honesty." |
| **Notebook: `NameError: hygiene`** | They skipped the ▶️ toolkit cell. Run STEP 0 and the toolkit cell. |
| **Notebook: `ValueError: cannot reindex on an axis with duplicate labels`** on their own data | `.asfreq()` before dropping duplicates. Drop duplicates first, then `.asfreq()`. |
| **Notebook: Part E does nothing** | Correct: it only runs on the training server once `PROJECT_CSV` is set. In Colab it skips on purpose. |

## Extras in this folder

| File | What it is |
|---|---|
| `2-exercise/demo-day/W6D3-peer-scoring-sheet.pdf` (+ `.md`) | One sheet per presenter (two copies included; print as many as you need): the six rubric lines with "what to look for", a score box, two stars and a wish. The last page is your tally for the whole cohort |
| `2-exercise/demo-day/W6D3-final-report-template.pdf` (+ `.md`) | The 2–4 page report skeleton: each section mapped to its rubric line, the evaluation table, the 4 sentences, 3 limitations, the AI-use note and a pre-submission box |

## After the session

<ul class="check">
<li>Collect any late reports and repository links; give a deadline (e.g. one week) to anyone who presented on synthetic data or a laptop-only tool.</li>
<li>Return the peer scoring sheets to each presenter.</li>
<li>Email each unit head their participant's 4 sentences and report.</li>
<li>Note which tools units plan to keep using: that's the course's real result.</li>
</ul>
