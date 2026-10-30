"""Weekly question banks for the LMS: one per course week, in exactly the format of the original
Time-series/MCQ files (a JSON list and a CSV with the same seven fields, plain ASCII).

Each week holds 30 questions: the 120 originals regrouped by the week that now teaches them, with the
errors found in review fixed and the old week numbers updated, plus new questions on what this course
adds. Correct answers are spread evenly over the options (in the originals 74% were option B).
The original files are never changed."""
from __future__ import annotations

import csv
import json
import random
from collections import Counter

from common import ORIGINALS, ROOT

FIELDS = ["title", "description", "type", "question", "options", "answer", "difficulty"]
MC, TF = "multiple choice", "True or False"
LETTERS = "ABCD"

# original quiz topic -> (our week, the day that teaches it)
TOPICS = {
    "structure of time-series data": (1, "W1D1"),
    "visualising time-series and data storytelling": (1, "W1D2"),
    "rolling windows and smoothing": (1, "W1D3"),
    "decomposing an operational time series": (2, "W2D1"),
    "autocorrelation in operational data": (2, "W2D2"),
    "what your alarm software already does": (3, "W3D1"),
    "statistical process control": (3, "W3D2"),
    "residual-based detection": (3, "W3D2"),
    "change points and drift": (3, "W3D3"),
    "evaluating a detector": (4, "W4D1"),
    "the scikit-learn workflow": (4, "W4D2"),
    "isolation forest and clustering": (4, "W4D2"),
    "feature engineering from time series": (4, "W4D3"),
    "temporal train-test discipline": (5, "W5D1"),
    "forecasting baselines": (5, "W5D2"),
    "regression-based forecasting": (5, "W5D3"),
    "uncertainty and prediction intervals": (5, "W5D3"),
    "backtesting": (6, "W6D1"),
    "trend-to-threshold and remaining useful life": (6, "W6D2"),
}
DAY_OVERRIDE = {("06", 29): "W6D2", ("06", 30): "W6D2"}   # backtesting questions about the battery call

# topic order inside each week's file (new topics included)
ORDER = {
    1: ["working in Google Colab", "structure of time-series data", "loading a time series with pandas",
        "visualising time-series and data storytelling", "rolling windows and smoothing"],
    2: ["decomposing an operational time series", "autocorrelation in operational data",
        "investigating a series end to end", "choosing your final project"],
    3: ["what your alarm software already does", "alarms with context", "statistical process control",
        "residual-based detection", "change points and drift"],
    4: ["evaluating a detector", "the scikit-learn workflow", "isolation forest and clustering",
        "feature engineering from time series"],
    5: ["temporal train-test discipline", "forecasting baselines", "regression-based forecasting",
        "uncertainty and prediction intervals"],
    6: ["backtesting", "trend-to-threshold and remaining useful life", "project clinic and demo day"],
}

