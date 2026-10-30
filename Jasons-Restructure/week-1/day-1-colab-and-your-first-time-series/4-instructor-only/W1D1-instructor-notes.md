# W1D1 Instructor Notes: Colab Bootcamp + Your First Time Series

> **The one idea for today:** *a time series is a table where the order of the rows carries meaning.* Everything else (Colab, pandas, `.asfreq`) is the tooling to work with that idea.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours (it can stretch to 2.5 if Colab sign-in is slow) |
| **Participants leave able to** | open and save a Colab notebook, run cells in order, recover from a restart, load a CSV as a proper time series, find gaps, name the 4 components |
| **Covers (original)** | Week 3 Code Book: *Setup*, the `profile()` helper, *Conventions used in every file*, **B1 Ka-band availability daily**, **B2 monthly**; Week 3 quiz topic *structure of time-series data* |
| **Dataset** | `Time-series/week-03/data/ka_band_availability_daily.csv` (+ `noc_tickets_daily.csv` for the bonus) |
| **Files you need open** | animated slides (`1-slides/web-animated/`), your **solution** notebook, the rule book PDF |

## The day before: checklist

<ul class="check">
<li>Open the exercise link yourself in a fresh Chrome window and run STEP 0. You should see <code>✅ Ready!</code></li>
<li>Run your <b>solution</b> notebook top to bottom: every check should be ✅ (it takes about 20 seconds).</li>
<li>Ask participants to bring a laptop with <b>Chrome</b> and to know their <b>Google account password</b>. A personal Gmail is fine.</li>
<li>Some work Google accounts block Colab. If so, participants use a personal Gmail for the course.</li>
<li>Test the projector with the animated slides: press <b>F</b> for full screen and <b>N</b> to see these notes on your laptop.</li>
<li>Share the rule book PDF and the exercise link in the class group chat (WhatsApp/Teams).</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | NEPA light diary: “a time + a value = a time series” | 1–3 |
| 0:10 | **Colab bootcamp** | What Colab is, the 5 parts of the screen, the 3 golden rules. **Everyone saves a copy in Drive NOW.** | 4–7 |
| 0:25 | **Live demo** | Restart → NameError → fix it. The AI-button data rule. | 8–9 |
| 0:35 | **What is a time series** | Order matters (shuffle demo), anatomy, NigComSat-1R, today's data | 10–14 |
| 0:50 | **The recipe** | parse_dates → index_col → asfreq; the 5 inspection questions; UTC vs WAT; 4 characters | 15–19 |
| 1:00 | **Hands-on** | Exercise Part A (15 min) then Part B (45 min). Walk the room. | 20 |
| 1:45 | **Wrap-up** | Scoreboards up, recap, 2 volunteers explain “order matters” and “why asfreq” | 21 |
| 1:55 | **Exit** | Share the glossary PDF as revision. Tease Day 2. | — |

## Explain it like this (in plain English)

