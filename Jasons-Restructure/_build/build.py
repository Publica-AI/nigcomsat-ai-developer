"""Builds the course. Usage:
    python build.py                 # everything that exists
    python build.py W1D1            # one day
    python build.py toolkit         # toolkit PDFs + master glossary
    python build.py project         # final-project PDF
"""
from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import nbformat

sys.path.insert(0, str(Path(__file__).parent))
from common import (BUILD, DAYS, ROOT, SUB, WEEK_TITLES, colab_url)  # noqa: E402
import emoji  # noqa: E402
import notebook  # noqa: E402
import pdfdoc  # noqa: E402
import webdeck  # noqa: E402

# every finished day is a module in days/ named like w1d2.py
BUILT = {p.stem.upper(): f"days.{p.stem}" for p in sorted((Path(__file__).parent / "days").glob("w[0-9]d[0-9].py"))}


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ----------------------------------------------------------------------------- skeleton
def day_readme(d, built: bool) -> str:
    head = (f"# Week {d.week} · Day {d.day}: {d.title}\n\n"
            f"| | |\n|---|---|\n| **Covers (original material)** | {d.original} |\n"
            f"| **Main dataset(s)** | `{d.datasets}` |\n| **The Naija hook** | {d.hook} |\n"
            f"| **Session length** | ~2 hours (10 min hook · 30 min slides · 60 min hands-on · 20 min wrap-up) |\n\n")
    if not built:
        return head + (f"> 🚧 **Coming in build Step {d.step}** (see `00-PLAN.md`). This folder will get the same kit as Day 1: "
                       "slides (animated web, PowerPoint, PDF), a Colab exercise, a rule book, a glossary and instructor notes.\n")
    c = d.code
    nb_path = f"Jasons-Restructure/{d.rel}/{SUB['exercise']}/{c}-exercise.ipynb"
    return head + f"""## What's in this folder

| Folder | File | Who it's for | How to use it |
|---|---|---|---|
| `{SUB['web']}/` | `{c}-slides-animated.html` | Presenter | Double-click to open in Chrome. **→ / Space** next, **←** back, **F** full screen, **N** speaker notes |
| `{SUB['pptx']}/` | `{c}-slides.pptx` | Presenter | Static, simpler version. Opens in PowerPoint or Keynote. **Google Slides:** upload to Drive → *Open with Google Slides* |
| `{SUB['slides_pdf']}/` | `{c}-slides.pdf` | Everyone | Printable handout of the animated deck |
| `{SUB['exercise']}/` | `{c}-exercise.ipynb` | Participants | [Open in Colab]({colab_url(nb_path)}), then **File → Save a copy in Drive** |
| `{SUB['rulebook']}/` | `{c}-rulebook.pdf` / `.md` | Participants | One page of steps, rules and error fixes for the exercise |
| `{SUB['glossary']}/` | `{c}-glossary.pdf` / `.md` | Participants | Today's new words, made easy with Naija analogies |
| `{SUB['instructor']}/` | `{c}-instructor-notes.pdf` / `.md`, `{c}-solution.ipynb` | **You only** | Run of show, what to say, answers, and the filled-in notebook |

## Order on the day
1. Open the **animated slides** (or the PowerPoint) and teach.
2. Participants open the **exercise** in Colab with the **rule book** beside them.
3. Hand out the **glossary** (PDF or link) at the end, as revision for next time.
"""


def week_readme(w: int) -> str:
    rows = "\n".join(f"| Day {d.day} | [{d.title}](day-{d.day}-{d.slug}/) | {d.original} | {d.hook} |"
                     for d in DAYS if d.week == w)
    extra = ""
    if w == 6:
        extra = "\n## 🏁 Final project\nEverything about the final project is in **[`final-project/`](final-project/)**: the requirements PDF, checklists and the data-collection hardware recommendations.\n"
    if w == 2:
        extra = "\n## 🏁 Final project starts this week\nOn **Day 3** participants pick their brief. Requirements: [`../week-6/final-project/`](../week-6/final-project/)\n"
    return f"# Week {w}: {WEEK_TITLES[w]}\n\n| Day | Session | Original topic | Naija hook |\n|---|---|---|---|\n{rows}\n{extra}"


def build_skeleton():
    for w in range(1, 7):
        write(ROOT / f"week-{w}" / "README.md", week_readme(w))
    for d in DAYS:
        write(d.folder / "README.md", day_readme(d, d.code in BUILT))


def build_readme():
    rows = []
    for d in DAYS:
        status = "✅ ready" if d.code in BUILT else f"🚧 Step {d.step}"
        rows.append(f"| {d.week} | {d.day} | [{d.title}]({d.rel}/) | {d.original} | {status} |")
    text = (ROOT / "_build" / "content" / "README-top.md").read_text(encoding="utf-8")
    text = text.replace("{{COURSE_MAP}}", "| Week | Day | Session | Original topic | Status |\n|---|---|---|---|---|\n" + "\n".join(rows))
    write(ROOT / "README.md", text)


