# Quiz 1: Weeks 1–2

**30 questions · 20 minutes · just you.** Phones face down, notebooks closed, no AI tools. Circle **one** letter per question. True/False questions have two options.

Name: ______________________________ &nbsp;&nbsp; Unit: ______________________


## Structure of time-series data

**1.** Which property most clearly separates a time series from an ordinary table of records?

- **A.** It was exported from a database
- **B.** It has more than one numeric column
- **C.** The order of the rows carries information
- **D.** Every row has a unique ID

**2.** Ka-band availability drops every August during the rainy season. Which component is this?

- **A.** Noise
- **B.** Trend
- **C.** Cycle
- **D.** Seasonality

**3.** NOC tickets moving from 38 last week to 41 this week is a change the shift lead should investigate.

- **A.** True
- **B.** False

**4.** Capacity demand was strong for two years, weak for three, and is now rising again. Which component best describes this?

- **A.** A cycle, because the length is not fixed in advance
- **B.** Noise, because it is irregular
- **C.** Trend, because it is rising now
- **D.** Seasonality, because it repeats

**5.** Why do we call .asfreq("D") after setting a daily DatetimeIndex?

- **A.** To sort the rows by date
- **B.** To make missing days appear as NaN instead of silently disappearing
- **C.** To average duplicate readings
- **D.** To convert the timestamps to UTC

**6.** Telemetry is logged in UTC and the ticket system in WAT. What is the correct approach before joining them?

- **A.** Shift the tickets back by one day
- **B.** Ignore it, since the offset is only one hour
- **C.** Drop the time part and join on date only
- **D.** Convert both to the same time zone first


## Visualising time-series and data storytelling

**7.** When is a tight y-axis range (for example 97 to 100) the right choice?

- **A.** For bounded measures that live near the top, with the range stated on the chart
- **B.** Only for bar charts
- **C.** Never, the axis must always start at zero
- **D.** For quantities you can add up, such as tickets

**8.** To answer "did the link breach its SLA this month?", which daily summary of hourly link margin should you plot?

- **A.** The daily mean
- **B.** The daily minimum
- **C.** The daily median
- **D.** The monthly mean

**9.** What is the recommended way to compare weekly uptime across six regions?

- **A.** Small multiples on a shared y-axis
- **B.** Two y-axes with three regions on each
- **C.** Six lines on one axis in different colours
- **D.** A pie chart of average uptime

**10.** Dividing each region's uptime by its week-1 value and multiplying by 100 lets you answer which question?

- **A.** Which region has the most terminals
- **B.** Which week had the most rain
- **C.** Which region fell furthest from its own starting point
- **D.** Which region has the highest uptime

**11.** A report-ready chart title should state the finding, not just the variable name.

- **A.** True
- **B.** False

**12.** In the four-sentence finding, which sentence comes last?

- **A.** Recommendation
- **B.** Observation
- **C.** Implication
- **D.** Situation


## Rolling windows and smoothing

**13.** Why is a seven-day window the natural first choice for daily NOC tickets?

- **A.** It is the shortest window allowed
- **B.** It contains every weekday exactly once, so the weekend effect cancels
- **C.** It is the pandas default
- **D.** Tickets are only counted weekly

**14.** A trailing 30-day rolling mean is safe for live monitoring. What is its main cost?

- **A.** It removes the trend
- **B.** It cannot handle missing days
- **C.** It reacts late, roughly half a window behind the event
- **D.** It uses future data

**15.** A centred rolling window is a good input for a forecast because it lines up exactly with events.

- **A.** True
- **B.** False

**16.** s.rolling(7).mean() returns NaN for the first six days. What does that mean?

- **A.** The data has gaps
- **B.** A seven-day mean genuinely does not exist until day seven
- **C.** The series needs sorting
- **D.** The function failed

**17.** In .ewm(alpha=...).mean(), what does a high alpha do?

- **A.** Follows the data closely and reacts fast
- **B.** Smooths heavily and reacts slowly
- **C.** Removes the weekly cycle
- **D.** Ignores the most recent day

**18.** Why should SLA breaches never be reported from a smoothed line?

- **A.** Smoothed lines are harder to plot
- **B.** Smoothing adds noise
- **C.** Smoothing changes the units
- **D.** Short outages vanish inside the average


## Decomposing an operational time series

**19.** In additive decomposition, how does the observed series relate to its parts?

- **A.** observed = trend + seasonal + residual
- **B.** observed = trend x seasonal x residual
- **C.** observed = trend - seasonal
- **D.** observed = seasonal / trend

**20.** Which period should you pass when decomposing daily NOC tickets?

- **A.** 365
- **B.** 12
- **C.** 24
- **D.** 7

**21.** The seasonal swing grows as the level rises. Which model fits?

- **A.** Neither, use a straight line
- **B.** Either, they give the same result
- **C.** Multiplicative
- **D.** Additive

**22.** Which component should the NOC incident review look at for genuinely unusual months?

- **A.** The trend
- **B.** The raw series
- **C.** The residual
- **D.** The seasonal profile

**23.** How many full seasonal cycles does the course recommend at minimum before trusting a seasonal profile?

- **A.** Ten
- **B.** One
- **C.** Two
- **D.** Three

**24.** One catastrophic August makes every August look bad in the seasonal profile. What is the suggested fix?

- **A.** Use a multiplicative model
- **B.** Use STL with robust=True
- **C.** Switch to period=7
- **D.** Delete that August


## Autocorrelation in operational data

**25.** What is autocorrelation at lag 1?

- **A.** The average change per day
- **B.** The correlation of a series with a copy of itself shifted by one step
- **C.** The correlation between two different series
- **D.** The slope of the trend

**26.** A correlogram of daily throughput shows spikes at lags 7, 14 and 21. What does this tell you?

- **A.** The data is daily noise
- **B.** The series has no memory
- **C.** There is a weekly season with period 7
- **D.** There is a strong trend

**27.** A correlogram where every lag stays high and decays slowly usually indicates what?

- **A.** Pure noise
- **B.** A random split
- **C.** A trend
- **D.** A backlog cleared in cycles

**28.** The bar at lag 0 of a correlogram is always 1.0 and can be ignored.

- **A.** True
- **B.** False

**29.** Why is a random train/test split invalid on autocorrelated data?

- **A.** scikit-learn does not allow it
- **B.** Neighbouring rows are near-copies, so the test set leaks into training
- **C.** It is slower to compute
- **D.** It removes the seasonal profile

**30.** Suya sales and generator sales both rise steadily over time and correlate at 0.97, but their changes (.diff()) correlate at only 0.06. What explains the raw correlation?

- **A.** A real link between the two businesses
- **B.** The weekly roster
- **C.** Measurement error
- **D.** Mostly shared trend