- **Colab** = Python on Google's computer. The laptop is just a screen. Nothing to install.
- **Time series** = readings in time order. If you can shuffle the rows without losing anything, it's *not* a time series (a shopping list). If shuffling destroys the story, it *is* (the Ka-band chart).
- **`parse_dates`**: pandas reads dates from a CSV as text until you tell it otherwise. Text can't do “give me August”.
- **`index_col`**: makes the dates the row labels, so you can say `ka.loc["2024-08"]`.
- **`.asfreq("D")`**: the most important line. If an export is missing 3 days, `len()` still looks normal. `.asfreq` creates a slot for every day, so the missing ones show up as `NaN` and you can count them.
- **UTC vs WAT**: satellite telemetry is UTC, Lagos clocks are UTC + 1. Join two tables in different time zones and every event moves by an hour.
- **The 4 characters**: *trend* (direction), *seasonality* (fixed calendar), *cycle* (no fixed length), *noise* (ignore it). The seasonality-vs-cycle difference trips people up: the calendar decides seasonality; nobody can schedule a cycle.

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | “You've been collecting time series all your life.” | “How many hours of light did you get yesterday?” |
| 5 | “Even a small laptop is fine; the work happens in Google's data centre.” | — |
| 7 | Stop and make everyone do Rule 1. Walk the room and check. | “Whose notebook title now starts with *Copy of*?” |
| 8 | Demo the restart live. Make the NameError happen on purpose. | “What does NameError mean?” → “Colab forgot.” |
| 9 | The training data is synthetic and safe. Real data is restricted. | — |
| 11 | Press next to shuffle. Pause. Let them see the story vanish. | “Same numbers. What changed?” |
| 13 | Launched Dec 2011, replaced NigComSat-1 (lost in 2008 after a solar-array failure). 28 transponders, 4 bands. | — |
| 14 | Point at the dips: every rainy season. Ka-band hates heavy rain, like DStv. | “Which month do you think is worst?” (don't answer: they find it in B8) |
| 16 | Count the boxes in the top row: 11. Then the bottom: 14. | “Which one would you rather trust?” |
| 19 | “38 vs 41 tickets is the same week twice. Don't call a meeting.” | — |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A2 | `24 * 365` → 8760 | — |
| A3 | Restart → `NameError` → run STEP 0 + A2 | They forget STEP 0 after restarting → “STEP 0 after every restart.” |
| B1 | `"text"` | Typing `object` or `str` is also accepted |
| B2 | `"timestamp"` | No quotes → `NameError` → “text needs quotes” |
| B3 | `len(ka)` → 1,096 | — |
| B4 | `ka.index.min()` / `ka.index.max()` → 2023-01-01 / 2025-12-31 | Using `ka["timestamp"]` → it's the index now, not a column |
| B5 | `FREQ = "D"` → 3 missing days | `FREQ = D` without quotes |
| B6 | `ka["availability_pct"].idxmin()` → **2023-07-25** (95.71%) | `.min()` gives the value, not the date. `idxmin` gives the date. |
| B7 | Any sentence that states a finding | “Availability” alone is a label, not a finding |
| B8 | `"August"` | — |
| B9 | seasonality, trend, noise, cycle | Mixing up seasonality and cycle (fixed calendar vs not) |
| B10 | `22` | Answering 20 (subtracting instead of adding) |
| 🌶️ | `"Sunday"` (Saturday is close behind) | Forgetting `parse_dates`/`index_col` → `.day_name()` fails |

## Quiz link

The original Week 3 quiz (`Time-series/MCQ/week-03-mcq.csv`), topic **“structure of time-series data”**, questions 1–6, is exactly today's content: order matters, the 4 components, noise vs change, seasonality vs cycle, `.asfreq`, time zones. Use them as a 5-minute warm-up at the start of Day 2.

## Troubleshooting

| Problem | Fix |
|---|---|
| “Colab is blocked / disabled for your organisation” | Use a personal Gmail account |
| STEP 0 fails with `HTTP Error` / `URLError` | Rare: GitHub is briefly unreachable from Google. Wait a minute and re-run. Fallback: download the CSV from the repo, drag it into the 📁 Files panel, and STEP 0 will use the uploaded copy |
| “Runtime disconnected” | Idle too long. Click *Reconnect*, then run STEP 0 and the cells above |
| Someone's checks pass but their chart is empty | They ran the plot before loading `ka`. Restart and run all |
| A participant finishes in 20 minutes | Send them to the 🌶️ bonus, then ask them to help a neighbour |

## Notes on the original material

- The original code book loads data with `DATA = Path("data")`, which **doesn't work in Colab**. Our `data_path()` downloads each file from the original repo instead.
- The original uses `.asfreq("H")`, which newer pandas prints warnings about. We use `"h"` (hourly) and `"D"` (daily).
- Facts about NigComSat-1R used on the slides are in `toolkit/nigcomsat-fact-sheet.md`, with sources.
