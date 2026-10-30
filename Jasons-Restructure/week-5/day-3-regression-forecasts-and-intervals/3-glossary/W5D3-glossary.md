# W5D3 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 📈 Regression forecasts

### 📈 Regression forecast
- **Plain English:** A regression that predicts next week's value from columns that are all known before the week starts.
- **Naija analogy:** A danfo conductor guessing today's passengers from yesterday's crowd, last December's crowd and how many new estates opened on the route.
- **Example:** `LinearRegression` on lag1, lag52, terminals, sin52 and cos52 forecast the 8 held-out weeks with MAE 5.85.

### 🔒 The leak rule (Monday-morning test)
- **Plain English:** Every feature must be something you could compute **before** the week you're forecasting begins. If not, it leaks the future and the score is fake.
- **Naija analogy:** Predicting Saturday's match result on Friday with Sunday's newspaper in your bag.
- **Example:** `shift(1)` puts 27 Oct's 74 on 3 Nov's row (fine). `shift(-1)` puts 10 Nov's 54 there (a leak).

### 🕰️ Week-of-year clock (`sin52`, `cos52`)
- **Plain English:** Two columns that place each week on a circle, so the model sees the yearly cycle and week 52 sits next to week 1.
- **Naija analogy:** The hour hand: 11 o'clock and 1 o'clock are close, even though 11 and 1 are far apart as numbers.
- **Example:** `np.sin(2 * np.pi * woy / 52)` and `np.cos(...)`. A circle is smooth, so it can't make the rainy season's sudden on/off step.

### ⚖️ Coefficient
- **Plain English:** The weight a regression gives one column: how much the forecast moves when that column goes up by one, with the others held still.
- **Naija analogy:** The price per derica of garri: buy one more, pay that much more.
- **Example:** `terminals` +0.0231 per terminal, about +23 tickets a week per 1,000 terminals. Positive, as it should be.

### 🚨 Coefficient sanity check
- **Plain English:** Reading each coefficient's sign (+ or −) and asking whether it makes physical sense. A sign that makes no sense means something is broken until proven otherwise.
- **Naija analogy:** If the receipt says the more fuel you buy, the less you pay, check the receipt before celebrating.
- **Example:** A negative terminals coefficient would say "bigger network, fewer tickets": investigate.

### 🔢 Intercept
- **Plain English:** The starting number a regression adds before the weighted columns. It often has no meaning on its own.
- **Naija analogy:** The "call-out fee" a mechanic charges before he even touches the car.
- **Example:** −22.1 in today's model. Never read it alone.

## ⚖️ Comparing fairly

### 1️⃣ One-step-ahead forecast
- **Plain English:** A forecast for just the next period, made with the real value of the period before it.
- **Naija analogy:** Predicting tomorrow's bus fare when you already know today's.
- **Example:** The regression used last week's real count every week: a one-step forecast. One-step naive scored 6.75 on the same weeks.

### 🙈 Blind (multi-step) forecast
- **Plain English:** Forecasting several periods ahead from one starting point, without seeing any of the real values in between.
- **Naija analogy:** Planning the whole month's foodstuff on the first of the month.
- **Example:** Naive, seasonal naive and the rate seasonal naive all forecast 3 Nov – 22 Dec blind, standing on 27 Oct.

### ⚖️ Like with like
- **Plain English:** Only compare two forecasts on the same weeks, the same horizon and the same information.
- **Naija analogy:** Don't compare a student who wrote WAEC with one who wrote a class test.
- **Example:** "Half of naive's error" (5.85 vs 11.25) was unfair; like with like it's 5.85 vs 6.75. And the best baseline (2.24) beats both.

## ↔️ Honest ranges

### ↔️ Prediction interval (90% band)
- **Plain English:** A range around a forecast that the real value should land inside a stated share of the time. A 90% band should be right about 9 times in 10.
- **Naija analogy:** "30 to 90 minutes, Third Mainland permitting" instead of "I'm on my way".
- **Example:** The rate forecast for the week of 3 Nov: 56, band 49 to 63. Actual: 53.

### 🎯 Coverage
- **Plain English:** The share of held-out periods whose real value actually landed inside the band. It's how you check a band's promise.
- **Naija analogy:** The weatherman who says "90% chance of rain": count how often it actually rained.
- **Example:** The code book's band covered 5 of 8 weeks (62.5%): too narrow for a "90%" claim.

### 🏠 In-sample error (marking your own homework)
- **Plain English:** Misses measured on the same weeks the model was fitted to. They are always flattering.
- **Naija analogy:** Grading your own exam script with the marking guide on your desk.
- **Example:** Training misses had a spread of 2.84; misses on weeks it never saw had 6.99.

### 🚶🏾 Walk-forward misses (honest past errors)
- **Plain English:** For each past week, fit only on the weeks before it, forecast that week, and write down the miss. These are the misses the model really made before knowing the answer.
- **Naija analogy:** Checking a tipster's record on matches he predicted **before** kick-off, not after.
- **Example:** 32 walk-forward misses from 24 Mar 2025; the biggest, +15.1 on 7 Apr, is the week the rains arrived.

### 📊 Quantile (90th percentile)
- **Plain English:** The value that a given share of the numbers falls below. The 90th percentile of the misses: 90% of misses were smaller than this.
- **Naija analogy:** In a class of 10, the score that only the top student beats.
- **Example:** `np.quantile(np.abs(misses), 0.9)` = 8.20, so the honest band is forecast ± 8.20, and it covered 7 of 8.

### 🌧️ Calibration weeks
- **Plain English:** The past weeks whose misses you use to size a band. They must include the kind of trouble you'll be forecasting.
- **Naija analogy:** Testing a new umbrella in harmattan and declaring it rain-proof.
- **Example:** Misses from summer only (from 19 May) gave ± 3.33 and covered just 2 of 8 November–December weeks.

### 🎛️ Turning the knob (tuning on the test)
- **Plain English:** Changing a setting (like z or the band width) until the test result looks good. It uses the answers, so the score is fake: expo.
- **Naija analogy:** Moving the goalpost after the ball has been kicked.
- **Example:** Raising z until all 8 test weeks fit is not a fix. The width must come from misses before the test.

### 🗣️ The honest forecast sentence
- **Plain English:** Most likely value, a range, and the thing that could blow it up, in one sentence.
- **Naija analogy:** Amaka on the phone from the Island.
- **Example:** "Week of 3 Nov: most likely around 56, plausibly 49 to 63; expect bigger misses at season changes."

## 🏁 Final project

### ⚖️ Honest test (Checkpoint 4)
- **Plain English:** The final-project checkpoint where you bring a split by time and a table comparing your method with a simple baseline on the same period, with the same scorer.
- **Naija analogy:** A football friendly on neutral ground, same referee for both teams.
- **Example:** Today's table: each method, how far ahead, MAE, 90% band, coverage. The rate seasonal naive wins: say so.