# ----------------------------------------------------------------------------- one day
def build_day(code: str):
    d = next(x for x in DAYS if x.code == code)
    mod = importlib.import_module(BUILT[code])
    f = d.folder
    foot = f"Publica Academy · NIGCOMSAT Time-Series Programme · {code}"

    # 1. animated web slides + PDF of them
    html_path = f / SUB["web"] / f"{code}-slides-animated.html"
    slides = mod.web_slides()
    write(html_path, webdeck.render(code, d.title, slides))
    pdf_path = f / SUB["slides_pdf"] / f"{code}-slides.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdfdoc.deck_to_pdf(html_path, pdf_path, len(slides))

    # 2. PowerPoint
    spec_path = BUILD / ".cache" / f"{code}-pptx.json"
    spec = mod.pptx_spec()
    spec["emoji"] = emoji.emoji_map(spec)
    write(spec_path, json.dumps(spec, ensure_ascii=False))
    pptx_path = f / SUB["pptx"] / f"{code}-slides.pptx"
    pptx_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["node", str(BUILD / "build_pptx.js"), str(spec_path), str(pptx_path)], check=True)

    # 3. notebooks
    setup = notebook.setup_code(mod.CHECKS)
    cells = mod.notebook_cells(setup)
    ex_rel = f"Jasons-Restructure/{d.rel}/{SUB['exercise']}/{code}-exercise.ipynb"
    sol_rel = f"Jasons-Restructure/{d.rel}/{SUB['instructor']}/{code}-solution.ipynb"
    for rel, sol in ((ex_rel, False), (sol_rel, True)):
        nb = notebook.build(cells, rel, sol, d.title)
        p = ROOT.parent / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(nb, p)

    # 4. rule book, glossary, instructor notes (markdown is hand-written; PDFs are generated)
    for sub, name, kick, sub_t, cards in (
        ("rulebook", "rulebook", f"Week {d.week} · Day {d.day} · Rule book", "Follow it step by step. Every common error and its fix is here.", False),
        ("glossary", "glossary", f"Week {d.week} · Day {d.day} · Glossary", "Today's new words, made easy.", True),
        ("instructor", "instructor-notes", f"Week {d.week} · Day {d.day} · Instructor notes", "For the trainer only.", False),
    ):
        md = f / SUB[sub] / f"{code}-{name}.md"
        if md.exists():
            pdfdoc.md_to_pdf(md, md.with_suffix(".pdf"), kicker=kick, title=d.title, subtitle=sub_t, foot=foot, cards=cards)

    # 5. anything special to this day (quizzes, worksheets, ...)
    if hasattr(mod, "extra"):
        mod.extra(d, foot)
    print("built", code)


# ----------------------------------------------------------------------------- toolkit & project
def build_master_glossary():
    entries: dict = {}          # term -> [first block, [day codes]]
    for d in DAYS:
        md = d.folder / SUB["glossary"] / f"{d.code}-glossary.md"
        if not md.exists():
            continue
        text = md.read_text(encoding="utf-8")
        for block in re.split(r"\n(?=### )", text):
            if block.startswith("### "):
                term = block.splitlines()[0][4:].strip()
                key = re.sub(r"[^a-z0-9]+", " ", re.sub(r"^[^\w]+", "", term).lower()).strip()
                block = block.split("\n## ")[0].strip()     # don't drag the next section heading along
                if key in entries:
                    entries[key][1].append(d.code)
                else:
                    entries[key] = [block, [d.code]]
    body = "\n\n".join(blk + "\n\n" + " ".join(f'<span class="pill">{c}</span>' for c in codes)
                       for _, (blk, codes) in sorted(entries.items()))
    write(ROOT / "toolkit" / "master-glossary.md",
          "# Master Glossary\n\nEvery new word from every day, A to Z. The tag (e.g. `W1D1`) shows the day it was introduced. "
          "This file is rebuilt automatically from the daily glossaries.\n\n" + body + "\n")


def build_toolkit():
    build_master_glossary()
    foot = "Publica Academy · NIGCOMSAT Time-Series Programme · Toolkit"
    for name, title, sub, cards in (
        ("colab-survival-guide", "Colab Survival Guide", "Everything you need to use Google Colab in this course.", False),
        ("nigcomsat-fact-sheet", "NIGCOMSAT Fact Sheet", "Verified facts for real examples, with sources.", False),
        ("master-glossary", "Master Glossary", "Every new word from every day, A to Z.", True),
    ):
        md = ROOT / "toolkit" / f"{name}.md"
        if md.exists():
            pdfdoc.md_to_pdf(md, md.with_suffix(".pdf"), kicker="Toolkit", title=title, subtitle=sub, foot=foot, cards=cards)
    print("built toolkit")


def build_project():
    md = ROOT / "week-6" / "final-project" / "Final-Project-Requirements.md"
    pdfdoc.md_to_pdf(md, md.with_suffix(".pdf"), kicker="Week 6 · Final project", title="Final Project Requirements",
                     subtitle="From real NIGCOMSAT data to a working monitor your unit can use.",
                     foot="Publica Academy · NIGCOMSAT Time-Series Programme · Final project")
    print("built final project")


if __name__ == "__main__":
    args = sys.argv[1:] or ["all"]
    build_skeleton()
    build_readme()
    for a in args:
        if a in BUILT:
            build_day(a)
        elif a == "toolkit":
            build_toolkit()
        elif a == "project":
            build_project()
        elif a == "all":
            for c in BUILT:
                build_day(c)
            build_toolkit()
            build_project()
