# W5D1 Rule Book: No Expo! Honest Train/Test Splits

> **Your goal today:** catch a model cheating, build an honest split by time, then referee a fair fight between the isolation forest and the Week 4 control chart. **14 green ✅ ticks** to collect.
> Time: about 45 minutes, then Quiz 3. Keep this page open next to Colab.

## Before you start (2 minutes)

<ul class="check">
<li>Open <code>W5D1-exercise</code> in Colab → <b>File → Save a copy in Drive</b>.</li>
<li>Run <b>STEP 0</b>. Wait for <code>✅ Ready!</code></li>
<li>Run the three ▶️ cells under STEP 0 (data, scorer, Week 4 tools). Everything below needs them.</li>
<li>Run every cell in order. Each ✍️ cell depends on the cells above it.</li>
</ul>

## What "expo" looks like in time series

| Expo | What it looks like | The honest version |
|---|---|---|
| 👥 **Neighbours in training** | A random split: the test hour at 10:00 has 09:00 and 11:00 in training | Split **by time**: past to train, future to test |
| 🔮 **Features that peek ahead** | `shift(-1)`, `rolling(..., center=True)` | Only `shift(1)`, `shift(24)`, plain `rolling(24)`: the **14:00 test** |
| 🔑 **Settings tuned on the key** | Picking `k` or `contamination` by looking at the test answers | Fix settings first, or tune on the **training** months only |

## The 4 rules of a fair fight (write them down BEFORE you score)

| # | Rule | Today |
|---|---|---|
| 1 | Same held-out months | 2 Sep – 31 Dec |
| 2 | Same hours | steady sunlight (`steady`) |
| 3 | Same scorer | `score_events` (one flag inside = caught, outside = false alarm) |
| 4 | Settings fixed first | chart `k = 3`, forest `contamination = 0.005` |

## The exercise, step by step

| Task | What you do | The tool you need |
|---|---|---|
| **A1** | Random split: share of fault hours the copycat found | `pred[y_te == 1].mean()` |
| **A2** | Split by time: same question | `CUT = "2025-09-01"` |
| **A3** | Which event did it still catch? | read the table, e.g. `"EV05"` |
| **B1** | Build train, embargo, test | `TRAIN_END = "2025-09-01"`, `TEST_START = "2025-09-02"` |
| **B2** | How long must the embargo be? | the longest window, in hours |
| **C1** | Contender 1: Week 4 chart, sunlit hours | `K = 3` |
| **C2** | Real catch or lucky catch? | `"real"` or `"lucky"` |
| **C3** | Contender 2: same chart, steady hours | `CONTEXT = steady` (no quotes) |
| **C4** | Contender 3: the forest on the lean features | `CONTAMINATION = 0.005` |
| **C5** | Contender 4: the chart on the lean features | `K = 3` |
| **C6** | Your recommendation | 1, 2, 3 or 4 |
| **D1** | Rolling origin: four exams | `GAP = 24` |
| **D2** | A dirty reference period | `DIRTY_FIT = steady` (no quotes) |
| **🌶️ Bonus** | Tune the forest honestly, on the past only | the smallest budget that catches all 3 past events |

## The code you'll use

```python
train = bus.index <  "2025-09-01"          # every hour BEFORE 1 Sep
test  = bus.index >= "2025-09-02"          # every hour FROM 2 Sep (1 Sep = embargo)
assert bus.index[train].max() < bus.index[test].min()

chart_flags(X, train & steady, steady)             # 3-sigma chart: fit on train, judge steady hours
forest_flags(X, train & steady, steady)            # isolation forest, same rows
score_events(flags[test], labels)                  # score the test months only
event_table(flags[test], labels)                   # caught? how late? how many hours lit?
```

`train & steady` means "training months **and** steady sunlight". The first argument says which rows the detector **learns** from; the second says which rows it **judges**.

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `AssertionError: ✍️ Fill in … first` | A `___` is still there | Replace it, run the cell again |
| `AssertionError: ✍️ Finish … first` | You skipped an earlier task | Do that task, then come back |
| `AssertionError: ✍️ Use the variable itself, without quotes` | You typed `"steady"` | Type `steady` (it's a variable, not text) |
| `NameError: name 'chart_flags' …` / `'X'` / `'steady'` | You skipped the ▶️ tools cell | Run the three ▶️ cells under STEP 0 |
| `NameError: name 'train' is not defined` | You skipped B1 | Do B1 first |
| `AssertionError: leakage: training overlaps the test` | Your dates are the wrong way round | `TRAIN_END` must come **before** `TEST_START` |
| `SyntaxError: leading zeros in decimal integer literals …` | You typed a date without quotes | Dates are text: `"2025-09-01"` |
| Your forest's false alarms differ a little from your neighbour's | Different `random_state` or library version | That's the forest's dice. The check accepts a range |
| Everything is weird | — | **Runtime → Restart session and run all** |

## Rules of thumb you'll keep forever

1. **Never shuffle time series** before splitting. Train on the past, test on the future.
2. **Embargo ≥ your longest feature window.** Then `assert` the split.
3. **Fix your settings before you look at the test.** Tune only on the training months.
4. **Same months, same hours, same scorer** for every detector you compare.
5. **Ask why a flag fired.** A catch for the wrong reason is a lucky catch.
6. **If the simple model wins or ties, recommend it.** That's a professional result.
7. **Write down your reference period** and why operations believe it was quiet.

> 🏁 **Finished?** Run `scoreboard()`. Then try the 🌶️ honest-tuning task, and get ready for **Quiz 3** (phones down, no AI, 20 minutes).
