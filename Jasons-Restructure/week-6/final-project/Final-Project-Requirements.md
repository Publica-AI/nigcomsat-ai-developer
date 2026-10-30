# Final Project Requirements

<div class="box good" markdown="1">
**In one sentence:** pick one real problem in **your own unit**, use **real NIGCOMSAT data** to watch it or forecast it, test your method honestly against a simple baseline, and hand your unit a working tool they can open.
</div>

This is an **individual** project. It follows the original Publica Academy capstone brief (`Time-series/module-project/`) and keeps its rubric. This document breaks that brief into simple steps, checklists and templates.

---

## 1. The journey at a glance

| Stage | What you do | Skills from |
|---|---|---|
| **0. Choose** | Pick one brief + one named process in your unit. Get your unit head's OK by email | Week 2 |
| **1. Understand** | Load, profile and plot your series; find its season | Weeks 1–2 |
| **2. Build** | Build the method your brief needs | Weeks 3–6 |
| **3. Test honestly** | Split by time, compare with a simple baseline, same scorer | Weeks 4–6 |
| **4. Deploy** | A Streamlit dashboard **or** a scheduled report your unit can use | Week 6 |
| **5. Present** | 2–4 page report + 5-minute demo | Week 6 Day 3 |

### Checkpoints during the course

| When | Checkpoint | Bring |
|---|---|---|
| **Week 2 · Day 3** | 🎯 Brief chosen | Your brief, the named process, the draft email to your unit head |
| **Week 3 · Day 3** | 📥 Data in hand | Unit head's reply, your data loaded and profiled (rows, range, gaps, duplicates) |
| **Week 4 · Day 3** | 🛠️ Method drafted | First version of your detector / forecast / trend-to-threshold |
| **Week 5 · Day 3** | ⚖️ Honest test | Temporal split + baseline comparison table |
| **Week 6 · Day 3** | 🎤 Demo day | Working tool, report, 5-minute demo |

---

## 2. Choose ONE brief

| Brief | The question in plain words | Naija version | Skills |
|---|---|---|---|
| **A. Telemetry anomaly detection** | Which hours of subsystem telemetry are abnormal, and why? | “Which hours did the satellite behave strangely, and what was the cause?” | Weeks 1, 3, 4–5 |
| **B. Power and battery degradation** | When will battery (or solar array) health cross its operational limit? | “When will the battery be too tired to carry us through eclipse?” | Weeks 1, 3, 6 |
| **C. RF link-quality prediction** | Will link margin fall below threshold in the coming hours or days? | “Will the rain cut our signal tomorrow?” | Weeks 1, 4–5, 6 |
| **D. Carrier and capacity monitoring** | Is utilisation or throughput drifting, and when will capacity run short? | “When will the expressway be full?” | Weeks 1, 3, 6 |
| **E. Site-downtime prediction** | Which sites or regions are likely to go down, and how many tickets should the NOC expect? | “Which VSAT sites will give us wahala next week?” | Weeks 1, 4–5, 6 |

If your unit's process doesn't fit exactly, you may adapt a brief **with your unit head's agreement**. Say what you adapted in your report.

---

## 3. Data rules: read these twice

<div class="box bad" markdown="1">
**Rule 1: real data.** Use real, accessible NIGCOMSAT data that your unit produces and you are allowed to use. The synthetic course files are for practice only (exception: your unit head confirms in writing that no real data can be made available).

**Rule 2: real data stays inside NIGCOMSAT.** Google Colab runs on Google's servers. **Do not upload real NIGCOMSAT data to Colab or paste it into any AI tool** unless your unit head has agreed in writing. Develop on the **training server** or your work laptop.

**Rule 3: no raw data on GitHub.** Commit your **code**, never the data export. Load data from a path set in a config file or `.env`.
</div>

<ul class="check">
<li>I named a <b>specific process</b> with an owner (e.g. “weekly battery-health review on the bus subsystem”), not just “satellite data”.</li>
<li>My unit head agreed <b>by email</b> to the process, the data and who the tool is for. The email is in my submission.</li>
<li>I know which of my data is restricted, and I describe its <i>shape</i> to AI tools instead of pasting it.</li>
<li>My repository contains no raw NIGCOMSAT data.</li>
</ul>

---

## 4. What you must build: stage by stage

### Stage 1: Understand the series

<ul class="check">
<li>Loaded with a proper <code>DatetimeIndex</code>, a declared frequency (<code>.asfreq()</code>) and <b>one</b> time zone.</li>
<li>Profiled: rows, date range, gaps, duplicate timestamps, changes in sampling rate. I wrote what I found and what I did about it.</li>
<li>An honest plot: sensible axis, the <b>operational threshold drawn on the chart</b>, a title that states a finding.</li>
<li>Seasonal period found <b>from a correlogram</b> (not assumed), and used in a decomposition.</li>
</ul>

### Stage 2: Build the method

