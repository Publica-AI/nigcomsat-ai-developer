# Jason's Restructure: The Plan

**Course:** Time-Series Analysis, Anomaly Detection and Forecasting, for NIGCOMSAT engineers
**Format:** 6 weeks × 3 sessions = **18 sessions**, all hands-on in **Google Colab**
**Rule zero:** nothing in the original repo gets changed or deleted. Everything new lives in this folder and points back to the originals.

---

## 1. What is in the repo, in plain English

| Folder | What it is | Do we use it? |
|---|---|---|
| `Time-series/` | The course we are teaching: 4 "code books" (notebooks), 25 data files, 120 quiz questions and 1 capstone project | **Yes, this is the whole job** |
| `MODULE-01`, `MODULE-04`, `MODULE-05`, `shared/` | Other Publica modules on LLMs, chatbots and AI agents | No, those are a different track |

The `Time-series/` folders are numbered **week-03 to week-06** because they were cut from a longer 8-week programme. Weeks 1–2 of that programme (Python setup, data cleaning, data-privacy rules) are **not in this repo**. Our Week 1 has to cover that ground itself.

### What each original week teaches

| Original | Big question | Topics (from the quiz files) |
|---|---|---|
| Week 3 | *What does this series look like?* | structure · visualising · rolling windows · decomposition · autocorrelation |
| Week 4 | *When is a reading wrong?* (one sensor at a time) | alarm thresholds · control charts · residuals · drift/CUSUM · scoring a detector |
| Week 5 | *When is the combination wrong?* (machine learning) | scikit-learn · isolation forest & clustering · feature engineering · train/test by time |
| Week 6 | *What happens next, and when does it break?* | forecasting baselines · regression forecasts · prediction intervals · remaining useful life · backtesting |
| Capstone | Build one real tool on **real** NIGCOMSAT data for your own unit | — |

The full review, including every bug I found by running the notebooks, is in **`01-REVIEW-OF-ORIGINALS.md`**. Read it before teaching. Several cells will embarrass you live if you don't.

---

## 2. The 18-session map

Each session has one idea, one dataset and one Naija story.

