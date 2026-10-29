# Quiz 1 Answer Key

> 🧑🏾‍🏫 **Instructor only.** Built from the original `Time-series/MCQ/week-03-mcq.csv` (unchanged). Options were reshuffled with a fixed seed (2603) so the correct letters are spread out: multiple-choice answers sit at A ×6, B ×7, C ×7, D ×6 (in the original, 74% of all answers were option B). The 4 True/False questions keep their original order.

| # | Answer | Correct option | What it tests | Level |
|---|---|---|---|---|
| 1 | **C** | The order of the rows carries information | What makes data a time series | beginner |
| 2 | **D** | Seasonality | The four components | beginner |
| 3 | **B** | False | Noise versus change | beginner |
| 4 | **A** | A cycle, because the length is not fixed in advance | Seasonality versus cycle | intermediate |
| 5 | **B** | To make missing days appear as NaN instead of silently disappearing | Declaring the frequency | intermediate |
| 6 | **D** | Convert both to the same time zone first | Mixed time zones | intermediate |
| 7 | **A** | For bounded measures that live near the top, with the range stated on the chart | Honest y-axis | intermediate |
| 8 | **B** | The daily minimum | Mean hides the outage | beginner |
| 9 | **A** | Small multiples on a shared y-axis | Comparing six regions | beginner |
| 10 | **C** | Which region fell furthest from its own starting point | Indexing to a baseline | intermediate |
| 11 | **A** | True | Chart titles | beginner |
| 12 | **A** | Recommendation | Four-sentence finding | beginner |
| 13 | **B** | It contains every weekday exactly once, so the weekend effect cancels | Why seven days | beginner |
| 14 | **C** | It reacts late, roughly half a window behind the event | Trailing windows | intermediate |
| 15 | **B** | False | Centred windows | intermediate |
| 16 | **B** | A seven-day mean genuinely does not exist until day seven | First rows are NaN | beginner |
| 17 | **A** | Follows the data closely and reacts fast | Exponential smoothing alpha | intermediate |
| 18 | **D** | Short outages vanish inside the average | Cost of smoothing | beginner |
| 19 | **A** | observed = trend + seasonal + residual | The decomposition equation | beginner |
| 20 | **D** | 7 | Choosing the period | intermediate |
| 21 | **C** | Multiplicative | Additive or multiplicative | intermediate |
| 22 | **C** | The residual | Where to investigate | beginner |
| 23 | **D** | Three | Minimum cycles | intermediate |
| 24 | **B** | Use STL with robust=True | Robust decomposition | advanced |
| 25 | **B** | The correlation of a series with a copy of itself shifted by one step | Definition | beginner |
| 26 | **C** | There is a weekly season with period 7 | Reading the correlogram | beginner |
| 27 | **C** | A trend | Slow decay | intermediate |
| 28 | **A** | True | Lag 0 | beginner |
| 29 | **B** | Neighbouring rows are near-copies, so the test set leaks into training | Random splits | intermediate |
| 30 | **D** | Mostly shared trend | Two trending series | advanced |

## Marking it together (10 minutes)

1. Read out the letters; everyone marks their own paper.
2. Ask for hands up on each question. Any question that more than a third of the room got wrong, explain it again with the matching day's slide.
3. Map each topic back to its day: structure → W1D1 · charts → W1D2 · rolling windows → W1D3 · decomposition → W2D1 · autocorrelation → W2D2.

## Quick topic tally

| Topic | Questions |
|---|---|
| structure of time-series data | 1, 2, 3, 4, 5, 6 |
| visualising time-series and data storytelling | 7, 8, 9, 10, 11, 12 |
| rolling windows and smoothing | 13, 14, 15, 16, 17, 18 |
| decomposing an operational time series | 19, 20, 21, 22, 23, 24 |
| autocorrelation in operational data | 25, 26, 27, 28, 29, 30 |
