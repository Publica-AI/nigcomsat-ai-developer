# Project Kickoff Worksheet

Fill this in **today**, then send the email in section 5. Bring your unit head's reply to **Week 3 · Day 3**.
Full rules and grading: `week-6/final-project/Final-Project-Requirements.pdf`.

## 1. Pick ONE brief

| ✔ | Brief | The question in Naija words |
|---|---|---|
| ☐ | **A. Telemetry anomaly detection** | “Which hours did the satellite behave strangely, and what was the cause?” |
| ☐ | **B. Power and battery degradation** | “When will the battery be too tired to carry us through eclipse?” |
| ☐ | **C. RF link-quality prediction** | “Will the rain cut our signal tomorrow?” |
| ☐ | **D. Carrier and capacity monitoring** | “When will the expressway be full?” |
| ☐ | **E. Site-downtime prediction** | “Which VSAT sites will give us wahala next week?” |

Adapting a brief? Write what you'd change (needs your unit head's OK):

______________________________________________________________________________

## 2. Name the process (not a topic)

<div class="box bad" markdown="1">
❌ Too vague: “satellite data”, “network performance”, “something with AI”
</div>
<div class="box good" markdown="1">
✅ A named process with an owner: “the weekly battery-health review on the bus subsystem”, “VSAT site fault escalation in the NOC”
</div>

| | Your answer |
|---|---|
| **My unit** | |
| **The named process** | |
| **Who owns it** (name / role) | |
| **Who will use my tool** | |
| **The question my tool answers** | |

## 3. The data

| | Your answer |
|---|---|
| **Source system / export** | |
| **What one row is** (e.g. one hour of one channel) | |
| **Time span available** (how many months/years) | |
| **Cadence** (hourly / daily / weekly / monthly) | |
| **Time zone of the timestamps** (UTC or WAT?) | |
| **Known gaps or problems** | |
| **Labels / ground truth?** (maintenance log, tickets, operator notes) | |

## 4. Data restrictions: tick every box

<ul class="check">
<li>I know which parts of this data are <b>restricted</b>.</li>
<li>Real data stays on <b>NIGCOMSAT systems</b> (training server or work laptop). It does not go into Colab without written agreement.</li>
<li>I will commit <b>code only</b> to GitHub, never the raw export.</li>
<li>I will <b>describe the shape</b> of the data to AI tools, never paste it.</li>
</ul>

## 5. The email to your unit head

> **Subject:** Time-series training: final-project scope for approval
>
> Dear __________________,
>
> For my final project in the NIGCOMSAT time-series programme, I'd like to build a small monitoring tool for **__________________________________________** (named process).
> - **Brief:** ____ (A–E)
> - **Data I'd use:** __________________ (system/export), __________________ (span), ____________ (cadence). It stays on NIGCOMSAT systems; nothing is uploaded to outside tools.
> - **Who it's for:** __________________________________
> - **Output:** a ☐ dashboard / ☐ daily report on the training server.
>
> Could you confirm by replying to this email? Thank you.

<ul class="check">
<li>Email sent</li>
<li>Reply received (keep it: it goes into your final submission)</li>
</ul>

## 6. My checkpoint plan

| Checkpoint | When | What I'll bring | Done |
|---|---|---|---|
| 🎯 Brief chosen | Week 2 · Day 3 | This worksheet + the draft email | ☐ |
| 📥 Data in hand | Week 3 · Day 3 | Unit head's reply + data loaded and profiled | ☐ |
| 🛠️ Method drafted | Week 4 · Day 3 | First version of my detector / forecast / trend-to-threshold | ☐ |
| ⚖️ Honest test | Week 5 · Day 3 | Temporal split + comparison with a simple baseline | ☐ |
| 🎤 Demo day | Week 6 · Day 3 | Working tool, 2–4 page report, 5-minute demo | ☐ |

> 💡 **Three yes answers = a good project:** Is it in *my* unit? Can I get the *data*? Does someone *own* the process?