| Your brief | Minimum method |
|---|---|
| A. Anomaly / E. Site downtime (detection) | A statistical baseline (control chart, residual or CUSUM detector), **plus** a multivariate detector on engineered, trailing-only features if several channels are involved |
| B. Degradation / D. Capacity | A trend-to-threshold estimate giving a crossing date **and a window** (never a single day), with the assumptions stated |
| C. RF prediction / E. Ticket forecast | At least one baseline forecast (naive or seasonal naive) **plus** a regression with engineered features, **each with a prediction interval** |

<div class="box warn" markdown="1">
**The leak test, for every feature:** *“Could I have computed this at the moment the prediction was needed, using only what I knew then?”* If not, delete it. Trailing windows and positive shifts only.
</div>

### Stage 3: Test it honestly

<ul class="check">
<li>Split <b>by time</b>, never at random. An <code>assert</code> proves every training timestamp comes before every test timestamp.</li>
<li>An <b>embargo</b> at the split at least as long as my longest feature window.</li>
<li>Compared with the <b>simple baseline</b>, on the <b>same period</b>, with the <b>same scorer</b>.</li>
<li>Detection: <b>event-level precision and recall</b>, with my scoring rules written down first. <b>No accuracy figure.</b></li>
<li>Forecasting: a <b>walk-forward backtest</b> reporting the spread across folds, not just the average.</li>
<li>Degradation: the call repeated from <b>several starting points</b>, showing how the date and the warning time change.</li>
<li>Intervals: <b>coverage checked</b> on held-out data.</li>
<li>No labelled events? I said so, and agreed a substitute (maintenance log, ticket history) with my unit.</li>
</ul>

> ✅ **If the simple method wins, say so and recommend it.** That is a legitimate, respected result.

### Stage 4: Deploy it

Choose **one**:

| Option | What it is | Must show |
|---|---|---|
| **Streamlit dashboard** | A small web app your unit opens in a browser | the series, the threshold, current flags or the forecast with its range, a one-paragraph plain-language summary |
| **Scheduled report** | A script that runs daily (cron / Task Scheduler) and saves a dated chart + summary to a shared folder | the same content, refreshed automatically |

It must run on the **training server**. **Server access is rostered: at most 5 participants at a time.** Book your slot, build and test locally first, and use the server for deployment and final checks. A tool that runs only on your laptop earns at most half of the deployment marks.

---

## 5. What you hand in

<ul class="check">
<li><b>Repository</b> (or folder): code, <code>requirements.txt</code>, <code>README.md</code> explaining how to run it. <b>No raw data.</b></li>
<li><b>The running tool</b> on the training server: its URL or schedule written in the README.</li>
<li><b>Report</b> (2–4 pages, Markdown or PDF): unit, process, brief and the unit head's agreement; the data (source, span, cadence, quality issues and fixes); the method and why it fits; the evaluation table against the baseline, with rules stated; a <b>4-sentence recommendation</b>; limitations.</li>
<li><b>AI-use note</b> (one paragraph): what you used AI for, and how you checked it without exposing restricted data.</li>
<li><b>5-minute demo</b> to the cohort and, if possible, your unit head.</li>
</ul>

---

## 6. How it's graded (100 points)

| Criterion | What earns the points | Points |
|---|---|---|
| Problem framing and data | Unit, named process, one brief, unit head's agreement; real data described (source, span, cadence); restrictions respected; no raw data committed | **15** |
| Understanding the series | DatetimeIndex, declared frequency, one time zone; gaps and duplicates handled; honest plot with threshold; period from a correlogram + decomposition | **15** |
| Method | Suits the brief; every feature passes the leak test | **20** |
| Honest evaluation | Temporal split with assert + embargo; same period, same scorer vs the baseline; spread / repeated calls / coverage reported; conclusion follows the evidence | **25** |
| Deployment | Dashboard or scheduled report running on the training server; README explains how to run it | **15** |
| Communication and AI use | 4-sentence recommendation, limitations stated, readable by the unit head; AI-use note; demo delivered | **10** |

<div class="box bad" markdown="1">
**Automatic penalties:** a random train/test split · any feature that uses future information · an accuracy figure for rare-event detection · a degradation estimate given as a single date with no window or assumptions · **committing restricted data** (treated as a serious failure and reported to the programme lead).

**Not penalised:** a model that loses to the simple baseline, as long as the comparison is fair and you recommend the simpler method.
</div>

---

## 7. Templates you can copy

### Email to your unit head

> **Subject:** Time-series training: final-project scope for approval
>
> Dear [Name],
>
> For my final project in the NIGCOMSAT time-series programme, I'd like to build a small monitoring tool for **[named process, e.g. the weekly battery-health review]**.
> - **Brief:** [A–E]
> - **Data I'd use:** [system/export], [date range], [cadence]. It stays on NIGCOMSAT systems; nothing is uploaded to outside tools.
> - **Who it's for:** [team / role]
> - **Output:** a [dashboard / daily report] on the training server.
>
> Could you confirm by replying to this email? Thank you.

### The 4-sentence recommendation

