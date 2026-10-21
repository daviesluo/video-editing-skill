"""The globe's skin and the flat maps' relief, in the house look: a sea
coloured by real depth with sea-floor relief, cream land with hypsometric
tints and a multi-directional hillshade, white ice sheets, blue lakes, then
calmed by a grade so it reads neither washed out nor vivid. Built from
NASA Earth Observatory's GEBCO-based elevation and bathymetry maps
(21600x10800, public domain) and Natural Earth 10m land, lakes, glaciated
areas, Antarctic ice shelves and land borders (public domain).
pipeline/textures.py downloads the sources and runs this; by hand:

    python pipeline/globetex.py relief <elev.png> <bath.png> <natural_earth_dir> <out_dir> [width] [globe|plates] [chroma lift land_chroma] [shading]
    python pipeline/globetex.py borders <natural_earth_dir> <out_dir> [width]
    python pipeline/globetex.py grade <in.jpg> <rough.png> <out.jpg> <chroma> <lift> [land_chroma]

The globe set is earth-relief.jpg, earth-bump.png and earth-rough.png in
studio/public/textures/ (not committed). A change of grade is shown as a
ladder of stills first (`grade`), and one level is picked.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def _ramp(x, stops):
    """Piecewise-linear colour ramp: stops are (value, "#rrggbb")."""
    xs = [v for v, _ in stops]
    cols = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for _, h in stops], np.float32) / 255
    return np.stack([np.interp(x, xs, cols[:, k]) for k in range(3)], axis=-1).astype(np.float32)


def _raster(shp, W, H, S=2, outline=None):
    """Rasterises polygon shapes (outer rings filled, holes cut) to a soft
    W x H mask (uint8, 255 inside), drawn at S times the size and averaged
    down."""
    import shapefile
    from PIL import ImageDraw

    big = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(big)
    for shape in shapefile.Reader(shp).shapes():
        parts = list(shape.parts) + [len(shape.points)]
        for a, b in zip(parts[:-1], parts[1:]):
            ring = [((x + 180) / 360 * W * S, (90 - y) / 180 * H * S) for x, y in shape.points[a:b]]
            if len(ring) < 3:
                continue
            # Shapefile outer rings run clockwise (negative signed area here,
            # since y points down), holes counter-clockwise.
            area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]))
            d.polygon(ring, fill=255 if area > 0 else 0)
    return np.asarray(big.resize((W, H), Image.BOX))


def _blur(a, r):
    """Approximate Gaussian blur of a float array: three box passes of
    radius r along each axis (edges clamped)."""
    for _ in range(3):
        for ax in (0, 1):
            pad = [(0, 0), (0, 0)]
            pad[ax] = (r + 1, r)
            c = np.cumsum(np.pad(a, pad, mode="edge"), axis=ax, dtype=np.float64)
            hi = np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax)
            lo = np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)
            a = ((hi - lo) / (2 * r + 1)).astype(np.float32)
    return a


def _hillshade(z, H, row0=0, min_cos=0.05, dirs=((-1, 1, 0.6), (0, 1, 0.2), (-1, 0, 0.2))):
    """Multi-directional hillshade on an equirectangular height field (x steps
    shrink with latitude) whose first row is row `row0` of an H-row map.
    1.0 is flat ground; lit slopes go above 1. `min_cos` caps how much the
    east-west slope is boosted toward the poles: the source grids are
    oversampled there, and a full boost turns their steps into streaks."""
    lat = np.radians(90 - (np.arange(row0, row0 + z.shape[0]) + 0.5) * 180 / H)[:, None]
    gy, gx = np.gradient(z)
    gx = gx / np.maximum(np.cos(lat), min_cos)
    n = np.sqrt(gx ** 2 + gy ** 2 + 1)
    out = np.zeros_like(z)
    for dx, dy, w in dirs:
        l = np.array([dx, dy, 1.0], np.float32)
        l /= np.linalg.norm(l)
        out += w * ((-gx * l[0] + gy * l[1] + l[2]) / n) / l[2]
    return out


def relief(elev_src, bath_src, ne_dir, out_dir, width="8192", mode="globe", chroma="0.6", lift="0.3", land_chroma="0.9", shading="1"):
    """The relief skin: cream land with hypsometric tints and a
    multi-directional hillshade, a sea coloured by real depth (GEBCO
    bathymetry) with sea-floor relief, white ice sheets and blue lakes from
    Natural Earth 10m, then calmed by the house grade (`chroma` 0.6, `lift`
    0.3, `land_chroma` 0.9; see `grade`), picked from a ladder of stills
    after the full-strength skin read as too vivid and paler ones as washed
    out.

    mode "globe" writes `earth-relief.jpg` with hairline 10m borders, and
    the bump and roughness maps. mode "plates" writes
    `earth-relief-plain-<width>.jpg` with no borders, for flat-map plates
    (their borders are crisp vectors drawn over the raster); run it at 16384
    so the Mercator Arctic stays sharp. `shading` scales the hillshade
    (land and sea floor): country-scale maps use about 0.2, because the
    elevation grid (about 1.9 km) is coarser than the map and its shading
    prints as soft streaks. Works in bands of rows to bound memory."""
    from PIL import ImageDraw
    import shapefile

    W = int(width)
    H = W // 2
    ne = Path(ne_dir)
    out = Path(out_dir)
    chroma, lift, land_chroma, k = float(chroma), float(lift), float(land_chroma), float(shading)
    load = lambda f: np.asarray(Image.open(f).convert("L").resize((W, H), Image.LANCZOS))
    elev8 = load(elev_src)
    bath8 = load(bath_src)
    land8 = _raster(ne / "ne_10m_land/ne_10m_land.shp", W, H)
    ice8 = np.maximum(
        _raster(ne / "ne_10m_glaciated_areas/ne_10m_glaciated_areas.shp", W, H),
        _raster(ne / "ne_10m_antarctic_ice_shelves_polys/ne_10m_antarctic_ice_shelves_polys.shp", W, H),
    )
    lakes8 = _raster(ne / "ne_10m_lakes/ne_10m_lakes.shp", W, H)
    lake_rgb = np.array([0x8A, 0xD2, 0xDD], np.float32) / 255
    r = max(1, W // 4096)
    result = np.zeros((H, W, 3), np.uint8)
    band, margin = 512, 8 * r + 4
    for y0 in range(0, H, band):
        y1 = min(H, y0 + band)
        a, b = max(0, y0 - margin), min(H, y1 + margin)
        elev = elev8[a:b].astype(np.float32) / 255
        depth = (1 - bath8[a:b].astype(np.float32) / 255) * 8000  # metres below sea level
        land = land8[a:b, :, None].astype(np.float32) / 255
        ice = ice8[a:b, :, None].astype(np.float32) / 255
        lakes = lakes8[a:b, :, None].astype(np.float32) / 255

        # Sea: shelves turquoise, the open ocean a deepening blue.
        sea = _ramp(depth, [(0, "#A6E1DF"), (120, "#84D2DB"), (600, "#62BCD6"), (2000, "#4AA2CF"), (4000, "#3889C3"), (6000, "#2E76B6"), (8000, "#2865A6")])
        floor = _hillshade(_blur(depth, 2 * r) * -0.004 * W / 4096, H, a, min_cos=0.4)
        sea *= np.clip(1 + 0.10 * k * (floor - 1), 0.9, 1.08)[..., None]

        # Land relief from the elevation map, smoothed so the 8-bit steps do
        # not print as terraces in the lowlands. The height scale grows with
        # the width so the shading reads the same at any texture size.
        shade = _hillshade(_blur(elev, r) * 45.0 * W / 4096, H, a, min_cos=0.2)[..., None]
        lit = np.clip(1 + 0.42 * k * (shade - 1), 0.56, 1.12)
        hyps = _ramp(elev, [(0, "#F6F4E8"), (0.08, "#F2EEDD"), (0.23, "#ECE2CB"), (0.47, "#E3D5BC"), (0.78, "#EDE7DD"), (1, "#F7F5F1")])
        ice_rgb = _ramp(elev, [(0, "#F4F8FA"), (1, "#FBFDFE")]) * np.clip(1 + 0.30 * k * (shade - 1), 0.75, 1.06)
        rgb = hyps * lit * (1 - ice) + ice_rgb * ice
        rgb = rgb * (1 - lakes) + lake_rgb * lakes
        img = sea * (1 - land) + rgb * land
        water = (1 - land) + land * lakes
        img = _calm(img, water, chroma, lift, land_chroma)
        result[y0:y1] = (np.clip(img[y0 - a:y0 - a + (y1 - y0)], 0, 1) * 255 + 0.5).astype(np.uint8)

    pil = Image.fromarray(result)
    if mode == "plates":
        name = f"earth-relief-plain-{W}.jpg" if k == 1 else f"earth-relief-plain-{W}-shade{k:g}.jpg"
        pil.save(out / name, quality=92)
        print(name, (out / name).stat().st_size)
        return
    S = 2
    big = pil.resize((W * S, H * S), Image.BICUBIC)
    d = ImageDraw.Draw(big)
    border = _calm(np.array([[[150, 140, 124]]], np.float32) / 255, np.zeros((1, 1, 1), np.float32), chroma, lift, land_chroma)
    border = tuple(int(c * 255 + 0.5) for c in border[0, 0])
    for shape in shapefile.Reader(str(ne / "ne_10m_admin_0_boundary_lines_land/ne_10m_admin_0_boundary_lines_land.shp")).shapes():
        parts = list(shape.parts) + [len(shape.points)]
        for p0, p1 in zip(parts[:-1], parts[1:]):
            line = [((x + 180) / 360 * W * S, (90 - y) / 180 * H * S) for x, y in shape.points[p0:p1]]
            if len(line) > 1:
                d.line(line, fill=border, width=S)
    big.resize((W, H), Image.LANCZOS).save(out / "earth-relief.jpg", quality=90)
    print("earth-relief.jpg", (out / "earth-relief.jpg").stat().st_size)

    # Bump: land relief only; the sea surface is flat. Roughness: a glossy
    # sea (0.30) under a matte land (0.92).
    land, lakes = land8.astype(np.float32) / 255, lakes8.astype(np.float32) / 255
    bump = (elev8.astype(np.float32) / 255) ** 0.6 * land * (1 - lakes)
    Image.fromarray((bump * 255 + 0.5).astype(np.uint8)).save(out / "earth-bump.png", optimize=True)
    rough = 0.92 - (0.92 - 0.30) * ((1 - land) + land * lakes)
    Image.fromarray((rough * 255 + 0.5).astype(np.uint8)).save(out / "earth-rough.png", optimize=True)


def borders(ne_dir, out_dir, width=8192):
    """The globe's land borders alone, as a mask (white lines on black),
    drawn exactly as `relief` draws them into earth-relief.jpg: Natural
    Earth 10m boundary lines, one pixel wide at 8192, drawn at twice the
    size and averaged down. Lay it over a data layer that would otherwise
    cover the borders the skin already has (GlobeView's `lines`)."""
    from PIL import ImageDraw
    import shapefile

    W = int(width)
    H = W // 2
    S = 2
    big = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(big)
    for shape in shapefile.Reader(str(Path(ne_dir) / "ne_10m_admin_0_boundary_lines_land/ne_10m_admin_0_boundary_lines_land.shp")).shapes():
        parts = list(shape.parts) + [len(shape.points)]
        for p0, p1 in zip(parts[:-1], parts[1:]):
            line = [((x + 180) / 360 * W * S, (90 - y) / 180 * H * S) for x, y in shape.points[p0:p1]]
            if len(line) > 1:
                d.line(line, fill=255, width=S)
    out = Path(out_dir) / "earth-borders.png"
    big.resize((W, H), Image.LANCZOS).save(out, optimize=True)
    print(out.name, out.stat().st_size)


def _calm(img, water, chroma, lift, land_chroma):
    """The grade: water colour scaled toward its own grey by `chroma` and
    its darks lifted toward white by `lift`; land colour scaled by
    `land_chroma`."""
    lum = (img @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    sea = 1 - (1 - lum) * (1 - lift) + (img - lum) * chroma
    land = lum + (img - lum) * land_chroma
    return sea * water + land * (1 - water)


def grade(src, rough_png, out, chroma, lift, land_chroma="1"):
    """Calms an existing relief skin with `_calm`, for trying grades; the
    water mask comes from the roughness map."""
    img = np.asarray(Image.open(src).convert("RGB"), np.float32) / 255
    r = np.asarray(Image.open(rough_png).convert("L").resize(img.shape[1::-1], Image.BILINEAR), np.float32) / 255
    water = np.clip((0.92 - r) / (0.92 - 0.30), 0, 1)[..., None]
    res = _calm(img, water, float(chroma), float(lift), float(land_chroma))
    Image.fromarray((np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out, quality=90)
    print(out, Path(out).stat().st_size)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    if sys.argv[1] == "relief":
        relief(*sys.argv[2:])
    elif sys.argv[1] == "borders":
        borders(*sys.argv[2:])
    elif sys.argv[1] == "grade":
        grade(*sys.argv[2:])
    else:
        raise SystemExit(__doc__)
