# W4D1 Instructor Notes: Scoring a Detector + Quiz 2

> **The one idea for today:** *a detector is only as good as its score against the answer key, and the score must be recall and precision, with the rules written down first.* Accuracy is banned for rare events.

## At a glance

| | |
|---|---|
| **Length** | ~2 hours, including Quiz 2 (20 min + 10 min marking) |
| **Participants leave able to** | score any detector at event level, explain recall vs precision, refuse to quote accuracy, turn false alarms into engineer hours, say why rain fade isn't an anomaly |
| **Covers (original)** | Week 4 Code Book: *5. Anomaly ground truth*, *Scoring conventions*, *A reusable event-level scorer*; Week 4 quiz topic *evaluating a detector* (all 6 questions); Quiz 2 = the whole Week 4 MCQ file |
| **Datasets** | `week-04/data/telemetry_anomaly_labels.csv` (repaired on load), `bus_power_telemetry_hourly`, `twta_thermal_daily` (week-04), `battery_health_daily` (week-04), `rf_link_quality_hourly` |
| **Files you need open** | animated slides, your **solution** notebook, `W4D1-quiz-2-answer-key.pdf` |

## The day before: checklist

<ul class="check">
<li>Run the <b>solution</b> notebook top to bottom: 14 of 14 ✅ (about 30 seconds).</li>
<li>Print <code>2-exercise/quiz/W4D1-quiz-2.pdf</code> (one per person), <b>or</b> import <code>W4D1-quiz-2-google-forms.csv</code> into Google Forms / your LMS.</li>
<li>Print or open <code>4-instructor-only/W4D1-quiz-2-answer-key.pdf</code>. Don't share it until marking.</li>
<li>Remind the room: today the answer key is revealed, so anyone still finishing W3 detectors should do it before class.</li>
</ul>

## Run of show (2 hours)

| Time | Block | What happens | Slides |
|---|---|---|---|
| 0:00 | **Hook** | Musa vs Ade the mai-guards; vote; the 99.87% accuracy trap | 1–4 |
| 0:10 | **The answer key** | Six events on three lanes; the four scoring rules; recall vs precision | 5–8 |
| 0:25 | **Report cards** | Each detector scored on screen; the full report card | 9–15 |
| 0:35 | **Count the cost** | False alarms → hours; rain fade isn't an anomaly; recall-first vs precision-first | 16–19 |
| 0:40 | **Hands-on** | Parts A, B, C (50 min). Walk the room. | 21 |
| 1:30 | **Quiz 2** | 20 minutes, phones down, no AI | 20 |
| 1:50 | **Mark + wrap** | Swap and mark (letters from the key), re-teach any question a third of the room missed, recap | 22 |

If time is tight, run the quiz at the start of W4D2 instead.

## Explain it like this (in plain English)

- **Why an answer key?** Without it, "my detector works" is an opinion. With it, it's a number.
- **Event-level scoring:** we care whether we *noticed* each problem, not how many rows we painted red. One flag inside the event = caught; many flags = still one catch.
- **False alarm:** every flag outside a real event. Think of each one as a phone call to the duty engineer at 2 a.m.
- **Recall:** "Did we miss anything?" **Precision:** "When it pages me, is it real?" You always need both.
- **Accuracy lies** for rare events: 6 events in 4,706 readings means "always say no" scores 99.87%.
- **Conditioning beats widening:** the all-hours chart pages on every eclipse hour (normal physics). Add "only judge sunlit hours" and the false alarms vanish without losing a single catch.
- **Hours, not ratios:** "precision 0.06" means nothing to a manager. "31 hours a year of pointless pages, about 4 shifts" does.
- **Unusual ≠ anomaly:** rain fade is rare and dramatic, but it's physics with a known cause. Alarm on the *service* (margin below 0 dB) and use a rain gauge to explain it.

## The report card (computed from the data, same scorer for all)

| Detector | Watches | Caught | False alarms | Recall | Precision |
|---|---|---|---|---|---|
| State-of-charge floor < 82% | bus power (EV01–03) | 0/3 | 18 | 0.00 | 0.00 |
| 3σ control chart, all hours | bus power | 3/3 | 46 | 1.00 | 0.06 |
| 3σ control chart, sunlit only | bus power | 3/3 | 0 | 1.00 | 1.00 |
| Raw 3σ on temperature | TWTA (EV04–05) | 0/2 | 0 | 0.00 | — (never fired) |
| Residual 3σ (drive + season + age, fitted on 2024) | TWTA | 2/2 | 0 | 1.00 | 1.00 |
| CUSUM on the residual (k = 0.5, h = 5) | TWTA | 2/2 | 2 (21 Apr, 6 May 2025) | 1.00 | 0.50 |
| Fixed floor 95 Ah | battery (EV06) | 0/1 | 0 | 0.00 | — (never fired) |
| 🌶️ 90-day fade rate below −3 Ah/yr | battery | 1/1 | 0 | 1.00 | 1.00 (first alarm 2 May 2025, 31 days after the knee) |

Supporting numbers: sunlit array current mean 28.21 A, sd 0.594 A, band 26.43–29.99 A; all 46 false alarms are at 21:00 UTC (eclipse hour); the 3 dropouts read about 15.3–15.5 A. TWTA raw 3σ ceiling 69.8 °C vs highest day 68.2 °C (the EV04 spike); residual sd 0.378 °C; EV04 is 13σ in residual terms. Battery lowest day 95.39 Ah (never below 95).

## Slide talking points

