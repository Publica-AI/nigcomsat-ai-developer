# W1D3 Glossary: today's new words

Every new word from today: what it means, a Naija way to remember it, and an example from the course.

## 🌊 Smoothing words

### 🌊 Rolling window
- **Plain English:** A fixed number of rows that slides along the series one row at a time. You calculate something (usually the average) inside it.
- **Naija analogy:** A danfo with exactly 7 seats: every time one passenger enters at the front, the oldest one drops at the back.
- **Example:** `tk["tickets_raised"].rolling(7).mean()`

### 🧮 Moving (rolling) average
- **Plain English:** The average of the last N values, recalculated every day as the window moves forward.
- **Naija analogy:** Your average fuel spend over the last 7 days. One big fill-up on Monday doesn't make you panic.
- **Example:** The 7-day average of NOC tickets sits around 6 a day in the dry season.

### 📏 Window size
- **Plain English:** How many rows go into each calculation. Bigger = smoother but slower.
- **Naija analogy:** How many days of gossip you collect before you believe a rumour.
- **Example:** 3, 7 and 30-day windows on the same ticket data.

### 🌀 Smoothing
- **Plain English:** Removing the small, fast wiggles so the slower, real movement is easier to see.
- **Naija analogy:** Ironing a shirt: the shape is still there, the creases are gone.
- **Example:** The 7-day line shows the rainy-season rise hidden inside the daily zig-zag.

### 🎶 Weekly rhythm (day-of-week effect)
- **Plain English:** A pattern that repeats every 7 days because people work Monday to Friday.
- **Naija analogy:** Lagos traffic: wahala on weekdays, free roads on Sunday morning.
- **Example:** Weekdays average about 7 tickets, weekends about 3.4.

## ⏳ Window position words

### ⬅️ Trailing window
- **Plain English:** A window that ends today and only looks at the past. pandas does this by default.
- **Naija analogy:** Driving using only your rear-view mirror: safe information, but always a bit late.
- **Example:** `s.rolling(30).mean()` is trailing.

### 🔮 Centred window
- **Plain English:** A window with today in the middle: half the days are in the past, half in the **future**.
- **Naija analogy:** Marking a WAEC script after you've seen the answer sheet. Looks perfect, but it's cheating if you use it live.
- **Example:** `s.rolling(30, center=True).mean()` is empty for the last 15 days.

### ⏰ Lag (delay)
- **Plain English:** How late a smoothed line reacts to a real change. For a trailing window, about half the window.
- **Naija analogy:** News reaching the village two weeks after it happened in Abuja.
- **Example:** The trailing 30-day peak came 14 days after the centred one.

### 🕳️ Warm-up NaN
- **Plain English:** The empty values at the start of a rolling result, before the window has enough rows.
- **Naija analogy:** You can't average 7 days of salary when you only started work 3 days ago.
- **Example:** `rolling(7)` gives 6 `NaN` values at the start.

## 📈 Other smoothers and helpers

### 📰 Exponential smoothing (`.ewm`)
- **Plain English:** A smoother that gives the newest values the most weight and older values less and less.
- **Naija analogy:** How you rate a footballer: last week's match counts most, matches from last season count a little.
- **Example:** `s.ewm(alpha=0.3).mean()`

### 🎚️ Alpha
- **Plain English:** The setting for exponential smoothing. High alpha = follows the data closely and reacts fast. Low alpha = smooth and slow.
- **Naija analogy:** High alpha believes every WhatsApp broadcast immediately. Low alpha waits for three people to confirm.
- **Example:** alpha 0.5 hugs the daily line; alpha 0.05 is very calm.

### 🪣 Resample
- **Plain English:** Putting rows into time buckets (weeks, months) and summarising each bucket.
- **Naija analogy:** Sorting your daily receipts into one envelope per week.
- **Example:** `s.resample("W").sum()` gives one total per week.

### ✂️ Partial period
- **Plain English:** A bucket at the edge of the data that doesn't have all its days.
- **Naija analogy:** Judging a football match at half-time and saying the team scored few goals.
- **Example:** The last weekly bucket has only 2 days, so it shows just 9 tickets.

### 〽️ Rolling standard deviation
- **Plain English:** How much the values jumped around inside the window. A measure of wobble.
- **Naija analogy:** How much your neighbour's generator noise goes up and down in one evening.
- **Example:** `s.rolling(7).std()`

## 🛰️ Operations words

### 🎧 NOC (Network Operations Centre)
- **Plain English:** The team that watches the network 24/7 and opens a ticket for every fault.
- **Naija analogy:** The control room of a big estate, where security watches all the CCTV.
- **Example:** `noc_tickets_daily.csv` counts their tickets.

### 🚨 Priority-1 ticket
- **Plain English:** The most urgent kind of fault ticket. Rare, but serious.
- **Naija analogy:** A call from your MD at 11pm: it doesn't happen often, but when it does, everybody moves.
- **Example:** About 1 a day, and 17% of days have none.

### 🔢 Sparse (small) counts
- **Plain English:** Counts that are usually 0, 1 or 2. One extra event is a big jump, so they need wider windows.
- **Naija analogy:** Counting how many times NEPA brings light at 3am. Mostly zero, sometimes one.
- **Example:** Priority-1 tickets per day.

### 📜 SLA (Service Level Agreement)
- **Plain English:** A promise to a customer about uptime or quality, e.g. “the link will be up 99.5% of the time”.
- **Naija analogy:** The promise your internet provider made when you paid for the bundle.
- **Example:** SLA breaches must be counted from raw hourly readings, never from an average.

### ☕ Noise (again)
- **Plain English:** Random week-to-week wobble with no meaning. Don't react to it.
- **Naija analogy:** Your weight after a heavy plate of pounded yam. Wait a week before you worry.
- **Example:** 38 vs 41 tickets a week, when the mean is about 36 and the usual swing is about 5.
