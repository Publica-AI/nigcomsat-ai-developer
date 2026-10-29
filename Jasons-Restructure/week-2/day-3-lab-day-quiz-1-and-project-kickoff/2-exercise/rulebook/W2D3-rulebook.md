# W2D3 Rule Book: Lab Day + Quiz 1 + Pick Your Project

> **Today you drive.** One investigation from start to finish (**10 checks + 🌶️ bonus**), then Quiz 1, then your final-project kickoff.
> Fewer hints than usual: use this page plus your rule books and glossaries from Days 1–5.

## Before you start (2 minutes)

<ul class="check">
<li>Open <code>W2D3-exercise</code> in Colab → <b>File → Save a copy in Drive</b>. Work in the new tab.</li>
<li>Run <b>STEP 0</b>. Wait for <code>✅ Ready!</code></li>
<li>Have your Day 1–5 rule books and glossaries open in another tab.</li>
</ul>

## The 6 golden rules of an investigation

| # | Rule | Why |
|---|---|---|
| 1 | **Load the right file.** `battery_health_daily` exists in week-03 (clean) AND week-04 (planted faults) | Same name, different data. The wrong one gives the wrong story |
| 2 | **Profile before you plot** | Gaps and duplicates silently break everything after |
| 3 | **Threshold on the chart, finding in the title** | Your oga reads the title, not the axes |
| 4 | **Trailing windows only** | A centred window peeks at the future |
| 5 | **The process picks the period** | Monthly data with a yearly calendar → 12 (or half-year → 6) |
| 6 | **The correlogram confirms; it doesn't guess for you** | Measure the repeat, don't assume it |

## The investigation, step by step

| Task | What you do | Tool |
|---|---|---|
| **L1** | Choose the folder, time column and rhythm | `"week-03"`, the date column, `"D"` |
| **L2** | Rows, empty cells, duplicate timestamps | `len()`, `.isna().sum().sum()`, `.index.duplicated().sum()` |
| **L3** | First day capacity drops below 97 Ah | `bat.index[ condition ][0]` |
| **L4** | Chart with the line + a finding title | a sentence, in quotes |
| **L5** | Window (days) that swallows the eclipse dips | about half a year, or a full year |
| **L6** | How far the smoothed voltage fell | `smooth.dropna().iloc[0] - smooth.iloc[-1]` |
| **L7** | Decomposition period for monthly data | months in a year (half also works) |
| **L8** | The two months with the biggest seasonal bump | read the bar chart |
| **L9** | Tallest correlogram bar after lag 1 | read the plot or the printed list |
| **L10** | Your 4-sentence finding | Situation · Observation (with a number!) · Implication · Recommendation |
| **🌶️** | When do the two twin files first differ? | subtract the columns, filter, first date |

## The 4-sentence finding

| Sentence | Answers | Must have |
|---|---|---|
| **Situation** | What's going on? | the process and who runs it |
| **Observation** | What did the data show? | **a number** |
| **Implication** | So what? | the operational meaning |
| **Recommendation** | What should we do? | an action someone can take |

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `AssertionError: ✍️ Do L1 first…` | A setting above is still blank | Fill it in, run that cell, then this one |
| `KeyError: 'timestamp'` | This file's time column has a different name | Look at the CSV header: it's `date` |
| `ValueError: … must have 2 complete cycles` | The period is too big for 36 months | Use a period of 18 or less |
| `IndexError: index 0 is out of bounds` | Your filter matched nothing | Check the `<` direction and the line value |
| Smoothed line starts late | Normal: the first `WINDOW - 1` values are `NaN` | Use `.dropna()` before `.iloc[0]` |
| `NameError` | Colab forgot | Run STEP 0 and the cells above |

## Quiz 1 rules (20 minutes)

<ul class="check">
<li>Phones face down, notebooks closed, <b>no AI tools</b>.</li>
<li>One answer per question. True/False questions have two options.</li>
<li>Read the whole question; don't hunt for patterns in the letters.</li>
<li>We mark it together. Wrong answers are where you learn the most.</li>
</ul>

## Project kickoff: before you leave today

<ul class="check">
<li>Picked <b>one</b> brief (A–E).</li>
<li>Named a <b>process</b> with an <b>owner</b>, not just a topic.</li>
<li>Filled in the <b>project kickoff worksheet</b>.</li>
<li>Sent (or scheduled) the <b>email to your unit head</b>.</li>
</ul>

> 🏁 **Done with the lab?** Run `scoreboard()`, try the 🌶️ bonus, then help a neighbour with their finding.
