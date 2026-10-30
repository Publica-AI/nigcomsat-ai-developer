# W1D2 Rule Book: Charts That Don't Lie

> **Your goal today:** catch the daily *average* hiding a month of outages, compare six zones fairly, and write a title and a 4-sentence finding. Earn **14 green ✅ ticks**.
> Time: about 60 minutes. Keep this page open next to Colab.

## Before you start (2 minutes)

<ul class="check">
<li>Open <b>W1D2-exercise</b> in Colab → <b>File → Save a copy in Drive</b>. Work in the <i>Copy of…</i> tab.</li>
<li>Run <b>STEP 0</b> (Shift + Enter). Wait for <code>✅ Ready!</code></li>
<li>Run every cell <b>top to bottom</b>. Replace every <code>___</code>, run, read the ✅ or ❌.</li>
</ul>

## The 5 honest-chart rules (today's big idea)

| # | Rule | In code |
|---|---|---|
| 1 | **Draw the threshold** (the line that matters: 0 dB, the SLA %) | `plt.axhline(0, color="red", ls="--")` |
| 2 | **Title = the finding**, with a number | `plt.title("Link went down on 11 of 31 days")` |
| 3 | **Sensible axis**: counts start at 0; bounded % near the top may zoom in, **say the range** | `plt.ylim(0, None)` or `plt.ylim(96, 100)` |
| 4 | **One y-axis per chart.** Two units? Two stacked charts | `plt.subplots(2, 1, sharex=True)` |
| 5 | **Units on the axis** | `plt.ylabel("link margin (dB)")` |

## Pick the right daily summary

| Your question | Use | Why |
|---|---|---|
| “Did it ever go down?” / SLA breach | `.resample("D").min()` | the **worst moment** of each day |
| “Did it ever overheat?” | `.resample("D").max()` | the worst moment, other direction |
| “What's the typical level?” / trend | `.resample("D").mean()` | averages smooth away short events |

## The exercise, step by step

| Task | What you do | The tool you need |
|---|---|---|
| **A1** | Frequency code for hourly | `"h"` (lowercase, in quotes) |
| **A2** | Count outage hours | `(rf["link_margin_db"] < 0).sum()` |
| **A3** | Lowest daily average | `daily_mean.min()` |
| **A4** | Days with an outage, from daily minimums | `.resample("D").min()` |
| **A5** | Threshold at 0 + a title with a number | `THRESHOLD = 0`, `my_title = "…"` |
| **A6** | Which summary for an SLA question? | `"min"` |
| **A7** | Uplink power: cause or response? | `"response"` |
| **B1** | Pivot long → wide | `"week_start"`, `"region"`, `"uptime_pct"` |
| **B2** | Small multiples on the same y-axis? | `True` (no quotes) |
| **B3** | Lowest zone on average | `wide.mean().idxmin()` |
| **B4** | Zone that fell furthest from its own week 1 | `indexed.min().idxmin()` |
| **B5** | Axis for tickets? for availability? | `"zero"`, `"tight"` |
| **B6** | Order of the 4-sentence finding | Situation, Observation, Implication, Recommendation |
| **🌶️ Bonus** | Lightest rain that caused an outage | `rf.loc[condition, "rain_rate_mmhr"].min()` |

## Recipes you'll reuse

```python
# long -> wide (one column per group)
wide = df.pivot(index="week_start", columns="region", values="uptime_pct")

# small multiples on ONE shared y-axis
wide.plot(subplots=True, layout=(2, 3), sharey=True, figsize=(12, 5), legend=False)

# index every group to its own first value (= 100)
indexed = wide / wide.iloc[0] * 100
```

## The 4-sentence finding

1. **Situation**: what the unit does / the context.
2. **Observation**: what the data showed, **with a number**.
3. **Implication**: why it matters.
4. **Recommendation**: what to do next. **Always last.**

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `ValueError: Invalid frequency: H` | Old uppercase code | Use lowercase `"h"` |
| `AttributeError: 'Resampler' object has no attribute '___'` | The blank in A4 is still there | Type the method name: `min` |
| `KeyError: 'region'` | Column name typo | Copy names exactly from `vsat.head()` |
| `ValueError: Index contains duplicate entries, cannot reshape` | Wrong columns in `pivot` | index = the week, columns = the zone |
| `NameError: name 'daily_min' is not defined` | You skipped A4 | Run A3 and A4 first |
| `AssertionError: ✍️ Do … first` | A blank above is still empty | Go back, fill it, run again |
| Six tiny charts look equally bad | `sharey=False` | Use `sharey=True` |
| Everything is weird | — | **Runtime → Restart session and run all** |

## Stuck? Climb the ladder

1. Read the ❌ hint. 2. Check this rule book. 3. Ask your neighbour. 4. Ask the AI button to *explain the error* (code only, never real data). 5. Raise your hand.

> 🏁 **Finished?** Run `scoreboard()`. 14 of 14 = 🏆. Then write your 4-sentence finding about the six zones. Your trainer will pick a few to read out. 🎤
