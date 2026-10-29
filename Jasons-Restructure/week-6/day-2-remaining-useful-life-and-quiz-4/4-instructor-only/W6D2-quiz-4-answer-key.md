# Quiz 4 Answer Key

> 🧑🏾‍🏫 **Instructor only.** Built from the original `Time-series/MCQ/week-06-mcq.csv` (unchanged). Options were reshuffled with a fixed seed (6203) so the correct letters are spread out: multiple-choice answers sit at A ×6, B ×7, C ×6, D ×7 (in the original, most answers were option B). The 4 True/False questions keep their original order.

| # | Answer | Correct option | What it tests | Level |
|---|---|---|---|---|
| 1 | **C** | The last observed value | Naive forecast | beginner |
| 2 | **B** | The same week one year (52 weeks) ago | Seasonal naive | beginner |
| 3 | **B** | On a typical week it was off by about 11 tickets | MAE in words | beginner |
| 4 | **C** | It repeated last year, when the network was much smaller | Seasonal naive came last | intermediate |
| 5 | **A** | Makes the forecast follow the latest week closely | Alpha in exponential smoothing | intermediate |
| 6 | **B** | False | Keeping a baseline | beginner |
| 7 | **A** | It must be known at the moment the forecast is made | The leak rule | beginner |
| 8 | **D** | df["tickets_raised"].shift(1) | shift direction | beginner |
| 9 | **D** | The 52-week lag does not exist for the first year | Rows lost to lag 52 | intermediate |
| 10 | **A** | So week 52 sits next to week 1 as a smooth cycle, using two columns instead of 52 | sin and cos | intermediate |
| 11 | **D** | 6.75 | Like with like | advanced |
| 12 | **A** | True | Coefficient sanity | intermediate |
| 13 | **B** | A range the true value should fall inside a stated share of the time | Prediction interval | beginner |
| 14 | **C** | forecast plus and minus 1.645 times the residual standard deviation | Building the band | intermediate |
| 15 | **C** | The interval is too narrow for a 90% claim | Coverage | beginner |
| 16 | **D** | The model was scored on weeks it had already been fitted to | Why too narrow | intermediate |
| 17 | **B** | False | Turning up z | advanced |
| 18 | **B** | Most likely around 71, plausibly 63 to 79; expect bigger misses at season changes | Communicating | intermediate |
| 19 | **D** | The time until the trend crosses its operational limit | Framing RUL | beginner |
| 20 | **C** | The slope and intercept of the best straight line | np.polyfit | beginner |
| 21 | **B** | 1 May 2025 | Battery call | intermediate |
| 22 | **B** | A planning figure with a range, re-estimated every year | Long reach | intermediate |
| 23 | **A** | It falls in discrete steps at each station-keeping burn | Propellant shape | intermediate |
| 24 | **A** | True | Time to intervention | beginner |
| 25 | **A** | Forecasting from past dates using only what was known then, and scoring against what came next | What backtesting is | beginner |
| 26 | **C** | The model is refit on everything before the cut and forecasts the next few weeks | Walk-forward | beginner |
| 27 | **D** | The spread across folds and when the bad folds occur | Report the spread | intermediate |
| 28 | **B** | Naive won five of six folds with lower mean error | Baseline backtest | advanced |
| 29 | **A** | 13 days early | Battery check | beginner |
| 30 | **D** | The warning time left to act shrinks | Accuracy versus lead time | intermediate |

## Marking it together (10 minutes)

1. Read out the letters; everyone marks their own paper.
2. Ask for hands up on each question. Any question that more than a third of the room got wrong, explain it again with the matching day's slide.
3. Map each topic back to its day: forecasting baselines → W5D2 · regression-based forecasting → W5D3 · uncertainty and prediction intervals → W5D3 · trend-to-threshold and remaining useful life → W6D2 · backtesting → W6D1 (Q29–30 → W6D2).

## Quick topic tally

| Topic | Questions |
|---|---|
| forecasting baselines | 1, 2, 3, 4, 5, 6 |
| regression-based forecasting | 7, 8, 9, 10, 11, 12 |
| uncertainty and prediction intervals | 13, 14, 15, 16, 17, 18 |
| trend-to-threshold and remaining useful life | 19, 20, 21, 22, 23, 24 |
| backtesting | 25, 26, 27, 28, 29, 30 |
