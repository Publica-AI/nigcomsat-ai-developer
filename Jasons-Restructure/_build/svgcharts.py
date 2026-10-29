"""Inline SVG charts drawn from the real course data, with draw-on animation."""
from __future__ import annotations

import numpy as np

from common import BRAND as B

GRID = "#24384F"
AXIS_TXT = "#9DB0C6"


def _scale(v, lo, hi, a, b):
    return a + (v - lo) / (hi - lo) * (b - a) if hi != lo else (a + b) / 2


def line_svg(values, *, w=1400, h=480, color=B["blue_d"], ymin=None, ymax=None,
             xlabels=(), yticks=(), bands=(), markers=(), hline=None, gaps=(),
             stroke=3, dur="2.6s", delay=".3s", area=True, max_points=700, extra=""):
    """values: 1-D sequence (NaN allowed -> gap). xlabels: [(index, text)].
    bands: [(i0, i1, color, opacity, label)]. markers: [(index, text, color)]."""
    v = np.asarray(values, dtype=float)
    n = len(v)
    idx = np.arange(n)
    if n > max_points:  # keep shape, cut weight
        step = int(np.ceil(n / max_points))
        idx = idx[::step]
    lo = np.nanmin(v) if ymin is None else ymin
    hi = np.nanmax(v) if ymax is None else ymax
    L, R, T, Bm = 90, w - 30, 30, h - 60

    def X(i):
        return _scale(i, 0, n - 1, L, R)

    def Y(y):
        return _scale(y, lo, hi, Bm, T)

    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    for (i0, i1, col, op, lab) in bands:
        out.append(f'<rect x="{X(i0):.1f}" y="{T}" width="{X(i1) - X(i0):.1f}" height="{Bm - T}" fill="{col}" opacity="{op}" rx="6"/>')
        if lab:
            out.append(f'<text x="{(X(i0) + X(i1)) / 2:.1f}" y="{T + 30}" fill="{col}" font-size="22" font-weight="700" text-anchor="middle">{lab}</text>')
    for (yv, lab) in yticks:
        out.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{L - 14}" y="{Y(yv) + 7:.1f}" fill="{AXIS_TXT}" font-size="20" text-anchor="end">{lab}</text>')
    for (i, lab) in xlabels:
        anchor = "start" if i == 0 else ("end" if i >= n - 1 else "middle")
        out.append(f'<text x="{X(i):.1f}" y="{h - 20}" fill="{AXIS_TXT}" font-size="20" text-anchor="{anchor}">{lab}</text>')
    # build path segments (break on NaN)
    segs, cur = [], []
    for i in idx:
        if np.isnan(v[i]):
            if cur:
                segs.append(cur)
            cur = []
        else:
            cur.append((X(i), Y(v[i])))
    if cur:
        segs.append(cur)
    for seg in segs:
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in seg)
        if area and len(seg) > 1:
            ad = d + f" L{seg[-1][0]:.1f},{Bm} L{seg[0][0]:.1f},{Bm} Z"
            out.append(f'<path d="{ad}" fill="{color}" fill-opacity=".13" class="anim a-fade" style="--d:1.6s"/>')
        out.append(f'<path class="draw" style="--dur:{dur};--d:{delay}" d="{d}" fill="none" stroke="{color}" '
                   f'stroke-width="{stroke}" stroke-linejoin="round" stroke-linecap="round"/>')
    for (i0, i1) in gaps:
        out.append(f'<rect x="{X(i0):.1f}" y="{T}" width="{max(6, X(i1) - X(i0)):.1f}" height="{Bm - T}" fill="{B["bad"]}" fill-opacity=".35" class="anim a-fade" style="--d:2.4s"/>')
    if hline:
        yv, lab, col = hline
        out.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{col}" stroke-width="2.5" stroke-dasharray="10 8"/>')
        out.append(f'<text x="{R}" y="{Y(yv) - 12:.1f}" fill="{col}" font-size="22" font-weight="700" text-anchor="end">{lab}</text>')
    for k, (i, lab, col) in enumerate(markers):
        x, y = X(i), Y(v[i])
        out.append(f'<g class="anim a-pop" style="--d:{2.6 + .25 * k:.2f}s;transform-origin:{x:.0f}px {y:.0f}px">'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{col}" stroke="{B["space"]}" stroke-width="3"/>'
                   f'<text x="{x + 18:.1f}" y="{y + 8:.1f}" fill="{col}" font-size="24" font-weight="800">{lab}</text></g>')
    out.append(extra)
    out.append("</svg>")
    return "".join(out)


