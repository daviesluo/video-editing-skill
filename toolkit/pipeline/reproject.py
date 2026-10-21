"""Warp an equirectangular image (the relief skin, satellite imagery) onto a
projected map plate, so a flat map shows the same surface as the globe.

    python pipeline/reproject.py <projection> <width> <height> <src.jpg> <out.jpg> [grade] [outside]

pipeline/textures.py runs it for the house plates; run it by hand for a
new projection added to studio/src/lib/projections.ts.

The projection's fitted scale, translate and rotation come from the same
factory the scenes use; projections with no closed-form inverse here
(conics, azimuthals) are inverted by d3 itself, pixel by pixel
(studio/scripts/plate-grid.ts). Either way the projection comes from the same
factory the scenes use (studio/src/lib/projections.ts via
studio/scripts/plate-params.ts), so the raster lines up with the vector
borders drawn over it. `grade` "none" (the default) keeps the source as it
is, which is right for the relief skin, graded already; "night" compresses
highlights, lowers saturation and tints it cool, for a dark look under
light type. `outside` is the colour off the map, as #rrggbb (default: the
page colour in brand.json).
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
STUDIO = Path(__file__).resolve().parent.parent / "studio"

# Equal Earth constants (Šavrič, Patterson and Jenny 2018), as in d3-geo.
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = np.sqrt(3) / 2


def params(name, w, h):
    out = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings", "scripts/plate-params.ts", name, str(w), str(h)],
        cwd=STUDIO, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def inverse(p, xs, ys):
    """Plate pixels to (lambda, phi) in radians, or NaN outside the map."""
    x = (xs - p["t"][0]) / p["k"]
    y = (p["t"][1] - ys) / p["k"]
    if p["type"] == "mercator":
        lam = x
        phi = 2 * np.arctan(np.exp(y)) - np.pi / 2
    elif p["type"] == "equalearth":
        l = y.copy()
        for _ in range(12):
            l2 = l * l
            l6 = l2 ** 3
            fy = l * (A1 + A2 * l2 + l6 * (A3 + A4 * l2)) - y
            fpy = A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)
            l = l - fy / fpy
        l2 = l * l
        l6 = l2 ** 3
        lam = M * x * (A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)) / np.cos(l)
        phi = np.arcsin(np.clip(np.sin(l) / M, -1, 1))
        lam = np.where(np.abs(lam) > np.pi + 1e-9, np.nan, lam)
    else:
        raise SystemExit(f"no inverse for {p['type']}")
    lam = lam - np.radians(p["rotate"][0])
    lam = (lam + np.pi) % (2 * np.pi) - np.pi
    return lam, phi


def night_grade(img):
    img = 1 - np.exp(-img * 1.35)  # soft highlight roll-off
    img = img / (1 - np.exp(-1.35))
    lum = (img @ np.array([0.2126, 0.7152, 0.0722]))[..., None]
    img = lum + (img - lum) * 0.6
    img = img ** 1.2 * 0.58
    tint = np.array([11, 20, 38]) / 255
    return np.clip(img * 0.86 + tint * 0.35, 0, 1)


def grid(name, w, h):
    """Longitude and latitude (radians) of every plate pixel, from d3 itself
    (studio/scripts/plate-grid.ts), for projections with no inverse here."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".bin") as f:
        subprocess.run(["node", "--experimental-strip-types", "--no-warnings", "scripts/plate-grid.ts", name, str(w), str(h), f.name],
                       cwd=STUDIO, check=True)
        g = np.fromfile(f.name, np.float32).reshape(h, w, 2)
    return np.radians(g[..., 0].astype(np.float64)), np.radians(g[..., 1].astype(np.float64))


def main(name, w, h, src, out, grade="none", outside=None):
    w, h = int(w), int(h)
    if outside is None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from config import brand

        outside = brand()["palette"]["ink"]
    off = np.array([int(outside[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    p = params(name, w, h)
    lut = grid(name, w, h) if p["type"] not in ("mercator", "equalearth") else None
    tex = np.asarray(Image.open(src).convert("RGB"), dtype=np.float32) / 255
    th, tw, _ = tex.shape
    result = np.zeros((h, w, 3), np.float32)
    xs = np.arange(w) + 0.5
    for y0 in range(0, h, 256):  # in bands, to bound memory
        ys = np.arange(y0, min(h, y0 + 256)) + 0.5
        X, Y = np.meshgrid(xs, ys)
        if lut is None:
            lam, phi = inverse(p, X, Y)
        else:
            lam, phi = lut[0][y0:y0 + len(ys)], lut[1][y0:y0 + len(ys)]
        valid = ~np.isnan(lam)
        u = (np.nan_to_num(lam) + np.pi) / (2 * np.pi) * tw - 0.5
        v = (np.pi / 2 - np.nan_to_num(phi)) / np.pi * th - 0.5
        x0 = np.floor(u).astype(int)
        yy = np.floor(v).astype(int)
        fx = (u - x0)[..., None]
        fy = (v - yy)[..., None]
        x0 %= tw
        x1 = (x0 + 1) % tw
        ya = np.clip(yy, 0, th - 1)
        yb = np.clip(yy + 1, 0, th - 1)
        band = (tex[ya, x0] * (1 - fx) * (1 - fy) + tex[ya, x1] * fx * (1 - fy)
                + tex[yb, x0] * (1 - fx) * fy + tex[yb, x1] * fx * fy)
        if grade == "night":
            band = night_grade(band)
        band[~valid] = off
        result[y0:y0 + len(ys)] = band
    Image.fromarray((result * 255).astype(np.uint8)).save(out, quality=90)
    meta = Path(out).with_suffix(".json")
    meta.write_text(json.dumps(dict(p, source=Path(src).name), indent=1))
    print("wrote", out, meta)


if __name__ == "__main__":
    main(*sys.argv[1:])
