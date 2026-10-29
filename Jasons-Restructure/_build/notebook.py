"""Builds the Colab exercise notebook and its solution twin from one list of cells."""
from __future__ import annotations

import base64
import io

import nbformat as nbf
from PIL import Image

from common import BRAND_DIR, RAW_BASE, colab_badge_md

# which original week-folder each dataset lives in
DATA_HOME = {
    "additive_multiplicative_demo": "week-03", "bandwidth_throughput_daily": "week-03",
    "ka_band_availability_daily": "week-03", "ka_band_availability_monthly": "week-03",
    "link_margin_hourly_aug2025": "week-03", "noc_tickets_daily": "week-03", "noc_tickets_weekly": "week-03",
    "transponder_utilisation_monthly": "week-03", "vsat_uptime_by_region_weekly": "week-03",
    "rf_link_quality_hourly": "week-03",
    "bus_power_telemetry_hourly": "week-04", "battery_health_daily": "week-04", "twta_thermal_daily": "week-04",
    "telemetry_anomaly_labels": "week-04",
    "bus_telemetry_multivariate_hourly": "week-05", "anomaly_labels_week5": "week-05",
    "degradation_assets_daily": "week-06", "degradation_thresholds": "week-06", "ops_tickets_weekly": "week-06",
}

SETUP_BASE = '''#@title 🚀 STEP 0 · Run me first (click the ▶ button on the left of this cell) { display-mode: "form" }
import sys, warnings
warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from pathlib import Path
from urllib.request import urlretrieve

pd.set_option("display.width", 130)
pd.set_option("display.max_columns", 30)
plt.rcParams.update({"figure.figsize": (11, 3.6), "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25, "axes.titleweight": "bold",
                     "axes.prop_cycle": plt.cycler(color=["#0A5DB4", "#C77700", "#008C7E"])})

IN_COLAB = "google.colab" in sys.modules
RAW = "%(raw)s"
DATA_HOME = %(home)r

def data_path(name, week=None):
    """Download a course CSV once and return where it is saved.
    week: which original folder to use, e.g. "week-03" (two files exist in both week-03 and week-04).
    If you uploaded the file yourself (Files panel), that copy is used instead."""
    uploaded = Path(f"{name}.csv")
    if uploaded.exists():
        return uploaded
    week = week or DATA_HOME[name]
    local = Path("course_data") / week / f"{name}.csv"
    if not local.exists():
        local.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(f"{RAW}/{week}/data/{name}.csv", local)
    return local

def load_labels(name="telemetry_anomaly_labels", week=None):
    """Read an answer-key (labels) file. The original telemetry_anomaly_labels.csv has a stray comma
    inside one description, which makes pd.read_csv crash, so the last column is read as free text."""
    lines = Path(data_path(name, week)).read_text(encoding="utf-8").splitlines()
    cols = lines[0].split(",")
    rows = [ln.split(",", len(cols) - 1) for ln in lines[1:] if ln.strip()]
    df = pd.DataFrame(rows, columns=cols)
    for c in ("start", "end"):
        if c in df:
            df[c] = pd.to_datetime(df[c], format="mixed")
    return df

___ = None          # this is "the blank". Replace every ___ with your answer.
SCORE = {}

def _blank(x):
    return x is None or (isinstance(x, tuple) and any(v is None for v in x))

def check(task, answer):
    """Marks one task. Prints ✅ or ❌ with a hint."""
    if _blank(answer):
        print("✍️  Fill in the blank first: replace ___ with your answer, then run the cell again.")
        return
    try:
        ok, good, hint = CHECKS[task](answer)
    except Exception as e:
        ok, good, hint = False, "", f"{HINTS.get(task, 'Read the task again.')}  (Python said: {type(e).__name__})"
    SCORE[task] = ok
    print(("✅ " + good) if ok else ("❌ Not yet. Hint: " + hint))

def scoreboard():
    got = sum(SCORE.values())
    print(f"You have {got} of {len(CHECKS)} tasks correct.")
    print("🏆 Oya, you don finish! Mad o!" if got == len(CHECKS) else "💪 Keep going: scroll up and fix the ❌ ones.")
'''


def setup_code(checks_code: str) -> str:
    return SETUP_BASE % {"raw": RAW_BASE, "home": DATA_HOME} + "\n# ---- today's checks ----\n" + checks_code.strip() + \
        '\n\nprint(f"✅ Ready! pandas {pd.__version__} · running in {\'Google Colab\' if IN_COLAB else \'Jupyter\'}. Scroll down and let\'s go 🚀")\n'


def _logo_strip() -> str:
    """Small logo strip as an inline image so it works without internet."""
    def tiny(name, h):
        im = Image.open(BRAND_DIR / name)
        im.thumbnail((10_000, h))
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    return (f'<img src="{tiny("nigcomsat-logo.png", 90)}" height="60" alt="NIGCOMSAT"> &nbsp;&nbsp; '
            f'<img src="{tiny("publica-academy-logo.png", 90)}" height="48" alt="Publica Academy">')


def build(cells: list, repo_path: str, solution: bool, title: str):
    """cells: ("md", text) | ("setup", code) | ("code", code) | ("task", blank_code, solution_code)"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "colab": {"provenance": [], "toc_visible": True, "name": repo_path.split("/")[-1]},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    }
    head = f"{_logo_strip()}\n\n{colab_badge_md(repo_path)}\n\n"
    if solution:
        head += "> 🧑🏾‍🏫 **INSTRUCTOR SOLUTION.** Every blank is filled in. Don't share this with participants before the session ends.\n\n"
    out = []
    first_md = True
    for c in cells:
        kind = c[0]
        if kind == "md":
            text = (head + c[1]) if first_md else c[1]
            first_md = False
            out.append(nbf.v4.new_markdown_cell(text))
        elif kind == "setup":
            cell = nbf.v4.new_code_cell(c[1])
            cell.metadata = {"cellView": "form", "id": "setup"}
            out.append(cell)
        elif kind == "code":
            out.append(nbf.v4.new_code_cell(c[1]))
        elif kind == "task":
            out.append(nbf.v4.new_code_cell(c[2] if solution else c[1]))
        else:
            raise ValueError(kind)
    nb.cells = out
    return nb
