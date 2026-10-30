# W4D1 Rule Book: Scoring a Detector

> **Your goal today:** be the referee. Score every alarm from Week 3 with **one** scorer and **one** set of rules, then turn false alarms into engineer hours. **14 green ✅ ticks** to collect.
> Time: about 50 minutes, then Quiz 2. Keep this page open next to Colab.

## Before you start (2 minutes)

<ul class="check">
<li>Open <code>W4D1-exercise</code> in Colab → <b>File → Save a copy in Drive</b>.</li>
<li>Run <b>STEP 0</b>. Wait for <code>✅ Ready!</code></li>
<li>Run every ▶️ cell in order. Each ✍️ cell depends on the cells above it.</li>
</ul>

## The 4 scoring rules (write them down BEFORE you score)

| # | Rule | Example |
|---|---|---|
| 1 | One flag anywhere inside an event's start→end (±1 time step) = **caught** | One flagged hour at 09:00 on 18 Aug catches EV01 |
| 2 | Many flags inside one event = still **one** catch | EV02 flagged on both its hours = 1 catch |
| 3 | A flag outside every event = **one false alarm** | Every eclipse-hour flag = a 2 a.m. page for nothing |
| 4 | A long event is still **one** event | Flag 1 of EV05's 233 days → caught once, not 233 times |

## The 3 numbers

| Number | Formula | Plain question | Use it? |
|---|---|---|---|
| **Recall** | caught ÷ real events | Did we miss anything? | ✅ always |
| **Precision** | caught ÷ (caught + false alarms) | When it pages, is it real? | ✅ always |
| **Accuracy** | right answers ÷ all readings | — | ❌ **never** for rare events (doing nothing scores 99.87%) |

## The exercise, step by step

| Task | What you do | The tool you need |
|---|---|---|
| **A1** | Accuracy of a detector that never fires | `1 - n_events / n_readings` |
| **A2** | Agree two scoring rules | `"yes"` / `"no"` and a number |
| **A3** | Musa the mai-guard: recall and precision | `9 / 10` and `9 / 200` |
| **B1** | Score the 82% state-of-charge floor | `SOC_FLOOR = 82` |
| **B2** | Score the control chart, all hours | `K = 3` |
| **B3** | Same chart, sunlit hours only | `eclipse_flag == 0` |
| **B4** | 3σ on the amplifier residual | `N_SIGMA = 3` |
| **B5** | CUSUM on the residual | `H = 5` |
| **B6** | The event every detector missed | read the report card |
| **B7** | Your pick for the bus-power console | 1, 2 or 3 |
| **C1** | False alarms → hours a year | per season × 2 × 20 ÷ 60 |
| **C2** | Precision of the naive rain alarm | `n_real / n_flags` |
| **C3** | Is every rain-fade hour an anomaly? | `True` or `False` (no quotes) |
| **🌶️ Bonus** | Build a slope alarm that catches EV06 | pick `RATE_LINE`, e.g. `-3.0` |

## The scorer (you'll see it in the notebook)

```python
score_events(flags, labels, "bus_power_telemetry_hourly.csv")          # hourly files: tol="1h" (default)
score_events(flags, labels, "twta_thermal_daily.csv", tol="1D")         # daily files: tol="1D"
```

`flags` is a True/False Series with the same time index as the data. The source file name must match the `source_file` column of the answer key **exactly**, including `.csv`.

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `AssertionError: ✍️ Fill in … first` | A `___` is still there | Replace it, run the cell again |
| `NameError: name 'labels' is not defined` | You skipped the answer-key cell | Run the 🔑 cell (`labels = load_labels()`) |
| `NameError: name 'score_events' …` | You skipped the scorer cell | Run the ▶️ scorer cell at the start of Part B |
| `{'events': 0, …}` / `ZeroDivisionError` | The file name doesn't match the key | Copy it exactly: `"bus_power_telemetry_hourly.csv"` |
| `ParserError: Expected 8 fields …` | You loaded the labels with plain `pd.read_csv` | Use `load_labels()`: it repairs the stray comma |
| `ValueError: Invalid frequency: H` | Old code with capital `"H"` | Use lowercase `"h"` (and `"1h"` for tolerance) |
| `False alarms` look huge | You scored eclipse hours as faults | Add `& (bus["eclipse_flag"] == 0)` |
| Everything is weird | — | **Runtime → Restart session and run all** |

## Rules of thumb you'll keep forever

1. **Write the rules first**, then compute. Never change them after seeing the score.
2. **Never report accuracy** for rare events. Report recall **and** precision.
3. **Same scorer, same period** for every detector you compare.
4. **Condition on known causes** (eclipse, rain) instead of widening the band.
5. **Say false alarms in hours.** That's the number a manager can act on.
6. **Decide which number leads** before you score: recall for "a miss could cost the satellite", precision for "too many pages and people stop reading them".

> 🏁 **Finished?** Run `scoreboard()`. Then try the 🌶️ slope alarm, and get ready for **Quiz 2** (phones down, no AI, 20 minutes).