# ----------------------------------------------------------------------------- fixes to original questions
# (original file week, question number) -> (kind, why, changed fields). Options are given in full when they change.
FIXES = {
    ("03", 5): ("reworded", 'It said "the code book", which participants never see.',
                {"question": 'Why do we call .asfreq("D") after setting a daily DatetimeIndex?'}),
    ("03", 30): ("corrected", 'On the real amplifier file the correlation only drops from 0.59 to 0.40 after differencing, '
                 'which is not a collapse. Replaced with the made-up suya example taught in W2D2 (0.97 to 0.06).',
                 {"question": "Suya sales and generator sales both rise steadily over time and correlate at 0.97, but their "
                              "changes (.diff()) correlate at only 0.06. What explains the raw correlation?",
                  "options": ["A real link between the two businesses", "Mostly shared trend", "Measurement error",
                              "The weekly roster"]}),
    ("04", 2): ("corrected", 'It said the floor fires on "all 46 eclipse hours". On the data it fires 18 times, all during eclipses.',
                {"question": "A fixed floor on battery state of charge (SoC < 82%) fires 18 times, every one of them during "
                             "an eclipse. Why is this a problem?"}),
    ("04", 4): ("reworded", "Week 4 of the original course is Week 3 here.",
                {"question": "Which three anomaly shapes appear in the Week 3 data?"}),
    ("04", 23): ("corrected", 'It said the fade rate "roughly doubled". The data shows -2.24 to -3.68 Ah a year: 1.6x faster.',
                 {"question": "From April 2025 the battery's capacity fade speeds up from about -2.2 to -3.7 Ah a year. "
                              "What should you monitor to detect this?"}),
    ("05", 1): ("reworded", "Week 4 of the original course is Week 3 here.",
                {"question": "According to the course, what does machine learning add over Week 3's per-channel methods?"}),
    ("05", 4): ("corrected", 'The option "It does not matter for isolation forest" was also true (the forest\'s scores with and '
                'without scaling correlate 0.99999999), so the question had two right answers.',
                {"question": "State of charge spans 77 to 100 while array current spans 0 to 29.8. Why does this matter "
                             "for a distance-based method such as k-means?",
                 "options": ["k-means rescales the columns itself, so it does not matter",
                             "Without scaling, channels with large ranges dominate distance-based methods",
                             "The values must be integers", "It breaks the timestamp index"]}),
    ("05", 6): ("reworded", "Week 5 of the original course is Week 4 here.",
                {"question": "The isolation forest in Week 4 is trained using the anomaly labels."}),
    ("05", 8): ("corrected", 'The original answer "Two" follows the label file, which only checks array current. A 3-sigma '
                "chart on each raw channel, on steady-sun hours, catches four; only EV04 needs two channels.",
                {"description": "Faults one channel can see",
                 "question": "On steady-sun hours, a 3-sigma chart on each raw channel catches how many of the five "
                             "labelled events (EV01 to EV05)?",
                 "options": ["All five", "Four", "Two", "None"], "answer": "Four"}),
    ("05", 11): ("reworded", 'It said "in the code book", which participants never see.',
                 {"question": "For an isolation forest, what does a lower decision_function score mean?"}),
    ("05", 15): ("reworded", "Week 4 of the original course is Week 3 here.",
                 {"question": "For simple single-channel spikes, a Week 3 control chart can still be the better tool than "
                              "an isolation forest."}),
    ("05", 18): ("corrected", 'The original answer "About 22 sigma" does not reproduce: the recipe gives 28.9 sigma, and the '
                 "same feature flags all 2,208 hours of October to December. The question now asks the lesson the course "
                 "teaches.",
                 {"question": "Raw amplifier temperature during EV04 never breaches its 3-sigma limit. A model of temperature "
                              "against drive level puts EV04 about 29 sigma out, yet the course uses the plain temp_per_drive "
                              "ratio instead. Why?",
                  "options": ["The model also flags every hour from October to December, so it is useless in service",
                              "29 sigma is too small to notice", "The model needs the anomaly labels to fit",
                              "The ratio puts EV04 even further out"],
                  "answer": "The model also flags every hour from October to December, so it is useless in service"}),
    ("05", 28): ("reworded", "It named the original course's Weeks 4 and 5.",
                 {"question": "What makes the comparison between the control chart and the isolation forest honest?"}),
    ("06", 14): ("reworded", 'It said "the code book", which participants never see.',
                 {"question": "How was the first 90% band in Week 5 built?"}),
    ("06", 29): ("reworded", 'W6D2 teaches a crossing as a window, so the question now says which definition it scores against.',
                 {"question": "The three-year battery call was 1 May 2025. Daily capacity first dipped below 80% on 14 May 2025. "
                              "Measured against that first dip, how far off was the call?"}),
}


# ----------------------------------------------------------------------------- new questions
def Q(day, title, desc, level, question, answer, *wrong):
    """A new multiple-choice question: the right answer first, then three wrong ones."""
    return {"day": day, "title": title, "description": desc, "type": MC, "question": question,
            "options": [answer, *wrong], "answer": answer, "difficulty": level}


def T(day, title, desc, level, statement, true: bool):
    return {"day": day, "title": title, "description": desc, "type": TF, "question": statement,
            "options": ["True", "False"], "answer": "True" if true else "False", "difficulty": level}


