# _build: how the course materials are generated

You never need to touch this folder to teach. It exists so every day looks the same and anything can be rebuilt in one command.

## What makes what

| Script | Makes |
|---|---|
| `build.py` | Runs everything: folders and READMEs, then each finished day, the toolkit PDFs and the final-project PDF |
| `days/w1d1.py` (one file per day) | That day's content: animated slides, PowerPoint outline, notebook cells and answer checks |
| `webdeck.py` | The animated web-slide engine (one self-contained `.html` per day) |
| `build_pptx.js` + `theme.js` | The static PowerPoint decks (pptxgenjs) |
| `notebook.py` | The Colab exercise and solution notebooks |
| `pdfdoc.py` | Markdown → branded PDF (rule books, glossaries, notes, toolkit, final project) |
| `svgcharts.py` | Animated charts drawn from the real course data |
| `emoji.py` + `emoji/` | Icon images for PowerPoint |
| `content/README-top.md` | Template for the main README (the course map is filled in automatically) |

Hand-written files (rule books, glossaries, instructor notes, toolkit, final project) are the `.md` files in their own folders. The build only turns them into PDFs.

## Rebuild

```bash
cd Jasons-Restructure/_build
npm install                                   # once
pip install pandas numpy matplotlib nbformat markdown pillow
python build.py            # everything
python build.py W1D1       # one day
python build.py toolkit    # toolkit PDFs + master glossary
python build.py project    # final-project PDF
```

Needs Google Chrome (for PDFs) and Node.js. To move the course to another GitHub repo or branch, change `GITHUB_REPO` / `GITHUB_BRANCH` in `common.py` and rebuild: every “Open in Colab” link updates.

## Test (run before every commit)

```bash
_build/test/setup_test_envs.sh /some/scratch/folder            # once: pandas 2.2 + pandas 3 environments
export TS_TEST_DIR=/some/scratch/folder
_build/test/run_day.sh W1D1 week-1/day-1-*/4-instructor-only/W1D1-solution.ipynb
```

Every solution notebook must say "You have N of N tasks correct" with `ERRORS: []` on **both** pandas versions. The runner works offline (it pre-fills the download cache from `Time-series/`).

## Credits

Icons in the PowerPoint decks: [Noto Emoji](https://github.com/googlefonts/noto-emoji) by Google, Apache License 2.0. Logos belong to NIGCOMSAT and Publica Academy.
