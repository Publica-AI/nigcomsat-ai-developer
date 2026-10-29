# W3D1 Rule Book: Alarms That Cry Wolf

> **Your goal today:** test a fixed alarm on satellite power telemetry, watch it cry wolf every eclipse night, fix it with context, and earn **14 green ✅ ticks**.
> Time: about 60 minutes. Keep this page open next to Colab.

## Before you start (2 minutes)

<ul class="check">
<li>Open <b>W3D1-exercise</b> with the <b>Open in Colab</b> button.</li>
<li><b>File → Save a copy in Drive.</b> Work only in the new tab.</li>
<li>Run <b>STEP 0</b> (Shift + Enter). Wait for <code>✅ Ready!</code></li>
</ul>

## The 7 golden rules for today

| # | Rule | Why |
|---|---|---|
| 1 | **An alarm is a True/False column**: `alarm = bus["col"] < 20` | Then `.sum()` counts how many times it fires |
| 2 | **Combine conditions with `&`, and wrap each one in brackets** | `(a < 20) & (b == 0)`. Python's `and` does not work on columns |
| 3 | **`~` means "not"** | `hot & ~after_eclipse` = hot, but not right after an eclipse |
| 4 | **The flag is a number, not text**: `== 0`, not `== "0"` | `eclipse_flag` holds 0 and 1 |
| 5 | **Add context, don't widen the limit** | A wider limit also hides the real faults |
| 6 | **Always ask "where did that number come from?"** | A limit with no reason is a guess |
| 7 | **Rain is not a fault. Margin below 0 dB is.** | A detector must separate "raining" from "link down" |

## The exercise, step by step

| Task | What you do | The tool you need |
|---|---|---|
| **A1** | Count eclipse hours | `bus["eclipse_flag"].sum()` |
| **A2** | Count the 20 A floor alarms | `floor_alarm.sum()` |
| **A3** | How many of those are eclipse nights? | `(floor_alarm & (bus["eclipse_flag"] == 1)).sum()` |
| **A4** | Count the SoC < 82% alarms | `(bus["battery_soc_pct"] < 82).sum()` |
| **A5** | Which flag value means sunlit? | `0` or `1` |
| **B1** | Lower 3σ limit from sunlit hours | `sunlit.mean() - 3 * sunlit.std()` |
| **B2** | Sunlit hours below that limit | `(sunlit < low_limit).sum()` |
| **B3** | Temperature alarms right after eclipse | `(hot & after_eclipse).sum()` |
| **C1** | Rain alarms vs real outages | `cn_flags.sum()`, `(cn_flags & outage).sum()` |
| **C2** | Outages caught by a 2-hour rule | `two_in_a_row.sum()` |
| **C3** | Use uplink power as an input? | `"yes"` or `"no"` |
| **C4** | Name the three shapes | `"spike"`, `"level shift"`, `"drift"` |
| **C5** | Days below 95 Ah | `(bat["est_capacity_ah"] < 95).sum()` |
| **🌶️ Bonus** | Which date has two alarms? | read the A5 output |

## The alarm toolbox

```python
alarm = bus["solar_array_current_a"] < 20                 # a fixed limit = a True/False column
alarm.sum()                                               # how many hours it fires
alarm & (bus["eclipse_flag"] == 0)                        # context: only when sunlit
bus["eclipse_flag"].shift(1) == 1                         # "the hour right after an eclipse"
s.mean() - 3 * s.std()                                    # a 3-sigma limit from the data
outage & outage.shift(1, fill_value=False)                # "bad for 2 hours in a row"
bus.index[alarm].tolist()                                 # WHEN did it fire?
```

## When things go wrong: error → fix

| You see | It means | Fix |
|---|---|---|
| `ValueError: The truth value of a Series is ambiguous` | You used `and` / `or` between columns | Use `&` / `\|` and brackets: `(a < 20) & (b == 0)` |
| `TypeError: unsupported operand type(s) for &` | Missing brackets around a comparison | `(bus["eclipse_flag"] == 0)` in brackets |
| A count of `0` that should not be 0 | Compared a number with text (`== "0"`) | Use `== 0` |
| `NameError: name 'floor_alarm' is not defined` | You skipped A2, or restarted | Run STEP 0 and the cells above |
| `AssertionError: ✍️ Fill in SUNLIT first` | A5 still has `___` | Put `0` or `1` |
| `KeyError: 'eclipse_flag'` | Typo in the column name | Copy it exactly from `bus.head()` |
| C1 says wrong format | Gave one number instead of two | `check("C1", (n_flags, n_real))` |
| Everything is weird | — | **Runtime → Restart session and run all** |

## Stuck? Climb the ladder

1. **Read the ❌ hint.**
2. **Check this rule book's error table.**
3. **Ask your neighbour.**
4. **Ask the AI button** to explain the error. Course data only, never real telemetry.
5. **Raise your hand.**

> 🏁 **Finished?** Run `scoreboard()`. 14 of 14 = 🏆. Then try the 🌶️ bonus, and think: which alarm in *your* unit cries wolf?
