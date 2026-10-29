# Colab Survival Guide

Everything you need to use Google Colab in this course, on one page. Keep it handy for the full six weeks.

## 1. What is Colab?

Google Colab is a free website for writing and running Python. **Your laptop only shows the screen. Google's computer does the work.** Python, pandas, matplotlib, scikit-learn and statsmodels are already installed, so there is nothing to set up.

> 🧠 Think of it as a cyber café computer that lives inside Chrome: free, always ready, and it never runs out of fuel.

## 2. Getting in

| Step | Do this |
|---|---|
| 1 | Use **Google Chrome** (other browsers work, Chrome works best) |
| 2 | Sign in with a **Google account**. If your work account blocks Colab, use a personal Gmail |
| 3 | Click the **Open in Colab** button on the day's exercise |
| 4 | **File → Save a copy in Drive.** A new tab opens. Work only in that tab |

Your copies live in **Google Drive → My Drive → Colab Notebooks**.

## 3. The screen

| Part | Where | What it does |
|---|---|---|
| ▶ **Run button** | left of each code cell | runs that one cell |
| **Code cell** | grey box | Python goes here |
| **Text cell** | plain text | instructions and notes. Double-click to edit |
| 📁 **Files panel** | left sidebar | files you downloaded or uploaded |
| **{x} Variables** | left sidebar | shows everything Colab currently remembers |
| ☰ **Table of contents** | left sidebar | jump between parts of the notebook |
| **Runtime menu** | top menu | restart, run all, run before |

## 4. Running cells

| You want to | Do this |
|---|---|
| Run a cell and move to the next | **Shift + Enter** |
| Run a cell and stay on it | **Ctrl + Enter** (Mac: **Cmd + Enter**) |
| Run everything from the top | **Runtime → Run all** |
| Run everything above this cell | **Runtime → Run before** |
| Stop a cell that runs forever | click the ⏹ button, or **Runtime → Interrupt execution** |
| Start fresh | **Runtime → Restart session** (then run STEP 0 again!) |

> **Golden rule:** run cells **top to bottom**. A cell can only use what the cells above it created.

## 5. Colab's short memory

- Colab **remembers** every variable you create, until the session restarts.
- Sessions end if you are **idle for a while** (roughly 90 minutes) or after many hours of use. You'll see *"Runtime disconnected"*.
- After a restart or disconnect: **run STEP 0, then the cells above where you were.**
- Files in the 📁 Files panel are **deleted when the session ends**. Your notebook (in Drive) is safe.

## 6. Files and your own data

| You want to | Do this |
|---|---|
| Use the course data | Nothing: STEP 0 and `data_path("name")` download it for you |
| Upload a small CSV | Drag it into the 📁 Files panel, then `pd.read_csv("yourfile.csv")` |
| Keep files between sessions | Mount Drive: `from google.colab import drive; drive.mount("/content/drive")` |
| Download your notebook | **File → Download → Download .ipynb** |
| Share with the trainer | **Share** button (top right) → add their email as *Commenter* |

> ⛔ **Real NIGCOMSAT data does not go into Colab** unless your unit head has agreed in writing. Colab runs on Google's servers, outside NIGCOMSAT. The course data is synthetic, so it's fine.

## 7. The AI button (Gemini)

| ✅ OK | ⛔ Never |
|---|---|
| “Explain this error to me” | Pasting real telemetry, RF records or network logs |
| “What does `.asfreq()` do?” | Customer, staff or contract details |
| Pasting course (synthetic) data | Anything your unit has not cleared |

**Not sure?** Describe the *shape* of your data (“a table of hourly voltages with a timestamp column”) instead of pasting it. And always **check what the AI tells you**: it can be confidently wrong.

## 8. Keyboard shortcuts worth learning

| Shortcut (Mac: Cmd instead of Ctrl) | Does |
|---|---|
| Shift + Enter | Run cell, go to next |
| Ctrl + Enter | Run cell, stay |
| Alt + Enter | Run cell, insert a new one below |
| Ctrl + M, then B | New code cell below |
| Ctrl + M, then D | Delete cell |
| Ctrl + M, then M / Y | Turn cell into text / code |
| Ctrl + / | Comment or uncomment a line |
| Ctrl + Z | Undo typing |

## 9. Errors you'll meet (and the fix)

| Error | Meaning | Fix |
|---|---|---|
| `NameError: name 'x' is not defined` | Colab doesn't remember `x` | Run STEP 0 and the cells above. Check for missing quotes |
| `KeyError: 'col'` | No column with that name | Copy the exact name from `df.head()` |
| `SyntaxError` | Typo: missing `)`, `"`, `,` or `:` | Read the line slowly; Colab underlines the spot |
| `IndentationError` | Spaces at the start of a line are wrong | Line it up with the lines around it |
| `FileNotFoundError` | File isn't where you said | Use `data_path("name")`, or check the 📁 panel |
| `ModuleNotFoundError` | A library isn't installed | `!pip install name` in a cell (rarely needed in this course) |
| *Runtime disconnected* | Idle too long | Reconnect, run STEP 0 and the cells above |

## 10. Five habits of people who never suffer in Colab

1. **Save a copy first.** Every time.
2. **Top to bottom.** No jumping around.
3. **STEP 0 after every restart.**
4. **Read the error's last line first.** It usually tells you exactly what's wrong.
5. **Restart & run all** before you say “I'm done”. If it runs clean from the top, it's really done.
