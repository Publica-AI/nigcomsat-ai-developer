# 🛰️ Time-Series for NIGCOMSAT: Start Here

**A 6-week, 18-day hands-on course** on reading, monitoring and forecasting operational data, built on the original Publica Academy *Time-Series* module (`../Time-series/`) and restructured to be simple, visual and fun.

- **Who it's for:** NIGCOMSAT engineers and staff who know basic Python. No satellite or statistics background needed.
- **Where it runs:** 100% in **Google Colab**: nothing to install.
- **Rhythm:** 3 days a week × 6 weeks, about **2 hours** per day.
- **The originals are untouched.** Everything here is new and points back to them.

---

## 📁 How this folder is organised

```
Jasons-Restructure/
├── README.md                    ← you are here
├── 00-PLAN.md                   ← the plan and build steps
├── 01-REVIEW-OF-ORIGINALS.md    ← instructor eyes only: bugs and traps in the originals
├── toolkit/                     ← for everyone, all six weeks
│   ├── colab-survival-guide     (.md + .pdf)
│   ├── master-glossary          (.md + .pdf): every new word, A to Z
│   └── nigcomsat-fact-sheet     (.md + .pdf): real facts behind the examples
├── week-1/ … week-6/            ← one folder per week, one sub-folder per day
│   └── day-N-topic/
│       ├── 1-slides/
│       │   ├── web-animated/    ← the WOW deck: open in Chrome (→ next, F full screen, N notes)
│       │   ├── powerpoint/      ← static deck (also opens in Google Slides)
│       │   └── pdf/             ← printable slides
│       ├── 2-exercise/          ← the Colab notebook
│       │   └── rulebook/        ← one-page rules + error fixes (.md + .pdf)
│       ├── 3-glossary/          ← today's new words with Naija analogies (.md + .pdf)
│       └── 4-instructor-only/   ← run of show, answer key, solution notebook
├── week-6/final-project/        ← final-project requirements (PDF) + hardware recommendations
├── assets/brand/                ← NIGCOMSAT and Publica Academy logos
└── _build/                      ← the scripts that generate the slides, PDFs and notebooks (you never need to touch this)
```

## 🗺️ The course map

| Week | Day | Session | Original topic | Status |
|---|---|---|---|---|
| 1 | 1 | [Colab Bootcamp + Your First Time Series](week-1/day-1-colab-and-your-first-time-series/) | Week 3 · 3.1 Structure of time-series data | ✅ ready |
| 1 | 2 | [Charts That Don't Lie](week-1/day-2-charts-that-dont-lie/) | Week 3 · 3.2 Visualising and data storytelling | ✅ ready |
| 1 | 3 | [Calm Down the Noise: Rolling Windows](week-1/day-3-rolling-windows/) | Week 3 · 3.3 Rolling windows and smoothing | ✅ ready |
| 2 | 1 | [Take It Apart: Trend, Season and Noise](week-2/day-1-trend-season-noise/) | Week 3 · 3.4 Decomposition | ✅ ready |
| 2 | 2 | [Does Today Remember Yesterday?](week-2/day-2-does-today-remember-yesterday/) | Week 3 · 3.5 Autocorrelation | ✅ ready |
| 2 | 3 | [Lab Day + Quiz 1 + Pick Your Project](week-2/day-3-lab-day-quiz-1-and-project-kickoff/) | Week 3 review + capstone kickoff | ✅ ready |
| 3 | 1 | [Alarms That Cry Wolf](week-3/day-1-alarms-that-cry-wolf/) | Week 4 · 4.1 What your alarm software already does | 🚧 Step 3 |
| 3 | 2 | [Control Charts and Residuals](week-3/day-2-control-charts-and-residuals/) | Week 4 · 4.2 SPC, 4.3 Residual-based detection | 🚧 Step 3 |
| 3 | 3 | [The Slow Creep: Drift and CUSUM](week-3/day-3-drift-and-cusum/) | Week 4 · 4.4 Change points and drift | 🚧 Step 3 |
| 4 | 1 | [Scoring a Detector + Quiz 2](week-4/day-1-scoring-detectors-and-quiz-2/) | Week 4 · 4.5 Evaluating a detector | 🚧 Step 3 |
| 4 | 2 | [Meet scikit-learn + Isolation Forest](week-4/day-2-scikit-learn-and-isolation-forest/) | Week 5 · 5.1 scikit-learn workflow, 5.2 Isolation forest | 🚧 Step 4 |
| 4 | 3 | [Give the Model Eyes: Feature Engineering](week-4/day-3-feature-engineering/) | Week 5 · 5.3 Feature engineering | 🚧 Step 4 |
| 5 | 1 | [No Expo! Honest Train/Test Splits + Quiz 3](week-5/day-1-honest-splits-and-quiz-3/) | Week 5 · 5.4 Temporal train/test discipline | 🚧 Step 4 |
| 5 | 2 | [Forecasting Baselines](week-5/day-2-forecasting-baselines/) | Week 6 · 6.1 Forecasting baselines | 🚧 Step 5 |
| 5 | 3 | [Regression Forecasts + Honest Ranges](week-5/day-3-regression-forecasts-and-intervals/) | Week 6 · 6.2 Regression forecasting, 6.3 Prediction intervals | 🚧 Step 5 |
| 6 | 1 | [Backtesting: Test It on the Past First](week-6/day-1-backtesting/) | Week 6 · 6.5 Backtesting | 🚧 Step 5 |
| 6 | 2 | [When Will It Break? Remaining Useful Life + Quiz 4](week-6/day-2-remaining-useful-life-and-quiz-4/) | Week 6 · 6.4 Trend-to-threshold and RUL | 🚧 Step 5 |
| 6 | 3 | [Project Clinic and Demo Day](week-6/day-3-project-clinic-and-demo-day/) | Capstone | 🚧 Step 5 |

## 🚀 How to run a day

1. **Before:** read `4-instructor-only/…-instructor-notes.pdf` and run the solution notebook once.
2. **Teach:** open `1-slides/web-animated/…html` in Chrome. **→** next · **←** back · **F** full screen · **N** speaker notes.
   No projector magic? Use the PowerPoint in `1-slides/powerpoint/` (or upload it to Google Drive → *Open with Google Slides*).
3. **Practise:** participants click **Open in Colab** on `2-exercise/…-exercise.ipynb`, then **File → Save a copy in Drive**.
4. **Support:** everyone keeps `2-exercise/rulebook/…-rulebook.pdf` open beside the notebook.
5. **Revise:** share `3-glossary/…-glossary.pdf` at the end of the day.

## 🧰 Where the data comes from

The notebooks download the **original synthetic datasets** straight from `Time-series/week-0X/data/` in this repository, so there are no copies to get out of sync. The data is synthetic teaching data built to behave like NigComSat-1R, so it's safe to use in AI assistants. **Real NIGCOMSAT data is not**: see the Colab Survival Guide.