def spark_svg(values, *, w=300, h=110, color=B["blue_d"], delay=".4s"):
    v = np.asarray(values, dtype=float)
    lo, hi = v.min(), v.max()
    pts = " L".join(f"{_scale(i, 0, len(v) - 1, 8, w - 8):.1f},{_scale(y, lo, hi, h - 8, 8):.1f}" for i, y in enumerate(v))
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;display:block"><path class="draw" style="--dur:1.8s;--d:{delay}" '
            f'd="M{pts}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def lines_svg(series, *, w=1400, h=480, ymin=None, ymax=None, xlabels=(), yticks=(), bands=(), markers=(),
              hline=None, labels_right=True, max_points=700):
    """Several lines on one axis. series: [dict(values=..., color=..., stroke=3, dash=None, label=None,
    delay=".3s", dur="2.4s", area=False)]. All series share the same x positions (same length)."""
    n = len(series[0]["values"])
    allv = np.concatenate([np.asarray(s["values"], dtype=float) for s in series])
    lo = np.nanmin(allv) if ymin is None else ymin
    hi = np.nanmax(allv) if ymax is None else ymax
    L, R, T, Bm = 90, w - (170 if labels_right else 30), 30, h - 60

    def X(i):
        return _scale(i, 0, n - 1, L, R)

    def Y(y):
        return _scale(y, lo, hi, Bm, T)

    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    for (i0, i1, col, op, lab) in bands:
        out.append(f'<rect x="{X(i0):.1f}" y="{T}" width="{X(i1) - X(i0):.1f}" height="{Bm - T}" fill="{col}" fill-opacity="{op}" rx="6"/>')
        if lab:
            out.append(f'<text x="{(X(i0) + X(i1)) / 2:.1f}" y="{T + 30}" fill="{col}" font-size="22" font-weight="700" text-anchor="middle">{lab}</text>')
    for (yv, lab) in yticks:
        out.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{L - 14}" y="{Y(yv) + 7:.1f}" fill="{AXIS_TXT}" font-size="20" text-anchor="end">{lab}</text>')
    for (i, lab) in xlabels:
        anchor = "start" if i == 0 else ("end" if i >= n - 1 else "middle")
        out.append(f'<text x="{X(i):.1f}" y="{h - 20}" fill="{AXIS_TXT}" font-size="20" text-anchor="{anchor}">{lab}</text>')
    step = max(1, int(np.ceil(n / max_points)))
    for s in series:
        v = np.asarray(s["values"], dtype=float)
        pts = [(X(i), Y(v[i])) for i in range(0, n, step) if not np.isnan(v[i])]
        if not pts:
            continue
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        if s.get("area"):
            out.append(f'<path d="{d} L{pts[-1][0]:.1f},{Bm} L{pts[0][0]:.1f},{Bm} Z" fill="{s["color"]}" fill-opacity=".12" class="anim a-fade" style="--d:1.6s"/>')
        dash = f' stroke-dasharray="{s["dash"]}"' if s.get("dash") else ""
        cls = "" if s.get("dash") else ' class="draw"'      # dashed lines fade in instead of drawing on
        fade = ' class="anim a-fade"' if s.get("dash") else ""
        out.append(f'<path{cls}{fade} style="--dur:{s.get("dur", "2.4s")};--d:{s.get("delay", ".3s")}" d="{d}" fill="none" '
                   f'stroke="{s["color"]}" stroke-width="{s.get("stroke", 3)}" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        if s.get("label") and labels_right:
            out.append(f'<text class="anim a-fade" style="--d:{s.get("delay", ".3s")}" x="{pts[-1][0] + 14:.1f}" y="{pts[-1][1] + 8:.1f}" '
                       f'fill="{s["color"]}" font-size="22" font-weight="800">{s["label"]}</text>')
    if hline:
        yv, lab, col = hline
        out.append(f'<line x1="{L}" x2="{R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{col}" stroke-width="2.5" stroke-dasharray="10 8"/>')
        out.append(f'<text x="{R}" y="{Y(yv) - 12:.1f}" fill="{col}" font-size="22" font-weight="700" text-anchor="end">{lab}</text>')
    for k, (i, yv, lab, col) in enumerate(markers):
        x, y = X(i), Y(yv)
        out.append(f'<g class="anim a-pop" style="--d:{2.6 + .25 * k:.2f}s;transform-origin:{x:.0f}px {y:.0f}px">'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{col}" stroke="{B["space"]}" stroke-width="3"/>'
                   f'<text x="{x + 18:.1f}" y="{y + 8:.1f}" fill="{col}" font-size="24" font-weight="800">{lab}</text></g>')
    out.append("</svg>")
    return "".join(out)


def bars_svg(labels, values, *, w=1400, h=460, ymin=0, ymax=None, color=B["blue_d"], highlight=(), hcolor=B["gold"],
             fmt="{:.1f}", show_values=True):
    """Vertical bars that grow in. highlight: indexes drawn in hcolor."""
    v = np.asarray(values, dtype=float)
    hi = v.max() * 1.12 if ymax is None else ymax
    L, R, T, Bm = 40, w - 20, 40, h - 60
    n = len(v)
    slot = (R - L) / n
    bw = slot * 0.62
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">',
           f'<line x1="{L}" x2="{R}" y1="{Bm}" y2="{Bm}" stroke="{GRID}" stroke-width="2"/>']
    for i, (lab, val) in enumerate(zip(labels, v)):
        x = L + i * slot + (slot - bw) / 2
        top = _scale(val, ymin, hi, Bm, T)
        col = hcolor if i in highlight else color
        d = .2 + i * .08
        out.append(f'<g class="anim" style="--d:{d:.2f}s"><rect x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{Bm - top:.1f}" rx="6" fill="{col}"/>')
        if show_values:
            out.append(f'<text x="{x + bw / 2:.1f}" y="{top - 12:.1f}" fill="#EAF2FB" font-size="22" font-weight="800" text-anchor="middle">{fmt.format(val)}</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{h - 22}" fill="{AXIS_TXT}" font-size="21" text-anchor="middle">{lab}</text></g>')
    out.append("</svg>")
    return "".join(out)
