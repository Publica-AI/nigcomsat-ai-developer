# W1D3 Rule Book: Calm Down the Noise: Rolling Windows

> **Your goal today:** smooth the daily NOC ticket series with a rolling window, find out what smoothing hides, and earn **14 green ✅ ticks**.
> Time: about 60 minutes. Keep this page open next to Colab.

## Before you start (2 minutes)

<ul class="check">
<li>Open the <b>W1D3-exercise</b> notebook with the <b>Open in Colab</b> button.</li>
<li><b>File → Save a copy in Drive.</b> Work only in the new tab.</li>
<li>Run <b>STEP 0</b> (Shift + Enter). Wait for <code>✅ Ready!</code></li>
</ul>

## The 7 golden rules for today

| # | Rule | Why |
|---|---|---|
| 1 | **Run cells top to bottom** | Every cell uses what the cells above made (`tk`, `roll7`, `margin`, …) |
| 2 | **Roll one column, not the whole table**: `tk["tickets_raised"].rolling(7)` | The column is the series. The table has other columns too |
| 3 | **A window is a number of rows**: `rolling(7)` on daily data = 7 days | On hourly data, `rolling(24)` = one day |
| 4 | **The first N−1 values are `NaN`** | A 7-day average doesn't exist until day 7. It's not an error |
| 5 | **Trailing (the default) for anything live** | `center=True` uses future days: reports only |
| 6 | **Never report an SLA from a smoothed line** | Short outages disappear inside the average |
| 7 | **`True`/`False` have no quotes; text does** | `CENTER = True`, but `"half"`, `"no"`, `"high"` |

## The exercise, step by step

| Task | What you do | The tool you need |
|---|---|---|
| **A1** | Name the time column | `"date"` |
| **A2** | Weekend vs weekday volume | read the two averages: `"a quarter"`, `"half"` or `"the same"` |
| **B1** | Window size for one week | `7` |
| **B2** | Count the empty rows at the start | `tk["roll7"].isna().sum()` |
| **B3** | Which window still zig-zags? | read the chart: `3`, `7` or `30` |
| **B4** | Prove 7 cancels the weekend | `roll7_by_day.max() - roll7_by_day.min()` |
| **B5** | Make a centred window | `CENTER = True` |
| **B6** | Is the centred line usable live? | `"yes"` or `"no"` |
| **B7** | Count weekly buckets | `len(weekly)` |
| **B8** | Which alpha follows the data closely? | `"high"` or `"low"` |
| **B9** | Share of days with zero P1 tickets | `(tk["priority_1"] == 0).mean()` |
| **B10** | Outage hours: raw vs smoothed | `(margin < 0).sum()`, `(smooth < 0).sum()` |
| **B11** | Weekly mean + “investigate 38 → 41?” | `wk["tickets_raised"].mean()`, `"yes"`/`"no"` |
| **🌶️ Bonus** | Count the odd weeks | `((q - q.mean()).abs() > 2 * q.std()).sum()` |

## The smoothing toolbox

```python
s = tk["tickets_raised"]

s.rolling(7).mean()                # trailing 7-day average (safe for live use)
s.rolling(7).std()                 # how wobbly the last 7 days were
s.rolling(30, center=True).mean()  # centred: uses 15 future days (reports only!)
s.ewm(alpha=0.3).mean()            # exponential smoothing: high alpha = fast, low = smooth
s.resample("W").sum()              # weekly buckets: one value per week (not a rolling window)
```

**Pick a window:** daily tickets → start with **7**. Rare counts (P1) → **30**. Hourly data → **24** for a day.

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `AssertionError: ✍️ Do A1 first…` | A blank above is still empty | Fill it in, run that cell, then run this one again |
| `NameError: name 'tk' is not defined` | Colab forgot, or you skipped a cell | Run STEP 0 and the cells above, top to bottom |
| `ValueError: window must be an integer` | `rolling()` got text or nothing | `WINDOW = 7`, no quotes |
| `KeyError: 'roll7'` | You skipped the cell that makes `roll7` | Run the B1 cell after filling `WINDOW` |
| `TypeError: unsupported operand…` | You did maths with text (e.g. `"7"`) | Numbers have no quotes |
| A ✅ check says ❌ for `CENTER` | You typed `"True"` with quotes | `CENTER = True` |
| Chart is flat or empty | The cell above it didn't run | Re-run the cells in order |
| Everything is weird | — | **Runtime → Restart session and run all** |

## Stuck? Climb the ladder

1. **Read the ❌ hint**: it usually says exactly what's wrong.
2. **Check this rule book's error table.**
3. **Ask your neighbour.**
4. **Ask the AI button** to *explain the error*. Paste your code and the error, never real data.
5. **Raise your hand.**

> 🏁 **Finished?** Run `scoreboard()`. 14 of 14 = 🏆. Then help someone near you.
