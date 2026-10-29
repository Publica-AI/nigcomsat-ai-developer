# W3D3 Rule Book: The Slow Creep: Drift and CUSUM

> **Your goal today:** write a CUSUM detector, catch the amplifier's step and a secret fault, find when the battery started ageing faster, and earn **14 green ✅ ticks**.
> Time: about 60 minutes. Keep this page open next to Colab.

## Before you start (2 minutes)

<ul class="check">
<li>Open <code>W3D3-exercise</code> in Colab, then <b>File → Save a copy in Drive</b>. Work only in the copy.</li>
<li>Run <b>STEP 0</b>. Wait for <code>✅ Ready!</code>. It also loads three helpers: <code>expected_temp</code>, <code>fade_rate</code>, <code>rolling_slope</code>.</li>
<li>Run every cell <b>top to bottom</b>. Part B needs your CUSUM from Part A.</li>
</ul>

## Today's 6 golden rules

| # | Rule | Why |
|---|---|---|
| 1 | **Name the shape first**: spike, level shift or drift | Each shape needs a different tool |
| 2 | **Take away what you already know** (season, drive level, ageing) before you watch | Otherwise the normal yearly swing hides the fault |
| 3 | **CUSUM line:** `S = max(0, S + leftover - k)` | Add today, minus the slack, never below zero |
| 4 | **Set k and h from σ**: `k = 0.5 * sigma`, `h = 5 * sigma` | σ = the normal wobble of the leftovers in a calm period |
| 5 | **Alarm date ≠ start date.** Start = the day after S was last 0 | CUSUM needs time to collect evidence |
| 6 | **Drift? Watch the slope, not the level** | The battery never crosses 95 Ah, but its speed doubles |

## The exercise, step by step

| Task | What you do | The tool you need |
|---|---|---|
| **A1** | Name three shapes | `"spike"`, `"level shift"`, `"drift"` |
| **A2** | Write the CUSUM line | `max(0, S + x - k)` |
| **A3** | Start day and alarm day of the toy example (h = 2) | read the printed table |
| **A4** | What is k for? | `"a"`, `"b"` or `"c"` in quotes |
| **B1** | Days above the whole-series 3σ ceiling | `(tw["twta_temp_c"] > ceiling).sum()` |
| **B2** | The step in units of local wobble | `(post.mean() - pre.mean()) / pre.std()` |
| **B3** | Leftovers after 12 May 2025 | `expected_temp(tw)`, then `resid["2025-05-12":].mean()` |
| **B4** | The two knobs | `0.5 * sigma` and `5 * sigma` |
| **B5** | First CUSUM alarm in 2025 | `S[S > h].index.min()` |
| **B6** | Secret fault: alarm date and start date | `Sp[Sp > h].index.min()` and `last_zero + pd.Timedelta(days=1)` |
| **C1** | Days below 95 Ah | `(cap < 95).sum()` |
| **C2** | Speed before and after April 2025 | `fade_rate(cap[:"2025-03-31"])`, `fade_rate(cap["2025-04-01":])` |
| **C3** | First day the rolling slope crosses the warning line | `WARNING_LINE = -3.0` |
| **🌶️ Bonus** | False alarms with a jumpy h = 2σ | count alarm days before `start` |

## The CUSUM recipe

```python
def cusum(values, k):
    S = 0
    out = []
    for x in values:              # x = today's leftover (actual - expected)
        S = max(0, S + x - k)     # add it, take away the slack, never below zero
        out.append(S)
    return out

S = pd.Series(cusum(resid.to_numpy(), k), index=resid.index)
first_alarm = S[S > h].index.min()                      # first day S is above h
last_zero = S[:first_alarm][S[:first_alarm] == 0].index.max()
start = last_zero + pd.Timedelta(days=1)                # best guess of when the change began
```

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `❌` on A2 with `None` in the list | the blank in the loop is still `___` | write `S = max(0, S + x - k)` |
| `TypeError: '>' not supported … NoneType` | a blank above is still empty | fill A2 / B4 first, then re-run |
| `AssertionError: ✍️ Do … first` | a cell needs an earlier answer | do the task it names, then run again |
| `NameError: name 'sigma' is not defined` | B3 didn't run successfully | fill `expected = expected_temp(tw)` and run B3 |
| CUSUM alarms on day 1 of January | you forgot `- k`, or used `h` where `k` belongs | k = 0.5σ goes **inside** the loop; h is only the alarm line |
| B6 start date is one day early | you gave `last_zero`, not the day after | `last_zero + pd.Timedelta(days=1)` |
| Battery "fires" or looks different | wrong file version | use the default `data_path("battery_health_daily")` (week-04) |
| Everything is weird | — | **Runtime → Restart session and run all** |

## 🏁 Final project · Checkpoint 2: 📥 Data in hand

Bring these to your trainer today (on **your** data, on NIGCOMSAT systems, not Colab):

<ul class="check">
<li>Your unit head's <b>email reply</b> agreeing the process, the data and who it's for</li>
<li>Your data loaded with a <code>DatetimeIndex</code>, one time zone, and <code>.asfreq()</code></li>
<li>Profiled: <b>rows, date range, gaps, duplicated timestamps</b></li>
<li>One honest plot with your <b>operational threshold</b> drawn on it</li>
<li>No raw data on GitHub; nothing restricted pasted into an AI tool</li>
</ul>

Next checkpoint: **Week 4 · Day 3: method drafted.**

## Stuck? Climb the ladder

1. **Read the ❌ hint.**
2. **Check the error table above.**
3. **Ask your neighbour.**
4. **Ask the AI button** to *explain the error*: paste code and error, never real data.
5. **Raise your hand.**

> 🏁 **Finished?** Run `scoreboard()`. 14 of 14 = 🏆. Then try the 🌶️ bonus.
