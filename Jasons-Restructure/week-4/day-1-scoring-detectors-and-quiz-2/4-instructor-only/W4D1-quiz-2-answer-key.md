# Quiz 2 Answer Key

> 🧑🏾‍🏫 **Instructor only.** Built from the original `Time-series/MCQ/week-04-mcq.csv` (that file is unchanged), with 3 questions edited: see *Changes from the original* below. Options were reshuffled with a fixed seed (4104) so the correct letters are spread out: multiple-choice answers sit at A ×7, B ×7, C ×6, D ×6 (in the original, most answers were option B). The 4 True/False questions keep their original order.

| # | Answer | Correct option | What it tests | Level |
|---|---|---|---|---|
| 1 | **A** | True | A threshold is a model | beginner |
| 2 | **D** | Every alarm is technically correct but operationally useless | Seasonal false alarms | beginner |
| 3 | **A** | Zero | Silent degradation | beginner |
| 4 | **D** | Spike, level shift and drift | Three anomaly shapes | beginner |
| 5 | **D** | It is a response to rain, so it leaks the answer | Leaking the answer | advanced |
| 6 | **A** | Where did that number come from? | Where thresholds come from | intermediate |
| 7 | **C** | Tampering | Common versus special cause | intermediate |
| 8 | **C** | Three standard deviations either side of the reference-period mean | Control chart parts | beginner |
| 9 | **B** | About 8 | Three sigma as a budget | intermediate |
| 10 | **B** | They are a different operating state and would widen the limits | Reference period | intermediate |
| 11 | **D** | Level shifts | Run rule 2 | intermediate |
| 12 | **B** | Fit a separate set of limits for each operating state | One chart per state | beginner |
| 13 | **A** | Observed value minus expected value | Predict, subtract, chart | beginner |
| 14 | **C** | A few extreme points cannot move them | Median and MAD | intermediate |
| 15 | **C** | To make it comparable to a standard deviation | The 1.4826 factor | advanced |
| 16 | **A** | True | The anomaly hides in its baseline | intermediate |
| 17 | **B** | Slow drift | What residuals miss | intermediate |
| 18 | **A** | Values all above zero | Is the residual clean | beginner |
| 19 | **A** | A level shift | Shift versus drift | beginner |
| 20 | **B** | Small deviations from target, so a sustained change becomes a clear slope | CUSUM idea | beginner |
| 21 | **C** | It is slack, so ordinary noise does not accumulate | The slack k | intermediate |
| 22 | **B** | False | Alarm date versus onset | intermediate |
| 23 | **B** | The rolling slope of capacity | Battery fade knee | intermediate |
| 24 | **C** | No single reading looks extreme against the whole series | TWTA level shift | advanced |
| 25 | **A** | About 99.87% | Why not accuracy | beginner |
| 26 | **A** | Of the real events, how many we caught | Recall | beginner |
| 27 | **D** | Precision | Precision | beginner |
| 28 | **D** | As one catch | Event-level scoring | intermediate |
| 29 | **B** | It turns a statistical choice into a decision an operations manager can make | Pricing false alarms | intermediate |
| 30 | **B** | False | Unusual is not wrong | advanced |

## Changes from the original

The same fixes are in the weekly question banks (`week-N/MCQ/`).

- **Q2** (corrected): It said the floor fires on "all 46 eclipse hours". On the data it fires 18 times, all during eclipses.
- **Q4** (reworded): Week 4 of the original course is Week 3 here.
- **Q23** (corrected): It said the fade rate "roughly doubled". The data shows -2.24 to -3.68 Ah a year: 1.6x faster.

## Marking it together (10 minutes)

1. Read out the letters; everyone marks their own paper.
2. Ask for hands up on each question. Any question that more than a third of the room got wrong, explain it again with the matching day's slide.
3. Map each topic back to its day: what your alarm software already does → W3D1 · statistical process control → W3D2 · residual-based detection → W3D2 · change points and drift → W3D3 · evaluating a detector → W4D1.

## Quick topic tally

| Topic | Questions |
|---|---|
| what your alarm software already does | 1, 2, 3, 4, 5, 6 |
| statistical process control | 7, 8, 9, 10, 11, 12 |
| residual-based detection | 13, 14, 15, 16, 17, 18 |
| change points and drift | 19, 20, 21, 22, 23, 24 |
| evaluating a detector | 25, 26, 27, 28, 29, 30 |
