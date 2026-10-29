# Quiz 3: Machine learning

**30 questions · 20 minutes · just you.** Phones face down, notebooks closed, no AI tools. Circle **one** letter per question. True/False questions have two options.

Name: ______________________________ &nbsp;&nbsp; Unit: ______________________


## The scikit-learn workflow

**1.** According to the course, what does machine learning add over Week 4's per-channel methods?

- **A.** It can notice when the relationship between channels breaks
- **B.** It explains every alarm automatically
- **C.** It never produces false alarms
- **D.** It replaces the need for a reference period

**2.** Which method names make up the basic scikit-learn pattern?

- **A.** open, read, close
- **B.** load, run, plot
- **C.** train, test, deploy
- **D.** fit, predict (or transform), score

**3.** In the X matrix for hourly telemetry, what are the rows and columns?

- **A.** Rows are channels, columns are hours
- **B.** Rows are events, columns are labels
- **C.** Rows are days, columns are months
- **D.** Rows are hours, columns are channels

**4.** State of charge spans 77 to 100 while array current spans 0 to 29.8. Why does this matter?

- **A.** Without scaling, channels with large ranges dominate distance-based methods
- **B.** It breaks the timestamp index
- **C.** The values must be integers
- **D.** It does not matter for isolation forest

**5.** Why bind the scaler and model into one pipeline?

- **A.** It removes the need for a test set
- **B.** The scaler fitted on training rows is the one applied at prediction time
- **C.** Pipelines are required by pandas
- **D.** It makes the code shorter only

**6.** The isolation forest in Week 5 is trained using the anomaly labels.

- **A.** True
- **B.** False

**7.** You asked for contamination=0.01 on 8,760 hours and got 4,000 flags. What should you conclude?

- **A.** Contamination is ignored by the model
- **B.** That is the expected result
- **C.** Something in the code is wrong and needs checking
- **D.** The satellite is failing


## Isolation forest and clustering

**8.** How many of the five Week 5 labelled events are detectable by a single-channel method?

- **A.** None
- **B.** All five
- **C.** Two
- **D.** Three

**9.** How does an isolation forest decide that a point is anomalous?

- **A.** It is far from the cluster centre
- **B.** It has the highest value in its column
- **C.** It needs few random cuts to isolate it
- **D.** It matches a label

**10.** During EV02, array current is normal at about 27 A but state of charge sits near 93%. What kind of fault is this?

- **A.** A correlation break
- **B.** A seasonal effect
- **C.** A gap in the data
- **D.** A point spike

**11.** In the code book, what does a lower decision_function score mean?

- **A.** A missing value
- **B.** Higher battery charge
- **C.** More normal
- **D.** More anomalous

**12.** With contamination=0.005 on about 8,736 rows, roughly how many hours should be flagged?

- **A.** About 44
- **B.** About 4
- **C.** About 440
- **D.** About 4,000

**13.** What is clustering most useful for in this week's data?

- **A.** Finding the operating modes such as sunlit and eclipse
- **B.** Replacing the scaler
- **C.** Choosing the forecast horizon
- **D.** Computing recall

**14.** What is the cheapest way to explain why the detector flagged an hour?

- **A.** Rerun the model with a new seed
- **B.** Per-channel z-scores against the training baseline
- **C.** Show the decision tree
- **D.** Lower the contamination

**15.** For simple single-channel spikes, a Week 4 control chart can still be the better tool than an isolation forest.

- **A.** True
- **B.** False


## Feature engineering from time series

**16.** Why does the course say "the model cannot tell time"?

- **A.** It runs too slowly on hourly data
- **B.** Each row is judged on its own unless features carry history such as lags and rolling stats
- **C.** It ignores the eclipse flag
- **D.** It cannot read datetime columns

**17.** What does the temp_per_drive feature capture?

- **A.** The eclipse duration
- **B.** The daily mean temperature
- **C.** Battery temperature per hour
- **D.** Amplifier temperature relative to its RF drive level

**18.** Raw amplifier temperature during EV04 never breaches its 3-sigma limit. Modelled against drive level, roughly how far out does it sit?

- **A.** It is still inside
- **B.** 3 sigma
- **C.** 1 sigma
- **D.** About 22 sigma

**19.** Which feature leaks future information?

- **A.** df[c].rolling(24).mean()
- **B.** df.index.hour
- **C.** df[c].shift(-1)
- **D.** df[c].shift(1)

**20.** Which question should you ask of every feature?

- **A.** Does it improve the score?
- **B.** Is it highly correlated with the label?
- **C.** Could I compute this at 14:00 using only what I knew at 14:00?
- **D.** Is it a float?

**21.** Why prune feature pairs with correlation above about 0.98 before fitting an isolation forest?

- **A.** They reduce the number of rows
- **B.** Duplicates double-weight that channel because split dimensions are chosen at random
- **C.** They cause errors in pandas
- **D.** They make the scaler fail

**22.** The feature matrix loses 24 rows at the start. Why?

- **A.** Duplicate timestamps
- **B.** The longest window is 24 hours
- **C.** Eclipse hours are removed
- **D.** The labels start late


## Temporal train-test discipline

**23.** Why does a random split on hourly telemetry produce a score that is too good?

- **A.** The scaler is skipped
- **B.** The model is trained on more data
- **C.** Test hours have near-identical neighbours in the training set
- **D.** Random splits remove anomalies

**24.** Which line proves a temporal split has no overlap?

- **A.** assert tr.index.max() < te.index.min()
- **B.** assert tr.shape == te.shape
- **C.** assert te.isna().sum() == 0
- **D.** assert len(tr) > len(te)

**25.** How long should the embargo at the train/test boundary be?

- **A.** Exactly one week
- **B.** One row
- **C.** Half the test set
- **D.** At least as long as the longest feature window

**26.** What is the main advantage of rolling-origin validation over a single cut?

- **A.** It allows random shuffling
- **B.** It removes the embargo
- **C.** It uses less data
- **D.** It gives a spread of scores instead of one possibly lucky number

**27.** In rolling-origin (TimeSeriesSplit) validation, the training window only ever grows forwards in time.

- **A.** True
- **B.** False

**28.** What makes the Week 4 versus Week 5 comparison honest?

- **A.** Using accuracy for both
- **B.** Same held-out period and the same scorer for both detectors
- **C.** Training both on the labels
- **D.** Using the newest model

**29.** How should the clean reference period be defined in production, where there are no labels?

- **A.** From a period operations independently believe was quiet, stated in the write-up
- **B.** From the label file
- **C.** From the most recent month
- **D.** From a random sample

**30.** If an ML detector only ties the statistical baseline, recommending the simpler detector is a legitimate finding.

- **A.** True
- **B.** False

