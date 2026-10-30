# W1D1 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 💻 Colab words

### 💻 Google Colab
- **Plain English:** A free website where you write and run Python. Google's computer does the work; yours just shows the screen.
- **Naija analogy:** A cyber café computer that lives in your browser, never runs out of fuel and never asks for ₦200 per hour.
- **Example:** You open `W1D1-exercise.ipynb` in Colab and run it without installing anything.

### 📓 Notebook
- **Plain English:** A document that mixes reading (text) and code you can run, in one page.
- **Naija analogy:** A recipe book where you can cook each step right on the page and taste it immediately.
- **Example:** Files ending in `.ipynb` are notebooks.

### 🧱 Cell (code cell / text cell)
- **Plain English:** One block in a notebook. A **code cell** runs Python; a **text cell** is just for reading.
- **Naija analogy:** One stop on a danfo route. You can't jump to Oshodi without passing the stops before it.
- **Example:** `print("Hello")` lives in a code cell. These instructions live in text cells.

### ⌨️ Shift + Enter
- **Plain English:** The keyboard shortcut that runs the current cell and moves to the next.
- **Naija analogy:** “Next please!” at the bank queue.
- **Example:** Click a cell, press Shift + Enter, see the output.

### 🔄 Runtime / session
- **Plain English:** The live connection to Google's computer, plus everything it currently remembers.
- **Naija analogy:** A phone call. Hang up (restart) and the other person forgets what you were saying.
- **Example:** *Runtime → Restart session* wipes the memory. Run STEP 0 again after it.

### 🧠 NameError
- **Plain English:** Python's way of saying “I don't know this name.” Usually you skipped a cell, restarted, or forgot quotes.
- **Naija analogy:** Calling someone “Chief” at a party when nobody has introduced him to you yet.
- **Example:** `NameError: name 'ka' is not defined` → run the cells above.

### 💾 Save a copy in Drive
- **Plain English:** Makes your own editable copy of the notebook in your Google Drive.
- **Naija analogy:** Photocopying the class notes before writing on them, so you don't scribble on the original.
- **Example:** *File → Save a copy in Drive*. Your copy lands in Drive → *Colab Notebooks*.

### 🤖 AI button (Gemini)
- **Plain English:** Colab's built-in AI helper. Great for explaining code and errors.
- **Naija analogy:** A very smart friend who talks a lot. Never tell him company secrets.
- **Example:** OK to ask: “Explain this error.” Never paste real NIGCOMSAT telemetry.

## ⏱️ Time-series words

### ⏱️ Time series
- **Plain English:** Measurements recorded one after another in time, where the **order matters**.
- **Naija analogy:** Your NEPA light diary: “06:00 light came, 09:00 light gone…” Shuffle it and it means nothing.
- **Example:** Daily Ka-band availability from 2023 to 2025.

### 🕐 Timestamp
- **Plain English:** The date and time attached to a reading.
- **Naija analogy:** The time printed on your POS receipt.
- **Example:** `2025-08-01T21:00` = 1 August 2025, 9pm UTC.

### 🥁 Cadence (frequency)
- **Plain English:** How often a reading is recorded: hourly, daily, weekly, monthly.
- **Naija analogy:** How often your landlord comes for rent: monthly? yearly? (Hopefully not weekly 😅)
- **Example:** `bus_power_telemetry` is hourly; `ka_band_availability` is daily.

### 🐼 pandas
- **Plain English:** The Python library for working with tables of data.
- **Naija analogy:** Microsoft Excel, but you control it by typing instructions, so it never gets tired.
- **Example:** `import pandas as pd`, then `pd.read_csv(...)`.

### 📋 DataFrame
- **Plain English:** pandas' name for a table: rows and named columns.
- **Naija analogy:** The class register: one row per student, one column per day.
- **Example:** `ka` is a DataFrame with 1,096 rows.

### 📄 CSV file
- **Plain English:** A plain-text table where commas separate the columns.
- **Naija analogy:** A list written in a jotter with commas instead of lines.
- **Example:** `date,tickets_raised` / `2024-01-01,8`

### 🗓️ parse_dates
- **Plain English:** Tells pandas “this column is a date, not just text.”
- **Naija analogy:** Telling the gateman, “this is not just any paper, it's my ID card.”
- **Example:** `pd.read_csv(..., parse_dates=["timestamp"])`

### 🧷 Index (DatetimeIndex)
- **Plain English:** The row labels of a table. When they're dates, pandas can do time tricks with them.
- **Naija analogy:** The page numbers of a book. Put dates there and you can jump straight to “August 2024.”
- **Example:** `index_col="timestamp"` makes the dates the index.

### 📏 .asfreq()
- **Plain English:** Declares the rhythm of your data (e.g. daily) and creates an empty slot for any missing period.
- **Naija analogy:** A class register with every school day printed on it. An absent student shows as a blank, not a missing page.
- **Example:** `ka.asfreq("D")`. Missing days appear as `NaN`.

