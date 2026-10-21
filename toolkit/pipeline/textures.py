"""Downloads the public-domain sources of the globe and the flat-map relief,
records where each came from, and builds the textures the studio needs.
Textures are not committed: they are large, and they rebuild exactly from
the recorded sources.

    python pipeline/textures.py fetch [--width 4096|8192] [--satellite]

1. Downloads, into a cache outside the repository's tracked files
   ($TEXTURE_CACHE, default .cache/texture-sources/), NASA Earth
   Observatory's GEBCO-based elevation and bathymetry maps and five Natural
   Earth 10m layers (and, with --satellite, NASA's Blue Marble).
2. Checks each file against the SHA-256 recorded in
   studio/public/textures/SOURCES.md, when one is recorded, and records
   URL, licence, date and SHA-256 when not, so a later fetch proves it got
   the same file.
3. Builds, in studio/public/textures/: the globe set (earth-relief.jpg,
   earth-bump.png, earth-rough.png, earth-borders.png) at --width (4096 is
   enough for a whole planet; a close zoom needs 8192), and the relief
   plates for the projections in PLATES (plate-relief-<name>-<w>x<h>.jpg
   and its .json), reprojected from a 8192-wide border-free skin.

Downloads are about 65 MB; building takes a few minutes on four cores.
"""

import datetime as dt
import hashlib
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from config import ROOT, STUDIO

TEX = STUDIO / "public" / "textures"
CACHE = Path(os.environ.get("TEXTURE_CACHE", ROOT / ".cache" / "texture-sources"))
NE = "https://naciscdn.org/naturalearth/10m"
EO = "https://eoimages.gsfc.nasa.gov/images/imagerecords"
SOURCES = [
    ("gebco_08_rev_elev_21600x10800.png", f"{EO}/73000/73934/gebco_08_rev_elev_21600x10800.png",
     "NASA Earth Observatory, Topography (image record 73934), from GEBCO_08", "public domain (NASA); credit NASA Earth Observatory"),
    ("gebco_08_rev_bath_21600x10800.png", f"{EO}/73000/73963/gebco_08_rev_bath_21600x10800.png",
     "NASA Earth Observatory, Bathymetry (image record 73963), from GEBCO_08", "public domain (NASA); credit NASA Earth Observatory"),
    ("ne_10m_land.zip", f"{NE}/physical/ne_10m_land.zip", "Natural Earth 1:10m land", "public domain"),
    ("ne_10m_lakes.zip", f"{NE}/physical/ne_10m_lakes.zip", "Natural Earth 1:10m lakes", "public domain"),
    ("ne_10m_glaciated_areas.zip", f"{NE}/physical/ne_10m_glaciated_areas.zip", "Natural Earth 1:10m glaciated areas", "public domain"),
    ("ne_10m_antarctic_ice_shelves_polys.zip", f"{NE}/physical/ne_10m_antarctic_ice_shelves_polys.zip",
     "Natural Earth 1:10m Antarctic ice shelves", "public domain"),
    ("ne_10m_admin_0_boundary_lines_land.zip", f"{NE}/cultural/ne_10m_admin_0_boundary_lines_land.zip",
     "Natural Earth 1:10m land boundary lines", "public domain"),
]
SATELLITE = ("world.200407.3x5400x2700.jpg", f"{EO}/74000/74092/world.200407.3x5400x2700.jpg",
             "NASA Blue Marble Next Generation, July 2004 (image record 74092)", "public domain (NASA); credit NASA Earth Observatory")
# The relief plates the house style draws flat maps on: projection name
# (studio/src/lib/projections.ts) and plate size. Add a row for a new one.
PLATES = [("equalearth-world", 4096, 2000), ("mercator-world84", 4096, 6400)]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def recorded():
    """{file name: sha256} from SOURCES.md, if it exists."""
    md = TEX / "SOURCES.md"
    if not md.exists():
        return {}
    return dict(re.findall(r"^\| `([^`]+)` \|.*\| ([0-9a-f]{64}) \|$", md.read_text(), re.M))


def download(name, url, tries=5):
    """Downloads once into the cache, retrying a dropped connection after
    2, 4, 8 and 16 s: the large NASA files sometimes reset mid-transfer."""
    import time

    import requests

    dst = CACHE / name
    if dst.exists():
        return dst
    tmp = dst.with_suffix(dst.suffix + ".part")
    for attempt in range(tries):
        print("downloading", url, flush=True)
        try:
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            tmp.rename(dst)
            return dst
        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError) as e:
            if attempt == tries - 1:
                raise SystemExit(f"{url}: {e}; run textures.py fetch again later")
            print(f"  {type(e).__name__}; retrying in {2 ** (attempt + 1)} s", flush=True)
            time.sleep(2 ** (attempt + 1))


def fetch(width=4096, satellite=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    TEX.mkdir(parents=True, exist_ok=True)
    known = recorded()
    rows = []
    sources = SOURCES + ([SATELLITE] if satellite else [])
    for name, url, what, licence in sources:
        path = download(name, url)
        digest = sha256(path)
        if name in known and known[name] != digest:
            raise SystemExit(f"{name}: SHA-256 {digest} differs from the recorded {known[name]}; the source changed")
        rows.append((name, what, url, licence, digest))
        if name.endswith(".zip"):
            out = CACHE / name[:-4]
            if not out.exists():
                with zipfile.ZipFile(path) as z:
                    z.extractall(out)
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    lines = ["# Texture sources", "",
             "Written by `pipeline/textures.py fetch`. The textures in this folder are built",
             "from these files and are not committed; a later fetch checks each file",
             f"against the SHA-256 below. First recorded {today}.", "",
             "| File | What | URL | Licence | SHA-256 |", "|---|---|---|---|---|"]
    lines += [f"| `{n}` | {w} | {u} | {lic} | {d} |" for n, w, u, lic, d in rows]
    if not (TEX / "SOURCES.md").exists() or set(known) != {r[0] for r in rows}:
        (TEX / "SOURCES.md").write_text("\n".join(lines) + "\n")

    py = sys.executable
    here = Path(__file__).resolve().parent
    elev, bath = CACHE / SOURCES[0][0], CACHE / SOURCES[1][0]
    run = lambda *a: subprocess.run([py, *map(str, a)], check=True, cwd=ROOT)
    if not (TEX / "earth-relief.jpg").exists():
        run(here / "globetex.py", "relief", elev, bath, CACHE, TEX, width, "globe")
    if not (TEX / "earth-borders.png").exists():
        run(here / "globetex.py", "borders", CACHE, TEX, width)
    plain = CACHE / "earth-relief-plain-8192.jpg"
    if not plain.exists():
        run(here / "globetex.py", "relief", elev, bath, CACHE, CACHE, 8192, "plates")
    for name, w, h in PLATES:
        out = TEX / f"plate-relief-{name}-{w}x{h}.jpg"
        if not out.exists():
            run(here / "reproject.py", name, w, h, plain, out, "none")
    if satellite and not (TEX / "bluemarble-4096.jpg").exists():
        from PIL import Image

        Image.open(CACHE / SATELLITE[0]).resize((4096, 2048), Image.LANCZOS).save(TEX / "bluemarble-4096.jpg", quality=90)
    print("textures ready in", TEX)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] != "fetch":
        raise SystemExit(__doc__)
    w = int(args[args.index("--width") + 1]) if "--width" in args else 4096
    fetch(w, "--satellite" in args)
