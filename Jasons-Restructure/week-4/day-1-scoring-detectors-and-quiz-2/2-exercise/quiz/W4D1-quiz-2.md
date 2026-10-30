# Quiz 2: Week 3

**30 questions · 20 minutes · just you.** Phones face down, notebooks closed, no AI tools. Circle **one** letter per question. True/False questions have two options.

Name: ______________________________ &nbsp;&nbsp; Unit: ______________________


## What your alarm software already does

**1.** A fixed alarm threshold on a telemetry channel is already a simple anomaly-detection model.

- **A.** True
- **B.** False

**2.** A fixed floor on battery state of charge (SoC < 82%) fires 18 times, every one of them during an eclipse. Why is this a problem?

- **A.** Those hours are real faults that were missed
- **B.** The threshold is too low to fire
- **C.** The battery is failing
- **D.** Every alarm is technically correct but operationally useless

**3.** Battery capacity falls from about 103 Ah to 95.4 Ah over three years. How many times does a 95 Ah threshold fire?

- **A.** Zero
- **B.** Once
- **C.** 46
- **D.** Hundreds

**4.** Which three anomaly shapes appear in the Week 3 data?

- **A.** Trend, season and noise
- **B.** Spike, outage and gap
- **C.** Drift, cycle and duplicate
- **D.** Spike, level shift and drift

**5.** Why should uplink_power_dbm not be fed to the RF link detector as a feature?

- **A.** It is constant
- **B.** It is measured in the wrong unit
- **C.** It has missing values
- **D.** It is a response to rain, so it leaks the answer

**6.** Which question does the course ask of every existing alarm limit?

- **A.** Where did that number come from?
- **B.** How many sensors use it?
- **C.** Who installed it?
- **D.** Is it in volts?


## Statistical process control

**7.** Reacting to common-cause variation as if it were a special cause is called what?

- **A.** Backtesting
- **B.** Smoothing
- **C.** Tampering
- **D.** Detrending

**8.** In a control chart, what are the control limits?

- **A.** The engineering design limits
- **B.** The 5th and 95th percentiles of all data
- **C.** Three standard deviations either side of the reference-period mean
- **D.** The minimum and maximum ever recorded

**9.** In 2,880 hourly readings, roughly how many false alarms does a 3-sigma limit produce on normal data?

- **A.** Exactly 0
- **B.** About 8
- **C.** About 130
- **D.** About 1,000

**10.** Why are eclipse hours excluded from the reference period for solar array current?

- **A.** They contain faults
- **B.** They are a different operating state and would widen the limits
- **C.** There are too few of them
- **D.** They are missing data

**11.** Run rule 2 (nine consecutive points on one side of the centre line) is most sensitive to which anomaly?

- **A.** A frozen sensor
- **B.** Duplicate timestamps
- **C.** Single spikes
- **D.** Level shifts

**12.** What is the right fix when eclipse hours trigger false alarms on a control chart?

- **A.** Switch to 2-sigma limits
- **B.** Fit a separate set of limits for each operating state
- **C.** Widen the limits until eclipse hours fit
- **D.** Delete eclipse hours from the file


## Residual-based detection

**13.** What is a residual in residual-based detection?

- **A.** Observed value minus expected value
- **B.** The control limit
- **C.** The rolling standard deviation
- **D.** The raw reading

**14.** Why does the robust detector use a rolling median and MAD instead of mean and standard deviation?

- **A.** They remove the trend automatically
- **B.** They are faster to compute
- **C.** A few extreme points cannot move them
- **D.** They work only on hourly data

**15.** Why is MAD multiplied by 1.4826?

- **A.** To widen the limit to 4 sigma
- **B.** To account for weekends
- **C.** To make it comparable to a standard deviation
- **D.** To convert Celsius to Kelvin

**16.** A centred 61-day rolling mean can absorb part of the spike it is meant to detect, because the spike is inside the window.

- **A.** True
- **B.** False

**17.** On which anomaly shape is a rolling-model residual detector described as useless?

- **A.** Spike
- **B.** Slow drift
- **C.** Single-hour dropout
- **D.** Onset of a level shift

**18.** Which is NOT one of the checks for a clean residual?

- **A.** Values all above zero
- **B.** Mean near zero
- **C.** No autocorrelation left
- **D.** Constant spread over time


## Change points and drift

**19.** A step to a new level that then holds is called what?

- **A.** A level shift
- **B.** A cycle
- **C.** A spike
- **D.** A drift

**20.** What does CUSUM accumulate?

- **A.** The raw readings
- **B.** Small deviations from target, so a sustained change becomes a clear slope
- **C.** The number of alarms
- **D.** The squared errors of a forecast

**21.** In the CUSUM code, what is the role of k = 0.5 x sigma?

- **A.** It is the decision threshold
- **B.** It is the reset value
- **C.** It is slack, so ordinary noise does not accumulate
- **D.** It sets the reference period

**22.** The date CUSUM first alarms is the date the change actually began.

- **A.** True
- **B.** False

**23.** From April 2025 the battery's capacity fade speeds up from about -2.2 to -3.7 Ah a year. What should you monitor to detect this?

- **A.** Eclipse minutes
- **B.** The rolling slope of capacity
- **C.** The cycle count
- **D.** The daily capacity level against 95 Ah

**24.** The May 2025 TWTA shift is about 6.9 sigma against local spread. Why does a single-point 3-sigma rule miss it?

- **A.** The data has gaps
- **B.** The rule only works on hourly data
- **C.** No single reading looks extreme against the whole series
- **D.** It happened at night


## Evaluating a detector

**25.** With 6 events in about 4,700 observations, what accuracy does a detector that never fires score?

- **A.** About 99.87%
- **B.** About 0.13%
- **C.** Exactly 100%
- **D.** About 50%

**26.** What does recall measure?

- **A.** Of the real events, how many we caught
- **B.** How fast the detector runs
- **C.** How many hours were scored
- **D.** Of our alarms, how many were real

**27.** Which metric answers "when the system pages the duty engineer, how often is something really there?"

- **A.** Coverage
- **B.** Accuracy
- **C.** Recall
- **D.** Precision

**28.** Under event-level scoring, how is a seven-month level shift counted if the detector flags it on one day?

- **A.** As a false alarm
- **B.** As a miss
- **C.** As 233 catches
- **D.** As one catch

**29.** Why does the course convert false alarms into shift hours?

- **A.** Because recall is measured in hours
- **B.** It turns a statistical choice into a decision an operations manager can make
- **C.** To satisfy the SLA
- **D.** To pay overtime

**30.** In the RF file, every rain-fade excursion should be raised as an anomaly because it is statistically unusual.

- **A.** True
- **B.** False