COLAB, LOAD = "working in Google Colab", "loading a time series with pandas"
DECOMP, ACF = "decomposing an operational time series", "autocorrelation in operational data"
LAB, PROJ = "investigating a series end to end", "choosing your final project"
CTX, DRIFT = "alarms with context", "change points and drift"
EVAL, FOREST = "evaluating a detector", "isolation forest and clustering"
SPLIT, BASE, BAND = "temporal train-test discipline", "forecasting baselines", "uncertainty and prediction intervals"
BACK, RUL, DEMO = "backtesting", "trend-to-threshold and remaining useful life", "project clinic and demo day"

NEW = {
    1: [
        Q("W1D1", COLAB, "Saving your work", "beginner",
          "You open the exercise with the Open in Colab button. What must you do first so your work is not lost?",
          "File > Save a copy in Drive, then work in the new tab", "Nothing, Colab saves the original automatically",
          "Download the notebook as a PDF", "Run every cell twice"),
        Q("W1D1", COLAB, "Run order", "beginner",
          "A cell fails with NameError: name 'ka' is not defined, although the cell that creates ka is further up. "
          "What is the most likely cause?",
          "That cell was skipped or Colab was restarted, so ka was never created in this session",
          "The data file is corrupt", "pandas is not installed in Colab", "Variable names cannot be two letters long"),
        T("W1D1", COLAB, "Restarting the session", "beginner",
          "After Runtime > Restart session, the variables you created are still in memory, so you can carry on from the next cell.",
          False),
        Q("W1D1", COLAB, "Text versus names", "beginner",
          "Which argument correctly tells pd.read_csv that the time column is called timestamp?",
          'index_col="timestamp"', "index_col=timestamp", "index_col=[timestamp]", "index_col=time_stamp"),
        Q("W1D1", COLAB, "The AI button and real data", "intermediate",
          "You are stuck on an error while working with a real NIGCOMSAT telemetry export. What may you share with "
          "Colab's AI (Gemini) button?",
          "Your code and the error message, never the real data", "The full export, so it can see the problem",
          "The first 100 rows only", "Nothing at all: the AI button is banned"),
        Q("W1D1", COLAB, "Fill-in-the-blank checks", "beginner",
          "A check cell says: Fill in the blank first. What does it mean?",
          "A ___ placeholder above is still there: replace it and run the cell again",
          "The notebook is broken and must be reopened", "Your answer is wrong", "Colab has run out of memory"),
        Q("W1D1", LOAD, "Reading dates as dates", "beginner",
          'What does parse_dates=["timestamp"] do in pd.read_csv?',
          "Turns the timestamp text into real dates that pandas can sort, slice and resample",
          "Deletes rows with missing dates", "Converts the times from UTC to WAT", "Sorts the file by its first column"),
        Q("W1D1", LOAD, "Frequency codes in pandas 3", "intermediate",
          'Old code runs .asfreq("H") and fails with ValueError: Invalid frequency: H. What is the fix?',
          'Use lowercase "h"', 'Use "HOUR"', "Delete the .asfreq line", 'Use "D" instead'),
        Q("W1D1", LOAD, "Finding when, not just what", "beginner",
          "You want the DATE of the worst Ka-band availability day, not the value. Which call gives it?",
          'ka["availability_pct"].idxmin()', 'ka["availability_pct"].min()', 'ka["availability_pct"].argmax()',
          "ka.index.min()"),
        Q("W1D1", LOAD, "Lagos time", "beginner",
          "An eclipse is logged at 21:00 UTC. What time is that on a Lagos clock (WAT)?",
          "22:00", "20:00", "21:00", "09:00"),
        Q("W1D3", LOAD, "Resample versus rolling", "intermediate",
          'What is the difference between s.resample("W").sum() and s.rolling(7).sum() on daily tickets?',
          "resample gives one value per calendar week; rolling gives a value every day, for the last 7 days",
          "They give identical results", "resample uses future days and rolling does not",
          "rolling only works on weekly data"),
        Q("W1D3", LOAD, "Window size on hourly data", "beginner",
          "Battery charge is logged every hour. Which rolling window covers exactly one day?",
          "rolling(24)", "rolling(1)", "rolling(7)", "rolling(60)"),
    ],
    2: [
        Q("W2D1", DECOMP, "Logs and growing swings", "intermediate",
          "The seasonal swing grows as the level rises, but you want to keep an additive decomposition. What can you do first?",
          "Take np.log() of the series", "Take .diff() of the series", "Drop the largest values", "Use period=1"),
        T("W2D1", DECOMP, "Empty ends of the trend", "beginner",
          "With period=12, the trend panel is empty for the first and last six months. This means the decomposition failed.",
          False),
        Q("W2D1", DECOMP, "Multiplicative needs positive values", "intermediate",
          'A multiplicative decomposition fails with "Multiplicative seasonality is not appropriate for zero and negative '
          'values". What is the fix?',
          "Use the additive model, or find out why the series has zeros", "Add period=7", "Sort the index",
          "Run the cell again"),
        Q("W2D1", DECOMP, "Choosing the period for monthly data", "beginner",
          "Monthly data follows Nigeria's yearly rainy season. Which period should you pass to the decomposition?",
          "12", "7", "24", "30"),
        Q("W2D2", ACF, "Shifting to make a lag", "beginner",
          "On daily data, what does s.shift(7) give you?",
          "The same weekday last week, lined up with today", "The next seven days", "The average of the last seven days",
          "Every seventh row only"),
        Q("W2D2", ACF, "Autocorrelation needs one column", "beginner",
          "bw.autocorr(lag=1) fails with AttributeError: 'DataFrame' object has no attribute 'autocorr'. What is the fix?",
          'Pick one column first: bw["throughput_gbps"].autocorr(lag=1)', "Use lag=0", "Sort the index",
          "Convert the table to a list"),
        Q("W2D2", ACF, "The period in the data's own units", "intermediate",
          "A correlogram of HOURLY battery charge has tall spikes at lags 24 and 48. What is the period?",
          "One day (24 hours)", "24 days", "One week", "Two hours"),
        Q("W2D2", ACF, "No memory", "beginner",
          "Every bar of a correlogram after lag 0 stays inside the shaded band. What does that mean?",
          "The series has no useful memory: it behaves like noise", "There is a strong weekly season",
          "There is a strong trend", "The data has gaps"),
        Q("W2D3", LAB, "Two files with the same name", "beginner",
          "battery_health_daily exists in both the week-03 and the week-04 data folders. What is the difference?",
          "week-03 is the clean version; week-04 has planted faults", "They are identical copies",
          "week-04 is hourly and week-03 is daily", "week-03 is in WAT and week-04 is in UTC"),
        Q("W2D3", LAB, "Profile before you plot", "beginner",
          "What should you check before drawing the first chart of a new file?",
          "The row count, empty cells and duplicate timestamps", "The colour scheme", "The file size in MB",
          "Nothing: the chart will show any problem"),
        Q("W2D3", LAB, "Finding the first crossing", "intermediate",
          "Which line gives the first day battery capacity drops below 97 Ah?",
          'bat.index[bat["est_capacity_ah"] < 97][0]', 'bat.index[bat["est_capacity_ah"] < 97][-1]',
          'bat.index[bat["est_capacity_ah"] > 97][0]', 'bat["est_capacity_ah"].min()'),
        Q("W2D3", LAB, "A window for the long-term trend", "intermediate",
          "Daily battery voltage dips in both eclipse seasons each year. You want a smoothed line that shows only the "
          "long-term trend. Roughly which window?",
          "About half a year to a year of days", "7 days", "24 days", "2 days"),
        Q("W2D3", LAB, "Duplicate timestamps", "intermediate",
          'df.index.duplicated().sum() returns 3. What happens if you call .asfreq("D") without fixing it?',
          'It fails with "cannot reindex on an axis with duplicate labels"', "pandas averages the duplicates for you",
          "Three days go missing without a warning", "Nothing: duplicates are harmless"),
        T("W2D3", LAB, "The Observation sentence", "beginner",
          "In the four-sentence finding, the Observation sentence must contain a number from the data.", True),
        Q("W2D3", PROJ, "A process, not a topic", "beginner",
          "Which is a good focus for the final project?",
          "The weekly battery-health review on the bus subsystem, with a named owner", "Satellite data",
          "Machine learning", "Everything the NOC logs"),
        Q("W2D3", PROJ, "Agreement from your unit head", "beginner",
          "Before you start the project, what must your unit head agree to by email?",
          "The process, the data and who the tool is for", "Your chart colours", "Your final grade",
          "The Python version"),
        T("W2D3", PROJ, "Real data in Colab", "beginner",
          "You may upload a real NIGCOMSAT data export to Google Colab without asking anyone, because Colab is free.",
          False),
        Q("W2D3", PROJ, "What goes on GitHub", "intermediate",
          "What belongs in your project repository?",
          "Code, requirements.txt and a README, with the data loaded from a path in a config file",
          "The raw data export, so others can rerun the analysis", "Screenshots of the raw data",
          "Nothing until demo day"),
    ],
    3: [
        Q("W3D1", CTX, "Combining conditions in pandas", "beginner",
          "You want hours where array current is below 20 A AND the satellite is sunlit. Which line works?",
          '(bus["solar_array_current_a"] < 20) & (bus["eclipse_flag"] == 0)',
          'bus["solar_array_current_a"] < 20 and bus["eclipse_flag"] == 0',
          'bus["solar_array_current_a"] < 20 & bus["eclipse_flag"] == 0',
          '(bus["solar_array_current_a"] < 20) & (bus["eclipse_flag"] == "0")'),
        Q("W3D1", CTX, "The not operator", "beginner",
          "In pandas, what does hot & ~after_eclipse select?",
          "Hours that are hot but NOT right after an eclipse", "Hours that are hot OR right after an eclipse",
          "Hours that are hot AND right after an eclipse", "Hours that are roughly hot after an eclipse"),
        Q("W3D1", CTX, "The hour after an eclipse", "intermediate",
          "Which expression is True for the hour right after an eclipse hour?",
          'bus["eclipse_flag"].shift(1) == 1', 'bus["eclipse_flag"].shift(-1) == 1', 'bus["eclipse_flag"] == 2',
          'bus["eclipse_flag"].diff() == 0'),
        Q("W3D3", DRIFT, "Dating the start of a change", "intermediate",
          "CUSUM first crosses h on 20 May. S was last at zero on 9 May. What is the best estimate of when the change began?",
          "10 May", "9 May", "20 May", "21 May"),
        Q("W3D3", DRIFT, "Take away what you already know", "intermediate",
          "Before running CUSUM on amplifier temperature, why do you subtract the expected temperature for the season "
          "and drive level?",
          "So the normal yearly swing does not look like a fault; only the leftovers are watched",
          "To make the numbers smaller", "Because CUSUM cannot handle decimals", "To remove the faults from the data"),
        T("W3D3", DRIFT, "Name the shape first", "beginner",
          "One detector works equally well on spikes, level shifts and drifts, so there is no need to name the shape first.",
          False),
    ],
    4: [
        Q("W4D2", FOREST, "Steady sun", "intermediate",
          "Fitted on every hour of the training months and judged on every hour, the isolation forest flagged 58 hours, "
          "all at 21:00 UTC (eclipse), and caught 1 of 5 events. Fitted and judged on steady-sun hours only, it caught "
          "4 of 5. What is the lesson?",
          "Rare is not broken: give the model context instead of hoping it works it out",
          "The forest is broken and must be replaced", "The eclipse hours are the real faults",
          "Raise contamination until every event is caught"),
        T("W4D2", EVAL, "Lucky catches", "intermediate",
          "If event_table shows a long event as caught, the detector must have recognised that fault.", False),
    ],
    5: [
        Q("W5D1", SPLIT, "The detector verdict", "intermediate",
          "On the held-out months, the 3-sigma chart on steady-sun hours with temp_per_drive caught both events with "
          "1 false alarm. The isolation forest on the same features caught both with 25. What should you recommend?",
          "The chart with temp_per_drive: the feature did the work, not the forest",
          "The forest, because machine learning is more advanced", "The forest, because it uses more trees",
          "Neither: retrain the forest on the held-out months"),
        Q("W5D2", BASE, "The rate seasonal naive", "intermediate",
          "Tickets per terminal repeat every year, while the network grew from 1,581 to 2,131 terminals over the year "
          "before the forecast. How does the rate seasonal naive forecast a week?",
          "Last year's tickets per terminal for that week x today's number of terminals",
          "Last year's ticket count for that week, unchanged", "Last week's count, repeated",
          "The average of every past week"),
        Q("W5D2", BASE, "Beat the best baseline", "intermediate",
          "On the 8 held-out weeks the MAEs were: naive 11.25, moving average 14.25, seasonal naive 15.25 and rate "
          "seasonal naive 2.24. A new model scores 9.0. What is the verdict?",
          "It has not earned its place: the rate seasonal naive is far better",
          "Deploy it: it beats naive", "Deploy it: it beats three of the four baselines",
          "MAE cannot compare these methods"),
        Q("W5D3", BAND, "Building an honest band", "advanced",
          "Which recipe gave a 90% band that covered 7 of the 8 held-out weeks?",
          "Forecast plus or minus the 90th percentile of walk-forward misses that include the season changes",
          "Forecast plus or minus 1.645 x the training residual standard deviation",
          "The 90th percentile of walk-forward misses from summer weeks only",
          "Raising z until 7 of the 8 held-out weeks fit"),
    ],
    6: [
        Q("W6D1", BACK, "Rolling origin", "beginner",
          "In a rolling-origin backtest, what happens at each origin?",
          "Using only the weeks before it, forecast the next h weeks blind and score them, then move one week on",
          "Shuffle the weeks and score a random block", "Refit on all 104 weeks and score the last 8",
          "Score the forecast on the weeks it was trained on"),
        Q("W6D1", BACK, "The horizon the user needs", "intermediate",
          "The NOC needs a month-ahead staff roster. Why can't the one-step regression, which uses last week's real "
          "count, make it?",
          "Four weeks ahead, last week's real count is not known yet", "Regression cannot forecast tickets",
          "It is too accurate", "Rosters must use seasonal naive"),
        Q("W6D1", BACK, "The backtest verdict", "advanced",
          "The backtest from every origin showed naive winning one week ahead and the rate seasonal naive winning four "
          "to eight weeks ahead. What does the course recommend?",
          "Naive for next week, the rate seasonal naive for 4 to 8 weeks ahead", "The regression for every horizon",
          "Seasonal naive for every horizon", "The rate seasonal naive for next week, naive for later weeks"),
        T("W6D1", BACK, "Fix the design first", "beginner",
          "It is fine to try several fold sizes and report the one that makes your model look best.", False),
        Q("W6D1", BACK, "Comparing methods across folds", "advanced",
          "Over six folds the mean MAEs were: rate seasonal naive 2.65, naive 3.13, regression 4.01 and seasonal naive "
          "17.8. The rate seasonal naive beat naive in 3 of the 6 folds. Which statement is honest?",
          "The rate seasonal naive has the lowest mean, but it wins only half the folds against naive, so report the spread",
          "The rate seasonal naive wins every fold", "The regression is best because it uses the most features",
          "Seasonal naive is best because tickets are seasonal"),
        Q("W6D2", RUL, "The three limits", "beginner",
          "Which limits does the course use for the battery, the amplifier and the propellant?",
          "80% capacity, -2 dB gain and 5 kg of propellant", "50% capacity, -10 dB gain and 0 kg of propellant",
          "95 Ah, 0 dB and 15 kg", "100% capacity, +2 dB and 5% of propellant"),
        Q("W6D2", RUL, "Defining the crossing", "intermediate",
          "Daily battery capacity first dips below 80% on 14 May 2025, the 30-day mean crosses on 20 Jun, and the last "
          "day above 80% is 24 Jul. What should you report?",
          "A window from mid-May to late July, saying which definition you score against",
          "14 May 2025, the first time it happened", "24 Jul 2025, the last possible date",
          "The average of the three dates, as a single day"),
        T("W6D2", RUL, "No crossing is an answer", "intermediate",
          "If day_of_threshold returns None, the safe move is to treat it as day 0, in case the limit is already crossed.",
          False),
        Q("W6D2", RUL, "Sanity-check with a simple sum", "intermediate",
          "Propellant stands at 101.93 kg, the reserve is 5 kg, and the satellite uses about 9.62 kg a year. Roughly how "
          "many years are left?",
          "About 10 years", "About 1 year", "About 20 years", "About 5 years"),
        Q("W6D2", RUL, "Why the calls come early", "advanced",
          "Measured against the 30-day mean crossing (20 Jun 2025), battery calls made from 1, 2, 3 and 4 years of data "
          "were all early. Why?",
          "The fade slows a little every year, so a straight line fitted on the past runs ahead of it",
          "The data has gaps", "The limit changed every year", "The calls were made in WAT instead of UTC"),
        Q("W6D2", RUL, "Where the wear happens", "intermediate",
          "Eclipse-season days are about a quarter of the battery's days, yet they carry about 43% of its capacity fade. "
          "What does that suggest?",
          "Eclipse-season discharge wears the battery faster than ordinary days", "The eclipse data is wrong",
          "The battery only fades at night", "Eclipses recharge the battery"),
        Q("W6D3", DEMO, "Demo timing", "beginner",
          "How long is each demo-day presentation?",
          "5 minutes, then 1 question", "20 minutes, with open questions", "As long as the slides take",
          "2 minutes, with no questions"),
        Q("W6D3", DEMO, "How to end", "beginner",
          "How should your demo end?",
          "On the recommendation, in plain words", 'On "Any questions?"', "On the code", "On the raw data table"),
        Q("W6D3", DEMO, "The honest-test slide", "intermediate",
          "What should the honest-test part of your demo show?",
          "One table: your method against the baseline, on the same period with the same scorer",
          "Three tables, one per metric", "Only your method's best score", "The accuracy on the training data"),
        T("W6D3", DEMO, "Real data on the projector", "beginner",
          "If people from outside NIGCOMSAT are in the room, show charts and summaries, not raw rows of real data.", True),
        Q("W6D3", DEMO, "Automatic penalties", "intermediate",
          "Which of these costs automatic marks in the final project?",
          "Reporting an accuracy figure for rare-event detection",
          "A model that loses to the baseline in a fair test, with the simpler method recommended",
          "A two-page report", "Using pandas instead of plain Python"),
        Q("W6D3", DEMO, "What deployed means", "intermediate",
          "What counts as deployed for the final project?",
          "A dashboard or scheduled report running on the training server, with a README that says how to run it",
          "A notebook shared in Google Drive", "Slides with screenshots", "Code emailed to the unit head"),
        Q("W6D3", DEMO, "Saying the limits", "beginner",
          "Why should you say one limitation of your tool out loud on demo day?",
          "Unit heads trust the engineer who knows where the tool stops",
          "To lower expectations so any result looks good", "Because the rubric asks for five limitations",
          "So the judges skip the honest test"),
    ],
}


