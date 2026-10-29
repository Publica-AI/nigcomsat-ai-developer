# Final Report Template

Copy this into your own file (Markdown or Word, then PDF). Keep it to **2–4 pages**. Replace the hints in each section with your own words. The rubric line each section earns is shown in **[brackets]**.

## Title: one line that states the finding

> e.g. *"The battery-health review can see the 80% floor coming about 4 months ahead"*

**Name · Unit · Brief (A–E) · Date of the unit head's agreement**

## 1. The process and the agreement **[Problem framing and data · 15]**

| | Your answer |
|---|---|
| **Unit** | |
| **Named process** (with its owner) | |
| **Who uses the tool** | |
| **The question it answers** | |
| **Unit head's agreement** | attach the email (appendix) |
| **Adapted brief?** | what you changed, and that your unit head agreed |

## 2. The data **[Problem framing and data · Understanding the series]**

| | Your answer |
|---|---|
| **Source system / export** | |
| **Span** (from – to) and **cadence** | |
| **Time zone** | |
| **Problems found** (gaps, duplicates, sampling changes) | |
| **What you did about each one** | |
| **Seasonal period** (from the correlogram) | |
| **Restrictions** | what is restricted, and how you kept it on NIGCOMSAT systems |

Paste **one honest chart**: sensible axis, the operational threshold drawn, a title that states the finding.

## 3. The method **[Method · 20]**

- What it is, in two or three sentences, and **why it suits this process**.
- Every feature, and the result of its **leak test**.
- The settings, and **when** you fixed them (before the test).

## 4. The honest test **[Honest evaluation · 25]**

- **Split:** train from ____ to ____, test from ____ to ____, embargo ____ (= the longest feature window). The `assert` passed.
- **Scorer and rules, written first:** e.g. event-level precision and recall with a ±1 h window, or MAE in units per week.

| Method | Period | Score | Spread / coverage / repeated calls |
|---|---|---|---|
| Simple baseline | | | |
| Your method | | | |

- Detection: event-level precision and recall, **never accuracy**.
- Forecasting: the walk-forward spread across folds, and the coverage of your band on held-out data.
- Remaining life: the call repeated from several starting points, with the warning time each one gave. A **window**, never a single date.
- If the simple method won or tied: say so, and recommend it.

## 5. The tool **[Deployment · 15]**

- Streamlit dashboard **or** scheduled report: what it shows (series, threshold, flags or forecast with its range, a plain-language paragraph).
- Where it runs on the training server, its URL or its schedule (e.g. cron `0 7 * * *`).
- How to run it: see the `README.md` in the repository. No raw data in the repository.

## 6. Recommendation: four sentences **[Communication · 10]**

1. **Situation:**
2. **Observation** (one number):
3. **Implication:**
4. **Recommendation:**

## 7. Limitations

- **What will it miss?**
- **How late will it be, or how far ahead can it see?**
- **What did you assume was normal?** (the reference / training period)

## 8. AI-use note (one paragraph)

What you used an AI assistant for, how you checked its output, and how you kept restricted data out of it (e.g. "I described the column names and shape; I never pasted rows").

## Appendix

- The unit head's email
- The repository link and the `requirements.txt`

<div class="box warn" markdown="1">
**Before you submit:** no random split · no feature that uses the future · no accuracy figure for rare events · no remaining-life date without a window · **no real NIGCOMSAT data in the repository**.
</div>
