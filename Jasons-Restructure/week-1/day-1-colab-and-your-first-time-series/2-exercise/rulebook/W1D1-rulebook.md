# W1D1 Rule Book: Colab Bootcamp + Your First Time Series

> **Your goal today:** open the exercise in Colab, load 3 years of Ka-band availability data, and earn **12 green ✅ ticks**.
> Time: about 60 minutes. Keep this page open next to Colab.

## Before you start (2 minutes)

<ul class="check">
<li>Open <b>Google Chrome</b> and sign in to your Google account (top-right of Chrome).</li>
<li>Click the <b>Open in Colab</b> button for <code>W1D1-exercise</code>.</li>
<li><b>File → Save a copy in Drive.</b> A new tab opens. <b>Work only in that new tab.</b></li>
<li>Run <b>STEP 0</b> (click it, press <b>Shift + Enter</b>). Wait for <code>✅ Ready!</code></li>
</ul>

## The 7 golden rules

| # | Rule | Why |
|---|---|---|
| 1 | **Save a copy in Drive first** | The original can't be saved. Your work would vanish. |
| 2 | **Run cells top to bottom**, one at a time | Each cell uses what the cells above created. |
| 3 | **Shift + Enter** runs a cell and jumps to the next | Fastest way to move through the notebook. |
| 4 | **Replace every `___`** with your answer, then run that cell | `___` is the blank. The check only marks filled-in answers. |
| 5 | **Text goes in quotes**: `"timestamp"`, `"August"` | Without quotes Python thinks it's a variable name → `NameError`. |
| 6 | **After any restart, run STEP 0 again** | A restart wipes Colab's memory. |
| 7 | **Never paste real NIGCOMSAT data into the AI (Gemini) button** | Course data is synthetic and safe. Real telemetry is restricted. |

## The exercise, step by step

| Task | What you do | The tool you need |
|---|---|---|
| **A1** | Run the hello cell, then put your name in the message | Shift + Enter |
| **A2** | Hours in a year | `24 * 365` |
| **A3** | Restart, see `NameError`, fix it | Runtime → Restart session, then STEP 0 |
| **A4–A5** | Edit a text cell; find the 📁 Files panel | Double-click; left sidebar |
| **B1** | Is `timestamp` a date or text? | Read the `dtypes` output |
| **B2** | Name the time column | `"timestamp"` in quotes |
| **B3** | Count the days | `len(ka)` |
| **B4** | First and last day | `ka.index.min()`, `ka.index.max()` |
| **B5** | Reveal the 3 hidden missing days | frequency code for daily: `"D"` |
| **B6** | Find the worst day | `ka["availability_pct"].idxmin()` |
| **B7** | Chart title that states a finding | a sentence, in quotes |
| **B8** | Worst month on average | read the bar chart |
| **B9** | Trend, seasonality, cycle or noise? | the 4 characters (see glossary) |
| **B10** | 21:00 UTC on a Lagos clock | WAT = UTC + 1 |
| **🌶️ Bonus** | Quietest day for NOC tickets | copy the 3-line recipe |

## The 3-line recipe (you'll use it every day of this course)

```python
df = pd.read_csv(data_path("FILE_NAME"),
                 parse_dates=["TIME_COLUMN"],   # 1. text → real dates
                 index_col="TIME_COLUMN")       # 2. time becomes the row label
df = df.asfreq("D")                             # 3. declare the rhythm: "h" hourly, "D" daily, "W-MON" weekly, "MS" monthly
```

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `NameError: name 'ka' is not defined` | Colab forgot (restart), or you skipped a cell | Run STEP 0, then the cells above, top to bottom |
| `NameError: name 'timestamp' is not defined` | You forgot the quotes | Write `"timestamp"` |
| `NameError: name 'check' is not defined` | STEP 0 was not run | Run STEP 0 |
| `KeyError: 'timestamp'` | Wrong column name or spelling | Copy the name exactly from `head()` |
| `SyntaxError` | A typo: missing `)`, `"` or `,` | Compare with the recipe above, character by character |
| `✍️ Fill in the blank first` | A `___` is still there | Replace it, run again |
| Chart doesn't show | The cell didn't finish | Re-run it; make sure `plt.show()` is at the end |
| "This notebook was not authored by Google" | Normal warning | Click **Run anyway** |
| Everything is weird | — | **Runtime → Restart session and run all** |

## Stuck? Climb the ladder

1. **Read the ❌ hint**: it usually says exactly what's wrong.
2. **Check this rule book's error table.**
3. **Ask your neighbour** (explaining helps both of you).
4. **Ask the AI button** to *explain the error*. Paste your code and the error, never real data.
5. **Raise your hand.**

> 🏁 **Finished?** Run `scoreboard()`. 12 of 12 = 🏆. Then try the 🌶️ bonus and help someone near you.