# ----------------------------------------------------------------------------- assembling a week
def _originals():
    """Every original question with its source tag, fixes applied, grouped by our week."""
    weeks: dict = {w: [] for w in ORDER}
    for fw in ("03", "04", "05", "06"):
        for i, r in enumerate(json.load(open(ORIGINALS / "MCQ" / f"week-{fw}-mcq.json", encoding="utf-8")), 1):
            q = dict(r)
            q["options"] = r["options"].split("|")
            week, day = TOPICS[r["title"]]
            q["day"] = DAY_OVERRIDE.get((fw, i), day)
            q["source"] = f"original week-{fw} Q{i}"
            if (fw, i) in FIXES:
                kind, why, changes = FIXES[(fw, i)]
                q.update(changes)
                q["source"] += f", {kind}"
                q["why"] = why
            weeks[week].append(q)
    return weeks


def week_bank(week: int) -> list[dict]:
    """The week's 30 questions, ordered by topic, with the right answers spread evenly over the options."""
    qs = _originals()[week] + [dict(q, source="new") for q in NEW[week]]
    qs.sort(key=lambda q: ORDER[week].index(q["title"]))          # stable: originals first inside a topic
    rng = random.Random(1000 + week)
    mc = [q for q in qs if q["type"] == MC]
    targets = [0, 1, 2, 3] * (len(mc) // 4) + rng.sample([0, 1, 2, 3], len(mc) % 4)
    rng.shuffle(targets)
    for q, t in zip(mc, targets):
        others = [o for o in q["options"] if o != q["answer"]]
        q["options"] = others[:t] + [q["answer"]] + others[t:]
    _validate(week, qs)
    return qs


def _validate(week: int, qs: list[dict]):
    assert len(qs) == 30, (week, len(qs))
    descs = [q["description"] for q in qs]
    assert len(descs) == len(set(descs)), (week, [d for d in descs if descs.count(d) > 1])   # the originals never repeat one
    for q in qs:
        assert q["type"] in (MC, TF) and q["difficulty"] in ("beginner", "intermediate", "advanced"), q
        assert q["answer"] in q["options"] and len(set(q["options"])) == len(q["options"]), q["question"]
        assert q["options"] == (["True", "False"] if q["type"] == TF else q["options"]) and len(q["options"]) in (2, 4), q
        assert (q["type"] == TF) == (len(q["options"]) == 2), q["question"]
        for f in FIELDS:
            v = "|".join(q[f]) if f == "options" else q[f]
            assert v.isascii(), (f, v)                   # the originals are plain ASCII
        assert all("|" not in o for o in q["options"]), q["question"]
        assert "code book" not in q["question"].lower(), q["question"]


# ----------------------------------------------------------------------------- writing
def write_all():
    seen = set()
    for week in ORDER:
        qs = week_bank(week)
        for q in qs:
            assert q["question"] not in seen, q["question"]
            seen.add(q["question"])
        rows = [{f: ("|".join(q[f]) if f == "options" else q[f]) for f in FIELDS} for q in qs]
        out = ROOT / f"week-{week}" / "MCQ"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"week-{week}-mcq.json").write_text(json.dumps(rows, indent=4), encoding="utf-8")   # same layout as the originals
        with open(out / f"week-{week}-mcq.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        (out / "README.md").write_text(_readme(week, qs), encoding="utf-8")
        letters = Counter(LETTERS[q["options"].index(q["answer"])] for q in qs if q["type"] == MC)
        print(f"week {week} MCQ: {len(qs)} questions, answers {dict(sorted(letters.items()))}, "
              f"{sum(q['type'] == TF for q in qs)} true/false")


def _readme(week: int, qs: list[dict]) -> str:
    mc = [q for q in qs if q["type"] == MC]
    letters = Counter(LETTERS[q["options"].index(q["answer"])] for q in mc)
    n_orig = sum(q["source"] != "new" for q in qs)
    rows = "\n".join(
        f"| {i} | {q['title']} | {q['day']} | {'True/False' if q['type'] == TF else 'MC'} | {q['difficulty']} | "
        f"**{LETTERS[q['options'].index(q['answer'])] if q['type'] == MC else q['answer']}** | {q['source']} |"
        for i, q in enumerate(qs, 1))
    fixes = "\n".join(f"- **Q{i}** ({q['source'].split(', ')[0]}): {q['why']}"
                      for i, q in enumerate(qs, 1) if "why" in q)
    return (f"# Week {week} question bank\n\n"
            f"`week-{week}-mcq.json` and `week-{week}-mcq.csv` hold the same {len(qs)} questions for the LMS, in exactly the "
            "format of the original `Time-series/MCQ/` files: the fields `title`, `description`, `type`, `question`, "
            "`options` (separated by `|`), `answer` (the text of the right option) and `difficulty`.\n\n"
            f"- **{n_orig}** questions come from the original quizzes, regrouped by the week that teaches them. "
            f"**{len(qs) - n_orig}** are new and cover what this course adds.\n"
            f"- The right answers are spread over the options: "
            + ", ".join(f"{k} ×{letters[k]}" for k in LETTERS) + " (in the originals, 74% were option B).\n"
            "- The original files are unchanged. This file is generated by `_build/build.py mcq`: edit `_build/mcq.py`, "
            "not the JSON or CSV.\n\n"
            "| # | Topic | Taught on | Type | Level | Answer | Source |\n|---|---|---|---|---|---|---|\n"
            f"{rows}\n"
            + (f"\n## Changes to original questions\n\n{fixes}\n" if fixes else ""))