| Wk | # | Session title | Original topic it covers | Main dataset | The Naija hook |
|---|---|---|---|---|---|
| **1** | 1 | **Colab bootcamp + "What is a time series?"** | 3.1 structure | `ka_band_availability_daily` | Your house's NEPA light log is a time series. "Up NEPA!" is a data point. |
| | 2 | **Charts that don't lie** | 3.2 visualising | `rf_link_quality_hourly`, `vsat_uptime_by_region_weekly` | DStv vanishes when Lagos rain falls: that's Ka-band rain fade. Also, the *average* lies. |
| | 3 | **Calm down the noise: rolling windows** | 3.3 rolling windows | `noc_tickets_daily` | Even faults rest on Sunday: weekend tickets are half of weekday tickets. |
| **2** | 4 | **Take it apart: trend, season, noise** | 3.4 decomposition | `ka_band_availability_monthly`, `additive_multiplicative_demo` | Lagos traffic = city growing (trend) + rush hour (season) + one keke breakdown (noise). |
| | 5 | **Does today remember yesterday?** | 3.5 autocorrelation | `bandwidth_throughput_daily`, `twta_thermal_daily` | Suya sales and generator sales both rise in December. Does suya cause generators? |
| | 6 | **Lab day + Quiz 1 + choose your capstone** | Week 3 review | all Week 3 files | Capstone brief picked, email to unit head drafted |
| **3** | 7 | **Alarms that cry wolf** | 4.1 thresholds | `bus_power_telemetry_hourly` | Eclipse = the satellite's own "NEPA has taken light": it runs on battery like your inverter. NigComSat-1 was lost in 2008 to a solar-array failure, and this is why we watch the array. |
| | 8 | **Control charts & residuals** | 4.2 SPC, 4.3 residuals | `bus_power_telemetry_hourly`, `twta_thermal_daily` | Mama Put knows the normal price of tomatoes. One price outside her range and she notices. |
| | 9 | **The slow creep: drift & CUSUM** | 4.4 change points | `twta_thermal_daily` (W4), `battery_health_daily` (W4) | The landlord adds a little to the rent every year. No single year shocks you, but CUSUM keeps the receipts. |
| **4** | 10 | **Scoring a detector + Quiz 2** | 4.5 precision/recall | `telemetry_anomaly_labels` (fixed copy) | The mai-guard who shouts "Thief!" at every goat: high recall, terrible precision. |
| | 11 | **Meet scikit-learn + Isolation Forest** | 5.1, 5.2 | `bus_telemetry_multivariate_hourly` | Spot the man in agbada at a beach party: the odd one out gets isolated fast. |
| | 12 | **Give the model eyes: feature engineering** | 5.3 | `bus_telemetry_multivariate_hourly` | NEPA brought light, but the inverter still isn't charging. Each thing looks normal alone and is wrong together. |
| **5** | 13 | **No expo! Honest train/test splits + Quiz 3** | 5.4 | multivariate + labels | WAEC "expo": if you saw the questions before the exam, your score is fake. |
| | 14 | **Forecasting baselines** | 6.1 | `ops_tickets_weekly` | Grandma's forecast: "tomorrow will be like today." She's hard to beat. |
| | 15 | **Regression forecasts + honest ranges** | 6.2, 6.3 | `ops_tickets_weekly` | "I'm on my way" is a point forecast. "30 to 90 minutes, Third Mainland Bridge permitting" is an interval. |
| **6** | 16 | **Backtesting: test it on the past first** | 6.5 | `ops_tickets_weekly` | Try your strategy on last season's matches before you stake real money. |
| | 17 | **When will it break? Remaining useful life + Quiz 4** | 6.4 | `degradation_assets_daily` | NigComSat-1R launched in 2011 with a 15-year design life. NIGCOMSAT-2A/2B are targeted for 2028/2029. How much fuel is left in the tank? |
| | 18 | **Capstone clinic & demo day** | Capstone | participants' own data | Five-minute demos to the cohort and, ideally, unit heads |

**Capstone runs alongside the course, not at the end:** pick a brief in S6, email the unit head in S6, then 15-minute checkpoints in S9, S12 and S15, and demo in S18.

---

## 3. What every session folder contains (the "kit")

```
week-1/day-1-colab-and-your-first-time-series/
├── README.md                      ← what's here and how to use it
├── 1-slides/
│   ├── web-animated/W1D1-slides-animated.html   ← the WOW deck: motion, real charts, flow diagrams (→ next, F full screen, N notes)
│   ├── powerpoint/W1D1-slides.pptx              ← static, simpler deck; also opens in Google Slides
│   └── pdf/W1D1-slides.pdf                      ← printable version of the animated deck
├── 2-exercise/
│   ├── W1D1-exercise.ipynb        ← Colab-ready: Open-in-Colab button, fill-in-the-blanks, instant ✅/❌ checks
│   └── rulebook/W1D1-rulebook.pdf (+ .md)       ← steps, golden rules, every common error and its fix
├── 3-glossary/W1D1-glossary.pdf (+ .md)         ← today's new words: plain English + Naija analogy + example
└── 4-instructor-only/
    ├── W1D1-instructor-notes.pdf (+ .md)        ← run of show, what to say, answer key, troubleshooting
    └── W1D1-solution.ipynb                      ← the filled-in notebook (for you)
```

Plus a shared **toolkit** for the whole course:

| File | What it is |
|---|---|
| `README.md` | Start here: the 18-day map with links |
| `toolkit/colab-survival-guide` (.md + .pdf) | Everything Colab: open, *save a copy to Drive*, run, restart, upload, the AI-button data rule |
| `toolkit/master-glossary` (.md + .pdf) | Every word from every daily glossary, A to Z (rebuilt automatically) |
| `toolkit/nigcomsat-fact-sheet` (.md + .pdf) | Verified facts about NIGCOMSAT and NigComSat-1R, with sources |
| `toolkit/master-rulebook` (.md + .pdf) | All the rules from all 18 days, grouped by theme, with the key rules on page one |
| `week-6/final-project/` | Final-project requirements PDF, with hardware and data-collection recommendations |
| `week-N/MCQ/` | Each week's 30 questions for the LMS, in the original MCQ format (JSON + CSV): the 120 originals regrouped by week and corrected, plus 60 new ones on what this course adds |
| `assets/brand/` | NIGCOMSAT and Publica Academy logos |

