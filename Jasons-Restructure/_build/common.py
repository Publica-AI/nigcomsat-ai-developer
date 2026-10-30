"""Shared settings for every build script: paths, brand, course map, data links."""
from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parent                      # Jasons-Restructure/
REPO = ROOT.parent                       # the whole repo
ORIGINALS = REPO / "Time-series"
BRAND_DIR = ROOT / "assets" / "brand"

# --- where the course lives on GitHub (change these two lines if it moves) ---
GITHUB_REPO = "Publica-AI/nigcomsat-ai-developer"
GITHUB_BRANCH = "jasons-restructure"

# The training data is read straight from the ORIGINAL files on the main branch.
DATA_BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{DATA_BRANCH}/Time-series"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# --- brand --------------------------------------------------------------------
BRAND = {
    "space": "#0B1622",       # dark background
    "space2": "#12233A",      # dark cards
    "ink": "#0B1622",         # text on light
    "muted_light": "#5B6B7D",
    "muted_dark": "#9DB0C6",
    "paper": "#FFFFFF",
    "paper2": "#F2F6FA",
    "line_light": "#DCE4EC",
    "line_dark": "#24384F",
    "blue": "#0A5DB4",        # NIGCOMSAT blue (light surfaces)
    "blue_d": "#3B8BE0",      # NIGCOMSAT blue (dark surfaces)
    "teal": "#008C7E",        # Publica teal (light)
    "teal_d": "#16A394",      # Publica teal (dark)
    "amber": "#C77700",       # highlight (light)
    "amber_d": "#C98205",     # highlight (dark, data)
    "gold": "#F5B83D",        # glow / text accent on dark
    "good": "#1E9E5A",
    "bad": "#E5484D",
}


