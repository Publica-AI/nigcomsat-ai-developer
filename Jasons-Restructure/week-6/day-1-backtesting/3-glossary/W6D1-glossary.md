# W6D1 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🔁 Testing a forecast on the past

### 🔁 Backtesting
- **Plain English:** Replaying a forecasting method on the past, many times, using only what was known at each moment, and scoring it against what really happened next.
- **Naija analogy:** Before you pay Oga Tipster for VIP tips, your cousin checks his tips against every match from last season.
- **Example:** The Week 5 Day 3 regression replayed on six 4-week stretches of 2025, refitted each time.

### 📸 Lucky split
- **Plain English:** A single train/test split whose score is good (or bad) by chance, because of which weeks happened to land in the test.
- **Naija analogy:** The tipster's one WhatsApp screenshot of a 10-odds win. It says nothing about all the other weekends of the season.
- **Example:** On the last 8 weeks a flat training average scored MAE 7.77 and beat all four code-book baselines. From 45 origins it was the worst method (16.50).

### 🚶🏾 Walk-forward backtest (expanding window)
- **Plain English:** Cut the data at a point, train on everything before it, forecast the next few weeks, score them; then move the cut forward and do it again. The training block only grows.
- **Naija analogy:** Pretend it's June, make your call, check it; pretend it's July, make your call, check it. No time travel allowed.
- **Example:** `walk_forward_mae(tickets, make_features, X_COLS, step=4, h=4)` gives six fold MAEs: 2.46, 4.67, 2.81, 1.27, 7.67, 5.15.

### 🧩 Fold
- **Plain English:** One round of a backtest: one training block and the test weeks scored after it.
- **Naija analogy:** One match day in the season. A season has many.
- **Example:** Fold 5 trains on 42 weeks and tests 20 Oct – 10 Nov 2025.

### 🔄 Refit
- **Plain English:** Training the model again from scratch at each fold, on only the data before that fold's cut.
- **Naija analogy:** A coach who picks the team fresh each week from the latest form, not from last season's line-up.
- **Example:** The code book refits every 4 weeks. Refitting every week instead moves the regression from losing to naive (5 of 6 folds) to a near tie (2.96 vs 3.16).

## 🔭 Where you stand and how far you look

### 🧍🏾 Forecast origin (rolling origin)
- **Plain English:** The week you are standing in when you make the forecast. Everything before it may be used; nothing after it. A rolling-origin backtest makes a forecast from every week in turn.
- **Naija analogy:** Standing at the bus stop: you can see the danfos that have passed, not the ones still coming.
- **Example:** `rolling_origin(tickets, forecasters, h=8)` stands at 45 origins, from 30 Dec 2024 to 3 Nov 2025.

### 🔭 Forecast horizon
- **Plain English:** How far ahead a forecast reaches, here in weeks. Different questions need different horizons.
- **Naija analogy:** "Will it rain this evening?" and "Will it rain at my December wedding?" are different forecasts.
- **Example:** Next week's shift = 1 week; the month-ahead roster = 4 weeks.

### 1️⃣ One-step-ahead forecast
- **Plain English:** A forecast for the very next week only, made with last week's real value already known.
- **Naija analogy:** Guessing tomorrow's fuel price when you already know today's.
- **Example:** The regression uses `tickets_lag1`, so every forecast it makes is one step ahead. One-step naive is just `tickets_lag1` itself.

### 🙈 Blind (multi-step) forecast
- **Plain English:** Forecasting a whole block of weeks at the origin, without seeing any of the real values inside the block.
- **Naija analogy:** Planning the whole month's foodstuff on the 1st, without knowing what prices will do in the market.
- **Example:** The rate forecast made at the start of each fold covers all 4 weeks blind, and still scores the lowest mean MAE (2.65).

## 📊 Reporting it honestly

### 📊 Spread across folds
- **Plain English:** The range of scores from best fold to worst fold, and when the bad ones happened. It tells the user how much to trust the forecast, and when not to.
- **Naija analogy:** A striker who "averages a goal a game" but scored five in one match and none in the other nine.
- **Example:** The regression's fold MAEs run from 1.27 to 7.67 (mean 4.01); the worst fold contains 3 November, when tickets fell from 74 to 53.

### 📝 Four-sentence recommendation
- **Plain English:** The plain-language verdict for a manager: what to use, for which question, what not to use, and when to be careful.
- **Naija analogy:** What your mechanic tells you after the test drive: "Use the car for town, not for Abuja. Don't trust the spare tyre. The brakes go soft in the rain."
- **Example:** Naive for next week; the rate forecast for the month-ahead roster; not the regression; expect misses when the rains start or stop.
