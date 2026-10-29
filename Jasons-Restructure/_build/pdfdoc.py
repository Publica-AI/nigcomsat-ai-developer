"""Markdown -> branded HTML -> PDF (via headless Chrome)."""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import markdown

from common import BRAND as B, CHROME, logo_data_uri

CSS = """
@page{size:A4;margin:16mm 15mm 18mm 15mm;
  @bottom-left{content:"%(foot)s";font:9pt "Avenir Next","Segoe UI",Arial,sans-serif;color:#5B6B7D}
  @bottom-right{content:"Page " counter(page) " of " counter(pages);font:9pt "Avenir Next","Segoe UI",Arial,sans-serif;color:#5B6B7D}}
*{box-sizing:border-box}
body{font-family:"Avenir Next","Segoe UI",-apple-system,Arial,sans-serif;color:%(ink)s;font-size:10.6pt;line-height:1.5;margin:0}
.cover{background:%(space)s;color:#fff;border-radius:14px;padding:22px 26px 20px;margin-bottom:18px;display:flex;align-items:center;gap:18px}
.cover .logos{display:flex;gap:10px;flex:none}
.cover .logos span{background:#fff;border-radius:10px;padding:6px 10px;display:flex;align-items:center;gap:6px;height:58px}
.cover .logos img{height:46px}
.cover .logos b{color:%(ink)s;font-size:10pt;line-height:1.05}
.cover .t .k{font-size:8.5pt;letter-spacing:.18em;text-transform:uppercase;color:%(gold)s;font-weight:700}
.cover .t h1{margin:4px 0 2px;font-size:21pt;line-height:1.1;color:#fff;border:none;padding:0}
.cover .t p{margin:0;color:#C9D6E5;font-size:10pt}
h1{font-size:19pt;margin:18px 0 8px;color:%(ink)s}
h2{font-size:14.5pt;margin:20px 0 8px;color:%(blue)s;break-after:avoid}
h3{font-size:12pt;margin:14px 0 6px;color:%(ink)s;break-after:avoid}
p{margin:6px 0}
a{color:%(blue)s}
table{border-collapse:separate;border-spacing:0;width:100%%;margin:10px 0 14px;font-size:9.8pt;break-inside:auto}
th{background:%(space)s;color:#fff;text-align:left;padding:7px 9px;font-weight:700}
th:first-child{border-top-left-radius:8px}th:last-child{border-top-right-radius:8px}
td{padding:7px 9px;border-bottom:1px solid #DCE4EC;vertical-align:top}
tr:nth-child(even) td{background:#F5F8FB}
tr{break-inside:avoid}
blockquote{margin:12px 0;padding:10px 14px;background:#EEF5FD;border-radius:10px;color:%(ink)s}
blockquote p{margin:3px 0}
code{font-family:"SF Mono",Menlo,Consolas,monospace;font-size:9.2pt;background:#EEF3F8;padding:1px 5px;border-radius:5px}
pre{background:%(space)s;color:#D7E3F1;padding:12px 14px;border-radius:10px;overflow:hidden;white-space:pre-wrap;break-inside:avoid}
pre code{background:none;color:inherit;padding:0}
ul,ol{margin:6px 0 6px 20px;padding:0}
li{margin:3px 0}
hr{border:none;border-top:1px solid #DCE4EC;margin:16px 0}
.term{border:1px solid #DCE4EC;border-radius:12px;padding:10px 14px;margin:10px 0;break-inside:avoid;background:#fff}
.term h3{margin:0 0 4px;color:%(blue)s}
.term p{margin:3px 0}
.pill{display:inline-block;background:#EEF5FD;color:%(blue)s;border-radius:99px;padding:1px 9px;font-size:8.5pt;font-weight:700}
.box{border:1px solid #DCE4EC;border-radius:12px;padding:10px 14px;margin:10px 0;break-inside:avoid}
.box.good{background:#EDF8F2;border-color:#BFE6CF}
.box.warn{background:#FFF6E5;border-color:#F3D9A4}
.box.bad{background:#FDEEEE;border-color:#F4C2C3}
.check{list-style:none;margin-left:0}
.check li:before{content:"☐  ";font-size:11pt;color:%(blue)s}
.pagebreak{break-before:page}
"""


def _glossary_cards(html: str) -> str:
    """Wrap every <h3> and the paragraphs after it in a card (used by glossaries)."""
    parts = re.split(r"(?=<h3)", html)
    out = [parts[0]]
    for p in parts[1:]:
        m = re.match(r"(<h3.*?</h3>)(.*?)(?=(<h2|<hr|$))", p, flags=re.S)
        if m:
            out.append(f'<div class="term">{m.group(1)}{m.group(2)}</div>{p[m.end():]}')
        else:
            out.append(p)
    return "".join(out)


def md_to_pdf(md_path: Path, pdf_path: Path, *, kicker: str, title: str, subtitle: str, foot: str,
              cards: bool = False) -> None:
    text = md_path.read_text(encoding="utf-8")
    # drop the first markdown H1 (the cover replaces it)
    text = re.sub(r"\A\s*# .*\n", "", text)
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list", "md_in_html", "sane_lists"])
    if cards:
        body = _glossary_cards(body)
    css = CSS % {**B, "foot": foot.replace('"', "'")}
    nig, pub = logo_data_uri("nigcomsat-logo.png"), logo_data_uri("publica-academy-logo.png")
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="cover"><div class="logos"><span><img src="{nig}"></span><span><img src="{pub}"><b>Publica<br>Academy</b></span></div>
<div class="t"><div class="k">{kicker}</div><h1>{title}</h1><p>{subtitle}</p></div></div>
{body}</body></html>"""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(page)
        tmp = f.name
    html_to_pdf(Path(tmp), pdf_path)
    Path(tmp).unlink()


def html_to_pdf(html_path: Path, pdf_path: Path, query: str = "") -> None:
    url = html_path.resolve().as_uri() + query
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--hide-scrollbars",
                    "--virtual-time-budget=4000", f"--print-to-pdf={pdf_path}", url],
                   check=True, capture_output=True)


def screenshot(html_path: Path, png_path: Path, query: str, size=(1600, 900)) -> None:
    url = html_path.resolve().as_uri() + query
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={size[0]},{size[1]}",
                    "--virtual-time-budget=3000", f"--screenshot={png_path}", url], check=True, capture_output=True)