1. **Situation:** what the unit does today, and the problem.
2. **Observation:** what the data and your method showed (one number).
3. **Implication:** what it means for operations.
4. **Recommendation:** what the unit should do next, and with which tool.

### Limitations: answer these three

- **What will it miss?** (blind spots)
- **How late will it be?** (detection delay / forecast horizon)
- **What did you assume was normal?** (the training period)

---

## 8. Hardware and data-collection recommendations

Good models need good data. These recommendations are for **NIGCOMSAT units and IT/infrastructure teams** that want better data for this kind of work. Treat them as a menu: agree priorities and budget with your unit; some may already be in place.

### 8.1 For the course itself

| Item | Recommendation | Why |
|---|---|---|
| **Participant laptops** | Any laptop from the last ~6 years with **8 GB RAM** and **Google Chrome** | Colab does the computing; the laptop only shows the screen |
| **Internet** | Stable broadband, at least **~2 Mbps per participant**, plus a backup connection | Colab needs a live connection; disconnects lose memory |
| **Power** | UPS or inverter for the training room, projector and router | A NEPA cut shouldn't end a session 😅 |
| **Projector** | 1080p, HDMI; a clicker for the animated slides | The decks are designed for 16:9 |

### 8.2 The training server (for deployment)

| Item | Recommended minimum | Why |
|---|---|---|
| CPU / RAM | **16 vCPU, 64 GB RAM** | 5 concurrent users × (2 vCPU + 8 GB) plus headroom for dashboards |
| Storage | **1 TB SSD** (+ backup) | Years of hourly telemetry for many channels, plus model outputs |
| GPU | **Not needed** | Every method in this course is CPU-light |
| Software | Linux (Ubuntu LTS), Python 3.11+, JupyterHub, Streamlit, cron, Git | Development, dashboards and scheduled reports on one box |
| Access | Named user accounts, a booking roster, VPN for remote access | The rostered 5-user limit, plus security |
| Power | UPS + generator changeover | Scheduled reports must run every day |

### 8.3 Better data at the source: what to collect, and how

| Area | Recommendation | What it unlocks |
|---|---|---|
| **Time** | **NTP or GPS-disciplined time sync** on every logger, server and modem. Store all timestamps in **UTC** | Events from different systems line up; no hour-shift joins |
| **Telemetry archive** | Keep **full-rate** satellite telemetry (not just daily summaries) in a time-series database (e.g. TimescaleDB, InfluxDB), and keep **5+ years** | Briefs A and B: degradation forecasting needs long history |
| **Weather at earth stations** | A **rain gauge / weather station** logging at 1-minute resolution beside each Ka/Ku-band antenna | Brief C: separates **rain fade** from **equipment faults**, which gives you free labels |
| **Propagation** | A **Ka-band beacon receiver** measuring signal attenuation directly | Brief C: a clean, physical measure of rain impact |
| **Carrier monitoring** | A carrier-monitoring system / spectrum analyser logging **C/N, Eb/N0, EIRP** at fixed intervals | Briefs C and D: link quality and capacity trends |
| **VSAT sites** | **SNMP polling** of modem, BUC and LNB metrics every 1–5 minutes into the time-series database | Brief E: early warning before a site drops |
| **Site power** | **Power monitoring** at remote sites: grid vs generator vs battery, voltage, changeovers (smart meter / ATS logs) | Brief E: in Nigeria, power is a top cause of site downtime. Now you can prove it |
| **Store and forward** | Local buffering on site loggers so data isn't lost during link outages | No gaps exactly when things go wrong |
| **NOC tickets** | Structured fields: **site ID, cause code, open/close time (UTC), linked alarm ID** | Brief E: ticket counts become trustworthy labels |
| **Maintenance log** | A **machine-readable** log of interventions, faults and fixes (date, asset, what happened) | Briefs A and B: ground truth for scoring detectors |
| **Data contract** | Fixed export schema + data dictionary (column names with units, ISO dates, empty = missing), plus an automatic daily `quick_check` for gaps and duplicates | Every brief: no silent data problems |
| **Security** | Role-based access, audit logs, a clear list of what is restricted | Safe use of AI tools; compliance |

> 💡 **Quick wins (low cost, big impact):** time sync to UTC, a rain gauge at each Ka-band station, structured NOC cause codes, and a machine-readable maintenance log.

---

## 9. FAQ

**Can I use the course's synthetic data?** For practice, yes. For the submission, only if your unit head confirms in writing that no real data could be made available, and you include that email.

**My model is worse than the baseline. Did I fail?** No. Recommend the baseline, show the fair comparison, explain why. That's full marks for honesty.

**Can I work in Colab?** Yes, with the synthetic data while you learn. Real data stays on NIGCOMSAT systems unless your unit head agrees otherwise in writing.

**Can I use AI to write code?** Yes, but you must understand and verify every line, never paste restricted data, and describe how you used it in your AI-use note.

**We have no labelled faults.** Agree a substitute with your unit (maintenance log, ticket history, operator notes) and say so in the report.
