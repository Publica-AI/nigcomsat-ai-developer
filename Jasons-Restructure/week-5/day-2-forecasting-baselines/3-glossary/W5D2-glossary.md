# W5D2 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🔮 Forecasting

### 🔮 Forecast
- **Plain English:** A guess about a value that hasn't happened yet, made **only** from what was known at the time.
- **Naija analogy:** Mama Put deciding how much rice to cook tomorrow from how many plates she sold this week.
- **Example:** Standing on 27 Oct 2025, guess the NOC tickets for each of the next 8 weeks.

### 📍 Forecast origin
- **Plain English:** The moment you stand at when you make the forecast. Everything after it is unknown.
- **Naija analogy:** The day you buy your ticket at the motor park: you don't yet know how the road will be.
- **Example:** Today's origin is the last training week, 27 Oct 2025.

### 🔭 Horizon
- **Plain English:** How far ahead you forecast, counted in steps (here, weeks).
- **Naija analogy:** "I'll pay you back in 8 weeks." The horizon is 8 weeks.
- **Example:** `H = 8`: forecast the 8 weeks from 3 Nov to 22 Dec 2025.

### 🙈 Blind forecast
- **Plain English:** Every week of the horizon is forecast from the origin, without using any real value that arrives later.
- **Naija analogy:** Writing your full betting slip before the first match kicks off. No changing it at half-time.
- **Example:** The forecast for 22 December can't use the real count from 15 December.

### 🔒 Hold-out (test weeks)
- **Plain English:** The last stretch of the series, locked away until the forecasts are made, then used to score them.
- **Naija analogy:** The sealed exam envelope that only opens in the hall (Week 5 · Day 1's "no expo").
- **Example:** The last 8 of the 104 weeks.

## 👵🏾 The baselines

### 📏 Baseline
- **Plain English:** A cheap, simple forecast that any fancier method must beat to earn its place.
- **Naija analogy:** "Can your new ₦25 million AI beat Grandma?"
- **Example:** Naive, seasonal naive, moving average, exponential smoothing, and today's winner, rate seasonal naive.

### 👵🏾 Naive forecast
- **Plain English:** Repeat the last value you saw for every future step.
- **Naija analogy:** Grandma: "Tomorrow go be like today."
- **Example:** 74 tickets for all 8 weeks (the count on 27 Oct 2025). MAE 11.25.

### 📅 Seasonal naive
- **Plain English:** Copy the value from exactly one season ago: for weekly data with a yearly pattern, 52 weeks back.
- **Naija analogy:** "Last December the market was full, so this December will be full too."
- **Example:** It copied 42–54 tickets from Nov–Dec 2024, when the network was 35% smaller. MAE 15.25, last place.

### 🧮 Moving average forecast
- **Plain English:** The average of the last few values (the window), held flat for the whole horizon.
- **Naija analogy:** Averaging your last 8 weeks of transport money to plan next week.
- **Example:** The mean of the last 8 training weeks: 77 tickets. MAE 14.25.

### 🫖 Exponential smoothing
- **Plain English:** A running "level" that each new value pulls part of the way towards itself. Recent weeks count most, old weeks fade away.
- **Naija analogy:** How your opinion of a bus driver updates: today's ride counts a lot, last year's ride a little.
- **Example:** With α = 0.3 the final level is 75.6. MAE 12.80.

### 🎚️ Alpha (α)
- **Plain English:** The smoothing setting between 0 and 1: how hard each new value pulls the level. Close to 1 = follows the latest week; close to 0 = very smooth and slow.
- **Naija analogy:** α = 0.9 is the friend who believes the last rumour he heard; α = 0.1 is the uncle who needs ten stories before he changes his mind.
- **Example:** α = 0.9 gives a level of 73.9, right next to the last week (74).

### 📐 Period (season length)
- **Plain English:** How many steps until the pattern repeats.
- **Naija analogy:** Harmattan comes back every 12 months, not every 7 days.
- **Example:** Weekly data with a yearly season: `period = 52`. There's no weekday pattern in a weekly series.

## 📏 Scoring

### 📏 MAE (mean absolute error)
- **Plain English:** Take each miss, drop the minus sign, average them. It's in the data's own unit.
- **Naija analogy:** "On a typical day, the bus came about 11 minutes late."
- **Example:** Naive missed by 21, 20, 16, 19, 6, 1, 5 and 2 tickets: average 11.25.

### ❌ Forecast error
- **Plain English:** Actual minus forecast for one step. Positive = forecast too low, negative = too high.
- **Naija analogy:** You budgeted ₦5,000 for fuel and spent ₦7,000: an error of ₦2,000.
- **Example:** Week of 3 Nov: actual 53, naive 74, error −21.

## ➗ The series and the trick

### 📈 Trend
- **Plain English:** The long, slow climb (or fall) under the wiggles.
- **Naija analogy:** Lagos traffic getting a little worse every year as the city grows.
- **Example:** Terminals grew from 1,200 to 2,181; tickets grew with them.

### 🌧️ Seasonality in steps
- **Plain English:** A pattern that repeats every year but switches on and off suddenly, instead of rising and falling smoothly.
- **Naija analogy:** The rainy season doesn't creep in: one week it's dry, the next week the gutters are full.
- **Example:** Tickets jumped +17 in the first week of April 2024 and +16 in April 2025, and dropped −15 in the first week of November 2024.

### 🎲 Noise
- **Plain English:** The week-to-week wobble that no forecast should try to chase.
- **Naija analogy:** Some weeks the queue at the bank is long for no reason anyone can explain.
- **Example:** The small ups and downs inside the rainy season.

### ➗ Rate (per-size number)
- **Plain English:** A count divided by the size of what produces it. Rates repeat when counts don't, because the growth is divided out.
- **Naija analogy:** NEPA bill **per room**, fuel **per kilometre**, jollof **per guest**.
- **Example:** Tickets per 1,000 terminals: January 25.6 in 2024, 25.9 in 2025.

### 🎯 Rate seasonal naive
- **Plain English:** Seasonal naive on the rate: last year's tickets per terminal × today's terminals.
- **Naija analogy:** Grandma, adjusted for the bigger family: "Last Christmas each guest ate two plates. This year we have 35% more guests."
- **Example:** 42 tickets ÷ 1,588 terminals × 2,131 terminals = 56.4 for the week of 3 Nov (actual 53). MAE 2.24 over the 8 weeks.

### 📡 Driver (exogenous variable)
- **Plain English:** A second series that pushes the one you forecast, and that you know at the moment you forecast.
- **Naija analogy:** The number of guests drives how much rice you cook.
- **Example:** Active VSAT terminals drive the number of tickets.

### 🎰 Lucky split
- **Plain English:** One test period on which a method scores well by chance, not by skill.
- **Naija analogy:** The man who won one bet and now calls himself a tipster.
- **Example:** The flat training average (57.9 every week) scored 7.77 here and "beat" four baselines. Week 6 · Day 1 tests it on many periods.
