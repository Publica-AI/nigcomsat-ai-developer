# Quiz 4: Forecasting and remaining life

**30 questions · 20 minutes · just you.** Phones face down, notebooks closed, no AI tools. Circle **one** letter per question. True/False questions have two options.

Name: ______________________________ &nbsp;&nbsp; Unit: ______________________


## Forecasting baselines

**1.** What does the naive forecast predict for every future week?

- **A.** The value 52 weeks ago
- **B.** The overall average
- **C.** The last observed value
- **D.** Zero

**2.** For weekly ticket data with a yearly pattern, what does seasonal naive copy?

- **A.** The mean of the last 8 weeks
- **B.** The same week one year (52 weeks) ago
- **C.** The highest week on record
- **D.** The previous week

**3.** A forecast has an MAE of 11.25 tickets per week. What does that mean?

- **A.** It predicted 11.25 tickets
- **B.** On a typical week it was off by about 11 tickets
- **C.** Its error grew by 11.25 each week
- **D.** It was right 11.25% of the time

**4.** Ticket data is clearly seasonal, yet seasonal naive scored worst (MAE 15.25). Why?

- **A.** The season was misaligned by a week
- **B.** It cannot handle December
- **C.** It repeated last year, when the network was much smaller
- **D.** MAE penalises seasonal methods

**5.** In simple exponential smoothing, what does an alpha close to 1 do?

- **A.** Makes the forecast follow the latest week closely
- **B.** Adds a trend
- **C.** Makes the forecast very smooth and slow
- **D.** Doubles the horizon

**6.** A model that only ties the best baseline has earned its place and should be deployed.

- **A.** True
- **B.** False


## Regression-based forecasting

**7.** What is the one rule every forecasting feature must obey?

- **A.** It must be known at the moment the forecast is made
- **B.** It must be numeric
- **C.** It must be scaled
- **D.** It must correlate with the target

**8.** Which pandas call correctly creates last week's ticket count as a feature?

- **A.** df["tickets_raised"].rolling(1).mean()
- **B.** df["tickets_raised"].shift(-1)
- **C.** df["tickets_raised"].diff(-1)
- **D.** df["tickets_raised"].shift(1)

**9.** Why do 104 weeks become 52 usable rows in the feature table?

- **A.** Weekends are dropped
- **B.** Duplicates are removed
- **C.** Half the weeks are in the test set
- **D.** The 52-week lag does not exist for the first year

**10.** Why encode week of year as sin52 and cos52?

- **A.** So week 52 sits next to week 1 as a smooth cycle, using two columns instead of 52
- **B.** Because linear regression needs angles
- **C.** To scale the target
- **D.** To remove the trend

**11.** The regression scores MAE 5.85 using last week's real count. Made the same way, what does naive score?

- **A.** 11.25
- **B.** 15.25
- **C.** 2.84
- **D.** 6.75

**12.** If the terminals coefficient came out negative, it should be treated as a warning sign to investigate.

- **A.** True
- **B.** False


## Uncertainty and prediction intervals

**13.** What is a prediction interval?

- **A.** The forecast horizon
- **B.** A range the true value should fall inside a stated share of the time
- **C.** The time between forecasts
- **D.** The training period

**14.** How does the code book build the 90% band?

- **A.** the minimum and maximum of the training data
- **B.** forecast times 0.9
- **C.** forecast plus and minus 1.645 times the residual standard deviation
- **D.** forecast plus and minus 10%

**15.** The 90% band covered 5 of 8 held-out weeks. What is the correct conclusion?

- **A.** The interval is honest
- **B.** The forecast is perfect
- **C.** The interval is too narrow for a 90% claim
- **D.** Coverage does not matter

**16.** Training residual sd was 2.84 but held-out error sd was about 7. Why?

- **A.** A coding error
- **B.** The test set was too large
- **C.** z was too big
- **D.** The model was scored on weeks it had already been fitted to

**17.** Increasing z until the held-out coverage looks right is the honest fix for an overconfident interval.

- **A.** True
- **B.** False

**18.** Which statement communicates uncertainty honestly?

- **A.** The model is accurate to within 3 tickets
- **B.** Most likely around 71, plausibly 63 to 79; expect bigger misses at season changes
- **C.** Next week will have 71 tickets
- **D.** We are 90% confident it will be 66 to 75, though the band was never checked


## Trend-to-threshold and remaining useful life

**19.** In trend-to-threshold analysis, what is the remaining useful life?

- **A.** The age of the satellite
- **B.** The value predicted for tomorrow
- **C.** The slope of the trend
- **D.** The time until the trend crosses its operational limit

**20.** What does np.polyfit(x, y, 1) return?

- **A.** The crossing date
- **B.** The residuals
- **C.** The slope and intercept of the best straight line
- **D.** A smoothed series

**21.** Using only the first three years of data, when did the straight line predict battery capacity would cross 80%?

- **A.** 14 May 2025
- **B.** 1 May 2025
- **C.** 1 March 2025
- **D.** 5 May 2033

**22.** The amplifier call reaches about 9 years past the data. What should be reported?

- **A.** A precise date
- **B.** A planning figure with a range, re-estimated every year
- **C.** The battery date instead
- **D.** Nothing until it fails

**23.** Why is a straight line an approximation for propellant?

- **A.** It falls in discrete steps at each station-keeping burn
- **B.** It rises over time
- **C.** It has no trend
- **D.** It is measured in percent

**24.** Engineers should plan to act before the predicted crossing, not on the crossing date.

- **A.** True
- **B.** False


## Backtesting

**25.** What is backtesting?

- **A.** Forecasting from past dates using only what was known then, and scoring against what came next
- **B.** Reversing the time order
- **C.** Running the code twice
- **D.** Scoring a model on its training data

**26.** In a walk-forward backtest, what happens at each fold?

- **A.** Only the test set is changed
- **B.** The data is shuffled
- **C.** The model is refit on everything before the cut and forecasts the next few weeks
- **D.** The oldest data is deleted

**27.** Fold MAEs range from 1.27 to 7.67 with mean 4.01. What should you report?

- **A.** Only the last fold
- **B.** Only the mean
- **C.** Only the best fold
- **D.** The spread across folds and when the bad folds occur

**28.** Backtested on the same six folds, how did one-step naive compare with the regression?

- **A.** They tied every fold
- **B.** Naive won five of six folds with lower mean error
- **C.** Seasonal naive won
- **D.** Regression won all six folds

**29.** The three-year battery call was 1 May 2025. The real crossing was 14 May 2025. How far off was it?

- **A.** 13 days early
- **B.** 13 days late
- **C.** Exactly right
- **D.** 74 days early

**30.** As more data is used, the battery call gets more accurate. What is the trade-off?

- **A.** The data has more gaps
- **B.** The threshold changes
- **C.** The model becomes biased late
- **D.** The warning time left to act shrinks

