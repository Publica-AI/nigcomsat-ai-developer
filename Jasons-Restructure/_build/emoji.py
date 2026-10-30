"""Turns emoji into PNG icons (Google Noto Emoji, Apache-2.0) so they show in every PowerPoint viewer."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.request import urlretrieve

from PIL import Image

HERE = Path(__file__).parent / "emoji"
NOTO = "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/2D/png/512/emoji_u{}.png"
FLAG = "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/third_party/region-flags/png/{}.png"
_HAS_TEXT = re.compile(r"[A-Za-z0-9]")


def is_emoji(s) -> bool:
    return isinstance(s, str) and 0 < len(s) <= 10 and not _HAS_TEXT.search(s) and any(ord(c) > 0x2000 for c in s)


def png_for(e: str) -> str | None:
    cps = "_".join(f"{ord(c):x}" for c in e if ord(c) != 0xFE0F)
    out = HERE / f"{cps}.png"
    url = NOTO.format(cps)
    if len(e) == 2 and all(0x1F1E6 <= ord(c) <= 0x1F1FF for c in e):   # a flag, e.g. 🇳🇬 -> NG
        url = FLAG.format("".join(chr(ord(c) - 0x1F1E6 + 65) for c in e))
    if not out.exists():
        HERE.mkdir(exist_ok=True)
        try:
            urlretrieve(url, out)
            im = Image.open(out)
            im.thumbnail((192, 192))
            im.save(out, optimize=True)
        except Exception:
            out.unlink(missing_ok=True)
            return None
    return str(out)


def collect(obj, found: set):
    if isinstance(obj, dict):
        for v in obj.values():
            collect(v, found)
    elif isinstance(obj, list):
        for v in obj:
            collect(v, found)
    elif is_emoji(obj):
        found.add(obj)


def emoji_map(spec) -> dict:
    found: set = set()
    collect(spec, found)
    return {e: p for e in sorted(found) if (p := png_for(e))}
