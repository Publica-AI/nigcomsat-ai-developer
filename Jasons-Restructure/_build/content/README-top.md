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
│   ├── master-rulebook          (.md + .pdf): every rule from all 18 days, by theme
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

{{COURSE_MAP}}

## 🚀 How to run a day

1. **Before:** read `4-instructor-only/…-instructor-notes.pdf` and run the solution notebook once.
2. **Teach:** open `1-slides/web-animated/…html` in Chrome. **→** next · **←** back · **F** full screen · **N** speaker notes.
   No projector magic? Use the PowerPoint in `1-slides/powerpoint/` (or upload it to Google Drive → *Open with Google Slides*).
3. **Practise:** participants click **Open in Colab** on `2-exercise/…-exercise.ipynb`, then **File → Save a copy in Drive**.
4. **Support:** everyone keeps `2-exercise/rulebook/…-rulebook.pdf` open beside the notebook.
5. **Revise:** share `3-glossary/…-glossary.pdf` at the end of the day.

## 🧰 Where the data comes from

The notebooks download the **original synthetic datasets** straight from `Time-series/week-0X/data/` in this repository, so there are no copies to get out of sync. The data is synthetic teaching data built to behave like NigComSat-1R, so it's safe to use in AI assistants. **Real NIGCOMSAT data is not**: see the Colab Survival Guide.
