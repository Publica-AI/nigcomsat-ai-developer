# W5D2 Rule Book: Forecasting Baselines

> **Your goal today:** lock the last 8 weeks of NOC tickets away, forecast them four cheap ways, score every forecast with the same ruler (MAE), then build the two-line forecast that beats them all. **14 green ✅ ticks** to collect.
> Time: about 60 minutes. Keep this page open next to Colab.

## Before you start (2 minutes)

<ul class="check">
<li>Open <code>W5D2-exercise</code> in Colab → <b>File → Save a copy in Drive</b>.</li>
<li>Run <b>STEP 0</b>. Wait for <code>✅ Ready!</code></li>
<li>Run every cell in order. Each ✍️ cell depends on the cells above it.</li>
<li>The ▶️ cell with <code>def mae(...)</code> (top of Part B) must run before the scoreboards.</li>
</ul>

## The four baselines (and the fifth that wins)

| Baseline | Grandma says | One line of the function | Forecast for all 8 test weeks |
|---|---|---|---|
| 👵🏾 **Naive** | "Same as last week" | `series.iloc[-1]` | 74 every week |
| 📅 **Seasonal naive** | "Same week last year" | `series.iloc[-52:]` | 42, 42, 44, 42, 53, 51, 52, 54 |
| 🧮 **Moving average** | "The average of the last 8 weeks" | `series.iloc[-8:].mean()` | 77 every week |
| 🫖 **Exponential smoothing** | "A running level" | `alpha * v + (1 - alpha) * level` | 75.6 every week (α = 0.3) |
| 🎯 **Rate seasonal naive** | "Last year's rate × today's network" | `rate = series / terminals` | 56.4, 56.1, 58.5, 55.6, 69.8, 66.8, 67.7, 70.0 |

**MAE** (mean absolute error) = the average size of the misses, in tickets. *"On a typical week we were off by N tickets."* Lower is better.

## The exercise, step by step

| Task | What you do | The tool you need |
|---|---|---|
| **A1** | Load the weeks with the right frequency | `FREQ = "W-MON"` (in quotes) |
| **A2** | Lock the last weeks away | `H = 8` |
| **B1** | Naive: the last value | `series.iloc[-1]` |
| **B2** | Seasonal naive: the season length | `period=52` |
| **B3** | Moving average: the window | `window=8` |
| **B4** | Exponential smoothing: what stays of the old level | `(1 - alpha)` |
| **B5** | The scoreboard: compare with what really happened | `COMPARE_WITH = actual` (no quotes) |
| **B6** | Why seasonal naive came last: network growth in a year | `WEEKS_BACK = 52` |
| **C1** | Tickets per 1,000 terminals, by month | `DIVIDE_BY = train_terminals` (no quotes) |
| **C2** | When does the rain arrive? | a month number, 1–12 |
| **C3** | Rate seasonal naive: the rate | `series / terminals` |
| **C4** | Score it on the same 8 weeks | `HORIZON = H` |
| **D1** | The flat training average | `FLAT = train.mean()` |
| **🌶️ Bonus** | Which α follows the latest week closely? | `0.1`, `0.3` or `0.9` |

## The code you'll use

```python
tickets = pd.read_csv(data_path("ops_tickets_weekly"), parse_dates=["week_start"],
                      index_col="week_start").asfreq("W-MON")    # one row per Monday
y = tickets["tickets_raised"]
train, actual = y.iloc[:-H], y.iloc[-H:]                         # learn from the past, judge on the last H
assert train.index.max() < actual.index.min()                    # no overlap, ever

naive(train, H)                                   # every baseline: (training series, horizon) -> H numbers
rate_seasonal_naive(train, train_terminals, H)    # the rate version also needs the terminals
mae(forecast, actual)                             # the typical miss, in tickets
```

**Blind** means every forecast is made on the last training week (27 Oct 2025). The forecast for 22 December can't use the real number from 15 December.

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `AssertionError: ✍️ Fill in … first` | A `___` is still there | Replace it, run the cell again |
| `AssertionError: ✍️ Finish … first` / `Get B1 to B4 to ✅ first` | An earlier task isn't done or isn't ✅ yet | Go back, fix it, then come back |
| `❌ Not yet … (Python said: TypeError)` under a function | The `___` inside the function is still there, or the wrong type | Fill the blank in the `def` line or the body, run the cell again |
| `NameError: name 'W' is not defined` | You typed `W-MON` without quotes | Frequencies are text: `"W-MON"` |
| A1 shows 103 weeks and 206 gaps | You used `"W"` (weeks ending on **Sunday**) | Every date is a Monday: `"W-MON"` |
| `NameError: name 'mae' is not defined` | You skipped the ▶️ `def mae` cell | Run it (top of Part B) |
| `AssertionError: ✍️ Use the variable itself, without quotes` | You typed `"train_terminals"` | Type `train_terminals` (a variable, not text) |
| C4 shows 52 numbers instead of 8 / a length error | `HORIZON` isn't 8 | `HORIZON = H` |
| Everything is weird | — | **Runtime → Restart session and run all** |

## Rules of thumb you'll keep forever

1. **Baselines first.** Before any model, forecast with the cheap ones. A model that can't beat them has not earned its place.
2. **Lock the test weeks away** and forecast them blind, from one origin. No peeking, no expo.
3. **Same weeks, same scorer** (MAE) for every forecast you compare.
4. **Say MAE in words:** "off by about N tickets on a typical week".
5. **Divide by the size you already know** (terminals, drive, rooms). A rate repeats; a count grows.
6. **Beat the BEST baseline**, not the one with the fanciest name.
7. **Don't choose settings (like α) by looking at the test weeks.** That's expo.
8. **One split is one result.** Test on many splits before you trust it (Week 6 · Day 1).

> 🏁 **Finished?** Run `scoreboard()`, then the 🌶️ α task. For your project: build this same table (your baselines, same test period, same MAE) for **Checkpoint 4** next session.