| # | Say this | Ask this |
|---|---|---|
| 3 | "Neither guard is good. Today we learn the two numbers that prove it." | "Who would you hire?" (most pick Musa) |
| 4 | Point at the 6 red dots among 4,706. | "A detector that does nothing scores how much?" |
| 7 | Read the 4 rules aloud; get a thumbs-up from the room *before* anyone computes. | "Does flagging one day of EV05 count?" |
| 10 | Every red dot is a normal eclipse night: the battery doing its job. | "Is this alarm wrong or useless?" (useless) |
| 11 | Grey dots = eclipse, gold dots = real dropouts. One condition removes all the grey. | — |
| 12 | The raw series swings 7 °C a year, so a 2 °C shift hides inside it. The residual removes the swing. | — |
| 13 | CUSUM is more sensitive. Here that bought 2 false alarms and nothing else. | "So is CUSUM bad?" (no: it wins when the shift is small vs the noise) |
| 14 | No single battery day is strange; the *speed* changed. | "What kind of alarm would catch that?" |
| 17 | 46 × 2 × 20 min ≈ 31 h. | "What's your unit's real minutes-per-alarm?" |
| 18 | Only 12 of the 18 flagged hours were real outages; all 18 were rainy. | Quiz Q6: True or False? |
| 19 | NigComSat-1 (2008, solar-array failure): why power systems are recall-first. | — |

## Answer key

| Task | Answer | Common mistake → what to say |
|---|---|---|
| A1 | `1 - n_events / n_readings` = 0.9987 | `n_events / n_readings` (that's the error rate) |
| A2 | `"yes"`, `1` | Answering 2 for EV02 (rule 2: many flags = one catch) |
| A3 | `9 / 10` = 0.90, `9 / 200` = 0.045 | Swapping them: recall is about *real events*, precision about *alarms* |
| B1 | `SOC_FLOOR = 82` → caught 0/3, 18 false alarms | Expecting it to catch the dropouts: it's watching the wrong column |
| B2 | `K = 3` → 3/3, 46 false alarms | — |
| B3 | `== 0` → 3/3, 0 false alarms | Writing `== 1` (that keeps only eclipse hours) |
| B4 | `N_SIGMA = 3` → 2/2, 0 false alarms | — |
| B5 | `H = 5` → 2/2, 2 false alarms | Other H values give different counts; the check expects the standard 5 |
| B6 | `"EV06"` | — |
| B7 | `3` | — |
| C1 | `false_alarms_per_season * seasons_per_year * MINUTES_PER_FALSE_ALARM / 60` = 30.7 | Forgetting `/ 60` (gives minutes) |
| C2 | `n_real / n_flags` = 12/18 = 0.67 | — |
| C3 | `False` | Writing `"False"` with quotes is also accepted |
| 🌶️ | `RATE_LINE = -3.0` (anything that catches EV06 with 0 false alarms: below about −2.6 and above about −3.9) | Picking −2: fires on normal fade too |

## Quiz 2

- **Files:** `2-exercise/quiz/W4D1-quiz-2.pdf` (printable, no answers), `W4D1-quiz-2-google-forms.csv` (import), `4-instructor-only/W4D1-quiz-2-answer-key.pdf`.
- **Source:** the original `Time-series/MCQ/week-04-mcq.csv` (that file is unchanged), with three questions edited: Q2 and Q23 corrected to match the data, Q4 renumbered to our Week 3. The answer key lists them. Options reshuffled with a fixed seed (4104) so the correct letters are spread: multiple choice A ×7, B ×7, C ×6, D ×6; True/False A ×2, B ×2. (In the original file, most answers were option B.)
- **Topic → day:** alarm software → W3D1 · SPC and residuals → W3D2 · change points and drift → W3D3 · evaluating a detector → today.
- **Two questions are corrected to match the data** (their answers are unchanged):
  - **Q2**: the original said the SoC < 82% floor "fires on all 46 eclipse hours". It fires **18** times, all on eclipse hours, and the question now says so. The detector that fires on all 46 eclipse hours is the all-hours control chart (slide 11).
  - **Q23**: the original said the fade rate "roughly doubled". The question now gives the real numbers: about **−2.2 → −3.7 Ah/year** (×1.6).

## Troubleshooting

| Problem | Fix |
|---|---|
| `ParserError: Expected 8 fields in line 5, saw 9` | Someone loaded the key with `pd.read_csv`. Use `load_labels()` (STEP 0) |
| `ValueError: Invalid frequency: H` / bad tolerance | Old code using `"1H"`. Use `"1h"` |
| Scores of `events: 0` / `ZeroDivisionError` | The `source_file` string doesn't match the key exactly; copy it including `.csv` |
| A participant's B5 gives different false alarms | They changed k or H. The check expects k = 0.5, H = 5 |
| Fast finishers | 🌶️ slope alarm, then: "try K = 2 in B2 and B3: what happens to precision?" (sunlit-only jumps to 138 false alarms at K = 2) |

## Notes on the original material

- The original labels file **crashes on load** (`ParserError`): EV04's cause text has an unquoted comma. Our `load_labels()` / `common.read_labels()` repair it; the original file is untouched.
- The original scorer uses `tol="1H"`, which pandas 3 rejects. Ours uses `"1h"` / `"1D"`.
- The original code book (section 4) says a naive 3σ rule on C/N flags "roughly all 56 rainy hours, a 79% false-alarm rate". The data says **18** flags, **12** real, **6** false (33%). Slide 18 and C2 use the real numbers.
- The original code book (section 1) says the sunlit standard deviation is about 0.06 A. The data says **0.594 A** (band 26.43–29.99 A). The dropouts (~15.5 A) are still far outside it.
- The original's worked example scores a state-of-charge floor against *solar-array current* events: we keep that on purpose, because it shows a detector watching the wrong channel.
