# W6D3 Rule Book: Project Clinic and Demo Day

> **Your goal today:** fix the last problems in your project at the clinic, deliver a **5-minute demo**, and hand in your report. In the notebook you rehearse the self-check on Ada's draft: **12 green ✅ ticks** to collect.
> Keep this page open next to Colab (or next to the training server).

## Before you start (2 minutes)

<ul class="check">
<li>Open <code>W6D3-exercise</code> in Colab → <b>File → Save a copy in Drive</b>.</li>
<li>Run <b>STEP 0</b>. Wait for <code>✅ Ready!</code></li>
<li>Run the ▶️ <b>self-check toolkit</b> cell. Everything below needs it.</li>
<li>Run every cell in order. Each ✍️ cell depends on the cells above it.</li>
</ul>

<div class="box bad" markdown="1">
**Real NIGCOMSAT data never goes into Colab, into an AI tool, or onto GitHub.** Parts A–D use a synthetic course file. Part E (your own data) is for the **training server** only: **File → Download → Download .ipynb**, then open it there.
</div>

## The exercise, step by step

| Task | What you do | The tool you need |
|---|---|---|
| **A1** | Run the hygiene report on Ada's export | the frequency for "weekly, on Mondays": `"W-MON"` |
| **A2** | Count what it found | (duplicates, missing): read the two ⚠️ lines |
| **A3** | Fix the export | `GAP_FILL = "interpolate"` (and say so in your report) |
| **A4** | Fix the leaky 4-week mean | `.shift(1)`: week *t* only sees the 4 weeks before it |
| **B1** | Split by time | `CUT = "2025-11-03"`: the first test week |
| **B2** | The comparison table | `TERMINALS = train["active_vsat_terminals"]` |
| **B3** | Measure Ada's "90%" band | `coverage(test_y, fc - 3, fc + 3)` |
| **B4** | The honest band | the 90% quantile of past misses: `Q = 0.9` |
| **C1** | Name the report files by date | `"%Y-%m-%d"`: year first, so files sort by date |
| **C2** | Schedule it for 07:00 every day | `"0 7 * * *"` |
| **D1** | Write the 4-sentence recommendation | one number in the Observation |
| **D2** | Write three honest limitations | misses · how late or how far · what you called normal |

## Your self-check toolkit (copy it into your project)

```python
hygiene(df, "W-MON")                        # index, order, repeats, holes, frequency, time zone
leak_test(lambda d: d["x"].shift(1), df)    # True = honest, False = it needed the future
# fails loudly if the split is not by time, or the gap is shorter than the embargo:
check_temporal_split(train.index, test.index, embargo="24h")
compare(actual, {"base": f1, "mine": f2})   # same weeks, same scorer, best first
coverage(actual, lower, upper)              # about 0.9 for an honest 90% band
recommendation(situation, observation, implication, action)
```

## Demo-day rules

| # | Rule | Why |
|---|---|---|
| 1 | **5 minutes, then 1 question.** The timer is the MC. | Everyone presents inside the hour |
| 2 | **Six beats:** problem 0:45 · data 0:45 · method 0:45 · honest test 1:00 · the tool live 1:00 · recommendation 0:45 | The honest test and the tool carry the most marks |
| 3 | **Show the tool live** from the training server, with a screenshot as backup | "Deployed" means it runs where your unit can use it |
| 4 | **One table** for the honest test: your method vs the baseline, same period, same scorer | Judges can't read three tables in a minute |
| 5 | **End on the recommendation**, not on "any questions?" | It's the sentence your unit head repeats |
| 6 | **Say one limitation out loud** | Unit heads trust the engineer who knows where the tool stops |
| 7 | **No real data on the projector** if outsiders are present | Show charts and summaries, not raw rows |
| 8 | **Two stars and a wish** for every other presenter | Kind, specific, about the work |

## Final pre-submission checklist

<ul class="check">
<li><b>Agreement:</b> my unit head's email names the process, the data and who the tool is for. It's in my submission.</li>
<li><b>Hygiene:</b> DatetimeIndex, declared frequency, one time zone (written down), gaps and duplicates handled and <b>explained</b>.</li>
<li><b>Honest chart:</b> sensible axis, the threshold drawn, a title that states the finding.</li>
<li><b>Season:</b> the period comes from a correlogram, and I decomposed with it.</li>
<li><b>Leak test:</b> every feature passes. Trailing windows and positive shifts only.</li>
<li><b>Split by time</b> with an <code>assert</code> and an embargo ≥ my longest feature window.</li>
<li><b>Baseline</b> on the same period, with the same scorer.</li>
<li><b>Spread / repeated calls / coverage</b> reported (folds for forecasts, several origins for remaining life, coverage for bands).</li>
<li>Detection: <b>event-level</b> precision and recall. <b>No accuracy figure.</b></li>
<li>Remaining life: a <b>window</b>, never a single date.</li>
<li>If the simple method won or tied, I <b>recommend it</b>.</li>
<li><b>Deployed</b> on the training server (dashboard or scheduled report). The README says how to run it.</li>
<li>Repository: code + <code>requirements.txt</code> + <code>README.md</code>. <b>No raw NIGCOMSAT data.</b></li>
<li>Report: 2–4 pages, the 4 sentences, 3 limitations, the AI-use note.</li>
<li>Demo rehearsed once with a timer: under 5:00.</li>
</ul>

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `✍️ Fill in the blank first` | A `___` is still there | Replace it, run the cell again |
| `✍️ Finish the task that makes … first` | You skipped an earlier task | Do that task, then come back |
| `NameError: name 'hygiene' is not defined` | You skipped the ▶️ toolkit cell | Run it (and STEP 0) |
| `❌ not a split by time: training reaches …` | The split is shuffled, or the dates are the wrong way round | Train = **before** the cut, test = **from** the cut |
| `❌ … forecasts but the test has … weeks` | Two methods were scored on different periods | Forecast the same weeks for every method |
| `ValueError: cannot reindex on an axis with duplicate labels` | `.asfreq()` on data with a repeated timestamp | Drop duplicates first: `df[~df.index.duplicated()]` |
| `ValueError: Invalid frequency: H` | The old hourly code (pandas 3 removed it) | Use `"h"` (and `"D"`, `"W-MON"`, `"MS"`) |
| **Demo:** the dashboard won't load | Server slot, VPN or port | Switch to your screenshot and keep talking; fix it after |
| **Demo:** you're at 4:30 and not at the recommendation | Too long on the data or method | Skip to the 4 sentences. Always. |
| Everything is weird | — | **Runtime → Restart session and run all** |

## Rules of thumb you'll keep forever

1. **Name the process and its owner.** A tool without an owner is a demo, not a deployment.
2. **Clean, then say what you cleaned.** Every gap filled is an assumption written down.
3. **Split by time, assert it, and score everything on the same period with the same scorer.**
4. **A range, checked.** A band is only as honest as its coverage on weeks it never saw.
5. **If the simple method wins, recommend it.** That's a respected result, not a failure.
6. **Four sentences, one number, one action.** Then stop talking.

> 🏁 **Finished?** Run `scoreboard()`. Then rehearse your own 5-minute demo with a partner and a timer.
