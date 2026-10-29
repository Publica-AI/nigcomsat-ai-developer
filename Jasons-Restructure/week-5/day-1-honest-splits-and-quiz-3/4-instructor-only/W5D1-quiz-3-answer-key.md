# Quiz 3 Answer Key

> 🧑🏾‍🏫 **Instructor only.** Built from the original `Time-series/MCQ/week-05-mcq.csv` (unchanged). Options were reshuffled with a fixed seed (5103) so the correct letters are spread out: multiple-choice answers sit at A ×7, B ×6, C ×6, D ×7 (in the original, most answers were option B). The 4 True/False questions keep their original order.

| # | Answer | Correct option | What it tests | Level |
|---|---|---|---|---|
| 1 | **A** | It can notice when the relationship between channels breaks | What ML buys you | beginner |
| 2 | **D** | fit, predict (or transform), score | The one pattern | beginner |
| 3 | **D** | Rows are hours, columns are channels | The X matrix | beginner |
| 4 | **A** | Without scaling, channels with large ranges dominate distance-based methods | Why scale | intermediate |
| 5 | **B** | The scaler fitted on training rows is the one applied at prediction time | Pipelines | intermediate |
| 6 | **B** | False | Unsupervised | beginner |
| 7 | **C** | Something in the code is wrong and needs checking | Verifying generated code | intermediate |
| 8 | **C** | Two | Invisible faults | beginner |
| 9 | **C** | It needs few random cuts to isolate it | Isolation intuition | intermediate |
| 10 | **A** | A correlation break | EV02 | intermediate |
| 11 | **D** | More anomalous | Decision function | beginner |
| 12 | **A** | About 44 | Contamination | intermediate |
| 13 | **A** | Finding the operating modes such as sunlit and eclipse | Clustering use | intermediate |
| 14 | **B** | Per-channel z-scores against the training baseline | Explaining a flag | intermediate |
| 15 | **A** | True | When the baseline wins | advanced |
| 16 | **B** | Each row is judged on its own unless features carry history such as lags and rolling stats | Why engineer features | intermediate |
| 17 | **D** | Amplifier temperature relative to its RF drive level | temp_per_drive | beginner |
| 18 | **D** | About 22 sigma | EV04 in sigma | advanced |
| 19 | **C** | df[c].shift(-1) | Features that cheat | intermediate |
| 20 | **C** | Could I compute this at 14:00 using only what I knew at 14:00? | The feature test | beginner |
| 21 | **B** | Duplicates double-weight that channel because split dimensions are chosen at random | Redundant features | advanced |
| 22 | **B** | The longest window is 24 hours | Rows lost | beginner |
| 23 | **C** | Test hours have near-identical neighbours in the training set | Why random lies | beginner |
| 24 | **A** | assert tr.index.max() < te.index.min() | The assertion | intermediate |
| 25 | **D** | At least as long as the longest feature window | The embargo | intermediate |
| 26 | **D** | It gives a spread of scores instead of one possibly lucky number | Rolling origin | intermediate |
| 27 | **A** | True | Training only grows forwards | beginner |
| 28 | **B** | Same held-out period and the same scorer for both detectors | Fair comparison | beginner |
| 29 | **A** | From a period operations independently believe was quiet, stated in the write-up | Anomaly-specific trap | advanced |
| 30 | **A** | True | Recommending against your model | intermediate |

## Marking it together (10 minutes)

1. Read out the letters; everyone marks their own paper.
2. Ask for hands up on each question. Any question that more than a third of the room got wrong, explain it again with the matching day's slide.
3. Map each topic back to its day: the scikit-learn workflow → W4D2 · isolation forest and clustering → W4D2 · feature engineering from time series → W4D3 · temporal train-test discipline → W5D1.

## Quick topic tally

| Topic | Questions |
|---|---|
| the scikit-learn workflow | 1, 2, 3, 4, 5, 6, 7 |
| isolation forest and clustering | 8, 9, 10, 11, 12, 13, 14, 15 |
| feature engineering from time series | 16, 17, 18, 19, 20, 21, 22 |
| temporal train-test discipline | 23, 24, 25, 26, 27, 28, 29, 30 |