### 🕳️ NaN
- **Plain English:** “Not a Number”. pandas' symbol for an empty or missing value.
- **Naija analogy:** The empty seat at a wedding where the guest didn't come.
- **Example:** After `.asfreq("D")`, the 3 deleted days show `NaN`.

### 🕵🏾 Gap
- **Plain English:** A period with no reading at all, e.g. a missing day.
- **Naija analogy:** The days in your diary when you were “too busy” to write. 🙈
- **Example:** In B5 we found 3 missing days in March 2024.

### 👯 Duplicate timestamp
- **Plain English:** The same time appearing twice: usually an export mistake.
- **Naija analogy:** Being charged twice on one POS transaction.
- **Example:** Two rows both saying `2024-03-06`.

### 🔍 Profiling
- **Plain English:** Quick checks before you trust a dataset: rows, date range, gaps, duplicates, missing values.
- **Naija analogy:** Inspecting a tokunbo car before you pay: engine, tyres, papers.
- **Example:** `len(ka)`, `ka.index.min()`, `ka.isna().sum()`.

### 🌍 UTC
- **Plain English:** The world's reference clock. Satellites and telemetry usually record in UTC.
- **Naija analogy:** The “master clock” everyone agrees on, like full-time at Old Trafford: the same moment for the whole world.
- **Example:** The eclipse happens at 21:00 UTC.

### 🇳🇬 WAT
- **Plain English:** West Africa Time, Nigeria's clock. Always **UTC + 1**, with no daylight saving.
- **Naija analogy:** Lagos time is UTC time plus one hour. (“African time” is another matter 😄)
- **Example:** 21:00 UTC = 22:00 WAT.

## 🛰️ Satellite words

### 🛰️ GEO (geostationary) satellite
- **Plain English:** A satellite about 36,000 km up that moves with the Earth's spin, so it stays over the same spot.
- **Naija analogy:** A security light on a high pole: it always shines on the same compound.
- **Example:** NigComSat-1R sits at 42.5° East.

### 📡 Transponder
- **Plain English:** A channel on the satellite that receives a signal and sends it back down. NigComSat-1R has 28 active ones.
- **Naija analogy:** One lane on a busy expressway. More lanes = more traffic carried.
- **Example:** `transponder_utilisation_monthly.csv` tracks how busy they are.

### 📶 Ka-band
- **Plain English:** A high-frequency radio band that carries lots of data but is very sensitive to rain.
- **Naija analogy:** A sports car: very fast, but it hates bad roads (here: heavy rain).
- **Example:** The Ka-band Nigeria spot beam in today's dataset.

### 🔦 Spot beam
- **Plain English:** A satellite beam aimed at one region, not the whole continent.
- **Naija analogy:** A torchlight pointed at one spot instead of a bulb lighting the whole room.
- **Example:** “Nigeria spot beam” in the `beam` column.

### ✅ Availability
- **Plain English:** The percentage of time a link worked properly.
- **Naija analogy:** Out of 24 hours, how many did your network actually give you full bars?
- **Example:** 99.6% availability = about 6 minutes of bad service in a day.

### 🌧️ Rain fade
- **Plain English:** Heavy rain absorbs the satellite signal, so quality drops or the link goes down.
- **Naija analogy:** DStv showing “No signal” during a heavy Lagos downpour.
- **Example:** The yearly dips in availability, worst in July and August.

### 🧪 Synthetic data
- **Plain English:** Made-up data designed to behave like the real thing. It's safe to share and safe to use with AI.
- **Naija analogy:** A mock exam: same style as WAEC, no real stakes.
- **Example:** All course datasets are synthetic, built to behave like NigComSat-1R.

## 🧩 The 4 characters in every series

### 📈 Trend
- **Plain English:** The long-term direction: up, down or flat.
- **Naija analogy:** Lagos population: more people every year.
- **Example:** Transponder utilisation climbing from about 50% to about 78%.

### 🌧️ Seasonality
- **Plain English:** A pattern that repeats on a **fixed calendar**: every day, every week, every year.
- **Naija analogy:** Harmattan every December, rainy season every year, traffic every weekday morning.
- **Example:** Ka-band availability dips every August.

### 🎢 Cycle
- **Plain English:** Ups and downs that repeat, but **with no fixed length**.
- **Naija analogy:** Business boom years and slow years. Nobody can tell you the exact date of the next boom.
- **Example:** Demand strong for 2 years, weak for 3, then rising again.

### 🎲 Noise
- **Plain English:** Random wobble that means nothing. Don't react to it.
- **Naija analogy:** Weighing yourself after eating amala: 2 kg up doesn't mean you're getting fat. 😄
- **Example:** NOC tickets 38 one week, 41 the next = the same week twice.