def logo_data_uri(name: str) -> str:
    raw = (BRAND_DIR / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode()


# --- the course map -------------------------------------------------------------
@dataclass(frozen=True)
class Day:
    week: int
    day: int
    slug: str
    title: str
    original: str          # which original topic(s) it covers
    datasets: str
    hook: str
    step: int              # build step in 00-PLAN.md

    @property
    def code(self) -> str:
        return f"W{self.week}D{self.day}"

    @property
    def folder(self) -> Path:
        return ROOT / f"week-{self.week}" / f"day-{self.day}-{self.slug}"

    @property
    def rel(self) -> str:
        return f"week-{self.week}/day-{self.day}-{self.slug}"


WEEK_TITLES = {
    1: "Hello, Time: Colab and reading a time series",
    2: "Patterns: taking a series apart",
    3: "When things go wrong: one sensor at a time",
    4: "Scoring detectors and meeting machine learning",
    5: "Honest ML and the first forecasts",
    6: "The future: backtesting, remaining life and your project",
}

DAYS = [
    Day(1, 1, "colab-and-your-first-time-series", "Colab Bootcamp + Your First Time Series",
        "Week 3 · 3.1 Structure of time-series data", "ka_band_availability_daily",
        "Every “Up NEPA!” is a timestamp and a value", 1),
    Day(1, 2, "charts-that-dont-lie", "Charts That Don't Lie",
        "Week 3 · 3.2 Visualising and data storytelling", "rf_link_quality_hourly, vsat_uptime_by_region_weekly",
        "DStv vanishes when Lagos rain falls, and the average hides it", 2),
    Day(1, 3, "rolling-windows", "Calm Down the Noise: Rolling Windows",
        "Week 3 · 3.3 Rolling windows and smoothing", "noc_tickets_daily",
        "Even faults rest on Sunday", 2),
    Day(2, 1, "trend-season-noise", "Take It Apart: Trend, Season and Noise",
        "Week 3 · 3.4 Decomposition", "ka_band_availability_monthly, additive_multiplicative_demo",
        "Lagos traffic = city growing + rush hour + one keke breakdown", 2),
    Day(2, 2, "does-today-remember-yesterday", "Does Today Remember Yesterday?",
        "Week 3 · 3.5 Autocorrelation", "bandwidth_throughput_daily, twta_thermal_daily",
        "Suya sales and generator sales both rise in December", 2),
    Day(2, 3, "lab-day-quiz-1-and-project-kickoff", "Lab Day + Quiz 1 + Pick Your Project",
        "Week 3 review + capstone kickoff", "all Week 3 files",
        "Choose your final-project brief", 2),
    Day(3, 1, "alarms-that-cry-wolf", "Alarms That Cry Wolf",
        "Week 4 · 4.1 What your alarm software already does", "bus_power_telemetry_hourly",
        "Eclipse is the satellite's own “NEPA has taken light”", 3),
    Day(3, 2, "control-charts-and-residuals", "Control Charts and Residuals",
        "Week 4 · 4.2 SPC, 4.3 Residual-based detection", "bus_power_telemetry_hourly, twta_thermal_daily",
        "Mama Put knows the normal price of tomatoes", 3),
    Day(3, 3, "drift-and-cusum", "The Slow Creep: Drift and CUSUM",
        "Week 4 · 4.4 Change points and drift", "twta_thermal_daily (W4), battery_health_daily (W4)",
        "The landlord adds small-small to the rent every year", 3),
    Day(4, 1, "scoring-detectors-and-quiz-2", "Scoring a Detector + Quiz 2",
        "Week 4 · 4.5 Evaluating a detector", "telemetry_anomaly_labels",
        "The mai-guard who shouts “Thief!” at every goat", 3),
    Day(4, 2, "scikit-learn-and-isolation-forest", "Meet scikit-learn + Isolation Forest",
        "Week 5 · 5.1 scikit-learn workflow, 5.2 Isolation forest", "bus_telemetry_multivariate_hourly",
        "Spot the man in agbada at a beach party", 4),
    Day(4, 3, "feature-engineering", "Give the Model Eyes: Feature Engineering",
        "Week 5 · 5.3 Feature engineering", "bus_telemetry_multivariate_hourly",
        "NEPA brought light but the inverter is still not charging", 4),
    Day(5, 1, "honest-splits-and-quiz-3", "No Expo! Honest Train/Test Splits + Quiz 3",
        "Week 5 · 5.4 Temporal train/test discipline", "bus_telemetry_multivariate_hourly + labels",
        "WAEC expo: if you saw the questions, the score is fake", 4),
    Day(5, 2, "forecasting-baselines", "Forecasting Baselines",
        "Week 6 · 6.1 Forecasting baselines", "ops_tickets_weekly",
        "Grandma's forecast: tomorrow will be like today", 5),
    Day(5, 3, "regression-forecasts-and-intervals", "Regression Forecasts + Honest Ranges",
        "Week 6 · 6.2 Regression forecasting, 6.3 Prediction intervals", "ops_tickets_weekly",
        "“I'm on my way” vs “30 to 90 minutes, Third Mainland Bridge permitting”", 5),
    Day(6, 1, "backtesting", "Backtesting: Test It on the Past First",
        "Week 6 · 6.5 Backtesting", "ops_tickets_weekly",
        "Try your strategy on last season's matches before staking real money", 5),
    Day(6, 2, "remaining-useful-life-and-quiz-4", "When Will It Break? Remaining Useful Life + Quiz 4",
        "Week 6 · 6.4 Trend-to-threshold and RUL", "degradation_assets_daily, degradation_thresholds",
        "How much fuel is left in the tank?", 5),
    Day(6, 3, "project-clinic-and-demo-day", "Project Clinic and Demo Day",
        "Capstone", "participants' own data", "Five-minute demos to the cohort", 5),
]


def day(week: int, d: int) -> Day:
    return next(x for x in DAYS if x.week == week and x.day == d)


def colab_url(path_in_repo: str) -> str:
    return f"https://colab.research.google.com/github/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{path_in_repo}"


def colab_badge_md(path_in_repo: str) -> str:
    return (f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
            f"({colab_url(path_in_repo)})")


# Day sub-folders (kept identical for all 18 days)
SUB = {
    "slides": "1-slides",
    "web": "1-slides/web-animated",
    "pptx": "1-slides/powerpoint",
    "slides_pdf": "1-slides/pdf",
    "exercise": "2-exercise",
    "rulebook": "2-exercise/rulebook",
    "glossary": "3-glossary",
    "instructor": "4-instructor-only",
}


def read_labels(path):
    """Build-side twin of the notebooks' load_labels(): survives the stray comma in the original labels file."""
    import pandas as pd
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    cols = lines[0].split(",")
    df = pd.DataFrame([ln.split(",", len(cols) - 1) for ln in lines[1:] if ln.strip()], columns=cols)
    for c in ("start", "end"):
        if c in df:
            df[c] = pd.to_datetime(df[c], format="mixed")
    return df
