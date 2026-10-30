"""Quizzes from the original MCQ files, with answer positions spread evenly (the originals are ~74% option B).
Questions the review found wrong are corrected on the way in, with the same fixes as the weekly banks (mcq.FIXES).
The original CSVs are never changed."""
from __future__ import annotations

import csv
import random

from common import ORIGINALS, SUB
from mcq import FIXES

LETTERS = "ABCD"


def shuffled_quiz(mcq_file: str, seed: int):
    """True/False questions keep their original order; 4-option questions get the answer moved to a planned letter."""
    src = list(csv.DictReader(open(ORIGINALS / "MCQ" / mcq_file, encoding="utf-8")))
    week = mcq_file.split("-")[1]                     # "week-04-mcq.csv" -> "04"
    for i, r in enumerate(src, 1):
        if (week, i) in FIXES:
            kind, why, changes = FIXES[(week, i)]
            r.update({k: "|".join(v) if k == "options" else v for k, v in changes.items()})
            r["change"] = (kind, why)
    rng = random.Random(seed)
    mc = [i for i, r in enumerate(src) if len(r["options"].split("|")) == 4]
    targets = [0, 1, 2, 3] * (len(mc) // 4) + rng.sample([0, 1, 2, 3], len(mc) % 4)
    rng.shuffle(targets)
    tgt = dict(zip(mc, targets))
    out = []
    for i, r in enumerate(src):
        opts = r["options"].split("|")
        ans = r["answer"]
        assert ans in opts, r["question"]
        if i in tgt:
            others = [o for o in opts if o != ans]
            rng.shuffle(others)
            others.insert(tgt[i], ans)
            opts = others
        out.append({"number": i + 1, "topic": r["title"], "tests": r["description"], "type": r["type"],
                    "difficulty": r["difficulty"], "question": r["question"], "options": opts, "answer": ans,
                    "letter": LETTERS[opts.index(ans)], "change": r.get("change")})
    return out


def write_quiz(d, foot, *, n: int, mcq_file: str, seed: int, covers: str, topic_map: str):
    """Writes the Google-Forms CSV + printable quiz (exercise folder) and the answer key (instructor folder)."""
    import pdfdoc

    code = d.code
    quiz = shuffled_quiz(mcq_file, seed)
    qdir = d.folder / SUB["exercise"] / "quiz"
    qdir.mkdir(parents=True, exist_ok=True)
    kicker = f"Week {d.week} · Day {d.day} · Quiz {n}"
    minutes = 20

    with open(qdir / f"{code}-quiz-{n}-google-forms.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["number", "question", "options", "answer", "topic", "type"])
        for q in quiz:
            w.writerow([q["number"], q["question"], "|".join(q["options"]), q["answer"], q["topic"], q["type"]])

    lines = [f"# Quiz {n}: {covers}", "",
             f"**{len(quiz)} questions · {minutes} minutes · just you.** Phones face down, notebooks closed, no AI tools. "
             "Circle **one** letter per question. True/False questions have two options.", "",
             "Name: ______________________________ &nbsp;&nbsp; Unit: ______________________", ""]
    topic = None
    for q in quiz:
        if q["topic"] != topic:
            topic = q["topic"]
            lines += ["", f"## {topic[0].upper() + topic[1:]}", ""]
        lines.append(f"**{q['number']}.** {q['question']}")
        lines.append("")
        for k, o in enumerate(q["options"]):
            lines.append(f"- **{LETTERS[k]}.** {o}")
        lines.append("")
    qmd = qdir / f"{code}-quiz-{n}.md"
    qmd.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pdfdoc.md_to_pdf(qmd, qmd.with_suffix(".pdf"), kicker=kicker, title=f"Quiz {n}: {covers}",
                     subtitle=f"{len(quiz)} questions · {minutes} minutes · just you", foot=foot)

    counts = {L: sum(q["letter"] == L for q in quiz if len(q["options"]) == 4) for L in LETTERS}
    tf = sum(len(q["options"]) == 2 for q in quiz)
    key = [f"# Quiz {n} Answer Key", "",
           f"> 🧑🏾‍🏫 **Instructor only.** Built from the original `Time-series/MCQ/{mcq_file}` (that file is unchanged), "
           f"with {sum(q['change'] is not None for q in quiz)} questions edited: see *Changes from the original* below. "
           f"Options were reshuffled with a fixed seed ({seed}) so the correct letters are spread out: "
           f"multiple-choice answers sit at A ×{counts['A']}, B ×{counts['B']}, C ×{counts['C']}, D ×{counts['D']} "
           f"(in the original, most answers were option B). The {tf} True/False questions keep their original order.", "",
           "| # | Answer | Correct option | What it tests | Level |", "|---|---|---|---|---|"]
    for q in quiz:
        key.append(f"| {q['number']} | **{q['letter']}** | {q['answer']} | {q['tests']} | {q['difficulty']} |")
    changed = [q for q in quiz if q["change"]]
    if changed:
        key += ["", "## Changes from the original", "",
                "The same fixes are in the weekly question banks (`week-N/MCQ/`).", ""]
        key += [f"- **Q{q['number']}** ({q['change'][0]}): {q['change'][1]}" for q in changed]
    key += ["", "## Marking it together (10 minutes)", "",
            "1. Read out the letters; everyone marks their own paper.",
            "2. Ask for hands up on each question. Any question that more than a third of the room got wrong, explain it again with the matching day's slide.",
            f"3. Map each topic back to its day: {topic_map}.",
            "", "## Quick topic tally", "", "| Topic | Questions |", "|---|---|"]
    topics: dict = {}
    for q in quiz:
        topics.setdefault(q["topic"], []).append(str(q["number"]))
    for t, nums in topics.items():
        key.append(f"| {t} | {', '.join(nums)} |")
    kmd = d.folder / SUB["instructor"] / f"{code}-quiz-{n}-answer-key.md"
    kmd.write_text("\n".join(key) + "\n", encoding="utf-8")
    pdfdoc.md_to_pdf(kmd, kmd.with_suffix(".pdf"), kicker=f"Week {d.week} · Day {d.day} · Instructor only",
                     title=f"Quiz {n} Answer Key", subtitle=f"{covers} · shuffled version", foot=foot)
    return quiz
