"""Checks covers against the cover design (references/10-covers.md):

    python pipeline/covercheck.py covers/cover-01.png [...]

Each cover-NN.png needs its layout, cover-NN.json, written beside it by
studio/scripts/covers.mjs: the title block and the picture's subject as
measured in the page (kit/CoverProbe.tsx). `publish.py check` runs the same
rules on a release's cover. Exits non-zero if any cover breaks a rule.

The rules, and why:
- the profile grid shows only the middle 3:4 of a 9:16 cover (y 240 to
  1680), so the title and the subject sit inside that tile with a margin,
  and the cover is judged in the tile, not only at full size;
- the title stays inside the safe band for key text (x 90 to 960);
- the subject starts clear under the title, never under it;
- a picture on the bare page is centred in the space under the title:
  neither gap more than 1.5 times the other, each at least 80 px (shapes
  bunched up under the title with an empty bottom read as unbalanced).
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from config import brand

W, H = 1080, 1920
INK = 60  # summed RGB difference from the page that counts as drawn
FULL_BLEED = 0.5  # share of the tile under the title that is drawn


def _rgb(hexcolour):
    h = hexcolour.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)])


def problems(png, layout_json, cfg=None):
    """The rules a cover breaks, as readable lines (empty if none)."""
    cfg = cfg or brand()
    tile, safe = cfg["tile"], cfg["safe"]
    top, bottom, margin = tile["top"], tile["bottom"], tile["margin"]
    page = _rgb(cfg["palette"]["ink"])
    png, layout_json = Path(png), Path(layout_json)
    if not layout_json.exists():
        return [f"no layout {layout_json.name}: render covers with studio/scripts/covers.mjs"]
    lay = json.loads(layout_json.read_text())
    img = Image.open(png).convert("RGB")
    if img.size != (W, H):
        return [f"cover is {img.size[0]}x{img.size[1]}, not {W}x{H}"]
    title, subject = lay.get("title"), lay.get("subject")
    if not title:
        return ["the cover has no measured title"]
    out = []
    tl, tt, tr, tb = title
    if tt < top + margin or tb > bottom - margin:
        out.append(f"title spans y {tt} to {tb}, outside the grid tile's {top + margin} to {bottom - margin}")
    if tl < safe["left"] or tr > safe["right"]:
        out.append(f"title spans x {tl} to {tr}, outside the safe band {safe['left']} to {safe['right']}")
    if not subject:
        out.append("no visible subject is marked (data-cover-subject)")
        return out
    sl, st, sr, sb = subject
    if st - tb < tile["clear"]:
        out.append(f"the subject starts {st - tb} px under the title, under {tile['clear']}")
    if sb > bottom - margin:
        out.append(f"the subject ends at y {sb}, below the tile's {bottom - margin}")
    if sl < 0 or sr > W:
        out.append(f"the subject runs off the frame (x {sl} to {sr})")
    a = np.asarray(img).astype(int)[tb + 8:bottom]
    drawn = np.abs(a - page).sum(axis=2) > INK
    if drawn.mean() < FULL_BLEED:
        rows = np.nonzero(drawn.sum(axis=1) > 2)[0]
        if len(rows):
            first, last = tb + 8 + rows[0], tb + 8 + rows[-1]
            above, below = first - tb, bottom - last
            gap, k = tile["minGap"], tile["balance"]
            if min(above, below) < gap or max(above, below) > k * min(above, below):
                out.append(f"picture under the title is off centre in the tile: {above} px above it, {below} px below "
                           f"(each at least {gap}, neither over {k} times the other)")
    return out


def report(png):
    png = Path(png)
    lay = json.loads(png.with_suffix(".json").read_text()) if png.with_suffix(".json").exists() else {}
    found = problems(png, png.with_suffix(".json"))
    print(f"{png.name}: title {lay.get('title')}, subject {lay.get('subject')}")
    for p in found:
        print("FAIL", p)
    return found


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    bad = [p for p in sys.argv[1:] if report(p)]
    print("covers OK" if not bad else f"{len(bad)} cover(s) FAILED")
    if bad:
        raise SystemExit(1)