---

## 4. How Colab will work

- **One click to open.** Every notebook carries an "Open in Colab" badge.
- **One cell to set up.** Cell 1 fetches the original data straight from the public GitHub repo and prints `✅ Ready`. No uploads and no "file not found". Colab already has pandas, numpy, matplotlib, scikit-learn and statsmodels, so nothing needs installing.
- **Instant feedback.** After each task they run a check: `✅ Correct! The 7-day window removes the weekend effect` or `❌ Not yet. Hint: weekends are 2 days in every 7…`
- **Session 1 is a real Colab bootcamp:** Shift+Enter, run order, restart, "Save a copy in Drive" (otherwise their work disappears), the Files panel, uploading their own CSV, downloading `.ipynb`, and the Gemini button: **never paste real NIGCOMSAT data into it.**
- **Tested before you teach.** I run every notebook from top to bottom in a clean environment (current and newer pandas) before handing it to you.

---

## 5. Build order: one step at a time

| Step | What gets built | You check |
|---|---|---|
| **0** ✅ | Research, review of originals, this plan, branch `jasons-restructure` | This plan |
| **1** ✅ | Brand + folder structure for all 18 days, toolkit (README, Colab guide, glossary, fact sheet), **final-project requirements PDF**, and **Day 1 complete in every format** as the pilot | The look and feel. This sets the template for the other 17 |
| **2** ✅ | Days 2–6 (Weeks 1–2: understanding a series), incl. Quiz 1 with shuffled answers and the final-project kickoff worksheet | Kits + test run |
| **3** ✅ | Days 7–10 (Weeks 3–4: anomaly detection), incl. Quiz 2 with shuffled answers and final-project Checkpoint 2 | Kits + test run |
| **4** ✅ | Sessions 11–13 (Weeks 4–5: machine learning), incl. Quiz 3 and final-project Checkpoint 3. The Week 5 detector was rebuilt and checked on the data first (the original's result doesn't reproduce, see review): one relationship feature catches the hidden faults, and the honest test recommends the simpler detector | Kits + test run |
| **5** ✅ | Sessions 14–18 (Weeks 5–6: forecasting, RUL, capstone), incl. Quiz 4, Checkpoint 4 and demo day (peer scoring sheet + report template). The original's numbers were checked on the data first (they reproduce, bar the propellant bug). One idea it misses carries the forecasting days: tickets **per terminal** repeat every year, so a simple rate forecast beats every model, and the backtest recommends it. Remaining life is taught as a window, not a day | Kits + test run |
| **6** ✅ | Master rulebook (`toolkit/master-rulebook`: the key rules on page one, then every rule by theme and one error → fix table), shuffled quiz versions, PDF exports of slides, final full test (all 18 solution notebooks N of N on pandas 2.2 and 3), commit. Push and PR wait for Write access to the repo | Final sign-off |

Each step ends with every notebook test-run and a commit under your name only.

---

## 6. Decisions made

1. **Hosting:** write access to the Publica repo comes later, and the branch gets pushed then. The "Open in Colab" links already point at branch `jasons-restructure` and go live once it's pushed. To host somewhere else, change two lines in `_build/common.py` and rebuild.
2. **Slide formats:** all three. Animated web decks for the wow factor, static PowerPoint (which also opens in Google Slides), and PDF.
3. **Session length:** planned for ~2 hours. The content can stretch.
4. **Final project:** requirements PDF in `week-6/final-project/`, including hardware and data-collection recommendations.
5. **No dates anywhere:** days are "Week N · Day N" only.
